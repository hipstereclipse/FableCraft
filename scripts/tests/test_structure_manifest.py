"""Exercise each structure-contract edge independently, including real negative fixtures."""
import copy
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from structure_contract import ROOT, MANIFEST, EVIDENCE, capture, check, runtime_tables, anchor_errors, interaction_errors


class StructureContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.generated, cls.voxels = capture()
        cls.manifest = json.loads(MANIFEST.read_text())
        cls.tables = runtime_tables(ROOT)

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for relative in ('packs/Fablecraft_BP/structures/fc', str(EVIDENCE.parent)):
            shutil.copytree(ROOT / relative, self.root / relative)
        self.m = copy.deepcopy(self.manifest); self.g = copy.deepcopy(self.generated); self.t = copy.deepcopy(self.tables)

    def errors(self):
        return check(self.root, self.root, self.m, self.g, self.t, self.voxels)

    def assert_error(self, text):
        self.assertTrue(any(text in e for e in self.errors()), self.errors())

    def test_current_real_contract_passes(self): self.assertEqual(self.errors(), [])

    def test_missing_generator(self):
        del self.g['arena_ring']; self.assert_error('Missing generator output: arena_ring')

    def test_missing_asset(self):
        (self.root / 'packs/Fablecraft_BP/structures/fc/arena_ring.mcstructure').unlink()
        self.assert_error('Missing structure asset: arena_ring')

    def test_changed_asset_bytes(self):
        with (self.root / 'packs/Fablecraft_BP/structures/fc/arena_ring.mcstructure').open('ab') as out: out.write(b'changed')
        self.assert_error('Stale generated asset: arena_ring')

    def test_missing_and_changed_image(self):
        path = self.root / EVIDENCE.parent / 'arena_ring.png'
        path.write_bytes(b'not the current render'); self.assert_error('Stale render image: arena_ring')
        path.unlink(); self.assert_error('Missing render file: arena_ring')

    def test_missing_grade_and_audit_row(self):
        path = self.root / EVIDENCE
        data = json.loads(path.read_text()); del data['structures']['arena_ring']['grade']
        path.write_text(json.dumps(data)); self.assert_error('Missing render grade: arena_ring')
        audit = self.root / EVIDENCE.parent / 'AUDIT.md'
        audit.write_text(''); self.assert_error('Missing audit row: arena_ring')

    def test_stale_render_source(self):
        self.g['arena_ring']['sha256'] = 'changed'; self.assert_error('Stale render source: arena_ring')

    def test_width_depth_and_height_independently(self):
        for key in ('w', 'h', 'd'):
            with self.subTest(key=key):
                self.t = copy.deepcopy(self.tables); self.t['STRUCTS'][0][key] += 1
                self.assert_error('Runtime footprint mismatch: demon_door_arch')

    def test_missing_runtime_and_orphan_loot(self):
        self.t['STRUCTS'].pop(0); self.assert_error('Missing scatter registration: demon_door_arch')
        self.t['CHEST_LOOT']['fc:no_such_structure'] = []; self.assert_error('Orphan loot reference')

    def test_orphans_and_duplicate_manifest(self):
        self.g['orphan'] = self.g['arena_ring']; self.assert_error('Orphan generator output: orphan')
        self.m['structures'].append(self.m['structures'][0]); self.assert_error('Duplicate manifest structure')

    def test_numeric_anchors_are_separate_from_asset_edges(self):
        for key, field in (('skill', 'x'), ('cullis', 'z'), ('maze', 'studyY')):
            actual = copy.deepcopy(self.tables['GUILD']); actual[key][field] += 1
            self.assertIn(f'Guild anchor mismatch: {key}', anchor_errors(actual))
        self.t['GUILD']['questTables'][1]['x'] += 1
        self.assert_error('Guild anchor mismatch: questTables')

    def test_blocked_npc_column_and_missing_interaction_blocks(self):
        actual = copy.deepcopy(self.tables['GUILD']); actual['maze']['z'] = 72
        self.assertIn('Guild standing clearance mismatch: maze', interaction_errors(self.voxels['guild_hall'], actual))
        actual['skill']['x'] += 1
        self.assertIn('Guild interaction block mismatch: skill', interaction_errors(self.voxels['guild_hall'], actual))

    def test_cross_poi_spawn_coordinates_fail_bounds(self):
        entry = next(e for e in self.t['STRUCTS'] if e['id'] == 'fc:power_snowspire_oracle')
        entry['mobSpawns'] = [[30.5, 3, 20.5], [18.5, 1, 23.5], [23.5, 1, 10.5]]
        self.assert_error('Spawn out of bounds: power_snowspire_oracle[0]')

    def test_spawn_count_shape_and_feet_headroom(self):
        entry = next(e for e in self.t['STRUCTS'] if e['id'] == 'fc:hook_coast')
        original = copy.deepcopy(entry['mobSpawns'])
        entry['mobSpawns'] = original[:-1]
        self.assert_error('Spawn count mismatch: hook_coast')
        for point, message in [([1, 2], 'Invalid spawn coordinate'),
                               ([True, 1, 1], 'Invalid spawn coordinate'),
                               (['1', 1, 1], 'Invalid spawn coordinate'),
                               ([float('nan'), 1, 1], 'Invalid spawn coordinate'),
                               ([-1, 1, 1], 'Spawn out of bounds'),
                               ([1, 0, 1], 'Spawn out of bounds'),
                               ([1, 19, 1], 'Spawn out of bounds'),
                               ([1, 1, 37], 'Spawn out of bounds')]:
            with self.subTest(point=point):
                entry['mobSpawns'] = copy.deepcopy(original)
                entry['mobSpawns'][0] = point
                self.assert_error(message + ': hook_coast[0]')

    def test_fixed_and_legacy_are_explicit(self):
        self.t['fixed'].remove('fc:guild_hall'); self.assert_error('Missing fixed registration: guild_hall')
        entry = next(e for e in self.m['structures'] if e['kind'] == 'legacy')
        del entry['reason']; self.assert_error('Undocumented legacy output')

    def test_per_cell_chamber_registration_requires_owner_and_manifest(self):
        main = Path('packs/Fablecraft_BP/scripts/main.js')
        source = (ROOT / main).read_text()
        self.assertEqual(self.tables['fixed'].count('fc:chamber_of_fate'), 1)
        target = self.root / main
        target.parent.mkdir(parents=True, exist_ok=True)
        for old, new in (('./guild_caves.js', './unrelated.js'),
                         ('const guildCaves = createGuildCaveLifecycle(', 'const guildCaves = unrelatedFactory('),
                         ('chamber: DATA.guildChamber', 'chamber: DATA.unrelated')):
            with self.subTest(binding=old):
                self.assertIn(old, source)
                target.write_text(source.replace(old, new))
                self.t = runtime_tables(self.root)
                self.assert_error('Missing fixed registration: chamber_of_fate')


if __name__ == '__main__': unittest.main(verbosity=2)

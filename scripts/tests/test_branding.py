"""Real generator/build isolation and name-routing contracts; never edit live packs."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
import build_addon
import fc_branding
import fc_data
import fc_strings as names
import gen_behavior
import gen_resources


def pack_hashes(root):
    return {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in (root / 'packs').rglob('*') if p.is_file()}


def read_json(root, relative):
    return json.loads((root / relative).read_text(encoding='utf-8'))


class Naming(unittest.TestCase):
    def test_strict_accessor_and_mode_restoration(self):
        self.assertEqual(names.name('realm'), 'Albion')
        with names.branding('original'):
            self.assertEqual(names.name('realm'), 'Elderfen')
            with self.assertRaises(RuntimeError), names.branding('faithful'):
                self.assertEqual(names.name('realm'), 'Albion')
                raise RuntimeError('test context restoration')
            self.assertEqual(names.mode(), 'original')
        self.assertEqual(names.mode(), 'faithful')
        with self.assertRaises(KeyError):
            names.name('missing')
        for invalid in ('', 'release', 'ORIGINAL'):
            with self.subTest(mode=invalid), self.assertRaises(ValueError):
                names.name('realm', invalid)

    def test_interpolation_accents_color_codes_and_overlap(self):
        source = '§6Café: {hero}, take Avo’s Tear to the Heroes’ Guild. We’re ready!'
        with names.branding('faithful'):
            self.assertEqual(names.text(source), source)
        with names.branding('original'):
            self.assertEqual(names.text(source).format(hero='Zoë'),
                             '§6Café: Zoë, take Dawnfall to the Wayfarer Hall. We’re ready!')
            self.assertEqual(names.text('§aBalverines §r/ Balverine'), '§aMoonfangs §r/ Moonfang')

    def test_display_inventory_detects_names_after_color_codes(self):
        self.assertEqual(names.faithful_matches('§6Fablecraft §dTheresa'), ['Fablecraft', 'Theresa'])

    def test_dictionary_keys_and_internal_references_unchanged(self):
        value = {'Albion': ['fc:balverine', 'wd:ghost_sword', 'textures/items/avos_tear', 42, True],
                 'display': 'Albion'}
        with names.branding('original'):
            result = names.localize(value)
        self.assertEqual(result['Albion'], value['Albion'])
        self.assertEqual(result['display'], 'Elderfen')
        self.assertEqual(value['display'], 'Albion')


class StagedGeneration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.addClassCleanup(cls.temp.cleanup)
        cls.before = pack_hashes(ROOT)
        cls.faithful = fc_branding.stage_packs(ROOT, 'faithful', Path(cls.temp.name))
        cls.original = fc_branding.stage_packs(ROOT, 'original', Path(cls.temp.name))

    def test_live_packs_unchanged_and_paths_restored(self):
        self.assertEqual(self.before, pack_hashes(ROOT))
        self.assertEqual(gen_behavior.BP, ROOT / 'packs/Fablecraft_BP')
        self.assertEqual(gen_resources.RP, ROOT / 'packs/Fablecraft_RP')
        self.assertEqual(names.mode(), 'faithful')
        self.assertNotEqual(self.faithful, self.original)

    def test_faithful_generated_output_matches_live_semantics(self):
        for item in fc_data.all_items():
            relative = f"packs/Fablecraft_BP/items/{item['id']}.json"
            self.assertEqual(read_json(ROOT, relative), read_json(self.faithful, relative))
        for relative in ('packs/Fablecraft_BP/scripts/fc_gamedata.js',
                         'packs/Fablecraft_RP/texts/en_US.lang',
                         'packs/Fablecraft_BP/scripts/fc_strings.js'):
            self.assertEqual((ROOT / relative).read_text(), (self.faithful / relative).read_text())

    def test_lore_helper_translates_without_changing_color_and_stats(self):
        item = {'cat': 'misc', 'desc': "Theresa waits in Albion. Café."}
        with names.branding('original'):
            self.assertEqual(gen_behavior.lore_lines(item), ['§o§9Seren waits in Elderfen. Café.'])

    def test_generated_item_names_keep_gameplay_components(self):
        for item in fc_data.all_items():
            relative = f"packs/Fablecraft_BP/items/{item['id']}.json"
            faithful, original = read_json(self.faithful, relative), read_json(self.original, relative)
            with self.subTest(item=item['id']):
                # Only display_name may change in emitted item JSON; stats and IDs are identical.
                a = faithful['minecraft:item']['components'].pop('minecraft:display_name')
                b = original['minecraft:item']['components'].pop('minecraft:display_name')
                self.assertEqual(faithful, original)
                if item['id'] == 'avos_tear':
                    self.assertEqual(a['value'], "§fAvo's Tear")
                    self.assertEqual(b['value'], '§fDawnfall')

    def test_lang_keys_stable_and_values_translated(self):
        def lang(root):
            return dict(line.split('=', 1) for line in
                        (root / 'packs/Fablecraft_RP/texts/en_US.lang').read_text().splitlines()
                        if '=' in line and not line.startswith('#'))
        faithful, original = lang(self.faithful), lang(self.original)
        self.assertEqual(faithful.keys(), original.keys())
        self.assertEqual(faithful['entity.fc:theresa.name'], 'Theresa')
        self.assertEqual(original['entity.fc:theresa.name'], 'Seren')
        self.assertEqual(original['fc.guild.welcome'], 'Welcome to the Wayfarer Hall')
        self.assertEqual(read_json(self.original, 'packs/Fablecraft_RP/texts/languages.json'), ['en_US'])

    def test_generated_data_lore_and_names(self):
        def data(root):
            source = (root / 'packs/Fablecraft_BP/scripts/fc_gamedata.js').read_text()
            return json.loads(source.split('export const DATA = ', 1)[1].rstrip(';\n'))
        faithful, original = data(self.faithful), data(self.original)
        def compare(a, b):
            if isinstance(a, dict):
                self.assertEqual(a.keys(), b.keys())
                for key in a:
                    compare(a[key], b[key])
            elif isinstance(a, list):
                self.assertEqual(len(a), len(b))
                for first, second in zip(a, b):
                    compare(first, second)
            elif not isinstance(a, str) or a.startswith(('fc:', 'wd:', 'textures/')):
                self.assertEqual(a, b)
        compare(faithful, original)
        self.assertEqual(original['quests'][0]['name'], 'Join the Wayfarer Hall')
        self.assertEqual(faithful['quests'][0]['name'], "Join the Heroes' Guild")
        self.assertIn('Wayfarer Hall', json.dumps(original))
        self.assertNotIn('Jack of Blades', json.dumps(original))

    def test_expression_display_names_preserve_unlocks_and_animation_ids(self):
        path = 'packs/Fablecraft_BP/config/fable_emotes.json'
        faithful, original = read_json(self.faithful, path), read_json(self.original, path)
        self.assertEqual(len(faithful['emotes']), 31)
        for first, second in zip(faithful['emotes'], original['emotes']):
            self.assertEqual(first['id'], second['id'])
            if first['id'] == 'yeron':
                self.assertEqual(first['name'], 'Yeron')
                self.assertEqual(second['name'], 'Aren')
            first.pop('name'); second.pop('name')
            self.assertEqual(first, second)
        faithful.pop('emotes'); original.pop('emotes')
        self.assertEqual(faithful, original)

    def test_manifest_identity_and_dependencies_preserved(self):
        for label in ('Fablecraft_BP', 'Fablecraft_RP'):
            relative = f'packs/{label}/manifest.json'
            faithful, original = read_json(self.faithful, relative), read_json(self.original, relative)
            for field in ('uuid', 'version', 'min_engine_version'):
                self.assertEqual(faithful['header'][field], original['header'][field])
            self.assertEqual(faithful['modules'], original['modules'])
            self.assertEqual(faithful.get('dependencies'), original.get('dependencies'))
            self.assertIn('Wayfarer Tales', original['header']['name'])
            self.assertNotIn('All Wayfarer lore property', original['metadata']['license'])

    def test_debt_reports_runtime_without_claiming_release_ready(self):
        report = fc_branding.write_debt_report(self.original)
        self.assertIn('packs/Fablecraft_BP/scripts/main.js', report['files'])
        self.assertNotIn('packs/Fablecraft_RP/texts/en_US.lang', report['files'])
        self.assertFalse(read_json(self.original, 'build-info.json')['distribution_ready'])

    def test_owners_restore_after_generation_failure(self):
        bp, rp = gen_behavior.BP, gen_resources.RP
        with patch.object(gen_behavior, 'emit_weapon', side_effect=RuntimeError('failure')):
            with self.assertRaises(RuntimeError):
                fc_branding.emit_display_files(self.original, 'original')
        self.assertEqual((gen_behavior.BP, gen_resources.RP), (bp, rp))
        self.assertEqual(names.mode(), 'faithful')

    def test_release_and_nonlocal_packaging_fail_closed(self):
        with self.assertRaises(ValueError):
            build_addon.package(self.original, 'original')
        with self.assertRaises(ValueError):
            build_addon.package(self.faithful, 'faithful')
        result = subprocess.run([sys.executable, str(ROOT / 'scripts/build_addon.py'),
                                 '--branding', 'original'], capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('blocked until L3/L4', result.stderr)
        self.assertFalse((self.original / 'dist').exists())

    def test_auditors_check_staged_packs_and_detect_staged_failures(self):
        # Deliberately break ONLY a copied target, proving --root doesn't validate live assets.
        root = fc_branding.stage_packs(ROOT, 'faithful', Path(self.temp.name))
        commands = [
            [sys.executable, str(ROOT / 'scripts/verify_emotes.py'), '--root', str(root)],
            [sys.executable, str(ROOT / 'scripts/audit_hud.py'), '--check', '--root', str(root)],
        ]
        for cmd in commands:
            result = subprocess.run(cmd, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        path = root / 'packs/Fablecraft_RP/animations/fable_player_emotes.animation.json'
        content = json.loads(path.read_text()); content['animations'] = {}
        path.write_text(json.dumps(content))
        (root / 'packs/Fablecraft_RP/textures/ui/fable_hud/gold.png').unlink()
        for cmd in commands:
            result = subprocess.run(cmd, capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(self.before, pack_hashes(ROOT))


if __name__ == '__main__':
    unittest.main(verbosity=2)

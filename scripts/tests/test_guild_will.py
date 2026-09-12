"""GP9 final generated Will station, runtime lane and appearance-owner regressions."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
import fc_mobs
import gen_emotes
import gen_resources
import gen_structures as GS
import structure_contract as contract


class GuildWill(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        captured = {}
        with patch.object(GS.Vox, 'save', lambda vox, name: captured.setdefault(name, vox)):
            GS.guild_hall()
        cls.vox = captured['guild_hall']
        cls.tables = contract.runtime_tables(ROOT)

    def test_final_voxels_support_actual_station_and_harmless_beam_preflights(self):
        v = self.vox
        cells = {f'{x},{y},{z}': v.palette[v.grid[v.idx(x, y, z)]][0]
                 for x in range(58, 64) for y in range(6) for z in range(83, 91)}
        result = subprocess.run(['node', '--experimental-vm-modules', 'scripts/tests/guild_will_voxels.mjs'],
                                input=json.dumps({'station': GS.GUILD_LAYOUT['will_training'], 'cells': cells}),
                                capture_output=True, text=True, cwd=ROOT)
        print(result.stdout, end='')
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_numeric_station_and_target_changes_fail_coupled_anchor_contract(self):
        self.assertEqual(contract.anchor_errors(self.tables['GUILD']), [])
        for role in ('will', 'willTarget'):
            for axis in ('x', 'z'):
                changed = copy.deepcopy(self.tables['GUILD'])
                changed['training'][role][axis] += 1
                self.assertIn('Guild anchor mismatch: training', contract.anchor_errors(changed), (role, axis))
        missing = copy.deepcopy(self.tables['GUILD'])
        del missing['training']['will']
        self.assertIn('Guild anchor mismatch: training', contract.anchor_errors(missing))

    def test_will_cast_clip_uses_existing_rig_and_only_will_loses_the_training_stick(self):
        mobs = {m['id']: m for m in fc_mobs.MOBS}
        will = mobs['guild_apprentice_will']
        parts = {part['name'] for part in fc_mobs.build_parts(will)}
        self.assertNotIn('training_stick', parts)
        self.assertIn('training_stick', {p['name'] for p in fc_mobs.build_parts(mobs['guild_apprentice_might'])})
        self.assertIn('training_bow', {p['name'] for p in fc_mobs.build_parts(mobs['guild_apprentice_skill'])})
        clip = gen_emotes.npc_animations()['animations']['animation.npc.will_practice']
        self.assertFalse(clip['loop'])
        self.assertLessEqual(clip['animation_length'], 1.5)
        self.assertTrue(set(clip['bones']) <= parts)
        for bone in clip['bones'].values():
            frames = bone['rotation']
            self.assertEqual(frames['0.0'], frames['1.4'], 'A released cast must settle back to neutral')
        for mob in (will, mobs['guild_apprentice_might'], mobs['guild_apprentice_skill']):
            outputs = {}
            with patch.object(gen_resources, 'write_json', lambda path, value: outputs.setdefault(path.name, value)):
                gen_resources.emit_client_entity(mob)
            desc = outputs[f"{mob['id']}.entity.json"]['minecraft:client_entity']['description']
            self.assertEqual('will_practice' in desc['animations'], mob is will)


if __name__ == '__main__':
    unittest.main()

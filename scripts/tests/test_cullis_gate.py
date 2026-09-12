"""W1.1 geometry, arrival clearance, palette and actual runtime detector contracts."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import gen_structures as GS
from gen_screenshots import BLOCK_COLORS
from structure_contract import ROOT, runtime_tables


class CullisGate(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        captures = {}
        with patch.object(GS.Vox, 'save', lambda vox, name: captures.setdefault(name, vox)):
            GS.focus_site()
        cls.captures = captures; cls.vox = captures['focus_site']

    def block(self, x, y, z): return self.vox.palette[self.vox.grid[self.vox.idx(x, y, z)]][0]

    def test_stable_id_footprint_and_travel_registration(self):
        self.assertEqual(list(self.captures), ['focus_site'])
        self.assertEqual((self.vox.sx, self.vox.sy, self.vox.sz), (13, 10, 13))
        entry = next(s for s in runtime_tables(ROOT)['STRUCTS'] if s['id'] == 'fc:focus_site')
        self.assertEqual([entry[k] for k in ('w', 'h', 'd')], [13, 10, 13]); self.assertTrue(entry['cullis'])

    def test_arrival_core_and_three_blocks_of_headroom(self):
        self.assertEqual(self.block(6, 0, 6), 'minecraft:sea_lantern')
        for x in range(5, 8):
            for z in range(5, 8):
                for y in (1, 2, 3): self.assertEqual(self.block(x, y, z), 'minecraft:air')

    def test_four_level_three_wide_walking_routes(self):
        for step in range(13):
            for offset in (-1, 0, 1):
                for x, z in ((6 + offset, step), (step, 6 + offset)):
                    self.assertNotEqual(self.block(x, 0, z), 'minecraft:air')
                    for y in (1, 2): self.assertEqual(self.block(x, y, z), 'minecraft:air')

    def test_palette_is_known_and_no_floating_crystal(self):
        names = {self.vox.palette[i][0] for i in self.vox.grid}
        self.assertLessEqual(names - {'minecraft:air'}, BLOCK_COLORS.keys())
        self.assertIn('minecraft:blue_glazed_terracotta', names)
        self.assertFalse(names & {'minecraft:amethyst_block', 'minecraft:amethyst_cluster'})

    def test_actual_runtime_configuration_and_failure_paths(self):
        blocks = {f'{x},{y},{z}': self.block(x,y,z) for x in range(13) for y in range(10) for z in range(13)
                  if self.block(x,y,z) != 'minecraft:air'}
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'gate.json'; path.write_text(json.dumps(blocks))
            result = subprocess.run(['node', 'scripts/tests/cullis_configuration.cjs', str(path)],
                                    cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        print(result.stdout.strip())


if __name__ == '__main__': unittest.main(verbosity=2)

"""GP7 actual maintenance callbacks and final generated approach/training cells.

The bounded cardinal graph recognizes full and half-slab surfaces with two
blocks of standing clearance. It does not emulate live Bedrock collision or AI.
"""
import copy
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import gen_structures as GS
from test_guild_routes import FLOORS, cell, clear, interval, reachable, supported

ROOT = Path(__file__).resolve().parents[2]


def approach_graph(vox):
    nodes = set()
    for x in range(59, 85):
        for z in range(74, 97):
            for y in range(3):
                name, states = cell(vox, x, y, z)
                if name not in FLOORS:
                    continue
                feet = interval(name, states, y)[1]
                if clear(vox, x, feet, z):
                    nodes.add((x, feet, z))
    return nodes


class GuildMaintenance(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        captured = {}
        with patch.object(GS.Vox, 'save', lambda vox, name: captured.setdefault(name, vox)):
            GS.guild_hall()
        cls.vox = captured['guild_hall']

    def check_approach(self, vox):
        nodes = approach_graph(vox)
        # Independently surveyed east path, bank apron, island apron and throat.
        points = [(82, 1., 80), (77, 1., 76), (75, 1.5, 77),
                  (66, 1.5, 84), (66, 1., 88), (66, 1., 95)]
        for start in (points[0], points[-1]):
            found = reachable(vox, nodes, start)
            for point in points:
                self.assertIn(point, found, f'Approach cannot reach {point} from {start}')

    def test_actual_maintenance_callback_preserves_old_worlds_and_training(self):
        result = subprocess.run(['node', '--experimental-vm-modules', 'scripts/tests/guild_maintenance.test.mjs'],
                                text=True, capture_output=True, cwd=ROOT)
        print(result.stdout, end='')
        print(result.stderr, end='', file=sys.stderr)
        self.assertEqual(result.returncode, 0, 'Actual maintenance callback regression failed')

    def test_final_generator_connects_both_approaches_without_runtime_repairs(self):
        self.check_approach(self.vox)
        # Both full standing cells are authored even where the retired helper
        # only used to clear y1. Preserve the two-wide south walk.
        for z in range(86, 96):
            for x in ((65, 66) if z <= 89 else (66, 67)):
                self.assertTrue(supported(self.vox, x, 1., z), (x, z))
                self.assertTrue(clear(self.vox, x, 1., z), (x, z))

    def test_existing_ring_and_island_clearance_is_generator_owned(self):
        for x, z in ((99, 59), (103, 63), (103, 59), (63, 87)):
            self.assertTrue(supported(self.vox, x, 1., z), (x, z))
            self.assertTrue(clear(self.vox, x, 1., z, height=3.), (x, z))
        for z in (86, 88):
            self.assertEqual(cell(self.vox, 63, 2, z)[0], 'minecraft:air')
        # Survey actual apprentice station columns and both standing cells.
        for x, z in ((99, 61), (102, 61), (83, 39)):
            self.assertIn(cell(self.vox, x, 0, z)[0], ('minecraft:coarse_dirt', 'minecraft:dirt_path'))
            for y in (1, 2):
                self.assertEqual(cell(self.vox, x, y, z)[0], 'minecraft:air')

    def test_independent_missing_floor_and_apron_obstruction_fail_route_checks(self):
        floor = copy.deepcopy(self.vox)
        floor.set(66, 0, 95, 'minecraft:air')
        with self.assertRaises(AssertionError):
            self.check_approach(floor)
        head = copy.deepcopy(self.vox)
        head.set(66, 3, 84, 'minecraft:stone_bricks')
        with self.assertRaises(AssertionError):
            self.check_approach(head)


if __name__ == '__main__':
    unittest.main()

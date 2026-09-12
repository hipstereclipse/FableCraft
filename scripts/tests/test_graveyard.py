"""W1.2 landmark, walking route and actual scatter spawn regression contracts."""
from collections import deque
import importlib.util
import json
import os
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

if os.environ.get('FC_GRAVEYARD_TEST_SOURCE'):
    spec = importlib.util.spec_from_file_location('old_structures', os.environ['FC_GRAVEYARD_TEST_SOURCE'])
    GS = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(GS)


class Graveyard(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.captures, cls.clipped = {}, []
        original = GS.Vox.set
        def bounded(vox, x, y, z, *args, **kwargs):
            if not (0 <= x < vox.sx and 0 <= y < vox.sy and 0 <= z < vox.sz):
                cls.clipped.append((x, y, z))
            return original(vox, x, y, z, *args, **kwargs)
        with patch.object(GS.Vox, 'save', lambda v, n: cls.captures.setdefault(n, v)), patch.object(GS.Vox, 'set', bounded):
            GS.graveyard()
        cls.vox = cls.captures['graveyard']
        cls.tables = runtime_tables(ROOT)
        cls.entry = next(s for s in cls.tables['STRUCTS'] if s['id'] == 'fc:graveyard')

    def block(self, x, y, z):
        return self.vox.palette[self.vox.grid[self.vox.idx(x, y, z)]][0]

    def clear(self, x, y, z):
        return all(self.block(x, h, z) == 'minecraft:air' for h in (y, y + 1))

    def test_stable_scatter_contract_and_loot(self):
        self.assertEqual(list(self.captures), ['graveyard'])
        self.assertEqual((self.vox.sx, self.vox.sy, self.vox.sz), (25, 13, 25))
        for key, value in {'w': 25, 'h': 13, 'd': 25, 'weight': 7, 'surf': ['grass', 'dark'], 'theme': 'dark',
                           'mobs': ['fc:undead', 'fc:undead_soldier', 'fc:undead_knight']}.items():
            self.assertEqual(self.entry[key], value)
        self.assertFalse(self.entry.get('door')); self.assertFalse(self.entry.get('cullis'))
        self.assertEqual(self.tables['CHEST_LOOT']['fc:graveyard'], [
            ['fc:ectoplasm', 2, 5, 1], ['fc:will_potion', 1, 2, 0.6], ['fc:silver_key', 1, 1, 0.3],
            ['fc:banshees_tear', 1, 1, 0.2], ['fc:orb_will', 1, 2, 0.5]])

    def test_no_clipped_writes_and_known_palette(self):
        self.assertEqual(self.clipped, [])
        names = {self.vox.palette[i][0] for i in self.vox.grid}
        self.assertLessEqual(names - {'minecraft:air'}, BLOCK_COLORS.keys())

    def test_stone_sarcophagi_and_chest_clearance(self):
        for x, z in ((12, 4), (10, 3), (14, 3)):
            for zz in (z, z + 1):
                self.assertEqual(self.block(x, 1, zz), 'minecraft:chiseled_stone_bricks')
                self.assertEqual(self.block(x, 2, zz), 'minecraft:stone_brick_slab')
        self.assertEqual(self.block(12, 1, 2), 'minecraft:chest')
        self.assertEqual(self.block(12, 2, 2), 'minecraft:air')
        self.assertTrue(self.clear(12, 1, 3))

    def test_keeper_hut_has_floor_roof_and_accessible_workbench(self):
        self.assertEqual(self.block(21, 1, 17), 'minecraft:crafting_table')
        self.assertEqual(self.block(22, 1, 21), 'minecraft:barrel')
        self.assertEqual(self.block(20, 0, 20), 'minecraft:spruce_planks')
        self.assertEqual(self.block(20, 8, 20), 'minecraft:spruce_planks')
        for z in (19, 20): self.assertTrue(self.clear(16, 1, z))

    def test_connected_level_routes_from_south_gate(self):
        # Conservative two-block-tall standing columns, full supporting blocks.
        walkable = {(x,z) for x in range(25) for z in range(25)
                    if self.clear(x, 1, z) and self.block(x, 0, z) not in ('minecraft:air', 'minecraft:water')}
        queue = deque([(12,24)]); reached = {(12,24)}
        while queue:
            x,z = queue.popleft()
            for p in ((x-1,z),(x+1,z),(x,z-1),(x,z+1)):
                if p in walkable and p not in reached: reached.add(p); queue.append(p)
        for destination in ((12,3),(11,4),(13,4),(20,20),(21,18),(21,21),(20,8)):
            self.assertIn(destination, reached, f'Blocked route to {destination}')
        for local in self.entry['mobSpawns']:
            self.assertEqual(local[1], 1)
            self.assertIn((int(local[0]),int(local[2])), reached)

    def test_three_wide_north_facing_stairs_and_sealed_face(self):
        for z,y in ((7,1),(6,2),(5,3)):
            for x in range(19,22):
                name, states = self.vox.palette[self.vox.grid[self.vox.idx(x,y,z)]]
                self.assertEqual(name, 'minecraft:stone_brick_stairs')
                self.assertEqual(states, {'weirdo_direction': 3, 'upside_down_bit': False})
                self.assertTrue(self.clear(x,y+1,z))
        for x in range(19,22): self.assertTrue(self.clear(x,4,4))
        for x in (19,21): self.assertEqual(self.block(x,8,3), 'minecraft:deepslate_tiles')
        self.assertEqual(self.block(20,7,4), 'minecraft:chiseled_stone_bricks')
        self.assertNotEqual(self.block(20,4,3), 'minecraft:air')

    def test_actual_runtime_spawns_use_clear_voxel_positions(self):
        blocks = {f'{x},{y},{z}': self.block(x,y,z) for x in range(25) for y in range(13) for z in range(25)}
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'graveyard.json'; path.write_text(json.dumps(blocks))
            result = subprocess.run(['node', 'scripts/tests/graveyard_placement.cjs', str(path)], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        print(result.stdout.strip())


if __name__ == '__main__': unittest.main(verbosity=2)

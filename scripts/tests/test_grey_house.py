"""Grey House routes, cellar encounter and actual scatter initialization."""
from collections import deque
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
from structure_contract import ROOT, MANIFEST, runtime_tables


class GreyHouse(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.captured, cls.clipped = {}, []
        original = GS.Vox.set
        def bounded(v, x, y, z, *args, **kwargs):
            if not (0 <= x < v.sx and 0 <= y < v.sy and 0 <= z < v.sz):
                cls.clipped.append((x, y, z))
            return original(v, x, y, z, *args, **kwargs)
        with patch.object(GS.Vox, 'save', lambda v, n: cls.captured.setdefault(n, v)), patch.object(GS.Vox, 'set', bounded):
            GS.grey_house()
        cls.vox = cls.captured['grey_house']
        cls.tables = runtime_tables(ROOT)
        cls.entry = next(e for e in cls.tables['STRUCTS'] if e['id'] == 'fc:grey_house')

    def block(self, x, y, z):
        if not (0 <= x < self.vox.sx and 0 <= y < self.vox.sy and 0 <= z < self.vox.sz):
            return None
        return self.vox.palette[self.vox.grid[self.vox.idx(x, y, z)]][0]

    def clear(self, x, y, z):
        return all(self.block(x, h, z) == 'minecraft:air' for h in (y, y + 1))

    def reached(self):
        support = {'minecraft:grass_block', 'minecraft:gravel', 'minecraft:cobblestone',
                   'minecraft:stone_brick_stairs', 'minecraft:dark_oak_planks',
                   'minecraft:stone_bricks', 'minecraft:cracked_stone_bricks', 'minecraft:mossy_stone_bricks'}
        walkable = {(x, y, z) for x in range(31) for y in range(1, 7) for z in range(35)
                    if self.clear(x, y, z) and self.block(x, y - 1, z) in support}
        reached = {(15, 1, 0)}
        queue = deque(reached)
        while queue:
            x, y, z = queue.popleft()
            for xx, zz in ((x-1, z), (x+1, z), (x, z-1), (x, z+1)):
                for yy in (y-1, y, y+1):
                    point = (xx, yy, zz)
                    # A step up also needs clearance above the lower standing cell.
                    low = (x, y+2, z) if yy > y else (xx, yy+2, zz)
                    if yy != y and self.block(*low) != 'minecraft:air':
                        continue
                    if point in walkable and point not in reached:
                        reached.add(point)
                        queue.append(point)
        return reached

    def test_dimensions_palette_and_registration(self):
        self.assertEqual(list(self.captured), ['grey_house'])
        self.assertEqual((self.vox.sx, self.vox.sy, self.vox.sz), (31, 20, 35))
        entry = next(e for e in json.loads(MANIFEST.read_text())['structures'] if e['name'] == 'grey_house')
        self.assertEqual(entry['size'], [31, 20, 35])
        for key, value in {'w':31, 'h':20, 'd':35, 'weight':5, 'surf':['grass','rock'],
                           'theme':'dark', 'loot':'grey_house', 'door':False, 'cullis':False}.items():
            self.assertEqual(self.entry[key], value)
        self.assertEqual(self.clipped, [])
        self.assertLessEqual({self.vox.palette[i][0] for i in self.vox.grid} - {'minecraft:air'}, BLOCK_COLORS.keys())

    def test_manor_roof_windows_and_cellar_coffins(self):
        for z in (11, 20, 29): self.assertEqual(self.block(15, 19, z), 'minecraft:deepslate_tiles')
        self.assertEqual(self.block(20, 17, 25), 'minecraft:cracked_stone_bricks')
        self.assertEqual(self.block(10, 8, 12), 'minecraft:glass_pane')
        self.assertTrue(self.clear(15, 6, 12))
        self.assertEqual(self.block(15, 5, 20), 'minecraft:dark_oak_planks')
        self.assertEqual(self.block(8, 2, 20), 'minecraft:stone_bricks')
        for x in (14, 18):
            self.assertEqual(self.block(x, 1, 21), 'minecraft:chiseled_stone_bricks')
            for z in (22, 23): self.assertEqual(self.block(x, 1, z), 'minecraft:polished_deepslate')

    def test_stair_directions_and_headroom(self):
        for xs, zs, direction in ((range(14,17), range(4,9), 2), (range(10,12), range(14,18), 3)):
            for x in xs:
                for z in zs:
                    y = z-3 if direction == 2 else 18-z
                    self.assertEqual(self.block(x,y,z), 'minecraft:stone_brick_stairs')
                    states = self.vox.palette[self.vox.grid[self.vox.idx(x,y,z)]][1]
                    self.assertEqual(states, {'weirdo_direction':direction, 'upside_down_bit':False})
                    self.assertTrue(self.clear(x,y+1,z))

    def test_routes_to_manor_cellar_chests_and_spawns(self):
        reached = self.reached()
        targets = [(15,6,12), (10,6,13), (11,6,13), (10,1,18), (11,1,18),
                   (19,6,15), (20,1,25), (15,1,22), (19,1,22)]
        targets += [tuple(map(int, p)) for p in self.entry['mobSpawns']]
        for point in targets: self.assertIn(point, reached, f'Blocked north-entry route: {point}')

    def test_exact_chests_clear_lids_and_ordinary_loot(self):
        chests = {(x,y,z) for x in range(31) for y in range(20) for z in range(35)
                  if self.block(x,y,z) == 'minecraft:chest'}
        self.assertEqual(chests, {(20,6,15), (20,1,26)})
        for x,y,z in chests: self.assertEqual(self.block(x,y+1,z), 'minecraft:air')
        self.assertEqual({e[0] for e in self.tables['CHEST_LOOT']['fc:grey_house']},
                         {'fc:ectoplasm', 'fc:will_potion', 'fc:gold_coin'})

    def test_blocked_cellar_and_chest_lid_negative_fixtures(self):
        original = self.vox.grid.copy()
        try:
            self.vox.fill(10,1,17,11,8,17, GS.STONE)
            with self.assertRaises(AssertionError):
                self.test_routes_to_manor_cellar_chests_and_spawns()
            self.vox.set(20,2,26, GS.STONE)
            with self.assertRaises(AssertionError):
                self.test_exact_chests_clear_lids_and_ordinary_loot()
        finally:
            self.vox.grid[:] = original

    def test_actual_scatter_encounter_loot_and_saved_region(self):
        self.assertEqual(self.entry['mobs'], ['fc:undead','fc:undead_soldier','fc:undead'])
        blocks = {f'{x},{y},{z}':self.block(x,y,z) for x in range(31) for y in range(20) for z in range(35)}
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/'grey_house.json'
            path.write_text(json.dumps(blocks))
            result = subprocess.run(['node','scripts/tests/poi_population.cjs',str(path),'grey_house'],
                                    cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        print(result.stdout.strip())


if __name__ == '__main__': unittest.main(verbosity=2)

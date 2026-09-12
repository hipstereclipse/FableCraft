"""W2.1 generated geometry, walking routes and actual scatter population."""
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
from structure_contract import ROOT, MANIFEST, runtime_tables

if os.environ.get('FC_BOWERSTONE_TEST_SOURCE'):
    spec = importlib.util.spec_from_file_location('old_structures', os.environ['FC_BOWERSTONE_TEST_SOURCE'])
    GS = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(GS)


class BowerstoneNorth(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.captures, cls.clipped = {}, []
        original = GS.Vox.set
        def bounded(v, x, y, z, *args, **kwargs):
            if not (0 <= x < v.sx and 0 <= y < v.sy and 0 <= z < v.sz):
                cls.clipped.append((x, y, z))
            return original(v, x, y, z, *args, **kwargs)
        with patch.object(GS.Vox, 'save', lambda v,n: cls.captures.setdefault(n,v)), patch.object(GS.Vox, 'set', bounded):
            GS.bowerstone_market()
        cls.vox = cls.captures['bowerstone_market']
        cls.tables = runtime_tables(ROOT)
        cls.entry = next(e for e in cls.tables['STRUCTS'] if e['id'] == 'fc:bowerstone_market')

    def block(self, x, y, z):
        if not (0 <= x < self.vox.sx and 0 <= y < self.vox.sy and 0 <= z < self.vox.sz):
            return None
        return self.vox.palette[self.vox.grid[self.vox.idx(x,y,z)]][0]

    def clear(self, x, y, z):
        return all(self.block(x,h,z) == 'minecraft:air' for h in (y,y+1))

    def test_manifest_runtime_palette_bounds_and_residents(self):
        self.assertEqual(list(self.captures), ['bowerstone_market'])
        self.assertEqual((self.vox.sx,self.vox.sy,self.vox.sz), (37,21,59))
        entry = next(e for e in json.loads(MANIFEST.read_text())['structures'] if e['name'] == 'bowerstone_market')
        self.assertEqual(entry['size'], [37,21,59])
        for key,value in {'w':37,'h':21,'d':59,'weight':7,'surf':['grass'],'theme':'village','cullis':True,
                          'mobs':['fc:guard_bowerstone','fc:trader','fc:barkeep','fc:villager_albion','fc:lady_grey']}.items():
            self.assertEqual(self.entry[key], value)
        self.assertFalse(self.entry.get('door'))
        self.assertEqual(self.clipped, [])
        self.assertLessEqual({self.vox.palette[i][0] for i in self.vox.grid} - {'minecraft:air'}, BLOCK_COLORS.keys())

    def test_manor_two_floors_windows_furnishings_and_open_door(self):
        for x in range(17,20):
            self.assertTrue(self.clear(x,1,15))
            self.assertEqual(self.block(x,5,10), 'minecraft:dark_oak_planks')
            self.assertEqual(self.block(x,6,15), 'minecraft:glass_pane')
        self.assertEqual(self.block(18,19,10), 'minecraft:deepslate_tiles')
        self.assertEqual(self.block(11,2,6), 'minecraft:bookshelf')
        self.assertEqual(self.block(12,1,12), 'minecraft:chest')
        self.assertEqual(self.block(12,6,6), 'minecraft:red_wool')
        self.assertEqual(self.block(15,6,5), 'minecraft:barrel')

    def test_class_wall_forecourt_and_connected_wealthy_street(self):
        for x in range(1,36):
            if 15 <= x <= 21:
                continue
            self.assertEqual(self.block(x,1,37), 'minecraft:stone_bricks')
        for x in range(17,20):
            self.assertTrue(self.clear(x,2,37))
            for z in range(16,36):
                self.assertTrue(self.clear(x,1,z))
        for x in (9,27):
            self.assertEqual(self.block(x,2,20), 'minecraft:iron_bars')
        for x in (12,24):
            self.assertEqual(self.block(x,1,19), 'minecraft:oak_leaves')
        # Retained rich houses: quartz trim, ground entrances and interior chests.
        for x in (3,24):
            self.assertEqual(self.block(x,4,27), 'minecraft:quartz_block')
        for x in (8,29):
            self.assertTrue(self.clear(x,1,28))

    def test_stair_clearance_directions_and_landing(self):
        for i in range(5):
            for x in (23,24):
                y,z = i+1,12-i
                self.assertEqual(self.block(x,y,z), 'minecraft:stone_brick_stairs')
                self.assertEqual(self.vox.palette[self.vox.grid[self.vox.idx(x,y,z)]][1]['weirdo_direction'], 3)
                self.assertTrue(self.clear(x,y+1,z))
        self.assertTrue(self.clear(23,6,7))
        self.assertEqual(self.block(23,5,7), 'minecraft:dark_oak_planks')
        for z,direction in ((36,2),(44,3)):
            self.assertEqual(self.block(18,1,z), 'minecraft:stone_brick_stairs')
            self.assertEqual(self.vox.palette[self.vox.grid[self.vox.idx(18,1,z)]][1]['weirdo_direction'], direction)

    def test_south_to_manor_spawns_cullis_and_chest_access(self):
        # Conservative full-cell floor model with <=1 step rise. It checks route
        # connectivity and headroom, not Bedrock stair or partial-block collision.
        support = {'minecraft:stone_bricks','minecraft:deepslate_tiles','minecraft:gravel',
                   'minecraft:cobblestone','minecraft:dark_oak_planks','minecraft:stone_brick_stairs','minecraft:moss_block'}
        walkable = {(x,y,z) for x in range(self.vox.sx) for y in range(1,8) for z in range(self.vox.sz)
                    if self.clear(x,y,z) and self.block(x,y-1,z) in support}
        reached = {(18,1,58)}
        queue = deque(reached)
        while queue:
            x,y,z = queue.popleft()
            for xx,zz in ((x-1,z),(x+1,z),(x,z-1),(x,z+1)):
                for yy in (y-1,y,y+1):
                    point = (xx,yy,zz)
                    if point in walkable and point not in reached:
                        reached.add(point); queue.append(point)
        targets = [(18,2,40),(18,1,29),(18,1,22),(18,1,14),(18,1,9),(23,6,7),(18,6,12)]
        targets += [tuple(map(int,p)) for p in self.entry['mobSpawns']]
        for point in targets:
            self.assertIn(point, reached, f'Blocked south-entry route: {point}')
        chests = [(x,y,z) for x in range(self.vox.sx) for y in range(self.vox.sy) for z in range(self.vox.sz)
                  if self.block(x,y,z) == 'minecraft:chest']
        self.assertEqual(len(chests), 8)  # seven retained, one manor storage chest
        for x,y,z in chests:
            self.assertEqual(self.block(x,y+1,z), 'minecraft:air')
            self.assertTrue(any(p in reached for p in ((x-1,y,z),(x+1,y,z),(x,y,z-1),(x,y,z+1))), f'Inaccessible chest {(x,y,z)}')

    def test_actual_scatter_population_travel_and_saved_region(self):
        blocks = {f'{x},{y},{z}':self.block(x,y,z) for x in range(self.vox.sx) for y in range(self.vox.sy) for z in range(self.vox.sz)}
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/'bowerstone.json'; path.write_text(json.dumps(blocks))
            result = subprocess.run(['node','scripts/tests/poi_population.cjs',str(path),'bowerstone_market'], cwd=ROOT, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stdout+result.stderr)
            poisoned = Path(directory)/'main.js'
            original = (ROOT/'packs/Fablecraft_BP/scripts/main.js').read_text()
            needle = '{ x: cxw, y: floorY, z: czw });'
            self.assertEqual(original.count(needle), 1)
            poisoned.write_text(original.replace(needle, '{ x: cxw, y: floorY, z: czw + 1 });'))
            rejected = subprocess.run(['node','scripts/tests/poi_population.cjs',str(path),'bowerstone_market'],
                cwd=ROOT, capture_output=True, text=True, env=dict(os.environ, FC_STRUCTURE_TEST_SOURCE=str(poisoned)))
            self.assertNotEqual(rejected.returncode, 0, 'Harness swallowed a wrong Cullis location')
            self.assertIn('AssertionError', rejected.stderr)
        print(result.stdout.strip())


if __name__ == '__main__':
    unittest.main(verbosity=2)

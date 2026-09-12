"""Bargate landmarks, vertical routes and actual scatter initialization."""
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


class BargatePrison(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.captured, cls.clipped = {}, []
        original = GS.Vox.set
        def bounded(v, x, y, z, *args, **kwargs):
            if not (0 <= x < v.sx and 0 <= y < v.sy and 0 <= z < v.sz):
                cls.clipped.append((x,y,z))
            return original(v,x,y,z,*args,**kwargs)
        with patch.object(GS.Vox,'save',lambda v,n:cls.captured.setdefault(n,v)), patch.object(GS.Vox,'set',bounded):
            GS.bargate_prison()
        cls.vox = cls.captured['bargate_prison']
        cls.tables = runtime_tables(ROOT)
        cls.entry = next(e for e in cls.tables['STRUCTS'] if e['id'] == 'fc:bargate_prison')

    def block(self,x,y,z):
        if not (0 <= x < self.vox.sx and 0 <= y < self.vox.sy and 0 <= z < self.vox.sz): return None
        return self.vox.palette[self.vox.grid[self.vox.idx(x,y,z)]][0]

    def clear(self,x,y,z):
        return all(self.block(x,h,z) == 'minecraft:air' for h in (y,y+1))

    def reached(self):
        support = {'minecraft:cobblestone','minecraft:stone_bricks','minecraft:mossy_stone_bricks',
                   'minecraft:cracked_stone_bricks','minecraft:dark_oak_planks','minecraft:stone_brick_stairs'}
        walkable = {(x,y,z) for x in range(41) for y in range(1,12) for z in range(49)
                    if self.clear(x,y,z) and self.block(x,y-1,z) in support}
        reached = {(20,1,0)}; queue = deque(reached)
        while queue:
            x,y,z = queue.popleft()
            for xx,zz in ((x-1,z),(x+1,z),(x,z-1),(x,z+1)):
                for yy in (y-1,y,y+1):
                    point = (xx,yy,zz)
                    low = (x,y+2,z) if yy > y else (xx,yy+2,zz)
                    if yy != y and self.block(*low) != 'minecraft:air': continue
                    if point in walkable and point not in reached:
                        reached.add(point); queue.append(point)
        return reached

    def test_dimensions_palette_and_runtime_flags(self):
        self.assertEqual(list(self.captured),['bargate_prison'])
        self.assertEqual((self.vox.sx,self.vox.sy,self.vox.sz),(41,20,49))
        entry = next(e for e in json.loads(MANIFEST.read_text())['structures'] if e['name']=='bargate_prison')
        self.assertEqual(entry['size'],[41,20,49])
        for k,v in {'w':41,'h':20,'d':49,'weight':4,'surf':['grass','rock'],'theme':'dark',
                    'loot':'bargate_prison','door':False,'cullis':False}.items(): self.assertEqual(self.entry[k],v)
        self.assertEqual(self.clipped,[])
        self.assertLessEqual({self.vox.palette[i][0] for i in self.vox.grid}-{'minecraft:air'},BLOCK_COLORS.keys())

    def test_two_open_cell_blocks_and_third_sealed_silhouette(self):
        for x0 in (7,25):
            self.assertEqual(self.block(x0+4,14,20),'minecraft:deepslate_tiles')
            for z in (19,25): self.assertTrue(self.clear(x0+4,6,z))
            self.assertEqual(self.block(x0+4,6,22),'minecraft:iron_bars')
        self.assertEqual(self.block(20,15,40),'minecraft:deepslate_tiles')
        self.assertEqual(self.block(18,7,35),'minecraft:iron_bars')
        reached = self.reached()
        self.assertNotIn((20,6,38),reached)

    def test_barracks_office_torture_and_underground_basin(self):
        self.assertEqual(self.block(31,6,35),'minecraft:white_wool')
        self.assertEqual(self.block(12,12,36),'minecraft:lectern')
        self.assertEqual(self.block(14,12,40),'minecraft:bookshelf')
        self.assertEqual(self.block(9,8,36),'minecraft:iron_bars')
        self.assertEqual(self.block(26,0,25),'minecraft:water')
        self.assertTrue(self.clear(23,1,25))
        for x in (16,24):
            self.assertEqual(self.block(x,7,5),'minecraft:blue_wool')
            self.assertEqual(self.block(x,8,5),'minecraft:white_wool')

    def test_routes_to_four_ramparts_cells_office_and_chamber(self):
        reached = self.reached()
        targets = [(20,6,8),(3,11,20),(37,11,20),(20,11,7),(20,11,45),
                   (9,6,19),(9,6,25),(31,6,19),(31,6,25),(27,6,37),
                   (13,6,38),(8,11,39),(13,11,40),(30,6,41),(30,1,29),
                   (23,1,25),(29,1,25)]
        targets += [tuple(map(int,p)) for p in self.entry['mobSpawns']]
        for p in targets: self.assertTrue(p in reached,f'Blocked north-entry route: {p}')

    def test_stairs_orientation_clearance_and_exact_chests(self):
        flights = [(range(19,22),range(1,6),lambda z:z,2),
                   (range(5,7),range(9,14),lambda z:z-3,2),
                   (range(5,7),range(34,39),lambda z:z-28,2),
                   (range(20,22),range(12,16),lambda z:16-z,3)]
        for xs,zs,height,direction in flights:
            for x in xs:
                for z in zs:
                    y = height(z)
                    self.assertEqual(self.block(x,y,z),'minecraft:stone_brick_stairs')
                    self.assertEqual(self.vox.palette[self.vox.grid[self.vox.idx(x,y,z)]][1],
                                     {'weirdo_direction':direction,'upside_down_bit':False})
                    self.assertTrue(self.clear(x,y+1,z))
        chests = {(x,y,z) for x in range(41) for y in range(20) for z in range(49) if self.block(x,y,z)=='minecraft:chest'}
        self.assertEqual(chests,{(13,11,41),(31,6,41),(30,1,30)})
        for x,y,z in chests: self.assertEqual(self.block(x,y+1,z),'minecraft:air')
        self.assertEqual({e[0] for e in self.tables['CHEST_LOOT']['fc:bargate_prison']},
                         {'fc:gold_coin','fc:health_potion','fc:red_meat'})

    def test_blocked_chamber_and_closed_cell_negative_fixtures(self):
        original = self.vox.grid.copy()
        try:
            self.vox.fill(20,1,16,21,4,16,GS.STONE)
            with self.assertRaises(AssertionError): self.test_routes_to_four_ramparts_cells_office_and_chamber()
            self.vox.grid[:] = original
            self.vox.fill(11,6,19,11,7,20,GS.IRON_BARS)
            with self.assertRaises(AssertionError): self.test_routes_to_four_ramparts_cells_office_and_chamber()
        finally: self.vox.grid[:] = original

    def test_actual_scatter_guards_loot_and_saved_region(self):
        self.assertEqual(self.entry['mobs'],['fc:guard_bowerstone']*3)
        blocks = {f'{x},{y},{z}':self.block(x,y,z) for x in range(41) for y in range(20) for z in range(49)}
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/'bargate.json';path.write_text(json.dumps(blocks))
            result = subprocess.run(['node','scripts/tests/poi_population.cjs',str(path),'bargate_prison'],cwd=ROOT,capture_output=True,text=True)
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)
        print(result.stdout.strip())


if __name__ == '__main__': unittest.main(verbosity=2)

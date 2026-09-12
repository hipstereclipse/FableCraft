"""W2.3 memorial landmarks, retained village and rectangular scatter contract."""
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

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import gen_structures as GS
from gen_screenshots import BLOCK_COLORS
from structure_contract import ROOT, MANIFEST, runtime_tables

if os.environ.get('FC_OAKVALE_TEST_SOURCE'):
    spec=importlib.util.spec_from_file_location('old_structures',os.environ['FC_OAKVALE_TEST_SOURCE'])
    GS=importlib.util.module_from_spec(spec);spec.loader.exec_module(GS)


class OakvaleMemorial(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cap,cls.clipped={},[];original=GS.Vox.set
        def bounded(v,x,y,z,*args,**kwargs):
            if not (0<=x<v.sx and 0<=y<v.sy and 0<=z<v.sz):cls.clipped.append((x,y,z))
            return original(v,x,y,z,*args,**kwargs)
        with patch.object(GS.Vox,'save',lambda v,n:cls.cap.setdefault(n,v)),patch.object(GS.Vox,'set',bounded):GS.oakvale_village()
        cls.vox=cls.cap['oakvale_village'];cls.tables=runtime_tables(ROOT)
        cls.entry=next(s for s in cls.tables['STRUCTS'] if s['id']=='fc:oakvale_village')

    def block(self,x,y,z):
        if not (0<=x<self.vox.sx and 0<=y<self.vox.sy and 0<=z<self.vox.sz):return None
        return self.vox.palette[self.vox.grid[self.vox.idx(x,y,z)]][0]

    def clear(self,x,y,z):return all(self.block(x,h,z)=='minecraft:air' for h in (y,y+1))

    def test_dimensions_palette_and_retained_runtime_contract(self):
        self.assertEqual(list(self.cap),['oakvale_village'])
        self.assertEqual((self.vox.sx,self.vox.sy,self.vox.sz),(53,14,35))
        self.assertEqual(next(e for e in json.loads(MANIFEST.read_text())['structures'] if e['name']=='oakvale_village')['size'],[53,14,35])
        for k,v in {'w':53,'h':14,'d':35,'weight':8,'surf':['grass','sand'],'theme':'village','cullis':True,
                    'mobs':['fc:villager_farmer','fc:villager_fisher','fc:guard_oakvale']}.items():self.assertEqual(self.entry[k],v)
        self.assertFalse(self.entry.get('door'));self.assertEqual(self.clipped,[])
        self.assertLessEqual({self.vox.palette[i][0] for i in self.vox.grid}-{'minecraft:air'},BLOCK_COLORS.keys())

    def test_raised_garden_gate_stairs_and_grave_rows(self):
        for x,y in ((35,1),(36,2)):
            for z in range(16,19):
                self.assertEqual(self.block(x,y,z),'minecraft:stone_brick_stairs')
                self.assertEqual(self.vox.palette[self.vox.grid[self.vox.idx(x,y,z)]][1]['weirdo_direction'],0)
                self.assertTrue(self.clear(x,y+1,z))
        for z in range(16,19):self.assertTrue(self.clear(37,3,z))
        for x in (40,44,48):
            for z in (9,22):
                self.assertEqual(self.block(x,3,z),'minecraft:chiseled_stone_bricks')
                self.assertEqual(self.block(x,4,z),'minecraft:stone_brick_wall')
        self.assertEqual(self.block(51,3,17),'minecraft:mossy_stone_bricks')
        self.assertEqual(self.block(37,6,15),'minecraft:lantern')

    def test_hero_separate_legs_head_and_raised_broad_axe(self):
        self.assertEqual(self.block(44,4,13),'minecraft:chiseled_stone_bricks')
        for x in (43,45):self.assertEqual(self.block(x,5,13),'minecraft:stone_bricks')
        self.assertEqual(self.block(44,5,13),'minecraft:air')
        self.assertEqual(self.block(44,9,13),'minecraft:smooth_quartz')
        for y in range(8,12):self.assertEqual(self.block(46,y,13),'minecraft:polished_deepslate')
        for x in (47,48):
            for y in (10,11):self.assertEqual(self.block(x,y,13),'minecraft:polished_deepslate')

    def test_retained_oak_well_field_coast_and_chest_coordinates(self):
        self.assertTrue(self.clear(28,1,13))  # old squeezed statue is gone
        self.assertEqual(self.block(21,1,17),'minecraft:oak_log')
        self.assertEqual(self.block(21,8,17),'minecraft:oak_leaves')
        self.assertEqual(self.block(14,1,18),'minecraft:water')
        self.assertEqual(self.block(6,3,15),'minecraft:carved_pumpkin')
        self.assertEqual(self.block(17,1,30),'minecraft:spruce_planks')
        self.assertEqual(self.block(30,0,33),'minecraft:water')
        chests={(x,y,z) for x in range(self.vox.sx) for y in range(self.vox.sy) for z in range(self.vox.sz) if self.block(x,y,z)=='minecraft:chest'}
        self.assertEqual(chests,{(10,1,11),(11,1,21),(19,2,27),(28,1,11),(28,1,21)})

    def test_north_gate_to_garden_statue_graves_residents_and_cullis(self):
        support={'minecraft:grass_block','minecraft:coarse_dirt','minecraft:dirt_path','minecraft:gravel',
                 'minecraft:sand','minecraft:cobblestone','minecraft:spruce_planks','minecraft:stone_brick_stairs'}
        walkable={(x,y,z) for x in range(self.vox.sx) for y in range(1,5) for z in range(self.vox.sz)
                  if self.clear(x,y,z) and self.block(x,y-1,z) in support}
        reached={(17,1,0)};queue=deque(reached)
        while queue:
            x,y,z=queue.popleft()
            for xx,zz in ((x-1,z),(x+1,z),(x,z-1),(x,z+1)):
                for yy in (y-1,y,y+1):
                    point=(xx,yy,zz)
                    if point in walkable and point not in reached:reached.add(point);queue.append(point)
        targets=[(17,1,15),(26,1,17),(34,1,16),(38,3,17),(44,3,17),(44,3,15),(20,1,17),(17,1,18)]
        targets += [(x,3,z) for x in (40,44,48) for z in (10,21)]
        targets += [tuple(map(int,p)) for p in self.entry['mobSpawns']]
        for p in targets:self.assertTrue(p in reached,f'Blocked north-entry route: {p}')

    def test_actual_scatter_population_cullis_and_saved_region(self):
        blocks={f'{x},{y},{z}':self.block(x,y,z) for x in range(self.vox.sx) for y in range(self.vox.sy) for z in range(self.vox.sz)}
        with tempfile.TemporaryDirectory() as directory:
            p=Path(directory)/'oakvale.json';p.write_text(json.dumps(blocks))
            r=subprocess.run(['node','scripts/tests/poi_population.cjs',str(p),'oakvale_village'],cwd=ROOT,capture_output=True,text=True)
        self.assertEqual(r.returncode,0,r.stdout+r.stderr);print(r.stdout.strip())


if __name__=='__main__':unittest.main(verbosity=2)

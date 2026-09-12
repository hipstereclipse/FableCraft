"""W2.2 climbable lighthouse, terrace/graves and actual resident placement."""
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

if os.environ.get('FC_HOOK_COAST_TEST_SOURCE'):
    spec = importlib.util.spec_from_file_location('old_structures', os.environ['FC_HOOK_COAST_TEST_SOURCE'])
    GS = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(GS)


class HookCoast(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.captures, cls.clipped = {}, []
        original = GS.Vox.set
        def bounded(v,x,y,z,*args,**kwargs):
            if not (0 <= x < v.sx and 0 <= y < v.sy and 0 <= z < v.sz):
                cls.clipped.append((x,y,z))
            return original(v,x,y,z,*args,**kwargs)
        with patch.object(GS.Vox,'save',lambda v,n:cls.captures.setdefault(n,v)), patch.object(GS.Vox,'set',bounded):
            GS.hook_coast()
        cls.vox = cls.captures['hook_coast']
        cls.entry = next(e for e in runtime_tables(ROOT)['STRUCTS'] if e['id']=='fc:hook_coast')

    def block(self,x,y,z):
        if not (0 <= x < self.vox.sx and 0 <= y < self.vox.sy and 0 <= z < self.vox.sz):
            return None
        return self.vox.palette[self.vox.grid[self.vox.idx(x,y,z)]][0]

    def clear(self,x,y,z):
        return all(self.block(x,h,z)=='minecraft:air' for h in (y,y+1))

    def test_stable_dimensions_palette_population_and_new_anchors(self):
        self.assertEqual(list(self.captures),['hook_coast'])
        self.assertEqual((self.vox.sx,self.vox.sy,self.vox.sz),(37,20,37))
        entry=next(e for e in json.loads(MANIFEST.read_text())['structures'] if e['name']=='hook_coast')
        self.assertEqual(entry['size'],[37,20,37])
        for k,v in {'w':37,'h':20,'d':37,'weight':7,'surf':['snow','sand','rock'],'theme':'snow','cullis':True,
                    'mobs':['fc:oracle','fc:guard_snowspire','fc:villager_woman']}.items():
            self.assertEqual(self.entry[k],v)
        self.assertFalse(self.entry.get('door'))
        self.assertEqual(self.clipped,[])
        self.assertLessEqual({self.vox.palette[i][0] for i in self.vox.grid}-{'minecraft:air'},BLOCK_COLORS.keys())
        for x,y,z in self.entry['mobSpawns']:
            self.assertTrue(self.clear(int(x),y,int(z)))
            self.assertNotIn(self.block(int(x),y-1,int(z)), (None, "minecraft:air", "minecraft:water"))

    def test_lighthouse_internal_stairs_landing_beacon_and_foundation(self):
        steps=([(4,i+1,26+i,2) for i in range(4)]+[(x,x,30,0) for x in range(5,9)]+[(8,9+i,29-i,3) for i in range(3)])
        for x,y,z,direction in steps:
            self.assertEqual(self.block(x,y,z),'minecraft:stone_brick_stairs')
            self.assertEqual(self.vox.palette[self.vox.grid[self.vox.idx(x,y,z)]][1]['weirdo_direction'],direction)
            self.assertTrue(self.clear(x,y+1,z))
        for p in ((4,5,30),(7,12,27)):
            self.assertTrue(self.clear(*p))
            self.assertEqual(self.block(p[0],p[1]-1,p[2]),'minecraft:polished_diorite')
        self.assertEqual(self.block(6,12,28),'minecraft:sea_lantern')
        self.assertEqual(self.block(6,0,32),'minecraft:polished_diorite')

    def test_abbey_terrace_stairs_clear_aisle_and_retained_bell(self):
        for x,y in ((24,1),(25,2)):
            for z in (24,25):
                self.assertEqual(self.block(x,y,z),'minecraft:stone_brick_stairs')
                self.assertTrue(self.clear(x,y+1,z))
        for z in range(19,26):
            self.assertTrue(self.clear(30,3,z))
            self.assertIsNotNone(self.block(30,2,z))
        self.assertEqual(self.block(30,3,18),'minecraft:beacon')
        self.assertEqual(self.block(29,4,16),'minecraft:light_blue_stained_glass_pane')
        self.assertEqual(self.block(32,6,23),'minecraft:bell')

    def test_graveyard_rows_bell_and_cottage_door_headroom(self):
        for x in (28,30,32):
            for z in (9,12):
                self.assertEqual(self.block(x,1,z),'minecraft:chiseled_stone_bricks')
                self.assertEqual(self.block(x,2,z),'minecraft:polished_diorite')
        self.assertEqual(self.block(30,3,5),'minecraft:bell')
        for bx,bz in ((12,8),(20,8),(12,16),(20,16)):
            self.assertTrue(self.clear(bx+3,1,bz))

    def test_entry_routes_to_lamp_abbey_graves_residents_and_all_chests(self):
        support={'minecraft:calcite','minecraft:polished_diorite','minecraft:stone_brick_stairs',
                 'minecraft:spruce_stairs','minecraft:spruce_planks','minecraft:deepslate_tiles',
                 'minecraft:snow_block','minecraft:gravel'}
        walkable={(x,y,z) for x in range(37) for y in range(1,14) for z in range(37)
                  if self.clear(x,y,z) and self.block(x,y-1,z) in support}
        reached={(18,1,0)};queue=deque(reached)
        while queue:
            x,y,z=queue.popleft()
            for xx,zz in ((x-1,z),(x+1,z),(x,z-1),(x,z+1)):
                for yy in (y-1,y,y+1):
                    point=(xx,yy,zz)
                    if point in walkable and point not in reached:
                        reached.add(point);queue.append(point)
        for point in [(6,1,24),(7,12,27),(30,3,20),(30,1,6),(29,1,10),(31,1,13),(18,1,18),(18,2,28)]+[tuple(map(int,p)) for p in self.entry['mobSpawns']]:
            self.assertTrue(point in reached,f'Blocked north-entry route: {point}')
        chests=[(x,y,z) for x in range(37) for y in range(20) for z in range(37) if self.block(x,y,z)=='minecraft:chest']
        self.assertEqual(len(chests),5)
        for x,y,z in chests:
            self.assertEqual(self.block(x,y+1,z),'minecraft:air')
            self.assertTrue(any(p in reached for p in ((x-1,y,z),(x+1,y,z),(x,y,z-1),(x,y,z+1))),f'Inaccessible chest {(x,y,z)}')

    def test_actual_population_and_travel_on_supported_surfaces(self):
        blocks={f'{x},{y},{z}':self.block(x,y,z) for x in range(37) for y in range(20) for z in range(37)}
        with tempfile.TemporaryDirectory() as directory:
            p=Path(directory)/'hook.json';p.write_text(json.dumps(blocks))
            r=subprocess.run(['node','scripts/tests/poi_population.cjs',str(p),'hook_coast'],cwd=ROOT,capture_output=True,text=True)
        self.assertEqual(r.returncode,0,r.stdout+r.stderr);print(r.stdout.strip())


if __name__=='__main__':
    unittest.main(verbosity=2)

"""W1.4 rectangle, open approaches, stairs, landmark and runtime spawn contracts."""
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

if os.environ.get('FC_ARENA_TEST_SOURCE'):
    spec=importlib.util.spec_from_file_location('old_structures',os.environ['FC_ARENA_TEST_SOURCE'])
    GS=importlib.util.module_from_spec(spec);spec.loader.exec_module(GS)


class ArenaHalls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.captures,cls.clipped={},[];original=GS.Vox.set
        def bounded(v,x,y,z,*args,**kwargs):
            if not (0<=x<v.sx and 0<=y<v.sy and 0<=z<v.sz):cls.clipped.append((x,y,z))
            return original(v,x,y,z,*args,**kwargs)
        with patch.object(GS.Vox,'save',lambda v,n:cls.captures.setdefault(n,v)),patch.object(GS.Vox,'set',bounded):GS.arena_ring()
        cls.vox=cls.captures['arena_ring'];cls.tables=runtime_tables(ROOT)
        cls.entry=next(s for s in cls.tables['STRUCTS'] if s['id']=='fc:arena_ring')

    def block(self,x,y,z):
        if not (0<=x<self.vox.sx and 0<=y<self.vox.sy and 0<=z<self.vox.sz):return None
        return self.vox.palette[self.vox.grid[self.vox.idx(x,y,z)]][0]
    def clear(self,x,y,z):return all(self.block(x,h,z)=='minecraft:air' for h in (y,y+1))

    def test_dimensions_manifest_palette_and_population(self):
        self.assertEqual(list(self.captures),['arena_ring'])
        self.assertEqual((self.vox.sx,self.vox.sy,self.vox.sz),(27,12,41))
        self.assertEqual(next(s for s in json.loads(MANIFEST.read_text())['structures'] if s['name']=='arena_ring')['size'],[27,12,41])
        for k,v in {'w':27,'h':12,'d':41,'weight':5,'surf':['sand','rock','grass'],'theme':'dark',
                    'mobs':['fc:hobbe','fc:hobbe','fc:beetle','fc:trader']}.items():self.assertEqual(self.entry[k],v)
        self.assertFalse(self.entry.get('door'));self.assertFalse(self.entry.get('cullis'))
        self.assertEqual(self.clipped,[])
        self.assertLessEqual({self.vox.palette[i][0] for i in self.vox.grid}-{'minecraft:air'},BLOCK_COLORS.keys())
        self.assertEqual(self.tables['CHEST_LOOT']['fc:arena_ring'],[
            ['fc:gold_coin',6,16,1],['fc:ages_of_skill_potion',1,1,0.3],['fc:experience_augment',1,1,0.2],['fc:orb_skill',1,3,0.5]])

    def test_south_corridor_open_north_beast_gate_barred(self):
        for x in range(12,15):
            for z in range(21,41):
                self.assertTrue(self.clear(x,1,z));self.assertEqual(self.block(x,0,z),'minecraft:stone_bricks')
            self.assertEqual(self.block(x,1,5),'minecraft:iron_bars')

    def test_waiting_room_dummies_and_shop(self):
        for z in (30,35):
            self.assertEqual(self.block(5,1,z),'minecraft:hay_block')
            self.assertEqual(self.block(5,3,z),'minecraft:carved_pumpkin')
        self.assertEqual(self.block(8,2,36),'minecraft:brewing_stand')
        self.assertEqual(self.block(9,1,37),'minecraft:barrel')
        self.assertTrue(self.clear(9,1,34))
        for z in range(32,35):self.assertTrue(self.clear(11,1,z))

    def test_hall_figures_and_original_inward_statues(self):
        for x,z in ((18,30),(22,30),(18,36),(22,36)):
            self.assertEqual(self.block(x,1,z),'minecraft:chiseled_stone_bricks')
            self.assertEqual(self.block(x,4,z),'minecraft:smooth_quartz')
        for x,z,ix,iz in ((24,13,23,13),(13,24,13,23),(2,13,3,13),(13,2,13,3)):
            self.assertEqual(self.block(x,10,z),'minecraft:smooth_quartz')
            self.assertEqual(self.block(ix,10,iz),'minecraft:end_rod')
        self.assertTrue(self.clear(20,1,33))

    def test_stair_ascent_and_tier_landings(self):
        for x in range(6,0,-1):
            height=7-x
            for z in range(17,20):
                self.assertEqual(self.block(x,height,z),'minecraft:stone_brick_stairs')
                self.assertEqual(self.vox.palette[self.vox.grid[self.vox.idx(x,height,z)]][1],{'weirdo_direction':1,'upside_down_bit':False})
                self.assertTrue(self.clear(x,height+1,z))
        for x,y,z in ((3,5,16),(1,7,16)):
            self.assertTrue(self.clear(x,y,z));self.assertNotIn(self.block(x,y-1,z),(None,'minecraft:air'))

    def test_level_routes_to_every_room_and_spawn(self):
        walkable={(x,z) for x in range(27) for z in range(41) if self.clear(x,1,z) and self.block(x,0,z) not in (None,'minecraft:air','minecraft:water')}
        reached={(13,40)};queue=deque(reached)
        while queue:
            x,z=queue.popleft()
            for p in ((x-1,z),(x+1,z),(x,z-1),(x,z+1)):
                if p in walkable and p not in reached:reached.add(p);queue.append(p)
        for p in ((13,13),(7,18),(9,34),(10,37),(7,30),(7,35),(20,33),(20,29),(20,37)):
            self.assertTrue(p in reached,f'Blocked entry-to-landmark route: {p}')
        for x,y,z in self.entry['mobSpawns']:self.assertEqual(y,1);self.assertIn((int(x),int(z)),reached)

    def test_actual_runtime_population_rectangular_bounds_and_save(self):
        blocks={f'{x},{y},{z}':self.block(x,y,z) for x in range(self.vox.sx) for y in range(self.vox.sy) for z in range(self.vox.sz)}
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'arena.json';path.write_text(json.dumps(blocks))
            result=subprocess.run(['node','scripts/tests/poi_population.cjs',str(path),'arena_ring'],cwd=ROOT,capture_output=True,text=True)
        self.assertEqual(result.returncode,0,result.stdout+result.stderr);print(result.stdout.strip())


if __name__=='__main__':unittest.main(verbosity=2)

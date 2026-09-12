"""W1.3 camp rings, landmark routes and clear actual runtime population."""
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

if os.environ.get('FC_CAMP_TEST_SOURCE'):
    spec = importlib.util.spec_from_file_location('old_structures', os.environ['FC_CAMP_TEST_SOURCE'])
    GS = importlib.util.module_from_spec(spec); spec.loader.exec_module(GS)


class BanditCamp(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.captured, cls.clipped = {}, []
        original = GS.Vox.set
        def bounded(v,x,y,z,*args,**kwargs):
            if not (0 <= x < v.sx and 0 <= y < v.sy and 0 <= z < v.sz): cls.clipped.append((x,y,z))
            return original(v,x,y,z,*args,**kwargs)
        with patch.object(GS.Vox,'save',lambda v,n: cls.captured.setdefault(n,v)), patch.object(GS.Vox,'set',bounded): GS.bandit_camp()
        cls.vox=cls.captured['bandit_camp']
        cls.tables=runtime_tables(ROOT)
        cls.entry=next(s for s in cls.tables['STRUCTS'] if s['id']=='fc:bandit_camp')

    def block(self,x,y,z): return self.vox.palette[self.vox.grid[self.vox.idx(x,y,z)]][0]
    def clear(self,x,y,z): return all(self.block(x,h,z)=='minecraft:air' for h in (y,y+1))

    def test_registration_bounds_palette_and_loot(self):
        self.assertEqual(list(self.captured),['bandit_camp'])
        self.assertEqual((self.vox.sx,self.vox.sy,self.vox.sz),(33,13,33))
        for k,v in {'w':33,'h':13,'d':33,'weight':9,'surf':['grass','dark','rock'],'theme':'dark',
                    'mobs':['fc:bandit','fc:bandit','fc:bandit_archer','fc:twinblade']}.items(): self.assertEqual(self.entry[k],v)
        self.assertFalse(self.entry.get('door')); self.assertFalse(self.entry.get('cullis'))
        self.assertEqual(self.clipped,[])
        names={self.vox.palette[i][0] for i in self.vox.grid}
        self.assertLessEqual(names-{'minecraft:air'},BLOCK_COLORS.keys())
        self.assertEqual(self.tables['CHEST_LOOT']['fc:bandit_camp'],[
            ['fc:gold_coin',4,12,1],['fc:steel_longsword',1,1,0.4],['fc:health_potion',1,2,0.6],
            ['fc:golden_carrot_brew',1,3,0.5],['fc:sharpening_augment',1,1,0.15],
            ['fc:silver_key',1,1,0.2],['fc:orb_strength',1,2,0.4]])

    def test_two_checkpoints_and_command_tent_faces_south(self):
        for z in (13,31):
            for x in range(14,19): self.assertTrue(self.clear(x,1,z))
            self.assertNotEqual(self.block(13,1,z),'minecraft:air')
            self.assertNotEqual(self.block(19,1,z),'minecraft:air')
        for z in range(3,13):
            for x in (9,23): self.assertEqual(self.block(x,1,z),'minecraft:spruce_log')
        for x in range(14,19): self.assertTrue(self.clear(x,1,11))
        self.assertEqual(self.block(16,1,4),'minecraft:brown_wool')
        self.assertEqual(self.block(16,7,8),'minecraft:brown_wool')

    def test_fighting_floor_and_external_fires(self):
        import math
        for x in range(11,22):
            for z in range(15,26):
                d=math.hypot(x-16,z-20)
                if d<=4.5:
                    self.assertTrue(self.clear(x,1,z),f'Obstructed fighting floor {x,z}')
                    self.assertEqual(self.block(x,0,z),'minecraft:cobblestone' if d>=3.6 else 'minecraft:coarse_dirt')
        for x in (10,22): self.assertEqual(self.block(x,1,18),'minecraft:campfire')

    def test_three_stalls_four_openable_chests_and_ladders(self):
        for x,z in ((5,13),(5,19),(8,25)):
            self.assertEqual(self.block(x+2,4,z+1),'minecraft:brown_wool')
            self.assertTrue(self.clear(x+2,1,z))
            self.assertEqual(self.block(x,1,z),'minecraft:spruce_fence')
        chests=[(x,y,z) for x in range(33) for y in range(13) for z in range(33) if self.block(x,y,z)=='minecraft:chest']
        self.assertEqual(set(chests),{(14,1,9),(7,1,14),(26,1,16),(26,1,23)})
        for x,y,z in chests: self.assertEqual(self.block(x,y+1,z),'minecraft:air')
        for x,z in ((6,7),(26,8)):
            for y in range(1,8):
                name,states=self.vox.palette[self.vox.grid[self.vox.idx(x,y,z)]]
                self.assertEqual(name,'minecraft:ladder'); self.assertEqual(states,{'facing_direction':2})
                self.assertEqual(self.block(x,y,z+1),'minecraft:spruce_log')
            self.assertTrue(self.clear(x,8,z+1))

    def test_all_interaction_routes_connected_from_outer_gate(self):
        walkable={(x,z) for x in range(33) for z in range(33) if self.clear(x,1,z) and self.block(x,0,z) not in ('minecraft:air','minecraft:water')}
        reached={(16,32)}; queue=deque(reached)
        while queue:
            x,z=queue.popleft()
            for p in ((x-1,z),(x+1,z),(x,z-1),(x,z+1)):
                if p in walkable and p not in reached: reached.add(p);queue.append(p)
        for p in ((14,10),(18,10),(16,12),(7,13),(7,19),(10,25),(26,15),(26,22),(6,6),(26,7)):
            self.assertTrue(p in reached,f'No gate-to-interaction route: {p}')
        for local in self.entry['mobSpawns']:
            self.assertEqual(local[1],1); self.assertIn((int(local[0]),int(local[2])),reached)

    def test_actual_runtime_population_and_saved_region(self):
        blocks={f'{x},{y},{z}':self.block(x,y,z) for x in range(33) for y in range(13) for z in range(33)}
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'camp.json';path.write_text(json.dumps(blocks))
            result=subprocess.run(['node','scripts/tests/poi_population.cjs',str(path),'bandit_camp'],cwd=ROOT,capture_output=True,text=True)
        self.assertEqual(result.returncode,0,result.stdout+result.stderr);print(result.stdout.strip())


if __name__=='__main__': unittest.main(verbosity=2)

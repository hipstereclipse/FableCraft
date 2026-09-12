"""Shrine access, Bronze Gate, and actual scatter/Cullis behavior regressions."""
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


class ArchonShrine(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        captured, cls.clipped = {}, []
        original = GS.Vox.set
        def bounded(v,x,y,z,*args,**kwargs):
            if not (0<=x<v.sx and 0<=y<v.sy and 0<=z<v.sz): cls.clipped.append((x,y,z))
            return original(v,x,y,z,*args,**kwargs)
        with patch.object(GS.Vox,'save',lambda v,n:captured.setdefault(n,v)), patch.object(GS.Vox,'set',bounded):
            GS.archon_shrine()
        cls.vox = captured['archon_shrine']
        cls.tables = runtime_tables(ROOT)
        cls.entry = next(e for e in cls.tables['STRUCTS'] if e['id']=='fc:archon_shrine')

    def block(self,x,y,z):
        if not (0<=x<49 and 0<=y<24 and 0<=z<57): return None
        return self.vox.palette[self.vox.grid[self.vox.idx(x,y,z)]][0]

    def clear(self,x,y,z):
        return all(self.block(x,h,z)=='minecraft:air' for h in (y,y+1))

    def reached(self):
        support={GS.STONE,GS.CRACK,GS.CHISELED,GS.OBSIDIAN,'minecraft:snow_block',
                 'minecraft:stone_brick_stairs','minecraft:sea_lantern','minecraft:blue_glazed_terracotta'}
        walkable={(x,y,z) for x in range(49) for y in range(1,4) for z in range(57)
                  if self.clear(x,y,z) and self.block(x,y-1,z) in support}
        reached={(24,1,0)};queue=deque(reached)
        while queue:
            x,y,z=queue.popleft()
            for xx,zz in ((x-1,z),(x+1,z),(x,z-1),(x,z+1)):
                for yy in (y-1,y,y+1):
                    p=(xx,yy,zz)
                    if yy!=y and self.block(*( (x,y+2,z) if yy>y else (xx,yy+2,zz) ))!='minecraft:air': continue
                    if p in walkable and p not in reached: reached.add(p);queue.append(p)
        return reached

    def test_dimensions_palette_and_scatter_contract(self):
        self.assertEqual((self.vox.sx,self.vox.sy,self.vox.sz),(49,24,57))
        m=next(e for e in json.loads(MANIFEST.read_text())['structures'] if e['name']=='archon_shrine')
        self.assertEqual(m['size'],[49,24,57]);self.assertEqual(self.clipped,[])
        self.assertLessEqual({self.vox.palette[i][0] for i in self.vox.grid}-{'minecraft:air'},BLOCK_COLORS.keys())
        for k,v in dict(w=49,h=24,d=57,weight=4,surf=['snow','rock'],theme='snow',loot='archon_shrine',door=False,cullis=True,mobs=[],mobSpawns=[]).items():
            self.assertEqual(self.entry[k],v)

    def test_dome_and_three_distinct_floor_sockets(self):
        self.assertNotEqual(self.block(24,19,14),'minecraft:air')
        self.assertNotEqual(self.block(34,9,14),'minecraft:air')
        self.assertTrue(self.clear(24,7,14))
        for x in (20,24,28):
            self.assertEqual(self.block(x,2,14),'minecraft:blue_glazed_terracotta')
            for xx,zz in ((x-1,14),(x+1,14),(x,13),(x,15)): self.assertEqual(self.block(xx,2,zz),GS.OBSIDIAN)
            self.assertTrue(self.clear(x,3,14))
        for z,y in ((3,1),(4,2)):
            for x in range(22,27):
                self.assertEqual(self.vox.palette[self.vox.grid[self.vox.idx(x,y,z)]],
                                 ('minecraft:stone_brick_stairs',{'weirdo_direction':2,'upside_down_bit':False}))
                self.assertTrue(self.clear(x,y+1,z))

    def test_routes_to_sockets_chests_disc_and_gate(self):
        reached=self.reached()
        for p in [(24,3,6),(20,3,14),(24,3,14),(28,3,14),(18,3,16),(30,3,16),
                  (8,1,29),(40,1,29),(24,1,28),(24,1,43)]:
            self.assertIn(p,reached,f'Blocked north-entry route: {p}')

    def test_sealed_monumental_gate_and_exact_chests(self):
        for x in range(17,32):
            for y in range(1,18): self.assertEqual(self.block(x,y,47),'minecraft:waxed_cut_copper')
        self.assertEqual(self.block(24,22,48),GS.CHISELED)
        self.assertEqual(self.block(24,8,46),GS.DEEP_TILES)
        self.assertEqual(self.block(24,11,45),GS.DEEP_TILES)
        self.assertEqual(self.block(24,20,45),'minecraft:waxed_weathered_cut_copper')
        chests={(x,y,z) for x in range(49) for y in range(24) for z in range(57) if self.block(x,y,z)=='minecraft:chest'}
        self.assertEqual(chests,{(18,3,17),(30,3,17)})
        for x,y,z in chests: self.assertEqual(self.block(x,y+1,z),'minecraft:air')
        self.assertEqual({r[0] for r in self.tables['CHEST_LOOT']['fc:archon_shrine']},{'fc:will_potion','fc:gold_coin'})

    def run_fixture(self,script,blocks,*args):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'fixture.json';path.write_text(json.dumps(blocks))
            result=subprocess.run(['node',script,str(path),*args],cwd=ROOT,capture_output=True,text=True)
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)
        print(result.stdout.strip())

    def test_real_cullis_detector_and_negative_fixtures(self):
        # Translate the existing detector fixture's expected center (6,1,6).
        blocks={f'{x-18},{y},{z-22}':self.block(x,y,z) for x in range(18,31) for y in range(4) for z in range(22,35)}
        self.run_fixture('scripts/tests/cullis_configuration.cjs',blocks)

    def test_actual_scatter_loot_travel_and_saved_region(self):
        blocks={f'{x},{y},{z}':self.block(x,y,z) for x in range(49) for y in range(24) for z in range(57)}
        self.run_fixture('scripts/tests/poi_population.cjs',blocks,'archon_shrine')

    def test_closed_shrine_and_obstructed_arrival_negative_fixtures(self):
        original=self.vox.grid.copy()
        try:
            self.vox.fill(22,3,3,26,6,5,GS.STONE)
            with self.assertRaises(AssertionError): self.test_routes_to_sockets_chests_disc_and_gate()
            self.vox.grid[:]=original
            self.vox.set(24,1,28,GS.STONE)
            with self.assertRaises(AssertionError): self.test_actual_scatter_loot_travel_and_saved_region()
        finally: self.vox.grid[:]=original


if __name__=='__main__': unittest.main(verbosity=2)

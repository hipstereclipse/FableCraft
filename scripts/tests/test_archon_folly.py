"""Volcanic arena routes, lava containment and real dragon collision clearance."""
import json
import math
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


class ArchonFolly(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        captured,cls.clipped={},[]
        original=GS.Vox.set
        def bounded(v,x,y,z,*args,**kwargs):
            if not (0<=x<v.sx and 0<=y<v.sy and 0<=z<v.sz): cls.clipped.append((x,y,z))
            return original(v,x,y,z,*args,**kwargs)
        with patch.object(GS.Vox,'save',lambda v,n:captured.setdefault(n,v)),patch.object(GS.Vox,'set',bounded): GS.archon_folly()
        cls.vox=captured['archon_folly'];cls.tables=runtime_tables(ROOT)
        cls.entry=next(e for e in cls.tables['STRUCTS'] if e['id']=='fc:archon_folly')

    def block(self,x,y,z):
        if not (0<=x<49 and 0<=y<18 and 0<=z<55): return None
        return self.vox.palette[self.vox.grid[self.vox.idx(x,y,z)]][0]

    def clear(self,x,y,z): return all(self.block(x,h,z)=='minecraft:air' for h in (y,y+1))

    def test_dimensions_palette_flags_and_no_structure_loot(self):
        self.assertEqual((self.vox.sx,self.vox.sy,self.vox.sz),(49,18,55));self.assertEqual(self.clipped,[])
        m=next(e for e in json.loads(MANIFEST.read_text())['structures'] if e['name']=='archon_folly')
        self.assertEqual(m['size'],[49,18,55])
        for k,v in dict(w=49,h=18,d=55,weight=2,surf=['rock'],theme='dark',loot='archon_folly',door=False,cullis=False,mobs=['fc:jack_dragon'],mobSpawns=[[24.5,3,30.5]]).items(): self.assertEqual(self.entry[k],v)
        names={self.vox.palette[i][0] for i in self.vox.grid}
        self.assertLessEqual(names-{'minecraft:air'},BLOCK_COLORS.keys())
        self.assertNotIn('minecraft:chest',names);self.assertEqual(self.tables['CHEST_LOOT']['fc:archon_folly'],[])

    def test_lava_has_solid_floor_and_retaining_neighbors(self):
        lava={(x,1,z) for x in range(49) for z in range(55) if self.block(x,1,z)=='minecraft:lava'}
        self.assertGreater(len(lava),300)
        solid={'minecraft:polished_blackstone','minecraft:polished_blackstone_bricks','minecraft:basalt'}
        for x,y,z in lava:
            self.assertIn(self.block(x,0,z),solid,f'Open lava floor {(x,z)}')
            for xx,zz in ((x-1,z),(x+1,z),(x,z-1),(x,z+1)):
                self.assertIn(self.block(xx,y,zz),solid|{'minecraft:lava'},f'Open lava bank {(xx,y,zz)}')
        for x,z in ((5,14),(43,16),(7,44),(41,46)):
            self.assertEqual(self.block(x,10,z),'minecraft:basalt')

    def test_open_dry_entrance_and_return_route(self):
        # The continuous central route is deliberately stricter than floodfill:
        # each whole-width landing and step must stay dry with two-block headroom.
        for z in range(0,43):
            y=1 if z==0 else (2 if z==1 else 3)
            for x in range(22,27):
                self.assertTrue(self.clear(x,y,z),f'Blocked route {(x,y,z)}')
                self.assertIn(self.block(x,y-1,z),{'minecraft:polished_blackstone','minecraft:polished_blackstone_bricks','minecraft:stone_brick_stairs'})
        for z,y in ((1,1),(2,2)):
            self.assertEqual(self.vox.palette[self.vox.grid[self.vox.idx(24,y,z)]],
                             ('minecraft:stone_brick_stairs',{'weirdo_direction':2,'upside_down_bit':False}))

    def test_actual_dragon_collision_volume_and_dry_landing(self):
        components=json.loads((ROOT/'packs/Fablecraft_BP/entities/jack_dragon.json').read_text())['minecraft:entity']['components']
        box=components['minecraft:collision_box'];x,y,z=self.entry['mobSpawns'][0];half=box['width']/2
        for xx in range(math.floor(x-half),math.ceil(x+half)):
            for zz in range(math.floor(z-half),math.ceil(z+half)):
                self.assertIn(self.block(xx,2,zz),{'minecraft:polished_blackstone','minecraft:polished_blackstone_bricks'})
                for yy in range(math.floor(y),math.ceil(y+box['height'])):
                    self.assertEqual(self.block(xx,yy,zz),'minecraft:air',f'Dragon clips {(xx,yy,zz)}')
        # A generous landing square around the anchor, independent of its narrow collider.
        for xx in range(19,31):
            for zz in range(25,37): self.assertTrue(self.clear(xx,3,zz))

    def test_actual_scatter_dragon_and_saved_region(self):
        blocks={f'{x},{y},{z}':self.block(x,y,z) for x in range(49) for y in range(18) for z in range(55)}
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'folly.json';path.write_text(json.dumps(blocks))
            result=subprocess.run(['node','scripts/tests/poi_population.cjs',str(path),'archon_folly'],cwd=ROOT,text=True,capture_output=True)
        self.assertEqual(result.returncode,0,result.stdout+result.stderr);print(result.stdout.strip())

    def test_open_bank_blocked_exit_and_high_collision_negative_fixtures(self):
        original=self.vox.grid.copy()
        try:
            self.vox.set(24,0,47,'minecraft:air')
            with self.assertRaises(AssertionError): self.test_lava_has_solid_floor_and_retaining_neighbors()
            self.vox.grid[:]=original
            self.vox.set(24,1,49,'minecraft:air')
            with self.assertRaises(AssertionError): self.test_lava_has_solid_floor_and_retaining_neighbors()
            self.vox.grid[:]=original
            self.vox.fill(21,3,9,27,5,9,GS.STONE)
            with self.assertRaises(AssertionError): self.test_open_dry_entrance_and_return_route()
            self.vox.grid[:]=original
            self.vox.set(24,6,30,GS.STONE)
            with self.assertRaises(AssertionError): self.test_actual_dragon_collision_volume_and_dry_landing()
        finally: self.vox.grid[:]=original


if __name__=='__main__': unittest.main(verbosity=2)

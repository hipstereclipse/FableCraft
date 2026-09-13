"""Gorge bridge, descent, checkpoint routes and actual scatter regressions."""
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
from door_realms import GORGE_ARBORETUM_SOURCE
from test_guild_map_table import voxel_changes


class GreatwoodGorge(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        captured, cls.clipped = {}, []
        original = GS.Vox.set
        def bounded(v,x,y,z,*args,**kwargs):
            if not (0<=x<v.sx and 0<=y<v.sy and 0<=z<v.sz): cls.clipped.append((x,y,z))
            return original(v,x,y,z,*args,**kwargs)
        with patch.object(GS.Vox,'save',lambda v,n:captured.setdefault(n,v)), patch.object(GS.Vox,'set',bounded):
            GS.greatwood_gorge()
        cls.vox = captured['greatwood_gorge']
        cls.tables = runtime_tables(ROOT)
        cls.entry = next(e for e in cls.tables['STRUCTS'] if e['id']=='fc:greatwood_gorge')

    def block(self,x,y,z):
        if not (0<=x<39 and 0<=y<16 and 0<=z<43): return None
        return self.vox.palette[self.vox.grid[self.vox.idx(x,y,z)]][0]

    def clear(self,x,y,z):
        return all(self.block(x,h,z)=='minecraft:air' for h in (y,y+1))

    def reached(self):
        support={GS.STONE,GS.COBBLE,GS.GRAVEL,GS.SPRUCE,'minecraft:grass_block','minecraft:stone_brick_stairs'}
        walkable={(x,y,z) for x in range(39) for y in range(1,7) for z in range(43)
                  if self.clear(x,y,z) and self.block(x,y-1,z) in support}
        reached={(8,1,0)};queue=deque(reached)
        while queue:
            x,y,z=queue.popleft()
            for xx,zz in ((x-1,z),(x+1,z),(x,z-1),(x,z+1)):
                for yy in (y-1,y,y+1):
                    p=(xx,yy,zz)
                    if yy!=y and self.block(*( (x,y+2,z) if yy>y else (xx,yy+2,zz) ))!='minecraft:air': continue
                    if p in walkable and p not in reached: reached.add(p);queue.append(p)
        return reached

    def test_dimensions_palette_and_runtime_contract(self):
        self.assertEqual((self.vox.sx,self.vox.sy,self.vox.sz),(39,16,43));self.assertEqual(self.clipped,[])
        m=next(e for e in json.loads(MANIFEST.read_text())['structures'] if e['name']=='greatwood_gorge')
        self.assertEqual(m['size'],[39,16,43])
        self.assertLessEqual({self.vox.palette[i][0] for i in self.vox.grid}-{'minecraft:air'},BLOCK_COLORS.keys())
        for k,v in dict(w=39,h=16,d=43,weight=6,surf=['grass','rock'],theme='forest',loot='greatwood_gorge',door=False,cullis=False).items(): self.assertEqual(self.entry[k],v)

    def test_continuous_bridge_deck_and_guardrails(self):
        for x in range(12,27):
            for z in range(17,22):
                self.assertEqual(self.block(x,5,z),GS.SPRUCE)
                self.assertTrue(self.clear(x,6,z))
            for z in (16,22): self.assertIn(self.block(x,6,z),{GS.SPRUCE_FENCE,GS.SPRUCE_LOG})
        for z in range(17,22):
            self.assertTrue(self.clear(19,1,z))
            self.assertTrue(self.clear(19,3,z))

    def test_routes_to_checkpoint_chest_face_and_lower_ravine(self):
        reached=self.reached()
        targets=[(8,6,7),(19,6,19),(29,6,19),(31,6,26),(31,6,31),(32,6,6),
                 (26,6,25),(25,2,30),(23,1,31),(23,1,19)]
        targets += [tuple(map(int,p)) for p in self.entry['mobSpawns']]
        for p in targets: self.assertIn(p,reached,f'Blocked north-entry route: {p}')

    def test_stairs_face_and_exact_chest(self):
        for xs,zs,height,direction in [(range(6,11),range(1,6),lambda z:z,2),
                                      (range(24,27),range(26,31),lambda z:31-z,3)]:
            for x in xs:
                for z in zs:
                    y=height(z)
                    self.assertEqual(self.vox.palette[self.vox.grid[self.vox.idx(x,y,z)]],
                        ('minecraft:stone_brick_stairs',{'weirdo_direction':direction,'upside_down_bit':False}))
                    self.assertTrue(self.clear(x,y+1,z))
        for x in (30,34):self.assertEqual(self.block(x,11,7),GS.DEEP_TILES)
        self.assertEqual(self.block(32,10,7),GS.CHISELED)
        chests={(x,y,z) for x in range(39) for y in range(16) for z in range(43) if self.block(x,y,z)=='minecraft:chest'}
        self.assertEqual(chests,{(31,6,32)});self.assertEqual(self.block(31,7,32),'minecraft:air')
        self.assertEqual({r[0] for r in self.tables['CHEST_LOOT']['fc:greatwood_gorge']},{'fc:gold_coin','fc:health_potion','fc:red_meat'})

    def test_actual_scatter_bandits_loot_and_saved_region(self):
        self.assertEqual(self.entry['mobs'],['fc:bandit','fc:bandit','fc:bandit_archer'])
        blocks={f'{x},{y},{z}':self.block(x,y,z) for x in range(39) for y in range(16) for z in range(43)}
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'gorge.json';path.write_text(json.dumps(blocks))
            result=subprocess.run(['node','scripts/tests/poi_population.cjs',str(path),'greatwood_gorge'],cwd=ROOT,text=True,capture_output=True)
        self.assertEqual(result.returncode,0,result.stdout+result.stderr);print(result.stdout.strip())

    def test_new_canonical_source_full_throat_and_both_approaches(self):
        self.assertEqual(GORGE_ARBORETUM_SOURCE['center'],(32.5,6,7.5))
        self.assertEqual(GORGE_ARBORETUM_SOURCE['normal'],(0,0,-1))
        reached=self.reached()
        for x in range(31,34):
            for z in range(6,13):
                self.assertEqual(self.block(x,5,z),'minecraft:grass_block',f'Lost source support {(x,z)}')
                for y in range(6,10):
                    self.assertEqual(self.block(x,y,z),'minecraft:air',f'Blocked source approach {(x,y,z)}')
                self.assertIn((x,6,z),reached)
        self.assertEqual(self.block(32,10,7),GS.CHISELED,'Lost lintel')

    def test_source_only_changes_43_existing_cells_without_shared_rng_drift(self):
        captures={}; streams=[]; old_rng=GS.rng
        def tracked_rng(*keys):
            stream=old_rng(*keys); streams.append((keys,stream)); return stream
        with patch.object(GS,'rng',tracked_rng):
            with patch.object(GS.Vox,'save',lambda v,n:captures.setdefault('before',v)), patch.object(GS,'open_gorge_arboretum_throat',lambda *_:None):
                GS.greatwood_gorge()
            with patch.object(GS.Vox,'save',lambda v,n:captures.setdefault('after',v)):
                GS.greatwood_gorge()
        before,after=captures['before'],captures['after']
        changed=set(voxel_changes(before,after))
        expected={(x,y,z) for x in range(31,34) for y in range(6,10) for z in range(8,11)}
        expected|={(x,y,7) for x in range(31,34) for y in (7,8)}|{(32,9,7)}
        self.assertEqual(changed,expected);self.assertEqual(len(changed),43)
        self.assertTrue(all(after.palette[after.grid[after.idx(*p)]][0]=='minecraft:air' for p in changed))
        self.assertEqual([(k,s.getstate()) for k,s in streams[:1]],[(k,s.getstate()) for k,s in streams[1:]])

    def test_source_obstruction_and_missing_support_are_rejected(self):
        original=self.vox.grid.copy()
        try:
            for at,name in (((32,7,9),GS.STONE),((33,5,11),'minecraft:air'),((31,8,6),GS.STONE)):
                self.vox.set(*at,name)
                with self.assertRaises(AssertionError):self.test_new_canonical_source_full_throat_and_both_approaches()
                self.vox.grid[:]=original
        finally:self.vox.grid[:]=original

    def test_broken_bridge_closed_shack_and_blocked_stairs_negative_fixtures(self):
        original=self.vox.grid.copy()
        try:
            self.vox.set(19,5,19,'minecraft:air')
            with self.assertRaises(AssertionError):self.test_continuous_bridge_deck_and_guardrails()
            self.vox.grid[:]=original
            self.vox.fill(30,6,25,32,8,25,GS.SPRUCE)
            with self.assertRaises(AssertionError):self.test_routes_to_checkpoint_chest_face_and_lower_ravine()
            self.vox.grid[:]=original
            self.vox.fill(24,4,29,26,5,29,GS.STONE)
            with self.assertRaises(AssertionError):self.test_stairs_face_and_exact_chest()
        finally:self.vox.grid[:]=original


if __name__=='__main__':unittest.main(verbosity=2)

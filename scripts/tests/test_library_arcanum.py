"""Final-voxel reward-grove routes, containment and damaged-room negatives."""
from collections import deque
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from gen_structures import Vox
from door_realms import build_library_arcanum, LIBRARY_ARCANUM
from gen_screenshots import BLOCK_COLORS


class ArcanumGeometry(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.clipped=[]; original=Vox.set
        def bounded(v,x,y,z,*args,**kwargs):
            if not (0<=x<v.sx and 0<=y<v.sy and 0<=z<v.sz):cls.clipped.append((x,y,z))
            return original(v,x,y,z,*args,**kwargs)
        with patch.object(Vox,'save',lambda *_:None), patch.object(Vox,'set',bounded):
            cls.v=build_library_arcanum(Vox)

    def block(self,x,y,z):
        if not (0<=x<49 and 0<=y<28 and 0<=z<49):return None
        return self.v.palette[self.v.grid[self.v.idx(x,y,z)]][0]

    def reached(self,start=(24,7)):
        solid={'minecraft:stone_bricks','minecraft:mossy_stone_bricks','minecraft:grass_block',
               'minecraft:chiseled_stone_bricks','minecraft:podzol','minecraft:coarse_dirt',
               'minecraft:dark_oak_planks','minecraft:calcite'}
        walk={(x,z) for x in range(49) for z in range(49)
              if self.block(x,2,z) in solid and all(self.block(x,y,z)=='minecraft:air' for y in (3,4))}
        seen={start} if start in walk else set();q=deque(seen)
        while q:
            x,z=q.popleft()
            for p in ((x+1,z),(x-1,z),(x,z+1),(x,z-1)):
                if p in walk and p not in seen:seen.add(p);q.append(p)
        return seen

    def test_dimensions_and_no_clipped_writes(self):
        self.assertEqual((self.v.sx,self.v.sy,self.v.sz),(49,28,49));self.assertEqual(self.clipped,[])
        names={n for n,s in self.v.palette}-{'minecraft:air','minecraft:barrier'}
        self.assertLessEqual(names,BLOCK_COLORS.keys())

    def test_connected_discovery_sites_and_return_from_both_sides(self):
        reached=self.reached()
        points=[(24,2),(24,3),(24,4),(24,7),(24,34),(16,27),(32,27),(16,33),
                (18,12),(32,12),(32,34),(20,34),(15,38),(24,38),(33,38)]
        for p in points:self.assertIn(p,reached,f'No dry arrival route to {p}')
        for start in ((24,34),(16,27),(32,27),(16,33)):
            self.assertIn((24,7),self.reached(start),f'No reverse path from {start}')
        for x in range(23,26):
            for z in range(2,10):
                for y in (3,4,5,6):self.assertEqual(self.block(x,y,z),'minecraft:air')

    def test_empty_container_asset_lids_and_adjacent_routes(self):
        chests={(x,y,z) for x in range(49) for y in range(28) for z in range(49)
                if self.block(x,y,z) in ('minecraft:chest','minecraft:barrel')}
        self.assertEqual(chests,set(LIBRARY_ARCANUM['containers']))
        self.assertEqual(self.block(16,3,28),'minecraft:barrel')
        for x,y,z in chests:
            self.assertEqual(self.block(x,y+1,z),'minecraft:air')
            self.assertIn((x,z-1),self.reached())
        # Vox serializes an empty block_position_data map; runtime seeds only
        # the first private build and controls claims. No loot in this owner.
        self.assertFalse(hasattr(self.v,'block_position_data'))

    def test_boundary_and_pond_are_contained(self):
        for x in range(49):
            for z in range(49):
                self.assertEqual(self.block(x,27,z),'minecraft:barrier')
                self.assertEqual(self.block(x,0,z),'minecraft:barrier')
        for y in range(28):
            for k in range(49):
                for x,z in ((0,k),(48,k),(k,0),(k,48)):
                    self.assertEqual(self.block(x,y,z),'minecraft:barrier')
        water={(x,z) for x in range(49) for z in range(49) if self.block(x,2,z)=='minecraft:water'}
        self.assertGreater(len(water),35)
        for x,z in water:
            self.assertEqual(self.block(x,1,z),'minecraft:stone')
            for xx,zz in ((x-1,z),(x+1,z),(x,z-1),(x,z+1)):
                self.assertNotIn(self.block(xx,2,zz),('minecraft:air',None))

    def test_negative_blocked_return_chest_and_broken_containment(self):
        original=self.v.grid.copy()
        try:
            self.v.fill(23,3,3,25,6,3,'minecraft:stone')
            with self.assertRaises(AssertionError):self.test_connected_discovery_sites_and_return_from_both_sides()
            self.v.grid[:]=original
            self.v.set(24,4,35,'minecraft:stone')
            with self.assertRaises(AssertionError):self.test_empty_container_asset_lids_and_adjacent_routes()
            self.v.grid[:]=original
            self.v.set(0,5,24,'minecraft:air')
            with self.assertRaises(AssertionError):self.test_boundary_and_pond_are_contained()
        finally:self.v.grid[:]=original


if __name__=='__main__':unittest.main(verbosity=2)

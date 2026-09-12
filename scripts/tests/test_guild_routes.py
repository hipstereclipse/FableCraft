"""GP2 final-voxel Guild circulation, half-slab transitions and failure fixtures.

The collision model handles full blocks and bottom/top slabs, with two blocks of
headroom and cardinal movement. It is not Bedrock NPC/pathfinding execution.
"""
from collections import deque
import copy
import math
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import gen_structures as GS

PASSABLE = {'minecraft:air','minecraft:red_carpet','minecraft:blue_carpet',
            'minecraft:light_blue_carpet','minecraft:tallgrass','minecraft:fern',
            'minecraft:azure_bluet','minecraft:allium','minecraft:peony',
            'minecraft:rose_bush','minecraft:lilac'}
FLOORS = {'minecraft:stone_bricks','minecraft:mossy_stone_bricks','minecraft:cracked_stone_bricks',
          'minecraft:chiseled_stone_bricks','minecraft:smooth_stone','minecraft:cobblestone',
          'minecraft:mossy_cobblestone','minecraft:spruce_planks','minecraft:dark_oak_planks',
          'minecraft:oak_planks','minecraft:red_wool','minecraft:grass_block','minecraft:moss_block',
          'minecraft:coarse_dirt','minecraft:dirt_path','minecraft:deepslate_tiles','minecraft:podzol',
          'minecraft:stone_brick_slab','minecraft:spruce_slab','minecraft:dark_oak_slab',
          'minecraft:emerald_block','minecraft:sea_lantern','minecraft:obsidian','minecraft:crying_obsidian'}


def cell(v,x,y,z):
    if not (0<=x<v.sx and 0<=y<v.sy and 0<=z<v.sz):return ('minecraft:air',{})
    return v.palette[v.grid[v.idx(x,y,z)]]


def interval(name, states, y):
    if name in PASSABLE:return None
    if name.endswith('_slab'):
        upper=states.get('minecraft:vertical_half')=='top' or states.get('top_slot_bit',False)
        return (y+.5,y+1) if upper else (y,y+.5)
    # Stairs/fences and furniture are never counted as certified half-step floors.
    # Conservatively treat their occupied column as a cube here.
    return (y,y+1.5) if name.endswith('_fence') or name.endswith('_wall') else (y,y+1)


def clear(v,x,feet,z,height=2.):
    for y in range(max(0,math.floor(feet)-1),min(v.sy,math.ceil(feet+height))):
        name,states=cell(v,x,y,z); span=interval(name,states,y)
        if span and span[0]<feet+height-1e-6 and span[1]>feet+1e-6:return False
    return True


def supported(v,x,feet,z):
    y=math.ceil(feet)-1;name,states=cell(v,x,y,z)
    span=interval(name,states,y)
    return name in FLOORS and span is not None and span[1]==feet


def walking_graph(v):
    nodes=set()
    for x in range(v.sx):
        for z in range(v.sz):
            for y in range(15):
                name,states=cell(v,x,y,z)
                if name not in FLOORS:continue
                feet=interval(name,states,y)[1]
                if clear(v,x,feet,z):nodes.add((x,feet,z))
    return nodes


def reachable(v,nodes,start,max_rise=.5):
    seen={start} if start in nodes else set();q=deque(seen)
    while q:
        x,y,z=q.popleft()
        for xx,zz in ((x-1,z),(x+1,z),(x,z-1),(x,z+1)):
            for dy in (-.5,0,.5):
                point=(xx,y+dy,zz)
                if point not in nodes or point in seen:continue
                top=max(y,y+dy)
                if clear(v,x,top,z) and clear(v,xx,top,zz):
                    seen.add(point);q.append(point)
    return seen


class GuildRoutes(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        captured={}
        with patch.object(GS.Vox,'save',lambda v,n:captured.setdefault(n,v)):GS.guild_hall()
        cls.vox=captured['guild_hall'];cls.nodes=walking_graph(cls.vox)
        cls.from_gate=reachable(cls.vox,cls.nodes,(10,1.,42))

    def check_run(self,points,vox=None):
        """Each authored lane must work forward AND backward without a jump."""
        v=vox or self.vox
        for direction in (points,list(reversed(points))):
            for x,y,z in direction:
                self.assertTrue(supported(v,x,y,z),f'No surface {(x,y,z)}')
                self.assertTrue(clear(v,x,y,z),f'Blocked standing volume {(x,y,z)}')
            for a,b in zip(direction,direction[1:]):
                self.assertEqual(abs(a[0]-b[0])+abs(a[2]-b[2]),1,f'Nonadjacent {a} -> {b}')
                self.assertLessEqual(abs(a[1]-b[1]),.5,f'Jump {a} -> {b}')
                top=max(a[1],b[1])
                for x,_,z in (a,b):self.assertTrue(clear(v,x,top,z),f'Blocked transition {a} -> {b}')

    def test_gate_connects_gallery_dining_and_maze_in_both_directions(self):
        for destination in ((31,10.,42),(39,8.,42),(46,12.,70),(46,1.,70)):
            with self.subTest(destination=destination):
                self.assertTrue(destination in self.from_gate,f'Unreachable {destination}')
                self.assertTrue((10,1.,42) in reachable(self.vox,self.nodes,destination),f'No return from {destination}')

    def test_two_lobby_flights_have_contiguous_half_steps_and_turns(self):
        # Independent surveyed centreline, including flat turn landings.
        north=[(20,1.,41)]+[(20,1.5+i*.5,z) for i,z in enumerate(range(40,36,-1))]
        north += [(20,3.,36),(21,3.,36)]
        north += [(x,3.5+i*.5,36) for i,x in enumerate(range(22,31))]
        north += [(31,7.5,36),(31,7.5,37)]
        north += [(31,8.+i*.5,z) for i,z in enumerate(range(38,43))]
        self.check_run(north);self.check_run([(x,y,84-z) for x,y,z in north])
        # The second lane is real flooring, not fences masquerading as treads.
        for z in (35,36):
            for i,x in enumerate(range(22,31)):
                self.assertTrue(supported(self.vox,x,3.5+i*.5,z))
                self.assertTrue(clear(self.vox,x,3.5+i*.5,z))

    def test_gallery_bridge_threshold_is_supported_and_clear(self):
        for z in (41,42,43):
            run=[(x,y,z) for x,y in ((33,9.5),(34,9.),(35,8.5),(36,8.),(37,8.),(38,8.),(39,8.))]
            self.check_run(run)
        self.assertEqual(cell(self.vox,36,7,42)[0],'minecraft:spruce_planks')
        self.assertEqual(cell(self.vox,37,8,42)[0],'minecraft:air')
        self.assertEqual(cell(self.vox,38,8,42)[0],'minecraft:air')

    def tower_run(self):
        run=[(49,1.,69)]+[(49,1.5+i*.5,z) for i,z in enumerate(range(70,75))]
        run += [(49,3.5,75)]
        run += [(x,4.+i*.5,75) for i,x in enumerate(range(48,43,-1))]
        run += [(43,6.,75)]
        run += [(43,6.5+i*.5,z) for i,z in enumerate(range(74,69,-1))]
        run += [(43,8.5,69)]
        run += [(x,9.+i*.5,69) for i,x in enumerate(range(44,49))]
        run += [(49,11.,69),(49,11.5,70),(49,12.,71)]
        run += [(48,12.,71),(47,12.,71),(46,12.,71),(46,12.,70)]
        return run

    def test_tower_every_turn_and_floor_landing_is_walkable(self):
        self.check_run(self.tower_run())
        # Positive landing into the middle floor at the west flight's y7 surface.
        self.check_run([(42,7.,73),(43,7.,73),(44,7.,73),(44,7.,72)])
        for x in (49,50):
            for i,z in enumerate(range(70,75)):
                self.assertTrue(supported(self.vox,x,1.5+i*.5,z))
                self.assertTrue(clear(self.vox,x,1.5+i*.5,z))

    def test_ground_arches_and_existing_interaction_approaches_remain_open(self):
        for x,y,z in ((20,1.,42),(27,1.,24),(27,1.,55),(39,1.,42),
                      (16,1.,35),(16,1.,49),(22,1.,69),(46,1.,70),
                      (86,1.,39),(101,1.,61),(66,1.,88)):
            self.assertTrue((x,y,z) in self.from_gate,f'Lost adjacent route {(x,y,z)}')
        for z in (34,35,36,48,49,50):
            for x in (25,26,27):self.assertTrue(clear(self.vox,x,1.,z),f'Blocked ground arch {(x,z)}')
        self.assertEqual(GS.GUILD_LAYOUT['maze_spawn'],(46,70))
        self.assertEqual(GS.GUILD_LAYOUT['maze_study_y'],12)
        self.assertEqual(GS.GUILD_LAYOUT['size'],(122,30,108))
        for x,z in ((40,72),(46,66)):
            self.assertTrue(clear(self.vox,x,1.,z),f'Blocked tower door {(x,z)}')

    def test_independent_missing_tread_blocked_head_and_bridge_fixtures_fail(self):
        broken=copy.deepcopy(self.vox)
        for x in (49,50):broken.fill(x,1,73,x,3,73,'minecraft:air')
        with self.assertRaisesRegex(AssertionError,'No surface'):
            self.check_run(self.tower_run(),broken)
        blocked=copy.deepcopy(self.vox)
        blocked.set(49,5,74,'minecraft:stone_bricks')
        with self.assertRaisesRegex(AssertionError,'Blocked'):
            self.check_run(self.tower_run(),blocked)
        bridge=copy.deepcopy(self.vox)
        bridge.fill(35,7,41,35,9,43,'minecraft:air')
        with self.assertRaisesRegex(AssertionError,'No surface'):
            self.check_run([(34,9.,42),(35,8.5,42),(36,8.,42)],bridge)


if __name__=='__main__':unittest.main(verbosity=2)

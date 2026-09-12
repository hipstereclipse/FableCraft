"""GP13: complete NE dorm ascent via the surviving native stair and restored top.

Extends GP2's slab intervals, two-block headroom and half-step movement to a
half-cell horizontal survey of straight native stairs. It checks geometry, not
Bedrock pathfinding, player auto-jump or native collision execution.
"""
from collections import deque
import copy
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import gen_structures as GS
from test_guild_routes import cell, interval, FLOORS, walking_graph, reachable
from test_guild_map_table import voxel_changes


class DormStairSurvey:
    """Half-cell centres; native stairs split into a base and upper half-block.

    This bounded flight has no same-height perpendicular stair neighbors, so
    no inside/outside corner shape is assumed. A route certifies a centreline
    and standing-height column; entity width/steering remain native acceptance.
    """
    def __init__(self, vox):
        self.vox = vox
        self.nodes = set()
        for qx in range(85 * 2, 92 * 2):
            for qz in range(7 * 2, 14 * 2):
                for y in range(7):
                    name, _ = cell(vox, qx // 2, y, qz // 2)
                    if name not in FLOORS and name != "minecraft:oak_stairs":
                        continue
                    feet = self.span(qx, y, qz)[1]
                    if self.clear(qx, feet, qz):
                        self.nodes.add((qx, feet, qz))

    def span(self, qx, y, qz):
        name, states = cell(self.vox, qx // 2, y, qz // 2)
        if name == "minecraft:oak_stairs":
            assert states.get("upside_down_bit") is False
            # Bedrock weirdo_direction: upper half east/west/south/north.
            d = states["weirdo_direction"]
            assert d in (0, 1, 2, 3)
            high = (qx % 2 == 1, qx % 2 == 0, qz % 2 == 1, qz % 2 == 0)[d]
            return (y, y + 1 if high else y + .5)
        return interval(name, states, y)

    def clear(self, qx, feet, qz):
        for y in range(9):
            span = self.span(qx, y, qz)
            if span and span[0] < feet + 2 and span[1] > feet:
                return False
        return True

    def path(self, start, goal):
        if start not in self.nodes or goal not in self.nodes:
            return []
        previous = {start: None}
        todo = deque([start])
        while todo:
            point = todo.popleft()
            if point == goal:
                result = []
                while point is not None:
                    result.append(point)
                    point = previous[point]
                return list(reversed(result))
            x, y, z = point
            for xx, zz in ((x-1, z), (x+1, z), (x, z-1), (x, z+1)):
                for dy in (-.5, 0, .5):
                    target = (xx, y+dy, zz)
                    top = max(y, y+dy)
                    if (target in self.nodes and target not in previous
                            and self.clear(x, top, z) and self.clear(xx, top, zz)):
                        previous[target] = point
                        todo.append(target)
        return []

    @staticmethod
    def coordinates(path):
        return [(qx / 2 + .25, y, qz / 2 + .25) for qx, y, qz in path]


LOWER = (180, 1., 18)  # (90.25,1,9.25), common-room floor beside the first tread
UPPER = (180, 6., 24)  # (90.25,6,12.25), existing upper bedroom deck


class GuildDormRoutes(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        streams = []
        original_rng = GS.rng
        def observed_rng(*keys):
            stream = original_rng(*keys)
            streams.append(stream)
            return stream
        with patch.object(GS, "rng", observed_rng):
            cls.vox = GS.build_guild_hall()
            with patch.object(GS, "restore_guild_dorm_stair_top", lambda *args: None):
                cls.before = GS.build_guild_hall()
        cls.rng_states = [stream.getstate() for stream in streams]
        cls.survey = DormStairSurvey(cls.vox)

    def test_restores_only_the_erased_authored_outer_top_tread(self):
        self.assertEqual(voxel_changes(self.before, self.vox), [(86, 5, 11)])
        self.assertEqual(cell(self.before, 86, 5, 11), ("minecraft:air", {}))
        self.assertEqual(cell(self.vox, 86, 5, 11),
                         ("minecraft:oak_stairs", {"weirdo_direction": 1, "upside_down_bit": False}))
        self.assertEqual(cell(self.vox, 86, 4, 11)[0], "minecraft:stone_bricks")
        self.assertEqual(cell(self.vox, 86, 6, 11)[0], "minecraft:air", "Floating rug over landing")
        self.assertEqual(self.rng_states[0], self.rng_states[1])

    def test_straight_native_treads_use_half_height_geometry_without_corner_neighbors(self):
        stairs = []
        for x in range(85, 90):
            for y in range(1, 6):
                for z in range(7, 12):
                    name, states = cell(self.vox, x, y, z)
                    if name != "minecraft:oak_stairs":
                        continue
                    stairs.append((x, y, z))
                    for xx, zz in ((x-1, z), (x+1, z), (x, z-1), (x, z+1)):
                        neighbor, other = cell(self.vox, xx, y, zz)
                        if neighbor.endswith("_stairs"):
                            self.assertEqual(states["weirdo_direction"], other["weirdo_direction"],
                                             "Perpendicular neighbor needs a native corner audit")
                    heights = {self.survey.span(x*2+dx, y, z*2+dz)[1]
                               for dx in (0, 1) for dz in (0, 1)}
                    self.assertEqual(heights, {y+.5, y+1})
        self.assertEqual(len(stairs), 7)
        self.assertEqual(self.survey.span(173, 5, 22), (5, 5.5))  # east/low half
        self.assertEqual(self.survey.span(172, 5, 22), (5, 6))    # west/high half

    def test_complete_ascent_and_descent_have_contiguous_supported_half_steps(self):
        for start, goal in ((LOWER, UPPER), (UPPER, LOWER)):
            path = self.survey.path(start, goal)
            self.assertTrue(path, f"No stair route {start} -> {goal}")
            self.assertIn(5.5, {p[1] for p in path})
            for a, b in zip(path, path[1:]):
                self.assertEqual(abs(a[0]-b[0]) + abs(a[2]-b[2]), 1)
                self.assertLessEqual(abs(a[1]-b[1]), .5)
                self.assertTrue(self.survey.clear(a[0], max(a[1], b[1]), a[2]))
                self.assertTrue(self.survey.clear(b[0], max(a[1], b[1]), b[2]))
        old = DormStairSurvey(self.before)
        self.assertFalse(old.path(LOWER, UPPER), "Historical missing top wrongly accepted")

    def test_campus_gate_to_bedroom_route_composes_with_both_stair_directions(self):
        nodes = walking_graph(self.vox)
        ground = reachable(self.vox, nodes, (10, 1., 42))
        self.assertIn((90, 1., 9), ground)
        self.assertTrue(self.survey.path(LOWER, UPPER))
        upper = reachable(self.vox, nodes, (90, 6., 12))
        for point in ((91, 6., 20), (94, 6., 9), (94, 6., 20)):
            self.assertIn(point, upper, f"Lost bedroom approach {point}")
            self.assertIn((90, 6., 12), reachable(self.vox, nodes, point))
        self.assertTrue(self.survey.path(UPPER, LOWER))
        self.assertIn((10, 1., 42), reachable(self.vox, nodes, (90, 1., 9)))

    def test_unchanged_bunks_roof_post_and_mazes_fixed_study_remain_protected(self):
        for x in range(84, 99):
            for z in range(6, 29):
                for y in (0, 6, 7, 8, 9, 10, 11, 12, 13):
                    self.assertEqual(cell(self.vox, x, y, z), cell(self.before, x, y, z))
        for y in range(1, 7):
            self.assertEqual(cell(self.vox, 87, y, 9), cell(self.before, 87, y, 9))
        self.assertEqual(GS.GUILD_LAYOUT["maze_spawn"], (46, 70))
        self.assertEqual(GS.GUILD_LAYOUT["maze_study_y"], 12)

    def test_independent_removed_tread_and_blocked_headroom_fail_the_complete_route(self):
        missing = copy.deepcopy(self.vox)
        missing.set(86, 5, 11, "minecraft:air")
        self.assertFalse(DormStairSurvey(missing).path(LOWER, UPPER))
        blocked = copy.deepcopy(self.vox)
        blocked.set(86, 6, 11, "minecraft:stone_bricks")
        self.assertFalse(DormStairSurvey(blocked).path(LOWER, UPPER))
        facing = copy.deepcopy(self.vox)
        facing.set(86, 5, 11, "minecraft:oak_stairs", {"weirdo_direction": 0, "upside_down_bit": False})
        self.assertFalse(DormStairSurvey(facing).path(LOWER, UPPER))


if __name__ == "__main__":
    unittest.main(verbosity=2)

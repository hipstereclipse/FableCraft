"""GP23 final-voxel bank lamps, supported bridge crossings and body bounds.

Fences are conservatively full horizontal columns through y+1.5; lanterns are
full cubes. The step sweep raises to the higher tread before moving laterally.
This checks the authored corridor, not native collision shapes or pathfinding.
"""
import copy
import math
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import gen_structures as GS
from test_guild_routes import cell, clear, supported, interval


BRIDGES = {z: [(x, 1.5 if x in (59, 67) else 2. if 60 <= x <= 66 else 1., z)
               for x in range(57, 70)] for z in (36, 54)}
POSTS = {(x, z) for x in (58, 68) for z in (35, 37, 53, 55)}


def segment_enters_box(a, b, low, high):
    """Strict analytic overlap; touching a support boundary is allowed."""
    entry, leave = 0., 1.
    for axis in range(3):
        delta = b[axis] - a[axis]
        if abs(delta) < 1e-12:
            if a[axis] <= low[axis] or a[axis] >= high[axis]:
                return False
        else:
            first = (low[axis] - a[axis]) / delta
            last = (high[axis] - a[axis]) / delta
            entry, leave = max(entry, min(first, last)), min(leave, max(first, last))
    return entry < leave and leave > 0 and entry < 1


def body_hits(vox, path, radius=.35, height=1.9):
    """Inspect every final block near each swept segment, including lower fences."""
    hits = set()
    for first, last in zip(path, path[1:]):
        feet = max(first[1], last[1])
        start, end = (first[0] + .5, first[1], first[2] + .5), (last[0] + .5, last[1], last[2] + .5)
        raised_start, raised_end = (start[0], feet, start[2]), (end[0], feet, end[2])
        for a, b in ((start, raised_start), (raised_start, raised_end), (raised_end, end)):
            for x in range(math.floor(min(a[0], b[0]) - radius), math.ceil(max(a[0], b[0]) + radius)):
                for z in range(math.floor(min(a[2], b[2]) - radius), math.ceil(max(a[2], b[2]) + radius)):
                    for y in range(max(0, math.floor(min(a[1], b[1])) - 1), math.ceil(max(a[1], b[1]) + height)):
                        span = interval(*cell(vox, x, y, z), y)
                        if span and segment_enters_box(a, b, (x - radius, span[0] - height, z - radius),
                                                       (x + 1 + radius, span[1], z + 1 + radius)):
                            hits.add((x, y, z))
    return hits


class GuildBridgeLamps(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.vox = GS.build_guild_hall()

    def check_lamps(self, vox):
        for x, z in POSTS:
            self.assertTrue(supported(vox, x, 1., z), f"Unsupported lamp base {(x, z)}")
            for y in (1, 2):
                self.assertEqual(cell(vox, x, y, z), ("minecraft:dark_oak_fence", {}),
                                 f"Broken tall lamp post {(x, y, z)}")
            self.assertEqual(cell(vox, x, 3, z), ("minecraft:lantern", {"hanging": False}))
            self.assertEqual(cell(vox, x, 4, z), ("minecraft:air", {}))

    def check_run(self, vox, path):
        for points in (path, list(reversed(path))):
            for x, feet, z in points:
                self.assertTrue(supported(vox, x, feet, z), f"Missing tread {(x, feet, z)}")
                self.assertTrue(clear(vox, x, feet, z), f"Blocked crossing {(x, feet, z)}")
            for a, b in zip(points, points[1:]):
                self.assertEqual(abs(a[0] - b[0]) + abs(a[2] - b[2]), 1)
                self.assertLessEqual(abs(a[1] - b[1]), .5)
                for x, _, z in (a, b):
                    self.assertTrue(clear(vox, x, max(a[1], b[1]), z))

    def test_all_eight_bank_lamps_have_supported_tall_posts_and_standing_heads(self):
        self.check_lamps(self.vox)
        # The independently surveyed nearby bollard is a separate fixture.
        self.assertEqual(cell(self.vox, 60, 1, 56), ("minecraft:chiseled_stone_bricks", {}))
        self.assertEqual(cell(self.vox, 60, 2, 56), ("minecraft:lantern", {"hanging": False}))

    def test_three_row_decks_and_slab_approaches_retain_outer_rails(self):
        for zc in BRIDGES:
            for z in range(zc - 1, zc + 2):
                for x in range(60, 67):
                    self.assertEqual(cell(self.vox, x, 1, z), ("minecraft:dark_oak_planks", {}))
                for x in (59, 67):
                    self.assertTrue(supported(self.vox, x, 1.5, z))
                    self.assertTrue(clear(self.vox, x, 1.5, z))
            for x in range(60, 67):
                for z in (zc - 1, zc + 1):
                    self.assertEqual(cell(self.vox, x, 2, z), ("minecraft:spruce_fence", {}))

    def test_both_complete_crossings_keep_supported_half_step_transitions(self):
        for path in BRIDGES.values():
            self.check_run(self.vox, path)

    def test_full_final_geometry_keeps_centerline_bodies_clear_both_directions(self):
        for path in BRIDGES.values():
            self.assertFalse(body_hits(self.vox, path))
            self.assertFalse(body_hits(self.vox, list(reversed(path))))

    def test_independent_broken_post_missing_tread_and_headroom_fixtures_fail(self):
        broken = copy.deepcopy(self.vox)
        broken.set(58, 2, 35, "minecraft:air")
        with self.assertRaisesRegex(AssertionError, "Broken tall lamp post"):
            self.check_lamps(broken)
        missing = copy.deepcopy(self.vox)
        missing.set(59, 1, 36, "minecraft:air")
        with self.assertRaisesRegex(AssertionError, "Missing tread"):
            self.check_run(missing, BRIDGES[36])
        overhead = copy.deepcopy(self.vox)
        overhead.set(58, 2, 36, "minecraft:lantern", {"hanging": False})
        self.assertIn((58, 2, 36), body_hits(overhead, BRIDGES[36]))
        # A lower-cell fence reaches half a block into the supported body even
        # though a unit-cube-only sweep would stop at the deck surface.
        lower_fence = copy.deepcopy(self.vox)
        lower_fence.set(63, 1, 36, "minecraft:dark_oak_fence")
        self.assertIn((63, 1, 36), body_hits(lower_fence, BRIDGES[36]))


if __name__ == "__main__":
    unittest.main()

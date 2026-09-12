"""GP11: authored hall arches retain their full opening after all finish passes.

Paired whole-Guild builds isolate the obsolete late connector shells and expose
any accidental shared-RNG drift. No Bedrock light/pathfinding is simulated.
"""
import copy
from pathlib import Path
import random
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import gen_structures as GS
from test_guild_routes import cell, clear, supported, walking_graph, reachable
from test_guild_map_table import voxel_changes


def legacy_link_corridor(v, r, cx, z0, z1):
    """The historical vertical corridor branch used by both actual hall links."""
    lo, hi = sorted((z0, z1))
    for z in range(lo, hi + 1):
        for x in (cx - 1, cx, cx + 1):
            v.set(x, 0, z, GS.STONE)
            v.fill(x, 1, z, x, 3, z, "minecraft:air")
            v.set(x, 4, z, GS.SLATE if (x + z) % 2 else GS.DEEP_TILES)
        for yy in (1, 2, 3):
            v.set(cx - 1, yy, z, GS.guild_brick(r))
            v.set(cx + 1, yy, z, GS.guild_brick(r))
        if (z - lo) % 3 == 1:
            v.set(cx - 1, 2, z, GS.GLASS)
            v.set(cx + 1, 2, z, GS.GLASS)
    if hi - lo >= 3:
        v.set(cx, 3, (lo + hi) // 2, GS.LANTERN, {"hanging": True})


def in_link_scope(x, y, z):
    return 1 <= y <= 4 and ((25 <= x <= 27 and 30 <= z <= 34)
                            or (26 <= x <= 28 and 50 <= z <= 52))


class GuildHallLinks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.vox = GS.build_guild_hall()
        with patch.object(GS, "finish_guild_link_floor", legacy_link_corridor):
            cls.before = GS.build_guild_hall()

    def assert_lanes(self, vox):
        for z0, z1 in ((28, 38), (47, 54)):
            for x in (25, 26, 27):
                for zs in (range(z0, z1 + 1), range(z1, z0 - 1, -1)):
                    for z in zs:
                        self.assertTrue(supported(vox, x, 1., z), f"Unsupported lane {(x, z)}")
                        self.assertTrue(clear(vox, x, 1., z), f"Blocked lane {(x, z)}")

    def assert_arches(self, vox):
        for z, x0, x1 in ((30, 23, 30), (52, 25, 30)):
            for x in range(x0, x1 + 1):
                for y in range(1, 5):
                    self.assertEqual(cell(vox, x, y, z)[0], "minecraft:air",
                                     f"Blocked broad arch {(x, y, z)}")
                self.assertNotEqual(cell(vox, x, 5, z)[0], "minecraft:air", "Lost arch lintel")

    def assert_scope(self, before, after):
        changes = voxel_changes(before, after)
        self.assertTrue(changes)
        for point in changes:
            self.assertTrue(in_link_scope(*point), f"Changed non-link voxel {point}")

    def test_library_and_store_keep_three_contiguous_ground_lanes(self):
        self.assert_lanes(self.vox)
        with self.assertRaisesRegex(AssertionError, "Blocked lane"):
            self.assert_lanes(self.before)

    def test_broad_room_arches_and_overhead_bay_roofs_are_preserved(self):
        self.assert_arches(self.vox)
        with self.assertRaisesRegex(AssertionError, "Blocked broad arch"):
            self.assert_arches(self.before)
        for x, z in ((25, 31), (26, 32), (27, 33), (26, 51), (27, 51), (28, 51)):
            self.assertEqual(cell(self.vox, x, 9, z), cell(self.before, x, 9, z))
            self.assertNotEqual(cell(self.vox, x, 9, z)[0], "minecraft:air", "Missing bay roof")

    def test_library_eye_height_sightlines_are_clear_across_the_join(self):
        # Player feet y1 + nominal eye 1.62: this horizontal ray crosses y2.
        # It is a block obstruction check, not a native camera/render assertion.
        for x in (25, 26, 27):
            for z in range(29, 35):
                self.assertEqual(cell(self.vox, x, 2, z)[0], "minecraft:air")
        for x in (25, 27):
            self.assertNotEqual(cell(self.before, x, 2, 30)[0], "minecraft:air")
            self.assertNotEqual(cell(self.before, x, 2, 33)[0], "minecraft:air")
        self.assertEqual(cell(self.before, 26, 3, 32)[0], "minecraft:lantern")
        self.assertEqual(cell(self.vox, 26, 3, 32)[0], "minecraft:air")

    def test_complete_campus_delta_is_confined_to_the_two_obsolete_shells(self):
        self.assert_scope(self.before, self.vox)
        for x in range(self.vox.sx):
            for z in range(self.vox.sz):
                self.assertEqual(cell(self.vox, x, 0, z), cell(self.before, x, 0, z))

    def test_gate_retains_library_cave_store_gallery_and_living_space_routes(self):
        walked = reachable(self.vox, walking_graph(self.vox), (10, 1., 42))
        for point in ((27, 1., 24), (27, 1., 16), (33, 1., 10), (15, 1., 22),
                      (27, 1., 55), (22, 1., 69), (39, 1., 42), (31, 10., 42),
                      (39, 8., 42), (46, 12., 70), (22, 1., 41)):
            self.assertIn(point, walked, f"Lost adjacent destination {point}")

    def test_both_floor_links_retain_all_48_legacy_masonry_draws(self):
        for seed in (5, 999):
            actual, expected = random.Random(seed), random.Random(seed)
            vox = GS.Vox(40, 10, 60)
            GS.finish_guild_link_floor(vox, actual, 26, 34, 30)
            GS.finish_guild_link_floor(vox, actual, 27, 50, 52)
            for _ in range(48):
                expected.random()
            self.assertEqual(actual.getstate(), expected.getstate())
            non_air = [(i, vox.palette[pid][0]) for i, pid in enumerate(vox.grid)
                       if vox.palette[pid][0] != "minecraft:air"]
            self.assertEqual(len(non_air), 24)
            for i, name in non_air:
                self.assertEqual((i // vox.sz) % vox.sy, 0)
                self.assertEqual(name, "minecraft:stone_bricks")

    def test_blocked_side_lane_missing_floor_and_shared_rng_failure_fixtures(self):
        blocked = copy.deepcopy(self.vox)
        blocked.set(25, 2, 32, "minecraft:stone_bricks")
        with self.assertRaisesRegex(AssertionError, "Blocked lane"):
            self.assert_lanes(blocked)
        unsupported = copy.deepcopy(self.vox)
        unsupported.set(27, 0, 51, "minecraft:air")
        with self.assertRaisesRegex(AssertionError, "Unsupported lane"):
            self.assert_lanes(unsupported)
        low_roof = copy.deepcopy(self.vox)
        low_roof.set(26, 4, 30, "minecraft:deepslate_tiles")
        with self.assertRaisesRegex(AssertionError, "Blocked broad arch"):
            self.assert_arches(low_roof)
        authored = GS.finish_guild_link_floor
        def shifted(v, r, *args):
            authored(v, r, *args)
            r.random()
        with patch.object(GS, "finish_guild_link_floor", shifted):
            shifted_guild = GS.build_guild_hall()
        with self.assertRaisesRegex(AssertionError, "Changed non-link voxel"):
            self.assert_scope(self.vox, shifted_guild)


if __name__ == "__main__":
    unittest.main(verbosity=2)

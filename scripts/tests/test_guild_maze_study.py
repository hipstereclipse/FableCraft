"""GP18: supported study case, retained routes, and an exact eleven-cell fixture.

The GP17 frozen survey records the independently inspected final pre-fixture
geometry. Native rendering, carpet collision and NPC movement remain unrun.
"""
import copy
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import gen_structures as GS
import test_guild_routes as routes
from test_guild_map_table import voxel_changes
from test_guild_routes import cell, clear, reachable, supported, walking_graph

SURVEY = json.loads((ROOT / "screenshots/validation/GP17/maze-study-final-voxel-survey.json").read_text())
CARPET = {(45, 12, 71), (45, 12, 73), (47, 12, 73)}
CASE = {(x, y, 75) for x in (43, 44) for y in range(12, 16)}
FIXTURE = CARPET | CASE
FRONTS = ((43, 12., 74), (44, 12., 74))
UPPER_APPROACH = tuple((x, 12., z) for x in range(50, 53) for z in range(71, 74))
UPPER_APPROACH += tuple((x, 12., z) for x in range(45, 48) for z in range(75, 79))
UPPER_APPROACH += ((49, 12., 67), (50, 12., 67), (50, 12., 68), (51, 12., 68),
                   (51, 12., 69), (52, 12., 69), (52, 12., 70))
DESTINATIONS = ((10, 1., 42), (46, 1., 70), (44, 7., 72), (46, 12., 70))


def capture_rng(builder):
    original = GS.rng
    streams = []

    def tracked(*args):
        stream = original(*args)
        streams.append((args, stream))
        return stream

    with patch.object(GS, "rng", tracked):
        vox = builder()
    return vox, [(args, stream.getstate()) for args, stream in streams]


class GuildMazeStudy(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with patch.object(GS, "build_guild_maze_study", lambda *_: None):
            cls.before, cls.before_rng = capture_rng(GS.build_guild_hall)
        cls.vox, cls.after_rng = capture_rng(GS.build_guild_hall)

    def assert_fixture_scope(self, vox):
        self.assertEqual(set(voxel_changes(self.before, vox)), FIXTURE)
        for p in CASE:
            self.assertEqual(cell(self.before, *p), ("minecraft:air", {}))
        for p in CARPET:
            self.assertEqual(cell(self.before, *p), ("minecraft:blue_carpet", {}))

    def assert_supported_case(self, vox):
        for x in (43, 44):
            self.assertEqual(cell(vox, x, 11, 75), ("minecraft:dark_oak_planks", {}), "Missing case deck")
            for y in (12, 15):
                self.assertEqual(cell(vox, x, y, 75), ("minecraft:dark_oak_planks", {}), "Broken case base/cap")
            for y in (13, 14):
                self.assertEqual(cell(vox, x, y, 75), ("minecraft:bookshelf", {}), "Broken continuous shelves")
        for point in FRONTS:
            self.assertTrue(supported(vox, *point), f"Missing case-front support {point}")
            self.assertTrue(clear(vox, *point), f"Blocked case front {point}")

    def assert_carpet(self, vox):
        for x, y, z in CARPET:
            self.assertEqual(cell(vox, x, y, z), ("minecraft:red_carpet", {}), "Wrong study carpet")
            self.assertEqual(cell(vox, x, y - 1, z), cell(self.before, x, y - 1, z))
            self.assertTrue(clear(vox, x, 12., z))
        # The fourth nominal carpet is a reserved landing, not another rug cell.
        self.assertEqual(cell(vox, 47, 12, 71), ("minecraft:air", {}))

    def assert_protected(self, vox):
        rows = SURVEY["protected_cells"]
        self.assertEqual(len(rows), 678)
        self.assertEqual(len({tuple(row["at"]) for row in rows}), 678)
        for row in rows:
            self.assertEqual(cell(vox, *row["at"]), (row["name"], row["states"]),
                             f"Changed protected cell {row['at']}")
        for row in SURVEY["final_material_fixtures"]["minecraft:glass_pane"]:
            self.assertEqual(cell(vox, *row["at"]), (row["name"], row["states"]), "Changed study window")

    def assert_routes(self, vox):
        check = routes.GuildRoutes()
        check.check_run(check.tower_run(), vox)
        check.check_run([(42, 7., 73), (43, 7., 73), (44, 7., 73), (44, 7., 72)], vox)
        nodes = walking_graph(vox)
        from_maze = reachable(vox, nodes, (46, 12., 70))
        for point in DESTINATIONS + UPPER_APPROACH + FRONTS:
            self.assertIn(point, from_maze, f"Lost study route {point}")
        for path in SURVEY["study_connector_routes"].values():
            check.check_run([tuple(p) for p in path], vox)
        return from_maze

    def test_full_campus_delta_contains_only_eleven_surveyed_fixture_cells(self):
        self.assert_fixture_scope(self.vox)
        self.assertEqual(len(FIXTURE), 11)

    def test_case_is_continuous_supported_and_reachable_at_both_fronts(self):
        self.assert_supported_case(self.vox)

    def test_red_carpet_retains_existing_support_and_landing_air(self):
        self.assert_carpet(self.vox)

    def test_protected_stairs_deck_doors_anchor_windows_and_other_fixtures_remain_exact(self):
        self.assert_protected(self.vox)
        self.assertEqual(GS.GUILD_LAYOUT["maze_spawn"], (46, 70))
        self.assertEqual(GS.GUILD_LAYOUT["maze_study_y"], 12)
        self.assertEqual(GS.GUILD_LAYOUT["size"], (122, 30, 108))
        for p in ((44, 12, 73), (48, 12, 72), (47, 12, 74), (46, 15, 72),
                  (45, 12, 69), (46, 12, 69), (49, 12, 73), (49, 13, 73)):
            self.assertEqual(cell(self.vox, *p), cell(self.before, *p))
        self.assertEqual(cell(self.vox, 46, 15, 72), ("minecraft:lantern", {"hanging": False}))

    def test_existing_two_way_tower_and_all_upper_door_routes_remain_connected(self):
        before = self.assert_routes(self.before)
        after = self.assert_routes(self.vox)
        self.assertEqual(before - after, {(43, 12., 75), (44, 12., 75)},
                         "Fixture disconnected more than its two standing footprints")
        self.assertEqual(after - before, set())

    def test_fixture_uses_no_randomness_and_preserves_all_shared_rng_states(self):
        self.assertEqual(self.before_rng, self.after_rng)
        trial = copy.deepcopy(self.before)
        with patch.object(GS, "rng", side_effect=AssertionError("Unexpected fixture randomness")):
            GS.build_guild_maze_study(trial)
        self.assert_fixture_scope(trial)

    def test_independent_support_frame_headroom_window_route_and_rng_failures_are_detected(self):
        for at, name, check in (
            ((43, 11, 75), "minecraft:air", self.assert_supported_case),
            ((43, 12, 75), "minecraft:air", self.assert_supported_case),
            ((44, 14, 75), "minecraft:air", self.assert_supported_case),
            ((43, 12, 74), "minecraft:stone_bricks", self.assert_supported_case),
            ((45, 12, 71), "minecraft:blue_carpet", self.assert_carpet),
            ((41, 13, 72), "minecraft:air", self.assert_protected),
            ((46, 13, 70), "minecraft:stone_bricks", self.assert_protected),
            ((49, 11, 71), "minecraft:air", self.assert_routes),
            ((52, 12, 72), "minecraft:stone_bricks", self.assert_routes),
            ((45, 12, 69), "minecraft:red_bed", self.assert_fixture_scope),
        ):
            with self.subTest(at=at, check=check.__name__):
                broken = copy.deepcopy(self.vox)
                broken.set(*at, name)
                with self.assertRaises(AssertionError):
                    check(broken)
        original = GS.build_guild_maze_study

        def stray_rng(vox):
            original(vox)
            GS.rng("unexpected", "maze-study").random()

        with patch.object(GS, "build_guild_maze_study", stray_rng):
            _, changed_rng = capture_rng(GS.build_guild_hall)
        self.assertNotEqual(changed_rng, self.before_rng)


if __name__ == "__main__":
    unittest.main(verbosity=2)

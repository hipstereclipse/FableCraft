"""GP15/GP22 final-voxel scenery, access, fixture support and actual Skill ray.

Independent historical fixtures disable only the board or freestanding scenery
helper. Routes use GP2's conservative occupied intervals; native Bedrock walking
remains unrun.
"""
import copy
import json
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import gen_structures as GS
import structure_contract as contract
from test_guild_map_table import voxel_changes
from test_guild_routes import cell, clear, supported, walking_graph, reachable


BOARD = {(x, y, 30) for x in range(80, 89) for y in range(1, 7)}
FRAME = {p for p in BOARD if p[0] in (80, 88) or p[1] in (1, 6)}
APPROACH = ([(79, 1., 30)] + [(x, 1., 29) for x in range(79, 90)]
            + [(89, 1., 30), (89, 1., 31)]
            + [(x, 1., 31) for x in range(88, 79, -1)])
DESTINATIONS = ((78, 1., 28), (90, 1., 28), (83, 1., 39),
                (99, 1., 61), (102, 1., 61), (93, 1., 37), (60, 1., 88))
SCENERY = {(x, y, z) for z, columns in ((32, ((80, 1), (81, 2), (82, 1))),
                                      (33, ((87, 3), (88, 2), (89, 3))))
           for x, height in columns for y in range(1, height + 1)}
SCENERY_COLORS = {"minecraft:purple_terracotta", "minecraft:white_terracotta",
                  "minecraft:light_blue_terracotta", "minecraft:black_wool"}
RESERVED_RUNS = (
    [(x, 1., 31) for x in range(80, 91)],  # the complete rear scenery bypass
    [(78, 1., z) for z in range(27, 31)],  # kitchen south threshold and apron
    [(90, 1., z) for z in range(27, 36)],  # dormitory south threshold and apron
    [(x, 1., 38) for x in range(82, 85)],  # the complete three-column firing gap
)


class GuildArcheryBackboard(unittest.TestCase):
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
            with patch.object(GS, "build_guild_archery_backboard", lambda *_: None):
                cls.before = GS.build_guild_hall()
            with patch.object(GS, "build_guild_archery_scenery", lambda *_: None):
                cls.scenery_before = GS.build_guild_hall()
        cls.rng_states = [stream.getstate() for stream in streams]
        cls.skill_reports = {}

    def check_frame(self, vox):
        for p in FRAME:
            self.assertEqual(cell(vox, *p), ("minecraft:spruce_planks", {}),
                             f"Missing timber frame {p}")
        # The rectangular panel rests on an unbroken full-width bottom frame.
        for x in range(80, 89):
            self.assertTrue(supported(vox, x, 1., 30), f"Unsupported board base {x}")
            for y in range(1, 7):
                self.assertNotEqual(cell(vox, x, y, 30)[0], "minecraft:air")

    def check_approach(self, vox):
        for x, feet, z in APPROACH:
            self.assertTrue(supported(vox, x, feet, z), f"Unsupported approach {(x, feet, z)}")
            self.assertTrue(clear(vox, x, feet, z), f"Blocked approach {(x, feet, z)}")
        for a, b in zip(APPROACH, APPROACH[1:]):
            self.assertEqual(abs(a[0] - b[0]) + abs(a[2] - b[2]), 1)

    def scenery_points(self, vox):
        # Detect the visible props independently of the generator's helper or
        # expected cell list. The painted backboard is behind this survey box.
        return {(x, y, z) for x in range(79, 91) for y in range(1, 5)
                for z in range(31, 35) if cell(vox, x, y, z)[0] in SCENERY_COLORS}

    def check_scenery_support(self, vox):
        points = self.scenery_points(vox)
        self.assertTrue(points, "Missing separate scenery")
        for x, z in {(x, z) for x, _, z in points}:
            ys = {y for xx, y, zz in points if (xx, zz) == (x, z)}
            self.assertEqual(ys, set(range(1, max(ys) + 1)),
                             f"Floating scenery column {(x, z)}")
            self.assertTrue(supported(vox, x, 1., z), f"Unsupported scenery base {(x, z)}")
        # Each connected scenic form must be detached from the other and from
        # the painted backboard; this detects an accidental solid joining wall.
        unseen, components = set(points), []
        while unseen:
            pending, component = [unseen.pop()], set()
            while pending:
                point = pending.pop()
                component.add(point)
                x, y, z = point
                for neighbor in ((x-1, y, z), (x+1, y, z), (x, y-1, z),
                                 (x, y+1, z), (x, y, z-1), (x, y, z+1)):
                    if neighbor in unseen:
                        unseen.remove(neighbor)
                        pending.append(neighbor)
            components.append(component)
        self.assertEqual(len(components), 2, "Scenery is not two separate forms")

    def check_reserved_scenery_routes(self, vox):
        for run in RESERVED_RUNS:
            for x, feet, z in run:
                self.assertTrue(supported(vox, x, feet, z), f"Unsupported reserved route {(x, feet, z)}")
                self.assertTrue(clear(vox, x, feet, z), f"Blocked reserved route {(x, feet, z)}")
            for a, b in zip(run, run[1:]):
                self.assertEqual(abs(a[0]-b[0]) + abs(a[2]-b[2]), 1)

    def actual_skill_report(self, vox):
        if id(vox) not in self.skill_reports:
            cells = {f"{x},{y},{z}": cell(vox, x, y, z)[0]
                     for x in range(77, 94) for y in range(7) for z in range(29, 43)}
            result = subprocess.run(["node", "--experimental-vm-modules", "scripts/tests/guild_archery_voxels.mjs"],
                                    input=json.dumps({"cells": cells}), text=True,
                                    capture_output=True, cwd=ROOT)
            print(result.stdout, end="")
            self.assertEqual(result.returncode, 0, result.stderr)
            self.skill_reports[id(vox)] = json.loads(result.stdout.strip().splitlines()[-1])
        return self.skill_reports[id(vox)]

    def test_exact_final_campus_scope_and_shared_rng(self):
        self.assertEqual(set(voxel_changes(self.before, self.vox)), BOARD)
        self.assertEqual(len(BOARD), 54)
        self.assertEqual(self.rng_states[0], self.rng_states[1])
        for p in BOARD:
            self.assertEqual(cell(self.before, *p), ("minecraft:air", {}))
        self.assertEqual((self.vox.sx, self.vox.sy, self.vox.sz), (122, 30, 108))

    def test_supported_closed_timber_frame_and_non_emissive_landscape(self):
        self.check_frame(self.vox)
        panel = [cell(self.vox, *p)[0] for p in BOARD - FRAME]
        self.assertEqual(set(panel), {"minecraft:light_blue_terracotta",
                         "minecraft:purple_terracotta", "minecraft:white_terracotta",
                         "minecraft:green_terracotta", "minecraft:black_wool"})
        self.assertEqual(len(panel), 28)
        # Sky stays above the valley, with an asymmetric higher ridge at right.
        self.assertGreaterEqual([cell(self.vox, x, 5, 30)[0] for x in range(81, 88)]
                                .count("minecraft:light_blue_terracotta"), 5)
        self.assertIn("minecraft:green_terracotta", [cell(self.vox, x, 2, 30)[0] for x in range(81, 88)])

    def test_existing_targets_dummies_floors_and_runtime_anchors_are_unchanged(self):
        targets = []
        heads = []
        for x in range(self.vox.sx):
            for z in range(self.vox.sz):
                self.assertEqual(cell(self.before, x, 0, z), cell(self.vox, x, 0, z))
                for y in range(1, 4):
                    name = cell(self.vox, x, y, z)[0]
                    if name == "minecraft:target" and 75 <= x <= 98 and 29 <= z <= 45:
                        targets.append((x, y, z))
                    if name == "minecraft:carved_pumpkin" and ((75 <= x <= 98 and 29 <= z <= 45) or (58 <= x <= 63 and 83 <= z <= 86)):
                        heads.append((x, y, z))
        self.assertEqual(targets, [(78, 2, 31), (83, 2, 34), (84, 2, 33), (87, 2, 36)])
        self.assertEqual(len(heads), 7)
        self.assertEqual(contract.anchor_errors(contract.runtime_tables(ROOT)["GUILD"]), [])
        self.assertEqual(GS.GUILD_LAYOUT["maze_spawn"], (46, 70))
        self.assertEqual(GS.GUILD_LAYOUT["maze_study_y"], 12)

    def test_behind_and_side_approaches_and_complete_gate_return_routes(self):
        self.check_approach(self.before)
        self.check_approach(self.vox)
        for vox in (self.before, self.vox):
            nodes = walking_graph(vox)
            found = reachable(vox, nodes, (10, 1., 42))
            for point in DESTINATIONS + tuple(APPROACH):
                self.assertIn(point, found)
            # The same graph is symmetric; independently start inside each room
            # and at the range to certify a return to the entrance.
            for start in ((78, 1., 28), (90, 1., 28), (83, 1., 39)):
                self.assertIn((10, 1., 42), reachable(vox, nodes, start))

    def test_actual_production_skill_station_and_emitted_ray_use_clear_final_voxels(self):
        self.actual_skill_report(self.vox)

    def test_independent_missing_frame_unsupported_base_and_blocked_approach_fail(self):
        frame = copy.deepcopy(self.vox)
        frame.set(80, 4, 30, "minecraft:air")
        with self.assertRaisesRegex(AssertionError, "Missing timber frame"):
            self.check_frame(frame)
        base = copy.deepcopy(self.vox)
        base.set(80, 0, 30, "minecraft:air")
        with self.assertRaisesRegex(AssertionError, "Unsupported board base"):
            self.check_frame(base)
        blocked = copy.deepcopy(self.vox)
        blocked.set(84, 2, 29, "minecraft:chest")
        with self.assertRaisesRegex(AssertionError, "Blocked approach"):
            self.check_approach(blocked)
        missing = copy.deepcopy(self.vox)
        missing.set(89, 0, 30, "minecraft:air")
        with self.assertRaisesRegex(AssertionError, "Unsupported approach"):
            self.check_approach(missing)

    def test_scenery_exact_delta_palette_shared_rng_and_all_other_campus_cells(self):
        self.assertEqual(set(voxel_changes(self.scenery_before, self.vox)), SCENERY)
        self.assertEqual(len(SCENERY), 12)
        self.assertEqual(self.scenery_before.palette, self.vox.palette)
        self.assertEqual(self.rng_states[0], self.rng_states[2])
        changed_indices = {self.vox.idx(*p) for p in SCENERY}
        self.assertEqual({i for i, (old, new) in enumerate(zip(self.scenery_before.grid, self.vox.grid))
                          if old != new}, changed_indices)
        for p in SCENERY:
            self.assertEqual(cell(self.scenery_before, *p), ("minecraft:air", {}))
            name = ("minecraft:white_terracotta" if p == (81, 2, 32)
                    else "minecraft:black_wool" if p == (88, 1, 33)
                    else "minecraft:purple_terracotta" if p[2] == 32
                    else "minecraft:light_blue_terracotta")
            self.assertEqual(cell(self.vox, *p), (name, {}))

    def test_scenery_two_low_supported_forms_have_independent_silhouettes(self):
        self.check_scenery_support(self.vox)
        points = self.scenery_points(self.vox)
        self.assertEqual(points, SCENERY)
        for z, xs, expected in ((32, range(80, 83), [1, 2, 1]),
                                (33, range(87, 90), [3, 2, 3])):
            self.assertEqual([max(y for xx, y, zz in points if (xx, zz) == (x, z))
                              for x in xs], expected)
        self.assertFalse(self.scenery_points(self.scenery_before))

    def test_scenery_preserves_floors_backboard_rails_targets_hay_and_runtime_anchors(self):
        for x in range(self.vox.sx):
            for z in range(self.vox.sz):
                self.assertEqual(cell(self.scenery_before, x, 0, z), cell(self.vox, x, 0, z))
        # Every previously occupied local fixture, including floor marks and
        # target supports, remains byte-for-byte the same palette/state entry.
        for x in range(75, 99):
            for y in range(1, 8):
                for z in range(27, 46):
                    before = cell(self.scenery_before, x, y, z)
                    if before[0] != "minecraft:air":
                        self.assertEqual(cell(self.vox, x, y, z), before)
        self.assertEqual(contract.anchor_errors(contract.runtime_tables(ROOT)["GUILD"]), [])
        self.assertEqual(GS.GUILD_LAYOUT["maze_spawn"], (46, 70))
        self.assertEqual(GS.GUILD_LAYOUT["maze_study_y"], 12)

    def test_scenery_preserves_bypass_both_south_doors_firing_gap_and_complete_walking_graph(self):
        before_nodes, after_nodes = walking_graph(self.scenery_before), walking_graph(self.vox)
        footprint = {(x, 1., z) for x, _, z in SCENERY}
        self.assertEqual(before_nodes - after_nodes, footprint)
        self.assertEqual(after_nodes - before_nodes, set())
        before_reached = reachable(self.scenery_before, before_nodes, (10, 1., 42))
        after_reached = reachable(self.vox, after_nodes, (10, 1., 42))
        self.assertEqual(before_reached - after_reached, footprint)
        for vox, nodes in ((self.scenery_before, before_nodes), (self.vox, after_nodes)):
            self.check_reserved_scenery_routes(vox)
            found = reachable(vox, nodes, (10, 1., 42))
            for run in RESERVED_RUNS:
                for point in run:
                    self.assertIn(point, found)
            for start in ((78, 1., 28), (90, 1., 28), (83, 1., 39)):
                self.assertIn((10, 1., 42), reachable(vox, nodes, start))

    def test_scenery_retains_actual_skill_station_target_and_all_emitted_ray_failures(self):
        before, current = self.actual_skill_report(self.scenery_before), self.actual_skill_report(self.vox)
        self.assertEqual(before, current)
        self.assertEqual(current["actual_emitted_particles_on_clear_lane"], 6)
        self.assertEqual(current["negative_cases"], 10)
        self.assertGreater(current["crossed_cell_negatives"], 20)
        self.assertEqual(current["engine_acceptance"], "unrun")

    def test_scenery_independent_floating_support_bypass_door_and_gap_mutations_fail(self):
        floating = copy.deepcopy(self.vox)
        floating.set(81, 1, 32, "minecraft:air")
        with self.assertRaisesRegex(AssertionError, "Floating scenery column"):
            self.check_scenery_support(floating)
        unsupported = copy.deepcopy(self.vox)
        unsupported.set(89, 0, 33, "minecraft:air")
        with self.assertRaisesRegex(AssertionError, "Unsupported scenery base"):
            self.check_scenery_support(unsupported)
        for where, block in (((84, 2, 31), "minecraft:chest"),
                             ((78, 2, 28), "minecraft:stone"),
                             ((90, 2, 28), "minecraft:stone"),
                             ((83, 1, 38), "minecraft:spruce_fence")):
            blocked = copy.deepcopy(self.vox)
            blocked.set(*where, block)
            with self.assertRaisesRegex(AssertionError, "Blocked reserved route"):
                self.check_reserved_scenery_routes(blocked)
        missing = copy.deepcopy(self.vox)
        missing.set(85, 0, 31, "minecraft:air")
        with self.assertRaisesRegex(AssertionError, "Unsupported reserved route"):
            self.check_reserved_scenery_routes(missing)


if __name__ == "__main__":
    unittest.main(verbosity=2)

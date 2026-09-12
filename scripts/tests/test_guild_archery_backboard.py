"""GP15 final-voxel scenic board, access, fixture support and actual Skill ray.

The historical fixture disables only the new final board helper. Routes use
GP2's conservative occupied intervals; native Bedrock walking remains unrun.
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
        cls.rng_states = [stream.getstate() for stream in streams]

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
        cells = {f"{x},{y},{z}": cell(self.vox, x, y, z)[0]
                 for x in range(77, 94) for y in range(7) for z in range(29, 43)}
        result = subprocess.run(["node", "--experimental-vm-modules", "scripts/tests/guild_archery_voxels.mjs"],
                                input=json.dumps({"cells": cells}), text=True,
                                capture_output=True, cwd=ROOT)
        print(result.stdout, end="")
        self.assertEqual(result.returncode, 0, result.stderr)

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


if __name__ == "__main__":
    unittest.main(verbosity=2)

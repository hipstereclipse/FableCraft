"""GP10: final-voxel map geography, sightlines and unchanged Guild approaches.

The historical map fixture isolates the furniture change within today's whole
Guild builder, so an accidental shared-RNG shift is caught anywhere on campus.
These are offline geometry checks; native rendering and movement remain unrun.
"""
from collections import deque
import copy
import math
from pathlib import Path
import random
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import gen_structures as GS
from test_guild_routes import cell, clear, reachable, walking_graph


def legacy_map_table(v, cx, cz, r):
    """Unchanged historical GP7 allocation, including all 37 random draws."""
    for x in range(cx - 4, cx + 5):
        for z in range(cz - 4, cz + 5):
            d = math.hypot(x - cx, z - cz)
            if d <= 4.3:
                v.set(x, 0, z, GS.DARKOAK)
            if d <= 3.4:
                roll = r.random()
                v.set(x, 1, z,
                      "minecraft:lapis_block" if roll < .34 else
                      "minecraft:moss_block" if roll < .62 else
                      "minecraft:sand" if roll < .74 else
                      "minecraft:emerald_block" if roll < .9 else GS.GOLD)
    v.set(cx, 2, cz, "minecraft:sea_lantern")
    v.set(cx, 3, cz, "minecraft:end_rod")


def voxel_changes(before, after):
    assert (before.sx, before.sy, before.sz) == (after.sx, after.sy, after.sz)
    changed = []
    for i, (old, new) in enumerate(zip(before.grid, after.grid)):
        if before.palette[old] != after.palette[new]:
            x, yz = divmod(i, after.sy * after.sz)
            y, z = divmod(yz, after.sz)
            changed.append((x, y, z))
    return changed


def connected(points):
    if not points:
        return False
    visited = {next(iter(points))}
    todo = deque(visited)
    while todo:
        x, z = todo.popleft()
        for p in ((x-1, z), (x+1, z), (x, z-1), (x, z+1)):
            if p in points and p not in visited:
                visited.add(p)
                todo.append(p)
    return visited == points


class GuildMapTable(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.vox = GS.build_guild_hall()
        with patch.object(GS, "build_guild_map_table", legacy_map_table):
            cls.before = GS.build_guild_hall()
        cls.cx, cls.cz, _ = GS.GUILD_LAYOUT["rotunda"]
        cls.footprint = {(x, z) for x in range(cls.cx-4, cls.cx+5)
                         for z in range(cls.cz-4, cls.cz+5)
                         if math.hypot(x-cls.cx, z-cls.cz) <= 3.4}

    def assert_furniture_scope(self, before, after):
        changes = voxel_changes(before, after)
        self.assertTrue(changes)
        for x, y, z in changes:
            self.assertTrue((x, z) in self.footprint and 1 <= y <= 3,
                            f"Changed non-map voxel {(x, y, z)}")

    def assert_low_geography(self, vox):
        water, land = set(), set()
        earth = {"minecraft:coarse_dirt", "minecraft:moss_block", "minecraft:sandstone_slab"}
        allowed = earth | {"minecraft:spruce_slab", "minecraft:dark_prismarine_slab"}
        for x, z in self.footprint:
            name, states = cell(vox, x, 1, z)
            self.assertIn(name, allowed)
            if name.endswith("_slab"):
                self.assertEqual(states, {"minecraft:vertical_half": "bottom"})
            if name == "minecraft:dark_prismarine_slab":
                water.add((x, z))
            elif name in earth:
                land.add((x, z))
            for y in (2, 3):
                self.assertEqual(cell(vox, x, y, z)[0], "minecraft:air", "Raised map obstruction")
        self.assertTrue(connected(water), "Disconnected sea")
        self.assertTrue(connected(land), "Disconnected landform")
        self.assertGreater(len(land), len(water))
        self.assertGreaterEqual(len(water), 6)

    def test_complete_guild_delta_is_confined_to_map_furniture(self):
        self.assert_furniture_scope(self.before, self.vox)
        # Independent cell count catches disappearing detail or a no-op replacement.
        self.assertEqual(len(voxel_changes(self.before, self.vox)), 38)

    def test_connected_land_and_recessed_sea_replace_jewel_mosaic_and_beacon(self):
        self.assert_low_geography(self.vox)
        # The single half-height coastline shelf is part of the land, not a light.
        self.assertEqual(cell(self.vox, 26, 1, 43)[0], "minecraft:sandstone_slab")

    def test_low_wood_rim_preserves_the_exact_table_footprint(self):
        for x in range(self.cx-4, self.cx+5):
            for z in range(self.cz-4, self.cz+5):
                self.assertEqual(cell(self.vox, x, 0, z), cell(self.before, x, 0, z))
                self.assertEqual(cell(self.vox, x, 1, z)[0] != "minecraft:air",
                                 cell(self.before, x, 1, z)[0] != "minecraft:air")
                if (x, z) in self.footprint and any((x+dx, z+dz) not in self.footprint
                        for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                    self.assertEqual(cell(self.vox, x, 1, z),
                                     ("minecraft:spruce_slab", {"minecraft:vertical_half": "bottom"}))

    def test_wake_lectern_fronts_and_existing_side_approaches_remain_reachable(self):
        nodes = walking_graph(self.vox)
        walked = reachable(self.vox, nodes, (10, 1., 42))
        self.assertEqual(GS.GUILD_LAYOUT["wake"], (20, 42))
        self.assertEqual(GS.GUILD_LAYOUT["quest_tables"], ((22, 42), (28, 39), (28, 45)))
        fronts = ((21, 1., 42), (28, 1., 38), (28, 1., 46))
        for point in fronts + ((20, 1., 42), (22, 1., 41), (22, 1., 43)):
            self.assertIn(point, walked, f"Lost map approach or Guildmaster birth {point}")
        for qx, qz in GS.GUILD_LAYOUT["quest_tables"]:
            self.assertEqual(cell(self.vox, qx, 1, qz), cell(self.before, qx, 1, qz))
            for x, z in ((qx-1, qz), (qx+1, qz), (qx, qz-1), (qx, qz+1)):
                if clear(self.before, x, 1., z):
                    self.assertTrue(clear(self.vox, x, 1., z), f"Lost lectern side {(x, z)}")

    def test_authored_map_is_seed_independent_but_retains_37_legacy_draws(self):
        maps = []
        for seed in (17, 9001):
            vox = GS.Vox(11, 6, 11)
            actual, expected = random.Random(seed), random.Random(seed)
            GS.build_guild_map_table(vox, 5, 5, actual)
            for _ in range(37):
                expected.random()
            self.assertEqual(actual.getstate(), expected.getstate())
            maps.append([vox.palette[i] for i in vox.grid])
        self.assertEqual(*maps)

    def test_independent_beacon_broken_rim_and_rng_shift_fixtures_fail(self):
        beacon = copy.deepcopy(self.vox)
        beacon.set(self.cx, 2, self.cz, "minecraft:sea_lantern")
        with self.assertRaisesRegex(AssertionError, "Raised map obstruction"):
            self.assert_low_geography(beacon)
        broken = copy.deepcopy(self.vox)
        broken.set(self.cx, 1, self.cz-3, "minecraft:air")
        with self.assertRaises(AssertionError):
            self.assert_low_geography(broken)
        authored = GS.build_guild_map_table
        def shifted(v, cx, cz, r):
            authored(v, cx, cz, r)
            r.random()
        with patch.object(GS, "build_guild_map_table", shifted):
            shifted_guild = GS.build_guild_hall()
        with self.assertRaisesRegex(AssertionError, "Changed non-map voxel"):
            self.assert_furniture_scope(self.vox, shifted_guild)


if __name__ == "__main__":
    unittest.main(verbosity=2)

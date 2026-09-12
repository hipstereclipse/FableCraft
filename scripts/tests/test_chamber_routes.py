"""GP5/GP8 final Chamber voxels, half-step collision and damaged routes.

The tested Vox is the final save input; its emitted NBT must equal the shipped
asset. Full/bottom/top slab surfaces and two-block swept headroom are modeled
offline. These checks do not establish live Bedrock physics or NPC navigation.
"""
from collections import deque
import contextlib
import copy
import hashlib
import io
import json
import math
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import gen_structures as GS
from test_guild_routes import FLOORS, cell, clear, interval

CHAMBER_FLOORS = FLOORS | {'minecraft:chiseled_sandstone'}


def supported(vox, x, feet, z):
    y = math.ceil(feet) - 1
    name, states = cell(vox, x, y, z)
    span = interval(name, states, y)
    return name in CHAMBER_FLOORS and span is not None and span[1] == feet


def walking_graph(vox):
    nodes = set()
    for x in range(vox.sx):
        for z in range(vox.sz):
            for y in range(vox.sy):
                name, states = cell(vox, x, y, z)
                if name not in CHAMBER_FLOORS:
                    continue
                feet = interval(name, states, y)[1]
                if clear(vox, x, feet, z):
                    nodes.add((x, feet, z))
    return nodes


def reached(vox, start):
    nodes = walking_graph(vox)
    seen = {start} if start in nodes else set()
    queue = deque(seen)
    while queue:
        x, y, z = queue.popleft()
        for xx, zz in ((x - 1, z), (x + 1, z), (x, z - 1), (x, z + 1)):
            for dy in (-.5, 0, .5):
                candidate = (xx, y + dy, zz)
                if candidate not in nodes or candidate in seen:
                    continue
                top = max(y, y + dy)
                if clear(vox, x, top, z) and clear(vox, xx, top, zz):
                    seen.add(candidate)
                    queue.append(candidate)
    return seen


def protected_gp5_digest(vox):
    """Frozen GP5 altar/standing clearance, entry, foundation and containment.

    GP8 intentionally replaces the walls and ceiling. Preserve the actual altar
    radius (8.4), not the old obstructing lamps just outside it at radius 8.54.
    """
    values = []
    for x in range(vox.sx):
        for y in range(vox.sy):
            for z in range(vox.sz):
                protected = (y == 0 or (math.hypot(x - 15, z - 15) <= 8.4 and y <= 6)
                             or (13 <= x <= 17 and z <= 11 and y <= 6) or y in (17, 18))
                if not protected:
                    continue
                name, states = cell(vox, x, y, z)
                values.append([x, y, z, name, states])
    return hashlib.sha256(json.dumps(values, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


class ChamberRoutes(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        captured = {}
        original_save = GS.Vox.save

        def save(vox, name):
            captured[name] = vox
            original_save(vox, name)

        with tempfile.TemporaryDirectory() as directory:
            with patch.object(GS, 'BP', Path(directory)), patch.object(GS.Vox, 'save', save):
                with contextlib.redirect_stdout(io.StringIO()):
                    GS.chamber_of_fate()
            cls.emitted = (Path(directory) / 'structures/fc/chamber_of_fate.mcstructure').read_bytes()
        cls.vox = captured['chamber_of_fate']
        cls.arch = (15, 2., 0)
        cls.cullis = (15, 5., 15)

    def north_run(self, x=15):
        # Surveyed independently of the owner's stair loop: the entire north
        # vestibule, each alternating surface, and the existing ward/core deck.
        heights = (2., 2., 2., 2., 2., 2., 2., 2.5, 3., 3.5, 4., 4.5, 5., 5., 5., 5.)
        return [(x, height, z) for z, height in enumerate(heights)]

    def check_run(self, points, vox=None):
        vox = vox or self.vox
        for direction in (points, list(reversed(points))):
            for x, feet, z in direction:
                self.assertTrue(supported(vox, x, feet, z), f'No surface {(x, feet, z)}')
                self.assertTrue(clear(vox, x, feet, z), f'Blocked standing {(x, feet, z)}')
            for a, b in zip(direction, direction[1:]):
                self.assertEqual(abs(a[0] - b[0]) + abs(a[2] - b[2]), 1, f'Nonadjacent {a} -> {b}')
                self.assertLessEqual(abs(a[1] - b[1]), .5, f'Jump {a} -> {b}')
                for x, _, z in (a, b):
                    self.assertTrue(clear(vox, x, max(a[1], b[1]), z), f'Blocked transition {a} -> {b}')

    def test_final_emitted_asset_and_generated_interaction_contract(self):
        asset = GS.BP / 'structures/fc/chamber_of_fate.mcstructure'
        self.assertEqual(self.emitted, asset.read_bytes(), 'Regenerate only the Chamber asset through its owner')
        self.assertEqual(GS.CHAMBER_LAYOUT['size'], (31, 20, 31))
        self.assertEqual((self.vox.sx, self.vox.sy, self.vox.sz), (31, 20, 31))
        self.assertEqual(GS.CHAMBER_LAYOUT['origin'], (11, -22, 27))
        self.assertEqual(GS.CHAMBER_LAYOUT['cullis'], self.cullis)
        self.assertEqual(GS.CHAMBER_LAYOUT['north_entry'], self.arch)
        self.assertEqual(cell(self.vox, 15, 4, 15)[0], 'minecraft:sea_lantern')
        self.assertTrue(supported(self.vox, *self.cullis))
        self.assertTrue(clear(self.vox, *self.cullis))
        # The old registered feet y7 have no supporting platform.
        self.assertFalse(supported(self.vox, 15, 7., 15))

    def test_three_wide_north_arch_to_cullis_and_return_have_half_steps(self):
        for x in (14, 15, 16):
            self.check_run(self.north_run(x))
        self.assertIn(self.cullis, reached(self.vox, self.arch))
        self.assertIn(self.arch, reached(self.vox, self.cullis))

    def test_all_cardinal_and_diagonal_altar_approaches_climb_and_return(self):
        # The side/south approaches start beside the existing outer columns and
        # braziers, then join the radial treads. All eight runs reach the core.
        approaches = [[(15, 2., 6)], [(24, 2., 14), (23, 2.5, 14)],
                      [(16, 2., 24), (16, 2.5, 23)], [(6, 2., 16), (7, 2.5, 16)]]
        north = self.north_run()[7:]
        diagonal = [(6, 2., -6), (5, 2.5, -6), (5, 3., -5), (4, 3., -5),
                    (4, 3.5, -4), (3, 4., -4), (3, 4.5, -3), (2, 4.5, -3),
                    (2, 5., -2), (1, 5., -2), (0, 5., -2), (0, 5., -1), (0, 5., 0)]
        for turn in range(4):
            def rotate(x, y, z):
                for _ in range(turn):
                    x, z = -z, x
                return (x + 15, y, z + 15)
            self.check_run(approaches[turn] + [rotate(x - 15, y, z - 15) for x, y, z in north])
            self.check_run([rotate(x, y, z) for x, y, z in diagonal])

    def test_concentric_treads_cover_full_circumference_and_join_cardinal_walking_graph(self):
        nodes = walking_graph(self.vox)
        forward = reached(self.vox, self.arch)
        footprint = {(x, z) for x in range(31) for z in range(31)
                     if 3.4 < math.hypot(x - 15, z - 15) <= 8.4}
        # Survey the altar's vertical interval; the opaque GP8 roof also has a
        # solid top above these x/z columns and is not an altar tread.
        treads = {(x, z): y for x, y, z in nodes if (x, z) in footprint and 2 < y < 5}
        self.assertEqual(set(treads), footprint, 'An altar column has no clear supported tread')
        expected_counts = {2.5: 44, 3.: 48, 3.5: 32, 4.: 36, 4.5: 24}
        for feet, count in expected_counts.items():
            band = {(x, z) for (x, z), y in treads.items() if y == feet}
            self.assertEqual(len(band), count)
            # Eight-neighbor continuity certifies a complete rasterized annulus,
            # not diagonal movement physics. Actual travel is certified below
            # with cardinal half-step transitions, including corner detours.
            seen = {next(iter(band))}
            queue = deque(seen)
            while queue:
                x, z = queue.popleft()
                for dx in (-1, 0, 1):
                    for dz in (-1, 0, 1):
                        point = (x + dx, z + dz)
                        if point in band and point not in seen:
                            seen.add(point)
                            queue.append(point)
            self.assertEqual(seen, band, f'Disconnected circumference at feet y{feet}')
            for quadrant in ((-1, -1), (-1, 1), (1, -1), (1, 1)):
                self.assertTrue(any((x - 15) * quadrant[0] > 0 and (z - 15) * quadrant[1] > 0
                                    for x, z in band))
        for (x, z), feet in treads.items():
            self.assertTrue((x, feet, z) in forward, f'Isolated tread {(x, feet, z)}')
            expected = 'minecraft:stone_brick_slab' if feet % 1 else 'minecraft:stone_bricks'
            self.assertEqual(cell(self.vox, x, math.ceil(feet) - 1, z)[0], expected)
            for xx, zz in ((x - 1, z), (x + 1, z), (x, z - 1), (x, z + 1)):
                if (xx, zz) in treads:
                    self.assertLessEqual(abs(feet - treads[xx, zz]), .5,
                                         f'Full-height jump between adjacent treads {(x, z)} and {(xx, zz)}')

    def test_exported_runtime_plan_matches_final_chamber_and_actual_guild_entry(self):
        source = (GS.BP / 'scripts/fc_gamedata.js').read_text()
        data, _ = json.JSONDecoder().raw_decode(source.split('export const DATA = ', 1)[1])
        contract = data['guildChamber']
        for key in ('size', 'origin', 'cullis'):
            self.assertEqual(contract[key], list(GS.CHAMBER_LAYOUT[key]))

        def decode(plan):
            palette = [(entry['name'], entry['states']) for entry in plan['palette']]
            cells = []
            for index, count in plan['runs']:
                self.assertIs(type(index), int)
                self.assertIs(type(count), int)
                self.assertGreater(count, 0)
                self.assertTrue(0 <= index < len(palette))
                cells.extend([palette[index]] * count)
            self.assertEqual(len(cells), math.prod(plan['size']))
            return cells

        self.assertEqual(decode(contract), [self.vox.palette[index] for index in self.vox.grid])
        entry = contract['entry']
        self.assertEqual(entry['origin'], [25, 0, 12])
        self.assertEqual(entry['size'], [5, 3, 5])
        guild = GS.build_guild_hall()
        expected = [cell(guild, x, y, z) for x in range(25, 30)
                    for y in range(3) for z in range(12, 17)]
        self.assertEqual(decode(entry), expected)

    def test_gp5_compatibility_manifest_is_frozen_and_exported_unchanged(self):
        frozen = Path(__file__).resolve().parents[2] / 'scripts/data/guild_chamber_gp5.json'
        self.assertEqual(hashlib.sha256(frozen.read_bytes()).hexdigest(),
                         'a8f59e438d2a9e64876acb7ff5e2cd32494c03a06608c195b646d58a706a9916')
        source = (GS.BP / 'scripts/fc_gamedata.js').read_text()
        data, _ = json.JSONDecoder().raw_decode(source.split('export const DATA = ', 1)[1])
        self.assertEqual(data['guildChamber']['compatibility'], [json.loads(frozen.read_text())])

    def test_bottom_slab_surfaces_and_swept_headroom(self):
        for x in (14, 15, 16):
            for y, z in ((2, 7), (3, 9), (4, 11)):
                self.assertEqual(cell(self.vox, x, y, z),
                                 ('minecraft:stone_brick_slab', {'minecraft:vertical_half': 'bottom'}))
                self.assertTrue(supported(self.vox, x, y + .5, z))
                self.assertFalse(supported(self.vox, x, y + 1., z))
        top = copy.deepcopy(self.vox)
        top.set(15, 3, 9, 'minecraft:stone_brick_slab', {'minecraft:vertical_half': 'top'})
        with self.assertRaisesRegex(AssertionError, 'No surface'):
            self.check_run(self.north_run(), top)
        # Two standing columns can each be clear but ascending movement still
        # strikes a low ceiling over the lower tread; the swept check catches it.
        overhang = copy.deepcopy(self.vox)
        overhang.set(15, 4, 6, 'minecraft:stone_bricks')
        self.assertTrue(clear(overhang, 15, 2., 6))
        with self.assertRaisesRegex(AssertionError, 'Blocked transition'):
            self.check_run(self.north_run(), overhang)

    def test_adjacent_floor_routes_and_warded_dais_remain_connected(self):
        forward = reached(self.vox, self.arch)
        # East/west outer floor and south floor remain reachable around the
        # mound; all four dais sides connect to the Cullis and the north stair.
        for point in ((5, 2., 14), (25, 2., 14), (15, 2., 25),
                      (12, 5., 15), (18, 5., 15), (15, 5., 18)):
            self.assertTrue(point in forward, f'Lost adjacent route {point}')
            self.assertTrue(self.arch in reached(self.vox, point), f'No return from {point}')

    def test_independent_local_missing_tread_and_head_obstruction_reject_damaged_approach(self):
        hole = copy.deepcopy(self.vox)
        hole.fill(14, 2, 9, 16, 3, 9, 'minecraft:air')
        with self.assertRaisesRegex(AssertionError, 'No surface'):
            self.check_run(self.north_run(), hole)
        # Surrounding treads provide another approach; the damaged local flight
        # must fail its own survey even while the rest of the altar stays usable.
        self.assertIn(self.cullis, reached(hole, self.arch))
        self.assertIn(self.arch, reached(hole, self.cullis))
        blocked = copy.deepcopy(self.vox)
        blocked.fill(14, 4, 9, 16, 5, 9, 'minecraft:stone_bricks')
        with self.assertRaisesRegex(AssertionError, 'Blocked standing'):
            self.check_run(self.north_run(), blocked)
        self.assertIn(self.cullis, reached(blocked, self.arch))
        self.assertIn(self.arch, reached(blocked, self.cullis))

    def test_skylight_water_is_contained_and_independent_missing_rim_fails(self):
        def containment(vox):
            water = {(x, y, z) for x in range(vox.sx) for y in range(vox.sy) for z in range(vox.sz)
                     if cell(vox, x, y, z)[0] == 'minecraft:water'}
            self.assertEqual(len(water), 177)
            rim = set()
            for x, y, z in water:
                self.assertEqual(cell(vox, x, y - 1, z)[0], 'minecraft:glass', 'No skylight water base')
                for xx, zz in ((x - 1, z), (x + 1, z), (x, z - 1), (x, z + 1)):
                    if (xx, y, zz) in water:
                        continue
                    self.assertEqual(cell(vox, xx, y, zz)[0], 'minecraft:glass',
                                     f'Uncontained skylight water at {(xx, y, zz)}')
                    rim.add((xx, y, zz))
            self.assertEqual(len(rim), 44)
        containment(self.vox)
        leaking = copy.deepcopy(self.vox)
        leaking.set(7, 18, 15, 'minecraft:air')
        with self.assertRaisesRegex(AssertionError, 'Uncontained skylight'):
            containment(leaking)

    def test_gp8_preserves_gp5_altar_entry_foundation_and_containment(self):
        # 4,419 independently frozen cells from the unchanged GP7 Chamber owner.
        self.assertEqual(protected_gp5_digest(self.vox),
                         '431343b708bfb6b5c9a803bc8c787dc254d36f50e8abd5a197bd8e3b29b65a53')
        self.assertEqual(GS.GUILD_LAYOUT['maze_spawn'], (46, 70))
        self.assertEqual(GS.GUILD_LAYOUT['maze_study_y'], 12)
        self.assertEqual(GS.GUILD_LAYOUT['size'], (122, 30, 108))

    def test_outer_walk_is_clear_all_around_and_local_obstruction_fails(self):
        def outer_walk(vox):
            accessible = reached(vox, self.arch)
            for x in range(31):
                for z in range(31):
                    if 8.6 < math.hypot(x - 15, z - 15) <= 10.5:
                        self.assertTrue(supported(vox, x, 2., z), f'Outer walk floor {(x, z)}')
                        self.assertTrue(clear(vox, x, 2., z), f'Outer walk blocked {(x, z)}')
                        self.assertIn((x, 2., z), accessible, f'Outer walk isolated {(x, z)}')
        outer_walk(self.vox)
        blocked = copy.deepcopy(self.vox)
        blocked.set(24, 2, 15, 'minecraft:campfire')
        with self.assertRaisesRegex(AssertionError, 'Outer walk blocked'):
            outer_walk(blocked)

    def test_pointed_wall_bays_have_connected_ribs_and_widen_below_apex(self):
        # Independently surveyed east bay, then all four cardinal rotations.
        # The original source supports pointed wall ribs, not their exact count.
        profile = {3: {-3, 3}, 6: {-3, 3}, 7: {-3, -2, 2, 3},
                   8: {-2, -1, 1, 2}, 9: {-1, 0, 1}, 10: {0}}
        for turn in range(4):
            for y, offsets in profile.items():
                for tangent in range(-4, 5):
                    x, z = 11, tangent
                    for _ in range(turn):
                        x, z = -z, x
                    x, z = x + 15, z + 15
                    # North entry keeps its GP5 aperture through y6; lamps
                    # occupy the center at y6/7 of the other three bays.
                    if turn == 3 and y <= 6 and abs(tangent) <= 2:
                        continue
                    if y in (6, 7) and tangent == 0:
                        continue
                    self.assertEqual(cell(self.vox, x, y, z)[0] == 'minecraft:stone_bricks',
                                     tangent in offsets, f'Broken pointed rib {(x, y, z)}')

    def test_shell_is_closed_except_entry_and_independent_wall_breach_fails(self):
        def enclosure(vox):
            room = copy.deepcopy(vox)
            room.fill(13, 2, 0, 17, 6, 4, 'minecraft:stone_bricks')
            visited = {(15, 8, 15)}
            pending = deque(visited)
            while pending:
                x, y, z = pending.popleft()
                self.assertTrue(0 < x < 30 and 0 < y < 19 and 0 < z < 30,
                                f'Chamber shell leak {(x, y, z)}')
                for dx, dy, dz in ((-1, 0, 0), (1, 0, 0), (0, -1, 0),
                                   (0, 1, 0), (0, 0, -1), (0, 0, 1)):
                    point = (x + dx, y + dy, z + dz)
                    if point not in visited and cell(room, *point)[0] == 'minecraft:air':
                        visited.add(point)
                        pending.append(point)
        enclosure(self.vox)
        breach = copy.deepcopy(self.vox)
        breach.fill(26, 5, 15, 30, 5, 15, 'minecraft:air')
        with self.assertRaisesRegex(AssertionError, 'Chamber shell leak'):
            enclosure(breach)


if __name__ == '__main__':
    unittest.main(verbosity=2)

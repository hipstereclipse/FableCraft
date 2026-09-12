"""GP12 final Library furnishings, support, access and whole-campus scope."""
from collections import deque
import copy
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import gen_structures as GS
from test_guild_routes import cell, clear, interval, reachable, supported, walking_graph


def previous_library_interior(vox):
    """Frozen pre-GP12 owner behavior, injected before all final decorator passes.

    The helper consumed no random values; the original central lamp is retained
    here so the actual final decor owner, not this fixture, removes it.
    """
    for z in (19, 21, 23, 25, 27):
        for y in (1, 2, 3, 6, 7):
            for x in (19, 35):
                vox.set(x, y, z, 'minecraft:bookshelf')
    for z, facing in ((19, 'west'), (23, 'east'), (27, 'west')):
        vox.set(22, 1, z, 'minecraft:lectern', {'minecraft:cardinal_direction': facing})
    vox.set(27, 7, 23, 'minecraft:lantern', {'hanging': True})


def permitted_change(x, y, z):
    return ((x in (19, 35) and 1 <= y <= 7 and 18 <= z <= 28)
            or (x in (20, 34) and y in (5, 6) and z in (19, 27))
            or (x == 31 and y in (1, 2) and 20 <= z <= 26))


class GuildLibrary(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.vox = GS.build_guild_hall()
        with patch.object(GS, 'build_guild_library_interior', previous_library_interior):
            cls.before = GS.build_guild_hall()
        cls.nodes = walking_graph(cls.vox)
        cls.from_gate = reachable(cls.vox, cls.nodes, (10, 1., 42))

    def assert_scope(self, vox):
        changed = []
        for x in range(vox.sx):
            for y in range(vox.sy):
                for z in range(vox.sz):
                    if cell(vox, x, y, z) != cell(self.before, x, y, z):
                        self.assertTrue(permitted_change(x, y, z), f'Unrelated campus change {(x, y, z)}')
                        changed.append((x, y, z))
        return changed

    def assert_case_connected(self, vox, x):
        pieces = {(x, y, z) for y in range(1, 8) for z in range(18, 29)
                  if cell(vox, x, y, z)[0] in ('minecraft:bookshelf', 'minecraft:dark_oak_planks')}
        roots = {p for p in pieces if p[1] == 1 and supported(vox, p[0], 1., p[2])}
        seen, pending = set(roots), deque(roots)
        while pending:
            xx, y, z = pending.popleft()
            for dy, dz in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                point = (xx, y + dy, z + dz)
                if point in pieces and point not in seen:
                    seen.add(point)
                    pending.append(point)
        self.assertTrue(pieces)
        self.assertEqual(seen, pieces, f'Detached bookcase band x{x}')
        for y in range(1, 8):
            for z in range(18, 29):
                if x == 19 and y <= 3 and 21 <= z <= 23:
                    self.assertEqual(cell(vox, x, y, z)[0], 'minecraft:air', 'Blocked west Library door')
                else:
                    self.assertIn((x, y, z), pieces, f'Broken continuous case {(x, y, z)}')

    def assert_lamps(self, vox):
        for x, z in ((20, 19), (20, 27), (34, 19), (34, 27)):
            self.assertEqual(cell(vox, x, 5, z), ('minecraft:lantern', {'hanging': True}))
            self.assertEqual(cell(vox, x, 6, z)[0], 'minecraft:dark_oak_planks', 'Missing lamp support')
            case_x = 19 if x == 20 else 35
            self.assertIn(cell(vox, case_x, 6, z)[0], ('minecraft:bookshelf', 'minecraft:dark_oak_planks'),
                          'Detached lamp bracket')

    def assert_spine(self, vox):
        for x in (25, 26, 27, 28, 29):
            for z in range(17, 30):
                self.assertTrue(supported(vox, x, 1., z), f'Library spine floor {(x, z)}')
                self.assertTrue(clear(vox, x, 1., z), f'Library spine blocked {(x, z)}')

    def test_baseline_reproduces_disconnected_shelf_bands_and_missing_light(self):
        with self.assertRaisesRegex(AssertionError, 'Detached bookcase band'):
            self.assert_case_connected(self.before, 35)
        self.assertEqual(cell(self.before, 27, 7, 23)[0], 'minecraft:air')
        lights = [cell(self.before, x, y, z)[0] for x in range(19, 36)
                  for y in range(1, 9) for z in range(17, 30)
                  if cell(self.before, x, y, z)[0] in ('minecraft:lantern', 'minecraft:torch')]
        self.assertEqual(lights, [])

    def test_final_changes_are_only_furnishings_preserving_floor_shell_anchors_and_rng(self):
        self.assertTrue(self.assert_scope(self.vox))
        self.assertEqual(GS.GUILD_LAYOUT['size'], (122, 30, 108))
        self.assertEqual(GS.GUILD_LAYOUT['maze_spawn'], (46, 70))
        self.assertEqual(GS.GUILD_LAYOUT['maze_study_y'], 12)
        self.assertEqual(GS.GUILD_LAYOUT['cave_shaft'], (27, 14))
        drift = copy.deepcopy(self.vox)
        drift.set(86, 0, 39, 'minecraft:diamond_block')
        with self.assertRaisesRegex(AssertionError, 'Unrelated campus change'):
            self.assert_scope(drift)

    def test_bookcases_are_continuous_and_grounded_with_broken_band_negative(self):
        for x in (19, 35):
            self.assert_case_connected(self.vox, x)
        broken = copy.deepcopy(self.vox)
        broken.fill(35, 4, 18, 35, 4, 28, 'minecraft:air')
        with self.assertRaisesRegex(AssertionError, 'Detached bookcase band'):
            self.assert_case_connected(broken, 35)

    def test_final_lamps_have_connected_solid_support_and_missing_support_fails(self):
        self.assert_lamps(self.vox)
        unsupported = copy.deepcopy(self.vox)
        unsupported.set(20, 6, 19, 'minecraft:air')
        with self.assertRaisesRegex(AssertionError, 'Missing lamp support'):
            self.assert_lamps(unsupported)
        detached = copy.deepcopy(self.vox)
        detached.set(19, 6, 19, 'minecraft:air')
        with self.assertRaisesRegex(AssertionError, 'Detached lamp bracket'):
            self.assert_lamps(detached)

    def test_desk_has_supported_half_slab_top_with_both_sides_and_lecterns_accessible(self):
        for z in range(20, 27):
            name, states = cell(self.vox, 31, 2, z)
            self.assertEqual(name, 'minecraft:spruce_slab')
            self.assertEqual(interval(name, states, 2), (2, 2.5))
            for x in (30, 32):
                self.assertIn((x, 1., z), self.from_gate, 'Inaccessible desk side')
        for z in (20, 23, 26):
            self.assertEqual(cell(self.vox, 31, 1, z)[0], 'minecraft:dark_oak_planks')
            self.assertTrue(supported(self.vox, 31, 1., z))
        for z in (19, 23, 27):
            self.assertEqual(cell(self.vox, 22, 1, z), cell(self.before, 22, 1, z))
            self.assertIn((22, 1., z + 1), self.from_gate, 'Inaccessible lectern')

    def test_cave_entry_commons_north_wing_and_resident_routes_survive_with_local_negatives(self):
        self.assert_spine(self.vox)
        for destination in ((26, 1., 24), (27, 1., 16), (18, 1., 22), (34, 1., 16),
                            (27, 1., 29), (27, 1., 32), (16, 1., 35), (16, 1., 49),
                            (31, 10., 42), (39, 8., 42), (46, 12., 70)):
            self.assertIn(destination, self.from_gate, f'Lost Library/adjacent access {destination}')
            self.assertIn((10, 1., 42), reachable(self.vox, self.nodes, destination))
        blocked = copy.deepcopy(self.vox)
        blocked.set(26, 2, 26, 'minecraft:chest')
        with self.assertRaisesRegex(AssertionError, 'Library spine blocked'):
            self.assert_spine(blocked)
        hole = copy.deepcopy(self.vox)
        hole.set(26, 0, 26, 'minecraft:air')
        with self.assertRaisesRegex(AssertionError, 'Library spine floor'):
            self.assert_spine(hole)


if __name__ == '__main__':
    unittest.main(verbosity=2)

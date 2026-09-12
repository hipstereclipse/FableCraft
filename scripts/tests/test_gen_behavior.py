"""Regression contract for the repaired generator; no writes to the live packs.

python scripts/tests/test_gen_behavior.py
FC_BEHAVIOR_SOURCE=tmp/conformance/gen_behavior_stripped.py python scripts/tests/test_gen_behavior.py
"""
import importlib.util
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
import fc_data
from fc_mobs import MOBS, is_romanceable

source = Path(os.environ.get('FC_BEHAVIOR_SOURCE', ROOT / 'scripts/gen_behavior.py'))
spec = importlib.util.spec_from_file_location('behavior_under_test', source)
gb = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gb)


class BehaviorRegression(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.bp = Path(self.temp.name)
        self.redirect = patch.object(gb, 'BP', self.bp)
        self.redirect.start()
        self.addCleanup(self.redirect.stop)

    def test_social_contracts(self):
        social = [m for m in MOBS if m['behavior'] in ('npc', 'guard') or m['id'] == 'mercenary']
        self.assertGreaterEqual(len(social), 21)
        for mob in social:
            with self.subTest(mob=mob['id']):
                gb.emit_entity(mob)
                data = json.loads((self.bp / 'entities' / (mob['id'] + '.json')).read_text())['minecraft:entity']
                for event in ('fc:react_flee', 'fc:react_attack', 'fc:react_neutral', 'fc:react_follow', 'fc:react_watch'):
                    self.assertIn(event, data['events'])
                self.assertIn('minecraft:persistent', data['components'])
                self.assertNotIn('minecraft:despawn', data['components'])
                for prop in ('fc:love_hate', 'fc:fear_funny', 'fc:ugly_attractive'):
                    self.assertTrue(data['description']['properties'][prop]['client_sync'])
                if is_romanceable(mob):
                    self.assertTrue(data['description']['properties']['fc:married']['client_sync'])
                if mob['id'].startswith('guild_apprentice_'):
                    self.assertIn('fc:guild_training_start', data['events'])
                if mob['behavior'] == 'guard':
                    self.assertIn('fc:bounty_hostile', data['events'])

    def test_theresa_matches_existing_entity(self):
        mob = next(m for m in MOBS if m['id'] == 'theresa')
        gb.emit_entity(mob)
        generated = json.loads((self.bp / 'entities/theresa.json').read_text())
        existing = json.loads((ROOT / 'packs/Fablecraft_BP/entities/theresa.json').read_text())
        self.assertEqual(generated, existing)

    def test_guild_training_restores_overridden_components(self):
        # Component removal does not fall back to base components in Bedrock.
        # Exercise the emitted transition actions with remove-then-add semantics.
        keys = ('minecraft:movement', 'minecraft:knockback_resistance', 'minecraft:pushable')
        for mob in (m for m in MOBS if m['id'].startswith('guild_apprentice_')):
            with self.subTest(mob=mob['id']):
                gb.emit_entity(mob)
                data = json.loads((self.bp / 'entities' / (mob['id'] + '.json')).read_text())['minecraft:entity']
                live = dict(data['components'])
                groups = data['component_groups']
                for event in ('fc:guild_training_start', 'fc:guild_training_stop',
                              'fc:guild_training_stop', 'fc:guild_training_start', 'fc:guild_training_stop'):
                    action = data['events'][event]
                    for group in action.get('remove', {}).get('component_groups', []):
                        for key in groups[group]:
                            live.pop(key, None)
                    for group in action.get('add', {}).get('component_groups', []):
                        live.update(groups[group])
                    if event.endswith('_start'):
                        self.assertEqual(live['minecraft:movement']['value'], 0)
                    else:
                        for key in keys:
                            self.assertEqual(live[key], data['components'][key])
                        self.assertGreater(live['minecraft:movement']['value'], 0)
                        self.assertTrue(live['minecraft:pushable']['is_pushable'])

    def test_all_item_formats(self):
        items = fc_data.all_items()
        self.assertGreaterEqual(len(items), 194)
        for item in items:
            with self.subTest(item=item['id']):
                emitter = (gb.emit_weapon if item['cat'] in ('melee', 'ranged') else
                           gb.emit_armor if item['cat'] == 'armor' else
                           gb.emit_consumable if item['cat'] == 'consumable' else gb.emit_simple)
                emitter(item)
                comp = json.loads((self.bp / 'items' / (item['id'] + '.json')).read_text())['minecraft:item']['components']
                self.assertEqual(comp['minecraft:icon'], item['id'])
                if item['cat'] in ('melee', 'ranged'):
                    self.assertIsInstance(comp['minecraft:damage'], (int, float))
                    self.assertEqual(comp['minecraft:damage'], item['damage'])
        # wd focus is maintained outside fc_data; an isolated behavior regen must
        # not overwrite it, and the checked-in charge contract must survive.
        self.assertFalse((self.bp / 'items/will_focus.json').exists())
        focus = json.loads((ROOT / 'packs/Fablecraft_BP/items/will_focus.json').read_text())['minecraft:item']['components']
        self.assertEqual(focus['minecraft:icon'], 'will_focus')
        self.assertGreater(focus['minecraft:use_modifiers']['use_duration'], 1)

    def test_alignment_cosmetics(self):
        self.assertTrue(hasattr(gb, 'emit_alignment_cosmetics'))
        gb.emit_alignment_cosmetics()
        for name in ('evil_horns', 'divine_halo'):
            data = json.loads((self.bp / 'entities' / (name + '.json')).read_text())['minecraft:entity']
            self.assertFalse(data['components']['minecraft:physics']['has_collision'])
            self.assertIn('minecraft:persistent', data['components'])


if __name__ == '__main__':
    unittest.main(verbosity=2)

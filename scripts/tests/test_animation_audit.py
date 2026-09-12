"""Regression tests for real gate-driver audit and CLI exit status."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
from _audit_anims import audit_entity


class GateAudit(unittest.TestCase):
    def setUp(self):
        self.desc = {'identifier': 'fc:test', 'animations': {'ctrl': 'controller.test', 'attack': 'animation.test'},
                     'scripts': {'animate': ['ctrl']}}
        self.ctrl = {'controller.test': {'states': {
            'default': {'transitions': [{'strike': 'variable.attack_time > 0'}]},
            'strike': {'animations': ['attack'], 'transitions': [{'default': 'variable.attack_time <= 0'}]}}}}
        self.clips = {'animation.test': {'bones': {'body': {}}}}
        self.behavior = {'components': {'minecraft:behavior.melee_box_attack': {}}}

    def problems(self):
        return audit_entity(self.desc, self.behavior, self.ctrl, self.clips, {'body'})

    def test_engine_binding_requires_melee_goal(self):
        self.assertEqual(self.problems(), [])
        self.behavior = {'components': {'minecraft:behavior.ranged_attack': {}}}
        self.assertTrue(any('undriven gate variable.attack_time' in p for p in self.problems()))

    def test_reaction_component_group_can_supply_melee(self):
        self.behavior = {'component_groups': {'fc:reaction_attack': self.behavior['components']}}
        self.assertEqual(self.problems(), [])

    def test_missing_gate_fails_before_assignment_then_passes(self):
        self.ctrl['controller.test']['states']['default']['transitions'] = [{'strike': 'v.ready > 0'}]
        self.assertTrue(any('variable.ready' in p for p in self.problems()))
        self.desc['scripts']['pre_animation'] = ['variable.ready = query.is_on_ground;']
        self.assertEqual(self.problems(), [])

    def test_other_entity_and_unreachable_state_do_not_supply_driver(self):
        self.ctrl['controller.test']['states']['default']['transitions'] = [{'strike': 'v.missing > 0'}]
        self.ctrl['controller.test']['states']['unreachable'] = {'on_entry': ['v.missing = 1;']}
        other = copy.deepcopy(self.desc)
        other['scripts']['pre_animation'] = ['v.missing = query.life_time;']
        self.assertEqual(audit_entity(other, self.behavior, self.ctrl, self.clips, {'body'}), [])
        self.assertTrue(any('variable.missing' in p for p in self.problems()))

    def test_alias_dependencies_must_resolve(self):
        self.ctrl['controller.test']['states']['default']['transitions'] = [{'strike': 'v.alias > 0'}]
        self.desc['scripts']['pre_animation'] = ['v.alias = v.missing;']
        self.assertTrue(self.problems())
        self.desc['scripts']['pre_animation'] += ['v.missing = query.life_time;']
        self.assertEqual(self.problems(), [])

    def test_constant_override_cannot_replace_engine_swing(self):
        self.desc['scripts']['initialize'] = ['v.attack_time = 0;']
        self.assertTrue(self.problems())

    def test_conditional_animation_gate_and_cycle(self):
        self.desc['scripts']['animate'] = [{'ctrl': 'v.missing > 0'}]
        self.assertTrue(self.problems())
        self.desc['scripts']['initialize'] = ['v.missing = 1;']
        self.assertEqual(self.problems(), [])
        self.ctrl['controller.test']['states']['strike']['animations'] = ['ctrl']
        self.assertTrue(any('cycle' in p for p in self.problems()))

    def test_missing_bone_clip_and_controller(self):
        self.clips['animation.test']['bones']['nonexistent'] = {}
        self.assertTrue(any('absent bones' in p for p in self.problems()))
        self.clips.clear()
        self.assertTrue(any('missing clip' in p for p in self.problems()))
        self.ctrl.clear()
        self.assertTrue(any('missing controller' in p for p in self.problems()))

    def test_invalid_attack_query_is_rejected(self):
        self.ctrl['controller.test']['states']['default']['transitions'] = [{'strike': 'query.attack_time > 0'}]
        self.assertTrue(any('invalid query.attack_time' in p for p in self.problems()))

    def test_cli_returns_nonzero_for_broken_isolated_tree(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            def put(relative, data):
                path = root / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(json.dumps(data))
            put('packs/Fablecraft_RP/entity/test.entity.json', {'minecraft:client_entity': {'description': self.desc}})
            put('packs/Fablecraft_RP/animation_controllers/test.json', {'animation_controllers': self.ctrl})
            put('packs/Fablecraft_RP/animations/test.json', {'animations': self.clips})
            # No BP melee goal and no geometry: real CLI must exit 1, not print-only.
            result = subprocess.run([sys.executable, str(ROOT / 'scripts/_audit_anims.py'), '--root', tmp], capture_output=True, text=True)
            self.assertEqual(result.returncode, 1)
            self.assertIn('undriven gate variable.attack_time', result.stdout)


if __name__ == '__main__':
    unittest.main(verbosity=2)

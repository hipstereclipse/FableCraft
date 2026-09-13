"""GP19 native transitions, including destructive shared-component removal.

This exercises actual emitted events. It does not simulate native pathfinding,
target caching, tag persistence or physical movement; those remain engine work.
"""
from copy import deepcopy
import importlib.util
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from fc_mobs import MOBS

source = Path(os.environ.get("FC_BEHAVIOR_SOURCE", ROOT / "scripts/gen_behavior.py"))
spec = importlib.util.spec_from_file_location("activity_behavior_under_test", source)
gb = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gb)

OWNED = "fc_guild_activity_owned_v1"
WAIT = "fc_guild_activity_wait_v1"
DEFENDING = "fc_guild_defending"
ROAM_KEYS = ("minecraft:movement", "minecraft:pushable", "minecraft:knockback_resistance")
FOLLOW = "minecraft:behavior.follow_mob"
TARGET = "minecraft:behavior.nearest_attackable_target"
ACTIVITIES = ("fc:guild_activity_follow_range", "fc:guild_activity_follow_hall", "fc:guild_activity_wait")
SOCIAL = ("fc:react_follow", "fc:react_watch", "fc:react_flee", "fc:react_attack", "fc:react_neutral")


def matches(rule, self_tags=(), other_tags=(), other_family=()):
    if "all_of" in rule:
        return all(matches(r, self_tags, other_tags, other_family) for r in rule["all_of"])
    if "any_of" in rule:
        return any(matches(r, self_tags, other_tags, other_family) for r in rule["any_of"])
    if "none_of" in rule:
        return not any(matches(r, self_tags, other_tags, other_family) for r in rule["none_of"])
    if rule["test"] == "has_tag":
        result = rule["value"] in (self_tags if rule.get("subject", "self") == "self" else other_tags)
    elif rule["test"] == "is_family" and rule.get("subject") == "other":
        result = rule["value"] in other_family
    else:
        raise AssertionError(f"Unsupported test in native fixture: {rule}")
    operator = rule.get("operator", "equals")
    if operator in ("not", "!=", "not_equals"):
        return not result
    if operator not in ("equals", "=="):
        raise AssertionError(f"Unsupported operator in native fixture: {operator}")
    return result


class NativeState:
    """Removing an active group deletes its keys, even if another supplied them."""
    def __init__(self, data):
        self.data = deepcopy(data)
        self.live = deepcopy(data["components"])
        self.active = set()
        self.tags = set()

    def apply(self, action):
        if isinstance(action, str):
            action = self.data["events"][action]
        if "filters" in action and not matches(action["filters"], self.tags):
            return
        for part in action.get("sequence", []):
            self.apply(part)
        for name in action.get("remove", {}).get("component_groups", []):
            if name in self.active:
                for key in self.data["component_groups"][name]:
                    self.live.pop(key, None)
                self.active.remove(name)
        for name in action.get("add", {}).get("component_groups", []):
            self.active.add(name)
            self.live.update(deepcopy(self.data["component_groups"][name]))


class GuildActivityBehavior(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.outputs = {}
        with tempfile.TemporaryDirectory() as directory, patch.object(gb, "BP", Path(directory)):
            for mob in MOBS:
                gb.emit_entity(mob)
                path = Path(directory) / "entities" / f"{mob['id']}.json"
                cls.outputs[mob["id"]] = json.loads(path.read_text())["minecraft:entity"]
        cls.skill = cls.outputs["guild_apprentice_skill"]

    def state(self, data=None):
        return NativeState(self.skill if data is None else data)

    def assert_roaming(self, state):
        for key in ROAM_KEYS:
            self.assertEqual(state.live.get(key), state.data["components"][key], key)

    def wait(self, state):
        state.tags.update((OWNED, WAIT))
        state.apply("fc:guild_activity_wait")
        self.assertEqual(state.live["minecraft:movement"], {"value": 0.0})

    def assert_scoped_filters(self, data):
        for slot in ("range", "hall"):
            goal = data["component_groups"][f"fc:guild_activity_follow_{slot}"][FOLLOW]
            self.assertEqual(goal["filters"], {"all_of": [
                {"test": "is_family", "subject": "other", "value": "player"},
                {"test": "has_tag", "subject": "other", "value": f"fc_skill_{slot}_requester_v1"},
            ]})
            self.assertFalse(goal["use_home_position_restriction"])
            self.assertEqual(goal["priority"], 1)

    def test_only_skill_gets_owned_groups_without_taming_or_position_changes(self):
        for eid, data in self.outputs.items():
            groups = data.get("component_groups", {})
            found = [k for k in groups if k.startswith("fc:guild_activity_")]
            self.assertEqual(set(found), set(ACTIVITIES) if eid == "guild_apprentice_skill" else set())
            if eid == "guild_apprentice_skill":
                for name in (*ACTIVITIES, "fc:guild_activity_stop"):
                    self.assertIn(name, data["events"])
        for group in ACTIVITIES:
            self.assertEqual(set(self.skill["component_groups"][group]),
                             {"minecraft:movement"} if group.endswith("_wait") else {FOLLOW})

    def test_each_follow_channel_admits_only_its_tagged_other_player(self):
        self.assert_scoped_filters(self.skill)
        for slot, wrong in (("range", "hall"), ("hall", "range")):
            rule = self.skill["component_groups"][f"fc:guild_activity_follow_{slot}"][FOLLOW]["filters"]
            tag = f"fc_skill_{slot}_requester_v1"
            self.assertTrue(matches(rule, (), (tag,), ("player",)))
            self.assertFalse(matches(rule, (), (), ("player",)))
            self.assertFalse(matches(rule, (tag,), (), ("player",)))
            self.assertFalse(matches(rule, (), (f"fc_skill_{wrong}_requester_v1",), ("player",)))
            self.assertFalse(matches(rule, (), (tag,), ("fc_friendly",)))

    def test_wait_removes_training_and_social_goals_and_stop_restores_canonical_motion(self):
        for legacy in ("fc:guild_training_start", *SOCIAL):
            state = self.state()
            state.apply(legacy)
            self.wait(state)
            self.assertNotIn("fc:guild_training", state.active)
            for key in (FOLLOW, "minecraft:behavior.avoid_mob_type", TARGET):
                self.assertNotIn(key, state.live)
            for key in ("minecraft:physics", "minecraft:pushable", "minecraft:knockback_resistance"):
                self.assertEqual(state.live[key], self.skill["components"][key])
            # Failed tag cleanup must not prevent native stop from restoring.
            state.apply("fc:guild_activity_stop")
            state.apply("fc:guild_activity_stop")
            self.assert_roaming(state)
            self.assertTrue(set(ACTIVITIES).isdisjoint(state.active))

    def test_redundant_training_cleanup_and_direct_social_events_do_not_release_wait(self):
        state = self.state()
        self.wait(state)
        for event in ("fc:guild_training_stop", "fc:guild_training_stop", "fc:guild_training_start", *SOCIAL):
            state.apply(event)
            self.assertEqual(state.live["minecraft:movement"], {"value": 0.0}, event)
            self.assertNotIn("fc:guild_training", state.active)
            self.assertNotIn(FOLLOW, state.live)

    def test_follow_wait_channel_switch_and_stop_never_fall_back_to_generic_players(self):
        state = self.state()
        self.wait(state)
        state.tags.remove(WAIT)
        for slot in ("range", "hall", "range"):
            state.apply(f"fc:guild_activity_follow_{slot}")
            self.assert_roaming(state)
            self.assertEqual(state.live[FOLLOW], self.skill["component_groups"][f"fc:guild_activity_follow_{slot}"][FOLLOW])
            self.assertEqual(set(ACTIVITIES) & state.active, {f"fc:guild_activity_follow_{slot}"})
            for event in ("fc:guild_training_stop", *SOCIAL):
                state.apply(event)
                self.assertEqual(state.live[FOLLOW], self.skill["component_groups"][f"fc:guild_activity_follow_{slot}"][FOLLOW])
        state.apply("fc:guild_activity_stop")
        self.assertNotIn(FOLLOW, state.live)
        self.assert_roaming(state)

    def test_defence_preempts_wait_or_follow_even_with_stale_markers(self):
        for mode in ("wait", "follow_range", "follow_hall"):
            state = self.state()
            state.tags.add(OWNED)
            if mode == "wait":
                state.tags.add(WAIT)
            state.apply(f"fc:guild_activity_{mode}")
            state.tags.add(DEFENDING)
            state.apply("fc:guild_defence_start")
            for event in ("fc:guild_training_stop", "fc:guild_training_start", *SOCIAL, "fc:guild_activity_stop"):
                state.apply(event)
                self.assert_roaming(state)
                self.assertNotIn(FOLLOW, state.live)
                self.assertTrue(set(ACTIVITIES).isdisjoint(state.active))
                self.assertEqual(state.live[TARGET], self.skill["component_groups"]["fc:guild_defence"][TARGET])
            state.tags.difference_update((OWNED, WAIT, DEFENDING))
            state.apply("fc:guild_defence_stop")
            state.apply("fc:guild_training_stop")
            self.assert_roaming(state)
            self.assertNotIn(TARGET, state.live)

    def test_native_activation_requires_consistent_derived_markers_and_no_defence(self):
        for mode in ("wait", "follow_range", "follow_hall"):
            invalid = (set(), {WAIT}, {OWNED, WAIT, DEFENDING}, {OWNED, DEFENDING})
            invalid += ({OWNED},) if mode == "wait" else ({OWNED, WAIT},)
            for tags in invalid:
                state = self.state()
                state.tags.update(tags)
                before = deepcopy(state.live)
                state.apply(f"fc:guild_activity_{mode}")
                self.assertEqual(state.live, before, (mode, tags))
                self.assertTrue(set(ACTIVITIES).isdisjoint(state.active))

    def test_broadened_filters_and_broken_shared_key_restoration_are_detected(self):
        broken = deepcopy(self.skill)
        broken["component_groups"][ACTIVITIES[0]][FOLLOW]["filters"] = {"test": "is_family", "subject": "other", "value": "player"}
        with self.assertRaises(AssertionError):
            self.assert_scoped_filters(broken)
        for mutation in ("stop_restore", "training_wait", "defence_restore", "social_guard"):
            data = deepcopy(self.skill)
            if mutation == "stop_restore":
                data["events"]["fc:guild_activity_stop"]["sequence"][0].pop("add")
            elif mutation == "training_wait":
                data["events"]["fc:guild_training_stop"]["sequence"].pop()
            elif mutation == "defence_restore":
                data["events"]["fc:guild_defence_start"]["sequence"].pop(0)
            else:
                data["events"]["fc:react_follow"]["sequence"][0].pop("filters")
            state = self.state(data)
            self.wait(state)
            with self.assertRaises(AssertionError, msg=mutation):
                if mutation == "stop_restore":
                    state.apply("fc:guild_activity_stop")
                    self.assert_roaming(state)
                elif mutation == "training_wait":
                    state.apply("fc:guild_training_stop")
                    self.assertEqual(state.live["minecraft:movement"], {"value": 0.0})
                elif mutation == "defence_restore":
                    state.tags.add(DEFENDING)
                    state.apply("fc:guild_defence_start")
                    self.assert_roaming(state)
                else:
                    state.apply("fc:react_follow")
                    self.assertNotIn(FOLLOW, state.live)


if __name__ == "__main__":
    unittest.main(verbosity=2)

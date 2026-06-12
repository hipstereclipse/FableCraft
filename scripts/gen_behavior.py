"""gen_behavior.py — emits the entire Behavior Pack JSON:
items, entity behaviors, loot tables, spawn rules, and the shared data
blob consumed by scripts/main.js.
"""
import json

from fc_lib import BP, NAMESPACE, write_json, write_text
import fc_data
from fc_mobs import MOBS

FV_ITEM = "1.21.30"
FV_ENT = "1.21.0"
FV_SPAWN = "1.8.0"


# ---------------------------------------------------------------------------
# ITEMS
# ---------------------------------------------------------------------------

def lore_lines(item):
    lines = []
    if item["cat"] in ("melee", "ranged"):
        lines.append(f"§7Damage: §c{item['fable_damage']}§7 (Fable)")
        if item.get("slots", 0) > 0:
            lines.append(f"§7Augment slots: §b{item['slots']}")
        if item.get("augments"):
            lines.append("§6Augmented: §e" + ", ".join(a.title() for a in item["augments"]))
        if item.get("two_handed"):
            lines.append("§8Two-handed")
        if item.get("lore"):
            lines.append(f"§o§9{item['lore']}")
    elif item["cat"] == "armor":
        lines.append(f"§7Set: §f{fc_data_set_name(item)}")
        if item.get("attract"):
            lines.append(f"§dAttractiveness +{item['attract']}")
        if item.get("scary"):
            lines.append(f"§4Scariness +{item['scary']}")
        if item.get("align", 0) > 0:
            lines.append("§eGood-aligned")
        elif item.get("align", 0) < 0:
            lines.append("§5Evil-aligned")
    elif item["cat"] == "spell":
        lines.append("§bUse to equip this Will power.")
        lines.append(f"§o§9{item.get('desc','')}")
    elif item.get("desc"):
        lines.append(f"§o§9{item['desc']}")
    return lines


def fc_data_set_name(item):
    for s in fc_data.ARMOR_SETS + fc_data.HATS:
        if s["id"] == item.get("set"):
            return s["name"]
    return item.get("set", "?")


def emit_weapon(item):
    iid = item["id"]
    comp = {
        "minecraft:icon": iid,
        "minecraft:display_name": {"value": f"§f{item['name']}"},
        "minecraft:max_stack_size": 1,
        "minecraft:hand_equipped": True,
        "minecraft:damage": item["damage"],
        "minecraft:durability": {"max_durability": item["durability"]},
        "minecraft:repairable": {
            "repair_items": [{"items": ["minecraft:iron_ingot"], "repair_amount": item["durability"] // 4}]
        },
        "minecraft:enchantable": {"slot": "sword", "value": 10},
        "minecraft:tags": {"tags": [f"fc:weapon", f"fc:{item['cat']}",
                                    f"fc:slots_{item.get('slots',0)}"]},
    }
    if item["cat"] == "ranged":
        comp["minecraft:enchantable"] = {"slot": "bow", "value": 10}
        comp["minecraft:shooter"] = {
            "ammunition": [{"item": "minecraft:arrow",
                            "use_offhand": True,
                            "search_inventory": True,
                            "use_in_creative": True}],
            "max_draw_duration": 1.0 if item["wtype"] != "crossbow" else 1.4,
            "scale_power_by_draw_duration": True,
            "charge_on_draw": False,
        }
        comp["minecraft:use_modifiers"] = {"use_duration": 3.0, "movement_modifier": 0.55}
    data = {
        "format_version": FV_ITEM,
        "minecraft:item": {
            "description": {
                "identifier": f"{NAMESPACE}:{iid}",
                "menu_category": {"category": "equipment", "group": "itemGroup.name.sword"},
            },
            "components": comp,
        },
    }
    write_json(BP / "items" / f"{iid}.json", data)


def emit_armor(item):
    iid = item["id"]
    slot_map = {"helm": ("armorGroup.name.helmet", "slot.armor.head"),
                "torso": ("armorGroup.name.chestplate", "slot.armor.chest"),
                "legs": ("armorGroup.name.leggings", "slot.armor.legs"),
                "boots": ("armorGroup.name.boots", "slot.armor.feet")}
    group, slot = slot_map[item["slot"]]
    comp = {
        "minecraft:icon": iid,
        "minecraft:display_name": {"value": f"§f{item['name']}"},
        "minecraft:max_stack_size": 1,
        "minecraft:wearable": {"slot": slot, "protection": item["protection"]},
        "minecraft:durability": {"max_durability": item["durability"]},
        "minecraft:repairable": {
            "repair_items": [{"items": ["minecraft:leather", "minecraft:iron_ingot"],
                              "repair_amount": item["durability"] // 4}]
        },
        "minecraft:enchantable": {"slot": "armor_" + ("head" if item["slot"] == "helm" else
                                                       "torso" if item["slot"] == "torso" else
                                                       "legs" if item["slot"] == "legs" else "feet"),
                                  "value": 10},
        "minecraft:tags": {"tags": ["fc:armor", f"fc:set_{item['set']}",
                                    f"fc:align_{item.get('align',0)}"]},
    }
    data = {
        "format_version": FV_ITEM,
        "minecraft:item": {
            "description": {
                "identifier": f"{NAMESPACE}:{iid}",
                "menu_category": {"category": "equipment"},
            },
            "components": comp,
        },
    }
    write_json(BP / "items" / f"{iid}.json", data)


def emit_consumable(item):
    iid = item["id"]
    comp = {
        "minecraft:icon": iid,
        "minecraft:display_name": {"value": f"§f{item['name']}"},
        "minecraft:max_stack_size": item.get("stack", 16),
        "minecraft:use_modifiers": {"use_duration": 1.2, "movement_modifier": 0.6},
        "minecraft:food": {"nutrition": item.get("food", 0), "saturation_modifier": 0.6,
                           "can_always_eat": True},
        "minecraft:use_animation": "drink" if "potion" in iid or "phial" in item["kind"] or "elixir" in iid else "eat",
        "minecraft:tags": {"tags": ["fc:consumable"]},
    }
    data = {
        "format_version": FV_ITEM,
        "minecraft:item": {
            "description": {
                "identifier": f"{NAMESPACE}:{iid}",
                "menu_category": {"category": "equipment", "group": "itemGroup.name.potion"},
            },
            "components": comp,
        },
    }
    write_json(BP / "items" / f"{iid}.json", data)


def emit_simple(item, category="items"):
    iid = item["id"]
    comp = {
        "minecraft:icon": iid,
        "minecraft:display_name": {"value": f"§f{item['name']}"},
        "minecraft:max_stack_size": item.get("stack", 64),
        "minecraft:tags": {"tags": [f"fc:{item['cat']}"]},
    }
    if item["cat"] == "spell":
        comp["minecraft:max_stack_size"] = 1
        comp["minecraft:foil"] = True
    if item["id"] in ("septimal_key", "guild_seal", "jack_of_blades_mask"):
        comp["minecraft:foil"] = True
    data = {
        "format_version": FV_ITEM,
        "minecraft:item": {
            "description": {
                "identifier": f"{NAMESPACE}:{iid}",
                "menu_category": {"category": "items"},
            },
            "components": comp,
        },
    }
    write_json(BP / "items" / f"{iid}.json", data)


# ---------------------------------------------------------------------------
# LOOT TABLES
# ---------------------------------------------------------------------------

def emit_loot(mob):
    pools = []
    for item, lo, hi, chance in mob.get("drops", []):
        entry = {"type": "item", "name": item, "weight": 1}
        functions = []
        if hi > 1 or lo != 1:
            functions.append({"function": "set_count", "count": {"min": lo, "max": hi}})
        if functions:
            entry["functions"] = functions
        pool = {"rolls": 1, "entries": [entry]}
        if chance < 1.0:
            pool["conditions"] = [{"condition": "random_chance", "chance": chance}]
        pools.append(pool)
    write_json(BP / "loot_tables" / "entities" / f"{mob['id']}.json", {"pools": pools})


# ---------------------------------------------------------------------------
# ENTITIES
# ---------------------------------------------------------------------------

def base_components(mob):
    c = {
        "minecraft:type_family": {"family": mob["family"]},
        "minecraft:health": {"value": mob["hp"], "max": mob["hp"]},
        "minecraft:movement": {"value": mob["speed"]},
        "minecraft:collision_box": {"width": 0.7 * mob.get("scale", 1.0),
                                    "height": 1.9 * mob.get("scale", 1.0)},
        "minecraft:loot": {"table": f"loot_tables/entities/{mob['id']}.json"},
        "minecraft:physics": {},
        "minecraft:pushable": {"is_pushable": True, "is_pushable_by_piston": True},
        "minecraft:jump.static": {},
        "minecraft:movement.basic": {},
        "minecraft:navigation.walk": {"can_path_over_water": True, "avoid_water": True,
                                      "can_walk": True},
        "minecraft:knockback_resistance": {"value": 0.2 if mob["hp"] > 100 else 0.0},
        "minecraft:nameable": {},
        "minecraft:leashable": {},
        "minecraft:despawn": {"despawn_from_distance": {}},
    }
    if mob.get("dmg"):
        c["minecraft:attack"] = {"damage": mob["dmg"]}
    return c


def melee_behaviors(mob, target_players=True):
    targets = []
    if target_players:
        targets.append({"filters": {"test": "is_family", "subject": "other", "value": "player"},
                        "max_dist": 28})
    targets.append({"filters": {"test": "is_family", "subject": "other", "value": "fc_ally"},
                    "max_dist": 20})
    targets.append({"filters": {"test": "is_family", "subject": "other", "value": "fc_guard"},
                    "max_dist": 20})
    return {
        "minecraft:behavior.melee_box_attack": {"priority": 3, "speed_multiplier": 1.25,
                                                "track_target": True},
        "minecraft:behavior.nearest_attackable_target": {
            "priority": 2, "must_see": True, "reselect_targets": True,
            "within_radius": 28.0, "entity_types": targets},
        "minecraft:behavior.hurt_by_target": {"priority": 1},
        "minecraft:behavior.random_stroll": {"priority": 6, "speed_multiplier": 0.8},
        "minecraft:behavior.random_look_around": {"priority": 7},
        "minecraft:behavior.look_at_player": {"priority": 8, "look_distance": 8.0},
    }


def emit_entity(mob):
    eid = mob["id"]
    behavior = mob["behavior"]
    comp = base_components(mob)
    events = {}
    cgroups = {}

    if behavior in ("melee", "boss_melee"):
        comp.update(melee_behaviors(mob))
        if mob.get("leap"):
            comp["minecraft:behavior.leap_at_target"] = {"priority": 4, "yd": 0.5,
                                                          "must_be_on_ground": True}
        if mob.get("poison"):
            comp["minecraft:attack"] = {"damage": mob["dmg"], "effect_name": "poison",
                                        "effect_duration": 5}
        if mob.get("knockback"):
            comp["minecraft:behavior.knockback_roar"] = {
                "priority": 4, "duration": 1.0, "attack_time": 0.5,
                "knockback_strength": 3, "knockback_range": 4,
                "cooldown_time": 8.0, "damage_filters": {"test": "is_family", "subject": "other", "value": "player"}}
    elif behavior == "ranged":
        comp["minecraft:behavior.ranged_attack"] = {
            "priority": 3, "attack_interval_min": 1.6, "attack_interval_max": 3.2,
            "attack_radius": 14.0}
        comp["minecraft:shooter"] = {"def": "minecraft:arrow"}
        comp.update({k: v for k, v in melee_behaviors(mob).items()
                     if "melee_box_attack" not in k})
    elif behavior == "caster":
        comp["minecraft:behavior.ranged_attack"] = {
            "priority": 3, "attack_interval_min": 2.4, "attack_interval_max": 4.0,
            "attack_radius": 12.0}
        comp["minecraft:shooter"] = {"def": "minecraft:small_fireball"}
        comp.update({k: v for k, v in melee_behaviors(mob).items()
                     if "melee_box_attack" not in k})
    elif behavior in ("flying", "flying_boss", "ally_flying"):
        comp.pop("minecraft:navigation.walk", None)
        comp.pop("minecraft:jump.static", None)
        comp.pop("minecraft:movement.basic", None)
        comp["minecraft:navigation.hover"] = {
            "can_path_over_water": True, "can_sink": False, "can_pass_doors": True,
            "can_fly": True}
        comp["minecraft:movement.hover"] = {}
        comp["minecraft:flying_speed"] = {"value": mob["speed"] * 0.45}
        comp["minecraft:can_fly"] = {}
        comp["minecraft:behavior.float_wander"] = {"priority": 6, "xz_dist": 12,
                                                    "y_dist": 5, "y_offset": 2.0}
        if "ally" not in behavior:
            comp.update({k: v for k, v in melee_behaviors(mob).items()
                         if k in ("minecraft:behavior.nearest_attackable_target",
                                  "minecraft:behavior.hurt_by_target")})
            comp["minecraft:behavior.melee_box_attack"] = {"priority": 3,
                                                           "speed_multiplier": 1.4,
                                                           "track_target": True}
    elif behavior == "ghost":
        comp.update(melee_behaviors(mob))
        comp["minecraft:fire_immune"] = {}
        comp["minecraft:float"] = {}
    elif behavior == "guard":
        comp["minecraft:behavior.nearest_attackable_target"] = {
            "priority": 2, "must_see": True, "within_radius": 20.0,
            "entity_types": [{"filters": {"test": "is_family", "subject": "other", "value": "monster"},
                              "max_dist": 20}]}
        comp["minecraft:behavior.melee_box_attack"] = {"priority": 3, "speed_multiplier": 1.2,
                                                       "track_target": True}
        comp["minecraft:behavior.hurt_by_target"] = {"priority": 1}
        comp["minecraft:behavior.random_stroll"] = {"priority": 6, "speed_multiplier": 0.7}
        comp["minecraft:behavior.look_at_player"] = {"priority": 8, "look_distance": 8.0}
        # faction system: guards turn on infamous players (driven by main.js)
        cgroups["fc:hostile"] = {
            "minecraft:behavior.nearest_attackable_target": {
                "priority": 1, "must_see": False, "reselect_targets": True,
                "within_radius": 24.0,
                "entity_types": [
                    {"filters": {"test": "is_family", "subject": "other", "value": "player"},
                     "max_dist": 24},
                    {"filters": {"test": "is_family", "subject": "other", "value": "monster"},
                     "max_dist": 20}]},
        }
        events["fc:turn_hostile"] = {"add": {"component_groups": ["fc:hostile"]}}
        events["fc:calm"] = {"remove": {"component_groups": ["fc:hostile"]}}
    elif behavior in ("ally",):
        comp["minecraft:behavior.nearest_attackable_target"] = {
            "priority": 2, "must_see": True, "within_radius": 18.0,
            "entity_types": [{"filters": {"test": "is_family", "subject": "other", "value": "monster"},
                              "max_dist": 18}]}
        comp["minecraft:behavior.melee_box_attack"] = {"priority": 3, "speed_multiplier": 1.25,
                                                       "track_target": True}
        comp["minecraft:behavior.hurt_by_target"] = {"priority": 1}
        comp["minecraft:behavior.follow_owner"] = {"priority": 4, "speed_multiplier": 1.1,
                                                   "start_distance": 8, "stop_distance": 3}
        comp["minecraft:is_tamed"] = {}
        comp["minecraft:behavior.random_stroll"] = {"priority": 6}
    elif behavior == "npc":
        comp["minecraft:behavior.random_stroll"] = {"priority": 6, "speed_multiplier": 0.6}
        comp["minecraft:behavior.look_at_player"] = {"priority": 7, "look_distance": 10.0,
                                                     "probability": 0.9}
        comp["minecraft:behavior.random_look_around"] = {"priority": 8}
        comp["minecraft:damage_sensor"] = {"triggers": [
            {"cause": "all", "deals_damage": True}]}
    elif behavior == "door":
        comp.pop("minecraft:behavior.random_stroll", None)
        comp.pop("minecraft:despawn", None)
        comp["minecraft:movement"] = {"value": 0.0}
        comp["minecraft:variant"] = {"value": 0}
        comp["minecraft:knockback_resistance"] = {"value": 1.0}
        comp["minecraft:damage_sensor"] = {"triggers": [
            {"cause": "all", "deals_damage": False}]}
        comp["minecraft:fire_immune"] = {}
        comp["minecraft:persistent"] = {}
        comp["minecraft:is_stackable"] = {}
        comp["minecraft:body_rotation_blocked"] = {}
        cgroups["fc:door_open"] = {"minecraft:variant": {"value": 1}}
        events["fc:open"] = {"add": {"component_groups": ["fc:door_open"]}}

    if mob.get("despawn"):
        comp["minecraft:timer"] = {"looping": False, "time": mob["despawn"] / 20.0,
                                   "time_down_event": {"event": "fc:expire"}}
        events["fc:expire"] = {"add": {"component_groups": ["fc:despawn_now"]}}
        cgroups["fc:despawn_now"] = {"minecraft:instant_despawn": {}}

    if mob.get("fire"):
        comp["minecraft:fire_immune"] = {}

    if behavior in ("npc", "guard", "door"):
        comp["minecraft:persistent"] = {}

    desc = {
        "identifier": f"{NAMESPACE}:{eid}",
        "is_spawnable": True,
        "is_summonable": True,
    }
    spawn_cat = "monster" if "monster" in mob["family"] else "creature"
    desc["spawn_category"] = spawn_cat

    data = {
        "format_version": FV_ENT,
        "minecraft:entity": {
            "description": desc,
            "component_groups": cgroups,
            "components": comp,
            "events": events,
        },
    }
    if not cgroups:
        data["minecraft:entity"].pop("component_groups")
    if not events:
        data["minecraft:entity"].pop("events")
    write_json(BP / "entities" / f"{eid}.json", data)


# ---------------------------------------------------------------------------
# SPAWN RULES
# ---------------------------------------------------------------------------

BIOME_TAGS = {
    "forest": ["forest"], "taiga": ["taiga"], "roofed": ["roofed"],
    "plains": ["plains"], "savanna": ["savanna"], "mesa": ["mesa"],
    "extreme_hills": ["extreme_hills"], "swamp": ["swamp"],
    "frozen": ["frozen"], "caves": ["monster"], "flower": ["flower_forest"],
    "jungle": ["jungle"],
}


def emit_spawn_rules(mob):
    sp = mob.get("spawn")
    if not sp:
        return
    conditions = []
    for biome in sp["biomes"]:
        cond = {
            "minecraft:spawns_on_surface": {},
            "minecraft:weight": {"default": sp["weight"]},
            "minecraft:herd": {"min_size": sp["herd"][0], "max_size": sp["herd"][1]},
            "minecraft:biome_filter": {"test": "has_biome_tag", "operator": "==",
                                       "value": BIOME_TAGS.get(biome, [biome])[0]},
            "minecraft:density_limit": {"surface": 4},
        }
        if sp.get("night"):
            cond["minecraft:brightness_filter"] = {"min": 0, "max": 7,
                                                   "adjust_for_weather": True}
        else:
            cond["minecraft:brightness_filter"] = {"min": 8, "max": 15,
                                                   "adjust_for_weather": False}
        conditions.append(cond)
    data = {
        "format_version": FV_SPAWN,
        "minecraft:spawn_rules": {
            "description": {
                "identifier": f"{NAMESPACE}:{mob['id']}",
                "population_control": "monster" if "monster" in mob["family"] else "animal",
            },
            "conditions": conditions,
        },
    }
    write_json(BP / "spawn_rules" / f"{mob['id']}.json", data)


# ---------------------------------------------------------------------------
# Shared gameplay data for main.js
# ---------------------------------------------------------------------------

def emit_script_data():
    items = fc_data.all_items()
    weapons = {f"{NAMESPACE}:{i['id']}": {
        "fable": i["fable_damage"], "slots": i.get("slots", 0),
        "augments": i.get("augments", []), "cat": i["cat"],
    } for i in items if i["cat"] in ("melee", "ranged")}
    armor = {f"{NAMESPACE}:{i['id']}": {
        "align": i.get("align", 0), "attract": i.get("attract", 0),
        "scary": i.get("scary", 0), "set": i["set"], "slot": i["slot"],
    } for i in items if i["cat"] == "armor"}
    consum = {f"{NAMESPACE}:{i['id']}": {
        "heal": i.get("heal", 0), "will": i.get("will", 0),
        "food": i.get("food", 0), "morality": i.get("morality", 0),
        "xp": i.get("xp"), "xp_amount": i.get("xp_amount", 0),
        "max_hp": i.get("max_hp", 0),
        "phial": i["id"] == "resurrection_phial",
    } for i in items if i["cat"] == "consumable"}
    spells = {s["id"]: {k: s[k] for k in ("name", "will", "cd", "align", "desc")}
              for s in fc_data.SPELLS}
    data = {
        "weapons": weapons,
        "armor": armor,
        "consumables": consum,
        "spells": spells,
        "upgrades": {u["id"]: u for u in fc_data.UPGRADES},
        "quests": fc_data.QUESTS,
        "demonDoors": fc_data.DEMON_DOORS,
        "killXp": fc_data.KILL_XP,
        "killMorality": fc_data.KILL_MORALITY,
        "augments": {f"{NAMESPACE}:{a['id']}": a["id"].replace("_augment", "")
                     for a in fc_data.AUGMENTS if a["id"] != "augment_remover"},
    }
    write_text(BP / "scripts" / "fc_gamedata.js",
               "// AUTO-GENERATED by gen_behavior.py — do not edit.\n"
               "export const DATA = " + json.dumps(data, indent=1) + ";\n")


# ---------------------------------------------------------------------------
# RECIPES + AZURITE ORE BLOCK
# ---------------------------------------------------------------------------

def emit_recipes():
    recipes = fc_data.build_recipes()
    for rec in recipes:
        rid = rec["id"]
        if rec["type"] == "shaped":
            data = {
                "format_version": "1.20.10",
                "minecraft:recipe_shaped": {
                    "description": {"identifier": f"{NAMESPACE}:craft_{rid}"},
                    "tags": ["crafting_table"],
                    "pattern": rec["pattern"],
                    "key": {k: {"item": v} for k, v in rec["key"].items()},
                    "unlock": [{"item": rec["unlock"]}],
                    "result": {"item": rec["output"], "count": rec.get("count", 1)},
                },
            }
        elif rec["type"] == "shapeless":
            data = {
                "format_version": "1.20.10",
                "minecraft:recipe_shapeless": {
                    "description": {"identifier": f"{NAMESPACE}:craft_{rid}"},
                    "tags": ["crafting_table"],
                    "ingredients": [{"item": i} for i in rec["ingredients"]],
                    "unlock": [{"item": rec["unlock"]}],
                    "result": {"item": rec["output"], "count": rec.get("count", 1)},
                },
            }
        else:  # furnace
            data = {
                "format_version": "1.20.10",
                "minecraft:recipe_furnace": {
                    "description": {"identifier": f"{NAMESPACE}:smelt_{rid}"},
                    "tags": ["furnace", "blast_furnace"],
                    "input": rec["input"],
                    "output": rec["output"],
                },
            }
        write_json(BP / "recipes" / f"{rid}.json", data)
    return len(recipes)


def emit_azurite():
    """Mineable azurite ore: drops Will Shards; veins seed underground."""
    write_json(BP / "blocks" / "azurite_ore.json", {
        "format_version": "1.21.0",
        "minecraft:block": {
            "description": {
                "identifier": f"{NAMESPACE}:azurite_ore",
                "menu_category": {"category": "nature"},
            },
            "components": {
                "minecraft:destructible_by_mining": {"seconds_to_destroy": 4.0},
                "minecraft:destructible_by_explosion": {"explosion_resistance": 6},
                "minecraft:map_color": "#3F66B0",
                "minecraft:light_dampening": 15,
                "minecraft:geometry": "minecraft:geometry.full_block",
                "minecraft:material_instances": {
                    "*": {"texture": "fc_azurite_ore", "render_method": "opaque"}
                },
                "minecraft:loot": "loot_tables/blocks/azurite_ore.json",
            },
        },
    })
    write_json(BP / "loot_tables" / "blocks" / "azurite_ore.json", {
        "pools": [{
            "rolls": 1,
            "entries": [{
                "type": "item", "name": "fc:will_shard", "weight": 1,
                "functions": [{"function": "set_count", "count": {"min": 1, "max": 3}}],
            }],
        }],
    })
    write_json(BP / "features" / "azurite_ore_feature.json", {
        "format_version": "1.13.0",
        "minecraft:ore_feature": {
            "description": {"identifier": "fc:azurite_ore_feature"},
            "count": 7,
            "replace_rules": [
                {"places_block": "fc:azurite_ore",
                 "may_replace": ["minecraft:stone", "minecraft:deepslate",
                                 "minecraft:granite", "minecraft:diorite",
                                 "minecraft:andesite", "minecraft:tuff"]},
            ],
        },
    })
    write_json(BP / "feature_rules" / "azurite_placement.json", {
        "format_version": "1.13.0",
        "minecraft:feature_rules": {
            "description": {
                "identifier": "fc:azurite_placement",
                "places_feature": "fc:azurite_ore_feature",
            },
            "conditions": {
                "placement_pass": "underground_pass",
                "minecraft:biome_filter": [
                    {"test": "has_biome_tag", "operator": "==", "value": "overworld"},
                ],
            },
            "distribution": {
                "iterations": 9,
                "coordinate_eval_order": "zyx",
                "x": {"distribution": "uniform", "extent": [0, 16]},
                "z": {"distribution": "uniform", "extent": [0, 16]},
                "y": {"distribution": "uniform", "extent": [4, 54]},
            },
        },
    })


def main():
    items = fc_data.all_items()
    for item in items:
        cat = item["cat"]
        if cat in ("melee", "ranged"):
            emit_weapon(item)
        elif cat == "armor":
            emit_armor(item)
        elif cat == "consumable":
            emit_consumable(item)
        else:
            emit_simple(item)
    for mob in MOBS:
        emit_entity(mob)
        emit_loot(mob)
        emit_spawn_rules(mob)
    emit_script_data()
    n_rec = emit_recipes()
    emit_azurite()
    print(f"emitted {len(items)} items, {len(MOBS)} entities + loot + spawn rules, "
          f"{n_rec} recipes, azurite ore (block+feature)")


if __name__ == "__main__":
    main()

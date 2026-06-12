"""gen_resources.py — emits the Resource Pack:
geometry (from fc_mobs cube data), client entities, animations,
render controllers, item_texture.json, attachables for held weapons,
terrain/blocks pass-through, lang files, and sound definitions JSON.
"""
import json

from fc_lib import RP, NAMESPACE, write_json, write_text
import fc_data
from fc_mobs import MOBS, build_parts, mob_palette, pack_uvs

FV_GEO = "1.12.0"
FV_CE = "1.10.0"
FV_ANIM = "1.8.0"
FV_RC = "1.10.0"
FV_ATTACH = "1.10.0"


# ---------------------------------------------------------------------------
# GEOMETRY
# ---------------------------------------------------------------------------

def emit_geometry(mob):
    parts = build_parts(mob)
    tw, th, uv = pack_uvs(parts)
    bones = []
    for pi, part in enumerate(parts):
        cubes = []
        for ci, cube in enumerate(part["cubes"]):
            c = {
                "origin": cube["origin"],
                "size": cube["size"],
                "uv": list(uv[(pi, ci)]),
            }
            if cube.get("inflate"):
                c["inflate"] = cube["inflate"]
            cubes.append(c)
        bone = {"name": part["name"], "pivot": part["pivot"], "cubes": cubes}
        if part.get("parent"):
            bone["parent"] = part["parent"]
        if any(part.get("rot", [0, 0, 0])):
            bone["rotation"] = part["rot"]
        bones.append(bone)
    geo = {
        "format_version": FV_GEO,
        "minecraft:geometry": [{
            "description": {
                "identifier": f"geometry.fc.{mob['id']}",
                "texture_width": tw,
                "texture_height": th,
                "visible_bounds_width": 4,
                "visible_bounds_height": 4,
                "visible_bounds_offset": [0, 1.5, 0],
            },
            "bones": bones,
        }],
    }
    write_json(RP / "models" / "entity" / f"{mob['id']}.geo.json", geo)


# ---------------------------------------------------------------------------
# ANIMATIONS (shared per body-plan archetype)
# ---------------------------------------------------------------------------

def emit_animations():
    anims = {
        "format_version": FV_ANIM,
        "animations": {
            "animation.fc.biped.walk": {
                "loop": True,
                "anim_time_update": "query.modified_distance_moved",
                "bones": {
                    "leg_r": {"rotation": ["math.cos(query.anim_time * 38) * 28 * query.modified_move_speed", 0, 0]},
                    "leg_l": {"rotation": ["-math.cos(query.anim_time * 38) * 28 * query.modified_move_speed", 0, 0]},
                    "arm_r": {"rotation": ["-math.cos(query.anim_time * 38) * 24 * query.modified_move_speed", 0, 0]},
                    "arm_l": {"rotation": ["math.cos(query.anim_time * 38) * 24 * query.modified_move_speed", 0, 0]},
                },
            },
            "animation.fc.biped.idle": {
                "loop": True,
                "bones": {
                    "arm_r": {"rotation": ["math.sin(query.life_time * 67) * 2.5", 0, 2]},
                    "arm_l": {"rotation": ["-math.sin(query.life_time * 67) * 2.5", 0, -2]},
                    "head": {"rotation": ["query.target_x_rotation", "query.target_y_rotation", 0]},
                },
            },
            "animation.fc.biped.attack": {
                "loop": True,
                "bones": {
                    "arm_r": {"rotation": ["query.attack_time > 0 ? (-110 * math.sin(query.attack_time * 180)) : 0", 0, 0]},
                },
            },
            "animation.fc.quadruped.walk": {
                "loop": True,
                "anim_time_update": "query.modified_distance_moved",
                "bones": {
                    "leg_r": {"rotation": ["math.cos(query.anim_time * 38) * 32 * query.modified_move_speed", 0, 0]},
                    "leg_l": {"rotation": ["-math.cos(query.anim_time * 38) * 32 * query.modified_move_speed", 0, 0]},
                    "arm_r": {"rotation": ["-math.cos(query.anim_time * 38) * 30 * query.modified_move_speed", 0, 0]},
                    "arm_l": {"rotation": ["math.cos(query.anim_time * 38) * 30 * query.modified_move_speed", 0, 0]},
                    "tail": {"rotation": ["math.sin(query.life_time * 150) * 8", 0, 0]},
                },
            },
            "animation.fc.fly": {
                "loop": True,
                "bones": {
                    "wing_r": {"rotation": [0, 0, "-math.sin(query.life_time * 1400) * 40 - 15"]},
                    "wing_l": {"rotation": [0, 0, "math.sin(query.life_time * 1400) * 40 + 15"]},
                    "legs": {"rotation": ["math.sin(query.life_time * 200) * 6", 0, 0]},
                },
            },
            "animation.fc.hover": {
                "loop": True,
                "bones": {
                    "body": {"position": [0, "math.sin(query.life_time * 120) * 0.6", 0]},
                },
            },
            "animation.fc.ghost.float": {
                "loop": True,
                "bones": {
                    "body": {"position": [0, "1.5 + math.sin(query.life_time * 90) * 0.8", 0]},
                    "arm_r": {"rotation": ["math.sin(query.life_time * 80) * 6 - 40", 0, 10]},
                    "arm_l": {"rotation": ["-math.sin(query.life_time * 80) * 6 - 40", 0, -10]},
                    "head": {"rotation": ["query.target_x_rotation", "query.target_y_rotation", 0]},
                },
            },
            "animation.fc.scorpion.walk": {
                "loop": True,
                "anim_time_update": "query.modified_distance_moved",
                "bones": {
                    **{f"leg_r{i}": {"rotation": [0, f"math.cos(query.anim_time * 40 + {i*90}) * 14 * query.modified_move_speed", 0]} for i in range(4)},
                    **{f"leg_l{i}": {"rotation": [0, f"-math.cos(query.anim_time * 40 + {i*90}) * 14 * query.modified_move_speed", 0]} for i in range(4)},
                    "tail": {"rotation": ["math.sin(query.life_time * 100) * 5 - 46", 0, 0]},
                    "claw_r": {"rotation": [0, "24 + math.sin(query.life_time * 130) * 8", 0]},
                    "claw_l": {"rotation": [0, "-24 - math.sin(query.life_time * 130) * 8", 0]},
                },
            },
            "animation.fc.dragon.fly": {
                "loop": True,
                "bones": {
                    "wing_r": {"rotation": [0, 0, "30 - math.sin(query.life_time * 500) * 35"]},
                    "wing_l": {"rotation": [0, 0, "-30 + math.sin(query.life_time * 500) * 35"]},
                    "tail": {"rotation": ["14 + math.sin(query.life_time * 90) * 6", 0, 0]},
                    "neck": {"rotation": ["-26 + math.sin(query.life_time * 70) * 4", 0, 0]},
                },
            },
            "animation.fc.door.idle": {
                "loop": True,
                "bones": {
                    "brow": {"position": [0, "math.sin(query.life_time * 40) * 0.3", 0]},
                    "jaw": {"rotation": ["math.sin(query.life_time * 25) * 2", 0, 0]},
                },
            },
        },
    }
    write_json(RP / "animations" / "fc_shared.animation.json", anims)


PLAN_ANIMS = {
    "humanoid": [("walk", "animation.fc.biped.walk"), ("idle", "animation.fc.biped.idle"),
                 ("attack", "animation.fc.biped.attack")],
    "hobbe": [("walk", "animation.fc.biped.walk"), ("idle", "animation.fc.biped.idle")],
    "balverine": [("walk", "animation.fc.quadruped.walk"), ("idle", "animation.fc.biped.idle")],
    "troll": [("walk", "animation.fc.biped.walk"), ("idle", "animation.fc.biped.idle")],
    "wasp": [("fly", "animation.fc.fly"), ("hover", "animation.fc.hover")],
    "beetle": [("walk", "animation.fc.scorpion.walk")],
    "wraith": [("float", "animation.fc.ghost.float")],
    "banshee": [("float", "animation.fc.ghost.float")],
    "scorpion": [("walk", "animation.fc.scorpion.walk")],
    "dragon": [("fly", "animation.fc.dragon.fly")],
    "nymph": [("fly", "animation.fc.fly"), ("hover", "animation.fc.hover")],
    "demon_door": [("idle", "animation.fc.door.idle")],
}


# ---------------------------------------------------------------------------
# CLIENT ENTITIES + RENDER CONTROLLER
# ---------------------------------------------------------------------------

def emit_render_controller():
    rc = {
        "format_version": FV_RC,
        "render_controllers": {
            "controller.render.fc_default": {
                "geometry": "Geometry.default",
                "materials": [{"*": "Material.default"}],
                "textures": ["Texture.default"],
            },
            "controller.render.fc_ghost": {
                "geometry": "Geometry.default",
                "materials": [{"*": "Material.ghost"}],
                "textures": ["Texture.default"],
                "is_hurt_color": {"r": 0.5, "g": 1.0, "b": 0.8, "a": 0.5},
            },
        },
    }
    write_json(RP / "render_controllers" / "fc.render_controllers.json", rc)


GHOST_PLANS = {"wraith", "banshee"}


def emit_client_entity(mob):
    eid = mob["id"]
    plan = mob["plan"][0]
    anims = PLAN_ANIMS.get(plan, PLAN_ANIMS["humanoid"])
    anim_map = {k: v for k, v in anims}
    scripts = {"animate": [k for k, _ in anims]}
    ghost = plan in GHOST_PLANS or eid == "oracle"
    material = "entity_alphatest"
    ce = {
        "format_version": FV_CE,
        "minecraft:client_entity": {
            "description": {
                "identifier": f"{NAMESPACE}:{eid}",
                "materials": {"default": material,
                              "ghost": "entity_alphablend"},
                "textures": {"default": f"textures/entity/{eid}"},
                "geometry": {"default": f"geometry.fc.{eid}"},
                "animations": anim_map,
                "scripts": scripts,
                "render_controllers": [
                    "controller.render.fc_ghost" if ghost else "controller.render.fc_default"],
                "spawn_egg": {"base_color": "#%02x%02x%02x" % mob_palette(mob).get(
                    list(mob_palette(mob).keys())[0], (120, 110, 100))[:3],
                    "overlay_color": "#222222"},
            },
        },
    }
    if mob.get("scale", 1.0) != 1.0:
        ce["minecraft:client_entity"]["description"]["scripts"]["scale"] = str(mob["scale"])
    write_json(RP / "entity" / f"{eid}.entity.json", ce)


# ---------------------------------------------------------------------------
# ITEM TEXTURE ATLAS + ATTACHABLES
# ---------------------------------------------------------------------------

def emit_item_atlas(items):
    tex_data = {}
    for i in items:
        tex_data[i["id"]] = {"textures": f"textures/items/{i['id']}"}
    atlas = {
        "resource_pack_name": "fablecraft",
        "texture_name": "atlas.items",
        "texture_data": tex_data,
    }
    write_json(RP / "textures" / "item_texture.json", atlas)


def emit_lang(items):
    lines = ["## Fablecraft: Reforged — generated lang", ""]
    for i in items:
        lines.append(f"item.{NAMESPACE}:{i['id']}={i['name']}")
    for m in MOBS:
        lines.append(f"entity.{NAMESPACE}:{m['id']}.name={m['name']}")
        lines.append(f"item.spawn_egg.entity.{NAMESPACE}:{m['id']}.name=Spawn {m['name']}")
    lines += [
        "fc.hud.title=Fablecraft: Reforged",
        "fc.guild.welcome=Welcome to the Heroes' Guild",
    ]
    write_text(RP / "texts" / "en_US.lang", "\n".join(lines) + "\n")
    write_json(RP / "texts" / "languages.json", ["en_US"])


def main():
    items = fc_data.all_items()
    for mob in MOBS:
        emit_geometry(mob)
        emit_client_entity(mob)
    emit_animations()
    emit_render_controller()
    emit_item_atlas(items)
    emit_lang(items)
    print(f"emitted RP: {len(MOBS)} geometries + client entities, atlas({len(items)}), lang")


if __name__ == "__main__":
    main()

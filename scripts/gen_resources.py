"""gen_resources.py — emits the Resource Pack:
geometry (from fc_mobs cube data), client entities, animations,
render controllers, item_texture.json, attachables for held weapons,
terrain/blocks pass-through, lang files, and sound definitions JSON.
"""
import json

from fc_lib import Px, RP, NAMESPACE, write_json, write_text
import fc_data
from fc_mobs import MOBS, build_parts, mob_palette, pack_uvs, is_romanceable

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
                    "leg_r": {"rotation": [
                        "math.cos(query.anim_time * 38) * 30 * math.clamp(query.modified_move_speed * 3, 0.4, 1.15)",
                        0,
                        0,
                    ]},
                    "leg_l": {"rotation": [
                        "-math.cos(query.anim_time * 38) * 30 * math.clamp(query.modified_move_speed * 3, 0.4, 1.15)",
                        0,
                        0,
                    ]},
                    "arm_r": {"rotation": [
                        "-math.cos(query.anim_time * 38 + 7) * 24 * math.clamp(query.modified_move_speed * 3, 0.35, 1.1)",
                        "math.sin(query.anim_time * 38) * 2",
                        "1.5 + math.sin(query.anim_time * 76) * 0.8",
                    ]},
                    "arm_l": {"rotation": [
                        "math.cos(query.anim_time * 38 - 7) * 24 * math.clamp(query.modified_move_speed * 3, 0.35, 1.1)",
                        "-math.sin(query.anim_time * 38) * 2",
                        "-1.5 - math.sin(query.anim_time * 76) * 0.8",
                    ]},
                    "body": {
                        "rotation": [
                            "1.5 + math.abs(math.sin(query.anim_time * 38)) * 1.2",
                            "math.sin(query.anim_time * 38) * 2.6",
                            "math.cos(query.anim_time * 38) * 2.2",
                        ],
                        "position": [
                            0,
                            "math.abs(math.sin(query.anim_time * 38)) * 0.42 * math.clamp(query.modified_move_speed * 3, 0.4, 1.15)",
                            0,
                        ],
                    },
                    "head": {"rotation": [
                        "query.target_x_rotation - math.abs(math.sin(query.anim_time * 38)) * 1.1",
                        "query.target_y_rotation - math.sin(query.anim_time * 38) * 1.3",
                        "-math.cos(query.anim_time * 38) * 0.7",
                    ]},
                },
            },
            "animation.fc.biped.idle": {
                "loop": True,
                "bones": {
                    "arm_r": {"rotation": [
                        "math.sin(query.life_time * 72 + variable.anim_offset) * 2.6",
                        0,
                        "2 + math.sin(query.life_time * 43 + variable.anim_offset + 65) * 1.2",
                    ]},
                    "arm_l": {"rotation": [
                        "-math.sin(query.life_time * 72 + variable.anim_offset + 28) * 2.4",
                        0,
                        "-2 - math.sin(query.life_time * 43 + variable.anim_offset + 65) * 1.2",
                    ]},
                    "body": {
                        "rotation": [
                            "math.sin(query.life_time * 76 + variable.anim_offset + 18) * 0.7",
                            "math.sin(query.life_time * 29 + variable.anim_offset) * 1.1",
                            "math.sin(query.life_time * 43 + variable.anim_offset + 65) * 1.4",
                        ],
                        "position": [
                            0,
                            "math.sin(query.life_time * 76 + variable.anim_offset) * 0.19",
                            0,
                        ],
                    },
                    "head": {"rotation": [
                        "query.target_x_rotation + math.sin(query.life_time * 31 + variable.anim_offset + 20) * 1.5",
                        "query.target_y_rotation + math.sin(query.life_time * 21 + variable.anim_offset) * 2.8",
                        "math.sin(query.life_time * 37 + variable.anim_offset + 80) * 0.7",
                    ]},
                },
            },
            "animation.fc.biped.attack": {
                "loop": True,
                "bones": {
                    "arm_r": {"rotation": [
                        "-138 * math.sin(variable.attack_time * 180)",
                        "-12 * math.sin(variable.attack_time * 180)",
                        "7 * math.sin(variable.attack_time * 360)",
                    ]},
                    "arm_l": {"rotation": [
                        "-24 * math.sin(variable.attack_time * 180)",
                        "7 * math.sin(variable.attack_time * 180)",
                        "-5 * math.sin(variable.attack_time * 360)",
                    ]},
                    "body": {
                        "rotation": [
                            "8 * math.sin(variable.attack_time * 180)",
                            "-14 * math.sin(variable.attack_time * 180)",
                            "3 * math.sin(variable.attack_time * 360)",
                        ],
                        "position": [
                            0,
                            "-math.sin(variable.attack_time * 180) * 0.25",
                            "-math.sin(variable.attack_time * 180) * 0.35",
                        ],
                    },
                    "head": {"rotation": [
                        "-5 * math.sin(variable.attack_time * 180)",
                        "8 * math.sin(variable.attack_time * 180)",
                        0,
                    ]},
                },
            },
            "animation.fc.biped.gesture": {
                "loop": True,
                "bones": {
                    "arm_r": {"rotation": [
                        "-46 + math.sin(query.life_time * 160 + variable.anim_offset) * 14",
                        "math.sin(query.life_time * 83 + variable.anim_offset) * 5",
                        "10 + math.sin(query.life_time * 90 + variable.anim_offset + 35) * 6",
                    ]},
                    "arm_l": {"rotation": [
                        "-12 + math.sin(query.life_time * 130 + variable.anim_offset + 55) * 8",
                        0,
                        "-6 - math.sin(query.life_time * 74 + variable.anim_offset) * 3",
                    ]},
                    "head": {"rotation": [
                        "query.target_x_rotation + math.sin(query.life_time * 140 + variable.anim_offset) * 5",
                        "query.target_y_rotation + math.sin(query.life_time * 48 + variable.anim_offset + 25) * 2",
                        "math.sin(query.life_time * 61 + variable.anim_offset) * 1.5",
                    ]},
                    "body": {
                        "rotation": [
                            "math.sin(query.life_time * 90 + variable.anim_offset) * 1.2",
                            "math.sin(query.life_time * 70 + variable.anim_offset) * 3.5",
                            "math.sin(query.life_time * 45 + variable.anim_offset + 70) * 1.2",
                        ],
                        "position": [
                            0,
                            "math.sin(query.life_time * 90 + variable.anim_offset) * 0.12",
                            0,
                        ],
                    },
                },
            },
            "animation.fc.biped.bow": {
                "loop": True,
                "bones": {
                    "arm_r": {"rotation": ["-90 + query.target_x_rotation", "query.target_y_rotation - 12", 0]},
                    "arm_l": {"rotation": ["-86 + query.target_x_rotation", "query.target_y_rotation + 14", 0]},
                },
            },
            # one-shot greeting wave, played on demand when an NPC notices / talks
            # to a passing Hero (script-driven via Entity.playAnimation)
            "animation.fc.biped.greet": {
                "loop": False,
                "animation_length": 1.5,
                "bones": {
                    "arm_r": {"rotation": {
                        "0.0": [0, 0, 0], "0.25": [-128, 0, 18], "0.55": [-128, 0, -16],
                        "0.85": [-128, 0, 18], "1.15": [-128, 0, -16], "1.5": [0, 0, 0],
                    }},
                    "arm_l": {"rotation": {"0.0": [0, 0, 0], "0.5": [-16, 0, -4], "1.5": [0, 0, 0]}},
                    "head": {"rotation": {"0.0": [0, 0, 0], "0.4": [9, 0, 0], "1.5": [0, 0, 0]}},
                    "body": {"rotation": {"0.0": [0, 0, 0], "0.4": [5, 0, 0], "1.5": [0, 0, 0]}},
                },
            },
            "animation.fc.hobbe.walk": {
                "loop": True,
                "anim_time_update": "query.modified_distance_moved",
                "bones": {
                    "leg_r": {"rotation": [
                        "math.cos(query.anim_time * 58) * 38 * math.clamp(query.modified_move_speed * 3.4, 0.55, 1.2)",
                        0,
                        3,
                    ]},
                    "leg_l": {"rotation": [
                        "-math.cos(query.anim_time * 58) * 38 * math.clamp(query.modified_move_speed * 3.4, 0.55, 1.2)",
                        0,
                        -3,
                    ]},
                    "arm_r": {"rotation": [
                        "-18 - math.cos(query.anim_time * 58 + 10) * 30",
                        "math.sin(query.anim_time * 58) * 4",
                        8,
                    ]},
                    "arm_l": {"rotation": [
                        "-18 + math.cos(query.anim_time * 58 - 10) * 30",
                        "-math.sin(query.anim_time * 58) * 4",
                        -8,
                    ]},
                    "body": {
                        "rotation": [
                            "10 + math.abs(math.sin(query.anim_time * 58)) * 4",
                            "math.sin(query.anim_time * 58) * 5",
                            "math.cos(query.anim_time * 58) * 4",
                        ],
                        "position": [
                            0,
                            "math.abs(math.sin(query.anim_time * 58)) * 0.55",
                            "math.cos(query.anim_time * 116) * 0.08",
                        ],
                    },
                    "head": {"rotation": [
                        "query.target_x_rotation - 6 - math.abs(math.sin(query.anim_time * 58)) * 2",
                        "query.target_y_rotation - math.sin(query.anim_time * 58) * 2",
                        "-math.cos(query.anim_time * 58) * 2",
                    ]},
                },
            },
            "animation.fc.hobbe.idle": {
                "loop": True,
                "bones": {
                    "body": {
                        "rotation": [
                            "8 + math.sin(query.life_time * 82 + variable.anim_offset) * 1.8",
                            "math.sin(query.life_time * 37 + variable.anim_offset) * 2",
                            "math.sin(query.life_time * 51 + variable.anim_offset + 40) * 2.4",
                        ],
                        "position": [
                            0,
                            "math.sin(query.life_time * 82 + variable.anim_offset) * 0.2",
                            0,
                        ],
                    },
                    "head": {"rotation": [
                        "query.target_x_rotation - 4 + math.sin(query.life_time * 61 + variable.anim_offset) * 2.5",
                        "query.target_y_rotation + math.sin(query.life_time * 29 + variable.anim_offset) * 4",
                        "math.sin(query.life_time * 43 + variable.anim_offset + 70) * 1.5",
                    ]},
                    "arm_r": {"rotation": [
                        "-14 + math.sin(query.life_time * 82 + variable.anim_offset) * 4",
                        0,
                        7,
                    ]},
                    "arm_l": {"rotation": [
                        "-14 - math.sin(query.life_time * 82 + variable.anim_offset + 25) * 4",
                        0,
                        -7,
                    ]},
                    "leg_r": {"rotation": [
                        "math.sin(query.life_time * 31 + variable.anim_offset) * 1.5",
                        0,
                        2,
                    ]},
                    "leg_l": {"rotation": [
                        "-math.sin(query.life_time * 31 + variable.anim_offset) * 1.5",
                        0,
                        -2,
                    ]},
                },
            },
            "animation.fc.hobbe.attack": {
                "loop": True,
                "bones": {
                    "arm_r": {"rotation": [
                        "-150 * math.sin(variable.attack_time * 180)",
                        "-18 * math.sin(variable.attack_time * 180)",
                        "16 * math.sin(variable.attack_time * 360)",
                    ]},
                    "arm_l": {"rotation": [
                        "-55 * math.sin(variable.attack_time * 180)",
                        "12 * math.sin(variable.attack_time * 180)",
                        "-10 * math.sin(variable.attack_time * 360)",
                    ]},
                    "body": {
                        "rotation": [
                            "16 * math.sin(variable.attack_time * 180)",
                            "-20 * math.sin(variable.attack_time * 180)",
                            "7 * math.sin(variable.attack_time * 360)",
                        ],
                        "position": [0, "-math.sin(variable.attack_time * 180) * 0.5", 0],
                    },
                    "head": {"rotation": [
                        "-12 * math.sin(variable.attack_time * 180)",
                        "12 * math.sin(variable.attack_time * 180)",
                        0,
                    ]},
                },
            },
            "animation.fc.troll.walk": {
                "loop": True,
                "anim_time_update": "query.modified_distance_moved",
                "bones": {
                    "leg_r": {"rotation": [
                        "math.cos(query.anim_time * 27) * 24 * math.clamp(query.modified_move_speed * 3.8, 0.5, 1.05)",
                        0,
                        3,
                    ]},
                    "leg_l": {"rotation": [
                        "-math.cos(query.anim_time * 27) * 24 * math.clamp(query.modified_move_speed * 3.8, 0.5, 1.05)",
                        0,
                        -3,
                    ]},
                    "arm_r": {"rotation": [
                        "-18 - math.cos(query.anim_time * 27 + 12) * 16",
                        "math.sin(query.anim_time * 27) * 3",
                        8,
                    ]},
                    "arm_l": {"rotation": [
                        "-18 + math.cos(query.anim_time * 27 - 12) * 16",
                        "-math.sin(query.anim_time * 27) * 3",
                        -8,
                    ]},
                    "body": {
                        "rotation": [
                            "10 + math.abs(math.sin(query.anim_time * 27)) * 3",
                            "math.sin(query.anim_time * 27) * 3.5",
                            "math.cos(query.anim_time * 27) * 3.8",
                        ],
                        "position": [
                            0,
                            "math.abs(math.sin(query.anim_time * 27)) * 0.62",
                            "-math.abs(math.cos(query.anim_time * 27)) * 0.12",
                        ],
                    },
                    "head": {"rotation": [
                        "query.target_x_rotation - 5 - math.abs(math.sin(query.anim_time * 27)) * 1.5",
                        "query.target_y_rotation - math.sin(query.anim_time * 27) * 1.5",
                        "-math.cos(query.anim_time * 27) * 1.4",
                    ]},
                },
            },
            "animation.fc.troll.idle": {
                "loop": True,
                "bones": {
                    "body": {
                        "rotation": [
                            "10 + math.sin(query.life_time * 58 + variable.anim_offset) * 1.3",
                            "math.sin(query.life_time * 21 + variable.anim_offset) * 1.5",
                            "math.sin(query.life_time * 32 + variable.anim_offset + 60) * 1.8",
                        ],
                        "position": [
                            0,
                            "math.sin(query.life_time * 58 + variable.anim_offset) * 0.28",
                            0,
                        ],
                    },
                    "head": {"rotation": [
                        "query.target_x_rotation - 4 + math.sin(query.life_time * 27 + variable.anim_offset) * 1.2",
                        "query.target_y_rotation + math.sin(query.life_time * 17 + variable.anim_offset) * 2",
                        "math.sin(query.life_time * 31 + variable.anim_offset + 60) * 0.8",
                    ]},
                    "arm_r": {"rotation": [
                        "-16 + math.sin(query.life_time * 58 + variable.anim_offset) * 2.5",
                        0,
                        8,
                    ]},
                    "arm_l": {"rotation": [
                        "-16 - math.sin(query.life_time * 58 + variable.anim_offset + 35) * 2.5",
                        0,
                        -8,
                    ]},
                    "leg_r": {"rotation": [0, 0, 3]},
                    "leg_l": {"rotation": [0, 0, -3]},
                },
            },
            "animation.fc.troll.attack": {
                "loop": True,
                "bones": {
                    "arm_r": {"rotation": [
                        "-165 * math.sin(variable.attack_time * 180)",
                        "-22 * math.sin(variable.attack_time * 180)",
                        "15 * math.sin(variable.attack_time * 360)",
                    ]},
                    "arm_l": {"rotation": [
                        "-118 * math.sin(variable.attack_time * 180)",
                        "18 * math.sin(variable.attack_time * 180)",
                        "-15 * math.sin(variable.attack_time * 360)",
                    ]},
                    "body": {
                        "rotation": [
                            "20 * math.sin(variable.attack_time * 180)",
                            "-16 * math.sin(variable.attack_time * 180)",
                            "5 * math.sin(variable.attack_time * 360)",
                        ],
                        "position": [
                            0,
                            "-math.sin(variable.attack_time * 180) * 0.7",
                            "math.sin(variable.attack_time * 180) * 0.3",
                        ],
                    },
                    "head": {"rotation": [
                        "-10 * math.sin(variable.attack_time * 180)",
                        "10 * math.sin(variable.attack_time * 180)",
                        0,
                    ]},
                    "leg_r": {"rotation": [
                        "10 * math.sin(variable.attack_time * 180)",
                        0,
                        0,
                    ]},
                    "leg_l": {"rotation": [
                        "6 * math.sin(variable.attack_time * 180)",
                        0,
                        0,
                    ]},
                },
            },
            "animation.fc.twinblade.walk": {
                "loop": True,
                "anim_time_update": "query.modified_distance_moved",
                "bones": {
                    "leg_r": {"rotation": [
                        "math.cos(query.anim_time * 31) * 25 * math.clamp(query.modified_move_speed * 3.4, 0.5, 1.1)",
                        0,
                        4,
                    ]},
                    "leg_l": {"rotation": [
                        "-math.cos(query.anim_time * 31) * 25 * math.clamp(query.modified_move_speed * 3.4, 0.5, 1.1)",
                        0,
                        -4,
                    ]},
                    "arm_r": {"rotation": [
                        "-10 - math.cos(query.anim_time * 31 + 9) * 18",
                        "math.sin(query.anim_time * 31) * 3",
                        7,
                    ]},
                    "arm_l": {"rotation": [
                        "-10 + math.cos(query.anim_time * 31 - 9) * 18",
                        "-math.sin(query.anim_time * 31) * 3",
                        -7,
                    ]},
                    "body": {
                        "rotation": [
                            "4 + math.abs(math.sin(query.anim_time * 31)) * 2",
                            "math.sin(query.anim_time * 31) * 3.2",
                            "math.cos(query.anim_time * 31) * 3.1",
                        ],
                        "position": [
                            0,
                            "math.abs(math.sin(query.anim_time * 31)) * 0.5",
                            0,
                        ],
                    },
                    "head": {"rotation": [
                        "query.target_x_rotation - 2",
                        "query.target_y_rotation - math.sin(query.anim_time * 31) * 1.4",
                        "-math.cos(query.anim_time * 31) * 0.9",
                    ]},
                    "collar": {"rotation": [
                        "-math.abs(math.sin(query.anim_time * 31 + 12)) * 1.5",
                        0,
                        "-math.cos(query.anim_time * 31 + 12) * 1.2",
                    ]},
                    "pauldron_r": {"rotation": [
                        "math.sin(query.anim_time * 62 + 18) * 1.5",
                        0,
                        "8 + math.cos(query.anim_time * 31 + 15) * 1.5",
                    ]},
                    "pauldron_l": {"rotation": [
                        "-math.sin(query.anim_time * 62 + 18) * 1.5",
                        0,
                        "-8 - math.cos(query.anim_time * 31 + 15) * 1.5",
                    ]},
                    "blade_r": {"rotation": [
                        "math.sin(query.anim_time * 31 + 18) * 1.2",
                        0,
                        "26 - math.cos(query.anim_time * 31 + 18) * 1.4",
                    ]},
                    "blade_l": {"rotation": [
                        "math.sin(query.anim_time * 31 + 18) * 1.2",
                        0,
                        "-26 + math.cos(query.anim_time * 31 + 18) * 1.4",
                    ]},
                },
            },
            "animation.fc.twinblade.idle": {
                "loop": True,
                "bones": {
                    "body": {
                        "rotation": [
                            "math.sin(query.life_time * 63 + variable.anim_offset) * 1",
                            "math.sin(query.life_time * 24 + variable.anim_offset) * 1.5",
                            "math.sin(query.life_time * 34 + variable.anim_offset + 60) * 1.5",
                        ],
                        "position": [
                            0,
                            "math.sin(query.life_time * 63 + variable.anim_offset) * 0.24",
                            0,
                        ],
                    },
                    "head": {"rotation": [
                        "query.target_x_rotation + math.sin(query.life_time * 29 + variable.anim_offset) * 1.2",
                        "query.target_y_rotation + math.sin(query.life_time * 17 + variable.anim_offset) * 2",
                        "math.sin(query.life_time * 31 + variable.anim_offset + 60) * 0.7",
                    ]},
                    "arm_r": {"rotation": [
                        "-8 + math.sin(query.life_time * 63 + variable.anim_offset) * 2",
                        0,
                        6,
                    ]},
                    "arm_l": {"rotation": [
                        "-8 - math.sin(query.life_time * 63 + variable.anim_offset + 30) * 2",
                        0,
                        -6,
                    ]},
                    "collar": {"rotation": [
                        "math.sin(query.life_time * 42 + variable.anim_offset + 20) * 0.8",
                        0,
                        0,
                    ]},
                    "blade_r": {"rotation": [
                        "math.sin(query.life_time * 42 + variable.anim_offset + 40) * 0.7",
                        0,
                        26,
                    ]},
                    "blade_l": {"rotation": [
                        "math.sin(query.life_time * 42 + variable.anim_offset + 40) * 0.7",
                        0,
                        -26,
                    ]},
                },
            },
            "animation.fc.twinblade.attack": {
                "loop": True,
                "bones": {
                    "arm_r": {"rotation": [
                        "-165 * math.sin(variable.attack_time * 180)",
                        "-28 * math.sin(variable.attack_time * 180)",
                        "18 * math.sin(variable.attack_time * 360)",
                    ]},
                    "arm_l": {"rotation": [
                        "-150 * math.sin(variable.attack_time * 180)",
                        "28 * math.sin(variable.attack_time * 180)",
                        "-18 * math.sin(variable.attack_time * 360)",
                    ]},
                    "body": {
                        "rotation": [
                            "18 * math.sin(variable.attack_time * 180)",
                            "-24 * math.sin(variable.attack_time * 180)",
                            "7 * math.sin(variable.attack_time * 360)",
                        ],
                        "position": [
                            0,
                            "-math.sin(variable.attack_time * 180) * 0.55",
                            "-math.sin(variable.attack_time * 180) * 0.35",
                        ],
                    },
                    "head": {"rotation": [
                        "-9 * math.sin(variable.attack_time * 180)",
                        "12 * math.sin(variable.attack_time * 180)",
                        0,
                    ]},
                    "pauldron_r": {"rotation": [
                        "-10 * math.sin(variable.attack_time * 180)",
                        0,
                        "8 + 6 * math.sin(variable.attack_time * 360)",
                    ]},
                    "pauldron_l": {"rotation": [
                        "-10 * math.sin(variable.attack_time * 180)",
                        0,
                        "-8 - 6 * math.sin(variable.attack_time * 360)",
                    ]},
                    "blade_r": {"rotation": [
                        "7 * math.sin(variable.attack_time * 180)",
                        0,
                        "26 - 4 * math.sin(variable.attack_time * 360)",
                    ]},
                    "blade_l": {"rotation": [
                        "7 * math.sin(variable.attack_time * 180)",
                        0,
                        "-26 + 4 * math.sin(variable.attack_time * 360)",
                    ]},
                },
            },
            # quadruped (balverine): diagonal-pair gait (rear-right + front-left lead
            # together), amplitude clamped so slow prowls don't skate, with a sprung
            # body bob, head look-tracking and a live tail (seeded so the 3 balverines
            # don't wag in unison).
            "animation.fc.quadruped.walk": {
                "loop": True,
                "anim_time_update": "query.modified_distance_moved",
                "bones": {
                    "leg_r": {"rotation": ["math.cos(query.anim_time * 38) * 34 * math.clamp(query.modified_move_speed * 3, 0.45, 1.2)", 0, 0]},
                    "leg_l": {"rotation": ["-math.cos(query.anim_time * 38) * 34 * math.clamp(query.modified_move_speed * 3, 0.45, 1.2)", 0, 0]},
                    "arm_r": {"rotation": ["-math.cos(query.anim_time * 38) * 32 * math.clamp(query.modified_move_speed * 3, 0.45, 1.2)", 0, 0]},
                    "arm_l": {"rotation": ["math.cos(query.anim_time * 38) * 32 * math.clamp(query.modified_move_speed * 3, 0.45, 1.2)", 0, 0]},
                    "body": {
                        "rotation": [
                            "math.cos(query.anim_time * 76) * 2.5",
                            "math.sin(query.anim_time * 38) * 3",
                            "math.cos(query.anim_time * 38) * 2.5",
                        ],
                        "position": [0, "math.abs(math.sin(query.anim_time * 38)) * 0.4 * math.clamp(query.modified_move_speed * 3, 0.45, 1.2)", 0],
                    },
                    "head": {"rotation": [
                        "query.target_x_rotation - math.abs(math.sin(query.anim_time * 38)) * 2",
                        "query.target_y_rotation - math.sin(query.anim_time * 38) * 2",
                        "-math.cos(query.anim_time * 38) * 1.5",
                    ]},
                    "tail": {"rotation": [
                        "8 + math.sin(query.anim_time * 38 + variable.anim_offset) * 6",
                        "math.cos(query.anim_time * 38) * 8",
                        0,
                    ]},
                },
            },
            # standing-on-all-fours idle: breathing body, look-around head, faint
            # weight shift through the legs and a lazy tail — NOT the bipedal arm swing
            # the balverines used to borrow from animation.fc.biped.idle.
            "animation.fc.quadruped.idle": {
                "loop": True,
                "bones": {
                    # heavier breathing + a slow shoulder roll so a standing balverine
                    # clearly reads as alive, not frozen.
                    "body": {
                        "rotation": [
                            "math.sin(query.life_time * 60 + variable.anim_offset) * 1.4",
                            "math.sin(query.life_time * 23 + variable.anim_offset) * 1.6",
                            "math.sin(query.life_time * 34 + variable.anim_offset + 50) * 2.2",
                        ],
                        "position": [0, "math.sin(query.life_time * 60 + variable.anim_offset) * 0.4", 0],
                    },
                    "head": {"rotation": [
                        "query.target_x_rotation + math.sin(query.life_time * 38 + variable.anim_offset) * 4",
                        "query.target_y_rotation + math.sin(query.life_time * 17 + variable.anim_offset) * 9",
                        "math.sin(query.life_time * 30 + variable.anim_offset + 60) * 3",
                    ]},
                    "leg_r": {"rotation": ["math.sin(query.life_time * 25 + variable.anim_offset) * 2", 0, 0]},
                    "leg_l": {"rotation": ["-math.sin(query.life_time * 25 + variable.anim_offset) * 2", 0, 0]},
                    "arm_r": {"rotation": ["math.sin(query.life_time * 27 + variable.anim_offset + 30) * 2", 0, 0]},
                    "arm_l": {"rotation": ["-math.sin(query.life_time * 27 + variable.anim_offset + 30) * 2", 0, 0]},
                    "tail": {"rotation": [
                        "10 + math.sin(query.life_time * 46 + variable.anim_offset) * 8",
                        "math.sin(query.life_time * 34 + variable.anim_offset) * 12",
                        0,
                    ]},
                },
            },
            # pounce: rear up on the hind legs, front paws rake forward, body lunges in.
            "animation.fc.quadruped.attack": {
                "loop": True,
                "bones": {
                    "arm_r": {"rotation": ["-95 * math.sin(variable.attack_time * 180)", 0, "12 * math.sin(variable.attack_time * 360)"]},
                    "arm_l": {"rotation": ["-95 * math.sin(variable.attack_time * 180)", 0, "-12 * math.sin(variable.attack_time * 360)"]},
                    "body": {
                        "rotation": ["-22 * math.sin(variable.attack_time * 180)", 0, 0],
                        "position": [0, "math.sin(variable.attack_time * 180) * 0.5", "-math.sin(variable.attack_time * 180) * 0.6"],
                    },
                    "head": {"rotation": ["18 * math.sin(variable.attack_time * 180)", 0, 0]},
                    "leg_r": {"rotation": ["20 * math.sin(variable.attack_time * 180)", 0, 0]},
                    "leg_l": {"rotation": ["20 * math.sin(variable.attack_time * 180)", 0, 0]},
                    "tail": {"rotation": ["-20 * math.sin(variable.attack_time * 180)", 0, 0]},
                },
            },
            # ---- Stag Beetle: only owns body/head/legs, so it had NO usable motion
            #      under the borrowed scorpion.walk (which drives leg_r0..3/claw/tail it
            #      lacks). Its own clips animate the three bones it actually has. ----
            "animation.fc.beetle.walk": {
                "loop": True,
                "anim_time_update": "query.modified_distance_moved * 2.2",
                "bones": {
                    "legs": {"rotation": [
                        "math.cos(query.anim_time * 180) * 12 * math.clamp(query.modified_move_speed * 3, 0.5, 1.2)",
                        "math.sin(query.anim_time * 360) * 5",
                        0,
                    ]},
                    "body": {
                        "rotation": [
                            "2 + math.abs(math.sin(query.anim_time * 180)) * 2",
                            "math.sin(query.anim_time * 180) * 3",
                            "math.cos(query.anim_time * 180) * 4",
                        ],
                        "position": [0, "math.abs(math.sin(query.anim_time * 360)) * 0.12 * math.clamp(query.modified_move_speed * 3, 0.5, 1.2)", 0],
                    },
                    "head": {"rotation": ["math.sin(query.anim_time * 360) * 4", "math.sin(query.anim_time * 180) * 5", 0]},
                },
            },
            "animation.fc.beetle.idle": {
                "loop": True,
                "bones": {
                    "body": {
                        "rotation": [0, 0, "math.sin(query.life_time * 40 + variable.anim_offset) * 1.2"],
                        "position": [0, "math.sin(query.life_time * 64 + variable.anim_offset) * 0.08", 0],
                    },
                    "head": {"rotation": [
                        "math.sin(query.life_time * 33 + variable.anim_offset) * 3",
                        "math.sin(query.life_time * 27 + variable.anim_offset + 40) * 5",
                        0,
                    ]},
                    "legs": {"rotation": ["math.sin(query.life_time * 80 + variable.anim_offset) * 2", 0, 0]},
                },
            },
            "animation.fc.beetle.attack": {
                "loop": True,
                "bones": {
                    "body": {
                        "rotation": ["-18 * math.sin(variable.attack_time * 180)", 0, 0],
                        "position": [0, 0, "-math.sin(variable.attack_time * 180) * 0.4"],
                    },
                    "head": {"rotation": ["-22 * math.sin(variable.attack_time * 180)", 0, 0]},
                    "legs": {"rotation": ["10 * math.sin(variable.attack_time * 180)", 0, 0]},
                },
            },
            # fly = the wing/leg layer; hover = the body-bob layer. Both sit in the
            # always-on list together, so they MUST stay on disjoint bones. anim_offset
            # desyncs the swarm (wasps no longer beat their wings in unison).
            "animation.fc.fly": {
                "loop": True,
                "bones": {
                    "wing_r": {"rotation": [0, 0, "-math.sin(query.life_time * 1400 + variable.anim_offset) * 40 - 15"]},
                    "wing_l": {"rotation": [0, 0, "math.sin(query.life_time * 1400 + variable.anim_offset) * 40 + 15"]},
                    "legs": {"rotation": ["math.sin(query.life_time * 200 + variable.anim_offset) * 6", 0, 0]},
                },
            },
            "animation.fc.hover": {
                "loop": True,
                "bones": {
                    "body": {
                        "rotation": [
                            "math.sin(query.life_time * 120 + variable.anim_offset) * 2.5",
                            0,
                            "math.sin(query.life_time * 90 + variable.anim_offset + 40) * 2",
                        ],
                        "position": [0, "math.sin(query.life_time * 120 + variable.anim_offset) * 0.6", 0],
                    },
                },
            },
            "animation.fc.ghost.float": {
                "loop": True,
                "bones": {
                    "body": {
                        "position": [0, "1.5 + math.sin(query.life_time * 90 + variable.anim_offset) * 0.8", 0],
                        "rotation": [
                            0,
                            "math.sin(query.life_time * 33 + variable.anim_offset) * 3",
                            "math.sin(query.life_time * 47 + variable.anim_offset + 40) * 2.5",
                        ],
                    },
                    "arm_r": {"rotation": [
                        "-40 + math.sin(query.life_time * 70 + variable.anim_offset) * 8",
                        "math.sin(query.life_time * 55 + variable.anim_offset) * 5",
                        "10 + math.sin(query.life_time * 60 + variable.anim_offset + 30) * 4",
                    ]},
                    "arm_l": {"rotation": [
                        "-40 - math.sin(query.life_time * 70 + variable.anim_offset + 25) * 8",
                        "-math.sin(query.life_time * 55 + variable.anim_offset) * 5",
                        "-10 - math.sin(query.life_time * 60 + variable.anim_offset + 30) * 4",
                    ]},
                    "head": {"rotation": [
                        "query.target_x_rotation + math.sin(query.life_time * 31 + variable.anim_offset) * 2",
                        "query.target_y_rotation + math.sin(query.life_time * 21 + variable.anim_offset) * 3",
                        "math.sin(query.life_time * 37 + variable.anim_offset + 60) * 2",
                    ]},
                },
            },
            # ghostly lunge — both arms rake forward as the spectre surges in
            "animation.fc.ghost.attack": {
                "loop": True,
                "bones": {
                    "arm_r": {"rotation": ["-120 * math.sin(variable.attack_time * 180)", "-18 * math.sin(variable.attack_time * 180)", "20 * math.sin(variable.attack_time * 360)"]},
                    "arm_l": {"rotation": ["-120 * math.sin(variable.attack_time * 180)", "18 * math.sin(variable.attack_time * 180)", "-20 * math.sin(variable.attack_time * 360)"]},
                    "body": {
                        "rotation": ["14 * math.sin(variable.attack_time * 180)", 0, 0],
                        "position": [0, 0, "-math.sin(variable.attack_time * 180) * 0.7"],
                    },
                    "head": {"rotation": ["-10 * math.sin(variable.attack_time * 180)", 0, 0]},
                },
            },
            "animation.fc.scorpion.walk": {
                "loop": True,
                "anim_time_update": "query.modified_distance_moved",
                "bones": {
                    **{f"leg_r{i}": {"rotation": [0, f"math.cos(query.anim_time * 40 + {i*90}) * 15 * math.clamp(query.modified_move_speed * 3, 0.45, 1.2)", 0]} for i in range(4)},
                    **{f"leg_l{i}": {"rotation": [0, f"-math.cos(query.anim_time * 40 + {i*90}) * 15 * math.clamp(query.modified_move_speed * 3, 0.45, 1.2)", 0]} for i in range(4)},
                    "body": {"position": [0, "math.abs(math.sin(query.anim_time * 80)) * 0.12 * math.clamp(query.modified_move_speed * 3, 0.45, 1.2)", 0]},
                    "tail": {"rotation": ["-46 + math.sin(query.life_time * 100) * 5", 0, "math.sin(query.anim_time * 40) * 4"]},
                    "tail_tip": {"rotation": ["-60 + math.sin(query.life_time * 120 + 30) * 6", 0, 0]},
                    "claw_r": {"rotation": [0, "24 + math.sin(query.life_time * 130) * 8", "math.sin(query.anim_time * 40) * 4"]},
                    "claw_l": {"rotation": [0, "-24 - math.sin(query.life_time * 130) * 8", "-math.sin(query.anim_time * 40) * 4"]},
                },
            },
            "animation.fc.scorpion.idle": {
                "loop": True,
                "bones": {
                    "body": {"position": [0, "math.sin(query.life_time * 58 + variable.anim_offset) * 0.1", 0]},
                    "head": {"rotation": [
                        "math.sin(query.life_time * 33 + variable.anim_offset) * 3",
                        "math.sin(query.life_time * 27 + variable.anim_offset) * 5",
                        0,
                    ]},
                    "tail": {"rotation": ["-46 + math.sin(query.life_time * 47 + variable.anim_offset) * 7", 0, 0]},
                    "tail_tip": {"rotation": ["-60 + math.sin(query.life_time * 47 + variable.anim_offset + 40) * 9", 0, 0]},
                    "claw_r": {"rotation": [0, "24 + math.sin(query.life_time * 70 + variable.anim_offset) * 10", 0]},
                    "claw_l": {"rotation": [0, "-24 - math.sin(query.life_time * 70 + variable.anim_offset + 20) * 10", 0]},
                    **{f"leg_r{i}": {"rotation": [0, f"math.sin(query.life_time * 40 + variable.anim_offset + {i*50}) * 2", 0]} for i in range(4)},
                    **{f"leg_l{i}": {"rotation": [0, f"-math.sin(query.life_time * 40 + variable.anim_offset + {i*50}) * 2", 0]} for i in range(4)},
                },
            },
            # tail arcs back and snaps over the head; pincers flare and the body lunges.
            "animation.fc.scorpion.attack": {
                "loop": True,
                "bones": {
                    "tail": {"rotation": ["-46 - 60 * math.sin(variable.attack_time * 180)", 0, 0]},
                    "tail_tip": {"rotation": ["-60 - 50 * math.sin(variable.attack_time * 180)", 0, 0]},
                    "claw_r": {"rotation": [0, "24 - 30 * math.sin(variable.attack_time * 360)", 0]},
                    "claw_l": {"rotation": [0, "-24 + 30 * math.sin(variable.attack_time * 360)", 0]},
                    "body": {
                        "rotation": ["-10 * math.sin(variable.attack_time * 180)", 0, 0],
                        "position": [0, 0, "-math.sin(variable.attack_time * 180) * 0.4"],
                    },
                    "head": {"rotation": ["-8 * math.sin(variable.attack_time * 180)", 0, 0]},
                },
            },
            "animation.fc.dragon.fly": {
                "loop": True,
                "bones": {
                    "wing_r": {"rotation": [0, 0, "30 - math.sin(query.life_time * 500) * 35"]},
                    "wing_l": {"rotation": [0, 0, "-30 + math.sin(query.life_time * 500) * 35"]},
                    "tail": {"rotation": ["14 + math.sin(query.life_time * 90) * 6", 0, "math.sin(query.life_time * 70) * 5"]},
                    "neck": {"rotation": ["-26 + math.sin(query.life_time * 70) * 4", 0, 0]},
                    "head": {"rotation": ["query.target_x_rotation + math.sin(query.life_time * 60) * 3", "query.target_y_rotation", 0]},
                    # body heaves on the downbeat; limbs tuck and sway with the wings
                    "body": {"position": [0, "math.sin(query.life_time * 500 + 90) * 0.5", 0]},
                    "leg_r": {"rotation": ["18 + math.sin(query.life_time * 90) * 4", 0, 0]},
                    "leg_l": {"rotation": ["18 + math.sin(query.life_time * 90) * 4", 0, 0]},
                    "arm_r": {"rotation": ["-14 + math.sin(query.life_time * 500 + 45) * 5", 0, 0]},
                    "arm_l": {"rotation": ["-14 + math.sin(query.life_time * 500 + 45) * 5", 0, 0]},
                },
            },
            # bite: neck recoils then drives the head down, wings flare for balance,
            # foreclaws rake and the whole body surges forward.
            "animation.fc.dragon.attack": {
                "loop": True,
                "bones": {
                    "neck": {"rotation": ["-26 - 30 * math.sin(variable.attack_time * 180)", 0, 0]},
                    "head": {"rotation": ["20 * math.sin(variable.attack_time * 180)", 0, 0]},
                    "body": {
                        "rotation": ["8 * math.sin(variable.attack_time * 180)", 0, 0],
                        "position": [0, 0, "-math.sin(variable.attack_time * 180) * 0.8"],
                    },
                    "wing_r": {"rotation": [0, 0, "30 - 40 * math.sin(variable.attack_time * 180)"]},
                    "wing_l": {"rotation": [0, 0, "-30 + 40 * math.sin(variable.attack_time * 180)"]},
                    "arm_r": {"rotation": ["-40 * math.sin(variable.attack_time * 180)", 0, "15 * math.sin(variable.attack_time * 360)"]},
                    "arm_l": {"rotation": ["-40 * math.sin(variable.attack_time * 180)", 0, "-15 * math.sin(variable.attack_time * 360)"]},
                    "tail": {"rotation": ["14 - 10 * math.sin(variable.attack_time * 180)", 0, 0]},
                },
            },
            # Demon Door: the model has NO "jaw" bone — its mouth is lower_lip/upper_lip/
            # mouth_corner_l/r. The old clips animated a phantom "jaw" (silent no-op), so
            # the talking face never moved its mouth. These drive the real bones: lower_lip
            # is the jaw, the corners + eyes + brow carry the performance. (Lip open
            # direction/magnitude are a live-tuning item — pivots aren't visible here.)
            "animation.fc.door.idle": {
                "loop": True,
                "bones": {
                    "brow": {
                        "rotation": ["math.sin(query.life_time * 32 + variable.anim_offset) * 2", 0, 0],
                        "position": [0, "math.sin(query.life_time * 40 + variable.anim_offset) * 0.15", 0],
                    },
                    "lower_lip": {"rotation": ["3 + math.sin(query.life_time * 25 + variable.anim_offset) * 2", 0, 0]},
                    "eye_r": {"rotation": [
                        "math.sin(query.life_time * 21 + variable.anim_offset) * 3",
                        "math.sin(query.life_time * 17 + variable.anim_offset) * 4", 0]},
                    "eye_l": {"rotation": [
                        "math.sin(query.life_time * 21 + variable.anim_offset) * 3",
                        "math.sin(query.life_time * 17 + variable.anim_offset) * 4", 0]},
                },
            },
            "animation.fc.door.open": {
                "animation_length": 1.3,
                "bones": {
                    "lower_lip": {"rotation": {
                        "0.0": [0, 0, 0], "0.45": [18, 0, 0], "0.9": [32, 0, 0], "1.3": [40, 0, 0]}},
                    "upper_lip": {"rotation": {"0.0": [0, 0, 0], "0.9": [-8, 0, 0], "1.3": [-12, 0, 0]}},
                    "mouth_corner_r": {"rotation": {"0.0": [0, 0, 0], "1.3": [0, 0, -8]}},
                    "mouth_corner_l": {"rotation": {"0.0": [0, 0, 0], "1.3": [0, 0, 8]}},
                    "brow": {"position": {"0.0": [0, 0, 0], "0.8": [0, 0.28, 0], "1.3": [0, 0.35, 0]}},
                    "eye_r": {"rotation": {"0.0": [0, 0, 0], "0.6": [-6, 0, 0], "1.3": [-8, 0, 0]}},
                    "eye_l": {"rotation": {"0.0": [0, 0, 0], "0.6": [-6, 0, 0], "1.3": [-8, 0, 0]}},
                },
            },
            "animation.fc.door.open_hold": {
                "loop": True,
                "bones": {
                    "lower_lip": {"rotation": ["38 + math.sin(query.life_time * 30) * 3", 0, 0]},
                    "upper_lip": {"rotation": ["-11 + math.sin(query.life_time * 30 + 20) * 1.5", 0, 0]},
                    "brow": {"position": [0, "0.32 + math.sin(query.life_time * 50) * 0.06", 0]},
                    "eye_r": {"rotation": ["math.sin(query.life_time * 26) * 3", "math.sin(query.life_time * 19) * 4", 0]},
                    "eye_l": {"rotation": ["math.sin(query.life_time * 26) * 3", "math.sin(query.life_time * 19) * 4", 0]},
                },
            },
        },
    }
    write_json(RP / "animations" / "fc_shared.animation.json", anims)


def emit_animation_controllers():
    """State machines: idle<->walk blending, attack overlay, NPC gestures."""
    ctrl = {
        "format_version": "1.10.0",
        "animation_controllers": {
            "controller.animation.fc.biped_move": {
                "initial_state": "idle",
                "states": {
                    "idle": {"animations": ["idle"], "blend_transition": 0.3, "blend_via_shortest_path": True,
                             "transitions": [{"walk": "query.modified_move_speed > 0.04"}]},
                    "walk": {"animations": ["walk"], "blend_transition": 0.14, "blend_via_shortest_path": True,
                             "transitions": [{"idle": "query.modified_move_speed <= 0.04"}]},
                },
            },
            "controller.animation.npc.move": {
                "initial_state": "idle",
                "states": {
                    "idle": {
                        "animations": ["idle"],
                        "blend_transition": 0.3,
                        "blend_via_shortest_path": True,
                        "transitions": [{"walk": "query.modified_move_speed > 0.02"}],
                    },
                    "walk": {
                        "animations": ["walk"],
                        "blend_transition": 0.14,
                        "blend_via_shortest_path": True,
                        "transitions": [
                            {"run": "query.modified_move_speed > 0.34"},
                            {"idle": "query.modified_move_speed <= 0.02"},
                        ],
                    },
                    "run": {
                        "animations": ["run"],
                        "blend_transition": 0.1,
                        "blend_via_shortest_path": True,
                        "transitions": [{"walk": "query.modified_move_speed <= 0.34"}],
                    },
                },
            },
            "controller.animation.fc.attack": {
                "initial_state": "calm",
                "states": {
                    "calm": {"transitions": [{"strike": "variable.attack_time > 0.0"}]},
                    "strike": {"animations": ["attack"], "blend_transition": 0.1, "blend_via_shortest_path": True,
                               "transitions": [{"calm": "variable.attack_time <= 0.0"}]},
                },
            },
            "controller.animation.fc.gesture": {
                "initial_state": "quiet",
                "states": {
                    "quiet": {"transitions": [
                        {"chat": "math.mod(query.life_time + variable.anim_offset / 22.5, 16) < 4 && query.modified_move_speed < 0.04"}]},
                    "chat": {"animations": ["gesture"], "blend_transition": 0.4, "blend_via_shortest_path": True,
                             "transitions": [
                                 {"quiet": "math.mod(query.life_time + variable.anim_offset / 22.5, 16) >= 4 || query.modified_move_speed >= 0.04"}]},
                },
            },
            "controller.animation.fc.ranged": {
                "initial_state": "calm",
                "states": {
                    "calm": {"transitions": [{"aim": "query.has_target"}]},
                    "aim": {"animations": ["bow"], "blend_transition": 0.2, "blend_via_shortest_path": True,
                            "transitions": [{"calm": "!query.has_target"}]},
                },
            },
            "controller.animation.fc.door": {
                "initial_state": "closed",
                "states": {
                    "closed": {
                        "animations": ["idle"],
                        "transitions": [{"opening": "query.variant == 1"}]
                    },
                    "opening": {
                        "animations": ["open"],
                        "transitions": [{"open": "query.any_animation_finished"}]
                    },
                    "open": {
                        "animations": ["open_hold"]
                    }
                }
            },
        },
    }
    write_json(RP / "animation_controllers" / "fc.animation_controllers.json", ctrl)


PLAN_ANIMS = {
    "humanoid": [("walk", "animation.fc.biped.walk"), ("idle", "animation.fc.biped.idle"),
                 ("attack", "animation.fc.biped.attack"), ("gesture", "animation.fc.biped.gesture"),
                 ("bow", "animation.fc.biped.bow"), ("greet", "animation.fc.biped.greet")],
    "hobbe": [("walk", "animation.fc.hobbe.walk"), ("idle", "animation.fc.hobbe.idle"),
              ("attack", "animation.fc.hobbe.attack"), ("bow", "animation.fc.biped.bow")],
    "twinblade": [("walk", "animation.fc.twinblade.walk"), ("idle", "animation.fc.twinblade.idle"),
                  ("attack", "animation.fc.twinblade.attack")],
    "balverine": [("walk", "animation.fc.quadruped.walk"), ("idle", "animation.fc.quadruped.idle"),
                  ("attack", "animation.fc.quadruped.attack")],
    "troll": [("walk", "animation.fc.troll.walk"), ("idle", "animation.fc.troll.idle"),
              ("attack", "animation.fc.troll.attack")],
    "wasp": [("fly", "animation.fc.fly"), ("hover", "animation.fc.hover")],
    "beetle": [("walk", "animation.fc.beetle.walk"), ("idle", "animation.fc.beetle.idle"),
               ("attack", "animation.fc.beetle.attack")],
    "wraith": [("float", "animation.fc.ghost.float"), ("attack", "animation.fc.ghost.attack")],
    "banshee": [("float", "animation.fc.ghost.float"), ("attack", "animation.fc.ghost.attack")],
    "scorpion": [("walk", "animation.fc.scorpion.walk"), ("idle", "animation.fc.scorpion.idle"),
                 ("attack", "animation.fc.scorpion.attack")],
    "dragon": [("fly", "animation.fc.dragon.fly"), ("attack", "animation.fc.dragon.attack")],
    "nymph": [("fly", "animation.fc.fly"), ("hover", "animation.fc.hover")],
    "jack": [("walk", "animation.fc.biped.walk"), ("idle", "animation.fc.biped.idle"),
             ("attack", "animation.fc.biped.attack")],
    "demon_door": [("idle", "animation.fc.door.idle"),
                   ("open", "animation.fc.door.open"),
                   ("open_hold", "animation.fc.door.open_hold")],
}

# one-shot clips are fired from script (Entity.playAnimation) and must never sit
# in the always-on `animate` list, or the pose freezes on their last keyframe.
ONE_SHOT_ANIMS = {"greet", "spar", "block", "archery_shot"}


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
            # Married NPCs swap to their "wedding finery" skin. The index is the
            # client-synced fc:married property (0 = default skin, 1 = married).
            "controller.render.fc_npc_married": {
                "arrays": {
                    "textures": {"Array.skins": ["Texture.default", "Texture.married"]},
                },
                "geometry": "Geometry.default",
                "materials": [{"*": "Material.default"}],
                "textures": ["Array.skins[math.clamp(query.property('fc:married'), 0, 1)]"],
            },
        },
    }
    write_json(RP / "render_controllers" / "fc.render_controllers.json", rc)


GHOST_PLANS = {"wraith", "banshee"}


def emit_client_entity(mob):
    eid = mob["id"]
    plan = mob["plan"][0]
    anims = PLAN_ANIMS.get(plan, PLAN_ANIMS["humanoid"])
    social_npc = mob.get("behavior") in ("npc", "guard") or eid == "mercenary"
    if plan in {"humanoid", "theresa"} and social_npc:
        anims = [
            ("walk", "animation.npc.walk"),
            ("idle", "animation.npc.idle"),
            ("run", "animation.npc.run"),
            ("attack", "animation.fc.biped.attack"),
            ("gesture", "animation.fc.biped.gesture"),
            ("bow", "animation.fc.biped.bow"),
            ("greet", "animation.fc.biped.greet"),
            ("spar", "animation.npc.spar"),
            ("block", "animation.npc.block"),
            ("archery_shot", "animation.npc.archery_shot"),
        ]
    anim_map = {k: v for k, v in anims}
    keys = [k for k, _ in anims]
    # A mob is biped-driven if it owns both a walk and an idle clip — those feed
    # the idle<->walk controller. Deriving this from the clip set (not a hardcoded
    # plan list) means custom humanoids like Theresa get the blended controllers
    # too, instead of stacking every clip on top of each other at once.
    biped = "walk" in keys and "idle" in keys
    if plan == "demon_door":
        anim_map["ctrl_door"] = "controller.animation.fc.door"
        scripts = {
            "initialize": ["variable.anim_offset = math.random(0, 360);"],
            "animate": ["ctrl_door"],
        }
    elif biped:
        # animation controllers: blended idle/walk + attack overlay (+NPC gestures)
        if social_npc and "run" in anim_map:
            anim_map["ctrl_move"] = "controller.animation.npc.move"
        else:
            anim_map["ctrl_move"] = "controller.animation.fc.biped_move"
        animate = ["ctrl_move"]
        if "attack" in anim_map:                       # only overlay a strike when the plan owns one
            anim_map["ctrl_attack"] = "controller.animation.fc.attack"
            animate.append("ctrl_attack")
        if mob.get("behavior") == "npc":
            anim_map["ctrl_gesture"] = "controller.animation.fc.gesture"
            animate.append("ctrl_gesture")
        if mob.get("behavior") == "ranged" and "bow" in anim_map:
            anim_map["ctrl_ranged"] = "controller.animation.fc.ranged"
            animate.append("ctrl_ranged")
        scripts = {
            "initialize": ["variable.anim_offset = math.random(0, 360);"],
            "animate": animate,
        }
    else:
        # non-biped (flyers, ghosts, dragon): play the plan's looping clips, and overlay
        # the attack controller if a strike clip exists so e.g. the dragon can lunge
        # without owning an idle/walk pair. A raw looping attack clip would otherwise
        # sit on the always-on list and fight the move clip on shared bones.
        animate = [k for k in keys if k not in ONE_SHOT_ANIMS and k != "attack"]
        if "attack" in anim_map:
            anim_map["ctrl_attack"] = "controller.animation.fc.attack"
            animate.append("ctrl_attack")
        scripts = {
            "initialize": ["variable.anim_offset = math.random(0, 360);"],
            "animate": animate,
        }
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
    # MARRIAGE: courtable NPCs get a second "wedding finery" skin, swapped by a
    # render controller keyed on the client-synced fc:married property, plus a
    # gentle scale bump when wed. Ghost NPCs are excluded above by is_romanceable.
    if is_romanceable(mob) and not ghost:
        desc = ce["minecraft:client_entity"]["description"]
        desc["textures"]["married"] = f"textures/entity/{eid}_married"
        desc["render_controllers"] = ["controller.render.fc_npc_married"]
        # NOTE: no Molang-on-scale here. A query-driven `scripts.scale` made the
        # courtable NPCs render invisible (a failed scale expression collapses the
        # model), so the wedding "puff" is dropped — the skin swap, ring and spouse
        # menu carry the upgrade. The skin swap itself is the documented, safe
        # render-controller pattern below.
    write_json(RP / "entity" / f"{eid}.entity.json", ce)


# ---------------------------------------------------------------------------
# ITEM TEXTURE ATLAS + ATTACHABLES
# ---------------------------------------------------------------------------

def emit_item_atlas(items):
    tex_data = {}
    for i in items:
        tex_data[i["id"]] = {"textures": f"textures/items/{i['id']}"}
    tex_data["will_focus"] = {"textures": "textures/items/will_focus"}
    atlas = {
        "resource_pack_name": "fablecraft",
        "texture_name": "atlas.items",
        "texture_data": tex_data,
    }
    write_json(RP / "textures" / "item_texture.json", atlas)


def emit_terrain_atlas():
    write_json(RP / "textures" / "terrain_texture.json", {
        "resource_pack_name": "fablecraft",
        "texture_name": "atlas.terrain",
        "padding": 8, "num_mip_levels": 4,
        "texture_data": {
            "fc_azurite_ore": {"textures": "textures/blocks/azurite_ore"},
        },
    })
    write_json(RP / "blocks.json", {
        "format_version": "1.21.40",
        "fc:azurite_ore": {"sound": "stone"},
    })


# NOTE: the vanilla worn-armor geometries are helmet / chestplate / leggings /
# boots. Using "chest"/"legs" silently fails to bind, so the chestplate and
# leggings render invisible while the (correctly-named) helmet and boots show.
ARMOR_GEO = {
    "helm": ("geometry.humanoid.armor.helmet", "variable.helmet_layer_visible", 1),
    "torso": ("geometry.humanoid.armor.chestplate", "variable.chest_layer_visible", 1),
    "legs": ("geometry.humanoid.armor.leggings", "variable.leg_layer_visible", 2),
    "boots": ("geometry.humanoid.armor.boots", "variable.boot_layer_visible", 1),
}


def emit_attachables(items):
    """Worn armor layers: every fc armor piece renders on the player using
    the painted layer textures."""
    count = 0
    for i in items:
        if i["cat"] != "armor":
            continue
        geo, layer_var, layer_n = ARMOR_GEO[i["slot"]]
        set_id = i["set"]
        att = {
            "format_version": FV_ATTACH,
            "minecraft:attachable": {
                "description": {
                    "identifier": f"{NAMESPACE}:{i['id']}",
                    "materials": {"default": "armor", "enchanted": "armor_enchanted"},
                    "textures": {
                        "default": f"textures/models/armor/fc_{set_id}_layer_{layer_n}",
                        "enchanted": "textures/misc/enchanted_item_glint",
                    },
                    "geometry": {"default": geo},
                    "scripts": {"parent_setup": f"{layer_var} = 0.0;"},
                    "render_controllers": ["controller.render.armor"],
                },
            },
        }
        write_json(RP / "attachables" / f"{i['id']}.json", att)
        count += 1
    return count


def emit_lang(items):
    lines = ["## Fablecraft: Reforged — generated lang", ""]
    for i in items:
        lines.append(f"item.{NAMESPACE}:{i['id']}={i['name']}")
    for m in MOBS:
        lines.append(f"entity.{NAMESPACE}:{m['id']}.name={m['name']}")
        lines.append(f"item.spawn_egg.entity.{NAMESPACE}:{m['id']}.name=Spawn {m['name']}")
    lines += [
        "item.wd:will_focus=Will Focus",
        "entity.wd:evil_horns.name=Horns of Corruption",
        "entity.wd:divine_halo.name=Halo of Avo",
        "fc.hud.title=Fablecraft: Reforged",
        "fc.guild.welcome=Welcome to the Heroes' Guild",
    ]
    write_text(RP / "texts" / "en_US.lang", "\n".join(lines) + "\n")
    write_json(RP / "texts" / "languages.json", ["en_US"])


def emit_alignment_cosmetics():
    horns_geo = {
        "format_version": FV_GEO,
        "minecraft:geometry": [{
            "description": {
                "identifier": "geometry.wd.evil_horns",
                "texture_width": 32,
                "texture_height": 32,
                "visible_bounds_width": 3,
                "visible_bounds_height": 3.5,
                "visible_bounds_offset": [0, 1.25, 0],
            },
            "bones": [
                {
                    "name": "horn_left_base",
                    "pivot": [-3.2, 30.0, 0],
                    "rotation": [0, 0, -18],
                    "cubes": [{
                        "origin": [-4.8, 29.0, -1.6],
                        "size": [2.8, 4.8, 3.2],
                        "uv": [0, 0],
                        "inflate": 0.04,
                    }],
                },
                {
                    "name": "horn_left_mid",
                    "parent": "horn_left_base",
                    "pivot": [-3.6, 33.0, 0],
                    "rotation": [0, 0, -20],
                    "cubes": [{
                        "origin": [-4.7, 32.2, -1.25],
                        "size": [2.1, 4.5, 2.5],
                        "uv": [0, 10],
                    }],
                },
                {
                    "name": "horn_left_tip",
                    "parent": "horn_left_mid",
                    "pivot": [-3.9, 36.0, 0],
                    "rotation": [0, 0, -24],
                    "cubes": [{
                        "origin": [-4.45, 35.3, -0.75],
                        "size": [1.2, 3.7, 1.5],
                        "uv": [16, 0],
                    }],
                },
                {
                    "name": "horn_right_base",
                    "pivot": [3.2, 30.0, 0],
                    "rotation": [0, 0, 18],
                    "cubes": [{
                        "origin": [2.0, 29.0, -1.6],
                        "size": [2.8, 4.8, 3.2],
                        "uv": [0, 0],
                        "inflate": 0.04,
                    }],
                },
                {
                    "name": "horn_right_mid",
                    "parent": "horn_right_base",
                    "pivot": [3.6, 33.0, 0],
                    "rotation": [0, 0, 20],
                    "cubes": [{
                        "origin": [2.6, 32.2, -1.25],
                        "size": [2.1, 4.5, 2.5],
                        "uv": [0, 10],
                    }],
                },
                {
                    "name": "horn_right_tip",
                    "parent": "horn_right_mid",
                    "pivot": [3.9, 36.0, 0],
                    "rotation": [0, 0, 24],
                    "cubes": [{
                        "origin": [3.25, 35.3, -0.75],
                        "size": [1.2, 3.7, 1.5],
                        "uv": [16, 0],
                    }],
                },
            ],
        }],
    }
    write_json(RP / "models" / "entity" / "evil_horns.geo.json", horns_geo)

    halo_bones = []
    for index, angle in enumerate(range(0, 360, 45)):
        halo_bones.append({
            "name": f"halo_segment_{index}",
            "parent": "halo_root",
            "pivot": [0, 35.6, 0],
            "rotation": [0, angle, 0],
            "cubes": [{
                "origin": [-2.05, 35.2, -5.0],
                "size": [4.1, 0.8, 0.8],
                "uv": [0, 0],
                "inflate": 0.08,
            }],
        })
    halo_geo = {
        "format_version": FV_GEO,
        "minecraft:geometry": [{
            "description": {
                "identifier": "geometry.wd.divine_halo",
                "texture_width": 16,
                "texture_height": 16,
                "visible_bounds_width": 3,
                "visible_bounds_height": 3.5,
                "visible_bounds_offset": [0, 1.35, 0],
            },
            "bones": [{
                "name": "halo_root",
                "pivot": [0, 35.6, 0],
            }, *halo_bones],
        }],
    }
    write_json(RP / "models" / "entity" / "divine_halo.geo.json", halo_geo)

    write_json(RP / "animations" / "wd_alignment_cosmetics.animation.json", {
        "format_version": FV_ANIM,
        "animations": {
            "animation.wd.divine_halo.float": {
                "loop": True,
                "bones": {
                    "halo_root": {
                        "position": [0, "math.sin(query.life_time * 90) * 0.35", 0],
                        "rotation": [0, "query.life_time * 24", 0],
                    },
                },
            },
        },
    })

    for entity_id, material, animation in (
        ("evil_horns", "entity_alphatest", None),
        ("divine_halo", "entity_emissive_alpha", "animation.wd.divine_halo.float"),
    ):
        description = {
            "identifier": f"wd:{entity_id}",
            "materials": {"default": material},
            "textures": {"default": f"textures/entity/{entity_id}"},
            "geometry": {"default": f"geometry.wd.{entity_id}"},
            "render_controllers": ["controller.render.fc_default"],
        }
        if animation:
            description["animations"] = {"float": animation}
            description["scripts"] = {"animate": ["float"]}
        write_json(RP / "entity" / f"{entity_id}.entity.json", {
            "format_version": FV_CE,
            "minecraft:client_entity": {
                "description": description,
            },
        })

    horns = Px(32, 32)
    horns.rect(0, 0, 16, 32, (74, 12, 18, 255))
    horns.rect(0, 0, 16, 3, (132, 29, 34, 255))
    horns.rect(0, 13, 16, 4, (46, 7, 12, 255))
    horns.rect(16, 0, 16, 32, (164, 123, 94, 255))
    horns.rect(16, 0, 16, 4, (229, 197, 147, 255))
    horns.rect(16, 18, 16, 5, (104, 65, 55, 255))
    horns.save(RP / "textures" / "entity" / "evil_horns.png")

    halo = Px(16, 16)
    halo.rect(0, 0, 16, 16, (255, 216, 82, 255))
    halo.rect(0, 0, 16, 3, (255, 249, 196, 255))
    halo.rect(0, 10, 16, 3, (238, 157, 28, 255))
    halo.save(RP / "textures" / "entity" / "divine_halo.png")

    write_json(RP / "particles" / "wd_divine_glow.particle.json", {
        "format_version": "1.10.0",
        "particle_effect": {
            "description": {
                "identifier": "wd:divine_glow",
                "basic_render_parameters": {
                    "material": "particles_add",
                    "texture": "textures/particle/particles",
                },
            },
            "components": {
                "minecraft:emitter_local_space": {
                    "position": False,
                    "rotation": False,
                    "velocity": False,
                },
                "minecraft:emitter_lifetime_once": {
                    "active_time": 0.04,
                },
                "minecraft:emitter_rate_instant": {
                    "num_particles": "2 + variable.intensity * 2",
                },
                "minecraft:emitter_shape_sphere": {
                    "radius": 0.28,
                    "direction": [0, 1, 0],
                },
                "minecraft:particle_lifetime_expression": {
                    "max_lifetime": "0.45 + variable.particle_random_1 * 0.5",
                },
                "minecraft:particle_initial_speed": "0.015 + variable.particle_random_1 * 0.035",
                "minecraft:particle_motion_dynamic": {
                    "linear_acceleration": [0, 0.035, 0],
                    "linear_drag_coefficient": 0.12,
                },
                "minecraft:particle_appearance_billboard": {
                    "size": [
                        "variable.size * (0.65 + variable.particle_random_1 * 0.55)",
                        "variable.size * (0.65 + variable.particle_random_2 * 0.55)",
                    ],
                    "facing_camera_mode": "lookat_xyz",
                    "uv": {
                        "texture_width": 128,
                        "texture_height": 128,
                        "uv": [0, 0],
                        "uv_size": [8, 8],
                    },
                },
                "minecraft:particle_appearance_tinting": {
                    "color": [
                        "variable.color.r",
                        "variable.color.g",
                        "variable.color.b",
                        "variable.color.a * (1.0 - variable.particle_age / variable.particle_lifetime)",
                    ],
                },
            },
        },
    })


def main():
    items = fc_data.all_items()
    for mob in MOBS:
        emit_geometry(mob)
        emit_client_entity(mob)
    emit_animations()
    emit_animation_controllers()
    emit_render_controller()
    emit_item_atlas(items)
    emit_terrain_atlas()
    n_att = emit_attachables(items)
    emit_lang(items)
    emit_alignment_cosmetics()
    print(f"emitted RP: {len(MOBS)} geometries + client entities, atlas({len(items)}), "
          f"{n_att} armor attachables, anim controllers, lang, alignment cosmetics")


if __name__ == "__main__":
    main()

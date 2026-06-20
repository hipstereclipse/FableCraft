"""Generate the Fable expression registry, player clips and NPC social assets."""
import json

from fc_emotes import EMOTES
from fc_lib import BP, RP, write_json, write_text


def player_clip(template):
    """Reusable Blockbench-style keyframe templates for the standard player rig."""
    neutral = [0, 0, 0]
    poses = {
        "belch": ([-55, 0, 8], [-12, 0, -4], [8, 0, 0], [0, 0, 0]),
        "fart": ([8, 0, 10], [8, 0, -10], [0, 22, 8], [0, 0, 0]),
        "beckon": ([-75, 0, 12], [0, 0, 0], [0, -8, 0], [0, 0, 0]),
        "halt": ([-92, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0]),
        "laugh": ([-35, 0, 22], [-35, 0, -22], [-8, 0, 0], [-12, 0, 0]),
        "flirt": ([-58, -8, 18], [-10, 0, -8], [0, -12, 0], [0, 0, -4]),
        "cossack": ([-72, -12, 36], [-72, 12, -36], [12, 0, 0], [0, 0, 0]),
        "sneer": ([8, 0, 10], [8, 0, -10], [0, -14, 0], [-8, 0, 0]),
        "arm_pump": ([-135, 0, 20], [-25, 0, -8], [-4, 0, 0], [0, 0, 0]),
        "scary_laugh": ([-72, 0, 35], [-72, 0, -35], [-12, 0, 0], [-18, 0, 0]),
        "hero_pose": ([-40, 0, 22], [-40, 0, -22], [0, 18, 0], [0, 0, 0]),
        "roar": ([-128, 0, 34], [-128, 0, -34], [-12, 0, 0], [-22, 0, 0]),
        "apologise": ([12, 0, 4], [12, 0, -4], [28, 0, 0], [18, 0, 0]),
        "air_guitar": ([-68, -24, 8], [-42, 28, -12], [6, -18, 0], [0, 0, 0]),
        "thanks": ([-42, 0, 4], [-42, 0, -4], [18, 0, 0], [12, 0, 0]),
        "rude": ([-88, 0, 4], [8, 0, 0], [0, -8, 0], [-4, 0, 0]),
        "crotch": ([35, 0, 10], [35, 0, -10], [0, 0, 0], [8, 0, 0]),
        "disco": ([-155, 0, 15], [28, 0, -12], [0, 20, 0], [0, 0, 0]),
        "vulgar": ([26, 0, 10], [26, 0, -10], [0, 0, 0], [18, 0, 0]),
        "kiss_ass": ([30, 0, 16], [30, 0, -16], [35, 0, 0], [12, 0, 0]),
        "tap": ([-25, 0, 18], [-25, 0, -18], [0, 12, 0], [0, 0, 0]),
        "steal": ([-48, -18, 8], [-32, 18, -8], [22, 0, 0], [12, 0, 0]),
        "lockpick": ([-72, -18, 8], [-72, 18, -8], [30, 0, 0], [18, 0, 0]),
        "flamenco": ([-150, 0, 24], [-58, -18, -34], [0, 22, 0], [0, 0, -6]),
        "oracle_yeron": ([-105, -18, 34], [-46, 20, -18], [-6, -12, 0], [0, 10, 0]),
        "oracle_moryk": ([-62, -28, 22], [-122, 12, -38], [-4, 14, 0], [-8, -8, 0]),
        "oracle_calran": ([-132, 18, 28], [-132, -18, -28], [-8, 0, 0], [-12, 0, 0]),
        "oracle_avisto": ([-82, 30, 38], [-82, -30, -38], [-4, 0, 8], [0, 0, 8]),
        "ballet": ([-135, 0, 20], [-135, 0, -20], [0, 28, 0], [0, 0, 0]),
        "chicken": ([-55, 0, 58], [-55, 0, -58], [14, 0, 0], [16, 0, 0]),
        "insult": ([-72, 0, 20], [10, 0, -10], [0, -18, 0], [-8, 0, 0]),
    }
    right, left, body, head = poses[template]
    # Preserve gesture direction in the counter pose. The original generator
    # inverted Y/Z for every clip, which made many arms cross the body or point
    # backward halfway through the expression.
    counter_r = [right[0] * 0.78, right[1] * 0.8, right[2] * 0.82]
    counter_l = [left[0] * 0.78, left[1] * 0.8, left[2] * 0.82]
    counter_overrides = {
        "beckon": ([-68, -24, 14], left),
        "laugh": ([-48, 0, 28], [-48, 0, -28]),
        "flirt": ([-42, 14, 20], [-18, 0, -10]),
        "cossack": ([-42, 18, 42], [-42, -18, -42]),
        "arm_pump": ([-72, 0, 24], [-20, 0, -8]),
        "scary_laugh": ([-92, 0, 42], [-92, 0, -42]),
        "roar": ([-108, 0, 46], [-108, 0, -46]),
        "air_guitar": ([-50, 26, 10], [-70, -24, -14]),
        "thanks": ([-58, -12, 6], [-58, 12, -6]),
        "flamenco": ([-62, 20, 34], [-150, 0, -24]),
        "disco": ([28, 0, 12], [-155, 0, -18]),
        "tap": ([-38, 0, 22], [-12, 0, -20]),
        "steal": ([-62, -8, 12], [-44, 26, -10]),
        "lockpick": ([-82, -10, 10], [-82, 10, -10]),
        "oracle_yeron": ([-72, 22, 30], [-92, -16, -28]),
        "oracle_moryk": ([-118, -10, 34], [-58, 26, -20]),
        "oracle_calran": ([-92, 30, 36], [-92, -30, -36]),
        "oracle_avisto": ([-118, 12, 44], [-54, -24, -28]),
        "ballet": ([-92, 0, 48], [-92, 0, -48]),
        "chicken": ([-72, 0, 64], [-72, 0, -64]),
        "insult": ([-58, -18, 22], [12, 0, -10]),
    }
    if template in counter_overrides:
        counter_r, counter_l = counter_overrides[template]

    leg_poses = {
        "cossack": ([42, 0, -8], [42, 0, 8], [-24, 0, 10], [58, 0, -10]),
        "flamenco": ([-18, 0, 5], [28, 0, -5], [32, 0, -8], [-16, 0, 8]),
        "tap": ([-28, 0, 4], [18, 0, -4], [22, 0, -4], [-30, 0, 4]),
        "disco": ([-18, 0, 0], [24, 0, 0], [26, 0, 0], [-18, 0, 0]),
        "ballet": ([-30, 0, -8], [34, 0, 8], [18, 0, 12], [-12, 0, -12]),
        "chicken": ([22, 0, -6], [22, 0, 6], [-12, 0, 6], [34, 0, -6]),
        "steal": ([28, 0, 0], [24, 0, 0], [18, 0, 0], [34, 0, 0]),
        "lockpick": ([18, 0, 0], [18, 0, 0], [24, 0, 0], [24, 0, 0]),
    }
    leg_a_r, leg_a_l, leg_b_r, leg_b_l = leg_poses.get(
        template, ([8, 0, 0], [-8, 0, 0], [-8, 0, 0], [8, 0, 0])
    )
    return {
        "loop": False,
        "animation_length": 2.0,
        "bones": {
            "rightArm": {"rotation": {"0.0": neutral, "0.25": right,
                                       "1.1": counter_r, "1.75": right, "2.0": neutral}},
            "leftArm": {"rotation": {"0.0": neutral, "0.25": left,
                                      "1.1": counter_l, "1.75": left, "2.0": neutral}},
            "body": {"rotation": {"0.0": neutral, "0.3": body, "1.7": body, "2.0": neutral}},
            "head": {"rotation": {"0.0": neutral, "0.3": head, "1.7": head, "2.0": neutral}},
            "rightLeg": {"rotation": {"0.0": neutral, "0.35": leg_a_r,
                                       "1.1": leg_b_r, "2.0": neutral}},
            "leftLeg": {"rotation": {"0.0": neutral, "0.35": leg_a_l,
                                      "1.1": leg_b_l, "2.0": neutral}},
        },
    }


def npc_animations():
    return {
        "format_version": "1.8.0",
        "animations": {
            "animation.npc.idle": {
                "loop": True,
                "bones": {
                    "body": {
                        "position": [
                            0,
                            "math.sin(query.life_time * 82 + variable.anim_offset) * 0.16",
                            0,
                        ],
                        "rotation": [
                            "math.sin(query.life_time * 74 + variable.anim_offset + 18) * 0.65",
                            "math.sin(query.life_time * 27 + variable.anim_offset) * 1.1",
                            "math.sin(query.life_time * 39 + variable.anim_offset + 70) * 1.25",
                        ],
                    },
                    "head": {
                        "rotation": [
                            "query.target_x_rotation + math.sin(query.life_time * 31 + variable.anim_offset + 25) * 1.4",
                            "query.target_y_rotation + math.sin(query.life_time * 19 + variable.anim_offset) * 3.2",
                            "math.sin(query.life_time * 37 + variable.anim_offset + 90) * 0.8",
                        ]
                    },
                    "arm_r": {"rotation": [
                        "math.sin(query.life_time * 68 + variable.anim_offset) * 2.2",
                        0,
                        "2 + math.sin(query.life_time * 39 + variable.anim_offset + 70) * 1.1",
                    ]},
                    "arm_l": {"rotation": [
                        "-math.sin(query.life_time * 68 + variable.anim_offset + 32) * 2.0",
                        0,
                        "-2 - math.sin(query.life_time * 39 + variable.anim_offset + 70) * 1.1",
                    ]},
                    "leg_r": {"rotation": [
                        "math.sin(query.life_time * 23 + variable.anim_offset) * 0.7",
                        0,
                        "math.sin(query.life_time * 39 + variable.anim_offset + 70) * 0.55",
                    ]},
                    "leg_l": {"rotation": [
                        "-math.sin(query.life_time * 23 + variable.anim_offset) * 0.7",
                        0,
                        "math.sin(query.life_time * 39 + variable.anim_offset + 70) * 0.55",
                    ]},
                },
            },
            # Vanilla-paced stroll. anim_time advances 1:1 with distance moved and the
            # limbs swing at ~38 deg/unit (the same cadence Minecraft's own humanoid walk
            # uses, and what fc.biped.walk uses) — a full stride every ~9 units instead of
            # the frantic ~0.8 of the old 2.4x / 180-coeff version. The amplitude clamp
            # range is tightened (0.6..1.0) so start/stop pathfinding doesn't pulse the
            # swing, which read as the "choppy" part.
            "animation.npc.walk": {
                "loop": True,
                "anim_time_update": "query.modified_distance_moved",
                "bones": {
                    "leg_r": {"rotation": [
                        "math.cos(query.anim_time * 38) * 30 * math.clamp(query.modified_move_speed * 2.5, 0.6, 1.0)",
                        0,
                        0,
                    ]},
                    "leg_l": {"rotation": [
                        "-math.cos(query.anim_time * 38) * 30 * math.clamp(query.modified_move_speed * 2.5, 0.6, 1.0)",
                        0,
                        0,
                    ]},
                    "arm_r": {"rotation": [
                        "-math.cos(query.anim_time * 38 + 8) * 22 * math.clamp(query.modified_move_speed * 2.5, 0.5, 1.0)",
                        0,
                        "2 + math.sin(query.anim_time * 76) * 0.8",
                    ]},
                    "arm_l": {"rotation": [
                        "math.cos(query.anim_time * 38 - 8) * 22 * math.clamp(query.modified_move_speed * 2.5, 0.5, 1.0)",
                        0,
                        "-2 - math.sin(query.anim_time * 76) * 0.8",
                    ]},
                    "body": {
                        "rotation": [
                            "1.5 + math.abs(math.sin(query.anim_time * 38)) * 1.2",
                            "math.sin(query.anim_time * 38) * 2.2",
                            "math.cos(query.anim_time * 38) * 1.8",
                        ],
                        "position": [
                            0,
                            "math.abs(math.sin(query.anim_time * 38)) * 0.38 * math.clamp(query.modified_move_speed * 2.5, 0.6, 1.0)",
                            0,
                        ],
                    },
                    "head": {
                        "rotation": [
                            "query.target_x_rotation - math.abs(math.sin(query.anim_time * 38)) * 1.0",
                            "query.target_y_rotation - math.sin(query.anim_time * 38) * 1.0",
                            "-math.cos(query.anim_time * 38) * 0.6",
                        ]
                    },
                },
            },
            # run = same 38-coeff cadence (so walk<->run blends without a frequency pop)
            # but a bigger stride and a forward lean; it reads faster because the entity
            # covers ground faster, not because the legs whirl.
            "animation.npc.run": {
                "loop": True,
                "anim_time_update": "query.modified_distance_moved",
                "bones": {
                    "leg_r": {"rotation": ["math.cos(query.anim_time * 38) * 44", 0, 0]},
                    "leg_l": {"rotation": ["-math.cos(query.anim_time * 38) * 44", 0, 0]},
                    "arm_r": {"rotation": [
                        "-math.cos(query.anim_time * 38 + 10) * 36 - 14",
                        "math.sin(query.anim_time * 38) * 4",
                        5,
                    ]},
                    "arm_l": {"rotation": [
                        "math.cos(query.anim_time * 38 - 10) * 36 - 14",
                        "-math.sin(query.anim_time * 38) * 4",
                        -5,
                    ]},
                    "body": {
                        "rotation": [
                            "12 + math.abs(math.sin(query.anim_time * 38)) * 2",
                            "math.sin(query.anim_time * 38) * 3",
                            "math.cos(query.anim_time * 38) * 2.6",
                        ],
                        "position": [
                            0,
                            "math.abs(math.sin(query.anim_time * 38)) * 0.5",
                            "math.cos(query.anim_time * 76) * 0.06",
                        ],
                    },
                    "head": {"rotation": [
                        "query.target_x_rotation - 8 - math.abs(math.sin(query.anim_time * 38)) * 1.2",
                        "query.target_y_rotation - math.sin(query.anim_time * 38) * 1.4",
                        "-math.cos(query.anim_time * 38) * 1.0",
                    ]},
                },
            },
            "animation.npc.spar": {
                "loop": False,
                "animation_length": 1.0,
                "bones": {
                    "body": {"rotation": {
                        "0.0": [0, 0, 0], "0.18": [-5, 18, -3],
                        "0.42": [9, -24, 5], "0.68": [4, -10, 2], "1.0": [0, 0, 0],
                    }},
                    "head": {"rotation": {
                        "0.0": [0, 0, 0], "0.18": [2, -10, 0],
                        "0.42": [-5, 13, -2], "1.0": [0, 0, 0],
                    }},
                    "arm_r": {"rotation": {
                        "0.0": [0, 0, 2], "0.18": [-126, -18, 30],
                        "0.42": [-38, 28, -12], "0.68": [-18, 8, 4],
                        "1.0": [0, 0, 2],
                    }},
                    "arm_l": {"rotation": {
                        "0.0": [0, 0, -2], "0.18": [-48, 12, -20],
                        "0.42": [-72, -16, 18], "0.68": [-32, -5, -8],
                        "1.0": [0, 0, -2],
                    }},
                    "leg_r": {"rotation": {
                        "0.0": [0, 0, 0], "0.18": [-12, 0, 5],
                        "0.42": [18, 0, -4], "1.0": [0, 0, 0],
                    }},
                    "leg_l": {"rotation": {
                        "0.0": [0, 0, 0], "0.18": [14, 0, -5],
                        "0.42": [-8, 0, 4], "1.0": [0, 0, 0],
                    }},
                },
            },
            "animation.npc.block": {
                "loop": False,
                "animation_length": 1.0,
                "bones": {
                    "body": {
                        "rotation": {
                            "0.0": [0, 0, 0], "0.3": [12, -8, -4],
                            "0.55": [16, -12, -6], "1.0": [0, 0, 0],
                        },
                        "position": {
                            "0.0": [0, 0, 0], "0.55": [0, -0.25, 0.18],
                            "1.0": [0, 0, 0],
                        },
                    },
                    "head": {"rotation": {
                        "0.0": [0, 0, 0], "0.3": [8, 8, 3],
                        "0.55": [12, 12, 5], "1.0": [0, 0, 0],
                    }},
                    "arm_r": {"rotation": {
                        "0.0": [0, 0, 2], "0.2": [-96, -20, 36],
                        "0.55": [-110, -12, 42], "1.0": [0, 0, 2],
                    }},
                    "arm_l": {"rotation": {
                        "0.0": [0, 0, -2], "0.2": [-96, 20, -36],
                        "0.55": [-110, 12, -42], "1.0": [0, 0, -2],
                    }},
                    "leg_r": {"rotation": {
                        "0.0": [0, 0, 0], "0.3": [12, 0, 4], "1.0": [0, 0, 0],
                    }},
                    "leg_l": {"rotation": {
                        "0.0": [0, 0, 0], "0.3": [18, 0, -4], "1.0": [0, 0, 0],
                    }},
                },
            },
            "animation.npc.archery_shot": {
                "loop": False,
                "animation_length": 1.2,
                "bones": {
                    "body": {"rotation": {
                        "0.0": [0, 0, 0], "0.3": [2, -12, 0],
                        "0.82": [2, -12, 0], "1.2": [0, 0, 0],
                    }},
                    "head": {"rotation": {
                        "0.0": [0, 0, 0], "0.3": [-4, 8, 0],
                        "0.82": [-4, 8, 0], "1.2": [0, 0, 0],
                    }},
                    "arm_l": {"rotation": {
                        "0.0": [0, 0, -2], "0.28": [-92, 6, -8],
                        "0.82": [-92, 6, -8], "0.94": [-74, 4, -6],
                        "1.2": [0, 0, -2],
                    }},
                    "arm_r": {"rotation": {
                        "0.0": [0, 0, 2], "0.28": [-82, -42, 22],
                        "0.82": [-82, -42, 22], "0.9": [-58, 18, -8],
                        "1.2": [0, 0, 2],
                    }},
                    "leg_r": {"rotation": {
                        "0.0": [0, 0, 0], "0.3": [-5, 0, 4], "1.2": [0, 0, 0],
                    }},
                    "leg_l": {"rotation": {
                        "0.0": [0, 0, 0], "0.3": [7, 0, -4], "1.2": [0, 0, 0],
                    }},
                },
            },
            "animation.npc.cower": {
                "loop": True,
                "bones": {
                    "body": {"rotation": [28, 0, 0], "position": [0, -1.2, 0]},
                    "head": {"rotation": [22, 0, 0]},
                    "arm_r": {"rotation": [-125, 0, 28]},
                    "arm_l": {"rotation": [-125, 0, -28]},
                    "leg_r": {"rotation": [18, 0, 0]},
                    "leg_l": {"rotation": [18, 0, 0]},
                },
            },
            "animation.npc.laugh": {
                "loop": True,
                "bones": {
                    "body": {"rotation": ["8 + math.sin(query.life_time * 260) * 6", 0, 0]},
                    "head": {"rotation": ["-12 + math.sin(query.life_time * 260) * 5", 0, 0]},
                    "arm_r": {"rotation": [-42, 0, 24]},
                    "arm_l": {"rotation": [-42, 0, -24]},
                },
            },
            "animation.npc.clap": {
                "loop": True,
                "bones": {
                    "arm_r": {"rotation": [-72, "18 + math.sin(query.life_time * 500) * 16", 8]},
                    "arm_l": {"rotation": [-72, "-18 - math.sin(query.life_time * 500) * 16", -8]},
                    "body": {"position": [0, "math.abs(math.sin(query.life_time * 250)) * 0.25", 0]},
                },
            },
            "animation.npc.cheer": {
                "loop": True,
                "bones": {
                    "arm_r": {"rotation": ["-145 + math.sin(query.life_time * 250) * 18", 0, 24]},
                    "arm_l": {"rotation": ["-145 - math.sin(query.life_time * 250) * 18", 0, -24]},
                    "body": {"position": [0, "math.abs(math.sin(query.life_time * 250)) * 0.45", 0]},
                },
            },
            "animation.npc.angry": {
                "loop": True,
                "bones": {
                    "body": {"rotation": [8, 0, 0]},
                    "head": {"rotation": [-12, 0, 0]},
                    "arm_r": {"rotation": [-68, 0, 14]},
                    "arm_l": {"rotation": [-68, 0, -14]},
                },
            },
        },
    }


def reference_geometry():
    return {
        "format_version": "1.12.0",
        "minecraft:geometry": [{
            "description": {
                "identifier": "geometry.fable.npc",
                "texture_width": 64,
                "texture_height": 64,
                "visible_bounds_width": 3,
                "visible_bounds_height": 4,
                "visible_bounds_offset": [0, 1.5, 0],
            },
            "bones": [
                {"name": "body", "pivot": [0, 12, 0],
                 "cubes": [{"origin": [-4, 12, -2], "size": [8, 12, 4], "uv": [16, 16]}]},
                {"name": "head", "parent": "body", "pivot": [0, 24, 0],
                 "cubes": [{"origin": [-4, 24, -4], "size": [8, 8, 8], "uv": [0, 0]}]},
                {"name": "arm_r", "parent": "body", "pivot": [-5, 22, 0],
                 "cubes": [{"origin": [-8, 12, -2], "size": [4, 12, 4], "uv": [40, 16]}]},
                {"name": "arm_l", "parent": "body", "pivot": [5, 22, 0],
                 "cubes": [{"origin": [4, 12, -2], "size": [4, 12, 4], "uv": [40, 16],
                            "mirror": True}]},
                {"name": "leg_r", "pivot": [-2, 12, 0],
                 "cubes": [{"origin": [-4, 0, -2], "size": [4, 12, 4], "uv": [0, 16]}]},
                {"name": "leg_l", "pivot": [2, 12, 0],
                 "cubes": [{"origin": [0, 0, -2], "size": [4, 12, 4], "uv": [0, 16],
                            "mirror": True}]},
            ],
        }],
    }


def emit_registry():
    write_json(BP / "config" / "fable_emotes.json", {
        "format_version": 1,
        "camera": {
            "preset": "minecraft:third_person",
            "durationTicks": 40,
            "restore": "clear_to_player_default",
        },
        "ratingAxes": {
            "fc:love_hate": {"min": -100, "max": 100, "negative": "Hate", "positive": "Love"},
            "fc:fear_funny": {"min": -100, "max": 100, "negative": "Funny", "positive": "Fear"},
            "fc:ugly_attractive": {
                "min": -100, "max": 100, "negative": "Ugly", "positive": "Attractive"
            },
        },
        "emotes": EMOTES,
    })
    js = (
        "// Generated by scripts/gen_emotes.py. Do not edit by hand.\n"
        f"export const FABLE_EMOTES = {json.dumps(EMOTES, ensure_ascii=False, indent=2)};\n"
        "export const FABLE_EMOTE_BY_ID = new Map(FABLE_EMOTES.map((entry) => [entry.id, entry]));\n"
    )
    write_text(BP / "scripts" / "fable_emote_registry.js", js)


def main():
    emit_registry()
    write_json(RP / "animations" / "fable_player_emotes.animation.json", {
        "format_version": "1.8.0",
        "animations": {e["animation"]: player_clip(e["template"]) for e in EMOTES},
    })
    write_json(RP / "animations" / "fable_npc.animation.json", npc_animations())
    write_json(RP / "models" / "entity" / "fable_npc.geo.json", reference_geometry())
    print("emitted 31 Fable expressions, player clips, NPC movement/reactions and reference rig")


if __name__ == "__main__":
    main()

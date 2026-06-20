"""Render offline preview cards for every Fable expression.

The renderer reads the generated registry and animation JSON, then poses the
same NPC geometry and textures used by the resource pack. It produces:

  screenshots/expressions/<expression_id>.png
  screenshots/gallery/expressions.png
  screenshots/expressions/INDEX.md

Usage:
  python scripts/gen_expression_previews.py
  python scripts/gen_expression_previews.py --models barkeep,guard_bowerstone,lady_grey
"""
import argparse
import json
import math
from pathlib import Path

from PIL import Image, ImageDraw

from fc_lib import BP, RP, SHOTS
from fc_mobs import MOBS, build_parts, pack_uvs
from gen_screenshots import (
    MOB_MOOD,
    add,
    backdrop,
    contact_sheet,
    cube_quads,
    load_font,
    render_quads,
    rot_x,
    rot_y,
    sub,
)


REGISTRY = BP / "config" / "fable_emotes.json"
ANIMATIONS = RP / "animations" / "fable_player_emotes.animation.json"
ENTITY_TEXTURES = RP / "textures" / "entity"
OUT = SHOTS / "expressions"

DEFAULT_MODELS = [
    "villager_albion",
    "villager_woman",
    "villager_farmer",
    "villager_tailor",
    "villager_blacksmith",
    "villager_fisher",
    "barkeep",
    "trader",
    "guard_bowerstone",
    "guard_oakvale",
    "guard_snowspire",
    "guildmaster",
    "guild_apprentice_might",
    "guild_apprentice_skill",
    "guild_apprentice_will",
    "lady_grey",
    "briar_rose",
    "mercenary",
    "maze",
    "theresa",
]

BONE_MAP = {
    "rightarm": "arm_r",
    "rightArm": "arm_r",
    "leftarm": "arm_l",
    "leftArm": "arm_l",
    "rightleg": "leg_r",
    "rightLeg": "leg_r",
    "leftleg": "leg_l",
    "leftLeg": "leg_l",
    "body": "body",
    "head": "head",
}

CATEGORY_MOOD = {
    "friendly": "holy",
    "romantic": "royal",
    "funny": "forest",
    "scary": "fire",
    "rude": "dark",
    "criminal": "stone",
    "oracle": "frost",
}

CATEGORY_COLOR = {
    "friendly": (112, 190, 118, 255),
    "romantic": (220, 118, 174, 255),
    "funny": (228, 190, 76, 255),
    "scary": (208, 82, 58, 255),
    "rude": (174, 92, 74, 255),
    "criminal": (150, 150, 158, 255),
    "oracle": (112, 198, 220, 255),
}


def load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def rotate_z(point, angle):
    c, s = math.cos(angle), math.sin(angle)
    return (
        point[0] * c - point[1] * s,
        point[0] * s + point[1] * c,
        point[2],
    )


def interpolate(a, b, amount):
    return [a[i] + (b[i] - a[i]) * amount for i in range(3)]


def sample_track(track, time):
    """Sample a Blockbench vector track at a specific animation time."""
    if isinstance(track, list):
        return [float(v) for v in track]
    if not isinstance(track, dict) or not track:
        return [0.0, 0.0, 0.0]

    frames = sorted((float(key), value) for key, value in track.items())
    if time <= frames[0][0]:
        return [float(v) for v in frames[0][1]]
    if time >= frames[-1][0]:
        return [float(v) for v in frames[-1][1]]

    for index in range(1, len(frames)):
        t1, v1 = frames[index]
        if time > t1:
            continue
        t0, v0 = frames[index - 1]
        amount = (time - t0) / max(0.0001, t1 - t0)
        return interpolate(v0, v1, amount)
    return [0.0, 0.0, 0.0]


def sample_pose(animation, time):
    pose = {}
    for player_bone, tracks in animation.get("bones", {}).items():
        npc_bone = BONE_MAP.get(player_bone)
        if not npc_bone:
            continue
        pose[npc_bone] = {
            "rotation": sample_track(tracks.get("rotation", [0, 0, 0]), time),
            "position": sample_track(tracks.get("position", [0, 0, 0]), time),
        }
    return pose


def posed_mob_quads(mob, pose):
    """Convert a generated mob into textured quads with animation transforms."""
    parts = build_parts(mob)
    _, _, uvmap = pack_uvs(parts)
    texture = Image.open(ENTITY_TEXTURES / f"{mob['id']}.png").convert("RGBA")
    by_name = {part["name"]: part for part in parts}
    glowy = mob["plan"][0] in ("wraith", "banshee", "nymph") or mob["id"] == "oracle"
    quads = []

    def transform_node(node, point):
        animation = pose.get(node["name"], {})
        rest = node.get("rot", [0, 0, 0])
        animated = animation.get("rotation", [0, 0, 0])
        # Bedrock animation JSON uses the opposite Euler handedness from this
        # renderer's right-handed matrix helpers. Rest geometry already uses
        # renderer-space rotations, so invert only the sampled animation delta.
        rx, ry, rz = [
            math.radians(rest[i] - animated[i])
            for i in range(3)
        ]
        pivot = node["pivot"]
        point = sub(point, pivot)
        if rz:
            point = rotate_z(point, rz)
        if ry:
            point = rot_y(point, ry)
        if rx:
            point = rot_x(point, rx)
        point = add(point, pivot)
        offset = animation.get("position", [0, 0, 0])
        return add(point, offset)

    def chain_transform(part, point):
        node = part
        while node is not None:
            point = transform_node(node, point)
            node = by_name.get(node.get("parent"))
        return point

    for part_index, part in enumerate(parts):
        for cube_index, cube in enumerate(part["cubes"]):
            quads += cube_quads(
                cube["origin"],
                cube["size"],
                uvmap[(part_index, cube_index)],
                texture,
                inflate=cube.get("inflate", 0.0),
                xform=lambda point, active=part: chain_transform(active, point),
                glow=glowy,
            )
    return quads


def model_for_expression(models, expression, index):
    """Use category-biased casting while still rotating through the full roster."""
    preferred = {
        "romantic": ["lady_grey", "villager_woman", "theresa", "briar_rose"],
        "scary": ["guard_bowerstone", "mercenary", "guildmaster", "guard_snowspire"],
        "rude": ["barkeep", "guard_oakvale", "villager_blacksmith", "mercenary"],
        "criminal": ["mercenary", "briar_rose", "trader"],
        "oracle": ["maze", "theresa", "guild_apprentice_will"],
        "friendly": ["villager_albion", "guildmaster", "trader", "villager_farmer"],
        "funny": ["barkeep", "villager_fisher", "guild_apprentice_might", "villager_tailor"],
    }
    available = {mob["id"]: mob for mob in models}
    choices = [available[mid] for mid in preferred.get(expression["category"], []) if mid in available]
    if choices:
        return choices[index % len(choices)]
    return models[index % len(models)]


def unlock_label(unlock):
    kind = unlock["type"]
    if kind == "start":
        return "Available from start"
    if kind == "renown":
        return f"Renown rank {unlock['rank']}"
    if kind == "alignment":
        if "min" in unlock:
            return f"Good alignment {unlock['min']}+"
        return f"Evil alignment {abs(unlock['max'])}+"
    if kind == "guile":
        return f"Guile level {unlock['level']}"
    if kind == "quest":
        return "Complete Find the Oracle"
    if kind == "challenge":
        return "Chicken Kicking champion"
    return kind.title()


def effect_label(effect):
    values = [
        ("Love", effect.get("loveHate", 0)),
        ("Fear", effect.get("fearFunny", 0)),
        ("Looks", effect.get("uglyAttractive", 0)),
    ]
    return "  ".join(f"{name} {value:+d}" for name, value in values)


def expression_card(expression, animation, mob, size=(900, 1000)):
    """Render two key moments so motion-heavy expressions remain readable."""
    mood = CATEGORY_MOOD.get(expression["category"], MOB_MOOD.get(mob["id"], "stone"))
    width, height = size
    card = backdrop(size, mood)
    draw = ImageDraw.Draw(card)
    accent = CATEGORY_COLOR.get(expression["category"], (210, 190, 150, 255))

    # Pose A is the primary held pose; pose B shows the counter-motion used by
    # dances, laughs and gestures.
    times = (0.42, 1.10)
    panel_width = (width - 78) // 2
    panel_height = 690
    panel_y = 78

    for panel_index, time in enumerate(times):
        pose = sample_pose(animation, time)
        quads = posed_mob_quads(mob, pose)
        render = render_quads(
            quads,
            size=(panel_width, panel_height),
            yaw=math.pi - (0.58 if panel_index == 0 else 0.78),
            pitch=0.24,
            rim=True,
            shadow=True,
        )
        x = 24 + panel_index * (panel_width + 30)
        draw.rounded_rectangle(
            [x, panel_y, x + panel_width, panel_y + panel_height],
            radius=16,
            fill=(24, 20, 18, 105),
            outline=accent[:3] + (185,),
            width=2,
        )
        card.alpha_composite(render, (x, panel_y))
        draw.text(
            (x + panel_width / 2, panel_y + panel_height - 24),
            f"POSE {'A' if panel_index == 0 else 'B'}",
            font=load_font(15),
            fill=accent,
            anchor="mm",
        )

    draw.rounded_rectangle(
        [24, 20, width - 24, 66],
        radius=14,
        fill=(25, 20, 18, 220),
        outline=accent,
        width=2,
    )
    draw.text(
        (width / 2, 43),
        expression["category"].upper(),
        font=load_font(19),
        fill=accent,
        anchor="mm",
    )

    band_y = 790
    draw.rounded_rectangle(
        [24, band_y, width - 24, height - 24],
        radius=18,
        fill=(30, 23, 19, 238),
        outline=(190, 156, 96, 255),
        width=3,
    )
    draw.text(
        (width / 2, band_y + 48),
        expression["name"],
        font=load_font(40),
        fill=(242, 221, 174, 255),
        anchor="mm",
    )
    draw.text(
        (width / 2, band_y + 96),
        f"Model: {mob['name']}  |  {unlock_label(expression['unlock'])}",
        font=load_font(20),
        fill=(190, 172, 140, 255),
        anchor="mm",
    )
    draw.text(
        (width / 2, band_y + 139),
        effect_label(expression["effect"]),
        font=load_font(19),
        fill=accent,
        anchor="mm",
    )
    return card


def resolve_models(model_ids):
    by_id = {mob["id"]: mob for mob in MOBS}
    models = []
    for model_id in model_ids:
        mob = by_id.get(model_id)
        if not mob:
            raise SystemExit(f"Unknown NPC model: {model_id}")
        parts = {part["name"] for part in build_parts(mob)}
        required = {"head", "body", "arm_r", "arm_l", "leg_r", "leg_l"}
        if not required.issubset(parts):
            raise SystemExit(f"NPC model {model_id} is not a compatible humanoid rig")
        models.append(mob)
    if not models:
        raise SystemExit("At least one NPC model is required")
    return models


def write_index(rows):
    lines = [
        "# Fable expression previews",
        "",
        "Generated by `python scripts/gen_expression_previews.py` from the current",
        "expression registry, animation JSON, NPC geometry and entity textures.",
        "",
        "| Expression | Category | NPC model | Preview |",
        "|---|---|---|---|",
    ]
    for expression, mob in rows:
        lines.append(
            f"| {expression['name']} | {expression['category'].title()} | "
            f"{mob['name']} | [{expression['id']}.png]({expression['id']}.png) |"
        )
    (OUT / "INDEX.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--models",
        default=",".join(DEFAULT_MODELS),
        help="Comma-separated NPC IDs to use as preview models",
    )
    args = parser.parse_args()

    registry = load_json(REGISTRY)
    animations = load_json(ANIMATIONS)["animations"]
    models = resolve_models([value.strip() for value in args.models.split(",") if value.strip()])

    OUT.mkdir(parents=True, exist_ok=True)
    (SHOTS / "gallery").mkdir(parents=True, exist_ok=True)
    thumbnails = []
    index_rows = []

    for index, expression in enumerate(registry["emotes"]):
        animation = animations.get(expression["animation"])
        if not animation:
            raise SystemExit(f"Missing animation: {expression['animation']}")
        mob = model_for_expression(models, expression, index)
        card = expression_card(expression, animation, mob)
        path = OUT / f"{expression['id']}.png"
        card.convert("RGB").save(path, quality=94)
        thumbnails.append((card, expression["name"]))
        index_rows.append((expression, mob))
        print(f"  {expression['id']:22s} -> {mob['id']}")

    contact_sheet(
        thumbnails,
        cols=5,
        cell=250,
        title="FABLECRAFT - 31 EXPRESSIONS",
        path=SHOTS / "gallery" / "expressions.png",
    )
    write_index(index_rows)
    print(f"rendered {len(index_rows)} expression cards -> {OUT}")
    print(f"contact sheet -> {SHOTS / 'gallery' / 'expressions.png'}")


if __name__ == "__main__":
    main()

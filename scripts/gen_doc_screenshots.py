"""gen_doc_screenshots.py - render documentation showcase screenshots.

Builds a deterministic set of README-ready promo images. Most scenes are real
3D renders of the addon's structures with mob models and spell-effect quads
composited directly into the voxel scene (via the same painter's-algorithm
renderer used for the gallery); a handful of UI/inventory mockups and the
recipe/collage scenes round out the set.
"""
import math

from PIL import Image, ImageDraw, ImageFont

from fc_lib import ROOT, SHOTS, rng
from gen_screenshots import (
    backdrop, render_structure, mob_quads, cube_quads, rot_y,
    ENT_TEX, ITEM_TEX,
)
from fc_mobs import MOBS
import gen_structures as GS

DOC_DIR = SHOTS / "docs"
ITEM_TEX_DIR = ITEM_TEX
SOUND_DIR = ROOT / "sound_preview"
MISSING_ASSETS = []
TITLE_BAND_H = 132
CONTENT_BOTTOM_PAD = TITLE_BAND_H + 26
OUT_SIZE = (1920, 1080)
RENDER_SIZE = 2560

MOB_BY_ID = {m["id"]: m for m in MOBS}

STRUCTURE_BUILDERS = {
    "guild_hall": GS.guild_hall,
    "witchwood_stones": GS.witchwood_stones,
    "graveyard": GS.graveyard,
    "darkwood_camp": GS.darkwood_camp,
    "bandit_camp": GS.bandit_camp,
    "temple_avo": GS.temple_avo,
    "bowerstone_market": GS.bowerstone_market,
    "focus_site": GS.focus_site,
    "demon_door_arch": GS.demon_door_arch,
}

STRUCT_MOOD = {
    "guild_hall": "holy",
    "witchwood_stones": "dark",
    "graveyard": "swamp",
    "darkwood_camp": "forest",
    "bandit_camp": "fire",
    "temple_avo": "holy",
    "bowerstone_market": "stone",
    "focus_site": "dark",
    "demon_door_arch": "dark",
}

_VOX_CACHE = {}
_BACKDROP_CACHE = {}


# ---------------------------------------------------------------------------
# 3D scene compositing
# ---------------------------------------------------------------------------

def get_vox(name):
    if name not in _VOX_CACHE:
        builder = STRUCTURE_BUILDERS[name]
        captured = {}
        orig_save = GS.Vox.save
        GS.Vox.save = lambda self, nm: captured.setdefault(nm, self)
        try:
            builder()
        finally:
            GS.Vox.save = orig_save
        _VOX_CACHE[name] = next(iter(captured.values()))
    return _VOX_CACHE[name]


def cached_backdrop(size, mood):
    key = (size, mood)
    if key not in _BACKDROP_CACHE:
        _BACKDROP_CACHE[key] = backdrop(size, mood)
    return _BACKDROP_CACHE[key].copy()


def place_mob(mob_id, pos, scale=0.062, yaw=0.0):
    """Return extra_quads for a mob model placed in structure block-space."""
    mob = MOB_BY_ID.get(mob_id)
    tex_path = ENT_TEX / f"{mob_id}.png"
    if mob is None or not tex_path.exists():
        MISSING_ASSETS.append(f"mob:{mob_id}")
        return []
    px, py, pz = pos
    out = []
    for corners, tex, uvs, glow in mob_quads(mob):
        new_corners = []
        for c in corners:
            p = (c[0] * scale, c[1] * scale, c[2] * scale)
            if yaw:
                p = rot_y(p, yaw)
            new_corners.append((p[0] + px, p[1] + py, p[2] + pz))
        out.append((new_corners, tex, uvs, glow))
    return out


def _flat_tex(color):
    return Image.new("RGBA", (2, 2), color)


def fireball_fx(center, target=None, seed="fireball"):
    """Layered glowing core + embers + a streak toward a target."""
    r = rng("docfx", seed)
    cx, cy, cz = center
    quads = []
    for color, size in (((255, 224, 140, 255), 0.55), ((255, 150, 50, 255), 0.85),
                         ((220, 70, 24, 235), 1.15)):
        tex = _flat_tex(color)
        quads += cube_quads((cx - size / 2, cy - size / 2, cz - size / 2),
                             (size, size, size), (0, 0), tex, glow=True)
    for _ in range(12):
        ang = r.uniform(0, 2 * math.pi)
        dist = r.uniform(0.5, 1.6)
        ex = cx + math.cos(ang) * dist
        ez = cz + math.sin(ang) * dist
        ey = cy + r.uniform(-0.4, 1.1)
        s = r.uniform(0.08, 0.22)
        tex = _flat_tex((255, r.randint(110, 210), r.randint(20, 90), 255))
        quads += cube_quads((ex - s / 2, ey - s / 2, ez - s / 2), (s, s, s), (0, 0), tex, glow=True)
    if target:
        tx, ty, tz = target
        steps = 5
        for i in range(steps):
            t = (i + 1) / (steps + 1)
            sx = cx + (tx - cx) * t
            sy = cy + (ty - cy) * t
            sz = cz + (tz - cz) * t
            s = 0.5 - 0.3 * t
            tex = _flat_tex((255, 190 - int(60 * t), 60, 255))
            quads += cube_quads((sx - s / 2, sy - s / 2, sz - s / 2), (s, s, s), (0, 0), tex, glow=True)
    return quads


def slow_time_fx(center, radius=4.0):
    """A ring of pale-blue glowing motes at ground level plus a sparser dome."""
    cx, cy, cz = center
    quads = []
    ring_tex = _flat_tex((210, 235, 255, 230))
    for i in range(28):
        ang = math.radians(i * (360 / 28))
        x = cx + math.cos(ang) * radius
        z = cz + math.sin(ang) * radius
        s = 0.4
        quads += cube_quads((x - s / 2, cy - 0.45, z - s / 2), (s, 0.12, s), (0, 0), ring_tex, glow=True)
    dome_tex = _flat_tex((225, 242, 255, 130))
    for i in range(16):
        ang = math.radians(i * (360 / 16) + 11)
        x = cx + math.cos(ang) * radius * 0.78
        z = cz + math.sin(ang) * radius * 0.78
        s = 0.32
        quads += cube_quads((x - s / 2, cy + radius * 0.55, z - s / 2), (s, s, s), (0, 0), dome_tex, glow=True)
    return quads


def holy_glow_fx(center, height=4.5):
    """A vertical column of pale-gold light plus radiating rays."""
    cx, cy, cz = center
    quads = []
    beam_tex = _flat_tex((255, 244, 200, 210))
    steps = int(height * 2)
    for i in range(steps):
        y = cy + i * 0.5
        s = max(0.18, 0.6 - 0.5 * (i / steps))
        quads += cube_quads((cx - s / 2, y, cz - s / 2), (s, 0.42, s), (0, 0), beam_tex, glow=True)
    ray_tex = _flat_tex((255, 250, 215, 150))
    for i in range(6):
        ang = math.radians(i * 60)
        dx, dz = math.cos(ang) * 1.6, math.sin(ang) * 1.6
        x0, x1 = sorted((cx, cx + dx))
        z0, z1 = sorted((cz, cz + dz))
        quads += cube_quads((x0, cy + 0.3, z0), (max(0.18, x1 - x0), 0.12, max(0.18, z1 - z0)), (0, 0), ray_tex, glow=True)
    return quads


def compose_structure_scene(struct_name, mobs=(), effects=(), mood=None, veil=None,
                             yaw=None, pitch=None, crop_offset=(0, 0)):
    """Render a real structure with mobs/effects composited in, cropped to a
    16:9 close-up so creatures read clearly (not a tiny dollhouse view)."""
    vox = get_vox(struct_name)
    extra = []
    for mob_id, pos, kwargs in mobs:
        extra += place_mob(mob_id, pos, **kwargs)
    for fx in effects:
        extra += fx
    kw = {}
    if yaw is not None:
        kw["yaw"] = yaw
    if pitch is not None:
        kw["pitch"] = pitch
    render = render_structure(vox, size=(RENDER_SIZE, RENDER_SIZE), extra_quads=extra, **kw)
    canvas = cached_backdrop((RENDER_SIZE, RENDER_SIZE), mood or STRUCT_MOOD.get(struct_name, "stone"))
    canvas.alpha_composite(render)
    if veil:
        canvas.alpha_composite(Image.new("RGBA", canvas.size, veil))
    ow, oh = OUT_SIZE
    cx = (RENDER_SIZE - ow) // 2 + crop_offset[0] + 0
    cy = (RENDER_SIZE - oh) // 2 + crop_offset[1] + 220
    cx = max(0, min(RENDER_SIZE - ow, cx))
    cy = max(0, min(RENDER_SIZE - oh, cy))
    return canvas.crop((cx, cy, cx + ow, cy + oh))


# ---------------------------------------------------------------------------
# Overlays
# ---------------------------------------------------------------------------

def load_font(size, bold=False):
    names = ["seguisb.ttf", "segoeuib.ttf", "arialbd.ttf"] if bold else ["segoeui.ttf", "arial.ttf"]
    for name in names:
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def fit_image(img, max_size, resample=Image.Resampling.LANCZOS):
    w, h = img.size
    scale = min(max_size[0] / max(1, w), max_size[1] / max(1, h))
    target = (max(1, int(w * scale)), max(1, int(h * scale)))
    return img.resize(target, resample)


def add_item_tray(canvas, item_ids, label=None, corner="br"):
    """Small inset panel showing relevant item icons over a 3D scene."""
    items = []
    for iid in item_ids:
        p = ITEM_TEX_DIR / f"{iid}.png"
        if p.exists():
            items.append(Image.open(p).convert("RGBA"))
        else:
            MISSING_ASSETS.append(f"item:{iid}")
    if not items:
        return
    cell, pad = 108, 16
    w = len(items) * cell + pad * (len(items) + 1)
    h = cell + pad * 2 + (32 if label else 0)
    panel = Image.new("RGBA", (w, h), (24, 20, 16, 215))
    d = ImageDraw.Draw(panel)
    d.rectangle([0, 0, w - 1, h - 1], outline=(196, 160, 100, 255), width=2)
    y0 = pad + (30 if label else 0)
    if label:
        d.text((pad, 6), label, fill=(232, 210, 168, 255), font=load_font(20, bold=True))
    for i, icon in enumerate(items):
        ic = icon.resize((cell, cell), Image.NEAREST)
        panel.alpha_composite(ic, (pad + i * (cell + pad), y0))
    W, H = canvas.size
    positions = {
        "br": (W - w - 36, H - h - TITLE_BAND_H - 24),
        "tr": (W - w - 36, 36),
        "bl": (36, H - h - TITLE_BAND_H - 24),
        "tl": (36, 36),
    }
    x, y = positions.get(corner, positions["br"])
    canvas.alpha_composite(panel, (x, y))


def apply_veil(canvas, color):
    canvas.alpha_composite(Image.new("RGBA", canvas.size, color))


def dialogue_overlay(canvas, speaker, lines):
    w, h = canvas.size
    box_h = 70 + len(lines) * 38
    d = ImageDraw.Draw(canvas)
    top = h - TITLE_BAND_H - box_h - 24
    d.rounded_rectangle([40, top, w - 40, top + box_h], radius=14,
                        fill=(22, 18, 16, 232), outline=(196, 160, 100, 255), width=3)
    d.text((64, top + 16), speaker, fill=(246, 220, 178, 255), font=load_font(30, bold=True))
    for i, line in enumerate(lines):
        d.text((64, top + 60 + i * 38), line, fill=(222, 198, 160, 255), font=load_font(24))


def travel_overlay(canvas, destinations):
    w, h = canvas.size
    panel_w, panel_h = 480, 56 + len(destinations) * 46
    x0 = w - panel_w - 60
    y0 = 60
    d = ImageDraw.Draw(canvas)
    d.rounded_rectangle([x0, y0, x0 + panel_w, y0 + panel_h], radius=14,
                        fill=(22, 18, 16, 228), outline=(196, 160, 100, 255), width=3)
    d.text((x0 + 24, y0 + 14), "Cullis Gate — Attuned Sites", fill=(240, 222, 182, 255), font=load_font(26, bold=True))
    for i, dest in enumerate(destinations):
        y = y0 + 56 + i * 46
        d.text((x0 + 36, y), dest, fill=(222, 198, 160, 255), font=load_font(24))
        d.text((x0 + panel_w - 36, y), ">", anchor="ra", fill=(196, 160, 100, 255), font=load_font(24, bold=True))


# ---------------------------------------------------------------------------
# UI mockups / inventory grids / recipe / collage
# ---------------------------------------------------------------------------

def ui_bg(kind, size):
    w, h = size
    img = Image.new("RGBA", size, (26, 22, 18, 255))
    d = ImageDraw.Draw(img)
    frame = (186, 148, 92, 255)
    panel = (42, 34, 28, 235)

    if kind == "quest":
        d.rectangle([20, 20, w - 20, h - 20], fill=panel, outline=frame, width=3)
        d.text((36, 44), "Quest Log", fill=(236, 214, 174, 255), font=load_font(34, bold=True))
        quests = [
            "1. Wasp Menace", "2. Find the Archaeologist", "3. The Arena",
            "4. Trader Escort", "5. Find Twinblade's Camp", "6. Assassinate Twinblade",
            "7. Rescue the Prisoner", "8. Retrieve the Sword", "9. Arena Champion",
        ]
        for i, q in enumerate(quests):
            d.text((44, 100 + i * 42), q, fill=(224, 196, 146, 255), font=load_font(24, bold=False))
    elif kind == "hero":
        d.rectangle([20, 20, w - 20, h - 20], fill=panel, outline=frame, width=3)
        d.text((34, 36), "Hero Menu", fill=(240, 218, 176, 255), font=load_font(34, bold=True))
        bars = [
            ("General XP", (244, 214, 90), 0.82),
            ("Strength XP", (220, 74, 64), 0.63),
            ("Skill XP", (86, 136, 244), 0.56),
            ("Will XP", (96, 220, 110), 0.71),
        ]
        for i, (name, col, v) in enumerate(bars):
            y = 112 + i * 78
            d.text((40, y), name, fill=(224, 198, 160, 255), font=load_font(24, bold=False))
            d.rectangle([260, y + 8, w - 60, y + 38], fill=(58, 48, 42, 255), outline=(126, 100, 72, 255), width=2)
            d.rectangle([264, y + 12, 264 + int((w - 328) * v), y + 34], fill=col + (255,))
        d.text((40, 450), "Morality: +58", fill=(148, 232, 156, 255), font=load_font(28, bold=True))
        d.text((40, 494), "Title: Hero", fill=(236, 214, 172, 255), font=load_font(28, bold=True))
    elif kind == "files":
        d.rectangle([20, 20, w - 20, h - 20], fill=(22, 28, 36, 255), outline=(80, 130, 170, 255), width=2)
        d.rectangle([20, 20, w - 20, 72], fill=(30, 42, 56, 255))
        d.text((36, 36), "sound_preview", fill=(202, 226, 246, 255), font=load_font(30, bold=True))
        files = sorted(p.name for p in SOUND_DIR.glob("*.wav"))
        for i, f in enumerate(files):
            y = 98 + i * 52
            d.rectangle([36, y, w - 36, y + 38], fill=(34, 48, 64, 255), outline=(66, 92, 120, 255), width=1)
            d.text((50, y + 7), f, fill=(210, 228, 244, 255), font=load_font(24, bold=False))
    elif kind == "roadmap":
        d.rectangle([20, 20, w - 20, h - 20], fill=panel, outline=frame, width=3)
        d.text((36, 40), "Version 1.0.0 Status", fill=(238, 218, 176, 255), font=load_font(34, bold=True))
        status = [
            "[x] 45 creatures functional",
            "[x] 185 items obtainable",
            "[x] 122 recipes working",
            "[x] 17 spells tested",
            "[x] 14 quests completable",
            "[x] 8 Demon Doors operational",
            "[x] 9 structures generating",
            "[ ] Multiplayer sync improvements",
            "[ ] 10 additional side quests",
        ]
        for i, line in enumerate(status):
            d.text((44, 102 + i * 44), line, fill=(222, 198, 162, 255), font=load_font(24, bold=False))
    else:
        return cached_backdrop(size, "stone")
    return img


def anvil_scene(item_ids, size=OUT_SIZE):
    w, h = size
    img = Image.new("RGBA", size, (26, 22, 18, 255))
    d = ImageDraw.Draw(img)
    frame = (186, 148, 92, 255)
    panel = (42, 34, 28, 235)
    d.rectangle([20, 20, w - 20, h - 20], fill=panel, outline=frame, width=3)
    d.text((36, 38), "Augmentation Forge", fill=(240, 218, 176, 255), font=load_font(34, bold=True))
    slots = [(120, 130), (290, 130), (460, 130), (690, 130)]
    for x, y in slots:
        d.rounded_rectangle([x, y, x + 150, y + 150], radius=10,
                            fill=(58, 46, 38, 255), outline=(128, 102, 72, 255), width=2)
    d.line([(620, 205), (680, 205)], fill=(236, 214, 172, 255), width=8)
    d.polygon([(680, 182), (680, 228), (716, 205)], fill=(236, 214, 172, 255))
    for (x, y), iid in zip(slots, item_ids):
        p = ITEM_TEX_DIR / f"{iid}.png"
        if not p.exists():
            MISSING_ASSETS.append(f"item:{iid}")
            continue
        icon = Image.open(p).convert("RGBA")
        icon = fit_image(icon, (120, 120), Image.NEAREST)
        img.alpha_composite(icon, (x + (150 - icon.width) // 2, y + (150 - icon.height) // 2))
    return img


def inventory_scene(item_ids, size=OUT_SIZE):
    w, h = size
    img = Image.new("RGBA", size, (26, 22, 18, 255))
    d = ImageDraw.Draw(img)
    frame = (186, 148, 92, 255)
    panel = (42, 34, 28, 235)
    d.rectangle([24, 24, w - 24, h - CONTENT_BOTTOM_PAD], fill=panel, outline=frame, width=3)
    cols, rows = 4, 2
    cw = (w - 80) // cols
    ch = (h - CONTENT_BOTTOM_PAD - 92) // rows
    for i, iid in enumerate(item_ids):
        rx, ry = i % cols, i // cols
        x0 = 40 + rx * cw
        y0 = 70 + ry * ch
        d.rounded_rectangle([x0, y0, x0 + cw - 10, y0 + ch - 10], radius=8,
                            fill=(56, 46, 38, 255), outline=(112, 90, 62, 255), width=2)
        p = ITEM_TEX_DIR / f"{iid}.png"
        if not p.exists():
            MISSING_ASSETS.append(f"item:{iid}")
            continue
        icon = Image.open(p).convert("RGBA")
        icon = fit_image(icon, (int((cw - 30) * 0.7), int((ch - 30) * 0.7)), Image.NEAREST)
        cx = x0 + (cw - 10 - icon.width) // 2
        cy = y0 + (ch - 10 - icon.height) // 2
        img.alpha_composite(icon, (cx, cy))
    return img


def recipe_scene(recipe_id, size=OUT_SIZE):
    p = SHOTS / "recipes" / f"{recipe_id}.png"
    if p.exists():
        return Image.open(p).convert("RGBA").resize(size, Image.Resampling.LANCZOS)
    MISSING_ASSETS.append(f"recipe:{recipe_id}")
    return cached_backdrop(size, "stone")


def collage_scene(size=OUT_SIZE):
    w, h = size
    tiles = [
        SHOTS / "gallery" / "bosses.png",
        SHOTS / "gallery" / "npcs_features.png",
        SHOTS / "gallery" / "progression_weapons.png",
        SHOTS / "gallery" / "progression_armor.png",
        SHOTS / "gallery" / "forge_weapons.png",
        SHOTS / "gallery" / "forge_armor.png",
    ]
    img = Image.new("RGBA", size, (18, 18, 20, 255))
    cols, rows = 3, 2
    tw = (w - 42) // cols
    th = (h - CONTENT_BOTTOM_PAD - 42) // rows
    i = 0
    for ry in range(rows):
        for rx in range(cols):
            x = 14 + rx * (tw + 14)
            y = 14 + ry * (th + 14)
            if i < len(tiles) and tiles[i].exists():
                t = Image.open(tiles[i]).convert("RGBA")
                t = t.resize((tw, th), Image.Resampling.LANCZOS)
            else:
                t = cached_backdrop((tw, th), "stone")
            img.alpha_composite(t, (x, y))
            i += 1
    apply_veil(img, (0, 0, 0, 72))
    return img


def add_frame_and_titles(img, title, subtitle):
    w, h = img.size
    card = img.copy()
    d = ImageDraw.Draw(card)
    band_h = TITLE_BAND_H
    d.rectangle([0, h - band_h, w, h], fill=(22, 18, 14, 226))
    d.rectangle([24, h - band_h + 14, w - 24, h - 14], outline=(188, 150, 98, 255), width=2)
    d.text((w // 2, h - 84), title, anchor="mm", fill=(240, 222, 182, 255), font=load_font(42, bold=True))
    d.text((w // 2, h - 38), subtitle, anchor="mm", fill=(204, 178, 134, 255), font=load_font(27, bold=False))
    return card


# ---------------------------------------------------------------------------
# Scene definitions
# ---------------------------------------------------------------------------

SCENES = [
    {
        "id": "01_hero_guild_gate", "kind": "scene3d", "struct": "guild_hall",
        "title": "Hero at Heroes' Guild",
        "subtitle": "Stepping through the gate, Guild Seal in hand",
        "mobs": [("guildmaster", (22, 1, 4), {"yaw": 0.0})],
        "items": (["guild_seal", "stick"], "Starting Gear"),
    },
    {
        "id": "02_balverine_night_fight", "kind": "scene3d", "struct": "witchwood_stones",
        "title": "Balverine Night Hunt",
        "subtitle": "Moonlit ambush among the monoliths",
        "mobs": [
            ("balverine", (8, 1, 14), {"scale": 0.078, "yaw": 0.5}),
            ("white_balverine", (16, 1, 9), {"scale": 0.078, "yaw": -0.9}),
        ],
        "veil": (8, 10, 30, 130),
    },
    {
        "id": "03_roster_group_shot", "kind": "scene3d", "struct": "graveyard",
        "title": "Creature Roster",
        "subtitle": "Hobbes, Hollow Men, and an Earth Troll among the headstones",
        "mobs": [
            ("hobbe", (7, 1, 16), {"yaw": 0.3}),
            ("hobbe_scout", (17, 1, 15), {"yaw": -0.6}),
            ("undead", (12, 1, 20), {"yaw": 3.0}),
            ("undead_knight", (9, 1, 20), {"yaw": 2.6}),
            ("earth_troll", (16, 1, 18), {"scale": 0.085, "yaw": -0.2}),
        ],
    },
    {
        "id": "04_inventory_weapon_armor", "kind": "inventory",
        "title": "Item Compendium",
        "subtitle": "Weapon tiers and armour sets, crafted in order",
        "items": ["iron_longsword", "steel_longsword", "obsidian_longsword", "master_longsword",
                  "apprentice_torso", "guild_cloth", "platemail_torso", "archon_torso"],
    },
    {
        "id": "05_archon_with_aeons", "kind": "scene3d", "struct": "temple_avo",
        "title": "Archon Endgame Kit",
        "subtitle": "Full Archon armour blessed at the Temple of Avo",
        "mobs": [],
        "effects": [holy_glow_fx((8, 3, 14))],
        "items": (["archon_helm", "archon_torso", "archon_legs", "archon_boots", "sword_of_aeons"], "Archon Set + Sword of Aeons"),
    },
    {
        "id": "06_master_katana_recipe", "kind": "recipe", "recipe": "master_katana",
        "title": "Crafting Progression",
        "subtitle": "Master Katana recipe at the table",
    },
    {
        "id": "07_fireball_vs_hobbes", "kind": "scene3d", "struct": "darkwood_camp",
        "title": "Will Power — Fireball",
        "subtitle": "An explosive sphere of flame bursts over a hobbe pack",
        "mobs": [
            ("hobbe", (9, 1, 13), {"yaw": 0.4}),
            ("hobbe_scout", (15, 1, 9), {"yaw": -0.7}),
            ("hobbe", (12, 1, 17), {"yaw": 2.2}),
        ],
        "effects": [fireball_fx((13, 2.4, 13), target=(10, 1.2, 13))],
        "items": (["spell_fireball"], "Will Power"),
    },
    {
        "id": "08_slow_time_bandit_camp", "kind": "scene3d", "struct": "bandit_camp",
        "title": "Will Power — Slow Time",
        "subtitle": "The world crawls around Twinblade's raiders",
        "mobs": [
            ("twinblade", (16, 1, 19), {"scale": 0.082, "yaw": 3.1}),
            ("bandit", (11, 1, 21), {"yaw": 2.6}),
            ("bandit_archer", (21, 1, 21), {"yaw": 3.6}),
        ],
        "effects": [slow_time_fx((16, 1.4, 19), radius=4.5)],
        "items": (["spell_slow_time"], "Will Power"),
    },
    {
        "id": "09_quest_log_ui", "kind": "ui", "ui": "quest",
        "title": "Quest Log",
        "subtitle": "Main chain and side quest progress",
    },
    {
        "id": "10_twinblade_boss_fight", "kind": "scene3d", "struct": "bandit_camp",
        "title": "Twinblade Boss Fight",
        "subtitle": "The Bandit King makes his stand at the war-camp pavilion",
        "mobs": [
            ("twinblade", (16, 1, 11), {"scale": 0.085, "yaw": 3.14}),
            ("bandit", (11, 1, 15), {"yaw": 2.7}),
            ("bandit_archer", (21, 1, 15), {"yaw": 3.5}),
        ],
        "items": (["master_greatsword"], "Loot"),
    },
    {
        "id": "11_demon_door_closeup", "kind": "scene3d", "struct": "demon_door_arch",
        "title": "Demon Door Encounter",
        "subtitle": "A living stone face carved into the hillside",
        "mobs": [("demon_door", (11.5, 0.6, 5.5), {"scale": 0.16})],
    },
    {
        "id": "12_guild_wide_lake_view", "kind": "scene3d", "struct": "guild_hall",
        "title": "Heroes' Guild — Walled Grounds",
        "subtitle": "The academy seen across its training yards",
        "mobs": [
            ("guildmaster", (22, 1, 20), {"yaw": 1.0}),
            ("guard_bowerstone", (28, 1, 22), {"yaw": -1.2}),
        ],
        "pitch": 0.64,
    },
    {
        "id": "13_temple_avo_donation", "kind": "scene3d", "struct": "temple_avo",
        "title": "Temple of Avo",
        "subtitle": "Villagers leave coin offerings at the donation fountain",
        "mobs": [("villager_albion", (5, 3, 9), {"yaw": 0.9})],
        "effects": [holy_glow_fx((8, 4, 9), height=3.0)],
        "items": (["gold_coin"], "Offerings"),
    },
    {
        "id": "14_guard_low_rep_dialogue", "kind": "scene3d", "struct": "bowerstone_market",
        "title": "Faction Reputation",
        "subtitle": "A low-reputation Bowerstone Guard keeps watch",
        "mobs": [("guard_bowerstone", (18, 1, 10), {"yaw": 3.14})],
        "dialogue": ("Bowerstone Guard", [
            "I've got my eye on you.",
            "One wrong move and you'll answer to the law.",
        ]),
    },
    {
        "id": "15_hero_menu_xp_morality", "kind": "ui", "ui": "hero",
        "title": "Hero Menu",
        "subtitle": "XP bars, morality meter, and title",
    },
    {
        "id": "16_cullis_gate_travel_ui", "kind": "scene3d", "struct": "focus_site",
        "title": "Cullis Gate Fast Travel",
        "subtitle": "Attuned focus sites join the teleport network",
        "mobs": [],
        "effects": [holy_glow_fx((6, 3, 6), height=3.5)],
        "items": (["guild_seal", "septimal_key"], "Attunement"),
        "travel": ["Heroes' Guild", "Oakvale", "Bowerstone", "Snowspire Oracle"],
    },
    {
        "id": "17_visible_armor_sets", "kind": "inventory",
        "title": "Visible Armour System",
        "subtitle": "Apprentice, Guild, Plate, and Archon — worn on the hero",
        "items": ["apprentice_torso", "guild_cloth", "platemail_torso", "archon_torso",
                  "apprentice_helm", "wizard_hat", "platemail_helm", "archon_helm"],
    },
    {
        "id": "18_anvil_augments", "kind": "anvil",
        "title": "Weapon Augmentation",
        "subtitle": "Sword of Aeons with three augments bound",
        "items": ["sword_of_aeons", "sharpening_augment", "lightning_augment", "silver_augment"],
    },
    {
        "id": "19_sound_files_overview", "kind": "ui", "ui": "files",
        "title": "Synthesized Sound Design",
        "subtitle": "Procedural WAV set in the repository",
    },
    {
        "id": "20_starter_inventory", "kind": "inventory",
        "title": "Quick Start Loadout",
        "subtitle": "Guild Seal and Stick on spawn",
        "items": ["guild_seal", "stick", "apprentice_torso", "apprentice_helm"],
    },
    {
        "id": "21_roadmap_progress", "kind": "ui", "ui": "roadmap",
        "title": "Known Issues and Future Plans",
        "subtitle": "Current status and planned updates",
    },
    {
        "id": "22_media_collage", "kind": "collage",
        "title": "Gallery and Media",
        "subtitle": "Procedural assets and gameplay collage",
    },
]


# ---------------------------------------------------------------------------
# Render dispatch
# ---------------------------------------------------------------------------

def render_scene(scene):
    kind = scene["kind"]
    if kind == "scene3d":
        img = compose_structure_scene(
            scene["struct"], mobs=scene.get("mobs", ()), effects=scene.get("effects", ()),
            veil=scene.get("veil"), yaw=scene.get("yaw"), pitch=scene.get("pitch"),
        )
        if "items" in scene:
            ids, label = scene["items"]
            add_item_tray(img, ids, label=label)
        if "dialogue" in scene:
            speaker, lines = scene["dialogue"]
            dialogue_overlay(img, speaker, lines)
        if "travel" in scene:
            travel_overlay(img, scene["travel"])
    elif kind == "inventory":
        img = inventory_scene(scene["items"])
    elif kind == "anvil":
        img = anvil_scene(scene["items"])
    elif kind == "ui":
        img = ui_bg(scene["ui"], OUT_SIZE)
    elif kind == "recipe":
        img = recipe_scene(scene["recipe"])
    elif kind == "collage":
        img = collage_scene()
    else:
        raise ValueError(f"unknown scene kind: {kind}")
    return add_frame_and_titles(img, scene["title"], scene["subtitle"])


def write_index(rows):
    lines = [
        "# Documentation Screenshot Set",
        "",
        "Generated by scripts/gen_doc_screenshots.py.",
        "",
    ]
    for sid, title, subtitle in rows:
        lines.append(f"- {sid}: {title} - {subtitle}")
    (DOC_DIR / "INDEX.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    DOC_DIR.mkdir(parents=True, exist_ok=True)
    rows = []
    for scene in SCENES:
        img = render_scene(scene)
        out = DOC_DIR / f"{scene['id']}.png"
        img.convert("RGB").save(out, quality=92)
        rows.append((scene["id"], scene["title"], scene["subtitle"]))
        print(f"wrote {out.name}")
    write_index(rows)
    if MISSING_ASSETS:
        missing = ", ".join(sorted(set(MISSING_ASSETS)))
        raise SystemExit(f"missing documentation assets: {missing}")
    print(f"done: {len(rows)} documentation screenshots")


if __name__ == "__main__":
    main()

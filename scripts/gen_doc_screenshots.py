"""gen_doc_screenshots.py - render documentation showcase screenshots.

Builds a deterministic set of README-ready promo images by compositing
already-generated screenshots and texture assets into scene cards that map
to the long-form documentation sections.
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

from fc_lib import ROOT, SHOTS

DOC_DIR = SHOTS / "docs"
MOBS_DIR = SHOTS / "mobs"
STRUCT_DIR = SHOTS / "structures"
ITEM_TEX_DIR = ROOT / "packs" / "Fablecraft_RP" / "textures" / "items"
SOUND_DIR = ROOT / "sound_preview"
MISSING_ASSETS = []
TITLE_BAND_H = 132
CONTENT_BOTTOM_PAD = TITLE_BAND_H + 26


SCENES = [
    {
        "id": "01_hero_guild_gate",
        "title": "Hero at Heroes' Guild",
        "subtitle": "Guild entrance with Cullis Gate glow in foreground",
        "bg": "structure:guild_hall",
        "entities": ["mob:guildmaster", "item:guild_seal", "item:stick"],
    },
    {
        "id": "02_balverine_night_fight",
        "title": "Balverine Night Hunt",
        "subtitle": "Forest fight under moonlight",
        "bg": "mood:forest_night",
        "entities": ["mob:balverine", "mob:white_balverine", "item:sword_of_aeons"],
    },
    {
        "id": "03_roster_group_shot",
        "title": "Creature Roster",
        "subtitle": "Hobbes, Hollow Men, and Trolls",
        "bg": "mood:swamp_dusk",
        "entities": ["mob:hobbe", "mob:hobbe_scout", "mob:undead", "mob:undead_knight", "mob:earth_troll"],
    },
    {
        "id": "04_inventory_weapon_armor",
        "title": "Item Compendium",
        "subtitle": "Weapon tiers and armor sets",
        "bg": "ui:grid",
        "entities": [
            "item:iron_longsword", "item:steel_longsword", "item:obsidian_longsword", "item:master_longsword",
            "item:apprentice_torso", "item:guild_cloth", "item:platemail_torso", "item:archon_torso",
        ],
    },
    {
        "id": "05_archon_with_aeons",
        "title": "Archon Endgame Kit",
        "subtitle": "Full Archon armor with Sword of Aeons",
        "bg": "mood:holy",
        "entities": ["item:archon_helm", "item:archon_torso", "item:archon_legs", "item:archon_boots", "item:sword_of_aeons"],
    },
    {
        "id": "06_master_katana_recipe",
        "title": "Crafting Progression",
        "subtitle": "Master Katana recipe at the table",
        "bg": "recipe:master_katana",
        "entities": ["item:master_ingot", "item:will_shard", "item:master_katana"],
    },
    {
        "id": "07_fireball_vs_hobbes",
        "title": "Will Power - Fireball",
        "subtitle": "Explosive cast against a hobbe pack",
        "bg": "mood:fire",
        "entities": ["item:spell_fireball", "mob:hobbe", "mob:hobbe_scout", "mob:hobbe"],
    },
    {
        "id": "08_slow_time_bandit_camp",
        "title": "Will Power - Slow Time",
        "subtitle": "Temporal field in Twinblade's camp",
        "bg": "structure:bandit_camp",
        "entities": ["item:spell_slow_time", "mob:bandit", "mob:bandit_archer", "mob:twinblade"],
    },
    {
        "id": "09_quest_log_ui",
        "title": "Quest Log",
        "subtitle": "Main chain and side quest progress",
        "bg": "ui:quest",
        "entities": ["item:quest_card", "item:guild_seal"],
    },
    {
        "id": "10_twinblade_boss_fight",
        "title": "Twinblade Boss Fight",
        "subtitle": "War camp confrontation",
        "bg": "structure:bandit_camp",
        "entities": ["mob:twinblade", "mob:bandit", "mob:bandit_archer", "item:master_greatsword"],
    },
    {
        "id": "11_demon_door_closeup",
        "title": "Demon Door Encounter",
        "subtitle": "Living stone face in a carved crag",
        "bg": "structure:demon_door_arch",
        "entities": ["mob:demon_door"],
    },
    {
        "id": "12_guild_wide_lake_view",
        "title": "Heroes' Guild Exterior",
        "subtitle": "Walled complex from across the water",
        "bg": "structure:guild_hall",
        "entities": ["item:guild_seal"],
    },
    {
        "id": "13_temple_avo_donation",
        "title": "Temple of Avo",
        "subtitle": "Donation bowl and blessing altar",
        "bg": "structure:temple_avo",
        "entities": ["item:gold_coin", "item:gold_coin", "item:gold_coin"],
    },
    {
        "id": "14_guard_low_rep_dialogue",
        "title": "Faction Reputation",
        "subtitle": "Low reputation guard warning",
        "bg": "ui:dialogue",
        "entities": ["mob:guard_bowerstone", "item:jack_of_blades_mask"],
    },
    {
        "id": "15_hero_menu_xp_morality",
        "title": "Hero Menu",
        "subtitle": "XP bars, morality meter, and title",
        "bg": "ui:hero",
        "entities": ["item:orb_general", "item:orb_strength", "item:orb_skill", "item:orb_will"],
    },
    {
        "id": "16_cullis_gate_travel_ui",
        "title": "Cullis Gate Fast Travel",
        "subtitle": "Attuned destinations in travel menu",
        "bg": "structure:focus_site",
        "entities": ["item:guild_seal", "item:septimal_key"],
    },
    {
        "id": "17_visible_armor_sets",
        "title": "Visible Armor System",
        "subtitle": "Apprentice, Guild, Plate, Archon",
        "bg": "ui:grid",
        "entities": [
            "item:apprentice_torso", "item:guild_cloth", "item:platemail_torso", "item:archon_torso",
            "item:apprentice_helm", "item:wizard_hat", "item:platemail_helm", "item:archon_helm",
        ],
    },
    {
        "id": "18_anvil_augments",
        "title": "Weapon Augmentation",
        "subtitle": "Sword of Aeons with three augments",
        "bg": "ui:anvil",
        "entities": ["item:sword_of_aeons", "item:sharpening_augment", "item:lightning_augment", "item:silver_augment"],
    },
    {
        "id": "19_sound_files_overview",
        "title": "Synthesized Sound Design",
        "subtitle": "Procedural WAV set in repository",
        "bg": "ui:files",
        "entities": [
            "text:door_rumble.wav", "text:door_speak.wav", "text:banshee_shriek.wav", "text:spell_cast.wav",
            "text:level_up.wav", "text:guild_pad.wav", "text:sword_clash.wav",
        ],
    },
    {
        "id": "20_starter_inventory",
        "title": "Quick Start Loadout",
        "subtitle": "Guild Seal and Stick on spawn",
        "bg": "ui:grid",
        "entities": ["item:guild_seal", "item:stick", "item:apprentice_torso", "item:apprentice_helm"],
    },
    {
        "id": "21_roadmap_progress",
        "title": "Known Issues and Future Plans",
        "subtitle": "Current status and planned updates",
        "bg": "ui:roadmap",
        "entities": ["item:quest_card"],
    },
    {
        "id": "22_media_collage",
        "title": "Gallery and Media",
        "subtitle": "Procedural assets and gameplay collage",
        "bg": "collage:core",
        "entities": [],
    },
]


def load_font(size, bold=False):
    names = ["seguisb.ttf", "segoeuib.ttf", "arialbd.ttf"] if bold else ["segoeui.ttf", "arial.ttf"]
    for name in names:
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def asset_image(token):
    kind, value = token.split(":", 1)
    if kind == "mob":
        p = MOBS_DIR / f"{value}.png"
    elif kind == "item":
        p = ITEM_TEX_DIR / f"{value}.png"
    else:
        return None
    if p.exists():
        img = Image.open(p).convert("RGBA")
        if kind == "mob":
            margin_x = int(img.width * 0.10)
            top = int(img.height * 0.04)
            bottom = int(img.height * 0.68)
            img = img.crop((margin_x, top, img.width - margin_x, bottom))
        return img
    MISSING_ASSETS.append(token)
    return None


def fit_image(img, max_size, resample=Image.Resampling.LANCZOS):
    w, h = img.size
    scale = min(max_size[0] / max(1, w), max_size[1] / max(1, h))
    target = (max(1, int(w * scale)), max(1, int(h * scale)))
    return img.resize(target, resample)


def structure_bg(name, size):
    p = STRUCT_DIR / f"{name}.png"
    if p.exists():
        img = Image.open(p).convert("RGBA").resize(size, Image.Resampling.LANCZOS)
        veil = Image.new("RGBA", size, (14, 14, 18, 90))
        img.alpha_composite(veil)
        return img
    return mood_bg("stone", size)


def mood_bg(name, size):
    palettes = {
        "forest_night": ((12, 20, 22), (34, 68, 52)),
        "swamp_dusk": ((18, 24, 20), (68, 82, 62)),
        "holy": ((44, 36, 22), (164, 126, 72)),
        "fire": ((42, 18, 14), (160, 72, 42)),
        "stone": ((24, 24, 26), (84, 84, 88)),
    }
    lo, hi = palettes.get(name, palettes["stone"])
    w, h = size
    img = Image.new("RGBA", size, (0, 0, 0, 255))
    px = img.load()
    cx, cy = w / 2, h * 0.4
    maxd = (cx * cx + cy * cy) ** 0.5 * 1.15
    for y in range(h):
        for x in range(w):
            d = (((x - cx) ** 2 + (y - cy) ** 2) ** 0.5) / maxd
            t = max(0.0, 1.0 - d)
            c = tuple(int(lo[i] + (hi[i] - lo[i]) * t * t) for i in range(3))
            px[x, y] = c + (255,)
    return img


def ui_bg(kind, size):
    w, h = size
    img = Image.new("RGBA", size, (26, 22, 18, 255))
    d = ImageDraw.Draw(img)
    frame = (186, 148, 92, 255)
    panel = (42, 34, 28, 235)

    if kind == "grid":
        d.rectangle([24, 24, w - 24, h - CONTENT_BOTTOM_PAD], fill=panel, outline=frame, width=3)
        cols, rows = 4, 2
        cw = (w - 80) // cols
        ch = (h - CONTENT_BOTTOM_PAD - 92) // rows
        for ry in range(rows):
            for rx in range(cols):
                x0 = 40 + rx * cw
                y0 = 70 + ry * ch
                d.rounded_rectangle([x0, y0, x0 + cw - 10, y0 + ch - 10], radius=8,
                                    fill=(56, 46, 38, 255), outline=(112, 90, 62, 255), width=2)
    elif kind == "quest":
        d.rectangle([20, 20, w - 20, h - 20], fill=panel, outline=frame, width=3)
        d.text((36, 44), "Quest Log", fill=(236, 214, 174, 255), font=load_font(34, bold=True))
        quests = [
            "1. Wasp Menace", "2. Find the Archaeologist", "3. The Arena",
            "4. Trader Escort", "5. Find Twinblade's Camp", "6. Assassinate Twinblade",
            "7. Rescue the Prisoner", "8. Retrieve the Sword", "9. Arena Champion",
        ]
        for i, q in enumerate(quests):
            d.text((44, 100 + i * 42), q, fill=(224, 196, 146, 255), font=load_font(24, bold=False))
    elif kind == "dialogue":
        img = mood_bg("stone", size)
        box_h = 180
        d = ImageDraw.Draw(img)
        d.rounded_rectangle([30, h - box_h - 24, w - 30, h - 24], radius=18,
                            fill=(24, 20, 18, 236), outline=frame, width=3)
        d.text((54, h - box_h), "Bowerstone Guard", fill=(246, 220, 178, 255), font=load_font(30, bold=True))
        d.text((54, h - 112), "I've got my eye on you.", fill=(232, 204, 164, 255), font=load_font(30, bold=False))
        d.text((54, h - 74), "One wrong move and you'll answer to the law.", fill=(196, 170, 132, 255), font=load_font(22, bold=False))
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
    elif kind == "anvil":
        d.rectangle([20, 20, w - 20, h - 20], fill=panel, outline=frame, width=3)
        d.text((36, 38), "Augmentation Forge", fill=(240, 218, 176, 255), font=load_font(34, bold=True))
        slots = [(120, 130), (290, 130), (460, 130), (690, 130)]
        for x, y in slots:
            d.rounded_rectangle([x, y, x + 150, y + 150], radius=10,
                                fill=(58, 46, 38, 255), outline=(128, 102, 72, 255), width=2)
        d.line([(620, 205), (680, 205)], fill=(236, 214, 172, 255), width=8)
        d.polygon([(680, 182), (680, 228), (716, 205)], fill=(236, 214, 172, 255))
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
        return mood_bg("stone", size)
    return img


def recipe_bg(recipe_id, size):
    p = SHOTS / "recipes" / f"{recipe_id}.png"
    if p.exists():
        return Image.open(p).convert("RGBA").resize(size, Image.Resampling.LANCZOS)
    return ui_bg("grid", size)


def collage_bg(size):
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
                t = mood_bg("stone", (tw, th))
            img.alpha_composite(t, (x, y))
            i += 1
    veil = Image.new("RGBA", size, (0, 0, 0, 72))
    img.alpha_composite(veil)
    return img


def base_for_scene(scene, size):
    bg = scene["bg"]
    kind, value = bg.split(":", 1)
    if kind == "structure":
        return structure_bg(value, size)
    if kind == "mood":
        return mood_bg(value, size)
    if kind == "ui":
        return ui_bg(value, size)
    if kind == "recipe":
        return recipe_bg(value, size)
    if kind == "collage":
        return collage_bg(size)
    return mood_bg("stone", size)


def grid_slots(size, count):
    w, h = size
    cols = 4
    rows = 2
    cw = (w - 80) // cols
    ch = (h - CONTENT_BOTTOM_PAD - 92) // rows
    slots = []
    for ry in range(rows):
        for rx in range(cols):
            x0 = 40 + rx * cw
            y0 = 70 + ry * ch
            slots.append((x0, y0, x0 + cw - 10, y0 + ch - 10))
    if count <= len(slots):
        return slots[:count]
    return slots


def flow_slots(size, count, bg_kind, bg_value):
    w, h = size
    content_h = h - CONTENT_BOTTOM_PAD
    if count <= 0:
        return []
    if count == 1:
        cx = w * 0.72 if bg_kind == "ui" else w * 0.50
        return [(cx, content_h * 0.50, w * 0.30, content_h * 0.46)]
    if bg_kind == "ui":
        left = w * 0.45
        right = w * 0.86
        if bg_value in ("quest", "hero", "files", "roadmap"):
            left = w * 0.52
            right = w * 0.84
        top = content_h * 0.34
        bottom = content_h * 0.70
        slot_w = (right - left) / count
        slots = []
        for i in range(count):
            cx = left + slot_w * (i + 0.5)
            cy = top + (bottom - top) * (0.42 if i % 2 == 0 else 0.58)
            slots.append((cx, cy, slot_w * 0.72, content_h * 0.34))
        return slots
    top = content_h * (0.19 if bg_kind == "structure" else 0.24)
    bottom = content_h * (0.82 if bg_kind == "structure" else 0.78)
    slot_w = w / count
    slots = []
    for i in range(count):
        cx = slot_w * (i + 0.5)
        cy = top + (bottom - top) * (0.38 if i % 2 == 0 else 0.62)
        slots.append((cx, cy, slot_w * 0.72, content_h * 0.52))
    return slots


def paste_asset(canvas, img, cx, cy, max_w, max_h, token):
    resample = Image.Resampling.LANCZOS if token.startswith("mob:") else Image.Resampling.NEAREST
    img = fit_image(img, (int(max_w), int(max_h)), resample)
    x = int(cx - img.width / 2)
    y = int(cy - img.height / 2)
    shadow = Image.new("RGBA", (img.width + 24, img.height + 24), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    sd.ellipse([6, img.height - 4, img.width + 18, img.height + 18], fill=(0, 0, 0, 95))
    shadow = shadow.filter(ImageFilter.GaussianBlur(6))
    canvas.alpha_composite(shadow, (x - 12, y - 10))
    canvas.alpha_composite(img, (x, y))


def paste_missing_marker(canvas, draw, token, cx, cy):
    x = int(cx)
    y = int(cy)
    draw.rectangle([x - 90, y - 90, x + 90, y + 90], fill=(80, 24, 64, 180), outline=(245, 96, 210, 255), width=4)
    draw.text((x, y), token, anchor="mm", fill=(255, 220, 246, 255), font=load_font(24, bold=True))


def paste_entities(canvas, entities, bg):
    w, h = canvas.size
    draw = ImageDraw.Draw(canvas)
    bg_kind, bg_value = bg.split(":", 1)
    visual = [e for e in entities if not e.startswith("text:")]
    if visual and bg == "ui:grid":
        slots = grid_slots(canvas.size, len(visual))
        for i, token in enumerate(visual):
            x0, y0, x1, y1 = slots[i]
            img = asset_image(token)
            if img is None:
                paste_missing_marker(canvas, draw, token, (x0 + x1) / 2, (y0 + y1) / 2)
                continue
            paste_asset(canvas, img, (x0 + x1) / 2, (y0 + y1) / 2, (x1 - x0) * 0.56, (y1 - y0) * 0.56, token)
    elif visual:
        slots = flow_slots(canvas.size, len(visual), bg_kind, bg_value)
        for i, token in enumerate(visual):
            cx, cy, max_w, max_h = slots[i]
            img = asset_image(token)
            if img is None:
                paste_missing_marker(canvas, draw, token, cx, cy)
                continue
            if token.startswith("item:") and bg_kind != "ui":
                max_w *= 0.48
                max_h *= 0.48
            elif token.startswith("item:"):
                max_w *= 0.78
                max_h *= 0.78
            elif bg_kind == "structure":
                max_w *= 0.50
                max_h *= 0.50
            elif bg_kind == "mood":
                max_w *= 0.72
                max_h *= 0.72
            paste_asset(canvas, img, cx, cy, max_w, max_h, token)

    text_rows = [e.split(":", 1)[1] for e in entities if e.startswith("text:")]
    if text_rows:
        y0 = int((h - CONTENT_BOTTOM_PAD) * 0.24)
        for i, row in enumerate(text_rows):
            draw.text((int(w * 0.12), y0 + i * 38), row, fill=(218, 232, 246, 255), font=load_font(24, bold=False))


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


def render_scene(scene, size=(1920, 1080)):
    base = base_for_scene(scene, size)
    paste_entities(base, scene["entities"], scene["bg"])
    return add_frame_and_titles(base, scene["title"], scene["subtitle"])


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

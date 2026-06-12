"""gen_readme_panels.py - curated README panels for Forge and Rogues' Gallery.

Builds organized, informative gallery panels from already rendered assets:
- screenshots/gallery/forge_*.png
- screenshots/gallery/rogues_*.png
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from fc_lib import SHOTS
from fc_mobs import MOBS as MOB_DEFS

GALLERY = SHOTS / "gallery"
RECIPES = SHOTS / "recipes"
MOB_SHOTS = SHOTS / "mobs"


def load_font(size, bold=False):
    names = ["seguisb.ttf", "segoeuib.ttf", "arialbd.ttf"] if bold else ["segoeui.ttf", "arial.ttf"]
    for name in names:
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def backdrop(size, lo=(28, 24, 20), hi=(110, 92, 66)):
    w, h = size
    img = Image.new("RGBA", size)
    px = img.load()
    cx, cy = w / 2, h * 0.35
    maxd = ((cx * cx + cy * cy) ** 0.5) * 1.1
    for y in range(h):
        for x in range(w):
            d = (((x - cx) ** 2 + (y - cy) ** 2) ** 0.5) / maxd
            t = max(0.0, 1.0 - d)
            c = tuple(int(lo[i] + (hi[i] - lo[i]) * t * t) for i in range(3))
            px[x, y] = c + (255,)
    return img


def open_tile(path, max_size):
    if path.exists():
        img = Image.open(path).convert("RGBA")
        img.thumbnail(max_size, Image.Resampling.LANCZOS)
        return img
    return None


def draw_missing(size, label):
    img = Image.new("RGBA", size, (70, 50, 46, 255))
    d = ImageDraw.Draw(img)
    d.rectangle([2, 2, size[0] - 3, size[1] - 3], outline=(168, 126, 90, 255), width=2)
    d.text((size[0] // 2, size[1] // 2), label, anchor="mm", fill=(224, 200, 170, 255), font=load_font(20, bold=True))
    return img


def panel(path, title, subtitle, tiles, cols=3, cell=(520, 360)):
    rows = (len(tiles) + cols - 1) // cols
    w = cols * cell[0] + 64
    h = rows * cell[1] + 180
    img = backdrop((w, h))
    d = ImageDraw.Draw(img)

    d.text((w // 2, 42), title, anchor="mm", fill=(242, 222, 184, 255), font=load_font(44, bold=True))
    d.text((w // 2, 84), subtitle, anchor="mm", fill=(196, 170, 132, 255), font=load_font(24, bold=False))

    for i, tile in enumerate(tiles):
        col = i % cols
        row = i // cols
        x0 = 24 + col * cell[0]
        y0 = 120 + row * cell[1]
        x1 = x0 + cell[0] - 24
        y1 = y0 + cell[1] - 20
        d.rectangle([x0, y0, x1, y1], fill=(30, 24, 20, 232), outline=(142, 112, 74, 255), width=2)

        source = tile["path"]
        asset = open_tile(source, (cell[0] - 42, cell[1] - 108))
        if asset is None:
            asset = draw_missing((cell[0] - 42, cell[1] - 108), "Missing")

        px = x0 + (cell[0] - 24 - asset.width) // 2
        py = y0 + 14
        img.alpha_composite(asset, (px, py))

        d.text((x0 + (cell[0] - 24) // 2, y1 - 52), tile["name"], anchor="mm", fill=(238, 214, 172, 255), font=load_font(22, bold=True))
        d.text((x0 + (cell[0] - 24) // 2, y1 - 26), tile["meta"], anchor="mm", fill=(190, 164, 128, 255), font=load_font(18, bold=False))

    path.parent.mkdir(parents=True, exist_ok=True)
    img.convert("RGB").save(path, quality=92)
    print(f"wrote {path.name}")


def recipe_tile(recipe_id, name, meta):
    return {"path": RECIPES / f"{recipe_id}.png", "name": name, "meta": meta}


def mob_tile(mob_id, name, meta):
    return {"path": MOB_SHOTS / f"{mob_id}.png", "name": name, "meta": meta}


def main():
    mob_by_id = {m["id"]: m for m in MOB_DEFS}

    # Forge panels
    forge_core = [
        recipe_tile("steel_ingot", "Steel Ingot", "2x Iron + Coal"),
        recipe_tile("obsidian_ingot", "Obsidian Ingot", "Smelt Obsidian"),
        recipe_tile("master_ingot", "Master Ingot", "Steel + 2x Will Shard"),
        recipe_tile("runed_hilt", "Runed Hilt", "Steel + Straps + Will"),
        recipe_tile("tempered_plate", "Tempered Plate", "Steel + Coal"),
        recipe_tile("guild_cloth", "Guild Cloth", "Wool + String + Dye"),
    ]
    panel(
        GALLERY / "forge_smithing_core.png",
        "The Forge of Albion - Core Materials",
        "Smelting and refinement chain for all late-game crafts",
        forge_core,
        cols=3,
    )

    forge_weapons = [
        recipe_tile("iron_longsword", "Iron Longsword", "Tier 1 - starter steel"),
        recipe_tile("steel_longsword", "Steel Longsword", "Tier 2 - 1 augment slot"),
        recipe_tile("obsidian_longsword", "Obsidian Longsword", "Tier 3 - 2 augment slots"),
        recipe_tile("master_longsword", "Master Longsword", "Tier 4 - 3 augment slots"),
        recipe_tile("master_katana", "Master Katana", "Endgame speed weapon"),
        recipe_tile("master_crossbow", "Master Crossbow", "Endgame ranged tier"),
    ]
    panel(
        GALLERY / "forge_weapon_progression.png",
        "The Forge of Albion - Weapon Progression",
        "Representative recipes across tiers and combat styles",
        forge_weapons,
        cols=3,
    )

    forge_armor_aug = [
        recipe_tile("apprentice_torso", "Apprentice Chest", "Starter guild gear"),
        recipe_tile("platemail_torso", "Platemail Chest", "Heavy mid-late armor"),
        recipe_tile("archon_torso", "Archon Chest", "Endgame holy set"),
        recipe_tile("sharpening_augment", "Sharpening Augment", "+Melee damage"),
        recipe_tile("lightning_augment", "Lightning Augment", "Shock proc chance"),
        recipe_tile("silver_augment", "Silver Augment", "Bonus vs undead/beasts"),
    ]
    panel(
        GALLERY / "forge_armor_augments.png",
        "The Forge of Albion - Armor and Augments",
        "Set crafting and augmentation paths",
        forge_armor_aug,
        cols=3,
    )

    # Rogues panels
    bosses = ["twinblade", "jack_of_blades", "jack_dragon", "arachanox", "wasp_queen", "rock_giant"]
    rogues_boss_tiles = []
    for mid in bosses:
        m = mob_by_id[mid]
        rogues_boss_tiles.append(mob_tile(mid, m["name"], f"{m['behavior']} - HP {m['hp']} - DMG {m['dmg']}"))
    panel(
        GALLERY / "rogues_bosses.png",
        "Rogues' Gallery - Boss Encounters",
        "Major threat targets and end-of-zone fights",
        rogues_boss_tiles,
        cols=3,
    )

    undead_beasts = ["white_balverine", "frost_balverine", "undead", "undead_soldier", "undead_knight", "earth_troll"]
    rogues_ub_tiles = []
    for mid in undead_beasts:
        m = mob_by_id[mid]
        rogues_ub_tiles.append(mob_tile(mid, m["name"], f"{m['behavior']} - HP {m['hp']} - DMG {m['dmg']}"))
    panel(
        GALLERY / "rogues_undead_beasts.png",
        "Rogues' Gallery - Undead and Beasts",
        "Night predators, graveborn soldiers, and giant brutes",
        rogues_ub_tiles,
        cols=3,
    )

    raiders_casters = ["bandit", "bandit_archer", "assassin", "summoner", "wraith", "banshee"]
    rogues_rc_tiles = []
    for mid in raiders_casters:
        m = mob_by_id[mid]
        rogues_rc_tiles.append(mob_tile(mid, m["name"], f"{m['behavior']} - HP {m['hp']} - DMG {m['dmg']}"))
    panel(
        GALLERY / "rogues_raiders_casters.png",
        "Rogues' Gallery - Raiders and Casters",
        "Human threats and magical hostiles",
        rogues_rc_tiles,
        cols=3,
    )


if __name__ == "__main__":
    main()

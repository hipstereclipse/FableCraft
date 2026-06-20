"""build_addon.py — full pipeline: regenerate everything, validate, package.

Usage:
  python scripts/build_addon.py            # validate + package only
  python scripts/build_addon.py --full     # regen all assets first
"""
import json
import re
import subprocess
import sys
import zipfile
from pathlib import Path

from fc_lib import ROOT, BP, RP, DIST

GENERATORS = [
    "gen_item_textures.py",
    "gen_ui.py",
    "gen_hud_font.py",
    "gen_entity_textures.py",
    "gen_behavior.py",
    "gen_resources.py",
    "gen_emotes.py",
    "gen_structures.py",
    "gen_sounds.py",
]


def run_generators():
    for g in GENERATORS:
        print(f"== {g}")
        r = subprocess.run([sys.executable, str(ROOT / "scripts" / g)],
                           capture_output=True, text=True)
        if r.returncode != 0:
            print(r.stdout)
            print(r.stderr)
            sys.exit(f"generator failed: {g}")
        print(r.stdout.strip())


def validate():
    errors = []
    counts = {"json": 0, "png": 0, "wav": 0, "mcstructure": 0, "js": 0}
    for pack in (BP, RP):
        for f in pack.rglob("*"):
            if f.is_dir():
                continue
            ext = f.suffix.lower()
            if ext == ".json":
                counts["json"] += 1
                try:
                    json.loads(f.read_text(encoding="utf-8"))
                except Exception as e:
                    errors.append(f"{f.relative_to(ROOT)}: {e}")
            elif ext == ".png":
                counts["png"] += 1
            elif ext == ".wav":
                counts["wav"] += 1
            elif ext == ".mcstructure":
                counts["mcstructure"] += 1
            elif ext == ".js":
                counts["js"] += 1
    # cross-checks
    item_dir = BP / "items"
    atlas = json.loads((RP / "textures" / "item_texture.json").read_text(encoding="utf-8"))
    tex_data = atlas["texture_data"]
    for f in item_dir.glob("*.json"):
        data = json.loads(f.read_text(encoding="utf-8"))
        icon = data["minecraft:item"]["components"].get("minecraft:icon")
        name = icon if isinstance(icon, str) else icon.get("texture")
        if name not in tex_data:
            errors.append(f"item {f.stem}: icon '{name}' missing from atlas")
        else:
            tex_png = RP / (tex_data[name]["textures"] + ".png")
            if not tex_png.exists():
                errors.append(f"atlas entry {name}: missing png {tex_png.name}")
    # entity geometry/texture check
    for f in (RP / "entity").glob("*.entity.json"):
        ce = json.loads(f.read_text(encoding="utf-8"))["minecraft:client_entity"]["description"]
        for tex in ce["textures"].values():
            if not (RP / (tex + ".png")).exists():
                errors.append(f"client entity {f.stem}: missing texture {tex}")
        for geo in ce["geometry"].values():
            geo_file = RP / "models" / "entity" / (f.stem.replace(".entity", "") + ".geo.json")
            if not geo_file.exists():
                errors.append(f"client entity {f.stem}: missing geometry file")
    # BP entity <-> loot
    for f in (BP / "entities").glob("*.json"):
        data = json.loads(f.read_text(encoding="utf-8"))
        loot = data["minecraft:entity"]["components"].get("minecraft:loot", {}).get("table")
        if loot and not (BP / loot).exists():
            errors.append(f"entity {f.stem}: missing loot table {loot}")
    for script in (BP / "scripts").rglob("*.js"):
        script_text = script.read_text(encoding="utf-8")
        if "runCommandAsync(" in script_text:
            errors.append(
                f"{script.relative_to(ROOT)}: @minecraft/server 2.1.0 "
                "does not expose runCommandAsync; use runCommand"
            )
        for texture in re.findall(r'"(textures/items/[A-Za-z0-9_]+)"', script_text):
            if not (RP / f"{texture}.png").exists():
                errors.append(f"{script.relative_to(ROOT)}: form texture '{texture}' is missing")
    main_script = (BP / "scripts" / "main.js").read_text(encoding="utf-8")
    for contract in (
        "const maxX = x0 + w - 1;",
        "const maxZ = z0 + d - 1;",
        "Math.min(maxX, x)",
        "Math.min(maxZ, z)",
        "clearSkirtCover(dim, x, z, info.coverBottom, info.coverTop);",
        'world.setDynamicProperty("fc_guild_skirt_veg_v1", true);',
        'world.setDynamicProperty("fc_guild_terrain_v2", true);',
        'world.setDynamicProperty("fc_guild_terrain_v3", true);',
        'world.setDynamicProperty("fc_guild_ocean_cleanup_v1", true);',
        "const GUILD_TERRAIN_RADIUS = 40;",
        "const OVERWORLD_SEA_LEVEL = 62;",
        "const y = Math.max(OVERWORLD_SEA_LEVEL, sampledY - 1);",
        "const y = naturalGroundY(dim, x, z, allowLiquid);",
        '{ cap: "minecraft:sand", fill: "minecraft:sandstone" }',
    ):
        if contract not in main_script:
            errors.append(
                "scripts/main.js: terrain skirt must use inclusive "
                f"width-1/depth-1 footprint bounds (missing {contract!r})"
            )
    required_ui = [
        "dialog_background_hollow_3",
        "button_borderless_light",
        "button_borderless_lighthover",
        "button_borderless_lightpressed",
        "button_borderless_lightpressednohover",
        "ScrollRail",
        "ScrollHandle",
    ]
    for name in required_ui:
        for suffix in (".json", ".png"):
            path = RP / "textures" / "ui" / f"{name}{suffix}"
            if not path.exists():
                errors.append(f"required generated UI asset missing: {path.relative_to(ROOT)}")
    required_fable_hud = [
        RP / "ui" / "_ui_defs.json",
        RP / "ui" / "hud_screen.json",
        RP / "font" / "glyph_E9.png",
        *(RP / "textures" / "ui" / "fable_hud" / f"{name}.png" for name in (
            "status_frame", "minimap", "eye_frame", "eye_open", "eye_partial", "eye_closed",
            "multiplier", "gold", "clock", "hunger_slot", "map_details", "wanted_star",
        )),
    ]
    for path in required_fable_hud:
        if not path.exists():
            errors.append(f"required Fable HUD asset missing: {path.relative_to(ROOT)}")
    print(f"validated: {counts}")
    audit = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "verify_emotes.py")],
        capture_output=True,
        text=True,
    )
    if audit.stdout.strip():
        print(audit.stdout.strip())
    if audit.returncode != 0:
        if audit.stderr.strip():
            print(audit.stderr.strip())
        errors.append("Fable expression audit failed")
    hud_audit = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "audit_hud.py"), "--check"],
        capture_output=True,
        text=True,
    )
    if hud_audit.stdout.strip():
        print(hud_audit.stdout.strip())
    if hud_audit.returncode != 0:
        if hud_audit.stderr.strip():
            print(hud_audit.stderr.strip())
        errors.append("Fable HUD audit failed")
    if errors:
        print("\n".join("  ERROR " + e for e in errors))
        sys.exit(f"{len(errors)} validation error(s)")
    print("all cross-references OK")


def package():
    DIST.mkdir(exist_ok=True)
    out = DIST / "Fablecraft_Reforged.mcaddon"
    if out.exists():
        out.unlink()
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED, compresslevel=7) as z:
        for pack, prefix in ((BP, "Fablecraft_BP"), (RP, "Fablecraft_RP")):
            for f in sorted(pack.rglob("*")):
                if f.is_file():
                    z.write(f, f"{prefix}/{f.relative_to(pack)}")
    size = out.stat().st_size
    print(f"packaged {out.name}: {size/1024/1024:.2f} MB")
    # also emit separate .mcpack files for convenience
    for pack, label in ((BP, "Fablecraft_BP"), (RP, "Fablecraft_RP")):
        mp = DIST / f"{label}.mcpack"
        if mp.exists():
            mp.unlink()
        with zipfile.ZipFile(mp, "w", zipfile.ZIP_DEFLATED, compresslevel=7) as z:
            for f in sorted(pack.rglob("*")):
                if f.is_file():
                    z.write(f, f.relative_to(pack))
        print(f"packaged {mp.name}: {mp.stat().st_size/1024/1024:.2f} MB")


if __name__ == "__main__":
    if "--full" in sys.argv:
        run_generators()
    validate()
    package()

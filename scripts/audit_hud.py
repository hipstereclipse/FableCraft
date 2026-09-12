"""Static and visual audit for the Fablecraft in-game HUD.

Usage:
  python scripts/audit_hud.py
  python scripts/audit_hud.py --check
  python scripts/audit_hud.py --reference original.png --capture current.png
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFont, ImageStat


ROOT = Path(__file__).resolve().parents[1]
RP = ROOT / "packs" / "Fablecraft_RP"
HUD_JSON = RP / "ui" / "hud_screen.json"
HUD_SCRIPT = ROOT / "packs" / "Fablecraft_BP" / "scripts" / "fable_hud.js"
HUD_TEXTURES = RP / "textures" / "ui" / "fable_hud"
GLYPHS = RP / "font" / "glyph_E9.png"
OUTPUT = ROOT / "screenshots" / "ui"

CANVAS = (1280, 720)
UI_SCALE = 3

OVERLAY_SPEC = {
    "fable_status_frame": ("top_left", (3, 3), (120, 38)),
    "fable_minimap": ("top_right", (-14, 20), (72, 72)),
    "fable_map_details_frame": ("top_right", (-4, 92), (92, 10)),
    "fable_gold_frame": ("bottom_left", (4, -5), (68, 22)),
}

CLIP_SPEC = {
    "fable_eye_clip": ("top_right", (-55, 13), (22, 18), -40, 1.0),
    "fable_clock_clip": ("top_right", (-23, 13), (18, 18), -60, 1.0),
    "fable_radar_clip": ("top_right", (-24, 31), (52, 39), -29, 0.36),
    "fable_map_details_clip": ("top_right", (-5, 94), (90, 6), -80, 0.42),
    "fable_gold_clip": ("bottom_left", (31, -13), (32, 6), -84, 0.42),
    "fable_notice_clip": ("bottom_right", (-6, -31), (150, 5), -88, 0.42),
    "fable_wanted_clip": ("top_middle", (0, 6), (112, 18), -158, 0.72),
}
MIN_ACTIONBAR_LABEL_WIDTH = 320

# Each slicer label is scrolled by -(line_index * BASE_LINE_HEIGHT * font_scale)
# so only its target payload line peeks through the clip. The line indices below
# are the contract from fable_hud.js payload(): 4 status-ish lines, then eye (4),
# a CG.blank spacer (5), clock (6), another spacer (7), RADAR_SIZE(=11) radar rows
# on 8..18, then nav (19), gold (20), notice (21). The spacers below the eye and
# dial absorb the 16px glyph's overhang so neither bleeds into the other's window.
# Because the scroll error grows with line index, the deep lines (nav/gold/notice)
# are the ones that silently drift — so they are checked arithmetically here, not
# just against the hand-copied offsets above.
BASE_LINE_HEIGHT = 10
PAYLOAD_LINE = {
    "fable_eye_clip": 4,
    "fable_clock_clip": 6,
    "fable_radar_clip": 8,
    "fable_map_details_clip": 19,
    "fable_gold_clip": 20,
    "fable_notice_clip": 21,
    "fable_wanted_clip": 22,
}

# Broad regions taken from the supplied Fable HUD reference. These are
# intentionally tolerant of GUI scale while still catching major drift.
TARGET_ZONES = {
    "status": (0.00, 0.00, 0.30, 0.24),
    "map": (0.76, 0.08, 1.00, 0.40),
    "map_details": (0.72, 0.35, 1.00, 0.48),
    "eye": (0.72, 0.00, 0.92, 0.14),
    "dial": (0.83, 0.00, 1.00, 0.14),
    "gold": (0.00, 0.78, 0.28, 1.00),
    "wanted": (0.35, 0.00, 0.65, 0.15),
}


def controls(panel: dict) -> dict[str, dict]:
    found = {}
    for entry in panel.get("controls", []):
        if entry:
            name, value = next(iter(entry.items()))
            found[name] = value
    return found


def check(results: list[tuple[bool, str]], condition: bool, message: str) -> None:
    results.append((bool(condition), message))


def pair(value) -> tuple:
    return tuple(value)


def anchor_rect(anchor: str, offset, size, canvas=CANVAS, scale=UI_SCALE):
    width, height = size[0] * scale, size[1] * scale
    ox, oy = offset[0] * scale, offset[1] * scale
    cw, ch = canvas
    if anchor == "top_left":
        x, y = ox, oy
    elif anchor == "top_right":
        x, y = cw + ox - width, oy
    elif anchor == "bottom_left":
        x, y = ox, ch + oy - height
    elif anchor == "bottom_right":
        x, y = cw + ox - width, ch + oy - height
    elif anchor == "bottom_middle":
        x, y = cw / 2 + ox - width / 2, ch + oy - height
    elif anchor == "top_middle":
        x, y = cw / 2 + ox - width / 2, oy
    else:
        raise ValueError(f"unsupported anchor: {anchor}")
    return tuple(round(v) for v in (x, y, x + width, y + height))


def inside_zone(rect, zone) -> bool:
    width, height = CANVAS
    target = (
        zone[0] * width,
        zone[1] * height,
        zone[2] * width,
        zone[3] * height,
    )
    return (
        rect[0] >= target[0]
        and rect[1] >= target[1]
        and rect[2] <= target[2]
        and rect[3] <= target[3]
    )


def glyph_cell(sheet: Image.Image, codepoint: int) -> Image.Image:
    col = codepoint & 0xF
    row = (codepoint >> 4) & 0xF
    return sheet.crop((col * 16, row * 16, col * 16 + 16, row * 16 + 16))


def static_audit():
    data = json.loads(HUD_JSON.read_text(encoding="utf-8"))
    script = HUD_SCRIPT.read_text(encoding="utf-8")
    overlay = controls(data["fable_hud_overlay"])
    actionbar = controls(data["hud_actionbar_text"])
    results: list[tuple[bool, str]] = []

    for name, (anchor, offset, size) in OVERLAY_SPEC.items():
        control = overlay.get(name)
        check(results, control is not None, f"overlay contains {name}")
        if not control:
            continue
        check(results, control.get("anchor_from") == anchor, f"{name} uses {anchor}")
        check(results, pair(control.get("offset", ())) == offset, f"{name} offset is {offset}")
        check(results, pair(control.get("size", ())) == size, f"{name} size is {size}")

    for name, (anchor, offset, size, line_offset, font_scale) in CLIP_SPEC.items():
        control = actionbar.get(name)
        check(results, control is not None, f"action-bar slicer contains {name}")
        if not control:
            continue
        check(results, control.get("anchor_from") == anchor, f"{name} uses {anchor}")
        check(results, pair(control.get("offset", ())) == offset, f"{name} offset is {offset}")
        check(results, pair(control.get("size", ())) == size, f"{name} size is {size}")
        label = next(iter(controls(control).values()))
        check(
            results,
            label.get("size", [0])[0] >= MIN_ACTIONBAR_LABEL_WIDTH,
            f"{name} keeps the shared action-bar payload on logical lines",
        )
        check(results, label.get("offset", [None, None])[1] == line_offset,
              f"{name} reads action-bar line offset {line_offset}")
        check(results, label.get("font_scale_factor") == font_scale,
              f"{name} font scale is {font_scale}")
        # The offset must actually land on the payload line it is meant to show.
        # 4px-per-line rounding silently undershoots the true 10*scale pitch, so
        # the deep lines slide up by ~a line and (e.g.) the nav string bleeds into
        # the gold purse. Verify offset == -round(line_index * 10 * scale).
        line_index = PAYLOAD_LINE.get(name)
        if line_index is not None:
            expected = -round(line_index * BASE_LINE_HEIGHT * font_scale)
            actual = label.get("offset", [None, None])[1]
            check(
                results,
                actual is not None and abs(actual - expected) <= 1,
                f"{name} offset {actual} lands on payload line {line_index} "
                f"(expected ~{expected})",
            )

    check(results, bool(re.search(r"const RADAR_SIZE = 11;", script)), "radar is 11x11")
    check(results, "const RADAR_BLOCKS_PER_CELL = 3;" in script, "radar samples every 3 blocks")
    check(results, "horizontalBasis(player)" in script, "radar uses yaw-stable rotation basis")
    check(results, "String.fromCodePoint(0xE920" in script, "day dial follows world time")
    check(results, "return `§f${dial}`;" in script, "day dial has no text label")
    check(results, "return CG.water" in script, "map selects baked-colour glyphs")
    check(
        results,
        re.search(r"`§f\$\{eyeGlyph\}`,\s*CG\.blank,\s*clock\(\),\s*CG\.blank,", script) is not None,
        "eye and day dial each get a CG.blank spacer so neither bleeds into the other",
    )
    check(results, "Line 20 is intentionally coin-only" in script, "coin/map line contract is documented")
    check(
        results,
        'multiplier > 0 ? `§6× ${multiplier}` : CG.blank' in script,
        "empty multiplier preserves its payload row",
    )
    check(
        results,
        "const noticeText = noticeActive ? notice.text : CG.blank;" in script,
        "empty notice preserves its payload row",
    )
    check(results, "function wantedStars(player)" in script, "wanted heat has a dedicated HUD payload row")
    check(results, '"\\uE946".repeat(heat)' in script, "wanted heat repeats the authored star glyph")
    root = controls(data["root_panel"])
    check(
        results,
        "mob_effects_renderer@mob_effects_renderer" not in root,
        "vanilla effect icons do not overlap the custom map header",
    )

    required = [
        "status_frame.png", "minimap.png", "map_details.png",
        "gold.png", "eye_open.png",
        "eye_partial.png", "eye_closed.png", "clock.png",
        "wanted_star.png",
    ]
    for filename in required:
        check(results, (HUD_TEXTURES / filename).exists(), f"texture exists: {filename}")

    if GLYPHS.exists():
        sheet = Image.open(GLYPHS).convert("RGBA")
        eye_cells = [glyph_cell(sheet, code) for code in (0xE900, 0xE901, 0xE902)]
        check(results, all(cell.getbbox() for cell in eye_cells), "all three eye states have glyph art")
        eye_colours = [
            len(cell.getcolors(maxcolors=4096) or [])
            for cell in eye_cells
        ]
        check(results, min(eye_colours) > 24, "eye glyphs preserve authored full-colour art")
        check(
            results,
            all(glyph_cell(sheet, 0xE920 + phase).getbbox() for phase in range(24)),
            "all 24 day-cycle glyphs exist",
        )
        clock_source = Image.open(HUD_TEXTURES / "clock.png").convert("RGBA")
        expected_clock_cells = []
        for phase in range(24):
            rotation_degrees = phase * 15 - 90
            rotated = clock_source if not rotation_degrees else clock_source.rotate(
                rotation_degrees,
                resample=Image.Resampling.BICUBIC,
                expand=False,
                center=((clock_source.width - 1) / 2, (clock_source.height - 1) / 2),
            )
            expected_clock_cells.append(
                rotated.resize((16, 16), Image.Resampling.LANCZOS)
            )
        check(
            results,
            all(
                ImageChops.difference(
                    glyph_cell(sheet, 0xE920 + phase),
                    expected_clock_cells[phase],
                ).getbbox() is None
                for phase in range(24)
            ),
            "day-cycle frames rotate the whole dial to keep the current time at the top",
        )
        wanted_source = Image.open(HUD_TEXTURES / "wanted_star.png").convert("RGBA")
        check(
            results,
            ImageChops.difference(
                glyph_cell(sheet, 0xE946),
                wanted_source.resize((16, 16), Image.Resampling.LANCZOS),
            ).getbbox() is None,
            "wanted-star glyph preserves the generated Fable emblem",
        )
        map_codes = list(range(0xE910, 0xE920)) + [0xE944, 0xE945]
        map_cells = [glyph_cell(sheet, code) for code in map_codes]
        check(results, all(cell.getbbox() for cell in map_cells), "all coloured map cells exist")
        opaque_colours = {
            pixel[:3]
            for cell in map_cells
            for pixel in cell.get_flattened_data()
            if pixel[3] > 96
        }
        check(results, len(opaque_colours) >= 18, "map glyph sheet contains a baked RGB palette")
    else:
        check(results, False, "HUD glyph sheet exists")

    layout_rects = {
        "status": anchor_rect(*OVERLAY_SPEC["fable_status_frame"]),
        "map": anchor_rect(*OVERLAY_SPEC["fable_minimap"]),
        "map_details": anchor_rect(*OVERLAY_SPEC["fable_map_details_frame"]),
        "eye": anchor_rect(*CLIP_SPEC["fable_eye_clip"][:3]),
        "dial": anchor_rect(*CLIP_SPEC["fable_clock_clip"][:3]),
        "gold": anchor_rect(*OVERLAY_SPEC["fable_gold_frame"]),
        "wanted": anchor_rect(*CLIP_SPEC["fable_wanted_clip"][:3]),
    }
    for name, rect in layout_rects.items():
        check(results, inside_zone(rect, TARGET_ZONES[name]), f"{name} stays in its Fable reference zone")
    centres = [
        (layout_rects[name][0] + layout_rects[name][2]) / 2
        for name in ("map", "map_details")
    ]
    radar_rect = anchor_rect(*CLIP_SPEC["fable_radar_clip"][:3])
    centres.append((radar_rect[0] + radar_rect[2]) / 2)
    check(results, max(centres) - min(centres) <= 1, "minimap, map content, and detail rail are centered")
    check(
        results,
        max(layout_rects["eye"][3], layout_rects["dial"][3]) - layout_rects["map"][1] == 11 * UI_SCALE,
        "eye and day dial slightly overlap the minimap ornament",
    )
    check(results, layout_rects["dial"][0] - layout_rects["eye"][2] == 14 * UI_SCALE,
          "eye and day dial use the balanced fourteen-unit gap")
    map_center = (layout_rects["map"][0] + layout_rects["map"][2]) / 2
    icon_pair_center = (layout_rects["eye"][0] + layout_rects["dial"][2]) / 2
    check(results, map_center == icon_pair_center,
          "eye and day dial are balanced over the minimap")

    return data, results, layout_rects


def font(size: int):
    for name in ("arial.ttf", "segoeui.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            pass
    return ImageFont.load_default()


def background():
    image = Image.new("RGB", CANVAS, (54, 66, 42))
    draw = ImageDraw.Draw(image)
    for y in range(CANVAS[1]):
        t = y / CANVAS[1]
        draw.line((0, y, CANVAS[0], y), fill=(round(58 + 28 * t), round(68 - 12 * t), round(44 - 18 * t)))
    draw.ellipse((300, 80, 930, 650), fill=(99, 83, 52))
    draw.rectangle((0, 500, 1280, 720), fill=(47, 68, 34))
    return image.convert("RGBA")


def paste_control(canvas: Image.Image, control: dict):
    texture = control["texture"].removeprefix("textures/ui/fable_hud/")
    source = Image.open(HUD_TEXTURES / f"{texture}.png").convert("RGBA")
    rect = anchor_rect(control["anchor_from"], control["offset"], control["size"])
    source = source.resize((rect[2] - rect[0], rect[3] - rect[1]), Image.Resampling.LANCZOS)
    canvas.alpha_composite(source, (rect[0], rect[1]))
    return rect


def render_preview(data: dict, layout_rects: dict[str, tuple]):
    overlay = controls(data["fable_hud_overlay"])
    canvas = background()
    for name in OVERLAY_SPEC:
        paste_control(canvas, overlay[name])

    draw = ImageDraw.Draw(canvas)
    # Representative status bars.
    for y, colour, ratio in ((45, (218, 52, 50), 0.78), (78, (57, 91, 219), 0.66), (129, (219, 167, 45), 0.55)):
        draw.rounded_rectangle((100, y, 350, y + 13), 5, fill=(22, 18, 15), outline=(205, 151, 64), width=2)
        draw.rounded_rectangle((104, y + 3, 104 + round(240 * ratio), y + 10), 3, fill=colour)

    # Coloured 11x11 camera-relative map sample.
    map_rect = layout_rects["map"]
    cx = (map_rect[0] + map_rect[2]) / 2
    cy = (map_rect[1] + map_rect[3]) / 2
    tile = 11
    palette = [(69, 124, 60), (46, 94, 56), (55, 126, 150), (166, 139, 74), (103, 101, 92)]
    for row in range(11):
        for col in range(11):
            if ((col - 5) ** 2 + (row - 5) ** 2) ** 0.5 > 5.2:
                continue
            colour = palette[(row * 3 + col * 5 + (row - col) ** 2) % len(palette)]
            x = round(cx + (col - 5.5) * tile)
            y = round(cy + (row - 5.5) * tile)
            draw.rectangle((x, y, x + tile - 1, y + tile - 1), fill=colour)
    draw.polygon(((cx, cy - 11), (cx - 7, cy + 8), (cx, cy + 4), (cx + 7, cy + 8)), fill=(244, 244, 224))

    text_font = font(15)
    detail_rect = layout_rects["map_details"]
    draw.text((detail_rect[0] + 35, detail_rect[1] + 7), "NE · Heroes' Guild · 121m",
              fill=(246, 215, 119), font=text_font)

    eye_rect = anchor_rect(*CLIP_SPEC["fable_eye_clip"][:3])
    eye = Image.open(HUD_TEXTURES / "eye_open.png").convert("RGBA")
    eye = eye.resize((eye_rect[2] - eye_rect[0], eye_rect[3] - eye_rect[1]), Image.Resampling.LANCZOS)
    canvas.alpha_composite(eye, (eye_rect[0], eye_rect[1]))
    dial_rect = anchor_rect(*CLIP_SPEC["fable_clock_clip"][:3])
    dial = Image.open(HUD_TEXTURES / "clock.png").convert("RGBA")
    dial = dial.resize(
        (dial_rect[2] - dial_rect[0], dial_rect[3] - dial_rect[1]),
        Image.Resampling.LANCZOS,
    )
    canvas.alpha_composite(dial, (dial_rect[0], dial_rect[1]))
    gold_rect = layout_rects["gold"]
    draw.text((gold_rect[0] + 94, gold_rect[1] + 27), "4608", fill=(255, 226, 139), font=font(18))
    wanted_rect = layout_rects["wanted"]
    wanted_star = Image.open(HUD_TEXTURES / "wanted_star.png").convert("RGBA")
    wanted_size = round(12 * UI_SCALE)
    wanted_star = wanted_star.resize((wanted_size, wanted_size), Image.Resampling.LANCZOS)
    wanted_gap = round(2 * UI_SCALE)
    wanted_width = wanted_size * 4 + wanted_gap * 3
    wanted_x = round((wanted_rect[0] + wanted_rect[2] - wanted_width) / 2)
    wanted_y = round((wanted_rect[1] + wanted_rect[3] - wanted_size) / 2)
    for index in range(4):
        canvas.alpha_composite(wanted_star, (wanted_x + index * (wanted_size + wanted_gap), wanted_y))

    guide = background()
    guide_draw = ImageDraw.Draw(guide, "RGBA")
    for name, zone in TARGET_ZONES.items():
        rect = (
            round(zone[0] * CANVAS[0]), round(zone[1] * CANVAS[1]),
            round(zone[2] * CANVAS[0]), round(zone[3] * CANVAS[1]),
        )
        guide_draw.rectangle(rect, fill=(66, 156, 106, 40), outline=(109, 238, 161, 220), width=3)
        guide_draw.text((rect[0] + 8, rect[1] + 8), name.replace("_", " ").upper(),
                        fill=(228, 255, 238, 255), font=font(16))
    for name, rect in layout_rects.items():
        guide_draw.rectangle(rect, outline=(255, 204, 75, 255), width=3)
        guide_draw.text((rect[0] + 5, rect[3] + 4), f"implemented: {name}",
                        fill=(255, 224, 137, 255), font=font(13))

    output = Image.new("RGB", (CANVAS[0] * 2, CANVAS[1] + 42), (20, 18, 15))
    output.paste(canvas.convert("RGB"), (0, 42))
    output.paste(guide.convert("RGB"), (CANVAS[0], 42))
    title = ImageDraw.Draw(output)
    title.text((16, 12), "IMPLEMENTED HUD PREVIEW", fill=(245, 224, 172), font=font(18))
    title.text((CANVAS[0] + 16, 12), "FABLE REFERENCE ZONES vs IMPLEMENTED BOUNDS",
               fill=(245, 224, 172), font=font(18))
    return output


def compare_images(reference: Path, capture: Path):
    ref = Image.open(reference).convert("RGB")
    cap = Image.open(capture).convert("RGB").resize(ref.size, Image.Resampling.LANCZOS)
    diff = ImageChops.difference(ref, cap)
    mean_error = sum(ImageStat.Stat(diff).mean) / 3
    heat = diff.point(lambda value: min(255, value * 3))
    comparison = Image.new("RGB", (ref.width * 3, ref.height), "black")
    comparison.paste(ref, (0, 0))
    comparison.paste(cap, (ref.width, 0))
    comparison.paste(heat, (ref.width * 2, 0))
    return comparison, mean_error


def report(results, mean_error=None):
    passed = sum(ok for ok, _ in results)
    lines = [
        "# HUD Audit",
        "",
        f"- Checks passed: {passed}/{len(results)}",
        "- Layout reference: supplied Fable HUD composition",
        "- Map contract: 11×11 yaw-rotating coloured terrain grid",
        "- Payload contract: eye 4, dial 6, map 19, gold 20, notice 21, wanted heat 22",
        "",
        "## Results",
        "",
    ]
    lines.extend(f"- {'PASS' if ok else 'FAIL'} — {message}" for ok, message in results)
    if mean_error is not None:
        lines.extend(("", "## Screenshot comparison", "", f"- Mean absolute RGB error: {mean_error:.2f}/255"))
    lines.extend(("", "Generated by `python scripts/audit_hud.py`."))
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="validate without writing audit images")
    parser.add_argument("--reference", type=Path)
    parser.add_argument("--capture", type=Path)
    args = parser.parse_args()
    if bool(args.reference) != bool(args.capture):
        parser.error("--reference and --capture must be provided together")

    data, results, layout_rects = static_audit()
    mean_error = None
    if not args.check:
        OUTPUT.mkdir(parents=True, exist_ok=True)
        render_preview(data, layout_rects).save(OUTPUT / "hud_audit.png")
        if args.reference and args.capture:
            comparison, mean_error = compare_images(args.reference, args.capture)
            comparison.save(OUTPUT / "hud_capture_comparison.png")
        (OUTPUT / "HUD_AUDIT.md").write_text(report(results, mean_error), encoding="utf-8")

    failed = [message for ok, message in results if not ok]
    print(f"Fable HUD audit: {len(results) - len(failed)}/{len(results)} checks passed")
    for message in failed:
        print(f"  FAIL {message}")
    if not args.check:
        print(f"wrote {OUTPUT / 'hud_audit.png'}")
        print(f"wrote {OUTPUT / 'HUD_AUDIT.md'}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())

"""Faithful HUD slice preview.

The audit's render_preview paints *placeholder* text at fixed coordinates, so it
cannot reveal action-bar slicing bugs (it showed a perfect HUD while the game put
the nav string in the coin purse). This script instead reproduces what Bedrock
actually does: it builds the real multi-line payload -- the same §-coded strings
fable_hud.js feeds setActionBar, bars included -- then for every fable_*_clip it
scrolls a full-payload label by the clip's offset and crops it to the clip window,
so the image shows the content that truly lands in each frame.

Run: python scripts/preview_hud_faithful.py  ->  screenshots/ui/hud_faithful.png
"""
from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageDraw

from audit_hud import (
    CANVAS, UI_SCALE, HUD_TEXTURES, OVERLAY_SPEC,
    anchor_rect, background, controls, font, paste_control,
)
from gen_hud_font import clock_glyph

ROOT = Path(__file__).resolve().parents[1]
HUD_JSON = ROOT / "packs" / "Fablecraft_RP" / "ui" / "hud_screen.json"
OUTPUT = ROOT / "screenshots" / "ui" / "hud_faithful.png"

BASE_LINE_HEIGHT = 10  # UI units per text line; pitch = BASE * font_scale.

# Bedrock §-code palette.
SECTION_COLOURS = {
    "0": (0, 0, 0), "1": (0, 0, 170), "2": (0, 170, 0), "3": (0, 170, 170),
    "4": (170, 0, 0), "5": (170, 0, 170), "6": (255, 170, 0), "7": (170, 170, 170),
    "8": (85, 85, 85), "9": (85, 85, 255), "a": (85, 255, 85), "b": (85, 255, 255),
    "c": (255, 85, 85), "d": (255, 85, 255), "e": (255, 255, 85), "f": (255, 255, 255),
}


def bar(value, maximum, width, colour):
    """Mirror fable_hud.js bar(): filled run in colour, empty run in §8."""
    fill = round(value / maximum * width) if maximum else 0
    fill = max(0, min(width, fill))
    return f"{colour}{'█' * fill}§8{'█' * (width - fill)}"


def radar_grid():
    """11 rows of fixed-width terrain cells with the player marker dead-centre,
    standing in for the baked-colour glyph rows fable_hud.js emits on lines 6-16."""
    palette = ["a", "2", "a", "3", "a", "2", "a", "2", "3", "a", "2"]
    rows = []
    for r in range(11):
        cells = []
        for c in range(11):
            if r == 5 and c == 5:
                cells.append("§f█")              # player marker
            elif (r - 5) ** 2 + (c - 5) ** 2 > 30:
                cells.append("§0 ")              # outside the dial
            else:
                cells.append(f"§{palette[(r * 3 + c * 5) % len(palette)]}█")
        rows.append("".join(cells))
    return rows


# Representative payload, line-for-line with fable_hud.js payload(). Full bars
# (20/20, 100/100, 20/20) mirror the in-game screenshot's fresh-spawn state.
PAYLOAD = [
    f"{bar(20, 20, 12, '§c')} §f20/20",       # 0 health
    f"{bar(100, 100, 12, '§9')} §f100/100",   # 1 will
    f"{bar(20, 20, 12, '§6')} §f20/20",       # 2 hunger
    "",                                        # 3 multiplier (blank at x0)
    "§fEYE",                                   # 4 eye glyph (icon sliced over)
    "",                                        # 5 spacer — keeps the dial out of the eye window
    "§fDIAL",                                  # 6 day dial glyph (icon sliced over)
    "",                                        # 7 spacer — keeps the radar out of the dial window
    *radar_grid(),                             # 8..18 radar rows
    "§eNE §8· §6Heroes' Guild §8· §f121m",     # 19 nav
    "§64608",                                  # 20 gold
    "",                                        # 21 notice (blank when idle)
    "\uE946\uE946\uE946\uE946",                 # 22 wanted heat
]


def runs(text):
    """Split a §-coded string into (segment, rgb) runs."""
    out, colour, buf, i = [], (255, 255, 255), "", 0
    while i < len(text):
        if text[i] == "§" and i + 1 < len(text):
            if buf:
                out.append((buf, colour))
                buf = ""
            colour = SECTION_COLOURS.get(text[i + 1], colour)
            i += 2
        else:
            buf += text[i]
            i += 1
    if buf:
        out.append((buf, colour))
    return out


def slice_clip(canvas, clip, lines):
    """Reproduce one clips_children window over the scrolled payload label."""
    win = anchor_rect(clip["anchor_from"], tuple(clip["offset"]), tuple(clip["size"]))
    win_w, win_h = win[2] - win[0], win[3] - win[1]
    label = next(iter(controls(clip).values()))
    scale = label.get("font_scale_factor", 1.0)
    align = label.get("text_alignment", "left")
    label_off_y = label.get("offset", [0, 0])[1]

    pitch = BASE_LINE_HEIGHT * scale * UI_SCALE
    text_font = font(max(6, round(pitch)))

    strip = Image.new("RGBA", (win_w, round(len(lines) * pitch + pitch)), (0, 0, 0, 0))
    draw = ImageDraw.Draw(strip)
    for i, line in enumerate(lines):
        segs = runs(line)
        if not segs:
            continue
        total = sum(draw.textlength(t, font=text_font) for t, _ in segs)
        if align == "center":
            x = (win_w - total) / 2
        elif align == "right":
            x = win_w - total - 2
        else:
            x = 2
        y = round(i * pitch)
        for t, colour in segs:
            width = draw.textlength(t, font=text_font)
            if t and set(t) <= {"█"}:
                # Bars are runs of full-block glyphs. Draw them as cell-height
                # rectangles (inset a touch for the track) instead of the font
                # glyph, which over-extends its cell and would fake a bleed the
                # exact-cell engine never produces.
                draw.rectangle((x, y + pitch * 0.12, x + width, y + pitch * 0.88),
                               fill=colour + (255,))
            else:
                draw.text((x, y), t, fill=colour + (255,), font=text_font, anchor="la")
            x += width

    crop_y0 = round(-label_off_y * UI_SCALE)  # label is scrolled up by |offset|
    visible = strip.crop((0, crop_y0, win_w, crop_y0 + win_h))
    canvas.alpha_composite(visible, (win[0], win[1]))


# A glyph_E9 cell is 16px and renders taller than the 10px line pitch: in game a
# single glyph occupies ~1.6x its line. That is why the eye/dial windows (18px,
# ~one cell) need a blank spacer on the line below — otherwise the next line's
# glyph, drawn only one 10px pitch down, overlaps into the bottom of the window.
GLYPH_CELL_RATIO = 1.6


def slice_icon(canvas, clip, icon, below):
    """Honestly slice a single-glyph window (detection eye / day dial).

    The live HUD renders these as font glyphs, each ~1.6x its line pitch tall, so
    the line *below* (one pitch down) overlaps unless it is blank. The old preview
    pasted clean art at the full clip rect, hiding the bleed that put the green
    radar row inside the dial window. Model the real slice: lay the icon on its
    payload line at true cell size and the next line below it, then crop to the
    window. `below=None` means that line is a CG.blank spacer (the live fix), so
    nothing leaks; pass art/colour to prove what a missing spacer would leak.
    """
    win = anchor_rect(clip["anchor_from"], tuple(clip["offset"]), tuple(clip["size"]))
    win_w, win_h = win[2] - win[0], win[3] - win[1]
    label = next(iter(controls(clip).values()))
    scale = label.get("font_scale_factor", 1.0)
    label_off_y = label.get("offset", [0, 0])[1]
    pitch = round(BASE_LINE_HEIGHT * scale * UI_SCALE)
    cell = round(pitch * GLYPH_CELL_RATIO)
    crop_y0 = round(-label_off_y * UI_SCALE)
    line = round(crop_y0 / pitch)  # payload line index that lands at the window top

    strip = Image.new("RGBA", (win_w, crop_y0 + win_h + cell), (0, 0, 0, 0))
    # Icon first, neighbour after: later payload lines are drawn on top in game.
    strip.alpha_composite(
        icon.resize((cell, cell), Image.Resampling.LANCZOS), ((win_w - cell) // 2, line * pitch))
    if below is not None:
        band = (Image.new("RGBA", (win_w, cell), below) if isinstance(below, tuple)
                else below.resize((cell, cell), Image.Resampling.LANCZOS))
        for bx in range(0, win_w, band.width):
            strip.alpha_composite(band, (bx, (line + 1) * pitch))
    canvas.alpha_composite(strip.crop((0, crop_y0, win_w, crop_y0 + win_h)), (win[0], win[1]))

def slice_wanted(canvas, clip, heat):
    """Render the generated wanted emblem at the same scale as its font glyph."""
    win = anchor_rect(clip["anchor_from"], tuple(clip["offset"]), tuple(clip["size"]))
    win_w, win_h = win[2] - win[0], win[3] - win[1]
    label = next(iter(controls(clip).values()))
    cell = round(16 * label.get("font_scale_factor", 1.0) * UI_SCALE)
    gap = round(2 * UI_SCALE)
    star = Image.open(HUD_TEXTURES / "wanted_star.png").convert("RGBA")
    star = star.resize((cell, cell), Image.Resampling.LANCZOS)
    total = heat * cell + max(0, heat - 1) * gap
    x = win[0] + round((win_w - total) / 2)
    y = win[1] + round((win_h - cell) / 2)
    for index in range(heat):
        canvas.alpha_composite(star, (x + index * (cell + gap), y))


def main():
    data = json.loads(HUD_JSON.read_text(encoding="utf-8"))
    overlay = controls(data["fable_hud_overlay"])
    clips = controls(data["hud_actionbar_text"])

    canvas = background()
    for name in OVERLAY_SPEC:
        paste_control(canvas, overlay[name])

    # Eye + day-dial are real font-glyph slices. Slice them like the game does so
    # any window/pitch mismatch shows its bleed. Each now has a CG.blank spacer on
    # the line below (below=None), so the dial no longer leaks into the eye and the
    # green radar row no longer leaks into the dial. The dial uses the live
    # midnight rotation so the preview proves the night side moves to the top.
    eye_art = Image.open(HUD_TEXTURES / "eye_open.png").convert("RGBA")
    dial_art = clock_glyph(18)  # midnight, to verify the night side is at top
    slice_icon(canvas, clips["fable_eye_clip"], eye_art, None)
    slice_icon(canvas, clips["fable_clock_clip"], dial_art, None)

    for name, clip in clips.items():
        if name in ("fable_eye_clip", "fable_clock_clip"):
            continue
        if name == "fable_wanted_clip":
            slice_wanted(canvas, clip, 4)
            continue
        slice_clip(canvas, clip, PAYLOAD)

    out = Image.new("RGB", (CANVAS[0], CANVAS[1] + 42), (20, 18, 15))
    out.paste(canvas.convert("RGB"), (0, 42))
    ImageDraw.Draw(out).text(
        (16, 12), "FAITHFUL SLICE  (real payload through the live clip offsets)",
        fill=(245, 224, 172), font=font(18),
    )
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    out.save(OUTPUT)
    print(f"wrote {OUTPUT}")


if __name__ == "__main__":
    main()

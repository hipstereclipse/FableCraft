"""Generate the Fable HUD glyph sheet (font/glyph_E9.png).

The live HUD ([fable_hud.js]) packs the whole status read-out into one
action-bar string which hud_screen.json slices into the ornate frames.  The
radar/marker cells MUST be fixed width or the 11x11 grid shears apart, and the
glyphs must actually exist in the font or Minecraft draws "tofu" boxes.  So we
author our own private-use glyphs (U+E9xx) here instead of borrowing Unicode
box-drawing characters from the default proportional font.

Determinism rules that keep the grid square without in-game tuning:
  * Every radar/marker glyph (and the blank cell) shares the exact same left
    and right pixel extent via two near-invisible anchor pixels, so each cell
    advances the cursor by the same amount regardless of its motif.
  * Glyphs are pure white so the existing section-colour codes (e.g. "§c") tint
    them; one motif serves many colours.
"""
from PIL import Image

from fc_lib import RP

CELL = 16          # glyph_E9.png is a 16x16 grid of 16px cells -> 256x256
SHEET = CELL * 16
HUD_TEXTURES = RP / "textures" / "ui" / "fable_hud"

# Pixel legend ---------------------------------------------------------------
#   #  solid white      +  soft white edge      .  invisible width anchor
W = (255, 255, 255, 255)
S = (255, 255, 255, 170)
A = (255, 255, 255, 16)
LEGEND = {"#": W, "+": S, ".": A}

# Each glyph is 16 rows x 16 cols.  Radar/marker motifs stay inside columns
# 2..13 so the shared anchor pixels (added below) define a uniform advance.
GLYPHS = {
    # --- detection eye, drawn so the three states differ by overall height ---
    "eye_open": [
        "                ",
        "                ",
        "                ",
        "     ######     ",
        "   ##      ##   ",
        "  #   ####   #  ",
        " #   ######   # ",
        " #   ######   # ",
        "  #   ####   #  ",
        "   ##      ##   ",
        "     ######     ",
        "                ",
        "                ",
        "                ",
        "                ",
        "                ",
    ],
    "eye_half": [
        "                ",
        "                ",
        "                ",
        "                ",
        "                ",
        "   ##########   ",
        "  #   ####   #  ",
        " #   ######   # ",
        "  #   ####   #  ",
        "   ##      ##   ",
        "    ########    ",
        "                ",
        "                ",
        "                ",
        "                ",
        "                ",
    ],
    "eye_closed": [
        "                ",
        "                ",
        "                ",
        "                ",
        "                ",
        "                ",
        "                ",
        " #            # ",
        "  ############  ",
        "   #        #   ",
        "    ##    ##    ",
        "                ",
        "                ",
        "                ",
        "                ",
        "                ",
    ],
    # --- radar markers (white; tinted at runtime) ---------------------------
    "player": [
        "                ",
        "                ",
        "                ",
        "       ##       ",
        "       ##       ",
        "      ####      ",
        "      ####      ",
        "     ######     ",
        "     ######     ",
        "    ########    ",
        "    ########    ",
        "   ##########   ",
        "   ##########   ",
        "                ",
        "                ",
        "                ",
    ],
    "enemy": [
        "                ",
        "                ",
        "                ",
        "                ",
        "    ########    ",
        "    ########    ",
        "    ########    ",
        "    ########    ",
        "    ########    ",
        "    ########    ",
        "    ########    ",
        "    ########    ",
        "                ",
        "                ",
        "                ",
        "                ",
    ],
    "friendly": [
        "                ",
        "                ",
        "                ",
        "                ",
        "                ",
        "      ####      ",
        "     ######     ",
        "     ######     ",
        "     ######     ",
        "      ####      ",
        "                ",
        "                ",
        "                ",
        "                ",
        "                ",
        "                ",
    ],
    "landmark": [
        "                ",
        "                ",
        "                ",
        "       ##       ",
        "      #  #      ",
        "     #    #     ",
        "    #      #    ",
        "   #        #   ",
        "    #      #    ",
        "     #    #     ",
        "      #  #      ",
        "       ##       ",
        "                ",
        "                ",
        "                ",
        "                ",
    ],
    "terrain": [
        "                ",
        "                ",
        "   ++++++++++   ",
        "   +########+   ",
        "   +########+   ",
        "   +########+   ",
        "   +########+   ",
        "   +########+   ",
        "   +########+   ",
        "   +########+   ",
        "   +########+   ",
        "   ++++++++++   ",
        "                ",
        "                ",
        "                ",
        "                ",
    ],
    "water": [
        "                ",
        "                ",
        "   ++++++++++   ",
        "   ###++#####   ",
        "   ++#####++#   ",
        "   #####++###   ",
        "   ##++######   ",
        "   +#####++##   ",
        "   ####++####   ",
        "   #++######+   ",
        "   ++++++++++   ",
        "                ",
        "                ",
        "                ",
        "                ",
        "                ",
    ],
    "tree": [
        "                ",
        "                ",
        "                ",
        "      ####      ",
        "     ######     ",
        "    ########    ",
        "    ########    ",
        "     ######     ",
        "       ##       ",
        "       ##       ",
        "      ####      ",
        "                ",
        "                ",
        "                ",
        "                ",
        "                ",
    ],
    "peak": [
        "                ",
        "                ",
        "                ",
        "                ",
        "       ##       ",
        "      #  #      ",
        "     #    #     ",
        "    #      #    ",
        "   #        #   ",
        "   ##########   ",
        "                ",
        "                ",
        "                ",
        "                ",
        "                ",
        "                ",
    ],
    "path": [
        "                ",
        "                ",
        "   +++####+++   ",
        "   ++######++   ",
        "   ++######++   ",
        "   +++######+   ",
        "   +++######+   ",
        "   ++######++   ",
        "   ++######++   ",
        "   +######+++   ",
        "   +######+++   ",
        "   ++++++++++   ",
        "                ",
        "                ",
        "                ",
        "                ",
    ],
    "structure": [
        "                ",
        "                ",
        "   ++++++++++   ",
        "   +########+   ",
        "   +##++++##+   ",
        "   +##+##+##+   ",
        "   +##+##+##+   ",
        "   +##++++##+   ",
        "   +########+   ",
        "   +########+   ",
        "   ++++++++++   ",
        "                ",
        "                ",
        "                ",
        "                ",
        "                ",
    ],
    "field": [
        "                ",
        "                ",
        "   ++++++++++   ",
        "   +#++#++##+   ",
        "   +#++#++##+   ",
        "   +#++#++##+   ",
        "   +#++#++##+   ",
        "   +#++#++##+   ",
        "   +#++#++##+   ",
        "   +#++#++##+   ",
        "   ++++++++++   ",
        "                ",
        "                ",
        "                ",
        "                ",
        "                ",
    ],
    "blank": ["                "] * 16,
}
GLYPHS.update({
    "lava": GLYPHS["water"],
    "snow": GLYPHS["terrain"],
    "sand": GLYPHS["terrain"],
    "earth": GLYPHS["terrain"],
    "stone": GLYPHS["structure"],
    "lowland": GLYPHS["terrain"],
})

# Custom glyph sheets preserve source RGB more reliably than Bedrock applies
# section-code tints to private-use characters. Bake the map palette directly
# into each cell so the minimap remains coloured in game.
GLYPH_PALETTES = {
    "player": {"#": (242, 244, 226, 255), "+": (126, 204, 255, 255), ".": A},
    "enemy": {"#": (210, 51, 45, 255), "+": (255, 130, 76, 255), ".": A},
    "friendly": {"#": (91, 190, 91, 255), "+": (168, 232, 128, 255), ".": A},
    "landmark": {"#": (238, 185, 65, 255), "+": (255, 230, 139, 255), ".": A},
    "terrain": {"#": (82, 139, 67, 255), "+": (45, 91, 43, 255), ".": A},
    "water": {"#": (54, 135, 181, 255), "+": (111, 202, 224, 255), ".": A},
    "tree": {"#": (35, 87, 43, 255), "+": (78, 145, 69, 255), ".": A},
    "peak": {"#": (172, 178, 176, 255), "+": (103, 110, 111, 255), ".": A},
    "path": {"#": (178, 143, 84, 255), "+": (111, 85, 52, 255), ".": A},
    "blank": {"#": W, "+": S, ".": A},
    "structure": {"#": (143, 124, 96, 255), "+": (213, 175, 93, 255), ".": A},
    "field": {"#": (168, 139, 54, 255), "+": (226, 190, 77, 255), ".": A},
    "lava": {"#": (220, 67, 31, 255), "+": (255, 169, 48, 255), ".": A},
    "snow": {"#": (231, 244, 246, 255), "+": (174, 214, 231, 255), ".": A},
    "sand": {"#": (216, 191, 121, 255), "+": (244, 221, 159, 255), ".": A},
    "earth": {"#": (132, 87, 53, 255), "+": (84, 56, 38, 255), ".": A},
    "stone": {"#": (116, 122, 124, 255), "+": (76, 82, 84, 255), ".": A},
    "lowland": {"#": (69, 72, 67, 255), "+": (47, 51, 47, 255), ".": A},
}

# Sheet position (col, row) within the 16x16 grid -> code point U+E9{row}{col}.
PLACEMENT = {
    "eye_open": (0, 0),   # U+E900  seen
    "eye_closed": (1, 0),  # U+E901  clear (no NPC)
    "eye_half": (2, 0),   # U+E902  nearby, not looking
    "player": (0, 1),     # U+E910
    "enemy": (1, 1),      # U+E911
    "friendly": (2, 1),   # U+E912
    "landmark": (3, 1),   # U+E913
    "terrain": (4, 1),    # U+E914
    "water": (5, 1),      # U+E915
    "tree": (6, 1),       # U+E916
    "peak": (7, 1),       # U+E917
    "path": (8, 1),       # U+E918
    "blank": (9, 1),      # U+E919
    "structure": (10, 1), # U+E91A
    "field": (11, 1),     # U+E91B
    "lava": (12, 1),      # U+E91C
    "snow": (13, 1),      # U+E91D
    "sand": (14, 1),      # U+E91E
    "earth": (15, 1),     # U+E91F
    "stone": (4, 4),      # U+E944
    "lowland": (5, 4),    # U+E945
    "wanted_star": (6, 4), # U+E946
}
PLACEMENT.update({
    f"clock_{phase:02d}": (phase % 16, 2 + phase // 16)
    for phase in range(24)
})

# Markers/terrain (not the eyes) get shared width anchors at cols 2 and 13.
ANCHORED = {n for n in PLACEMENT if PLACEMENT[n][1] == 1}
SOURCE_TEXTURES = {
    "eye_open": "eye_open.png",
    "eye_half": "eye_partial.png",
    "eye_closed": "eye_closed.png",
    "wanted_star": "wanted_star.png",
}


def texture_glyph(filename: str) -> Image.Image:
    """Downsample authored HUD art into one full-colour private-use glyph."""
    source = Image.open(HUD_TEXTURES / filename).convert("RGBA")
    return source.resize((CELL, CELL), Image.Resampling.LANCZOS)


def clock_glyph(phase: int) -> Image.Image:
    """Rotate the authored dial so the current game-time segment is at the top.

    The time path is dawn on the left, noon at the top, dusk on the right, and
    midnight at the bottom. Rotating the whole face by the inverse of that path
    keeps the current segment under the HUD's fixed top reading position without
    drawing a separate hand or marker that travels around the dial.
    """
    source = Image.open(HUD_TEXTURES / "clock.png").convert("RGBA")
    rotation_degrees = phase * 15 - 90
    if rotation_degrees:
        source = source.rotate(
            rotation_degrees,
            resample=Image.Resampling.BICUBIC,
            expand=False,
            center=((source.width - 1) / 2, (source.height - 1) / 2),
        )
    return source.resize((CELL, CELL), Image.Resampling.LANCZOS)


def main() -> None:
    sheet = Image.new("RGBA", (SHEET, SHEET), (0, 0, 0, 0))
    for name, (col, row) in PLACEMENT.items():
        ox, oy = col * CELL, row * CELL
        if name in SOURCE_TEXTURES:
            sheet.alpha_composite(texture_glyph(SOURCE_TEXTURES[name]), (ox, oy))
            continue
        if name.startswith("clock_"):
            sheet.alpha_composite(clock_glyph(int(name[-2:])), (ox, oy))
            continue

        rows = GLYPHS[name]
        palette = GLYPH_PALETTES.get(name, LEGEND)
        grid = [list(r.ljust(CELL)[:CELL]) for r in rows]
        if name in ANCHORED:
            grid[15][2] = "."
            grid[15][13] = "."
        for y, line in enumerate(grid):
            for x, ch in enumerate(line):
                colour = palette.get(ch)
                if colour:
                    sheet.putpixel((ox + x, oy + y), colour)
    out = RP / "font" / "glyph_E9.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(out)
    print(f"wrote {out.relative_to(RP.parent)} ({SHEET}x{SHEET}, {len(PLACEMENT)} glyphs)")


if __name__ == "__main__":
    main()

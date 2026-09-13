"""fc_pixelfont.py — a 5x7 pixel face for rendering in-game text in captures.

Every HUD string and menu label in a Minecraft screenshot is drawn in a pixel
font with a hard one-pixel drop shadow. Substituting a smooth proportional face
(DejaVu, Liberation, whatever PIL falls back to on the build machine) is the
single most obvious tell that an image was composited rather than captured, and
it shows up at every text size in the frame.

So the glyphs are authored here the same way scripts/gen_hud_font.py authors the
private-use HUD glyphs: as ASCII art, in code, with no font file to ship or
license. Glyphs are trimmed to their own ink width so the face is proportional
like Mojangles rather than fixed-pitch, and drawing is integer-scaled so it
stays crisp at any size.
"""
from __future__ import annotations

from PIL import Image, ImageDraw

HEIGHT = 7          # rows of ink
LINE = 9            # baseline-to-baseline, in font pixels
SPACE = 1           # blank columns between glyphs

_G = {
    "A": ["  #  ", " # # ", "#   #", "#   #", "#####", "#   #", "#   #"],
    "B": ["#### ", "#   #", "#   #", "#### ", "#   #", "#   #", "#### "],
    "C": [" ### ", "#   #", "#    ", "#    ", "#    ", "#   #", " ### "],
    "D": ["#### ", "#   #", "#   #", "#   #", "#   #", "#   #", "#### "],
    "E": ["#####", "#    ", "#    ", "#### ", "#    ", "#    ", "#####"],
    "F": ["#####", "#    ", "#    ", "#### ", "#    ", "#    ", "#    "],
    "G": [" ### ", "#   #", "#    ", "#  ##", "#   #", "#   #", " ### "],
    "H": ["#   #", "#   #", "#   #", "#####", "#   #", "#   #", "#   #"],
    "I": ["###", " # ", " # ", " # ", " # ", " # ", "###"],
    "J": ["  ###", "   # ", "   # ", "   # ", "   # ", "#  # ", " ##  "],
    "K": ["#   #", "#  # ", "# #  ", "##   ", "# #  ", "#  # ", "#   #"],
    "L": ["#    ", "#    ", "#    ", "#    ", "#    ", "#    ", "#####"],
    "M": ["#   #", "## ##", "# # #", "# # #", "#   #", "#   #", "#   #"],
    "N": ["#   #", "##  #", "# # #", "#  ##", "#   #", "#   #", "#   #"],
    "O": [" ### ", "#   #", "#   #", "#   #", "#   #", "#   #", " ### "],
    "P": ["#### ", "#   #", "#   #", "#### ", "#    ", "#    ", "#    "],
    "Q": [" ### ", "#   #", "#   #", "#   #", "# # #", "#  # ", " ## #"],
    "R": ["#### ", "#   #", "#   #", "#### ", "# #  ", "#  # ", "#   #"],
    "S": [" ####", "#    ", "#    ", " ### ", "    #", "    #", "#### "],
    "T": ["#####", "  #  ", "  #  ", "  #  ", "  #  ", "  #  ", "  #  "],
    "U": ["#   #", "#   #", "#   #", "#   #", "#   #", "#   #", " ### "],
    "V": ["#   #", "#   #", "#   #", "#   #", "#   #", " # # ", "  #  "],
    "W": ["#   #", "#   #", "#   #", "# # #", "# # #", "## ##", "#   #"],
    "X": ["#   #", "#   #", " # # ", "  #  ", " # # ", "#   #", "#   #"],
    "Y": ["#   #", "#   #", " # # ", "  #  ", "  #  ", "  #  ", "  #  "],
    "Z": ["#####", "    #", "   # ", "  #  ", " #   ", "#    ", "#####"],

    "a": ["     ", "     ", " ### ", "    #", " ####", "#   #", " ####"],
    "b": ["#    ", "#    ", "#### ", "#   #", "#   #", "#   #", "#### "],
    "c": ["     ", "     ", " ### ", "#    ", "#    ", "#   #", " ### "],
    "d": ["    #", "    #", " ####", "#   #", "#   #", "#   #", " ####"],
    "e": ["     ", "     ", " ### ", "#   #", "#####", "#    ", " ### "],
    "f": ["  ## ", " #   ", "#### ", " #   ", " #   ", " #   ", " #   "],
    "g": ["     ", "     ", " ####", "#   #", " ####", "    #", " ### "],
    "h": ["#    ", "#    ", "#### ", "#   #", "#   #", "#   #", "#   #"],
    "i": ["#", " ", "#", "#", "#", "#", "#"],
    "j": ["  #", "   ", "  #", "  #", "  #", "  #", "##"],
    "k": ["#    ", "#    ", "#  # ", "# #  ", "##   ", "# #  ", "#  # "],
    "l": ["##", " #", " #", " #", " #", " #", " #"],
    "m": ["     ", "     ", "## # ", "# # #", "# # #", "# # #", "# # #"],
    "n": ["     ", "     ", "#### ", "#   #", "#   #", "#   #", "#   #"],
    "o": ["     ", "     ", " ### ", "#   #", "#   #", "#   #", " ### "],
    "p": ["     ", "     ", "#### ", "#   #", "#### ", "#    ", "#    "],
    "q": ["     ", "     ", " ####", "#   #", " ####", "    #", "    #"],
    "r": ["     ", "     ", "# ## ", "##   ", "#    ", "#    ", "#    "],
    "s": ["     ", "     ", " ####", "#    ", " ### ", "    #", "#### "],
    "t": [" #   ", " #   ", "#### ", " #   ", " #   ", " #  #", "  ## "],
    "u": ["     ", "     ", "#   #", "#   #", "#   #", "#   #", " ####"],
    "v": ["     ", "     ", "#   #", "#   #", "#   #", " # # ", "  #  "],
    "w": ["     ", "     ", "#   #", "# # #", "# # #", "# # #", " # # "],
    "x": ["     ", "     ", "#   #", " # # ", "  #  ", " # # ", "#   #"],
    "y": ["     ", "     ", "#   #", "#   #", " ####", "    #", " ##  "],
    "z": ["     ", "     ", "#####", "   # ", "  #  ", " #   ", "#####"],

    "0": [" ### ", "#   #", "#  ##", "# # #", "##  #", "#   #", " ### "],
    "1": ["  #  ", " ##  ", "  #  ", "  #  ", "  #  ", "  #  ", " ### "],
    "2": [" ### ", "#   #", "    #", "   # ", "  #  ", " #   ", "#####"],
    "3": ["#####", "   # ", "  #  ", "   # ", "    #", "#   #", " ### "],
    "4": ["   # ", "  ## ", " # # ", "#  # ", "#####", "   # ", "   # "],
    "5": ["#####", "#    ", "#### ", "    #", "    #", "#   #", " ### "],
    "6": ["  ## ", " #   ", "#    ", "#### ", "#   #", "#   #", " ### "],
    "7": ["#####", "    #", "   # ", "  #  ", " #   ", " #   ", " #   "],
    "8": [" ### ", "#   #", "#   #", " ### ", "#   #", "#   #", " ### "],
    "9": [" ### ", "#   #", "#   #", " ####", "    #", "   # ", " ##  "],

    " ": ["   ", "   ", "   ", "   ", "   ", "   ", "   "],
    ".": ["  ", "  ", "  ", "  ", "  ", "##", "##"],
    ",": ["  ", "  ", "  ", "  ", "  ", "##", " #"],
    ":": ["  ", "##", "##", "  ", "##", "##", "  "],
    ";": ["  ", "##", "##", "  ", "##", " #", "# "],
    "'": ["#", "#", " ", " ", " ", " ", " "],
    '"': ["# #", "# #", "   ", "   ", "   ", "   ", "   "],
    "!": ["#", "#", "#", "#", "#", " ", "#"],
    "?": [" ### ", "#   #", "    #", "   # ", "  #  ", "     ", "  #  "],
    "-": ["    ", "    ", "    ", "####", "    ", "    ", "    "],
    "+": ["     ", "  #  ", "  #  ", "#####", "  #  ", "  #  ", "     "],
    "=": ["     ", "     ", "#####", "     ", "#####", "     ", "     "],
    "/": ["    #", "    #", "   # ", "  #  ", " #   ", "#    ", "#    "],
    "\\": ["#    ", "#    ", " #   ", "  #  ", "   # ", "    #", "    #"],
    "(": [" #", "# ", "# ", "# ", "# ", "# ", " #"],
    ")": ["# ", " #", " #", " #", " #", " #", "# "],
    "[": ["##", "# ", "# ", "# ", "# ", "# ", "##"],
    "]": ["##", " #", " #", " #", " #", " #", "##"],
    "%": ["##  #", "##  #", "   # ", "  #  ", " #   ", "#  ##", "#  ##"],
    "*": ["     ", "#   #", " # # ", "#####", " # # ", "#   #", "     "],
    "#": [" # # ", "#####", " # # ", " # # ", "#####", " # # ", "     "],
    "<": ["  #", " # ", "#  ", "#  ", "#  ", " # ", "  #"],
    ">": ["#  ", " # ", "  #", "  #", "  #", " # ", "#  "],
    "|": ["#", "#", "#", "#", "#", "#", "#"],
    "_": ["     ", "     ", "     ", "     ", "     ", "     ", "#####"],
    "^": ["  #  ", " # # ", "#   #", "     ", "     ", "     ", "     "],
    "&": [" ##  ", "#  # ", " ##  ", " ##  ", "#  ##", "#  # ", " ## #"],
    "@": [" ### ", "#   #", "# ###", "# # #", "# ## ", "#    ", " ### "],
    "$": ["  #  ", " ####", "#  # ", " ### ", "  #  ", "#### ", "  #  "],

    # Typographic characters the HUD payload and menu copy actually use.
    "·": ["  ", "  ", "  ", "##", "##", "  ", "  "],           # middle dot
    "—": ["      ", "      ", "      ", "######", "      ", "      ", "      "],  # em dash
    "–": ["     ", "     ", "     ", "#####", "     ", "     ", "     "],          # en dash
    "‘": ["#", "#", " ", " ", " ", " ", " "],
    "’": ["#", "#", " ", " ", " ", " ", " "],
    "“": ["# #", "# #", "   ", "   ", "   ", "   ", "   "],
    "”": ["# #", "# #", "   ", "   ", "   ", "   ", "   "],
    "…": ["      ", "      ", "      ", "      ", "      ", "# # # ", "# # # "],   # ellipsis
    "×": ["     ", "     ", "#   #", " # # ", "  #  ", " # # ", "#   #"],          # times
    "→": ["     ", "  #  ", "   # ", "#####", "   # ", "  #  ", "     "],          # right arrow
    "★": ["  #  ", "  #  ", "#####", " ### ", " # # ", "#   #", "     "],          # star
    "▸": ["#  ", "## ", "###", "## ", "#  ", "   ", "   "],                        # play caret
    "█": ["#####", "#####", "#####", "#####", "#####", "#####", "#####"],          # full block

    # Ornaments the pack's own strings use in menu titles and list markers
    # (fc_strings.js), which would otherwise render as tofu.
    "✦": ["  #  ", "  #  ", "# # #", " ### ", "# # #", "  #  ", "  #  "],          # four-pointed star
    "✧": ["  #  ", "  #  ", "# # #", " # # ", "# # #", "  #  ", "  #  "],          # open four-point
    "❖": ["  #  ", " ### ", "## ##", "#   #", "## ##", " ### ", "  #  "],          # lozenge
    "◈": ["  #  ", " ### ", "#####", "## ##", "#####", " ### ", "  #  "],          # inset diamond
    "◆": ["  #  ", " ### ", "#####", "#####", "#####", " ### ", "  #  "],          # solid diamond
    "▶": ["#    ", "##   ", "###  ", "#### ", "###  ", "##   ", "#    "],          # play marker
    "⚔": ["#   #", "## ##", " ### ", "  #  ", " ### ", "## ##", "#   #"],          # crossed blades
    "═": ["     ", "     ", "#####", "     ", "#####", "     ", "     "],          # double rule
    "✔": ["    #", "    #", "   # ", "#  # ", " ##  ", "  #  ", "     "],          # check
    " ": ["   ", "   ", "   ", "   ", "   ", "   ", "   "],                        # nbsp
}

_FALLBACK = "?"


def _glyph(ch):
    rows = _G.get(ch)
    if rows is None:
        rows = _G.get(ch.upper()) or _G[_FALLBACK]
    return rows


def glyph_width(ch):
    return len(_glyph(ch)[0])


def text_width(text, scale=1, tracking=SPACE):
    """Width in pixels of `text` at `scale`, including inter-glyph spacing."""
    if not text:
        return 0
    total = sum(glyph_width(c) for c in text) + tracking * (len(text) - 1)
    return total * scale


def draw_text(img, xy, text, fill=(255, 255, 255), scale=3, shadow=(63, 63, 63),
              tracking=SPACE, anchor="lt"):
    """Draw `text` with Minecraft's one-pixel offset drop shadow.

    `anchor` takes an x code (l/c/r) and a y code (t/m/b), matching how HUD and
    menu strings are positioned against their frames.
    """
    width = text_width(text, scale, tracking)
    height = HEIGHT * scale
    x, y = xy
    if anchor[0] == "c":
        x -= width / 2
    elif anchor[0] == "r":
        x -= width
    if anchor[1] == "m":
        y -= height / 2
    elif anchor[1] == "b":
        y -= height
    x, y = round(x), round(y)

    draw = ImageDraw.Draw(img, "RGBA")

    def blit(ox, oy, colour):
        cx = x + ox
        for ch in text:
            rows = _glyph(ch)
            for ry, row in enumerate(rows):
                run = None
                for rx in range(len(row) + 1):
                    on = rx < len(row) and row[rx] == "#"
                    if on and run is None:
                        run = rx
                    elif not on and run is not None:
                        draw.rectangle(
                            (cx + run * scale, y + oy + ry * scale,
                             cx + rx * scale - 1, y + oy + (ry + 1) * scale - 1),
                            fill=colour)
                        run = None
            cx += (len(rows[0]) + tracking) * scale

    if shadow:
        blit(scale, scale, tuple(shadow) + ((fill[3],) if len(fill) > 3 else (255,)))
    blit(0, 0, fill if len(fill) > 3 else fill + (255,))
    return width


def text_image(text, fill=(255, 255, 255), scale=3, shadow=(63, 63, 63), tracking=SPACE):
    """Standalone RGBA image of one line, sized to the ink."""
    pad = scale if shadow else 0
    img = Image.new("RGBA", (text_width(text, scale, tracking) + pad,
                             HEIGHT * scale + pad), (0, 0, 0, 0))
    draw_text(img, (0, 0), text, fill=fill, scale=scale, shadow=shadow, tracking=tracking)
    return img


# ---------------------------------------------------------------------------
# Minecraft section codes
# ---------------------------------------------------------------------------
#
# Every string the packs hand to setActionBar or a form body is §-coded, so any
# renderer that draws those strings has to parse them or the § lands on screen
# as a literal. Both the HUD and the menus draw the same payloads, so the parser
# lives here with the glyphs rather than being written twice.

SECTION_COLOURS = {
    "0": (0, 0, 0), "1": (0, 0, 170), "2": (0, 170, 0), "3": (0, 170, 170),
    "4": (170, 0, 0), "5": (170, 0, 170), "6": (255, 170, 0), "7": (170, 170, 170),
    "8": (85, 85, 85), "9": (85, 85, 255), "a": (85, 255, 85), "b": (85, 255, 255),
    "c": (255, 85, 85), "d": (255, 85, 255), "e": (255, 255, 85), "f": (255, 255, 255),
}
# Formatting codes (obfuscate/bold/strike/underline/italic) and the reset. These
# change style, not colour, and are consumed without emitting anything.
STYLE_CODES = set("klmno")


def runs(text, default=(255, 255, 255), palette=None):
    """Split a §-coded string into (segment, rgb) runs."""
    colours = palette or SECTION_COLOURS
    out, colour, buf, i = [], default, "", 0
    while i < len(text):
        if text[i] == "\u00a7" and i + 1 < len(text):
            code = text[i + 1].lower()
            if buf:
                out.append((buf, colour))
                buf = ""
            if code == "r":
                colour = default
            elif code not in STYLE_CODES:
                colour = colours.get(code, colour)
            i += 2
        else:
            buf += text[i]
            i += 1
    if buf:
        out.append((buf, colour))
    return out


def strip_codes(text):
    return "".join(segment for segment, _ in runs(text))


def rich_width(text, scale=1, tracking=SPACE):
    segs = runs(text)
    return sum(text_width(t, scale, tracking) + scale for t, _ in segs) - (scale if segs else 0)


def draw_rich(img, xy, text, default=(255, 255, 255), scale=3, shadow=(63, 63, 63),
              tracking=SPACE, anchor="lt", palette=None):
    """Draw one §-coded line, anchoring against the whole line's width."""
    segs = runs(text, default, palette)
    width = rich_width(text, scale, tracking)
    x, y = xy
    if anchor[0] == "c":
        x -= width / 2
    elif anchor[0] == "r":
        x -= width
    if anchor[1] == "m":
        y -= HEIGHT * scale / 2
    elif anchor[1] == "b":
        y -= HEIGHT * scale
    for segment, colour in segs:
        draw_text(img, (x, y), segment, fill=colour, scale=scale, shadow=shadow,
                  tracking=tracking)
        x += text_width(segment, scale, tracking) + scale
    return width

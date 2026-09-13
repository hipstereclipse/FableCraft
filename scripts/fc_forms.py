"""fc_forms.py — draw the pack's server-UI forms the way Bedrock draws them.

Every menu in this addon is a `@minecraft/server-ui` form, and the resource pack
re-skins the stock dialog and button textures (dialog_background_hollow_3,
button_borderless_light) into dark leather with parchment controls and gilt trim.
So a menu screenshot is not a full-bleed page: it is a modest panel, nine-sliced
from those very textures, floating over a dimmed and blurred game frame, with the
world still visible around its edges.

Content here is quoted from the pack's own strings (fc_strings.js) and form
builders rather than invented, so the captures show menus that exist. Section
codes are parsed the way Bedrock parses them, so §-coloured copy lands in the
right colours.
"""
from __future__ import annotations

import json

from PIL import Image, ImageDraw, ImageFilter

import fc_pixelfont as PF
from audit_hud import UI_SCALE
from fc_lib import RP

UI_TEX = RP / "textures" / "ui"
SIGILS = UI_TEX / "wd"

# The dialog skin is dark leather, so §0 and §8 need lifting off it; every other
# code keeps its Bedrock value from fc_pixelfont.
FORM_COLOURS = dict(PF.SECTION_COLOURS)
FORM_COLOURS.update({"0": (24, 18, 12), "8": (110, 96, 80)})

BODY_DEFAULT = (208, 198, 178)
BUTTON_TEXT = (46, 32, 20)


def draw_rich(canvas, xy, text, default=BODY_DEFAULT, scale=2, anchor="lt",
              shadow=(26, 20, 14)):
    """Draw one §-coded form line in the dialog's palette."""
    return PF.draw_rich(canvas, xy, text, default=default, scale=scale,
                        shadow=shadow, anchor=anchor, palette=FORM_COLOURS)


def rich_width(text, scale=2):
    return PF.rich_width(text, scale)


# ---------------------------------------------------------------------------
# nine-slice
# ---------------------------------------------------------------------------

def nineslice(name, size, scale=UI_SCALE):
    """Render a Bedrock nine-sliced UI texture at `size` pixels.

    Corners keep their authored pixels (scaled by the UI scale); the edges and
    centre stretch. That is what keeps the gilt trim one texel thick on a panel
    of any size, exactly as the game draws it.
    """
    png = UI_TEX / f"{name}.png"
    meta_path = UI_TEX / f"{name}.json"
    src = Image.open(png).convert("RGBA")
    meta = json.loads(meta_path.read_text(encoding="utf-8")) if meta_path.exists() else {}
    slices = meta.get("nineslice_size", 0)
    if isinstance(slices, (int, float)):
        left = top = right = bottom = int(slices)
    else:
        left, top, right, bottom = (int(v) for v in slices)
    bw, bh = meta.get("base_size", src.size)
    if (bw, bh) != src.size:
        src = src.resize((bw, bh), Image.Resampling.NEAREST)

    tw, th = size
    dl, dt = left * scale, top * scale
    dr, db = right * scale, bottom * scale
    # A panel smaller than its own corners would overlap them; clamp instead.
    if dl + dr > tw:
        dl = dr = tw // 2
    if dt + db > th:
        dt = db = th // 2

    sx = [0, left, bw - right, bw]
    sy = [0, top, bh - bottom, bh]
    dx = [0, dl, tw - dr, tw]
    dy = [0, dt, th - db, th]

    out = Image.new("RGBA", size, (0, 0, 0, 0))
    for r in range(3):
        for c in range(3):
            sbox = (sx[c], sy[r], sx[c + 1], sy[r + 1])
            dbox = (dx[c], dy[r], dx[c + 1], dy[r + 1])
            sw, sh = sbox[2] - sbox[0], sbox[3] - sbox[1]
            dw, dh = dbox[2] - dbox[0], dbox[3] - dbox[1]
            if sw <= 0 or sh <= 0 or dw <= 0 or dh <= 0:
                continue
            out.paste(src.crop(sbox).resize((dw, dh), Image.Resampling.NEAREST), dbox[:2])
    return out


# ---------------------------------------------------------------------------
# forms
# ---------------------------------------------------------------------------

HEADER_UNITS = 23           # the dialog skin's fixed title band
PAD = 9 * UI_SCALE


def button(size, hovered=False):
    name = "button_borderless_lighthover" if hovered else "button_borderless_light"
    return nineslice(name, size)


def sigil(name, size):
    path = SIGILS / f"{name}.png"
    if not path.exists():
        return None
    return Image.open(path).convert("RGBA").resize((size, size), Image.Resampling.NEAREST)


def action_form(background, title, body, buttons, width_units=200, height_units=196,
                hovered=None, scroll=None, scale=UI_SCALE):
    """Composite an ActionFormData panel over a game frame.

    `buttons` is a list of (label, sigil_name_or_None). `scroll` is a 0..1
    fraction for the scrollbar handle when the button list overflows, matching
    what the game shows once a form is longer than its panel.
    """
    canvas = background.convert("RGBA").copy()
    W, H = canvas.size

    # Bedrock dims and blurs the world behind an open form.
    canvas = canvas.filter(ImageFilter.GaussianBlur(2.2))
    canvas.alpha_composite(Image.new("RGBA", (W, H), (0, 0, 0, 120)))

    pw, ph = width_units * scale, height_units * scale
    px, py = (W - pw) // 2, (H - ph) // 2
    panel = nineslice("dialog_background_hollow_3", (pw, ph))
    canvas.alpha_composite(panel, (px, py))

    head_h = HEADER_UNITS * scale
    draw_rich(canvas, (px + pw / 2, py + head_h / 2 - PF.HEIGHT * scale / 2),
              title, default=(32, 22, 14), scale=scale, anchor="ct", shadow=None)

    # Close control, top-right, as the game draws it on a dialog.
    cx, cy = px + pw - 7 * scale, py + 8 * scale
    PF.draw_text(canvas, (cx, cy), "x", fill=(92, 62, 38), scale=scale, shadow=None,
                 anchor="ct")

    y = py + head_h + PAD
    inner_x = px + PAD
    inner_w = pw - 2 * PAD

    for line in body.split("\n"):
        if line.strip():
            draw_rich(canvas, (inner_x, y), line, scale=scale - 1)
        y += (PF.HEIGHT + 3) * (scale - 1)
    y += PAD // 2

    bh = 22 * scale
    gap = 3 * scale
    bar_w = 5 * scale if scroll is not None else 0
    bw = inner_w - (bar_w + 2 * scale if bar_w else 0)
    for index, (label, icon) in enumerate(buttons):
        top = y + index * (bh + gap)
        if top + bh > py + ph - PAD:
            break
        canvas.alpha_composite(button((bw, bh), hovered=(index == hovered)),
                               (inner_x, top))
        tx = inner_x + 6 * scale
        if icon:
            art = sigil(icon, bh - 6 * scale)
            if art is not None:
                canvas.alpha_composite(art, (tx, top + 3 * scale))
                tx += bh - 2 * scale
        # Button labels can carry a newline (the Cullis list puts the distance
        # on a second line), so they are laid out as a block centred in the row.
        lines = label.split("\n")
        line_h = (PF.HEIGHT + 2) * (scale - 1)
        ty = top + bh / 2 - (len(lines) * line_h) / 2
        for line in lines:
            draw_rich(canvas, (tx, ty), line, default=BUTTON_TEXT, scale=scale - 1,
                      shadow=None)
            ty += line_h

    if scroll is not None:
        rail_x = px + pw - PAD - bar_w
        rail_y0, rail_y1 = y, py + ph - PAD
        canvas.alpha_composite(nineslice("ScrollRail", (bar_w, rail_y1 - rail_y0)),
                               (rail_x, rail_y0))
        handle_h = max(12 * scale, (rail_y1 - rail_y0) // 3)
        hy = rail_y0 + round((rail_y1 - rail_y0 - handle_h) * scroll)
        canvas.alpha_composite(nineslice("ScrollHandle", (bar_w, handle_h)), (rail_x, hy))

    return canvas


def message_form(background, title, body, buttons, width_units=190, height_units=118,
                 hovered=None, scale=UI_SCALE):
    """A MessageFormData panel: body copy and two side-by-side choices.

    The arrest prompt and the Sword of Aeons choice both use this shape.
    """
    canvas = background.convert("RGBA").copy()
    W, H = canvas.size
    canvas = canvas.filter(ImageFilter.GaussianBlur(2.2))
    canvas.alpha_composite(Image.new("RGBA", (W, H), (0, 0, 0, 120)))

    pw, ph = width_units * scale, height_units * scale
    px, py = (W - pw) // 2, (H - ph) // 2
    canvas.alpha_composite(nineslice("dialog_background_hollow_3", (pw, ph)), (px, py))

    head_h = HEADER_UNITS * scale
    draw_rich(canvas, (px + pw / 2, py + head_h / 2 - PF.HEIGHT * scale / 2), title,
              default=(32, 22, 14), scale=scale, anchor="ct", shadow=None)

    y = py + head_h + PAD
    for line in body.split("\n"):
        if line.strip():
            draw_rich(canvas, (px + PAD, y), line, scale=scale - 1)
        y += (PF.HEIGHT + 3) * (scale - 1)

    bh = 22 * scale
    count = len(buttons)
    gap = 4 * scale
    total = pw - 2 * PAD
    bw = (total - gap * (count - 1)) // count
    top = py + ph - PAD - bh
    for index, label in enumerate(buttons):
        bx = px + PAD + index * (bw + gap)
        canvas.alpha_composite(button((bw, bh), hovered=(index == hovered)), (bx, top))
        draw_rich(canvas, (bx + bw / 2, top + bh / 2 - PF.HEIGHT * (scale - 1) / 2),
                  label, default=BUTTON_TEXT, scale=scale - 1, anchor="ct", shadow=None)
    return canvas

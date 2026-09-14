"""fc_hud.py — composite the live HUD over a rendered frame.

A screenshot of this addon is not a picture of the world; it is a picture of the
world *behind the HUD the pack installs*. hud_screen.json hides vanilla hearts,
hunger and armour outright and replaces them with the Fable status frame, the
detection eye, the day dial, the radar, the nav line and the coin purse, while
leaving the hotbar and XP bar alone. A capture missing that layer is missing the
part a player looks at most.

Rather than re-describing the layout, everything here is anchored from the real
hud_screen.json and the real textures in textures/ui/fable_hud, at the same
UI_SCALE the HUD audit uses. If the pack moves a frame, these captures move with
it. Text is drawn with fc_pixelfont for the reasons in that module.
"""
from __future__ import annotations

import json
import math
from dataclasses import dataclass, field

from PIL import Image, ImageDraw

import fc_pixelfont as PF
import fc_viewmodel as VM
from audit_hud import HUD_TEXTURES, HUD_JSON, UI_SCALE, CANVAS, anchor_rect, controls
from fc_lib import RP
from gen_hud_font import clock_glyph

ITEM_TEX = RP / "textures" / "items"

# Bedrock's §-code palette. The radar bakes its terrain into these, so the
# minimap here quantises to the same 16 colours the live HUD can actually emit.
_HUD = None


def hud_json():
    global _HUD
    if _HUD is None:
        _HUD = json.loads(HUD_JSON.read_text(encoding="utf-8"))
    return _HUD


def clip_rect(name):
    """Screen rect of a named clips_children window, straight from the pack."""
    clip = controls(hud_json()["hud_actionbar_text"])[name]
    return anchor_rect(clip["anchor_from"], tuple(clip["offset"]), tuple(clip["size"]))


def overlay_rect(name):
    frame = controls(hud_json()["fable_hud_overlay"])[name]
    return anchor_rect(frame["anchor_from"], tuple(frame["offset"]), tuple(frame["size"]))


def paste_frame(canvas, name):
    frame = controls(hud_json()["fable_hud_overlay"])[name]
    texture = frame["texture"].removeprefix("textures/ui/fable_hud/")
    art = Image.open(HUD_TEXTURES / f"{texture}.png").convert("RGBA")
    rect = overlay_rect(name)
    art = art.resize((rect[2] - rect[0], rect[3] - rect[1]), Image.Resampling.LANCZOS)
    canvas.alpha_composite(art, (rect[0], rect[1]))
    return rect


# ---------------------------------------------------------------------------
# state
# ---------------------------------------------------------------------------

@dataclass
class Hud:
    """Everything the HUD shows for one captured moment."""

    health: tuple = (20, 20)
    will: tuple = (100, 100)
    stamina: tuple = (20, 20)
    multiplier: int = 0
    gold: int = 0
    heading: str = "N"
    place: str = "Heroes' Guild"
    distance: int = 0
    notice: str = ""
    wanted: int = 0                       # 0-4 wanted stars
    eye: str = "open"                     # open | partial | closed
    hour: int = 9                         # 0-23, drives the day dial
    hotbar: list = field(default_factory=lambda: [None] * 9)
    selected: int = 0
    counts: dict = field(default_factory=dict)     # slot index -> stack size
    level: int = 0
    xp: float = 0.0                       # 0..1 through the current level
    held: str = None                      # overrides the selected slot if set
    radar: list = None                    # 11x11 of §-code chars, or None
    crosshair: bool = True
    show_hand: bool = True                # false while a form is open
    sleeve: str = "apprentice"           # armour set the arm wears

    def in_hand(self):
        """What the player is actually holding.

        The game can only ever show the selected slot in first person, so a
        capture must not be able to disagree with its own hotbar.
        """
        if not self.show_hand:
            return None
        if self.held is not None:
            return self.held
        if 0 <= self.selected < len(self.hotbar):
            return self.hotbar[self.selected]
        return None


def bar(canvas, rect, value, maximum, colour, track=(38, 30, 24)):
    """One status bar inside its clip window.

    fable_hud.js draws these as a run of filled block glyphs against an empty
    run, so the bar is always a hard-edged block fill, never a gradient.
    """
    x0, y0, x1, y1 = rect
    draw = ImageDraw.Draw(canvas, "RGBA")
    draw.rectangle((x0, y0, x1 - 1, y1 - 1), fill=track + (210,))
    if maximum > 0 and value > 0:
        cells = 12                                  # the live bar is 12 glyphs wide
        filled = max(1, round(cells * min(1.0, value / maximum)))
        step = (x1 - x0) / cells
        for i in range(filled):
            draw.rectangle((x0 + round(i * step), y0,
                            x0 + round((i + 1) * step) - 1, y1 - 1), fill=colour + (255,))


def draw_radar(canvas, rows):
    """Paint the 11x11 terrain dial into the radar clip window."""
    rect = clip_rect("fable_radar_clip")
    x0, y0, x1, y1 = rect
    size = min(x1 - x0, y1 - y0)
    cell = size / 11.0
    ox = x0 + ((x1 - x0) - size) / 2
    oy = y0 + ((y1 - y0) - size) / 2
    draw = ImageDraw.Draw(canvas, "RGBA")
    for r, row in enumerate(rows):
        for c, code in enumerate(row):
            if code == " ":
                continue
            colour = PF.SECTION_COLOURS.get(code)
            if colour is None:
                continue
            draw.rectangle((ox + c * cell, oy + r * cell,
                            ox + (c + 1) * cell - 1, oy + (r + 1) * cell - 1),
                           fill=colour + (255,))


def world_radar(world, cam, span=11, step=3.0):
    """Sample the world into the dial's 11x11 grid, rotated to the view.

    The live HUD bakes terrain colours into glyph cells; this reads the same
    information out of the Vox the frame was rendered from, so the dial in a
    capture agrees with what is actually around the player.
    """
    half = span // 2
    cy, sy = math.cos(cam.yaw), math.sin(cam.yaw)
    rows = []
    for r in range(span):
        row = ""
        for c in range(span):
            if (r - half) ** 2 + (c - half) ** 2 > half * half + 1:
                row += " "                      # outside the round dial
                continue
            if r == half and c == half:
                row += "f"                      # the player marker
                continue
            # Dial is view-relative: forward is up, so rotate the offset by yaw.
            fwd = -(r - half) * step
            side = (c - half) * step
            wx = cam.pos[0] + side * cy + fwd * sy
            wz = cam.pos[2] - side * sy + fwd * cy
            top = world.heightmap.get((int(wx), int(wz)), -1)
            if top < 0:
                row += "8"                      # unsurveyed ground, not a void
                continue
            name = world.pal_name[world.pid(int(wx), top, int(wz))]
            row += _terrain_code(name)
        rows.append(row)
    return rows


def _terrain_code(name):
    if "water" in name:
        return "1"
    if "grass" in name or "moss" in name or "leaves" in name:
        return "a"
    if "log" in name or "planks" in name or "dirt" in name or "path" in name:
        return "6"
    if "lantern" in name or "torch" in name or "glowstone" in name or "gold" in name:
        return "e"
    if "wool" in name or "carpet" in name or "terracotta" in name:
        return "c"
    if "sand" in name:
        return "e"
    if "stone" in name or "brick" in name or "cobble" in name or "andesite" in name:
        return "7"
    if "deepslate" in name or "obsidian" in name or "blackstone" in name:
        return "8"
    return "2"


# ---------------------------------------------------------------------------
# the vanilla layer the pack keeps
# ---------------------------------------------------------------------------

HOTBAR_W, HOTBAR_H = 182, 22                # vanilla widget units
SLOT = 20


def item_icon(item_id, size):
    """Item art at `size`, nearest-neighbour so the pixels stay hard."""
    if not item_id:
        return None
    path = ITEM_TEX / f"{item_id}.png"
    if not path.exists():
        return None
    return Image.open(path).convert("RGBA").resize((size, size), Image.Resampling.NEAREST)


def draw_hotbar(canvas, state, scale=UI_SCALE):
    """Vanilla hotbar and XP bar, rebuilt from their vanilla proportions.

    hud_screen.json turns off hearts, hunger and armour but leaves
    exp_progress_bar_and_hotbar alone, so these two are the only vanilla HUD
    pieces a player still sees under this pack.
    """
    W, H = canvas.size
    bw, bh = HOTBAR_W * scale, HOTBAR_H * scale
    bx = round((W - bw) / 2)
    by = H - bh - 3 * scale
    draw = ImageDraw.Draw(canvas, "RGBA")

    draw.rectangle((bx - scale, by - scale, bx + bw + scale - 1, by + bh + scale - 1),
                   fill=(0, 0, 0, 165))
    draw.rectangle((bx, by, bx + bw - 1, by + bh - 1), fill=(60, 60, 60, 190))
    draw.rectangle((bx, by, bx + bw - 1, by + scale - 1), fill=(122, 122, 122, 190))
    draw.rectangle((bx, by, bx + scale - 1, by + bh - 1), fill=(122, 122, 122, 190))
    draw.rectangle((bx, by + bh - scale, bx + bw - 1, by + bh - 1), fill=(28, 28, 28, 190))

    slot_px = SLOT * scale
    for i in range(9):
        sx = bx + scale + i * slot_px
        if i:
            draw.rectangle((sx - scale, by + scale, sx - 1, by + bh - scale - 1),
                           fill=(28, 28, 28, 190))
        icon = item_icon(state.hotbar[i], slot_px - 6 * scale)
        if icon:
            canvas.alpha_composite(icon, (sx + 3 * scale, by + 3 * scale))
            count = state.counts.get(i)
            if count and count > 1:
                PF.draw_text(canvas, (sx + slot_px - 2 * scale, by + bh - 3 * scale),
                             str(count), fill=(255, 255, 255), scale=max(1, scale - 1),
                             anchor="rb")

    # Selected-slot frame: vanilla draws a 24x24 highlight around the 20px slot.
    sx = bx + scale + state.selected * slot_px - 2 * scale
    sy = by - scale
    for w in range(scale):
        draw.rectangle((sx + w, sy + w, sx + slot_px + 4 * scale - 1 - w,
                        sy + slot_px + 4 * scale - 1 - w),
                       outline=(255, 255, 255, 235))

    # XP bar and level.
    if state.level or state.xp:
        xw, xh = HOTBAR_W * scale, 5 * scale
        xx, xy = bx, by - xh - 2 * scale
        draw.rectangle((xx, xy, xx + xw - 1, xy + xh - 1), fill=(0, 0, 0, 200))
        draw.rectangle((xx + scale, xy + scale, xx + xw - scale - 1, xy + xh - scale - 1),
                       fill=(58, 58, 58, 220))
        fill_w = round((xw - 2 * scale) * max(0.0, min(1.0, state.xp)))
        if fill_w:
            draw.rectangle((xx + scale, xy + scale, xx + scale + fill_w, xy + xh - scale - 1),
                           fill=(128, 255, 32, 255))
        if state.level:
            PF.draw_text(canvas, (W / 2, xy - 2 * scale), str(state.level),
                         fill=(128, 255, 32), scale=scale, shadow=(0, 0, 0), anchor="cb")


def draw_crosshair(canvas, scale=UI_SCALE):
    """Vanilla's centre crosshair, as a light cross over the frame."""
    W, H = canvas.size
    cx, cy = W // 2, H // 2
    arm, thick = 5 * scale, max(2, scale - 1)
    layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer, "RGBA")
    d.rectangle((cx - arm, cy - thick // 2, cx + arm, cy - thick // 2 + thick - 1),
                fill=(235, 235, 235, 225))
    d.rectangle((cx - thick // 2, cy - arm, cx - thick // 2 + thick - 1, cy + arm),
                fill=(235, 235, 235, 225))
    canvas.alpha_composite(layer)


# ---------------------------------------------------------------------------
# assembly
# ---------------------------------------------------------------------------

def compose(frame, state, world=None, cam=None, brightness=1.0):
    """Lay the view model and the full HUD over a rendered POV frame."""
    canvas = frame.convert("RGBA").copy()
    if canvas.size != CANVAS:
        canvas = canvas.resize(CANVAS, Image.Resampling.LANCZOS)

    # The hand and item go through the same camera as the world (see
    # fc_viewmodel), so they share the frame's perspective instead of sitting
    # on top of it as flat art.
    if cam is not None and (state.show_hand or state.in_hand()):
        VM.draw(canvas, cam, state.in_hand(), brightness=brightness,
                set_name=state.sleeve)
    if state.crosshair:
        draw_crosshair(canvas)

    for name in ("fable_status_frame", "fable_hunger_frame", "fable_minimap",
                 "fable_map_details_frame", "fable_gold_frame"):
        paste_frame(canvas, name)

    rows = state.radar
    if rows is None and world is not None and cam is not None:
        rows = world_radar(world, cam)
    if rows:
        # The radar clip window already sits inside the bezel ring, so the dial
        # draws over the frame rather than the other way round.
        draw_radar(canvas, rows)

    bar(canvas, clip_rect("fable_health_clip"), state.health[0], state.health[1],
        (218, 52, 50))
    bar(canvas, clip_rect("fable_will_clip"), state.will[0], state.will[1], (64, 96, 222))
    bar(canvas, clip_rect("fable_hunger_clip"), state.stamina[0], state.stamina[1],
        (222, 160, 44))

    small = max(1, UI_SCALE - 1)
    hx = clip_rect("fable_health_clip")
    PF.draw_text(canvas, (hx[2] + 5, (hx[1] + hx[3]) / 2),
                 f"{state.health[0]}/{state.health[1]}", fill=(255, 255, 255),
                 scale=small, anchor="lm")
    wx = clip_rect("fable_will_clip")
    PF.draw_text(canvas, (wx[2] + 5, (wx[1] + wx[3]) / 2),
                 f"{state.will[0]}/{state.will[1]}", fill=(255, 255, 255),
                 scale=small, anchor="lm")
    sx = clip_rect("fable_hunger_clip")
    PF.draw_text(canvas, (sx[2] + 5, (sx[1] + sx[3]) / 2),
                 f"{state.stamina[0]}/{state.stamina[1]}", fill=(255, 255, 255),
                 scale=small, anchor="lm")

    if state.multiplier:
        mx = clip_rect("fable_multiplier_clip")
        PF.draw_text(canvas, (mx[0], (mx[1] + mx[3]) / 2), f"x{state.multiplier}",
                     fill=(255, 214, 92), scale=small, anchor="lm")

    eye_rect = clip_rect("fable_eye_clip")
    eye_art = Image.open(HUD_TEXTURES / f"eye_{state.eye}.png").convert("RGBA")
    side = min(eye_rect[2] - eye_rect[0], eye_rect[3] - eye_rect[1])
    canvas.alpha_composite(eye_art.resize((side, side), Image.Resampling.LANCZOS),
                           (eye_rect[0] + ((eye_rect[2] - eye_rect[0]) - side) // 2,
                            eye_rect[1]))

    dial_rect = clip_rect("fable_clock_clip")
    side = min(dial_rect[2] - dial_rect[0], dial_rect[3] - dial_rect[1])
    dial = clock_glyph(state.hour).resize((side, side), Image.Resampling.LANCZOS)
    canvas.alpha_composite(dial, (dial_rect[0] + ((dial_rect[2] - dial_rect[0]) - side) // 2,
                                  dial_rect[1]))

    nav = clip_rect("fable_map_details_clip")
    PF.draw_text(canvas, ((nav[0] + nav[2]) / 2, (nav[1] + nav[3]) / 2 + 1),
                 f"{state.heading} · {state.place} · {state.distance}m",
                 fill=(255, 222, 140), scale=small, anchor="cm")

    gold = clip_rect("fable_gold_clip")
    PF.draw_text(canvas, (gold[0], (gold[1] + gold[3]) / 2), f"{state.gold}",
                 fill=(255, 196, 64), scale=small, anchor="lm")

    if state.notice:
        # Notices arrive from fable_hud.js already §-coded, so they are parsed
        # rather than printed, or the § itself lands on screen.
        notice = clip_rect("fable_notice_clip")
        notice_scale = small
        while notice_scale > 1 and PF.rich_width(state.notice, notice_scale) > notice[2] - notice[0]:
            notice_scale -= 1
        PF.draw_rich(canvas, (notice[2], (notice[1] + notice[3]) / 2), state.notice,
                     default=(255, 244, 214), scale=notice_scale, anchor="rm")

    if state.wanted:
        wrect = clip_rect("fable_wanted_clip")
        cell = wrect[3] - wrect[1]
        gap = round(cell * 0.12)
        star = Image.open(HUD_TEXTURES / "wanted_star.png").convert("RGBA")
        star = star.resize((cell, cell), Image.Resampling.LANCZOS)
        total = state.wanted * cell + (state.wanted - 1) * gap
        x = wrect[0] + round(((wrect[2] - wrect[0]) - total) / 2)
        for i in range(state.wanted):
            canvas.alpha_composite(star, (x + i * (cell + gap), wrect[1]))

    draw_hotbar(canvas, state)
    return canvas

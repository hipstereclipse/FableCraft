"""gen_entity_textures.py — paints every mob texture using the exact UV layout
from fc_mobs.pack_uvs, so geometry and texture always align.

Box UV layout per cube (origin u,v; size sx,sy,sz):
   top:    (u+sz,      v)        size (sx, sz)
   bottom: (u+sz+sx,   v)        size (sx, sz)
   right:  (u,         v+sz)     size (sz, sy)   (faces -x)
   front:  (u+sz,      v+sz)     size (sx, sy)   (faces -z)
   left:   (u+sz+sx,   v+sz)     size (sz, sy)
   back:   (u+sz+sx+sz,v+sz)     size (sx, sy)
"""
import math

from PIL import Image

from fc_lib import RP, Px, mix, ramp, rng, shade, with_alpha
from fc_mobs import MOBS, build_parts, mob_palette, pack_uvs

OUT = RP / "textures" / "entity"

ROLE_TEXTURE = {
    # role -> (palette key, noise style)
    "fur": ("fur", "fur"),
    "skin": ("skin", "skin"),
    "cloth": ("cloth", "cloth"),
    "bone": ("bone", "bone"),
    "metal": ("metal", "metal"),
    "steel": ("steel", "metal"),
    "rock": ("rock", "rock"),
    "chitin": ("chitin", "chitin"),
    "wing": ("wing", "wing"),
    "ghost": ("ghost", "ghost"),
    "scale": ("scale", "scale"),
    "wing_leather": ("wing_leather", "scale"),
    "glow": ("glow", "glow"),
    "moss": ("moss", "rock"),
    "hair": ("hair", "fur"),
    "horn": ("horn", "bone"),
    "boots": ("boots", "leather"),
    "belt": ("belt", "leather"),
    "tabard": ("tabard", "cloth"),
    "crest": ("crest", "metal"),
    "straw": ("straw", "straw"),
    "cape": ("cape", "cloth"),
    "tunic": ("tunic", "cloth"),
    "sleeves": ("sleeves", "cloth"),
    "pants": ("pants", "cloth"),
    "apron": ("apron", "cloth"),
}


def fill_face(p, x, y, w, h, base, style, r):
    """Paint a face region with material-appropriate noise."""
    if w <= 0 or h <= 0:
        return
    pal = ramp(base, 5, 0.55, 1.25)
    if style == "fur":
        p.rect(x, y, w, h, pal[2])
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                v = r.random()
                if v < 0.18:
                    p.px(xx, yy, pal[1])
                elif v < 0.30:
                    p.px(xx, yy, pal[3])
                elif v < 0.34 and yy % 2 == 0:
                    p.px(xx, yy, pal[0])
        # vertical streaks
        for s in range(max(1, w // 3)):
            sx = x + r.randrange(w)
            for yy in range(y, y + h):
                if r.random() < 0.6:
                    p.px(sx, yy, pal[1])
    elif style == "skin":
        p.rect(x, y, w, h, pal[3])
        p.noise_rect(x, y, w, h, [pal[2], pal[3], pal[3], shade(base, 1.1)], r, 0.35)
    elif style == "cloth":
        p.rect(x, y, w, h, pal[2])
        for yy in range(y, y + h):
            if yy % 3 == 0:
                for xx in range(x, x + w):
                    if r.random() < 0.5:
                        p.px(xx, yy, pal[1])
        p.noise_rect(x, y, w, h, [pal[2], pal[3]], r, 0.18)
    elif style == "bone":
        p.rect(x, y, w, h, pal[3])
        p.noise_rect(x, y, w, h, [pal[2], pal[4]], r, 0.25)
        for s in range(max(1, (w * h) // 24)):
            cx = x + r.randrange(max(1, w))
            cy = y + r.randrange(max(1, h))
            p.px(cx, cy, pal[1])
    elif style == "metal":
        p.rect(x, y, w, h, pal[3])
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                if (xx + yy) % 4 == 0:
                    p.px(xx, yy, pal[2])
                if r.random() < 0.06:
                    p.px(xx, yy, pal[4])
        # rivets along top
        for xx in range(x + 1, x + w - 1, 3):
            p.px(xx, y + 1, pal[4])
    elif style == "rock":
        p.rect(x, y, w, h, pal[2])
        p.noise_rect(x, y, w, h, [pal[1], pal[2], pal[3]], r, 0.6)
        # cracks
        for c in range(max(1, (w * h) // 30)):
            cx = x + r.randrange(max(1, w))
            cy = y + r.randrange(max(1, h))
            for step in range(r.randrange(2, 5)):
                p.px(cx, cy, pal[0])
                cx += r.choice((-1, 0, 1))
                cy += 1
    elif style == "chitin":
        p.rect(x, y, w, h, pal[2])
        for yy in range(y, y + h):
            band = (yy - y) % 4
            for xx in range(x, x + w):
                if band == 0:
                    p.px(xx, yy, pal[1])
                elif band == 2 and r.random() < 0.4:
                    p.px(xx, yy, pal[3])
        for xx in range(x, x + w, 5):
            p.px(xx, y, pal[4])
    elif style == "wing":
        p.rect(x, y, w, h, with_alpha(shade(base, 1.1), 150))
        for xx in range(x, x + w, 3):
            for yy in range(y, y + h):
                p.px(xx, yy, with_alpha(shade(base, 0.8), 180))
    elif style == "ghost":
        for yy in range(y, y + h):
            t = (yy - y) / max(1, h - 1)
            a = int(235 - t * 110)
            col = with_alpha(mix(base, (255, 255, 255), 0.2 * (1 - t)), a)
            for xx in range(x, x + w):
                p.px(xx, yy, col)
        p.noise_rect(x, y, w, h, [with_alpha(shade(base, 1.3), 160)], r, 0.12)
    elif style == "scale":
        p.rect(x, y, w, h, pal[2])
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                if (xx + (yy % 4) * 2) % 4 == 0 and yy % 2 == 0:
                    p.px(xx, yy, pal[1])
                elif r.random() < 0.08:
                    p.px(xx, yy, pal[3])
    elif style == "glow":
        p.rect(x, y, w, h, shade(base, 1.15))
        p.noise_rect(x, y, w, h, [shade(base, 1.35), shade(base, 0.95)], r, 0.4)
    elif style == "leather":
        # worn leather: warm mid-tone, stitch row, scuffed highlights
        p.rect(x, y, w, h, pal[2])
        p.noise_rect(x, y, w, h, [pal[1], pal[2], pal[3]], r, 0.3)
        for xx in range(x, x + w, 2):
            p.px(xx, y, pal[3])           # top stitching
        for xx in range(x, x + w):
            p.px(xx, y + h - 1, pal[0])   # dark sole/edge
        if h > 3:
            p.px(x + r.randrange(max(1, w)), y + 1, pal[4])  # scuff shine
    elif style == "straw":
        # woven straw: alternating warp/weft strands
        p.rect(x, y, w, h, pal[3])
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                if (xx + yy) % 3 == 0:
                    p.px(xx, yy, pal[2])
                elif (xx - yy) % 4 == 0:
                    p.px(xx, yy, pal[4])
        for xx in range(x, x + w, 3):
            p.px(xx, y + h - 1, pal[1])
    else:
        p.rect(x, y, w, h, pal[2])


# ---------------------------------------------------------------------------
# Decorations painted onto the front face of specific cubes
# ---------------------------------------------------------------------------

def decorate_front(p, x, y, w, h, decor, pal, glow, r):
    cx = x + w // 2
    SCLERA = (244, 240, 232, 255)
    PUPIL = (38, 30, 24, 255)
    BROW = (52, 38, 26, 255)

    def eyes(ey, iris=(70, 100, 150, 255), wide=False, brows=True):
        """Proper two-pixel eyes with whites, iris and brows."""
        lx = cx - w // 4 - 1
        rx = cx + w // 4
        for ex in (lx, rx):
            p.px(ex, ey, SCLERA)
            p.px(ex + 1, ey, iris)
            if wide:
                p.px(ex, ey + 1, SCLERA)
                p.px(ex + 1, ey + 1, PUPIL)
            if brows:
                p.px(ex, ey - 1, BROW)
                p.px(ex + 1, ey - 1, BROW)

    for d in decor:
        if d == "face":
            ey = y + max(2, h // 2)
            eyes(ey)
            # nose shadow
            p.px(cx, ey + 2, (0, 0, 0, 45))
            my = y + (2 * h) // 3 + 1
            p.px(cx - 1, my, (140, 84, 70, 255))
            p.px(cx, my, (150, 92, 76, 255))
        elif d == "lady_face":
            ey = y + max(2, h // 2)
            eyes(ey, iris=(60, 110, 160, 255))
            # lashes
            p.px(cx - w // 4 - 2, ey, (60, 44, 34, 255))
            p.px(cx + w // 4 + 2, ey, (60, 44, 34, 255))
            # blush + lips
            p.px(cx - w // 4 - 1, ey + 2, (215, 150, 130, 160))
            p.px(cx + w // 4 + 1, ey + 2, (215, 150, 130, 160))
            my = y + (2 * h) // 3 + 1
            p.px(cx - 1, my, (186, 76, 84, 255))
            p.px(cx, my, (200, 88, 96, 255))
        elif d == "blindfold_face":
            ey = y + max(2, h // 2)
            for xx in range(x, x + w):
                p.px(xx, ey, (150, 32, 32, 255))
                p.px(xx, ey + 1, (118, 26, 26, 255))
            p.px(x + 1, ey, (180, 60, 50, 255))  # knot highlight
            my = y + (2 * h) // 3 + 1
            p.px(cx - 1, my, (150, 96, 84, 255))
            p.px(cx, my, (150, 96, 84, 255))
        elif d in ("apprentice_hood_face", "hood_lady_face", "hood_will_face"):
            skin = pal.get("skin", (204, 164, 124)) + (255,)
            skin_dk = shade(skin, 0.82)
            hood_shadow = shade(pal.get("cloth", (226, 228, 234)) + (255,), 0.48)
            fx0, fx1 = x + max(1, w // 4), x + w - max(1, w // 4) - 1
            fy0, fy1 = y + max(2, h // 4), y + h - 2
            for yy in range(y + 1, y + h - 1):
                for xx in range(x + 1, x + w - 1):
                    if fx0 <= xx <= fx1 and fy0 <= yy <= fy1:
                        p.px(xx, yy, skin if (xx + yy) % 5 else skin_dk)
                    elif yy > fy0 - 1 and abs(xx - cx) <= max(2, w // 3):
                        p.px(xx, yy, hood_shadow)
            ey = y + h // 2
            if d == "hood_lady_face":
                eyes(ey, iris=(80, 110, 150, 255))
                p.px(cx - w // 4 - 2, ey, (64, 46, 34, 255))
                p.px(cx + w // 4 + 2, ey, (64, 46, 34, 255))
                lip = (190, 86, 88, 255)
            elif d == "hood_will_face":
                eyes(ey, iris=(86, 170, 220, 255))
                p.px(cx - 2, ey + 2, with_alpha(glow + (255,), 210))
                p.px(cx + 2, ey + 2, with_alpha(glow + (255,), 210))
                lip = (132, 78, 74, 255)
            else:
                eyes(ey, iris=(76, 96, 118, 255))
                lip = (142, 84, 72, 255)
            p.px(cx, ey + 2, (0, 0, 0, 45))
            my = y + (3 * h) // 4 + 1
            p.px(cx - 1, my, lip)
            p.px(cx, my, shade(lip, 1.1))
        elif d == "theresa_face":
            # hooded seeress: normal blindfolded face inside a crimson cowl.
            ey = y + max(2, h // 2)
            skin = pal.get("skin", (192, 156, 124)) + (255,)
            skin_dk = shade(skin, 0.84)
            cowl_shadow = (50, 12, 16, 255)
            fx0, fx1 = x + max(1, w // 4), x + w - max(1, w // 4) - 1
            fy0, fy1 = y + max(2, h // 4), y + h - 2
            for yy in range(y, y + h):
                for xx in range(x, x + w):
                    edge = min(xx - x, x + w - 1 - xx, yy - y, y + h - 1 - yy)
                    if fx0 <= xx <= fx1 and fy0 <= yy <= fy1:
                        p.px(xx, yy, skin if (xx + yy) % 5 else skin_dk)
                    elif edge <= 1 or yy < fy0:
                        p.px(xx, yy, cowl_shadow)
            for xx in range(fx0 - 1, fx1 + 2):
                if x <= xx < x + w:
                    p.px(xx, ey, (142, 30, 34, 255))
                    p.px(xx, ey + 1, (104, 22, 26, 255))
            p.px(fx0, ey, (196, 158, 80, 255))
            p.px(fx1, ey + 1, (196, 158, 80, 255))
            # will-tattoo marks under the band
            p.px(fx0, ey + 2, (96, 150, 196, 230))
            p.px(fx0 + 1, ey + 3, (96, 150, 196, 200))
            p.px(fx1, ey + 2, (96, 150, 196, 230))
            p.px(fx1 - 1, ey + 3, (96, 150, 196, 200))
            my = y + (3 * h) // 4 + 1
            p.px(cx, ey + 2, (0, 0, 0, 45))
            p.px(cx - 1, my, (150, 88, 80, 255))
            p.px(cx, my, (160, 94, 84, 255))
        elif d == "theresa_robe":
            # crimson seeress robe: gold sash, rune stitching, clasp
            for i in range(min(w, h)):
                xx, yy = x + i, y + i
                if xx < x + w and yy < y + h:
                    p.px(xx, yy, (176, 140, 72, 255))
                    if xx + 1 < x + w:
                        p.px(xx + 1, yy, (132, 102, 50, 255))
            for yy in range(y + 1, y + h - 1, 3):
                p.px(x + 1, yy, (196, 158, 80, 200))
                p.px(x + w - 2, yy + 1 if yy + 1 < y + h else yy, (196, 158, 80, 200))
            p.px(cx, y + 1, (220, 186, 110, 255))        # throat clasp
        elif d == "twinblade_face":
            # the Bandit King: heavy brow, eyepatch, scar, weathered glare
            ey = y + max(2, h // 2) - 1
            for xx in range(x, x + w):
                p.px(xx, ey - 1, (74, 56, 42, 255))      # heavy brow ridge
            # right eye (his good one): narrow glare
            p.px(cx - w // 4 - 1, ey, (236, 230, 220, 255))
            p.px(cx - w // 4, ey, (60, 48, 36, 255))
            # left eye: black leather patch + strap
            p.px(cx + w // 4, ey, (24, 20, 18, 255))
            p.px(cx + w // 4 + 1, ey, (24, 20, 18, 255))
            p.px(cx + w // 4, ey + 1, (24, 20, 18, 255))
            for xx in range(x, x + w):                    # strap across face
                if (xx + ey) % 2 == 0:
                    p.px(xx, ey - 2, (34, 28, 24, 255))
            # scar down the patched side
            p.px(cx + w // 4 + 1, ey - 3, (150, 96, 84, 255))
            p.px(cx + w // 4 + 2, ey - 2, (150, 96, 84, 255))
            p.px(cx + w // 4 + 1, ey + 2, (150, 96, 84, 255))
            # nose shadow + snarl
            p.px(cx, ey + 2, (0, 0, 0, 60))
            my = y + (3 * h) // 4
            for xx in range(cx - 2, cx + 3):
                p.px(xx, my, (54, 40, 30, 255))
        elif d == "straps":
            # crossed leather chest straps with iron buckle
            for i in range(h):
                t = i / max(1, h - 1)
                xx1 = x + 1 + int(t * (w - 3))
                xx2 = x + w - 2 - int(t * (w - 3))
                yy = y + i
                for xo in (0, 1):
                    if x <= xx1 + xo < x + w:
                        p.px(xx1 + xo, yy, (56, 38, 28, 255))
                    if x <= xx2 + xo < x + w:
                        p.px(xx2 + xo, yy, (48, 32, 24, 255))
            p.px(cx, y + h // 2, (180, 175, 170, 255))   # buckle
            p.px(cx + 1, y + h // 2, (140, 134, 130, 255))
        elif d == "balverine_face":
            ey = y + max(1, h // 4)
            for ex in (cx - w // 4 - 1, cx + w // 4):
                p.px(ex, ey, glow + (255,))
                p.px(ex, ey - 1, with_alpha(glow + (255,), 150))
            # snarl rows of teeth at bottom
            ty = y + h - 2
            for xx in range(x + 1, x + w - 1, 2):
                p.px(xx, ty, (235, 230, 215, 255))
                p.px(xx, ty - 1, (60, 20, 20, 255))
        elif d == "hobbe_face":
            ey = y + h // 3
            for ex in (cx - w // 4 - 1, cx + w // 4 + 1):
                p.px(ex, ey, (240, 220, 80, 255))
                p.px(ex, ey + 1, (30, 24, 20, 255))
            my = y + (3 * h) // 4
            for xx in range(cx - 2, cx + 3):
                p.px(xx, my, (50, 30, 26, 255))
            p.px(cx - 2, my - 1, (235, 230, 210, 255))
            p.px(cx + 2, my - 1, (235, 230, 210, 255))
            # big ears on sides handled by silhouette; nose
            p.px(cx, ey + 1, (90, 100, 60, 255))
            p.px(cx - 1, ey + 1, (90, 100, 60, 255))
        elif d == "skull_face":
            ey = y + h // 3
            for ex in (cx - w // 4 - 1, cx + w // 4):
                p.px(ex, ey, (16, 14, 12, 255))
                p.px(ex + (1 if ex < cx else -1), ey, (16, 14, 12, 255))
                p.px(ex, ey + 1, glow + (200,))
            p.px(cx, ey + 2, (40, 36, 30, 255))
            ty = y + h - 2
            for xx in range(x + 2, x + w - 2):
                p.px(xx, ty, (30, 26, 22, 255) if xx % 2 else (210, 205, 190, 255))
        elif d == "bandit_face":
            ey = y + h // 3
            eyes(ey, iris=(80, 70, 50, 255))
            # bandana over mouth with knot shading
            for yy in range(y + (2 * h) // 3, y + h):
                for xx in range(x, x + w):
                    p.px(xx, yy, (148, 42, 42, 255) if (xx + yy) % 2 else (116, 32, 32, 255))
            p.px(x, y + (2 * h) // 3, (170, 60, 50, 255))
            # scar across brow
            p.px(cx + w // 4 + 1, ey - 2, (150, 80, 70, 255))
            p.px(cx + w // 4 + 1, ey - 1, (160, 90, 76, 255))
            p.px(cx + w // 4 + 2, ey, (150, 80, 70, 255))
        elif d == "guard_helm":
            # full helm crown with rim and rivets
            for yy in range(y, y + h // 3):
                for xx in range(x, x + w):
                    p.px(xx, yy, (158, 163, 176, 255) if (xx + yy) % 3 else (126, 130, 142, 255))
            for xx in range(x, x + w):
                p.px(xx, y + h // 3, (96, 100, 112, 255))  # rim shadow
            p.px(x + 1, y + 1, (210, 214, 224, 255))       # shine
            ey = y + h // 2
            eyes(ey, iris=(70, 80, 100, 255), brows=False)
            # nose guard strip
            for yy in range(y + h // 3, y + h):
                p.px(cx, yy, (172, 177, 190, 255))
            p.px(cx, y + h // 3, (200, 205, 216, 255))
            # chin strap
            for xx in range(x, x + w):
                p.px(xx, y + h - 1, (88, 66, 44, 255))
        elif d == "summoner_face":
            ey = y + h // 2
            for ex in (cx - w // 4 - 1, cx + w // 4):
                p.px(ex, ey, glow + (255,))
                p.px(ex, ey - 1, with_alpha(glow + (255,), 140))
            for yy in range(y, y + h // 3):
                for xx in range(x, x + w):
                    p.px(xx, yy, (30, 22, 48, 255))
        elif d == "assassin_face":
            ey = y + h // 2
            p.px(cx - w // 4 - 1, ey, (255, 120, 90, 255))
            p.px(cx + w // 4, ey, (255, 120, 90, 255))
            for yy in range(y + h // 2 + 2, y + h):
                for xx in range(x, x + w):
                    p.px(xx, yy, (30, 28, 36, 255))
        elif d == "jack_mask":
            # white mask with gold linework, red eyes and purple paint around one eye
            white = (238, 236, 228, 255)
            white_hi = (255, 252, 242, 255)
            white_dk = (190, 186, 178, 255)
            gold = (218, 174, 74, 255)
            purple = (78, 42, 112, 255)
            for yy in range(y, y + h):
                for xx in range(x, x + w):
                    edge = min(xx - x, x + w - 1 - xx, yy - y, y + h - 1 - yy)
                    col = white if edge > 0 else white_dk
                    if (xx + yy) % 7 == 0:
                        col = shade(col, 0.94)
                    p.px(xx, yy, col)
            # purple paint over the upper-left eye region of the mask
            ey = y + h // 3
            for yy in range(y + 1, min(y + h - 1, ey + 2)):
                for xx in range(x + 1, cx):
                    if (xx - (x + 1)) + (yy - (y + 1)) < max(3, w // 2):
                        p.px(xx, yy, purple if (xx + yy) % 2 else shade(purple, 1.18))
            # red glowing eye slits
            for ex in (cx - w // 4 - 1, cx + w // 4):
                p.px(ex, ey, (42, 8, 10, 255))
                p.px(ex + 1, ey, (255, 42, 34, 255))
                p.px(ex, ey + 1, (120, 18, 18, 255))
                p.px(ex + 1, ey + 1, (255, 82, 48, 255))
            # gold lines across brow, cheeks and down the nose
            for xx in range(x + 1, x + w - 1):
                if xx % 2 == 0:
                    p.px(xx, ey - 2, gold)
            for yy in range(ey + 1, y + h - 2):
                p.px(cx, yy, gold if yy % 2 else shade(gold, 0.72))
            p.line(x + 1, ey + 2, cx - 1, y + h - 2, gold, 1)
            p.line(x + w - 2, ey + 2, cx + 1, y + h - 2, gold, 1)
            p.px(cx - 1, y + h - 2, (42, 24, 24, 255))
            p.px(cx, y + h - 2, (42, 24, 24, 255))
            p.px(x + 2, y + 1, white_hi)
        elif d == "minion_face":
            ey = y + h // 3
            for ex in (cx - w // 4 - 1, cx + w // 4):
                p.px(ex, ey, glow + (255,))
            for xx in range(x + 1, x + w - 1):
                p.px(xx, y + h - 2, (40, 36, 44, 255))
            for xx in range(x + 1, x + w - 1, 2):
                p.px(xx, y + h - 3, (200, 200, 210, 255))
        elif d == "troll_face":
            ey = y + h // 3
            for ex in (cx - w // 3, cx + w // 3):
                p.px(ex, ey, glow + (255,))
                p.px(ex, ey + 1, with_alpha(glow + (255,), 120))
            my = y + (3 * h) // 4
            for xx in range(cx - w // 3, cx + w // 3):
                p.px(xx, my, (30, 26, 22, 255))
        elif d == "dragon_face":
            ey = y + h // 4
            for ex in (x + 1, x + w - 2):
                p.px(ex, ey, (255, 220, 90, 255))
                p.px(ex, ey + 1, (160, 60, 20, 255))
            ny = y + (3 * h) // 4
            p.px(x + 1, ny, (30, 16, 14, 255))
            p.px(x + w - 2, ny, (30, 16, 14, 255))
        elif d == "banshee_face":
            ey = y + h // 3
            for ex in (cx - w // 4 - 1, cx + w // 4):
                p.px(ex, ey, (20, 30, 40, 255))
                p.px(ex, ey + 1, glow + (180,))
            # screaming mouth
            my = y + (2 * h) // 3
            for yy in range(my, min(y + h - 1, my + 3)):
                for xx in range(cx - 1, cx + 2):
                    p.px(xx, yy, (12, 16, 22, 255))
        elif d == "hood_face":
            for yy in range(y, y + h):
                for xx in range(x, x + w):
                    d2 = math.hypot(xx - cx + 0.5, yy - (y + h // 2))
                    if d2 < min(w, h) / 2.6:
                        p.px(xx, yy, (16, 20, 24, 255))
            ey = y + h // 2 - 1
            p.px(cx - 2, ey, glow + (255,))
            p.px(cx + 1, ey, glow + (255,))
        elif d == "nymph_face":
            p.px(cx - 1, y + h // 3, (30, 60, 50, 255))
            p.px(cx + 1, y + h // 3, (30, 60, 50, 255))
            p.px(cx, y + h // 2 + 1, (255, 255, 255, 200))
        elif d == "maze_face":
            ey = y + h // 2
            eyes(ey, iris=(110, 200, 240, 255), brows=False)
            # white brows
            p.px(cx - w // 4 - 1, ey - 1, (226, 224, 218, 255))
            p.px(cx - w // 4, ey - 1, (226, 224, 218, 255))
            p.px(cx + w // 4, ey - 1, (226, 224, 218, 255))
            p.px(cx + w // 4 + 1, ey - 1, (226, 224, 218, 255))
            # glowing will-tattoo lines on brow and cheeks
            p.px(cx, y + 1, with_alpha(glow + (255,), 220))
            p.px(cx, y + 2, with_alpha(glow + (255,), 160))
            p.px(cx - w // 4 - 2, ey + 1, with_alpha(glow + (255,), 200))
            p.px(cx - w // 4 - 2, ey + 2, with_alpha(glow + (255,), 140))
            p.px(cx + w // 4 + 2, ey + 1, with_alpha(glow + (255,), 200))
            p.px(cx + w // 4 + 2, ey + 2, with_alpha(glow + (255,), 140))
            # stern mouth
            my = y + (3 * h) // 4 + 1
            p.px(cx - 1, my, (150, 96, 84, 255))
            p.px(cx, my, (150, 96, 84, 255))
        elif d == "beard":
            for yy in range(y + (2 * h) // 3, y + h):
                for xx in range(cx - w // 3, cx + w // 3 + 1):
                    if r.random() < 0.85:
                        shade_v = 195 + r.randrange(40)
                        p.px(xx, yy, (shade_v, shade_v, shade_v - 10, 255))
            # moustache wings
            my = y + (2 * h) // 3
            p.px(cx - w // 3 - 1, my, (200, 200, 192, 255))
            p.px(cx + w // 3 + 1, my, (200, 200, 192, 255))
        elif d == "moustache":
            mc = pal.get("hair", (90, 60, 40))
            my = y + (2 * h) // 3
            for xx in range(cx - 2, cx + 2):
                p.px(xx, my, mc + (255,))
            p.px(cx - 3, my + 1, mc + (255,))
            p.px(cx + 2, my + 1, mc + (255,))
        elif d == "stripes":
            for yy in range(y, y + h, 3):
                for xx in range(x, x + w):
                    p.px(xx, yy, (50, 42, 28, 255))
        elif d == "bug_eyes":
            for ex in (x + 1, x + w - 2):
                p.px(ex, y + 1, (20, 16, 12, 255))
                p.px(ex, y + 2, (60, 40, 20, 255))
        elif d == "claws":
            for xx in range(x, x + w, 2):
                p.px(xx, y + h - 1, (240, 236, 225, 255))
        elif d == "spine":
            for yy in range(y, y + h, 2):
                p.px(cx, yy, (40, 30, 26, 255))
        elif d == "ribs":
            for yy in range(y + 1, y + h - 1, 2):
                for xx in range(x + 1, x + w - 1):
                    p.px(xx, yy, (190, 186, 168, 255))
        elif d == "stitches":
            for xx in range(x + 1, x + w - 1, 3):
                p.px(xx, y + h // 2, (50, 36, 28, 255))
                p.px(xx, y + h // 2 - 1, (180, 160, 130, 255))
        elif d == "belt":
            yy = y + (2 * h) // 3
            for xx in range(x, x + w):
                p.px(xx, yy, (60, 44, 30, 255))
            p.px(cx, yy, (220, 190, 90, 255))
        elif d == "tabard":
            tab = pal.get("tabard", (210, 190, 100)) + (255,)
            tdk = shade(tab, 0.72)
            crest = pal.get("crest", (120, 90, 40)) + (255,)
            x0t, x1t = cx - w // 4 - 1, cx + w // 4 + 1
            for yy in range(y, y + h):
                for xx in range(x0t, x1t + 1):
                    p.px(xx, yy, tab if (xx + yy) % 3 else tdk)
            # edged border
            for yy in range(y, y + h):
                p.px(x0t, yy, tdk)
                p.px(x1t, yy, tdk)
            # heraldic crest emblem centred on the chest
            ey0 = y + h // 4
            p.px(cx, ey0, crest)
            p.px(cx - 1, ey0 + 1, crest)
            p.px(cx + 1, ey0 + 1, crest)
            p.px(cx, ey0 + 2, crest)
            p.px(cx, ey0 + 1, shade(crest, 1.35))
            # bottom dags (split hem)
            for xx in range(x0t, x1t + 1, 2):
                p.px(xx, y + h - 1, (0, 0, 0, 0))
        elif d == "guild_crest":
            p.px(cx, y + 2, (220, 200, 120, 255))
            p.px(cx - 1, y + 3, (220, 200, 120, 255))
            p.px(cx + 1, y + 3, (220, 200, 120, 255))
            p.px(cx, y + 4, (220, 200, 120, 255))
        elif d == "runes":
            for i in range(6):
                xx = x + 1 + r.randrange(max(1, w - 2))
                yy = y + 1 + r.randrange(max(1, h - 2))
                p.px(xx, yy, glow + (235,))
                if r.random() < 0.5:
                    p.px(xx + 1, yy, with_alpha(glow + (255,), 140))
        elif d == "plates":
            for yy in range(y, y + h, 3):
                for xx in range(x, x + w):
                    p.px(xx, yy, (120, 120, 134, 255))
        elif d == "quiver":
            for yy in range(y + 1, y + h // 2):
                p.px(x + w - 2, yy, (110, 80, 50, 255))
            p.px(x + w - 2, y, (200, 60, 50, 255))
        elif d == "satchel":
            p.rect(x + 1, y + h // 2, 3, 3, (96, 66, 40, 255))
            p.px(x + 2, y + h // 2, (220, 190, 90, 255))
        elif d == "apron":
            ap = pal.get("apron", (228, 221, 204)) + (255,)
            ap_dk = shade(ap, 0.82)
            for yy in range(y + h // 3, y + h):
                for xx in range(cx - w // 4, cx + w // 4 + 1):
                    p.px(xx, yy, ap if (xx + yy) % 4 else ap_dk)
            # straps + pocket
            p.px(cx - w // 4, y + h // 3 - 1, (150, 120, 86, 255))
            p.px(cx + w // 4, y + h // 3 - 1, (150, 120, 86, 255))
            py = y + (2 * h) // 3
            for xx in range(cx - 1, cx + 2):
                p.px(xx, py, (150, 120, 86, 255))
        elif d == "vest":
            vest = shade(pal.get("tunic", pal.get("cloth", (100, 80, 60))) + (255,), 0.62)
            edge = shade(vest, 1.35)
            for yy in range(y + 1, y + h - 1):
                p.px(x + 1, yy, vest)
                p.px(x + 2, yy, vest if yy % 2 else edge)
                p.px(x + w - 2, yy, vest)
                p.px(x + w - 3, yy, vest if yy % 2 else edge)
            for yy in range(y + 2, y + h // 2):
                p.px(cx, yy, shade(vest, 0.55))
        elif d == "tool_belt":
            by = y + (2 * h) // 3
            leather = pal.get("belt", (70, 48, 32)) + (255,)
            metal = pal.get("metal", (160, 160, 160)) + (255,)
            for xx in range(x, x + w):
                p.px(xx, by, leather)
            p.px(cx, by, (214, 176, 86, 255))
            p.px(x + 2, by + 1, metal)
            p.px(x + 2, by + 2, shade(metal, 0.7))
            p.px(x + w - 3, by + 1, (110, 72, 42, 255))
        elif d == "embroidered_hem":
            trim = pal.get("crest", (220, 190, 90)) + (255,)
            for xx in range(x + 1, x + w - 1):
                if xx % 2 == 0:
                    p.px(xx, y + h - 2, trim)
                else:
                    p.px(xx, y + h - 1, shade(trim, 0.72))
        elif d == "robe_trim":
            trim = pal.get("crest", (220, 190, 90)) + (255,)
            for yy in range(y + 1, y + h - 1):
                p.px(x + 1, yy, trim if yy % 3 else shade(trim, 0.7))
                p.px(x + w - 2, yy, trim if yy % 3 else shade(trim, 0.7))
            for xx in range(x + 1, x + w - 1):
                p.px(xx, y + h - 1, shade(trim, 0.8))
        elif d == "training_sash":
            sash = pal.get("crest", (220, 190, 90)) + (255,)
            for i in range(h):
                xx = x + w - 2 - int(i * (w - 3) / max(1, h - 1))
                yy = y + i
                if x <= xx < x + w:
                    p.px(xx, yy, sash)
                    if xx - 1 >= x:
                        p.px(xx - 1, yy, shade(sash, 0.65))
        elif d == "net_sash":
            cord = (210, 200, 170, 255)
            for i in range(h):
                xx = x + 1 + int(i * (w - 3) / max(1, h - 1))
                yy = y + i
                if x <= xx < x + w:
                    p.px(xx, yy, cord)
            for yy in range(y + 2, y + h - 1, 3):
                for xx in range(x + 2, x + w - 2, 3):
                    p.px(xx, yy, shade(cord, 0.75))
        elif d == "rolled_sleeves":
            band = (218, 204, 176, 255)
            for xx in range(x, x + w):
                p.px(xx, y + h - 4, band)
                p.px(xx, y + h - 3, shade(band, 0.72))
        elif d == "bodice":
            # laced bodice over dress
            for yy in range(y + 1, y + h - 1):
                p.px(cx - w // 4, yy, (70, 50, 44, 255))
                p.px(cx + w // 4, yy, (70, 50, 44, 255))
            for yy in range(y + 1, y + h - 1, 2):
                p.px(cx - 1, yy, (224, 204, 160, 255))
                p.px(cx + 1, yy + 1 if yy + 1 < y + h - 1 else yy, (224, 204, 160, 255))
        elif d == "jack_robe":
            # layered crimson robe with dark inner tunic, gold clasps and worn folds
            fold_dark = (92, 16, 20, 255)
            fold_hi = (180, 36, 38, 255)
            for yy in range(y, y + h):
                if yy % 4 == 0:
                    for xx in range(x + 1, x + w - 1):
                        if xx % 3 == 0:
                            p.px(xx, yy, fold_dark)
                if yy in (y + 1, y + h - 2):
                    for xx in range(x + 1, x + w - 1):
                        p.px(xx, yy, fold_hi if xx % 2 else fold_dark)
            px0, px1 = cx - w // 4, cx + w // 4
            for yy in range(y, y + h):
                for xx in range(px0, px1 + 1):
                    p.px(xx, yy, (34, 26, 28, 255) if (xx + yy) % 4 else (26, 20, 22, 255))
            # panel edges
            for yy in range(y, y + h):
                p.px(px0, yy, (154, 118, 48, 255) if yy % 2 else (86, 42, 28, 255))
                p.px(px1, yy, (154, 118, 48, 255) if yy % 2 else (86, 42, 28, 255))
            # gold clasps down the centre
            for yy in range(y + 2, y + h - 2, 3):
                p.px(cx - 1, yy, (212, 172, 84, 255))
                p.px(cx, yy, (235, 194, 96, 255))
                p.px(cx, yy + 1, (150, 116, 48, 255))
            # high collar shadow beneath the mask
            for xx in range(cx - 2, cx + 3):
                p.px(xx, y + 1, (34, 20, 22, 255))
            # dark belt with gold buckle
            by = y + (2 * h) // 3
            for xx in range(x, x + w):
                p.px(xx, by, (20, 14, 16, 255))
                if xx % 3 == 0 and by + 1 < y + h:
                    p.px(xx, by + 1, (70, 38, 24, 255))
            p.px(cx - 1, by, (212, 172, 84, 255))
            p.px(cx, by, (235, 194, 96, 255))
            p.px(cx + 1, by, (150, 116, 48, 255))
        elif d == "bandolier":
            leather = (116, 64, 32, 255)
            leather_dk = (48, 28, 18, 255)
            metal = (214, 176, 92, 255)
            for i in range(h):
                xx = x + 1 + int(i * (w - 3) / max(1, h - 1))
                yy = y + i
                if x <= xx < x + w:
                    p.px(xx, yy, leather)
                    if xx + 1 < x + w:
                        p.px(xx + 1, yy, leather_dk)
                    if xx - 1 >= x:
                        p.px(xx - 1, yy, shade(leather, 1.25))
            for yy in range(y + 2, y + h - 1, 3):
                xx = x + 1 + int((yy - y) * (w - 3) / max(1, h - 1))
                if x <= xx < x + w:
                    p.px(xx, yy, metal)
        elif d == "robe_split":
            fold_dark = (80, 12, 18, 255)
            fold_hi = (180, 34, 38, 255)
            for yy in range(y, y + h):
                p.px(cx, yy, (28, 20, 22, 255))
                if cx - 1 >= x:
                    p.px(cx - 1, yy, fold_dark)
                if cx + 1 < x + w:
                    p.px(cx + 1, yy, fold_dark)
            for xx in range(x + 1, x + w - 1):
                p.px(xx, y + h - 1, (154, 118, 48, 255) if xx % 2 else fold_dark)
                if xx % 3 == 0:
                    p.px(xx, y + h - 3, fold_hi)
        elif d == "steel_chestplate":
            hi = (214, 220, 224, 255)
            mid = (154, 162, 170, 255)
            dk = (82, 88, 96, 255)
            for yy in range(y, y + h):
                for xx in range(x, x + w):
                    shoulder_cut = yy < y + 2 and abs(xx - cx) > max(2, w // 3)
                    if shoulder_cut:
                        p.px(xx, yy, (0, 0, 0, 0))
                    elif abs(xx - cx) <= 1:
                        p.px(xx, yy, dk)
                    elif yy < y + 2 or yy > y + h - 3:
                        p.px(xx, yy, mid)
            for yy in range(y + 1, y + h - 1, 3):
                p.px(x + 1, yy, hi)
                p.px(x + w - 2, yy, dk)
            p.px(cx - 1, y + 2, hi)
            p.px(cx + 1, y + 2, dk)
            for xx in (x + 2, x + w - 3):
                for yy in range(y + 2, y + h - 2, 3):
                    p.px(xx, yy, hi if xx < cx else dk)
        elif d == "steel_plates":
            hi = (210, 216, 222, 255)
            dk = (86, 92, 100, 255)
            for yy in range(y + 1, y + h - 1, 4):
                for xx in range(x, x + w):
                    p.px(xx, yy, dk)
                p.px(x + 1, yy - 1 if yy > y else yy, hi)
            for xx in range(x + 1, x + w - 1, 3):
                p.px(xx, y + h - 2, hi)
        elif d == "trim_cuff":
            for xx in range(x, x + w):
                p.px(xx, y + h - 2, (212, 172, 84, 255) if xx % 2 else (180, 140, 60, 255))
                p.px(xx, y + h - 1, (150, 116, 48, 255))
        elif d == "necklace":
            p.px(cx, y + 1, (250, 220, 120, 255))
            p.px(cx - 1, y + 1, (250, 220, 120, 255))
            p.px(cx + 1, y + 1, (250, 220, 120, 255))
            p.px(cx, y + 2, (120, 220, 240, 255))
        elif d == "corset":
            for yy in range(y, y + h):
                p.px(cx, yy, (60, 70, 84, 255))
            for yy in range(y + 1, y + h, 2):
                p.px(cx - 1, yy, (200, 210, 224, 200))
                p.px(cx + 1, yy, (200, 210, 224, 200))
        elif d == "tatters":
            for xx in range(x, x + w):
                yy = y + h - 1 - (xx % 3)
                for clear_y in range(yy + 1, y + h):
                    p.px(xx, clear_y, (0, 0, 0, 0))
        elif d == "hair":
            pass
        elif d == "trim":
            for xx in range(x, x + w):
                p.px(xx, y, (220, 190, 90, 255))
                p.px(xx, y + h - 1, (220, 190, 90, 255))
        elif d == "daggers":
            p.px(x + 1, y + h // 2, (200, 205, 215, 255))
            p.px(x + 1, y + h // 2 + 1, (200, 205, 215, 255))
            p.px(x + 1, y + h // 2 + 2, (140, 100, 60, 255))
        elif d == "moss":
            for i in range(max(2, w * h // 14)):
                xx = x + r.randrange(max(1, w))
                yy = y + r.randrange(max(1, h // 2))
                p.px(xx, yy, (86, 116, 60, 255))
        elif d == "ice_shards":
            for i in range(max(2, w // 3)):
                xx = x + r.randrange(max(1, w))
                p.px(xx, y + 1, (220, 240, 250, 255))
                p.px(xx, y + 2, (180, 215, 235, 255))
        elif d == "cracks":
            for c in range(2):
                cx2 = x + r.randrange(max(1, w))
                cy2 = y + r.randrange(max(1, h // 2))
                for step in range(3):
                    p.px(cx2, cy2, glow + (200,))
                    cx2 += r.choice((-1, 0, 1))
                    cy2 += 1
        elif d == "shell_split":
            for yy in range(y, y + h):
                p.px(cx, yy, (28, 30, 20, 255))
        elif d == "shell_plates":
            for yy in range(y, y + h, 3):
                for xx in range(x, x + w):
                    p.px(xx, yy, (50, 34, 70, 255))
        elif d == "segments":
            for yy in range(y, y + h, 2):
                for xx in range(x, x + w):
                    p.px(xx, yy, (50, 34, 70, 255))
        elif d == "stinger":
            p.px(cx, y + h - 1, (255, 240, 140, 255))
        elif d == "mandibles":
            p.px(x, y + h - 1, (90, 70, 30, 255))
            p.px(x + w - 1, y + h - 1, (90, 70, 30, 255))
        elif d == "wing_bones":
            for xx in range(x, x + w, 4):
                for yy in range(y, y + h):
                    p.px(xx, yy, (40, 14, 16, 255))
        elif d == "spikes":
            for xx in range(x, x + w, 2):
                p.px(xx, y, (220, 200, 160, 255))
        elif d == "belly_plates":
            for yy in range(y + h // 2, y + h, 2):
                for xx in range(x + 1, x + w - 1):
                    p.px(xx, yy, (190, 150, 110, 255))
        elif d == "horns":
            pass
        elif d == "door_slab":
            # masonry coursing so the living door matches its stone arch
            course = 6
            mortar = (88, 84, 78, 255)
            for yy in range(y, y + h):
                row = (yy - y) // course
                for xx in range(x, x + w):
                    if (yy - y) % course == 0:
                        p.px(xx, yy, mortar)
                    elif (xx - x + (row % 2) * (course)) % (course * 2) == 0:
                        p.px(xx, yy, mortar)
            # weathering streaks + moss
            for i in range(14):
                xx = x + r.randrange(max(1, w))
                yy0 = y + r.randrange(max(1, h - 6))
                for t in range(r.randrange(3, 7)):
                    p.px(xx, yy0 + t, (104, 108, 92, 200))
        elif d == "door_eye":
            # carved stone eye: weathered socket, pale stone iris, dark pupil
            for yy in range(y, y + h):
                for xx in range(x, x + w):
                    p.px(xx, yy, (52, 47, 42, 255))
            for yy in range(y + 1, y + h - 1):
                for xx in range(x + 1, x + w - 1):
                    p.px(xx, yy, (188, 182, 170, 255))
            # stone iris ring + recessed pupil
            iy = y + h // 2
            p.px(cx - 1, iy, (146, 140, 128, 255))
            p.px(cx + 1, iy, (146, 140, 128, 255))
            p.px(cx, iy - 1, (146, 140, 128, 255))
            p.px(cx, iy + 1, (146, 140, 128, 255))
            p.px(cx, iy, (38, 34, 30, 255))
            # weather streak under the eye
            p.px(cx - 1, y + h - 1, (96, 100, 86, 220))
        elif d == "door_mouth":
            # arched recessed stone mouth; the separate lip geometry carries the shape.
            stone_hi = (150, 144, 134, 255)
            stone_mid = (92, 86, 78, 255)
            stone_dark = (52, 46, 40, 255)
            for yy in range(y, y + h):
                for xx in range(x, x + w):
                    nx = (xx - cx) / max(1, w / 2)
                    ny = (yy - (y + h * 0.50)) / max(1, h * 0.58)
                    if nx * nx + ny * ny <= 1.0:
                        edge = abs(1.0 - (nx * nx + ny * ny))
                        col = stone_dark if edge > 0.36 else stone_mid
                        if r.random() < 0.12:
                            col = shade(col, 1.18)
                        p.px(xx, yy, col)
                    else:
                        p.px(xx, yy, (0, 0, 0, 0))
            for xx in range(x + 2, x + w - 2):
                if xx % 2 == 0:
                    p.px(xx, y + 1, stone_hi)
                    p.px(xx, y + h - 2, stone_mid)
            for yy in range(y + 1, y + h - 1):
                if yy % 2 == 0:
                    p.px(x + 1, yy, stone_mid)
                    p.px(x + w - 2, yy, stone_hi)
            for xx in range(cx - 2, cx + 3):
                p.px(xx, y + h // 2, stone_dark if xx != cx else shade(stone_dark, 1.2))
        elif d == "brow":
            for xx in range(x, x + w):
                p.px(xx, y + h - 1, (40, 34, 30, 255))
        elif d == "hood":
            for yy in range(y, y + h // 4):
                for xx in range(x, x + w):
                    p.px(xx, yy, (40, 36, 46, 255))


def paint_mob(mob):
    parts = build_parts(mob)
    tw, th, uv = pack_uvs(parts)
    p = Px(tw, th)
    pal = mob_palette(mob)
    glow = pal.get("glowcol", (255, 255, 255))
    r = rng("mob", mob["id"])
    tint = mob.get("tint")
    for pi, part in enumerate(parts):
        part_role = part.get("role", "cloth")
        cube_roles = part.get("cube_roles", {})
        decor_cube = part.get("decor_cube", 0)
        for ci, cube in enumerate(part["cubes"]):
            role = cube_roles.get(ci, part_role)
            base = (pal.get(role)
                    or {"hair": (96, 70, 44), "horn": (224, 214, 192),
                        "boots": (76, 56, 38), "belt": (58, 42, 28),
                        "tabard": (204, 182, 92), "crest": (200, 60, 50),
                        "straw": (208, 182, 108)}.get(role)
                    or pal.get("cloth") or pal.get("skin") or (120, 110, 100))
            if tint:
                base = mix(base, tint, 0.45)[:3]
            style = ROLE_TEXTURE.get(role, (None, "cloth"))[1]
            sx, sy, sz = (max(1, round(v)) for v in cube["size"])
            u, v = uv[(pi, ci)]
            # six faces
            fill_face(p, u + sz, v, sx, sz, shade(base, 1.12)[:3], style, r)            # top
            fill_face(p, u + sz + sx, v, sx, sz, shade(base, 0.6)[:3], style, r)        # bottom
            fill_face(p, u, v + sz, sz, sy, shade(base, 0.82)[:3], style, r)            # right
            fill_face(p, u + sz, v + sz, sx, sy, base, style, r)                        # front
            fill_face(p, u + sz + sx, v + sz, sz, sy, shade(base, 0.9)[:3], style, r)   # left
            fill_face(p, u + sz + sx + sz, v + sz, sx, sy, shade(base, 0.72)[:3], style, r)  # back
            if ci == decor_cube and part.get("decor"):
                decorate_front(p, u + sz, v + sz, sx, sy, part["decor"], pal, glow, r)
    p.save(OUT / f"{mob['id']}.png")
    return tw, th


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for mob in MOBS:
        tw, th = paint_mob(mob)
    print(f"painted {len(MOBS)} entity textures -> {OUT}")
    paint_all_armor_layers()


# ---------------------------------------------------------------------------
# WORN ARMOR LAYERS — 64x32 classic armor textures so equipped fc: armor is
# actually visible on the player (consumed by attachables in gen_resources).
# ---------------------------------------------------------------------------

ARMOR_OUT = RP / "textures" / "models" / "armor"


def _box_region(p, u, v, sx, sy, sz, base, style, r):
    """Paint all six faces of a classic box-UV region."""
    fill_face(p, u + sz, v, sx, sz, shade(base, 1.12)[:3], style, r)
    fill_face(p, u + sz + sx, v, sx, sz, shade(base, 0.6)[:3], style, r)
    fill_face(p, u, v + sz, sz, sy, shade(base, 0.82)[:3], style, r)
    fill_face(p, u + sz, v + sz, sx, sy, base, style, r)
    fill_face(p, u + sz + sx, v + sz, sz, sy, shade(base, 0.9)[:3], style, r)
    fill_face(p, u + sz + sx + sz, v + sz, sx, sy, shade(base, 0.72)[:3], style, r)


def _clear(p, x, y, w, h):
    for yy in range(y, y + h):
        for xx in range(x, x + w):
            p.px(xx, yy, (0, 0, 0, 0))


def paint_armor_set_layers(set_rec):
    """layer_1: helmet + chest + arms + boots; layer_2: leggings."""
    pal = set_rec["palette"]
    base = pal["base"]
    trim = pal["trim"] + (255,)
    style = "metal" if pal.get("metal") else ("leather" if "leather" in set_rec["id"] else "cloth")
    hood = pal.get("hood")
    r = rng("armorlayer", set_rec["id"])

    # ---- layer 1 ----
    p1 = Px(64, 32)
    # helmet head box at (0,0) 8x8x8
    _box_region(p1, 0, 0, 8, 8, 8, base, style, r)
    if hood:
        # open cowl: clear the face, keep brow rim + sides
        _clear(p1, 9, 11, 6, 5)
        for xx in range(8, 16):
            p1.px(xx, 10, shade(base, 0.7)[:3] + (255,))
    elif set_rec.get("hat") and not pal.get("metal"):
        # brimmed/cloth hat: keep crown band only, open face fully
        _clear(p1, 8, 12, 8, 4)
        for xx in range(8, 16):
            p1.px(xx, 11, trim)
    else:
        # metal helm: open eye slot, keep nasal bar + cheeks
        _clear(p1, 9, 12, 2, 2)
        _clear(p1, 13, 12, 2, 2)
        p1.px(11, 12, shade(base, 1.2)[:3] + (255,))
        p1.px(12, 12, shade(base, 1.2)[:3] + (255,))
        for xx in range(8, 16):
            p1.px(xx, 8, trim)   # brow trim line
    # chest body box at (16,16) 8x12x4
    _box_region(p1, 16, 16, 8, 12, 4, base, style, r)
    for xx in range(20, 28):
        p1.px(xx, 30, trim)      # hem trim
        p1.px(xx, 20, trim)      # collar trim
    accent = pal.get("accent")
    if set_rec.get("id") == "apprentice":
        robe_edge = shade(base, 1.12)[:3] + (255,)
        robe_shadow = shade(base, 0.75)[:3] + (255,)
        robe_sash = accent + (255,) if accent else trim
        for xx in range(18, 26):
            p1.px(xx, 18, robe_edge)
            p1.px(xx, 19, robe_edge)
            p1.px(xx, 29, robe_shadow)
        for yy in range(19, 30):
            p1.px(18, yy, robe_edge)
            p1.px(25, yy, robe_edge)
        for offset in range(8):
            p1.px(19 + offset, 21 + offset, robe_sash)
            p1.px(24 - offset, 21 + offset, robe_sash)
    if accent:
        for i in range(8):       # apprentice-style sash
            p1.px(20 + i, 21 + i, accent + (255,))
    # arms box at (40,16) 4x12x4
    _box_region(p1, 40, 16, 4, 12, 4, shade(base, 0.95)[:3], style, r)
    for xx in range(44, 48):
        p1.px(xx, 27, trim)      # cuff
    # boots: leg box at (0,16) 4x12x4. The vanilla boots geometry renders the
    # WHOLE leg, so only the lower portion may be opaque — if the upper leg is
    # painted, the "boots" read as full leggings/pants on the player. Paint the
    # box, then wipe the upper-leg faces so just the boot (rows 27..31) remains.
    _box_region(p1, 0, 16, 4, 12, 4, shade(base, 0.85)[:3], style, r)
    _clear(p1, 0, 20, 16, 7)   # upper-leg side faces (keep the lower boot only)
    _clear(p1, 4, 16, 4, 4)    # the leg's top cross-section (hidden in the body)
    for xx in range(0, 16):
        p1.px(xx, 27, trim)    # cuff line along the top of the boot
    p1.save(ARMOR_OUT / f"fc_{set_rec['id']}_layer_1.png")

    # ---- layer 2 (leggings) ----
    p2 = Px(64, 32)
    _box_region(p2, 0, 16, 4, 12, 4, base, style, r)
    _box_region(p2, 16, 16, 8, 12, 4, shade(base, 0.9)[:3], style, r)
    for xx in range(20, 28):
        p2.px(xx, 20, trim)      # belt line
    p2.save(ARMOR_OUT / f"fc_{set_rec['id']}_layer_2.png")


def paint_all_armor_layers():
    import fc_data
    ARMOR_OUT.mkdir(parents=True, exist_ok=True)
    count = 0
    for s in fc_data.ARMOR_SETS:
        paint_armor_set_layers(s)
        count += 1
    for h in fc_data.HATS:
        rec = dict(h)
        rec["hat"] = True
        paint_armor_set_layers(rec)
        count += 1
    print(f"painted {count} worn-armor layer sets -> {ARMOR_OUT}")


if __name__ == "__main__":
    main()

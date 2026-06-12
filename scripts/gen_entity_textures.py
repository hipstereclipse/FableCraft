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
            # skin reference: crimson hood framing a stark white mask
            hoodc = (122, 16, 18, 255)
            hooddk = (84, 10, 12, 255)
            for yy in range(y, y + h):
                for xx in range(x, x + w):
                    p.px(xx, yy, hoodc if (xx + yy) % 3 else hooddk)
            mx0, mx1 = x + 1, x + w - 2
            my0, my1 = y + 1, y + h - 1
            for yy in range(my0, my1):
                for xx in range(mx0, mx1 + 1):
                    sh = 1.0 - 0.18 * ((yy - my0) / max(1, my1 - my0 - 1))
                    v = int(246 * sh) if (xx + yy) % 6 else int(234 * sh)
                    p.px(xx, yy, (v, v, min(255, v + 5), 255))
            # mask edge shading
            for yy in range(my0, my1):
                p.px(mx0, yy, (210, 208, 214, 255))
                p.px(mx1, yy, (194, 192, 200, 255))
            # narrow dark eye slits with ember glints
            ey = y + h // 3
            for ex in (cx - w // 4 - 1, cx + w // 4):
                p.px(ex, ey, (24, 18, 18, 255))
                p.px(ex + 1, ey, (24, 18, 18, 255))
                p.px(ex + (1 if ex < cx else 0), ey, (250, 90, 50, 255))
                p.px(ex, ey - 1, (152, 148, 154, 255))
                p.px(ex + 1, ey - 1, (152, 148, 154, 255))
            # smooth nose ridge + grim mouth slit
            for yy in range(ey + 1, y + (3 * h) // 4):
                p.px(cx, yy, (224, 222, 228, 255))
            my = y + (3 * h) // 4
            for xx in range(cx - 1, cx + 2):
                p.px(xx, my, (40, 32, 32, 255))
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
            for yy in range(y + h // 3, y + h):
                for xx in range(cx - w // 4, cx + w // 4 + 1):
                    p.px(xx, yy, (228, 221, 204, 255) if (xx + yy) % 4 else (214, 206, 188, 255))
            # straps + pocket
            p.px(cx - w // 4, y + h // 3 - 1, (150, 120, 86, 255))
            p.px(cx + w // 4, y + h // 3 - 1, (150, 120, 86, 255))
            py = y + (2 * h) // 3
            for xx in range(cx - 1, cx + 2):
                p.px(xx, py, (150, 120, 86, 255))
        elif d == "bodice":
            # laced bodice over dress
            for yy in range(y + 1, y + h - 1):
                p.px(cx - w // 4, yy, (70, 50, 44, 255))
                p.px(cx + w // 4, yy, (70, 50, 44, 255))
            for yy in range(y + 1, y + h - 1, 2):
                p.px(cx - 1, yy, (224, 204, 160, 255))
                p.px(cx + 1, yy + 1 if yy + 1 < y + h - 1 else yy, (224, 204, 160, 255))
        elif d == "jack_robe":
            # skin reference: black coat panel over crimson, gold clasps, dark belt
            px0, px1 = cx - w // 4, cx + w // 4
            for yy in range(y, y + h):
                for xx in range(px0, px1 + 1):
                    p.px(xx, yy, (34, 26, 28, 255) if (xx + yy) % 4 else (26, 20, 22, 255))
            # panel edges
            for yy in range(y, y + h):
                p.px(px0, yy, (60, 24, 26, 255))
                p.px(px1, yy, (60, 24, 26, 255))
            # gold clasps down the centre
            for yy in range(y + 2, y + h - 2, 3):
                p.px(cx, yy, (212, 172, 84, 255))
                p.px(cx, yy + 1, (150, 116, 48, 255))
            # dark belt with gold buckle
            by = y + (2 * h) // 3
            for xx in range(x, x + w):
                p.px(xx, by, (20, 14, 16, 255))
            p.px(cx, by, (212, 172, 84, 255))
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
            # dark carved socket with a blazing iris
            for yy in range(y, y + h):
                for xx in range(x, x + w):
                    p.px(xx, yy, (42, 36, 30, 255))
            for yy in range(y + 1, y + h - 1):
                for xx in range(x + 1, x + w - 1):
                    p.px(xx, yy, glow + (255,))
            p.px(cx - 1, y + h // 2, (255, 255, 230, 255))
            p.px(cx, y + h // 2, (255, 255, 235, 255))
            p.px(cx, y + h // 2 - 1, (255, 245, 200, 255))
        elif d == "door_mouth":
            # cavernous mouth with irregular teeth
            for yy in range(y, y + h):
                for xx in range(x, x + w):
                    p.px(xx, yy, (16, 11, 9, 255))
            for xx in range(x + 1, x + w - 1, 2):
                deep = 2 if xx % 3 == 0 else 1
                for t in range(deep):
                    p.px(xx, y + 1 + t, (216, 210, 194, 255))
                p.px(xx + 1, y + h - 2, (198, 190, 174, 255))
                if xx % 4 == 1:
                    p.px(xx + 1, y + h - 3, (198, 190, 174, 255))
            for xx in range(x, x + w):
                p.px(xx, y, (72, 64, 56, 255))
                p.px(xx, y + h - 1, (72, 64, 56, 255))
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


if __name__ == "__main__":
    main()

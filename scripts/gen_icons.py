"""gen_icons.py — pack_icon.png for BP & RP: a Guild Seal motif."""
import math

from fc_lib import BP, RP, Px, shade

def paint_icon(evil=False):
    p = Px(128, 128)
    # background: parchment vignette
    bg_in = (58, 46, 34, 255) if not evil else (40, 26, 30, 255)
    bg_out = (28, 22, 16, 255)
    for y in range(128):
        for x in range(128):
            d = math.hypot(x - 64, y - 64) / 90
            t = max(0.0, 1 - d)
            c = tuple(int(bg_out[i] + (bg_in[i] - bg_out[i]) * t) for i in range(3)) + (255,)
            p.px(x, y, c)
    gold = (250, 210, 90, 255)
    blue = (90, 140, 230, 255) if not evil else (170, 60, 60, 255)
    # outer ring
    for a in range(0, 3600):
        ang = a / 3600 * 2 * math.pi
        for rr in (46, 47, 48):
            x = 64 + math.cos(ang) * rr
            y = 64 + math.sin(ang) * rr
            p.px(round(x), round(y), gold if rr != 47 else shade(gold, 0.8))
    # studs
    for a in range(0, 360, 30):
        x = 64 + math.cos(math.radians(a)) * 47
        y = 64 + math.sin(math.radians(a)) * 47
        for dx in range(-2, 3):
            for dy in range(-2, 3):
                if dx * dx + dy * dy <= 4:
                    p.px(round(x) + dx, round(y) + dy, shade(gold, 1.2))
    # inner disc
    for y in range(128):
        for x in range(128):
            d = math.hypot(x - 64, y - 64)
            if d < 44:
                t = d / 44
                c = tuple(int(blue[i] * (1.15 - 0.5 * t)) for i in range(3)) + (255,)
                p.px(x, y, c)
    # sword silhouette
    sw = (240, 235, 220, 255)
    dk = (150, 145, 130, 255)
    for y in range(30, 88):
        p.px(63, y, sw)
        p.px(64, y, sw)
        p.px(65, y, dk)
    p.px(63, 28, sw)
    p.px(64, 28, sw)
    p.px(64, 29, sw)
    for x in range(52, 77):
        p.px(x, 88, gold)
        p.px(x, 89, shade(gold, 0.75))
    for y in range(90, 102):
        p.px(63, y, shade(gold, 0.9))
        p.px(64, y, shade(gold, 0.9))
    for dx in range(-3, 4):
        for dy in range(-3, 4):
            if dx * dx + dy * dy <= 9:
                p.px(64 + dx, 105 + dy, gold)
    # will-lines radiating
    glow = (140, 220, 255, 160) if not evil else (255, 120, 80, 160)
    for a in range(0, 360, 45):
        for rr in range(20, 36, 2):
            x = 64 + math.cos(math.radians(a + rr)) * rr
            y = 64 + math.sin(math.radians(a + rr)) * rr
            p.px(round(x), round(y), glow)
    return p

paint_icon(False).save(RP / "pack_icon.png")
paint_icon(True).save(BP / "pack_icon.png")
print("pack icons painted")

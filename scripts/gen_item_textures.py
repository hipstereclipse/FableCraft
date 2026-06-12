"""gen_item_textures.py — paints every item icon (16x16 or 32x32) for the RP.

Each weapon kind gets bespoke pixel art; materials tint the blade/haft.
Run:  python scripts/gen_item_textures.py
"""
import math

from fc_lib import RP, Px, mix, ramp, rng, shade, with_alpha
import fc_data

OUT = RP / "textures" / "items"

# Material palettes for weapon parts
MAT_PAL = {
    "iron":      {"blade": (176, 180, 190), "dark": (104, 108, 118), "haft": (104, 78, 50)},
    "steel":     {"blade": (204, 214, 228), "dark": (124, 136, 156), "haft": (90, 70, 48)},
    "obsidian":  {"blade": (118, 96, 160),  "dark": (58, 44, 84),    "haft": (62, 48, 44)},
    "master":    {"blade": (238, 228, 192), "dark": (172, 152, 102), "haft": (70, 50, 80)},
    "yew":       {"blade": (158, 126, 80),  "dark": (104, 82, 50),   "haft": (158, 126, 80)},
    "oak":       {"blade": (128, 98, 62),   "dark": (86, 64, 40),    "haft": (128, 98, 62)},
    "ebony":     {"blade": (84, 72, 80),    "dark": (44, 36, 42),    "haft": (84, 72, 80)},
    "legendary": {"blade": (240, 220, 160), "dark": (180, 140, 80),  "haft": (90, 40, 40)},
}

GOLD = (250, 210, 90)
DARKLINE = (28, 20, 16, 255)


def diag(p, t, c, w=1):
    """Plot along the main diagonal: t in [0..15] maps bottom-left->top-right."""
    x = t
    y = p.h - 1 - t
    for ox in range(w):
        for oy in range(w):
            p.px(x + ox, y + oy, c)


# ---------------------------------------------------------------------------
# Weapon painters (all draw blade bottom-left -> top-right diagonal)
# ---------------------------------------------------------------------------

def paint_sword(p, pal, r, length=11, width=2, guard=True, curved=False):
    blade, dark, haft = pal["blade"], pal["dark"], pal["haft"]
    hi = shade(blade, 1.35)
    # grip with wrap bands
    for t in range(1, 4):
        diag(p, t, shade(haft, 1.05 if t % 2 else 0.75), 2)
    p.px(1, p.h - 2, shade(haft, 0.55))
    # pommel
    p.px(0, p.h - 1, GOLD + (255,))
    p.px(1, p.h - 1, shade(GOLD + (255,), 0.7))
    p.px(0, p.h - 2, shade(GOLD + (255,), 1.25))
    # guard
    if guard:
        g = shade(GOLD + (255,), 1.0)
        p.px(3, p.h - 6, g)
        p.px(4, p.h - 5, g)
        p.px(5, p.h - 4, g)
        p.px(6, p.h - 5, shade(g, 0.75))
        p.px(4, p.h - 7, shade(g, 1.2))
        p.px(3, p.h - 5, shade(g, 0.7))
    # blade with fuller groove
    for t in range(5, 5 + length):
        bend = 0
        if curved:
            bend = round(math.sin((t - 5) / length * math.pi) * 1.4)
        x = t
        y = p.h - 1 - t - bend
        p.px(x, y, blade if t % 3 else shade(blade, 0.88))
        p.px(x + 1, y, hi)
        if width > 1:
            p.px(x, y + 1, dark)
        if width > 2:
            p.px(x + 1, y - 1, hi)
    # tip sparkle
    tipx = 5 + length
    tipy = p.h - 1 - tipx
    p.px(tipx, tipy, hi)
    p.px(tipx + 1, tipy, (255, 255, 255, 235))


def paint_greatsword(p, pal, r):
    blade, dark, haft = pal["blade"], pal["dark"], pal["haft"]
    hi = shade(blade, 1.35)
    for t in range(1, 5):
        diag(p, t, shade(haft, 0.9), 2)
    p.px(0, p.h - 1, GOLD + (255,))
    g = GOLD + (255,)
    for o in (-1, 0, 1, 2):
        p.px(5 + o, p.h - 6 + (1 - o), g if o % 2 == 0 else shade(g, 0.75))
    for t in range(6, 15):
        x, y = t, p.h - 1 - t
        p.px(x, y, blade)
        p.px(x + 1, y, hi)
        p.px(x, y + 1, blade)
        p.px(x - 1, y + 1, dark)
        if t < 13:
            p.px(x + 1, y - 1, hi)
    p.px(15, 0, hi)
    # fuller line
    for t in range(7, 13):
        p.px(t, p.h - 1 - t, shade(dark, 1.1))


def paint_katana(p, pal, r):
    blade, dark, haft = pal["blade"], pal["dark"], pal["haft"]
    hi = shade(blade, 1.4)
    for t in range(1, 5):
        diag(p, t, (30, 26, 34, 255), 1)
        p.px(t + 1, p.h - 1 - t, (60, 50, 70, 255))
    p.px(5, p.h - 6, GOLD + (255,))
    p.px(6, p.h - 6, shade(GOLD + (255,), 0.7))
    p.px(5, p.h - 7, shade(GOLD + (255,), 0.7))
    for t in range(6, 15):
        arc = round(math.sin((t - 6) / 9 * math.pi * 0.5) * 2)
        x, y = t, p.h - 1 - t - arc
        p.px(x, y, blade)
        p.px(x, y - 1, hi)
    p.px(15, 1, hi)
    p.px(15, 0, hi)


def paint_cleaver(p, pal, r):
    blade, dark, haft = pal["blade"], pal["dark"], pal["haft"]
    hi = shade(blade, 1.3)
    for t in range(1, 5):
        diag(p, t, shade(haft, 0.95), 2)
    p.px(0, p.h - 1, shade(haft, 0.6))
    # broad rectangular blade
    for t in range(5, 13):
        x, y = t, p.h - 1 - t
        p.px(x, y, blade)
        p.px(x + 1, y, hi)
        p.px(x, y + 1, blade)
        p.px(x + 1, y + 1, blade)
        p.px(x - 1, y + 1, dark)
        p.px(x + 2, y, hi)
    p.px(13, 1, hi)
    p.px(14, 2, hi)
    p.px(14, 1, hi)


def paint_axe(p, pal, r, double=False):
    blade, dark, haft = pal["blade"], pal["dark"], pal["haft"]
    hi = shade(blade, 1.3)
    for t in range(1, 11):
        diag(p, t, shade(haft, 0.95 if t % 2 else 0.8), 1)
        p.px(t + 1, p.h - 1 - t, shade(haft, 0.65))
    # axe head at upper end
    cx, cy = 11, 4
    for dx in range(-1, 4):
        for dy in range(-4, 2):
            d = math.hypot(dx - 1.2, dy + 1.5)
            if d < 3.2:
                p.px(cx + dx, cy + dy, blade if d > 1.8 else dark)
    for dy in range(-4, 2):
        p.px(cx + 3, cy + dy, hi)
    if double:
        for dx in range(-4, 0):
            for dy in range(-3, 1):
                d = math.hypot(dx + 2.2, dy + 1.0)
                if d < 2.6:
                    p.px(cx + dx, cy + dy, blade if d > 1.4 else dark)


def paint_mace(p, pal, r):
    blade, dark, haft = pal["blade"], pal["dark"], pal["haft"]
    hi = shade(blade, 1.35)
    for t in range(1, 10):
        diag(p, t, shade(haft, 0.95 if t % 2 else 0.8), 1)
    p.px(0, p.h - 1, GOLD + (255,))
    # spiked ball head
    cx, cy = 11, 4
    for dx in range(-3, 4):
        for dy in range(-3, 4):
            d = math.hypot(dx, dy)
            if d <= 2.6:
                p.px(cx + dx, cy + dy, blade if d > 1.4 else hi)
    for ang in range(8):
        a = ang * math.pi / 4
        sx = cx + round(math.cos(a) * 3.6)
        sy = cy + round(math.sin(a) * 3.6)
        p.px(sx, sy, dark)


def paint_hammer(p, pal, r, pick=False):
    blade, dark, haft = pal["blade"], pal["dark"], pal["haft"]
    hi = shade(blade, 1.3)
    for t in range(1, 10):
        diag(p, t, shade(haft, 0.95 if t % 2 else 0.8), 1)
        p.px(t + 1, p.h - 1 - t, shade(haft, 0.6))
    # head: blocky slab perpendicular to handle
    cx, cy = 11, 4
    for dx in range(-2, 3):
        for dy in range(-3, 3):
            p.px(cx + dx, cy + dy, blade if (dx + dy) % 2 == 0 else shade(blade, 0.92))
    for dy in range(-3, 3):
        p.px(cx + 3, cy + dy, hi)
        p.px(cx - 3, cy + dy, dark)
    if pick:
        # pick spike
        for i, dx in enumerate(range(-6, -3)):
            p.px(cx + dx, cy + 1 - i, dark)
            p.px(cx + dx, cy - i, blade)


def paint_bow(p, pal, r, cross=False):
    wood, dark = pal["blade"], pal["dark"]
    hi = shade(wood, 1.25)
    if not cross:
        # arc from bottom-left to top-right
        for t in range(14):
            a = t / 13 * math.pi - math.pi / 2
            x = 8 + round(math.sin(a) * 6.5)
            y = 8 - round(math.cos(a) * 6.5)
            p.px(x, y, wood)
            p.px(x - 1, y, hi if 3 < t < 10 else wood)
        # string
        p.line(8 + round(math.sin(-math.pi / 2) * 6.5), 8 - round(math.cos(-math.pi / 2) * 6.5),
               8 + round(math.sin(math.pi / 2) * 6.5), 8 - round(math.cos(math.pi / 2) * 6.5),
               (225, 220, 200, 255))
        # arrow
        for t in range(3, 12):
            p.px(t, 15 - t, (150, 120, 80, 255))
        p.px(12, 3, (200, 205, 215, 255))
        p.px(13, 2, (230, 235, 245, 255))
        p.px(3, 12, (210, 60, 50, 255))
        p.px(4, 12, (210, 60, 50, 255))
    else:
        # crossbow: stock diagonal, bow perpendicular
        for t in range(2, 13):
            diag(p, t, shade((96, 72, 48, 255), 0.95 if t % 2 else 0.85), 2)
        for s in range(-5, 6):
            x = 9 + s
            y = 6 + s
            if abs(s) > 1:
                p.px(x, y - abs(s) // 2, wood if abs(s) < 4 else dark)
        p.line(4, 9, 14, 0, (225, 220, 200, 255))
        p.px(2, p.h - 2, (60, 50, 40, 255))
        # bolt
        p.px(12, 3, (200, 205, 215, 255))
        p.px(13, 2, (235, 240, 248, 255))


def paint_stick(p, pal, r):
    wood = (134, 100, 60, 255)
    for t in range(2, 13):
        diag(p, t, shade(wood, 0.9 + (t % 3) * 0.08), 1)
    p.px(6, 8, shade(wood, 1.2))
    p.px(10, 4, shade(wood, 0.7))
    p.px(12, 3, shade(wood, 1.1))
    p.px(4, 12, shade(wood, 0.75))


# ---------------------------------------------------------------------------
# Legendary weapon painters — bespoke 32px art per weapon, faithful to Fable
# ---------------------------------------------------------------------------

def _grip32(p, t0, t1, color, pommel=(250, 210, 90, 255)):
    """Wrapped grip + pommel along the diagonal (32px canvas)."""
    for t in range(t0, t1):
        x, y = t, p.h - 1 - t
        p.px(x, y, shade(color, 1.1 if t % 2 else 0.8))
        p.px(x + 1, y, shade(color, 1.3))
        p.px(x, y + 1, shade(color, 0.55))
    p.disc(t0 - 1, p.h - t0, 1.5, pommel)
    p.px(t0 - 2, p.h - t0 - 1, shade(pommel, 1.35))


def paint_sword_of_aeons(p, r):
    """Fable's final blade: near-black steel, molten glowing core,
    swept bat-wing guard, heat shimmer along the edge."""
    body = (54, 44, 60, 255)
    edge = (140, 126, 152, 255)
    core = (255, 120, 40, 255)
    core_hi = (255, 215, 95, 255)
    _grip32(p, 3, 9, (44, 30, 36, 255), pommel=(150, 34, 30, 255))
    g = (96, 74, 106, 255)
    gh = shade(g, 1.35)
    for o in range(-4, 5):
        x = 11 + o
        y = p.h - 11 + (-o)
        p.px(x, y, g if o % 2 == 0 else gh)
        p.px(x + 1, y, shade(g, 0.7))
    # upswept prongs hugging the blade root
    p.px(7, p.h - 16, g)
    p.px(8, p.h - 17, gh)
    p.px(8, p.h - 16, shade(g, 0.8))
    p.px(16, p.h - 7, g)
    p.px(17, p.h - 8, gh)
    p.px(16, p.h - 8, shade(g, 0.8))
    # broad black blade w/ molten centre line
    for t in range(12, 30):
        x, y = t, p.h - 1 - t
        p.px(x - 1, y + 1, body)
        p.px(x, y + 1, body)
        p.px(x + 1, y - 1, body)
        p.px(x, y, core if t % 2 == 0 else core_hi)
        p.px(x + 2, y - 1, edge)
        p.px(x - 1, y + 2, edge)
        if t % 5 == 2:
            p.px(x + 1, y - 2, with_alpha(core_hi, 150))
    p.px(30, 1, edge)
    p.px(30, 0, core_hi)
    p.px(31, 0, (255, 255, 255, 235))
    p.glow((255, 90, 30), 58)


def paint_avos_tear(p, r):
    """Avo's Tear: radiant silver blade, sapphire core, gull-wing gold guard."""
    body = (214, 226, 240, 255)
    edge = (245, 250, 255, 255)
    core = (90, 160, 255, 255)
    core_hi = (180, 225, 255, 255)
    _grip32(p, 3, 9, (70, 86, 130, 255), pommel=(140, 200, 255, 255))
    g = (236, 196, 96, 255)
    for o in range(-4, 5):
        x = 11 + o
        y = p.h - 11 + (-o)
        p.px(x, y, g if o % 2 == 0 else shade(g, 1.2))
        p.px(x + 1, y, shade(g, 0.75))
    # wings flaring outward (gull-wing)
    p.px(6, p.h - 14, g)
    p.px(5, p.h - 15, shade(g, 1.25))
    p.px(14, p.h - 6, g)
    p.px(15, p.h - 5, shade(g, 1.25))
    for t in range(12, 30):
        x, y = t, p.h - 1 - t
        p.px(x - 1, y + 1, body)
        p.px(x, y + 1, body)
        p.px(x + 1, y - 1, body)
        p.px(x, y, core if t % 2 == 0 else core_hi)
        p.px(x + 2, y - 1, edge)
        p.px(x - 1, y + 2, edge)
        if t % 4 == 1 and t < 27:
            p.px(x + 1, y - 2, (255, 255, 255, 190))  # holy runes
    p.px(30, 1, edge)
    p.px(30, 0, (255, 255, 255, 250))
    p.glow((150, 210, 255), 55)


def paint_harbinger(p, r):
    """The Harbinger: immense flat slab of pale steel, squared tip,
    ancient runes etched down the fuller."""
    body = (196, 200, 208, 255)
    edge = (235, 238, 244, 255)
    dk = (130, 134, 146, 255)
    rune = (110, 190, 200, 255)
    _grip32(p, 2, 8, (74, 58, 44, 255), pommel=(180, 184, 196, 255))
    g = (150, 154, 166, 255)
    for o in range(-4, 5):
        x = 10 + o
        y = p.h - 10 + (-o)
        p.px(x, y, g if o % 2 == 0 else shade(g, 1.15))
        p.px(x + 1, y, shade(g, 0.7))
    # extra-wide slab blade (5px across)
    for t in range(11, 29):
        x, y = t, p.h - 1 - t
        p.px(x - 2, y + 2, dk)
        p.px(x - 1, y + 1, body)
        p.px(x, y + 1, body)
        p.px(x, y, body)
        p.px(x + 1, y - 1, body)
        p.px(x + 1, y, body)
        p.px(x + 2, y - 1, edge)
        p.px(x - 1, y + 2, edge)
        if t % 3 == 0 and 13 < t < 27:
            p.px(x, y, rune)  # rune chain down the fuller
    # squared-off tip (the Harbinger has no point)
    for o in range(3):
        p.px(29 + (1 if o < 2 else 0), 2 - o if 2 - o >= 0 else 0, edge)
    p.px(29, 1, body)
    p.px(30, 1, edge)
    p.px(30, 2, dk)
    p.glow((140, 200, 210), 30)


def paint_solus(p, r):
    """Solus Greatsword: the brightest blade in Albion — white-gold steel,
    sun-disc guard, dawn radiance."""
    body = (244, 226, 170, 255)
    edge = (255, 248, 215, 255)
    dk = (190, 160, 96, 255)
    _grip32(p, 3, 9, (120, 70, 40, 255), pommel=(255, 230, 130, 255))
    # SUN DISC guard
    gx, gy = 11, p.h - 12
    for dx in range(-3, 4):
        for dy in range(-3, 4):
            d = math.hypot(dx, dy)
            if d <= 2.6:
                p.px(gx + dx, gy + dy, (255, 215, 105, 255) if d > 1.4 else (255, 240, 170, 255))
    for a in range(0, 360, 45):  # rays
        x = gx + round(math.cos(math.radians(a)) * 4)
        y = gy + round(math.sin(math.radians(a)) * 4)
        p.px(x, y, (255, 200, 80, 255))
    for t in range(13, 30):
        x, y = t, p.h - 1 - t
        p.px(x - 1, y + 1, dk)
        p.px(x, y, body)
        p.px(x, y + 1, body)
        p.px(x + 1, y - 1, body)
        p.px(x + 2, y - 1, edge)
        p.px(x - 1, y + 2, edge)
        if t % 4 == 2:
            p.px(x + 1, y - 2, (255, 255, 230, 200))
    p.px(30, 1, edge)
    p.px(30, 0, (255, 255, 255, 245))
    p.glow((255, 190, 70), 60)


def paint_bereaver(p, r):
    """The Bereaver: black jagged executioner's greatsword, gold serrated
    spine, grave-green witchfire."""
    body = (44, 42, 52, 255)
    edge = (110, 108, 126, 255)
    gold = (212, 172, 84, 255)
    fire = (140, 230, 150, 255)
    _grip32(p, 3, 9, (36, 30, 34, 255), pommel=(212, 172, 84, 255))
    g = (80, 76, 92, 255)
    for o in range(-4, 5):
        x = 11 + o
        y = p.h - 11 + (-o)
        p.px(x, y, g if o % 2 == 0 else gold)
        p.px(x + 1, y, shade(g, 0.7))
    for t in range(12, 30):
        x, y = t, p.h - 1 - t
        p.px(x - 1, y + 1, body)
        p.px(x, y, body)
        p.px(x, y + 1, body)
        p.px(x + 1, y - 1, body)
        p.px(x + 2, y - 1, edge)
        # jagged saw-teeth along the back edge
        if t % 3 == 0:
            p.px(x - 2, y + 2, gold)
            p.px(x - 2, y + 3, shade(gold, 0.7))
        else:
            p.px(x - 1, y + 2, edge)
        if t % 5 == 1 and t < 27:
            p.px(x + 1, y - 2, with_alpha(fire, 180))  # witchfire wisps
    p.px(30, 1, edge)
    p.px(30, 0, fire)
    p.glow((120, 220, 140), 42)


def paint_skorms_bow(p, r):
    """Skorm's Bow: obsidian-black demonic recurve, molten red veins,
    spiked limb tips."""
    wood = (40, 32, 40, 255)
    woodh = (78, 62, 78, 255)
    vein = (235, 70, 40, 255)
    veinh = (255, 150, 70, 255)
    # recurve arc with flared spiked tips
    pts = []
    for t in range(15):
        a = t / 14 * math.pi - math.pi / 2
        x = 15 + round(math.sin(a) * 12)
        y = 16 - round(math.cos(a) * 12)
        pts.append((x, y))
    for i, (x, y) in enumerate(pts):
        p.px(x, y, wood)
        p.px(x - 1, y, woodh)
        p.px(x - 2, y, wood if i % 3 else shade(wood, 0.7))
        if i % 2 == 0:
            p.px(x - 1, y, vein if i % 4 == 0 else veinh)  # molten veins
    # spiked recurve tips
    x0, y0 = pts[0]
    x1, y1 = pts[-1]
    p.px(x0 - 2, y0 - 1, wood)
    p.px(x0 - 3, y0 - 2, vein)
    p.px(x1 - 2, y1 + 1, wood)
    p.px(x1 - 3, y1 + 2, vein)
    # bowstring (sinew)
    p.line(x0, y0, x1, y1, (190, 170, 150, 235))
    # nocked arrow w/ red head
    for t in range(7, 24):
        p.px(t, 31 - t, (96, 72, 48, 255))
    p.px(24, 7, vein)
    p.px(25, 6, veinh)
    p.px(26, 5, (255, 230, 150, 255))
    p.px(7, 24, (150, 40, 40, 255))
    p.px(8, 24, (150, 40, 40, 255))
    p.px(7, 23, (150, 40, 40, 255))
    # demonic eye at the grip
    p.px(15, 16, (255, 220, 90, 255))
    p.px(15, 17, (120, 20, 20, 255))
    p.glow((255, 70, 30), 52)


def paint_arkens_crossbow(p, r):
    """Arken's Crossbow: shipwright's masterpiece — dark lacquered stock,
    blued-steel bow, brass fittings."""
    stock = (74, 50, 34, 255)
    stockh = (110, 78, 52, 255)
    steel = (120, 140, 170, 255)
    steelh = (180, 200, 226, 255)
    brass = (212, 172, 84, 255)
    # heavy stock along diagonal
    for t in range(4, 26):
        x, y = t, p.h - 1 - t
        p.px(x, y, stock if t % 3 else stockh)
        p.px(x + 1, y, stockh)
        p.px(x, y + 1, shade(stock, 0.6))
    # shoulder plate
    p.rect(3, p.h - 6, 3, 4, shade(stock, 0.8))
    p.px(3, p.h - 6, brass)
    # blued-steel bow perpendicular at the front
    for s in range(-7, 8):
        x = 21 + s
        y = 10 + s
        curve = abs(s) // 3
        if abs(s) > 1:
            p.px(x, y - 4 - curve, steel if abs(s) < 6 else steelh)
            p.px(x, y - 5 - curve, shade(steel, 0.7))
    # string + trigger + brass cranequin wheel
    p.line(14, 13, 28, 0, (220, 214, 196, 235))
    p.disc(13, p.h - 14, 1.6, brass)
    p.px(13, p.h - 14, shade(brass, 1.3))
    p.px(12, p.h - 11, steel)  # trigger
    p.px(12, p.h - 10, steel)
    # bolt
    for t in range(16, 27):
        p.px(t, p.h - 4 - t, (180, 186, 198, 255))
    p.px(27, 1, steelh)
    p.px(28, 0, (240, 246, 255, 245))
    p.glow((140, 180, 255), 30)


def paint_katana_legend(p, r, hiryu=False):
    """Avenger / Katana Hiryu: folded steel, long curve, silk-wrapped tsuka.
    Hiryu gets a dragon-blue blade and red silk."""
    blade = (170, 200, 235, 255) if hiryu else (215, 222, 232, 255)
    bladeh = (230, 245, 255, 255) if hiryu else (248, 250, 255, 255)
    hamon = (130, 160, 200, 255) if hiryu else (170, 178, 195, 255)
    silk1 = (160, 30, 36, 255) if hiryu else (30, 30, 40, 255)
    silk2 = (220, 70, 60, 255) if hiryu else (90, 90, 110, 255)
    # tsuka with diamond silk wrap
    for t in range(2, 9):
        x, y = t, p.h - 1 - t
        p.px(x, y, silk1 if t % 2 else silk2)
        p.px(x + 1, y, silk2 if t % 2 else silk1)
    p.px(1, p.h - 2, (212, 172, 84, 255))  # kashira cap
    # round gold tsuba
    p.disc(10, p.h - 11, 1.8, (212, 172, 84, 255))
    p.px(10, p.h - 11, (250, 220, 130, 255))
    # long curved blade
    for t in range(11, 30):
        arc = round(math.sin((t - 11) / 19 * math.pi * 0.5) * 3)
        x, y = t, p.h - 1 - t - arc
        p.px(x, y, blade)
        p.px(x, y - 1, bladeh)
        p.px(x - 1, y + 1, hamon)  # hamon temper-line
        if hiryu and t % 5 == 2:
            p.px(x + 1, y - 2, (120, 200, 255, 190))  # dragon-breath shimmer
    p.px(30, 0, bladeh)
    p.px(31, 0, (255, 255, 255, 240))
    p.glow((140, 190, 255) if hiryu else (220, 230, 255), 36 if hiryu else 26)


def paint_orkons_club(p, r):
    """Orkon's Club: brutal knotted greatclub, iron bands, embedded spikes."""
    wood = (104, 74, 44, 255)
    woodd = (70, 48, 30, 255)
    iron = (130, 132, 142, 255)
    spike = (200, 204, 214, 255)
    # tapering haft thickening into the head
    for t in range(3, 27):
        x, y = t, p.h - 1 - t
        w = 1 + (t - 3) // 8  # grows thicker toward the tip
        for o in range(w + 1):
            p.px(x - o, y + o if o else y, shade(wood, 1.0 - o * 0.12) if (t + o) % 4 else woodd)
        p.px(x + 1, y - 1, shade(wood, 1.25))
    # grip wrap
    for t in range(3, 8):
        p.px(t, p.h - 1 - t, (60, 44, 32, 255) if t % 2 else (84, 60, 40, 255))
    p.px(2, p.h - 2, woodd)
    # iron bands around the head
    for bt in (18, 23):
        for o in range(-1, 3):
            p.px(bt - o, p.h - 1 - bt - 1 + o, iron)
            p.px(bt - o + 1, p.h - 1 - bt - 1 + o, shade(iron, 1.25))
    # embedded spikes
    for sx, sy in ((20, 8), (24, 5), (22, 4), (26, 8)):
        p.px(sx, sy, spike)
        p.px(sx + 1, sy - 1, (255, 255, 255, 220))
    # knots
    p.px(12, p.h - 13, woodd)
    p.px(16, p.h - 18, woodd)
    p.glow((255, 150, 60), 22)


def paint_dollmasters_mace(p, r):
    """Dollmaster's Mace: a porcelain doll's head atop a black iron haft.
    It is exactly as unsettling as it sounds."""
    iron = (54, 50, 60, 255)
    ironh = (96, 90, 104, 255)
    skin = (236, 220, 204, 255)
    skind = (200, 178, 160, 255)
    # haft
    for t in range(3, 21):
        x, y = t, p.h - 1 - t
        p.px(x, y, iron if t % 3 else ironh)
        p.px(x + 1, y, ironh)
    p.disc(2, p.h - 3, 1.4, (140, 90, 200, 255))  # amethyst pommel
    # collar
    p.px(20, 10, (212, 172, 84, 255))
    p.px(21, 9, (212, 172, 84, 255))
    p.px(20, 9, (250, 220, 130, 255))
    # PORCELAIN DOLL HEAD
    cx, cy = 24, 6
    for dx in range(-4, 5):
        for dy in range(-4, 5):
            d = math.hypot(dx, dy)
            if d <= 3.8:
                p.px(cx + dx, cy + dy, skin if d < 3 else skind)
    p.px(cx - 3, cy - 3, (255, 250, 245, 255))  # glaze shine
    p.px(cx - 2, cy - 4, (255, 250, 245, 255))
    # painted hair
    for dx in range(-4, 5):
        if abs(dx) < 4:
            p.px(cx + dx, cy - 4, (80, 50, 36, 255))
        if abs(dx) < 3:
            p.px(cx + dx, cy - 5, (96, 62, 44, 255))
    # dead glass eyes + painted smile + crack
    p.px(cx - 2, cy - 1, (30, 50, 90, 255))
    p.px(cx + 2, cy - 1, (30, 50, 90, 255))
    p.px(cx - 2, cy - 2, (250, 250, 250, 255))
    p.px(cx + 2, cy - 2, (250, 250, 250, 255))
    p.px(cx - 1, cy + 2, (170, 80, 90, 255))
    p.px(cx, cy + 2, (190, 90, 100, 255))
    p.px(cx + 1, cy + 2, (170, 80, 90, 255))
    # the crack
    p.px(cx + 3, cy - 3, skind)
    p.px(cx + 3, cy - 2, (150, 130, 115, 255))
    p.px(cx + 4, cy - 1, (150, 130, 115, 255))
    p.glow((180, 140, 255), 34)


def paint_wellows_pickhammer(p, r):
    """Wellow's Pickhammer: dwarf-forged mining maul — hammer face one side,
    pick spike the other, brass-bound oak haft."""
    steel = (168, 174, 188, 255)
    steelh = (215, 222, 236, 255)
    steeld = (110, 114, 128, 255)
    oak = (134, 96, 56, 255)
    brass = (212, 172, 84, 255)
    # haft
    for t in range(3, 22):
        x, y = t, p.h - 1 - t
        p.px(x, y, oak if t % 3 else shade(oak, 0.8))
        p.px(x + 1, y, shade(oak, 1.2))
    # brass bands
    for bt in (8, 14):
        p.px(bt, p.h - 1 - bt, brass)
        p.px(bt + 1, p.h - 1 - bt, shade(brass, 1.25))
        p.px(bt, p.h - bt, shade(brass, 0.7))
    p.px(2, p.h - 3, brass)
    # head: hammer block upper-left of axis
    hx, hy = 22, 8
    for dx in range(-2, 4):
        for dy in range(-4, 2):
            p.px(hx + dx, hy + dy, steel if (dx + dy) % 2 else shade(steel, 0.92))
    for dy in range(-4, 2):
        p.px(hx + 4, hy + dy, steelh)   # striking face
        p.px(hx - 3, hy + dy, steeld)
    p.px(hx + 4, hy - 4, (255, 255, 255, 230))
    # pick spike sweeping down-left
    for i in range(6):
        px_ = hx - 4 - i
        py_ = hy - 1 + i // 2
        p.px(px_, py_, steeld if i > 3 else steel)
        if i < 4:
            p.px(px_, py_ + 1, steel)
    p.px(hx - 10, hy + 2, steelh)  # spike tip glint
    # engraved guild rune on hammer cheek
    p.px(hx, hy - 2, (120, 230, 160, 255))
    p.px(hx + 1, hy - 1, (120, 230, 160, 255))
    p.px(hx, hy, (120, 230, 160, 255))
    p.glow((120, 230, 160), 30)


def paint_coin(p, pal, r):
    c = (250, 210, 90, 255)
    p.disc(8, 8, 5.2, c)
    p.disc(8, 8, 5.2, c)
    for a in range(0, 360, 30):
        x = 8 + round(math.cos(math.radians(a)) * 5)
        y = 8 + round(math.sin(math.radians(a)) * 5)
        p.px(x, y, shade(c, 0.75))
    p.disc(7, 7, 2.0, shade(c, 1.2))
    # crown emboss
    p.px(7, 8, shade(c, 0.6))
    p.px(8, 7, shade(c, 0.6))
    p.px(9, 8, shade(c, 0.6))
    p.px(8, 9, shade(c, 0.6))
    p.px(11, 11, shade(c, 0.55))


def paint_key(p, color, ornate=False):
    c = color + (255,)
    hi = shade(c, 1.3)
    dk = shade(c, 0.6)
    # bow (ring)
    p.disc(4, 4, 2.8, c)
    p.disc(4, 4, 1.2, (0, 0, 0, 0))
    p.px(2, 2, hi)
    if ornate:
        p.px(1, 4, dk)
        p.px(7, 4, dk)
        p.px(4, 1, dk)
        p.px(4, 7, dk)
    # shaft
    for t in range(6, 13):
        p.px(t, t, c)
        p.px(t + 1, t, hi if t % 2 else c)
    # teeth
    p.px(12, 13, c)
    p.px(13, 13, c)
    p.px(11, 14, c)
    p.px(13, 11, dk)


def paint_flask(p, color, large=False):
    glass = (200, 220, 235, 160)
    liquid = color + (235,)
    hi = (255, 255, 255, 120)
    cy = 9 if not large else 8
    rr = 4 if not large else 5
    # body
    p.disc(8, cy, rr, glass)
    for y in range(cy - 1, cy + rr):
        for x in range(8 - rr, 8 + rr + 1):
            if (x - 8) ** 2 + (y - cy) ** 2 <= rr * rr:
                p.px(x, y, liquid)
    # neck + cork
    p.rect(7, cy - rr - 3, 3, 3, glass)
    p.rect(7, cy - rr - 4, 3, 2, (150, 110, 70, 255))
    p.px(8 - rr + 1, cy - 1, hi)
    p.px(8 - rr + 1, cy, hi)
    p.disc(8, cy - 1, 1, with_alpha(shade(liquid, 1.5), 200))


def paint_phial(p, color):
    glass = (215, 230, 245, 150)
    liquid = color + (240,)
    dk = shade(liquid, 0.55)
    hi = shade(liquid, 1.4)
    p.rect(6, 5, 5, 9, glass)
    p.rect(7, 6, 3, 7, liquid)
    p.rect(7, 11, 3, 2, dk)
    p.px(7, 6, hi)
    p.px(7, 7, (255, 255, 255, 170))
    p.px(9, 9, dk)
    p.rect(7, 3, 3, 2, glass)
    p.rect(7, 2, 3, 1, (250, 210, 90, 255))
    p.px(6, 5, shade((215, 230, 245, 255), 0.7))
    p.px(10, 13, shade((215, 230, 245, 255), 0.6))
    p.glow(color, 22)


def paint_tome(p, color, r):
    cover = color + (255,)
    hi = shade(cover, 1.3)
    dk = shade(cover, 0.55)
    p.rect(3, 2, 10, 12, cover)
    p.rect(3, 2, 2, 12, dk)         # spine
    p.rect_outline(3, 2, 10, 12, dk)
    p.rect(12, 3, 1, 10, (235, 228, 200, 255))  # pages
    # rune emblem
    cx, cy = 8, 8
    p.px(cx, cy - 2, hi)
    p.px(cx - 1, cy - 1, hi)
    p.px(cx + 1, cy - 1, hi)
    p.px(cx, cy, hi)
    p.px(cx, cy + 1, hi)
    p.px(cx - 1, cy + 2, hi)
    p.px(cx + 1, cy + 2, hi)
    p.glow(color, 45)


def paint_augment(p, color, r):
    """Augment = faceted gem rune-stone."""
    c = color + (255,)
    hi = shade(c, 1.45)
    dk = shade(c, 0.5)
    pts = [(8, 2), (13, 6), (11, 13), (5, 13), (3, 6)]
    # fill polygon (scanline-ish, small enough to brute force)
    for y in range(2, 14):
        for x in range(3, 14):
            # inside check via winding of pentagon approx with circle blend
            d = math.hypot(x - 8, y - 8)
            if d < 5.4 - (1.2 if y < 5 else 0):
                p.px(x, y, c)
    for (x0, y0), (x1, y1) in zip(pts, pts[1:] + pts[:1]):
        p.line(x0, y0, x1, y1, dk)
    p.line(8, 2, 8, 8, hi)
    p.line(3, 6, 8, 8, hi)
    p.line(13, 6, 8, 8, shade(c, 0.8))
    p.px(8, 8, hi)
    p.px(7, 5, hi)
    p.glow(color, 50)


def paint_card(p, r):
    parch = (214, 196, 158, 255)
    dk = (150, 128, 92, 255)
    sealc = (170, 40, 40, 255)
    p.rect(2, 1, 12, 14, parch)
    p.rect_outline(2, 1, 12, 14, dk)
    for y in (4, 6, 8):
        p.line(4, y, 11, y, shade(dk, 1.15))
    p.disc(10, 12, 1.6, sealc)
    p.px(10, 12, shade(sealc, 1.4))
    p.px(3, 2, shade(parch, 1.1))


def paint_seal(p, r):
    c = (90, 140, 230, 255)
    g = (250, 210, 90, 255)
    p.disc(8, 8, 6, g)
    for a in range(0, 360, 24):
        x = 8 + round(math.cos(math.radians(a)) * 5.6)
        y = 8 + round(math.sin(math.radians(a)) * 5.6)
        p.px(x, y, shade(g, 0.7))
    p.disc(8, 8, 4.6, c)
    p.disc(7, 7, 2.0, shade(c, 1.25))
    p.px(11, 11, shade(c, 0.6))
    p.px(10, 12, shade(c, 0.6))
    # guild "G" sigil
    p.px(7, 6, g)
    p.px(6, 7, g)
    p.px(6, 8, g)
    p.px(7, 9, g)
    p.px(8, 9, g)
    p.px(9, 9, g)
    p.px(9, 8, g)
    p.px(8, 8, g)
    p.px(5, 5, (255, 255, 255, 180))
    p.glow((120, 170, 255), 30)


def paint_ring(p, r):
    g = (250, 220, 120, 255)
    p.disc(8, 9, 4.4, g)
    p.disc(8, 9, 2.6, (0, 0, 0, 0))
    p.px(5, 7, shade(g, 1.3))
    p.disc(8, 4, 1.5, (220, 240, 255, 255))
    p.px(8, 3, (255, 255, 255, 255))


def paint_fang(p, color, r):
    c = color + (255,)
    hi = shade(c, 1.3)
    dk = shade(c, 0.6)
    for i in range(9):
        w = max(1, 3 - i // 3)
        x = 4 + i
        y = 3 + i
        for o in range(w):
            col = hi if o == 0 and i > 4 else (c if o == 0 else (dk if o == w - 1 else shade(c, 0.85)))
            p.px(x - o, y, col)
    p.px(12, 11, hi)
    p.px(13, 12, (255, 255, 255, 220))
    p.px(4, 3, dk)
    p.px(5, 3, shade(c, 0.75))
    p.px(3, 4, dk)


def paint_wing(p, color, r):
    c = color + (210,)
    vein = shade(color + (255,), 0.7)
    for t in range(11):
        a = t / 10
        x0 = 2 + t
        y0 = 12 - round(math.sin(a * math.pi) * 7)
        h = max(1, round(math.sin(a * math.pi) * 6))
        for y in range(y0, min(14, y0 + h)):
            p.px(x0, y, c)
    p.line(2, 12, 12, 5, vein)
    p.line(2, 12, 10, 8, vein)


def paint_goo(p, color, r):
    c = color + (230,)
    dk = shade(c, 0.55)
    hi = shade(c, 1.45)
    p.disc(8, 10, 4.5, c)
    p.disc(5, 8, 2.5, c)
    p.disc(11, 8, 2.2, c)
    p.disc(8, 6, 2.2, c)
    # bottom shadow band
    for x in range(4, 13):
        p.px(x, 13, dk)
        if r.random() < 0.6:
            p.px(x, 12, shade(c, 0.75))
    p.px(6, 8, hi)
    p.px(7, 9, hi)
    p.px(8, 5, hi)
    p.px(5, 7, (255, 255, 255, 160))
    p.px(11, 10, dk)
    p.px(10, 7, shade(c, 0.8))
    p.disc(11, 5, 1.0, with_alpha(c, 180))
    p.glow(color, 18)


def paint_heart(p, color, r):
    c = color + (255,)
    dk = shade(c, 0.55)
    hi = shade(c, 1.35)
    p.disc(6, 6, 2.6, c)
    p.disc(10, 6, 2.6, c)
    for y in range(6, 14):
        half = max(0, 6 - (y - 6))
        for x in range(8 - half, 8 + half + 1):
            p.px(x, y, c if y < 10 else shade(c, 0.8))
    p.px(5, 5, hi)
    p.px(4, 6, hi)
    p.px(6, 4, (255, 255, 255, 150))
    p.px(8, 8, dk)
    p.line(8, 8, 8, 11, dk)
    p.px(10, 9, shade(c, 0.7))
    p.px(11, 7, shade(c, 0.7))
    # ventricle tubes
    p.px(6, 3, dk)
    p.px(10, 3, dk)
    p.px(7, 2, shade(dk, 1.3))


def paint_bones(p, color, r):
    c = color + (255,)
    dk = shade(c, 0.7)
    p.line(4, 11, 11, 4, c, 2)
    for cx, cy in ((3, 12), (5, 12), (3, 10)):
        p.disc(cx, cy, 1.2, c)
    for cx, cy in ((12, 3), (10, 3), (12, 5)):
        p.disc(cx, cy, 1.2, c)
    p.px(7, 8, dk)
    p.px(8, 7, shade(c, 1.2))


def paint_stinger(p, color, r):
    c = color + (255,)
    hi = shade(c, 1.35)
    dk = shade(c, 0.6)
    # broad curved stinger filling the canvas
    for i in range(12):
        w = max(1, 4 - i // 3)
        x = 2 + i
        y = 14 - i
        for o in range(w):
            col = hi if o == 0 else (c if o < w - 1 else dk)
            p.px(x, y - o, col)
    p.px(13, 3, hi)
    p.px(14, 2, (255, 255, 255, 230))
    # venom sac base
    p.disc(4, 12, 2.6, shade(c, 0.8))
    p.disc(3, 11, 1.4, c)
    p.px(3, 11, hi)
    p.px(5, 13, dk)
    p.glow(color, 26)


def paint_trophy(p, color, r):
    base = (120, 84, 50, 255)
    c = color + (255,)
    p.rect(3, 12, 10, 3, base)
    p.rect(4, 11, 8, 1, shade(base, 1.2))
    # mounted balverine head silhouette
    p.disc(8, 7, 3.2, c)
    p.px(5, 4, c)
    p.px(6, 3, c)
    p.px(10, 3, c)
    p.px(11, 4, c)
    p.rect(7, 9, 3, 2, shade(c, 0.85))
    p.px(7, 6, (200, 40, 40, 255))
    p.px(10, 6, (200, 40, 40, 255))


def paint_mask(p, color, r):
    c = color + (255,)
    dk = shade(c, 0.55)
    hi = shade(c, 1.3)
    for y in range(3, 14):
        w = 5 if y < 8 else max(1, 5 - (y - 8))
        for x in range(8 - w, 8 + w + 1):
            p.px(x, y, c)
    # horns
    p.px(3, 3, dk)
    p.px(2, 2, dk)
    p.px(13, 3, dk)
    p.px(14, 2, dk)
    # eyes — judging slits
    p.rect(5, 6, 2, 1, (20, 16, 14, 255))
    p.rect(9, 6, 2, 1, (20, 16, 14, 255))
    p.px(5, 6, (255, 230, 140, 255))
    p.px(10, 6, (255, 230, 140, 255))
    p.line(8, 8, 8, 11, dk)
    p.px(7, 4, hi)
    p.glow((255, 100, 40), 35)


def paint_book(p, color, r):
    paint_tome(p, color, r)


def paint_food(p, item, r):
    color = item["color"]
    c = color + (255,)
    kind = item["kind"]
    if kind == "pie":
        crust = (190, 140, 80, 255)
        p.disc(8, 9, 5.5, crust)
        p.disc(8, 9, 4.2, c)
        for a in range(0, 360, 45):
            x = 8 + round(math.cos(math.radians(a)) * 5.2)
            y = 9 + round(math.sin(math.radians(a)) * 5.2)
            p.px(x, y, shade(crust, 0.75))
        p.px(6, 7, shade(c, 1.3))
        p.px(9, 10, shade(c, 0.8))
    elif kind == "tankard":
        wood = (130, 92, 54, 255)
        p.rect(5, 4, 6, 9, wood)
        p.rect(5, 4, 6, 2, (240, 234, 210, 255))  # foam
        p.px(4, 3, (240, 234, 210, 255))
        p.px(8, 3, (240, 234, 210, 255))
        p.rect(11, 6, 2, 5, shade(wood, 0.8))
        p.rect(12, 7, 1, 3, (0, 0, 0, 0))
        p.line(5, 7, 10, 7, shade(wood, 0.85))
    elif kind == "food" and item["id"] == "crunchy_chick":
        body = (240, 220, 90, 255)
        p.disc(8, 9, 3.4, body)
        p.disc(8, 5, 2.2, body)
        p.px(6, 4, (30, 26, 22, 255))   # eye
        p.px(9, 5, (250, 150, 50, 255))  # beak
        p.px(10, 5, (250, 150, 50, 255))
        p.px(6, 13, (250, 150, 50, 255))
        p.px(9, 13, (250, 150, 50, 255))
        p.px(5, 9, shade(body, 0.8))
    elif kind == "food" and item["id"] == "tofu":
        p.rect(4, 6, 9, 6, c)
        p.rect(4, 6, 9, 2, shade(c, 1.1))
        p.rect_outline(4, 6, 9, 6, shade(c, 0.75))
        p.px(6, 8, shade(c, 0.85))
        p.px(10, 9, shade(c, 0.85))
    else:  # red meat
        p.disc(8, 8, 4.5, c)
        p.disc(7, 8, 4.0, shade(c, 1.1))
        p.disc(7, 7, 1.6, (240, 230, 220, 255))
        p.px(11, 10, shade(c, 0.7))
        bone = (235, 230, 215, 255)
        p.rect(12, 4, 2, 2, bone)


KIND_PAINTERS = {}

LEGEND_PAINTERS = {
    "sword_of_aeons": paint_sword_of_aeons,
    "avos_tear": paint_avos_tear,
    "the_harbinger": paint_harbinger,
    "solus_greatsword": paint_solus,
    "the_bereaver": paint_bereaver,
    "the_avenger_bow": paint_skorms_bow,
    "arkens_crossbow": paint_arkens_crossbow,
    "avenger": lambda p, r: paint_katana_legend(p, r, hiryu=False),
    "katana_hiryu": lambda p, r: paint_katana_legend(p, r, hiryu=True),
    "orkons_club": paint_orkons_club,
    "dollmasters_mace": paint_dollmasters_mace,
    "wellows_pickhammer": paint_wellows_pickhammer,
}


def paint_weapon_icon(item):
    kind = item["kind"]
    mat = item.get("material", "iron")
    pal = MAT_PAL.get(mat, MAT_PAL["iron"])
    r = rng("item", item["id"])
    # bespoke legendary art first
    if item["id"] in LEGEND_PAINTERS:
        p = Px(32, 32)
        LEGEND_PAINTERS[item["id"]](p, r)
        p.outline(DARKLINE)
        p.save(OUT / f"{item['id']}.png")
        return 32
    p = Px(16, 16)
    if kind == "sword":
        paint_sword(p, pal, r)
    elif kind == "katana":
        paint_katana(p, pal, r)
    elif kind == "scimitar":
        paint_sword(p, pal, r, length=10, curved=True)
    elif kind == "cleaver":
        paint_cleaver(p, pal, r)
    elif kind == "axe":
        paint_axe(p, pal, r)
    elif kind == "greataxe":
        paint_axe(p, pal, r, double=True)
    elif kind == "mace":
        paint_mace(p, pal, r)
    elif kind == "pickhammer":
        paint_hammer(p, pal, r, pick=True)
    elif kind == "greathammer":
        paint_hammer(p, pal, r)
    elif kind == "greatsword":
        paint_greatsword(p, pal, r)
    elif kind == "bow":
        paint_bow(p, pal, r)
    elif kind == "crossbow":
        paint_bow(p, pal, r, cross=True)
    elif kind == "stick":
        paint_stick(p, pal, r)
    else:
        paint_sword(p, pal, r)
    p.outline(DARKLINE)
    p.save(OUT / f"{item['id']}.png")
    return p.w


# ---------------------------------------------------------------------------
# Armor icons
# ---------------------------------------------------------------------------

def paint_armor_icon(item):
    p = Px(16, 16)
    pal = item["palette"]
    base = pal["base"] + (255,)
    trim = pal["trim"] + (255,)
    dark_set = max(pal["base"]) < 110
    hi = mix(base, (255, 255, 255), 0.4) if dark_set else shade(base, 1.3)
    dk = shade(base, 0.55)
    mid = shade(base, 0.85)
    r = rng("armor", item["id"])
    slot = item["slot"]
    accent = pal.get("accent")
    accent = accent + (255,) if accent else trim
    if slot == "helm":
        if pal.get("hood"):
            # cloth hood: rounded cowl, deep face shadow, draped shoulder hem
            p.disc(8, 7, 5.4, base)
            p.rect(3, 7, 11, 4, base)
            p.rect(2, 11, 13, 2, mid)           # shoulder drape
            p.rect(2, 11, 13, 1, dk)
            p.disc(8, 8, 3.2, (22, 18, 16, 255))  # face shadow
            p.rect(5, 9, 7, 3, (22, 18, 16, 255))
            p.px(4, 4, hi)
            p.px(5, 3, hi)
            p.px(11, 5, dk)
            # rim stitching in accent colour
            for a in range(0, 180, 30):
                xx = 8 + round(math.cos(math.radians(a)) * 5)
                yy = 7 - round(math.sin(math.radians(a)) * 5)
                p.px(xx, yy, accent)
            p.px(8, 12, accent)  # clasp
        elif item.get("horns"):
            p.px(3, 3, hi)
            p.px(2, 2, dk)
            p.px(12, 3, hi)
            p.px(13, 2, dk)
        if item.get("brim"):
            p.rect(2, 10, 12, 2, base)
            p.rect(2, 10, 12, 1, hi)
            p.rect(5, 3, 6, 7, base)
            p.rect(5, 3, 6, 1, hi)
            p.px(6, 4, hi)
            p.px(9, 8, dk)
            if "wizard" in item["id"]:
                p.px(7, 1, base)
                p.px(8, 1, hi)
                p.px(8, 0, hi)
                p.rect(5, 8, 6, 1, trim)
                p.px(10, 4, trim)  # star stud
        else:
            p.disc(8, 8, 5, base)
            p.rect(3, 8, 11, 4, base)
            p.rect(4, 9, 8, 3, (24, 20, 18, 255))
            p.rect(7, 9, 1, 3, mid)
            p.px(4, 4, hi)
            p.px(5, 3, hi)
            p.px(11, 5, dk)
            p.rect(3, 7, 11, 1, trim)
            p.px(3, 8, trim)
            p.px(13, 8, trim)
    elif slot == "torso":
        p.rect(4, 3, 8, 9, base)
        p.rect(2, 3, 2, 5, mid)
        p.rect(12, 3, 2, 5, mid)
        p.rect(4, 3, 8, 1, trim)
        p.rect(4, 11, 8, 1, trim)
        p.line(8, 4, 8, 11, dk)
        p.px(5, 5, hi)
        p.px(5, 6, hi)
        p.px(6, 4, hi)
        p.px(10, 9, dk)
        p.px(11, 10, dk)
        if pal.get("accent"):
            # diagonal sash in the accent colour
            for i in range(8):
                p.px(4 + i, 3 + i, accent)
                if i < 7:
                    p.px(5 + i, 3 + i, shade(accent, 0.8))
        if pal.get("metal"):
            for yy in range(4, 11, 2):
                p.px(6, yy, hi)
                p.px(10, yy, mid)
            p.px(9, 5, hi)
        else:
            for yy in range(5, 11, 3):
                p.px(9, yy, dk)  # stitches
                p.px(10, yy, mid)
        p.px(7, 3, hi)
    elif slot == "legs":
        p.rect(4, 3, 8, 3, base)
        p.rect(4, 3, 8, 1, trim)
        p.rect(4, 6, 3, 8, base)
        p.rect(9, 6, 3, 8, base)
        p.px(5, 7, hi)
        p.px(5, 8, hi)
        p.px(10, 9, dk)
        p.px(11, 12, dk)
        p.px(4, 13, dk)
        p.px(9, 7, mid)
        p.px(6, 11, mid)
        if pal.get("metal"):
            p.px(5, 10, hi)
            p.px(10, 11, hi)
    else:  # boots
        p.rect(4, 6, 3, 5, base)
        p.rect(9, 6, 3, 5, base)
        p.rect(3, 11, 4, 3, dk)
        p.rect(9, 11, 5, 3, dk)
        p.px(4, 7, hi)
        p.px(9, 7, hi)
        p.px(5, 9, mid)
        p.px(11, 9, mid)
        p.rect(3, 11, 4, 1, trim)
        p.rect(9, 11, 5, 1, trim)
        p.px(3, 13, shade(dk, 0.7))
        p.px(13, 13, shade(dk, 0.7))
    p.outline(DARKLINE)
    p.save(OUT / f"{item['id']}.png")


# ---------------------------------------------------------------------------
# Misc dispatch
# ---------------------------------------------------------------------------

def paint_misc(item):
    p = Px(16, 16)
    r = rng("item", item["id"])
    kind = item["kind"]
    color = item.get("color", (200, 200, 200))
    if kind == "coin":
        paint_coin(p, None, r)
    elif kind == "key":
        paint_key(p, color)
    elif kind == "key_ornate":
        paint_key(p, color, ornate=True)
        p.glow(color, 26)
    elif kind == "seal":
        paint_seal(p, r)
    elif kind == "card":
        paint_card(p, r)
    elif kind == "ring":
        paint_ring(p, r)
    elif kind in ("fang", "chitin"):
        paint_fang(p, color, r)
    elif kind == "hide":
        c = color + (255,)
        p.rect(3, 4, 10, 9, c)
        p.px(3, 4, (0, 0, 0, 0))
        p.px(12, 4, (0, 0, 0, 0))
        p.px(3, 12, (0, 0, 0, 0))
        p.px(12, 12, (0, 0, 0, 0))
        p.noise_rect(4, 5, 8, 7, ramp(c, 4, 0.8, 1.15), r, 0.4)
        p.rect_outline(3, 4, 10, 9, shade(c, 0.7))
    elif kind == "trophy":
        paint_trophy(p, color, r)
    elif kind == "wing":
        paint_wing(p, color, r)
    elif kind == "stinger":
        paint_stinger(p, color, r)
    elif kind == "goo":
        paint_goo(p, color, r)
    elif kind == "tear":
        c = color + (240,)
        dk = shade(c, 0.6)
        p.px(8, 3, c)
        p.px(8, 4, c)
        p.px(7, 5, shade(c, 0.85))
        p.disc(8, 8, 3, c)
        p.px(7, 7, (255, 255, 255, 220))
        p.px(6, 8, shade(c, 1.3))
        p.px(9, 10, dk)
        p.px(10, 9, dk)
        p.px(8, 11, shade(c, 0.75))
        p.glow(color, 28)
    elif kind == "heart":
        paint_heart(p, color, r)
    elif kind == "bones":
        paint_bones(p, color, r)
    elif kind == "core":
        c = color + (255,)
        p.disc(8, 8, 4.5, shade(c, 0.5))
        p.disc(8, 8, 3.0, c)
        p.disc(8, 8, 1.5, shade(c, 1.5))
        for a in range(0, 360, 60):
            x = 8 + round(math.cos(math.radians(a)) * 5.5)
            y = 8 + round(math.sin(math.radians(a)) * 5.5)
            p.px(x, y, shade(c, 0.7))
        p.glow(color, 70)
    elif kind == "book":
        paint_book(p, color, r)
    elif kind == "mask":
        paint_mask(p, color, r)
    else:
        p.disc(8, 8, 4, color + (255,))
    p.outline(DARKLINE)
    p.save(OUT / f"{item['id']}.png")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    count = 0
    for item in fc_data.all_items():
        cat = item["cat"]
        if cat in ("melee", "ranged"):
            paint_weapon_icon(item)
        elif cat == "armor":
            paint_armor_icon(item)
        elif cat == "augment":
            p = Px(16, 16)
            if item["id"] == "augment_remover":
                # pliers-like tool
                c = item["color"] + (255,)
                p.line(4, 12, 11, 5, shade(c, 0.8), 2)
                p.line(11, 5, 13, 3, c, 1)
                p.line(10, 4, 12, 6, shade(c, 1.3), 1)
                p.px(4, 12, (90, 70, 50, 255))
                p.px(3, 13, (90, 70, 50, 255))
                p.outline(DARKLINE)
            else:
                paint_augment(p, item["color"], rng("aug", item["id"]))
                p.outline(DARKLINE)
            p.save(OUT / f"{item['id']}.png")
        elif cat == "consumable":
            p = Px(16, 16)
            kind = item["kind"]
            if kind == "flask":
                paint_flask(p, item["color"])
            elif kind == "flask_large":
                paint_flask(p, item["color"], large=True)
            elif kind == "phial":
                paint_phial(p, item["color"])
            else:
                paint_food(p, item, rng("food", item["id"]))
            p.outline(DARKLINE)
            p.save(OUT / f"{item['id']}.png")
        elif cat == "spell":
            p = Px(16, 16)
            paint_tome(p, item["color"], rng("spell", item["id"]))
            p.outline(DARKLINE)
            p.save(OUT / f"{item['id']}.png")
        else:
            paint_misc(item)
        count += 1
    print(f"painted {count} item icons -> {OUT}")


if __name__ == "__main__":
    main()

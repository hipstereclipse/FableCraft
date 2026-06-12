"""gen_screenshots.py — offline 3D renders of every creation + visual audit.

Renders, using the SAME data that generates the game assets:
  * every mob (textured box model, 3/4 hero view, vignette backdrop)
  * every item icon (upscaled, framed showcase card)
  * every structure (isometric voxel render with palette-true colours)
  * gallery contact sheets per category
  * screenshots/AUDIT.md with measured visual metrics

Renderer: painter's algorithm over textured quads with face shading,
rim-light pass and soft ground shadow. Pure PIL, no GL.
"""
import math
from collections import defaultdict
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

from fc_lib import RP, BP, SHOTS, rng
import fc_data
from fc_mobs import MOBS, build_parts, pack_uvs

ENT_TEX = RP / "textures" / "entity"
ITEM_TEX = RP / "textures" / "items"

# ---------------------------------------------------------------------------
# Math helpers
# ---------------------------------------------------------------------------

def rot_x(p, a):
    c, s = math.cos(a), math.sin(a)
    return (p[0], p[1] * c - p[2] * s, p[1] * s + p[2] * c)


def rot_y(p, a):
    c, s = math.cos(a), math.sin(a)
    return (p[0] * c + p[2] * s, p[1], -p[0] * s + p[2] * c)


def sub(a, b):
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def add(a, b):
    return (a[0] + b[0], a[1] + b[1], a[2] + b[2])


def cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def dot(a, b):
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def norm(a):
    l = math.sqrt(dot(a, a)) or 1.0
    return (a[0] / l, a[1] / l, a[2] / l)


# ---------------------------------------------------------------------------
# Textured-quad renderer
# ---------------------------------------------------------------------------

LIGHT_DIR = norm((-0.45, 0.85, 0.30))


def render_quads(quads, size=(900, 900), zoom=None, center=None, bg=None,
                 yaw=math.pi - 0.65, pitch=0.42, rim=True, floor_y=0.0, shadow=True):
    """quads: list of (corners[4 xyz], tex Image, uv[4 (u,v)], glow:boolean)
    Renders with painter's algorithm after camera transform."""
    W, H = size
    img = Image.new("RGBA", size, (0, 0, 0, 0))
    # transform all corners
    txq = []
    for corners, tex, uvs, glow in quads:
        cam = []
        for c in corners:
            p = c
            if center:
                p = sub(p, center)
            p = rot_y(p, yaw)
            p = rot_x(p, pitch)
            cam.append(p)
        # face normal & depth
        n = norm(cross(sub(cam[1], cam[0]), sub(cam[3], cam[0])))
        depth = sum(c[2] for c in cam) / 4.0
        txq.append((depth, cam, n, tex, uvs, glow))
    txq.sort(key=lambda q: q[0])  # painter: far (small z) first, near last
    # fit zoom
    if zoom is None:
        xs = [c[0] for q in txq for c in q[1]]
        ys = [c[1] for q in txq for c in q[1]]
        span = max(max(xs) - min(xs), max(ys) - min(ys)) or 1
        zoom = (min(W, H) * 0.72) / span
    ox, oy = W / 2, H / 2
    if txq:
        xs = [c[0] for q in txq for c in q[1]]
        ys = [c[1] for q in txq for c in q[1]]
        cx = (max(xs) + min(xs)) / 2
        cy = (max(ys) + min(ys)) / 2
    else:
        cx = cy = 0

    def proj(p):
        return (ox + (p[0] - cx) * zoom, oy - (p[1] - cy) * zoom)

    # soft shadow puddle
    if shadow and txq:
        sh = Image.new("RGBA", size, (0, 0, 0, 0))
        sd = ImageDraw.Draw(sh)
        gx = [proj(c)[0] for q in txq for c in q[1]]
        bottom = max(proj(c)[1] for q in txq for c in q[1])
        x0, x1 = min(gx), max(gx)
        w = (x1 - x0) * 0.6
        cxs = (x0 + x1) / 2
        sd.ellipse([cxs - w / 2, bottom - w * 0.10, cxs + w / 2, bottom + w * 0.10],
                   fill=(10, 8, 6, 110))
        sh = sh.filter(ImageFilter.GaussianBlur(8))
        img.alpha_composite(sh)

    dr = ImageDraw.Draw(img)
    for depth, cam, n, tex, uvs, glow in txq:
        # ambient + key light (lifted so dark fur still reads)
        lum = 0.62 + 0.55 * max(0.0, dot(n, LIGHT_DIR))
        if glow:
            lum = min(1.45, lum + 0.45)
        pts = [proj(c) for c in cam]
        paint_quad(img, dr, pts, tex, uvs, lum)
        if rim:
            # rim light on top edges
            e = norm(cross(sub(cam[1], cam[0]), (0, 0, -1)))
            if n[1] > 0.55:
                dr.line([pts[0], pts[1]], fill=(255, 244, 214, 90), width=1)
    return img


def paint_quad(img, dr, pts, tex, uvs, lum):
    """Subdivide quad into texel-aligned cells and fill with shaded texture
    colours (fast approximate texture mapping)."""
    tw, th = tex.size
    (u0, v0), (u1, v1), (u2, v2), (u3, v3) = uvs
    du = max(abs(u1 - u0), abs(u2 - u3), 1e-6)
    dv = max(abs(v3 - v0), abs(v2 - v1), 1e-6)
    nu = max(1, min(28, int(du)))
    nv = max(1, min(28, int(dv)))
    px = tex.load()

    def lerp2(a, b, t):
        return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)

    for iv in range(nv):
        tv0 = iv / nv
        tv1 = (iv + 1) / nv
        left0 = lerp2(pts[0], pts[3], tv0)
        right0 = lerp2(pts[1], pts[2], tv0)
        left1 = lerp2(pts[0], pts[3], tv1)
        right1 = lerp2(pts[1], pts[2], tv1)
        for iu in range(nu):
            tu0 = iu / nu
            tu1 = (iu + 1) / nu
            quad = [lerp2(left0, right0, tu0), lerp2(left0, right0, tu1),
                    lerp2(left1, right1, tu1), lerp2(left1, right1, tu0)]
            # sample texel
            su = u0 + (u1 - u0) * ((tu0 + tu1) / 2)
            sv = v0 + (v3 - v0) * ((tv0 + tv1) / 2)
            sx = max(0, min(tw - 1, int(su)))
            sy = max(0, min(th - 1, int(sv)))
            c = px[sx, sy]
            if c[3] < 12:
                continue
            col = (max(0, min(255, int(c[0] * lum))),
                   max(0, min(255, int(c[1] * lum))),
                   max(0, min(255, int(c[2] * lum))), c[3])
            dr.polygon(quad, fill=col)


# ---------------------------------------------------------------------------
# Mob -> quads
# ---------------------------------------------------------------------------

def cube_quads(origin, size, uv, tex, inflate=0.0, xform=None, glow=False):
    x0, y0, z0 = origin[0] - inflate, origin[1] - inflate, origin[2] - inflate
    sx, sy, sz = size[0] + 2 * inflate, size[1] + 2 * inflate, size[2] + 2 * inflate
    x1, y1, z1 = x0 + sx, y0 + sy, z0 + sz
    u, v = uv
    isx, isy, isz = max(1, round(size[0])), max(1, round(size[1])), max(1, round(size[2]))
    # corner shorthand
    c = {
        "lbf": (x0, y0, z0), "rbf": (x1, y0, z0), "ltf": (x0, y1, z0), "rtf": (x1, y1, z0),
        "lbb": (x0, y0, z1), "rbb": (x1, y0, z1), "ltb": (x0, y1, z1), "rtb": (x1, y1, z1),
    }
    if xform:
        c = {k: xform(p) for k, p in c.items()}
    quads = []
    def q(corners, uvr):
        (uu0, vv0, uu1, vv1) = uvr
        quads.append((corners, tex, [(uu0, vv0), (uu1, vv0), (uu1, vv1), (uu0, vv1)], glow))
    # front (-z): texture front region
    q([c["ltf"], c["rtf"], c["rbf"], c["lbf"]], (u + isz, v + isz, u + isz + isx, v + isz + isy))
    # back (+z)
    q([c["rtb"], c["ltb"], c["lbb"], c["rbb"]], (u + isz + isx + isz, v + isz, u + 2 * isz + 2 * isx, v + isz + isy))
    # right (-x)
    q([c["ltb"], c["ltf"], c["lbf"], c["lbb"]], (u, v + isz, u + isz, v + isz + isy))
    # left (+x)
    q([c["rtf"], c["rtb"], c["rbb"], c["rbf"]], (u + isz + isx, v + isz, u + 2 * isz + isx, v + isz + isy))
    # top (+y)
    q([c["ltb"], c["rtb"], c["rtf"], c["ltf"]], (u + isz, v, u + isz + isx, v + isz))
    # bottom (-y)
    q([c["lbf"], c["rbf"], c["rbb"], c["lbb"]], (u + isz + isx, v, u + isz + 2 * isx, v + isz))
    return quads


def mob_quads(mob):
    parts = build_parts(mob)
    tw, th, uvmap = pack_uvs(parts)
    tex = Image.open(ENT_TEX / f"{mob['id']}.png").convert("RGBA")
    by_name = {p["name"]: p for p in parts}
    quads = []
    glowy = mob["plan"][0] in ("wraith", "banshee", "nymph") or mob["id"] == "oracle"

    def chain_rot(part, point):
        """Apply this part's rest rotation about its pivot, then parents'."""
        node = part
        while node is not None:
            rx, ry, rz = [math.radians(a) for a in node.get("rot", [0, 0, 0])]
            pv = node["pivot"]
            p = sub(point, pv)
            if rz:
                cz, szn = math.cos(rz), math.sin(rz)
                p = (p[0] * cz - p[1] * szn, p[0] * szn + p[1] * cz, p[2])
            if ry:
                p = rot_y(p, ry)
            if rx:
                p = rot_x(p, rx)
            point = add(p, pv)
            node = by_name.get(node.get("parent"))
        return point

    for pi, part in enumerate(parts):
        for ci, cube in enumerate(part["cubes"]):
            uv = uvmap[(pi, ci)]
            quads += cube_quads(cube["origin"], cube["size"], uv, tex,
                                inflate=cube.get("inflate", 0.0),
                                xform=lambda pt, part=part: chain_rot(part, pt),
                                glow=glowy)
    return quads


# ---------------------------------------------------------------------------
# Backdrops & framing
# ---------------------------------------------------------------------------

MOOD = {
    "frost": ((26, 34, 48), (118, 152, 178)), "fire": ((40, 18, 14), (190, 92, 40)),
    "forest": ((22, 30, 22), (96, 128, 84)), "swamp": ((24, 28, 22), (94, 110, 70)),
    "dark": ((16, 14, 20), (74, 60, 92)), "holy": ((38, 34, 26), (200, 174, 110)),
    "stone": ((26, 24, 22), (120, 110, 96)), "royal": ((28, 22, 30), (140, 110, 150)),
}

MOB_MOOD = {
    "balverine": "forest", "white_balverine": "frost", "frost_balverine": "frost",
    "hobbe": "forest", "hobbe_scout": "forest", "bandit": "stone", "bandit_archer": "stone",
    "undead": "swamp", "wasp": "forest", "wasp_queen": "fire", "beetle": "forest",
    "earth_troll": "swamp", "ice_troll": "frost", "rock_giant": "fire",
    "summoner": "dark", "wraith": "dark", "banshee": "swamp", "minion": "fire",
    "arachanox": "dark", "assassin": "dark", "jack_of_blades": "fire",
    "jack_dragon": "fire", "villager_albion": "holy", "guard_bowerstone": "royal",
    "guard_oakvale": "stone", "guard_snowspire": "frost", "trader": "holy",
    "barkeep": "holy", "guildmaster": "holy", "maze": "royal", "theresa": "royal",
    "lady_grey": "royal", "oracle": "frost", "briar_rose": "forest",
    "mercenary": "stone", "nymph": "forest", "summoned_wasp": "forest",
    "summoned_hobbe": "forest", "summoned_balverine": "forest", "demon_door": "stone",
}


def backdrop(size, mood):
    lo, hi = MOOD[mood]
    W, H = size
    img = Image.new("RGBA", size)
    px = img.load()
    cx, cy = W / 2, H * 0.42
    maxd = math.hypot(cx, cy) * 1.15
    for y in range(H):
        for x in range(0, W, 2):
            d = math.hypot(x - cx, y - cy) / maxd
            t = max(0.0, 1 - d)
            col = tuple(int(lo[i] + (hi[i] - lo[i]) * t * t) for i in range(3)) + (255,)
            px[x, y] = col
            if x + 1 < W:
                px[x + 1, y] = col
    return img


def load_font(sz):
    for name in ("seguisb.ttf", "segoeuib.ttf", "arialbd.ttf", "arial.ttf"):
        try:
            return ImageFont.truetype(name, sz)
        except OSError:
            continue
    return ImageFont.load_default()


def frame_card(render, title, subtitle, mood="stone", size=(900, 1000)):
    W, H = size
    card = backdrop(size, mood)
    # parchment band
    d = ImageDraw.Draw(card)
    rw, rh = render.size
    card.alpha_composite(render, ((W - rw) // 2, int(H * 0.06)))
    band_y = H - 150
    d.rectangle([24, band_y, W - 24, H - 24], fill=(34, 26, 20, 235),
                outline=(190, 156, 96, 255), width=3)
    d.rectangle([30, band_y + 6, W - 30, H - 30], outline=(120, 94, 56, 255), width=1)
    f1 = load_font(40)
    f2 = load_font(22)
    d.text((W / 2, band_y + 38), title, font=f1, fill=(238, 218, 170, 255), anchor="mm")
    d.text((W / 2, band_y + 86), subtitle, font=f2, fill=(170, 150, 118, 255), anchor="mm")
    # corner flourishes
    for cx, cy in ((24, 24), (W - 24, 24), (24, H - 24), (W - 24, H - 24)):
        d.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], outline=(190, 156, 96, 200), width=2)
    return card


# ---------------------------------------------------------------------------
# Structure rendering (voxel -> quads)
# ---------------------------------------------------------------------------

BLOCK_COLORS = {
    "minecraft:stone_bricks": (124, 120, 116), "minecraft:mossy_stone_bricks": (110, 122, 100),
    "minecraft:cracked_stone_bricks": (112, 106, 100), "minecraft:cobblestone": (108, 106, 104),
    "minecraft:mossy_cobblestone": (96, 110, 88), "minecraft:dark_oak_planks": (78, 56, 34),
    "minecraft:dark_oak_log": (58, 42, 26), "minecraft:spruce_planks": (114, 84, 50),
    "minecraft:lantern": (250, 190, 90), "minecraft:soul_lantern": (120, 220, 220),
    "minecraft:chiseled_stone_bricks": (134, 130, 124), "minecraft:obsidian": (28, 22, 44),
    "minecraft:gold_block": (248, 208, 92), "minecraft:quartz_block": (236, 230, 222),
    "minecraft:smooth_quartz": (242, 236, 228), "minecraft:quartz_pillar": (238, 233, 224),
    "minecraft:white_candle": (240, 234, 220), "minecraft:gravel": (118, 114, 110),
    "minecraft:grass_path": (148, 120, 72), "minecraft:polished_deepslate": (78, 78, 82),
    "minecraft:glass_pane": (190, 220, 235), "minecraft:sea_lantern": (190, 235, 225),
    "minecraft:emerald_block": (60, 200, 110), "minecraft:lapis_block": (38, 80, 180),
    "minecraft:moss_block": (96, 130, 66), "minecraft:lectern": (150, 110, 64),
    "minecraft:bookshelf": (140, 105, 62), "minecraft:bed": (170, 50, 50),
    "minecraft:chest": (140, 100, 52), "minecraft:barrel": (120, 88, 50),
    "minecraft:scaffolding": (180, 150, 96), "minecraft:oak_pressure_plate": (160, 130, 80),
    "minecraft:campfire": (255, 150, 50), "minecraft:soul_campfire": (110, 220, 220),
    "minecraft:vine": (70, 110, 50), "minecraft:chiseled_deepslate": (88, 88, 94),
    "minecraft:coarse_dirt": (120, 88, 58), "minecraft:hay_block": (200, 170, 70),
    "minecraft:red_wool": (160, 48, 44), "minecraft:brown_wool": (96, 66, 44),
    "minecraft:black_wool": (38, 34, 34), "minecraft:oak_fence": (150, 118, 70),
    "minecraft:oak_log": (110, 86, 52), "minecraft:carved_pumpkin": (208, 130, 40),
    "minecraft:podzol": (94, 66, 40), "minecraft:cobblestone_wall": (110, 108, 106),
    "minecraft:stone_button": (130, 126, 122), "minecraft:dark_oak_fence": (70, 50, 30),
    "minecraft:crying_obsidian": (60, 30, 90), "minecraft:beacon": (140, 240, 230),
    "minecraft:magma": (190, 90, 30), "minecraft:polished_blackstone": (44, 40, 46),
    "minecraft:gilded_blackstone": (90, 70, 40), "minecraft:polished_blackstone_bricks": (50, 46, 52),
    "minecraft:blackstone_wall": (40, 36, 42), "minecraft:sand": (218, 204, 160),
    "minecraft:sandstone": (208, 192, 148), "minecraft:stone_brick_wall": (120, 116, 112),
    "minecraft:torch": (255, 200, 100), "minecraft:smooth_quartz_stairs": (240, 234, 226),
    "minecraft:end_rod": (240, 240, 255),
    "minecraft:spruce_log": (88, 64, 38), "minecraft:stripped_spruce_log": (146, 110, 64),
    "minecraft:spruce_fence": (114, 84, 50), "minecraft:deepslate_tiles": (66, 66, 70),
    "minecraft:iron_bars": (140, 144, 150), "minecraft:target": (226, 200, 160),
    "minecraft:water": (52, 110, 190), "minecraft:grass_block": (110, 150, 76),
    "minecraft:brown_mushroom": (150, 110, 80), "minecraft:bone_block": (222, 216, 196),
    "minecraft:red_sand": (172, 96, 50), "minecraft:white_wool": (234, 234, 230),
    "minecraft:blue_wool": (60, 80, 160), "minecraft:amethyst_block": (140, 100, 200),
    "minecraft:amethyst_cluster": (180, 140, 240),
}

GLOW_BLOCKS = {"minecraft:lantern", "minecraft:soul_lantern", "minecraft:sea_lantern",
               "minecraft:campfire", "minecraft:soul_campfire", "minecraft:torch",
               "minecraft:beacon", "minecraft:magma", "minecraft:end_rod",
               "minecraft:gold_block", "minecraft:emerald_block", "minecraft:crying_obsidian"}


def render_structure(vox, size=(1100, 900)):
    """vox: gen_structures.Vox (re-built). Isometric painter render."""
    flat = Image.new("RGBA", (4, 4), (255, 255, 255, 255))
    quads = []
    sx, sy, sz = vox.sx, vox.sy, vox.sz
    grid = vox.grid
    pal = vox.palette

    def at(x, y, z):
        if 0 <= x < sx and 0 <= y < sy and 0 <= z < sz:
            return grid[vox.idx(x, y, z)]
        return None

    air = {i for i, (n, s) in enumerate(pal) if n == "minecraft:air"}
    for x in range(sx):
        for y in range(sy):
            for z in range(sz):
                pid = at(x, y, z)
                if pid in air or pid is None:
                    continue
                name = pal[pid][0]
                col = BLOCK_COLORS.get(name, (200, 120, 200))
                glow = name in GLOW_BLOCKS
                # only emit faces exposed to air
                tex = Image.new("RGBA", (2, 2), col + (255,))
                fq = cube_quads((x, y, z), (1, 1, 1), (0, 0), tex, glow=glow)
                keep = []
                checks = [(0, 0, -1), (0, 0, 1), (-1, 0, 0), (1, 0, 0), (0, 1, 0), (0, -1, 0)]
                for i, (dx, dy, dz) in enumerate(checks):
                    nb = at(x + dx, y + dy, z + dz)
                    if nb is None or nb in air or pal[nb][0] in ("minecraft:glass_pane", "minecraft:vine"):
                        # remap uv to flat 2x2
                        corners, _, _, g = fq[i]
                        keep.append((corners, tex, [(0, 0), (2, 0), (2, 2), (0, 2)], g))
                quads += keep
    return render_quads(quads, size=size, yaw=math.pi - 0.72, pitch=0.50, shadow=False)


# ---------------------------------------------------------------------------
# Audit metrics
# ---------------------------------------------------------------------------

def audit_image(img):
    """Returns coverage %, colour count, contrast spread, brightness."""
    small = img.convert("RGBA")
    px = small.load()
    W, H = small.size
    step = 1 if max(W, H) <= 64 else 2
    opaque = 0
    colors = set()
    lum = []
    for y in range(0, H, step):
        for x in range(0, W, step):
            c = px[x, y]
            if c[3] > 40:
                opaque += 1
                colors.add((c[0] // 16, c[1] // 16, c[2] // 16))
                lum.append(0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2])
    total = ((W + step - 1) // step) * ((H + step - 1) // step)
    coverage = opaque / max(1, total)
    if lum:
        mean = sum(lum) / len(lum)
        spread = (max(lum) - min(lum)) / 255
    else:
        mean, spread = 0, 0
    return {
        "coverage": round(coverage * 100, 1),
        "colors": len(colors),
        "contrast": round(spread, 2),
        "brightness": round(mean / 255, 2),
    }


def grade(m, kind):
    score = 0
    notes = []
    if kind == "mob":
        score += 30 if m["colors"] >= 14 else 15 if m["colors"] >= 8 else 5
        score += 30 if m["contrast"] >= 0.55 else 18 if m["contrast"] >= 0.35 else 8
        score += 25 if 10 <= m["coverage"] <= 70 else 12
        score += 15 if 0.18 <= m["brightness"] <= 0.72 else 7
        if m["colors"] < 8:
            notes.append("low palette variety")
        if m["contrast"] < 0.35:
            notes.append("flat shading")
    else:
        score += 35 if m["colors"] >= 6 else 18 if m["colors"] >= 4 else 6
        score += 35 if m["contrast"] >= 0.5 else 20 if m["contrast"] >= 0.3 else 8
        score += 30 if m["coverage"] >= 12 else 15
        if m["coverage"] < 12:
            notes.append("sparse silhouette")
    letter = "S" if score >= 90 else "A" if score >= 75 else "B" if score >= 60 else "C" if score >= 45 else "D"
    return letter, score, notes


# ---------------------------------------------------------------------------
# Contact sheets
# ---------------------------------------------------------------------------

def contact_sheet(images, cols, cell, title, path):
    rows = (len(images) + cols - 1) // cols
    W = cols * cell + 40
    H = rows * cell + 110
    sheet = backdrop((W, H), "stone")
    d = ImageDraw.Draw(sheet)
    f1 = load_font(42)
    d.text((W / 2, 44), title, font=f1, fill=(238, 218, 170, 255), anchor="mm")
    f2 = load_font(15)
    for i, (img, label) in enumerate(images):
        cx = 20 + (i % cols) * cell
        cy = 84 + (i // cols) * cell
        thumb = img.copy()
        thumb.thumbnail((cell - 14, cell - 30))
        sheet.alpha_composite(thumb, (cx + (cell - 14 - thumb.width) // 2 + 7,
                                      cy + (cell - 30 - thumb.height) // 2))
        d.rectangle([cx + 4, cy, cx + cell - 4, cy + cell - 6],
                    outline=(120, 96, 60, 160), width=1)
        d.text((cx + cell / 2, cy + cell - 16), label[:24], font=f2,
               fill=(210, 192, 150, 255), anchor="mm")
    sheet.convert("RGB").save(path, quality=92)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    (SHOTS / "mobs").mkdir(parents=True, exist_ok=True)
    (SHOTS / "items").mkdir(parents=True, exist_ok=True)
    (SHOTS / "structures").mkdir(parents=True, exist_ok=True)
    (SHOTS / "gallery").mkdir(parents=True, exist_ok=True)
    audit_rows = []

    # ---- mobs ----
    mob_thumbs = []
    for mob in MOBS:
        quads = mob_quads(mob)
        mood = MOB_MOOD.get(mob["id"], "stone")
        render = render_quads(quads, size=(860, 760))
        sub = {
            "boss_melee": "Boss · Melee Titan", "flying_boss": "Boss · Airborne Terror",
            "melee": "Hostile · Melee", "ranged": "Hostile · Ranged", "caster": "Hostile · Will-user",
            "flying": "Hostile · Flying", "ghost": "Hostile · Spectral", "npc": "Friendly NPC",
            "guard": "Town Guard", "ally": "Ally", "ally_flying": "Flying Ally", "door": "Ancient Construct",
        }.get(mob["behavior"], mob["behavior"])
        card = frame_card(render, mob["name"], f"{sub}  ·  {mob['hp']} HP  ·  DMG {mob['dmg']}", mood)
        out = SHOTS / "mobs" / f"{mob['id']}.png"
        card.convert("RGB").save(out, quality=92)
        m = audit_image(render)
        letter, score, notes = grade(m, "mob")
        audit_rows.append(("mob", mob["name"], m, letter, score, notes))
        mob_thumbs.append((card, mob["name"]))
        print(f"  mob   {mob['id']:24s} {letter} ({score})")

    # ---- items (group by category; showcase cards for the notable ones) ----
    items = fc_data.all_items()
    notable = {i["id"] for i in fc_data.build_legendaries()}
    notable |= {a["id"] for a in fc_data.AUGMENTS}
    notable |= {s["id"] for s in [{"id": f"spell_{x['id']}"} for x in fc_data.SPELLS]}
    notable |= {"gold_coin", "silver_key", "septimal_key", "guild_seal", "quest_card",
                "resurrection_phial", "jack_of_blades_mask", "archon_torso", "demon_helm",
                "platemail_torso", "assassin_torso", "wizard_hat", "health_potion", "will_potion"}
    item_thumbs = []
    for item in items:
        tex_path = ITEM_TEX / f"{item['id']}.png"
        if not tex_path.exists():
            continue
        icon = Image.open(tex_path).convert("RGBA")
        big = icon.resize((512, 512), Image.NEAREST)
        if item["id"] in notable:
            mood = ("fire" if item["cat"] == "melee" else
                    "dark" if item["cat"] == "spell" else
                    "holy" if item["cat"] in ("augment", "misc") else "stone")
            pad = Image.new("RGBA", (860, 700), (0, 0, 0, 0))
            pad.alpha_composite(big, (174, 70))
            subtitle = {
                "melee": f"Damage {item.get('fable_damage','?')} · {item.get('slots',0)} augment slots",
                "ranged": f"Damage {item.get('fable_damage','?')} · ranged",
                "armor": f"Armour piece · {item.get('slot','')}",
                "augment": "Weapon Augmentation",
                "spell": "Will Power Tome",
                "consumable": "Consumable",
                "misc": item.get("desc", "Treasure of Albion")[:46] if item.get("desc") else "Treasure of Albion",
            }.get(item["cat"], item["cat"])
            card = frame_card(pad, item["name"], subtitle, mood)
            card.convert("RGB").save(SHOTS / "items" / f"{item['id']}.png", quality=92)
        m = audit_image(icon)
        letter, score, notes = grade(m, "item")
        audit_rows.append(("item", item["name"], m, letter, score, notes))
        item_thumbs.append((big, item["name"]))
    print(f"  items rendered ({len(item_thumbs)} icons, {len(notable)} showcase cards)")

    # ---- structures ----
    import gen_structures as GS
    builders = {
        "demon_door_arch": GS.demon_door_arch, "guild_hall": GS.guild_hall,
        "silver_chest_ruin": GS.silver_chest_ruin, "focus_site": GS.focus_site,
        "bandit_camp": GS.bandit_camp, "graveyard": GS.graveyard,
        "temple_avo": GS.temple_avo, "chapel_skorm": GS.chapel_skorm,
        "arena_ring": GS.arena_ring,
    }
    # rebuild Vox objects without saving by monkeypatching save
    struct_thumbs = []
    captured = {}
    orig_save = GS.Vox.save
    def capture_save(self, name):
        captured[name] = self
    GS.Vox.save = capture_save
    for fn in builders.values():
        fn()
    GS.Vox.save = orig_save
    STRUCT_LABELS = {
        "demon_door_arch": ("Demon Door", "Carved arch · dialogue-locked vault", "dark"),
        "guild_hall": ("Heroes' Guild", "Map Room · dormitories · training", "holy"),
        "silver_chest_ruin": ("Silver Key Ruin", "Hidden silver chest dais", "forest"),
        "focus_site": ("Focus Site", "Septimal Key attunement circle", "dark"),
        "bandit_camp": ("Bandit Camp", "Twinblade's raiders · tents · loot", "stone"),
        "graveyard": ("Lychfield Graveyard", "Hollow Men rise at dusk", "swamp"),
        "temple_avo": ("Temple of Avo", "Sanctum of light · sword in the stone", "holy"),
        "chapel_skorm": ("Chapel of Skorm", "Dark sacrifices welcome", "fire"),
        "arena_ring": ("The Arena", "Round-based gladiator combat", "fire"),
    }
    for name, vox in captured.items():
        render = render_structure(vox)
        title, sub, mood = STRUCT_LABELS[name]
        card = frame_card(render, title, sub, mood, size=(1100, 1040))
        card.convert("RGB").save(SHOTS / "structures" / f"{name}.png", quality=92)
        m = audit_image(render)
        letter, score, notes = grade(m, "mob")
        audit_rows.append(("structure", title, m, letter, score, notes))
        struct_thumbs.append((card, title))
        print(f"  struct {name:22s} {letter} ({score})")

    # ---- galleries ----
    contact_sheet(mob_thumbs, 5, 250, "FABLECRAFT — Bestiary of Albion",
                  SHOTS / "gallery" / "bestiary.png")
    weapon_thumbs = [(im, lb) for (im, lb) in item_thumbs
                     if any(w["name"] == lb for w in fc_data.build_weapons() + fc_data.build_legendaries())]
    contact_sheet(weapon_thumbs, 8, 150, "FABLECRAFT — Armoury",
                  SHOTS / "gallery" / "armoury.png")
    other_thumbs = [(im, lb) for (im, lb) in item_thumbs if (im, lb) not in weapon_thumbs][:96]
    contact_sheet(other_thumbs, 8, 150, "FABLECRAFT — Reliquary & Wardrobe",
                  SHOTS / "gallery" / "reliquary.png")
    contact_sheet(struct_thumbs, 3, 360, "FABLECRAFT — Places of Power",
                  SHOTS / "gallery" / "places.png")
    print("  galleries written")

    # ---- audit report ----
    lines = [
        "# Fablecraft: Reforged — Visual Audit",
        "",
        "Automated appearance audit of all generated renders. Metrics measured",
        "directly from the rendered RGBA buffers:",
        "",
        "- **coverage** — % of frame occupied by the subject (silhouette weight)",
        "- **colors** — distinct quantized colours (palette richness)",
        "- **contrast** — luminance spread 0..1 (shading depth)",
        "- **brightness** — mean luminance 0..1",
        "",
        "Grades: S (≥90) A (≥75) B (≥60) C (≥45) D (<45)",
        "",
    ]
    for section, kind in (("Mobs & NPCs", "mob"), ("Items", "item"), ("Structures", "structure")):
        rows = [r for r in audit_rows if r[0] == kind]
        if not rows:
            continue
        lines.append(f"## {section}")
        lines.append("")
        lines.append("| Asset | Grade | Score | Coverage % | Colours | Contrast | Brightness | Notes |")
        lines.append("|---|---|---|---|---|---|---|---|")
        for _, name, m, letter, score, notes in sorted(rows, key=lambda r: -r[4]):
            lines.append(f"| {name} | **{letter}** | {score} | {m['coverage']} | {m['colors']} | {m['contrast']} | {m['brightness']} | {', '.join(notes) if notes else '—'} |")
        avg = sum(r[4] for r in rows) / len(rows)
        lines.append("")
        lines.append(f"**Category average: {avg:.1f}**")
        lines.append("")
    flagged = [r for r in audit_rows if r[3] in ("C", "D")]
    lines.append("## Verdict")
    lines.append("")
    if flagged:
        lines.append(f"{len(flagged)} asset(s) flagged below B grade — listed above with notes.")
    else:
        lines.append("All assets graded B or above. Ship it to Bowerstone.")
    (SHOTS / "AUDIT.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"  AUDIT.md written ({len(audit_rows)} assets, {len(flagged)} flagged)")


if __name__ == "__main__":
    main()

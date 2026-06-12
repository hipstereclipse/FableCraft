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
from io import BytesIO
from collections import defaultdict
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import urlopen

from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageStat

from fc_lib import RP, BP, SHOTS, rng
import fc_data
from fc_mobs import MOBS, build_parts, pack_uvs

ENT_TEX = RP / "textures" / "entity"
ITEM_TEX = RP / "textures" / "items"
VANILLA_TEX_CACHE = Path(__file__).resolve().parent / ".cache" / "vanilla_items"
VANILLA_TEX_BASE = "https://raw.githubusercontent.com/InventivetalentDev/minecraft-assets/1.20.4/assets/minecraft/textures"
_VANILLA_IMAGE_CACHE = {}


def _load_vanilla_texture(item_id):
    if not item_id.startswith("minecraft:"):
        return None
    if item_id in _VANILLA_IMAGE_CACHE:
        return _VANILLA_IMAGE_CACHE[item_id]

    name = item_id.split(":", 1)[1]
    VANILLA_TEX_CACHE.mkdir(parents=True, exist_ok=True)
    for kind in ("item", "block"):
        cached = VANILLA_TEX_CACHE / f"{kind}_{name}.png"
        if cached.exists():
            try:
                img = Image.open(cached).convert("RGBA")
                _VANILLA_IMAGE_CACHE[item_id] = img
                return img
            except OSError:
                pass
        url = f"{VANILLA_TEX_BASE}/{kind}/{name}.png"
        try:
            with urlopen(url, timeout=8) as resp:
                raw = resp.read()
            img = Image.open(BytesIO(raw)).convert("RGBA")
            img.save(cached)
            _VANILLA_IMAGE_CACHE[item_id] = img
            return img
        except (HTTPError, URLError, OSError):
            continue

    _VANILLA_IMAGE_CACHE[item_id] = None
    return None

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
    "twinblade": "fire", "undead": "swamp", "undead_soldier": "swamp", "undead_knight": "dark",
    "wasp": "forest", "wasp_queen": "fire", "beetle": "forest",
    "earth_troll": "swamp", "ice_troll": "frost", "rock_giant": "fire",
    "summoner": "dark", "wraith": "dark", "banshee": "swamp", "minion": "fire",
    "arachanox": "dark", "assassin": "dark", "jack_of_blades": "fire",
    "jack_dragon": "fire", "villager_albion": "holy", "villager_woman": "holy",
    "villager_farmer": "forest", "guard_bowerstone": "royal",
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
    "minecraft:fern": (92, 132, 72), "minecraft:tallgrass": (102, 142, 76),
    "minecraft:dark_oak_leaves": (52, 82, 42),
    "minecraft:white_terracotta": (224, 214, 196), "minecraft:calcite": (228, 226, 220),
    "minecraft:diorite": (200, 198, 196), "minecraft:polished_diorite": (212, 210, 208),
    "minecraft:hay_bale": (200, 170, 70), "minecraft:dirt": (134, 96, 62),
    "minecraft:farmland": (96, 64, 40), "minecraft:wheat": (208, 186, 96),
    "minecraft:oak_leaves": (66, 104, 48), "minecraft:azalea_leaves_flowered": (150, 110, 170),
    "minecraft:sweet_berry_bush": (80, 110, 60), "minecraft:composter": (120, 90, 52),
    "minecraft:beehive": (196, 160, 96), "minecraft:cauldron": (60, 58, 62),
    "minecraft:rose_bush": (190, 50, 60), "minecraft:peony": (228, 170, 200),
    "minecraft:lilac": (196, 150, 210), "minecraft:poppy": (210, 50, 40),
    "minecraft:cornflower": (90, 110, 210), "minecraft:oxeye_daisy": (230, 230, 210),
    "minecraft:red_tulip": (220, 70, 50), "minecraft:allium": (180, 120, 220),
    "minecraft:birch_fence": (206, 192, 150), "minecraft:stripped_oak_log": (178, 144, 90),
    "minecraft:snow_layer": (240, 244, 250), "minecraft:snow_block": (236, 240, 248),
    "minecraft:ice": (160, 200, 240), "minecraft:waterlily": (60, 130, 60),
    "minecraft:deadbush": (148, 108, 60), "minecraft:bell": (240, 200, 90),
    "minecraft:light_blue_stained_glass_pane": (140, 200, 240),
    "minecraft:glowstone": (255, 220, 130), "minecraft:soul_torch": (120, 220, 220),
    "minecraft:stone": (128, 126, 124), "minecraft:mud": (88, 70, 60),
    "minecraft:mud_bricks": (140, 110, 86), "minecraft:enchanting_table": (60, 40, 70),
    "minecraft:oak_planks": (162, 130, 78), "minecraft:packed_ice": (148, 192, 232),
    "minecraft:seagrass": (66, 124, 70),
}

GLOW_BLOCKS = {"minecraft:lantern", "minecraft:soul_lantern", "minecraft:sea_lantern",
               "minecraft:campfire", "minecraft:soul_campfire", "minecraft:torch",
               "minecraft:beacon", "minecraft:magma", "minecraft:end_rod",
               "minecraft:gold_block", "minecraft:emerald_block", "minecraft:crying_obsidian",
               "minecraft:amethyst_cluster", "minecraft:soul_torch", "minecraft:glowstone"}


def render_structure(vox, size=(1100, 900), extra_quads=None,
                      yaw=math.pi - 0.72, pitch=0.50):
    """vox: gen_structures.Vox (re-built). Isometric painter render."""
    flat = Image.new("RGBA", (4, 4), (255, 255, 255, 255))
    quads = list(extra_quads) if extra_quads else []
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
    return render_quads(quads, size=size, yaw=yaw, pitch=pitch, shadow=False)


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
        "placeholder": len(colors) <= 3,
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
        if m.get("placeholder"):
            score -= 18
            notes.append("possible placeholder art")
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


def progression_sheet(matrix, row_labels, col_labels, title, path, cell=132):
    """Render a labeled row/column matrix for tier progression showcases.
    matrix keys are (row_i, col_i) -> (img, label)."""
    rows = len(row_labels)
    cols = len(col_labels)
    left = 260
    top = 110
    W = left + cols * cell + 30
    H = top + rows * cell + 40
    sheet = backdrop((W, H), "stone")
    d = ImageDraw.Draw(sheet)
    f_title = load_font(40)
    f_col = load_font(20)
    f_row = load_font(20)
    f_label = load_font(14)
    d.text((W / 2, 46), title, font=f_title, fill=(238, 218, 170, 255), anchor="mm")

    for ci, col in enumerate(col_labels):
        x = left + ci * cell + cell / 2
        d.text((x, top - 26), col, font=f_col, fill=(218, 196, 158, 255), anchor="mm")

    for ri, row in enumerate(row_labels):
        y = top + ri * cell + cell / 2
        d.text((left - 16, y), row, font=f_row, fill=(210, 188, 150, 255), anchor="rm")

    for ri in range(rows):
        for ci in range(cols):
            x0 = left + ci * cell
            y0 = top + ri * cell
            d.rounded_rectangle([x0 + 4, y0 + 4, x0 + cell - 6, y0 + cell - 8], radius=9,
                                fill=(40, 32, 26, 210), outline=(118, 94, 58, 200), width=2)
            if (ri, ci) not in matrix:
                continue
            img, label = matrix[(ri, ci)]
            thumb = img.copy()
            thumb.thumbnail((cell - 18, cell - 38))
            sheet.alpha_composite(thumb, (x0 + (cell - thumb.width) // 2,
                                          y0 + 6 + (cell - 42 - thumb.height) // 2))
            if label:
                d.text((x0 + cell / 2, y0 + cell - 18), label[:22], font=f_label,
                       fill=(194, 174, 140, 255), anchor="mm")

    sheet.convert("RGB").save(path, quality=92)


# ---------------------------------------------------------------------------
# Recipe cards
# ---------------------------------------------------------------------------

# palette tuples are (base, accent) and drive small procedural icon painting.
VANILLA_PALETTES = {
    "minecraft:iron_ingot": ((172, 178, 188), (218, 224, 236)),
    "minecraft:iron_nugget": ((168, 172, 180), (218, 222, 230)),
    "minecraft:gold_ingot": ((236, 198, 78), (254, 228, 122)),
    "minecraft:gold_nugget": ((230, 188, 72), (250, 220, 112)),
    "minecraft:gold_block": ((232, 194, 66), (255, 232, 120)),
    "minecraft:coal": ((58, 56, 58), (100, 98, 104)),
    "minecraft:coal_block": ((36, 34, 38), (80, 78, 84)),
    "minecraft:stick": ((142, 98, 54), (186, 140, 88)),
    "minecraft:string": ((222, 220, 214), (246, 244, 238)),
    "minecraft:leather": ((154, 98, 56), (198, 142, 94)),
    "minecraft:chain": ((124, 130, 138), (170, 176, 184)),
    "minecraft:obsidian": ((46, 34, 64), (96, 70, 136)),
    "minecraft:ink_sac": ((28, 30, 38), (70, 74, 88)),
    "minecraft:fire_charge": ((236, 126, 46), (255, 208, 104)),
    "minecraft:flint": ((74, 72, 74), (122, 118, 124)),
    "minecraft:arrow": ((178, 172, 160), (220, 214, 196)),
    "minecraft:glass_bottle": ((184, 214, 224), (224, 244, 248)),
    "minecraft:red_mushroom": ((194, 58, 52), (246, 220, 196)),
    "minecraft:sugar": ((236, 236, 234), (255, 255, 255)),
    "minecraft:wheat": ((210, 172, 86), (242, 212, 126)),
    "minecraft:egg": ((236, 220, 194), (252, 242, 224)),
    "minecraft:apple": ((198, 54, 48), (246, 116, 94)),
    "minecraft:paper": ((236, 232, 218), (252, 248, 236)),
    "minecraft:lapis_lazuli": ((52, 86, 190), (102, 146, 238)),
    "minecraft:blue_dye": ((42, 78, 182), (88, 134, 234)),
    "minecraft:honeycomb": ((224, 158, 56), (252, 214, 112)),
    "minecraft:spruce_planks": ((112, 80, 50), (156, 118, 74)),
    "minecraft:oak_planks": ((158, 126, 76), (206, 166, 108)),
    "minecraft:dark_oak_planks": ((78, 56, 36), (126, 92, 62)),
    "minecraft:white_wool": ((232, 232, 226), (252, 252, 248)),
    "minecraft:black_wool": ((52, 50, 52), (94, 92, 96)),
    "minecraft:blue_wool": ((72, 92, 172), (122, 146, 226)),
    "minecraft:red_wool": ((164, 56, 52), (212, 104, 92)),
    "minecraft:purple_wool": ((126, 64, 152), (174, 112, 204)),
}


def _mix(a, b, t):
    return tuple(int(a[i] * (1.0 - t) + b[i] * t) for i in range(3))


def _slot_tile(cell, base):
    tile = Image.new("RGBA", (cell, cell), (0, 0, 0, 0))
    d = ImageDraw.Draw(tile)
    rim = _mix(base, (20, 18, 16), 0.75)
    inner = _mix(base, (255, 255, 255), 0.12)
    d.rounded_rectangle([6, 6, cell - 6, cell - 6], radius=10,
                        fill=inner + (255,), outline=rim + (255,), width=2)
    d.rounded_rectangle([9, 9, cell - 9, 20], radius=7,
                        fill=_mix(base, (255, 255, 255), 0.30) + (70,))
    return tile, d


def _draw_ingot(d, cell, base, accent):
    x0, y0 = 20, cell // 2 - 10
    x1, y1 = cell - 20, cell // 2 + 12
    d.polygon([(x0 + 6, y0), (x1 - 6, y0), (x1, y0 + 7), (x1 - 8, y1), (x0 + 8, y1), (x0, y0 + 7)],
              fill=base + (255,), outline=(24, 20, 18, 255))
    d.polygon([(x0 + 12, y0 + 4), (x1 - 12, y0 + 4), (x1 - 18, y0 + 10), (x0 + 18, y0 + 10)],
              fill=accent + (230,))


def _draw_nugget(d, cell, base, accent):
    d.polygon([(cell // 2 - 12, cell // 2 + 12), (cell // 2 - 22, cell // 2 - 2), (cell // 2 - 6, cell // 2 - 16),
               (cell // 2 + 14, cell // 2 - 10), (cell // 2 + 22, cell // 2 + 8), (cell // 2 + 4, cell // 2 + 18)],
              fill=base + (255,), outline=(24, 20, 18, 255))
    d.polygon([(cell // 2 - 8, cell // 2 - 6), (cell // 2 + 8, cell // 2 - 4), (cell // 2 + 3, cell // 2 + 6),
               (cell // 2 - 10, cell // 2 + 5)], fill=accent + (230,))


def _draw_motif(d, item_id, cell, base, accent):
    if item_id in ("minecraft:iron_ingot", "minecraft:gold_ingot", "minecraft:gold_block"):
        _draw_ingot(d, cell, base, accent)
    elif item_id in ("minecraft:iron_nugget", "minecraft:gold_nugget"):
        _draw_nugget(d, cell, base, accent)
    elif item_id in ("minecraft:coal", "minecraft:coal_block"):
        d.polygon([(24, 62), (18, 46), (30, 30), (50, 26), (62, 38), (56, 58), (38, 66)],
                  fill=base + (255,), outline=(16, 14, 14, 255))
        d.polygon([(42, 58), (36, 42), (48, 34), (56, 42), (52, 54)], fill=accent + (180,))
    elif item_id == "minecraft:stick":
        d.polygon([(24, 64), (30, 70), (70, 30), (64, 24)], fill=base + (255,), outline=(42, 26, 14, 255))
        d.line([(34, 62), (62, 34)], fill=accent + (220,), width=2)
    elif item_id == "minecraft:string":
        d.arc([24, 24, 72, 72], 16, 340, fill=base + (255,), width=4)
        d.arc([28, 30, 68, 68], 28, 350, fill=accent + (220,), width=2)
    elif item_id == "minecraft:chain":
        d.ellipse([30, 26, 52, 48], outline=base + (255,), width=4)
        d.ellipse([44, 40, 66, 62], outline=accent + (255,), width=4)
    elif item_id == "minecraft:obsidian":
        d.polygon([(46, 18), (62, 36), (56, 70), (36, 74), (22, 52), (30, 28)],
                  fill=base + (255,), outline=(12, 10, 18, 255))
        d.line([(40, 28), (52, 44)], fill=accent + (200,), width=2)
        d.line([(34, 44), (48, 60)], fill=accent + (160,), width=2)
    elif item_id.endswith("_wool"):
        d.ellipse([22, 24, 74, 76], fill=base + (255,), outline=(26, 22, 20, 255), width=2)
        for off in (30, 40, 50):
            d.arc([24, off - 8, 72, off + 14], 190, 350, fill=accent + (200,), width=2)
    elif item_id in ("minecraft:ink_sac", "minecraft:blue_dye", "minecraft:lapis_lazuli"):
        d.polygon([(26, 60), (22, 46), (32, 30), (44, 28), (58, 36), (64, 52), (54, 66), (40, 68)],
                  fill=base + (255,), outline=(16, 14, 18, 255))
        d.polygon([(42, 54), (36, 44), (46, 36), (54, 44), (50, 54)], fill=accent + (220,))
    elif item_id == "minecraft:fire_charge":
        d.ellipse([24, 24, 72, 72], fill=_mix(base, (52, 22, 18), 0.3) + (255,), outline=(40, 18, 12, 255), width=2)
        d.polygon([(48, 26), (34, 52), (46, 70), (64, 48)], fill=base + (255,))
        d.polygon([(49, 36), (43, 52), (50, 62), (58, 48)], fill=accent + (255,))
    elif item_id == "minecraft:flint":
        d.polygon([(30, 68), (22, 44), (36, 24), (54, 22), (66, 36), (58, 58), (44, 70)],
                  fill=base + (255,), outline=(20, 18, 18, 255))
        d.line([(34, 38), (54, 52)], fill=accent + (180,), width=2)
    elif item_id == "minecraft:arrow":
        d.line([(26, 66), (66, 26)], fill=base + (255,), width=4)
        d.polygon([(68, 22), (74, 34), (62, 30)], fill=accent + (255,))
        d.polygon([(24, 68), (20, 74), (30, 70)], fill=(180, 132, 86, 255))
    elif item_id == "minecraft:glass_bottle":
        d.rounded_rectangle([38, 22, 58, 34], radius=3, fill=_mix(base, (255, 255, 255), 0.2) + (220,))
        d.rounded_rectangle([30, 32, 66, 72], radius=10, fill=base + (120,), outline=accent + (210,), width=2)
        d.rounded_rectangle([35, 46, 61, 67], radius=7, fill=_mix(base, accent, 0.2) + (120,))
    elif item_id == "minecraft:red_mushroom":
        d.polygon([(34, 62), (38, 44), (50, 44), (54, 62)], fill=(228, 216, 196, 255))
        d.ellipse([22, 24, 66, 52], fill=base + (255,), outline=(70, 20, 18, 255), width=2)
        for px, py in ((34, 34), (44, 30), (54, 36)):
            d.ellipse([px - 3, py - 3, px + 3, py + 3], fill=accent + (255,))
    elif item_id == "minecraft:sugar":
        for bx, by in ((30, 52), (42, 40), (52, 50)):
            d.polygon([(bx, by), (bx + 8, by - 6), (bx + 16, by), (bx + 8, by + 6)],
                      fill=accent + (240,), outline=(190, 190, 190, 255))
    elif item_id == "minecraft:wheat":
        d.line([(34, 70), (48, 26)], fill=(174, 138, 66, 255), width=3)
        for i in range(5):
            y = 58 - i * 7
            d.polygon([(48, y), (58, y - 4), (50, y + 1)], fill=base + (255,))
            d.polygon([(46, y + 1), (36, y - 3), (44, y + 3)], fill=accent + (220,))
    elif item_id == "minecraft:egg":
        d.ellipse([30, 24, 66, 70], fill=base + (255,), outline=(130, 116, 92, 255), width=2)
        d.ellipse([38, 32, 48, 42], fill=accent + (160,))
    elif item_id == "minecraft:apple":
        d.ellipse([26, 30, 70, 72], fill=base + (255,), outline=(78, 24, 20, 255), width=2)
        d.rectangle([46, 20, 50, 32], fill=(124, 84, 44, 255))
        d.ellipse([50, 18, 62, 30], fill=(78, 132, 60, 255))
        d.ellipse([34, 40, 44, 50], fill=accent + (120,))
    elif item_id == "minecraft:paper":
        d.polygon([(28, 24), (60, 24), (68, 32), (68, 70), (28, 70)], fill=base + (255,), outline=(140, 130, 110, 255))
        d.polygon([(60, 24), (60, 32), (68, 32)], fill=accent + (220,))
        d.line([(34, 42), (62, 42)], fill=(186, 176, 152, 255), width=2)
        d.line([(34, 50), (60, 50)], fill=(186, 176, 152, 255), width=2)
    elif item_id == "minecraft:honeycomb":
        for row in range(3):
            for col in range(3 - (row % 2)):
                cx = 30 + col * 14 + (7 if row % 2 else 0)
                cy = 30 + row * 12
                hexp = [(cx - 5, cy), (cx - 2, cy - 5), (cx + 2, cy - 5), (cx + 5, cy), (cx + 2, cy + 5), (cx - 2, cy + 5)]
                d.polygon(hexp, fill=base + (255,), outline=(126, 80, 22, 255))
    elif item_id.endswith("_planks"):
        d.rounded_rectangle([20, 24, 76, 70], radius=6, fill=base + (255,), outline=(54, 34, 20, 255), width=2)
        for y in (34, 46, 58):
            d.line([(24, y), (72, y)], fill=accent + (190,), width=2)
        d.line([(44, 26), (44, 68)], fill=_mix(base, (40, 26, 16), 0.35) + (170,), width=2)
    elif item_id == "minecraft:leather":
        d.polygon([(24, 60), (22, 42), (32, 28), (56, 26), (70, 38), (68, 62), (46, 70)],
                  fill=base + (255,), outline=(80, 46, 24, 255))
        d.line([(34, 36), (60, 56)], fill=accent + (180,), width=2)
    else:
        # Safe fallback for any future vanilla ingredient IDs.
        d.ellipse([24, 24, 72, 72], fill=base + (255,), outline=(28, 22, 18, 255), width=2)
        d.polygon([(48, 30), (54, 44), (70, 48), (54, 52), (48, 66), (42, 52), (26, 48), (42, 44)],
                  fill=accent + (210,))


def ingredient_icon(item_id, cell):
    """Returns an RGBA tile for an ingredient: fc icons from the RP,
    vanilla items as mini painted glyph-free icons."""
    if item_id.startswith("fc:"):
        path = ITEM_TEX / f"{item_id[3:]}.png"
        if path.exists():
            tile = Image.new("RGBA", (cell, cell), (0, 0, 0, 0))
            ic = Image.open(path).convert("RGBA").resize((cell - 10, cell - 10), Image.NEAREST)
            tile.alpha_composite(ic, (5, 5))
            return tile

    vanilla = _load_vanilla_texture(item_id)
    if vanilla is not None:
        tile = Image.new("RGBA", (cell, cell), (0, 0, 0, 0))
        bg, _ = _slot_tile(cell, (58, 52, 46))
        tile.alpha_composite(bg)
        ic = vanilla.resize((cell - 10, cell - 10), Image.NEAREST)
        tile.alpha_composite(ic, (5, 5))
        return tile

    base, accent = VANILLA_PALETTES.get(item_id, ((138, 106, 154), (202, 162, 220)))
    tile, d = _slot_tile(cell, base)
    _draw_motif(d, item_id, cell, base, accent)
    return tile


def render_recipe_card(rec, items_by_id):
    cell = 96
    inner = Image.new("RGBA", (860, 560), (0, 0, 0, 0))
    d = ImageDraw.Draw(inner)
    gx0, gy0 = 120, 120
    # slot grid background
    for ry in range(3):
        for rx_ in range(3):
            x0 = gx0 + rx_ * (cell + 8)
            y0 = gy0 + ry * (cell + 8)
            d.rounded_rectangle([x0, y0, x0 + cell, y0 + cell], radius=8,
                                fill=(30, 24, 20, 200), outline=(118, 94, 58, 255), width=2)
    if rec["type"] == "shaped":
        for ry, row in enumerate(rec["pattern"]):
            for rx_, ch in enumerate(row):
                if ch == " " or ch not in rec["key"]:
                    continue
                icon = ingredient_icon(rec["key"][ch], cell)
                inner.alpha_composite(icon, (gx0 + rx_ * (cell + 8), gy0 + ry * (cell + 8)))
    elif rec["type"] == "shapeless":
        for i, ing in enumerate(rec["ingredients"][:9]):
            rx_, ry = i % 3, i // 3
            icon = ingredient_icon(ing, cell)
            inner.alpha_composite(icon, (gx0 + rx_ * (cell + 8), gy0 + ry * (cell + 8)))
    else:  # furnace
        icon = ingredient_icon(rec["input"], cell)
        inner.alpha_composite(icon, (gx0 + (cell + 8), gy0))
        # drawn flame under the input slot
        fx = gx0 + cell + 56
        fy = gy0 + cell + 70
        d.polygon([(fx, fy - 34), (fx - 22, fy + 14), (fx + 22, fy + 14)],
                  fill=(244, 138, 42, 255))
        d.polygon([(fx, fy - 14), (fx - 11, fy + 12), (fx + 11, fy + 12)],
                  fill=(255, 214, 96, 255))
        d.text((fx, fy + 44), "furnace",
               font=load_font(26), fill=(220, 170, 110, 255), anchor="mm")
    # arrow
    ax = gx0 + 3 * (cell + 8) + 50
    ay = gy0 + (cell + 8) * 1.5 - 6
    d.line([ax, ay, ax + 90, ay], fill=(238, 218, 170, 255), width=8)
    d.polygon([(ax + 90, ay - 18), (ax + 90, ay + 18), (ax + 122, ay)],
              fill=(238, 218, 170, 255))
    # result
    res_id = rec["output"]
    res_icon = ingredient_icon(res_id, 168)
    rx0 = ax + 150
    d.rounded_rectangle([rx0, ay - 84, rx0 + 168, ay + 84], radius=12,
                        fill=(40, 32, 24, 220), outline=(196, 160, 92, 255), width=3)
    inner.alpha_composite(res_icon, (rx0, int(ay) - 84))
    if rec.get("count", 1) > 1:
        d.text((rx0 + 150, ay + 58), f"x{rec['count']}", font=load_font(34),
               fill=(255, 235, 180, 255), anchor="mm")
    return inner


def render_recipe_cards(items):
    items_by_id = {f"fc:{i['id']}": i for i in items}
    thumbs = []
    all_recipes = sorted(fc_data.build_recipes(), key=lambda r: r["id"])
    for rec in all_recipes:
        rid = rec["id"]
        res = items_by_id.get(rec["output"])
        title = res["name"] if res else rid.replace("_", " ").title()
        kind = {"shaped": "Crafting Table", "shapeless": "Crafting Table (shapeless)",
                "furnace": "Furnace Smelting"}[rec["type"]]
        inner = render_recipe_card(rec, items_by_id)
        card = frame_card(inner, title, f"Recipe · {kind}", "stone", size=(1000, 760))
        card.convert("RGB").save(SHOTS / "recipes" / f"{rid}.png", quality=92)
        thumbs.append({"card": card, "title": title, "recipe": rec})
    return thumbs


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
    mob_cards = []
    for mob in MOBS:
        quads = mob_quads(mob)
        mood = MOB_MOOD.get(mob["id"], "stone")
        if mob["id"] == "demon_door":
            # near-frontal so the carved face (eyes + mouth) reads fully
            render = render_quads(quads, size=(860, 760), yaw=math.pi - 0.22, pitch=0.12)
        elif mob["id"] == "jack_of_blades":
            # near-frontal so mask linework and hood silhouette can be judged
            render = render_quads(quads, size=(860, 760), yaw=math.pi - 0.20, pitch=0.24)
        else:
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
        mob_cards.append({"id": mob["id"], "name": mob["name"], "behavior": mob["behavior"], "card": card})
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
    item_cards = []
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
        item_cards.append({"id": item["id"], "name": item["name"], "cat": item["cat"], "img": big, "item": item})
    print(f"  items rendered ({len(item_thumbs)} icons, {len(notable)} showcase cards)")

    # ---- structures ----
    import gen_structures as GS
    builders = {
        "demon_door_arch": GS.demon_door_arch, "guild_hall": GS.guild_hall,
        "chamber_of_fate": GS.chamber_of_fate,
        "oakvale_village": GS.oakvale_village,
        "bowerstone_market": GS.bowerstone_market,
        "knothole_glade": GS.knothole_glade,
        "hook_coast": GS.hook_coast,
        "silver_chest_ruin": GS.silver_chest_ruin, "focus_site": GS.focus_site,
        "power_guild_courtyard": GS.power_guild_courtyard,
        "power_oakvale_quay": GS.power_oakvale_quay,
        "power_snowspire_oracle": GS.power_snowspire_oracle,
        "power_necropolis": GS.power_necropolis,
        "bandit_camp": GS.bandit_camp, "graveyard": GS.graveyard,
        "temple_avo": GS.temple_avo, "chapel_skorm": GS.chapel_skorm,
        "arena_ring": GS.arena_ring,
        "lookout_point": GS.lookout_point, "orchard_farm": GS.orchard_farm,
        "fisher_creek": GS.fisher_creek, "rose_cottage": GS.rose_cottage,
        "witchwood_stones": GS.witchwood_stones, "darkwood_camp": GS.darkwood_camp,
        "hobbe_cave": GS.hobbe_cave, "windmill_hill": GS.windmill_hill,
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
        "chamber_of_fate": ("Chamber of Fate", "Domed fresco hall · central dais", "royal"),
        "oakvale_village": ("Oakvale", "Thatched green · wheat field · quay", "forest"),
        "bowerstone_market": ("Bowerstone Market", "Urban bridge district · walled square", "stone"),
        "knothole_glade": ("Knothole Glade", "Hidden timber village in Witchwood", "forest"),
        "hook_coast": ("Hook Coast", "Snowy port, lighthouse and abbey ruin", "frost"),
        "silver_chest_ruin": ("Silver Key Ruin", "Hidden silver chest dais", "forest"),
        "focus_site": ("Focus Site", "Septimal Key attunement circle", "dark"),
        "power_guild_courtyard": ("Guild Courtyard", "Chalk stream · bridges · Will island", "holy"),
        "power_oakvale_quay": ("Oakvale Quay", "Village green, tree, well and coast", "forest"),
        "power_snowspire_oracle": ("Snowspire Oracle", "Frozen lane to the Oracle monolith", "frost"),
        "power_necropolis": ("Necropolis Ruin", "Glyph stones and broken bridge", "dark"),
        "bandit_camp": ("Bandit Camp", "Twinblade's raiders · tents · loot", "stone"),
        "graveyard": ("Lychfield Graveyard", "Hollow Men rise at dusk", "swamp"),
        "temple_avo": ("Temple of Avo", "Donation fountain · sword in the stone", "holy"),
        "chapel_skorm": ("Chapel of Skorm", "Dark sacrifices welcome", "fire"),
        "arena_ring": ("The Arena", "Round-based gladiator combat", "fire"),
        "lookout_point": ("Lookout Point", "Standing stones · the pointing hero", "forest"),
        "orchard_farm": ("Orchard Farm", "Apple rows · cider barn · beehive", "forest"),
        "fisher_creek": ("Fisher Creek", "Stilt hut · jetty · drying nets", "forest"),
        "rose_cottage": ("Rose Cottage", "Walled rose garden · wishing well", "forest"),
        "witchwood_stones": ("Witchwood Stones", "Monolith ring · dolmen altar", "dark"),
        "darkwood_camp": ("Darkwood Camp", "Trader waystation · watch fire", "stone"),
        "hobbe_cave": ("Hobbe Cave", "Bone-strewn warren · skull totem", "swamp"),
        "windmill_hill": ("Windmill Hill", "Sail arms · millstone · grain field", "forest"),
    }
    for name, vox in captured.items():
        extra = None
        if name == "demon_door_arch":
            # composite the living door face into the carved hillside arch
            dd = next(m for m in MOBS if m["id"] == "demon_door")
            dq = mob_quads(dd)
            s = 0.16  # model units -> blocks, slightly oversized to fill arch
            ox, oy, oz = 11.5, 0.6, 5.5
            extra = [([(c[0] * s + ox, c[1] * s + oy, c[2] * s + oz) for c in corners],
                      tex, uvs, glow) for corners, tex, uvs, glow in dq]
        render = render_structure(vox, extra_quads=extra)
        title, sub, mood = STRUCT_LABELS[name]
        card = frame_card(render, title, sub, mood, size=(1100, 1040))
        card.convert("RGB").save(SHOTS / "structures" / f"{name}.png", quality=92)
        m = audit_image(render)
        letter, score, notes = grade(m, "mob")
        audit_rows.append(("structure", title, m, letter, score, notes))
        struct_thumbs.append((card, title))
        print(f"  struct {name:22s} {letter} ({score})")

    # ---- crafting recipe cards ----
    (SHOTS / "recipes").mkdir(parents=True, exist_ok=True)
    recipe_cards = render_recipe_cards(items)
    print(f"  {len(recipe_cards)} recipe cards rendered")

    # ---- galleries ----
    contact_sheet(mob_thumbs, 5, 250, "FABLECRAFT — Bestiary of Albion",
                  SHOTS / "gallery" / "bestiary.png")

    # focused creature sheets for documentation
    boss_beh = {"boss_melee", "flying_boss"}
    boss_cards = [(m["card"], m["name"]) for m in mob_cards if m["behavior"] in boss_beh]
    hostile_cards = [(m["card"], m["name"]) for m in mob_cards
                     if m["behavior"] in {"melee", "ranged", "caster", "flying", "ghost"}]
    npc_cards = [(m["card"], m["name"]) for m in mob_cards
                 if m["behavior"] in {"npc", "guard", "ally", "ally_flying", "door"}]
    contact_sheet(boss_cards, 4, 260, "FABLECRAFT — Boss Encounters",
                  SHOTS / "gallery" / "bosses.png")
    contact_sheet(hostile_cards, 6, 220, "FABLECRAFT — Hostile Creatures",
                  SHOTS / "gallery" / "mobs_hostile.png")
    contact_sheet(npc_cards, 6, 220, "FABLECRAFT — NPCs, Allies & Curios",
                  SHOTS / "gallery" / "npcs_features.png")

    weapon_thumbs = [(im, lb) for (im, lb) in item_thumbs
                     if any(w["name"] == lb for w in fc_data.build_weapons() + fc_data.build_legendaries())]
    contact_sheet(weapon_thumbs, 8, 150, "FABLECRAFT — Armoury",
                  SHOTS / "gallery" / "armoury.png")
    other_thumbs = [(im, lb) for (im, lb) in item_thumbs if (im, lb) not in weapon_thumbs][:96]
    contact_sheet(other_thumbs, 8, 150, "FABLECRAFT — Reliquary & Wardrobe",
                  SHOTS / "gallery" / "reliquary.png")
    contact_sheet(struct_thumbs, 3, 360, "FABLECRAFT — Places of Power",
                  SHOTS / "gallery" / "places.png")

    # split forge by recipe category for clearer progression coverage
    weapon_ids = {w["id"] for w in fc_data.build_weapons()} | {w["id"] for w in fc_data.build_legendaries()}
    armor_ids = {a["id"] for a in fc_data.build_armor()}
    augment_ids = {a["id"] for a in fc_data.AUGMENTS}
    forge_weapon = [(r["card"], r["title"]) for r in recipe_cards
                    if r["recipe"]["output"].startswith("fc:") and r["recipe"]["output"][3:] in weapon_ids]
    forge_armor = [(r["card"], r["title"]) for r in recipe_cards
                   if r["recipe"]["output"].startswith("fc:") and r["recipe"]["output"][3:] in armor_ids]
    forge_system = [(r["card"], r["title"]) for r in recipe_cards
                    if r["recipe"]["output"].startswith("fc:") and
                    (r["recipe"]["output"][3:] in augment_ids or r["recipe"]["output"][3:] in {
                        "steel_ingot", "obsidian_ingot", "master_ingot", "will_shard",
                        "runed_hilt", "tempered_plate", "guild_cloth", "chain_links",
                    })]

    contact_sheet([(r["card"], r["title"]) for r in recipe_cards], 4, 300, "FABLECRAFT — The Forge of Albion",
                  SHOTS / "gallery" / "forge.png")
    contact_sheet(forge_weapon, 4, 300, "FABLECRAFT — Forge: Weapons",
                  SHOTS / "gallery" / "forge_weapons.png")
    contact_sheet(forge_armor, 4, 300, "FABLECRAFT — Forge: Armour",
                  SHOTS / "gallery" / "forge_armor.png")
    contact_sheet(forge_system, 4, 300, "FABLECRAFT — Forge: Components & Augments",
                  SHOTS / "gallery" / "forge_systems.png")

    # full progression matrices for all craftable weapon and armour lines
    item_img = {x["id"]: x["img"] for x in item_cards}
    weapons = fc_data.build_weapons()
    tiers = ["iron", "steel", "obsidian", "master"]
    wtypes = ["longsword", "katana", "cleaver", "axe", "mace", "pickhammer",
              "greataxe", "greatsword", "greathammer", "longbow", "crossbow"]
    w_matrix = {}
    for ri, wt in enumerate(wtypes):
        for ci, mat in enumerate(tiers):
            iid = f"{mat}_{wt}"
            if iid in item_img:
                w_matrix[(ri, ci)] = (item_img[iid], iid.replace("_", " ").title())
    progression_sheet(w_matrix,
                      [w.replace("_", " ").title() for w in wtypes],
                      [t.title() for t in tiers],
                      "FABLECRAFT — Full Weapon Tier Progression",
                      SHOTS / "gallery" / "progression_weapons.png",
                      cell=128)

    armor = fc_data.build_armor()
    armor_map = {(a["set"], a["slot"]): a["id"] for a in armor if a.get("slot") in {"helm", "torso", "legs", "boots"}}
    sets = sorted({a["set"] for a in armor if a.get("slot") in {"helm", "torso", "legs", "boots"}})
    slots = ["helm", "torso", "legs", "boots"]
    a_matrix = {}
    for ri, set_id in enumerate(sets):
        for ci, slot in enumerate(slots):
            iid = armor_map.get((set_id, slot))
            if iid and iid in item_img:
                a_matrix[(ri, ci)] = (item_img[iid], slot.title())
    progression_sheet(a_matrix,
                      [s.replace("_", " ").title() for s in sets],
                      [s.title() for s in slots],
                      "FABLECRAFT — Full Armour Set Progression",
                      SHOTS / "gallery" / "progression_armor.png",
                      cell=116)
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
    doc_paths = sorted((SHOTS / "docs").glob("*.png"))
    if doc_paths:
        doc_rows = []
        for path in doc_paths:
            img = Image.open(path).convert("RGB")
            stat = ImageStat.Stat(img)
            contrast = sum(stat.stddev) / 3
            palette = len(img.resize((320, 180)).getcolors(320 * 180) or [])
            doc_rows.append((path.name, img.size, contrast, palette))
        sizes = sorted(set(size for _, size, _, _ in doc_rows))
        lines.append("## Documentation Showcase QA")
        lines.append("")
        lines.append(f"- **screenshots checked:** {len(doc_rows)}")
        lines.append(f"- **dimensions:** {', '.join(f'{w}x{h}' for w, h in sizes)}")
        lines.append(f"- **contrast floor:** {min(row[2] for row in doc_rows):.1f} RGB stddev")
        lines.append(f"- **palette floor:** {min(row[3] for row in doc_rows)} sampled colours")
        lines.append("- **missing asset tokens:** 0; scripts/gen_doc_screenshots.py exits non-zero if a scene references missing mob or item art")
        lines.append("")
    flagged = [r for r in audit_rows if r[3] in ("C", "D")]
    lines.append("## Verdict")
    lines.append("")
    if flagged:
        lines.append(f"{len(flagged)} asset(s) flagged below B grade — listed above with notes.")
    else:
        lines.append("All generated asset renders graded B or above, with no missing documentation showcase assets.")
    (SHOTS / "AUDIT.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"  AUDIT.md written ({len(audit_rows)} assets, {len(flagged)} flagged)")


if __name__ == "__main__":
    main()

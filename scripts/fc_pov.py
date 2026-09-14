"""fc_pov.py — first-person perspective renderer over the generated voxel world.

The gallery renderer in gen_screenshots.py is orthographic and frames a structure
from outside as a floating diorama. That is the right format for a catalogue
plate and the wrong one for a screenshot: a player never sees Albion from a
detached isometric camera, and never sees it without a HUD.

This module is the other half — a pinhole camera that stands *inside* the same
Vox data at eye height, so the framing, the occlusion and the sense of scale are
the ones a player actually gets. It keeps the painter's-algorithm, pure-PIL
approach of the gallery renderer (no GL dependency in this repo) and adds the
parts a POV view needs and an isometric one does not:

  * a perspective divide with near-plane clipping, so walls you stand against
    fill the frame instead of vanishing;
  * Minecraft's own directional face shading (top 1.0, N/S 0.8, E/W 0.6,
    bottom 0.5) plus a sky/block light split, so interiors read as lamplit
    rooms rather than evenly lit models;
  * distance fog toward the horizon colour, which is what actually sells depth
    in a voxel scene.

Block faces carry one flat colour each, so they project as exact polygons and
need no texture subdivision; only entity quads are texture-mapped, and those
subdivide in world space (not screen space) so the perspective stays correct.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

from PIL import Image, ImageDraw, ImageFilter

NEAR = 0.05

# Minecraft's fixed directional shading. Rendering every face at full brightness
# is the single biggest reason a naive voxel render reads as "a model" rather
# than "the game": these four constants are what give blocks their solidity.
FACE_SHADE = {
    "up": 1.00,
    "down": 0.50,
    "north": 0.80,
    "south": 0.80,
    "east": 0.60,
    "west": 0.60,
}

# (dx, dy, dz, face name, outward normal)
NEIGHBOURS = (
    (0, 1, 0, "up", (0.0, 1.0, 0.0)),
    (0, -1, 0, "down", (0.0, -1.0, 0.0)),
    (0, 0, -1, "north", (0.0, 0.0, -1.0)),
    (0, 0, 1, "south", (0.0, 0.0, 1.0)),
    (-1, 0, 0, "west", (-1.0, 0.0, 0.0)),
    (1, 0, 0, "east", (1.0, 0.0, 0.0)),
)

# Corner winding per face, in unit-cube local coordinates.
FACE_CORNERS = {
    "up": ((0, 1, 0), (0, 1, 1), (1, 1, 1), (1, 1, 0)),
    "down": ((0, 0, 0), (1, 0, 0), (1, 0, 1), (0, 0, 1)),
    "north": ((0, 0, 0), (0, 1, 0), (1, 1, 0), (1, 0, 0)),
    "south": ((1, 0, 1), (1, 1, 1), (0, 1, 1), (0, 0, 1)),
    "west": ((0, 0, 1), (0, 1, 1), (0, 1, 0), (0, 0, 0)),
    "east": ((1, 0, 0), (1, 1, 0), (1, 1, 1), (1, 0, 1)),
}

# Blocks that do not occlude their neighbours, so a face touching one is still
# drawn. Without this every window is a solid wall and every interior is black.
SEE_THROUGH = {
    "minecraft:air", "minecraft:barrier", "minecraft:glass", "minecraft:glass_pane",
    "minecraft:water", "minecraft:flowing_water", "minecraft:lantern",
    "minecraft:soul_lantern", "minecraft:torch", "minecraft:soul_torch",
    "minecraft:vine", "minecraft:ladder", "minecraft:iron_bars", "minecraft:chain",
    "minecraft:light_blue_stained_glass", "minecraft:blue_stained_glass",
    "minecraft:red_stained_glass", "minecraft:yellow_stained_glass",
    "minecraft:white_stained_glass", "minecraft:purple_stained_glass",
    "minecraft:green_stained_glass", "minecraft:orange_stained_glass",
    "minecraft:brown_stained_glass", "minecraft:black_stained_glass",
    "minecraft:tinted_glass", "minecraft:rail", "minecraft:lever",
    "minecraft:tripwire", "minecraft:cobweb", "minecraft:end_rod",
}

# Faces of these draw but never hide what is behind them.
TRANSLUCENT = {
    "minecraft:glass", "minecraft:glass_pane", "minecraft:water",
    "minecraft:flowing_water", "minecraft:tinted_glass",
}

# name -> emitted light level (0..15), matching the vanilla values the packs rely on.
LIGHT_SOURCES = {
    "minecraft:lantern": 15, "minecraft:soul_lantern": 10, "minecraft:torch": 14,
    "minecraft:soul_torch": 10, "minecraft:campfire": 15, "minecraft:soul_campfire": 10,
    "minecraft:glowstone": 15, "minecraft:sea_lantern": 15, "minecraft:beacon": 15,
    "minecraft:shroomlight": 15, "minecraft:end_rod": 14, "minecraft:magma": 3,
    "minecraft:crying_obsidian": 10, "minecraft:amethyst_cluster": 5,
    "minecraft:redstone_torch": 7, "minecraft:candle": 3, "minecraft:lava": 15,
    "minecraft:flowing_lava": 15, "minecraft:fire": 15, "minecraft:lit_pumpkin": 15,
}


# ---------------------------------------------------------------------------
# vector helpers
# ---------------------------------------------------------------------------

def norm(v):
    length = math.sqrt(v[0] * v[0] + v[1] * v[1] + v[2] * v[2]) or 1.0
    return (v[0] / length, v[1] / length, v[2] / length)


def dot(a, b):
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def cross(a, b):
    return (a[1] * b[2] - a[2] * b[1],
            a[2] * b[0] - a[0] * b[2],
            a[0] * b[1] - a[1] * b[0])


_norm = norm          # the private spelling predates the view model


# ---------------------------------------------------------------------------
# camera
# ---------------------------------------------------------------------------

@dataclass
class Camera:
    """A player-eye pinhole camera in structure block coordinates.

    `yaw` follows the in-game convention used across this repo's scene data:
    0 looks toward +Z, and it increases toward +X. `pitch` is positive looking
    down, matching how a player tilts the view.
    """

    pos: tuple
    yaw: float = 0.0
    pitch: float = 0.0
    fov: float = 70.0          # vertical field of view, degrees
    size: tuple = (1280, 720)

    def __post_init__(self):
        cy, sy = math.cos(self.yaw), math.sin(self.yaw)
        cp, sp = math.cos(self.pitch), math.sin(self.pitch)
        # Right-handed basis (right, up, forward); see module docstring.
        self.forward = (sy * cp, -sp, cy * cp)
        self.right = (cy, 0.0, -sy)
        self.up = (sy * sp, cp, cy * sp)
        self.focal = (self.size[1] / 2.0) / math.tan(math.radians(self.fov) / 2.0)
        self.cx = self.size[0] / 2.0
        self.cy = self.size[1] / 2.0

    def to_cam(self, p):
        dx = p[0] - self.pos[0]
        dy = p[1] - self.pos[1]
        dz = p[2] - self.pos[2]
        r, u, f = self.right, self.up, self.forward
        return (dx * r[0] + dy * r[1] + dz * r[2],
                dx * u[0] + dy * u[1] + dz * u[2],
                dx * f[0] + dy * f[1] + dz * f[2])

    def project(self, c):
        """Camera-space point -> screen. Caller guarantees c[2] >= NEAR."""
        inv = self.focal / c[2]
        return (self.cx + c[0] * inv, self.cy - c[1] * inv)


def clip_near(poly):
    """Sutherland-Hodgman against z >= NEAR, in camera space.

    A POV camera stands close enough to geometry that quads routinely straddle
    the eye plane; without this they project through infinity and smear across
    the frame.
    """
    out = []
    count = len(poly)
    for i in range(count):
        cur = poly[i]
        nxt = poly[(i + 1) % count]
        cur_in = cur[2] >= NEAR
        nxt_in = nxt[2] >= NEAR
        if cur_in:
            out.append(cur)
        if cur_in != nxt_in:
            t = (NEAR - cur[2]) / (nxt[2] - cur[2])
            out.append((cur[0] + (nxt[0] - cur[0]) * t,
                        cur[1] + (nxt[1] - cur[1]) * t,
                        NEAR))
    return out


# ---------------------------------------------------------------------------
# world sampling
# ---------------------------------------------------------------------------

class World:
    """Read-only view over a gen_structures.Vox with the lookups a POV render
    needs: solid test, sky exposure per column, and a block-light field."""

    def __init__(self, vox, block_colors, extra_lights=()):
        self.vox = vox
        self.sx, self.sy, self.sz = vox.sx, vox.sy, vox.sz
        self.colors = block_colors
        pal = vox.palette
        self.pal_name = [name for name, _ in pal]
        self.pal_solid = [name not in SEE_THROUGH for name, _ in pal]
        self.pal_air = [name in ("minecraft:air", "minecraft:barrier") for name, _ in pal]
        self.pal_translucent = [name in TRANSLUCENT for name, _ in pal]
        self.pal_color = [self.colors.get(name, (168, 120, 170)) for name, _ in pal]
        self.pal_tex = [block_texture(name) for name, _ in pal]
        self.grid = vox.grid
        self._heightmap = None
        self._cover = None
        self._lights = None
        self._extra_lights = list(extra_lights)

    def pid(self, x, y, z):
        if 0 <= x < self.sx and 0 <= y < self.sy and 0 <= z < self.sz:
            return self.grid[x * self.sy * self.sz + y * self.sz + z]
        return None

    @property
    def heightmap(self):
        """Highest opaque block per column; anything above it is sky-lit."""
        if self._heightmap is None:
            hm = {}
            solid = self.pal_solid
            for x in range(self.sx):
                base = x * self.sy * self.sz
                for z in range(self.sz):
                    top = -1
                    for y in range(self.sy - 1, -1, -1):
                        if solid[self.grid[base + y * self.sz + z]]:
                            top = y
                            break
                    hm[(x, z)] = top
            self._heightmap = hm
        return self._heightmap

    def sky_exposed(self, x, y, z):
        if not (0 <= x < self.sx and 0 <= z < self.sz):
            return True                       # outside the footprint is open sky
        return y > self.heightmap.get((x, z), -1)

    @property
    def cover(self):
        """Per column, how many solid cells sit above each height.

        A binary open/enclosed test makes anything under a tree canopy or an
        eave as dark as a sealed cellar, which is why the Arboretum's trunks
        came out pure black. Counting the blockers instead lets a leaf layer
        dim the light without extinguishing it, which is much closer to how
        Minecraft's sky light actually falls through a canopy.
        """
        if self._cover is None:
            table = {}
            solid = self.pal_solid
            for x in range(self.sx):
                base = x * self.sy * self.sz
                for z in range(self.sz):
                    counts = bytearray(self.sy + 1)
                    running = 0
                    for y in range(self.sy - 1, -1, -1):
                        counts[y] = min(255, running)
                        if solid[self.grid[base + y * self.sz + z]]:
                            running += 1
                    table[(x, z)] = counts
            self._cover = table
        return self._cover

    def sky_factor(self, x, y, z, indoor):
        """How much of the sky's light reaches a cell, 0..1."""
        if not (0 <= x < self.sx and 0 <= z < self.sz and 0 <= y < self.sy):
            return 1.0
        blockers = self.cover[(x, z)][y]
        if blockers == 0:
            return 1.0
        if blockers <= 2:
            return max(indoor, 0.58)          # canopy, eaves, an open arch
        if blockers <= 4:
            return max(indoor, 0.38)
        return indoor

    @property
    def lights(self):
        """Emissive cells as (x+0.5, y+0.5, z+0.5, level)."""
        if self._lights is None:
            found = list(self._extra_lights)
            emissive = {i: LIGHT_SOURCES[n] for i, n in enumerate(self.pal_name)
                        if n in LIGHT_SOURCES}
            if emissive:
                for x in range(self.sx):
                    base = x * self.sy * self.sz
                    for y in range(self.sy):
                        row = base + y * self.sz
                        for z in range(self.sz):
                            level = emissive.get(self.grid[row + z])
                            if level:
                                found.append((x + 0.5, y + 0.5, z + 0.5, level))
            self._lights = found
        return self._lights


class LightField:
    """Block light sampled from emissive cells, bucketed on a coarse grid.

    Real Minecraft light is a flood fill through air, losing one level per block
    and stopping at walls. Propagating that over a 122x30x108 structure in Python
    costs more than the render itself, so this keeps the part that matters — the
    one-level-per-block falloff, which is what sets how far a lantern actually
    reaches — and skips the occlusion. An inverse-square falloff was tried first
    and put every interior in the dark: a level-15 lantern died within three
    blocks instead of the fifteen it lights in game.
    """

    CELL = 8

    def __init__(self, lights, reach=16.0):
        self.reach = reach
        self.buckets = {}
        for lx, ly, lz, level in lights:
            key = (int(lx // self.CELL), int(ly // self.CELL), int(lz // self.CELL))
            self.buckets.setdefault(key, []).append((lx, ly, lz, level))
        self.span = int(math.ceil(reach / self.CELL))

    def at(self, p):
        px, py, pz = p
        bx, by, bz = int(px // self.CELL), int(py // self.CELL), int(pz // self.CELL)
        total = 0.0
        span = self.span
        reach2 = self.reach * self.reach
        for gx in range(bx - span, bx + span + 1):
            for gy in range(by - span, by + span + 1):
                for gz in range(bz - span, bz + span + 1):
                    for lx, ly, lz, level in self.buckets.get((gx, gy, gz), ()):
                        d2 = (lx - px) ** 2 + (ly - py) ** 2 + (lz - pz) ** 2
                        if d2 > reach2:
                            continue
                        # Vanilla: a source of `level` reaches `level` blocks,
                        # dropping one level per block.
                        reached = level - math.sqrt(d2)
                        if reached > 0:
                            total += (reached / 15.0) ** 1.35
        return min(1.15, total)


# ---------------------------------------------------------------------------
# sky
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Sky:
    """Sky gradient, fog and sun/moon for one time of day."""

    top: tuple
    horizon: tuple
    fog: tuple
    ambient: float                 # sky-light multiplier reaching exposed faces
    indoor: float                  # floor brightness for unlit enclosed faces
    fog_start: float = 34.0
    fog_end: float = 96.0
    sun: tuple = None              # (azimuth rad, elevation rad, radius px, rgb)
    stars: int = 0
    clouds: float = 0.0

    def render(self, cam):
        W, H = cam.size
        img = Image.new("RGB", (W, H))
        draw = ImageDraw.Draw(img)
        # Horizon sits where the camera's pitch puts it, so tilting up shows
        # more open sky exactly as it would in game.
        horizon_y = cam.cy + math.tan(cam.pitch) * cam.focal
        for y in range(H):
            # 0 at the horizon, 1 straight up.
            t = max(0.0, min(1.0, (horizon_y - y) / max(1.0, cam.focal * 1.15)))
            t = t ** 0.72
            col = tuple(round(self.horizon[i] + (self.top[i] - self.horizon[i]) * t)
                        for i in range(3))
            draw.line((0, y, W, y), fill=col)
        if self.stars:
            self._draw_stars(img, cam, horizon_y)
        if self.sun:
            self._draw_sun(img, cam)
        if self.clouds:
            self._draw_clouds(img, cam, horizon_y)
        # Ground haze below the horizon keeps distant terrain from butting
        # straight into open sky.
        if horizon_y < H:
            band = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            bd = ImageDraw.Draw(band)
            depth = max(1, int(H - horizon_y))
            for i in range(depth):
                a = round(200 * (1 - i / depth) ** 1.4)
                bd.line((0, horizon_y + i, W, horizon_y + i), fill=self.fog + (a,))
            img = Image.alpha_composite(img.convert("RGBA"), band).convert("RGB")
        return img.convert("RGBA")

    def _draw_stars(self, img, cam, horizon_y):
        from fc_lib import rng
        r = rng("pov", "stars")
        draw = ImageDraw.Draw(img)
        W, _ = cam.size
        for _ in range(self.stars):
            x = r.uniform(0, W)
            y = r.uniform(-cam.focal * 0.9, horizon_y - 8)
            if y < 0:
                continue
            s = r.choice((1, 1, 1, 2))
            b = r.randint(150, 255)
            draw.rectangle((x, y, x + s, y + s), fill=(b, b, min(255, b + 14)))

    def _draw_sun(self, img, cam):
        az, el, radius, rgb = self.sun
        direction = (math.sin(az) * math.cos(el), math.sin(el), math.cos(az) * math.cos(el))
        c = cam.to_cam((cam.pos[0] + direction[0] * 400,
                        cam.pos[1] + direction[1] * 400,
                        cam.pos[2] + direction[2] * 400))
        if c[2] < NEAR:
            return
        sx, sy = cam.project(c)
        W, H = cam.size
        if not (-radius * 4 < sx < W + radius * 4 and -radius * 4 < sy < H + radius * 4):
            return
        glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        gd = ImageDraw.Draw(glow)
        for i in range(9, 0, -1):
            rr = radius * (1 + i * 0.55)
            gd.ellipse((sx - rr, sy - rr, sx + rr, sy + rr),
                       fill=rgb + (round(16 - i * 1.3),))
        gd.ellipse((sx - radius, sy - radius, sx + radius, sy + radius), fill=rgb + (255,))
        glow = glow.filter(ImageFilter.GaussianBlur(radius * 0.35))
        img.paste(Image.alpha_composite(img.convert("RGBA"), glow).convert("RGB"), (0, 0))

    def _draw_clouds(self, img, cam, horizon_y):
        """Vanilla clouds are a flat sheet at y=192; at ground level they read as
        a soft band just above the horizon rather than individual puffs."""
        from fc_lib import rng
        r = rng("pov", "clouds")
        W, _ = cam.size
        layer = Image.new("RGBA", cam.size, (0, 0, 0, 0))
        ld = ImageDraw.Draw(layer)
        top = horizon_y - cam.focal * 0.62
        for _ in range(26):
            cw = r.uniform(W * 0.08, W * 0.3)
            ch = r.uniform(7, 17)
            cx = r.uniform(-W * 0.1, W * 1.1)
            cy = top + r.uniform(-cam.focal * 0.22, cam.focal * 0.1)
            ld.ellipse((cx, cy, cx + cw, cy + ch),
                       fill=(252, 252, 255, round(150 * self.clouds)))
        layer = layer.filter(ImageFilter.GaussianBlur(7))
        img.paste(Image.alpha_composite(img.convert("RGBA"), layer).convert("RGB"), (0, 0))


DAY = Sky(top=(96, 149, 245), horizon=(178, 206, 240), fog=(186, 211, 240),
          ambient=1.0, indoor=0.26, fog_start=40, fog_end=118,
          sun=(2.1, 0.72, 26, (255, 248, 214)), clouds=0.85)

GOLDEN = Sky(top=(74, 116, 190), horizon=(238, 176, 112), fog=(226, 174, 124),
             ambient=0.86, indoor=0.24, fog_start=32, fog_end=104,
             sun=(1.15, 0.13, 30, (255, 226, 168)), clouds=0.7)

NIGHT = Sky(top=(9, 12, 32), horizon=(28, 34, 66), fog=(24, 30, 58),
            ambient=0.30, indoor=0.14, fog_start=20, fog_end=72,
            sun=(4.0, 0.55, 17, (226, 232, 248)), stars=260, clouds=0.16)

OVERCAST = Sky(top=(126, 140, 160), horizon=(186, 192, 200), fog=(180, 188, 198),
               ambient=0.82, indoor=0.24, fog_start=26, fog_end=86, clouds=0.95)

INDOORS = Sky(top=(52, 58, 78), horizon=(74, 78, 92), fog=(38, 34, 32),
              ambient=0.62, indoor=0.30, fog_start=16, fog_end=58)

UNDERGROUND = Sky(top=(10, 10, 14), horizon=(16, 15, 18), fog=(9, 8, 10),
                  ambient=0.10, indoor=0.10, fog_start=8, fog_end=38)

# The Demon Door reward worlds are their own places, not the overworld; a violet
# sky is how the Library Arcanum reads as "through the door" at a glance.
ARCANE = Sky(top=(44, 32, 78), horizon=(126, 96, 150), fog=(112, 88, 140),
             ambient=0.82, indoor=0.26, fog_start=28, fog_end=92,
             sun=(2.6, 0.34, 21, (232, 208, 255)), stars=90, clouds=0.4)


# ---------------------------------------------------------------------------
# renderer
# ---------------------------------------------------------------------------

@dataclass
class Scene:
    world: World
    cam: Camera
    sky: Sky = field(default_factory=lambda: DAY)
    reach: float = 64.0
    entities: list = field(default_factory=list)   # (corners, tex, uvs, glow) quads
    tint: tuple = None                             # RGBA wash over the world layer


def _lerp3(a, b, t):
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t,
            a[2] + (b[2] - a[2]) * t)


def _expand(pts, amount=0.55):
    """Push a polygon's corners out from its centre by a sub-pixel amount.

    PIL fills polygons without anti-aliasing, so two sub-quads that share an
    edge can round to leave a one-pixel gap and the face ends up gridded with
    background. Overlapping them slightly costs nothing and removes the seams.
    """
    cx = sum(q[0] for q in pts) / len(pts)
    cy = sum(q[1] for q in pts) / len(pts)
    out = []
    for qx, qy in pts:
        dx, dy = qx - cx, qy - cy
        d = math.hypot(dx, dy) or 1.0
        out.append((qx + dx / d * amount, qy + dy / d * amount))
    return out


def _shade(rgb, mult):
    return (max(0, min(255, int(rgb[0] * mult))),
            max(0, min(255, int(rgb[1] * mult))),
            max(0, min(255, int(rgb[2] * mult))))


def _fog_mix(rgb, fog, t):
    return (round(rgb[0] + (fog[0] - rgb[0]) * t),
            round(rgb[1] + (fog[1] - rgb[1]) * t),
            round(rgb[2] + (fog[2] - rgb[2]) * t))


def collect_faces(scene):
    """Visible block faces as (depth, screen_poly, rgb, alpha).

    Walks only solid cells inside the camera's reach, keeps faces that touch a
    see-through neighbour, back-face culls against the eye, then shades by
    face direction, sky exposure and nearby lamps before fogging by distance.
    """
    world, cam, sky = scene.world, scene.cam, scene.sky
    ex, ey, ez = cam.pos
    reach = scene.reach
    reach2 = reach * reach
    grid, syz, sz = world.grid, world.sy * world.sz, world.sz
    pal_air, pal_solid, pal_color = world.pal_air, world.pal_solid, world.pal_color
    pal_translucent = world.pal_translucent
    pal_name = world.pal_name
    pal_tex = world.pal_tex
    light = LightField(world.lights)
    fwd = cam.forward
    W, H = cam.size

    x0 = max(0, int(ex - reach)); x1 = min(world.sx - 1, int(ex + reach))
    y0 = max(0, int(ey - reach)); y1 = min(world.sy - 1, int(ey + reach))
    z0 = max(0, int(ez - reach)); z1 = min(world.sz - 1, int(ez + reach))

    # Anything more than ~60 degrees off the view axis cannot land on screen at
    # these fields of view; rejecting it per cell is what keeps the walk cheap.
    cos_limit = math.cos(math.radians(cam.fov) * 0.5 + math.radians(38))

    faces = []
    append = faces.append
    for x in range(x0, x1 + 1):
        bx = x * syz
        cxd = x + 0.5 - ex
        for y in range(y0, y1 + 1):
            by = bx + y * sz
            cyd = y + 0.5 - ey
            for z in range(z0, z1 + 1):
                pid = grid[by + z]
                if pal_air[pid] or not pal_solid[pid]:
                    if pid is None or pal_air[pid]:
                        continue
                czd = z + 0.5 - ez
                d2 = cxd * cxd + cyd * cyd + czd * czd
                if d2 > reach2:
                    continue
                if d2 > 2.5:
                    dist = math.sqrt(d2)
                    if (cxd * fwd[0] + cyd * fwd[1] + czd * fwd[2]) / dist < cos_limit:
                        continue
                base_rgb = pal_color[pid]
                translucent = pal_translucent[pid]
                emissive = pal_name[pid] in LIGHT_SOURCES
                for dx, dy, dz, face, normal in NEIGHBOURS:
                    nb = world.pid(x + dx, y + dy, z + dz)
                    if nb is not None and pal_solid[nb] and not pal_translucent[nb]:
                        continue
                    if nb is not None and translucent and pal_translucent[nb]:
                        continue
                    # Back-face cull: keep only faces whose outward normal has a
                    # component toward the eye.
                    fcx = x + 0.5 + normal[0] * 0.5
                    fcy = y + 0.5 + normal[1] * 0.5
                    fcz = z + 0.5 + normal[2] * 0.5
                    if ((ex - fcx) * normal[0] + (ey - fcy) * normal[1]
                            + (ez - fcz) * normal[2]) <= 0:
                        continue
                    corners = [(x + cx, y + cy, z + cz)
                               for cx, cy, cz in FACE_CORNERS[face]]
                    cam_poly = [cam.to_cam(c) for c in corners]
                    if max(p[2] for p in cam_poly) < NEAR:
                        continue

                    shade = FACE_SHADE[face]
                    if emissive:
                        level = 1.18
                    else:
                        lit = light.at((fcx, fcy, fcz))
                        daylight = sky.ambient * world.sky_factor(
                            x + dx, y + dy, z + dz, sky.indoor)
                        level = max(daylight, lit)
                    dist = math.sqrt(d2)
                    fog_t = 0.0
                    if dist > sky.fog_start:
                        fog_t = min(1.0, (dist - sky.fog_start)
                                    / (sky.fog_end - sky.fog_start)) ** 1.25
                    alpha = 150 if translucent else 255

                    def emit(poly_cam, mult):
                        rgb = _shade(base_rgb, shade * level * mult)
                        if fog_t:
                            rgb = _fog_mix(rgb, sky.fog, fog_t)
                        append((d2, poly_cam, rgb, alpha))

                    if min(p[2] for p in cam_poly) < NEAR:
                        # Straddling the eye plane: clip and fill flat. This is a
                        # wall pressed against the camera, where surface grain
                        # would not read anyway.
                        clipped = clip_near(cam_poly)
                        if len(clipped) >= 3:
                            emit([cam.project(q) for q in clipped], 1.0)
                        continue

                    pts = [cam.project(q) for q in cam_poly]
                    xs = [q[0] for q in pts]
                    ys = [q[1] for q in pts]
                    if max(xs) < 0 or min(xs) > W or max(ys) < 0 or min(ys) > H:
                        continue

                    # Level of detail: subdivide into texels only as finely as the
                    # face's size on screen can actually show.
                    span = max(max(xs) - min(xs), max(ys) - min(ys))
                    steps = 1 if span < 15 else min(TEX_N, max(2, int(span / 7)))
                    if steps == 1:
                        emit(pts, 1.0)
                        continue

                    tex = block_mip(pal_name[pid], steps)
                    c0, c1, c2, c3 = corners
                    for iv in range(steps):
                        tv0, tv1 = iv / steps, (iv + 1) / steps
                        l0 = _lerp3(c0, c3, tv0)
                        r0 = _lerp3(c1, c2, tv0)
                        l1 = _lerp3(c0, c3, tv1)
                        r1 = _lerp3(c1, c2, tv1)
                        trow = tex[iv]
                        for iu in range(steps):
                            tu0, tu1 = iu / steps, (iu + 1) / steps
                            quad = [_lerp3(l0, r0, tu0), _lerp3(l0, r0, tu1),
                                    _lerp3(l1, r1, tu1), _lerp3(l1, r1, tu0)]
                            screen = [cam.project(cam.to_cam(q)) for q in quad]
                            emit(_expand(screen), trow[iu])
    return faces


def _entity_faces(scene):
    """Textured entity quads, subdivided in world space so perspective holds."""
    cam = scene.cam
    sky = scene.sky
    world = scene.world
    light = LightField(world.lights)
    ex, ey, ez = cam.pos
    out = []
    for corners, tex, uvs, glow in scene.entities:
        cam_corners = [cam.to_cam(c) for c in corners]
        if max(p[2] for p in cam_corners) < NEAR:
            continue
        cx = sum(c[0] for c in corners) / 4.0
        cy = sum(c[1] for c in corners) / 4.0
        cz = sum(c[2] for c in corners) / 4.0
        d2 = (cx - ex) ** 2 + (cy - ey) ** 2 + (cz - ez) ** 2
        # How many texels this quad covers on screen decides the subdivision.
        screen = [cam.project(p) for p in cam_corners if p[2] >= NEAR]
        if len(screen) < 2:
            continue
        span = max(max(p[0] for p in screen) - min(p[0] for p in screen),
                   max(p[1] for p in screen) - min(p[1] for p in screen))
        (u0, v0), (u1, _), (_, _), (_, v3) = uvs
        nu = max(1, min(20, int(abs(u1 - u0)), int(span / 2) + 1))
        nv = max(1, min(20, int(abs(v3 - v0)), int(span / 2) + 1))
        tw, th = tex.size
        px = tex.load()
        if glow:
            level = 1.25
        else:
            lit = light.at((cx, cy, cz))
            daylight = sky.ambient * world.sky_factor(
                int(cx), int(cy) + 1, int(cz), sky.indoor)
            level = max(daylight, lit)
        dist = math.sqrt(d2)
        fog_t = 0.0
        if dist > sky.fog_start:
            fog_t = min(1.0, (dist - sky.fog_start) / (sky.fog_end - sky.fog_start)) ** 1.25

        def lerp3(a, b, t):
            return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t,
                    a[2] + (b[2] - a[2]) * t)

        for iv in range(nv):
            tv0, tv1 = iv / nv, (iv + 1) / nv
            left0 = lerp3(corners[0], corners[3], tv0)
            right0 = lerp3(corners[1], corners[2], tv0)
            left1 = lerp3(corners[0], corners[3], tv1)
            right1 = lerp3(corners[1], corners[2], tv1)
            sv = int(v0 + (v3 - v0) * ((tv0 + tv1) / 2))
            sy_ = max(0, min(th - 1, sv))
            for iu in range(nu):
                tu0, tu1 = iu / nu, (iu + 1) / nu
                su = int(u0 + (u1 - u0) * ((tu0 + tu1) / 2))
                sx_ = max(0, min(tw - 1, su))
                col = px[sx_, sy_]
                if col[3] < 12:
                    continue
                world_quad = [lerp3(left0, right0, tu0), lerp3(left0, right0, tu1),
                              lerp3(left1, right1, tu1), lerp3(left1, right1, tu0)]
                cam_quad = [cam.to_cam(p) for p in world_quad]
                if max(p[2] for p in cam_quad) < NEAR:
                    continue
                clipped = clip_near(cam_quad)
                if len(clipped) < 3:
                    continue
                rgb = _shade(col[:3], level)
                if fog_t:
                    rgb = _fog_mix(rgb, sky.fog, fog_t)
                # Nudge entity depth toward the eye so a mob standing against a
                # wall is not swallowed by the wall's own face.
                out.append((d2 - 0.35, [cam.project(p) for p in clipped], rgb, col[3]))
    return out


def render(scene):
    """Full POV frame: sky, world, entities, then atmosphere."""
    cam = scene.cam
    img = scene.sky.render(cam)
    faces = collect_faces(scene) + _entity_faces(scene)
    faces.sort(key=lambda f: -f[0])            # painter: far first

    layer = Image.new("RGBA", cam.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer, "RGBA")
    for _depth, pts, rgb, alpha in faces:
        if len(pts) < 3:
            continue
        draw.polygon(pts, fill=rgb + (alpha,))
    img.alpha_composite(layer)

    if scene.tint:
        wash = Image.new("RGBA", cam.size, scene.tint)
        img.alpha_composite(wash)
    return img


def vignette(img, strength=0.55):
    """Minecraft darkens the frame edges in low light; it also stops a flat
    render from looking like a texture swatch."""
    W, H = img.size
    mask = Image.new("L", (W, H), 0)
    md = ImageDraw.Draw(mask)
    md.ellipse((-W * 0.30, -H * 0.36, W * 1.30, H * 1.36), fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(min(W, H) * 0.14))
    dark = Image.new("RGBA", (W, H), (0, 0, 0, round(255 * strength)))
    out = img.copy()
    out.paste(Image.alpha_composite(img, dark), (0, 0),
              Image.eval(mask, lambda v: 255 - v))
    return out


# ---------------------------------------------------------------------------
# procedural block surfaces
# ---------------------------------------------------------------------------
#
# Blocks rendered as one flat colour per face read as a model, not a world: real
# Minecraft surfaces carry grain, courses and mortar, and that detail is most of
# what makes a screenshot legible at a glance.
#
# These are generated from the palette colour rather than downloaded from a
# Minecraft asset mirror on purpose. LEGAL.md commits the repository to assets
# that are "original or generated for this project", and baking Mojang's block
# textures into images that then get committed would quietly break that. So each
# family below paints a 16x16 field of *brightness multipliers* around 1.0,
# which the shading pipeline applies on top of the existing palette colour: the
# palette stays authoritative, provenance stays clean, and the surfaces still
# break up the way stone, plank and brick surfaces do.

TEX_N = 16
_TEX_CACHE = {}


def _tex_rng(name):
    from fc_lib import rng
    return rng("pov-tex", name)


def _blank(value=1.0):
    return [[value] * TEX_N for _ in range(TEX_N)]


def _speckle(grid, r, amount, density=1.0):
    for y in range(TEX_N):
        for x in range(TEX_N):
            if density >= 1.0 or r.random() < density:
                grid[y][x] *= 1.0 + r.uniform(-amount, amount)


def _planks(r, vertical=False):
    grid = _blank()
    board = 4
    for b in range((TEX_N + board - 1) // board):
        tone = 1.0 + r.uniform(-0.09, 0.09)
        for i in range(board):
            p = b * board + i
            if p >= TEX_N:
                break
            edge = 0.89 if i == 0 else 1.0
            for j in range(TEX_N):
                # Grain runs along the board, so streaks vary across its length.
                streak = 1.0 + r.uniform(-0.055, 0.055)
                if vertical:
                    grid[j][p] = tone * edge * streak
                else:
                    grid[p][j] = tone * edge * streak
    return grid


def _bricks(r):
    grid = _blank()
    course = 4
    for y in range(TEX_N):
        row = y // course
        offset = (row % 2) * (course * 2)
        for x in range(TEX_N):
            if y % course == 0 or (x + offset) % (course * 2) == 0:
                grid[y][x] = 0.82                      # mortar
            else:
                grid[y][x] = 1.0 + r.uniform(-0.045, 0.045)
    return grid


def _cobble(r):
    grid = _blank()
    # A handful of stone lumps with darker gaps between them.
    lumps = [(r.uniform(0, TEX_N), r.uniform(0, TEX_N),
              r.uniform(2.2, 4.4), 1.0 + r.uniform(-0.13, 0.13)) for _ in range(9)]
    for y in range(TEX_N):
        for x in range(TEX_N):
            best, tone = 1e9, 0.70
            for lx, ly, rad, lt in lumps:
                d = math.hypot(x + 0.5 - lx, y + 0.5 - ly) - rad
                if d < best:
                    best, tone = d, lt
            grid[y][x] = tone if best < 0 else 0.83
    return grid


def _mottle(r, amount=0.09):
    grid = _blank()
    for y in range(0, TEX_N, 2):
        for x in range(0, TEX_N, 2):
            tone = 1.0 + r.uniform(-amount, amount)
            for dy in range(2):
                for dx in range(2):
                    grid[y + dy][x + dx] = tone * (1.0 + r.uniform(-0.028, 0.028))
    return grid


def _fabric(r):
    grid = _blank()
    for y in range(TEX_N):
        for x in range(TEX_N):
            weave = 0.965 if (x + y) % 2 else 1.03
            grid[y][x] = weave * (1.0 + r.uniform(-0.03, 0.03))
    return grid


def _glass(r):
    grid = _blank(1.06)
    for i in range(TEX_N):
        grid[0][i] = grid[TEX_N - 1][i] = 1.28
        grid[i][0] = grid[i][TEX_N - 1] = 1.28
    grid[1][1] = grid[1][2] = grid[2][1] = 1.42       # a highlight in one corner
    return grid


def _foliage(r):
    grid = _blank()
    _speckle(grid, r, 0.26)
    for _ in range(14):                                # gaps between the leaves
        grid[r.randrange(TEX_N)][r.randrange(TEX_N)] = 0.52
    return grid


def _plated(r):
    """Metal and polished blocks: flat, with a seam and a soft sheen."""
    grid = _blank()
    for y in range(TEX_N):
        for x in range(TEX_N):
            sheen = 1.0 + 0.10 * (1.0 - abs((x + y) / (2.0 * TEX_N) - 0.35) * 2.2)
            grid[y][x] = sheen * (1.0 + r.uniform(-0.018, 0.018))
    for i in range(TEX_N):
        grid[1][i] *= 1.10
        grid[TEX_N - 2][i] *= 0.90
    return grid


def _grass_top(r):
    grid = _blank()
    _speckle(grid, r, 0.14)
    for _ in range(22):
        x, y = r.randrange(TEX_N), r.randrange(TEX_N)
        grid[y][x] *= r.choice((0.86, 1.14))
    return grid


def _family(name):
    """Pick a surface family from the block id. Order matters: the specific
    checks have to win over the substring catch-alls below them."""
    if "glass" in name:
        return "glass"
    if "leaves" in name or name.endswith(("vine", "grass_block")):
        return "foliage"
    if "planks" in name or "fence" in name or "door" in name or "bookshelf" in name:
        return "planks"
    if "log" in name or "wood" in name or "stem" in name:
        return "log"
    if "bricks" in name or name.endswith("brick") or "tiles" in name:
        return "bricks"
    if "cobblestone" in name or "cobbled" in name or "andesite" in name or "gravel" in name:
        return "cobble"
    if "wool" in name or "carpet" in name or "banner" in name or "bed" in name:
        return "fabric"
    if ("_block" in name and any(m in name for m in ("iron", "gold", "diamond", "copper",
                                                     "emerald", "netherite", "lapis"))
            or "polished" in name or "smooth" in name or "terracotta" in name):
        return "plated"
    if "grass" in name or "moss" in name or "podzol" in name:
        return "grass"
    if "sand" in name or "dirt" in name or "path" in name or "soul" in name:
        return "mottle_rough"
    return "mottle"


_BUILDERS = {
    "glass": lambda r: _glass(r),
    "foliage": lambda r: _foliage(r),
    "planks": lambda r: _planks(r, vertical=False),
    "log": lambda r: _planks(r, vertical=True),
    "bricks": lambda r: _bricks(r),
    "cobble": lambda r: _cobble(r),
    "fabric": lambda r: _fabric(r),
    "plated": lambda r: _plated(r),
    "grass": lambda r: _grass_top(r),
    "mottle_rough": lambda r: _mottle(r, 0.15),
    "mottle": lambda r: _mottle(r, 0.085),
}


def block_texture(name):
    """16x16 brightness multipliers for a block id, deterministic per name."""
    if name not in _TEX_CACHE:
        _TEX_CACHE[name] = _BUILDERS[_family(name)](_tex_rng(name))
    return _TEX_CACHE[name]


_MIP_CACHE = {}


def block_mip(name, steps):
    """The block's surface averaged down to steps x steps.

    Point-sampling the full 16x16 field at a coarse subdivision turns a one-texel
    mortar line into a band several texels wide and leaves the walls looking
    tiled. Averaging each cell instead makes the grain wash out smoothly as a
    face gets smaller on screen, which is what a mipmapped texture does in game.
    """
    key = (name, steps)
    mip = _MIP_CACHE.get(key)
    if mip is None:
        base = block_texture(name)
        if steps >= TEX_N:
            mip = base
        else:
            mip = []
            for iv in range(steps):
                y0, y1 = iv * TEX_N // steps, (iv + 1) * TEX_N // steps
                row = []
                for iu in range(steps):
                    x0, x1 = iu * TEX_N // steps, (iu + 1) * TEX_N // steps
                    cells = [base[y][x] for y in range(y0, y1) for x in range(x0, x1)]
                    row.append(sum(cells) / len(cells))
                mip.append(row)
        _MIP_CACHE[key] = mip
    return mip


# ---------------------------------------------------------------------------
# staging
# ---------------------------------------------------------------------------
#
# Picking camera coordinates by hand against a 122x30x108 structure means
# guessing, and a guess that lands one block off puts the lens inside a wall.
# These helpers stage a shot the way a player would take one: stand on a floor,
# check you can actually see the subject, and prefer the angle that shows the
# most of the room.

EYE_HEIGHT = 1.62          # vanilla player eye offset above the feet


def floor_y(world, x, z, y_hint=None, headroom=2):
    """Highest surface at (x, z) with headroom above it, or None.

    Searches downward from y_hint (or the top) so multi-storey builds resolve to
    the floor the caller means rather than always the ground one.
    """
    xi, zi = int(x), int(z)
    if not (0 <= xi < world.sx and 0 <= zi < world.sz):
        return None
    top = world.sy - 1 if y_hint is None else min(world.sy - 1, int(y_hint))
    for y in range(top, -1, -1):
        pid = world.pid(xi, y, zi)
        if pid is None or not world.pal_solid[pid]:
            continue
        if all(world.pal_air[world.pid(xi, y + 1 + h, zi)]
               for h in range(headroom)
               if world.pid(xi, y + 1 + h, zi) is not None):
            return y + 1
    return None


def line_of_sight(world, a, b, step=0.3):
    """March a ray from a to b; False as soon as an opaque block blocks it."""
    dx, dy, dz = b[0] - a[0], b[1] - a[1], b[2] - a[2]
    dist = math.sqrt(dx * dx + dy * dy + dz * dz)
    if dist < 1e-6:
        return True
    steps = int(dist / step)
    for i in range(1, steps):
        t = i / steps
        pid = world.pid(int(a[0] + dx * t), int(a[1] + dy * t), int(a[2] + dz * t))
        if pid is None:
            continue
        if world.pal_solid[pid] and not world.pal_translucent[pid]:
            return False
    return True


def look_at(eye, target):
    """(yaw, pitch) pointing eye at target, in this module's convention."""
    dx, dy, dz = target[0] - eye[0], target[1] - eye[1], target[2] - eye[2]
    return math.atan2(dx, dz), math.atan2(-dy, math.hypot(dx, dz))


def content_score(world, eye, yaw, pitch, fov=70.0, reach=26.0, rays=60):
    """How much solid geometry a candidate view actually lands on.

    A viewpoint can have clear line of sight to its subject and still be a bad
    shot — staring across an empty yard, or nose-first into one flat wall. Firing
    a spread of rays through the frustum and counting distinct blocks hit (and
    how varied their distances are) separates "a room" from "a surface".
    """
    from fc_lib import rng
    r = rng("pov-score", f"{eye}:{yaw:.3f}")
    cam = Camera(pos=eye, yaw=yaw, pitch=pitch, fov=fov, size=(16, 9))
    hits, depths = set(), []
    for _ in range(rays):
        # Sample the frustum in normalised screen space.
        sx, sy = r.uniform(-0.9, 0.9), r.uniform(-0.55, 0.55)
        d = (cam.forward[0] + cam.right[0] * sx + cam.up[0] * sy,
             cam.forward[1] + cam.right[1] * sx + cam.up[1] * sy,
             cam.forward[2] + cam.right[2] * sx + cam.up[2] * sy)
        d = _norm(d)
        for i in range(1, int(reach / 0.5)):
            t = i * 0.5
            px, py, pz = eye[0] + d[0] * t, eye[1] + d[1] * t, eye[2] + d[2] * t
            pid = world.pid(int(px), int(py), int(pz))
            if pid is None:
                break
            if world.pal_solid[pid] and not world.pal_translucent[pid]:
                hits.add((int(px), int(py), int(pz)))
                depths.append(t)
                break
    if not depths:
        return 0.0
    mean = sum(depths) / len(depths)
    spread = math.sqrt(sum((d - mean) ** 2 for d in depths) / len(depths))
    # Distinct surfaces filling the frame, at a mix of depths, and not so close
    # that the camera is buried in one wall.
    return len(hits) * (1.0 + spread * 0.35) * min(1.0, mean / 3.0)


def find_viewpoint(world, target, distances=(6, 8, 10, 13), headings=24,
                   y_hint=None, eye_height=EYE_HEIGHT, pitch_bias=0.0,
                   fov=70.0, must_see=True):
    """Stage a camera that stands on a floor and actually frames `target`.

    Returns (eye, yaw, pitch) for the best-scoring candidate on a ring around
    the subject, or None when nothing in range can see it.
    """
    best = None
    for ring in distances:
        for h in range(headings):
            ang = 2 * math.pi * h / headings
            x = target[0] + math.cos(ang) * ring
            z = target[2] + math.sin(ang) * ring
            fy = floor_y(world, x, z, y_hint=y_hint)
            if fy is None:
                continue
            eye = (x, fy + eye_height, z)
            if must_see and not line_of_sight(world, eye, target):
                continue
            yaw, pitch = look_at(eye, target)
            pitch += pitch_bias
            score = content_score(world, eye, yaw, pitch, fov=fov)
            # Prefer a subject that sits at a comfortable distance rather than
            # filling the lens or vanishing into the far wall.
            score *= 1.0 - abs(ring - 9) * 0.035
            if best is None or score > best[0]:
                best = (score, eye, yaw, pitch)
    if best is None:
        return None
    return best[1], best[2], best[3]


# ---------------------------------------------------------------------------
# camera-space geometry (the view model)
# ---------------------------------------------------------------------------
#
# The held item and the player's arm are not in the world: they are pinned to
# the camera, and Minecraft renders them through the same projection as
# everything else. Compositing them as flat 2D sprites is what makes a frame
# look assembled rather than captured — a rotated pixel sprite has no thickness,
# no foreshortening and ragged non-axis-aligned edges that nothing else in the
# frame has.
#
# These take quads already expressed in camera space (X right, Y up, Z forward)
# and put them through the same near-clip, projection and fill path the world
# uses, so the view model shares the frame's perspective exactly.

def paint_camera_quads(img, cam, quads):
    """Draw (corners, rgb, alpha) camera-space quads over a rendered frame."""
    prepared = []
    for corners, rgb, alpha in quads:
        if max(c[2] for c in corners) < NEAR:
            continue
        clipped = clip_near(list(corners))
        if len(clipped) < 3:
            continue
        depth = sum(c[2] for c in corners) / len(corners)
        prepared.append((depth, [cam.project(c) for c in clipped], rgb, alpha))
    prepared.sort(key=lambda q: -q[0])            # painter: far first

    layer = Image.new("RGBA", cam.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer, "RGBA")
    for _d, pts, rgb, alpha in prepared:
        draw.polygon(_expand(pts), fill=tuple(rgb) + (alpha,))
    img.alpha_composite(layer)
    return img


def box_quads(centre, size, basis, faces):
    """Six shaded faces of an oriented box.

    `basis` is (right, up, forward) unit vectors in camera space; `faces` maps
    each face name to (rgb, alpha) or to a callable (u, v) -> (rgb, alpha) for
    textured faces sampled across the face.
    """
    r, u, f = basis
    hx, hy, hz = size[0] / 2, size[1] / 2, size[2] / 2

    def corner(sx, sy, sz):
        return (centre[0] + r[0] * sx * hx + u[0] * sy * hy + f[0] * sz * hz,
                centre[1] + r[1] * sx * hx + u[1] * sy * hy + f[1] * sz * hz,
                centre[2] + r[2] * sx * hx + u[2] * sy * hy + f[2] * sz * hz)

    # (name, corner signs in winding order, outward normal in basis terms)
    plan = (
        ("up", ((-1, 1, -1), (-1, 1, 1), (1, 1, 1), (1, 1, -1)), (0, 1, 0)),
        ("down", ((-1, -1, 1), (-1, -1, -1), (1, -1, -1), (1, -1, 1)), (0, -1, 0)),
        ("front", ((-1, -1, -1), (-1, 1, -1), (1, 1, -1), (1, -1, -1)), (0, 0, -1)),
        ("back", ((1, -1, 1), (1, 1, 1), (-1, 1, 1), (-1, -1, 1)), (0, 0, 1)),
        ("left", ((-1, -1, 1), (-1, 1, 1), (-1, 1, -1), (-1, -1, -1)), (-1, 0, 0)),
        ("right", ((1, -1, -1), (1, 1, -1), (1, 1, 1), (1, -1, 1)), (1, 0, 0)),
    )
    out = []
    for name, signs, _n in plan:
        spec = faces.get(name)
        if spec is None:
            continue
        corners = [corner(*s) for s in signs]
        out.append((corners, spec[0], spec[1]))
    return out

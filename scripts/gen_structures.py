"""gen_structures.py — builds .mcstructure files (little-endian NBT) for all
generated buildings. Placement happens at runtime via world.structureManager
driven by deterministic chunk hashing in main.js.

Structures land in BP/structures/fc/<name>.mcstructure  ->  "fc:<name>".
"""
import math

from fc_lib import (BP, NBT, TAG_COMPOUND, TAG_END, TAG_INT, nbt_byte,
                    nbt_compound, nbt_int, nbt_list, nbt_string,
                    write_mcstructure, rng)

BLOCK_VERSION = 18176512  # 1.21.90


class Vox:
    """Tiny voxel canvas -> .mcstructure"""

    def __init__(self, sx, sy, sz, fill="minecraft:air"):
        self.sx, self.sy, self.sz = sx, sy, sz
        self.palette = []
        self.pal_idx = {}
        self.grid = [self._pid(fill)] * (sx * sy * sz)

    def _pid(self, name, states=None):
        key = (name, tuple(sorted((states or {}).items())))
        if key not in self.pal_idx:
            self.pal_idx[key] = len(self.palette)
            self.palette.append((name, states or {}))
        return self.pal_idx[key]

    def idx(self, x, y, z):
        # mcstructure order: x*sy*sz + y*sz + z
        return x * self.sy * self.sz + y * self.sz + z

    def set(self, x, y, z, name, states=None):
        if 0 <= x < self.sx and 0 <= y < self.sy and 0 <= z < self.sz:
            self.grid[self.idx(x, y, z)] = self._pid(name, states)

    def fill(self, x0, y0, z0, x1, y1, z1, name, states=None):
        for x in range(min(x0, x1), max(x0, x1) + 1):
            for y in range(min(y0, y1), max(y0, y1) + 1):
                for z in range(min(z0, z1), max(z0, z1) + 1):
                    self.set(x, y, z, name, states)

    def box(self, x0, y0, z0, x1, y1, z1, name, states=None):
        """Hollow box (walls only)."""
        for x in range(x0, x1 + 1):
            for y in range(y0, y1 + 1):
                for z in range(z0, z1 + 1):
                    if x in (x0, x1) or y in (y0, y1) or z in (z0, z1):
                        self.set(x, y, z, name, states)

    def save(self, name):
        pal_nodes = []
        for bname, states in self.palette:
            state_nodes = {}
            for k, v in states.items():
                if isinstance(v, bool):
                    state_nodes[k] = nbt_byte(1 if v else 0)
                elif isinstance(v, int):
                    state_nodes[k] = nbt_int(v)
                else:
                    state_nodes[k] = nbt_string(str(v))
            pal_nodes.append(nbt_compound({
                "name": nbt_string(bname),
                "states": nbt_compound(state_nodes),
                "version": nbt_int(BLOCK_VERSION),
            }))
        layer0 = nbt_list(TAG_INT, [nbt_int(i) for i in self.grid])
        layer1 = nbt_list(TAG_INT, [nbt_int(-1)] * len(self.grid))
        root = nbt_compound({
            "format_version": nbt_int(1),
            "size": nbt_list(TAG_INT, [nbt_int(self.sx), nbt_int(self.sy), nbt_int(self.sz)]),
            "structure": nbt_compound({
                "block_indices": nbt_list(9, [layer0, layer1]),
                "entities": nbt_list(TAG_END, []),
                "palette": nbt_compound({
                    "default": nbt_compound({
                        "block_palette": nbt_list(TAG_COMPOUND, pal_nodes),
                        "block_position_data": nbt_compound({}),
                    })
                }),
            }),
            "structure_world_origin": nbt_list(TAG_INT, [nbt_int(0), nbt_int(0), nbt_int(0)]),
        })
        write_mcstructure(BP / "structures" / "fc" / f"{name}.mcstructure", root)
        print(f"  fc:{name}  ({self.sx}x{self.sy}x{self.sz}, palette {len(self.palette)})")


STONE = "minecraft:stone_bricks"
MOSSY = "minecraft:mossy_stone_bricks"
CRACK = "minecraft:cracked_stone_bricks"
COBBLE = "minecraft:cobblestone"
MCOBBLE = "minecraft:mossy_cobblestone"
DARKOAK = "minecraft:dark_oak_planks"
DARKLOG = "minecraft:dark_oak_log"
SPRUCE = "minecraft:spruce_planks"
LANTERN = "minecraft:lantern"
SOUL_LANTERN = "minecraft:soul_lantern"
CHISELED = "minecraft:chiseled_stone_bricks"
OBSIDIAN = "minecraft:obsidian"
GOLD = "minecraft:gold_block"
QUARTZ = "minecraft:quartz_block"
CANDLE = "minecraft:white_candle"
GRAVEL = "minecraft:gravel"
PATH = "minecraft:dirt_path"   # Bedrock 1.21 id; the old "grass_path" no longer
                              # exists and silently places as AIR (the holes)
DEEPSLATE_W = "minecraft:polished_deepslate"


def rnd_stone(r):
    return r.choice([STONE, STONE, STONE, MOSSY, CRACK])


SPRUCE_LOG = "minecraft:spruce_log"
STRIPPED_SPRUCE = "minecraft:stripped_spruce_log"
SPRUCE_FENCE = "minecraft:spruce_fence"
DEEP_TILES = "minecraft:deepslate_tiles"
IRON_BARS = "minecraft:iron_bars"
GLASS = "minecraft:glass_pane"


def cylinder(v, cx, cz, radius, y0, y1, mat, hollow=True, fill_mat=None):
    for x in range(cx - radius, cx + radius + 1):
        for z in range(cz - radius, cz + radius + 1):
            d = math.hypot(x - cx, z - cz)
            if d <= radius + 0.4:
                inner = d < radius - 0.6
                for y in range(y0, y1 + 1):
                    if inner:
                        if fill_mat:
                            v.set(x, y, z, fill_mat)
                        continue
                    v.set(x, y, z, mat)


def cone_roof(v, cx, cz, radius, y, mat, tip=None):
    rr, lvl = radius, 0
    while rr >= 0:
        for x in range(cx - rr, cx + rr + 1):
            for z in range(cz - rr, cz + rr + 1):
                d = math.hypot(x - cx, z - cz)
                if (rr - 1 < d <= rr + 0.4) or (rr <= 1 and d <= rr + 0.4):
                    v.set(x, y + lvl, z, mat)
        rr -= 1
        lvl += 1
    if tip:
        v.set(cx, y + lvl, cz, tip)


def gable_roof_z(v, x0, x1, z0, z1, y, mat, end_mat):
    """Gable with ridge running along z. Fills triangular end walls."""
    i = 0
    while x0 + i <= x1 - i:
        for z in range(z0, z1 + 1):
            v.set(x0 + i, y + i, z, mat)
            v.set(x1 - i, y + i, z, mat)
        for x in range(x0 + i + 1, x1 - i):
            v.set(x, y + i, z0, end_mat)
            v.set(x, y + i, z1, end_mat)
        i += 1


def tent(v, x0, z0, depth, half, col, r, open_front=True):
    """A-frame wool tent with log ridge poles; front faces -z."""
    wool = f"minecraft:{col}_wool"
    cx = x0 + half
    for i in range(half + 1):
        for z in range(z0, z0 + depth):
            v.set(x0 + i, 1 + i, z, wool)
            v.set(x0 + 2 * half - i, 1 + i, z, wool)
    # close the back wall
    for i in range(half):
        for x in range(x0 + i + 1, x0 + 2 * half - i):
            v.set(x, 1 + i, z0 + depth - 1, wool)
    # ridge poles
    v.set(cx, 1, z0, SPRUCE_FENCE)
    v.set(cx, 2, z0, SPRUCE_FENCE) if half > 2 else None
    # bedroll + storage inside
    v.set(cx - 1, 1, z0 + 1, "minecraft:white_wool")
    v.set(cx - 1, 1, z0 + 2, "minecraft:white_wool")
    if half > 2:
        v.set(cx + 1, 1, z0 + depth - 2, "minecraft:chest",
              {"minecraft:cardinal_direction": "north"})
        v.set(cx, 1, z0 + 1, LANTERN, {"hanging": False})


# ---------------------------------------------------------------------------

def demon_door_arch():
    """Demon Door site carved into a living hillside: a rocky crag rises and
    widens behind the carved arch so the door always reads as set into a
    mountainside. Rune monoliths, braziers, stairs and overgrowth out front.
    The fc:demon_door entity (the living face) is summoned in the arch."""
    r = rng("struct", "demon_door")
    W, H, D = 23, 18, 13
    v = Vox(W, H, D)
    cx = W // 2
    wall_z = 4  # the carved face sits here; everything behind is hillside
    # foundation
    for x in range(W):
        for z in range(D):
            v.set(x, 0, z, MCOBBLE if r.random() < 0.3 else COBBLE)
    # ---- the hillside crag: rises and widens toward the back ----
    for z in range(wall_z, D):
        t = (z - wall_z) / max(1, D - 1 - wall_z)
        spread = int(t * 3)            # widens with depth
        crest = 11 + int(t * 6)        # rises with depth
        for x in range(W):
            edge_fall = max(0, (abs(x - cx) - (7 + spread))) * 2
            h = crest - edge_fall + r.randrange(0, 2)
            for y in range(1, max(2, h)):
                roll = r.random()
                mat = STONE if roll < 0.45 else (MOSSY if roll < 0.65 else
                                                 (CRACK if roll < 0.8 else COBBLE))
                v.set(x, y, z, mat)
            # grassy crown on the hill
            if h > 3 and z > wall_z + 1:
                v.set(x, max(2, h), z, "minecraft:grass_block" if r.random() < 0.75 else MCOBBLE)
                if r.random() < 0.12:
                    v.set(x, max(2, h) + 1, z, "minecraft:fern" if r.random() < 0.5 else "minecraft:tallgrass")
    # a windswept tree atop the crag
    tx = cx + r.choice((-5, 5))
    ty = 0
    for y in range(H - 1, 1, -1):
        if v.grid[v.idx(tx, y, D - 3)] != v._pid("minecraft:air"):
            ty = y + 1
            break
    if ty:
        for y in range(ty, min(H - 2, ty + 3)):
            v.set(tx, y, D - 3, DARKLOG)
        v.set(tx, min(H - 2, ty + 3), D - 3, "minecraft:dark_oak_leaves")
        v.set(tx - 1, min(H - 3, ty + 2), D - 3, "minecraft:dark_oak_leaves")
        v.set(tx + 1, min(H - 3, ty + 2), D - 3, "minecraft:dark_oak_leaves")
    # ---- carve the deep arch opening into the face (5 wide, 8 high) ----
    v.fill(cx - 2, 1, wall_z, cx + 2, 7, wall_z + 2, "minecraft:air")
    v.fill(cx - 1, 8, wall_z, cx + 1, 8, wall_z + 2, "minecraft:air")
    # tiered chiseled arch frame
    for y in range(1, 9):
        v.set(cx - 3, y, wall_z, CHISELED)
        v.set(cx + 3, y, wall_z, CHISELED)
    for x in range(cx - 3, cx + 4):
        v.set(x, 9, wall_z, CHISELED)
    v.set(cx - 2, 8, wall_z, CHISELED)
    v.set(cx + 2, 8, wall_z, CHISELED)
    # skull keystone + flanking carvings
    v.set(cx, 10, wall_z, "minecraft:chiseled_deepslate")
    v.set(cx - 1, 9, wall_z, "minecraft:chiseled_deepslate")
    v.set(cx + 1, 9, wall_z, "minecraft:chiseled_deepslate")
    # rune monoliths flanking the approach
    for mx in (2, W - 3):
        for y in range(1, 6):
            v.set(mx, y, 1, OBSIDIAN if y < 4 else "minecraft:crying_obsidian")
        v.set(mx, 6, 1, SOUL_LANTERN)
    # brazier pedestals at the arch
    for bx in (cx - 5, cx + 5):
        v.set(bx, 1, wall_z - 1, CHISELED)
        v.set(bx, 2, wall_z - 1, "minecraft:campfire")
    # worn path + steps to the door
    for z in range(0, wall_z):
        for x in range(cx - 2, cx + 3):
            v.set(x, 0, z, PATH if r.random() < 0.7 else GRAVEL)
    # rubble + hanging vines on the face
    for i in range(10):
        x = r.randrange(W)
        if r.random() < 0.5:
            v.set(x, 1, r.choice([0, 1, 2]), MCOBBLE if r.random() < 0.5 else "minecraft:cobblestone_wall")
    for x in range(0, W, 2):
        if abs(x - cx) > 3:
            h = r.randrange(3, 8)
            for y in range(max(1, 10 - h), 10):
                v.set(x, y, wall_z - 1, "minecraft:vine", {"vine_direction_bits": 8})
    v.save("demon_door_arch")


# ---------------------------------------------------------------------------
# Heroes' Guild construction helpers
# ---------------------------------------------------------------------------

# warm sandstone palette for the Guild's tan Albion masonry
SAND = "minecraft:sandstone"
SAND_SMOOTH = "minecraft:smooth_sandstone"
SAND_CUT = "minecraft:cut_sandstone"
SAND_CHIS = "minecraft:chiseled_sandstone"
SAND_STAIR = "minecraft:sandstone_stairs"
SAND_WALL = "minecraft:sandstone_wall"
SLATE = "minecraft:deepslate_tiles"      # cool grey roof slate
SLATE_STAIR = "minecraft:cobblestone_stairs"
RED = "minecraft:red_wool"               # crimson runner / Fable red trim
BRICK = "minecraft:bricks"
SBRICK_STAIR = "minecraft:stone_brick_stairs"
OAK_STAIR = "minecraft:oak_stairs"
SPRUCE_STAIR = "minecraft:spruce_stairs"
DARKOAK_FENCE = "minecraft:dark_oak_fence"


def _mat(m):
    """Allow callers to pass either a block name or a zero-arg factory that
    returns one (for per-block masonry variation)."""
    return m() if callable(m) else m


def guild_stone(r):
    """Warm Guild masonry: mostly sandstone with mossy/cut variation."""
    return r.choice([SAND, SAND, SAND, SAND_CUT, SAND_SMOOTH, STONE, MOSSY])


def _stair_dir(dx, dz):
    """Bedrock stair weirdo_direction ascending toward the dominant axis of
    (dx, dz):  0=+x east, 1=-x west, 2=+z south, 3=-z north."""
    if abs(dx) >= abs(dz):
        return 0 if dx > 0 else 1
    return 2 if dz > 0 else 3


def spiral_stair(v, cx, cz, radius, y0, y1, mat, post=None, steps_per_rev=12,
                 ccw=True, support=STONE):
    """A walkable spiral staircase winding up around (cx,cz). One block of
    climb per step; consecutive treads stay edge/corner adjacent so a Hero can
    walk straight up. Optional centre post and a support block under each tread."""
    n = y1 - y0
    pts = []
    for i in range(n + 1):
        ang = (i / steps_per_rev) * 2 * math.pi * (1 if ccw else -1)
        x = cx + round(math.cos(ang) * radius)
        z = cz + round(math.sin(ang) * radius)
        pts.append((x, y0 + i, z))
    for i, (x, y, z) in enumerate(pts):
        if i + 1 < len(pts):
            dx, dz = pts[i + 1][0] - x, pts[i + 1][2] - z
        else:
            dx, dz = x - pts[i - 1][0], z - pts[i - 1][2]
        if dx == 0 and dz == 0:
            dx = 1
        v.set(x, y, z, mat, {"weirdo_direction": _stair_dir(dx, dz),
                             "upside_down_bit": False})
        if support:
            v.set(x, y - 1, z, support)
    if post:
        for y in range(y0, y1 + 2):
            v.set(cx, y, cz, post)
    return pts


def dome(v, cx, cz, radius, y0, mat, ring_mat=None, oculus=None):
    """A stepped hemispherical dome capping a round room, rising from y0."""
    rr = radius
    lvl = 0
    while rr >= 0:
        for x in range(cx - rr, cx + rr + 1):
            for z in range(cz - rr, cz + rr + 1):
                d = math.hypot(x - cx, z - cz)
                if rr - 1 < d <= rr + 0.45 or (rr <= 1 and d <= rr + 0.45):
                    m = ring_mat if (ring_mat and lvl % 2 == 0) else mat
                    v.set(x, y0 + lvl, z, _mat(m))
        rr -= 1
        lvl += 1
    if oculus:
        v.set(cx, y0 + lvl - 1, cz, oculus)


def ring_wall(v, cx, cz, radius, y0, y1, mat, gaps=()):
    """Hollow circular wall; gaps is a list of (angle_deg, half_width_deg)
    openings left for doorways."""
    for x in range(cx - radius, cx + radius + 1):
        for z in range(cz - radius, cz + radius + 1):
            d = math.hypot(x - cx, z - cz)
            if radius - 0.6 < d <= radius + 0.45:
                ang = math.degrees(math.atan2(z - cz, x - cx)) % 360
                skip = False
                for ga, gw in gaps:
                    da = abs((ang - ga + 180) % 360 - 180)
                    if da <= gw:
                        skip = True
                        break
                for y in range(y0, y1 + 1):
                    if skip and y <= y0 + 3:
                        continue
                    v.set(x, y, z, _mat(mat))


def long_table(v, x0, x1, z, y, top="minecraft:oak_planks",
               leg="minecraft:oak_fence", runner=None):
    """A long banquet table running along x at height y (top sits on y, legs
    fill y-? down to floor at y0=1). Optional decorative runner block on top."""
    for x in range(x0, x1 + 1):
        v.set(x, y, z, top)
        if runner and x0 + 1 <= x <= x1 - 1 and (x - x0) % 2 == 0:
            v.set(x, y + 1, z, runner)
    for x in (x0, x1, (x0 + x1) // 2):
        for yy in range(1, y):
            v.set(x, yy, z, leg)


def hip_roof(v, x0, x1, z0, z1, y, mat, ridge=None, step=1, levels=None, cap=None):
    """A four-sided hipped roof shrinking inward on all edges each level. If
    `levels` is given the slopes stop after that many courses and the remaining
    top is flat-filled with `cap` (or `mat`), keeping wide halls from spiking
    into tall black pyramids."""
    i = 0
    while x0 + i <= x1 - i and z0 + i <= z1 - i:
        if levels is not None and i >= levels:
            for x in range(x0 + i, x1 - i + 1):
                for z in range(z0 + i, z1 - i + 1):
                    v.set(x, y + i, z, cap or mat)
            return
        yy = y + i
        for x in range(x0 + i, x1 - i + 1):
            v.set(x, yy, z0 + i, mat)
            v.set(x, yy, z1 - i, mat)
        for z in range(z0 + i, z1 - i + 1):
            v.set(x0 + i, yy, z, mat)
            v.set(x1 - i, yy, z, mat)
        i += step
    if ridge:
        for x in range(x0 + i - 1, x1 - i + 2):
            v.set(x, y + i, (z0 + z1) // 2, ridge)


def guild_hall():
    """The Heroes' Guild of Albion — a painstaking recreation of the Fable hall.

    One connected campus on a single floor. The heart is a round, domed MAP
    ROOM rotunda holding the breathing relief Map of Albion; the CULLIS GATE
    glows in its LEFT (west) alcove and the green SKILL / Experience portal in
    its RIGHT (east) alcove. A pillared nave runs south to the twin-towered
    gatehouse and forecourt (with the Boasting Platform to the left); the
    Dining Hall and bar lie east, a stream runs through the grounds spanned by
    plank bridges with the Bakery on the far bank; the two-storey domed Library
    runs north to the iron Guild-Cave door, its gallery lined with dormitory
    cells; and a stone path crosses to MAZE'S TOWER, whose spiral stair winds
    up to his study. The Demon-Door plaza sits in the south-east. Every room is
    walkable and the waking Hero lands dry on the crimson runner."""
    r = rng("struct", "guild")
    W, H, L = 92, 30, 100
    v = Vox(W, H, L)

    # ---- feature anchors (kept in lock-step with main.js placeGuildNear) ----
    AX = 34                       # the campus' north-south spine (x)
    ROT_X, ROT_Z, ROT_R = 34, 44, 9   # Map Room rotunda centre + radius
    CGX, CGZ = 21, 44             # Cullis Gate   — LEFT  / west of the map
    SKX, SKZ = 47, 44             # Skill portal  — RIGHT / east of the map
    WAKE_Z = 30                   # crimson-runner wake/recall point (x = AX)
    QUEST_Z = 40                  # Quest lectern at the map's south edge
    TWR_X, TWR_Z, TWR_R = 62, 85, 6   # Maze's Tower spire
    STUDY_Y = 15                  # tower study floor
    UP_Y = 9                      # rotunda balcony / clerestory level
    WCX0, WCX1 = 74, 79           # the stream that runs through the grounds

    warm = lambda: guild_stone(r)

    # ================= GROUND: one continuous campus plinth =================
    # A LEVEL lawn of full-height blocks only (grass + a little moss/podzol for
    # natural colour). No grass-path/gravel speckle here — those left a pocked,
    # hole-ridden checkerboard; intentional paving is laid per-area further down.
    for x in range(W):
        for z in range(L):
            roll = r.random()
            v.set(x, 0, z, "minecraft:grass_block" if roll < 0.84 else
                  ("minecraft:moss_block" if roll < 0.94 else "minecraft:podzol"))

    # the stream + cobbled banks
    for z in range(8, L - 5):
        for x in range(WCX0, WCX1 + 1):
            v.set(x, 0, z, "minecraft:water")
        v.set(WCX0 - 1, 0, z, COBBLE if r.random() < 0.6 else MCOBBLE)
        v.set(WCX1 + 1, 0, z, COBBLE if r.random() < 0.6 else MCOBBLE)
        if r.random() < 0.12:
            v.set(WCX0 - 1, 1, z, "minecraft:tallgrass")

    def plank_bridge(zc, x0, x1):
        # A 3-wide plank deck one block proud of the banks, with a ramp STAIR at
        # each end so a Hero walks straight up onto it (no awkward jump), railed
        # along both sides, and a paved landing where it meets each bank.
        for x in range(x0 + 1, x1):
            for z in (zc - 1, zc, zc + 1):
                v.set(x, 1, z, DARKOAK)
            v.set(x, 2, zc - 1, SPRUCE_FENCE)
            v.set(x, 2, zc + 1, SPRUCE_FENCE)
        for z in (zc - 1, zc, zc + 1):
            v.set(x0, 1, z, SPRUCE_STAIR, {"weirdo_direction": 0, "upside_down_bit": False})  # ascend east
            v.set(x1, 1, z, SPRUCE_STAIR, {"weirdo_direction": 1, "upside_down_bit": False})  # ascend west
        # lantern posts on the rails + paved landings onto each bank
        v.set(x0 + 1, 3, zc - 1, SPRUCE_FENCE); v.set(x0 + 1, 4, zc - 1, LANTERN, {"hanging": False})
        v.set(x1 - 1, 3, zc + 1, SPRUCE_FENCE); v.set(x1 - 1, 4, zc + 1, LANTERN, {"hanging": False})
        for z in (zc - 1, zc, zc + 1):
            for x in (x0 - 1, x0 - 2, x1 + 1, x1 + 2):
                if 0 <= x < W:
                    v.set(x, 0, z, STONE if (x + z) % 2 else SAND_SMOOTH)
    # three bridges, each lined up with a real crossing: the Demon-Door plaza
    # (south), the training grounds (centre) and the Archery Range (north)
    for zc in (22, 44, 64):
        plank_bridge(zc, WCX0 - 2, WCX1 + 2)

    # ================= FORECOURT + paved approach =================
    for x in range(16, 53):
        for z in range(7, 35):
            v.set(x, 0, z, STONE if (x + z) % 4 else SAND)
    for z in range(7, ROT_Z - ROT_R + 1):
        for x in range(AX - 2, AX + 3):
            v.set(x, 0, z, DEEP_TILES if (x + z) % 5 == 0 else SAND_SMOOTH)

    # ---- twin-towered GATEHOUSE (south) ----
    for tx in (AX - 6, AX + 6):
        cylinder(v, tx, 5, 2, 1, 11, warm())
        for ang in range(0, 360, 90):
            wx_ = tx + round(math.cos(math.radians(ang)) * 2)
            wz_ = 5 + round(math.sin(math.radians(ang)) * 2)
            v.set(wx_, 6, wz_, GLASS)
        cone_roof(v, tx, 5, 3, 12, SLATE, tip="minecraft:end_rod")
        v.set(tx, 4, 5, LANTERN, {"hanging": True})
    # a tall, grand arch — side piers rise seven courses, a deep chiseled lintel
    # caps it, and the tympanum carries the Guild's crimson-and-gold sigil
    for y in range(1, 8):
        v.set(AX - 3, y, 5, SAND_CHIS)
        v.set(AX + 3, y, 5, SAND_CHIS)
    for x in range(AX - 3, AX + 4):
        v.set(x, 8, 5, SAND_CHIS)
    for x in range(AX - 2, AX + 3):
        v.set(x, 7, 5, RED)
    v.set(AX, 7, 5, GOLD)            # the gold sigil at the heart of the banner
    v.set(AX - 1, 6, 5, GOLD)
    v.set(AX + 1, 6, 5, GOLD)
    v.set(AX - 2, 6, 5, LANTERN, {"hanging": True})
    v.set(AX + 2, 6, 5, LANTERN, {"hanging": True})
    # twin stone torchieres flank the approach (lore: "two stone torchieres")
    for txr in (AX - 8, AX + 8):
        for y in range(1, 4):
            v.set(txr, y, 9, SAND_CUT if y < 3 else SAND_CHIS)
        v.set(txr, 4, 9, "minecraft:campfire")
        v.set(txr - 1, 1, 9, SAND_WALL)
        v.set(txr + 1, 1, 9, SAND_WALL)
    # broad welcoming steps rising to the threshold
    for x in range(AX - 3, AX + 4):
        for sz in (6, 7):
            v.set(x, 0, sz, SBRICK_STAIR, {"weirdo_direction": 3, "upside_down_bit": False})
    # standing stones lining the flagstone path to the doors (lore)
    for sz in (10, 14, 18):
        v.set(AX - 5, 1, sz, SAND_WALL)
        v.set(AX - 5, 2, sz, "minecraft:torch")
        v.set(AX + 5, 1, sz, SAND_WALL)
        v.set(AX + 5, 2, sz, "minecraft:torch")

    # ---- BOASTING PLATFORM (to the left of the entrance) ----
    bpx0, bpx1, bpz0, bpz1 = 7, 14, 12, 19
    for x in range(bpx0, bpx1 + 1):
        for z in range(bpz0, bpz1 + 1):
            v.set(x, 1, z, SPRUCE if (x + z) % 2 else DARKOAK)
    for x in range(bpx0, bpx1 + 1):
        v.set(x, 1, bpz0 - 1, SPRUCE_STAIR, {"weirdo_direction": 3, "upside_down_bit": False})
    for x in (bpx0, bpx1):
        for z in (bpz0, bpz1):
            v.set(x, 2, z, SPRUCE_FENCE)
            v.set(x, 3, z, SPRUCE_FENCE)
    v.set(bpx0 + 3, 2, bpz1, "minecraft:lectern", {"minecraft:cardinal_direction": "south"})
    v.set(bpx0, 4, bpz0, LANTERN, {"hanging": True})
    v.set(bpx1, 4, bpz1, LANTERN, {"hanging": True})
    v.set(bpx1 + 2, 1, bpz0, SAND_WALL)
    v.set(bpx1 + 2, 2, bpz0, SAND_CHIS)

    for gx in (AX - 9, AX + 9):
        v.set(gx, 1, 14, "minecraft:oak_leaves")
        v.set(gx, 1, 16, "minecraft:azalea_leaves_flowered")
        v.set(gx, 1, 18, "minecraft:oak_leaves")
    v.set(AX + 9, 1, 12, "minecraft:barrel")
    v.set(AX + 10, 1, 13, "minecraft:composter")

    # ================= GUILD SHOP (west of the entrance nave) =================
    sx0, sx1, sz0, sz1 = 16, 27, 26, 35
    for x in range(sx0, sx1 + 1):
        for z in range(sz0, sz1 + 1):
            v.set(x, 0, z, DARKOAK if (x + z) % 3 else SPRUCE)
    for x in range(sx0, sx1 + 1):
        for z in (sz0, sz1):
            for y in range(1, 6):
                v.set(x, y, z, warm())
    for z in range(sz0, sz1 + 1):
        for x in (sx0, sx1):
            for y in range(1, 6):
                v.set(x, y, z, warm())
    gable_roof_z(v, sx0, sx1, sz0, sz1, 5, SLATE, SAND)
    for x in range(sx0 + 2, sx1 - 1):
        v.set(x, 1, sz0 + 3, SPRUCE_STAIR, {"weirdo_direction": 3, "upside_down_bit": False})
    for x in range(sx0 + 1, sx1):
        for y in (2, 3):
            v.set(x, y, sz1 - 1, "minecraft:bookshelf" if (x + y) % 2 else "minecraft:barrel")
    v.set(sx0 + 1, 1, sz1 - 1, "minecraft:chest", {"minecraft:cardinal_direction": "south"})
    v.set(sx1 - 1, 1, sz1 - 1, "minecraft:barrel")
    v.set((sx0 + sx1) // 2, 4, (sz0 + sz1) // 2, LANTERN, {"hanging": True})
    v.fill(sx1, 1, 30, sx1, 3, 32, "minecraft:air")   # door to the nave

    # ================= ENTRANCE NAVE (gatehouse -> rotunda) =================
    nx0, nx1 = AX - 4, AX + 4
    for z in range(34, ROT_Z - ROT_R + 2):
        for x in range(nx0, nx1 + 1):
            v.set(x, 0, z, DEEP_TILES if (x + z) % 6 == 0 else STONE)
        for x in (nx0, nx1):
            for y in range(1, 8):
                v.set(x, y, z, warm())
    for z in range(WAKE_Z - 4, ROT_Z + ROT_R):
        for x in (AX - 1, AX, AX + 1):
            v.set(x, 0, z, RED)
    for z in range(35, 44, 4):
        for x in (nx0, nx1):
            v.set(x, 6, z, DARKLOG)
        v.set(AX, 7, z, LANTERN, {"hanging": True})
    gable_roof_z(v, nx0, nx1, 34, ROT_Z - ROT_R + 1, 7, SLATE, SAND)

    # ================= THE MAP ROOM ROTUNDA =================
    for x in range(ROT_X - ROT_R, ROT_X + ROT_R + 1):
        for z in range(ROT_Z - ROT_R, ROT_Z + ROT_R + 1):
            if math.hypot(x - ROT_X, z - ROT_Z) <= ROT_R + 0.4:
                v.set(x, 0, z, DEEP_TILES if (x + z) % 4 == 0 else STONE)
    ring_wall(v, ROT_X, ROT_Z, ROT_R, 1, UP_Y, warm,
              gaps=[(0, 11), (90, 11), (180, 11), (270, 11)])
    for ang in (45, 135, 225, 315):
        px = ROT_X + round(math.cos(math.radians(ang)) * ROT_R)
        pz = ROT_Z + round(math.sin(math.radians(ang)) * ROT_R)
        for y in range(1, UP_Y):
            v.set(px, y, pz, DARKLOG)
        v.set(px, 4, pz, GLASS)
        v.set(px, 5, pz, GLASS)
    ring_wall(v, ROT_X, ROT_Z, ROT_R, UP_Y, UP_Y + 1, warm)
    dome(v, ROT_X, ROT_Z, ROT_R, UP_Y + 1, SAND_SMOOTH, ring_mat=SLATE,
         oculus="minecraft:sea_lantern")
    v.set(ROT_X, UP_Y, ROT_Z, "minecraft:sea_lantern")

    # ---- the breathing relief Map of Albion at the heart ----
    for x in range(ROT_X - 4, ROT_X + 5):
        for z in range(ROT_Z - 4, ROT_Z + 5):
            d = math.hypot(x - ROT_X, z - ROT_Z)
            if d <= 4.3:
                v.set(x, 1, z, DARKOAK)
            if d <= 3.4:
                roll = r.random()
                v.set(x, 2, z,
                      "minecraft:lapis_block" if roll < 0.34 else
                      "minecraft:moss_block" if roll < 0.62 else
                      "minecraft:sand" if roll < 0.74 else
                      "minecraft:emerald_block" if roll < 0.9 else GOLD)
    v.set(ROT_X, 3, ROT_Z, "minecraft:sea_lantern")
    v.set(ROT_X, 4, ROT_Z, "minecraft:end_rod")
    v.set(AX, 1, QUEST_Z, "minecraft:lectern", {"minecraft:cardinal_direction": "north"})
    v.set(AX - 4, 2, QUEST_Z, CANDLE, {"lit": True, "candles": 2})
    v.set(AX + 4, 2, QUEST_Z, CANDLE, {"lit": True, "candles": 2})
    for ang in range(0, 360, 60):
        bx = ROT_X + round(math.cos(math.radians(ang)) * (ROT_R - 2))
        bz = ROT_Z + round(math.sin(math.radians(ang)) * (ROT_R - 2))
        if abs(bx - AX) <= 1 and bz < ROT_Z:
            continue
        v.set(bx, 1, bz, SAND_CHIS)
        v.set(bx, 2, bz, "minecraft:campfire")
    for z in range(ROT_Z - ROT_R + 1, ROT_Z + ROT_R):
        for x in (AX - 1, AX, AX + 1):
            if math.hypot(x - ROT_X, z - ROT_Z) <= ROT_R - 0.6:
                v.set(x, 0, z, RED)
    for ang, col in ((20, "minecraft:red_wool"), (160, "minecraft:brown_wool"),
                     (200, "minecraft:black_wool"), (340, "minecraft:red_wool")):
        px = ROT_X + round(math.cos(math.radians(ang)) * (ROT_R - 1))
        pz = ROT_Z + round(math.sin(math.radians(ang)) * (ROT_R - 1))
        for y in (5, 6, 7):
            v.set(px, y, pz, col)

    # ---- grand staircase up to a railed balcony overlooking the map ----
    for i in range(1, UP_Y):
        sz = ROT_Z - 6 + i
        v.set(ROT_X - 6, i, sz, SBRICK_STAIR, {"weirdo_direction": 2, "upside_down_bit": False})
        v.set(ROT_X - 6, i - 1, sz, STONE)
    for x in range(ROT_X - 7, ROT_X - 1):
        for z in range(ROT_Z - 1, ROT_Z + 4):
            if math.hypot(x - ROT_X, z - ROT_Z) <= ROT_R - 1.4:
                v.set(x, UP_Y, z, SPRUCE)
    for z in range(ROT_Z - 1, ROT_Z + 4):
        v.set(ROT_X - 2, UP_Y + 1, z, DARKOAK_FENCE)
    v.set(ROT_X - 5, UP_Y + 1, ROT_Z + 3, LANTERN, {"hanging": True})

    # ================= CULLIS GATE (left/west alcove) =================
    for x in range(CGX - 3, CGX + 4):
        for z in range(CGZ - 4, CGZ + 5):
            for y in range(1, 7):
                if x in (CGX - 3, CGX + 3) or z in (CGZ - 4, CGZ + 4):
                    v.set(x, y, z, warm())
    gable_roof_z(v, CGX - 3, CGX + 3, CGZ - 4, CGZ + 4, 6, SLATE, SAND)
    v.fill(CGX + 3, 1, CGZ - 1, CGX + 3, 4, CGZ + 1, "minecraft:air")  # link to rotunda
    for x in range(CGX - 2, CGX + 3):
        for z in range(CGZ - 3, CGZ + 4):
            d = math.hypot(x - CGX, z - CGZ)
            if d <= 3.3:
                v.set(x, 0, z, CHISELED if (x + z) % 2 else DEEP_TILES)
            if 2.3 < d <= 3.3:
                v.set(x, 1, z, OBSIDIAN if (x + z) % 3 else "minecraft:crying_obsidian")
    for ang in range(0, 360, 45):
        px = CGX + round(math.cos(math.radians(ang)) * 2)
        pz = CGZ + round(math.sin(math.radians(ang)) * 2)
        v.set(px, 1, pz, "minecraft:sea_lantern" if ang % 90 == 0 else QUARTZ)
    v.set(CGX, 1, CGZ, "minecraft:beacon")
    for ang in range(45, 360, 90):
        px = CGX + round(math.cos(math.radians(ang)) * 3)
        pz = CGZ + round(math.sin(math.radians(ang)) * 3)
        for y in range(1, 4):
            v.set(px, y, pz, OBSIDIAN if y < 3 else "minecraft:crying_obsidian")
        v.set(px, 4, pz, "minecraft:amethyst_cluster")

    # ================= SKILL / EXPERIENCE green portal (right/east) =========
    for x in range(SKX - 3, SKX + 4):
        for z in range(SKZ - 4, SKZ + 5):
            for y in range(1, 7):
                if x in (SKX - 3, SKX + 3) or z in (SKZ - 4, SKZ + 4):
                    v.set(x, y, z, warm())
    gable_roof_z(v, SKX - 3, SKX + 3, SKZ - 4, SKZ + 4, 6, SLATE, SAND)
    v.fill(SKX - 3, 1, SKZ - 1, SKX - 3, 4, SKZ + 1, "minecraft:air")  # link to rotunda
    for x in range(SKX - 2, SKX + 3):
        for z in range(SKZ - 3, SKZ + 4):
            v.set(x, 0, z, CHISELED if (x + z) % 2 else DEEP_TILES)
    # the glowing green portal arch on the east face
    for y in range(1, 5):
        v.set(SKX - 1, y, SKZ + 3, SAND_CHIS)
        v.set(SKX + 1, y, SKZ + 3, SAND_CHIS)
    for x in range(SKX - 1, SKX + 2):
        v.set(x, 5, SKZ + 3, SAND_CHIS)
    for x in range(SKX, SKX + 1):
        for y in (1, 2, 3, 4):
            v.set(x, y, SKZ + 3, "minecraft:green_stained_glass")
    v.set(SKX, 1, SKZ + 4, "minecraft:sea_lantern")
    v.set(SKX, 1, SKZ, "minecraft:smooth_quartz")
    v.set(SKX, 2, SKZ, "minecraft:enchanting_table")
    for ang in range(0, 360, 90):
        px = SKX + round(math.cos(math.radians(ang)) * 2)
        pz = SKZ + round(math.sin(math.radians(ang)) * 2)
        v.set(px, 1, pz, "minecraft:amethyst_block")
        v.set(px, 2, pz, CANDLE, {"lit": True, "candles": 3})
    v.set(SKX, 3, SKZ + 2, "minecraft:glowstone")

    # ================= DINING HALL (east) =================
    dx0, dx1, dz0, dz1 = 50, 70, 30, 57
    dwall = 7
    for x in range(dx0, dx1 + 1):
        for z in range(dz0, dz1 + 1):
            v.set(x, 0, z, SAND if (x + z) % 3 else STONE)
    for x in range(dx0, dx1 + 1):
        for z in (dz0, dz1):
            for y in range(1, dwall):
                v.set(x, y, z, warm())
    for z in range(dz0, dz1 + 1):
        for x in (dx0, dx1):
            for y in range(1, dwall):
                v.set(x, y, z, warm())
    for z in range(dz0 + 3, dz1, 4):
        v.set(dx1, 3, z, GLASS)
        v.set(dx1, 4, z, GLASS)
    # ---- SECOND STOREY: the Dining Hall is two floors (a galleried dormitory
    #      over the feast-hall), reached by a spiral stair in the SW corner ----
    UPPER = dwall                          # 7 — the upper-floor deck level
    for x in range(dx0 + 1, dx1):
        for z in range(dz0 + 1, dz1):
            v.set(x, UPPER, z, SPRUCE if (x + z) % 5 else DARKOAK)
    for x in range(dx0, dx1 + 1):
        for z in (dz0, dz1):
            for y in range(UPPER + 1, UPPER + 6):
                v.set(x, y, z, warm())
    for z in range(dz0, dz1 + 1):
        for x in (dx0, dx1):
            for y in range(UPPER + 1, UPPER + 6):
                v.set(x, y, z, warm())
    for z in range(dz0 + 3, dz1, 4):       # clerestory windows upstairs
        v.set(dx0, UPPER + 3, z, GLASS)
        v.set(dx1, UPPER + 3, z, GLASS)
    spiral_stair(v, dx0 + 3, dz1 - 3, 2, 1, UPPER, SPRUCE_STAIR, post=DARKLOG,
                 steps_per_rev=12)
    v.fill(dx0 + 1, UPPER, dz1 - 5, dx0 + 5, UPPER, dz1 - 1, "minecraft:air")  # stairwell
    # upstairs dormitory beds + reading nooks down both long walls
    for bz in range(dz0 + 4, dz1 - 3, 4):
        v.set(dx0 + 2, UPPER + 1, bz, "minecraft:bed", {"direction": 1})
        v.set(dx0 + 3, UPPER + 1, bz, "minecraft:bed", {"direction": 1, "head_piece_bit": True})
        v.set(dx0 + 2, UPPER + 1, bz + 1, "minecraft:chest", {"minecraft:cardinal_direction": "south"})
        v.set(dx1 - 2, UPPER + 1, bz, "minecraft:bed", {"direction": 3})
        v.set(dx1 - 3, UPPER + 1, bz, "minecraft:bed", {"direction": 3, "head_piece_bit": True})
        v.set(dx1 - 5, UPPER + 1, bz, "minecraft:bookshelf")
    v.set(dx0 + 7, UPPER + 4, (dz0 + dz1) // 2, LANTERN, {"hanging": True})
    v.set(dx1 - 7, UPPER + 4, (dz0 + dz1) // 2, LANTERN, {"hanging": True})
    hip_roof(v, dx0, dx1, dz0, dz1, UPPER + 6, SLATE, levels=4, cap=DEEP_TILES)
    for tz in (dz0 + 9, dz0 + 16):
        long_table(v, dx0 + 5, dx1 - 4, tz, 2)
        for x in range(dx0 + 5, dx1 - 3, 2):
            v.set(x, 1, tz - 1, OAK_STAIR, {"weirdo_direction": 2, "upside_down_bit": False})
            v.set(x, 1, tz + 1, OAK_STAIR, {"weirdo_direction": 3, "upside_down_bit": False})
    hx = dx1 - 1
    hzc = (dz0 + dz1) // 2
    for z in (hzc - 1, hzc, hzc + 1):
        v.set(hx, 1, z, BRICK)
        v.set(hx, 2, z, BRICK)
    v.set(hx, 1, hzc, "minecraft:campfire")
    v.set(hx, 2, hzc, "minecraft:magma")
    for y in range(3, dwall + 4):
        v.set(hx, y, hzc, BRICK)
    v.set(dx1 - 2, 3, hzc, "minecraft:black_wool")
    for x in range(dx0 + 3, dx0 + 9):
        v.set(x, 1, dz0 + 2, SPRUCE_STAIR, {"weirdo_direction": 2, "upside_down_bit": False})
        v.set(x, 1, dz0 + 3, "minecraft:barrel")
    v.set(dx0 + 4, 2, dz0 + 4, "minecraft:brown_wool")
    v.set(dx0 + 6, 2, dz0 + 4, "minecraft:white_wool")
    for z in range(dz0 + 4, dz1 - 1, 5):
        v.set(dx0 + 10, dwall - 1, z, LANTERN, {"hanging": True})
        v.set(dx1 - 6, dwall - 1, z, LANTERN, {"hanging": True})

    # ---- dress the Dining Hall: from bland sandstone box to a feast-hall ----
    daisle = (dx0 + dx1) // 2
    for x in range(dx0 + 2, dx1 - 1):              # crimson runner, door to hearth
        v.set(x, 1, hzc, "minecraft:red_carpet")
    # harvest tapestries (muted ochre / forest-green / rust) on the end walls
    cloths = ["minecraft:brown_wool", "minecraft:green_wool", "minecraft:red_wool"]
    for wall_z in (dz0, dz1):
        for i, x in enumerate(range(dx0 + 4, dx1 - 3, 5)):
            col = cloths[i % len(cloths)]
            v.set(x, 5, wall_z, DARKLOG)
            v.set(x, 4, wall_z, col)
            v.set(x, 3, wall_z, col)
            v.set(x, 2, wall_z, DARKLOG)
    # iron chandeliers and a laden feast over the two long tables
    for tz in (dz0 + 9, dz0 + 16):
        for cxp in (daisle - 4, daisle + 4):
            v.set(cxp, dwall - 1, tz, "minecraft:chain")
            v.set(cxp, dwall - 2, tz, LANTERN, {"hanging": True})
        v.set(dx0 + 7, 3, tz, "minecraft:cake")
        v.set(dx0 + 12, 3, tz, CANDLE, {"lit": True, "candles": 2})
        v.set(dx1 - 7, 3, tz, "minecraft:cake")
    # mantel trophies over the great hearth (bleached bones, a hung lantern)
    v.set(dx1 - 2, 4, hzc - 1, "minecraft:bone_block")
    v.set(dx1 - 2, 3, hzc + 1, "minecraft:lantern", {"hanging": False})
    v.set(dx1 - 2, 5, hzc, "minecraft:chain")

    # ================= LIBRARY ARCANUM (north, two storeys + dome) =========
    lx0, lx1, lz0, lz1 = 18, 50, 55, 75
    for x in range(lx0, lx1 + 1):
        for z in range(lz0, lz1 + 1):
            v.set(x, 0, z, DARKOAK if (x + z) % 4 else SPRUCE)
    for x in range(lx0, lx1 + 1):
        for z in (lz0, lz1):
            for y in range(1, 13):
                v.set(x, y, z, warm())
    for z in range(lz0, lz1 + 1):
        for x in (lx0, lx1):
            for y in range(1, 13):
                v.set(x, y, z, warm())
    for z in range(lz0 + 2, lz1 - 1):
        if z % 2:
            for y in range(1, 12):
                if y not in (6, 7):
                    v.set(lx0 + 1, y, z, "minecraft:bookshelf")
                    v.set(lx1 - 1, y, z, "minecraft:bookshelf")
    # the upper gallery floor (with a central light well) + rail
    for x in range(lx0 + 1, lx1):
        for z in range(lz0 + 1, lz1):
            if not (lx0 + 6 < x < lx1 - 6 and lz0 + 5 < z < lz1 - 5):
                v.set(x, 7, z, SPRUCE)
    for x in range(lx0 + 6, lx1 - 5):
        v.set(x, 8, lz0 + 5, DARKOAK_FENCE)
        v.set(x, 8, lz1 - 6, DARKOAK_FENCE)
    for z in range(lz0 + 5, lz1 - 5):
        v.set(lx0 + 6, 8, z, DARKOAK_FENCE)
        v.set(lx1 - 6, 8, z, DARKOAK_FENCE)
    # flat slate roof over the library, leaving the central dome open
    lcx, lcz = (lx0 + lx1) // 2, (lz0 + lz1) // 2
    for x in range(lx0, lx1 + 1):
        for z in range(lz0, lz1 + 1):
            if math.hypot(x - lcx, z - lcz) > 6.5:
                v.set(x, 12, z, SLATE if (x + z) % 2 else DEEP_TILES)
    dome(v, lcx, lcz, 6, 12, DARKLOG, ring_mat=GLASS,
         oculus="minecraft:sea_lantern")
    # spiral stair to the gallery + reading lecterns + oil lamps
    spiral_stair(v, lx0 + 4, lz1 - 4, 2, 1, 7, SPRUCE_STAIR, post=DARKLOG,
                 steps_per_rev=12)
    v.fill(lx0 + 2, 7, lz1 - 6, lx0 + 6, 7, lz1 - 2, "minecraft:air")  # stairwell hole
    for i, z in enumerate(range(lz0 + 4, lz1 - 3, 4)):
        v.set(lx0 + 9, 1, z, "minecraft:lectern",
              {"minecraft:cardinal_direction": "east" if i % 2 else "west"})
        v.set(lx1 - 9, 1, z, "minecraft:lectern",
              {"minecraft:cardinal_direction": "west" if i % 2 else "east"})
        v.set(AX, 6, z, LANTERN, {"hanging": True})
    v.set(AX, 1, lz0 + 3, "minecraft:lectern", {"minecraft:cardinal_direction": "north"})
    v.set(AX - 1, 1, lz0 + 3, CANDLE, {"lit": True, "candles": 1})
    # the iron Guild-Cave door at the north end into a rough-hewn pit
    cvx = AX
    v.fill(cvx - 1, 1, lz1, cvx + 1, 4, lz1, "minecraft:air")
    for x in range(cvx - 2, cvx + 3):
        for z in range(lz1 + 1, lz1 + 5):
            v.set(x, 0, z, COBBLE if r.random() < 0.6 else MCOBBLE)
            for y in range(1, 5):
                if x in (cvx - 2, cvx + 2) or z == lz1 + 4:
                    v.set(x, y, z, COBBLE if r.random() < 0.7 else MCOBBLE)
    for y in (1, 2, 3):
        v.set(cvx, y, lz1, "minecraft:iron_bars")
    for y in range(0, 4):
        v.set(cvx, y, lz1 + 3, "minecraft:ladder", {"facing_direction": 2})
    v.set(cvx - 2, 4, lz1 + 2, SOUL_LANTERN)

    # ---- dormitory cells lining the library gallery ----
    for k in range(3):
        cz0 = lz0 + 2 + k * 6
        cz1 = cz0 + 4
        for x in range(lx0 + 1, lx0 + 8):
            for z in (cz0, cz1):
                for y in range(8, 12):
                    v.set(x, y, z, warm())
        for z in range(cz0, cz1 + 1):
            v.set(lx0 + 7, 8, z, warm())
            v.set(lx0 + 7, 9, z, warm())
        v.fill(lx0 + 7, 8, cz0 + 2, lx0 + 7, 9, cz0 + 2, "minecraft:air")  # doorway
        v.set(lx0 + 2, 8, cz0 + 1, "minecraft:bed", {"direction": 3})
        v.set(lx0 + 3, 8, cz0 + 1, "minecraft:bed", {"direction": 3, "head_piece_bit": True})
        v.set(lx0 + 2, 8, cz1 - 1, "minecraft:chest", {"minecraft:cardinal_direction": "south"})
        v.set(lx0 + 5, 9, cz0, "minecraft:bookshelf")
        v.set(lx0 + 6, 9, cz1, "minecraft:torch")

    # ================= MAZE'S TOWER (south spire, moated, spiral stair) =====
    # the tower stands on an island with "water all around" — a still pond rings
    # it, broken only by the covered corridor that reaches it from the north.
    for x in range(TWR_X - 11, TWR_X + 12):
        for z in range(TWR_Z - 11, TWR_Z + 12):
            if not (0 <= x < W and 0 <= z < L):
                continue
            d = math.hypot(x - TWR_X, z - TWR_Z)
            corridor = abs(x - TWR_X) <= 1 and z < TWR_Z   # keep the north approach dry
            if TWR_R + 0.4 < d <= 10.2 and not corridor:
                v.set(x, 0, z, "minecraft:water")
                v.fill(x, 1, z, x, 3, z, "minecraft:air")
            elif d <= TWR_R + 0.4:
                v.set(x, 0, z, MCOBBLE if r.random() < 0.4 else COBBLE)   # island shore
    # a little reed island with a scarecrow out in the pond (lore)
    isx, isz = TWR_X + 8, TWR_Z + 6
    for x in range(isx - 1, isx + 2):
        for z in range(isz - 1, isz + 2):
            if 0 <= x < W and 0 <= z < L:
                v.set(x, 0, z, "minecraft:grass_block")
    v.set(isx, 1, isz, "minecraft:oak_fence")
    v.set(isx, 2, isz, "minecraft:hay_block")
    v.set(isx, 3, isz, "minecraft:carved_pumpkin", {"minecraft:cardinal_direction": "north"})
    cylinder(v, TWR_X, TWR_Z, TWR_R, 0, 0, DEEP_TILES, fill_mat=DEEP_TILES)
    ring_wall(v, TWR_X, TWR_Z, TWR_R, 1, STUDY_Y + 4, warm, gaps=[(270, 14)])
    for ang in range(0, 360, 45):
        wx_ = TWR_X + round(math.cos(math.radians(ang)) * TWR_R)
        wz_ = TWR_Z + round(math.sin(math.radians(ang)) * TWR_R)
        v.set(wx_, 5, wz_, GLASS)
        v.set(wx_, STUDY_Y + 2, wz_, GLASS)
    sp = spiral_stair(v, TWR_X, TWR_Z, 2, 1, STUDY_Y, SBRICK_STAIR,
                      post="minecraft:chiseled_stone_bricks", steps_per_rev=12)
    top_x, _, top_z = sp[-1]
    stairwell = {(t[0], t[2]) for t in sp[-3:]}   # keep the stair head open
    for x in range(TWR_X - TWR_R, TWR_X + TWR_R + 1):
        for z in range(TWR_Z - TWR_R, TWR_Z + TWR_R + 1):
            if math.hypot(x - TWR_X, z - TWR_Z) < TWR_R - 0.6 and (x, z) not in stairwell:
                v.set(x, STUDY_Y, z, SPRUCE)
    for ang in range(0, 360, 36):
        bx = TWR_X + round(math.cos(math.radians(ang)) * (TWR_R - 1))
        bz = TWR_Z + round(math.sin(math.radians(ang)) * (TWR_R - 1))
        if (bx, bz) == (top_x, top_z):
            continue
        v.set(bx, STUDY_Y + 1, bz, "minecraft:bookshelf")
        v.set(bx, STUDY_Y + 2, bz, "minecraft:bookshelf")
    v.set(TWR_X - 2, STUDY_Y + 1, TWR_Z, "minecraft:lectern",
          {"minecraft:cardinal_direction": "east"})
    v.set(TWR_X + 2, STUDY_Y + 1, TWR_Z, "minecraft:enchanting_table")
    v.set(TWR_X, STUDY_Y + 1, TWR_Z, "minecraft:smithing_table")
    v.set(TWR_X + 1, STUDY_Y + 1, TWR_Z - 2, "minecraft:amethyst_cluster")
    v.set(TWR_X - 1, STUDY_Y + 1, TWR_Z + 2, "minecraft:amethyst_cluster")
    # Maze's cot on the quiet west side, clear of the spiral's stair head
    v.set(TWR_X - 3, STUDY_Y + 1, TWR_Z - 2, "minecraft:purple_bed", {"direction": 1})
    v.set(TWR_X - 2, STUDY_Y + 1, TWR_Z - 2, "minecraft:purple_bed",
          {"direction": 1, "head_piece_bit": True})
    v.set(TWR_X, STUDY_Y + 2, TWR_Z, "minecraft:sea_lantern")
    cone_roof(v, TWR_X, TWR_Z, TWR_R + 1, STUDY_Y + 4, SLATE, tip="minecraft:end_rod")
    # ---- covered stone corridor: Dining Hall (north) down to the tower door,
    #      enclosed on its exterior (east) flank, railed and open toward the
    #      grounds on the west — "stone corridor, enclosed only exterior side"
    v.fill(TWR_X, 1, dz1, TWR_X, 3, dz1, "minecraft:air")     # door out of the Dining Hall
    for z in range(dz1, TWR_Z - TWR_R + 1):                    # 57 .. 79
        for x in (TWR_X - 1, TWR_X, TWR_X + 1):
            v.set(x, 0, z, STONE if (x + z) % 2 else DEEP_TILES)   # deck over the moat
            v.fill(x, 1, z, x, 4, z, "minecraft:air")
            v.set(x, 5, z, SLATE if z % 2 else DEEP_TILES)         # flat roof
        for y in range(1, 5):
            v.set(TWR_X + 1, y, z, warm())          # enclosed exterior (east) wall
        v.set(TWR_X - 1, 1, z, SAND_WALL)           # open rail toward the grounds (west)
    for z in range(dz1 + 1, TWR_Z - TWR_R, 3):
        v.set(TWR_X, 4, z, LANTERN, {"hanging": True})

    # ============= EAST TRAINING GROUNDS (across the stream) ==============
    # the Dueling Ring — a kerbed sawdust sparring circle with straw dummies,
    # reached straight off the central bridge (z 44)
    drx, drz, drr = 85, 42, 5
    for x in range(drx - drr, drx + drr + 1):
        for z in range(drz - drr, drz + drr + 1):
            d = math.hypot(x - drx, z - drz)
            if d <= drr + 0.3:
                v.set(x, 0, z, "minecraft:coarse_dirt" if r.random() < 0.65 else GRAVEL)
            if drr - 0.7 < d <= drr + 0.3:
                v.set(x, 1, z, DARKOAK_FENCE)
    v.set(drx - drr, 1, drz, "minecraft:air")            # gate facing the bridge
    for dmx, dmz in ((drx - 2, drz - 2), (drx + 2, drz + 2), (drx + 2, drz - 2)):
        v.set(dmx, 1, dmz, "minecraft:hay_block")
        v.set(dmx, 2, dmz, "minecraft:hay_block")
        v.set(dmx, 3, dmz, "minecraft:carved_pumpkin", {"minecraft:cardinal_direction": "west"})
    v.set(drx, 1, drz + drr + 1, "minecraft:lectern", {"minecraft:cardinal_direction": "south"})

    # the Archery Range — a railed lane with a covered shooting stand to the west
    # and a row of straw-backed targets along the east butt (z 54-74)
    arx0, arx1, arz0, arz1 = 81, 90, 54, 74
    for x in range(arx0, arx1 + 1):
        for z in range(arz0, arz1 + 1):
            v.set(x, 0, z, "minecraft:coarse_dirt" if (x + z) % 3 else GRAVEL)
    for x in range(arx0, arx1 + 1):
        v.set(x, 1, arz0, DARKOAK_FENCE)
        v.set(x, 1, arz1, DARKOAK_FENCE)
    for z in range(arz0, arz1 + 1):
        v.set(arx1, 1, z, DARKOAK_FENCE)
    for z in range(arz0 + 2, arz1 - 1, 3):               # straw-backed targets
        v.set(arx1 - 1, 1, z, "minecraft:hay_block")
        v.set(arx1 - 1, 2, z, "minecraft:target")
        v.set(arx1 - 1, 3, z, "minecraft:target")
    # covered shooting stand along the west edge (open toward the targets)
    for z in range(arz0, arz1 + 1):
        for x in (arx0, arx0 + 1):
            v.set(x, 5, z, SLATE if (x + z) % 2 else DARKOAK)   # lean-to roof
    for z in (arz0, (arz0 + arz1) // 2, arz1):
        for y in range(1, 5):
            v.set(arx0, y, z, SPRUCE_LOG)                # roof posts
    for z in range(arz0 + 1, arz1):
        v.set(arx0 + 1, 1, z, SPRUCE_STAIR, {"weirdo_direction": 0, "upside_down_bit": False})  # bench
    v.set(arx0 + 1, 4, (arz0 + arz1) // 2, LANTERN, {"hanging": True})
    v.set(arx0 + 2, 1, arz0 + 1, "minecraft:barrel")
    v.set(arx0 + 2, 2, arz0 + 1, "minecraft:fletching_table")
    v.set(arx0 + 2, 1, arz1 - 1, "minecraft:chest", {"minecraft:cardinal_direction": "north"})

    # ================= DEMON-DOOR PLAZA (SE corner) =================
    px0, px1, pz0, pz1 = 80, 90, 11, 28
    fcx = (px0 + px1) // 2
    # a worn flagstone plaza (full blocks → dead level) with a moss-grown
    # dirt approach lane leading straight to the door's mouth
    for x in range(px0, px1 + 1):
        for z in range(pz0, pz1 + 1):
            roll = r.random()
            v.set(x, 0, z, COBBLE if roll < 0.45 else
                  (MCOBBLE if roll < 0.68 else (STONE if roll < 0.86 else MOSSY)))
    for z in range(pz0, pz1 - 2):
        for x in range(fcx - 1, fcx + 2):
            v.set(x, 0, z, PATH)
    for z in range(pz1 - 3, pz1 + 1):
        t = (z - (pz1 - 3)) / 3
        for x in range(px0, px1 + 1):
            h = int(4 + t * 5) - max(0, (abs(x - fcx) - 3))
            for y in range(1, max(1, h)):
                roll = r.random()
                v.set(x, y, z, STONE if roll < 0.4 else
                      (MOSSY if roll < 0.62 else (CRACK if roll < 0.8 else COBBLE)))
    v.fill(fcx - 1, 1, pz1 - 3, fcx + 1, 5, pz1 - 2, "minecraft:air")
    for y in range(1, 6):
        v.set(fcx - 2, y, pz1 - 3, CHISELED)
        v.set(fcx + 2, y, pz1 - 3, CHISELED)
    for x in range(fcx - 2, fcx + 3):
        v.set(x, 6, pz1 - 3, CHISELED)
    v.set(fcx, 6, pz1 - 3, "minecraft:chiseled_deepslate")
    v.set(fcx - 1, 3, pz1 - 3, SOUL_LANTERN)
    v.set(fcx + 1, 3, pz1 - 3, SOUL_LANTERN)
    for mx in (px0 + 1, px1 - 1):
        for y in range(1, 4):
            v.set(mx, y, pz0 + 2, OBSIDIAN if y < 3 else "minecraft:crying_obsidian")
        v.set(mx, 4, pz0 + 2, SOUL_LANTERN)
    for bxp in (fcx - 4, fcx + 4):
        v.set(bxp, 1, pz1 - 5, SAND_CHIS)
        v.set(bxp, 2, pz1 - 5, "minecraft:soul_campfire")

    # ================= LIGHTING: warm every hall (no more dark rooms) =======
    # All hung from a deck/roof directly above so none float unsupported.
    def hang(x, y, z):
        v.set(x, y, z, LANTERN, {"hanging": True})
    # Guild Shop — hung from the gable
    for lxp, lzp in ((sx0 + 3, sz0 + 2), (sx1 - 3, sz1 - 2), (sx1 - 3, sz0 + 2)):
        hang(lxp, 4, lzp)
    # Library ground floor — a lantern grid beneath the gallery deck (y7)
    for xx in range(lx0 + 7, lx1 - 6, 8):
        for zz in range(lz0 + 4, lz1 - 3, 6):
            hang(xx, 6, zz)
    # Cullis & Skill alcoves (gable roofs at y6 above)
    hang(CGX, 5, CGZ - 2)
    hang(SKX, 5, SKZ - 2)
    # Dining Hall — extra lanterns hung from the upper-floor deck (y7)
    for zz in range(dz0 + 4, dz1 - 1, 6):
        hang(dx0 + 1, dwall - 1, zz)
        hang(dx1 - 1, dwall - 1, zz)

    # ================= PERIMETER: the Guild's main wall =================
    # a crenellated stone curtain rings the whole campus on the hilltop, opening
    # only at the south gatehouse; corner turrets carry lanterns.
    WALL_H = 4

    def wall_seg(x, z):
        if z <= 1 and abs(x - AX) <= 3:
            return                       # leave the south gate open
        for y in range(1, WALL_H):
            v.set(x, y, z, COBBLE if r.random() < 0.45 else STONE)
        if (x + z) % 2 == 0:
            v.set(x, WALL_H, z, SAND_WALL)   # battlements
    for x in range(1, W - 1):
        wall_seg(x, 1)
        wall_seg(x, L - 2)
    for z in range(1, L - 1):
        wall_seg(1, z)
        wall_seg(W - 2, z)
    # gate piers flanking the south opening
    for gx in (AX - 4, AX + 4):
        for y in range(1, WALL_H + 1):
            v.set(gx, y, 1, SAND_CHIS if y == WALL_H else warm())
        v.set(gx, WALL_H + 1, 1, LANTERN, {"hanging": False})
    for cx_, cz_ in ((1, 1), (W - 2, 1), (1, L - 2), (W - 2, L - 2)):
        for y in range(1, WALL_H + 2):
            v.set(cx_, y, cz_, warm() if y < WALL_H + 1 else SAND_CHIS)
        v.set(cx_, WALL_H + 2, cz_, LANTERN, {"hanging": False})

    # ================= CONNECT ROOMS: doorway thresholds =================
    v.fill(AX - 1, 1, 34, AX + 1, 4, 34, "minecraft:air")     # forecourt -> nave
    for zz in (ROT_Z - ROT_R, ROT_Z + ROT_R):
        v.fill(AX - 1, 1, zz, AX + 1, 4, zz, "minecraft:air")  # nave<->rotunda<->library
    v.fill(ROT_X - ROT_R, 1, ROT_Z - 1, ROT_X - ROT_R, 4, ROT_Z + 1, "minecraft:air")  # west -> Cullis
    v.fill(ROT_X + ROT_R, 1, ROT_Z - 1, ROT_X + ROT_R, 4, ROT_Z + 1, "minecraft:air")  # east -> Skill
    v.fill(SKX + 3, 1, SKZ - 1, dx0, 4, SKZ + 1, "minecraft:air")    # skill alcove -> dining
    v.fill(lx0, 1, lz0 + 3, lx0, 4, lz0 + 5, "minecraft:air")        # library west service door

    v.save("guild_hall")


def silver_chest_ruin():
    """A collapsed chapel: one surviving arch, broken wall fragments, fallen
    column, overgrowth — and the silver chest waiting on its dais."""
    r = rng("struct", "ruin")
    S = 13
    v = Vox(S, 8, S)
    for x in range(S):
        for z in range(S):
            roll = r.random()
            if roll < 0.55:
                v.set(x, 0, z, MCOBBLE if roll < 0.25 else COBBLE)
            elif roll < 0.7:
                v.set(x, 0, z, "minecraft:grass_block")
    # surviving gothic arch (west)
    ax = 2
    for y in range(1, 6):
        v.set(ax, y, 3, CHISELED if y > 3 else rnd_stone(r))
        v.set(ax, y, 7, CHISELED if y > 3 else rnd_stone(r))
    for z in range(3, 8):
        v.set(ax, 6, z, CHISELED)
    v.set(ax, 5, 5, "minecraft:chiseled_deepslate")  # keystone
    # broken wall fragments with ragged tops
    for z in range(2, 11):
        h = max(0, 4 - abs(z - 4) + r.randrange(-1, 2))
        for y in range(1, h + 1):
            v.set(S - 3, y, z, rnd_stone(r))
        if h > 2 and r.random() < 0.5:
            v.set(S - 3, h + 1, z, "minecraft:cobblestone_wall")
    for x in range(3, 9):
        h = r.randrange(0, 3)
        for y in range(1, h + 1):
            v.set(x, y, 2, rnd_stone(r))
    # fallen column lying across the floor
    for i in range(4):
        v.set(4 + i, 1, 9, "minecraft:quartz_pillar")
    v.set(8, 1, 9, QUARTZ)
    # rubble piles + vines
    for i in range(10):
        x, z = r.randrange(S), r.randrange(S)
        if r.random() < 0.5:
            v.set(x, 1, z, MCOBBLE if r.random() < 0.5 else "minecraft:cobblestone_wall")
    for y in range(2, 6):
        v.set(S - 3, y, 5, "minecraft:vine", {"vine_direction_bits": 8})
    # the dais: chiseled platform, candles, silver chest
    dx, dz = 6, 5
    v.fill(dx - 1, 1, dz - 1, dx + 1, 1, dz + 1, CHISELED)
    v.set(dx, 2, dz, "minecraft:chest", {"minecraft:cardinal_direction": "south"})
    v.set(dx - 1, 2, dz - 1, CANDLE, {"lit": True, "candles": 2})
    v.set(dx + 1, 2, dz + 1, CANDLE, {"lit": True})
    v.set(dx + 1, 2, dz - 1, SOUL_LANTERN)
    v.save("silver_chest_ruin")


def focus_site():
    """Focus Site: concentric obsidian rings, four rune monoliths chained in
    light, and a levitating crystal above the focus dais."""
    v = Vox(13, 10, 13)
    r = rng("struct", "focus")
    c = 6
    for x in range(13):
        for z in range(13):
            d = math.hypot(x - c, z - c)
            if d <= 5.6:
                if d <= 1.2:
                    v.set(x, 0, z, OBSIDIAN)
                elif 2.4 < d <= 3.2:
                    v.set(x, 0, z, "minecraft:crying_obsidian" if (x + z) % 2 else OBSIDIAN)
                elif 4.6 < d <= 5.6:
                    v.set(x, 0, z, CHISELED if (x + z) % 2 else STONE)
                else:
                    v.set(x, 0, z, DEEP_TILES if (x + z) % 3 else STONE)
    # four rune monoliths with glow caps
    for cx, cz in ((1, c), (11, c), (c, 1), (c, 11)):
        for y in range(1, 5):
            v.set(cx, y, cz, OBSIDIAN if y < 3 else "minecraft:crying_obsidian")
        v.set(cx, 5, cz, "minecraft:sea_lantern")
        v.set(cx, 6, cz, "minecraft:end_rod")
    # candle ring
    for ang in range(0, 360, 45):
        x = c + round(math.cos(math.radians(ang)) * 4)
        z = c + round(math.sin(math.radians(ang)) * 4)
        v.set(x, 1, z, CANDLE, {"lit": True, "candles": 1 + ang % 3})
    # central dais + levitating crystal
    v.set(c, 1, c, "minecraft:beacon")
    v.set(c, 4, c, "minecraft:amethyst_block")
    v.set(c, 5, c, "minecraft:amethyst_cluster")
    v.save("focus_site")


def power_guild_courtyard():
    """Heroes' Guild-inspired Place of Power: chalk stream crossing the court,
    twin bridges to a Will island, grave stones, training ring and a cullis
    focus circle anchored by Old Kingdom pillars."""
    r = rng("struct", "power_guild")
    W, H, D = 27, 13, 27
    v = Vox(W, H, D)
    cx, cz = W // 2, D // 2
    # base greens + paths
    for x in range(W):
        for z in range(D):
            roll = r.random()
            v.set(x, 0, z, "minecraft:grass_block" if roll < 0.66 else (PATH if roll < 0.87 else GRAVEL))
    # stream slices through the grounds (west-east)
    for x in range(2, W - 2):
        for z in range(cz - 2, cz + 3):
            edge = abs(z - cz)
            if edge == 2:
                v.set(x, 0, z, MCOBBLE if r.random() < 0.45 else STONE)
            else:
                v.set(x, 0, z, "minecraft:water")
                if r.random() < 0.12:
                    v.set(x, 1, z, "minecraft:seagrass")
    # will island in the stream
    for x in range(cx - 3, cx + 4):
        for z in range(cz - 1, cz + 2):
            v.set(x, 0, z, "minecraft:grass_block")
    # twin bridges to the island
    for bx in (cx - 6, cx + 6):
        for x in range(min(bx, cx - 3), max(bx, cx + 3) + 1):
            v.set(x, 1, cz - 1, SPRUCE)
            v.set(x, 1, cz, SPRUCE)
            v.set(x, 1, cz + 1, SPRUCE)
        for fx in (bx, cx - 3 if bx < cx else cx + 3):
            v.set(fx, 2, cz - 2, SPRUCE_FENCE)
            v.set(fx, 2, cz + 2, SPRUCE_FENCE)
            v.set(fx, 3, cz - 2, LANTERN)
            v.set(fx, 3, cz + 2, LANTERN)
    # cullis focus circle on the island
    for ang in range(0, 360, 45):
        px = cx + round(math.cos(math.radians(ang)) * 2)
        pz = cz + round(math.sin(math.radians(ang)) * 1)
        v.set(px, 1, pz, CHISELED if ang % 90 == 0 else DEEP_TILES)
    v.set(cx, 1, cz, "minecraft:beacon")
    for px, pz in ((cx - 3, cz), (cx + 3, cz), (cx, cz - 2), (cx, cz + 2)):
        for y in range(1, 5):
            v.set(px, y, pz, OBSIDIAN if y < 3 else "minecraft:crying_obsidian")
        v.set(px, 5, pz, "minecraft:end_rod")
    # melee ring + dummy
    rx, rz = 6, 7
    for x in range(rx - 3, rx + 4):
        for z in range(rz - 3, rz + 4):
            d = math.hypot(x - rx, z - rz)
            if d <= 3.3:
                v.set(x, 0, z, "minecraft:coarse_dirt" if r.random() < 0.7 else GRAVEL)
            if 2.4 < d <= 3.3:
                v.set(x, 1, z, SPRUCE_FENCE)
    v.set(rx, 1, rz, "minecraft:hay_block")
    v.set(rx, 2, rz, "minecraft:hay_block")
    v.set(rx, 3, rz, "minecraft:carved_pumpkin", {"minecraft:cardinal_direction": "south"})
    # old hero standing stones (grave markers)
    for gx, gz in ((20, 5), (22, 8), (19, 10), (23, 12), (21, 15)):
        h = 2 + r.randrange(0, 3)
        for y in range(1, h + 1):
            v.set(gx, y, gz, CHISELED if y == h else rnd_stone(r))
        if r.random() < 0.4:
            v.set(gx + 1, 1, gz, CANDLE, {"lit": True})
    # low perimeter ruins and approach path
    for x in range(W):
        for z in (0, D - 1):
            if z == 0 and abs(x - cx) <= 1:
                continue
            v.set(x, 1, z, rnd_stone(r))
    for z in range(D):
        for x in (0, W - 1):
            v.set(x, 1, z, rnd_stone(r))
    for z in range(0, 8):
        v.set(cx, 0, z, PATH)
        v.set(cx - 1, 0, z, PATH if r.random() < 0.7 else GRAVEL)
        v.set(cx + 1, 0, z, PATH if r.random() < 0.7 else GRAVEL)
    v.save("power_guild_courtyard")


def guild_armoury():
    """West annex of the Heroes' Guild: a working forge and armoury where
    apprentices temper steel and drill with practice dummies. Sits just
    west of the Great Hall, sharing its stone-brick-and-deepslate style."""
    r = rng("struct", "guild_armoury")
    W, H, D = 18, 18, 22
    v = Vox(W, H, D)
    mx = W // 2
    wall_h = 8

    # floor
    for x in range(W):
        for z in range(D):
            roll = r.random()
            v.set(x, 0, z, COBBLE if roll < 0.55 else (GRAVEL if roll < 0.75 else STONE))

    # outer walls
    for x in range(W):
        for z in (0, D - 1):
            for y in range(1, wall_h):
                v.set(x, y, z, rnd_stone(r))
    for z in range(D):
        for x in (0, W - 1):
            for y in range(1, wall_h):
                v.set(x, y, z, rnd_stone(r))

    # arrow-slit windows
    for z in range(3, D - 1, 4):
        v.set(0, 3, z, IRON_BARS)
        v.set(0, 4, z, IRON_BARS)
        v.set(W - 1, 3, z, IRON_BARS)
        v.set(W - 1, 4, z, IRON_BARS)

    # entrance on the east wall, toward the Great Hall
    ez = D // 2
    v.fill(W - 1, 1, ez - 1, W - 1, 3, ez + 1, "minecraft:air")
    for y in range(1, 5):
        v.set(W - 1, y, ez - 2, CHISELED)
        v.set(W - 1, y, ez + 2, CHISELED)
    v.set(W - 1, 4, ez - 1, LANTERN, {"hanging": True})
    v.set(W - 1, 4, ez + 1, LANTERN, {"hanging": True})

    # forge corner (NW)
    for fx, fz in ((1, 2), (2, 2)):
        v.set(fx, 1, fz, "minecraft:furnace")
    v.set(3, 1, 2, "minecraft:blast_furnace")
    v.set(1, 1, 1, "minecraft:anvil")
    v.set(2, 1, 1, COBBLE)
    v.set(3, 1, 1, COBBLE)

    # weapon racks: chest row + barrels along the south wall
    for cx_ in range(3, W - 3, 3):
        v.set(cx_, 1, D - 2, "minecraft:chest", {"minecraft:cardinal_direction": "north"})
        v.set(cx_, 1, D - 3, "minecraft:barrel")

    # sparring dummies near the entrance
    for dx_, dz_ in ((mx - 2, ez), (mx + 2, ez)):
        v.set(dx_, 1, dz_, "minecraft:hay_block")
        v.set(dx_, 2, dz_, "minecraft:hay_block")
        v.set(dx_, 3, dz_, "minecraft:target")

    # ceiling beams + hanging lanterns
    for z in range(2, D - 2, 4):
        for x in range(0, W):
            v.set(x, wall_h - 1, z, SPRUCE_LOG)
        v.set(mx, wall_h - 1, z, LANTERN, {"hanging": True})

    # stepped gable roof, ridge running along z (the long axis)
    gable_roof_z(v, 0, W - 1, 0, D - 1, wall_h, DEEP_TILES, STONE)

    v.save("guild_armoury")


def guild_scriptorium():
    """East annex of the Heroes' Guild: the Scriptorium, where apprentices of
    Will study tomes and copy maps. Mirrors the armoury across the Great
    Hall, sharing its stone-brick-and-deepslate style."""
    r = rng("struct", "guild_scriptorium")
    W, H, D = 18, 18, 22
    v = Vox(W, H, D)
    mx = W // 2
    wall_h = 8

    # checkerboard floor
    for x in range(W):
        for z in range(D):
            v.set(x, 0, z, DEEP_TILES if (x + z) % 2 == 0 else STONE)

    # outer walls
    for x in range(W):
        for z in (0, D - 1):
            for y in range(1, wall_h):
                v.set(x, y, z, rnd_stone(r))
    for z in range(D):
        for x in (0, W - 1):
            for y in range(1, wall_h):
                v.set(x, y, z, rnd_stone(r))

    # dark-oak pilasters + clerestory windows along the long walls
    for z in range(2, D - 1, 4):
        for x in (0, W - 1):
            for y in range(1, wall_h + 1):
                v.set(x, y, z, DARKLOG)
            if z + 2 < D - 1:
                for y in (3, 4, 5):
                    v.set(x, y, z + 2, GLASS)

    # entrance on the west wall, toward the Great Hall
    ez = D // 2
    v.fill(0, 1, ez - 1, 0, 3, ez + 1, "minecraft:air")
    for y in range(1, 5):
        v.set(0, y, ez - 2, CHISELED)
        v.set(0, y, ez + 2, CHISELED)
    v.set(0, 4, ez - 1, LANTERN, {"hanging": True})
    v.set(0, 4, ez + 1, LANTERN, {"hanging": True})

    # bookshelves lining the long walls
    for z in range(2, D - 2):
        if z % 3:
            for y in (1, 2, 3):
                v.set(1, y, z, "minecraft:bookshelf")
                v.set(W - 2, y, z, "minecraft:bookshelf")

    # study lecterns down the centre aisle
    for i, z in enumerate(range(4, D - 3, 6)):
        v.set(mx, 1, z, "minecraft:lectern",
              {"minecraft:cardinal_direction": "east" if i % 2 else "west"})
        v.set(mx - 1, 1, z, CANDLE, {"lit": True, "candles": (i % 4) + 1})
        v.set(mx + 1, 1, z, CANDLE, {"lit": True, "candles": (i % 4) + 1})

    # scholars' bunks in the far corner
    for i in range(2):
        z = D - 4 + i * 2
        v.set(2, 1, z, "minecraft:bed", {"direction": 1})
        v.set(3, 1, z, "minecraft:bed", {"direction": 1, "head_piece_bit": True})
    v.set(2, 1, D - 6, "minecraft:chest", {"minecraft:cardinal_direction": "east"})

    # ceiling beams + hanging lanterns
    for z in range(2, D - 2, 4):
        for x in range(0, W):
            v.set(x, wall_h - 1, z, SPRUCE_LOG)
        v.set(mx, wall_h - 1, z, LANTERN, {"hanging": True})

    # stepped gable roof with a glass skylight at the ridge
    gable_roof_z(v, 0, W - 1, 0, D - 1, wall_h, DEEP_TILES, STONE)
    for z in range(4, D - 4, 5):
        v.set(mx, H - 2, z, GLASS)

    v.save("guild_scriptorium")


def guild_sentinel_gate():
    """Outermost gate of the Heroes' Guild grounds: twin Sentinel towers,
    each crowned with a pair of ever-lit redstone lamps -- the visible face
    of the Guild's permanent warding Seal. Sits south of the training
    courtyard, aligned on the same gate axis."""
    r = rng("struct", "guild_sentinel")
    W, H, D = 27, 20, 14
    v = Vox(W, H, D)
    mx = W // 2  # 13

    # ground: stone court with a paved path through the gate
    for x in range(W):
        for z in range(D):
            v.set(x, 0, z, MCOBBLE if r.random() < 0.6 else STONE)
    for z in range(D):
        for x in range(mx - 1, mx + 2):
            v.set(x, 0, z, DEEP_TILES if (x + z) % 2 else CHISELED)

    # twin towers
    for tx0 in (1, W - 5):
        v.box(tx0, 1, 1, tx0 + 3, 14, D - 2, rnd_stone(r))
        v.fill(tx0 + 1, 1, 2, tx0 + 2, 12, D - 3, "minecraft:air")
        # crenellations + spires
        for x in range(tx0, tx0 + 4):
            for z in (1, D - 2):
                if (x + z) % 2 == 0:
                    v.set(x, 15, z, "minecraft:stone_brick_wall")
        v.set(tx0 + 1, 16, (D - 1) // 2, "minecraft:end_rod")
        v.set(tx0 + 2, 16, (D - 1) // 2, "minecraft:end_rod")
        # the Seal: 2x2 ever-lit redstone lamps set into the south face
        for x in (tx0 + 1, tx0 + 2):
            for y in (11, 12):
                v.set(x, y, 1, "minecraft:lit_redstone_lamp")
        # arrow-slit windows
        for z in (4, 8):
            v.set(tx0, 6, z, IRON_BARS)
            v.set(tx0 + 3, 6, z, IRON_BARS)

    # curtain walls linking the towers to the central gate pillars
    for xr in (range(5, mx - 3), range(mx + 4, W - 5)):
        for x in xr:
            for y in range(1, 7):
                v.set(x, y, 0, rnd_stone(r))
                v.set(x, y, D - 1, rnd_stone(r))
            v.set(x, 7, 0, "minecraft:stone_brick_wall")
            v.set(x, 7, D - 1, "minecraft:stone_brick_wall")

    # central gate: obsidian pillars framing the open passage
    for px in (mx - 4, mx + 4):
        for y in range(1, 8):
            v.set(px, y, 0, OBSIDIAN if y < 5 else "minecraft:crying_obsidian")
            v.set(px, y, D - 1, OBSIDIAN if y < 5 else "minecraft:crying_obsidian")

    # retracted portcullis grate over the passage
    for x in range(mx - 3, mx + 4):
        for z in range(D):
            v.set(x, 7, z, IRON_BARS)

    # warded lanterns glow above both faces of the gate
    v.set(mx, 8, 0, "minecraft:sea_lantern")
    v.set(mx, 8, D - 1, "minecraft:sea_lantern")
    for x in (mx - 4, mx + 4):
        v.set(x, 8, 0, SOUL_LANTERN)
        v.set(x, 8, D - 1, SOUL_LANTERN)

    v.save("guild_sentinel_gate")


def power_oakvale_quay():
    """Oakvale-inspired Place of Power: cliffside village green around a great
    tree and well, with a guarded timber quay and barns below."""
    r = rng("struct", "power_oakvale")
    W, H, D = 29, 15, 29
    v = Vox(W, H, D)
    cx = W // 2
    # terrain: village rise in north, beach/quay in south
    for x in range(W):
        for z in range(D):
            rise = 1 if z < 11 else (2 if z < 7 else 0)
            mat = "minecraft:grass_block" if z < 16 else ("minecraft:sand" if z < 24 else "minecraft:water")
            v.set(x, 0, z, mat)
            for y in range(1, rise + 1):
                v.set(x, y, z, "minecraft:dirt")
            if rise:
                v.set(x, rise + 1, z, "minecraft:grass_block")
    # central oak tree + well ring
    tx, tz, gy = cx, 8, 3
    for y in range(gy, gy + 5):
        v.set(tx, y, tz, "minecraft:oak_log")
    for ox in (-2, -1, 0, 1, 2):
        for oz in (-2, -1, 0, 1, 2):
            if abs(ox) + abs(oz) <= 3:
                v.set(tx + ox, gy + 5, tz + oz, "minecraft:oak_leaves")
    wx, wz = cx + 4, 9
    for x in range(wx - 2, wx + 3):
        for z in range(wz - 2, wz + 3):
            if x in (wx - 2, wx + 2) or z in (wz - 2, wz + 2):
                v.set(x, 3, z, COBBLE)
    v.set(wx, 2, wz, "minecraft:water")
    v.set(wx, 3, wz, "minecraft:water")
    # clustered cottages
    houses = [(6, 4, 6, 5), (18, 4, 6, 5), (11, 10, 7, 5)]
    for hx, hz, hw, hd in houses:
        for x in range(hx, hx + hw):
            for z in range(hz, hz + hd):
                v.set(x, 3, z, DARKOAK)
                for y in range(4, 7):
                    if x in (hx, hx + hw - 1) or z in (hz, hz + hd - 1):
                        v.set(x, y, z, COBBLE if r.random() < 0.6 else rnd_stone(r))
        v.fill(hx + 1, 4, hz, hx + hw - 2, 5, hz, "minecraft:air")
        gable_roof_z(v, hx - 1, hx + hw, hz, hz + hd - 1, 7, "minecraft:oak_planks", COBBLE)
        v.set(hx + 1, 4, hz + hd - 2, GLASS)
        v.set(hx + hw - 2, 4, hz + 1, GLASS)
    # steps down to quay
    for z in range(12, 18):
        v.set(cx, 2, z, COBBLE)
        v.set(cx, 1, z + 1, COBBLE)
    # timber quay and mooring posts
    for x in range(cx - 4, cx + 5):
        for z in range(20, 26):
            v.set(x, 1, z, SPRUCE)
    for px in (cx - 3, cx + 3):
        for y in range(2, 5):
            v.set(px, y, 24, SPRUCE_LOG)
        v.set(px, 5, 24, LANTERN)
    # barns and scarecrow field
    for x in range(3, 9):
        for z in range(14, 20):
            v.set(x, 2, z, "minecraft:hay_block" if (x + z) % 2 else SPRUCE)
    v.set(10, 2, 15, "minecraft:oak_fence")
    v.set(10, 3, 15, "minecraft:hay_block")
    v.set(10, 4, 15, "minecraft:carved_pumpkin", {"minecraft:cardinal_direction": "south"})
    # cullis circle near the tree, like a reclaimed old kingdom site
    gx, gz = cx, 12
    for ang in range(0, 360, 45):
        x = gx + round(math.cos(math.radians(ang)) * 2)
        z = gz + round(math.sin(math.radians(ang)) * 2)
        v.set(x, 3, z, CHISELED if ang % 90 == 0 else QUARTZ)
    v.set(gx, 3, gz, "minecraft:beacon")
    v.save("power_oakvale_quay")


def power_snowspire_oracle():
    """Northern Wastes Place of Power: Snowspire lanes leading to a colossal
    Oracle monolith face, with frozen cullis stones and shrine braziers."""
    r = rng("struct", "power_snowspire")
    W, H, D = 29, 18, 31
    v = Vox(W, H, D)
    cx = W // 2
    # packed snow field
    for x in range(W):
        for z in range(D):
            mat = "minecraft:snow_block" if r.random() < 0.82 else "minecraft:packed_ice"
            v.set(x, 0, z, mat)
            if r.random() < 0.35:
                v.set(x, 1, z, "minecraft:snow_layer")
    # village lane and small houses
    for z in range(4, 20):
        for x in range(cx - 2, cx + 3):
            v.set(x, 0, z, PATH if (x + z) % 3 else GRAVEL)
    for hx, hz in ((4, 6), (20, 7), (5, 13), (19, 14)):
        for x in range(hx, hx + 5):
            for z in range(hz, hz + 4):
                v.set(x, 1, z, COBBLE)
                for y in range(2, 5):
                    if x in (hx, hx + 4) or z in (hz, hz + 3):
                        v.set(x, y, z, DEEPSLATE_W if r.random() < 0.5 else STONE)
        gable_roof_z(v, hx - 1, hx + 5, hz, hz + 3, 5, DEEP_TILES, STONE)
        v.fill(hx + 1, 2, hz, hx + 3, 3, hz, "minecraft:air")
        v.set(hx + 2, 3, hz, SOUL_LANTERN)
    # Oracle monolith at north end
    mz0 = 22
    for x in range(cx - 6, cx + 7):
        for z in range(mz0, D - 1):
            rise = 5 + max(0, 5 - abs(x - cx))
            for y in range(1, min(H - 2, rise + (z - mz0) // 2)):
                v.set(x, y, z, DEEPSLATE_W if r.random() < 0.55 else STONE)
    # carve Oracle face relief
    face_z = mz0
    for y in range(5, 12):
        for x in range(cx - 4, cx + 5):
            v.set(x, y, face_z, "minecraft:air")
    # brow + eyes
    for x in range(cx - 4, cx + 5):
        v.set(x, 12, face_z, CHISELED)
    for ex in (cx - 2, cx + 2):
        v.set(ex, 9, face_z, "minecraft:crying_obsidian")
        v.set(ex, 8, face_z, "minecraft:sea_lantern")
    # nose + mouth
    v.set(cx, 8, face_z, CHISELED)
    v.set(cx, 7, face_z, CHISELED)
    for x in range(cx - 2, cx + 3):
        v.set(x, 6, face_z, "minecraft:deepslate_tiles")
    # cullis dais before the oracle
    gx, gz = cx, 19
    for x in range(gx - 3, gx + 4):
        for z in range(gz - 3, gz + 4):
            d = math.hypot(x - gx, z - gz)
            if d <= 3.4:
                v.set(x, 1, z, DEEPSLATE_W if (x + z) % 2 else CHISELED)
            if 2.5 < d <= 3.4:
                v.set(x, 2, z, OBSIDIAN)
    v.set(gx, 2, gz, "minecraft:beacon")
    for bx, bz in ((gx - 4, gz), (gx + 4, gz), (gx, gz - 4), (gx, gz + 4)):
        for y in range(1, 5):
            v.set(bx, y, bz, OBSIDIAN)
        v.set(bx, 5, bz, SOUL_LANTERN)
    v.save("power_snowspire_oracle")


def power_necropolis():
    """Necropolis Place of Power: collapsed old-kingdom cemetery with broken
    bridge, ruined crypt blocks, glyph pillars and a dead cullis nexus."""
    r = rng("struct", "power_necropolis")
    W, H, D = 29, 14, 29
    v = Vox(W, H, D)
    cx, cz = W // 2, D // 2
    for x in range(W):
        for z in range(D):
            roll = r.random()
            v.set(x, 0, z, "minecraft:podzol" if roll < 0.5 else (GRAVEL if roll < 0.75 else "minecraft:coarse_dirt"))
    # cracked city ring walls
    for x in range(2, W - 2):
        for z in (2, D - 3):
            h = 2 + r.randrange(0, 3)
            for y in range(1, h + 1):
                if r.random() < 0.88:
                    v.set(x, y, z, rnd_stone(r))
    for z in range(2, D - 2):
        for x in (2, W - 3):
            h = 2 + r.randrange(0, 3)
            for y in range(1, h + 1):
                if r.random() < 0.88:
                    v.set(x, y, z, rnd_stone(r))
    # ravine + broken bridge
    for x in range(cx - 6, cx + 7):
        for z in range(cz - 1, cz + 2):
            v.set(x, 0, z, "minecraft:air")
            v.set(x, 1, z, "minecraft:air")
    for x in range(cx - 6, cx - 1):
        v.set(x, 1, cz, COBBLE)
    for x in range(cx + 2, cx + 7):
        v.set(x, 1, cz, COBBLE)
    for x in (cx - 1, cx + 1):
        v.set(x, 2, cz, "minecraft:cobblestone_wall")
    # glyph pillars (Inquiry stones)
    for gx, gz in ((7, 8), (21, 8), (8, 21), (21, 21)):
        for y in range(1, 6):
            v.set(gx, y, gz, OBSIDIAN if y < 4 else "minecraft:crying_obsidian")
        v.set(gx, 6, gz, "minecraft:chiseled_deepslate")
        v.set(gx, 7, gz, SOUL_LANTERN)
    # dead cullis nexus
    for ang in range(0, 360, 30):
        px = cx + round(math.cos(math.radians(ang)) * 4)
        pz = cz + round(math.sin(math.radians(ang)) * 4)
        v.set(px, 1, pz, CHISELED if ang % 60 == 0 else STONE)
        if ang % 60 == 0:
            v.set(px, 2, pz, "minecraft:soul_torch")
    v.set(cx, 1, cz, "minecraft:beacon")
    v.set(cx, 2, cz, "minecraft:chiseled_deepslate")
    # crypt fragments + graves
    for hx, hz in ((5, 5), (20, 5), (6, 19), (19, 19), (13, 6), (14, 22)):
        v.set(hx, 1, hz, CRACK)
        v.set(hx, 2, hz, "minecraft:cobblestone_wall")
        if r.random() < 0.35:
            v.set(hx + 1, 1, hz, CANDLE, {"lit": True})
    for t in ((4, 13), (24, 12), (12, 25)):
        tx, tz = t
        h = 3 + r.randrange(0, 3)
        for y in range(1, h + 1):
            v.set(tx, y, tz, DARKLOG)
        v.set(tx, h + 1, tz, "minecraft:dark_oak_fence")
    v.save("power_necropolis")


def bandit_camp():
    """Twinblade's war-camp: a 33-block double-staked palisade ring, skull
    totem gate, TWO watchtowers, the Bandit King's great red pavilion on a
    raised platform, crew tents, spit-roast fire, supply dump, prisoner cage,
    war banners and loot chests."""
    r = rng("struct", "camp")
    S = 33
    v = Vox(S, 13, S)
    cx = cz = S // 2
    RAD = 15
    # trampled ground
    for x in range(S):
        for z in range(S):
            d = math.hypot(x - cx, z - cz)
            if d < RAD + 0.8:
                roll = r.random()
                v.set(x, 0, z, "minecraft:coarse_dirt" if roll < 0.5 else
                      (PATH if roll < 0.8 else GRAVEL))
    # ring palisade, gate to the south (+z)
    for ang in range(0, 360, 2):
        x = cx + round(math.cos(math.radians(ang)) * RAD)
        z = cz + round(math.sin(math.radians(ang)) * RAD)
        if 0 <= x < S and 0 <= z < S:
            if 78 <= ang <= 102:
                continue  # gate gap
            h = 4 + (1 if ang % 8 < 4 else 0)
            for y in range(1, h + 1):
                v.set(x, y, z, SPRUCE_LOG)
            v.set(x, h + 1, z, SPRUCE_FENCE)
            # second inner stake row for heft
            if ang % 6 < 3:
                ix = cx + round(math.cos(math.radians(ang)) * (RAD - 1))
                iz = cz + round(math.sin(math.radians(ang)) * (RAD - 1))
                for y in range(1, 4):
                    v.set(ix, y, iz, STRIPPED_SPRUCE)
    # gate: posts, lintel, skull totems, lanterns
    gz = cz + RAD
    gx0, gx1 = cx - 3, cx + 3
    for y in range(1, 6):
        v.set(gx0, y, gz, STRIPPED_SPRUCE)
        v.set(gx1, y, gz, STRIPPED_SPRUCE)
    for x in range(gx0, gx1 + 1):
        v.set(x, 6, gz, STRIPPED_SPRUCE)
    v.set(gx0, 6, gz, "minecraft:chiseled_deepslate")   # skull totems
    v.set(gx1, 6, gz, "minecraft:chiseled_deepslate")
    v.set(gx0 + 1, 5, gz, LANTERN, {"hanging": True})
    v.set(gx1 - 1, 5, gz, LANTERN, {"hanging": True})
    # ==== TWINBLADE'S GREAT PAVILION (north, raised platform) ====
    px0, pz0 = cx - 6, cz - RAD + 3
    for x in range(px0 - 1, px0 + 13):       # platform
        for z in range(pz0 - 1, pz0 + 9):
            v.set(x, 0, z, SPRUCE)
    half = 6
    for i in range(half + 1):                # big red marquee, front open
        for z in range(pz0, pz0 + 8):
            v.set(px0 + i, 1 + i, z, "minecraft:red_wool")
            v.set(px0 + 12 - i, 1 + i, z, "minecraft:red_wool")
    for i in range(half):                     # close back wall
        for x in range(px0 + i + 1, px0 + 12 - i):
            v.set(x, 1 + i, pz0 + 7, "minecraft:red_wool")
    # black trim stripe along the eaves
    for z in range(pz0, pz0 + 8):
        v.set(px0 + 1, 2, z, "minecraft:black_wool")
        v.set(px0 + 11, 2, z, "minecraft:black_wool")
    # throne of the Bandit King: stair throne + gold + war chest
    tx, tz = px0 + 6, pz0 + 5
    v.set(tx, 1, tz, GOLD)
    v.set(tx, 2, tz, "minecraft:red_wool")
    v.set(tx - 1, 1, tz, SPRUCE_FENCE)
    v.set(tx + 1, 1, tz, SPRUCE_FENCE)
    v.set(tx - 2, 1, tz, "minecraft:chest", {"minecraft:cardinal_direction": "south"})
    v.set(tx + 2, 1, tz, "minecraft:barrel")
    v.set(tx, 5, tz, LANTERN, {"hanging": True})
    # twin blades crossed before the throne (end rods on fences)
    v.set(tx - 1, 1, tz - 2, SPRUCE_FENCE)
    v.set(tx - 1, 2, tz - 2, "minecraft:end_rod")
    v.set(tx + 1, 1, tz - 2, SPRUCE_FENCE)
    v.set(tx + 1, 2, tz - 2, "minecraft:end_rod")
    # ==== two watchtowers (NE + SW) ====
    for tx_, tz_ in ((cx + 8, cz - 8), (cx - 11, cz + 6)):
        for lx, lz in ((tx_, tz_), (tx_ + 2, tz_), (tx_, tz_ + 2), (tx_ + 2, tz_ + 2)):
            for y in range(1, 7):
                v.set(lx, y, lz, SPRUCE_LOG)
        for x in range(tx_ - 1, tx_ + 4):
            for z in range(tz_ - 1, tz_ + 4):
                v.set(x, 7, z, SPRUCE)
                if x in (tx_ - 1, tx_ + 3) or z in (tz_ - 1, tz_ + 3):
                    v.set(x, 8, z, SPRUCE_FENCE)
        v.set(tx_ + 1, 8, tz_ + 1, "minecraft:campfire")
        v.set(tx_ + 1, 1, tz_ + 1, "minecraft:barrel")
    # ==== crew tents around the fire ====
    tent(v, cx - 12, cz - 5, 5, 3, "brown", r)
    tent(v, cx + 6, cz + 2, 5, 3, "black", r)
    tent(v, cx - 7, cz + 6, 4, 2, "brown", r)
    tent(v, cx + 2, cz - 9, 4, 2, "black", r)
    # ==== central spit-roast fire pit ====
    for dx, dz in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        v.set(cx + dx, 0, cz + dz, COBBLE)
    v.set(cx, 1, cz, "minecraft:campfire")
    for sx_ in (cx - 2, cx + 2):
        v.set(sx_, 1, cz, SPRUCE_FENCE)
        v.set(sx_, 2, cz, SPRUCE_FENCE)
    for x in range(cx - 1, cx + 2):
        v.set(x, 3, cz, SPRUCE_FENCE)
    for bz in (cz - 3, cz + 3):              # log benches
        for x in range(cx - 2, cx + 3):
            v.set(x, 1, bz, STRIPPED_SPRUCE)
    # ==== prisoner cage ====
    cgx, cgz = cx + 9, cz + 7
    for x in range(cgx, cgx + 4):
        for z in range(cgz, cgz + 4):
            if x in (cgx, cgx + 3) or z in (cgz, cgz + 3):
                v.set(x, 1, z, IRON_BARS)
                v.set(x, 2, z, IRON_BARS)
            v.set(x, 3, z, SPRUCE)
    v.set(cgx + 1, 1, cgz, "minecraft:air")  # cage door gap
    # ==== supply dump + loot ====
    sx, sz = cx - 10, cz - 1
    v.set(sx, 1, sz, "minecraft:barrel")
    v.set(sx + 1, 1, sz, "minecraft:barrel")
    v.set(sx, 2, sz, "minecraft:barrel")
    v.set(sx, 1, sz + 1, "minecraft:bookshelf")
    v.set(sx + 1, 1, sz - 1, "minecraft:hay_block")
    v.set(sx + 1, 2, sz - 1, "minecraft:hay_block")
    v.set(sx - 1, 1, sz, "minecraft:chest", {"minecraft:cardinal_direction": "east"})
    # supply cart by the gate
    wx, wz = cx + 5, cz + 10
    v.set(wx, 1, wz, SPRUCE_LOG)
    v.set(wx, 1, wz + 2, SPRUCE_LOG)
    for z in range(wz - 1, wz + 4):
        for x in range(wx - 1, wx + 2):
            v.set(x, 2, z, SPRUCE)
    for x in (wx - 1, wx + 1):
        for z in (wz - 1, wz + 3):
            v.set(x, 3, z, SPRUCE_FENCE)
    v.set(wx, 3, wz, "minecraft:hay_block")
    v.set(wx, 3, wz + 1, "minecraft:barrel")
    # training dummy
    dx_, dz_ = cx - 6, cz - 10
    v.set(dx_, 1, dz_, "minecraft:hay_block")
    v.set(dx_, 2, dz_, "minecraft:hay_block")
    v.set(dx_, 3, dz_, "minecraft:carved_pumpkin", {"minecraft:cardinal_direction": "south"})
    v.set(dx_ - 1, 2, dz_, SPRUCE_FENCE)
    v.set(dx_ + 1, 2, dz_, SPRUCE_FENCE)
    # war banner poles
    for bx_, bz_ in ((cx + 4, gz - 2), (cx - 4, gz - 2), (px0 - 1, pz0 - 1), (px0 + 13, pz0 - 1)):
        for y in range(1, 7):
            v.set(bx_, y, bz_, SPRUCE_FENCE)
        v.set(bx_, 6, bz_ - 1, "minecraft:red_wool")
        v.set(bx_, 5, bz_ - 1, "minecraft:red_wool")
        v.set(bx_, 4, bz_ - 1, "minecraft:black_wool")
    v.save("bandit_camp")


def graveyard():
    """Lychfield, grown to a proper burial ground: iron-fenced 25-block yard,
    a grand gabled mausoleum with sunken crypt and loot, a ruined chapel
    corner, rows of varied headstones, exhumed graves, dead trees, ossuary
    and drifting soul-light."""
    r = rng("struct", "grave")
    S = 25
    v = Vox(S, 13, S)
    mid = S // 2
    for x in range(S):
        for z in range(S):
            roll = r.random()
            v.set(x, 0, z, "minecraft:podzol" if roll < 0.4 else
                  ("minecraft:coarse_dirt" if roll < 0.55 else "minecraft:grass_block"))
    # perimeter: cobble base + iron bars, arched gate south
    for x in range(S):
        for z in (0, S - 1):
            if z == S - 1 and abs(x - mid) <= 1:
                continue
            v.set(x, 1, z, COBBLE)
            v.set(x, 2, z, IRON_BARS)
    for z in range(S):
        for x in (0, S - 1):
            v.set(x, 1, z, COBBLE)
            v.set(x, 2, z, IRON_BARS)
    for gx in (mid - 2, mid + 2):
        for y in range(1, 4):
            v.set(gx, y, S - 1, CHISELED)
        v.set(gx, 4, S - 1, SOUL_LANTERN)
    for x in range(mid - 2, mid + 3):
        v.set(x, 4, S - 1, CHISELED)  # gate arch
    # gravel path: gate -> mausoleum, with a fork to the chapel
    for z in range(4, S - 1):
        v.set(mid, 0, z, GRAVEL)
        if r.random() < 0.4:
            v.set(mid + r.choice((-1, 1)), 0, z, GRAVEL)
    for x in range(4, mid):
        v.set(x, 0, 8, GRAVEL if r.random() < 0.8 else "minecraft:coarse_dirt")
    # ==== GRAND MAUSOLEUM (north centre) ====
    mw, md = 11, 7
    mx0, mz0 = mid - mw // 2, 1
    for x in range(mx0, mx0 + mw):
        for z in range(mz0, mz0 + md):
            for y in range(1, 6):
                if x in (mx0, mx0 + mw - 1) or z in (mz0, mz0 + md - 1):
                    v.set(x, y, z, MOSSY if r.random() < 0.35 else STONE)
            v.set(x, 0, z, DEEP_TILES if (x + z) % 3 else STONE)
    # pilaster columns on the facade
    for px_ in (mx0 + 1, mx0 + mw - 2):
        for y in range(1, 6):
            v.set(px_, y, mz0 + md - 1, CHISELED)
    # entrance arch + iron gate
    v.fill(mid - 1, 1, mz0 + md - 1, mid + 1, 3, mz0 + md - 1, "minecraft:air")
    v.set(mid, 1, mz0 + md - 1, IRON_BARS)
    v.set(mid - 1, 4, mz0 + md - 1, CHISELED)
    v.set(mid + 1, 4, mz0 + md - 1, CHISELED)
    v.set(mid, 4, mz0 + md - 1, "minecraft:chiseled_deepslate")  # skull keystone
    # steep gabled roof with finials
    i = 0
    while mx0 - 1 + i <= mx0 + mw - i:
        y = 6 + i
        if y >= 12:
            break
        for z in range(mz0 - 1, mz0 + md + 1):
            v.set(mx0 - 1 + i, y, z, DEEP_TILES)
            v.set(mx0 + mw - i, y, z, DEEP_TILES)
        if mx0 + i <= mx0 + mw - 1 - i:
            for x in range(mx0 + i, mx0 + mw - i):
                v.set(x, y, mz0, STONE)
                v.set(x, y, mz0 + md - 1, STONE)
        i += 1
    v.set(mid, 6 + i, mz0 + md // 2, "minecraft:stone_brick_wall")
    # interior: twin coffins, candles, soul lantern, crypt loot chest
    v.set(mid - 2, 1, mz0 + 2, DARKOAK)
    v.set(mid - 2, 1, mz0 + 3, DARKOAK)
    v.set(mid + 2, 1, mz0 + 2, DARKOAK)
    v.set(mid + 2, 1, mz0 + 3, DARKOAK)
    v.set(mid, 1, mz0 + 1, "minecraft:chest", {"minecraft:cardinal_direction": "south"})
    v.set(mid - 3, 1, mz0 + 1, CANDLE, {"lit": True, "candles": 2})
    v.set(mid + 3, 1, mz0 + 1, CANDLE, {"lit": True})
    v.set(mid, 4, mz0 + 3, SOUL_LANTERN, {"hanging": True})
    # ==== ruined chapel corner (west) ====
    chx, chz = 2, 6
    for z in range(chz, chz + 7):
        h = max(0, 5 - abs(z - (chz + 3)) + r.randrange(-1, 2))
        for y in range(1, h + 1):
            v.set(chx, y, z, rnd_stone(r))
    for x in range(chx, chx + 5):
        h = r.randrange(0, 3)
        for y in range(1, h + 1):
            v.set(x, y, chz, rnd_stone(r))
    for y in range(1, 5):  # surviving lancet arch
        v.set(chx, y, chz + 8, CHISELED)
        v.set(chx + 2, y, chz + 8, CHISELED)
    v.set(chx + 1, 4, chz + 8, CHISELED)
    v.set(chx + 1, 1, chz + 6, "minecraft:lectern", {"minecraft:cardinal_direction": "east"})
    v.set(chx + 1, 1, chz + 9, CANDLE, {"lit": True, "candles": 3})
    # ==== headstone rows (varied) ====
    for gx in range(4, S - 4, 3):
        for gz in range(10, S - 4, 3):
            if abs(gx - mid) < 2 or r.random() > 0.8:
                continue
            style = r.randrange(5)
            if style == 0:
                v.set(gx, 1, gz, COBBLE)
                v.set(gx, 2, gz, "minecraft:cobblestone_wall")
            elif style == 1:
                v.set(gx, 1, gz, CRACK)
                v.set(gx, 2, gz, STONE)
                v.set(gx, 3, gz, "minecraft:stone_brick_wall")
            elif style == 2:
                v.set(gx, 1, gz, MOSSY)
                v.set(gx + 1, 1, gz, "minecraft:cobblestone_wall")
            elif style == 3:  # table tomb
                v.set(gx, 1, gz, STONE)
                v.set(gx + 1, 1, gz, STONE)
                v.set(gx, 2, gz, "minecraft:smooth_quartz")
                v.set(gx + 1, 2, gz, "minecraft:smooth_quartz")
            else:
                v.set(gx, 1, gz, "minecraft:cobblestone_wall")
            if r.random() < 0.3:
                v.set(gx, 1, gz + 1, "minecraft:brown_mushroom")
            if r.random() < 0.18:
                v.set(gx + 1, 1, gz - 1, SOUL_LANTERN)
    # open exhumed graves with dirt piles
    for ox, oz in ((4, 12), (S - 6, 16)):
        v.fill(ox, 0, oz, ox + 1, 0, oz + 2, "minecraft:air")
        v.set(ox + 2, 1, oz + 1, "minecraft:coarse_dirt")
        v.set(ox + 2, 2, oz + 1, "minecraft:coarse_dirt")
        v.set(ox, 1, oz - 1, "minecraft:cobblestone_wall")
    # ossuary: stacked bone blocks under a lean-to
    bx_, bz_ = S - 5, 6
    v.set(bx_, 1, bz_, "minecraft:bone_block")
    v.set(bx_ + 1, 1, bz_, "minecraft:bone_block")
    v.set(bx_, 2, bz_, "minecraft:bone_block")
    v.set(bx_ - 1, 1, bz_, DARKLOG)
    v.set(bx_ + 2, 1, bz_, DARKLOG)
    for x in range(bx_ - 1, bx_ + 3):
        v.set(x, 3, bz_, SPRUCE)
    # dead trees
    for tx, tz in ((3, S - 4), (S - 4, S - 7), (S - 3, 11)):
        h = r.randrange(3, 6)
        for y in range(1, h + 1):
            v.set(tx, y, tz, DARKLOG)
        v.set(tx, h + 1, tz, "minecraft:dark_oak_fence")
        v.set(tx + 1, h, tz, "minecraft:dark_oak_fence")
        v.set(tx - 1, h - 1, tz, "minecraft:dark_oak_fence")
    v.save("graveyard")


def temple_avo():
    """Temple of Avo: stepped marble platform, full peristyle colonnade,
    pedimented gables, golden altar beneath an open skylight, statue of Avo
    and the Harbinger's sword-in-the-stone in the forecourt."""
    r = rng("struct", "avo")
    W, H, L = 17, 13, 21
    v = Vox(W, H, L)
    # stepped crepidoma (3 levels)
    for i, (inset, y) in enumerate(((0, 0), (1, 1), (2, 2))):
        for x in range(inset, W - inset):
            for z in range(inset + 2, L - inset):
                v.set(x, y, z, QUARTZ if (x + z + i) % 2 else "minecraft:smooth_quartz")
    deck = 2
    # peristyle columns on the deck perimeter
    for z in range(4, L - 1, 3):
        for x in (3, W - 4):
            for y in range(deck + 1, deck + 6):
                v.set(x, y, z, "minecraft:quartz_pillar")
            v.set(x, deck + 6, z, QUARTZ)  # capital
    for x in range(3, W - 3, 3):
        for z in (4, L - 2):
            for y in range(deck + 1, deck + 6):
                v.set(x, y, z, "minecraft:quartz_pillar")
            v.set(x, deck + 6, z, QUARTZ)
    # entablature ring
    for x in range(2, W - 2):
        for z in (3, L - 1):
            v.set(x, deck + 6, z, "minecraft:smooth_quartz")
    for z in range(3, L):
        for x in (2, W - 3):
            v.set(x, deck + 6, z, "minecraft:smooth_quartz")
    # roof slab with open skylight over the altar
    for x in range(2, W - 2):
        for z in range(3, L):
            v.set(x, deck + 7, z, QUARTZ)
    for x in range(W // 2 - 1, W // 2 + 2):
        for z in range(L - 8, L - 5):
            v.set(x, deck + 7, z, "minecraft:air")  # skylight
    # pediment gables (front/back)
    i = 0
    while 2 + i <= W - 3 - i:
        for x in range(2 + i, W - 2 - i):
            v.set(x, deck + 8 + i, 3, "minecraft:smooth_quartz")
            v.set(x, deck + 8 + i, L - 1, "minecraft:smooth_quartz")
        i += 1
        if deck + 8 + i >= H:
            break
    # golden altar under the skylight
    ax, az = W // 2, L - 7
    v.fill(ax - 1, deck + 1, az - 1, ax + 1, deck + 1, az + 1, GOLD)
    v.set(ax, deck + 2, az, "minecraft:enchanting_table")
    v.set(ax - 2, deck + 1, az, CANDLE, {"lit": True, "candles": 3})
    v.set(ax + 2, deck + 1, az, CANDLE, {"lit": True, "candles": 3})
    v.set(ax, deck + 1, az - 3, "minecraft:sea_lantern")
    # circular donation fountain in the nave — coins glitter under the water
    fx, fz = W // 2, 9
    for x in range(fx - 2, fx + 3):
        for z in range(fz - 2, fz + 3):
            d = math.hypot(x - fx, z - fz)
            if 1.4 < d <= 2.5:
                v.set(x, deck + 1, z, "minecraft:smooth_quartz")
            elif d <= 1.4:
                v.set(x, deck, z, GOLD)          # offerings on the basin floor
                v.set(x, deck + 1, z, "minecraft:water")
    v.set(fx, deck + 1, fz, "minecraft:sea_lantern")
    v.set(fx - 2, deck + 2, fz - 2, CANDLE, {"lit": True, "candles": 2})
    v.set(fx + 2, deck + 2, fz + 2, CANDLE, {"lit": True, "candles": 2})
    # flower offerings at the fountain rim
    v.set(fx - 3, deck + 1, fz, "minecraft:oxeye_daisy")
    v.set(fx + 3, deck + 1, fz, "minecraft:cornflower")
    # statue of Avo (rear centre): pillar body, out-stretched arms, halo
    sx, sz2 = W // 2, L - 3
    for y in range(deck + 1, deck + 5):
        v.set(sx, y, sz2, "minecraft:quartz_pillar")
    v.set(sx, deck + 5, sz2, "minecraft:smooth_quartz")  # head
    v.set(sx - 1, deck + 4, sz2, QUARTZ)
    v.set(sx + 1, deck + 4, sz2, QUARTZ)
    v.set(sx, deck + 6, sz2, "minecraft:end_rod")        # halo light
    # forecourt: sword in the stone on the approach
    v.set(W // 2, 0, 0, GRAVEL)
    v.set(W // 2, 0, 1, GRAVEL)
    v.set(W // 2, 1, 1, CHISELED)
    v.set(W // 2, 2, 1, "minecraft:end_rod")  # the Harbinger waits
    # gold trim line on the architrave
    for x in range(3, W - 3, 2):
        v.set(x, deck + 6, 3, GOLD)
    v.save("temple_avo")


def chapel_skorm():
    """Chapel of Skorm: gothic blackstone nave with buttresses, pointed
    spire crowned in soul-fire, glowing rose window, pews, blood font and
    the sacrificial altar."""
    r = rng("struct", "skorm")
    W, H, L = 15, 17, 19
    v = Vox(W, H, L)
    mx = W // 2
    # ground: blackstone with gilded seams
    for x in range(W):
        for z in range(L):
            v.set(x, 0, z, "minecraft:polished_blackstone" if (x + z) % 4 else "minecraft:gilded_blackstone")
    # nave walls
    for x in range(2, W - 2):
        for z in (2, L - 2):
            for y in range(1, 7):
                v.set(x, y, z, "minecraft:polished_blackstone_bricks")
    for z in range(2, L - 1):
        for x in (2, W - 3):
            for y in range(1, 7):
                v.set(x, y, z, "minecraft:polished_blackstone_bricks")
    # buttresses stepping out of the side walls
    for z in range(4, L - 3, 4):
        for side in (1, W - 2):
            v.set(side, 1, z, "minecraft:polished_blackstone")
            v.set(side, 2, z, "minecraft:polished_blackstone")
            v.set(side, 3, z, "minecraft:blackstone_wall")
    # crying-obsidian lancet windows with magma sills
    for z in range(4, L - 3, 4):
        for side in (2, W - 3):
            v.set(side, 3, z, "minecraft:crying_obsidian")
            v.set(side, 4, z, "minecraft:crying_obsidian")
            v.set(side, 2, z, "minecraft:magma")
    # pointed entrance arch (south) + soul sconces
    v.fill(mx - 1, 1, L - 2, mx + 1, 3, L - 2, "minecraft:air")
    v.set(mx, 4, L - 2, "minecraft:air")
    for y in range(1, 5):
        v.set(mx - 2, y, L - 2, "minecraft:gilded_blackstone" if y % 2 else "minecraft:polished_blackstone_bricks")
        v.set(mx + 2, y, L - 2, "minecraft:gilded_blackstone" if y % 2 else "minecraft:polished_blackstone_bricks")
    v.set(mx - 2, 5, L - 2, "minecraft:blackstone_wall")
    v.set(mx + 2, 5, L - 2, "minecraft:blackstone_wall")
    v.set(mx, 5, L - 2, "minecraft:chiseled_deepslate")
    v.set(mx - 3, 3, L - 2, SOUL_LANTERN)
    v.set(mx + 3, 3, L - 2, SOUL_LANTERN)
    # rose window (north end): great glowing wheel ringed in gold
    for dy in range(-2, 3):
        for dxx in range(-2, 3):
            ad = abs(dxx) + abs(dy)
            if ad == 2:
                v.set(mx + dxx, 4 + dy, 2, "minecraft:crying_obsidian")
            elif ad == 1:
                v.set(mx + dxx, 4 + dy, 2, "minecraft:magma")
    v.set(mx, 4, 2, "minecraft:glowstone")
    for dxx, dy in ((-2, -2), (2, -2), (-2, 2), (2, 2)):
        v.set(mx + dxx, 4 + dy, 2, "minecraft:gilded_blackstone")
    # steep gable roof
    gable_roof_z(v, 1, W - 2, 2, L - 2, 7, "minecraft:polished_blackstone", "minecraft:polished_blackstone_bricks")
    # gilded ridge seam + soul-fire sconces along the eaves
    for z in range(3, L - 2, 3):
        v.set(mx, 7 + (W - 4) // 2, z, "minecraft:gilded_blackstone")
    for z in range(5, L - 4, 6):
        v.set(1, 4, z, "minecraft:soul_torch")
        v.set(W - 2, 4, z, "minecraft:soul_torch")
    # spire over the altar end + soul beacon
    cylinder(v, mx, 5, 2, 7, 12, "minecraft:polished_blackstone_bricks")
    cone_roof(v, mx, 5, 3, 13, "minecraft:polished_blackstone")
    v.set(mx, 16, 5, "minecraft:soul_campfire")
    # pews: two columns of blackstone-wall benches
    for z in range(8, L - 4, 2):
        for x in (mx - 3, mx - 2, mx + 2, mx + 3):
            v.set(x, 1, z, "minecraft:blackstone_wall")
    # central aisle: red carpet of nether wart-red wool
    for z in range(4, L - 2):
        v.set(mx, 0, z, "minecraft:red_wool")
    # blood font at the entrance
    v.set(mx + 3, 1, L - 4, "minecraft:polished_blackstone")
    v.set(mx + 3, 2, L - 4, "minecraft:magma")
    # sacrificial altar (north): gilded dais, soul fire, skull
    v.fill(mx - 2, 1, 3, mx + 2, 1, 5, "minecraft:gilded_blackstone")
    v.set(mx, 2, 4, "minecraft:soul_campfire")
    v.set(mx - 2, 2, 4, SOUL_LANTERN)
    v.set(mx + 2, 2, 4, SOUL_LANTERN)
    v.set(mx, 2, 3, "minecraft:chiseled_deepslate")
    # sacrificial pit before the dais
    v.fill(mx - 1, 0, 6, mx + 1, 0, 7, "minecraft:magma")
    v.save("chapel_skorm")


def arena_ring():
    """The Arena: two-tier elliptical amphitheatre — sand pit scattered with
    bones, barred beast gates, tiered stands, champion's box and banners."""
    r = rng("struct", "arena")
    D = 27
    v = Vox(D, 12, D)
    c = D // 2
    for x in range(D):
        for z in range(D):
            d2 = (x - c) ** 2 + (z - c) ** 2
            d = math.sqrt(d2)
            if d <= c - 5:
                # fighting pit: sand with bone-litter
                roll = r.random()
                v.set(x, 0, z, "minecraft:sand" if roll < 0.8 else
                      ("minecraft:bone_block" if roll < 0.86 else "minecraft:red_sand"))
            elif d <= c - 3:
                # inner wall ring
                for y in range(0, 4):
                    v.set(x, y, z, rnd_stone(r))
                v.set(x, 4, z, "minecraft:stone_brick_wall")
            elif d <= c - 1:
                # lower stands
                for y in range(0, 5):
                    v.set(x, y, z, STONE if y < 4 else "minecraft:smooth_quartz")
            elif d <= c + 0.4:
                # outer wall + upper stands
                for y in range(0, 7):
                    v.set(x, y, z, rnd_stone(r))
                if (x * 7 + z * 3) % 9 == 0:
                    v.set(x, 7, z, "minecraft:torch")
                else:
                    v.set(x, 7, z, "minecraft:stone_brick_wall")
    # beast gates N/S: barred arches through all rings. The south gate is left
    # open as the spectators' walk-in entrance; only the north stays a barred
    # beast gate so the pit is always reachable on foot.
    for gz, gdir in ((0, 1), (D - 1, -1)):
        for x in range(c - 1, c + 2):
            for off in range(0, 6):
                z = gz + gdir * off
                for y in range(1, 4):
                    v.set(x, y, z, "minecraft:air")
        # portcullis bars at the pit mouth (north beast gate only)
        if gdir == -1:
            for x in range(c - 1, c + 2):
                for y in range(1, 4):
                    v.set(x, y, gz + gdir * 5, IRON_BARS)
        # gate arch dressing
        for y in range(1, 5):
            v.set(c - 2, y, gz, CHISELED)
            v.set(c + 2, y, gz, CHISELED)
        for x in range(c - 2, c + 3):
            v.set(x, 5, gz, CHISELED)
    # champion's box (east): gilded balcony
    bx = c + (c - 2)
    for x in range(bx - 2, min(D, bx + 1)):
        for z in range(c - 2, c + 3):
            v.set(x, 5, z, GOLD)
            v.set(x, 6, z, "minecraft:red_wool")
    v.set(min(D - 1, bx - 1), 7, c, LANTERN, {"hanging": False})
    # banner poles at four compass points on the rim
    for ang in range(45, 360, 90):
        px_ = c + round(math.cos(math.radians(ang)) * (c - 1))
        pz_ = c + round(math.sin(math.radians(ang)) * (c - 1))
        if 0 <= px_ < D and 0 <= pz_ < D:
            for y in range(7, 10):
                v.set(px_, y, pz_, SPRUCE_FENCE)
            v.set(px_, 10, pz_, "minecraft:red_wool")
            v.set(px_, 9, pz_, "minecraft:red_wool")
    # champion statues on the rim at the compass points, gazing into the pit
    for ang in range(0, 360, 90):
        sx_ = c + round(math.cos(math.radians(ang)) * (c - 2))
        sz_ = c + round(math.sin(math.radians(ang)) * (c - 2))
        if not (1 <= sx_ < D - 1 and 1 <= sz_ < D - 1):
            continue
        v.set(sx_, 7, sz_, CHISELED)                      # plinth
        v.set(sx_, 8, sz_, "minecraft:quartz_pillar")     # body
        v.set(sx_, 9, sz_, "minecraft:quartz_pillar")
        v.set(sx_, 10, sz_, "minecraft:smooth_quartz")    # head
        # raised sword arm toward the sand
        ix = c + round(math.cos(math.radians(ang)) * (c - 3))
        iz = c + round(math.sin(math.radians(ang)) * (c - 3))
        v.set(ix, 9, iz, "minecraft:stone_brick_wall")
        v.set(ix, 10, iz, "minecraft:end_rod")
    # blood stains + shattered shield props in the pit
    for i in range(6):
        x = c + r.randrange(-6, 7)
        z = c + r.randrange(-6, 7)
        v.set(x, 0, z, "minecraft:red_sand")
    v.set(c - 4, 1, c + 3, "minecraft:bone_block")
    v.set(c + 5, 1, c - 2, "minecraft:cobblestone_wall")
    v.save("arena_ring")


def chamber_of_fate():
    """Heroes' Guild undercroft — the Old Kingdom Chamber of Fate: a great
    circular domed hall ringed with framed frescoes of a hero's deeds and a
    raised central dais holding the Cullis focus.

    It is deliberately HOLLOW: only the floor, the encircling wall, the columns
    and the dome are solid — everything a Hero stands in is open air. (At
    runtime `hollowChamber()` also scrubs any rock that bleeds in when the room
    is placed deep underground, so it can never read as a solid block of fill.)
    """
    r = rng("struct", "chamber_fate")
    S, H = 31, 18
    v = Vox(S, H, S)
    c = S // 2
    WALL_R = 13          # outer wall radius
    INNER = 11.5         # inner face of the wall (open floor reaches to here)
    WALL_TOP = 11        # dome springs from here

    # ---- floor: concentric flagstone rings ----
    for x in range(S):
        for z in range(S):
            d = math.hypot(x - c, z - c)
            if d <= WALL_R + 0.6:
                v.set(x, 0, z, DEEP_TILES if (x + z) % 3 else STONE)
            if d <= INNER:
                v.set(x, 1, z, CHISELED if (x + z) % 2 else DEEP_TILES)

    # ---- encircling wall (airtight, no gaps) ----
    for x in range(S):
        for z in range(S):
            d = math.hypot(x - c, z - c)
            if INNER < d <= WALL_R + 0.5:
                for y in range(1, WALL_TOP):
                    roll = r.random()
                    v.set(x, y, z, STONE if roll < 0.7 else
                          (CRACK if roll < 0.85 else MOSSY))

    # ---- framed frescoes set into the inner wall face ----
    # bold glazed murals (dragon-fire, the magic shield, the dark villain, the
    # hero's gold halo, Albion's woods, the cold sea) each framed in gold and
    # chiseled stone and lit by a brazier — "the chamber's most remarkable
    # feature", per the lore.
    murals = [
        ("minecraft:red_glazed_terracotta", "minecraft:orange_glazed_terracotta"),
        ("minecraft:light_blue_glazed_terracotta", "minecraft:blue_glazed_terracotta"),
        ("minecraft:black_glazed_terracotta", "minecraft:purple_glazed_terracotta"),
        ("minecraft:yellow_glazed_terracotta", "minecraft:white_glazed_terracotta"),
        ("minecraft:green_glazed_terracotta", "minecraft:lime_glazed_terracotta"),
        ("minecraft:cyan_glazed_terracotta", "minecraft:light_blue_glazed_terracotta"),
    ]
    for i, ang in enumerate(range(0, 360, 60)):
        a = math.radians(ang)
        bx = c + round(math.cos(a) * (WALL_R - 1))
        bz = c + round(math.sin(a) * (WALL_R - 1))
        top, bot = murals[i % len(murals)]
        tx, tz = -round(math.sin(a)), round(math.cos(a))   # tangent along the wall
        for k in (-1, 0, 1):
            px, pz = bx + tx * k, bz + tz * k
            v.set(px, 4, pz, bot)
            v.set(px, 5, pz, bot)
            v.set(px, 6, pz, top)
            v.set(px, 7, pz, top)
            v.set(px, 3, pz, GOLD if k == 0 else CHISELED)   # framed base
            v.set(px, 8, pz, GOLD if k == 0 else CHISELED)   # framed lintel
        # a brazier on the floor before each fresco
        lx = c + round(math.cos(a) * (WALL_R - 3))
        lz = c + round(math.sin(a) * (WALL_R - 3))
        v.set(lx, 1, lz, CHISELED)
        v.set(lx, 2, lz, "minecraft:campfire")

    # ---- inner ring columns (between the frescoes), holding the dome ----
    for ang in range(30, 360, 60):
        px = c + round(math.cos(math.radians(ang)) * 9)
        pz = c + round(math.sin(math.radians(ang)) * 9)
        for y in range(2, WALL_TOP - 1):
            v.set(px, y, pz, QUARTZ if y < WALL_TOP - 2 else "minecraft:quartz_pillar")
        v.set(px, WALL_TOP - 1, pz, GOLD)
        v.set(px, 2, pz - 1, "minecraft:lantern", {"hanging": False})

    # ---- raised central dais + the Cullis focus at the heart ----
    for x in range(c - 4, c + 5):
        for z in range(c - 4, c + 5):
            d = math.hypot(x - c, z - c)
            if d <= 4.2:
                v.set(x, 2, z, CHISELED)
            if d <= 2.9:
                v.set(x, 3, z, DEEP_TILES)
            if d <= 1.5:
                v.set(x, 4, z, OBSIDIAN if (x + z) % 2 else "minecraft:crying_obsidian")
    v.set(c, 5, c, "minecraft:beacon")
    for ang in range(0, 360, 45):
        px = c + round(math.cos(math.radians(ang)) * 3)
        pz = c + round(math.sin(math.radians(ang)) * 3)
        v.set(px, 4, pz, "minecraft:sea_lantern" if ang % 90 == 0 else QUARTZ)

    # ---- cave bridge approach from the south (kept open) ----
    for z in range(S - 1, c + 5, -1):
        for x in range(c - 2, c + 3):
            v.set(x, 1, z, COBBLE if (x + z) % 2 else MCOBBLE)
            v.fill(x, 2, z, x, 5, z, "minecraft:air")

    # ---- dome shell (airtight) with hanging lanterns + a central oculus ----
    for y in range(WALL_TOP, H):
        rad = max(2, int(13 - (y - WALL_TOP) * 0.95))
        for x in range(c - rad - 1, c + rad + 2):
            for z in range(c - rad - 1, c + rad + 2):
                d = math.hypot(x - c, z - c)
                if rad - 0.8 <= d <= rad + 0.6:
                    v.set(x, y, z, STONE if r.random() < 0.8 else CRACK)
    for ang in range(0, 360, 90):
        px = c + round(math.cos(math.radians(ang)) * 6)
        pz = c + round(math.sin(math.radians(ang)) * 6)
        v.set(px, WALL_TOP, pz, "minecraft:chain")
        v.set(px, WALL_TOP - 1, pz, "minecraft:lantern", {"hanging": True})
    v.set(c, H - 2, c, "minecraft:sea_lantern")
    v.set(c, H - 1, c, "minecraft:end_rod")
    v.save("chamber_of_fate")


def oakvale_village():
    """Oakvale: whitewashed plaster-and-timber cottages under hay thatch,
    a guarded gate, the great oak and well green, a working wheat field with
    scarecrow, a memorial garden for the raided dead, and a timber quay."""
    r = rng("struct", "oakvale_village")
    W, H, L = 35, 14, 35
    v = Vox(W, H, L)
    c = W // 2
    PLASTER = "minecraft:white_terracotta"
    # terrain gradient to coast
    for x in range(W):
        for z in range(L):
            if z > 29:
                v.set(x, 0, z, "minecraft:water")
            elif z > 24:
                v.set(x, 0, z, "minecraft:sand")
            else:
                v.set(x, 0, z, "minecraft:grass_block" if r.random() < 0.8 else "minecraft:coarse_dirt")
    # guarded north gate: cobble piers, lantern arch, fence wings
    for gx_ in (c - 3, c + 3):
        for y in range(1, 5):
            v.set(gx_, y, 2, COBBLE if y < 4 else MCOBBLE)
        v.set(gx_, 5, 2, LANTERN, {"hanging": False})
    for x in range(c - 2, c + 3):
        v.set(x, 4, 2, SPRUCE_LOG)
    for x in list(range(3, c - 3)) + list(range(c + 4, W - 3)):
        v.set(x, 1, 2, SPRUCE_FENCE)
    # lane from the gate to the green
    for z in range(2, c + 2):
        for x in (c - 1, c, c + 1):
            v.set(x, 0, z, PATH if r.random() < 0.8 else GRAVEL)
    # central great oak and well
    tx, tz = c + 4, c
    for y in range(1, 8):
        v.set(tx, y, tz, "minecraft:oak_log")
    for x in range(tx - 3, tx + 4):
        for y in range(6, 10):
            for z in range(tz - 3, tz + 4):
                if math.hypot(x - tx, z - tz) + abs(y - 7.5) <= 3.8:
                    v.set(x, y, z, "minecraft:oak_leaves")
    wx, wz = c - 3, c + 1
    for x in range(wx - 2, wx + 3):
        for z in range(wz - 2, wz + 3):
            if x in (wx - 2, wx + 2) or z in (wz - 2, wz + 2):
                v.set(x, 1, z, COBBLE)
    v.set(wx, 1, wz, "minecraft:water")
    for px_, pz_ in ((wx - 2, wz - 2), (wx + 2, wz + 2)):  # well roof posts
        v.set(px_, 2, pz_, SPRUCE_FENCE)
        v.set(px_, 3, pz_, SPRUCE_FENCE)
    for x in range(wx - 2, wx + 3):
        for z in range(wz - 2, wz + 3):
            v.set(x, 4, z, SPRUCE if (x + z) % 2 else "minecraft:hay_block")
    # ring path around the green
    for x in range(c - 8, c + 9):
        for z in range(c - 8, c + 9):
            d = math.hypot(x - c, z - c)
            if 6.1 < d <= 7.2:
                v.set(x, 0, z, PATH)

    def cottage(bx, bz, bw=6, bd=5):
        """Whitewashed plaster walls, spruce-log frame, hay thatch roof."""
        for x in range(bx, bx + bw):
            for z in range(bz, bz + bd):
                v.set(x, 0, z, COBBLE)
                for y in range(1, 4):
                    if x in (bx, bx + bw - 1) or z in (bz, bz + bd - 1):
                        v.set(x, y, z, PLASTER)
        for px_, pz_ in ((bx, bz), (bx + bw - 1, bz), (bx, bz + bd - 1),
                         (bx + bw - 1, bz + bd - 1)):
            for y in range(1, 4):
                v.set(px_, y, pz_, SPRUCE_LOG)       # corner frame
        v.fill(bx + 1, 1, bz + 1, bx + bw - 2, 3, bz + bd - 2, "minecraft:air")
        gable_roof_z(v, bx - 1, bx + bw, bz, bz + bd - 1, 4, "minecraft:hay_block", PLASTER)
        v.set(bx + bw // 2, 4 + bw // 2, bz + bd // 2, SPRUCE)  # ridge cap
        v.set(bx + 2, 1, bz, "minecraft:air")        # door
        v.set(bx + 2, 2, bz, "minecraft:air")
        v.set(bx + 1, 2, bz, GLASS)
        v.set(bx + bw - 2, 2, bz, GLASS)
        v.set(bx + 1, 1, bz + bd - 2, "minecraft:bed", {"direction": 0})
        v.set(bx + bw - 2, 1, bz + bd - 2, "minecraft:chest",
              {"minecraft:cardinal_direction": "south"})
        v.set(bx + bw - 2, 1, bz + 1, "minecraft:barrel")
        # window-box flowers
        v.set(bx, 1, bz - 1, r.choice(("minecraft:poppy", "minecraft:cornflower",
                                       "minecraft:oxeye_daisy")))
    cottage(6, 8)
    cottage(24, 8)
    cottage(7, 18)
    cottage(24, 18)
    cottage(14, 23)
    # working wheat field with scarecrow (west)
    fx0, fz0 = 3, 13
    for x in range(fx0, fx0 + 7):
        for z in range(fz0, fz0 + 6):
            if x == fx0 + 3:
                v.set(x, 0, z, "minecraft:water")     # irrigation channel
            else:
                v.set(x, 0, z, "minecraft:farmland", {"moisturized_amount": 7})
                v.set(x, 1, z, "minecraft:wheat", {"growth": 5 + r.randrange(3)})
    for x in range(fx0 - 1, fx0 + 8):                  # picket fence
        v.set(x, 1, fz0 - 1, "minecraft:oak_fence")
        v.set(x, 1, fz0 + 6, "minecraft:oak_fence")
    scx, scz = fx0 + 3, fz0 + 2
    v.set(scx, 1, scz, "minecraft:oak_fence")
    v.set(scx, 2, scz, "minecraft:hay_block")
    v.set(scx, 3, scz, "minecraft:carved_pumpkin", {"minecraft:cardinal_direction": "south"})
    v.set(scx - 1, 2, scz, "minecraft:oak_fence")
    v.set(scx + 1, 2, scz, "minecraft:oak_fence")
    v.set(fx0, 1, fz0 + 7, "minecraft:composter")
    # memorial garden for the raid dead (east): statue + graves + roses
    mx0, mz0 = 28, 13
    v.set(mx0, 1, mz0, CHISELED)                       # plinth
    v.set(mx0, 2, mz0, STONE)                          # the axe-hero
    v.set(mx0, 3, mz0, STONE)
    v.set(mx0, 4, mz0, "minecraft:smooth_quartz")      # head
    v.set(mx0 + 1, 3, mz0, "minecraft:stone_brick_wall")  # raised arm
    v.set(mx0 + 1, 4, mz0, DEEPSLATE_W)                # the axe
    for gvx, gvz in ((mx0 - 2, mz0 + 2), (mx0, mz0 + 3), (mx0 + 2, mz0 + 2)):
        v.set(gvx, 1, gvz, "minecraft:cobblestone_wall")
        if r.random() < 0.6:
            v.set(gvx + 1, 1, gvz, "minecraft:rose_bush")
    v.set(mx0 - 1, 1, mz0 - 1, CANDLE, {"lit": True, "candles": 2})
    # flower borders along the green
    for i in range(10):
        fx_, fz_ = 4 + r.randrange(W - 8), 5 + r.randrange(18)
        if v.grid[v.idx(fx_, 1, fz_)] == v._pid("minecraft:air"):
            if v.grid[v.idx(fx_, 0, fz_)] == v._pid("minecraft:grass_block"):
                v.set(fx_, 1, fz_, r.choice(("minecraft:poppy", "minecraft:cornflower",
                                             "minecraft:oxeye_daisy", "minecraft:red_tulip")))
    # quay with smoke-rack and moored boat
    for x in range(c - 4, c + 5):
        for z in range(25, 32):
            v.set(x, 1, z, SPRUCE)
    for x in (c - 4, c + 4):
        for y in range(2, 5):
            v.set(x, y, 29, SPRUCE_FENCE)
        v.set(x, 5, 29, LANTERN)
    v.set(c - 3, 2, 26, "minecraft:barrel")
    v.set(c - 2, 2, 26, "minecraft:campfire")          # fish smoker
    v.set(c + 2, 2, 27, "minecraft:chest", {"minecraft:cardinal_direction": "west"})
    # little rowing boat off the quay
    for bz_ in (32, 33):
        v.set(c + 6, 1, bz_, SPRUCE)
    v.set(c + 6, 1, 31, SPRUCE_FENCE)
    v.save("oakvale_village")


def bowerstone_market():
    """Bowerstone South: crenellated wall and twin-tower gatehouse, jettied
    Tudor townhouses (dark-oak frame over white plaster), river and bridge,
    market stalls, street lamps, a clock tower — and the class-divide gate
    to the richer quartz-trimmed North bank."""
    r = rng("struct", "bowerstone_market")
    W, H, L = 37, 16, 37
    v = Vox(W, H, L)
    c = W // 2
    PLASTER = "minecraft:white_terracotta"
    # paving + river band
    for x in range(W):
        for z in range(L):
            if 16 <= z <= 20:
                v.set(x, 0, z, "minecraft:water")
            else:
                v.set(x, 0, z, DEEP_TILES if (x + z) % 4 else GRAVEL)
    # river embankment walls
    for x in range(W):
        v.set(x, 0, 16, STONE)
        v.set(x, 0, 20, STONE)
    # arched stone bridge
    for x in range(c - 3, c + 4):
        for z in range(15, 22):
            v.set(x, 1, z, STONE)
            if x in (c - 3, c + 3):
                v.set(x, 2, z, "minecraft:stone_brick_wall")
    v.set(c - 3, 3, 18, LANTERN, {"hanging": False})
    v.set(c + 3, 3, 18, LANTERN, {"hanging": False})
    # ==== crenellated south wall + twin-tower gatehouse ====
    for x in range(2, W - 2):
        if abs(x - c) <= 3:
            continue
        for y in range(1, 5):
            v.set(x, y, 33, rnd_stone(r))
        if x % 2 == 0:
            v.set(x, 5, 33, STONE)                     # merlons
    for gx in (c - 4, c + 4):                           # round gate towers
        cylinder(v, gx, 33, 2, 1, 7, STONE)
        cone_roof(v, gx, 33, 3, 8, DEEP_TILES, tip="minecraft:end_rod")
        v.set(gx, 4, 31, GLASS)
    for x in range(c - 3, c + 4):                       # gate arch
        v.set(x, 5, 33, CHISELED)
        v.set(x, 6, 33, STONE)
    for y in range(1, 5):
        v.set(c - 3, y, 33, CHISELED)
        v.set(c + 3, y, 33, CHISELED)
    v.set(c, 6, 32, GOLD)                               # city crest
    v.set(c - 2, 4, 33, LANTERN, {"hanging": True})
    v.set(c + 2, 4, 33, LANTERN, {"hanging": True})
    # lane from gate to bridge
    for z in range(21, 33):
        for x in (c - 1, c, c + 1):
            v.set(x, 0, z, DEEP_TILES)

    def townhouse(bx, bz, bw, bd, rich=False):
        """Two-storey Tudor: stone ground floor, jettied plaster upper floor
        with dark-oak cross-frame, steep slate roof."""
        trim = QUARTZ if rich else DARKLOG
        # ground floor
        for x in range(bx, bx + bw):
            for z in range(bz, bz + bd):
                v.set(x, 0, z, COBBLE)
                for y in (1, 2):
                    if x in (bx, bx + bw - 1) or z in (bz, bz + bd - 1):
                        v.set(x, y, z, rnd_stone(r))
        # jettied upper floor (overhangs by 1 on the front)
        for x in range(bx - 1, bx + bw + 1):
            for z in range(bz - 1, bz + bd):
                v.set(x, 3, z, SPRUCE)                  # jetty floor band
        for x in range(bx - 1, bx + bw + 1):
            for z in range(bz - 1, bz + bd):
                for y in (4, 5):
                    if x in (bx - 1, bx + bw) or z in (bz - 1, bz + bd - 1):
                        v.set(x, y, z, PLASTER)
        # dark-oak frame: corner posts + mid studs
        for px_, pz_ in ((bx - 1, bz - 1), (bx + bw, bz - 1), (bx - 1, bz + bd - 1),
                         (bx + bw, bz + bd - 1)):
            for y in (3, 4, 5):
                v.set(px_, y, pz_, trim)
        for x in range(bx + 1, bx + bw - 1, 2):
            v.set(x, 4, bz - 1, trim)
        # hollow interiors
        v.fill(bx + 1, 1, bz + 1, bx + bw - 2, 2, bz + bd - 2, "minecraft:air")
        v.fill(bx, 4, bz, bx + bw - 1, 5, bz + bd - 2, "minecraft:air")
        # roof
        gable_roof_z(v, bx - 2, bx + bw + 1, bz - 1, bz + bd - 1, 6, DEEP_TILES, PLASTER)
        # door + leaded windows
        v.set(bx + bw // 2, 1, bz, "minecraft:air")
        v.set(bx + bw // 2, 2, bz, "minecraft:air")
        v.set(bx + 1, 2, bz, GLASS)
        v.set(bx + bw - 2, 2, bz, GLASS)
        v.set(bx, 5, bz - 1, GLASS)
        v.set(bx + bw - 1, 5, bz - 1, GLASS)
        v.set(bx + bw // 2, 4, bz - 1, GLASS)
        # furnishing + chest
        v.set(bx + 1, 1, bz + bd - 2, "minecraft:chest",
              {"minecraft:cardinal_direction": "south"})
        v.set(bx + bw - 2, 1, bz + bd - 2, "minecraft:barrel")
        if rich:
            v.set(bx + bw // 2, 6 + (bw + 2) // 2, bz + bd // 2, GOLD)  # gilt finial
    # south bank (working quarter)
    townhouse(5, 23, 7, 7)
    townhouse(25, 23, 7, 7)
    # north bank (rich quarter, quartz-trimmed)
    townhouse(4, 6, 8, 8, rich=True)
    townhouse(25, 6, 8, 8, rich=True)
    # class-divide gate on the bridge: iron gate + guard braziers
    for x in (c - 2, c + 2):
        for y in range(2, 6):
            v.set(x, y, 15, CHISELED)
        v.set(x, 6, 15, LANTERN, {"hanging": False})
    for x in range(c - 1, c + 2):
        v.set(x, 5, 15, STONE)
        v.set(x, 4, 15, IRON_BARS)
    # clock tower on the north market square
    ckx, ckz = c, 4
    for y in range(1, 10):
        v.set(ckx, y, ckz, STONE if y % 3 else CHISELED)
        v.set(ckx - 1, y, ckz, STONE if y < 8 else "minecraft:air")
        v.set(ckx + 1, y, ckz, STONE if y < 8 else "minecraft:air")
    v.set(ckx, 8, ckz - 1, GOLD)                        # clock face
    v.set(ckx, 7, ckz - 1, "minecraft:stone_brick_wall")
    v.set(ckx, 10, ckz, CHISELED)
    v.set(ckx, 11, ckz, "minecraft:end_rod")
    # market stalls (south square)
    for sx, sz, col in ((9, 21, "red"), (24, 21, "blue"), (16, 28, "white")):
        for x in (sx, sx + 3):
            for z in (sz, sz + 2):
                v.set(x, 1, z, SPRUCE_FENCE)
                v.set(x, 2, z, SPRUCE_FENCE)
        for x in range(sx, sx + 4):
            for z in range(sz, sz + 3):
                v.set(x, 3, z, f"minecraft:{col}_wool")
        v.set(sx + 1, 1, sz + 1, "minecraft:barrel")
        v.set(sx + 2, 1, sz + 1, "minecraft:chest", {"minecraft:cardinal_direction": "south"})
    # street lamps along the lanes
    for lx_, lz_ in ((c - 5, 25), (c + 5, 30), (c - 6, 10), (c + 6, 12), (4, 21), (32, 22)):
        v.set(lx_, 1, lz_, DARKLOG)
        v.set(lx_, 2, lz_, "minecraft:dark_oak_fence")
        v.set(lx_, 3, lz_, "minecraft:dark_oak_fence")
        v.set(lx_, 4, lz_, LANTERN, {"hanging": False})
    # dockside crates on the river walk
    v.set(3, 1, 15, "minecraft:barrel")
    v.set(4, 1, 15, "minecraft:barrel")
    v.set(3, 2, 15, "minecraft:hay_block")
    v.save("bowerstone_market")


def knothole_glade():
    """Knothole Glade: a hidden forest settlement of round timber huts under
    conical spruce roofs, carved guardian totems, the Scarlet Robe memorial
    statue and an archery range, ringed by a cliff wall."""
    r = rng("struct", "knothole_glade")
    W, H, L = 35, 15, 35
    v = Vox(W, H, L)
    c = W // 2
    for x in range(W):
        for z in range(L):
            v.set(x, 0, z, "minecraft:podzol" if (x + z) % 5 else "minecraft:grass_block")
            if r.random() < 0.06:
                v.set(x, 1, z, "minecraft:fern")
    # surrounding stone/wood cliff edge
    for x in range(W):
        for z in range(L):
            d = math.hypot(x - c, z - c)
            if 14.3 < d <= 16.3:
                h = 3 + int((d - 14.3) * 2)
                for y in range(1, h):
                    v.set(x, y, z, COBBLE if r.random() < 0.45 else STONE)
                if r.random() < 0.2:
                    v.set(x, h, z, "minecraft:dark_oak_leaves")
    # palisade gate
    gz = 4
    for gx in (c - 3, c + 3):
        for y in range(1, 8):
            v.set(gx, y, gz, SPRUCE_LOG)
        v.set(gx, 8, gz, LANTERN)
    for x in range(c - 3, c + 4):
        v.set(x, 8, gz, SPRUCE)
    for x in range(4, W - 4):
        if abs(x - c) <= 4:
            continue
        v.set(x, 1, 6, SPRUCE_LOG)
        v.set(x, 2, 6, SPRUCE_FENCE)
    # the Scarlet Robe memorial: red-robed heroine on a chiseled plinth
    sx, sz = c, c
    v.fill(sx - 1, 1, sz - 1, sx + 1, 1, sz + 1, CHISELED)
    v.set(sx, 2, sz, STONE)
    v.set(sx, 3, sz, "minecraft:red_wool")             # the scarlet robe
    v.set(sx, 4, sz, "minecraft:red_wool")
    v.set(sx, 5, sz, "minecraft:smooth_quartz")        # head
    v.set(sx - 1, 4, sz, "minecraft:stone_brick_wall")  # bow arm
    v.set(sx - 1, 5, sz, "minecraft:dark_oak_fence")    # the longbow
    v.set(sx + 1, 4, sz, "minecraft:end_rod")
    for fx_, fz_ in ((sx - 2, sz), (sx + 2, sz), (sx, sz - 2), (sx, sz + 2)):
        v.set(fx_, 1, fz_, "minecraft:poppy")

    def roundhut(hx, hz, rad=3):
        """Round timber hut with a conical spruce roof and fire inside."""
        cylinder(v, hx, hz, rad, 1, 3, SPRUCE_LOG)
        cone_roof(v, hx, hz, rad + 1, 4, SPRUCE, tip=LANTERN)
        # door gap (south) + window
        v.set(hx, 1, hz - rad, "minecraft:air")
        v.set(hx, 2, hz - rad, "minecraft:air")
        v.set(hx + rad, 2, hz, GLASS)
        v.set(hx - rad, 2, hz, GLASS)
        # hearth + bunk + storage
        v.set(hx, 1, hz + 1, "minecraft:campfire")
        v.set(hx - 1, 1, hz, "minecraft:bed", {"direction": 0})
        v.set(hx + 1, 1, hz, "minecraft:chest", {"minecraft:cardinal_direction": "west"})
    roundhut(9, 12)
    roundhut(25, 12)
    roundhut(9, 24, rad=4)
    roundhut(24, 25)
    # carved guardian totems at the corners
    for tx, tz in ((8, 7), (27, 7), (7, 28), (28, 28)):
        for y in range(1, 5):
            v.set(tx, y, tz, SPRUCE_LOG if y % 2 else STRIPPED_SPRUCE)
        v.set(tx, 5, tz, "minecraft:carved_pumpkin", {"minecraft:cardinal_direction": "south"})
        v.set(tx, 6, tz, SOUL_LANTERN)
        v.set(tx + 1, 4, tz, SPRUCE_FENCE)             # totem wings
        v.set(tx - 1, 4, tz, SPRUCE_FENCE)
    # archery range along the east cliff
    for i in range(3):
        z = 18 + i * 3
        v.set(30, 1, z, "minecraft:hay_block")
        v.set(30, 2, z, "minecraft:target")
        for lx in range(25, 29):
            v.set(lx, 0, z, GRAVEL)
    v.set(26, 1, 16, "minecraft:barrel")               # arrow stock
    # fire circle on the green
    v.set(c, 1, c + 6, "minecraft:campfire")
    for bz_ in (c + 4, c + 8):
        for x in range(c - 2, c + 3):
            v.set(x, 1, bz_, STRIPPED_SPRUCE)
    v.save("knothole_glade")


def hook_coast():
    """Hook Coast: pale diorite-and-calcite port under snow — lighthouse with
    a glazed lamp room, snow-capped cottages, the ruined abbey with stained
    glass and its bell, an icy quay."""
    r = rng("struct", "hook_coast")
    W, H, L = 37, 20, 37
    v = Vox(W, H, L)
    c = W // 2
    PALE = "minecraft:polished_diorite"
    CALC = "minecraft:calcite"
    for x in range(W):
        for z in range(L):
            if z > 30:
                v.set(x, 0, z, "minecraft:water")
                if r.random() < 0.4:
                    v.set(x, 1, z, "minecraft:ice")
            else:
                v.set(x, 0, z, "minecraft:snow_block" if (x + z) % 3 else CALC)
                if r.random() < 0.12:
                    v.set(x, 1, z, "minecraft:snow_layer")
    # cleared cobble lanes
    for z in range(6, 28):
        for x in (c - 1, c, c + 1):
            v.set(x, 0, z, DEEP_TILES if (x + z) % 4 else GRAVEL)
            v.set(x, 1, z, "minecraft:air")
    # ==== lighthouse with glazed lamp room ====
    lx, lz = 6, 28
    cylinder(v, lx, lz, 4, 1, 11, PALE)
    for y in (4, 8):                                    # red signal bands
        for ang in range(0, 360, 20):
            bx_ = lx + round(math.cos(math.radians(ang)) * 4)
            bz_ = lz + round(math.sin(math.radians(ang)) * 4)
            v.set(bx_, y, bz_, "minecraft:red_wool")
    # lamp room: glass drum + sea lantern beacon
    cylinder(v, lx, lz, 3, 12, 13, GLASS)
    v.set(lx, 12, lz, "minecraft:sea_lantern")
    v.set(lx, 13, lz, "minecraft:sea_lantern")
    cone_roof(v, lx, lz, 4, 14, DEEP_TILES, tip="minecraft:end_rod")
    v.set(lx, 1, lz - 4, "minecraft:air")               # door
    v.set(lx, 2, lz - 4, "minecraft:air")
    for y in range(3, 11, 3):
        v.set(lx + 4, y, lz, GLASS)                     # stair slits
    # ==== snow-capped cottages ====
    for bx, bz in ((12, 8), (20, 8), (12, 16), (20, 16)):
        for x in range(bx, bx + 6):
            for z in range(bz, bz + 6):
                v.set(x, 0, z, CALC)
                for y in range(1, 5):
                    if x in (bx, bx + 5) or z in (bz, bz + 5):
                        v.set(x, y, z, PALE if (x + y) % 2 else CALC)
        v.fill(bx + 1, 1, bz + 1, bx + 4, 4, bz + 4, "minecraft:air")
        gable_roof_z(v, bx, bx + 5, bz, bz + 5, 5, DEEP_TILES, PALE)
        # snow drifts settled on the roof
        for x in range(bx, bx + 6):
            for z in range(bz, bz + 6):
                if r.random() < 0.4:
                    yy = 5 + min(x - bx, bx + 5 - x)
                    v.set(x, yy + 1, z, "minecraft:snow_layer")
        v.set(bx + 3, 1, bz, "minecraft:air")
        v.set(bx + 2, 3, bz, GLASS)
        v.set(bx + 1, 1, bz + 4, "minecraft:campfire")  # hearth glow
        v.set(bx + 4, 1, bz + 4, "minecraft:chest", {"minecraft:cardinal_direction": "north"})
    # ==== ruined abbey with stained glass + bell ====
    ax0, az0 = 27, 16
    aw, ad = 8, 10
    for x in range(ax0, ax0 + aw):
        for z in range(az0, az0 + ad):
            v.set(x, 0, z, PALE if (x + z) % 3 else CALC)
    for z in range(az0, az0 + ad):                      # side walls, ragged
        for x in (ax0, ax0 + aw - 1):
            h = 6 - abs(z - (az0 + ad // 2)) // 2 + r.randrange(-1, 2)
            for y in range(1, max(2, h)):
                if r.random() < 0.85:
                    v.set(x, y, z, PALE if r.random() < 0.6 else CRACK)
    for x in range(ax0, ax0 + aw):                      # gable ends
        for y in range(1, 7 - abs(x - (ax0 + aw // 2))):
            if r.random() < 0.8:
                v.set(x, y, az0, PALE)
    # stained-glass lancets in the surviving north gable
    for wx_ in (ax0 + 2, ax0 + 4, ax0 + 6):
        v.set(wx_, 2, az0, "minecraft:light_blue_stained_glass_pane")
        v.set(wx_, 3, az0, "minecraft:light_blue_stained_glass_pane")
    v.set(ax0 + 3, 5, az0, "minecraft:light_blue_stained_glass_pane")
    # altar, soul lanterns and the abbey bell
    v.set(ax0 + 3, 1, az0 + 2, "minecraft:beacon")
    v.set(ax0 + 3, 2, az0 + 2, IRON_BARS)
    v.set(ax0 + 1, 1, az0 + 3, SOUL_LANTERN)
    v.set(ax0 + 6, 1, az0 + 3, SOUL_LANTERN)
    bfx, bfz = ax0 + 5, az0 + 7                         # belfry frame
    for y in range(1, 5):
        v.set(bfx - 1, y, bfz, PALE)
        v.set(bfx + 1, y, bfz, PALE)
    v.set(bfx - 1, 5, bfz, PALE)
    v.set(bfx + 1, 5, bfz, PALE)
    v.set(bfx, 5, bfz, PALE)
    v.set(bfx, 4, bfz, "minecraft:bell")
    # pews half-buried in snow
    for z in range(az0 + 4, az0 + 8, 2):
        v.set(ax0 + 2, 1, z, "minecraft:blackstone_wall")
        v.set(ax0 + 5, 1, z, "minecraft:blackstone_wall")
    # ==== icy quay ====
    for x in range(13, 25):
        for z in range(27, 31):
            v.set(x, 1, z, SPRUCE)
            if r.random() < 0.2:
                v.set(x, 2, z, "minecraft:snow_layer")
    for x in (13, 24):
        for z in (27, 30):
            v.set(x, 2, z, SPRUCE_FENCE)
        v.set(x, 3, 30, LANTERN)
    v.set(15, 2, 28, "minecraft:barrel")
    v.set(22, 2, 29, "minecraft:chest", {"minecraft:cardinal_direction": "west"})
    v.save("hook_coast")


# ===========================================================================
# Wilderness encounters — small repeatable set dressing for the open world
# ===========================================================================

def lookout_point():
    """A grassy knoll crowned by a ring of standing stones and a pointing
    hero statue — a picnic landmark with benches and lanterns."""
    r = rng("struct", "lookout_point")
    D = 21
    v = Vox(D, 12, D)
    c = D // 2
    # the knoll: layered dome of grass
    for x in range(D):
        for z in range(D):
            d = math.hypot(x - c, z - c)
            h = max(0, int(3.2 - d * 0.34))
            v.set(x, 0, z, "minecraft:grass_block")
            for y in range(1, h + 1):
                v.set(x, y, z, "minecraft:dirt" if y < h else "minecraft:grass_block")
            if d > 4 and r.random() < 0.08:
                v.set(x, h + 1, z, "minecraft:tallgrass")
    top = 3
    # crown of weathered standing stones
    for ang in range(0, 360, 45):
        sx_ = c + round(math.cos(math.radians(ang)) * 4)
        sz_ = c + round(math.sin(math.radians(ang)) * 4)
        hh = 2 + (ang // 45) % 2
        for y in range(top + 1, top + 1 + hh):
            v.set(sx_, y, sz_, rnd_stone(r))
        if ang % 90 == 0:
            v.set(sx_, top + 1 + hh, sz_, "minecraft:cobblestone_wall")
    # pointing statue on a plinth at the summit
    v.set(c, top + 1, c, CHISELED)
    v.set(c, top + 2, c, STONE)
    v.set(c, top + 3, c, STONE)
    v.set(c, top + 4, c, "minecraft:smooth_quartz")
    v.set(c + 1, top + 3, c, "minecraft:stone_brick_wall")   # pointing arm
    v.set(c + 2, top + 3, c, "minecraft:end_rod")
    # benches and lanterns for travellers
    for bx_, bz_ in ((c - 3, c + 3), (c + 3, c - 3)):
        v.set(bx_, top + 1, bz_, SPRUCE)
        v.set(bx_ + 1, top + 1, bz_, SPRUCE)
        v.set(bx_ - 1, top + 1, bz_, SPRUCE_FENCE)
    for ang in (90, 270):
        lx_ = c + round(math.cos(math.radians(ang)) * 6)
        lz_ = c + round(math.sin(math.radians(ang)) * 6)
        v.set(lx_, 1, lz_, "minecraft:oak_fence")
        v.set(lx_, 2, lz_, "minecraft:oak_fence")
        v.set(lx_, 3, lz_, LANTERN, {"hanging": False})
    # radiating gravel footpaths
    for ang in range(0, 360, 90):
        for i in range(5, c + 1):
            px_ = c + round(math.cos(math.radians(ang + 45)) * i)
            pz_ = c + round(math.sin(math.radians(ang + 45)) * i)
            v.set(px_, 0, pz_, PATH)
    # a traveller's cache
    v.set(c - 4, top + 1, c, "minecraft:chest", {"minecraft:cardinal_direction": "east"})
    v.set(c + 4, 1, c + 7, "minecraft:campfire")
    v.save("lookout_point")


def orchard_farm():
    """A smallholding: apple orchard rows, a thatched farmhouse, a cider barn
    full of barrels, beehive, and a picket fence."""
    r = rng("struct", "orchard_farm")
    D = 29
    v = Vox(D, 12, D)
    PLASTER = "minecraft:white_terracotta"
    for x in range(D):
        for z in range(D):
            v.set(x, 0, z, "minecraft:grass_block" if r.random() < 0.85 else "minecraft:coarse_dirt")
    # picket fence ring with gate
    for x in range(1, D - 1):
        for z in (1, D - 2):
            if abs(x - D // 2) > 1:
                v.set(x, 1, z, "minecraft:oak_fence")
    for z in range(1, D - 1):
        for x in (1, D - 2):
            v.set(x, 1, z, "minecraft:oak_fence")
    # orchard rows (west half)
    for gx in (4, 9):
        for gz in (5, 11, 17, 23):
            tx, tz = gx + (gz // 7) % 2, gz
            for y in range(1, 4):
                v.set(tx, y, tz, "minecraft:oak_log")
            for dx in (-1, 0, 1):
                for dz in (-1, 0, 1):
                    if abs(dx) + abs(dz) <= 1:
                        v.set(tx + dx, 4, tz + dz, "minecraft:azalea_leaves_flowered")
            v.set(tx, 5, tz, "minecraft:oak_leaves")
            if r.random() < 0.5:
                v.set(tx + 1, 1, tz, "minecraft:sweet_berry_bush", {"growth": 3})
    # farmhouse (NE): plaster + thatch
    bx, bz = 17, 4
    for x in range(bx, bx + 8):
        for z in range(bz, bz + 6):
            v.set(x, 0, z, COBBLE)
            for y in range(1, 4):
                if x in (bx, bx + 7) or z in (bz, bz + 5):
                    v.set(x, y, z, PLASTER)
    for px_, pz_ in ((bx, bz), (bx + 7, bz), (bx, bz + 5), (bx + 7, bz + 5)):
        for y in range(1, 4):
            v.set(px_, y, pz_, SPRUCE_LOG)
    v.fill(bx + 1, 1, bz + 1, bx + 6, 3, bz + 4, "minecraft:air")
    gable_roof_z(v, bx - 1, bx + 8, bz, bz + 5, 4, "minecraft:hay_block", PLASTER)
    v.set(bx + 3, 1, bz + 5, "minecraft:air")
    v.set(bx + 3, 2, bz + 5, "minecraft:air")
    v.set(bx + 1, 2, bz + 5, GLASS)
    v.set(bx + 6, 2, bz + 5, GLASS)
    v.set(bx + 1, 1, bz + 1, "minecraft:bed", {"direction": 2})
    v.set(bx + 6, 1, bz + 1, "minecraft:chest", {"minecraft:cardinal_direction": "south"})
    # brick chimney with ember glow
    v.set(bx + 7, 4, bz + 2, COBBLE)
    v.set(bx + 7, 5, bz + 2, COBBLE)
    v.set(bx + 7, 6, bz + 2, "minecraft:campfire")
    # cider barn (SE): open front stacked with barrels
    cx0, cz0 = 18, 18
    for x in range(cx0, cx0 + 7):
        for z in range(cz0, cz0 + 6):
            v.set(x, 0, z, "minecraft:coarse_dirt")
            for y in range(1, 4):
                if z == cz0 + 5 or x in (cx0, cx0 + 6):
                    v.set(x, y, z, SPRUCE_LOG if (x + y) % 3 == 0 else SPRUCE)
    gable_roof_z(v, cx0 - 1, cx0 + 7, cz0, cz0 + 5, 4, SPRUCE, SPRUCE)
    for i, (dx, dz) in enumerate(((1, 4), (2, 4), (3, 4), (1, 3), (5, 4))):
        v.set(cx0 + dx, 1, cz0 + dz, "minecraft:barrel")
        if i < 2:
            v.set(cx0 + dx, 2, cz0 + dz, "minecraft:barrel")
    v.set(cx0 + 5, 1, cz0 + 1, "minecraft:composter")
    v.set(cx0 + 1, 1, cz0 + 1, "minecraft:hay_block")
    # beehive on a post near the orchard
    v.set(14, 1, 14, "minecraft:oak_fence")
    v.set(14, 2, 14, "minecraft:beehive")
    # flowers for the bees
    for _ in range(8):
        fx_, fz_ = 3 + r.randrange(11), 3 + r.randrange(23)
        v.set(fx_, 1, fz_, r.choice(("minecraft:poppy", "minecraft:oxeye_daisy",
                                     "minecraft:cornflower", "minecraft:red_tulip")))
    # cart track to the gate
    for z in range(2, 15):
        v.set(D // 2, 0, z, PATH)
    v.save("orchard_farm")


def fisher_creek():
    """A stilted fisher's hut over a reedy creek: jetty, drying nets, a
    beached coracle and a smoking rack."""
    r = rng("struct", "fisher_creek")
    D = 23
    v = Vox(D, 12, D)
    # creek running diagonally
    for x in range(D):
        for z in range(D):
            d = abs((x + z) - D) / 1.41
            if d < 3.2:
                v.set(x, 0, z, "minecraft:water")
                if r.random() < 0.18:
                    v.set(x, 1, z, "minecraft:waterlily")
            elif d < 4.6:
                v.set(x, 0, z, "minecraft:sand" if r.random() < 0.7 else "minecraft:gravel")
                if r.random() < 0.2:
                    v.set(x, 1, z, "minecraft:tallgrass")
            else:
                v.set(x, 0, z, "minecraft:grass_block")
                if r.random() < 0.07:
                    v.set(x, 1, z, "minecraft:fern")
    # stilted hut on the north bank, decked over the water
    hx, hz = 6, 4
    for sx_, sz_ in ((hx, hz), (hx + 5, hz), (hx, hz + 4), (hx + 5, hz + 4)):
        for y in range(1, 3):
            v.set(sx_, y, sz_, SPRUCE_LOG)            # stilts
    for x in range(hx - 1, hx + 7):
        for z in range(hz - 1, hz + 6):
            v.set(x, 3, z, SPRUCE)                    # raised deck
    for x in range(hx, hx + 6):
        for z in range(hz, hz + 5):
            for y in (4, 5):
                if x in (hx, hx + 5) or z in (hz, hz + 4):
                    v.set(x, y, z, SPRUCE if (x + z) % 3 else SPRUCE_LOG)
    v.fill(hx + 1, 4, hz + 1, hx + 4, 5, hz + 3, "minecraft:air")
    gable_roof_z(v, hx - 1, hx + 6, hz, hz + 4, 6, DEEP_TILES, SPRUCE)
    v.set(hx + 2, 4, hz + 4, "minecraft:air")          # door to jetty
    v.set(hx + 2, 5, hz + 4, "minecraft:air")
    v.set(hx + 1, 5, hz, GLASS)
    v.set(hx + 4, 5, hz, GLASS)
    v.set(hx + 1, 4, hz + 1, "minecraft:bed", {"direction": 0})
    v.set(hx + 4, 4, hz + 1, "minecraft:chest", {"minecraft:cardinal_direction": "south"})
    v.set(hx + 6, 4, hz + 2, LANTERN, {"hanging": False})
    # ladder-stair of slabs down to the jetty
    v.set(hx + 2, 2, hz + 5, SPRUCE)
    v.set(hx + 2, 1, hz + 6, SPRUCE)
    # jetty out across the creek
    jx = hx + 2
    for z in range(hz + 6, hz + 14):
        v.set(jx, 1, z, SPRUCE)
        v.set(jx + 1, 1, z, SPRUCE)
    v.set(jx, 2, hz + 13, SPRUCE_FENCE)
    v.set(jx + 1, 2, hz + 13, LANTERN, {"hanging": False})
    # drying nets: fence frames hung with wool
    for nx_, nz_ in ((13, 6), (16, 8)):
        for i in range(3):
            v.set(nx_ + i, 1, nz_, SPRUCE_FENCE)
            v.set(nx_ + i, 2, nz_, SPRUCE_FENCE)
            v.set(nx_ + i, 3, nz_, "minecraft:white_wool" if i % 2 else "minecraft:brown_wool")
    # beached coracle on the south bank
    bx_, bz_ = 16, 16
    v.set(bx_, 1, bz_, SPRUCE)
    v.set(bx_ + 1, 1, bz_, SPRUCE)
    v.set(bx_ + 2, 1, bz_, SPRUCE)
    v.set(bx_ - 1, 1, bz_, SPRUCE_FENCE)
    v.set(bx_ + 3, 1, bz_, SPRUCE_FENCE)
    # smoking rack + catch barrels
    v.set(18, 1, 13, "minecraft:campfire")
    v.set(19, 1, 13, "minecraft:barrel")
    v.set(19, 1, 14, "minecraft:barrel")
    v.set(4, 1, 13, "minecraft:barrel")
    v.save("fisher_creek")


def rose_cottage():
    """Grandmother's rose cottage: chimney smoke, a walled rose garden,
    a birch arbour and a wishing well."""
    r = rng("struct", "rose_cottage")
    D = 21
    v = Vox(D, 12, D)
    PLASTER = "minecraft:white_terracotta"
    for x in range(D):
        for z in range(D):
            v.set(x, 0, z, "minecraft:grass_block")
    # cottage
    bx, bz = 3, 3
    for x in range(bx, bx + 8):
        for z in range(bz, bz + 6):
            v.set(x, 0, z, COBBLE)
            for y in range(1, 4):
                if x in (bx, bx + 7) or z in (bz, bz + 5):
                    v.set(x, y, z, PLASTER)
    for px_, pz_ in ((bx, bz), (bx + 7, bz), (bx, bz + 5), (bx + 7, bz + 5)):
        for y in range(1, 4):
            v.set(px_, y, pz_, DARKLOG)
    v.fill(bx + 1, 1, bz + 1, bx + 6, 3, bz + 4, "minecraft:air")
    gable_roof_z(v, bx - 1, bx + 8, bz, bz + 5, 4, DEEP_TILES, PLASTER)
    # chimney with campfire smoke
    v.set(bx + 6, 4, bz + 1, COBBLE)
    v.set(bx + 6, 5, bz + 1, COBBLE)
    v.set(bx + 6, 6, bz + 1, COBBLE)
    v.set(bx + 6, 7, bz + 1, "minecraft:campfire")
    # door, windows, interior
    v.set(bx + 3, 1, bz + 5, "minecraft:air")
    v.set(bx + 3, 2, bz + 5, "minecraft:air")
    v.set(bx + 1, 2, bz + 5, GLASS)
    v.set(bx + 5, 2, bz + 5, GLASS)
    v.set(bx + 7, 2, bz + 2, GLASS)
    v.set(bx + 1, 1, bz + 1, "minecraft:bed", {"direction": 2})
    v.set(bx + 5, 1, bz + 1, "minecraft:bookshelf")
    v.set(bx + 6, 1, bz + 4, "minecraft:chest", {"minecraft:cardinal_direction": "west"})
    v.set(bx + 3, 1, bz + 1, "minecraft:cauldron")
    # walled rose garden (south half)
    gx0, gz0, gx1, gz1 = 3, 11, 17, 18
    for x in range(gx0, gx1 + 1):
        for z in (gz0, gz1):
            v.set(x, 1, z, "minecraft:cobblestone_wall")
    for z in range(gz0, gz1 + 1):
        for x in (gx0, gx1):
            v.set(x, 1, z, "minecraft:cobblestone_wall")
    v.set(10, 1, gz0, "minecraft:air")                 # garden gate
    for x in range(gx0 + 2, gx1 - 1, 3):
        for z in range(gz0 + 2, gz1, 2):
            v.set(x, 1, z, r.choice(("minecraft:rose_bush", "minecraft:peony",
                                     "minecraft:lilac", "minecraft:rose_bush")))
    for z in range(gz0 + 1, gz1):                      # central path
        v.set(10, 0, z, PATH)
    # birch arbour over the path
    for az_ in (gz0 + 3, gz0 + 4):
        v.set(9, 1, az_, "minecraft:birch_fence")
        v.set(11, 1, az_, "minecraft:birch_fence")
        v.set(9, 2, az_, "minecraft:birch_fence")
        v.set(11, 2, az_, "minecraft:birch_fence")
    for x in (9, 10, 11):
        v.set(x, 3, gz0 + 3, "minecraft:azalea_leaves_flowered")
        v.set(x, 3, gz0 + 4, "minecraft:azalea_leaves_flowered")
    # wishing well (east)
    wx, wz = 17, 6
    for x in range(wx - 1, wx + 2):
        for z in range(wz - 1, wz + 2):
            if x != wx or z != wz:
                v.set(x, 1, z, COBBLE)
    v.set(wx, 1, wz, "minecraft:water")
    v.set(wx - 1, 2, wz - 1, SPRUCE_FENCE)
    v.set(wx + 1, 2, wz + 1, SPRUCE_FENCE)
    v.set(wx - 1, 3, wz - 1, SPRUCE_FENCE)
    v.set(wx + 1, 3, wz + 1, SPRUCE_FENCE)
    for x in range(wx - 1, wx + 2):
        for z in range(wz - 1, wz + 2):
            v.set(x, 4, z, SPRUCE)
    # stray flowers + lantern post by the door
    for _ in range(6):
        v.set(1 + r.randrange(D - 2), 1, 1 + r.randrange(8),
              r.choice(("minecraft:poppy", "minecraft:oxeye_daisy", "minecraft:lilac")))
    v.set(bx + 5, 1, bz + 7, "minecraft:oak_fence")
    v.set(bx + 5, 2, bz + 7, LANTERN, {"hanging": False})
    v.save("rose_cottage")


def witchwood_stones():
    """A haunted ring of mossy monoliths around a dolmen altar, soul fire
    flickering, dead trees clawing at the sky."""
    r = rng("struct", "witchwood_stones")
    D = 25
    v = Vox(D, 14, D)
    c = D // 2
    for x in range(D):
        for z in range(D):
            v.set(x, 0, z, "minecraft:podzol" if (x + z) % 3 else "minecraft:coarse_dirt")
            if r.random() < 0.12:
                v.set(x, 1, z, "minecraft:fern" if r.random() < 0.6 else "minecraft:brown_mushroom")
    # monolith ring
    for ang in range(0, 360, 40):
        sx_ = c + round(math.cos(math.radians(ang)) * 8)
        sz_ = c + round(math.sin(math.radians(ang)) * 8)
        hh = 3 + (ang // 40) % 3
        for y in range(1, hh + 1):
            v.set(sx_, y, sz_, MOSSY if y <= 2 else rnd_stone(r))
        if ang % 120 == 0:
            v.set(sx_, hh + 1, sz_, "minecraft:soul_torch")
    # dolmen: two upright slabs + capstone over the altar
    for dx in (-2, 2):
        for y in range(1, 4):
            v.set(c + dx, y, c, CHISELED if y == 1 else MOSSY)
    for x in range(c - 2, c + 3):
        v.set(x, 4, c, DEEPSLATE_W)
    v.set(c, 1, c, "minecraft:chiseled_deepslate")     # the altar
    v.set(c, 2, c, "minecraft:soul_campfire")
    # offering chest tucked under the capstone
    v.set(c, 1, c + 1, "minecraft:chest", {"minecraft:cardinal_direction": "south"})
    # candle shrine stones
    for ang in (45, 135, 225, 315):
        px_ = c + round(math.cos(math.radians(ang)) * 4)
        pz_ = c + round(math.sin(math.radians(ang)) * 4)
        v.set(px_, 1, pz_, MCOBBLE)
        v.set(px_, 2, pz_, CANDLE, {"lit": True, "candles": 1 + (ang // 90) % 3})
    # dead trees on the rim
    for tx, tz in ((3, 4), (20, 3), (4, 20), (21, 20)):
        th = 4 + r.randrange(2)
        for y in range(1, th + 1):
            v.set(tx, y, tz, DARKLOG)
        v.set(tx + 1, th, tz, "minecraft:dark_oak_fence")   # bare branches
        v.set(tx - 1, th - 1, tz, "minecraft:dark_oak_fence")
        v.set(tx, th + 1, tz, "minecraft:dark_oak_fence")
    # scattered bones of the unlucky
    v.set(c - 5, 1, c + 5, "minecraft:bone_block")
    v.set(c + 6, 1, c - 4, "minecraft:bone_block")
    v.save("witchwood_stones")


def darkwood_camp():
    """A trader waystation deep in Darkwood: spruce palisade, covered wagon,
    tents and a watch fire — safety in numbers."""
    r = rng("struct", "darkwood_camp")
    D = 25
    v = Vox(D, 12, D)
    c = D // 2
    for x in range(D):
        for z in range(D):
            v.set(x, 0, z, "minecraft:podzol" if r.random() < 0.6 else "minecraft:coarse_dirt")
            if r.random() < 0.05:
                v.set(x, 1, z, "minecraft:fern")
    # spruce palisade ring with south gate
    for x in range(D):
        for z in range(D):
            d = math.hypot(x - c, z - c)
            if 10.0 < d <= 11.2:
                if abs(x - c) <= 2 and z < c:
                    continue                            # gate gap
                v.set(x, 1, z, SPRUCE_LOG)
                v.set(x, 2, z, SPRUCE_LOG if (x + z) % 2 else SPRUCE_FENCE)
                if (x + z) % 5 == 0:
                    v.set(x, 3, z, SPRUCE_FENCE)
    for gx in (c - 3, c + 3):                           # gate posts
        for y in range(1, 5):
            v.set(gx, y, 2, SPRUCE_LOG)
        v.set(gx, 5, 2, LANTERN, {"hanging": False})
    # covered trader wagon: plank bed, wool canopy, log wheels
    wx, wz = c + 3, c + 2
    for x in range(wx, wx + 5):
        for z in range(wz, wz + 3):
            v.set(x, 1, z, SPRUCE)
    for x in (wx, wx + 4):
        for z in (wz, wz + 2):
            v.set(x, 1, z, DARKLOG)                     # wheels
    for x in range(wx, wx + 5):
        for z in range(wz, wz + 3):
            v.set(x, 3, z, "minecraft:white_wool")      # canopy
    v.set(wx + 1, 2, wz + 1, "minecraft:chest", {"minecraft:cardinal_direction": "west"})
    v.set(wx + 3, 2, wz + 1, "minecraft:barrel")
    v.set(wx - 1, 1, wz + 1, SPRUCE_FENCE)              # wagon tongue
    # tents
    tent(v, c - 8, c - 2, 5, 2, "white", r)
    tent(v, c - 3, c + 5, 5, 2, "brown", r)
    # central watch fire ring + log seats
    v.set(c, 1, c - 2, "minecraft:campfire")
    for sx_, sz_ in ((c - 2, c - 2), (c + 2, c - 2), (c, c - 4)):
        v.set(sx_, 1, sz_, STRIPPED_SPRUCE)
    # supply crates + lantern posts
    v.set(c - 6, 1, c + 6, "minecraft:barrel")
    v.set(c - 6, 1, c + 7, "minecraft:barrel")
    v.set(c - 6, 2, c + 6, "minecraft:hay_block")
    for lx_, lz_ in ((c - 5, c - 5), (c + 5, c + 5)):
        v.set(lx_, 1, lz_, SPRUCE_FENCE)
        v.set(lx_, 2, lz_, SPRUCE_FENCE)
        v.set(lx_, 3, lz_, LANTERN, {"hanging": False})
    v.save("darkwood_camp")


def hobbe_cave():
    """A rocky hobbe warren: gaping cave mouth in a boulder mound, bone
    litter, skull totem and mushroom filth."""
    r = rng("struct", "hobbe_cave")
    D = 23
    v = Vox(D, 14, D)
    c = D // 2
    for x in range(D):
        for z in range(D):
            v.set(x, 0, z, "minecraft:coarse_dirt" if (x + z) % 3 else GRAVEL)
            if r.random() < 0.08:
                v.set(x, 1, z, "minecraft:brown_mushroom")
    # boulder mound (rear two-thirds), hollowed
    mz0 = 8
    for x in range(2, D - 2):
        for z in range(mz0, D - 1):
            d = math.hypot(x - c, z - (D - 4))
            h = max(0, int(8.5 - d * 0.8 + r.random() * 1.2))
            for y in range(1, min(h + 1, 11)):
                v.set(x, y, z, r.choice((COBBLE, "minecraft:stone", "minecraft:stone", MCOBBLE)))
    # hollow chamber + cave mouth tunnel (south-facing)
    v.fill(c - 3, 1, mz0 + 3, c + 3, 4, D - 4, "minecraft:air")
    for y in range(1, 4):
        for x in range(c - 2, c + 3):
            v.set(x, y, mz0, "minecraft:air")
            v.set(x, y, mz0 + 1, "minecraft:air")
            v.set(x, y, mz0 + 2, "minecraft:air")
    # jagged teeth over the mouth
    for x in range(c - 3, c + 4):
        v.set(x, 4, mz0, "minecraft:cobblestone_wall" if x % 2 else COBBLE)
    # warren furnishings: filth, bones, loot
    v.set(c, 1, D - 5, "minecraft:chest", {"minecraft:cardinal_direction": "south"})
    v.set(c - 2, 1, D - 6, "minecraft:bone_block")
    v.set(c + 2, 1, D - 7, "minecraft:brown_mushroom")
    v.set(c - 2, 1, mz0 + 4, "minecraft:campfire")     # cook fire
    v.set(c + 2, 1, mz0 + 4, "minecraft:bone_block")
    v.set(c, 1, mz0 + 5, "minecraft:hay_block")        # stolen bedding
    # skull totem warning outside
    v.set(c - 4, 1, 4, SPRUCE_LOG)
    v.set(c - 4, 2, 4, SPRUCE_LOG)
    v.set(c - 4, 3, 4, "minecraft:carved_pumpkin", {"minecraft:cardinal_direction": "south"})
    v.set(c - 4, 4, 4, "minecraft:soul_torch")
    # bone litter strewn down the approach
    for _ in range(5):
        bx_, bz_ = c - 3 + r.randrange(7), 2 + r.randrange(6)
        v.set(bx_, 1, bz_, "minecraft:bone_block" if r.random() < 0.5 else "minecraft:deadbush")
    v.save("hobbe_cave")


def windmill_hill():
    """A round stone windmill on a grassy rise — white sail arms, grain
    field, millstone and hay store."""
    r = rng("struct", "windmill_hill")
    D = 21
    v = Vox(D, 20, D)
    c = D // 2
    # gentle rise
    for x in range(D):
        for z in range(D):
            d = math.hypot(x - c, z - c)
            h = max(0, int(2.4 - d * 0.26))
            v.set(x, 0, z, "minecraft:grass_block")
            for y in range(1, h + 1):
                v.set(x, y, z, "minecraft:dirt" if y < h else "minecraft:grass_block")
            if d > 5 and r.random() < 0.07:
                v.set(x, h + 1, z, "minecraft:tallgrass")
    base = 2
    # tapering round tower
    cylinder(v, c, c, 4, base + 1, base + 5, STONE)
    cylinder(v, c, c, 3, base + 6, base + 10, STONE)
    cone_roof(v, c, c, 4, base + 11, SPRUCE, tip=LANTERN)
    # door + windows
    v.set(c, base + 1, c - 4, "minecraft:air")
    v.set(c, base + 2, c - 4, "minecraft:air")
    v.set(c - 4, base + 4, c, GLASS)
    v.set(c + 4, base + 4, c, GLASS)
    v.set(c, base + 8, c - 3, GLASS)
    # hub + four sail arms on the south face (fence lattice + wool cloth)
    hy = base + 9
    hz = c - 3
    v.set(c, hy, hz, DARKLOG)
    for i in range(1, 5):                               # vertical arms
        v.set(c, hy + i, hz, "minecraft:oak_fence")
        v.set(c, hy - i, hz, "minecraft:oak_fence")
        v.set(c + i, hy, hz, "minecraft:oak_fence")     # horizontal arms
        v.set(c - i, hy, hz, "minecraft:oak_fence")
    for i in range(2, 5):                               # sail cloth panels
        v.set(c + 1, hy + i, hz, "minecraft:white_wool")
        v.set(c - 1, hy - i, hz, "minecraft:white_wool")
        v.set(c + i, hy - 1, hz, "minecraft:white_wool")
        v.set(c - i, hy + 1, hz, "minecraft:white_wool")
    # interior: millstone, grain sacks, flour chest
    v.set(c, base + 1, c + 1, CHISELED)                 # millstone
    v.set(c - 1, base + 1, c + 1, "minecraft:hay_block")
    v.set(c + 1, base + 1, c + 1, "minecraft:chest", {"minecraft:cardinal_direction": "north"})
    # wheat patch on the south slope
    for x in range(c - 5, c - 1):
        for z in range(3, 7):
            v.set(x, 0, z, "minecraft:farmland", {"moisturized_amount": 7})
            v.set(x, 1, z, "minecraft:wheat", {"growth": 4 + r.randrange(4)})
    v.set(c - 3, 0, 7, "minecraft:water")
    # hay cart + millstone yard
    v.set(c + 4, 1, 4, "minecraft:hay_block")
    v.set(c + 5, 1, 4, "minecraft:hay_block")
    v.set(c + 4, 2, 4, "minecraft:hay_block")
    v.set(c + 6, 1, 4, SPRUCE_FENCE)
    # path from door down the rise
    for z in range(2, c - 3):
        v.set(c, 0, z, PATH)
    v.save("windmill_hill")


def main():
    print("building structures:")
    demon_door_arch()
    guild_hall()
    chamber_of_fate()
    oakvale_village()
    bowerstone_market()
    knothole_glade()
    hook_coast()
    silver_chest_ruin()
    focus_site()
    power_guild_courtyard()
    guild_armoury()
    guild_scriptorium()
    guild_sentinel_gate()
    power_oakvale_quay()
    power_snowspire_oracle()
    power_necropolis()
    bandit_camp()
    graveyard()
    temple_avo()
    chapel_skorm()
    arena_ring()
    lookout_point()
    orchard_farm()
    fisher_creek()
    rose_cottage()
    witchwood_stones()
    darkwood_camp()
    hobbe_cave()
    windmill_hill()


if __name__ == "__main__":
    main()

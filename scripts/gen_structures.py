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
SBRICK_SLAB = "minecraft:stone_brick_slab"
OAK_STAIR = "minecraft:oak_stairs"
SPRUCE_STAIR = "minecraft:spruce_stairs"
DARKOAK_FENCE = "minecraft:dark_oak_fence"

# Eastward displacement of the RIVER and every east-of-river feature. The
# canonical reference puts the river at ~0.53 of the campus width; the original
# build sat it at ~0.47, squeezing the west complex. Shifting the river + east
# grounds east by GUILD_EAST (and widening the campus to match) lands the
# overlay 1:1. The NW cluster (rotunda/Cullis/Skill/cave/Chamber), the Library,
# Store, Maze's Tower and the west building stay fixed so their couplings hold.
GUILD_EAST = 10
GUILD_LAYOUT = {
    "size": (112 + GUILD_EAST, 30, 108),
    "ref_rect": (185, 886, 20, 694),
    "rotunda": (26, 42, 8),
    "cullis": (15, 49),
    "skill": (15, 35),
    "wake": (20, 42),
    "quest": (22, 42),
    "quest_tables": ((22, 42), (28, 39), (28, 45)),
    "maze_tower": (46, 72, 6),
    "maze_study_y": 12,
    "upper_gallery_y": 9,
    "demon_door": (56 + GUILD_EAST, 96),
    "river_bridges": (36, 54),
    "archery": (76 + GUILD_EAST, 39, 6),
    "dueling": (91 + GUILD_EAST, 61, 6),
    "exit_c_z": 32,
    "cave_shaft": (27, 14),
    "cave_exclusion": (25, 29, 12, 16),
    "islands": ((52 + GUILD_EAST, 86, 4),),                 # ONE scarecrow island in the south pond
    "pond_bridge": ((55 + GUILD_EAST, 84), (65 + GUILD_EAST, 76)),
}


def _mat(m):
    """Allow callers to pass either a block name or a zero-arg factory that
    returns one (for per-block masonry variation)."""
    return m() if callable(m) else m


def guild_stone(r):
    """Warm Guild masonry: mostly sandstone with mossy/cut variation."""
    return r.choice([SAND, SAND, SAND, SAND_CUT, SAND_SMOOTH, STONE, MOSSY])


def guild_brick(r):
    """Canonical Guild masonry: grey STONE BRICKS with only the occasional mossy
    accent (and the rare cracked block for age) — moss kept sparse, not a
    speckle, per the reference."""
    roll = r.random()
    if roll < 0.87:
        return STONE          # stone bricks dominate
    if roll < 0.96:
        return MOSSY          # ~9% mossy accents, here and there
    return CRACK              # ~4% weathered cracked bricks


def _stair_dir(dx, dz):
    """Bedrock stair weirdo_direction ascending toward the dominant axis of
    (dx, dz):  0=+x east, 1=-x west, 2=+z south, 3=-z north."""
    if abs(dx) >= abs(dz):
        return 0 if dx > 0 else 1
    return 2 if dz > 0 else 3


def spiral_stair(v, cx, cz, radius, y0, y1, mat, post=None, steps_per_rev=16,
                 ccw=True, support=STONE):
    """A TWO-WIDE walkable spiral winding up around (cx,cz). Each course lays an
    outer stair tread plus an inner stair tread (so it is two blocks wide) on a
    solid pillar that fills to the floor, so the run is always climbable and
    reaches the storey above. Returns the OUTER tread points (x, y, z)."""
    n = y1 - y0
    outer = []
    prev = None
    for i in range(n + 1):
        ang = (i / steps_per_rev) * 2 * math.pi * (1 if ccw else -1)
        ox = cx + round(math.cos(ang) * radius)
        oz = cz + round(math.sin(ang) * radius)
        ix = cx + round(math.cos(ang) * (radius - 1))
        iz = cz + round(math.sin(ang) * (radius - 1))
        y = y0 + i
        dx, dz = (ox - prev[0], oz - prev[1]) if prev else (0, 1)
        if dx == 0 and dz == 0:
            dx = 1
        st = {"weirdo_direction": _stair_dir(dx, dz), "upside_down_bit": False}
        v.set(ox, y, oz, mat, st)
        if (ix, iz) != (ox, oz):
            v.set(ix, y, iz, mat, st)              # inner tread -> two wide
        if support:
            for yy in range(y0 - 1, y):            # solid carriage under both treads
                v.set(ox, yy, oz, support)
                v.set(ix, yy, iz, support)
        outer.append((ox, y, oz))
        prev = (ox, oz)
    if post:
        for y in range(y0, y1 + 2):
            v.set(cx, y, cz, post)
    return outer


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


# blocks a lantern/torch can NOT rest on or hang from (so they don't anchor decor)
_NONSUPPORT = {
    "minecraft:air", "minecraft:water", "minecraft:lantern", "minecraft:soul_lantern",
    "minecraft:torch", "minecraft:soul_torch", "minecraft:redstone_torch",
    "minecraft:vine", "minecraft:tallgrass", "minecraft:fern", "minecraft:large_fern",
    "minecraft:end_rod", "minecraft:white_candle", "minecraft:red_carpet",
    "minecraft:rose_bush", "minecraft:peony", "minecraft:lilac", "minecraft:poppy",
    "minecraft:allium", "minecraft:oxeye_daisy", "minecraft:cornflower",
    "minecraft:azure_bluet",
}


def fix_floating_decor(v):
    """Audit every lantern in the canvas and re-seat it so nothing floats:
    keep it standing if a block sits below, flip it to hanging if a block sits
    above, otherwise mount a wall torch on an adjacent wall — or, failing that,
    drop it. Solves the 'floating lanterns / detached decor' that crept in when
    posts and ceilings shifted under the build."""
    LANT = {"minecraft:lantern", "minecraft:soul_lantern"}

    def name_at(x, y, z):
        if 0 <= x < v.sx and 0 <= y < v.sy and 0 <= z < v.sz:
            return v.palette[v.grid[v.idx(x, y, z)]][0]
        return "minecraft:air"

    def solid(x, y, z):
        return name_at(x, y, z) not in _NONSUPPORT

    fixes = []
    for x in range(v.sx):
        for y in range(v.sy):
            for z in range(v.sz):
                nm = name_at(x, y, z)
                if nm not in LANT:
                    continue
                if solid(x, y - 1, z):
                    fixes.append((x, y, z, nm, {"hanging": False}))
                elif solid(x, y + 1, z):
                    fixes.append((x, y, z, nm, {"hanging": True}))
                else:
                    torch = "minecraft:soul_torch" if "soul" in nm else "minecraft:torch"
                    side = None
                    for dx, dz, face in ((-1, 0, "east"), (1, 0, "west"),
                                         (0, -1, "south"), (0, 1, "north")):
                        if solid(x + dx, y, z + dz):
                            side = face
                            break
                    if side:
                        fixes.append((x, y, z, torch, {"torch_facing_direction": side}))
                    else:
                        fixes.append((x, y, z, "minecraft:air", None))
    for (x, y, z, nm, st) in fixes:
        v.grid[v.idx(x, y, z)] = v._pid(nm, st)
    return len(fixes)


def guild_hall():
    """The Heroes' Guild of Albion — laid out to match the canonical ground plan.

    You enter from the WEST (Lookout / Exit A) into the domed MAP ROOM: the
    Cullis Gate sits in its south-west nook, the Skill/Experience shrine in its
    north-west nook, and twin grand stairs behind them climb to the upper
    dormitory. The LIBRARY and the Guild-Cave / Chamber exit (B) lie NORTH; the
    DINING HALL & KITCHEN lie EAST and the STORE to the south. A curved RIVER
    runs north-south through the grounds, crossed by two plank bridges and, in
    the north, a covered STONE hallway to the north-east KITCHEN / STORES /
    DORMITORY block. Across the river are the ARCHERY RANGE and DUELING RING
    (Exit C, to the Guild Woods). A covered stone corridor runs south to MAZE'S
    TOWER on its moated island; past the scarecrow islands at the far south
    stands the Guild DEMON DOOR. Every room connects and the waking Hero lands
    dry on the crimson runner before the Map."""
    r = rng("struct", "guild")
    W, H, L = GUILD_LAYOUT["size"]        # expanded footprint (was 92x100) so the campus
    v = Vox(W, H, L)              # fits to scale: room for the east grounds + forest
    #                              buffer, the tower garden and a denser complex.
    #  NW cluster (rotunda/library/Cullis/Skill/spiral/chamber/caves/gate) keeps its
    #  local coords so the runtime chamber + cave carve stay coupled; the perimeter
    #  wall, Exit C and corners derive from W/L and shift out automatically. main.js
    #  dimension couplings (ticking/sample/blend/skirt/loot/bounds/woods) updated to match.
    # The Heroes' Guild is grey STONE-BRICK masonry — stone bricks throughout with
    # only sparse mossy accents (and the rare cracked block), chiseled-stone-brick
    # trim and stone-brick parapets. The old warm sandstone palette is REMAPPED
    # here (local aliases) so every wall in this function reads as stone brick
    # without rewriting each call site.
    warm = lambda: guild_brick(r)
    SAND = STONE
    SAND_CUT = STONE
    SAND_SMOOTH = "minecraft:smooth_stone"   # pale floors/links, contrasts the bricks
    SAND_CHIS = CHISELED                      # chiseled stone-brick trim
    SAND_WALL = "minecraft:stone_brick_wall"  # parapets / balustrades

    # ---- feature anchors (kept in lock-step with main.js placeGuildNear) ----
    ROT_X, ROT_Z, ROT_R = GUILD_LAYOUT["rotunda"]       # Map Room rotunda
    CGX, CGZ = GUILD_LAYOUT["cullis"]                   # Cullis Gate (SW nook)
    SKX, SKZ = GUILD_LAYOUT["skill"]                    # Skill shrine (NW nook)
    WAKE_X, WAKE_Z = GUILD_LAYOUT["wake"]               # wake on the crimson runner, facing east
    QUEST_X, QUEST_Z = GUILD_LAYOUT["quest"]            # quest lectern off the central axis
    QUEST_TABLES = GUILD_LAYOUT["quest_tables"]
    TWR_X, TWR_Z, TWR_R = GUILD_LAYOUT["maze_tower"]    # Maze's Tower
    STUDY_Y = GUILD_LAYOUT["maze_study_y"]              # Maze stands on floor 3
    UP_Y = GUILD_LAYOUT["upper_gallery_y"]
    DOOR_X, DOOR_Z = GUILD_LAYOUT["demon_door"]         # Demon Door crag (far south)
    BRIDGE_ZS = GUILD_LAYOUT["river_bridges"]
    ARCH_X, ARCH_Z, ARCH_R = GUILD_LAYOUT["archery"]
    DUEL_X, DUEL_Z, DUEL_R = GUILD_LAYOUT["dueling"]
    EXIT_C_Z = GUILD_LAYOUT["exit_c_z"]
    EAST = GUILD_EAST          # eastward shift of the river + east-of-river features

    # ================= GROUND: a level, SMOOTH grass lawn =================
    # Mostly clean grass with only a faint wash of moss (near-grass green) and the
    # rare podzol fleck, so the open grounds read smooth — not a brown-speckled
    # patchwork. Paths (gravel) and gardens are laid over this later.
    for x in range(W):
        for z in range(L):
            roll = r.random()
            v.set(x, 0, z, "minecraft:grass_block" if roll < 0.965 else "minecraft:moss_block")

    # ================= THE CURVED RIVER + south pond =================
    # The river BOWS gently north-south down the tower's EAST flank with ORGANIC
    # banks (a meander + ragged edge), then broadens into a south pond that laps
    # the tower's SOUTH flank — so Maze's Tower keeps open water on exactly TWO
    # sides (east + south). Its NORTH (cloister + graves garden) and WEST stay dry.
    # The WEST quay column (x<=50) is always kept dry so the riverside causeway,
    # grand stair and plank-bridge abutments still land on solid ground.
    def _wh(x, z):                                  # deterministic 0..1 hash (no rng order issues)
        return (((x * 73856093) ^ (z * 19349663)) & 0xffff) / 65535.0

    def _river_center(z):
        pts = ((4, 53.0 + EAST), (24, 53.0 + EAST), (42, 52.4 + EAST), (58, 53.8 + EAST),
               (70, 56.0 + EAST), (78, 58.0 + EAST), (88, 55.0 + EAST))
        if z <= pts[0][0]:
            return pts[0][1]
        for (z0, x0), (z1, x1) in zip(pts, pts[1:]):
            if z <= z1:
                t = (z - z0) / max(1, z1 - z0)
                return x0 + (x1 - x0) * t
        return pts[-1][1]

    def _river_half_width(z):
        if z < 42:
            return 2.1
        if z < 62:
            return 2.6
        if z < 75:
            return 3.4
        return 4.2

    def is_water(x, z):
        dt = math.hypot(x - TWR_X, z - TWR_Z)
        if dt <= TWR_R + 0.6:
            return False                       # the tower island itself is dry
        for ix, iz, ir in GUILD_LAYOUT["islands"]:
            if math.hypot((x - ix) * 1.05, z - iz) <= ir + 0.25:
                return False
        if 4 <= z <= 82:
            cen = _river_center(z)
            half = _river_half_width(z)
            edge = half + (0.45 if _wh(x, z) < 0.18 else 0.0)
            if abs(x - cen) <= edge and x >= 50 + EAST:
                return True
        if 36 <= x <= 80 + EAST and 70 <= z <= 100:
            wobble = 0.8 if _wh(x, z) < 0.22 else (-0.35 if _wh(x, z) > 0.86 else 0.0)
            # tower_moat stays put (the tower at TWR_X keeps its own moat WEST of
            # the eastward river); the river mouth + pond basins shift east by EAST.
            tower_moat = ((x - 49) / 9.0) ** 2 + ((z - 75) / 7.2) ** 2 <= 1.0 + wobble * 0.04
            river_mouth = ((x - (56 + EAST)) / 7.0) ** 2 + ((z - 76) / 6.0) ** 2 <= 1.0 + wobble * 0.04
            island_basin = ((x - (54 + EAST)) / 13.5) ** 2 + ((z - 86) / 12.2) ** 2 <= 1.0 + wobble * 0.05
            south_basin = ((x - (57 + EAST)) / 16.0) ** 2 + ((z - 91) / 8.8) ** 2 <= 1.0 + wobble * 0.05
            east_channel = ((x - (60 + EAST)) / 8.0) ** 2 + ((z - 83) / 5.5) ** 2 <= 1.0 + wobble * 0.05
            if tower_moat or river_mouth or island_basin or south_basin or east_channel:
                return True
        return False
    for x in range(W):
        for z in range(L):
            if is_water(x, z):
                v.set(x, 0, z, "minecraft:water")

    # ================= PERIMETER: the western main wall + GATEHOUSE =============
    # A proper crenellated STONE-BRICK curtain wall with a battered base, a stepped
    # GATEHOUSE on the entrance axis (twin towers flanking a tall chiseled arch,
    # gate lanterns) and a clean paved main road running in from the world.
    # Replaces the old cobble wall + carpet-on-grass.
    WALL_X = 10
    GATE_Z = ROT_Z                              # the gate lines up with the Map Room

    def crenellate(x, z, y):                    # alternating merlon cap on a wall top
        v.set(x, y, z, SAND_WALL if (x + z) % 2 == 0 else CHISELED)

    for z in range(2, L - 2):                    # west curtain wall
        if abs(z - GATE_Z) <= 2:
            continue                             # the gate stays open
        v.set(WALL_X, 1, z, MCOBBLE if r.random() < 0.16 else STONE)   # battered base
        for y in range(2, 5):
            v.set(WALL_X, y, z, warm())
        crenellate(WALL_X, z, 5)
        if z % 6 == 0:                           # arrow-slit windows
            v.set(WALL_X, 3, z, GLASS)
    for gz in (GATE_Z - 3, GATE_Z + 3):          # twin gate towers (taller, chiseled)
        for y in range(1, 7):
            v.set(WALL_X, y, gz, CHISELED if y in (1, 6) else warm())
        v.set(WALL_X, 7, gz, SAND_WALL)
        v.set(WALL_X, 8, gz, LANTERN, {"hanging": False})
    for gz in (GATE_Z - 2, GATE_Z + 2):          # gate jambs
        for y in range(1, 6):
            v.set(WALL_X, y, gz, warm())
    for gz in range(GATE_Z - 2, GATE_Z + 3):     # arch lintel over the opening
        v.set(WALL_X, 5, gz, CHISELED)
    for gz in (GATE_Z - 1, GATE_Z, GATE_Z + 1):
        v.set(WALL_X, 6, gz, warm())
    v.set(WALL_X, 7, GATE_Z, LANTERN, {"hanging": True})
    # the MAIN ROAD: a 5-wide stone-brick avenue from the gate west to the world,
    # plain paved stone (the red carpet is reserved for the boasting platform deck)
    for x in range(0, WALL_X):
        for z in range(GATE_Z - 2, GATE_Z + 3):
            v.set(x, 0, z, STONE if z in (GATE_Z - 2, GATE_Z + 2) else SAND_SMOOTH)
    for x in range(0, WALL_X, 3):                # lamp-posts lining the avenue
        for z in (GATE_Z - 3, GATE_Z + 3):
            v.set(x, 0, z, STONE)
            v.set(x, 1, z, DARKOAK_FENCE)
            v.set(x, 2, z, LANTERN, {"hanging": False})
    # the rest of the perimeter: a lower crenellated stone-brick wall (N / S / E)
    for x in range(2, W - 2):
        for z in (2, L - 3):
            v.set(x, 1, z, MCOBBLE if r.random() < 0.14 else STONE)
            for y in range(2, 4):
                v.set(x, y, z, warm())
            if x % 2 == 0:
                v.set(x, 4, z, SAND_WALL)
    for z in range(2, L - 2):
        v.set(W - 3, 1, z, MCOBBLE if r.random() < 0.14 else STONE)
        for y in range(2, 4):
            v.set(W - 3, y, z, warm())
        if z % 2 == 0:
            v.set(W - 3, 4, z, SAND_WALL)
    for cx_, cz_ in ((WALL_X, 2), (W - 3, 2), (WALL_X, L - 3), (W - 3, L - 3)):  # corner turrets
        for y in range(1, 6):
            v.set(cx_, y, cz_, warm() if y < 5 else CHISELED)
        v.set(cx_, 6, cz_, LANTERN, {"hanging": False})

    # ================= BOASTING PLATFORM (west, outside the gate) ===============
    # A handsome raised stone DAIS facing the lawn: a stone-brick plinth (deck
    # surface y3), a back screen hung with Fable-red banners under a chiseled
    # cornice, corner lamp-posts, a broad flight of front steps down to the lawn,
    # and a plain paved spur linking the deck down to the main road. The red carpet
    # is laid ONLY on the deck itself (not the road or the approach spur).
    # The runtime gathers the crowd before it (main.js: stage centre local 4,26
    # deck y3, crowd at 8,31 facing 4,27) — the deck stays centred on (4,26).
    BX, BZ = 4, 26
    for x in range(1, 8):                            # 1-tall plinth ledge (surface y2)
        for z in range(21, 32):
            v.set(x, 1, z, MOSSY if (x + z) % 7 == 0 else STONE)
    for x in range(2, 7):                            # raised deck (stand at y3)
        for z in range(22, 30):
            v.set(x, 2, z, SAND_SMOOTH if (x + z) % 3 else STONE)
    for i, sz in enumerate((31, 30)):                # broad front steps up the SE face
        for sx in range(3, 6):
            v.set(sx, 1 + i, sz, SBRICK_STAIR, {"weirdo_direction": 3, "upside_down_bit": False})
    for x in range(2, 7):                            # back screen + red banner + cornice
        v.set(x, 3, 22, warm())
        v.set(x, 4, 22, RED if 2 < x < 6 else CHISELED)
        v.set(x, 5, 22, CHISELED)
    for sx in (2, 6):                                # screen returns down the sides
        v.set(sx, 3, 23, warm())
        v.set(sx, 4, 23, RED)
    for (lx, lz) in ((2, 23), (6, 23), (2, 28), (6, 28)):   # corner lamp-posts
        v.set(lx, 3, lz, DARKOAK_FENCE)
        v.set(lx, 4, lz, LANTERN, {"hanging": False})
    for z in range(23, 30):                          # red carpet down the deck centre (the ONLY carpet)
        v.set(BX, 3, z, "minecraft:red_carpet")
    for z in range(32, GATE_Z - 1):                  # plain paved stone spur linking the deck to the avenue
        for sx in (BX, BX + 1):
            v.set(sx, 0, z, SAND_SMOOTH)
    # a trader's covered cart (cloth canopy hoisted on posts, dark-oak wheels),
    # set back from the gate path so the Hero meets the trader off the road
    cwx, cwz = 2, 47
    for x in range(cwx, cwx + 4):
        for z in (cwz, cwz + 1):
            v.set(x, 1, z, SPRUCE)
    for wz in (cwz, cwz + 1):
        v.set(cwx + 4, 1, wz, DARKLOG)
    for px, pz in ((cwx, cwz), (cwx + 3, cwz), (cwx, cwz + 1), (cwx + 3, cwz + 1)):
        v.set(px, 2, pz, SPRUCE_FENCE)
        v.set(px, 3, pz, SPRUCE_FENCE)
    for x in range(cwx, cwx + 4):
        for z in (cwz, cwz + 1):
            v.set(x, 4, z, "minecraft:white_wool")
    v.set(cwx + 1, 2, cwz, "minecraft:barrel")
    v.set(cwx + 2, 2, cwz + 1, "minecraft:chest", {"minecraft:cardinal_direction": "south"})

    # ---- a small room helper: walled box with a floor and (optional) roof ----
    def room(x0, z0, x1, z1, wh, floor=None, roof="gable"):
        if floor:
            for x in range(x0, x1 + 1):
                for z in range(z0, z1 + 1):
                    v.set(x, 0, z, floor() if callable(floor) else floor)
        for x in range(x0, x1 + 1):
            for z in (z0, z1):
                for y in range(1, wh):
                    v.set(x, y, z, warm())
        for z in range(z0, z1 + 1):
            for x in (x0, x1):
                for y in range(1, wh):
                    v.set(x, y, z, warm())
        if roof == "gable":
            gable_roof_z(v, x0, x1, z0, z1, wh, SLATE, SAND)
        elif roof == "hip":
            hip_roof(v, x0, x1, z0, z1, wh, SLATE, levels=3, cap=DEEP_TILES)

    def door(x, z, axis="x", h=3):
        if axis == "x":
            v.fill(x, 1, z - 1, x, h, z + 1, "minecraft:air")
        else:
            v.fill(x - 1, 1, z, x + 1, h, z, "minecraft:air")

    # ================= MAP ROOM ROTUNDA (the hub) =================
    for x in range(ROT_X - ROT_R, ROT_X + ROT_R + 1):
        for z in range(ROT_Z - ROT_R, ROT_Z + ROT_R + 1):
            if math.hypot(x - ROT_X, z - ROT_Z) <= ROT_R + 0.4:
                v.set(x, 0, z, DEEP_TILES if (x + z) % 4 == 0 else STONE)
    ring_wall(v, ROT_X, ROT_Z, ROT_R, 1, UP_Y, warm,
              gaps=[(0, 12), (90, 12), (180, 12), (270, 12)])   # E/S/W/N doorways
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
    # the breathing relief Map of Albion
    for x in range(ROT_X - 4, ROT_X + 5):
        for z in range(ROT_Z - 4, ROT_Z + 5):
            d = math.hypot(x - ROT_X, z - ROT_Z)
            if d <= 4.3:
                v.set(x, 0, z, DARKOAK)
            if d <= 3.4:
                roll = r.random()
                v.set(x, 1, z,
                      "minecraft:lapis_block" if roll < 0.34 else
                      "minecraft:moss_block" if roll < 0.62 else
                      "minecraft:sand" if roll < 0.74 else
                      "minecraft:emerald_block" if roll < 0.9 else GOLD)
    v.set(ROT_X, 2, ROT_Z, "minecraft:sea_lantern")
    v.set(ROT_X, 3, ROT_Z, "minecraft:end_rod")
    quest_dirs = {
        (ROT_X - 4, ROT_Z): "west",
        (ROT_X + 2, ROT_Z - 3): "north",
        (ROT_X + 2, ROT_Z + 3): "south",
    }
    for qx, qz in QUEST_TABLES:
        v.set(qx, 1, qz, "minecraft:lectern",
              {"minecraft:cardinal_direction": quest_dirs.get((qx, qz), "east")})
    # crimson runner from the west gate, through the rotunda, to the map
    for x in range(9, ROT_X + 1):
        for z in (WAKE_Z - 1, WAKE_Z, WAKE_Z + 1):
            v.set(x, 0, z, RED)
    # the MAIN ENTRANCE is a covered stone corridor from the gate to the Map Room
    for x in range(11, ROT_X - ROT_R + 1):           # 11 .. 18
        for y in range(1, 5):
            v.set(x, y, WAKE_Z - 2, warm())
            v.set(x, y, WAKE_Z + 2, warm())
        v.fill(x, 1, WAKE_Z - 1, x, 4, WAKE_Z + 1, "minecraft:air")
        for z in range(WAKE_Z - 2, WAKE_Z + 3):      # gabled stone roof
            v.set(x, 5, z, SLATE if (x + z) % 2 else DEEP_TILES)
        if x % 3 == 0:
            v.set(x, 4, WAKE_Z, LANTERN, {"hanging": True})
    for y in range(1, 5):                            # framed portal at the gatehead
        v.set(11, y, WAKE_Z - 2, SAND_CHIS)
        v.set(11, y, WAKE_Z + 2, SAND_CHIS)

    # TWIN grand stairs to the upper gallery — a symmetric DOUBLE staircase set
    # along the SOUTH arc. Two parallel flights climb in OPPOSITE directions up
    # onto a ring GALLERY that rings a central well looking down on the Map. Both
    # runs ride on slim off-axis piers (never on the x=ROT_X doorway line), so all
    # four ground arches stay walkable: the south approach passes clean UNDER the
    # stairs. (The upper stone-arch BRIDGE to the Dining hall joins this gallery.)
    # Wrapped lobby stairs are installed after the Cullis/Skill nooks below.
    # ring GALLERY deck at y=UP_Y — an annulus that carries the twin stair-tops and
    # the Dining bridge while a central WELL stays open over the breathing Map
    # ===== CULLIS GATE + SKILL SHRINE — ROUNDED nooks that merge into the Map
    #       Room's western wall (apsidal bays, not square out-buildings) =====
    def merge_nook(cx, cz, rad, wh, floor):
        for x in range(cx - rad, cx + rad + 1):
            for z in range(cz - rad, cz + rad + 1):
                d = math.hypot(x - cx, z - cz)
                if d <= rad + 0.4:
                    v.set(x, 0, z, floor)
                # the curved wall, dropped where it overlaps the rotunda (they fuse)
                if rad - 0.6 < d <= rad + 0.45 and math.hypot(x - ROT_X, z - ROT_Z) > ROT_R - 0.3:
                    for y in range(1, wh):
                        v.set(x, y, z, warm())
        cone_roof(v, cx, cz, rad, wh, SLATE, tip="minecraft:end_rod")
        # an open throat fuses the nook interior straight into the rotunda — but
        # STOPS at the rotunda floor so it never carves through the Map relief
        steps = max(1, int(round(math.hypot(ROT_X - cx, ROT_Z - cz))))
        for i in range(steps + 1):
            px = round(cx + (ROT_X - cx) * i / steps)
            pz = round(cz + (ROT_Z - cz) * i / steps)
            if math.hypot(px - ROT_X, pz - ROT_Z) <= ROT_R - 1.5:
                break                       # reached the Map Room floor; spare the Map
            for ox, oz in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)):
                v.set(px + ox, 0, pz + oz, floor)
                v.fill(px + ox, 1, pz + oz, px + ox, 3, pz + oz, "minecraft:air")
    merge_nook(CGX, CGZ, 4, 6, DEEP_TILES)          # Cullis Gate (SW bay)
    merge_nook(SKX, SKZ, 4, 6, DEEP_TILES)          # Skill Shrine (NW bay)
    # Cullis Gate — a FLAT warded platform (no pedestal); its glow, beam and
    # swirling particles are animated at runtime when a Hero stands on it
    for x in range(CGX - 3, CGX + 4):
        for z in range(CGZ - 3, CGZ + 4):
            d = math.hypot(x - CGX, z - CGZ)
            if d <= 3.2:
                v.set(x, 0, z, CHISELED if d <= 1.4 else DEEP_TILES)
            if 1.6 < d <= 2.5:
                v.set(x, 0, z, OBSIDIAN if (x + z) % 2 else "minecraft:crying_obsidian")
    v.set(CGX, 0, CGZ, "minecraft:sea_lantern")          # flush glowing core (cullis detect)
    v.set(CGX, 8, CGZ, LANTERN, {"hanging": True})       # hung from the y9 cone apex (y6 floats -> fix_floating_decor would strip it)
    # Skill / Experience Shrine — also a FLAT platform; its green training light
    # and particles are animated at runtime
    for x in range(SKX - 3, SKX + 4):
        for z in range(SKZ - 3, SKZ + 4):
            d = math.hypot(x - SKX, z - SKZ)
            if d <= 3.2:
                v.set(x, 0, z, CHISELED if d <= 1.4 else DEEP_TILES)
            if 1.6 < d <= 2.5:
                v.set(x, 0, z, "minecraft:emerald_block" if (x + z) % 2 else "minecraft:sea_lantern")
    v.set(SKX, 0, SKZ, "minecraft:sea_lantern")          # flush glowing core
    v.set(SKX, 8, SKZ, LANTERN, {"hanging": True})       # hung from the y9 cone apex (y6 floats -> fix_floating_decor would strip it)

    # Grand lobby stairs: two wall-hugging wrapped flights start just after the
    # Cullis and Skill nooks, then meet on the rear platform over the dining arch.
    def inward_offset(x, z):
        dx = 1 if x < ROT_X else (-1 if x > ROT_X else 0)
        dz = 1 if z < ROT_Z else (-1 if z > ROT_Z else 0)
        if abs(x - ROT_X) >= abs(z - ROT_Z):
            return dx, 0
        return 0, dz

    stair_cells = set()

    def place_wrapped_stair(path):
        for i, (sx, sz) in enumerate(path):
            sy = 1 + i // 2
            ox, oz = inward_offset(sx, sz)
            cells = ((sx, sz), (sx + ox, sz + oz))
            mat = SBRICK_SLAB if i % 2 == 0 else STONE
            for cx_, cz_ in cells:
                v.set(cx_, sy, cz_, mat)
                stair_cells.add((cx_, cz_))
                for yy in range(sy + 1, min(UP_Y + 4, sy + 4)):
                    v.set(cx_, yy, cz_, "minecraft:air")
            if i % 4 == 0 or sy >= UP_Y - 1:
                for yy in range(1, sy):
                    v.set(sx, yy, sz, SAND_CHIS if yy in (1, sy - 1) else STONE)

    north_stair = ((20, 38), (21, 37), (22, 36), (23, 36),
                   (24, 35), (25, 35), (26, 35), (27, 35),
                   (28, 36), (29, 36), (30, 37), (31, 38),
                   (31, 39), (32, 40), (32, 41), (32, 42))
    south_stair = ((20, 46), (21, 47), (22, 48), (23, 48),
                   (24, 49), (25, 49), (26, 49), (27, 49),
                   (28, 48), (29, 48), (30, 47), (31, 46),
                   (31, 45), (32, 44), (32, 43), (32, 42))
    place_wrapped_stair(north_stair)
    place_wrapped_stair(south_stair)

    rear_deck = set()
    for x in range(30, 33):
        for z in range(38, 47):
            d = math.hypot(x - ROT_X, z - ROT_Z)
            if 4.2 < d <= ROT_R - 0.5 and (x, z) not in stair_cells:
                v.set(x, UP_Y, z, SPRUCE)
                rear_deck.add((x, z))
                for yy in range(UP_Y + 1, UP_Y + 4):
                    v.set(x, yy, z, "minecraft:air")
    for x, z in rear_deck:
        if x == 30 or z in (38, 46):
            if (x, z) not in stair_cells:
                v.set(x, UP_Y + 1, z, DARKOAK_FENCE)
    for z in range(ROT_Z - 2, ROT_Z + 3):
        v.set(ROT_X + 6, UP_Y - 1, z, LANTERN if z == ROT_Z else DARKOAK_FENCE,
              {"hanging": True} if z == ROT_Z else None)

    # ================= LIBRARY (north) + Guild-Cave exit (B) =================
    lx0, lx1, lz0, lz1 = 18, 36, 16, 30
    room(lx0, lz0, lx1, lz1, 9, floor=lambda: DARKOAK if r.random() < 0.5 else SPRUCE, roof="hip")
    door(ROT_X, ROT_Z - ROT_R, axis="z")            # rotunda N <-> library S
    door(ROT_X, lz1, axis="z")                       # aligned with the link corridor (x=ROT_X)
    for z in range(lz0 + 2, lz1 - 1):
        if z % 2:
            for y in range(1, 8):
                if y not in (4, 5):
                    v.set(lx0 + 1, y, z, "minecraft:bookshelf")
                    v.set(lx1 - 1, y, z, "minecraft:bookshelf")
    for i, z in enumerate(range(lz0 + 3, lz1 - 1, 4)):
        v.set(lx0 + 4, 1, z, "minecraft:lectern",
              {"minecraft:cardinal_direction": "east" if i % 2 else "west"})
    v.set((lx0 + lx1) // 2, 7, (lz0 + lz1) // 2, LANTERN, {"hanging": True})
    # the Guild-Cave exit (B): a chiseled stone archway into an alcove whose
    # floor opens onto a 3x3 spiral stair (carved at runtime) winding down to the
    # Chamber of Fate. cvx/cvz anchor the spiral — keep in sync with main.js.
    cvx, cvz = (lx0 + lx1) // 2, lz0 - 2          # spiral centre (local 27,14)
    door(cvx, lz0, axis="z", h=4)                # library -> caves alcove
    for x in range(cvx - 2, cvx + 3):            # the alcove walls
        for z in range(lz0 - 4, lz0):
            v.set(x, 0, z, COBBLE if r.random() < 0.6 else MCOBBLE)
            for y in range(1, 6):
                if x in (cvx - 2, cvx + 2) or z == lz0 - 4:
                    v.set(x, y, z, COBBLE if r.random() < 0.7 else MCOBBLE)
    for x in range(cvx - 1, cvx + 2):            # a stone arch over the descent
        v.set(x, 5, cvz, CHISELED)
    v.set(cvx - 1, 4, cvz, CHISELED)
    v.set(cvx + 1, 4, cvz, CHISELED)
    v.fill(cvx - 1, 0, cvz - 1, cvx + 1, 0, cvz + 1, "minecraft:air")   # mouth of the shaft
    v.set(cvx, 0, cvz, "minecraft:chiseled_stone_bricks")              # central pillar cap
    v.set(cvx - 2, 4, lz0 - 2, SOUL_LANTERN)
    v.set(cvx + 2, 4, lz0 - 2, SOUL_LANTERN)

    # ===== NORTH WING (the missing top range) — a roofed hall wrapping the Guild-
    #       Cave stair-well at the very TOP of the complex. It carries the Library's
    #       stonework NORTH, keeps the spiral shaft (27,14) open as its stair-well,
    #       links SOUTH into the Library (through the cave alcove + a wide arch) and
    #       reaches EAST by the covered TOP bridge over the river to the NE block.
    #       This is the wing the relocated top bridge attaches to. =====
    nwgx0, nwgx1, nwgz0, nwgz1 = 22, 40, 6, 15
    for x in range(nwgx0, nwgx1 + 1):
        for z in range(nwgz0, nwgz1 + 1):
            alcove = (25 <= x <= 29 and 12 <= z <= 15)     # keep the rough cave alcove blocks
            if not alcove:
                v.set(x, 0, z, STONE if (x + z) % 4 else DEEP_TILES)   # paved floor
                v.fill(x, 1, z, x, 8, z, "minecraft:air")              # clear interior
            v.set(x, 9, z, SLATE if (x + z) % 2 else DEEP_TILES)       # roof at common eave
    for x in range(nwgx0, nwgx1 + 1):                  # north wall (z6)
        for y in range(1, 9):
            v.set(x, y, nwgz0, warm())
    for z in range(nwgz0, nwgz1 + 1):                  # west (x22) + east (x40) walls
        for y in range(1, 9):
            v.set(nwgx0, y, z, warm())
            v.set(nwgx1, y, z, warm())
    for x in range(nwgx0 + 2, nwgx1, 4):               # north windows
        v.set(x, 3, nwgz0, GLASS); v.set(x, 6, nwgz0, GLASS)
    for z in range(nwgz0 + 2, nwgz1 - 1, 3):           # west windows
        v.set(nwgx0, 3, z, GLASS)
    v.fill(26, 1, 12, 28, 4, 12, "minecraft:air")      # open the alcove's north wall into the wing
    v.fill(33, 1, 16, 35, 3, 16, "minecraft:air")      # wide arch SOUTH into the Library
    v.set(32, 3, 16, SAND_CHIS); v.set(36, 3, 16, SAND_CHIS)
    v.fill(nwgx1, 1, 7, nwgx1, 4, 8, "minecraft:air")  # NE door -> the covered top bridge
    v.set(nwgx1, 5, 7, SAND_CHIS); v.set(nwgx1, 5, 8, SAND_CHIS)
    # a low rail ringing the open stair-well, a couple of bunks, a hanging lantern
    for (rx, rz) in ((24, 13), (24, 14), (24, 15), (30, 13), (30, 14), (30, 15),
                     (26, 11), (27, 11), (28, 11)):
        if v.grid[v.idx(rx, 1, rz)] == v._pid("minecraft:air"):
            v.set(rx, 1, rz, DARKOAK_FENCE)
    for bz in (7, 9):
        v.set(nwgx1 - 2, 1, bz, "minecraft:bed", {"direction": 1})
        v.set(nwgx1 - 1, 1, bz, "minecraft:bed", {"direction": 1, "head_piece_bit": True})
    v.set((nwgx0 + nwgx1) // 2, 8, nwgz0 + 2, LANTERN, {"hanging": True})

    # ================= DINING HALL & KITCHEN (east, two storeys) =================
    # Shortened on its EAST flank (was x49) to open a riverside terrace: the
    # freed strip between the hall and the river becomes a grand tiered stone
    # staircase descending from the upper gallery to a waterside promenade.
    dx0, dx1, dz0, dz1 = 36, 45, 33, 51
    UPPER = 7
    room(dx0, dz0, dx1, dz1, UPPER, floor=lambda: SAND if r.random() < 0.5 else STONE, roof=None)
    door(dx0, ROT_Z, axis="x")                      # rotunda E <-> dining W
    for x in range(ROT_X + ROT_R, dx0 + 1):         # broad arched ground link to the dining hall
        for z in range(ROT_Z - 2, ROT_Z + 3):
            v.set(x, 0, z, STONE if (x + z) % 2 else SAND_SMOOTH)
            v.fill(x, 1, z, x, 4, z, "minecraft:air")
        for yy in range(1, 6):                       # warm-stone arch cheeks both sides
            v.set(x, yy, ROT_Z - 3, warm())
            v.set(x, yy, ROT_Z + 3, warm())
        for z in range(ROT_Z - 3, ROT_Z + 4):
            v.set(x, 6, z, SLATE if z in (ROT_Z - 3, ROT_Z + 3) else DEEP_TILES)
    # task 13: an upper covered stone-arch BRIDGE links the rotunda gallery (y=UP_Y)
    # to the Dining Hall's upper floor (y=UPPER), so the second storeys join up
    for x in range(ROT_X + 5, dx0 + 1):             # x31..36, stepping y9 -> y7
        step = x - (ROT_X + 5)
        if step <= 1:
            yb, deck_mat = UP_Y, SPRUCE
        elif step == 2:
            yb, deck_mat = UP_Y, "minecraft:spruce_slab"
        elif step == 3:
            yb, deck_mat = UP_Y - 1, SPRUCE
        elif step == 4:
            yb, deck_mat = UP_Y - 1, "minecraft:spruce_slab"
        else:
            yb, deck_mat = UPPER, SPRUCE
        for zz in (ROT_Z - 1, ROT_Z, ROT_Z + 1):
            v.set(x, yb, zz, deck_mat)
            v.fill(x, yb + 1, zz, x, yb + 3, zz, "minecraft:air")
        v.set(x, yb + 1, ROT_Z - 1, DARKOAK_FENCE)  # railings
        v.set(x, yb + 1, ROT_Z + 1, DARKOAK_FENCE)
        v.set(x, yb + 4, ROT_Z, SLATE)              # little gabled cover
    v.fill(dx0, UPPER, ROT_Z - 1, dx0, UPPER + 2, ROT_Z + 1, "minecraft:air")   # into dining upper
    v.fill(ROT_X + 4, UP_Y, ROT_Z - 1, ROT_X + 4, UP_Y + 2, ROT_Z + 1, "minecraft:air")  # from gallery
    # two long banquet tables joined END-TO-END down the CENTRE (along the hall's
    # length), benches down both long sides, candelabra spaced along the boards
    tcx = (dx0 + dx1) // 2
    for tz in range(dz0 + 3, dz1 - 3):
        v.set(tcx, 2, tz, "minecraft:oak_planks")               # table top
        if (tz - dz0) % 4 == 0:
            v.set(tcx, 1, tz, "minecraft:oak_fence")            # legs
        v.set(tcx - 2, 1, tz, OAK_STAIR, {"weirdo_direction": 1, "upside_down_bit": False})
        v.set(tcx + 2, 1, tz, OAK_STAIR, {"weirdo_direction": 0, "upside_down_bit": False})
    for tz in range(dz0 + 4, dz1 - 3, 4):                       # feast dressing
        v.set(tcx, 3, tz, LANTERN, {"hanging": False})
    v.set(tcx, 2, dz0 + 3, "minecraft:cake")
    # kitchen hearth + smoker (north end, by the link to the hall)
    for x in range(dx0 + 1, dx0 + 4):
        v.set(x, 1, dz0 + 1, "minecraft:furnace" if x % 2 else "minecraft:smoker")
    v.set(dx1 - 1, 1, dz0 + 1, "minecraft:barrel")
    v.set(dx1 - 1, 1, dz1 - 1, "minecraft:cauldron")
    # ---- the FEAST-HALL crimson runner (canon): a red carpet leads east out of the
    #      Map Room, over a pair of carpeted threshold STEPS, and on down the Dining
    #      Hall's central aisle. The darker red-wool treads read as carpeted steps. ----
    AIR_ = v._pid("minecraft:air")
    for dz in (-1, 0, 1):                            # carpeted step treads at the hall threshold
        v.set(dx0, 0, ROT_Z + dz, RED)               # darker red-wool "step" band (sits in the doorway)
        v.set(dx0 + 1, 0, ROT_Z + dz, RED)
    for x in range(ROT_X + ROT_R, dx1):              # the runner along the entry axis (z=ROT_Z)
        if v.grid[v.idx(x, 1, ROT_Z)] == AIR_:
            v.set(x, 1, ROT_Z, "minecraft:red_carpet")
        for dz in (-1, 1):                           # widen to a 3-wide runner inside the hall
            if x > dx0 + 1 and v.grid[v.idx(x, 1, ROT_Z + dz)] == AIR_:
                v.set(x, 1, ROT_Z + dz, "minecraft:red_carpet")
    # ---- second storey: a LEVEL, fully-decked dormitory floor. Reached from the
    #      rotunda gallery by the upper stone-arch bridge (the in-hall spiral stair
    #      was removed per owner ask). The whole interior is solid deck — no
    #      stairwell hole — so the floor is continuous and traversable. ----
    for x in range(dx0 + 1, dx1):
        for z in range(dz0 + 1, dz1):
            v.set(x, UPPER, z, SPRUCE if (x + z) % 5 else DARKOAK)
    # perimeter wall runs CONTINUOUS from y=UPPER up (was UPPER+1, leaving a 1-block
    # gap at deck level that left the floor edge open + wood exposed) so the upper
    # storey is sealed and the deck meets solid wall all the way round.
    for x in range(dx0, dx1 + 1):
        for z in (dz0, dz1):
            for y in range(UPPER, UPPER + 6):
                v.set(x, y, z, warm())
    for z in range(dz0, dz1 + 1):
        for x in (dx0, dx1):
            for y in range(UPPER, UPPER + 6):
                v.set(x, y, z, warm())
    v.fill(dx0, UPPER, ROT_Z - 1, dx0, UPPER + 2, ROT_Z + 1, "minecraft:air")  # re-open the gallery-bridge doorway
    for z in range(dz0 + 3, dz1, 4):
        v.set(dx0, UPPER + 3, z, GLASS)
    hip_roof(v, dx0, dx1, dz0, dz1, UPPER + 6, SLATE, levels=3, cap=DEEP_TILES)
    v.fill(dx0 + 1, UPPER + 1, dz0 + 1, dx1 - 1, UPPER + 5, dz1 - 1, "minecraft:air")  # clear the upper room
    for bz in range(dz0 + 6, dz1 - 1, 3):
        v.set(dx0 + 2, UPPER + 1, bz, "minecraft:bed", {"direction": 1})
        v.set(dx0 + 1, UPPER + 1, bz, "minecraft:bed", {"direction": 1, "head_piece_bit": True})
    v.set((dx0 + dx1) // 2, UPPER + 4, (dz0 + dz1) // 2, LANTERN, {"hanging": True})

    # ---- the RIVERSIDE CAUSEWAY + grand staircase + terrace: the strip between
    #      the shortened hall (x45) and the river (x51). A clean, CONTINUOUS 2-wide
    #      stone QUAY (x49-50) runs the whole river flank — from the covered hallway
    #      in the north to the tower island in the south — deliberate stone-tile
    #      paving (not gravel speckle), flush with the water, the through-lane on
    #      x49 always clear and chiseled lantern bollards punctuating the river edge
    #      (x50). Onto it land the three plank bridges and the grand staircase: a
    #      2-wide stone flight on a SOLID carriage (nothing floats) climbing to a
    #      railed riverside terrace that opens, through a door, into the hall's
    #      upper floor. One flat landing breaks the run.
    TR_A, TR_B = 47, 48                              # the two tread columns (stair stays on the hall)
    rim = 50 + EAST                                  # the river's west bank (after the eastward shift)
    for z in range(22, 71):                          # a NARROW 2-wide stone quay at the river's edge
        for x in (rim - 1, rim):                     # (not a big paved platform — the lawn stays open)
            if not is_water(x, z) and v.grid[v.idx(x, 1, z)] == v._pid("minecraft:air"):
                v.set(x, 0, z, DEEP_TILES if (x + z) % 4 == 0 else STONE)   # quay deck
        if z % 8 == 0 and not is_water(rim, z) and v.grid[v.idx(rim, 1, z)] == v._pid("minecraft:air"):
            v.set(rim, 1, z, SAND_CHIS)             # river-edge lantern bollard
            v.set(rim, 2, z, LANTERN, {"hanging": False})
    stand, z = 1, dz1                                # climb NORTH from the promenade
    for step in ["s", "s", "s", "L", "s", "s", "s", "s"]:   # 7 rises -> stand 8 at z=44
        topy = stand if step == "s" else stand - 1
        for tx in (TR_A, TR_B):
            if step == "s":
                v.set(tx, stand, z, SBRICK_STAIR, {"weirdo_direction": 3, "upside_down_bit": False})
            else:
                v.set(tx, stand - 1, z, DEEP_TILES if (tx + z) % 2 else STONE)
            for yy in range(1, topy):
                v.set(tx, yy, z, warm())            # solid carriage down to the ground
        v.set(46, topy + 1, z, SAND_WALL)           # building-side rail (river side = the quay)
        if step == "s":
            stand += 1
        z -= 1
    for x in range(46, 49):                          # the railed riverside TERRACE deck
        for tz in range(dz0 + 4, dz1 - 7):          # z=37..43, level with the upper floor
            for yy in range(1, UPPER):
                v.set(x, yy, tz, warm())
            v.set(x, UPPER, tz, SPRUCE)
    for tz in range(dz0 + 4, dz1 - 6):
        v.set(49, UPPER + 1, tz, SAND_WALL)         # river-side terrace balustrade
    v.set(46, UPPER + 1, dz0 + 4, SAND_CHIS)
    v.set(46, UPPER + 2, dz0 + 4, LANTERN, {"hanging": False})
    v.fill(dx1, UPPER + 1, dz0 + 6, dx1, UPPER + 3, dz0 + 8, "minecraft:air")   # door into upper floor
    # (the staircase foot lands directly on the continuous causeway at x49-50)

    # ================= STORE (south of the rotunda) =================
    stx0, stx1, stz0, stz1 = 22, 33, 52, 59
    # raised to the complex's common y9 eave (was a low y5 wing) so the south arm
    # of the roof runs continuous with the Library/rotunda line — dome + 2-storey
    # Dining stay proud above. A hip cap matches the Library's roof.
    room(stx0, stz0, stx1, stz1, 9, floor=lambda: DARKOAK if r.random() < 0.5 else SPRUCE, roof="hip")
    door((stx0 + stx1) // 2, stz0, axis="z")        # store N <-> rotunda S grounds
    for x in range(stx0 + 1, stx1):
        for y in (2, 3):
            v.set(x, y, stz1 - 1, "minecraft:bookshelf" if (x + y) % 2 else "minecraft:barrel")
    v.set(stx0 + 1, 1, stz1 - 1, "minecraft:chest", {"minecraft:cardinal_direction": "south"})
    v.set((stx0 + stx1) // 2, 7, (stz0 + stz1) // 2, LANTERN, {"hanging": True})

    # ===== ONE CONNECTED BUILDING =============================================
    # The Library (N), Map-Room rotunda (centre), Dining hall (E) and Store (S)
    # are knitted into a SINGLE rambling hall. Connective bays fill the lawn gaps
    # between the subsections with a paved floor, warm-stone side walls and a
    # slate roof DECK whose height matches the neighbour it joins — so the
    # rooflines run continuous from wing to wing while the dome still rises proud
    # at the heart. Wide archways open each bay into the rooms it links, so the
    # whole complex reads (and walks) as one building, not separate boxes.
    def join_bay(x0, z0, x1, z1, eave, wall_axis):
        for x in range(x0, x1 + 1):
            for z in range(z0, z1 + 1):
                v.set(x, 0, z, STONE if (x + z) % 4 else DEEP_TILES)         # paved floor
                v.fill(x, 1, z, x, eave, z, "minecraft:air")                  # clear interior
                v.set(x, eave + 1, z, SLATE if (x + z) % 2 else DEEP_TILES)   # roof deck
        if wall_axis == 'z':                     # walls on the x extremes (run along z)
            for z in range(z0, z1 + 1):
                for x in (x0, x1):
                    for y in range(1, eave + 1):
                        v.set(x, y, z, warm())
        else:                                    # walls on the z extremes (run along x)
            for x in range(x0, x1 + 1):
                for z in (z0, z1):
                    for y in range(1, eave + 1):
                        v.set(x, y, z, warm())
    join_bay(18, 31, 34, 33, 8, 'z')     # Library  <-> rotunda (north): walls x18/x34, roof y9
    join_bay(22, 51, 33, 51, 8, 'z')     # rotunda  <-> Store   (south): now full-height, roof y9
    join_bay(35, 34, 35, 50, 8, 'x')     # rotunda  <-> Dining  (east):  walls z34/z50, roof y9
    # grand archways so the bays read as one open hall (the rotunda's cardinal
    # doorways already open its three connecting sides)
    v.fill(23, 1, 30, 30, 4, 30, "minecraft:air")     # wide opening into the Library
    v.fill(25, 1, 52, 30, 4, 52, "minecraft:air")     # wide opening into the Store
    v.fill(36, 1, 39, 36, 4, 45, "minecraft:air")     # wide opening into the Dining hall

    def arch_on_z(z, x0, x1):
        v.fill(x0, 1, z, x1, 4, z, "minecraft:air")
        for px in (x0 - 1, x1 + 1):
            for yy in range(1, 6):
                v.set(px, yy, z, CHISELED if yy in (1, 5) else warm())
        for x in range(x0, x1 + 1):
            v.set(x, 5, z, SAND_CHIS if (x - x0) in (0, x1 - x0) else CHISELED)
        for x in range(x0 + 2, x1 - 1):
            v.set(x, 6, z, SAND_CHIS)

    def arch_on_x(x, z0, z1):
        v.fill(x, 1, z0, x, 4, z1, "minecraft:air")
        for pz in (z0 - 1, z1 + 1):
            for yy in range(1, 6):
                v.set(x, yy, pz, CHISELED if yy in (1, 5) else warm())
        for z in range(z0, z1 + 1):
            v.set(x, 5, z, SAND_CHIS if (z - z0) in (0, z1 - z0) else CHISELED)
        for z in range(z0 + 2, z1 - 1):
            v.set(x, 6, z, SAND_CHIS)

    arch_on_x(ROT_X - ROT_R, ROT_Z - 2, ROT_Z + 2)   # west entrance arch
    arch_on_z(30, 23, 30)                             # library arch
    arch_on_z(52, 25, 30)                             # store arch
    arch_on_x(ROT_X + ROT_R, ROT_Z - 2, ROT_Z + 2)   # rear arch behind the map
    arch_on_x(36, 39, 45)                             # dining hall arch

    # ===== NORTH RIVERSIDE ANNEX — closes the open courtyard between the Library,
    #       the covered hallway and the Dining hall so the north & east ranges read
    #       as ONE built mass (the map shows rooms here, not a yard). A single-storey
    #       reading-room roofed at the complex's common eave (y9, BELOW the proud
    #       two-storey Dining): warm-stone walls continuing the Dining's river face,
    #       a flat slate roof deck, river windows, bookshelves + a long reading table,
    #       opening south through a wide arch into the Dining hall. Built before the
    #       woods/paving passes so trees keep clear of it. =====
    az0, az1 = 22, dz0 - 1                            # 22..32 (z33 = the Dining's north wall)
    for x in range(dx0, dx1 + 1):                     # 36..45
        for z in range(az0, az1 + 1):
            v.set(x, 0, z, STONE if (x + z) % 4 else DEEP_TILES)   # paved floor
            v.fill(x, 1, z, x, 8, z, "minecraft:air")              # clear interior (7 headroom)
            v.set(x, 9, z, SLATE if (x + z) % 2 else DEEP_TILES)   # flat roof deck at common eave
    for z in range(az0, az1 + 1):                     # west + east (river) walls, y1..8
        for y in range(1, 9):
            v.set(dx0, y, z, warm())
            v.set(dx1, y, z, warm())
    for x in range(dx0, dx1 + 1):                     # north wall (against the covered hallway)
        for y in range(1, 9):
            v.set(x, y, az0, warm())
    for z in range(az0 + 2, az1 + 1, 3):             # river windows on the east wall
        v.set(dx1, 3, z, GLASS)
    v.fill(dx0 + 5, 1, dz0, dx0 + 7, 3, dz0, "minecraft:air")     # wide arch S into the Dining hall
    v.set(dx0 + 4, 3, dz0, SAND_CHIS); v.set(dx0 + 8, 3, dz0, SAND_CHIS)
    for z in range(az0 + 2, az1):                     # bookshelves along the side walls
        if z % 2:
            v.set(dx0 + 1, 1, z, "minecraft:bookshelf"); v.set(dx0 + 1, 2, z, "minecraft:bookshelf")
            v.set(dx1 - 1, 1, z, "minecraft:bookshelf"); v.set(dx1 - 1, 2, z, "minecraft:bookshelf")
    long_table(v, dx0 + 3, dx1 - 4, az0 + 2, 2, top="minecraft:oak_planks")   # reading table (north end)
    v.set((dx0 + dx1) // 2, 8, az0 + 2, LANTERN, {"hanging": True})

    # ===== §6.2 KITCHEN — the small cook-room at the Dining hall's NE corner
    #       (local x40..44, z28..32, inside the riverside annex): a cauldron over a
    #       hearth, a stone oven + smoker, a flour-dusted prep table and apple
    #       barrels. It opens south into the Dining hall (the annex already links).
    k2x0, k2x1, k2z0, k2z1 = 40, 44, 28, 32
    for x in range(k2x0, k2x1):                       # a low screen wall N of the cook-room
        v.set(x, 1, k2z0 - 1, warm()); v.set(x, 2, k2z0 - 1, warm())
    v.fill(k2x0 + 1, 1, k2z0 - 1, k2x0 + 2, 2, k2z0 - 1, "minecraft:air")    # doorway in the screen
    v.set(k2x0, 1, k2z1, "minecraft:cauldron")        # cauldron in the corner
    v.set(k2x0 + 1, 1, k2z1, "minecraft:furnace")     # stone oven + smoker
    v.set(k2x0 + 2, 1, k2z1, "minecraft:smoker")
    long_table(v, k2x0 + 1, k2x0 + 3, k2z0 + 2, 2, top="minecraft:oak_planks")  # prep table
    v.set(k2x0 + 2, 3, k2z0 + 2, "minecraft:white_carpet")     # flour dusting
    v.set(k2x0 + 3, 3, k2z0 + 2, "minecraft:hay_block")
    v.set(k2x0, 1, k2z0, "minecraft:barrel"); v.set(k2x0, 2, k2z0, "minecraft:barrel")
    v.set(k2x0, 1, k2z0 + 1, "minecraft:chest", {"minecraft:cardinal_direction": "east"})

    # ===== NW COMMON ROOM — encloses the open west ward (north of the Skill apse,
    #       west of the Library) into a roofed tables-and-chairs room, so the west
    #       range reads solid (the map's dense NW). Roofed at the common eave (y9);
    #       opens east into the Library; arrow-slit lights face the curtain wall. =====
    nwx0, nwx1, nwz0, nwz1 = 11, 18, 16, 30          # x18 = the Library's west wall (shared)
    for x in range(nwx0, nwx1):                       # interior x11..17: floor + clear + roof deck
        for z in range(nwz0, nwz1 + 1):
            v.set(x, 0, z, STONE if (x + z) % 4 else DEEP_TILES)
            v.fill(x, 1, z, x, 8, z, "minecraft:air")
            v.set(x, 9, z, SLATE if (x + z) % 2 else DEEP_TILES)
    for z in range(nwz0, nwz1 + 1):                   # west wall (x11), y1..8
        for y in range(1, 9):
            v.set(nwx0, y, z, warm())
        if z % 4 == 2:
            v.set(nwx0, 3, z, GLASS); v.set(nwx0, 6, z, GLASS)   # arrow-slit lights
    for x in range(nwx0, nwx1 + 1):                   # north (z16) + south (z30) walls, y1..8
        for y in range(1, 9):
            v.set(x, y, nwz0, warm())
            v.set(x, y, nwz1, warm())
    v.fill(nwx1, 1, nwz0 + 5, nwx1, 3, nwz0 + 7, "minecraft:air")       # arch through the Library wall (x18)
    v.fill(nwx1 + 1, 1, nwz0 + 5, nwx1 + 1, 3, nwz0 + 7, "minecraft:air")  # clear the Library shelf (x19) behind it
    for z in range(nwz0 + 2, nwz1, 2):               # bookshelves + a reading nook
        if z % 2:
            v.set(nwx0 + 1, 1, z, "minecraft:bookshelf"); v.set(nwx0 + 1, 2, z, "minecraft:bookshelf")
    long_table(v, nwx0 + 2, nwx1 - 2, (nwz0 + nwz1) // 2, 2, top="minecraft:oak_planks")
    v.set((nwx0 + nwx1) // 2, 8, (nwz0 + nwz1) // 2, LANTERN, {"hanging": True})

    # ================= NE KITCHEN / STORES / DORMITORY (across the river) =======
    # Foundation planted at GROUND level (was a block proud); both flanks opened
    # with arches onto the gravel paths so the Hero can step off the bridge and
    # head down to the archery range or out across the grounds.
    # §7.1/§7.2: the block divides N-S into a single-storey KITCHEN / FOOD-STORES
    # (west, x64..74) and a TWO-STOREY DORMITORY (east, x75..88). The covered
    # stone hallway docks the food-stores' north face; both halves open south onto
    # the gravel grounds (the archery apron + the dueling path).
    kx0, kx1, kz0, kz1 = 64 + EAST, 88 + EAST, 6, 28
    PX = 74 + EAST                   # the N-S partition: FOOD-STORES (west) | DORMITORY (east)
    FS_H, DM_H = 6, 9                # food-stores eave y6 (1 storey); dormitory eave y9 (2 storeys)
    DM_DECK = 5                      # dormitory upper-floor deck at y5 (a Hero stands at y6)
    ne_h = lambda x: DM_H if x >= PX else FS_H        # the dormitory half rises taller
    for x in range(kx0, kx1 + 1):                    # shared ground floor
        for z in range(kz0, kz1 + 1):
            v.set(x, 0, z, STONE if (x + z) % 3 else DEEP_TILES)
    for x in range(kx0, kx1 + 1):                    # north + south outer walls (stepped height)
        for z in (kz0, kz1):
            for y in range(1, ne_h(x) + 1):
                v.set(x, y, z, warm())
    for z in range(kz0, kz1 + 1):
        for y in range(1, FS_H + 1):
            v.set(kx0, y, z, warm())                 # west end wall (food stores)
        for y in range(1, DM_H + 1):
            v.set(kx1, y, z, warm())                 # east end wall (dormitory)
            v.set(PX, y, z, warm())                  # the full-height N-S partition
    v.fill(PX, 1, kz0 + 10, PX, 3, kz0 + 12, "minecraft:air")     # arch linking the two halves
    v.set(PX, 4, kz0 + 10, SAND_CHIS); v.set(PX, 4, kz0 + 12, SAND_CHIS)
    hip_roof(v, kx0, PX, kz0, kz1, FS_H, SLATE, levels=3, cap=DEEP_TILES)   # low roof over the stores
    hip_roof(v, PX, kx1, kz0, kz1, DM_H, SLATE, levels=4, cap=DEEP_TILES)   # proud roof over the dorm
    for z in range(kz0 + 3, kz1, 4):                 # windows on the long outer walls
        v.set(kx0, 3, z, GLASS)
        v.set(kx1, 3, z, GLASS); v.set(kx1, DM_DECK + 2, z, GLASS)
    KND = kx0 + 4                                    # the covered stone hallway docks the NORTH face
    v.fill(KND - 1, 1, kz0, KND + 1, 3, kz0, "minecraft:air")
    v.set(KND - 2, 1, kz0, SAND_CHIS); v.set(KND + 2, 1, kz0, SAND_CHIS)
    v.set(KND, 4, kz0, SAND_CHIS)
    v.set(KND, 0, kz0 + 1, STONE)
    for dx in (68 + EAST, 80 + EAST):                # SOUTH arches (-> archery / grounds)
        v.fill(dx - 1, 1, kz1, dx + 1, 3, kz1, "minecraft:air")
        for x in (dx - 1, dx + 1):
            v.set(x, 1, kz1, SAND_CHIS); v.set(x, 2, kz1, SAND_CHIS)
        v.set(dx, 3, kz1, SAND_CHIS)
        v.set(dx, 0, kz1 + 1, "minecraft:coarse_dirt")
    # ---- KITCHEN / FOOD STORES (west room x64..74) — cooking range + stacked stores ----
    for x in range(kx0 + 6, PX - 1):                 # cooking range along the north wall (clear of the dock)
        v.set(x, 1, kz0 + 1, "minecraft:furnace" if x % 2 else "minecraft:smoker")
    v.set(PX - 2, 1, kz0 + 1, "minecraft:blast_furnace")
    v.set(kx0 + 1, 1, kz1 - 1, "minecraft:cauldron")
    v.set(kx0 + 2, 1, kz1 - 1, "minecraft:brewing_stand")
    v.set(kx0 + 3, 1, kz1 - 1, "minecraft:cartography_table")
    long_table(v, kx0 + 4, PX - 2, kz0 + 6, 2, top="minecraft:smooth_stone_slab")  # prep island
    for x in range(kx0 + 5, PX - 2, 3):              # produce on the island
        v.set(x, 3, kz0 + 6, r.choice(["minecraft:pumpkin", "minecraft:melon_block",
                                        "minecraft:hay_block", "minecraft:cake"]))
    for z in range(kz0 + 2, kz1 - 1, 2):            # rows of barrels & crates (the stores)
        v.set(kx0 + 1, 1, z, "minecraft:barrel"); v.set(kx0 + 1, 2, z, "minecraft:barrel")
        v.set(PX - 1, 1, z, "minecraft:barrel")
    for (ix, iz) in ((kx0 + 2, kz0 + 9), (kx0 + 6, kz0 + 13)):    # two cold rooms (ice on the floor)
        for dx in range(0, 3):
            for dz in range(0, 3):
                v.set(ix + dx, 0, iz + dz, "minecraft:packed_ice" if (dx + dz) % 2 else "minecraft:blue_ice")
    v.set(kx0 + 1, 1, kz0 + 7, "minecraft:composter")
    v.set(kx0 + 2, 1, kz0 + 7, "minecraft:chest", {"minecraft:cardinal_direction": "east"})
    for hz in (kz0 + 6, kz0 + 14, kz0 + 20):        # chandeliers down the food-stores ceiling
        v.set(kx0 + 5, FS_H - 1, hz, LANTERN, {"hanging": True})
    # ---- DORMITORY (east room x75..88) — TWO floors: a common room below, four
    #      bunk rooms above on a deck reached by a corner spiral stair (§7.2) ----
    dmx0, dmx1 = PX + 1, kx1                          # 75..88 interior
    tcx_dm = (dmx0 + dmx1) // 2
    for tz in range(kz0 + 3, kz1 - 2):               # ground: a long common-room table
        v.set(tcx_dm, 2, tz, "minecraft:oak_planks")  # continuous top (no floating gaps between legs)
        if tz % 4 == 1:
            v.set(tcx_dm, 1, tz, "minecraft:oak_fence")   # a fence leg every 4 blocks
    for hx in (dmx1 - 2, dmx1 - 1, dmx1):            # a warming hearth on the back wall
        v.set(hx, 1, kz0 + 1, STONE); v.set(hx, 2, kz0 + 1, STONE)
    v.set(dmx1 - 1, 1, kz0 + 1, "minecraft:campfire")
    v.set(dmx0 + 1, 1, kz1 - 1, "minecraft:lectern", {"minecraft:cardinal_direction": "north"})  # notice board
    v.set(dmx0 + 2, 1, kz1 - 1, "minecraft:bookshelf")
    spiral_stair(v, dmx0 + 2, kz0 + 3, 2, 1, DM_DECK, OAK_STAIR, post=DARKLOG, steps_per_rev=12)
    for x in range(dmx0, dmx1 + 1):                  # the upper-floor deck (stairwell left open)
        for z in range(kz0 + 1, kz1):
            v.set(x, DM_DECK, z, SPRUCE if (x + z) % 5 else DARKOAK)
    v.fill(dmx0, DM_DECK, kz0 + 1, dmx0 + 4, DM_DECK, kz0 + 5, "minecraft:air")   # stairwell opening
    v.set(dmx0 + 2, DM_DECK, kz0 + 3, DARKLOG)       # restore the newel post the opening cut (was floating its cap)
    DECK_AIR = v._pid("minecraft:air")
    for (rx0, rz0) in ((dmx0 + 1, kz0 + 1), (dmx0 + 7, kz0 + 1),
                       (dmx0 + 1, kz0 + 11), (dmx0 + 7, kz0 + 11)):   # four bunk rooms
        for x in range(rx0, rx0 + 5):
            for z in range(rz0, rz0 + 6):
                if 0 <= x < W and 0 <= z < L and v.grid[v.idx(x, DM_DECK, z)] != DECK_AIR:
                    v.set(x, DM_DECK + 1, z, "minecraft:light_blue_carpet")    # rug
        # only furnish a bunk where the deck below is solid — the NW bunk overlaps the
        # open stairwell, so its bed/shelf would otherwise float over the carved hole.
        def _decked(x, z):
            return 0 <= x < W and 0 <= z < L and v.grid[v.idx(x, DM_DECK, z)] != DECK_AIR
        if _decked(rx0, rz0 + 1) and _decked(rx0, rz0 + 2):
            v.set(rx0, DM_DECK + 1, rz0 + 1, "minecraft:bed", {"direction": 1})
            v.set(rx0, DM_DECK + 1, rz0 + 2, "minecraft:bed", {"direction": 1, "head_piece_bit": True})
        if _decked(rx0 + 4, rz0 + 1):
            v.set(rx0 + 4, DM_DECK + 1, rz0 + 1, "minecraft:bookshelf")
    v.set((dmx0 + dmx1) // 2, DM_H - 1, (kz0 + kz1) // 2, LANTERN, {"hanging": True})

    # ---- the covered STONE TOP HALLWAY: it leaves the North Wing's NE door, runs
    #      along the very TOP of the campus (z3-5, well clear of the wooden river
    #      bridges far to the south), humps over the river, then continues as a
    #      covered colonnade along the kitchen's NORTH (top) face ALL THE WAY to
    #      the building's east end — opening into the kitchen through an arcade so
    #      the whole top range walks as one hall. Deck is flush at the ends. ----
    segA = {(x, z) for x in range(41, 44) for z in range(4, 9)}        # riser off the wing
    segB = {(x, z) for x in range(41, kx1 + 1) for z in range(3, 6)}   # top run to the building's END
    deck = segA | segB
    walk = ({(42, z) for z in range(5, 9)} | {(x, 4) for x in range(42, kx1)})   # x88 caps the east end
    arcade = {(x, 5) for x in range(kx0, kx1 + 1)}                     # opens south into the kitchen
    joins = {(41, 7), (42, 7), (41, 8), (42, 8)} | arcade             # never wall these
    dky = lambda x: 1 if 50 + EAST <= x <= 56 + EAST else 0            # gentle hump over the river
    for (x, z) in deck:
        y = dky(x)
        v.set(x, y, z, STONE if (x + z) % 2 else DEEP_TILES)           # deck (walk y+1)
        v.fill(x, y + 1, z, x, 4, z, "minecraft:air")                  # headroom
        v.set(x, 5, z, SLATE if (x + z) % 2 else DEEP_TILES)           # continuous slate roof
    for px in (51 + EAST, 53 + EAST, 55 + EAST):                       # mossy piers in the river
        v.set(px, 0, 4, MCOBBLE)
    v.set(49 + EAST, 0, 4, SBRICK_STAIR, {"weirdo_direction": 0, "upside_down_bit": False})  # up onto the hump
    v.set(57 + EAST, 0, 4, SBRICK_STAIR, {"weirdo_direction": 1, "upside_down_bit": False})  # down off it
    for (x, z) in deck:                                                # side walls carry the roof (no float)
        if (x, z) in walk or (x, z) in joins:
            continue
        if any((x + dx, z + dz) not in deck for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1))):
            for y in range(dky(x) + 1, 5):
                v.set(x, y, z, warm())
            if (x + z) % 3 == 0:
                v.set(x, dky(x) + 2, z, GLASS)                        # arched window slits
    # turn the kitchen's north wall into an open ARCADE so the hallway runs into it
    for x in range(kx0, kx1 + 1):
        if x % 3 == 0:
            for y in range(1, 4):
                v.set(x, y, kz0, warm())                              # pier
            v.set(x, 4, kz0, CHISELED)                                # arch springer
        else:
            v.fill(x, 1, kz0, x, 3, kz0, "minecraft:air")            # open bay
    for x in range(45, kx1, 6):                                        # hanging lanterns down the run
        v.set(x, 4, 4, LANTERN, {"hanging": True})

    # =========== BRIDGES across the north river (FLAT, jump-free plank spans) ===
    # A clean flat dark-oak plank deck rides just above the water (deck surface y2).
    # A single half-slab tread on each bank breaks the 1-block rise into two 0.5
    # steps, so the whole crossing walks WITHOUT a jump (bank 1.0 -> slab 1.5 ->
    # deck 2.0 -> slab 1.5 -> bank 1.0). Mossy stone piers carry the deck over
    # midstream; spruce-fence rails and lantern gateheads finish it.
    def plank_bridge(zc):
        for x in range(50 + EAST, 57 + EAST):          # flat plank deck (surface y2)
            for z in (zc - 1, zc, zc + 1):
                v.set(x, 1, z, DARKOAK)
        for x in (49 + EAST, 57 + EAST):               # half-slab approach treads (surface 1.5)
            for z in (zc - 1, zc, zc + 1):
                v.set(x, 1, z, "minecraft:dark_oak_slab")
        for px in (51 + EAST, 53 + EAST, 55 + EAST):   # mossy stone piers under midstream
            v.set(px, 0, zc, MCOBBLE)
        for x in range(50 + EAST, 57 + EAST):          # fence rails down both deck edges
            v.set(x, 2, zc - 1, SPRUCE_FENCE)
            v.set(x, 2, zc + 1, SPRUCE_FENCE)
        for px in (48 + EAST, 58 + EAST):              # lantern gateheads on the banks
            for zr in (zc - 1, zc + 1):
                v.set(px, 1, zr, DARKOAK_FENCE)
                v.set(px, 2, zr, LANTERN, {"hanging": False})
    for bridge_z in BRIDGE_ZS:
        plank_bridge(bridge_z)

    # ================= EAST TRAINING GROUNDS (across the river) =================
    # the ARCHERY RANGE — a CIRCULAR packed-dirt range (canon design) set hard
    # against the Kitchen's SOUTH wall (attached to the building), a dirt apron
    # joining the two; the red bullseye stands on the NORTH backstop and five
    # straw dummies ring the rim. It sits EAST of the riverside walk and the link
    # path skirts its edge, so it never blocks the through-route.
    acx, acz, arr = ARCH_X, ARCH_Z, ARCH_R
    # FLAT, hole-free dirt — NO gravel (a gravity block: it settles into the async
    # foundation fill at runtime and leaves pits). Pack the disc solid at y0.
    for x in range(acx - arr, acx + arr + 1):
        for z in range(acz - arr, acz + arr + 1):
            if math.hypot(x - acx, z - acz) <= arr + 0.5:
                v.set(x, 0, z, "minecraft:coarse_dirt" if (x * 7 + z) % 4 else PATH)
    for x in range(acx - 4, acx + 5):                # dirt apron up to the kitchen south doors
        for z in range(kz1 + 1, acz - arr + 1):     # z29..31
            if v.grid[v.idx(x, 1, z)] == v._pid("minecraft:air"):
                v.set(x, 0, z, "minecraft:coarse_dirt" if (x + z) % 3 else PATH)
    # staged target lane from the building wall down to the circular range
    for tx, tz, width in ((acx - 8, kz1 + 3, 1), (acx - 2, kz1 + 5, 1), (acx + 1, kz1 + 8, 2), (acx - 3, acz - arr + 1, 1)):
        for dx in range(-width, width + 1):
            v.set(tx + dx, 1, tz, "minecraft:hay_block")
        v.set(tx, 2, tz, "minecraft:target")
        v.set(tx, 0, tz + 1, "minecraft:coarse_dirt")
    # five straw dummies spaced round the perimeter (facing the centre)
    for ang in (155, 210, 270, 325, 25):
        dmx = acx + round(math.cos(math.radians(ang)) * (arr - 1))
        dmz = acz + round(math.sin(math.radians(ang)) * (arr - 1))
        face = "north" if dmz > acz else "south"
        v.set(dmx, 1, dmz, "minecraft:hay_block")
        v.set(dmx, 2, dmz, "minecraft:hay_block")
        v.set(dmx, 3, dmz, "minecraft:carved_pumpkin", {"minecraft:cardinal_direction": face})
    v.set(acx + arr - 1, 1, acz + 1, "minecraft:fletching_table")
    for (fx, fz) in ((acx - arr, acz - arr), (acx + arr, acz - arr),
                     (acx - arr, acz + arr), (acx + arr, acz + arr)):   # torch fence posts
        if 0 <= fx < W and 0 <= fz < L:
            v.set(fx, 1, fz, SPRUCE_FENCE)
            v.set(fx, 2, fz, "minecraft:torch")
    # the DUELING RING — a dirt sparring circle ringed by a LOW stone wall topped
    # with spruce fence (canon). Keep its centre clear for apprentice sparring.
    drx, drz, drr = DUEL_X, DUEL_Z, DUEL_R
    for x in range(drx - drr, drx + drr + 1):
        for z in range(drz - drr, drz + drr + 1):
            d = math.hypot(x - drx, z - drz)
            if d <= drr + 0.5:
                v.set(x, 0, z, "minecraft:coarse_dirt" if (x * 7 + z) % 4 else PATH)  # flat, no gravel
            if drr - 0.6 < d <= drr + 0.5:
                v.set(x, 1, z, "minecraft:mossy_stone_brick_slab" if (x + z) % 5 == 0 else "minecraft:stone_brick_slab")
    for ez in range(drz - 2, drz + 3, 2):            # a west gate onto the path
        v.fill(drx - drr, 1, ez, drx - drr, 2, ez, "minecraft:air")
    # (the east-grounds gravel spine + the dirt branch out to the Woods are laid
    #  in the consolidated GROUNDS path circuit below, clipped to open lawn)

    # ================= MAZE'S TOWER (moated island, south) — THREE floors =======
    # A circular medieval tower: a wall-hugging spiral winds up past book-lined
    # walls, lecterns, candles and framed art through three floors to Maze's
    # study. Two ground entrances (WEST to the cloister, NORTH to the graves
    # garden) are guarded by suits of armour (spawned at runtime); floor 2 meets
    # the cloister's upper deck so the second storeys all link.
    F2, F3, TOP = 6, 11, 16                          # floor-2 / floor-3 / parapet base
    TOP_R = TWR_R - 1                                # third-floor room steps inward for a balcony
    BALC_R = TWR_R + 1                               # outer edge of the viewing balcony
    LOWER_TOP = F3 - 1                               # lower walls stop at the second-floor ceiling
    SPR_R = 4                                         # spiral radius (winds inside the wall)
    def tower_stone():
        roll = r.random()
        if roll < 0.68:
            return SAND_SMOOTH
        if roll < 0.90:
            return SAND_CUT
        return STONE
    for x in range(TWR_X - TWR_R - 1, TWR_X + TWR_R + 2):
        for z in range(TWR_Z - TWR_R - 1, TWR_Z + TWR_R + 2):
            if 0 <= x < W and 0 <= z < L and math.hypot(x - TWR_X, z - TWR_Z) <= TWR_R + 0.4:
                v.set(x, 0, z, "minecraft:grass_block" if math.hypot(x - TWR_X, z - TWR_Z) > TWR_R - 0.3 else DEEP_TILES)
    cylinder(v, TWR_X, TWR_Z, TWR_R, 0, 0, DEEP_TILES, fill_mat=DEEP_TILES)
    # outer wall with two GROUND doorways: 180=west (cloister), 270=north (garden).
    # It stops below floor 3; the study above is set inward so a balcony can wrap it.
    ring_wall(v, TWR_X, TWR_Z, TWR_R, 1, LOWER_TOP, tower_stone, gaps=[(180, 16), (270, 16)])

    def tower_spiral_points(y0, y1):
        pts = []
        slabs = set()
        prev = None
        for i in range((y1 - y0 + 1) * 2):
            y = y0 + i // 2
            ang = math.radians(25 + i * (360 / 16))
            outer = (TWR_X + round(math.cos(ang) * SPR_R),
                     TWR_Z + round(math.sin(ang) * SPR_R))
            inner = (TWR_X + round(math.cos(ang) * (SPR_R - 1)),
                     TWR_Z + round(math.sin(ang) * (SPR_R - 1)))
            dx, dz = (outer[0] - prev[0], outer[1] - prev[1]) if prev else (-1, 0)
            st = {"weirdo_direction": _stair_dir(dx or -1, dz), "upside_down_bit": False}
            pts.append((outer[0], y, outer[1], st))
            if i % 2 == 0:
                slabs.add((outer[0], y, outer[1]))
            else:
                slabs.discard((outer[0], y, outer[1]))
            if inner != outer:
                pts.append((inner[0], y, inner[1], st))
                if i % 2 == 0:
                    slabs.add((inner[0], y, inner[1]))
                else:
                    slabs.discard((inner[0], y, inner[1]))
            prev = outer
        return pts, slabs

    stair_pts, stair_slabs = tower_spiral_points(1, F3)
    stair_xy = {(x, z) for x, _, z, _ in stair_pts}
    # floor decks at F2 and F3, each leaving a clean stairwell and landing edge
    for deck in (F2, F3):
        near = {(x, z) for x, y, z, _ in stair_pts if abs(y - deck) <= 1}
        deck_r = TWR_R if deck == F2 else TOP_R
        for x in range(TWR_X - TWR_R, TWR_X + TWR_R + 1):
            for z in range(TWR_Z - TWR_R, TWR_Z + TWR_R + 1):
                if math.hypot(x - TWR_X, z - TWR_Z) < deck_r - 0.4 and (x, z) not in near:
                    v.set(x, deck, z, DARKOAK if deck == F3 else SPRUCE)
        # positive landings beside the opening so the stair path resolves onto each floor
        for x, y, z, _ in stair_pts:
            if y == deck:
                for dx, dz in ((1, 0), (0, 1), (-1, 0), (0, -1)):
                    lx, lz = x + dx, z + dz
                    if math.hypot(lx - TWR_X, lz - TWR_Z) < TWR_R - 0.8 and (lx, lz) not in near:
                        v.set(lx, deck, lz, DARKOAK if deck == F3 else SPRUCE)
    # viewing balcony: a continuous timber ring outside the smaller third-floor study.
    near_f3 = {(x, z) for x, y, z, _ in stair_pts if abs(y - F3) <= 1}
    for x in range(TWR_X - BALC_R, TWR_X + BALC_R + 1):
        for z in range(TWR_Z - BALC_R, TWR_Z + BALC_R + 1):
            d = math.hypot(x - TWR_X, z - TWR_Z)
            if TOP_R - 0.35 <= d <= BALC_R + 0.35 and (x, z) not in near_f3:
                v.set(x, F3, z, SPRUCE)
    top_balcony_doors = [(0, 13), (90, 13), (315, 10)]
    ring_wall(v, TWR_X, TWR_Z, TOP_R, F3 + 1, TOP, tower_stone, gaps=top_balcony_doors)
    # per-floor: arched windows in the lower wall + a ring of bookshelves just inside it
    ART = ["minecraft:blue_glazed_terracotta", "minecraft:cyan_glazed_terracotta",
           "minecraft:light_blue_glazed_terracotta"]
    for base_y, wall_r in ((1, TWR_R), (F2 + 1, TWR_R)):
        for ang in range(0, 360, 30):
            rad = math.radians(ang)
            wx_ = TWR_X + round(math.cos(rad) * wall_r)
            wz_ = TWR_Z + round(math.sin(rad) * wall_r)
            ix = TWR_X + round(math.cos(rad) * (wall_r - 1))
            iz = TWR_Z + round(math.sin(rad) * (wall_r - 1))
            if 200 < ang < 260 or 160 <= ang <= 200 or 250 <= ang <= 290:
                continue                            # keep doorways / their heads clear
            if ang % 60 == 0:                       # arched window
                v.set(wx_, base_y + 1, wz_, GLASS)
                v.set(wx_, base_y + 2, wz_, GLASS)
                v.set(wx_, base_y + 3, wz_, CHISELED)
            else:                                   # book-lined wall (with candles/art)
                if (ix, iz) != (TWR_X, TWR_Z) and (ix, iz) not in stair_xy:
                    v.set(ix, base_y, iz, "minecraft:bookshelf")
                    v.set(ix, base_y + 1, iz, "minecraft:bookshelf" if ang % 90 else r.choice(ART))
                    v.set(ix, base_y + 2, iz, "minecraft:white_candle")
    # carve clear entrance corridors AFTER shelves/windows so neither doorway is boxed in
    v.fill(TWR_X - TWR_R, 1, TWR_Z - 1, TWR_X - 2, 4, TWR_Z + 1, "minecraft:air")
    v.fill(TWR_X - 1, 1, TWR_Z - TWR_R, TWR_X + 1, 4, TWR_Z - 2, "minecraft:air")

    def lower_glow_window(ang, y_lo=2):
        rad = math.radians(ang)
        wx_ = TWR_X + round(math.cos(rad) * TWR_R)
        wz_ = TWR_Z + round(math.sin(rad) * TWR_R)
        tx = round(-math.sin(rad))
        tz = round(math.cos(rad))
        for yy in range(y_lo, F3):
            v.set(wx_, yy, wz_, "minecraft:glowstone")
        if y_lo <= 2:
            v.set(wx_, 1, wz_, CHISELED)
        v.set(wx_, F3, wz_, CHISELED)
        for sx, sz in ((wx_ - tx, wz_ - tz), (wx_ + tx, wz_ + tz)):
            for yy in range(y_lo, F3):
                v.set(sx, yy, sz, SAND_CHIS if yy in (y_lo, F3 - 1) else CHISELED)

    # Three glowstone WINDOW COLUMNS, centred on each face EXCEPT the west
    # (main-wall) side: EAST and SOUTH run the full height; the NORTH face — the
    # library/entrance side — runs the glow column down to just above its doorway.
    lower_glow_window(0)              # east
    lower_glow_window(90)             # south
    lower_glow_window(270, y_lo=5)    # north (library/entrance side), above the door
    # ---- FLOOR 1 (entry hall): armour-guarded doorways + a reading nook ----
    v.set(TWR_X + 2, 1, TWR_Z + 2, "minecraft:lectern", {"minecraft:cardinal_direction": "west"})
    v.set(TWR_X + 3, 1, TWR_Z - 2, "minecraft:chest", {"minecraft:cardinal_direction": "west"})
    for (ax, az) in ((TWR_X - 3, TWR_Z + 2), (TWR_X + 2, TWR_Z - 3)):   # armour plinths beside, not in, the entries
        v.set(ax, 1, az, "minecraft:chiseled_stone_bricks")
    # ---- FLOOR 2 (scriptorium): lecterns, a desk, candles ----
    v.set(TWR_X - 2, F2 + 1, TWR_Z + 1, "minecraft:lectern", {"minecraft:cardinal_direction": "east"})
    v.set(TWR_X + 2, F2 + 1, TWR_Z - 1, "minecraft:lectern", {"minecraft:cardinal_direction": "west"})
    v.set(TWR_X, F2 + 1, TWR_Z + 2, "minecraft:cartography_table")
    v.set(TWR_X - 1, F2 + 1, TWR_Z + 2, "minecraft:white_candle")
    # ---- FLOOR 3 (Maze's study): enchanting, bed, lectern, hanging light ----
    v.set(TWR_X - 2, F3 + 1, TWR_Z + 1, "minecraft:lectern", {"minecraft:cardinal_direction": "east"})
    v.set(TWR_X + 2, F3 + 1, TWR_Z, "minecraft:enchanting_table")
    v.set(TWR_X - 1, F3 + 1, TWR_Z - 3, "minecraft:red_bed", {"direction": 1})
    v.set(TWR_X, F3 + 1, TWR_Z - 3, "minecraft:red_bed", {"direction": 1, "head_piece_bit": True})
    v.set(TWR_X, F3 + 3, TWR_Z, "minecraft:sea_lantern")
    v.set(TWR_X, F3 + 4, TWR_Z, "minecraft:lantern", {"hanging": True})
    # place the stair last and clear its headroom so it cannot be overwritten by floors or decor
    for x, y, z, st in stair_pts:
        v.set(x, y, z, SBRICK_SLAB if (x, y, z) in stair_slabs else STONE)
        for yy in range(y + 1, min(TOP, y + 4)):
            v.set(x, yy, z, "minecraft:air")
    for yy in range(1, F3 + 3):                      # dark newel with arcane lamps
        v.set(TWR_X, yy, TWR_Z, "minecraft:chiseled_deepslate" if yy % 3 else "minecraft:sea_lantern")
    for x, y, z, _ in stair_pts:                     # inner rail; kept off entrance corridors
        ox = 1 if x > TWR_X else (-1 if x < TWR_X else 0)
        oz = 1 if z > TWR_Z else (-1 if z < TWR_Z else 0)
        rx, rz = x - ox, z - oz
        if (rx, rz) not in ((TWR_X, TWR_Z), (TWR_X - 1, TWR_Z), (TWR_X, TWR_Z - 1)):
            v.set(rx, y, rz, DARKOAK_FENCE)
    # richer wizard interior: carpets, apparatus and shelves kept off the spiral path.
    tower_clear = {(x, z) for x, _, z, _ in stair_pts}
    tower_clear |= {(x, z) for x in range(TWR_X - TWR_R, TWR_X - 1) for z in range(TWR_Z - 1, TWR_Z + 2)}
    tower_clear |= {(x, z) for x in range(TWR_X - 1, TWR_X + 2) for z in range(TWR_Z - TWR_R, TWR_Z - 1)}
    for fx, fz in ((TWR_X + 1, TWR_Z + 1), (TWR_X - 1, TWR_Z + 1),
                   (TWR_X + 1, TWR_Z - 1), (TWR_X - 1, TWR_Z - 1)):
        if (fx, fz) not in tower_clear:
            v.set(fx, 1, fz, "minecraft:blue_carpet")
            v.set(fx, F2 + 1, fz, "minecraft:light_blue_carpet")
            v.set(fx, F3 + 1, fz, "minecraft:blue_carpet")
    for bx, bz in ((TWR_X + 3, TWR_Z + 1), (TWR_X + 3, TWR_Z - 1),
                   (TWR_X - 1, TWR_Z + 3), (TWR_X + 1, TWR_Z + 3)):
        if (bx, bz) not in tower_clear:
            v.set(bx, F2 + 1, bz, "minecraft:bookshelf")
            v.set(bx, F2 + 2, bz, "minecraft:bookshelf")
    for obj in ((TWR_X - 3, F2 + 1, TWR_Z - 1, "minecraft:brewing_stand"),
                (TWR_X - 3, F2 + 1, TWR_Z + 1, "minecraft:cauldron"),
                (TWR_X + 1, F3 + 1, TWR_Z + 2, "minecraft:sea_lantern"),
                (TWR_X + 3, F3 + 1, TWR_Z + 1, "minecraft:bookshelf"),
                (TWR_X + 3, F3 + 2, TWR_Z + 1, "minecraft:bookshelf")):
        ox, oy, oz, block = obj
        if (ox, oz) not in tower_clear:
            v.set(ox, oy, oz, block)
    # link FLOOR 2 to the cloister's upper deck: a doorway in the WEST wall at F2
    v.fill(TWR_X - TWR_R, F2 + 1, TWR_Z - 1, TWR_X - TWR_R, F2 + 3, TWR_Z + 1, "minecraft:air")
    for x in range(TWR_X - TWR_R - 1, TWR_X - TWR_R + 1):    # a short bridge to the cloister
        v.set(x, F2, TWR_Z, SPRUCE)
        v.set(x, F2, TWR_Z - 1, SPRUCE)
        v.set(x, F2, TWR_Z + 1, SPRUCE)

    # ---- exterior: darker base, vertical buttresses, arched bays, tall spire --
    for ang in range(0, 360, 15):                    # dark stone skirt against the moat
        for rr, yy in ((TWR_R + 2, 1), (TWR_R + 1, 2)):
            bx = TWR_X + round(math.cos(math.radians(ang)) * rr)
            bz = TWR_Z + round(math.sin(math.radians(ang)) * rr)
            if 0 <= bx < W and 0 <= bz < L and not is_water(bx, bz):
                v.set(bx, yy, bz, DEEP_TILES if yy == 1 else CHISELED)
    for ang in range(0, 360, 45):                    # lower buttress ribs, ending below the balcony
        bx = TWR_X + round(math.cos(math.radians(ang)) * (TWR_R + 1))
        bz = TWR_Z + round(math.sin(math.radians(ang)) * (TWR_R + 1))
        if 0 <= bx < W and 0 <= bz < L and not is_water(bx, bz):
            for y in range(1, F3 + 1):
                v.set(bx, y, bz, CHISELED if y in (1, 5, 10) else SAND_CUT)
            v.set(bx, F3 + 1, bz, SAND_CHIS)

    for ang in range(0, 360, 15):                    # low stone-wall railing around the balcony
        px = TWR_X + round(math.cos(math.radians(ang)) * BALC_R)
        pz = TWR_Z + round(math.sin(math.radians(ang)) * BALC_R)
        if 0 <= px < W and 0 <= pz < L:
            v.set(px, F3 + 1, pz, "minecraft:stone_brick_wall")
    for ang in range(0, 360, 45):                    # balcony supports rising to the roof eave
        px = TWR_X + round(math.cos(math.radians(ang)) * BALC_R)
        pz = TWR_Z + round(math.sin(math.radians(ang)) * BALC_R)
        if 0 <= px < W and 0 <= pz < L:
            for yy in range(F3 + 1, TOP + 3):
                v.set(px, yy, pz, "minecraft:stone_brick_wall" if yy < TOP + 2 else SAND_WALL)

    ring_wall(v, TWR_X, TWR_Z, TOP_R, TOP, TOP + 1, tower_stone)        # parapet ring
    def lancet_window(ang):
        rad = math.radians(ang)
        cxw = TWR_X + round(math.cos(rad) * TOP_R)
        czw = TWR_Z + round(math.sin(rad) * TOP_R)
        tx = round(-math.sin(rad))
        tz = round(math.cos(rad))
        base_y = F3 + 2
        bottom = ((cxw - tx, czw - tz), (cxw, czw), (cxw + tx, czw + tz))
        mid = ((cxw - tx, czw - tz), (cxw, czw), (cxw + tx, czw + tz))
        for x, z in bottom:
            if (x, z) not in stair_xy:
                v.set(x, base_y, z, GLASS)
                v.set(x, base_y + 1, z, GLASS)
        for x, z in mid:
            if (x, z) not in stair_xy:
                v.set(x, base_y - 1, z, CHISELED)
        if (cxw, czw) not in stair_xy:
            v.set(cxw, base_y + 2, czw, GLASS)
            v.set(cxw, base_y + 3, czw, "minecraft:sea_lantern")
        for x, z in ((cxw - 2 * tx, czw - 2 * tz), (cxw + 2 * tx, czw + 2 * tz)):
            for yy in range(base_y - 1, base_y + 3):
                if (x, z) not in stair_xy:
                    v.set(x, yy, z, CHISELED)
        if (cxw, czw) not in stair_xy:
            v.set(cxw, base_y + 4, czw, SAND_CHIS)

    for ang in (45, 135, 180, 225, 270):
        lancet_window(ang)
    for ang in range(0, 360, 30):                    # crenellations with warm lamps
        px = TWR_X + round(math.cos(math.radians(ang)) * TOP_R)
        pz = TWR_Z + round(math.sin(math.radians(ang)) * TOP_R)
        v.set(px, TOP + 1, pz, SAND_WALL)
        if ang % 60 == 0:
            v.set(px, TOP + 2, pz, LANTERN, {"hanging": False})

    def tower_spire(cx, cz, y0):
        courses = [(5, 0), (5, 1), (4, 2), (4, 3), (3, 4), (3, 5),
                   (2, 6), (2, 7), (1, 8), (1, 9), (0, 10)]
        for rr, dy in courses:
            yy = y0 + dy
            for x in range(cx - rr, cx + rr + 1):
                for z in range(cz - rr, cz + rr + 1):
                    d = math.hypot(x - cx, z - cz)
                    if d <= rr + 0.4 and (rr <= 1 or d >= rr - 1.2):
                        v.set(x, yy, z, SLATE if dy % 2 == 0 else DEEP_TILES)
        v.set(cx, y0 + 11, cz, "minecraft:sea_lantern")
        v.set(cx, y0 + 12, cz, "minecraft:end_rod")

    # broad eave under the pointed roof so the spire reads medieval instead of flat.
    for x in range(TWR_X - BALC_R, TWR_X + BALC_R + 1):
        for z in range(TWR_Z - BALC_R, TWR_Z + BALC_R + 1):
            if TOP_R - 0.2 <= math.hypot(x - TWR_X, z - TWR_Z) <= BALC_R + 0.35:
                v.set(x, TOP + 2, z, DEEP_TILES)
    tower_spire(TWR_X, TWR_Z, TOP + 3)
    for ang in (45, 135, 225, 315):                  # blue mage banners on diagonal faces
        bx = TWR_X + round(math.cos(math.radians(ang)) * (TWR_R + 1))
        bz = TWR_Z + round(math.sin(math.radians(ang)) * (TWR_R + 1))
        for yy in range(7, 11):
            v.set(bx, yy, bz, "minecraft:blue_wool" if yy < 10 else "minecraft:blue_carpet")

    # ---- task 7: a small ARCHWAY ENTRANCE on the tower's NORTH side with monuments
    #      and flower gardens on the LEFT (toward the Four Graves to the NW) ----
    npz = TWR_Z - TWR_R                              # the north doorway threshold (z=66)
    for x in range(TWR_X - 1, TWR_X + 2):           # a stone porch arch over the entrance
        v.set(x, 4, npz - 1, CHISELED)
    v.set(TWR_X - 2, 1, npz - 1, CHISELED); v.set(TWR_X - 2, 2, npz - 1, CHISELED)
    v.set(TWR_X - 2, 3, npz - 1, CHISELED)
    v.set(TWR_X + 2, 1, npz - 1, CHISELED); v.set(TWR_X + 2, 2, npz - 1, CHISELED)
    v.set(TWR_X + 2, 3, npz - 1, CHISELED)
    for x in range(TWR_X - 2, TWR_X + 3):           # paved threshold out of the arch
        v.set(x, 0, npz - 1, DEEP_TILES if (x) % 2 else STONE)

    def obelisk(mx, mz, lamp=False):                # a stepped stone obelisk
        if not (0 <= mx < W and 0 <= mz < L) or is_water(mx, mz):
            return
        v.set(mx, 1, mz, CHISELED)
        v.set(mx, 2, mz, "minecraft:smooth_quartz")
        v.set(mx, 3, mz, SAND_CHIS)
        v.set(mx, 4, mz, LANTERN if lamp else "minecraft:chiseled_deepslate")
    obelisk(TWR_X - 4, npz - 2, lamp=True)          # monuments flanking the approach
    obelisk(TWR_X + 4, npz - 2, lamp=True)
    obelisk(TWR_X - 5, npz - 5)
    for gx in range(TWR_X - 6, TWR_X + 6):          # flower gardens between tower & graves
        for gz in range(npz - 6, npz - 1):
            if 0 <= gx < W and 0 <= gz < L and not is_water(gx, gz) \
                    and v.grid[v.idx(gx, 0, gz)] in (v._pid("minecraft:grass_block"),
                        v._pid("minecraft:moss_block"), v._pid("minecraft:podzol")) \
                    and v.grid[v.idx(gx, 1, gz)] == v._pid("minecraft:air"):
                roll = r.random()
                if roll < 0.30:
                    v.set(gx, 1, gz, r.choice(["minecraft:rose_bush", "minecraft:peony",
                                               "minecraft:lilac", "minecraft:azure_bluet",
                                               "minecraft:allium"]))
                elif roll < 0.38:
                    v.set(gx, 1, gz, "minecraft:oak_leaves")   # clipped topiary

    # ---- the covered stone CLOISTER: an L-shaped, TWO-storey medieval walk that
    #      leaves the STORE (the Map-Room / Store branch of the main hall), runs
    #      SOUTH down the west flank, then turns EAST to Maze's Tower. Its OUTER
    #      flank (west, then south toward the water) is enclosed warm stone pierced
    #      by arrow-slit lights; its INNER flank (facing the Four Graves garden in
    #      the crook) is an open WOODEN ARCADE of repeated arches full of daylight.
    DECK_Y = 5                                          # upper-floor deck (4-tall storeys)

    def cl_floor(x, z):                                 # paved walk, both storeys cleared
        v.set(x, 0, z, DEEP_TILES if (x + z) % 2 else STONE)
        v.fill(x, 1, z, x, 9, z, "minecraft:air")
        v.set(x, DECK_Y, z, SPRUCE)                     # upper-floor deck

    def cl_extwall(x, z, slit=False):                   # enclosed warm stone, two storeys
        for y in range(1, 10):
            v.set(x, y, z, warm())
        if slit:
            v.set(x, 3, z, GLASS)
            v.set(x, 7, z, GLASS)

    def cl_arcade(x, z, pier):                          # open WOODEN arcade (garden side)
        v.fill(x, 1, z, x, 9, z, "minecraft:air")
        if pier:                                        # dark-oak pier column
            for y in range(1, 10):
                v.set(x, y, z, SPRUCE if y == DECK_Y else DARKLOG)
        else:                                           # open arched bay (light pours in)
            v.set(x, DECK_Y, z, SPRUCE)                 # storey band
            v.set(x, 4, z, SPRUCE)                      # ground arch lintel (opening y1-3)
            v.set(x, 9, z, SPRUCE)                      # upper arch lintel (opening y6-8)
            v.set(x, 6, z, SPRUCE_FENCE)                # upper-storey balustrade
            if r.random() < 0.5:                        # window-box blooms catch the sun
                v.set(x, 7, z, r.choice(["minecraft:peony", "minecraft:rose_bush",
                                         "minecraft:allium"]))

    # The whole L is shifted WEST (toward the curtain wall) so the Four-Graves
    # courtyard in the crook opens out wide. Columns are parametrised off CLW.
    CLW = 20                                            # outer (west) wall column — pushed toward the
    CLF0, CLF1 = 21, 22                                 # main wall so the Four-Graves court opens wider
    CLA = 23                                            # inner (garden-side) arcade column
    #   (CLF1=22 stays on the Store's west wall column so the south doorway holds)
    v.fill(CLF0, 1, 59, CLF1, 4, 59, "minecraft:air")  # doorway through the Store's south wall
    # leg 1 — SOUTH down the WEST flank, ALL the way to the tower's mid-line (z72)
    # so the walk meets the tower's WEST door square-on (outer wall west, arcade east)
    for z in range(59, 73):
        cl_floor(CLF0, z)
        cl_floor(CLF1, z)
        cl_extwall(CLW, z, slit=(z % 3 == 1))
    for z in range(59, 70):
        cl_arcade(CLA, z, pier=(z % 3 == 0))
    for z in range(59, 73):
        v.set(CLF0, 0, z, RED)                          # crimson runner down the walk
    # leg 2 — turn EAST into the tower's WEST entrance, centred on z72 (the run is
    # longer now the vertical leg moved west). Outer wall south, arcade north.
    for x in range(CLF0, 40):
        cl_floor(x, 71)
        cl_floor(x, 72)
        v.set(x, 0, 72, RED)
    for x in range(CLW, 40):
        cl_extwall(x, 73, slit=(x % 3 == 1))
    for x in range(CLA + 1, 40):
        cl_arcade(x, 70, pier=(x % 3 == 1))
    cl_extwall(CLW, 73)                                 # outer SW corner pier
    for y in range(1, 10):                              # inner corner pier of the arcade
        v.set(CLA, y, 70, SPRUCE if y == DECK_Y else DARKLOG)
    # north-end stair to the upper storey, with a stairwell void in the deck
    v.fill(CLF0, DECK_Y, 60, CLF1, DECK_Y, 64, "minecraft:air")
    for i in range(1, DECK_Y + 1):
        v.set(CLF1, i, 59 + i, SBRICK_STAIR, {"weirdo_direction": 2, "upside_down_bit": False})
        for yy in range(1, i):
            v.set(CLF1, yy, 59 + i, STONE)
    # pitched slate roofs over both legs (ridge along the run of each)
    gable_roof_z(v, CLW, CLA, 59, 72, 10, SLATE, SAND)
    j = 0
    while 70 + j <= 73 - j:
        for x in range(CLW, 41):
            v.set(x, 10 + j, 70 + j, SLATE)
            v.set(x, 10 + j, 73 - j, SLATE)
        for z in range(70 + j + 1, 73 - j):
            v.set(CLW, 10 + j, z, SAND)
            v.set(40, 10 + j, z, SAND)
        j += 1
    for z in range(60, 72, 3):                          # hanging lanterns light both storeys
        v.set(CLF0, 4, z, LANTERN, {"hanging": True})
        v.set(CLF0, 9, z, LANTERN, {"hanging": True})
    for x in range(CLA + 1, 40, 3):
        v.set(x, 4, 72, LANTERN, {"hanging": True})
        v.set(x, 9, 72, LANTERN, {"hanging": True})

    # ===== the FOUR GRAVES + MONUMENT garden — the court in the crook of the L,
    #       hemmed by the Store/Dining walls (north), the cloister's west leg and
    #       its south leg. Clipped hedges and flower borders hug those walls; the
    #       four heroes' graves stand to the west, a row of stone MONUMENTS lines
    #       the avenue toward the tower's west entrance =====
    ggx0, ggx1, ggz0, ggz1 = 24, 39, 60, 69     # west edge follows the shifted cloister arcade (wider court)
    AIRP = v._pid("minecraft:air")
    WATERP = v._pid("minecraft:water")
    FLOWERS = ["minecraft:rose_bush", "minecraft:peony", "minecraft:lilac",
               "minecraft:poppy", "minecraft:allium", "minecraft:oxeye_daisy",
               "minecraft:cornflower"]

    def plant(x, z, opts):
        if (0 <= x < W and 0 <= z < L and v.grid[v.idx(x, 1, z)] == AIRP
                and v.grid[v.idx(x, 0, z)] != WATERP):
            v.set(x, 1, z, r.choice(opts))

    def monument(mx, mz, lamp=False):                   # a stepped stone obelisk
        for (dx, dz) in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            if v.grid[v.idx(mx + dx, 1, mz + dz)] == AIRP:
                v.set(mx + dx, 1, mz + dz, SAND_WALL)   # kerb
        v.set(mx, 1, mz, CHISELED)
        v.set(mx, 2, mz, "minecraft:smooth_quartz")
        v.set(mx, 3, mz, SAND_CHIS)
        v.set(mx, 4, mz, LANTERN if lamp else "minecraft:chiseled_deepslate")
    # hedge + flower borders along the building wall (north) and the two arcades
    for x in range(ggx0, ggx1 + 1):
        plant(x, ggz0, ["minecraft:oak_leaves"] if x % 2 else FLOWERS)   # building wall (N)
    for z in range(ggz0, ggz1):
        plant(ggx0, z, ["minecraft:oak_leaves"] if z % 2 else FLOWERS)   # west-leg arcade
    # the FOUR GRAVES arranged as a + (cross) around an open, paved memorial
    # centre with an eternal flame; each arm is a turned-earth mound with a
    # headstone at its outer tip
    gcx, gcz = 31, 64                                  # recentred in the widened court
    for x in range(gcx - 1, gcx + 2):                  # paved memorial plot, kept clear
        for z in range(gcz - 1, gcz + 2):
            v.set(x, 0, z, DEEP_TILES if (x + z) % 2 else "minecraft:smooth_stone")
    v.set(gcx, 0, gcz, SAND_CHIS)
    v.set(gcx, 1, gcz, "minecraft:campfire")          # eternal flame at the heart

    def hero_grave(gx, gz, hx, hz):
        v.set(gx, 0, gz, "minecraft:podzol")
        v.set(hx, 0, hz, "minecraft:coarse_dirt")
        v.set(hx, 1, hz, "minecraft:cobblestone_wall")             # headstone base
        v.set(hx, 2, hz, r.choice([CHISELED, "minecraft:stone_brick_wall", MOSSY]))
        plant(gx, gz, ["minecraft:poppy", "minecraft:rose_bush", "minecraft:lily_of_the_valley"])
    hero_grave(gcx, gcz - 2, gcx, gcz - 3)            # north arm
    hero_grave(gcx, gcz + 2, gcx, gcz + 3)            # south arm
    hero_grave(gcx - 2, gcz, gcx - 3, gcz)            # west arm
    hero_grave(gcx + 2, gcz, gcx + 3, gcz)            # east arm
    # garden lamp posts at the north corners
    for (lx, lz) in ((ggx0, ggz0), (ggx1, ggz0)):
        v.set(lx, 1, lz, DARKOAK_FENCE)
        v.set(lx, 2, lz, DARKOAK_FENCE)
        v.set(lx, 3, lz, LANTERN, {"hanging": False})

    # the small + scarecrow islands out in the south pond, each its own grassy
    # isle — "small island with scarecrows". The small isle laps the tower's dry
    # south shore; the scarecrow isle is reached by the arched bridge from the
    # east bank and steps on to the Demon Door's stones. (No log walkways.)
    for (isx, isz, rad) in GUILD_LAYOUT["islands"]:     # organic, irregular isles
        for x in range(isx - rad - 1, isx + rad + 2):
            for z in range(isz - rad - 1, isz + rad + 2):
                # ragged shoreline: the radius wobbles per-cell so the isle isn't a disc
                er = rad + 0.4 + (0.8 if _wh(x, z) < 0.32 else (-0.7 if _wh(x, z) > 0.8 else 0.0))
                if 0 <= x < W and 0 <= z < L and math.hypot(x - isx, z - isz) <= er:
                    v.set(x, 0, z, "minecraft:grass_block" if _wh(x, z) > 0.15 else "minecraft:coarse_dirt")
                    if r.random() < 0.14:
                        v.set(x, 1, z, "minecraft:tallgrass" if r.random() < 0.6 else "minecraft:fern")
        if rad >= 4:
            v.set(isx + 2, 1, isz - 1, "minecraft:lantern", {"hanging": False})

    # a handsome arched span carries the scarecrow island over the pond to the
    # east bank (the "bridge" marked on the ground plan) — 3-wide dark-oak deck
    # crowned over mossy-stone piers, with railings and lantern gateheads
    def pond_bridge(x0, x1, z):
        # §9.1: a STONE BRICK arched bridge — stone-brick-stair ramps onto a raised
        # crown deck, mossy-cobble piers in the water, low stone-wall parapets.
        mid0, mid1 = x0 + 2, x1 - 2
        for x in range(x0, x1 + 1):
            yb = 2 if mid0 <= x <= mid1 else 1               # gentle arch crown
            if x in (x0 + 1, x1 - 1):                        # stone ramp up onto the crown
                wd = 0 if x == x0 + 1 else 1
                for zz in (z - 1, z, z + 1):
                    v.set(x, 1, zz, SBRICK_STAIR, {"weirdo_direction": wd, "upside_down_bit": False})
            else:
                for zz in (z - 1, z, z + 1):
                    v.set(x, yb, zz, DEEP_TILES if (x + zz) % 2 else STONE)
            v.set(x, yb + 1, z - 1, "minecraft:stone_brick_wall")     # stone parapets both sides
            v.set(x, yb + 1, z + 1, "minecraft:stone_brick_wall")
        for px in (mid0, (x0 + x1) // 2, mid1):              # mossy piers in the water
            v.set(px, 0, z, MCOBBLE)
            v.set(px, 1, z, MCOBBLE)
        for px in (x0, x1):                                  # chiseled lantern gateheads
            for zr in (z - 1, z + 1):
                v.set(px, 2, zr, SAND_CHIS)
                v.set(px, 3, zr, LANTERN, {"hanging": False})
    def pond_bridge_diag(start, end):
        # A WIDE, FLAT, walkable diagonal WOODEN bridge (replaces the old thin
        # mixed-height span with floating posts). A 3-wide contiguous dark-oak deck
        # rides at y1 (surface 2.0); a half-slab apron at each bank end eases the
        # rise to 0.5 (bank 1.0 -> slab 1.5 -> deck 2.0). Spruce-fence rails sit ON
        # the water-facing deck cells (continuous, supported — never floating);
        # mossy-cobble piers carry it over the water, lanterns mark the gateheads.
        x0, z0 = start
        x1, z1 = end
        steps = max(abs(x1 - x0), abs(z1 - z0), 1)
        centers = []
        for i in range(steps + 1):
            cx = round(x0 + (x1 - x0) * i / steps)
            cz = round(z0 + (z1 - z0) * i / steps)
            if not centers or centers[-1] != (cx, cz):
                centers.append((cx, cz))
        DY = 1
        blob = lambda c: {(c[0] + dx, c[1] + dz) for dx in (-1, 0, 1) for dz in (-1, 0, 1)}
        deck = set().union(*(blob(c) for c in centers))
        ends = blob(centers[0]) | blob(centers[-1])             # bank aprons -> slabs
        for (x, z) in deck:                                     # the flat deck
            if not (0 <= x < W and 0 <= z < L):
                continue
            v.fill(x, DY + 1, z, x, DY + 3, z, "minecraft:air")  # clear headroom
            v.set(x, DY, z, "minecraft:dark_oak_slab" if (x, z) in ends else DARKOAK)
        for i, (cx, cz) in enumerate(centers):                 # mossy piers every few cells (water stays between)
            if 0 < i < len(centers) - 1 and i % 4 == 0 and is_water(cx, cz):
                v.set(cx, 0, cz, MCOBBLE)
                v.set(cx, 0, cz + 1, MCOBBLE)
        for (x, z) in deck:                                    # continuous rails on water-facing edges
            if not (0 <= x < W and 0 <= z < L) or (x, z) in ends:
                continue
            if any((x + dx, z + dz) not in deck and is_water(x + dx, z + dz)
                   for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                v.set(x, DY + 1, z, SPRUCE_FENCE)
        for (cx, cz) in (centers[0], centers[-1]):             # lantern gateheads on the banks
            v.set(cx, DY + 1, cz, DARKOAK_FENCE)
            v.set(cx, DY + 2, cz, LANTERN, {"hanging": False})

    pond_bridge_diag(*GUILD_LAYOUT["pond_bridge"])

    # ---- task 8: tidy (smooth) the river bank by the isle above the bridge.
    #      Scarecrows belong only on the scarecrow island, not at Maze's shore. ----
    GRASSY = (v._pid("minecraft:grass_block"), v._pid("minecraft:moss_block"),
              v._pid("minecraft:podzol"))
    for x in range(40, 62):                              # clean grassy shore where land meets pond
        for z in range(66, 82):
            if not (0 <= x < W and 0 <= z < L) or is_water(x, z):
                continue
            if v.grid[v.idx(x, 0, z)] in GRASSY and v.grid[v.idx(x, 1, z)] == v._pid("minecraft:air") \
                    and any(is_water(x + dx, z + dz) for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                v.set(x, 0, z, "minecraft:coarse_dirt" if (x + z) % 3 else PATH)

    def scarecrow(sx, sz, facing):
        if not (0 <= sx < W and 0 <= sz < L):
            return
        if is_water(sx, sz):
            return
        v.set(sx, 0, sz, "minecraft:grass_block")
        v.set(sx, 1, sz, "minecraft:oak_fence")
        v.set(sx, 2, sz, "minecraft:hay_block")
        v.set(sx, 3, sz, "minecraft:carved_pumpkin", {"minecraft:cardinal_direction": facing})
        v.set(sx, 2, sz - 1, "minecraft:oak_fence")     # outstretched arms
        v.set(sx, 2, sz + 1, "minecraft:oak_fence")
    _isx, _isz, _isr = GUILD_LAYOUT["islands"][0]        # the single scarecrow island
    scarecrow(_isx - 2, _isz - 1, "north")               # scarecrows stand on the island
    scarecrow(_isx, _isz - 2, "north")

    # ================= DEMON DOOR (far south, by the islands) =================
    # An Old-Kingdom temple front sculpted into a glaring FACE — glowing eyes, a
    # stone brow and a deep mouth-archway — reached by stepping stones laid across
    # the shallow pond (an ESO-style sculpted gate).
    for x in range(DOOR_X - 4, DOOR_X + 5):
        for z in range(DOOR_Z - 1, min(L - 1, DOOR_Z + 2)):
            if 0 <= x < W:
                v.set(x, 0, z, MCOBBLE if r.random() < 0.45 else COBBLE)
    for z in range(DOOR_Z, min(L - 1, DOOR_Z + 2)):   # shallow facade/crag behind the door
        t = (z - DOOR_Z) / 2
        for x in range(DOOR_X - 3, DOOR_X + 4):
            if not (0 <= x < W):
                continue
            h = int(4 + t) - max(0, abs(x - DOOR_X) - 2)
            for y in range(1, max(1, h)):
                roll = r.random()
                v.set(x, y, z, STONE if roll < 0.4 else
                      (MOSSY if roll < 0.62 else (CRACK if roll < 0.8 else COBBLE)))
    for z in range(DOOR_Z + 1, min(L - 2, DOOR_Z + 8)):   # rocky cliff face behind the shore door
        t = (z - DOOR_Z) / 7
        for x in range(DOOR_X - 6, DOOR_X + 7):
            edge = max(0, abs(x - DOOR_X) - 3)
            h = max(1, int(3 + t * 5) - edge + (1 if _wh(x, z) < 0.28 else 0))
            if h <= 1:
                continue
            v.set(x, 0, z, MCOBBLE if _wh(x, z) < 0.35 else COBBLE)
            for y in range(1, h + 1):
                roll = _wh(x + y * 7, z)
                v.set(x, y, z, MOSSY if roll < 0.22 else (CRACK if roll < 0.44 else COBBLE))
            if h >= 5 and _wh(x, z + h) < 0.18:
                v.set(x, h + 1, z, "minecraft:vine", {"vine_direction_bits": 2})
    for side in (-1, 1):                              # tiered buttresses (temple front)
        for tier, dx in enumerate((4, 3)):
            for y in range(1, 5 + tier):
                v.set(DOOR_X + side * dx, y, DOOR_Z, CHISELED if y % 3 == 0 else STONE)
            v.set(DOOR_X + side * dx, 5 + tier, DOOR_Z, "minecraft:chiseled_deepslate")
    v.fill(DOOR_X - 1, 1, DOOR_Z, DOOR_X + 1, 4, DOOR_Z, "minecraft:air")   # the mouth
    for y in range(1, 5):
        v.set(DOOR_X - 2, y, DOOR_Z, CHISELED)
        v.set(DOOR_X + 2, y, DOOR_Z, CHISELED)
    for x in range(DOOR_X - 2, DOOR_X + 3):
        v.set(x, 5, DOOR_Z, CHISELED)
    for yy in (6, 7):                                 # carved brow / nose ridge
        v.set(DOOR_X, yy, DOOR_Z, "minecraft:chiseled_deepslate")
    for ex in (DOOR_X - 3, DOOR_X + 3):              # the glaring eyes
        v.set(ex, 6, DOOR_Z, "minecraft:iron_bars")
        v.set(ex, 6, DOOR_Z + 1, "minecraft:glowstone")
        v.set(ex, 7, DOOR_Z, CHISELED)
    v.set(DOOR_X - 1, 3, DOOR_Z, SOUL_LANTERN)
    v.set(DOOR_X + 1, 3, DOOR_Z, SOUL_LANTERN)
    for bxp in (DOOR_X - 4, DOOR_X + 4):             # flanking braziers
        v.set(bxp, 1, DOOR_Z - 1, SAND_CHIS)
        v.set(bxp, 2, DOOR_Z - 1, "minecraft:soul_campfire")
    # Continuous two-wide cobblestone walk from the Demon Door threshold to the
    # nearby bridge apron. The old one-wide zigzag touched only at corners and
    # also cleared one of the bridge's end slabs.
    bridge_x, bridge_z = GUILD_LAYOUT["pond_bridge"][0]
    path_len = max(1, DOOR_Z - 1 - bridge_z)
    for zz in range(bridge_z, DOOR_Z):
        path_x = round(bridge_x + (DOOR_X - bridge_x) * (zz - bridge_z) / path_len)
        for sxp in (path_x, path_x + 1):
            if not (0 <= sxp < W and 0 <= zz < L):
                continue
            v.set(sxp, 0, zz, MCOBBLE if (sxp + zz) % 4 == 0 else COBBLE)
            if zz > bridge_z + 1:                    # preserve the bridge apron at z83..85
                v.set(sxp, 1, zz, "minecraft:air")

    # ============= GROUNDS: covered links, gravel paths, trees & rocks =========
    # short covered passages knit the main complex into one connected mass
    def link_corridor(x0, z0, x1, z1):
        # a 3-wide COVERED stone passage knitting two buildings together: solid
        # floor, side walls pierced by arch windows, a full slate roof, and a
        # hanging lantern — the ENDS stay open (each building's doorway) so the
        # join reads as one clear archway with no gap and no blocking wall
        if abs(z1 - z0) >= abs(x1 - x0):
            lo, hi = sorted((z0, z1))
            for z in range(lo, hi + 1):
                for x in (x0 - 1, x0, x0 + 1):
                    v.set(x, 0, z, STONE)
                    v.fill(x, 1, z, x, 3, z, "minecraft:air")
                    v.set(x, 4, z, SLATE if (x + z) % 2 else DEEP_TILES)
                for yy in (1, 2, 3):
                    v.set(x0 - 1, yy, z, warm())
                    v.set(x0 + 1, yy, z, warm())
                if (z - lo) % 3 == 1:
                    v.set(x0 - 1, 2, z, GLASS)
                    v.set(x0 + 1, 2, z, GLASS)
            if hi - lo >= 3:
                v.set(x0, 3, (lo + hi) // 2, LANTERN, {"hanging": True})
        else:
            lo, hi = sorted((x0, x1))
            for x in range(lo, hi + 1):
                for z in (z0 - 1, z0, z0 + 1):
                    v.set(x, 0, z, STONE)
                    v.fill(x, 1, z, x, 3, z, "minecraft:air")
                    v.set(x, 4, z, SLATE if (x + z) % 2 else DEEP_TILES)
                for yy in (1, 2, 3):
                    v.set(x, yy, z0 - 1, warm())
                    v.set(x, yy, z0 + 1, warm())
                if (x - lo) % 3 == 1:
                    v.set(x, 2, z0 - 1, GLASS)
                    v.set(x, 2, z0 + 1, GLASS)
            if hi - lo >= 3:
                v.set((lo + hi) // 2, 3, z0, LANTERN, {"hanging": True})
    link_corridor(ROT_X, ROT_Z - ROT_R, ROT_X, lz1)              # rotunda <-> library
    link_corridor((stx0 + stx1) // 2, ROT_Z + ROT_R, (stx0 + stx1) // 2, stz0)  # rotunda <-> store

    GRASS = {v._pid("minecraft:grass_block"), v._pid("minecraft:moss_block"),
             v._pid("minecraft:podzol")}
    AIR = v._pid("minecraft:air")

    def lay_path(x0, z0, x1, z1, wide=1, mat="gravel"):
        steps = max(abs(x1 - x0), abs(z1 - z0), 1)
        for i in range(steps + 1):
            cx = round(x0 + (x1 - x0) * i / steps)
            cz = round(z0 + (z1 - z0) * i / steps)
            for dx in range(0, wide + 1):
                for dz in range(0, wide + 1):
                    ax, az = cx + dx, cz + dz
                    if 0 <= ax < W and 0 <= az < L and v.grid[v.idx(ax, 0, az)] in GRASS \
                            and v.grid[v.idx(ax, 1, az)] == AIR:   # open lawn only (no paving under flowers/decor)
                        if mat == "gravel":          # SMOOTH grey gravelled lane (full
                            # flat blocks only — no sunk path tiles, so it reads even)
                            v.set(ax, 0, az, COBBLE if r.random() < 0.84 else MCOBBLE)
                        else:                        # a worn earthen track (the east branch)
                            v.set(ax, 0, az, "minecraft:coarse_dirt" if r.random() < 0.5 else PATH)
    # ===== the campus GRAVEL circuit (the plan's PURPLE paths): one connected,
    #       SMOOTH gravelled walk that reaches every feature. lay_path is clipped
    #       to open lawn, so it never paves a floor, wall, garden bed or the water
    #       — the grounds stay continuous with no pocked holes. =====
    # west: the gate / Cullis lawn and Boasting Platform match the left purple mark
    lay_path(0, 36, 10, 36, wide=2)
    lay_path(4, 29, 4, 39, wide=1)
    lay_path(12, 47, 20, 50, wide=1)
    lay_path(20, 50, 27, 52, wide=1)
    lay_path(34, 30, 34, 17)
    # west riverbank: vertical path by the kitchen/stairs, with short bridge spurs
    lay_path(50, 31, 50, 58, wide=1)
    lay_path(47, BRIDGE_ZS[0], 50, BRIDGE_ZS[0], wide=1)
    lay_path(45, BRIDGE_ZS[1], 50, BRIDGE_ZS[1], wide=1)
    lay_path(35, 44, 50, 44, wide=1)
    lay_path(34, 56, 50, 56, wide=1)
    # Four Graves court: a SINGLE-WIDE cobble pattern wrapped around the graves so
    # the lawn shows through between the lanes (the complex wrap the owner wants).
    lay_path(CLF0, 59, 31, 60, wide=0)        # in from the Store's south door
    lay_path(26, 61, 37, 61, wide=0)          # court perimeter — north run
    lay_path(26, 67, 37, 67, wide=0)          # south run
    lay_path(26, 61, 26, 67, wide=0)          # west run
    lay_path(37, 61, 37, 67, wide=0)          # east run
    lay_path(31, 61, 31, 67, wide=0)          # N-S axis to the graves
    lay_path(26, 64, 37, 64, wide=0)          # E-W axis to the graves
    lay_path(26, 61, 30, 64, wide=0)          # diagonal corner accents (the wrapped pattern)
    lay_path(37, 61, 32, 64, wide=0)
    lay_path(26, 67, 30, 64, wide=0)
    lay_path(37, 67, 32, 64, wide=0)
    lay_path(37, 64, 44, 70, wide=0)          # out to the cloister → tower avenue
    lay_path(40, 70, 45, 72, wide=0)
    # east riverbank/training path: curved line beside the river, then down the
    # west side of archery and dueling to the island bridge. The final short spur
    # reaches the bank-side apron without paving over the wooden deck.
    lay_path(58 + EAST, 30, 60 + EAST, BRIDGE_ZS[0], wide=1)
    lay_path(60 + EAST, BRIDGE_ZS[0], 65 + EAST, 48, wide=1)
    lay_path(65 + EAST, 48, 59 + EAST, BRIDGE_ZS[1], wide=1)
    lay_path(58 + EAST, BRIDGE_ZS[-1], ARCH_X - ARCH_R - 1, BRIDGE_ZS[-1], wide=1)
    lay_path(ARCH_X - ARCH_R - 1, BRIDGE_ZS[-1], ARCH_X - ARCH_R - 1, ARCH_Z + ARCH_R, wide=1)
    lay_path(ARCH_X - ARCH_R + 1, ARCH_Z + ARCH_R, DUEL_X - DUEL_R - 3, DUEL_Z - 2, wide=1)
    bridge_path_x, bridge_path_z = 72 + EAST, 80
    bridge_bank_x, bridge_bank_z = GUILD_LAYOUT["pond_bridge"][1]
    lay_path(DUEL_X - DUEL_R - 3, DUEL_Z - 2, bridge_path_x, bridge_path_z, wide=1)
    lay_path(bridge_path_x, bridge_path_z, bridge_bank_x + 2, bridge_bank_z, wide=1)
    # a cobble spur skirts the archery's south + east rim to a JUNCTION node, where
    # the dirt woods-path begins — so the dirt path meets the cobble network.
    DJX, DJZ = ARCH_X + ARCH_R + 1, ARCH_Z - 2          # the dirt/cobble junction
    lay_path(ARCH_X - ARCH_R - 1, ARCH_Z + ARCH_R, DJX, ARCH_Z + ARCH_R, wide=1)
    lay_path(DJX, ARCH_Z + ARCH_R, DJX, DJZ, wide=1)
    # ===== the DIRT PATH branch (the plan's ORANGE): begins at that junction and
    #       runs east through Exit C to the Guild Woods (continued beyond the
    #       footprint at runtime by layWoodsPath in main.js) =====
    lay_path(DJX, DJZ, W - 4, EXIT_C_Z, wide=1, mat="dirt")

    # Exit C — a chiseled stone archway through the east wall to the Guild Woods
    ecz = EXIT_C_Z
    v.fill(W - 3, 1, ecz - 1, W - 3, 4, ecz + 1, "minecraft:air")
    for y in range(1, 6):
        v.set(W - 3, y, ecz - 2, CHISELED)
        v.set(W - 3, y, ecz + 2, CHISELED)
    for z in range(ecz - 2, ecz + 3):
        v.set(W - 3, 6, z, CHISELED)
    v.set(W - 3, 6, ecz, "minecraft:chiseled_deepslate")
    v.set(W - 3, 4, ecz - 1, LANTERN, {"hanging": True})
    v.set(W - 3, 4, ecz + 1, LANTERN, {"hanging": True})
    for x in range(W - 2, W):                        # paved threshold out to the Woods
        for z in range(ecz - 1, ecz + 2):
            v.set(x, 0, z, STONE if (x + z) % 2 else "minecraft:coarse_dirt")

    def open_ground(x, z):
        return (0 <= x < W and 0 <= z < L
                and v.grid[v.idx(x, 1, z)] == AIR and v.grid[v.idx(x, 0, z)] in GRASS)

    def tree(tx, tz):
        if not open_ground(tx, tz):
            return
        h = r.randint(4, 7)
        rad = 2 if h < 6 else 3
        # CLEARANCE: the whole canopy footprint (+1 margin) must be open lawn, so
        # leaves never punch through a wall, roof, path or garden bed
        for dx in range(-rad - 1, rad + 2):
            for dz in range(-rad - 1, rad + 2):
                cx, cz = tx + dx, tz + dz
                if not (0 <= cx < W and 0 <= cz < L) or v.grid[v.idx(cx, 0, cz)] not in GRASS:
                    return
        kind = r.random()
        if kind < 0.45:
            trunk, leaf = "minecraft:oak_log", "minecraft:oak_leaves"
        elif kind < 0.8:
            trunk, leaf = SPRUCE_LOG, "minecraft:spruce_leaves"
        else:
            trunk, leaf = "minecraft:birch_log", "minecraft:birch_leaves"
        for y in range(1, h):
            v.set(tx, y, tz, trunk)
        for dx in range(-rad, rad + 1):
            for dz in range(-rad, rad + 1):
                for dy in range(h - 2, h + 2):
                    if math.hypot(dx, dz) + abs(dy - h) * 0.8 <= rad + 0.5 and r.random() < 0.85:
                        v.set(tx + dx, dy, tz + dz, leaf)
        if r.random() < 0.3:                         # feet: shrubs / flowers
            v.set(tx + r.choice((-1, 1)), 1, tz, "minecraft:fern" if r.random() < 0.5 else "minecraft:tallgrass")

    def rock(rx, rz):
        for dx in range(-1, 2):
            for dz in range(-1, 2):
                if open_ground(rx + dx, rz + dz) and r.random() < 0.7:
                    v.set(rx + dx, 1, rz + dz, COBBLE if r.random() < 0.5 else "minecraft:stone")
                    if r.random() < 0.35:
                        v.set(rx + dx, 2, rz + dz, MCOBBLE)

    # Woodland on the open green: a THICK forest wraps the perimeter and thins
    # quickly inward, so the courtyards, training grounds, gardens and paths stay
    # open (open_ground() keeps trees off anything but bare lawn)
    for gx in range(2, W - 2, 3):
        for gz in range(2, L - 2, 3):
            tx, tz = gx + r.randint(-1, 1), gz + r.randint(-1, 1)
            if 0 <= tx <= 9 and 19 <= tz <= 43:
                continue                         # keep the Boasting stage + main road clear
            edge = min(tx, W - 1 - tx, tz, L - 1 - tz)
            p = 0.6 if edge < 7 else (0.16 if edge < 13 else 0.04)
            if r.random() < p:
                tree(tx, tz)
    for _ in range(28):                  # mossy rock clusters, thick at the edges
        if r.random() < 0.6:
            rx = r.choice([r.randint(3, 11), r.randint(W - 11, W - 3)])
            rz = r.randint(3, L - 3)
        else:
            rx, rz = r.randint(3, W - 3), r.choice([r.randint(3, 11), r.randint(L - 11, L - 3)])
        rock(rx, rz)

    # ===== GO BIG — KNIT THE WEST COMPLEX INTO ONE ROOFED MASS ================
    # Every open-to-sky cell still sitting INSIDE the building envelope is a
    # leftover internal courtyard. If it is hemmed by building (wall or roof) on
    # most sides, roof it at the common eave (y9) so the whole west range reads as
    # ONE continuous hall from above — the dome and the two-storey Dining keep
    # rising proud through the deck. Iterated so it grows inward and fills slots up
    # to a few cells wide, but never the open gate apron (too few built neighbours).
    EAVE = 9
    def _solid(x, y, z):
        p = v.grid[v.idx(x, y, z)]
        return p != AIR and p != WATERP
    def _roofed(x, z):
        return any(_solid(x, y, z) for y in range(5, 16))
    def _wallcell(x, z):
        return _solid(x, 1, z) and _solid(x, 2, z)
    def _building(x, z):
        return _roofed(x, z) or _wallcell(x, z)
    def _high_support(x, z):
        # the EAVE-level deck only reads as built if it actually meets fabric at the
        # eave band (a wall top y8 or an existing roof y9) on this cell or a neighbour.
        # Without this the pass laid y9 decks over the low-walled (y5-6) Cullis/Skill
        # nooks and the SE garden court, leaving roofs floating 3-4 blocks in the air.
        for dx in (-1, 0, 1):
            for dz in (-1, 0, 1):
                nx, nz = x + dx, z + dz
                if 0 <= nx < W and 0 <= nz < L and (_solid(nx, EAVE, nz) or _solid(nx, EAVE - 1, nz)):
                    return True
        return False
    def _enclosed(x, z, reach=14):
        # a cell is INSIDE the building outline only if every cardinal ray hits
        # built fabric before it escapes — open plaza / garden rays reach lawn first
        for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            hit = False
            for s in range(1, reach + 1):
                nx, nz = x + dx * s, z + dz * s
                if not (0 <= nx < W and 0 <= nz < L):
                    break
                if _building(nx, nz):
                    hit = True
                    break
            if not hit:
                return False
        return True
    for _pass in range(2):
        fill_cells = []
        for x in range(11, 46):
            for z in range(16, 60):
                if _roofed(x, z) or is_water(x, z):
                    continue
                if math.hypot(x - ROT_X, z - ROT_Z) <= ROT_R + 1.0:
                    continue                          # leave the domed Map Room proud
                # Leave the western apsidal Cullis/Skill bays OPEN — their cones are
                # the roof. Without this, the pass's _high_support creep mistakes the
                # cone tips for eave fabric and drops floating y9 deck panels over the
                # open lawn ringing each nook (a ceiling with no walls under it).
                if math.hypot(x - CGX, z - CGZ) <= 6.5 or math.hypot(x - SKX, z - SKZ) <= 6.5:
                    continue
                if _enclosed(x, z) and _high_support(x, z):
                    fill_cells.append((x, z))
        if not fill_cells:
            break
        for (x, z) in fill_cells:
            if v.grid[v.idx(x, 0, z)] == AIR:
                v.set(x, 0, z, STONE if (x + z) % 4 else DEEP_TILES)   # ensure a floor
            v.fill(x, 1, z, x, EAVE - 1, z, "minecraft:air")           # clear headroom
            v.set(x, EAVE, z, SLATE if (x + z) % 2 else DEEP_TILES)    # continuous roof deck

    # ===== FULL CIVIC PAVING (match the Inkarnate ground plan) — the developed
    #       complex reads as dense tan FLAGSTONE courtyards, not open lawn. We
    #       convert the still-open ground of the WESTERN civic core — the gate
    #       forecourt + boasting apron, the whole joined building's courtyards,
    #       and the southern cloister / Four-Graves court — into a designed
    #       sandstone plaza. This runs AFTER paths, gardens, trees and rocks, so
    #       it only touches ground that is still open: building floors, walls,
    #       decor, water, garden beds, tree trunks AND the eastern training lawns
    #       (archery / dueling / woods) are all left untouched. =====
    PAVE_OK = GRASS | {v._pid(GRAVEL), v._pid(MCOBBLE), v._pid(PATH),
                       v._pid("minecraft:coarse_dirt")}
    def flagstone(x, z):
        if (x % 4 == 0) or (z % 4 == 0):
            return SAND_CUT                       # joint lines frame 3x3 flag tiles
        roll = r.random()
        if roll < 0.05:
            return STONE                          # occasional grey inlay
        if roll < 0.09:
            return "minecraft:coarse_dirt"        # worn grit between flags (non-gravity)
        if roll < 0.15:
            return SAND                           # plain sandstone tonal variation
        return SAND_SMOOTH
    def pave_region(rx0, rz0, rx1, rz1):
        for x in range(max(0, rx0), min(W, rx1 + 1)):
            for z in range(max(0, rz0), min(L, rz1 + 1)):
                if 24 <= x <= 30 and 9 <= z <= 16:
                    continue                      # spare the rough Guild-Cave alcove + shaft
                if v.grid[v.idx(x, 1, z)] == AIR and v.grid[v.idx(x, 0, z)] in PAVE_OK \
                        and not is_water(x, z):
                    v.set(x, 0, z, flagstone(x, z))
    # Owner ask: NO big paved plazas ("huge concrete platforms"). The grounds stay
    # GREEN lawn and the only paving is the narrow (2-wide) cobblestone path network
    # laid above + the building floors. So the civic flagstone paving is disabled;
    # pave_region/flagstone are kept defined but only used for the gate threshold
    # immediately at the door so the entrance doesn't read as raw dirt.
    pave_region(2, GATE_Z - 1, 9, GATE_Z + 1)   # just the gate threshold strip

    # ---- SMOOTH GROUNDS: a final no-holes sweep. Every ground column must carry
    #      a solid surface block (the lawn is grass/moss/podzol, water is water,
    #      buildings/paths set their own floors) so the grounds never read as a
    #      field of pocked holes. The ONLY intended y=0 opening is the spiral-shaft
    #      mouth in the library alcove (carved open at runtime), which we spare. ----
    cvx, cvz = (lx0 + lx1) // 2, lz0 - 2     # spiral centre (27,14) — keep its mouth open
    for x in range(W):
        for z in range(L):
            if cvx - 1 <= x <= cvx + 1 and cvz - 1 <= z <= cvz + 1:
                continue                     # spare the shaft mouth
            if v.grid[v.idx(x, 0, z)] == AIR:
                v.set(x, 0, z, "minecraft:grass_block")

    fix_floating_decor(v)                # re-seat every lantern; no floaters
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
    S, H = 31, 20
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

    # ---- central CULLIS GATE — a RAISED warded dais crowning a broad HILL: the
    #      whole chamber centre swells into a stone mound that climbs from the floor
    #      to a flat platform 5 blocks proud, ringed by chiseled/obsidian wards
    #      around a glowing core. The mound rises 1 block at a time (walkable), so
    #      the cave causeway arrives at floor level (north) and climbs the slope. ----
    RAISE = 3
    TOPY = 1 + RAISE                                  # platform deck y4 (a Hero stands at y5)
    HILLR = 8

    def _surf(d):                                     # mound surface height (flat top, 1-high steps)
        if d <= 3.0:
            return TOPY
        return max(1, TOPY - int((d - 3.0) * 0.75 + 0.5))
    for x in range(c - HILLR - 1, c + HILLR + 2):     # solid mound (no gaps beneath)
        for z in range(c - HILLR - 1, c + HILLR + 2):
            if not (0 <= x < S and 0 <= z < S):
                continue
            d = math.hypot(x - c, z - c)
            if d > HILLR + 0.6:
                continue
            for y in range(2, _surf(d) + 1):
                v.set(x, y, z, DEEP_TILES if (x + z) % 2 else CHISELED)
    for x in range(c - 4, c + 5):                     # warded TOP platform: obsidian ring + core
        for z in range(c - 4, c + 5):
            d = math.hypot(x - c, z - c)
            if d <= 3.4:
                v.set(x, TOPY, z, CHISELED if d <= 1.0 else
                      (OBSIDIAN if (x + z) % 2 else "minecraft:crying_obsidian"))
    v.set(c, TOPY, c, "minecraft:sea_lantern")        # glowing core, crowning the hill
    for ang in range(0, 360, 45):                     # chiseled ward markers ringing the platform
        px = c + round(math.cos(math.radians(ang)) * 3)
        pz = c + round(math.sin(math.radians(ang)) * 3)
        if 0 <= px < S and 0 <= pz < S:
            v.set(px, TOPY, pz, SAND_CHIS)

    # ---- cave entrance approach from the NORTH (the runtime tunnel pierces the
    #      NORTH wall here). A flat entry vestibule meets the tunnel at floor level;
    #      south of it the approach RAMPS UP the hill's north slope (just clear the
    #      headroom over the mound, keeping its steps) onto the platform. ----
    for z in range(0, c - 3):
        for x in range(c - 2, c + 3):
            d = math.hypot(x - c, z - c)
            if d > HILLR:                                  # flat vestibule beyond the mound toe
                v.set(x, 1, z, COBBLE if (x + z) % 2 else MCOBBLE)
                v.fill(x, 2, z, x, 6, z, "minecraft:air")
            else:                                          # over the slope: clear headroom, keep the ramp
                v.fill(x, _surf(d) + 1, z, x, _surf(d) + 6, z, "minecraft:air")

    # ---- dome shell (thick rings overlap so it is airtight against bleed-in) --
    for y in range(WALL_TOP, H - 2):
        rad = max(2, int(13 - (y - WALL_TOP) * 0.95))
        for x in range(c - rad - 1, c + rad + 2):
            for z in range(c - rad - 1, c + rad + 2):
                d = math.hypot(x - c, z - c)
                if rad - 1.6 <= d <= rad + 0.6:
                    v.set(x, y, z, STONE if r.random() < 0.8 else CRACK)
    for ang in range(0, 360, 90):
        px = c + round(math.cos(math.radians(ang)) * 6)
        pz = c + round(math.sin(math.radians(ang)) * 6)
        v.set(px, WALL_TOP, pz, "minecraft:chain")
        v.set(px, WALL_TOP - 1, pz, "minecraft:lantern", {"hanging": True})
    # ---- a glowing 'daylight' skylight seals the dome top: glass (seen from
    #      below) under a water layer under glowstone, so soft light pours down
    #      and the Chamber of Fate is fully enclosed and naturally bright ----
    cap = H - 3
    for x in range(c - 8, c + 9):
        for z in range(c - 8, c + 9):
            if math.hypot(x - c, z - c) <= 7.6:
                v.set(x, cap, z, "minecraft:glass")
                v.set(x, cap + 1, z, "minecraft:water")
                v.set(x, cap + 2, z, "minecraft:glowstone")
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

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
PATH = "minecraft:grass_path"
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
    """Demon Door site: a 17-wide cliff face of weathered masonry with a
    deep-set carved arch, twin rune monoliths, brazier pedestals, stairs
    and creeping overgrowth. The fc:demon_door entity (the living face)
    is summoned centred in the arch by the placement script."""
    r = rng("struct", "demon_door")
    W, H, D = 17, 14, 7
    v = Vox(W, H, D)
    cx = W // 2
    # foundation slab + approach steps
    for x in range(W):
        for z in range(D):
            v.set(x, 0, z, MCOBBLE if r.random() < 0.3 else COBBLE)
    # cliff wall the door is carved into (two blocks thick, ragged top)
    for x in range(W):
        crown = H - 2 - (abs(x - cx) // 3) + r.randrange(0, 2)
        for y in range(1, crown):
            for z in range(D - 2, D):
                v.set(x, y, z, rnd_stone(r))
    # carve the deep arch opening (5 wide, 8 high, rounded top)
    v.fill(cx - 2, 1, D - 2, cx + 2, 7, D - 1, "minecraft:air")
    v.fill(cx - 1, 8, D - 2, cx + 1, 8, D - 1, "minecraft:air")
    # tiered chiseled arch frame
    for y in range(1, 9):
        v.set(cx - 3, y, D - 2, CHISELED)
        v.set(cx + 3, y, D - 2, CHISELED)
    for x in range(cx - 3, cx + 4):
        v.set(x, 9, D - 2, CHISELED)
    v.set(cx - 2, 8, D - 2, CHISELED)
    v.set(cx + 2, 8, D - 2, CHISELED)
    # skull keystone + flanking carvings
    v.set(cx, 10, D - 2, "minecraft:chiseled_deepslate")
    v.set(cx - 1, 9, D - 2, "minecraft:chiseled_deepslate")
    v.set(cx + 1, 9, D - 2, "minecraft:chiseled_deepslate")
    # rune monoliths flanking the approach
    for mx in (1, W - 2):
        for y in range(1, 6):
            v.set(mx, y, 2, OBSIDIAN if y < 4 else "minecraft:crying_obsidian")
        v.set(mx, 6, 2, SOUL_LANTERN)
    # brazier pedestals at the arch
    for bx in (cx - 5, cx + 5):
        v.set(bx, 1, D - 3, CHISELED)
        v.set(bx, 2, D - 3, "minecraft:campfire")
    # worn path + steps
    for z in range(0, D - 2):
        for x in range(cx - 2, cx + 3):
            v.set(x, 0, z, PATH if r.random() < 0.7 else GRAVEL)
    # rubble, moss and vines
    for i in range(12):
        x = r.randrange(W)
        if r.random() < 0.5:
            v.set(x, 1, r.choice([0, 1, 2]), MCOBBLE if r.random() < 0.5 else "minecraft:cobblestone_wall")
    for x in range(0, W, 2):
        if abs(x - cx) > 3:
            h = r.randrange(3, 9)
            for y in range(max(1, H - 3 - h), H - 3):
                v.set(x, y, D - 3, "minecraft:vine", {"vine_direction_bits": 8})
    v.save("demon_door_arch")


def guild_hall():
    """The Heroes' Guild, modelled on Fable's academy: a walled forecourt
    with hero statue and archery range, a great hall with columned nave,
    east dining wing, west dormitory wing, library corner — and the round
    MAP ROOM tower at the rear crowned with a cone roof, holding the glowing
    map of Albion and the Guildmaster's quest table."""
    r = rng("struct", "guild")
    W, H, L = 37, 20, 35
    v = Vox(W, H, L)
    mx = W // 2  # midline

    # ======== FORECOURT (z 0..9): walls, statue, archery range ========
    for x in range(W):
        for z in range(0, 10):
            roll = r.random()
            v.set(x, 0, z, DEEP_TILES if (x + z) % 6 == 0 else
                  (PATH if roll < 0.25 else STONE))
    # low courtyard wall with corner finials
    for x in range(W):
        for z in (0,):
            if abs(x - mx) > 3:  # gate gap centre
                v.set(x, 1, z, COBBLE)
                v.set(x, 2, z, "minecraft:cobblestone_wall")
    for z in range(0, 10):
        v.set(0, 1, z, COBBLE)
        v.set(0, 2, z, "minecraft:cobblestone_wall")
        v.set(W - 1, 1, z, COBBLE)
        v.set(W - 1, 2, z, "minecraft:cobblestone_wall")
    # gate pillars + lanterns
    for gx in (mx - 4, mx + 4):
        for y in range(1, 5):
            v.set(gx, y, 0, CHISELED)
        v.set(gx, 5, 0, LANTERN, {"hanging": False})
    # hero statue on plinth (west court)
    sx, sz = mx - 9, 5
    v.fill(sx - 1, 1, sz - 1, sx + 1, 1, sz + 1, CHISELED)
    v.set(sx, 2, sz, STONE)
    v.set(sx, 3, sz, STONE)
    v.set(sx, 4, sz, CHISELED)            # head
    v.set(sx - 1, 3, sz, "minecraft:stone_brick_wall")   # arms
    v.set(sx + 1, 3, sz, "minecraft:stone_brick_wall")
    v.set(sx + 1, 4, sz, "minecraft:end_rod")            # raised sword
    # archery range (east court): 3 hay targets
    for i in range(3):
        ax, az = mx + 6 + i * 3, 2
        v.set(ax, 1, az, "minecraft:hay_block")
        v.set(ax, 2, az, "minecraft:hay_block")
        v.set(ax, 2, az - 1, "minecraft:target")
    # fountain pool centre court
    v.fill(mx - 1, 0, 4, mx + 1, 0, 6, "minecraft:water")
    for x in range(mx - 2, mx + 3):
        for z in range(3, 8):
            if x in (mx - 2, mx + 2) or z in (3, 7):
                v.set(x, 1, z, "minecraft:smooth_quartz")
    v.set(mx, 1, 5, "minecraft:sea_lantern")

    # ======== GREAT HALL (z 10..26) ========
    hz0, hz1 = 10, 26
    for x in range(2, W - 2):
        for z in range(hz0, hz1 + 1):
            v.set(x, 0, z, DEEP_TILES if (x + z) % 5 == 0 else STONE)
    # outer walls with pilasters + tall windows
    for x in range(2, W - 2):
        for z in (hz0, hz1):
            for y in range(1, 8):
                v.set(x, y, z, rnd_stone(r))
    for z in range(hz0, hz1 + 1):
        for y in range(1, 8):
            v.set(2, y, z, rnd_stone(r))
            v.set(W - 3, y, z, rnd_stone(r))
    # pilasters every 4 blocks + glass between
    for z in range(hz0 + 2, hz1, 4):
        for y in range(1, 9):
            v.set(2, y, z, DARKLOG)
            v.set(W - 3, y, z, DARKLOG)
        for y in (3, 4, 5):
            v.set(2, y, z + 2, GLASS)
            v.set(W - 3, y, z + 2, GLASS)
    # grand entrance: recessed arch, double doors of air, guild crest
    v.fill(mx - 2, 1, hz0, mx + 2, 4, hz0, "minecraft:air")
    for y in range(1, 6):
        v.set(mx - 3, y, hz0, CHISELED)
        v.set(mx + 3, y, hz0, CHISELED)
    for x in range(mx - 3, mx + 4):
        v.set(x, 6, hz0, CHISELED)
    v.set(mx - 1, 5, hz0, CHISELED)
    v.set(mx + 1, 5, hz0, CHISELED)
    v.set(mx, 5, hz0, GOLD)               # crest
    v.set(mx - 4, 4, hz0, LANTERN, {"hanging": False})
    v.set(mx + 4, 4, hz0, LANTERN, {"hanging": False})
    # nave columns: two rows of dark-oak columns w/ gold caps
    for z in range(hz0 + 3, hz1 - 2, 4):
        for cxp in (mx - 5, mx + 5):
            for y in range(1, 7):
                v.set(cxp, y, z, DARKLOG)
            v.set(cxp, 7, z, GOLD)
    # red carpet up the nave
    for z in range(hz0 + 1, hz1):
        v.set(mx - 1, 0, z, "minecraft:red_wool")
        v.set(mx, 0, z, "minecraft:red_wool")
        v.set(mx + 1, 0, z, "minecraft:red_wool")
    # second storey: gallery floor strips along walls
    for z in range(hz0 + 1, hz1):
        for x in list(range(3, 7)) + list(range(W - 7, W - 3)):
            v.set(x, 8, z, SPRUCE)
    # roof: grand gable across hall, ridge along z
    gable_roof_z(v, 1, W - 2, hz0 - 1, hz1 + 1, 8, SPRUCE, STONE)
    # hanging lanterns down the nave
    for z in range(hz0 + 3, hz1, 4):
        v.set(mx, 9, z, LANTERN, {"hanging": True})

    # ======== WEST WING: dormitory (beds, chests, rugs) ========
    for i in range(4):
        z = hz0 + 3 + i * 4
        v.set(4, 1, z, "minecraft:bed", {"direction": 1})
        v.set(5, 1, z, "minecraft:bed", {"direction": 1, "head_piece_bit": True})
        v.set(3, 1, z, "minecraft:chest", {"minecraft:cardinal_direction": "east"})
        v.set(4, 0, z + 1, "minecraft:blue_wool")  # rug
    # ======== EAST WING: dining + library ========
    for i in range(3):
        z = hz0 + 3 + i * 5
        # long table: stripped logs + lanterns + seats
        for tz in range(z, z + 3):
            v.set(W - 6, 1, tz, STRIPPED_SPRUCE)
        v.set(W - 6, 2, z + 1, CANDLE, {"lit": True, "candles": 2})
        v.set(W - 7, 1, z + 1, SPRUCE_FENCE)  # stools
        v.set(W - 5, 1, z + 1, SPRUCE_FENCE)
    v.set(W - 4, 1, hz1 - 2, "minecraft:barrel")
    v.set(W - 4, 2, hz1 - 2, "minecraft:barrel")
    # library corner: bookshelf stacks
    for x in range(W - 8, W - 3):
        for y in range(1, 4):
            if (x + y) % 2:
                v.set(x, y, hz1 - 1, "minecraft:bookshelf")
    v.set(W - 6, 1, hz1 - 4, "minecraft:lectern", {"minecraft:cardinal_direction": "south"})

    # ======== MAP ROOM TOWER (rear, round, cone roof) ========
    tcx, tcz, trad = mx, 30, 6
    cylinder(v, tcx, tcz, trad, 0, 0, DEEP_TILES, fill_mat=DEEP_TILES)
    cylinder(v, tcx, tcz, trad, 1, 10, STONE)
    # tower windows
    for ang in range(30, 360, 60):
        wx_ = tcx + round(math.cos(math.radians(ang)) * trad)
        wz_ = tcz + round(math.sin(math.radians(ang)) * trad)
        v.set(wx_, 4, wz_, GLASS)
        v.set(wx_, 5, wz_, GLASS)
    # doorway from hall into tower
    v.fill(tcx - 1, 1, hz1, tcx + 1, 3, tcz - trad + 1, "minecraft:air")
    # THE MAP OF ALBION: circular glowing table
    for x in range(tcx - 3, tcx + 4):
        for z in range(tcz - 3, tcz + 4):
            d = math.hypot(x - tcx, z - tcz)
            if d <= 3.4:
                v.set(x, 1, z, DARKOAK)
                roll = r.random()
                blk = ("minecraft:emerald_block" if roll < 0.4 else
                       "minecraft:lapis_block" if roll < 0.6 else
                       "minecraft:moss_block" if roll < 0.85 else GOLD)
                v.set(x, 2, z, blk)
    v.set(tcx, 2, tcz, "minecraft:sea_lantern")  # the Guild's heart-light
    # quest table + lectern by the map
    v.set(tcx - 4, 1, tcz + 2, "minecraft:lectern", {"minecraft:cardinal_direction": "east"})
    v.set(tcx + 4, 1, tcz + 2, "minecraft:bookshelf")
    v.set(tcx + 4, 2, tcz + 2, CANDLE, {"lit": True, "candles": 3})
    # wall sconces inside tower
    for ang in range(0, 360, 90):
        sx_ = tcx + round(math.cos(math.radians(ang)) * (trad - 1))
        sz_ = tcz + round(math.sin(math.radians(ang)) * (trad - 1))
        v.set(sx_, 6, sz_, LANTERN, {"hanging": True})
    # cone roof + finial
    cone_roof(v, tcx, tcz, trad + 1, 11, DEEP_TILES, tip="minecraft:end_rod")
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


def bandit_camp():
    """Twinblade's raider camp: log palisade with a gate, watchtower,
    three wool tents with bedrolls, supply cart, stacked barrels and crates,
    spit-roast campfire, training dummy and a war banner."""
    r = rng("struct", "camp")
    S = 21
    v = Vox(S, 11, S)
    cx = cz = S // 2
    # trampled ground: coarse dirt / path / patches of grass gone bald
    for x in range(S):
        for z in range(S):
            d = math.hypot(x - cx, z - cz)
            if d < 9.6:
                roll = r.random()
                v.set(x, 0, z, "minecraft:coarse_dirt" if roll < 0.5 else
                      (PATH if roll < 0.8 else GRAVEL))
    # ring palisade of spruce logs, gate to the south
    for ang in range(0, 360, 2):
        x = cx + round(math.cos(math.radians(ang)) * 9.5)
        z = cz + round(math.sin(math.radians(ang)) * 9.5)
        if 0 <= x < S and 0 <= z < S:
            if 80 <= ang <= 100:   # gate gap (south, +z)
                continue
            h = 3 + (1 if ang % 8 < 4 else 0)
            for y in range(1, h + 1):
                v.set(x, y, z, SPRUCE_LOG)
            v.set(x, h + 1, z, SPRUCE_FENCE)  # sharpened tips
    # gate posts + lintel + lanterns
    gx0, gx1 = cx - 2, cx + 2
    gz = cz + 9
    for y in range(1, 5):
        v.set(gx0, y, gz, STRIPPED_SPRUCE)
        v.set(gx1, y, gz, STRIPPED_SPRUCE)
    for x in range(gx0, gx1 + 1):
        v.set(x, 5, gz, STRIPPED_SPRUCE)
    v.set(gx0 + 1, 4, gz, LANTERN, {"hanging": True})
    v.set(gx1 - 1, 4, gz, LANTERN, {"hanging": True})
    # watchtower (NE): 4 log legs, plank platform, fence rail, ladder void
    tx, tz = cx + 5, cz - 5
    for lx, lz in ((tx, tz), (tx + 2, tz), (tx, tz + 2), (tx + 2, tz + 2)):
        for y in range(1, 6):
            v.set(lx, y, lz, SPRUCE_LOG)
    for x in range(tx - 1, tx + 4):
        for z in range(tz - 1, tz + 4):
            v.set(x, 6, z, SPRUCE)
    for x in range(tx - 1, tx + 4):
        for z in range(tz - 1, tz + 4):
            if x in (tx - 1, tx + 3) or z in (tz - 1, tz + 3):
                v.set(x, 7, z, SPRUCE_FENCE)
    v.set(tx + 1, 7, tz + 1, "minecraft:campfire")  # signal fire
    v.set(tx + 1, 1, tz + 1, "minecraft:barrel")
    # three tents facing the fire
    tent(v, cx - 8, cz - 3, 5, 3, "red", r)
    tent(v, cx + 3, cz + 2, 5, 3, "brown", r)
    tent(v, cx - 4, cz + 4, 4, 2, "black", r)
    # central spit-roast fire pit
    for dx, dz in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        v.set(cx + dx, 0, cz + dz, COBBLE)
    v.set(cx, 1, cz, "minecraft:campfire")
    v.set(cx - 2, 1, cz, SPRUCE_FENCE)
    v.set(cx + 2, 1, cz, SPRUCE_FENCE)
    v.set(cx - 2, 2, cz, SPRUCE_FENCE)
    v.set(cx + 2, 2, cz, SPRUCE_FENCE)
    for x in range(cx - 1, cx + 2):
        v.set(x, 3, cz, SPRUCE_FENCE)  # spit bar
    # log benches around the fire
    for bz in (cz - 3, cz + 3):
        for x in range(cx - 2, cx + 3):
            v.set(x, 1, bz, STRIPPED_SPRUCE)
    # supply cart: plank bed on log axles, stair shafts, cargo
    wx, wz = cx + 6, cz + 5
    v.set(wx, 1, wz, SPRUCE_LOG)          # axles
    v.set(wx, 1, wz + 2, SPRUCE_LOG)
    for z in range(wz - 1, wz + 4):
        for x in range(wx - 1, wx + 2):
            v.set(x, 2, z, SPRUCE)        # bed
    for x in (wx - 1, wx + 1):
        for z in (wz - 1, wz + 3):
            v.set(x, 3, z, SPRUCE_FENCE)  # corner rails
    v.set(wx, 3, wz, "minecraft:hay_block")
    v.set(wx, 3, wz + 1, "minecraft:barrel")
    v.set(wx, 2, wz + 4, SPRUCE_FENCE)    # towing shaft
    v.set(wx, 2, wz + 5, SPRUCE_FENCE)
    # supply dump: stacked barrels + crates + hay
    sx, sz = cx - 7, cz + 2
    v.set(sx, 1, sz, "minecraft:barrel")
    v.set(sx + 1, 1, sz, "minecraft:barrel")
    v.set(sx, 1, sz + 1, "minecraft:bookshelf")   # crate stand-in
    v.set(sx, 2, sz, "minecraft:barrel")
    v.set(sx + 1, 1, sz - 1, "minecraft:hay_block")
    # loot chest under tarp by north wall
    v.set(cx, 1, cz - 7, "minecraft:chest", {"minecraft:cardinal_direction": "south"})
    v.set(cx - 1, 1, cz - 7, "minecraft:barrel")
    for x in range(cx - 1, cx + 2):
        v.set(x, 2, cz - 7, "minecraft:brown_wool")  # tarp
    # training dummy
    dx_, dz_ = cx - 5, cz - 5
    v.set(dx_, 1, dz_, "minecraft:hay_block")
    v.set(dx_, 2, dz_, "minecraft:hay_block")
    v.set(dx_, 3, dz_, "minecraft:carved_pumpkin", {"minecraft:cardinal_direction": "south"})
    v.set(dx_ - 1, 2, dz_, SPRUCE_FENCE)
    v.set(dx_ + 1, 2, dz_, SPRUCE_FENCE)
    # war banner pole by the gate
    bx = cx + 3
    for y in range(1, 6):
        v.set(bx, y, gz - 1, SPRUCE_FENCE)
    v.set(bx, 5, gz - 2, "minecraft:red_wool")
    v.set(bx, 4, gz - 2, "minecraft:red_wool")
    v.set(bx, 3, gz - 2, "minecraft:black_wool")
    v.save("bandit_camp")


def graveyard():
    """Lychfield: iron-fenced burial ground with a gabled mausoleum,
    varied headstones, an open exhumed grave, dead trees and soul-light."""
    r = rng("struct", "grave")
    S = 15
    v = Vox(S, 9, S)
    for x in range(S):
        for z in range(S):
            roll = r.random()
            v.set(x, 0, z, "minecraft:podzol" if roll < 0.4 else
                  ("minecraft:coarse_dirt" if roll < 0.55 else "minecraft:grass_block"))
    # perimeter: cobble base + iron bars, gate south
    for x in range(S):
        for z in (0, S - 1):
            if z == S - 1 and abs(x - S // 2) <= 1:
                continue
            v.set(x, 1, z, COBBLE)
            v.set(x, 2, z, IRON_BARS)
    for z in range(S):
        for x in (0, S - 1):
            v.set(x, 1, z, COBBLE)
            v.set(x, 2, z, IRON_BARS)
    for gx in (S // 2 - 2, S // 2 + 2):  # gate pillars + lanterns
        v.set(gx, 1, S - 1, CHISELED)
        v.set(gx, 2, S - 1, CHISELED)
        v.set(gx, 3, S - 1, SOUL_LANTERN)
    # gravel path from gate to mausoleum
    for z in range(3, S - 1):
        v.set(S // 2, 0, z, GRAVEL)
    # headstone rows, varied shapes
    for gx in range(2, S - 2, 3):
        for gz in range(4, S - 3, 3):
            if abs(gx - S // 2) < 1 or r.random() > 0.85:
                continue
            style = r.randrange(4)
            if style == 0:   # slab + cross
                v.set(gx, 1, gz, COBBLE)
                v.set(gx, 2, gz, "minecraft:cobblestone_wall")
            elif style == 1:  # tall stele
                v.set(gx, 1, gz, CRACK)
                v.set(gx, 2, gz, STONE)
                v.set(gx, 3, gz, "minecraft:stone_brick_wall")
            elif style == 2:  # toppled
                v.set(gx, 1, gz, MOSSY)
                v.set(gx + 1, 1, gz, "minecraft:cobblestone_wall")
            else:            # humble marker
                v.set(gx, 1, gz, "minecraft:cobblestone_wall")
            if r.random() < 0.3:
                v.set(gx, 1, gz + 1, "minecraft:brown_mushroom")
    # open exhumed grave with dirt pile
    ox, oz = 3, 3
    v.fill(ox, 0, oz, ox + 1, 0, oz + 2, "minecraft:air")
    v.set(ox + 2, 1, oz + 1, "minecraft:coarse_dirt")
    v.set(ox + 2, 2, oz + 1, "minecraft:coarse_dirt")
    v.set(ox, 1, oz - 1, "minecraft:cobblestone_wall")  # its headstone
    # MAUSOLEUM (north): gabled crypt with iron door + coffin
    mx0, mz0 = S // 2 - 3, 1
    for x in range(mx0, mx0 + 7):
        for z in range(mz0, mz0 + 5):
            for y in range(1, 5):
                if x in (mx0, mx0 + 6) or z in (mz0, mz0 + 4):
                    v.set(x, y, z, MOSSY if r.random() < 0.35 else STONE)
    # entrance arch + iron bars door
    v.fill(mx0 + 3, 1, mz0 + 4, mx0 + 3, 2, mz0 + 4, "minecraft:air")
    v.set(mx0 + 3, 1, mz0 + 4, IRON_BARS)
    v.set(mx0 + 2, 3, mz0 + 4, CHISELED)
    v.set(mx0 + 4, 3, mz0 + 4, CHISELED)
    v.set(mx0 + 3, 3, mz0 + 4, "minecraft:chiseled_deepslate")  # skull keystone
    # gable roof
    gable_roof_z(v, mx0 - 1, mx0 + 7, mz0, mz0 + 4, 5, DEEP_TILES, STONE)
    # coffin + candles inside
    v.set(mx0 + 3, 1, mz0 + 2, DARKOAK)
    v.set(mx0 + 3, 1, mz0 + 1, DARKOAK)
    v.set(mx0 + 2, 1, mz0 + 1, CANDLE, {"lit": True})
    v.set(mx0 + 4, 1, mz0 + 2, "minecraft:chest", {"minecraft:cardinal_direction": "west"})
    v.set(mx0 + 3, 4, mz0 + 2, SOUL_LANTERN, {"hanging": True})
    # dead trees
    for tx, tz in ((2, S - 3), (S - 3, 4)):
        h = r.randrange(3, 5)
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
    # rose window (north end): glowing ring
    for dy in range(-1, 2):
        for dxx in range(-1, 2):
            if abs(dxx) + abs(dy) == 1:
                v.set(mx + dxx, 4 + dy, 2, "minecraft:crying_obsidian")
    v.set(mx, 4, 2, "minecraft:magma")
    # steep gable roof
    gable_roof_z(v, 1, W - 2, 2, L - 2, 7, "minecraft:polished_blackstone", "minecraft:polished_blackstone_bricks")
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
    # beast gates N/S: barred arches through all rings
    for gz, gdir in ((0, 1), (D - 1, -1)):
        for x in range(c - 1, c + 2):
            for off in range(0, 6):
                z = gz + gdir * off
                for y in range(1, 4):
                    v.set(x, y, z, "minecraft:air")
        # portcullis bars at the pit mouth
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
    # blood stains + shattered shield props in the pit
    for i in range(6):
        x = c + r.randrange(-6, 7)
        z = c + r.randrange(-6, 7)
        v.set(x, 0, z, "minecraft:red_sand")
    v.set(c - 4, 1, c + 3, "minecraft:bone_block")
    v.set(c + 5, 1, c - 2, "minecraft:cobblestone_wall")
    v.save("arena_ring")


def main():
    print("building structures:")
    demon_door_arch()
    guild_hall()
    silver_chest_ruin()
    focus_site()
    bandit_camp()
    graveyard()
    temple_avo()
    chapel_skorm()
    arena_ring()


if __name__ == "__main__":
    main()

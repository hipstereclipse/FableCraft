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


def guild_hall():
    """The Heroes' Guild, after the academy in Fable: walled grounds entered
    through a twin-towered gatehouse; a grand pitched-roof great hall with
    clerestory windows; the round Map Room tower at the rear; the CULLIS GATE
    teleport circle in the west yard; and the training grounds (archery range,
    sparring ring, Will circle) in the east yard. Loot chests included."""
    r = rng("struct", "guild")
    W, H, L = 45, 26, 41
    v = Vox(W, H, L)
    mx = W // 2

    # ================= GROUNDS + PERIMETER WALL =================
    for x in range(W):
        for z in range(L):
            roll = r.random()
            v.set(x, 0, z, "minecraft:grass_block" if roll < 0.45 else
                  (PATH if roll < 0.6 else STONE))
    # perimeter wall with parapet
    for x in range(W):
        for z in (0, L - 1):
            if z == 0 and abs(x - mx) <= 3:
                continue  # gatehouse opening
            v.set(x, 1, z, rnd_stone(r))
            v.set(x, 2, z, rnd_stone(r))
            v.set(x, 3, z, "minecraft:stone_brick_wall")
    for z in range(L):
        for x in (0, W - 1):
            v.set(x, 1, z, rnd_stone(r))
            v.set(x, 2, z, rnd_stone(r))
            v.set(x, 3, z, "minecraft:stone_brick_wall")
    # corner watch turrets
    for cx_, cz_ in ((1, 1), (W - 2, 1), (1, L - 2), (W - 2, L - 2)):
        for y in range(1, 6):
            v.set(cx_, y, cz_, CHISELED if y > 3 else STONE)
        v.set(cx_, 6, cz_, LANTERN, {"hanging": False})

    # ================= GATEHOUSE (south) with twin round towers =================
    for tx in (mx - 5, mx + 5):
        cylinder(v, tx, 2, 2, 1, 8, STONE)
        cone_roof(v, tx, 2, 3, 9, DEEP_TILES, tip="minecraft:end_rod")
        v.set(tx, 5, 0, GLASS)  # arrow slit
    for x in range(mx - 3, mx + 4):  # arch over the gate
        v.set(x, 5, 0, CHISELED)
        v.set(x, 6, 0, STONE)
    for y in range(1, 5):
        v.set(mx - 3, y, 0, CHISELED)
        v.set(mx + 3, y, 0, CHISELED)
    v.set(mx - 2, 4, 0, LANTERN, {"hanging": True})
    v.set(mx + 2, 4, 0, LANTERN, {"hanging": True})
    v.set(mx, 6, 1, "minecraft:gold_block")  # guild crest above gate
    # path from the gate to the hall doors
    for z in range(1, 13):
        for x in range(mx - 2, mx + 3):
            v.set(x, 0, z, DEEP_TILES if (x + z) % 5 == 0 else STONE)

    # ================= FORECOURT: fountain + hero statue =================
    v.fill(mx - 1, 0, 6, mx + 1, 0, 8, "minecraft:water")
    for x in range(mx - 2, mx + 3):
        for z in range(5, 10):
            if x in (mx - 2, mx + 2) or z in (5, 9):
                v.set(x, 1, z, "minecraft:smooth_quartz")
    v.set(mx, 1, 7, "minecraft:sea_lantern")
    sx, sz = mx - 8, 7  # hero statue
    v.fill(sx - 1, 1, sz - 1, sx + 1, 1, sz + 1, CHISELED)
    v.set(sx, 2, sz, STONE)
    v.set(sx, 3, sz, STONE)
    v.set(sx, 4, sz, CHISELED)
    v.set(sx - 1, 3, sz, "minecraft:stone_brick_wall")
    v.set(sx + 1, 3, sz, "minecraft:stone_brick_wall")
    v.set(sx + 1, 4, sz, "minecraft:end_rod")

    # ================= WEST YARD: THE CULLIS GATE =================
    gx, gz = 6, 20  # portal centre
    for x in range(gx - 4, gx + 5):
        for z in range(gz - 4, gz + 5):
            d = math.hypot(x - gx, z - gz)
            if d <= 4.4:
                v.set(x, 0, z, CHISELED if (x + z) % 2 else DEEP_TILES)
            if 3.4 < d <= 4.4:
                v.set(x, 1, z, OBSIDIAN if (x + z) % 3 else "minecraft:crying_obsidian")
    # the glowing portal ring + heart
    for ang in range(0, 360, 45):
        px_ = gx + round(math.cos(math.radians(ang)) * 2)
        pz_ = gz + round(math.sin(math.radians(ang)) * 2)
        v.set(px_, 1, pz_, "minecraft:sea_lantern" if ang % 90 == 0 else QUARTZ)
    v.set(gx, 1, gz, "minecraft:beacon")
    # four rune pillars
    for ang in range(45, 360, 90):
        px_ = gx + round(math.cos(math.radians(ang)) * 4)
        pz_ = gz + round(math.sin(math.radians(ang)) * 4)
        for y in range(1, 5):
            v.set(px_, y, pz_, OBSIDIAN if y < 3 else "minecraft:crying_obsidian")
        v.set(px_, 5, pz_, "minecraft:amethyst_cluster")
    # worn path from forecourt to the gate
    for x in range(gx + 4, mx - 2):
        v.set(x, 0, 14, PATH)
        v.set(x, 0, 15, PATH)

    # ================= EAST YARD: TRAINING GROUNDS =================
    ty0 = W - 11
    # archery range: 3 targets against the east wall
    for i in range(3):
        az = 12 + i * 4
        v.set(W - 3, 1, az, "minecraft:hay_block")
        v.set(W - 3, 2, az, "minecraft:hay_block")
        v.set(W - 3, 2, az - 1, "minecraft:target")
        v.set(W - 5, 0, az, GRAVEL)  # shooting lane
        v.set(W - 6, 0, az, GRAVEL)
        v.set(W - 7, 0, az, GRAVEL)
    # sparring ring
    rx, rz = ty0 + 4, 28
    for x in range(rx - 3, rx + 4):
        for z in range(rz - 3, rz + 4):
            d = math.hypot(x - rx, z - rz)
            if d <= 3.4:
                v.set(x, 0, z, "minecraft:coarse_dirt" if r.random() < 0.7 else GRAVEL)
            if 2.6 < d <= 3.4:
                v.set(x, 1, z, SPRUCE_FENCE)
    # melee dummies
    for dx_, dz_ in ((rx - 1, rz), (rx + 1, rz + 1)):
        v.set(dx_, 1, dz_, "minecraft:hay_block")
        v.set(dx_, 2, dz_, "minecraft:hay_block")
        v.set(dx_, 3, dz_, "minecraft:carved_pumpkin", {"minecraft:cardinal_direction": "south"})
    # weapon rack + chest of practice gear
    v.set(ty0 + 1, 1, 33, "minecraft:barrel")
    v.set(ty0 + 1, 1, 34, "minecraft:chest", {"minecraft:cardinal_direction": "east"})
    v.set(ty0 + 1, 2, 33, SPRUCE_FENCE)
    # Will circle: candle ring for magic training
    wx, wz = ty0 + 4, 16
    for ang in range(0, 360, 60):
        px_ = wx + round(math.cos(math.radians(ang)) * 2)
        pz_ = wz + round(math.sin(math.radians(ang)) * 2)
        v.set(px_, 0, pz_, DEEP_TILES)
        v.set(px_, 1, pz_, CANDLE, {"lit": True, "candles": 1 + ang % 3})
    v.set(wx, 0, wz, "minecraft:crying_obsidian")

    # ================= NW CORNER: APPLE ORCHARD =================
    for ox_, oz_ in ((3, 29), (7, 32), (4, 36)):
        for y in range(1, 4):
            v.set(ox_, y, oz_, "minecraft:oak_log")
        for dx in (-1, 0, 1):
            for dz in (-1, 0, 1):
                if abs(dx) + abs(dz) <= 1:
                    v.set(ox_ + dx, 4, oz_ + dz, "minecraft:azalea_leaves_flowered")
        v.set(ox_, 5, oz_, "minecraft:azalea_leaves_flowered")
        v.set(ox_ + 1, 3, oz_, "minecraft:oak_leaves")
        v.set(ox_ - 1, 3, oz_, "minecraft:oak_leaves")
    v.set(5, 1, 33, "minecraft:composter")
    v.set(8, 1, 36, "minecraft:beehive")
    v.set(6, 1, 30, "minecraft:sweet_berry_bush", {"growth": 3})

    # ================= SE CORNER: GRAVES OF THE OLD HEROES =================
    for i, (gvx, gvz) in enumerate(((33, 36), (36, 37), (39, 36), (41, 38))):
        v.set(gvx, 1, gvz, MOSSY if i % 2 else CRACK)
        v.set(gvx, 2, gvz, "minecraft:stone_brick_wall")
        if i == 1:
            v.set(gvx, 3, gvz, CHISELED)  # the founder's taller marker
        if i % 2 == 0:
            v.set(gvx + 1, 1, gvz, "minecraft:poppy")
    v.set(37, 1, 35, SOUL_LANTERN)
    v.set(34, 1, 38, "minecraft:cobblestone_wall")

    # ================= GREAT HALL (x 11..W-12, z 12..32) =================
    hx0, hx1, hz0, hz1 = 11, W - 12, 12, 32
    for x in range(hx0, hx1 + 1):
        for z in range(hz0, hz1 + 1):
            v.set(x, 0, z, DEEP_TILES if (x + z) % 5 == 0 else STONE)
    wall_h = 9
    # outer walls with dark-oak pilasters + tall glass
    for x in range(hx0, hx1 + 1):
        for z in (hz0, hz1):
            for y in range(1, wall_h):
                v.set(x, y, z, rnd_stone(r))
    for z in range(hz0, hz1 + 1):
        for x in (hx0, hx1):
            for y in range(1, wall_h):
                v.set(x, y, z, rnd_stone(r))
    for z in range(hz0 + 3, hz1 - 1, 5):
        for x in (hx0, hx1):
            for y in range(1, wall_h + 1):
                v.set(x, y, z, DARKLOG)
            for y in (3, 4, 5):
                v.set(x, y, z + 2, GLASS)
    # grand entrance (south face of hall): recessed arch + crest
    v.fill(mx - 2, 1, hz0, mx + 2, 4, hz0, "minecraft:air")
    for y in range(1, 6):
        v.set(mx - 3, y, hz0, CHISELED)
        v.set(mx + 3, y, hz0, CHISELED)
    for x in range(mx - 3, mx + 4):
        v.set(x, 6, hz0, CHISELED)
    v.set(mx - 1, 5, hz0, CHISELED)
    v.set(mx + 1, 5, hz0, CHISELED)
    v.set(mx, 5, hz0, GOLD)
    v.set(mx - 4, 4, hz0, LANTERN, {"hanging": False})
    v.set(mx + 4, 4, hz0, LANTERN, {"hanging": False})
    # nave columns + red carpet
    for z in range(hz0 + 4, hz1 - 3, 5):
        for cxp in (mx - 5, mx + 5):
            for y in range(1, wall_h - 1):
                v.set(cxp, y, z, DARKLOG)
            v.set(cxp, wall_h - 1, z, GOLD)
    for z in range(hz0 + 1, hz1):
        for x in (mx - 1, mx, mx + 1):
            v.set(x, 0, z, "minecraft:red_wool")
    # the Quest Table: a lectern at the heart of the nave, flanked by candles,
    # where the Hero finds new contracts
    qx, qz = mx, (hz0 + hz1) // 2
    v.set(qx, 1, qz, "minecraft:lectern", {"minecraft:cardinal_direction": "south"})
    v.set(qx - 1, 1, qz, CANDLE, {"lit": True, "candles": 2})
    v.set(qx + 1, 1, qz, CANDLE, {"lit": True, "candles": 2})
    # west wing: dormitory
    for i in range(4):
        z = hz0 + 4 + i * 5
        v.set(hx0 + 2, 1, z, "minecraft:bed", {"direction": 1})
        v.set(hx0 + 3, 1, z, "minecraft:bed", {"direction": 1, "head_piece_bit": True})
        v.set(hx0 + 1, 1, z, "minecraft:chest", {"minecraft:cardinal_direction": "east"})
        v.set(hx0 + 2, 0, z + 1, "minecraft:blue_wool")
    # east wing: feast tables + library
    for i in range(3):
        z = hz0 + 4 + i * 6
        for tz in range(z, z + 3):
            v.set(hx1 - 3, 1, tz, STRIPPED_SPRUCE)
        v.set(hx1 - 3, 2, z + 1, CANDLE, {"lit": True, "candles": 2})
        v.set(hx1 - 4, 1, z + 1, SPRUCE_FENCE)
        v.set(hx1 - 2, 1, z + 1, SPRUCE_FENCE)
    for x in range(hx1 - 6, hx1):
        for y in range(1, 4):
            if (x + y) % 2:
                v.set(x, y, hz1 - 1, "minecraft:bookshelf")
    v.set(hx1 - 3, 1, hz1 - 3, "minecraft:lectern", {"minecraft:cardinal_direction": "south"})
    # storeroom loot chest + barrels
    v.set(hx0 + 1, 1, hz1 - 2, "minecraft:chest", {"minecraft:cardinal_direction": "east"})
    v.set(hx0 + 1, 1, hz1 - 3, "minecraft:barrel")
    v.set(hx0 + 1, 2, hz1 - 3, "minecraft:barrel")
    # gallery floors along the walls
    for z in range(hz0 + 1, hz1):
        for x in list(range(hx0 + 1, hx0 + 4)) + list(range(hx1 - 3, hx1)):
            v.set(x, wall_h - 1, z, SPRUCE)
    # ---- proper pitched roof: stepped gable with 1-block eave overhang ----
    i = 0
    rx0, rx1 = hx0 - 1, hx1 + 1
    while rx0 + i <= rx1 - i:
        y = wall_h + i
        if y >= H - 1:
            break
        for z in range(hz0 - 1, hz1 + 2):
            v.set(rx0 + i, y, z, DEEP_TILES)
            v.set(rx1 - i, y, z, DEEP_TILES)
        # gable end walls
        if rx0 + i + 1 <= rx1 - i - 1:
            for x in range(rx0 + i + 1, rx1 - i):
                v.set(x, y, hz0, STONE)
                v.set(x, y, hz1, STONE)
        i += 1
    ridge_y = min(H - 2, wall_h + i - 1)
    for z in range(hz0 - 1, hz1 + 2, 4):   # ridge crest ornaments
        v.set(mx, ridge_y + 1, z, "minecraft:stone_brick_wall")
    # chimney with ember glow
    chx, chz = hx1 - 2, hz0 + 6
    for y in range(wall_h, ridge_y + 2):
        v.set(chx, y, chz, COBBLE)
    v.set(chx, ridge_y + 2, chz, "minecraft:campfire")
    # hanging lanterns down the nave
    for z in range(hz0 + 4, hz1 - 2, 5):
        v.set(mx, wall_h - 1, z, LANTERN, {"hanging": True})

    # ================= MAP ROOM TOWER (rear) =================
    tcx, tcz, trad = mx, L - 7, 6
    cylinder(v, tcx, tcz, trad, 0, 0, DEEP_TILES, fill_mat=DEEP_TILES)
    cylinder(v, tcx, tcz, trad, 1, 13, STONE)
    for ang in range(30, 360, 60):
        wx_ = tcx + round(math.cos(math.radians(ang)) * trad)
        wz_ = tcz + round(math.sin(math.radians(ang)) * trad)
        v.set(wx_, 5, wz_, GLASS)
        v.set(wx_, 6, wz_, GLASS)
        v.set(wx_, 10, wz_, GLASS)
    # doorway from hall into the tower
    v.fill(tcx - 1, 1, hz1, tcx + 1, 3, tcz - trad + 1, "minecraft:air")
    # THE MAP OF ALBION
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
    v.set(tcx, 2, tcz, "minecraft:sea_lantern")
    v.set(tcx - 4, 1, tcz + 2, "minecraft:lectern", {"minecraft:cardinal_direction": "east"})
    v.set(tcx + 4, 1, tcz + 2, "minecraft:bookshelf")
    v.set(tcx + 4, 2, tcz + 2, CANDLE, {"lit": True, "candles": 3})
    v.set(tcx + 4, 1, tcz - 2, "minecraft:chest", {"minecraft:cardinal_direction": "west"})
    for ang in range(0, 360, 90):
        sx_ = tcx + round(math.cos(math.radians(ang)) * (trad - 1))
        sz_ = tcz + round(math.sin(math.radians(ang)) * (trad - 1))
        v.set(sx_, 7, sz_, LANTERN, {"hanging": True})
    cone_roof(v, tcx, tcz, trad + 1, 14, DEEP_TILES, tip="minecraft:end_rod")
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
    """Heroes' Guild undercroft: circular fresco dome and raised center dais
    with a Cullis focus at the heart."""
    r = rng("struct", "chamber_fate")
    S, H = 31, 18
    v = Vox(S, H, S)
    c = S // 2
    # floor rings
    for x in range(S):
        for z in range(S):
            d = math.hypot(x - c, z - c)
            if d <= 14.2:
                v.set(x, 0, z, DEEP_TILES if (x + z) % 3 else STONE)
            if d <= 10.8:
                v.set(x, 1, z, CHISELED if (x + z) % 2 else DEEP_TILES)
    # outer wall cylinder + mural band
    for x in range(S):
        for z in range(S):
            d = math.hypot(x - c, z - c)
            if 12.0 <= d <= 14.0:
                for y in range(2, 11):
                    v.set(x, y, z, STONE if r.random() < 0.75 else CRACK)
                # mural stripe echoes fresco storytelling
                if 5 <= (x + z) % 14 <= 8:
                    v.set(x, 7, z, "minecraft:red_wool")
                    v.set(x, 8, z, "minecraft:blue_wool")
                    v.set(x, 9, z, "minecraft:white_wool")
    # inner ring columns
    for ang in range(0, 360, 30):
        px = c + round(math.cos(math.radians(ang)) * 9)
        pz = c + round(math.sin(math.radians(ang)) * 9)
        for y in range(2, 10):
            v.set(px, y, pz, QUARTZ if y < 8 else "minecraft:quartz_pillar")
        v.set(px, 10, pz, GOLD if ang % 60 == 0 else CHISELED)
    # stepped center platform
    for x in range(c - 4, c + 5):
        for z in range(c - 4, c + 5):
            d = math.hypot(x - c, z - c)
            if d <= 4.2:
                v.set(x, 2, z, CHISELED)
            if d <= 2.9:
                v.set(x, 3, z, DEEP_TILES)
            if d <= 1.5:
                v.set(x, 4, z, OBSIDIAN if (x + z) % 2 else "minecraft:crying_obsidian")
    # cullis focus
    v.set(c, 5, c, "minecraft:beacon")
    for ang in range(0, 360, 45):
        px = c + round(math.cos(math.radians(ang)) * 3)
        pz = c + round(math.sin(math.radians(ang)) * 3)
        v.set(px, 4, pz, "minecraft:sea_lantern" if ang % 90 == 0 else QUARTZ)
    # cave bridge approach from south
    for z in range(S - 1, c + 5, -1):
        for x in range(c - 2, c + 3):
            v.set(x, 1, z, COBBLE if (x + z) % 2 else MCOBBLE)
            v.set(x, 2, z, "minecraft:air")
    # dome shell
    for y in range(10, H):
        rad = max(2, int(13 - (y - 10) * 0.95))
        for x in range(c - rad - 1, c + rad + 2):
            for z in range(c - rad - 1, c + rad + 2):
                d = math.hypot(x - c, z - c)
                if rad - 0.8 <= d <= rad + 0.5:
                    v.set(x, y, z, STONE if r.random() < 0.8 else CRACK)
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

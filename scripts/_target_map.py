"""Coded TARGET map for the Heroes' Guild — the dense, per-cell GROUND TRUTH
transcribed from the annotated Inkarnate reference (red=building, blue=water,
brown circles=training grounds, grey lines=paths). `target_class(x, z)` labels
EVERY one of the ~13k local cells so `scripts/_audit_match.py` can score the
generated guild against the reference at full resolution (the owner asked for
hundreds–thousands of comparison points, not the ~14 anchors `_grade.py` used).

Regions are keyed to `GUILD_LAYOUT` anchors + the §-doc block coordinates, so they
track `GUILD_EAST`. Run directly to composite the target over the reference crop
for sign-off  ->  scripts/_align/_target_overlay.png
"""
import math
import argparse
from pathlib import Path
from PIL import Image, ImageDraw
import numpy as np
import gen_structures as GS

W, _, L = GS.GUILD_LAYOUT["size"]
EAST = getattr(GS, "GUILD_EAST", 0)
ARCH = GS.GUILD_LAYOUT["archery"]
DUEL = GS.GUILD_LAYOUT["dueling"]
TWR = GS.GUILD_LAYOUT["maze_tower"]
ROT = GS.GUILD_LAYOUT["rotunda"]

# ---- classes (priority: high index wins when a cell matches several) ----
OUTSIDE, FOREST, LAWN, PATH, TRAINING, WATER, BUILDING = range(7)
NAMES = {OUTSIDE: "outside", FOREST: "forest", LAWN: "lawn", PATH: "path",
         TRAINING: "training", WATER: "water", BUILDING: "building"}
COLORS = {OUTSIDE: (28, 36, 28), FOREST: (38, 74, 44), LAWN: (104, 158, 84),
          PATH: (188, 176, 128), TRAINING: (176, 132, 78), WATER: (58, 108, 198),
          BUILDING: (158, 158, 162)}

# ---- transcribed feature regions (LOCAL block coords) ----
# Building footprint = the red-outlined complex (rooms + connective mass), the NE
# block, the covered top hallway, Maze's Tower and the boasting dais.
DOOR = GS.GUILD_LAYOUT["demon_door"]
BUILD_RECT = [
    (41, 3, 98, 6),     # "Stone enclosed hallway / bridge" along the top -> NE block
    (22, 3, 40, 15),    # north wing (covers the west top range) wrapping the cave stair-well
    (18, 16, 36, 30),   # Library (§4.1)
    (10, 31, 35, 52),   # west range: curtain/gate/corridor + Cullis/Skill nooks + rotunda west
    (36, 28, 49, 51),   # Dining hall + Kitchen (§6.1/§6.2)
    (46, 34, 48, 46),   # riverside terrace (narrow — the big patio is lawn/quay now)
    (22, 52, 33, 59),   # Store (§5.1)
    (20, 59, 23, 73),   # cloister — vertical (west) leg
    (20, 71, 41, 73),   # cloister — horizontal (south) leg to the tower
    (74, 6, 98, 28),    # NE block: Food Stores / Dormitory (§7.1/§7.2)
    (1, 21, 7, 31),     # Boasting dais (outside the gate)
    (DOOR[0] - 6, DOOR[1] - 2, DOOR[0] + 6, min(L - 3, DOOR[1] + 7)),  # Demon Door crag
    # the curtain WALL ("Main wall") — thin perimeter bands
    (10, 2, 10, 39), (10, 45, 10, L - 3),                 # west wall (gate gap z40-44)
    (W - 3, 2, W - 3, L - 3),                             # east wall
    (2, 2, W - 3, 3), (2, L - 4, W - 3, L - 3),           # north + south walls
]
BUILD_DISC = [(ROT[0], ROT[1], ROT[2]), (TWR[0], TWR[1], TWR[2]),
              (15, 35, 4), (15, 49, 4)]                   # rotunda, tower, Skill + Cullis nooks
TRAIN_DISC = [(ARCH[0], ARCH[1], ARCH[2]), (DUEL[0], DUEL[1], DUEL[2])]

# Path network (2-wide corridors) transcribed from the reference's grey/gravel lanes.
PATHS = [
    [(0, 42), (10, 42)],                                  # main road into the gate
    [(4, 31), (4, 41)],                                   # boasting -> road spur
    [(26, 52), (26, 60), (31, 62)],                       # store south -> four-graves court
    [(26, 61), (37, 61), (37, 67), (26, 67), (26, 61)],   # graves wrap loop
    [(37, 64), (44, 70)],                                 # court -> cloister/tower avenue
    [(50 + EAST, 30), (50 + EAST, 70)],                   # riverside west-bank walk
    [(60 + EAST, 36), (66 + EAST, 40), ARCH[:2]],         # east bank -> archery
    [ARCH[:2], (DUEL[0] - DUEL[2] - 2, DUEL[1] - 2)],     # archery -> dueling
    [(ARCH[0] + ARCH[2], ARCH[1] - 2), (W - 4, 32)],      # dirt path -> Guild Woods (Exit C)
]


def _rect(x, z, x0, z0, x1, z1):
    return x0 <= x <= x1 and z0 <= z <= z1


def _disc(x, z, cx, cz, r):
    return math.hypot(x - cx, z - cz) <= r + 0.5


def _seg(x, z, ax, az, bx, bz, half):
    dx, dz = bx - ax, bz - az
    d2 = dx * dx + dz * dz
    t = 0.0 if d2 == 0 else max(0.0, min(1.0, ((x - ax) * dx + (z - az) * dz) / d2))
    return math.hypot(x - (ax + t * dx), z - (az + t * dz)) <= half


def _water(x, z):
    if 4 <= z <= 82 and abs(x - (53 + EAST)) <= (2.6 if z < 60 else 3.6):
        return True                                       # the curved river channel
    if z >= 79 and _disc(x, z, 52 + EAST, 88, 14):
        return True                                       # the south pond
    if 6.6 < math.hypot(x - TWR[0], z - TWR[1]) <= 8.6:
        return True                                       # Maze's Tower moat
    return False


def target_class(x, z):
    if not (2 <= x <= W - 3 and 2 <= z <= L - 3):
        # near margin = forest, far = outside
        return FOREST if (-6 <= x <= W + 5 and -6 <= z <= L + 5) else OUTSIDE
    for (cx, cz, r) in BUILD_DISC:
        if _disc(x, z, cx, cz, r):
            return BUILDING
    for (x0, z0, x1, z1) in BUILD_RECT:
        if _rect(x, z, x0, z0, x1, z1):
            return BUILDING
    if _water(x, z):
        return WATER
    for (cx, cz, r) in TRAIN_DISC:
        if _disc(x, z, cx, cz, r):
            return TRAINING
    for poly in PATHS:
        for (ax, az), (bx, bz) in zip(poly, poly[1:]):
            if _seg(x, z, ax, az, bx, bz, 1.0):
                return PATH
    return LAWN


def target_grid():
    g = np.empty((L, W), np.uint8)
    for x in range(W):
        for z in range(L):
            g[z, x] = target_class(x, z)
    return g


def _overlay(reference=None):
    output = Path(__file__).resolve().parent / "_align"
    output.mkdir(exist_ok=True)
    W0, E, N, S = GS.GUILD_LAYOUT["ref_rect"]
    g = target_grid()
    img = np.zeros((L, W, 3), np.uint8)
    for x in range(W):
        for z in range(L):
            img[z, x] = COLORS[int(g[z, x])]
    tgt = Image.fromarray(img, "RGB").resize((E - W0, S - N), Image.NEAREST).convert("RGBA")
    if reference is not None:
        out = Image.open(reference).convert("RGBA")
        layer = Image.new("RGBA", out.size, (0, 0, 0, 0))
        a = np.asarray(tgt).copy()
        a[:, :, 3] = 130
        layer.paste(Image.fromarray(a), (W0, N))
        out = Image.alpha_composite(out, layer)
        d = ImageDraw.Draw(out)
        d.rectangle([W0, N, E, S], outline=(255, 0, 255, 255), width=2)
        out.convert("RGB").save(output / "_target_overlay.png")
        print("wrote", output / "_target_overlay.png")
    else:
        print("Reference overlay not requested; target-only render is not a canon comparison.")
    # also a standalone legend strip render of the target alone
    Image.fromarray(img, "RGB").resize((W * 8, L * 8), Image.NEAREST).save(output / "_target_only.png")
    counts = {NAMES[c]: int((g == c).sum()) for c in NAMES}
    print("target cell counts:", counts)
    print("wrote", output / "_target_only.png")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reference", type=Path, help="Optional original reference image for overlay")
    args = parser.parse_args()
    if args.reference and not args.reference.is_file():
        parser.error(f"reference image does not exist: {args.reference}")
    _overlay(args.reference)

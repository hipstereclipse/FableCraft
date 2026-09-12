"""Dense per-cell audit of the generated Heroes' Guild against the transcribed
TARGET map (scripts/_target_map.py). Compares the class of EVERY local cell
(~13k points) — building / water / training / path / lawn — and reports where the
build deviates so corrective edits can be aimed precisely.

Outputs:
  scripts/_align/_audit.png   3 panels: TARGET | GEN | MISMATCH (red=missing feature,
                              blue=extra feature) on a fine grid
  stdout                      per-class recall/precision + the worst mismatch buckets

Usage:  PYTHONPATH=scripts python scripts/_audit_match.py
"""
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw
import gen_structures as GS
import _target_map as T

W, _, L = GS.GUILD_LAYOUT["size"]
B = T  # class enum + colors live in the target module
PANEL = 980
BUCKET = 8


def build_vox():
    cap = {}
    o = GS.Vox.save
    try:
        GS.Vox.save = lambda self, n: cap.__setitem__(n, self)
        GS.guild_hall()
    finally:
        GS.Vox.save = o
    return cap["guild_hall"]


def gen_grid(vox):
    air = vox._pid("minecraft:air")
    water = vox._pid("minecraft:water")

    def pid(x, y, z):
        return vox.grid[vox.idx(x, y, z)]

    def solid(x, y, z):
        p = pid(x, y, z)
        return p != air and p != water

    _TREE = ("_leaves", "_log", "_wood")

    def roof_solid(x, y, z):
        # a real ROOF/upper-storey block — NOT tree canopy (else every tree reads
        # as "building"), NOT water/air.
        p = pid(x, y, z)
        if p == air or p == water:
            return False
        n = vox.palette[p][0]
        return not any(t in n for t in _TREE)

    def name0(x, z):
        return vox.palette[pid(x, 0, z)][0]

    PATHBLK = {"minecraft:cobblestone", "minecraft:mossy_cobblestone",
               "minecraft:dirt_path", "minecraft:gravel", "minecraft:red_carpet",
               "minecraft:red_wool"}
    LAWNBLK = {"minecraft:grass_block", "minecraft:moss_block", "minecraft:podzol",
               "minecraft:tallgrass", "minecraft:fern"}
    g = np.empty((L, W), np.uint8)
    for x in range(W):
        for z in range(L):
            roofed = any(roof_solid(x, y, z) for y in range(5, 16))
            wall = solid(x, 2, z) and solid(x, 3, z)
            p0 = pid(x, 0, z)
            n0 = name0(x, z)
            if wall or roofed:
                c = B.BUILDING
            elif p0 == water:
                c = B.WATER
            elif n0 == "minecraft:coarse_dirt":
                c = B.TRAINING
            elif n0 in PATHBLK:
                c = B.PATH
            elif n0 in LAWNBLK:
                c = B.LAWN
            elif p0 != air:
                c = B.BUILDING       # bare paved/stone floor reads as built fabric
            else:
                c = B.OUTSIDE
            g[z, x] = c
    return g


def paint(grid):
    img = np.zeros((L, W, 3), np.uint8)
    for x in range(W):
        for z in range(L):
            img[z, x] = B.COLORS[int(grid[z, x])]
    return Image.fromarray(img, "RGB").resize((PANEL, PANEL), Image.NEAREST)


def grid_lines(im, title):
    d = ImageDraw.Draw(im)
    sx, sz = PANEL / W, PANEL / L
    for bx in range(0, W + 1, 20):
        d.line([(bx * sx, 0), (bx * sx, PANEL)], fill=(255, 0, 255), width=1)
        d.text((bx * sx + 2, 2), str(bx), fill=(255, 255, 0))
    for bz in range(0, L + 1, 20):
        d.line([(0, bz * sz), (PANEL, bz * sz)], fill=(255, 0, 255), width=1)
        d.text((2, bz * sz + 2), str(bz), fill=(255, 255, 0))
    d.text((8, PANEL - 18), title, fill=(0, 255, 255))
    return im


FEATURES = (B.BUILDING, B.WATER, B.TRAINING)


def main():
    vox = build_vox()
    tgt = T.target_grid()
    gen = gen_grid(vox)

    # ---- mismatch image: red = target feature missing in gen; blue = gen feature
    #      not in target; faint grey = agree ----
    mm = np.zeros((L, W, 3), np.uint8)
    for x in range(W):
        for z in range(L):
            t, g = int(tgt[z, x]), int(gen[z, x])
            if t == g:
                mm[z, x] = (45, 55, 45)
            elif t in FEATURES and g not in FEATURES:
                mm[z, x] = (220, 40, 40)          # missing a feature here
            elif g in FEATURES and t not in FEATURES:
                mm[z, x] = (60, 90, 230)          # extra feature here
            else:
                mm[z, x] = (210, 180, 60)          # wrong feature class
    mmi = Image.fromarray(mm, "RGB").resize((PANEL, PANEL), Image.NEAREST)

    out = Image.new("RGB", (PANEL * 3 + 24, PANEL), (18, 18, 18))
    out.paste(grid_lines(paint(tgt), "TARGET (transcribed reference)"), (0, 0))
    out.paste(grid_lines(paint(gen), "GENERATED"), (PANEL + 12, 0))
    out.paste(grid_lines(mmi, "MISMATCH  red=missing  blue=extra  yellow=wrong"), (PANEL * 2 + 24, 0))
    output = Path(__file__).resolve().parent / "_align" / "_audit.png"
    output.parent.mkdir(exist_ok=True)
    out.save(output)

    # ---- per-class recall / precision ----
    print("=== per-class match (recall = of target cells, how many gen got right) ===")
    total = ok = 0
    for c in (B.BUILDING, B.WATER, B.TRAINING, B.PATH, B.LAWN):
        tmask = tgt == c
        gmask = gen == c
        inter = int((tmask & gmask).sum())
        tcnt, gcnt = int(tmask.sum()), int(gmask.sum())
        rec = inter / tcnt * 100 if tcnt else 0.0
        prec = inter / gcnt * 100 if gcnt else 0.0
        print(f"  {B.NAMES[c]:9} target={tcnt:5d} gen={gcnt:5d} recall={rec:5.1f}% precision={prec:5.1f}%")
        if c in FEATURES or c == B.LAWN:
            total += tcnt
            ok += inter
    print(f"  -> structural cell agreement (building/water/training/lawn): {ok/total*100:.1f}%")

    # ---- worst mismatch buckets (BUCKET-block tiles), feature-missing first ----
    miss = (np.isin(tgt, FEATURES)) & (~np.isin(gen, FEATURES))
    extra = (np.isin(gen, FEATURES)) & (~np.isin(tgt, FEATURES))
    buckets = []
    for bz in range(0, L, BUCKET):
        for bx in range(0, W, BUCKET):
            m = int(miss[bz:bz + BUCKET, bx:bx + BUCKET].sum())
            e = int(extra[bz:bz + BUCKET, bx:bx + BUCKET].sum())
            if m + e >= 8:
                # dominant target feature in this bucket (to name the fix)
                sub = tgt[bz:bz + BUCKET, bx:bx + BUCKET]
                feats = [c for c in FEATURES if (sub == c).any()]
                buckets.append((m + e, bx, bz, m, e, feats))
    buckets.sort(reverse=True)
    print("\n=== worst mismatch buckets (x..x+%d, z..z+%d) — aim corrective edits here ===" % (BUCKET, BUCKET))
    for tot, bx, bz, m, e, feats in buckets[:18]:
        names = "/".join(B.NAMES[c] for c in feats) or "none"
        print(f"  x{bx:3d}-{bx+BUCKET:3d} z{bz:3d}-{bz+BUCKET:3d}: missing={m:3d} extra={e:3d}  target={names}")
    print("\nwrote scripts/_align/_audit.png")


if __name__ == "__main__":
    main()

"""Resilient overlay-grade for the Heroes' Guild.

Left panel : the canonical Inkarnate plan, cropped to the campus rectangle.
Right panel: a SCHEMATIC built from the actual guild_hall() Vox (not the artistic
render) — walls, floors, carpet, water, roofed mass and the nook cores — so wall
locations, touch-points (doors/carpet/steps) and the nook identities can be read
off and compared to canon in block units.

Canon nooks (per owner): SKILL = green circle (north); WILL/Cullis = dark-blue
circle (south); the WORLD MAP sits between them, a little to the east.

Usage: python scripts/_grade.py [REF_W0 REF_E REF_N REF_S]
"""
import sys
from PIL import Image, ImageDraw
import numpy as np
import gen_structures as GS

REF = r"C:\Users\Eclipse\Downloads\Screenshot 2026-06-13 150337.png"
OUT = "scripts/_align/GRADE.png"
W, L = 112, 108

REF_W0, REF_E, REF_N, REF_S = 185, 886, 42, 694
a = sys.argv[1:]
if len(a) >= 4:
    REF_W0, REF_E, REF_N, REF_S = map(int, a[:4])

# anchors (local x=east, z=south); colour-coded to the canon's circles
ANCHORS = {
    "SKILL(grn)": (15, 35, (80, 255, 80)), "WILL(blu)": (15, 49, (90, 160, 255)),
    "MAP": (26, 42, (255, 230, 60)), "Library": (26, 22, (255, 255, 255)),
    "Tower": (46, 72, (255, 255, 255)), "Archery": (68, 33, (255, 255, 255)),
    "Dueling": (80, 54, (255, 255, 255)), "Kitchen": (76, 17, (255, 255, 255)),
    "Demon": (56, 94, (255, 255, 255)),
}
PANEL = 1000
GRID = 20


def build_vox():
    cap = {}
    orig = GS.Vox.save
    GS.Vox.save = lambda self, n: cap.__setitem__(n, self)
    GS.guild_hall()
    GS.Vox.save = orig
    return cap["guild_hall"]


def schematic(vox):
    """Per-column feature colour, emphasising WALLS and touch-points."""
    air = vox._pid("minecraft:air")
    water = vox._pid("minecraft:water")
    carpet = {vox._pid("minecraft:red_carpet"), vox._pid("minecraft:red_wool")}
    img = np.zeros((L, W, 3), np.uint8)

    def pid(x, y, z):
        return vox.grid[vox.idx(x, y, z)]

    def solid(x, y, z):
        p = pid(x, y, z)
        return p != air and p != water

    for x in range(W):
        for z in range(L):
            p0 = pid(x, 0, z)
            roofed = any(solid(x, y, z) for y in range(5, 16))
            wall = solid(x, 2, z) and solid(x, 3, z)          # a 2-tall standing wall
            carp = pid(x, 1, z) in carpet or p0 in carpet
            if p0 == water:
                c = (60, 90, 200)                              # water
            elif carp:
                c = (200, 40, 40)                              # red carpet / steps (touch-point)
            elif wall:
                c = (20, 20, 20)                               # WALL / pier (compare to canon)
            elif roofed:
                c = (120, 120, 130)                            # roofed interior
            elif p0 != air:
                c = (200, 190, 150)                            # open floor / paving / lawn
            else:
                c = (40, 60, 40)                               # void
            img[z, x] = c
    # nook cores: paint the sea-lantern centres their canon colours
    for (cx, cz, col) in ((15, 35, (80, 255, 80)), (15, 49, (90, 160, 255))):
        for dx in range(-1, 2):
            for dz in range(-1, 2):
                img[cz + dz, cx + dx] = col
    return Image.fromarray(img, "RGB").resize((PANEL, PANEL), Image.NEAREST)


def load_ref():
    im = Image.open(REF).convert("RGB")
    return im.crop((REF_W0, REF_N, REF_E, REF_S)).resize((PANEL, PANEL), Image.LANCZOS)


def grid(img, title):
    d = ImageDraw.Draw(img)
    sx, sz = PANEL / W, PANEL / L
    for bx in range(0, W + 1, GRID):
        d.line([(bx * sx, 0), (bx * sx, PANEL)], fill=(255, 0, 255), width=1)
        d.text((bx * sx + 2, 2), str(bx), fill=(255, 255, 0))
    for bz in range(0, L + 1, GRID):
        d.line([(0, bz * sz), (PANEL, bz * sz)], fill=(255, 0, 255), width=1)
        d.text((2, bz * sz + 2), str(bz), fill=(255, 255, 0))
    for name, (lx, lz, col) in ANCHORS.items():
        x, z = lx * sx, lz * sz
        d.line([(x - 7, z), (x + 7, z)], fill=col, width=2)
        d.line([(x, z - 7), (x, z + 7)], fill=col, width=2)
        d.text((x + 6, z + 4), name, fill=col)
    d.text((8, PANEL - 20), title, fill=(0, 255, 255))
    return img


vox = build_vox()
ref = grid(load_ref(), "CANON (Inkarnate)")
gen = grid(schematic(vox), "SCHEMATIC: black=wall red=carpet blue=water grey=roof")
out = Image.new("RGB", (PANEL * 2 + 12, PANEL), (20, 20, 20))
out.paste(ref, (0, 0)); out.paste(gen, (PANEL + 12, 0))
out.save(OUT)
ref.save("scripts/_align/GRADE_canon.png"); gen.save("scripts/_align/GRADE_gen.png")
print("wrote", OUT, "ref rect", (REF_W0, REF_E, REF_N, REF_S))

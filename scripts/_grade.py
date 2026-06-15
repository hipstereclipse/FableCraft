"""Honest overlay-grade: put the canonical Inkarnate plan and the generated guild
ground-render SIDE BY SIDE at the same campus scale, with a shared local-block
coordinate grid drawn on both, so misalignments can be read off in block units.

Reference campus rectangle (pixels) registers local (0..W, 0..L) onto the ref map.
Generated render is cropped to its non-black campus bbox and scaled to the same box.

Usage: python scripts/_grade.py [REF_W0 REF_E REF_N REF_S]
"""
import sys
from PIL import Image, ImageDraw, ImageFont
import numpy as np

REF = r"C:\Users\Eclipse\Downloads\Screenshot 2026-06-13 150337.png"
GT  = "screenshots/structures/_guild_ground_top.png"
OUT = "scripts/_align/GRADE.png"
W, L = 112, 108

REF_W0, REF_E, REF_N, REF_S = 185, 880, 20, 690
a = sys.argv[1:]
if len(a) >= 4:
    REF_W0, REF_E, REF_N, REF_S = map(int, a[:4])

# anchors (local x=east, z=south) we care about
ANCHORS = {
    "rotunda": (26, 42), "Cullis": (15, 49), "Skill": (15, 35),
    "Library": (26, 22), "Tower": (46, 72), "Demon": (56, 94),
    "Archery": (68, 33), "Dueling": (80, 54),
    "NEblock": (76, 17), "bTop": (52, 20), "bLow": (53, 54),
}

PANEL = 1000  # px per panel side
GRID = 20


def load_ref():
    im = Image.open(REF).convert("RGB")
    crop = im.crop((REF_W0, REF_N, REF_E, REF_S))
    return crop.resize((PANEL, PANEL), Image.LANCZOS)


def load_gen():
    im = Image.open(GT).convert("RGB")
    arr = np.asarray(im)
    mask = arr.sum(axis=2) > 25
    ys, xs = np.where(mask)
    crop = im.crop((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1))
    return crop.resize((PANEL, PANEL), Image.LANCZOS)


def draw_grid(img, title):
    d = ImageDraw.Draw(img)
    sx, sz = PANEL / W, PANEL / L
    for bx in range(0, W + 1, GRID):
        x = bx * sx
        d.line([(x, 0), (x, PANEL)], fill=(255, 0, 255), width=1)
        d.text((x + 2, 2), str(bx), fill=(255, 255, 0))
    for bz in range(0, L + 1, GRID):
        z = bz * sz
        d.line([(0, z), (PANEL, z)], fill=(255, 0, 255), width=1)
        d.text((2, z + 2), str(bz), fill=(255, 255, 0))
    for name, (lx, lz) in ANCHORS.items():
        x, z = lx * sx, lz * sz
        d.line([(x - 7, z), (x + 7, z)], fill=(255, 40, 40), width=2)
        d.line([(x, z - 7), (x, z + 7)], fill=(255, 40, 40), width=2)
        d.text((x + 6, z + 4), name, fill=(255, 255, 255))
    d.text((8, PANEL - 20), title, fill=(0, 255, 255))
    return img


refc = load_ref()
genc = load_gen()
ref = draw_grid(refc.copy(), "CANON (Inkarnate)")
gen = draw_grid(genc.copy(), "GENERATED (ground)")
out = Image.new("RGB", (PANEL * 2 + 12, PANEL), (20, 20, 20))
out.paste(ref, (0, 0))
out.paste(gen, (PANEL + 12, 0))
out.save(OUT)
ref.save("scripts/_align/GRADE_canon.png")
gen.save("scripts/_align/GRADE_gen.png")
# registered overlay: generated at 50% directly on canon
ov = Image.blend(refc, genc, 0.5)
draw_grid(ov, "OVERLAY gen@50% on canon").save("scripts/_align/GRADE_overlay.png")
print("wrote", OUT, "ref rect", (REF_W0, REF_E, REF_N, REF_S))

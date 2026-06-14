"""Overlay the guild top-down render onto the annotated Fable reference map.

Purpose: visually grade how closely the generated guild matches the hand-drawn
Inkarnate ground plan. NOT part of the build; a tuning aid only.

The reference map is artistic (anisotropic, hand-drawn), so the fit is approximate.
We map the topdown's campus bbox onto a campus rectangle in the reference, defined
by four edges (REF_W0/REF_E / REF_N/REF_S) that we tune by eye.

Usage:  python scripts/_overlay_ref.py [W0 E N S] [alpha]
"""
import sys, os
from PIL import Image
import numpy as np

REF = r"C:\Users\Eclipse\Downloads\Screenshot 2026-06-13 150337.png"
TD  = "screenshots/structures/_guild_topdown.png"
GT  = "screenshots/structures/_guild_ground_top.png"
OUT_DIR = "scripts/_align"

# Reference campus rectangle (pixel edges) — tune these.
REF_W0, REF_E, REF_N, REF_S = 185, 880, 20, 690
ALPHA = 0.55

args = sys.argv[1:]
if len(args) >= 4:
    REF_W0, REF_E, REF_N, REF_S = map(int, args[:4])
if len(args) == 1 or len(args) == 5:
    ALPHA = float(args[-1])

os.makedirs(OUT_DIR, exist_ok=True)

def campus_bbox(arr):
    mask = arr.sum(axis=2) > 25
    ys, xs = np.where(mask)
    return xs.min(), ys.min(), xs.max() + 1, ys.max() + 1

def make_overlay(td_path, tag):
    ref = Image.open(REF).convert("RGBA")
    td  = Image.open(td_path).convert("RGB")
    tda = np.asarray(td)
    x0, y0, x1, y1 = campus_bbox(tda)
    crop = td.crop((x0, y0, x1, y1))
    tw, th = REF_E - REF_W0, REF_S - REF_N
    crop = crop.resize((tw, th), Image.LANCZOS).convert("RGBA")
    # build a layer: transparent everywhere, crop at ALPHA
    layer = Image.new("RGBA", ref.size, (0, 0, 0, 0))
    ca = np.asarray(crop).copy()
    # make near-black margin (none after crop) transparent; keep all else
    a = np.full((th, tw), int(255 * ALPHA), np.uint8)
    ca[:, :, 3] = a
    layer.paste(Image.fromarray(ca, "RGBA"), (REF_W0, REF_N))
    out = Image.alpha_composite(ref, layer)
    # draw the campus rectangle outline for reference
    from PIL import ImageDraw
    d = ImageDraw.Draw(out)
    d.rectangle([REF_W0, REF_N, REF_E, REF_S], outline=(255, 0, 255, 255), width=2)
    out = out.convert("RGB")
    p = f"{OUT_DIR}/overlay_{tag}.png"
    out.save(p)
    # also a 1.6x zoom for detail
    out.resize((int(out.width * 1.6), int(out.height * 1.6)), Image.LANCZOS).save(
        f"{OUT_DIR}/overlay_{tag}_zoom.png")
    print(f"{tag}: campus bbox {(x0,y0,x1,y1)} -> ref rect "
          f"W0={REF_W0} E={REF_E} N={REF_N} S={REF_S} alpha={ALPHA}  -> {p}")

make_overlay(TD, "td")
make_overlay(GT, "ground")
print("done")

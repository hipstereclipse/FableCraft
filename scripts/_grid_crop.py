"""Crop a region of an image and draw a labelled pixel grid, so the Read tool
(which downsamples wide images) can show fine detail at readable scale.

Usage:
  python scripts/_grid_crop.py <img> <x0> <y0> <x1> <y1> [grid] [scale] [out]

Saves to scripts/_align/_gc.png unless <out> given. Grid lines every <grid>
source px (default 25), labelled with the SOURCE pixel coordinate. Output is
scaled by <scale> (default chosen so width ~= 200 src px -> fits Read).
"""
import sys, os
from PIL import Image, ImageDraw

img = sys.argv[1]
x0, y0, x1, y1 = map(int, sys.argv[2:6])
grid = int(sys.argv[6]) if len(sys.argv) > 6 else 25
scale = float(sys.argv[7]) if len(sys.argv) > 7 else max(1.0, 210.0 / (x1 - x0))
out = sys.argv[8] if len(sys.argv) > 8 else "scripts/_align/_gc.png"

im = Image.open(img).convert("RGB")
crop = im.crop((x0, y0, x1, y1))
W, H = crop.size
crop = crop.resize((int(W * scale), int(H * scale)), Image.LANCZOS)
d = ImageDraw.Draw(crop)
# vertical grid
gx = (x0 // grid + 1) * grid
while gx < x1:
    px = int((gx - x0) * scale)
    d.line([(px, 0), (px, crop.height)], fill=(255, 0, 255), width=1)
    d.text((px + 1, 1), str(gx), fill=(255, 255, 0))
    gx += grid
# horizontal grid
gy = (y0 // grid + 1) * grid
while gy < y1:
    py = int((gy - y0) * scale)
    d.line([(0, py), (crop.width, py)], fill=(255, 0, 255), width=1)
    d.text((1, py + 1), str(gy), fill=(255, 255, 0))
    gy += grid
crop.save(out)
print(f"{img} [{x0},{y0}..{x1},{y1}] grid={grid} scale={scale:.2f} -> {out} ({crop.size})")

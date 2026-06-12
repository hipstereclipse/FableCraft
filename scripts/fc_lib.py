"""fc_lib.py — shared helpers for the Fablecraft: Reforged build pipeline.

Paths, JSON emission, deterministic RNG, PIL pixel-art helpers and a
little-endian NBT writer for .mcstructure files.
"""
import json
import math
import os
import random
import struct
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent.parent
BP = ROOT / "packs" / "Fablecraft_BP"
RP = ROOT / "packs" / "Fablecraft_RP"
SHOTS = ROOT / "screenshots"
DIST = ROOT / "dist"

NAMESPACE = "fc"
FORMAT_ITEM = "1.21.30"
FORMAT_ENTITY = "1.21.0"
FORMAT_GEO = "1.12.0"

SEED = 1407  # Year of the Guild's founding, why not.


def rng(*key):
    """Deterministic RNG per asset so rebuilds are reproducible."""
    return random.Random(f"{SEED}:{':'.join(str(k) for k in key)}")


def write_json(path: Path, data, sort=False):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, sort_keys=sort)
        f.write("\n")


def write_text(path: Path, text: str):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


# ---------------------------------------------------------------------------
# Colour helpers
# ---------------------------------------------------------------------------

def clamp(v, lo=0, hi=255):
    return max(lo, min(hi, int(v)))


def shade(c, f):
    """Multiply RGB by factor f, keep alpha."""
    if len(c) == 3:
        return (clamp(c[0] * f), clamp(c[1] * f), clamp(c[2] * f), 255)
    return (clamp(c[0] * f), clamp(c[1] * f), clamp(c[2] * f), c[3])


def mix(a, b, t):
    return tuple(clamp(a[i] + (b[i] - a[i]) * t) for i in range(3)) + (255,)


def ramp(base, n=5, lo=0.45, hi=1.35):
    """Build a shading ramp (dark -> light) around a base colour."""
    return [shade(base, lo + (hi - lo) * i / (n - 1)) for i in range(n)]


def with_alpha(c, a):
    return (c[0], c[1], c[2], a)


# ---------------------------------------------------------------------------
# Pixel art canvas
# ---------------------------------------------------------------------------

class Px:
    """Tiny pixel-art canvas wrapper around PIL with shading utilities."""

    def __init__(self, w=16, h=16):
        self.img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        self.d = ImageDraw.Draw(self.img)
        self.w, self.h = w, h

    def px(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            self.img.putpixel((int(x), int(y)), c)

    def get(self, x, y):
        if 0 <= x < self.w and 0 <= y < self.h:
            return self.img.getpixel((int(x), int(y)))
        return (0, 0, 0, 0)

    def line(self, x0, y0, x1, y1, c, width=1):
        steps = int(max(abs(x1 - x0), abs(y1 - y0))) + 1
        for i in range(steps + 1):
            t = i / max(1, steps)
            x = x0 + (x1 - x0) * t
            y = y0 + (y1 - y0) * t
            for ox in range(width):
                for oy in range(width):
                    self.px(round(x) + ox - width // 2, round(y) + oy - width // 2, c)

    def rect(self, x, y, w, h, c):
        for yy in range(int(y), int(y + h)):
            for xx in range(int(x), int(x + w)):
                self.px(xx, yy, c)

    def rect_outline(self, x, y, w, h, c):
        for xx in range(int(x), int(x + w)):
            self.px(xx, y, c)
            self.px(xx, y + h - 1, c)
        for yy in range(int(y), int(y + h)):
            self.px(x, yy, c)
            self.px(x + w - 1, yy, c)

    def disc(self, cx, cy, r, c):
        for yy in range(int(cy - r), int(cy + r + 1)):
            for xx in range(int(cx - r), int(cx + r + 1)):
                if (xx - cx) ** 2 + (yy - cy) ** 2 <= r * r + 0.4:
                    self.px(xx, yy, c)

    def noise_rect(self, x, y, w, h, palette, r, density=1.0):
        """Fill a rect with random picks from a shading palette."""
        for yy in range(int(y), int(y + h)):
            for xx in range(int(x), int(x + w)):
                if r.random() <= density:
                    self.px(xx, yy, palette[r.randrange(len(palette))])

    def outline(self, c=(20, 14, 10, 255)):
        """1px contour around all opaque pixels."""
        src = self.img.copy()
        for y in range(self.h):
            for x in range(self.w):
                if src.getpixel((x, y))[3] == 0:
                    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < self.w and 0 <= ny < self.h and src.getpixel((nx, ny))[3] > 60:
                            self.px(x, y, c)
                            break

    def glow(self, color, strength=70):
        """Soft halo behind opaque pixels (for magical items)."""
        halo = Image.new("RGBA", (self.w, self.h), (0, 0, 0, 0))
        hd = ImageDraw.Draw(halo)
        for y in range(self.h):
            for x in range(self.w):
                if self.img.getpixel((x, y))[3] > 100:
                    hd.ellipse([x - 2, y - 2, x + 2, y + 2],
                               fill=with_alpha(color, strength))
        halo.alpha_composite(self.img)
        self.img = halo
        self.d = ImageDraw.Draw(self.img)

    def save(self, path):
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        self.img.save(path)


# ---------------------------------------------------------------------------
# Little-endian NBT writer (Bedrock .mcstructure)
# ---------------------------------------------------------------------------

TAG_END, TAG_BYTE, TAG_SHORT, TAG_INT, TAG_LONG = 0, 1, 2, 3, 4
TAG_FLOAT, TAG_DOUBLE, TAG_BYTE_ARRAY, TAG_STRING = 5, 6, 7, 8
TAG_LIST, TAG_COMPOUND, TAG_INT_ARRAY = 9, 10, 11


class NBT:
    """Tagged value. Use helper constructors below."""

    def __init__(self, tag, value):
        self.tag = tag
        self.value = value


def nbt_byte(v):
    return NBT(TAG_BYTE, v)


def nbt_short(v):
    return NBT(TAG_SHORT, v)


def nbt_int(v):
    return NBT(TAG_INT, v)


def nbt_long(v):
    return NBT(TAG_LONG, v)


def nbt_float(v):
    return NBT(TAG_FLOAT, v)


def nbt_string(v):
    return NBT(TAG_STRING, v)


def nbt_list(tag, values):
    return NBT(TAG_LIST, (tag, values))


def nbt_compound(d):
    return NBT(TAG_COMPOUND, d)


def _w_str(buf, s):
    raw = s.encode("utf-8")
    buf += struct.pack("<H", len(raw))
    buf += raw


def _w_payload(buf, node):
    t, v = node.tag, node.value
    if t == TAG_BYTE:
        buf += struct.pack("<b", v)
    elif t == TAG_SHORT:
        buf += struct.pack("<h", v)
    elif t == TAG_INT:
        buf += struct.pack("<i", v)
    elif t == TAG_LONG:
        buf += struct.pack("<q", v)
    elif t == TAG_FLOAT:
        buf += struct.pack("<f", v)
    elif t == TAG_DOUBLE:
        buf += struct.pack("<d", v)
    elif t == TAG_STRING:
        _w_str(buf, v)
    elif t == TAG_LIST:
        et, items = v
        buf += struct.pack("<b", et)
        buf += struct.pack("<i", len(items))
        for it in items:
            _w_payload(buf, it)
    elif t == TAG_COMPOUND:
        for name, child in v.items():
            buf += struct.pack("<b", child.tag)
            _w_str(buf, name)
            _w_payload(buf, child)
        buf += struct.pack("<b", TAG_END)
    else:
        raise ValueError(f"unsupported tag {t}")


def write_mcstructure(path: Path, root: NBT):
    """Write a root compound (unnamed '') as little-endian NBT."""
    buf = bytearray()
    buf += struct.pack("<b", TAG_COMPOUND)
    _w_str(buf, "")
    _w_payload(buf, root)
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(bytes(buf))


# ---------------------------------------------------------------------------
# Misc
# ---------------------------------------------------------------------------

def title_case(ident: str) -> str:
    small = {"of", "the", "a", "an", "and"}
    words = ident.replace("_", " ").split()
    out = []
    for i, w in enumerate(words):
        out.append(w if (w in small and i > 0) else w.capitalize())
    return " ".join(out)

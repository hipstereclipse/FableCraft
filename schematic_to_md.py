#!/usr/bin/env python3
"""
schematic_to_md.py — Convert .schematic (and .litematic / .nbt) Minecraft world files
into extremely descriptive Markdown build guides.

Usage:
    python schematic_to_md.py                    (open analyzer GUI)
    python schematic_to_md.py --nogui <file.schematic> [output.md]
    python schematic_to_md.py <file.schematic> [output.md]
    python schematic_to_md.py *.schematic          (batch)

Supports:
  • Classic .schematic  (MCEdit / Schematica — "Schematic" NBT root)
  • Sponge .schem       (WorldEdit 1.13+ — "Schematic" or "Version" tag)
  • .litematic          (Litematica mod — "Regions" tag)
  • .nbt                (vanilla structure files — "size" + "blocks" tags)
"""

import sys
import os
import math
import gzip
import struct
import threading
import queue
import time
from collections import Counter, defaultdict
from pathlib import Path
from typing import Optional
import nbtlib

try:
    import tkinter as tk
    from tkinter import filedialog
except Exception:
    tk = None
    filedialog = None

try:
    from tkinter import ttk, messagebox
except Exception:
    ttk = None
    messagebox = None

try:
    from tkinter import scrolledtext
except Exception:
    scrolledtext = None


CHUNK_SIZE = 16
NATURAL_BLOCK_KEYWORDS = (
    "stone", "dirt", "grass", "sand", "gravel", "water", "lava", "clay",
    "deepslate", "andesite", "diorite", "granite", "ice", "snow", "mud",
    "tuff", "basalt", "netherrack", "soul_sand", "mycelium", "podzol",
)


class AnalysisCancelled(Exception):
    """Raised when the user cancels a running analysis."""


# ---------------------------------------------------------------------------
# Block name helpers
# ---------------------------------------------------------------------------

DIRECTIONS = {
    0: "South", 1: "West", 2: "North", 3: "East",
    4: "Up",    5: "Down",
}

CARDINAL = {0: "S", 1: "W", 2: "N", 3: "E"}

def strip_namespace(name: str) -> str:
    """minecraft:stone → stone"""
    return name.split(":")[-1] if ":" in name else name

def pretty_block(name: str) -> str:
    return strip_namespace(name).replace("_", " ").title()

def coord_label(x, y, z) -> str:
    return f"({x}, {y}, {z})"


# ---------------------------------------------------------------------------
# Legacy block-ID → name table (1.12 and earlier)
# ---------------------------------------------------------------------------

LEGACY_BLOCKS = {
    0: "air", 1: "stone", 2: "grass", 3: "dirt", 4: "cobblestone",
    5: "planks", 6: "sapling", 7: "bedrock", 8: "flowing_water", 9: "water",
    10: "flowing_lava", 11: "lava", 12: "sand", 13: "gravel", 14: "gold_ore",
    15: "iron_ore", 16: "coal_ore", 17: "log", 18: "leaves", 19: "sponge",
    20: "glass", 21: "lapis_ore", 22: "lapis_block", 23: "dispenser",
    24: "sandstone", 25: "noteblock", 26: "bed", 27: "golden_rail",
    28: "detector_rail", 29: "sticky_piston", 30: "web", 31: "tallgrass",
    32: "deadbush", 33: "piston", 34: "piston_head", 35: "wool",
    37: "yellow_flower", 38: "red_flower", 39: "brown_mushroom",
    40: "red_mushroom", 41: "gold_block", 42: "iron_block",
    43: "double_stone_slab", 44: "stone_slab", 45: "brick_block",
    46: "tnt", 47: "bookshelf", 48: "mossy_cobblestone", 49: "obsidian",
    50: "torch", 51: "fire", 52: "mob_spawner", 53: "oak_stairs",
    54: "chest", 55: "redstone_wire", 56: "diamond_ore",
    57: "diamond_block", 58: "crafting_table", 59: "wheat",
    60: "farmland", 61: "furnace", 62: "lit_furnace", 63: "standing_sign",
    64: "wooden_door", 65: "ladder", 66: "rail", 67: "stone_stairs",
    68: "wall_sign", 69: "lever", 70: "stone_pressure_plate", 71: "iron_door",
    72: "wooden_pressure_plate", 73: "redstone_ore", 74: "lit_redstone_ore",
    75: "unlit_redstone_torch", 76: "redstone_torch", 77: "stone_button",
    78: "snow_layer", 79: "ice", 80: "snow", 81: "cactus", 82: "clay",
    83: "reeds", 84: "jukebox", 85: "fence", 86: "pumpkin",
    87: "netherrack", 88: "soul_sand", 89: "glowstone", 90: "portal",
    91: "lit_pumpkin", 92: "cake", 93: "unpowered_repeater",
    94: "powered_repeater", 95: "stained_glass", 96: "trapdoor",
    97: "monster_egg", 98: "stonebrick", 99: "brown_mushroom_block",
    100: "red_mushroom_block", 101: "iron_bars", 102: "glass_pane",
    103: "melon_block", 104: "pumpkin_stem", 105: "melon_stem",
    106: "vine", 107: "fence_gate", 108: "brick_stairs",
    109: "stone_brick_stairs", 110: "mycelium", 111: "waterlily",
    112: "nether_brick", 113: "nether_brick_fence",
    114: "nether_brick_stairs", 115: "nether_wart", 116: "enchanting_table",
    117: "brewing_stand", 118: "cauldron", 119: "end_portal",
    120: "end_portal_frame", 121: "end_stone", 122: "dragon_egg",
    123: "redstone_lamp", 124: "lit_redstone_lamp", 125: "double_wooden_slab",
    126: "wooden_slab", 127: "cocoa", 128: "sandstone_stairs",
    129: "emerald_ore", 130: "ender_chest", 131: "tripwire_hook",
    132: "tripwire", 133: "emerald_block", 134: "spruce_stairs",
    135: "birch_stairs", 136: "jungle_stairs", 137: "command_block",
    138: "beacon", 139: "cobblestone_wall", 140: "flower_pot",
    141: "carrots", 142: "potatoes", 143: "wooden_button",
    144: "skull", 145: "anvil", 146: "trapped_chest",
    147: "light_weighted_pressure_plate", 148: "heavy_weighted_pressure_plate",
    149: "unpowered_comparator", 150: "powered_comparator",
    151: "daylight_detector", 152: "redstone_block", 153: "quartz_ore",
    154: "hopper", 155: "quartz_block", 156: "quartz_stairs",
    157: "activator_rail", 158: "dropper", 159: "stained_hardened_clay",
    160: "stained_glass_pane", 161: "leaves2", 162: "log2",
    163: "acacia_stairs", 164: "dark_oak_stairs", 165: "slime",
    166: "barrier", 167: "iron_trapdoor", 168: "prismarine",
    169: "sea_lantern", 170: "hay_block", 171: "carpet",
    172: "hardened_clay", 173: "coal_block", 174: "packed_ice",
    175: "double_plant", 176: "standing_banner", 177: "wall_banner",
    178: "daylight_detector_inverted", 179: "red_sandstone",
    180: "red_sandstone_stairs", 181: "double_stone_slab2",
    182: "stone_slab2", 183: "spruce_fence_gate", 184: "birch_fence_gate",
    185: "jungle_fence_gate", 186: "dark_oak_fence_gate",
    187: "acacia_fence_gate", 188: "spruce_fence", 189: "birch_fence",
    190: "jungle_fence", 191: "dark_oak_fence", 192: "acacia_fence",
    193: "spruce_door", 194: "birch_door", 195: "jungle_door",
    196: "acacia_door", 197: "dark_oak_door", 198: "end_rod",
    199: "chorus_plant", 200: "chorus_flower", 201: "purpur_block",
    202: "purpur_pillar", 203: "purpur_stairs", 204: "purpur_double_slab",
    205: "purpur_slab", 206: "end_bricks", 207: "beetroots",
    208: "grass_path", 209: "end_gateway", 210: "repeating_command_block",
    211: "chain_command_block", 212: "frosted_ice", 213: "magma",
    214: "nether_wart_block", 215: "red_nether_brick", 216: "bone_block",
    217: "structure_void", 218: "observer", 219: "white_shulker_box",
    255: "structure_block",
}

WOOL_COLORS = ["White","Orange","Magenta","Light Blue","Yellow","Lime",
               "Pink","Gray","Light Gray","Cyan","Purple","Blue",
               "Brown","Green","Red","Black"]

PLANKS_TYPES = ["Oak","Spruce","Birch","Jungle","Acacia","Dark Oak"]

def legacy_block_name(block_id: int, data: int = 0) -> str:
    name = LEGACY_BLOCKS.get(block_id, f"unknown_{block_id}")
    if name == "wool" and 0 <= data < 16:
        name = f"{WOOL_COLORS[data].lower().replace(' ','_')}_wool"
    elif name == "planks" and 0 <= data < 6:
        name = f"{PLANKS_TYPES[data].lower()}_planks"
    elif name in ("log", "log2") and data & 3 < 6:
        types1 = ["oak","spruce","birch","jungle"]
        types2 = ["acacia","dark_oak"]
        idx = data & 3
        name = (types1[idx] if name == "log" else types2[idx]) + "_log"
    elif name == "leaves" and data & 3 < 4:
        types = ["oak","spruce","birch","jungle"]
        name = types[data & 3] + "_leaves"
    elif name == "stone" and 0 < data < 7:
        variants = ["","granite","polished_granite","diorite",
                    "polished_diorite","andesite","polished_andesite"]
        name = variants[data]
    return name


# ---------------------------------------------------------------------------
# Schematic parsers
# ---------------------------------------------------------------------------

class Block:
    __slots__ = ("name", "properties", "x", "y", "z")
    def __init__(self, name, x, y, z, properties=None):
        self.name = name
        self.x = x
        self.y = y
        self.z = z
        self.properties = properties or {}

    def pretty(self) -> str:
        return pretty_block(self.name)

    def is_air(self) -> bool:
        return self.name in ("air", "minecraft:air", "cave_air",
                             "minecraft:cave_air", "void_air")


def _nbt_int(tag):
    """Unwrap any nbtlib numeric tag to a plain Python int."""
    if hasattr(tag, '__index__'):
        return int(tag)
    return int(str(tag))


def parse_classic_schematic(nbt_data) -> list[Block]:
    """MCEdit / Schematica format (Blocks + Data byte arrays)."""
    root = nbt_data.get("Schematic") or nbt_data
    width  = _nbt_int(root["Width"])
    height = _nbt_int(root["Height"])
    length = _nbt_int(root["Length"])

    raw_blocks = bytes(root["Blocks"])
    raw_data   = bytes(root.get("Data", b"\x00" * len(raw_blocks)))

    # AddBlocks for blocks above ID 255
    add_blocks = bytes(root["AddBlocks"]) if "AddBlocks" in root else None

    blocks = []
    for y in range(height):
        for z in range(length):
            for x in range(width):
                idx = (y * length + z) * width + x
                bid = raw_blocks[idx]
                if add_blocks:
                    nibble_idx = idx >> 1
                    if idx & 1:
                        bid |= (add_blocks[nibble_idx] & 0xF0)
                    else:
                        bid |= (add_blocks[nibble_idx] & 0x0F) << 8
                data = raw_data[idx] & 0x0F
                name = legacy_block_name(bid, data)
                b = Block(name, x, y, z)
                blocks.append(b)
    return blocks


def parse_sponge_schematic(nbt_data) -> list[Block]:
    """WorldEdit Sponge .schem format."""
    root = nbt_data.get("Schematic") or nbt_data
    width  = _nbt_int(root["Width"])
    height = _nbt_int(root["Height"])
    length = _nbt_int(root["Length"])

    palette = {}
    for k, v in root["Palette"].items():
        palette[_nbt_int(v)] = k  # e.g. "minecraft:stone[snowy=false]"

    block_data = bytes(root["BlockData"])

    # VarInt decode
    def read_varints(data):
        values = []
        val = 0
        shift = 0
        for byte in data:
            val |= (byte & 0x7F) << shift
            shift += 7
            if not (byte & 0x80):
                values.append(val)
                val = 0
                shift = 0
        return values

    indices = read_varints(block_data)

    blocks = []
    for i, state_idx in enumerate(indices):
        y = i // (width * length)
        rem = i % (width * length)
        z = rem // width
        x = rem % width
        raw = palette.get(state_idx, "minecraft:air")
        # split "minecraft:stone[half=bottom,facing=north]"
        if "[" in raw:
            name, props_str = raw.split("[", 1)
            props_str = props_str.rstrip("]")
            props = dict(p.split("=") for p in props_str.split(",") if "=" in p)
        else:
            name = raw
            props = {}
        blocks.append(Block(strip_namespace(name), x, y, z, props))
    return blocks


def parse_litematic(nbt_data) -> list[Block]:
    """Litematica .litematic format."""
    root = nbt_data
    regions = root.get("Regions") or root.get("regions")
    if not regions:
        raise ValueError("No Regions tag found — not a .litematic file?")

    all_blocks = []
    for region_name, region in regions.items():
        size = region.get("Size") or region.get("size")
        width  = abs(_nbt_int(size["x"]))
        height = abs(_nbt_int(size["y"]))
        length = abs(_nbt_int(size["z"]))

        palette_list = region.get("BlockStatePalette") or region.get("blockStatePalette", [])
        palette = []
        for entry in palette_list:
            name = str(entry.get("Name", "minecraft:air")).replace('"','')
            props = {}
            if "Properties" in entry:
                for k, v in entry["Properties"].items():
                    props[str(k).replace('"','')] = str(v).replace('"','')
            palette.append((strip_namespace(name), props))

        bits_per_block = max(2, math.ceil(math.log2(max(len(palette), 2))))
        raw_longs = region.get("BlockStates") or region.get("blockStates", [])
        raw_longs = [_nbt_int(v) for v in raw_longs]

        # Unpack bit-packed longs
        total_blocks = width * height * length
        mask = (1 << bits_per_block) - 1

        def get_state(block_idx):
            bit_start = block_idx * bits_per_block
            long_idx  = bit_start >> 6
            bit_off   = bit_start & 63
            if long_idx >= len(raw_longs):
                return 0
            val = raw_longs[long_idx] & 0xFFFFFFFFFFFFFFFF
            if bit_off + bits_per_block > 64:
                if long_idx + 1 < len(raw_longs):
                    val |= (raw_longs[long_idx + 1] & 0xFFFFFFFFFFFFFFFF) << 64
            return (val >> bit_off) & mask

        for i in range(total_blocks):
            y = i // (width * length)
            rem = i % (width * length)
            z = rem // width
            x = rem % width
            idx = get_state(i)
            if idx < len(palette):
                name, props = palette[idx]
            else:
                name, props = "air", {}
            all_blocks.append(Block(name, x, y, z, props))

    return all_blocks


def parse_nbt_structure(nbt_data) -> list[Block]:
    """Vanilla NBT structure (.nbt) files."""
    root = nbt_data

    size = root.get("size", [])
    if size:
        # sx = _nbt_int(size[0])
        pass

    palette = []
    for entry in root.get("palette", []):
        name = str(entry.get("Name", "minecraft:air")).replace('"','')
        props = {}
        if "Properties" in entry:
            for k, v in entry["Properties"].items():
                props[str(k).replace('"','')] = str(v).replace('"','')
        palette.append((strip_namespace(name), props))

    blocks = []
    for block_entry in root.get("blocks", []):
        pos = block_entry["pos"]
        x, y, z = _nbt_int(pos[0]), _nbt_int(pos[1]), _nbt_int(pos[2])
        state = _nbt_int(block_entry["state"])
        if state < len(palette):
            name, props = palette[state]
        else:
            name, props = "air", {}
        blocks.append(Block(name, x, y, z, props))
    return blocks


def load_schematic(path: str) -> list[Block]:
    """Auto-detect and parse any supported schematic format."""
    with open(path, "rb") as f:
        magic = f.read(2)

    if magic == b"\x1f\x8b":
        with gzip.open(path, "rb") as f:
            raw = f.read()
    else:
        with open(path, "rb") as f:
            raw = f.read()

    nbt_data = nbtlib.load(path)

    # Detect format
    if "Schematic" in nbt_data:
        root = nbt_data["Schematic"]
        if "Palette" in root and "BlockData" in root:
            return parse_sponge_schematic(nbt_data)
        if "Blocks" in root:
            return parse_classic_schematic(nbt_data)
    # flat-root classic
    if "Blocks" in nbt_data and "Width" in nbt_data:
        return parse_classic_schematic(nbt_data)
    # sponge flat root
    if "Palette" in nbt_data and "BlockData" in nbt_data:
        return parse_sponge_schematic(nbt_data)
    # litematic
    if "Regions" in nbt_data or "regions" in nbt_data:
        return parse_litematic(nbt_data)
    # vanilla .nbt
    if "blocks" in nbt_data and "palette" in nbt_data:
        return parse_nbt_structure(nbt_data)

    raise ValueError(f"Unrecognised schematic format in {path}")


# ---------------------------------------------------------------------------
# Analysis helpers
# ---------------------------------------------------------------------------

def bounding_box(blocks: list[Block]):
    xs = [b.x for b in blocks]
    ys = [b.y for b in blocks]
    zs = [b.z for b in blocks]
    return (min(xs), max(xs)), (min(ys), max(ys)), (min(zs), max(zs))


def non_air(blocks: list[Block]) -> list[Block]:
    return [b for b in blocks if not b.is_air()]


def chunk_coord(x: int, z: int, chunk_size: int = CHUNK_SIZE) -> tuple[int, int]:
    return x // chunk_size, z // chunk_size


def is_natural_block(name: str) -> bool:
    n = strip_namespace(name)
    return any(k in n for k in NATURAL_BLOCK_KEYWORDS)


def block_interest_score(block: Block) -> int:
    if block.is_air():
        return 0
    role = classify_block_role(block.name)
    if role in ("redstone", "functional", "lighting"):
        return 8
    if role == "structural-detail":
        return 4
    if role == "window":
        return 5
    if role in ("wood", "stone") and not is_natural_block(block.name):
        return 3
    if is_natural_block(block.name):
        return 0
    return 1


def find_interesting_chunks(
    blocks: list[Block],
    min_interest: int = 200,
    min_density: float = 0.08,
    chunk_size: int = CHUNK_SIZE,
    progress_cb=None,
    cancel_cb=None,
):
    """Score chunks and return those likely to contain player-made structures."""
    per_chunk_blocks = defaultdict(int)
    per_chunk_interest = defaultdict(int)
    per_chunk_non_natural = defaultdict(int)

    total_blocks = max(len(blocks), 1)
    for idx, b in enumerate(blocks, start=1):
        if cancel_cb and cancel_cb():
            raise AnalysisCancelled("Cancelled while scanning chunks")
        if b.is_air():
            continue
        c = chunk_coord(b.x, b.z, chunk_size)
        per_chunk_blocks[c] += 1
        score = block_interest_score(b)
        per_chunk_interest[c] += score
        if not is_natural_block(b.name):
            per_chunk_non_natural[c] += 1
        if progress_cb and (idx % 50000 == 0 or idx == total_blocks):
            progress_cb("chunk_scan", idx, total_blocks)

    interesting = set()
    metrics = {}
    chunk_volume = chunk_size * chunk_size

    for c, total in per_chunk_blocks.items():
        interest = per_chunk_interest[c]
        non_natural = per_chunk_non_natural[c]
        density = non_natural / max(total, 1)
        rough_2d_density = total / chunk_volume
        metrics[c] = {
            "total": total,
            "interest": interest,
            "non_natural": non_natural,
            "density": density,
            "footprint_density": rough_2d_density,
        }
        if interest >= min_interest and density >= min_density:
            interesting.add(c)

    return interesting, metrics


def expand_chunk_set(chunks: set[tuple[int, int]], radius: int = 1) -> set[tuple[int, int]]:
    if not chunks or radius <= 0:
        return set(chunks)
    expanded = set(chunks)
    for cx, cz in list(chunks):
        for dx in range(-radius, radius + 1):
            for dz in range(-radius, radius + 1):
                expanded.add((cx + dx, cz + dz))
    return expanded


def filter_blocks_by_chunks(
    blocks: list[Block],
    chunks: set[tuple[int, int]],
    chunk_size: int = CHUNK_SIZE,
) -> list[Block]:
    if not chunks:
        return []
    return [b for b in blocks if chunk_coord(b.x, b.z, chunk_size) in chunks]


def layer_grid(blocks: list[Block], y: int, x_range, z_range) -> list[list[Optional[Block]]]:
    """Return a 2D grid [z][x] for a given Y layer."""
    x0, x1 = x_range
    z0, z1 = z_range
    layer_map = {(b.x, b.z): b for b in blocks if b.y == y and not b.is_air()}
    grid = []
    for z in range(z0, z1 + 1):
        row = []
        for x in range(x0, x1 + 1):
            row.append(layer_map.get((x, z)))
        grid.append(row)
    return grid


def detect_structures(blocks: list[Block], progress_cb=None, cancel_cb=None) -> list[dict]:
    """
    Heuristic structure detection: flood-fill connected components of
    non-air blocks that are spatially contiguous.
    Returns list of dicts with 'blocks', 'bbox', 'label'.
    """
    solid = non_air(blocks)
    coord_set = {(b.x, b.y, b.z): b for b in solid}

    visited = set()
    components = []

    def flood(start):
        stack = [start]
        comp = []
        while stack:
            if cancel_cb and cancel_cb():
                raise AnalysisCancelled("Cancelled while detecting structures")
            pos = stack.pop()
            if pos in visited:
                continue
            visited.add(pos)
            if pos in coord_set:
                comp.append(coord_set[pos])
                x, y, z = pos
                for dx, dy, dz in [(1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1)]:
                    nb = (x+dx, y+dy, z+dz)
                    if nb not in visited and nb in coord_set:
                        stack.append(nb)
        return comp

    total_positions = len(coord_set)
    processed = 0

    for pos in coord_set:
        if cancel_cb and cancel_cb():
            raise AnalysisCancelled("Cancelled while detecting structures")
        if pos not in visited:
            comp = flood(pos)
            if comp:
                components.append(comp)
        processed += 1
        if progress_cb and (processed % 5000 == 0 or processed == total_positions):
            progress_cb("structure_scan", processed, total_positions)

    # Sort by size descending
    components.sort(key=lambda c: len(c), reverse=True)

    results = []
    for i, comp in enumerate(components):
        xs = [b.x for b in comp]; ys = [b.y for b in comp]; zs = [b.z for b in comp]
        results.append({
            "id": i + 1,
            "blocks": comp,
            "bbox": ((min(xs), max(xs)), (min(ys), max(ys)), (min(zs), max(zs))),
            "size": (max(xs)-min(xs)+1, max(ys)-min(ys)+1, max(zs)-min(zs)+1),
        })
    return results


def material_summary(blocks: list[Block]) -> Counter:
    c = Counter()
    for b in blocks:
        if not b.is_air():
            c[b.name] += 1
    return c


def redstone_blocks() -> set:
    return {
        "redstone_wire","redstone_torch","redstone_lamp","redstone_block",
        "repeater","comparator","piston","sticky_piston","observer",
        "hopper","dropper","dispenser","daylight_detector",
        "tripwire","tripwire_hook","lever","button","pressure_plate",
        "wooden_button","stone_button","target",
    }

def interactive_blocks() -> set:
    return {
        "chest","barrel","furnace","blast_furnace","smoker","crafting_table",
        "enchanting_table","anvil","brewing_stand","beacon","ender_chest",
        "shulker_box","loom","cartography_table","grindstone","smithing_table",
        "stonecutter","composter","bell","lectern","cauldron","chiseled_bookshelf",
    }


def classify_block_role(name: str) -> str:
    n = strip_namespace(name)
    if n in redstone_blocks() or any(r in n for r in ("redstone","piston","observer","hopper","dropper","dispenser","comparator","repeater")):
        return "redstone"
    if any(s in n for s in ("_stairs", "_slab", "_wall", "fence", "door", "trapdoor", "gate")):
        return "structural-detail"
    if any(s in n for s in ("glass","glass_pane","iron_bars")):
        return "window"
    if any(s in n for s in ("torch","lantern","glowstone","sea_lantern","shroomlight","beacon","end_rod")):
        return "lighting"
    if n in interactive_blocks() or any(s in n for s in ("chest","barrel","furnace","crafting","anvil")):
        return "functional"
    if any(s in n for s in ("log","wood","planks","stripped")):
        return "wood"
    if any(s in n for s in ("stone","cobble","brick","concrete","terracotta","quartz","deepslate","basalt")):
        return "stone"
    if "water" in n or "lava" in n:
        return "fluid"
    if any(s in n for s in ("grass","dirt","sand","gravel","mycelium","podzol","mud","clay")):
        return "earth"
    return "misc"


# ---------------------------------------------------------------------------
# Markdown generation
# ---------------------------------------------------------------------------

def render_layer_ascii(grid: list[list[Optional[Block]]]) -> str:
    """Render a layer as an ASCII block map."""
    symbol_map = {}
    symbol_chars = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789#@&%$!+~^")
    legend = {}

    lines = []
    for row in grid:
        line = ""
        for cell in row:
            if cell is None:
                line += "."
            else:
                name = strip_namespace(cell.name)
                if name not in symbol_map:
                    idx = len(symbol_map)
                    sym = symbol_chars[idx % len(symbol_chars)]
                    symbol_map[name] = sym
                    legend[sym] = pretty_block(name)
                line += symbol_map[name]
        lines.append(line)

    result = "```\n"
    result += "\n".join(lines)
    result += "\n```\n"
    if legend:
        result += "\n**Legend:**\n"
        for sym, name in legend.items():
            result += f"- `{sym}` = {name}\n"
    return result


def structure_shape_desc(size) -> str:
    w, h, d = size
    if w == d and w == h:
        return f"cubic ({w}³)"
    if w == d:
        return f"square footprint ({w}×{d}), height {h}"
    if h == 1:
        return f"flat slab ({w}×{d})"
    return f"{w} wide × {h} tall × {d} deep"


def redstone_description(blocks: list[Block]) -> str:
    rs = [b for b in blocks if classify_block_role(b.name) == "redstone"]
    if not rs:
        return ""
    out = "### Redstone & Mechanisms\n\n"
    counts = Counter(pretty_block(b.name) for b in rs)
    out += "| Component | Count |\n|---|---|\n"
    for name, count in counts.most_common():
        out += f"| {name} | {count} |\n"
    out += "\n"

    # Repeaters
    repeaters = [b for b in rs if "repeater" in b.name]
    if repeaters:
        delays = Counter(b.properties.get("delay","1") for b in repeaters)
        out += f"**Repeaters:** {len(repeaters)} total. "
        delay_desc = ", ".join(f"{v}× delay-{k}" for k,v in sorted(delays.items()))
        out += f"Delay breakdown: {delay_desc}.\n\n"

    # Comparators
    comps = [b for b in rs if "comparator" in b.name]
    if comps:
        modes = Counter(b.properties.get("mode","compare") for b in comps)
        out += f"**Comparators:** {len(comps)} total. "
        out += f"Modes: {dict(modes)}.\n\n"

    # Pistons
    pistons = [b for b in rs if "piston" in b.name and "head" not in b.name]
    if pistons:
        sticky = [b for b in pistons if "sticky" in b.name]
        normal = [b for b in pistons if "sticky" not in b.name]
        out += f"**Pistons:** {len(sticky)} sticky, {len(normal)} normal.\n\n"

    return out


def functional_description(blocks: list[Block]) -> str:
    func = [b for b in blocks if classify_block_role(b.name) == "functional"]
    if not func:
        return ""
    counts = Counter(pretty_block(b.name) for b in func)
    out = "### Functional Blocks / Storage\n\n"
    out += "| Block | Count | Positions |\n|---|---|---|\n"
    block_positions = defaultdict(list)
    for b in func:
        block_positions[b.name].append(coord_label(b.x, b.y, b.z))
    for name, count in counts.most_common():
        positions = block_positions[name][:5]
        pos_str = ", ".join(positions)
        if len(block_positions[name]) > 5:
            pos_str += f" …+{len(block_positions[name])-5} more"
        out += f"| {pretty_block(name)} | {count} | {pos_str} |\n"
    return out + "\n"


def layer_descriptions(blocks: list[Block], x_range, z_range, max_layers=None) -> str:
    y_vals = sorted(set(b.y for b in blocks if not b.is_air()))
    if not y_vals:
        return ""

    # Identify interesting layers (not just repeats of previous)
    def layer_sig(y):
        return frozenset((b.x, b.z, b.name) for b in blocks if b.y == y and not b.is_air())

    shown = 0
    last_sig = None
    out = "## Layer-by-Layer Build Guide\n\n"
    out += ("> Layers are listed bottom to top (increasing Y). "
            "Identical consecutive layers are collapsed.\n\n")

    layer_groups = []
    current_sig = None
    current_start = None

    for y in y_vals:
        sig = layer_sig(y)
        if sig == current_sig:
            pass
        else:
            if current_sig is not None:
                layer_groups.append((current_start, y - 1, current_sig))
            current_sig = sig
            current_start = y
    if current_sig is not None:
        layer_groups.append((current_start, y_vals[-1], current_sig))

    for y_start, y_end, sig in layer_groups:
        if max_layers and shown >= max_layers:
            remaining = len(layer_groups) - shown
            out += f"> *…{remaining} more layer group(s) omitted for brevity.*\n\n"
            break

        layer_blocks = [b for b in blocks if b.y == y_start and not b.is_air()]
        name_counts = Counter(pretty_block(b.name) for b in layer_blocks)
        total = sum(name_counts.values())

        if y_start == y_end:
            heading = f"### Layer Y={y_start}"
        else:
            heading = f"### Layers Y={y_start}–{y_end} *(repeated {y_end - y_start + 1}×)*"

        out += heading + "\n\n"
        out += f"**Blocks in layer:** {total} non-air\n\n"

        # Block list
        out += "| Block Type | Count |\n|---|---|\n"
        for name, count in name_counts.most_common():
            out += f"| {name} | {count} |\n"
        out += "\n"

        # ASCII map for layers with reasonable width
        w = x_range[1] - x_range[0] + 1
        d = z_range[1] - z_range[0] + 1
        if w <= 48 and d <= 48:
            grid = layer_grid(blocks, y_start, x_range, z_range)
            out += "**Top-down map (X→ Z↓):**\n\n"
            out += render_layer_ascii(grid)
        else:
            out += f"*(Layer too large for ASCII map: {w}×{d})*\n\n"

        # Notable blocks with positions
        special = [b for b in layer_blocks if classify_block_role(b.name) in
                   ("redstone","functional","lighting")]
        if special:
            out += "**Notable blocks this layer:**\n\n"
            for b in special[:20]:
                role = classify_block_role(b.name)
                out += f"- `{pretty_block(b.name)}` at {coord_label(b.x, b.y, b.z)} *[{role}]*\n"
            if len(special) > 20:
                out += f"- *…and {len(special)-20} more*\n"
            out += "\n"

        shown += 1

    return out


def generate_markdown(
    path: str,
    blocks: list[Block],
    analysis_mode: str = "targeted",
    interest_threshold: int = 200,
    density_threshold: float = 0.08,
    chunk_padding: int = 1,
    progress_cb=None,
    cancel_cb=None,
) -> str:
    name = Path(path).stem

    if progress_cb:
        progress_cb("prepare", 0, 1)
    if cancel_cb and cancel_cb():
        raise AnalysisCancelled("Cancelled before analysis started")

    all_solid = non_air(blocks)
    analysis_blocks = blocks
    chunk_stats = {}
    selected_chunks = set()

    if analysis_mode == "targeted":
        selected_chunks, chunk_stats = find_interesting_chunks(
            all_solid,
            min_interest=interest_threshold,
            min_density=density_threshold,
            progress_cb=progress_cb,
            cancel_cb=cancel_cb,
        )
        selected_chunks = expand_chunk_set(selected_chunks, radius=chunk_padding)
        filtered = filter_blocks_by_chunks(blocks, selected_chunks)
        if filtered:
            analysis_blocks = filtered
    if cancel_cb and cancel_cb():
        raise AnalysisCancelled("Cancelled during analysis")

    solid = non_air(analysis_blocks)

    if not solid:
        solid = all_solid
        analysis_blocks = blocks

    (x0, x1), (y0, y1), (z0, z1) = bounding_box(analysis_blocks)
    width  = x1 - x0 + 1
    height = y1 - y0 + 1
    length = z1 - z0 + 1

    materials = material_summary(analysis_blocks)
    if progress_cb:
        progress_cb("structure_scan", 0, max(len(solid), 1))
    structures = detect_structures(analysis_blocks, progress_cb=progress_cb, cancel_cb=cancel_cb)
    if progress_cb:
        progress_cb("structure_scan", max(len(solid), 1), max(len(solid), 1))

    md = []

    # ------------------------------------------------------------------ Title
    md.append(f"# Minecraft Build Guide: `{name}`\n")
    md.append(f"> *Auto-generated from `{Path(path).name}` by schematic_to_md.py*\n")

    # ----------------------------------------------------------- Overview
    md.append("## Overview\n")
    md.append(f"| Property | Value |")
    md.append(f"|---|---|")
    md.append(f"| Schematic file | `{Path(path).name}` |")
    md.append(f"| Total blocks in file (incl. air) | {len(blocks):,} |")
    md.append(f"| Blocks analyzed (incl. air) | {len(analysis_blocks):,} |")
    md.append(f"| Non-air blocks | {len(solid):,} |")
    md.append(f"| Bounding box | {width} × {height} × {length} (W×H×D) |")
    md.append(f"| X range | {x0} → {x1} |")
    md.append(f"| Y range | {y0} → {y1} (ground → top) |")
    md.append(f"| Z range | {z0} → {z1} |")
    md.append(f"| Distinct block types | {len(materials)} |")
    md.append(f"| Connected structures detected | {len(structures)} |\n")

    if analysis_mode == "targeted":
        md.append("## Targeted Analysis Details\n")
        md.append("| Metric | Value |")
        md.append("|---|---|")
        md.append(f"| Mode | Targeted chunk filtering |")
        md.append(f"| Interest threshold | {interest_threshold} |")
        md.append(f"| Density threshold | {density_threshold:.3f} |")
        md.append(f"| Chunk padding radius | {chunk_padding} |")
        md.append(f"| Selected chunks | {len(selected_chunks):,} |")
        md.append(f"| Candidate chunks scanned | {len(chunk_stats):,} |\n")

    # --------------------------------------------------------- Structures
    if len(structures) > 1:
        md.append("## Detected Sub-Structures\n")
        md.append("The schematic contains multiple spatially separate components:\n")
        md.append("| # | Block count | Dimensions (W×H×D) | Position (min corner) |")
        md.append("|---|---|---|---|")
        for s in structures[:20]:
            (sx0,sx1),(sy0,sy1),(sz0,sz1) = s["bbox"]
            w,h,d = s["size"]
            md.append(f"| {s['id']} | {len(s['blocks']):,} | {w}×{h}×{d} | {coord_label(sx0,sy0,sz0)} |")
        if len(structures) > 20:
            md.append(f"| … | {len(structures)-20} more structures | | |")
        md.append("")

        # Describe each structure
        for s in structures[:10]:
            (sx0,sx1),(sy0,sy1),(sz0,sz1) = s["bbox"]
            w,h,d = s["size"]
            md.append(f"### Structure {s['id']} — {structure_shape_desc(s['size'])}\n")
            md.append(f"- **Position:** {coord_label(sx0,sy0,sz0)} → {coord_label(sx1,sy1,sz1)}")
            md.append(f"- **Block count:** {len(s['blocks']):,}")

            smats = material_summary(s["blocks"])
            top5 = smats.most_common(5)
            top5_str = ", ".join(f"{pretty_block(n)} ×{c}" for n,c in top5)
            md.append(f"- **Dominant materials:** {top5_str}")

            roles = Counter(classify_block_role(b.name) for b in s["blocks"])
            role_str = ", ".join(f"{v} {k}" for k,v in roles.most_common())
            md.append(f"- **Block roles:** {role_str}\n")

    # ------------------------------------------------------- Material list
    md.append("## Full Material List\n")
    md.append("All quantities needed to build this schematic from scratch:\n")
    md.append("| Material | Quantity | Stacks | Role |")
    md.append("|---|---|---|---|")
    for bname, count in materials.most_common():
        stacks = f"{count // 64}×64 + {count % 64}" if count >= 64 else "< 1 stack"
        role = classify_block_role(bname)
        md.append(f"| {pretty_block(bname)} | {count:,} | {stacks} | {role} |")
    md.append("")

    # ---------------------------------------------- Block-role breakdown
    md.append("## Block Role Breakdown\n")
    roles = Counter(classify_block_role(b.name) for b in solid)
    total_solid = len(solid)
    md.append("| Role | Count | % of Structure |")
    md.append("|---|---|---|")
    for role, count in roles.most_common():
        pct = count / total_solid * 100
        md.append(f"| {role.title()} | {count:,} | {pct:.1f}% |")
    md.append("")

    # ------------------------------------------ Redstone & Functional
    rs_desc = redstone_description(solid)
    if rs_desc:
        md.append(rs_desc)
    func_desc = functional_description(solid)
    if func_desc:
        md.append(func_desc)

    # -------------------------------------------- Layer-by-layer guide
    max_layers = 80  # cap for very tall builds
    md.append(layer_descriptions(analysis_blocks, (x0, x1), (z0, z1), max_layers=max_layers))

    # -------------------------------------------- Build tips
    md.append("## Build Tips & Sequence\n")
    md.append("Follow this order for the smoothest construction experience:\n")

    steps = []
    if any(b for b in solid if classify_block_role(b.name) == "earth"):
        steps.append("**1. Terrain prep** — Lay the foundation blocks (dirt, sand, stone) first "
                     "to establish the ground level.")
    steps.append(f"**2. Structural shell** — Place the main structural blocks layer by layer "
                 f"from Y={y0} upward. Refer to the ASCII maps above for each layer's footprint.")
    if any(b for b in solid if classify_block_role(b.name) == "window"):
        steps.append("**3. Windows & transparent elements** — Insert glass panes/iron bars after "
                     "the surrounding frame is complete.")
    if any(b for b in solid if classify_block_role(b.name) == "redstone"):
        steps.append("**4. Redstone wiring** — Install redstone components (wire, repeaters, "
                     "comparators, pistons) after the walls are up. Wire from the output device "
                     "back toward the input source.")
    if any(b for b in solid if classify_block_role(b.name) == "functional"):
        steps.append("**5. Functional blocks** — Place storage (chests, barrels), crafting "
                     "stations, and other interactables once the room is enclosed.")
    if any(b for b in solid if classify_block_role(b.name) == "lighting"):
        steps.append("**6. Lighting** — Add torches, lanterns, glowstone, and sea lanterns last "
                     "after redstone is tested.")
    if any(b for b in solid if classify_block_role(b.name) == "structural-detail"):
        steps.append("**7. Decorative details** — Stairs, slabs, fences, and walls for trim and "
                     "visual texture can be placed any time after the main structure is stable.")

    for step in steps:
        md.append(f"- {step}\n")

    md.append("\n---\n")
    md.append(f"*Generated by `schematic_to_md.py`. Schematic: `{Path(path).name}` "
              f"— {len(solid):,} blocks across {height} layers.*\n")

    if progress_cb:
        progress_cb("done", 1, 1)

    return "\n".join(md)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def process_file(input_path: str, output_path: Optional[str] = None):
    print(f"[+] Loading: {input_path}")
    blocks = load_schematic(input_path)
    print(f"    {len(blocks):,} total blocks loaded")

    print("[+] Analysing…")
    md = generate_markdown(
        input_path,
        blocks,
        analysis_mode="targeted",
        interest_threshold=200,
        density_threshold=0.08,
        chunk_padding=1,
    )

    if output_path is None:
        output_path = str(Path(input_path).with_suffix(".md"))

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(md)

    print(f"[✓] Written: {output_path}  ({len(md):,} chars)")
    return output_path


def pick_input_file() -> Optional[str]:
    """Open a file picker to choose a supported schematic file."""
    if tk is None or filedialog is None:
        return None

    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    try:
        selected = filedialog.askopenfilename(
            title="Select a schematic file",
            filetypes=[
                (
                    "Minecraft schematic files",
                    "*.schematic *.schem *.litematic *.nbt",
                ),
                ("All files", "*.*"),
            ],
        )
    finally:
        root.destroy()

    return selected or None


def _progress_stage_label(stage: str) -> str:
    labels = {
        "prepare": "Preparing",
        "chunk_scan": "Scanning chunks",
        "structure_scan": "Detecting structures",
        "done": "Done",
    }
    return labels.get(stage, stage.replace("_", " ").title())


class SchematicAnalyzerGUI:
    def __init__(self):
        if tk is None or ttk is None:
            raise RuntimeError("Tkinter/ttk not available in this Python environment")

        self.root = tk.Tk()
        self.root.title("Schematic to Markdown Analyzer")
        self.root.geometry("760x410")
        self.root.minsize(700, 360)

        self.queue = queue.Queue()
        self.worker = None
        self.cancel_event = threading.Event()
        self.current_task = None
        self.start_time = None
        self.last_stage = None
        self.last_stage_pct = 0.0

        self.input_var = tk.StringVar()
        self.output_var = tk.StringVar()
        self.mode_var = tk.StringVar(value="targeted")
        self.interest_var = tk.IntVar(value=200)
        self.density_var = tk.DoubleVar(value=0.08)
        self.padding_var = tk.IntVar(value=1)

        self.status_var = tk.StringVar(value="Choose a schematic and press Analyze")
        self.progress_var = tk.DoubleVar(value=0.0)

        self._build_ui()
        self.root.after(100, self._poll_queue)

    def _build_ui(self):
        frame = ttk.Frame(self.root, padding=12)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="Input schematic:").grid(row=0, column=0, sticky="w")
        ttk.Entry(frame, textvariable=self.input_var, width=80).grid(row=1, column=0, sticky="ew", padx=(0, 8))
        ttk.Button(frame, text="Browse", command=self.browse_input).grid(row=1, column=1, sticky="ew")

        ttk.Label(frame, text="Output markdown (optional):").grid(row=2, column=0, sticky="w", pady=(10, 0))
        ttk.Entry(frame, textvariable=self.output_var, width=80).grid(row=3, column=0, sticky="ew", padx=(0, 8))
        ttk.Button(frame, text="Save As", command=self.browse_output).grid(row=3, column=1, sticky="ew")

        options = ttk.LabelFrame(frame, text="Analysis Options", padding=10)
        options.grid(row=4, column=0, columnspan=2, sticky="ew", pady=(12, 0))

        ttk.Radiobutton(options, text="Targeted (interesting chunks only)", variable=self.mode_var, value="targeted").grid(row=0, column=0, sticky="w")
        ttk.Radiobutton(options, text="Full (entire file)", variable=self.mode_var, value="full").grid(row=0, column=1, sticky="w", padx=(16, 0))

        ttk.Label(options, text="Interest threshold:").grid(row=1, column=0, sticky="w", pady=(10, 0))
        ttk.Entry(options, textvariable=self.interest_var, width=10).grid(row=1, column=0, sticky="e", pady=(10, 0))

        ttk.Label(options, text="Density threshold (0-1):").grid(row=1, column=1, sticky="w", pady=(10, 0))
        ttk.Entry(options, textvariable=self.density_var, width=10).grid(row=1, column=1, sticky="e", pady=(10, 0))

        ttk.Label(options, text="Chunk padding radius:").grid(row=2, column=0, sticky="w", pady=(8, 0))
        ttk.Entry(options, textvariable=self.padding_var, width=10).grid(row=2, column=0, sticky="e", pady=(8, 0))

        self.progress = ttk.Progressbar(frame, variable=self.progress_var, maximum=100, mode="determinate")
        self.progress.grid(row=5, column=0, columnspan=2, sticky="ew", pady=(14, 0))
        ttk.Label(frame, textvariable=self.status_var).grid(row=6, column=0, columnspan=2, sticky="w", pady=(6, 0))

        preview_box = ttk.LabelFrame(frame, text="Targeted Chunk Preview", padding=8)
        preview_box.grid(row=7, column=0, columnspan=2, sticky="nsew", pady=(10, 0))
        if scrolledtext is not None:
            self.preview_text = scrolledtext.ScrolledText(preview_box, height=8, wrap="word")
        else:
            self.preview_text = tk.Text(preview_box, height=8, wrap="word")
        self.preview_text.pack(fill="both", expand=True)
        self.preview_text.insert("1.0", "No preview yet. Click 'Preview Chunks' in targeted mode.")
        self.preview_text.configure(state="disabled")

        btns = ttk.Frame(frame)
        btns.grid(row=8, column=0, columnspan=2, sticky="e", pady=(14, 0))
        self.preview_btn = ttk.Button(btns, text="Preview Chunks", command=self.start_preview)
        self.preview_btn.pack(side="left")
        self.analyze_btn = ttk.Button(btns, text="Analyze", command=self.start_analysis)
        self.analyze_btn.pack(side="left", padx=(8, 0))
        self.cancel_btn = ttk.Button(btns, text="Cancel", command=self.cancel_task, state="disabled")
        self.cancel_btn.pack(side="left", padx=(8, 0))
        ttk.Button(btns, text="Close", command=self.root.destroy).pack(side="left", padx=(8, 0))

        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(7, weight=1)

    def browse_input(self):
        path = filedialog.askopenfilename(
            title="Select schematic",
            filetypes=[
                ("Minecraft schematic files", "*.schematic *.schem *.litematic *.nbt"),
                ("All files", "*.*"),
            ],
        )
        if path:
            self.input_var.set(path)
            if not self.output_var.get().strip():
                self.output_var.set(str(Path(path).with_suffix(".md")))

    def browse_output(self):
        initial = self.output_var.get().strip() or "output.md"
        path = filedialog.asksaveasfilename(
            title="Save markdown as",
            initialfile=Path(initial).name,
            defaultextension=".md",
            filetypes=[("Markdown", "*.md"), ("All files", "*.*")],
        )
        if path:
            self.output_var.set(path)

    def _set_running(self, running: bool):
        active = "disabled" if running else "normal"
        cancel_state = "normal" if running else "disabled"
        self.analyze_btn.configure(state=active)
        self.preview_btn.configure(state=active)
        self.cancel_btn.configure(state=cancel_state)

    def _set_preview_text(self, text: str):
        self.preview_text.configure(state="normal")
        self.preview_text.delete("1.0", "end")
        self.preview_text.insert("1.0", text)
        self.preview_text.configure(state="disabled")

    def cancel_task(self):
        if self.worker and self.worker.is_alive():
            self.cancel_event.set()
            self.status_var.set("Cancelling... waiting for current stage to stop")

    def start_preview(self):
        if self.worker and self.worker.is_alive():
            return

        if self.mode_var.get().strip() != "targeted":
            self._set_preview_text("Preview is only available in targeted mode. Switch mode to targeted first.")
            return

        input_path = self.input_var.get().strip()
        if not input_path or not os.path.isfile(input_path):
            if messagebox:
                messagebox.showerror("Invalid input", "Select a valid schematic file first.")
            return

        try:
            interest = int(self.interest_var.get())
            density = float(self.density_var.get())
            padding = int(self.padding_var.get())
            density = max(0.0, min(1.0, density))
            padding = max(0, padding)
        except Exception:
            if messagebox:
                messagebox.showerror("Invalid options", "Check threshold and padding values.")
            return

        self.current_task = "preview"
        self.cancel_event.clear()
        self.start_time = time.time()
        self.last_stage = None
        self.last_stage_pct = 0.0
        self.progress_var.set(0)
        self.status_var.set("Starting chunk preview...")
        self._set_running(True)

        self.worker = threading.Thread(
            target=self._run_preview,
            args=(input_path, interest, density, padding),
            daemon=True,
        )
        self.worker.start()

    def start_analysis(self):
        if self.worker and self.worker.is_alive():
            return

        input_path = self.input_var.get().strip()
        if not input_path:
            if messagebox:
                messagebox.showerror("Missing input", "Select a schematic file first.")
            return
        if not os.path.isfile(input_path):
            if messagebox:
                messagebox.showerror("Invalid input", "Selected input file does not exist.")
            return

        output_path = self.output_var.get().strip() or str(Path(input_path).with_suffix(".md"))
        mode = self.mode_var.get().strip() or "targeted"

        try:
            interest = int(self.interest_var.get())
            density = float(self.density_var.get())
            padding = int(self.padding_var.get())
            density = max(0.0, min(1.0, density))
            padding = max(0, padding)
        except Exception:
            if messagebox:
                messagebox.showerror("Invalid options", "Check threshold and padding values.")
            return

        self.current_task = "analysis"
        self.cancel_event.clear()
        self.start_time = time.time()
        self.last_stage = None
        self.last_stage_pct = 0.0
        self.progress_var.set(0)
        self.status_var.set("Starting analysis...")
        self._set_running(True)

        self.worker = threading.Thread(
            target=self._run_analysis,
            args=(input_path, output_path, mode, interest, density, padding),
            daemon=True,
        )
        self.worker.start()

    def _run_preview(self, input_path, interest, density, padding):
        try:
            self.queue.put(("status", "Loading schematic for preview..."))
            blocks = load_schematic(input_path)
            solid = non_air(blocks)

            def progress_cb(stage, cur, total):
                total = max(int(total), 1)
                cur = max(0, min(int(cur), total))
                pct = (cur / total) * 100.0
                msg = f"{_progress_stage_label(stage)}: {cur:,}/{total:,}"
                self.queue.put(("progress", pct, msg, stage, cur, total))

            selected, stats = find_interesting_chunks(
                solid,
                min_interest=interest,
                min_density=density,
                progress_cb=progress_cb,
                cancel_cb=self.cancel_event.is_set,
            )
            selected = expand_chunk_set(selected, radius=padding)

            ranked = sorted(
                selected,
                key=lambda c: stats.get(c, {}).get("interest", 0),
                reverse=True,
            )
            lines = []
            lines.append(f"Input non-air blocks: {len(solid):,}")
            lines.append(f"Candidate chunks: {len(stats):,}")
            lines.append(f"Selected chunks (with padding): {len(selected):,}")
            lines.append("")
            lines.append("Top selected chunks by interest:")
            for i, c in enumerate(ranked[:40], start=1):
                m = stats.get(c, {})
                lines.append(
                    f"{i:02d}. chunk {c}: interest={m.get('interest', 0):,}, "
                    f"non_natural={m.get('non_natural', 0):,}, density={m.get('density', 0.0):.3f}"
                )
            if len(ranked) > 40:
                lines.append(f"... and {len(ranked) - 40:,} more")

            self.queue.put(("preview_done", "\n".join(lines)))
        except AnalysisCancelled:
            self.queue.put(("cancelled", "Preview cancelled"))
        except Exception as exc:
            self.queue.put(("error", str(exc)))

    def _run_analysis(self, input_path, output_path, mode, interest, density, padding):
        try:
            self.queue.put(("status", "Loading schematic..."))
            blocks = load_schematic(input_path)

            def progress_cb(stage, cur, total):
                total = max(int(total), 1)
                cur = max(0, min(int(cur), total))
                pct = (cur / total) * 100.0
                msg = f"{_progress_stage_label(stage)}: {cur:,}/{total:,}"
                self.queue.put(("progress", pct, msg, stage, cur, total))

            self.queue.put(("status", f"Loaded {len(blocks):,} blocks. Analyzing..."))
            md = generate_markdown(
                input_path,
                blocks,
                analysis_mode=("targeted" if mode == "targeted" else "full"),
                interest_threshold=interest,
                density_threshold=density,
                chunk_padding=padding,
                progress_cb=progress_cb,
                cancel_cb=self.cancel_event.is_set,
            )

            with open(output_path, "w", encoding="utf-8") as f:
                f.write(md)

            self.queue.put(("done", output_path))
        except AnalysisCancelled:
            self.queue.put(("cancelled", "Analysis cancelled"))
        except Exception as exc:
            self.queue.put(("error", str(exc)))

    def _eta_text(self, stage: str, cur: int, total: int) -> str:
        if not self.start_time or total <= 0 or cur <= 0:
            return ""
        now = time.time()
        elapsed = max(now - self.start_time, 0.001)
        if stage != self.last_stage:
            self.last_stage = stage
            self.last_stage_pct = 0.0
            return ""
        stage_progress = cur / total
        if stage_progress <= 0.01 or stage_progress <= self.last_stage_pct:
            self.last_stage_pct = stage_progress
            return ""
        rate = stage_progress / elapsed
        if rate <= 0:
            return ""
        remaining = max((1.0 - stage_progress) / rate, 0.0)
        self.last_stage_pct = stage_progress
        if remaining < 1:
            return " ETA <1s"
        if remaining < 120:
            return f" ETA ~{int(remaining)}s"
        return f" ETA ~{int(remaining // 60)}m {int(remaining % 60)}s"

    def _poll_queue(self):
        try:
            while True:
                item = self.queue.get_nowait()
                kind = item[0]
                if kind == "status":
                    self.status_var.set(item[1])
                elif kind == "progress":
                    _, pct, msg, stage, cur, total = item
                    self.progress_var.set(pct)
                    self.status_var.set(msg + self._eta_text(stage, cur, total))
                elif kind == "preview_done":
                    self.progress_var.set(100)
                    self._set_preview_text(item[1])
                    self.status_var.set("Preview complete")
                    self._set_running(False)
                elif kind == "done":
                    out = item[1]
                    self.progress_var.set(100)
                    self.status_var.set(f"Done. Wrote {out}")
                    self._set_running(False)
                    if messagebox:
                        messagebox.showinfo("Analysis complete", f"Markdown written to:\n{out}")
                elif kind == "cancelled":
                    self.status_var.set(item[1])
                    self._set_running(False)
                elif kind == "error":
                    self.status_var.set(f"Error: {item[1]}")
                    self._set_running(False)
                    if messagebox:
                        messagebox.showerror("Analysis failed", item[1])
        except queue.Empty:
            pass
        finally:
            self.root.after(100, self._poll_queue)

    def run(self):
        self.root.mainloop()


def main():
    args = sys.argv[1:]
    if args and args[0] in ("-h", "--help"):
        print(__doc__)
        sys.exit(0)

    if not args:
        if tk is not None and ttk is not None:
            app = SchematicAnalyzerGUI()
            app.run()
            return
        print("[!] GUI is unavailable in this environment. Use --nogui with a file path.")
        sys.exit(1)

    nogui = False
    if args and args[0] == "--nogui":
        nogui = True
        args = args[1:]

    if not args:
        if nogui:
            print("[!] No input file provided.")
            print(__doc__)
            sys.exit(1)

    # Batch or single
    if len(args) == 1 and not args[0].endswith(".md"):
        process_file(args[0])
    elif len(args) == 2 and args[1].endswith(".md"):
        process_file(args[0], args[1])
    else:
        for path in args:
            if path.endswith((".schematic", ".schem", ".litematic", ".nbt")):
                try:
                    process_file(path)
                except Exception as e:
                    print(f"[!] Failed {path}: {e}")


if __name__ == "__main__":
    main()

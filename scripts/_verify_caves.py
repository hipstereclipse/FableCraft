"""Render-verify the RUNTIME Guild-cave carve (spiral + flat causeway + Chamber
arch). This geometry lives in `carveGuildCaves()` in main.js, NOT in any
.mcstructure, so `_verify_guild.py` can't show it. This script mirrors that JS
carve EXACTLY into a Vox and renders it so the bridge can be eyeballed and the
y-levels reasoned about. Keep this in lockstep with carveGuildCaves().
"""
import math
import random
import gen_structures as GS
import gen_screenshots as SS

# ---- mirror of carveGuildCaves anchors (base at origin; BY chosen so the abyss
#      floor stays >= 0 for the Vox) ----
BX, BY, BZ = 0, 40, 0
SX, SZ = BX + 27, BZ + 14
TX = BX + 26
CWALL = BZ + 29
CFY = BY - 21
DECK = CFY
BSTART = BZ + 16
CSTART, CEND = BZ + 17, BZ + 28
HALF = 10
CEIL = DECK + 7
FLOORB = max(BY - 36, -60)
ringCW = [(0, 1), (-1, 1), (-1, 0), (-1, -1), (0, -1), (1, -1), (1, 0), (1, 1)]

SX_V, SY_V, SZ_V = 40, BY + 4, 32
random.seed(7)


def build(mode):
    """mode 'path' = only the walkable build (skip the rock shell) so the span +
    helix are visible; mode 'full' = everything, to confirm the gulf is sealed."""
    v = GS.Vox(SX_V, SY_V, SZ_V)
    shell = (mode == "full")

    def setB(x, y, z, id):
        if 0 <= x < SX_V and 0 <= y < SY_V and 0 <= z < SZ_V:
            v.set(x, y, z, id)

    def air(x, y, z):
        pass  # Vox starts as air; carving is a no-op in this additive sim

    def stone():
        return "minecraft:mossy_stone_bricks" if random.random() < 0.22 else "minecraft:stone_bricks"

    # 1. shaft pillar + walls
    for y in range(BY + 2, DECK - 2, -1):
        for ox in range(-2, 3):
            for oz in range(-2, 3):
                cheb = max(abs(ox), abs(oz))
                if ox == 0 and oz == 0:
                    setB(SX, y, SZ, "minecraft:chiseled_stone_bricks")
                elif cheb == 2:
                    if oz == 2 and y >= BY:
                        pass
                    elif shell:
                        setB(SX + ox, y, SZ + oz, stone())
    # 2. helix treads + newels
    n = 0
    while True:
        dx, dz = ringCW[n % 8]
        ty = BY - 1 - n
        if ty < DECK:
            break
        setB(SX + dx, ty, SZ + dz, stone())
        setB(SX + dx, ty - 1, SZ + dz, stone())
        if n % 3 == 0:
            setB(SX, ty + 1, SZ, "minecraft:glowstone")
        n += 1
    # spiral-foot landing
    for ox in range(-1, 2):
        for oz in range(-1, 2):
            setB(SX + ox, DECK, SZ + oz, stone())
            setB(SX + ox, DECK - 1, SZ + oz, stone())
    # 3. causeway
    for z in range(BSTART, CWALL):
        if CSTART <= z <= CEND:
            if shell:
                for ox in range(-HALF, HALF + 1):
                    setB(TX + ox, CEIL, z, stone())
                for yy in range(FLOORB, CEIL + 1):
                    setB(TX - HALF - 1, yy, z, stone())
                    setB(TX + HALF + 1, yy, z, stone())
        else:
            if shell:
                for ox in range(-HALF - 1, HALF + 2):
                    if abs(ox) <= 2:
                        continue
                    for yy in range(FLOORB, CEIL + 1):
                        setB(TX + ox, yy, z, stone())
            for ox in range(-2, 3):
                for yy in range(DECK - 3, DECK):
                    setB(TX + ox, yy, z, stone())
        for ox in range(-2, 3):
            setB(TX + ox, DECK, z, stone())
        setB(TX - 2, DECK + 1, z, "minecraft:cobblestone_wall")
        setB(TX + 2, DECK + 1, z, "minecraft:cobblestone_wall")
        if (z - BSTART) % 4 == 1:
            setB(TX - 2, DECK + 2, z, "minecraft:soul_lantern")
            setB(TX + 2, DECK + 2, z, "minecraft:soul_lantern")
    # 4. arch
    for ox in range(-1, 2):
        setB(TX + ox, DECK, CWALL, stone())
    for oy in range(1, 6):
        setB(TX - 2, DECK + oy, CWALL, "minecraft:chiseled_stone_bricks")
        setB(TX + 2, DECK + oy, CWALL, "minecraft:chiseled_stone_bricks")
    for ox in range(-2, 3):
        setB(TX + ox, DECK + 5, CWALL, "minecraft:chiseled_stone_bricks")
    setB(TX, DECK + 4, CWALL, "minecraft:lantern")
    return v


path = build("path")
full = build("full")

SS.render_structure(path, size=(1300, 1000), yaw=math.pi + 0.6, pitch=0.5
                    ).convert("RGB").save("screenshots/structures/_caves_iso.png", quality=92)
# near-side view straight down the bridge to confirm the deck is DEAD LEVEL
SS.render_structure(path, size=(1300, 700), yaw=math.pi, pitch=0.12
                    ).convert("RGB").save("screenshots/structures/_caves_side.png", quality=92)
SS.render_structure(path, size=(1000, 1000), yaw=0.0, pitch=math.pi / 2 - 0.001
                    ).convert("RGB").save("screenshots/structures/_caves_top.png", quality=92)
SS.render_structure(full, size=(1300, 1000), yaw=math.pi + 0.6, pitch=0.5
                    ).convert("RGB").save("screenshots/structures/_caves_full.png", quality=92)

print("=== Guild-cave y-level report (jump-free check) ===")
print(f"Library alcove floor (feet):     {BY + 1}")
print(f"Spiral first tread (feet):       {BY}      (1 step down into the shaft)")
print(f"Spiral foot tread / landing:     deck={DECK}  feet={DECK + 1}")
print(f"Causeway deck:                   y={DECK}    feet={DECK + 1}  (FLAT, z {BSTART}->{CWALL - 1})")
print(f"Chamber threshold (arch floor):  y={DECK}    feet={DECK + 1}")
print(f"Chamber corridor floor:          y={CFY}    feet={CFY + 1}")
print(f"  -> deck feet ({DECK + 1}) == chamber feet ({CFY + 1}): {'LEVEL, jump-free' if DECK == CFY else 'MISMATCH!'}")
print(f"Gulf: ceiling y={CEIL}, abyss floor y={FLOORB}  (drop below deck = {DECK - FLOORB} blocks)")
print(f"Span length (flat): {CWALL - BSTART} blocks; gulf width: {2 * HALF + 1} blocks")
print("rendered _caves_iso / _caves_side / _caves_top / _caves_full")

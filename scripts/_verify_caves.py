"""Render- AND walk-verify the RUNTIME Guild-cave carve (HALF-BLOCK spiral +
flat causeway + Chamber arch). This geometry lives in `carveGuildCaves()` in
main.js, NOT in any .mcstructure, so `_verify_guild.py` can't show it. This
script mirrors that JS carve EXACTLY, then (a) walks the whole path through a
small player-physics model to PROVE it is jump-free up *and* down, and (b)
renders it so the helix can be eyeballed. Keep in lockstep with carveGuildCaves().

Player physics (Bedrock): auto-step height ~0.5625, so a rise of <=0.5 per step
is climbed without jumping; any rise >0.5 needs a jump (a FAIL for a smooth
stair). A standing Hero is ~1.8 tall, so we want >=2 clear blocks of headroom
above each tread. Slab treads top out at +0.5 of their cell, full courses at +1.
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

SX_V, SY_V, SZ_V = 40, BY + 6, 32
random.seed(7)


def descent_treads():
    """The HALF-BLOCK helix exactly as carveGuildCaves builds it. Returns a list
    of (x, y_block, z, is_slab, surface_top) in descent order."""
    treads = []
    for n in range(0, 4000):
        dx, dz = ringCW[n % 8]
        block_y = (BY - n // 2) if n % 2 == 0 else (BY - (n + 1) // 2)
        if block_y < DECK or (block_y == DECK and n % 2 == 0):
            break
        is_slab = (n % 2 == 0)
        surface = block_y + (0.5 if is_slab else 1.0)
        treads.append((SX + dx, block_y, SZ + dz, is_slab, surface))
    return treads


def build(mode):
    """mode 'path' = only the walkable build (skip the rock shell) so the span +
    helix are visible; mode 'full' = everything, to confirm the gulf is sealed.
    Slab treads are drawn as full blocks here (over-states the obstruction, so a
    headroom check that passes on this Vox passes for the real slabs too)."""
    v = GS.Vox(SX_V, SY_V, SZ_V)
    shell = (mode == "full")

    def setB(x, y, z, id):
        if 0 <= x < SX_V and 0 <= y < SY_V and 0 <= z < SZ_V:
            v.set(x, y, z, id)

    def stone():
        return "minecraft:mossy_stone_bricks" if random.random() < 0.22 else "minecraft:stone_bricks"

    # 1. shaft pillar + walls (hollow interior)
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
    # 2. HALF-BLOCK helix treads + glowing newels
    for n, (tx, by, tz, is_slab, _surf) in enumerate(descent_treads()):
        setB(tx, by, tz, "minecraft:stone_brick_slab" if is_slab else stone())
        if n % 4 == 0:
            setB(SX, by + 1, SZ, "minecraft:glowstone")
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


def walk_report(vox):
    """Walk the whole route and check (a) every rise is <=0.5 (jump-free) and
    (b) >=2 blocks of clear headroom above each foothold. Returns (ok, lines)."""
    treads = descent_treads()
    AIR = vox._pid("minecraft:air")

    def is_air(x, y, z):
        if not (0 <= x < SX_V and 0 <= y < SY_V and 0 <= z < SZ_V):
            return True
        return vox.grid[vox.idx(x, y, z)] == AIR

    # ordered footholds: (x, z, surface_top, label). The spiral ends on a full
    # course at deck level, abutting the causeway, so the route flows straight on.
    route = [(SX, SZ + 2, float(BY + 1), "alcove floor (entry)")]
    for i, (tx, by, tz, is_slab, surf) in enumerate(treads):
        route.append((tx, tz, surf, f"tread {i:>2} {'slab' if is_slab else 'full'} y={by}"))
    for z in range(BSTART, CWALL):
        route.append((TX, z, float(DECK + 1), f"causeway z={z}"))
    route.append((TX, CWALL, float(DECK + 1), "chamber threshold (arch)"))

    lines, ok = [], True
    worst_step = 0.0
    prev = None
    for (x, z, surf, label) in route:
        if prev is not None:
            step = abs(surf - prev[2])     # magnitude of the up/down between footholds
            if step > 0.5 + 1e-6:          # >0.5 = a jump one way / a hard drop the other
                ok = False
                lines.append(f"  NOT SMOOTH  {step:.1f}  between {prev[3]} -> {label}")
            worst_step = max(worst_step, step)
        # headroom: a standing Hero (~1.8 tall) occupies the two cells strictly
        # above the foot surface (the foothold cell itself holds the tread/slab).
        head_lo = int(math.ceil(surf - 1e-6))
        head_ok = is_air(x, head_lo, z) and is_air(x, head_lo + 1, z)
        if not head_ok:
            ok = False
            lines.append(f"  LOW HEADROOM at {label}  (cells y={head_lo},{head_lo + 1} blocked)")
        prev = (x, z, surf, label)
    summary = [
        f"route footholds:            {len(route)}",
        f"spiral half-steps:          {len(treads)}  ({len(treads) / 8:.2f} revolutions)",
        f"entry surface:              {BY + 1}",
        f"chamber/causeway surface:   {DECK + 1}",
        f"total drop on the spiral:   {BY + 1 - (DECK + 1)} blocks over {len(treads)} steps "
        f"= {(BY + 1 - (DECK + 1)) / len(treads):.2f} block/step",
        f"worst step (up OR down):    {worst_step:.1f} block  "
        f"({'OK <=0.5 — smooth & jump-free both ways' if worst_step <= 0.5 + 1e-6 else 'FAIL >0.5'})",
    ]
    return ok, summary + (["", "ISSUES:"] + lines if lines else ["", "no jump points, no low headroom — fully walkable"])


path = build("path")
full = build("full")

ok, report = walk_report(path)
print("=== Guild-cave WALKABILITY report (half-block spiral) ===")
for ln in report:
    print(ln)
print("=== RESULT:", "PASS — jump-free both ways" if ok else "FAIL — see issues above", "===")

SS.render_structure(path, size=(1300, 1000), yaw=math.pi + 0.6, pitch=0.5
                    ).convert("RGB").save("screenshots/structures/_caves_iso.png", quality=92)
SS.render_structure(path, size=(1300, 700), yaw=math.pi, pitch=0.12
                    ).convert("RGB").save("screenshots/structures/_caves_side.png", quality=92)
SS.render_structure(path, size=(1000, 1000), yaw=0.0, pitch=math.pi / 2 - 0.001
                    ).convert("RGB").save("screenshots/structures/_caves_top.png", quality=92)
SS.render_structure(full, size=(1300, 1000), yaw=math.pi + 0.6, pitch=0.5
                    ).convert("RGB").save("screenshots/structures/_caves_full.png", quality=92)
print("rendered _caves_iso / _caves_side / _caves_top / _caves_full")

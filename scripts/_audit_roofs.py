"""Floating-roof audit for the Heroes' Guild.

Captures the guild_hall Vox, then:
  1. FLOOD-FILL SUPPORT TEST: every solid block must connect (26-connectivity,
     through solid blocks) down to a grounded block (y<=1). Any solid component
     that never touches the ground is FLOATING. Reports floating blocks grouped
     into connected clusters with their bounding boxes.
  2. ROOF-EAVE OVERHANG TEST: for the flat roof DECKS (deepslate_tiles/sandstone
     at the common eaves y>=5), flag deck cells whose cell directly below is air
     AND which sit on the EDGE of the deck (a neighbour is not roof) AND have no
     wall within 1 cell beneath the edge -> the eave overhangs open air.
Run from REPO ROOT:  python scripts/_audit_roofs.py
"""
import collections
import gen_structures as GS

captured = {}
orig = GS.Vox.save
try:
    GS.Vox.save = lambda self, name: captured.__setitem__(name, self)
    GS.guild_hall()
finally:
    GS.Vox.save = orig
vox = captured["guild_hall"]
SX, SY, SZ = vox.sx, vox.sy, vox.sz

AIR = vox._pid("minecraft:air")
WATER = vox._pid("minecraft:water")
# decor that hangs off blocks but is not structural -- treat as "not solid support"
NONSOLID_NAMES = {
    "minecraft:air", "minecraft:water", "minecraft:lantern", "minecraft:soul_lantern",
    "minecraft:torch", "minecraft:soul_torch", "minecraft:redstone_torch",
    "minecraft:vine", "minecraft:glass_pane", "minecraft:end_rod",
}
NONSOLID = {vox._pid(n) for n in NONSOLID_NAMES if (n, ()) in vox.pal_idx} | {AIR, WATER}


def name(x, y, z):
    return vox.palette[vox.grid[vox.idx(x, y, z)]][0]


def solid(x, y, z):
    if not (0 <= x < SX and 0 <= y < SY and 0 <= z < SZ):
        return False
    return vox.grid[vox.idx(x, y, z)] not in NONSOLID


# ---- 1. FLOOD-FILL SUPPORT ----
supported = bytearray(SX * SY * SZ)
dq = collections.deque()
for x in range(SX):
    for z in range(SZ):
        for y in (0, 1):
            if solid(x, y, z):
                i = vox.idx(x, y, z)
                if not supported[i]:
                    supported[i] = 1
                    dq.append((x, y, z))
# 26-connectivity: stair-stepped roof courses touch only along edges/corners, which
# reads as visually attached in Minecraft. Only blocks touching NOTHING (not even a
# corner) down to the ground are genuinely floating.
NB = tuple((dx, dy, dz) for dx in (-1, 0, 1) for dy in (-1, 0, 1) for dz in (-1, 0, 1)
           if (dx, dy, dz) != (0, 0, 0))
while dq:
    x, y, z = dq.popleft()
    for dx, dy, dz in NB:
        nx, ny, nz = x + dx, y + dy, z + dz
        if solid(nx, ny, nz):
            j = vox.idx(nx, ny, nz)
            if not supported[j]:
                supported[j] = 1
                dq.append((nx, ny, nz))

floating = []
for x in range(SX):
    for y in range(SY):
        for z in range(SZ):
            if solid(x, y, z) and not supported[vox.idx(x, y, z)]:
                floating.append((x, y, z))

# cluster the floating cells (6-connectivity) for a readable report
fset = set(floating)
seen = set()
clusters = []
for cell in floating:
    if cell in seen:
        continue
    comp = []
    stack = [cell]
    seen.add(cell)
    while stack:
        cx, cy, cz = stack.pop()
        comp.append((cx, cy, cz))
        for dx, dy, dz in NB:
            n = (cx + dx, cy + dy, cz + dz)
            if n in fset and n not in seen:
                seen.add(n)
                stack.append(n)
    clusters.append(comp)

clusters.sort(key=len, reverse=True)
print(f"=== FLOATING (ground-disconnected) blocks: {len(floating)} in {len(clusters)} clusters ===")
for comp in clusters[:40]:
    xs = [c[0] for c in comp]; ys = [c[1] for c in comp]; zs = [c[2] for c in comp]
    mats = collections.Counter(name(*c) for c in comp)
    top = ", ".join(f"{m.split(':')[1]}x{n}" for m, n in mats.most_common(3))
    print(f"  {len(comp):4d} cells  x[{min(xs)}..{max(xs)}] y[{min(ys)}..{max(ys)}] "
          f"z[{min(zs)}..{max(zs)}]  {top}")
if len(clusters) > 40:
    print(f"  ... and {len(clusters) - 40} more small clusters")


# ---- 2. ROOF EAVE OVERHANG ----
ROOF_NAMES = {"minecraft:deepslate_tiles", "minecraft:sandstone"}
ROOF = {vox._pid(n) for n in ROOF_NAMES}


def is_roof(x, y, z):
    return 0 <= x < SX and 0 <= y < SY and 0 <= z < SZ and vox.grid[vox.idx(x, y, z)] in ROOF


# top roof height per column
overhang = []
for x in range(SX):
    for z in range(SZ):
        for y in range(5, SY):
            if not is_roof(x, y, z):
                continue
            if solid(x, y - 1, z):
                continue  # something directly under the roof cell -> supported here
            # roof cell with air directly below: is it an EDGE cell whose outward
            # neighbour has no wall below it within the eave band?
            for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nx, nz = x + dx, z + dz
                # neighbour is not part of any roof/structure at-or-below this y, AND
                # there's no wall just below the edge -> the eave juts into open air
                edge = not any(solid(nx, yy, nz) for yy in range(1, y + 1))
                if edge:
                    overhang.append((x, y, z))
                    break

oset = set(overhang)
seen = set()
oclusters = []
for cell in overhang:
    if cell in seen:
        continue
    comp = []
    stack = [cell]
    seen.add(cell)
    while stack:
        cx, cy, cz = stack.pop()
        comp.append((cx, cy, cz))
        for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)):
            n = (cx + dx, cy, cz + dz)
            if n in oset and n not in seen:
                seen.add(n)
                stack.append(n)
    oclusters.append(comp)
oclusters.sort(key=len, reverse=True)
print(f"\n=== ROOF EAVE cells overhanging open air (no wall under the edge): {len(overhang)} "
      f"in {len(oclusters)} clusters ===")
for comp in oclusters[:40]:
    xs = [c[0] for c in comp]; ys = [c[1] for c in comp]; zs = [c[2] for c in comp]
    print(f"  {len(comp):4d} cells  x[{min(xs)}..{max(xs)}] y[{min(ys)}..{max(ys)}] z[{min(zs)}..{max(zs)}]")
if len(oclusters) > 40:
    print(f"  ... and {len(oclusters) - 40} more small clusters")

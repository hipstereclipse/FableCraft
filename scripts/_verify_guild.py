"""Scratch render-verify for the Heroes' Guild rebuild. Captures the guild_hall
Vox without writing the .mcstructure, then renders a top-down and an isometric
view so the layout (water sides, cloister, graves garden, bridge, paths) can be
eyeballed without launching Minecraft."""
import math
import gen_structures as GS
import gen_screenshots as SS

captured = {}
orig = GS.Vox.save
GS.Vox.save = lambda self, name: captured.__setitem__(name, self)
GS.guild_hall()
GS.Vox.save = orig
vox = captured["guild_hall"]

# top-down (look straight down, north up)
top = SS.render_structure(vox, size=(1100, 1100), yaw=0.0, pitch=math.pi / 2 - 0.001)
top.convert("RGB").save("screenshots/structures/_guild_topdown.png", quality=92)
# isometric beauty angle
iso = SS.render_structure(vox, size=(1300, 1000))
iso.convert("RGB").save("screenshots/structures/_guild_iso.png", quality=92)
# a second iso from the south-east to read the tower / corridor / bridge
iso2 = SS.render_structure(vox, size=(1300, 1000), yaw=math.pi + 0.7, pitch=0.55)
iso2.convert("RGB").save("screenshots/structures/_guild_iso_se.png", quality=92)


def crop(src, x0, x1, z0, z1):
    sub = GS.Vox(x1 - x0 + 1, src.sy, z1 - z0 + 1)
    for x in range(x0, x1 + 1):
        for y in range(src.sy):
            for z in range(z0, z1 + 1):
                pid = src.grid[src.idx(x, y, z)]
                name, states = src.palette[pid]
                sub.set(x - x0, y, z - z0, name, dict(states))
    return sub

# focused crop: Store / Four Graves garden / cloister / Maze's Tower / pond bridge
sub = crop(vox, 22, 70, 40, 92)
c_iso = SS.render_structure(sub, size=(1300, 1000), yaw=math.pi - 0.55, pitch=0.62)
c_iso.convert("RGB").save("screenshots/structures/_guild_crop_iso.png", quality=92)
c_top = SS.render_structure(sub, size=(1100, 1100), yaw=0.0, pitch=math.pi / 2 - 0.001)
c_top.convert("RGB").save("screenshots/structures/_guild_crop_top.png", quality=92)
# crop WITHOUT the roofs so the cloister arcade + graves read clearly (clip y<=6)
sub_noroof = GS.Vox(sub.sx, 7, sub.sz)
for x in range(sub.sx):
    for y in range(7):
        for z in range(sub.sz):
            n, s = sub.palette[sub.grid[sub.idx(x, y, z)]]
            sub_noroof.set(x, y, z, n, dict(s))
nr = SS.render_structure(sub_noroof, size=(1300, 1000), yaw=math.pi - 0.55, pitch=0.62)
nr.convert("RGB").save("screenshots/structures/_guild_crop_noroof.png", quality=92)
nrt = SS.render_structure(sub_noroof, size=(1100, 1100), yaw=0.0, pitch=math.pi / 2 - 0.001)
nrt.convert("RGB").save("screenshots/structures/_guild_crop_noroof_top.png", quality=92)

# GROUND-ONLY top-down (just the y=0..2 surface) so the gravel/dirt path network
# reads unambiguously against the lawn — no roofs, no walls hiding the paths.
ground = GS.Vox(vox.sx, 3, vox.sz)
for x in range(vox.sx):
    for y in range(3):
        for z in range(vox.sz):
            n, s = vox.palette[vox.grid[vox.idx(x, y, z)]]
            ground.set(x, y, z, n, dict(s))
gt = SS.render_structure(ground, size=(1100, 1100), yaw=0.0, pitch=math.pi / 2 - 0.001)
gt.convert("RGB").save("screenshots/structures/_guild_ground_top.png", quality=92)


def bridge_surface(x, z):
    """Approximate walk surface for bridge audits; ignores rails and lights."""
    ignored = {
        "minecraft:air", "minecraft:water", "minecraft:spruce_fence",
        "minecraft:dark_oak_fence", "minecraft:stone_brick_wall",
        "minecraft:lantern", "minecraft:soul_lantern",
    }
    surf = None
    for y in range(0, min(5, vox.sy)):
        name, _ = vox.palette[vox.grid[vox.idx(x, y, z)]]
        if name in ignored:
            continue
        if name.endswith("_slab"):
            surf = y + 0.5
        else:
            surf = y + 1.0
    return surf


def block_name(x, y, z):
    if not (0 <= x < vox.sx and 0 <= y < vox.sy and 0 <= z < vox.sz):
        return "minecraft:air"
    return vox.palette[vox.grid[vox.idx(x, y, z)]][0]


def any_surface(x, z, y0=0, y1=None):
    ignored = {
        "minecraft:air", "minecraft:water", "minecraft:spruce_fence",
        "minecraft:dark_oak_fence", "minecraft:stone_brick_wall",
        "minecraft:lantern", "minecraft:soul_lantern", "minecraft:torch",
    }
    y1 = min(vox.sy - 1, y1 if y1 is not None else vox.sy - 1)
    surf = None
    for y in range(max(0, y0), y1 + 1):
        name = block_name(x, y, z)
        if name in ignored:
            continue
        surf = y + (0.5 if name.endswith("_slab") else 1.0)
    return surf


def audit_bridge(label, route, max_step=1.0):
    vals = [(x, z, bridge_surface(x, z)) for x, z in route]
    bad = [p for p in vals if p[2] is None]
    steps = [abs(vals[i + 1][2] - vals[i][2]) for i in range(len(vals) - 1)
             if vals[i][2] is not None and vals[i + 1][2] is not None]
    worst = max(steps) if steps else 0.0
    status = "OK" if not bad and worst <= max_step else "CHECK"
    print(f"bridge audit {label}: {status}, worst step {worst:.1f}, missing {len(bad)}")


def audit_endpoint_contact(label, center):
    """Catch bridges whose path is walkable but stops in water visually."""
    cx, cz = center
    footprint = {(cx, cz), (cx, cz + 1), (cx - 1, cz), (cx - 1, cz + 1)}
    bridge_levels = [bridge_surface(x, z) for x, z in footprint
                     if 0 <= x < vox.sx and 0 <= z < vox.sz]
    water = vox._pid("minecraft:water")
    air = vox._pid("minecraft:air")
    dry_under = 0
    dry_adjacent = 0
    for x, z in footprint:
        if not (0 <= x < vox.sx and 0 <= z < vox.sz):
            continue
        ground = vox.grid[vox.idx(x, 0, z)]
        if ground not in (air, water):
            dry_under += 1
        for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            ax, az = x + dx, z + dz
            if (ax, az) in footprint or not (0 <= ax < vox.sx and 0 <= az < vox.sz):
                continue
            ground = vox.grid[vox.idx(ax, 0, az)]
            surf = bridge_surface(ax, az)
            if ground not in (air, water) and surf is not None:
                if dry_under or any(abs(surf - b) <= 0.5 for b in bridge_levels if b is not None):
                    dry_adjacent += 1
    status = "OK" if dry_under or dry_adjacent else "CHECK"
    print(f"bridge endpoint {label}: {status}, dry under {dry_under}, dry adjacent {dry_adjacent}")


def audit_island_channel(route):
    water = vox._pid("minecraft:water")
    air = vox._pid("minecraft:air")
    dry = 0
    wet = 0
    for cx, cz in route[3:-3]:
        for x, z in ((cx, cz), (cx, cz + 1), (cx - 1, cz), (cx - 1, cz + 1)):
            if not (0 <= x < vox.sx and 0 <= z < vox.sz):
                continue
            ground = vox.grid[vox.idx(x, 0, z)]
            if ground == water:
                wet += 1
            elif ground != air:
                dry += 1
    status = "OK" if wet > 0 and dry == 0 else "CHECK"
    print(f"island bridge channel: {status}, water under span {wet}, dry under span {dry}")


def audit_tower_stairs():
    cx, cz, radius = GS.GUILD_LAYOUT["maze_tower"]
    study_y = GS.GUILD_LAYOUT["maze_study_y"]
    spr_r = 4
    route = []
    for i in range((study_y - 1) * 2):
        y = 1 + i // 2
        if y >= study_y:
            break
        ang = math.radians(25 + i * (360 / 16))
        route.append((cx + round(math.cos(ang) * spr_r), y,
                      cz + round(math.sin(ang) * spr_r)))
    missing = []
    blocked = []
    steps = []
    prev = None
    for x, y, z in route:
        surf = any_surface(x, z, y, y)
        if surf is None:
            missing.append((x, y, z))
        for hy in range(y + 1, min(vox.sy, y + 4)):
            if block_name(x, hy, z) not in ("minecraft:air", "minecraft:lantern"):
                blocked.append((x, hy, z, block_name(x, hy, z)))
                break
        if prev and surf is not None and prev[3] is not None:
            steps.append(abs(surf - prev[3]))
        prev = (x, y, z, surf)
    worst = max(steps) if steps else 0
    status = "OK" if not missing and not blocked and worst <= 1.0 else "CHECK"
    print(f"tower stair audit: {status}, worst step {worst:.1f}, missing {len(missing)}, blocked {len(blocked)}")


def audit_tower_entrances():
    cx, cz, radius = GS.GUILD_LAYOUT["maze_tower"]
    openings = {
        "west": [(x, z) for x in range(cx - radius, cx - 1) for z in range(cz - 1, cz + 2)],
        "north": [(x, z) for x in range(cx - 1, cx + 2) for z in range(cz - radius, cz - 1)],
    }
    for label, cells in openings.items():
        blocked = [(x, z) for x, z in cells
                   if any(block_name(x, y, z) != "minecraft:air" for y in range(1, 4))]
        status = "OK" if not blocked else "CHECK"
        print(f"tower entrance {label}: {status}, blocked {len(blocked)}")


def audit_ground_holes():
    air = vox._pid("minecraft:air")
    holes = 0
    for x in range(vox.sx):
        for z in range(vox.sz):
            if 26 <= x <= 28 and 13 <= z <= 15:
                continue
            if vox.grid[vox.idx(x, 0, z)] == air:
                holes += 1
    print(f"ground hole audit: {'OK' if holes == 0 else 'CHECK'}, holes {holes}")


for zc in GS.GUILD_LAYOUT["river_bridges"]:
    audit_bridge(f"river z{zc}", [(x, zc) for x in range(48, 59)])

pb0, pb1 = GS.GUILD_LAYOUT["pond_bridge"]
steps = max(abs(pb1[0] - pb0[0]), abs(pb1[1] - pb0[1]), 1)
island_route = []
for i in range(steps + 1):
    x = round(pb0[0] + (pb1[0] - pb0[0]) * i / steps)
    z = round(pb0[1] + (pb1[1] - pb0[1]) * i / steps)
    if not island_route or island_route[-1] != (x, z):
        island_route.append((x, z))
audit_bridge("island", island_route, max_step=0.5)
audit_endpoint_contact("island start", pb0)
audit_endpoint_contact("island end", pb1)
audit_island_channel(island_route)
audit_tower_stairs()
audit_tower_entrances()
audit_ground_holes()
print("rendered topdown / iso / iso_se / crop_iso / crop_top / crop_noroof(+top) / ground_top")

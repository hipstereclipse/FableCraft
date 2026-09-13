"""Original reward-realm geometry, called through gen_structures' explicit owners.

Library Arcanum is a Minecraft adaptation of TLC's library grove. No reference
assets are embedded. Containers are EMPTY: the persistent runtime seeds them
once before admission. The invisible boundary is world-storage containment.
"""
import math
import random

LIBRARY_ARCANUM = {
    'size': (49, 28, 49), 'version': 1,
    'arrival': (24.5, 3, 7.5), 'return': (24.5, 3, 3.5),
    'containers': ((24, 3, 35), (16, 3, 28), (32, 3, 28), (16, 3, 34)),
}

# Integer x/z route points name block columns; runtime walks their +0.5 centres.
# These dimensions and the original root/forest composition are adaptations,
# not measurements recovered from the small 2005 guide image.
ARBORETUM = {
    'size': (49, 28, 49), 'version': 1,
    'arrival': (24.5, 3, 7.5), 'return': (24.5, 3, 3.5),
    'containers': ((34, 3, 35),),
    'routeWaypoints': ((24,12),(17,12),(13,19),(13,29),(19,35),
                       (28,35),(31,31),(37,24),(35,16),(29,12),(24,12)),
    'spine': ((24,2),(24,12)), 'chestApproach': (34.5,3,34.5),
    'chestPath': ((31,31),(34,34)),
    'returnDetectorCells': ((24,2,3),(24,7,3)),
    'returnDetectorBlocks': ('minecraft:chiseled_stone_bricks','minecraft:sea_lantern'),
}

GORGE_ARBORETUM_SOURCE = {
    'size': (39,16,43), 'center': (32.5,6,7.5), 'normal': (0,0,-1),
    'throatMin': (31,6,7), 'throatMax': (33,9,11),
    'approachMin': (31,6,6), 'approachMax': (33,9,12),
}


def arboretum_path_columns():
    """Three-wide dry loop/spine with corner overlap and a chest-front apron."""
    points = set()
    segments = list(zip(ARBORETUM['routeWaypoints'], ARBORETUM['routeWaypoints'][1:]))
    segments.append(ARBORETUM['spine'])
    segments.append(ARBORETUM['chestPath'])
    for (x0,z0),(x1,z1) in segments:
        steps = max(abs(x1-x0), abs(z1-z0), 1)*2
        for i in range(steps+1):
            x = round(x0+(x1-x0)*i/steps)
            z = round(z0+(z1-z0)*i/steps)
            points.update((x+dx,z+dz) for dx in (-1,0,1) for dz in (-1,0,1))
    # The chest is a discovery endpoint beside the lane, never part of its floor.
    points.discard((34,35))
    return points


def build_arboretum(vox_type):
    """A shaded rooted woodland with two dry arcs and one empty reward chest."""
    v = vox_type(*ARBORETUM['size'])
    r = random.Random('fablecraft.arboretum.v1')
    log, leaves = 'minecraft:dark_oak_log', 'minecraft:oak_leaves'
    air, moss = 'minecraft:air', 'minecraft:moss_block'
    route = arboretum_path_columns()
    # Independent original forest room, fully sealed in its allocated volume.
    v.box(0,0,0,48,27,48,'minecraft:barrier')
    v.fill(1,1,1,47,1,47,'minecraft:stone')
    v.fill(1,2,1,47,2,47,'minecraft:grass_block')
    for x in range(1,48):
        for z in range(1,48):
            if r.random() < .24:
                v.set(x,2,z,'minecraft:podzol' if r.random() < .6 else moss)
            edge = min(x,z,48-x,48-z)
            rim = 4.5 + math.sin(x*.43)*1.2 + math.cos(z*.39)
            if edge < rim and (x,z) not in route:
                height = min(7,3+int(rim-edge))
                v.fill(x,3,z,x,height,z,'minecraft:coarse_dirt')
                v.set(x,height,z,moss)
    # Broad irregular bases taper into substantial trunks, with high branches
    # and overlapping crowns. Root forms are original ambiguous low shapes;
    # the tiny guide image does not identify its curved foreground objects.
    trees = ((7,8,16,1),(40,9,18,1),(8,23,18,1),(41,26,20,1),
             (8,39,19,1),(25,42,21,1),(41,40,18,1),(23,22,21,2),(28,27,18,1))
    for tx,tz,h,radius in trees:
        for y in range(3,h+1):
            rad = radius if y < h-5 else max(0,radius-1)
            for dx in range(-rad,rad+1):
                for dz in range(-rad,rad+1):
                    if dx*dx+dz*dz <= rad*rad+1 and (tx+dx,tz+dz) not in route:
                        v.set(tx+dx,y,tz+dz,log,{'pillar_axis':'y'})
        for dx,dz in ((1,0),(-1,0),(0,1),(0,-1),(1,1),(-1,-1)):
            length = 4+r.randrange(3)
            for step in range(1,length+1):
                x,z = tx+dx*step,tz+dz*step
                if not (0<x<48 and 0<z<48) or (x,z) in route or (x,z)==(34,35):
                    continue
                top = 4 if step <= 2 else 3
                v.fill(x,3,z,x,top,z,log,{'pillar_axis':'x' if dx else 'z'})
                if step == length: v.set(x,top,z,moss)
            # High branching stays above all declared player lanes.
            if dx*dz == 0:
                for step in range(1,5):
                    x,z = tx+dx*step,tz+dz*step
                    if 0<x<48 and 0<z<48:
                        v.set(x,h-4+step//3,z,log,{'pillar_axis':'x' if dx else 'z'})
        for dx in range(-6,7):
            for dz in range(-6,7):
                for dy in range(-4,5):
                    x,y,z = tx+dx,h+dy,tz+dz
                    if 0<x<48 and 3<y<27 and 0<z<48 and dx*dx+dz*dz+dy*dy*2 < 37+r.randrange(7):
                        # Do not erase the trunk or branching inside the crown.
                        if v.palette[v.grid[v.idx(x,y,z)]][0] != log:
                            v.set(x,y,z,leaves,{'persistent_bit':True})
    # Earth paths curve around the planted mass; full-width clearance is final.
    # They never share the Library's pond, book bays, reading furniture or map.
    for x,z in sorted(route):
        v.set(x,2,z,'minecraft:coarse_dirt' if (x*7+z*11)%5 else 'minecraft:grass_block')
        v.fill(x,3,z,x,6,z,air)
    # A bent timber return frame, distinct from the stone library arch. Side
    # roots stand outside the three-wide throat, with its lamp overhead.
    for x in (21,27):
        v.fill(x,3,3,x,6,3,log,{'pillar_axis':'y'})
        v.set(x,3,4,moss)
    v.fill(22,7,3,26,7,3,log,{'pillar_axis':'x'})
    for p,name in zip(ARBORETUM['returnDetectorCells'],ARBORETUM['returnDetectorBlocks']):
        v.set(*p,name)
    # A single earth-and-root niche, empty until the durable room owner seeds it.
    # Keep the entire front apron and lid clear. No generator-owned inventory.
    v.set(34,2,35,'minecraft:podzol')
    v.set(34,3,35,'minecraft:chest',{'minecraft:cardinal_direction':'north'})
    v.fill(33,4,34,35,6,36,air)
    v.fill(33,3,34,35,3,34,air)
    # Low, warm lamps are tucked outside the dry route and reveal the niche.
    for x,z in ((19,9),(10,28),(31,39),(38,32)):
        if (x,z) not in route:
            v.set(x,3,z,'minecraft:mossy_cobblestone')
            v.set(x,4,z,'minecraft:lantern',{'hanging':False})
    v.save('arboretum')
    return v


def build_library_arcanum(vox_type):
    v = vox_type(*LIBRARY_ARCANUM['size'])
    r = random.Random('fablecraft.library_arcanum.v1')
    stone = 'minecraft:stone_bricks'
    moss = 'minecraft:mossy_stone_bricks'
    cobble = 'minecraft:mossy_cobblestone'
    wood = 'minecraft:dark_oak_planks'
    log = 'minecraft:dark_oak_log'
    leaves = 'minecraft:oak_leaves'
    air = 'minecraft:air'
    # A sealed invisible shell permits daylight without exposing the storage
    # plateau. It is intentionally distinct from visible grotto/cliff geometry.
    v.box(0, 0, 0, 48, 27, 48, 'minecraft:barrier')
    v.fill(1, 1, 1, 47, 1, 47, 'minecraft:stone')
    v.fill(1, 2, 1, 47, 2, 47, 'minecraft:grass_block')
    for x in range(1, 48):
        for z in range(1, 48):
            radius = math.hypot((x-24)/25, (z-24)/27)
            rim = .77 + .04*math.sin(x*.41) + .025*math.cos(z*.57)
            if radius > rim:
                # Rising, uneven crags wrap an irregular clearing. The earlier
                # square vertical wall read as a fortified courtyard in review.
                h = min(21, max(3, int((radius-rim)*33) + 3 + r.randrange(3)))
                for y in range(3, h + 1):
                    v.set(x, y, z, r.choice(('minecraft:stone', cobble, 'minecraft:cobblestone')))
                if h < 13:
                    v.set(x,h,z,'minecraft:moss_block')
            elif r.random() < .08:
                v.set(x, 2, z, 'minecraft:podzol')
    # Mature edge trees: bowed roots, irregular crowns, open central sky.
    for x, z, h in ((8,8,10),(39,9,12),(7,26,12),(40,26,11),(10,40,13),(37,40,12),(24,44,14)):
        v.fill(x, 3, z, x, h, z, log)
        for dx,dz in ((1,0),(-1,0),(0,1),(0,-1)):
            v.set(x+dx, 3, z+dz, log)
        for dx in range(-4,5):
            for dz in range(-4,5):
                for dy in range(-2,3):
                    if (dx*dx + dz*dz + dy*dy*3 <= 20 + r.randrange(5)
                            and 0 < x+dx < 48 and 0 < z+dz < 48):
                        v.set(x+dx,h+dy,z+dz,leaves,{'persistent_bit':True})
        v.fill(x, h-3, z, x+2, h-3, z, log)
    # Chalk-edged pond, retained by the solid y1 basin and its dry stone rim.
    for x in range(7,17):
        for z in range(13,23):
            d=((x-11.5)/4.5)**2+((z-17.5)/4.5)**2
            if d <= 1:
                v.set(x,2,z,'minecraft:water')
            elif d <= 1.6:
                v.set(x,2,z,'minecraft:calcite')
    # The 2005 guide's small gameplay view shows earthy, irregular ground rather
    # than a formal paved garden. Keep the same dry route footprint, softening
    # its visible edges with grass and broken earth patches. No item/portal
    # anchors move, so the persistent v1 destination contract stays compatible.
    def path(x0,z0,x1,z1):
        for x in range(x0-1,x1+2):
            for z in range(z0-1,z1+2):
                core = x0 <= x <= x1 and z0 <= z <= z1
                noise = (math.sin(x*.31+z*.27)+math.cos(z*.23-x*.19))/2
                if not core and noise < .5:
                    continue
                # Preserve the pond, rock boundary and previous furnishings.
                existing = v.palette[v.grid[v.idx(x,2,z)]][0]
                if existing not in ('minecraft:grass_block','minecraft:podzol','minecraft:coarse_dirt'):
                    continue
                v.set(x,2,z,'minecraft:coarse_dirt' if noise > -.3 else 'minecraft:grass_block')
    path(23,3,25,38)
    path(18,10,33,12); path(31,10,33,35); path(18,10,20,35)
    path(14,25,34,27); path(14,31,34,33); path(14,35,34,37)
    # Three open-air book bays arranged around a reading court; exposed beam
    # pergolas make a library within the grove rather than a generic box room.
    for x0,x1 in ((13,19),(21,27),(29,35)):
        v.fill(x0,2,38,x1,2,41,wood)
        for x in range(x0,x1+1):
            v.fill(x,3,40,x,7,40,'minecraft:bookshelf')
            v.set(x,8,40,wood)
        for x in (x0,x1):
            v.fill(x,3,38,x,8,38,log)
        v.fill(x0,8,38,x1,8,38,wood)
        for x in range(x0,x1+1,2):
            v.fill(x,9,38,x,9,41,'minecraft:spruce_slab',{'minecraft:vertical_half':'bottom'})
    # A table and two shelving islands supply separately discoverable pickups.
    for x,z in ((32,28),(16,34)):
        v.fill(x-1,2,z,x+1,2,z+1,wood)
        v.fill(x-1,3,z+1,x+1,5,z+1,'minecraft:bookshelf')
        v.set(x-1,3,z-1,'minecraft:dark_oak_stairs',{'weirdo_direction':2,'upside_down_bit':False})
        v.set(x+1,3,z-1,'minecraft:dark_oak_stairs',{'weirdo_direction':2,'upside_down_bit':False})
    # Making Friends rests in a low reading table, apart from the shelves.
    for x in (15,17):
        v.set(x,3,28,'minecraft:dark_oak_slab',{'minecraft:vertical_half':'top'})
    v.set(16,3,30,'minecraft:dark_oak_stairs',{'weirdo_direction':3,'upside_down_bit':False})
    # Quiet reading benches east of the pool, and lamps out of walking lanes.
    for x,z in ((28,17),(28,21),(21,21),(35,32)):
        v.set(x,3,z,'minecraft:dark_oak_stairs',{'weirdo_direction':1,'upside_down_bit':False})
    for x,z in ((21,8),(28,8),(21,29),(28,29),(12,35),(36,36)):
        v.fill(x,3,z,x,4,z,'minecraft:dark_oak_fence')
        v.set(x,5,z,'minecraft:lantern',{'hanging':False})
    # A low stone return arch, well in front of arrival. Its three-wide throat
    # is clear from BOTH sides; the y2 disc is a recognisable exit landmark.
    path(21,2,27,9)
    for x in (21,27):
        v.fill(x,3,3,x,7,3,moss)
        v.set(x,6,2,'minecraft:chiseled_stone_bricks')
    v.fill(21,7,3,27,7,3,stone)
    v.set(24,7,3,'minecraft:sea_lantern')
    v.fill(23,3,2,25,6,9,air)
    v.fill(23,2,2,25,2,9,stone)
    # Reward reliquary is at the end of the grove walk, distinct from the exit.
    v.fill(22,2,34,26,2,36,'minecraft:chiseled_stone_bricks')
    for x in (22,26):
        v.set(x,3,36,'minecraft:stone_brick_wall')
        v.set(x,4,36,'minecraft:lantern',{'hanging':False})
    for point in LIBRARY_ARCANUM['containers']:
        x,y,z=point
        if point == (16,3,28):
            v.set(x,y,z,'minecraft:barrel',{'facing_direction':1,'open_bit':False})
        else:
            v.set(x,y,z,'minecraft:chest',{'minecraft:cardinal_direction':'north'})
        v.set(x,y+1,z,air)
        v.set(x,y,z-1,air); v.set(x,y+1,z-1,air)
    # Flowers at edges and the pond: keep the routed interior unobstructed.
    for x,z in ((9,11),(15,11),(7,23),(14,23),(37,17),(38,33),(11,37),(35,11)):
        v.set(x,3,z,r.choice(('minecraft:poppy','minecraft:oxeye_daisy','minecraft:oxeye_daisy')))
    v.save('library_arcanum')
    return v

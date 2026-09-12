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

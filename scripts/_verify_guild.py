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
print("rendered topdown / iso / iso_se / crop_iso / crop_top / crop_noroof(+top) / ground_top")

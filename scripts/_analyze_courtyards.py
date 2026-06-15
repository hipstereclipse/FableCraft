"""Build the guild Vox and print an ASCII map of the western complex so I can
see exactly which cells are paved-but-UNROOFED courtyard (to enclose) vs already
roofed rooms vs walls vs open lawn. No Minecraft / no .mcstructure write."""
import gen_structures as GS

captured = {}
GS.Vox.save = lambda self, name: captured.__setitem__(name, self)
GS.guild_hall()
vox = captured["guild_hall"]
pid_air = vox._pid("minecraft:air")
pid_water = vox._pid("minecraft:water")


def solid(x, y, z):
    p = vox.grid[vox.idx(x, y, z)]
    return p != pid_air and p != pid_water


def classify(x, z):
    if not (0 <= x < vox.sx and 0 <= z < vox.sz):
        return " "
    p0 = vox.grid[vox.idx(x, 0, z)]
    if p0 == pid_water:
        return "~"
    floor = p0 != pid_air
    roof = any(solid(x, y, z) for y in range(5, 16))
    wall = solid(x, 1, z) and solid(x, 2, z)
    head_open = not solid(x, 1, z) and not solid(x, 2, z)
    if wall:
        return "W"            # wall / pier / decor column
    if roof and head_open:
        return "#"            # roofed room (walkable under a roof) — good
    if roof:
        return "+"            # roofed but something at head height
    if floor and head_open:
        return "O"            # PAVED OPEN COURTYARD (candidate to roof)
    return "."               # bare/odd


X0, X1, Z0, Z1 = 8, 50, 12, 62
print("    " + "".join(str((x // 10) % 10) for x in range(X0, X1 + 1)))
print("    " + "".join(str(x % 10) for x in range(X0, X1 + 1)))
for z in range(Z0, Z1 + 1):
    print(f"{z:3d} " + "".join(classify(x, z) for x in range(X0, X1 + 1)))
print("\nlegend: #=roofed room  O=open paved courtyard  W=wall/pier  ~=water  .=bare  +=roofed/obstructed")
# also a count of O cells by rough region
opens = [(x, z) for z in range(Z0, Z1 + 1) for x in range(X0, X1 + 1) if classify(x, z) == "O"]
print(f"open courtyard cells: {len(opens)}")

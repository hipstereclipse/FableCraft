"""fc_mobs.py — every creature in Fablecraft: Reforged.

Defines body-plan builders (parts -> cubes) plus the full mob roster with
gameplay stats. The same cube data drives:
  * RP geometry JSON (auto-packed box UVs)
  * procedural entity textures (painted per cube face)
  * the offline screenshot renderer

Cube convention: Bedrock model space, feet at y=0, front faces -z.
A part: {"name", "pivot": [x,y,z], "rot": [rx,ry,rz] (rest pose),
         "cubes": [{"origin","size","inflate"?}], "role": material role,
         "decor": [face decorations], "mirror"?: bool}
"""
from fc_lib import title_case

# ---------------------------------------------------------------------------
# Body-plan builders
# ---------------------------------------------------------------------------


def _cube(origin, size, inflate=0.0):
    c = {"origin": list(origin), "size": list(size)}
    if inflate:
        c["inflate"] = inflate
    return c


def plan_humanoid(head=8, torso_w=8, torso_h=12, torso_d=4, arm_w=4, arm_len=12,
                  leg_h=12, leg_w=4, hunch=0.0, belly=0, hat=None, hair=False,
                  skirt=False, cape=False, pauldrons=False, horns=False,
                  boots=False, belt=False, helmet=False,
                  hands=False, roles=None, decor=None):
    roles = roles or {}
    decor = decor or {}
    hip = leg_h
    shoulder = hip + torso_h - 2
    top = hip + torso_h
    half_t = torso_w // 2
    parts = []

    def role(p, default):
        return roles.get(p, default)

    def dec(p):
        return decor.get(p, [])

    boot_h = max(3, leg_h // 3)
    r_leg = [_cube([-(leg_w + 1), 0, -leg_w / 2], [leg_w, leg_h, leg_w])]
    l_leg = [_cube([1, 0, -leg_w / 2], [leg_w, leg_h, leg_w])]
    leg_roles = {}
    if boots:
        r_leg.append(_cube([-(leg_w + 1), 0, -leg_w / 2], [leg_w, boot_h, leg_w], inflate=0.35))
        l_leg.append(_cube([1, 0, -leg_w / 2], [leg_w, boot_h, leg_w], inflate=0.35))
        leg_roles = {1: "boots"}
    parts.append({
        "name": "leg_r", "pivot": [-(leg_w // 2 + 1), hip, 0], "rot": [0, 0, 0],
        "cubes": r_leg, "cube_roles": dict(leg_roles),
        "role": role("legs", "cloth"), "decor": dec("legs")})
    parts.append({
        "name": "leg_l", "pivot": [leg_w // 2 + 1, hip, 0], "rot": [0, 0, 0],
        "cubes": l_leg, "cube_roles": dict(leg_roles),
        "role": role("legs", "cloth"), "decor": dec("legs")})
    body_cubes = [_cube([-half_t, hip, -torso_d / 2], [torso_w, torso_h, torso_d])]
    body_roles = {}
    if belly:
        body_cubes.append(_cube([-half_t - 1, hip + 1, -torso_d / 2 - belly],
                                [torso_w + 2, torso_h - 4, torso_d + belly], inflate=0.2))
    if skirt:
        body_cubes.append(_cube([-half_t - 1, hip - 5, -torso_d / 2 - 1],
                                [torso_w + 2, 6, torso_d + 2]))
    if belt:
        body_cubes.append(_cube([-half_t, hip + 1, -torso_d / 2], [torso_w, 2, torso_d], inflate=0.4))
        body_roles[len(body_cubes) - 1] = "belt"
    parts.append({
        "name": "body", "pivot": [0, hip, 0], "rot": [hunch, 0, 0],
        "cubes": body_cubes, "cube_roles": body_roles,
        "role": role("body", "cloth"), "decor": dec("body")})
    if cape:
        parts.append({
            "name": "cape", "pivot": [0, top - 1, torso_d / 2], "rot": [4, 0, 0],
            "cubes": [_cube([-half_t, hip - 6, torso_d / 2], [torso_w, torso_h + 4, 1])],
            "role": role("cape", "cloth"), "decor": dec("cape"), "parent": "body"})
    head_cubes = [_cube([-head / 2, top, -head / 2], [head, head, head])]
    cube_roles = {}
    decor_cube = 0
    if hair:
        style = "long" if hair == "long" else "short"
        # hairline cap wrapping the top of the skull (keeps eyes clear)
        head_cubes.append(_cube([-head / 2, top + (head * 5) // 8, -head / 2],
                                [head, head - (head * 5) // 8, head], inflate=0.35))
        cube_roles[len(head_cubes) - 1] = "hair"
        if style == "long":
            # hair fall down the back to the shoulders
            head_cubes.append(_cube([-head / 2, top - 4, head / 2 - 1],
                                    [head, head, 2], inflate=0.2))
            cube_roles[len(head_cubes) - 1] = "hair"
    if helmet:
        # rounded sallet: dome cap, flared rear neck-guard, nasal bar — face open
        head_cubes.append(_cube([-head / 2, top + (head * 5) // 8, -head / 2],
                                [head, head - (head * 5) // 8, head], inflate=0.55))
        cube_roles[len(head_cubes) - 1] = "metal"
        head_cubes.append(_cube([-head / 2, top + 1, head / 2 - 1],
                                [head, head // 2, 1], inflate=0.45))
        cube_roles[len(head_cubes) - 1] = "metal"
        head_cubes.append(_cube([-0.5, top + 2, -head / 2 - 0.6],
                                [1, (head * 3) // 8 + 1, 1]))
        cube_roles[len(head_cubes) - 1] = "metal"
    if horns:
        head_cubes.append(_cube([-head / 2 - 1, top + head - 2, -1], [2, 4, 2]))
        cube_roles[len(head_cubes) - 1] = "horn"
        head_cubes.append(_cube([head / 2 - 1, top + head - 2, -1], [2, 4, 2]))
        cube_roles[len(head_cubes) - 1] = "horn"
    if hat == "wizard":
        head_cubes.append(_cube([-head / 2 - 1, top + head, -head / 2 - 1], [head + 2, 1, head + 2]))
        cube_roles[len(head_cubes) - 1] = "cloth"
        head_cubes.append(_cube([-2, top + head + 1, -2], [4, 5, 4]))
        cube_roles[len(head_cubes) - 1] = "cloth"
    elif hat == "straw":
        head_cubes.append(_cube([-head / 2 - 2, top + head - 1, -head / 2 - 2],
                                [head + 4, 1, head + 4]))
        cube_roles[len(head_cubes) - 1] = "straw"
        head_cubes.append(_cube([-3, top + head, -3], [6, 2, 6]))
        cube_roles[len(head_cubes) - 1] = "straw"
    elif hat == "hood":
        head_cubes.append(_cube([-head / 2, top, -head / 2], [head, head, head], inflate=0.6))
        cube_roles[len(head_cubes) - 1] = "cloth"
        decor_cube = len(head_cubes) - 1  # face decor paints onto the hood shell
    parts.append({
        "name": "head", "pivot": [0, top, 0], "rot": [0, 0, 0],
        "cubes": head_cubes, "role": role("head", "skin"),
        "cube_roles": cube_roles, "decor_cube": decor_cube,
        "decor": dec("head") or ["face"]})
    arm_y = shoulder - arm_len + 2
    r_cubes = [_cube([-half_t - arm_w, arm_y, -arm_w / 2], [arm_w, arm_len, arm_w])]
    l_cubes = [_cube([half_t, arm_y, -arm_w / 2], [arm_w, arm_len, arm_w])]
    arm_roles = {}
    if pauldrons:
        r_cubes.append(_cube([-half_t - arm_w - 1, shoulder - 2, -arm_w / 2 - 1],
                             [arm_w + 2, 4, arm_w + 2]))
        l_cubes.append(_cube([half_t - 1, shoulder - 2, -arm_w / 2 - 1],
                             [arm_w + 2, 4, arm_w + 2]))
    if hands:
        r_cubes.append(_cube([-half_t - arm_w, arm_y - 2, -arm_w / 2], [arm_w, 3, arm_w], inflate=0.08))
        l_cubes.append(_cube([half_t, arm_y - 2, -arm_w / 2], [arm_w, 3, arm_w], inflate=0.08))
        arm_roles[len(r_cubes) - 1] = "skin"
    parts.append({
        "name": "arm_r", "pivot": [-half_t - 1, shoulder, 0], "rot": [0, 0, 0],
        "cubes": r_cubes, "cube_roles": dict(arm_roles),
        "role": role("arms", "cloth"), "decor": dec("arms")})
    parts.append({
        "name": "arm_l", "pivot": [half_t + 1, shoulder, 0], "rot": [0, 0, 0],
        "cubes": l_cubes, "cube_roles": dict(arm_roles),
        "role": role("arms", "cloth"), "decor": dec("arms")})
    return parts


def plan_balverine(frost=False, white=False, scale=1.0):
    decor_head = ["balverine_face"]
    parts = [
        {"name": "leg_r", "pivot": [-3, 14, 0], "rot": [-4, 0, 0],
         "cubes": [_cube([-5, 7, -2], [4, 8, 4]), _cube([-5, 0, -3], [4, 7, 4])],
         "role": "fur", "decor": []},
        {"name": "leg_l", "pivot": [3, 14, 0], "rot": [-4, 0, 0],
         "cubes": [_cube([1, 7, -2], [4, 8, 4]), _cube([1, 0, -3], [4, 7, 4])],
         "role": "fur", "decor": []},
        {"name": "body", "pivot": [0, 14, 0], "rot": [12, 0, 0],
         "cubes": [_cube([-5, 14, -3], [10, 12, 6]),
                   _cube([-4, 24, -4], [8, 5, 5])],
         "role": "fur", "decor": ["spine"]},
        {"name": "tail", "pivot": [0, 15, 3], "rot": [-30, 0, 0], "parent": "body",
         "cubes": [_cube([-1, 8, 3], [2, 8, 2])], "role": "fur", "decor": []},
        {"name": "head", "pivot": [0, 28, 0], "rot": [-8, 0, 0],
         "cubes": [_cube([-3.5, 28, -5], [7, 7, 7]),
                   _cube([-2, 28, -9], [4, 3, 4]),
                   _cube([-3.5, 35, -2], [2, 3, 1]),
                   _cube([1.5, 35, -2], [2, 3, 1])],
         "role": "fur", "decor": decor_head},
        {"name": "arm_r", "pivot": [-6, 26, 0], "rot": [26, 0, 6],
         "cubes": [_cube([-9, 12, -2], [4, 15, 4]),
                   _cube([-9, 8, -3], [4, 5, 4]),
                   _cube([-8.5, 4, -3.5], [3, 4, 3])],
         "role": "fur", "decor": ["claws"]},
        {"name": "arm_l", "pivot": [6, 26, 0], "rot": [26, 0, -6],
         "cubes": [_cube([5, 12, -2], [4, 15, 4]),
                   _cube([5, 8, -3], [4, 5, 4]),
                   _cube([5.5, 4, -3.5], [3, 4, 3])],
         "role": "fur", "decor": ["claws"]},
    ]
    return parts


def plan_hobbe():
    return plan_humanoid(head=9, torso_w=10, torso_h=9, torso_d=6, arm_w=3,
                         arm_len=10, leg_h=5, leg_w=4, belly=1, hunch=8,
                         roles={"head": "skin", "body": "cloth", "arms": "skin",
                                "legs": "skin"},
                         decor={"head": ["hobbe_face"], "body": ["stitches"]})


def plan_troll(icy=False, giant=False):
    s = 1.35 if giant else 1.0
    def S(v):
        return [round(x * s, 1) for x in v]
    return [
        {"name": "leg_r", "pivot": S([-5, 12, 0]), "rot": [0, 0, 0],
         "cubes": [_cube(S([-9, 0, -4]), S([7, 12, 8]))], "role": "rock", "decor": []},
        {"name": "leg_l", "pivot": S([5, 12, 0]), "rot": [0, 0, 0],
         "cubes": [_cube(S([2, 0, -4]), S([7, 12, 8]))], "role": "rock", "decor": []},
        {"name": "body", "pivot": S([0, 12, 0]), "rot": [10, 0, 0],
         "cubes": [_cube(S([-9, 12, -6]), S([18, 16, 12])),
                   _cube(S([-7, 26, -7]), S([14, 6, 6]))],
         "role": "rock", "decor": ["moss" if not icy else "ice_shards"]},
        {"name": "head", "pivot": S([0, 30, -4]), "rot": [0, 0, 0],
         "cubes": [_cube(S([-3.5, 28, -10]), S([7, 6, 6]))],
         "role": "rock", "decor": ["troll_face"]},
        {"name": "arm_r", "pivot": S([-10, 26, 0]), "rot": [-10, 0, 6],
         "cubes": [_cube(S([-16, 4, -4]), S([6, 24, 8])),
                   _cube(S([-17, 0, -5]), S([8, 6, 10]))],
         "role": "rock", "decor": ["cracks"]},
        {"name": "arm_l", "pivot": S([10, 26, 0]), "rot": [-10, 0, -6],
         "cubes": [_cube(S([10, 4, -4]), S([6, 24, 8])),
                   _cube(S([9, 0, -5]), S([8, 6, 10]))],
         "role": "rock", "decor": ["cracks"]},
    ]


def plan_wasp(queen=False):
    s = 1.8 if queen else 1.0
    def S(v):
        return [round(x * s, 1) for x in v]
    parts = [
        {"name": "body", "pivot": S([0, 6, 0]), "rot": [0, 0, 0],
         "cubes": [_cube(S([-3, 4, -4]), S([6, 5, 7]))], "role": "chitin",
         "decor": ["stripes"]},
        {"name": "abdomen", "pivot": S([0, 6, 3]), "rot": [22, 0, 0], "parent": "body",
         "cubes": [_cube(S([-3.5, 2, 3]), S([7, 6, 9])),
                   _cube(S([-1, 3.5, 12]), S([2, 2, 4]))],
         "role": "chitin", "decor": ["stripes", "stinger"]},
        {"name": "head", "pivot": S([0, 7, -4]), "rot": [0, 0, 0],
         "cubes": [_cube(S([-2.5, 4.5, -9]), S([5, 5, 5]))], "role": "chitin",
         "decor": ["bug_eyes", "mandibles"]},
        {"name": "wing_r", "pivot": S([-2, 9, -1]), "rot": [0, 0, -20],
         "cubes": [_cube(S([-12, 9, -2]), S([10, 0.5, 5]))], "role": "wing", "decor": []},
        {"name": "wing_l", "pivot": S([2, 9, -1]), "rot": [0, 0, 20],
         "cubes": [_cube(S([2, 9, -2]), S([10, 0.5, 5]))], "role": "wing", "decor": []},
        {"name": "legs", "pivot": S([0, 4, 0]), "rot": [0, 0, 0],
         "cubes": [_cube(S([-3.5, 1, -3]), S([1, 4, 1])),
                   _cube(S([2.5, 1, -3]), S([1, 4, 1])),
                   _cube(S([-3.5, 1, 0]), S([1, 4, 1])),
                   _cube(S([2.5, 1, 0]), S([1, 4, 1]))],
         "role": "chitin", "decor": []},
    ]
    return parts


def plan_beetle():
    return [
        {"name": "body", "pivot": [0, 3, 0], "rot": [0, 0, 0],
         "cubes": [_cube([-4, 1, -5], [8, 4, 10]),
                   _cube([-3.5, 4.5, -4], [7, 2, 8])],
         "role": "chitin", "decor": ["shell_split"]},
        {"name": "head", "pivot": [0, 3, -5], "rot": [0, 0, 0],
         "cubes": [_cube([-2.5, 1, -8], [5, 3, 3]),
                   _cube([-2, 3.5, -8.5], [1, 3, 1]),
                   _cube([1, 3.5, -8.5], [1, 3, 1])],
         "role": "chitin", "decor": ["bug_eyes"]},
        {"name": "legs", "pivot": [0, 2, 0], "rot": [0, 0, 0],
         "cubes": [_cube([-5, 0, -4], [1, 2, 1]), _cube([4, 0, -4], [1, 2, 1]),
                   _cube([-5, 0, -1], [1, 2, 1]), _cube([4, 0, -1], [1, 2, 1]),
                   _cube([-5, 0, 2], [1, 2, 1]), _cube([4, 0, 2], [1, 2, 1])],
         "role": "chitin", "decor": []},
    ]


def plan_wraith():
    return [
        {"name": "body", "pivot": [0, 14, 0], "rot": [0, 0, 0],
         "cubes": [_cube([-5, 8, -3], [10, 12, 6]),
                   _cube([-4, 2, -2], [8, 6, 4]),
                   _cube([-2.5, -2, -1.5], [5, 4, 3])],
         "role": "ghost", "decor": ["tatters"]},
        {"name": "head", "pivot": [0, 20, 0], "rot": [6, 0, 0],
         "cubes": [_cube([-3.5, 20, -3.5], [7, 7, 7], inflate=0.4),
                   _cube([-3.5, 19, -3.5], [7, 9, 7], inflate=0.9)],
         "cube_roles": {1: "ghost"}, "decor_cube": 1,
         "role": "ghost", "decor": ["hood_face"]},
        {"name": "arm_r", "pivot": [-5, 18, 0], "rot": [-40, 0, 10],
         "cubes": [_cube([-8, 9, -2], [3, 10, 3]),
                   _cube([-8.5, 5, -2.5], [3, 4, 3])],
         "role": "ghost", "decor": ["claws"]},
        {"name": "arm_l", "pivot": [5, 18, 0], "rot": [-40, 0, -10],
         "cubes": [_cube([5, 9, -2], [3, 10, 3]),
                   _cube([5.5, 5, -2.5], [3, 4, 3])],
         "role": "ghost", "decor": ["claws"]},
    ]


def plan_banshee():
    return [
        {"name": "body", "pivot": [0, 12, 0], "rot": [0, 0, 0],
         "cubes": [_cube([-4, 10, -2.5], [8, 10, 5])],
         "role": "ghost", "decor": ["corset"]},
        {"name": "skirt", "pivot": [0, 10, 0], "rot": [0, 0, 0], "parent": "body",
         "cubes": [_cube([-5, 2, -3.5], [10, 8, 7]),
                   _cube([-4, -3, -2.5], [8, 5, 5])],
         "role": "ghost", "decor": ["tatters"]},
        {"name": "head", "pivot": [0, 20, 0], "rot": [4, 0, 0],
         "cubes": [_cube([-3.5, 20, -3.5], [7, 7, 7]),
                   _cube([-4, 16, 1.5], [8, 12, 2], inflate=0.3)],
         "role": "ghost", "decor": ["banshee_face", "hair"]},
        {"name": "arm_r", "pivot": [-4.5, 19, 0], "rot": [-70, 0, 14],
         "cubes": [_cube([-7.5, 10, -1.5], [3, 9, 3])], "role": "ghost", "decor": []},
        {"name": "arm_l", "pivot": [4.5, 19, 0], "rot": [-70, 0, -14],
         "cubes": [_cube([4.5, 10, -1.5], [3, 9, 3])], "role": "ghost", "decor": []},
    ]


def plan_scorpion():
    parts = [
        {"name": "body", "pivot": [0, 5, 0], "rot": [0, 0, 0],
         "cubes": [_cube([-6, 2, -8], [12, 5, 16]),
                   _cube([-5, 6.5, -6], [10, 2, 12])],
         "role": "chitin", "decor": ["shell_plates"]},
        {"name": "head", "pivot": [0, 4, -8], "rot": [0, 0, 0],
         "cubes": [_cube([-4, 2, -12], [8, 4, 4])], "role": "chitin",
         "decor": ["bug_eyes"]},
        {"name": "claw_r", "pivot": [-6, 4, -9], "rot": [0, 24, 0],
         "cubes": [_cube([-12, 2, -13], [6, 3, 4]),
                   _cube([-13, 2.5, -15], [5, 2, 3])],
         "role": "chitin", "decor": []},
        {"name": "claw_l", "pivot": [6, 4, -9], "rot": [0, -24, 0],
         "cubes": [_cube([6, 2, -13], [6, 3, 4]),
                   _cube([8, 2.5, -15], [5, 2, 3])],
         "role": "chitin", "decor": []},
        {"name": "tail", "pivot": [0, 6, 8], "rot": [-46, 0, 0],
         "cubes": [_cube([-2.5, 6, 8], [5, 14, 5])], "role": "chitin",
         "decor": ["segments"]},
        {"name": "tail_tip", "pivot": [0, 19, 10], "rot": [-60, 0, 0], "parent": "tail",
         "cubes": [_cube([-1.5, 18, 6], [3, 7, 3]),
                   _cube([-1, 24, 4.5], [2, 3, 2])],
         "role": "chitin", "decor": ["stinger"]},
    ]
    for i in range(4):
        z = -6 + i * 4
        parts.append({"name": f"leg_r{i}", "pivot": [-6, 4, z], "rot": [0, 0, 35],
                      "cubes": [_cube([-11, 0, z - 0.5], [5, 1.5, 1.5]),
                                _cube([-11, -0.0, z - 0.5], [1.5, 4, 1.5])],
                      "role": "chitin", "decor": []})
        parts.append({"name": f"leg_l{i}", "pivot": [6, 4, z], "rot": [0, 0, -35],
                      "cubes": [_cube([6, 0, z - 0.5], [5, 1.5, 1.5]),
                                _cube([9.5, 0, z - 0.5], [1.5, 4, 1.5])],
                      "role": "chitin", "decor": []})
    return parts


def plan_dragon():
    return [
        {"name": "body", "pivot": [0, 14, 0], "rot": [0, 0, 0],
         "cubes": [_cube([-9, 8, -10], [18, 14, 24])], "role": "scale",
         "decor": ["belly_plates"]},
        {"name": "neck", "pivot": [0, 18, -10], "rot": [-26, 0, 0],
         "cubes": [_cube([-4, 16, -20], [8, 8, 11])], "role": "scale", "decor": []},
        {"name": "head", "pivot": [0, 24, -19], "rot": [16, 0, 0], "parent": "neck",
         "cubes": [_cube([-4.5, 22, -29], [9, 7, 10]),
                   _cube([-3, 22, -35], [6, 4, 6]),
                   _cube([-4.5, 29, -24], [2, 5, 2]),
                   _cube([2.5, 29, -24], [2, 5, 2])],
         "role": "scale", "decor": ["dragon_face", "horns"]},
        {"name": "wing_r", "pivot": [-8, 20, -4], "rot": [0, 0, 30],
         "cubes": [_cube([-30, 19, -6], [22, 1.5, 3]),
                   _cube([-30, 6, -5], [22, 14, 0.6], inflate=-0.1)],
         "role": "wing_leather", "decor": ["wing_bones"]},
        {"name": "wing_l", "pivot": [8, 20, -4], "rot": [0, 0, -30],
         "cubes": [_cube([8, 19, -6], [22, 1.5, 3]),
                   _cube([8, 6, -5], [22, 14, 0.6], inflate=-0.1)],
         "role": "wing_leather", "decor": ["wing_bones"]},
        {"name": "leg_r", "pivot": [-6, 10, 8], "rot": [0, 0, 0],
         "cubes": [_cube([-10, 0, 5], [6, 10, 7])], "role": "scale", "decor": []},
        {"name": "leg_l", "pivot": [6, 10, 8], "rot": [0, 0, 0],
         "cubes": [_cube([4, 0, 5], [6, 10, 7])], "role": "scale", "decor": []},
        {"name": "arm_r", "pivot": [-7, 10, -6], "rot": [0, 0, 0],
         "cubes": [_cube([-10, 0, -8], [5, 9, 6])], "role": "scale", "decor": []},
        {"name": "arm_l", "pivot": [7, 10, -6], "rot": [0, 0, 0],
         "cubes": [_cube([5, 0, -8], [5, 9, 6])], "role": "scale", "decor": []},
        {"name": "tail", "pivot": [0, 14, 14], "rot": [14, 0, 0],
         "cubes": [_cube([-4, 10, 14], [8, 7, 14]),
                   _cube([-2, 11, 27], [4, 4, 12])],
         "role": "scale", "decor": ["spikes"]},
    ]


def plan_nymph():
    return [
        {"name": "body", "pivot": [0, 5, 0], "rot": [0, 0, 0],
         "cubes": [_cube([-2.5, 2.5, -2.5], [5, 5, 5])], "role": "glow",
         "decor": ["nymph_face"]},
        {"name": "wing_r", "pivot": [-2.5, 6, 1], "rot": [0, 0, -25],
         "cubes": [_cube([-8, 4, 1], [6, 7, 0.5])], "role": "wing", "decor": []},
        {"name": "wing_l", "pivot": [2.5, 6, 1], "rot": [0, 0, 25],
         "cubes": [_cube([2, 4, 1], [6, 7, 0.5])], "role": "wing", "decor": []},
        {"name": "legs", "pivot": [0, 2, 0], "rot": [0, 0, 0],
         "cubes": [_cube([-1.5, 0, -0.5], [1, 3, 1]),
                   _cube([0.5, 0, -0.5], [1, 3, 1])], "role": "glow", "decor": []},
    ]


def plan_jack():
    """Jack of Blades: normal robed figure with crimson hood, bandolier,
    white mask and a sword mounted across his back."""
    parts = plan_humanoid(
        head=8, torso_w=8, torso_h=12, torso_d=4, arm_w=4, arm_len=12,
        leg_h=12, skirt=True, cape=True, boots=True, belt=True, hands=True,
        roles={"body": "dark", "arms": "cloth", "legs": "steel",
               "head": "cloth", "cape": "cape"},
        decor={"head": ["jack_mask"],
               "cape": ["trim"], "arms": ["trim_cuff"]})
    head = next(p for p in parts if p["name"] == "head")
    # Smooth hood shell: no horned/pointed silhouette.
    head["cubes"].append(_cube([-4.3, 24.0, -4.3], [8.6, 8.6, 8.6], inflate=0.35))
    head["cube_roles"] = {1: "cloth"}
    head["decor"] = []
    parts.append({"name": "mask", "pivot": [0, 24, 0], "rot": [0, 0, 0], "parent": "head",
                  "cubes": [_cube([-3.8, 24.4, -5.8], [7.6, 7.2, 0.7], inflate=0.02)],
                  "role": "skin", "decor": ["jack_mask"]})
    body = next(p for p in parts if p["name"] == "body")
    # Robe mantle and front panel to break up the body without bulky armour.
    body["cubes"].append(_cube([-4.5, 21.0, -2.5], [9.0, 3.0, 5.0], inflate=0.12))
    body.setdefault("cube_roles", {})[len(body["cubes"]) - 1] = "cloth"
    parts.append({"name": "robe_front", "pivot": [0, 18, -2.8], "rot": [0, 0, 0], "parent": "body",
                  "cubes": [_cube([-3.5, 11.2, -2.95], [7.0, 12.8, 0.7], inflate=0.02)],
                  "role": "cloth", "decor": ["jack_robe"]})
    parts.append({"name": "jack_underrobe", "pivot": [0, 17, -3.1], "rot": [0, 0, 0], "parent": "body",
                  "cubes": [_cube([-1.7, 11.6, -3.45], [3.4, 10.8, 0.45])],
                  "role": "dark", "decor": []})
    parts.append({"name": "jack_lapel_l", "pivot": [0, 17, -3.2], "rot": [0, 0, -6], "parent": "body",
                  "cubes": [_cube([-3.55, 11.8, -3.62], [2.25, 10.6, 0.5])],
                  "role": "cloth", "decor": []})
    parts.append({"name": "jack_lapel_r", "pivot": [0, 17, -3.2], "rot": [0, 0, 6], "parent": "body",
                  "cubes": [_cube([1.3, 11.8, -3.62], [2.25, 10.6, 0.5])],
                  "role": "cloth", "decor": []})
    parts.append({"name": "jack_inner_trim_l", "pivot": [0, 17, -3.3], "rot": [0, 0, -6], "parent": "body",
                  "cubes": [_cube([-1.4, 12.1, -3.76], [0.45, 9.8, 0.38])],
                  "role": "metal", "decor": []})
    parts.append({"name": "jack_inner_trim_r", "pivot": [0, 17, -3.3], "rot": [0, 0, 6], "parent": "body",
                  "cubes": [_cube([0.95, 12.1, -3.76], [0.45, 9.8, 0.38])],
                  "role": "metal", "decor": []})
    parts.append({"name": "jack_collar_shadow", "pivot": [0, 22, -3.2], "rot": [0, 0, 0], "parent": "body",
                  "cubes": [_cube([-2.2, 21.0, -3.72], [4.4, 1.2, 0.55])],
                  "role": "dark", "decor": []})
    parts.append({"name": "robe_skirt_front", "pivot": [0, 10, -2.9], "rot": [0, 0, 0], "parent": "body",
                  "cubes": [_cube([-4.1, 6.8, -3.0], [8.2, 6.0, 0.7], inflate=0.02)],
                  "role": "cloth", "decor": ["robe_split"]})
    arm_r = next(p for p in parts if p["name"] == "arm_r")
    arm_l = next(p for p in parts if p["name"] == "arm_l")
    arm_r.setdefault("cube_roles", {})[1] = "dark"
    arm_l.setdefault("cube_roles", {})[1] = "dark"
    for leg_name in ("leg_r", "leg_l"):
        leg = next(p for p in parts if p["name"] == leg_name)
        leg["role"] = "steel"
        leg["decor"] = ["steel_plates"]
        for cube_index in range(len(leg["cubes"])):
            leg.setdefault("cube_roles", {})[cube_index] = "steel"
    # Raised outfit details so they read from gameplay distance.
    parts.append({"name": "jack_chestplate", "pivot": [0, 18, -3.55], "rot": [0, 0, 0], "parent": "body",
                  "cubes": [_cube([-3.9, 14.2, -4.25], [7.8, 7.4, 0.65], inflate=0.04)],
                  "role": "steel", "decor": ["steel_chestplate"]})
    parts.append({"name": "jack_sabaton_r", "pivot": [-3, 2, -2.3], "rot": [0, 0, 0], "parent": "leg_r",
                  "cubes": [_cube([-5.1, 0.0, -3.25], [4.2, 2.4, 2.2], inflate=0.08)],
                  "role": "steel", "decor": []})
    parts.append({"name": "jack_sabaton_l", "pivot": [3, 2, -2.3], "rot": [0, 0, 0], "parent": "leg_l",
                  "cubes": [_cube([0.9, 0.0, -3.25], [4.2, 2.4, 2.2], inflate=0.08)],
                  "role": "steel", "decor": []})
    parts.append({"name": "jack_bandolier", "pivot": [0, 17.8, -2.55], "rot": [0, 0, -28], "parent": "body",
                  "cubes": [_cube([-0.45, 10.5, -3.95], [0.9, 16.5, 0.55], inflate=0.03)],
                  "role": "belt", "decor": []})
    parts.append({"name": "jack_robe_trim_l", "pivot": [0, 12, 0], "rot": [0, 0, 0], "parent": "body",
                  "cubes": [_cube([-3.35, 12.0, -3.05], [0.65, 11.5, 0.7])],
                  "role": "metal", "decor": []})
    parts.append({"name": "jack_robe_trim_r", "pivot": [0, 12, 0], "rot": [0, 0, 0], "parent": "body",
                  "cubes": [_cube([2.7, 12.0, -3.05], [0.65, 11.5, 0.7])],
                  "role": "metal", "decor": []})
    parts.append({"name": "jack_buckle", "pivot": [0, 15, -3.0], "rot": [0, 0, 0], "parent": "body",
                  "cubes": [_cube([-1.2, 13.3, -4.05], [2.4, 1.7, 0.45])],
                  "role": "metal", "decor": []})
    parts.append({"name": "jack_waist_sash", "pivot": [0, 14, -3.3], "rot": [0, 0, 0], "parent": "body",
                  "cubes": [_cube([-4.1, 13.0, -3.86], [8.2, 1.55, 0.42])],
                  "role": "belt", "decor": []})
    parts.append({"name": "scabbard_strap", "pivot": [0, 18, 3.7], "rot": [0, 0, 32], "parent": "body",
                  "cubes": [_cube([-0.5, 8.4, 4.0], [1.0, 18.0, 0.55])],
                  "role": "belt", "decor": []})
    # Sword mounted diagonally across the back.
    parts.append({"name": "back_sword", "pivot": [0, 18, 4.25], "rot": [0, 0, -34], "parent": "body",
                  "cubes": [_cube([-0.45, 11.0, 4.45], [0.9, 20.0, 0.7]),
                            _cube([-3.4, 12.2, 4.35], [6.8, 1.0, 0.9]),
                            _cube([-0.7, 7.0, 4.35], [1.4, 5.0, 0.9])],
                  "cube_roles": {1: "metal", 2: "dark"}, "role": "metal", "decor": []})
    return parts


def plan_theresa():
    """Theresa: hooded seeress with a visible blindfolded face and layered crimson robes."""
    parts = plan_humanoid(
        head=8, torso_w=8, torso_h=12, torso_d=4, arm_w=4, arm_len=12,
        leg_h=12, hat="hood", cape=True, skirt=True, boots=True, belt=True, hands=True,
        roles={"body": "cloth", "arms": "cloth", "legs": "cloth", "head": "skin", "cape": "cape"},
        decor={"head": ["theresa_face"], "body": ["theresa_robe"], "cape": ["trim"], "arms": ["trim_cuff"]})
    body = next(p for p in parts if p["name"] == "body")
    body["cubes"].append(_cube([-4.6, 20.5, -2.6], [9.2, 3.2, 5.2], inflate=0.14))
    body.setdefault("cube_roles", {})[len(body["cubes"]) - 1] = "cloth"
    parts.append({"name": "theresa_front_panel", "pivot": [0, 16, -2.8], "rot": [0, 0, 0], "parent": "body",
                  "cubes": [_cube([-3.25, 9.0, -3.05], [6.5, 13.4, 0.55], inflate=0.02)],
                  "role": "cloth", "decor": ["theresa_robe"]})
    parts.append({"name": "theresa_sash", "pivot": [0, 15.5, -3.2], "rot": [0, 0, -24], "parent": "body",
                  "cubes": [_cube([-0.45, 9.8, -3.58], [0.9, 13.6, 0.45], inflate=0.02)],
                  "role": "belt", "decor": []})
    parts.append({"name": "theresa_trim_l", "pivot": [0, 12, 0], "rot": [0, 0, 0], "parent": "body",
                  "cubes": [_cube([-3.65, 8.8, -3.42], [0.55, 13.2, 0.45])],
                  "role": "belt", "decor": []})
    parts.append({"name": "theresa_trim_r", "pivot": [0, 12, 0], "rot": [0, 0, 0], "parent": "body",
                  "cubes": [_cube([3.1, 8.8, -3.42], [0.55, 13.2, 0.45])],
                  "role": "belt", "decor": []})
    parts.append({"name": "theresa_pendant", "pivot": [0, 18.5, -3.4], "rot": [0, 0, 0], "parent": "body",
                  "cubes": [_cube([-0.65, 17.8, -3.72], [1.3, 1.3, 0.45])],
                  "role": "belt", "decor": []})
    return parts


def plan_twinblade():
    """Twinblade, the Bandit King: a mountain of a man in dark-red leather,
    spiked pauldrons, pale fur collar, bald head, black beard, eyepatch — and the two
    great blades crossed on his back that earned the name."""
    hip, tw, th, td = 13, 14, 14, 7
    shoulder, top = hip + th - 2, hip + th
    parts = [
        {"name": "leg_r", "pivot": [-4, hip, 0], "rot": [0, 0, 0],
         "cubes": [_cube([-7, 0, -2.5], [5, 13, 5]),
                   _cube([-7, 0, -2.5], [5, 5, 5], inflate=0.4)],
         "cube_roles": {1: "boots"}, "role": "cloth", "decor": []},
        {"name": "leg_l", "pivot": [4, hip, 0], "rot": [0, 0, 0],
         "cubes": [_cube([2, 0, -2.5], [5, 13, 5]),
                   _cube([2, 0, -2.5], [5, 5, 5], inflate=0.4)],
         "cube_roles": {1: "boots"}, "role": "cloth", "decor": []},
        {"name": "body", "pivot": [0, hip, 0], "rot": [0, 0, 0],
         "cubes": [_cube([-7, hip, -3.5], [tw, th, td]),
                   _cube([-7, hip + 1, -3.5], [tw, 3, td], inflate=0.45)],
         "cube_roles": {1: "belt"}, "role": "cloth", "decor": ["straps"]},
        {"name": "collar", "pivot": [0, shoulder, 0], "rot": [0, 0, 0], "parent": "body",
         "cubes": [_cube([-8, shoulder - 1, -4.5], [16, 4, 9], inflate=0.3)],
         "role": "fur", "decor": []},
        {"name": "pauldron_r", "pivot": [-8, shoulder, 0], "rot": [0, 0, 8], "parent": "body",
         "cubes": [_cube([-13, shoulder - 2, -4], [6, 5, 8]),
                   _cube([-12, shoulder + 3, -2], [2, 3, 2]),
                   _cube([-10, shoulder + 3, 0], [2, 3, 2])],
         "cube_roles": {1: "horn", 2: "horn"}, "role": "metal", "decor": ["spikes"]},
        {"name": "pauldron_l", "pivot": [8, shoulder, 0], "rot": [0, 0, -8], "parent": "body",
         "cubes": [_cube([7, shoulder - 2, -4], [6, 5, 8]),
                   _cube([10, shoulder + 3, -2], [2, 3, 2]),
                   _cube([8, shoulder + 3, 0], [2, 3, 2])],
         "cube_roles": {1: "horn", 2: "horn"}, "role": "metal", "decor": ["spikes"]},
        {"name": "arm_r", "pivot": [-8, shoulder, 0], "rot": [0, 0, 4],
         "cubes": [_cube([-13, 12, -2.5], [5, 13, 5]),
                   _cube([-13, 12, -2.5], [5, 4, 5], inflate=0.35)],
         "cube_roles": {1: "metal"}, "role": "skin", "decor": []},
        {"name": "arm_l", "pivot": [8, shoulder, 0], "rot": [0, 0, -4],
         "cubes": [_cube([8, 12, -2.5], [5, 13, 5]),
                   _cube([8, 12, -2.5], [5, 4, 5], inflate=0.35)],
         "cube_roles": {1: "metal"}, "role": "skin", "decor": []},
        {"name": "head", "pivot": [0, top, 0], "rot": [0, 0, 0],
         "cubes": [_cube([-4.5, top, -4.5], [9, 9, 9]),
                   _cube([-3.2, top - 3.5, -5.7], [6.4, 6.4, 2.2]),
                   _cube([-4.0, top + 0.2, -5.0], [8.0, 3.8, 1.2]),
                   _cube([-4.8, top - 1.2, -3.8], [1.5, 5.5, 2.2]),
                   _cube([3.3, top - 1.2, -3.8], [1.5, 5.5, 2.2])],
         "cube_roles": {1: "hair", 2: "hair", 3: "hair", 4: "hair"}, "role": "skin",
         "decor": ["twinblade_face"]},
        {"name": "blade_r", "pivot": [0, shoulder - 4, 4], "rot": [0, 0, 26], "parent": "body",
         "cubes": [_cube([-1, hip + 2, 3.6], [2, 17, 1])], "role": "metal", "decor": []},
        {"name": "blade_l", "pivot": [0, shoulder - 4, 4], "rot": [0, 0, -26], "parent": "body",
         "cubes": [_cube([-1, hip + 2, 4.7], [2, 17, 1])], "role": "metal", "decor": []},
    ]
    return parts


def plan_demon_door():
    """The carved living face of a Demon Door. Both eyes protrude further
    than the nose so the whole face reads from any angle."""
    return [
        {"name": "body", "pivot": [0, 0, 0], "rot": [0, 0, 0],
         "cubes": [_cube([-16, 0, -4], [32, 48, 6])],
         "role": "rock", "decor": ["door_slab"]},
        {"name": "brow", "pivot": [0, 34, -4], "rot": [0, 0, 0],
         "cubes": [_cube([-13, 33, -7], [10, 4, 4]),
                   _cube([3, 33, -7], [10, 4, 4]),
                   _cube([-3, 35, -6], [6, 3, 3])],
         "role": "rock", "decor": ["brow"]},
        {"name": "eye_r", "pivot": [-7, 29, -4], "rot": [0, 0, 0],
         "cubes": [_cube([-11, 26, -7], [8, 7, 3])],
         "role": "rock", "decor": ["door_eye"]},
        {"name": "eye_l", "pivot": [7, 29, -4], "rot": [0, 0, 0],
         "cubes": [_cube([3, 26, -7], [8, 7, 3])],
         "role": "rock", "decor": ["door_eye"]},
        {"name": "nose", "pivot": [0, 24, -4], "rot": [0, 0, 0],
         "cubes": [_cube([-3, 17, -6, ], [6, 12, 2.5])],
         "role": "rock", "decor": []},
        {"name": "upper_lip", "pivot": [0, 13, -4], "rot": [0, 0, 0],
         "cubes": [_cube([-10.5, 12.0, -8], [21, 3.8, 4])],
         "role": "rock", "decor": []},
        {"name": "lower_lip", "pivot": [0, 6, -4], "rot": [0, 0, 0],
         "cubes": [_cube([-9.5, 4.2, -8], [19, 3.4, 4])],
         "role": "rock", "decor": []},
        {"name": "mouth_corner_r", "pivot": [-8.5, 8.2, -4], "rot": [0, 0, -10],
         "cubes": [_cube([-11.4, 6.0, -8], [3.4, 7.6, 3.5])],
         "role": "rock", "decor": []},
        {"name": "mouth_corner_l", "pivot": [8.5, 8.2, -4], "rot": [0, 0, 10],
         "cubes": [_cube([8.0, 6.0, -8], [3.4, 7.6, 3.5])],
         "role": "rock", "decor": []},
        {"name": "mouth_cavity", "pivot": [0, 9.2, -6], "rot": [0, 0, 0],
         "cubes": [_cube([-7.6, 7.2, -8.65], [15.2, 5.5, 1.1])],
         "role": "rock", "decor": ["door_mouth"]},
    ]


# ---------------------------------------------------------------------------
# Palettes (material role -> base colour per mob)
# ---------------------------------------------------------------------------

PAL = {
    "balverine": {"fur": (66, 52, 44), "skin": (120, 96, 80), "glowcol": (220, 170, 60)},
    "white_balverine": {"fur": (225, 222, 215), "skin": (190, 180, 175), "glowcol": (130, 200, 255)},
    "frost_balverine": {"fur": (164, 196, 216), "skin": (200, 224, 236), "glowcol": (110, 220, 255)},
    "hobbe": {"skin": (134, 142, 92), "cloth": (104, 82, 58), "glowcol": (230, 200, 80)},
    "hobbe_scout": {"skin": (120, 130, 86), "cloth": (70, 76, 60), "glowcol": (230, 200, 80)},
    "bandit": {"skin": (196, 154, 116), "cloth": (94, 60, 48), "metal": (130, 130, 140), "boots": (72, 50, 34), "belt": (44, 34, 26), "glowcol": (255, 220, 150)},
    "bandit_archer": {"skin": (186, 148, 112), "cloth": (62, 72, 52), "metal": (120, 120, 130), "boots": (58, 54, 42), "belt": (40, 36, 30), "glowcol": (255, 220, 150)},
    "twinblade": {"skin": (190, 144, 104), "cloth": (116, 46, 38), "metal": (148, 142, 148), "fur": (212, 198, 180), "hair": (34, 24, 18), "horn": (208, 198, 182), "boots": (58, 40, 30), "belt": (40, 30, 24), "glowcol": (255, 200, 120)},
    "undead": {"skin": (148, 158, 132), "bone": (208, 206, 186), "cloth": (78, 84, 70), "glowcol": (140, 240, 170)},
    "undead_soldier": {"bone": (204, 200, 178), "cloth": (96, 86, 66), "metal": (124, 98, 78), "tabard": (122, 108, 82), "crest": (70, 60, 46), "belt": (50, 42, 34), "glowcol": (140, 240, 170)},
    "undead_knight": {"bone": (200, 196, 176), "cloth": (70, 64, 56), "metal": (98, 86, 76), "belt": (46, 38, 32), "glowcol": (140, 240, 170)},
    "wasp": {"chitin": (212, 168, 52), "dark": (52, 44, 30), "wing": (220, 230, 240), "glowcol": (255, 230, 120)},
    "wasp_queen": {"chitin": (230, 150, 40), "dark": (60, 30, 24), "wing": (235, 220, 245), "glowcol": (255, 200, 90)},
    "beetle": {"chitin": (124, 138, 84), "dark": (54, 60, 38), "glowcol": (200, 235, 140)},
    "earth_troll": {"rock": (118, 104, 84), "moss": (86, 116, 60), "glowcol": (255, 190, 80)},
    "ice_troll": {"rock": (158, 186, 206), "moss": (210, 235, 245), "glowcol": (120, 220, 255)},
    "rock_giant": {"rock": (96, 90, 86), "moss": (140, 110, 70), "glowcol": (255, 130, 40)},
    "summoner": {"cloth": (84, 64, 130), "skin": (182, 162, 172), "metal": (170, 150, 200), "glowcol": (210, 140, 255)},
    "wraith": {"ghost": (96, 120, 124), "glowcol": (150, 255, 200)},
    "banshee": {"ghost": (140, 160, 178), "glowcol": (170, 230, 255)},
    "minion": {"skin": (110, 70, 80), "metal": (74, 70, 82), "cloth": (60, 40, 50), "glowcol": (255, 90, 60)},
    "arachanox": {"chitin": (78, 52, 110), "dark": (40, 26, 56), "glowcol": (200, 120, 255)},
    "assassin": {"cloth": (48, 44, 56), "skin": (180, 150, 130), "metal": (90, 30, 36), "glowcol": (255, 120, 90)},
    "jack_of_blades": {"cloth": (150, 22, 26), "dark": (34, 28, 30), "metal": (170, 150, 118), "steel": (164, 170, 176), "skin": (235, 232, 224), "cape": (96, 14, 20), "boots": (24, 20, 22), "belt": (92, 54, 28), "glowcol": (255, 60, 45)},
    "jack_dragon": {"scale": (96, 26, 30), "wing_leather": (60, 18, 22), "glowcol": (255, 200, 90)},
    "villager_albion": {"skin": (208, 168, 130), "cloth": (110, 90, 64), "hair": (112, 78, 46), "boots": (112, 80, 50), "belt": (58, 42, 28), "glowcol": (255, 240, 200)},
    "villager_woman": {"skin": (212, 172, 134), "cloth": (104, 118, 74), "hair": (86, 58, 34), "boots": (50, 38, 32), "belt": (62, 44, 30), "glowcol": (255, 240, 200)},
    "villager_farmer": {"skin": (204, 162, 122), "cloth": (126, 98, 62), "straw": (208, 182, 108), "boots": (138, 106, 64), "belt": (56, 40, 28), "glowcol": (255, 240, 200)},
    "villager_tailor": {"skin": (188, 132, 92), "tunic": (92, 56, 118), "sleeves": (176, 150, 116), "pants": (70, 54, 48), "apron": (220, 210, 190), "hair": (42, 32, 28), "boots": (44, 34, 28), "belt": (86, 58, 34), "glowcol": (255, 230, 190)},
    "villager_blacksmith": {"skin": (126, 86, 60), "tunic": (78, 74, 68), "sleeves": (154, 126, 92), "pants": (54, 48, 44), "apron": (72, 58, 48), "hair": (28, 24, 22), "boots": (34, 30, 28), "belt": (92, 62, 36), "metal": (150, 154, 160), "glowcol": (255, 200, 130)},
    "villager_fisher": {"skin": (220, 178, 132), "tunic": (58, 108, 126), "sleeves": (196, 178, 138), "pants": (64, 82, 72), "hair": (150, 98, 46), "boots": (50, 42, 34), "belt": (70, 48, 32), "glowcol": (190, 230, 255)},
    "guild_apprentice_might": {"skin": (198, 150, 106), "tunic": (226, 228, 234), "sleeves": (146, 156, 172), "pants": (214, 218, 226), "cloth": (226, 228, 234), "hair": (76, 48, 28), "boots": (92, 58, 34), "belt": (82, 54, 30), "crest": (148, 190, 224), "glowcol": (180, 220, 255)},
    "guild_apprentice_skill": {"skin": (216, 172, 126), "tunic": (226, 228, 234), "sleeves": (146, 156, 172), "pants": (214, 218, 226), "cloth": (226, 228, 234), "hair": (108, 68, 40), "boots": (92, 58, 34), "belt": (82, 54, 30), "crest": (148, 190, 224), "glowcol": (180, 220, 255)},
    "guild_apprentice_will": {"skin": (176, 126, 98), "tunic": (226, 228, 234), "sleeves": (146, 156, 172), "pants": (214, 218, 226), "cloth": (226, 228, 234), "hair": (32, 26, 24), "boots": (92, 58, 34), "belt": (82, 54, 30), "crest": (148, 190, 224), "glowcol": (180, 220, 255)},
    "guard_bowerstone": {"skin": (200, 162, 124), "cloth": (52, 70, 140), "metal": (150, 155, 168), "tabard": (204, 182, 92), "crest": (60, 84, 170), "boots": (40, 44, 64), "belt": (48, 36, 26), "glowcol": (200, 220, 255)},
    "guard_oakvale": {"skin": (204, 166, 126), "cloth": (150, 44, 40), "metal": (150, 150, 160), "tabard": (232, 222, 198), "crest": (170, 50, 44), "boots": (92, 40, 34), "belt": (50, 38, 26), "glowcol": (255, 200, 180)},
    "guard_snowspire": {"skin": (198, 160, 124), "cloth": (200, 110, 36), "metal": (170, 180, 195), "tabard": (240, 235, 224), "crest": (216, 124, 44), "boots": (146, 112, 72), "belt": (54, 40, 28), "glowcol": (255, 220, 160)},
    "trader": {"skin": (202, 164, 128), "cloth": (140, 100, 50), "boots": (122, 62, 40), "belt": (60, 44, 30), "glowcol": (255, 230, 170)},
    "barkeep": {"skin": (210, 170, 132), "cloth": (90, 60, 40), "boots": (64, 46, 32), "belt": (54, 40, 28), "glowcol": (255, 230, 170)},
    "guildmaster": {"skin": (190, 158, 128), "tunic": (64, 76, 132), "sleeves": (178, 188, 210), "pants": (46, 52, 86), "cloth": (70, 80, 120), "metal": (180, 170, 130), "hair": (176, 174, 168), "boots": (38, 34, 48), "belt": (76, 54, 34), "crest": (220, 190, 90), "glowcol": (180, 220, 255)},
    "maze": {"skin": (216, 186, 152), "cloth": (58, 122, 130), "cape": (96, 60, 130), "metal": (208, 172, 88), "hair": (228, 226, 220), "boots": (46, 34, 56), "belt": (190, 156, 78), "glowcol": (120, 220, 255)},
    "theresa": {"skin": (192, 156, 124), "cloth": (126, 30, 34), "cape": (88, 24, 28), "hair": (70, 48, 34), "boots": (58, 36, 32), "belt": (168, 134, 70), "glowcol": (255, 160, 160)},
    "lady_grey": {"skin": (214, 178, 144), "cloth": (90, 96, 110), "metal": (220, 200, 140), "hair": (208, 178, 116), "boots": (152, 152, 164), "belt": (180, 160, 110), "glowcol": (220, 220, 255)},
    "oracle": {"ghost": (130, 170, 190), "glowcol": (150, 230, 255)},
    "briar_rose": {"skin": (200, 160, 126), "cloth": (120, 40, 60), "hair": (140, 72, 48), "boots": (126, 66, 44), "belt": (58, 42, 28), "glowcol": (255, 180, 200)},
    "mercenary": {"skin": (192, 152, 118), "cloth": (80, 70, 60), "metal": (140, 140, 150), "boots": (92, 90, 96), "belt": (48, 36, 26), "glowcol": (255, 230, 170)},
    "nymph": {"glow": (150, 230, 200), "wing": (210, 245, 235), "glowcol": (180, 255, 220)},
    "demon_door": {"rock": (120, 116, 110), "glowcol": (210, 205, 192)},
}

# ---------------------------------------------------------------------------
# MOB ROSTER
# ---------------------------------------------------------------------------
# behavior templates: melee | ranged | caster | npc | boss_melee | flying |
#                     flying_boss | ghost | ally | door

MOBS = [
    # --- hostile ---
    {"id": "balverine", "name": "Balverine", "plan": ("balverine", {}),
     "behavior": "melee", "hp": 40, "dmg": 7, "speed": 0.38, "family": ["monster", "fc_balverine", "fc_supernatural"],
     "spawn": {"biomes": ["forest", "taiga", "roofed"], "night": True, "weight": 18, "herd": [1, 3]},
     "drops": [("fc:balverine_fang", 1, 2, 1.0), ("fc:gold_coin", 1, 4, 0.6)],
     "scale": 1.0, "leap": True},
    {"id": "white_balverine", "name": "White Balverine", "plan": ("balverine", {"white": True}),
     "behavior": "boss_melee", "hp": 300, "dmg": 13, "speed": 0.42, "family": ["monster", "fc_white_balverine", "fc_boss", "fc_supernatural"],
     "spawn": None, "drops": [("fc:balverine_trophy", 1, 1, 1.0), ("fc:silver_key", 1, 1, 0.5)],
     "scale": 1.25, "leap": True, "boss_summons": "fc:balverine"},
    {"id": "frost_balverine", "name": "Frost Balverine", "plan": ("balverine", {"frost": True}),
     "behavior": "melee", "hp": 90, "dmg": 10, "speed": 0.4, "family": ["monster", "fc_frost_balverine", "fc_supernatural"],
     "spawn": {"biomes": ["frozen"], "night": True, "weight": 14, "herd": [1, 2]},
     "drops": [("fc:frost_balverine_hide", 1, 2, 1.0), ("fc:balverine_fang", 0, 2, 0.7)],
     "scale": 1.1, "leap": True},
    {"id": "hobbe", "name": "Hobbe", "plan": ("hobbe", {}),
     "behavior": "melee", "hp": 18, "dmg": 4, "speed": 0.3, "family": ["monster", "fc_hobbe"],
     "spawn": {"biomes": ["forest", "extreme_hills", "caves"], "night": True, "weight": 25, "herd": [2, 5]},
     "drops": [("fc:gold_coin", 1, 3, 0.8), ("fc:health_potion", 1, 1, 0.15)],
     "scale": 0.85},
    {"id": "hobbe_scout", "name": "Hobbe Scout", "plan": ("hobbe", {}),
     "behavior": "ranged", "hp": 14, "dmg": 4, "speed": 0.32, "family": ["monster", "fc_hobbe"],
     "spawn": {"biomes": ["forest", "extreme_hills"], "night": True, "weight": 10, "herd": [1, 2]},
     "drops": [("fc:gold_coin", 1, 2, 0.8)], "scale": 0.8},
    {"id": "bandit", "name": "Bandit", "plan": ("humanoid", {"boots": True, "belt": True,
                                                             "roles": {"body": "cloth", "arms": "cloth", "legs": "cloth", "head": "skin"},
                                                             "decor": {"head": ["bandit_face"], "body": ["belt"]}}),
     "behavior": "melee", "hp": 24, "dmg": 6, "speed": 0.33, "family": ["monster", "fc_bandit", "illager"],
     "spawn": {"biomes": ["plains", "savanna", "extreme_hills", "mesa"], "night": False, "weight": 16, "herd": [2, 4]},
     "drops": [("fc:gold_coin", 2, 6, 1.0), ("fc:iron_longsword", 1, 1, 0.1)],
     "scale": 1.0},
    {"id": "bandit_archer", "name": "Bandit Archer", "plan": ("humanoid", {"boots": True, "belt": True,
                                                                           "roles": {"body": "cloth", "arms": "cloth", "legs": "cloth", "head": "skin"},
                                                                           "decor": {"head": ["bandit_face", "hood"], "body": ["quiver"]}}),
     "behavior": "ranged", "hp": 20, "dmg": 5, "speed": 0.33, "family": ["monster", "fc_bandit", "illager"],
     "spawn": {"biomes": ["plains", "savanna", "extreme_hills", "mesa"], "night": False, "weight": 10, "herd": [1, 2]},
     "drops": [("fc:gold_coin", 2, 5, 1.0), ("fc:yew_longbow", 1, 1, 0.1)],
     "scale": 1.0},
    {"id": "twinblade", "name": "Twinblade", "plan": ("twinblade", {}),
     "behavior": "boss_melee", "hp": 280, "dmg": 13, "speed": 0.3,
     "family": ["monster", "fc_twinblade", "fc_boss"],
     "spawn": None,
     "drops": [("fc:gold_coin", 10, 30, 1.0), ("fc:steel_greatsword", 1, 1, 0.5),
               ("fc:obsidian_longsword", 1, 1, 0.3), ("fc:ages_of_might_potion", 1, 1, 0.4)],
     "scale": 1.5, "knockback": True},
    {"id": "undead", "name": "Hollow Man", "plan": ("humanoid", {"roles": {"body": "bone", "arms": "bone", "legs": "bone", "head": "bone"},
                                                                 "decor": {"head": ["skull_face"], "body": ["ribs"]}, "hunch": 12}),
     "behavior": "melee", "hp": 22, "dmg": 5, "speed": 0.24, "family": ["monster", "undead", "fc_undead", "fc_supernatural"],
     "spawn": {"biomes": ["swamp", "plains", "roofed"], "night": True, "weight": 20, "herd": [2, 4]},
     "drops": [("fc:ectoplasm", 0, 2, 0.6), ("fc:gold_coin", 0, 3, 0.5)],
     "scale": 1.0, "poison": True},
    {"id": "undead_soldier", "name": "Hollow Soldier", "plan": ("humanoid", {"helmet": True, "belt": True, "hunch": 8,
                                                                             "roles": {"body": "cloth", "arms": "bone", "legs": "bone", "head": "bone"},
                                                                             "decor": {"head": ["skull_face"], "body": ["tabard", "tatters"]}}),
     "behavior": "melee", "hp": 30, "dmg": 6, "speed": 0.26, "family": ["monster", "undead", "fc_undead", "fc_supernatural"],
     "spawn": {"biomes": ["swamp", "roofed"], "night": True, "weight": 9, "herd": [1, 3]},
     "drops": [("fc:ectoplasm", 0, 2, 0.6), ("fc:iron_longsword", 1, 1, 0.12), ("fc:gold_coin", 0, 4, 0.5)],
     "scale": 1.0, "poison": True},
    {"id": "undead_knight", "name": "Hollow Knight", "plan": ("humanoid", {"helmet": True, "pauldrons": True, "belt": True, "hunch": 5,
                                                                            "roles": {"body": "metal", "arms": "metal", "legs": "metal", "head": "bone"},
                                                                            "decor": {"head": ["skull_face"], "body": ["plates"]}}),
     "behavior": "melee", "hp": 44, "dmg": 8, "speed": 0.22, "family": ["monster", "undead", "fc_undead", "fc_supernatural"],
     "spawn": {"biomes": ["swamp", "roofed"], "night": True, "weight": 5, "herd": [1, 2]},
     "drops": [("fc:ectoplasm", 1, 3, 0.8), ("fc:steel_longsword", 1, 1, 0.15), ("fc:gold_coin", 1, 5, 0.6)],
     "scale": 1.05, "poison": True},
    {"id": "wasp", "name": "Wasp", "plan": ("wasp", {}),
     "behavior": "flying", "hp": 10, "dmg": 3, "speed": 0.6, "family": ["monster", "fc_wasp", "arthropod"],
     "spawn": {"biomes": ["forest", "plains", "flower"], "night": False, "weight": 22, "herd": [2, 6]},
     "drops": [("fc:wasp_wing", 1, 2, 1.0)], "scale": 1.0},
    {"id": "wasp_queen", "name": "Wasp Queen", "plan": ("wasp", {"queen": True}),
     "behavior": "flying_boss", "hp": 160, "dmg": 8, "speed": 0.55, "family": ["monster", "fc_wasp_queen", "fc_boss", "arthropod"],
     "spawn": None, "drops": [("fc:queens_stinger", 1, 1, 1.0)], "scale": 1.0,
     "boss_summons": "fc:wasp"},
    {"id": "beetle", "name": "Stag Beetle", "plan": ("beetle", {}),
     "behavior": "melee", "hp": 8, "dmg": 2, "speed": 0.32, "family": ["monster", "fc_beetle", "arthropod"],
     "spawn": {"biomes": ["forest", "swamp", "jungle"], "night": False, "weight": 20, "herd": [2, 5]},
     "drops": [("fc:beetle_chitin", 1, 2, 1.0)], "scale": 1.0},
    {"id": "earth_troll", "name": "Earth Troll", "plan": ("troll", {}),
     "behavior": "boss_melee", "hp": 140, "dmg": 14, "speed": 0.22, "family": ["monster", "fc_troll"],
     "spawn": {"biomes": ["extreme_hills", "swamp"], "night": False, "weight": 4, "herd": [1, 1]},
     "drops": [("fc:troll_heart", 1, 1, 0.8), ("fc:troll_bones", 2, 5, 1.0)],
     "scale": 1.45, "knockback": True},
    {"id": "ice_troll", "name": "Ice Troll", "plan": ("troll", {"icy": True}),
     "behavior": "boss_melee", "hp": 220, "dmg": 16, "speed": 0.22, "family": ["monster", "fc_troll"],
     "spawn": {"biomes": ["frozen"], "night": False, "weight": 4, "herd": [1, 1]},
     "drops": [("fc:troll_heart", 1, 1, 1.0), ("fc:troll_bones", 3, 6, 1.0)],
     "scale": 1.6, "knockback": True},
    {"id": "rock_giant", "name": "Rock Giant", "plan": ("troll", {"giant": True}),
     "behavior": "boss_melee", "hp": 400, "dmg": 20, "speed": 0.18, "family": ["monster", "fc_rock_giant", "fc_boss"],
     "spawn": None, "drops": [("fc:giants_core", 1, 1, 1.0), ("fc:troll_bones", 4, 8, 1.0)],
     "scale": 2.0, "knockback": True},
    {"id": "summoner", "name": "Summoner", "plan": ("humanoid", {"hat": "hood", "cape": True,
                                                                 "roles": {"body": "cloth", "arms": "cloth", "legs": "cloth", "head": "cloth", "cape": "cloth"},
                                                                 "decor": {"head": ["summoner_face"], "body": ["runes"]}}),
     "behavior": "caster", "hp": 55, "dmg": 6, "speed": 0.3, "family": ["monster", "fc_summoner"],
     "spawn": {"biomes": ["frozen"], "night": True, "weight": 8, "herd": [1, 2]},
     "drops": [("fc:summoners_grimoire", 1, 1, 0.2), ("fc:will_potion", 1, 1, 0.5)],
     "scale": 1.05, "boss_summons": "fc:minion"},
    {"id": "wraith", "name": "Wraith", "plan": ("wraith", {}),
     "behavior": "ghost", "hp": 35, "dmg": 6, "speed": 0.3, "family": ["monster", "undead", "fc_wraith", "fc_supernatural"],
     "spawn": {"biomes": ["frozen", "roofed", "swamp"], "night": True, "weight": 8, "herd": [1, 2]},
     "drops": [("fc:ectoplasm", 1, 3, 1.0), ("fc:silver_key", 1, 1, 0.06)],
     "scale": 1.0},
    {"id": "banshee", "name": "Banshee", "plan": ("banshee", {}),
     "behavior": "ghost", "hp": 70, "dmg": 8, "speed": 0.28, "family": ["monster", "undead", "fc_banshee", "fc_supernatural"],
     "spawn": {"biomes": ["swamp"], "night": True, "weight": 5, "herd": [1, 1]},
     "drops": [("fc:banshees_tear", 1, 1, 0.7), ("fc:ectoplasm", 1, 2, 1.0)],
     "scale": 1.05, "shriek": True},
    {"id": "minion", "name": "Minion", "plan": ("humanoid", {"pauldrons": True, "horns": True,
                                                             "head": 8, "torso_w": 12, "torso_h": 13, "arm_w": 5, "arm_len": 14, "leg_h": 11,
                                                             "roles": {"body": "metal", "arms": "skin", "legs": "metal", "head": "metal"},
                                                             "decor": {"head": ["minion_face"], "body": ["plates"]}}),
     "behavior": "melee", "hp": 50, "dmg": 9, "speed": 0.28, "family": ["monster", "fc_minion"],
     "spawn": {"biomes": ["mesa", "savanna"], "night": True, "weight": 10, "herd": [1, 3]},
     "drops": [("fc:minion_flesh", 1, 2, 1.0), ("fc:gold_coin", 1, 4, 0.5)],
     "scale": 1.15},
    {"id": "arachanox", "name": "Arachanox", "plan": ("scorpion", {}),
     "behavior": "boss_melee", "hp": 350, "dmg": 15, "speed": 0.3, "family": ["monster", "fc_arachanox", "fc_boss", "arthropod"],
     "spawn": None, "drops": [("fc:scorpion_stinger", 1, 1, 1.0)],
     "scale": 1.8, "poison": True},
    {"id": "assassin", "name": "Assassin", "plan": ("humanoid", {"hat": "hood", "cape": True,
                                                                 "roles": {"body": "cloth", "arms": "cloth", "legs": "cloth", "head": "cloth", "cape": "cloth"},
                                                                 "decor": {"head": ["assassin_face"], "body": ["belt", "daggers"]}}),
     "behavior": "melee", "hp": 45, "dmg": 9, "speed": 0.42, "family": ["monster", "fc_assassin"],
     "spawn": None, "drops": [("fc:gold_coin", 4, 10, 1.0), ("fc:assassin_torso", 1, 1, 0.15)],
     "scale": 1.0},
    {"id": "jack_of_blades", "name": "Jack of Blades", "plan": ("jack", {}),
     "behavior": "boss_melee", "hp": 500, "dmg": 16, "speed": 0.38, "family": ["monster", "fc_jack", "fc_boss"],
     "spawn": None, "drops": [("fc:jack_of_blades_mask", 1, 1, 1.0)],
        "scale": 1.05, "boss_summons": "fc:undead"},
    {"id": "jack_dragon", "name": "Dragon of Blades", "plan": ("dragon", {}),
     "behavior": "flying_boss", "hp": 700, "dmg": 22, "speed": 0.5, "family": ["monster", "fc_jack_dragon", "fc_boss"],
     "spawn": None, "drops": [("fc:sword_of_aeons", 1, 1, 1.0), ("fc:gold_coin", 30, 60, 1.0)],
     "scale": 2.2, "fire": True},
    # --- friendly ---
    {"id": "villager_albion", "name": "Albion Villager", "plan": ("humanoid", {"hair": True, "boots": True, "belt": True, "hands": True,
                                                                               "roles": {"body": "tunic", "arms": "sleeves", "legs": "pants"},
                                                                               "decor": {"head": ["face"], "body": ["vest", "apron"]}}),
     "behavior": "npc", "hp": 20, "dmg": 1, "speed": 0.3, "family": ["fc_villager", "fc_friendly"],
     "spawn": None, "drops": [], "scale": 1.0, "dialogue": "villager"},
    {"id": "villager_woman", "name": "Albion Villager (Woman)", "plan": ("humanoid", {"hair": "long", "skirt": True, "boots": True, "belt": True, "hands": True,
                                                                                      "roles": {"body": "tunic", "arms": "sleeves", "legs": "pants"},
                                                                                      "decor": {"head": ["lady_face"], "body": ["bodice", "embroidered_hem"]}}),
     "behavior": "npc", "hp": 20, "dmg": 1, "speed": 0.3, "family": ["fc_villager", "fc_friendly"],
     "spawn": None, "drops": [], "scale": 0.98, "dialogue": "villager"},
    {"id": "villager_farmer", "name": "Albion Farmer", "plan": ("humanoid", {"hat": "straw", "boots": True, "belt": True, "hands": True,
                                                                             "roles": {"body": "tunic", "arms": "sleeves", "legs": "pants"},
                                                                             "decor": {"head": ["face", "beard"], "body": ["apron", "tool_belt"]}}),
     "behavior": "npc", "hp": 22, "dmg": 1, "speed": 0.3, "family": ["fc_villager", "fc_friendly"],
     "spawn": None, "drops": [], "scale": 1.0, "dialogue": "villager"},
    {"id": "villager_tailor", "name": "Bowerstone Tailor", "plan": ("humanoid", {"hair": "long", "boots": True, "belt": True, "hands": True,
                                                                                 "roles": {"body": "tunic", "arms": "sleeves", "legs": "pants"},
                                                                                 "decor": {"head": ["lady_face"], "body": ["apron", "embroidered_hem"], "arms": ["trim_cuff"]}}),
     "behavior": "npc", "hp": 20, "dmg": 1, "speed": 0.3, "family": ["fc_villager", "fc_friendly"],
     "spawn": None, "drops": [], "scale": 0.98, "dialogue": "villager"},
    {"id": "villager_blacksmith", "name": "Albion Blacksmith", "plan": ("humanoid", {"hair": True, "boots": True, "belt": True, "hands": True,
                                                                                   "roles": {"body": "tunic", "arms": "sleeves", "legs": "pants"},
                                                                                   "decor": {"head": ["face", "moustache"], "body": ["apron", "tool_belt"], "arms": ["rolled_sleeves"]}}),
     "behavior": "npc", "hp": 26, "dmg": 2, "speed": 0.28, "family": ["fc_villager", "fc_friendly"],
     "spawn": None, "drops": [], "scale": 1.04, "dialogue": "villager"},
    {"id": "villager_fisher", "name": "Oakvale Fisher", "plan": ("humanoid", {"hair": True, "boots": True, "belt": True, "hands": True,
                                                                             "roles": {"body": "tunic", "arms": "sleeves", "legs": "pants"},
                                                                             "decor": {"head": ["face"], "body": ["vest", "net_sash"]}}),
     "behavior": "npc", "hp": 20, "dmg": 1, "speed": 0.3, "family": ["fc_villager", "fc_friendly"],
     "spawn": None, "drops": [], "scale": 1.0, "dialogue": "villager"},
    {"id": "guard_bowerstone", "name": "Bowerstone Guard", "plan": ("humanoid", {"helmet": True, "boots": True, "belt": True, "pauldrons": True,
                                                                                 "roles": {"body": "metal", "legs": "cloth", "arms": "metal", "head": "skin"},
                                                                                 "decor": {"head": ["face"], "body": ["tabard"]}}),
     "behavior": "guard", "hp": 40, "dmg": 8, "speed": 0.34, "family": ["fc_guard", "fc_friendly"],
     "spawn": None, "drops": [], "scale": 1.05, "dialogue": "guard"},
    {"id": "guard_oakvale", "name": "Oakvale Guard", "plan": ("humanoid", {"helmet": True, "boots": True, "belt": True, "pauldrons": True,
                                                                           "roles": {"body": "metal", "legs": "cloth", "arms": "metal", "head": "skin"},
                                                                           "decor": {"head": ["face"], "body": ["tabard"]}}),
     "behavior": "guard", "hp": 36, "dmg": 7, "speed": 0.34, "family": ["fc_guard", "fc_friendly"],
     "spawn": None, "drops": [], "scale": 1.05, "dialogue": "guard"},
    {"id": "guard_snowspire", "name": "Snowspire Guard", "plan": ("humanoid", {"helmet": True, "boots": True, "belt": True, "pauldrons": True,
                                                                               "roles": {"body": "metal", "legs": "cloth", "arms": "metal", "head": "skin"},
                                                                               "decor": {"head": ["face"], "body": ["tabard"]}}),
     "behavior": "guard", "hp": 46, "dmg": 9, "speed": 0.34, "family": ["fc_guard", "fc_friendly"],
     "spawn": None, "drops": [], "scale": 1.05, "dialogue": "guard"},
    {"id": "trader", "name": "Trader", "plan": ("humanoid", {"hat": "wizard", "belly": 1, "boots": True, "belt": True,
                                                             "decor": {"head": ["face"], "body": ["satchel"]}}),
     "behavior": "npc", "hp": 25, "dmg": 1, "speed": 0.3, "family": ["fc_trader", "fc_friendly"],
     "spawn": None, "drops": [], "scale": 1.0, "dialogue": "trader"},
    {"id": "barkeep", "name": "Barkeep", "plan": ("humanoid", {"belly": 2, "boots": True, "belt": True,
                                                               "decor": {"head": ["face", "moustache"], "body": ["apron"]}}),
     "behavior": "npc", "hp": 25, "dmg": 1, "speed": 0.28, "family": ["fc_barkeep", "fc_friendly"],
     "spawn": None, "drops": [], "scale": 1.0, "dialogue": "barkeep"},
    {"id": "guildmaster", "name": "Guildmaster", "plan": ("humanoid", {"boots": True, "belt": True, "hands": True,
                                                                       "roles": {"body": "tunic", "arms": "sleeves", "legs": "pants", "head": "skin"},
                                                                       "decor": {"head": ["face", "moustache"], "body": ["guild_crest", "robe_trim"], "arms": ["trim_cuff"]}}),
     "behavior": "npc", "hp": 100, "dmg": 1, "speed": 0.28, "family": ["fc_guildmaster", "fc_friendly"],
     "spawn": None, "drops": [], "scale": 1.0, "dialogue": "guildmaster"},
    {"id": "guild_apprentice_might", "name": "Guild Apprentice (Might)", "plan": ("humanoid", {"hat": "hood", "skirt": True, "boots": True, "belt": True, "hands": True,
                                                                                              "roles": {"body": "tunic", "arms": "sleeves", "legs": "pants"},
                                                                                              "decor": {"head": ["apprentice_hood_face"], "body": ["guild_crest", "robe_trim", "training_sash"], "arms": ["trim_cuff"]}}),
     "behavior": "npc", "hp": 24, "dmg": 2, "speed": 0.32, "family": ["fc_guild", "fc_villager", "fc_friendly"],
     "spawn": None, "drops": [], "scale": 0.98, "dialogue": "apprentice"},
    {"id": "guild_apprentice_skill", "name": "Guild Apprentice (Skill)", "plan": ("humanoid", {"hat": "hood", "skirt": True, "boots": True, "belt": True, "hands": True,
                                                                                              "roles": {"body": "tunic", "arms": "sleeves", "legs": "pants"},
                                                                                              "decor": {"head": ["hood_lady_face"], "body": ["guild_crest", "robe_trim", "quiver"], "arms": ["trim_cuff"]}}),
     "behavior": "npc", "hp": 22, "dmg": 1, "speed": 0.34, "family": ["fc_guild", "fc_villager", "fc_friendly"],
     "spawn": None, "drops": [], "scale": 0.96, "dialogue": "apprentice"},
    {"id": "guild_apprentice_will", "name": "Guild Apprentice (Will)", "plan": ("humanoid", {"hat": "hood", "skirt": True, "boots": True, "belt": True, "hands": True,
                                                                                            "roles": {"body": "tunic", "arms": "sleeves", "legs": "pants"},
                                                                                            "decor": {"head": ["hood_will_face"], "body": ["guild_crest", "robe_trim", "runes"], "arms": ["trim_cuff"]}}),
     "behavior": "npc", "hp": 20, "dmg": 1, "speed": 0.3, "family": ["fc_guild", "fc_villager", "fc_friendly"],
     "spawn": None, "drops": [], "scale": 0.96, "dialogue": "apprentice"},
    {"id": "maze", "name": "Maze", "plan": ("humanoid", {"hair": True, "cape": True, "boots": True, "belt": True,
                                                         "roles": {"cape": "cape"},
                                                         "decor": {"head": ["maze_face"], "body": ["runes"], "cape": ["trim"]}}),
     "behavior": "npc", "hp": 120, "dmg": 1, "speed": 0.3, "family": ["fc_maze", "fc_friendly"],
     "spawn": None, "drops": [], "scale": 1.08, "dialogue": "maze"},
    {"id": "theresa", "name": "Theresa", "plan": ("theresa", {}),
     "behavior": "npc", "hp": 100, "dmg": 1, "speed": 0.3, "family": ["fc_theresa", "fc_friendly"],
     "spawn": None, "drops": [], "scale": 0.98, "dialogue": "theresa"},
    {"id": "lady_grey", "name": "Lady Grey", "plan": ("humanoid", {"hair": "long", "skirt": True, "boots": True, "belt": True,
                                                                   "decor": {"head": ["lady_face"], "body": ["necklace", "bodice"]}}),
     "behavior": "npc", "hp": 30, "dmg": 1, "speed": 0.3, "family": ["fc_lady_grey", "fc_friendly"],
     "spawn": None, "drops": [], "scale": 0.98, "dialogue": "lady_grey"},
    {"id": "oracle", "name": "The Oracle", "plan": ("wraith", {}),
     "behavior": "npc", "hp": 200, "dmg": 1, "speed": 0.0, "family": ["fc_oracle", "fc_friendly"],
     "spawn": None, "drops": [], "scale": 1.4, "dialogue": "oracle"},
    {"id": "briar_rose", "name": "Briar Rose", "plan": ("humanoid", {"hair": "long", "boots": True, "belt": True,
                                                                     "decor": {"head": ["lady_face"], "body": ["bodice"]}}),
     "behavior": "npc", "hp": 60, "dmg": 1, "speed": 0.32, "family": ["fc_briar", "fc_friendly"],
     "spawn": None, "drops": [], "scale": 1.0, "dialogue": "briar_rose"},
    {"id": "mercenary", "name": "Mercenary", "plan": ("humanoid", {"pauldrons": True, "boots": True, "belt": True,
                                                                   "roles": {"body": "metal", "arms": "cloth", "legs": "cloth", "head": "skin"},
                                                                   "decor": {"head": ["bandit_face"], "body": ["plates"]}}),
     "behavior": "ally", "hp": 50, "dmg": 8, "speed": 0.34, "family": ["fc_mercenary", "fc_friendly", "fc_ally"],
     "spawn": None, "drops": [], "scale": 1.02, "dialogue": "mercenary"},
    {"id": "nymph", "name": "Nymph", "plan": ("nymph", {}),
     "behavior": "ally_flying", "hp": 14, "dmg": 3, "speed": 0.5, "family": ["fc_nymph", "fc_friendly", "fc_ally"],
     "spawn": None, "drops": [], "scale": 1.0},
    # --- summoned allies ---
    {"id": "summoned_wasp", "name": "Summoned Hornet", "plan": ("wasp", {}),
     "behavior": "ally_flying", "hp": 16, "dmg": 4, "speed": 0.6, "family": ["fc_summon", "fc_ally", "fc_friendly"],
     "spawn": None, "drops": [], "scale": 0.9, "tint": (120, 230, 200), "despawn": 1200},
    {"id": "summoned_hobbe", "name": "Summoned Hobbe", "plan": ("hobbe", {}),
     "behavior": "ally", "hp": 30, "dmg": 6, "speed": 0.34, "family": ["fc_summon", "fc_ally", "fc_friendly"],
     "spawn": None, "drops": [], "scale": 0.85, "tint": (120, 230, 200), "despawn": 1600},
    {"id": "summoned_balverine", "name": "Summoned Balverine", "plan": ("balverine", {}),
     "behavior": "ally", "hp": 60, "dmg": 10, "speed": 0.4, "family": ["fc_summon", "fc_ally", "fc_friendly"],
     "spawn": None, "drops": [], "scale": 1.0, "tint": (120, 230, 200), "despawn": 2000},
    # --- the demon door ---
    {"id": "demon_door", "name": "Demon Door", "plan": ("demon_door", {}),
     "behavior": "door", "hp": 10000, "dmg": 0, "speed": 0.0, "family": ["fc_demon_door"],
     "spawn": None, "drops": [], "scale": 1.0},
]

# Global hostile-tuning pass: keep identity, lower frustration.
# Non-boss monsters are softened more than bosses.
for mob in MOBS:
    fam = set(mob.get("family", []))
    if "monster" not in fam:
        continue
    is_boss = ("fc_boss" in fam) or (mob.get("behavior") in ("boss_melee", "flying_boss"))

    hp_mult = 0.88 if is_boss else 0.82
    dmg_mult = 0.82 if is_boss else 0.78
    speed_mult = 0.9 if is_boss else 0.86

    mob["hp"] = max(1, int(round(mob["hp"] * hp_mult)))
    mob["dmg"] = max(1, int(round(mob["dmg"] * dmg_mult)))
    mob["speed"] = round(max(0.16, mob["speed"] * speed_mult), 3)

PLAN_BUILDERS = {
    "humanoid": plan_humanoid,
    "balverine": plan_balverine,
    "hobbe": plan_hobbe,
    "troll": plan_troll,
    "wasp": plan_wasp,
    "beetle": plan_beetle,
    "wraith": plan_wraith,
    "banshee": plan_banshee,
    "scorpion": plan_scorpion,
    "dragon": plan_dragon,
    "nymph": plan_nymph,
    "jack": plan_jack,
    "theresa": plan_theresa,
    "twinblade": plan_twinblade,
    "demon_door": plan_demon_door,
}


def _add_training_bow(parts):
    """Model a wooden longbow into a humanoid's right hand (the Skill apprentice
    is an archer — it already wears a quiver — but had nothing to shoot with). The
    bow is parented to arm_r so it swings with the arm and the archery animation.
    Right hand sits near (x -6, y 11, z 0); the stave is held just in front of the
    fist. Painted automatically by gen_entity_textures from the cube roles."""
    parts.append({
        "name": "training_bow", "pivot": [-6, 11, -3], "rot": [0, 0, 0], "parent": "arm_r",
        "cubes": [
            _cube([-6.5, 9, -3.5], [1, 5, 1]),     # grip
            _cube([-6.5, 13, -4.0], [1, 6, 1]),    # upper limb (bows forward)
            _cube([-6.5, 19, -3.5], [1, 2, 1]),    # upper tip (recurves back)
            _cube([-6.5, 3, -4.0], [1, 6, 1]),     # lower limb
            _cube([-6.5, 1, -3.5], [1, 2, 1]),     # lower tip
            _cube([-6.0, 2, -2.7], [0.4, 19, 0.4]),  # string, on the inner side
        ],
        "cube_roles": {5: "horn"},                 # string reads pale; limbs = wood
        "role": "boots", "decor": []})


def _add_training_stick(parts):
    """Model a wooden practice stick into a sparring apprentice's right hand.
    The stick is parented to arm_r so the existing spar and block animations
    carry it through each exchange instead of leaving the apprentices miming
    weapon strikes."""
    parts.append({
        "name": "training_stick", "pivot": [-6, 10, -3], "rot": [0, 0, 0], "parent": "arm_r",
        "cubes": [
            _cube([-6.5, 2, -3.5], [1, 18, 1]),       # wooden shaft
            _cube([-6.7, 8, -3.7], [1.4, 4, 1.4]),   # wrapped hand grip
        ],
        "cube_roles": {1: "belt"},
        "role": "boots", "decor": []})


# Per-mob accessory parts appended after the base plan is built (build_parts is
# shared by the geometry, texture and married generators, so a hook here keeps all
# three in agreement). Keyed by mob id.
ACCESSORY_BUILDERS = {
    "guild_apprentice_might": _add_training_stick,
    "guild_apprentice_skill": _add_training_bow,
    "guild_apprentice_will": _add_training_stick,
}


def build_parts(mob):
    plan, kwargs = mob["plan"]
    parts = PLAN_BUILDERS[plan](**kwargs)
    accessory = ACCESSORY_BUILDERS.get(mob["id"])
    if accessory:
        accessory(parts)
    return parts


def mob_palette(mob):
    return PAL.get(mob["id"], PAL.get(mob["plan"][0], PAL["villager_albion"]))


# ---------------------------------------------------------------------------
# UV packing — shelf packer producing per-cube uv origins
# ---------------------------------------------------------------------------

def pack_uvs(parts):
    """Assign box-UV origins for every cube. Returns (tex_w, tex_h, uv_map)
    where uv_map[(part_idx, cube_idx)] = (u, v)."""
    boxes = []
    for pi, part in enumerate(parts):
        for ci, cube in enumerate(part["cubes"]):
            sx, sy, sz = (max(1, round(v)) for v in cube["size"])
            w = 2 * (sx + sz)
            h = sy + sz
            boxes.append(((pi, ci), w, h))
    boxes.sort(key=lambda b: -b[2])
    tex_w = 128
    x, y, shelf_h = 0, 0, 0
    uv = {}
    for key, w, h in boxes:
        if x + w > tex_w:
            x = 0
            y += shelf_h + 1
            shelf_h = 0
        uv[key] = (x, y)
        x += w + 1
        shelf_h = max(shelf_h, h)
    tex_h = y + shelf_h + 1
    size = 1
    while size < tex_h:
        size *= 2
    return tex_w, max(size, 64), uv


# ---------------------------------------------------------------------------
# ROMANCE / MARRIAGE eligibility — shared by the behaviour, resource and texture
# generators so the entity property, render controller and married skin always
# agree on which NPCs can be courted. Unique story characters are excluded
# (the Guildmaster/Maze/Theresa/Oracle are plot fixtures; Lady Grey and Briar
# Rose already have their own bespoke marriage flow in main.js).
# ---------------------------------------------------------------------------
SPOUSE_EXCLUDE = {"guildmaster", "maze", "theresa", "oracle", "lady_grey", "briar_rose"}


def is_social_npc(mob):
    return mob.get("behavior") in ("npc", "guard") or mob["id"] == "mercenary"


def is_romanceable(mob):
    return is_social_npc(mob) and mob["id"] not in SPOUSE_EXCLUDE


if __name__ == "__main__":
    for m in MOBS:
        parts = build_parts(m)
        w, h, uv = pack_uvs(parts)
        print(f"{m['id']:24s} parts={len(parts):2d} cubes={sum(len(p['cubes']) for p in parts):2d} tex={w}x{h}")
    print(f"{len(MOBS)} mobs total")
    print("romanceable:", [m["id"] for m in MOBS if is_romanceable(m)])

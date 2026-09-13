"""gen_ingame_screenshots.py — staged player's-eye captures of the addon.

The gallery set (gen_screenshots.py) and the showcase set (gen_doc_screenshots.py)
both frame the addon from outside: isometric dioramas of a structure floating on
a gradient, and full-bleed catalogue plates of items and menus. Those are useful
as a catalogue and useless as an answer to "what does this look like to play".

This set answers that instead. Each frame is rendered through a perspective
camera standing on a floor inside the same Vox data the packs ship, wearing the
same HUD hud_screen.json installs, with the same menus the scripts build from
fc_strings.js. Nothing here is captured from a running game: these are staged
renders, and screenshots/staged/INDEX.md says so on the record. What they are is
honest about framing — eye height, field of view, occlusion, the HUD in front of
it all — which the isometric plates could never be.

Run:  python scripts/gen_ingame_screenshots.py [shot_id ...]
Out:  screenshots/staged/*.png  +  INDEX.md
"""
from __future__ import annotations

import dataclasses
import math
import sys
import time

from PIL import Image

import fc_forms as FM
import fc_hud as HUD
import fc_pov as P
import gen_doc_screenshots as DOC
from fc_lib import SHOTS as SHOTS_DIR
from gen_screenshots import BLOCK_COLORS

OUT_DIR = SHOTS_DIR / "staged"
SIZE = (1280, 720)

_WORLDS = {}


def world(name):
    if name not in _WORLDS:
        _WORLDS[name] = P.World(DOC.get_vox(name), BLOCK_COLORS)
    return _WORLDS[name]


# ---------------------------------------------------------------------------
# shot data
# ---------------------------------------------------------------------------
#
# `eye` / `yaw` / `pitch` place the camera by hand where the framing matters.
# `target` instead hands the staging to fc_pov.find_viewpoint, which stands on a
# real floor with line of sight to the subject. Mob coordinates are reused from
# the showcase scenes where they already exist, so both sets show the same cast
# in the same places.

STANDARD_BAR = ["guild_seal", "steel_longsword", "yew_longbow", "spell_fireball",
                "health_potion", "apple_pie", None, None, None]


def hud(**kw):
    base = dict(health=(18, 20), will=(76, 100), stamina=(17, 20), gold=1486,
                hotbar=list(STANDARD_BAR), selected=1, level=12, xp=0.42,
                hour=10, counts={5: 3})
    base.update(kw)
    return HUD.Hud(**base)


SHOTS = [
    # --- the Guild, outside -------------------------------------------------
    {
        "id": "01_guild_grounds",
        "struct": "guild_hall",
        # Across the lawn and the canal at last light: the one frame that shows
        # how much of the Guild campus there actually is.
        "eye": (70, 2.62, 34), "look": (56, 3.2, 20),
        "sky": "GOLDEN", "reach": 96,
        "hud": dict(place="Heroes' Guild", heading="NW", distance=0, hour=18,
                    notice="§eQuest Card: Wasp Menace"),
        "caption": "The Guild campus across its lawns and canal at last light.",
    },
    {
        "id": "02_guild_courtyard",
        "struct": "guild_hall",
        # The canal runs down x62-64, so the cast stands on the west lawn rather
        # than on the water.
        "eye": (52.5, 2.62, 31), "look": (57, 3.0, 20),
        "sky": "DAY", "reach": 90,
        "mobs": [("guildmaster", (57, 1, 23), {"yaw": 3.3}),
                 ("guard_bowerstone", (53, 1, 21), {"yaw": 2.9}),
                 ("guild_apprentice_might", (60, 1, 25), {"yaw": 3.6})],
        "hud": dict(place="Heroes' Guild", heading="NW", distance=12, hour=9,
                    notice="§7The Guildmaster is expecting you."),
        "caption": "The Guild courtyard, where the Guildmaster is waiting.",
    },
    # --- the Guild, inside --------------------------------------------------
    {
        "id": "03_map_room",
        "struct": "guild_hall",
        "eye": (33.4, 2.62, 47.0), "look": (25, 1.9, 40),
        "sky": "INDOORS", "reach": 44,
        "mobs": [("guildmaster", (23, 1, 44), {"yaw": 1.1}),
                 ("guild_apprentice_might", (31, 1, 45), {"yaw": 2.4})],
        "hud": dict(place="Map Room", heading="NW", distance=6, hour=11,
                    notice="§7The Guildmaster has work for you."),
        "caption": "The Map Room: the land-and-sea relief and the Guildmaster.",
    },
    {
        "id": "04_guild_library",
        "struct": "guild_hall",
        "eye": (34.4, 2.62, 28.0), "look": (23, 2.2, 19),
        "sky": "INDOORS", "reach": 46,
        "mobs": [("guild_apprentice_will", (24, 1, 21), {"yaw": 1.3}),
                 ("guild_apprentice_skill", (29, 1, 24), {"yaw": 2.8}),
                 ("theresa", (32, 1, 26), {"yaw": 3.4})],
        "hud": dict(place="Guild Library", heading="NW", distance=9, hour=12,
                    selected=3),
        "caption": "The Library: framed cases, reading desk and supported lamps.",
    },
    {
        "id": "05_chamber_of_fate",
        "struct": "chamber_of_fate",
        "eye": (15.5, 6.6, 24.0), "look": (16, 6.0, 13),
        "sky": "INDOORS", "reach": 44,
        "mobs": [("maze", (18, 5, 13), {"yaw": 0.3}),
                 ("guildmaster", (13, 5, 15), {"yaw": 0.6})],
        "effects": ["holy_glow:16,6,13,3.5"],
        "hud": dict(place="Chamber of Fate", heading="N", distance=11, hour=14,
                    will=(100, 100), notice="§9Maze reads the Chamber."),
        "caption": "The Chamber of Fate, where Maze reads what is coming.",
    },
    {
        "id": "06_guild_dormitory",
        "struct": "guild_hall",
        "eye": (89.2, 7.62, 21.5), "look": (84, 6.9, 17),
        # The sleeping hall has no lamp within 14 blocks — the nearest light in
        # the whole Guild build is outside it — so this frame leans on the
        # window light it does have rather than pretending to a lantern.
        "sky": "INDOORS", "sky_overrides": {"indoor": 0.44, "ambient": 0.76},
        "reach": 40,
        "mobs": [("guild_apprentice_might", (83.5, 6, 20), {"yaw": 0.2})],
        "hud": dict(place="Dormitory", heading="NW", distance=7, hour=22,
                    health=(20, 20), stamina=(20, 20), eye="closed"),
        "caption": "The apprentice dormitory and its framed red bay.",
    },
    {
        "id": "07_maze_study",
        "struct": "guild_hall",
        # A wall at z=72 splits the tower top in two; the study is the northern
        # half, so the camera has to stand inside it rather than across the wall.
        "eye": (52.0, 13.62, 69.0), "look": (45.5, 12.9, 69.5),
        "sky": "INDOORS", "reach": 34,
        "mobs": [("maze", (46, 12, 70), {"yaw": 1.4})],
        "hud": dict(place="Maze's Study", heading="NW", distance=8, hour=1,
                    hour_override=True, eye="partial"),
        "caption": "Maze's study at the top of the tower.",
    },
    {
        "id": "08_archery_range",
        "struct": "guild_hall",
        "eye": (86.5, 2.62, 31.0), "look": (86.5, 3.4, 43),
        "sky": "DAY", "reach": 54,
        "mobs": [("guild_apprentice_skill", (84, 1, 36), {"yaw": 0.1})],
        "hud": dict(place="Training Grounds", heading="S", distance=18, hour=10,
                    selected=2, notice="§b+12 Skill XP"),
        "caption": "The archery range, down the firing lanes to the backboard.",
    },
    # --- Albion at large ----------------------------------------------------
    {
        "id": "09_bowerstone_market",
        "struct": "bowerstone_market",
        "target": (18, 2.0, 22), "distances": (8, 11, 14),
        "sky": "DAY", "reach": 68,
        "mobs": [("guard_bowerstone", (18, 1, 16), {"yaw": 3.14}),
                 ("trader", (14, 1, 20), {"yaw": 1.2}),
                 ("villager_woman", (22, 1, 24), {"yaw": 2.2})],
        "hud": dict(place="Bowerstone", heading="N", distance=212, hour=13,
                    gold=2740, notice="§7Bowerstone: §aFriendly"),
        "caption": "Bowerstone market, where reputation moves the prices.",
    },
    {
        "id": "10_temple_of_avo",
        "struct": "temple_avo",
        # The nave floor is y4 and the dais y5; standing on the dais and looking
        # down the colonnade is the view the building is built around.
        "eye": (8, 6.62, 14.5), "look": (8, 5.4, 5),
        "sky": "GOLDEN", "reach": 44,
        "mobs": [("villager_albion", (5.5, 4, 9), {"yaw": 0.9})],
        "effects": ["holy_glow:8,5,9,3.0"],
        "hud": dict(place="Temple of Avo", heading="N", distance=88, hour=7,
                    notice="§eYou donate 50 gold.",
                    hotbar=["guild_seal", "gold_coin", "yew_longbow", "spell_fireball",
                            "health_potion", "apple_pie", None, None, None],
                    selected=1, counts={1: 50, 5: 3}),
        "caption": "The Temple of Avo and its donation fountain.",
    },
    {
        "id": "11_cullis_gate",
        "struct": "focus_site",
        "target": (6, 2.4, 6), "distances": (5, 6, 8),
        "sky": "NIGHT", "reach": 36,
        "effects": ["holy_glow:6,2,6,3.5"],
        "hud": dict(place="Focus Site", heading="E", distance=402, hour=22,
                    will=(100, 100), eye="open",
                    notice="§bFocus Site attuned — joined to the lattice."),
        "caption": "A wild Focus Site, attuned and joined to the Cullis lattice.",
    },
    {
        "id": "12_demon_door",
        "struct": "demon_door_arch",
        # Straight on and close: the whole point of a Demon Door is the face.
        "eye": (11.5, 2.62, 0.5), "look": (11.5, 3.0, 5.5),
        "sky": "OVERCAST", "reach": 40,
        "mobs": [("demon_door", (11.5, 0.6, 5.5), {"scale": 0.16})],
        "hud": dict(place="Greatwood", heading="S", distance=640, hour=15,
                    notice="§5\"You are not yet worth opening for.\""),
        "caption": "A Demon Door: a living face in the hillside that judges you.",
    },
    {
        "id": "13_library_arcanum",
        "struct": "library_arcanum",
        "eye": (16, 4.62, 10), "look": (30, 6.0, 30),
        "sky": "ARCANE", "reach": 56,
        "hud": dict(place="The Library Arcanum", heading="N", distance=0, hour=12,
                    will=(92, 100), notice="§dA reward world beyond the door."),
        "caption": "Behind the Guild lamp door: the Library Arcanum.",
    },
    {
        "id": "14_arboretum",
        "struct": "arboretum",
        # The grove's centre column is a tree trunk, so this stands on the walking
        # loop at the north-west and looks diagonally across the rooted trees.
        "eye": (16, 4.62, 10), "look": (28, 8.0, 28),
        "sky": "DAY", "reach": 60,
        "hud": dict(place="The Arboretum", heading="E", distance=0, hour=10,
                    selected=1,
                    hotbar=["guild_seal", "wellows_pickhammer", "yew_longbow",
                            "spell_fireball", "health_potion", "apple_pie",
                            None, None, None],
                    notice="§aWellow's Pickhammer is yours."),
        "caption": "The Arboretum: nine rooted trees and Wellow's Pickhammer.",
    },
    # --- encounters ---------------------------------------------------------
    {
        "id": "15_balverine_night",
        "struct": "witchwood_stones",
        # Close and low, so the balverines read as a threat rather than as two
        # distant silhouettes among the monoliths.
        "eye": (12.5, 2.62, 19.0), "look": (11, 2.2, 13),
        "sky": "NIGHT", "reach": 46,
        "mobs": [("balverine", (10.5, 1, 13), {"scale": 0.082, "yaw": 0.1}),
                 ("white_balverine", (15, 1, 11), {"scale": 0.082, "yaw": -0.7})],
        "hud": dict(place="Witchwood", heading="W", distance=760, hour=0,
                    health=(11, 20), multiplier=4, eye="open",
                    notice="§cBalverine strikes! §7x4"),
        "caption": "A moonlit balverine ambush among the Witchwood stones.",
    },
    {
        "id": "16_fireball_hobbes",
        "struct": "darkwood_camp",
        "eye": (17.0, 2.62, 8.0), "look": (12, 2.2, 13),
        "sky": "OVERCAST", "reach": 44,
        "mobs": [("hobbe", (9, 1, 13), {"yaw": 0.4}),
                 ("hobbe_scout", (15, 1, 10), {"yaw": -0.7}),
                 ("hobbe", (12, 1, 17), {"yaw": 2.2})],
        "effects": ["fireball:13,2.4,13:10,1.2,13"],
        "hud": dict(place="Darkwood", heading="N", distance=512, hour=16,
                    will=(41, 100), multiplier=3, selected=3,
                    notice="§6Fireball — §7-25 Will"),
        "caption": "Fireball bursting over a hobbe pack in Darkwood.",
    },
    {
        "id": "17_twinblade_camp",
        "struct": "bandit_camp",
        # Dead down the camp's axis, so the palisade gate frames Twinblade.
        "eye": (16.0, 2.62, 22.0), "look": (16, 2.3, 11),
        "sky": "GOLDEN", "reach": 52,
        "mobs": [("twinblade", (16, 1, 11), {"scale": 0.085, "yaw": 3.14}),
                 ("bandit", (11, 1, 15), {"yaw": 2.7}),
                 ("bandit_archer", (21, 1, 15), {"yaw": 3.5})],
        "effects": ["slow_time:16,1.4,14,4.5"],
        "hud": dict(place="Twinblade's Camp", heading="N", distance=980, hour=18,
                    health=(9, 20), will=(18, 100), multiplier=6, selected=1,
                    hotbar=["guild_seal", "master_greatsword", "yew_longbow",
                            "spell_slow_time", "health_potion", "apple_pie",
                            None, None, None],
                    notice="§cTwinblade: §7half health"),
        "caption": "Slow Time over Twinblade's war-camp as the Bandit King charges.",
    },
    {
        "id": "18_lychfield_undead",
        "struct": "graveyard",
        "target": (12, 2.0, 18), "distances": (7, 9, 12),
        "sky": "NIGHT", "reach": 44,
        "mobs": [("undead", (12, 1, 20), {"yaw": 3.0}),
                 ("undead_knight", (9, 1, 20), {"yaw": 2.6}),
                 ("hobbe", (16, 1, 18), {"yaw": -0.3})],
        "hud": dict(place="Lychfield", heading="N", distance=1180, hour=1,
                    health=(14, 20), multiplier=2, eye="open",
                    notice="§7Hollow men rise from the plots."),
        "caption": "Hollow men rising in Lychfield graveyard.",
    },
]

# Menu captures reuse a world frame, then lay the pack's own form over it. Titles
# and copy are quoted from fc_strings.js / the form builders in main.js and
# scripts/wd/herobook.js so these show menus the addon really has.
FORMS = [
    {
        "id": "19_hero_menu",
        "base": "03_map_room",
        "kind": "action",
        "title": "§0✦ The Hero's Tale ✦",
        "body": ("§8A chronicle bound in parchment and gold.\n\n"
                 "§aGood §8· §7morality §f+240\n§7Will §976§7/§9100"),
        "buttons": [("The Hero", "sigil_hero"), ("Magic", "sigil_magic"),
                    ("Appearance", "sigil_appearance"), ("Weapons", "sigil_weapons"),
                    ("Inventory", "sigil_inventory"), ("Clothing", "sigil_inventory"),
                    ("Expressions", "sigil_factions"), ("Quests", "sigil_quests"),
                    ("Factions", "sigil_factions"), ("Map of Albion", "sigil_map"),
                    ("Logbook", "sigil_logbook")],
        "hovered": 1, "scroll": 0.0,
        "caption": "The Guild Seal opens the Hero's Tale — eleven storybook pages.",
    },
    {
        "id": "20_cullis_travel",
        "base": "11_cullis_gate",
        "kind": "action",
        "title": "§b◈ Cullis Gate",
        "body": ("§6═══════════\n§7The lattice of Albion bends to your Will.\n"
                 "§7Standing at: §bFocus Site\n§6═══════════"),
        "buttons": [("§bHeroes' Guild\n§80m distant", None),
                    ("§bBowerstone\n§8212m distant", None),
                    ("§bOakvale\n§8486m distant", None),
                    ("§bSnowspire\n§81204m distant", None)],
        "hovered": 0, "scroll": None,
        "height": 196,
        "caption": "Sneak on a gate to open the Cullis travel lattice.",
    },
    {
        "id": "21_arrest_warrant",
        "base": "09_bowerstone_market",
        "kind": "message",
        "title": "§4Bowerstone Watch",
        "body": ('§c"Hold there. You owe 180 gold for 2 deaths."\n\n'
                 "§7Your purse: §62740 gold\n"
                 "§7Pay the warrant, surrender your possessions\n§7and accept exile, or resist arrest."),
        "buttons": ["§6Pay 180 gold", "§8Go to jail", "§4Resist arrest"],
        "hovered": 0,
        "hud": dict(wanted=3, place="Bowerstone", notice="§cWANTED in Bowerstone"),
        "caption": "A warrant in Bowerstone: pay, jail, or resist.",
    },
    {
        "id": "22_logbook",
        "base": "04_guild_library",
        "kind": "action",
        "title": "§0✦ The Logbook ✦",
        "body": ("§8Albion keeps its own account of you.\n\n"
                 "§7Renown §f2,480 §8· §7Title §eHero of Skill\n"
                 "§7Kills §f318 §8· §7Quests §f7§7/§f15"),
        "buttons": [("§bCullis Gates", "sigil_map"), ("Factions & Standing", "sigil_factions"),
                    ("Bounties & Warrants", "sigil_quests"), ("Titles & Renown", "sigil_hero"),
                    ("How Albion Works", "sigil_logbook")],
        "hovered": 2, "scroll": None,
        "height": 202,
        "caption": "The Logbook: factions, bounties, titles and system help.",
    },
]


SKIES = {"DAY": P.DAY, "GOLDEN": P.GOLDEN, "NIGHT": P.NIGHT, "ARCANE": P.ARCANE,
         "OVERCAST": P.OVERCAST, "INDOORS": P.INDOORS, "UNDERGROUND": P.UNDERGROUND}


def slow_time_motes(centre, radius=4.0):
    """Pale, translucent motes hanging in stopped time.

    DOC.slow_time_fx sizes its motes for an isometric plate; at eye height the
    same quads read as sheets of paper. These are smaller, dimmer and kept low
    enough to sit in the scene rather than hover over it.
    """
    from fc_lib import rng
    from gen_screenshots import cube_quads
    r = rng("pov-fx", "slow_time")
    cx, cy, cz = centre
    tex = Image.new("RGBA", (2, 2), (206, 232, 255, 120))
    quads = []
    for i in range(30):
        ang = 2 * math.pi * i / 30 + r.uniform(-0.06, 0.06)
        dist = radius * r.uniform(0.55, 1.0)
        x = cx + math.cos(ang) * dist
        z = cz + math.sin(ang) * dist
        y = cy + r.uniform(-0.3, 1.9)
        size = r.uniform(0.09, 0.17)
        quads += cube_quads((x - size / 2, y, z - size / 2), (size, size, size),
                            (0, 0), tex, glow=True)
    return quads


def build_effects(specs):
    """Expand the compact effect strings into showcase-renderer quads."""
    quads = []
    for spec in specs or ():
        kind, _, rest = spec.partition(":")
        if kind == "holy_glow":
            x, y, z, h = (float(v) for v in rest.split(","))
            quads += DOC.holy_glow_fx((x, y, z), height=h)
        elif kind == "fireball":
            centre, _, target = rest.partition(":")
            cx, cy, cz = (float(v) for v in centre.split(","))
            tx, ty, tz = (float(v) for v in target.split(","))
            quads += DOC.fireball_fx((cx, cy, cz), target=(tx, ty, tz))
        elif kind == "slow_time":
            x, y, z, r = (float(v) for v in rest.split(","))
            quads += slow_time_motes((x, y, z), radius=r)
        else:
            raise ValueError(f"unknown effect: {spec}")
    return quads


def check_items(state):
    """Every hotbar entry must resolve to a real item texture."""
    missing = [i for i in list(state.hotbar) + [state.in_hand()]
               if i and not (HUD.ITEM_TEX / f"{i}.png").exists()]
    if missing:
        raise RuntimeError(f"no item texture for: {', '.join(sorted(set(missing)))}")


def stage(shot):
    """Resolve a shot's camera, either hand-placed or searched for."""
    w = world(shot["struct"])
    if "eye" in shot:
        eye = shot["eye"]
        yaw, pitch = P.look_at(eye, shot["look"])
        return w, P.Camera(pos=eye, yaw=yaw, pitch=pitch, fov=shot.get("fov", 70),
                           size=SIZE)
    found = P.find_viewpoint(w, shot["target"],
                             distances=shot.get("distances", (7, 9, 12)),
                             y_hint=shot.get("y_hint"),
                             pitch_bias=shot.get("pitch_bias", 0.0))
    if found is None:
        raise RuntimeError(f"{shot['id']}: no viewpoint can see {shot['target']}")
    eye, yaw, pitch = found
    return w, P.Camera(pos=eye, yaw=yaw, pitch=pitch, fov=shot.get("fov", 70), size=SIZE)


def render_world(shot):
    w, cam = stage(shot)
    entities = []
    for mob_id, pos, opts in shot.get("mobs", ()):
        entities += DOC.place_mob(mob_id, pos, scale=opts.get("scale", 0.062),
                                  yaw=opts.get("yaw", 0.0))
    entities += build_effects(shot.get("effects"))
    sky = SKIES[shot.get("sky", "DAY")]
    if shot.get("sky_overrides"):
        # Per-shot atmosphere tweaks, for rooms the build genuinely leaves dark.
        sky = dataclasses.replace(sky, **shot["sky_overrides"])
    scene = P.Scene(world=w, cam=cam, sky=sky,
                    reach=shot.get("reach", 56), entities=entities)
    frame = P.render(scene)
    return w, cam, P.vignette(frame, shot.get("vignette", 0.36))


def render_shot(shot):
    w, cam, frame = render_world(shot)
    options = dict(shot.get("hud", {}))
    options.pop("hour_override", None)
    return HUD.compose(frame, hud(**options), world=w, cam=cam)


def render_form(spec, bases):
    base_shot = next(s for s in SHOTS if s["id"] == spec["base"])
    w, cam, frame = bases[spec["base"]]
    options = dict(base_shot.get("hud", {}))
    options.pop("hour_override", None)
    options.update(spec.get("hud", {}))
    options["crosshair"] = False
    options["show_hand"] = False    # an open form puts the item away
    state = hud(**options)
    check_items(state)
    plate = HUD.compose(frame, state, world=w, cam=cam)
    if spec["kind"] == "message":
        return FM.message_form(plate, spec["title"], spec["body"], spec["buttons"],
                               hovered=spec.get("hovered"),
                               height_units=spec.get("height", 126))
    return FM.action_form(plate, spec["title"], spec["body"], spec["buttons"],
                          hovered=spec.get("hovered"), scroll=spec.get("scroll"),
                          height_units=spec.get("height", 196))


INDEX_HEADER = """# Staged captures

Player's-eye frames of Fablecraft: Reforged, at 1280x720.

**These are staged renders, not live captures.** Every frame is drawn by
`scripts/gen_ingame_screenshots.py` through a perspective camera placed inside
the very `.mcstructure` data the behaviour pack ships, wearing the HUD laid out
by `packs/Fablecraft_RP/ui/hud_screen.json`, with menu copy quoted from
`packs/Fablecraft_BP/scripts/fc_strings.js`. They show the addon's real
geometry, real HUD anchors and real menu text from the position a player
occupies — but no Minecraft client produced them, and block surfaces are
generated from the palette rather than sampled from Minecraft's own textures.

The only genuine in-game photographs in this repository are the two files in
[`screenshots/ingame/`](../ingame), which are labelled as such wherever they
appear.

Regenerate with `python scripts/gen_ingame_screenshots.py`.

| Shot | What it shows |
|---|---|
"""


def write_index(rows):
    lines = [INDEX_HEADER]
    for shot_id, caption in rows:
        lines.append(f"| [`{shot_id}.png`]({shot_id}.png) | {caption} |\n")
    (OUT_DIR / "INDEX.md").write_text("".join(lines), encoding="utf-8")


def main(only=None):
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    wanted = set(only or [])
    rows = []
    bases = {}
    needed_bases = {f["base"] for f in FORMS
                    if not wanted or f["id"] in wanted or f["base"] in wanted}

    for shot in SHOTS:
        run = not wanted or shot["id"] in wanted
        if not run and shot["id"] not in needed_bases:
            continue
        start = time.time()
        w, cam, frame = render_world(shot)
        if shot["id"] in needed_bases:
            bases[shot["id"]] = (w, cam, frame)
        if run:
            options = dict(shot.get("hud", {}))
            options.pop("hour_override", None)
            state = hud(**options)
            check_items(state)
            image = HUD.compose(frame, state, world=w, cam=cam)
            path = OUT_DIR / f"{shot['id']}.png"
            image.convert("RGB").save(path)
            print(f"  {shot['id']:<24} {time.time() - start:5.1f}s  -> {path.name}")
        rows.append((shot["id"], shot["caption"]))

    for spec in FORMS:
        if wanted and spec["id"] not in wanted:
            rows.append((spec["id"], spec["caption"]))
            continue
        if spec["base"] not in bases:
            continue
        start = time.time()
        image = render_form(spec, bases)
        path = OUT_DIR / f"{spec['id']}.png"
        image.convert("RGB").save(path)
        print(f"  {spec['id']:<24} {time.time() - start:5.1f}s  -> {path.name}")
        rows.append((spec["id"], spec["caption"]))

    if not wanted:
        rows.sort(key=lambda r: r[0])
        write_index(rows)
        print(f"wrote {OUT_DIR / 'INDEX.md'}")


if __name__ == "__main__":
    main(sys.argv[1:] or None)

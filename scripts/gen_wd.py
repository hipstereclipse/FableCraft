"""gen_wd.py — Will & Destiny (Phase 2) resource generation.

Emits everything the Phase 2 spell/appearance systems consume that is not already
produced by gen_resources.py:

  * per-spell particle effects (charge / cast / impact / sustain stages), all
    tinted at runtime from the spell color via variable.color (neutral sprite).
  * the wd:overlay appearance rig: client entity, geometry, render controllers,
    a morph/halo animation, and the shell / eyes / Will-Lines / body-hair
    textures (RGB baked; alpha keeps the base skin visible underneath).
  * storybook Hero-Menu sigil textures (cosmetic button icons).

The wd:overlay *behavior* entity is hand-authored at
packs/Fablecraft_BP/entities/wd_overlay.json (it carries the wd:* property
declarations); this script only emits the resource-pack side.
"""
from fc_lib import RP, Px, write_json, shade, with_alpha, rng

PARTICLE_SHEET = "textures/particle/particles"

# ---------------------------------------------------------------------------
# Particles — one neutral sprite cell, tinted per cast via variable.color.
# ---------------------------------------------------------------------------

def particle(identifier, *, material="particles_add", radius=0.12, count="2 + variable.intensity * 2",
             life="0.20 + variable.particle_random_1 * 0.25", speed=0.04, drag=0.6,
             direction="outwards", gravity=0.0, size_scale=1.0):
    return {
        "format_version": "1.10.0",
        "particle_effect": {
            "description": {
                "identifier": identifier,
                "basic_render_parameters": {"material": material, "texture": PARTICLE_SHEET},
            },
            "components": {
                "minecraft:emitter_lifetime_once": {"active_time": 0.03},
                "minecraft:emitter_rate_instant": {"num_particles": count},
                "minecraft:emitter_shape_sphere": {"radius": radius, "direction": direction},
                "minecraft:particle_lifetime_expression": {"max_lifetime": life},
                "minecraft:particle_initial_speed": speed,
                "minecraft:particle_motion_dynamic": {
                    "linear_drag_coefficient": drag,
                    "linear_acceleration": [0, gravity, 0],
                },
                "minecraft:particle_appearance_billboard": {
                    "size": [f"variable.size * {size_scale}", f"variable.size * {size_scale}"],
                    "facing_camera_mode": "lookat_xyz",
                    "uv": {"texture_width": 128, "texture_height": 128, "uv": [0, 0], "uv_size": [8, 8]},
                },
                "minecraft:particle_appearance_tinting": {
                    "color": [
                        "variable.color.r",
                        "variable.color.g",
                        "variable.color.b",
                        "variable.color.a * (1.0 - variable.particle_age / variable.particle_lifetime)",
                    ]
                },
            },
        },
    }


# id -> kwargs overrides; each renders a distinct stage for one spell.
SPELL_PARTICLES = {
    "wd:enflame_ring":     dict(material="particles_add", radius=0.05, speed=0.02, drag=0.8, life="0.30 + variable.particle_random_1 * 0.30", size_scale=1.2),
    "wd:enflame_ember":    dict(material="particles_add", radius=0.20, speed=0.10, gravity=-1.2, drag=0.2, life="0.40 + variable.particle_random_1 * 0.40"),
    "wd:lightning_arc":    dict(material="particles_add", radius=0.04, speed=0.0, drag=1.0, life="0.10 + variable.particle_random_1 * 0.06", size_scale=0.8),
    "wd:lightning_spark":  dict(material="particles_add", radius=0.10, speed=0.18, drag=0.4, life="0.18 + variable.particle_random_1 * 0.12"),
    "wd:force_dome":       dict(material="particles_blend", radius=0.06, speed=0.0, drag=1.0, life="0.22 + variable.particle_random_1 * 0.10", size_scale=1.1),
    "wd:force_dust":       dict(material="particles_blend", radius=0.16, speed=0.08, gravity=-0.6, drag=0.5, life="0.45 + variable.particle_random_1 * 0.30"),
    "wd:drain_thread":     dict(material="particles_add", radius=0.04, speed=0.0, drag=1.0, life="0.16 + variable.particle_random_1 * 0.10", size_scale=0.7),
    "wd:drain_mote":       dict(material="particles_add", radius=0.10, speed=0.05, direction="inwards", drag=0.5, life="0.30 + variable.particle_random_1 * 0.20"),
    "wd:heal_mote":        dict(material="particles_add", radius=0.10, speed=0.06, gravity=0.5, drag=0.4, life="0.40 + variable.particle_random_1 * 0.30"),
    "wd:heal_pulse":       dict(material="particles_add", radius=0.05, speed=0.02, drag=0.9, life="0.30 + variable.particle_random_1 * 0.15", size_scale=1.3),
    "wd:shield_hex":       dict(material="particles_blend", radius=0.05, speed=0.0, drag=1.0, life="0.40 + variable.particle_random_1 * 0.20", size_scale=1.0),
    "wd:slowtime_bubble":  dict(material="particles_blend", radius=0.05, speed=0.0, drag=1.0, life="0.50 + variable.particle_random_1 * 0.30", size_scale=1.2),
    "wd:slowtime_glyph":   dict(material="particles_add", radius=0.10, speed=0.01, drag=0.95, life="0.60 + variable.particle_random_1 * 0.40"),
    "wd:rush_streak":      dict(material="particles_add", radius=0.08, speed=0.04, drag=0.6, life="0.28 + variable.particle_random_1 * 0.20"),
    "wd:charge_wave":      dict(material="particles_add", radius=0.12, speed=0.08, drag=0.5, life="0.30 + variable.particle_random_1 * 0.20", size_scale=1.1),
    # --- Phase 3 spells ---
    "wd:summon_sigil":     dict(material="particles_add", radius=0.05, speed=0.0, drag=1.0, life="0.50 + variable.particle_random_1 * 0.30", size_scale=1.2),
    "wd:summon_soul":      dict(material="particles_add", radius=0.12, speed=0.06, gravity=0.6, drag=0.5, life="0.45 + variable.particle_random_1 * 0.35"),
    "wd:charm_tendril":    dict(material="particles_add", radius=0.04, speed=0.0, drag=1.0, life="0.18 + variable.particle_random_1 * 0.12", size_scale=0.7),
    "wd:charm_mote":       dict(material="particles_add", radius=0.12, speed=0.05, gravity=0.3, drag=0.6, life="0.40 + variable.particle_random_1 * 0.30"),
    "wd:ghost_blade":      dict(material="particles_add", radius=0.06, speed=0.04, drag=0.6, life="0.26 + variable.particle_random_1 * 0.18", size_scale=0.9),
    "wd:multi_mote":       dict(material="particles_add", radius=0.14, speed=0.03, drag=0.7, life="0.45 + variable.particle_random_1 * 0.35"),
    "wd:blade_arc":        dict(material="particles_add", radius=0.06, speed=0.05, drag=0.6, life="0.20 + variable.particle_random_1 * 0.14", size_scale=1.0),
    "wd:rage_heat":        dict(material="particles_add", radius=0.16, speed=0.10, gravity=0.8, drag=0.3, life="0.40 + variable.particle_random_1 * 0.30"),
    "wd:radiant_beam":     dict(material="particles_add", radius=0.05, speed=0.0, drag=1.0, life="0.30 + variable.particle_random_1 * 0.20", size_scale=1.1),
    "wd:nether_portal":    dict(material="particles_blend", radius=0.10, speed=0.04, direction="inwards", drag=0.5, life="0.45 + variable.particle_random_1 * 0.30", size_scale=1.2),
}


def emit_particles():
    for identifier, kwargs in SPELL_PARTICLES.items():
        name = identifier.split(":", 1)[1]
        write_json(RP / "particles" / f"wd_{name}.particle.json", particle(identifier, **kwargs))
    return len(SPELL_PARTICLES)


# ---------------------------------------------------------------------------
# Overlay textures — RGB baked; alpha kept moderate so the base skin shows.
# ---------------------------------------------------------------------------

def _tex_skin(evil):
    p = Px(64, 64)
    r = rng("wd_overlay_skin", "evil" if evil else "good")
    if evil:
        base = (28, 10, 10, 150)
        pal = [(46, 14, 14, 150), (20, 8, 8, 160), (70, 22, 18, 140), (12, 6, 6, 170)]
        crack = (255, 96, 40, 190)
    else:
        base = (235, 232, 210, 120)
        pal = [(255, 250, 230, 110), (220, 224, 235, 120), (255, 244, 200, 110), (210, 215, 225, 130)]
        crack = (255, 240, 170, 170)
    p.rect(0, 0, 64, 64, base)
    p.noise_rect(0, 0, 64, 64, pal, r, density=0.7)
    for _ in range(40):
        x, y = r.randrange(64), r.randrange(64)
        p.px(x, y, crack)
    return p


def _tex_eyes():
    p = Px(64, 64)
    glow = (255, 220, 90, 235)
    for cx in (10, 26):
        p.disc(cx, 10, 3, glow)
        p.disc(cx, 10, 1, (255, 255, 240, 255))
    return p


def _tex_will_lines():
    p = Px(64, 64)
    r = rng("wd_overlay", "will_lines")
    line = (120, 200, 255, 230)
    bright = (200, 240, 255, 255)
    for _ in range(26):
        x0, y0 = r.randrange(64), r.randrange(64)
        x1, y1 = x0 + r.randint(-10, 10), y0 + r.randint(-10, 10)
        p.line(x0, y0, x1, y1, line, width=1)
    for _ in range(40):
        p.px(r.randrange(64), r.randrange(64), bright)
    return p


def _tex_body_hair():
    p = Px(64, 64)
    r = rng("wd_overlay", "body_hair")
    dark = (40, 28, 18, 150)
    for _ in range(260):
        p.px(r.randrange(64), r.randrange(64), dark)
    return p


def emit_overlay_textures():
    out = RP / "textures" / "entity" / "wd"
    _tex_skin(True).save(out / "skin_evil.png")
    _tex_skin(False).save(out / "skin_good.png")
    _tex_eyes().save(out / "eyes.png")
    _tex_will_lines().save(out / "will_lines.png")
    _tex_body_hair().save(out / "body_hair.png")
    return 5


# ---------------------------------------------------------------------------
# Overlay geometry — an inflated humanoid shell aligned to the vanilla player
# rig, plus opaque horn/halo bones, eye shells, and Will-Line rune plates.
# ---------------------------------------------------------------------------

def _cube(origin, size, uv=(0, 0), inflate=0.0):
    return {"origin": list(origin), "size": list(size), "uv": list(uv), "inflate": inflate}


def emit_overlay_geometry():
    SHELL = 0.45  # shell inflation over the base skin
    bones = [
        {"name": "root", "pivot": [0, 0, 0]},
        {"name": "shell_body", "parent": "root", "pivot": [0, 24, 0],
         "cubes": [_cube([-4, 12, -2], [8, 12, 4], (16, 16), SHELL)]},
        {"name": "shell_head", "parent": "root", "pivot": [0, 24, 0],
         "cubes": [_cube([-4, 24, -4], [8, 8, 8], (0, 0), SHELL)]},
        {"name": "shell_arm_r", "parent": "shell_body", "pivot": [-5, 22, 0],
         "cubes": [_cube([-8, 12, -2], [4, 12, 4], (40, 16), SHELL)]},
        {"name": "shell_arm_l", "parent": "shell_body", "pivot": [5, 22, 0],
         "cubes": [_cube([4, 12, -2], [4, 12, 4], (40, 16), SHELL)]},
        {"name": "shell_leg_r", "parent": "root", "pivot": [-2, 12, 0],
         "cubes": [_cube([-4, 0, -2], [4, 12, 4], (0, 16), SHELL)]},
        {"name": "shell_leg_l", "parent": "root", "pivot": [2, 12, 0],
         "cubes": [_cube([0, 0, -2], [4, 12, 4], (0, 16), SHELL)]},
        # Opaque ornaments
        {"name": "horn_r", "parent": "shell_head", "pivot": [-3, 32, 0], "rotation": [0, 0, 18],
         "cubes": [_cube([-4.0, 31.5, -1.0], [2, 5, 2], (0, 0))]},
        {"name": "horn_l", "parent": "shell_head", "pivot": [3, 32, 0], "rotation": [0, 0, -18],
         "cubes": [_cube([2.0, 31.5, -1.0], [2, 5, 2], (0, 0))]},
        {"name": "halo", "parent": "shell_head", "pivot": [0, 35, 0],
         "cubes": [_cube([-4, 35, -4], [8, 1, 8], (0, 32))]},
        # Emissive eyes + Will-Lines
        {"name": "eyes", "parent": "shell_head", "pivot": [0, 28, -4],
         "cubes": [_cube([-3.5, 27, -4.6], [7, 2, 1], (0, 0))]},
        {"name": "rune_chest", "parent": "shell_body", "pivot": [0, 18, -2],
         "cubes": [_cube([-4, 13, -2.7], [8, 10, 0], (0, 0))]},
        {"name": "rune_arm_r", "parent": "shell_arm_r", "pivot": [-6, 18, 0],
         "cubes": [_cube([-8.7, 12, -2], [0, 12, 4], (0, 0))]},
        {"name": "rune_arm_l", "parent": "shell_arm_l", "pivot": [6, 18, 0],
         "cubes": [_cube([8.7, 12, -2], [0, 12, 4], (0, 0))]},
        # Physical Shield — a warded sphere shell enclosing the Hero (Phase 3
        # reactive: shown on wd:shield_active, sized by wd:mana_ratio).
        {"name": "shield", "parent": "root", "pivot": [0, 18, 0],
         "cubes": [_cube([-5, 10, -5], [10, 18, 10], (0, 0), 2.0)]},
    ]
    geo = {
        "format_version": "1.12.0",
        "minecraft:geometry": [{
            "description": {
                "identifier": "geometry.wd_overlay",
                "texture_width": 64,
                "texture_height": 64,
                "visible_bounds_width": 4,
                "visible_bounds_height": 5,
                "visible_bounds_offset": [0, 1.5, 0],
            },
            "bones": bones,
        }],
    }
    write_json(RP / "models" / "entity" / "wd_overlay.geo.json", geo)


# ---------------------------------------------------------------------------
# Overlay render controllers — skin chosen by alignment sign; ornament/rune
# visibility gated by the mirrored tier properties.
# ---------------------------------------------------------------------------

def emit_overlay_render_controllers():
    shell = {
        "arrays": {
            "textures": {"Array.skin": ["Texture.skin_good", "Texture.skin_evil"]},
        },
        "geometry": "Geometry.default",
        "materials": [{"*": "Material.shell"}],
        "textures": ["Array.skin[q.property('wd:alignment_tier') < 0 ? 1 : 0]"],
        "part_visibility": [
            {"*": False},
            {"shell_body": "math.abs(q.property('wd:alignment_tier')) >= 1"},
            {"shell_head": "math.abs(q.property('wd:alignment_tier')) >= 1"},
            {"shell_arm_r": "math.abs(q.property('wd:alignment_tier')) >= 1"},
            {"shell_arm_l": "math.abs(q.property('wd:alignment_tier')) >= 1"},
            {"shell_leg_r": "math.abs(q.property('wd:alignment_tier')) >= 2"},
            {"shell_leg_l": "math.abs(q.property('wd:alignment_tier')) >= 2"},
            {"horn_r": "q.property('wd:alignment_tier') <= -2"},
            {"horn_l": "q.property('wd:alignment_tier') <= -2"},
            {"halo": "q.property('wd:alignment_tier') >= 2"},
        ],
    }
    # Will Lines glow with learned Will AND brighten during any cast/charge
    # (q.property('wd:casting_level') > 0) — the Phase 3 reactive flare.
    emissive = {
        "geometry": "Geometry.default",
        "materials": [{"*": "Material.emissive"}],
        "textures": ["Texture.will_lines"],
        "part_visibility": [
            {"*": False},
            {"rune_chest": "q.property('wd:will_tier') >= 1 || q.property('wd:casting_level') > 0"},
            {"rune_arm_r": "q.property('wd:will_tier') >= 3 || q.property('wd:casting_level') > 0"},
            {"rune_arm_l": "q.property('wd:will_tier') >= 3 || q.property('wd:casting_level') > 0"},
        ],
    }
    eyes = {
        "geometry": "Geometry.default",
        "materials": [{"*": "Material.emissive"}],
        "textures": ["Texture.eyes"],
        "part_visibility": [
            {"*": False},
            {"eyes": "math.abs(q.property('wd:alignment_tier')) >= 2 || q.property('wd:casting_level') > 0"},
        ],
    }
    # Physical Shield shell — emissive warded sphere, shown while the shield is up.
    shield = {
        "geometry": "Geometry.default",
        "materials": [{"*": "Material.emissive"}],
        "textures": ["Texture.will_lines"],
        "part_visibility": [
            {"*": False},
            {"shield": "q.property('wd:shield_active')"},
        ],
    }
    write_json(RP / "render_controllers" / "wd_overlay.render_controllers.json", {
        "format_version": "1.10.0",
        "render_controllers": {
            "controller.render.wd_overlay_shell": shell,
            "controller.render.wd_overlay_runes": emissive,
            "controller.render.wd_overlay_eyes": eyes,
            "controller.render.wd_overlay_shield": shield,
        },
    })


def emit_overlay_animation():
    # Physique/height morph via Molang bone-scale; halo float + slow spin. Phase 3
    # reactive layer: a Berserk (gesture 15) size pulse on the body, Will-Line /
    # eye flares that grow with wd:casting_level, and a mana-linked shield shell.
    berserk_pulse = "(q.property('wd:casting') == 15 ? 1.12 + math.sin(q.life_time * 600) * 0.06 : 1)"
    flare = "1 + q.property('wd:casting_level') * 0.22"
    write_json(RP / "animations" / "wd_overlay.animation.json", {
        "format_version": "1.8.0",
        "animations": {
            "animation.wd_overlay.idle": {
                "loop": True,
                "bones": {
                    "shell_body": {
                        "scale": [
                            f"(q.property('wd:morph') ? 1 + q.property('wd:strength_tier') * 0.04 : 1) * {berserk_pulse}",
                            f"(q.property('wd:morph') ? 1 + q.property('wd:skill_tier') * 0.05 : 1) * {berserk_pulse}",
                            f"(q.property('wd:morph') ? 1 + q.property('wd:strength_tier') * 0.04 : 1) * {berserk_pulse}",
                        ],
                    },
                    "halo": {
                        "position": [0, "math.sin(q.life_time * 90) * 0.4", 0],
                        "rotation": [0, "q.life_time * 26", 0],
                    },
                    "eyes": {"scale": flare},
                    "rune_chest": {"scale": flare},
                    "rune_arm_r": {"scale": flare},
                    "rune_arm_l": {"scale": flare},
                    "shield": {
                        "scale": "0.92 + q.property('wd:mana_ratio') * 0.14 + math.sin(q.life_time * 200) * 0.02",
                    },
                },
            },
        },
    })


def emit_overlay_animation_controller():
    write_json(RP / "animation_controllers" / "wd_overlay.ac.json", {
        "format_version": "1.10.0",
        "animation_controllers": {
            "controller.animation.wd_overlay.main": {
                "states": {"default": {"animations": ["idle"]}},
            },
        },
    })


def emit_overlay_client_entity():
    desc = {
        "identifier": "wd:overlay",
        "materials": {"shell": "entity_alphatest", "emissive": "entity_emissive_alpha"},
        "textures": {
            "skin_good": "textures/entity/wd/skin_good",
            "skin_evil": "textures/entity/wd/skin_evil",
            "eyes": "textures/entity/wd/eyes",
            "will_lines": "textures/entity/wd/will_lines",
            "body_hair": "textures/entity/wd/body_hair",
        },
        "geometry": {"default": "geometry.wd_overlay"},
        "render_controllers": [
            "controller.render.wd_overlay_shell",
            "controller.render.wd_overlay_runes",
            "controller.render.wd_overlay_eyes",
            "controller.render.wd_overlay_shield",
        ],
        "animations": {
            "idle": "animation.wd_overlay.idle",
            "ctrl": "controller.animation.wd_overlay.main",
        },
        "scripts": {"animate": ["ctrl"]},
    }
    write_json(RP / "entity" / "wd_overlay.entity.json", {
        "format_version": "1.10.0",
        "minecraft:client_entity": {"description": desc},
    })


def emit_overlay():
    emit_overlay_textures()
    emit_overlay_geometry()
    emit_overlay_render_controllers()
    emit_overlay_animation()
    emit_overlay_animation_controller()
    emit_overlay_client_entity()


# ---------------------------------------------------------------------------
# Storybook Hero-Menu sigils (cosmetic ActionForm button icons).
# ---------------------------------------------------------------------------

SIGILS = {
    "sigil_hero": (210, 180, 90),
    "sigil_magic": (255, 140, 40),
    "sigil_appearance": (180, 130, 220),
    "sigil_weapons": (200, 205, 215),
    "sigil_inventory": (170, 140, 90),
    "sigil_quests": (220, 200, 120),
    "sigil_map": (150, 200, 150),
    "sigil_factions": (200, 90, 90),
    "sigil_logbook": (160, 200, 240),
}


def emit_sigils():
    out = RP / "textures" / "ui" / "wd"
    for name, color in SIGILS.items():
        p = Px(16, 16)
        ring = shade(color + (255,), 0.8)
        face = with_alpha(color, 235)
        p.disc(8, 8, 7, (52, 40, 24, 255))
        p.disc(8, 8, 6, face)
        p.disc(8, 8, 6, with_alpha(ring, 90))
        p.disc(8, 8, 3, with_alpha((255, 248, 220), 230))
        p.outline((30, 20, 12, 255))
        p.save(out / f"{name}.png")
    return len(SIGILS)


def main():
    n_part = emit_particles()
    emit_overlay()
    n_sig = emit_sigils()
    print(f"emitted WD: {n_part} spell particles, overlay rig (geo+rc+anim+6 tex), {n_sig} menu sigils")


if __name__ == "__main__":
    main()

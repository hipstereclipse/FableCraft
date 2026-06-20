# Will & Destiny — Phase 1

## Scope and assumptions

Phase 1 is integrated into the existing Fablecraft packs instead of replacing the current quests, NPCs, structures, and generated assets.

- Target: Minecraft Bedrock 1.21.100.
- Script modules: `@minecraft/server` 2.1.0 and `@minecraft/server-ui` 2.0.0.
- Multiplayer is the default operating mode. Every persistent state document is stored on its owning player.
- Temporary terrain effects are disabled by default.
- Existing `fc_*` morality, XP, Magic Power, mana, and Fireball-level properties remain authoritative during migration. `wd:state` mirrors them so existing worlds retain progression.
- Phase 1 ships Fireball, evil and good auras, plus extreme-alignment horns and halo. Full skin overlays, physique morphs, and remaining spells are Phase 2/3 work.
- Uploaded player skins are never rewritten. Horns and halo use separate cosmetic overlay entities; later appearance work must use slightly inflated overlay geometry and emissive/alpha materials.
- Morph geometry is visible primarily in third person and to other players. First-person horns, halo, skin shells, and runes are not a reliable Bedrock presentation surface.

## Delivered file tree

```text
packs/Fablecraft_BP/
  entities/player.json
  items/will_focus.json
  loot_tables/empty.json
  recipes/will_focus.json
  scripts/main.js
  scripts/wd/
    alignment.js
    auras.js
    config.js
    main.js
    mana.js
    particles.js
    state.js
    stats.js
    ui.js
    visuals.js
    spells/
      fireball.js
      registry.js

packs/Fablecraft_RP/
  animations/wd_player.animation.json
  particles/
    wd_evil_fog.particle.json
    wd_fireball_core.particle.json
    wd_fireball_ember.particle.json
    wd_fireball_glow.particle.json
    wd_fireball_impact_smoke.particle.json
    wd_will_fizzle.particle.json
  textures/item_texture.json
  texts/en_US.lang
```

## Controls

- Use `wd:will_focus`: cast the active attuned Will power.
- Sneak-use `wd:will_focus`: open the three-slot attunement menu.
- Press Sneak + hotbar key 7, 8, or 9 to cast that virtual Will slot without
  replacing the item stored in the corresponding hotbar slot.
- The same attunement screen is available from Guild Seal → Magic → Will Focus.
- Fireball is learned at level 1 when a player's state is first created.
- A focus is granted when the player first loads with the system. It is also craftable from two blaze rods, an amethyst shard, and a Will Shard.

## Persistence schema

All Will & Destiny state is serialized to the player's `wd:state` dynamic string property.

```json
{
  "schemaVersion": 1,
  "alignment": 0,
  "xp": {
    "generic": 0,
    "strength": 0,
    "skill": 0,
    "will": 0
  },
  "attributes": {
    "magicPower": 0
  },
  "mana": {
    "current": 100,
    "max": 100
  },
  "spells": {
    "equipped": "fireball",
    "owned": {
      "fireball": 1
    }
  },
  "options": {
    "allowTerrainEffects": false,
    "auraDensity": 1.0
  }
}
```

`schemaVersion` is mandatory. `state.js` clamps all numeric data and supplies defaults for missing fields. A future migration increments the version and normalizes the old document before saving.

## Client-synced entity properties

The behavior player override is based on Mojang's 1.21.90 player definition, with only these properties added. Resource-pack Molang can read them with `query.property('wd:...')`; client entity JSON does not redeclare behavior entity properties.

| Property | Type/range | Purpose |
|---|---:|---|
| `wd:alignment_tier` | int, -6..6 | Neutral, six evil tiers, or six good tiers |
| `wd:strength_tier` | int, 0..5 | Future body-width/hair geometry selection |
| `wd:skill_tier` | int, 0..5 | Future height/lean geometry selection |
| `wd:will_tier` | int, 0..5 | Future rune/hand/eye overlay selection |
| `wd:casting` | int, 0..18 | Active cast gesture; Fireball is 1 |
| `wd:casting_level` | int, 0..4 | VFX/animation intensity |
| `wd:mana_ratio` | float, 0..1 | Future HUD/material response |
| `wd:shield_active` | bool | Future Physical Shield shell |

Properties are synchronized every 20 ticks, not every tick.

## Alignment tiers and deeds

Tier thresholds are symmetric:

| Magnitude | Tier |
|---:|---:|
| 0..149 | 0 |
| 150..299 | 1 |
| 300..499 | 2 |
| 500..699 | 3 |
| 700..849 | 4 |
| 850..949 | 5 |
| 950..1000 | 6 |

The modular deed table is:

| Deed | Alignment |
|---|---:|
| Kill hostile | +3 |
| Kill boss | +20 |
| Kill villager | -100 |
| Kill iron golem | -75 |
| Kill tamed pet | -60 |
| Eat pure food | +15 |
| Eat vile food | -25 |
| Donate at Altar of Light | +125 |
| Sacrifice at Altar of Shadow | -175 |

The current repository already handles kill and food morality in `scripts/main.js`. With `useLegacyFcProgressionBridge: true`, Phase 1 mirrors those values and does not subscribe a second deed listener. Set the bridge to `false` only after the monolithic handlers have been removed or routed through `wd/alignment.js`.

## Evil aura

`wd:evil_fog` is emitted every 12 ticks. Density scales with the absolute evil tier and is capped at three emitters per player per pass. Each emitter creates a small batch of ground-hugging particles, so the script does not perform entity scans or per-tick particle work.

Color, alpha, size, and intensity are passed through `MolangVariableMap`. The particle uses the vanilla particle atlas, so no binary texture is required for Phase 1.

## Fireball specification

**SPELL: Fireball | family: Attack | alignment lock: none**

- Cast gesture: right-arm charge and forward thrust from `animation.player.wd.fireball_cast`.
- Core: `wd:fireball_core`, orange additive, size 0.44–0.60 by level during flight.
- Glow: `wd:fireball_glow`, gold additive, size 0.78–1.02 during flight.
- Detail: `wd:fireball_ember`, red-orange falling embers.
- Dissipation: `wd:fireball_impact_smoke`, dark warm smoke plus expanding core/glow.
- Sound: `fc.spell_cast` charge, `mob.blaze.shoot` launch, `random.explode` impact.
- Feedback: short positional camera shake on impact.
- Targeting: scripted projectile stepping at 1.15 blocks per tick. Local 1.15-block entity checks avoid a wide dimension scan.
- Multiplayer rule: players and `fc_ally` family entities are excluded from damage.
- Knockback: the compatibility helper first calls the pinned 2.0.0 `VectorXZ` form, then falls back to the older four-argument form. It never uses `applyImpulse` on players.

| Level | Direct damage | Splash damage/radius | Fire | Range | Mana | Cooldown |
|---:|---:|---:|---:|---:|---:|---:|
| 1 | 9 | 4 / 2.5 blocks | 3 s | 18 | 18 | 50 ticks |
| 2 | 13 | 6 / 3.0 blocks | 4 s | 22 | 24 | 46 ticks |
| 3 | 18 | 9 / 3.5 blocks | 5 s | 26 | 31 | 42 ticks |
| 4 | 24 | 12 / 4.0 blocks | 6 s | 30 | 40 | 36 ticks |

When `allowTerrainEffects` is enabled, impact temporarily swaps up to a two-block-radius set of ground blocks to black concrete powder and may place brief fire above them. The original block permutations are restored after 4–8 seconds. Restoration only occurs if the temporary block is still present, so a later player edit is not overwritten.

## Configuration

Edit `packs/Fablecraft_BP/scripts/wd/config.js`.

| Setting | Default | Effect |
|---|---:|---|
| `allowTerrainEffects` | `false` | Enables temporary scorch/fire block changes |
| `auraDensity` | `1.0` | Global multiplier, clamped with player option to 0..2 |
| `auraIntervalTicks` | `12` | Aura cadence |
| `maxAuraEmittersPerPlayer` | `3` | Hard per-pass aura cap |
| `manaRegenIntervalTicks` | `10` | Mana loop cadence |
| `manaRegenPerSecond` | `4` | Base regeneration |
| `grantFocusOnFirstJoin` | `true` | Gives one focus if absent |
| `enableDebugScriptEvents` | `true` | Enables test script events |
| `useLegacyFcProgressionBridge` | `true` | Mirrors existing Fablecraft progression |

## Debug/test script events

Run these as the player being tested:

```text
/scriptevent wd:set_alignment -1000
/scriptevent wd:set_alignment 0
/scriptevent wd:grant_fireball 4
/scriptevent wd:refill_mana
/scriptevent wd:dump
```

## Installation and build

1. Keep the behavior and resource packs paired; their UUID dependency is already configured.
2. Enable the Script API/Beta APIs required by the target Bedrock release.
3. Validate and package:

```powershell
.venv/Scripts/python scripts/build_addon.py
```

Use `--full` only when intentionally regenerating all procedural NPC, item, sound, structure, and screenshot-adjacent assets. `gen_resources.py` preserves the Will Focus atlas/lang entry during a full regeneration.

## Manual test checklist

1. Load an existing world and confirm normal movement, hunger, breathing, riding, raid omen, and death behavior still work with the player override.
2. Confirm one Will Focus appears if the player does not already own one.
3. Sneak-use the focus and verify Fireball level, mana, alignment, equip, and upgrade controls.
4. Cast at open air and verify charge, thrust, core/glow/trail, maximum-range impact, sounds, and camera shake.
5. Cast at a hostile and verify direct damage, splash damage, knockback, and fire.
6. Put another player beside the target and confirm Fireball does not damage that player.
7. Empty mana through repeated casts and verify action-bar, blue fizzle, sound, and no cast.
8. Wait and verify mana regenerates in 10-tick batches.
9. Run `/scriptevent wd:set_alignment -150`, `-500`, and `-1000`; verify fog density increases.
10. Leave terrain effects disabled and verify no blocks change.
11. Temporarily enable terrain effects, impact solid ground, and verify scorch/fire restore without overwriting a manually changed temporary block.
12. Rejoin and run `/scriptevent wd:dump`; verify alignment, XP, mana, spell ownership, and equipped spell persisted.
13. Test with two players at different alignment/mana values to confirm state does not bleed between them.

## Phase 1 optional art build sheet

No binary art is required to run Phase 1. The focus currently aliases the generated Will Shard icon and particles use Mojang's built-in particle atlas.

For a dedicated focus icon:

- File: `packs/Fablecraft_RP/textures/items/will_focus.png`
- Canvas: 32×32 RGBA.
- Silhouette: diagonal dark-oak or obsidian handle from `(5,27)` to `(22,10)`, 4–6 pixels thick.
- Focus crystal: 10×10 diamond centered near `(24,8)`.
- Palette: navy `#14233f`, Will blue `#2f8cff`, emissive highlight `#b8eeff`, warm metal `#a47a36`.
- Alpha: fully transparent background; no semi-transparent edge pixels below alpha 96.
- Atlas change after creation: point `will_focus` to `textures/items/will_focus`.

For replacement custom particle sprites:

- File: `packs/Fablecraft_RP/textures/particle/wd_particles.png`
- Canvas: 64×64 RGBA, four 16×16 cells per row.
- Cell `(0,0)`: soft radial white core, additive.
- Cell `(16,0)`: thin four-point ember, additive.
- Cell `(32,0)`: soft smoke puff, alpha blend.
- Cell `(48,0)`: ragged ground fog puff, alpha blend.
- Keep RGB white/neutral; script tint supplies color.
- Update each particle's texture path, texture dimensions, UV, and UV size together.

## Phase 2 model rule

Do not bake morality or Will effects into a replacement player skin. Horns and halo must be separate opaque bones. Charred/pale skin, eyes, body hair, and runes must be slightly inflated transparent overlay shells so every uploaded skin remains visible underneath.

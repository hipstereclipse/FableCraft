# Ghost Sword and Assassin Rush completion

Implementation choice [B], 2026-09-12: finish the existing floating-companion and
horizontal-dash work. These are Bedrock adaptations, not verified 1:1 TLC timings.

Ghost Sword maintains one particle blade per player. Recasting replaces it and
renews its lifetime (levels 1–4: 10/14/18/22 seconds). Damage is 4/5/6/7 per hit,
at least 12 ticks apart, credited to the caster's Will damage. Target selection
uses the existing ally/player/Turncoat exclusion. The owner bounds its search
radius; changing dimension or teleporting beyond its leash reseats it. Death,
respawn, departure and expiry clear it. Unreadable blocks and walls stop movement
and strikes. It does not pathfind around obstacles. Particle artwork is existing
original pack artwork; no new generated entity is required.

Assassin Rush follows horizontal facing, including a yaw fallback when looking
straight up/down. It checks the player's width and height along quarter-block
steps, steps up at most one full block and down at most three per sample, stops
at walls/deep ledges/liquids/unreadable terrain, and uses a checked `tryTeleport`.
It preserves camera direction and clears velocity. No movement or rejected
teleport returns false to the shared cast pipeline, without a speed buff.
Clearance is conservative around plants, slabs, stairs and other partial blocks;
the engine performs the final collision check. This is not continuous physics.

## Automated evidence

- `node --experimental-vm-modules scripts/tests/spells.test.mjs`: 17 boundary-mocked tests.
- `python scripts/build_addon.py`: asset, expression and HUD checks + local package.
- `npx --no-install eslint packs/Fablecraft_BP/scripts`: zero errors; existing unused-code warnings remain.
- Logs: `screenshots/validation/spells/`. These logs are not in-game screenshots.

To make the requested lint validator runnable, this change also adds ESLint's
flat configuration and reproducible npm dependencies. Empty catches remain
allowed because Bedrock entity handles can expire between operations. Actual
errors were repaired: an unreachable retired HUD loop referenced deleted state,
redundant initial assignments, an intentionally drained generator loop, and a
Physical Shield refund expression whose operator precedence could produce NaN.
No runtime-error rules have been disabled.

## Manual checklist — PENDING, requires Bedrock 1.21.100+ / server API 2.1.0

Use a disposable world with both packs installed and Content Log enabled.

- [ ] Learn/equip Ghost Sword with Will Focus; cast all four charge levels. Blade
      silhouette, orientation, flourish and sound are readable in first/third person.
- [ ] A blade follows at rest, pursues nearby enemies, damages on cooldown, expires
      on schedule and does not multiply after repeated casts.
- [ ] Test two players, allies, summoned/charmed creatures, a foe behind a wall,
      an unloaded boundary and a foe beyond owner range; no friendly/remote hits.
- [ ] Change dimensions, teleport far, die/respawn, leave/rejoin and reload the world;
      no stale blade, damage source or script error survives.
- [ ] Rush facing level/up/down; camera remains unchanged and range scales 8/11/14/16.
- [ ] Rush against a wall, corner, low ceiling, step, staircase, slab, plant,
      shallow descent, cliff, water/lava and chunk boundary; no embedding or launch.
- [ ] Blocked/failed casts refund through the cast pipeline; successful ones consume
      mana once. Check cooldowns, Will XP attribution and Physical Shield refund.
- [ ] Confirm spells, HUD, Guild spawning, NPC reactions and other powers still load.

The mock tests exercise actual script modules but cannot establish engine event
ordering, collision shapes, particle quality or controller support. No in-game
pass or visual conformance grade is claimed.

API references consulted 2026-09-12:
[Entity.tryTeleport](https://learn.microsoft.com/en-us/minecraft/creator/scriptapi/minecraft/server/entity?view=minecraft-bedrock-stable),
[TeleportOptions](https://learn.microsoft.com/en-us/minecraft/creator/scriptapi/minecraft/server/teleportoptions?view=minecraft-bedrock-stable),
[Block](https://learn.microsoft.com/en-us/minecraft/creator/scriptapi/minecraft/server/block?view=minecraft-bedrock-stable),
[ESLint migration](https://eslint.org/docs/latest/use/configure/migration-guide).

// Will & Destiny combat hooks (Phase 3, spec §3.3). Read-only listeners that
// Multi Arrow and Multi Strike arm with a short window; the player's own bow
// shots and melee blows are then augmented. These are purely additive: the
// legacy sneak-hotbar cast path was removed in Phase 2 and the monolith's
// SPELL_BOOK is unreachable to players, so there is no double-application. The
// extra arrows/blows are produced with applyDamage / tagged spawns that never
// re-enter these handlers (no recursion).
import { world, system, EntityDamageCause } from "@minecraft/server";
import { viewDirection } from "./spells/shared/targeting.js";
import { tint, burst } from "./spells/shared/vfx.js";

const SPLIT_TAG = "wd_split";

// playerId -> { shots, fan, expires } / { blows, bonus, expires }
const arrowWindows = new Map();
const strikeWindows = new Map();

export function armMultiArrow(player, shots, fan, durationTicks) {
  arrowWindows.set(player.id, { shots, fan, expires: system.currentTick + durationTicks });
}

export function armMultiStrike(player, blows, bonus, durationTicks) {
  strikeWindows.set(player.id, { blows, bonus, expires: system.currentTick + durationTicks });
}

function projectileOwner(projectile) {
  try {
    return projectile.getComponent("minecraft:projectile")?.owner;
  } catch {
    return undefined;
  }
}

// Multi Arrow — split the next bow shots into a fan around the shooter's aim.
world.afterEvents.entitySpawn.subscribe((event) => {
  const arrow = event.entity;
  if (!arrow?.isValid || arrow.typeId !== "minecraft:arrow") return;
  try {
    if (arrow.hasTag(SPLIT_TAG)) return; // never split an arrow we ourselves spawned
  } catch {
    return;
  }
  const owner = projectileOwner(arrow);
  if (!owner || owner.typeId !== "minecraft:player") return;
  const win = arrowWindows.get(owner.id);
  if (!win || system.currentTick > win.expires) {
    arrowWindows.delete(owner.id);
    return;
  }
  win.shots -= 1;
  if (win.shots <= 0) arrowWindows.delete(owner.id);

  const dir = viewDirection(owner);
  const origin = { x: arrow.location.x, y: arrow.location.y, z: arrow.location.z };
  const fan = win.fan;
  // Spawn the extras next tick so the original shot's components have settled.
  system.run(() => {
    for (let i = 1; i <= fan; i++) {
      const side = (i % 2 === 0 ? 1 : -1) * Math.ceil(i / 2);
      const spread = side * 0.14;
      let extra;
      try {
        extra = owner.dimension.spawnEntity("minecraft:arrow", origin);
      } catch {
        continue; // an extra arrow is a bonus; a failure just means fewer arrows
      }
      try {
        extra.addTag(SPLIT_TAG);
        const proj = extra.getComponent("minecraft:projectile");
        if (proj) {
          proj.owner = owner;
          proj.shoot({ x: (dir.x - dir.z * spread) * 2.6, y: dir.y * 2.6 + 0.05, z: (dir.z + dir.x * spread) * 2.6 });
        }
      } catch {
        // The extra exists but could not be aimed; harmless.
      }
    }
  });
});

// Multi Strike — the next melee blows land extra ghosted hits.
world.afterEvents.entityHitEntity.subscribe((event) => {
  const player = event.damagingEntity;
  const victim = event.hitEntity;
  if (!player || player.typeId !== "minecraft:player" || !victim?.isValid) return;
  const win = strikeWindows.get(player.id);
  if (!win || system.currentTick > win.expires) {
    strikeWindows.delete(player.id);
    return;
  }
  win.blows -= 1;
  if (win.blows <= 0) strikeWindows.delete(player.id);

  const bonus = win.bonus;
  // Two ghosted follow-up strikes; applyDamage does not re-enter this handler.
  for (let n = 1; n <= 2; n++) {
    system.runTimeout(() => {
      if (!victim.isValid) return;
      try {
        victim.applyDamage(bonus, { cause: EntityDamageCause.entityAttack, damagingEntity: player });
        burst(victim.dimension, "wd:blade_arc",
          { x: victim.location.x, y: victim.location.y + 1, z: victim.location.z }, [255, 200, 90], 4, 0.6, 0.6, 1, 0.95);
      } catch {
        // A failed follow-up just lands fewer blows.
      }
    }, n * 3);
  }
  tint(victim.dimension, "wd:blade_arc", { x: victim.location.x, y: victim.location.y + 1, z: victim.location.z }, [255, 200, 90], 0.7, 1, 0.95);
});

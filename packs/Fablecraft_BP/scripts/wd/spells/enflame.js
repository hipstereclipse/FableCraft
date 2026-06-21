// Enflame — Surround. A wave of fire around the Hero that knocks targets down;
// larger radius per level. Charge = fire coalesces at the feet; release = a fast
// expanding ground fire-ring + upward flame burst; impact = embers + brief burn.
import { system, EntityDamageCause } from "@minecraft/server";
import { applyAroundCaster } from "./shared/aoe.js";
import { damageEnemy, igniteEnemy } from "./shared/combat.js";
import { knockbackFrom } from "./shared/knockback.js";
import { applyEffect } from "./shared/selfbuff.js";
import { tint, ring, burst, cameraShake, dimensionSound } from "./shared/vfx.js";

const RADIUS = [0, 3, 4, 5, 6];
const DAMAGE = [0, 4, 7, 10, 12];
const BURN = [0, 2, 3, 4, 5];

function feet(player) {
  return { x: player.location.x, y: player.location.y + 0.1, z: player.location.z };
}

export function enflameCast(ctx) {
  const { player, level, spell } = ctx;
  const center = feet(player);
  const radius = RADIUS[level];

  // Charge: fire coalesces at the feet, ground glows.
  burst(player.dimension, "wd:enflame_ember", center, spell.color, 6 + level * 2, 1.2, 0.4, level / 4, 0.9);
  dimensionSound(player.dimension, "fc.spell_cast", center, { volume: 0.7, pitch: 0.8 });

  // Release: expanding ground fire-ring over a few ticks + an upward burst.
  const steps = 4;
  for (let s = 0; s < steps; s++) {
    system.runTimeout(() => {
      if (!player.isValid) return;
      const r = (radius * (s + 1)) / steps;
      ring(player.dimension, feet(player), r, Math.round(8 + r * 3), (loc) => {
        tint(player.dimension, "wd:enflame_ring", loc, spell.color, 0.7 + level * 0.1, level / 4, 0.85);
      });
    }, s * 2);
  }
  for (let i = 0; i < 3 + level; i++) {
    const up = { x: center.x, y: center.y + 0.5 + i * 0.4, z: center.z };
    tint(player.dimension, "wd:enflame_ring", up, spell.color, 0.9, level / 4, 0.8);
  }
  cameraShake(player, 0.06 + level * 0.02, 0.2);
  dimensionSound(player.dimension, "mob.ghast.fireball", center, { volume: 0.8, pitch: 1.1 });

  // Impact: damage, ignite, and a knock-down pop on each caught enemy.
  applyAroundCaster(player, radius, (entity) => {
    damageEnemy(player, entity, DAMAGE[level], EntityDamageCause.fire);
    igniteEnemy(entity, BURN[level]);
    knockbackFrom(entity, center, 0.5 + level * 0.12, 0.42 + level * 0.05);
    applyEffect(entity, "slowness", 12 + level * 4, 1);
  });
  return true;
}

// Force Push — Surround. A blast of energy radiating from the caster sending
// enemies sprawling. Charge = a pressure ring tightens inward; release = a
// translucent shock dome snaps outward with a dust ring; impact = enemies flung.
import { system, EntityDamageCause } from "@minecraft/server";
import { applyAroundCaster } from "./shared/aoe.js";
import { damageEnemy } from "./shared/combat.js";
import { knockbackFrom } from "./shared/knockback.js";
import { tint, ring, cameraShake, dimensionSound } from "./shared/vfx.js";

const RADIUS = [0, 4, 5.5, 7, 8];
const IMPULSE = [0, 1.0, 1.25, 1.45, 1.6];

function origin(player) {
  return { x: player.location.x, y: player.location.y + 0.9, z: player.location.z };
}

export function forcePushCast(ctx) {
  const { player, level, spell } = ctx;
  const radius = RADIUS[level];

  // Charge: a faint pressure ring tightens inward.
  for (let s = 0; s < 3; s++) {
    system.runTimeout(() => {
      if (!player.isValid) return;
      const r = radius * (1 - s / 4);
      ring(player.dimension, origin(player), r, 14, (loc) => {
        tint(player.dimension, "wd:force_dust", loc, spell.color, 0.4, level / 4, 0.5);
      });
    }, s * 2);
  }

  system.runTimeout(() => {
    if (!player.isValid) return;
    // Release: shock dome + dust ring.
    const o = origin(player);
    for (let yi = 0; yi <= 3; yi++) {
      const r = radius * (1 - yi * 0.18);
      ring(player.dimension, { x: o.x, y: o.y + yi * 0.5, z: o.z }, r, Math.round(10 + r * 2), (loc) => {
        tint(player.dimension, "wd:force_dome", loc, spell.color, 0.6 + level * 0.06, level / 4, 0.55);
      });
    }
    ring(player.dimension, { x: o.x, y: player.location.y + 0.1, z: o.z }, radius, Math.round(12 + radius * 2), (loc) => {
      tint(player.dimension, "wd:force_dust", loc, spell.color, 0.7, level / 4, 0.5);
    });
    cameraShake(player, 0.07 + level * 0.02, 0.18);
    dimensionSound(player.dimension, "mob.warden.sonic_boom", o, { volume: 0.4, pitch: 1.4 });

    // Impact: fling non-ally entities outward. Players are excluded upstream.
    applyAroundCaster(player, radius, (entity) => {
      knockbackFrom(entity, o, IMPULSE[level], 0.45 + level * 0.05);
      damageEnemy(player, entity, 1 + level, EntityDamageCause.entityAttack);
    });
  }, 6);
  return true;
}

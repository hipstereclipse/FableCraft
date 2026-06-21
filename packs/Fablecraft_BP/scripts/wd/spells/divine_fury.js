// Divine Fury — Attack (good, cheaper-when-good capstone). White-hot pillars of
// godly fury descend on every foe within a radius. The alignment cost discount
// is handled by the cast gate (alignCost +1); this body gathers light overhead,
// drops a radiant column on each target, and sears it. VFX markers are capped
// per cast so a large area never spikes the tick.
import { EntityDamageCause } from "@minecraft/server";
import { enemiesNear } from "./shared/targeting.js";
import { drawColumn } from "./shared/beam.js";
import { damageEnemy } from "./shared/combat.js";
import { tint, burst, cameraShake, dimensionSound } from "./shared/vfx.js";
import { WD_CONFIG } from "../config.js";

const RADIUS = [0, 6, 7, 8, 9];
const DAMAGE = [0, 9, 12, 15, 18];

export function divineFuryCast(ctx) {
  const { player, level, spell } = ctx;
  const center = { x: player.location.x, y: player.location.y, z: player.location.z };

  // Charge: light gathers overhead and the Will Lines blaze.
  burst(player.dimension, "wd:radiant_beam",
    { x: center.x, y: center.y + 2.6, z: center.z }, spell.color, 8 + level * 2, 1.0, 0.7, level / 4, 0.95);
  dimensionSound(player.dimension, "beacon.activate", center, { volume: 0.7, pitch: 1.15 });

  const markerCap = Math.max(1, WD_CONFIG.maxVfxMarkersPerCast ?? 8);
  let pillars = 0;
  for (const enemy of enemiesNear(player, center, RADIUS[level])) {
    damageEnemy(player, enemy, DAMAGE[level], EntityDamageCause.magic);
    if (pillars < markerCap) {
      pillars++;
      const base = { x: enemy.location.x, y: enemy.location.y, z: enemy.location.z };
      drawColumn(base, 6, (point) => tint(player.dimension, "wd:radiant_beam", point, spell.color, 0.6 + level * 0.06, level / 4, 0.95), { spacing: 0.4 });
      burst(player.dimension, "wd:radiant_beam", { x: base.x, y: base.y + 1, z: base.z }, spell.color, 4 + level, 0.7, 0.6, level / 4, 0.95);
    }
  }
  cameraShake(player, 0.06 + level * 0.02, 0.3);
  return true;
}

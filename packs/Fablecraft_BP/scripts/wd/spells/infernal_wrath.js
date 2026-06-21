// Infernal Wrath — Attack (evil, cheaper-when-evil capstone). Nether vortices
// tear open beneath each victim, draining life into the underworld. The cost
// discount is handled by the cast gate (alignCost -1); this body opens a shadow
// portal under each foe, withers it, and roots it briefly. VFX markers capped
// per cast.
import { EntityDamageCause } from "@minecraft/server";
import { enemiesNear } from "./shared/targeting.js";
import { drawColumn } from "./shared/beam.js";
import { damageEnemy } from "./shared/combat.js";
import { applyEffect } from "./shared/selfbuff.js";
import { tint, burst, cameraShake, dimensionSound } from "./shared/vfx.js";
import { changeAlignment } from "../alignment.js";
import { WD_CONFIG } from "../config.js";

const RADIUS = [0, 6, 7, 8, 9];
const DAMAGE = [0, 9, 12, 15, 18];

export function infernalWrathCast(ctx) {
  const { player, level, spell } = ctx;
  const center = { x: player.location.x, y: player.location.y, z: player.location.z };

  // Charge: the ground darkens and shadow gathers.
  burst(player.dimension, "wd:nether_portal",
    { x: center.x, y: center.y + 0.2, z: center.z }, spell.color, 8 + level * 2, 1.2, 0.7, level / 4, 0.9);
  dimensionSound(player.dimension, "mob.wither.shoot", center, { volume: 0.6, pitch: 0.7 });

  const markerCap = Math.max(1, WD_CONFIG.maxVfxMarkersPerCast ?? 8);
  let portals = 0;
  for (const enemy of enemiesNear(player, center, RADIUS[level])) {
    damageEnemy(player, enemy, DAMAGE[level], EntityDamageCause.magic);
    applyEffect(enemy, "wither", 80, 1, true);
    applyEffect(enemy, "slowness", 40, 3); // dragged / rooted
    if (portals < markerCap) {
      portals++;
      const base = { x: enemy.location.x, y: enemy.location.y, z: enemy.location.z };
      // A vortex column rising out of the portal beneath the victim.
      drawColumn(base, 3, (point) => tint(player.dimension, "wd:nether_portal", point, spell.color, 0.6 + level * 0.06, level / 4, 0.92), { spacing: 0.35 });
      burst(player.dimension, "wd:nether_portal", { x: base.x, y: base.y + 0.1, z: base.z }, spell.color, 5 + level, 0.8, 0.7, level / 4, 0.92);
    }
  }
  cameraShake(player, 0.06 + level * 0.02, 0.35);
  // Evil deed — reinforces the dark lock (faithful to the legacy -5 morality).
  changeAlignment(player, -3, false);
  return true;
}

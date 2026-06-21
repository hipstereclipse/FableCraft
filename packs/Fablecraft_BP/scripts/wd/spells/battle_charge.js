// Battle Charge — Attack. Propels the caster forward at great speed, smashing
// into and blasting aside anything in the path. Charge = the body winds up
// wreathed in amber motion energy; release = a motion-blur streak with a leading
// bow wave; impact = dust/crack along the path + a burst on each enemy hit.
import { system, EntityDamageCause } from "@minecraft/server";
import { normalize, enemiesNear } from "./shared/targeting.js";
import { damageEnemy } from "./shared/combat.js";
import { knockbackAlong } from "./shared/knockback.js";
import { tint, burst, cameraShake, dimensionSound } from "./shared/vfx.js";

const DISTANCE = [0, 5, 6.5, 8, 9];
const DAMAGE = [0, 4, 7, 10, 12];

export function battleChargeCast(ctx) {
  const { player, level, spell } = ctx;
  const view = player.getViewDirection();
  const dir = normalize({ x: view.x, y: 0, z: view.z });

  burst(player.dimension, "wd:charge_wave", { x: player.location.x, y: player.location.y + 1, z: player.location.z },
    spell.color, 6 + level * 2, 1.0, 0.6, level / 4, 0.8);
  dimensionSound(player.dimension, "fc.spell_cast", player.location, { volume: 0.8, pitch: 0.7 });
  cameraShake(player, 0.05 + level * 0.02, 0.25);

  const struck = new Set();
  const steps = Math.max(4, Math.round(DISTANCE[level]));
  let step = 0;

  const advance = () => {
    if (!player.isValid || step++ >= steps) return;
    const here = player.location;
    const next = { x: here.x + dir.x, y: here.y, z: here.z + dir.z };
    let blocked = false;
    try {
      const block = player.dimension.getBlock({ x: Math.floor(next.x), y: Math.floor(next.y), z: Math.floor(next.z) });
      blocked = block && !block.isAir && !block.isLiquid;
    } catch {
      blocked = false;
    }
    if (!blocked) {
      try {
        player.teleport(next);
      } catch {
        // Stop the dash on a teleport failure.
      }
    }
    const at = player.location;
    tint(player.dimension, "wd:charge_wave", { x: at.x, y: at.y + 1, z: at.z }, spell.color, 0.8 + level * 0.08, level / 4, 0.75);
    for (const entity of enemiesNear(player, { x: at.x, y: at.y + 0.5, z: at.z }, 2.2)) {
      if (struck.has(entity.id)) continue;
      struck.add(entity.id);
      damageEnemy(player, entity, DAMAGE[level], EntityDamageCause.entityAttack);
      knockbackAlong(entity, dir, 1.1 + level * 0.2, 0.4);
      burst(player.dimension, "wd:charge_wave", entity.location, spell.color, 4 + level, 0.8, 0.5, level / 4, 0.85);
    }
    if (blocked) return;
    system.run(advance);
  };
  advance();
  return true;
}

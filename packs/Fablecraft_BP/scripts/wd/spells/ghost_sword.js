// Ghost Sword — Physical. Summons a volley of ethereal blades that streak toward
// nearby foes; their number and bite grow with charge level. Implemented as a
// fan of stepping spectral projectiles (reusing projectile.js) aimed at the
// nearest enemies — no new entity, and ally-safe because projectile.js only
// strikes valid targets from targeting.js.
import { EntityDamageCause } from "@minecraft/server";
import { add, headLocation, viewDirection, normalize, enemiesNear, nearestEnemy } from "./shared/targeting.js";
import { fireProjectile } from "./shared/projectile.js";
import { damageEnemy } from "./shared/combat.js";
import { tint, burst, dimensionSound } from "./shared/vfx.js";

const BLADES = [0, 3, 4, 5, 6];
const DAMAGE = [0, 4, 5, 6, 7];
const RANGE = [0, 14, 16, 18, 20];

export function ghostSwordCast(ctx) {
  const { player, level, spell } = ctx;
  const origin = add(headLocation(player), viewDirection(player), 0.6);
  const forward = viewDirection(player);

  // Pick a spread of nearby foes so the volley reads as "homing"; fall back to
  // the look direction when nothing is in range.
  const foes = enemiesNear(player, add(headLocation(player), forward, RANGE[level] * 0.5), RANGE[level]);
  burst(player.dimension, "wd:ghost_blade", origin, spell.color, 6 + level, 0.6, 0.6, level / 4, 0.9);
  dimensionSound(player.dimension, "item.trident.throw", player.location, { volume: 0.6, pitch: 1.4 });

  const count = BLADES[level];
  for (let i = 0; i < count; i++) {
    const foe = foes[i] ?? nearestEnemy(player, add(headLocation(player), forward, RANGE[level] * 0.5), RANGE[level]);
    let direction;
    if (foe?.isValid) {
      direction = normalize({
        x: foe.location.x - origin.x,
        y: (foe.location.y + 1) - origin.y,
        z: foe.location.z - origin.z,
      });
    } else {
      const fan = (i - (count - 1) / 2) * 0.12;
      direction = normalize({ x: forward.x + fan, y: forward.y, z: forward.z - fan });
    }
    fireProjectile(player, {
      direction,
      range: RANGE[level],
      onStep: (loc) => tint(player.dimension, "wd:ghost_blade", loc, spell.color, 0.5 + level * 0.05, level / 4, 0.9),
      onImpact: (loc, hitEntity) => {
        burst(player.dimension, "wd:ghost_blade", loc, spell.color, 4 + level, 0.7, 0.5, level / 4, 0.95);
        if (hitEntity) damageEnemy(player, hitEntity, DAMAGE[level], EntityDamageCause.magic);
      },
    });
  }
  return true;
}

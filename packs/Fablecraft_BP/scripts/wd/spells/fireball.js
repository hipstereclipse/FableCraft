// Fireball — Attack. A sphere of flame formed in the palm and hurled; charges
// into a bigger, more explosive ball. Refactored onto the shared pipeline with
// no behavior change (charge stage now scales the palm-gather and explosion).
import { system, EntityDamageCause } from "@minecraft/server";
import { add, headLocation, viewDirection } from "./shared/targeting.js";
import { fireProjectile } from "./shared/projectile.js";
import { applyRadius } from "./shared/aoe.js";
import { damageEnemy, igniteEnemy } from "./shared/combat.js";
import { knockbackFrom } from "./shared/knockback.js";
import { tint, cameraShake, dimensionSound } from "./shared/vfx.js";

const DAMAGE = [0, 9, 13, 18, 24];
const SPLASH = [0, 4, 6, 9, 12];
const RADIUS = [0, 2.5, 3.0, 3.5, 4.0];
const FIRE_SECONDS = [0, 3, 4, 5, 6];
const RANGE = [0, 18, 22, 26, 30];

const ORANGE = [255, 64, 4];
const GOLD = [255, 174, 20];
const EMBER = [255, 20, 3];
const SMOKE = [40, 18, 11];

function impact(player, location, level, directTarget) {
  const dimension = player.dimension;
  tint(dimension, "wd:fireball_core", location, ORANGE, 1.15 + level * 0.14, level / 4);
  tint(dimension, "wd:fireball_glow", location, GOLD, 1.8 + level * 0.22, level / 4, 0.82);
  tint(dimension, "wd:fireball_impact_smoke", location, SMOKE, 0.8 + level * 0.12, level / 4, 0.62);
  dimensionSound(dimension, "random.explode", location, { volume: 0.75, pitch: 1.05 - level * 0.05 });
  cameraShake(player, 0.08 + level * 0.035, 0.22);

  applyRadius(player, location, RADIUS[level], (entity) => {
    const direct = directTarget && entity.id === directTarget.id;
    damageEnemy(player, entity, direct ? DAMAGE[level] : SPLASH[level], EntityDamageCause.fire);
    igniteEnemy(entity, direct ? FIRE_SECONDS[level] : Math.max(2, FIRE_SECONDS[level] - 1));
    knockbackFrom(entity, location, 0.8 + level * 0.25, 0.18 + level * 0.04);
  });
}

export function fireballCast(ctx) {
  const { player, level } = ctx;
  const direction = viewDirection(player);

  // Charge stage: flame gathers in the palm, scaling with charge level.
  for (let i = 0; i < 3; i++) {
    system.runTimeout(() => {
      if (!player.isValid) return;
      const hand = add(headLocation(player), direction, 0.65 + i * 0.08);
      hand.y -= 0.45;
      tint(player.dimension, "wd:fireball_core", hand, ORANGE, 0.22 + i * 0.05 + level * 0.04, level / 4);
      tint(player.dimension, "wd:fireball_glow", hand, GOLD, 0.46 + i * 0.08 + level * 0.05, level / 4, 0.82);
    }, i * 2);
  }

  system.runTimeout(() => {
    if (!player.isValid) return;
    try {
      player.playSound("mob.blaze.shoot", { volume: 0.8, pitch: 1.05 });
    } catch {
      // The cast still proceeds without the cue.
    }
    fireProjectile(player, {
      direction,
      range: RANGE[level],
      onStep: (loc) => {
        tint(player.dimension, "wd:fireball_core", loc, ORANGE, 0.38 + level * 0.06, level / 4);
        tint(player.dimension, "wd:fireball_glow", loc, GOLD, 0.7 + level * 0.08, level / 4, 0.82);
        tint(player.dimension, "wd:fireball_ember", loc, EMBER, 0.16 + level * 0.02, level / 4, 0.9);
      },
      onImpact: (loc, hitEntity) => impact(player, loc, level, hitEntity),
    });
  }, 6);
  return true;
}

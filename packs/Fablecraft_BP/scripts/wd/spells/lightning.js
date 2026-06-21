// Lightning — Attack. An arc of pure energy leaping from the fingertips to the
// target; higher charge chains to nearby foes. Charge = sparks at the hand;
// release = a jagged forking beam; impact = electrified flash + chain arcs.
import { EntityDamageCause } from "@minecraft/server";
import { add, headLocation, viewDirection, lookedAtEnemy, nearestEnemy, enemiesNear, distanceSquared } from "./shared/targeting.js";
import { drawBeam } from "./shared/beam.js";
import { damageEnemy } from "./shared/combat.js";
import { tint, burst, dimensionSound } from "./shared/vfx.js";

const RANGE = [0, 14, 18, 21, 24];
const DAMAGE = [0, 6, 9, 12, 14];
const CHAINS = [0, 1, 2, 3, 4];

function strike(player, from, target, color, level, damage) {
  const to = add(target.getHeadLocation?.() ?? target.location, { x: 0, y: 0.4, z: 0 }, 1);
  drawBeam(from, to, (point) => {
    tint(player.dimension, "wd:lightning_arc", point, color, 0.5 + level * 0.06, level / 4, 0.95);
  }, { spacing: 0.5, jitter: 0.35 });
  burst(player.dimension, "wd:lightning_spark", target.location, color, 4 + level, 0.8, 0.4, level / 4, 0.9);
  damageEnemy(player, target, damage, EntityDamageCause.lightning);
  dimensionSound(player.dimension, "ambient.weather.thunder", target.location, { volume: 0.5, pitch: 1.6 });
}

export function lightningCast(ctx) {
  const { player, level, spell } = ctx;
  const hand = add(headLocation(player), viewDirection(player), 0.6);

  // Charge: sparks crackle around the hand.
  burst(player.dimension, "wd:lightning_spark", hand, spell.color, 5 + level, 0.5, 0.35, level / 4, 0.9);
  try {
    player.playSound("ambient.weather.lightning.impact", { volume: 0.4, pitch: 1.4 });
  } catch {
    // Audio is additive.
  }

  const primary = lookedAtEnemy(player, RANGE[level]) ?? nearestEnemy(player, add(headLocation(player), viewDirection(player), RANGE[level] * 0.5), RANGE[level] * 0.6);
  if (!primary) {
    // No target: still arc forward as a visible bolt so the cast reads.
    const end = add(headLocation(player), viewDirection(player), RANGE[level]);
    drawBeam(hand, end, (point) => tint(player.dimension, "wd:lightning_arc", point, spell.color, 0.5, level / 4, 0.9), { spacing: 0.5, jitter: 0.35 });
    return true;
  }

  strike(player, hand, primary, spell.color, level, DAMAGE[level]);

  // Chain arcs to nearby foes (count scales with charge level).
  const struck = new Set([primary.id]);
  let source = primary;
  for (let c = 0; c < CHAINS[level]; c++) {
    const candidates = enemiesNear(player, source.location, 6)
      .filter((e) => !struck.has(e.id))
      .sort((a, b) => distanceSquared(a.location, source.location) - distanceSquared(b.location, source.location));
    const next = candidates[0];
    if (!next) break;
    strike(player, add(source.location, { x: 0, y: 1, z: 0 }, 1), next, spell.color, level, Math.max(3, DAMAGE[level] - 2));
    struck.add(next.id);
    source = next;
  }
  return true;
}

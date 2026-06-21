// Assassin Rush — Physical. Blink through space; with a target, appear behind
// it instantly. Cast = the caster dissolves into a streak of shadow/violet
// particles and reforms at the destination with a brief shadow cloak.
import { add, headLocation, viewDirection, lookedAtEnemy } from "./shared/targeting.js";
import { applyEffect } from "./shared/selfbuff.js";
import { tint, burst, dimensionSound } from "./shared/vfx.js";

const RANGE = [0, 8, 11, 14, 16];
const SPEED_SECONDS = [0, 1, 2, 2, 3];

function trail(player, from, to, color, level) {
  const steps = 10;
  for (let i = 0; i <= steps; i++) {
    const t = i / steps;
    const point = { x: from.x + (to.x - from.x) * t, y: from.y + (to.y - from.y) * t + 1, z: from.z + (to.z - from.z) * t };
    tint(player.dimension, "wd:rush_streak", point, color, 0.5 + level * 0.06, level / 4, 0.85);
  }
}

export function assassinRushCast(ctx) {
  const { player, level, spell } = ctx;
  const from = { ...player.location };
  const target = lookedAtEnemy(player, RANGE[level]);

  let destination;
  let facing;
  if (target) {
    const tv = viewDirection(target);
    const horizontal = Math.hypot(tv.x, tv.z) || 1;
    const behind = { x: -tv.x / horizontal, z: -tv.z / horizontal };
    destination = { x: target.location.x + behind.x * 1.1, y: target.location.y, z: target.location.z + behind.z * 1.1 };
    facing = { x: target.location.x, y: target.location.y + 1, z: target.location.z };
  } else {
    destination = add(player.location, viewDirection(player), RANGE[level]);
  }

  burst(player.dimension, "wd:rush_streak", headLocation(player), spell.color, 8 + level * 2, 0.8, 0.5, level / 4, 0.85);
  dimensionSound(player.dimension, "mob.endermen.portal", from, { volume: 0.5, pitch: 1.3 });

  try {
    if (facing) player.teleport(destination, { facingLocation: facing });
    else player.teleport(destination);
  } catch {
    return false;
  }

  trail(player, from, destination, spell.color, level);
  burst(player.dimension, "wd:rush_streak", { x: destination.x, y: destination.y + 1, z: destination.z }, spell.color, 8 + level * 2, 0.8, 0.5, level / 4, 0.85);
  dimensionSound(player.dimension, "mob.endermen.portal", destination, { volume: 0.5, pitch: 1.1 });
  applyEffect(player, "speed", SPEED_SECONDS[level] * 20, level, false);
  return true;
}

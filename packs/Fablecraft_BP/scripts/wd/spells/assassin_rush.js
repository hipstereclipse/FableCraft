// Assassin Rush — Physical. Blink through space along the Hero's line of sight:
// the caster dissolves into a streak of shadow/violet particles and reforms at
// the spot they are looking at — or, with a foe under the crosshair, instantly
// behind it — then drops a brief shadow cloak.
import { headLocation, viewDirection, lookedAtEnemy } from "./shared/targeting.js";
import { applyEffect } from "./shared/selfbuff.js";
import { tint, burst, dimensionSound } from "./shared/vfx.js";

const RANGE = [0, 8, 11, 14, 16];
const SPEED_SECONDS = [0, 1, 2, 2, 3];
const EYE_HEIGHT = 1.62; // eye -> feet offset, so a settled blink stands cleanly

function isSolid(dim, x, y, z) {
  try {
    const block = dim.getBlock({ x: Math.floor(x), y: Math.floor(y), z: Math.floor(z) });
    return !!block && !block.isAir && !block.isLiquid;
  } catch {
    return false; // unloaded / out of range — treat as open so the dash continues
  }
}

// Drop a candidate point onto the nearest solid footing so the Hero never
// reforms inside a wall or hovering. Searches a couple of blocks up (in case the
// point landed buried) then down for a 2-high air gap above solid ground.
function settle(dim, point) {
  const { x, z } = point;
  const startY = Math.floor(point.y);
  for (let y = startY + 2; y >= startY - 4; y--) {
    const feetClear = !isSolid(dim, x, y, z);
    const headClear = !isSolid(dim, x, y + 1, z);
    const ground = isSolid(dim, x, y - 1, z);
    if (feetClear && headClear && ground) return { x, y, z };
  }
  return { x, y: point.y, z }; // no footing nearby — keep the raw height (open leap)
}

// March along the look ray from the eyes, stopping just short of the first solid
// block, so the Hero blinks as far down their sightline as the path stays open.
function blinkPoint(player, maxDistance) {
  const head = headLocation(player);
  const dir = viewDirection(player);
  const dim = player.dimension;
  let reach = 0;
  const steps = Math.max(1, Math.ceil(maxDistance * 2));
  for (let i = 1; i <= steps; i++) {
    const t = (i / steps) * maxDistance;
    if (isSolid(dim, head.x + dir.x * t, head.y + dir.y * t, head.z + dir.z * t)) break;
    reach = t;
  }
  reach = Math.max(0, reach - 0.6); // back off the face we stopped against
  const landing = {
    x: head.x + dir.x * reach,
    y: head.y + dir.y * reach - EYE_HEIGHT,
    z: head.z + dir.z * reach,
  };
  return settle(dim, landing);
}

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
    // No foe under the crosshair: blink to wherever the Hero is looking.
    destination = blinkPoint(player, RANGE[level]);
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

// Assassin Rush — Physical. A fast forward blink: the caster dissolves into a
// streak of shadow/violet particles and reforms further along the way they are
// facing, hugging the ground. It is a horizontal ground dash (never a launch),
// it stops at walls and ledges, and it leaves the camera exactly where it was.
import { headLocation, viewDirection } from "./shared/targeting.js";
import { applyEffect } from "./shared/selfbuff.js";
import { tint, burst, dimensionSound } from "./shared/vfx.js";

const RANGE = [0, 8, 11, 14, 16];
const SPEED_SECONDS = [0, 1, 2, 2, 3];

// Read failures and liquids block the route. Only known air is body clearance;
// this deliberately treats plants/partial blocks conservatively on the stable API.
function blockAt(dim, x, y, z) {
  try {
    const block = dim.getBlock({ x: Math.floor(x), y: Math.floor(y), z: Math.floor(z) });
    return block ? { air: block.isAir, liquid: block.isLiquid } : null;
  } catch { return null; }
}

function bodyClear(dim, x, y, z) {
  for (const dx of [-0.3, 0.3]) {
    for (const dz of [-0.3, 0.3]) {
      for (let by = Math.floor(y); by <= Math.floor(y + 1.79); by++) {
        if (blockAt(dim, x + dx, by, z + dz)?.air !== true) return false;
      }
    }
  }
  return true;
}

function standableY(dim, x, baseY, z, fx, fz) {
  const start = Math.floor(baseY);
  for (let y = start + 1; y >= start - 3; y--) {
    // The leading edge reaches a step before the centre does. Accept support
    // under any footprint corner while still clearing the entire body above it.
    const supports = [-0.3, 0.3].flatMap(dx => [-0.3, 0.3].map(dz => blockAt(dim, x + dx, y - 1, z + dz)));
    const front = blockAt(dim, x + fx * 0.3, y - 1, z + fz * 0.3);
    if (front && !front.air && !front.liquid && supports.every(Boolean)
        && !supports.some(b => b.liquid) && bodyClear(dim, x, y, z)) return y;
  }
  return null;
}

// Walk forward along the HORIZONTAL facing in quarter-block steps, following the
// ground and halting at the first wall or unbridgeable ledge. Returns the
// furthest safe footing — or the caster's own position if blocked immediately.
function blinkPoint(player, maxDistance) {
  const dim = player.dimension;
  const origin = player.location; // feet
  const view = viewDirection(player);
  let fx = view.x, fz = view.z;
  const horizontal = Math.hypot(fx, fz);
  if (horizontal < 1e-3) {
    // Looking straight up or down: fall back to the body's yaw for a direction.
    const yaw = player.getRotation().y * Math.PI / 180;
    fx = -Math.sin(yaw); fz = Math.cos(yaw);
  } else {
    fx /= horizontal; fz /= horizontal;
  }

  let best = { x: origin.x, y: origin.y, z: origin.z };
  let curY = origin.y;
  for (let d = 0.25; d <= maxDistance; d += 0.25) {
    const x = origin.x + fx * d;
    const z = origin.z + fz * d;
    const y = standableY(dim, x, curY, z, fx, fz);
    if (y === null) break; // wall / ledge — stop at the last good footing
    // Swept clearance: stepping up cannot clip through a low ceiling, and
    // stepping down cannot bypass an obstruction at the previous feet height.
    if (y > curY && !bodyClear(dim, best.x, y, best.z)) break;
    if (y < curY && !bodyClear(dim, x, curY, z)) break;
    curY = y;
    best = { x: x, y: y, z: z };
  }
  return best;
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
  const destination = blinkPoint(player, RANGE[level]);

  if (Math.hypot(destination.x - from.x, destination.z - from.z) < 0.25) return false;

  burst(player.dimension, "wd:rush_streak", headLocation(player), spell.color, 8 + level * 2, 0.8, 0.5, level / 4, 0.85);
  dimensionSound(player.dimension, "mob.endermen.portal", from, { volume: 0.5, pitch: 1.3 });

  try {
    // No facingLocation: keep the player's own view so the camera never snaps.
    if (!player.tryTeleport(destination, { keepVelocity: false, checkForBlocks: true })) return false;
  } catch {
    return false;
  }

  trail(player, from, destination, spell.color, level);
  burst(player.dimension, "wd:rush_streak", { x: destination.x, y: destination.y + 1, z: destination.z }, spell.color, 8 + level * 2, 0.8, 0.5, level / 4, 0.85);
  dimensionSound(player.dimension, "mob.endermen.portal", destination, { volume: 0.5, pitch: 1.1 });
  applyEffect(player, "speed", SPEED_SECONDS[level] * 20, level, false);
  return true;
}

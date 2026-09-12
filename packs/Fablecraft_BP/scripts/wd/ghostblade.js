// Will & Destiny — Ghost Sword companion. A floating spectral blade the power
// conjures to fight at the Hero's side for a timer, then dissipates. It is
// SCRIPT-SIMULATED (no new entity, so no gen_behavior pass): a per-player record
// is flown toward the nearest valid foe each run, drawn as an oriented blade of
// particles, and bites on a short cooldown. Ally-safe via targeting.js.
import { EntityDamageCause, system, world } from "@minecraft/server";
import { nearestEnemy, normalize, distanceSquared } from "./spells/shared/targeting.js";
import { damageEnemy } from "./spells/shared/combat.js";
import { tint, burst, dimensionSound } from "./spells/shared/vfx.js";

const TICK = () => system.currentTick;
const TICK_STEP = 2;        // run cadence (ticks)
const HIT_COOLDOWN = 12;    // ticks between strikes on a foe
const STRIKE_REACH = 1.7;   // distance to a foe at which the blade bites

// Per level (1..4): how long the blade lingers, how hard it bites, how far it
// hunts, how fast it flies. Index 0 is unused (cast level is always >= 1).
const LIFETIME = [0, 200, 280, 360, 440]; // ~10–22 s
const DAMAGE = [0, 4, 5, 6, 7];
const SEEK = [0, 12, 14, 16, 18];
const SPEED = [0, 0.8, 0.9, 1.0, 1.1];    // blocks per run

const blades = new Map(); // playerId -> { level, color, expiry, pos, lastHit }

// Conjure (or refresh) the Hero's ghost sword. One blade per Hero — recasting
// renews the timer and reseats it at the Hero's shoulder.
export function deployGhostSword(player, level, color) {
  const lvl = Number.isFinite(level) ? Math.max(1, Math.min(4, Math.floor(level))) : 1;
  blades.set(player.id, {
    level: lvl,
    color,
    expiry: TICK() + LIFETIME[lvl],
    pos: { x: player.location.x, y: player.location.y + 1.5, z: player.location.z },
    lastHit: TICK() - HIT_COOLDOWN,
    dimensionId: player.dimension.id,
  });
}

// Where the blade idles with no foe near: hovering at the Hero's right shoulder.
function idleHome(player) {
  const yaw = player.getRotation().y * Math.PI / 180;
  const right = { x: Math.cos(yaw), z: Math.sin(yaw) };
  return { x: player.location.x + right.x * 0.7, y: player.location.y + 1.6, z: player.location.z + right.z * 0.7 };
}

// Draw the blade as an oriented line of spectral motes (tip along `dir`) with a
// short crossguard, so it reads as a sword rather than a blob.
function drawBlade(dim, pos, dir, color, level) {
  const steps = 5;
  for (let i = 0; i <= steps; i++) {
    const t = (i / steps) * 1.0;
    tint(dim, "wd:ghost_blade",
      { x: pos.x + dir.x * t, y: pos.y + dir.y * t, z: pos.z + dir.z * t },
      color, 0.45 + level * 0.04, level / 4, 0.85);
  }
  const guard = normalize({ x: -dir.z, y: 0, z: dir.x });
  for (const s of [-0.28, 0.28]) {
    tint(dim, "wd:ghost_blade",
      { x: pos.x + guard.x * s, y: pos.y, z: pos.z + guard.z * s },
      color, 0.4, level / 4, 0.85);
  }
}

// Do not deal damage through walls or unreadable chunks, even for a spectral blade.
function clearStrike(dim, from, to) {
  const steps = Math.max(1, Math.ceil(Math.sqrt(distanceSquared(from, to)) * 4));
  for (let i = 0; i <= steps; i++) {
    const t = i / steps;
    try {
      const b = dim.getBlock({
        x: Math.floor(from.x + (to.x - from.x) * t),
        y: Math.floor(from.y + (to.y - from.y) * t),
        z: Math.floor(from.z + (to.z - from.z) * t),
      });
      if (!b || (!b.isAir && !b.isLiquid)) return false;
    } catch { return false; }
  }
  return true;
}

function tickBlade(player, blade) {
  const dim = player.dimension;
  const { color, level } = blade;

  const home = idleHome(player);
  if (blade.dimensionId !== dim.id || distanceSquared(blade.pos, home) > (SEEK[level] + 4) ** 2) {
    blade.pos = home;
    blade.dimensionId = dim.id;
  }
  // Range is measured from the owner so a chain of foes cannot lure it away.
  const foe = nearestEnemy(player, player.location, SEEK[level]);
  const target = foe?.isValid
    ? { x: foe.location.x, y: foe.location.y + 1.0, z: foe.location.z }
    : idleHome(player);

  const to = { x: target.x - blade.pos.x, y: target.y - blade.pos.y, z: target.z - blade.pos.z };
  const dist = Math.hypot(to.x, to.y, to.z) || 1e-3;
  const dir = { x: to.x / dist, y: to.y / dist, z: to.z / dist };
  const step = Math.min(dist, SPEED[level]);
  const next = { x: blade.pos.x + dir.x * step, y: blade.pos.y + dir.y * step, z: blade.pos.z + dir.z * step };
  if (!clearStrike(dim, blade.pos, next)) {
    drawBlade(dim, blade.pos, { x: 0, y: 1, z: 0 }, color, level);
    return;
  }
  blade.pos = next;

  drawBlade(dim, blade.pos, dist < 0.05 ? { x: 0, y: 1, z: 0 } : dir, color, level);

  if (foe?.isValid && distanceSquared(blade.pos, target) <= STRIKE_REACH ** 2
      && TICK() - blade.lastHit >= HIT_COOLDOWN && clearStrike(dim, blade.pos, target)) {
    blade.lastHit = TICK();
    damageEnemy(player, foe, DAMAGE[level], EntityDamageCause.magic);
    burst(dim, "wd:ghost_blade", { x: foe.location.x, y: foe.location.y + 1, z: foe.location.z },
      color, 5 + level, 0.6, 0.5, level / 4, 0.95);
    dimensionSound(dim, "item.trident.hit_ground", blade.pos, { volume: 0.5, pitch: 1.6 });
  }
}

system.runInterval(() => {
  if (blades.size === 0) return;
  const players = new Map(world.getPlayers().map((p) => [p.id, p]));
  for (const [pid, blade] of [...blades.entries()]) {
    const player = players.get(pid);
    if (!player || !player.isValid) { blades.delete(pid); continue; } // offline — drop the blade
    if (TICK() >= blade.expiry) {
      try { burst(player.dimension, "wd:ghost_blade", blade.pos, blade.color, 8 + blade.level, 0.7, 0.6, blade.level / 4, 0.9); } catch { /* dissipate flourish is cosmetic */ }
      blades.delete(pid);
      continue;
    }
    try { tickBlade(player, blade); } catch {
      // A transient API failure (chunk unload, despawn) must never kill the loop.
    }
  }
}, TICK_STEP);

// Clear a leaving player's blade so the ledger never leaks.
world.afterEvents.playerLeave.subscribe((event) => { blades.delete(event.playerId); });

// Death and respawn must not leave a damage source alive or restore an old blade.
world.afterEvents.entityDie.subscribe(({ deadEntity }) => { blades.delete(deadEntity.id); });
world.afterEvents.playerSpawn.subscribe(({ player }) => { blades.delete(player.id); });

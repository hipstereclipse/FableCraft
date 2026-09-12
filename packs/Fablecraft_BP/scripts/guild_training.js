// Background training is a Minecraft adaptation. A session acquires a clear
// station once; normal strolling resumes on release. It is not NPC pathfinding.
export const GUILD_TRAINING_TAGS = Object.freeze([
  "fc_train_ring_a", "fc_train_ring_b", "fc_train_range", "fc_train_will",
]);
const TRAIN_TICKS = 1200;
const CYCLE_TICKS = 3600;
// gen_structures.py authors the training discs and island mark from these floors.
// Block.isSolid is pre-release, unavailable to our stable @minecraft/server 2.1.
// Refuse unknown replacement floors rather than guessing their support shape.
const STATION_FLOORS = new Set(["minecraft:coarse_dirt", "minecraft:dirt_path"]);
let reactionController;

// The handwritten emote and conversation owners share this hook. Follow must
// survive reload; a later social event replaces that AI group and clears it.
export function bindGuildTrainingReactions(controller) { reactionController = controller; }

export function notifyGuildTrainingReaction(entity, event) {
  try {
    if (!entity.typeId.startsWith("fc:guild_apprentice_") || !event.startsWith("fc:react_")) return;
    if (event === "fc:react_follow") entity.addTag("fc_guild_following");
    else entity.removeTag("fc_guild_following");
  } catch { }
  reactionController?.interrupt(entity);
}

export function guildTrainingSession(tick, timeOfDay) {
  if (timeOfDay < 0 || timeOfDay >= 12000 || tick % CYCLE_TICKS >= TRAIN_TICKS) return null;
  return Math.floor(tick / CYCLE_TICKS);
}

// Check the full apprentice footprint and headroom as well as the supporting
// floor. An unloaded, liquid, occupied or unsupported station is unavailable.
// tryTeleport's engine collision check is still required after this preflight.
export function guildStationClear(entity, point) {
  try {
    const minX = Math.floor(point.x - 0.35), maxX = Math.floor(point.x + 0.35);
    const minZ = Math.floor(point.z - 0.35), maxZ = Math.floor(point.z + 0.35);
    const feet = Math.floor(point.y), head = Math.floor(point.y + 1.9);
    for (let x = minX; x <= maxX; x++) {
      for (let z = minZ; z <= maxZ; z++) {
        if (!STATION_FLOORS.has(entity.dimension.getBlock({ x, y: feet - 1, z })?.typeId)) return false;
        for (let y = feet; y <= head; y++) {
          if (!entity.dimension.getBlock({ x, y, z })?.isAir) return false;
        }
      }
    }
    return true;
  } catch { return false; }
}

export function createGuildTrainingController({ now, session, canTrain, stationClear = guildStationClear }) {
  const records = new Map();
  let nextToken = 1;

  function usable(entity) {
    try { return !!entity && entity.isValid !== false; } catch { return false; }
  }

  function recordFor(entity) {
    let record = records.get(entity.id);
    if (!record) {
      // Always stop once on first observation, including tagless legacy NPCs
      // whose old stop event failed. This touches only the training group.
      record = { entity, active: false, pending: true, blockedSession: null,
        attemptedSession: null, quietUntil: 0, token: nextToken++ };
      records.set(entity.id, record);
    } else record.entity = entity;
    return record;
  }

  function clean(record) {
    if (!usable(record.entity)) {
      records.delete(record.entity.id);
      return false;
    }
    try {
      // Keep tags until the component event succeeds; failed tag removal also
      // leaves cleanup pending. Both operations are safe to retry next pass.
      record.entity.triggerEvent("fc:guild_training_stop");
      for (const tag of record.entity.getTags()) {
        if (GUILD_TRAINING_TAGS.includes(tag)) record.entity.removeTag(tag);
      }
      record.pending = false;
      return true;
    } catch { return false; }
  }

  function release(record, interrupt = false) {
    if (interrupt) {
      record.blockedSession = session();
      record.quietUntil = Math.max(record.quietUntil, now() + 200);
    }
    if (record.active) {
      record.active = false;
      record.pending = true;
      record.token = nextToken++; // Invalidate queued animation/archery work now.
    }
    return !record.pending || clean(record);
  }

  function allowed(entity) {
    try { return usable(entity) && canTrain(entity); } catch { return false; }
  }

  function stillAtStation(record) {
    try {
      const location = record.entity.location;
      return record.entity.dimension.id === record.dimension
        && Math.hypot(location.x - record.point.x, location.y - record.point.y,
          location.z - record.point.z) <= 0.8
        && record.entity.getTags().includes(record.role);
    } catch { return false; }
  }

  function beginPass(entities) {
    const seen = new Set(entities.map(entity => entity.id));
    for (const record of records.values()) {
      // A clean, inactive record has no pending release to invoke clean().
      // Drop invalid handles here too; a later loaded handle must reconcile.
      if (!usable(record.entity)) {
        records.delete(record.entity.id);
        continue;
      }
      if (!seen.has(record.entity.id)) release(record, true);
    }
    for (const entity of entities) {
      const record = recordFor(entity);
      if (record.pending) clean(record);
      if (!allowed(entity)) release(record, true);
      else if (record.active && (session() !== record.session || session() === null)) release(record);
      else if (record.active && (!stillAtStation(record) || !stationClear(entity, record.point))) release(record, true);
    }
  }

  function eligible(entity) {
    const record = entity && records.get(entity.id);
    const current = session();
    return !!record && !record.pending && allowed(entity) && current !== null
      && record.blockedSession !== current && now() >= record.quietUntil
      && (record.active || record.attemptedSession !== current);
  }

  function interrupt(entity) {
    if (!entity || !usable(entity)) return;
    release(recordFor(entity), true);
  }

  function acquire(entity, role, point, facing) {
    const record = entity && records.get(entity.id);
    if (!eligible(entity) || !GUILD_TRAINING_TAGS.includes(role)) return null;
    if (record.active) return record.role === role ? record.token : null;
    record.attemptedSession = session();
    if (!stationClear(entity, point)) return null;
    try {
      // One checked placement per session is retained as an explicit temporary
      // adaptation. Never fall back to unchecked teleport or repeat on failure.
      if (!entity.tryTeleport(point, { facingLocation: facing, checkForBlocks: true })) return null;
      record.pending = true;
      entity.triggerEvent("fc:guild_training_start");
      entity.addTag(role);
      record.role = role;
      record.point = { ...point };
      record.dimension = entity.dimension.id;
      record.session = session();
      record.token = nextToken++;
      record.active = true;
      record.pending = false;
      return record.token;
    } catch {
      release(record, true);
      return null;
    }
  }

  function acquirePair(first, second) {
    if (!first || !second || first.entity.id === second.entity.id
      || !eligible(first.entity) || !eligible(second.entity)) {
      if (first) interrupt(first.entity);
      if (second) interrupt(second.entity);
      return null;
    }
    const a = acquire(first.entity, first.role, first.point, first.facing);
    const b = a === null ? null : acquire(second.entity, second.role, second.point, second.facing);
    if (a === null || b === null) {
      interrupt(first.entity);
      interrupt(second.entity);
      return null;
    }
    return [a, b];
  }

  function retain(ids) {
    for (const record of records.values()) {
      if (record.active && !ids.has(record.entity.id)) release(record, true);
    }
  }

  function isActive(entity, token) {
    const record = entity && records.get(entity.id);
    if (!record?.active || token === null || record.token !== token) return false;
    if (session() === null || session() !== record.session) {
      release(record);
      return false;
    }
    if (!allowed(entity) || !stillAtStation(record) || !stationClear(entity, record.point)) {
      release(record, true);
      return false;
    }
    return true;
  }

  function reserved(entity) {
    const record = entity && records.get(entity.id);
    return !!record && (record.active || record.pending);
  }

  return { beginPass, eligible, acquire, acquirePair, retain, interrupt, isActive, reserved };
}

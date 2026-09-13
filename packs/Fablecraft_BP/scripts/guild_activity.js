// Two established Skill residents share one requester authority. Native tags are
// derived filters; the write-ahead holder journal is never inferred from them.
export const GUILD_ACTIVITY_KEY = "fc_guild_skill_activity_v1";
export const GUILD_ACTIVITY_WITNESS = "fc_guild_skill_activity_seen_v1";
export const GUILD_ACTIVITY_OWNED = "fc_guild_activity_owned_v1";
export const GUILD_ACTIVITY_WAIT = "fc_guild_activity_wait_v1";
export const GUILD_ACTIVITY_CHANNELS = Object.freeze({
  skill_range: { tag: "fc_skill_range_requester_v1", event: "fc:guild_activity_follow_range" },
  skill_hall: { tag: "fc_skill_hall_requester_v1", event: "fc:guild_activity_follow_hall" },
});
const SLOTS = Object.keys(GUILD_ACTIVITY_CHANNELS);
const TYPE = "fc:guild_apprentice_skill";
const MODES = new Set(["idle", "follow", "wait", "stopping"]);
const NPC_TAGS = [GUILD_ACTIVITY_OWNED, GUILD_ACTIVITY_WAIT, "fc_guild_following"];
const HOLDER_LIMIT = 64;
const point = p => p && [p.x, p.y, p.z].every(Number.isFinite);
const sameBase = (a, b) => point(a) && point(b) && a.x === b.x && a.y === b.y && a.z === b.z;
const usable = e => { try { return !!e && e.isValid === true && typeof e.id === "string" && !!e.id; } catch { return false; } };

export function createGuildActivityController({ read, write, readWitness, writeWitness,
  resolve, base, lookup, players, stopTraining, trainingReserved, now = () => 0 }) {
  // Only stable IDs/revisions live here. Reload intentionally loses permission
  // to activate: saved activity must first stop and reconcile its holder debt.
  const active = new Map(), pending = new Map(), known = new Map(), idleClean = new Set();
  const invalidations = new Map(), debts = new Map(SLOTS.map(slot => [slot, new Set()]));
  // Excess external tag holders quarantine the channel permanently. This pilot
  // has no manual recovery operation and never evicts an unresolved obligation.
  const overflow = new Set();
  const result = (handled, accepted, reason, queued = false) => ({ handled, accepted, reason, pending: queued });

  function identity(entity) {
    try {
      if (entity?.typeId !== TYPE) return { kind: "other" };
      if (!usable(entity)) return { kind: "blocked", reason: "invalid-entity" };
      const binding = resolve(entity);
      if (binding?.kind === "other") {
        const remembered = known.has(entity.id) || Object.values(journal()?.channels ?? {}).some(r => r.entityId === entity.id);
        return remembered ? { kind: "blocked", reason: "lost-established-identity" } : binding;
      }
      if (binding?.kind !== "bound" || !SLOTS.includes(binding.slot) || binding.entityId !== entity.id
        || binding.type !== TYPE || !sameBase(binding.base, base())) return { kind: "blocked", reason: "unavailable-identity" };
      return binding;
    } catch { return { kind: "blocked", reason: "unreadable-identity" }; }
  }
  function validJournal(saved) {
    if (!saved || saved.schema !== 1 || !sameBase(saved.base, base()) || !saved.channels
      || Object.keys(saved.channels).length !== SLOTS.length) return false;
    const ids = new Set();
    return SLOTS.every(slot => {
      const r = saved.channels[slot];
      if (!r || !Number.isSafeInteger(r.revision) || r.revision < 0 || !MODES.has(r.mode)
        || (r.holderOverflow !== undefined && typeof r.holderOverflow !== "boolean")
        || !Array.isArray(r.pendingTagHolders) || r.pendingTagHolders.length > HOLDER_LIMIT
        || r.pendingTagHolders.some(id => typeof id !== "string" || !id)
        || new Set(r.pendingTagHolders).size !== r.pendingTagHolders.length) return false;
      if (r.entityId !== null && (typeof r.entityId !== "string" || !r.entityId || ids.has(r.entityId))) return false;
      if (r.entityId) ids.add(r.entityId);
      if (r.entityId === null && (r.mode !== "idle" || r.revision !== 0)) return false;
      if (r.mode === "idle") return r.ownerId === null && r.dimension === null && !r.pendingTagHolders.length;
      if (r.mode === "follow" && !r.pendingTagHolders.includes(r.ownerId)) return false;
      if (r.mode === "wait" && r.pendingTagHolders.length) return false;
      return !!r.entityId && typeof r.ownerId === "string" && !!r.ownerId && typeof r.dimension === "string" && !!r.dimension;
    });
  }
  function save(saved) {
    try {
      for (const slot of overflow) saved.channels[slot].holderOverflow = true;
      if (!validJournal(saved)) return false;
      const raw = JSON.stringify(saved);
      write(raw);
      return read() === raw && readWitness() === true;
    } catch { return false; }
  }
  function journal(initialize = false) {
    try {
      const witness = readWitness(), raw = read();
      if (raw === undefined && witness === undefined && initialize && point(base())) {
        // The witness is never removed. A crash between these writes leaves a
        // missing established journal blocked instead of guessing empty history.
        writeWitness(true);
        if (readWitness() !== true) return null;
        const saved = { schema: 1, base: { ...base() }, channels: Object.fromEntries(SLOTS.map(slot => [slot,
          { entityId: null, revision: 0, mode: "idle", ownerId: null, dimension: null, pendingTagHolders: [] }])) };
        return save(saved) ? saved : null;
      }
      if (witness !== true || typeof raw !== "string") return null;
      const saved = JSON.parse(raw);
      if (!validJournal(saved)) return null;
      for (const slot of SLOTS) if (saved.channels[slot].holderOverflow) overflow.add(slot);
      return saved;
    } catch { return null; }
  }
  function status(entity) {
    const binding = identity(entity);
    if (binding.kind === "other") return { managed: false, blocked: false, mode: "idle", ownerId: null, revision: null };
    const saved = binding.kind === "bound" ? journal() : null;
    const record = saved?.channels[binding.slot];
    if (!record || record.entityId !== entity.id) return { managed: true, blocked: true, mode: "stopping", ownerId: null, revision: null };
    return { managed: true, blocked: overflow.has(binding.slot) || invalidations.has(entity.id) || record.revision >= Number.MAX_SAFE_INTEGER || record.mode === "stopping" || (record.mode === "idle" && !idleClean.has(entity.id))
      || (record.mode !== "idle" && (active.get(entity.id) !== record.revision || !derivedCurrent(entity, binding.slot, record))),
      mode: record.mode, ownerId: record.ownerId, revision: record.revision };
  }
  function clearNative(entity) {
    active.delete(entity.id);
    idleClean.delete(entity.id);
    try {
      let tagsClean = true;
      for (const tag of NPC_TAGS) {
        try { entity.removeTag(tag); if (entity.hasTag(tag)) tagsClean = false; } catch { tagsClean = false; }
      }
      // Always attempt the unconditional stop, even if marker removal failed.
      entity.triggerEvent("fc:guild_activity_stop");
      return tagsClean;
    } catch { return false; }
  }
  function heroes() {
    try {
      const all = players();
      if (!Array.isArray(all) || all.some(p => !usable(p) || p.typeId !== "minecraft:player")) return null;
      if (new Set(all.map(p => p.id)).size !== all.length) return null;
      return all;
    } catch { return null; }
  }
  function oweHolder(slot, id) {
    const owed = debts.get(slot);
    if (owed.has(id)) return true;
    if (owed.size >= HOLDER_LIMIT) { overflow.add(slot); return false; }
    owed.add(id);
    return true;
  }
  function observeHolders(slot, all) {
    if (!all) return;
    const tag = GUILD_ACTIVITY_CHANNELS[slot].tag;
    for (const player of all) {
      try { if (player.hasTag(tag)) oweHolder(slot, player.id); }
      catch { oweHolder(slot, player.id); }
    }
  }
  function relationship(entity, player, spouseOnly = false) {
    try {
      if (!usable(entity) || !usable(player) || player.typeId !== "minecraft:player"
        || entity.dimension.id !== player.dimension.id || entity.hasTag("fc_guild_defending") || entity.hasTag("fc_aggravated")) return false;
      const married = entity.getProperty("fc:married"), owner = entity.getDynamicProperty("fc_spouse_player");
      return (!spouseOnly && married === 0 && (owner === undefined || owner === "")) || (married === 1 && owner === player.id);
    } catch { return false; }
  }
  function nearby(entity, player) {
    try { return point(entity.location) && point(player.location)
      && Math.hypot(entity.location.x - player.location.x, entity.location.y - player.location.y,
        entity.location.z - player.location.z) <= 12; } catch { return false; }
  }
  function rememberHolder(saved, slot, id) {
    const r = saved.channels[slot];
    if (!oweHolder(slot, id)) { save(saved); return false; }
    if (r.pendingTagHolders.includes(id)) return true;
    if (r.pendingTagHolders.length >= HOLDER_LIMIT) { overflow.add(slot); save(saved); return false; }
    r.pendingTagHolders.push(id);
    return save(saved);
  }
  function cleanHolders(saved, slot, retainOwner = false) {
    for (const id of debts.get(slot)) if (!rememberHolder(saved, slot, id)) return false;
    const all = heroes();
    if (!all) return false;
    const r = saved.channels[slot], tag = GUILD_ACTIVITY_CHANNELS[slot].tag;
    let readable = true;
    // A bad player read must not starve cleanup for other recorded live holders.
    for (const player of all) {
      try { if (player.hasTag(tag) && !rememberHolder(saved, slot, player.id)) return false; }
      catch { readable = false; if (!rememberHolder(saved, slot, player.id)) return false; }
    }
    const remaining = [];
    for (const id of r.pendingTagHolders) {
      const player = all.find(p => p.id === id);
      if (!player) { remaining.push(id); continue; }
      try {
        player.removeTag(tag);
        if (player.hasTag(tag)) remaining.push(id);
      } catch { remaining.push(id); }
    }
    const ready = readable && remaining.length === 0;
    if (retainOwner && !remaining.includes(r.ownerId)) remaining.push(r.ownerId);
    if (remaining.length !== r.pendingTagHolders.length) {
      r.pendingTagHolders = remaining;
      if (!save(saved)) return false;
    }
    for (const id of [...debts.get(slot)]) if (!remaining.includes(id)) debts.get(slot).delete(id);
    return ready && !overflow.has(slot);
  }
  function derivedCurrent(entity, slot, record, all = heroes()) {
    if (!all) return false;
    try {
      const owner = all.find(p => p.id === record.ownerId);
      if (!owner || !relationship(entity, owner) || entity.dimension.id !== record.dimension
        || !entity.hasTag(GUILD_ACTIVITY_OWNED)
        || entity.hasTag(GUILD_ACTIVITY_WAIT) !== (record.mode === "wait")
        || entity.hasTag("fc_guild_following") !== (record.mode === "follow")) return false;
      const tag = GUILD_ACTIVITY_CHANNELS[slot].tag;
      return all.every(p => p.hasTag(tag) === (record.mode === "follow" && p.id === record.ownerId));
    } catch { return false; }
  }
  function bind(saved, binding) {
    const r = saved.channels[binding.slot];
    if (r.entityId !== null) {
      if (r.entityId !== binding.entityId) return false;
      known.set(binding.entityId, binding.slot);
      return true;
    }
    r.entityId = binding.entityId;
    if (!save(saved)) return false;
    known.set(binding.entityId, binding.slot);
    return true;
  }
  function advanceRevision(saved, slot) {
    const r = saved.channels[slot];
    invalidations.set(r.entityId, Math.max(invalidations.get(r.entityId) ?? -1, r.revision));
    if (r.revision >= Number.MAX_SAFE_INTEGER) return false;
    r.revision++;
    if (!save(saved)) return false;
    invalidations.delete(r.entityId);
    return true;
  }
  function recoverInvalidation(saved, slot, entity) {
    const r = saved.channels[slot], prior = invalidations.get(r.entityId);
    if (prior === undefined) return true;
    if (r.revision > prior) { invalidations.delete(r.entityId); return true; }
    if (prior >= Number.MAX_SAFE_INTEGER) { if (entity) clearNative(entity); return false; }
    r.revision = prior + 1;
    if (r.mode !== "idle") r.mode = "stopping";
    if (!save(saved)) { if (entity) clearNative(entity); return false; }
    invalidations.delete(r.entityId);
    return true;
  }
  function stopRecord(saved, slot, entity) {
    const r = saved.channels[slot];
    pending.delete(r.entityId); active.delete(r.entityId);
    if (r.mode !== "idle" && r.mode !== "stopping") {
      r.mode = "stopping";
      if (!advanceRevision(saved, slot)) { if (entity) clearNative(entity); return false; }
    }
    if (!entity || !clearNative(entity) || !cleanHolders(saved, slot)) return false;
    if (r.revision >= Number.MAX_SAFE_INTEGER) return false;
    if (r.mode !== "idle") {
      r.mode = "idle"; r.ownerId = null; r.dimension = null;
      if (!save(saved)) return false;
    }
    idleClean.add(entity.id);
    return true;
  }
  function request(entity, player, mode, options = {}) {
    const binding = identity(entity);
    if (binding.kind === "other") return result(false, false, "unmanaged");
    if (binding.kind !== "bound" || !["follow", "wait", "idle"].includes(mode)
      || !relationship(entity, player) || !nearby(entity, player)) return result(true, false, "unavailable");
    const saved = journal(true);
    if (!saved || !bind(saved, binding)) return result(true, false, "unavailable-history");
    const r = saved.channels[binding.slot];
    if (options.expectedRevision !== undefined && options.expectedRevision !== r.revision) return result(true, false, "stale");
    if (r.mode === "stopping" || (r.ownerId !== null && r.ownerId !== player.id)) return result(true, false, "owned-or-pending");
    if ((mode === "wait" && r.ownerId === null && (!options.acquireWait || !relationship(entity, player, true))) || (mode === "idle" && r.ownerId !== player.id)) return result(true, false, "not-owner");
    if (r.revision >= Number.MAX_SAFE_INTEGER) return result(true, false, "revision-exhausted");
    observeHolders(binding.slot, heroes());
    if (overflow.has(binding.slot)) { clearNative(entity); save(saved); return result(true, false, "holder-overflow"); }
    r.mode = "stopping"; r.ownerId = player.id; r.dimension = player.dimension.id;
    pending.delete(entity.id); active.delete(entity.id);
    if (!advanceRevision(saved, binding.slot)) { clearNative(entity); return result(true, false, "save-failed"); }
    try {
      if (stopTraining(entity) === false || trainingReserved(entity) || !clearNative(entity) || !cleanHolders(saved, binding.slot)) return result(true, false, "cleanup-pending");
    } catch { clearNative(entity); return result(true, false, "cleanup-pending"); }
    if (mode === "idle") {
      r.mode = "idle"; r.ownerId = null; r.dimension = null;
      const released = save(saved);
      if (released) idleClean.add(entity.id);
      return result(true, released, "released");
    }
    r.mode = mode;
    if (mode === "follow" && !r.pendingTagHolders.includes(player.id)) r.pendingTagHolders.push(player.id);
    if (!save(saved)) return result(true, false, "save-failed");
    // No player tag or replacement native goal is granted during the tick in
    // which stop was requested. Native target-drop still needs engine testing.
    pending.set(entity.id, { revision: r.revision, ready: now() + 1 });
    return result(true, true, "queued", true);
  }
  function activate(saved, slot, entity, player) {
    const r = saved.channels[slot];
    try {
      if (trainingReserved(entity) || !relationship(entity, player) || !nearby(entity, player)
        || entity.dimension.id !== r.dimension) return false;
      if (!cleanHolders(saved, slot, r.mode === "follow")) return false;
      if (r.mode === "follow") {
        if (!rememberHolder(saved, slot, player.id)) return false;
        player.addTag(GUILD_ACTIVITY_CHANNELS[slot].tag);
        if (!player.hasTag(GUILD_ACTIVITY_CHANNELS[slot].tag)) return false;
      }
      entity.addTag(GUILD_ACTIVITY_OWNED);
      if (!entity.hasTag(GUILD_ACTIVITY_OWNED)) return false;
      if (r.mode === "wait") { entity.addTag(GUILD_ACTIVITY_WAIT); if (!entity.hasTag(GUILD_ACTIVITY_WAIT)) return false; }
      else { entity.addTag("fc_guild_following"); if (!entity.hasTag("fc_guild_following")) return false; }
      entity.triggerEvent(r.mode === "wait" ? "fc:guild_activity_wait" : GUILD_ACTIVITY_CHANNELS[slot].event);
      active.set(entity.id, r.revision); pending.delete(entity.id);
      return true;
    } catch { return false; }
  }
  function preempt(entity) {
    const binding = identity(entity);
    if (binding.kind === "other") return true;
    if (!usable(entity)) return false;
    pending.delete(entity.id);
    const stopped = (binding.kind === "bound" || known.has(entity.id)) && clearNative(entity);
    const saved = journal(), slot = binding.kind === "bound" ? binding.slot : known.get(entity.id);
    if (saved && slot && saved.channels[slot].entityId === entity.id) {
      const r = saved.channels[slot];
      if (r.mode !== "idle") r.mode = "stopping";
      if (!advanceRevision(saved, slot)) return false;
      stopRecord(saved, slot, entity);
    }
    return !!stopped;
  }
  function reconcile(entities = []) {
    const candidates = new Map();
    for (const entity of entities) {
      const binding = identity(entity);
      if (binding.kind === "bound") candidates.set(binding.slot, entity);
    }
    const saved = journal(candidates.size > 0);
    if (!saved) {
      const cleanup = new Map([...candidates.values()].map(e => [e.id, e]));
      for (const id of known.keys()) {
        let entity = entities.find(e => e?.id === id);
        if (!entity) { try { entity = lookup(id); } catch { } }
        if (usable(entity)) cleanup.set(id, entity);
      }
      for (const entity of cleanup.values()) { pending.delete(entity.id); clearNative(entity); }
      return;
    }
    for (const slot of SLOTS) {
      const r = saved.channels[slot];
      let entity = candidates.get(slot);
      if (r.entityId && entity?.id !== r.entityId) { try { entity = lookup(r.entityId); } catch { entity = undefined; } }
      if (!recoverInvalidation(saved, slot, usable(entity) && entity.id === r.entityId ? entity : null)) continue;
      const binding = identity(entity);
      if (binding.kind !== "bound" || binding.slot !== slot || !bind(saved, binding)) {
        pending.delete(r.entityId); active.delete(r.entityId);
        if (r.mode !== "idle") stopRecord(saved, slot, usable(entity) && entity.id === r.entityId ? entity : null);
        continue;
      }
      if (overflow.has(slot)) {
        if (!r.holderOverflow) save(saved);
        stopRecord(saved, slot, entity);
        continue;
      }
      if (r.mode === "idle") {
        if (!idleClean.has(entity.id)) {
          try {
            if (stopTraining(entity) !== false && !trainingReserved(entity) && clearNative(entity)) idleClean.add(entity.id);
          } catch { /* failed initial cleanup excludes acquisition until retried */ }
        }
        continue;
      }
      const all = heroes(), owner = all?.find(p => p.id === r.ownerId);
      observeHolders(slot, all);
      const queued = pending.get(entity.id);
      if (r.mode === "stopping" || !owner || !relationship(entity, owner) || entity.dimension.id !== r.dimension) {
        stopRecord(saved, slot, entity); continue;
      }
      if (active.get(entity.id) === r.revision) {
        if (!derivedCurrent(entity, slot, r, all)) stopRecord(saved, slot, entity);
        continue;
      }
      if (queued?.revision === r.revision) {
        if (now() < queued.ready) continue;
        if (activate(saved, slot, entity, owner)) continue;
      }
      stopRecord(saved, slot, entity);
    }
  }
  const reserved = entity => { const s = status(entity); return s.managed && (s.blocked || s.mode !== "idle"); };
  const valid = (entity, revision) => { const s = status(entity); return s.managed && !s.blocked && s.revision === revision; };
  return { status, request, preempt, reconcile, reserved, valid };
}

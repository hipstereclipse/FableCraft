// Persistent residence is separate from location, activity and relationships.
// In particular, an unavailable entity ID is never permission to replace it.
export const GUILD_RESIDENTS_KEY = "fc_guild_residents_v1";
export const GUILD_RESIDENT_SLOT = "fc_guild_resident_slot";
const STATES = new Set(["never", "unknown", "spawning", "conflict", "bound", "dead"]);
const PROVENANCE = new Set(["spawn", "marker", "legacy-tag", "legacy-inferred"]);
const FLOORS = new Set([
  "minecraft:stone_bricks", "minecraft:mossy_stone_bricks", "minecraft:cracked_stone_bricks",
  "minecraft:chiseled_stone_bricks", "minecraft:smooth_stone", "minecraft:cobblestone",
  "minecraft:mossy_cobblestone", "minecraft:spruce_planks", "minecraft:dark_oak_planks",
  "minecraft:oak_planks", "minecraft:red_wool", "minecraft:grass_block", "minecraft:moss_block",
  "minecraft:coarse_dirt", "minecraft:dirt_path", "minecraft:deepslate_tiles", "minecraft:podzol",
  "minecraft:emerald_block", "minecraft:sea_lantern", "minecraft:obsidian", "minecraft:crying_obsidian",
]);
const OFFSETS = [[0, 0], [-1, 0], [1, 0], [0, -1], [0, 1],
  [-1, -1], [1, -1], [-1, 1], [1, 1], [-2, 0], [2, 0], [0, -2], [0, 2]];
const finitePoint = p => p && [p.x, p.y, p.z].every(Number.isFinite);
const sameBase = (a, b) => finitePoint(a) && finitePoint(b)
  && a.x === b.x && a.y === b.y && a.z === b.z;
const usable = e => { try { return !!e && e.isValid !== false && typeof e.id === "string"; } catch { return false; } };

// Home anchors identify columns. Only a new birth may choose a clear column
// centre within two horizontal blocks, at the authored height. No entity moves.
// Bounds cover the emitted resident colliders (Maze is tallest at 2.052).
export function guildResidentSpawnPoint(dimension, home, slot) {
  if (!finitePoint(home)) return undefined;
  const height = slot.type === "fc:maze" ? 2.1 : 2;
  for (const [dx, dz] of OFFSETS) {
    const point = { x: Math.floor(home.x) + dx + 0.5, y: home.y, z: Math.floor(home.z) + dz + 0.5 };
    try {
      let clear = true;
      for (let x = Math.floor(point.x - 0.4); x <= Math.floor(point.x + 0.4); x++) {
        for (let z = Math.floor(point.z - 0.4); z <= Math.floor(point.z + 0.4); z++) {
          if (!FLOORS.has(dimension.getBlock({ x, y: Math.floor(point.y) - 1, z })?.typeId)) clear = false;
          for (let y = Math.floor(point.y); y < Math.ceil(point.y + height); y++) {
            if (!dimension.getBlock({ x, y, z })?.isAir) clear = false;
          }
        }
      }
      if (clear && dimension.getEntities({ location: point, maxDistance: 2 }).length === 0) return point;
    } catch { /* unloaded/unknown terrain or failed occupancy query refuses birth */ }
  }
  return undefined;
}

export function createGuildResidentsController({ slots, read, write, lookup, candidates,
  spawnPoint, spawn, onCampus }) {
  const definitions = new Map(slots.map(slot => [slot.id, slot]));
  const types = new Set(slots.map(slot => slot.type));
  const observed = new Map(), unattempted = new Set();
  let state, dirty = false, blocked;

  function valid(saved) {
    if (!saved || saved.schema !== 1 || !["fresh", "legacy"].includes(saved.origin)
      || !finitePoint(saved.base) || !Array.isArray(saved.residents) || saved.residents.length !== slots.length) return false;
    const usedSlots = new Set(), usedIds = new Set();
    for (const r of saved.residents) {
      if (!r || usedSlots.has(r.slot) || definitions.get(r.slot)?.type !== r.type || !STATES.has(r.status)) return false;
      usedSlots.add(r.slot);
      if ((r.status === "never" || r.status === "spawning") && saved.origin !== "fresh") return false;
      if (r.status === "unknown" && saved.origin !== "legacy") return false;
      if (r.status === "bound" || r.status === "dead") {
        if (typeof r.entityId !== "string" || !r.entityId || usedIds.has(r.entityId) || !PROVENANCE.has(r.provenance)) return false;
        usedIds.add(r.entityId);
      } else if (r.entityId !== undefined || r.provenance !== undefined) return false;
    }
    return true;
  }
  function flush() {
    if (!dirty) { blocked = undefined; return true; }
    try { write(JSON.stringify(state)); dirty = false; blocked = undefined; return true; }
    catch { blocked = "save-failed"; return false; }
  }
  function initialize(base, fresh = false) {
    if (!finitePoint(base)) { blocked = "invalid-base"; return false; }
    if (!state) {
      let raw;
      try { raw = read(); } catch { blocked = "read-failed"; return false; }
      if (raw === undefined) {
        state = { schema: 1, origin: fresh ? "fresh" : "legacy", base: { ...base },
          residents: slots.map(s => ({ slot: s.id, type: s.type, status: fresh ? "never" : "unknown" })) };
        dirty = true;
      } else {
        let saved;
        try { saved = typeof raw === "string" ? JSON.parse(raw) : undefined; } catch { }
        if (!valid(saved)) { blocked = "invalid-registry"; return false; }
        state = saved;
      }
    }
    if (!sameBase(state.base, base)) { blocked = "base-mismatch"; return false; }
    return flush();
  }
  function marker(record) {
    return `${state.base.x},${state.base.y},${state.base.z}/${record.slot}`;
  }
  function observe(entity) {
    try {
      if (!usable(entity) || !types.has(entity.typeId)) return false;
      observed.set(entity.id, entity); return true;
    } catch { return false; }
  }
  function metadata(record, entity) {
    try {
      const current = entity.getDynamicProperty(GUILD_RESIDENT_SLOT);
      if (current !== undefined && current !== marker(record)) return false;
      if (current === undefined) entity.setDynamicProperty(GUILD_RESIDENT_SLOT, marker(record));
      if (entity.getDynamicProperty(GUILD_RESIDENT_SLOT) !== marker(record)) return false;
      if (!entity.hasTag("fc_guild_npc")) entity.addTag("fc_guild_npc");
      if (definitions.get(record.slot).guard && !entity.hasTag("fc_guild_guard")) entity.addTag("fc_guild_guard");
      return entity.hasTag("fc_guild_npc") && (!definitions.get(record.slot).guard || entity.hasTag("fc_guild_guard"));
    } catch { return false; }
  }
  function bind(record, entity, provenance) {
    record.status = "bound"; record.entityId = entity.id; record.provenance = provenance;
    dirty = true;
    // A marker can recover a spawn interrupted before the world save. If it
    // fails, the original ID remains in memory and no second spawn is allowed.
    metadata(record, entity);
    return flush();
  }
  function collect() {
    try { for (const entity of candidates()) observe(entity); } catch { }
    for (const r of state.residents) if (r.status === "bound") {
      try { observe(lookup(r.entityId)); } catch { /* not evidence of death */ }
    }
    const found = [];
    for (const [id, entity] of observed) {
      if (!usable(entity)) { observed.delete(id); continue; }
      try {
        found.push({ entity, id, type: entity.typeId, marker: entity.getDynamicProperty(GUILD_RESIDENT_SLOT),
          tagged: entity.hasTag("fc_guild_npc") || (entity.typeId === "fc:guard_bowerstone" && entity.hasTag("fc_guild_guard")) });
      } catch { /* no adoption with unreadable identity metadata */ }
    }
    return found;
  }
  function adopt(found) {
    const assigned = new Set(state.residents.map(r => r.entityId).filter(Boolean));
    for (const r of state.residents) {
      if (!["unknown", "spawning", "never", "conflict"].includes(r.status)) continue;
      const matches = found.filter(e => e.marker === marker(r));
      if (!matches.length) continue;
      if (matches.length !== 1 || matches[0].type !== r.type || assigned.has(matches[0].id)) {
        // Competing/copied metadata is evidence against a new birth, even for
        // a fresh never-spawned slot. Persist the reservation across reload.
        unattempted.delete(r.slot);
        if (r.status !== "conflict") { r.status = "conflict"; dirty = true; if (!flush()) return false; }
        continue;
      }
      if (!bind(r, matches[0].entity, "marker")) return false;
      assigned.add(matches[0].id); unattempted.delete(r.slot);
    }
    if (state.origin !== "legacy") return true;
    for (const type of types) {
      for (const tagged of [true, false]) {
        const empty = state.residents.filter(r => r.type === type && r.status === "unknown");
        if (!empty.length) continue;
        const inferredType = ["fc:guildmaster", "fc:maze", "fc:theresa"].includes(type) || type.startsWith("fc:guild_apprentice_");
        const campusCandidate = e => { try { return inferredType && onCampus(e); } catch { return false; } };
        const choices = found.filter(e => e.type === type && !assigned.has(e.id) && e.marker === undefined
          && e.tagged === tagged && (tagged || campusCandidate(e.entity)))
          .sort((a, b) => a.id < b.id ? -1 : a.id > b.id ? 1 : 0);
        // A loaded excess cannot establish which historical entity owns a slot.
        if (choices.length > empty.length) break;
        for (let i = 0; i < choices.length; i++) {
          if (!bind(empty[i], choices[i].entity, tagged ? "legacy-tag" : "legacy-inferred")) return false;
          assigned.add(choices[i].id);
        }
      }
    }
    return true;
  }
  function reconcile(base, allowSpawn = false) {
    if (!initialize(base)) return;
    const found = collect();
    if (!adopt(found)) return;
    for (const r of state.residents) {
      if (r.status === "bound") {
        const entity = found.find(e => e.id === r.entityId && e.type === r.type)?.entity;
        if (entity) metadata(r, entity);
        continue;
      }
      if (!allowSpawn || state.origin !== "fresh" || (r.status !== "never" && !unattempted.has(r.slot))) continue;
      const slot = definitions.get(r.slot);
      let point;
      try { point = spawnPoint(slot, state.base); } catch { }
      if (!finitePoint(point)) continue;
      if (r.status === "never") {
        r.status = "spawning"; dirty = true; unattempted.add(r.slot);
        if (!flush()) return;
      }
      // Clear the in-memory permission before native spawn, including calls
      // that throw or return no handle. Persisted intent never authorizes retry.
      unattempted.delete(r.slot);
      let entity;
      try { entity = spawn(slot, point); } catch { continue; }
      if (!usable(entity) || entity.typeId !== r.type || state.residents.some(s => s.entityId === entity.id)) continue;
      observe(entity);
      if (!bind(r, entity, "spawn")) return;
    }
  }
  function recordDeath(entity) {
    let id;
    try { id = entity.id; } catch { return false; }
    const r = state?.residents.find(s => s.status === "bound" && s.entityId === id);
    if (!r) return false;
    r.status = "dead"; dirty = true; observed.delete(id); flush(); return true;
  }
  function removed(id) { observed.delete(id); }
  // Read-only activity authority: never trust an optimistic cached enrollment,
  // adopt an entity, flush a failed save, or rewrite its marker from this path.
  function binding(entity, base) {
    try {
      if (!entity || entity.isValid !== true || typeof entity.id !== "string" || !entity.id) return { kind: "blocked", reason: "invalid-entity" };
      const raw = read();
      const saved = typeof raw === "string" ? JSON.parse(raw) : undefined;
      if (!valid(saved) || !sameBase(saved.base, base)) return { kind: "blocked", reason: "unavailable-registry" };
      const current = entity.getDynamicProperty(GUILD_RESIDENT_SLOT);
      const record = saved.residents.find(r => r.entityId === entity.id);
      if (!record) {
        const copied = saved.residents.some(r => current === `${saved.base.x},${saved.base.y},${saved.base.z}/${r.slot}`);
        return { kind: copied ? "blocked" : "other", reason: copied ? "unbound-marker" : undefined };
      }
      if (record.status !== "bound" || record.type !== entity.typeId
        || current !== `${saved.base.x},${saved.base.y},${saved.base.z}/${record.slot}`) return { kind: "blocked", reason: "identity-mismatch" };
      return { kind: "bound", slot: record.slot, entityId: record.entityId, type: record.type, base: { ...saved.base } };
    } catch { return { kind: "blocked", reason: "unreadable-registry" }; }
  }
  function snapshot() { return { blocked, state: state ? JSON.parse(JSON.stringify(state)) : undefined }; }
  return { initialize, reconcile, observe, removed, recordDeath, snapshot, binding };
}

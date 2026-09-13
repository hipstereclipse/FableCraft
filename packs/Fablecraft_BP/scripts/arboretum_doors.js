// Owned Arboretum pilot. All Bedrock effects are injected; saved records, not
// replaceable faces or coordinate personas, own identity and return history.
export const ARBORETUM = Object.freeze({
  id: "fc:arboretum", version: 1, size: { x: 49, y: 28, z: 49 },
  arrival: { x: 24.5, y: 3, z: 7.5 }, exit: { x: 24.5, y: 3, z: 3.5 },
  chest: { x: 34, y: 3, z: 35 }, item: "fc:wellows_pickhammer",
  routeWaypoints: [[24, 12], [17, 12], [13, 19], [13, 29], [19, 35],
    [28, 35], [31, 31], [37, 24], [35, 16], [29, 12], [24, 12]],
  chestApproach: [[31, 31], [34, 34]],
  returnDetectorCells: [{ x: 24, y: 2, z: 3 }, { x: 24, y: 7, z: 3 }],
  returnDetectorBlocks: ["minecraft:chiseled_stone_bricks", "minecraft:sea_lantern"],
});
export const ARBORETUM_INDEX_KEY = "fc_dp_arbor_index_v1";
export const ARBORETUM_WITNESS_KEY = "fc_dp_arbor_initialized_v1";
export const ARBORETUM_RETURN_KEY = "fc_dp_arbor_return_v1";
export const ARBORETUM_SOURCE = Object.freeze({ offset: { x: 32.5, y: 6, z: 7.5 },
  normal: { x: 0, y: 0, z: -1 }, throat: { min: { x: 31, y: 6, z: 7 }, max: { x: 33, y: 9, z: 11 } },
  fallbackOffset: { x: 0, y: 0, z: -1 } });
export const arboretumStateKey = (id) => `fc_dp_arbor_v1_${String(id).split(":")[1]}`;
export const arboretumCellKey = (cell) => `fc_dp_arbor_cell_v1_${cell}`;
export const arboretumOrigin = (cell) => ({ x: 620000 + cell % 64 * 128, y: 272, z: 600000 + Math.floor(cell / 64) * 128 });
const ROOM_LEASE = "fc_dp_arbor_load", RETURN_LEASE = "fc_dp_arbor_return";
const ARCHETYPE = "greatwood_gorge_arboretum";
const add = (a, b) => ({ x: a.x + b.x, y: a.y + b.y, z: a.z + b.z });
const point = (p) => !!p && [p.x, p.y, p.z].every(Number.isFinite);
const distance = (a, b) => Math.hypot(a.x - b.x, a.y - b.y, a.z - b.z);
const same = (a, b) => JSON.stringify(a) === JSON.stringify(b);
const copy = (v) => JSON.parse(JSON.stringify(v));
const integer = (v, min, max) => Number.isInteger(v) && v >= min && v <= max;
const validId = (id) => typeof id === "string" && /^arboretum:(?:[0-9]|[1-5][0-9]|6[0-3])$/.test(id);
const dimensions = ["minecraft:overworld", "minecraft:nether", "minecraft:the_end"];
const sourcePoint = (p) => point(p) && dimensions.includes(p.dimension)
  && Math.abs(p.x) < 30000000 && Math.abs(p.z) < 30000000 && p.y >= -63 && p.y <= 317;
const originValid = (p) => sourcePoint({ ...p, y: p?.y + 1 })
  && [p.x, p.y, p.z].every(Number.isInteger) && p.y <= 304;
const sourceFor = (origin) => ({ ...add(origin, ARBORETUM_SOURCE.offset), dimension: origin.dimension });
const heroId = (id) => typeof id === "string" && id.length > 0 && id.length <= 128;
const openingAt = (p, a) => point(p) && Math.abs(p.x - a.x) <= 1.35
  && Math.abs(p.z - a.z) <= 0.9 && p.y >= a.y - 0.15 && p.y <= a.y + 2.4;
export const inArboretum = (p, cell, margin = 0) => {
  if (!point(p) || !integer(cell, 0, 4095)) return false;
  const o = arboretumOrigin(cell);
  return p.x >= o.x - margin && p.x < o.x + 49 + margin
    && p.y >= o.y - margin && p.y < o.y + 28 + margin
    && p.z >= o.z - margin && p.z < o.z + 49 + margin;
};
const shell = [];
for (let x = 0; x < 49; x++) for (let y = 0; y < 28; y++) for (let z = 0; z < 49; z++) {
  if ([0, 48].includes(x) || [0, 27].includes(y) || [0, 48].includes(z)) shell.push({ x, y, z });
}
const sentinels = shell.filter(p => [0, 24, 48].includes(p.x) && [0, 14, 27].includes(p.y) && [0, 24, 48].includes(p.z));
const route = [];
for (const path of [ARBORETUM.routeWaypoints, ARBORETUM.chestApproach, [[24, 3], [24, 12]]]) {
  for (let i = 1; i < path.length; i++) {
    const [x, z] = path[i - 1], [tx, tz] = path[i], steps = Math.ceil(Math.hypot(tx - x, tz - z) * 2);
    for (let n = 0; n <= steps; n++) route.push({ x: x + 0.5 + (tx - x) * n / steps, y: 3, z: z + 0.5 + (tz - z) * n / steps });
  }
}
const floorIds = new Set(["stone", "stone_bricks", "chiseled_stone_bricks", "mossy_stone_bricks", "cracked_stone_bricks", "cobblestone", "mossy_cobblestone", "grass_block", "dirt", "coarse_dirt", "dirt_with_roots", "rooted_dirt", "podzol", "moss_block", "grass_path", "dirt_path", "gravel", "andesite", "polished_andesite", "deepslate", "polished_deepslate", "bedrock", "oak_planks", "dark_oak_planks", "spruce_planks"].map(id => `minecraft:${id}`));

export function createArboretumDoors({ world, system, ItemStack, definition = null,
  sourceReady = () => false, canEnter = () => true, readAlignment = () => null, canWitnessUse = () => false,
  volumeIsEmpty = () => false, volumeIsBlock = () => false, report = () => {}, placeRoom = null }) {
  if (definition && (definition.id !== ARCHETYPE || definition.destination?.structure !== ARBORETUM.id)) throw new Error("Arboretum definition does not match its room contract.");
  let job = null, roomLease = null, returnLease = null;
  const verified = new Set(), retryAt = new Map(), opening = new Map(), approaches = new Map();
  const dwell = new Map(), cooldown = new Map(), disarmed = new Set(), seen = new Set();
  const returnQueue = new Map(), notices = new Map();
  const now = () => system.currentTick;
  const log = (s) => { try { report(s); } catch { } };
  const dim = (id = "minecraft:overworld") => world.getDimension(id);
  const usable = (p) => { try { return p?.isValid === true && heroId(p.id) && point(p.location) && dimensions.includes(p.dimension.id); } catch { return false; } };
  function property(owner, key) {
    try { const raw = owner.getDynamicProperty(key); return { available: true, raw }; }
    catch { return { available: false }; }
  }
  function parsed(raw) { try { return JSON.parse(raw); } catch { return null; } }
  function write(owner, key, value) {
    const raw = value === undefined ? undefined : JSON.stringify(value);
    try {
      owner.setDynamicProperty(key, raw);
      return owner.getDynamicProperty(key) === raw;
    } catch { return false; }
  }
  function index() {
    const w = property(world, ARBORETUM_WITNESS_KEY), p = property(world, ARBORETUM_INDEX_KEY);
    if (!w.available || !p.available || w.raw !== "1") return null;
    const r = parsed(p.raw);
    if (!r || r.schema !== 1 || !integer(r.nextCell, 0, 4096) || !Array.isArray(r.entries) || r.entries.length > 64) return null;
    const regions = new Set();
    for (let i = 0; i < r.entries.length; i++) {
      const e = r.entries[i];
      if (e?.id !== `arboretum:${i}` || typeof e.regionKey !== "string" || !e.regionKey || e.regionKey.length > 96
        || regions.has(e.regionKey) || !originValid(e.origin) || !same(e.source, sourceFor(e.origin))) return null;
      regions.add(e.regionKey);
    }
    return r;
  }
  function pristine() {
    const w = property(world, ARBORETUM_WITNESS_KEY), p = property(world, ARBORETUM_INDEX_KEY);
    if (!w.available || !p.available || w.raw !== undefined || p.raw !== undefined) return false;
    for (let i = 0; i < 64; i++) {
      const old = property(world, arboretumStateKey(`arboretum:${i}`));
      if (!old.available || old.raw !== undefined) return false;
    }
    // An orphaned reservation is also positive evidence of established history.
    // The stable property-name query avoids thousands of reads in a new world.
    try {
      if (typeof world.getDynamicPropertyIds === "function") {
        if (world.getDynamicPropertyIds().some(k => k.startsWith("fc_dp_arbor_cell_v1_"))) return false;
      } else {
        for (let i = 0; i < 4096; i++) {
          const old = property(world, arboretumCellKey(i));
          if (!old.available || old.raw !== undefined) return false;
        }
      }
    } catch { return false; }
    return true;
  }
  function initialize() {
    const established = index();
    if (established) return established;
    if (!pristine()) return null;
    // The witness is committed first. Missing established history never becomes
    // a new allocator. Losing every property and witness is not detectable.
    if (!write(world, ARBORETUM_WITNESS_KEY, 1)) return null;
    if (!write(world, ARBORETUM_INDEX_KEY, { schema: 1, nextCell: 0, entries: [] })) return null;
    return index();
  }
  function getState(id, registry = index()) {
    if (!validId(id) || !registry) return null;
    const e = registry.entries[Number(id.split(":")[1])];
    if (!e || e.id !== id) return null;
    const p = property(world, arboretumStateKey(id)), r = p.available ? parsed(p.raw) : null;
    if (!r || r.schema !== 1 || r.id !== id || r.archetype !== ARCHETYPE
      || !same(r.origin, e.origin) || !same(r.source, e.source) || r.regionKey !== e.regionKey
      || !same(r.normal, { x: 0, z: -1 }) || !integer(r.revision, 0, Number.MAX_SAFE_INTEGER)
      || !["pending", "placed", "confirmed"].includes(r.placement) || typeof r.unlocked !== "boolean"
      || !Array.isArray(r.progress) || r.progress.length > 64
      || !r.reward || typeof r.reward.seeded !== "boolean" || typeof r.reward.claimed !== "boolean") return null;
    const heroes = new Set();
    for (const h of r.progress) {
      if (!heroId(h?.heroId) || heroes.has(h.heroId) || !integer(h.count, 1, 10) || !integer(h.lastTick, 0, Number.MAX_SAFE_INTEGER)) return null;
      heroes.add(h.heroId);
    }
    if (r.placement !== "confirmed" && (r.unlocked || r.room || r.progress.length || r.reward.seeded || r.reward.claimed)) return null;
    if (r.room !== null) {
      const room = r.room;
      if (!room || !r.unlocked || !integer(room.cell, 0, registry.nextCell - 1)
        || !same(room.origin, arboretumOrigin(room.cell)) || room.version !== 1 || typeof room.visited !== "boolean"
        || !["allocated", "placing", "seeding", "ready"].includes(room.phase)
        || room.visited && room.phase !== "ready" || (room.phase === "ready") !== r.reward.seeded) return null;
      const preparation = room.preparation;
      if (preparation !== undefined && (!preparation || preparation.schema !== 1
        || !({ placing: ["placing", "placed"], seeding: ["seeding", "seeded"], ready: ["seeded"] })[room.phase]?.includes(preparation.phase))) return null;
      const reservation = property(world, arboretumCellKey(room.cell));
      if (!reservation.available || parsed(reservation.raw) !== id) return null;
    } else if (r.reward.seeded || r.reward.claimed) return null;
    if (r.reward.claimed && !r.reward.seeded) return null;
    return r;
  }
  function save(r, expected = null) {
    const current = getState(r.id);
    if (!current || current.revision !== r.revision || r.revision >= Number.MAX_SAFE_INTEGER
      || expected && !same(current, expected)) return false;
    const next = { ...r, revision: r.revision + 1 };
    if (!write(world, arboretumStateKey(r.id), next)) return false;
    r.revision = next.revision;
    return true;
  }
  function records() {
    const registry = index();
    return registry ? registry.entries.map(e => getState(e.id, registry)).filter(Boolean) : [];
  }
  function sources({ includePending = false } = {}) {
    if (!includePending) return records().filter(r => r.placement === "confirmed");
    const registry = index();
    return registry ? registry.entries.map(e => getState(e.id, registry) ?? { ...copy(e), placement: "unavailable", quarantined: true }) : [];
  }
  function getPlacement(regionKey) {
    const registry = index(), e = registry?.entries.find(v => v.regionKey === regionKey);
    return e ? getState(e.id, registry) ?? { ...copy(e), placement: "unavailable" } : null;
  }
  function isRecordedRegion(regionKey) {
    const registry = index();
    return registry ? registry.entries.some(e => e.regionKey === regionKey) : !pristine();
  }
  function beginPlacement({ regionKey, origin } = {}) {
    if (typeof regionKey !== "string" || !regionKey || regionKey.length > 96 || !originValid(origin) || !sourcePoint(sourceFor(origin))) return null;
    const registry = initialize();
    if (!registry || registry.entries.length >= 64 || registry.entries.some(e => e.regionKey === regionKey)) return null;
    const id = `arboretum:${registry.entries.length}`, prior = property(world, arboretumStateKey(id));
    if (!prior.available || prior.raw !== undefined) return null;
    const entry = { id, regionKey, origin: copy(origin), source: sourceFor(origin) };
    registry.entries.push(entry);
    if (!write(world, ARBORETUM_INDEX_KEY, registry)) return null;
    const r = { schema: 1, ...entry, archetype: ARCHETYPE, normal: { x: 0, z: -1 }, revision: 0,
      placement: "pending", unlocked: false, progress: [], room: null, reward: { seeded: false, claimed: false } };
    return write(world, arboretumStateKey(id), r) ? id : null;
  }
  function sourceIsReady(r) { try { return sourceReady(copy(r)) === true; } catch { return false; } }
  function recordPlaced(id) {
    const r = getState(id);
    if (!r) return false;
    if (r.placement !== "pending") return true;
    r.placement = "placed";
    return save(r);
  }
  function confirmPlacement(id) {
    const r = getState(id);
    if (!r) return false;
    if (r.placement === "confirmed") return sourceIsReady(r);
    if (r.placement !== "placed") return false;
    if (!sourceIsReady(r)) return false;
    r.placement = "confirmed";
    return save(r);
  }
  function sourceAt(dimensionId, position) {
    if (!point(position)) return null;
    const found = sources({ includePending: true }).filter(r => r.source.dimension === dimensionId
      && Math.hypot(position.x - r.source.x, position.z - r.source.z) < 0.1
      && position.y >= r.source.y - 0.1 && position.y <= r.source.y + 5.1);
    return found.length === 1 ? found[0] : null;
  }
  function isCanonicalFace(face) {
    try {
      const marker = face.getDynamicProperty("fc_door_identity");
      return typeof marker === "string" && marker.startsWith("arboretum:") || !!sourceAt(face.dimension.id, face.location);
    } catch { return true; } // Unreadable identity must not become a legacy persona.
  }
  function bindFace(face, id = null) {
    try {
      if (face?.isValid !== true || face.typeId !== "fc:demon_door") return null;
      const r = sourceAt(face.dimension.id, face.location);
      if (!r || r.placement !== "confirmed" || id !== null && r.id !== id) return null;
      const marker = face.getDynamicProperty("fc_door_identity");
      if (marker !== undefined && marker !== r.id) return null;
      if (marker === undefined && (face.getDynamicProperty("fc_door_idx") !== undefined || face.getDynamicProperty("fc_door_open") === true)) return null;
      face.setDynamicProperty("fc_door_identity", r.id);
      return face.getDynamicProperty("fc_door_identity") === r.id ? r.id : null;
    } catch { return null; }
  }
  function reconcileFace(face, id = null) {
    const bound = bindFace(face, id), r = bound && getState(bound);
    if (!r) return false;
    try {
      if (r.unlocked) {
        face.setDynamicProperty("fc_door_open", true); face.triggerEvent("fc:open");
        if (!opening.has(r.id)) face.teleport(add(r.source, { x: 0, y: 5, z: 0 }));
      }
    } catch { }
    return true;
  }
  function notice(p, message) {
    const key = `${p.id}/${message}`;
    if (now() - (notices.get(key) ?? -1000) < 100) return;
    notices.set(key, now());
    try { p.sendMessage(`§5Demon Door: §7${message}`); } catch { }
  }
  function inSight(p, r) { return usable(p) && p.dimension.id === r.source.dimension
    && distance(p.location, r.source) <= 6 && p.location.z <= r.source.z - 0.25; }
  function unlock(r, p, face = null) {
    if (r.unlocked) return true;
    if (!sourceIsReady(r)) return false;
    r.unlocked = true;
    if (!save(r)) return false;
    if (face) opening.set(r.id, { face, source: copy(r.source), start: now() });
    try { face?.setDynamicProperty("fc_door_open", true); face?.triggerEvent("fc:open"); p.playSound("fc.door_rumble"); } catch { }
    notice(p, definition?.success ?? "Such wickedness. The Arboretum is open; step through and discover what it guards.");
    ensureRoom(r);
    return true;
  }
  function interact(p, face) {
    if (!isCanonicalFace(face)) return false;
    const id = bindFace(face), r = id && getState(id);
    if (!r || !inSight(p, r)) return true;
    if (r.unlocked) { reconcileFace(face); notice(p, "The Arboretum awaits beyond this opening."); return true; }
    let alignment = null;
    try { alignment = readAlignment(p); } catch { }
    if (alignment === -1000 || r.progress.some(h => h.heroId === p.id && h.count === 10)) unlock(r, p, face);
    else notice(p, definition?.requirement?.hint ?? "Show me great evil. Eat ten Crunchy Chicks here before my eyes, or return wholly evil.");
    return true;
  }
  function completeUse(p, itemId, alignmentSnapshot) {
    if (itemId !== "fc:crunchy_chick" || !usable(p)) return false;
    try { if (canWitnessUse(p) !== true) return false; } catch { return false; }
    const witnesses = sources().filter(r => !r.unlocked && inSight(p, r));
    if (witnesses.length !== 1) return false;
    const r = witnesses[0];
    if (!sourceIsReady(r)) return false;
    let h = r.progress.find(v => v.heroId === p.id);
    if (h && (h.count === 10 || h.lastTick === now()) || !h && r.progress.length >= 64) return false;
    if (!h) { h = { heroId: p.id, count: 0, lastTick: now() }; r.progress.push(h); }
    h.count++; h.lastTick = now();
    // Credit and unlock share a record write. Native food consumption has
    // already occurred; never consume/refund again on an ambiguous save.
    if (alignmentSnapshot === undefined) { try { alignmentSnapshot = readAlignment(p); } catch { alignmentSnapshot = null; } }
    if (h.count === 10 || alignmentSnapshot === -1000) r.unlocked = true;
    if (!save(r)) return false;
    if (r.unlocked) { notice(p, "I saw every wicked bite. The Arboretum is open."); ensureRoom(r); }
    return true;
  }
  function blockAt(d, p) { try { return d.getBlock(p) ?? null; } catch { return null; } }
  const air = b => !!b && (b.isAir === true || b.typeId === "minecraft:air");
  function safe(d, p) {
    if (!point(p)) return false;
    for (const dx of [-0.3, 0.3]) for (const dz of [-0.3, 0.3]) {
      const x = Math.floor(p.x + dx), z = Math.floor(p.z + dz), y = Math.floor(p.y);
      if (!floorIds.has(blockAt(d, { x, y: y - 1, z })?.typeId)) return false;
      for (let h = y; h < Math.ceil(p.y + 1.8); h++) if (!air(blockAt(d, { x, y: h, z }))) return false;
    }
    return true;
  }
  function inventory(r) {
    try { return blockAt(dim(), add(r.room.origin, ARBORETUM.chest))?.getComponent("minecraft:inventory")?.container ?? null; }
    catch { return null; }
  }
  function emptyInventory(c) {
    try { return c?.size === 27 && Array.from({ length: c.size }, (_, i) => c.getItem(i)).every(item => !item); }
    catch { return false; }
  }
  function rewardVerified(r) {
    try {
      const c = inventory(r);
      if (c?.size !== 27) return false;
      const item = c.getItem(0);
      return item?.typeId === ARBORETUM.item && item.amount === 1
        && (item.nameTag ?? "") === "" && same(item.getLore(), [])
        && Array.from({ length: c.size - 1 }, (_, i) => c.getItem(i + 1)).every(slot => !slot);
    } catch { return false; }
  }
  function jobCurrent() { return !!job && same(getState(job.id), job.authority); }
  function savePreparation(r) {
    if (!job || !save(r, job.authority)) return false;
    job.authority = copy(r);
    return jobCurrent();
  }
  function roomVerified(r) {
    if (!r.room) return false;
    const d = dim(), o = r.room.origin;
    return route.every(p => safe(d, add(o, p))) && safe(d, add(o, ARBORETUM.arrival))
      && safe(d, add(o, ARBORETUM.exit)) && safe(d, add(o, { x: 34.5, y: 3, z: 34.5 }))
      && sentinels.every(p => blockAt(d, add(o, p))?.typeId === "minecraft:barrier")
      && ARBORETUM.returnDetectorCells.every((p, i) => blockAt(d, add(o, p))?.typeId === ARBORETUM.returnDetectorBlocks[i])
      && blockAt(d, add(o, ARBORETUM.chest))?.typeId === "minecraft:chest"
      && air(blockAt(d, add(o, { ...ARBORETUM.chest, y: 4 }))) && !!inventory(r);
  }
  function shellIntact(o) {
    try {
      for (const [at, size] of [
        [{ x: 0, y: 0, z: 0 }, { x: 1, y: 28, z: 49 }], [{ x: 48, y: 0, z: 0 }, { x: 1, y: 28, z: 49 }],
        [{ x: 0, y: 0, z: 0 }, { x: 49, y: 1, z: 49 }], [{ x: 0, y: 27, z: 0 }, { x: 49, y: 1, z: 49 }],
        [{ x: 0, y: 0, z: 0 }, { x: 49, y: 28, z: 1 }], [{ x: 0, y: 0, z: 48 }, { x: 49, y: 28, z: 1 }],
      ]) if (volumeIsBlock(dim(), add(o, at), size, "minecraft:barrier") !== true) return false;
      return true;
    } catch { return false; }
  }
  function removeLease(name, held) {
    if (held) { try { dim(held.dimension).runCommand(`tickingarea remove ${name}`); } catch { } }
  }
  function lease(name, dimensionId, origin, size) {
    try {
      // Remove only this owner's names, including a prior-reload lease in a
      // different supported dimension. No tickingarea remove_all is used.
      for (const d of dimensions) { try { dim(d).runCommand(`tickingarea remove ${name}`); } catch { } }
      const end = add(origin, { x: size.x - 1, y: size.y - 1, z: size.z - 1 });
      const result = dim(dimensionId).runCommand(`tickingarea add ${Math.floor(origin.x)} ${Math.floor(origin.y)} ${Math.floor(origin.z)} ${Math.floor(end.x)} ${Math.floor(end.y)} ${Math.floor(end.z)} ${name} true`);
      return result?.successCount === 0 ? null : { dimension: dimensionId, used: now() };
    } catch { log("Arboretum loading authority is unavailable; travel deferred."); return null; }
  }
  function allocate(r) {
    const expected = copy(r);
    if (r.revision >= Number.MAX_SAFE_INTEGER || !same(getState(r.id), expected)) return false;
    const registry = index();
    if (!registry || registry.nextCell >= 4096) return false;
    const cell = registry.nextCell++;
    if (!write(world, ARBORETUM_INDEX_KEY, registry)) return false;
    const reserved = property(world, arboretumCellKey(cell));
    if (!reserved.available || reserved.raw !== undefined || !write(world, arboretumCellKey(cell), r.id)) return false;
    r.room = { cell, origin: arboretumOrigin(cell), version: 1, phase: "allocated", visited: false };
    return save(r, expected); // A failed write burns the reservation; it is never recycled.
  }
  const verifiedKey = r => `${r.id}/${r.room.cell}`;
  function ensureRoom(r) {
    if (!r?.unlocked || r.placement !== "confirmed" || job || now() < (retryAt.get(r.id) ?? 0)) return;
    if (r.room?.phase === "placing" && r.room.preparation?.phase !== "placed"
      || r.room?.phase === "seeding" && r.room.preparation?.phase !== "seeded") {
      retryAt.set(r.id, now() + 200); log("Arboretum preparation is ambiguous; no placement replay, reseeding or admission."); return;
    }
    if (r.room?.phase === "ready" && verified.has(verifiedKey(r)) && roomVerified(r)) return;
    if (!r.room && !allocate(r)) return;
    removeLease(ROOM_LEASE, roomLease);
    roomLease = lease(ROOM_LEASE, "minecraft:overworld", r.room.origin, ARBORETUM.size);
    if (!roomLease) { retryAt.set(r.id, now() + 200); return; }
    job = { id: r.id, cell: r.room.cell, authority: copy(r), start: now(), phase: r.room.phase === "allocated" ? "scan" : "verify", scan: 0, verify: 0, skips: 0 };
  }
  function failJob(message) {
    if (job) { verified.delete(`${job.id}/${job.cell}`); retryAt.set(job.id, now() + 200); }
    log(message); job = null; removeLease(ROOM_LEASE, roomLease); roomLease = null;
  }
  function playersRead() { try { return world.getPlayers(); } catch { return null; } }
  function unoccupied(o) {
    const ps = playersRead();
    if (!ps) return false;
    try {
      if (ps.some(p => p.dimension.id === "minecraft:overworld" && inArboretum(p.location, (o.x - 620000) / 128 + (o.z - 600000) / 128 * 64))) return false;
      return !dim().getEntities({ location: add(o, { x: 24, y: 14, z: 24 }), maxDistance: 45 }).some(e => {
        const p = e.location;
        return !point(p) || p.x >= o.x && p.x < o.x + 49 && p.y >= o.y && p.y < o.y + 28 && p.z >= o.z && p.z < o.z + 49;
      });
    } catch { return false; }
  }
  function tickBuild() {
    if (!job) return;
    const r = getState(job.id);
    if (!r?.room || r.room.cell !== job.cell || !r.unlocked || !same(r, job.authority)) { failJob("Arboretum room history changed or became unavailable; no reconstruction."); return; }
    if (now() - job.start > 1600) { failJob("Arboretum room loading timed out; source admission remains closed."); return; }
    roomLease.used = now();
    const o = r.room.origin, d = dim();
    if (job.phase === "scan") {
      for (let n = 0; n < 512 && job.scan < 49 * 28 * 49; n++, job.scan++) {
        const i = job.scan, p = add(o, { x: i % 49, y: Math.floor(i / 49) % 28, z: Math.floor(i / (49 * 28)) });
        const b = blockAt(d, p);
        if (!b) return;
        if (!air(b)) {
          if (++job.skips >= 8 || !jobCurrent() || !allocate(r)) { failJob("Arboretum candidate cells are occupied; nothing was cleared."); return; }
          removeLease(ROOM_LEASE, roomLease);
          roomLease = lease(ROOM_LEASE, "minecraft:overworld", r.room.origin, ARBORETUM.size);
          if (!roomLease) { failJob("Arboretum next candidate could not be loaded."); return; }
          job.cell = r.room.cell; job.authority = copy(r); job.scan = 0; job.start = now(); return;
        }
      }
      if (job.scan < 49 * 28 * 49) return;
      // A late edit must not be overwritten because an earlier slice was air.
      // The adapter performs one stable native bulk query with unloaded chunks
      // disallowed. Its failure/absence is never interpreted as empty.
      let empty = false;
      try { empty = volumeIsEmpty(d, o, ARBORETUM.size) === true; } catch { }
      if (!empty) { failJob("Arboretum volume changed during its survey or is unavailable; no blocks were placed."); return; }
      if (!unoccupied(o)) { failJob("Arboretum destination contains entities or cannot be inspected."); return; }
      r.room.phase = "placing";
      r.room.preparation = { schema: 1, phase: "placing" };
      if (!savePreparation(r)) { failJob("Arboretum placement journal could not commit."); return; }
      // Recheck native effects after the journal write. Intent alone never
      // authorizes recovery, even when an ambiguous call left a complete shell.
      try {
        if (volumeIsEmpty(d, o, ARBORETUM.size) !== true || !unoccupied(o) || !jobCurrent()) {
          failJob("Arboretum placement preconditions changed after its intent; no blocks were placed."); return;
        }
        if (placeRoom) placeRoom(d, o);
        else world.structureManager.place(ARBORETUM.id, d, o, { includeEntities: false });
      } catch { failJob("Arboretum placement is ambiguous; no structure replay."); return; }
      r.room.preparation.phase = "placed";
      if (!savePreparation(r)) { failJob("Arboretum placed receipt could not commit; no replay or reward writes."); return; }
      job.phase = "verify"; return;
    }
    if (job.phase === "verify") {
      for (let n = 0; n < 512 && job.verify < shell.length; n++, job.verify++) {
        const b = blockAt(d, add(o, shell[job.verify]));
        if (!b) return;
        if (b.typeId !== "minecraft:barrier") { failJob("Arboretum containment is incomplete; no rebuild or admission."); return; }
      }
      if (job.verify < shell.length || !roomVerified(r)) return;
      if (!shellIntact(o)) { failJob("Arboretum containment changed during verification; no admission."); return; }
      if (!jobCurrent()) { failJob("Arboretum verification history changed; no admission."); return; }
      if (r.room.phase === "ready") { verified.add(verifiedKey(r)); job = null; return; }
      if (r.room.visited || r.reward.seeded || !unoccupied(o)) { failJob("Arboretum preparation authority is unavailable."); return; }
      if (r.room.phase === "placing" && r.room.preparation?.phase === "placed") {
        if (!emptyInventory(inventory(r))) { failJob("Arboretum reward chest is not empty or readable; refusing to replace its contents."); return; }
        r.room.phase = "seeding"; r.room.preparation.phase = "seeding";
        if (!savePreparation(r)) { failJob("Arboretum seed journal could not commit."); return; }
        try {
          const item = new ItemStack(ARBORETUM.item, 1), c = inventory(r);
          if (!roomVerified(r) || !shellIntact(o) || !unoccupied(o) || !emptyInventory(c) || !jobCurrent()) {
            failJob("Arboretum seed preconditions changed after its intent; no reward was written."); return;
          }
          c.setItem(0, item);
        } catch { failJob("Arboretum reward transfer is ambiguous; no reseeding."); return; }
        // Reacquire the live chest; the handle used for setItem cannot prove
        // that the current destination contains the intended shared reward.
        if (!rewardVerified(r) || !roomVerified(r) || !shellIntact(o) || !unoccupied(o) || !jobCurrent()) {
          failJob("Arboretum reward could not be verified exactly; no admission or reseeding."); return;
        }
        r.room.preparation.phase = "seeded";
        if (!savePreparation(r)) { failJob("Arboretum seeded receipt could not commit; no reseeding."); return; }
      }
      // A durable seeded receipt permits only read-only verification and a
      // ready retry. Depleted visited rooms never pass through this branch.
      if (r.room.phase !== "seeding" || r.room.preparation?.phase !== "seeded"
        || !rewardVerified(r) || !roomVerified(r) || !shellIntact(o) || !unoccupied(o) || !jobCurrent()) {
        failJob("Arboretum final preparation changed; no admission or reseeding."); return;
      }
      r.reward.seeded = true; r.room.phase = "ready";
      if (!savePreparation(r)) { failJob("Arboretum ready journal could not commit; no reseeding."); return; }
      verified.add(verifiedKey(r)); job = null;
    }
  }
  function readTicket(p) {
    const v = property(p, ARBORETUM_RETURN_KEY), t = v.available ? parsed(v.raw) : null;
    const valid = t?.schema === 1 && t.family === "arboretum" && validId(t.id) && integer(t.cell, 0, 4095)
      && sourcePoint(t.source) && sourcePoint(t.door) && t.source.dimension === t.door.dimension && distance(t.source, t.door) <= 9
      && ["entering", "inside", "outside", "returning"].includes(t.phase);
    return { available: v.available, ticket: valid ? t : null };
  }
  function occupiedTicket(p, t) { return usable(p) && t && p.dimension.id === "minecraft:overworld" && inArboretum(p.location, t.cell) ? t : null; }
  function occupied(p, current = readTicket(p)) {
    if (!usable(p)) return null;
    const t = occupiedTicket(p, current.ticket);
    if (t) return { cell: t.cell, ticket: t, record: null };
    if (p.dimension.id !== "minecraft:overworld") return null;
    const matches = records().filter(r => r.room && inArboretum(p.location, r.room.cell));
    return matches.length === 1 ? { cell: matches[0].room.cell, ticket: null, record: matches[0] } : null;
  }
  function occupiedRealm(p) { return !!occupied(p); }
  function allowsOtherEntry(p) {
    const current = readTicket(p);
    return current.available && !occupied(p, current) && (!current.ticket || current.ticket.phase === "outside");
  }
  function protectedCells() {
    const cells = new Set(records().filter(r => r.room).map(r => r.room.cell));
    for (const p of playersRead() ?? []) {
      const t = occupiedTicket(p, readTicket(p).ticket);
      if (t) cells.add(t.cell);
    }
    return cells;
  }
  function protectsBlock(dimensionId, p) { return dimensionId === "minecraft:overworld" && [...protectedCells()].some(c => inArboretum(p, c)); }
  function excludesWorldPosition(dimensionId, p) { return dimensionId === "minecraft:overworld" && point(p)
    && [...protectedCells()].some(c => inArboretum({ ...p, y: 272 }, c, 160)); }
  function isReturnBlock(p, dimensionId, at) {
    if (dimensionId !== "minecraft:overworld" || !point(at)) return false;
    const inside = occupied(p);
    if (!inside) return false;
    const o = arboretumOrigin(inside.cell);
    return ARBORETUM.returnDetectorCells.some(q => at.x === o.x + q.x && at.y === o.y + q.y && at.z === o.z + q.z);
  }
  const fallback = (r, dx = 0) => ({ ...add(r.source, { x: dx, y: 0, z: -1 }), dimension: r.source.dimension });
  function approachSource(p, r) {
    const prior = approaches.get(`${p.id}/${r.id}`), d = dim(r.source.dimension);
    if (prior && prior.dimension === r.source.dimension && distance(prior, r.source) <= 8 && safe(d, prior)) return prior;
    return [0, -1, 1, -2, 2].map(dx => fallback(r, dx)).find(q => safe(d, q)) ?? null;
  }
  function matchesTicket(r, t) { return !!r?.room && r.room.cell === t.cell && same(r.source, t.door); }
  function returnFrom(p, current) {
    if (!current.available || !usable(p)) return false;
    const inside = occupied(p, current);
    if (!inside) return false;
    let t = inside.ticket;
    const r = t ? getState(t.id) : inside.record;
    if (!t) {
      t = { schema: 1, family: "arboretum", id: r.id, cell: r.room.cell, source: fallback(r), door: copy(r.source), phase: "inside" };
      if (!write(p, ARBORETUM_RETURN_KEY, t)) return false;
    }
    const d = dim(t.source.dimension), candidates = [t.source];
    if (matchesTicket(r, t)) candidates.push(...[0, -1, 1, -2, 2].map(dx => fallback(r, dx)));
    const target = candidates.find(q => q.dimension === t.source.dimension && distance(q, t.source) < 9 && safe(d, q));
    if (!target) {
      if (!returnQueue.has(p.id)) returnQueue.set(p.id, { source: copy(t.source), requested: now() });
      notice(p, "Your exact way home is blocked or still loading. It remains remembered; try the return arch again.");
      return false;
    }
    t.phase = "returning";
    if (!write(p, ARBORETUM_RETURN_KEY, t)) return false;
    try { p.tryTeleport({ x: target.x, y: target.y, z: target.z }, { dimension: d, checkForBlocks: true,
      facingLocation: add(target, { x: 0, y: 1, z: -4 }), keepVelocity: false }); } catch { }
    if (usable(p) && p.dimension.id === d.id && distance(p.location, target) < 0.8) {
      write(p, ARBORETUM_RETURN_KEY, undefined); returnQueue.delete(p.id);
      cooldown.set(p.id, now() + 60); disarmed.add(p.id); dwell.delete(p.id);
      return true;
    }
    t.phase = "inside"; write(p, ARBORETUM_RETURN_KEY, t); return false;
  }
  function requestReturn(p) { try { return returnFrom(p, readTicket(p)); } catch { return false; } }
  function attemptEntry(p, r, current) {
    if (!current.available || !usable(p) || occupied(p, current) || current.ticket && current.ticket.phase !== "outside") return false;
    try { if (canEnter(p) !== true || !sourceIsReady(r)) return false; } catch { return false; }
    ensureRoom(r);
    r = getState(r.id);
    if (!r?.unlocked || r.room?.phase !== "ready" || !verified.has(verifiedKey(r)) || !roomVerified(r) || opening.has(r.id)) return "pending";
    if (!shellIntact(r.room.origin)) { verified.delete(verifiedKey(r)); return "pending"; }
    if (p.dimension.id !== r.source.dimension || !openingAt(p.location, r.source)) return false;
    const source = approachSource(p, r);
    if (!source) { notice(p, "The approach is obstructed; a safe return must be ready before you enter."); return false; }
    if (!r.room.visited) { r.room.visited = true; if (!save(r)) return false; }
    const t = { schema: 1, family: "arboretum", id: r.id, cell: r.room.cell, source: copy(source), door: copy(r.source), phase: "entering" };
    if (!write(p, ARBORETUM_RETURN_KEY, t)) return false;
    const target = add(r.room.origin, ARBORETUM.arrival);
    try { p.tryTeleport(target, { dimension: dim(), checkForBlocks: true, facingLocation: add(r.room.origin, { x: 17.5, y: 4, z: 19.5 }), keepVelocity: false }); } catch { }
    if (occupiedTicket(p, t)) { t.phase = "inside"; write(p, ARBORETUM_RETURN_KEY, t); return true; }
    // Keep committed source information after a failed/ambiguous move.
    t.phase = "outside"; write(p, ARBORETUM_RETURN_KEY, t); return false;
  }
  function tickReturnLease(active) {
    for (const [id, q] of returnQueue) if (!active.has(id) || now() - q.requested > 200) returnQueue.delete(id);
    if (returnLease && (now() >= returnLease.until || !returnQueue.has(returnLease.owner))) {
      removeLease(RETURN_LEASE, returnLease);
      const q = returnQueue.get(returnLease.owner);
      if (q) { returnQueue.delete(returnLease.owner); returnQueue.set(returnLease.owner, q); }
      returnLease = null;
    }
    if (!returnLease && returnQueue.size) {
      const [id, q] = returnQueue.entries().next().value;
      const held = lease(RETURN_LEASE, q.source.dimension, add(q.source, { x: -8, y: -2, z: -8 }), { x: 17, y: 6, z: 17 });
      if (held) returnLease = { ...held, owner: id, until: now() + 40 };
    }
  }
  function tick() {
    try { tickBuild(); } catch { if (job) failJob("Arboretum build inspection failed; progress preserved."); }
    for (const [id, animation] of opening) {
      const r = getState(id), progress = Math.min(1, (now() - animation.start) / 40);
      if (!r?.unlocked || !same(r.source, animation.source)) { opening.delete(id); continue; }
      try { animation.face.teleport(add(animation.source, { x: 0, y: 5 * progress, z: 0 })); } catch { }
      if (progress === 1) opening.delete(id);
    }
    const ps = playersRead() ?? [], active = new Set(), currentRecords = sources();
    for (const p of ps) {
      try {
        if (!usable(p)) continue;
        active.add(p.id);
        const current = readTicket(p);
        if (!current.available) continue;
        const inside = occupied(p, current), t = current.ticket;
        if (!seen.has(p.id)) { seen.add(p.id); disarmed.add(p.id); }
        if (t && !inside && t.phase !== "outside") { t.phase = "outside"; if (!write(p, ARBORETUM_RETURN_KEY, t)) continue; }
        if (inside && t && t.phase === "outside") { t.phase = "inside"; if (!write(p, ARBORETUM_RETURN_KEY, t)) continue; }
        const nearby = inside ? [] : currentRecords.filter(r => p.dimension.id === r.source.dimension && distance(p.location, r.source) < 8);
        const touchingSources = nearby.filter(r => openingAt(p.location, r.source));
        const r = touchingSources.length === 1 ? touchingSources[0] : null;
        const anchor = inside ? add(arboretumOrigin(inside.cell), ARBORETUM.exit) : r?.source;
        const touching = !!anchor && openingAt(p.location, anchor);
        if (!touching) {
          dwell.delete(p.id); disarmed.delete(p.id); returnQueue.delete(p.id);
          for (const source of nearby) if (safe(dim(source.source.dimension), p.location)) approaches.set(`${p.id}/${source.id}`, { ...p.location, dimension: p.dimension.id });
          continue;
        }
        if (!inside && !r.unlocked || disarmed.has(p.id) || now() < (cooldown.get(p.id) ?? 0)) continue;
        const portal = inside ? `return/${inside.cell}` : r.id;
        if (dwell.get(p.id)?.portal !== portal) dwell.set(p.id, { portal, start: now() });
        if (now() - dwell.get(p.id).start < 20) continue;
        const result = inside ? returnFrom(p, current) : attemptEntry(p, r, current);
        if (result === "pending") { dwell.set(p.id, { portal, start: now() }); continue; }
        dwell.delete(p.id); cooldown.set(p.id, now() + 60); disarmed.add(p.id);
      } catch { log("Arboretum visitor reconciliation deferred; saved history preserved."); }
    }
    for (const r of currentRecords) {
      if (r.unlocked && now() % 20 === 0) {
        const points = [];
        if (ps.some(p => usable(p) && p.dimension.id === r.source.dimension && distance(p.location, r.source) <= 24)) points.push(r.source);
        if (r.room?.phase === "ready" && ps.some(p => usable(p) && p.dimension.id === "minecraft:overworld" && inArboretum(p.location, r.room.cell))) points.push({ ...add(r.room.origin, ARBORETUM.exit), dimension: "minecraft:overworld" });
        for (const at of points) for (const x of [-0.8, 0, 0.8]) {
          try { dim(at.dimension).spawnParticle("minecraft:soul_particle", add(at, { x, y: 1.3, z: 0 })); } catch { }
        }
      }
      if (r.room?.phase !== "ready" || r.reward.claimed) continue;
      try {
        const c = inventory(r);
        if (c && !c.getItem(0)) { r.reward.claimed = true; save(r); }
      } catch { }
    }
    for (const id of seen) if (!active.has(id)) {
      seen.delete(id); dwell.delete(id); cooldown.delete(id); disarmed.delete(id); returnQueue.delete(id);
      for (const key of approaches.keys()) if (key.startsWith(`${id}/`)) approaches.delete(key);
      for (const key of notices.keys()) if (key.startsWith(`${id}/`)) notices.delete(key);
    }
    tickReturnLease(active);
    if (roomLease && !job && now() - roomLease.used > 80) { removeLease(ROOM_LEASE, roomLease); roomLease = null; }
  }
  return { beginPlacement, recordPlaced, confirmPlacement, getPlacement, isRecordedRegion, sources, sourceAt,
    isCanonicalFace, bindFace, reconcileFace, interact, completeUse, tick, requestReturn, occupiedRealm,
    protectsBlock, excludesWorldPosition, isReturnBlock, allowsOtherEntry, getState };
}

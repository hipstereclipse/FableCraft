// Owned runtime: Guild Demon Door pilot. Bedrock effects are injected so tests
// execute this module itself without importing a fake @minecraft/server package.
export const ARCANUM = Object.freeze({
  id: "fc:library_arcanum", version: 1, size: { x: 49, y: 28, z: 49 },
  arrival: { x: 24.5, y: 3, z: 7.5 }, exit: { x: 24.5, y: 3, z: 3.5 },
  rewards: [
    { at: { x: 24, y: 3, z: 35 }, item: "fc:elixir_of_life" },
    { at: { x: 16, y: 3, z: 28 }, item: "minecraft:book", name: "Making Friends" },
    { at: { x: 32, y: 3, z: 28 }, item: "minecraft:book", name: "Book of Spells" },
    { at: { x: 16, y: 3, z: 34 }, item: "minecraft:paper", name: "Howl Tattoo" },
  ],
});
export const DOOR_STATE_KEY = "fc_dp_guild_v1";
export const DOOR_RETURN_KEY = "fc_dp_return_v1";
const ROOM_LEASE = "fc_dp_guild_load", SOURCE_LEASE = "fc_dp_guild_return";
const add = (a, b) => ({ x: a.x + b.x, y: a.y + b.y, z: a.z + b.z });
const finitePosition = (p) => p && [p.x, p.y, p.z].every(Number.isFinite);
const distance = (a, b) => Math.hypot(a.x - b.x, a.y - b.y, a.z - b.z);
const parse = (value) => { try { return JSON.parse(value); } catch { return null; } };
const supportedDimensions = new Set(["minecraft:overworld", "minecraft:nether", "minecraft:the_end"]);
const validSource = (p) => finitePosition(p) && Math.abs(p.x) < 30000000 && Math.abs(p.z) < 30000000
  && p.y >= -63 && p.y <= 317 && supportedDimensions.has(p.dimension);
const shellPoints = [];
for (let x = 0; x < 49; x++) for (let y = 0; y < 28; y++) for (let z = 0; z < 49; z++) {
  if (x === 0 || x === 48 || y === 0 || y === 27 || z === 0 || z === 48) shellPoints.push({ x, y, z });
}
const shellSentinels = shellPoints.filter(({ x, y, z }) => [0, 24, 48].includes(x)
  && [0, 14, 27].includes(y) && [0, 24, 48].includes(z));
export const realmOrigin = (cell) => ({ x: 600000 + (cell % 64) * 128, y: 272, z: 600000 + Math.floor(cell / 64) * 128 });
export function inRealm(position, origin, margin = 0) {
  return finitePosition(position) && finitePosition(origin)
    && position.x >= origin.x - margin && position.x < origin.x + ARCANUM.size.x + margin
    && position.y >= origin.y - margin && position.y < origin.y + ARCANUM.size.y + margin
    && position.z >= origin.z - margin && position.z < origin.z + ARCANUM.size.z + margin;
}
export function inDoorOpening(position, anchor) {
  return finitePosition(position) && finitePosition(anchor)
    && Math.abs(position.x - anchor.x) <= 1.35 && Math.abs(position.z - anchor.z) <= 0.9
    && position.y >= anchor.y - 0.15 && position.y <= anchor.y + 2.4;
}

export function createDemonDoorPilot({ world, system, ItemStack, report = () => {}, definition = null, placeRoom = null, sourceReady = () => true }) {
  if (definition && (definition.id !== "guild_library_arcanum" || definition.destination?.structure !== ARCANUM.id)) {
    throw new Error("Guild Demon Door definition does not match its generated destination contract.");
  }
  let job = null, opening = null, roomLease = false, sourceLease = false, leaseLastUsed = -1000, buildRetryAt = 0;
  let verifiedReadyCell = null;
  const dwell = new Map(), cooldown = new Map(), disarmed = new Set(), seen = new Set();
  const notices = new Map(), approach = new Map(), returnWait = new Map();
  const leaseDimensions = new Map();
  const now = () => system.currentTick;
  const dimension = (id = "minecraft:overworld") => world.getDimension(id);
  const blockAt = (dim, p) => { try { return dim.getBlock(p) ?? null; } catch { return null; } };
  const air = (b) => !!b && (b.isAir === true || b.typeId === "minecraft:air");
  const floorIds = new Set(["stone", "stone_bricks", "chiseled_stone_bricks", "mossy_stone_bricks", "cracked_stone_bricks", "cobblestone", "mossy_cobblestone", "grass_block", "dirt", "coarse_dirt", "dirt_with_roots", "grass_path", "dirt_path", "gravel", "andesite", "polished_andesite", "deepslate", "polished_deepslate", "bedrock", "oak_planks", "dark_oak_planks", "spruce_planks"].map((id) => `minecraft:${id}`));
  function read() {
    let r;
    try { r = parse(world.getDynamicProperty(DOOR_STATE_KEY)); } catch { return null; }
    if (!r || r.schema !== 1 || r.id !== "guild" || r.archetype !== "guild_library_arcanum"
      || !validSource(r.source) || typeof r.unlocked !== "boolean"
      || !r.rewards || typeof r.rewards.seeded !== "boolean" || typeof r.rewards.suppressed !== "boolean"
      || !Array.isArray(r.rewards.claimed) || r.rewards.claimed.length !== 4
      || !r.rewards.claimed.every((claimed) => typeof claimed === "boolean")) return null;
    if (r.room && (!Number.isInteger(r.room.cell) || r.room.cell < 0 || r.room.cell >= 4096
      || !finitePosition(r.room.origin) || distance(r.room.origin, realmOrigin(r.room.cell)) > 0.01
      || !["allocated", "placing", "ready"].includes(r.room.phase) || typeof r.room.visited !== "boolean"
      || r.room.version !== ARCANUM.version || (r.room.phase === "ready" && !r.rewards.seeded))) return null;
    return r;
  }
  function save(r) { world.setDynamicProperty(DOOR_STATE_KEY, JSON.stringify(r)); }
  function getSource(candidate = null) {
    try {
      // Once present, the progress ledger is the sole placement authority.
      // Corrupt/unavailable history must not fall back to a new source.
      if (world.getDynamicProperty(DOOR_STATE_KEY) !== undefined) return read()?.source ?? null;
      const hint = candidate ?? parse(world.getDynamicProperty("fc_guild_door"));
      const source = { ...hint, dimension: hint?.dimension ?? "minecraft:overworld" };
      return validSource(source) ? source : null;
    } catch { return null; }
  }
  function rawTicket(p) {
    const t = parse(p.getDynamicProperty(DOOR_RETURN_KEY));
    return t?.schema === 1 && t.doorId === "guild" && validSource(t.source)
      && Number.isInteger(t.cell) && t.cell >= 0 && t.cell < 4096
      && ["entering", "inside", "outside", "returning"].includes(t.phase) ? t : null;
  }
  function ticket(p) {
    const t = rawTicket(p), r = read();
    return t && t.cell === r?.room?.cell && t.source.dimension === r.source.dimension
      && distance(t.source, r.source) < 16 ? t : null;
  }
  function occupiedTicket(p) {
    const t = rawTicket(p);
    // This committed ticket remains a return authority when a missing world
    // ledger is later recreated for another/no room. Actual occupancy of its
    // exact bounded Overworld cell is required; a stale outside ticket cannot
    // teleport its owner or select someone else's destination.
    return t && p.dimension.id === dimension().id && inRealm(p.location, realmOrigin(t.cell)) ? t : null;
  }
  function saveTicket(p, t) { p.setDynamicProperty(DOOR_RETURN_KEY, t ? JSON.stringify(t) : undefined); }
  function notice(p, text) {
    const key = `${p.id}|${text}`;
    if (now() - (notices.get(key) ?? -1000) < 100) return;
    notices.set(key, now());
    try { p.sendMessage(`§5Demon Door: §7${text}`); } catch { }
  }
  function safe(dim, p) {
    if (!finitePosition(p)) return false;
    for (const dx of [-0.3, 0.3]) for (const dz of [-0.3, 0.3]) {
      const x = Math.floor(p.x + dx), z = Math.floor(p.z + dz), y = Math.floor(p.y);
      if (!floorIds.has(blockAt(dim, { x, y: y - 1, z })?.typeId)) return false;
      // A recorded approach can have fractional feet while jumping. Check
      // every cell intersected by the standing player, including a third cell
      // above those feet, so a blocked exact point can select a safe fallback.
      for (let headY = y; headY < Math.ceil(p.y + 1.8); headY++) if (!air(blockAt(dim, { x, y: headY, z }))) return false;
    }
    return true;
  }
  function lease(dim, name, origin, size) {
    try {
      // Remove only our own possibly orphaned lease before recreating it.
      try { dim.runCommand(`tickingarea remove ${name}`); } catch { }
      const end = add(origin, { x: size.x - 1, y: size.y - 1, z: size.z - 1 });
      const result = dim.runCommand(`tickingarea add ${Math.floor(origin.x)} ${Math.floor(origin.y)} ${Math.floor(origin.z)} ${Math.floor(end.x)} ${Math.floor(end.y)} ${Math.floor(end.z)} ${name} true`);
      if (result?.successCount === 0) return false;
      leaseDimensions.set(name, dim.id);
      return true;
    } catch (e) { report(`Demon Door loading unavailable: ${String(e)}`); return false; }
  }
  function removeLease(name) {
    try { dimension(leaseDimensions.get(name)).runCommand(`tickingarea remove ${name}`); } catch { }
    leaseDimensions.delete(name);
    if (name === ROOM_LEASE) roomLease = false;
    else sourceLease = false;
  }
  function registerGuild(source, face = null, { isNew = false } = {}) {
    if (world.getDynamicProperty(DOOR_STATE_KEY) !== undefined) {
      const existing = read();
      if (!existing) report("Demon Door record is invalid; refusing to reset saved progress.");
      return existing;
    }
    if (!finitePosition(source)) return null;
    source = { ...source, dimension: source.dimension ?? "minecraft:overworld" };
    if (!validSource(source)) return null;
    let legacyOpen = false, idx = null;
    if (face) {
      try {
        legacyOpen = face.getDynamicProperty("fc_door_open") === true;
        idx = face.getDynamicProperty("fc_door_idx") ?? null;
      } catch {
        report("Guild door legacy history is temporarily unreadable; registration deferred.");
        return null;
      }
    }
    const status = isNew ? "new" : face ? (legacyOpen ? "surviving_open" : "surviving_closed") : "history_unknown";
    const r = { schema: 1, id: "guild", archetype: "guild_library_arcanum",
      source: { ...source, dimension: source.dimension ?? "minecraft:overworld" }, unlocked: legacyOpen,
      legacy: { status, idx, priorReplacementHistory: isNew ? "none" : "unrecoverable" }, room: null,
      rewards: { suppressed: legacyOpen || status === "history_unknown", seeded: false, claimed: [false, false, false, false] } };
    save(r);
    if (status === "history_unknown") report("Guild door legacy payment history is missing; new room rewards conservatively suppressed.");
    return r;
  }
  function matchesFace(face) {
    const r = read();
    try { return !!r && face.typeId === "fc:demon_door" && face.dimension.id === r.source.dimension
      && Math.hypot(face.location.x - r.source.x, face.location.z - r.source.z) < 3
      && Math.abs(face.location.y - r.source.y) < 7; } catch { return false; }
  }
  function reconcileFace(face) {
    const r = read();
    if (!r || !matchesFace(face)) return false;
    try {
      face.setDynamicProperty("fc_door_identity", "guild");
      if (r.unlocked && !opening) {
        face.setDynamicProperty("fc_door_open", true);
        face.triggerEvent("fc:open");
        face.teleport(add(r.source, { x: 0, y: 5, z: 0 }));
      }
    } catch { }
    return true;
  }
  function interact(p, face, heldItemId) {
    if (!matchesFace(face)) return false;
    const r = read();
    if (p.dimension.id !== r.source.dimension || distance(p.location, r.source) > 7) return true;
    if (r.unlocked) { notice(p, "The Library Arcanum awaits. Step into the light."); return true; }
    if (heldItemId !== (definition?.requirement?.item ?? "minecraft:lantern")) {
      notice(p, definition?.requirement?.hint ?? "Bring light to this dark path. Hold a lantern and use it on my face.");
      return true;
    }
    if (!sourceIsReady(r)) { notice(p, "My passage is obstructed. Clear the doorway before bringing your light."); return true; }
    // This synchronous reread/commit precedes all animation and delayed work.
    // The Guild challenge consumes nothing and grants no opening-time rewards.
    const fresh = read();
    if (!fresh || fresh.unlocked) return true;
    fresh.unlocked = true;
    save(fresh);
    opening = { face, start: now(), source: { ...fresh.source } };
    try { face.setDynamicProperty("fc_door_open", true); face.triggerEvent("fc:open"); p.playSound("fc.door_rumble"); } catch { }
    notice(p, definition?.success ?? "Light at last. Enter the Library Arcanum.");
    ensureRoom(fresh);
    return true;
  }
  function container(dim, at) {
    try { return blockAt(dim, at)?.getComponent("minecraft:inventory")?.container ?? null; } catch { return null; }
  }
  function roomVerified(r) {
    if (!r.room) return false;
    const dim = dimension(), o = r.room.origin;
    if (!safe(dim, add(o, ARCANUM.arrival)) || !safe(dim, add(o, ARCANUM.exit))) return false;
    // A continuous approach to the main chest, independent of endpoint checks.
    for (let z = 4; z <= 34; z++) if (!safe(dim, add(o, { x: 24.5, y: 3, z: z + 0.5 }))) return false;
    // Branch lanes connect the main walk to every minor collectible approach.
    for (const z of [26.5, 32.5]) for (let x = 16; x <= 32; x++) {
      if (!safe(dim, add(o, { x: x + 0.5, y: 3, z }))) return false;
    }
    if (!shellSentinels.every((point) => blockAt(dim, add(o, point))?.typeId === "minecraft:barrier")) return false;
    return ARCANUM.rewards.every((reward) => container(dim, add(o, reward.at)) !== null
      && air(blockAt(dim, add(o, add(reward.at, { x: 0, y: 1, z: 0 }))))
      && safe(dim, add(o, add(reward.at, { x: 0.5, y: 0, z: -0.5 }))));
  }
  function ensureRoom(r = read()) {
    if (!r?.unlocked || job || now() < buildRetryAt) return;
    if (r.room?.phase === "ready" && verifiedReadyCell === r.room.cell && roomVerified(r)) { leaseLastUsed = now(); return; }
    if (!r.room) {
      r.room = { cell: 0, origin: realmOrigin(0), version: ARCANUM.version, phase: "allocated", visited: false };
      save(r);
    }
    if (!roomLease) roomLease = lease(dimension(), ROOM_LEASE, r.room.origin, ARCANUM.size);
    if (!roomLease) { buildRetryAt = now() + 200; return; }
    leaseLastUsed = now();
    job = { phase: "loading", started: now(), scan: 0, verifyScan: 0, skips: 0, readyOnly: r.room.phase === "ready" || r.room.visited === true };
  }
  function failJob(message) {
    report(message);
    verifiedReadyCell = null;
    buildRetryAt = now() + 200;
    job = null;
    removeLease(ROOM_LEASE);
  }
  function tickBuild() {
    if (!job) return;
    const r = read();
    if (!r?.room) { failJob("Demon Door room state disappeared."); return; }
    const o = r.room.origin, dim = dimension();
    if (now() - job.started > 1200) { failJob("Demon Door room loading timed out; entrance remains at source."); return; }
    leaseLastUsed = now();
    if (job.phase === "loading") {
      for (const x of [0, 48]) for (const z of [0, 48]) if (!blockAt(dim, add(o, { x, y: 2, z }))) return;
      if (job.readyOnly) {
        if (!roomVerified(r)) { failJob("Visited Demon Door room is damaged; refusing to rebuild or replenish rewards."); return; }
        job.phase = "verify";
      } else {
        job.phase = r.room.phase === "allocated" ? "preflight" : "place";
      }
    }
    if (job.phase === "preflight") {
      const total = ARCANUM.size.x * ARCANUM.size.y * ARCANUM.size.z;
      for (let n = 0; n < 512 && job.scan < total; n++, job.scan++) {
        const i = job.scan;
        const at = add(o, { x: i % 49, y: Math.floor(i / 49) % 28, z: Math.floor(i / (49 * 28)) });
        const b = blockAt(dim, at);
        if (!b) return;
        if (!air(b)) {
          if (++job.skips >= 8 || r.room.cell >= 4095) { failJob("Demon Door allocation found occupied cells; no blocks changed."); return; }
          r.room.cell++;
          r.room.origin = realmOrigin(r.room.cell);
          save(r);
          removeLease(ROOM_LEASE);
          roomLease = lease(dim, ROOM_LEASE, r.room.origin, ARCANUM.size);
          if (!roomLease) { job = null; return; }
          job.scan = 0; job.phase = "loading"; job.started = now();
          return;
        }
      }
      if (job.scan < total) return;
      job.phase = "place";
    }
    if (job.phase === "place") {
      // No player can be present when first placement/retry may replace blocks.
      if (world.getPlayers().some((p) => p.dimension.id === dim.id && inRealm(p.location, o))) return;
      try {
        if (dim.getEntities({ location: add(o, { x: 24, y: 14, z: 24 }), maxDistance: 45 }).length) {
          failJob("Demon Door destination contains entities; placement deferred."); return;
        }
        r.room.phase = "placing";
        save(r);
        if (placeRoom) placeRoom(dim, o);
        else world.structureManager.place(ARCANUM.id, dim, o, { includeEntities: false });
        job.phase = "verify";
      } catch (e) { failJob(`Demon Door structure unavailable: ${String(e)}`); }
      return;
    }
    if (job.phase === "verify") {
      // Verify all 9,794 containment cells before first admission and once after
      // reload/unloaded-room recovery, spread across ticks. Ordinary repeated
      // visits use route/lid checks and sentinel probes instead of rescanning.
      for (let n = 0; n < 512 && job.verifyScan < shellPoints.length; n++, job.verifyScan++) {
        const b = blockAt(dim, add(o, shellPoints[job.verifyScan]));
        if (!b) return;
        if (b.typeId !== "minecraft:barrier") { failJob("Demon Door containment is incomplete; admission refused."); return; }
      }
      if (job.verifyScan < shellPoints.length) return;
      if (!roomVerified(r)) return;
      if (job.readyOnly) { verifiedReadyCell = r.room.cell; job = null; return; }
      try {
        for (const reward of ARCANUM.rewards) {
          const c = container(dim, add(o, reward.at));
          if (!r.rewards.suppressed) {
            const item = new ItemStack(reward.item, 1);
            if (reward.name) {
              item.nameTag = reward.name;
              item.setLore(["A keepsake from the Library Arcanum."]);
            }
            c.setItem(0, item);
          }
        }
        r.rewards.seeded = true;
        r.rewards.claimed = ARCANUM.rewards.map(() => r.rewards.suppressed);
        r.room.phase = "ready";
        save(r);
        verifiedReadyCell = r.room.cell;
        job = null;
      } catch (e) { failJob(`Demon Door reward preparation failed: ${String(e)}`); }
    }
  }
  function sourceReturn(r, p) {
    const prior = approach.get(p.id);
    const dim = dimension(r.source.dimension);
    const position = prior && prior.dimension === r.source.dimension && distance(prior, r.source) <= 8 && safe(dim, prior)
      ? prior : add(r.source, { x: 0.5, y: 0, z: -3.5 });
    return { x: position.x, y: position.y, z: position.z, dimension: r.source.dimension };
  }
  function sourceIsReady(r) { try { return sourceReady(r.source) === true; } catch { return false; } }
  function attemptEntry(p, r) {
    if (!sourceIsReady(r)) { notice(p, "My passage is obstructed. Clear the doorway before entering."); return false; }
    ensureRoom(r);
    r = read();
    if (opening || job || r?.room?.phase !== "ready" || verifiedReadyCell !== r.room.cell || !roomVerified(r)) {
      notice(p, "The passage is taking shape. Wait in the light to cross."); return "pending";
    }
    if (ticket(p)?.phase === "inside") return false;
    const source = sourceReturn(r, p);
    if (!safe(dimension(source.dimension), source)) { notice(p, "Clear the path outside my doorway before entering."); return false; }
    const t = { schema: 1, doorId: r.id, cell: r.room.cell, source, phase: "entering" };
    r.room.visited = true; // Even a failed/ambiguous move can never authorize reseeding.
    save(r);
    saveTicket(p, t);
    const arrival = add(r.room.origin, ARCANUM.arrival);
    let moved = false;
    try { moved = p.tryTeleport(arrival, { dimension: dimension(), checkForBlocks: true, facingLocation: add(arrival, { x: 0, y: 1, z: 8 }), keepVelocity: false }); } catch { }
    const inside = p.dimension.id === dimension().id && inRealm(p.location, r.room.origin);
    if (moved || inside) {
      t.phase = "inside"; saveTicket(p, t); cooldown.set(p.id, now() + 60); disarmed.add(p.id); leaseLastUsed = now();
      notice(p, "The Library Arcanum. Explore the grove; the light behind you leads home.");
      return true;
    }
    saveTicket(p, null);
    notice(p, "The crossing faltered. You are still safely at the Guild.");
    return false;
  }
  function requestReturn(p) {
    let r = read();
    let t = ticket(p);
    const remembered = occupiedTicket(p);
    if (remembered && (!r?.room || r.room.cell !== remembered.cell || !t)) {
      // A newer valid ledger must not revoke a committed way home. Recovery
      // uses only this ticket's exact source; it never reconstructs a room,
      // resets unlocks/claims, or borrows alternatives from the newer ledger.
      r = null;
      t = remembered;
    }
    if (!r) {
      // A previously committed player ticket remains a return authority if the
      // primary world record becomes unreadable. Require the exact bounded cell
      // and its actual Overworld position; never guess a source or rebuild data.
      t = remembered;
      if (!t) return false;
    } else if (!r.room || p.dimension.id !== dimension().id || !inRealm(p.location, r.room.origin)) return false;
    if (r && (!t || t.cell !== r.room.cell)) {
      t = { schema: 1, doorId: r.id, cell: r.room.cell, source: { ...add(r.source, { x: 0.5, y: 0, z: -3.5 }), dimension: r.source.dimension }, phase: "inside" };
      saveTicket(p, t);
    }
    if (!returnWait.has(p.id)) returnWait.set(p.id, now());
    const dim = dimension(t.source.dimension);
    const candidates = [t.source, ...(r ? [0, -1, 1, -2, 2].map((dx) => ({ ...add(r.source, { x: dx + 0.5, y: 0, z: -3.5 }), dimension: r.source.dimension })) : [])];
    // Alternatives are valid only for this ticket's original door source.
    const target = candidates.find((c) => c.dimension === t.source.dimension && distance(c, t.source) < 9 && safe(dim, c));
    if (!target) {
      if (!sourceLease) sourceLease = lease(dim, SOURCE_LEASE, add(t.source, { x: -8, y: -2, z: -8 }), { x: 17, y: 6, z: 17 });
      notice(p, "The way home is blocked or still loading. Clear the Guild approach and try this light again.");
      return false;
    }
    t.phase = "returning"; saveTicket(p, t);
    let moved = false;
    try { moved = p.tryTeleport({ x: target.x, y: target.y, z: target.z }, { dimension: dim, checkForBlocks: true, facingLocation: add(target, { x: 0, y: 1, z: -4 }), keepVelocity: false }); } catch { }
    if (moved || (p.dimension.id === dim.id && distance(p.location, target) < 1)) {
      saveTicket(p, null); returnWait.delete(p.id); cooldown.set(p.id, now() + 60); disarmed.add(p.id);
      if (sourceLease && returnWait.size === 0) removeLease(SOURCE_LEASE);
      return true;
    }
    t.phase = "inside"; saveTicket(p, t);
    notice(p, "The crossing faltered. Your way home is remembered; try the light again.");
    return false;
  }
  function occupiedRealm(p) {
    const r = read();
    return !!occupiedTicket(p) || (!!r?.room && p.dimension.id === dimension().id && inRealm(p.location, r.room.origin));
  }
  function protectsBlock(dimId, position) {
    const r = read();
    return !!r?.room && dimId === dimension().id && inRealm(position, r.room.origin);
  }
  function excludesWorldPosition(dimId, position) {
    const r = read();
    return !!r?.room && dimId === dimension().id && finitePosition(position)
      && inRealm({ ...position, y: r.room.origin.y }, r.room.origin, 160);
  }
  function tick() {
    tickBuild();
    const r = read();
    // Ticketed visitors still own an exit while the primary ledger is absent
    // or unreadable. No source admission, room work or reward work is permitted.
    if (!r && roomLease && !job) removeLease(ROOM_LEASE);
    if (opening) {
      const progress = Math.min(1, (now() - opening.start) / 40);
      try { opening.face.teleport(add(opening.source, { x: 0, y: progress * 5, z: 0 })); } catch { }
      if (progress === 1) opening = null;
    }
    const active = new Set();
    for (const p of world.getPlayers()) {
      active.add(p.id);
      try {
        const remembered = occupiedTicket(p), t = remembered ?? ticket(p);
        if (!r && !remembered) continue;
        const roomOrigin = remembered ? realmOrigin(remembered.cell) : r.room?.origin;
        const inside = !!roomOrigin && p.dimension.id === dimension().id && inRealm(p.location, roomOrigin);
        if (!seen.has(p.id)) { seen.add(p.id); disarmed.add(p.id); }
        if (t && !inside && t.phase !== "outside") { t.phase = "outside"; saveTicket(p, t); }
        if (inside) {
          leaseLastUsed = now();
          if (!t) {
            saveTicket(p, { schema: 1, doorId: r.id, cell: r.room.cell,
              source: { ...add(r.source, { x: 0.5, y: 0, z: -3.5 }), dimension: r.source.dimension }, phase: "inside" });
          } else if (t.phase === "outside") {
            t.phase = "inside";
            saveTicket(p, t);
          }
        }
        const nearSource = !!r && p.dimension.id === r.source.dimension && distance(p.location, r.source) < 8;
        const anchor = inside ? add(roomOrigin, ARCANUM.exit) : r.source;
        const touching = (inside || nearSource) && inDoorOpening(p.location, anchor);
        if (!touching) {
          dwell.delete(p.id); disarmed.delete(p.id); returnWait.delete(p.id);
          if (nearSource && safe(dimension(r.source.dimension), p.location)) approach.set(p.id, { ...p.location, dimension: p.dimension.id });
          continue;
        }
        if (!inside && !r.unlocked) continue;
        if (disarmed.has(p.id) || now() < (cooldown.get(p.id) ?? 0)) continue;
        if (!dwell.has(p.id)) dwell.set(p.id, now());
        if (now() - dwell.get(p.id) < 20) continue;
        const result = inside ? requestReturn(p) : attemptEntry(p, r);
        if (result === "pending") { dwell.set(p.id, now()); continue; }
        dwell.delete(p.id); cooldown.set(p.id, now() + 60); disarmed.add(p.id);
      } catch (e) { report(`Demon Door player reconciliation: ${String(e)}`); }
    }
    if (r?.room?.phase === "ready") {
      let changed = false;
      ARCANUM.rewards.forEach((reward, index) => {
        if (r.rewards.claimed[index]) return;
        const c = container(dimension(), add(r.room.origin, reward.at));
        // A missing/unloaded chest is not proof that a player collected it.
        try { if (c && !c.getItem(0)) { r.rewards.claimed[index] = true; changed = true; } } catch { }
      });
      if (changed) {
        const latest = read();
        latest.rewards.claimed = latest.rewards.claimed.map((claimed, index) => claimed || r.rewards.claimed[index]);
        save(latest);
      }
    }
    if (r?.unlocked && now() % 20 === 0) {
      for (const at of [r.source, ...(r.room?.phase === "ready" ? [add(r.room.origin, ARCANUM.exit)] : [])]) {
        for (const dx of [-0.9, 0, 0.9]) for (const y of [0.4, 1.5, 2.6]) {
          try { dimension(at.dimension).spawnParticle("minecraft:soul_particle", add(at, { x: dx, y, z: 0 })); } catch { }
        }
      }
    }
    for (const id of seen) if (!active.has(id)) {
      seen.delete(id); dwell.delete(id); cooldown.delete(id); disarmed.delete(id); approach.delete(id); returnWait.delete(id);
      for (const key of notices.keys()) if (key.startsWith(`${id}|`)) notices.delete(key);
    }
    if (roomLease && !job && now() - leaseLastUsed > 80) removeLease(ROOM_LEASE);
    for (const [id, started] of returnWait) if (now() - started > 200 || !active.has(id)) returnWait.delete(id);
    if (sourceLease && returnWait.size === 0) removeLease(SOURCE_LEASE);
  }
  return { registerGuild, matchesFace, reconcileFace, interact, tick, requestReturn, occupiedRealm, protectsBlock, excludesWorldPosition,
    getState: read, getSource, getReturnTicket: ticket };
}

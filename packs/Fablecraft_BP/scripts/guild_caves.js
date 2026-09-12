// GP5 owns the final cave cells, including the supported Library threshold.
// Keep the construction order: later treads/decks intentionally replace air.
export function guildCavePlan(base) {
  const cells = new Map();
  const setB = (x, y, z, name, states = {}) => cells.set(`${x},${y},${z}`, { x, y, z, name, states });
  const air = (x, y, z) => setB(x, y, z, "minecraft:air");
  let seed = 0x5cafe;
  const random = () => { seed = (Math.imul(seed, 1664525) + 1013904223) >>> 0; return seed / 4294967296; };
  const stone = () => random() < 0.22 ? "minecraft:mossy_stone_bricks" : "minecraft:stone_bricks";
  // ---- anchors (keep in lockstep with gen_structures.py guild_hall + chamber) ----
  const SX = base.x + 27, SZ = base.z + 14;   // 3x3 spiral centre (Library alcove)
  const TX = base.x + 26;                      // causeway centreline == Chamber centre x
  const CWALL = base.z + 29;                   // Chamber north wall (pierced here)
  const CFY = base.y - 21;                     // Chamber floor block (a Hero walks at CFY+1)
  const DECK = CFY;                            // FLAT deck == Chamber floor -> level walk-in
  const BSTART = base.z + 16;                  // deck springs from a solid abutment here
  const CSTART = base.z + 17, CEND = base.z + 28;  // the deck floats over the gulf here
  const HALF = 10;                             // gulf half-width carved to darkness each side
  const CEIL = DECK + 7;                       // sealed rock ceiling capping the gulf
  const FLOORB = Math.max(base.y - 36, -60);   // abyss floor — a long dark drop below the span
  // clockwise ring S,SW,W,NW,N,NE,E,SE starting at the Library-entry (south) side
  const ringCW = [[0, 1], [-1, 1], [-1, 0], [-1, -1], [0, -1], [1, -1], [1, 0], [1, 1]];
  const work = () => {
    // ===== 1. the SHAFT: a hollow 3x3 around a chiseled pillar, OPEN at the top
    //         and OPEN on its south face so you walk straight in off the Library
    //         alcove (that south wall was the bug the player had to dig through) =====
    for (let y = base.y + 2; y >= DECK - 1; y--) {
      for (let ox = -2; ox <= 2; ox++) for (let oz = -2; oz <= 2; oz++) {
        const cheb = Math.max(Math.abs(ox), Math.abs(oz));
        if (ox === 0 && oz === 0) setB(SX, y, SZ, "minecraft:chiseled_stone_bricks"); // pillar
        else if (cheb === 2) {
          if (oz === 2 && y > base.y) air(SX + ox, y, SZ + oz);   // open the entry doorway
          else setB(SX + ox, y, SZ + oz, stone());                 // shaft wall
        } else air(SX + ox, y, SZ + oz);                           // hollow interior
      }

    }
    // ===== 2. the DESCENT: a helix of HALF-BLOCK steps. Each tread drops the
    //         walking surface by exactly 0.5 block (even cells = bottom slabs,
    //         odd cells = full courses), so a Hero strolls DOWN and back UP it
    //         without ever jumping (the engine auto-steps 0.5). It takes twice
    //         the cells of a full-block stair, so the helix simply winds more
    //         turns to carry the same drop down to deck level (the causeway stays
    //         dead level). The treads float off the glowing central pillar — the
    //         cell beneath each is the headroom of the tread one turn below, so we
    //         leave it open (no posts) to keep the climb jump-free. =====
    air(SX, base.y, SZ + 1);                            // open the entry mouth
    const slab = () => (random() < 0.22 ? "minecraft:mossy_stone_brick_slab" : "minecraft:stone_brick_slab");
    for (let n = 0; ; n++) {
      const [dx, dz] = ringCW[n % 8];
      const tx = SX + dx, tz = SZ + dz;
      // surface = base.y + 0.5 - 0.5*n ; even n -> bottom slab (top at +.5), odd n -> full course
      const blockY = (n % 2 === 0) ? (base.y - n / 2) : (base.y - (n + 1) / 2);
      if (blockY < DECK || (blockY === DECK && n % 2 === 0)) break;   // end on the full course at deck level
      setB(tx, blockY, tz, (n % 2 === 0) ? slab() : stone());        // the tread
      air(tx, blockY + 1, tz); air(tx, blockY + 2, tz); air(tx, blockY + 3, tz);  // headroom
      if (n % 4 === 0) setB(SX, blockY + 1, SZ, "minecraft:glowstone");           // glowing newel

    }
    // a clean flat landing at the spiral foot (deck level) feeding south to the bridge
    for (let ox = -1; ox <= 1; ox++) for (let oz = -1; oz <= 1; oz++) {
      setB(SX + ox, DECK, SZ + oz, stone());            // landing floor
      setB(SX + ox, DECK - 1, SZ + oz, stone());        // solid beneath
    }
    // ===== 3. the CAUSEWAY: a long, dead-level span over a wide, deep, dark gulf.
    //         Deck is 5 wide (inner 3 walkable, outer 2 carry the rails); the gulf
    //         is carved to darkness on BOTH sides for the entire crossing. =====
    for (let z = BSTART; z < CWALL; z++) {
      if (z >= CSTART && z <= CEND) {                   // open the gulf under + beside the span
        for (let ox = -HALF; ox <= HALF; ox++) {
          setB(TX + ox, CEIL, z, stone());              // sealed rock ceiling over the void
          for (let yy = CEIL - 1; yy > FLOORB; yy--) air(TX + ox, yy, z);
        }
        for (let yy = FLOORB; yy <= CEIL; yy++) {       // sealed gulf side-walls (no bleed-in)
          setB(TX - HALF - 1, yy, z, stone());
          setB(TX + HALF + 1, yy, z, stone());
        }
      } else {                                          // solid abutment north of the gulf
        for (let ox = -HALF - 1; ox <= HALF + 1; ox++) {
          if (Math.abs(ox) <= 2) continue;              // leave the bridge portal open
          for (let yy = FLOORB; yy <= CEIL; yy++) setB(TX + ox, yy, z, stone());
        }
        for (let ox = -2; ox <= 2; ox++) for (let yy = DECK - 3; yy < DECK; yy++) setB(TX + ox, yy, z, stone());
      }
      // the level deck + low rails — identical at every z, so the walk never slopes
      for (let ox = -2; ox <= 2; ox++) setB(TX + ox, DECK, z, stone());
      for (let ox = -1; ox <= 1; ox++) { air(TX + ox, DECK + 1, z); air(TX + ox, DECK + 2, z); air(TX + ox, DECK + 3, z); }
      setB(TX - 2, DECK + 1, z, "minecraft:cobblestone_wall");   // rail the whole length
      setB(TX + 2, DECK + 1, z, "minecraft:cobblestone_wall");
      if ((z - BSTART) % 4 === 1) {                     // sparse low light; flanks stay dark
        setB(TX - 2, DECK + 2, z, "minecraft:soul_lantern");
        setB(TX + 2, DECK + 2, z, "minecraft:soul_lantern");
      }

    }
    // ===== 4. pierce the Chamber's north wall with a level stone arch =====
    for (let ox = -1; ox <= 1; ox++) {
      setB(TX + ox, DECK, CWALL, stone());                       // threshold floor (no dip)
      for (let oy = 1; oy <= 4; oy++) air(TX + ox, DECK + oy, CWALL);   // doorway opening
    }
    for (let oy = 1; oy <= 5; oy++) {                            // chiseled jambs
      setB(TX - 2, DECK + oy, CWALL, "minecraft:chiseled_stone_bricks");
      setB(TX + 2, DECK + oy, CWALL, "minecraft:chiseled_stone_bricks");
    }
    for (let ox = -2; ox <= 2; ox++) setB(TX + ox, DECK + 5, CWALL, "minecraft:chiseled_stone_bricks"); // lintel
    setB(TX, DECK + 4, CWALL, "minecraft:lantern", { hanging: true }); // attached to the lintel above
  };
  work();
  return [...cells.values()];
}

const RECORD = "fc_guild_caves_v1";
const PAGE = 64;
const RETRY = 40;
const STALE = 200;
const NATURAL = new Set([
  "air", "stone", "deepslate", "dirt", "coarse_dirt", "rooted_dirt", "gravel",
  "andesite", "diorite", "granite", "tuff", "calcite", "dripstone_block", "clay",
  "sand", "red_sand", "sandstone", "red_sandstone", "grass_block", "podzol",
  "mycelium", "moss_block", "water", "flowing_water", "lava", "flowing_lava",
  "coal_ore", "iron_ore", "copper_ore", "gold_ore", "redstone_ore", "lit_redstone_ore",
  "lapis_ore", "diamond_ore", "emerald_ore", "deepslate_coal_ore", "deepslate_iron_ore",
  "deepslate_copper_ore", "deepslate_gold_ore", "deepslate_redstone_ore",
  "lit_deepslate_redstone_ore", "deepslate_lapis_ore", "deepslate_diamond_ore", "deepslate_emerald_ore",
].map((id) => `minecraft:${id}`));

function signature(name, states) {
  return JSON.stringify([name, Object.entries(states).sort(([a], [b]) => a.localeCompare(b))]);
}

// Walls derive their connections from surrounding blocks. These fields cannot
// be authored invariants; slab height, fluid level and all other states remain
// checked. The saved original fingerprint always retains the full state set.
function targetSignature(name, states) {
  const fixed = { ...states };
  if (name === "minecraft:cobblestone_wall") {
    for (const field of ["wall_connection_type_east", "wall_connection_type_north", "wall_connection_type_south",
      "wall_connection_type_west", "wall_post_bit"]) delete fixed[field];
  }
  return signature(name, fixed);
}

function placementOrder(cell) {
  if (["minecraft:water", "minecraft:lava"].includes(cell.name)) return 3;
  if (["minecraft:lantern", "minecraft:soul_lantern", "minecraft:campfire"].includes(cell.name)) return 2;
  if (cell.name === "minecraft:air") return 1;
  return 0;
}

function hash(text) {
  let h = 2166136261;
  for (let i = 0; i < text.length; i++) h = Math.imul(h ^ text.charCodeAt(i), 16777619) >>> 0;
  return h.toString(16);
}

function manifestCells(manifest, base) {
  const [sx, sy, sz] = manifest.size;
  const [ox, oy, oz] = manifest.origin;
  const cells = [];
  let i = 0;
  for (const [pid, count] of manifest.runs) {
    const block = manifest.palette[pid];
    if (!block || !Number.isInteger(count) || count < 1) throw Error("Invalid Chamber manifest");
    for (let n = 0; n < count; n++, i++) {
      cells.push({ x: base.x + ox + Math.floor(i / (sy * sz)), y: base.y + oy + Math.floor(i / sz) % sy,
        z: base.z + oz + i % sz, name: block.name, states: block.states });
    }
  }
  if (i !== sx * sy * sz) throw Error("Incomplete Chamber manifest");
  return cells;
}

// No Bedrock import: the runtime supplies the real permutation resolver and
// scheduler. Only a newly placed Guild can enroll. Absence of this journal is
// deliberately NOT interpreted as permission to rebuild a saved/occupied cave.
export function createGuildCaveLifecycle({ world, system, chamber, resolve, terrainReady = () => true, onReady = () => {} }) {
  let active = null, nextAttempt = 0, cache = null;
  const keyAt = (i) => `${RECORD}_${i}`;
  const save = (record) => world.setDynamicProperty(RECORD, JSON.stringify(record));
  const baseKey = (base) => JSON.stringify([base.x, base.y, base.z]);
  const validBase = (base) => base && [base.x, base.y, base.z].every(Number.isInteger);
  function read() {
    const raw = world.getDynamicProperty(RECORD);
    return raw === undefined ? null : JSON.parse(raw);
  }
  function plan(base) {
    const anchor = baseKey(base);
    if (cache?.anchor === anchor) return cache;
    const permutations = new Map();
    function target(cell) {
      const key = signature(cell.name, cell.states);
      if (!permutations.has(key)) {
        const permutation = resolve(cell.name, cell.states);
        permutations.set(key, { permutation, signature: targetSignature(cell.name, permutation.getAllStates()) });
      }
      return { ...cell, target: permutations.get(key) };
    }
    const cells = new Map();
    for (const cell of [...manifestCells(chamber, base), ...guildCavePlan(base)]) cells.set(`${cell.x},${cell.y},${cell.z}`, target(cell));
    const entry = new Map(manifestCells(chamber.entry, base).map((cell) => [`${cell.x},${cell.y},${cell.z}`, target(cell).target.signature]));
    // All supports and containment are complete before attached decorations,
    // and every liquid source is last. Yielded placement cannot leak the new
    // skylight water or drop a lantern while its support is still unbuilt.
    const all = [...cells.values()].sort((a, b) => placementOrder(a) - placementOrder(b));
    cache = { anchor, cells: all, entry, hash: hash(JSON.stringify([all.map((c) => [c.x, c.y, c.z, c.target.signature]), [...entry]])) };
    return cache;
  }
  function enroll(base) {
    try {
      if (!validBase(base)) return false;
      const existing = read();
      if (existing) return existing.schema === 1 && existing.anchor === baseKey(base)
        && ["snapshot", "applying", "ready"].includes(existing.phase);
      if (world.getDynamicProperty("fc_guild_caves_done") || world.getDynamicProperty("fc_guild_chamber_placed")) return false;
      // Called before the new surface structure is placed. No block resolver or
      // generated data access can prevent this durable retry marker being made.
      save({ schema: 1, anchor: baseKey(base), phase: "snapshot" });
      return true;
    } catch { return false; }
  }
  function pendingBase() {
    try {
      const record = read();
      if (record?.schema !== 1 || record.phase !== "snapshot") return null;
      const [x, y, z] = JSON.parse(record.anchor);
      const base = { x, y, z };
      return validBase(base) ? base : null;
    } catch { return null; }
  }
  function blockAt(dim, cell) {
    const block = dim.getBlock({ x: cell.x, y: cell.y, z: cell.z });
    if (!block) throw Error("unloaded");
    return block;
  }
  const current = (block) => signature(block.typeId, block.permutation.getAllStates());
  const matchesTarget = (block, cell) => targetSignature(block.typeId, block.permutation.getAllStates()) === cell.target.signature;
  function pageAt(index, owned) {
    const raw = world.getDynamicProperty(keyAt(index));
    if (raw === undefined) return null;
    const page = JSON.parse(raw);
    const length = Math.min(PAGE, owned.cells.length - index * PAGE);
    if (page.hash !== owned.hash || page.original.length !== length || page.done.length !== length
      || !/^[01]+$/.test(page.done) || page.original.some((id) => typeof page.palette[id] !== "string")) throw Error("journal");
    return page;
  }
  function savePage(index, page) {
    const raw = JSON.stringify(page);
    // Bedrock permits 32,767 UTF-8 bytes per string property. Every fingerprint
    // is ASCII for these block IDs/states; keep a deliberately smaller cap.
    if (raw.length > 24000 || /[^\x20-\x7e]/.test(raw)) throw Error("journal-size");
    world.setDynamicProperty(keyAt(index), raw);
  }
  function finish(record) {
    // These compatibility flags are committed only after the complete final
    // plan was verified. Once ready, maintenance performs no more block writes.
    if (!world.getDynamicProperty("fc_guild_chamber_placed")) world.setDynamicProperty("fc_guild_chamber_placed", true);
    if (!world.getDynamicProperty("fc_guild_caves_done")) world.setDynamicProperty("fc_guild_caves_done", true);
    if (!record.notified) {
      record.notified = true;
      save(record); // claim decoration before side effects; never refill on reload
      onReady();
    }
  }
  function maintain(dim, base) {
    if (!validBase(base) || dim?.id !== "minecraft:overworld") return false;
    let record, owned;
    try {
      record = read();
      if (!record || record.schema !== 1 || record.anchor !== baseKey(base)
        || !["snapshot", "applying", "ready"].includes(record.phase)) return false;
      if (record.phase === "ready") { finish(record); return true; }
      if (!terrainReady() || system.currentTick < nextAttempt) return false;
      if (active) {
        if (system.currentTick - active.heartbeat <= STALE) return false;
        // Cancel first, then invalidate its token. A delayed old generator is
        // also fenced at each yield even if clearJob itself fails.
        try { system.clearJob(active.id); } catch { }
        active = null;
      }
      owned = plan(base);
      if (record.phase === "snapshot" && record.hash === undefined && record.count === undefined) {
        record.hash = owned.hash;
        record.count = owned.cells.length;
        save(record);
      }
      if (record.hash !== owned.hash || record.count !== owned.cells.length) return false;
    } catch { return false; }
    const token = { heartbeat: system.currentTick };
    active = token;
    const live = () => active === token;
    function* work() {
      try {
        const pages = Math.ceil(owned.cells.length / PAGE);
        if (record.phase === "snapshot") {
          // Capture every original before the first write. An unavailable or
          // foreign cell refuses the whole build; saved pages cannot be recast
          // as new originals after a retry or reload.
          for (let i = 0; i < pages; i++) {
            if (!live()) return;
            token.heartbeat = system.currentTick;
            if (!pageAt(i, owned)) {
              const page = { hash: owned.hash, palette: [], original: [], done: "" };
              for (const cell of owned.cells.slice(i * PAGE, (i + 1) * PAGE)) {
                const block = blockAt(dim, cell), value = current(block);
                const entry = owned.entry.get(`${cell.x},${cell.y},${cell.z}`);
                if (block.getComponent("minecraft:inventory") || (!NATURAL.has(block.typeId)
                  && entry !== targetSignature(block.typeId, block.permutation.getAllStates()))) throw Error("foreign-original");
                if (!page.palette.includes(value)) page.palette.push(value);
                page.original.push(page.palette.indexOf(value));
                page.done += "0";
              }
              savePage(i, page);
            }
            yield;
          }
          record.phase = "applying";
          delete record.issue;
          save(record);
        }
        for (let i = 0; i < pages; i++) {
          if (!live()) return;
          const page = pageAt(i, owned);
          if (!page) throw Error("journal");
          for (let j = 0; j < page.original.length; j++) {
            if (!live()) return;
            token.heartbeat = system.currentTick;
            const cell = owned.cells[i * PAGE + j], block = blockAt(dim, cell), value = current(block);
            if (!matchesTarget(block, cell)) {
              if (page.done[j] === "1" || value !== page.palette[page.original[j]]
                || block.getComponent("minecraft:inventory")) throw Error("changed-cell");
              block.setPermutation(cell.target.permutation);
              if (!matchesTarget(blockAt(dim, cell), cell)) throw Error("unverified-write");
            }
            if (page.done[j] !== "1") {
              page.done = `${page.done.slice(0, j)}1${page.done.slice(j + 1)}`;
              // Persist each verified cell before yielding or moving on. A
              // successful write followed by a journal failure is recognized
              // by its exact target on retry, without writing it a second time.
              savePage(i, page);
            }
            if (j % 16 === 15) yield;
          }
        }
        // Verification is a separate pass over the assembled final geometry.
        // A changed already-completed cell blocks completion; it is never fixed.
        for (let i = 0; i < owned.cells.length; i++) {
          if (!live()) return;
          token.heartbeat = system.currentTick;
          const cell = owned.cells[i];
          if (!matchesTarget(blockAt(dim, cell), cell)) throw Error("verification-changed");
          if (i % PAGE === PAGE - 1) yield;
        }
        if (!live()) return;
        record.phase = "ready";
        delete record.issue;
        save(record);
        finish(record);
      } catch (error) {
        if (live()) {
          record.issue = String(error?.message ?? "unavailable").slice(0, 80);
          try { save(record); } catch { }
        }
      } finally {
        if (live()) { active = null; nextAttempt = system.currentTick + RETRY; }
      }
    }
    try { token.id = system.runJob(work()); } catch { active = null; nextAttempt = system.currentTick + RETRY; }
    return false;
  }
  return { enroll, maintain, pendingBase };
}

function carveGuildCaves(dim, base) {
  if (world.getDynamicProperty("fc_guild_caves_done")) return;
  if (!world.getDynamicProperty("fc_guild_chamber_placed")) return;
  const setB = (x, y, z, id) => { try { const b = dim.getBlock({ x, y, z }); if (b) b.setType(id); } catch { } };
  const air = (x, y, z) => setB(x, y, z, "minecraft:air");
  const stone = () => (Math.random() < 0.22 ? "minecraft:mossy_stone_bricks" : "minecraft:stone_bricks");
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
  const work = function* () {
    // ===== 1. the SHAFT: a hollow 3x3 around a chiseled pillar, OPEN at the top
    //         and OPEN on its south face so you walk straight in off the Library
    //         alcove (that south wall was the bug the player had to dig through) =====
    for (let y = base.y + 2; y >= DECK - 1; y--) {
      for (let ox = -2; ox <= 2; ox++) for (let oz = -2; oz <= 2; oz++) {
        const cheb = Math.max(Math.abs(ox), Math.abs(oz));
        if (ox === 0 && oz === 0) setB(SX, y, SZ, "minecraft:chiseled_stone_bricks"); // pillar
        else if (cheb === 2) {
          if (oz === 2 && y >= base.y) air(SX + ox, y, SZ + oz);   // open the entry doorway
          else setB(SX + ox, y, SZ + oz, stone());                 // shaft wall
        } else air(SX + ox, y, SZ + oz);                           // hollow interior
      }
      yield;
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
    const slab = () => (Math.random() < 0.22 ? "minecraft:mossy_stone_brick_slab" : "minecraft:stone_brick_slab");
    for (let n = 0; ; n++) {
      const [dx, dz] = ringCW[n % 8];
      const tx = SX + dx, tz = SZ + dz;
      // surface = base.y + 0.5 - 0.5*n ; even n -> bottom slab (top at +.5), odd n -> full course
      const blockY = (n % 2 === 0) ? (base.y - n / 2) : (base.y - (n + 1) / 2);
      if (blockY < DECK || (blockY === DECK && n % 2 === 0)) break;   // end on the full course at deck level
      setB(tx, blockY, tz, (n % 2 === 0) ? slab() : stone());        // the tread
      air(tx, blockY + 1, tz); air(tx, blockY + 2, tz); air(tx, blockY + 3, tz);  // headroom
      if (n % 4 === 0) setB(SX, blockY + 1, SZ, "minecraft:glowstone");           // glowing newel
      yield;
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
      yield;
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
    setB(TX, DECK + 4, CWALL, "minecraft:lantern");              // arch lantern
  };
  try { system.runJob(work()); world.setDynamicProperty("fc_guild_caves_done", true); } catch { }
}


function placeGuildAnnexes(dim) {
  const raw = world.getDynamicProperty("fc_guild_base");
  if (!raw) return;
  let base;
  try { base = JSON.parse(raw); } catch { return; }
  if (!world.getDynamicProperty("fc_guild_chamber_placed")) {
    // the Chamber of Fate sleeps far beneath the Map Room rotunda (local 26,42),
    // so its 31x31 footprint is centred under the dome
    const chx = base.x + 11, chy = base.y - 22, chz = base.z + 27;
    try {
      world.structureManager.place("fc:chamber_of_fate", dim, { x: chx, y: chy, z: chz });
      world.setDynamicProperty("fc_guild_chamber_placed", true);
      // the Cullis crowns a raised HILL now (platform deck local y6, stand y7)
      registerCullis("Chamber of Fate", { x: chx + 15.5, y: chy + 7, z: chz + 15.5 });
      fillLootChests(dim, chx, chy, chz, 31, 20, 31, "fc:chamber_of_fate");
      hangChamberArt(dim, chx, chy, chz, 31);       // best-effort vanilla paintings
      // The Guild's foundation fill (blendTerrain) is an async job that finishes
      // AFTER this and can leak stone through the dome into the Chamber, so scrub
      // it now and again on delays once the foundation has fully settled.
      for (const delay of [10, 200, 600, 1400]) {
        system.runTimeout(() => { try { hollowChamber(dim, chx, chy, chz, 31, 20); } catch { } }, delay);
      }
    } catch { }
  }
  carveGuildCaves(dim, base);                       // spiral + ravine to the Chamber
}


const CHAMBER_FILL = new Set([
  "minecraft:stone", "minecraft:deepslate", "minecraft:dirt", "minecraft:gravel",
  "minecraft:andesite", "minecraft:diorite", "minecraft:granite", "minecraft:tuff",
  "minecraft:cobblestone", "minecraft:water", "minecraft:lava", "minecraft:coarse_dirt",
  "minecraft:calcite", "minecraft:dripstone_block", "minecraft:clay", "minecraft:sand",
  "minecraft:sandstone", "minecraft:grass_block", "minecraft:moss_block",
]);
function hollowChamber(dim, x0, y0, z0, S, H) {
  const c = S >> 1;
  const work = function* () {
    for (let lx = 1; lx < S - 1; lx++) {
      for (let lz = 1; lz < S - 1; lz++) {
        const d = Math.hypot(lx - c, lz - c);
        if (d > 11.4) continue;                 // inside the wall ring only
        for (let ly = 2; ly < H - 3; ly++) {    // stop below the glass/water/glowstone skylight
          let b;
          try { b = dim.getBlock({ x: x0 + lx, y: y0 + ly, z: z0 + lz }); } catch { continue; }
          if (b && !b.isAir && CHAMBER_FILL.has(b.typeId)) {
            try { b.setType("minecraft:air"); } catch { }
          }
        }
      }
      yield;
    }
  };
  try { system.runJob(work()); } catch { }
}


const CULLIS_CORE = new Set(["minecraft:beacon", "minecraft:sea_lantern"]);
const CULLIS_RING = new Set(["minecraft:chiseled_stone_bricks", "minecraft:obsidian",
  "minecraft:crying_obsidian", "minecraft:polished_deepslate", "minecraft:deepslate_tiles",
  "minecraft:quartz_block", "minecraft:smooth_quartz", "minecraft:amethyst_block"]);
function isCullisConfigured(dim, s) {
  try {
    let core = false;
    for (const dy of [0, -1, 1]) {
      const b = dim.getBlock({ x: s.x, y: s.y + dy, z: s.z });
      if (b && CULLIS_CORE.has(b.typeId)) { core = true; break; }
    }
    if (!core) return false;
    let ring = 0;
    for (const [dx, dz] of [[2, 0], [-2, 0], [0, 2], [0, -2], [3, 0], [-3, 0], [0, 3], [0, -3]]) {
      for (const dy of [0, 1, -1]) {
        const b = dim.getBlock({ x: s.x + dx, y: s.y + dy, z: s.z + dz });
        if (b && CULLIS_RING.has(b.typeId)) { ring++; break; }
      }
    }
    return ring >= 3;
  } catch { return false; }
}


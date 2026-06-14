// ============================================================================
// Fablecraft: Reforged — main gameplay script
// Hero stats (Strength/Skill/Will XP), morality, combat multiplier, Will
// powers, quests, Demon Doors, NPC dialogue, traders, world decoration,
// boss phases (Jack of Blades), augments, and the Guild.
// ============================================================================
import {
  world, system, EquipmentSlot, EntityDamageCause, ItemStack,
} from "@minecraft/server";
import {
  ActionFormData, MessageFormData, ModalFormData,
} from "@minecraft/server-ui";
import { DATA } from "./fc_gamedata.js";

const OW = () => world.getDimension("overworld");
const TICKS = () => system.currentTick;

// ---------------------------------------------------------------------------
// Hero state helpers (player dynamic properties)
// ---------------------------------------------------------------------------
const P = {
  get(p, k, d = 0) { const v = p.getDynamicProperty(k); return v === undefined ? d : v; },
  set(p, k, v) { p.setDynamicProperty(k, v); },
  add(p, k, dv) { const v = P.get(p, k, 0) + dv; p.setDynamicProperty(k, v); return v; },
  getJ(p, k, d) { const v = p.getDynamicProperty(k); if (!v) return d; try { return JSON.parse(v); } catch { return d; } },
  setJ(p, k, o) { p.setDynamicProperty(k, JSON.stringify(o)); },
};

const XP_KEYS = { general: "fc_xp_general", strength: "fc_xp_strength", skill: "fc_xp_skill", will: "fc_xp_will" };
const XP_COLOR = { general: "§a", strength: "§c", skill: "§9", will: "§e" };
const NPC_SOUND_CUES = {
  "fc:balverine": { sound: "fc.entity.balverine", range: 18, chance: 0.18, cooldown: 180, volume: 0.62, pitch: [0.92, 1.08] },
  "fc:white_balverine": { sound: "fc.entity.white_balverine", range: 24, chance: 0.22, cooldown: 160, volume: 0.78, pitch: [0.82, 0.98] },
  "fc:frost_balverine": { sound: "fc.entity.frost_balverine", range: 20, chance: 0.18, cooldown: 180, volume: 0.68, pitch: [0.9, 1.05] },
  "fc:summoned_balverine": { sound: "fc.entity.summoned_balverine", range: 16, chance: 0.12, cooldown: 220, volume: 0.52, pitch: [0.96, 1.12] },
  "fc:banshee": { sound: "fc.entity.banshee", range: 18, chance: 0.16, cooldown: 180, volume: 0.68, pitch: [0.92, 1.06] },
  "fc:wraith": { sound: "fc.entity.wraith", range: 18, chance: 0.14, cooldown: 200, volume: 0.62, pitch: [0.86, 1.02] },
  "fc:hobbe": { sound: "fc.entity.hobbe", range: 14, chance: 0.14, cooldown: 200, volume: 0.52, pitch: [0.95, 1.14] },
  "fc:hobbe_scout": { sound: "fc.entity.hobbe_scout", range: 14, chance: 0.14, cooldown: 200, volume: 0.5, pitch: [1.04, 1.2] },
  "fc:earth_troll": { sound: "fc.entity.earth_troll", range: 24, chance: 0.12, cooldown: 220, volume: 0.78, pitch: [0.84, 0.96] },
  "fc:ice_troll": { sound: "fc.entity.ice_troll", range: 24, chance: 0.12, cooldown: 220, volume: 0.78, pitch: [0.86, 0.98] },
  "fc:rock_giant": { sound: "fc.entity.rock_giant", range: 28, chance: 0.12, cooldown: 240, volume: 0.82, pitch: [0.78, 0.92] },
  "fc:wasp": { sound: "fc.entity.wasp", range: 12, chance: 0.12, cooldown: 160, volume: 0.38, pitch: [0.95, 1.12] },
  "fc:wasp_queen": { sound: "fc.entity.wasp_queen", range: 18, chance: 0.16, cooldown: 180, volume: 0.56, pitch: [0.82, 1.0] },
  "fc:arachanox": { sound: "fc.entity.arachanox", range: 22, chance: 0.16, cooldown: 200, volume: 0.7, pitch: [0.82, 0.98] },
};
const npcSoundCooldown = new Map();

// Fable: The Lost Chapters menu dressing
const FABLE_RULE = "§8════════════§6❦§8════════════";
const FABLE_DOT = "§6❖ ";
function fableTitle(t) { return `§8‹§6❦§8› §6§l${t}§r §8‹§6❦§8›`; }

function maybePlayNpcCue(p, e, cue) {
  const key = `${p.id}|${e.id}|${cue.sound}`;
  const now = TICKS();
  if ((npcSoundCooldown.get(key) ?? -99999) + cue.cooldown > now) return;
  if (Math.random() >= cue.chance) return;
  npcSoundCooldown.set(key, now);
  const pitch = cue.pitch[0] + Math.random() * (cue.pitch[1] - cue.pitch[0]);
  p.playSound(cue.sound, { volume: cue.volume, pitch });
}

function giveXp(p, type, amount) {
  if (amount <= 0) return;
  const mult = 1 + Math.min(25, P.get(p, "fc_mult", 0)) * 0.08;
  const total = Math.round(amount * mult);
  P.add(p, XP_KEYS[type], total);
  if (type !== "general") P.add(p, XP_KEYS.general, Math.round(total * 0.4));
}

function morality(p) { return P.get(p, "fc_morality", 0); }
function addMorality(p, dv) {
  const v = Math.max(-1000, Math.min(1000, morality(p) + dv));
  P.set(p, "fc_morality", v);
  if (Math.abs(dv) >= 25) {
    p.sendMessage(dv > 0 ? `§e✦ The light favours you. (+${dv} morality)` : `§5✦ Darkness seeps into your soul. (${dv} morality)`);
  }
  return v;
}
function moralityTitle(p) {
  const m = morality(p);
  if (m >= 750) return "§eParagon";
  if (m >= 400) return "§eSaint";
  if (m >= 150) return "§aGood";
  if (m > -150) return "§7Neutral";
  if (m > -400) return "§cRogue";
  if (m > -750) return "§cVillain";
  return "§5Avatar of Skorm";
}

function maxWill(p) { return 100 + P.get(p, "fc_up_magic_power", 0) * 50; }
function willEnergy(p) { return Math.min(maxWill(p), P.get(p, "fc_will", 100)); }
function spendWill(p, amt) {
  const w = willEnergy(p);
  if (w < amt) return false;
  P.set(p, "fc_will", w - amt);
  return true;
}

// ---------------------------------------------------------------------------
// Inventory helpers
// ---------------------------------------------------------------------------
function inv(p) { return p.getComponent("minecraft:inventory")?.container; }
function countItem(p, id) {
  const c = inv(p); if (!c) return 0;
  let n = 0;
  for (let i = 0; i < c.size; i++) { const it = c.getItem(i); if (it?.typeId === id) n += it.amount; }
  return n;
}
function removeItem(p, id, count) {
  const c = inv(p); if (!c) return false;
  if (countItem(p, id) < count) return false;
  let left = count;
  for (let i = 0; i < c.size && left > 0; i++) {
    const it = c.getItem(i);
    if (it?.typeId !== id) continue;
    const take = Math.min(left, it.amount);
    left -= take;
    if (it.amount - take <= 0) c.setItem(i, undefined);
    else { it.amount -= take; c.setItem(i, it); }
  }
  return true;
}
function giveItem(p, id, count = 1) {
  try {
    let left = count;
    while (left > 0) {
      const batch = Math.min(64, left);
      const st = new ItemStack(id, batch);
      inv(p)?.addItem(st);
      left -= batch;
    }
  } catch {
    try { p.runCommand(`give @s ${id} ${count}`); } catch { }
  }
}

function ensureGuildSeal(p) {
  if (countItem(p, "fc:guild_seal") >= 1) return;
  giveItem(p, "fc:guild_seal", 1);
  if (countItem(p, "fc:guild_seal") >= 1) return;
  // Last-resort fallback: force one seal into the final inventory slot.
  const c = inv(p);
  if (!c) return;
  try {
    c.setItem(c.size - 1, new ItemStack("fc:guild_seal", 1));
  } catch { }
}

function heldItem(p) {
  return p.getComponent("minecraft:equippable")?.getEquipment(EquipmentSlot.Mainhand);
}
function setHeld(p, item) {
  p.getComponent("minecraft:equippable")?.setEquipment(EquipmentSlot.Mainhand, item);
}

// ---------------------------------------------------------------------------
// First spawn: Chamber of Fate, starter kit, Guild placement
// ---------------------------------------------------------------------------
world.afterEvents.playerSpawn.subscribe((ev) => {
  const p = ev.player;
  try { ensureBaseTitles(p); } catch { }         // Sparrow + Apprentice start unlocked
  try { applyTitleTag(p); } catch { }            // re-wear the chosen title
  if (!ev.initialSpawn) {
    // Respawning after death — a Hero of the Guild always carries their seal.
    ensureGuildSeal(p);
    setGuildSpawn(p);
    return;
  }
  system.runTimeout(() => initHero(p), 20);
});

// Point the player's respawn location at the Guild rather than whatever
// patch of world (often a lake or village well) the game first chose.
function setGuildSpawn(p) {
  const raw = world.getDynamicProperty("fc_guild_loc");
  if (!raw) return;
  try {
    const loc = JSON.parse(raw);
    p.setSpawnPoint({ dimension: p.dimension, x: Math.floor(loc.x), y: Math.floor(loc.y), z: Math.floor(loc.z) });
  } catch { }
}

// If the Hero's first spawn dropped them into water (a fountain, well, lake,
// etc.), walk them out onto the nearest dry ground before the Guild is laid
// out around them.
function ensureDryLanding(p) {
  const dim = p.dimension;
  const fx = Math.floor(p.location.x), fz = Math.floor(p.location.z);
  const below = dim.getBlock({ x: fx, y: Math.floor(p.location.y) - 1, z: fz });
  if (!below?.isLiquid) return;
  for (let r = 1; r <= 16; r++) {
    for (let dx = -r; dx <= r; dx++) {
      for (let dz = -r; dz <= r; dz++) {
        if (Math.max(Math.abs(dx), Math.abs(dz)) !== r) continue;
        const x = fx + dx, z = fz + dz;
        const y = groundY(dim, x, z);
        if (y === null) continue;
        const ground = dim.getBlock({ x, y: y - 1, z });
        if (ground && !ground.isLiquid) {
          p.teleport({ x: x + 0.5, y, z: z + 0.5 });
          return;
        }
      }
    }
  }
}

function initHero(p) {
  if (P.get(p, "fc_init", false)) return;
  P.set(p, "fc_init", true);
  P.set(p, "fc_will", 100);
  for (const it of ["fc:stick", "fc:guild_seal", "fc:quest_card",
    "fc:apprentice_helm", "fc:apprentice_torso", "fc:apprentice_legs", "fc:apprentice_boots",
    "fc:health_potion", "fc:apple_pie"]) giveItem(p, it, 1);
  ensureGuildSeal(p);
  giveItem(p, "fc:gold_coin", 5);
  p.onScreenDisplay.setTitle("§6Fablecraft", { fadeInDuration: 10, stayDuration: 70, fadeOutDuration: 20, subtitle: "§eReforged — Welcome to Albion" });
  p.sendMessage("§6═══ The Guildmaster ═══");
  p.sendMessage("§f\"Ah, the new apprentice wakes. Your §eGuild Seal§f opens the Hero menu. Use a §eQuest Card§f to begin your training. Albion is watching, little sparrow.\"");
  ensureDryLanding(p);
  placeGuildNear(p);
  setGuildSpawn(p);
}

const GUILD_TA = "fc_guild_keep";  // ticking area that force-loads the campus

// Pin the whole 92x100 Guild footprint with a ticking area so every chunk is
// force-loaded regardless of the player's render/simulation distance. The
// campus is far wider than the few chunks a low render distance keeps live, so
// without this the far rooms (Library, Maze's Tower) would land in unloaded
// chunks and silently fail to generate. Idempotent — adds the area only once.
function forceLoadGuild(dim, p, base) {
  if (world.getDynamicProperty("fc_guild_ta")) return;
  const cmd = `tickingarea add ${base.x - 4} 0 ${base.z - 4} ${base.x + 96} 319 ${base.z + 104} ${GUILD_TA}`;
  dim.runCommandAsync(cmd).then(() => {
    world.setDynamicProperty("fc_guild_ta", true);
  }).catch(() => {
    try { p.runCommandAsync(cmd); world.setDynamicProperty("fc_guild_ta", true); } catch { }
  });
}

function placeGuildNear(p) {
  if (world.getDynamicProperty("fc_guild_placed")) return;
  // Self-healing guard: only one build runs at a time, but if a build attempt
  // ever stalls or throws without rescheduling itself, the timestamp goes stale
  // and the next sweep restarts it — so the Guild can never be wedged "never
  // spawning" by a single failed attempt.
  const now = system.currentTick;
  const last = world.getDynamicProperty("fc_guild_build_tick");
  if (typeof last === "number" && now - last < 200) return;  // a build is in flight
  world.setDynamicProperty("fc_guild_build_tick", now);
  const dim = p.dimension;
  const base = { x: Math.floor(p.location.x) + 16, y: 0, z: Math.floor(p.location.z) + 16 };
  try { buildGuildWhenReady(p, dim, base, 0); } catch { /* stale tick lets the sweep retry */ }
}

// Force-load the footprint, wait for the chunks to report ready, then build the
// whole Guild in one place call. Retries for ~5 minutes so generation succeeds
// even when the player's render distance leaves most of the campus unloaded.
function buildGuildWhenReady(p, dim, base, attempt) {
  if (world.getDynamicProperty("fc_guild_placed")) return;
  world.setDynamicProperty("fc_guild_build_tick", system.currentTick);  // keep the guard fresh while working
  forceLoadGuild(dim, p, base);
  const y = sampleGroundY(dim, base.x, base.z, 92, 100, true);
  if (y === null) {  // chunks still loading — try again shortly
    if (attempt < 600) system.runTimeout(() => buildGuildWhenReady(p, dim, base, attempt + 1), 10);
    return;  // else stop refreshing — the stale tick lets the next sweep restart us
  }
  p.onScreenDisplay.setTitle("§6Founding Guild...", { fadeInDuration: 0, stayDuration: 200, fadeOutDuration: 0, subtitle: "§ePlease wait..." });
  system.runTimeout(() => {
  try {
    // The Heroes' Guild is ONE connected 92x30x100 structure on a single floor
    // level. The heart is the domed Map Room rotunda at local (34,44); the
    // Cullis Gate glows in its LEFT/west alcove (21,44) and the green Skill
    // portal in its RIGHT/east alcove (47,44). The pillared nave runs south to
    // the gatehouse; the Dining Hall lies east; the two-storey Library runs
    // north to the Guild-Cave door; Maze's Tower spire stands NE (study floor
    // at local y+15). The Hero wakes on the crimson runner at (34,~30).
    world.structureManager.place("fc:guild_hall", dim, { x: base.x, y, z: base.z });
  } catch {  // chunk-edge race — retry; the ticking area keeps loading them
    if (attempt < 600) system.runTimeout(() => buildGuildWhenReady(p, dim, base, attempt + 1), 10);
    return;  // else stop refreshing — the stale tick lets the next sweep restart us
  }
  world.setDynamicProperty("fc_guild_placed", true);
  world.setDynamicProperty("fc_guild_base", JSON.stringify({ x: base.x, y, z: base.z }));
  // New ground plan: you enter from the WEST onto the crimson runner before the
  // Map Room rotunda (local 26,42). Wake at (21,42), facing east to the Map.
  world.setDynamicProperty("fc_guild_loc", JSON.stringify({ x: base.x + 21, y, z: base.z + 42 }));
  // Skill / Experience shrine in the Map Room's NW nook (local 15,35)
  world.setDynamicProperty("fc_guild_train", JSON.stringify({ x: base.x + 15, y, z: base.z + 35 }));
  world.setDynamicProperty("fc_guild_skill", JSON.stringify({ x: base.x + 15, y, z: base.z + 35 }));
  // the Quest lectern at the near (south) edge of the Map relief (local 26,37)
  world.setDynamicProperty("fc_guild_quest_table", JSON.stringify({ x: base.x + 29, y: y + 1, z: base.z + 38 }));
  // the Guild's own Demon Door — the crag on the far south bank past the islands
  const doorLoc = { x: base.x + 56, y: y + 1, z: base.z + 94.4 };
  world.setDynamicProperty("fc_guild_door", JSON.stringify(doorLoc));
  // Everything below is decoration: NPCs, the Cullis registration, loot, terrain
  // and the buried Chamber. The Guild is already PLACED above, so none of this is
  // allowed to abort the build — wrap it so a single failure can't matter.
  try {
    // the Cullis Gate beacon core in the Map Room's SW nook (local 15,49)
    registerCullis("Heroes' Guild", { x: base.x + 15, y: y + 1, z: base.z + 49 });
    // Guildmaster greets arrivals at the Map; Maze keeps his tower study; Theresa
    // reads in the Library (north); a trader works the Store (south).
    trySpawn(dim, "fc:guildmaster", { x: base.x + 23, y: y + 1, z: base.z + 42 });
    trySpawn(dim, "fc:maze", { x: base.x + 46, y: y + 11, z: base.z + 72 });   // tower floor 3
    trySpawn(dim, "fc:theresa", { x: base.x + 26, y: y + 1, z: base.z + 23 });
    // a Trader works the covered cart OUTSIDE the west gate (random wares + a title)
    trySpawn(dim, "fc:trader", { x: base.x + 5, y: y + 1, z: base.z + 46 });
    // apprentices at work across the grounds
    trySpawn(dim, "fc:guild_apprentice_might", { x: base.x + 12, y: y + 1, z: base.z + 42 });
    trySpawn(dim, "fc:guild_apprentice_might", { x: base.x + 80, y: y + 1, z: base.z + 54 });
    trySpawn(dim, "fc:guild_apprentice_skill", { x: base.x + 68, y: y + 1, z: base.z + 38 });
    trySpawn(dim, "fc:guild_apprentice_skill", { x: base.x + 42, y: y + 1, z: base.z + 40 });
    trySpawn(dim, "fc:guild_apprentice_will", { x: base.x + 26, y: y + 1, z: base.z + 24 });
    trySpawn(dim, "fc:guild_apprentice_will", { x: base.x + 16, y: y + 1, z: base.z + 35 });
    // suits of armour stand guard at Maze's Tower's two ground entrances
    guardArmour(dim, { x: base.x + 41, y: y + 1, z: base.z + 72 }, { x: base.x + 40, y: y + 1, z: base.z + 72 });
    guardArmour(dim, { x: base.x + 46, y: y + 1, z: base.z + 67 }, { x: base.x + 46, y: y + 1, z: base.z + 66 });
    ensureDemonDoor(dim, doorLoc, base.z + 86);
    fillLootChests(dim, base.x, y, base.z, 92, 30, 100, "fc:guild_hall");
    blendTerrain(dim, base.x, y, base.z, 92, 100);
    skirtTerrain(dim, base.x, y, base.z, 92, 100, 16);
    dressSurroundings(dim, base.x, y, base.z, 92, "holy");
    populateSurroundings(dim, base);                 // biome-matched woods around the campus
    layWoodsPath(dim, base);                          // the orange dirt trail out to the Woods
    placeGuildAnnexes(dim);
    setGuildSpawn(p);
  } catch { /* decoration is best-effort; the Guild itself is already placed */ }
  // wake the new Hero on the dry crimson runner, facing north to the Map Room
  system.runTimeout(() => {
    try {
      p.teleport({ x: base.x + 21.5, y: y + 1, z: base.z + 42.5 },
        { facingLocation: { x: base.x + 26, y: y + 2, z: base.z + 42 } });
      p.sendMessage("§6⚔ You awaken in the Heroes' Guild. The §bCullis Gate§6 glows in the Map Room's south-west nook; the §aSkill Shrine§6 waits to the north-west.");
    } catch { }
  }, 10);
  }, 5);
}

// The Guild hall itself is a single connected structure placed by
// placeGuildNear. The only remaining annex is the Chamber of Fate, buried far
// beneath the hall; it keeps its own flag so chunk-edge failures retry later.
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
      registerCullis("Chamber of Fate", { x: chx + 15.5, y: chy + 2, z: chz + 15.5 });
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

// Carve the Guild Caves: a 3x3 spiral stair (central glowing pillar) carries the
// ENTIRE descent from the Library's caves alcove down to the Chamber floor level,
// then a long, DEAD-LEVEL stone causeway crosses a wide, deep, DARK gulf and
// pierces the Chamber of Fate's north wall through a level arch. The descent is
// all on the spiral; the bridge never slopes, so the walk is jump-free end to
// end (alcove -> spiral down -> flat span over darkness -> arch -> Chamber).
// Runtime-carved because it spans the surface build down to the buried Chamber.
// Idempotent, bounded, and fully wrapped so it can never break a build.
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
    // ===== 2. the DESCENT: a true helix winding the shaft, ONE course down per
    //         cell, carrying the WHOLE vertical drop down to deck level so the
    //         causeway itself can stay dead level. The pillar glows to light it. =====
    air(SX, base.y, SZ + 1);                            // open the entry mouth
    for (let n = 0; ; n++) {
      const [dx, dz] = ringCW[n % 8];
      const ty = base.y - 1 - n;                        // one step down per cell
      if (ty < DECK) break;
      setB(SX + dx, ty, SZ + dz, stone());             // tread you stand on
      setB(SX + dx, ty - 1, SZ + dz, stone());         // solid beneath the tread
      air(SX + dx, ty + 1, SZ + dz);                   // 3 of headroom for the step-down
      air(SX + dx, ty + 2, SZ + dz);
      air(SX + dx, ty + 3, SZ + dz);
      if (n % 3 === 0) setB(SX, ty + 1, SZ, "minecraft:glowstone");   // glowing newel
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

// Populate the land just outside the Guild with biome-matched trees and ground
// cover so the campus melts into the surrounding wilds instead of sitting on a
// bare ring. Idempotent; bounded; fully wrapped.
function populateSurroundings(dim, base) {
  if (world.getDynamicProperty("fc_guild_wild_done")) return;
  const W = 92, D = 100, R = 26;
  const setBlk = (x, y, z, id) => { try { const b = dim.getBlock({ x, y, z }); if (b) b.setType(id); } catch { } };
  const work = function* () {
    for (let n = 0; n < 240; n++) {
      const side = n & 3, off = 2 + Math.floor(Math.random() * R);
      let px, pz;
      if (side === 0) { px = base.x - off; pz = base.z + Math.floor(Math.random() * D); }
      else if (side === 1) { px = base.x + W + off; pz = base.z + Math.floor(Math.random() * D); }
      else if (side === 2) { pz = base.z - off; px = base.x + Math.floor(Math.random() * W); }
      else { pz = base.z + D + off; px = base.x + Math.floor(Math.random() * W); }
      const gy = groundY(dim, px, pz);
      if (gy === null) { yield; continue; }
      let g; try { g = dim.getBlock({ x: px, y: gy - 1, z: pz }); } catch { g = null; }
      const slot = (() => { try { return dim.getBlock({ x: px, y: gy, z: pz }); } catch { return null; } })();
      if (!g || !slot || !slot.isAir) { yield; continue; }
      const t = g.typeId;
      const grassy = t.includes("grass") || t === "minecraft:dirt" || t.includes("podzol") || t.includes("moss");
      if (t.includes("water") || t.includes("ice")) { yield; continue; }
      if (Math.random() < 0.35) {                      // ground cover
        setBlk(px, gy, pz, t.includes("snow") ? "minecraft:snow_layer"
          : (Math.random() < 0.5 ? "minecraft:tallgrass" : "minecraft:fern"));
        yield; continue;
      }
      if (!grassy && !t.includes("snow")) { yield; continue; }
      const spruce = t.includes("podzol") || t.includes("snow") || t.includes("spruce") || t.includes("moss");
      const trunk = spruce ? "minecraft:spruce_log" : (Math.random() < 0.3 ? "minecraft:birch_log" : "minecraft:oak_log");
      const leaf = spruce ? "minecraft:spruce_leaves" : (trunk.includes("birch") ? "minecraft:birch_leaves" : "minecraft:oak_leaves");
      const h = 4 + Math.floor(Math.random() * 3);
      for (let i = 0; i < h; i++) setBlk(px, gy + i, pz, trunk);
      for (let dx = -2; dx <= 2; dx++) for (let dz = -2; dz <= 2; dz++) for (let dy = h - 2; dy <= h; dy++)
        if (Math.abs(dx) + Math.abs(dz) + Math.abs(dy - h + 1) <= 3 && Math.random() < 0.85)
          setBlk(px + dx, gy + dy, pz + dz, leaf);
      yield;
    }
    world.setDynamicProperty("fc_guild_wild_done", true);
  };
  try { system.runJob(work()); } catch { }
}

// Guarantee the Chamber of Fate reads as an open, hollow hall even when it is
// stamped into solid deepslate: clear any *natural* rock that intruded into the
// room volume, while leaving the structure's own masonry, columns, frescoes and
// dais untouched (we only delete raw stone/dirt/ore, never built blocks).
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

// Hang real paintings on the chamber's cardinal walls (best-effort — the engine
// picks whatever motif fits the space; mismatched art is fine, it's the gallery
// feel that matters). The block frescoes carry the look if this no-ops.
function hangChamberArt(dim, x0, y0, z0, S) {
  const c = S >> 1, y = y0 + 6;
  // (offset toward centre, facing) for each cardinal wall
  const spots = [
    { x: x0 + c, z: z0 + 2, dir: "south" },
    { x: x0 + c, z: z0 + S - 3, dir: "north" },
    { x: x0 + 2, z: z0 + c, dir: "east" },
    { x: x0 + S - 3, z: z0 + c, dir: "west" },
  ];
  for (const s of spots) {
    try {
      const e = dim.spawnEntity("minecraft:painting", { x: s.x + 0.5, y, z: s.z + 0.5 });
      try { e.setProperty?.("minecraft:cardinal_direction", s.dir); } catch { }
    } catch { }
  }
}

function trySpawn(dim, type, loc) { try { return dim.spawnEntity(type, loc); } catch { return undefined; } }

// A "suit of armour" on guard: an armour stand kitted in iron, facing the door.
// Idempotent — won't stack duplicates if the build sweep re-runs.
function guardArmour(dim, loc, faceLoc) {
  try {
    if (dim.getEntities({ location: loc, maxDistance: 2, type: "minecraft:armor_stand" }).length) return;
    const a = dim.spawnEntity("minecraft:armor_stand", loc);
    try { a.teleport(loc, { facingLocation: faceLoc }); } catch { }
    const eq = a.getComponent("minecraft:equippable");
    if (eq) {
      eq.setEquipment(EquipmentSlot.Head, new ItemStack("minecraft:iron_helmet"));
      eq.setEquipment(EquipmentSlot.Chest, new ItemStack("minecraft:iron_chestplate"));
      eq.setEquipment(EquipmentSlot.Legs, new ItemStack("minecraft:iron_leggings"));
      eq.setEquipment(EquipmentSlot.Feet, new ItemStack("minecraft:iron_boots"));
      eq.setEquipment(EquipmentSlot.Mainhand, new ItemStack("minecraft:iron_sword"));
    }
  } catch { }
}

function groundY(dim, x, z, allowLiquid = false) {
  for (let y = 120; y > 40; y--) {
    try {
      const b = dim.getBlock({ x, y, z });
      const below = dim.getBlock({ x, y: y - 1, z });
      if (b?.isAir && below && !below.isAir && (allowLiquid || !below.isLiquid)) return y;
    } catch { return null; }
  }
  return null;
}

// ---------------------------------------------------------------------------
// Guild wards — the grounds around the Guild Hall are sacred: hostile mobs
// are turned away at the boundary, and any that get close to a defender
// (Guildmaster, Maze, or an apprentice) are cut down on sight.
// ---------------------------------------------------------------------------
function guildBounds() {
  const raw = world.getDynamicProperty("fc_guild_base");
  if (!raw) return null;
  let base; try { base = JSON.parse(raw); } catch { return null; }
  return {
    base,
    // the Guild is one 92x30x100 structure (rotunda + nave + wings + library +
    // tower + grounds), with the Chamber of Fate buried beneath it
    minX: base.x - 3, maxX: base.x + 95,
    minZ: base.z - 3, maxZ: base.z + 103,
    minY: base.y - 26, maxY: base.y + 32,
  };
}

// ---------------------------------------------------------------------------
// Connected campus + world spacing. The Guild's pieces are laced together with
// worn paths; randomly-rendered locations keep clear of the Guild and of each
// other so the world never overlaps two builds into one tangle.
// ---------------------------------------------------------------------------
function layPath(dim, x, z, mat = "minecraft:dirt_path") {
  const gy = groundY(dim, x, z);
  if (gy === null) return;
  try {
    const below = dim.getBlock({ x, y: gy - 1, z });
    if (below && !below.isAir && !below.isLiquid) below.setType(mat);
  } catch { }
}
// The Guild's east DIRT PATH (the plan's ORANGE branch): continues the
// in-structure track out past Exit C (local z=32) into the Guild Woods, hugging
// the natural ground so it reads as a worn forest trail that gently wanders and
// forks. 2 wide, idempotent, bounded, fully wrapped so it can never break a build.
function layWoodsPath(dim, base) {
  if (world.getDynamicProperty("fc_guild_woodspath_done")) return;
  const z0 = base.z + 32;                            // Exit C centreline
  const work = function* () {
    let z = z0;
    for (let i = 0; i < 30; i++) {                   // main trail, heading east
      const x = base.x + 92 + i;                     // just outside the east wall, onward
      if (i > 5 && Math.random() < 0.3) z += (Math.random() < 0.5 ? 1 : -1);  // gentle wander
      for (let dz = -1; dz <= 0; dz++) layPath(dim, x, z + dz);   // 2 wide
      yield;
    }
    let fz = z0;                                     // a fork peeling off to the north-east
    for (let i = 0; i < 14; i++) {
      const x = base.x + 102 + i;
      fz -= 1;
      for (let dz = -1; dz <= 0; dz++) layPath(dim, x, fz + dz);
      yield;
    }
  };
  try { system.runJob(work()); world.setDynamicProperty("fc_guild_woodspath_done", true); } catch { }
}
function connectGuildPaths(dim, base) {
  if (world.getDynamicProperty("fc_guild_paths_done")) return;
  // gate axis: Sentinel Gate -> courtyard -> hall gate (N-S along x = base.x+22)
  for (let z = base.z - 40; z <= base.z + 1; z++) {
    for (let dx = -1; dx <= 1; dx++) layPath(dim, base.x + 22 + dx, z);
  }
  // hall <-> Armoury (west) and hall <-> Scriptorium (east), along z = base.z+16
  for (let x = base.x - 9; x <= base.x; x++) layPath(dim, x, base.z + 16);
  for (let x = base.x + 44; x <= base.x + 54; x++) layPath(dim, x, base.z + 16);
  world.setDynamicProperty("fc_guild_paths_done", true);
}

function rectsOverlap(ax0, az0, ax1, az1, bx0, bz0, bx1, bz1) {
  return ax0 <= bx1 && bx0 <= ax1 && az0 <= bz1 && bz0 <= az1;
}
// would a w×w footprint at (x,z) crowd the Guild grounds or an existing build?
function tooCloseToExisting(x, z, w, margin) {
  const g = guildBounds();
  if (g && rectsOverlap(x - margin, z - margin, x + w + margin, z + w + margin,
    g.minX, g.minZ, g.maxX, g.maxZ)) return true;
  const places = JSON.parse(world.getDynamicProperty("fc_places") ?? "[]");
  for (const pl of places) {
    if (rectsOverlap(x - margin, z - margin, x + w + margin, z + w + margin,
      pl.x, pl.z, pl.x + pl.w, pl.z + pl.w)) return true;
  }
  return false;
}
function recordPlace(x, z, w, id, theme) {
  const places = JSON.parse(world.getDynamicProperty("fc_places") ?? "[]");
  places.push({ x, z, w, id, theme, k: `${x}_${z}` });
  if (places.length > 160) places.splice(0, places.length - 160);
  world.setDynamicProperty("fc_places", JSON.stringify(places));
}

system.runInterval(() => {
  const b = guildBounds();
  if (!b) return;
  const dim = OW();
  const cx = (b.minX + b.maxX) / 2, cz = (b.minZ + b.maxZ) / 2;
  const radius = Math.max(b.maxX - b.minX, b.maxZ - b.minZ) / 2 + 6;
  for (const mob of dim.getEntities({ location: { x: cx, y: b.base.y, z: cz }, maxDistance: radius + 24, families: ["monster"] })) {
    const loc = mob.location;
    if (loc.x < b.minX || loc.x > b.maxX || loc.z < b.minZ || loc.z > b.maxZ || loc.y < b.minY || loc.y > b.maxY) continue;
    // Guild grounds are fully protected: hostile mobs cannot remain inside.
    const defender = dim.getEntities({ location: loc, maxDistance: 24, families: ["fc_guild_defender"] })[0];
    try {
      if (defender) mob.applyDamage(1000, { cause: EntityDamageCause.entityAttack, damagingEntity: defender });
      else mob.kill();
      dim.spawnParticle("minecraft:critical_hit_emitter", loc);
    } catch {
      try { mob.kill(); } catch { }
    }
  }
}, 10);

// ---------------------------------------------------------------------------
// Combat multiplier + kill XP + morality + augment effects
// ---------------------------------------------------------------------------
world.afterEvents.entityHitEntity.subscribe((ev) => {
  const src = ev.damagingEntity, tgt = ev.hitEntity;
  if (src?.typeId !== "minecraft:player" || !tgt) return;
  const p = src;
  // combat multiplier
  P.add(p, "fc_mult", 1);
  P.set(p, "fc_lastHit", TICKS());
  // augment effects from held weapon lore
  const it = heldItem(p);
  if (it && DATA.weapons[it.typeId]) {
    if (Math.random() < 0.35) p.playSound("fc.sword_clash", { volume: 0.45, pitch: 0.9 + Math.random() * 0.25 });
    const augs = weaponAugments(it);
    applyAugmentHits(p, tgt, augs);
  }
});

world.afterEvents.entityHurt.subscribe((ev) => {
  const e = ev.hurtEntity;
  if (e?.typeId !== "minecraft:player") return;
  // taking damage resets the multiplier — Fable rules
  if (ev.damage > 0) P.set(e, "fc_mult", 0);
  // Resurrection Phial: cheat death at the brink
  const hp = e.getComponent("minecraft:health");
  if (hp && hp.currentValue > 0 && hp.currentValue <= 3 && countItem(e, "fc:resurrection_phial") > 0) {
    removeItem(e, "fc:resurrection_phial", 1);
    hp.setCurrentValue(Math.min(hp.effectiveMax, 14));
    P.set(e, "fc_will", maxWill(e));
    e.dimension.spawnParticle("minecraft:totem_particle", e.location);
    e.playSound("random.totem");
    e.sendMessage("§6✦ The Resurrection Phial shatters — death is cheated, this once.");
  }
});

function familyOf(entity) {
  const fam = entity.getComponent("minecraft:type_family");
  if (!fam) return null;
  for (const key of Object.keys(DATA.killXp)) { try { if (fam.hasTypeFamily(key)) return key; } catch { } }
  for (const key of Object.keys(DATA.killMorality)) { try { if (fam.hasTypeFamily(key)) return key; } catch { } }
  return null;
}

world.afterEvents.entityDie.subscribe((ev) => {
  const dead = ev.deadEntity;
  const src = ev.damageSource;
  let killer = src?.damagingEntity;
  if (killer?.typeId !== "minecraft:player" && src?.damagingProjectile) {
    // projectile owner not exposed pre-2.0; approximate via nearest player
    killer = nearestPlayer(dead.dimension, dead.location, 48);
  }
  if (dead.typeId === "minecraft:player") { P.set(dead, "fc_mult", 0); return; }
  if (killer?.typeId !== "minecraft:player") return;
  const p = killer;
  const fam = familyOf(dead);
  if (fam) {
    const xp = DATA.killXp[fam] ?? 5;
    const isRanged = !!src?.damagingProjectile;
    giveXp(p, "general", xp);
    giveXp(p, isRanged ? "skill" : "strength", Math.round(xp * 0.8));
    const mor = DATA.killMorality[fam] ?? 0;
    if (mor) addMorality(p, mor);
    if (mor <= -100) P.add(p, "fc_renown", 5); // infamy is still fame
    else P.add(p, "fc_renown", Math.max(1, Math.round(xp / 10)));
    // augment XP bonus
    const it = heldItem(p);
    if (it && weaponAugments(it).includes("experience")) giveXp(p, "general", Math.round(xp * 0.5));
    questKill(p, fam, dead.typeId);
    factionKillHooks(p, dead, fam);
    dropOrbs(dead.dimension, dead.location, src, fam);
  }
  if (dead.typeId === "fc:twinblade") {
    world.sendMessage("§6§l⚔ Twinblade has fallen. The camps whisper of a new power in Albion.");
  }
  // Jack of Blades: phase 2 — the Dragon
  if (dead.typeId === "fc:jack_of_blades") {
    world.sendMessage("§4§l✦ Jack of Blades falls... but his mask drinks the darkness!");
    const loc = dead.location, dim = dead.dimension;
    system.runTimeout(() => {
      dim.spawnParticle("minecraft:huge_explosion_emitter", loc);
      trySpawn(dim, "fc:jack_dragon", { x: loc.x, y: loc.y + 3, z: loc.z });
      world.sendMessage("§4§l✦ THE DRAGON OF BLADES RISES. End this, Hero!");
    }, 60);
  }
  if (dead.typeId === "fc:jack_dragon") {
    world.sendMessage("§6§l✦ The Dragon of Blades is destroyed. Albion is free.");
    system.runTimeout(() => offerAeonsChoice(p), 40);
  }
});

function nearestPlayer(dim, loc, range) {
  let best = null, bd = range * range;
  for (const pl of world.getPlayers()) {
    if (pl.dimension.id !== dim.id) continue;
    const dx = pl.location.x - loc.x, dz = pl.location.z - loc.z;
    const d = dx * dx + dz * dz;
    if (d < bd) { bd = d; best = pl; }
  }
  return best;
}

// The iconic choice: keep the Sword of Aeons, or cast it into the vortex.
function offerAeonsChoice(p) {
  const f = new MessageFormData()
    .title("§4The Sword of Aeons")
    .body("The blade hums in your hands, heavy with your bloodline's power.\n\n§cKeep it§r — and rule Albion through fear.\n§eDestroy it§r — and Avo's Tear shall answer your sacrifice.")
    .button1("§cKEEP THE SWORD")
    .button2("§eDESTROY IT");
  f.show(p).then((res) => {
    if (res.canceled) return;
    if (res.selection === 0) {
      addMorality(p, -500);
      P.add(p, "fc_renown", 500);
      addTitle(p, "Avatar of Aeons");
      p.sendMessage("§5The Sword feeds. Albion will learn to kneel.");
    } else {
      removeItem(p, "fc:sword_of_aeons", 1);
      giveItem(p, "fc:avos_tear", 1);
      addMorality(p, 500);
      P.add(p, "fc_renown", 500);
      addTitle(p, "Hero of Light");
      p.dimension.spawnParticle("minecraft:totem_particle", p.location);
      p.sendMessage("§eThe Sword shatters into dawn — Avo's Tear is yours.");
    }
  });
}

function addTitle(p, t) {
  const titles = P.getJ(p, "fc_titles", []);
  if (!titles.includes(t)) { titles.push(t); P.setJ(p, "fc_titles", titles); p.sendMessage(`§6✦ Title earned: §e${t}`); }
}

// ---------------------------------------------------------------------------
// Augments
// ---------------------------------------------------------------------------
const AUG_PREFIX = "§6⬩ ";
function weaponAugments(item) {
  return (item.getLore() ?? []).filter((l) => l.startsWith(AUG_PREFIX))
    .map((l) => l.substring(AUG_PREFIX.length).toLowerCase().split(" ")[0]);
}
// Visual and audio signature for each augment — used by the Augmentation Forge
// when binding a stone, and by the ambient weapon-aura on augmented gear.
const AUGMENT_FX = {
  sharpening: { glyph: "§c⚔", particle: "minecraft:critical_hit_emitter", sound: "random.anvil_use" },
  piercing: { glyph: "§7➳", particle: "minecraft:knockback_roar_particle", sound: "random.anvil_use" },
  health: { glyph: "§c❤", particle: "minecraft:heart_particle", sound: "random.levelup" },
  mana: { glyph: "§b✦", particle: "minecraft:enchanting_table_particle", sound: "random.levelup" },
  experience: { glyph: "§a✦", particle: "minecraft:totem_particle", sound: "random.levelup" },
  lightning: { glyph: "§9⚡", particle: "minecraft:knockback_roar_particle", sound: "beacon.activate" },
  flame: { glyph: "§6♦", particle: "minecraft:mobflame_single", sound: "fc.spell_cast" },
  silver: { glyph: "§f✶", particle: "minecraft:end_chest", sound: "random.orb" },
};
// Spawns a short flourish of particles + sound around the player to mark an
// augment binding to (or being stripped from) their weapon.
function forgeEffect(p, fx, strip = false) {
  try {
    const loc = { x: p.location.x, y: p.location.y + 1.4, z: p.location.z };
    p.dimension.spawnParticle(strip ? "minecraft:basic_smoke_particle" : "minecraft:totem_particle", loc);
    p.playSound(strip ? "random.break" : "random.anvil_use");
    const particle = fx?.particle;
    for (let i = 0; i < 6; i++) {
      system.runTimeout(() => {
        try {
          p.dimension.spawnParticle(particle ?? "minecraft:enchanting_table_particle", {
            x: loc.x + (Math.random() - 0.5) * 0.7,
            y: loc.y + (Math.random() - 0.5) * 0.5,
            z: loc.z + (Math.random() - 0.5) * 0.7,
          });
        } catch { }
      }, i * 3);
    }
    if (!strip && fx?.sound) system.runTimeout(() => { try { p.playSound(fx.sound, { pitch: 1.1 }); } catch { } }, 6);
  } catch { }
}
function applyAugmentHits(p, tgt, augs) {
  if (!augs.length) return;
  try {
    for (const a of augs) {
      if (a === "flame") tgt.setOnFire(4, true);
      else if (a === "lightning" && Math.random() < 0.3) {
        tgt.dimension.spawnParticle("minecraft:knockback_roar_particle", tgt.location);
        tgt.applyDamage(3, { cause: EntityDamageCause.lightning });
      } else if (a === "health") healPlayer(p, 1);
      else if (a === "mana") P.set(p, "fc_will", Math.min(maxWill(p), willEnergy(p) + 2));
      else if (a === "sharpening") tgt.applyDamage(2, { cause: EntityDamageCause.entityAttack });
      else if (a === "piercing") tgt.applyDamage(2, { cause: EntityDamageCause.override });
      else if (a === "silver") {
        const fam = tgt.getComponent("minecraft:type_family");
        if (fam?.hasTypeFamily("fc_supernatural")) {
          tgt.applyDamage(5, { cause: EntityDamageCause.magic });
          tgt.dimension.spawnParticle("minecraft:end_chest", tgt.location);
        }
      }
    }
  } catch { }
}
function healPlayer(p, n) {
  const hp = p.getComponent("minecraft:health");
  if (hp) hp.setCurrentValue(Math.min(hp.effectiveMax, hp.currentValue + n));
}

// ---------------------------------------------------------------------------
// Item use: Guild Seal, quest cards, spell tomes, augments
// ---------------------------------------------------------------------------
world.afterEvents.itemUse.subscribe((ev) => {
  const p = ev.source, it = ev.itemStack;
  if (!p || p.typeId !== "minecraft:player" || !it) return;
  const id = it.typeId;
  if (id === "fc:guild_seal") {
    if (p.isSneaking) return recallToGuild(p);
    return heroMenu(p);
  }
  if (id === "fc:quest_card") return questBoard(p);
  if (id.startsWith("fc:spell_")) return castSpell(p, id.substring("fc:spell_".length));
  if (ORB_XP[id]) {
    const [type, amt] = ORB_XP[id];
    removeItem(p, id, 1);
    giveXp(p, type, amt);
    p.playSound("random.orb", { pitch: 1.2 });
    try { p.dimension.spawnParticle("minecraft:villager_happy", { x: p.location.x, y: p.location.y + 1.6, z: p.location.z }); } catch { }
    p.onScreenDisplay.setActionBar(`${XP_COLOR[type]}✦ +${amt} ${type} experience absorbed`);
    return;
  }
  if (DATA.augments[id]) return applyAugment(p, it, DATA.augments[id]);
  if (id === "fc:augment_remover") return removeAugments(p);
  if (id === "fc:summoners_grimoire") return castSpell(p, "summon", true);
});

function recallToGuild(p) {
  const locS = world.getDynamicProperty("fc_guild_loc");
  if (!locS) return p.sendMessage("§7The Guild has not yet been founded.");
  const loc = JSON.parse(locS);
  p.dimension.spawnParticle("minecraft:large_explosion", p.location);
  p.teleport({ x: loc.x, y: loc.y + 1, z: loc.z });
  p.playSound("mob.endermen.portal");
  p.sendMessage("§9✦ The Guild Seal carries you home.");
}

// Opens the Augmentation Forge: lets the Hero choose which weapon in their
// pack should receive the stone, then binds it with a flourish of effects.
function applyAugment(p, item, augId) {
  const c = inv(p);
  if (!c) return;
  const info = DATA.augmentInfo?.[augId];
  const fx = AUGMENT_FX[augId];
  const candidates = [];
  for (let i = 0; i < c.size; i++) {
    const w = c.getItem(i);
    if (!w || !DATA.weapons[w.typeId]) continue;
    const slots = DATA.weapons[w.typeId].slots ?? 0;
    if (slots <= 0) continue;
    candidates.push({ slot: i, item: w, slots, current: weaponAugments(w) });
  }
  if (!candidates.length) {
    p.sendMessage("§7You carry no weapon with augment slots to bind this stone to.");
    return;
  }
  const f = new ActionFormData()
    .title(fableTitle("Augmentation Forge"))
    .body([
      FABLE_RULE,
      `${fx?.glyph ?? "§6⬩"} §l${info?.name ?? augId}§r`,
      `§7${info?.desc ?? ""}`,
      FABLE_RULE,
      "§7The forge-fire hums. Choose the weapon",
      "§7that will carry this power into battle.",
    ].join("\n"));
  for (const cand of candidates) {
    const name = cand.item.typeId.replace("fc:", "").split("_").map((w) => w[0].toUpperCase() + w.slice(1)).join(" ");
    const full = cand.current.length >= cand.slots;
    const dots = "§6⬩ ".repeat(cand.current.length) + "§8⬩ ".repeat(cand.slots - cand.current.length);
    f.button(`${full ? "§8" : "§e"}${name}\n${dots}§r §7(${cand.current.length}/${cand.slots})`,
      `textures/items/${cand.item.typeId.replace("fc:", "")}`);
  }
  f.button("§8❖ Leave the stone unbound");
  f.show(p).then((r) => {
    if (r.canceled || r.selection == null || r.selection >= candidates.length) return;
    const cand = candidates[r.selection];
    if (cand.current.length >= cand.slots) {
      p.sendMessage("§7That weapon's augment slots are already brimming with power.");
      return;
    }
    const w = cand.item;
    const lore = w.getLore() ?? [];
    lore.push(`${AUG_PREFIX}${augId.charAt(0).toUpperCase() + augId.slice(1)} Augmentation`);
    w.setLore(lore);
    c.setItem(cand.slot, w);
    removeItem(p, `fc:${augId}_augment`, 1);
    forgeEffect(p, fx);
    const wname = w.typeId.replace("fc:", "").replace(/_/g, " ");
    p.sendMessage([
      FABLE_RULE,
      `${fx?.glyph ?? "§6⬩"} §f${info?.name ?? augId} §7is bound to your §e${wname}§7.`,
      `§7(${cand.current.length + 1}/${cand.slots} augment slots filled)`,
      FABLE_RULE,
    ].join("\n"));
  });
}

// Opens a similar picker for the Augment Remover, then strips all bound
// augmentations from the chosen weapon with a fading-embers effect.
function removeAugments(p) {
  const c = inv(p);
  if (!c) return;
  const candidates = [];
  for (let i = 0; i < c.size; i++) {
    const w = c.getItem(i);
    if (!w || !DATA.weapons[w.typeId]) continue;
    const current = weaponAugments(w);
    if (!current.length) continue;
    candidates.push({ slot: i, item: w, current });
  }
  if (!candidates.length) {
    p.sendMessage("§7You carry no augmented weapon to strip.");
    return;
  }
  const f = new ActionFormData()
    .title(fableTitle("Augment Remover"))
    .body([
      FABLE_RULE,
      "§7Choose a weapon to strip of its augmentations.",
      "§c⚠ The augments are destroyed in the process.",
      FABLE_RULE,
    ].join("\n"));
  for (const cand of candidates) {
    const name = cand.item.typeId.replace("fc:", "").split("_").map((w) => w[0].toUpperCase() + w.slice(1)).join(" ");
    f.button(`§e${name}\n§6${"⬩ ".repeat(cand.current.length)}§r`, `textures/items/${cand.item.typeId.replace("fc:", "")}`);
  }
  f.button("§8❖ Cancel");
  f.show(p).then((r) => {
    if (r.canceled || r.selection == null || r.selection >= candidates.length) return;
    const cand = candidates[r.selection];
    const w = cand.item;
    w.setLore((w.getLore() ?? []).filter((l) => !l.startsWith(AUG_PREFIX)));
    c.setItem(cand.slot, w);
    removeItem(p, "fc:augment_remover", 1);
    forgeEffect(p, null, true);
    p.sendMessage(`${FABLE_RULE}\n§7The augmentations crumble from your §e${w.typeId.replace("fc:", "").replace(/_/g, " ")}§7 to ash.\n${FABLE_RULE}`);
  });
}

// ---------------------------------------------------------------------------
// Consumables
// ---------------------------------------------------------------------------
world.afterEvents.itemCompleteUse.subscribe((ev) => {
  const p = ev.source, it = ev.itemStack;
  if (!p || !it) return;
  const c = DATA.consumables[it.typeId];
  if (!c) return;
  if (c.heal) healPlayer(p, c.heal);
  if (c.will) P.set(p, "fc_will", Math.min(maxWill(p), willEnergy(p) + c.will));
  if (c.morality) addMorality(p, c.morality);
  if (c.xp) giveXp(p, c.xp, c.xp_amount);
  if (c.max_hp) {
    P.add(p, "fc_bonus_hp", c.max_hp);
    p.sendMessage("§d✦ Your life force expands permanently.");
  }
  if (it.typeId === "fc:health_potion" || it.typeId === "fc:great_health_potion") p.playSound("random.drink");
});

// ---------------------------------------------------------------------------
// WILL POWERS (spells)
// ---------------------------------------------------------------------------
const spellCd = new Map(); // playerId|spell -> tick

function spellLevel(p, id) { return Math.max(1, P.get(p, `fc_spell_lvl_${id}`, 1)); }

function castSpell(p, id, fromGrimoire = false) {
  const s = DATA.spells[id];
  if (!s) return;
  const m = morality(p);
  if (s.align > 0 && m < 100) return p.sendMessage("§7Your soul is not pure enough for this Will power.");
  if (s.align < 0 && m > -100) return p.sendMessage("§7Your soul is not dark enough for this Will power.");
  const key = `${p.id}|${id}`;
  const last = spellCd.get(key) ?? -99999;
  const lvl = spellLevel(p, id);
  const cd = Math.max(10, s.cd - lvl * 5);
  if (TICKS() - last < cd) {
    return p.onScreenDisplay.setActionBar("§b…the Will is still gathering…");
  }
  // good spells cost more for evil heroes and vice versa
  let cost = s.will;
  if (s.align > 0 && m < 0) cost = Math.round(cost * 1.5);
  if (s.align < 0 && m > 0) cost = Math.round(cost * 1.5);
  if (!spendWill(p, cost)) return p.onScreenDisplay.setActionBar("§9Not enough Will energy.");
  spellCd.set(key, TICKS());
  giveXp(p, "will", Math.round(cost * 0.6));
  p.playSound("fc.spell_cast", { pitch: 0.85 + lvl * 0.08 });
  playSpellAnim(p, id);
  castFlash(p, id);
  SPELL_FX[id]?.(p, lvl);
}

function foes(p, r) {
  return p.dimension.getEntities({ location: p.location, maxDistance: r, families: ["monster"] })
    .filter((e) => !(e.getComponent("minecraft:type_family")?.hasTypeFamily("fc_ally")));
}

// Which gestural animation (defined in fc_player_spells.animation.json) best
// fits each Will Power, so casting reads as a distinct motion per spell.
const SPELL_ANIM = {
  enflame: "animation.player.fc_cast_offense",
  fireball: "animation.player.fc_cast_offense",
  lightning: "animation.player.fc_cast_offense",
  force_push: "animation.player.fc_cast_offense",
  drain_life: "animation.player.fc_cast_offense",
  multi_arrow: "animation.player.fc_cast_offense",
  infernal_wrath: "animation.player.fc_cast_offense",
  divine_fury: "animation.player.fc_cast_defense",
  heal_life: "animation.player.fc_cast_defense",
  physical_shield: "animation.player.fc_cast_defense",
  slow_time: "animation.player.fc_cast_defense",
  turncoat: "animation.player.fc_cast_defense",
  summon: "animation.player.fc_cast_summon",
  multi_strike: "animation.player.fc_cast_melee",
  battle_charge: "animation.player.fc_cast_melee",
  berserk: "animation.player.fc_cast_melee",
  assassin_rush: "animation.player.fc_cast_melee",
};

function playSpellAnim(p, id) {
  const anim = SPELL_ANIM[id] ?? "animation.player.fc_cast_offense";
  try { p.playAnimation(anim, { blendOutTime: 0.2 }); } catch { }
}

// A short particle "muzzle flash" at the caster's hands, themed per spell,
// so every Will Power has an immediate visual tell the moment it's cast.
const SPELL_CAST_PARTICLE = {
  enflame: "minecraft:mobflame_single",
  fireball: "minecraft:mobflame_single",
  lightning: "minecraft:knockback_roar_particle",
  force_push: "minecraft:knockback_roar_particle",
  drain_life: "minecraft:soul_particle",
  heal_life: "minecraft:crop_growth_emitter",
  physical_shield: "minecraft:end_chest",
  slow_time: "minecraft:enchanting_table_particle",
  assassin_rush: "minecraft:dragon_breath_trail",
  summon: "minecraft:totem_particle",
  turncoat: "minecraft:heart_particle",
  multi_arrow: "minecraft:critical_hit_emitter",
  multi_strike: "minecraft:critical_hit_emitter",
  battle_charge: "minecraft:critical_hit_emitter",
  berserk: "minecraft:totem_particle",
  divine_fury: "minecraft:totem_particle",
  infernal_wrath: "minecraft:soul_particle",
};

function castFlash(p, id) {
  const particle = SPELL_CAST_PARTICLE[id] ?? "minecraft:enchanting_table_particle";
  const dir = p.getViewDirection();
  const loc = { x: p.location.x + dir.x * 0.7, y: p.location.y + 1.2, z: p.location.z + dir.z * 0.7 };
  for (let i = 0; i < 5; i++) {
    system.runTimeout(() => {
      try {
        p.dimension.spawnParticle(particle, {
          x: loc.x + (Math.random() - 0.5) * 0.4,
          y: loc.y + (Math.random() - 0.5) * 0.4,
          z: loc.z + (Math.random() - 0.5) * 0.4,
        });
      } catch { }
    }, i * 2);
  }
}

const SPELL_FX = {
  enflame(p, lvl) {
    const r = 3 + lvl;
    ringParticles(p.dimension, p.location, r, "minecraft:mobflame_single");
    for (const e of foes(p, r)) { try { e.setOnFire(3 + lvl, true); e.applyDamage(4 + lvl * 2, { cause: EntityDamageCause.fire }); } catch { } }
  },
  fireball(p, lvl) {
    const dim = p.dimension;
    const dir = p.getViewDirection();
    const loc = { x: p.location.x + dir.x * 1.5, y: p.location.y + 1.5 + dir.y, z: p.location.z + dir.z * 1.5 };
    const shots = lvl >= 3 ? 3 : 1;
    // Visual projectile(s) — vanilla small fireballs for the flame trail.
    for (let i = 0; i < shots; i++) {
      const fb = trySpawn(dim, "minecraft:small_fireball", loc);
      const proj = fb?.getComponent("minecraft:projectile");
      if (proj) { proj.owner = p; proj.shoot({ x: dir.x * 1.4 + (i - 1) * 0.12, y: dir.y * 1.4, z: dir.z * 1.4 + (i - 1) * 0.12 }); }
    }
    // Guaranteed hit-scan so the spell always lands, regardless of whether the
    // vanilla fireball entity actually collides with anything.
    const range = 14 + lvl * 2;
    const hits = p.getEntitiesFromViewDirection({ maxDistance: range });
    const hit = hits.find((h) => h.entity && h.entity.typeId !== "minecraft:player"
      && !h.entity.getComponent("minecraft:type_family")?.hasTypeFamily("fc_ally"));
    const impact = hit ? hit.entity.location
      : { x: p.location.x + dir.x * range, y: p.location.y + 1.5 + dir.y * range, z: p.location.z + dir.z * range };
    try { dim.spawnParticle("minecraft:large_explosion", impact); } catch { }
    try { dim.spawnParticle("minecraft:mobflame_single", impact); } catch { }
    try { p.playSound("mob.blaze.shoot", { location: impact, volume: 0.8, pitch: 0.9 }); } catch { }
    if (hit) {
      const e = hit.entity;
      try {
        e.applyDamage(7 + lvl * 3, { cause: EntityDamageCause.fire, damagingEntity: p });
        e.setOnFire(4 + lvl, true);
        const dx = e.location.x - p.location.x, dz = e.location.z - p.location.z;
        const len = Math.max(0.01, Math.hypot(dx, dz));
        e.applyKnockback(dx / len, dz / len, 1.2 + lvl * 0.3, 0.25);
      } catch { }
      // Splash damage to other foes caught near the impact point.
      for (const n of dim.getEntities({ location: impact, maxDistance: 3 + Math.floor(lvl / 2), families: ["monster"] })) {
        if (n.id === e.id || n.getComponent("minecraft:type_family")?.hasTypeFamily("fc_ally")) continue;
        try { n.applyDamage(4 + lvl * 2, { cause: EntityDamageCause.fire, damagingEntity: p }); n.setOnFire(3, true); } catch { }
      }
    } else {
      p.onScreenDisplay.setActionBar("§6The fireball scorches the ground ahead.");
    }
  },
  lightning(p, lvl) {
    const hits = p.getEntitiesFromViewDirection({ maxDistance: 18 });
    let struck = 0;
    for (const h of hits) {
      if (struck >= lvl + 1) break;
      const e = h.entity;
      if (!e || e.typeId === "minecraft:player") continue;
      try {
        trySpawn(p.dimension, "minecraft:lightning_bolt", e.location);
        e.applyDamage(6 + lvl * 2, { cause: EntityDamageCause.lightning });
        struck++;
        for (const n of foes(p, 14)) {
          if (struck > lvl + 1) break;
          if (n.id !== e.id) { n.applyDamage(4 + lvl, { cause: EntityDamageCause.lightning }); n.dimension.spawnParticle("minecraft:knockback_roar_particle", n.location); struck++; }
        }
      } catch { }
    }
    if (!struck) p.onScreenDisplay.setActionBar("§9The arc finds no target.");
  },
  force_push(p, lvl) {
    p.dimension.spawnParticle("minecraft:knockback_roar_particle", p.location);
    for (const e of foes(p, 4 + lvl)) {
      const dx = e.location.x - p.location.x, dz = e.location.z - p.location.z;
      const len = Math.max(0.01, Math.hypot(dx, dz));
      try { e.applyKnockback(dx / len, dz / len, 2 + lvl * 0.7, 0.45); e.applyDamage(2, { cause: EntityDamageCause.entityAttack }); } catch { }
    }
    p.playSound("mob.warden.sonic_boom", { volume: 0.4, pitch: 1.6 });
  },
  drain_life(p, lvl) {
    let drained = 0;
    for (const e of foes(p, 4 + lvl)) {
      try { e.applyDamage(3 + lvl, { cause: EntityDamageCause.magic }); e.dimension.spawnParticle("minecraft:soul_particle", e.location); drained++; } catch { }
    }
    if (drained) { healPlayer(p, drained * (2 + lvl)); addMorality(p, -5); }
  },
  heal_life(p, lvl) {
    healPlayer(p, 6 + lvl * 4);
    p.dimension.spawnParticle("minecraft:crop_growth_emitter", p.location);
  },
  physical_shield(p, lvl) {
    p.addEffect("resistance", (8 + lvl * 4) * 20, { amplifier: 1, showParticles: true });
    p.addEffect("absorption", (8 + lvl * 4) * 20, { amplifier: lvl - 1, showParticles: false });
    p.dimension.spawnParticle("minecraft:end_chest", p.location);
  },
  slow_time(p, lvl) {
    for (const e of foes(p, 10 + lvl * 2)) {
      try { e.addEffect("slowness", (4 + lvl * 2) * 20, { amplifier: 3, showParticles: true }); } catch { }
    }
    p.addEffect("speed", (4 + lvl * 2) * 20, { amplifier: 1, showParticles: false });
    p.playSound("mob.wither.spawn", { volume: 0.3, pitch: 1.8 });
  },
  assassin_rush(p, lvl) {
    const hits = p.getEntitiesFromViewDirection({ maxDistance: 10 + lvl * 3 });
    const tgt = hits.find((h) => h.entity && h.entity.typeId !== "minecraft:player")?.entity;
    if (!tgt) return p.onScreenDisplay.setActionBar("§9No target in sight.");
    const dir = p.getViewDirection();
    p.teleport({ x: tgt.location.x + dir.x * 1.2, y: tgt.location.y, z: tgt.location.z + dir.z * 1.2 }, { facingLocation: tgt.location });
    p.addEffect("strength", 60, { amplifier: lvl - 1, showParticles: false });
    p.dimension.spawnParticle("minecraft:dragon_breath_trail", p.location);
    p.playSound("mob.endermen.portal", { pitch: 1.5 });
  },
  summon(p, lvl) {
    if (morality(p) < 100) return p.sendMessage("§7Only good Heroes may bind creatures to their side.");
    const tier = Math.min(3, lvl);
    const type = tier === 1 ? "fc:summoned_wasp" : tier === 2 ? "fc:summoned_hobbe" : "fc:summoned_balverine";
    const e = trySpawn(p.dimension, type, { x: p.location.x + 1, y: p.location.y, z: p.location.z + 1 });
    if (e) { e.addTag(`fc_owner_${p.id}`); p.dimension.spawnParticle("minecraft:totem_particle", e.location); }
  },
  turncoat(p, lvl) {
    const hits = p.getEntitiesFromViewDirection({ maxDistance: 14 });
    const tgt = hits.find((h) => h.entity && h.entity.typeId !== "minecraft:player")?.entity;
    if (!tgt) return p.onScreenDisplay.setActionBar("§9No mind to bend.");
    try {
      tgt.addEffect("weakness", (6 + lvl * 3) * 20, { amplifier: 2, showParticles: true });
      tgt.dimension.spawnParticle("minecraft:heart_particle", { x: tgt.location.x, y: tgt.location.y + 2, z: tgt.location.z });
      for (const e of tgt.dimension.getEntities({ location: tgt.location, maxDistance: 8, families: ["monster"] })) {
        if (e.id !== tgt.id) e.applyDamage(3 + lvl * 2, { cause: EntityDamageCause.entityAttack });
      }
      p.sendMessage("§d✦ Their allies turn upon them in confusion.");
    } catch { }
  },
  multi_arrow(p, lvl) {
    const dir = p.getViewDirection();
    const n = 3 + lvl;
    for (let i = 0; i < n; i++) {
      const spread = (i - (n - 1) / 2) * 0.09;
      const ar = trySpawn(p.dimension, "minecraft:arrow",
        { x: p.location.x + dir.x, y: p.location.y + 1.5, z: p.location.z + dir.z });
      const proj = ar?.getComponent("minecraft:projectile");
      if (proj) { proj.owner = p; proj.shoot({ x: dir.x * 2 - dir.z * spread, y: dir.y * 2 + 0.08, z: dir.z * 2 + dir.x * spread }); }
    }
    p.playSound("random.bow", { pitch: 0.9 });
  },
  multi_strike(p, lvl) {
    p.addEffect("haste", (5 + lvl * 2) * 20, { amplifier: 2 + lvl, showParticles: false });
    p.addEffect("strength", (5 + lvl * 2) * 20, { amplifier: 0, showParticles: false });
    p.onScreenDisplay.setActionBar("§6Your blade blurs with impossible speed!");
  },
  battle_charge(p, lvl) {
    const dir = p.getViewDirection();
    try { p.applyKnockback(dir.x, dir.z, 3.5 + lvl, 0.25); } catch { }
    system.runTimeout(() => {
      p.dimension.spawnParticle("minecraft:large_explosion", p.location);
      for (const e of foes(p, 4)) {
        try { e.applyDamage(5 + lvl * 2, { cause: EntityDamageCause.entityAttack }); e.applyKnockback(e.location.x - p.location.x, e.location.z - p.location.z, 1.5, 0.4); } catch { }
      }
    }, 8);
  },
  berserk(p, lvl) {
    p.addEffect("strength", (10 + lvl * 4) * 20, { amplifier: 1, showParticles: true });
    p.addEffect("speed", (10 + lvl * 4) * 20, { amplifier: 1, showParticles: false });
    p.addEffect("resistance", (10 + lvl * 4) * 20, { amplifier: 0, showParticles: false });
    addMorality(p, -2);
    p.playSound("mob.ravager.roar", { pitch: 1.3 });
  },
  divine_fury(p, lvl) {
    p.dimension.spawnParticle("minecraft:totem_particle", p.location);
    for (const e of foes(p, 7 + lvl)) {
      try {
        const fam = e.getComponent("minecraft:type_family");
        const dmg = fam?.hasTypeFamily("fc_supernatural") ? 14 + lvl * 3 : 9 + lvl * 2;
        e.applyDamage(dmg, { cause: EntityDamageCause.magic });
        e.dimension.spawnParticle("minecraft:totem_particle", e.location);
      } catch { }
    }
    p.playSound("beacon.activate");
  },
  infernal_wrath(p, lvl) {
    p.dimension.spawnParticle("minecraft:huge_explosion_emitter", p.location);
    for (const e of foes(p, 7 + lvl)) {
      try {
        e.applyDamage(9 + lvl * 2, { cause: EntityDamageCause.magic });
        e.addEffect("wither", 80, { amplifier: 1, showParticles: true });
        e.dimension.spawnParticle("minecraft:soul_particle", e.location);
      } catch { }
    }
    addMorality(p, -5);
    p.playSound("mob.wither.shoot", { pitch: 0.7 });
  },
};

function ringParticles(dim, loc, r, particle) {
  for (let a = 0; a < 16; a++) {
    const ang = (a / 16) * Math.PI * 2;
    try { dim.spawnParticle(particle, { x: loc.x + Math.cos(ang) * r, y: loc.y + 0.4, z: loc.z + Math.sin(ang) * r }); } catch { }
  }
}

// ---------------------------------------------------------------------------
// HERO MENU (Guild Seal)
// ---------------------------------------------------------------------------
function heroMenu(p) {
  const aq = activeQuest(p);
  const q = aq ? DATA.quests.find((x) => x.id === aq.id) : null;
  const questLine = q
    ? `§e◈ Quest: §f${q.name} §8(${q.objectives.filter((o, i) => (o.type === "collect" ? countItem(p, o.item) : aq.progress[i]) >= o.count).length}/${q.objectives.length} objectives)`
    : "§7◈ No active quest — the Quest Table awaits in the Great Hall.";
  const f = new ActionFormData()
    .title(fableTitle("Hero of Albion"))
    .body([
      FABLE_RULE,
      `§7"${moralityTitle(p)}§7 — that is what they call you."`,
      questLine,
      `§8Renown §d${P.get(p, "fc_renown", 0)}  §8·  Gold §6${countItem(p, "fc:gold_coin")}`,
      `§b◈ Will: ${bar(willEnergy(p), maxWill(p), "§b", 14)} §f${willEnergy(p)}/${maxWill(p)}`,
      FABLE_RULE,
    ].join("\n"))
    .button("§2❖ Stats & Personality", "textures/items/guild_seal")
    .button("§e❖ Quest Log", "textures/items/quest_card")
    .button("§6❖ Weapon Locker", "textures/items/sharpening_augment")
    .button("§b❖ Map of Albion", "textures/items/septimal_key")
    .button("§c❖ Guild Training (Upgrades)", "textures/items/health_augment")
    .button("§9❖ Will Powers", "textures/items/spell_fireball")
    .button("§d❖ Titles & Renown", "textures/items/gold_coin")
    .button("§a❖ Factions & Standing", "textures/items/wedding_ring");
  f.show(p).then((r) => {
    if (r.canceled) return;
    [statsMenu, questMenu, weaponLockerMenu, mapMenu, trainMenu, spellMenu, titlesMenu, factionMenu][r.selection]?.(p);
  });
}

function weaponLockerMenu(p) {
  const held = heldItem(p);
  const lines = [FABLE_RULE];
  const wd = held && DATA.weapons[held.typeId];
  if (wd) {
    const name = held.typeId.replace("fc:", "").split("_").map((w) => w[0].toUpperCase() + w.slice(1)).join(" ");
    const augs = weaponAugments(held);
    lines.push(`§e◈ Wielding: §f${name}`);
    lines.push(`§7   Damage §c${wd.fable}§7 (Fable)`);
    if (wd.slots > 0) {
      lines.push(`§7   Augment slots: §f${augs.length}/${wd.slots}`);
      for (const a of augs) {
        const info = DATA.augmentInfo?.[a];
        lines.push(`   §6⬩ §f${info?.name ?? a} §8— §7${info?.desc ?? ""}`);
      }
      for (let i = augs.length; i < wd.slots; i++) lines.push("   §8⬩ (empty augment slot)");
    } else {
      lines.push("§7   This weapon has no augment slots.");
    }
  } else {
    lines.push("§7Hold a weapon to inspect it here.");
  }
  lines.push(FABLE_RULE);
  lines.push("§7Use an §6augmentation stone§7 from your pack to open the");
  lines.push("§7Augmentation Forge and bind new powers to a weapon.");
  new ActionFormData().title(fableTitle("Weapon Locker")).body(lines.join("\n")).button("§8❖ Back")
    .show(p).then((r) => { if (!r.canceled) heroMenu(p); });
}

function mapMenu(p) {
  const sites = JSON.parse(world.getDynamicProperty("fc_cullis") ?? "[]");
  if (!sites.length) {
    new ActionFormData().title(fableTitle("Map of Albion"))
      .body([
        FABLE_RULE,
        "§7No Focus Sites discovered yet.",
        "§7Cullis Gates scattered across Albion will join the lattice as you find them.",
        FABLE_RULE,
      ].join("\n"))
      .button("§8❖ Back")
      .show(p).then((r) => { if (!r.canceled) heroMenu(p); });
    return;
  }
  const f = new ActionFormData().title(fableTitle("Map of Albion"))
    .body(`${FABLE_RULE}\n§7The lattice of Albion bends to your Will.\n§7Choose a Focus Site to travel.\n${FABLE_RULE}`);
  for (const s of sites) {
    const d = Math.round(Math.hypot(p.location.x - s.x, p.location.z - s.z));
    f.button(`§b◈ ${s.name}\n§8${d}m distant`, "textures/items/septimal_key");
  }
  f.button("§8❖ Back");
  f.show(p).then((r) => {
    if (r.canceled) return;
    if (r.selection >= sites.length) return heroMenu(p);
    const s = sites[r.selection];
    try { p.dimension.spawnParticle("minecraft:huge_explosion_emitter", p.location); } catch { }
    p.playSound("fc.spell_cast", { pitch: 0.6 });
    p.teleport({ x: s.x + 0.5, y: s.y + 1, z: s.z + 0.5 });
    p.playSound("mob.endermen.portal");
    p.onScreenDisplay.setTitle("§b◈", { fadeInDuration: 2, stayDuration: 16, fadeOutDuration: 8, subtitle: `§f${s.name}` });
  });
}

function bar(v, max, color, width = 20) {
  const fill = Math.max(0, Math.min(width, Math.round((v / max) * width)));
  return color + "█".repeat(fill) + "§8" + "░".repeat(width - fill);
}

function statsMenu(p) {
  const m = morality(p);
  const morBar = (() => {
    const pos = Math.round(((m + 1000) / 2000) * 20);
    let s = "§5";
    for (let i = 0; i < 21; i++) s += i === pos ? "§f┃" : (i < 10 ? "§5▒" : "§e▒");
    return s;
  })();
  const lines = [
    FABLE_RULE,
    `${FABLE_DOT}§lAlignment§r  ${moralityTitle(p)} §7(${m})`,
    morBar,
    FABLE_RULE,
    `§a ◈ General XP: §f${P.get(p, "fc_xp_general", 0)}`,
    `§c ◈ Strength XP: §f${P.get(p, "fc_xp_strength", 0)}`,
    `§9 ◈ Skill XP: §f${P.get(p, "fc_xp_skill", 0)}`,
    `§e ◈ Will XP: §f${P.get(p, "fc_xp_will", 0)}`,
    "",
    `§b ◈ Will Energy: ${bar(willEnergy(p), maxWill(p), "§b")} §f${willEnergy(p)}/${maxWill(p)}`,
    `§6 ◈ Combat Multiplier: §f${P.get(p, "fc_mult", 0)}`,
    `§d ◈ Renown: §f${P.get(p, "fc_renown", 0)}`,
    FABLE_RULE,
    "§7Guild disciplines:",
    ...Object.values(DATA.upgrades).map((u) => `  §f${u.name}: §6${"◆".repeat(P.get(p, `fc_up_${u.id}`, 0))}§8${"◇".repeat(u.max - P.get(p, `fc_up_${u.id}`, 0))}`),
  ];
  new ActionFormData().title(fableTitle("Stats · Personality")).body(lines.join("\n")).button("§8❖ Back")
    .show(p).then((r) => { if (!r.canceled) heroMenu(p); });
}

function factionMenu(p) {
  const rows = Object.entries(FACTION_NAMES).map(([f, name]) => {
    const v = rep(p, f);
    const tier = repTier(v);
    const col = { hostile: "§4", wary: "§c", neutral: "§7", friendly: "§a", revered: "§6" }[tier];
    return ` ${col}◈ ${name}: ${tier.toUpperCase()} §8(${v})`;
  });
  const body = [
    FABLE_RULE,
    "§7Albion keeps score. Guards, traders and barkeeps",
    "§7all treat you by your standing.",
    FABLE_RULE,
    ...rows,
    "",
    "§8Defend towns and finish quests to rise.",
    "§8Murder and banditry are... remembered.",
  ].join("\n");
  new ActionFormData().title(fableTitle("Factions")).body(body).button("§8❖ Back")
    .show(p).then((r) => { if (!r.canceled) heroMenu(p); });
}

function trainMenu(p) {
  const guild = world.getDynamicProperty("fc_guild_loc");
  if (guild) {
    const g = JSON.parse(guild);
    const t = world.getDynamicProperty("fc_guild_train");
    const tr = t ? JSON.parse(t) : g;
    const d = Math.min(
      Math.hypot(p.location.x - g.x, p.location.z - g.z),
      Math.hypot(p.location.x - tr.x, p.location.z - tr.z));
    if (d > 46) return p.sendMessage("§7Training happens at the Guild — stand at the §aSkill Altar§7 to the right of the Map Room. (Sneak+use the Seal to recall.)");
  }
  const f = new ActionFormData().title(fableTitle("Guild Training"));
  const ups = Object.values(DATA.upgrades);
  for (const u of ups) {
    const lvl = P.get(p, `fc_up_${u.id}`, 0);
    const cost = (lvl + 1) * 120;
    const xpKey = XP_KEYS[u.xp];
    const have = P.get(p, xpKey, 0);
    f.button(`${XP_COLOR[u.xp]}❖ ${u.name} §8[${lvl}/${u.max}]\n§7${cost} ${u.xp} XP ${have >= cost ? "§a✔" : "§c✘"}`);
  }
  f.button("§8❖ Back");
  f.show(p).then((r) => {
    if (r.canceled) return;
    if (r.selection >= ups.length) return heroMenu(p);
    const u = ups[r.selection];
    const lvl = P.get(p, `fc_up_${u.id}`, 0);
    if (lvl >= u.max) { p.sendMessage("§7You have mastered this discipline."); return trainMenu(p); }
    const cost = (lvl + 1) * 120;
    const xpKey = XP_KEYS[u.xp];
    if (P.get(p, xpKey, 0) < cost) { p.sendMessage(`§7Not enough ${u.xp} experience.`); return trainMenu(p); }
    P.add(p, xpKey, -cost);
    P.add(p, `fc_up_${u.id}`, 1);
    applyUpgrades(p);
    p.playSound("fc.level_up");
    p.dimension.spawnParticle("minecraft:totem_particle", p.location);
    p.sendMessage(`§6✦ ${u.name} increased to ${lvl + 1}! §7${u.desc}`);
    trainMenu(p);
  });
}

function applyUpgrades(p) {
  // persistent effect-based morphing
  const phys = P.get(p, "fc_up_physique", 0);
  const tough = P.get(p, "fc_up_toughness", 0);
  const speed = P.get(p, "fc_up_speed", 0);
  const health = P.get(p, "fc_up_health", 0);
  if (phys) p.addEffect("strength", 21 * 20, { amplifier: Math.ceil(phys / 2) - 1, showParticles: false });
  if (tough) p.addEffect("resistance", 21 * 20, { amplifier: Math.ceil(tough / 3) - 1, showParticles: false });
  if (speed) p.addEffect("speed", 21 * 20, { amplifier: Math.ceil(speed / 3) - 1, showParticles: false });
  const bonus = health * 4 + P.get(p, "fc_bonus_hp", 0);
  if (bonus) p.addEffect("health_boost", 21 * 20, { amplifier: Math.min(5, Math.ceil(bonus / 4) - 1), showParticles: false });
}

function spellMenu(p) {
  const f = new ActionFormData().title(fableTitle("Will Powers"));
  const ids = Object.keys(DATA.spells);
  for (const id of ids) {
    const s = DATA.spells[id];
    const lvl = spellLevel(p, id);
    const owned = countItem(p, `fc:spell_${id}`) > 0;
    const alignTag = s.align > 0 ? " §e[Good]" : s.align < 0 ? " §5[Evil]" : "";
    f.button(`${owned ? "§b❖ " : "§8❖ "}${s.name}${alignTag} §7Lv${lvl}\n§8${s.will} Will · upgrade: ${lvl * 150} Will XP`);
  }
  f.button("§b⚡ Attune Quick-Cast Slots", "textures/items/spell_fireball");
  f.button("§8❖ Back");
  f.show(p).then((r) => {
    if (r.canceled) return;
    if (r.selection === ids.length) return willAttuneMenu(p);
    if (r.selection > ids.length) return heroMenu(p);
    const id = ids[r.selection];
    const lvl = spellLevel(p, id);
    if (lvl >= 4) { p.sendMessage("§7This Will power is already mastered."); return spellMenu(p); }
    const cost = lvl * 150;
    if (P.get(p, "fc_xp_will", 0) < cost) { p.sendMessage(`§7You need ${cost} Will XP to deepen this power.`); return spellMenu(p); }
    P.add(p, "fc_xp_will", -cost);
    P.set(p, `fc_spell_lvl_${id}`, lvl + 1);
    p.playSound("fc.level_up", { pitch: 1.3 });
    p.sendMessage(`§9✦ ${DATA.spells[id].name} flows stronger (level ${lvl + 1}).`);
    spellMenu(p);
  });
}

// ---------------------------------------------------------------------------
// WILL QUICK-CAST BAR — once a Hero unlocks Will, their three attuned powers
// live in the three rightmost hotbar slots (6/7/8 → keys 7/8/9, the right edge
// of the screen). Selecting a slot and using it casts. Bedrock cannot bind
// custom hotkeys, so the hotbar IS the quick bar; it is sortable from the
// attunement menu and by dragging in the inventory.
// ---------------------------------------------------------------------------
function willOwnedSpells(p) {
  return Object.keys(DATA.spells).filter((id) => countItem(p, `fc:spell_${id}`) > 0);
}
function applyWillLabel(st, p, id) {
  const s = DATA.spells[id];
  if (!s) return;
  try {
    st.nameTag = `§b❖ ${s.name} §7Lv${spellLevel(p, id)}`;
    st.setLore([`§9Will cost: §f${s.will}`, "§8Quick-cast — select this slot and use"]);
  } catch { }
}
// Explicit placement (attune / init): put exactly one tome in the target slot,
// stripping stray copies and rehoming whatever was displaced.
function forceAttune(p, target, id) {
  const c = inv(p); if (!c) return;
  const tomeId = `fc:spell_${id}`;
  const displaced = c.getItem(target);
  for (let j = 0; j < c.size; j++) { const it = c.getItem(j); if (it?.typeId === tomeId) c.setItem(j, undefined); }
  const st = new ItemStack(tomeId, 1);
  applyWillLabel(st, p, id);
  c.setItem(target, st);
  if (displaced && displaced.typeId !== tomeId) { try { c.addItem(displaced); } catch { } }
}
// Gentle upkeep: only fills an EMPTY bar slot when the power tome is wholly
// missing (death/relog), so it never clobbers the player's own arrangement.
function maintainWillSlot(p, c, target, id) {
  if (!id) return;
  const tomeId = `fc:spell_${id}`;
  const cur = c.getItem(target);
  if (cur) return;                          // already in place / busy — leave it
  if (countItem(p, tomeId) > 0) return;     // owned elsewhere — respect arrangement
  const st = new ItemStack(tomeId, 1);
  applyWillLabel(st, p, id);
  c.setItem(target, st);
}
function gatherWillBar(p) {
  if (!P.get(p, "fc_will_bar", 1)) { p.sendMessage("§7Enable the Quick-Cast Bar first."); return; }
  const slots = P.getJ(p, "fc_will_slots", [null, null, null]);
  for (let i = 0; i < 3; i++) if (slots[i]) forceAttune(p, 6 + i, slots[i]);
  p.sendMessage("§9❖ Will powers gathered to slots §f7 · 8 · 9§9.");
}

const willGreeted = new Set();
system.runInterval(() => {
  for (const p of world.getPlayers()) {
    let slots = P.getJ(p, "fc_will_slots", null);
    if (slots === null) {
      const owned = willOwnedSpells(p);
      if (!owned.length) continue;          // Will not unlocked yet
      slots = [owned[0] ?? null, owned[1] ?? null, owned[2] ?? null];
      P.setJ(p, "fc_will_slots", slots);
      if (P.get(p, "fc_will_bar", -1) === -1) P.set(p, "fc_will_bar", 1);
      for (let i = 0; i < 3; i++) if (slots[i]) forceAttune(p, 6 + i, slots[i]);
      if (!willGreeted.has(p.id)) {
        willGreeted.add(p.id);
        p.sendMessage("§9❖ Will unlocked — your powers are bound to the three rightmost hotbar slots (keys §f7 · 8 · 9§9). Select one and use it to cast. Re-bind them via Guild Seal → Will Powers → Attune.");
        p.playSound("fc.level_up", { pitch: 1.1 });
      }
      continue;
    }
    if (!P.get(p, "fc_will_bar", 1)) continue;
    const c = inv(p); if (!c) continue;
    for (let i = 0; i < 3; i++) maintainWillSlot(p, c, 6 + i, slots[i]);
  }
}, 40);

function willAttuneMenu(p) {
  const slots = P.getJ(p, "fc_will_slots", [null, null, null]);
  const on = P.get(p, "fc_will_bar", 1);
  const f = new ActionFormData().title(fableTitle("Attune Quick-Cast"))
    .body(`${FABLE_RULE}\n§7Bind up to three Will powers to the rightmost hotbar\n§7slots — keys §f7 · 8 · 9§7. Select a slot to change it.\n§7Quick-Cast Bar: ${on ? "§aON" : "§cOFF"}\n${FABLE_RULE}`);
  for (let i = 0; i < 3; i++) {
    const id = slots[i];
    const name = id ? (DATA.spells[id]?.name ?? id) : "§8(empty)";
    f.button(`§bSlot ${i + 1} §7(key ${7 + i})\n§f${name}`, "textures/items/spell_fireball");
  }
  f.button(on ? "§e⏼ Disable Quick-Cast Bar" : "§a⏼ Enable Quick-Cast Bar");
  f.button("§b⇅ Gather powers to bar");
  f.button("§8❖ Back");
  f.show(p).then((r) => {
    if (r.canceled) return;
    if (r.selection < 3) return willSlotPicker(p, r.selection);
    if (r.selection === 3) { P.set(p, "fc_will_bar", on ? 0 : 1); return willAttuneMenu(p); }
    if (r.selection === 4) { gatherWillBar(p); return willAttuneMenu(p); }
    return spellMenu(p);
  });
}

function willSlotPicker(p, slotIdx) {
  const owned = willOwnedSpells(p);
  const f = new ActionFormData().title(fableTitle(`Slot ${slotIdx + 1}`))
    .body(`${FABLE_RULE}\n§7Choose the Will power for key §f${7 + slotIdx}§7.\n${FABLE_RULE}`);
  for (const id of owned) f.button(`§b❖ ${DATA.spells[id].name}\n§8${DATA.spells[id].will} Will`);
  f.button("§7✖ Clear slot");
  f.button("§8❖ Back");
  f.show(p).then((r) => {
    if (r.canceled) return willAttuneMenu(p);
    const slots = P.getJ(p, "fc_will_slots", [null, null, null]);
    if (r.selection < owned.length) {
      const id = owned[r.selection];
      for (let k = 0; k < 3; k++) if (slots[k] === id) slots[k] = null;  // de-dupe
      slots[slotIdx] = id;
      P.setJ(p, "fc_will_slots", slots);
      if (P.get(p, "fc_will_bar", 1)) forceAttune(p, 6 + slotIdx, id);
    } else if (r.selection === owned.length) {
      const c = inv(p);
      if (c) {
        const cur = c.getItem(6 + slotIdx);
        if (cur?.typeId.startsWith("fc:spell_")) { c.setItem(6 + slotIdx, undefined); try { c.addItem(cur); } catch { } }
      }
      slots[slotIdx] = null;
      P.setJ(p, "fc_will_slots", slots);
    }
    willAttuneMenu(p);
  });
}

function activeTitle(p) { return P.getJ(p, "fc_active_title", ""); }
function applyTitleTag(p) {
  try { const t = activeTitle(p); p.nameTag = t ? `§e${t}\n§f${p.name}` : p.name; } catch { }
}
// How an NPC addresses the Hero — by their worn title if they have one.
function heroAddress(p) { return activeTitle(p) || "Hero"; }

// Every Hero starts with the two earliest Guild titles already unlocked.
function ensureBaseTitles(p) {
  const titles = P.getJ(p, "fc_titles", []);
  let changed = false;
  for (const t of ["Sparrow", "Apprentice"]) if (!titles.includes(t)) { titles.push(t); changed = true; }
  if (changed) P.setJ(p, "fc_titles", titles);
}

function titlesMenu(p) {
  ensureBaseTitles(p);
  const titles = P.getJ(p, "fc_titles", []);
  const active = activeTitle(p);
  const f = new ActionFormData().title(fableTitle("Titles & Renown")).body([
    FABLE_RULE,
    `§dRenown: §f${P.get(p, "fc_renown", 0)}`,
    `§7Now wearing: §e${active || "(none)"}`,
    FABLE_RULE,
    titles.length ? "§6Choose the title you wear — Albion will address you by it:"
      : "§7No titles yet. Earn renown and deeds to claim them.",
  ].join("\n"));
  f.button("§8✦ Wear no title");
  for (const t of titles) f.button((t === active ? "§a● " : "§e✦ ") + t);
  f.button("§8❖ Back");
  f.show(p).then((r) => {
    if (r.canceled) return;
    if (r.selection === 0) { P.setJ(p, "fc_active_title", ""); applyTitleTag(p); p.sendMessage("§7You wear no title."); return; }
    if (r.selection === titles.length + 1) { heroMenu(p); return; }
    const t = titles[r.selection - 1];
    P.setJ(p, "fc_active_title", t); applyTitleTag(p);
    p.sendMessage(`§6✦ You will be known as §e${t}§6 across Albion.`);
  });
}

// ---------------------------------------------------------------------------
// QUESTS
// ---------------------------------------------------------------------------
function activeQuest(p) { return P.getJ(p, "fc_quest", null); }
function doneQuests(p) { return P.getJ(p, "fc_quests_done", []); }

function questBoard(p) {
  const done = doneQuests(p);
  const aq = activeQuest(p);
  if (aq) return questMenu(p);
  const avail = DATA.quests.filter((q) => {
    if (done.includes(q.id)) return false;
    if (q.chain === "main") {
      const prior = DATA.quests.filter((o) => o.chain === "main" && o.order < q.order);
      return prior.every((o) => done.includes(o.id));
    }
    return true;
  });
  if (!avail.length) return p.sendMessage("§7No quest cards remain. Albion sleeps soundly... for now.");
  const f = new ActionFormData().title(fableTitle("Quest Cards"))
    .body(`${FABLE_RULE}\n§7Choose a contract, Hero. Renown and gold await.\n${FABLE_RULE}`);
  for (const q of avail) {
    const tag = q.chain === "main" ? "§6[MAIN]" : q.chain === "side" ? "§a[SIDE]" : "§b[JOB]";
    f.button(`${tag} §f${q.name}\n§7${q.giver} · ${q.renown} renown`, "textures/items/quest_card");
  }
  f.show(p).then((r) => {
    if (r.canceled) return;
    const q = avail[r.selection];
    new MessageFormData().title(`§e${q.name}`)
      .body(`§o"${q.desc}"§r\n\n§7Objectives:\n${q.objectives.map((o) => " §f• " + o.label).join("\n")}\n\n§7Rewards: §6${q.rewards.gold} gold§7${q.rewards.items.length ? ", items" : ""}, XP`)
      .button1("§aACCEPT").button2("§8Later")
      .show(p).then((res) => {
        if (res.canceled || res.selection !== 0) return;
        P.setJ(p, "fc_quest", { id: q.id, progress: q.objectives.map(() => 0) });
        p.playSound("random.orb");
        p.sendMessage(`§e✦ Quest accepted: ${q.name}`);
        if (q.id === "join_guild") placeGuildNear(p);
      });
  });
}

function questMenu(p) {
  const aq = activeQuest(p);
  if (!aq) return questBoard(p);
  const q = DATA.quests.find((x) => x.id === aq.id);
  if (!q) { P.set(p, "fc_quest", undefined); return; }
  const lines = q.objectives.map((o, i) => {
    let cur = aq.progress[i];
    if (o.type === "collect") cur = countItem(p, o.item);
    const doneMark = cur >= o.count ? "§a✔" : "§7";
    return ` ${doneMark} ${o.label} §8(${Math.min(cur, o.count)}/${o.count})`;
  });
  const complete = q.objectives.every((o, i) => (o.type === "collect" ? countItem(p, o.item) : aq.progress[i]) >= o.count);
  const f = new ActionFormData().title(`§e${q.name}`)
    .body(`§o"${q.desc}"§r\n\n${lines.join("\n")}`)
    .button(complete ? "§a§lTURN IN" : "§8(objectives incomplete)")
    .button("§cAbandon quest");
  f.show(p).then((r) => {
    if (r.canceled) return;
    if (r.selection === 0 && complete) return completeQuest(p, q);
    if (r.selection === 1) {
      P.set(p, "fc_quest", undefined);
      p.sendMessage("§7The quest card crumbles. The Guild will not be impressed.");
    }
  });
}

function completeQuest(p, q) {
  for (const o of q.objectives) if (o.type === "collect") removeItem(p, o.item, o.count);
  const rw = q.rewards;
  if (rw.gold) giveItem(p, "fc:gold_coin", Math.min(64, Math.max(1, Math.round(rw.gold / 100))));
  for (const it of rw.items ?? []) giveItem(p, it.id, it.count);
  for (const [t, amt] of Object.entries(rw.xp ?? {})) giveXp(p, t, amt);
  if (rw.morality) addMorality(p, rw.morality);
  P.add(p, "fc_renown", q.renown);
  if (rw.title) addTitle(p, rw.title);
  const done = doneQuests(p); done.push(q.id); P.setJ(p, "fc_quests_done", done);
  P.set(p, "fc_quest", undefined);
  addRep(p, "guild", Math.max(2, Math.round(q.renown / 50)));
  p.playSound("fc.level_up");
  p.dimension.spawnParticle("minecraft:totem_particle", p.location);
  p.onScreenDisplay.setTitle("§6Quest Complete", { fadeInDuration: 5, stayDuration: 50, fadeOutDuration: 15, subtitle: `§e${q.name}` });
  // chain spawns
  if (q.id === "wasp_menace") spawnQuestBoss(p, "fc:wasp_queen", "§4The Wasp Queen descends!");
  if (q.next) p.sendMessage(`§7A new quest card waits in the Map Room: §e${DATA.quests.find((x) => x.id === q.next)?.name ?? q.next}`);
}

function spawnQuestBoss(p, type, msg) { /* bosses spawn on quest ACCEPT for kill quests instead */ }

function questKill(p, fam, typeId) {
  const aq = activeQuest(p);
  if (!aq) return;
  const q = DATA.quests.find((x) => x.id === aq.id);
  if (!q) return;
  let changed = false;
  q.objectives.forEach((o, i) => {
    if (o.type !== "kill" || aq.progress[i] >= o.count) return;
    if (o.family === fam || `fc:${o.family.replace("fc_", "")}` === typeId || o.family === typeId) {
      aq.progress[i]++;
      changed = true;
      p.onScreenDisplay.setActionBar(`§e${o.label}: §f${aq.progress[i]}/${o.count}`);
    }
  });
  if (changed) P.setJ(p, "fc_quest", aq);
}

// Boss-need spawner: if player has a kill objective for a boss family with no
// candidates nearby, conjure it close by (dramatically).
system.runInterval(() => {
  for (const p of world.getPlayers()) {
    const aq = activeQuest(p);
    if (!aq) continue;
    const q = DATA.quests.find((x) => x.id === aq.id);
    if (!q) continue;
    q.objectives.forEach((o, i) => {
      if (o.type !== "kill" || aq.progress[i] >= o.count) return;
      const bossMap = {
        fc_wasp_queen: "fc:wasp_queen", fc_white_balverine: "fc:white_balverine",
        fc_jack: "fc:jack_of_blades", fc_jack_dragon: "fc:jack_dragon",
        fc_troll: "fc:earth_troll", fc_banshee: "fc:banshee",
        fc_twinblade: "fc:twinblade",
      };
      const type = bossMap[o.family];
      if (!type) return;
      const near = p.dimension.getEntities({ location: p.location, maxDistance: 64, type });
      if (near.length) return;
      if (Math.random() < 0.25) {
        const ang = Math.random() * Math.PI * 2;
        const loc = { x: p.location.x + Math.cos(ang) * 18, y: p.location.y + 1, z: p.location.z + Math.sin(ang) * 18 };
        const e = trySpawn(p.dimension, type, loc);
        if (e) {
          p.playSound("mob.wither.spawn", { volume: 0.6 });
          p.sendMessage(`§4✦ ${e.typeId === "fc:jack_of_blades" ? "Jack of Blades steps from the shadows." : "Your quarry has found YOU."}`);
        }
      }
    });
  }
}, 200);

// ---------------------------------------------------------------------------
// DEMON DOORS + NPC dialogue
// ---------------------------------------------------------------------------
world.beforeEvents.playerInteractWithEntity.subscribe((ev) => {
  const t = ev.target?.typeId ?? "";
  if (!t.startsWith("fc:")) return;
  const p = ev.player, target = ev.target;
  if (t === "fc:demon_door") { ev.cancel = true; system.run(() => demonDoorTalk(p, target)); return; }
  const NPC_TYPES = ["fc:guildmaster", "fc:maze", "fc:theresa", "fc:lady_grey", "fc:oracle",
    "fc:briar_rose", "fc:trader", "fc:barkeep", "fc:villager_albion", "fc:villager_woman",
    "fc:villager_farmer", "fc:villager_tailor", "fc:villager_blacksmith", "fc:villager_fisher",
    "fc:guild_apprentice_might", "fc:guild_apprentice_skill", "fc:guild_apprentice_will", "fc:mercenary",
    "fc:guard_bowerstone", "fc:guard_oakvale", "fc:guard_snowspire"];
  if (NPC_TYPES.includes(t)) {
    ev.cancel = true;
    system.run(() => {
      // a one-shot wave the moment the Hero is greeted (humanoid NPCs only; the
      // call is a harmless no-op on plans without the clip, e.g. the Oracle)
      try { target.playAnimation("animation.fc.biped.greet", { blendOutTime: 0.4 }); } catch { }
      try { target.lookAt?.(p.getHeadLocation()); } catch { }
      npcTalk(p, target);
    });
  }
});

// the Quest Table lectern in the Heroes' Guild great hall opens the quest board
world.beforeEvents.playerInteractWithBlock.subscribe((ev) => {
  if (ev.block?.typeId !== "minecraft:lectern") return;
  const raw = world.getDynamicProperty("fc_guild_quest_table");
  if (!raw) return;
  const loc = JSON.parse(raw);
  const b = ev.block.location;
  if (b.x !== loc.x || b.y !== loc.y || b.z !== loc.z) return;
  ev.cancel = true;
  const p = ev.player;
  system.run(() => questBoard(p));
});

function doorPersona(door) {
  let idx = door.getDynamicProperty("fc_door_idx");
  if (idx === undefined) {
    idx = Math.abs(Math.floor(door.location.x * 31 + door.location.z * 17)) % DATA.demonDoors.length;
    door.setDynamicProperty("fc_door_idx", idx);
  }
  return DATA.demonDoors[idx];
}

// Summon the living Demon-Door face at an arch if one isn't already there, and
// turn it to face the approach. Idempotent: re-running is a no-op while the
// door exists, but it re-spawns one that failed to spawn (chunk timing) or was
// somehow lost — so a carved arch never reads as a blank wall.
function ensureDemonDoor(dim, loc, facingZ) {
  let present;
  try {
    present = dim.getEntities({ location: loc, maxDistance: 4, type: "fc:demon_door" }).length > 0;
  } catch { return; }   // chunk not ready — the sweep will retry
  if (present) return;
  const door = trySpawn(dim, "fc:demon_door", loc);
  if (!door) return;
  try { door.teleport(loc, { facingLocation: { x: loc.x, y: loc.y + 1, z: facingZ } }); } catch { }
  try { doorPersona(door); } catch { }
}

// Remember every standalone Demon-Door arch we render so the periodic sweep can
// keep its face present even if the first spawn missed or the chunk reloaded.
function recordDemonDoor(loc, faceZ) {
  let arr;
  try { arr = JSON.parse(world.getDynamicProperty("fc_doors") ?? "[]"); } catch { arr = []; }
  arr.push({ x: loc.x, y: loc.y, z: loc.z, f: faceZ });
  if (arr.length > 64) arr = arr.slice(-64);
  world.setDynamicProperty("fc_doors", JSON.stringify(arr));
}

function ensureAllDemonDoors(dim) {
  const doors = [];
  const g = world.getDynamicProperty("fc_guild_door");
  if (g) { try { const d = JSON.parse(g); doors.push({ x: d.x, y: d.y, z: d.z, f: d.z - 14 }); } catch { } }
  try { for (const d of JSON.parse(world.getDynamicProperty("fc_doors") ?? "[]")) doors.push(d); } catch { }
  const players = world.getPlayers();
  for (const d of doors) {
    const near = players.some((p) => p.dimension.id === dim.id
      && Math.hypot(p.location.x - d.x, p.location.z - d.z) < 80);
    if (near) ensureDemonDoor(dim, { x: d.x, y: d.y, z: d.z }, d.f);
  }
}

function demonDoorTalk(p, door) {
  const d = doorPersona(door);
  p.playSound("fc.door_speak", { volume: 0.9 });
  if (door.getDynamicProperty("fc_door_open")) {
    p.sendMessage(`§8${d.name}: §7"I have given all I guard. Leave an old door to its naps."`);
    return;
  }
  const req = d.requirement;
  if (req.type === "riddle") return doorRiddle(p, door, d);
  const f = new MessageFormData()
    .title(`§5${d.name}`)
    .body(`§o"${d.greeting}"§r\n\n§7${req.hint}`)
    .button1("§aAnswer the Door")
    .button2("§8Step away");
  f.show(p).then((r) => {
    if (r.canceled || r.selection !== 0) return;
    let ok = false, consume = null;
    const m = morality(p);
    switch (req.type) {
      case "items": ok = countItem(p, req.item) >= req.count; consume = ok ? [req.item, req.count] : null; break;
      case "multiplier": ok = P.get(p, "fc_mult", 0) >= req.count; break;
      case "night_multiplier": {
        const t = world.getTimeOfDay();
        ok = (t > 13000 && t < 23000) && P.get(p, "fc_mult", 0) >= req.count; break;
      }
      case "morality_min": ok = m >= req.count; break;
      case "morality_max": ok = m <= req.count; break;
      case "renown": ok = P.get(p, "fc_renown", 0) >= req.count; break;
    }
    if (!ok) {
      p.sendMessage(`§5${d.name}: §c"${d.fail}"`);
      p.playSound("mob.villager.no", { pitch: 0.5 });
      door.dimension.spawnParticle("minecraft:basic_smoke_particle", door.location);
      return;
    }
    if (consume) removeItem(p, consume[0], consume[1]);
    openDemonDoor(p, door, d);
  });
}

function doorRiddle(p, door, d) {
  const req = d.requirement;
  const f = new ActionFormData().title(`§5${d.name}`).body(`§o"${d.greeting}"§r\n\n§e${req.riddle}`);
  for (const a of req.answers) f.button(a);
  f.show(p).then((r) => {
    if (r.canceled) return;
    if (r.selection === req.correct) return openDemonDoor(p, door, d);
    p.sendMessage(`§5${d.name}: §c"${d.fail}"`);
    p.playSound("mob.villager.no", { pitch: 0.5 });
  });
}

function openDemonDoor(p, door, d) {
  door.setDynamicProperty("fc_door_open", true);
  try { door.triggerEvent("fc:open"); } catch { }
  p.sendMessage(`§5${d.name}: §a"${d.success}"`);
  const dim = door.dimension, loc = door.location;
  dim.spawnParticle("minecraft:huge_explosion_emitter", loc);
  p.playSound("fc.door_rumble", { volume: 0.9 });
  animateDoorOpening(door);
  for (const it of d.reward.items) giveItem(p, it.id, it.count);
  giveXp(p, "general", d.reward.xp);
  addRep(p, "guild", 5);
  addTitle(p, "Door-Speaker");
  p.onScreenDisplay.setTitle("§5Demon Door Opened", { fadeInDuration: 8, stayDuration: 60, fadeOutDuration: 15, subtitle: `§7${d.name}` });
}

function animateDoorOpening(door) {
  const base = { ...door.location };
  const steps = 18;
  for (let i = 0; i <= steps; i++) {
    system.runTimeout(() => {
      try {
        const t = i / steps;
        const zOff = 1.45 * t;
        const yOff = Math.sin(t * Math.PI) * 0.14;
        door.teleport({ x: base.x, y: base.y + yOff, z: base.z + zOff });
        door.dimension.spawnParticle("minecraft:basic_smoke_particle",
          { x: base.x + (Math.random() - 0.5) * 1.4, y: base.y + 1.1 + Math.random() * 1.2, z: base.z + 0.2 + zOff });
        if (i % 3 === 0) {
          door.dimension.spawnParticle("minecraft:soul_particle",
            { x: base.x + (Math.random() - 0.5) * 1.2, y: base.y + 1.3, z: base.z + zOff });
        }
        if (i % 4 === 0) {
          for (const pl of world.getPlayers({ location: door.location, maxDistance: 22 })) {
            pl.playSound("fc.door_rumble", { volume: 0.25, pitch: 0.7 + Math.random() * 0.2 });
          }
        }
      } catch { }
    }, i * 2);
  }
}

// ---------------------------------------------------------------------------
// NPCs
// ---------------------------------------------------------------------------
const SHOP_STOCK = [
  { id: "fc:health_potion", cost: 2, label: "Health Potion" },
  { id: "fc:will_potion", cost: 2, label: "Will Potion" },
  { id: "fc:great_health_potion", cost: 8, label: "Great Health Potion" },
  { id: "fc:steel_ingot", cost: 3, label: "Steel Ingot" },
  { id: "fc:will_shard", cost: 6, label: "Will Shard" },
  { id: "fc:obsidian_ingot", cost: 10, label: "Obsidian Ingot" },
  { id: "fc:steel_longsword", cost: 12, label: "Steel Longsword" },
  { id: "fc:steel_greatsword", cost: 16, label: "Steel Greatsword" },
  { id: "fc:yew_longbow", cost: 8, label: "Yew Longbow" },
  { id: "fc:chainmail_bright_torso", cost: 20, label: "Bright Chainmail Torso" },
  { id: "fc:leather_dark_torso", cost: 10, label: "Dark Leather Torso" },
  { id: "fc:sharpening_augment", cost: 25, label: "Sharpening Augmentation" },
  { id: "fc:flame_augment", cost: 30, label: "Flame Augmentation" },
  { id: "fc:wedding_ring", cost: 15, label: "Wedding Ring" },
  { id: "fc:apple_pie", cost: 1, label: "Apple Pie" },
];
const SELL_PRICES = {
  "fc:balverine_fang": 1, "fc:wasp_wing": 1, "fc:beetle_chitin": 1,
  "fc:troll_heart": 6, "fc:troll_bones": 1, "fc:ectoplasm": 2,
  "fc:banshees_tear": 8, "fc:frost_balverine_hide": 4, "fc:minion_flesh": 1,
  "fc:queens_stinger": 15, "fc:scorpion_stinger": 25, "fc:giants_core": 30,
};

function npcTalk(p, npc) {
  const t = npc.typeId;
  const m = morality(p);
  if (t === "fc:guildmaster") {
    const guildLn = guildRepLine(p);
    const you = heroAddress(p);
    new ActionFormData().title("§6The Guildmaster")
      .body(`§o"${m > 200 ? `Albion sings of your kindness, ${you}.` : m < -200 ? `I hear dark whispers about you, ${you}. Tread carefully.` : `Your training continues, ${you}.`}\n\nA Hero balances Strength, Skill and Will. Use Quest Cards to earn your renown. And do stop hitting the practice dummies with your forehead."§r${guildLn ? `\n\n§o"${guildLn}"§r` : ""}`)
      .button("§eTake a Quest Card", "textures/items/quest_card")
      .button("§9Hero Menu")
      .button("§8Farewell")
      .show(p).then((r) => {
        if (r.canceled) return;
        if (r.selection === 0) { giveItem(p, "fc:quest_card", 1); p.sendMessage("§e✦ Quest Card received."); }
        if (r.selection === 1) heroMenu(p);
      });
  } else if (t === "fc:maze") {
    const guildLn = guildRepLine(p);
    new MessageFormData().title("§5Maze")
      .body([
        '§o"The Will is a muscle, Hero. Spell tomes hide in ruins and Demon Door hoards — each one a power your enemies will learn to dread. Visit the Oracle in the far snows, when you are ready for truths."§r',
        guildLn ? `\n§7"${guildLn}"` : "",
      ].join(""))
      .button1("§9Receive a Lightning tome").button2("§8Leave")
      .show(p).then((r) => {
        if (!r.canceled && r.selection === 0 && !P.get(p, "fc_maze_gift", false)) {
          P.set(p, "fc_maze_gift", true);
          giveItem(p, "fc:spell_lightning", 1);
          giveItem(p, "fc:spell_fireball", 1);
          p.sendMessage("§9✦ Maze presses two humming tomes into your hands.");
        } else if (!r.canceled && r.selection === 0) {
          p.sendMessage('§5Maze: "I am a Hero, not a lending library."');
        }
      });
  } else if (t === "fc:theresa") {
    const renownLn = renownLine(p);
    new ActionFormData().title("§dTheresa")
      .body([
        `§o"${m >= 0 ? "I see many paths for you, and most are bright." : "Blood follows you like a stray dog, brother."} The blind see further than you'd think."§r`,
        renownLn ? `\n§7"${renownLn}"` : "",
      ].join(""))
      .button("§dAsk about your fate")
      .button("§5Ask about Jack of Blades")
      .button("§8Leave")
      .show(p).then((r) => {
        if (r.canceled) return;
        if (r.selection === 0) {
          p.sendMessage(`§dTheresa: §o"${m > 200 ? "Light follows you, Hero. Do not let it blind you to its cost." : m < -200 ? "Your shadow grows long. It will swallow you, in the end." : "Your path forks soon. Choose with your heart, not your purse."}"`);
        } else if (r.selection === 1) {
          p.sendMessage('§dTheresa: §o"He wears a mask of swords and calls it a face. When he comes, the Sword of Aeons will sing. What you do with it after is yours to choose — Albion remembers either way."');
        }
      });
  } else if (t === "fc:lady_grey") {
    const married = P.get(p, "fc_married", false);
    if (married) { p.sendMessage('§dLady Grey: §o"My consort. Bowerstone bores me — slay something interesting."'); return; }
    const hasRing = countItem(p, "fc:wedding_ring") > 0;
    const done = doneQuests(p).includes("lady_greys_invitation");
    new MessageFormData().title("§dLady Grey, Mayor of Bowerstone")
      .body(done && hasRing
        ? '§o"A ring? For me? You do move quickly, Hero. Very well — I accept. Try not to die embarrassingly."'
        : '§o"Charmed. Complete my little... invitation, and bring a ring, and we shall discuss matrimony and property."')
      .button1(done && hasRing ? "§dMarry her" : "§7Bow politely").button2("§8Leave")
      .show(p).then((r) => {
        if (r.canceled || r.selection !== 0) return;
        if (done && hasRing) {
          removeItem(p, "fc:wedding_ring", 1);
          P.set(p, "fc_married", true);
          addMorality(p, 200);
          addTitle(p, "Consort of Bowerstone");
          p.playSound("random.levelup");
        } else p.sendMessage('§dLady Grey: §o"Manners! How refreshing."');
      });
  } else if (t === "fc:oracle") {
    new ActionFormData().title("§bThe Oracle of Snowspire")
      .body('§o"WE REMEMBER ALL. THE MASK RETURNS. THE BLOODLINE ENDURES. ASK, LITTLE EMBER."')
      .button("§bProphecy").button("§eRiddle me a reward").button("§8Depart")
      .show(p).then((r) => {
        if (r.canceled) return;
        if (r.selection === 0) p.sendMessage('§bOracle: §o"When the red mask burns, hold fast to what your mother gave you: stubbornness."');
        if (r.selection === 1) {
          if (!P.get(p, "fc_oracle_gift", false)) {
            P.set(p, "fc_oracle_gift", true);
            giveItem(p, "fc:ages_of_will_potion", 1);
            p.sendMessage("§b✦ The Oracle exhales a phial of liquid memory.");
          } else p.sendMessage('§bOracle: §o"GREED IS A SECOND MOUTH. FEED IT ELSEWHERE."');
        }
      });
  } else if (t === "fc:briar_rose") {
    const renownLn = renownLine(p);
    new ActionFormData().title("§cBriar Rose")
      .body([
        '§o"Done staring? The hills hide more than flowers, Hero."§r',
        renownLn ? `\n§7"${renownLn}"` : "",
      ].join(""))
      .button("§cAsk about Demon Doors")
      .button("§dAsk about the roses")
      .button("§8Leave")
      .show(p).then((r) => {
        if (r.canceled) return;
        if (r.selection === 0) {
          p.sendMessage('§cBriar Rose: §o"Demon Doors respond to deeds, not poetry. Multiplier 14 opens the Warrior\'s arch — if you can keep your footing."');
        } else if (r.selection === 1) {
          p.sendMessage('§cBriar Rose: §o"Every thorn here grew from a broken promise. Mind you don\'t leave one of your own behind."');
        }
      });
  } else if (t === "fc:trader") {
    shopMenu(p, "§6Travelling Trader");
  } else if (t === "fc:barkeep") {
    new ActionFormData().title("§6Barkeep")
      .body('§o"Welcome to the Cock in the Crown! Ale, pie, and only mild fistfights."')
      .button("§6Hobbe Tooth Ale — 1 gold").button("§6Apple Pie — 1 gold").button("§7Any rumours?").button("§8Leave")
      .show(p).then((r) => {
        if (r.canceled) return;
        if (r.selection === 0 && removeItem(p, "fc:gold_coin", 1)) giveItem(p, "fc:golden_carrot_brew", 1);
        else if (r.selection === 1 && removeItem(p, "fc:gold_coin", 1)) giveItem(p, "fc:apple_pie", 1);
        else if (r.selection === 2) {
          const rumours = [
            "They say a White Balverine prowls Knothole way. Silver, friend. Silver.",
            "Lady Grey never did find her sister. Don't ask her about it.",
            "A door in the hills demanded my pies. My PIES.",
            "Snow folk swear the Oracle speaks in three voices at once.",
            "Bandits pay gold for Guild seals. Don't sell yours. Probably.",
          ];
          p.sendMessage(`§6Barkeep: §o"${rumours[Math.floor(Math.random() * rumours.length)]}"`);
        } else if (r.selection <= 1) p.sendMessage("§7Your purse is empty, friend.");
      });
  } else if (t === "fc:mercenary") {
    const guildLn = guildRepLine(p);
    new MessageFormData().title("§7Mercenary")
      .body([
        '§o"Twenty gold and my blade walks with you. I don\'t do funerals — especially mine."§r',
        guildLn ? `\n§7"${guildLn}"` : "",
      ].join(""))
      .button1("§6Hire (20 gold)").button2("§8Not today")
      .show(p).then((r) => {
        if (r.canceled || r.selection !== 0) return;
        if (removeItem(p, "fc:gold_coin", 20)) {
          npc.addTag(`fc_hired_${p.id}`);
          p.sendMessage('§7Mercenary: "Point me at something with teeth."');
        } else p.sendMessage("§7Mercenary: \"Twenty. Gold. Coins. Counting is free, Hero.\"");
      });
  } else if (t.startsWith("fc:guard_")) {
    const town = GUARD_TOWN[t];
    const v = rep(p, town);
    const tier = repTier(v);
    if (tier === "hostile") p.sendMessage("§cGuard: \"YOU! Don't move— GUARDS! GUARDS!\"");
    else if (tier === "wary" || m <= -200) p.sendMessage('§cGuard: "I\'ve got my eye on you, scoundrel."');
    else if (tier === "revered") p.sendMessage(`§6Guard: "§o${FACTION_NAMES[town]} sleeps easy with you about, Hero. An honour.§r§6"`);
    else if (tier === "friendly") p.sendMessage(`§9Guard: "Good to see a friend of ${FACTION_NAMES[town]}. Mind the Hobbes after dark."`);
    else p.sendMessage('§9Guard: "All quiet, Hero. Mind the Hobbes after dark."');
  } else if (t === "fc:guild_apprentice_might" || t === "fc:guild_apprentice_skill" || t === "fc:guild_apprentice_will") {
    const lines = t.endsWith("might") ? ["The Guildmaster says footwork wins duels. My bruises agree.", "One day I'll take Twinblade's measure myself."]
      : t.endsWith("skill") ? ["Maze says patience is an arrow loosed before the bow is drawn.", "I can hit the yard post nine times out of ten now."]
        : ["The Will hums louder near the Cullis Gate.", "I saw blue fire in my sleep. Theresa said not to panic."];
    p.sendMessage(`§6Guild Apprentice: §f"${lines[Math.floor(Math.random() * lines.length)]}"`);
    const renownLn = renownLine(p);
    if (renownLn) p.sendMessage(`§6Guild Apprentice: §f"${renownLn}"`);
  } else if (t === "fc:villager_albion" || t === "fc:villager_woman" || t === "fc:villager_farmer" || t === "fc:villager_tailor" || t === "fc:villager_blacksmith" || t === "fc:villager_fisher") {
    const town = VILLAGER_TOWN[t] ?? "bowerstone";
    const tier = repTier(rep(p, town));
    const att = P.get(p, "fc_renown", 0);
    const lines = tier === "hostile" || m < -300 ? ["P-please don't hurt me.", "*backs away slowly*", "I saw nothing. NOTHING."]
      : tier === "revered" || m > 300 ? ["Bless you, Hero!", "It's really you! The kind one!", "My chickens adore you. As do we all."]
        : att > 500 ? ["You're that Hero from the songs!", "Sign my pitchfork?"]
          : ["Lovely weather, if the wasps don't carry you off.", "Buy a pie, they said. Adventure, they said.", "Have you seen my cousin? Tall, screams at beetles?"];
    new ActionFormData().title(fableTitle("Villager"))
      .body(`§f§o"${lines[Math.floor(Math.random() * lines.length)]}"§r\n\n§8Standing with ${FACTION_NAMES[town]}: ${repTier(rep(p, town))}`)
      .button("§6❖ Give 1 gold (charity)")
      .button("§7❖ Ask for rumours")
      .button("§8❖ Leave")
      .show(p).then((r) => {
        if (r.canceled || r.selection === 2) return;
        if (r.selection === 0) {
          if (removeItem(p, "fc:gold_coin", 1)) {
            addRep(p, town, 2);
            addMorality(p, 3);
            p.playSound("random.orb");
            p.sendMessage('§fVillager: §o"Avo bless you, kind one!"');
          } else p.sendMessage("§7Your purse is empty.");
        } else {
          const rum = [
            "Twinblade's lot camp behind a palisade of whole trees. Cowards.",
            "They say azurite veins glow blue in the deep dark. Will made stone.",
            "The Cullis Gates hum when a storm is coming. Or a Hero.",
            "Hollow Men wear whatever armour they died in. Some died rich.",
          ];
          p.sendMessage(`§fVillager: §o"${rum[Math.floor(Math.random() * rum.length)]}"`);
        }
      });
  }
}

function shopMenu(p, title) {
  const tier = repTier(townAvgRep(p));
  if (tier === "hostile") {
    p.sendMessage('§cTrader: "I don\'t serve YOUR kind. Out, before I call the guards."');
    return;
  }
  const mult = { wary: 1.15, neutral: 1.0, friendly: 0.9, revered: 0.8 }[tier] ?? 1.0;
  const tierNote = { wary: "§c(wary — prices up 15%)", neutral: "", friendly: "§a(friendly — 10% off)", revered: "§6(revered — 20% off)" }[tier] ?? "";
  const f = new ActionFormData().title(fableTitle(title.replace(/§./g, "")))
    .body(`${FABLE_RULE}\n§7Your gold: §6${countItem(p, "fc:gold_coin")} coins ${tierNote}\n${FABLE_RULE}`)
    .button("§a❖ BUY").button("§e❖ SELL trophies").button("§d✦ BUY a Title").button("§8❖ Leave");
  f.show(p).then((r) => {
    if (r.canceled || r.selection === 3) return;
    if (r.selection === 2) { traderTitleMenu(p, title); return; }
    if (r.selection === 0) {
      const b = new ActionFormData().title(fableTitle("Buy"));
      const priced = SHOP_STOCK.map((s) => ({ ...s, cost: Math.max(1, Math.round(s.cost * mult)) }));
      for (const s of priced) b.button(`§f${s.label}\n§6${s.cost} gold`, `textures/items/${s.id.replace("fc:", "")}`);
      b.show(p).then((res) => {
        if (res.canceled) return;
        const s = priced[res.selection];
        if (removeItem(p, "fc:gold_coin", s.cost)) {
          giveItem(p, s.id, 1);
          p.playSound("mob.villager.yes");
        } else p.sendMessage("§7Trader: \"Coin first, hero second.\"");
        shopMenu(p, title);
      });
    } else {
      let sold = 0;
      for (const [id, price] of Object.entries(SELL_PRICES)) {
        const n = countItem(p, id);
        if (n > 0) { removeItem(p, id, n); sold += n * price; }
      }
      if (sold > 0) {
        sold = tier === "friendly" || tier === "revered" ? Math.round(sold * 1.1) : sold;
        giveItem(p, "fc:gold_coin", Math.min(64, sold));
        p.playSound("random.orb");
        p.sendMessage(`§6Sold your trophies for ${sold} gold.`);
      } else p.sendMessage("§7Nothing in your pack interests the trader.");
      shopMenu(p, title);
    }
  });
}

// The trader also peddles vanity TITLES for gold — wear one and boast it.
const TRADER_TITLES = [
  { t: "Wanderer", cost: 8 }, { t: "Sellsword", cost: 16 }, { t: "Gilded", cost: 32 },
];
function traderTitleMenu(p, shopTitle) {
  const owned = P.getJ(p, "fc_titles", []);
  const b = new ActionFormData().title(fableTitle("Titles for Sale")).body(
    `${FABLE_RULE}\n§7Your gold: §6${countItem(p, "fc:gold_coin")}\n` +
    "§7§oA title bought is a title earned… more or less.§r\n" + FABLE_RULE);
  for (const s of TRADER_TITLES) {
    b.button(owned.includes(s.t) ? `§a● ${s.t} §7(owned)` : `§e✦ ${s.t}\n§6${s.cost} gold`);
  }
  b.button("§8❖ Back");
  b.show(p).then((res) => {
    if (res.canceled) return;
    if (res.selection === TRADER_TITLES.length) { shopMenu(p, shopTitle); return; }
    const s = TRADER_TITLES[res.selection];
    if (owned.includes(s.t)) { p.sendMessage('§7Trader: "You already wear that one, friend."'); shopMenu(p, shopTitle); return; }
    if (removeItem(p, "fc:gold_coin", s.cost)) {
      addTitle(p, s.t);
      p.playSound("random.orb");
      p.sendMessage(`§6Trader: "A pleasure — you're a §e${s.t}§6 now. Go boast it on the platform!"`);
    } else p.sendMessage('§7Trader: "No coin, no title."');
    shopMenu(p, shopTitle);
  });
}

// ---------------------------------------------------------------------------
// CULLIS GATES — Fable's fast-travel network (Guild gate + Focus Sites)
// ---------------------------------------------------------------------------
function registerCullis(name, loc) {
  const sites = JSON.parse(world.getDynamicProperty("fc_cullis") ?? "[]");
  if (sites.some((s) => s.name === name)) return;
  sites.push({ name, x: Math.floor(loc.x), y: Math.floor(loc.y), z: Math.floor(loc.z) });
  world.setDynamicProperty("fc_cullis", JSON.stringify(sites));
}

const cullisCd = new Map();
const cullisDwell = new Map();      // `${playerId}|${siteName}` -> dwell intervals
let cullisPhase = 0;

// The "special cullis gate configuration": a beacon / sea-lantern core ringed
// by chiseled stone or obsidian. A gate our structures actually build qualifies
// as a portal; a bare registered travel-point does not (it keeps sneak-travel).
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

system.runInterval(() => {
  cullisPhase++;
  const sites = JSON.parse(world.getDynamicProperty("fc_cullis") ?? "[]");
  const dim = OW();
  const players = world.getPlayers();

  // animate only the gates close to a player (keeps particle work bounded)
  for (const s of sites) {
    const seen = players.some((p) => Math.hypot(p.location.x - s.x, p.location.z - s.z) < 48
      && Math.abs(p.location.y - s.y) < 24);
    if (!seen) continue;
    const cx = s.x + 0.5, cz = s.z + 0.5;
    // a rising double-helix of enchant glyphs that spirals up out of the ring
    for (let i = 0; i < 8; i++) {
      const ang = (cullisPhase * 0.22) + (Math.PI * 2 * i) / 8;
      const rad = 1.7 + 0.5 * Math.sin(cullisPhase * 0.09 + i);
      const y = s.y + 0.5 + ((cullisPhase * 0.13 + i * 0.4) % 2.8);
      try { dim.spawnParticle("minecraft:enchanting_table_particle", { x: cx + Math.cos(ang) * rad, y, z: cz + Math.sin(ang) * rad }); } catch { }
    }
    // a bright rising column of soul-fire at the core
    for (let j = 0; j < 5; j++) {
      const y = s.y + 0.3 + ((cullisPhase * 0.3 + j * 0.6) % 3.4);
      try {
        dim.spawnParticle("minecraft:soul_particle",
          { x: cx + (Math.random() - 0.5) * 0.4, y, z: cz + (Math.random() - 0.5) * 0.4 });
      } catch { }
    }
    if (cullisPhase % 5 === 0) {                   // periodic arcane flares
      try { dim.spawnParticle("minecraft:end_chest", { x: cx, y: s.y + 1.3, z: cz }); } catch { }
      try { dim.spawnParticle("minecraft:dragon_breath_trail", { x: cx, y: s.y + 0.7, z: cz }); } catch { }
    }
  }

  // Demon Doors breathe and whisper in the hills.
  for (const door of dim.getEntities({ type: "fc:demon_door" })) {
    const o = door.location;
    try {
      dim.spawnParticle("minecraft:basic_smoke_particle",
        { x: o.x + (Math.random() - 0.5) * 0.9, y: o.y + 1.2 + Math.random() * 0.9, z: o.z + 0.3 });
      if (cullisPhase % 4 === 0) {
        dim.spawnParticle("minecraft:soul_particle", { x: o.x, y: o.y + 1.4, z: o.z + 0.2 });
      }
    } catch { }
  }

  for (const p of players) {
    const near = sites.find((s) => Math.hypot(p.location.x - s.x, p.location.z - s.z) < 3.0
      && Math.abs(p.location.y - s.y) < 4);
    if (!near) {                                  // drop any stale dwell charge
      for (const k of [...cullisDwell.keys()]) if (k.startsWith(p.id + "|")) cullisDwell.delete(k);
      continue;
    }
    const dwellKey = `${p.id}|${near.name}`;
    if (isCullisConfigured(dim, near)) {
      // PORTAL: stand in the central blue light for ~3s to be carried away
      const inCentre = Math.hypot(p.location.x - (near.x + 0.5), p.location.z - (near.z + 0.5)) < 1.3;
      if (!inCentre) {
        cullisDwell.delete(dwellKey);
        p.onScreenDisplay.setActionBar("§b◈ Cullis Gate §7— step into the light to travel");
        continue;
      }
      const NEED = 3;                             // intervals of 20t ≈ 3 seconds
      const d = (cullisDwell.get(dwellKey) ?? 0) + 1;
      cullisDwell.set(dwellKey, d);
      if (d < NEED) {
        try {
          for (let k = 0; k < 10; k++) {
            const ang = Math.random() * Math.PI * 2;
            dim.spawnParticle("minecraft:soul_particle",
              { x: near.x + 0.5 + Math.cos(ang) * 0.8, y: near.y + 0.4 + Math.random() * 2.0, z: near.z + 0.5 + Math.sin(ang) * 0.8 });
          }
        } catch { }
        p.playSound("note.bell", { pitch: 0.6 + 0.3 * d });
        p.onScreenDisplay.setActionBar(`§b◈ The Gate awakens… §f${"▮".repeat(d)}§8${"▯".repeat(NEED - d)}`);
        continue;
      }
      const last = cullisCd.get(p.id) ?? -9999;
      if (TICKS() - last < 80) continue;
      cullisCd.set(p.id, TICKS());
      cullisDwell.delete(dwellKey);
      try { dim.spawnParticle("minecraft:huge_explosion_emitter", { x: near.x + 0.5, y: near.y + 1, z: near.z + 0.5 }); } catch { }
      cullisTravel(p, sites, near);
    } else {
      // bare travel-point — keep the sneak-to-travel fallback
      if (!p.isSneaking) {
        p.onScreenDisplay.setActionBar("§b◈ Cullis Gate §7— sneak to focus your Will and travel");
        continue;
      }
      const last = cullisCd.get(p.id) ?? -9999;
      if (TICKS() - last < 80) continue;
      cullisCd.set(p.id, TICKS());
      cullisTravel(p, sites, near);
    }
  }
}, 20);

// The Skill Altar / Experience Shrine (right of the Map Room): like the Cullis
// Gate, stand in its green light for ~3 seconds and the Shrine drinks your
// deeds and opens Guild Training. (Still reachable from the Guild Seal menu.)
const skillAltarCd = new Map();
const skillDwell = new Map();
let skillPhase = 0;
system.runInterval(() => {
  skillPhase++;
  const raw = world.getDynamicProperty("fc_guild_skill");
  if (!raw) return;
  let s; try { s = JSON.parse(raw); } catch { return; }
  const dim = OW();
  const cx = s.x + 0.5, cz = s.z + 0.5;
  const players = world.getPlayers();
  // green arcane swirl when a Hero is near (the Cullis Gate's twin, in green)
  if (players.some((p) => Math.hypot(p.location.x - cx, p.location.z - cz) < 40 && Math.abs(p.location.y - s.y) < 16)) {
    for (let i = 0; i < 7; i++) {
      const ang = (skillPhase * 0.2) + (Math.PI * 2 * i) / 7;
      const rad = 1.5 + 0.4 * Math.sin(skillPhase * 0.11 + i);
      const y = s.y + 0.5 + ((skillPhase * 0.13 + i * 0.4) % 2.6);
      try { dim.spawnParticle("minecraft:villager_happy", { x: cx + Math.cos(ang) * rad, y, z: cz + Math.sin(ang) * rad }); } catch { }
    }
    for (let j = 0; j < 3; j++) {
      const y = s.y + 0.3 + ((skillPhase * 0.28 + j * 0.7) % 3.0);
      try { dim.spawnParticle("minecraft:villager_happy", { x: cx + (Math.random() - 0.5) * 0.4, y, z: cz + (Math.random() - 0.5) * 0.4 }); } catch { }
    }
  }
  for (const p of players) {
    const dist = Math.hypot(p.location.x - cx, p.location.z - cz);
    if (dist > 2.8 || Math.abs(p.location.y - s.y) > 3) { skillDwell.delete(p.id); continue; }
    if (dist > 1.4) {                              // near but not centred
      skillDwell.delete(p.id);
      p.onScreenDisplay.setActionBar("§a✦ Experience Shrine §7— step into the green light to train");
      continue;
    }
    const NEED = 3;                                // intervals of 20t ≈ 3 seconds
    const d = (skillDwell.get(p.id) ?? 0) + 1;
    skillDwell.set(p.id, d);
    if (d < NEED) {
      try {
        for (let k = 0; k < 12; k++) {
          const ang = Math.random() * Math.PI * 2;
          dim.spawnParticle("minecraft:villager_happy",
            { x: cx + Math.cos(ang) * 0.7, y: s.y + 0.4 + Math.random() * 2.0, z: cz + Math.sin(ang) * 0.7 });
        }
      } catch { }
      p.playSound("note.bell", { pitch: 1.0 + 0.3 * d });
      p.onScreenDisplay.setActionBar(`§a✦ The Shrine drinks your deeds… §f${"▮".repeat(d)}§8${"▯".repeat(NEED - d)}`);
      continue;
    }
    const last = skillAltarCd.get(p.id) ?? -9999;
    if (TICKS() - last < 80) continue;
    skillAltarCd.set(p.id, TICKS());
    skillDwell.delete(p.id);
    try { dim.spawnParticle("minecraft:totem_particle", { x: cx, y: s.y + 1, z: cz }); } catch { }
    try { p.playSound("random.levelup", { pitch: 1.2 }); } catch { }
    trainMenu(p);
  }
}, 20);

// The Boasting Platform (NW of the gate): step onto the raised stage and, over
// five seconds, the crowd gathers — how many turn out depends on your Renown —
// then you declare the Title you wear. Albion's folk address you by it after.
const boastDwell = new Map();
const boastCrowded = new Set();
system.runInterval(() => {
  const raw = world.getDynamicProperty("fc_guild_base");
  if (!raw) return;
  let base; try { base = JSON.parse(raw); } catch { return; }
  const bx = base.x + 4, by = base.y + 3, bz = base.z + 26;     // raised stage deck centre
  const dim = OW();
  for (const p of world.getPlayers()) {
    const on = Math.abs(p.location.x - bx) <= 3 && Math.abs(p.location.z - bz) <= 3.5
      && Math.abs(p.location.y - by) <= 2;
    if (!on) { boastDwell.delete(p.id); boastCrowded.delete(p.id); continue; }
    try { dim.spawnParticle("minecraft:villager_happy", { x: bx + (Math.random() - 0.5) * 3, y: by + 1.2, z: bz + (Math.random() - 0.5) * 3 }); } catch { }
    const d = (boastDwell.get(p.id) ?? 0) + 1;
    boastDwell.set(p.id, d);
    if (d === 2 && !boastCrowded.has(p.id)) { boastCrowded.add(p.id); boastGatherCrowd(p, base); }
    if (d < 5) { p.onScreenDisplay.setActionBar(`§6❖ Boasting Platform §7— the crowd gathers… §e${5 - d}s`); continue; }
    if (d === 5) { try { p.playSound("random.orb"); } catch { } boastMenu(p, base); }
  }
}, 20);

// Gather the Guild's folk to the lawn before the stage — a thin turnout for an
// unknown Hero (maybe the trader and a guard just outside), the whole complex
// for the truly renowned, who all cheer out front.
function boastGatherCrowd(p, base) {
  const renown = P.get(p, "fc_renown", 0);
  const radius = renown >= 500 ? 90 : renown >= 150 ? 50 : renown >= 30 ? 24 : 11;
  const dim = OW();
  let folk;
  try {
    folk = dim.getEntities({
      location: { x: base.x + 34, y: base.y + 1, z: base.z + 45 },
      maxDistance: radius, families: ["fc_friendly"],
    });
  } catch { return; }
  folk = folk.filter((e) => e.typeId && e.typeId.startsWith("fc:")
    && e.typeId !== "fc:oracle" && e.typeId !== "fc:demon_door" && e.typeId !== "fc:maze");
  folk = folk.slice(0, renown < 30 ? 2 : 24);            // almost nobody for an unknown
  const fx0 = base.x + 8, fz0 = base.z + 31;             // lawn just before the stage
  const face = { x: base.x + 4, y: base.y + 3, z: base.z + 27 };
  let i = 0;
  for (const e of folk) {
    const row = Math.floor(i / 6), col = i % 6;
    try { e.teleport({ x: fx0 + col - 2.5 + row * 0.5, y: base.y + 1, z: fz0 + row * 1.4 }, { facingLocation: face }); } catch { }
    try { e.playAnimation("animation.fc.biped.greet", { blendOutTime: 0.4 }); } catch { }
    i++;
  }
  p.setDynamicProperty("fc_boast_crowd", folk.length);
  try {
    p.sendMessage(renown >= 500 ? "§6The whole Guild pours out to watch you boast!"
      : renown >= 30 ? "§6A crowd gathers to hear your boast."
        : "§7A couple of curious folk wander over.");
  } catch { }
}

// The boast: declare the title you wear (always offering no-title, Sparrow and
// Apprentice plus any you've earned); the gathered crowd then cheers.
function boastMenu(p, base) {
  ensureBaseTitles(p);
  const titles = P.getJ(p, "fc_titles", []);
  const ordered = ["Sparrow", "Apprentice", ...titles.filter((t) => t !== "Sparrow" && t !== "Apprentice")];
  const active = activeTitle(p);
  const f = new ActionFormData().title(fableTitle("Boast")).body([
    FABLE_RULE,
    `§dRenown: §f${P.get(p, "fc_renown", 0)}`,
    `§7Now wearing: §e${active || "(none)"}`,
    FABLE_RULE,
    "§6Declare the title you wear before the crowd:",
  ].join("\n"));
  f.button("§8✦ Wear no title");
  for (const t of ordered) f.button((t === active ? "§a● " : "§e✦ ") + t);
  f.show(p).then((res) => {
    if (res.canceled) return;
    if (res.selection === 0) { P.setJ(p, "fc_active_title", ""); applyTitleTag(p); p.sendMessage("§7You wear no title."); return; }
    const t = ordered[res.selection - 1];
    P.setJ(p, "fc_active_title", t); applyTitleTag(p);
    p.sendMessage(`§6✦ You declare yourself §e${t}§6 before Albion!`);
    boastCheer(p, base);
  });
}

function boastCheer(p, base) {
  const n = p.getDynamicProperty("fc_boast_crowd") ?? 0;
  if (!n) return;
  const dim = OW();
  const cx = base.x + 8, cz = base.z + 32;
  for (let k = 0; k < 6; k++) {
    system.runTimeout(() => {
      try {
        for (let j = 0; j < Math.min(8, n); j++)
          dim.spawnParticle("minecraft:totem_particle",
            { x: cx + (Math.random() - 0.5) * 6, y: base.y + 2 + Math.random() * 2, z: cz + (Math.random() - 0.5) * 4 });
      } catch { }
      try { for (const q of world.getPlayers()) q.playSound("random.levelup", { volume: 0.45 }); } catch { }
    }, k * 8);
  }
}

// NPCs murmur and react as the Hero passes — a villager sound and the odd
// remark, addressed by the Hero's worn title.
const NPC_VOICE = {
  "fc:guildmaster": ["Mind your stance, {you}.", "Renown is earned, not given."],
  "fc:maze": ["The Will stirs around you, {you}.", "Knowledge is the deadliest blade."],
  "fc:trader": ["Finest wares in Albion, {you}!", "Browse a while, no pressure."],
  "fc:theresa": ["The future bends around you, {you}.", "I see paths you cannot."],
  "fc:oracle": ["The deep ice remembers your name, {you}.", "Ask, and the truth may wound you."],
  "fc:briar_rose": ["Demon Doors love a riddle, {you}.", "Mind the wilds after dark."],
  "fc:lady_grey": ["Bowerstone watches you closely, {you}.", "Charm opens more doors than steel."],
  "fc:mercenary": ["Coin first, questions later, {you}.", "I've bled in worse places than this."],
  "fc:barkeep": ["Ale, {you}? Best in the guild.", "Mind the floor, just mopped."],
  "fc:guild_apprentice_might": ["One day I'll best you, {you}.", "*grunts, swinging a practice sword*"],
  "fc:guild_apprentice_skill": ["Bullseye! See that, {you}?", "*looses an arrow at the butt*"],
  "fc:guild_apprentice_will": ["The Will hums today…", "*sparks crackle between their fingers*"],
  "fc:villager_albion": ["A real Hero! Bless you, {you}.", "Did you hear the news from Bowerstone?"],
  "fc:villager_woman": ["Stay safe out there, {you}.", "My, but you've grown famous, {you}."],
  "fc:villager_farmer": ["Crops won't tend themselves, {you}.", "Hobbes got into the turnips again."],
  "fc:villager_tailor": ["I could let out that jerkin, {you}.", "Fine cloth from Bowerstone, just in."],
  "fc:villager_blacksmith": ["Keep that blade keen, {you}.", "*hammer rings on hot iron*"],
  "fc:villager_fisher": ["The catch is good by the quay, {you}.", "Smells like rain off the coast."],
  "fc:guard_bowerstone": ["Move along, {you}.", "No trouble on my watch."],
  "fc:guard_oakvale": ["Quiet village, let's keep it so, {you}.", "Eyes open after dusk."],
  "fc:guard_snowspire": ["Cold enough for you, {you}?", "The Oracle sees all who pass."],
};
const NPC_NAME = {
  "fc:guildmaster": "Guildmaster", "fc:maze": "Maze", "fc:trader": "Trader",
  "fc:theresa": "Theresa", "fc:oracle": "The Oracle", "fc:briar_rose": "Briar Rose",
  "fc:lady_grey": "Lady Grey", "fc:mercenary": "Mercenary", "fc:barkeep": "Alfie",
  "fc:guild_apprentice_might": "Apprentice", "fc:guild_apprentice_skill": "Apprentice",
  "fc:guild_apprentice_will": "Apprentice", "fc:villager_albion": "Villager",
  "fc:villager_woman": "Villager", "fc:villager_farmer": "Farmer",
  "fc:villager_tailor": "Tailor", "fc:villager_blacksmith": "Blacksmith",
  "fc:villager_fisher": "Fisher", "fc:guard_bowerstone": "Bowerstone Guard",
  "fc:guard_oakvale": "Oakvale Guard", "fc:guard_snowspire": "Snowspire Guard",
};
// the NPC's own synthesized voice cue (fc.entity.<id>), wired in RP sounds.json
function npcVoiceSound(typeId) { return "fc.entity." + typeId.slice(3); }
// a passing Hero is greeted: the NPC waves (limbs move), murmurs its own voice,
// and remarks, addressed by the Hero's worn title.
function npcGreet(p, e) {
  try { e.playAnimation("animation.fc.biped.greet", { blendOutTime: 0.4 }); } catch { }
  try { p.playSound(npcVoiceSound(e.typeId), { location: e.location, volume: 1.0, pitch: 0.88 + Math.random() * 0.22 }); } catch { }
}
const npcSaidAt = new Map();
system.runInterval(() => {
  const now = TICKS();
  for (const p of world.getPlayers()) {
    let near;
    try { near = p.dimension.getEntities({ location: p.location, maxDistance: 7 }); } catch { continue; }
    for (const e of near) {
      const lines = NPC_VOICE[e.typeId];
      if (!lines) continue;
      if ((npcSaidAt.get(e.id) ?? -9999) > now - 140) continue;   // per-NPC cooldown
      if (Math.random() > 0.5) continue;
      npcSaidAt.set(e.id, now);
      const line = lines[Math.floor(Math.random() * lines.length)].replace("{you}", heroAddress(p));
      try { p.onScreenDisplay.setActionBar(`§e${NPC_NAME[e.typeId] ?? "Citizen"}: §f${line}`); } catch { }
      npcGreet(p, e);
      break;
    }
  }
}, 40);

function cullisTravel(p, sites, here) {
  const others = sites.filter((s) => s.name !== here.name);
  if (!others.length) {
    return p.sendMessage("§7The Gate hums, but no sister-gates answer. Discover Focus Sites to expand the lattice.");
  }
  const f = new ActionFormData().title("§b◈ Cullis Gate")
    .body(`${FABLE_RULE}\n§7The lattice of Albion bends to your Will.\n§7Standing at: §b${here.name}\n${FABLE_RULE}`);
  for (const s of others) {
    f.button(`§b${s.name}\n§8${Math.round(Math.hypot(p.location.x - s.x, p.location.z - s.z))}m distant`,
      "textures/items/septimal_key");
  }
  f.show(p).then((r) => {
    if (r.canceled) return;
    const s = others[r.selection];
    try { p.dimension.spawnParticle("minecraft:huge_explosion_emitter", p.location); } catch { }
    p.playSound("fc.spell_cast", { pitch: 0.6 });
    p.teleport({ x: s.x + 0.5, y: s.y + 1, z: s.z + 0.5 });
    p.playSound("mob.endermen.portal");
    p.onScreenDisplay.setTitle("§b◈", { fadeInDuration: 2, stayDuration: 16, fadeOutDuration: 8, subtitle: `§f${s.name}` });
  });
}

// ---------------------------------------------------------------------------
// FACTIONS — per-player reputation that NPCs actually care about
// ---------------------------------------------------------------------------
const FACTION_NAMES = {
  guild: "The Heroes' Guild", bowerstone: "Bowerstone", oakvale: "Oakvale",
  snowspire: "Snowspire", bandits: "Twinblade's Bandits",
};
function rep(p, f) { return P.get(p, `fc_rep_${f}`, 0); }
function addRep(p, f, dv) {
  if (!dv) return;
  const v = Math.max(-200, Math.min(200, rep(p, f) + dv));
  P.set(p, `fc_rep_${f}`, v);
  if (Math.abs(dv) >= 5) {
    p.sendMessage(`§7✦ ${FACTION_NAMES[f]}: ${dv > 0 ? "§a+" : "§c"}${dv} §7reputation (${v})`);
  }
}
function repTier(v) {
  return v <= -100 ? "hostile" : v < 0 ? "wary" : v < 50 ? "neutral" : v < 150 ? "friendly" : "revered";
}
function townAvgRep(p) {
  return (rep(p, "bowerstone") + rep(p, "oakvale") + rep(p, "snowspire")) / 3;
}

// Renown-based flavour line NPCs use to acknowledge the Hero's growing fame —
// independent of any single faction, since renown is global.
function renownLine(p) {
  const renown = P.get(p, "fc_renown", 0);
  const m = morality(p);
  if (renown >= 1500) return m >= 0 ? "Your name is sung in every tavern from here to Bowerstone." : "They speak your name only after the door is barred.";
  if (renown >= 500) return m >= 0 ? "Word of your deeds is starting to travel." : "Folk go quiet when your name comes up.";
  if (renown >= 100) return "You're starting to make a name for yourself.";
  return "";
}

// Guild reputation flavour line for NPCs tied to the Heroes' Guild.
const GUILD_REP_LINES = {
  hostile: "The Guild has all but disowned you.",
  wary: "Some here still whisper about your last stunt.",
  neutral: "",
  friendly: "Good to see a friend of the Guild.",
  revered: "The Guild speaks of you with real pride these days.",
};
function guildRepLine(p) {
  return GUILD_REP_LINES[repTier(rep(p, "guild"))] ?? "";
}
const GUARD_TOWN = {
  "fc:guard_bowerstone": "bowerstone", "fc:guard_oakvale": "oakvale",
  "fc:guard_snowspire": "snowspire",
};
const VILLAGER_TOWN = {
  "fc:villager_albion": "bowerstone", "fc:villager_farmer": "oakvale",
  "fc:villager_woman": "snowspire", "fc:villager_tailor": "bowerstone",
  "fc:villager_blacksmith": "bowerstone", "fc:villager_fisher": "oakvale",
};

function factionKillHooks(p, dead, fam) {
  const t = dead.typeId;
  if (fam === "fc_twinblade") {
    addRep(p, "bandits", -40);
    addRep(p, "bowerstone", 15); addRep(p, "oakvale", 15); addRep(p, "snowspire", 10);
    addRep(p, "guild", 20);
  } else if (fam === "fc_bandit") {
    addRep(p, "bandits", -2);
    addRep(p, "bowerstone", 1); addRep(p, "oakvale", 1);
  } else if (fam === "fc_guard") {
    const town = GUARD_TOWN[t];
    if (town) addRep(p, town, -30);
    for (const o of ["bowerstone", "oakvale", "snowspire"]) if (o !== town) addRep(p, o, -8);
    addRep(p, "bandits", 6);
    addRep(p, "guild", -10);
  } else if (fam === "fc_villager" || fam === "fc_trader") {
    const town = VILLAGER_TOWN[t] ?? "bowerstone";
    addRep(p, town, -15);
    for (const o of ["bowerstone", "oakvale", "snowspire"]) if (o !== town) addRep(p, o, -4);
    addRep(p, "bandits", 3);
  } else if (["fc_balverine", "fc_undead", "fc_troll", "fc_banshee", "fc_wraith"].includes(fam)) {
    if (Math.random() < 0.25) addRep(p, "guild", 1);
  }
}

// guards remember: infamous players get attacked on sight
system.runInterval(() => {
  for (const p of world.getPlayers()) {
    for (const g of p.dimension.getEntities({ location: p.location, maxDistance: 18, families: ["fc_guard"] })) {
      const town = GUARD_TOWN[g.typeId];
      if (!town) continue;
      try {
        g.triggerEvent(rep(p, town) <= -100 ? "fc:turn_hostile" : "fc:calm");
      } catch { }
    }
  }
}, 100);

// ---------------------------------------------------------------------------
// EXPERIENCE ORBS — slain foes shed coloured essence (use to absorb)
// ---------------------------------------------------------------------------
function dropOrbs(dim, loc, src, fam) {
  const boss = fam === "fc_boss" || fam === "fc_twinblade";
  if (!boss && Math.random() > 0.35) return;
  const ranged = !!src?.damagingProjectile;
  const cause = src?.cause ?? "";
  const magic = ["magic", "lightning", "wither", "fireTick", "fire"].includes(cause);
  const typed = magic ? "fc:orb_will" : ranged ? "fc:orb_skill" : "fc:orb_strength";
  try {
    const n = boss ? 3 + Math.floor(Math.random() * 3) : 1;
    dim.spawnItem(new ItemStack(typed, n), loc);
    if (boss || Math.random() < 0.4) dim.spawnItem(new ItemStack("fc:orb_general", boss ? 2 : 1), loc);
  } catch { }
}

const ORB_XP = {
  "fc:orb_general": ["general", 60], "fc:orb_strength": ["strength", 60],
  "fc:orb_skill": ["skill", 60], "fc:orb_will": ["will", 60],
};

// ---------------------------------------------------------------------------
// World decoration: deterministic, biome-aware region structures
// ---------------------------------------------------------------------------
const REGION = 160;
// Each entry: weight = relative pick frequency; surf = ground categories the
// structure may settle on; theme = surrounding set-dressing flavour.
// The Heroes' Guild complex (hall, courtyard, Chamber of Fate) is placed
// exactly once by placeGuildNear and never appears in this pool.
const STRUCTS = [
  { id: "fc:demon_door_arch", w: 23, weight: 10, surf: ["grass", "dark", "rock", "snow"], theme: "dark", door: true },
  { id: "fc:silver_chest_ruin", w: 13, weight: 11, surf: ["grass", "dark", "rock", "sand", "snow"], theme: "forest", loot: "ruin" },
  { id: "fc:bandit_camp", w: 33, weight: 9, surf: ["grass", "dark", "rock"], theme: "dark", mobs: ["fc:bandit", "fc:bandit", "fc:bandit_archer", "fc:twinblade"] },
  { id: "fc:graveyard", w: 25, weight: 7, surf: ["grass", "dark"], theme: "dark", mobs: ["fc:undead", "fc:undead_soldier", "fc:undead_knight"] },
  { id: "fc:focus_site", w: 13, weight: 7, surf: ["grass", "dark", "rock", "sand", "snow"], theme: "dark", cullis: true },
  { id: "fc:oakvale_village", w: 35, weight: 8, surf: ["grass", "sand"], theme: "village", cullis: true,
    mobs: ["fc:villager_farmer", "fc:villager_fisher", "fc:guard_oakvale"] },
  { id: "fc:bowerstone_market", w: 37, weight: 7, surf: ["grass"], theme: "village", cullis: true,
    mobs: ["fc:guard_bowerstone", "fc:trader", "fc:barkeep", "fc:villager_albion"] },
  { id: "fc:knothole_glade", w: 35, weight: 7, surf: ["dark", "grass"], theme: "forest", cullis: true,
    mobs: ["fc:villager_woman", "fc:guard_oakvale", "fc:mercenary"] },
  { id: "fc:hook_coast", w: 37, weight: 7, surf: ["snow", "sand", "rock"], theme: "snow", cullis: true,
    mobs: ["fc:oracle", "fc:guard_snowspire", "fc:villager_woman"] },
  { id: "fc:power_oakvale_quay", w: 29, weight: 5, surf: ["grass", "sand"], theme: "village", cullis: true,
    mobs: ["fc:villager_farmer", "fc:villager_fisher", "fc:guard_oakvale"] },
  { id: "fc:power_snowspire_oracle", w: 31, weight: 6, surf: ["snow", "rock"], theme: "snow", cullis: true,
    mobs: ["fc:oracle", "fc:guard_snowspire", "fc:villager_woman"] },
  { id: "fc:power_necropolis", w: 29, weight: 5, surf: ["dark", "rock", "grass"], theme: "dark", cullis: true,
    mobs: ["fc:wraith", "fc:undead_knight", "fc:frost_balverine"] },
  { id: "fc:temple_avo", w: 17, weight: 6, surf: ["grass"], theme: "holy" },
  { id: "fc:chapel_skorm", w: 15, weight: 6, surf: ["dark", "grass", "rock"], theme: "dark" },
  { id: "fc:arena_ring", w: 27, weight: 5, surf: ["sand", "rock", "grass"], theme: "dark", mobs: ["fc:hobbe", "fc:hobbe", "fc:beetle"] },
  // wilderness encounters — small, common, keep the road alive
  { id: "fc:lookout_point", w: 21, weight: 9, surf: ["grass", "rock", "snow"], theme: "village",
    mobs: ["fc:villager_albion", "fc:villager_albion", "fc:guard_bowerstone"] },
  { id: "fc:orchard_farm", w: 29, weight: 9, surf: ["grass"], theme: "farm",
    mobs: ["fc:villager_farmer", "fc:villager_farmer", "fc:villager_woman"] },
  { id: "fc:fisher_creek", w: 23, weight: 8, surf: ["grass", "sand"], theme: "village",
    mobs: ["fc:villager_fisher", "fc:villager_fisher"] },
  { id: "fc:rose_cottage", w: 21, weight: 8, surf: ["grass"], theme: "farm",
    mobs: ["fc:briar_rose", "fc:villager_woman"] },
  { id: "fc:witchwood_stones", w: 25, weight: 8, surf: ["dark", "grass", "rock"], theme: "dark",
    mobs: ["fc:nymph", "fc:balverine"] },
  { id: "fc:darkwood_camp", w: 25, weight: 8, surf: ["dark", "grass"], theme: "forest",
    mobs: ["fc:trader", "fc:trader", "fc:mercenary"] },
  { id: "fc:hobbe_cave", w: 23, weight: 8, surf: ["dark", "rock", "grass"], theme: "dark",
    mobs: ["fc:hobbe", "fc:hobbe", "fc:hobbe", "fc:hobbe_scout"] },
  { id: "fc:windmill_hill", w: 21, weight: 8, surf: ["grass"], theme: "farm",
    mobs: ["fc:villager_farmer"] },
];

// themed loot rolled into every chest found inside a placed structure
const CHEST_LOOT = {
  "fc:bandit_camp": [["fc:gold_coin", 4, 12, 1], ["fc:steel_longsword", 1, 1, 0.4],
  ["fc:health_potion", 1, 2, 0.6], ["fc:golden_carrot_brew", 1, 3, 0.5],
  ["fc:sharpening_augment", 1, 1, 0.15], ["fc:silver_key", 1, 1, 0.2],
  ["fc:orb_strength", 1, 2, 0.4]],
  "fc:graveyard": [["fc:ectoplasm", 2, 5, 1], ["fc:will_potion", 1, 2, 0.6],
  ["fc:silver_key", 1, 1, 0.3], ["fc:banshees_tear", 1, 1, 0.2],
  ["fc:orb_will", 1, 2, 0.5]],
  "fc:silver_chest_ruin": [["fc:silver_key", 1, 2, 1], ["fc:gold_coin", 3, 10, 0.8],
  ["fc:mana_augment", 1, 1, 0.2], ["fc:will_shard", 1, 2, 0.4]],
  "fc:guild_hall": [["fc:health_potion", 1, 2, 1], ["fc:will_potion", 1, 2, 1],
  ["fc:quest_card", 1, 1, 1], ["fc:steel_ingot", 2, 4, 0.7], ["fc:gold_coin", 3, 8, 0.6]],
  "fc:arena_ring": [["fc:gold_coin", 6, 16, 1], ["fc:ages_of_skill_potion", 1, 1, 0.3],
  ["fc:experience_augment", 1, 1, 0.2], ["fc:orb_skill", 1, 3, 0.5]],
  "fc:temple_avo": [["fc:health_potion", 1, 2, 0.8], ["fc:elixir_of_life", 1, 1, 0.1]],
  "fc:chapel_skorm": [["fc:will_potion", 1, 2, 0.8], ["fc:crunchy_chick", 1, 2, 0.5]],
  "fc:chamber_of_fate": [["fc:quest_card", 1, 1, 0.9], ["fc:will_shard", 1, 3, 0.8],
  ["fc:ages_of_will_potion", 1, 1, 0.35], ["fc:orb_will", 1, 3, 0.7]],
  "fc:oakvale_village": [["fc:apple_pie", 1, 3, 0.8], ["fc:health_potion", 1, 2, 0.7],
  ["fc:gold_coin", 2, 8, 0.9], ["fc:orb_general", 1, 2, 0.5]],
  "fc:bowerstone_market": [["fc:gold_coin", 6, 16, 1], ["fc:steel_ingot", 1, 3, 0.6],
  ["fc:chain_links", 1, 3, 0.5], ["fc:orb_skill", 1, 2, 0.4]],
  "fc:knothole_glade": [["fc:balverine_fang", 1, 3, 0.7], ["fc:yew_longbow", 1, 1, 0.25],
  ["fc:will_potion", 1, 2, 0.6], ["fc:orb_skill", 1, 2, 0.5]],
  "fc:hook_coast": [["fc:frost_balverine_hide", 1, 2, 0.6], ["fc:will_shard", 1, 2, 0.7],
  ["fc:ages_of_will_potion", 1, 1, 0.25], ["fc:silver_key", 1, 1, 0.3]],
  "fc:power_guild_courtyard": [["fc:quest_card", 1, 1, 0.8], ["fc:will_potion", 1, 2, 0.8],
  ["fc:orb_will", 1, 2, 0.6], ["fc:silver_key", 1, 1, 0.2]],
  "fc:guild_armoury": [["fc:steel_ingot", 2, 5, 0.8], ["fc:steel_longsword", 1, 1, 0.3],
  ["fc:sharpening_augment", 1, 1, 0.2], ["fc:gold_coin", 3, 9, 0.7], ["fc:orb_strength", 1, 2, 0.4]],
  "fc:guild_scriptorium": [["fc:quest_card", 1, 1, 0.7], ["fc:will_shard", 1, 3, 0.8],
  ["fc:will_potion", 1, 2, 0.7], ["fc:ages_of_will_potion", 1, 1, 0.2], ["fc:orb_will", 1, 2, 0.5]],
  "fc:power_oakvale_quay": [["fc:gold_coin", 2, 8, 0.9], ["fc:apple_pie", 1, 3, 0.8],
  ["fc:health_potion", 1, 2, 0.6], ["fc:orb_general", 1, 2, 0.5]],
  "fc:power_snowspire_oracle": [["fc:will_shard", 1, 3, 0.9], ["fc:ages_of_will_potion", 1, 1, 0.35],
  ["fc:will_potion", 1, 2, 0.7], ["fc:silver_key", 1, 1, 0.3]],
  "fc:power_necropolis": [["fc:ectoplasm", 2, 6, 0.9], ["fc:banshees_tear", 1, 1, 0.3],
  ["fc:orb_will", 1, 3, 0.7], ["fc:silver_key", 1, 1, 0.25]],
  "fc:lookout_point": [["fc:gold_coin", 2, 6, 0.9], ["fc:apple_pie", 1, 2, 0.7],
  ["fc:health_potion", 1, 1, 0.5], ["fc:silver_key", 1, 1, 0.15]],
  "fc:orchard_farm": [["fc:apple_pie", 1, 3, 1], ["fc:golden_carrot_brew", 1, 2, 0.6],
  ["fc:gold_coin", 2, 6, 0.8], ["fc:orb_general", 1, 2, 0.4]],
  "fc:fisher_creek": [["fc:gold_coin", 2, 6, 0.8], ["fc:health_potion", 1, 2, 0.6],
  ["fc:silver_key", 1, 1, 0.2], ["fc:orb_skill", 1, 2, 0.4]],
  "fc:rose_cottage": [["fc:health_potion", 1, 2, 0.8], ["fc:gold_coin", 2, 6, 0.7],
  ["fc:elixir_of_life", 1, 1, 0.05], ["fc:orb_general", 1, 2, 0.4]],
  "fc:witchwood_stones": [["fc:ectoplasm", 1, 4, 0.9], ["fc:will_shard", 1, 2, 0.7],
  ["fc:will_potion", 1, 2, 0.6], ["fc:orb_will", 1, 2, 0.5], ["fc:banshees_tear", 1, 1, 0.15]],
  "fc:darkwood_camp": [["fc:gold_coin", 3, 9, 0.9], ["fc:steel_ingot", 1, 3, 0.5],
  ["fc:health_potion", 1, 2, 0.6], ["fc:sharpening_augment", 1, 1, 0.12], ["fc:silver_key", 1, 1, 0.2]],
  "fc:hobbe_cave": [["fc:gold_coin", 2, 8, 0.9], ["fc:crunchy_chick", 1, 2, 0.6],
  ["fc:orb_strength", 1, 2, 0.5], ["fc:silver_key", 1, 1, 0.25]],
  "fc:windmill_hill": [["fc:apple_pie", 1, 3, 0.9], ["fc:gold_coin", 2, 6, 0.7],
  ["fc:golden_carrot_brew", 1, 2, 0.5]],
};

function fillLootChests(dim, x0, y0, z0, w, h, d, themeId) {
  const loot = CHEST_LOOT[themeId];
  if (!loot) return;
  const work = function* () {
    for (let x = x0; x < x0 + w; x++) {
      for (let z = z0; z < z0 + d; z++) {
        for (let y = y0 - 1; y < y0 + h; y++) {
          let b;
          try { b = dim.getBlock({ x, y, z }); } catch { continue; }
          if (!b || b.typeId !== "minecraft:chest") continue;
          const cont = b.getComponent("minecraft:inventory")?.container;
          if (!cont) continue;
          for (const [id, lo, hi, chance] of loot) {
            if (Math.random() > chance) continue;
            const n = lo + Math.floor(Math.random() * (hi - lo + 1));
            try { cont.addItem(new ItemStack(id, n)); } catch { }
          }
          yield;
        }
        yield;
      }
    }
  };
  try { system.runJob(work()); } catch { for (const _ of work()) { } }
}

// Sample several points across a footprint (corners + centre) and return a
// representative ground height, so a structure sits on the land instead of
// floating above it or sinking into it. Returns null if most of the
// footprint has no solid ground beneath it (e.g. open water) — callers
// should skip placement in that case.
function sampleGroundY(dim, x0, z0, w, d, allowLiquid = false) {
  const pts = [
    [x0 + 1, z0 + 1], [x0 + w - 2, z0 + 1], [x0 + 1, z0 + d - 2],
    [x0 + w - 2, z0 + d - 2], [x0 + Math.floor(w / 2), z0 + Math.floor(d / 2)],
  ];
  const ys = [];
  for (const [x, z] of pts) {
    const y = groundY(dim, x, z, allowLiquid);
    if (y !== null) ys.push(y);
  }
  if (ys.length < 3) return null;
  return Math.round(ys.reduce((a, b) => a + b, 0) / ys.length);
}

function blendTerrain(dim, x0, y0, z0, w, d) {
  // foundation fill: every column under the structure (plus a 1-block
  // border) gets filled from the structure's base down to solid ground —
  // no gaps below buildings, no water pockets trapped underneath.
  const work = function* () {
    for (let x = x0 - 1; x <= x0 + w; x++) {
      for (let z = z0 - 1; z <= z0 + d; z++) {
        yield* foundationColumn(dim, x, y0, z);
      }
      yield;
    }
  };
  try { system.runJob(work()); } catch { /* skip blending if jobs unavailable */ }
}

function* foundationColumn(dim, x, yTop, z) {
  for (let y = yTop - 1; y > yTop - 16; y--) {
    let b;
    try { b = dim.getBlock({ x, y, z }); } catch { return; }
    if (!b) return;
    if (!b.isAir && !b.isLiquid) return; // reached solid ground
    try {
      b.setType(y > yTop - 4
        ? (Math.random() < 0.5 ? "minecraft:cobblestone" : "minecraft:stone")
        : (Math.random() < 0.4 ? "minecraft:deepslate" : "minecraft:stone"));
    } catch { return; }
    yield;
  }
}

// Feather the plinth into the surrounding land. blendTerrain only fills the
// void *under* a build; on sloping ground that leaves the lawn ending in a
// sheer rectangular cliff (the "floating slab" look). skirtTerrain rings the
// footprint with a GENTLE, organic earthen bank — the step boundary is jittered
// so it never reads as a square terrace, the grade is shallow (~1 down per 1.6
// out), and grass caps are softened with tufts — so each site melts into the
// hillside it grew from instead of perching on a dropped slab.
function skirtTerrain(dim, x0, y0, z0, w, d, R) {
  const { cap, sub } = skirtBiome(dim, x0, z0, w, d, R);
  const work = function* () {
    for (let x = x0 - R; x < x0 + w + R; x++) {
      for (let z = z0 - R; z < z0 + d + R; z++) {
        const ox = x < x0 ? x0 - x : (x >= x0 + w ? x - (x0 + w - 1) : 0);
        const oz = z < z0 ? z0 - z : (z >= z0 + d ? z - (z0 + d - 1) : 0);
        const out = Math.max(ox, oz);
        if (out === 0) continue;          // inside the footprint — leave it
        // a STEEP, lightly-jittered bank that hugs the plinth and drives down to
        // the natural ground fast (no wide out-of-place shelf)
        const j = hash2(x * 2 + 7, z * 2 + 3) * 1.4;
        const step = Math.max(0, Math.round(out - j));   // ~1:1 grade
        skirtColumn(dim, x, z, y0, y0 - step, cap, sub);
        yield;
      }
    }
  };
  try { system.runJob(work()); } catch { }
}

// Choose the skirt's surface material from the untouched land just outside the
// footprint, so the ramp wears snow on snow, sand on sand, etc.
function skirtBiome(dim, x0, z0, w, d, R) {
  const pts = [
    [x0 + (w >> 1), z0 - R - 3], [x0 + (w >> 1), z0 + d + R + 2],
    [x0 - R - 3, z0 + (d >> 1)], [x0 + w + R + 2, z0 + (d >> 1)],
    [x0 - R - 3, z0 - R - 3], [x0 + w + R + 2, z0 + d + R + 2],
  ];
  const tally = {};
  for (const [px, pz] of pts) {
    const gy = groundY(dim, px, pz);
    if (gy === null) continue;
    let t = "";
    try { t = dim.getBlock({ x: px, y: gy - 1, z: pz })?.typeId ?? ""; } catch { }
    let k = "grass";
    if (t.includes("snow") || t.includes("ice")) k = "snow";
    else if (t.includes("sand")) k = "sand";
    else if (t.includes("stone") || t.includes("deepslate") || t.includes("gravel")
      || t.includes("andesite") || t.includes("diorite") || t.includes("granite")
      || t.includes("tuff") || t.includes("calcite")) k = "rock";
    tally[k] = (tally[k] ?? 0) + 1;
  }
  let best = "grass", n = -1;
  for (const k in tally) if (tally[k] > n) { n = tally[k]; best = k; }
  return ({
    snow: { cap: "minecraft:snow", sub: "minecraft:dirt" },
    sand: { cap: "minecraft:sand", sub: "minecraft:sandstone" },
    rock: { cap: "minecraft:stone", sub: "minecraft:stone" },
    grass: { cap: "minecraft:grass_block", sub: "minecraft:dirt" },
  })[best];
}

function skirtColumn(dim, x, z, yPlinth, targetTop, cap, sub) {
  const gy = groundY(dim, x, z);
  if (gy === null) return;                 // open water / unloaded — skip
  const natTop = gy - 1;                    // highest natural solid block here
  if (natTop > targetTop) return;           // a real hill rises here — leave it
  for (let y = natTop + 1; y < targetTop; y++) skirtSet(dim, x, y, z, sub);
  skirtSet(dim, x, targetTop, z, cap);
  // shave any exposed foundation wall / plinth overhang above the bank
  for (let y = targetTop + 1; y <= yPlinth + 1; y++) {
    try { const b = dim.getBlock({ x, y, z }); if (b && !b.isAir) b.setType("minecraft:air"); } catch { }
  }
  // soften grassy banks with the odd tuft of grass or fern
  if (cap === "minecraft:grass_block" && hash2(x * 5 + 1, z * 5 + 9) < 0.16) {
    try {
      const t = dim.getBlock({ x, y: targetTop + 1, z });
      if (t && t.isAir) t.setType(hash2(x, z) < 0.5 ? "minecraft:tallgrass" : "minecraft:fern");
    } catch { }
  }
}

function skirtSet(dim, x, y, z, id) {
  try { const b = dim.getBlock({ x, y, z }); if (b && (b.isAir || b.isLiquid || b.typeId !== id)) b.setType(id); } catch { }
}

function hash2(x, z) {
  let h = (x * 374761393 + z * 668265263) ^ 1407;
  h = (h ^ (h >> 13)) * 1274126177;
  h = h ^ (h >> 16);
  return ((h >>> 0) % 100000) / 100000;
}

// classify the ground so structures land where they belong
function surfaceCategory(dim, x, z) {
  const y = groundY(dim, x, z);
  if (y === null) return null;
  let b;
  try { b = dim.getBlock({ x, y: y - 1, z }); } catch { return null; }
  if (!b) return null;
  const t = b.typeId;
  if (t.includes("snow") || t.includes("ice")) return "snow";
  if (t.includes("sand")) return "sand";
  if (t === "minecraft:podzol" || t === "minecraft:mycelium" || t === "minecraft:mud"
    || t === "minecraft:coarse_dirt") return "dark";
  if (t === "minecraft:grass_block" || t === "minecraft:dirt" || t === "minecraft:grass_path"
    || t === "minecraft:dirt_path" || t === "minecraft:moss_block") return "grass";
  if (t.includes("stone") || t.includes("gravel") || t.includes("deepslate")
    || t.includes("andesite") || t.includes("diorite") || t.includes("granite")
    || t.includes("tuff") || t.includes("calcite")) return "rock";
  return "grass";
}

// scatter themed set-dressing in a ring around a placed structure so each
// site bleeds naturally into the surrounding terrain
const THEME_DECOR = {
  forest: ["minecraft:fern", "minecraft:mossy_cobblestone", "minecraft:tallgrass", "minecraft:oak_leaves"],
  village: ["minecraft:poppy", "minecraft:oxeye_daisy", "minecraft:dirt_path", "minecraft:cornflower"],
  farm: ["minecraft:hay_block", "minecraft:poppy", "minecraft:oxeye_daisy", "minecraft:dirt_path"],
  dark: ["minecraft:deadbush", "minecraft:brown_mushroom", "minecraft:soul_torch", "minecraft:mossy_cobblestone"],
  snow: ["minecraft:snow_layer", "minecraft:snow_layer", "minecraft:spruce_fence", "minecraft:lantern"],
  holy: ["minecraft:oxeye_daisy", "minecraft:white_candle", "minecraft:smooth_quartz", "minecraft:cornflower"],
};

function dressSurroundings(dim, x0, y0, z0, w, theme) {
  const deco = THEME_DECOR[theme];
  if (!deco) return;
  const cx = x0 + w / 2, cz = z0 + w / 2;
  const work = function* () {
    const n = 26;
    for (let i = 0; i < n; i++) {
      const ang = (i / n) * Math.PI * 2 + Math.random() * 0.4;
      const rad = w / 2 + 2 + Math.random() * 8;
      const px = Math.floor(cx + Math.cos(ang) * rad);
      const pz = Math.floor(cz + Math.sin(ang) * rad);
      const py = groundY(dim, px, pz);
      if (py === null) { yield; continue; }
      try {
        const ground = dim.getBlock({ x: px, y: py - 1, z: pz });
        const slot = dim.getBlock({ x: px, y: py, z: pz });
        if (!ground || !slot || !slot.isAir || ground.isLiquid) { yield; continue; }
        const id = deco[Math.floor(Math.random() * deco.length)];
        if (id === "minecraft:dirt_path") ground.setType(id);
        else slot.setType(id);
      } catch { }
      yield;
    }
  };
  try { system.runJob(work()); } catch { }
}

system.runInterval(() => {
  for (const p of world.getPlayers()) {
    // Guild placement comes FIRST and is isolated: a failure anywhere else in
    // this sweep (doors, world structures) must never stop the Guild spawning.
    try {
      if (!world.getDynamicProperty("fc_guild_placed")) placeGuildNear(p);
      else if (!world.getDynamicProperty("fc_guild_chamber_placed")) placeGuildAnnexes(p.dimension);
    } catch { }
    try { ensureAllDemonDoors(p.dimension); } catch { }   // keep every carved arch wearing its face
    try {
      const rx = Math.floor(p.location.x / REGION), rz = Math.floor(p.location.z / REGION);
      for (let dx = -1; dx <= 1; dx++) {
        for (let dz = -1; dz <= 1; dz++) {
          maybePlace(p, rx + dx, rz + dz);
        }
      }
    } catch { }
  }
}, 80);

function maybePlace(p, rx, rz) {
  const key = `fc_s_${rx}_${rz}`;
  if (world.getDynamicProperty(key)) return;
  const jx = Math.floor(hash2(rx * 7 + 1, rz) * (REGION - 40)) + 20;
  const jz = Math.floor(hash2(rx, rz * 7 + 1) * (REGION - 40)) + 20;
  let x = rx * REGION + jx, z = rz * REGION + jz;
  const dx = x - p.location.x, dz = z - p.location.z;
  const dist = Math.hypot(dx, dz);
  if (dist > 96 || dist < 20) return; // wait until in sweet placement range
  const dim = p.dimension;
  // what ground are we standing on? (null = chunk not ready — retry later)
  const surf = surfaceCategory(dim, x + 11, z + 11);
  if (surf === null) return;
  // deterministic weighted pick among structures suited to this terrain,
  // with a slice of "nothing here" so the world keeps breathing room
  const pool = STRUCTS.filter((s) => s.surf.includes(surf));
  if (!pool.length) { world.setDynamicProperty(key, 1); return; }
  const total = pool.reduce((a, s) => a + s.weight, 0);
  const noneSlice = Math.max(12, Math.round(total * 0.18));
  let roll = hash2(rx * 13 + 5, rz * 7 + 3) * (total + noneSlice);
  let pick = null;
  for (const s of pool) { if (roll < s.weight) { pick = s; break; } roll -= s.weight; }
  if (!pick) { world.setDynamicProperty(key, 1); return; }
  // Demon Doors seek rising ground so the carved hillside meets a real slope
  if (pick.door) {
    let best = null, bestSlope = -1;
    for (let probe = 0; probe < 6; probe++) {
      const px = x + (probe % 3 - 1) * 14, pz = z + (Math.floor(probe / 3) - 0.5) * 28;
      const fy = groundY(dim, px + 11, pz + 1);
      const by = groundY(dim, px + 11, pz + 11);
      if (fy === null || by === null) continue;
      const slope = by - fy;
      if (slope > bestSlope) { bestSlope = slope; best = { x: px, z: pz }; }
    }
    if (best) { x = Math.floor(best.x); z = Math.floor(best.z); }
  }
  // keep clear of the Guild grounds and of any build we already rendered
  if (tooCloseToExisting(x, z, pick.w, 24)) { world.setDynamicProperty(key, 1); return; }
  const y = sampleGroundY(dim, x, z, pick.w, pick.w);
  if (y === null) return;
  try {
    world.structureManager.place(pick.id, dim, { x, y: y - 1, z });
    world.setDynamicProperty(key, 1);
    recordPlace(x, z, pick.w, pick.id, pick.theme);
    if (pick.door) {
      const doorLoc = { x: x + 11.5, y: y, z: z + 4.6 };
      recordDemonDoor(doorLoc, z - 6);   // faces the approach (lower z)
      ensureDemonDoor(dim, doorLoc, z - 6);
    }
    if (pick.cullis) registerCullis(`Focus Site ${rx},${rz}`, { x: x + 6.5, y, z: z + 6.5 });
    for (const mtype of pick.mobs ?? []) {
      trySpawn(dim, mtype, { x: x + 5 + Math.random() * (pick.w - 10), y: y + 1, z: z + 5 + Math.random() * (pick.w - 10) });
    }
    if (pick.loot === "ruin") {
      trySpawn(dim, "fc:wraith", { x: x + 4, y: y + 1, z: z + 6 });
    }
    fillLootChests(dim, x, y - 1, z, pick.w, 28, pick.w, pick.id);
    blendTerrain(dim, x, y - 1, z, pick.w, pick.w);
    skirtTerrain(dim, x, y - 1, z, pick.w, pick.w, 6);
    dressSurroundings(dim, x, y - 1, z, pick.w, pick.theme);
  } catch { /* chunk edge; try next sweep */ }
}

// ---------------------------------------------------------------------------
// First-entry live encounters: the first time a Hero sets foot inside a
// rendered location it reacts — a greeter hails them, or its denizens stir.
// One-shot per location per player, keyed off the fc_places footprints.
// ---------------------------------------------------------------------------
const ENTRY_BY_THEME = {
  village: { line: "§e\"Well met, Hero. Mind the guards and you'll do fine here.\"", spawn: ["fc:villager_albion"], sound: "random.levelup", hostile: false },
  farm: { line: "§e\"Visitors! Don't go trampling the crops, eh?\"", spawn: ["fc:villager_farmer"], sound: "random.levelup", hostile: false },
  forest: { line: "§a Something rustles in the trees — you are being watched.", spawn: ["fc:mercenary"], sound: "mob.wolf.growl", hostile: false },
  holy: { line: "§f A hush falls — Avo's light warms this place.", spawn: [], sound: "beacon.activate", hostile: false },
  snow: { line: "§b The wind bites. A lone watcher marks your arrival.", spawn: ["fc:villager_woman"], sound: "random.levelup", hostile: false },
  dark: { line: "§5 The air turns cold — something here resents the living.", spawn: ["fc:undead", "fc:undead_soldier"], sound: "ambient.cave", hostile: true },
};
const ENTRY_BY_ID = {
  "fc:bandit_camp": { line: "§c\"Intruder in the camp — cut them down!\"", spawn: ["fc:bandit", "fc:bandit_archer"], sound: "mob.zombie.say", hostile: true },
  "fc:graveyard": { line: "§5 The graves crack open at your trespass…", spawn: ["fc:undead", "fc:undead_soldier"], sound: "ambient.cave", hostile: true },
  "fc:hobbe_cave": { line: "§c Shrieks echo from the dark — the hobbes have your scent!", spawn: ["fc:hobbe", "fc:hobbe"], sound: "mob.zombie.say", hostile: true },
  "fc:bowerstone_market": { line: "§e A Bowerstone guard strides over: \"State your business, stranger.\"", spawn: ["fc:guard_bowerstone"], sound: "random.levelup", hostile: false },
  "fc:arena_ring": { line: "§6 The crowd roars — a challenger steps into the sand!", spawn: ["fc:hobbe", "fc:beetle"], sound: "random.levelup", hostile: true },
  "fc:temple_avo": { line: "§f Avo's light embraces you; your spirit feels lighter.", spawn: [], sound: "beacon.activate", hostile: false },
  "fc:chapel_skorm": { line: "§4 A cold dread seeps from the altar of Skorm.", spawn: ["fc:undead"], sound: "ambient.cave", hostile: true },
};
function firstEntryFor(place) {
  return ENTRY_BY_ID[place.id] ?? ENTRY_BY_THEME[place.theme] ?? null;
}
const entryCd = new Map();
system.runInterval(() => {
  const places = JSON.parse(world.getDynamicProperty("fc_places") ?? "[]");
  if (!places.length) return;
  for (const p of world.getPlayers()) {
    const visited = P.getJ(p, "fc_visited", []);
    const px = p.location.x, pz = p.location.z;
    for (const pl of places) {
      // require the player to be well inside the footprint before it reacts
      if (px < pl.x + 3 || px > pl.x + pl.w - 3 || pz < pl.z + 3 || pz > pl.z + pl.w - 3) continue;
      if (visited.includes(pl.k)) continue;
      const last = entryCd.get(p.id) ?? -9999;
      if (TICKS() - last < 40) break;  // one trigger per player per pass
      entryCd.set(p.id, TICKS());
      visited.push(pl.k);
      if (visited.length > 200) visited.splice(0, visited.length - 200);
      P.setJ(p, "fc_visited", visited);
      fireFirstEntry(p, pl);
      break;
    }
  }
}, 20);

function fireFirstEntry(p, pl) {
  const e = firstEntryFor(pl);
  if (!e) return;
  const dim = p.dimension;
  try { p.playSound(e.sound, { pitch: 1.0 }); } catch { }
  p.sendMessage(e.line);
  let i = 0;
  for (const type of e.spawn) {
    const ang = (Math.PI * 2 * i) / Math.max(1, e.spawn.length) + Math.random();
    const sx = p.location.x + Math.cos(ang) * 5;
    const sz = p.location.z + Math.sin(ang) * 5;
    const sy = groundY(dim, Math.floor(sx), Math.floor(sz)) ?? (Math.floor(p.location.y) + 1);
    trySpawn(dim, type, { x: sx, y: sy, z: sz });
    i++;
  }
  if (e.hostile) {
    try { dim.spawnParticle("minecraft:knockback_roar_particle", { x: p.location.x, y: p.location.y + 1, z: p.location.z }); } catch { }
  }
}

// ---------------------------------------------------------------------------
// Boss minion summoning + characterful mob voices + ally cleanup
// ---------------------------------------------------------------------------
system.runInterval(() => {
  for (const p of world.getPlayers()) {
    const dim = p.dimension;
    for (const [type, cue] of Object.entries(NPC_SOUND_CUES)) {
      for (const e of dim.getEntities({ location: p.location, maxDistance: cue.range, type })) {
        maybePlayNpcCue(p, e, cue);
      }
    }
    for (const boss of dim.getEntities({ location: p.location, maxDistance: 40, families: ["fc_boss"] })) {
      const minionType = boss.typeId === "fc:white_balverine" ? "fc:balverine"
        : boss.typeId === "fc:wasp_queen" ? "fc:wasp"
          : boss.typeId === "fc:jack_of_blades" ? "fc:undead" : null;
      if (!minionType) continue;
      const existing = dim.getEntities({ location: boss.location, maxDistance: 24, type: minionType }).length;
      if (existing < 3 && Math.random() < 0.4) {
        const e = trySpawn(dim, minionType, { x: boss.location.x + 2, y: boss.location.y + 1, z: boss.location.z });
        if (e) dim.spawnParticle("minecraft:mobspawn_emitter", e.location);
      }
    }
    // banshee shriek
    for (const b of dim.getEntities({ location: p.location, maxDistance: 12, type: "fc:banshee" })) {
      if (Math.random() < 0.2) {
        p.addEffect("nausea", 100, { amplifier: 0, showParticles: false });
        p.addEffect("darkness", 60, { amplifier: 0, showParticles: false });
        p.playSound("fc.banshee_shriek", { volume: 0.8 });
      }
    }
  }
}, 160);

// ---------------------------------------------------------------------------
// HUD + Will regen + morph auras + multiplier decay
// ---------------------------------------------------------------------------
let auraPhase = 0;
system.runInterval(() => {
  auraPhase++;
  for (const p of world.getPlayers()) {
    // Will regen
    const regen = 1 + P.get(p, "fc_up_magic_power", 0);
    P.set(p, "fc_will", Math.min(maxWill(p), willEnergy(p) + regen));
    // multiplier decay
    if (TICKS() - P.get(p, "fc_lastHit", 0) > 240 && P.get(p, "fc_mult", 0) > 0) {
      P.set(p, "fc_mult", Math.max(0, P.get(p, "fc_mult", 0) - 2));
    }
    // HUD
    const mult = P.get(p, "fc_mult", 0);
    const aq = activeQuest(p);
    const qname = aq ? DATA.quests.find((q) => q.id === aq.id)?.name : null;
    p.onScreenDisplay.setActionBar(
      `§b✦ Will ${bar(willEnergy(p), maxWill(p), "§b", 10)} §f${willEnergy(p)} ` +
      (mult > 0 ? ` §6⚔ x${mult} ` : "") +
      ` ${moralityTitle(p)}` +
      (qname ? ` §8| §e${qname}` : ""));
    // morph aura
    const m = morality(p);
    const willLv = P.get(p, "fc_up_magic_power", 0);
    if (auraPhase % 3 === 0) {
      try {
        if (m >= 400) p.dimension.spawnParticle("minecraft:villager_happy", { x: p.location.x, y: p.location.y + 2.3, z: p.location.z });
        if (m >= 750) p.dimension.spawnParticle("minecraft:totem_particle", { x: p.location.x + (Math.random() - 0.5), y: p.location.y + 2.5, z: p.location.z + (Math.random() - 0.5) });
        if (m <= -400) p.dimension.spawnParticle("minecraft:basic_smoke_particle", { x: p.location.x + (Math.random() - 0.5), y: p.location.y + 1.8, z: p.location.z + (Math.random() - 0.5) });
        if (m <= -750) p.dimension.spawnParticle("minecraft:soul_particle", { x: p.location.x, y: p.location.y + 1.2, z: p.location.z });
        if (willLv >= 3) p.dimension.spawnParticle("minecraft:enchanting_table_particle", { x: p.location.x, y: p.location.y + 1.5, z: p.location.z });
      } catch { }
    }
    // augmented weapons hum with the colours of their bound powers
    if (auraPhase % 5 === 0) {
      try {
        const held = heldItem(p);
        if (held && DATA.weapons[held.typeId]) {
          const augs = weaponAugments(held);
          if (augs.length) {
            const fx = AUGMENT_FX[augs[(auraPhase / 5) % augs.length]];
            const dir = p.getViewDirection();
            p.dimension.spawnParticle(fx?.particle ?? "minecraft:enchanting_table_particle", {
              x: p.location.x + dir.x * 0.8 + (Math.random() - 0.5) * 0.2,
              y: p.location.y + 1 + (Math.random() - 0.5) * 0.2,
              z: p.location.z + dir.z * 0.8 + (Math.random() - 0.5) * 0.2,
            });
          }
        }
      } catch { }
    }
    applyUpgrades(p);
  }
}, 20);

// renown attracts ambushes: famous heroes get jumped by assassins
system.runInterval(() => {
  for (const p of world.getPlayers()) {
    const renown = P.get(p, "fc_renown", 0);
    if (renown < 400) continue;
    if (Math.random() > Math.min(0.25, renown / 8000)) continue;
    const t = world.getTimeOfDay();
    if (t < 13000) continue; // night ambushes only
    const ang = Math.random() * Math.PI * 2;
    const loc = { x: p.location.x + Math.cos(ang) * 14, y: p.location.y + 1, z: p.location.z + Math.sin(ang) * 14 };
    const n = renown > 1500 ? 3 : 2;
    let spawned = 0;
    for (let i = 0; i < n; i++) if (trySpawn(p.dimension, "fc:assassin", loc)) spawned++;
    if (spawned) p.sendMessage("§4✦ Your fame has a price — assassins emerge from the dark!");
  }
}, 1200);

console.warn("[Fablecraft] Reforged systems online. Albion awaits.");

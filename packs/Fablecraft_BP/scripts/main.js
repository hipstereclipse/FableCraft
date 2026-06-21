// ============================================================================
// Fablecraft: Reforged — main gameplay script
// Hero stats (Strength/Skill/Will XP), morality, combat multiplier, Will
// powers, quests, Demon Doors, NPC dialogue, traders, world decoration,
// boss phases (Jack of Blades), augments, and the Guild.
// ============================================================================
import {
  world, system, EquipmentSlot, EntityDamageCause, ItemStack, MolangVariableMap,
} from "@minecraft/server";
import {
  ActionFormData, MessageFormData, ModalFormData,
} from "@minecraft/server-ui";
import { DATA } from "./fc_gamedata.js";
import {
  performFableEmote, refreshFableEmoteUnlocks,
} from "./fable_emotes.js";
import { FABLE_EMOTES } from "./fable_emote_registry.js";
import { showHudNotice } from "./fable_hud.js";
import "./wd/main.js";
import { openHeroMenu as wdOpenHeroMenu } from "./wd/herobook.js";
import { LEGACY_MENU } from "./wd/menu_bridge.js";

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

function showHeroActionBar(p, text, holdTicks = 30) {
  showHudNotice(p, text, holdTicks);
  return undefined;
}

function showHeroTitle(p, title, options = {}) {
  const stayDuration = options.stayDuration ?? 40;
  showHudNotice(p, `${title}${options.subtitle ? ` §7— ${options.subtitle}` : ""}`, stayDuration);
}

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

function fableBody(lines) { return [FABLE_RULE, ...lines, FABLE_RULE].join("\n"); }
function displayName(id) {
  return id.replace(/^(fc|wd):/, "").split("_")
    .map((word) => word ? word[0].toUpperCase() + word.slice(1) : "")
    .join(" ");
}

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
  // Use one idempotent recovery path for first spawn and later joins.
  system.runTimeout(() => initHero(p), ev.initialSpawn ? 20 : 5);
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

const STARTER_KIT_VERSION = 235;
const STARTER_KIT_ITEMS = [
  "fc:stick", "fc:guild_seal", "fc:quest_card",
  "fc:apprentice_helm", "fc:apprentice_torso", "fc:apprentice_legs", "fc:apprentice_boots",
  "fc:health_potion", "fc:apple_pie",
];

function grantStarterKit(p) {
  for (const itemId of STARTER_KIT_ITEMS) {
    if (countItem(p, itemId) < 1) giveItem(p, itemId, 1);
  }
  ensureGuildSeal(p);
  const goldNeeded = Math.max(0, 5 - countItem(p, "fc:gold_coin"));
  if (goldNeeded > 0) giveItem(p, "fc:gold_coin", goldNeeded);
  const complete = STARTER_KIT_ITEMS.every((itemId) => countItem(p, itemId) > 0)
    && countItem(p, "fc:gold_coin") >= 5;
  if (complete) {
    P.set(p, "fc_starter_kit_version", STARTER_KIT_VERSION);
  }
}

function initHero(p) {
  const firstInit = !P.get(p, "fc_init", false);
  if (P.get(p, "fc_starter_kit_version", 0) < STARTER_KIT_VERSION) {
    grantStarterKit(p);
  } else {
    ensureGuildSeal(p);
  }
  if (firstInit) {
    P.set(p, "fc_init", true);
    P.set(p, "fc_will", 100);
    showHeroTitle(p, "§6Fablecraft", { fadeInDuration: 10, stayDuration: 70, fadeOutDuration: 20, subtitle: "§eReforged — Welcome to Albion" });
    p.sendMessage("§6═══ The Guildmaster ═══");
    p.sendMessage("§f\"Ah, the new apprentice wakes. Your §eGuild Seal§f opens the Hero menu. Use a §eQuest Card§f to begin your training. Albion is watching, little sparrow.\"");
    ensureDryLanding(p);
  }
  // Retry unfinished placement on every join. The world-level completion flag
  // keeps this idempotent after the Guild has been successfully assembled.
  placeGuildNear(p);
  setGuildSpawn(p);
  repairGuildAnchors();
}

// Re-derive the Guild's interactive anchors (Skill shrine + Cullis Gate) from
// the recorded base on every join. The campus itself is placed only once, but
// its layout constants can shift between versions; refreshing the live anchors
// here keeps the Cullis Gate, Skill shrine and Boasting platform from going dead
// on a world whose Guild was built by an earlier layout. Harmless when current.
function repairGuildAnchors() {
  if (!world.getDynamicProperty("fc_guild_placed")) return;
  const raw = world.getDynamicProperty("fc_guild_base");
  if (!raw) return;
  let base; try { base = JSON.parse(raw); } catch { return; }
  const y = base.y;
  try {
    const skill = JSON.stringify({ x: base.x + GUILD.skill.x, y, z: base.z + GUILD.skill.z });
    world.setDynamicProperty("fc_guild_skill", skill);
    world.setDynamicProperty("fc_guild_train", skill);
    registerCullis("Heroes' Guild", { x: base.x + GUILD.cullis.x, y: y + 1, z: base.z + GUILD.cullis.z });
  } catch { }
}

// In-game diagnostics / repair (run from chat):
//   /scriptevent fc:reanchor   — re-derive the Cullis/Skill/Boast anchors and
//                                report where they sit relative to you.
//   /scriptevent fc:wanted     — list your active warrants.
//   /scriptevent fc:clearwanted — drop all your warrants (testing aid).
system.afterEvents.scriptEventReceive.subscribe((ev) => {
  const p = ev.sourceEntity;
  if (ev.id === "fc:reanchor") {
    repairGuildAnchors();
    const raw = world.getDynamicProperty("fc_guild_base");
    if (!raw) { try { p?.sendMessage("§cNo Guild base recorded in this world yet."); } catch { } return; }
    let base; try { base = JSON.parse(raw); } catch { return; }
    const cullis = { x: base.x + GUILD.cullis.x, y: base.y + 1, z: base.z + GUILD.cullis.z };
    const skill = { x: base.x + GUILD.skill.x, y: base.y, z: base.z + GUILD.skill.z };
    const boast = { x: base.x + 4, y: base.y + 3, z: base.z + 26 };
    const here = p?.location;
    const dist = (a) => here ? `${Math.round(Math.hypot(here.x - a.x, here.z - a.z))}m` : "?";
    try {
      p?.sendMessage([
        "§6⚙ Guild anchors re-derived from base:",
        `§b◈ Cullis §7${cullis.x},${cullis.y},${cullis.z} §8(${dist(cullis)} away)`,
        `§a✦ Skill §7${skill.x},${skill.y},${skill.z} §8(${dist(skill)} away)`,
        `§6❖ Boast §7${boast.x},${boast.y},${boast.z} §8(${dist(boast)} away)`,
        "§7Stand on each spot and re-run — it should read ~0–2m. If it's far off,",
        "§7the structure and the layout constants are out of sync.",
      ].join("\n"));
    } catch { }
    return;
  }
  if (p?.typeId !== "minecraft:player") return;
  if (ev.id === "fc:wanted") {
    const lines = bountySummaryLines(p);
    try { p.sendMessage(lines.length ? lines.join("\n") : "§7You have no active warrants."); } catch { }
  } else if (ev.id === "fc:clearwanted") {
    for (const key of Object.keys(getBounties(p))) clearSettlementBounty(p, key, "cleared by command");
    try { p.sendMessage("§aAll your warrants cleared."); } catch { }
  }
});

const GUILD_TA = "fc_guild_keep";  // legacy core ticking area
const GUILD_TERRAIN_RADIUS = 40;
const GUILD_TA_MARGIN = GUILD_TERRAIN_RADIUS + 4;
const OVERWORLD_SEA_LEVEL = 62;
// NOTE: the campus + the river/east features were shifted EAST by GUILD_EAST=10
// in gen_structures.py (the reference puts the river at ~0.53 of width). The
// width grew 112 -> 122 and the east anchors (archery/dueling/demon) moved +10.
// The NW cluster (wake/skill/cullis/quest/cave), the Library spawns and Maze's
// Tower (x46) stayed put, so their couplings are unchanged.
const GUILD = Object.freeze({
  sx: 122, sz: 108,
  wake: { x: 20, z: 42 },
  skill: { x: 15, z: 35 },
  cullis: { x: 15, z: 49 },
  quest: { x: 22, z: 42 },
  questTables: [{ x: 22, z: 42 }, { x: 28, z: 39 }, { x: 28, z: 45 }],
  maze: { x: 46, z: 72, studyY: 12 },
  demon: { x: 66, z: 96, approachZ: 88 },
  archery: { x: 86, z: 39 },
  dueling: { x: 101, z: 61 },
  training: {
    ringA: { x: 99.5, z: 61.5 },
    ringB: { x: 102.5, z: 61.5 },
    range: { x: 83.5, z: 39.5 },
    target: { x: 83.5, z: 34.5 },
  },
  cave: { sx: 27, sz: 14, x0: 25, x1: 29, z0: 12, z1: 16 },
  exitC: { z: 32 },
});

// Keep the campus and its 40-block terrain grade loaded regardless of render
// distance. The expanded bounds are split below to stay under Bedrock's
// per-ticking-area chunk limit.
function ensureGuildTickingArea(dim, p, property, name, minX, minZ, maxX, maxZ) {
  if (world.getDynamicProperty(property)) return true;
  const cmd = `tickingarea add ${minX} 0 ${minZ} ${maxX} 319 ${maxZ} ${name}`;
  try {
    dim.runCommand(cmd);
    world.setDynamicProperty(property, true);
    return true;
  } catch {
    try {
      p?.runCommand(cmd);
      world.setDynamicProperty(property, true);
      return true;
    } catch { return false; }
  }
}

function forceLoadGuild(dim, p, base) {
  const minX = base.x - GUILD_TA_MARGIN;
  const maxX = base.x + GUILD.sx - 1 + GUILD_TA_MARGIN;
  const minZ = base.z - GUILD_TA_MARGIN;
  const maxZ = base.z + GUILD.sz - 1 + GUILD_TA_MARGIN;
  const midX = base.x + Math.floor((GUILD.sx - 1) / 2);
  const midZ = base.z + Math.floor((GUILD.sz - 1) / 2);
  const areas = [
    ["fc_guild_ta_nw_v2", "fc_guild_t_nw", minX, minZ, midX, midZ],
    ["fc_guild_ta_ne_v2", "fc_guild_t_ne", midX + 1, minZ, maxX, midZ],
    ["fc_guild_ta_sw_v2", "fc_guild_t_sw", minX, midZ + 1, midX, maxZ],
    ["fc_guild_ta_se_v2", "fc_guild_t_se", midX + 1, midZ + 1, maxX, maxZ],
  ];
  let complete = true;
  for (const [property, name, ax0, az0, ax1, az1] of areas) {
    complete = ensureGuildTickingArea(dim, p, property, name, ax0, az0, ax1, az1) && complete;
  }
  if (complete) {
    world.setDynamicProperty("fc_guild_ta", true);
    return true;
  }
  ensureGuildTickingArea(dim, p, "fc_guild_ta", GUILD_TA,
    base.x - 4, base.z - 4, base.x + GUILD.sx + 4, base.z + GUILD.sz + 4);
  return false;
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
// Guild from <=56-block tiles. Retries for ~5 minutes so generation succeeds
// even when the player's render distance leaves most of the campus unloaded.
function buildGuildWhenReady(p, dim, base, attempt) {
  if (world.getDynamicProperty("fc_guild_placed")) return;
  world.setDynamicProperty("fc_guild_build_tick", system.currentTick);  // keep the guard fresh while working
  const terrainAreaReady = forceLoadGuild(dim, p, base);
  const sampledY = sampleGroundY(dim, base.x, base.z, 122, 108, true);
  if (sampledY === null) {  // chunks still loading — try again shortly
    if (attempt < 600) system.runTimeout(() => buildGuildWhenReady(p, dim, base, attempt + 1), 10);
    return;  // else stop refreshing — the stale tick lets the next sweep restart us
  }
  // The structure's baked local-y0 ground replaces the natural surface, but
  // never place that platform below the overworld waterline.
  const y = Math.max(OVERWORLD_SEA_LEVEL, sampledY - 1);
  showHeroTitle(p, "§6Founding Guild...", { fadeInDuration: 0, stayDuration: 200, fadeOutDuration: 0, subtitle: "§ePlease wait..." });
  system.runTimeout(() => {
  try {
    // The Heroes' Guild is one connected campus placed as a single structure
    // on a single floor level. The heart is the domed Map Room rotunda at
    // local (34,44); the
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
  // Map Room rotunda (local 26,42). Wake at (20,42), facing east to the Map.
  world.setDynamicProperty("fc_guild_loc", JSON.stringify({ x: base.x + GUILD.wake.x, y, z: base.z + GUILD.wake.z }));
  // Skill / Experience shrine in the Map Room's NW nook (local 15,35)
  world.setDynamicProperty("fc_guild_train", JSON.stringify({ x: base.x + GUILD.skill.x, y, z: base.z + GUILD.skill.z }));
  world.setDynamicProperty("fc_guild_skill", JSON.stringify({ x: base.x + GUILD.skill.x, y, z: base.z + GUILD.skill.z }));
  // three Quest lecterns ring the lowered Map relief; keep a single legacy point too
  world.setDynamicProperty("fc_guild_quest_table", JSON.stringify({ x: base.x + GUILD.quest.x, y: y + 1, z: base.z + GUILD.quest.z }));
  world.setDynamicProperty("fc_guild_quest_tables", JSON.stringify(GUILD.questTables.map((q) => ({ x: base.x + q.x, y: y + 1, z: base.z + q.z }))));
  // the Guild's own Demon Door — the crag on the far south bank past the islands
  const doorLoc = { x: base.x + GUILD.demon.x, y: y + 1, z: base.z + GUILD.demon.z };
  world.setDynamicProperty("fc_guild_door", JSON.stringify(doorLoc));
  // Everything below is decoration: NPCs, the Cullis registration, loot, terrain
  // and the buried Chamber. The Guild is already PLACED above, so none of this is
  // allowed to abort the build — wrap it so a single failure can't matter.
  try {
    // the Cullis Gate beacon core in the Map Room's SW nook (local 15,49)
    registerCullis("Heroes' Guild", { x: base.x + GUILD.cullis.x, y: y + 1, z: base.z + GUILD.cullis.z });
    // Guildmaster greets arrivals at the Map; Maze keeps his tower study; Theresa
    // reads in the Library (north); a trader works the Store (south).
    trySpawn(dim, "fc:guildmaster", { x: base.x + 23, y: y + 1, z: base.z + 42 });
    trySpawn(dim, "fc:maze", { x: base.x + GUILD.maze.x, y: y + GUILD.maze.studyY, z: base.z + GUILD.maze.z });   // tower floor 3
    trySpawn(dim, "fc:theresa", { x: base.x + 26, y: y + 1, z: base.z + 23 });
    // a Trader works the covered cart OUTSIDE the west gate (random wares + a title)
    trySpawn(dim, "fc:trader", { x: base.x + 5, y: y + 1, z: base.z + 46 });
    // apprentices at work across the grounds
    trySpawn(dim, "fc:guild_apprentice_might", { x: base.x + 12, y: y + 1, z: base.z + 42 });
    trySpawn(dim, "fc:guild_apprentice_might", { x: base.x + GUILD.dueling.x, y: y + 1, z: base.z + GUILD.dueling.z });
    trySpawn(dim, "fc:guild_apprentice_skill", { x: base.x + GUILD.archery.x, y: y + 1, z: base.z + GUILD.archery.z });
    trySpawn(dim, "fc:guild_apprentice_skill", { x: base.x + 42, y: y + 1, z: base.z + 40 });
    trySpawn(dim, "fc:guild_apprentice_will", { x: base.x + 26, y: y + 1, z: base.z + 24 });
    trySpawn(dim, "fc:guild_apprentice_will", { x: base.x + 16, y: y + 1, z: base.z + 35 });
    // two watchmen keep the Guild's west entrance and answer violence on the grounds
    for (const post of [{ x: 10, z: 39 }, { x: 10, z: 45 }]) {
      const guard = trySpawn(dim, "fc:guard_bowerstone",
        { x: base.x + post.x, y: y + 1, z: base.z + post.z });
      try {
        guard?.addTag("fc_guild_npc");
        guard?.addTag("fc_guild_guard");
      } catch { }
    }
    // suits of armour stand guard at Maze's Tower's two ground entrances
    guardArmour(dim, { x: base.x + 41, y: y + 1, z: base.z + 72 }, { x: base.x + 40, y: y + 1, z: base.z + 72 });
    guardArmour(dim, { x: base.x + 46, y: y + 1, z: base.z + 67 }, { x: base.x + 46, y: y + 1, z: base.z + 66 });
    ensureDemonDoor(dim, doorLoc, base.z + GUILD.demon.approachZ);
    fillLootChests(dim, base.x, y, base.z, GUILD.sx, 30, GUILD.sz, "fc:guild_hall");
    // keep the Guild-cave spiral shaft (local 27,14 +-2) hollow — never re-fill it
    if (terrainAreaReady) settleGuildTerrain(dim, { x: base.x, y, z: base.z });
    dressSurroundings(dim, base.x, y, base.z, GUILD.sx, "holy");
    layWoodsPath(dim, base);                          // the orange dirt trail out to the Woods
    placeGuildAnnexes(dim);
    setGuildSpawn(p);
  } catch { /* decoration is best-effort; the Guild itself is already placed */ }
  // wake the new Hero on the dry crimson runner, facing north to the Map Room
  system.runTimeout(() => {
    try {
      p.teleport({ x: base.x + GUILD.wake.x + 0.5, y: y + 1, z: base.z + GUILD.wake.z + 0.5 },
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

// Carve the Guild Caves: a 3x3 spiral stair (central glowing pillar) of
// HALF-BLOCK steps carries the ENTIRE descent from the Library's caves alcove
// down to the Chamber floor level, then a long, DEAD-LEVEL stone causeway
// crosses a wide, deep, DARK gulf and pierces the Chamber of Fate's north wall
// through a level arch. Every spiral tread drops the floor by exactly 0.5 block
// (slab/full-course alternation), so the walk is jump-free DOWN *and* UP, end to
// end (alcove -> spiral down -> flat span over darkness -> arch -> Chamber).
// Runtime-carved because it spans the surface build down to the buried Chamber.
// Idempotent, bounded, and fully wrapped so it can never break a build. The
// shaft footprint is excluded from blendTerrain (foundation fill) so the
// freshly-carved well is never back-filled with rock — and re-scrubbed on a few
// delays to defeat any late async fill (see scrubCaveShaft).
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

// Populate the land just outside the Guild with biome-matched trees and ground
// cover so the campus melts into the surrounding wilds instead of sitting on a
// bare ring. Idempotent; bounded; fully wrapped.
function populateSurroundings(dim, base, force = false) {
  if (!force && world.getDynamicProperty("fc_guild_wild_done")) return;
  const W = 122, D = 108, R = 26;
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
      if (t.includes("water") || t.includes("ice")) { yield; continue; }
      const sandy = t.includes("sand");
      const snowy = t.includes("snow");
      const grassy = t.includes("grass") || t === "minecraft:dirt" || t.includes("podzol") || t.includes("moss") || t.includes("mycelium");
      if (Math.random() < 0.35) {                      // biome-matched ground cover
        if (snowy) setBlk(px, gy, pz, "minecraft:snow_layer");
        else if (sandy) { if (Math.random() < 0.25) setBlk(px, gy, pz, "minecraft:deadbush"); }
        else if (grassy) setBlk(px, gy, pz, Math.random() < 0.5 ? "minecraft:tallgrass" : "minecraft:fern");
        yield; continue;
      }
      if (!grassy && !snowy) { yield; continue; }      // sand / bare rock: keep the shore & slopes open, no woods
      const spruce = t.includes("podzol") || snowy || t.includes("spruce") || t.includes("moss");
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

// Find actual terrain, not the top of a tree. Guild placement used groundY()
// here previously, so a jungle canopy was interpreted as a buildable plateau.
function naturalGroundY(dim, x, z, allowLiquid = false) {
  try {
    const top = dim.getTopmostBlock({ x, z });
    if (!top) return null;
    const topY = top.y ?? top.location?.y;
    if (typeof topY !== "number") return null;
    const lo = Math.max(-64, topY - 128);
    for (let y = topY; y >= lo; y--) {
      const b = dim.getBlock({ x, y, z });
      if (!b || b.isAir) continue;
      if (b.isLiquid) return allowLiquid ? y + 1 : null;
      const t = b.typeId;
      if (t === "minecraft:snow_layer" || isSkirtVeg(t)) continue;
      return y + 1;
    }
  } catch { }
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
    // the Guild is one 122x30x108 tiled campus (rotunda + nave + wings +
    // library + tower + grounds), with the Chamber of Fate buried beneath it
    minX: base.x - 3, maxX: base.x + 125,
    minZ: base.z - 3, maxZ: base.z + 111,
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
      const x = base.x + 122 + i;                    // just outside the east wall, onward
      if (i > 5 && Math.random() < 0.3) z += (Math.random() < 0.5 ? 1 : -1);  // gentle wander
      for (let dz = -1; dz <= 0; dz++) layPath(dim, x, z + dz);   // 2 wide
      yield;
    }
    let fz = z0;                                     // a fork peeling off to the north-east
    for (let i = 0; i < 14; i++) {
      const x = base.x + 132 + i;
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
    // Only NORMALLY-hostile mobs are turned away. A friendly resident that has
    // been provoked (fc_aggravated) is allowed to be hostile on the grounds, and
    // guards are always exempt so the guard/bounty mechanics keep working here.
    if (entityHasFamily(mob, "fc_friendly") || entityHasFamily(mob, "fc_guard")) continue;
    try { if (mob.hasTag("fc_aggravated")) continue; } catch { }
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
// Guild apprentice training — two apprentices spar inside the dueling ring
// while one Skill apprentice shoots the north target in the archery range.
// Assignments run only during daylight. Training component groups freeze normal
// random-stroll movement; this scheduler maintains position/facing and drives
// one-shot animation exchanges plus real, short-lived practice arrows.
// ---------------------------------------------------------------------------
const APPRENTICE_TYPES = [
  "fc:guild_apprentice_might",
  "fc:guild_apprentice_skill",
  "fc:guild_apprentice_will",
];
const TRAINING_TAGS = ["fc_train_ring_a", "fc_train_ring_b", "fc_train_range"];
let nextSparTick = 0;
let nextArcheryTick = 0;
let sparTurn = 0;
// Apprentices drill in intermittent SESSIONS instead of manning the ring all day:
// a short TRAIN window pins a sparring pair + an archer to the grounds, then a
// longer REST window empties the training areas and sends them to roam the halls.
// Tuned so the dueling ring / archery range are staffed only ~1/3 of daylight.
const TRAIN_SESSION_TICKS = 1200;             // ~60s drilling
const REST_SESSION_TICKS = 2400;              // ~120s roaming the halls
const TRAIN_CYCLE_TICKS = TRAIN_SESSION_TICKS + REST_SESSION_TICKS;
let lastTrainPhase = false;                   // were we drilling last pass?
// Scattered hall posts (guild-local) the dispersing apprentices return to when a
// session closes. These reuse existing NPC home tiles in the west complex, so
// they are guaranteed clear, walkable floor.
const GUILD_HALL_POSTS = [
  { x: 12, z: 42 }, { x: 16, z: 35 }, { x: 23, z: 42 },
  { x: 26, z: 24 }, { x: 42, z: 40 },
];

function guildApprentices(dim, base) {
  const centre = { x: base.x + 61, y: base.y + 1, z: base.z + 54 };
  const apprentices = [];
  for (const type of APPRENTICE_TYPES) {
    try {
      apprentices.push(...dim.getEntities({ type, location: centre, maxDistance: 100 }));
    } catch { }
  }
  return apprentices;
}

function localGuildPoint(base, point, yOffset = 1) {
  return { x: base.x + point.x, y: base.y + yOffset, z: base.z + point.z };
}

function distanceXZ(entity, point) {
  return Math.hypot(entity.location.x - point.x, entity.location.z - point.z);
}

function setTrainingRole(entity, role) {
  let tags = [];
  try { tags = entity.getTags(); } catch { }
  for (const tag of TRAINING_TAGS) {
    if (tag !== role && tags.includes(tag)) {
      try { entity.removeTag(tag); } catch { }
    }
  }
  if (!tags.includes(role)) {
    try { entity.addTag(role); } catch { }
    try { entity.triggerEvent("fc:guild_training_start"); } catch { }
  }
}

function clearTrainingRole(entity) {
  let hadRole = false;
  let tags = [];
  try { tags = entity.getTags(); } catch { }
  for (const tag of TRAINING_TAGS) {
    if (!tags.includes(tag)) continue;
    hadRole = true;
    try { entity.removeTag(tag); } catch { }
  }
  if (!hadRole) return;
  try { entity.triggerEvent("fc:guild_training_stop"); } catch { }
  try { entity.playAnimation("animation.npc.idle", { blendOutTime: 0.2 }); } catch { }
}

function lockTrainingPosition(entity, point, facing) {
  try {
    entity.teleport(point, { facingLocation: facing });
  } catch { }
}

function clearGuildRingScarecrows(dim, base) {
  if (world.getDynamicProperty("fc_guild_ring_scarecrows_removed")) return;
  const columns = [
    { x: GUILD.dueling.x - 2, z: GUILD.dueling.z - 2 },
    { x: GUILD.dueling.x + 2, z: GUILD.dueling.z + 2 },
    { x: GUILD.dueling.x + 2, z: GUILD.dueling.z - 2 },
  ];
  for (const column of columns) {
    for (let y = 1; y <= 3; y++) {
      try {
        const block = dim.getBlock({
          x: base.x + column.x,
          y: base.y + y,
          z: base.z + column.z,
        });
        if (block?.typeId === "minecraft:hay_block"
          || block?.typeId === "minecraft:carved_pumpkin") {
          block.setType("minecraft:air");
        }
      } catch { }
    }
  }
  world.setDynamicProperty("fc_guild_ring_scarecrows_removed", true);
}

function repairGuildDemonApproach(dim, base) {
  if (world.getDynamicProperty("fc_guild_demon_approach_v2")) return;
  let complete = true;
  const setCobble = (x, z, clearHeadroom) => {
    try {
      const ground = dim.getBlock({
        x: base.x + x,
        y: base.y,
        z: base.z + z,
      });
      if (!ground) {
        complete = false;
        return;
      }
      ground.setType((x + z) % 4 === 0
        ? "minecraft:mossy_cobblestone"
        : "minecraft:cobblestone");
      if (!clearHeadroom) return;
      const headroom = dim.getBlock({
        x: base.x + x,
        y: base.y + 1,
        z: base.z + z,
      });
      if (headroom) headroom.setType("minecraft:air");
      else complete = false;
    } catch { complete = false; }
  };

  const bridgeX = GUILD.demon.x - 1;
  const bridgeZ = 84;
  const pathLength = GUILD.demon.z - 1 - bridgeZ;
  for (let z = bridgeZ; z < GUILD.demon.z; z++) {
    const x = Math.round(bridgeX
      + (GUILD.demon.x - bridgeX) * (z - bridgeZ) / pathLength);
    for (const pathX of [x, x + 1]) {
      setCobble(pathX, z, z > bridgeZ + 1);
    }
  }

  // Join the east-bank cobblestone network to the bridge's bank-side apron.
  const bankX = GUILD.demon.x + 9;
  const bankZ = 76;
  const eastPathX = GUILD.demon.x + 16;
  const eastPathZ = 80;
  const eastSteps = Math.max(Math.abs(eastPathX - (bankX + 2)),
    Math.abs(eastPathZ - bankZ), 1);
  for (let i = 0; i <= eastSteps; i++) {
    const x = Math.round(eastPathX + (bankX + 2 - eastPathX) * i / eastSteps);
    const z = Math.round(eastPathZ + (bankZ - eastPathZ) * i / eastSteps);
    for (let dx = 0; dx <= 1; dx++) {
      for (let dz = 0; dz <= 1; dz++) {
        setCobble(x + dx, z + dz, true);
      }
    }
  }

  // Remove only the island scarecrow closest to the Demon Door.
  const scarecrowX = GUILD.demon.x - 3;
  const scarecrowZ = GUILD.demon.z - 9;
  const parts = [
    { x: scarecrowX, y: 1, z: scarecrowZ, type: "minecraft:oak_fence" },
    { x: scarecrowX, y: 2, z: scarecrowZ, type: "minecraft:hay_block" },
    { x: scarecrowX, y: 3, z: scarecrowZ, type: "minecraft:carved_pumpkin" },
    { x: scarecrowX, y: 2, z: scarecrowZ - 1, type: "minecraft:oak_fence" },
    { x: scarecrowX, y: 2, z: scarecrowZ + 1, type: "minecraft:oak_fence" },
  ];
  for (const part of parts) {
    try {
      const block = dim.getBlock({
        x: base.x + part.x,
        y: base.y + part.y,
        z: base.z + part.z,
      });
      if (!block) {
        complete = false;
        continue;
      }
      if (block?.typeId === part.type) block.setType("minecraft:air");
    } catch { complete = false; }
  }
  if (complete) world.setDynamicProperty("fc_guild_demon_approach_v2", true);
}

let guildSkirtVegetationRepairRunning = false;
let guildTerrainRepairRunning = false;

function guildCaveColumn(base, x, z) {
  return x >= base.x + GUILD.cave.x0 && x <= base.x + GUILD.cave.x1
    && z >= base.z + GUILD.cave.z0 && z <= base.z + GUILD.cave.z1;
}

// Foundation first, skirt second. The delay gives newly-added ticking areas
// time to load their outer chunks before the grading scan starts.
function settleGuildTerrain(dim, base) {
  if (world.getDynamicProperty("fc_guild_terrain_v3") || guildTerrainRepairRunning) return;
  guildTerrainRepairRunning = true;
  const grade = () => {
    blendTerrain(dim, base.x, base.y, base.z, GUILD.sx, GUILD.sz,
      (x, z) => guildCaveColumn(base, x, z),
      () => skirtTerrain(dim, base.x, base.y, base.z, GUILD.sx, GUILD.sz, GUILD_TERRAIN_RADIUS, () => {
        world.setDynamicProperty("fc_guild_terrain_v2", true);
        world.setDynamicProperty("fc_guild_terrain_v3", true);
        world.setDynamicProperty("fc_guild_skirt_veg_v1", true);
        guildTerrainRepairRunning = false;
        guildSkirtVegetationRepairRunning = false;
        populateSurroundings(dim, base, true);
      }));
  };
  system.runTimeout(() => {
    if (world.getDynamicProperty("fc_guild_terrain_v2")) {
      repairLegacyGuildOcean(dim, base, grade);
    } else {
      grade();
    }
  }, 20);
}

// Upgrade already-generated worlds in place; the Guild does not need to be
// deleted and recreated for the foundation and surrounding grade to be fixed.
function repairGuildTerrain(dim, base) {
  if (world.getDynamicProperty("fc_guild_terrain_v3") || guildTerrainRepairRunning) return;
  const p = world.getPlayers().find((player) => player.dimension.id === dim.id);
  if (!forceLoadGuild(dim, p, base)) return;
  settleGuildTerrain(dim, base);
}

// Worlds generated before the skirt cleanup retained the original mountain
// trees after their supporting terrain was carved away. Clear vegetation from
// the reshaped inner apron once, then plant a fresh grounded transition layer.
function repairGuildSkirtVegetation(dim, base) {
  if (world.getDynamicProperty("fc_guild_skirt_veg_v1")
    || guildSkirtVegetationRepairRunning || guildTerrainRepairRunning) return;
  guildSkirtVegetationRepairRunning = true;
  const radius = 28;
  const maxX = base.x + GUILD.sx - 1;
  const maxZ = base.z + GUILD.sz - 1;
  const hi = Math.min(250, base.y + 80);
  const lo = Math.max(-60, base.y - 4);
  const work = function* () {
    for (let x = base.x - radius; x <= maxX + radius; x++) {
      for (let z = base.z - radius; z <= maxZ + radius; z++) {
        const cx = Math.max(base.x, Math.min(maxX, x));
        const cz = Math.max(base.z, Math.min(maxZ, z));
        const dist = Math.hypot(x - cx, z - cz);
        if (dist < 1 || dist > radius - 2) continue;
        clearSkirtCover(dim, x, z, lo, hi);
        yield;
      }
      yield;
    }
    world.setDynamicProperty("fc_guild_skirt_veg_v1", true);
    guildSkirtVegetationRepairRunning = false;
    populateSurroundings(dim, base, true);
  };
  try {
    system.runJob(work());
  } catch {
    guildSkirtVegetationRepairRunning = false;
  }
}

function playSparExchange(attacker, defender) {
  try { attacker.playAnimation("animation.npc.spar", { blendOutTime: 0.15 }); } catch { }
  try { defender.playAnimation("animation.npc.block", { blendOutTime: 0.15 }); } catch { }
  system.runTimeout(() => {
    try {
      const hit = {
        x: (attacker.location.x + defender.location.x) / 2,
        y: defender.location.y + 1.25,
        z: (attacker.location.z + defender.location.z) / 2,
      };
      defender.dimension.spawnParticle("minecraft:critical_hit_emitter", hit);
      defender.dimension.playSound("fc.sword_clash", hit, {
        volume: 0.35,
        pitch: 1.05 + Math.random() * 0.12,
      });
    } catch { }
  }, 8);
}

function firePracticeArrow(archer, target) {
  try {
    const origin = {
      x: archer.location.x,
      y: archer.location.y + 1.35,
      z: archer.location.z,
    };
    const dx = target.x - origin.x;
    const dy = target.y - origin.y;
    const dz = target.z - origin.z;
    const length = Math.max(0.001, Math.hypot(dx, dy, dz));
    const speed = 1.45;
    const arrow = archer.dimension.spawnEntity("minecraft:arrow", origin);
    arrow.addTag("fc_training_arrow");
    const projectile = arrow.getComponent("minecraft:projectile");
    if (projectile) {
      projectile.owner = archer;
      projectile.shoot({
        x: dx / length * speed,
        y: dy / length * speed + 0.035,
        z: dz / length * speed,
      });
    }
    archer.dimension.playSound("random.bow", origin, { volume: 0.45, pitch: 1.1 });
    system.runTimeout(() => { try { arrow.remove(); } catch { } }, 60);
  } catch { }
}

system.runInterval(() => {
  const bounds = guildBounds();
  if (!bounds || !world.getDynamicProperty("fc_guild_placed")) return;
  const dim = OW();
  const base = bounds.base;
  clearGuildRingScarecrows(dim, base);
  repairGuildDemonApproach(dim, base);
  repairGuildTerrain(dim, base);
  repairGuildSkirtVegetation(dim, base);
  const apprentices = guildApprentices(dim, base);
  if (!apprentices.length) return;

  // Combat overrides the daytime training script. Without this, the scheduler
  // immediately re-applies movement=0 and teleports aggravated apprentices back
  // to their marks while they are trying to defend the Guild.
  const available = [];
  for (const apprentice of apprentices) {
    let aggravated = false;
    try { aggravated = apprentice.hasTag("fc_aggravated"); } catch { }
    if (aggravated) clearTrainingRole(apprentice);
    else available.push(apprentice);
  }

  const time = world.getTimeOfDay();
  const daylight = time >= 0 && time < 12000;
  // Intermittent drilling: a TRAIN window pins the sparring pair + archer to the
  // grounds; a REST window (or night) releases everyone. On the closing edge of a
  // session, the apprentices who were drilling are walked back to scattered hall
  // posts so the campus — not the dueling ring — is where most of the Guild lives.
  const training = daylight && (TICKS() % TRAIN_CYCLE_TICKS) < TRAIN_SESSION_TICKS;
  const sessionEnded = lastTrainPhase && !training;
  lastTrainPhase = training;
  if (!training) {
    let dispersed = 0;
    const centre = { x: base.x + 61, y: base.y + 1, z: base.z + 54 };
    for (const apprentice of available) {
      let onMark = false;
      try { onMark = TRAINING_TAGS.some((t) => apprentice.hasTag(t)); } catch { }
      clearTrainingRole(apprentice);
      if (sessionEnded && onMark) {
        const post = GUILD_HALL_POSTS[dispersed++ % GUILD_HALL_POSTS.length];
        lockTrainingPosition(apprentice, localGuildPoint(base, post), centre);
      }
    }
    return;
  }

  const ringA = localGuildPoint(base, GUILD.training.ringA);
  const ringB = localGuildPoint(base, GUILD.training.ringB);
  const range = localGuildPoint(base, GUILD.training.range);
  const target = localGuildPoint(base, GUILD.training.target, 2.45);

  const skill = available
    .filter((entity) => entity.typeId === "fc:guild_apprentice_skill")
    .sort((a, b) => distanceXZ(a, range) - distanceXZ(b, range))[0];
  const fighterPool = available
    .filter((entity) => entity.id !== skill?.id)
    .sort((a, b) => {
      const aMight = a.typeId === "fc:guild_apprentice_might" ? 0 : 1;
      const bMight = b.typeId === "fc:guild_apprentice_might" ? 0 : 1;
      return aMight - bMight || distanceXZ(a, ringA) - distanceXZ(b, ringA);
    });
  const fighterA = fighterPool[0];
  const fighterB = fighterPool[1];
  const selected = new Set([fighterA?.id, fighterB?.id, skill?.id].filter(Boolean));

  for (const apprentice of apprentices) {
    if (!selected.has(apprentice.id)) clearTrainingRole(apprentice);
  }
  if (fighterA && fighterB) {
    setTrainingRole(fighterA, "fc_train_ring_a");
    setTrainingRole(fighterB, "fc_train_ring_b");
    lockTrainingPosition(fighterA, ringA, ringB);
    lockTrainingPosition(fighterB, ringB, ringA);
    if (TICKS() >= nextSparTick) {
      playSparExchange(sparTurn === 0 ? fighterA : fighterB,
        sparTurn === 0 ? fighterB : fighterA);
      sparTurn = 1 - sparTurn;
      nextSparTick = TICKS() + 36;
    }
  }
  if (skill) {
    setTrainingRole(skill, "fc_train_range");
    lockTrainingPosition(skill, range, target);
    if (TICKS() >= nextArcheryTick) {
      try { skill.playAnimation("animation.npc.archery_shot", { blendOutTime: 0.15 }); } catch { }
      system.runTimeout(() => {
        let tags = [];
        try { tags = skill.getTags(); } catch { }
        if (tags.includes("fc_train_range") && world.getTimeOfDay() < 12000) {
          firePracticeArrow(skill, target);
        }
      }, 16);
      nextArcheryTick = TICKS() + 58;
    }
  }
}, 10);

// ---------------------------------------------------------------------------
// GUILD ROSTER — the Guild's residents are persistent (the distance-despawn was
// removed in gen_behavior), but this restores any that were lost before that fix
// or that a build hiccup never spawned. Runs only while a Hero is on the grounds
// (so a wedded apprentice following the Hero elsewhere is never duplicated), and
// counts the force-loaded campus, respawning only the shortfall at home posts.
// ---------------------------------------------------------------------------
const GUILD_ROSTER = [
  { type: "fc:guildmaster", homes: [{ x: 23, z: 42 }] },
  { type: "fc:maze", homes: [{ x: GUILD.maze.x, y: GUILD.maze.studyY, z: GUILD.maze.z }] },
  { type: "fc:theresa", homes: [{ x: 26, z: 23 }] },
  { type: "fc:trader", homes: [{ x: 5, z: 46 }] },
  { type: "fc:guard_bowerstone", tag: "fc_guild_guard", homes: [{ x: 10, z: 39 }, { x: 10, z: 45 }] },
  { type: "fc:guild_apprentice_might", homes: [{ x: 12, z: 42 }, { x: GUILD.dueling.x, z: GUILD.dueling.z }] },
  { type: "fc:guild_apprentice_skill", homes: [{ x: GUILD.archery.x, z: GUILD.archery.z }, { x: 42, z: 40 }] },
  { type: "fc:guild_apprentice_will", homes: [{ x: 26, z: 24 }, { x: 16, z: 35 }] },
];
system.runInterval(() => {
  const b = guildBounds();
  if (!b || !world.getDynamicProperty("fc_guild_placed")) return;
  if (!world.getPlayers().some((p) => isInsideGuild(p.location, p.dimension.id))) return;
  const dim = OW();
  const base = b.base;
  const centre = { x: base.x + 61, y: base.y + 1, z: base.z + 54 };
  for (const entry of GUILD_ROSTER) {
    let present = 0;
    try {
      const query = { type: entry.type, location: centre, maxDistance: 140 };
      if (entry.tag) query.tags = [entry.tag];
      present = dim.getEntities(query).length;
    } catch { continue; }
    for (let i = present; i < entry.homes.length; i++) {
      const h = entry.homes[i];
      const e = trySpawn(dim, entry.type, { x: base.x + h.x, y: base.y + (h.y ?? 1), z: base.z + h.z });
      if (e) {
        try { e.addTag("fc_guild_npc"); } catch { }
        try { if (entry.tag) e.addTag(entry.tag); } catch { }
      }
    }
  }
}, 200);

// ---------------------------------------------------------------------------
// Combat multiplier + kill XP + morality + augment effects
// ---------------------------------------------------------------------------
world.afterEvents.entityHitEntity.subscribe((ev) => {
  const src = ev.damagingEntity, tgt = ev.hitEntity;
  if (src?.typeId !== "minecraft:player" || !tgt) return;
  const p = src;
  // combat multiplier
  const multiplier = P.add(p, "fc_mult", 1);
  P.set(p, "fc_lastHit", TICKS());
  if (!currentBounty(p)) {
    showHeroActionBar(p, `§6⚔ Combat Multiplier §f×${multiplier}`, 15);
  }
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
  if (!e) return;
  if (e.typeId !== "minecraft:player") {
    let attacker = ev.damageSource?.damagingEntity;
    if (attacker?.typeId !== "minecraft:player" && ev.damageSource?.damagingProjectile) {
      try {
        attacker = ev.damageSource.damagingProjectile
          .getComponent("minecraft:projectile")?.owner;
      } catch { }
    }
    // Use the damage event rather than the melee-only hit event so arrows, Will
    // powers and other scripted player damage also alert local protectors.
    if (attacker?.typeId === "minecraft:player") handlePlayerAssault(attacker, e);
    return;
  }
  // taking damage resets the multiplier — Fable rules
  if (ev.damage > 0) {
    const prior = P.get(e, "fc_mult", 0);
    P.set(e, "fc_mult", 0);
    if (prior > 0 && !currentBounty(e)) {
      showHeroActionBar(e, "§c⚔ Combat Multiplier broken");
    }
  }
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
  // A killing blow is the gravest crime — towns AND the Heroes' Guild answer it.
  accrueCrime(p, dead, "kill");
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
    // Will & Destiny (Phase 2): the storybook Hero Menu. Its deep ledger pages
    // fall back to the legacy heroMenu via menu_bridge.js.
    return wdOpenHeroMenu(p);
  }
  if (id === "fc:quest_card") return questBoard(p);
  // Will & Destiny (Phase 2): spell tomes are consumed to permanently learn a
  // power (wd/learn.js) and the Will Focus charge/cast is handled by
  // wd/quickcast.js. Both subscribe to itemUse directly, so no branch here.
  if (ORB_XP[id]) {
    const [type, amt] = ORB_XP[id];
    removeItem(p, id, 1);
    giveXp(p, type, amt);
    p.playSound("random.orb", { pitch: 1.2 });
    try { p.dimension.spawnParticle("minecraft:villager_happy", { x: p.location.x, y: p.location.y + 1.6, z: p.location.z }); } catch { }
    showHeroActionBar(p, `${XP_COLOR[type]}✦ +${amt} ${type} experience absorbed`);
    return;
  }
  if (DATA.augments[id]) return applyAugment(p, it, DATA.augments[id]);
  if (id === "fc:augment_remover") return removeAugments(p);
  // fc:summoners_grimoire is now a learn-tome for Summon (wd/learn.js).
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

// Expose the legacy ledgers to the storybook Hero Menu (wd/herobook.js). These
// are hoisted function declarations, so the bridge resolves them at click time.
LEGACY_MENU.heroMenu = heroMenu;
LEGACY_MENU.recall = recallToGuild;

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
  learnWillSpell(p, id);
  const m = morality(p);
  if (s.align > 0 && m < 100) return p.sendMessage("§7Your soul is not pure enough for this Will power.");
  if (s.align < 0 && m > -100) return p.sendMessage("§7Your soul is not dark enough for this Will power.");
  const key = `${p.id}|${id}`;
  const last = spellCd.get(key) ?? -99999;
  const lvl = spellLevel(p, id);
  const cd = Math.max(10, s.cd - lvl * 5);
  if (TICKS() - last < cd) {
    return showHeroActionBar(p, "§b…the Will is still gathering…");
  }
  // good spells cost more for evil heroes and vice versa
  let cost = s.will;
  if (s.align > 0 && m < 0) cost = Math.round(cost * 1.5);
  if (s.align < 0 && m > 0) cost = Math.round(cost * 1.5);
  if (!spendWill(p, cost)) return showHeroActionBar(p, "§9Not enough Will energy.");
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
      showHeroActionBar(p, "§6The fireball scorches the ground ahead.");
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
    if (!struck) showHeroActionBar(p, "§9The arc finds no target.");
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
    if (!tgt) return showHeroActionBar(p, "§9No target in sight.");
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
    if (!tgt) return showHeroActionBar(p, "§9No mind to bend.");
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
    showHeroActionBar(p, "§6Your blade blurs with impossible speed!");
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
    ? `§e◈ ${q.name} §8(${q.objectives.filter((o, i) => (o.type === "collect" ? countItem(p, o.item) : aq.progress[i]) >= o.count).length}/${q.objectives.length})`
    : "§7◈ No active Quest Card";
  const f = new ActionFormData()
    .title(fableTitle("Hero of Albion"))
    .body(fableBody([
      `§6${activeTitle(p) || "Hero"} §8· ${moralityTitle(p)}`,
      questLine,
      `§cHealth §f${Math.ceil(p.getComponent("minecraft:health")?.currentValue ?? 0)}  §8·  §bWill §f${willEnergy(p)}/${maxWill(p)}`,
      `§dRenown §f${P.get(p, "fc_renown", 0)}  §8·  §6Gold §f${countItem(p, "fc:gold_coin")}  §8·  §cPhials §f${countItem(p, "fc:resurrection_phial")}`,
      `§6Combat Multiplier §f×${P.get(p, "fc_mult", 0)}`,
      "§8The Guild Seal contains Albion's book of record.",
    ]))
    .button("§6Items", "textures/items/health_potion")
    .button("§cWeapons", "textures/items/iron_longsword")
    .button("§9Magic", "textures/items/spell_fireball")
    .button("§7Clothing", "textures/items/apprentice_torso")
    .button("§dExpressions", "textures/items/wedding_ring")
    .button("§eQuests", "textures/items/quest_card")
    .button("§2Stats", "textures/items/guild_seal")
    .button("§6Logbook", "textures/items/summoners_grimoire")
    .button("§bMap", "textures/items/septimal_key");
  f.show(p).then((r) => {
    if (r.canceled) return;
    [
      itemsMenu, weaponLockerMenu, magicMenu, clothingMenu, expressionsMenu,
      questJournalMenu, statsMenu, logbookMenu, mapMenu,
    ][r.selection]?.(p);
  }).catch(() => { });
}

function inventoryEntries(p, predicate) {
  const c = inv(p);
  const entries = [];
  if (!c) return entries;
  for (let slot = 0; slot < c.size; slot++) {
    const item = c.getItem(slot);
    if (item && predicate(item)) entries.push({ slot, item });
  }
  return entries;
}

function moveSlotToHand(p, slot) {
  const c = inv(p);
  if (!c) return;
  const selected = p.selectedSlotIndex ?? 0;
  if (slot === selected) return;
  const chosen = c.getItem(slot);
  const current = c.getItem(selected);
  c.setItem(selected, chosen);
  c.setItem(slot, current);
}

function customItemKind(id) {
  if (DATA.consumables[id]) return "Provisions";
  if (DATA.augments[id] || id === "fc:augment_remover") return "Augments";
  if (id.startsWith("fc:orb_")) return "Experience Orbs";
  return "Quest & Other";
}

function itemsMenu(p) {
  const entries = inventoryEntries(p, (item) => (item.typeId.startsWith("fc:") || item.typeId.startsWith("wd:"))
    && !DATA.weapons[item.typeId] && !DATA.armor[item.typeId] && !item.typeId.startsWith("fc:spell_"));
  const groups = ["Provisions", "Augments", "Experience Orbs", "Quest & Other"];
  const f = new ActionFormData().title(fableTitle("Items")).body(fableBody([
    "§7Select a page of your inventory.",
    `§8${entries.length} Fablecraft stacks carried`,
  ]));
  for (const group of groups) {
    const count = entries.filter(({ item }) => customItemKind(item.typeId) === group)
      .reduce((sum, { item }) => sum + item.amount, 0);
    f.button(`§6${group}\n§8${count} carried`);
  }
  f.button("§8Back");
  f.show(p).then((r) => {
    if (r.canceled) return;
    if (r.selection >= groups.length) return heroMenu(p);
    itemCategoryMenu(p, groups[r.selection]);
  }).catch(() => { });
}

function itemCategoryMenu(p, group) {
  const entries = inventoryEntries(p, (item) => (item.typeId.startsWith("fc:") || item.typeId.startsWith("wd:"))
    && customItemKind(item.typeId) === group
    && !DATA.weapons[item.typeId] && !DATA.armor[item.typeId] && !item.typeId.startsWith("fc:spell_"));
  const f = new ActionFormData().title(fableTitle(group)).body(fableBody([
    entries.length ? "§7Choose an item to use or ready." : "§8This page is empty.",
  ]));
  for (const { item } of entries) {
    f.button(`§f${displayName(item.typeId)}\n§8${item.amount} carried`,
      `textures/items/${item.typeId.replace(/^(fc|wd):/, "")}`);
  }
  f.button("§8Back");
  f.show(p).then((r) => {
    if (r.canceled) return;
    if (r.selection >= entries.length) return itemsMenu(p);
    itemActionMenu(p, entries[r.selection], group);
  }).catch(() => { });
}

function itemActionMenu(p, entry, group) {
  const { item, slot } = entry;
  const f = new ActionFormData().title(fableTitle(displayName(item.typeId)))
    .body(fableBody([`§7Quantity: §f${item.amount}`, `§8${group}`]));
  const actions = [];
  if (DATA.consumables[item.typeId] || item.typeId.startsWith("fc:orb_")) {
    actions.push({ label: "§aUse one", run: () => useInventoryItem(p, item.typeId) });
  }
  if (item.typeId === "fc:quest_card") actions.push({ label: "§eRead Quest Cards", run: () => questBoard(p) });
  if (DATA.augments[item.typeId]) actions.push({ label: "§6Open Augmentation Forge", run: () => applyAugment(p, item, DATA.augments[item.typeId]) });
  if (item.typeId === "fc:augment_remover") actions.push({ label: "§6Strip a weapon", run: () => removeAugments(p) });
  if (item.typeId === "fc:summoners_grimoire") actions.push({ label: "§9Cast Summon", run: () => castSpell(p, "summon", true) });
  actions.push({ label: "§fMove to active hotbar slot", run: () => { moveSlotToHand(p, slot); itemCategoryMenu(p, group); } });
  for (const action of actions) f.button(action.label);
  f.button("§8Back");
  f.show(p).then((r) => {
    if (r.canceled) return;
    if (r.selection >= actions.length) return itemCategoryMenu(p, group);
    actions[r.selection].run();
  }).catch(() => { });
}

function useInventoryItem(p, id) {
  const c = DATA.consumables[id];
  if (c) {
    if (!removeItem(p, id, 1)) return;
    if (c.heal) healPlayer(p, c.heal);
    if (c.will) P.set(p, "fc_will", Math.min(maxWill(p), willEnergy(p) + c.will));
    if (c.food) p.addEffect("saturation", 2, { amplifier: Math.max(0, c.food - 1), showParticles: false });
    if (c.morality) addMorality(p, c.morality);
    if (c.xp) giveXp(p, c.xp, c.xp_amount);
    if (c.max_hp) {
      P.add(p, "fc_bonus_hp", c.max_hp);
      p.sendMessage("§d✦ Your life force expands permanently.");
    }
    p.playSound(id.includes("potion") || id.includes("elixir") || id.includes("phial") ? "random.drink" : "random.eat");
    return itemsMenu(p);
  }
  if (ORB_XP[id]) {
    const [type, amount] = ORB_XP[id];
    if (!removeItem(p, id, 1)) return;
    giveXp(p, type, amount);
    p.playSound("random.orb", { pitch: 1.2 });
    showHeroActionBar(p, `${XP_COLOR[type]}✦ +${amount} ${type} experience absorbed`);
    return itemsMenu(p);
  }
}

function carriedWeapons(p) {
  return inventoryEntries(p, (item) => !!DATA.weapons[item.typeId]);
}

function weaponLockerMenu(p) {
  const weapons = carriedWeapons(p);
  const held = heldItem(p);
  const f = new ActionFormData().title(fableTitle("Weapons")).body(fableBody([
    held && DATA.weapons[held.typeId] ? `§6Drawn: §f${displayName(held.typeId)}` : "§7No Fable weapon drawn.",
    "§8Choose a weapon to inspect or equip.",
  ]));
  for (const { item } of weapons) {
    const data = DATA.weapons[item.typeId];
    const augments = weaponAugments(item);
    f.button(`${item.typeId === held?.typeId ? "§a● " : "§f"}${displayName(item.typeId)}\n§c${data.fable} damage §8· §6${augments.length}/${data.slots} augments`,
      `textures/items/${item.typeId.replace("fc:", "")}`);
  }
  f.button("§8Back");
  f.show(p).then((r) => {
    if (r.canceled) return;
    if (r.selection >= weapons.length) return heroMenu(p);
    weaponDetailMenu(p, weapons[r.selection]);
  }).catch(() => { });
}

function weaponDetailMenu(p, entry) {
  const data = DATA.weapons[entry.item.typeId];
  const augments = weaponAugments(entry.item);
  const lines = [
    `§cDamage: §f${data.fable}`,
    `§6Augment slots: §f${augments.length}/${data.slots}`,
    ...(augments.length ? augments.map((id) => `§6⬩ §f${DATA.augmentInfo?.[id]?.name ?? displayName(id)}`) : ["§8No powers bound."]),
  ];
  const f = new ActionFormData().title(fableTitle(displayName(entry.item.typeId)))
    .body(fableBody(lines))
    .button("§aEquip weapon")
    .button("§8Back");
  f.show(p).then((r) => {
    if (r.canceled) return;
    if (r.selection === 0) {
      moveSlotToHand(p, entry.slot);
      p.playSound("random.armor_equip_generic");
    }
    weaponLockerMenu(p);
  }).catch(() => { });
}

function magicMenu(p) {
  const owned = willOwnedSpells(p);
  const f = new ActionFormData().title(fableTitle("Magic")).body(fableBody([
    `§bWill: §f${willEnergy(p)}/${maxWill(p)}`,
    `§9Known powers: §f${owned.length}/${Object.keys(DATA.spells).length}`,
    "§8Learned powers stay available without occupying quick-cast inventory slots.",
  ]))
    .button("§9Will Powers & Upgrades", "textures/items/spell_fireball")
    .button("§bAttune Will Hotkeys", "textures/items/spell_lightning")
    .button("§dWill Focus", "textures/items/will_focus")
    .button("§8Back");
  f.show(p).then((r) => {
    if (r.canceled) return;
    if (r.selection === 0) return spellMenu(p);
    if (r.selection === 1) return willAttuneMenu(p);
    if (r.selection === 2) return willAttuneMenu(p);
    heroMenu(p);
  }).catch(() => { });
}

const ARMOR_EQUIPMENT = {
  helm: EquipmentSlot.Head,
  torso: EquipmentSlot.Chest,
  legs: EquipmentSlot.Legs,
  boots: EquipmentSlot.Feet,
};

function equipArmorEntry(p, entry) {
  const data = DATA.armor[entry.item.typeId];
  const equipmentSlot = data && ARMOR_EQUIPMENT[data.slot];
  const c = inv(p);
  const eq = p.getComponent("minecraft:equippable");
  if (!c || !eq || !equipmentSlot) return false;
  const chosen = c.getItem(entry.slot);
  if (!chosen || chosen.typeId !== entry.item.typeId) return false;
  const old = eq.getEquipment(equipmentSlot);
  c.setItem(entry.slot, undefined);
  eq.setEquipment(equipmentSlot, chosen);
  if (old) c.setItem(entry.slot, old);
  return true;
}

function equippedArmor(p) {
  const eq = p.getComponent("minecraft:equippable");
  if (!eq) return [];
  return Object.values(ARMOR_EQUIPMENT)
    .map((slot) => eq.getEquipment(slot))
    .filter((item) => item && DATA.armor[item.typeId]);
}

function clothingMenu(p) {
  const carried = inventoryEntries(p, (item) => !!DATA.armor[item.typeId]);
  const equipped = equippedArmor(p);
  const sets = new Map();
  for (const entry of carried) {
    const set = DATA.armor[entry.item.typeId].set;
    if (!sets.has(set)) sets.set(set, []);
    sets.get(set).push(entry);
  }
  const f = new ActionFormData().title(fableTitle("Clothing")).body(fableBody([
    `§7Equipped: §f${equipped.length}/4 pieces`,
    "§8Equip a whole suit or choose individual pieces.",
  ]));
  if (equipped.length) f.button("§7Unequip all clothing");
  for (const [set, entries] of sets) {
    const complete = new Set(entries.map(({ item }) => DATA.armor[item.typeId].slot)).size >= 4;
    f.button(`§f${displayName(set)}\n${complete ? "§aComplete suit" : `§8${entries.length} piece${entries.length === 1 ? "" : "s"}`}`,
      `textures/items/${entries[0].item.typeId.replace("fc:", "")}`);
  }
  f.button("§8Back");
  const setEntries = [...sets.entries()];
  f.show(p).then((r) => {
    if (r.canceled) return;
    let index = r.selection;
    if (equipped.length) {
      if (index === 0) {
        unequipAllClothing(p);
        return clothingMenu(p);
      }
      index--;
    }
    if (index >= setEntries.length) return heroMenu(p);
    clothingSetMenu(p, setEntries[index][0]);
  }).catch(() => { });
}

function unequipAllClothing(p) {
  const c = inv(p);
  const eq = p.getComponent("minecraft:equippable");
  if (!c || !eq) return;
  for (const slot of Object.values(ARMOR_EQUIPMENT)) {
    const item = eq.getEquipment(slot);
    if (!item) continue;
    const leftover = c.addItem(item);
    if (leftover) p.dimension.spawnItem(leftover, p.location);
    eq.setEquipment(slot, undefined);
  }
  p.playSound("random.armor_equip_generic", { pitch: 0.8 });
}

function clothingSetMenu(p, setId) {
  const entries = inventoryEntries(p, (item) => DATA.armor[item.typeId]?.set === setId);
  const f = new ActionFormData().title(fableTitle(displayName(setId))).body(fableBody([
    "§7Clothing records its attractiveness, scariness and moral character.",
  ]));
  const complete = new Set(entries.map(({ item }) => DATA.armor[item.typeId].slot)).size >= 4;
  if (complete) f.button("§aEquip complete suit");
  for (const entry of entries) {
    const data = DATA.armor[entry.item.typeId];
    f.button(`§f${displayName(entry.item.typeId)}\n§8${displayName(data.slot)}`,
      `textures/items/${entry.item.typeId.replace("fc:", "")}`);
  }
  f.button("§8Back");
  f.show(p).then((r) => {
    if (r.canceled) return;
    let index = r.selection;
    if (complete) {
      if (index === 0) {
        for (const entry of entries) equipArmorEntry(p, entry);
        p.playSound("random.armor_equip_generic");
        return clothingMenu(p);
      }
      index--;
    }
    if (index >= entries.length) return clothingMenu(p);
    if (equipArmorEntry(p, entries[index])) p.playSound("random.armor_equip_generic");
    clothingSetMenu(p, setId);
  }).catch(() => { });
}

const EXPRESSION_CATEGORIES = [
  ["friendly", "Friendly"],
  ["romantic", "Romantic"],
  ["funny", "Funny"],
  ["scary", "Scary"],
  ["rude", "Rude"],
  ["criminal", "Criminal"],
  ["oracle", "Oracle"],
];

function expressionsMenu(p) {
  const unlocked = new Set(refreshFableEmoteUnlocks(p));
  const f = new ActionFormData().title(fableTitle("Expressions")).body(fableBody([
    `§dLearned: §f${unlocked.size}/${FABLE_EMOTES.length}`,
    "§7Expressions affect nearby townsfolk and may perform special actions.",
  ]));
  for (const [id, label] of EXPRESSION_CATEGORIES) {
    const all = FABLE_EMOTES.filter((entry) => entry.category === id);
    const known = all.filter((entry) => unlocked.has(entry.id)).length;
    f.button(`§d${label}\n§8${known}/${all.length} learned`);
  }
  f.button("§8Back");
  f.show(p).then((r) => {
    if (r.canceled) return;
    if (r.selection >= EXPRESSION_CATEGORIES.length) return heroMenu(p);
    expressionCategoryMenu(p, EXPRESSION_CATEGORIES[r.selection][0], EXPRESSION_CATEGORIES[r.selection][1]);
  }).catch(() => { });
}

function expressionCategoryMenu(p, category, label) {
  const unlocked = new Set(refreshFableEmoteUnlocks(p));
  const entries = FABLE_EMOTES.filter((entry) => entry.category === category);
  const f = new ActionFormData().title(fableTitle(label)).body(fableBody([
    "§7Select an expression. Nearby people will react.",
  ]));
  for (const emote of entries) {
    const status = unlocked.has(emote.id) ? "§aLearned" : "§8Locked";
    f.button(`${unlocked.has(emote.id) ? "§f" : "§8"}${emote.name}\n${status}`);
  }
  f.button("§8Back");
  f.show(p).then((r) => {
    if (r.canceled) return;
    if (r.selection >= entries.length) return expressionsMenu(p);
    const emote = entries[r.selection];
    if (!unlocked.has(emote.id)) {
      performFableEmote(p, emote.id, { camera: false, react: false, functional: false });
      return expressionCategoryMenu(p, category, label);
    }
    performFableEmote(p, emote.id);
  }).catch(() => { });
}

function questJournalMenu(p) {
  const active = activeQuest(p);
  const done = doneQuests(p);
  const f = new ActionFormData().title(fableTitle("Quests")).body(fableBody([
    active ? `§eActive: §f${DATA.quests.find((q) => q.id === active.id)?.name ?? active.id}` : "§7No active quest.",
    `§6Completed: §f${done.length}/${DATA.quests.length}`,
  ]))
    .button("§eActive Quest", "textures/items/quest_card")
    .button("§6Available Quest Cards", "textures/items/quest_card")
    .button("§7Completed Quests", "textures/items/summoners_grimoire")
    .button("§8Back");
  f.show(p).then((r) => {
    if (r.canceled) return;
    if (r.selection === 0) return active ? questMenu(p) : questJournalMenu(p);
    if (r.selection === 1) return questBoard(p);
    if (r.selection === 2) return completedQuestsMenu(p);
    heroMenu(p);
  }).catch(() => { });
}

function completedQuestsMenu(p) {
  const done = doneQuests(p);
  const quests = DATA.quests.filter((q) => done.includes(q.id));
  const f = new ActionFormData().title(fableTitle("Quest History")).body(fableBody([
    quests.length ? "§7Albion remembers these deeds." : "§8No completed Quest Cards yet.",
  ]));
  for (const q of quests) f.button(`§a✔ §f${q.name}\n§8${q.giver} · ${q.renown} renown`);
  f.button("§8Back");
  f.show(p).then((r) => {
    if (r.canceled) return;
    if (r.selection >= quests.length) return questJournalMenu(p);
    const q = quests[r.selection];
    new ActionFormData().title(fableTitle(q.name))
      .body(fableBody([`§o"${q.desc}"`, `§dRenown earned: §f${q.renown}`]))
      .button("§8Back").show(p).then(() => completedQuestsMenu(p));
  }).catch(() => { });
}

function logbookMenu(p) {
  const f = new ActionFormData().title(fableTitle("Logbook")).body(fableBody([
    "§7A Guild reference for the systems active in this world.",
  ]))
    .button("§6Hero's Handbook")
    .button("§9Will & Quick-Cast")
    .button("§bCullis Gates")
    .button("§4Crime & Bounties")
    .button("§aFactions & Standing")
    .button("§dTitles & Renown")
    .button("§cGuild Training")
    .button("§8Back");
  const pages = [
    ["Hero's Handbook", [
      "Use the Guild Seal to open this book.",
      "Sneak-use the Seal to recall to the Heroes' Guild.",
      "Use Quest Cards or the Guild lecterns to accept work.",
      "Experience is divided into General, Strength, Skill and Will.",
    ]],
    ["Will & Quick-Cast", [
      "Spell tomes cast their bound power when used.",
      "Attune three virtual powers, then cast with Sneak + 7, 8 or 9.",
      "These bindings do not replace the items in your hotbar.",
      "The Will Focus casts the active power; sneak-use it to attune.",
    ]],
    ["Cullis Gates", [
      "Discovered Focus Sites join the Cullis lattice.",
      "Stand on a gate and sneak, or choose Map from the Guild Seal.",
      "TLC navigation uses destinations and quest markers—not a golden trail.",
    ]],
    ["Crime & Bounties", [
      "Witnessed murder creates a settlement-specific bounty.",
      "Guards may demand payment, jail, or resistance.",
      "Leave the region long enough and its warrant expires.",
    ]],
  ];
  f.show(p).then((r) => {
    if (r.canceled) return;
    if (r.selection < pages.length) return logbookPage(p, pages[r.selection][0], pages[r.selection][1]);
    if (r.selection === 4) return factionMenu(p);
    if (r.selection === 5) return titlesMenu(p);
    if (r.selection === 6) return trainMenu(p);
    heroMenu(p);
  }).catch(() => { });
}

function logbookPage(p, title, lines) {
  new ActionFormData().title(fableTitle(title)).body(fableBody(lines.map((line) => `§7${line}`)))
    .button("§8Back").show(p).then(() => logbookMenu(p)).catch(() => { });
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
      .show(p).then((r) => { if (!r.canceled) heroMenu(p); }).catch(() => { });
    return;
  }
  const f = new ActionFormData().title(fableTitle("Map of Albion"))
    .body(fableBody([
      "§7The Cullis lattice bends Albion to your Will.",
      "§8Travel is destination-based; there is no breadcrumb trail.",
    ]))
    .button("§9Recall to the Heroes' Guild", "textures/items/guild_seal");
  for (const s of sites) {
    const d = Math.round(Math.hypot(p.location.x - s.x, p.location.z - s.z));
    f.button(`§b◈ ${s.name}\n§8${d}m distant`, "textures/items/septimal_key");
  }
  f.button("§8❖ Back");
  f.show(p).then((r) => {
    if (r.canceled) return;
    if (r.selection === 0) return recallToGuild(p);
    if (r.selection > sites.length) return heroMenu(p);
    const s = sites[r.selection - 1];
    try { p.dimension.spawnParticle("minecraft:huge_explosion_emitter", p.location); } catch { }
    p.playSound("fc.spell_cast", { pitch: 0.6 });
    p.teleport({ x: s.x + 0.5, y: s.y + 1, z: s.z + 0.5 });
    p.playSound("mob.endermen.portal");
    showHeroTitle(p, "§b◈", { fadeInDuration: 2, stayDuration: 16, fadeOutDuration: 8, subtitle: `§f${s.name}` });
  }).catch(() => { });
}

function bar(v, max, color, width = 20) {
  const fill = Math.max(0, Math.min(width, Math.round((v / max) * width)));
  return color + "█".repeat(fill) + "§8" + "░".repeat(width - fill);
}

function statsMenu(p) {
  const m = morality(p);
  const worn = equippedArmor(p);
  const attractiveness = worn.reduce((sum, item) => sum + (DATA.armor[item.typeId]?.attract ?? 0), 0);
  const scariness = worn.reduce((sum, item) => sum + (DATA.armor[item.typeId]?.scary ?? 0), 0);
  const time = world.getTimeOfDay();
  const hour = Math.floor(((time + 6000) % 24000) / 1000);
  const minute = Math.floor((((time + 6000) % 1000) / 1000) * 60);
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
    `§d ◈ Renown: §f${P.get(p, "fc_renown", 0)} §8· title: §e${activeTitle(p) || "none"}`,
    `§d ◈ Attractiveness: §f${attractiveness}`,
    `§4 ◈ Scariness: §f${scariness}`,
    `§d ◈ Marital status: §f${P.get(p, "fc_married", false) ? "Married to Lady Grey" : "Unmarried"}`,
    `§7 ◈ Albion time: §f${String(hour).padStart(2, "0")}:${String(minute).padStart(2, "0")}`,
    FABLE_RULE,
    `§a ◈ General XP: §f${P.get(p, "fc_xp_general", 0)}`,
    `§c ◈ Strength XP: §f${P.get(p, "fc_xp_strength", 0)}`,
    `§9 ◈ Skill XP: §f${P.get(p, "fc_xp_skill", 0)}`,
    `§e ◈ Will XP: §f${P.get(p, "fc_xp_will", 0)}`,
    "",
    `§b ◈ Will Energy: ${bar(willEnergy(p), maxWill(p), "§b")} §f${willEnergy(p)}/${maxWill(p)}`,
    `§6 ◈ Combat Multiplier: §f${P.get(p, "fc_mult", 0)}`,
    FABLE_RULE,
    "§7Guild disciplines:",
    ...Object.values(DATA.upgrades).map((u) => `  §f${u.name}: §6${"◆".repeat(P.get(p, `fc_up_${u.id}`, 0))}§8${"◇".repeat(u.max - P.get(p, `fc_up_${u.id}`, 0))}`),
  ];
  new ActionFormData().title(fableTitle("Stats · Personality")).body(lines.join("\n"))
    .button("§cGuild Training")
    .button("§dTitles & Renown")
    .button("§aFactions & Bounties")
    .button("§8Back")
    .show(p).then((r) => {
      if (r.canceled) return;
      if (r.selection === 0) return trainMenu(p);
      if (r.selection === 1) return titlesMenu(p);
      if (r.selection === 2) return factionMenu(p);
      heroMenu(p);
    }).catch(() => { });
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
    ...bountySummaryLines(p),
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
  const f = new ActionFormData().title(fableTitle("Will Powers")).body(fableBody([
    `§bWill energy: §f${willEnergy(p)}/${maxWill(p)}`,
    `§eWill experience: §f${P.get(p, "fc_xp_will", 0)}`,
    "§8Learn powers by finding their spell tomes.",
  ]));
  const ids = Object.keys(DATA.spells);
  for (const id of ids) {
    const s = DATA.spells[id];
    const lvl = spellLevel(p, id);
    const owned = willOwnedSpells(p).includes(id);
    const alignTag = s.align > 0 ? " §e[Good]" : s.align < 0 ? " §5[Evil]" : "";
    f.button(`${owned ? "§b❖ " : "§8◇ "}${s.name}${alignTag} ${owned ? `§7Lv${lvl}` : "§8Locked"}\n§8${s.will} Will${owned ? ` · upgrade ${lvl * 150} XP` : ""}`);
  }
  f.button("§b⚡ Attune Will Hotkeys", "textures/items/spell_fireball");
  f.button("§8❖ Back");
  f.show(p).then((r) => {
    if (r.canceled) return;
    if (r.selection === ids.length) return willAttuneMenu(p);
    if (r.selection > ids.length) return magicMenu(p);
    const id = ids[r.selection];
    const lvl = spellLevel(p, id);
    if (!willOwnedSpells(p).includes(id)) {
      p.sendMessage(`§7Find the ${DATA.spells[id].name} spell tome before training this power.`);
      return spellMenu(p);
    }
    if (lvl >= 4) { p.sendMessage("§7This Will power is already mastered."); return spellMenu(p); }
    const cost = lvl * 150;
    if (P.get(p, "fc_xp_will", 0) < cost) { p.sendMessage(`§7You need ${cost} Will XP to deepen this power.`); return spellMenu(p); }
    P.add(p, "fc_xp_will", -cost);
    P.set(p, `fc_spell_lvl_${id}`, lvl + 1);
    p.playSound("fc.level_up", { pitch: 1.3 });
    p.sendMessage(`§9✦ ${DATA.spells[id].name} flows stronger (level ${lvl + 1}).`);
    spellMenu(p);
  }).catch(() => { });
}

// ---------------------------------------------------------------------------
// WILL QUICK-CAST — learned powers and the three attuned slots are virtual.
// Sneak + hotbar keys 7/8/9 casts the matching power without replacing the
// item stored in that hotbar slot. The Will Focus casts the active slot.
// ---------------------------------------------------------------------------
function learnWillSpell(p, id) {
  if (!DATA.spells[id]) return false;
  const known = P.getJ(p, "fc_will_known", []);
  if (known.includes(id)) return false;
  known.push(id);
  P.setJ(p, "fc_will_known", known);
  return true;
}

function learnInventoryWillSpells(p) {
  const c = inv(p);
  if (!c) return;
  const known = P.getJ(p, "fc_will_known", []);
  const found = new Set(known);
  let changed = false;
  for (let slot = 0; slot < c.size; slot++) {
    const item = c.getItem(slot);
    if (!item?.typeId.startsWith("fc:spell_")) continue;
    const id = item.typeId.substring("fc:spell_".length);
    if (!DATA.spells[id] || found.has(id)) continue;
    found.add(id);
    changed = true;
  }
  if (changed) P.setJ(p, "fc_will_known", [...found]);
}

function willOwnedSpells(p) {
  learnInventoryWillSpells(p);
  return P.getJ(p, "fc_will_known", []).filter((id) => !!DATA.spells[id]);
}

function normalizedWillSlots(p) {
  const slots = P.getJ(p, "fc_will_slots", [null, null, null]);
  return [0, 1, 2].map((index) => DATA.spells[slots[index]] ? slots[index] : null);
}

function releaseLegacyWillBar(p) {
  if (P.get(p, "fc_will_virtual_migrated", 0)) return;
  const c = inv(p);
  if (!c) return;
  for (let source = 6; source <= 8; source++) {
    const item = c.getItem(source);
    if (!item?.typeId.startsWith("fc:spell_")) continue;
    let target = -1;
    for (let slot = 9; slot < c.size; slot++) {
      if (!c.getItem(slot)) { target = slot; break; }
    }
    if (target < 0) {
      for (let slot = 0; slot < 6; slot++) {
        if (!c.getItem(slot)) { target = slot; break; }
      }
    }
    if (target >= 0) {
      c.setItem(target, item);
      c.setItem(source, undefined);
    }
  }
  P.set(p, "fc_will_virtual_migrated", 1);
}

function castActiveWill(p) {
  const slots = normalizedWillSlots(p);
  const active = Math.max(0, Math.min(2, P.get(p, "fc_will_active", 0)));
  const id = slots[active] ?? slots.find(Boolean);
  if (!id) {
    showHeroActionBar(p, "§9No Will power is attuned. Sneak-use the Will Focus to choose one.");
    return;
  }
  P.set(p, "fc_will_active", slots.indexOf(id));
  castSpell(p, id);
}

const willGreeted = new Set();
system.runInterval(() => {
  for (const p of world.getPlayers()) {
    learnInventoryWillSpells(p);
    releaseLegacyWillBar(p);
    if (P.getJ(p, "fc_will_slots", null) !== null) continue;
    const owned = willOwnedSpells(p);
    if (!owned.length) continue;
    P.setJ(p, "fc_will_slots", [owned[0] ?? null, owned[1] ?? null, owned[2] ?? null]);
    P.set(p, "fc_will_active", 0);
    if (!willGreeted.has(p.id)) {
      willGreeted.add(p.id);
      p.sendMessage("§9Will unlocked: press Sneak + 7, 8, or 9 to cast an attuned power. Your hotbar items remain untouched.");
      p.playSound("fc.level_up", { pitch: 1.1 });
    }
  }
}, 40);

function willAttuneMenu(p) {
  const slots = normalizedWillSlots(p);
  const active = Math.max(0, Math.min(2, P.get(p, "fc_will_active", 0)));
  const f = new ActionFormData().title(fableTitle("Attune Will Hotkeys"))
    .body(`${FABLE_RULE}\n§7Bind three learned powers without using inventory space.\n§7Cast with §fSneak + 7 / 8 / 9§7. The Will Focus casts the active slot.\n${FABLE_RULE}`);
  for (let i = 0; i < 3; i++) {
    const id = slots[i];
    const name = id ? (DATA.spells[id]?.name ?? id) : "§8(empty)";
    f.button(
      `${i === active ? "§b▶ " : "§7"}Key ${7 + i}\n§f${name}`,
      id ? `textures/items/spell_${id}` : "textures/items/will_focus",
    );
  }
  f.button("§8❖ Back");
  f.show(p).then((r) => {
    if (r.canceled) return;
    if (r.selection < 3) return willSlotPicker(p, r.selection);
    return magicMenu(p);
  }).catch(() => { });
}

function willSlotPicker(p, slotIdx) {
  const owned = willOwnedSpells(p);
  const slots = normalizedWillSlots(p);
  const current = slots[slotIdx];
  const f = new ActionFormData().title(fableTitle(`Slot ${slotIdx + 1}`))
    .body(`${FABLE_RULE}\n§7Choose the Will power for Sneak + §f${7 + slotIdx}§7.\n${FABLE_RULE}`);
  if (current) f.button(`§bUse with Will Focus\n§f${DATA.spells[current].name}`);
  for (const id of owned) f.button(`§b❖ ${DATA.spells[id].name}\n§8${DATA.spells[id].will} Will`);
  f.button("§7✖ Clear slot");
  f.button("§8❖ Back");
  f.show(p).then((r) => {
    if (r.canceled) return willAttuneMenu(p);
    const offset = current ? 1 : 0;
    if (current && r.selection === 0) {
      P.set(p, "fc_will_active", slotIdx);
      return willAttuneMenu(p);
    }
    if (r.selection >= offset && r.selection < owned.length + offset) {
      const id = owned[r.selection - offset];
      for (let k = 0; k < 3; k++) if (slots[k] === id) slots[k] = null;
      slots[slotIdx] = id;
      P.setJ(p, "fc_will_slots", slots);
      P.set(p, "fc_will_active", slotIdx);
    } else if (r.selection === owned.length + offset) {
      slots[slotIdx] = null;
      P.setJ(p, "fc_will_slots", slots);
      if (P.get(p, "fc_will_active", 0) === slotIdx) {
        const fallback = slots.findIndex(Boolean);
        P.set(p, "fc_will_active", fallback < 0 ? 0 : fallback);
      }
    }
    willAttuneMenu(p);
  }).catch(() => { });
}

// Will & Destiny (Phase 2) retires the Sneak+7/8/9 virtual-hotbar caster. The
// permanent Will Focus now casts on use and hot-swaps on crouch+use, and quick-
// slots are assigned in the storybook Hero Menu's Magic page (wd/quickcast.js,
// wd/herobook.js). The legacy attune helpers above are left inert for any older
// save data and are no longer reachable from the live menu.

const COMPASS_POINTS = ["S", "SW", "W", "NW", "N", "NE", "E", "SE"];
function compassPoint(yaw) {
  const normalized = ((yaw % 360) + 360) % 360;
  return COMPASS_POINTS[Math.round(normalized / 45) % 8];
}

function nearestHudLandmark(p) {
  const markers = [];
  try {
    const guild = JSON.parse(world.getDynamicProperty("fc_guild_loc") ?? "null");
    if (guild) markers.push({ name: "Guild", x: guild.x, z: guild.z });
  } catch { }
  try {
    const sites = JSON.parse(world.getDynamicProperty("fc_cullis") ?? "[]");
    for (const site of sites) markers.push(site);
  } catch { }
  let nearest = null;
  for (const marker of markers) {
    if (!Number.isFinite(marker.x) || !Number.isFinite(marker.z)) continue;
    const distance = Math.round(Math.hypot(marker.x - p.location.x, marker.z - p.location.z));
    if (!nearest || distance < nearest.distance) nearest = { ...marker, distance };
  }
  return nearest;
}

function compactHudBar(value, maximum, width = 10) {
  const filled = maximum > 0
    ? Math.max(0, Math.min(width, Math.round(value / maximum * width)))
    : 0;
  return `${"■".repeat(filled)}§8${"□".repeat(width - filled)}`;
}

function scaledHudBarWidth(maximum, baseMaximum, perSegment, cap = 28) {
  return Math.max(10, Math.min(cap, 10 + Math.floor(Math.max(0, maximum - baseMaximum) / perSegment)));
}

function heroStatusText(p) {
  const health = p.getComponent("minecraft:health");
  const hp = Math.ceil(health?.currentValue ?? 0);
  const hpMax = Math.ceil(health?.effectiveMax ?? 20);
  const will = willEnergy(p);
  const willMax = maxWill(p);
  const hunger = p.getComponent("minecraft:player.hunger") ?? p.getComponent("minecraft:hunger");
  const hungerCurrent = Math.ceil(hunger?.currentValue ?? 20);
  const hungerMax = Math.ceil(hunger?.effectiveMax ?? hunger?.defaultValue ?? 20);
  const healthWidth = scaledHudBarWidth(hpMax, 20, 4, 24);
  const willWidth = scaledHudBarWidth(willMax, 100, 25, 28);
  const multiplier = P.get(p, "fc_mult", 0);
  const lines = [
    `§c${compactHudBar(hp, hpMax, healthWidth)} §f${hp}/${hpMax}`,
    `§9${compactHudBar(will, willMax, willWidth)} §f${will}/${willMax}`,
    `§6${compactHudBar(hungerCurrent, hungerMax, 10)} §f${hungerCurrent}/${hungerMax}`,
  ];
  if (multiplier > 0) lines.push(`§6× ${multiplier}`);
  return lines.join("\n");
}

function npcCanSeeHero(npc, p, maxDistance) {
  try {
    const head = npc.getHeadLocation?.() ?? {
      x: npc.location.x,
      y: npc.location.y + 1.5,
      z: npc.location.z,
    };
    const target = p.getHeadLocation?.() ?? {
      x: p.location.x,
      y: p.location.y + 1.5,
      z: p.location.z,
    };
    const dx = target.x - head.x;
    const dy = target.y - head.y;
    const dz = target.z - head.z;
    const distance = Math.max(0.001, Math.hypot(dx, dy, dz));
    if (distance > maxDistance) return false;
    const direction = { x: dx / distance, y: dy / distance, z: dz / distance };
    const look = npc.getViewDirection();
    const fieldOfView = p.isSneaking ? 0.55 : 0.25;
    if (look.x * direction.x + look.y * direction.y + look.z * direction.z < fieldOfView) {
      return false;
    }
    try {
      const obstruction = npc.dimension.getBlockFromRay(head, direction, {
        maxDistance: Math.max(0, distance - 0.6),
        includeLiquidBlocks: false,
        includePassableBlocks: false,
      });
      if (obstruction) return false;
    } catch { }
    return true;
  } catch { return false; }
}

function heroVisibleToNpc(p) {
  const maxDistance = p.isSneaking ? 10 : 18;
  let observers = [];
  try {
    observers = p.dimension.getEntities({
      location: p.location,
      maxDistance,
      families: ["fc_friendly"],
    });
  } catch { }
  observers.sort((a, b) => {
    const da = Math.hypot(a.location.x - p.location.x, a.location.z - p.location.z);
    const db = Math.hypot(b.location.x - p.location.x, b.location.z - p.location.z);
    return da - db;
  });
  return observers.slice(0, 16).some((npc) => npcCanSeeHero(npc, p, maxDistance));
}

function albionClockText() {
  const ticks = world.getTimeOfDay();
  const hour = (Math.floor(ticks / 1000) + 6) % 24;
  const minute = Math.floor((ticks % 1000) * 60 / 1000);
  const phase = ticks >= 13000 && ticks < 23000 ? "NIGHT" : "DAY";
  return `${phase} ${String(hour).padStart(2, "0")}:${String(minute).padStart(2, "0")}`;
}

function radarLandmarks() {
  const markers = [];
  try {
    const guild = JSON.parse(world.getDynamicProperty("fc_guild_loc") ?? "null");
    if (guild) markers.push({ name: "Guild", x: guild.x, z: guild.z });
  } catch { }
  try {
    const sites = JSON.parse(world.getDynamicProperty("fc_cullis") ?? "[]");
    for (const site of sites) markers.push(site);
  } catch { }
  return markers.filter((marker) => Number.isFinite(marker.x) && Number.isFinite(marker.z));
}

function liveRadarRows(p) {
  const size = 9;
  const middle = Math.floor(size / 2);
  const blocksPerCell = 4;
  const forward = p.getViewDirection();
  const right = { x: -forward.z, z: forward.x };
  const cells = Array.from({ length: size }, () => Array(size).fill(" "));
  const priorities = Array.from({ length: size }, () => Array(size).fill(0));
  const terrainGlyph = (block) => {
    if (!block) return "§8·";
    const id = block.typeId;
    const dy = block.location.y - p.location.y;
    if (id.includes("water") || id.includes("ice")) return "§b≈";
    if (id.includes("lava") || id.includes("fire") || id.includes("magma")) return "§c≈";
    if (id.includes("snow")) return "§f·";
    if (id.includes("sand") || id.includes("sandstone")) return "§e·";
    if (id.includes("leaves") || id.includes("log") || id.includes("wood")) return "§2♣";
    if (id.includes("grass") || id.includes("moss") || id.includes("azalea")) return "§a·";
    if (id.includes("path") || id.includes("plank") || id.includes("brick")
      || id.includes("cobble") || id.includes("concrete")) return "§6▪";
    if (id.includes("stone") || id.includes("ore") || id.includes("deepslate")
      || id.includes("tuff") || id.includes("gravel")) return dy > 4 ? "§7▲" : "§8▪";
    if (id.includes("dirt") || id.includes("mud") || id.includes("clay")) return "§6·";
    return dy > 4 ? "§7▲" : dy < -4 ? "§8▽" : "§7·";
  };

  for (let row = 0; row < size; row++) {
    for (let column = 0; column < size; column++) {
      const localX = column - middle;
      const localZ = middle - row;
      if (Math.hypot(localX, localZ) > middle + 0.25) continue;
      const x = Math.floor(p.location.x
        + right.x * localX * blocksPerCell
        + forward.x * localZ * blocksPerCell);
      const z = Math.floor(p.location.z
        + right.z * localX * blocksPerCell
        + forward.z * localZ * blocksPerCell);
      try {
        cells[row][column] = terrainGlyph(p.dimension.getTopmostBlock({ x, z }));
      } catch {
        try { cells[row][column] = terrainGlyph(p.dimension.getBlock({ x, y: Math.floor(p.location.y) - 1, z })); } catch { }
      }
    }
  }

  const place = (location, glyph, priority, clampToEdge = false) => {
    const dx = location.x - p.location.x;
    const dz = location.z - p.location.z;
    let column = middle + Math.round((dx * right.x + dz * right.z) / blocksPerCell);
    let row = middle - Math.round((dx * forward.x + dz * forward.z) / blocksPerCell);
    if (clampToEdge) {
      column = Math.max(0, Math.min(size - 1, column));
      row = Math.max(0, Math.min(size - 1, row));
    }
    if (row < 0 || row >= size || column < 0 || column >= size) return;
    if (priority < priorities[row][column]) return;
    cells[row][column] = glyph;
    priorities[row][column] = priority;
  };

  for (const landmark of radarLandmarks()) place(landmark, "§6◆", 1, true);
  try {
    for (const npc of p.dimension.getEntities({
      location: p.location,
      maxDistance: 27,
      families: ["fc_friendly"],
    })) {
      place(npc.location, "§a•", 2);
    }
  } catch { }
  try {
    for (const hostile of p.dimension.getEntities({
      location: p.location,
      maxDistance: 27,
      families: ["monster"],
    })) {
      place(hostile.location, "§c!", 3);
    }
  } catch { }
  cells[middle][middle] = "§f▲";
  return cells.map((row) => row.join(" "));
}

function heroRadarText(p) {
  const heading = compassPoint(p.getRotation().y);
  const landmark = nearestHudLandmark(p);
  const nav = landmark
    ? `${heading} · ${landmark.name} · ${landmark.distance}m`
    : `${heading} · ${Math.floor(p.location.x)}, ${Math.floor(p.location.z)}`;
  const seen = heroVisibleToNpc(p);
  const eye = seen ? "§c◉" : "§a—";
  const radarPadding = "               ";
  return [
    `     ${eye}                    §e${albionClockText()}`,
    "",
    ...liveRadarRows(p).map((row) => `${radarPadding}${row}`),
    `${radarPadding}§6${nav}`,
  ].join("\n");
}

// Live HUD output is owned by fable_hud.js.
if (false) system.runInterval(() => {
  for (const p of world.getPlayers()) {
    if (TICKS() >= (titleHoldUntil.get(p.id) ?? 0)) {
      try {
        p.onScreenDisplay.setTitle(heroStatusText(p), {
          fadeInDuration: 0,
          stayDuration: 16,
          fadeOutDuration: 0,
          subtitle: heroRadarText(p),
        });
      } catch { }
    }
    const notice = heroNotice.get(p.id);
    const message = notice && TICKS() < notice.until ? notice.text : "";
    if (notice && !message) heroNotice.delete(p.id);
    try {
      p.onScreenDisplay.setActionBar(`§6${countItem(p, "fc:gold_coin")}\n${message}`);
    } catch { }
  }
}, 10);

system.runInterval(() => {
  for (const p of world.getPlayers()) {
    const regen = 1 + P.get(p, "fc_up_magic_power", 0);
    P.set(p, "fc_will", Math.min(maxWill(p), willEnergy(p) + regen));
    if (TICKS() - P.get(p, "fc_lastHit", 0) > 240 && P.get(p, "fc_mult", 0) > 0) {
      P.set(p, "fc_mult", Math.max(0, P.get(p, "fc_mult", 0) - 2));
    }
    applyUpgrades(p);
  }
}, 20);

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
  f.button("§8Back");
  f.show(p).then((r) => {
    if (r.canceled) return;
    if (r.selection >= avail.length) return questJournalMenu(p);
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
  }).catch(() => { });
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
    .button("§cAbandon quest")
    .button("§8Back");
  f.show(p).then((r) => {
    if (r.canceled) return;
    if (r.selection === 0 && complete) return completeQuest(p, q);
    if (r.selection === 1) {
      P.set(p, "fc_quest", undefined);
      p.sendMessage("§7The quest card crumbles. The Guild will not be impressed.");
      return questJournalMenu(p);
    }
    if (r.selection === 2 || (r.selection === 0 && !complete)) return questJournalMenu(p);
  }).catch(() => { });
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
  showHeroTitle(p, "§6Quest Complete", { fadeInDuration: 5, stayDuration: 50, fadeOutDuration: 15, subtitle: `§e${q.name}` });
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
      showHeroActionBar(p, `§e${o.label}: §f${aq.progress[i]}/${o.count}`);
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
    const usedItem = ev.itemStack?.typeId;
    system.run(() => {
      // a one-shot wave the moment the Hero is greeted (humanoid NPCs only; the
      // call is a harmless no-op on plans without the clip, e.g. the Oracle)
      try { target.playAnimation("animation.fc.biped.greet", { blendOutTime: 0.4 }); } catch { }
      try { target.lookAt?.(p.getHeadLocation()); } catch { }
      // ROMANCE: a wedded spouse opens the marriage menu; offering a ring to a
      // courtable NPC proposes; offering a flower/pie/gold courts them. Otherwise
      // fall through to the normal conversation.
      if (isRomanceable(target)) {
        if (isMySpouse(target, p)) { spouseMenu(p, target); return; }
        if (usedItem === "fc:wedding_ring") { proposeMenu(p, target); return; }
        if (usedItem && HELD_GIFTS[usedItem] !== undefined) { offerGift(p, target, usedItem); return; }
      }
      npcTalk(p, target);
    });
  }
});

// the Quest Table lectern in the Heroes' Guild great hall opens the quest board
world.beforeEvents.playerInteractWithBlock.subscribe((ev) => {
  if (ev.block?.typeId !== "minecraft:lectern") return;
  const b = ev.block.location;
  const rawList = world.getDynamicProperty("fc_guild_quest_tables");
  let matched = false;
  if (rawList) {
    try {
      const locs = JSON.parse(rawList);
      matched = Array.isArray(locs) && locs.some((loc) => b.x === loc.x && b.y === loc.y && b.z === loc.z);
    } catch { matched = false; }
  }
  if (!matched) {
    const raw = world.getDynamicProperty("fc_guild_quest_table");
    if (!raw) return;
    const loc = JSON.parse(raw);
    matched = b.x === loc.x && b.y === loc.y && b.z === loc.z;
  }
  if (!matched) return;
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
  showHeroTitle(p, "§5Demon Door Opened", { fadeInDuration: 8, stayDuration: 60, fadeOutDuration: 15, subtitle: `§7${d.name}` });
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

// ===========================================================================
// ROMANCE & MARRIAGE
// A high NPC opinion (fc:love_hate, raised by expressions and by gifts) floats a
// red heart over the NPC's head. Court them with flowers/pies/gold, then offer a
// Wedding Ring to wed: the NPC dons wedding finery (a render-controller skin swap
// keyed on the client-synced fc:married property), the heart becomes a gold ring,
// and a full spouse conversation menu opens. Eligibility mirrors is_romanceable()
// in fc_mobs.py — every social NPC except the unique story characters, and Lady
// Grey / Briar Rose keep their own bespoke marriage flow.
// ===========================================================================
const LOVE_HEART = 60;            // love_hate at/above this = full heart & allows a proposal
const LIKE_HEART_MIN = 18;        // opinion at which a *small* heart first appears (warming to you)
const HEART_MIN_SIZE = 0.12;      // billboard size of the just-starting-to-like heart
const HEART_FULL_SIZE = 0.42;     // billboard size once they're in love (>= LOVE_HEART)
const HEART_MV = new MolangVariableMap(); // reused to drive variable.size on fc:love_heart_float
const GIFT_COOLDOWN_TICKS = 200;  // ~10s between accepted gifts per NPC

// Items a Hero can press into an NPC's hands to win their heart (value -> love).
// Gold is deliberately NOT here: the trader/barkeep are courtable and players
// hold gold to shop, so a gold-in-hand interact must still open their store.
const HELD_GIFTS = {
  "fc:apple_pie": 7, "fc:golden_carrot_brew": 6,
  "minecraft:poppy": 9, "minecraft:dandelion": 6, "minecraft:cornflower": 8,
  "minecraft:oxeye_daisy": 7, "minecraft:azure_bluet": 7, "minecraft:allium": 8,
  "minecraft:blue_orchid": 9, "minecraft:lily_of_the_valley": 9, "minecraft:rose_bush": 10,
  "minecraft:pink_tulip": 8, "minecraft:red_tulip": 8, "minecraft:orange_tulip": 7,
  "minecraft:white_tulip": 7, "minecraft:wither_rose": 4,
};
const PET_NAMES = ["Beloved", "Sweetheart", "Darling", "My Heart", "Treasure", "Dearest"];

function isRomanceable(e) {
  try { return typeof e.getProperty("fc:married") === "number"; } catch { return false; }
}
function npcLove(npc) {
  try { const v = npc.getProperty("fc:love_hate"); if (typeof v === "number") return v; } catch { }
  return 0;
}
function setNpcLove(npc, v) {
  const n = Math.max(-100, Math.min(100, Math.round(v)));
  try { npc.setProperty("fc:love_hate", n); } catch { }
  return n;
}
function isMarried(npc) {
  try { return (npc.getProperty("fc:married") || 0) > 0; } catch { return false; }
}
function isMySpouse(npc, p) {
  return isMarried(npc) && npc.getDynamicProperty("fc_spouse_player") === p.id;
}
function npcName(npc) { return displayName(npc.typeId); }

function marryNpc(p, npc) {
  if (!removeItem(p, "fc:wedding_ring", 1)) { p.sendMessage("§7You no longer have a wedding ring."); return; }
  setNpcLove(npc, 100);
  try { npc.setProperty("fc:married", 1); } catch { }
  npc.setDynamicProperty("fc_spouse_player", p.id);
  const base = npcName(npc);
  const pet = PET_NAMES[Math.floor(Math.random() * PET_NAMES.length)];
  try { npc.nameTag = `§d${pet} ♥ §r§7(${base})`; } catch { }
  const list = P.getJ(p, "fc_spouses", []);
  if (!list.includes(npc.id)) { list.push(npc.id); P.setJ(p, "fc_spouses", list); }
  addMorality(p, 40);
  try { npc.triggerEvent("fc:react_follow"); } catch { }
  try { npc.playAnimation("animation.npc.cheer", { blendOutTime: 0.3 }); } catch { }
  try { p.playSound("random.levelup"); } catch { }
  try {
    const l = npc.location;
    for (let i = 0; i < 8; i++) {
      npc.dimension.spawnParticle("minecraft:heart_particle",
        { x: l.x, y: l.y + 1.6 + Math.random() * 0.9, z: l.z });
    }
  } catch { }
  p.sendMessage(`§d♥ You and ${base} are wed! They will follow your heart now.`);
}

function proposeMenu(p, npc) {
  const base = npcName(npc);
  if (isMarried(npc)) {
    p.sendMessage(npc.getDynamicProperty("fc_spouse_player") === p.id
      ? `§d${base} is already your beloved.` : `§7${base} is already wed to another.`);
    return;
  }
  if (npcLove(npc) < LOVE_HEART) {
    new MessageFormData().title("§dToo soon...")
      .body(`§f§o"${base} eyes the ring and steps back. 'We barely know one another, Hero. Win my heart first — a kind word, a thoughtful gift...'"§r`)
      .button1("§7Of course").button2("§8Back").show(p).catch(() => { });
    return;
  }
  new MessageFormData().title("§d♥ A Proposal")
    .body(`§f§o"${base} sees the ring glinting in your hand, and their breath catches..."§r`)
    .button1("§dOffer the ring").button2("§8Not yet").show(p).then((r) => {
      if (r.canceled || r.selection !== 0) return;
      marryNpc(p, npc);
    }).catch(() => { });
}

function offerGift(p, npc, itemId) {
  const base = npcName(npc);
  if (isMarried(npc) && npc.getDynamicProperty("fc_spouse_player") !== p.id) {
    p.sendMessage(`§7${base} politely declines — their heart belongs to another.`);
    return;
  }
  const cd = npc.getDynamicProperty("fc_gift_cd");
  if (typeof cd === "number" && system.currentTick < cd) {
    p.sendMessage(`§7${base} is still glowing from your last gift.`);
    return;
  }
  if (!removeItem(p, itemId, 1)) { p.sendMessage("§7You have nothing to give."); return; }
  npc.setDynamicProperty("fc_gift_cd", system.currentTick + GIFT_COOLDOWN_TICKS);
  const before = npcLove(npc);
  const after = setNpcLove(npc, before + (HELD_GIFTS[itemId] ?? 4));
  try { npc.playAnimation("animation.fc.biped.greet", { blendOutTime: 0.4 }); } catch { }
  try { npc.lookAt?.(p.getHeadLocation()); } catch { }
  try { p.playSound("random.orb"); } catch { }
  p.sendMessage(`§d${base}: §o"For me? You're too kind, Hero."`);
  if (before < LOVE_HEART && after >= LOVE_HEART) {
    p.sendMessage(`§d♥ ${base} has fallen for you. A wedding ring would not go amiss now...`);
    try { p.playSound("random.levelup"); } catch { }
  }
}

function bestGiftInBag(p) {
  for (const id of Object.keys(HELD_GIFTS)) if (countItem(p, id) > 0) return id;
  return undefined;
}

function divorceConfirm(p, npc) {
  const base = npcName(npc);
  new MessageFormData().title("§cPart Ways")
    .body(`§f§o"You wish to end your marriage to ${base}? They will be heartbroken."§r`)
    .button1("§cYes, part ways").button2("§8No, stay wed").show(p).then((r) => {
      if (r.canceled || r.selection !== 0) return;
      try { npc.setProperty("fc:married", 0); } catch { }
      setNpcLove(npc, 20);
      npc.setDynamicProperty("fc_spouse_player", "");
      try { npc.nameTag = ""; } catch { }
      P.setJ(p, "fc_spouses", P.getJ(p, "fc_spouses", []).filter((id) => id !== npc.id));
      try { npc.triggerEvent("fc:react_neutral"); } catch { }
      addMorality(p, -30);
      p.sendMessage(`§7You and ${base} have parted ways.`);
    }).catch(() => { });
}

function spouseMenu(p, npc) {
  const base = npcName(npc);
  const m = morality(p);
  const greet = m > 200 ? "My love! The whole village glows when you visit."
    : m < -200 ? "You're back. They whisper such things about you... I don't believe a word. Mostly."
      : "There you are, my heart. I've missed you.";
  new ActionFormData().title(`§d${base} ♥`)
    .body(`§f§o"${greet}"§r`)
    .button("§dSweet nothings")
    .button("§aFollow me")
    .button("§eWait here")
    .button("§6Give a gift")
    .button("§cPart ways")
    .button("§8Farewell")
    .show(p).then((r) => {
      if (r.canceled) return;
      if (r.selection === 0) {
        const lines = [
          "You make a hard world soft, Hero.",
          "Come home safe. The hearth's warm and the kettle's on.",
          "Whatever Albion throws at you, throw me a wink first.",
          "I keep your trophies dusted. Mostly the less grisly ones.",
        ];
        setNpcLove(npc, Math.min(100, npcLove(npc) + 1));
        try { npc.playAnimation("animation.npc.cheer", { blendOutTime: 0.3 }); } catch { }
        p.sendMessage(`§d${base}: §o"${lines[Math.floor(Math.random() * lines.length)]}"`);
      } else if (r.selection === 1) {
        try { npc.triggerEvent("fc:react_follow"); } catch { }
        try { npc.lookAt?.(p.getHeadLocation()); } catch { }
        p.sendMessage(`§d${base}: §o"Lead on, my love."`);
      } else if (r.selection === 2) {
        try { npc.triggerEvent("fc:react_neutral"); } catch { }
        p.sendMessage(`§d${base}: §o"I'll wait right here for you."`);
      } else if (r.selection === 3) {
        const id = bestGiftInBag(p);
        if (!id) { p.sendMessage("§7You have nothing to give. Try a flower or an apple pie."); return; }
        offerGift(p, npc, id);
      } else if (r.selection === 4) {
        divorceConfirm(p, npc);
      }
    }).catch(() => { });
}

// Float a heart over smitten NPCs and a gold ring over wedded ones. Driven from
// the server (the proven Fablecraft pattern) off the synced opinion value. The
// heart appears small the moment an NPC starts to LIKE the Hero (love_hate >=
// LIKE_HEART_MIN) and swells to full size by the time they LOVE you (LOVE_HEART):
// the custom fc:love_heart_float particle reads variable.size, which we lerp from
// HEART_MIN_SIZE to HEART_FULL_SIZE across that window.
system.runInterval(() => {
  const players = world.getAllPlayers();
  if (!players.length) return;
  const seen = new Set();
  for (const p of players) {
    let nearby;
    try { nearby = p.dimension.getEntities({ location: p.location, maxDistance: 22 }); } catch { continue; }
    for (const e of nearby) {
      if (seen.has(e.id) || !isRomanceable(e)) continue;
      seen.add(e.id);
      let loc; try { loc = e.location; } catch { continue; }
      const at = { x: loc.x, y: loc.y + 2.15, z: loc.z };
      try {
        if (isMarried(e)) { e.dimension.spawnParticle("fc:wedding_ring_float", at); continue; }
        const love = npcLove(e);
        if (love < LIKE_HEART_MIN) continue;
        const t = Math.max(0, Math.min(1, (love - LIKE_HEART_MIN) / (LOVE_HEART - LIKE_HEART_MIN)));
        HEART_MV.setFloat("variable.size", HEART_MIN_SIZE + (HEART_FULL_SIZE - HEART_MIN_SIZE) * t);
        e.dimension.spawnParticle("fc:love_heart_float", at, HEART_MV);
      } catch { }
    }
  }
}, 16);

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
      b.button("§8Back");
      b.show(p).then((res) => {
        if (res.canceled) return;
        if (res.selection >= priced.length) return shopMenu(p, title);
        const s = priced[res.selection];
        buyQuantityMenu(p, title, s);
      }).catch(() => { });
    } else {
      sellMenu(p, title, tier);
    }
  }).catch(() => { });
}

function buyQuantityMenu(p, shopTitle, stock) {
  const max = Math.min(64, Math.floor(countItem(p, "fc:gold_coin") / stock.cost));
  if (max < 1) {
    p.sendMessage("§7Trader: \"Coin first, hero second.\"");
    return shopMenu(p, shopTitle);
  }
  new ActionFormData().title(fableTitle(stock.label)).body(fableBody([
    `§6Price: §f${stock.cost} gold each`,
    `§7Your purse: §f${countItem(p, "fc:gold_coin")} gold`,
  ]))
    .button(`§aBuy one\n§8${stock.cost} gold`)
    .button(`§6Buy maximum (${max})\n§8${max * stock.cost} gold`)
    .button("§eChoose amount")
    .button("§8Back")
    .show(p).then((r) => {
      if (r.canceled) return;
      if (r.selection === 0) return completePurchase(p, shopTitle, stock, 1);
      if (r.selection === 1) return completePurchase(p, shopTitle, stock, max);
      if (r.selection === 2) {
        return new ModalFormData().title(fableTitle("Choose Amount"))
          .slider(`${stock.label} (1–${max})`, 1, max, 1, max)
          .submitButton("Buy")
          .show(p).then((response) => {
            if (response.canceled) return buyQuantityMenu(p, shopTitle, stock);
            completePurchase(p, shopTitle, stock, Math.round(response.formValues?.[0] ?? 1));
          });
      }
      shopMenu(p, shopTitle);
    }).catch(() => { });
}

function completePurchase(p, shopTitle, stock, quantity) {
  const amount = Math.max(1, Math.min(64, quantity));
  const cost = stock.cost * amount;
  if (!removeItem(p, "fc:gold_coin", cost)) {
    p.sendMessage("§7Trader: \"Your purse comes up short.\"");
    return shopMenu(p, shopTitle);
  }
  giveItem(p, stock.id, amount);
  p.playSound("mob.villager.yes");
  p.sendMessage(`§6Bought ${amount} ${stock.label}${amount === 1 ? "" : "s"} for ${cost} gold.`);
  shopMenu(p, shopTitle);
}

function sellMenu(p, shopTitle, tier) {
  const bonus = tier === "friendly" || tier === "revered" ? 1.1 : 1;
  const entries = Object.entries(SELL_PRICES)
    .map(([id, base]) => ({ id, count: countItem(p, id), price: Math.max(1, Math.round(base * bonus)) }))
    .filter((entry) => entry.count > 0);
  const f = new ActionFormData().title(fableTitle("Sell Trophies")).body(fableBody([
    entries.length ? "§7Choose a trophy and quantity." : "§8Nothing in your pack interests the trader.",
  ]));
  for (const entry of entries) {
    f.button(`§f${displayName(entry.id)} ×${entry.count}\n§6${entry.price} gold each`,
      `textures/items/${entry.id.replace("fc:", "")}`);
  }
  f.button("§8Back");
  f.show(p).then((r) => {
    if (r.canceled) return;
    if (r.selection >= entries.length) return shopMenu(p, shopTitle);
    sellQuantityMenu(p, shopTitle, tier, entries[r.selection]);
  }).catch(() => { });
}

function sellQuantityMenu(p, shopTitle, tier, entry) {
  new ActionFormData().title(fableTitle(displayName(entry.id))).body(fableBody([
    `§7Carried: §f${entry.count}`,
    `§6Trader offers: §f${entry.price} gold each`,
  ]))
    .button(`§aSell one\n§8${entry.price} gold`)
    .button(`§6Sell maximum (${entry.count})\n§8${entry.count * entry.price} gold`)
    .button("§eChoose amount")
    .button("§8Back")
    .show(p).then((r) => {
      if (r.canceled) return;
      if (r.selection === 0) return completeSale(p, shopTitle, tier, entry, 1);
      if (r.selection === 1) return completeSale(p, shopTitle, tier, entry, entry.count);
      if (r.selection === 2) {
        return new ModalFormData().title(fableTitle("Choose Amount"))
          .slider(`${displayName(entry.id)} (1–${entry.count})`, 1, entry.count, 1, entry.count)
          .submitButton("Sell")
          .show(p).then((response) => {
            if (response.canceled) return sellQuantityMenu(p, shopTitle, tier, entry);
            completeSale(p, shopTitle, tier, entry, Math.round(response.formValues?.[0] ?? 1));
          });
      }
      sellMenu(p, shopTitle, tier);
    }).catch(() => { });
}

function completeSale(p, shopTitle, tier, entry, quantity) {
  const amount = Math.max(1, Math.min(entry.count, quantity));
  if (!removeItem(p, entry.id, amount)) {
    p.sendMessage("§7Trader: \"Those goods are no longer in your pack.\"");
    return sellMenu(p, shopTitle, tier);
  }
  const gold = amount * entry.price;
  giveItem(p, "fc:gold_coin", gold);
  p.playSound("random.orb");
  p.sendMessage(`§6Sold ${amount} ${displayName(entry.id)} for ${gold} gold.`);
  sellMenu(p, shopTitle, tier);
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
  const x = Math.floor(loc.x), y = Math.floor(loc.y), z = Math.floor(loc.z);
  const existing = sites.find((s) => s.name === name);
  if (existing) {                 // re-anchor an existing gate (Guild rebuilt/moved) — never leave it stale
    existing.x = x; existing.y = y; existing.z = z;
  } else {
    sites.push({ name, x, y, z });
  }
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
    // A reliable fallback at ANY gate: sneak while standing in it to travel at
    // once. (So the network always works even if the portal ring reads wrong.)
    if (p.isSneaking) {
      const last = cullisCd.get(p.id) ?? -9999;
      if (TICKS() - last < 80) continue;
      cullisCd.set(p.id, TICKS());
      cullisDwell.delete(dwellKey);
      try { dim.spawnParticle("minecraft:huge_explosion_emitter", { x: near.x + 0.5, y: near.y + 1, z: near.z + 0.5 }); } catch { }
      cullisTravel(p, sites, near);
      continue;
    }
    if (isCullisConfigured(dim, near)) {
      // PORTAL: stand in the central blue light for ~3s to be carried away
      const inCentre = Math.hypot(p.location.x - (near.x + 0.5), p.location.z - (near.z + 0.5)) < 1.3;
      if (!inCentre) {
        cullisDwell.delete(dwellKey);
        showHeroActionBar(p, "§b◈ Cullis Gate §7— step into the light to travel");
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
        showHeroActionBar(p, `§b◈ The Gate awakens… §f${"▮".repeat(d)}§8${"▯".repeat(NEED - d)}`);
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
        showHeroActionBar(p, "§b◈ Cullis Gate §7— sneak to focus your Will and travel");
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
  let raw = world.getDynamicProperty("fc_guild_skill");
  if (!raw) {                                  // self-heal: derive from the Guild base
    const baseRaw = world.getDynamicProperty("fc_guild_base");
    if (baseRaw) {
      try {
        const b = JSON.parse(baseRaw);
        raw = JSON.stringify({ x: b.x + GUILD.skill.x, y: b.y, z: b.z + GUILD.skill.z });
      } catch { }
    }
  }
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
      showHeroActionBar(p, "§a✦ Experience Shrine §7— step into the green light to train");
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
      showHeroActionBar(p, `§a✦ The Shrine drinks your deeds… §f${"▮".repeat(d)}§8${"▯".repeat(NEED - d)}`);
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
    if (d < 5) { showHeroActionBar(p, `§6❖ Boasting Platform §7— the crowd gathers… §e${5 - d}s`); continue; }
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
      showHeroActionBar(p, `§e${NPC_NAME[e.typeId] ?? "Citizen"}: §f${line}`);
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
    showHeroTitle(p, "§b◈", { fadeInDuration: 2, stayDuration: 16, fadeOutDuration: 8, subtitle: `§f${s.name}` });
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

// ---------------------------------------------------------------------------
// SETTLEMENT BOUNTIES — per-player, per-location crime and guard response
// ---------------------------------------------------------------------------
const BOUNTY_KEY = "fc_bounties";
// Harsh / Fable-tough wanted tuning (owner's call). EVERY blow and every kill
// adds to the bounty by severity, and tops up a live countdown; let the timer
// run out and the warrant fades on its own.
const BOUNTY_AMOUNT = {
  punch: { civilian: 10, guard: 20 },   // a struck townsfolk vs a struck guard/guild member
  kill: { civilian: 40, guard: 80 },
};
const BOUNTY_TIME_MS = {                 // how much each crime adds to the countdown
  punch: 40 * 1000,
  kill: 120 * 1000,
};
const BOUNTY_TIMER_START_MS = 120 * 1000;   // a fresh warrant's opening countdown
const BOUNTY_TIMER_MAX_MS = 15 * 60 * 1000; // hard cap on the countdown
const BOUNTY_GUARD_DETECTION_RADIUS = 36;
const BOUNTY_TOWNS = ["bowerstone", "oakvale", "snowspire"];
// The Heroes' Guild keeps its own order: it is its own bounty jurisdiction,
// enforced by the Guild's standing defenders rather than spawned town watch.
const GUILD_TOWN_KEY = "guild";
const GUILD_BOUNTY_KEY = "guild_heroes";
const BOUNTY_WANTED_TAG = {
  bowerstone: "fc_wanted_bowerstone",
  oakvale: "fc_wanted_oakvale",
  snowspire: "fc_wanted_snowspire",
};
const BOUNTY_GUARD_TYPE = {
  bowerstone: "fc:guard_bowerstone",
  oakvale: "fc:guard_oakvale",
  snowspire: "fc:guard_snowspire",
};
const SETTLEMENT_META = {
  "fc:bowerstone_market": ["bowerstone", "Bowerstone Market"],
  "fc:lookout_point": ["bowerstone", "Lookout Point"],
  "fc:darkwood_camp": ["bowerstone", "Darkwood Trading Camp"],
  "fc:oakvale_village": ["oakvale", "Oakvale"],
  "fc:power_oakvale_quay": ["oakvale", "Oakvale Quay"],
  "fc:knothole_glade": ["oakvale", "Knothole Glade"],
  "fc:orchard_farm": ["oakvale", "Orchard Farm"],
  "fc:fisher_creek": ["oakvale", "Fisher Creek"],
  "fc:rose_cottage": ["oakvale", "Rose Cottage"],
  "fc:windmill_hill": ["oakvale", "Windmill Hill"],
  "fc:hook_coast": ["snowspire", "Hook Coast"],
  "fc:power_snowspire_oracle": ["snowspire", "Snowspire"],
};
const CIVILIAN_TOWN = {
  ...VILLAGER_TOWN,
  "minecraft:villager": "bowerstone",
  "minecraft:villager_v2": "bowerstone",
  "fc:trader": "bowerstone",
  "fc:barkeep": "bowerstone",
  "fc:lady_grey": "bowerstone",
  "fc:oracle": "snowspire",
  "fc:briar_rose": "oakvale",
};
const bountyDemand = new Map(); // player id -> { placeKey, startedTick, prompted }
const bountySpawnCooldown = new Map(); // player id|place -> last reinforcement tick

function getBounties(p) {
  const value = P.getJ(p, BOUNTY_KEY, {});
  return value && typeof value === "object" && !Array.isArray(value) ? value : {};
}
function setBounties(p, records) { P.setJ(p, BOUNTY_KEY, records); }
function bountyKillCount(record) {
  return Math.max(0, record.civilianKills ?? 0) + Math.max(0, record.guardKills ?? 0);
}
function bountyResponseTier(record) {
  if (record.amount >= 200) return { tier: 3, cap: 4, label: "elite" };
  if (record.amount >= 75) return { tier: 2, cap: 3, label: "veteran" };
  return { tier: 1, cap: 2, label: "standard" };
}
function bountyHeatLevel(record) {
  const amount = Math.max(0, record?.amount ?? 0);
  if (amount >= 175) return 5;
  if (amount >= 110) return 4;
  if (amount >= 60) return 3;
  if (amount >= 20) return 2;
  return amount > 0 ? 1 : 0;
}
// The warrant the player most needs to worry about drives the HUD heat + timer.
function dominantBounty(records) {
  const all = Object.values(records);
  return all.length ? all.reduce((a, b) => (b.amount >= a.amount ? b : a)) : null;
}
// Push the active wanted level (stars) and remaining countdown (seconds) to the
// HUD. Shown whenever a warrant is live — wherever the Hero is.
function refreshWantedHud(p, dominant, now = Date.now()) {
  const stars = dominant ? bountyHeatLevel(dominant) : 0;
  const secs = dominant ? Math.max(0, Math.ceil((dominant.expiresAtMs - now) / 1000)) : 0;
  try {
    if (p.getDynamicProperty("fc_wanted_heat") !== stars) p.setDynamicProperty("fc_wanted_heat", stars);
    if (p.getDynamicProperty("fc_wanted_timer") !== secs) p.setDynamicProperty("fc_wanted_timer", secs);
  } catch { }
}
// A settlement-shaped descriptor for the Heroes' Guild so the bounty machinery
// can treat the campus as its own jurisdiction (enforced by its own defenders).
function guildJurisdiction() {
  const b = guildBounds();
  if (!b) return null;
  return {
    key: GUILD_BOUNTY_KEY,
    id: "fc:guild_hall",
    theme: "guild",
    x: b.minX,
    z: b.minZ,
    w: Math.max(b.maxX - b.minX, b.maxZ - b.minZ),
    town: GUILD_TOWN_KEY,
    name: "Heroes' Guild",
    dimension: OW().id,
  };
}
function formatBountyTime(ms) {
  const seconds = Math.max(0, Math.ceil(ms / 1000));
  const minutes = Math.floor(seconds / 60);
  return minutes > 0 ? `${minutes}m ${seconds % 60}s` : `${seconds}s`;
}
function bountySummaryLines(p) {
  const entries = Object.values(getBounties(p));
  if (!entries.length) return [];
  const now = Date.now();
  return [
    "",
    "§4Active bounties:",
    ...entries.map((record) => {
      const response = bountyResponseTier(record);
      const timer = record.expiresAtMs > 0 ? ` §8(${formatBountyTime(record.expiresAtMs - now)} left)` : "";
      const enforcers = record.town === GUILD_TOWN_KEY
        ? "Guild defenders" : `${response.cap} ${response.label} guards`;
      return ` §c⚖ ${record.name}: §6${record.amount}g §7· §e${"★".repeat(bountyHeatLevel(record))}§7 · ${enforcers}${timer}`;
    }),
  ];
}
function entityHasFamily(entity, family) {
  try { return entity.getComponent("minecraft:type_family")?.hasTypeFamily(family) === true; } catch { return false; }
}
function bountyCrimeKind(entity) {
  if (entityHasFamily(entity, "fc_guard")) return "guard";
  // Guild defenders (Guildmaster, Maze, fighting apprentices) answer like guards.
  if (isGuildDefenderType(entity)) return "guard";
  if (entity.typeId === "minecraft:villager" || entity.typeId === "minecraft:villager_v2") return "civilian";
  if (entityHasFamily(entity, "fc_friendly") && !entityHasFamily(entity, "fc_ally")) return "civilian";
  return null;
}
function settlementTown(place, victimType) {
  if (SETTLEMENT_META[place.id]) return SETTLEMENT_META[place.id][0];
  if (place.theme === "snow") return "snowspire";
  if (place.theme === "farm") return "oakvale";
  if (place.theme === "village") return CIVILIAN_TOWN[victimType] ?? "oakvale";
  return null;
}
function settlementName(place, town) {
  if (SETTLEMENT_META[place.id]) return SETTLEMENT_META[place.id][1];
  if (place.name) return place.name;
  if (place.id?.startsWith("fc:")) {
    return place.id.substring(3).split("_")
      .map((word) => word.charAt(0).toUpperCase() + word.slice(1)).join(" ");
  }
  return `${FACTION_NAMES[town]} Outskirts`;
}
function locationInsideSettlement(location, dimensionId, record, margin = 0) {
  if (record.dimension !== dimensionId) return false;
  return location.x >= record.x - margin && location.x <= record.x + record.w + margin
    && location.z >= record.z - margin && location.z <= record.z + record.w + margin;
}
function settlementForCrime(p, dead) {
  const existing = getBounties(p);
  try {
    const assignedKey = dead.getDynamicProperty("fc_bounty_place");
    if (typeof assignedKey === "string" && existing[assignedKey]) return existing[assignedKey];
  } catch { }

  // Any crime on Guild ground answers to the Guild, not the town watch.
  try {
    if (isInsideGuild(dead.location, dead.dimension.id)) {
      const guild = guildJurisdiction();
      if (guild) return guild;
    }
  } catch { }

  let places = [];
  try { places = JSON.parse(world.getDynamicProperty("fc_places") ?? "[]"); } catch { }
  let best = null, bestDistance = Infinity;
  for (const place of places) {
    const town = settlementTown(place, dead.typeId);
    if (!town) continue;
    const cx = place.x + place.w / 2, cz = place.z + place.w / 2;
    const distance = Math.hypot(dead.location.x - cx, dead.location.z - cz);
    const inside = dead.location.x >= place.x - 10 && dead.location.x <= place.x + place.w + 10
      && dead.location.z >= place.z - 10 && dead.location.z <= place.z + place.w + 10;
    if (inside && distance < bestDistance) {
      bestDistance = distance;
      best = {
        key: place.k ?? `${place.x}_${place.z}`,
        id: place.id,
        theme: place.theme,
        x: place.x,
        z: place.z,
        w: place.w,
        town,
        name: settlementName(place, town),
        dimension: dead.dimension.id,
      };
    }
  }
  if (best) return best;

  const town = CIVILIAN_TOWN[dead.typeId] ?? GUARD_TOWN[dead.typeId];
  if (!town) return null;
  const cellX = Math.floor(dead.location.x / 64) * 64;
  const cellZ = Math.floor(dead.location.z / 64) * 64;
  return {
    key: `outskirts_${town}_${cellX}_${cellZ}`,
    id: `fc:${town}_outskirts`,
    theme: town === "snowspire" ? "snow" : "village",
    x: cellX,
    z: cellZ,
    w: 64,
    town,
    name: `${FACTION_NAMES[town]} Outskirts`,
    dimension: dead.dimension.id,
  };
}
function currentBounty(p, records = getBounties(p)) {
  let best = null, bestDistance = Infinity;
  for (const record of Object.values(records)) {
    if (!locationInsideSettlement(p.location, p.dimension.id, record, 10)) continue;
    const distance = Math.hypot(
      p.location.x - (record.x + record.w / 2),
      p.location.z - (record.z + record.w / 2));
    if (distance < bestDistance) { bestDistance = distance; best = record; }
  }
  return best;
}
// Tag the Hero wanted in every town that currently holds a warrant, so each
// town's guard AI (which filters on its own tag) hunts only the guilty player.
function syncWantedTags(p, records = getBounties(p)) {
  const wantedTowns = new Set(Object.values(records).map((r) => r.town));
  for (const town of BOUNTY_TOWNS) {
    const tag = BOUNTY_WANTED_TAG[town];
    try {
      if (wantedTowns.has(town)) p.addTag(tag);
      else p.removeTag(tag);
    } catch { }
  }
}
function assignedBountyGuards(p, record) {
  let guards = [];
  try {
    guards = p.dimension.getEntities({
      location: { x: record.x + record.w / 2, y: p.location.y, z: record.z + record.w / 2 },
      maxDistance: record.w + 72,
      families: ["fc_guard"],
    });
  } catch { return []; }
  return guards.filter((guard) => {
    try {
      return guard.getDynamicProperty("fc_bounty_owner") === p.id
        && guard.getDynamicProperty("fc_bounty_place") === record.key;
    } catch { return false; }
  });
}
function removeBountyGuards(p, record) {
  if (p.dimension.id !== record.dimension) return;
  for (const guard of assignedBountyGuards(p, record)) {
    try { guard.remove(); } catch { }
  }
}
function setBountyGuardMode(guard, mode, record) {
  const response = bountyResponseTier(record);
  try {
    guard.triggerEvent("fc:calm");
    if (guard.getDynamicProperty("fc_bounty_tier_applied") !== response.tier) {
      guard.triggerEvent(`fc:bounty_tier_${response.tier}`);
      guard.setDynamicProperty("fc_bounty_tier_applied", response.tier);
    }
    guard.triggerEvent(mode === "approach" ? "fc:bounty_approach" : "fc:bounty_hostile");
  } catch { }
}
function guardSpawnLocation(p) {
  const view = p.getViewDirection();
  for (let attempt = 0; attempt < 28; attempt++) {
    const angle = Math.random() * Math.PI * 2;
    const radius = 18 + Math.random() * 10;
    const dx = Math.cos(angle) * radius, dz = Math.sin(angle) * radius;
    const dot = (dx / radius) * view.x + (dz / radius) * view.z;
    if (attempt < 18 && dot > 0.15) continue;
    const x = Math.floor(p.location.x + dx);
    const z = Math.floor(p.location.z + dz);
    const y = groundY(p.dimension, x, z);
    if (y === null) continue;
    try {
      const feet = p.dimension.getBlock({ x, y, z });
      const head = p.dimension.getBlock({ x, y: y + 1, z });
      if (feet?.isAir && head?.isAir) return { x: x + 0.5, y, z: z + 0.5 };
    } catch { }
  }
  return null;
}
function spawnBountyGuards(p, record, mode, naturalGuardCount = 0) {
  if (p.dimension.id !== record.dimension) return;
  const targetCount = Math.max(0, bountyResponseTier(record).cap - naturalGuardCount);
  const existing = assignedBountyGuards(p, record);
  for (const guard of existing.slice(0, targetCount)) setBountyGuardMode(guard, mode, record);
  for (const guard of existing.slice(targetCount)) {
    try { guard.remove(); } catch { }
  }
  let missing = Math.max(0, targetCount - existing.length);
  while (missing-- > 0) {
    const location = guardSpawnLocation(p);
    if (!location) break;
    const guard = trySpawn(p.dimension, BOUNTY_GUARD_TYPE[record.town], location);
    if (!guard) continue;
    try {
      guard.setDynamicProperty("fc_bounty_owner", p.id);
      guard.setDynamicProperty("fc_bounty_place", record.key);
      guard.addTag("fc_bounty_guard");
      setBountyGuardMode(guard, mode, record);
    } catch { }
  }
}
function activateLocalGuards(p, record, mode) {
  syncWantedTags(p);
  const cap = bountyResponseTier(record).cap;
  const assignedIds = new Set(assignedBountyGuards(p, record).map((guard) => guard.id));
  let naturalGuards = [];
  try {
    naturalGuards = p.dimension.getEntities({
      location: p.location, maxDistance: 32, type: BOUNTY_GUARD_TYPE[record.town],
    }).filter((guard) => !assignedIds.has(guard.id))
      .sort((a, b) => Math.hypot(a.location.x - p.location.x, a.location.z - p.location.z)
        - Math.hypot(b.location.x - p.location.x, b.location.z - p.location.z));
  } catch { }
  const selected = naturalGuards.slice(0, cap);
  for (const guard of selected) setBountyGuardMode(guard, mode, record);
  for (const guard of naturalGuards.slice(cap)) {
    try {
      guard.triggerEvent("fc:bounty_calm");
      guard.setDynamicProperty("fc_bounty_tier_applied", 0);
    } catch { }
  }
  spawnBountyGuards(p, record, mode, selected.length);
}
function markBountyHostile(p, record) {
  const records = getBounties(p);
  const current = records[record.key];
  if (!current) return;
  current.enforcement = "hostile";
  current.expiresAtMs = Date.now() + BOUNTY_TIMER_START_MS;   // resisting restarts the clock
  setBounties(p, records);
  bountyDemand.delete(p.id);
  activateLocalGuards(p, current, "hostile");
}
// Activate the right enforcers for a warrant: the town watch in settlements,
// the Guild's own standing defenders on Guild ground.
function activateEnforcers(p, record, mode) {
  if (record.town === GUILD_TOWN_KEY) rallyGuildDefenders(p);
  else activateLocalGuards(p, record, mode);
}
// THE unified crime entry point. Every punch and every kill runs through here:
// it raises the bounty for the responsible jurisdiction (town OR the Heroes'
// Guild) by a severity-scaled amount, tops up the countdown that clears the
// warrant, and rouses the local enforcers. Returns false if the place is not
// policed (so the caller can fall back to rousing whoever is nearby).
function accrueCrime(p, victim, severity) {   // severity: "punch" | "kill"
  const kind = bountyCrimeKind(victim);       // "civilian" | "guard" | null
  if (!kind) return false;
  const jur = settlementForCrime(p, victim);
  if (!jur) return false;
  const isGuild = jur.town === GUILD_TOWN_KEY;
  if (!isGuild && !BOUNTY_GUARD_TYPE[jur.town]) return false;

  const now = Date.now();
  const records = getBounties(p);
  const existed = !!records[jur.key];
  const record = records[jur.key] ?? {
    ...jur, amount: 0, civilianKills: 0, guardKills: 0, punches: 0,
    expiresAtMs: 0, enforcement: "approach",
  };
  const priorStars = bountyHeatLevel(record);

  const addAmount = BOUNTY_AMOUNT[severity][kind];
  record.amount = Math.min(9999, record.amount + addAmount);
  if (severity === "kill") {
    if (kind === "guard") record.guardKills++; else record.civilianKills++;
  } else {
    record.punches = (record.punches ?? 0) + 1;
  }
  // Top up the countdown: extend from whatever time is left (or from now for a
  // fresh warrant), capped. Every crime buys the law more time to hunt you.
  const floor = existed ? Math.max(record.expiresAtMs, now) : now + BOUNTY_TIMER_START_MS;
  record.expiresAtMs = Math.min(now + BOUNTY_TIMER_MAX_MS, floor + BOUNTY_TIME_MS[severity]);
  // Murder, or any violence against a guard / guild defender, is an immediate
  // lethal hunt; merely cuffing a civilian only brings the watch over to fine you.
  const hostile = severity === "kill" || kind === "guard" || isGuild;
  if (record.enforcement !== "hostile") record.enforcement = hostile ? "hostile" : "approach";
  records[jur.key] = record;
  setBounties(p, records);

  const stars = bountyHeatLevel(record);
  refreshWantedHud(p, dominantBounty(records), now);
  showHeroActionBar(p, `§4⚖ +${addAmount}g §8· §6${record.amount}g §8· §e${"★".repeat(Math.max(1, stars))} §8· ${formatBountyTime(record.expiresAtMs - now)}`, 45);
  if (!existed) {
    p.sendMessage(severity === "kill"
      ? `§4⚖ MURDER WITNESSED — you are WANTED in ${record.name}.`
      : `§4⚖ ASSAULT WITNESSED — you are WANTED in ${record.name}.`);
    try { p.playSound("raid.horn", { volume: 0.7, pitch: 1.1 }); } catch { }
  } else if (stars > priorStars) {
    p.sendMessage(`§4⚖ Your wanted level in ${record.name} rises to §e${"★".repeat(stars)}§4.`);
    try { p.playSound("raid.horn", { volume: 0.5, pitch: 1.0 + stars * 0.05 }); } catch { }
  }
  activateEnforcers(p, record, record.enforcement === "hostile" ? "hostile" : "approach");
  return true;
}
function protectedFromJail(item) {
  if (!item) return false;
  return item.typeId === "fc:guild_seal"
    || item.typeId === "wd:will_focus"
    || item.typeId === "fc:summoners_grimoire"
    || item.typeId.startsWith("fc:spell_");
}
function confiscateForJail(p) {
  const preserved = [];
  const container = inv(p);
  if (container) {
    for (let slot = 0; slot < container.size; slot++) {
      const item = container.getItem(slot);
      if (protectedFromJail(item)) preserved.push(item);
      container.setItem(slot, undefined);
    }
  }
  const equippable = p.getComponent("minecraft:equippable");
  if (equippable) {
    try {
      const offhand = equippable.getEquipment(EquipmentSlot.Offhand);
      if (protectedFromJail(offhand)) preserved.push(offhand);
    } catch { }
    for (const slot of [EquipmentSlot.Head, EquipmentSlot.Chest, EquipmentSlot.Legs,
      EquipmentSlot.Feet, EquipmentSlot.Offhand]) {
      try { equippable.setEquipment(slot, undefined); } catch { }
    }
  }
  for (const item of preserved) {
    try {
      const leftover = container?.addItem(item);
      if (leftover) p.dimension.spawnItem(leftover, p.location);
    } catch { }
  }
  ensureGuildSeal(p);
}
function outsideSettlementLocation(p, record) {
  const distances = [
    { side: "west", value: Math.abs(p.location.x - record.x) },
    { side: "east", value: Math.abs(p.location.x - (record.x + record.w)) },
    { side: "north", value: Math.abs(p.location.z - record.z) },
    { side: "south", value: Math.abs(p.location.z - (record.z + record.w)) },
  ].sort((a, b) => a.value - b.value);
  let x = Math.max(record.x + 1, Math.min(record.x + record.w - 1, p.location.x));
  let z = Math.max(record.z + 1, Math.min(record.z + record.w - 1, p.location.z));
  if (distances[0].side === "west") x = record.x - 14;
  else if (distances[0].side === "east") x = record.x + record.w + 14;
  else if (distances[0].side === "north") z = record.z - 14;
  else z = record.z + record.w + 14;
  const y = groundY(p.dimension, Math.floor(x), Math.floor(z)) ?? Math.floor(p.location.y);
  return { x: Math.floor(x) + 0.5, y, z: Math.floor(z) + 0.5 };
}
function clearSettlementBounty(p, placeKey, reason) {
  const records = getBounties(p);
  const record = records[placeKey];
  if (!record) return;
  if (record.town === GUILD_TOWN_KEY) calmGuildDefenders(p);
  else removeBountyGuards(p, record);
  delete records[placeKey];
  setBounties(p, records);
  bountyDemand.delete(p.id);
  syncWantedTags(p, records);
  refreshWantedHud(p, dominantBounty(records));
  if (reason) p.sendMessage(`§a⚖ ${record.name} bounty cleared — ${reason}.`);
}
function sendToJail(p, record) {
  const release = outsideSettlementLocation(p, record);
  confiscateForJail(p);
  clearSettlementBounty(p, record.key);
  p.teleport(release);
  showHeroTitle(p, "§8SENTENCED", {
    fadeInDuration: 5, stayDuration: 50, fadeOutDuration: 15,
    subtitle: `§7Released outside ${record.name}; possessions confiscated`,
  });
  p.sendMessage("§7The guards release you beyond the town limits with only your Guild Seal and Will powers.");
}
function demandBountyResolution(p, record) {
  const records = getBounties(p);
  const current = records[record.key];
  if (!current) return;
  const state = bountyDemand.get(p.id);
  if (state) state.prompted = true;
  const kills = bountyKillCount(current);
  const charge = kills > 0 ? `${kills} deaths` : "assaulting the townsfolk";
  new ActionFormData()
    .title(`§4Warrant — ${current.name}`)
    .body([
      `§c"Hold there. You owe ${current.amount} gold for ${charge}."`,
      "",
      `§7Your purse: §6${countItem(p, "fc:gold_coin")} gold`,
      "§7Pay the warrant, surrender your possessions and accept exile, or resist arrest.",
    ].join("\n"))
    .button(`§6Pay ${current.amount} gold`)
    .button("§8Go to jail")
    .button("§4Resist arrest")
    .show(p).then((response) => {
      if (!getBounties(p)[current.key]) return;
      if (!response.canceled && response.selection === 0) {
        if (removeItem(p, "fc:gold_coin", current.amount)) {
          clearSettlementBounty(p, current.key, "fine paid");
          try { p.playSound("random.orb", { pitch: 0.8 }); } catch { }
          return;
        }
        p.sendMessage("§cYou cannot pay the full bounty. The guards draw their weapons.");
      } else if (!response.canceled && response.selection === 1) {
        sendToJail(p, current);
        return;
      }
      p.sendMessage("§4Guard: \"Then you leave us no choice!\"");
      markBountyHostile(p, current);
    }).catch(() => {
      const pending = bountyDemand.get(p.id);
      if (pending?.placeKey === current.key) pending.prompted = false;
    });
}
function beginBountyDemand(p, record) {
  activateLocalGuards(p, record, "approach");
  bountyDemand.set(p.id, { placeKey: record.key, startedTick: TICKS(), prompted: false });
}

system.runInterval(() => {
  const now = Date.now();
  for (const p of world.getPlayers()) {
    const records = getBounties(p);
    let changed = false;

    // The countdown runs EVERYWHERE — committing more crime tops it up, but left
    // alone every warrant ticks down and fades on its own.
    for (const [key, record] of Object.entries(records)) {
      if (!(record.expiresAtMs > 0)) { record.expiresAtMs = now + BOUNTY_TIMER_START_MS; changed = true; }
      if (now >= record.expiresAtMs) {
        if (record.town === GUILD_TOWN_KEY) calmGuildDefenders(p);
        else removeBountyGuards(p, record);
        delete records[key];
        bountyDemand.delete(p.id);
        p.sendMessage(`§a⚖ Your wanted level in ${record.name} has faded.`);
        try { p.playSound("random.orb", { pitch: 0.7 }); } catch { }
        changed = true;
      }
    }
    if (changed) setBounties(p, records);
    syncWantedTags(p, records);

    // The most serious warrant drives the on-screen stars + countdown.
    const dominant = dominantBounty(records);
    refreshWantedHud(p, dominant, now);
    if (!dominant) { bountyDemand.delete(p.id); continue; }

    // Enforce each warrant whose jurisdiction the Hero currently stands in.
    for (const record of Object.values(records)) {
      if (record.town === GUILD_TOWN_KEY) {
        if (isInsideGuild(p.location, p.dimension.id)) rallyGuildDefenders(p);
        continue;
      }
      if (!locationInsideSettlement(p.location, p.dimension.id, record, 10)) continue;
      if (record.enforcement === "hostile") {
        const cdKey = `${p.id}|${record.key}`;
        if (TICKS() - (bountySpawnCooldown.get(cdKey) ?? -9999) >= 100) {
          bountySpawnCooldown.set(cdKey, TICKS());
          activateLocalGuards(p, record, "hostile");
        }
      } else {                                   // "approach" — the watch comes to fine you
        let pending = bountyDemand.get(p.id);
        if (!pending || pending.placeKey !== record.key) {
          beginBountyDemand(p, record);
          pending = bountyDemand.get(p.id);
        }
        if (pending && !pending.prompted) {
          let guardClose = false;
          try {
            guardClose = p.dimension.getEntities({
              location: p.location, maxDistance: 9, type: BOUNTY_GUARD_TYPE[record.town],
            }).length > 0;
          } catch { }
          if (guardClose || TICKS() - pending.startedTick >= 120) demandBountyResolution(p, record);
        }
      }
    }
  }
}, 20);

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

// Guards enforce active local warrants. Their AI filters on town-specific
// player tags, so a wanted Hero does not make guards attack innocent players.
system.runInterval(() => {
  const wantedByDimension = new Map();
  for (const p of world.getPlayers()) {
    const records = getBounties(p);
    syncWantedTags(p, records);
    for (const record of Object.values(records)) {
      if (record.town === GUILD_TOWN_KEY) continue;   // the Guild fields its own defenders
      if (!locationInsideSettlement(p.location, p.dimension.id, record, 10)) continue;
      const wanted = wantedByDimension.get(p.dimension.id) ?? [];
      wanted.push({ player: p, record });
      wantedByDimension.set(p.dimension.id, wanted);
    }
  }
  for (const p of world.getPlayers()) {
    let guards = [];
    try {
      guards = p.dimension.getEntities({
        location: p.location,
        maxDistance: BOUNTY_GUARD_DETECTION_RADIUS,
        families: ["fc_guard"],
      });
    } catch { }
    const wanted = wantedByDimension.get(p.dimension.id) ?? [];
    for (const guard of guards) {
      const town = GUARD_TOWN[guard.typeId];
      if (!town) continue;
      const hasNearbyWarrant = wanted.some(({ player, record }) => record.town === town
        && Math.hypot(player.location.x - guard.location.x, player.location.z - guard.location.z)
          <= BOUNTY_GUARD_DETECTION_RADIUS);
      if (!hasNearbyWarrant) {
        try {
          guard.triggerEvent("fc:bounty_calm");
          guard.triggerEvent("fc:calm");
          guard.setDynamicProperty("fc_bounty_tier_applied", 0);
        } catch { }
      }
    }
  }
}, 80);

// ---------------------------------------------------------------------------
// ASSAULTING FRIENDLY NPCs — they no longer stand there and take it. Striking a
// townsperson, guard or guild member triggers the reaction AI that already lives
// on every social NPC (fc:react_flee / fc:react_attack) and raises local heat.
// Per the owner's call: civilians FLEE and summon protectors; guards, guild
// members and your own hired blades FIGHT BACK; inside the Guild it's the Guild's
// own defenders that respond, governed by a per-Hero Guild Heat meter.
// ---------------------------------------------------------------------------
const CIVILIAN_FLEE_TICKS = 220;  // ~11s of panic before a civilian settles
const GUARD_AGGRO_TICKS = 320;    // ~16s of hunting before a defender stands down

function isAssaultableNpc(e) {
  try {
    if (!e || e.typeId === "minecraft:player") return false;
    return entityHasFamily(e, "fc_friendly");
  } catch { return false; }
}
// Combatants that draw steel when struck (rather than flee): town guards, the
// Hero's own mercenaries, and — anywhere — the Guild's defenders.
function isGuildDefenderType(e) {
  try {
    return e.typeId === "fc:guildmaster" || e.typeId === "fc:maze"
      || entityHasFamily(e, "fc_guild") || entityHasFamily(e, "fc_guard");
  } catch { return false; }
}
function aggravate(npc, event, ticks) {
  try { npc.triggerEvent(event); } catch { }
  try { npc.addTag("fc_aggravated"); } catch { }
  try { npc.setDynamicProperty("fc_aggro_until", TICKS() + ticks); } catch { }
}
function calmNpc(npc) {
  try { npc.triggerEvent("fc:react_neutral"); } catch { }
  try { npc.removeTag("fc_aggravated"); } catch { }
  try { npc.setDynamicProperty("fc_aggro_until", undefined); } catch { }
}
// When a civilian is struck, any guard or guild defender nearby comes to enforce.
function alertProtectors(victim) {
  let guards = [];
  try {
    guards = victim.dimension.getEntities({
      location: victim.location, maxDistance: 22, families: ["fc_friendly"],
    });
  } catch { }
  for (const g of guards) {
    if (isGuildDefenderType(g)) aggravate(g, "fc:react_attack", GUARD_AGGRO_TICKS);
  }
}
function isInsideGuild(loc, dimensionId) {
  if (dimensionId && dimensionId !== "minecraft:overworld") return false;
  const b = guildBounds();
  if (!b || !loc) return false;
  return loc.x >= b.minX && loc.x <= b.maxX
    && loc.z >= b.minZ && loc.z <= b.maxZ
    && loc.y >= b.minY && loc.y <= b.maxY;
}

// Coalesce a flurry of hits / continuous damage on one victim so each distinct
// swing counts once toward the bounty (rather than every damage tick).
const assaultCd = new Map();   // `${playerId}|${victimId}` -> tick

function handlePlayerAssault(p, tgt) {
  if (!isAssaultableNpc(tgt)) return;
  let loc; try { loc = tgt.location; } catch { return; }
  void loc;
  // Their opinion of you sours, and they react — defenders fight, others flee.
  const fightsBack = isGuildDefenderType(tgt) || entityHasFamily(tgt, "fc_ally");
  aggravate(tgt, fightsBack ? "fc:react_attack" : "fc:react_flee",
    fightsBack ? GUARD_AGGRO_TICKS : CIVILIAN_FLEE_TICKS);

  const cdKey = `${p.id}|${tgt.id}`;
  const fresh = TICKS() - (assaultCd.get(cdKey) ?? -9999) >= 6;
  assaultCd.set(cdKey, TICKS());
  if (!fresh) return;            // same swing / continuous damage — already counted

  try { if (typeof tgt.getProperty("fc:love_hate") === "number") setNpcLove(tgt, npcLove(tgt) - 14); } catch { }
  // Every blow adds to your bounty (severity-scaled), tops up the wanted
  // countdown and rouses the local enforcers — towns and the Guild alike.
  if (bountyCrimeKind(tgt)) {
    if (!accrueCrime(p, tgt, "punch")) alertProtectors(tgt);
  } else {
    alertProtectors(tgt);         // ally / wilderness fallback (no warrant applies)
  }
}

// ---------------------------------------------------------------------------
// Order on the Heroes' Guild grounds is kept by the Guild's own standing
// defenders (Guildmaster, Maze, the apprentices, the gate guards). They are
// roused by the unified bounty system: a Guild warrant rallies them, and they
// stand down when the warrant is paid off or its countdown fades.
// ---------------------------------------------------------------------------
function guildDefendersNear(p, tags) {
  const b = guildBounds();
  if (!b) return [];
  const opts = {
    location: { x: (b.minX + b.maxX) / 2, y: b.base.y, z: (b.minZ + b.maxZ) / 2 },
    maxDistance: Math.max(b.maxX - b.minX, b.maxZ - b.minZ),
    families: ["fc_friendly"],
  };
  if (tags) opts.tags = tags;
  let ents = [];
  try { ents = p.dimension.getEntities(opts); } catch { }
  return ents.filter(isGuildDefenderType);
}
function rallyGuildDefenders(p) {
  for (const e of guildDefendersNear(p)) aggravate(e, "fc:react_attack", 200);
}
function calmGuildDefenders(p) {
  for (const e of guildDefendersNear(p, ["fc_aggravated"])) calmNpc(e);
}

// Aggravated NPCs return to their daily routine once enough time passes without
// fresh provocation. Guild defenders are kept hot by the active Guild warrant in
// the bounty loop, so this only calms them after that warrant has faded.
system.runInterval(() => {
  const handled = new Set();
  for (const p of world.getPlayers()) {
    let ents = [];
    try { ents = p.dimension.getEntities({ location: p.location, maxDistance: 64, tags: ["fc_aggravated"] }); } catch { continue; }
    for (const e of ents) {
      if (handled.has(e.id)) continue;
      handled.add(e.id);
      let until; try { until = e.getDynamicProperty("fc_aggro_until"); } catch { continue; }
      if (typeof until === "number" && TICKS() >= until) calmNpc(e);
    }
  }
}, 40);

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
// World decoration: deterministic, biome-aware region structures. Driven by the
// region sweep + maybePlace below — as the Hero explores, each REGION cell rolls
// at most one of these and grades it into the surrounding land.
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
const STRUCTS_TOTAL_W = STRUCTS.reduce((a, s) => a + s.weight, 0);

// Stable 0..1 hash so the same region always rolls the same build — no two
// players (or relogs) ever generate a region differently.
function hash2(x, z) {
  let h = ((x | 0) * 374761393 + (z | 0) * 668265263) ^ 1407;
  h = (h ^ (h >> 13)) * 1274126177;
  h = h ^ (h >> 16);
  return ((h >>> 0) % 100000) / 100000;
}
function pickStruct(h) {
  let r = h * STRUCTS_TOTAL_W;
  for (const s of STRUCTS) { r -= s.weight; if (r < 0) return s; }
  return STRUCTS[STRUCTS.length - 1];
}

// Classify the natural ground at a point into the categories STRUCTS.surf uses,
// so a build only settles where it belongs (a coast camp on sand, a tomb on
// stone, a village on grass). Returns null over water/void so nothing places in
// a lake. "dark" (dread-themed sites) is treated as at home on grass or rock.
function surfaceCategory(dim, x, z) {
  const y = groundY(dim, x, z);
  if (y === null) return null;
  let t; try { t = dim.getBlock({ x, y: y - 1, z })?.typeId ?? ""; } catch { return null; }
  if (t.includes("water") || t.includes("ice")) return null;
  if (t.includes("snow")) return "snow";
  if (t.includes("sand")) return "sand";
  if (t.includes("stone") || t.includes("andesite") || t.includes("granite") || t.includes("diorite")
    || t.includes("gravel") || t.includes("tuff") || t.includes("deepslate") || t.includes("cobblestone")
    || t.includes("calcite")) return "rock";
  if (t.includes("grass") || t.includes("dirt") || t.includes("podzol") || t.includes("moss")
    || t.includes("mycelium") || t.includes("mud")) return "grass";
  return "grass";
}
function surfMatch(surf, cat) {
  if (!cat) return false;
  if (surf.includes(cat)) return true;
  return surf.includes("dark") && (cat === "grass" || cat === "rock");
}
function cullisLabel(id) {
  const m = {
    "fc:oakvale_village": "Oakvale", "fc:bowerstone_market": "Bowerstone",
    "fc:knothole_glade": "Knothole Glade", "fc:hook_coast": "Hook Coast",
    "fc:power_oakvale_quay": "Oakvale Quay", "fc:power_snowspire_oracle": "Snowspire Oracle",
    "fc:power_necropolis": "Necropolis", "fc:focus_site": "Focus Site",
  };
  return m[id] ?? id.replace("fc:", "").replace(/_/g, " ");
}

// World generation sweep: as the Hero explores, each REGION cell deterministically
// rolls at most one POI from STRUCTS, settles it onto the land, and dresses it
// (loot, mobs, Demon Door faces, Cullis travel points). Each placed build runs
// the same blendTerrain + skirtTerrain grading as the Guild, so its edges meet
// the surrounding biome (beaches into water, slopes up to mountains) instead of
// dropping off. Idempotent per region via the `fc_rgn_*` flag.
system.runInterval(() => {
  for (const p of world.getPlayers()) {
    if (p.dimension.id !== "minecraft:overworld") continue;
    const rx = Math.floor(p.location.x / REGION), rz = Math.floor(p.location.z / REGION);
    for (let dx = -1; dx <= 1; dx++) {
      for (let dz = -1; dz <= 1; dz++) {
        try { maybePlace(p, rx + dx, rz + dz); } catch { /* one bad region never stalls the sweep */ }
      }
    }
  }
}, 80);

function maybePlace(p, rx, rz) {
  const key = `fc_rgn_${rx}_${rz}`;
  if (world.getDynamicProperty(key)) return;

  // deterministic jittered anchor (NW corner) well inside the region cell
  const jx = Math.floor(hash2(rx * 7 + 1, rz) * (REGION - 56)) + 28;
  const jz = Math.floor(hash2(rx, rz * 7 + 1) * (REGION - 56)) + 28;
  const x = rx * REGION + jx, z = rz * REGION + jz;

  // not every cell gets a build — retire empties immediately (deterministic, no
  // chunks needed) so the sweep never revisits them
  if (hash2(rx + 31, rz + 17) >= 0.5) { world.setDynamicProperty(key, 1); return; }
  const pick = pickStruct(hash2(rx * 13 + 5, rz * 13 + 9));
  if (!pick) { world.setDynamicProperty(key, 1); return; }
  const w = pick.w;

  // act only when the cell is in the live placement window — close enough that
  // its chunks are loaded, far enough not to pop in the Hero's face
  const cxw = x + (w >> 1), czw = z + (w >> 1);
  const dist = Math.hypot(cxw - p.location.x, czw - p.location.z);
  if (dist > 120 || dist < 28) return;            // outside window — retry next sweep

  const dim = p.dimension;
  const cy = sampleGroundY(dim, x, z, w, w);       // null over water / chunks not ready
  if (cy === null) return;                          // retry once the ground is there
  if (!surfMatch(pick.surf, surfaceCategory(dim, cxw, czw))) { world.setDynamicProperty(key, 1); return; }
  if (tooCloseToExisting(x, z, w, 24)) { world.setDynamicProperty(key, 1); return; }

  const pY = cy - 1;                                // baked ground (local y0) flush with the land
  try {
    world.structureManager.place(pick.id, dim, { x, y: pY, z });
  } catch { return; }                               // chunk-edge race — retry next sweep
  world.setDynamicProperty(key, 1);
  recordPlace(x, z, w, pick.id, pick.theme);

  // settle into the land, then grade the edges out to meet the biome
  try {
    blendTerrain(dim, x, pY, z, w, w);
    skirtTerrain(dim, x, pY, z, w, w, Math.max(6, Math.min(16, Math.round(w / 3))));
    fillLootChests(dim, x, pY, z, w, 24, w, pick.id);
  } catch { }

  // population + props — best-effort, never aborts a placement that succeeded
  try {
    const floorY = pY + 1;
    for (const mtype of pick.mobs ?? []) {
      trySpawn(dim, mtype, { x: x + 4 + Math.random() * (w - 8), y: floorY, z: z + 4 + Math.random() * (w - 8) });
    }
    if (pick.door) {
      // the arch opening is centred on the face wall (local x=w/2, z=5)
      const dl = { x: cxw + 0.5, y: floorY, z: z + 5.5 };
      ensureDemonDoor(dim, dl, z + 2);
      recordDemonDoor({ x: cxw, y: floorY, z: z + 5 }, z + 2);
    }
    if (pick.cullis) registerCullis(`${cullisLabel(pick.id)} (${x},${z})`, { x: cxw, y: floorY, z: czw });
  } catch { }
}

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

// Sample a 5x5 grid across the footprint and use its median actual-terrain
// height. Trees and ground cover are ignored, and requiring 60% coverage keeps
// placement waiting until enough of the footprint is loaded.
function sampleGroundY(dim, x0, z0, w, d, allowLiquid = false) {
  const pts = [];
  for (let gx = 0; gx < 5; gx++) {
    for (let gz = 0; gz < 5; gz++) {
      pts.push([
        x0 + 1 + Math.round((w - 3) * gx / 4),
        z0 + 1 + Math.round((d - 3) * gz / 4),
      ]);
    }
  }
  const ys = [];
  for (const [x, z] of pts) {
    const y = naturalGroundY(dim, x, z, allowLiquid);
    if (y !== null) ys.push(y);
  }
  if (ys.length < Math.ceil(pts.length * 0.6)) return null;
  ys.sort((a, b) => a - b);
  return ys[Math.floor(ys.length / 2)];
}

function blendTerrain(dim, x0, y0, z0, w, d, skip, onDone) {
  // foundation fill: every column under the structure (plus a 1-block
  // border) gets filled from the structure's base down to solid ground —
  // no gaps below buildings, no water pockets trapped underneath.
  // `skip(x,z)` (optional) masks out columns that must stay hollow — e.g. the
  // Guild-cave spiral shaft, whose freshly-carved well would otherwise be
  // back-filled with rock (the "stairs filled in at the top" bug).
  const work = function* () {
    for (let x = x0 - 1; x <= x0 + w; x++) {
      for (let z = z0 - 1; z <= z0 + d; z++) {
        if (skip && skip(x, z)) continue;
        yield* foundationColumn(dim, x, y0, z);
      }
      yield;
    }
    try { onDone?.(); } catch { }
  };
  try { system.runJob(work()); } catch { try { onDone?.(); } catch { } }
}

function* foundationColumn(dim, x, y0, z) {
  const lo = Math.max(-64, y0 - 64);
  for (let y = y0 - 1; y >= lo; y--) {
    let b;
    try { b = dim.getBlock({ x, y, z }); } catch { return; }
    if (!b) return;
    if (!b.isAir && !b.isLiquid && !isSkirtVeg(b.typeId)) break;
    const depth = y0 - y;
    const fill = depth <= 3 ? "minecraft:dirt"
      : (depth <= 18 ? "minecraft:stone" : "minecraft:deepslate");
    try { b.setType(fill); } catch { return; }
    yield;
  }
}

// Vegetation / cover that should NOT count as "the ground" when sampling a
// column's natural surface — trees and plants sit *on* the land, not in it.
function isSkirtVeg(t) {
  return t.includes("leaves") || t.includes("log") || t.includes("tallgrass")
    || t.includes("tall_grass") || t.includes("short_grass") || t.includes("double_plant")
    || t.includes("fern") || t.includes("flower") || t.includes("sapling")
    || t.includes("mushroom") || t.includes("vine") || t.includes("bamboo")
    || t.includes("deadbush") || t.includes("sugar_cane") || t.includes("cactus")
    || t.includes("roots") || t.includes("azalea") || t.includes("cocoa")
    || t.includes("kelp") || t.includes("seagrass") || t.includes("lily_pad");
}

// Read a column's natural surface so the skirt can meet whatever the biome put
// there. Returns { y, top, water, waterY, snowy } where `y` is the first AIR
// cell above the highest real solid block (so the solid top is y-1), `top` is
// that solid's id (used to match the biome), and water/waterY describe any open
// liquid resting above it (lake/sea/river). Returns null if the column has no
// solid ground in the scanned window.
function columnScan(dim, x, z, hi, lo) {
  let waterY = null, snowy = false, coverTop = null, coverBottom = null;
  for (let y = hi; y > lo; y--) {
    let b; try { b = dim.getBlock({ x, y, z }); } catch { return null; }
    if (!b || b.isAir) continue;
    if (b.isLiquid) { if (waterY === null) waterY = y; continue; }
    const t = b.typeId;
    if (t === "minecraft:snow_layer" || isSkirtVeg(t)) {
      snowy ||= t === "minecraft:snow_layer";
      coverTop ??= y;
      coverBottom = y;
      continue;                                      // trees/plants don't count as ground
    }
    return {
      y: y + 1,
      top: t,
      water: waterY !== null,
      waterY,
      snowy,
      coverTop,
      coverBottom,
    };
  }
  return null;
}

function clearSkirtCover(dim, x, z, fromY, toY) {
  if (fromY === null || toY === null) return;
  for (let y = fromY; y <= toY; y++) {
    let b;
    try { b = dim.getBlock({ x, y, z }); } catch { continue; }
    if (b && (b.typeId === "minecraft:snow_layer" || isSkirtVeg(b.typeId))) {
      try { b.setType("minecraft:air"); } catch { }
    }
  }
}

function dominantGuildWaterY(dim, base) {
  const radius = GUILD_TERRAIN_RADIUS + 2;
  const maxX = base.x + GUILD.sx - 1;
  const maxZ = base.z + GUILD.sz - 1;
  const hi = Math.min(319, base.y + 96);
  const lo = Math.max(-64, base.y - 96);
  const samples = [];
  for (let x = base.x; x <= maxX; x += 12) {
    samples.push([x, base.z - radius], [x, maxZ + radius]);
  }
  for (let z = base.z; z <= maxZ; z += 12) {
    samples.push([base.x - radius, z], [maxX + radius, z]);
  }
  const tally = new Map();
  let loaded = 0;
  for (const [x, z] of samples) {
    const info = columnScan(dim, x, z, hi, lo);
    if (info) loaded++;
    if (!info?.water) continue;
    tally.set(info.waterY, (tally.get(info.waterY) ?? 0) + 1);
  }
  let bestY = null, bestCount = 0;
  for (const [y, count] of tally) {
    if (count > bestCount) { bestY = y; bestCount = count; }
  }
  return {
    ready: loaded >= Math.ceil(samples.length * 0.6),
    waterY: bestCount >= 6 ? bestY : null,
  };
}

// Terrain v2 raised ocean columns to sea level with unsupported sand, creating
// the large square beach wall and collapse holes. Generated columns are deep
// vertical runs of falling sand ending exactly at the dominant waterline.
function repairLegacyGuildOcean(dim, base, onDone) {
  if (world.getDynamicProperty("fc_guild_ocean_cleanup_v1")) {
    try { onDone?.(); } catch { }
    return;
  }
  const scan = dominantGuildWaterY(dim, base);
  if (!scan.ready) {
    system.runTimeout(() => repairLegacyGuildOcean(dim, base, onDone), 20);
    return;
  }
  const waterY = scan.waterY;
  if (waterY === null) {
    world.setDynamicProperty("fc_guild_ocean_cleanup_v1", true);
    try { onDone?.(); } catch { }
    return;
  }
  const maxX = base.x + GUILD.sx - 1;
  const maxZ = base.z + GUILD.sz - 1;
  const radius = GUILD_TERRAIN_RADIUS;
  const work = function* () {
    for (let x = base.x - radius; x <= maxX + radius; x++) {
      for (let z = base.z - radius; z <= maxZ + radius; z++) {
        const cx = Math.max(base.x, Math.min(maxX, x));
        const cz = Math.max(base.z, Math.min(maxZ, z));
        const dist = Math.hypot(x - cx, z - cz);
        if (dist < 1 || dist > radius) continue;
        // Falling sand may already have left air/water holes at the top. Look a
        // few blocks below the waterline for the remaining artificial column.
        let sandTopY = null, sandId = null;
        for (let y = waterY; y >= waterY - 8; y--) {
          let b;
          try { b = dim.getBlock({ x, y, z }); } catch { b = null; }
          if (!b) break;
          if (b.typeId === "minecraft:sand" || b.typeId === "minecraft:red_sand") {
            sandTopY = y;
            sandId = b.typeId;
            break;
          }
          if (!b.isAir && !b.isLiquid) break;
        }
        if (sandTopY === null || sandId === null) continue;
        let supportY = sandTopY;
        let run = 0;
        for (let y = sandTopY; y >= Math.max(-63, waterY - 64); y--) {
          let b;
          try { b = dim.getBlock({ x, y, z }); } catch { b = null; }
          if (!b || b.typeId !== sandId) { supportY = y; break; }
          run++;
        }
        if (run < 6) continue;
        try { dim.getBlock({ x, y: supportY + 1, z })?.setType(sandId); } catch { }
        for (let y = supportY + 2; y <= waterY; y++) {
          try { dim.getBlock({ x, y, z })?.setType("minecraft:water"); } catch { }
        }
        yield;
      }
      yield;
    }
    world.setDynamicProperty("fc_guild_ocean_cleanup_v1", true);
    try { onDone?.(); } catch { }
  };
  try { system.runJob(work()); } catch { try { onDone?.(); } catch { } }
}

// Pick fill/cap blocks that read as the same biome as the column's natural
// surface, so the transition ground looks like its surroundings instead of a
// generic dirt apron.
function skirtPalette(top, snowy) {
  const t = top || "";
  if (snowy || t.includes("snow")) return { cap: "minecraft:grass_block", fill: "minecraft:dirt", cover: "minecraft:snow_layer" };
  if (t.includes("sand") || t.includes("sandstone")) {
    const red = t.includes("red");
    return { cap: red ? "minecraft:red_sand" : "minecraft:sand", fill: red ? "minecraft:red_sandstone" : "minecraft:sandstone", cover: null };
  }
  if (t.includes("podzol")) return { cap: "minecraft:podzol", fill: "minecraft:dirt", cover: null };
  if (t.includes("mycelium")) return { cap: "minecraft:mycelium", fill: "minecraft:dirt", cover: null };
  if (t.includes("gravel")) return { cap: "minecraft:gravel", fill: "minecraft:stone", cover: null };
  if (t.includes("stone") || t.includes("andesite") || t.includes("granite") || t.includes("diorite")
    || t.includes("tuff") || t.includes("deepslate") || t.includes("cobblestone") || t.includes("calcite")) {
    return { cap: "minecraft:stone", fill: "minecraft:stone", cover: null };   // mountain / stony shore
  }
  return { cap: "minecraft:grass_block", fill: "minecraft:dirt", cover: null }; // temperate default
}

// Raise or carve a single column so its surface sits at targetY, capped with the
// biome surface block and resting on solid fill. `curTop` is the column's
// current highest solid block. Carving only removes what's above targetY (the
// skirt runs OUTSIDE the build footprint, so the structure is never touched).
function shapeColumn(dim, x, z, targetY, curTop, pal, cover) {
  const set = (y, id) => { try { dim.getBlock({ x, y, z })?.setType(id); } catch { } };
  if (targetY > curTop) {                       // low ground / water — raise up to the slope
    for (let y = curTop + 1; y <= targetY; y++) set(y, pal.fill);
  } else if (targetY < curTop) {                // higher ground (mountain) — pare it down to the slope
    for (let y = curTop; y > targetY; y--) set(y, "minecraft:air");
  }
  for (let y = targetY - 1; y >= targetY - 2; y--) {   // guarantee solid support under the new surface
    let b; try { b = dim.getBlock({ x, y, z }); } catch { b = null; }
    if (b && (b.isAir || b.isLiquid)) set(y, pal.fill);
  }
  set(targetY, pal.cap);
  if (cover) set(targetY + 1, cover);
  else {                                         // expose the cap: clear leftover plant/snow directly on top
    let a; try { a = dim.getBlock({ x, y: targetY + 1, z }); } catch { a = null; }
    if (a && !a.isAir && !a.isLiquid && (a.typeId === "minecraft:snow_layer" || isSkirtVeg(a.typeId))) set(targetY + 1, "minecraft:air");
  }
}

// Ring the footprint with a graded apron that *meets the surrounding land*
// rather than ending in a cliff. For every column out to `radius` we slope from
// the build's edge height (y0) toward that column's own natural height, so the
// ground steps DOWN to lower terrain and RISES UP to meet mountains. Water is
// turned into a sand beach that wades into the shoreline instead of dropping
// off. The cap matches the local biome (snow/sand/stone/grass) so the transition
// reads as nature, not a built plinth.
function skirtTerrain(dim, x0, y0, z0, w, d, radius, onDone) {
  const ease = (t) => t * t * (3 - 2 * t);            // smoothstep — a natural, settling curve
  const hi = Math.min(319, y0 + 96), lo = Math.max(-64, y0 - 80);
  // Structure dimensions are counts, so the occupied footprint ends at
  // x0+w-1 / z0+d-1. Treating x0+w or z0+d as interior leaves the first
  // positive-edge mountain column untouched and creates a vertical seam.
  const maxX = x0 + w - 1;
  const maxZ = z0 + d - 1;
  const work = function* () {
    for (let x = x0 - radius; x <= maxX + radius; x++) {
      for (let z = z0 - radius; z <= maxZ + radius; z++) {
        const cx = Math.max(x0, Math.min(maxX, x));
        const cz = Math.max(z0, Math.min(maxZ, z));
        const dist = Math.hypot(x - cx, z - cz);
        if (dist > radius || dist < 1) continue;
        const info = columnScan(dim, x, z, hi, lo);
        if (!info) continue;
        const t = ease(Math.min(1, dist / radius));     // 0 hugging the build → 1 out in the wild
        const curTop = info.y - 1;

        if (info.water) {
          // Return to the ORIGINAL seabed at the outside edge. Interpolating to
          // the waterline created a giant square sand wall around ocean builds.
          // Sand is only a supported cap; sandstone carries the shelf.
          const wy = info.waterY;
          const shelfY = Math.max(curTop, Math.round(y0 + (curTop - y0) * t));
          if (shelfY > curTop) {
            clearSkirtCover(dim, x, z, info.coverBottom, info.coverTop);
            shapeColumn(dim, x, z, shelfY, curTop,
              { cap: "minecraft:sand", fill: "minecraft:sandstone" }, null);
            for (let yy = shelfY + 1; yy <= wy; yy++) {
              try {
                const b = dim.getBlock({ x, y: yy, z });
                if (b?.isAir) b.setType("minecraft:water");
              } catch { }
            }
          }
          yield; continue;
        }

        // Land: interpolate from the platform height out to the column's own
        // natural height — rising to mountains, easing down to valleys.
        const targetY = Math.round(y0 + (curTop - y0) * t);
        const pal = skirtPalette(info.top, info.snowy);
        if (targetY !== curTop) {
          clearSkirtCover(dim, x, z, info.coverBottom, info.coverTop);
        }
        shapeColumn(dim, x, z, targetY, curTop, pal, pal.cover);
        yield;
      }
      yield;
    }
    try { onDone?.(); } catch { }
  };
  try { system.runJob(work()); } catch { try { onDone?.(); } catch { } }
}

function dressSurroundings(dim, x0, y0, z0, w, mood) {
  // Additional custom decoration stub
}

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

// Fable: The Lost Chapters menu dressing
const FABLE_RULE = "§8════════════§6❦§8════════════";
const FABLE_DOT = "§6❖ ";
function fableTitle(t) { return `§8‹§6❦§8› §6§l${t}§r §8‹§6❦§8›`; }

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
  if (!ev.initialSpawn) return;
  system.runTimeout(() => initHero(p), 20);
});

function initHero(p) {
  if (P.get(p, "fc_init", false)) return;
  P.set(p, "fc_init", true);
  P.set(p, "fc_will", 100);
  for (const it of ["fc:stick", "fc:guild_seal", "fc:quest_card",
    "fc:apprentice_torso", "fc:apprentice_legs", "fc:apprentice_boots",
    "fc:health_potion"]) giveItem(p, it, 1);
  giveItem(p, "fc:gold_coin", 5);
  p.onScreenDisplay.setTitle("§6Fablecraft", { fadeInDuration: 10, stayDuration: 70, fadeOutDuration: 20, subtitle: "§eReforged — Welcome to Albion" });
  p.sendMessage("§6═══ The Guildmaster ═══");
  p.sendMessage("§f\"Ah, the new apprentice wakes. Your §eGuild Seal§f opens the Hero menu. Use a §eQuest Card§f to begin your training. Albion is watching, little sparrow.\"");
  placeGuildNear(p);
}

function placeGuildNear(p) {
  if (world.getDynamicProperty("fc_guild_placed")) return;
  const dim = p.dimension;
  const base = { x: Math.floor(p.location.x) + 16, y: 0, z: Math.floor(p.location.z) + 16 };
  const y = groundY(dim, base.x + 22, base.z + 20);
  if (y === null) return;
  try {
    world.structureManager.place("fc:guild_hall", dim, { x: base.x, y, z: base.z });
    world.setDynamicProperty("fc_guild_placed", true);
    // recall point: the nave; training yard + cullis gate flank the hall
    world.setDynamicProperty("fc_guild_loc", JSON.stringify({ x: base.x + 22, y, z: base.z + 20 }));
    world.setDynamicProperty("fc_guild_train", JSON.stringify({ x: base.x + 38, y, z: base.z + 22 }));
    registerCullis("Heroes' Guild", { x: base.x + 6, y: y + 1, z: base.z + 20 });
    // Guildmaster presides over the Map Room; Maze studies by the Cullis
    // Gate; Theresa haunts the feast hall; a trader works the forecourt.
    trySpawn(dim, "fc:guildmaster", { x: base.x + 22, y: y + 1, z: base.z + 33 });
    trySpawn(dim, "fc:maze", { x: base.x + 9, y: y + 1, z: base.z + 20 });
    trySpawn(dim, "fc:theresa", { x: base.x + 30, y: y + 1, z: base.z + 20 });
    trySpawn(dim, "fc:trader", { x: base.x + 26, y: y + 1, z: base.z + 6 });
    fillLootChests(dim, base.x, y, base.z, 45, 26, 41, "fc:guild_hall");
    blendTerrain(dim, base.x, y, base.z, 45, 41);
    // wake the new Hero inside the Guild forecourt
    system.runTimeout(() => {
      try {
        p.teleport({ x: base.x + 22.5, y: y + 1, z: base.z + 6.5 },
          { facingLocation: { x: base.x + 22.5, y: y + 2, z: base.z + 20 } });
        p.sendMessage("§6⚔ You awaken at the Heroes' Guild. The Cullis Gate hums in the west yard; the Training Grounds wait in the east.");
      } catch { }
    }, 10);
  } catch { /* chunk not ready; retried by the structure sweep */ }
}

function trySpawn(dim, type, loc) { try { return dim.spawnEntity(type, loc); } catch { return undefined; } }

function groundY(dim, x, z) {
  for (let y = 120; y > 40; y--) {
    try {
      const b = dim.getBlock({ x, y, z });
      const below = dim.getBlock({ x, y: y - 1, z });
      if (b?.isAir && below && !below.isAir && !below.isLiquid) return y;
    } catch { return null; }
  }
  return null;
}

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

function applyAugment(p, item, augId) {
  // augment goes onto the weapon in the OFFHAND-free style: must hold weapon after sneak
  const c = inv(p);
  // find first fc weapon in hotbar that has a free slot
  for (let i = 0; i < 9; i++) {
    const w = c?.getItem(i);
    if (!w || !DATA.weapons[w.typeId]) continue;
    const wd = DATA.weapons[w.typeId];
    const lore = w.getLore() ?? [];
    const current = lore.filter((l) => l.startsWith(AUG_PREFIX));
    const slots = wd.slots ?? 0;
    if (slots <= 0 || current.length >= slots) continue;
    lore.push(`${AUG_PREFIX}${augId.charAt(0).toUpperCase() + augId.slice(1)} Augmentation`);
    w.setLore(lore);
    c.setItem(i, w);
    removeItem(p, `fc:${augId}_augment`, 1);
    p.playSound("random.anvil_use");
    p.sendMessage(`§6⬩ ${augId} augmentation bound to ${w.typeId.replace("fc:", "").replace(/_/g, " ")} §7(${current.length + 1}/${slots})`);
    return;
  }
  p.sendMessage("§7No weapon with a free augment slot in your hotbar.");
}

function removeAugments(p) {
  const c = inv(p);
  for (let i = 0; i < 9; i++) {
    const w = c?.getItem(i);
    if (!w || !DATA.weapons[w.typeId]) continue;
    const lore = (w.getLore() ?? []).filter((l) => !l.startsWith(AUG_PREFIX));
    if (lore.length === (w.getLore() ?? []).length) continue;
    w.setLore(lore);
    c.setItem(i, w);
    removeItem(p, "fc:augment_remover", 1);
    p.playSound("random.break");
    p.sendMessage("§7The augmentations crumble to dust.");
    return;
  }
  p.sendMessage("§7No augmented weapon found in your hotbar.");
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
  SPELL_FX[id]?.(p, lvl);
}

function foes(p, r) {
  return p.dimension.getEntities({ location: p.location, maxDistance: r, families: ["monster"] })
    .filter((e) => !(e.getComponent("minecraft:type_family")?.hasTypeFamily("fc_ally")));
}

const SPELL_FX = {
  enflame(p, lvl) {
    const r = 3 + lvl;
    ringParticles(p.dimension, p.location, r, "minecraft:mobflame_single");
    for (const e of foes(p, r)) { try { e.setOnFire(3 + lvl, true); e.applyDamage(4 + lvl * 2, { cause: EntityDamageCause.fire }); } catch { } }
  },
  fireball(p, lvl) {
    const dir = p.getViewDirection();
    const loc = { x: p.location.x + dir.x * 1.5, y: p.location.y + 1.5 + dir.y, z: p.location.z + dir.z * 1.5 };
    for (let i = 0; i < (lvl >= 3 ? 3 : 1); i++) {
      const fb = trySpawn(p.dimension, "minecraft:small_fireball", loc);
      const proj = fb?.getComponent("minecraft:projectile");
      if (proj) { proj.owner = p; proj.shoot({ x: dir.x * 1.4 + (i - 1) * 0.12, y: dir.y * 1.4, z: dir.z * 1.4 + (i - 1) * 0.12 }); }
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
  const f = new ActionFormData()
    .title(fableTitle("Hero of Albion"))
    .body([
      FABLE_RULE,
      `§7"${moralityTitle(p)}§7 — that is what they call you."`,
      `§8Renown §d${P.get(p, "fc_renown", 0)}  §8·  Gold §6${countItem(p, "fc:gold_coin")}`,
      FABLE_RULE,
    ].join("\n"))
    .button("§2❖ Stats & Personality", "textures/items/guild_seal")
    .button("§e❖ Quests", "textures/items/quest_card")
    .button("§c❖ Guild Training (Upgrades)", "textures/items/health_augment")
    .button("§9❖ Will Powers", "textures/items/spell_fireball")
    .button("§d❖ Titles & Renown", "textures/items/gold_coin")
    .button("§b❖ Factions & Standing", "textures/items/wedding_ring");
  f.show(p).then((r) => {
    if (r.canceled) return;
    [statsMenu, questMenu, trainMenu, spellMenu, titlesMenu, factionMenu][r.selection]?.(p);
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
    if (d > 46) return p.sendMessage("§7Training happens at the Guild — the Training Grounds in the east yard, or the Map Room. (Sneak+use the Seal to recall.)");
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
  f.button("§8❖ Back");
  f.show(p).then((r) => {
    if (r.canceled) return;
    if (r.selection >= ids.length) return heroMenu(p);
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

function titlesMenu(p) {
  const titles = P.getJ(p, "fc_titles", []);
  const body = [
    FABLE_RULE,
    `§dRenown: §f${P.get(p, "fc_renown", 0)}`,
    FABLE_RULE,
    titles.length ? "§6Titles:" : "§7No titles yet. Albion barely knows your name.",
    ...titles.map((t) => ` §e✦ ${t}`),
  ].join("\n");
  new ActionFormData().title(fableTitle("Titles & Renown")).body(body).button("§8❖ Back")
    .show(p).then((r) => { if (!r.canceled) heroMenu(p); });
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
    "fc:villager_farmer", "fc:mercenary",
    "fc:guard_bowerstone", "fc:guard_oakvale", "fc:guard_snowspire"];
  if (NPC_TYPES.includes(t)) { ev.cancel = true; system.run(() => npcTalk(p, target)); }
});

function doorPersona(door) {
  let idx = door.getDynamicProperty("fc_door_idx");
  if (idx === undefined) {
    idx = Math.abs(Math.floor(door.location.x * 31 + door.location.z * 17)) % DATA.demonDoors.length;
    door.setDynamicProperty("fc_door_idx", idx);
  }
  return DATA.demonDoors[idx];
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
  p.sendMessage(`§5${d.name}: §a"${d.success}"`);
  const dim = door.dimension, loc = door.location;
  dim.spawnParticle("minecraft:huge_explosion_emitter", loc);
  p.playSound("fc.door_rumble", { volume: 0.9 });
  for (const it of d.reward.items) giveItem(p, it.id, it.count);
  giveXp(p, "general", d.reward.xp);
  addRep(p, "guild", 5);
  addTitle(p, "Door-Speaker");
  p.onScreenDisplay.setTitle("§5Demon Door Opened", { fadeInDuration: 8, stayDuration: 60, fadeOutDuration: 15, subtitle: `§7${d.name}` });
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
    new ActionFormData().title("§6The Guildmaster")
      .body(`§o"${m > 200 ? "Albion sings of your kindness, Hero." : m < -200 ? "I hear dark whispers about you. Tread carefully." : "Your training continues, apprentice."}\n\nA Hero balances Strength, Skill and Will. Use Quest Cards to earn your renown. And do stop hitting the practice dummies with your forehead."`)
      .button("§eTake a Quest Card", "textures/items/quest_card")
      .button("§9Hero Menu")
      .button("§8Farewell")
      .show(p).then((r) => {
        if (r.canceled) return;
        if (r.selection === 0) { giveItem(p, "fc:quest_card", 1); p.sendMessage("§e✦ Quest Card received."); }
        if (r.selection === 1) heroMenu(p);
      });
  } else if (t === "fc:maze") {
    new MessageFormData().title("§5Maze")
      .body('§o"The Will is a muscle, Hero. Spell tomes hide in ruins and Demon Door hoards — each one a power your enemies will learn to dread. Visit the Oracle in the far snows, when you are ready for truths."')
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
    p.sendMessage(`§d Theresa: §o"${m >= 0 ? "I see many paths for you, and most are bright." : "Blood follows you like a stray dog, brother."} The blind see further than you'd think."`);
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
    p.sendMessage('§cBriar Rose: §o"Done staring? Demon Doors respond to deeds, not poetry. Multiplier 14 opens the Warrior\'s arch — if you can keep your footing."');
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
    new MessageFormData().title("§7Mercenary")
      .body('§o"Twenty gold and my blade walks with you. I don\'t do funerals — especially mine."')
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
  } else if (t === "fc:villager_albion" || t === "fc:villager_woman" || t === "fc:villager_farmer") {
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
    .button("§a❖ BUY").button("§e❖ SELL trophies").button("§8❖ Leave");
  f.show(p).then((r) => {
    if (r.canceled || r.selection === 2) return;
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
system.runInterval(() => {
  const sites = JSON.parse(world.getDynamicProperty("fc_cullis") ?? "[]");
  if (!sites.length) return;
  for (const p of world.getPlayers()) {
    const near = sites.find((s) => Math.hypot(p.location.x - s.x, p.location.z - s.z) < 2.4
      && Math.abs(p.location.y - s.y) < 4);
    if (!near) continue;
    if (!p.isSneaking) {
      p.onScreenDisplay.setActionBar("§b◈ Cullis Gate §7— sneak to focus your Will and travel");
      continue;
    }
    const last = cullisCd.get(p.id) ?? -9999;
    if (TICKS() - last < 80) continue;
    cullisCd.set(p.id, TICKS());
    cullisTravel(p, sites, near);
  }
}, 20);

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
const GUARD_TOWN = {
  "fc:guard_bowerstone": "bowerstone", "fc:guard_oakvale": "oakvale",
  "fc:guard_snowspire": "snowspire",
};
const VILLAGER_TOWN = {
  "fc:villager_albion": "bowerstone", "fc:villager_farmer": "oakvale",
  "fc:villager_woman": "snowspire",
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
// World decoration: deterministic region structures
// ---------------------------------------------------------------------------
const REGION = 160;
const STRUCTS = [
  { id: "fc:demon_door_arch", w: 23, chance: 0.16, door: true },
  { id: "fc:silver_chest_ruin", w: 13, chance: 0.34, loot: "ruin" },
  { id: "fc:bandit_camp", w: 33, chance: 0.50, mobs: ["fc:bandit", "fc:bandit", "fc:bandit_archer", "fc:twinblade"] },
  { id: "fc:graveyard", w: 25, chance: 0.62, mobs: ["fc:undead", "fc:undead_soldier", "fc:undead_knight"] },
  { id: "fc:focus_site", w: 13, chance: 0.70, cullis: true },
  { id: "fc:temple_avo", w: 17, chance: 0.76 },
  { id: "fc:chapel_skorm", w: 15, chance: 0.82 },
  { id: "fc:arena_ring", w: 27, chance: 0.86, mobs: ["fc:hobbe", "fc:hobbe", "fc:beetle"] },
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

function blendTerrain(dim, x0, y0, z0, w, d) {
  // foundation skirt: fill below the structure rim so it meets the land
  const work = function* () {
    for (let x = x0 - 1; x <= x0 + w; x++) {
      for (const z of [z0 - 1, z0 + d]) {
        yield* skirtColumn(dim, x, y0, z);
      }
      yield;
    }
    for (let z = z0 - 1; z <= z0 + d; z++) {
      for (const x of [x0 - 1, x0 + w]) {
        yield* skirtColumn(dim, x, y0, z);
      }
      yield;
    }
  };
  try { system.runJob(work()); } catch { /* skip blending if jobs unavailable */ }
}

function* skirtColumn(dim, x, yTop, z) {
  for (let y = yTop - 1; y > yTop - 9; y--) {
    let b;
    try { b = dim.getBlock({ x, y, z }); } catch { return; }
    if (!b) return;
    if (!b.isAir && !b.isLiquid) return; // reached ground
    try {
      b.setType(Math.random() < 0.5 ? "minecraft:cobblestone" : "minecraft:dirt");
    } catch { return; }
    yield;
  }
}

function hash2(x, z) {
  let h = (x * 374761393 + z * 668265263) ^ 1407;
  h = (h ^ (h >> 13)) * 1274126177;
  h = h ^ (h >> 16);
  return ((h >>> 0) % 100000) / 100000;
}

system.runInterval(() => {
  for (const p of world.getPlayers()) {
    if (!world.getDynamicProperty("fc_guild_placed")) placeGuildNear(p);
    const rx = Math.floor(p.location.x / REGION), rz = Math.floor(p.location.z / REGION);
    for (let dx = -1; dx <= 1; dx++) {
      for (let dz = -1; dz <= 1; dz++) {
        maybePlace(p, rx + dx, rz + dz);
      }
    }
  }
}, 80);

function maybePlace(p, rx, rz) {
  const key = `fc_s_${rx}_${rz}`;
  if (world.getDynamicProperty(key)) return;
  const h = hash2(rx, rz);
  let pick = null;
  for (const s of STRUCTS) { if (h < s.chance) { pick = s; break; } }
  if (!pick) { world.setDynamicProperty(key, 1); return; }
  const jx = Math.floor(hash2(rx * 7 + 1, rz) * (REGION - 40)) + 20;
  const jz = Math.floor(hash2(rx, rz * 7 + 1) * (REGION - 40)) + 20;
  let x = rx * REGION + jx, z = rz * REGION + jz;
  const dx = x - p.location.x, dz = z - p.location.z;
  const dist = Math.hypot(dx, dz);
  if (dist > 96 || dist < 20) return; // wait until in sweet placement range
  const dim = p.dimension;
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
  const y = groundY(dim, x + Math.floor(pick.w / 2), z + Math.floor(pick.w / 2)) ?? groundY(dim, x, z);
  if (y === null) return;
  try {
    world.structureManager.place(pick.id, dim, { x, y: y - 1, z });
    world.setDynamicProperty(key, 1);
    if (pick.door) {
      const door = trySpawn(dim, "fc:demon_door", { x: x + 11.5, y: y, z: z + 4.6 });
      if (door) doorPersona(door);
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
  } catch { /* chunk edge; try next sweep */ }
}

// ---------------------------------------------------------------------------
// Boss minion summoning + ghost shriek + ally cleanup
// ---------------------------------------------------------------------------
system.runInterval(() => {
  for (const p of world.getPlayers()) {
    const dim = p.dimension;
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
      if (Math.random() < 0.3) {
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

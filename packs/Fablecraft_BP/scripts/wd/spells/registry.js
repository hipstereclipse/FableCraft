// Will & Destiny spell registry. The single 18-power table consumed by the
// shared cast pipeline (shared/cast.js). Metadata mirrors fc_data.py SPELLS;
// per-level gameplay numbers live in each spell body. Phase-3 powers are listed
// with cast:null so the menu/HUD can show them while the pipeline replies
// "not yet woven" until their bodies land.
import { fireballCast } from "./fireball.js";
import { enflameCast } from "./enflame.js";
import { lightningCast } from "./lightning.js";
import { forcePushCast } from "./force_push.js";
import { assassinRushCast } from "./assassin_rush.js";
import { battleChargeCast } from "./battle_charge.js";
import { drainLifeCast } from "./drain_life.js";
import { healLifeCast } from "./heal_life.js";
import { physicalShieldCast } from "./physical_shield.js";
import { slowTimeCast } from "./slow_time.js";
// Phase 3 spell bodies.
import { summonCast } from "./summon.js";
import { turncoatCast } from "./turncoat.js";
import { ghostSwordCast } from "./ghost_sword.js";
import { multiArrowCast } from "./multi_arrow.js";
import { multiStrikeCast } from "./multi_strike.js";
import { berserkCast } from "./berserk.js";
import { divineFuryCast } from "./divine_fury.js";
import { infernalWrathCast } from "./infernal_wrath.js";

// category: attack | physical | surround  (Fable taxonomy)
// alignLock: 0 none | 1 good-only | -1 evil-only
// alignCost: 0 flat | 1 cheaper-when-good | -1 cheaper-when-evil (capstones)
const SPELLS = [
  { id: "fireball", name: "Fireball", category: "attack", gesture: 1, alignLock: 0, alignCost: 0,
    charges: true, color: [255, 90, 20], baseMana: 12, cooldown: 30, cast: fireballCast },
  { id: "enflame", name: "Enflame", category: "surround", gesture: 2, alignLock: 0, alignCost: 0,
    charges: true, color: [255, 120, 30], baseMana: 15, cooldown: 50, cast: enflameCast },
  { id: "lightning", name: "Lightning", category: "attack", gesture: 3, alignLock: 0, alignCost: 0,
    charges: true, color: [120, 180, 255], baseMana: 14, cooldown: 35, cast: lightningCast },
  { id: "force_push", name: "Force Push", category: "surround", gesture: 4, alignLock: 0, alignCost: 0,
    charges: true, color: [170, 200, 255], baseMana: 10, cooldown: 45, cast: forcePushCast },
  { id: "drain_life", name: "Drain Life", category: "surround", gesture: 5, alignLock: -1, alignCost: 0,
    charges: true, color: [180, 30, 60], baseMana: 16, cooldown: 60, cast: drainLifeCast },
  { id: "heal_life", name: "Heal Life", category: "physical", gesture: 6, alignLock: 1, alignCost: 0,
    charges: false, color: [120, 255, 150], baseMana: 18, cooldown: 60, cast: healLifeCast },
  { id: "physical_shield", name: "Physical Shield", category: "physical", gesture: 7, alignLock: 1, alignCost: 0,
    charges: false, color: [110, 160, 255], baseMana: 12, cooldown: 100, cast: physicalShieldCast },
  { id: "slow_time", name: "Slow Time", category: "surround", gesture: 8, alignLock: 0, alignCost: 0,
    charges: false, color: [200, 220, 255], baseMana: 20, cooldown: 200, cast: slowTimeCast },
  { id: "assassin_rush", name: "Assassin Rush", category: "physical", gesture: 9, alignLock: 0, alignCost: 0,
    charges: false, color: [140, 120, 200], baseMana: 8, cooldown: 40, cast: assassinRushCast },
  { id: "battle_charge", name: "Battle Charge", category: "attack", gesture: 10, alignLock: 0, alignCost: 0,
    charges: true, color: [255, 170, 60], baseMana: 14, cooldown: 80, cast: battleChargeCast },

  // --- Phase 3 ---
  { id: "summon", name: "Summon", category: "surround", gesture: 11, alignLock: 1, alignCost: 0,
    charges: false, color: [120, 230, 200], baseMana: 25, cooldown: 200, cast: summonCast },
  { id: "turncoat", name: "Turncoat", category: "surround", gesture: 12, alignLock: -1, alignCost: 0,
    charges: false, color: [220, 150, 240], baseMana: 18, cooldown: 160, cast: turncoatCast },
  { id: "multi_arrow", name: "Multi Arrow", category: "physical", gesture: 13, alignLock: 0, alignCost: 0,
    charges: false, color: [200, 230, 150], baseMana: 10, cooldown: 60, cast: multiArrowCast },
  { id: "multi_strike", name: "Multi Strike", category: "attack", gesture: 14, alignLock: 0, alignCost: 0,
    charges: false, color: [255, 200, 90], baseMana: 12, cooldown: 120, cast: multiStrikeCast },
  { id: "berserk", name: "Berserk", category: "physical", gesture: 15, alignLock: -1, alignCost: 0,
    charges: false, color: [255, 60, 40], baseMana: 20, cooldown: 240, cast: berserkCast },
  { id: "divine_fury", name: "Divine Fury", category: "attack", gesture: 16, alignLock: 1, alignCost: 1,
    charges: true, color: [255, 240, 150], baseMana: 35, cooldown: 300, cast: divineFuryCast },
  { id: "infernal_wrath", name: "Infernal Wrath", category: "attack", gesture: 17, alignLock: -1, alignCost: -1,
    charges: true, color: [180, 40, 200], baseMana: 35, cooldown: 300, cast: infernalWrathCast },
  { id: "ghost_sword", name: "Ghost Sword", category: "physical", gesture: 18, alignLock: 0, alignCost: 0,
    charges: false, color: [180, 220, 255], baseMana: 16, cooldown: 90, cast: ghostSwordCast },
];

export const SPELL_REGISTRY = Object.freeze(
  Object.fromEntries(SPELLS.map((spell) => [spell.id, Object.freeze(spell)])),
);

export const SPELL_ORDER = Object.freeze(SPELLS.map((spell) => spell.id));

export const CATEGORY_LABEL = Object.freeze({
  attack: "Attack",
  physical: "Physical",
  surround: "Surround",
});

export function getSpell(id) {
  return SPELL_REGISTRY[id];
}

export function isImplemented(id) {
  return typeof SPELL_REGISTRY[id]?.cast === "function";
}

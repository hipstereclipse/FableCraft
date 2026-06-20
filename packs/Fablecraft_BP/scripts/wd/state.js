// Will & Destiny persistence. This module owns the versioned per-player blob.
import { WD_CONFIG } from "./config.js";

export const WD_STATE_KEY = "wd:state";
export const WD_SCHEMA_VERSION = 1;

const XP_TIER_THRESHOLDS = [0, 250, 750, 1800, 4000, 8000];

export function clamp(value, min, max) {
  return Math.max(min, Math.min(max, value));
}

function finiteNumber(value, fallback = 0) {
  return typeof value === "number" && Number.isFinite(value) ? value : fallback;
}

function legacyNumber(player, key, fallback = 0) {
  try {
    return finiteNumber(player.getDynamicProperty(key), fallback);
  } catch {
    return fallback;
  }
}

export function tierFromXp(xp) {
  const value = Math.max(0, finiteNumber(xp));
  let tier = 0;
  for (let i = 1; i < XP_TIER_THRESHOLDS.length; i++) {
    if (value >= XP_TIER_THRESHOLDS[i]) tier = i;
  }
  return tier;
}

function newState(player) {
  const magicPower = clamp(Math.floor(legacyNumber(player, "fc_up_magic_power", 0)), 0, 10);
  const manaMax = 100 + magicPower * 50;
  const fireballLevel = clamp(Math.floor(legacyNumber(player, "fc_spell_lvl_fireball", 1)), 1, 4);

  return {
    schemaVersion: WD_SCHEMA_VERSION,
    alignment: clamp(Math.floor(legacyNumber(player, "fc_morality", 0)), -1000, 1000),
    xp: {
      generic: Math.max(0, Math.floor(legacyNumber(player, "fc_xp_general", 0))),
      strength: Math.max(0, Math.floor(legacyNumber(player, "fc_xp_strength", 0))),
      skill: Math.max(0, Math.floor(legacyNumber(player, "fc_xp_skill", 0))),
      will: Math.max(0, Math.floor(legacyNumber(player, "fc_xp_will", 0))),
    },
    attributes: {
      magicPower,
    },
    mana: {
      current: clamp(legacyNumber(player, "fc_will", manaMax), 0, manaMax),
      max: manaMax,
    },
    spells: {
      equipped: "fireball",
      owned: {
        fireball: fireballLevel,
      },
    },
    options: {
      allowTerrainEffects: WD_CONFIG.allowTerrainEffects,
      auraDensity: WD_CONFIG.auraDensity,
    },
  };
}

function normalizeState(player, candidate) {
  const fallback = newState(player);
  const state = candidate && typeof candidate === "object" ? candidate : {};
  const xp = state.xp && typeof state.xp === "object" ? state.xp : {};
  const attributes = state.attributes && typeof state.attributes === "object" ? state.attributes : {};
  const mana = state.mana && typeof state.mana === "object" ? state.mana : {};
  const spells = state.spells && typeof state.spells === "object" ? state.spells : {};
  const owned = spells.owned && typeof spells.owned === "object" ? spells.owned : {};
  const options = state.options && typeof state.options === "object" ? state.options : {};

  const magicPower = clamp(Math.floor(finiteNumber(attributes.magicPower, fallback.attributes.magicPower)), 0, 10);
  const manaMax = 100 + magicPower * 50;
  const fireballLevel = clamp(Math.floor(finiteNumber(owned.fireball, fallback.spells.owned.fireball)), 1, 4);

  return {
    schemaVersion: WD_SCHEMA_VERSION,
    alignment: clamp(Math.floor(finiteNumber(state.alignment, fallback.alignment)), -1000, 1000),
    xp: {
      generic: Math.max(0, Math.floor(finiteNumber(xp.generic, fallback.xp.generic))),
      strength: Math.max(0, Math.floor(finiteNumber(xp.strength, fallback.xp.strength))),
      skill: Math.max(0, Math.floor(finiteNumber(xp.skill, fallback.xp.skill))),
      will: Math.max(0, Math.floor(finiteNumber(xp.will, fallback.xp.will))),
    },
    attributes: {
      magicPower,
    },
    mana: {
      current: clamp(finiteNumber(mana.current, fallback.mana.current), 0, manaMax),
      max: manaMax,
    },
    spells: {
      equipped: owned[spells.equipped] ? spells.equipped : "fireball",
      owned: {
        ...owned,
        fireball: fireballLevel,
      },
    },
    options: {
      allowTerrainEffects: options.allowTerrainEffects === true,
      auraDensity: clamp(finiteNumber(options.auraDensity, WD_CONFIG.auraDensity), 0, 2),
    },
  };
}

export function saveState(player, state) {
  const normalized = normalizeState(player, state);
  player.setDynamicProperty(WD_STATE_KEY, JSON.stringify(normalized));
  return normalized;
}

export function getState(player) {
  let parsed;
  try {
    const raw = player.getDynamicProperty(WD_STATE_KEY);
    if (typeof raw === "string" && raw.length > 0) parsed = JSON.parse(raw);
  } catch {
    parsed = undefined;
  }
  const normalized = normalizeState(player, parsed);
  if (!parsed || parsed.schemaVersion !== WD_SCHEMA_VERSION) saveState(player, normalized);
  return normalized;
}

export function mutateState(player, mutator) {
  const state = getState(player);
  mutator(state);
  return saveState(player, state);
}

export function bridgeLegacyProgression(player) {
  if (!WD_CONFIG.useLegacyFcProgressionBridge) return getState(player);
  return mutateState(player, (state) => {
    state.alignment = clamp(Math.floor(legacyNumber(player, "fc_morality", state.alignment)), -1000, 1000);
    state.xp.generic = Math.max(0, Math.floor(legacyNumber(player, "fc_xp_general", state.xp.generic)));
    state.xp.strength = Math.max(0, Math.floor(legacyNumber(player, "fc_xp_strength", state.xp.strength)));
    state.xp.skill = Math.max(0, Math.floor(legacyNumber(player, "fc_xp_skill", state.xp.skill)));
    state.xp.will = Math.max(0, Math.floor(legacyNumber(player, "fc_xp_will", state.xp.will)));
    state.attributes.magicPower = clamp(
      Math.floor(legacyNumber(player, "fc_up_magic_power", state.attributes.magicPower)),
      0,
      10,
    );
    state.spells.owned.fireball = clamp(
      Math.floor(legacyNumber(player, "fc_spell_lvl_fireball", state.spells.owned.fireball)),
      1,
      4,
    );
  });
}

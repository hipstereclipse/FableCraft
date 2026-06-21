// Will & Destiny persistence. This module owns the versioned per-player blob.
import { WD_CONFIG } from "./config.js";

export const WD_STATE_KEY = "wd:state";
export const WD_SCHEMA_VERSION = 3;

const XP_TIER_THRESHOLDS = [0, 250, 750, 1800, 4000, 8000];
const ALIGNMENT_TIER_THRESHOLDS = [150, 300, 500, 700, 850, 950];

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

// Signed alignment tier (-6..6) used by the appearance rig fingerprint.
export function alignmentTierFromValue(alignment) {
  const value = clamp(Math.floor(finiteNumber(alignment)), -1000, 1000);
  const sign = Math.sign(value);
  const magnitude = Math.abs(value);
  let tier = 0;
  for (let i = 0; i < ALIGNMENT_TIER_THRESHOLDS.length; i++) {
    if (magnitude >= ALIGNMENT_TIER_THRESHOLDS[i]) tier = i + 1;
  }
  return tier * sign;
}

function quickSlotCount() {
  const configured = Math.floor(finiteNumber(WD_CONFIG.quickSlotCount, 3));
  return clamp(configured, 1, 6);
}

function summonCap() {
  return clamp(Math.floor(finiteNumber(WD_CONFIG.maxSummonsPerPlayer, 2)), 0, 8);
}

function appearanceTiers(alignment, xp) {
  return {
    alignment: alignmentTierFromValue(alignment),
    strength: tierFromXp(xp.strength),
    skill: tierFromXp(xp.skill),
    will: tierFromXp(xp.will),
  };
}

export function appearanceFingerprint(tiers) {
  return `${tiers.alignment}:${tiers.strength}:${tiers.skill}:${tiers.will}`;
}

function defaultOptions() {
  return {
    allowTerrainEffects: WD_CONFIG.allowTerrainEffects === true,
    auraDensity: WD_CONFIG.auraDensity,
    morphEnabled: WD_CONFIG.enableMorphs !== false,
    appearanceDetail: WD_CONFIG.appearanceDetailDefault ?? "full",
    chargeEnabled: WD_CONFIG.chargeEnabledDefault !== false,
  };
}

function newState(player) {
  const magicPower = clamp(Math.floor(legacyNumber(player, "fc_up_magic_power", 0)), 0, 10);
  const manaMax = 100 + magicPower * 50;
  const fireballLevel = clamp(Math.floor(legacyNumber(player, "fc_spell_lvl_fireball", 1)), 1, 4);
  const alignment = clamp(Math.floor(legacyNumber(player, "fc_morality", 0)), -1000, 1000);
  const xp = {
    generic: Math.max(0, Math.floor(legacyNumber(player, "fc_xp_general", 0))),
    strength: Math.max(0, Math.floor(legacyNumber(player, "fc_xp_strength", 0))),
    skill: Math.max(0, Math.floor(legacyNumber(player, "fc_xp_skill", 0))),
    will: Math.max(0, Math.floor(legacyNumber(player, "fc_xp_will", 0))),
  };
  const slots = new Array(quickSlotCount()).fill(null);
  slots[0] = "fireball";
  const tiers = appearanceTiers(alignment, xp);

  return {
    schemaVersion: WD_SCHEMA_VERSION,
    alignment,
    xp,
    attributes: { magicPower },
    mana: {
      current: clamp(legacyNumber(player, "fc_will", manaMax), 0, manaMax),
      max: manaMax,
    },
    spells: {
      owned: { fireball: fireballLevel },
      slots,
      active: 0,
    },
    cooldowns: {},
    // Phase 3 (schema v3): summon/allegiance ledgers, the per-spell Will-XP
    // upgrade ledger, and the Logbook chronicle counters. All additive over v2.
    summons: { active: [], max: summonCap() },
    allegiance: { charmed: [] },
    spellXp: {},
    logbook: { kills: {}, deeds: {}, discovered: [] },
    appearance: { tiers, fingerprint: appearanceFingerprint(tiers) },
    ui: { lastPage: "hero" },
    options: defaultOptions(),
  };
}

function normalizeOwned(rawOwned, fallbackFireball) {
  const owned = rawOwned && typeof rawOwned === "object" ? rawOwned : {};
  const result = {};
  for (const [id, level] of Object.entries(owned)) {
    if (typeof id !== "string" || !id) continue;
    const lvl = clamp(Math.floor(finiteNumber(level, 0)), 0, 4);
    if (lvl >= 1) result[id] = lvl;
  }
  // Fireball is the starter focus power; keep it owned so the focus always works.
  result.fireball = clamp(Math.floor(finiteNumber(owned.fireball, fallbackFireball)), 1, 4);
  return result;
}

function normalizeSlots(spells, owned) {
  const count = quickSlotCount();
  const slots = new Array(count).fill(null);
  const source = Array.isArray(spells.slots) ? spells.slots : [];
  for (let i = 0; i < count; i++) {
    const id = source[i];
    slots[i] = typeof id === "string" && owned[id] ? id : null;
  }
  // Migration from v1: wrap the single equipped spell into the first slot.
  if (source.length === 0 && typeof spells.equipped === "string" && owned[spells.equipped]) {
    slots[0] = spells.equipped;
  }
  if (!slots.some(Boolean) && owned.fireball) slots[0] = "fireball";
  return slots;
}

function normalizeCooldowns(raw) {
  const cooldowns = {};
  if (raw && typeof raw === "object") {
    for (const [id, tick] of Object.entries(raw)) {
      if (typeof id === "string" && typeof tick === "number" && Number.isFinite(tick)) {
        cooldowns[id] = Math.floor(tick);
      }
    }
  }
  return cooldowns;
}

// String-id ledger (summons.active / allegiance.charmed). Entity ids never
// survive a world reload; the summon/allegiance frameworks reconcile against
// live entities on join and drop the stale ids there.
function normalizeIdList(raw) {
  if (!Array.isArray(raw)) return [];
  const out = [];
  for (const id of raw) {
    if (typeof id === "string" && id && !out.includes(id)) out.push(id);
  }
  return out;
}

function normalizeIntMap(raw, min = 0, max = Number.MAX_SAFE_INTEGER) {
  const out = {};
  if (raw && typeof raw === "object") {
    for (const [key, value] of Object.entries(raw)) {
      if (typeof key !== "string" || !key) continue;
      const n = Math.floor(finiteNumber(value, 0));
      if (Number.isFinite(n) && n > 0) out[key] = clamp(n, min, max);
    }
  }
  return out;
}

function normalizeLogbook(raw) {
  const lb = raw && typeof raw === "object" ? raw : {};
  return {
    kills: normalizeIntMap(lb.kills),
    deeds: normalizeIntMap(lb.deeds),
    discovered: normalizeIdList(lb.discovered),
  };
}

function normalizeState(player, candidate) {
  const fallback = newState(player);
  const state = candidate && typeof candidate === "object" ? candidate : {};
  const xp = state.xp && typeof state.xp === "object" ? state.xp : {};
  const attributes = state.attributes && typeof state.attributes === "object" ? state.attributes : {};
  const mana = state.mana && typeof state.mana === "object" ? state.mana : {};
  const spells = state.spells && typeof state.spells === "object" ? state.spells : {};
  const options = state.options && typeof state.options === "object" ? state.options : {};
  const appearance = state.appearance && typeof state.appearance === "object" ? state.appearance : {};
  const ui = state.ui && typeof state.ui === "object" ? state.ui : {};
  const summons = state.summons && typeof state.summons === "object" ? state.summons : {};
  const allegiance = state.allegiance && typeof state.allegiance === "object" ? state.allegiance : {};

  const magicPower = clamp(Math.floor(finiteNumber(attributes.magicPower, fallback.attributes.magicPower)), 0, 10);
  const manaMax = 100 + magicPower * 50;
  const alignment = clamp(Math.floor(finiteNumber(state.alignment, fallback.alignment)), -1000, 1000);
  const normXp = {
    generic: Math.max(0, Math.floor(finiteNumber(xp.generic, fallback.xp.generic))),
    strength: Math.max(0, Math.floor(finiteNumber(xp.strength, fallback.xp.strength))),
    skill: Math.max(0, Math.floor(finiteNumber(xp.skill, fallback.xp.skill))),
    will: Math.max(0, Math.floor(finiteNumber(xp.will, fallback.xp.will))),
  };

  const owned = normalizeOwned(spells.owned, fallback.spells.owned.fireball);
  const slots = normalizeSlots(spells, owned);
  const active = clamp(Math.floor(finiteNumber(spells.active, 0)), 0, slots.length - 1);

  const tiers = appearanceTiers(alignment, normXp);
  const storedDefaults = defaultOptions();

  return {
    schemaVersion: WD_SCHEMA_VERSION,
    alignment,
    xp: normXp,
    attributes: { magicPower },
    mana: {
      current: clamp(finiteNumber(mana.current, fallback.mana.current), 0, manaMax),
      max: manaMax,
    },
    spells: { owned, slots, active },
    cooldowns: normalizeCooldowns(state.cooldowns),
    // v3 ledgers — additive over v2; absent on a v1/v2 doc and defaulted here so
    // migration is forward-only (no v2 field changes meaning).
    summons: {
      active: normalizeIdList(summons.active),
      max: clamp(Math.floor(finiteNumber(summons.max, summonCap())), 0, 8),
    },
    allegiance: { charmed: normalizeIdList(allegiance.charmed) },
    spellXp: normalizeIntMap(state.spellXp),
    logbook: normalizeLogbook(state.logbook),
    appearance: {
      tiers,
      fingerprint: typeof appearance.fingerprint === "string"
        ? appearance.fingerprint
        : appearanceFingerprint(tiers),
    },
    ui: {
      lastPage: typeof ui.lastPage === "string" ? ui.lastPage : storedDefaults.lastPage ?? "hero",
    },
    options: {
      allowTerrainEffects: options.allowTerrainEffects === true,
      auraDensity: clamp(finiteNumber(options.auraDensity, storedDefaults.auraDensity), 0, 2),
      morphEnabled: options.morphEnabled !== false,
      appearanceDetail: ["full", "overlays_only", "horns_halo_only"].includes(options.appearanceDetail)
        ? options.appearanceDetail
        : storedDefaults.appearanceDetail,
      chargeEnabled: options.chargeEnabled !== false,
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
  // Forward-only migration: persist whenever the stored doc is absent or older.
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

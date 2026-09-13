// Will & Destiny morality. This module owns alignment changes and tier mapping.
// Post-cutover, wd:state is authoritative for alignment; every change derives
// back to the legacy fc_morality property for the monolith's readers.
import { clamp, getState, mutateState, WD_STATE_KEY, WD_SCHEMA_VERSION } from "./state.js";

export const ALIGNMENT_DEEDS = Object.freeze({
  hostileKill: 3,
  bossKill: 20,
  villagerKill: -100,
  ironGolemKill: -75,
  tamedPetKill: -60,
  pureFood: 15,
  vileFood: -25,
  altarOfLightDonation: 125,
  altarOfShadowSacrifice: -175,
});

const TIER_THRESHOLDS = [150, 300, 500, 700, 850, 950];

export function alignmentTier(alignment) {
  const value = clamp(Math.floor(alignment), -1000, 1000);
  const sign = Math.sign(value);
  const magnitude = Math.abs(value);
  let tier = 0;
  for (let i = 0; i < TIER_THRESHOLDS.length; i++) {
    if (magnitude >= TIER_THRESHOLDS[i]) tier = i + 1;
  }
  return tier * sign;
}

export function getAlignment(player) {
  return getState(player).alignment;
}

// Challenge authority must not initialize, migrate, clamp or borrow legacy
// morality when current saved alignment is unavailable. null means defer.
export function readAlignmentAuthority(player) {
  try {
    if (player?.isValid !== true || player.typeId !== "minecraft:player"
      || typeof player.id !== "string" || !player.id) return null;
    const raw = player.getDynamicProperty(WD_STATE_KEY);
    if (typeof raw !== "string" || !raw) return null;
    const state = JSON.parse(raw);
    if (!state || typeof state !== "object" || Array.isArray(state)
      || state.schemaVersion !== WD_SCHEMA_VERSION || !Number.isInteger(state.alignment)
      || state.alignment < -1000 || state.alignment > 1000) return null;
    return state.alignment;
  } catch { return null; }
}

export function setAlignment(player, value, showFeedback = true) {
  const before = getState(player).alignment;
  const after = clamp(Math.floor(value), -1000, 1000);
  mutateState(player, (state) => {
    state.alignment = after;
  });
  // Derive the legacy property unconditionally (wd:state is authoritative; this
  // keeps the monolith's many fc_morality readers correct without the bridge).
  try {
    player.setDynamicProperty("fc_morality", after);
  } catch {
    // The wd:state value remains authoritative if the legacy property fails.
  }
  if (showFeedback && before !== after) {
    const delta = after - before;
    const color = delta > 0 ? "§e" : "§4";
    player.onScreenDisplay.setActionBar(`${color}${delta > 0 ? "+" : ""}${delta} alignment §7(${after}/1000)`);
  }
  return after;
}

export function changeAlignment(player, amount, showFeedback = true) {
  return setAlignment(player, getAlignment(player) + amount, showFeedback);
}

// Will & Destiny morality. This module owns alignment changes and tier mapping.
import { WD_CONFIG } from "./config.js";
import { bridgeLegacyProgression, clamp, getState, mutateState } from "./state.js";

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
  const state = WD_CONFIG.useLegacyFcProgressionBridge
    ? bridgeLegacyProgression(player)
    : getState(player);
  return state.alignment;
}

export function setAlignment(player, value, showFeedback = true) {
  const before = getState(player).alignment;
  const after = clamp(Math.floor(value), -1000, 1000);
  mutateState(player, (state) => {
    state.alignment = after;
  });
  if (WD_CONFIG.useLegacyFcProgressionBridge) {
    try {
      player.setDynamicProperty("fc_morality", after);
    } catch {
      // The wd:state value remains authoritative if the legacy property fails.
    }
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

// Will & Destiny client sync. This module owns wd:* entity property updates.
import { system } from "@minecraft/server";
import { alignmentTier } from "./alignment.js";
import { bridgeLegacyProgression, getState } from "./state.js";
import { getDisciplineTiers } from "./stats.js";

// Gesture ids live on the spell records (registry.js). 0 = idle. setCasting
// takes the numeric gesture so this module stays decoupled from the registry.
export const CASTING_NONE = 0;

function setProperty(player, id, value) {
  try {
    if (player.getProperty(id) !== value) player.setProperty(id, value);
  } catch {
    // A missing player override should not stop gameplay systems.
  }
}

export function syncPlayerProperties(player) {
  const state = bridgeLegacyProgression(player);
  const tiers = getDisciplineTiers(state);
  setProperty(player, "wd:alignment_tier", alignmentTier(state.alignment));
  setProperty(player, "wd:strength_tier", tiers.strength);
  setProperty(player, "wd:skill_tier", tiers.skill);
  setProperty(player, "wd:will_tier", tiers.will);
  setProperty(player, "wd:mana_ratio", state.mana.max > 0 ? state.mana.current / state.mana.max : 0);
}

export function setCasting(player, gesture, level, durationTicks) {
  const gestureId = Math.max(0, Math.min(18, Math.floor(gesture) || 0));
  setProperty(player, "wd:casting", gestureId);
  setProperty(player, "wd:casting_level", Math.max(0, Math.min(4, level)));
  system.runTimeout(() => {
    if (!player.isValid) return;
    setProperty(player, "wd:casting", CASTING_NONE);
    setProperty(player, "wd:casting_level", 0);
  }, durationTicks);
}

// Show a live charge gather while the focus is held (ramps with hold time).
export function setCharging(player, gesture, stage) {
  setProperty(player, "wd:casting", Math.max(0, Math.min(18, Math.floor(gesture) || 0)));
  setProperty(player, "wd:casting_level", Math.max(0, Math.min(4, stage)));
}

export function clearCasting(player) {
  setProperty(player, "wd:casting", CASTING_NONE);
  setProperty(player, "wd:casting_level", 0);
}

export function initializePlayerProperties(player) {
  syncPlayerProperties(player);
  setProperty(player, "wd:casting", CASTING_NONE);
  setProperty(player, "wd:casting_level", 0);
  setProperty(player, "wd:shield_active", false);
}

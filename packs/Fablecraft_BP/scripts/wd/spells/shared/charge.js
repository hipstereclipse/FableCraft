// Will & Destiny charge model. Hold time -> requested charge level. The cast
// pipeline clamps this to the owned level and to affordable mana.
import { WD_CONFIG } from "../../config.js";

const INSTANT_LEVEL = 99; // sentinel: "cast at the owned level" (pipeline clamps)

// Convert a held duration (ticks) into a requested charge level. When charging
// is disabled, or the spell does not charge, request the owned level instantly.
export function chargeLevelFromHold(heldTicks, { chargeEnabled = true, charges = true } = {}) {
  if (!chargeEnabled || !charges) return INSTANT_LEVEL;
  const perLevel = Math.max(1, Math.floor(WD_CONFIG.chargeTicksPerLevel ?? 8));
  const held = Math.max(0, Math.min(WD_CONFIG.chargeMaxHoldTicks ?? 40, Math.floor(heldTicks)));
  return Math.max(1, 1 + Math.floor(held / perLevel));
}

// The 0..4 charge stage used for VFX/animation intensity while still holding.
export function chargeStage(heldTicks, ownedLevel) {
  const perLevel = Math.max(1, Math.floor(WD_CONFIG.chargeTicksPerLevel ?? 8));
  const stage = 1 + Math.floor(Math.max(0, heldTicks) / perLevel);
  return Math.max(1, Math.min(Math.max(1, ownedLevel), stage));
}

export { INSTANT_LEVEL };

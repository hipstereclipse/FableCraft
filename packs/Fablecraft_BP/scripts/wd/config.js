// Will & Destiny configuration. This module owns server-safe feature toggles.
export const WD_CONFIG = Object.freeze({
  allowTerrainEffects: false,
  auraDensity: 1.0,
  auraIntervalTicks: 12,
  maxAuraEmittersPerPlayer: 3,
  alignmentAppearanceTier: 5,
  appearanceIntervalTicks: 1,
  manaRegenIntervalTicks: 10,
  manaRegenPerSecond: 4,
  grantFocusOnFirstJoin: true,
  enableDebugScriptEvents: true,
  combatMultiplierEnabled: false,
  agingEnabled: false,

  // Fablecraft already has live fc_* progression. Keep it authoritative while
  // Phase 1 migrates existing worlds into the versioned wd:state document.
  useLegacyFcProgressionBridge: true,
});

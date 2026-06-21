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
  // Phase 1/2 migrate existing worlds into the versioned wd:state document.
  // The legacy bridge stays ON for all of Phase 2; the cutover is Phase 3.
  useLegacyFcProgressionBridge: true,

  // --- Phase 2: controls & charging ---
  chargeEnabledDefault: true,   // hold-to-charge default; players may disable
  chargeTicksPerLevel: 8,       // hold ticks per charge level
  chargeMaxHoldTicks: 40,       // safety cap on a single charge hold
  quickSlotCount: 3,            // hot-swap quick-cast slots
  cycleOnSneakUse: true,        // crouch+use cycles the active slot

  // --- Phase 2: appearance rig ---
  enableMorphs: true,           // master switch for the overlay rig
  appearanceDetailDefault: "full", // full | overlays_only | horns_halo_only
  overlayFollowMode: "teleport",   // attach | teleport (smoothness/perf)
  overlaySyncIntervalTicks: 1,     // overlay follow cadence
  morphRebuildMinTicks: 20,        // min ticks between rig rebuilds per player

  // --- Phase 2: spells ---
  shieldDrainsWillDirectly: true,  // shield consumes Will (faithful) vs fixed pool
  slowTimeAffectsPlayers: false,   // hard off in multiplayer; solo-test only
  perSpellEnabled: Object.freeze({}), // id -> bool to disable individual powers

  // --- Phase 2: menu ---
  heroMenuTheme: "storybook",   // storybook reskin or plain forms
  guildSealFlourish: true,      // blue-ring + chime on open/recall

  // --- Phase 2: leveling ---
  spellUpgradeCostPerLevel: 150, // Will XP to deepen a spell one level

  // --- Phase 3: summons & allegiance (spec §3.8) ---
  maxSummonsPerPlayer: 2,       // living summons per player; cast-at-cap replaces oldest
  summonLifetimeTicks: 2400,    // informational; the summoned entity self-despawns on its own timer
  summonReplaceOnKill: true,    // a summon that kills a foe is refreshed by the fallen soul
  turncoatDurationTicks: 1200,  // base charm duration (scales with level)
  turncoatConvertTicks: 60,     // time-to-convert while the caster maintains the link
  charmableExcludesBosses: true, // bosses / quest-critical entities never charmable
  reactiveAppearance: true,     // master switch for cast-driven appearance (Phase 3 overlay rig)
  maxVfxMarkersPerCast: 8,      // cap on portals / beams / sigils spawned by a single cast
  entityBudgetPerServer: 200,   // soft cap for overlays + summons + charmed + markers
  deedParityCheck: true,        // log any drift between wd:state.alignment and fc_morality (diagnostic)
});

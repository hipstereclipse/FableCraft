// Will & Destiny progression-parity diagnostic (Phase 3, spec §3.6 step 1).
// Logs any divergence between wd:state.alignment (the WD source of truth) and the
// legacy fc_morality property. The purpose is to make the legacy-bridge cutover
// diagnosable:
//   * While useLegacyFcProgressionBridge is ON, this proves the FORWARD bridge
//     (fc_* -> wd:state) keeps the two in lock-step.
//   * After the cutover, it proves the REVERSE derive (wd:state -> fc_*) does.
// A persistent drift warning is the first thing to look for if morality starts
// double-counting or dropping after the flip.
import { system, world } from "@minecraft/server";
import { WD_CONFIG } from "./config.js";
import { getState } from "./state.js";

function legacyMorality(player) {
  try {
    const value = player.getDynamicProperty("fc_morality");
    return typeof value === "number" ? value : null;
  } catch {
    return null;
  }
}

const lastWarn = new Map(); // playerId -> last reported "wd:legacy" stamp (de-spams logs)

system.runInterval(() => {
  if (WD_CONFIG.deedParityCheck === false) return;
  for (const player of world.getAllPlayers()) {
    const wd = getState(player).alignment;
    const legacy = legacyMorality(player);
    if (legacy === null) continue;
    if (Math.abs(wd - legacy) > 1) {
      const stamp = `${wd}:${legacy}`;
      if (lastWarn.get(player.id) === stamp) continue;
      lastWarn.set(player.id, stamp);
      console.warn(
        `[WD parity] alignment drift for ${player.name}: wd:state=${wd} fc_morality=${legacy} ` +
        `(bridge=${WD_CONFIG.useLegacyFcProgressionBridge})`,
      );
    } else {
      lastWarn.delete(player.id);
    }
  }
}, 100);

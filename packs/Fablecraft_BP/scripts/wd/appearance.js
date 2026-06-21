// Will & Destiny appearance orchestration. Drives the single wd:overlay rig per
// player from stored options/tiers: horns/halo (opaque bones), charred/pale skin
// + eyes + body-hair + Will-Lines (inflated transparent shells), and physique/
// height morph (Molang bone-scale in the geometry). The base uploaded skin is
// always visible; this only adds overlays. Reactive cast-driven flares are
// Phase 3. The two Phase-1 cosmetic entities are folded into this one rig.
import { system } from "@minecraft/server";
import { getState } from "./state.js";
import { clearStaleOverlays, syncOverlays } from "./overlays.js";

let tickCounter = 0;
const planCache = new Map(); // playerId -> { enabled, detail }

function resolvePlan(player) {
  // Re-read the (cheap-to-change) options on a slow cadence; the per-tick follow
  // and property mirror in overlays.js use only fast getProperty reads.
  if (tickCounter % 20 === 0 || !planCache.has(player.id)) {
    let plan = { enabled: true, detail: "full" };
    try {
      const options = getState(player).options;
      plan = options.morphEnabled === false
        ? { enabled: false }
        : { enabled: true, detail: options.appearanceDetail ?? "full" };
    } catch {
      // Default to the full rig if state is briefly unavailable.
    }
    planCache.set(player.id, plan);
  }
  return planCache.get(player.id);
}

export function syncAlignmentAppearance() {
  tickCounter += 1;
  syncOverlays(resolvePlan);
}

export function clearStaleAlignmentCosmetics() {
  planCache.clear();
  clearStaleOverlays();
}

system.runTimeout(clearStaleAlignmentCosmetics, 1);

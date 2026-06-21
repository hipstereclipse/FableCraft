// Physical Shield — Physical (good). A protective sphere absorbing damage at the
// expense of Will until Will runs out; recasting removes it. Cast = a faceted
// energy sphere forms; sustain = hex-panel shimmer whose opacity tracks Will. The
// hit-flare is Phase 3 reactive polish.
import { system } from "@minecraft/server";
import { applyEffect, setShieldActive, isShieldActive } from "./shared/selfbuff.js";
import { mutateState, getState } from "../state.js";
import { tint, ring, dimensionSound } from "./shared/vfx.js";
import { WD_CONFIG } from "../config.js";

const DURATION = [0, 100, 160, 220, 300];
const DRAIN_PER_PASS = [0, 2, 2, 3, 3]; // Will per 20-tick pass while active

const activeShields = new Map(); // playerId -> { handle, endTick }

function shimmer(player, color, ratio) {
  const center = { x: player.location.x, y: player.location.y + 1, z: player.location.z };
  ring(player.dimension, center, 0.9, 12, (loc, angle) => {
    tint(player.dimension, "wd:shield_hex", { x: loc.x, y: center.y + Math.sin(angle * 2) * 0.5, z: loc.z }, color, 0.6, 1, 0.25 + ratio * 0.5);
  });
}

function clearShield(player, refund = false, message = "§9The shield fades.") {
  const entry = activeShields.get(player.id);
  if (entry) {
    try {
      system.clearRun(entry.handle);
    } catch {
      // The pass may already have ended.
    }
    activeShields.delete(player.id);
  }
  setShieldActive(player, false);
  if (refund) {
    mutateState(player, (d) => {
      d.mana.current = Math.min(d.mana.max, d.mana.current + entry?.refund ?? 0);
    });
  }
  try {
    player.onScreenDisplay.setActionBar(message);
  } catch {
    // Feedback only.
  }
}

export function physicalShieldCast(ctx) {
  const { player, level, spell } = ctx;

  // Recast dismisses an active shield (and refunds this cast's intent).
  if (isShieldActive(player) || activeShields.has(player.id)) {
    if (activeShields.has(player.id)) activeShields.get(player.id).refund = spell.baseMana;
    clearShield(player, true, "§9You release the shield.");
    return true;
  }

  setShieldActive(player, true);
  dimensionSound(player.dimension, "beacon.activate", player.location, { volume: 0.6, pitch: 1.2 });
  applyEffect(player, "resistance", 40, 3);
  applyEffect(player, "absorption", 40, level);

  const endTick = system.currentTick + DURATION[level];
  const handle = system.runInterval(() => {
    if (!player.isValid) {
      clearShield(player);
      return;
    }
    if (system.currentTick >= endTick) {
      clearShield(player, false, "§9The shield's Will is spent.");
      return;
    }
    // Keep the protective effects topped up between passes.
    applyEffect(player, "resistance", 40, 3);
    applyEffect(player, "absorption", 40, level);
    const state = getState(player);
    const ratio = state.mana.max > 0 ? state.mana.current / state.mana.max : 0;
    shimmer(player, spell.color, ratio);
    if (WD_CONFIG.shieldDrainsWillDirectly) {
      let depleted = false;
      mutateState(player, (d) => {
        d.mana.current = Math.max(0, d.mana.current - DRAIN_PER_PASS[level]);
        depleted = d.mana.current <= 0;
      });
      if (depleted) clearShield(player, false, "§9The shield's Will is spent.");
    }
  }, 20);

  activeShields.set(player.id, { handle, endTick, refund: 0 });
  return true;
}

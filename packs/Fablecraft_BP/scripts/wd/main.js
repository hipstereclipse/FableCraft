// Will & Destiny Phase 1 entrypoint. This module wires events and tick loops.
import { ItemStack, system, world } from "@minecraft/server";
import { WD_CONFIG } from "./config.js";
import { syncAlignmentAppearance } from "./appearance.js";
import { emitAlignmentAuras } from "./auras.js";
import { regenerateMana } from "./mana.js";
import { getState, mutateState } from "./state.js";
import { registerStatEvents } from "./stats.js";
import { initializePlayerProperties, syncPlayerProperties } from "./visuals.js";
import { setAlignment } from "./alignment.js";

const FOCUS_ID = "wd:will_focus";

function inventory(player) {
  return player.getComponent("minecraft:inventory")?.container;
}

function hasFocus(player) {
  const container = inventory(player);
  if (!container) return false;
  for (let slot = 0; slot < container.size; slot++) {
    if (container.getItem(slot)?.typeId === FOCUS_ID) return true;
  }
  return false;
}

function ensureFocus(player) {
  if (!WD_CONFIG.grantFocusOnFirstJoin) return;
  if (hasFocus(player)) {
    player.setDynamicProperty("wd:focus_granted", true);
    return;
  }
  if (player.getDynamicProperty("wd:focus_granted")) return;
  try {
    const leftover = inventory(player)?.addItem(new ItemStack(FOCUS_ID, 1));
    if (leftover) player.dimension.spawnItem(leftover, player.location);
    player.setDynamicProperty("wd:focus_granted", true);
    player.sendMessage("§9✦ A Will Focus answers your touch. Use it to cast; sneak-use to attune.");
  } catch {
    // A full inventory leaves the craftable focus available through its recipe.
  }
}

function initializePlayer(player) {
  getState(player);
  initializePlayerProperties(player);
  ensureFocus(player);
}

world.afterEvents.playerSpawn.subscribe((event) => {
  system.runTimeout(() => initializePlayer(event.player), event.initialSpawn ? 10 : 1);
});

registerStatEvents();

system.runInterval(() => {
  for (const player of world.getPlayers()) {
    regenerateMana(player);
  }
}, WD_CONFIG.manaRegenIntervalTicks);

system.runInterval(() => {
  for (const player of world.getPlayers()) {
    syncPlayerProperties(player);
  }
}, 20);

system.runInterval(emitAlignmentAuras, WD_CONFIG.auraIntervalTicks);
system.runInterval(syncAlignmentAppearance, WD_CONFIG.appearanceIntervalTicks);

if (WD_CONFIG.enableDebugScriptEvents) {
  system.afterEvents.scriptEventReceive.subscribe((event) => {
    const player = event.sourceEntity;
    if (!player || player.typeId !== "minecraft:player" || !event.id.startsWith("wd:")) return;
    const argument = event.message.trim();
    if (event.id === "wd:set_alignment") {
      const value = Number(argument);
      if (Number.isFinite(value)) setAlignment(player, value);
      return;
    }
    if (event.id === "wd:grant_fireball") {
      const level = Math.max(1, Math.min(4, Number(argument) || 1));
      mutateState(player, (state) => {
        state.spells.owned.fireball = level;
        state.spells.equipped = "fireball";
      });
      player.sendMessage(`§bFireball granted at level ${level}.`);
      return;
    }
    if (event.id === "wd:refill_mana") {
      mutateState(player, (state) => {
        state.mana.current = state.mana.max;
      });
      player.sendMessage("§bMana restored.");
      return;
    }
    if (event.id === "wd:dump") {
      player.sendMessage(`§8${JSON.stringify(getState(player))}`);
    }
  });
}

console.warn("[Will & Destiny] Phase 1 systems online.");

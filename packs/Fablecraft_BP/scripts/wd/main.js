// Will & Destiny entrypoint. This module wires events and tick loops.
import { ItemStack, system, world } from "@minecraft/server";
import { WD_CONFIG } from "./config.js";
import { syncAlignmentAppearance } from "./appearance.js";
import { emitAlignmentAuras } from "./auras.js";
import { regenerateMana } from "./mana.js";
import { getState, mutateState } from "./state.js";
import { registerStatEvents } from "./stats.js";
import { initializePlayerProperties, syncPlayerProperties } from "./visuals.js";
import { setAlignment } from "./alignment.js";
// Phase 2: control redesign and tome learning. The overlay appearance rig is
// imported from appearance.js below.
import "./quickcast.js";
import "./learn.js";
// Phase 3 frameworks. Both self-wire their global listeners (entityDie / leave)
// on import; reconcileSummons clears a player's stale summon ledger on join.
import { reconcileSummons } from "./summons.js";
import "./allegiance.js";
import "./combat_hooks.js";
import { getSpell, SPELL_ORDER } from "./spells/registry.js";
import { castSpellById } from "./spells/shared/cast.js";

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
  reconcileSummons(player); // last session's summons are gone; start the ledger clean
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
        if (!state.spells.slots.some(Boolean)) state.spells.slots[0] = "fireball";
      });
      player.sendMessage(`§bFireball granted at level ${level}.`);
      return;
    }
    // wd:grant_spell <id> [level] — learn any power for testing.
    if (event.id === "wd:grant_spell") {
      const [id, lvlText] = argument.split(/\s+/);
      if (!getSpell(id)) return player.sendMessage(`§cUnknown spell '${id}'.`);
      const level = Math.max(1, Math.min(4, Number(lvlText) || 1));
      mutateState(player, (state) => {
        state.spells.owned[id] = level;
        const empty = state.spells.slots.findIndex((s) => !s);
        if (empty >= 0) state.spells.slots[empty] = id;
      });
      player.sendMessage(`§b${getSpell(id).name} granted at level ${level}.`);
      return;
    }
    // wd:grant_all [level] — learn every power for testing.
    if (event.id === "wd:grant_all") {
      const level = Math.max(1, Math.min(4, Number(argument) || 4));
      mutateState(player, (state) => {
        for (const id of SPELL_ORDER) state.spells.owned[id] = level;
        for (let i = 0; i < state.spells.slots.length; i++) state.spells.slots[i] = SPELL_ORDER[i];
      });
      player.sendMessage(`§bAll Will powers granted at level ${level}.`);
      return;
    }
    // wd:cast <id> [level] — cast a power directly for testing.
    if (event.id === "wd:cast") {
      const [id, lvlText] = argument.split(/\s+/);
      castSpellById(player, id, Number(lvlText) || 99);
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

console.warn("[Will & Destiny] Phase 2 systems online.");

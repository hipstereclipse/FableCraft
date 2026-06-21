// Will & Destiny quick-cast control. The permanent Will Focus is the only item
// the player carries to use magic:
//   use (hold, release) -> charge & cast the active quick-slot spell
//   crouch + use        -> hot-swap the active slot to the next assigned spell
// Charge uses itemStartUse/itemStopUse when the focus's use-duration component is
// honored; a plain itemUse path is kept as a fallback so the focus still casts if
// the charge component is ignored on a given build.
import { world, system } from "@minecraft/server";
import { WD_CONFIG } from "./config.js";
import { getState, mutateState } from "./state.js";
import { getSpell } from "./spells/registry.js";
import { castSpellById } from "./spells/shared/cast.js";
import { chargeLevelFromHold, chargeStage } from "./spells/shared/charge.js";
import { setCharging, clearCasting } from "./visuals.js";
import { showHudNotice } from "../fable_hud.js";

const FOCUS_ID = "wd:will_focus";
const holds = new Map(); // playerId -> { startTick, spellId, gesture, suppress, rampHandle, ownedLevel }

function isFocus(item) {
  return item?.typeId === FOCUS_ID;
}

export function getActiveSpellId(player) {
  const state = getState(player);
  const slots = state.spells.slots;
  return slots[state.spells.active] ?? slots.find(Boolean) ?? null;
}

function announceActive(player) {
  const state = getState(player);
  const id = state.spells.slots[state.spells.active] ?? state.spells.slots.find(Boolean);
  if (!id) {
    showHudNotice(player, "§7No Will power attuned — Hero Menu → Magic to assign quick-slots.", 50);
    return;
  }
  const spell = getSpell(id);
  const level = state.spells.owned[id] ?? 1;
  showHudNotice(player, `§9✦ Active: §f${spell?.name ?? id} §7Lv ${level} §8(slot ${state.spells.active + 1})`, 50);
}

function cycleActive(player) {
  const state = getState(player);
  const slots = state.spells.slots;
  if (!slots.some(Boolean)) {
    showHudNotice(player, "§7No Will power attuned — Hero Menu → Magic to assign quick-slots.", 50);
    return;
  }
  let idx = state.spells.active;
  for (let i = 0; i < slots.length; i++) {
    idx = (idx + 1) % slots.length;
    if (slots[idx]) break;
  }
  mutateState(player, (d) => { d.spells.active = idx; });
  try {
    player.playSound("note.hat", { pitch: 1.5 });
  } catch {
    // Audio is additive.
  }
  announceActive(player);
}

function chargeNotice(player, spell, stage, ownedLevel) {
  const pips = Array.from({ length: Math.max(1, ownedLevel) }, (_, i) => (i < stage ? "▰" : "▱")).join("");
  showHudNotice(player, `§f${spell.name} §9${pips} §7charge ${stage}`, 8);
}

function beginCharge(player, id) {
  const state = getState(player);
  const spell = getSpell(id);
  const ownedLevel = Math.max(0, Math.min(4, state.spells.owned[id] ?? 0));
  if (!spell || ownedLevel < 1) {
    showHudNotice(player, "§7You have not learned that Will power.", 40);
    holds.set(player.id, { suppress: true });
    return;
  }

  // Instant path: charging disabled or a non-charging spell.
  if (state.options.chargeEnabled === false || spell.charges === false) {
    holds.set(player.id, { suppress: true });
    castSpellById(player, id, 99);
    return;
  }

  const startTick = system.currentTick;
  setCharging(player, spell.gesture, 1);
  try {
    player.playSound("conduit.activate", { volume: 0.4, pitch: 0.8 });
  } catch {
    // Audio is additive.
  }
  const entry = { startTick, spellId: id, gesture: spell.gesture, suppress: false, ownedLevel, rampHandle: null };
  entry.rampHandle = system.runInterval(() => {
    if (!player.isValid) {
      try { system.clearRun(entry.rampHandle); } catch { /* already cleared */ }
      holds.delete(player.id);
      return;
    }
    const held = system.currentTick - startTick;
    const stage = chargeStage(held, ownedLevel);
    setCharging(player, spell.gesture, stage);
    chargeNotice(player, spell, stage, ownedLevel);
    // Safety release if itemStopUse never arrives (missed event / stuck hold).
    if (held > (WD_CONFIG.chargeMaxHoldTicks ?? 40) + 12) releaseCharge(player);
  }, 2);
  holds.set(player.id, entry);
}

function releaseCharge(player) {
  const hold = holds.get(player.id);
  if (!hold) return;
  holds.delete(player.id);
  if (hold.rampHandle != null) {
    try { system.clearRun(hold.rampHandle); } catch { /* already ended */ }
  }
  if (hold.suppress || !hold.spellId) {
    clearCasting(player);
    return;
  }
  const held = system.currentTick - hold.startTick;
  const requested = chargeLevelFromHold(held, { chargeEnabled: true, charges: true });
  castSpellById(player, hold.spellId, requested);
}

world.afterEvents.itemStartUse.subscribe((event) => {
  const player = event.source;
  if (!player || player.typeId !== "minecraft:player" || !isFocus(event.itemStack)) return;
  if (WD_CONFIG.cycleOnSneakUse && player.isSneaking) {
    holds.set(player.id, { suppress: true });
    cycleActive(player);
    return;
  }
  const id = getActiveSpellId(player);
  if (!id) {
    holds.set(player.id, { suppress: true });
    showHudNotice(player, "§7No Will power attuned — Hero Menu → Magic to assign quick-slots.", 50);
    return;
  }
  beginCharge(player, id);
});

world.afterEvents.itemStopUse.subscribe((event) => {
  const player = event.source;
  if (!player || player.typeId !== "minecraft:player" || !isFocus(event.itemStack)) return;
  releaseCharge(player);
});

if (world.afterEvents.itemCompleteUse) {
  world.afterEvents.itemCompleteUse.subscribe((event) => {
    const player = event.source;
    if (!player || player.typeId !== "minecraft:player" || !isFocus(event.itemStack)) return;
    releaseCharge(player);
  });
}

// Fallback: if a build ignores the focus's use-duration component, the charge
// events never fire and a plain itemUse arrives instead. Handle that as an
// instant cast / crouch-cycle. (When the charge component works, itemUse does
// not fire for the focus, so there is no double-cast.)
world.afterEvents.itemUse.subscribe((event) => {
  const player = event.source;
  if (!player || player.typeId !== "minecraft:player" || !isFocus(event.itemStack)) return;
  if (holds.has(player.id)) return; // charge path already owns this press
  if (WD_CONFIG.cycleOnSneakUse && player.isSneaking) {
    cycleActive(player);
    return;
  }
  const id = getActiveSpellId(player);
  if (!id) {
    showHudNotice(player, "§7No Will power attuned — Hero Menu → Magic to assign quick-slots.", 50);
    return;
  }
  castSpellById(player, id, 99);
});

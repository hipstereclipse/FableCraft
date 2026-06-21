// Will & Destiny spell acquisition. Spell tomes are consumed to permanently
// learn the spell into wd:state — they are never carried or cast. The player
// keeps only the permanent Will Focus; learned powers live in state, freeing
// inventory. A duplicate tome of a known power is a no-op refund (kept).
import { world } from "@minecraft/server";
import { WD_CONFIG } from "./config.js";
import { getState, mutateState } from "./state.js";
import { getSpell } from "./spells/registry.js";
import { showHudNotice } from "../fable_hud.js";

const TOME_PREFIX = "fc:spell_";

function removeOne(player, typeId) {
  const container = player.getComponent("minecraft:inventory")?.container;
  if (!container) return false;
  for (let slot = 0; slot < container.size; slot++) {
    const item = container.getItem(slot);
    if (item?.typeId !== typeId) continue;
    if (item.amount <= 1) container.setItem(slot, undefined);
    else {
      item.amount -= 1;
      container.setItem(slot, item);
    }
    return true;
  }
  return false;
}

export function learnFromTome(player, spellId, sourceTypeId) {
  const spell = getSpell(spellId);
  if (!spell) {
    showHudNotice(player, "§7This tome's power is unknown to your Will.", 50);
    return;
  }
  const state = getState(player);
  if ((state.spells.owned[spellId] ?? 0) >= 1) {
    showHudNotice(player, `§7${spell.name} is already woven into your soul.`, 50);
    return; // keep the duplicate tome (no-op refund)
  }

  mutateState(player, (draft) => {
    draft.spells.owned[spellId] = Math.max(1, draft.spells.owned[spellId] ?? 0);
    const empty = draft.spells.slots.findIndex((s) => !s);
    if (empty >= 0) draft.spells.slots[empty] = spellId;
  });
  if (WD_CONFIG.useLegacyFcProgressionBridge) {
    try {
      const key = `fc_spell_lvl_${spellId}`;
      const current = player.getDynamicProperty(key);
      player.setDynamicProperty(key, Math.max(1, typeof current === "number" ? current : 0));
    } catch {
      // The versioned owned-map remains authoritative if the legacy mirror fails.
    }
  }
  if (sourceTypeId) removeOne(player, sourceTypeId);

  try {
    player.playSound("beacon.power", { pitch: 1.6 });
  } catch {
    // Audio is additive.
  }
  showHudNotice(player, `§9✦ Learned §f${spell.name}§9 — it lives in your Will now.`, 60);
}

world.afterEvents.itemUse.subscribe((event) => {
  const player = event.source;
  const item = event.itemStack;
  if (!player || player.typeId !== "minecraft:player" || !item) return;
  const id = item.typeId;
  if (id.startsWith(TOME_PREFIX)) {
    learnFromTome(player, id.substring(TOME_PREFIX.length), id);
    return;
  }
  if (id === "fc:summoners_grimoire") learnFromTome(player, "summon", id);
});

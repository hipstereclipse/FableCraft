// Will & Destiny UI. This module owns focus attunement and spell upgrades.
import { ActionFormData } from "@minecraft/server-ui";
import { SPELL_REGISTRY } from "./spells/registry.js";
import { getState, mutateState } from "./state.js";

function titleCase(identifier) {
  return identifier.split("_").map((word) => word.charAt(0).toUpperCase() + word.slice(1)).join(" ");
}

export function openWillFocusMenu(player, onBack) {
  const state = getState(player);
  const owned = Object.entries(state.spells.owned)
    .filter(([id, level]) => SPELL_REGISTRY[id] && level > 0);
  const equipped = SPELL_REGISTRY[state.spells.equipped];
  const form = new ActionFormData()
    .title("§9Will & Destiny")
    .body([
      `§bMana: §f${Math.floor(state.mana.current)}/${state.mana.max}`,
      `§7Equipped: §f${equipped?.name ?? "None"}`,
      `§7Alignment: §f${state.alignment}`,
      "",
      "§8Select a learned Will power to equip it.",
    ].join("\n"));

  for (const [id, level] of owned) {
    const spell = SPELL_REGISTRY[id];
    form.button(
      `${id === state.spells.equipped ? "§b▶ " : "§7"}${spell.name} §fLv${level}\n§8${spell.family} · ${spell.manaCost(level)} mana`,
      `textures/items/spell_${id}`,
    );
  }
  const equippedLevel = state.spells.owned[state.spells.equipped] ?? 0;
  const upgradeCost = equippedLevel * 150;
  form.button(`§dDeepen ${equipped?.name ?? "spell"}\n§8${upgradeCost} Will XP`);
  form.button("§8Back");

  form.show(player).then((response) => {
    if (response.canceled || response.selection == null) return;
    if (response.selection < owned.length) {
      const [id] = owned[response.selection];
      mutateState(player, (draft) => {
        draft.spells.equipped = id;
      });
      player.sendMessage(`§9✦ ${SPELL_REGISTRY[id].name} is now bound to your Will Focus.`);
      return openWillFocusMenu(player, onBack);
    }
    if (response.selection === owned.length + 1) {
      if (onBack) onBack();
      return;
    }
    if (response.selection !== owned.length || !equipped) return;
    if (equippedLevel >= 4) {
      player.sendMessage(`§7${equipped.name} is already mastered.`);
      return openWillFocusMenu(player, onBack);
    }
    if (state.xp.will < upgradeCost) {
      player.sendMessage(`§7You need ${upgradeCost} Will XP to deepen ${equipped.name}.`);
      return openWillFocusMenu(player, onBack);
    }
    mutateState(player, (draft) => {
      draft.xp.will -= upgradeCost;
      draft.spells.owned[equipped.id] = equippedLevel + 1;
      try {
        player.setDynamicProperty(`fc_spell_lvl_${equipped.id}`, equippedLevel + 1);
      } catch {
        // The wd state still owns the upgraded level without the legacy bridge.
      }
    });
    player.sendMessage(`§b✦ ${titleCase(equipped.id)} rises to level ${equippedLevel + 1}.`);
    try {
      player.playSound("fc.level_up", { volume: 0.8, pitch: 1.2 });
    } catch {
      // Text feedback is sufficient if the sound is unavailable.
    }
    openWillFocusMenu(player, onBack);
  }).catch(() => {
    // Forms may be rejected while another UI screen is open.
  });
}

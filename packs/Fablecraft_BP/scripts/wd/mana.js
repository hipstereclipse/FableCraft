// Will & Destiny mana. This module owns capacity, spending, and throttled regen.
import { WD_CONFIG } from "./config.js";
import { getState, mutateState } from "./state.js";

export function maxManaForState(state) {
  return 100 + Math.max(0, state.attributes.magicPower) * 50;
}

export function spendMana(player, amount) {
  const cost = Math.max(0, amount);
  const state = getState(player);
  if (state.mana.current < cost) return false;
  mutateState(player, (draft) => {
    draft.mana.max = maxManaForState(draft);
    draft.mana.current = Math.max(0, draft.mana.current - cost);
  });
  return true;
}

export function regenerateMana(player) {
  mutateState(player, (state) => {
    state.mana.max = maxManaForState(state);
    const perPass = WD_CONFIG.manaRegenPerSecond * (WD_CONFIG.manaRegenIntervalTicks / 20);
    state.mana.current = Math.min(state.mana.max, state.mana.current + perPass);
  });
}

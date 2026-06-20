// Will & Destiny spell registry. This module owns data-driven cast dispatch.
import { spawnParticle } from "../particles.js";
import { getState, mutateState } from "../state.js";
import { spendMana } from "../mana.js";
import { addDisciplineXp } from "../stats.js";
import { FIREBALL_SPELL } from "./fireball.js";

const FIZZLE_BLUE = { red: 0.18, green: 0.36, blue: 0.95, alpha: 0.72 };

export const SPELL_REGISTRY = Object.freeze({
  [FIREBALL_SPELL.id]: FIREBALL_SPELL,
});

function failCast(player, message) {
  player.onScreenDisplay.setActionBar(`§9${message}`);
  spawnParticle(
    player.dimension,
    "wd:will_fizzle",
    { x: player.location.x, y: player.location.y + 1.25, z: player.location.z },
    FIZZLE_BLUE,
    0.42,
    0.5,
  );
  try {
    player.playSound("random.fizz", { volume: 0.45, pitch: 0.7 });
  } catch {
    // Feedback remains available through action-bar text and particles.
  }
  return false;
}

export function castEquippedSpell(player) {
  const state = getState(player);
  const spell = SPELL_REGISTRY[state.spells.equipped];
  if (!spell) return failCast(player, "No Will power is equipped.");

  const level = Math.max(1, Math.min(4, state.spells.owned[spell.id] ?? 0));
  if (!level) return failCast(player, "You have not learned that Will power.");
  if (player.getItemCooldown("wd_will_focus") > 0) {
    return failCast(player, "The Will is still gathering.");
  }

  const cost = spell.manaCost(level);
  if (!spendMana(player, cost)) return failCast(player, `Not enough mana. ${cost} required.`);
  let success = false;
  try {
    success = spell.cast(player, level, { state }) === true;
  } catch (error) {
    console.warn(`[Will & Destiny] ${spell.id} cast failed: ${error}`);
  }
  if (!success) {
    mutateState(player, (draft) => {
      draft.mana.current = Math.min(draft.mana.max, draft.mana.current + cost);
    });
    return failCast(player, "The spell could not take form.");
  }

  try {
    player.startItemCooldown("wd_will_focus", spell.cooldownTicks(level));
  } catch {
    // State and gameplay remain valid if a client cannot display the cooldown.
  }
  addDisciplineXp(player, "will", Math.max(1, Math.floor(cost * 0.5)));
  return true;
}

// Will & Destiny cast pipeline. One gate for every spell: owned level ->
// align lock -> charge level -> mana cost -> cooldown -> gesture/anim/sound ->
// body. Generalized from the Phase 1 Fireball cast.
import { system } from "@minecraft/server";
import { WD_CONFIG } from "../../config.js";
import { spawnParticle } from "../../particles.js";
import { spendMana } from "../../mana.js";
import { addDisciplineXp } from "../../stats.js";
import { clamp, getState, mutateState } from "../../state.js";
import { setCasting } from "../../visuals.js";
import { SPELL_REGISTRY } from "../registry.js";

const FIZZLE_BLUE = { red: 0.18, green: 0.36, blue: 0.95, alpha: 0.72 };

export function fizzle(player, message) {
  try {
    player.onScreenDisplay.setActionBar(`§9${message}`);
  } catch {
    // Action-bar text is feedback only.
  }
  try {
    spawnParticle(
      player.dimension,
      "wd:will_fizzle",
      { x: player.location.x, y: player.location.y + 1.25, z: player.location.z },
      FIZZLE_BLUE,
      0.42,
      0.5,
    );
    player.playSound("random.fizz", { volume: 0.45, pitch: 0.7 });
  } catch {
    // Feedback remains available through action-bar text.
  }
  return false;
}

// Mana cost for a level, modulated by capstone align discount and Magic Power.
function manaCost(spell, level, state) {
  let cost = spell.baseMana * (1 + (level - 1) * 0.33);
  if (spell.alignCost) {
    const align = state.alignment;
    const favored = Math.sign(align) === Math.sign(spell.alignCost) && Math.abs(align) >= 100;
    const opposed = Math.sign(align) === -Math.sign(spell.alignCost) && Math.abs(align) >= 100;
    if (favored) cost *= 0.6;
    else if (opposed) cost *= 1.5;
  }
  cost *= 1 - Math.min(0.25, Math.max(0, state.attributes.magicPower) * 0.025);
  return Math.max(1, Math.round(cost));
}

function cooldownTicks(spell, level) {
  return Math.max(5, Math.round(spell.cooldown * (1 - (level - 1) * 0.06)));
}

function castDuration(level) {
  return 12 + level * 2;
}

function lockOk(spell, align) {
  if (!spell.alignLock) return true;
  return spell.alignLock > 0 ? align >= 100 : align <= -100;
}

function lockMessage(spell) {
  return spell.alignLock > 0 ? "Your soul is not pure enough." : "Your soul is not dark enough.";
}

function playCastCue(player, spell, level) {
  try {
    player.playAnimation("animation.player.wd.spell_cast", { blendOutTime: 0.2 });
  } catch {
    // The gesture also plays from the RP animation controller via wd:casting.
  }
  try {
    player.playSound("fc.spell_cast", { volume: 0.9, pitch: 0.86 + level * 0.05 });
  } catch {
    // Sound is additive.
  }
}

// Cast a spell by id at a requested level (the sentinel 99 means "owned level").
export function castSpellById(player, id, requestedLevel = 99) {
  const spell = SPELL_REGISTRY[id];
  if (!spell) return fizzle(player, "No Will power is attuned.");
  if (WD_CONFIG.perSpellEnabled?.[id] === false) return fizzle(player, `${spell.name} is dormant.`);
  if (typeof spell.cast !== "function") return fizzle(player, `${spell.name} is not yet woven. (coming soon)`);

  const state = getState(player);
  const ownedLevel = clamp(Math.floor(state.spells.owned[id] ?? 0), 0, 4);
  if (ownedLevel < 1) return fizzle(player, "You have not learned that Will power.");

  if (!lockOk(spell, state.alignment)) return fizzle(player, lockMessage(spell));

  const now = system.currentTick;
  const ready = state.cooldowns[id] ?? 0;
  if (now < ready) return fizzle(player, "The Will is still gathering.");

  // Charge level, clamped to owned and then down to affordable mana.
  let level = clamp(Math.floor(requestedLevel), 1, ownedLevel);
  let cost = manaCost(spell, level, state);
  while (level > 1 && cost > state.mana.current) {
    level -= 1;
    cost = manaCost(spell, level, state);
  }
  if (cost > state.mana.current) return fizzle(player, `Not enough Will. ${cost} required.`);
  if (!spendMana(player, cost)) return fizzle(player, `Not enough Will. ${cost} required.`);

  setCasting(player, spell.gesture, level, castDuration(level));
  playCastCue(player, spell, level);
  try {
    player.startItemCooldown("wd_will_focus", castDuration(level));
  } catch {
    // Item cooldown is a display aid; the real gate is state.cooldowns.
  }

  let success = false;
  try {
    success = spell.cast({ player, spell, level, state, dimension: player.dimension }) === true;
  } catch (error) {
    console.warn(`[Will & Destiny] ${id} cast failed: ${error}`);
  }
  if (!success) {
    mutateState(player, (draft) => {
      draft.mana.current = Math.min(draft.mana.max, draft.mana.current + cost);
    });
    return fizzle(player, "The spell could not take form.");
  }

  mutateState(player, (draft) => {
    draft.cooldowns[id] = system.currentTick + cooldownTicks(spell, level);
  });
  addDisciplineXp(player, "will", Math.max(1, Math.floor(cost * 0.5)));
  return true;
}

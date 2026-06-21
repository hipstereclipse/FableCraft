// Will & Destiny XP. This module owns discipline awards and tier derivation.
import { system, world } from "@minecraft/server";
import { ALIGNMENT_DEEDS, changeAlignment } from "./alignment.js";
import { mutateState, tierFromXp } from "./state.js";

const HOSTILE_FAMILIES = ["monster", "fc_hostile", "fc_boss"];
const INNOCENT_TYPES = new Map([
  ["minecraft:villager", ALIGNMENT_DEEDS.villagerKill],
  ["minecraft:villager_v2", ALIGNMENT_DEEDS.villagerKill],
  ["minecraft:iron_golem", ALIGNMENT_DEEDS.ironGolemKill],
  ["minecraft:wolf", ALIGNMENT_DEEDS.tamedPetKill],
  ["minecraft:cat", ALIGNMENT_DEEDS.tamedPetKill],
  ["minecraft:parrot", ALIGNMENT_DEEDS.tamedPetKill],
]);

function hasFamily(entity, family) {
  try {
    return entity.getComponent("minecraft:type_family")?.hasTypeFamily(family) === true;
  } catch {
    return false;
  }
}

function isHostile(entity) {
  return HOSTILE_FAMILIES.some((family) => hasFamily(entity, family));
}

export function addDisciplineXp(player, discipline, amount) {
  const award = Math.max(0, Math.floor(amount));
  if (!award) return;
  mutateState(player, (state) => {
    state.xp[discipline] = Math.max(0, (state.xp[discipline] ?? 0) + award);
    if (discipline !== "generic") {
      state.xp.generic = Math.max(0, state.xp.generic + Math.floor(award * 0.4));
    }
  });
  // Derive the legacy XP properties unconditionally. Post-cutover the legacy
  // guild upgrade platform still spends fc_xp_* directly, so XP mirrors fc_* <->
  // wd:state (see reconcileLegacyProgression); writing the gain to fc_xp_* here
  // keeps the two equal so there is no double-count.
  const legacyKey = {
    generic: "fc_xp_general",
    strength: "fc_xp_strength",
    skill: "fc_xp_skill",
    will: "fc_xp_will",
  }[discipline];
  try {
    const current = player.getDynamicProperty(legacyKey);
    player.setDynamicProperty(legacyKey, (typeof current === "number" ? current : 0) + award);
    if (discipline !== "generic") {
      const generic = player.getDynamicProperty("fc_xp_general");
      player.setDynamicProperty(
        "fc_xp_general",
        (typeof generic === "number" ? generic : 0) + Math.floor(award * 0.4),
      );
    }
  } catch {
    // The versioned state remains valid if the legacy property write fails.
  }
}

export function getDisciplineTiers(state) {
  return {
    strength: tierFromXp(state.xp.strength),
    skill: tierFromXp(state.xp.skill),
    will: tierFromXp(state.xp.will),
  };
}

export function markSpellDamage(player) {
  try {
    player.setDynamicProperty("wd:last_spell_damage_tick", system.currentTick);
  } catch {
    // Kill attribution falls back to melee/ranged classification.
  }
}

export function registerStatEvents() {
  // Phase 3 cutover: the legacy entityDie handler (main.js) is the single deed
  // path — it computes kill morality/XP from DATA.killMorality/killXp (entangled
  // with quests/factions/bounty/bosses/loot) and now FUNNELS those values through
  // wd/ (addMorality -> changeAlignment, giveXp -> addDisciplineXp). Enabling this
  // parallel wd/ handler would double-count, so it stays disabled.
  return;
  // eslint-disable-next-line no-unreachable
  world.afterEvents.entityDie.subscribe((event) => {
    const dead = event.deadEntity;
    const source = event.damageSource;
    const player = source?.damagingEntity;
    if (!player || player.typeId !== "minecraft:player" || dead.typeId === "minecraft:player") return;

    const spellTick = player.getDynamicProperty("wd:last_spell_damage_tick");
    const recentSpell = typeof spellTick === "number" && system.currentTick - spellTick <= 20;
    const discipline = recentSpell ? "will" : source?.damagingProjectile ? "skill" : "strength";
    const baseXp = hasFamily(dead, "fc_boss") ? 50 : isHostile(dead) ? 10 : 4;
    addDisciplineXp(player, discipline, baseXp);

    if (hasFamily(dead, "fc_boss")) changeAlignment(player, ALIGNMENT_DEEDS.bossKill);
    else if (isHostile(dead)) changeAlignment(player, ALIGNMENT_DEEDS.hostileKill, false);
    else if (INNOCENT_TYPES.has(dead.typeId)) changeAlignment(player, INNOCENT_TYPES.get(dead.typeId));
  });
}

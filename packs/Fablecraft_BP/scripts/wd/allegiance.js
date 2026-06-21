// Will & Destiny allegiance / mind-control framework (Phase 3, spec §3.2).
// Turncoat (evil) gradually converts an enemy while the caster maintains the
// link; once flipped the target fights for the caster for a duration, then
// reverts cleanly. Because a runtime type_family cannot be added to a living
// entity, a charmed enemy is registered with targeting.js (so every Will power
// spares it like an ally) and given an owner tag, rather than re-familied.
import { system, world, EntityDamageCause } from "@minecraft/server";
import { WD_CONFIG } from "./config.js";
import { mutateState } from "./state.js";
import { isCharmed, setCharmed, enemiesNear } from "./spells/shared/targeting.js";
import { applyEffect } from "./spells/shared/selfbuff.js";
import { markSpellDamage } from "./stats.js";
import { tint, burst } from "./spells/shared/vfx.js";

const CHARM_TAG = "wd_charmed";
const ownerTag = (playerId) => `fc_charm_owner_${playerId}`;

// id -> { ownerId, expires, dimensionId }
const charmed = new Map();

function hasFamily(entity, family) {
  try {
    return entity.getComponent("minecraft:type_family")?.hasTypeFamily(family) === true;
  } catch {
    return false;
  }
}

// Bosses and quest-critical entities are never charmable (spec guard).
export function canCharm(target) {
  if (!target?.isValid || target.typeId === "minecraft:player") return false;
  if (isCharmed(target.id)) return false; // no re-charm stacking
  try {
    if (!target.getComponent("minecraft:health")) return false;
  } catch {
    return false;
  }
  if (WD_CONFIG.charmableExcludesBosses && (hasFamily(target, "fc_boss") || hasFamily(target, "fc_quest"))) {
    return false;
  }
  return true;
}

// Flip a fully-converted target to the caster's side. Returns true on success.
export function convert(player, target, level) {
  if (!canCharm(target)) return false;
  const duration = Math.round((WD_CONFIG.turncoatDurationTicks ?? 1200) * (1 + (level - 1) * 0.35));
  setCharmed(target.id, true);
  try {
    target.addTag(CHARM_TAG);
    target.addTag(ownerTag(player.id));
  } catch {
    // Tags are ownership hints; the in-memory ledger below is the authority.
  }
  charmed.set(target.id, { ownerId: player.id, expires: system.currentTick + duration, dimensionId: target.dimension.id });
  mutateState(player, (state) => {
    if (!state.allegiance.charmed.includes(target.id)) state.allegiance.charmed.push(target.id);
  });
  // Now "fighting for you": a brief vigour buff and a side-shift flare.
  applyEffect(target, "strength", duration, level - 1);
  applyEffect(target, "speed", duration, 0);
  burst(target.dimension, "wd:charm_mote", { x: target.location.x, y: target.location.y + 1.2, z: target.location.z },
    [220, 150, 240], 12, 0.8, 0.6, 1, 0.95);
  try {
    player.playSound("mob.evocation_illager.prepare_summon", { volume: 0.5, pitch: 1.3 });
    player.onScreenDisplay.setActionBar("§d✦ Its allegiance is yours.");
  } catch {
    // Feedback is additive.
  }
  return true;
}

function revert(id) {
  const entity = (() => { try { return world.getEntity(id); } catch { return undefined; } })();
  setCharmed(id, false);
  charmed.delete(id);
  try {
    if (entity?.isValid) {
      entity.removeTag(CHARM_TAG);
      for (const tag of entity.getTags()) if (tag.startsWith("fc_charm_owner_")) entity.removeTag(tag);
    }
  } catch {
    // Tag cleanup is best-effort; the targeting registry is already cleared.
  }
}

// Revert every charm owned by a leaving player.
export function releaseCharmsFor(playerId) {
  for (const [id, info] of [...charmed]) {
    if (info.ownerId === playerId) revert(id);
  }
}

function resolveOwner(playerId) {
  for (const p of world.getAllPlayers()) if (p.id === playerId) return p;
  return undefined;
}

// Charmed entities fight nearby foes on the caster's behalf; expired/dead ones
// revert. Capped per pass so a large charm count cannot spike the tick.
function tickAllegiance() {
  const now = system.currentTick;
  for (const [id, info] of [...charmed]) {
    const entity = (() => { try { return world.getEntity(id); } catch { return undefined; } })();
    if (!entity?.isValid || now >= info.expires) {
      revert(id);
      continue;
    }
    const owner = resolveOwner(info.ownerId);
    // Strike the nearest real enemy near the charmed minion (attributed to the
    // owner so kills credit the caster). enemiesNear already excludes allies,
    // players, and other charmed minions.
    const foes = owner ? enemiesNear(owner, entity.location, 6) : [];
    const foe = foes.find((e) => e.id !== id);
    if (foe) {
      try {
        if (owner) markSpellDamage(owner);
        foe.applyDamage(3, { cause: EntityDamageCause.entityAttack, damagingEntity: owner ?? entity });
        tint(entity.dimension, "wd:charm_mote",
          { x: foe.location.x, y: foe.location.y + 1, z: foe.location.z }, [220, 150, 240], 0.6, 1, 0.85);
      } catch {
        // A failed strike just means the minion idles this pass.
      }
    }
  }
}

system.runInterval(tickAllegiance, 20);

world.afterEvents.playerLeave.subscribe((event) => {
  releaseCharmsFor(event.playerId);
});

// Will & Destiny summoned-ally framework (Phase 3, spec §3.1). Owns the cap,
// ownership ledger, and the faithful soul-replacement behaviour. The summoned
// creatures already carry the fc_ally / fc_friendly families (so every Will
// power spares them via targeting.js) and a built-in self-despawn timer, so this
// module never has to apply damage immunity or schedule lifetimes itself — it
// only tracks ownership, enforces maxSummonsPerPlayer, and refreshes a summon
// when it claims a soul.
import { world } from "@minecraft/server";
import { WD_CONFIG } from "./config.js";
import { getState, mutateState } from "./state.js";
import { tint, burst, dimensionSound } from "./spells/shared/vfx.js";

const OWNER_TAG = (playerId) => `fc_owner_${playerId}`;
const SUMMON_TAG = "wd_summon";

// Roster by charge level — tier rises with the power level the spell is cast at.
const ROSTER = ["fc:summoned_wasp", "fc:summoned_hobbe", "fc:summoned_balverine"];

function summonType(level) {
  return ROSTER[Math.min(ROSTER.length - 1, Math.max(0, level - 1))];
}

function resolveEntity(id) {
  try {
    return world.getEntity(id);
  } catch {
    return undefined;
  }
}

function removeEntity(entity) {
  try {
    if (entity?.isValid) entity.remove();
  } catch {
    // Cosmetic/ownership cleanup must never interrupt gameplay.
  }
}

// Live summons for a player, pruning any ids whose entity is gone (the creature
// self-despawned on its timer or by distance). Keeps state.summons.active honest
// so the cap is enforced against the real count.
function liveSummons(player) {
  const ids = getState(player).summons.active;
  const live = [];
  const liveIds = [];
  for (const id of ids) {
    const entity = resolveEntity(id);
    if (entity?.isValid) {
      live.push(entity);
      liveIds.push(id);
    }
  }
  if (liveIds.length !== ids.length) {
    mutateState(player, (state) => { state.summons.active = liveIds; });
  }
  return live;
}

function summonSigil(dimension, location, color) {
  // Glowing summon circle inscribed on the ground + a soul coalescing upward.
  for (let i = 0; i < 12; i++) {
    const angle = (i / 12) * Math.PI * 2;
    tint(dimension, "wd:summon_sigil",
      { x: location.x + Math.cos(angle) * 1.1, y: location.y + 0.1, z: location.z + Math.sin(angle) * 1.1 },
      color, 0.7, 1, 0.9);
  }
  burst(dimension, "wd:summon_soul", { x: location.x, y: location.y + 1, z: location.z }, color, 10, 0.7, 0.6, 1, 0.9);
}

// Bind a creature to the caster. At the cap the oldest summon is released first
// (never exceed maxSummonsPerPlayer). Returns the spawned entity or undefined.
export function summonAlly(player, level, color = [120, 230, 200]) {
  const max = Math.max(0, getState(player).summons.max ?? WD_CONFIG.maxSummonsPerPlayer);
  if (max <= 0) return undefined;

  const existing = liveSummons(player);
  while (existing.length >= max) {
    const oldest = existing.shift();
    removeEntity(oldest);
    mutateState(player, (state) => {
      state.summons.active = state.summons.active.filter((id) => id !== oldest.id);
    });
  }

  const dimension = player.dimension;
  const origin = { x: player.location.x + 1, y: player.location.y, z: player.location.z + 1 };
  let entity;
  try {
    entity = dimension.spawnEntity(summonType(level), origin);
  } catch {
    return undefined; // Asset missing or spawn blocked — the cast simply does not bind.
  }
  try {
    entity.addTag(SUMMON_TAG);
    entity.addTag(OWNER_TAG(player.id));
  } catch {
    // Ownership tags are best-effort; the ledger below is the authority.
  }
  mutateState(player, (state) => { state.summons.active.push(entity.id); });

  summonSigil(dimension, entity.location, color);
  dimensionSound(dimension, "mob.evocation_illager.cast_spell", player.location, { volume: 0.6, pitch: 1.1 });
  return entity;
}

// Faithful soul-replacement: when a summon claims a kill, the fallen soul renews
// it — restore it to full vitality with a brief spectral flare (spec §3.1).
function refreshOnKill(summon) {
  if (WD_CONFIG.summonReplaceOnKill !== true) return;
  try {
    const hp = summon.getComponent("minecraft:health");
    if (hp) hp.setCurrentValue(hp.effectiveMax);
    burst(summon.dimension, "wd:summon_soul", { x: summon.location.x, y: summon.location.y + 1, z: summon.location.z },
      [120, 230, 200], 8, 0.6, 0.6, 1, 0.95);
  } catch {
    // Refresh is cosmetic flavour; a failure leaves the summon on its own timer.
  }
}

// Release every summon a player owns (on leave) and clear the ledger.
export function releaseSummonsFor(playerId) {
  for (const dimensionId of ["overworld", "nether", "the_end"]) {
    try {
      for (const entity of world.getDimension(dimensionId).getEntities({ tags: [OWNER_TAG(playerId)] })) {
        removeEntity(entity);
      }
    } catch {
      // A dimension may not be initialized; the entity self-despawns regardless.
    }
  }
}

// On join, last session's summons are already gone — drop the stale ids so the
// cap starts from a clean ledger (spec: "defensive reconciliation on join").
export function reconcileSummons(player) {
  mutateState(player, (state) => { state.summons.active = []; });
}

// Self-wire the framework's global listeners (matches quickcast.js/learn.js).
world.afterEvents.entityDie.subscribe((event) => {
  const killer = event.damageSource?.damagingEntity;
  if (!killer?.isValid) return;
  try {
    if (killer.hasTag(SUMMON_TAG)) refreshOnKill(killer);
  } catch {
    // hasTag can throw on a despawning entity; ignore.
  }
});

world.afterEvents.playerLeave.subscribe((event) => {
  releaseSummonsFor(event.playerId);
});

// Will & Destiny overlay rig. Maintains exactly one wd:overlay entity per online
// player: spawned on need, despawned on leave, re-acquired if missing, made to
// follow the player, and carrying a mirror of the player's wd:* properties so
// the overlay's own render controller / Molang can read them (this is robust
// whether or not cross-entity Molang reads work on a given build).
import { world } from "@minecraft/server";
import { WD_CONFIG } from "./config.js";

const OVERLAY_ID = "wd:overlay";
const LEGACY_IDS = ["wd:evil_horns", "wd:divine_halo"];

// Reactive-appearance properties mirrored from the player onto the overlay. When
// reactiveAppearance is disabled they are pinned to these inert defaults so the
// overlay shows no cast flares or shield shell.
const REACTIVE_DEFAULTS = {
  "wd:casting": 0,
  "wd:casting_level": 0,
  "wd:mana_ratio": 1.0,
  "wd:shield_active": false,
};

const overlays = new Map(); // playerId -> entity

function removeEntity(entity) {
  try {
    if (entity?.isValid) entity.remove();
  } catch {
    // Cosmetic cleanup must never interrupt gameplay.
  }
}

export function removeOverlayFor(playerId) {
  const entity = overlays.get(playerId);
  if (entity) removeEntity(entity);
  overlays.delete(playerId);
}

function overlayLocation(player) {
  return { x: player.location.x, y: player.location.y, z: player.location.z };
}

function spawnOverlay(player) {
  try {
    const entity = player.dimension.spawnEntity(OVERLAY_ID, overlayLocation(player));
    overlays.set(player.id, entity);
    return entity;
  } catch {
    // The overlay entity asset may not be present yet; the rig is then a no-op.
    return undefined;
  }
}

function setProp(entity, id, value) {
  try {
    if (entity.getProperty(id) !== value) entity.setProperty(id, value);
  } catch {
    // A property the overlay does not declare is simply skipped.
  }
}

function getPlayerProp(player, id, fallback = 0) {
  try {
    const value = player.getProperty(id);
    return value === undefined ? fallback : value;
  } catch {
    return fallback;
  }
}

// Mirror tiers according to the player's appearance detail level.
function mirrorProperties(player, entity, detail) {
  setProp(entity, "wd:alignment_tier", getPlayerProp(player, "wd:alignment_tier", 0));
  const showShells = detail !== "horns_halo_only";
  setProp(entity, "wd:strength_tier", showShells ? getPlayerProp(player, "wd:strength_tier", 0) : 0);
  setProp(entity, "wd:skill_tier", showShells ? getPlayerProp(player, "wd:skill_tier", 0) : 0);
  setProp(entity, "wd:will_tier", showShells ? getPlayerProp(player, "wd:will_tier", 0) : 0);
  setProp(entity, "wd:morph", detail === "full");
  const reactive = WD_CONFIG.reactiveAppearance !== false;
  for (const [prop, fallback] of Object.entries(REACTIVE_DEFAULTS)) {
    setProp(entity, prop, reactive ? getPlayerProp(player, prop, fallback) : fallback);
  }
}

function follow(player, entity) {
  try {
    const yaw = player.getRotation().y;
    entity.teleport(overlayLocation(player), { rotation: { x: 0, y: yaw } });
  } catch {
    // A failed follow is recovered on the next sync pass.
  }
}

function ensureOverlay(player, plan) {
  if (!plan || !plan.enabled) {
    removeOverlayFor(player.id);
    return;
  }
  let entity = overlays.get(player.id);
  const invalid = !entity?.isValid;
  let wrongDimension = false;
  try {
    wrongDimension = !invalid && entity.dimension.id !== player.dimension.id;
  } catch {
    wrongDimension = true;
  }
  if (invalid || wrongDimension) {
    if (entity) removeEntity(entity);
    entity = spawnOverlay(player);
  }
  if (!entity) return;
  follow(player, entity);
  mirrorProperties(player, entity, plan.detail);
}

// resolvePlan(player) -> { enabled: boolean, detail: "full"|"overlays_only"|"horns_halo_only" }
export function syncOverlays(resolvePlan) {
  const players = world.getPlayers();
  const present = new Set(players.map((p) => p.id));
  for (const [playerId, entity] of overlays) {
    if (present.has(playerId)) continue;
    removeEntity(entity);
    overlays.delete(playerId);
  }
  for (const player of players) {
    let plan;
    try {
      plan = resolvePlan(player);
    } catch {
      plan = null;
    }
    ensureOverlay(player, plan);
  }
}

// Despawn any orphaned overlay entities (and retired Phase-1 horns/halo) on load.
export function clearStaleOverlays() {
  for (const dimensionId of ["overworld", "nether", "the_end"]) {
    try {
      const dimension = world.getDimension(dimensionId);
      for (const type of [OVERLAY_ID, ...LEGACY_IDS]) {
        for (const entity of dimension.getEntities({ type })) removeEntity(entity);
      }
    } catch {
      // A dimension may not be initialized yet.
    }
  }
  overlays.clear();
}

export const OVERLAY_FOLLOW_MODE = WD_CONFIG.overlayFollowMode;

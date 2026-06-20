// Script-driven morality overlays. These entities preserve player skins and
// armor while adding third-person horns or a halo at extreme alignment.
import { system, world } from "@minecraft/server";
import { WD_CONFIG } from "./config.js";
import { alignmentTier } from "./alignment.js";
import { getState } from "./state.js";

const TYPES = Object.freeze({
  evil: "wd:evil_horns",
  divine: "wd:divine_halo",
});

const activeCosmetics = new Map();

function removeEntity(entity) {
  try {
    if (entity?.isValid) entity.remove();
  } catch {
    // Cosmetic cleanup must not interrupt gameplay.
  }
}

function desiredKind(player) {
  let tier;
  try {
    tier = Number(player.getProperty("wd:alignment_tier"));
  } catch {
    tier = alignmentTier(getState(player).alignment);
  }
  if (!Number.isFinite(tier)) tier = alignmentTier(getState(player).alignment);
  if (tier <= -WD_CONFIG.alignmentAppearanceTier) return "evil";
  if (tier >= WD_CONFIG.alignmentAppearanceTier) return "divine";
  return undefined;
}

function cosmeticLocation(player) {
  return {
    x: player.location.x,
    y: player.location.y + (player.isSneaking ? -0.18 : 0),
    z: player.location.z,
  };
}

function facePlayerDirection(entity, player, location) {
  const view = player.getViewDirection();
  const horizontal = Math.hypot(view.x, view.z);
  const x = horizontal > 0.001 ? view.x / horizontal : 0;
  const z = horizontal > 0.001 ? view.z / horizontal : 1;
  entity.teleport(location, {
    facingLocation: {
      x: location.x + x,
      y: location.y + 1,
      z: location.z + z,
    },
  });
}

function spawnCosmetic(player, kind) {
  try {
    const entity = player.dimension.spawnEntity(TYPES[kind], cosmeticLocation(player));
    activeCosmetics.set(player.id, { entity, kind });
    return entity;
  } catch {
    return undefined;
  }
}

export function syncAlignmentAppearance() {
  const players = world.getPlayers();
  const present = new Set(players.map((player) => player.id));

  for (const [playerId, entry] of activeCosmetics) {
    if (present.has(playerId)) continue;
    removeEntity(entry.entity);
    activeCosmetics.delete(playerId);
  }

  for (const player of players) {
    const kind = desiredKind(player);
    let entry = activeCosmetics.get(player.id);

    if (!kind) {
      if (entry) removeEntity(entry.entity);
      activeCosmetics.delete(player.id);
      continue;
    }

    const wrongKind = entry?.kind !== kind;
    const invalid = !entry?.entity?.isValid;
    let wrongDimension = false;
    try {
      wrongDimension = !invalid && entry.entity.dimension.id !== player.dimension.id;
    } catch {
      wrongDimension = true;
    }

    if (wrongKind || invalid || wrongDimension) {
      if (entry) removeEntity(entry.entity);
      const entity = spawnCosmetic(player, kind);
      entry = entity ? { entity, kind } : undefined;
    }
    if (!entry) continue;

    try {
      facePlayerDirection(entry.entity, player, cosmeticLocation(player));
    } catch {
      removeEntity(entry.entity);
      activeCosmetics.delete(player.id);
    }
  }
}

export function clearStaleAlignmentCosmetics() {
  for (const dimensionId of ("overworld", "nether", "the_end")) {
    try {
      const dimension = world.getDimension(dimensionId);
      for (const type of Object.values(TYPES)) {
        for (const entity of dimension.getEntities({ type })) removeEntity(entity);
      }
    } catch {
      // A dimension may not be initialized yet.
    }
  }
  activeCosmetics.clear();
}

system.runTimeout(clearStaleAlignmentCosmetics, 1);

// Heal Life — Physical (good). Trade Will for health; at higher levels pass
// health to nearby non-hostiles. Cast = green-gold restorative motes rise with a
// soft radiant pulse; at L3+ a healing tether links to nearby allies.
import { healEntity } from "./shared/combat.js";
import { drawBeam } from "./shared/beam.js";
import { tint, burst, dimensionSound } from "./shared/vfx.js";

const SELF_HEAL = [0, 4, 7, 10, 12];
const ALLY_RADIUS = [0, 0, 0, 3, 4];

function isAlly(entity, player) {
  if (!entity?.isValid || entity.id === player.id) return false;
  if (entity.typeId === "minecraft:player") return true;
  try {
    return entity.getComponent("minecraft:type_family")?.hasTypeFamily("fc_ally") === true;
  } catch {
    return false;
  }
}

export function healLifeCast(ctx) {
  const { player, level, spell } = ctx;
  const center = { x: player.location.x, y: player.location.y + 1, z: player.location.z };

  healEntity(player, SELF_HEAL[level]);
  for (let i = 0; i < 5 + level; i++) {
    const loc = { x: center.x + (Math.random() - 0.5) * 0.8, y: center.y - 0.4 + i * 0.25, z: center.z + (Math.random() - 0.5) * 0.8 };
    tint(player.dimension, "wd:heal_mote", loc, spell.color, 0.5 + level * 0.06, level / 4, 0.9);
  }
  burst(player.dimension, "wd:heal_pulse", center, spell.color, 6, 1.0, 0.7, level / 4, 0.7);
  dimensionSound(player.dimension, "beacon.power", player.location, { volume: 0.6, pitch: 1.4 });

  const radius = ALLY_RADIUS[level];
  if (radius > 0) {
    let allies = [];
    try {
      allies = player.dimension.getEntities({ location: player.location, maxDistance: radius }).filter((e) => isAlly(e, player));
    } catch {
      allies = [];
    }
    for (const ally of allies) {
      healEntity(ally, Math.round(SELF_HEAL[level] * 0.6));
      drawBeam(center, { x: ally.location.x, y: ally.location.y + 1, z: ally.location.z }, (point) => {
        tint(player.dimension, "wd:heal_mote", point, spell.color, 0.35, level / 4, 0.8);
      }, { spacing: 0.6 });
    }
  }
  return true;
}

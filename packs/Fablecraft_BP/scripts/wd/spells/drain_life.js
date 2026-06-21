// Drain Life — Surround (evil). Heal the caster by sapping enemies' life. Charge
// = red motes draw inward to the hand; release/sustain = red life-threads stream
// from each non-ally into the caster, who pulses with absorbed vitality while
// victims briefly desaturate. Applies the -5 alignment deed (bridge writes it).
import { EntityDamageCause } from "@minecraft/server";
import { enemiesNear } from "./shared/targeting.js";
import { damageEnemy, healEntity } from "./shared/combat.js";
import { applyEffect } from "./shared/selfbuff.js";
import { drawBeam } from "./shared/beam.js";
import { tint, burst, dimensionSound } from "./shared/vfx.js";
import { changeAlignment } from "../alignment.js";

const RADIUS = [0, 3, 4, 4.5, 5];
const DRAIN = [0, 3, 5, 7, 8];
const HEAL_RATIO = [0, 0.5, 0.6, 0.7, 0.8];

function caster(player) {
  return { x: player.location.x, y: player.location.y + 1, z: player.location.z };
}

export function drainLifeCast(ctx) {
  const { player, level, spell } = ctx;
  const center = caster(player);
  const targets = enemiesNear(player, player.location, RADIUS[level]);

  burst(player.dimension, "wd:drain_mote", center, spell.color, 6 + level * 2, 0.8, 0.4, level / 4, 0.85);
  dimensionSound(player.dimension, "mob.wither.shoot", player.location, { volume: 0.4, pitch: 0.7 });

  let drained = 0;
  for (const entity of targets) {
    const from = { x: entity.location.x, y: entity.location.y + 1, z: entity.location.z };
    drawBeam(from, center, (point) => {
      tint(player.dimension, "wd:drain_thread", point, spell.color, 0.4 + level * 0.05, level / 4, 0.85);
    }, { spacing: 0.5, jitter: 0.2 });
    damageEnemy(player, entity, DRAIN[level], EntityDamageCause.magic);
    applyEffect(entity, "weakness", 30, 0);
    applyEffect(entity, "slowness", 30, 0);
    drained += DRAIN[level];
  }

  if (drained > 0) {
    healEntity(player, Math.round(drained * HEAL_RATIO[level]));
    burst(player.dimension, "wd:drain_mote", center, spell.color, 8, 0.6, 0.5, level / 4, 0.95);
  }
  // Evil deed — recorded through the legacy bridge so morality stays faithful.
  changeAlignment(player, -5, false);
  return true;
}

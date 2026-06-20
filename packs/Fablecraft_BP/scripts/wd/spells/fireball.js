// Will & Destiny Fireball. This module owns projectile simulation and impact.
import { EntityDamageCause, system } from "@minecraft/server";
import { WD_CONFIG } from "../config.js";
import { spawnParticle } from "../particles.js";
import { markSpellDamage } from "../stats.js";
import { setCasting } from "../visuals.js";

const ORANGE = { red: 1.0, green: 0.25, blue: 0.015, alpha: 1.0 };
const GOLD = { red: 1.0, green: 0.68, blue: 0.08, alpha: 0.82 };
const EMBER = { red: 1.0, green: 0.08, blue: 0.01, alpha: 0.9 };
const SMOKE = { red: 0.16, green: 0.07, blue: 0.045, alpha: 0.62 };

const DAMAGE = [0, 9, 13, 18, 24];
const SPLASH_DAMAGE = [0, 4, 6, 9, 12];
const RADIUS = [0, 2.5, 3.0, 3.5, 4.0];
const FIRE_SECONDS = [0, 3, 4, 5, 6];
const RANGE = [0, 18, 22, 26, 30];

function add(a, b, scale = 1) {
  return { x: a.x + b.x * scale, y: a.y + b.y * scale, z: a.z + b.z * scale };
}

function distanceSquared(a, b) {
  const dx = a.x - b.x;
  const dy = a.y - b.y;
  const dz = a.z - b.z;
  return dx * dx + dy * dy + dz * dz;
}

function isDamageable(entity, caster) {
  if (!entity?.isValid || entity.id === caster.id || entity.typeId === "minecraft:player") return false;
  try {
    if (!entity.getComponent("minecraft:health")) return false;
    if (entity.getComponent("minecraft:type_family")?.hasTypeFamily("fc_ally")) return false;
    return true;
  } catch {
    return false;
  }
}

// Script API 2.0.0 uses VectorXZ. The fallback supports older four-argument
// runtimes without using applyImpulse, which does not reliably move players.
function applyCompatibleKnockback(entity, x, z, strength, vertical) {
  const length = Math.max(0.001, Math.hypot(x, z));
  const nx = x / length;
  const nz = z / length;
  try {
    entity.applyKnockback({ x: nx * strength, z: nz * strength }, vertical);
    return;
  } catch {
    try {
      entity.applyKnockback(nx, nz, strength, vertical);
    } catch {
      // Damage and fire still apply when an entity rejects knockback.
    }
  }
}

function restoreScorch(block, originalPermutation) {
  try {
    if (block.typeId === "minecraft:black_concrete_powder") {
      block.setPermutation(originalPermutation);
    }
  } catch {
    // Chunks may unload before the temporary decoration expires.
  }
}

function applyTerrainFeedback(dimension, impact, level) {
  if (!WD_CONFIG.allowTerrainEffects) return;
  const radius = Math.min(2, Math.ceil(level / 2));
  const restored = new Set();

  for (let x = -radius; x <= radius; x++) {
    for (let z = -radius; z <= radius; z++) {
      if (x * x + z * z > radius * radius) continue;
      let ground;
      let above;
      try {
        ground = dimension.getBlock({
          x: Math.floor(impact.x) + x,
          y: Math.floor(impact.y) - 1,
          z: Math.floor(impact.z) + z,
        });
        above = dimension.getBlock({
          x: Math.floor(impact.x) + x,
          y: Math.floor(impact.y),
          z: Math.floor(impact.z) + z,
        });
      } catch {
        continue;
      }
      if (!ground || ground.isAir || ground.isLiquid) continue;

      try {
        const key = `${ground.location.x}|${ground.location.y}|${ground.location.z}`;
        if (!restored.has(key)) {
          restored.add(key);
          const original = ground.permutation;
          ground.setType("minecraft:black_concrete_powder");
          system.runTimeout(() => restoreScorch(ground, original), 80 + level * 20);
        }
        if (above?.isAir && Math.random() < 0.45) {
          above.setType("minecraft:fire");
          system.runTimeout(() => {
            try {
              if (above.typeId === "minecraft:fire") above.setType("minecraft:air");
            } catch {
              // Best-effort restoration only.
            }
          }, 40 + level * 10);
        }
      } catch {
        // Protected or unloaded blocks are ignored.
      }
    }
  }
}

function impact(caster, location, level, directTarget) {
  const dimension = caster.dimension;
  spawnParticle(dimension, "wd:fireball_core", location, ORANGE, 1.15 + level * 0.12, level / 4);
  spawnParticle(dimension, "wd:fireball_glow", location, GOLD, 1.8 + level * 0.18, level / 4);
  spawnParticle(dimension, "wd:fireball_impact_smoke", location, SMOKE, 0.8 + level * 0.1, level / 4);
  try {
    dimension.playSound("random.explode", location, { volume: 0.75, pitch: 1.05 - level * 0.05 });
  } catch {
    // Sound availability varies slightly by runtime.
  }
  try {
    caster.runCommand(`camerashake add @s ${0.08 + level * 0.035} 0.22 positional`);
  } catch {
    // Camera shake is feedback only and may be disabled by player settings.
  }

  let targets = [];
  try {
    targets = dimension.getEntities({ location, maxDistance: RADIUS[level] })
      .filter((entity) => isDamageable(entity, caster));
  } catch {
    targets = [];
  }
  for (const entity of targets) {
    const direct = directTarget && entity.id === directTarget.id;
    try {
      markSpellDamage(caster);
      entity.applyDamage(direct ? DAMAGE[level] : SPLASH_DAMAGE[level], {
        cause: EntityDamageCause.fire,
        damagingEntity: caster,
      });
      entity.setOnFire(direct ? FIRE_SECONDS[level] : Math.max(2, FIRE_SECONDS[level] - 1), true);
      applyCompatibleKnockback(
        entity,
        entity.location.x - location.x,
        entity.location.z - location.z,
        0.8 + level * 0.25,
        0.18 + level * 0.04,
      );
    } catch {
      // One invalid target must not suppress the rest of the splash.
    }
  }
  applyTerrainFeedback(dimension, location, level);
}

function launchProjectile(caster, level) {
  if (!caster.isValid) return;
  const dimension = caster.dimension;
  const direction = caster.getViewDirection();
  let location = add(caster.getHeadLocation(), direction, 0.9);
  const stepLength = 1.15;
  const maxSteps = Math.ceil(RANGE[level] / stepLength);
  let step = 0;

  const advance = () => {
    if (!caster.isValid || caster.dimension.id !== dimension.id) return;
    if (step++ >= maxSteps) {
      impact(caster, location, level);
      return;
    }
    const next = add(location, direction, stepLength);
    let block;
    let hitEntity;
    try {
      block = dimension.getBlock({
        x: Math.floor(next.x),
        y: Math.floor(next.y),
        z: Math.floor(next.z),
      });
      hitEntity = dimension.getEntities({ location: next, maxDistance: 1.15 })
        .filter((entity) => isDamageable(entity, caster))
        .sort((a, b) => distanceSquared(a.location, next) - distanceSquared(b.location, next))[0];
    } catch {
      impact(caster, location, level);
      return;
    }

    spawnParticle(dimension, "wd:fireball_core", next, ORANGE, 0.38 + level * 0.055, level / 4);
    spawnParticle(dimension, "wd:fireball_glow", next, GOLD, 0.7 + level * 0.08, level / 4);
    spawnParticle(dimension, "wd:fireball_ember", location, EMBER, 0.16 + level * 0.02, level / 4);

    if (hitEntity || (block && !block.isAir && !block.isLiquid)) {
      impact(caster, next, level, hitEntity);
      return;
    }
    location = next;
    system.run(advance);
  };
  advance();
}

export const FIREBALL_SPELL = Object.freeze({
  id: "fireball",
  name: "Fireball",
  family: "Attack",
  alignmentLock: "none",
  manaCost: (level) => [0, 18, 24, 31, 40][level],
  cooldownTicks: (level) => [0, 50, 46, 42, 36][level],
  cast(caster, level) {
    setCasting(caster, "fireball", level, 14);
    try {
      caster.playAnimation("animation.player.wd.fireball_cast", { blendOutTime: 0.2 });
      caster.playSound("fc.spell_cast", { volume: 0.9, pitch: 0.9 + level * 0.04 });
    } catch {
      // Animation/sound are additive; projectile gameplay remains authoritative.
    }

    const direction = caster.getViewDirection();
    for (let i = 0; i < 3; i++) {
      system.runTimeout(() => {
        if (!caster.isValid) return;
        const hand = add(caster.getHeadLocation(), direction, 0.65 + i * 0.08);
        hand.y -= 0.45;
        spawnParticle(caster.dimension, "wd:fireball_core", hand, ORANGE, 0.22 + i * 0.05, level / 4);
        spawnParticle(caster.dimension, "wd:fireball_glow", hand, GOLD, 0.46 + i * 0.08, level / 4);
      }, i * 2);
    }
    system.runTimeout(() => {
      try {
        caster.playSound("mob.blaze.shoot", { volume: 0.8, pitch: 1.05 });
      } catch {
        // The cast still proceeds if the cue is unavailable.
      }
      launchProjectile(caster, level);
    }, 6);
    return true;
  },
});

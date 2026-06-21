// Will & Destiny combat helpers. Damage is always attributed to the caster and
// marks the spell-damage tick so kill XP is credited to the Will discipline.
import { EntityDamageCause } from "@minecraft/server";
import { markSpellDamage } from "../../stats.js";

export function damageEnemy(caster, entity, amount, cause = EntityDamageCause.magic) {
  try {
    markSpellDamage(caster);
    entity.applyDamage(Math.max(0, amount), { cause, damagingEntity: caster });
    return true;
  } catch {
    return false;
  }
}

export function igniteEnemy(entity, seconds) {
  try {
    entity.setOnFire(Math.max(1, Math.floor(seconds)), true);
  } catch {
    // Ignition is secondary to the direct damage.
  }
}

export function healEntity(entity, amount) {
  try {
    const hp = entity.getComponent("minecraft:health");
    if (!hp) return;
    hp.setCurrentValue(Math.min(hp.effectiveMax, hp.currentValue + Math.max(0, amount)));
  } catch {
    // Healing is best-effort.
  }
}

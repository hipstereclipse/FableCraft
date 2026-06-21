// Will & Destiny area effects. Self-centered ring / radius application over
// valid enemies (players + allies excluded by targeting.js).
import { enemiesNear } from "./targeting.js";

// Apply perTarget() to every enemy within radius of a point. Returns the count.
export function applyRadius(caster, location, radius, perTarget) {
  const targets = enemiesNear(caster, location, radius);
  let hit = 0;
  for (const entity of targets) {
    try {
      perTarget(entity);
      hit++;
    } catch {
      // One invalid target must not suppress the rest of the area effect.
    }
  }
  return hit;
}

// Apply around the caster's feet (Enflame, Force Push, Drain Life, Slow Time).
export function applyAroundCaster(caster, radius, perTarget) {
  return applyRadius(caster, caster.location, radius, perTarget);
}

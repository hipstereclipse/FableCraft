// Will & Destiny knockback. Pinned to the 2.0.0 VectorXZ signature with a
// four-argument fallback. Never uses applyImpulse, which does not reliably move
// players; players are excluded from Will-power forces upstream in targeting.js.

export function applyHorizontalKnockback(entity, dirX, dirZ, strength, vertical) {
  const length = Math.max(0.001, Math.hypot(dirX, dirZ));
  const nx = dirX / length;
  const nz = dirZ / length;
  try {
    entity.applyKnockback({ x: nx * strength, z: nz * strength }, vertical);
    return;
  } catch {
    try {
      entity.applyKnockback(nx, nz, strength, vertical);
    } catch {
      // Damage and other effects still apply when an entity rejects knockback.
    }
  }
}

// Knock an entity away from an origin point (used by AoE blasts).
export function knockbackFrom(entity, origin, strength, vertical) {
  applyHorizontalKnockback(
    entity,
    entity.location.x - origin.x,
    entity.location.z - origin.z,
    strength,
    vertical,
  );
}

// Knock an entity along a direction vector (used by directional pushes/charges).
export function knockbackAlong(entity, direction, strength, vertical) {
  applyHorizontalKnockback(entity, direction.x, direction.z, strength, vertical);
}

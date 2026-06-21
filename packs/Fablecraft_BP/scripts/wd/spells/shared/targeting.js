// Will & Destiny targeting. Centralizes entity scans and the friendly-fire rule:
// players and the fc_ally family are never valid Will-power targets.

export function add(a, b, scale = 1) {
  return { x: a.x + b.x * scale, y: a.y + b.y * scale, z: a.z + b.z * scale };
}

export function sub(a, b) {
  return { x: a.x - b.x, y: a.y - b.y, z: a.z - b.z };
}

export function scale(a, s) {
  return { x: a.x * s, y: a.y * s, z: a.z * s };
}

export function lengthOf(a) {
  return Math.hypot(a.x, a.y, a.z);
}

export function normalize(a) {
  const len = Math.max(0.0001, lengthOf(a));
  return { x: a.x / len, y: a.y / len, z: a.z / len };
}

export function distanceSquared(a, b) {
  const dx = a.x - b.x;
  const dy = a.y - b.y;
  const dz = a.z - b.z;
  return dx * dx + dy * dy + dz * dz;
}

export function headLocation(entity) {
  try {
    return entity.getHeadLocation();
  } catch {
    return { x: entity.location.x, y: entity.location.y + 1.6, z: entity.location.z };
  }
}

export function viewDirection(entity) {
  try {
    return entity.getViewDirection();
  } catch {
    return { x: 0, y: 0, z: 1 };
  }
}

function hasFamily(entity, family) {
  try {
    return entity.getComponent("minecraft:type_family")?.hasTypeFamily(family) === true;
  } catch {
    return false;
  }
}

// Entities turned by Turncoat (allegiance.js). A runtime type_family cannot be
// added to an existing entity, so a charmed enemy is registered here instead and
// the friendly-fire gate below treats it exactly like the fc_ally family.
const charmedIds = new Set();

export function setCharmed(entityId, on) {
  if (on) charmedIds.add(entityId);
  else charmedIds.delete(entityId);
}

export function isCharmed(entityId) {
  return charmedIds.has(entityId);
}

// A valid Will-power target: alive, damageable, not the caster, not a player,
// not an ally, and not a charmed minion. This is the single friendly-fire gate.
export function isEnemy(entity, caster) {
  if (!entity?.isValid || (caster && entity.id === caster.id)) return false;
  if (entity.typeId === "minecraft:player") return false;
  try {
    if (!entity.getComponent("minecraft:health")) return false;
    if (hasFamily(entity, "fc_ally")) return false;
    if (charmedIds.has(entity.id)) return false;
    return true;
  } catch {
    return false;
  }
}

export function enemiesNear(caster, location, radius) {
  try {
    return caster.dimension
      .getEntities({ location, maxDistance: radius })
      .filter((entity) => isEnemy(entity, caster));
  } catch {
    return [];
  }
}

export function nearestEnemy(caster, location, radius) {
  return enemiesNear(caster, location, radius)
    .sort((a, b) => distanceSquared(a.location, location) - distanceSquared(b.location, location))[0];
}

// The enemy under the caster's crosshair, if any, within maxDistance.
export function lookedAtEnemy(caster, maxDistance) {
  try {
    const hits = caster.getEntitiesFromViewDirection({ maxDistance });
    for (const hit of hits) {
      if (isEnemy(hit.entity, caster)) return hit.entity;
    }
  } catch {
    // Fall back to a forward scan below.
  }
  const forward = add(headLocation(caster), viewDirection(caster), maxDistance * 0.5);
  return nearestEnemy(caster, forward, maxDistance * 0.6);
}

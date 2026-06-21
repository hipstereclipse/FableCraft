// Will & Destiny projectile. A stepping projectile generalized from Fireball:
// advances ~1.15 blocks per tick, calls onStep for trail VFX, and onImpact on
// hitting a solid block, a valid enemy, or reaching max range.
import { system } from "@minecraft/server";
import { add, distanceSquared, headLocation, isEnemy, viewDirection } from "./targeting.js";

export function fireProjectile(caster, options) {
  const {
    range = 20,
    stepLength = 1.15,
    startForward = 0.9,
    onStep,
    onImpact,
  } = options;
  if (!caster.isValid) return;

  const dimension = caster.dimension;
  const direction = options.direction ?? viewDirection(caster);
  let location = add(headLocation(caster), direction, startForward);
  const maxSteps = Math.max(1, Math.ceil(range / stepLength));
  let step = 0;

  const finish = (loc, hitEntity) => {
    try {
      onImpact?.(loc, hitEntity);
    } catch {
      // Impact handlers are best-effort.
    }
  };

  const advance = () => {
    if (!caster.isValid || caster.dimension.id !== dimension.id) {
      finish(location, undefined);
      return;
    }
    if (step++ >= maxSteps) {
      finish(location, undefined);
      return;
    }
    const next = add(location, direction, stepLength);
    let block;
    let hitEntity;
    try {
      block = dimension.getBlock({ x: Math.floor(next.x), y: Math.floor(next.y), z: Math.floor(next.z) });
      hitEntity = dimension
        .getEntities({ location: next, maxDistance: stepLength })
        .filter((entity) => isEnemy(entity, caster))
        .sort((a, b) => distanceSquared(a.location, next) - distanceSquared(b.location, next))[0];
    } catch {
      finish(location, undefined);
      return;
    }

    try {
      onStep?.(next, step);
    } catch {
      // Trail VFX is cosmetic.
    }

    if (hitEntity || (block && !block.isAir && !block.isLiquid)) {
      finish(next, hitEntity);
      return;
    }
    location = next;
    system.run(advance);
  };
  advance();
}

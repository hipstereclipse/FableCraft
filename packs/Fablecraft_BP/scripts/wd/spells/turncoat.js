// Turncoat — Surround (evil). Manipulates a nearby enemy's mind, gradually
// turning it into an ally while the caster maintains the link. Evil-only lock +
// cost/cooldown are enforced by the cast gate; this body finds a target, opens a
// violet tendril, and fills a conversion meter — handing off to allegiance.js to
// flip sides once the channel completes. Aborts cleanly if the link is broken.
import { system } from "@minecraft/server";
import { headLocation, lookedAtEnemy, distanceSquared } from "./shared/targeting.js";
import { drawBeam } from "./shared/beam.js";
import { tint, burst } from "./shared/vfx.js";
import { WD_CONFIG } from "../config.js";
import { canCharm, convert } from "../allegiance.js";

const RANGE = [0, 12, 13, 14, 14];
const STEP_TICKS = 4;

export function turncoatCast(ctx) {
  const { player, level, spell } = ctx;
  const reach = RANGE[level];
  const target = lookedAtEnemy(player, reach);
  if (!target) {
    try { player.onScreenDisplay.setActionBar("§9No mind to bend."); } catch { /* feedback */ }
    return false; // no target -> the cast gate refunds the Will
  }
  if (!canCharm(target)) {
    try { player.onScreenDisplay.setActionBar("§9That will cannot be bent."); } catch { /* feedback */ }
    return false;
  }

  // Higher charge converts faster. Conversion runs as a short channel; if the
  // caster strays out of range or the target dies, the attempt simply lapses.
  const needed = Math.max(20, Math.round((WD_CONFIG.turncoatConvertTicks ?? 60) - (level - 1) * 10));
  let progress = 0;

  const channel = () => {
    if (!player.isValid || !target.isValid) return;
    const hand = { x: headLocation(player).x, y: headLocation(player).y - 0.2, z: headLocation(player).z };
    const head = { x: target.location.x, y: target.location.y + 1.2, z: target.location.z };
    if (distanceSquared(player.location, target.location) > (reach + 2) ** 2) {
      try { player.onScreenDisplay.setActionBar("§9The link is broken."); } catch { /* feedback */ }
      return;
    }
    // Violet tendril/beam between caster and target; charm motes swirl up.
    drawBeam(hand, head, (point) => tint(player.dimension, "wd:charm_tendril", point, spell.color, 0.5, level / 4, 0.9),
      { spacing: 0.5, jitter: 0.25 });
    burst(target.dimension, "wd:charm_mote", head, spell.color, 3, 0.6, 0.4, level / 4, 0.85);

    progress += STEP_TICKS;
    const pct = Math.min(100, Math.round((progress / needed) * 100));
    try { player.onScreenDisplay.setActionBar(`§dBending will… §f${pct}%`); } catch { /* feedback */ }

    if (progress >= needed) {
      convert(player, target, level);
      return;
    }
    system.runTimeout(channel, STEP_TICKS);
  };
  channel();
  return true;
}

// Multi Arrow — Physical. The Hero's next bow volleys split into a fan of arrows;
// light motes swirl to show the shots remaining. Arms a window in combat_hooks.js
// (the actual splitting happens on the player's next shots).
import { burst } from "./shared/vfx.js";
import { armMultiArrow } from "../combat_hooks.js";

const SHOTS = [0, 2, 3, 4, 5]; // empowered shots per cast
const FAN = [0, 2, 2, 3, 3];   // extra arrows added to each shot
const WINDOW_TICKS = 200;       // ~10 s to loose the volley

export function multiArrowCast(ctx) {
  const { player, level, spell } = ctx;
  armMultiArrow(player, SHOTS[level], FAN[level], WINDOW_TICKS);

  // Orbiting light motes — one swirl per remaining shot.
  burst(player.dimension, "wd:multi_mote",
    { x: player.location.x, y: player.location.y + 1.2, z: player.location.z }, spell.color, 6 + SHOTS[level] * 2, 0.9, 0.5, level / 4, 0.9);
  try {
    player.playSound("random.orb", { volume: 0.6, pitch: 1.4 });
    player.onScreenDisplay.setActionBar(`§a✦ Your next ${SHOTS[level]} volleys split.`);
  } catch {
    // Feedback is additive.
  }
  return true;
}

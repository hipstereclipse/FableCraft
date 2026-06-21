// Multi Strike — Attack. Imbues the blade to strike several times in one blow.
// Arms a melee window in combat_hooks.js and wreathes the weapon in golden
// energy; a brief haste buff sells the impossible speed.
import { applyEffect } from "./shared/selfbuff.js";
import { burst } from "./shared/vfx.js";
import { armMultiStrike } from "../combat_hooks.js";

const BLOWS = [0, 2, 3, 4, 5]; // empowered melee blows per cast
const BONUS = [0, 3, 4, 5, 6]; // extra damage per ghosted hit
const WINDOW_TICKS = 200;

export function multiStrikeCast(ctx) {
  const { player, level, spell } = ctx;
  armMultiStrike(player, BLOWS[level], BONUS[level], WINDOW_TICKS);
  applyEffect(player, "haste", (5 + level * 2) * 20, 2 + level);

  burst(player.dimension, "wd:blade_arc",
    { x: player.location.x, y: player.location.y + 1.2, z: player.location.z }, spell.color, 8 + level * 2, 0.8, 0.6, level / 4, 0.95);
  try {
    player.playSound("item.trident.riptide_1", { volume: 0.6, pitch: 1.2 });
    player.onScreenDisplay.setActionBar("§6Your blade blurs with impossible speed!");
  } catch {
    // Feedback is additive.
  }
  return true;
}

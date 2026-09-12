// Ghost Sword — Physical. Conjures a floating spectral blade that fights at the
// Hero's side for a timer, hunting nearby foes, then dissipates. The blade is a
// script-simulated companion (wd/ghostblade.js) — no new entity, ally-safe via
// targeting.js. Casting again renews the blade and reseats it at the Hero.
import { headLocation } from "./shared/targeting.js";
import { burst, dimensionSound } from "./shared/vfx.js";
import { deployGhostSword } from "../ghostblade.js";

export function ghostSwordCast(ctx) {
  const { player, level, spell } = ctx;
  // A conjuring flourish at the Hero's hand, then the blade takes flight.
  burst(player.dimension, "wd:ghost_blade", headLocation(player), spell.color, 8 + level, 0.7, 0.6, level / 4, 0.9);
  dimensionSound(player.dimension, "item.trident.throw", player.location, { volume: 0.6, pitch: 1.4 });
  deployGhostSword(player, level, spell.color);
  return true;
}

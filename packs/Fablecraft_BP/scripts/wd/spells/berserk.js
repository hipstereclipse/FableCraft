// Berserk — Physical (evil). A hulking frenzy that raises speed and strength.
// The body swells (the reactive morph reads gesture 15), a red rage aura with
// heat boils up, and the deed nudges the Hero further toward Skorm. The "dims
// reason" downside is modelled as a controlled tradeoff (no player-harming
// effect) per the spec.
import { applyEffect } from "./shared/selfbuff.js";
import { burst, cameraShake, dimensionSound } from "./shared/vfx.js";
import { changeAlignment } from "../alignment.js";

const SECONDS = [0, 10, 14, 18, 22];

export function berserkCast(ctx) {
  const { player, level, spell } = ctx;
  const ticks = SECONDS[level] * 20;
  applyEffect(player, "strength", ticks, 1 + Math.floor(level / 2), true);
  applyEffect(player, "speed", ticks, 1);
  applyEffect(player, "resistance", ticks, 0);

  burst(player.dimension, "wd:rage_heat",
    { x: player.location.x, y: player.location.y + 1, z: player.location.z }, spell.color, 12 + level * 2, 1.0, 0.8, 1, 0.9);
  dimensionSound(player.dimension, "mob.ravager.roar", player.location, { volume: 0.6, pitch: 1.2 });
  cameraShake(player, 0.08 + level * 0.02, 0.4);

  // Evil deed — keeps the Hero on the dark side the lock requires (faithful to
  // the legacy berserk's morality cost).
  changeAlignment(player, -3, false);
  return true;
}

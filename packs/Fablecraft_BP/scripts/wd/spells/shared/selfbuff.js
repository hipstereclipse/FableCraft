// Will & Destiny self-buffs. Timed self-states (shield, slow-time immunity,
// rush/charge speed, berserk) plus the shield-active client flag.

export function applyEffect(entity, effectId, durationTicks, amplifier = 0, showParticles = false) {
  try {
    entity.addEffect(effectId, Math.max(1, Math.floor(durationTicks)), {
      amplifier: Math.max(0, Math.floor(amplifier)),
      showParticles,
    });
  } catch {
    // An unavailable effect must not abort the rest of the cast.
  }
}

export function setShieldActive(player, active) {
  try {
    if (player.getProperty("wd:shield_active") !== active) {
      player.setProperty("wd:shield_active", active === true);
    }
  } catch {
    // The shield still functions in script even if the client flag fails.
  }
}

export function isShieldActive(player) {
  try {
    return player.getProperty("wd:shield_active") === true;
  } catch {
    return false;
  }
}

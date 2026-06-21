// Will & Destiny VFX dispatch. Converts a spell's [r,g,b] tint into the
// particle color map and wraps the cosmetic-safe spawn/sound/shake helpers so
// each spell composes charge/release/impact/sustain stages from one toolkit.
import { spawnParticle } from "../../particles.js";

// Spell colors are authored as 0..255 triples (mirrors fc_data SPELLS color).
export function rgba(color, alpha = 1) {
  return {
    red: (color?.[0] ?? 255) / 255,
    green: (color?.[1] ?? 255) / 255,
    blue: (color?.[2] ?? 255) / 255,
    alpha,
  };
}

export function tint(dimension, identifier, location, color, size = 1, intensity = 1, alpha = 1) {
  spawnParticle(dimension, identifier, location, rgba(color, alpha), size, intensity);
}

// Scatter several emitters of one particle in a small jittered cloud.
export function burst(dimension, identifier, center, color, count, spread, size = 1, intensity = 1, alpha = 1) {
  const n = Math.max(1, Math.min(24, Math.floor(count)));
  for (let i = 0; i < n; i++) {
    const loc = {
      x: center.x + (Math.random() - 0.5) * spread,
      y: center.y + (Math.random() - 0.5) * spread,
      z: center.z + (Math.random() - 0.5) * spread,
    };
    tint(dimension, identifier, loc, color, size, intensity, alpha);
  }
}

// A ground-hugging ring of emitters (Enflame, Force Push dust, Divine pillars).
export function ring(dimension, center, radius, segments, emit) {
  const count = Math.max(4, Math.min(48, Math.floor(segments)));
  for (let i = 0; i < count; i++) {
    const angle = (i / count) * Math.PI * 2;
    emit({ x: center.x + Math.cos(angle) * radius, y: center.y, z: center.z + Math.sin(angle) * radius }, angle, i);
  }
}

export function sound(source, identifier, options) {
  try {
    source.playSound(identifier, options);
  } catch {
    // Audio is additive; gameplay never depends on a sound being available.
  }
}

export function dimensionSound(dimension, identifier, location, options) {
  try {
    dimension.playSound(identifier, location, options);
  } catch {
    // Audio is additive.
  }
}

export function cameraShake(player, intensity, seconds) {
  try {
    player.runCommand(`camerashake add @s ${intensity.toFixed(3)} ${seconds.toFixed(2)} positional`);
  } catch {
    // Camera shake is feedback only and may be disabled by player settings.
  }
}

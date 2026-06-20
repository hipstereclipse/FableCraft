// Will & Destiny ambient auras. This module owns bounded, throttled emission.
import { world } from "@minecraft/server";
import { WD_CONFIG } from "./config.js";
import { alignmentTier } from "./alignment.js";
import { bridgeLegacyProgression } from "./state.js";
import { spawnParticle } from "./particles.js";

const EVIL_RED = { red: 0.34, green: 0.015, blue: 0.025, alpha: 0.48 };
const DIVINE_GOLD = { red: 1.0, green: 0.72, blue: 0.18, alpha: 0.66 };

export function emitAlignmentAuras() {
  for (const player of world.getPlayers()) {
    const state = bridgeLegacyProgression(player);
    const tier = alignmentTier(state.alignment);
    const density = Math.max(0, Math.min(2, state.options.auraDensity * WD_CONFIG.auraDensity));
    if (tier === 0 || density <= 0) continue;
    const emitters = Math.min(
      WD_CONFIG.maxAuraEmittersPerPlayer,
      Math.max(1, Math.ceil((Math.abs(tier) / 2) * density)),
    );
    for (let i = 0; i < emitters; i++) {
      const magnitude = Math.abs(tier);
      const radius = 0.3 + magnitude * 0.08;
      if (tier > 0) {
        spawnParticle(
          player.dimension,
          "wd:divine_glow",
          {
            x: player.location.x + (Math.random() - 0.5) * radius,
            y: player.location.y + 0.25 + Math.random() * 1.65,
            z: player.location.z + (Math.random() - 0.5) * radius,
          },
          DIVINE_GOLD,
          0.24 + magnitude * 0.055,
          magnitude / 6,
        );
        continue;
      }
      spawnParticle(
        player.dimension,
        "wd:evil_fog",
        {
          x: player.location.x + (Math.random() - 0.5) * radius,
          y: player.location.y + 0.08 + Math.random() * 0.6,
          z: player.location.z + (Math.random() - 0.5) * radius,
        },
        EVIL_RED,
        0.45 + magnitude * 0.08,
        magnitude / 6,
      );
    }
  }
}

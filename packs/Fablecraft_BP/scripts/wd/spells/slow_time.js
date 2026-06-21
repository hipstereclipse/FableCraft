// Slow Time — Surround. Slows everything around the Hero to a crawl while the
// caster is immune; higher levels approach a standstill. Implemented as a per-
// entity heavy slowness on non-ally, non-player entities inside the radius — it
// never alters the world tick rate, so multiplayer stays fair. The caster is
// excluded and moves normally.
import { system } from "@minecraft/server";
import { enemiesNear } from "./shared/targeting.js";
import { applyEffect } from "./shared/selfbuff.js";
import { tint, ring, dimensionSound } from "./shared/vfx.js";

const RADIUS = [0, 6, 8, 10, 12];
const DURATION = [0, 80, 120, 140, 160];
const POTENCY = [0, 4, 5, 6, 6];

export function slowTimeCast(ctx) {
  const { player, level, spell } = ctx;
  const radius = RADIUS[level];
  const endTick = system.currentTick + DURATION[level];

  dimensionSound(player.dimension, "beacon.deactivate", player.location, { volume: 0.6, pitch: 0.5 });

  const pulse = () => {
    if (!player.isValid) return;
    const center = { x: player.location.x, y: player.location.y + 0.5, z: player.location.z };
    // Expanding translucent bubble + drifting clock glyphs.
    ring(player.dimension, center, radius * 0.92, 18, (loc) => {
      tint(player.dimension, "wd:slowtime_bubble", loc, spell.color, 0.7, level / 4, 0.3);
    });
    for (let i = 0; i < 4; i++) {
      const loc = { x: center.x + (Math.random() - 0.5) * radius, y: center.y + Math.random() * 2, z: center.z + (Math.random() - 0.5) * radius };
      tint(player.dimension, "wd:slowtime_glyph", loc, spell.color, 0.5, level / 4, 0.5);
    }
    // Heavy slowness on enemies inside the field (players/allies excluded).
    for (const entity of enemiesNear(player, player.location, radius)) {
      applyEffect(entity, "slowness", 16, POTENCY[level]);
      applyEffect(entity, "weakness", 16, 1);
    }
    if (system.currentTick < endTick) system.runTimeout(pulse, 8);
  };
  pulse();
  return true;
}

// Will & Destiny beams. Lays a capped line of particle emitters between two
// points for arcs/beams (Lightning, Turncoat tether, Divine pillars). The
// emitter count is bounded per call so large casts cannot spike the tick.
import { sub, lengthOf } from "./targeting.js";

const MAX_SEGMENTS = 28;

export function drawBeam(from, to, emit, options = {}) {
  const { spacing = 0.6, jitter = 0 } = options;
  const delta = sub(to, from);
  const distance = lengthOf(delta);
  const segments = Math.max(1, Math.min(MAX_SEGMENTS, Math.round(distance / spacing)));
  for (let i = 0; i <= segments; i++) {
    const t = i / segments;
    const point = {
      x: from.x + delta.x * t + (jitter ? (Math.random() - 0.5) * jitter : 0),
      y: from.y + delta.y * t + (jitter ? (Math.random() - 0.5) * jitter : 0),
      z: from.z + delta.z * t + (jitter ? (Math.random() - 0.5) * jitter : 0),
    };
    try {
      emit(point, t, i);
    } catch {
      // A single emitter failure must not break the beam.
    }
  }
}

// A vertical column of emitters descending onto a point (Divine Fury pillars).
export function drawColumn(base, height, emit, options = {}) {
  const top = { x: base.x, y: base.y + height, z: base.z };
  drawBeam(top, base, emit, options);
}

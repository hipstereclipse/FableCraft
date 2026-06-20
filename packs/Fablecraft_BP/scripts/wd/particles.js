// Will & Destiny particle helpers. This module owns Molang-driven spawn calls.
import { MolangVariableMap } from "@minecraft/server";

export function particleVariables(color, size = 1, intensity = 1) {
  const molang = new MolangVariableMap();
  molang.setColorRGBA("variable.color", {
    red: color.red,
    green: color.green,
    blue: color.blue,
    alpha: color.alpha ?? 1,
  });
  molang.setFloat("variable.size", size);
  molang.setFloat("variable.intensity", intensity);
  return molang;
}

export function spawnParticle(dimension, identifier, location, color, size = 1, intensity = 1) {
  try {
    dimension.spawnParticle(identifier, location, particleVariables(color, size, intensity));
  } catch {
    // Particle failures are cosmetic and must never interrupt spell effects.
  }
}

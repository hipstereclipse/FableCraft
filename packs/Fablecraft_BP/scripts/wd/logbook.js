// Will & Destiny Logbook (Phase 3, spec §3.5). The narrated chronicle of the
// playthrough: kills by creature, notable deeds, a discovered bestiary, and a
// short "story so far" assembled from the v3 logbook counters. Counting is
// independent of the progression bridge — the chronicle populates whether or not
// the legacy handlers are authoritative.
import { world } from "@minecraft/server";
import { getState, mutateState } from "./state.js";

function cleanName(typeId) {
  return String(typeId).replace(/^minecraft:/, "").replace(/^fc:/, "").replace(/_/g, " ");
}

export function recordKill(player, deadTypeId) {
  const name = cleanName(deadTypeId);
  mutateState(player, (s) => {
    s.logbook.kills[name] = (s.logbook.kills[name] ?? 0) + 1;
    if (!s.logbook.discovered.includes(name)) s.logbook.discovered.push(name);
  });
}

export function recordDeed(player, deedId, amount = 1) {
  mutateState(player, (s) => {
    s.logbook.deeds[deedId] = (s.logbook.deeds[deedId] ?? 0) + amount;
  });
}

function epithet(alignment) {
  if (alignment >= 500) return "a beacon of Avo";
  if (alignment >= 150) return "a Hero of good name";
  if (alignment > -150) return "a Hero of uncertain heart";
  if (alignment > -500) return "a Hero the towns mistrust";
  return "a shadow over Albion";
}

// Returns { lines, totalKills, discovered } for the storybook Logbook page.
export function chronicle(player) {
  const s = getState(player);
  const kills = s.logbook.kills;
  const entries = Object.entries(kills).sort((a, b) => b[1] - a[1]);
  const totalKills = entries.reduce((sum, [, n]) => sum + n, 0);

  const lines = [];
  lines.push(`§8“The story so far…”`);
  lines.push(`§7You are §f${epithet(s.alignment)}§7, ${totalKills} battles deep.`);
  lines.push(`§7Creatures known: §f${s.logbook.discovered.length}`);
  if (entries.length) {
    lines.push("");
    lines.push("§6Bestiary — most felled:");
    for (const [name, n] of entries.slice(0, 8)) lines.push(`§7• §f${name} §8×${n}`);
  }
  const deeds = Object.entries(s.logbook.deeds);
  if (deeds.length) {
    lines.push("");
    lines.push("§6Notable deeds:");
    for (const [id, n] of deeds.slice(0, 6)) lines.push(`§7• §f${id} §8×${n}`);
  }
  if (entries.length === 0 && deeds.length === 0) {
    lines.push("");
    lines.push("§8Your chronicle is yet unwritten. Go forth and earn its pages.");
  }
  return { lines, totalKills, discovered: s.logbook.discovered.length };
}

// Record every player kill into the chronicle (independent of XP/alignment).
world.afterEvents.entityDie.subscribe((event) => {
  const killer = event.damageSource?.damagingEntity;
  const dead = event.deadEntity;
  if (!killer || killer.typeId !== "minecraft:player" || !dead || dead.typeId === "minecraft:player") return;
  try {
    recordKill(killer, dead.typeId);
  } catch {
    // The chronicle is flavour; a recording failure never affects gameplay.
  }
});

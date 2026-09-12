// Will & Destiny Logbook (Phase 3, spec §3.5). The narrated chronicle of the
// playthrough: kills by creature, notable deeds, a discovered bestiary, and a
// short "story so far" assembled from the v3 logbook counters. Counting is
// independent of the progression bridge — the chronicle populates whether or not
// the legacy handlers are authoritative.
import { world } from "@minecraft/server";
import { getState, mutateState } from "./state.js";
import { t, bestiaryName } from "../fc_strings.js";

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
  if (alignment >= 500) return t("chronicle.beacon");
  if (alignment >= 150) return t("chronicle.good");
  if (alignment > -150) return t("chronicle.neutral");
  if (alignment > -500) return t("chronicle.mistrusted");
  return t("chronicle.evil");
}

// Returns { lines, totalKills, discovered } for the storybook Logbook page.
export function chronicle(player) {
  const s = getState(player);
  const kills = s.logbook.kills;
  const entries = Object.entries(kills).sort((a, b) => b[1] - a[1]);
  const totalKills = entries.reduce((sum, [, n]) => sum + n, 0);

  const lines = [];
  lines.push(t("chronicle.heading"));
  lines.push(t("chronicle.story", { epithet: epithet(s.alignment), kills: totalKills }));
  lines.push(t("chronicle.discovered", { count: s.logbook.discovered.length }));
  if (entries.length) {
    lines.push("");
    lines.push(t("chronicle.bestiary"));
    for (const [name, n] of entries.slice(0, 8)) lines.push(t("chronicle.entry", { name: bestiaryName(name), count: n }));
  }
  const deeds = Object.entries(s.logbook.deeds);
  if (deeds.length) {
    lines.push("");
    lines.push(t("chronicle.deeds"));
    for (const [id, n] of deeds.slice(0, 6)) lines.push(t("chronicle.entry", { name: id, count: n }));
  }
  if (entries.length === 0 && deeds.length === 0) {
    lines.push("");
    lines.push(t("chronicle.empty"));
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

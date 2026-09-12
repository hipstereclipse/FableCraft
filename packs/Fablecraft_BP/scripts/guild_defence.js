// Guild defence owns only its temporary target tag and combat component group.
// Warrants, social reactions, relationships and resident identity stay with their owners.
export const GUILD_OFFENDER_TAG = "fc_guild_offender";
export const GUILD_DEFENDING_TAG = "fc_guild_defending";
const TYPES = new Set(["fc:guildmaster", "fc:maze", "fc:guild_apprentice_might",
  "fc:guild_apprentice_skill", "fc:guild_apprentice_will"]);
let boundController;

export function isGuildDefender(entity) {
  try { return TYPES.has(entity.typeId)
    || (entity.typeId === "fc:guard_bowerstone" && entity.hasTag("fc_guild_guard")); }
  catch { return false; }
}
export function bindGuildDefence(controller) { boundController = controller; }
export function provokeGuildDefence(entity, player, ticks = 320) {
  if (!player || !isGuildDefender(entity) || !boundController) return false;
  boundController.provoke(player, [entity], ticks);
  return true;
}

export function createGuildDefenceController({ now, players, defenders, inGuild, hasWarrant, interruptTraining }) {
  const records = new Map(), provocations = new Map();
  const usable = e => { try { return !!e && e.isValid !== false; } catch { return false; } };
  const close = (a, b) => {
    try { return a.dimension.id === b.dimension.id && Math.hypot(a.location.x - b.location.x,
      a.location.y - b.location.y, a.location.z - b.location.z) <= 80; } catch { return false; }
  };
  const onCampus = e => { try { return inGuild(e.location, e.dimension.id); } catch { return false; } };

  function remember(entity) {
    let record = records.get(entity.id);
    if (!record) {
      // Reconcile persisted combat from an earlier session, including the old
      // unowned attack group, without emitting a social-neutral event.
      record = { entity, active: false, dirty: true };
      records.set(entity.id, record);
    } else record.entity = entity;
    return record;
  }
  function stop(record) {
    try {
      record.entity.triggerEvent("fc:guild_defence_stop");
      record.entity.removeTag(GUILD_DEFENDING_TAG);
      record.entity.removeTag("fc_aggravated");
      record.entity.setDynamicProperty("fc_aggro_until", undefined);
      record.active = false; record.dirty = false;
      return true;
    } catch { record.dirty = true; return false; }
  }
  function reconcile() {
    const heroes = players().filter(usable);
    const online = new Set(heroes.map(p => p.id));
    for (const [id, entries] of provocations) {
      if (!online.has(id)) { provocations.delete(id); continue; }
      for (const [npcId, until] of entries) if (now() >= until) entries.delete(npcId);
      if (!entries.size) provocations.delete(id);
    }
    for (const entity of defenders()) if (usable(entity) && isGuildDefender(entity)) remember(entity);
    for (const [id, record] of records) if (!usable(record.entity)) records.delete(id);
    const wanted = new Set(), provoked = new Map();
    let tagsReady = true;
    for (const p of heroes) {
      const warrant = onCampus(p) && hasWarrant(p);
      if (warrant) wanted.add(p.id);
      const targets = new Set();
      for (const npcId of provocations.get(p.id)?.keys() ?? []) {
        const entity = records.get(npcId)?.entity;
        if (entity && close(p, entity)) targets.add(npcId);
      }
      provoked.set(p.id, targets);
      try {
        if (warrant || targets.size) p.addTag(GUILD_OFFENDER_TAG);
        else p.removeTag(GUILD_OFFENDER_TAG);
      } catch { tagsReady = false; }
    }
    for (const record of records.values()) {
      const needed = tagsReady && heroes.some(p => (wanted.has(p.id) && onCampus(record.entity))
        || provoked.get(p.id)?.has(record.entity.id));
      if (record.dirty && !stop(record)) continue;
      if (!needed) {
        if (record.active) stop(record);
        continue;
      }
      if (record.active) continue;
      try {
        interruptTraining(record.entity);
        record.entity.addTag(GUILD_DEFENDING_TAG);
        record.entity.triggerEvent("fc:guild_defence_start");
        record.active = true;
      } catch { record.dirty = true; }
    }
  }
  function provoke(player, entities, ticks = 320) {
    if (!usable(player)) return;
    const entries = provocations.get(player.id) ?? new Map();
    for (const entity of entities) if (usable(entity) && isGuildDefender(entity)) {
      remember(entity);
      entries.set(entity.id, now() + Math.max(1, Math.min(320, ticks)));
    }
    if (entries.size) provocations.set(player.id, entries);
    reconcile();
  }
  function forgive(player) { provocations.delete(player.id); }
  return { reconcile, provoke, forgive };
}

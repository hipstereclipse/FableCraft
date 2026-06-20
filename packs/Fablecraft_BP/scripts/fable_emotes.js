import {
  CommandPermissionLevel,
  CustomCommandParamType,
  CustomCommandStatus,
  system,
  world,
} from "@minecraft/server";
import { FABLE_EMOTES, FABLE_EMOTE_BY_ID } from "./fable_emote_registry.js";

const CAMERA_TICKS = 40;
const SOCIAL_RANGE = 12;
const AXES = {
  love: "fc:love_hate",
  fear: "fc:fear_funny",
  looks: "fc:ugly_attractive",
};
const REACTION_ANIMATIONS = {
  cower: "animation.npc.cower",
  laugh: "animation.npc.laugh",
  clap: "animation.npc.clap",
  cheer: "animation.npc.cheer",
  angry: "animation.npc.angry",
  idle: "animation.npc.idle",
  walk: "animation.npc.walk",
  run: "animation.npc.run",
};
const cameraTokens = new Map();
const reactionTokens = new Map();
const nativePersonaMap = new Map();

for (const emote of FABLE_EMOTES) {
  for (const personaPieceId of emote.nativePersonaPieceIds ?? []) {
    nativePersonaMap.set(personaPieceId.toLowerCase(), emote.id);
  }
}

function audit(kind, message) {
  console.warn(`[Fablecraft][${new Date().toISOString()}][${kind}] ${message}`);
}

function clamp(value, min = -100, max = 100) {
  return Math.max(min, Math.min(max, Math.round(value)));
}

function getNumber(entity, key, fallback = 0) {
  try {
    const value = entity.getDynamicProperty(key);
    return typeof value === "number" ? value : fallback;
  } catch {
    return fallback;
  }
}

function setNumber(entity, key, value) {
  try {
    entity.setDynamicProperty(key, value);
  } catch {
    // Entity may have unloaded between the event and this deferred write.
  }
}

function getJson(entity, key, fallback) {
  try {
    const raw = entity.getDynamicProperty(key);
    if (typeof raw !== "string" || !raw) return fallback;
    return JSON.parse(raw);
  } catch {
    return fallback;
  }
}

function setJson(entity, key, value) {
  try {
    entity.setDynamicProperty(key, JSON.stringify(value));
  } catch {
    // See setNumber.
  }
}

function getAxis(npc, property) {
  try {
    const value = npc.getProperty(property);
    if (typeof value === "number") return value;
  } catch {
    // Older worlds can briefly contain an entity created before the property existed.
  }
  return getNumber(npc, `fc_social_${property.slice(3)}`, 0);
}

function setAxis(npc, property, value) {
  const next = clamp(value);
  try {
    npc.setProperty(property, next);
  } catch {
    setNumber(npc, `fc_social_${property.slice(3)}`, next);
  }
  return next;
}

function readAxes(npc) {
  return {
    loveHate: getAxis(npc, AXES.love),
    fearFunny: getAxis(npc, AXES.fear),
    uglyAttractive: getAxis(npc, AXES.looks),
  };
}

function writeAxes(npc, axes) {
  return {
    loveHate: setAxis(npc, AXES.love, axes.loveHate),
    fearFunny: setAxis(npc, AXES.fear, axes.fearFunny),
    uglyAttractive: setAxis(npc, AXES.looks, axes.uglyAttractive),
  };
}

function isNpc(entity) {
  if (!entity || entity.typeId === "minecraft:player") return false;
  try {
    return typeof entity.getProperty(AXES.love) === "number";
  } catch {
    return typeof entity.getDynamicProperty("fc_social_love_hate") === "number";
  }
}

function isGuard(entity) {
  return entity?.typeId?.startsWith("fc:guard_") ?? false;
}

function nearbyNpcs(player, range = SOCIAL_RANGE) {
  try {
    return player.dimension
      .getEntities({ location: player.location, maxDistance: range })
      .filter(isNpc);
  } catch {
    return [];
  }
}

function targetNpc(player, range = 14) {
  try {
    const hit = player.getEntitiesFromViewDirection({ maxDistance: range })
      .find((entry) => isNpc(entry.entity));
    if (hit) return hit.entity;
  } catch {
    // Fall through to the closest NPC.
  }
  const npcs = nearbyNpcs(player, range);
  npcs.sort((a, b) => {
    const da = Math.hypot(a.location.x - player.location.x, a.location.y - player.location.y,
      a.location.z - player.location.z);
    const db = Math.hypot(b.location.x - player.location.x, b.location.y - player.location.y,
      b.location.z - player.location.z);
    return da - db;
  });
  return npcs[0];
}

function setMorality(player, delta) {
  if (!delta) return;
  const current = getNumber(player, "fc_morality", 0);
  setNumber(player, "fc_morality", clamp(current + delta, -1000, 1000));
}

function guileLevel(player) {
  const explicit = getNumber(player, "fc_guile_level", 0);
  const xp = Math.max(getNumber(player, "fc_guile_xp", 0), getNumber(player, "fc_xp_skill", 0));
  const thresholds = [0, 250, 700, 2200, 6000, 14000, 27400];
  let derived = 0;
  for (let i = 1; i < thresholds.length; i++) if (xp >= thresholds[i]) derived = i;
  return Math.max(explicit, derived);
}

function unlockState(player, emote) {
  const unlock = emote.unlock;
  if (unlock.type === "start") return { unlocked: true, reason: "Available from game start" };
  if (unlock.type === "renown") {
    const value = getNumber(player, "fc_renown", 0);
    return { unlocked: value >= unlock.value, reason: `Requires Renown Rank ${unlock.rank} (${unlock.value})` };
  }
  if (unlock.type === "alignment") {
    const value = getNumber(player, "fc_morality", 0);
    if (unlock.min !== undefined) {
      return { unlocked: value >= unlock.min, reason: `Requires alignment ${unlock.min} or higher` };
    }
    return { unlocked: value <= unlock.max, reason: `Requires alignment ${unlock.max} or lower` };
  }
  if (unlock.type === "guile") {
    return {
      unlocked: guileLevel(player) >= unlock.level,
      reason: `Requires Guile level ${unlock.level} (${unlock.xp.toLocaleString()} Skill XP)`,
    };
  }
  if (unlock.type === "quest") {
    const done = getJson(player, "fc_quests_done", []);
    const oracleComplete = done.includes(unlock.quest) || !!player.getDynamicProperty("fc_oracle_gift");
    return { unlocked: oracleComplete, reason: "Requires completion of Find the Oracle" };
  }
  if (unlock.type === "challenge") {
    return {
      unlocked: !!player.getDynamicProperty(unlock.flag),
      reason: "Requires winning the Chicken Kicking competition",
    };
  }
  return { unlocked: false, reason: "Unknown unlock condition" };
}

export function refreshFableEmoteUnlocks(player, notify = false) {
  const previous = new Set(getJson(player, "fc_emotes_unlocked", []));
  const unlocked = FABLE_EMOTES.filter((entry) => unlockState(player, entry).unlocked)
    .map((entry) => entry.id);
  setJson(player, "fc_emotes_unlocked", unlocked);
  if (notify) {
    for (const id of unlocked) {
      if (previous.has(id)) continue;
      const emote = FABLE_EMOTE_BY_ID.get(id);
      player.sendMessage(`§6Expression unlocked: §e${emote.name}`);
      audit("UNLOCK", `${player.name} unlocked ${emote.name}`);
    }
  }
  return unlocked;
}

function forceThirdPerson(player, ticks = CAMERA_TICKS) {
  const token = (cameraTokens.get(player.id) ?? 0) + 1;
  cameraTokens.set(player.id, token);
  try {
    player.camera.setCamera("minecraft:third_person");
    audit("CAMERA", `${player.name} -> minecraft:third_person for ${ticks} ticks`);
  } catch (error) {
    audit("CAMERA_FAIL", `${player.name}: ${error}`);
    return;
  }
  system.runTimeout(() => {
    if (cameraTokens.get(player.id) !== token) return;
    try {
      // clear() returns to the player's configured perspective, so first-person,
      // third-person-back and third-person-front are all restored correctly.
      player.camera.clear();
      audit("CAMERA", `${player.name} -> player default`);
    } catch (error) {
      audit("CAMERA_FAIL", `${player.name} restore: ${error}`);
    }
  }, ticks);
}

function triggerNpcEvent(npc, eventName) {
  try {
    npc.triggerEvent(eventName);
  } catch (error) {
    audit("NPC_EVENT_FAIL", `${npc.typeId} ${eventName}: ${error}`);
  }
}

function playNpcReaction(npc, animationKey, ticks = 55) {
  const animation = REACTION_ANIMATIONS[animationKey];
  if (!animation) return;
  const token = (reactionTokens.get(npc.id) ?? 0) + 1;
  reactionTokens.set(npc.id, token);
  try {
    npc.playAnimation(animation, { blendOutTime: 0.2 });
  } catch (error) {
    audit("NPC_ANIM_FAIL", `${npc.typeId} ${animation}: ${error}`);
  }
  system.runTimeout(() => {
    if (reactionTokens.get(npc.id) !== token) return;
    try {
      npc.playAnimation(REACTION_ANIMATIONS.idle, { blendOutTime: 0.25 });
    } catch {
      // Entity can legitimately unload before the reaction expires.
    }
  }, ticks);
}

function maybeGiveGift(player, npc, love) {
  if (love < 65 || getNumber(npc, "fc_gift_cooldown", 0) > system.currentTick) return;
  if (Math.random() > 0.28) return;
  setNumber(npc, "fc_gift_cooldown", system.currentTick + 1200);
  try {
    player.runCommand("give @s fc:gold_coin 1");
    player.sendMessage("§dThe admirer presses a small gift into your hand.");
    audit("GIFT", `${npc.typeId} gave ${player.name} a gold coin`);
  } catch {
    // A missing item should not prevent the reaction.
  }
}

function finePlayer(player, guard, amount = 50) {
  const fine = getNumber(player, "fc_fine", 0) + amount;
  setNumber(player, "fc_fine", fine);
  const town = guard.typeId.includes("oakvale") ? "oakvale"
    : guard.typeId.includes("snowspire") ? "snowspire" : "bowerstone";
  setNumber(player, `fc_rep_${town}`, clamp(getNumber(player, `fc_rep_${town}`, 0) - 10, -200, 200));
  player.sendMessage(`§cGuard fine: ${amount} gold. Outstanding fines: ${fine}.`);
  audit("FINE", `${guard.typeId} fined ${player.name} ${amount}`);
}

function chooseNpcReaction(player, npc, emote, success, axes) {
  if (!success) {
    triggerNpcEvent(npc, "fc:react_watch");
    playNpcReaction(npc, "laugh");
    return "laugh_at_player";
  }
  if (isGuard(npc) && (emote.category === "rude" || emote.category === "criminal")) {
    triggerNpcEvent(npc, "fc:react_attack");
    playNpcReaction(npc, "angry");
    finePlayer(player, npc);
    return "guard_attack";
  }
  if (axes.fearFunny >= 45) {
    playNpcReaction(npc, "cower", 30);
    system.runTimeout(() => triggerNpcEvent(npc, "fc:react_flee"), 24);
    return "flee";
  }
  if (axes.loveHate >= 55) {
    triggerNpcEvent(npc, "fc:react_follow");
    playNpcReaction(npc, "cheer");
    maybeGiveGift(player, npc, axes.loveHate);
    return "follow";
  }
  if (axes.fearFunny <= -35 || emote.category === "funny") {
    triggerNpcEvent(npc, "fc:react_watch");
    playNpcReaction(npc, Math.random() < 0.5 ? "laugh" : "clap");
    return "laugh_or_clap";
  }
  if (emote.category === "scary") {
    triggerNpcEvent(npc, "fc:react_watch");
    playNpcReaction(npc, "cower");
    return "cower";
  }
  if (emote.category === "rude" || emote.category === "criminal") {
    triggerNpcEvent(npc, "fc:react_watch");
    playNpcReaction(npc, "angry");
    return "angry";
  }
  triggerNpcEvent(npc, emote.functional === "follow" ? "fc:react_follow" : "fc:react_watch");
  playNpcReaction(npc, emote.category === "romantic" ? "cheer" : "clap");
  return emote.category === "romantic" ? "cheer" : "approve";
}

function applyNpcEffect(player, npc, emote, success, visual = true) {
  const before = readAxes(npc);
  const delta = success ? emote.effect : {
    loveHate: -2,
    fearFunny: -6,
    uglyAttractive: -10,
  };
  const after = writeAxes(npc, {
    loveHate: before.loveHate + delta.loveHate,
    fearFunny: before.fearFunny + delta.fearFunny,
    uglyAttractive: before.uglyAttractive + delta.uglyAttractive,
  });
  const reaction = visual ? chooseNpcReaction(player, npc, emote, success, after) : "test";
  audit("REACTION",
    `${npc.typeId} <= ${player.name}/${emote.id}/${success ? "success" : "failed"} ` +
    `axes=${JSON.stringify(after)} reaction=${reaction}`);
  return { before, after, reaction };
}

function grantGuileXp(player, amount) {
  setNumber(player, "fc_guile_xp", getNumber(player, "fc_guile_xp", 0) + amount);
  setNumber(player, "fc_xp_skill", getNumber(player, "fc_xp_skill", 0) + Math.round(amount * 0.35));
  refreshFableEmoteUnlocks(player, true);
}

function executeSteal(player) {
  const npc = targetNpc(player, 5);
  if (!npc) return player.sendMessage("§7No mark is close enough to pickpocket.");
  const chance = Math.min(0.9, 0.35 + guileLevel(player) * 0.08);
  if (Math.random() <= chance) {
    const amount = 1 + Math.floor(Math.random() * 5);
    try {
      player.runCommand(`give @s fc:gold_coin ${amount}`);
    } catch {
      // Keep progression functional even if the item was removed from a custom build.
    }
    grantGuileXp(player, 150);
    player.sendMessage(`§aYou lift ${amount} gold without being noticed.`);
    audit("STEAL", `${player.name} stole ${amount} gold from ${npc.typeId}`);
    return;
  }
  player.sendMessage("§cThe mark catches your hand.");
  for (const guard of nearbyNpcs(player, 16).filter(isGuard)) {
    triggerNpcEvent(guard, "fc:react_attack");
    playNpcReaction(guard, "angry");
    finePlayer(player, guard, 100);
  }
  audit("STEAL_FAIL", `${player.name} failed against ${npc.typeId}`);
}

function executeLockpick(player) {
  let block;
  try {
    block = player.getBlockFromViewDirection({ maxDistance: 5 })?.block;
  } catch {
    block = undefined;
  }
  if (!block || !["minecraft:chest", "minecraft:trapped_chest", "minecraft:barrel"].includes(block.typeId)) {
    return player.sendMessage("§7Look directly at a chest or barrel to pick its lock.");
  }
  const key = `${block.dimension.id}:${block.location.x},${block.location.y},${block.location.z}`;
  const opened = new Set(getJson(player, "fc_lockpicked", []));
  if (opened.has(key)) return player.sendMessage("§7You have already picked this lock.");
  const chance = Math.min(0.95, 0.42 + guileLevel(player) * 0.08);
  if (Math.random() > chance) {
    player.sendMessage("§cThe pick slips. Nearby guards may have heard it.");
    try {
      player.playSound("random.break", { pitch: 1.8 });
    } catch {
      // Sound is cosmetic.
    }
    for (const guard of nearbyNpcs(player, 12).filter(isGuard)) {
      triggerNpcEvent(guard, "fc:react_attack");
      finePlayer(player, guard, 75);
    }
    audit("LOCKPICK_FAIL", `${player.name} at ${key}`);
    return;
  }
  opened.add(key);
  setJson(player, "fc_lockpicked", [...opened].slice(-128));
  const amount = 3 + Math.floor(Math.random() * 10);
  try {
    player.runCommand(`give @s fc:gold_coin ${amount}`);
  } catch {
    // See executeSteal.
  }
  grantGuileXp(player, 250);
  player.sendMessage(`§aThe lock yields. You find ${amount} gold.`);
  audit("LOCKPICK", `${player.name} opened ${key}`);
}

function executeOracleGesture(player, id) {
  const lines = {
    yeron: "The Oracle answers Yeron: courage without wisdom is merely noise.",
    moryk: "The Oracle answers Moryk: what was buried still remembers the sun.",
    calran: "The Oracle answers Calran: the northern path opens after sacrifice.",
    avisto: "The Oracle answers Avisto: your choices have already changed the ending.",
  };
  const oracle = player.dimension.getEntities({
    location: player.location, maxDistance: 20, type: "fc:oracle",
  })[0];
  player.sendMessage(`§b${lines[id]}`);
  if (oracle) playNpcReaction(oracle, "cheer");
  audit("ORACLE", `${player.name} queried ${id}`);
}

function executeFunctionalEffect(player, emote) {
  if (emote.functional === "steal") return executeSteal(player);
  if (emote.functional === "lockpick") return executeLockpick(player);
  if (emote.functional === "oracle") return executeOracleGesture(player, emote.id);
  if (emote.functional === "wait") {
    for (const npc of nearbyNpcs(player)) triggerNpcEvent(npc, "fc:react_neutral");
  }
}

export function performFableEmote(player, id, options = {}) {
  const emote = FABLE_EMOTE_BY_ID.get(String(id).toLowerCase());
  if (!emote) {
    player.sendMessage(`§cUnknown expression: ${id}`);
    return false;
  }
  const state = unlockState(player, emote);
  if (!state.unlocked && !options.bypassUnlock) {
    player.sendMessage(`§c${emote.name} is locked. §7${state.reason}.`);
    return false;
  }
  const precision = Math.max(0, Math.min(1, getNumber(player, "fc_emote_precision", 0.85)));
  const success = options.success ?? (Math.random() <= precision);
  if (options.camera !== false) forceThirdPerson(player, emote.durationTicks ?? CAMERA_TICKS);
  try {
    player.playAnimation(emote.animation, { blendOutTime: 0.2 });
  } catch (error) {
    audit("PLAYER_ANIM_FAIL", `${player.name} ${emote.animation}: ${error}`);
  }
  if (options.react !== false) {
    for (const npc of nearbyNpcs(player)) applyNpcEffect(player, npc, emote, success, true);
  }
  setMorality(player, success ? emote.effect.morality : -1);
  if (!success) player.sendMessage("§7You miss the expression's sweet spot. The crowd laughs at you.");
  if (options.functional !== false && success) executeFunctionalEffect(player, emote);
  setNumber(player, "fc_emotes_used", getNumber(player, "fc_emotes_used", 0) + 1);
  audit("EMOTE", `${player.name} ${emote.id} success=${success}`);
  refreshFableEmoteUnlocks(player, true);
  return true;
}

function resolveNativeEmote(player, personaPieceId) {
  const normalized = String(personaPieceId).toLowerCase();
  if (nativePersonaMap.has(normalized)) return nativePersonaMap.get(normalized);
  const bindings = getJson(player, "fc_native_emote_bindings", {});
  if (bindings[normalized] && FABLE_EMOTE_BY_ID.has(bindings[normalized])) return bindings[normalized];
  const unlocked = refreshFableEmoteUnlocks(player);
  const used = new Set(Object.values(bindings));
  const choice = unlocked.find((id) => !used.has(id)) ?? unlocked[0] ?? "giggle";
  bindings[normalized] = choice;
  setJson(player, "fc_native_emote_bindings", bindings);
  player.sendMessage(`§8Native emote bound to Fable expression: §e${FABLE_EMOTE_BY_ID.get(choice).name}`);
  audit("BIND", `${player.name} persona=${personaPieceId} -> ${choice}`);
  return choice;
}

function showNpcStats(player) {
  const npc = targetNpc(player);
  if (!npc) return player.sendMessage("§7Look at an NPC within 14 blocks.");
  const axes = readAxes(npc);
  const love = Math.max(0, axes.loveHate);
  const hate = Math.max(0, -axes.loveHate);
  const fear = Math.max(0, axes.fearFunny);
  const funny = Math.max(0, -axes.fearFunny);
  const attractive = Math.max(0, axes.uglyAttractive);
  const ugly = Math.max(0, -axes.uglyAttractive);
  player.sendMessage(
    `§6${npc.typeId} §7— §dLove ${love} §cHate ${hate} §4Fear ${fear} ` +
    `§eFunny ${funny} §8Ugly ${ugly} §bAttractive ${attractive}`
  );
}

function simulateNpcReaction(player, id) {
  const emote = FABLE_EMOTE_BY_ID.get(String(id).toLowerCase());
  const npc = targetNpc(player);
  if (!emote) return player.sendMessage(`§cUnknown expression: ${id}`);
  if (!npc) return player.sendMessage("§7Look at an NPC within 14 blocks.");
  applyNpcEffect(player, npc, emote, true, true);
}

function forceNpcAnimation(player, animationKey) {
  const npc = targetNpc(player);
  if (!npc) return player.sendMessage("§7Look at an NPC within 14 blocks.");
  const animation = REACTION_ANIMATIONS[animationKey];
  if (!animation) return player.sendMessage(`§cUnknown NPC animation: ${animationKey}`);
  try {
    npc.playAnimation(animation, { blendOutTime: 0.15 });
    audit("ANIMATE", `${player.name} forced ${npc.typeId} -> ${animation}`);
  } catch (error) {
    audit("ANIMATE_FAIL", `${npc.typeId}: ${error}`);
  }
  system.runTimeout(() => {
    try {
      npc.playAnimation(REACTION_ANIMATIONS.idle, { blendOutTime: 0.2 });
    } catch {
      // Entity unloaded.
    }
  }, 100);
}

export function runFableEmoteTests(player) {
  let npc;
  let passed = 0;
  let failed = 0;
  try {
    npc = player.dimension.spawnEntity("fc:villager_albion", {
      x: player.location.x + 3,
      y: player.location.y,
      z: player.location.z + 1,
    });
  } catch (error) {
    audit("TEST_FAIL", `Could not spawn test NPC: ${error}`);
    player.sendMessage("§cFable expression tests could not spawn the fixture NPC.");
    return;
  }
  for (const emote of FABLE_EMOTES) {
    try {
      writeAxes(npc, { loveHate: 0, fearFunny: 0, uglyAttractive: 0 });
      const result = applyNpcEffect(player, npc, emote, true, false);
      const expected = {
        loveHate: clamp(emote.effect.loveHate),
        fearFunny: clamp(emote.effect.fearFunny),
        uglyAttractive: clamp(emote.effect.uglyAttractive),
      };
      const ok = result.after.loveHate === expected.loveHate
        && result.after.fearFunny === expected.fearFunny
        && result.after.uglyAttractive === expected.uglyAttractive
        && emote.animation === `animation.fable.player.${emote.id}`;
      if (!ok) throw new Error(`expected=${JSON.stringify(expected)} actual=${JSON.stringify(result.after)}`);
      passed++;
      audit("TEST_PASS", `${emote.id}: registry, animation and rating deltas`);
    } catch (error) {
      failed++;
      audit("TEST_FAIL", `${emote.id}: ${error}`);
    }
  }
  forceThirdPerson(player, 8);
  audit("TEST_PASS", "camera entered third person; restore scheduled");
  system.runTimeout(() => {
    try {
      npc.remove();
    } catch {
      // Fixture already removed.
    }
  }, 10);
  player.sendMessage(`§6Fable expression tests: §a${passed} passed §c${failed} failed§6. See Content Log.`);
}

export function runFableVisualDemo(player) {
  player.sendMessage("§6Fable demo started. Begin video capture now; keep the player and NPC in frame.");
  const sequence = ["flirt", "blood_lust_roar", "fart", "vulgar_thrust"];
  sequence.forEach((id, index) => {
    system.runTimeout(() => performFableEmote(player, id, {
      bypassUnlock: true, success: true, react: false, functional: false,
    }), index * 55);
  });
  system.runTimeout(() => {
    let npc = targetNpc(player, 20);
    if (!npc) {
      try {
        npc = player.dimension.spawnEntity("fc:villager_albion", {
          x: player.location.x + 5, y: player.location.y, z: player.location.z,
        });
      } catch {
        return;
      }
    }
    const center = { ...npc.location };
    forceNpcAnimation(player, "walk");
    for (let i = 0; i <= 24; i++) {
      system.runTimeout(() => {
        const angle = (Math.PI * 2 * i) / 24;
        try {
          npc.teleport({
            x: center.x + Math.cos(angle) * 3,
            y: center.y,
            z: center.z + Math.sin(angle) * 3,
          }, {
            facingLocation: {
              x: center.x + Math.cos(angle + 0.25) * 3,
              y: center.y,
              z: center.z + Math.sin(angle + 0.25) * 3,
            },
          });
        } catch {
          // Chunk/entity unloaded.
        }
      }, i * 4);
    }
    system.runTimeout(() => {
      applyNpcEffect(player, npc, FABLE_EMOTE_BY_ID.get("blood_lust_roar"), true, true);
    }, 115);
    system.runTimeout(() => {
      writeAxes(npc, { loveHate: 0, fearFunny: -40, uglyAttractive: 0 });
      applyNpcEffect(player, npc, FABLE_EMOTE_BY_ID.get("fart"), true, true);
    }, 190);
  }, 245);
  audit("DEMO", `${player.name} started validation sequence`);
}

function commandPlayer(origin) {
  const entity = origin.sourceEntity ?? origin.initiator;
  return entity?.typeId === "minecraft:player" ? entity : undefined;
}

function commandResult(ok, message) {
  return {
    status: ok ? CustomCommandStatus.Success : CustomCommandStatus.Failure,
    message,
  };
}

function registerCommands(registry) {
  const ids = FABLE_EMOTES.map((entry) => entry.id);
  registry.registerEnum("fable:emote_name", ids);
  registry.registerEnum("fable:npc_animation", ["walk", "idle", "run"]);
  registry.registerCommand({
    name: "fable:emote",
    description: "Perform a Fable TLC expression",
    permissionLevel: CommandPermissionLevel.Any,
    cheatsRequired: false,
    mandatoryParameters: [{
      name: "emoteName", type: CustomCommandParamType.Enum, enumName: "fable:emote_name",
    }],
  }, (origin, args) => {
    const player = commandPlayer(origin);
    if (!player) return commandResult(false, "This command must be run by a player.");
    system.run(() => performFableEmote(player, args[0]));
    return commandResult(true, `Performing ${args[0]}`);
  });
  registry.registerCommand({
    name: "fable:npc_stats",
    description: "Display the targeted NPC's social ratings",
    permissionLevel: CommandPermissionLevel.Any,
    cheatsRequired: false,
  }, (origin) => {
    const player = commandPlayer(origin);
    if (!player) return commandResult(false, "This command must be run by a player.");
    system.run(() => showNpcStats(player));
    return commandResult(true, "Reading NPC ratings");
  });
  registry.registerCommand({
    name: "fable:npc_react",
    description: "Simulate a targeted NPC reaction",
    permissionLevel: CommandPermissionLevel.GameDirectors,
    cheatsRequired: true,
    mandatoryParameters: [{
      name: "emoteName", type: CustomCommandParamType.Enum, enumName: "fable:emote_name",
    }],
  }, (origin, args) => {
    const player = commandPlayer(origin);
    if (!player) return commandResult(false, "This command must be run by a player.");
    system.run(() => simulateNpcReaction(player, args[0]));
    return commandResult(true, `Simulating ${args[0]}`);
  });
  registry.registerCommand({
    name: "fable:animate",
    description: "Force the targeted NPC movement animation",
    permissionLevel: CommandPermissionLevel.GameDirectors,
    cheatsRequired: true,
    mandatoryParameters: [{
      name: "animation", type: CustomCommandParamType.Enum, enumName: "fable:npc_animation",
    }],
  }, (origin, args) => {
    const player = commandPlayer(origin);
    if (!player) return commandResult(false, "This command must be run by a player.");
    system.run(() => forceNpcAnimation(player, args[0]));
    return commandResult(true, `Forcing ${args[0]}`);
  });
  registry.registerCommand({
    name: "fable:test",
    description: "Run the Fable expression runtime tests",
    permissionLevel: CommandPermissionLevel.GameDirectors,
    cheatsRequired: true,
  }, (origin) => {
    const player = commandPlayer(origin);
    if (!player) return commandResult(false, "This command must be run by a player.");
    system.run(() => runFableEmoteTests(player));
    return commandResult(true, "Runtime tests started");
  });
  registry.registerCommand({
    name: "fable:demo",
    description: "Run the expression and NPC animation capture sequence",
    permissionLevel: CommandPermissionLevel.GameDirectors,
    cheatsRequired: true,
  }, (origin) => {
    const player = commandPlayer(origin);
    if (!player) return commandResult(false, "This command must be run by a player.");
    system.run(() => runFableVisualDemo(player));
    return commandResult(true, "Visual demo started");
  });
}

// Defensive boot: a throw here (e.g. an event signal that is unavailable on an
// older runtime) must NOT propagate, or it would abort this module's evaluation
// and take main.js — and with it the entire mod — down. Degrade quietly instead
// so combat, XP, quests, NPCs and the Guild keep working even if emotes can't.
try {
  system.beforeEvents.startup.subscribe((event) => {
    try {
      registerCommands(event.customCommandRegistry);
      audit("COMMANDS", "Registered /fable:emote, /fable:npc_stats, /fable:npc_react, /fable:animate");
    } catch (error) {
      audit("COMMAND_FAIL", String(error));
    }
  });

  world.afterEvents.playerEmote.subscribe((event) => {
    system.run(() => {
      const id = resolveNativeEmote(event.player, event.personaPieceId);
      performFableEmote(event.player, id);
    });
  });

  world.afterEvents.playerSpawn.subscribe((event) => {
    if (!event.initialSpawn) return;
    system.runTimeout(() => refreshFableEmoteUnlocks(event.player, true), 20);
  });

  system.afterEvents.scriptEventReceive.subscribe((event) => {
    const player = event.sourceEntity?.typeId === "minecraft:player" ? event.sourceEntity : undefined;
    if (!player) return;
    if (event.id === "fable:emote") performFableEmote(player, event.message.trim());
    if (event.id === "fable:npc_stats") showNpcStats(player);
    if (event.id === "fable:npc_react") simulateNpcReaction(player, event.message.trim());
    if (event.id === "fable:animate") forceNpcAnimation(player, event.message.trim());
    if (event.id === "fable:test") runFableEmoteTests(player);
    if (event.id === "fable:demo") runFableVisualDemo(player);
  });

  audit("SYSTEM", `Fable expression system online (${FABLE_EMOTES.length} expressions)`);
} catch (bootError) {
  console.warn(`[FableCraft] Fable emote system failed to initialize; the rest of the mod will still load. ${bootError}`);
}

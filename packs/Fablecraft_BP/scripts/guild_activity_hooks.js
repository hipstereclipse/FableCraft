// Shared handwritten adapters. Durable ownership lives in guild_activity.js;
// social callbacks may observe it but cannot replace a newer activity.
import { notifyGuildTrainingReaction } from "./guild_training.js";
let activity, training;
export function bindGuildActivity(controller, trainingController) {
  activity = controller; training = trainingController;
}
export function guildActivityStatus(entity) {
  try {
    if (activity) return activity.status(entity);
    return { managed: entity.typeId === "fc:guild_apprentice_skill", blocked: true };
  } catch { return { managed: true, blocked: true }; }
}
export function guildActivityReserved(entity) {
  const state = guildActivityStatus(entity);
  return state.managed && (state.blocked || state.mode !== "idle");
}
export function requestNpcActivity(entity, player, mode, options = {}) {
  const state = guildActivityStatus(entity);
  if (state.managed) {
    try { return activity?.request(entity, player, mode, options)
      ?? { handled: true, accepted: false, reason: "unavailable" }; }
    catch { return { handled: true, accepted: false, reason: "unavailable" }; }
  }
  // Legacy companions have no requester journal or genuine stationary goal.
  // Do not turn an unowned Wait into a crowd-wide neutral/roaming broadcast.
  if (mode === "wait") return { handled: true, accepted: false, reason: "unsupported" };
  try {
    const event = mode === "follow" ? "fc:react_follow" : "fc:react_neutral";
    training?.interrupt(entity);
    if (training?.reserved(entity)) return { handled: true, accepted: false, reason: "training-cleanup" };
    entity.triggerEvent(event);
    notifyGuildTrainingReaction(entity, event);
    return { handled: false, accepted: true };
  } catch { return { handled: false, accepted: false, reason: "unavailable" }; }
}
export function preemptNpcActivity(entity) {
  if (!guildActivityStatus(entity).managed) return false;
  try { activity?.preempt(entity); } catch { }
  return true;
}
export function routeGuildActivityReaction(entity, event, player) {
  if (!guildActivityStatus(entity).managed) return false;
  if (event === "fc:react_follow") {
    requestNpcActivity(entity, player, "follow");
    return true;
  }
  return guildActivityReserved(entity);
}
export function captureGuildReaction(entity) {
  try {
    return { id: entity.id, dimension: entity.dimension.id,
      revision: guildActivityStatus(entity).revision };
  } catch { return null; }
}
export function guildReactionCurrent(entity, token) {
  try {
    return !!token && entity.isValid === true && entity.id === token.id
      && entity.dimension.id === token.dimension
      && guildActivityStatus(entity).revision === token.revision
      && !guildActivityReserved(entity) && !training?.reserved(entity)
      && !entity.hasTag("fc_guild_defending") && !entity.hasTag("fc_aggravated");
  } catch { return false; }
}

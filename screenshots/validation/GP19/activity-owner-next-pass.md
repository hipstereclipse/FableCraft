# Next pass: requester-owned activity for two Skill residents

Read-only implementation design, 2026-09-12. **GP19 is not implemented.** GP18
changes only the Maze furnishing geometry. This note narrows the earlier
[DP5 activity audit](../DP5/activity-followup-audit.md) after GP17 repaired the
deferred relationship races. Native Follow/Wait, multiplayer/reconnect behavior
and movement restoration remain **unrun**.

## Smallest useful pilot

Introduce one activity controller for only the existing roster-bound
`skill_range` and `skill_hall` entity IDs. It owns Follow, Wait, release and
interruption. Keep station arrival, new schedules, new resident births and
whole-campus navigation outside this pass.

Resolve identity from the validated `fc_guild_residents_v1` registry: correct
base, slot, `bound` status, exact entity ID and Skill type, plus the matching
`fc_guild_resident_slot` marker. The marker is actually
`baseX,baseY,baseZ/slot`, not merely `skill_range`. A nearby same-type entity or a
copied slot marker is insufficient. Unavailable, dead, ambiguous, conflicting or
unreadable identity defers. Add a read-only resolver to the existing resident
owner if needed; do not enroll, respawn, move or rewrite identity to enable an
activity. A cached optimistic snapshot after a failed save is insufficient
mutation authority.

A requesting player must be valid, nearby and in the resident's dimension.
Current married state must be readable and internally consistent; a married
resident additionally requires the exact current spouse owner. An unowned
eligible resident may accept Follow. Its current activity requester alone may
change Follow to Wait, resume Follow or release it. Another Hero cannot replace
that requester. Functional Wait affects only the caller's owned eligible
followers; a spouse's explicit Wait can acquire an idle resident after the same
fresh spouse check. Wait reserves the resident and stops voluntary walking in
place; it does not teleport, disable gravity or promise immunity to external
knockback.

## Durable state and native selection

Use a separate versioned world activity journal, proposed
`fc_guild_skill_activity_v1`, with the Guild base and two fixed slot records:
`entityId`, monotonic `revision`, `mode` (`idle`, `follow`, `wait`, `stopping`),
`ownerId`, original dimension and `pendingTagHolders`. Keep this separate from
spouse lists, resident identity and opinion/name history. Player tags and NPC
component groups are derived effects, not the authority. No strong permanent
map of player/entity wrappers is needed; reacquire handles by stable IDs.

Generate two fixed native Follow channels on the Skill entity owner, one per
slot. Each `minecraft:behavior.follow_mob` filter must require both player family
and that channel's player tag on `subject: other`. For example, proposed tags
are `fc_skill_range_requester_v1` and `fc_skill_hall_requester_v1`. A Hero can
hold both channels. Do not use the existing family-only generic Follow goal,
`follow_owner`, taming, or an invented script target/path API. The existing goal
admits any eligible player; the primary docs do not justify describing its
choice as necessarily the nearest player.

Before granting a player tag, persist that player ID in the channel's holder
journal and verify the write. Stop the previous native goal explicitly before
changing targets; filter changes alone do not prove cached native targets were
dropped. Clear stale tags from all readable online players and verify the
result before enabling a channel. A previous holder who is offline remains
pending: absence from `world.getPlayers()` never proves their tag was removed.
The channel cannot be reassigned until their cleanup is verified. A failed
read, property write, tag removal/addition or event leaves the channel stopped
or pending, never optimistically free. Do not discard holder history because a
timeout elapsed or an NPC unloaded.

On entity load/removal, player spawn/join/leave and a bounded reconciliation
interval, refresh the exact handles and state. `entityRemove` means unavailable,
not dead. The pinned leave notification supplies an ID and is not a reliable
last chance to mutate a disconnected player. On reconnect, clear recorded stale
channel tags before reuse. Recheck generations inside delayed callbacks; an old
fear/idle/form callback cannot replace a newer activity.

For the first pilot, the conservative proposed reload policy is to stop and
reconcile existing native activity before allowing a fresh requester command,
while retaining owner and cleanup obligations until they are resolved. Automatic
resumption is a separate policy decision; do not silently promise it. Journal
bootstrap also needs a concrete rule before implementation: genuinely new state
must be distinguished from missing established holder history. A write-ahead
initialization witness is one option. Malformed or unreadable existing state
must never become an empty journal. These writes span world/player/entity
state; this design does not establish crash-atomic persistence.

## Exact integration points and ordering

| Existing owner | Required bounded integration |
| --- | --- |
| `guild_residents.js` and `main.js` resident adapters | Resolve the two established IDs read-only; use load/remove/death information without changing the roster. |
| New `guild_activity.js`, wired by `main.js` | Single requester/revision/journal authority, channel reconciliation and bounded pending cleanup. |
| `fable_emotes.js`: `performFableEmote`, `chooseNpcReaction`, `executeFunctionalEffect`, `triggerNpcEvent` | Route pilot activity through that authority and pass the actual requester. Successful Wait currently runs generic reaction effects first, then broadcasts neutral. Pilot Wait must bypass that generic activity branch, or it can create Follow before trying to stop it. Preserve non-pilot behavior within this bounded scope. |
| `fable_emotes.js`: delayed fear reaction and idle animation callbacks | Capture and revalidate the pilot's activity revision; prevent stale callbacks from replacing later Follow/Wait/defence. Generic social movement events must not erase another Hero's owned activity. |
| `main.js`: `spouseMenu`, `marryNpc`, `divorceConfirm` | Keep GP17's fresh relationship checks and route accepted Follow/Wait/release through the same activity owner. Marriage may succeed even if Follow must defer for channel cleanup; do not steal another activity or claim movement succeeded. |
| `main.js`: queued NPC interaction | Revalidate the live requester/target before the queued interaction; reserve/interruption behavior must respect current activity ownership. Conversation must not reset a different Hero's movement merely by emitting a reaction. |
| `guild_training.js` and `main.js` training adapters | Reserved or pending pilot activity excludes training. Complete training cleanup before adding Wait/Follow; verify cleanup rather than assuming `interrupt()` succeeded. Retain existing stale-session cancellation and one-placement limit. |
| `guild_defence.js`, its `main.js` adapter, and generated defence events | Defence invalidates activity callbacks and removes Wait/Follow before engaging. Restore movement even when Wait was active; priority-zero combat cannot walk while movement remains zero. Cleanup failures remain pending for retry. Do not alter offender selection or warrants. |
| `main.js`: `boastGatherCrowd` | Exclude reserved/pending pilot activity so boasting cannot teleport an owned waiting resident. Its current following-tag/training checks do not cover owned Wait. |
| `gen_behavior.py` | Generate filtered Follow channels, owned Wait and explicit stop/restore events only for the Skill type. Other instances cannot acquire these channels without the runtime's exact roster binding. Preserve defence reapplication when removing overlapping social components. |
| `gen_emotes.py` / `fc_emotes.py` | Visual/registry owners, not native activity authorities. No animation rewrite is needed. Only change registry data if the chosen expression contract actually requires it. |

Training stop restores `movement`, pushability and knockback components. Applying
it after a movement-zero Wait overlay can make the resident walk again. The
activation order must therefore be: reserve journal/revision, stop training and
confirm it is clean, remove conflicting native activity, reconcile player tags,
then apply the intended native group. Later training passes must not reapply
roaming over Wait. Conversely, every Wait exit and defence preemption must
restore the normal movement value explicitly; removing an overriding component
group does not restore the base component automatically.

Generic Follow shares `minecraft:behavior.follow_mob` with the proposed scoped
groups. Generic neutral/watch/flee events can erase that component even when a
different group supplied it. Cover every production caller through the dispatcher
and make generated transition ordering explicit. Keep the existing conditional
reapplication of Guild defence after social-component changes.

## Meaningful verification before claiming the pilot works

Execute actual controller and production callback code with two Heroes and both
canonical residents, including distinct wrappers sharing the same IDs. Cover:

- Independent Follow channels; attempted takeover; owner Follow/Wait/release;
  functional Wait preserving the other Hero and an unrelated trainee; spouse
  ownership changes and old form responses after an activity revision changes.
- Actual emote ordering, high-love implicit Follow, delayed fear/idle work,
  marriage/divorce hooks, queued interaction and boasting exclusion.
- Missing/corrupt registry or journal, copied markers, wrong base/ID/type,
  unreadable handles, duplicate online tags, failed writes before/after mutation,
  and cleanup failures that must not release the channel.
- Owner disconnect while NPC remains loaded, NPC unload while owner stays,
  both unavailable, reconnect in either order, dimension changes, death versus
  removal, fresh wrappers and reload with persisted groups/tags. A new Hero must
  never receive a channel while an offline previous holder remains unverified.
- Real training cleanup before Wait, failed cleanup, stale scheduled training
  work, defence preemption and restoration, and no automatic activity revival
  from a stale callback after defence.

Inspect the `gen_behavior.emit_entity` definition shared by the resident's
normal and married appearances. Assert exact other-player tag filters, no generic-player alternative in a scoped
channel, explicit movement restoration, preservation of defender filters and
absence of taming/teleport components. Simulate component addition/removal with
shared-key deletion; checking only JSON group names misses the Wait/Follow
restoration defects.

Native acceptance remains necessary for actual target selection, old-target
drop, Follow stopping distance, movement restoration, obstruction handling,
physical Wait behavior, two-Hero disconnect/reconnect and save/reload. Pinned
API/component provenance already lives in the DP5 audit; no new navigation API
is assumed here. Purposeful Skill arrival remains queued after this pilot.

# Guild Skill activity ownership

GP19 addresses the requester-independent Follow filter, roaming after promised
Wait, and the Wait expression's broadcast to unrelated NPCs. The implementation
passes offline validation. Native Bedrock movement and multiplayer acceptance are unrun.

Only the two established `skill_range` and `skill_hall` residents can acquire
the new activities. A fresh read of the existing resident registry must agree
with the exact entity ID, type, Guild base and saved marker. This read cannot
enroll, replace, teleport or rename a resident. Missing or conflicting history
defers. Relationships, opinion axes, residence and construction retain their
existing owners.

An eligible nearby Hero can request Follow from an idle resident. Only that
requester can change it to Wait, resume Follow or release it. A married resident
requires the current spouse; that spouse may explicitly ask an idle resident to
Wait. The twelve-block interaction range, two-channel pilot and stopping cadence
are Minecraft adaptations. They are not claims about original TLC AI schedules.

`guild_activity.js` owns a versioned world journal and a separate initialization
witness. The witness is verified before the first journal write. A missing
established journal, corrupt schema, changed base or unreadable storage never
becomes empty history. The journal records each channel's resident, requester,
revision and outstanding player-tag cleanup. It records a holder before granting
the tag. Offline holders retain their cleanup obligation; a channel cannot be
reused while that obligation remains unverified. If both journal and witness are
externally destroyed, the original history cannot be distinguished from a first
installation. Failed revision writes and newly observed holder debts remain
quarantined in the running session until a verified retry. A crash before those
observations can be persisted cannot recover them. No atomic crash-recovery or
administrator-edit recovery is promised. Each channel retains at most 64 holder
IDs. Overflow from unexpected or unreadable external tags latches a persistent
quarantine: native effects stop, but the channel is never silently reused. Manual
recovery of that exceptional history is outside this pilot.

Follow uses two generated native goals, each filtered by player family and its
own exact requester tag. Wait sets voluntary movement to zero while retaining
gravity and ordinary pushes. No taming or script navigation command is used.
Training cleanup must finish before activity activation. The old native goal is
stopped before any replacement requester tag, with at least one tick between
the stop and activation. Deferred activation rechecks identity, requester,
relationship, dimension, proximity and defence. A queued request is presented as
pending, rather than as completed movement.

Reload stops and reconciles saved activity; it does not automatically resume
Follow. Failed native events or tag/storage operations retain a pending state.
Defence removes Wait and Follow and restores movement before combat, including
when activity cleanup fails. Generated events account for removal of component
keys shared by training, social reactions and combat. No offender or warrant
selection changes.

The Wait expression bypasses its generic admiration/reaction branch and asks
only the caller's owned residents to wait. It leaves the other Hero's follower
and unrelated trainees alone. NPCs outside this pilot have no requester journal
or stationary Wait goal, so their Wait request defers without broadcasting
neutral. Their existing generic Follow remains outside this pass. Spouse menus
retain GP17 relationship checks and also capture the activity revision. Delayed
fear and idle callbacks cannot replace newer owned activity, active training or
defence. Boast gathering excludes owned and pending activity.

Owners are `guild_activity.js`, `guild_activity_hooks.js`, the read-only resident
resolver, `main.js`, `fable_emotes.js`, the defence adapter, and
`scripts/gen_behavior.py`. Only the Skill entity is regenerated. No Guild geometry,
station coordinates, saved-room assets or reward data change. The earlier
[activity audit](../screenshots/validation/DP5/activity-followup-audit.md) records
the reproduced defects and version-pinned primary API evidence. The
[GP19 design](../screenshots/validation/GP19/activity-owner-next-pass.md) records
the implementation boundary before this pass; this document records final scope.

Offline evidence is in `screenshots/validation/GP19/`: all 51 base gates, 64 ESM
syntax checks, 16 controller groups, 9 actual integration groups and 8 native
component-transition groups pass. Existing relationship/training/resident/defence
suites pass 24/33/22/14 groups. The GP18 actual-source probe reproduces both old
Wait broadcast and stale fear replacement. Independent review passes 13 additional
failure probes after fixing revision exhaustion, failed invalidation writes,
unverified holder debt and conflicting resident candidates.

The first base run exposed one missing dependency in the Might-only maintenance
test fixture. After supplying its unmanaged activity boundary, that gate passed;
the original failure and targeted rerun remain recorded. Production source did
not change during that correction. Fresh 35-asset C2 and Guild diagnostics pass.
All 35 structure assets, 35 C2 images and six rendering/data/geometry owners match
GP18; full-render evidence is retained from those unchanged inputs. No new full
render is claimed. Only the Skill behavior differs among 51 isolated entity outputs.

The native acceptance list remains open:

- Two Heroes independently Follow/Wait with both canonical Skill residents.
- Native target selection, cached target removal, stopping distance and obstacles.
- Wait on slopes, under pushes, and during a real Guild defence interruption.
- Save/reload, either rejoin order, unloaded residents and dimension changes.
- Failed cleanup followed by recovery without target reuse or identity changes.

Purposeful walking to training stations, other companions, canonical staffing,
player lessons and reactive targets remain separate work. Offline component and
callback checks do not establish native navigation or whole-facility fidelity.

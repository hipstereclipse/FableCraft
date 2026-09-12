# Guild training lifecycle — first GP3 pass

Implemented 2026-09-12 as a bounded response to
[GP1's NPC audit](GUILD_NPC_AUDIT.md). Assigned apprentices now acquire a station
once per background session, release reliably, and interrupt their drills for
conversation, social reactions or combat. A successful station acquisition still
uses one collision-checked placement: **this is a temporary Minecraft adaptation,
not walking to the station or canonical TLC scheduling**. Release restores normal
movement at the current location and never teleports residents back to hall posts.

The established discipline types, initial resident anchors and 60-second drill /
120-second rest cadence remain. Guildmaster, Maze, Whisper/tutorial lessons, Will
island activity, roster identity and offender-specific defence remain later work.
The first Demon Door pilot followed this bounded pass;
[GP4 defence](GUILD_DEFENCE.md) now adds offender-specific combat eligibility.

## Lifecycle and interruptions

`packs/Fablecraft_BP/scripts/guild_training.js` owns assignment state, collision
preflight, session eligibility, cleanup retries and delayed-action tokens. The
handwritten `main.js` interval selects a complete sparring pair and one Skill
apprentice, then drives existing animation clips. Its duties are now:

1. Reconcile each observed apprentice once, removing legacy training state even
   when old code left a component without its role tag. Failed cleanup stays
   pending and prevents acquisition until the stop event succeeds.
2. Check support under the full apprentice footprint and air at feet/head height,
   then use `tryTeleport` with `checkForBlocks: true`. Missing chunks, blocked
   headroom, absent floor, `false` returns and exceptions all refuse acquisition.
   Only authored coarse-dirt/dirt-path floors qualify; unknown replacement floors
   refuse drills. This uses stable typeId/isAir fields; Block.isSolid is currently
   marked pre-release in the official Block documentation.
   There is no unchecked fallback and no repeated attempt for that apprentice
   during the same session.
3. Keep a stable token while drilling. Repeated interval passes reuse it and do
   not teleport. Both fighters must acquire successfully; partial pair acquisition
   releases its successful member. Missing partners, displaced residents,
   obstructed stations and dimension changes cancel the assignment.
4. Cancel queued bow/spar feedback immediately on interruption. Conversation,
   Watch/Follow and aggression also keep the apprentice out of the remainder of
   the current session, with at least ten seconds of quiet time. Training resumes
   in a later session when the resident is eligible again.
5. Stop on rest, night, empty scans or invalid entities. A returning loaded entity
   is reconciled on first observation. Stop failures retain their cleanup state;
   they do not silently discard the role and strand a frozen resident.

The shared `notifyGuildTrainingReaction` hook is called by the handwritten emote
owner's `triggerNpcEvent` and the marriage/Follow/Wait conversation paths. A new
Follow reaction adds `fc_guild_following`; another social reaction clears it,
matching the behavior owner's replacement of social groups. Married apprentices
are conservatively excluded, preserving existing spouses whose pre-GP3 Follow
state has no durable marker. An old unmarried expression follower without that
marker cannot be identified reliably; this migration limitation remains open.

Boasting excludes active or cleanup-pending trainees, aggravated defenders and
marked followers. Eligible resting apprentices invited into a crowd receive the
same interruption before the existing gathering action. The larger boasting
feature still teleports crowds and has no walk/return schedule; GP3 fixes its
conflict with training rather than claiming that whole feature is faithful.

## Movement restoration and harmless practice

The owner fix is necessary independently of the runtime retry logic. Microsoft's
[component removal documentation](https://learn.microsoft.com/en-us/minecraft/creator/documents/entitybehaviorintroduction?view=minecraft-bedrock-stable#removing-components)
explains that removing an overriding component group does not reinstate the base
component. `gen_behavior.py` now emits `fc:guild_roaming` with each apprentice's
original movement, knockback resistance and pushability. Start removes roaming
and adds training; stop removes training and explicitly adds roaming. The event
does not remove social reaction groups, clear aggression tags or calm defenders.

Only the three apprentice BP entities were regenerated. Their existing health,
families, dimensions, romance state and dialogue definitions remain governed by
their established owner. No models, animation clips or resource outputs needed
regeneration. See the exact JSON-path/hash delta in
[apprentice-output-delta.json](../screenshots/validation/GP3/apprentice-output-delta.json).

Archery keeps its bow animation and sound, but its delayed release draws a short
particle trail toward the target. It creates no projectile/entity, damage, hit XP
or collectible arrow. Both bow release and the delayed spar impact validate the
current token, session, station and resident eligibility. A stale callback cannot
affect a newly acquired session. This harmless visual drill is an adaptation;
player archery lessons, target scoring, moving targets and Will practice remain
unimplemented.

The engine's placement options are documented in
[TeleportOptions](https://learn.microsoft.com/en-us/minecraft/creator/scriptapi/minecraft/server/teleportoptions?view=minecraft-bedrock-stable)
and [`Entity.tryTeleport`](https://learn.microsoft.com/en-us/minecraft/creator/scriptapi/minecraft/server/entity?view=minecraft-bedrock-stable#tryteleport).
Offline mocks verify call ordering and refusal paths, not the engine's actual
navigation, collision or animation response.

## Verification and remaining acceptance

Evidence is under `screenshots/validation/GP3/`. The pre-regeneration behavior
regression passed; the updated suite has five passing groups, including repeated
start/stop transitions over the emitted component definitions. Eighteen new Node
test groups execute the production controller and actual main/emote callbacks.
They cover repeated sessions, missing/failed component events and tag writes,
legacy cleanup, complete pairs, blocked/unloaded stations, failed engine
placement, conversation, Follow/Watch, combat, changed dimensions, displacement,
night, invalid/missing residents, stale delayed actions and boasting eligibility.
The existing runtime suite and NPC/runtime lint also pass; lint retains existing
warnings and reports no errors. Exact commands and results are in
[npc-checks.json](../screenshots/validation/GP3/npc-checks.json).

Run the focused suite with
`node --experimental-vm-modules scripts/tests/guild_training.test.mjs`.
It loads production ESM via `vm.SourceTextModule` and does not rely on an untracked
nested `package.json`. The generator transition test is part of
`python scripts/tests/test_gen_behavior.py`.

All in-engine acceptance remains **unrun**:

- Observe a full daylight session and rest transition; confirm each trainee
  receives at most one acquisition placement and actually resumes normal speed.
- Verify clear/blocked station collision with the real apprentice model/collider;
  observe facing, animation blending and the visible harmless archery trail.
- Talk, gift, use Watch/Follow, provoke, remove or unload an active trainee during
  the bow draw; confirm prompt release and no queued strike/shot afterward.
- Save/reload with old tags, during training and after Follow; verify recovery
  without changing spouse ownership or unrelated saved-world progress.
- Check partner loss, night transition, crowd gathering and two simultaneous
  visitors. Roster duplication from N5/N7 remains open. GP4 adds offender-specific
  targeting for N6; actual multiplayer engine behavior still requires testing.

N1's repeated and return teleports are fixed offline, while actual navigation to
marks remains open. N2–N4's lifecycle and delayed-projectile defects and N8's
training conflict have targeted coverage. No claim of complete Guild NPC fidelity,
roster repair correctness, player tutorial functionality or engine AI execution
is made by this pass.

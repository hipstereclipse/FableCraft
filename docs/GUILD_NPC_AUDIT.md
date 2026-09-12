# Guild NPC audit — GP1

Baseline audited on 2026-09-12. This is an offline source/control-flow audit;
Bedrock movement, collision, animation blending, saved-world loading and damage
checks remain **unrun**. No NPC behavior is fixed by this document. The priority
queue is [GUILD_DEMON_PRIORITIES.md](GUILD_DEMON_PRIORITIES.md).

The baseline probe executes the actual training/roster section of `main.js` in a
small Node VM, substitutes world/entity calls and records observed control flow.
Its source hash, results and explicit limits are in
[baseline-probe.json](../screenshots/validation/GP1/npc/baseline-probe.json); rerun
with `node screenshots/validation/GP1/npc/baseline-probe.mjs`. Component event
failure is injected; the probe does not emulate Bedrock component restoration.

## Reference roles and adaptation boundaries

The local architecture snapshot, especially lines 46–86, identifies the
Guildmaster/map room, Maze's upper quarters, apprentice dormitories and separate
melee, archery and Will grounds. The original TLC manual's
[About the Guild spread and map](https://www.gamesdatabase.org/Media/SYSTEM/Microsoft_Xbox/Manual/formated/Fable-_The_Lost_Chapters_-_Microsoft_Game_Studios.pdf)
corroborate distinct training areas, dining/sleeping facilities and Maze's quarters.
Its orientation must be reconciled against the generated layout rather than
interpreting snapshot compass labels as authoritative measurements.

[Ron Hiler's TLC PC walkthrough](https://gamefaqs.gamespot.com/pc/926702-fable-the-lost-chapters/faqs/41298)
corroborates Guildmaster-led instruction, sparring with Whisper, archery and Will
tests, and Maze's final examination in the Guild Woods. This is secondary textual
evidence; character timing, paths, gestures and exact lines need original-game
video verification. No current 60-second/120-second background schedule is
established as canonical.

| Character | Reference-supported purpose | Current implementation and fidelity gap |
| --- | --- | --- |
| Guildmaster | Instructor and quest/map-room guide. | Spawns beside map at `(23,1,42)`; random stroll, morality/reputation greeting, unlimited Quest Card button and Hero Menu. No guided training, activity state or return-to-map routine. Current comic dialogue is authored adaptation. |
| Maze | Upper quarters; final discipline exam in Woods. | Spawns at coupled `(46,12,70)` study anchor; random stroll, once-per-player Lightning **and Fireball** tome gift. UI promises only Lightning. No exam, story-aware presence, study activity or home constraint. Keep this anchor coupled to geometry. |
| Whisper | Named training partner. | No entity/roster entry. Generic apprentices cannot count as her tutorial interaction. |
| Might apprentices | Anonymous trainees are compatible with academy setting. | Two generic residents prioritize sword/stick sparring. Fixed role identity, routine, moves and text are adaptations. No player sparring lesson or hit/block grading. |
| Skill apprentices | Archery training is reference-supported. | One of two generic residents shoots at a stationary target. No scoring, moving targets or player instruction. Other resident has generic stroll. |
| Will apprentices | Separate magic training grounds. | Both roam halls; fallback may select one for stick sparring. Model owner adds a stick. No magic drill on the island; spark dialogue is not implemented activity. |
| Theresa | Story character; snapshot identifies a Theresa-like tavern **statue**. | A permanent living Library resident is an adaptation, not evidence-backed librarian behavior. No story-phase guard. Preserve existing world progress while deciding its replacement. |
| Trader / tavern staff | Snapshot names storekeeper Dylan and innkeeper Alfie. | Generic trader at west exterior cart; no Guild roster barkeep. Names, shop role, placement and residents need a separate fidelity pass. |
| Gate guards | Guild defence is compatible with fortress framing. | Two Bowerstone guard entities are tagged Guild guards. Faction dialogue still uses their Bowerstone type; campus-wide attacks and reinforcement behavior are gameplay adaptations. |

The inspectable roles come from `main.js` `buildGuildWhenReady` (initial spawn,
around line 476), `GUILD_ROSTER` (1365), `npcTalk` (3779), `spouseMenu` (3706)
and `NPC_BARKS` (around 4457). Local snapshot
`UIofFable.md:133` distinguishes experience spending at the platform from a
physical combat lesson. The existing `trainMenu` (2671) is XP spending; its name
does not establish tutorial implementation.

## Ranked defects

| Priority / ID | Concrete trigger and result | Evidence / owner | Bounded next action |
| --- | --- | --- | --- |
| High N1 | Assigned apprentices teleport every 10 ticks even if already exactly at their marks. Closing the session teleports them to hall posts despite the comment saying they are walked there. A 100-tick probe records 10 teleports per trainee, then an eleventh on release. | `main.js:1021` `lockTrainingPosition`, training interval at 1260; baseline `station_teleports_over_100_ticks`, `rest_transition`. | Explicit station/session lifecycle; no periodic teleport at rest. Walking requires a verified navigation owner and walkable routes; do not relabel teleport as walking. |
| High N2 | `clearTrainingRole` removes tags before invoking stop. If stop throws, the next attempt returns because there are no tags; a training component may remain frozen indefinitely. Start also tags before event success, so a failed start is not retried. | `main.js:992` `setTrainingRole`, `1007` `clearTrainingRole`; baseline `failed_stop` records one attempt and stranded stub component. | Keep pending cleanup until event succeeds; reconcile stale state after reload; test both event failures. |
| High N3 | If a sparring partner disappears, the remaining selected fighter retains its training tag/component but no exchange runs. Generic conversation, gifts and spouse Follow do not reserve/interrupt a station; the next scheduler pass restores it. | `main.js:1312–1354`, interact handler 3341, `spouseMenu:3706`; baseline `missing_partner`. | Require a complete pair; interruption/cooldown and cleanup for interaction, follow, combat, removal and unavailable partners. |
| High N4 | A Skill apprentice aggravated after its scheduling tick can release a real arrow before the next cleanup tick. The delayed callback only checks role/daylight. Arrows have one tag write and no tag-aware hit/damage interception or lane occupancy check anywhere in `main.js`. | `main.js:1230` `firePracticeArrow`, delayed callback 1347; baseline `delayed_release_after_aggravation` creates one arrow. `gen_behavior.py:428` allows all damage to NPCs. Actual damage severity is engine-unrun. | Revalidate session/role/interaction/combat at release. Use harmless practice feedback or an owner-defined harmless projectile; preserve visible archery activity without exposing visitors to unguarded projectiles. |
| High N5 | Roster counts types within 140 blocks, not persistent residents. An apprentice following Hero A away is replaced while Hero B remains at Guild; return yields three of that type. A foreign nearby trader suppresses a missing Guild trader. No duplicate cleanup exists. | `main.js:1365–1399`; baseline `resident_left_and_returned` and `foreign_trader_suppresses_repair`. Initial residents other than guards lack even `fc_guild_npc`; replacement residents get that tag. | Separate persistent slot/identity design with conservative legacy adoption. Missing/unloaded must not mean dead. Never delete married/progress-bearing duplicates automatically. |
| High N6 | A warrant for one Hero rallies defenders whose `fc:reaction_attack` target is any player within 80 blocks. Innocent multiplayer visitors qualify. Clearing one Hero's warrant calms the entire nearby Guild regardless of other warrants. | `gen_behavior.py:515` reaction filter; `main.js:5393` rally and `5396` calm; baseline records target filter. Damage/target selection needs two-player engine verification. | Separate bounty ownership pass: offender-specific eligibility and aggregate remaining-warrant checks. Requires generator/runtime coordination, not a visual pose fix. |
| Medium N7 | Every missing type is restored on a 200-tick sweep while any Hero is on campus. Death, deliberate removal, unavailable entity and lost spawn are indistinguishable. Persistent NPC components prevent distance despawn but do not establish roster identity. | `main.js:1375`; `gen_behavior.py:550` persistence; `trySpawn:774` catches failure. | Preserve named-character/story outcomes and spouse IDs in roster repair policy; record retries without treating geometry damage as successful placement. |
| Medium N8 | Boasting gathers friendly NPCs by teleport, including active trainees and aggravated defenders; next training tick pulls trainees back. No original activity return state exists. | `main.js:4379` `boastGatherCrowd`; Maze excluded, trainees/combatants not excluded. | Common activity reservation/interruption, with eligibility filters before any gathering. |
| Medium N9 | The supposed Guild ward defender family `fc_guild_defender` is never assigned by the mob owner. Its search normally falls back to `mob.kill()`, so the advertised defender participation is absent. | `main.js:931`; `scripts/fc_mobs.py:873–897`. Repository family search returns the query only. | Reconcile ward ownership and presentation; do not claim simulated combat from unconditional removal. |
| Medium N10 | Rest is random stroll; Guildmaster/Maze have no home restrictions, and Will has no magic routine. Training scheduler also invokes terrain and approach repairs every 10 ticks until flags complete. | `gen_behavior.py:422`; `main.js:1265–1268`; `scripts/fc_mobs.py:1010–1012`. | Separate visible character purpose from background adaptation. Decouple runtime repair from activity lifecycle; geometry must pass without hidden repairs. |

## Coupled owners and existing verification

`scripts/fc_mobs.py:873–897` owns definitions, family, health, speed and NPC
appearance; its equipment additions at 971–1012 attach bow/stick geometry.
`scripts/gen_behavior.py:422–462` owns generic NPC movement and the zero-movement,
nonpushable, knockback-resistant training group. Removing an overriding component
group must be validated in Bedrock before claiming baseline speed returns.
`scripts/gen_resources.py:1111–1126` owns animation aliases/controllers;
`scripts/gen_emotes.py:245–342` owns spar/block/archery clips. `scripts/fc_strings.py`
owns exported dialogue strings; inline dialogue remains authored in `main.js`.
Generated JSON/models/animations are outputs and must not be edited directly.

`scripts/tests/test_gen_behavior.py` verifies social events, persistence and the
presence of training-start events, but does not execute a session, retry event
failure or prove walking. `_verify_guild.py:227` inspects training-ground block
flatness. Neither establishes NPC AI execution. GP1's probe adds failure evidence,
not passing behavior acceptance.

## Proposed first GP3 scope

After the first layout pass, implement N1–N4 and the conflicting-activity part of
N8 as one bounded session lifecycle change. Keep existing geometry and role
anchors unless the GP2 owner moves all consumers together. Select only complete
pairs; release a trainee on conversation/follow/combat/night/partner loss; retry
failed stop cleanup; invalidate pending animations/projectiles when an assignment
ends. Remove unconditional station/return teleports. If actual walking cannot be
proved, release normal movement and state that travel to a designated station
remains incomplete rather than masking it with repairs.

Use isolated tests executing production helpers/interval callbacks for normal
session start/repeat/end, failed start and stop events, interaction cancellation,
follow, combat before delayed shot, missing partner, night transition, reload
with old tags, blocked station/failed placement, and entity disappearance.
Regenerate through `gen_behavior.py` only if its owner changes, after its existing
regression passes; inspect targeted output drift. Validate syntax and base/domain
gates. Record player/NPC pathfinding, restored speed, bow display and two-player
damage checks separately as unrun until engine access exists.

N5/N7 resident identity and N6 offender targeting need separately reviewable
changes and compatibility decisions. They remain high priority after the first
door pilot; the initial GP3 pass must not imply that they were solved. Named
story/tutorial roles, Will training, staff and canon dialogue also remain open.

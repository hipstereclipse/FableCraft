# Guild and Demon Door priorities

User override, 2026-09-12: prioritize recursively improving the Guild layout,
NPC behavior and accuracy to the original game, and redesign Demon Doors so an
opened door acts like a Nether portal into its corresponding Fable-style reward
room/world. This supersedes the old breadth-first milestone order. Implementation follows the supplemental checkpoints below. GP1 establishes the
offline baseline; later passes record their own gameplay changes and engine gaps.

## Execution order and recursive improvement

Begin with GP1, then one substantive Guild layout pass (GP2), one Guild NPC pass
(GP3), and a complete Guild Demon Door portal/reward-world pilot (DP1/DP2).
Then repeat Guild and door improvement passes against the largest observed
remaining defects. Keep both priorities advancing: complete the door pilot after
the first Guild layout and NPC passes, then alternate by defect priority. Defer W3.5 and other
unrelated expansion while this priority cycle has actionable work. Required
validation, compatibility and directly supporting animation/VFX work remain in scope.

Each pass: compare references and current behavior → list concrete defects → fix
one coherent group through its owners → regenerate affected assets → test routes,
NPC behavior and interactions → inspect the result → re-evaluate the affected
rooms, adjoining routes and NPCs. Feed discoveries back into the next pass. This
is an iterative quality-improvement cycle. Preserve separate commits, immediate
pushes and fresh handoffs;
continue without routine permission questions. If an engine check cannot run,
record it unrun and advance independent work rather than declaring fidelity done.

Supplemental queue (newly authorized work, outside the legacy 45-leaf scoreboard):

| Pass | Status | Outcome required |
| --- | --- | --- |
| GP1 | done | Offline reference/geometry/NPC/API audit, ranked defects and baseline views; engine observations unrun |
| GP2 | in-progress | First layout pass connects lobby/gallery/dining and Maze stairs; further fidelity and engine walking remain open |
| GP3 | in-progress | First training lifecycle pass fixes repeated teleport/cleanup/interruption defects; navigation, resident identity and targeted defence remain open |
| DP1 | in-progress | Guild lamp/Library Arcanum portal, durable rewards/returns and legacy mouth migration implemented offline; engine acceptance remains unrun |
| DP2 | in-progress | First library grove and four in-room collectibles implemented; other designed worlds and direct TLC comparison remain open |
| GP4 | todo | Integrated Guild/door review, regression checks and next ranked improvement pass |

Record each pass's exact scope, evidence, real commit or SELF resolver, remaining
defects and manual status here. These passes are not completed legacy leaves.
Keep the existing C3 scoreboard accurate; changing its denominator requires a
separate explicit implementation of the expanded scoring contract.

## Guild: design and NPC acceptance

Use the original 2005 Fable: The Lost Chapters as the target. Start with the
architecture, visual_reference, UIofFable and emotes snapshots in
`docs/references/fable-tlc-expert/`; find the referenced Guild build sample in the
original local reference directory if available. Verify contradictory details
and undocumented proportions against actual original-game views, retaining
source provenance. Keep reference-supported features separate from Minecraft
adaptations. Do not treat a renderer's S score as evidence of resemblance.

Audit the campus as a connected place: entrance and main hall, map/quest/skill
and Cullis interactions, library and living spaces, Maze's tower/study, courtyard,
river/islands/bridges and training grounds, cave/Chamber of Fate and Demon Door
approach. Establish adjacency, proportions, elevation, sightlines, architecture,
materials, roofs, interior furnishings and readable routes. Break the audit down
room by room and revisit adjacent spaces after each change. Prioritize serious
layout and silhouette mismatches before decorative detail. Track a reference
comparison and a walk-through for each route, including usable stairs/doorways,
headroom, NPC access and absence of hidden repairs masking bad generated geometry.

For each relevant Guild character and apprentice, document original-game role,
location, dialogue, activity and reaction. Improve training/sparring/archery,
idle activity, interaction interruption/resumption, player proximity and aggression
responses where supported. Distinguish canonical behavior from chosen background
routines; do not invent schedules or dialogue as canon. Audit current station
pinning, periodic teleports, movement freezing, repair sweeps, duplicates after
reload and friendly-fire handling. Aim for purposeful behavior and believable
movement without breaking quest/training interactions. Tests must exercise
state changes and failure paths; static poses do not prove AI execution.

Owners/starting points: `scripts/gen_structures.py` (`guild_hall`, `GUILD_LAYOUT`,
related chamber builders), `packs/Fablecraft_BP/scripts/main.js` (`GUILD`, initialization, station/training and
repair loops), `scripts/gen_behavior.py`, `scripts/gen_resources.py`, `scripts/fc_mobs.py`
and the actual owners of data/dialogue/animation outputs. Never hand-edit generated
entities, models, controllers, HUD or data exports. Run behavior regression before
regeneration and review targeted output drift.

Keep GUILD_LAYOUT, GUILD, interaction/spawn anchors, terrain/cave exclusions,
ticking areas and C2 assertions coupled. Current Maze anchor is (46,12,70): a
baseline to audit, not a ban on a reference-supported redesign. If any anchor
moves, change every owner/consumer and its tests together. Reanchor refreshes
coordinates only; it does not rebuild geometry. Explicitly distinguish new-world
redesign from any versioned saved-world migration; do not silently overwrite an
occupied Guild or revive the obsolete tiling patch.

## Demon Doors: complete destination experience

Current code audit: `doorPersona` defaults to a coordinate-derived table index;
`openDemonDoor` stores `fc_door_open` on the entity, moves the face through
`animateDoorOpening`, and immediately awards items/XP. `ensureAllDemonDoors` can
recreate faces. This is the starting implementation, not portal travel. Audit
`scripts/fc_data.py`, its exporter to `fc_gamedata.js`, the door entity/resource
owners, and these runtime functions before designing replacements.

For every supported door, maintain an explicit stable mapping of door identity,
location/archetype, original challenge, dialogue/personality, opening presentation,
reward realm and reward. Verify the Guild door's own challenge and destination
first. Then map other doors, including existing scattered ones and static
landmarks awaiting functional integration. Preserve story-route exceptions such
as Nostro's onward passage; do not replace them with a generic riddle/reward box.
Do not let coordinate changes or entity recreation silently select a new persona.

Required experience: locked speaking face → correct challenge → opening animation
and a visibly traversable portal → player steps into/dwells in the opening →
transition into that door's individually designed reward world → explore and
collect its reward → return portal restores the exact source door/dimension with
safe facing and clearance. An opened door remains a reusable entrance. Preserve
Fable-style presentation; the Nether-portal analogy describes physical traversal
and transition, not sending every door into the ordinary Nether or relying only
on a menu/instant inventory reward. Reward discovery belongs inside the destination.

Each destination needs distinct reference-led layout, atmosphere, architecture or
landscape, lighting, sound, set dressing, reward placement and exit. Reusing one
undecorated room for every door does not meet this request. Build original assets
through generators. The prototype must verify the installed Bedrock version's
actual dimension/structure/loading APIs against current official documentation;
do not promise arbitrary custom dimensions without proof. If separate custom
dimensions are unavailable, design stable isolated realm spaces in supported
world storage that preserve the distinct-world experience. Keep ordinary-world
scatter; do not turn Albion into a fixed map. Document the chosen storage and
allocation model, bounds and isolation before expanding the room catalogue.

Persist door-to-realm identity, unlocks, generated-room version, reward claims
and source/return dimension/position independently of a replaceable face entity.
Define shared-world versus per-player reward/access semantics explicitly. Handle
already-open legacy doors and already-awarded rewards without resetting progress
or granting duplicates. Build/verify a destination and safe arrival before moving
the player. Handle interrupted generation, unloaded chunks, death/disconnect,
concurrent players, retries and failed teleport; leave a recoverable return path.
Use cooldown/exit clearance to prevent immediate return loops. Confirm that moved
faces and surrounding blocks no longer obstruct the usable portal aperture.

Validate locked denial, correct/incorrect requirements, single consumption,
opening completion, approach from both sides, repeated visits, exact-door return,
missing destination, failed teleport, reload/entity replacement and simultaneous
players. Verify rewards cannot duplicate and separate doors cannot share the
wrong room/return anchor. Exercise portal and reward flow in-engine; mocks and
renders alone leave this priority in-progress.

## Evidence and iteration gate

Use the existing base/world/entity/VFX recipes as applicable, Guild match/roof
and numeric-anchor audits, structure-manifest tests and meaningful NPC/portal
regressions. Save original baseline and new exterior/interior views, reference
comparison notes, route diagrams and actual command results under
`screenshots/validation/<pass-ID>/`. Label cutaways and unrun engine checks.

At every checkpoint, record what improved, what still differs from the original,
what actually ran in-engine, and the next highest-impact defect. Return to the
Guild/door cycle when a pass reveals a related defect. Resume deferred breadth
only after the prioritized deliverables have evidence-backed acceptance, or
when all remaining priority work truly depends on unavailable engine/reference
access; record that dependency and do not mark it done. Merely adding rooms,
passing asset hashes or generating attractive thumbnails does not close this work.

## GP1 — baseline audit (2026-09-12)

Commit: 1ec9286f0859b3be38921594053877a861d779f4.
Baseline audited: f135546cd170f9c96d1e384576e8fb9a11b6f068; that exact head passed
remote CI run 34709848060. This pass changes documentation and evidence only.

The room ledger and baseline views are in [GUILD_GEOMETRY_AUDIT.md](GUILD_GEOMETRY_AUDIT.md);
behavior traces and role/source distinctions are in [GUILD_NPC_AUDIT.md](GUILD_NPC_AUDIT.md);
verified APIs and the portal/legacy contract are in [DEMON_DOOR_DESIGN.md](DEMON_DOOR_DESIGN.md).
Evidence: `screenshots/validation/GP1/`. All 27 base gates and explicit lint, spells,
syntax and Guild diagnostics pass as commands. The roof diagnostic reports 385
overhanging eave cells, despite zero detached blocks. The transcribed-map classifier's
85.3% structural agreement is not a TLC fidelity grade. Baseline route failures and
NPC probe results document defects, not passing gameplay tests. Engine checks unrun.

Ranked execution ledger:

| Rank / defect | Evidence and effect | Next bounded owner pass |
| --- | --- | --- |
| 1 / G-ROUTE | Maze's study and rotunda gallery are clear at their anchors but disconnected from waking point. Tower rails overwrite treads; angular spiral gaps and later roof/bay fills sever circulation. | GP2: connected stair/gallery layout through gen_structures, preserving anchors and existing worlds |
| 2 / N-TRAIN | Half-second station teleports and frozen movement replace believable training transitions; interactions and combat can compete with assignment. | GP3: station/session lifecycle, interruption/resumption and behavioral failure tests |
| 3 / D-PORTAL | Guild face selects invented coordinate persona, pays immediately and moves into rock; no reward destination or return exists. | DP1/DP2: lamp/Library Arcanum pilot, supported isolated storage, durable unlock/reward/return and traversable aperture |
| 4 / N-IDENTITY | Proximity counts cannot identify Guild residents after departure/reload; broad player targeting threatens innocent multiplayer visitors. | GP3 follow-up by risk, coupled runtime/behavior owners |
| 5 / G-FIDELITY | Roof massing/interiors and the Will-island bridge interpretation need closer original-game comparison; current transcribed map has uncertain provenance. | Recursive Guild reference/layout review after first portal pilot |
| 6 / G-CAVE | Runtime cave carving/repair has a separate completion lifecycle from the surface generator and needs integrated route verification. | GP4 integrated cave/Chamber/door review |

GP1 is complete as an offline defect audit. GP2/GP3/DP1/DP2/GP4 acceptance remains
open; no supplemental item changes the original C3 denominator of 45 leaves.

## GP2 — connected Guild circulation (2026-09-12)

Commit: fd95ef16141a2b806cad1146210aea84c71b9dbf.
Replaced rounded, disconnected stair samples and conflicting rail/floor passes
with two-wide continuous half-step flights, corner landings and a three-wide
supported gallery/dining connection. The doorway no longer cuts through a bunk.
The final generator owns those reserved volumes, so later room shells cannot
replace the route. All GUILD/GUILD_LAYOUT interaction anchors, Maze (46,12,70),
footprint and saved-world placement guards remain coupled and unchanged.

Six regression groups inspect final voxel half-slab collision intervals, forward
and reverse routes, both lobby flights, tower turns/deck joins, adjacent ground
arches and independent missing-step/headroom/bridge failures. Added the route
suite to continuous validation. See [GUILD_CIRCULATION.md](GUILD_CIRCULATION.md)
and `screenshots/validation/GP2/` for inspected detail renders and actual results.
Source validation uses an isolated reviewed-index snapshot so parallel unfinished
NPC/portal work is excluded. All 28 base gates and corrected ESM syntax checks pass.
Full screenshot and C2 render pipelines completed; all views are offline.

New placements receive this geometry. Existing occupied Guilds are never reloaded;
reanchor remains a coordinate refresh, so an old world's broken stairs remain a
separate migration task. NPC pathfinding, jumping/collision and complete interior
fidelity are unrun in-engine. GP2 stays in-progress for recursive layout/reference
work. Next: GP3 training lifecycle, then the complete Guild portal/destination pilot.

## GP3 — training lifecycle and interruptions (2026-09-12)

Commit: a61ab803b7ff328313957911b66521cb60d6ff5b.
Eighteen focused runtime groups cover the production controller and actual
main/emote callbacks. Apprentices acquire stations with one collision-checked
placement, hold a session without repeated teleports, and resume roaming in place.
Failed cleanup retries, incomplete pairs release, and conversation/Follow/combat/
night/rest/displacement invalidate queued drills. Harmless archery trails replace
unguarded practice projectiles. One-time placement and the background schedule
are explicitly Minecraft adaptations; walking to marks remains open.

The behavior owner explicitly restores movement, pushability and knockback
components on stop because removing the training group does not restore base
components in Bedrock. Only three apprentice entities were regenerated. The
shared handwritten emote hook preserves social reaction/Follow behavior while
interrupting training. Existing spouse ownership, rewards and quests are retained.
See [GUILD_TRAINING.md](GUILD_TRAINING.md) and `screenshots/validation/GP3/`.

All 29 base gates and explicit lint, spells, ESM syntax and Guild diagnostics
pass in the reviewed-index snapshot. The full screenshot pipeline completed
(51 mobs, 55 items, 130 recipes, 31 structures, 13 galleries); three apprentice
cards were inspected as static visuals only. Uncommitted portal work is excluded.
Engine movement/animation/multiplayer checks remain unrun.
N5/N7 resident identity/repair and N6 innocent-player targeting remain high
priority after the door pilot; no complete NPC fidelity claim is made.

## DP1 — Guild portal and first DP2 destination (2026-09-12)

Commit: SELF: TLC Conformance — DP1: open the Guild door into Library Arcanum.
The Guild uses a stable Lamp/Library Arcanum identity. Lantern use opens a clear
walk-through mouth with a rising, noncolliding face and soul-particle light.
The bounded worker reserves unloaded Overworld storage, scans the entire unused
volume, places/validates the designed library grove and seeds four containers
before admission. No items, XP or reputation are paid at opening. Shared-world
reward depletion never permits regrant or reconstruction of a visited room.
Per-player approach tickets support checked travel and return, retries,
cooldown/rearming, reload/death and orphan recovery. Ordinary procedural doors
and Nostro's story gap retain their existing separate behavior.

The source generator provides a 3×4×9 throat; an independently frozen GP1
fingerprint permits a strictly bounded existing-mouth clear and preserves its
floor. Foreign blocks refuse migration; identical replacement block types cannot
be distinguished from the generated original. Whole Guild geometry and existing
progress are preserved. The entity owner removes door gravity/pushing/leashing
and disables open collision. Only the door entity and targeted source/destination
assets/data were regenerated. The new room is fixed, absent from scatter/loot/
Cullis registration. C2 now covers 35 assets/renders (28 scatter, 3 fixed, 4 legacy).

See [LIBRARY_ARCANUM.md](LIBRARY_ARCANUM.md) and `screenshots/validation/DP1/`.
All 34 base gates passed in an isolated reviewed-index snapshot. The full
screenshot pipeline completed (51 mobs, 55 items, 130 recipes, 32 structures,
13 galleries). Static source-front/rear and grove views were inspected. The direct TLC camera
comparison, collision/lighting/loading/content-log tests, crash persistence and
multiplayer engine acceptance remain unrun. All GP/DP acceptance stays separate
from C3's original 45-leaf scoreboard. GP4 next revisits resident identity,
offender-specific defence, cave/Chamber routes and portal integration failures.

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
| GP4 | in-progress | Offender-specific Guild defence and projectile attribution fixed offline; integrated cave lifecycle/route defects reproduced; engine acceptance remains open |
| GP5 | in-progress | Resumable new cave/Chamber construction, Library threshold, concentric altar steps, water containment and recognized Cullis height correction; legacy geometry preserved; engine acceptance open |
| GP6 | in-progress | Durable resident identities, conservative legacy adoption and checked new births replace proximity respawn; engine acceptance open |
| DP3 | in-progress | Original-cell ticket return survives lost/recreated ledgers; unknown paid history defers registration; full standing return clearance; engine acceptance open |
| DP4 | in-progress | Durable source owns Guild face maintenance; stale hints cannot spawn ordinary doors or reset history; engine acceptance open |
| GP7 | in-progress | Retired obsolete approach/scarecrow sweeps preserve saved construction; generated routes and training remain checked; engine acceptance open |
| GP8 | in-progress | Pointed Chamber wall bays, subdued masonry and clear outer walk; recognized older construction resumes its original plan; engine acceptance open |
| GP9 | in-progress | Dedicated Will-island lightning drill and discipline-specific staffing; checked effects stop on interruption; engine acceptance open |
| GP10 | in-progress | Low wood-framed terrain map replaces random jewel mosaic and beacon; all adjacent interactions preserved; engine acceptance open |
| GP11 | in-progress | Broad Library/Store arches remain open after removing redundant indoor tunnel shells; floors and adjoining routes preserved; engine acceptance open |
| GP12 | in-progress | Continuous framed Library bookcases, accessible reading desk and supported lamps; spine/cave/commons routes preserved; engine acceptance open |
| GP13 | in-progress | Restore one erased NE dormitory top stair; complete bounded ascent/descent with all other campus cells preserved; engine acceptance open |
| GP14 | in-progress | Neutral-reference Chamber inset panels, colored window strips and grey/ochre paving; GP5/GP8 enrolled construction plans preserved; engine acceptance open |
| GP15 | in-progress | Framed scenic archery backboard from two inspected original views; final-voxel firing lanes and adjoining door/gate routes preserved; engine acceptance open |
| GP16 | in-progress | Live Skill target/support and complete firing-lane preflight before acquisition and delayed release; native acceptance open |
| DP5 | in-progress | Occupied original-ticket rooms retain block/explosion and world-generation guards after lost/replaced ledger; own-cell return clicks revalidate; native acceptance open |
| GP17 | in-progress | Deferred relationship actions revalidate current requester/ownership/eligibility before mutations; competing proposals cannot steal ownership or consume twice; native acceptance open |
| GP18 | in-progress | Supported Maze-study bookcase and red carpet accents from inspected original views; preserve surveyed routes, anchors and all unrelated campus cells; native acceptance open |
| GP19 | in-progress | Requester-owned Follow/Wait for the two canonical Skill residents with durable cleanup and social/training/defence arbitration; native acceptance open |
| DP6 | in-progress | Preserve exact return tickets during unavailable reads; retain confirmed absent/corrupt fallback and independent occupied-room guards; native acceptance open |
| GP20 | in-progress | One reference-led framed red dormitory wall bay replaces ten existing solid materials; routes, room fixtures and saved geometry preserved; native acceptance open |
| DP7 | in-progress | New Gorge instances open into a separately authored Arboretum with witnessed challenge, physical shared Pickhammer, bounded allocation and exact-source return; native acceptance open |
| DP8 | in-progress | Independent realm maintenance/tick boundaries preserve healthy Arboretum dwell returns through failed Guild claim writes; native acceptance open |

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

Commit: 60513c808c2c3f1dc5de14ce497770aa7c9d6cf2.
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

## DP2 — first original-image review and grove ground refinement (2026-09-12)

Commit: 91f46b92d324e2e53dae5493bc298648e8e10e31.
A contemporary 2005 guide image explicitly labeled Library Arcanum is now
verified and compared at its native 207×153 resolution. See
[LIBRARY_ARCANUM_REFERENCE_REVIEW.md](LIBRARY_ARCANUM_REFERENCE_REVIEW.md).
All external pixels remain ignored reference scratch. The image supports earthy,
irregular ground; it cannot establish complete room proportions or unseen sites.

The original room builder now uses irregular earth/grass patches instead of the
formal paved garden. Exactly 426 local-y2 surface materials change. Every other
voxel, all portal/reward coordinates and the persistent v1 contract are unchanged.
Old ready/visited rooms are preserved. This bounded refinement was inspected;
matching player-height lighting, complete original footage and broader
room fidelity remain open. `screenshots/validation/DP2/` records the exact delta
and offline results. All 34 base gates and explicit lint/spells/syntax/Guild
diagnostics pass in the reviewed-index snapshot. The full screenshot pipeline
completed with 51 mobs, 55 items, 130 recipes, 32 structures and 13 galleries.
GP4 offender-specific defence is the next code pass.

## GP4 — Guild defence and integrated cave review (2026-09-12)

Commit: cd6815facd1312f7659fd64296d0f5167ce9b018.
Guild combat now requires an identified player offender. Active local warrants
and short attributed provocations feed one aggregate controller, so clearing one
player's warrant does not calm defence against another. Portal departure/return
updates eligibility, stale/failed cleanup retries, and social Follow/Watch plus
spouse fields survive. Projectile deaths use the actual owner, never a nearest-
player guess. The six defender entity outputs explicitly restore base combat
components after stop. See [GUILD_DEFENCE.md](GUILD_DEFENCE.md).

Fourteen focused production controller/callback groups, eight behavior owner
groups and the existing training/runtime suites pass. All 35 base gates plus
explicit lint, spells, ESM syntax and Guild diagnostics pass from an isolated
reviewed-index snapshot. The full screenshot pipeline completed (51 mobs,
55 items, 130 recipes, 32 structures and 13 galleries); six defender cards are
unchanged static visuals, with representative cards inspected.
The independent implementation review found no introduced blocker. These are
offline results; target selection, dropping, movement and multiplayer engine
acceptance remain unrun. N5/N7 resident identity/repair remains a separate defect.

The [integrated cave audit](GUILD_CAVE_REVIEW.md) executes frozen actual callbacks
against generated Guild/Chamber voxels. It proves completion is recorded before
any cave write, interrupted/unloaded carving never retries, and annex placement
has no maintenance caller. It also finds a missing library threshold floor,
incorrect Chamber Cullis registration height and three jump-required hill rises.
The old mirrored cave verifier reports PASS despite the real threshold defect.
These findings are reproduced gaps, not implemented cave fixes. Next priority:
a conservative cave lifecycle/verification owner and its actual-callback tests,
followed by coupled threshold/Cullis fixes and persistent resident identity.

## GP5 — cave lifecycle and Chamber access (2026-09-12)

Commit: f7fb3f97c7932e461bd49336d7dee905ae1e4b47 (pushed).
The cave owner now distinguishes new enrolled construction from legacy occupied
worlds. Durable original-cell snapshots and verified progress support conservative
retries, with completion recorded only after final geometry verification. Ordinary
maintenance owns retries; the broad delayed Chamber scrub is removed. Generated
Chamber permutations and an exact surface entrance crop supply the runtime plan.

The Library threshold keeps its floor. Per the user's explicit correction,
184 changed tread cells form concentric steps around the entire altar with six
half-block rises to the unchanged dais. Another 44 glass cells contain the formerly open skylight
water perimeter. The generated local Cullis feet y5 correct the old y7 registration
only for the recognized old point with valid core/ring and arrival clearance.
Existing geometry, progress, inventory and custom registry coordinates survive.

See [GUILD_CAVE_LIFECYCLE.md](GUILD_CAVE_LIFECYCLE.md) and
`screenshots/validation/GP5/` for final route, lifecycle, migration and original-guide
comparison evidence. The current Chamber still differs substantially in center
material contrast, wall ribs/murals and lighting (partial visual C).
Manual movement, fluids, native state updates, loading and crash persistence remain
unrun. Legacy interrupted caves need a separate conservative migration; no blanket
recarve is introduced. Next: persistent resident identity/repair, then return to
Guild/door reference refinement and pilot integration defects.

GP5 validation: all 38 base gates pass from a reviewed-index snapshot, including
20 lifecycle, 10 Chamber route, 6 Cullis migration and 16 C2 contract groups.
Explicit lint/spells/ESM/Guild diagnostics pass. The full rendering pipeline
completed 51 mobs, 55 items, 130 recipes, 32 structures and 13 galleries.
The first base run exposed the outdated bulk-placement-only C2 registration
reader; its owner/manifest edge and independent negative fixtures are now fixed.
Initial failed logs are retained. No live engine acceptance was performed.

## GP6 — persistent Guild resident identities (2026-09-12)

Commit: 0343a963d49cb480804009e9aa6f30583541430c (pushed).
Twelve durable slots replace nearby type-count population repair. A spouse or
other resident leaving with one Hero is not duplicated while another remains
at the Guild; unavailable IDs, removal and unloading retain ownership. Confirmed
deaths leave tombstones. Fresh founding persists enrollment before placement,
and native spawn intent before birth; failed marker/save operations recover
bookkeeping without another native attempt. Duplicate or inconsistent slot
claims reserve a persistent conflict rather than authorizing an extra resident.

Legacy adoption records marker/tag/inferred provenance and preserves each
original entity's spouse, Follow, name, social state and player progress.
Unmarked generic traders/guards and unknown missing historical residents remain
unresolved. No resident is deleted, replaced or teleported home; unmarked spawn
intent after a crash may remain reserved indefinitely. Identity is an adaptation
with explicit migration limits, not a canonical role/schedule implementation.

New births use checked column centres within two blocks at the authored height,
with no floor/headroom/furniture repair. Production final-voxel checks find all
12 safe candidates, including sequential occupancy by prior births. Maze keeps
its audited home (46,12,70); centre placement fixes its old four-column straddle.
Adjacent safe births avoid Guildmaster map furniture, guard gate masonry and a
Skill hall stair. Existing misplaced residents remain unchanged.

Twenty-two focused groups execute the production controller and actual founding,
maintenance/load/remove/death callbacks, including two Heroes, failed native
spawns/saves, unload/reload, competing marker claims and corrupt registry data.
See [GUILD_RESIDENTS.md](GUILD_RESIDENTS.md) and screenshots/validation/GP6/.
Engine collision/loading, save/crash durability, spouse owner targeting and NPC AI
timing remain unrun. Named/tutorial staffing, Will-island routines and walking to
training remain priority work. Next: repair reproduced Guild portal return/history
integration defects, then continue reference-led Guild/door refinement.

GP6 passes all 39 base gates from `tmp/conformance/GP6-reviewed-snapshot`, including
22 resident, 18 training, 14 defence and 20 cave groups. Base validation includes
ESLint and the spell suite; all 62 BP JavaScript files also pass ESM syntax checks.
The static Guild diagnostics reuse GP5 results with byte-identical dependency
hashes recorded in additional-results.json. The full screenshot pipeline completed
51 mobs, 55 items, 130 recipes, 32 structures and 13 galleries. All six representative
NPC card hashes match GP4; Guildmaster, Maze and Will apprentice were inspected.
No generated appearance outputs changed and no engine acceptance is claimed.

## DP3 — Guild portal return and history recovery (2026-09-12)

Commit: 37c8d98a5ce47aa861f311c34c36fc99af22e7e2 (pushed; exact-head CI 34717404106 passed).
A committed visitor can use the original exit even after normal source maintenance
recreates a missing primary record with no room or a different cell. The same
walk-through return works while the primary record is missing, corrupt or throws
on read, including a lone visitor with nobody near the Guild. Recovery requires
valid ticket fields and actual occupancy of its exact Overworld cell; it uses
only the original source and preserves failed tickets. No room/reward/unlock
reconstruction is authorized by recovery.

A transient surviving-face history read now defers registration instead of
classifying an already-paid face as unpaid. Return clearance covers every cell
intersecting the standing height above fractional feet, allowing an obstructed
jumping approach to choose the existing same-door fallback. Module ownership,
actual callback failures/negatives and limits are documented in
[LIBRARY_ARCANUM_RECOVERY.md](LIBRARY_ARCANUM_RECOVERY.md).
The room asset/version, canonical challenge and shared native rewards are unchanged.
Manual Bedrock loading, collision, metadata and crash checks remain unrun.

DP3 passes all 39 base gates from `tmp/conformance/DP3-reviewed-snapshot`, including
19 actual portal adapter groups, 13 generated-room runtime groups, 4 aperture
migration groups and all Guild cave/resident/training/defence suites. ESLint and
spells are included in the base gates; all 62 BP scripts also pass ESM syntax.
Independent review of the no-ledger exit path found no remaining blocker after
adding unticketed/invalid-ticket periodic negatives. No visual asset or rendering
owner changed: the GP6 full rendering pipeline and GP5 Guild diagnostics are
reused with byte-identical dependency hashes in additional-results.json.
Both GP5 and GP6 exact-head remote CI passed. All live Bedrock acceptance is unrun.

## DP4 — single Guild door source authority (2026-09-12)

Commit: 407e0ce0e779bbee772485d7a3b319931d86eab6 (pushed; exact-head CI 34718207560 passed).
The durable pilot source now owns face lookup, replacement, proximity scheduling
and dimension selection. The old hint is used only before initial registration
and to quarantine stale Guild positions from ordinary challenges/payouts. It is
never rewritten; no reanchor, geometry replacement or progress reset occurs.
Corrupt/unreadable primary history defers repair. Distant stale faces remain
untouched because their ownership is uncertain. Actual-adapter regressions
reproduce four prior failures and cover 25 final groups, including dimension
conflicts and unavailable scans. See [LIBRARY_ARCANUM_SOURCE_AUTHORITY.md](LIBRARY_ARCANUM_SOURCE_AUTHORITY.md)
and `screenshots/validation/DP4/`. All engine acceptance remains unrun.

The next recursive audit reproduced destructive obsolete Guild approach/scarecrow
sweeps when old completion flags are absent. Current generated collision volumes
already satisfy those clearances; retire the obsolete writes separately in GP7.
NPC Follow/Wait ownership, Will-island routines and reference-led Chamber wall/
lighting refinement remain ranked work after that saved-world defect.

DP4 validation: all 39 base gates pass from the isolated reviewed-index snapshot,
plus 25 adapter groups and ESM syntax for all 62 BP scripts. Lint, spells, Guild
lifecycle/NPC gates and C2 are green. GP6 full renders and GP5 Guild diagnostics
are reused with matched dependency hashes; no visual owner changed. Independent
source-authority review found no blocking defect. Live engine tests remain unrun.

## GP7 — preserve saved Guild approach and training construction (2026-09-12)

Commit: f12b608e84bd4774caf6a39f4b2ba708ef71821b.
The actual old maintenance callback repaved a player diamond floor and erased a
chest when its legacy completion flag was missing. One unrelated unloaded cell
left the flag absent and repeated those destructive writes on later passes.
The second obsolete helper also removed player hay/pumpkins at old training
sites. GP7 removes both helpers and their calls; old flags remain stored unchanged.
Missing or false flags never enroll a new geometry migration.

Final generator inspection shows the old approach helper supplied no remaining
collision/headroom repair: only seven cosmetic cobble variants differed. Both
approaches, bridge aprons, source throat and ring/island clearance are already
owned by final generated geometry. No regeneration, anchor change, old-world
recarve or room/reward modification is introduced. Existing obstructed training
marks are preserved and refused by the actual session controller.

Eight actual-maintenance groups and four Python wrapper/geometry groups cover
foreign containers/materials, reload/retry/failures, old flags, blocked/clear
training, both-direction routes and independent missing-floor/headroom failures.
See [GUILD_MAINTENANCE.md](GUILD_MAINTENANCE.md) and `screenshots/validation/GP7/`.
The protection claim covers these two retired helpers only. Other terrain/skirt
repairs remain outside this pass and are mocked as adjacent owners in the new
suite. Legacy geometry migration still requires a separate provenance audit.
Live Bedrock loading, movement, saving and collision acceptance remains unrun.

GP7 validation: all 40 base gates pass from `tmp/conformance/GP7-reviewed-snapshot`,
including the new maintenance gate, all Guild lifecycle/NPC/door gates, lint and
spells. All 62 BP scripts pass ESM syntax. Independent review found no blocker.
GP6 full renders and GP5 Guild diagnostics are reused with byte-identical reviewed
snapshot dependencies. DP4 exact-head CI 34718207560 passed. Native checks remain unrun.

Next NPC source audit: the generated reaction_follow goal accepts any player;
spouse/emote Follow callers do not bind its requester. Wait removes reaction
components but leaves base random strolling, and the functional Wait emote sends
neutral to every nearby NPC. A pending spouse form callback also needs ownership
revalidation before action/success. This is a source-level finding, not an engine
repro. A separate activity owner should preserve resident/spouse identity and
arbitrate requester-specific Follow/Wait with training and defence; avoid permanent
taming or repeated-teleport shortcuts. Keep canonical staffing and reference-led
Will/Chamber work open alongside these behavioral repairs.

## GP8 — Chamber wall architecture and construction continuity (2026-09-12)

Commit: 444aef6e59403d0664ca8e872f64a45e841eceb7.
Original TLC battle views support pointed wall ribs, dark paving and broad curved
altar steps. The new generator replaces isolated quartz/gold posts, colored
placeholder panels, low fires and the luminous roof with attached pointed stone
bays, dark masonry and elevated lamps. All 116 outer-walk cells connect to the
entrance; 13 were previously obstructed. All 4,419 protected foundation, altar,
entry and containment cells remain exact. The user's surrounding shallow steps,
all anchors and the existing water/glass containment remain unchanged.

A frozen GP5 manifest lets already-enrolled construction finish its exact original
plan after this revision. It requires matching hash/count and the existing
original-cell journal; unknown plans and changed player cells defer safely.
Completed and legacy occupied rooms remain untouched. Arbitrary vanilla painting
injection is retired for new construction; saved painting entities remain.
See [GUILD_CHAMBER_INTERIOR.md](GUILD_CHAMBER_INTERIOR.md) and
`screenshots/validation/GP8/` for before/after views, reference provenance and the
old-controller failure reproduced before the fix. Eight bays and lamp positions
are adaptations, not recovered measurements. Frescoes, neutral lighting, the
central Cullis palette and full native appearance remain open.

GP8 validation: 40 base gates, 23 cave lifecycle groups, 14 Chamber geometry
and manifest groups, and all 62 script syntax checks pass from the reviewed-index
snapshot. Fresh 35-asset C2 and all-category renders (51 mobs, 55 items, 130 recipes,
32 structures, 13 galleries) completed, with fresh Guild diagnostics. Independent
compatibility review found no blocker. GP7 exact-head CI 34718493910 passed.
All Bedrock movement, light, fluid, saving and gameplay acceptance remains unrun.
Next: the dedicated Will-island routine and low main-hall map relief, followed by
continued reference/route review across adjoining rooms and NPC activity ownership.

## GP9 — dedicated Will-island practice (2026-09-12)

Commit: 99f4e4f21b4dcbd33ae99a8116d3aed4f9d62b34.
The original TLC manual explicitly places lightning practice at magic-response
dummies on the island. The actual previous scheduler left Will apprentices idle
or recruited them into the Might sparring pair when one swordsman was absent.
Now each discipline fills its own role. One Will apprentice acquires a checked
island mark and performs a finite casting pose with four harmless blue pulses.
Its model loses the training stick; Might and Skill accessories remain unchanged.
The timing, anonymous staffing and one-time station placement are adaptations.

Every pulse rechecks its session, eligibility, support, dummy and clear lane.
Follow/conversation, defence, rest/night and edited or unavailable geometry cancel
pending effects. The routine never casts a player spell, damages anything, awards
rewards or repairs player blocks. Resident identities/social history are preserved.
Only a new Guild receives the one-cell dirt mark. Old unrecognized marks refuse
practice; no saved-world repaving is introduced. All existing anchors, including
Maze, stay fixed. The Will mark and target are coupled across geometry/runtime/C2.

See [GUILD_WILL_TRAINING.md](GUILD_WILL_TRAINING.md) and
`screenshots/validation/GP9/`. Twenty-five training groups and three generated-voxel
Will groups include interrupted callbacks, failed placement, changed/unavailable
cells and numeric-anchor negatives. Forty-one base gates and all 62 script syntax
checks pass in the isolated reviewed-index snapshot. Targeted model/client/texture/
animation/structure regeneration, fresh C2/full renders and Guild diagnostics are
recorded with exact output hashes. Independent review found no blocker.
GP8 exact-head CI 34719947130 passed.
Live facing, pose blending, particles, navigation, collision and save/reload remain
unrun. The finite pose can outlast cancelled pulses briefly; reactive dummy
animation, player lessons and walking to training marks remain open.
Next: the main-hall map relief and broad Library/Store connections, then further
connected-facility reference review and requester-specific NPC activity ownership.

## GP10 — low main-hall relief map (2026-09-12)

Commit: cf646628b65ef2ba26d0280102965bc11e3f0970.
Three inspected original TLC views show a low polygonal wooden frame with earthy
terrain and teal water, open beneath the hall's twin stairs. The new authored map
replaces random jewel blocks and a central light column with connected land, a
recessed bay and a low wood rim. The coarse coastline and block palette remain
Minecraft adaptations; exact geography and native warm lighting are unverified.

Only 38 final voxels change, all inside existing map furniture. All 37 historical
random draws remain consumed, and the entire rest of the campus is identical by
normalized block/state comparison. The table floor footprint, surrounding routes,
three quest lecterns and Guildmaster birth/interaction anchors remain unchanged.
Saved Guilds retain their geometry and progress; this has no runtime migration.

See [GUILD_MAP_TABLE.md](GUILD_MAP_TABLE.md), four inspected native-slab detail/
hall-cutaway views and source provenance in `screenshots/validation/GP10/`.
Six focused groups test the terrain, footprint, approach routes and complete
campus scope, including independent broken rim, beacon and random-drift failures.
Forty-two base gates and all 62 script syntax checks pass in the isolated reviewed
snapshot. Only the Guild structure is regenerated; fresh 35-asset C2, full renders
and Guild diagnostics complete. Independent review found no blocker.
All native lighting, eye-height comparison, NPC movement and quest interaction
acceptance remains unrun. GP9 exact-head CI 34720288462 passed.
Next: broad Library/Store joins, supported Library
bookcases/reading furnishings, then continued whole-facility reference review.

## GP11 — broad Library and Store connections (2026-09-12)

Commit: e421d237d9d6c3640d239af1a447fe33675d126b.
The final generator built narrow windowed tunnels underneath its own broad room
arches and full-height bay roofs. Their inner walls and low caps obstructed eye
height and left a single centre lane. The finish pass now retains only the flush
floor; the existing joined rooms own their walls and roofs. Three continuous
lanes, the eight-wide Library opening and six-wide Store opening remain clear.

Exactly 64 final cells change inside the two obsolete shells. Every floor and
outside cell/state remains identical, with all 48 historical random draws retained.
Existing room/stair/quest/resident/cave anchors and surrounding routes are fixed.
New Guild generation only; no occupied-world recarve or progress/state change.
Original TLC views support connected arched interiors; exact arch measurements
remain adaptations. Grey stone is retained because warm lighting alone cannot
establish a different original wall material.

See [GUILD_HALL_LINKS.md](GUILD_HALL_LINKS.md) and `screenshots/validation/GP11/`.
Seven focused groups reproduce the prior obstructed width/arches and reject
blocked lanes, missing support, low caps and RNG drift. Six inspected before/after
views show the Library, Store and joined hall. Forty-three base gates, all 62 ESM
syntax checks, fresh C2/full renders and Guild diagnostics pass from a separately
reviewed snapshot; its source was verified against the staged checkpoint index.
Native movement, two-Hero passing, lighting and NPC navigation remain unrun.
GP10 exact-head CI 34720599204 passed.
Next: supported Library bookcases/reading furnishings and the northeast dormitory
stair's missing final transition, then continued whole-facility comparison.

User reference steering (2026-09-12): find additional online photographs/screenshots
throughout this cycle. GP11's `additional-online-references.json` records four
newly inspected TLC PC training/hall screenshots with visible 2011 watermarks.
Their masonry melee ring/wooden gate, archery rails/scenic backboard and straw
Will targets provide more precise next-pass comparison; terrain, dimensions and
neutral light remain uncertain. Keep searching original Library, sleeping-room,
Maze and courtyard views. Reject Anniversary, sequels and reboot imagery as TLC
geometry evidence. Original reference pixels remain ignored, never pack assets.

## GP12 — grounded Library bookshelves and reading furnishings (2026-09-12)

Commit: bf5768b70f02e5126eaaaed516028a15eb0b296e.
The original generator left disconnected upper shelf bands and lost its sole
hanging lamp during final decoration because the lamp had no ceiling support.
The Library now has continuous timber-framed bookcases, a narrow supported
reading desk and four lamps mounted beneath connected solid brackets. All three
existing lecterns retain their positions and facing. The central five-wide spine,
west commons doorway, cave approach and resident access remain clear.

Exactly 141 final fixture cells change. Every other campus block/state, room
shell, floor, anchor and shared random sequence stays unchanged. Sixty bookshelves
replace 44 separated shelf blocks; the desk has seven half-slabs and three legs.
New Guilds only: no saved-room rewrite or resident/progress reset.

The 2005 Prima Library image and additional original-TLC Library cutscene views
support tall continuous framed shelves and open arched access. The newer views
show a burning story state, so they do not establish neutral room lighting or
exact desk layout. Desk/lamp dimensions and placement remain explicit adaptations.
See [GUILD_LIBRARY_INTERIOR.md](GUILD_LIBRARY_INTERIOR.md) and
`screenshots/validation/GP12/` for six inspected before/after views and provenance.

Six focused groups reproduce detached shelf bands/missing light and test fixture
support, desk/lectern access and all adjoining routes; blocked paths, missing
floor, broken bands/brackets and unrelated-campus changes fail independently.
Forty-four base gates, all 62 ESM syntax checks, fresh C2/full renders and Guild
diagnostics pass in a reviewed snapshot matched to the staged source. Additional
online reference URLs/hashes/observations are retained as text; source pixels
remain ignored. Native texture/light/collision/interaction acceptance is unrun.
Next: the one-cell northeast dormitory stair repair and further reference-led
training/Chamber refinements from the new photos, keeping native unknowns open.

GP12 online evidence adds 16 distinct inspected screenshots across Library,
Chamber, hall, training and entrance views; see [GUILD_ONLINE_REFERENCES.md](GUILD_ONLINE_REFERENCES.md).
Their stronger neutral Chamber detail now drives the next GP14 wall/paving pass;
keep the older enrolled GP5/GP8 manifests available. GP11 exact-head CI 34721007299
passed. Dorm/Maze neutral interior views remain an explicit search gap.

## GP13 — northeast dormitory final stair transition (2026-09-12)

Commit: fd6c85238e9eb0a50493ab5385b01ebbcf76182f.
The upper deck's stairwell cut removed the original final stair course. The
highest surviving tread ended one full block below the bedroom landing. Restore
only its outer west-facing oak stair at local (86,5,11), after rug furnishing, on
the existing carriage. Exactly one final voxel changes; all lower steps, newel,
bunks, deck, roof, anchors, outside cells and random state remain identical.

The focused survey extends GP2's vertical collision intervals to half-cell
horizontal samples for straight native stairs. The before fixture has no route
to upper feet y6; the repair permits a 21-node route in both directions with no
rise above 0.5 blocks. Perpendicular same-height stair neighbors are rejected so
unknown corner shapes cannot silently enter the model. Gate and three bedroom
approaches compose with the route. This proves a single bounded route, not two
full-width stair lanes or native entity steering/collision.

Six focused groups reject a missing top tread, blocked headroom and reversed
facing, and verify exact scope/RNG. Four inspected before/after views use native
stair half geometry and thin drawn carpets. See [GUILD_DORM_STAIRS.md](GUILD_DORM_STAIRS.md)
and `screenshots/validation/GP13/`. Forty-five base gates, all 62 ESM syntax checks,
fresh 35-asset C2, full renders and Guild diagnostics pass in the isolated reviewed
snapshot. Independent review found no blocker. Official docs verify state names
and value ranges; cardinal numeric mapping follows the existing repository owner.
Native width, turn steering, carpet contact and ascent/descent remain unrun.
No saved-world recarve or geometry migration is introduced. Additional original
room photos are still missing; this is an access repair, not a canon staircase
reconstruction. Next: GP14 Chamber details/paving from newly inspected neutral
photos, then the reference-supported archery training backdrop/fixtures audit.

GP12 exact-head CI 34721620599 passed. GP15 now implements the inspected archery
scenic backboard in a separately checked clear volume; no continuous rails yet.

## GP14 — Chamber detail from clearer original screenshots (2026-09-12)

Commit: 569b3f2119390af2e19160ef52e2aa2072ff2cda (pushed; exact-head CI 34722255501 passed).
The newly inspected neutral TLC Chamber view resolves nested pointed frames,
small carved medallions, narrow colored windows and grey/ochre paving. These
replace GP8's undifferentiated dark floor and simple inner panels. Only 381 cell
values change: 173 floor and 208 wall-detail cells. Every air/solid classification,
all 4,419 protected altar/entry/foundation/containment cells, all 116 outer-walk
cells, anchors, roof and lamps remain exact. The bands and carved blocks are
coarse adaptations; figurative glass, story frescoes and native light remain open.

The exporter now retains both exact frozen GP5 and GP8 construction manifests.
Actual controller tests resume each historical plan from snapshot, applying and
verification interruptions, preserving original cell states and journal identities.
Edited/unknown history, changed completed cells/permutations and missing/corrupt/
wrong-hash journal pages defer. No runtime controller change, occupied-room
migration or duplicate reward/art write is introduced.

See [GUILD_CHAMBER_NEUTRAL_DETAILS.md](GUILD_CHAMBER_NEUTRAL_DETAILS.md) and
`screenshots/validation/GP14/`. Eighteen Chamber groups and 25 cave lifecycle groups
include independent geometry/history failures. Forty-five base gates, all 62 ESM
syntax checks, targeted Chamber/DATA regeneration, fresh C2/full renders and Guild
diagnostics pass in the isolated reviewed snapshot. The shared renderer gains
only missing approximate colors; glass remains opaque in offline previews and
fine carved textures are absent. Exact generated and rendered drift is recorded.
GP13 exact-head CI 34721823290 passed. All native appearance, movement, persistence
and gameplay checks remain unrun. Next: the photographed archery scenic backboard,
then adjoining grounds/NPC behavior and unresolved original-view comparisons.


## GP15 — the archery range's painted landmark (2026-09-12)

Commit: 17d1191e73d830ad4c809d2f6af62b724465eede (pushed; exact-head CI 34722859754 passed).
Two inspected original TLC training photos show a framed painting of purple
mountains, a wooded valley and sky behind the targets. An original coarse block
mosaic now restores that recognizable range prop. It is a Minecraft adaptation,
not copied screenshot art or a measured reconstruction. Continuous braced rails
remain deferred until their circulation footprint is measured.

Only 54 formerly empty cells at x80..88,y1..6,z30 change. The frame rests on the
unchanged floor, behind the active target and between the two south doors.
All other final campus voxels, shared RNG, dummies, target blocks, runtime
anchors and Maze (46,12,70) remain exact. Tests survey both sides/rear passage,
complete gate routes to both rooms and training marks, and the actual Skill
callback's six-particle line. Existing Will, maintenance and training contracts
remain checked. No saved-world reconstruction or runtime migration is introduced.

See [GUILD_ARCHERY_BACKBOARD.md](GUILD_ARCHERY_BACKBOARD.md) and
`screenshots/validation/GP15/`. Six focused groups include missing support/frame,
headroom, path and firing-line negatives. Four before/after renders show the
landmark and adjacent range; flat colors and simplified furniture remain offline
approximations. The 46-gate reviewed-snapshot suite, 62 ESM syntax checks, targeted
Guild asset regeneration, fresh 35-asset C2, full renders and Guild diagnostics
all pass offline. Only the Guild asset and its C2 image change; the other 34
assets/images remain exact. Full rendering produced 281 PNGs with 277 audit
rows and no renderer flags. Independent source/reference/visual review
found no blocker. GP14 exact-head CI 34722255501 passed.

The production Skill callback still lacks a runtime block-lane preflight; this
fixture preserves its ray rather than adding that behavior. Player lessons,
moving/scored targets, reactive straw dummies, purposeful walking and native
lighting/collision/AI remain open. Continue adjoining grounds, Follow/Wait
ownership, roof/interior reference comparisons and the retained Demon Door
priority. A passing cutaway does not establish whole-facility TLC fidelity.

The final bounded reference follow-up found two additional original-TLC Maze
study angles and a partial dormitory wake-up background. The ledger now contains
19 distinct inspected images. Round lattice window, red wall panels, tall shelves,
timber gallery and rug details are visible; exact study dimensions and neutral
wide dormitory/Library interiors remain unresolved. See GUILD_ONLINE_REFERENCES.md
and GP15/interior-reference-followup.json. No additional geometry was inferred
from these last images in this checkpoint.

The final [facility follow-up audit](../screenshots/validation/GP15/facility-followup-audit.md)
reproduces the Skill callback's missing live target/lane preflight and ranks
purposeful station arrival and three reactive Will dummies next. These remain
existing defects/adaptations; no new GP15 route blocker emerged.


## GP16 — live Skill target and firing-lane preflight (2026-09-12)

Commit: e5cf6069d22b6bda767e2face677d4caf6db28ee (pushed; exact-head CI 34730475595 passed).
The GP15 production probe still drew six particles through a chest or toward a
missing target. The Skill scheduler now checks the authored target, its hay
support and complete ray before station acquisition. Each delayed release checks
its current session first, then rechecks the live target and every crossed cell.
Exact segment/voxel clipping avoids gaps from fixed-distance samples when a
trainee shifts slightly. Edited or unavailable cells cancel the drill through
the existing interruption and cleanup owner; no saved block is repaired.

The six harmless particles, bow sound, source/target coordinates and background
cadence remain explicit adaptations. No geometry, generated asset, session
controller, resident/social identity, reward or damage behavior changes. Existing
Will checks and all anchors, including Maze (46,12,70), remain unchanged.
See [GUILD_SKILL_PREFLIGHT.md](GUILD_SKILL_PREFLIGHT.md) and
`screenshots/validation/GP16/` for before/after production probes, regressions,
reference follow-up and independent review. Native acceptance remains unrun.

Forty-six base gates, all 62 ESM syntax checks, fresh 35-asset C2/full renders
and Guild diagnostics pass in the isolated reviewed-index snapshot. Thirty-three
training groups and six archery groups cover actual callbacks/final voxels.
Independent review found no blocker; its 2,109-displacement probe also passed
11,099 crossed-cell negatives. All 35 structure assets, 35 C2 images and 281 full
rendered PNGs match GP15 exactly. GP15 exact-head CI 34722859754 passed.

Seven newly inspected original-TLC images bring the supplementary corpus to 26.
A wide dormitory gameplay image posted in April 2013 shows red-covered beds,
red timber-framed walls, pointed windows, diagonal paving and separate rugs;
complete dimensions, bed count and calibrated light remain open. Further
archery, bridge and hall views refine the next fixture comparisons. The bounded
Maze-study audit identifies window/rug/bookcase/furniture differences without
inferring the full gallery. Neutral ordinary Library views remain missing.

The independent [door follow-up audit](../screenshots/validation/GP16/door-followup-audit.md)
reproduces a separate DP3 recovery inconsistency: valid occupied old-cell tickets
still permit return after ledger loss/replacement, but block/explosion and
world-generation guards consult only the current ledger. Prioritize DP5's bounded
occupied-ticket protection before continuing station arrival/activity ownership,
reactive Will dummies and the newly supported interior/bridge/rail comparisons.
No screenshot or offline test closes the native or whole-facility fidelity gaps.


## DP5 — retain occupied recovery-room protections (2026-09-12)

Commit: 732670a83bcd7909858ca4480c31f5dc8aeeb8ad (pushed; exact-head CI 34730821095 passed).
The GP16 audit reproduced an inconsistent recovery state: valid original-cell
visitors could return after ledger loss/replacement, but break/build/explosion
and ordinary-world generation guards no longer recognized their room. The actual
boss callback requested a wasp queen inside it. The repaired owner now protects
the union of the current ledger allocation and each loaded visitor's own valid,
physically occupied ticket cell. Invalid, unreadable, outside or wrong-dimension
visitors cannot contribute a room or revoke another visitor's authority.

Return-arch clicks likewise recognize the requesting Hero's own occupied cell.
The deferred callback rechecks its captured block/dimension before using the
existing exact-source return. It refuses a changed cell, dimension, departed
player or lost old-room authority. Native non-sneaking container access, current
allocation protections, shared claims and failed-return tickets remain intact.
No ledger reconstruction, room placement, block repair, reward seeding, geometry
or generated asset changes occur. Missing history is not inferred from a ticket.
Old-room guards last only while valid loaded occupancy remains detectable.

See [LIBRARY_ARCANUM_PROTECTIONS.md](LIBRARY_ARCANUM_PROTECTIONS.md) and
`screenshots/validation/DP5/`. The actual-callback before/after probe, 33 adapter
groups, 13 generated-room runtime groups and four aperture groups pass. All 46
base gates and 62 ESM syntax checks pass in the isolated reviewed-index snapshot;
independent review found no blocker. Fresh 35-asset C2 and Guild diagnostics pass;
all corresponding assets/images and rendering owners match GP16. Full-render
evidence is retained from unchanged GP16 inputs, rather than claimed rerun.
GP16 exact-head CI 34730475595 passed. Every native acceptance remains unrun.

The [activity follow-up audit](../screenshots/validation/DP5/activity-followup-audit.md)
reproduces stale spouse/divorce callbacks, simultaneous proposal ownership/ring
loss and caller-independent Wait broadcasts. GP17 first closes deferred
relationship authority races. A separate durable requester activity owner,
proper native Wait/Follow and purposeful station arrival remain next; the pinned
2.1 API has no script navigation command. The audit records a feasible native
goal path and its missing engine evidence. Continue the 26-view interior/bridge/
range comparison queue and further designed Demon Door worlds, preserving
Nostro's distinct story passage and all legacy immediate-payout personas until
their own verified integrations exist.


## GP17 — deferred relationship authority (2026-09-12)

Commit: 10ffdd0578ae4327fb0c1c0a733d9b233d0d53f0 (pushed; exact-head CI 34731719396 passed).
The DP5 production probe reproduced ownership theft and two ring payments from
competing proposals, plus stale spouse and divorce actions affecting a later
partner. Relationship responses now require the original requester/NPC identities,
current same-dimension proximity and readable relationship history. Proposal
acceptance rechecks unmarried status, opinion and available ring; spouse actions
and nested divorce recheck the current spouse owner. Unknown or inconsistent
history defers without inventing an empty spouse list.

Form supersession and mutation invalidation share stable entity IDs. Requests
settle once and release their tracking; stale forms cannot revive after the same
Hero divorces and remarries. Required writes reserve ownership before payment.
Bounded rollback accounts for next-tick entity properties and setters that throw
after writing. Single-item wedding rings use their actual non-stackable inventory
definition. Ambiguous payment readback retains committed relationship authority
and suppresses success extras; there is no blind refund or atomic crash guarantee.

See [GUILD_RELATIONSHIP_AUTHORITY.md](GUILD_RELATIONSHIP_AUTHORITY.md) and
`screenshots/validation/GP17/` for actual-source regression, review findings and
version-pinned API provenance. All 47 base gates, 62 ESM syntax checks and 24
relationship groups pass in the isolated reviewed-index snapshot. The same final
suite reproduces 19 failures against DP5; 33 existing training groups and 17
independent review negatives pass. Independent review found no blocker. Fresh
35-asset C2 and Guild diagnostics pass; all 35 structure assets, 35 C2 images and
six rendering/geometry/data owners match GP16 exactly. Full-render evidence is
retained from GP16 unchanged inputs; no fresh full render is claimed.
No generator, geometry, resident identity, training controller or morality
authority changes.
Native multiplayer, persistence and navigation acceptance remain unrun.

The [final-voxel Maze survey](../screenshots/validation/GP17/maze-study-followup-audit.md)
corrects GP16's source-only furnishing comparison: three blue carpet cells remain,
but no study bookcase or bed survives final generation. The lectern and enchanting
table survive. An unshipped 11-cell fixture trial (three red carpet recolors and
eight supported bookcase cells) preserves 678 protected cells and all inspected
adjoining routes. This is preparatory evidence, not a changed Guild asset or a
complete original study reconstruction. Round lattice windows, bordered rug,
wall panels and full gallery dimensions remain open.

Next behavior priority: durable requester-specific activity ownership and native
Follow/Wait, then purposeful station arrival with interruption/defence preserved.
In parallel, implement the surveyed 11-cell Maze fixture as a separate GP18 pass,
with final-voxel regression and inspected detail renders. Continue bridge/range
comparisons and individually designed Demon Door worlds. GP17 form authority alone does not fix caller-independent Wait broadcasts,
generic native Follow targeting, roaming after Wait or station teleports.


## GP18 — supported Maze-study furnishings (2026-09-12)

Commit: c83246751b86aa489897efa3d0cadd49f303c588 (pushed; exact-head CI 34733425350 passed).
The final GP17 survey found that the source-authored study bookcase was skipped
and the bed erased by circulation clearance. A final generator fixture now adds
a supported two-column timber bookcase in the surveyed southwest pocket and
changes the three surviving blue carpet cells to red. Two inspected original-TLC
views support continuous framed shelves and a red rug. The 2-by-4 case, southwest
placement and retained sparse carpet patches are explicit block adaptations;
carved trim, full rug/border and original room proportions remain open.

Exactly eleven cells change: eight former-air case cells at x43..44,y12..15,z75
and the three existing carpet cells. Every other campus block/state, shared RNG
stream, interaction anchor, window and light remains exact. The complete tower
stair/deck/door routes and all 678 surveyed protected cells stay unchanged. Both
case fronts remain accessible. No bed is restored over the reserved stair opening.
Maze remains at (46,12,70). Existing occupied Guilds are never rebuilt; reanchor
continues to refresh coordinates only. No runtime or generated behavior change.

See [GUILD_MAZE_STUDY.md](GUILD_MAZE_STUDY.md) and
`screenshots/validation/GP18/`. Seven focused final-voxel groups pass, including
independent broken-support/frame/headroom/window/route/RNG negatives. The behavior
regression passed before targeted Guild-only regeneration. All 48 base gates,
62 ESM syntax checks, fresh 35-asset C2/full renders and Guild diagnostics pass
in the isolated reviewed-index snapshot. Independent review compares all 395,280
serialized voxels against the actual preceding owner and finds only eleven
changes; seven focused groups pass independently. Six inspected before/after
detail images show the supported case and retained openings. The other 34 assets
and all 35 C2 images stay exact.

The snapshot baseline includes concurrent commit
f7e875564d7aa61885ba5324e0a2a743f6751363, the README/documentation/Linux-font
refresh, whose CI 34731885346 passed. Its font fallback changes all 281 full
card PNGs relative to GP16. A separate render of that actual predecessor geometry
using the same current font/cache matches GP18 in all 281 images. The unchanged
distant views hide the interior fixture; the six focused detail images supply
its visual evidence. The font change is retained from the preceding commit and
is not part of GP18. See visual-delta.json and predecessor-font-comparison.json.
GP17 exact-head CI 34731719396 passed. Every native check remains unrun.

Next behavior priority remains durable requester-specific Follow/Wait and
purposeful station arrival, preserving training, relationship and defence
authority. Continue round lattice window, bordered rug, red wall-panel and
bridge/range comparisons, plus individual Demon Door worlds. Native lighting,
carpet collision, turning, navigation, multiplayer and saved-world acceptance
remain unrun; GP18 does not close facility fidelity or alter the 45-leaf score.


## GP19 — requester-owned Skill Follow and Wait (2026-09-12)

Commit: 6f490a7263226ce50e3ad72769ceaa3ad3fa2d24 (pushed; exact-head CI 34735910068 passed).
The two canonical Skill residents now accept activity through fresh exact resident
registry/marker/type/base/ID authority. A versioned world journal and write-ahead
initialization witness preserve requester, revision and outstanding tag cleanup.
Two native Follow channels select only their tagged requesting Hero; owned Wait
stops voluntary walking. Only the owner can change/resume/release activity; current
spouse authority remains required for married residents. Identity, opinion,
relationship, construction and reward history retain their existing owners.

Training cleanup precedes new native activity, and at least one tick separates
stop from replacement requester tags. Deferred activation rechecks live authority.
Reload stops/reconciles without automatic Follow resurrection. Offline holders,
failed writes and unavailable history block reuse; each channel has a 64-holder
limit and persistent overflow quarantine. Failed local observations that cannot
be persisted before a crash remain an explicit limit. Deleting both journal and
witness is indistinguishable from first installation; no atomic recovery claim.

Wait bypasses generic admiration and no longer broadcasts neutral to unrelated
followers/trainees. Outside this pilot, stationary Wait defers; legacy generic
Follow remains separate work. Spouse movement menus capture activity revision,
and delayed fear/idle callbacks cannot replace newer activity/training/defence.
Boast gathering excludes owned/pending activity. Defence independently removes
Wait/Follow and restores movement without changing offender selection. Only the
Skill entity is regenerated; no geometry, anchors, resources or reward changes.

See [GUILD_ACTIVITY_OWNERSHIP.md](GUILD_ACTIVITY_OWNERSHIP.md) and
`screenshots/validation/GP19/`. All 51 base gates and 64 ESM syntax checks pass in
the isolated reviewed-index snapshot. Sixteen controller, nine actual integration
and eight native component-transition groups pass, with 24 relationship, 33
training, 22 resident and 14 defence groups retained. Independent review passes
13 additional failure probes; early failures and repairs are recorded. An actual
GP18 probe reproduces both old Wait broadcast and stale fear replacement.
One missing activity dependency in the Might-only maintenance fixture was repaired
and that gate rerun; the first failure remains in evidence. No production code
changed during that correction. Fresh 35-asset C2 and Guild diagnostics pass.
All 35 structure assets, 35 C2 images and six rendering/data/geometry owners match
GP18; full-render evidence is retained from GP18, not rerun. Only Skill differs
among 51 isolated entity outputs. GP18 exact-head CI 34733425350 passed.
Every native movement, multiplayer and persistence check remains unrun.

The [door follow-up audit](../screenshots/validation/GP19/door-followup-audit.md)
reproduces a distinct return-history defect: an unreadable player ticket becomes
null, letting orphan recovery overwrite a valid exact source with a default.
When that default is obstructed, the preserved-source control succeeds while the
faulted path remains stranded after reads recover. Prioritize a separate DP6
unavailable-ticket distinction before mutation, retaining DP5 per-player guards
and intended absent/corrupt recovery. Then continue purposeful station arrival,
reactive training, reference-led interiors/bridges/range and individual door worlds.
This bounded pilot does not close whole-facility or native conformance.


## DP6 — preserve unavailable exact-source return tickets (2026-09-12)

Commit: 274da7f779aec56562341a7dc75de58a8907b81c. Pushed; exact-head CI
34736624694 passed.
The GP19 audit reproduced orphan recovery overwriting a valid exact return point
when the player-ticket read temporarily threw. The ticket reader now distinguishes
unavailable authority from confirmed missing/corrupt data. The affected periodic
or return operation defers before ticket writes, clears or teleport. Read recovery
retains the original safe source, including when every default approach is blocked.
One fresh ticket snapshot serves a synchronous operation; public and deferred-click
returns still read fresh authority. No snapshot persists across ticks.

Confirmed absent/invalid tickets retain primary-ledger fallback. DP5 protection
scans still isolate a failed reader while protecting the current allocation and
other readable occupied old cells. World progress, shared claims, room generation,
geometry, Guild activity and existing failed-write handling retain their owners.
Only the handwritten door controller and its adapter tests change.

See [LIBRARY_ARCANUM_TICKET_READS.md](LIBRARY_ARCANUM_TICKET_READS.md) and
`screenshots/validation/DP6/`. All 51 base gates and 64 ESM syntax checks pass in
the isolated reviewed-index snapshot. The 38 actual adapter groups include five
new groups; the same final suite fails three regressions against the preceding
controller. Thirteen room/runtime and four aperture groups pass. Independent
review repeats all 38 adapter groups and compares eight prior/current failed-write
cases without finding changed travel, primary history, placement or payout behavior.
Fresh 35-asset C2 and Guild diagnostics pass. All 35 structure assets, 35 C2 images
and six rendering/data/geometry owners match GP18; full-render evidence is retained
from those unchanged inputs, not rerun. GP19 exact-head CI 34735910068 passed.
All native travel, collision, collection, multiplayer and persistence checks remain
unrun. This injected failure proves the handling, not its frequency in Bedrock.

Continue purposeful Skill station arrival after GP19 ownership, reactive targets,
reference-led interior/bridge/range comparison and individually designed door worlds.
Preserve saved construction, exact-source returns, resident/relationship history,
legacy persona compatibility and Nostro's distinct story passage. The first portal
pilot and the facility still have open native and reference acceptance.


## GP20 — framed red dormitory wall bay (2026-09-13)

Commit: 71d70ed9f8ab21f49221a2c040f283c398f3f0ec. Pushed; exact-head CI
34737680186 passed.
The inspected original TLC dormitory screenshot 141296214 shows red plaster-like
infill, heavy timber uprights and dark carved lower panels. One existing plain
stone partition bay now uses six red terracotta cells between four dark-oak side
cells, x84, y7..8, z17..21. Size, placement and block materials are adaptations;
this does not establish the generated two-floor layout or complete room fidelity.
The shared roof courses remain exact. Both faces of the one-block partition
change, including its reverse beside the lower stores roof.

The final structure helper uses no RNG and changes only existing solid materials.
No floor, stair, bed, light, window, opening, anchor or saved-world geometry changes.
The renderer gains one approximate red-terracotta color entry. Required behavior
regressions passed before targeted generation; only the Guild asset changed among
1,661 pack files. Independent decoded comparison proves exactly ten of 395,280 cells change,
with all other materials, RNG/layout, 13,822 walking nodes and both dorm stair
routes intact. All 51 base gates and 64 ESM checks pass in the reviewed snapshot.
The initial build found stale C2 source metadata before the fresh render finished;
its red log remains, and only the build gate was rerun after adding the generated
C2 image/record. Fresh 35-asset C2, full 281-PNG renders and Guild diagnostics pass.
Only Guild changes among 35 assets/C2 images; only its full card and containing
places gallery change among 281 PNGs versus GP18. Six focused decoded views were
inspected. Use GP20 as the next visual-input baseline.
See GUILD_DORM_WALL_BAY.md and screenshots/validation/GP20/. Native acceptance remains
unrun; legacy C3 still has 45 leaves and 7 done.

The adjoining bridge/range survey found both existing bridge centerlines intact.
A hypothetical 22-cell rail footprint preserves surveyed routes and the actual
Skill ray, but precise source rail extent/bracing remains unverified. The DP6
arrival proposal still needs native offset/search/event calibration. A bounded
attempt to acquire the official pinned Linux server received transport failures;
no server or world was executed. Continue independent canonical-door/interior work
without inferring that these native checks passed.

The next distinct door candidate is Greatwood Gorge → The Arboretum, supported by
the retained 2005 guide's labelled interior and source views. GP20's
arboretum-followup.md records the bounded end-to-end scope: newly registered
Gorge instances, immutable identity, a disjoint realm grid, witnessed completed
consumption/full-evil admission, one physical shared Wellow's Pickhammer chest,
and exact-source return. Preserve all eight legacy personas, unregistered older
Gorges, Guild tickets/history and Nostro. This remains a proposal, not a second
implemented reward world; original murder parity, detailed source layout and
native acceptance remain open.


## DP7 — Greatwood Gorge to The Arboretum (2026-09-13)

Commit: e13127194b8bd596bf9db9fee03633a413825f24. Pushed; exact-head CI 34739113768 passed.
The second end-to-end pilot gives newly registered Gorges a distinct wooded
reward world, a physical shared Wellow’s Pickhammer and exact-instance return.
Current full evil or ten witnessed completed Crunchy Chick uses unlock it.
Counters belong to one Hero and one door; original murder parity remains open.
The native food event has no unique use token, so same-object/tick suppression is
bounded and native consumption/crash durability remains unrun.

Separate immutable source registration, placement receipts, initialization witness,
instance history and monotonic realm allocation preserve existing worlds. Unknown
pending source placement is never replayed; a successful saved receipt permits
confirmation retries. Existing unregistered Gorges and all eight legacy personas
retain their behavior. Guild schemas, exact tickets, current/old occupied-cell
guards and Nostro remain separate. Fresh raw alignment authority never migrates
or borrows legacy values to authorize a challenge.

Only 43 existing Gorge cells become the new mouth opening, with the rest of its
26,832 cells and RNG unchanged. The authored 49×28×49 Arboretum has large rooted
trees, a winding dry loop, one chest and a timber return frame. The original small
2005 guide image supports the wooded setting, not these exact dimensions or
furnishings. All Guild and Library geometry remains exact; no occupied-room
rebuild or reseeding is introduced. Native scan/loading cost, movement, lighting,
collection, multiplayer and persistence acceptance remain unrun.
See [ARBORETUM.md](ARBORETUM.md) and `screenshots/validation/DP7/` for evidence and
limits. Continue the facility/door cycle with proven defects and original pixels;
this pass does not close whole-facility or catalogue conformance.


## DP7 validation result

All 55 base gates and 65 ESM syntax checks pass in the isolated reviewed-index
snapshot. Runtime 27, actual main integration 16, alignment 6, Arboretum geometry 9,
Gorge 9, Library 5 and retained Guild adapter 38 groups pass. Independent runtime
review passes six negative probes against the final owner; its retained initial
checkpoint reproduces the revision-exhaustion defect before the final guard.
The first full run passed 54/55: the older rectangular-placement fixture lacked
new external portal dependencies. Only that fixture changed and its nine groups
reran successfully; the original result/log is retained. The earlier population
fixture correction and development failures are also explicitly recorded.

Fresh 36-asset C2, all 282 full PNGs and Guild diagnostics pass. Compared with GP20,
only the Gorge asset/C2 image changes and the Arboretum is added; all 34 other
assets/C2 images remain exact. Only the Gorge card and containing places gallery
change among 281 existing full PNGs, with one Arboretum card added. Root inspected
both cards, the gallery and six focused geometry views. Native acceptance remains
unrun. DP7 is the next visual baseline; C3 retains 45 leaves and 7 done.


## DP8 — independent Demon Door maintenance and returns (2026-09-13)

Commit: SELF: TLC Conformance — DP8: isolate Demon Door maintenance failures.
A failed Library reward-claim write escaped the shared periodic callback and
prevented a healthy Arboretum visitor's normal dwell return. Four independent
operation boundaries now isolate both families' face maintenance and runtime
ticks, including failed diagnostic reporting. Existing five/forty-tick cadence,
controllers, schemas, source/reward history, geometry and exact tickets remain.

See [DEMON_DOOR_TICK_ISOLATION.md](DEMON_DOOR_TICK_ISOLATION.md) and
`screenshots/validation/DP8/`. Twenty actual integration groups pass; the four
new groups fail against the actual DP7 main while sixteen prior groups pass.
The independent callback review found no blocker; root reviewed the actual
controller integration, semantic patch and predecessor failures. All 55 base gates, 65 ESM checks, fresh C2 and Guild diagnostics pass.
All 36 assets/C2 images and visual owners match DP7; full renders are retained
from its unchanged inputs, not rerun.
Native travel, multiplayer and persistence remain unrun. This correction does
not harden the older Guild first-build preparation or close either door pilot.

Next: reference-led firing-divider/interior improvements, then a separately
reproduced audit of Guild preparation/reward ambiguity. Purposeful Skill arrival
still needs native calibration; do not retry unchanged failed pinned downloads.

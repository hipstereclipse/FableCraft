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

Commit: SELF: TLC Conformance — GP11: open the Guild Library and Store archways.
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

# Continuation prompt

Continue the FableCraft → TLC Conformance plan on Linux.
Repository: /run/media/eclipse/8E025A94025A80DF/Users/Eclipse/Fablecraft
Branch: phase3-will-destiny
Remote: https://github.com/hipstereclipse/FableCraft.git

Read docs/CONFORMANCE_PLAN.md and docs/CONFORMANCE_CHECKLIST.md. Source plan and
six reference snapshots are in docs/. User override (2026-09-12): finish the spell
WIP and continue as far as practical without permission questions. Keep separate
milestone commits, validation, immediate pushes, evidence and fresh handoffs.

Latest user override (2026-09-12): prioritize recursively improving the Guild
layout, NPC behavior and fidelity to original 2005 Fable: The Lost Chapters.
Also prioritize redesigning Demon Doors so opening creates a Nether-portal-like
walk-through transition to each door's corresponding designed reward room/world,
with exploration, reward collection and a reliable portal back to the source.
This overrides the old instruction to start W3.5 or keep adding unrelated POIs.
Read docs/GUILD_DEMON_PRIORITIES.md first; it is the active execution queue.

Current checkpoint: GP11 — broad Library/Store connections
Last resolved prior commit: cf646628b65ef2ba26d0280102965bc11e3f0970 (GP10 pushed; exact-head CI 34720599204 passed).
Containing commit: TLC Conformance — GP11: open the Guild Library and Store archways.
Resolve current hash: git log -1 --format=%H --grep='TLC Conformance — GP11: open the Guild Library and Store archways'.
Never invent a self-hash. Read the supplemental priority ledger for implementation
scope, known defects and unrun engine checks.

Start with a reference/geometry/NPC defect audit, then a substantive Guild layout
pass, a Guild NPC pass and a complete Guild Demon Door/destination pilot. Repeat
inspect → compare → fix → regenerate → test → re-inspect, revisiting adjacent
rooms, routes and NPCs after changes. Rank concrete fidelity/behavior defects;
do not stop at a silhouette or a passing render score. Keep the Guild and door
work advancing; do not defer portals indefinitely behind Guild perfection.

Guild scope: architecture/proportions, connected rooms and interiors, map/quest/
skill/Cullis interactions, Maze's tower, courtyard/river/bridges/training, cave/
Chamber of Fate and door approach. Audit NPC purpose, training, dialogue and
reactions, movement freezing, repeated teleports and respawn/repair loops. Verify
canonical behavior; label Minecraft adaptations. Current Maze (46,12,70) is an
audited baseline: redesign may move anchors only with all owners/consumers/tests
changed together. Reanchor is not geometry migration. Preserve saved-world progress.

Guild portal pilot is implemented in DP1. Read docs/LIBRARY_ARCANUM.md. Stable
Lamp -> Library Arcanum mapping replaces the Guild's coordinate persona and
immediate payout. Lantern use opens a 3x4x9 throat, raises the face and admits
players through light after checked room creation. The original library grove
has one elixir chest and three minor keepsakes in containers; native collection
is shared-world and never refilled. World unlock/room/claim state and per-player
exact-approach tickets survive face replacement, death/reload and travel failure.
The unused Overworld volume is fully air-scanned; complete barrier containment,
paths, all reward approaches and lid/arrival/exit clearances are checked before
admission. No modern custom-dimension APIs or pack/API/UUID changes.

Existing Guilds receive only a fingerprinted 108-cell mouth clear, preserving
floor and progress; same-type player replacements cannot be distinguished.
GP2's old-world stair migration remains absent. Legacy open/paid or missing-face
history suppresses new room rewards; a replaced closed face's older payment
history is unrecoverable. Ordinary scatter still uses the legacy eight personas
and immediate payouts. Those conversions, direct TLC view comparisons and all
engine tests remain open; never substitute riddles for Nostro or other story doors.

GP2 fd95ef1: continuous two-wide half-block lobby/Maze stairs and gallery/dining
connection; 6 final-voxel regression groups. GP3 a61ab80: session/cleanup/interrupt
controller, 18 runtime groups and explicit roaming component restoration; one
checked station acquisition remains an adaptation, walking to marks unresolved.
Only 3 apprentice BP outputs changed. GP4 adds an offender-specific defence controller and actual projectile-owner
attribution; N5/N7 resident identity/repair remains open. Its transient
provocations clear on reload, while durable warrants and spouse fields persist. Existing GUILD anchors including Maze
(46,12,70) remain unchanged; reanchor is not geometry migration.

Current C2 covers 35 assets/renders (28 scatter/3 fixed/4 legacy), and the full
all-category screenshot pipeline has 32 structure cards. GP2 passed 28 gates,
GP3 passed 29 gates; DP1/DP2 passed all 34 gates; GP4 passed all 35 gates
and explicit lint/spells/ESM syntax/Guild diagnostics. Full GP4 rendering
completed (51 mobs, 55 items, 130 recipes, 32 structures, 13 galleries). All captures/tests are offline,
including mocked actual runtime callbacks; no live engine access has occurred.
DP2 91f46b9 inspects a native 207x153 gameplay screenshot in the 2005 Prima guide
and changes 426 local-y2 surface materials to irregular earth/grass; all other
voxels and every portal/reward/version contract remain unchanged. External
reference images remain ignored. Matching player-height/layout/lighting review
remains open; the limited original-image comparison has run.

GP4's historical actual-callback cave audit (docs/GUILD_CAVE_REVIEW.md) proved that the
existing caves_done flag is set before the first write and prevents retries
on interrupted/unloaded carving. No maintenance caller retries annex placement.
The library threshold floor is missing, the Chamber's registered Cullis feet
are two blocks too high, and its hill has three full-block rises. These were not fixed by the defence pass. GP5 now implements new-world
repairs described below. Never blanket-recarve occupied old worlds.

GP5 owns initial cave/Chamber work in guild_caves.js, with durable pre-placement
enrollment, original-cell snapshots, compare-safe verified progress and maintenance
retry. Legacy/no-journal worlds remain unmodified, including old interrupted caves.
The Chamber is placed from the exact generated DATA manifest through individual
permutations; completion follows verification. No broad delayed hollowing scrub.
The Library entrance floor is preserved, 184 concentric tread cells provide six half-height
rises around the entire unchanged dais (explicit user correction, 2026-09-12) and 44 glass cells contain the old water-cap perimeter.
CHAMBER_LAYOUT supplies origin (11,-22,27), size (31,20,31), Cullis feet (15,5,15).
Only a recognized old registry height can migrate, after actual core/arrival checks.
Source/destination door contracts and all surface Guild anchors remain unchanged.

Read docs/GUILD_CAVE_LIFECYCLE.md for conservative failure/legacy limits and manual
acceptance. The original 2005 guide's PDF p97/printed p96 was inspected at native
226x166 screenshots. The altar steps now wrap around fully; wall ribs/materials/lighting still differ;
partial visual C, full neutral-light/reference matching open. External pixels stay
ignored. _verify_caves.py now runs production suites instead of a mirrored carve.
No engine movement, native block state, fluid, loading or crash tests have run.
GP5 passes all 38 base gates from its isolated reviewed-index snapshot, plus
explicit lint/spells/ESM/Guild diagnostics. Focused groups: cave20, Chamber10,
Cullis6, C2 contract16. Full rendering: 51 mobs,55 items,130 recipes,32 structures,
13 galleries. The initial C2 bulk-placement-only reader failure was fixed and its
negative owner/manifest fixtures pass; initial logs are retained separately.

GP6 creates twelve durable resident slots with conservative old-world adoption,
confirmed-death tombstones and persistent native-spawn intent. Bound IDs retain
ownership through departure, another dimension, removal and failed lookup.
Extra/conflicting legacy residents are never deleted; unknown missing residents
and unmarked interrupted spawn intents remain reserved. Spouse/Follow/name/social
and quest state remain on originals. Only new births search checked same-height
column centres within two blocks; all 12 pass final-voxel/sequential occupancy.
Maze remains (46,12,70). No generated BP/RP output or existing location changes.
Read docs/GUILD_RESIDENTS.md for exact migration/crash limits and manual checks.
GP6 passes 39 base gates (resident 22/training 18/defence 14/cave 20), ESM syntax for 62 files,
and full rendering: 51 mobs/55 items/130 recipes/32 structures/13 galleries. Six NPC cards
remain hash-identical; static Guild diagnostics reuse byte-identical GP5 inputs.
All loading/Follow/collision/crash tests remain unrun.

DP3 keeps a valid player's original-cell return authority across a missing,
corrupt, throwing or recreated world door ledger. Normal exit dwell works even
for a lone visitor; invalid/outside/wrong-cell tickets authorize no recovery.
Only the original recorded source is used when primary history disagrees, with
failed tickets retained and no room/unlock/reward reconstruction. Unknown old
face payment history defers registration. Full standing-height clearance above
fractional feet avoids repeatedly selecting a ceiling-blocked approach.
Read docs/LIBRARY_ARCANUM_RECOVERY.md for actual callback repros and limitations.
The library asset/version/challenge and ordinary scattered doors are unchanged.
DP3 passes all 39 base gates (portal adapters 19/generated runtime 13/aperture 4),
including all Guild lifecycle/NPC suites, lint/spells and 62 ESM syntax checks.
No geometry/render-owner change: reuse GP6 full rendering and GP5 Guild diagnostics
with matched dependency hashes in evidence. Independent recovery review completed.
No live engine checks have run.

DP4 resolves persisted-anchor disagreement through one validated durable source
for lookup/spawn/scheduling/dimensions. The old hint is retained as a quarantine
alias only; it cannot spawn an ordinary door or change payment/room history.
Distant stale faces are preserved. No asset/version/anchor changes. Read
LIBRARY_ARCANUM_SOURCE_AUTHORITY.md and DP4 evidence; 25 adapter groups pass.
All native Bedrock acceptance remains unrun. GP7 retires the obsolete approach sweeps.

GP7 removes clearGuildRingScarecrows and repairGuildDemonApproach plus their calls.
Old flags stay unchanged; missing flags never authorize repaving or deleting player
containers. The actual baseline made 92 writes; an unloaded cell caused 91 writes
per retry. Current final generator needs no collision/headroom repair, differing
only in seven cobble variants. No asset/anchor/geometry migration. Eight callback
and four Python wrapper/geometry groups cover saved builds and training/routes.
Read GUILD_MAINTENANCE.md; terrain/skirt repairs remain separate, not proven safe.
Old blocked marks are retained and refused. All live engine checks remain unrun.

The GP/DP priorities are supplemental, tracked separately from C3's original 45
leaves; do not inflate the old scoreboard or mark these new deliverables done.
Defer W3.5 and other unrelated expansion while this cycle has actionable work.
Missing engine access leaves checks unrun; continue independent priority work.

W3.4 at 0a64e76 adds fc:greatwood_gorge, 39x16x43, weight 6, grass/rock, forest theme.
Raised banks, five-wide timber bridge/rails, bandit checkpoint/shack, static
stone face and two stair flights connect the upper route to a dry lower ravine.
One ordinary chest and three bandits have tested anchors. Six groups cover
bridge/rails, both stairs, chest/face/lower routes, actual scatter/idempotence
and independent broken-deck/closed-shack/blocked-stair fixtures. A TLC toll
shot supplies wooded material context only; full bridge/face comparison pending.
Straight banks, sparse trees and slab face are visible gaps. No toll transaction,
leader surrender/fleeing, Arboretum challenge/reward, quest completion or Cullis.
No unrelated Demon Door riddle substituted. See docs/GREATWOOD_GORGE.md.
All engine checks, including jump-free stairs/fence collision, remain unrun.

W3.3 at c73bbf6 adds fc:archon_folly, 49x18x55, weight 2, rock, dark theme. Circular
blackstone platform, contained lava annulus, raised edge, north causeway and
four basalt spires. One existing dragon at (24.5,3,30.5); actual 1.54x4.18
collider and 12x12 dry landing tested. Six groups cover basin floor/banks,
five-wide return route, stairs, scatter/idempotence and independent broken
floor/bank/exit/high-collision fixtures. Initial red test extended into the south
curb; corrected route ends at z42. No geometry removed. Partial visual grade C:
TLC shots have warmer paving and much stronger jagged volcanic surroundings.
No soul prerequisite, Shrine link, phased fight, confinement, mask choice or
ending. No structure loot, Cullis or Demon Door. Lava fluid behavior, dragon
combat and jump-free movement unrun. See docs/ARCHON_FOLLY.md.

W3.2 at b5db77c adds fc:archon_shrine, 49x24x57, weight 4, snow/rock, snow theme. Round
stepped shrine, curved dome, three floor sockets and two ordinary chests adjoin
an active center Cullis disc (24,1,28) and sealed monumental Bronze Gate. A TLC
guide shot prompted a circular bronze mechanism on the gate face; sculpted
ornament and full shrine reference comparison remain gaps. Seven test groups
cover routes, stairs, actual scatter/Cullis detection, missing-core/ring/unloaded
negatives, blocked shrine and blocked arrival. No souls quest, gate opening or
onward link to Folly. No mobs or Demon Door. See docs/ARCHON_SHRINE.md. Offline
routes permit one-block steps; engine stair/collision/travel checks remain unrun.

W3.1 at a214163 adds fc:bargate_prison, 41x20x49, weight 4, grass/rock. Seven
regression groups pass for courtyard/cells/ramparts/office/chamber and guards/loot.
The underground room is a major visual gap: small, rectangular and flat-roofed
instead of the TLC round domed basin hall with waterfall. No prison quest,
equipment confiscation/recovery, rescue, cell locks or Kraken. Chamber top stair
has a full-block transition; jump-free movement unproven. See docs/BARGATE_PRISON.md.

W2.4 at 40a92e7 adds fc:grey_house, 31x20x35, weight 5, grass/rock, dark theme.
Raised manor, internal cellar stairs, two coffins/chests and three undead have
seven passing groups. Stable, lantern sequence, ghost and investigation are absent.
A TLC guide stable image supplies material context, not full exterior/cellar proof.
See docs/GREY_HOUSE.md. Both new POIs keep local y=0 as the scatter foundation plane;
no buried placement offset. Added weights change future unvisited-region rolls;
existing region flags/geometry remain untouched. No Cullis or Demon Door at either.

W2.3 at 0edad619 widened Oakvale to 53x14x35 with east Memorial Garden, six graves
and upright axe statue. Its swinging pose/hillside/entry remain visual gaps. Five
emitted chests remain; an inherited cottage/quay overlap destroys an attempted sixth,
reserved for W4.1. W2.2 at a0b59f2 connects Hook Coast lighthouse/Abbey/graves; major
quest and travel gaps remain. W2.1 at fae89fb adds Bowerstone North/Manor, W1.4 at
ed57d1e adds Arena halls, W1.3 at add099a adds Twinblade rings, W1.2 at 608edf1 adds
Lychfield landmarks. Their detailed docs and manual checklists remain authoritative.
Nostro's onward route is missing: never substitute an unrelated Demon Door riddle.
No fc:place handler exists. Raw /structure load places blocks only; scatter owns
population, loot and travel. Keep procedural scatter, no fixed map or old-region retrofit.

The W3.4 baseline has all 27 local scripts/validate.py gates passing, plus spell
and syntax checks. This docs-only priority checkpoint saves its validation under
screenshots/validation/PRIORITY/: all 27 gates plus explicit lint/spells pass.
New renders are not applicable. No new in-engine checks or Guild/portal
implementation passes are claimed.
At the W3.4 baseline, C2 covered 34 assets/renders
(28 scatter/two fixed/four legacy), 15 contract groups
and nine placement cases. DP1 later raised C2 to 35 assets/renders; current
asset/render hashes match. Full all-category
pipelines ran through W3.4 in tmp/conformance/<ID>-full-screenshots; W3.4 renders
31 structure cards. Logs, audits, primary views and explicitly labeled cutaways
are in screenshots/validation/<ID>. These are offline evidence, never engine passes.
C2 checks mobSpawns count/finite shape/feet/head bounds; cross-POI fixtures catch
Snowspire contamination. Geometry clearance stays in individual POI tests.

C3 requires python scripts/conformance_score.py --write after EVERY checklist change,
then --check. It tracks 45 leaves, automated/manual counts and appearance separately.
W3.3 remote CI passed at c73bbf6 (run 34709053658); metadata is in
screenshots/validation/W3.3/remote-run.json. Inspect newest workflow's actual head next.
All current world rows remain in-progress for manual/reference work, not done.

Next three actions:
1. Inspect exact-head CI and current GP5/GP6/DP3/DP4/GP7 evidence. Run supported Bedrock
   acceptance when available: full surrounding altar stairs/cave loading, two-Hero
   resident departure/reload/death, portal collection/return/crash persistence.
2. Continue reference-led Guild/door refinement. DP4 fixes the persisted-anchor
   disagreement without resetting payment/room history. GP7 retired obsolete
   approach/scarecrow sweeps; broader terrain/skirt repair needs a separate audit.
   Next NPC defects: owner-specific Follow/Wait and distinct Will training.
   Current Follow accepts any player; Wait leaves strolling and its emote broadcasts
   neutral to all nearby NPCs. Recheck spouse ownership in deferred form actions.
   Preserve social/resident state; avoid permanent-taming or teleport shortcuts.
   Chamber wall ribs/materials/lighting, canonical NPC staffing and walking to
   training remain open. Preserve the user's full-circumference altar correction.
3. Continue separate milestones with base/domain gates, full renders as applicable,
   evidence, fresh handoff, commit and immediate push. Defer unrelated POIs and
   arbitrary story-door riddles. Old interrupted cave geometry needs a separate
   conservative migration; no blanket recarve. At context limits print this
   continuation verbatim. Missing engine access leaves checks unrun, never passed.

Landmines: hundreds of apparent edits are CRLF noise. Never git add -A, commit -a,
renormalize, create .gitattributes or discard unrelated work. Read diffs with
--ignore-cr-at-eol; stage named reviewed patches via git apply --cached --ignore-whitespace.
Behavior owner was restored from 6cfea15 in 0.1. Run python scripts/tests/test_gen_behavior.py
before regeneration; use targeted owners. Passing 0.1 does not prove unrestricted
--full output drift safe. Stripped owner remains in tmp/conformance/gen_behavior_stripped.py.

Never hand-edit generator-owned BP entities, RP models/animations/controllers/
attachables/particles, fable_emote_registry.js, fable_hud.js, fc_gamedata.js or
texts/languages.json. Find/establish ownership if memory disagrees. Keep GUILD anchors
coupled to gen_structures; reanchor refreshes but does not audit. Maze baseline is
(46,12,70); change it only as a fully coupled, validated redesign.
No Guild tiling applied; never run the old patch blindly. All-cross-references-OK
checks assets only. Keep HUD payload/spacers/clip offsets coupled. wd alignment is
authoritative; preserve the legacy XP-spending bridge. HUD's narrow green radar,
missing hunger frame and navigation bleed remain visible gaps.

Spells are separately complete in ccafd4c; never stash/revert/refold them into this
plan. SPELL_COMPANIONS.md engine checks, 0.3 and L3 remain pending. BOUNTY_SYSTEM.md
was reconciled in 0.4. L4 public releases remain blocked: known-name debt, unselected
public title (Wayfarer Tales provisional) and missing saved-world remap. No exemptions.
Preserve inherited dist archives, four scripts/_align/overlay_*.png and scratch files.
Build faithful archives only in ignored tmp/builds/faithful-<run>/dist; never stage or
publish them. Public builds need original branding and zero-debt L4 scan. Original/
generated assets only; external reference images stay ignored developer scratch.
No extracted Fable pack assets, free and never monetized.

Git writes/network require escalation here. Use the existing repository author from
git log via commit-scoped -c options, not global config. Origin is user-authorized
and verified; separate pushes succeeded. No force push. Preserve local commits and
report any push failure honestly; never claim remote sync without checking.

DP4 validation: all 39 base gates pass from the isolated reviewed-index snapshot,
plus 25 adapter groups and ESM syntax for all 62 BP scripts. Lint, spells, Guild
lifecycle/NPC gates and C2 are green. GP6 full renders and GP5 Guild diagnostics
are reused with matched dependency hashes; no visual owner changed. Independent
source-authority review found no blocking defect. Live engine tests remain unrun.

GP7 validation: all 40 base gates pass from the isolated reviewed-index snapshot,
including 8 maintenance callback groups within 4 Python wrapper/geometry groups,
all existing Guild/door suites, lint and spells. All 62 BP scripts pass ESM syntax.
GP6 renders/GP5 diagnostics have matched reviewed dependency hashes. Independent
review found no blocker. DP4 exact-head CI 34718207560 passed. GP7 native Bedrock
acceptance remains unrun; inspect its containing commit's actual remote CI next.

GP8: new Chambers use pointed attached wall ribs, dark stone and elevated lamps.
All 116 outer-walk cells are reachable; 4,419 protected cells preserve the user's
full surrounding altar steps, entry, foundation and water/glass containment.
Frozen scripts/data/guild_chamber_gp5.json lets interrupted recognized GP5 builds
finish their original appearance using the existing original-cell journal.
Unknown or edited histories defer; occupied rooms/painting entities stay unchanged.
Forty base gates, 23 cave groups, 14 Chamber groups, 62 ESM syntax checks and fresh
C2/full renders/Guild diagnostics pass offline. All Bedrock checks remain unrun.
See docs/GUILD_CHAMBER_INTERIOR.md. Next integrate/review GP9 dedicated Will practice
and GP10 low map relief as separate checkpoints; source/evidence may already be
unstaged. Then revisit connected rooms and requester-specific NPC Follow/Wait.

GP9 adds a dedicated Will-island pose/lightning drill and Might-only sparring.
Actual delayed callbacks recheck tokens/eligibility/dummy/lane before effects;
failed or edited stations refuse practice without repaving. New Guilds receive a
one-cell worn mark; existing residents and saved construction remain intact.
Twenty-five training groups, three final-voxel Will groups, 41 base gates and 62
ESM syntax checks pass offline. Fresh C2/full renders and Guild diagnostics ran.
Native facing, collision, blending and save/reload remain unrun. See
GUILD_WILL_TRAINING.md. Next integrate GP10 low map relief and GP11 broad interior
Library/Store connections separately; source may already be unstaged. Then resume
whole-facility reference/route review and requester-specific Follow/Wait ownership.

GP10 replaces the random jewel/beacon map with a low wood-framed land/sea relief.
Exactly 38 map-furniture cells change; all other campus cells and 37 original RNG
draws are preserved. Quest lecterns, Guildmaster birth and walking approaches stay
fixed. New Guilds only; no saved-world migration. Six focused groups, 42 base gates,
62 ESM checks, fresh C2/full renders and Guild diagnostics pass offline. Native
lighting/interaction/movement remain unrun. See GUILD_MAP_TABLE.md. Next integrate
GP11 broad Library/Store joins and GP12 supported Library shelves/reading furniture
as separate reviewed checkpoints; unfinished source may already be unstaged.

GP11 removes obsolete narrow tunnels from inside the larger Library/Store bays.
Three contiguous lanes and the broad arches are clear; exactly 64 cells change,
all within those shells. Floor, anchors, outside geometry and RNG48 stay exact.
Seven focused groups, 43 base gates, 62 ESM checks, fresh C2/full renders and Guild
diagnostics pass offline. Native movement/lighting/NPC acceptance remains unrun.
See GUILD_HALL_LINKS.md. GP12 Library interior and GP13 northeast dorm final stair
transition are the next separately reviewed passes; source may be unstaged.

Latest user steering: keep finding additional online reference photos. GP11 saves
four newly inspected 2011 TLC PC shots as text URLs/hashes/observations in
additional-online-references.json. External pixels are ignored under
tmp/conformance/reference-guild-additional. New evidence shows low stone melee
ring/wooden gate, archery rails/painted backdrop, straw Will targets; compare next.
Continue original Library/dorm/Maze/courtyard searches; exclude Anniversary/sequels.

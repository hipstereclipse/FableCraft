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

Current checkpoint: DP2 — limited original-image comparison and floor-only Library Arcanum refinement
Last resolved prior commit: 60513c808c2c3f1dc5de14ce497770aa7c9d6cf2 (pushed).
Containing commit: TLC Conformance — DP2: soften Arcanum paths from the 2005 reference.
Resolve current hash: git log -1 --format=%H --grep='TLC Conformance — DP2: soften Arcanum paths from the 2005 reference'.
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
Only 3 apprentice BP outputs changed. N5/N7 resident repair and N6 innocent-player
targeting are the highest next NPC risks. Existing GUILD anchors including Maze
(46,12,70) remain unchanged; reanchor is not geometry migration.

Current C2 covers 35 assets/renders (28 scatter/3 fixed/4 legacy), and the full
all-category screenshot pipeline has 32 structure cards. GP2 passed28 gates,
GP3 passed 29 gates; DP1 passed all 34 gates. All captures/tests are offline,
including mocked actual runtime callbacks; no live engine access has occurred.

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
C2 covers 34 assets/renders (28 scatter/two fixed/four legacy), 15 contract groups
and nine placement cases. Current asset/render hashes match. Full all-category
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
1. Complete the GP4 Guild defence pass with offender-specific attribution and
   aggregate warrant handling, including portal departure/return and cleanup.
2. Follow the integrated cave lifecycle/route audit; preserve saved-world work
   and never interpret a queued carve as verified completion.
3. Run base/domain gates, inspect renders/reference comparisons, update evidence
   and handoff, commit the coherent pass and push; engine checks remain unrun.
   At context limits print this continuation prompt verbatim.

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

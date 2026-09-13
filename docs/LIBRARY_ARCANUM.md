# Guild Demon Door and Library Arcanum pilot

DP1 implementation, 2026-09-12. The Guild now has a persistent, keyed
`guild_library_arcanum` challenge and a walk-through destination with four
collectibles and return travel. This also supplies DP2's first designed room.
Both priorities remain **in-progress**: live Bedrock acceptance has not run.
A later [reference review](LIBRARY_ARCANUM_REFERENCE_REVIEW.md) compared one
low-resolution original-game image; full layout/camera comparison remains open. Other doors retain their existing
procedural challenges and immediate rewards; they have not been converted.

The verified original pairing is **Lamp → Library Arcanum**. Its main chest
contains an Elixir of Life; Making Friends is on a table and Book of Spells and
the Howl Tattoo are in shelving. Source links and the pinned API investigation
are in [DEMON_DOOR_DESIGN.md](DEMON_DOOR_DESIGN.md). Holding a vanilla lantern
and using it on the face is the pilot's explicit Minecraft adaptation. It
consumes no lantern and grants no items, XP or reputation when the door opens.

## Using the passage

1. Hold a lantern and interact with the Guild face. The face rises over two
   seconds, loses collision, and leaves a soul-particle curtain in the mouth.
2. Walk into the light and remain there briefly. On the first opening, room
   preparation can take roughly forty seconds at normal tick speed, plus chunk
   loading. The player stays at the source until loading and verification finish;
   leaving cancels entry. The door reports that the passage is taking shape.
3. Explore the library grove. Take the elixir from the rear reliquary chest,
   Making Friends from the reading-table barrel, and the two other keepsakes
   from the shelving containers. Native inventory transfer owns collection.
4. Walk into the low stone arch behind the arrival point to return. Clicking
   its central paving or overhead light also requests return. The diagnostic
   `/scriptevent fc:door_return` requests the same checked recovery route.

The three minor items are named book/paper representations, without copied book
text, a reading system or a functioning tattoo unlock. Rewards belong to the
shared world: there is one set for the Guild, rather than one set per visitor.
The player's bed/home spawn is never changed by this excursion.

## DP2 reference refinement

After DP1, a bounded comparison with the 2005 guide image prompted a floor-only
refinement. New rooms use larger, irregular earth and grass patches in place
of the formal paved garden. The return arch retains its recognizable stone
approach. Exactly 426 blocks at local y2 change material; every other voxel,
the four containers, paths, portal coordinates, structure size and version-1
contract remain compatible. Existing ready/visited rooms retain their original
floor and rewards; no migration or room replacement is attempted.

The new overview was inspected against DP1's preview and the original reference.
It softens the paving pattern, but neither the underlying rectangular storage
footprint nor the trees, shelves and lighting are claimed faithful. Matching
player-height views and broader original footage remain required. Evidence:
`screenshots/validation/DP2/`, including the complete floor-material delta.

## Geometry and ownership

`scripts/door_realms.py` owns the original 49×28×49 grove, called by the explicit
`gen_structures.library_arcanum` wrapper. It has irregular mossy crags, seven
trees, a contained pond, a dry walking loop, three bookshelf pergolas, a separate
reading table, seating, lamps, four empty containers and a recognizable return
arch. Walkable ground is at y2 and normal feet at y3. The whole bottom, sides
and ceiling have invisible barrier containment; the renderer omits those
invisible surfaces while retaining them in the actual structure.

The layout is an original Minecraft interpretation of documented library-grove
features. Its square outer storage footprint, cuboid trees, shelf furniture and
limited atmosphere remain visible adaptations. No matching player-height camera view, exact proportions, butterflies,
animation or lighting fidelity is established.
Static renderer grades measure its image properties, not TLC resemblance.

The Guild generator clears x65..67, y1..4, z96..104, with a continuous cobble
floor and lamps outside the mouth. The rear opens onto the perimeter lane;
the campus boundary wall beyond that lane remains. Existing Guild anchors,
Maze's study, training marks and saved-world placement guards are unchanged.

`guild_door_aperture.js` is a separate, bounded saved-Guild migration. It checks
all 108 cells against a frozen GP1 block-type fingerprint and all 27 supporting
floor cells before clearing any block. Air permits new geometry or a partially
completed clear. A foreign block, absent floor or unloaded block refuses the
operation. A durable clearing/ready record supports retry; a ready passage is
never recleared after later edits. Only the mouth changes in an old Guild.
The old broken stairs remain a separate migration issue.

Block types cannot distinguish a player's replacement stone from identical
generated stone. The migration therefore does not promise perfect detection
of edits using those same materials. Modified mouths with foreign materials
require the player to clear them; no whole-campus structure reload occurs.

`fc_data.py` owns the keyed challenge and frozen aperture data; only
`gen_behavior.emit_script_data()` emits `fc_gamedata.js`. The eight old persona
rows and their order remain intact. `gen_behavior.emit_entity()` now gives
Demon Door faces no gravity, pushability, leash or navigation; opening disables
collision. This physical correction also applies to ordinary faces. It does
not convert their challenges or reward destinations.
[Microsoft physics component semantics](https://learn.microsoft.com/en-us/minecraft/creator/documents/entitycomponentsguide?view=minecraft-bedrock-stable#physical-components).

## Persistence, loading and recovery

`fc_demon_doors.js` owns world property `fc_dp_guild_v1`, player tickets
`fc_dp_return_v1`, the opening/dwell state machine and temporary chunk leases.
The main adapter registers surviving faces before replacing them, removes
duplicate Guild faces only after recording the surviving state, captures the
used item before deferring interaction, and drives the controller every five
ticks. A corrupt record never falls through to the old payout function.

The pinned server API remains 2.1.0. The destination occupies a checked, reserved
Overworld cell beginning at (600000,272,600000); this is isolated storage, not
Nether travel or a custom dimension. An unused cell is persisted before the
worker scans its entire 67,228-block volume for air, checks players/entities,
and places the structure. Occupied candidates are skipped without clearing.
Scans are spread over ticks. DP9 also checks the complete volume immediately
before placement with a native bulk query that refuses unloaded chunks. Only
the pilot's named ticking areas are managed.
Unavailable command authority, missing chunks or missing structures leave
entry at the source and back off before retrying.

The worker verifies all 9,794 barrier cells before first admission and after
reload/unloaded-room recovery. Entry also checks the arrival, return, central
walk, side branches, each reward approach and every container's lid space.
DP9 records verified placement and seed intents/receipts in the existing Guild
record. Rewards are seeded only after all four containers are verified empty
and the destination is checked unoccupied. Fresh exact item/count/name/lore and
all-slot readback precede the ready record. A visited or ready room is never
replaced or replenished. Missing or damaged
containers refuse future admission and still allow recovery return for visitors
already inside. Unknown legacy placing and interrupted placement/seed intents now remain closed;
unvisited state alone never permits replay. A saved placement receipt permits
verification; a saved seed receipt permits ready persistence after exact readback.
Neither retries block/item effects. Fresh complete shell queries also precede
entry into cached ready rooms. See [the DP9 preparation contract](LIBRARY_ARCANUM_PREPARATION.md).
Property writes and container changes are not an atomic engine save. Actual
crash durability remains a required engine test.

Each player records a safe source approach before travel. Return tries that
exact recorded position first, then a small set of safe alternatives beside the
same source if it has become obstructed. It loads the source if necessary and
retains the ticket on failed travel. A 20-tick dwell, 60-tick cooldown and
leave-volume rearming prevent immediate bounce. Arrival is four blocks beyond
the return plane. Death, disconnect and external travel reconcile actual
position without forcing the player back into the room.

DP3 preserves normal exit dwell and the diagnostic return command through a
missing, corrupt or temporarily unreadable primary record, and after source
maintenance recreates a record with no room or a different cell. A valid committed
player ticket and physical occupancy of its exact bounded Overworld cell are
required. Recovery uses only that original source, keeps failed tickets and never
resets world progress. If both records are lost or corrupt, the original source
cannot be recovered reliably; no guessed teleport is attempted. See
[LIBRARY_ARCANUM_RECOVERY.md](LIBRARY_ARCANUM_RECOVERY.md) for tested interleavings
and full standing-height clearance at fractional return positions.

A surviving paid/open legacy face migrates unlocked and suppresses all new room
rewards. A missing face with no ledger is labeled `history_unknown` and likewise
suppresses rewards. A surviving closed face can receive the canonical challenge;
historical destruction/replacement may have erased an earlier payout, so its
prior payment history remains unrecoverable. This limitation is recorded, not
inferred from current inventory. A transient read failure in surviving-face history
defers registration; it never establishes that rewards were unpaid.

DP5 now retains block and spawning protections for valid loaded original-cell
visitors through the same lost/replaced-ledger recovery cases. Return-arch clicks
revalidate the requesting player at the captured original cell. See
[LIBRARY_ARCANUM_PROTECTIONS.md](LIBRARY_ARCANUM_PROTECTIONS.md) for scope,
failed-scan/departure limits and actual callback tests.

The reserved footprint plus a 160-block margin is excluded from normal scatter
and scripted quest-boss spawning at every height. The room is outside the loot,
settlement and Cullis registries. Stable before-events block player breaking,
building interactions, escape items and explosion block damage; ordinary
non-sneaking container use remains available. The experimental before-place
event is not required. Commands, other add-ons and all engine-specific placement,
fluid, fire, natural-spawn and item-interaction paths are not proven contained
by the offline mocks.
[Microsoft before-events](https://learn.microsoft.com/en-us/minecraft/creator/scriptapi/minecraft/server/worldbeforeevents?view=minecraft-bedrock-stable).

## Verification and remaining acceptance

All 34 base gates pass from an isolated reviewed-index snapshot. The focused
suites comprise 13 runtime, 12 main-adapter, 5 source-geometry, 4 aperture and
5 destination groups; the behavior owner has 6 passing groups. The full render
pipeline completed with 51 mob, 55 item, 130 recipe, 32 structure and 13 gallery
images. C2 verifies 35 structure assets/renders independently.

Evidence is under `screenshots/validation/DP1/`. Final-voxel tests cover source
and destination routes in both directions, source migration compatibility,
the sealed shell, contained pond, empty containers and independently damaged
headroom/floor/exit fixtures. Actual-module runtime tests inject Bedrock effects
and actual generated voxels; adapter tests execute production main callbacks.
They exercise simultaneous requests, paid migration, unavailable loading,
partial builds, damaged rooms, failed teleport, reentry, reward depletion,
distinct player returns, reload/death and protected world-generation boundaries.

All live acceptance remains **unrun**: load the pack at its supported version,
inspect the content log, walk the entire source tunnel and grove, inspect
opening/particles/collision and both exit approaches, collect all four rewards,
return to two different recorded approaches, then repeat after reload/death,
two-player entry/collection, face replacement, failed loading authority and
interrupted saves. Test the cited protection limitations explicitly. The [2005 guide image review](LIBRARY_ARCANUM_REFERENCE_REVIEW.md) supplies
a bounded visual comparison; matching player-height footage, unseen areas and
further room design are still required.

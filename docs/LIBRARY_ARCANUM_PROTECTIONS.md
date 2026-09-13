# Occupied Library Arcanum recovery protections — DP5

DP5 retains the room's existing block and ordinary-world spawning guards while a
visitor recovers from a lost or replaced world ledger. Before this pass, the
visitor's committed ticket still permitted exact-source return, but breaking,
building interactions, explosion block filtering, scatter and quest-boss guards
lost the same room. The actual boss callback could request a wasp queen inside
the occupied Library. The before/after probe records these script decisions at
mocked engine boundaries; no native explosion or spawn was observed.

## Authority and scope

`fc_demon_doors.js` now combines the current valid ledger allocation with each
loaded visitor's own valid ticket cell, provided that visitor physically occupies
that exact bounded Overworld room. The existing ticket checks retain schema,
door ID, supported source dimension, finite source coordinates, cell range and
committed travel phase. A duplicate visitor in one cell adds no second volume.
Two old occupied cells can coexist with a new current allocation.

Block guards cover each room's exact 49×28×49 volume. Scatter and quest-boss
guards retain the existing 160-block horizontal margin at every height. This
does not reserve the entire cell grid or add rooms to ordinary scatter. Unknown
or stale outside tickets do not claim terrain. An invalid or unreadable player
is isolated from other valid visitors. A failed player scan preserves the current
ledger's allocation; it cannot infer unknown old ones. The helpers reread current
authority on each query rather than retaining an occupancy cache after departure.

Return-arch clicks now recognize the requesting player's own occupied room,
including a valid old-cell ticket. The callback captures the clicked block and
dimension, then rechecks that same player's authority at that arch after deferral.
Moving to another cell, changing dimension, leaving or losing old-room authority
cancels the queued action. It cannot borrow another visitor's ticket. Successful
clicks call the established checked return path; failed travel keeps the ticket,
and confirmed travel clears it. Normal dwell and diagnostic return remain intact.

Non-sneaking chest/barrel interactions still use native container transfer.
Neither the protection queries nor the click adapter reconstructs a ledger,
rebuilds a room, restores blocks, seeds rewards, reopens a door or changes shared
claim history. All geometry, structure IDs, assets and Guild anchors remain
unchanged. No generation or saved-world geometry migration is required.

## Verification and remaining acceptance

Evidence is under `screenshots/validation/DP5/`. The portable probe takes a
repository snapshot root and `before`/`after` expectation; it executes the actual
main callbacks and owned modules. `adapter-red.log` records the seven new groups
failing against the previous controller. The repaired adapter suite has 33
passing groups, including one additional failed-scan/invalid-handle group. The
existing 13 actual generated-room runtime groups and four aperture groups also
pass. All 46 base gates and 62 ESM syntax checks pass from the reviewed index
snapshot, with fresh 35-asset C2 and Guild diagnostics. Generated and visual
inputs remain identical to GP16; no new full render is claimed. The independent
source/test review records exact hashes and limitations.

Tests cover missing, corrupt, throwing, recreated-without-room and distant
replacement ledgers; multiple visitors/rooms; wrong cells/dimensions, corrupt or
missing ticket data, departure/disconnect, all committed travel phases and failed
player reads. They exercise actual break, interaction, explosion, scatter, boss
and deferred return callbacks, with positive controls outside the protected rooms.
Primary progress strings and structure-placement counts are checked unchanged.

Old-room protection requires a detectable loaded ticketed occupant when primary
history is unavailable. It is not permanent recovery of unknown allocations
after all visitors leave or disconnect. Commands, other add-ons, natural engine
spawns, fluid/fire behavior and every native item/placement path remain outside
the proven mock boundary. Initial block reach is supplied by the engine; the
queued check requires the original cell, not an unchanged in-cell position.

All native acceptance remains **unrun**: walk/return, actual protected block
interactions and explosions, ordinary container collection, two-Hero occupancy,
disconnect/reload, failed chunk loading, save/crash durability, performance and
content logs. DP5 remains in-progress. This repair does not complete Library
visual fidelity, convert the eight legacy scatter personas or add more designed
reward worlds. See [the design contract](DEMON_DOOR_DESIGN.md) and
[original-cell recovery](LIBRARY_ARCANUM_RECOVERY.md).

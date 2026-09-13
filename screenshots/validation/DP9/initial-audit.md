# DP9 independent predecessor preparation audit

2026-09-13. No production edits. These bounded offline native-effect probes run
actual `fc_demon_doors.js`, frozen in this ignored directory, against a fixture
captured from the actual `build_library_arcanum` owner. The fixture injects only
world/block/property/inventory/teleport effects. It does not reimplement the
controller. `baseline-sha256.txt` pins the owner bytes. No engine acceptance ran.

Run from repository root:

```sh
node --experimental-vm-modules tmp/conformance/dp9-audit/baseline-probes.mjs tmp/conformance/dp9-audit/room.json
```

The command exits 0 because these predecessor assertions deliberately require
the observed unsafe behavior. Its complete output is `baseline-probes.log`.

## Observations

1. **Late survey edit overwritten.** After the first 512-cell preflight slice,
   replace a previously observed air cell at local (10,1,0) with diamond block.
   The old worker still places in cell 0, replaces the block with barrier, and
   commits ready. The spread scan does not prove the volume is still empty at
   the placement boundary.
2. **Interrupted partial seed replays placement.** First reward set succeeds;
   second native set throws. Saved phase remains `placing`. Add a diamond block
   at local (10,20,10), reload and retry. A second full structure placement erases
   the diamond and recreates every reward container, then seeds and commits.
   `visited:false` does not prove this persisted placing room is untouched.
3. **Late nonsentinel shell hole admits.** After the first 512-cell shell slice,
   remove barrier local (0,4,5). The old worker commits ready and teleports the
   source visitor inside despite the hole still being air.
4. **Silent no-op seed becomes collected history.** Ignore all native setItem
   calls. Ready still commits, then ordinary claim polling marks all four
   rewards claimed because all four containers remain empty.
5. **Wrong native reward type accepted.** Replace each set effect with diamond;
   ready and seeded commit.
6. **Wrong amount accepted.** Write quantity 2 for every reward; ready commits.
7. **Wrong keepsake names accepted.** Preserve item/count but change all three
   names to `Wrong keepsake`; ready commits.
8. **Wrong keepsake lore accepted.** Preserve name/type/count but change lore;
   ready commits.
9. **Unexpected extra contents accepted.** Each effect also writes 64 diamonds
   at slot 8; ready commits.
10. **Preexisting contents overwritten.** Add 64 diamonds to first slot 0 and
    64 emeralds to second slot 8 during verification. Seeding overwrites slot 0
    while preserving the unexpected slot 8; ready commits.
11. **Late occupant not considered at seed boundary.** Move a native player to
    the generated arrival after structure placement; seeding still completes
    while that player is already inside. The placement occupancy check is stale.

A preserved-history control confirms existing ready reward depletion survives
return/reload/reentry with one total placement, and a migrated paid survivor
remains suppressed with four empty containers. Those protections must remain.

## Compatibility-safe invariant and design

Keep the schema-1 primary record, exact Guild source/cell/grid, reward ownership,
return tickets, geometry, ready/visited histories and paid/unknown suppression.
An optional first-build journal may distinguish newly witnessed work from old
`placing` records; an unmarked legacy placing record cannot establish whether
placement or any of four seed effects already occurred.

Only allocated + never visited + never seeded authorizes a first placement,
after a fresh native full-volume empty query and fresh player/entity absence.
Commit and verify a durable placement intent before that effect. Never replay
from any intent-only or prior placing record. A successfully returned placement
may acquire a separately persisted placed receipt; recovery from that receipt
performs read-only verification only.

After route/container/full-shell verification, reacquire all four inventories,
require all their slots empty and recheck occupancy. Persist and verify a seed
intent before any of the four native setItem calls. All native writes may be
partial or ambiguous: catch, silent no-op, wrong type/count/metadata, unexpected
extra slots, read failure, and property failure must all leave admission closed
and prohibit another item write. Reacquire all containers after the effects and
compare item ID, count, the three authored names/lore, and all unused slots.
Only exact readback permits a seeded receipt and then a ready commit.

A seeded receipt can retry ready persistence through read-only exact reward
verification. A seeding intent cannot infer success from empty contents or
retry effects. All job stages must remain bound to the same exact saved source,
cell, suppression and history and stop when that authority changes. Ready and
visited state must never authorize placement or inventory modification.

Fresh bulk shell checks are also needed at cached-room admission; a completed
spread scan alone can become stale. Keep engine durability, bulk-query cost,
non-script/native event ordering and simultaneous-player acceptance explicitly
unrun; these mocks demonstrate the bounded controller decisions only.

Portable predecessor reproduction: `python screenshots/validation/DP9/baseline-runner.py`.
The runner reads the actual GP21 controller via `git show`, captures current
unchanged Library geometry, and executes `baseline-probes.mjs`. Its successful
log is `baseline-reproduction.log`. The first helper launch attempted Node
child-process Git access and failed with EPERM; its original output is retained
in `baseline-reproduction-initial.log`. Moving that read to the Python runner
corrected the helper; no gameplay assertion was changed for this failure.

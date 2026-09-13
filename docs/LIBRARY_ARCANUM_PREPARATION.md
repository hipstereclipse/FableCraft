# Library Arcanum preparation and reward receipts

DP9, 2026-09-13. The older worker could replay a partially completed Library
structure and accept unchecked reward writes. The new worker preserves ambiguous
work and keeps admission closed. This is a bounded offline correction; engine
acceptance remains unrun and the portal pilot remains in-progress.

## Reproduced defects

Eleven probes execute the actual GP21 controller against voxels captured from
the actual Library builder. A failed second reward write followed by reload
causes another structure placement, erasing a later foreign block. Other probes
show that an early survey edit or containment hole can escape a sliced scan;
silent no-op, wrong item/count/name/lore and additional slot contents can commit
ready; existing container contents can be overwritten; and a late visitor does
not prevent seeding. The preserved-history control confirms old depletion and
paid suppression, which this change must retain.

`screenshots/validation/DP9/initial-audit.md` describes the injections and actual
observations. The original successful probe exit means the unsafe predecessor
behavior was reproduced; it does not mean that behavior was acceptable.

## Durable boundaries

The existing `fc_dp_guild_v1` schema-1 record, room phase names and return-ticket
schema remain. Newly witnessed preparation adds optional
`room.preparation = {schema: 1, phase: ...}`. The journal shares the original
source, room cell/origin/version, suppression and reward history in one record.
Each active job compares the complete record with its saved snapshot. Every
preparation write compares fresh authority and reads back the exact written
string before permitting the next native effect.

| Existing room phase / preparation | Permitted work |
| --- | --- |
| allocated, no preparation, never visited/seeded/claimed | Survey unused volume; fresh bulk air/occupancy check; persist placement intent |
| placing / placing, or unmarked legacy placing | Refuse replay and admission; effects may already have happened |
| placing / placed | Verify existing structure, complete shell, routes and empty inventories; persist seed intent |
| placing / seeding | Refuse inventory writes and admission; any of four writes may have happened |
| placing / seeded | Recheck exact existing rewards, geometry and occupancy; retry only ready persistence |
| ready or visited, including old records without preparation | Preserve structure and reward history; verify geometry for admission; retain recovery returns |

A successful placement call must acquire its `placed` receipt. A thrown call,
including one that changed blocks before throwing, never authorizes another
placement. A saved receipt can survive a later read failure or exception and
allow verification on a fresh retry. The same distinction applies to the seed
receipt. If the success receipt did not persist, admission stays closed; there
is no automatic repair command in this pass.

All 27 slots of all four containers must be empty before seed intent. Seeding
preserves the authored Elixir, two named books and named paper; suppressed rooms
write no items. Freshly reacquired native containers must show the exact item
type, amount, name and lore in slot zero and no unexpected contents elsewhere.
Partial throws, silent writes, stale handles, substitutions and failed readback
cannot commit ready or trigger another seed attempt. The worker never clears a
container to make these checks pass.

The sliced 67,228-cell air survey is followed by a fresh native full-volume
query before placement. The sliced 9,794-cell containment survey is followed by
six native shell-face queries before seed/ready acceptance. A complete shell
check also precedes each entry into a cached room. Fresh player/entity absence
is required before placement and seeding. A failure preserves the saved state
and the player remains at the source.

## Compatibility and limits

Existing ready/visited rooms do not need a new journal and never gain new block
or item writes. Old claimed/depleted rewards and migrated paid/unknown-history
suppression remain. Tickets still preserve exact-source return through lost or
replaced primary ledgers. Ordinary ready-room claim observation is unchanged.
Unknown legacy unfinished preparation is deliberately left closed because
`visited:false` cannot establish that no block/item effects occurred.

Only the handwritten Guild controller, its main adapter and regressions change.
No geometry, generated entities, dimensions, anchors, rewards, source mapping,
allocation grid, Arboretum controller or legacy personas change. Existing Guilds
are never rebuilt, and reanchor remains a coordinate refresh.

The actual retained Microsoft server 2.1.0 type file and current official
references confirm `containsBlock`, `Container.getItem/setItem/size` and
`ItemStack.getLore`. The adapter passes `allowUnloadedChunks:false`; an exception
or non-boolean result cannot count as a successful proof.
[Dimension reference](https://learn.microsoft.com/en-us/minecraft/creator/scriptapi/minecraft/server/dimension?view=minecraft-bedrock-stable),
[Container reference](https://learn.microsoft.com/en-us/minecraft/creator/scriptapi/minecraft/server/container?view=minecraft-bedrock-stable),
[ItemStack reference](https://learn.microsoft.com/en-us/minecraft/creator/scriptapi/minecraft/server/itemstack?view=minecraft-bedrock-stable).
The exact pinned type hash and inspected signatures are in DP9's API evidence.

Separate dynamic-property and container operations are not an atomic save.
Arbitrary external deletion/rollback of the full history, native save ordering,
bulk-query performance, loading, simultaneous Heroes, collision and collection
remain engine acceptance work. These mocks establish controller decisions under
injected effects, not the frequency of those faults in Bedrock. GP21 remains the
visual baseline; no new rendering can prove this runtime behavior.


## Validation result

All 55 base gates and 65 ESM syntax checks pass in the isolated reviewed-index
snapshot. The actual generated-voxel runtime passes 29 groups; the actual main
adapter passes 39. Independent review passes 34 cases. Its initial review found
two per-item defects after the first native write; each later write now checks
fresh history, occupancy and target emptiness. Both original reproductions and
final passing probes remain in evidence.

Two runtime development failures came from fixture expectations (a native
substituted property remains persisted, and reload requires leaving the portal
to rearm). Their original output and corrections are retained. The first
portable predecessor helper hit Node child-process Git EPERM; the revised
Python-owned Git read passes and its original failure remains. The full
55-gate snapshot run had no failure.

Fresh 36-asset C2 and Guild diagnostics pass. Every structure asset/C2 image and
all seven visual owners match GP21. Full 282-PNG and seven Guild documentation
scene renders are retained from those unchanged inputs, not rerun. Only the
Guild controller and its main adapter change among 1,662 snapshot pack files;
no generated asset was edited or regenerated. Protected unrelated files retain
their original hashes. GP21 exact-commit CI 34740634798 passed. Native acceptance
remains unrun; the legacy scoreboard remains 45 leaves and 7 done.

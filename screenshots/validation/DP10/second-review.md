# DP10 second review

No production blocker found in the reviewed Arboretum preparation change.
Reviewed owner SHA256:
`d66d184a9a8a87587dab054209fab8a69c658a663edec0e1f119eb2531c25125`.
The live owner still matched the retained `owner-reviewed.js` after all checks.
All reviewed source/test hashes are in `source-hashes.json`.

The comparison was against the captured GP22 owner in
`tmp/conformance/dp10-integration-audit/arboretum-owner-before.js`
(SHA256 `d2ea54066b594d57a3b9432c2a3b11edc85b41d08f2305caf96122c7ce9e7557`).
The review inspected the actual owner diff, modified runtime/integration fixtures,
the earlier native-effect reproduction helpers, and the retained independent
22-case review. No production file was edited by this review.

Results:

- Arboretum runtime: 35 groups pass (`runtime.log`).
- Actual main integration: 20 tests pass (`integration.log`).
- Independent retained review: 22 probes pass (`independent.log`).
- Additional independent second-review probes: 6 pass (`extra-final.log`).

The six added probes check late history/player/shell changes made by the native
seed effect, depletion during seeded-receipt persistence, same-revision history
changed by successful native placement, and exact-ticket return after an unknown
optional preparation schema makes the source record unreadable. All preserve
the established boundary: effects are not replayed, incomplete authority is not
admitted, later saved history is not replaced, and an occupied exact-ticket
return remains available without reconstructing room history.

The initial extra helper had five passes and one fixture assertion error: the
existing `inside()` fixture returns a source point, while the assertion treated
that return as a ticket. `extra-initial.log` retains the failure. The final helper
reads the ticket from its actual saved player property. The production owner
did not change to resolve that assertion error.

The final input-hash guard detected a concurrent change to the shared independent
helper: its author added only the crypto import and owner-SHA256 log line. Removing
those exact two lines reproduces the initial helper hash. Both helper versions,
the original input hashes and this correction are retained locally. Production
owner/main/test hashes remained unchanged; no additional production run was needed.

Specific reviewed contracts:

- Optional schema1 preparation phases distinguish intent from successful saved
  placement/seed receipts; old ready records may omit preparation.
- The active job pins its full original record; preparation writes compare the
  fresh full record, save, read back and refresh the job authority.
- Native placement requires fresh empty volume, occupancy and authority after
  the intent write; a thrown call cannot be replayed even with complete pixels.
- All 27 slots must be empty before seed intent and again before the native
  write. The native chest is reacquired after intent and after the effect.
- Seed verification checks exact type/amount/name/lore and all unused slots,
  followed by geometry, full containment, occupancy and fresh history checks.
- Seeded receipts retry through read-only validation. Legacy ready depletion,
  reward claims and occupied exact-source tickets retain their prior behavior.
- No source/room geometry, third-family contract, native API version, allocator
  grid, established outer schema or Guild controller was changed by this patch.

The tests inject native effects and durable-property failure boundaries; they
do not run Bedrock. Property/item effects remain separate saves, not an atomic
transaction. External deletion or rollback of all history is not solved.
Native loading, crash persistence, travel, collection and multiplayer acceptance
remain unrun. The reviewed synchronous checks do not establish native collider,
chunk-cost or world-save semantics.

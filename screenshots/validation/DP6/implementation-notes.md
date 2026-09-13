# DP6 — preserve unreadable committed return tickets

Working-tree-only implementation, 2026-09-12. Production ownership is confined to
`packs/Fablecraft_BP/scripts/fc_demon_doors.js`; regression additions are in
`scripts/tests/demon_door_integration.test.mjs`. No main adapter, generation,
geometry, reward schema or activity code changes are required. No staging or
commits were performed by this subtask. The independent GP19 baseline audit and
its results remain unchanged.

`readTicket` now returns availability separately from its validated ticket value.
An unavailable read skips the affected periodic player reconciliation or checked
return before a ticket write or teleport. A confirmed absent/invalid ticket can
still use the existing primary-ledger orphan recovery. The same local snapshot
feeds matching, original-cell occupancy and entry/return decisions in a synchronous
operation; it is never cached across ticks. Public `requestReturn` still takes
only the player and performs a fresh read; periodic dwell uses a private helper
with that tick's already-validated snapshot.

DP5 read-only protections still ignore a single unreadable player's contribution
while protecting the current ledger cell and any other readable ticketed visitors.
Nothing reconstructs world history, reseeds rewards or changes shared claim policy.
A deferred arch click uses the existing main callback and the newly guarded public
return path, so no main.js change is needed.

The five added adapter groups cover all four committed ticket phases; repeated
unavailable reads; normal exit dwell after recovery; direct diagnostic returns;
arch-floor and arch-light clicks with failure beginning before or after deferral;
confirmed absent/corrupt/invalid fallback; healthy old-cell visitors alongside an
unreadable visitor across all five primary-ledger failure/replacement modes; and
one fresh ticket snapshot per periodic operation. The exact approach stays clear
while all default candidates are deliberately blocked, proving that preserving
saved source data enables return that the former fallback could not perform.

`adapter-baseline-final-red.log` runs the final 38-group test file against the
captured pre-DP6 controller: 35 pass and three new groups fail. The baseline fixture
copies the same current main adapter, aperture and generated data plus final test
source under ignored `tmp/conformance/DP6-baseline-fixture/`, replacing only the
controller with `baseline-controller.js.txt`. The earlier red/first-green logs
record development before adding the final one-read-per-operation regression.

Final checks: 38 adapter groups, 13 actual generated-room runtime groups, four
aperture groups, controller lint and syntax checks pass. Exact command/source/log
hashes are recorded in `implementation-provenance.json`. Broader reviewed-snapshot/base validation
belongs to the root checkpoint workflow and is not claimed here.

Native acceptance remains unrun. The injected failure makes the player property
read unavailable while its saved backing string and write API remain available;
this proves the controller's handling, not the frequency or crash semantics of
that fault in Bedrock. Player displacement, actual collection, chunk loading,
persistence and two-Hero engine behavior retain their earlier manual gaps.

# DP9 final independent preparation review

2026-09-13. **34 independent actual-module observation cases pass; no unresolved
blocker reproduced in this bounded review.** No production edits were made by
this reviewer. Native Bedrock acceptance remains unrun.

The final reviewed owner is frozen in ignored `fc_demon_doors.review2.js`; its
SHA-256 is recorded in `review2-sha256.txt`. The final executable probe file is
`review2-probes.mjs`, with complete retained output in `review2-probes.log`.
Do not commit the full frozen owner or fixture duplicate; copy the findings and
logs/hash into milestone evidence as appropriate.

Run from repository root:

```sh
node --experimental-vm-modules tmp/conformance/dp9-audit/review2-probes.mjs tmp/conformance/dp9-audit/room.json
```

The probe evaluates actual owned production JavaScript against actual generated
Library voxels, with injected native block/inventory/property effects. It does
not duplicate the controller implementation.

The review covers:

- Twenty-four intent/receipt outcomes: before-write throw, after-write throw,
  silent drop and substituted source at all six allocated/placing/placed/
  seeding/seeded/ready transitions. Across retries and reloads, each scenario
  retains at most one room placement and four attempted native seed writes.
- Both reproduced review1 boundary defects are fixed. Replacing history during
  the first seed now stops with one native seed attempt and preserves the new
  ready/visited/claimed record. Filling the second target during the first seed
  now preserves its 64 diamonds, stops at one seed attempt, and never resumes
  seeding after reload.
- A late edit to an already-surveyed air cell prevents first placement and
  preserves the foreign diamond block.
- An already-scanned nonsentinel shell hole prevents seeding/admission. A new
  hole in a cached ready room also prevents entry without reconstructing it.
- A native placement that completes then throws never replays or seeds.
- An old unmarked placing record preserves foreign inventory and never replays
  placement or authorizes seed effects.
- A second native seed that transfers its item then throws preserves partial
  effects without retrying or admitting.
- An unmarked legacy ready room preserves depleted reward history and its sole
  placement. Paid history still suppresses all four item effects.
- Missing native bulk-query authority prevents placement and item effects.

Prior evidence remains intact. `baseline-probes.log` records eleven predecessor
defects and one preserved-history control. `review1-probes.log` records the first
patch's passing journal matrix and its two initially reproduced per-item holes;
`review1.md` explains those holes. `review2-probes.log` records their correction.

This demonstrates bounded controller decisions under injected effects. It does
not establish engine crash durability, bulk-query performance, synchronous
native event ordering, natural-world mutation, or multiplayer acceptance.

A portable copy of the final probes is retained here as `review-probes.mjs`.
Run `python screenshots/validation/DP9/review-runner.py` from a fresh checkout;
the helper captures current generator voxels and reads the current controller.
`review-reproduction.log` records the root rerun of this portable helper.

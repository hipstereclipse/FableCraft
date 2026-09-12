# Library Arcanum return and history recovery

DP3 implementation, 2026-09-12. This bounded pass fixes three runtime defects
in the existing Guild pilot. The room asset, version-1 storage contract, API
version, challenge, rewards and ordinary scattered doors are unchanged. Live
Bedrock acceptance remains unrun. The containing DP3 commit is recorded in the
supplemental priority ledger; this pass does not change C3's 45-leaf denominator.

## Reproduced defects and resulting behavior

1. **Normal source maintenance could revoke an old visitor's return ticket.**
   The prior emergency path accepted a committed ticket only while the primary
   world ledger was missing or unreadable. If that ledger was missing and a
   second player approached the Guild, the actual 40-tick adapter recreated a
   valid record with `room:null`. The visitor was still inside the original
   cell, but return then refused the new valid record, including the diagnostic
   command. The saved ticket remained present and no teleport occurred.

   A valid committed ticket now remains authority for its exact occupied
   Overworld cell even if the primary record names another cell or no room.
   Recovery uses that ticket's original source and retains it on an unavailable,
   blocked or failed return. It never borrows the replacement record's source
   alternatives, recreates a room, or resets unlocks, reward claims or contents.
   Normal periodic dwell at the original cell's exit also uses that cell's
   return arch after ledger replacement or while the ledger remains missing,
   corrupt or temporarily unreadable. The latter case previously required the
   diagnostic command and stranded a lone visitor trying to walk out normally.
   Without readable world state, only a valid occupied ticket can enter the
   exit-dwell path; source admission, room construction and reward work remain
   disabled. A ticket outside its exact cell, in another dimension, or with
   invalid fields authorizes no recovery travel.

2. **A failed history read could classify a paid face as unpaid.** The main
   adapter successfully selected an open legacy face; a second property read
   inside registration then threw. The swallowed error persisted
   `surviving_closed`, `unlocked:false` and `suppressed:false`, even though the
   surviving face still had `fc_door_open:true`. A later unlock could therefore
   authorize the new room rewards incorrectly.

   An exception while reading either legacy open/payment metadata or its old
   index now defers registration before any world record, replacement or face
   removal. A later successful read preserves the open state and suppresses new
   rewards through the existing legacy migration. A failed read provides no
   evidence that rewards were unpaid.

3. **Fractional return feet could miss a newly obstructed head cell.** A safe
   approach captured during a jump can record feet at y65.75. If another player
   later adds a ceiling at y67, the old two-integer-cell test accepted that
   target even though a standing 1.8-block collider intersected the ceiling.
   Native teleport rejection repeatedly selected the same blocked target,
   despite the existing same-door fallback at y65 having clearance.

   The clearance test now checks every cell intersected by the standing height
   from the actual fractional feet. The obstructed exact approach is rejected
   before travel, allowing the existing checked same-door fallback to be chosen.
   Native `tryTeleport(..., checkForBlocks:true)` remains the final movement
   check. The regression models full-height collision rejection; it is not a
   claim of live engine execution.

## Ownership and verification

`packs/Fablecraft_BP/scripts/fc_demon_doors.js` owns all three fixes. The actual
main adapters and periodic callback are executed by
`scripts/tests/demon_door_integration.test.mjs`; main itself required no edits.
All previous source-aperture and generated-room behavior remains covered.

The [DP3 evidence directory](../screenshots/validation/DP3/) contains:

- `adapter-red.log`: the three initial new regression groups fail against the
  prior runtime, with all twelve previous adapter groups passing.
- `clearance-red.log`: the fractional-ceiling regression fails after the first
  two fixes, with the other fifteen groups passing.
- `lone-visitor-red.log`: the focused lone-visitor exit-dwell regression fails
  before the missing/corrupt/unreadable-record periodic path is repaired.
- `adapter-final.log`: nineteen actual-adapter groups pass, including all seven
  new groups, replacement-ledger interleaving, automatic original-arch return,
  lone-visitor missing/corrupt/unreadable-ledger exits, denial of unticketed or
  invalid-ticket occupants in that same periodic path,
  false/throw/throw-after-movement returns, invalid or misplaced tickets,
  blocked original sources and unchanged replacement reward ledgers.
- `runtime-final.log`: all thirteen existing runtime groups pass against the
  actual generated Library Arcanum, including reward depletion, simultaneous
  independent return sources, death/reload, legacy reward suppression and
  refusing reconstruction of a damaged visited room.
- `aperture-final.log`: all four existing bounded mouth-migration groups pass.
- `portal-lint.log`: the changed runtime module passes lint.
- `provenance.json` and `baseline-portal.js.txt`: the baseline source, reviewed
  source/specification hashes, commands, outcomes and captured-log hashes.

Commands, from the repository root:

```sh
node --experimental-vm-modules scripts/tests/demon_door_integration.test.mjs
python scripts/tests/test_demon_doors.py
node --experimental-vm-modules scripts/tests/guild_door_aperture.test.mjs
node_modules/.bin/eslint packs/Fablecraft_BP/scripts/fc_demon_doors.js
```

## Final offline validation

DP3 passes all 39 base gates from `tmp/conformance/DP3-reviewed-snapshot`, including
19 actual portal adapter groups, 13 generated-room runtime groups, 4 aperture
migration groups and all Guild cave/resident/training/defence suites. ESLint and
spells are included in the base gates; all 62 BP scripts also pass ESM syntax.
Independent review of the no-ledger exit path found no remaining blocker after
adding unticketed/invalid-ticket periodic negatives. No visual asset or rendering
owner changed: the GP6 full rendering pipeline and GP5 Guild diagnostics are
reused with byte-identical dependency hashes in additional-results.json.
Both GP5 and GP6 exact-head remote CI passed. All live Bedrock acceptance is unrun.

## Remaining acceptance and next door refinement

The original [pilot contract](LIBRARY_ARCANUM.md) and its live acceptance list
still apply. Actual chunk loading, entity metadata failures, full-height player
collision, two-player returns and crash persistence remain unrun in Bedrock.
Complete record loss still cannot reconstruct the old room's unlock/claim
ledger; recovery preserves the committed way home without inventing that lost
history. If both world and player records are lost, the source is unknowable.
Both normal exit dwell and the diagnostic command can use a valid occupied
ticket without reconstructing a missing/corrupt ledger. Recovery still requires
the recorded original source to load and provide safe clearance.

The separate original-image comparison, player-height lighting and room fidelity
review remain open. A later bounded adapter pass should also reconcile an
explicit disagreement between `fc_guild_door` and the durable door source: the
current replacement adapter still queries/spawns from the former while face
matching trusts the latter. An injected mismatch produced repeated unkeyed
faces; ordinary current reanchor does not alter the Guild door, so this is a
separate persisted-data inconsistency case, not a change included in DP3.

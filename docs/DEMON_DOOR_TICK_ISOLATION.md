# Independent Demon Door maintenance and return ticks

DP8, 2026-09-13. A Library reward-claim write failure could prevent an otherwise
healthy Arboretum visitor from walking home. Both families ran in one five-tick
callback, with Guild work first. After ordinary chest depletion, a before-write
exception on `fc_dp_guild_v1` escaped `guildDoorPilot.tick()` and skipped the
Arboretum tick. Twelve consecutive callbacks reproduced twelve exceptions and
zero dwell returns. The same visitor's exact ticket still returned through the
direct own-family command. Healthy and after-write controls returned normally.

The actual main callback now isolates four operations: Guild face maintenance,
Arboretum face maintenance, Guild runtime tick and Arboretum runtime tick. Each
failure reports its operation and permits subsequent work. Diagnostic reporting
also has a guarded boundary. Runtime cadence remains five ticks and face
maintenance remains forty ticks. Failed work retries through its existing owner;
this does not roll back partial effects or add a new persistence interpretation.

Only handwritten `main.js` and the actual adapter fixture/tests change. Saved
schemas, source identity, allocation, native containers, ticket reads, return
clearance, build preparation, rewards, room geometry and both controllers retain
their owners. An unavailable own-family ticket still defers; the change does not
infer authority from a sibling's healthy tick. A long-running synchronous native
operation can still delay the callback; exception isolation is not a time budget.

## Verification

The final actual-adapter suite passes twenty groups, including four new groups:

- Healthy, before-write, after-write and failed-warning controls retain exactly
  one Arboretum dwell return and the saved exact approach.
- Arboretum preparation reaches ready with one physical Pickhammer seed while
  Guild claim persistence remains unavailable.
- Each face-maintenance read failure leaves both runtime operations running;
  later maintenance retries on the same cadence without a source replay.
- An injected outer Arboretum failure leaves the preceding Guild dwell return
  intact and is reported. The fixture explicitly distinguishes this scheduler
  injection from naturally caught Arboretum API reads.

`python screenshots/validation/DP8/compare-predecessor.py` runs the same final
suite with only main's input replaced by the actual DP7 commit. All four new
groups fail there while the sixteen earlier groups pass. Original red output,
commands and source hashes are retained. Both room owners and actual generated
room voxels execute in the adapter harness; a native engine is not involved.

All 55 isolated reviewed-index base gates, 65 ESM checks, fresh C2 and Guild diagnostics pass and are
recorded in `screenshots/validation/DP8/`. Full image evidence is retained from
DP7 because every structure, C2 image and rendering input remains identical.
No full render is represented as rerun. The legacy score remains seven done
among forty-five leaves. DP8 remains in-progress pending native acceptance.

## Remaining work

Native return dwell, loading cost, simultaneous Heroes, collection, reconnect and
saved-world persistence remain unrun. The older Guild first-build worker still
permits documented unvisited `placing` retries and seeds before committing ready.
Audit its preparation receipts, interrupted partial seeding, native write
read-back and late shell/volume changes separately before modifying that legacy
contract. The Arboretum's more conservative preparation is not evidence that the
Guild now has the same behavior. Continue reference-led Guild improvements and
individual canonical reward worlds without closing their open acceptance.

# GP17 deferred relationship evidence

The baseline is DP5 commit `732670a83bcd7909858ca4480c31f5dc8aeeb8ad`.
The saved ignored baseline `main.js` and `guild_training.js` bytes match that
commit exactly. `baseline-source-hashes.json` records their source hashes and
the predecessor validation entry point. No raw source snapshot is committed.

The actual production declarations are extracted through Espree in
`scripts/tests/guild_relationships.test.mjs`; the actual sibling
`guild_training.js` executes in the fixture. Bedrock entities, forms, inventory
and presentation are mocked. The fixture includes separate single-ring slots
matching the generated ring's stack limit, deferred synced-property visibility,
faults before/after mutation and distinct wrappers sharing backing state and IDs.

Recreate the saved baseline in an ignored directory from the repository root:

```sh
mkdir -p tmp/conformance/gp17/baseline
git show 732670a83bcd7909858ca4480c31f5dc8aeeb8ad:packs/Fablecraft_BP/scripts/main.js > tmp/conformance/gp17/baseline/main.js
git show 732670a83bcd7909858ca4480c31f5dc8aeeb8ad:packs/Fablecraft_BP/scripts/guild_training.js > tmp/conformance/gp17/baseline/guild_training.js
```

Run the same regression suite against predecessor and resulting production:

```sh
FC_RELATIONSHIP_SOURCE=tmp/conformance/gp17/baseline/main.js node --experimental-vm-modules scripts/tests/guild_relationships.test.mjs
node --experimental-vm-modules scripts/tests/guild_relationships.test.mjs
node --experimental-vm-modules scripts/tests/guild_training.test.mjs
```

The expected predecessor exit code is **1**, with **19 failures and 5 passes**.
The resulting relationship suite exits **0**, with **24 passes**, and the
existing training suite exits **0**, with **33 passes**. The actual outputs and
commands are retained in [focused-commands.json](focused-commands.json),
[relationship-regression-before.log](relationship-regression-before.log),
[relationship-regression-after.log](relationship-regression-after.log) and
[training-regression-after.log](training-regression-after.log).

The portable probe uses the same committed fixture prefix without copying the
production callbacks. It generates only an ignored runtime script, reads the
selected source and emits JSON observations with source hashes:

```sh
python screenshots/validation/GP17/probe_relationship_authority.py --main tmp/conformance/gp17/baseline/main.js
python screenshots/validation/GP17/probe_relationship_authority.py
```

Both probe commands exit zero; their observations are retained as
[relationship-probe-before.json](relationship-probe-before.json) and
[relationship-probe-after.json](relationship-probe-after.json). They show:

- Two pending proposals consume two rings and replace the first owner before;
  after, only the first accepted proposal commits one ring/reward/list entry.
  The result holds with immediate and next-tick synced-property visibility.
- An old nested divorce clears another owner's marriage before; after, it
  changes no properties, inventory, reaction, list or morality.
- An old spouse Follow interrupts actual Guild training before; after, that
  callback makes no changes and the training token remains active.
- A required list setter throwing after mutation consumes a ring and leaves
  partial completion before; after, attempted state is restored, including
  queued next-tick properties, and no ring is consumed.
- A normal proposal with one real nonstackable ring succeeds before and after.

These observations establish bounded callback and failure handling at mocked
engine boundaries. They do not establish native UI ordering, multiplayer/save
acceptance or an atomic transaction across inventory and saved properties. The
[relationship contract](../../../docs/GUILD_RELATIONSHIP_AUTHORITY.md) describes
uncertain payment and rollback limits. All native acceptance remains **unrun**.

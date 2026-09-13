This is the retained pre-repair audit note. Its scratch paths and line numbers
refer to that checkpoint. Reproduce the defect with the committed
`compare-predecessor.py`; its final fixture generates the required room voxels.
The original prose and raw result remain below.

# DP8 independent return audit

Production files were not edited. `probe.mjs` uses the actual current main interval
callback, both actual runtime controllers and the current owned source/room voxels.
It derives only dependency setup from the existing main integration fixture. The
fixture is extended to recognize Library barrels and expose the actual interval;
the main callback and runtime functions are not reimplemented.

The test supplies an already-ready Guild v1 room with its actual generated
containers, plus a valid occupied Arboretum return ticket and exact safe source.
It removes the existing Guild elixir from its native-container fixture, then
injects failures at the dynamic-property write boundary. This is an injected
failure proof, not an observed Bedrock failure or frequency estimate.

## Reproduced defect

`fc_demon_doors.js:521` reads the latest ready state and line 523 calls its
unchecked `save` to persist a newly collected item. A before-write exception
escapes `tick()` because this claim block is outside its per-player catch.
The actual `main.js:3366` Guild tick precedes Arboretum at line 3367 in one
unguarded periodic callback. The escaped Guild exception prevents Arboretum's
otherwise healthy dwell return from executing.

- Healthy control: one periodic return, zero exceptions.
- Guild claim before-write failure: zero periodic returns over twelve callbacks,
  twelve exceptions, exact Arboretum ticket untouched; immediate direct own return
  still succeeds to the saved exact source.
- Guild claim after-write failure: the state commits despite one exception;
  subsequent callbacks execute and the Arboretum returns once.

This coupling is new to the shared two-family periodic callback. It can delay
all Arboretum room jobs, presentation and dwell travel, while click/command return
remains available. No lost ticket, duplicate reward or native crash is claimed.

The minimal bounded repair is to contain errors independently around each owner
at the shared maintenance/tick boundary, log the affected family/operation, and
continue the other owner. Preserve the existing periodic cadence and all saved
Guild/Arboretum schemas. Tests should execute this actual callback, exercise
before/after write failures and show healthy return and room preparation progress.

## Other observations

The Arboretum controller already guards ambiguous placement/seeding, exact
read-back, late empty-volume/shell checks, exhausted revisions and healthy
ticket-owned returns through unavailable primary records. No independent new
defect was established in those reviewed paths.

The retained Guild controller has weaker first-build preparation semantics: an
unvisited `placing` room is replayed after a preparation failure, reward writes
have no exact read-back, and no late native bulk volume/shell check follows sliced
survey. Its permanent `interrupted private preparation resumes without duplicate
room reward` test and `LIBRARY_ARCANUM.md` explicitly retain that behavior. These
are separate hardening candidates; this audit does not claim they were newly
reproduced against actual controller effects or change their compatibility contract.

All native travel, loading, collection, multiplayer, collision, lighting and
crash/persistence acceptance remains unrun. `results.json` includes exact source,
fixture and generated-voxel hashes; `probe.raw.log` retains original output.

Reproduce with `node --experimental-vm-modules tmp/conformance/dp8-audit/probe.mjs`
after generating `geometry.json` from current `gen_structures` owners with
`Vox.save` replaced only by an in-memory capture (no production artifact writes).

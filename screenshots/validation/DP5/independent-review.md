# DP5 independent implementation review

Date: 2026-09-12. Read-only review of the unstaged DP5 door changes, independent
of the implementation author. **No blocking correctness finding was found in this
bounded source/adapter review.** Native Bedrock acceptance remains **unrun**.

## Scope and assessment

Read GP16's `door-followup-audit.md`, the unstaged semantic diff in
`fc_demon_doors.js`, the door block-interaction callback in `main.js`, and the
existing plus eight added adapter test groups. The separately staged GP16 Skill
change is outside this review. Read the surrounding validation, ticket, return,
maintenance and reward paths in the production pilot and the relevant Library
pilot/design contract.

- `protectedOrigins()` preserves the current validated room even when empty and
  adds each loaded player's own occupied ticket cell. Cell-keyed deduplication
  permits simultaneous old cells and a current replacement allocation without
  choosing one visitor's authority for another.
- Raw tickets retain the existing schema, door identity, finite supported source,
  cell-range and travel-phase checks. The added catches isolate unreadable ticket
  or player handles. A false `isValid`, a mismatched dimension, another cell or an
  out-of-bounds physical position contributes no old-room authority. A failed
  player scan retains the current ledger allocation and does not invent old ones.
- Block guards use the exact bounded volume and explicit Overworld dimension;
  generation guards retain the existing 160-block horizontal margin and apply it
  at every height. Invalid positions and unrelated/other-dimension locations stay
  outside those protections. Break, interaction, explosion, scatter and boss
  callbacks now consume the union rather than only the current ledger cell.
- `occupiedOrigin()` makes return-arch recognition use this player's occupied
  ticket first, with the existing authoritative current-room fallback. It does
  not borrow another player's ticket. The callback snapshots the clicked block
  coordinates and dimension, then rechecks those coordinates against the same
  player's occupied origin after `system.run` deferral. Leaving the room, moving
  into the replacement cell, changing dimension or losing old-room ticket
  authority prevents the queued click from causing a return.
- The deferred callback calls the existing `requestReturn`; it does not add a
  new destination or fallback. Recovery across a missing/corrupt/unreadable/
  recreated/replaced primary record continues to use the committed ticket's
  original source only. Failed travel keeps the ticket; confirmed travel clears
  it. Ordinary non-sneaking chest/barrel access remains allowed, while sneaking
  building interactions remain cancelled.
- The protection/origin helpers contain no save, placement, reward, admission or
  repair operation. The change does not reconstruct world history. The recovery
  click performs only the existing return path's player-ticket and transient
  loading-lease work; it does not write world progress, reseed rewards or rebuild
  the room. Added tests compare the exact primary-record string before/after,
  including the replacement record's nonuniform claimed-reward state.

## Independent verification

These commands were independently executed from the repository root and exited 0:

```sh
node --experimental-vm-modules scripts/tests/demon_door_integration.test.mjs
python scripts/tests/test_demon_doors.py
node --experimental-vm-modules scripts/tests/guild_door_aperture.test.mjs
```

Results: **33 actual-module adapter groups, 13 generated-room runtime groups and
4 aperture groups passed.** The adapter fixture parses the production main source
and runs the real relevant callback bodies with the owned pilot/aperture/data
modules at injected engine boundaries; it does not substitute a second protection
implementation. The generated-room suite exercises the actual serialized Library
geometry through its existing fixture. Node emitted its ordinary experimental VM
module warning, not a test failure.

The new coverage includes all five primary-record failure/replacement states;
current plus two old occupied cells; invalid/unreadable players; failed player
scan; all committed ticket phases; missing/corrupt/invalid/wrong-cell/source tickets;
out-of-bounds and cross-dimension occupants; both return landmark heights; failed
then successful exact-source return; and invalidated deferred clicks. The scatter
and boss cases exercise actual callback dispatch, with an ordinary-world positive
control after moving the player outside the protected cells. Assertions also
preserve unrelated explosion blocks, native container access, primary history and
zero structure placements.

## Limits retained

Old room recovery protection intentionally depends on a currently detectable
loaded occupant with valid ticket and physical position. If all such occupants
leave or their authority cannot be read, the controller does not infer a permanent
or historical allocation. A player-scan failure therefore preserves the current
ledger allocation only. This is consistent with the bounded DP5 contract and is
explicitly tested; it is not a claim of durable protection for unknown rooms.

The deferred click rechecks original-cell authority, not the player's exact
in-cell distance from the clicked block. Initial interaction is supplied by the
engine; this pass does not redefine native reach/collision behavior. Actual event
ordering, explosion effects, chunk loading, commands, fluid/fire behavior,
watchdog/performance, travel, persistence and two-Hero movement have not been
validated inside Bedrock. No engine or whole-door conformance status is closed by
these results. No source changes or staging were performed by this reviewer.

## Reviewed working-file byte hashes

These SHA-256 values identify the working source at review time. Full `main.js`
also contains the independent GP16 Skill work; the reviewed door diff was limited
to its return-block callback.

| Path | SHA-256 |
| --- | --- |
| `packs/Fablecraft_BP/scripts/fc_demon_doors.js` | `aee84404ebb7f8b5ebc63b7b584de2e1c08918e67094dc2d9e762044e6035b62` |
| `packs/Fablecraft_BP/scripts/main.js` | `ce3ab2e866663102ce86e1e0cfe18b836983b394313d4e91e372e5369ac261c2` |
| `scripts/tests/demon_door_integration.test.mjs` | `b739f75deed73f8d9ae50f056b3b1d1f44fad6c7394191a3d939bbb147b9e3f0` |

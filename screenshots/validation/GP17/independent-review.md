# GP17 independent final relationship review

Date: 2026-09-12. **No blocking correctness finding was found in the final bounded
relationship-form change.** The review was read-only; no production/test edits or
staging were performed. Native Bedrock acceptance remains **unrun**.

## Reviewed behavior and compatibility fixes

Read the unstaged romance-only `main.js` diff and surrounding production helpers,
the complete `guild_relationships.test.mjs` fixture, GP17 root findings and API
provenance, the generated wedding-ring item, and relevant pinned
`@minecraft/server` 2.1.0 declarations.

`readRelationship` now supplies strict mutation authority independently of the
legacy permissive boolean helpers: both handles must remain valid, their IDs must
be nonempty, their dimensions must match, positions must be finite and within six
blocks, and marriage/opinion/owner/spouse-list reads must be valid. Inconsistent
partial ownership and malformed/unreadable history defer. Missing player list
history alone is treated as a new empty list; corrupt history is preserved rather
than replaced with a default.

Every accepted proposal, spouse choice and nested divorce confirmation rereads
that authority. Form continuations also retain the captured IDs and original
dimension. The registry is keyed by stable player/NPC ID pairs, not wrapper
identity. New same-pair forms supersede old ones; relationship mutations
invalidate all tracked forms for that NPC. Responses are consumed once, old
rejections cannot erase a newer token, requests expire after 2,400 game ticks,
and the registry is capped at 128 entries containing primitive identity/timing
information. This closes same-Hero divorce/remarry revival and separate-wrapper
supersession without storing entity handles in the registry.

The pinned API says entity-property writes apply next tick. The changed rollback
explicitly writes the prior value for attempted deferred writes even when the
same-tick getter still returns that prior value. The fixture exercises both
immediate and next-tick property behavior, including setters that throw after
queuing. Immediate ownership reservation blocks a competing proposal during the
pending-property interval; inconsistent authority after divorce similarly prevents
same-tick repetition.

The generated wedding ring has stack limit one. Payment uses a captured inventory
slot with type/count checks, a cloned item for any legacy remainder, and confirmed
post-write contents. It does not use `isStackableWith`, which is unsuitable for
this nonstackable item. All required relationship writes precede the one-ring
debit. A demonstrably unpaid failure attempts guarded rollback. An ambiguous or
unreadable post-debit result retains reserved ownership and performs no duplicate
refund, morality grant or success presentation. Optional cosmetic failures do not
reopen an already committed relationship.

Spouse choice authority is checked before love changes, Follow/neutral events,
gifts or opening a nested divorce form. The nested confirmation checks again.
Successful divorce removes only the selected NPC ID from the current player's
strictly read list and applies its penalty once. Existing resident identity,
unrelated spouse entries and the training reaction hook remain intact.

## Independent execution

Executed from repository root, exit 0:

```sh
node --experimental-vm-modules scripts/tests/guild_relationships.test.mjs
```

All **24 production-source relationship groups passed** independently. The fixture
extracts actual main declarations and evaluates the actual training owner at
injected engine boundaries. It includes real stack-one ring slots and a pending
entity-property queue; no alternative relationship implementation is substituted.

An additional independent probe extracted that fixture prefix into
`/tmp/gp17-relationship-independent-probe.mjs` and ran with:

```sh
node --experimental-vm-modules --input-type=module < /tmp/gp17-relationship-independent-probe.mjs
```

The executed probe bytes are retained as [independent-extra-probe.mjs](independent-extra-probe.mjs), with the tool-returned result recorded in [independent-extra-results.json](independent-extra-results.json). Raw stdout was not saved separately at execution time.

All **17 extra cases passed**:

- Fifteen cases injected unreadable marriage, opinion or player spouse-list state
  after a valid spouse menu opened, across every actionable choice `0..4`.
  No relationship, inventory, reaction, nested form or presentation action occurred.
- A silently ignored inventory debit was detected by readback. After flushing
  queued entity properties, the complete prior relationship/inventory snapshot
  was restored and no wedding morality event was issued.
- A successful debit followed by unreadable confirmation retained the recorded
  owner and queued marriage, consumed only one ring, issued no success morality
  event and rejected another Hero's marriage attempt without further payment.

Node emitted the ordinary experimental VM-module warning; no test failed.

## Scope and remaining limits

This is protection for deferred relationship forms and their commit paths. The
standalone held-gift path, generic social reactions and the underlying Follow/Wait
movement behavior remain separate work. A neutral reaction is not proof of native
stationary Wait behavior. Requester-specific activity arbitration, navigation,
training/defence precedence in the engine and purposeful arrival remain open.

Inventory and entity/player dynamic properties are separate engine stores. The
change does not promise atomic crash recovery or universal rollback after
unreadable/failed writes. Ambiguous incomplete history can remain reserved and
inert; the code avoids converting that ambiguity into another ring consumption or
ownership replacement. The fixture models the declared next-tick property
semantics, but actual native event ordering, wrapper lifecycle, inventory failure
modes, multiplayer timing, saved-world persistence and UI behavior remain unrun.
Existing dialogue, love thresholds and Follow wording remain chosen gameplay
adaptations; this review supplies no new original-TLC behavior evidence.

## Reviewed byte hashes

Full `main.js` includes prior committed changes; this review covered its GP17
romance diff. The temporary probe is local read-only evidence, not a pack asset.

| Path | SHA-256 |
| --- | --- |
| `packs/Fablecraft_BP/scripts/main.js` | `3de202b284cde2acb20f22361b007570fb8154368d6d03fc3c22ea80d01122f8` |
| `scripts/tests/guild_relationships.test.mjs` | `ef1bafd464b907e5a3b6be12cf60a161a92aad8571a33a8c181465e86b3d6d17` |
| `packs/Fablecraft_BP/scripts/guild_training.js` | `baf0ff28090d771fb94b4884090e8cf45ba387aa9a6c3cbe7148082e9a70db41` |
| `packs/Fablecraft_BP/items/wedding_ring.json` | `28091c23f15d724310d86c727012c648ef32e34ab2c70441f2ec19f52646a420` |
| `tmp/conformance/gp17-activity-audit/index.d.ts` | `38e989f3f0371967c1df82a12d5f37a3832cbff3944e38be8bb51638ed0e771d` |
| `/tmp/gp17-relationship-independent-probe.mjs` | `219f5b5b57d96de16c601d8491a35a0693699c819df3106b4685f796bebbee59` |

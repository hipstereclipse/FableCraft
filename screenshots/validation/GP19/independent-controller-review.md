# GP19 independent controller review

Disposition: **no remaining blocking finding in the reviewed controller**.
The final source is `packs/Fablecraft_BP/scripts/guild_activity.js`, SHA-256
`9571f7cabb92799874ec4adb0481887dca9d4a644c69648e14e604e281f3fa19`.
This review covers the controller authored by the implementation agent. The
reviewer authored the generated native groups and their Python fixture, so this
is not an independent sign-off of those generator changes. Root and the other
reviewer cover production integration.

## Persisted authority and cleanup

The controller distinguishes a new journal from an unavailable established one
through the persistent initialization witness. Invalid schema, base, identity,
revision, holder list or witness cannot become empty authority. Follow records
must contain their owner's holder obligation before the queued native barrier;
Wait records cannot contain holder debt. Player and entity tags are checked
derived effects, not an alternative source of requester ownership.

Reconciliation stops loaded native activity when authority becomes unavailable,
and reacquires the journal's original entity ID even when another candidate is
reported for its slot. It does not enroll that replacement or rewrite resident
history. Returning a different wrapper for the same stable ID is supported.
An absent previous player remains an outstanding cleanup obligation; absence
alone never verifies tag removal.

Before a tag grant, owner debt is durably recorded. Failed or unreadable tag
discovery also creates an obligation. Primitive local debt survives failed
journal writes long enough to retry persistence if a player disconnects. Failed
revision writes retain an invalidation that prevents a previously captured
callback revision from becoming valid after ordinary idle cleanup. Exhausted
revisions still cause native stop and remain unavailable for new actions.

Each local debt set and durable holder list is capped at 64 IDs. Encountering
additional unverified holders latches `holderOverflow` for that channel instead
of evicting an obligation. The latch is preserved by subsequent saves and
adopted after reload. It keeps the channel blocked even if all visible tags are
later externally cleared; the pilot provides no recovery operation for that
state. The other channel remains independently available. Other remembered
activity state contains primitive IDs/revisions for the two journal bindings,
without retained player/entity wrappers.

## Independently reproduced failures and repairs

The [before-fix results](independent-controller-before-fix.json) record six
failing rows in the earlier `bcb2bbba...` controller:

- Follow and Wait at the maximum safe revision skipped native cleanup.
- Failed idle preemption could later revive an old callback revision.
- An unreadable unexpected holder could disconnect without being journaled.
- A refused discovery-debt write could be forgotten after that holder left.
- A conflicting candidate could hide the still-loaded durable resident from
  native cleanup.

All six rows now pass. Source inspection also found the initially unbounded
local debt set; the final controller adds the cap and persistent overflow latch
described above. The current scope does not silently remove previous holder
history to recover capacity.

## Executed verification

Both commands exited **0** against the final source hash:

```sh
node --experimental-vm-modules screenshots/validation/GP19/independent-controller-probe.mjs
node --experimental-vm-modules scripts/tests/guild_activity.test.mjs
```

The [independent probe](independent-controller-probe.mjs) passes **13/13** cases,
with [raw output](independent-controller-probe.log) and
[source-hashed results](independent-controller-results.json). Besides the
repaired rows, it checks corrupt active witness handling, owner-debt writes
failing before or after mutation, a tag grant that mutates then throws while
the owner disconnects, uncertain removal, and corrupted active NPC markers.
The two owner-debt fault injections were moved to the earlier request-time
write after the implementation strengthened its protocol; they explicitly
assert that the injected failure executed.

The independently repeated permanent controller suite passes **16/16** groups
in [independent-controller-suite-direct.log](independent-controller-suite-direct.log).
Its test source SHA-256 is
`feeea149e375e56da50ed5b500747275d44a9ee9b36cd5875a2494eee0e005a2`.
That suite exercises the actual resident and training controllers and includes
overflow during failed writes, 80 unexpected holders disconnecting, persistence
recovery, externally cleared tags and restart. A separate `--test` invocation
also exited zero but summarized one file; the direct invocation above records
the individual sixteen groups.

## Limits

The independent probe records native event calls; it does not execute Bedrock
goals. The generated-event tests separately check shared-component deletion,
Wait restoration after redundant training cleanup, exact player filters and
defence precedence. Successful script calls and a one-tick stop barrier do not
prove native target-cache removal, pathfinding, physical Wait behavior, engine
event timing or save/reload behavior. Native acceptance remains **unrun**.

These writes span world, player and entity state. Local retry debt and
invalidations cannot make a failed durable write crash-atomic. Corrupt or
overflowed history may intentionally remain unavailable without a recovery
operation. The review establishes the exercised same-process failure and retry
behavior, rather than a transaction guarantee across every interruption.

# Guild deferred relationship authority — GP17

GP17 prevents an old proposal or spouse-menu response from changing a relationship
that no longer belongs to its requester. It also prevents two pending proposals
from charging two wedding rings and replacing the first accepted spouse owner.
This is a bounded repair to the existing romance callbacks in `main.js`.

## Reproduced behavior

The DP5 predecessor `732670a83bcd7909858ca4480c31f5dc8aeeb8ad` accepted both
Heroes' pending proposals: each lost one ring, each received the NPC in their
spouse list, both received the marriage reward, and the second response replaced
the owner. An old nested divorce cleared another Hero's current ownership.
An old spouse Follow response also interrupted the actual Guild training owner
and marked the resident as following after ownership had changed.

The [portable actual-source probe](../screenshots/validation/GP17/probe_relationship_authority.py)
records these [before](../screenshots/validation/GP17/relationship-probe-before.json)
and [after](../screenshots/validation/GP17/relationship-probe-after.json)
observations. It extracts production callbacks and the existing training module;
only Bedrock entities, forms, inventory and presentation boundaries are mocked.
The same final 24-group regression suite fails 19 groups against DP5 and passes
all 24 against GP17. The successful single-ring baseline remains successful.

## Current authority and deferred forms

Every actionable proposal, spouse menu and nested divorce reads a fresh strict
relationship snapshot when opening and again when its response resolves. The
requester must still be the same valid player, and the NPC must still be the same
valid entity, with their captured IDs and original dimension. Both must have
finite positions in that dimension and remain within six blocks. Six blocks and
the two-minute form lifetime are Minecraft interaction adaptations, not a claim
about TLC's original social UI.

`fc:married` must be exactly zero or one, and `fc:love_hate` must be readable and
finite within its authored range. An unmarried record can have only an absent or
empty `fc_spouse_player`; a married record requires a nonempty owner ID. Partial
or unreadable records defer without treating them as unmarried. Spouse actions
require the freshly read owner to equal the requester ID. Proposal acceptance and
`marryNpc` independently require current unmarried status, sufficient love and a
readable wedding ring before mutation.

The raw `fc_spouses` property is parsed strictly. Only an absent property means a
fresh empty list. Corrupt JSON, wrong types and non-string/empty entries defer.
Existing unrelated spouse IDs and their order remain intact; marriage avoids
adding a duplicate target ID, and an authorized divorce removes that target's
entries. Generic property helpers and unrelated saved history are unchanged.

Pending requests are keyed by the stable player/NPC ID pair, without assuming
that two native wrappers for the same entity are the same JavaScript object.
Only the latest form for that pair can act, and each response is consumed once.
A marriage or divorce attempt invalidates all pending forms for the NPC. An old
menu therefore stays invalid even after divorce and remarriage to the same Hero.
The registry stores only IDs and expiry tokens, is capped at 128 entries, and
expires authority after 2,400 ticks. Responses and rejected promises clear only
their own token; an old callback cannot remove a newer request. Evicted or expired
forms refuse their response. No entity objects are retained in the registry.

## Synchronous mutation and payment boundaries

All required reads and writes occur synchronously in the accepted callback.
Marriage reserves `fc_spouse_player` first, then writes married state, the
requester's preserved spouse list and love. Only after those required setters
return does it consume one ring from the captured inventory slot. Required
setter failures suppress rewards, Follow, names and wedding presentation.

The generated wedding ring has `minecraft:max_stack_size: 1`. The debit clones
the original `ItemStack`, removes the single item, and verifies that exact slot.
A legacy multi-item ring stack retains its cloned metadata on the remainder.
The check compares type and amount in that slot; it does not claim opaque item
identity or distinguish an identical replacement. It never scans other slots to
restore payment and never grants or drops a refund. `isStackableWith` cannot
serve as ring equality because the pinned API always returns false for a
nonstackable item.

A failed required write triggers bounded reverse restoration of only attempted
values still belonging to the action. Entity `setProperty` changes are applied
next tick in the pinned API. An old same-tick read therefore cannot prove that a
write had no effect: restoration explicitly queues each attempted married/love
before-value again. If a read or restoration fails, or an unrelated value is
observed, restoration stops. Keeping the earlier owner reservation prevents a
later proposal from stealing unresolved history.

If payment fails while the captured slot still contains the original ring type
and amount, relationship restoration can proceed. If payment may already have
been consumed, or its readback is unavailable, ownership and bookkeeping stay
reserved and success extras are suppressed. That preserves duplicate-payment
protection at the cost of leaving an uncertain outcome for later inspection.
This is not a transaction spanning inventory and entity/player properties; it
does not promise crash atomicity, automatic recovery, rollback through arbitrary
engine failures, or a durable payment receipt. No migration or background repair
is added for partial records.

Divorce performs its own fresh authority check after confirmation, writes the
married/list/love changes and clears ownership last. A failed required write
attempts bounded restoration and suppresses the penalty and neutral reaction.
Successful normal actions still use existing morality, presentation and Guild
training interruption owners. Cosmetic failures after successful marriage do
not reopen the relationship or permit another ring debit.

The compatibility reference is Microsoft's exact published
[`@minecraft/server` 2.1.0 package](https://registry.npmjs.org/@minecraft/server/2.1.0),
with pinned declaration and generated ring hashes in
[API provenance](../screenshots/validation/GP17/api-provenance.json).
The current [Entity documentation](https://learn.microsoft.com/en-us/minecraft/creator/scriptapi/minecraft/server/entity?view=minecraft-bedrock-stable)
corroborates property timing and persistent IDs; current APIs beyond the pinned
package are not assumed.

## Verification and open work

`node --experimental-vm-modules scripts/tests/guild_relationships.test.mjs`
passes 24 groups, covering changed ownership, duplicate/stale/nested responses,
different wrappers sharing IDs, invalid or lost handles, movement and dimension
changes, diminished opinion, missing rings, malformed/unavailable reads, required
write failures before and after mutation, next-tick property visibility, bounded
form cleanup, uncertain payment, preserved history and successful normal actions.
The tests invoke the actual training owner for accepted marriage/Follow/Wait and
stale Follow refusal. The existing training suite also passes all 33 groups.
The new relationship gate is wired into `scripts/validate.py`.

[Focused commands and logs](../screenshots/validation/GP17/focused-commands.json)
and [reproduction instructions](../screenshots/validation/GP17/relationship-evidence.md)
retain the baseline and resulting evidence. These are automated source/fixture
checks. Native Bedrock form ordering, component restoration, inventory behavior,
multiplayer interaction and save/reload acceptance remain **unrun**.

Requester-specific native Follow/Wait ownership remains open: this milestone
only guards authority at existing deferred spouse callbacks. General emote
broadcasts, native following channels, permanent taming, behavior generation and
purposeful Skill arrival are unchanged. The
[activity follow-up audit](../screenshots/validation/DP5/activity-followup-audit.md)
records the separately scoped controller/navigation work and pinned API limits.

# DP6 independent ticket-read review

Disposition: **no blocking finding** in the reviewed DP6 source/test changes.
The initial review read the unstaged door hunks while HEAD was GP18. GP19 commit
`6f490a7263226ce50e3ad72769ceaa3ad3fa2d24` is now the integration baseline; its
committed door owner matches the saved predecessor used by the independent
comparison. Guild activity behavior is outside this door review. No
production/test edits or staging were performed by the reviewer.

`readTicket` now distinguishes a failed API read from readable absent/invalid
data. The periodic player loop skips an unavailable ticket before changing its
phase, synthesizing a fallback, recording an approach or attempting travel.
The public return method reads afresh and its private helper rejects an
unavailable result before any return-side work. A confirmed absent/corrupt
ticket can still use the current validated ledger's existing orphan recovery.

The private helper receives the periodic loop's single validated ticket
snapshot. There is no asynchronous gap in that call chain and no new public
method for supplying a cached return snapshot. The diagnostic/deferred-click
entry point remains `requestReturn(player)` and performs a fresh read when
called; DP5's deferred original-cell check is unchanged. Existing public
one-argument `getReturnTicket(player)` retains its nullable read-only result.

The occupied-ticket guard still checks the ticket's exact bounded Overworld
cell and the visitor's actual location. Read failures remain isolated to the
affected visitor. Current-allocation protection and other visitors' committed
occupied-cell protections continue to be combined. An unavailable ticket is
not used to invent protection for an otherwise unknown old room, nor can its
failure remove another visitor's independently established protection.

Valid saved sources and dimensions are retained throughout recovery. Returning
from an old cell after ledger loss/replacement still uses that ticket's exact
source without borrowing alternatives from the new ledger. The change adds no
world schema, reward reset, placement, resident/history migration or new return
authority.

The reviewer independently ran:

```sh
node --experimental-vm-modules scripts/tests/demon_door_integration.test.mjs
```

All **38 adapter groups pass** in [independent-adapter.log](independent-adapter.log).
The five added groups cover all four committed phases, diagnostic and deferred
arch returns with faults before/after the click, confirmed absent/corrupt
controls, another visitor's protection/return across five primary-ledger
conditions, and a periodic return whose hypothetical second ticket read would
fail. The exact saved return remains reachable when every default candidate is
blocked. Existing DP5 protection and original-cell cases pass unchanged.
`git diff --check` also passed for the two reviewed files.

The additional [write-fault probe](independent-write-fault-probe.mjs) loads the
actual preceding and current door owners into the same production adapter
fixture. Across **eight owner/scenario runs**, failures before/after writing
the `returning` phase and before/after clearing the ticket produce identical
observations. A refused `returning` write causes no travel; a later readable,
writable retry returns to the exact saved point despite blocked defaults. A
failure while clearing after successful travel does not cause another travel
on retry from outside the room. The source survives whenever backing ticket
data remains, with no world-history changes, payouts or placements. See
[results](independent-write-fault-results.json) and
[raw output](independent-write-fault.log). These checks preserve the existing
write-failure semantics; they do not claim atomic teleport-plus-ticket writes.

| Source actually reviewed/executed | SHA-256 |
| --- | --- |
| `packs/Fablecraft_BP/scripts/fc_demon_doors.js` | `843d0ce71425bd8969fff29a88504210358e5977ddf1f62a518f0a6a886c33d0` |
| `scripts/tests/demon_door_integration.test.mjs` | `78a4b2fdd2983b43e0c3b2a1e49ea36999839b130a48b9adeb8a31107aa5ade9` |
| `packs/Fablecraft_BP/scripts/main.js` callbacks loaded by the adapter | `2d158bedac0198480e359f10d93ea67710ab1a777a9e16117479ddbf11d32c8d` |

These tests inject a transient read failure at the actual module/callback API
boundaries. They do not establish that the fault has occurred in a native
world, or prove engine collision, loading, persistence and save/crash behavior.
Native Bedrock acceptance remains **unrun**. This review does not replace the
final combined-snapshot validation after integration with the frozen Guild
activity work.

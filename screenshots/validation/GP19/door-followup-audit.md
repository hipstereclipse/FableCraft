# GP19 independent Demon Door follow-up audit

Read-only follow-up, 2026-09-12. Audited HEAD was GP18
`c83246751b86aa489897efa3d0cadd49f303c588`, with concurrent GP19 working edits.
The already-pushed DP5 protection repair is retained. This audit changes only
this report and its text/code observation artifacts. Native Bedrock execution
remains **unrun**.

## Highest concrete defect: unreadable player ticket loses its saved return anchor

A transient failure to read an existing player return ticket is treated as an
absent/invalid ticket. With a readable current room ledger, orphan recovery then
writes a default source approach over the still-persisted valid exact approach.
The next return uses the default point. If that default corridor is obstructed,
the player can remain stranded even after ticket reads recover, because the
previous safe anchor has already been destroyed.

The source cause is the `rawTicket` catch returning `null`, introduced by DP5's
per-player fault isolation. `tick` and `requestReturn` also interpret that same
`null` as permission to synthesize an orphan ticket from the primary record.
Those meanings need to be distinct. DP5's guarded per-player scans are still
necessary; removing that isolation would restore the prior protection defect.
The new GP19 Skill activity work does not change this door path.

## Reproduction with actual production callbacks

Run from repository root:

```sh
node --experimental-vm-modules screenshots/validation/GP19/door-followup-audit.mjs
```

The portable probe includes the existing adapter fixture prefix, which loads
actual `fc_demon_doors.js`, aperture/data modules and AST-extracted `main.js`
portal tick, diagnostic return and deferred arch-click callbacks. It performs
in-memory mock operations only. The added cases inject a temporary exception
from the player's `getDynamicProperty(fc_dp_return_v1)` while leaving the saved
backing string and write API available. The readable backing ticket has source
`(102.1,65,195.5)`; the primary door is `(100,65,200)`, whose fallback approach is
`(100.5,65,196.5)`. Both approaches initially have checked floor/headroom.

For the blocked-default pair, stone at x97..104, y65, z196 blocks every default
return candidate while leaving the recorded exact approach clear. The intact
control demonstrates a successful exact return under those same blocks. This
is not a hypothetical inaccessible original source.

| Case | Observation |
| --- | --- |
| Readable ticket | Periodic reconciliation preserves the original source; command returns exactly there. |
| Readable ticket, default corridor blocked | Exact return still succeeds. |
| Ticket read throws during periodic reconciliation | Two failed reads cause the saved source to be overwritten with the default; after reads recover, command uses that default. |
| Same read fault, default corridor blocked | The safe source is overwritten; two subsequent return requests make zero teleport attempts even with reads restored. |
| Ticket read throws during diagnostic return | Recovery writes/uses the default and clears the original ticket after successful travel. |
| Ticket read throws during deferred arch click | The actual DP5 click adapter invokes the same default return while the existing ticket is unreadable. |
| Ticket absent | Existing intended primary-ledger fallback succeeds. |
| Ticket corrupt JSON | Existing intended primary-ledger fallback succeeds. |
| Both world and player ticket reads unavailable | The periodic path preserves backing ticket bytes and performs no travel. |

All nine observation cases exit 0 by asserting the observed behavior, including
the defect; this is **not** a repaired regression suite. Every case retains the
world progress string and places zero structures. The result JSON records exact
positions, read-failure counts and source hashes. `ticket_backing_history_preserved`
measures the final backing string: it is also false after an ordinary successful
return because successful travel intentionally clears the ticket. The meaningful
fault evidence is the intermediate source replacement and blocked-return control.

Existing suites also ran unchanged: **33 actual adapter groups and 13 generated-room
runtime groups pass**. Their existing player-read failure coverage verifies that
one visitor cannot remove another's protections; it does not cover retaining that
unreadable visitor's valid exact-source ticket during orphan recovery.

## Recommended next bounded door pass

Represent an unavailable player-ticket read separately from confirmed absence
or invalid data. Affected reconciliation/return work must defer before any ticket
write, ticket clear or teleport; a later readable retry should preserve and use
the original exact source. Keep the intentional absent/corrupt-ticket fallback,
DP3 original-cell return, DP5 live-occupancy protections, per-player error isolation,
shared once-only rewards and all structure/history safeguards unchanged.

Regression expectations: the periodic, diagnostic and deferred-click paths retain
unreadable ticket bytes; read recovery returns through the still-clear exact
approach when defaults are blocked; missing/corrupt-ticket controls still recover;
a failed ticket reader does not prevent another visitor's protections or return.
No room regeneration, reward reauthorization, new persistence schema or broader
scatter conversion is required to address this finding.

## Limits and continued destination work

The read/write fault split is an injected API failure case, not a claim that this
particular fault has been observed in a native world. Actual save/crash durability,
loading, player collision, collection and two-Hero engine behavior remain unrun.
This audit did not reproduce another new reward duplication or admission defect.
It does not claim the rest of the pilot is complete.

Following this bounded history repair, the designed-world queue still requires a
stable canonical identity/challenge/dialogue/reward mapping for the next supported
ordinary door, reference-backed individual destination geometry and atmosphere,
shared-world collection and exact-source reusable return. Existing coordinate
personas and immediate payouts do not fulfill that request; story exceptions such
as Nostro remain distinct. Broader Library player-height reference/fidelity work
also stays open.

## SHA-256 provenance

Hashes below identify bytes actually loaded by the observation probe. The full
main hash includes concurrent GP19 edits outside these door callbacks.

| Loaded source | SHA-256 |
| --- | --- |
| `packs/Fablecraft_BP/scripts/main.js` | `2d158bedac0198480e359f10d93ea67710ab1a777a9e16117479ddbf11d32c8d` |
| `packs/Fablecraft_BP/scripts/fc_demon_doors.js` | `aee84404ebb7f8b5ebc63b7b584de2e1c08918e67094dc2d9e762044e6035b62` |
| `packs/Fablecraft_BP/scripts/guild_door_aperture.js` | `5db5993efaebf1787125cd2552379f1a9220d5e485fa7edd9c4b52603681fbb5` |
| `packs/Fablecraft_BP/scripts/fc_gamedata.js` | `b649dacfc8960dcbff44534b8b553ccaecfb327aa28ce1096814393d259941eb` |

| Evidence | SHA-256 |
| --- | --- |
| `screenshots/validation/GP19/door-followup-audit.mjs` | `9e8d25cdfcfe4432d19a76f797e79c56854a8dbdd4665179dc278550e306ea7a` |
| `screenshots/validation/GP19/door-followup-audit.json` | `d478b97f3ee834e0eafb862b226ada42dbb527e7b61c0f910e1fe7964757d6cd` |
| `tmp/conformance/gp19-review/door-existing-adapter.log` | `bab50b67b02175bf2e876bc6527990eabbd4047709b896bfd916bef15850b695` |
| `tmp/conformance/gp19-review/door-existing-runtime.log` | `52a8f01d2664705464e2399f4e25a6807b09ba7b910b0d5cc15218febbb07590` |

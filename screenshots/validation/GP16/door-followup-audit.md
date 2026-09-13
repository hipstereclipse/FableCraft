# GP16 — independent Demon Door follow-up audit

Date: 2026-09-12. Read-only production review; no implementation or staging by
this audit. Baseline HEAD at the probe was
`17d1191e73d830ad4c809d2f6af62b724465eede` (GP15). GP16's separate Skill work does
not repair this door finding. All native Bedrock acceptance remains **unrun**.

## Highest concrete remaining defect found: occupied recovery rooms lose protections

A visitor's valid committed ticket still permits exact-source return after the
primary world ledger becomes missing, corrupt, unreadable or replaced. However,
`protectsBlock` and `excludesWorldPosition` only consult that primary ledger.
An old room with a valid ticketed occupant consequently loses block-break,
block-interaction, explosion and ordinary-world generation guards during the
same recovery cases that DP3 explicitly supports.

This is an observed source inconsistency, distinct from the documented unknown
native placement/fluid/fire behavior. `occupiedTicket` and `occupiedRealm` already
recognize the old occupied cell. Item-use protection therefore continues cancelling
an ender pearl while the other guards permit mutation of that same room. The
actual quest-boss callback requests `fc:wasp_queen` inside its bounds when its
normal probability branch is selected. A second player at the Guild can reproduce
the `room:null` replacement case through the actual periodic maintenance callback;
the probe does not need to synthesize that replacement record.

Relevant owners: `fc_demon_doors.js` functions `occupiedTicket`, `occupiedRealm`,
`protectsBlock`, `excludesWorldPosition`; `main.js` function
`guildDoorWorldExcluded`, before-break/block-interaction/explosion callbacks,
and the scatter and quest-boss intervals. Line numbers can shift during GP16;
function names and source hashes below identify the inspected code.

## Actual-module probe and results

Ignored working directory: `tmp/conformance/gp16-door-audit/`. `probe.mjs` copies
the existing adapter test fixture prefix up to its first `test(...)`, then runs
additional assertions. That fixture parses and executes production declarations,
actual main callbacks and the owned pilot/aperture/data modules; no alternate
implementation of protection or return logic is substituted.

Each case starts with the existing test fixture's ready, visited cell 0 and an
Overworld visitor carrying a valid cell-0 ticket with source
`(100.5,65,196.5)` in the Overworld. The interacted/impacted block is a cobblestone
floor at local `(24,2,10)`. The visitor remains at local arrival `(24.5,3,7.5)`.
The same operations run before checked return, and the probe asserts that return
succeeds without changing the primary ledger or placing a structure.

| Primary state | Break cancelled | Building interaction cancelled | Explosion blocks retained | World excluded | Scatter calls | Boss requests | Return succeeds |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Intact ready cell 0 | yes | yes | 0 | yes | 0 | 0 | yes |
| Missing | no | no | 1 | no | 9 | 1 | yes |
| Corrupt JSON | no | no | 1 | no | 9 | 1 | yes |
| Read throws | no | no | 1 | no | 9 | 1 | yes |
| Recreated `room:null` | no | no | 1 | no | 18 | 1 | yes |
| Replacement ready cell 8 | no | no | 1 | no | 9 | 1 | yes |

`occupiedRealm` and ender-pearl cancellation remain true in all six cases.
The recreated case has 18 scatter dispatches because it includes the second
player at the Guild: nine are for the room occupant, nine for that source player.
Cell 8 is deliberately far enough that the replacement room's 160-block exclusion
margin does not accidentally overlap cell 0.

The quest probe uses the actual generated quest list, selects the first kill
objective mapped by the production boss interval, supplies unfinished progress,
and sets the mocked random result to zero to exercise the normal spawn branch.
The spawn boundary records one `fc:wasp_queen` request in each failure case.
The scatter callback's `maybePlace` boundary records dispatch; this audit does
**not** claim an actual structure was generated or that an explosion destroyed a
block in Bedrock. The result is loss of script authorization guards, with the
concrete downstream spawn request proven at its injected boundary.

Commands run from repository root (all exited 0 after the probe fixture was
corrected to supply its quest-progress array):

```sh
node --experimental-vm-modules tmp/conformance/gp16-door-audit/probe.mjs
node --experimental-vm-modules scripts/tests/demon_door_integration.test.mjs
python scripts/tests/test_demon_doors.py
node --experimental-vm-modules scripts/tests/guild_door_aperture.test.mjs
```

Existing regression results: **25 adapter groups, 13 actual generated-room runtime
groups and 4 aperture groups pass**. The added probe passes by asserting the
observed defect against intact controls; it does not assert repaired behavior.
The first probe attempt exited 1 because its mock active quest lacked `progress`;
adding the ordinary zero-filled progress array fixed that harness omission before
the results above were collected. No production change was made for the probe.

## Next bounded door owner pass

Preserve block and world-generation protections for each currently occupied,
valid committed ticket cell alongside any current ledger cell. Keep dimension,
cell bounds and physical occupancy checks; an invalid ticket, stale ticket outside
its cell, unrelated coordinates or another dimension must not authorize a new
protected area. Multiple visitors and simultaneous current/old cells need explicit
coverage. Retain exact-source recovery, native ordinary container access and the
existing no-rebuild/no-reseed behavior without reconstructing missing history.
Check the return-arch click adapter as part of the same source-owner change: it
currently also locates its arch only through the primary record. Normal exit dwell
and the diagnostic return already work and must remain covered.

This is the highest concrete new controller/adapter defect found in this bounded
review. It warrants a separate DP milestone after GP16's Skill lane change.
No fixes to ordinary scattered doors or additional room catalogue are included.
After this recovery inconsistency, the next designed-world requirement remains
stable canonical identity/challenge/reward mapping and a distinct reference-led
destination for the next supported door; the eight immediate-payout scatter
personas do not fulfill that requirement. Story exceptions, including Nostro's
onward passage, must retain their own semantics.

## Review scope and limits

Read the active priority ledger, Demon Door design, Library pilot and recovery/
source-authority notes; reviewed the production pilot and main adapter protection,
maintenance, travel, allocation, seeding and claim paths plus their current tests.
The runtime regression uses actual generated Library geometry. This audit did not
run an engine, add visual reference evidence, test arbitrary add-ons/commands or
prove crash durability. No additional admission, return, reward-duplication or
persistence blocker was reproduced within this scope. That bounded result does
not close the documented full-room fidelity, multi-door design or native gaps.

## Source and evidence SHA-256

Byte hashes identify the source when probed. The full `main.js` hash may differ
from the final GP16 commit because its independent Skill callback is being edited;
the relevant door/boss protection scope hash provides a separate comparison.

| Source path | SHA-256 |
| --- | --- |
| `packs/Fablecraft_BP/scripts/fc_demon_doors.js` | `288d6c601b1b1b9d3e574eb7a9eb5ee093825141b4acbe6fc52b55abf62d1dfd` |
| `packs/Fablecraft_BP/scripts/main.js` | `c712c39be4aee51bc65e15248e1bd1e27f3cf7a667f7ccae3be53db430521b20` |
| `scripts/tests/demon_door_integration.test.mjs` | `356c8c0b186cf3b662ae10c029bc8be5bee10683518c2fadf668e7cde14700c7` |
| `scripts/tests/demon_doors.test.mjs` | `b267d84a1ce3b396f821ea28836bc115af49eb3fe720c3659fe4bd7872185f84` |
| `scripts/tests/test_demon_doors.py` | `f15f622e886988d87706f5bf5aaeabfb9a298a1955ceab054c4a362c436b6058` |
| `scripts/door_realms.py` | `2f6e52b2166935f2c2f48da2de6723930746d84294d9fd0116beaeee8d31bf69` |
| `packs/Fablecraft_BP/scripts/guild_door_aperture.js` | `5db5993efaebf1787125cd2552379f1a9220d5e485fa7edd9c4b52603681fbb5` |
| `packs/Fablecraft_BP/scripts/fc_gamedata.js` | `b649dacfc8960dcbff44534b8b553ccaecfb327aa28ce1096814393d259941eb` |

Relevant parsed main scope SHA-256: `693751a870555185d289137cc42b7de6b171166b703c8d91f34356f987bc26e4`.
The scope concatenates `guildDoorPilot` and `guildDoorWorldExcluded` declarations,
then top-level callback statements containing `guildDoorPilot.protectsBlock`,
`guildDoorPilot.occupiedRealm` or `Your quarry has found YOU.` in source order.

| Ignored local evidence | SHA-256 |
| --- | --- |
| `probe.mjs` | `eb2021d8fd8914c5a886f7820037333b72f5c03cc9d78f68726079e0a6b033d9` |
| `probe-results.json` | `a38efefb59f299aae60b1b90d958670e4f77bcd5ed2c348d26a05c36e891f21d` |
| `existing-adapter-tests.log` | `82dbc71b33835cd11a434e01c5bf23db2cfd32ace6d2e57ced0ae81fbabb2a74` |
| `existing-runtime-tests.log` | `52a8f01d2664705464e2399f4e25a6807b09ba7b910b0d5cc15218febbb07590` |
| `existing-aperture-tests.log` | `07e92a43b20aed557868142568ddf57de466b177cad9db8abb785b892d9591ee` |

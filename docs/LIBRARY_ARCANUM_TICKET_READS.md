# Library Arcanum unavailable ticket reads — DP6

A temporary failure to read a player's saved return ticket must preserve the
ticket. Previously, that failure looked like missing data, allowing orphan
recovery to replace a valid exact return point with a default Guild approach.
When all default positions were obstructed, that replacement destroyed a usable
way home. The GP19 actual-callback audit reproduces this case.

The ticket reader now reports availability separately from its validated value.
An unavailable read defers the affected player's periodic reconciliation or
return before a ticket write, clear or teleport. A later readable retry uses the
original source. Confirmed missing, corrupt or invalid tickets retain the existing
primary-ledger recovery. One fresh ticket snapshot serves each synchronous
operation; no ticket is cached across ticks. Public and deferred-click returns
still read fresh authority when invoked.

The existing read-only protection scans continue to isolate an unreadable player
from other visitors. The current allocation and other readable, physically
occupied original-ticket cells stay protected. This change does not reconstruct
world history, seed rewards, alter shared claims, place structures or change
portal geometry. DP3 original-cell recovery and DP5 guards remain intact. Only
the handwritten door controller and its actual-adapter regression suite change.

Five new test groups cover all four committed phases, repeated read failures,
periodic and diagnostic returns, both deferred arch click heights, confirmed
absent/corrupt recovery, old cells across lost/replaced ledgers, a healthy visitor
alongside a failed reader, and a single ticket read per periodic operation.
The exact saved point stays clear while every default candidate is blocked.
The final 38-group suite fails three new regressions against the previous owner
and passes against DP6. Thirteen room/runtime and four aperture groups also pass.
Independent review repeats all 38 adapter groups and compares eight old/new
failed-write cases without finding changed payment, placement or return behavior.

All 51 base gates and 64 ESM syntax checks pass in the isolated reviewed-index
snapshot, with fresh 35-asset C2 and Guild diagnostics. All 35 structure assets,
35 C2 images and six rendering/data/geometry owners match GP18; its full-render
evidence is retained from unchanged inputs, not rerun. See
`screenshots/validation/DP6/` for commands, raw failure/success logs and hashes. This is an injected
API failure test, not a claim about how often Bedrock encounters such failures.
Native travel, collision, loading, collection, multiplayer and save/crash
acceptance remain unrun. DP6 does not complete the reward-world catalogue or
whole-facility conformance.

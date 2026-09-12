# Guild door source authority

DP4, 2026-09-12. The durable `fc_dp_guild_v1.source` now owns Guild face
lookup, replacement and periodic maintenance. The older `fc_guild_door` property
is used for initial registration only when no progress ledger exists. This is
an adapter repair, not a reanchor or geometry migration.

## Reproduced defects and repair

Actual production-adapter tests showed that four repeated maintenance calls
against disagreeing anchors created four unkeyed faces. Face matching trusted
the durable source while lookup/spawn trusted the old hint. A missing/broken
hint also stopped periodic repair despite valid progress. The all-door sweep
could create an ordinary door at a stale Guild hint, and interaction could
present that door's unrelated challenge and payout.

The runtime controller's `getSource()` now resolves a validated authoritative
source for all maintenance callers. A present corrupt, malformed or unreadable
ledger denies fallback placement. Before first registration, a validated explicit
founding anchor or old hint is accepted; a failed scan still preserves the
existing new-world enrollment ordering. Source dimensions are retained and
wrong-dimension maintenance does nothing. Unavailable scans defer replacement.

The old hint remains stored unchanged and is recognized only as a quarantine
alias for ordinary-door dispatch. It cannot authorize a new face, challenge,
reward, room, source relocation or duplicate cleanup. Existing faces at a distant
stale hint are left in place because their ownership is uncertain; interacting
with one reports that saved progress is preserved. The original-source mouth
alone supplies candidate faces for the established survivor/duplicate handling.
Ordinary scatter away from both Guild positions keeps its prior behavior.

Payment history, unlocks, claimed/seeded rewards, visited rooms and player return
tickets are unchanged. The pilot challenge, realm version, generated assets,
source throat, surrounding altar steps and Guild/NPC anchors are unchanged.
A valid original-cell ticket retains DP3 recovery even when primary history is
unavailable. If both durable source and old hint are lost, an unmarked displaced
face cannot be reliably identified; no universal reconstruction is claimed.

## Evidence and acceptance

`screenshots/validation/DP4/adapter-red.log` records four failing new groups
against DP3 (20 other groups passed). The expanded final suite has 25 groups,
covering conflicting/missing/broken/throwing hints, invalid primary history,
durable source dimension disagreement, unavailable scans, quarantine, ordinary
scatter and unchanged world progress. These execute actual main adapters and
the controller with mocked native boundaries; they are not engine tests.

No visual owner changes in DP4: full GP6 renders and GP5 Guild diagnostics are
reused only with matching dependency hashes. Full base results, additional
syntax evidence and snapshot provenance are retained in the evidence directory.

Manual Bedrock acceptance remains unrun:

- [ ] Save/reload with conflicting anchors; verify a single face at the durable
  source and unchanged paid history, contents and exact-source returns.
- [ ] Unload source chunks, replace a face, and return with two Heroes.
- [ ] Verify stale-hint interaction cannot award an ordinary door reward.
- [ ] Inspect native opening collision, particles, room lighting and loading.

Next adjacent defect: obsolete Guild approach/scarecrow repair sweeps can erase
player construction when historical flags are absent. Retire them in a separate
GP7 milestone; current final geometry already owns their usable clearances.

DP4 validation: all 39 base gates pass from the isolated reviewed-index snapshot,
plus 25 adapter groups and ESM syntax for all 62 BP scripts. Lint, spells, Guild
lifecycle/NPC gates and C2 are green. GP6 full renders and GP5 Guild diagnostics
are reused with matched dependency hashes; no visual owner changed. Independent
source-authority review found no blocking defect. Live engine tests remain unrun.

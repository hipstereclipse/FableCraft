# DP7 API, alignment authority and adapter review

Reviewed 2026-09-13. This evidence executes actual JavaScript owners and actual
geometry builders with injected engine boundaries. Native Bedrock delivery,
inventory debit, chunk loading, command behavior and performance remain unrun.

## Completed food use

The pinned Microsoft `@minecraft/server` **2.1.0** declaration file has SHA-256
`38e989f3f0371967c1df82a12d5f37a3832cbff3944e38be8bb51638ed0e771d`.
Its provenance and compact signatures are in [pinned-api-contract.json](pinned-api-contract.json),
with [official package metadata](https://registry.npmjs.org/@minecraft/server/2.1.0).
`ItemCompleteUseAfterEvent` exposes `itemStack`, `source: Player` and
`useDuration`; no use ID, slot, consumed count or original timestamp is exposed.
The current [primary event reference](https://learn.microsoft.com/en-us/minecraft/creator/scriptapi/minecraft/server/itemcompleteuseafterevent?view=minecraft-bedrock-stable)
agrees. `useDuration` describes remaining charge duration, not event identity.

The existing Crunchy Chick is native food with stack limit 16, eating duration
1.2 seconds and existing morality effect -15. DP7 counts one qualifying completed
dispatch, regardless of stack amount. It does not remove another item or collect
payment when opening. `Player.getGameMode()` returns the pinned capitalized
`GameMode` values; only readable Survival/Adventure qualifies. Creative is
excluded because its inventory does not deplete. These are script qualification
checks; the event itself does not expose a debit receipt.

Food progress and full-evil alignment are independent paths. A valid witnessed
food completion may count when alignment is unavailable. Unavailable alignment
only refuses the full-evil shortcut. The actual callback invokes the new witness
before the old morality effect can normalize state. Ten qualifying chicks may
still unlock independently; a single unavailable-state event cannot use that
dispatch's later normalization to unlock early.

The callback WeakSet suppresses reuse of one event object; the controller also
suppresses same-Hero/same-tick repeats before assigning one instance. Stable Hero
IDs keep separate counters. Two simultaneously qualifying instances refuse
ambiguity. No native unique use token exists, so delayed indistinguishable replay,
restart and crashes between native use and journal persistence cannot be called
exactly-once physical consumption. Generic preexisting consumable effects are
outside DP7 replay suppression: the baseline replay probe invokes the original
callback twice and observes alignment 0 → -15 → -30. This is injected replay,
not a claim that native Bedrock duplicated an event.

## Read-only alignment owner

`wd/alignment.js:readAlignmentAuthority` requires the same live Player, a
nonempty ID, raw nonempty `wd:state`, a non-array schema-3 object, and an integer
alignment in [-1000,1000]. It returns the value or null without mutation,
normalization, migration or legacy fallback. Full evil is exactly -1000; -950
appearance tier and the legacy -500 persona threshold are not this threshold.
Unrelated saved state fields remain unchanged.

[authority-baseline-probe.mjs](authority-baseline-probe.mjs) reads the exact GP20
commit `71d70ed9f8ab21f49221a2c040f283c398f3f0ec` using `git show`, executes its
actual state/alignment owner and original consumable callback, then compares
the actual current DP7 helper. Eight invalid histories normalize/fall back to
-1000 in the baseline owner but return null from DP7 without writes; valid
-1000 and -999 remain distinct. [Results](authority-baseline-results.json) include
both source hashes. The original preimplementation observation is preserved as
[original results](authority-original-results.json) and its raw log; no entire
baseline main file is copied into this milestone.

## Fresh volume authority

Pinned 2.1.0 has `Dimension.containsBlock(BlockVolumeBase, BlockFilter,
allowUnloadedChunks?)`, `new BlockVolume(from, to)` and `excludeTypes?: string[]`.
The current [Dimension reference](https://learn.microsoft.com/en-us/minecraft/creator/scriptapi/minecraft/server/dimension?view=minecraft-bedrock-stable#containsblock),
[BlockVolume reference](https://learn.microsoft.com/en-us/minecraft/creator/scriptapi/minecraft/server/blockvolume?view=minecraft-bedrock-stable)
and [BlockFilter reference](https://learn.microsoft.com/en-us/minecraft/creator/scriptapi/minecraft/server/blockfilter?view=minecraft-bedrock-stable)
support this contract. The volume ends at `origin + size - 1`; the adapter asks
whether any block differs from the required air or barrier type. Only exact
`false` authorizes. `allowUnloadedChunks` is explicitly false: true can search
only the loaded subset. Exceptions defer.

The final air query closes the stale time-sliced air-scan interval before
placement. Six thin barrier queries close the stale shell-scan interval before
readiness/entry. These script checks do not establish native transactional
atomicity or benchmark the far-cell bulk query. The actual integration fixture
uses the generated Gorge and Arboretum voxel material at every queried cell,
including a late obstruction, unavailable query and late shell hole.

## Adapter review and reproduction

The main adapter reserves a fresh source before native placement; only a receipt
written after successful placement permits later confirmation. Actual
`ensureArboretumFaces` retries placed receipts near a Hero; controller `tick`
does not adopt unknown pending structures. A thrown/ambiguous placement remains
reserved even if matching mouth geometry happens to exist. Old region markers
and missing new markers never cause replay or old-Gorge enrollment.

The actual final Gorge floor at local x31..33, y5, z6..12 is grass, and its
throat x31..33, y6..9, z6..12 is air. Main checks the subset through z11.
Canonical face dispatch preserves instance identity and does not issue legacy
persona payouts after marker loss or unreadable state. Shared guards cover both
families; an unreadable other-family ticket blocks new entry while a healthy
own ticket can still return to its exact source.

Run from repository root:

```sh
node --experimental-vm-modules screenshots/validation/DP7/authority-baseline-probe.mjs
node --experimental-vm-modules scripts/tests/alignment_authority.test.mjs
node --experimental-vm-modules scripts/tests/arboretum_integration.test.mjs
```

The final focused gates contain 6 alignment groups and 16 integration groups.
Logs and source hashes are recorded separately. The integration uses actual
main AST adapters, both actual door controllers, the actual alignment/state
owners and generated final geometry; only engine boundaries are injected.
See [integration-development-notes.md](integration-development-notes.md) for
historical red logs and their fixture corrections; those are excluded from the
final passing counts.

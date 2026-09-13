# Next canonical Door implementation: Greatwood Caves and The Butterfly House

Status: bounded implementation plan, **no production implementation**. Baseline
GP23 is `4aed7cff4bdb6cecc706e2c4711067cab648d530`. Main remains SHA256
`c18b286d79bc16d6b3ea08985d5882f7a2411ae2aeb61de3bd83594d6ffb103e`.
The original audit workspace is ignored scratch; this checkpoint retains its
textual plan/probes with provenance. No source/room/item asset or saved state
was authored, no network request was made, and no native engine ran.

## Recommendation and readiness

Build one separate canonical family:
**Greatwood Caves → The Butterfly House → one physical Cutlass Bluetane**.
Use a new registered source and new destination; opening grants neither immediate
inventory items nor XP. Keep all eight indexed legacy personas, the Warrior/
Harbinger contract, old unregistered doors, `fc:hobbe_cave`, Guild/Arboretum saves
and Nostro's story passage intact.

DP10 now supplies a suitable preparation protocol: immutable source placement
receipts, pinned room authority, placement/seed intents and completion receipts,
fresh native validation, and independent exact-source return tickets. It does
**not** supply a generic configurable runtime. `createArboretumDoors` is coupled
to its lexical ID, source offset, cell grid, structure dimensions, chest, route,
return detectors, keys and identity regex. Merely supplying a new definition is
rejected; reusing its keys would attach the new world to existing history.

For the first third-family milestone, reuse the audited **protocol and test
matrix** in a separate `butterfly_house_doors.js` owner. Keep the two current
controllers unchanged except their injected mutual-admission callbacks. Do not
combine introduction of the third world with a generic rewrite of both existing
families. The duplication has a maintenance cost, but its bounded first-pass
review avoids changing old persistence and return behavior at the same time.
An eventual shared engine requires a separate three-family equivalence review.

The architecture is implementable offline. Missing full original dimensions and
native acceptance constrain fidelity claims; they do not require a routine user
confirmation to continue an explicitly labelled Minecraft adaptation. The
remaining choices below must be made and tested before enabling source spawning.

## What the retained original evidence establishes

The 2005 TLC guide's PDF pages 47 and 174 establish source, destination and reward
pairing, with an active combat multiplier of at least 14 at conversation time.
The original text distinguishes **Hobbe Cave Entrance** from **Greatwood Caves**.
Reusing/renaming the existing `fc:hobbe_cave` would therefore conflate locations.

This reviewer inspected the retained full page-174 PNG. The source picture shows
a pointed pale stone frame around the face, vegetation and a warm light beside
it. The interior picture is extremely dark and largely obscured by the Hero's
glow; it offers only a small distant warm object and a vertical brown feature at
the right. At 214×123 source pixels it does not establish full walls, roof,
footprint, route, furnishing count or proportions. **Do not infer a glass
greenhouse, butterfly enclosure or modern house geometry from the name.**

Retained guide text around PDF page 110 additionally identifies Cutlass Bluetane
as a **light Legendary cleaver**, damage **165**, value **40,425**. The follow-up full-page inspection of PDF 110/printed 109 and the Lightning
key on PDF 108/printed 107 confirms one installed Lightning augmentation and
no empty socket rings. The primary weapon icon is only 71×71; faithful weapon
art still requires an explicit original drawing and comparison. Reference URLs/hashes remain in
`screenshots/validation/GP22/next-door-provenance.json`; this follow-up hashes the
retained guide text and page PNG in `next-door-provenance.json`.

## Proposed identities and saved contract

These names and coordinates are proposed internal constants, not authored saves.

| Concern | Proposed contract |
| --- | --- |
| Definition | `greatwood_caves_butterfly_house` in `fc_data.CANONICAL_DEMON_DOORS` |
| Source structure | `fc:greatwood_caves`, new explicit generator and scatter entry |
| Destination structure | `fc:butterfly_house`, explicit fixed-room generator; never generic scatter/loot/population |
| Controller identity | `butterfly:0` through `butterfly:63`; archetype is the keyed definition |
| Index / initialization witness | `fc_dp_bfly_index_v1` / `fc_dp_bfly_initialized_v1` |
| Source/room record | `fc_dp_bfly_v1_<source-index>` |
| Cell ownership | `fc_dp_bfly_cell_v1_<cell>` |
| Player return ticket | `fc_dp_bfly_return_v1`; `family:"butterfly"` |
| Loading leases | `fc_dp_bfly_load` and `fc_dp_bfly_return`; remove only these names |
| Proposed room grid | origin `(640000,272,600000)`, 64×64 cells, stride 128, maximum 4096 allocations |
| Prototype volume envelope | at most 49×28×49; actual room dimension/layout must be explicit in both owners |
| Physical reward | `fc:cutlass_bluetane`, one item in one initially empty 27-slot chest |

The grid probe proves separation for the proposed maximum envelope and existing
160-block exclusions. Guild x extent including exclusion is 599840..608273;
Arboretum is 619840..628273; the proposal is 639840..648273. The minimum gap
between Arboretum and the proposal is **11,567 blocks**. These are half-open
bounding intervals, not generated or cleared world regions. The y envelope ends
at 300, below the retained overworld ceiling. Resurvey if dimensions/stride move.

Use source schema1 with immutable id/archetype/region/origin/source/normal,
monotonic safe revision, source placement `pending → placed → confirmed`, unlock
state, optional room and reward flags. New source allocation begins only after
its independent index/witness state passes pristine checks; orphan state/cell
reservations mean established history, never permission to initialize anew.

Room phases remain `allocated → placing → seeding → ready`; preparation schema1
is `{phase:"placing"|"placed"|"seeding"|"seeded"}` with DP10's allowed combinations.
Unknown/intent-only preparation remains closed. A successful native placement
followed by a saved placed receipt permits verification, not replay. A seeded
receipt permits only read-only reward validation and a ready retry. A new family
has no old ready saves to migrate, but its future ready/depletion contract should
be retained from its first version.

The return ticket holds schema/family/source-instance id/cell/exact source
dimension and location/door anchor/entering-inside-outside-returning phase.
When physically occupied, that ticket remains sufficient for old-cell protection
and exact return after source/index loss or replacement. It never recreates a
record, room or reward. Fallback return candidates require a matching current
source/cell record; otherwise only the original safe ticket source may be used.

## Challenge authority: explicit boundary

Use a dedicated read-only adapter for raw `fc_mult`, requiring an available,
nonnegative **safe integer**, then compare with 14. Missing, throwing, string,
fractional, nonfinite and unsafe-integer values defer. Do not coerce/normalize
the value, use `P.add`, borrow a HUD/form result, consume an item or save a
permanent 'best multiplier' that could unlock later.

At the actual synchronous interaction, independently recheck the same valid
Hero, source dimension, unique registered confirmed face, front-side range,
source throat/support, current locked record and fresh raw value. Commit unlock
with full-record compare/readback; only that successful durable transition can
open the face or start room allocation. No delayed form response may spend a
previous combat snapshot. A stored unlock audit value can explain the accepted
event, but never authorize a second placement or payout.

`next-door-authority-and-grid-probe.mjs` exercises the actual current legacy expression
and an unimplemented strict-reader prototype. Numeric 14.5 and string `"14"`
currently satisfy the old threshold; the proposed reader refuses them. The
existing hit callback credits any melee hit, including a cow, and a string
counter concatenates. Ordinary projectile/Will damage does not update this
counter. Preserve the legacy expression and event behavior in this milestone.

**Strict numeric reading alone does not establish original active-combat parity.**
`fc_lastHit` is a persisted dynamic property compared with `system.currentTick`.
The arithmetic probe demonstrates that a value from a longer previous session
(lastHit 10000, new currentTick 20, multiplier 14) does not satisfy the current
decay predicate. Native reload behavior was not run, but this shows that the raw
threshold has no independent freshness witness. Original damage scaling,
qualification, shield behavior and area-transition loss are also unresolved.

A bounded first portal pilot may explicitly use the **existing live numeric
counter as a Minecraft adaptation**, leaving full combat fidelity open. If the
milestone is intended to establish original *active* multiplier semantics, first
design an independently witnessed current-session combat authority and its
damage/reset/transition lifecycle. Do not silently invent a 240-tick expiry or
retroactively normalize legacy properties: the current counter can remain above
14 during decay, and 'recent hit' is not the original multiplier formula.

## Required owners and integration edits

Line references below identify the reviewed `main.js` hash, not mutable future
line numbers. The existing DP10 integration audit provides the longer inventory.

| Owner / current location | Required implementation |
| --- | --- |
| `scripts/fc_data.py:95,142,660` | Add only the new Legendary and keyed realm. Keep `DEMON_DOORS` byte/semantic ordering and all eight records unchanged. New definition has threshold14, destination version1, one chest reward and xp0. |
| `scripts/gen_behavior.py:65,827` | Emit only the new weapon item plus affected generated game data through existing emitters. `emit_script_data()` embeds a generated Guild/Chamber contract; compare those old subtrees exactly, especially after concurrent Guild passes. |
| `scripts/gen_item_textures.py:1233` | Add a verified cleaver-specific painter or use supported `kind:"cleaver"` as an explicit initial adaptation. Unrecognized `cleaver_legend` without a bespoke painter silently becomes a sword. Never hand-edit the generated PNG. |
| `scripts/gen_resources.py:1222,1291` | Regenerate atlas and language through their owners, preserving every old entry. A melee weapon does not need an armor attachable. |
| `scripts/gen_structures.py`, `scripts/door_realms.py` | Separate new Greatwood Caves source and distinct Butterfly House builder. Define source throat/front apron/encounter space plus room shell/routes/chest/lid/arrival/return detectors explicitly. Keep existing builders and RNG outputs exact. |
| `scripts/structure_manifest.json`, `structure_tables.cjs`, `structure_contract.py`, `gen_screenshots.py` | Add source as scatter and room as fixed, both explicit no-argument main builders and render labels. Native room adapter should use literal `"fc:butterfly_house"` so fixed-placement proof remains recognized. Do not hide placement behind a new unmodelled dynamic ID. |
| New `butterfly_house_doors.js` | Separate identities/keys/grid/source constants and DP10 preparation/ticket protocol. Export the existing public interface used by guards, dispatch, source registration, return and ticks. Omit the Arboretum food-witness challenge. |
| `main.js:14,3230–3258` | Import/construct new owner with source-ready, strict multiplier and native volume/structure adapters. Add six directed admission checks across the three families; each existing controller callback checks both other families. |
| `main.js:3260–3309,3432–3482` | Add separate source-ready and receipt-only face maintenance. Quarantine identity/location before legacy persona dispatch, including pending/unavailable sources and copied/moved canonical markers. Include new maintenance in generic door recovery. |
| `main.js:3311–3322` | Extend block protection, generation exclusion, occupied-owner selection and generic return routing. Preserve occupied original-ticket cells even when their primary history is missing. |
| `main.js:3363–3384` | Add separate third maintenance and third runtime error boundaries; keep five-tick runtime and forty-tick maintenance cadence. A failed family or reporter cannot stop another family's return. |
| `main.js:3388–3417` | Verify shared break/placement-interaction, normal chest access, dangerous-item and explosion guards against the third family. Deferred return clicks retain owner plus clicked cell and recheck both when executed. |
| `main.js:3130,5810–5864` | All generation/boss/anchor exclusion callers inherit new occupied cells. Add new source history guard before ordinary scatter markers. Reserve canonical source before native placement; save success receipt afterward; pending ambiguity never replays. |
| `main.js:5742`, `STRUCTS` and `pickStruct` | Add a separate source entry, not an alias/replacement of Hobbe Cave or Gorge. Adding weight changes deterministic choices for unvisited regions; review and document that delta. Existing placed-region flags and canonical reservations remain authoritative. |

The global Legendary builder currently forces value45000, slots0 and speed
"varies". Preserve those existing items. For the new Cutlass, either document
the established balance adaptation or add **optional per-entry defaults** whose
absence preserves every old Legendary exactly. Do not silently rewrite all
Legendary values to make one new item exact. Damage165 passes through the current
`mc_damage` mapping to 20; this is a Minecraft balance conversion, not 165 native
damage. Use the verified single Lightning augmentation when designing the new item;
review its Minecraft effect mapping separately.

## Implementation sequence and review gates

1. Freeze current main/controllers/data/assets and all protected archives before
   edits. Resolve the bounded source/room composition, routes and weapon visual/
   guide-verified Lightning mapping; write explicit adaptation limits. Choose whether the first
   challenge uses current-counter adaptation or a separately designed original
   combat authority. Do not enable scatter until the entire path below works.
2. Implement the new source/room/reward owners and independent keyed definition,
   then the separate controller. Reuse DP10's full-record preparation behavior
   and exact native readbacks, with its own constants and empty generated chest.
3. Integrate all dispatch/admission/protection/return/maintenance/scatter edges.
   Use actual-main AST extraction tests, not only controller mocks, to prove
   that literal structure IDs, source receipts, callbacks and guards are wired.
4. Run behavior regression **before** targeted regeneration; regenerate affected
   owners only. Compare all preexisting structure outputs and every old
   Legendary/persona/data subtree. Test every negative matrix below before
   final render/provenance and isolated reviewed-index validation.
5. Inspect source, interior, arrival-to-chest and return views; review semantics
   independently; commit/push one coherent third-family pilot checkpoint with
   native acceptance still explicitly unrun. Do not mark full original geometry,
   combat fidelity or the legacy conformance scoreboard complete.

## Minimum acceptance matrix

- **Identity:** all eight old persona records/order unchanged; Warrior still
  requires its existing multiplier expression and pays Harbinger; old unregistered
  Gorges/Hobbe Cave/Nostro unaffected; pending/missing/read-failed new sources
  never become legacy faces or replay source placement.
- **Challenge:** 13 refuses,14 passes; string/fraction/nonfinite/unsafe/missing/
  throwing values refuse without writes; wrong player/dimension/backside/range/
  source or changed locked authority refuse; delayed UI cannot unlock; successful
  unlock pays no item/XP and does not alter the global multiplier.
- **Preparation:** transplant DP10's before/after/ignored/wrong native placement
  and item effects, late complete-volume/shell changes, all-slot contents,
  replaced containers, metadata changes, entities, unreadable authority,
  same-revision history changes, revision exhaustion and receipt-write failures.
  Exactly one successful placement and one physical shared Cutlass; no replay,
  reseeding or reconstruction after ambiguous effects.
- **Six admission edges:** active or unreadable foreign tickets block entry;
  readable absent/outside states preserve established semantics. A foreign
  failure cannot prevent a healthy own-ticket return.
- **Three-family occupied guards:** each current room and each occupied orphan
  ticket cell blocks edits/dangerous uses/generation while normal nonsneaking
  chest collection remains native. Lost ledgers never redirect a ticket to a
  different cell or source. A queued return from cellA cannot return from cellB.
- **Maintenance isolation:** throw each of the three maintenance/tick/report
  boundaries in turn; both healthy families retain exact cadence and return.
- **Geometry and distribution:** complete shell; empty chest and clear lid;
  supported arrival/exit; body-clear complete routes; disjoint cells/margins;
  source confirmation does not repair edited throat blocks; all old structure
  bytes/RNG preserved; future-scatter selection delta measured and documented.
- **Native:** source approach, loading, opening animation, collision, travel,
  collection, two-player race, depletion, reload/crash and exact return are
  separate engine checks. Their present unavailability does not permit claims
  of native success or another unchanged pinned-server download attempt.

Remaining information chiefly limits **fidelity**, not the persistence design:
larger trustworthy source/interior/weapon views, complete original proportions,
the original combat formula/events and native behavior.
No content found in this follow-up authorizes relabelling existing locations or
making The Butterfly House another copy of the Library/Arboretum visual world.

## Reproducing the retained probe

Run `node screenshots/validation/GP24/next-door-authority-and-grid-probe.mjs`
from this repository root. It checks the reviewed main SHA before extracting
the legacy threshold. For a later checkout, set `FC_REVIEW_MAIN` to the exact
GP23 main file exported into ignored scratch. The curated helper changes only
input/output paths and adds that source-hash guard; the original helper hash
is retained in provenance. Its counter reader and grid are proposals only.

## Additional reference results

Root and the reference reviewer inspected the two full original guide pages and
both retrieved mirror images. The guide resolves the Lightning icon; its primary
weapon/augmentation images are only 71×71 and 35×35, so full-page enlargement
adds no detail. The mirror provides a 250×257 cleaver inventory panel and a
280×210 exterior doorway view, with classic-style UI and a TLC guide association.
Their capture edition/build/mod history is unverified, so they remain provisional
corroboration and do not increase the accepted corpus of 37. No larger verified
Butterfly House interior was found; do not infer architecture from its name.

See next-door-reference-manifest.json and next-door-reference-findings.md for
exact source/direct links, primary PDF hash, image hashes, attempted fetch
failures and excluded/uninspected candidates. All source pixels remain ignored.
The external retrieval happened after the original architecture audit; it did
not change any production source, native contract or existing family.

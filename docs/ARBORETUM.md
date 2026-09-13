# Greatwood Gorge → The Arboretum

DP7 adds a second traversable Demon Door world for newly placed Greatwood Gorges.
An opened face leads into a separate wooded grove with a winding dry loop, one
physical Wellow’s Pickhammer chest and an exit to that instance’s original source.
This is an offline implementation checkpoint; every native acceptance item below
remains unrun. The whole door catalogue and Guild facility remain in progress.

## Original evidence and adaptations

The retained original 2005 Prima TLC guide labels Greatwood Gorge and The
Arboretum, names Wellow’s Pickhammer and describes full evil or witnessed evil
acts, including about ten Crunchy Chicks. See the inspected source and labelled
interior crops, hashes, source URLs and catalogue comparison in
[GP20’s design audit](../screenshots/validation/GP20/arboretum-followup.md).
Its PDF pages 46 and 173 correspond to printed pages 45 and 172. The original
pixels remain under ignored `tmp/conformance/dp7-candidate/` and the original PDF
under `tmp/conformance/reference-arcanum/`; none are shipped or committed here.

The small interior view supports a dark wooded setting with substantial trunks
and indistinct low curved forms. It does not establish exact roots, a table,
complete room dimensions or a Minecraft plan. The 49×28×49 room, tree placement,
three-wide loop, chest niche, timber exit, lamps and block palette are authored
adaptations. They deliberately give this realm its own circulation and wooded
mass; the Library’s pond, bookcases, furniture and four pickups are absent.
The source retains its existing Gorge, bridge, banks, underpass and carved face.
Only 43 solid cells become air in the new three-wide, four-high throat through
local x31..33, y6..9, z7..11. No RNG or other source cells change.

This pilot supports strict current full evil (`wd:state` alignment -1000), or ten
completed native Crunchy Chick uses witnessed by the same locked instance for
the same Hero. The exact ten-use counter is an adaptation; it is not derived
from the item’s -15 morality effect. Original murder-solution parity remains
open. Dialogue is newly written adaptation text.

## Separate identities and existing saves

The keyed `greatwood_gorge_arboretum` definition is separate from `demonDoors`.
All eight legacy persona indices, challenges, immediate rewards and modulus
remain unchanged, including the old mismatched Wellow/Solus entries. Existing
unregistered Gorges are neither rebuilt nor assigned a canonical challenge.
Nostro’s story passage remains separate. Guild v1 state and return ticket schemas
retain their existing owners.

New source placement records an immutable region/origin descriptor before the
native structure call. A durable completion receipt follows a successful call;
only that receipt and fresh source clearance allow confirmation. Confirmations
can retry after temporary read/loading failures. Unknown pending placements stay
reserved; neither a missing scatter marker nor a later sweep replays the build.
Partial placement and an unavailable receipt can require manual investigation;
there is no repair/reset command that guesses saved history.

A separate initialization witness, bounded index and per-instance records own
up to 64 sources. Entries and Hero progress are never evicted to make space.
Unavailable, malformed or missing established history defers affected operations.
A wholly missing installation, including all witnesses and records, cannot be
distinguished from first use. There is no atomic native transaction guarantee.
Canonical markers and reserved source locations cannot fall through to legacy
persona assignment or opening-time payout. Face recreation reads the confirmed
record; a face never owns unlock or reward history.

## Challenge and travel

A witnessed food use requires a valid live Hero in readable Survival or Adventure,
within six blocks on the front side of exactly one locked, unobstructed source.
Progress belongs to that Hero and that instance. Creative, behind-face, distant,
ambiguous-source and unavailable source/progress uses do not receive credit. Native
food use performs consumption; the script never removes a second chick.
`readAlignmentAuthority` validates the raw current schema and bounded integer
without migration, normalization, clamping or legacy fallback. The witness runs
before the existing consumable morality handler can normalize missing history.
Food progress does not require alignment history: a null alignment refuses the
full-evil shortcut while ten independently witnessed chicks can still unlock it.

The pinned 2.1 completion event provides no unique use ID. Same event-object and
same-tick suppression prevent bounded duplicate credit, but cannot prove exactly
once across replay, restart or a crash between native consumption and journal
write. Existing consumable effects retain their existing owner. Do not report
these injected event tests as observed native consumption or crash durability.

An unlocked mouth uses dwell, disarming and cooldown. Admission requires readable
return history in both portal families, a safe source approach and a verified
room. The Arboretum grid begins at (620000,272,600000), uses 128-block spacing and
64 columns, and has 4096 bounded cells. It is disjoint from the Guild’s grid.
Allocation commits monotonically before effects and never recycles a cell.
Only one Arboretum room job and one rotating return-loading lease operate at once.

Room preparation checks the entire candidate volume for air, rechecks entities
and late changes before placement, then verifies the full barrier shell, standing
routes, arrival, exit and empty chest. Native scan cost remains unprofiled.
Placement, seeding and ready state are journaled separately. Ambiguous placement
can only be inspected; it cannot authorize a second structure write. Ambiguous
seeding defers without another Pickhammer. No visited room is rebuilt or reseeded.
The shared native chest provides collection: entering, interacting with the face
or reopening grants no item or XP. Deleting a collected item does not restock it.

A player ticket is committed before crossing and retains the exact source,
instance and cell. A safe recorded approach is preferred; the supported bank
fallback is local (32.5,6,6.5), not the unsupported ground farther north.
Returns require actual occupancy of that ticket’s bounded Overworld cell. A valid
occupied ticket survives lost/replaced world records; it never borrows a different
source. Unavailable ticket reads defer before mutations or teleport. A confirmed
absent/invalid ticket can recover only through the unique current occupied room.

Both families contribute block, dangerous-item, explosion and world-generation
guards for their actual allocations and readable ticket-owned old occupied cells.
Native ordinary non-sneaking container access remains available. Deferred return
clicks recheck the same owner and exact clicked cell. A failed unrelated family
read can block new admission, but does not block a healthy original-family exit.

## Owners and evidence

- Geometry: `scripts/door_realms.py` and `scripts/gen_structures.py`.
- Definitions/export: `scripts/fc_data.py` and `scripts/gen_behavior.py`.
- Runtime: `arboretum_doors.js`, main adapters and the small Guild admission gate.
- Alignment authority: `wd/alignment.js`, with existing state mutation unchanged.
- Contracts/rendering: `structure_manifest.json` and `gen_screenshots.py`.

[DP7 evidence](../screenshots/validation/DP7/) records the reviewed-index validation,
actual owner/callback failures, required behavior gate before targeted generation,
source/room contracts, focused views and exact asset/render deltas. C2 now contains
36 structures; the full card set contains 33 structures. The legacy C3 denominator
stays 45 leaves, with 7 done. Renderer grades do not establish original-game fidelity.

## Native and reference acceptance still open

Walk the source throat and both loop directions, inspect canopy lighting, actual
collision and chest lid/access, and test particle visibility. Verify consumption
in Survival and Adventure, rejected Creative uses, competing Heroes, delayed
reads, failed writes, reconnect/restart, room loading and scan/watchdog cost.
Exercise both portal families simultaneously, exact source return, independent
old-ticket protection, blocked exits, reward collection and no duplicate rewards.
Confirm saved Gorges, Guild history and occupied construction remain intact.
All of these are unrun. GP20’s bounded server-acquisition attempt encountered
transport failures; no Bedrock binary or world has been executed.

Seek clearer original neutral interior/source views before asserting layout or
root detail. Complete original challenge alternatives and more individual realms
in later reviewed passes, preserving legacy identities and story exceptions.


## DP7 validation result

All 55 base gates and 65 ESM syntax checks pass in the isolated reviewed-index
snapshot. Runtime 27, actual main integration 16, alignment 6, Arboretum geometry 9,
Gorge 9, Library 5 and retained Guild adapter 38 groups pass. Independent runtime
review passes six negative probes against the final owner; its retained initial
checkpoint reproduces the revision-exhaustion defect before the final guard.
The first full run passed 54/55: the older rectangular-placement fixture lacked
new external portal dependencies. Only that fixture changed and its nine groups
reran successfully; the original result/log is retained. The earlier population
fixture correction and development failures are also explicitly recorded.

Fresh 36-asset C2, all 282 full PNGs and Guild diagnostics pass. Compared with GP20,
only the Gorge asset/C2 image changes and the Arboretum is added; all 34 other
assets/C2 images remain exact. Only the Gorge card and containing places gallery
change among 281 existing full PNGs, with one Arboretum card added. Root inspected
both cards, the gallery and six focused geometry views. Native acceptance remains
unrun. DP7 is the next visual baseline; C3 retains 45 leaves and 7 done.

# DP7 candidate: Greatwood Gorge to The Arboretum

Read-only proposal retained with GP20 evidence, 2026-09-13. No implementation or
native acceptance is claimed. Source images stay in ignored scratch; only this
report and its text/code/results are retained here.
Choose the **Greatwood Gorge evil-witness door leading to The Arboretum**, with
**one physical Wellow's Pickhammer chest per new canonical door instance**.
The established Gorge already supplies a separate architectural source. The
2005 primary guide includes a labelled destination image and the challenge/reward
pairing, so this candidate can support an individually designed first room
without guessing another legacy persona's identity.

## Retained original reference and its limits

Casey Loe/Kaizen Media Group, *Fable: The Lost Chapters, Prima Official Game
Guide*, Prima Games, 2005, ISBN 0-7615-5180-8. The retained edition/copyright
inspection is documented in `docs/LIBRARY_ARCANUM_REFERENCE_REVIEW.md`.
[Original-era guide PDF](https://www.ogxbox.co.uk/media/com_eshop/attachments/Fable_The_Lost_Chapters_Strategy_Guide_Book.pdf).

- PDF page 46, printed 45: the Gorge-specific section establishes fully evil
  alignment or evil acts in view; it describes roughly ten Crunchy Chicks as
  another route and names Wellow's Pickhammer. The source-door gameplay view
  shows a dark, pointed stone surround among tall trunks and warm foliage.
- PDF page 173, printed 172: the same pairing appears in the appendix beside
  source and interior gameplay images. The second image visibly labels itself
  **The Arboretum**. It supports a shaded wooded setting, substantial trunks,
  green ground and low curved forms around the foreground/middle. Those small
  forms are too indistinct to identify confidently as specific roots, furniture
  or masonry. Do not reproduce an invented detailed object on their authority.
- Native extracted source image `tmp/conformance/dp7-candidate/prima-p46-image-017.png` is only 207x153;
  interior `tmp/conformance/dp7-candidate/prima-p173-image-018.png` is only 116x180. Full rendered pages were
  inspected too. These are contemporary TLC images, not Anniversary; the exact
  capture platform/build is not identified. No complete overhead layout,
  measured dimensions, complete tree count, exact chest orientation, return
  view or soundtrack is established.

The contemporary Ace5180 Area Item FAQ (updated 2005-12-21, reread online
2026-09-13) independently groups The Arboretum under Greatwood Gorge and lists
Wellow's Pickhammer in a treasure chest. It describes the evil-act/evil-character
distinction. This corroborates identity and physical discovery, not geometry.
[TLC Area Item FAQ, Greatwood Gorge / The Arboretum](https://gamefaqs.gamespot.com/xbox/929075-fable-the-lost-chapters/faqs/39945).

All external PDF/images remain ignored under `tmp/conformance/`; retain the
hashes in `screenshots/validation/GP20/arboretum-followup.json`. Generated art must be original. The book
image is sufficient for a bounded first design, not a full visual conformance
grade. Before closing the destination, obtain a larger original TLC traversal
or compare a native player-height capture with the limited evidence honestly.

## Exact current source boundary

Run `python screenshots/validation/GP20/arboretum-followup.py` from the repository
root. To retain the same log, append `> screenshots/validation/GP20/arboretum-followup.log`.
It imports actual fc_data, executes the actual Gorge generator with only
its disk-write boundary captured, compares every one of 26,832 emitted cells
and block states with the shipped NBT, and evaluates the actual main.js STRUCTS
literal through its AST. Results are in `screenshots/validation/GP20/arboretum-followup.json`.

Current canonical definitions contain only `guild_library_arcanum`. Preserve
the entire eight-entry legacy array and its order:

| Index / existing ID | Existing contract that must remain intact |
| --- | --- |
| 0 / gourmand | Five pies, Wellow's Pickhammer plus coins |
| 1 / warrior | Multiplier 14, Harbinger |
| 2 / judge | Goodness 500, armour |
| 3 / corrupted | Evil -500, armour |
| 4 / hoarder | Fifty coins, Orkon's Club plus keys |
| 5 / moonlit | Night multiplier 5, Avenger |
| 6 / riddler | Existing riddle, keys plus grimoire |
| 7 / arboretum | Renown 1000, Solus plus elixir |

The names/rewards overlapping canon do **not** identify a saved canonical
instance. Do not append to or reorder this array, change its modulus, reinterpret
`fc_door_idx`, migrate a paid gourmand/corrupted/arboretum face, or infer claim
history from inventory. The generic `fc:demon_door_arch` remains a legacy source.
Its first and retained anchors differ by half a block; at the current eight-entry
length the weighted offset is 24, divisible by eight, so that fact alone is not
a reproduced current persona-change defect. Exact anchor preservation still
matters when adding a new durable mapping.

W3.4 Gorge is 39x16x43 with `door:false`, `cullis:false`, normal bandit spawns
and one ordinary loot chest. Its static face is at the north of the east bank:
outcrop x28..36/y6..13/z8..10; visible carving at z7, feet level y6. No live
canonical face or payment history is registered there. It must receive a
separate explicit canonical placement adapter, not `door:true`, whose generic
adapter assumes the unrelated standalone arch's central x and z5 opening.
Nostro/Lychfield remains its separate story passage and receives no change.

## Smallest concrete implementation scope

1. **Add one keyed definition.** Append `greatwood_gorge_arboretum` to
   `CANONICAL_DEMON_DOORS`, exported separately from the legacy array. Use
   `fc:arboretum` version 1, one empty generated reward chest later seeded with
   `fc:wellows_pickhammer`, zero opening inventory/XP payout. Write original
   dialogue whose personality wants witnessed cruelty and welcomes an evil
   Hero. Do not borrow the current renown-garden speech.
2. **Register only new Gorge placements.** Give each newly placed Gorge an
   immutable versioned instance ID, e.g. `gorge:<dimension>:<region-x>:<region-z>`,
   and persist exact structure origin including y, exact face/approach position,
   dimension and normal. Coordinates identify the new placement once; future
   faces must read the record rather than recalculate an identity. Canonical
   registration needs an explicit pending/placed/ready journal before setting
   the region's completion flag; the existing best-effort population tail is
   insufficient. A failed registration must neither cause structure replay nor
   silently create a generic door. Retry only the recorded unfinished canonical
   registration after verifying the observed source footprint.
3. **Do not retrofit old regions in this pilot.** Existing `fc_rgn_*` regions,
   static Gorges, manually loaded structures, `fc_places` and `fc_doors` arrays
   are not enrollment authority. `fc_places` lacks y/dimension and is truncated;
   source registration therefore needs its own nontruncating authoritative
   per-instance records and bounded paged discovery index. A face property is
   only a derived instance marker. Unknown/corrupt/unavailable records defer;
   no nearest-face adoption, replacement identity, or assumed unpaid state.
   Existing scatter weights/order, mobs, ordinary loot and story routing stay
   unchanged. This preserves generation outside the explicit new-Gorge branch.
4. **Open the actual source throat.** Proposed source centre is local
   `(32.5,6,7.5)` with approach normal `(0,0,-1)`. The new-source geometry must
   create a three-wide, four-high opening and clear the full z7..11 throat,
   including the existing front carving. Keep supported feet and clearance
   from both sides, plus the nearby bank routes. This is a build proposal,
   not measured TLC coordinates. Use final-voxel/footprint tests to settle the
   exact carve before approval; do not reload existing saved Gorges. Opening
   moves/removes the live collider without blocking the throat with decoration.
5. **Support a bounded witnessed challenge first.** The first playable branch
   can support fully evil alignment or ten actually completed Crunchy Chick
   consumptions in this door's view. Current chicks carry -15 morality, while
   the guide discusses about 50 original evil points for about ten chicks:
   counting global morality deltas would incorrectly reduce the food challenge
   to four. Count completed native consumption events, scoped to player AND
   exact locked instance; retain existing food consumption/morality ownership
   and never remove another ten items on opening. Require current identity,
   dimension, position and fresh locked record when counting/completing. A
   single event cannot count toward two nearby doors. Persist per-Hero progress
   with bounded journal records; never combine two Heroes' partial acts.
   Do not evict unfinished progress silently when a record/page fills. A native
   completed-use event and a dynamic-property write are not one atomic operation:
   on an ambiguous write, preserve existing history and refuse unlock rather
   than inventing credit, consuming again or promising an automatic refund.
   This is an explicit engine durability check, not something mocks can prove.
   Read alignment through its existing owner with validated available history;
   full evil maps to the existing -1000 limit, not legacy corrupted's -500.
   A first food-only/full-evil pilot must explicitly leave the original witnessed
   murder alternative open; do not advertise all original solutions as complete.
   Exact view distance and whether to require facing are adaptation choices;
   a proposed six-block front-side radius needs tests and must be labelled.
6. **Give each instance its own room and durable recovery.** Current Guild code
   hardcodes `guild`, Arcanum geometry, four rewards, its property keys, lease
   names and cell grid; it cannot simply accept a second definition. First
   introduce an instance adapter and explicit room contract while retaining
   the Guild v1 validator, state, allocation and ticket compatibility. Select a
   **separate bounded Arboretum namespace/grid** for this second owner: proposed
   origin `(620000,272,600000)`, 128-block spacing, 64 columns and 4096 cells,
   with a serialized allocator/lease journal shared by all Arboretum instances.
   Guild's existing grid remains `(600000,272,600000)` with its same bounds;
   even its final column ends below x608113, while Arboretum starts at x620000.
   This proves grid separation only: survey every candidate volume/entity before
   first placement, reserve before building and never infer emptiness or reusable
   claim history from distance. Do not copy Guild's allocator unchanged or reuse
   its lease names. Keep new per-instance state and a separate versioned
   Arboretum return-ticket key; both dispatch through a small shared facade.
   Do not rewrite Guild's old player ticket schema just to add the second room.
   Protect allocated/actually occupied exact cells only. A shared entry gate
   reads both travel authorities and prevents nesting; checked return
   routing uses the player's occupied committed ticket's own family/instance
   and source, including when either primary ledger is gone. Unreadable data
   defers affected travel before mutation as in DP6. An unreadable unrelated
   room's ticket must not erase a healthy occupied family's independent return
   authority. Guard unions retain independent visitors and both room families
   without reserving either grid. No return ticket borrows another instance's
   default approach, source or reward state.

The deliverable is one end-to-end pilot: new Gorge registration, witnessed
challenge, visibly opened physical entrance, verified individually authored
realm, physical shared reward, exact reusable return and durable recovery.
Registration and two-room compatibility are internal implementation steps;
freeze all existing Guild source/reward/ticket regressions against that layer
before wiring admission. A geometry-only or definition-only result does not
complete this pilot.

## Individually authored destination brief

Use a compact shaded arboretum, with dense tall tree trunks and irregular green
ground. The proposed path bends around a central planted/root mass, revealing
one reward niche after the turn; an alternate dry arc reconnects to the return
opening so the room is explorable and legible. This provides a distinct visit
from Arcanum's reading bays, pond and book pickups. Those Arcanum objects should
not be copied into the new room. The exact low curved objects in the guide
remain unresolved, so use original ambiguous root/ground forms rather than
claiming a verified architectural model.

A feasible **proposed** contained asset is 49x28x49: feet y3, arrival
`(24.5,3,7.5)`, return `(24.5,3,3.5)`, path bends near `(17.5,3,19.5)` and
`(28.5,3,28.5)`, and the sole chest near `(34,3,35)`. These are explicit
Minecraft design coordinates, not recovered reference dimensions. Keep a
three-wide connected dry loop, full player headroom, irregular rooted canopy
edges, and a concealed storage boundary. The chest must be visibly discoverable
from the inner loop; native collection owns item transfer. A quiet original
ambient mix can be proposed, but no canonical soundtrack is asserted or copied.
Render both a topology view and matched player-height entry/chest views before
fixing version 1. Room layout remains independently authored even if its safe
container dimensions match the existing storage contract.

## Owners, acceptance and stopping point

Owner changes belong to `fc_data.py` and `gen_behavior.emit_script_data`, a new
`door_realms.build_arboretum` plus explicit `gen_structures.arboretum` owner,
the bounded new-source Gorge generator, and owned canonical runtime/adapter
code with main's explicit Gorge registration and complete-use hook. Generated
assets are regenerated only through those owners. This task changes none of them.

The first implementation must prove at least: two new same-archetype Gorges
get distinct immutable IDs/cells/chests and exact-source returns; old legacy
indices/rewards and unregistered existing Gorges are unchanged; interrupted
placement registration never replays a structure or marks unknown history new;
face replacement retains identity/unlock; wrong player/location/instance and
unreadable counters cannot unlock; completed use counts once and two Heroes do
not pool progress; consumption is never repeated at unlock; once-only shared
physical reward depletion; Guild and Arboretum visitors remain independently
protected and recoverable across ledger/ticket faults. Use actual callbacks and
generated final voxels, then the existing domain/base gates. The follow-up is
new-world content/identity integration, not another repeated Guild fault audit.

Native acceptance remains unrun: the complete opening, dwelling, room walk,
collection, return, reload/death and two-Hero sequence must be exercised in
Bedrock. Original murder-solution parity, larger interior footage, detailed
room topology and soundtrack are explicit open source/acceptance requirements.

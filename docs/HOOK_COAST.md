# W2.2 Hook Coast lighthouse and Abbey

Layout recorded before implementation. [B] Retain fc:hook_coast at 37x20x37,
weight 7, snow/sand/rock surfaces, snow theme, Cullis travel, current resident types
and five chest containers. Add explicit clear resident spawn coordinates. Keep
procedural scatter; no fixed island map or saved-world geometry retrofit.

[C] Sources: architecture.md, Hook Coast paragraphs; FullWorld §5;
visual_reference.md, Core Look. They identify a climbable lighthouse, ruined Abbey,
monk/keeper graves and a bell, and streets with stairs between tiers. Local layout,
block palette and dimensions are [B]. Existing southwest lighthouse orientation
is retained; the reference describes southeast placement. This adaptation is not
an exact map reconstruction.

| Feature | Local coordinates |
| --- | --- |
| Retained lighthouse | center (6,28), radius 4; entrance (6,1,24) |
| Lighthouse internal stair | (4,1,26) south to (4,4,29), turn (4,4,30), east to (8,8,30), north to (8,11,27); y values here are stair block heights |
| Lamp-room deck and landing | floor y=11; clear standing point (7,12,27) |
| Abbey terrace | x=26..35,z=15..26; floor y=2 |
| Terrace steps | x=24..25,z=24..25; stair blocks y=1..2 ascending east |
| Abbey entry / aisle | (30,3,25); aisle x=30,z=19..25 |
| Graveyard | x=27..34,z=7..13; two rows of three markers |
| Graveyard bell | (30,3,5) on frame at north end |
| Connecting lanes | x=18,z=0..26; z=6 and 23; lighthouse approach x=6,z=22..25 |

The lighthouse beacon is a static block light. Fire Heart activation, rotating beam,
Ship of the Drowned travel, Maze fight, Abbey barrier/dispelling and evacuation are
not implemented. No new generic Demon Door riddle or unrelated quest is registered.
Manual engine and original-TLC comparison checks remain unrun.

## Routes and interaction anchors

Enter on the clear north lane at (18,1,0). Turn east along z=6 to the graveyard
bell at (30,1,6); the two marker rows at z=9/12 have clear neighboring paths.
For the lighthouse, continue south to z=22, turn west to x=6, and enter at z=24.
Turn inside to (4,1,25), climb south through stair blocks (4,1,26)..(4,4,29),
use the level landing (4,5,30), ascend east across (5,5,30)..(8,8,30), then north
through (8,9,29)..(8,11,27). Step west onto the lamp-room deck at (7,12,27).
Step coordinates list block heights; standing feet are one above each stair.
The beacon remains at (6,12..13,28). Foundations replace water under the tower.

For the Abbey, turn east at z=23 then south to (23,1,24); climb east over
(24,1,24)/(25,2,24) onto the terrace, floor y=2. Walk through (26,3,24) to
(30,3,24), then north along the nave aisle to the altar at z=18. The original
Abbey bell is retained at (32,6,23), in addition to the graveyard's north bell.
The clear central street also reaches quay stairs at z=26 and the raised dock.
All four cottage entrances now have two-block headroom; their interiors/chests
remain. Clearing is limited to connecting routes and quay access; snow stays
elsewhere. The five original chests retain the current Hook Coast loot table.

Runtime local feet: Oracle (30.5,3,20.5), guard (18.5,1,23.5), resident
(23.5,1,10.5). These are the existing three resident types; the Oracle's presence
is inherited implementation, not a claim of TLC Hook Coast canon. Existing NPC
interaction handlers are reused. Cullis stays at the clear center (18,1,18).
Raw structure load initializes blocks only; use fresh scatter to verify residents,
loot and travel. Saved region flags prevent duplicate initialization in mocks;
existing placed towns are unchanged and no anchor/geometry retrofit is supplied.

## Verification and provenance

Six regression groups check bounds/known palette, stable dimensions and runtime
flags, lighthouse stair directions/clearance/landing/foundation, raised Abbey and
retained features, grave rows/bells/cottage doors, routes from the north entry to
every resident, all five chests and the lamp deck, and actual-source scatter on
snow/sand/rock with clear translated spawns/Cullis and saved-region idempotence.
The owner at fae89fb fails all six. Full-cell route modeling cannot validate
Bedrock stair/glass/snow collisions, lighting or NPC transactions.

Generated evidence is under screenshots/validation/W2.2. The south view is the
actual owner rendered at yaw=-0.72,pitch=0.75. The full-site cutaway removes the
west wall x=2..3,y=2..19,z=24..32 and roof x=2..10,y=14..19,z=24..32 only in a copy.
The separate lighthouse-stairs diagnostic isolates x=0..10,z=23..33, removes the
outer shell and roof, and omits deck y=11 except the final stair and landing.
Its exposed solid stair supports and floating glass drum are diagnostic artifacts.
The actual structure retains its full shell, roof and deck.

[G] Inspected south/cutaway/stair views show the cold harbor silhouette, new raised
Abbey approach, grave rows and continuous internal stair flights. The full-site
cutaway hides some flights behind the remaining shell, hence the isolated view.
The block renderer exaggerates snow layers and treats stairs/glass as cubes.
An image search found a [Hook Coast wiki candidate](https://fable.fandom.com/wiki/Hook_Coast),
but its original-2005 versus Anniversary provenance is unverified; no original-TLC
pixel comparison or canon grade is claimed. C2 appearance metrics remain separate.

## Manual checklist — all unrun

- [ ] Scatter fresh sites on snow, sand and rock, including slopes; inspect all
      terrain edges, lighthouse foundation, water/ice and terrace retention.
- [ ] Walk north entry to all cottages, grave rows/bell, quay, Abbey and lamp room;
      climb/descend the one-wide tower stair, both turns, final hatch and terrace.
- [ ] Check Bedrock stair collision, fall edges, lantern/sea-lantern lighting,
      snow/glass states, headroom and two-player crowding inside the lighthouse.
- [ ] Open all five chests and verify loot; interact with the existing residents
      and both bells. Check Oracle/guard placement and pathing between tiers.
- [ ] Discover/use Cullis, save/reload/revisit and verify no duplicate population or
      loot initialization. Confirm existing saved towns remain unchanged.
- [ ] Compare with verified original-2005 Hook Coast/lighthouse/Abbey screenshots;
      keep Fire Heart, rotating beam, ship travel, Maze fight, Abbey barrier and
      evacuation marked unimplemented.

W2.2 review also strengthened C2's optional spawn contract. An unintended copy of
Hook Coast's anchors into Snowspire was removed before commit; the new cross-POI
fixture proves that a 30.5-wide coordinate fails in Snowspire's width 29. Count,
shape, finite-number, feet/floor and headroom-bound fixtures now run in the shared
contract suite. The pre-fix missed-error report and post-fix tests are retained.

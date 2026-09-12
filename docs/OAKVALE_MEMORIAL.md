# W2.3 Oakvale Memorial Garden

Layout recorded before implementation. [B] Keep fc:oakvale_village, height 14 and
depth 35; widen from 35 to 53 for a distinct eastern garden. Runtime STRUCTS and
C2 manifest change together. Retain grass/sand, weight 8, village theme, existing
three resident types, current chest-loot table and Cullis travel.

[C] architecture.md, Oakvale; FullWorld §2; visual_reference.md, Core Look describe
an eastern uphill memorial path, an axe-swinging hero and graves, with a coastal
tree/well village. Dimensions, block sculpture and compact scatter layout are [B].
The original squeezed memorial at (28,13) is replaced; village buildings stay.

| Feature | Local coordinates |
| --- | --- |
| Retained village / great oak / well | x/z=0..34 / (21,17) / (14,18) |
| Eastern approach | x=17..34,z=15..16, floor y=0 |
| Garden steps | x=35/36,z=16..18, stair y=1/2, ascending east |
| Walled raised garden | x=37..51,z=6..25, floor y=2; west gate z=16..18 |
| Axe-hero plinth / head / axe | x=43..45,z=12..14,y=3..4 / (44,9,13) / x=46..48,y=8..11,z=13 |
| Six grave markers | x=40/44/48,z=9/22, y=3..4 |
| Clear garden aisle | x=38..50,z=17..18, feet y=3 |
| Resident feet | farmer (4.5,1,11.5), fisher (22.5,1,24.5), guard (17.5,1,5.5) |
| New computed Cullis arrival | (26,1,17) |

Procedural scatter and saved ID remain. No fixed map, historical name/quest marker,
new Demon Door, digging reward or saved-world retrofit is claimed. Full village
walkability remains W4.1. Required original-TLC and engine checks remain unrun.

## Routes and retained behavior

From (17,1,0), pass the original north gate and walk south to z=15. Turn east
along the two-wide gravel lane through (34,1,16). Ascend east through stair blocks
(35,1,16)/(36,2,16), then enter the west garden gate at (37,3,16). The garden's
main aisle at z=17..18 reaches the statue approach (44,3,15), the candle near
(44,3,16), and clear grave-adjacent points x=40/44/48,z=10/21. The central oak
(21,17), well (14,18), field/scarecrow and coastal quay remain at their old coordinates.

Five existing emitted chests remain at (10,1,11), (11,1,21), (19,2,27),
(28,1,11), (28,1,21); the garden adds none. The old cottage/quay overlap already
overwrites a sixth attempted cottage chest at (18,1,26). This inherited collision
is not repaired or counted as a sixth reward here; full cottage/quay walkability
belongs to W4.1. Removing the old memorial also removes its candle that overwrote
part of the northeast cottage's rear wall. Seeded rose rolls are retained so later
flower randomization keeps its prior stream.

The same three resident types now use clear explicit feet coordinates. The widened
rectangle moves the runtime's computed Cullis arrival to (26,1,17), cleared and
connected to the new lane. The shared actual-source harness verifies translated
spawn/travel coordinates on grass and sand and skips repeated initialization for
saved regions. Raw `/structure load` supplies blocks only. Existing saved town
geometry, region records and stored travel points are not retrofitted.

## Evidence and comparison

Six regression groups pass: dimensions/runtime/C2 coupling and palette/bounds,
garden walls/gate/steps/graves, statue legs/head/axe, retained village landmarks
and exact chest coordinates, north-gate-to-garden/resident/Cullis routes, and actual
scatter population/travel/save behavior. The owner at a0b59f2 fails five groups;
its population test still passes because the new spawn points also fit the old
village. The evidence records that distinction. C2's actual placement suite now
includes the 53x14x35 rectangle and checks terrain/loot/save-envelope dimensions.

Original generator images in screenshots/validation/W2.3 include before, south,
a garden-only detail and the full card. The detail copies x=35..52,z=5..26 to an
18x14x22 voxel canvas; no garden geometry is removed. C2 renders all 29 structures,
and full all-category rendering runs under tmp/conformance/W2.3-full-screenshots.
No static render or full-cell walking model is an in-world pass.

[G] The inspected renders show an eastern raised garden, six distinct memorial
markers and a taller axe-bearing figure, while the coastal village remains readable.
The isolated garden view shows its separated legs, pale head, dark broad axe and
open central aisle. The figure is rigid and the axe vertical; a convincing swinging
pose, finer grave variety and more natural hillside integration remain visual gaps.

Two images from this [2021 walkthrough](https://www.coordinatedgaming.com/Walkthrough/Fable_Treasure_Of_The_Ghost_Pirate)
were fetched and inspected only in ignored developer scratch storage. The entrance
image shows tall stone piers, urns and open ornate metal gates on an uphill wooded
path. The statue image shows a lunging armored figure holding a diagonal axe over
its shoulder on a large weathered plinth. Our open stone/lantern entry and upright
figure are simplified and visibly differ. The article labels the game only Fable;
original-2005 TLC version provenance is not confirmed, so this is a candidate
comparison, not a canon-grade pass. URLs and image hashes are retained in evidence.

## Manual checklist — all unrun

- [ ] Scatter fresh towns on grass/sand, flat/sloped; inspect the wider rectangular
      terrain grading, coastline and the garden's raised walls/entrance.
- [ ] Walk north gate to both stair lanes, garden, statue/candle and all six graves;
      check headroom, stair/partial-block collision and two-player passage.
- [ ] Verify the original oak/well/field/quay and three residents; inspect the five
      emitted chests and leave cottage/quay collision repair tracked under W4.1.
- [ ] Discover/use Cullis at the new clear center; save/reload/revisit to check no
      duplicate population/loot. Confirm old towns/travel records remain unchanged.
- [ ] Compare with verified original-2005 TLC screenshots before grading canon;
      refine swinging pose, grave variety and hillside/entrance details as needed.

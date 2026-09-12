# W2.4 Grey House and cellar

Layout recorded before implementation. [C] architecture.md, Grey House and FullWorld
§11 identify the isolated house, cellar and undead associated with Lady Grey's family.
The manor-cottage, coffins, block palette, always-open stairs and dimensions are [B].
Visual_reference.md Core Look supplies the muted storybook palette target [G].

Add standalone fc:grey_house, 31x20x35, weight 5, grass/rock surfaces and dark theme.
A raised earth mound contains the cellar above local y=0, preserving the scatter
engine's ground plane and saved-region contract without introducing buried placement.
Explicit ordinary chest loot, three existing undead and no Cullis or Demon Door.

| Feature | Local coordinates |
| --- | --- |
| North path / outer gate | x=14..16,z=0..3, floor y=0 |
| Three-wide approach steps | x=14..16,z=4..8, stair y=1..5, ascending south |
| Raised mound / porch | x=5..25,z=9..31, top y=5 / x=13..17,z=9..11 |
| Manor floor / front entrance | x=8..22,z=12..28,y=5 / x=14..16,z=12, feet y=6 |
| Slate roof / chimney | x=7..23,z=11..29,y=11..19 / (20,17,25) |
| Stone cellar | x=8..22,z=13..28,y=0..5; interior x=9..21,z=14..27 |
| Two-wide internal stairs | x=10..11,z=14..17, stair y=4..1, descending south |
| Coffins | x=14/18,z=21..23,y=1 |
| Chests | house (20,6,15), cellar (20,1,26) |
| Undead feet | yard (15.5,6,10.5), cellar (12.5,1,20.5)/(19.5,1,24.5) |

Walk from north gate up the approach, enter the manor, turn west at z=13 and
descend the internal stairs to the cellar aisle at (11,1,18). Both chests and all
spawn points must be reachable with two-block clearance in the voxel route model.

No family murder investigation, Amanda ghost, quest-gated cellar opening, Demon
Door marriage riddle, legendary/unique reward or fixed Oakvale link is implemented.
No old-region retrofit or in-world/canon pass is claimed.

## Manual checklist — all unrun

- [ ] Scatter fresh sites on grass/rock, flat/sloped; inspect grading and mound.
- [ ] Walk gate, approach steps, manor and both cellar stair lanes in both directions.
- [ ] Open both chests; inspect lids, furniture, lighting, coffins and stair collision.
- [ ] Verify three undead at clear spawns; fight in cellar with two players.
- [ ] Save/reload/revisit: no duplicate population or chest initialization; old regions retained.
- [ ] Compare exterior and cellar with verified original-2005 TLC screenshots.

## Validation and visual evidence

Seven regression groups pass, including bounds/palette, manor/cellar landmarks,
stair orientation and headroom, north-entry routes, exact chests/clear lids,
negative geometry fixtures and the actual scatter function on both grass and rock.
Blocking the cellar stair makes the route test fail; obstructing a chest lid makes
the chest test fail. C2 adds this rectangle to terrain/loot/save-envelope checks.
The runtime adds three undead once per newly placed region; no travel point or
Demon Door is registered. Ordinary loot quantities are build choices, not canon.
Adding a weighted entry changes future unvisited-region rolls; saved regions keep
their existing flags and geometry. Raw /structure load places blocks only.

All 23 scripts/validate.py gates pass. The explicit base spell invocation and
main.js syntax check are retained separately. Faithful archives stay in ignored
tmp/builds; original preview remains release-blocked despite validator success.

The inspected exterior shows a high slate gable, chimney, pale walls and a clear
front stair with bare trees and a low boundary. It is regular and spare; weathering,
vegetation, silhouette variety and natural terrain integration need refinement.
The cellar cutaway removes every block at y>=5, exposing two coffin forms, lit
stone walls and the rear chest. It is a diagnostic view, not the emitted geometry.
The full card and full-category audit are retained alongside C2's current render.
No renderer metric is a canon or engine grade.

A [Gamepressure TLC guide](https://www.gamepressure.com/fablethelostchapters/mayors-invitation/za46)
provides a screenshot of the stable/lantern location: heavy timber supports,
weathered stone, weeds and cobwebs. This is useful material context, but does not
establish the complete exterior or cellar layout. The page identifies TLC; exact
capture date/platform are unknown. The screenshot is developer-only ignored scratch;
its URL/hash and comparison notes are in reference-candidates.json. The stable,
lantern sequence, ghost and investigation remain absent. Verified complete exterior
and cellar comparison remains pending; no canon grade is assigned.

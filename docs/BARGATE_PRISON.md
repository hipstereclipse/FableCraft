# W3.1 Bargate Prison

Layout recorded before implementation. [C] architecture.md, Bargate and FullWorld
§9 identify fortress courtyard/ramparts, three cell blocks (two explorable), barracks,
torture room, warden office, crests and underground chamber. [B] Compact procedural
scatter adaptation fc:bargate_prison is 41x20x49, weight 4, grass/rock, dark theme.
The courtyard rests at y=5 over a foundation containing the underground room; the
scatter ground plane stays y=0. No fixed island/map or saved-region retrofit.

| Feature | Local coordinates |
| --- | --- |
| Approach / north gate | x=19..21,z=1..5, stair y=1..5 / z=6..8, feet y=6 |
| Courtyard | x=5..35,z=9..43, floor y=5 |
| Ramparts | x=2..4/36..38,z=6..46 and z=6..8/44..46, deck y=10 |
| Rampart stair | x=5..6,z=9..13, stair y=6..10, south up |
| Explorable cell blocks | west x=7..15 and east x=25..33,z=17..29, floor y=5 |
| Third cell-block silhouette | x=16..24,z=35..43, sealed front bars, floor y=5 |
| Barracks | x=25..33,z=34..43, north door x=27..28,z=34, feet y=6 |
| Torture room / upper warden office | x=7..15,z=34..43, floors y=5/10; lower north door x=12..13,z=34 |
| Office stair / west entry | x=5..6,z=34..38, stair y=6..10 / (7,11,39) |
| Underground stair | x=20..21,z=12..15, stair y=4..1, south down |
| Underground chamber / basin | x=16..32,z=16..32,y=0..5 / x=24..28,z=23..27,y=0 |
| Chests | office (13,11,41), barracks (31,6,41), chamber (30,1,30) |
| Guard feet | courtyard (18.5,6,10.5), barracks (29.5,6,37.5), office (10.5,11,39.5) |

Route from (20,1,0) ascends north steps into the courtyard. West stairs reach all
four ramparts. Cell-block doors face the central yard; their corridors reach two
open cells each. Continue south around the third block to the barracks, torture
room and office stairs. From the central north stair landing descend to the basin
room and rear chest; leave by the same route. Water is decorative and avoidable.

Crests are original blue/white geometric block emblems, not extracted game symbols.
Three existing Bowerstone guards retain their inherited behavior; no new prison AI.
No imprisonment, race, poetry/key theft, equipment confiscation/recovery, Scarlet
rescue, time passage, lever-controlled cells, unique rewards or Kraken encounter.
The third cell block is intentionally inaccessible. Coordinates/palette are build
choices; original TLC visual comparison and every engine observation remain pending.

## Manual checklist — all unrun

- [ ] Scatter on flat/sloped grass/rock; inspect foundation grading and chunk edges.
- [ ] Walk entrance, four ramparts, two cell corridors and all four open cells.
- [ ] Visit barracks, torture room, upper office and underground chamber in both directions.
- [ ] Open three chests; verify guards, stair/headroom collision, bars, light and water.
- [ ] Repeat with two players; save/reload/revisit without repeated population or loot.
- [ ] Verify existing regions remain unchanged; compare original TLC exterior/interiors.

## Validation and reference comparison

Seven groups pass: dimensions/runtime/palette/bounds, two open cell blocks versus
the sealed third, barracks/office/torture/basin landmarks, all vertical walking
routes, stair states and three chests with clear lids, negative geometry fixtures,
and actual scatter population/loot/save behavior on grass and rock. The first
route run exposed rear entrances obstructed by the third block. Both rear ground
floor entrances now face the north cross-lane; the initial failure log is retained.
Blocking the chamber entry or closing the first west cell independently makes the
route assertions fail. Existing Bowerstone guards initialize at three clear anchors.

C2 covers the 41x20x49 asset and render, plus terrain sampling, grading, loot scan
and saved-place envelope. All existing IDs remain. Weighted selection changes rolls
for future unvisited regions; already retired/placed regions remain unchanged. Raw
/structure load does not initialize guards or loot. No Cullis or Demon Door added.

Inspected exterior and two diagnostic cutaways: courtyard view retains local y=5..8
and the whole x/z footprint; chamber view crops x=16..32,z=16..32,y=0..4. The roof,
upper tower and foundation are removed only in these diagnostic images. Exterior
shows continuous crenellations, five roof masses and the higher warden tower.
The cutaways reveal open corridors, four cell interiors, north rear entrances and
the basin walkway. Repeated rectangular buildings and plain masonry remain visual
weaknesses; static full-cell routes do not establish engine stair/bar collision.

The inspected [TLC Prison Escape guide screenshots](https://www.gamepressure.com/fablethelostchapters/prison-escape/z21a)
show a dense office desk/book/noticeboard corner and a monumental round basin hall
with a ribbed dome, falling water and the Kraken. Our office props are sparse and
the small flat-ceiling rectangular room differs substantially in scale and shape.
There is no waterfall, grand dome or Kraken encounter. The guide names the 2005
TLC game, but exact image capture dates/platform are unknown. References stay in
ignored developer storage; URLs/hashes are retained in reference-candidates.json.
No canon grade is claimed, and full prison exterior comparison remains pending.

All 24 local validator gates and explicit spell/syntax commands pass; logs and
exit codes are retained under screenshots/validation/W3.1. The route model allows
one-block height changes; it does not prove movement without jumping. In particular,
the top of the chamber stairs has a full-block transition from the courtyard.
Engine stair motion, NPC navigation and water/foundation behavior remain unrun.
Faithful archives remain ignored/local and L4 public release remains blocked.

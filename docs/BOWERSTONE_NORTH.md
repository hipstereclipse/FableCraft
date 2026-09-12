# W2.1 Bowerstone North and Manor

Layout recorded before implementation. [B] Retain fc:bowerstone_market and width
37; extend height/depth from 16/37 to 21/59 by shifting the existing district +22
along z. Runtime STRUCTS and C2 manifest change together. Grass, weight 7, village
theme, chest loot and Cullis registration stay. Retain the four resident types;
add existing Lady Grey in the manor with explicit clear spawn coordinates for all.

[C] References: architecture.md, Bowerstone cluster and North paragraphs;
FullWorld §3; visual_reference.md, Core Look and Map And Ambient Detail. These
specify a class divide, refined houses and Lady Grey's grand manor. Dimensions,
layout and materials are [B] adaptations for procedural scatter, never a fixed map.

| Feature | Local coordinates |
| --- | --- |
| Existing market / river / southern gate | original z +22; river z=38..42, gate z=55 |
| Existing rich houses | x=4..11 and 25..32, z=28..35 |
| Internal class wall / open gate | z=37, gate x=17..19, bridge floor y=1 |
| Main north street / Cullis destination | x=18,z=24..36 / (18,1,29) |
| Manor shell / roof | x=9..27,z=3..15, floors y=0/5, roof y=9..19 |
| Manor front door | x=17..19,z=15,y=1..3 |
| Forecourt and open gateway | x=9..27,z=16..23; gateway x=17..19,z=23 |
| Manor stairs | x=23..24,z=12..8,y=1..5; landing z=7,feet y=6 |
| Guard / trader / barkeep / resident / Lady Grey feet | (18.5,2,38.5) / (8.5,1,31.5) / (29.5,1,48.5) / (20.5,1,47.5) / (18.5,1,9.5) |

The internal gate is an architectural open passage. Arena completion/invitation
checks, resident access enforcement, the Solus-specific shop, jail and full Quay
remain missing. Existing upstairs townhouse access is deferred to W4.2. No saved
world geometry/region retrofit is claimed. Raw structure load does not initialize
population/loot/travel; use fresh procedural scatter for gameplay verification.

## Routes and runtime behavior

Enter (18,1,58), pass the south gate at z=55 and go around the center market stall
through x=20,z=49..52. Approach the bridge at (18,1,45), climb the south step at
z=44, cross its raised deck (feet y=2) and pass the class arch at z=37. Descend the
north step at z=36. Continue through the rich district and forecourt gate at z=23
to the manor door at z=15. The clock tower moved west to x=14,z=26 to clear this
axis. The existing shop house entrance is (8,1,28); the barkeep's south house is
entered through (28,1,45). All ground-floor house chests have clear adjacent access.

Inside the manor, turn east to (23,1,13), climb north through z=12..8 and reach
(23,6,7). The upper salon connects to the sleeping prop and storage barrel. The
library, reception table and one new chest occupy the ground hall's sides. The
seven existing chests remain; all eight roll the existing Bowerstone loot table.
This adds one loot container but no new reward type or price. The current travel
registration computes (18,1,29), a clear point on the north street in the enlarged
rectangle. Actual-source mocks verify its translated position and clearance.

The existing trader, barkeep and Lady Grey interaction handlers remain authoritative.
Lady Grey now appears once per newly scattered Bowerstone, not as a globally unique
NPC; multi-town duplicates and existing romance/progression behavior need manual
review. No new NPC definition, dialogue, item stock or quest completion is authored.

## Evidence and limitations

Six regression groups check generated dimensions and C2/runtime coupling, unknown
palette/bounds, manor rooms and furnishings, class wall/forecourt/retained houses,
bridge/manor stair directions and clearance, entry-to-landmark/chest/spawn routes,
and actual scatter population/Cullis/save behavior. The previous owner at ed57d1e
fails all six. C2 placement tests also exercise the 37x21x59 terrain, loot and saved
settlement envelope. The route model approximates full cells and one-block steps;
it cannot prove engine collision, lighting, NPC navigation or transactions.

Original generator images are retained in screenshots/validation/W2.1: before,
south, north, diagnostic cutaway and full card. The cutaway removes the manor roof
and upper floor only from a copy; upper furnishings appear suspended. The shipped
structure retains both floors and roof. C2 separately regenerates all 29 structure
renders; the full all-category pipeline runs under tmp/conformance/W2.1-full-screenshots.

[G] Inspected renders show a dominant pitched-roof manor, symmetrical window rows,
stone/quartz forecourt and class wall, with the market, bridge and Tudor houses
retained. The roof is tall and the block sculpture remains a simplified manor;
these are layout observations, not a verified original-2005 silhouette match.
Image search surfaced a Lady Grey courtyard candidate on
[The Game Hoard](https://thegamehoard.com/2018/09/25/fable-the-lost-chapters-xbox/)
and generic South screenshots; no verified full North/manor comparison is recorded.
Canon grade remains pending. Offline appearance metrics are separate from fidelity.

## Manual checklist — all unrun

- [ ] Generate fresh Bowerstone sites through scatter on grass, flat and sloped;
      inspect the larger 59-block spacing envelope and terrain edges.
- [ ] Walk the south approach, market detour, both bridge ramps, class arch,
      rich-house entrances, forecourt and both manor floors in both directions.
- [ ] Check stairs, upper stairwell fall edges, headroom, light and glass/leaf states
      in Bedrock; static renders approximate partial-block collision.
- [ ] Open all eight chests and the manor barrel; verify loot and accessibility.
- [ ] Verify all five residents spawn clear and interact normally; check Lady Grey
      across multiple scattered towns, NPC pathing and two-player doorway crowding.
- [ ] Discover/use Cullis travel, save/reload/revisit, and verify no duplicate
      population/loot registration. Confirm old placed towns are not retrofitted.
- [ ] Compare with verified original TLC North/manor shots; retain missing Arena
      admission, resident gate enforcement, Solus shop, jail and Quay as open gaps.

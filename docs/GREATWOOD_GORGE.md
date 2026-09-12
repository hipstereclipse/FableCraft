# Greatwood Gorge — W3.4

Planned before implementation: owner `greatwood_gorge`, ID `fc:greatwood_gorge`,
39×16×43, weight 6, grass/rock, forest theme. Foundation y=0; banks top y=5.
Dry ravine x=15..23, z=6..38; wooden bridge x=12..26,z=17..21,y=5.
North approach (8,1,0) climbs five steps z=1..5 to feet y=6. West bank path
crosses to the east checkpoint/shack (27..35,25..34), then to the stone face
(28..36,8..10). East descent at x=24..26,z=26..30 leads to the lower ravine
path (23,1,31) and under-bridge point (23,1,19). One chest at (31,6,32).
Bandit anchors (12.5,6,19.5),(29.5,6,23.5), archer (33.5,6,30.5).
No Cullis or functional Demon Door. Explicit ordinary gold/food/potion loot.

[C] architecture.md Greatwood and FullWorld §6 supply gorge/bridge, stairs,
bandit checkpoint and Arboretum Demon Door. Dimensions, dry ravine, palette,
orientation and compressed scatter footprint are [B]. The face is a static
landmark: no Arboretum challenge/reward, generic riddle substitution, toll fee,
leader surrender/fleeing or quest completion. Existing regions remain unchanged;
new weights change future unvisited-region rolls. No fixed map or retrofit.

## Verification and remaining checks

Six groups check all emitted writes/palette and scatter dimensions/flags; every
bridge plank/rail and under-span clearance; north-entry routes to the shack,
chest, face approach and lower ravine; exact orientations/headroom of both stair
flights; actual bandit/archer spawn and ordinary chest table; grass/rock scatter
and region idempotence. Independent missing-plank, sealed-shack and obstructed
stair fixtures fail the relevant tests. Floodfill permits full one-block steps,
so partial-block/fence collision and jump-free traversal require engine checks.

The inspected [TLC Bandit Toll guide image](https://www.gamepressure.com/fablethelostchapters/gfx/word/1215502812.jpg)
shows a wooded toll approach with rough timber and masonry. It supplies material
context only: bridge, gorge floor and face are outside the frame. Our exposed
straight-sided ravine, sparse trees, regular shack and slab-like static face
remain visual gaps. No whole-POI visual grade is assigned without suitable
reference views. Reference provenance/hash is recorded under W3.4; external
bitmaps stay in ignored scratch. Generated exterior/rear/top views are offline.

Raw /structure load places blocks only. Scatter initializes mobs and ordinary
loot; no fc:place handler exists. There is no forced fall or hazardous block on
the tested entry route. Hostile bandits and possible combat knockback remain
engine concerns; the test does not claim a combat-safe encounter.

- [ ] New world: natural grass and rock scatter, terrain grading and edge seams.
- [ ] Walk both stairs and bridge without jumping; test rail/fence collisions.
- [ ] Reach/open populated chest and inspect all three spawned bandits.
- [ ] Descend, walk under bridge, climb back, and return to the north ground edge.
- [ ] Inspect face/shack/foliage lighting and full original-TLC reference views.
- [ ] Existing regions remain intact; new region population is not duplicated.
- [ ] Test combat/multiplayer retreat and knockback near the ravine rails.

Every engine check remains unrun; W3.4 is in-progress.

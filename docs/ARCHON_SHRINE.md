# Archon Shrine and Bronze Gate — W3.2

Planned before implementation: owner `archon_shrine`, ID `fc:archon_shrine`,
49×24×57, weight 4, snow/rock, snow theme; loot archon_shrine, no mobs or Demon
Door, Cullis enabled. Foundation local y=0 matches procedural scatter.

Shrine center (24,14), radius 10, floor y=2, dome spring y=9/crown y=19.
North entry (24,1,0) climbs two steps at z=3/4 to feet y=3. Soul sockets are
(20,2,14), (24,2,14), (28,2,14); ordinary chests (18,3,17)/(30,3,17).
Return outside to the west or east lane and level Cullis arrival (24,1,28),
then follow the central avenue to the sealed Bronze Gate at z=47..49.
Gate frame x=13..35, crown y=22; sealed leaves x=17..31,y=1..17 with a circular bronze mechanism centered
(24,11,45), radius 9. The circular face follows the inspected TLC guide shot.

[C] architecture.md Northern Wastes and FullWorld §12 supply the domed shrine,
three soul stones, nearby Cullis and monumental gate. Dimensions, palette,
orientation and the compressed shared footprint are [B] scatter adaptation.
The sockets and gate are landmarks only: no soul collection/consumption,
quest progression, opening animation, or onward travel to Archon Folly yet.
Existing region flags and saved structures are preserved; the extra weight
changes future unvisited-region rolls. Raw /structure load places blocks only;
scatter owns chest filling and Cullis registration. No fc:place handler exists.


## Verification and remaining checks

Seven automated groups cover palette/bounds, dimensions and scatter flags, three
sockets/dome/stairs, routes to both chests/Cullis/gate, the sealed gate, actual
Cullis detector with missing-core/ring/unloaded negatives, actual snow/rock
scatter and saved-region idempotence, plus blocked-entry/arrival negative fixtures.
The route model allows one-block steps and tests headroom; engine collision and
jump-free stair movement remain unproven. Ordinary chest tables contain Will
potions and gold; these are not claimed as canonical special rewards. The Cullis
label currently uses the existing ID-derived fallback `archon shrine`.

The inspected [TLC guide gate image](https://www.gamepressure.com/fablethelostchapters/gfx/word/1214258421.jpg)
shows a circular bronze mechanism and elaborate projecting ornament. Our revised
circular face approximates that shape, but omits the sculpted creatures and uses
a plain rectangular stone frame. Full dome/exterior reference comparison remains
pending. See screenshots/validation/W3.2/reference-candidates.json for hashes and
provenance limits; external images remain ignored developer scratch.

- [ ] New world: find natural placements on snow and rock; check graded edges.
- [ ] Walk both shrine steps without jumping; inspect doorway, dome and lighting.
- [ ] Reach all three sockets and open both populated chests.
- [ ] Discover/dwell/travel out and back to the center disc; verify safe arrival.
- [ ] Walk to the sealed gate and return; inspect actual copper palette/states.
- [ ] Existing world: old regions unchanged, new region discovery/travel persists.
- [ ] Compare full shrine/gate silhouette against verified original 2005 TLC shots.

No engine item above has been run. W3.2 remains in-progress.

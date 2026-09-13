# Independent decoded Guild review

Run `python screenshots/validation/GP21/independent-review.py --render` from the
repository root. The helper reuses the retained GP20 independent NBT decoder;
it executes the actual committed DP7 generator and actual current generator,
serializes each only under ignored `tmp/conformance/gp21-geometry/owners/`,
and compares both outputs byte-for-byte with their corresponding Guild assets.
No disabled helper substitutes for the actual predecessor.

The geometry baseline is DP7 `e13127194b8bd596bf9db9fee03633a413825f24`.
The intervening DP8 return-controller work does not alter Guild geometry.
Exact source, asset, decoder, route-model, callback and render hashes are in
`independent-review-results.json`; raw stdout/stderr is retained in
`independent-review.log`.

The complete decoded comparison finds exactly ten air-to-spruce-fence cells:
`x80..81` and `x85..92`, `y1`, `z38`. All other 395,270 campus cells remain exact.
The existing palette, block states, block metadata, secondary layer, entities,
origin, dimensions, layout/anchors and seeded RNG stream calls/final states remain
unchanged. This preserves every target, dummy, hay support, ground cell, board,
door, roof, bridge and resident mark. All 678 independently surveyed Maze cells
remain exact. The sole full-campus fletching table is still `(91,1,40)`.

The conservative walking graph contains 13,822 nodes before and 13,812 after.
Only the ten newly occupied rail cells are removed. Every other node and every
other gate-reachable node remain. All seven independently searched complete
gate routes retain the exact same coordinate sequences: both south room doors,
the Skill mark, east junction, both Might marks and Will mark. Eight explicit
local routes pass in both directions: both river bridges, the complete board
bypass, both outer range bypasses, the future short Skill arrival corridor,
the firing-gap centerline and the range's rear crossing. All three gap columns
`x82..84` remain clear and supported through `z37..40`.

The actual production Skill harness passes on both decoded assets, including
ten changed/unavailable-geometry refusals and 29 crossed-cell negatives. The
retained arrival prototype passes all 13 quarter-block corridor samples and 27
predicate refusals on both assets. That prototype still mocks 624 below-base
cells as readable air; it does not calibrate native search, arrival, offsets or
saved-world contents.

`ray-collision-probe.mjs` executes the actual shot callback and reconstructs its
line origin from its six emitted particles for each of five tolerated actor
offsets. The independent Python sweep tests 10,001 points on each actual line,
including occupancy from the block below each point. Its conservative model
treats fences/walls as full columns extending 1.5 blocks upward. Both assets
remain clear for every line. The model deliberately overestimates fence width;
it is separate from native shape, projectile and movement execution.

Six injected failures are detected by the exact local-route fixtures: removed
bridge deck, removed bridge approach slab, blocked bridge headroom, blocked
arrival corridor, blocked board bypass and closed firing gap. A seventh probe
inserts a fence at `(83,1,38)`: the expanded collision sweep detects the overlap
even though the existing block-cell ray harness still passes because its line
samples read air at `y2`. This records a checker boundary and prevents accepting
a continuous cross-firing fence on the strength of that harness alone. The final
three-column gap avoids the overlap at every tested tolerated displacement.

The six PNGs are decoded before/after views from the south, north and directly
above. They retain all cells in `x77..94,y0..7,z29..46`; surrounding architecture
is intentionally clipped. Fence posts and paired connected horizontal members
are drawn as thin approximate boxes, slabs at half height and carpets thin;
other props use full cubes and all materials use flat approximate colors.
These are authored-geometry schematics, with no original-game pixels, native
textures, target artwork, lighting, player-width simulation or engine execution.
Original rail features and the chosen block adaptation are evaluated separately
in the reference evidence. Native collision, movement, two-Hero passing,
lighting and saved-world acceptance remain unrun.

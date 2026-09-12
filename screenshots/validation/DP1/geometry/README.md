# DP1 source and destination geometry evidence

This directory records generated geometry and offline inspection. It does not
claim a Bedrock playtest or an exact visual match to the 2005 destination.

The Guild anchor remains `(66, 96)` in a `122 × 30 × 108` structure. The source
tunnel clears all 108 cells at x65–67, y1–4, z96–104 and lays cobblestone under
all 27 columns. The supported soul lanterns now stand at x63/69, y3, z95, outside
the passage. Front and rear routes are checked in both directions; the rear
route turns sideways at z104 before the existing perimeter wall.

- `guild-throat-front.png`: the open passage and separate lamp posts are visible.
- `guild-throat-rear.png`: the perimeter wall obscures the low rear mouth in this
  exterior view. It is contextual evidence; the exact voxel check establishes
  clearance through the exit and the adjacent z104 approach.
- `arcanum-library-view.png`: the generated library grove contains a central
  approach, reading places, trees, pond and surrounding crags. Bookshelves are
  partially hidden by foliage from this camera. Barrier blocks are omitted by
  the renderer while remaining in the actual asset.

`source-tests.log` records five passing groups: complete source volume and
approaches, independent obstruction/floor-hole rejection, fixed destination
registration, invisible-barrier rendering and migration of a frozen GP1 source.
The migration test runs the actual JavaScript aperture module against 135 cells
captured from commit `1ec9286f0859b3be38921594053877a861d779f4`, including all 27
floor cells. Its fixture is `scripts/tests/fixtures/guild_door_gp1.json`. The
runtime clears only the old non-air throat cells, preserves every old floor
material and reaches the same clear throat as the new generator. Existing floors
are deliberately preserved; fresh structures use continuous cobblestone.
`aperture-compatibility.log` independently compares the frozen 108-cell material
fingerprint with that old generator. Neither check changes any saved world.

`generation.log` records targeted generation of `guild_hall` and
`library_arcanum`. `room-tests.log`, `guild-circulation-tests.log` and
`behavior-before.log` record the room, existing Guild circulation and behavior
regressions run before generation.

`contract-renders.log` records all 35 declared C2 renders. The contract now
contains 28 scatter structures, 3 fixed destinations and 4 legacy structures.
`structure-contract.json` reports zero errors; `structure-manifest-tests.log`
records all 15 negative/positive contract tests passing. The full structure card
pipeline now includes 32 cards. Only the Guild and Library cards were generated
in this pass; the root task coordinates the full all-category pipeline.

The current contract audit's S/100 image score for Library Arcanum measures
render appearance only. Its canonical feature contract and remaining in-game
acceptance work are documented in `docs/DEMON_DOOR_DESIGN.md`.

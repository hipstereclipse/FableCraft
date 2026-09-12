# GP2 Guild circulation pass

This pass makes the existing lobby, gallery, dining dormitory and Maze study
reachable through continuous stairs in newly generated Guilds. GP1 found valid
standing anchors behind disconnected geometry: the tower's rounded tread samples
left gaps and its inner rails replaced seventeen intended treads; later room
passes removed the gallery bridge and its dining threshold.

`guild_circulation_routes()` in `scripts/gen_structures.py` now defines explicit
walking surfaces, including two-wide flights, flat turns and half-block rises.
`build_guild_circulation()` owns the bounded stair/landing/doorway volumes after
adjoining architectural shells have been constructed. The previous sparse tower
stair and overlapping rail installation, old wrapped lobby treads and earlier
bridge installation have been removed. This is generator construction, with no
new runtime geometry repair or periodic sweep.

The two lobby flights meet at the existing gallery elevation. The bridge descends
from feet y10 through half-block steps to the dining floor at y8, with a supported
three-wide doorway. A bunk previously crossing that doorway is omitted; the other
bunks remain. The tower follows connected stone flights and corner landings up to
Maze's study, with positive connections into the middle floor and study. A short
inner study landing reaches the existing `(46,12,70)` anchor. Three-wide ground
arches beneath the lobby crossings retain two blocks of standing clearance.

## Scope and reference basis

The GP1 audit's documented map/library/dining/shop/tower adjacency remains the
reference basis. This pass restores functional circulation through those spaces;
it does not establish exact 2005 TLC staircase proportions. The squared landings
and half-block treads are Minecraft adaptations. All original-game room-count,
roof, Will-island/bridge-count and furnishing questions listed in
`GUILD_GEOMETRY_AUDIT.md` remain open.

The exterior render retains the established tower, roof masses, grounds, bridges
and training layout. The labeled circulation cutaways show a continuous pair of
lobby stairs and a tower flight instead of separated treads. These views hide
architectural shells to expose the route; they are not normal gameplay views.
The ordinary hall/tower cutaways and exterior were also generated for context.

## Verification that actually ran

- `python scripts/tests/test_gen_behavior.py` passed four regression groups before
  structure regeneration. No behavior or resource generation was performed here.
- `python scripts/tests/test_guild_routes.py` passed six groups against final
  generator voxels. The geometry model checks actual full-block and half-slab
  vertical collision intervals, two blocks of headroom, cardinal adjacency,
  swept departure/arrival headroom and at most a half-block rise in either
  direction. It finds gate-to-gallery, gate-to-dining-dormitory and gate-to-Maze
  paths and verifies return paths separately.
- Independent surveyed point sequences cover both lobby flights and flat turns,
  every tower turn, floor landings and the three-wide gallery bridge. Adjacent
  ground routes include map/quest approaches, both nooks, library, shop, dining,
  cloister, tower doors, training and Demon Door approach. Maze coordinates and
  the 122×30×108 footprint remain unchanged.
- Three independent damage fixtures remove both lanes of a tower tread, obstruct
  tower headroom, and remove the gallery bridge. Each is rejected for the
  corresponding missing-surface or blocked-volume reason.
- Four new circulation groups were also run against the **actual GP1 generator**
  read from commit `1ec9286f0859b3be38921594053877a861d779f4`. They produced six
  expected failed assertions with no test errors. This demonstrates that the
  regression catches the prior implementation rather than merely accepting its
  own new coordinate table.
- The updated `_verify_guild.py` tower diagnostic checks the new final tread
  reservations: zero missing surfaces, zero blocked headroom and zero blocked
  west/north entrance columns. Its older trigonometric samples are retired.
  Independent route testing remains in `test_guild_routes.py`.
- Only `guild_hall()` was invoked for the targeted asset regeneration. The parent
  checkpoint records whole-project validation and contract-render results.

Evidence is under `screenshots/validation/GP2/geometry/`: `routes.log`,
`baseline-regression.log`, `behavior-before.log`, `tower-diagnostic.log`, the
render script/log and image hashes in `views.json`. `new_exterior.png`,
`new_hall_cutaway.png`, `new_tower_cutaway.png`, `lobby_circulation_cutaway.png`
and `tower_circulation_cutaway.png` are offline renders. The exterior and both
circulation detail views were visually inspected after generation.

## Compatibility and remaining acceptance

No `GUILD_LAYOUT` or runtime `GUILD` anchor changes, ticking-area changes,
terrain/cave-exclusion changes, reanchor changes, progress resets or saved-world
migration are included. Fresh placement receives this geometry. An existing
occupied Guild is not automatically overwritten; its old stairs remain until a
separate bounded migration is designed and validated. Raw structure loading is
not an authorized migration path for an occupied Guild.

The test collision model treats carpets and listed plants as passable and does
not simulate Bedrock stair collision, dynamic block updates, NPC navigation or
multiplayer interactions. New routes use half slabs/full blocks, but actual
jump-free movement remains **unrun in-engine**. Two-wide stairs make room for
navigation; no NPC route-execution claim follows from that geometry alone.

Required manual follow-up: walk both lobby flights in both directions; cross the
gallery bridge without jumping; enter the dining dormitory and return; walk both
tower ground entrances and the complete tower flight to Maze; inspect the middle
floor/cloister link and the study landing; repeat with nearby Guild NPCs and a
second player. Check rail/furniture collisions and falls, since this pass removes
the obstructing inner tower fence rail and leaves the circulation edge open.

Next ranked work after the first NPC and Demon Door pilot passes: original-game
room/roof comparisons, readable island Will training and its verified bridge
layout, cave/Chamber assembly, and deliberate furnishings/rails placed outside
these tested walking volumes. The upper cloister's inherited one-block rise to
the tower middle-floor doorway and NE dormitory's older stair geometry are not
certified jump-free by this pass and need the next adjoining-route review.

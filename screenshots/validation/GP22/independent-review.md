# Independent GP22 authored-output review

Run `python screenshots/validation/GP22/independent-review.py --render` from the
repository root. The review executes the actual DP9 generator from
`af73bfb42c3f742454c7cf88c17ad052c3f0cf41` and the actual current generator,
serializing each under ignored `tmp/conformance/gp22-geometry/owners/`. Each
output matches its corresponding shipped Guild NBT byte for byte. The retained
GP20 decoder and GP21 route/ray/render helpers are reused; no disabled-helper
surrogate or candidate-only mutation replaces the authored-output comparison.

Exactly 12 of 395,280 cells change from air to the independently enumerated
cutout blocks. All other 395,268 cells, existing occupied cells, floors, palette,
states, metadata, entities, secondary layers, origin and dimensions remain exact.
The single seeded RNG stream has identical call keys and final state; layout
and anchors are unchanged. This preserves every target, dummy, hay support,
resident mark, roof, door, bridge and approach. All 678 surveyed Maze cells
remain exact, with Maze at `(46,12,70)`. The sole campus fletching table remains
at `(91,1,40)`.

The mountain profile occupies x80..82 at z32, starting at y1 with heights 1/2/1.
The crenellated tower profile occupies x87..89 at z33, also from y1, with heights
3/2/3. Its black cell is a painted-slit cue represented by a full cube. Source
141099874 supports separate low scenic silhouettes ahead of the painted board;
the coordinates, materials, dimensions, steps and depth are Minecraft
adaptations. The accepted source image hash is retained in the JSON report.

Only the six newly occupied ground columns leave the conservative walking graph
(13,812 to 13,806) and gate-reachable set (10,603 to 10,597). Every other node
remains, with all seven independently searched gate paths retaining identical
coordinate sequences. Eight local paths pass in both directions, including
both bridges, the board bypass, outer range bypasses and future arrival route.
All three firing-gap columns x82..84 remain clear through z37..40.

An analytic body sweep checks the 12 added full-cube colliders against 19 paths:
the eight local paths, seven complete gate paths, three gap columns and the
13-sample future arrival corridor. Radius 0.35 and height 1.9 conservatively
exceed the Skill entity's approximately 0.672-wide, 1.824-high collider. No new
collider intersects those sweeps. Preexisting geometry is separately covered by
the retained slab/fence route model; this is not general native navigation.

Both decoded assets pass the actual Skill callback harness, including ten
changed/unavailable-geometry refusals and 29 crossed-cell negatives. Five
retained actor offsets emit the same rays before and after. A separate
10,001-point sweep includes the block below each ray sample and extends fence
and wall collision columns through y+1.5. Every ray remains clear. All cutout
blocks end at z34 or earlier, while the retained ray target is z34.5. The arrival
prototype retains all 13 corridor samples and 27 predicate refusals.

Nine negative fixtures are detected: missing bridge deck, missing approach
slab, blocked bridge headroom, blocked arrival corridor, blocked board bypass,
closed firing gap, lower-fence ray overhang, a body sweep through a blocked bay,
and an additional forward tower overlapping the east-door path. The last still
leaves every destination reachable but changes the protected route, demonstrating
why reachability alone is insufficient. The lower-fence fixture still passes
the generic block-cell shot harness while failing the expanded collision sweep;
the retained three-column opening avoids that checker limitation.

The six focused before/after PNGs were visually inspected. They show the two
new profiles at distinct depths while preserving the board, targets, floor and
divider. The south view reads as a low mountain silhouette and a separate
crenellated tower cue; the reverse view and plan expose the clear z31 board
bypass and retained target spacing. These are actual decoded-owner schematics
with approximate material colors and thin approximate fence members, not
original pixels or native textures/lighting. Rejected speculative pictures
remain ignored and are absent from this evidence directory.

The full raw output is in `independent-review.log`; exact source, output, reader,
route, callback, font and image hashes are in `independent-summary.json`.
Native walking, collision, lighting, two-Hero passing and saved-world acceptance
remain unrun. Decorative terracotta/wool tops are not certified walking floors
by this graph. The arrival prototype still mocks 624 below-base cells as readable
air, so native search, offset/event semantics and saved-world contents remain
unresolved. Broader render and pack gates belong to the milestone's main review.

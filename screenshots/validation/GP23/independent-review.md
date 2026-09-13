# Independent GP23 final geometry review

The actual DP10 Guild generator and actual final GP23 generator each reproduce
their corresponding serialized pack asset exactly. The comparison uses committed
DP10 `5fcf08a23389760762438c86092a8d3450f96195`, not an in-memory candidate with a
disabled helper. Both full generators execute unchanged into ignored scratch;
no pack or production source is written by this review.

Exactly 16 of 395,280 cells differ: at all eight existing lamp positions
`x58/68,z35/37/53/55`, y2 changes from standing lantern to dark-oak fence and y3
changes from air to the same standing-lantern state. All other 395,264 cells,
palette entries/states, secondary layers, entities, metadata, origin and size
remain exact. Every y0/y1 cell, all eight lower posts, 28 bridge rails and 981
water cells remain exact. The one observed RNG stream, its keys/final state,
all layout/anchors and all 678 protected Maze cells remain exact. Maze remains
at `(46,12,70)`.

All 13,806 walking nodes and 10,597 gate-reachable nodes retain their coordinates.
Seven complete gate-to-destination paths are identical. Eight local routes,
including both full bridge centerlines, pass forward and backward; all three
firing-gap columns remain clear. The actual Skill-ray, block-voxel shot and
future-arrival harness outputs are identical: five emitted rays, 13 proposed
arrival samples and 27 deliberate arrival refusals. No training, target, hay,
range scenery, source aperture or saved construction changed.

Nineteen retained body paths and ten additional bridge paths with lateral offsets
from -0.15 through +0.15 have no collision with the changed columns in either
version. These analytic segment/AABB sweeps use body radius 0.35 and height 1.9,
full horizontal fence columns extending to y+1.5 and full-cube lantern bounds.
The actual Skill collider fits those body dimensions. Both versions reject the
same four deliberate ±0.16 bridge offset paths under that conservative model.
This is a bound on the existing one-column passage, not a measurement of native
fence thickness or a certification of its physical lateral clearance.

Ten negative fixtures are detected: missing deck, missing slab approach, blocked
headroom and a centerline fence on each bridge; the retained lower firing-fence
ray overhang; and the preexisting post-column lateral limit. The ray-overhang
fixture still passes the older block-cell shot harness, demonstrating why the
additional shape bound remains necessary. The author separately checks complete
final bridge geometry using explicit half-step body transitions; this independent
review's changed-column sweeps do not replace native movement/collision tests.

Eight focused before/after decoded PNGs show both bridges from side and approach
angles. They use the same scale and camera bounds, including invisible common
framing bounds so raising a lamp cannot recenter the deck. Visual fence members,
lanterns and colors are simplified. The views show longer dark shafts and raised
lamp heads, with the crossings and thin existing rails preserved. All eight views
were inspected together; the full-size final approach views were also inspected.

Original TLC images `131726186` and `91147839` were re-inspected and their retained
hashes checked. They support a separate tall dark lamp beside the decorated bridge
end. They do not establish eight positions, block height, dark-oak material,
lantern shape or exact bridge dimensions. Those remain Minecraft adaptations.
Opaque ornamented parapets, rising profiles, capped ends, deck width and native
lighting remain open. The full reference provenance belongs to this milestone's
reference index and the retained GP16/GP22 records; no external pixels are added
to this evidence directory.

Run `python screenshots/validation/GP23/independent-review.py --render` to repeat
the actual-owner comparison and focused renders. `independent-summary.json`
records all changes, routes, checks, raw source/asset/dependency hashes and final
image hashes. The initial serializer-dependency check stopped on inherited CRLF
noise; the first output is retained. The corrected check ignores only CRLF while
recording both raw hashes, and the exact old/current generated-asset comparisons
still pass. A later image-only framing correction separates captions from the
approach plate; the earlier successful log and ignored images remain retained.
See `independent-helper-corrections.md` for exact correction scope.

No blocking geometry defect was found in this bounded pass. No native engine,
lighting, collision, movement or saved-world placement acceptance ran. This
review does not close whole-bridge or whole-Guild conformance.

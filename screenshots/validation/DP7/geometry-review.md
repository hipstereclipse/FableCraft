# DP7 geometry implementation and visual review

The new Arboretum is an original 49x28x49 contained woodland, with nine substantial
rooted trees, overlapping high crowns, a dry loop around the planted mass, a
short chest branch and a separate timber return frame. Exactly one empty chest
at `(34,3,35)` is provided for the runtime's Wellow's Pickhammer reward. There
is no generator-owned inventory, Library bookcase, reading furniture or pond.

Both retained 2005 Prima source/interior images were actually inspected before
implementation. They support a shaded wooded destination and substantial trunks;
the tiny curved foreground objects remain unidentified. Root forms, tree count,
loop shape, materials, lighting blocks, dimensions and exact placement are
original Minecraft adaptations. The source images and their edition/size/hash
limitations remain in GP20's Arboretum follow-up and ignored scratch. No external
pixels are copied into this evidence or the packs.

The room/source contracts are explicit in `scripts/door_realms.py`: `ARBORETUM`
and `GORGE_ARBORETUM_SOURCE`. Arrival is `(24.5,3,7.5)`, return `(24.5,3,3.5)`,
and chest front `(34.5,3,34.5)`. The loop has 11 listed points including its
repeated start; the final complete spine/branch/path reservation contains 309
columns with solid support and four clear blocks above. The chest stays outside
the main loop's three-wide shoulder. The generated runtime's actual room/source
constants, markers, waypoint arrays and branch match the Python owner.

The new-placement Gorge passage clears `x31..33,y6..9,z7..11`, changing exactly
43 previously occupied cells. Actual committed GP20 and current owners were
compared over all 26,832 cells, and each serialized output matches its own asset.
Every cell outside those 43 stays exact, including the grass support plane,
bridge, bank, underpass, chest, source lintel, approach stairs and trees. RNG keys
and final states match. The source's three-wide front and back approaches at
`z6..12` retain floor y5 and clear feet/headroom y6..9. This generator does not
reload an existing world or authorize enrollment of an old static Gorge.

The required eight behavior groups passed before targeted generation. The
whole-pack hash snapshot proves exactly two output changes among 1661→1662 files:
the changed Gorge and new Arboretum. Library Arcanum was independently rebuilt
only to ignored scratch and remains byte-identical to its shipped asset.

- Arboretum: `678c15573abf29e17f52c4edfb09cdc58b89f138d3172ba2d4667eb9827fd23c`
- Gorge: `77f2f37c610a5d7618a53c8785ef29aebe7e8cb866c4f56376d6ba973f69e7d5`
- Unchanged Library: `5e296dd3f30916a064181beb32f5e59692f830611449b7c920031caede9ab7c7`

Nine Arboretum groups pass, including actual canonical DATA versus Python owner,
runtime geometry, fixed registration, manifest and full-renderer coupling.
The five Library geometry groups and all nine Gorge groups pass. The existing
population group required root to update its isolated fixture for the new
`arboretumDoors` dependency; its successful rerun and initial failure are both
retained separately. Independent blocked-lane,
missing-floor, blocked-chest-lid, broken-side-shell/top-shell and source
obstruction/support probes all fail as intended.

All six focused views were inspected: topology, entry, chest, return and the
actual before/after Gorge source. The topology makes both arcs and chest branch
legible; the eye-level views show the substantial trunks, unobstructed chest
front and return frame. `render-geometry.py` reproduces the evidence and exact
scope JSON without mutating packs. The topology omits crowns above y7; its line
overlay is review-only. The perspective views use exact grid ray traversal but
opaque cube foliage/furniture, approximate colors and simple shading/fog. Source
cutaways use full cubes. They do not render native textures, animated faces,
lighting, inventory collection or collision execution.

This is the implementation author's geometry/visual review. Root independently
inspected the same six views and owns full snapshot/C2 validation; the separate
runtime remains subject to independent persistence/integration review. Native
opening, traversal, collection, exact-source return, reload/death and two-Hero
acceptance remain unrun. The small reference does not establish whole-room
conformance or the original witnessed-murder solution.

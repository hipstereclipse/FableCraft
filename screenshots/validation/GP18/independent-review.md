# GP18 independent Maze study review

Disposition: **no blocking finding** in the bounded production change, final
serialized output or reviewed reference/render claims. Native acceptance remains
unrun.

## Reference pixels and claims

The reviewer opened both downloaded original-TLC images, rather than relying on
the prior survey's captions. The primary pixel sources and confidence/patch
limits are retained in the GP17 Maze survey and repeated in the
[GP18 render scope](maze-study-render-scope.json).

- [Steam image 273468136](https://steamcommunity.com/sharedfiles/filedetails/?id=273468136)
  visibly shows a red rug with a patterned border and tall, adjoining bookcase
  sections with a timber frame. It also shows the round lattice window, high
  chair back and part of a pedestal table.
- [Steam image 247737302](https://steamcommunity.com/sharedfiles/filedetails/?id=247737302)
  corroborates the round window and timber-framed red wall panels, with a rail
  beside a level change. It does not independently establish the full bookcase
  or room arrangement.

Red carpet and contiguous shelves have direct visual support. The three small
carpet patches do not reproduce the rug's extent or decorative border. The
southwest two-column, four-block case with plain dark-oak base/cap is an explicit
Minecraft adaptation. The two views do not authorize an inferred gallery plan,
window reconstruction, hidden furniture counts, a bed over the retained stairs,
or changes to the room's circulation. No exact proportions or calibrated light
levels are claimed.

## Scope and production review

`build_guild_maze_study` runs after the complete Guild circulation, decor and
archery passes. It writes the three surveyed carpet cells and eight supported
case cells. It does not use randomness or runtime state. All placement comes
from the generator; there is no runtime repair or saved-world rebuild.

The exact permitted set is:

| Cells | Result |
| --- | --- |
| `(45,12,71)`, `(45,12,73)`, `(47,12,73)` | Red carpet replacing blue carpet |
| `x43..44, y12 and y15, z75` | Dark-oak base/cap replacing air |
| `x43..44, y13..14, z75` | Bookshelves replacing air |

The source test suite inspects the final complete owner output, checks support,
carpet/landing clearance, 678 frozen protected cells, window glass, case fronts,
complete two-way tower/connector routes and RNG state. It also introduces
missing support, broken case, blocked front/headroom, changed carpet/window,
broken route, forbidden bed and stray RNG failures to verify rejection.

## Independent serialized-output check

The separate [review probe](independent_review_probe.py) builds the actual
committed predecessor generator and current generator into ignored temporary
directories. It independently decodes the emitted little-endian NBT, compares
all 395,280 named/stateful voxels, and checks the exact eleven-cell result. The
baseline is actual source from DP5 commit
`732670a83bcd7909858ca4480c31f5dc8aeeb8ad`; the generator remains identical through
GP17. This comparison does not disable the new helper to construct its baseline.

Both final commands exited **0**:

```sh
python screenshots/validation/GP18/independent_review_probe.py --require-shipped-match
python scripts/tests/test_guild_maze_study.py
```

[Independent results](independent-review-results.json) establish exactly eleven
changed cells among 395,280, all 678 protected cells and 35 glass cells preserved,
identical layout/anchor values and seeded RNG calls/final state, and unchanged
palette, secondary block layer, entity data and origin. Full tower/connector
routes pass in both directions. The only two formerly reachable nodes removed
are the intended case footprints `(43,12,75)` and `(44,12,75)`. The current
serialized owner output matches the shipped Guild byte for byte at SHA-256
`a92f2c2ac76f1923b87f8c673a586d6427bb9a32a01dc5c83b7ab9f2091180e8`.
The independently repeated focused suite passes all seven groups in
[independent-maze-tests.log](independent-maze-tests.log).

All six focused before/after images were opened. The empty southwest pocket
becomes the intended tall case, the carpet changes from blue to red, and the
retained room openings/central fixtures remain legible. The images explicitly
omit clipped geometry and use approximate flat material colors: bookshelf cubes
show volume, not native book textures. The implementation owner clarified the before-case caption and changed the
plan's “original approach” wording to “existing approach.” The final
[implementation contract](../../../docs/GUILD_MAZE_STUDY.md) correctly separates
the visible rug/shelf references from the selected Minecraft footprint,
dimensions, retained windows and incomplete room/gallery fidelity.

Native carpet collision, furniture rendering and lighting, physical turning,
NPC navigation and save/reload remain **unrun**. Offline collision uses the
existing conservative full-block/half-step model. A passing route graph and
cropped render do not establish original-TLC fidelity or native playability.

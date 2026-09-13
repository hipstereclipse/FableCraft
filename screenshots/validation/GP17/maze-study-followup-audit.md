# GP17 read-only Maze study fixture survey

Date: 2026-09-12. The final owner-built Guild was serialized into a temporary
directory and matched the shipped `guild_hall.mcstructure` byte for byte. The
survey covers 1,575 cells at `x39..53, y11..17, z65..79`, centered on the tower at
`(46,72)`. Maze's standing anchor remains `(46,12,70)`.

Exact source hashes, surviving fixtures, window cells, supported pockets, proposed
cell changes and 678 protected cells are recorded in
[maze-study-final-voxel-survey.json](maze-study-final-voxel-survey.json).
This preparatory comparison stays behind requester-specific activity ownership.
No production source, generated asset, saved world or index was changed.

## Final geometry corrects the earlier source-only comparison

The two known original-TLC Maze views show a red bordered rug, continuous tall
framed bookcase, round window with diagonal lattice, high-backed chair and partial
pedestal table. The second angle shows timber-framed red wall panels and a rail at
a level change. Their image URLs/hashes remain in GP15 provenance and are repeated
in the survey JSON. Neither image establishes the complete floor/gallery plan,
furniture count, exact dimensions or calibrated light levels.

| Fixture | Actual surviving upper-study cells |
| --- | --- |
| Blue carpet | Exactly three: `(45,12,71)`, `(45,12,73)`, `(47,12,73)`. Each has dark oak deck immediately below and air above. |
| Bookshelf | **Zero** in the surveyed upper study. The nominal stack at `(49,12,73)` and `(49,13,73)` is skipped because the builder excludes all stair x/z columns, including lower flights. Both final cells are air over a supported deck. |
| Red bed | **Zero**. The nominal halves at `(45,12,69)` and `(46,12,69)` are erased by final circulation clearance; their `y11` cells are also air over the stair opening. Restoring a bed there would conflict with the retained stair volume. |
| Lectern | `(44,12,73)`, facing east, supported on dark oak. |
| Enchanting table | `(48,12,72)`, supported on dark oak. This remains an unverified block adaptation. |
| Central newel/lights | Newel at `x46,z72` through `y13`, including a sea lantern at `y12`; sea lantern at `(46,14,72)` supporting a standing lantern at `(46,15,72)` with final state `hanging:false`. A separate sea lantern survives at `(47,12,74)`. |
| Upper windows | Five pointed bays, with 35 surviving `minecraft:glass_pane` cells across `y13..15`, and five sea-lantern tips at `y16`. The final wall materials are stone bricks, smooth stone and chiseled stone bricks after the Guild's local material aliases. |

The fourth source-authored carpet at `(47,12,71)` is also erased by the final
study landing clearance. These differences explain why reading the earlier
furnishing statements alone overstates what the final room contains.

## Smallest supported follow-up

The smallest source-supported change is to recolor the three existing blue carpet
cells red. It changes no support, air/solid location or carpet footprint. The
remaining sparse patches and absent border remain explicit adaptations.

A small coherent furnishing pass can additionally use the southwest pocket at
`x43..44, z75, y12..15`. All eight cells are currently air, both columns stand on
the existing dark oak deck at `y11`, and masonry behind this pocket supplies a
wall backdrop without covering a window. A two-column case can use a continuous
dark oak base at `y12`, four bookshelf cells at `y13..14`, and a dark oak cap at
`y15`. Combined with the carpet recolors, this is an **11-cell** candidate:

| Exact editable set | Proposed material |
| --- | --- |
| `(45,12,71)`, `(45,12,73)`, `(47,12,73)` | `minecraft:red_carpet` |
| `(43,12,75)`, `(44,12,75)`, `(43,15,75)`, `(44,15,75)` | `minecraft:dark_oak_planks` |
| `(43,13,75)`, `(44,13,75)`, `(43,14,75)`, `(44,14,75)` | `minecraft:bookshelf` |

The source supports red carpet and continuous timber-framed shelving. This
two-block width, four-block height, southwest placement and simple base/cap are
chosen Minecraft dimensions. They do not reproduce the source's carved trim or
establish an upper gallery. Keep the lectern, apparatus, lights and existing room
topology outside this candidate's edit set. A later implementation should use a
bounded final fixture helper with no RNG calls, preserving all other campus cells
and the shared RNG sequence.

The southwest pocket is preferable to the three-column west pocket at
`x42,z71..73`: the latter is supported and empty but stands directly in front of
the west window. Other free supported columns are enumerated in JSON; inclusion
there establishes empty space/support only, not permission to fill every pocket.

## Protected circulation and copied-only experiment

The JSON's 678 unique protected cells preserve the full two-wide authored tower
stair reservations, their carriage/headroom, both middle landings, final study
landing, the entire surveyed `y11` deck/opening plane, Maze's support/headroom,
central newel/lights, ground north/west entrances and upper door approaches.

Upper approaches explicitly retained are the nine-cell east strip
`x50..52,z71..73` at feet `y12`, the twelve-cell south strip `x45..47,z75..78`,
and a seven-point northeast balcony return strip. Surveyed connector routes from
Maze to all three avoid the proposed furniture/carpet edit cells. Their exact
coordinates and baseline block states are in JSON; these are conservative route
reservations for review, not a measured original-TLC floor plan.

The 11-cell candidate was applied only to an in-memory copy of the final Guild.
Full-campus comparison found exactly those 11 changes, and all 678 protected
cells stayed exact. The existing independent complete tower route assertion
passed in both directions. The gate, Maze's ground anchor, middle landing and all
28 upper-approach points remained reachable from Maze's study. The only previously
reachable graph nodes removed were the two intended case footprint points,
`(43,12,75)` and `(44,12,75)`; no additional route area became disconnected.

The six existing `scripts/tests/test_guild_routes.py` groups also passed against
the unchanged production builder. These checks use the existing conservative
half-step collision model; carpet is treated as passable and full furniture as
solid. Native turning, carpet collision, NPC navigation, lighting and physical
walking remain **unrun**. The copied candidate was not saved into the pack.

## Window and larger furniture work remains queued

The west plane `x41,y12..16,z70..74` and north plane
`z67,y12..16,x44..48` each provide an exact 25-cell existing window/trim survey.
The round source window is a clear visual difference, but converting the current
five-high bays needs a deliberate coarse round/lattice design and sightline
review. No window replacement is included in the 11-cell candidate. The furniture
images are insufficient to relocate the stairs, introduce an interior gallery,
determine hidden bed locations, remove unverified apparatus as if absence were
proven, or calibrate the complete room. Existing occupied geometry remains intact.

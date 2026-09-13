# Maze study fixtures — GP18

The Guild's final generated study now has a supported timber bookcase and red
carpet at its three existing carpet cells. The preceding final-voxel survey
found no surviving study shelves: the earlier nominal shelf locations were
excluded by the final stair footprint. Its three surviving carpet blocks were
blue. This pass changes eleven cells in the complete generated Guild.

## Original reference and chosen adaptation

Two inspected screenshots belong to the original **Fable: The Lost Chapters**
Steam application, rather than Anniversary. The
[first view, 273468136](https://steamcommunity.com/sharedfiles/filedetails/?id=273468136),
shows tall adjoining shelves with timber framing beneath a gallery, a red rug
with a patterned border over diamond-pattern stone paving, a round lattice
window, a high chair back and part of a thick pedestal table. Bright equipment
affects the foreground; this image does not establish calibrated room lighting.
The [second view, 247737302](https://steamcommunity.com/sharedfiles/filedetails/?id=247737302),
corroborates the round window, timber-framed red wall panels, a rail beside a
level change and the red rug edge. It does not independently show the bookcase
or establish the full gallery arrangement.

These observations support red carpet and continuous shelving. The retained
three-cell carpet footprint, southwest placement, two-column width, four-block
height, dark-oak material and plain base/cap are Minecraft adaptations. Three
red patches do not reproduce the original rug's size, outline or patterned
border. The source views do not provide a measured room plan or hidden
furniture counts. The downloaded originals were inspected directly and remain
in ignored reference scratch storage; no source pixels enter the pack or
tracked render evidence. URLs, hashes and version limitations are retained in
the [GP17 survey](../screenshots/validation/GP17/maze-study-final-voxel-survey.json)
and [GP18 render scope](../screenshots/validation/GP18/maze-study-render-scope.json).

## Final geometry and protected access

`build_guild_maze_study` runs after the final circulation, floating-decor and
archery passes. Its complete editable set is:

| Local cells | Before | After |
| --- | --- | --- |
| `(45,12,71)`, `(45,12,73)`, `(47,12,73)` | Blue carpet | Red carpet |
| `x43..44, y12 and y15, z75` | Air | Dark-oak base and cap |
| `x43..44, y13..14, z75` | Air | Four contiguous bookshelf blocks |

The case stands on the existing dark-oak deck at y11. Its two front standing
columns at `(43,12,74)` and `(44,12,74)` retain support and headroom. The nominal
fourth carpet position `(47,12,71)` remains landing air. The helper uses no
randomness; complete builds finish with identical shared RNG calls and states.
Every campus cell outside the eleven-cell fixture is unchanged.

The frozen survey's **678 protected cells** remain exact, including the fixed
stairs, landing/deck, newel and central lights, Maze's `(46,12,70)` position and
door approaches. All **35 glass-pane cells** survive unchanged. The central
lantern at `(46,15,72)` remains a standing lantern (`hanging: false`) over its
existing sea-lantern support. The lectern, enchanting table and other existing
lights remain where the final survey found them. No bed is restored over the
stair opening, and the two excluded nominal shelf cells remain clear.

The full two-way tower run and intermediate landing, gate, Maze's ground and
study positions, both case fronts and all 28 surveyed upper-door approach
points remain connected in the offline walking model. The only two formerly
reachable standing nodes removed are the intended case footprints at
`(43,12,75)` and `(44,12,75)`; no new walkable nodes are introduced. Placement is
owned by the structure generator. This change does not rebuild an already
placed Guild or migrate occupied saved-world geometry.

## Verification and evidence

The required behavior regression passed all eight groups **before** targeted
regeneration. The new [focused suite](../scripts/tests/test_guild_maze_study.py)
passes seven groups covering the exact full-campus change set, case support
and continuity, carpet support and reserved landing air, protected cells and
windows, complete routes, and RNG preservation. Independent damaged fixtures
exercise missing deck/base/shelves, blocked case front, incorrect carpet,
removed window, blocked Maze headroom, broken stairs, blocked east door,
forbidden bed placement and unexpected randomness.

The [independent review](../screenshots/validation/GP18/independent-review.md)
also builds the actual preceding committed generator, decodes both serialized
structures and compares all 395,280 voxels. It finds exactly eleven changes,
with unchanged palette, secondary block layer, entity data, origin, layout and
RNG state. It independently repeats the seven focused groups and confirms that
the serialized current owner matches the shipped Guild asset byte for byte.
The [targeted regeneration record](../screenshots/validation/GP18/targeted-generated-drift.json)
confirms that the Guild asset was the only changed pack file.

Six inspected schematic images show the retained room and changed fixture:

| View | Before | After |
| --- | --- | --- |
| Study cutaway | [Before](../screenshots/validation/GP18/study-cutaway-before.png) | [After](../screenshots/validation/GP18/study-cutaway-after.png) |
| Southwest case pocket | [Before](../screenshots/validation/GP18/study-case-before.png) | [After](../screenshots/validation/GP18/study-case-after.png) |
| Upper-deck plan | [Before](../screenshots/validation/GP18/study-plan-before.png) | [After](../screenshots/validation/GP18/study-plan-after.png) |

The [render script](../screenshots/validation/GP18/render-maze-study.py) draws
the final generator voxels with approximate flat colors. Roof geometry is
clipped; the cutaway additionally omits the north wall. Bookshelves use plain
color proxies rather than native book textures. Carpets use one-sixteenth
height and slabs use half-height; other furniture, panes, walls and lamps are
simplified to full cubes. Image hashes, exact view bounds and matching
outside-fixture semantic hashes are recorded in the render scope.

Native rendering, carpet collision, physical turning, NPC navigation, lighting
and save/reload acceptance remain **unrun**. The round window, red wall panels,
gallery proportions, chair and pedestal table, complete bordered rug and the
current unverified enchanting apparatus remain open reference/conformance
work. This fixture pass does not establish complete study or Guild fidelity.

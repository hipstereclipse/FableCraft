# Next Guild bridge audit: tall lamps are feasible; parapets remain open

This is a scratch-only audit of the actual GP22 Guild asset. No production owner,
pack asset, saved-world construction, RNG, anchor or interaction was changed.
The recommended bounded next bridge pass is to raise the **eight existing lamp
heads one block on extended dark posts**. It does not settle the separate broad
parapet, curved/rising profile, inset ornament or capped-end defects.

## Original pixels inspected

All four complete retained images were viewed, and their hashes were verified.
Exact URLs, local paths, hashes and edition-evidence limits are in
`reference-provenance.json`.

- **91147839:** a dark tall lamp stands separately beside the foreground bridge
  end. Both bridges show broad, decorated, continuously opaque parapets.
- **131726186:** the clear foreground right lamp has a long dark shaft rising
  above the substantial capped bridge-end block, with a bright enclosed head.
  This close view is the strongest tall-post evidence.
- **689540613:** the right-hand lamp stands beside the decorated end. The bridge
  sides have broad pale insets, dark curving motifs and round ornament.
- **157299346:** newly inspected daylight deck view supports plank seams and
  broad continuous pale inset parapets with dark ornament. It shows no clear
  lamp and contributes **no** lamp-height or physical-width measurement.

These are accepted original TLC Steam app 204030 images. Capture/post dates and
patch/mod/settings provenance remain unknown. Perspective and character poses
cannot establish metric bridge width or lamp height. Eight lamp positions, stock
dark-oak fence/lantern materials and the one-block rise are explicit Minecraft
adaptations retaining the existing fixture arrangement.

## Actual width and approach survey

`full-width-survey.json` records every block from y0 through y4 for x56..70 and
the nine rows centered on each of z36/z54. It also records supported floor nodes
and clear standing columns at each centerline's height.

- Flat decks: x60..66, y1, z35..37 and z53..55: three rows, surface y2.
- Slab approaches: x59/67, y1, the same three rows: surface y1.5.
- Bank centerlines: x57..58 and x68..69, surface y1.
- Deck rails: all 28 spruce fences, x60..66, y2, z35/37/53/55.
- Bank lamps: all eight x58/68,z35/37/53/55 columns have a dark-oak fence at y1
  and a standing lantern at y2; y3 is air.

The retained full-column collision bound certifies only the one-block middle
lane between rails/posts. It does not measure native Bedrock fence thickness;
the older schematic 1.75-block post gap remains illustrative. Full-cube rail
replacement would make that one-block width physical and remains rejected.

Uniformly widening to a five-row deck with outer full-block rails is also not
ready. The 28 prospective outer y1/y2 cells on z34/38 are empty, but they cover
six current bank walking nodes at x60/65/66. Beneath them are eight water cells,
two stone-brick cells, one moss cell and three grass cells. At z52/56, the 28
prospective targets directly overwrite the existing chiseled bollard and lantern
at (60,1..2,56), and also cover two bank walking nodes at (60,1,52)/(66,1,52).
The underlying row contains eleven water cells, two deepslate cells and one
grass cell. This audit chooses no widening footprint or approach redesign.

## Why stock trapdoors are not the selected treatment

Microsoft's current block listing confirms `direction`, `open_bit` and
`upside_down_bit` on spruce/iron trapdoors; intrinsic-state documentation defines
the direction values and booleans. Neither source supplies the pinned native
trapdoor/fence collision boxes. A state name is not collider evidence.
The official trapdoor article also confirms iron trapdoors respond to redstone;
wooden variants are interactive. A mutable horizontal/vertical barrier is a new
behavior contract, and a one-block-high open panel must not be assumed to retain
the existing fence's 1.5-block barrier. No trapdoor candidate was authored.

A bespoke thin opaque block is another future investigation, but current official
documentation says 24-unit custom collision heights become stable in 1.26.0.
This pack retains min_engine_version 1.21.100 and server API 2.1.0. Do not assume
a newly documented 1.5-block custom collision box works on that target, or quietly
raise the engine target for a decorative bridge pass.

Technical sources (browsed 2026-09-13):

- [Default block listing](https://learn.microsoft.com/en-us/minecraft/creator/reference/content/vanillalistingsreference/blocks?view=minecraft-bedrock-stable)
- [Intrinsic states](https://learn.microsoft.com/en-us/minecraft/creator/reference/content/blockreference/examples/intrinsicblockstateslist?view=minecraft-bedrock-stable)
- [Taking Inventory: Trapdoor](https://www.minecraft.net/es-es/article/taking-inventory-trapdoor)
- [Custom collision component](https://learn.microsoft.com/en-us/minecraft/creator/reference/content/blockreference/examples/blockcomponents/minecraftblock_collision_box?view=minecraft-bedrock-stable)

## Measured lamp candidate

For every existing lamp column x58/68,z35/37/53/55:

1. Replace y2 standing lantern with dark-oak fence.
2. Place the same standing-lantern state at y3.

Exactly **16 cells** change; all other **395,264** cells and the entire palette
and state table remain exact. Existing y1 posts, all 28 deck-rail cells, all
deck/slab/bank/pier/water/training cells and fixture x/z coordinates remain exact.
No occupied Guild is rebuilt by this proposal.

`probe.py` reproduces the audit without writing production files. The walking
graph stays 13,806 nodes; every reached node and all seven complete gate paths
retain their coordinates. Both 13-sample bridge centerlines and eight local
routes pass in both directions. Nineteen analytic body sweeps use radius 0.35
and height 1.9. Every candidate fence is overbounded as its entire horizontal
column through y+1.5, and every lantern as its full cube: zero hits. A deliberate
full-height fence on the z36 centerline is detected by eight segment/path hits.
`feasibility.json` retains all cell deltas, paths, conservative bounds and hashes.

Eight fixed-scale before/after focused PNGs show both bridges from side and
approach views. Fence visual geometry, lamps and colors are simplified; these
are decoded-voxel schematics, not native lighting/collision images. They show
the lamp heads separated vertically from the low rails, with the existing
crossing opening preserved. Parapets are visibly still thin fences.

Before production authoring, use the owner at `scripts/gen_structures.py` around
`plank_bridge` to make this exact deterministic local change, then regenerate
only Guild after required behavior regression. Independently compare the actual
old/new owner outputs, RNG streams, anchors, all 16 cell deltas, serialized asset,
route/body checks and affected render owners. Current scratch output makes no
claim that this final-owner validation or any native engine run has happened.

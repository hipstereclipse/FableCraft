# W1.2 Lychfield crypt

Layout recorded before implementation. [B] Retain fc:graveyard, 25×13×25,
weight 7, grass/dark terrain, dark theme, the three undead spawn types and chest
loot table. Newly placed structures change; saved regions and existing blocks do not.

| Feature | Local coordinates |
| --- | --- |
| South gate / main walk | x=11..13, floor y=0, z=24..8 |
| Nostro crypt | x=7..17, z=1..7; doorway x=11..13, z=7 |
| Central stone sarcophagus | x=12, z=4..5, y=1..2 |
| Side sarcophagi | x=10/14, z=3..4, y=1..2 |
| Loot chest / approach | (12,1,2) / (12,1,3) via x=11 aisle |
| Gravekeeper hut | x=16..23, z=16..23; west doorway z=19..20 |
| Face / stair landing | x=18..22, z=3, y=4..10 / x=19..21,z=4,floor y=3 |
| Stair ascent north | x=19..21,z=7/6/5,y=1/2/3 |
| Spawn feet | (12.5,1,12.5), (12.5,1,16.5), (15.5,1,10.5) |

[C] Sources: architecture.md, Lychfield paragraph; FullWorld §9; visual_reference.md,
Core Look and Demon Doors. These describe crypts, sarcophagi, a gravekeeper hut,
and a carved stone face at gate stairs. [B] Dimensions, materials and compact scatter
layout are adaptations. The stone face is a sealed architectural landmark: Nostro's
command, talking/opening face and onward Old Graveyard Path are not implemented by
this geometry milestone. Do not register the unrelated generic Demon Door riddle.
No Cullis registration is added. These gameplay scope gaps remain visible.

Walk from (12,1,24) north to the crypt at z=7. Use x=11 or x=13 to pass
the central tomb, then stand at (12,1,3) to open its chest. From the main path,
turn east at z=19..20 into the hut; its crafting table and barrel are accessible
from (21,1,18) and (21,1,21). Turn east at z=9..10, then north along x=20:
three north-facing stairs climb to (20,4,4). The carved face at z=3 stays sealed.
The central lanes carry the three undead spawn anchors. Runtime translates these
by the actual placement origin; other POIs retain their existing spawn policy.

The structure contains no embedded NPCs. Automatic scatter populates its undead
and rolls the existing chest table. A raw `/structure load fc:graveyard ~ ~ ~`
only places blocks; this repository has no implemented `fc:place` handler. Test
scatter separately for population/loot. No fixed world adjacency is introduced.

## Evidence and limits

`python scripts/tests/test_graveyard.py` checks seven groups: unchanged registration
and loot, bounds/palette, stone tombs/chest clearance, keeper interior, connected
walking routes, north-facing stairs/face, and actual JavaScript placement against
voxel data on grass/dark. It checks save-region idempotence and translated spawn
clearance. The old owner fails four landmark/route contracts.
C2 additionally verifies emitted NBT bytes, runtime dimensions and render hashes.
The base suite includes this test in local and remote CI (17 gates total).

The isolated, south-facing and cutaway PNGs under screenshots/validation/W1.2 are
original generator renders, not engine captures. Reproduce by capturing graveyard()
with Vox.save patched, then render_structure(v); use yaw=-0.72 for the south view.
For cutaways, copy the Vox and clear x=6..18,y=5..12,z=0..8 plus
x=16..23,y=4..12,z=16..23; south cutaway also uses pitch=0.8. Only diagnostic copies
lose their roofs. The full screenshot pipeline redirects fc_lib.SHOTS before importing
gen_screenshots, and C2's separate renderer covers all 29 emitted structures.

[G] A search found a Windows TLC screenshot recorded September 25, 2005:
[MobyGames graveyard capture](https://www.mobygames.com/game/19218/fable-the-lost-chapters/screenshots/windows/127356/).
The page could not be fetched for pixel inspection (cache miss). This is a candidate,
not verified visual comparison evidence. No reference images were copied into packs.
Original-TLC comparison and canon grading remain pending. The block face and large
existing roof need in-world scale review; renderer cubes approximate stairs, slabs,
iron bars, glass and lighting. Automatic appearance grades are not canon grades.

## Manual checklist — all unrun

- [ ] Discover fresh placements on grass and dark terrain, including slopes; inspect
      edge grading, fence, floors and entrance, and walk every route above.
- [ ] Open the crypt chest, use the hut crafting table/barrel, inspect coffin spacing,
      lighting and collision, climb/descend the three-wide steps without jumping.
- [ ] Confirm three undead appear in the lanes, fight/navigate without clipping into
      graves or walls; verify chest loot through scatter (raw structure load is insufficient).
- [ ] Reload with two players and revisit: region persistence prevents duplicate
      structure/population/loot initialization; old graveyard regions retain their blocks.
- [ ] Compare all four landmark silhouettes with verified original-2005 TLC images.
- [ ] Track the separate missing Nostro interaction, talking/opening face and onward
      path; this architecture does not claim those behaviors are implemented.

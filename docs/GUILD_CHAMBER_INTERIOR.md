# Chamber of Fate: pointed bays and a clear outer walk

GP8, 2026-09-12. The Chamber now uses tall pointed wall bays, dark masonry and
seven high wall lamps. Freestanding quartz posts, saturated glazed rectangles,
floor campfires and the luminous roof are replaced through
`gen_structures.build_chamber_of_fate()`. Evidence and reproducible before/after
details are under `screenshots/validation/GP8/`. These are offline geometry views;
Bedrock appearance, light propagation, movement and save behavior remain unrun.

## Reference comparison and limits

The three native 226×166 battle views on PDF page 97 / printed page 96 of the
2005 *Fable: The Lost Chapters, Prima Official Game Guide* were inspected again.
They show a dark chamber, broad curved altar steps and tall pointed ribs on the
wall. Their provenance and hashes are retained in GP8's
`chamber-reference-provenance.json`, inherited from the GP5 reference audit.
[Original source PDF](https://www.ogxbox.co.uk/media/com_eshop/attachments/Fable_The_Lost_Chapters_Strategy_Guide_Book.pdf).
External images stay in ignored scratch and are not pack assets or committed
evidence pixels.

| Observed mismatch | GP8 change | Evidence boundary |
| --- | --- | --- |
| The original shows pointed wall ribs; the generated room had white isolated columns and rectangular colored panels. | Eight pointed stone bays are attached to a darker wall, with quiet recessed stone reliefs. | Pointed wall forms follow the original views. Eight bays, their dimensions and the block palette are Minecraft adaptations. Exact fresco subjects cannot be recovered from these images. |
| The original battle views show dark paving and a subdued chamber; the old generator created a glowing 177-block roof and bright gold trim. | Dark outer paving and an opaque stone soffit/cap replace the bright roof presentation. Seven elevated wall lamps provide localized light. | Combat effects obscure neutral lighting. Lamp positions, brightness and material choices require live comparison and are adaptations. |
| Thirteen floor columns in the outer walking band were obstructed by posts, low lamps or fires. | Wall details leave all 116 surveyed outer walking cells clear and connected to the entrance. | This is a measured Minecraft circulation improvement, not a recovered original floor-plan measurement. |

The source does not justify an exact roof profile, cave helix, mural sequence or
neutral light level. The current purple/sandstone Cullis pattern also remains a
clear visual mismatch. Those items remain follow-up work rather than receiving a
new fidelity grade from flat-color previews.

## Protected geometry and saved construction

The room remains 31×20×31 at Guild offset `(11,-22,27)`. Cullis feet stay at local
`(15,5,15)` and the north threshold at `(15,2,0)`. The user's full-circumference
shallow steps are unchanged: all five annular treads and six half-height
transitions survive around the altar. The generator changes 2,874 cells elsewhere.

A frozen digest checks 4,419 GP5 cells: the entire foundation, altar radius
≤8.4 through local y6, the north approach's clearance, and both glass/water
layers. The 177 water sources and their 221 glass base/rim cells are unchanged.
The new opaque soffit sits beneath that retained containment. Two obsolete low
lanterns at radius 8.54 disappear outside the protected altar.

The companion lifecycle change retains the exact old generated Chamber plan as
`scripts/data/guild_chamber_gp5.json`. An enrolled unfinished GP5 build selects
its matching saved plan instead of stopping when the new plan hash differs.
The usual original-cell journal checks still govern each write. An unknown plan
hash or corrupt journal never authorizes rebasing or a fresh destructive scan.
Completed and legacy occupied Chambers are not reconstructed or redecorated.

The runtime's one-off arbitrary vanilla painting injection is retired alongside
the geometry pass. New relief bays remain generator-owned; old saved painting
entities are preserved. This does not claim to implement the original narrative
frescoes. Existing one-time cave rewards remain separate.

## Evidence and validation

`render-chamber-details.py` reads the frozen old plan and the current owner to
produce open cutaways, low-angle east-bay crops and altar details. The open views
remove the roof and north half of the outer wall, then face into the retained
interior. All preserve actual slab halves. Other blocks, including lanterns,
remain cubes with approximate flat colors. The renders cannot test native light
propagation or establish matching player-height perspectives.

The four wall/cutaway views were inspected against the original native battle
images. The pointed profiles are now readable and the outer walk is clear. The
center's contrasting ward pattern, coarse block edges, missing narrative art and
unverified dome proportions remain visible limitations.

The local preflight ran 11 geometry groups before asset regeneration. It checks
both-way altar routes, all surrounding treads, adjacent floor access, the complete
outer walking band, pointed-rib profiles and shell closure after temporarily
sealing the intended entrance. Independent missing-step, headroom, obstructed
walk, breached wall and broken water-rim fixtures fail the intended checks.
The altar survey now excludes the roof's separate walkable top from its vertical
interval. Shared GP8 validation additionally checks regenerated asset/DATA
equality and the frozen compatibility plan; its exact results are recorded in the
GP8 checkpoint evidence.

Remaining acceptance: compare neutral in-engine wall/altar views with clearer
original footage; walk the cave approach and every altar side; verify native
lantern mounting, lighting and fluid containment; interrupt and resume both
recognized construction revisions; reload occupied old rooms and confirm their
geometry, painting entities and rewards remain untouched.

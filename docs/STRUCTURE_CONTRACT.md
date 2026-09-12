# Structure contract and placement bounds

The C2 contract now links all 29 generator outputs to pack assets, placement roles,
actual dimensions and fresh render evidence. It checks 23 scatter entries, two fixed
structures (Guild and Chamber of Fate), and four retained Guild annexes explicitly
classified as legacy. No tiles or aliases are currently emitted. Adding either requires
extending the declared model; the old one-off tiling patch is not an approved migration.

```sh
python scripts/structure_contract.py --output tmp/structure-contract.json
python scripts/tests/test_structure_manifest.py
node scripts/tests/structure_placement.test.cjs
python scripts/render_structure_contract.py
python scripts/validate.py --output screenshots/validation/C2
```

`scripts/structure_manifest.json` records IDs, owner functions, dimensions, titles and
placement classes. `structure_tables.cjs` parses the explicit STRUCTS/GUILD/CHEST_LOOT
JavaScript tables and structureManager.place calls with Espree, without running game
code. The Python audit reads direct builder calls from gen_structures.main() using AST,
regenerates into a temporary tree, and requires byte-identical shipped NBT. This detects
actual geometry/palette/content drift as well as missing files and dimensions.

Each ID maps to `screenshots/structures/contract/<ID>.png`, an entry in `evidence.json`
containing source-asset/image SHA-256 and dimensions, and its ID row in the adjacent
`AUDIT.md`. That report is the current structure-contract evidence; the older broad
`screenshots/AUDIT.md` is not proof of current generator output. The dedicated renderer
uses the existing offline renderer without regenerating mobs/items or using network
textures. All 29 images have been regenerated and the contact sheet visually inspected.
The metrics measure image appearance, not canon fidelity or in-world success.

The audit checks reverse edges for outputs, assets, scatter/fixed registrations, render
files/evidence and audit rows; loot keys must resolve to declared structures. Duplicate
IDs, unknown roles, undocumented legacy outputs and missing grades fail. Build validation
invokes the contract for both faithful staging and original previews; CI runs 13 Python
regression groups and four actual-source JavaScript placement tests.

## Defects caught and corrected

Four rectangular structures previously used square terrain/loot/spawn bounds:

| Structure | Actual width/height/depth | Previous square width |
| --- | --- | --- |
| Chapel of Skorm | 15/17/19 | 15 |
| Demon Door arch | 23/18/13 | 23 |
| Snowspire Oracle | 29/18/31 | 31 |
| Temple of Avo | 17/13/21 | 17 |

Every scatter entry now carries all three dimensions. Placement samples and grades
terrain over width/depth, scans loot over width/height/depth, uses depth for spawn bounds
and centers, and retains the existing square saved-place format with max(width, depth)
as a conservative envelope. Existing saved records are unchanged. These bounds affect
new placements; they do not retrofit terrain around already generated POIs.

The Guild asset was stale by 27 deepslate roof blocks. Its existing generator deliberately
excludes the open lawn around the Cullis/Skill nooks from roof infill. Regenerating only
that owner removed the stale panels; all 28 other assets already reproduced exactly.
The exact block coordinates are retained in `validation/C2/guild-asset-delta.json`.
Guild size, other geometry and feature anchors were preserved by that regeneration.

Numeric Guild anchors are checked separately against GUILD_LAYOUT. A second check
inspects actual interaction blocks (sea lanterns/lecterns) and standing clearance.
This exposed Maze's old anchor at (46,12,72) inside the solid tower column. A distinct
maze_spawn layout key now places him at (46,12,70), on clear study floor. The generator's
tower center remains (46,72). Existing runtime anchor refresh/roster paths use that same
GUILD.maze point. The old coordinate fails the physical regression fixture.

## Manual checks still required

- In a disposable world, place each rectangular POI on uneven ground. Check its full
  depth, foundations, loot chests, population and Cullis location; then reload.
- Check the Guild loads in the actual engine, including its large footprint. No static
  asset or numeric-anchor test proves engine placement limits or loaded-chunk behavior.
- Run `/scriptevent fc:reanchor`; visit the skill/cullis platforms and all three quest
  lecterns. Check Maze on the study floor, his idle/roster behavior and reload behavior.
- Inspect the western nook roofs in-world. The support audit reports no disconnected
  blocks, but its eave heuristic still reports overhangs and does not establish grade A.

The current standing check uses exact air for two vertical cells and non-liquid ground
at selected integer anchors. It does not model Bedrock collision shapes, navigation,
NPC width or all generated interactions. These remain explicit limits, not hidden passes.

W2.2 also validates optional explicit `mobSpawns`: one three-number feet position
per mob, finite coordinates, horizontal bounds and vertical room for floor/head.
A negative fixture copies Hook Coast's coordinates into the smaller Snowspire POI;
it now fails instead of silently allowing a spawn outside its footprint. These
bounds checks do not prove block clearance; each changed POI's actual-source voxel
population tests cover that separately. The random-spawn fallback is unchanged.

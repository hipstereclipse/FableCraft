# Guild cave lifecycle and Chamber access

GP5, 2026-09-12. This implements the next bounded repairs from
[GUILD_CAVE_REVIEW.md](GUILD_CAVE_REVIEW.md). Evidence is under
`screenshots/validation/GP5/`. All execution and images are offline; live Bedrock
collision, chunk loading, fluid updates and crash persistence remain unrun.

## Construction and saved worlds

The handwritten `guild_caves.js` owns the final cave plan and a versioned
construction journal. `gen_structures.py` owns both the Chamber and the exact
Guild entrance crop, exported by `gen_behavior.emit_script_data()` into DATA.
No pack UUID, manifest or API version changes are required.

New Guild placement first needs durable enrollment. Maintenance resumes enrolled
initial work after the terrain worker settles. The worker snapshots every original
cell before any cave/Chamber write, then applies bounded batches through native
block permutations. A missing block, failed write, canceled job or reload can
resume from the journal. It compares saved originals and verified progress before
writing; changed completed cells stop construction instead of being repaired.
Completion flags follow verification of the assembled final plan. The old broad
Chamber hollowing sweeps are removed. The Chamber has no entity or block-entity
payload, so exact generated per-cell placement preserves its asset contract.

The initial scan accepts natural terrain and the exact generated surface entrance
crop, refusing foreign containers or other construction. This cannot distinguish
a player's identical replacement permutation from the generated/natural original.
The journal is not an engine transaction; power-loss durability still needs live
testing. An incompatible/corrupt journal or conflicting player change remains
unresolved and never authorizes a fresh destructive baseline.

Legacy worlds without a new construction journal are not enrolled by maintenance.
Their old `fc_guild_caves_done`/Chamber flags and occupied geometry remain intact.
This deliberately leaves old interrupted caves, old stair geometry and old missing
thresholds unresolved. Reanchor refreshes coordinates only. A future migration
needs its own bounded evidence and preservation policy.

## Connected route and travel contract

The cave owner preserves a full Library entry floor while opening the standing
and head volume. The helix still uses half-block treads and reaches the level
causeway through the Chamber's north arch. Following the user's explicit correction, the Chamber generator replaces the
full-block mound terraces with concentric half-block steps around the entire altar.
Six half-height transitions connect the surrounding floor and raised center.
The final geometry changes 184 exposed annular tread cells, with matching stone
brick full blocks and slabs. Each band surrounds the full altar; all tread cells
join the cardinal walking graph. At rasterized corners, movement may change
height by half a block to follow the circumference; a perfectly level cardinal
circuit on every thin ring is not claimed. Its raised platform and
room origin do not move. Guild surface geometry and Maze `(46,12,70)` stay fixed.

The Chamber's generated `CHAMBER_LAYOUT` supplies size `(31,20,31)`, origin offset
`(11,-22,27)` and Cullis feet `(15,5,15)`. Registration uses that contract and the
actual detector. A saved point named Chamber of Fate is corrected only if it has
exactly the known old x/z and local y7, the expected core/ring still exists, and
arrival/head cells are clear. Other registry fields and destinations survive;
custom coordinates, ambiguity, missing blocks and failed persistence defer the
correction. This migration changes coordinates only.

An adjacent review found the decorative skylight's 177 water sources had 44
uncontained lateral neighbors. The generator closes that perimeter with glass;
water must be applied after its containing cells. This is a Minecraft construction
repair, not a claim that this skylight appears in TLC.

The original `_verify_caves.py` mirrored the old carve and passed despite the real
missing floor. It now runs the production lifecycle, assembled route and detector
suites instead. The frozen GP4 probe remains historical evidence of the defects.

## Original 2005 reference comparison

Casey Loe / Kaizen Media Group, *Fable: The Lost Chapters, Prima Official Game
Guide*, Prima Games, 2005, ISBN 0-7615-5180-8, PDF page 97 / printed page 96.
The complete page and three native 226x166 battle screenshots were inspected.
[Source PDF](https://www.ogxbox.co.uk/media/com_eshop/attachments/Fable_The_Lost_Chapters_Strategy_Guide_Book.pdf).
Source hashes and ignored scratch paths are recorded in `reference-provenance.json`.
External pixels are never pack assets or committed evidence images.

The battle images show broad shallow curved steps, dark paving and tall pointed
wall ribs. The revised concentric steps follow that broad curved form around the full altar.
The block radii, six half-height transitions and exact materials are Minecraft
adaptations, not measurements recovered from these low-resolution images. The current alternating masonry, bright quartz columns, rectangular
colored panels and glowing artificial roof still differ substantially. The source
is combat footage captured in a guide; spell light and small image size cannot
establish neutral lighting, exact dimensions, complete frescoes or the cave route.
No image-based justification is claimed for the existing spiral geometry.

The user explicitly requested image searches and full surrounding steps during
this pass. Google Images was attempted, but the fetch could not open it and no
browser was available. General image search and direct screenshot downloads
continued. Results labeled Anniversary or later games were excluded as original
TLC evidence. A 1280x727 Jack/wall image in a
[Steam TLC guide](https://steamcommunity.com/sharedfiles/filedetails/?id=121425366)
was inspected, but its exact version is unverified and it does not show the altar.
It supplies no independent stair measurements; the contemporary Prima images and
the user's correction remain the basis for the surrounding-step design.

Partial visual grade: C. The original circular raised-center idea is recognizable,
but center material contrast, wall detail and lighting need a later
reference-led design pass. Before/after altar details render actual half slabs;
open room cutaways remove roof/north wall for inspection and are explicitly labeled.
The standard all-category renderer represents blocks as cubes, including slabs.
The dedicated altar and open cutaway views preserve slab heights.
Neither renderer proves gameplay or resemblance from matching player-height views.

## Offline validation

All 38 base gates pass from `tmp/conformance/GP5-final-snapshot`, exported from
the reviewed index to exclude parallel NPC/portal changes and inherited dirt.
The focused suites cover 20 cave lifecycle groups, 10 final Chamber route groups,
6 actual Cullis detector/migration groups and 16 C2 contract groups. The initial
full run caught an outdated bulk-placement-only C2 reader; the final checker
recognizes the imported per-cell owner and requires its actual DATA binding.
Negative fixtures remove the import, factory or manifest independently. Initial
failure logs are retained separately from the successful final results.

Explicit lint (zero errors, 19 inherited warnings), 17 spell groups, ESM parsing
and Guild diagnostics pass. The full all-category pipeline rendered 51 mobs,
55 items, 130 recipes, 32 structures and 13 galleries; C2 covers 35 assets/renders.
Dedicated half-slab altar and cutaway views were inspected. Roof diagnostics
retain the same 388 eave-overhang cells in 55 clusters as GP4; no new floating
blocks were found. These diagnostics do not establish original-game fidelity.

## Acceptance still pending

- [ ] In a fresh world, interrupt loading/construction and confirm safe resumption,
  contained fluids, eventual completion and useful content-log diagnostics.
- [ ] Walk Library threshold, helix, landing, bridge, arch, circular steps and Cullis
  both ways without jumping; inspect headroom, rails and nearby NPC collisions.
- [ ] Verify standing/dwell Cullis activation at its corrected height and safe travel.
- [ ] Reload old completed/interrupted worlds; confirm geometry, inventories and
  progress remain unchanged while only a recognized registry height can migrate.
- [ ] Test player edits during construction, concurrent players, unload, death and
  power-loss persistence in the supported Bedrock build.
- [ ] Compare neutral player-height Chamber and Guild views with clearer original
  footage; refine curved steps, wall ribs, mural presentation and lighting.

These repairs remain in-progress acceptance under the supplemental GP/DP queue.
They do not change C3's historical 45-leaf denominator or close manual checks.

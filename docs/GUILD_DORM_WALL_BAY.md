# Guild dormitory wall bay — GP20

One existing upper-dormitory wall bay now has muted red terracotta infill between
dark-oak sides. The preceding partition was plain stone brick. This is a bounded
material change based on an inspected original TLC dormitory view; it does not
establish the generated room's overall fidelity or measured original layout.

The [original screenshot 141296214](https://steamcommunity.com/sharedfiles/filedetails/?id=141296214)
shows red plaster-like panels between heavy timber uprights, dark carved lower
panels, narrow pointed windows, patterned rugs and red-covered beds. Its retained
page was posted April 2013 and identifies the original TLC application. Source URL,
image hash and provenance are recorded in GP16/additional-online-references.json.
The downloaded image remains ignored reference material and is not a pack asset.

The chosen bay is local x84, y7..8, z17..21. Six red terracotta cells occupy
z18..20; four dark-oak cells form the sides at z17 and z21. These materials, size
and location are Minecraft adaptations. The existing shared roof courses at y6
and y9 remain in place; they do not reproduce the original carved dado. This
single-block-thick partition also changes on its reverse west face, beside the
stores roof. Focused views record that effect rather than implying an interior-only
surface treatment. Remaining stone walls, room proportions, patterned floor/rugs,
carved panels, window shapes and bed arrangement remain open reference work.

`build_guild_dorm_wall_bay` runs through the structure generator after final
circulation. It consumes no randomness and replaces existing full solid cells;
it adds no obstruction or furniture. Floors, stair treads, openings, windows,
lights, beds, anchors and all other campus cells are retained. Existing placed
Guilds are not rebuilt or redecorated. Reanchor remains a coordinate operation.

The shared screenshot renderer gains only the red-terracotta color entry needed
for the new material. RGB (143,61,47) is an approximate offline proxy, not a
calibrated color from the source image. Focused views use clipped voxel geometry
and simplified block shapes; native textures, lighting and physical movement
remain unrun.

Behavior regressions passed before targeted Guild regeneration. Exactly one of
1,661 compared pack files changed: guild_hall.mcstructure. Independent decoding
of the actual DP6/current owner outputs confirms ten changes out of 395,280 cells,
with all other cells, seeded RNG and layout exact. Existing palette entries and
NBT metadata remain intact; only the red-terracotta entry is appended. All 4,820
other surveyed NE-room cells, 345 deck cells, ten windows and 678 Maze reservations
remain exact. The campus keeps all 13,822 walking nodes; both 21-point dorm stair
paths and all five wall-front approaches remain available. Three independent
scope, missing-tread and blocked-headroom failures are detected.

All 51 base gates and 64 ESM checks pass in the reviewed snapshot. Initial build
validation caught the prior C2 source record before the concurrent fresh render
replaced it. Its failure is retained; only that build gate was rerun after the
new C2 image and metadata entered the reviewed index. Production/tests did not
change during that correction. Fresh 35-asset C2, full 281-PNG renders and Guild
diagnostics pass. Versus GP18's retained visual baseline, only the Guild asset,
its C2 image, its full card and the containing places gallery change; the other
34 assets/C2 images and 279 full PNGs are exact. Six inspected decoded cutaways
show the east interior and both low/high reverse views. Full cards remain too
distant to establish interior fidelity.

Evidence, commands, scope hashes and raw results are under
`screenshots/validation/GP20/`, including independent-review.md and
visual-delta.json. Native movement, collision, lighting, texture and saved-world
acceptance remain unrun. The adjoining bridge/range survey keeps both crossings
intact and records a hypothetical rail footprint without shipping it. Native
Skill arrival still needs offset/search/event calibration; a bounded official
Linux server download attempt failed at transport, before execution.

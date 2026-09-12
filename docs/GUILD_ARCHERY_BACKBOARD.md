# Scenic archery backboard — GP15

The Guild archery range now has a framed mountain-and-valley board behind its
existing targets. This restores a distinctive prop visible in two original TLC
screenshots. The picture is an original coarse block mosaic, built from muted
terracotta, pale peak caps and a dark tree silhouette; it contains no copied
screenshot pixels or extracted game art.

## Original reference and chosen adaptation

The [Altered Gamer TLC training walkthrough](https://www.alteredgamer.com/fable-the-lost-chapters/103803-walkthrough-the-guild-and-the-guildmaster/)
shows the range from the firing area. The inspected screenshot has the classic
PC interface and a visible TheInkandPen 2011 watermark. A broad rectangular
painting of purple mountains, trees and a valley stands behind the targets,
against Guild masonry. Low greenish timber rails and diagonal braces mark the
foreground. The mountains belong to the painted prop; they do not justify
reshaping the campus terrain.

An independent [Gamepressure TLC training view](https://www.gamepressure.com/fablethelostchapters/guild-training/z4d)
shows the same scenic board behind the black-hooded apprentice and Whisper.
Its local historical filename is `gamepressure-will.jpg`, but its pixels depict
archery. At only 280×159 pixels it corroborates the landmark and braced rails,
without establishing exact dimensions or a target count. The page was last
updated in 2016; the classic models and matching pre-Anniversary view provide
stronger version evidence than that update date alone.

The generated 9×6 frame, one-block depth, terracotta palette, 7×4 image and
particular peak/tree positions are Minecraft adaptations. They are not a measured
reconstruction. The two pale peaks use different heights so the tiny pattern
reads as an asymmetric valley rather than a face. The full wooden border is
also a chosen block-scale support. Continuous braced rails, exact original
painting detail and straw-dummy appearance remain separate work.

Exact source URLs, dimensions and image hashes are in
[archery-reference-provenance.json](../screenshots/validation/GP15/archery-reference-provenance.json).
External reference images remain ignored scratch material.

## Final geometry and protected approaches

`build_guild_archery_backboard` places exactly 54 blocks at local x80..88,
y1..6, z30. Every cell was air in the complete baseline builder. The timber
border surrounds the flat picture and rests on the existing uninterrupted
ground. The helper runs after all landscaping, circulation and decor passes;
it consumes no randomness and cannot alter earlier random path or tree choices.

The board lies behind the active target `(83,2,34)` and between the south kitchen
and dormitory doors at x78/x90, z28. A one-block passage remains behind it at
z29, with clear standing columns at both ends and across its front at z31.
The tests preserve those specific approaches as well as complete gate routes
to both doors, the Skill mark, both Might marks, the east junction and the Will
mark. Gate return routes from both rooms and the range also pass.

Paired complete Guild builds differ only within that 54-cell plane and finish
with identical shared RNG states. All ground floors, four target blocks, seven
archery/Will pumpkin heads and their supports remain unchanged, as do all
runtime anchors and Maze's fixed `(46,12,70)` position. There is no saved-world
repair, relocation or replacement operation; existing placed Guilds are not
reconstructed by this change.

Only three missing static colors are added to `gen_screenshots.py`, beside the
existing white terracotta entry. Light-blue, purple and green terracotta had no
earlier generator uses. These valid vanilla block identifiers require no new
block resource or API. The static RGB values approximate native materials;
the Microsoft [vanilla block listing](https://learn.microsoft.com/en-us/minecraft/creator/reference/content/vanillalistingsreference/blocks?view=minecraft-bedrock-stable)
documents identifiers, not the appearance of this authored board.

## Verification and limits

Six focused groups check the exact whole-campus voxel/RNG scope, frame and base
support, retained props/floors/anchors, behind-board and side approaches, complete
gate routes, and the actual production Skill station/shot against final voxels.
Independent missing-frame, unsupported-base, blocked-headroom and missing-path
fixtures fail their corresponding checks. The Skill harness also rejects
missing station support, station obstruction and an obstructed geometric ray.

The harness evaluates the actual scheduler's Skill coordinates and
`showPracticeShot`, recording its six harmless particle outputs. The emitted
line runs from `(83.5,2.35,39.5)` to `(83.5,2.45,34.5)` and stays clear before its
target. This is an offline geometry check: the production Skill callback still
has no block-lane preflight. The change preserves the ray without claiming to
add that missing runtime behavior. The existing Will preflight, dummy contract
and six negative voxel cases pass unchanged.

The existing Will suite (3 groups), maintenance suite (4 Python groups plus
8 JavaScript cases) and training suite (25 groups) also pass. Evidence is under
[GP15](../screenshots/validation/GP15/). Four inspected before/after renders show
the framed picture and adjoining range/doors. Their scope JSON records all
changed coordinates, matching normalized outside hashes and surveyed routes.
Slabs, carpets and isolated posts use reduced shapes; target/furniture textures
and lighting remain approximate. They do not execute Bedrock collision or AI.

- [ ] Inspect the board and original target textures from the native firing camera.
- [ ] Walk behind and around both ends, then through both south doors and back.
- [ ] Observe Skill and Will practice, interruption and resumption in Bedrock.
- [ ] Check native lighting, distant readability and preservation of saved construction.
- [ ] Measure braced rails before adding their collider footprint to the range.

The isolated reviewed snapshot also passes all 46 base gates and 62 ESM syntax
checks. Fresh C2 covers 35 structures; only the Guild asset/image differ. Full
rendering produces 281 PNGs (51 mobs, 55 items, 130 recipes, 32 structures and
13 galleries), with 277 audit rows and no renderer flags. Native acceptance
remains unrun.

Player instruction, Whisper sparring, moving/scored targets, reactive straw
dummies and purposeful walking to training marks remain open. This fixture pass
does not establish complete TLC training or whole-Guild fidelity.

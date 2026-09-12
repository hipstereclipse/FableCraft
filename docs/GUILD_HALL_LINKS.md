# Connected hall and Library sightlines — GP11

The Library and Store entrances now retain their broad masonry arches. An old
late generator pass rebuilt small windowed tunnels inside the already joined
hall, leaving a one-block centre lane, sidewalls at eye height and a low slate
roof beneath the real ceiling. GP11 retires those redundant shells while keeping
their flush floors and every existing room, stair and interaction anchor.

## Whole-facility review and priority

The GP8/9/10 source state was reviewed against three inspected TLC hall views and
the 2005 Prima guide, PDF pages 34–36 / printed pages 33–35. The source hall images
and provenance are listed in [GUILD_MAP_TABLE.md](GUILD_MAP_TABLE.md). The guide's
edition/provenance is recorded in [GUILD_CAVE_LIFECYCLE.md](GUILD_CAVE_LIFECYCLE.md).
External pixels remain ignored developer references.

| Area reviewed | Concrete remaining gap and consequence |
| --- | --- |
| Main hall → Library/Store | **Chosen priority:** later windowed tunnel shells overwrite the earlier broad arches. They constrict the direct walking lane and interrupt the open interior sightline. This is a final-voxel defect with an existing larger arch/roof already authored around it. |
| Library and north rooms | Tall shelf groups exist, but alternating columns and missing middle courses produce broken book walls. The small guide image shows a warm book-lined interior; it does not establish exact shelf measurements or justify wholesale room relocation. |
| Dining and sleeping spaces | Upper dining is a single bunk hall; the NE upper rooms are four unpartitioned rug groups. The text snapshot's three-room claim still needs better original interior views before introducing walls or moving beds. |
| Maze's tower | Access now works. Three generated levels, tall glowstone strips and the central luminous newel remain strong adaptations. The guide's small upper-room view shows stairs and a round bright window, insufficient to settle a complete tower redesign. |
| Courtyard and river | Current exterior remains a rigidly bounded campus with broad roof masses and a simplified river. The guide minimap supports a connected green, watery courtyard; roof pitches, neutral-light materials and exact proportions need clearer original views. |
| Training grounds | Melee/archery are active and Will now has island practice. The guide still shows a richer reactive-dummy lesson; static dummy appearance, tree enclosure and bridge proportions remain separate work. |

The original TLC hall screenshots show broad arched openings, connected stone
interiors and a visible stair/gallery structure. The guide's Library image is
small and partly obscured; it supplies book-lined-room context, not a measured
matching doorway. Existing grey masonry is retained: warm screenshot lighting
alone cannot prove that every wall should be replaced with orange stone.

## Reproduced defect and bounded owner

The earlier `join_bay` and `arch_on_z` passes already supply a roof at y9, an
eight-wide Library opening at z30 and a six-wide Store opening at z52. The
historical `link_corridor` later inserted sidewalls at x25/x27 over z30–34 and
x26/x28 over z50–52, plus roofs at y4. GP2 cleared only the low cells beneath the
rotunda stairs, leaving the indoor tunnel shells in the adjoining rooms.

Exact before examples: `(25,2,30)` and `(27,2,33)` are stone in the Library's
intended opening; `(26,3,32)` is a lantern under the added roof; `(26,2,52)` and
`(28,2,52)` close the Store's sides. These cells are air after GP11. The existing
Library and Store arch lintels and real bay roofs remain intact.

`finish_guild_link_floor` in `scripts/gen_structures.py` replaces the old nested
helper and its two calls. It keeps the same 24 flush floor cells, consumes the
same six `guild_brick` calls per row (**48 total draws**) and adds no interior
wall, glass, low roof or lamp. The existing broad room builders own those parts.

Complete paired Guild builds differ at **64 final cells**: 42 in the Library
envelope and 22 in the Store envelope. Sixty-three tunnel cells become air; the
old slate at `(28,4,50)` reveals the original rotunda masonry. All differences
stay within x25–27/y1–4/z30–34 or x26–28/y1–4/z50–52. Every floor cell and every
block/state outside those volumes is identical, including the GP10 map and
shared-RNG-dependent trees and furnishing. Serialized palette indices may differ.

Three continuous ground lanes at x25–27 connect the Library and Store to the
hall. The existing stair carriage still limits height at the rotunda edge;
GP11 does not pretend that the entire room is equally tall. Wake, quest fronts,
Guildmaster birth, library residents, cave threshold, gallery, living-space and
Maze routes remain checked and fixed.

This affects new Guild placement only. There is no old-world recarving,
geometry migration, delayed repair or saved-state change.

## Evidence and acceptance

[GP11 evidence](../screenshots/validation/GP11/) contains Library/Store detail
pairs and a joined hall/Library cutaway pair. Each before build uses the actual
historical vertical connector fixture inside the current generator. The paired
builds otherwise share every owner. Crop/removal limits, 64 changed coordinates,
source-image hashes and matching normalized outside-link hashes are in
`hall-link-render-scope.json`.

Focused checks: **seven hall-link groups**, plus six existing circulation groups,
six map groups and 22 resident lifecycle/birth groups. Failures are exercised
with independently blocked side lanes, missing floor support, a low roof in the
arch and one extra RNG draw. The original tunnel fixture fails the new width and
arch checks, proving that these checks detect the reproduced defect.

The renders respect half-height slabs but use approximate flat material colors;
they omit specified roof/front slices to expose the room. They are neither native
lighting nor player cameras. The open joins are visibly improved; whole-facility
TLC resemblance remains **partial C**, pending the other gaps above and engine
acceptance.

- [ ] Walk all three lanes in both directions in a fresh native Guild.
- [ ] Pass another Hero/NPC in the entrances and confirm collision/pathfinding.
- [ ] Inspect Library sightlines from the map under native light; compare original views.
- [ ] Visit the cave lip, Store, gallery, dormitory and Maze without lost interactions.
- [ ] Reload an occupied old Guild and confirm saved geometry/construction persists.

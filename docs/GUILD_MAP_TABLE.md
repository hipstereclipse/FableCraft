# Guild map-table refinement — GP10

The main-hall table now reads as a low, wood-framed land-and-sea relief.
The old random lapis/emerald/gold mosaic and central sea-lantern/end-rod column
made the Guild's focal point resemble a beacon. The generated replacement has
one connected earthy landform, a connected recessed teal bay, a sandy shoreline
and a low polygonal wood rim. This is an authored Minecraft adaptation, not an
exact reconstruction of Albion's coastline.

## Original-game comparison

Three source views were inspected directly on 2026-09-12:

| Source | Visible evidence and limit |
| --- | --- |
| [Andy Zhang's TLC review](https://andyzhang.me/blog/game-review-fable-the-lost-chapters.html) — `guild-table-review.jpg`, 1280×720 | Broad low relief with connected brown/green terrain, dark teal sea and a polygonal wood frame. Nearby red runners, masonry arches and Guildmaster show its modest height. Review screenshots, rather than a calibrated original capture. |
| [MobyGames TLC Windows screenshot](https://www.mobygames.com/game/19218/fable-the-lost-chapters/screenshots/windows/786915/) — `guild-table-moby.png`, 1000×800 | Low geographic relief beneath the twin stair/gallery room; broad wood rim and open sightline above the table. The page rejected access with HTTP 403; the [direct image](https://cdn.mobygames.com/screenshots/15759126-fable-the-lost-chapters-windows-an-experienced-old-hero-clad-in-.png) was available and inspected. |
| [uvejuegos TLC PC screenshot](https://uvejuegos.com/img/juegos/13352/ocht.jpg) — `guild-hall-uve.jpg`, 1024×768 | Wider hall view confirms the low table, stair pair, warm-lit masonry and flanking arches. Perspective and the foreground Hero obscure fine detail. |

Source pixels stay under ignored `tmp/conformance/reference-guild/` and are not
pack assets. Their hashes are recorded in the render-scope evidence. The local
[architecture snapshot](references/fable-tlc-expert/architecture.md) also describes
a three-dimensional relief map, quest-card use and the Guildmaster's presence.

The before/after render review shows the beacon obstruction removed and the
random jewel patches replaced by continuous regions. The table's frame and
shallow relief now follow the visible source cues. The nearby cutaway retains
both existing stairs and their open central well. Overall original-game fidelity
remains **partial C**: seven-block geography is coarse; the native block textures,
warm interior light, arches and room proportions still need original-view review.
No offline score establishes an in-engine match.

## Geometry and saved-world scope

Owner: `build_guild_map_table` in `scripts/gen_structures.py`, called once by
`build_guild_hall`. It retains the existing 37 occupied table cells at local y1
and the same flush wooden footprint beneath them. Bottom slabs place the frame,
sea and shore at y1.5; earth/moss reach y2. Nothing on the table occupies y2 or
y3, clearing the former y4-high beacon. The coastline contains 14 connected
land cells and seven connected sea cells inside the 16-cell rim.

The map keeps all 37 historical RNG draws. A paired complete-campus build with
the historical map fixture changes exactly **38 final voxels, all map furniture**;
every other block name/state is identical. Palette indices can change in the
serialized structure, so this is normalized final-voxel equality, not a claim
that unrelated byte offsets inside one NBT file are unchanged.

Wake `(20,42)`, quest lecterns `(22,42)`, `(28,39)`, `(28,45)`, their facing states,
Guildmaster birth `(22.5,1,41.5)`, the surrounding floor, and all remaining Guild
anchors stay fixed. Every formerly clear lectern side remains clear and all
three interaction fronts are reachable from the gate. The existing sequential
resident-collider test still finds supported birth points for all twelve slots.

This generator change affects newly placed Guilds. There is no saved-world
rewrite, delayed repair, version change or migration; existing player builds,
resident identities and quest progress retain their prior geometry/state.

## Evidence and verification

Evidence: [GP10 directory](../screenshots/validation/GP10/).

- `map-relief-before.png` / `map-relief-after.png`: table and adjacent floor,
  including true half-height slabs.
- `map-hall-cutaway-before.png` / `map-hall-cutaway-after.png`: same surrounding
  room geometry with the western slice and roof omitted to reveal the interior.
- `map-render-scope.json`: crop limits, reference hashes, 38 changed coordinates,
  zero non-map changes and matching normalized outside-map hashes.
- `map-tests.log`: six final-voxel/RNG/approach groups, including independent
  beacon, missing-rim and extra-RNG-draw failure fixtures.
- `map-adjacent-routes.log`: six existing Guild circulation groups.
- `map-resident-births.log`: 22 resident lifecycle and production-birth groups.

The initial focused test guessed 36 changed voxels; inspection showed 36 surface
changes plus two removed beacon cells. That count-only failure remains in
`map-tests-initial.log`; the corrected final check passes at 38.

The focused renderer uses flat approximate block colors and native slab heights.
It adds only the missing `dark_prismarine_slab` color to the shared screenshot
palette; no other generated structure previously used that material. The normal
full structure renderer still draws slabs as cubes, so use the focused views to
review the table's height. Neither renderer simulates Bedrock lighting or NPCs.

- [ ] Native fresh Guild: inspect the table at player eye height under game light.
- [ ] Click each quest lectern from its intended side; walk both table-side routes.
- [ ] Check Guildmaster interaction, walking/collision and returning Follow state.
- [ ] Reload an existing Guild and confirm its geometry and saved construction persist.
- [ ] Compare matched original-game angles, material appearance and hall proportions.

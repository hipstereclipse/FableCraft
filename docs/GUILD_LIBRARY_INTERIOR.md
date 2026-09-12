# Guild Library: framed shelves and reading furniture

GP12, 2026-09-12. The Library now has two continuous framed bookcase walls,
a modest reading desk and four supported warm lamps. The existing three lecterns,
room shell, floor and adjoining routes remain unchanged. The owner is
`gen_structures.build_guild_library_interior()`; new Guild placements receive its
141 changed cells. This pass adds no runtime repair or saved-world migration.

## Original reference and adaptation boundary

The original 2005 *Fable: The Lost Chapters, Prima Official Game Guide*, PDF page
34 / printed page 33, was inspected. Its Library screenshot shows a tall wall of
closely spaced bookshelves and a broad wooden furnishing in front, interpreted
here as a reading surface. The accompanying text identifies books available in
the ground-floor Library and the upstairs barracks. The repository's architecture
snapshot also describes tall wall bookcases.
[Original guide PDF](https://www.ogxbox.co.uk/media/com_eshop/attachments/Fable_The_Lost_Chapters_Strategy_Guide_Book.pdf).

The screenshot supports a book-lined room with substantial wood furniture. It
does not establish exact dimensions, shelf counts, timber species, table location
or lamp placement. Two wall-depth bookcases, their framed bays, a narrow slab
desk, four hanging lamps and their mounting heights are Minecraft adaptations.
The 60 bookshelf blocks do not represent 60 original collectible books. Existing
book identities, inventory, quest progression and dialogue are untouched.

The native page remains in ignored reference scratch. Its hash and source are
recorded in `screenshots/validation/GP12/library-reference-provenance.json`.
External pixels are not pack textures or committed evidence images.

## Reproduced furnishing defects

The previous final Library contained 44 bookshelf cells and three lecterns.
Ten upper shelf columns occupied y6–7 while y4–5 was completely empty, producing
disconnected horizontal bands rather than continuous cases. Although the masonry
behind those blocks supplied a wall attachment, the visible case had no frame
joining its upper and lower rows.

The intended central lantern at `(27,7,23)` also had no supporting cell above or
below. The final `fix_floating_decor` owner deleted it, leaving no lantern or
torch within the Library interior. The new fixtures survive that final owner:
each hangs below a full timber bracket connected directly to a bookcase.

`test_guild_library.previous_library_interior()` reconstructs the exact previous
furnishing calls inside the same final Guild builder. Both defects are reproduced
after all decorators run; the fixture does not manually remove the old lamp.

## Narrow geometry and access

Bookcases occupy the existing wall-depth columns x19/x35, z18–28, y1–7.
Their timber frames connect every shelf band to the floor. The west commons
doorway at x19/z21–23 remains clear through y3; a connected header spans above it.
The three lecterns stay at x22/z19,23,27 with their previous directions.

The desk at x31/z20–26 uses three solid legs and a continuous bottom-slab top,
whose upper surface is local y2.5. Both long sides remain accessible from the
entrance. Four wall lamps at x20/x34, z19/27, y5 hang beneath solid y6 brackets.
They sit above standing and headroom volumes.

All five columns of the main Library spine at x25–29/z17–29 remain clear. Paths
to the north cave threshold, western commons, north wing, broad GP11 main-hall
entry and Will resident home remain connected in both directions. The complete
campus comparison also preserves every cell outside the furnishings, including
the Library floor and shell, Cullis/skill platforms, cave crop, beds, training
grounds, main-hall gallery and Maze's `(46,12,70)` anchor. No shared RNG draws
are added or removed; distant trees, masonry and furniture remain identical.

## Evidence and acceptance

The six new regression groups check the actual final generator. They reproduce
the old gaps and missing lamp, enforce whole-campus change scope, check grounded
continuous cases, verify lamp supports and desk slab surfaces, and exercise
lectern/desk access plus adjoining routes. Independent broken shelf-band, missing
bracket, detached bracket, obstructed spine, missing floor and unrelated-campus
change fixtures fail their respective checks. All six groups passed locally.
Shared milestone validation records the regenerated asset and full gate results.

`screenshots/validation/GP12/render-library-details.py` generates paired room
cutaways, east-case details and desk details. The room cutaway removes the roof
and western wall/case/lamp slice, exposing the retained interior. The desk uses
actual half-slab geometry; other blocks, including lamps and lecterns, remain
diagnostic cubes with approximate flat colors. Renders establish neither native
lighting nor player-camera appearance. The original reference and the paired
room/case/desk views were inspected; the separated shelf bands are gone and the
room now has readable furnishing groups with open circulation.

Still unrun in Bedrock: lamp placement and light propagation, desk/lectern use,
NPC passage at the west doorway, the complete Library-to-cave walk and old-world
preservation after reload. Exact Library proportions, the current varied wood
floor, a functional concealed bookcase entrance, book interactions and adjoining
dormitory/Maze fidelity remain separate reference and implementation work.

Additional online review: two original-TLC Library cutscene screenshots now
corroborate continuous framed, floor-supported bookcases and open arched access.
Both show the burning story state; neither establishes a neutral lamp or desk
layout. [The additional image ledger](GUILD_ONLINE_REFERENCES.md) links the actual
views and records version confidence. No contradiction with this bounded fixture
pass was found; the desk and lamp placements remain adaptations.

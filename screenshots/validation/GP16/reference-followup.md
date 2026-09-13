# GP16 supplementary Guild reference and furnishing audit

Seven additional original-TLC screenshots were downloaded to ignored scratch and
their actual pixels inspected. The supplementary corpus now has 26 distinct
accepted views, in addition to the original guide and earlier map-hall references.
This pass changed no geometry, runtime, assets or occupied world.

Exact URLs, image/listing hashes, dimensions, exclusions and per-view limits are in
[additional-online-references.json](additional-online-references.json). Each
accepted image matches a screenshot card with `data-appid="204030"`, its screenshot
ID and direct image URL in saved Steam listing HTML. Classic models, textures and
interface/cutscene presentation were inspected. Patch/mod status remains unknown.
External screenshots, contact sheets and source HTML stay under ignored
`tmp/conformance/reference-guild-additional`; no external pixels belong in packs or
committed validation evidence.

## Useful new evidence

| Source | Visible contribution | Important limit |
| --- | --- | --- |
| [Guild dormitory 141296214](https://steamcommunity.com/sharedfiles/filedetails/?id=141296214) | Wide ordinary gameplay view: at least three separate red-covered bed forms, red wall panels, timber framing, pointed blue windows, diagonal stone paving and small patterned rugs. | One bed is cropped and the entire room is not shown. Purple NPC glow and unknown display settings prevent calibrated neutral-light claims. |
| [Archery 689540321](https://steamcommunity.com/sharedfiles/filedetails/?id=689540321) | Clear painted mountain/conifer background behind separate castle-shaped scenic targets; horizontal green wooden rail with triangular braces. | Characters hide rail ends and boundaries. Exact footprint and complete gate/perimeter layout remain unknown. |
| [Will station 689540613](https://steamcommunity.com/sharedfiles/filedetails/?id=689540613) | Plank bridge with solid curved parapets, capped end blocks, medallions/scrolls and adjacent post lantern. | Lightning dominates foreground; no neutral palette or full dummy layout. |
| [Melee 689538972](https://steamcommunity.com/sharedfiles/filedetails/?id=689538972) | Continuous curved masonry ring with spaced capped posts, broad dirt surface and trees/rocks outside. | Gate and whole circumference are not shown. |
| [Hall roof 146791162](https://steamcommunity.com/sharedfiles/filedetails/?id=146791162) | Circular candle chandelier, radial timber roof, upper decorative circular window patterns and red patterned wall band. | Strong upward perspective, cropped roof and uncalibrated warm light. |
| [Hall staircase 147536650](https://steamcommunity.com/sharedfiles/filedetails/?id=147536650) | Stone arches under timber-railed stairs, red stair runner, floor rugs and map-rim curls. | Corroborates earlier views without establishing exact route dimensions. |
| [Bridge at night 131726186](https://steamcommunity.com/sharedfiles/filedetails/?id=131726186) | Second clear bridge angle, solid decorated sides, plank deck, post lantern and adjoining window/eave shapes. | Night palette and precise world orientation are not calibrated. |

The dormitory detail page names **Fable - The Lost Chapters**, identifies the
contributor as Ovenmuffins, and displays a posting date of April 25, 2013. That
predates Anniversary and strengthens the version check; it is not a measured
capture timestamp. The Guild minimap and visible room details strengthen location
identification. This is substantially more informative than GP15's Whisper
close-up, while leaving the complete room plan and total bed count open.

Five original-TLC Steam listing queries covered dormitory, Library, sleep, training
and Guild; seventeen candidate downloads were inspected. The dormitory query was
empty. The Library query offered the previously accepted burning Library and a
Library Arcanum interior, which was excluded as ordinary Guild Library evidence.
No neutral ordinary Library photograph was found in this bounded pass.

## Maze-study comparison against the existing generator

GP15's [ordinary study view](https://steamcommunity.com/sharedfiles/filedetails/?id=273468136)
and [second cutscene angle](https://steamcommunity.com/sharedfiles/filedetails/?id=247737302)
were re-inspected at full image resolution against `scripts/gen_structures.py`.
These are known references, not newly counted GP16 images.

| Observed original detail | Current generator | Bounded follow-up |
| --- | --- | --- |
| Round stone-framed window crossed by diagonal lattice in both views. | `lancet_window()` builds narrow pointed glass bays on five study-wall angles. | Survey one visible study wall and propose a coarse round/lattice block motif. Preserve shell support, stair clearance and openings; exact window orientation/scale remain adaptations. |
| Red rug with a spiral-pattern border over diagonal stone paving. | The study deck is dark oak and sparse study carpet cells are blue. | Survey exposed study floor cells, then design a bounded red bordered rug and muted stone finish outside furniture/routes. Do not infer the unseen full rug outline. |
| Tall continuous timber-framed bookcase below an upper timber gallery. | Study furnishing is a sparse two-block bookshelf stack; most cases are on lower floors. | Develop a supported continuous study case in a measured free wall bay. Case length, height and number remain chosen block adaptations. |
| Ornate high-backed wooden chair and cropped thick-topped pedestal table. | Study contains a lectern, enchanting table and bed; no corresponding chair/table group. | Survey a small circulation-safe furniture footprint. The bed and apparatus are unverified adaptations; the reference cannot prove they are absent elsewhere. |
| Red wall panels bounded by substantial timber uprights and a carved lower band. | Upper study shell uses the shared warm stone selection. | Consider a limited panel/trim material treatment after window and furniture footprint review. Native palette and lighting remain unrun. |
| Timber rail at a level change; gallery underside above shelves. | Current fixed three-floor circular tower and outside viewing balcony. | Keep this geometry until a complete source view supports stronger claims. Two cropped views cannot justify redesigning the whole stair/gallery topology. |

Any study pass must preserve Maze's `(46,12,70)` standing anchor, existing two-way
stairs/landings and the structural contract. Its evidence must compare the final
serialized geometry and retain explicit source-versus-adaptation limits. No blind
reload into an occupied Guild is authorized by these reference observations.

## Adjacent facility observations and priority

The new dormitory image supports a later bounded finish/furniture review: red
coverings, timber-framed red walls, narrow pointed windows and separate patterned
rugs are visibly stronger source cues than the present stone shell, wood deck and
blue bunk-room carpet. It does not establish the generator's separate common-room
floor or four designated bunk areas. Preserve the repaired GP13 stair and survey
before altering beds, floor topology or roof geometry.

The new archery view strengthens the deferred rail survey and shows that the
painted mountain scene and low castle target forms are distinct depth layers. GP15
restores a coarse scenic landmark, not those original forms or a complete rail.
The bridge views expose another clear silhouette difference: original broad solid
decorated parapets versus the current simple plank-bridge fence rails. Survey the
bridge approaches and cross-campus routes before introducing thicker sides.

These are queued visual comparisons, not implementation acceptance. GP15's proven
Skill callback defect still takes precedence: live target/lane preflight should be
fixed before expanding range furniture. Purposeful station arrival, requester
ownership and reactive dummies remain behavior work; screenshots cannot validate
them. Native lighting, actual walking/collision, NPC behavior and whole-facility
fidelity remain unrun.

# Chamber of Fate: neutral wall and paving details

GP14, 2026-09-12. A clearer original-TLC gameplay screenshot resolves details
that were hidden by the small combat views used for GP8: smaller pointed frames
inside the wall bays, medallions above plain rectangular panels, narrow colored
windows, and grey/ochre floor tiles. This pass brings those distinctions into the
existing Chamber through `gen_structures.build_chamber_of_fate()`.

## Reference and interpretation

The main reference is the 1280×768 original-PC Chamber screenshot on the
[TLC Steam screenshot listing](https://steamcommunity.com/app/204030/screenshots/?searchText=chamber),
[individual screenshot page](https://steamcommunity.com/sharedfiles/filedetails/?id=297703872).
The direct image, exact SHA256, inspected dimensions and limitations are recorded
in `screenshots/validation/GP14/chamber-reference-provenance.json`. The listing
identifies Steam app 204030, and the actual image shows classic models, HUD and
textures. Its precise patch and mod status are unknown. Individual detail-page
fetches currently return a generic Steam JavaScript shell; the saved public
listing contains the matching screenshot ID and image URL.

The neutral view shows empty lower panels at this story stage. A second close
view, screenshot 300473426 from the same original-TLC listing, shows one panel
filled with a story scene and another still plain. These are separate from the
narrow figurative colored windows. No external image pixels are committed or
imported into the pack.

| Visible source detail | GP14 treatment | Remaining approximation |
| --- | --- | --- |
| Nested pointed frames and rectangular lower panels | Recessed polished-andesite inner frames and divided plain panels within the existing eight outer bays | The 31-block room cannot reproduce the original fine paired tracery; bay count, proportions and block materials remain adaptations |
| Small circular relief medallions | Fourteen single-block carved marks in the seven bays outside the north aperture | Vanilla chiseled-stone motifs approximate a small carved ornament; they do not reproduce the original relief figures |
| Narrow figurative colored window strips between bays | Eight one-block-wide strips of green, yellow, brown and cyan glass, each six blocks high with opaque backing | Abstract color bands only; no figures, leadwork, matching scenes or exterior view |
| Muted grey/ochre tiled floor | 173 outer paving cells use polished andesite and packed mud in deterministic two-block groups | Palette, scale and grid alignment are adaptations; exact original tile layout and native light response remain unverified |

The floor assessment changes with the better source: GP8's uniform dark outer
paving over-read the battle lighting. The new grey/ochre distinction is visible
without changing its height. An initial smooth-stone preview was too bright;
the final grey material is polished andesite. This is a material comparison,
not a measured reconstruction of the original light level.

The existing high lamps and vault remain. The glass strips have solid backing
and add no light source. The protected purple/sandstone Cullis pattern remains a
visible mismatch. Exact window figures, changing narrative frescoes, decorative
relief subjects, full room proportions and neutral Bedrock lighting remain open.

## Exact scope and construction compatibility

The total comparison covers all 19,220 Chamber cells. Only 381 cell values
change: 173 floor cells at local y1 and 208 wall-detail cells at y2–9. Every cell
keeps its previous air/solid classification. No shell boundary, wall footprint,
standing height, roof, lamp location or anchor changes, and no RNG calls are
introduced.

All 4,419 independently protected GP5 cells remain exact: foundation, altar
radius ≤8.4 through y6, north approach through y6, and the glass/water containment
layers. Their digest remains
`431343b708bfb6b5c9a803bc8c787dc254d36f50e8abd5a197bd8e3b29b65a53`.
The full-circumference half-step altar still connects to all 116 surveyed outer
walk cells. The seven lamps, 177 water sources and 221 original glass base/rim
cells are unchanged; colored wall glass is additional material substitution in
already solid wall cells.

The companion compatibility export retains the exact preceding GP8 construction
plan in `scripts/data/guild_chamber_gp8.json`, alongside GP5. Recognized unfinished
builds resume their own enrolled plan; completed and legacy rooms receive no
decoration writes from this geometry pass. The exporter and actual-journal replay
tests are integrated separately. No migration of occupied rooms is implied.

## Evidence and checks

`screenshots/validation/GP14/render-chamber-details.py` reads the frozen GP8 plan
and the current owner to produce three matched pairs: open cutaway, low-angle
east bay and paving/altar crop. All six final images were inspected against the
neutral source. Nested panels and narrow strips separate the broad bays, and the
outer floor no longer merges into the dark wall base. The altar shape is exact
between the pair. Block scale, the small carved marks and missing figurative art
remain apparent limits.

These are offline flat-color views with actual slab halves. Other blocks are
cubes; glass is displayed as opaque color, and chiseled texture motifs are not
drawn. The views cannot establish native transparency, light propagation or a
matching player-height perspective. The comparison JSON records complete cell
hashes, changed-cell counts and unchanged route/containment counts.

The owner-only preflight passes 15 groups, including four new GP14 groups for
total scope, inset frames/marks, continuous backed strips and connected paving.
Independent fixtures alter an unrelated foundation cell, remove an inset apex
or carved mark, break a window/backing, and remove a floor tile; each fails its
intended check. Existing tests continue to check the entire altar circumference,
swept headroom, outer walk, shell closure and water containment. Three generated
asset/DATA/frozen-export gates run after coordinated regeneration; their results
and actual historical-journal checks belong to the integrated GP14 checkpoint.

Remaining native acceptance: compare wall, floor and altar views with original
TLC; inspect colored glass against its backing and the carved block textures;
walk the north approach and all altar sides; resume both historical enrolled
plans and reload occupied rooms without geometry or reward changes.

# Separate Guild archery scenery

GP22, 2026-09-13. New Guild structures now have a small stepped mountain and a
crenellated tower ahead of the painted range backboard. The original TLC scene
has scenery at several depths; the generated range previously had only the
single flat panel. This adds two shallow profiles while retaining the existing
targets, firing bay and adjoining paths. Native acceptance remains unrun.

## Reference and adaptation

Root reinspected the full original-TLC
[range view 141099874](https://steamcommunity.com/sharedfiles/filedetails/?id=141099874),
posted April 24, 2013. Ahead of the painted mountain panel are separate low
mountain shapes, crenellated castle/tower forms and dark painted window slits.
The larger foreground tower and smaller shapes behind it establish visible
layering. The curved platform edge and timber bracing remain further comparisons.
The crop does not establish exact dimensions, full range layout or perimeter.

The mountain occupies x80..82,z32 with column heights 1/2/1 from y1; it uses
purple terracotta and one white peak. The tower occupies x87..89,z33 with
heights 3/2/3, using light-blue terracotta and one black-wool painted slit.
Both are one block deep. Their positions, materials, number, proportions,
stepped outlines and painted slit are Minecraft adaptations. The slit is a
solid decorative cell, not an opening. Curved/tapered cutouts, painted texture
detail and the full set of original scenery are still absent.

The board stays at z30; z31 is its reserved walking bypass. The two props sit
at z32 and z33, beyond the active Skill target endpoint at z34.5. An earlier
forward-tower proposal at x89..91,z35 kept destinations reachable but overlapped
the existing east-door path. It was rejected; the independent negative fixture
retains that distinction between reachability and preserving the actual route.

## Scope and route checks

`build_guild_archery_scenery` is a final generator helper without RNG calls.
Exactly twelve former-air cells change. All other 395,268 campus cells and
every preexisting occupied cell and floor remain. Palette, states, random stream,
layout and anchors stay exact, including Maze (46,12,70) and its 678 surveyed
reservations. All targets, hay supports, firing marks, dummies, fletching table,
roofs, both south doors, bridges and the GP21 divider remain.

The conservative walking graph loses only the six decorative ground columns,
13,812 to 13,806 nodes. Every other node and reachable node stays, and all seven
complete gate routes keep identical coordinates. Eight local routes, three
firing-gap columns and nineteen swept body paths remain clear. Five actual
emitted Skill rays are checked with the retained lower-fence collision bound.
All thirteen future-arrival samples and twenty-seven prototype refusals remain.

The body sweep tests added full-block obstructions against existing paths with
radius 0.35 and height 1.9; it is a conservative offline model, not a native
movement simulation. The walking graph does not certify standing on decorative
terracotta/wool tops. The arrival proposal still supplies mocked below-base air
and requires native search/offset/event calibration. Existing occupied Guilds
are never rebuilt; reanchor continues to refresh coordinates only.

## Evidence and remaining work

The behavior regression passed before Guild-only regeneration. Independent
review compares actual committed predecessor and authored serialized output,
with route/collision negatives and six focused before/after schematics. Evidence
and exact command results are in `screenshots/validation/GP22/`.
All 55 base gates and 65 ESM syntax checks pass in the isolated reviewed-index
snapshot, as do all 12 focused archery groups and Guild diagnostics. A second
independent review repeats the actual-owner comparison and finds no blocker.
Only the Guild changes among 1,663 worktree pack files. Fresh C2 metadata records
its new asset hash; all 36 C2 PNGs remain byte-identical to GP21. All 282 selected
full-render PNGs also remain exact: the added profiles are occluded at those
distant angles. Only 26_archery_backboard changes among seven fresh documentation scenes;
the two wide Guild views and four interior views remain exact. Root inspected
the archery and both wide views, both Guild cards, the gallery and all six focused
views. GP22 supplies the next asset/documentation baseline.

The initial C2-copy helper incorrectly expected a changed Guild PNG, and the
following staging helper lacked its manifest. An initial diagnostic launch also
used a missing relative helper path. The final staging audit also found that
the first documentation comparison used older images retained in the GP21 snapshot
instead of GP21’s actual custom render output. Actual committed-blob comparison
corrects the initial three-image claim to one. These errors and corrections are
retained; no base validation gate failed and no production source changed during
the corrections. Shared full/documentation renderers simplify fences as cubes;
the focused schematics use thin approximate posts/rails. Neither is native proof.

The three bridge/map-hall/courtyard images found during DP9 are now indexed in
[GUILD_ONLINE_REFERENCES.md](GUILD_ONLINE_REFERENCES.md), bringing the supplementary
corpus to 30. Their app-204030 listings, matching direct image URLs and inspected
classic pixels support edition attribution. Posting dates remain unavailable;
the elevated panorama has pronounced camera distortion and cannot establish
proportions. External images and HTML remain ignored; only provenance and
observations are committed. Production scenery relies on 141099874.

Next compare platform edging and adjoining bridge/interior architecture. Preserve
target/ray/door access while improving the broader range silhouette. Native
lighting, collision, movement, two-Hero passing and saved-world acceptance remain
unrun. Renderer metrics and static pictures do not close Guild fidelity.

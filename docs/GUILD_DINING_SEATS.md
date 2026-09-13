# Guild dining seat spacing — GP24

Original TLC dining views [343658414](https://steamcommunity.com/sharedfiles/filedetails/?id=343658414)
and [236178734](https://steamcommunity.com/sharedfiles/filedetails/?id=236178734)
show separate short stools along decorated long tables. The generated Guild had
24 oak-stair seats touching along two continuous rows. GP24 retains every second
seat, giving the furniture visible gaps within its existing footprint.

## Source and adaptation

Both full images were inspected again for this pass. Their matching original-TLC
Steam app 204030 cards, direct URLs and SHA-256 values are recorded in
`screenshots/validation/DP10/reference-followup.json` and GP23's reference index.
External images remain ignored development references, outside the pack.
These views support separate seating, red round tops, carved table surfaces,
pale teal-bordered table strips, mugs and two internal stair runs. They do not
establish the complete room dimensions or original seat count.

Only seat spacing changes here. Six existing oak-stair seats remain on each side
at x38/x42, y1, z36/38/40/42/44/46. The number, exact spacing, orientation and
stock stair shape are Minecraft adaptations. Round red stools, table decoration,
the original stair architecture and complete room proportions remain unresolved.

## Owner and final geometry

The dining loop in `scripts/gen_structures.py` places seats on alternate iterations.
It does not clear blocks after generation. Consequently the existing later carpet
runner fills four vacated seats at x38/x42, y1, z41/43; the other eight vacated
seats become air. This differs from the earlier pure-air feasibility fixture.
All twelve changes occupy former seat cells. Table surfaces, supports, lanterns,
food, kitchen appliances, floors, walls, roofs and adjoining circulation retain
their existing owners. No new random calls, runtime anchors or saved-world
construction rules are introduced. Reanchor remains a coordinate refresh.

## Validation

All 56 base gates and 65 ESM syntax checks pass in the isolated reviewed-index
snapshot. Behavior regression passed before Guild-only regeneration. Only Guild
changes among 1,663 worktree pack files; all nine protected unrelated files stay
exact. Actual GP23/current generators reproduce their respective serialized
assets. Exactly twelve cells change, with all other 395,268 cells, palette/state,
metadata/layers, RNG, layout, anchors and 678 Maze reservations preserved.

All prior walking and reachable nodes remain: 13,806→13,818 walking nodes and
10,597→10,609 gate-reachable nodes. Seven complete selected gate paths retain
identical coordinates, and eight existing local routes pass. Independent body
checks cover six dining aisles and twelve new gap crossings in both directions,
with radius 0.4 and height 2.1 covering the eight current resident entity types.
They model carpet at 1/16 block and use explicit raise/translate/lower segments,
with a separate complete footprint-support interval survey. Four negative
fixtures detect blocked gaps, low headroom and missing support. Native carpet
step dynamics and actor navigation remain unrun.

The actual resident spawn helper preserves all twelve default spawn choices,
including Skill hall at (41.5,1,40.5), and all prior candidates remain available.
A removed seat adds one possible future Skill birth candidate at (42.5,1,39.5)
when earlier choices are unavailable or occupied. The new carpet at (42,1,41)
remains rejected as non-air. Forty-eight unavailable block/occupancy probes
refuse births. No resident is spawned or moved by this offline review, and no
runtime or saved identity behavior changes. Actual Skill ray/shot/arrival
harness outputs remain identical.

Fresh 36-asset C2, all 282 full-render PNGs, seven Guild documentation scenes
and three diagnostics pass. Only Guild's asset hash changes in C2 evidence;
all 36 C2 images, 282 full PNGs and seven documentation images remain exact.
Root inspected both cards, the gallery, both wide Guild views and four focused
decoded before/after views. Two independent plan views expose the room footprint.
The wide cameras hide this interior change; focused views supply the visual
comparison. GP24 is the next asset/documentation baseline.

The author helper initially assumed a uniform ceiling at y7; two existing
supports have underside y6. That assertion was corrected without production
changes and the original failure remains. Its initial report also duplicated a
JSON key, hiding the candidate-node count; original report/helper/output and the
corrected explicit counts are retained. Portable and missing-reference runs
pass without changing source, asset or viewed pixels. Exact raw lint output is
retained in JSON; its readable log removes only an extra terminal newline.
No base gate failed. See the original logs and correction notes under GP24.

Native walking, carpet height, stair collision, NPC navigation, lighting,
multiplayer and saved-world acceptance remain unrun. Offline graphs and images
do not certify any of those behaviors or whole-Guild fidelity.

## Next comparison

The largest visible adjoining differences are the original twin internal stairs,
red stool forms, decorated table surfaces and the hall's timber/red wall treatment.
The current upper dining dormitory has a complete floor reached through the
gallery bridge and riverside stairs. Replacing that circulation needs a separate
layout survey, coordinated owner changes and complete ascent/descent review;
the two photos alone do not establish its full dimensions.

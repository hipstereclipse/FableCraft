# Taller Guild bridge lamps — GP23

The eight existing lamps beside the two north-river bridges now stand on taller
dark posts. Their heads rise one block above the previous position, separating
them visibly from the low deck rails. This is a bounded original-reference
adaptation; the bridges still lack the original broad decorated parapets.

## Reference and scope

Original TLC [view 131726186](https://steamcommunity.com/sharedfiles/filedetails/?id=131726186)
shows a long dark lamp shaft beside a substantial capped bridge end. The head
stands above the parapet. Retained views 91147839 and 689540613 corroborate the
separate tall fixture. Root inspected the complete close view before authoring.
Perspective does not supply an exact lamp height, bridge width or passing margin.

The existing eight positions are retained: x58/68, z35/37/53/55. Each y2 lantern
becomes dark-oak fence and the same standing lantern is placed at y3. The lower
y1 posts remain. Exact count, positions, one-block rise, stock materials and
fence/lantern shape are Minecraft adaptations. No new light source is added.

Newly indexed TLC view 157299346 shows plank seams and continuous pale bridge
insets with dark ornament. It has no clear lamp and supplies no lamp-height
evidence. The seven newly indexed hall/bridge/dining/dormitory images bring the
supplementary corpus to 37; none establishes a complete measured floor plan.

## Routes, ownership and remaining defects

The existing `plank_bridge` owner in `gen_structures.py` makes the deterministic
change. All deck/slab approaches, bridge rails, bank floors, piers, water,
training targets, interaction anchors and saved-world construction retain their
owners. Reanchor still refreshes coordinates only; it does not rebuild an
occupied Guild.

The prior bridge audit rejected full-cube rails because they leave only one
block between their inner faces. An unchanged conservative walking graph cannot
certify retained native passing clearance. Uniform
widening covers bank routes and collides with an existing bollard/lantern near
the z54 bridge. Stock trapdoors introduce mutable barriers without calibrated
native collision evidence. This pass leaves those separate design questions open.

The focused body model conservatively bounds fence cells as complete horizontal
columns up to 1.5 blocks high and lanterns as full cubes. Passing that model is
offline evidence for the sampled paths, not native fence thickness, two-Hero
passing, pathfinding or lighting. The original capped ends, rising parapets,
carved pale inset panels and full bridge profile still need further work.

## Evidence

Independent actual-predecessor/current owner and serialized comparisons, route
and negative-fixture results, focused before/after views, required render deltas
and reviewed-index validation are recorded in `screenshots/validation/GP23/`.
All 56 base gates and 65 ESM checks pass in the isolated reviewed-index snapshot.
Five focused bridge groups and ten independent negative fixtures pass. Actual
DP10/current generators reproduce their respective serialized assets: exactly
16 cells change; all other 395,264 cells, palette/state/metadata, RNG, layout,
anchors, 678 Maze reservations and 981 water cells remain exact. All 13,806
walking nodes, 10,597 reachable nodes and seven complete paths remain. Eight
local routes, 19 protected body sweeps, ten lateral bridge sweeps, five actual
Skill rays and 13 arrival samples/27 refusals retain their results. These are
conservative offline bounds; native collision and passing remain unrun.

Fresh C2, all 282 full-render PNGs, seven Guild documentation scenes and Guild
diagnostics pass. Only Guild changes among the 36 assets/C2 images. Only its
card and places gallery change among 282 full PNGs; only the two wide Guild
views change among seven documentation scenes. Root inspected both cards, the
gallery, both wide views and all eight focused before/after schematics. GP23 is
the next asset/documentation baseline. Only Guild changed among 1,663 worktree
pack files, and all nine protected unrelated files remain exact.

Initial helper errors (inherited CRLF comparison, an untracked full-render PNG
baseline) and focused-image caption spacing were corrected without production
changes; original output remains. Exact raw lint output is retained in JSON;
its readable log drops only the extra trailing blank line. No base gate failed.
Native acceptance is unrun; legacy C3 remains 45 leaves and 7 done.


The adjoining dining audit finds 24 contiguous stair seats where the new original
views show separate short stools. A scratch removal of 12 alternating seats
preserves every old walking/reachable node and adds 12, with checked routes intact.
This is a spacing proposal, not authored dining geometry or a verified original
seat count/stool shape. See GP23/dining-followup.* before the next furniture pass.

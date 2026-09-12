# W3.3 visual review

Inspected actual-owner exterior and high-angle overview. Both show an open round
platform, continuous bright lava moat, raised protective edge, guarded north
causeway and four stepped basalt spires. There are no diagnostic removals in
these images. The platform route and initial dragon clearance are separately
checked against the actual voxel data; static images do not show runtime AI.

Two small [TLC guide shots](https://www.gamepressure.com/fablethelostchapters/the-final-battle/z624)
show reddish paving and a much stronger jagged volcanic backdrop. Partial visual
grade C for silhouette/palette: broad landmarks present, substantial differences
in surrounding cliffs, warmth, scale and detail. Floorplan/canon completeness
is ungraded because the references are tight combat shots. No engine pass.
Reference URLs, hashes and uncertainty are in reference-candidates.json.

Six regression groups pass. The first route fixture extended into the protective
south curb; the saved first-folly-tests.log is red. The corrected route ends at
z=42, and missing lava floor/bank, closed exit and high dragon collider fixtures
independently fail. Tests read the shipped 1.54×4.18 collider rather than assuming
a humanoid head height. Existing dragon AI/loot remains unchanged; no soul gate,
phased fight, confinement, mask choice, ending, or link from the Shrine.

Full all-category rendering outcome is in full-render-summary.json. All generated
views are offline evidence. Engine fluid behavior, combat and stairs remain unrun.

All 26 local validation gates and explicit spell/syntax checks pass. The full
pipeline exited 0 with 51 mobs, 55 item cards, 30 structures, 130 recipe cards
and 13 galleries. C2 separately covers all 33 structure assets and hashes.

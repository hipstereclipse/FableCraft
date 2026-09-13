# Read-only bridge/range candidate survey

Run `python screenshots/validation/GP20/bridge-range-survey.py` from the repo
root. The adjacent JSON retains exact cell materials/states, complete path
fixtures, source hashes and actual Skill harness output. The probe decodes the
shipped Guild asset and verifies it matches every cell of the current generator.
It changes no production source, saved world, generated file, anchor or RNG call.

Both wooden bridge centerlines at local z36 and z54 currently pass in both
directions: bank y1, x59 slab y1.5, x60..66 deck y2, x67 slab y1.5, bank y1.
No existing traversal defect was reproduced. The side fences leave a one-column
center lane, so native collision and two-Hero passing remain unrun; this survey
does not justify widening or rebuilding either bridge. Three independent exact
crossing negatives (missing middle deck, missing approach slab, blocked headroom)
fail the same route fixture.

The unoccupied cells at x80 and x92, y1, z34..44 (22 total) lie between the
existing range cornerposts. All have supported ground and clear current standing
volume. Filling just these cells with spruce fence **in a RAM-only fixture**
preserves six explicit local routes: both bridge runs, the behind/in-front board
bypass, x79 and x93 side bypasses, and the four-cell future arrival corridor at
x83..86,z39. Seven complete gate connections remain available: the two south
room doors, Skill mark, east junction, both Might marks and Will mark.

The actual production Skill station/shot harness passes on baseline and the
hypothetical fixture, including its ten edited/unavailable geometry negatives
and 29 crossed-cell negatives. The table, targets, dummy supports, firing mark,
board and all floors remain unchanged in that fixture. No route result is a
native walking test.

Recommendation: preserve bridge geometry. Retain the 22 cells as a feasible
collider footprint for a later reference-led rail decision; current air does not
prove the cells are unused by players. Exact original rail extent, material,
brace spacing and desired openings were not measured here. The other agent is
independently evaluating a supported interior material-only change; this survey
does not compete with that smaller candidate or authorize a new rail design.

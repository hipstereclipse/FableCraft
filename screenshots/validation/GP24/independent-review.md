# Independent GP24 dining review

No blocker was found in the bounded seat-spacing change. The comparison executes
the actual committed GP23 generator at
`4aed7cff4bdb6cecc706e2c4711067cab648d530` and the actual current generator, and
each output exactly matches its corresponding serialized Guild asset. Production
sources and pack assets are read-only throughout this review.

Exactly 12 of 395,280 cells change: the odd-z seats in the two existing rows
`x38/x42,y1,z37/39/41/43/45/47`. Eight become air. The four at z41/43 receive
red carpet from the existing later runner pass. The 12 surviving stairs retain
their positions, oak material and facing states. All other 395,268 cells,
including table, legs, three lanterns, cake, kitchen appliances, floors, upper
gallery/ceiling, doorways and all other campus fixtures remain exact. Palette,
states, secondary layer, entities, metadata, size, origin, RNG state, layout,
anchors and 678 Maze reservations remain exact.

The inherited walking graph grows from 13,806 to 13,818 nodes; gate-reachable
nodes grow from 10,597 to 10,609. Only the 12 vacated seat nodes are added.
Every previous node, reachable node and all seven selected complete gate paths
retain their coordinates. Eight prior local routes and six dining routes pass
forward and backward. The actual Skill-ray, shot and future-arrival harness
outputs remain identical.

The inherited graph treats carpet as passable at y1. The independent body checks
instead place feet on the actual 1/16-high carpet where present, using an actor
bound of radius 0.4 and height 2.1. All eight current resident entity types fit
within those bounds. Six dining aisles pass in both old/current layouts, and
all 12 newly opened crossings pass against the full final dining block volume
in both directions. Before crossing a height change, the sweep raises to the
higher surface, translates, then lowers when appropriate. All 12 crossings are
blocked by the original seat geometry in the baseline control.

An additional support survey divides each crossing at every exact x boundary
where the actor footprint starts or stops spanning a floor column. Every
constant-footprint interval has solid base-floor support. The maximum support
height change is 1/16, occurring in the two west-row carpet gaps; the two east-row
carpet gaps meet existing carpet on both sides. The model therefore does not
pretend that all carpet crossings start on an equally raised flat floor. It
still does not execute native carpet stepping, friction, navigation or actor
movement; small steps and the square body bound remain offline assumptions.

Four meaningful negatives are detected: restoring a stair into an ordinary gap,
adding low headroom that blocks the taller body, restoring a continuous stair
at a carpet gap, and removing the base floor beneath a new gap. These are
bounded independent fixtures, not a new permanent base test suite.

## Actual resident-helper consequences

The `skill_hall` home `(42,1,40)` is an unchanged surviving seat. Its actual
existing spawn helper therefore retains the usual nearby clear point
`(41.5,1,40.5)`. All 12 resident slots keep the same default result, and every
previous valid default remains available under the same controlled query result.
All 48 unavailable-block/entity checks continue to refuse a birth position.

The opened air gap at `(42,1,39)` adds one valid **future-birth** candidate
`(42.5,1,39.5)` to that existing search. The new carpet at `(42,1,41)` remains
non-air and is rejected by the current birth helper. A separate spatial query
with two fixed occupants demonstrates a real ordering consequence: the old
helper output is `(41.5,1,39.5)` and the new output is `(42.5,1,39.5)` when both
earlier side candidates are occupied. Both layouts retain the original safe
choice; the freed seat adds an earlier valid option. The mock performs the
actual helper's distance queries but spawns or moves no entity. Existing bound
residents, home anchors, journals, identity and Follow/Wait behavior are unchanged.

## Visual and reference limits

Original images `343658414` and `236178734` were inspected and their retained
hashes verified. Separate short red-covered stools are visible, with space
between them. The exact count, alternating block spacing, two row coordinates
and retained oak-stair chair shape are Minecraft adaptations. This pass does
not reproduce the round stool shape/material, decorated table and runner,
individual mugs, full room proportions or twin internal red stair runs.

The two independent decoded furniture plans were inspected. Their gap pattern
and four newly exposed carpet cells match the serialized comparison; shapes and
colors are schematic. The source author supplies separate decoded cutaways.
No original pixels are copied into tracked evidence by this review.

## Reproduction and provenance

Run from the repository root:

```sh
python tmp/conformance/gp24-independent/review.py --render
python tmp/conformance/gp24-independent/review.py --render --output tmp/conformance/gp24-independent/portable-run
```

`review.py` finds the repository from its own path, reads the committed baseline
with Python-owned `git show`, runs both actual generators into the ignored
`tmp/conformance/gp24-independent/owners/`, checks current shipped bytes, and
passes decoded voxel data to `resident-probe.mjs`. The Node helper never invokes
Git. Both helpers also work together when copied to
`screenshots/validation/GP24/`; copy `reference-reinspection.json` alongside
them, retain the sibling `resident-probe.mjs` name, and use the copied Python
filename in the same command. For example, if curated as `independent-review.py`,
run `python screenshots/validation/GP24/independent-review.py --render --output
tmp/conformance/gp24-independent/repeat`. Resource lookup stays beside the helper
while output goes to the selected directory. Generated comparison structures
still stay in ignored scratch. If the ignored original photos are unavailable,
the helper records that absence and retained provenance rather than failing;
available pixels are hash-checked without claiming new visual inspection.

`review.json` records exact inputs, full deltas, paths, body/support surveys,
resident results, negative fixtures, reference provenance and image hashes.
`review.log` and `resident-probe.log` are the final output. The first run passed;
its helper, summary and log remain as `review-initial.py/json/log`. A later
successful support-only expansion remains in `review-support-pass.json/log`.
The later addition supplies a separate actual-distance two-occupant case; the
original candidate-mask probes remain controls. A final portability pass adds
`--output` and optional original-pixel availability handling without changing
geometry assertions. Its output remains in `review-portable.log` and the
`portable-run/` directory. There was no failed geometry assertion or production
correction.

All native acceptance remains unrun. This spacing pass is not whole-dining or
whole-Guild conformance.

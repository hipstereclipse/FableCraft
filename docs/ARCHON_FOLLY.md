# Archon Folly — W3.3

Planned before implementation: owner `archon_folly`, ID `fc:archon_folly`,
49×18×55, weight 2, rock surface, dark theme. Foundation at y=0 retains the
scatter settlement contract. No Cullis or Demon Door; no structure chests and
an empty explicit loot table. One existing fc:jack_dragon at (24.5,3,30.5).

Platform center (24,27), radius 16, floor y=2. Lava annulus at y=1, radius
17.4..21.4, has a full solid floor and inner/outer retaining walls. A raised
lip guards the arena edge. North entrance (24,1,0) climbs two steps at z=1/2
onto a seven-wide causeway, joins the platform at z=15, and returns by the
same permanently open path. Four basalt spires frame the volcanic silhouette.

[C] architecture.md Northern Wastes and FullWorld §12 supply a lava-surrounded
rock arena for Jack's dragon form. Dimensions, railings, local geometry and
procedural rock placement are [B]. This POI is independently scattered: no
fixed world map, link through Bronze Gate, souls prerequisite, fight phases,
scripted landing/flight cycle, mask choice or ending. The existing dragon AI
is unchanged. Spawn clearance does not prove combat safety or confinement.
New weights affect future unvisited rolls; old region flags/structures persist.

## Verification and limits

Six automated groups check dimensions/palette/bounds, explicit scatter flags and
absence of structure loot, all lava floors and lateral retaining neighbors,
a five-wide dry route from the north edge through z=42, exact stairs, the actual
shipped dragon collider (1.54 wide × 4.18 high), a surrounding 12×12 landing zone,
and real rock-surface scatter with region idempotence. Independent missing-floor,
missing-bank, closed-exit and high-collision fixtures fail the corresponding checks.
The first route fixture incorrectly extended onto the south protective curb at
z=43; first-folly-tests.log retains that red result. The corrected route remains
inside the platform. No geometry was removed to weaken the perimeter.

The [TLC final battle guide](https://www.gamepressure.com/fablethelostchapters/the-final-battle/z624)
provides two small inspected shots: warm reddish arena paving, orange volcanic
surroundings and tall angular rock silhouettes. Our black platform and bright
lava ring capture the broad contrast, but a narrow moat, short stepped spires,
plain deck and open normal-world sky miss much of that scene. Partial visual
comparison grade C: required broad landmarks present, substantial palette and
silhouette gaps. This is not an overall canon or engine grade; the shots do not
show the whole floorplan. Provenance/hashes are in W3.3/reference-candidates.json.
All external reference bitmaps remain ignored and unbundled.

Raw /structure load emits blocks only. Natural scatter populates the dragon;
there is no fc:place handler. The dragon remains hostile and can fly beyond
this footprint; no arena confinement or campaign progression was added. The
existing entity loot table remains unchanged. Foundation blending fills below
y=0 and skirt shaping operates outside the footprint; neither intentionally
edits the lava basin. Fluid updates and real terrain interactions are unrun.

- [ ] New world: natural rock placement, terrain settling and no lava leakage.
- [ ] Walk in and out without jumping; inspect stairs, curbs and fluid collision.
- [ ] Dragon spawns without suffocation; inspect full animated wings/body clearance.
- [ ] Fight with melee/bow/Will; test flight, targeting, retreat and multiplayer.
- [ ] Leave/reload region: existing geometry and spawn initialization not duplicated.
- [ ] Inspect lava under load/unload and after terrain grading completes.
- [ ] Compare full arena layout and volcanic backdrop to verified original TLC shots.

Every engine check remains unrun; W3.3 is in-progress.

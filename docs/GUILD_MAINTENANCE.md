# Retired Guild approach and scarecrow repairs — GP7

GP7 removes two obsolete block-writing helpers from the ten-tick Guild
maintenance callback. Existing player floors, containers and structures in those
footprints survive when old completion flags are missing or false. New Guilds
already receive the usable approach and training clearances from the structure
generator. Evidence is under `screenshots/validation/GP7/`; all checks are offline.

## Reproduced defect

The frozen pre-GP7 `repairGuildDemonApproach` writes every intended floor and
clears the standing block without checking its existing type or provenance.
With no `fc_guild_demon_approach_v2` flag, a player diamond floor at local
`(66,0,90)` becomes mossy cobblestone and a chest at `(66,1,90)` becomes air.
The helper makes 92 writes and then marks completion. If the unrelated floor
at `(65,0,84)` is unavailable, it makes 91 writes without completion; another
pass erases a barrel subsequently placed in the already-cleared cell.

`clearGuildRingScarecrows` similarly removes matching hay/pumpkin blocks in
three columns without proving that the old generator placed them. Its completion
flag can be written despite unavailable cells. Matching material alone cannot
distinguish an original prop from player construction.

The new regression initially ran against the actual old maintenance callback:
seven of eight groups failed. Those failures include writes into player blocks,
repeat clears, obsolete flag writes and an uncaught obsolete-flag read error.
The baseline helper source, SHA-256 manifest, reproducible probe and red log
are retained in `screenshots/validation/GP7/baseline/`.

## Generated geometry and saved-world policy

Running the old approach helper against the final current `guild_hall` voxel
plan changes only seven cobblestone/mossy-cobblestone floor variants on the
east-bank spur. It fixes no floor support, standing clearance or bridge step.
All nine ring-removal cells and five island-removal cells are already air.
The generator therefore needs no geometry change or regeneration for this pass.

The final-voxel regression walks a cardinal graph from the east path through
both half-slab bridge aprons to the source threshold, and back. It also checks
the two-wide south walk, including its shift from columns 65/66 to 66/67,
the former prop volumes and the actual apprentice station columns. Independent
missing-floor and blocked-apron fixtures fail those route checks.

The retired properties `fc_guild_ring_scarecrows_removed` and
`fc_guild_demon_approach_v2` remain untouched in saved worlds. Neither a missing
flag nor an unfamiliar value creates migration authority. This pass provides
no legacy approach or scarecrow migration: old incomplete layouts stay as saved.
A blocked training station remains unavailable to the existing checked session
owner. Residents, anchors, rewards and progress are not reset or relocated.

A future legacy migration would need independently frozen historical geometry,
an exact bounded permutation comparison, whole-footprint preflight and durable
interruption handling before writing. A fingerprint derived only from today's
asset does not establish historical provenance. Even historical matching cannot
distinguish a player's identical replacement permutation from the original.

The separate terrain grading, ocean repair and skirt vegetation owners still
run under their existing guards. This is not a campus-wide preservation audit;
their saved-world behavior remains a separate review item. The cave construction
journal, fingerprinted portal aperture migration and registered Cullis-height
correction retain their own existing contracts. Chamber concentric steps, Maze
`(46,12,70)`, Guild bounds and portal source anchors remain unchanged.

## Validation and pending acceptance

`scripts/tests/test_guild_maintenance.py` is a new continuous-validation gate.
Its four Python groups include eight Node callback groups. The Node fixture
executes the actual maintenance interval and actual training owner; the two
retired helpers are evaluated if present, so their reintroduction cannot be
hidden behind no-op substitutes. Adjacent cave/terrain/skirt owners are mocked
and their continued invocation is checked; they are not certified by this suite.

Coverage includes foreign floors/containers/props, absent and existing flags,
unavailable cells, failed writes, repeat passes, reload, unreadable old flags,
unplaced Guilds, refused blocked training and successful one-time acquisition.
The baseline probe separately records the cosmetic-only final-generator delta.
Focused working-tree test, lint and syntax results are in `focused-results.json`.
The coordinator also ran all 40 gates successfully from the isolated GP7
reviewed-index snapshot; its command results are in `results.json`.

No rendering owner, structure asset or NPC asset changed. Existing GP5/GP6
rendered views remain applicable to the unchanged assets. The working-tree
dependency review in `unchanged-assets.json` records inherited differences in
`fc_mobs.py` and `fc_lib.py`; those differences are excluded from the isolated snapshot.
Final isolated-snapshot dependency equivalence and syntax evidence are recorded
separately in `additional-results.json`. These images do not prove
collision, navigation, content-log behavior or fidelity to the original game.

Live Bedrock checks remain unrun: load old worlds with missing flags and player
construction in these footprints; revisit after reload/chunk unloading; walk
the bridge and portal approach; and observe blocked/clear apprentice sessions.
This checkpoint does not close supplemental gameplay acceptance or alter C3's
historical 45-leaf denominator.

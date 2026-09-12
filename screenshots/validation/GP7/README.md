# GP7 offline evidence

The two obsolete approach/scarecrow maintenance helpers are retired. This pass
changes no generated geometry or assets. See
[GUILD_MAINTENANCE.md](../../../docs/GUILD_MAINTENANCE.md) for saved-world policy,
the bounded scope and remaining terrain/skirt review.

- `baseline/retired_helpers.js` and `source-manifest.json`: actual pre-GP7 helper
  declarations, with their SHA-256 and the supplied baseline commit provenance.
- `baseline/run_probe.py`: executes those frozen helpers against player blocks
  and current generator voxels; `probe-results.json` records destructive writes
  and the seven cosmetic floor changes on already-generated geometry.
- `baseline/guild-maintenance-red.log`: actual old maintenance callback fails
  seven of eight regression groups. `baseline/commands.json` records commands.
- `guild-maintenance-tests.log`: four passing Python groups including eight
  actual callback groups, final-voxel routes and independent damaged fixtures.
- `initial-route-fixture-failure.log`: the initial test assumed a straight path;
  the corrected independent survey follows the existing two-wide path's bend.
- `focused-results.json` and `focused-*.log`: actual focused working-tree command statuses and original logs. All 40
  isolated gates pass in the coordinator's `results.json`; `additional-results.json`
  records final snapshot syntax and rendering dependency equivalence.
- `unchanged-assets.json`: working-tree dependency review and existing GP5/GP6
  image hashes. Inherited `fc_mobs.py`/`fc_lib.py` differences are explicitly shown;
  those changes are excluded from the reviewed snapshot.

The callbacks and route graphs run offline. No live-world writes, Bedrock
walkthrough, NPC navigation, multiplayer or crash-persistence check ran.

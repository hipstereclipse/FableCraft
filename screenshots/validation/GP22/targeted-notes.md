# GP22 focused regression results

Command: `python scripts/tests/test_guild_archery_backboard.py`

The first focused run passed all 12 groups in 5.579 seconds. The six existing GP15 groups remain; six GP22 groups compare the actual current builder against the actual builder with only `build_guild_archery_scenery` disabled.

The GP22 checks prove exactly twelve former-air cells change, unchanged palette ordering/states and shared RNG state, unchanged raw indices for every other campus cell, unchanged floors and all previously occupied nearby targets/hay/marks/backboard/rails, and retained runtime-anchor contracts including Maze (46,12,70). Independent component and support checks find two separate grounded scenic forms with the authored low silhouettes.

The complete walking-node and gate-reachable sets lose exactly the six occupied scenery columns; every other node and reachable point remains. The z31 bypass, both south thresholds/aprons and all three firing-gap columns remain supported, clear and gate-reachable. Both south doors and the Skill station retain return routes to the gate.

Independent negative fixtures reject a floating peak, removed scenery floor, blocked bypass, each blocked south door, a fence through the firing gap and missing bypass flooring. Both actual before/current voxel adapters retain six emitted particles, ten direct failure cases and twenty-nine crossed-cell failure probes across the runtime's tolerated offsets. Existing frame/support/approach failures remain active.

Only `scripts/tests/test_guild_archery_backboard.py` was changed by the regression task. No generator, generated asset or validation-runner edit was made here. Native Bedrock movement, collision, lighting and visual acceptance remain unrun.

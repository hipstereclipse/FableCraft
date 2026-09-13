# Live Guild Skill practice checks — GP16

GP16 makes the background archer decline practice when its target, hay support
or firing lane has changed or cannot be read. The previous callback still drew
six particles and played its bow sound through a chest or toward a missing
target. That was misleading cosmetic feedback; it did not create a damaging
projectile. The working target and particle path retain their GP15 positions.

## Scope and ownership

The handwritten `main.js` owns `guildSkillLaneClear` and calls it before station
acquisition and again when the delayed shot releases. It checks the target block
and hay immediately below it, then the live ray from the apprentice's hand height
to the target. The short segment is intersected with each candidate voxel so a
grazing cell cannot be skipped by fixed-distance sampling. Every crossed cell
except the validated target must be available air. Unknown blocks and failed
reads refuse practice.

The existing `guild_training.js` owner still checks the current session token,
eligibility, dimension, displacement, station footprint, support and headroom.
Failure at release interrupts through that owner, including its cleanup retries
and same-session exclusion. A callback from an old session cannot interrupt a
later assignment. Neither the helper nor the shot restores player blocks,
creates an entity, awards rewards or changes saved resident/social identity.

No geometry, anchors, entity definitions, models, animation clips, particles or
generated assets change. The authored target at `(83,2,34)`, hay at `(83,1,34)`,
range mark `(83.5,1,39.5)`, scenic backboard and adjacent return routes remain
fixed. No generator regeneration or occupied-world migration is required.

## Reference and acceptance limits

GP11/GP15's inspected original TLC screenshots support the recognizable range
and painted scenic landmark. This live validation is a Minecraft behavior choice,
not a recovered original-game shooting rule. The six-particle visual drill,
background cadence and one checked station placement per session remain
adaptations. Player archery lessons, scoring, moving targets, purposeful station
arrival and requester-specific Follow/Wait ownership remain separate work.

Evidence and exact command results are in `screenshots/validation/GP16/`.
All 46 base gates, 62 ESM syntax checks, 33 runtime groups, six final-voxel
archery groups, fresh 35-asset C2/full renders and Guild diagnostics pass.
Independent source review found no blocker and passed 11,099 crossed-cell
negatives. All 70 structure assets/C2 images and 281 full PNGs match GP15.
The runtime tests exercise actual production callbacks at mocked engine
boundaries; the translated final-voxel harness checks the generated range and
independent changes to support, target and lane. Offline checks do not establish
Bedrock behavior. All native acceptance remains **unrun**:

- Watch a normal shot, then obstruct the lane or remove the target/hay during
  bow draw; confirm the pending sound/trail stops and roaming resumes.
- Talk, Follow, provoke, displace or unload the archer during the draw, including
  two Heroes and saved/reloaded residents; confirm interruption and ownership.
- Check actual bow facing, animation blending, particles, collision and lighting.
- Walk both adjoining doors and the gate-return route in a saved and new Guild.

The finite bow animation may finish after its effect is cancelled. Same-type
player replacements cannot be distinguished from authored blocks; the check
validates current types/clearance, not construction provenance. GP16 remains
in-progress until native acceptance is observed.

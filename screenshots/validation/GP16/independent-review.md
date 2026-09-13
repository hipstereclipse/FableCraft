# GP16 independent source and test review

Date: 2026-09-12. Reviewed production source and tests read-only. **No blocking
GP16 defect found** in the Skill preflight, delayed effect ownership or final-voxel
harness. This review did not stage changes. Native Bedrock acceptance is **unrun**.
The separate `door-followup-audit.md` records a pre-existing door recovery-guard
defect for a following DP milestone; it is not introduced by this Skill change.

## Source conclusions

The production diff adds only `guildSkillLaneClear`, its pre-acquisition gate and
its delayed-shot gate. The target must still be the authored target block over
hay; unknown, changed or unloaded cells fail closed. The delayed shot first calls
the existing session owner's `isActive(archer, token)`, so stale callbacks return
before inspecting geometry or interrupting a newer assignment. An active shot
then rechecks target, support and the segment from the archer's current location.
A failed check interrupts the existing owner and emits no shot particles or sound.
Successful rays retain six harmless particles and the original bow sound.

The clipping loop visits the segment's finite voxel bounding box and excludes
only the verified destination target block. Intersecting intervals must have
positive length. Coincident plane/corner crossings do not require a zero-length
side-cell visit; a segment parallel to and on a block face conservatively checks
both adjacent cells. Block-read exceptions and unavailable reads refuse the shot.
The helper is called with the fixed authored station before acquisition and only
after the owner checks a maximum 0.8-block displacement for a delayed shot. For
these production call paths a conservative independent axis bound is 28 candidate
voxels; no world-size scan is introduced. This boundedness claim concerns those
call paths, not arbitrary coordinates supplied by hypothetical new callers.

The session controller remains unchanged: failed placement preserves the existing
one-attempt-per-session rule, interruption invalidates the token, and failed stop
cleanup remains pending for retry. New preflight code does not change resident or
spouse properties, combat state, training tags directly, geometry, rewards or
teleport behavior. The scheduler's existing retain/cleanup path releases an active
Skill assignment that is no longer selected after a blocked-lane check.

The three Will functions (`guildWillLaneClear`, `showPracticeWill`,
`playWillPractice`) match GP15 exactly after CRLF normalization. Their concatenated
scope SHA-256 is
`c06c11df542a33bdc58966e2d3d3173ed20e70d1c8ef35704c79d49053b82a66`.
The 33-group runtime suite includes the existing Will interruption and stale-token
coverage. This confirms unchanged source/regression behavior, not live lightning,
movement or native collision.

## Independent validation

Commands run from the repository root, all exit 0:

```sh
node --experimental-vm-modules scripts/tests/guild_training.test.mjs
python scripts/tests/test_guild_archery_backboard.py
node --experimental-vm-modules tmp/conformance/gp16-door-audit/independent-ray-probe.mjs
```

- Actual main/session/emote tests: **33 groups pass**, including refused acquisition,
  delayed target/hay/lane/station changes, unavailable reads/throws, failed cleanup,
  later successful-session recovery, later-pulse rechecks, social/spouse/defence/
  rest/death/dimension/displacement cancellation and stale-token isolation.
- Final generated Guild archery suite: **6 groups pass**. The subprocess harness
  executes the actual `guildSkillLaneClear`, `showPracticeShot`, authored station/
  target declarations and session owner against final generated voxels. It checks
  10 independent damaged/unavailable cell cases, exact clear-ray endpoint and six
  particles, then 29 obstructed cells sampled along five permitted shifted rays.
  Geometry, adjoining routes and shared RNG remain covered by the existing Python
  suite. The helper is not stubbed to succeed.
- Independent exact-plane probe: **2,109 permitted displacement cases and 11,099
  crossed-cell obstruction negatives pass**. Its oracle collects all integer-plane
  crossing times and checks a midpoint of every positive-length interval; it does
  not duplicate production's segment/AABB clipping. Every oracle cell was inspected
  by the production helper and refused when independently replaced with a chest.
  The sampled sphere uses 0.1-block increments through radius 0.8. Maximum observed
  candidate box: **24 voxels**; maximum distinct block reads: **9**. This deterministic
  lattice supplements source reasoning and is not a claim of exhaustive real-valued
  engine coverage.

The final-voxel helper's original dense `clearRay` check remains a useful geometric
control; the added actual-owner negatives and independent plane-crossing probe
provide the behavioral evidence. No native target animation, pathfinding, visible
particle width, turning, saved-world interaction or physics was executed.

## Reviewed source and local evidence SHA-256

Byte hashes below are for the reviewed working files. Baseline comparison is the
real GP15 commit `17d1191e73d830ad4c809d2f6af62b724465eede`.

| Source | SHA-256 |
| --- | --- |
| `packs/Fablecraft_BP/scripts/main.js` | `cee13efcb444f0dc73c1c4b09eb7877df32a98ebc70f48d96b2fb75de728991d` |
| `packs/Fablecraft_BP/scripts/guild_training.js` | `baf0ff28090d771fb94b4884090e8cf45ba387aa9a6c3cbe7148082e9a70db41` |
| `scripts/tests/guild_training.test.mjs` | `cbaba3586cce86c7a8842e92c1d88bc28e1a9533679e81d64838743472387197` |
| `scripts/tests/guild_archery_voxels.mjs` | `6e070ca04716a6df889f6573ac68fdfbb8cf0746b1113375cfef744dd9fa87c6` |
| `scripts/tests/test_guild_archery_backboard.py` | `09af4238470aa50c6ac991f214afd9c85ec2462063fd16509c09d029fa687330` |

The following evidence is preserved in ignored `tmp/conformance/gp16-door-audit/`:

| Evidence | SHA-256 |
| --- | --- |
| `independent-training-tests.log` | `7eeee2d3186ffa7ea67ac34c7b0d6020537a04963beea8279d910dd0d7a875fa` |
| `independent-archery-tests.log` | `407a468b482ebba146f820f3cb2cdcdcc83a532d5695e9ded8c746ea747c506e` |
| `independent-ray-probe.mjs` | `e972d468f69339c79de365f554519d6d797bc95613f07b5ee1f600769f17d7e7` |
| `independent-ray-results.json` | `6e3489a97c6e0b5a4ddaa1cdd575667f716f299b41e1d4e553eb68b7c207e9a7` |

The independent ray probe and JSON result are also committed beside this review
under their original filenames for reproducibility. Run the probe from the
repository root; its retained source hash identifies the reviewed GP16 callback.

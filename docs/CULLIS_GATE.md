# W1.1 Cullis gate

[B] The procedural `fc:focus_site` now builds a weathered stone disc with blue inlay,
a flush sea-lantern core, eight carved runestones and four low broken rim markers.
It replaces the earlier obsidian monoliths and floating purple crystal. The saved ID,
13×10×13 footprint, weight, terrain classes and travel registration are retained.

[C] The local reference snapshots describe a round stone platform with blue magical
glow and walking onto a blue platform to travel: architecture.md (Chamber of Fate)
and UIofFable.md (Fast Travel). [G] visual_reference.md calls for muted earth tones and
saturated color reserved for important signals. These references informed the shape
and palette; the block design is an adaptation, not an extracted game asset.

[G] Original-2005 screenshot comparison remains pending. Image searches returned
mixed later-game/remaster material; the [Ancient Cullis Gate gallery](https://fable.fandom.com/wiki/Ancient_Cullis_Gate)
was not accepted as verified original-TLC visual evidence. No third-party image was
copied into a pack, and no visual canon grade is claimed from an unverified capture.

## Local layout and route

| Feature | Coordinates / extent |
| --- | --- |
| Arrival feet | (6, 1, 6), unchanged |
| Sea-lantern core | (6, 0, 6) |
| Stone disc | Radius up to 5.6 around (6,6), floor y=0 |
| Blue inlay | Radius 3.3–4.2, floor y=0 |
| Eight detector runestones | Cardinal offsets ±2 and ±3 from center, y=0 |
| Approach strips | Three blocks wide along x=6 and z=6, extending to all four edges |
| Low broken markers | (2,2), (10,2), (2,10), (10,10), above y=0 |

[B] Walk from the south edge (6,1,12) straight to (6,1,6), then out through any cardinal
approach. The disc remains flush with existing runtime arrival height to avoid
teleporting into a raised block. The off-axis markers do not obstruct those routes.
It has no interior, stairs, chests or local NPC spawns. Region adjacency remains the
procedural scatter/travel network; this change introduces no fixed world map.

The existing nearby-player Cullis particle loop supplies the animated glyph/soul glow.
Its blue/white appearance in the actual engine remains a manual observation; offline
renders show block geometry and palette only. Its V1 particle redesign is separate.
Runtime UI may still call these saved sites “Focus Site”; this work preserves labels
and registration, while the offline evidence card is titled “Cullis Gate”.

## Verification

`python scripts/tests/test_cullis_gate.py` checks identity/footprint/registration,
arrival headroom, four three-wide level walking routes and recognized renderer palette.
It also runs the actual `isCullisConfigured` JavaScript against generated voxel data:
the gate passes; missing core, missing runestones and unreadable terrain fail. The
same geometry suite fails against the pre-W1.1 owner, retained as negative evidence.

C2 byte/provenance checks link the emitted NBT to the current image and audit row in
`screenshots/structures/contract/`. The dedicated full structure render was regenerated.
The full all-category screenshot pass is run with fc_lib.SHOTS redirected to
`tmp/conformance/W1.1-full-screenshots/` before importing gen_screenshots; it runs the
normal main() pipeline without overwriting unrelated checked-in renders. Its audit,
log and this gate's full card are retained in `screenshots/validation/W1.1/`.

Visual inspection: the circular stone rim and blue ring read clearly; no unknown
magenta blocks or floating crystal remain. The renderer approximates slabs as full
cubes and does not prove glowing particles or Bedrock collision shapes.

Manual checklist (all unrun):

- Discover a newly scattered gate on grass, dark, rock, sand and snow terrain; walk
  all four approaches and check the disc meets the ground without buried edges.
- Confirm its core/glow, dwell activation, destination selection, arrival clearance
  and return travel with two discovered gates; test keyboard/controller flows.
- Reload and check old saved `fc:focus_site` travel records still work. Existing world
  structures retain their old blocks; only new placements use the new geometry.
- Compare with a verified 2005 TLC gate screenshot before assigning a canon grade.

# Remaining Guild facility work after GP15

Read-only audit of GP14 HEAD `569b3f2119390af2e19160ef52e2aa2072ff2cda` plus
reviewed GP15 source. This ranks the next three bounded follow-ups; none is a
newly introduced GP15 regression. No implementation or generated asset changed
for this audit. Native Bedrock acceptance remains unrun.

1. **Skill practice ignores changes to its target and firing lane.**
   **Basis: source-reproduced behavior.** The actual `showPracticeShot` callback
   with the actual training controller emitted six particles and one bow sound
   in all three mocked cases: clear lane, chest at local `(83,2,37)`, and missing
   target at `(83,2,34)`. Every case read only the three station cells
   `(83,0..2,39)`. There were zero entity/projectile spawns; this is misleading
   cosmetic practice, not a demonstrated damage defect. The corresponding Will
   callback already refuses blocked or missing targets. A focused follow-up
   should add Skill preflight and cancellation, preserving saved blocks and the
   existing session/Follow/defence rules.
   **Owners:** `packs/Fablecraft_BP/scripts/main.js` (`showPracticeShot`, line 935),
   shared `guild_training.js` lifecycle, actual-callback tests.

2. **Apprentices still arrive at training by one checked teleport per session.**
   **Basis: source-confirmed adaptation, not a recovered TLC schedule.**
   `guild_training.js:149` acquires a station with `tryTeleport`; the generated
   training group sets movement to zero. Release restores roaming in place.
   The existing lifecycle test explicitly checks one placement during a session
   and a second placement in the next session. The earlier repeated half-second
   teleport defect is fixed. Purposeful travel remains missing and is a larger
   contributor to the campus feeling like a school than another decorative
   recolor. Start with one resident approaching one reachable mark, with finite
   failure handling and interruptions; native navigation must then be observed.
   **Owners:** `guild_training.js`, the apprentice groups in
   `scripts/gen_behavior.py:454`, and resident identity integration. Preserve
   existing saved identities, Follow, defence and release semantics.

3. **The Will island has two inert block scarecrows instead of the original
   recovering training dummies.** **Basis: original reference plus source.**
   The original [Prima TLC guide, printed page 34 / PDF page 35](https://www.ogxbox.co.uk/media/com_eshop/attachments/Fable_The_Lost_Chapters_Strategy_Guide_Book.pdf)
   describes the southern island test with three dummies and timed recovery.
   That page was visually inspected again for this audit. The original PC Will
   screenshot in [the reference record](../../../docs/GUILD_ONLINE_REFERENCES.md)
   corroborates straw humanoid targets and a rocky water edge, but its framing
   alone cannot establish the total count. Current `scarecrow` calls author two
   fence/hay/pumpkin props, while GP9 only projects harmless lightning at one.
   A coupled prop/response pass should establish all three targets and readable
   recovery without claiming that background activity completes the player
   tutorial. Exact proportions and positions still need reference coverage.
   **Owners:** `scripts/gen_structures.py:2186`, target model/resource ownership,
   and the Will callbacks/contracts in `main.js` and their tests.

Adjacent changes reviewed: the GP15 54-cell board, its two side passages and
one-block rear passage; the actual Skill ray and station harness; the existing
six-group GP15 result; and both after-render crops. The recorded before/after
outside-board hashes agree. Door, training and gate-return routes are covered
by that conservative offline graph. No new adjacency blocker emerged. This
review does not turn the graph or flat-color images into native collision,
lighting or navigation evidence. Preserve the original neutral Chamber palette,
GP5 full-circle shallow altar steps, GP13 restored NE dorm stair, and Maze's
fixed `(46,12,70)` placement. The updated 19-image reference ledger now supports
a later Maze window/furnishing pass and some dormitory wall details; full room
proportions, bed layout and gallery/stair dimensions still need better coverage.

The additional probe ran with exit 0 using
`node --experimental-vm-modules tmp/conformance/gp15-followup-probe.mjs`.
It extracted the existing test fixture and invoked the production callback;
results are retained in ignored `tmp/conformance/gp15-followup-probe.json`.
No broader validation was rerun for this audit. Source SHA-256 at inspection:

| File | SHA-256 |
| --- | --- |
| `packs/Fablecraft_BP/scripts/main.js` | `c712c39be4aee51bc65e15248e1bd1e27f3cf7a667f7ccae3be53db430521b20` |
| `packs/Fablecraft_BP/scripts/guild_training.js` | `baf0ff28090d771fb94b4884090e8cf45ba387aa9a6c3cbe7148082e9a70db41` |
| `scripts/gen_behavior.py` | `05c75e6c53b275a6eb82e424cecb9fefd8327aa184d1a6ae05f5091be945ba7f` |
| `scripts/gen_structures.py` | `e6362334bc8d97715ac92c379a4db718032fcdaaa5d64241acfcf810c4793ae6` |
| `scripts/tests/test_guild_archery_backboard.py` | `09af4238470aa50c6ac991f214afd9c85ec2462063fd16509c09d029fa687330` |

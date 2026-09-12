# W1.3 Twinblade camp

Layout recorded before implementation. [B] Retain fc:bandit_camp, 33×13×33,
weight 9, grass/dark/rock surfaces, dark theme, two bandits, an archer and Twinblade.
Retain the existing chest loot table and four chests. No travel or riddle-door flag.
Only fresh placements change; saved region IDs remain unchanged.

| Feature | Local coordinates |
| --- | --- |
| Outer ring / entrance | Radius 15 about (16,16); gate x=13..19,z=31; approach to z=32 |
| Inner palisade checkpoint | x=9..23,z=2..13; south opening x=14..18,z=13 |
| Command tent | x=10..22,z=4..11; open south, closed north |
| Command chest / barrel | (14,1,9) / (18,1,9) |
| Fighting circle | Center (16,20), radius 4.5; floor y=0; no central fire |
| Three covered stalls | x=5..9,z=13..15; x=5..9,z=19..21; x=8..12,z=25..27 |
| Crew tents | x=22..28,z=13..17 and z=20..24, openings north |
| Watchtower ladders / deck feet | (6,1..7,7) and (26,1..7,8) / (6,8,8) and (26,8,9) |
| Campfires | (10,1,18), (22,1,18), outside fighting floor |
| Spawn feet | (12.5,1,18.5), (20.5,1,20.5), (16.5,1,27.5), (16.5,1,17.5) |

[C] Source snapshots: architecture.md, Twinblade paragraph; FullWorld §10;
visual_reference.md, Core Look. These call for inward gated camps, a large command
tent, a fighting circle, three stalls and campfires. [B] Compact ring geometry,
brown wool hide/canvas, red command trim and all dimensions are adaptations for
procedural scatter. No fixed Albion map, quest checkpoint logic or staged duel is
introduced. The lakeside setting and makeshift tavern gameplay remain scope gaps.

The old supply dump/cart, cage and extra tent clutter were replaced by the three
covered stalls and two accessible crew tents. Two watchtowers remain, with ladders;
the east tower sits farther inside the palisade so its approach is clear. The command
tent is brown hide-like canvas with red trim. It opens south toward the inner gate.

## Routes and runtime coupling

Enter at (16,1,32), pass the outer gate z=31 and cross the clear circle at (16,1,20).
Continue through the inner gate z=13 into the command tent at z=11. Stand at
(14,1,10) for the war chest and (18,1,10) for the barrel. The main route is five
blocks wide. Stall counter approaches are (7,1,13), (7,1,19) and (10,1,25); approach
crew chests at (26,1,15) and (26,1,22). Walk outside the inner fence and around the
crew tents to the north-facing entrances. Tower ladders are reached from (6,1,6)
and (26,1,7); climb to y=8 and step south onto their decks. Fires at x=10/22,z=18
are outside the cobble ring; the combat floor has two clear blocks overhead.

Runtime uses W1.2's optional mobSpawns table: two bandits stand around the ring,
an archer stands on the southern lane, and Twinblade stands on its northern floor.
This guarantees initial clear geometry, not boss arena confinement or staged combat.
The existing scatter loot table fills four chests and population runs once per saved
region. Barrel contents and stall trading are not newly scripted. No new cullis/door
flags or external location connections are registered. Raw `/structure load` only
places blocks; scatter must be exercised to verify enemies and rolled loot.

## Verification and provenance

Six test groups in scripts/tests/test_bandit_camp.py check stable registration,
bounds/palette/loot, two gates and correct tent entrance, flat fighting circle and
external fires, three stalls/four openable chests/ladders, connected interaction
routes, and actual runtime population on grass/dark/rock. The old owner fails.
The shared scripts/tests/poi_population.cjs executes actual maybePlace against
emitted voxel data; W1.2 retains its wrapper and tests. No mock duplicates the
placement implementation. The full scripts/validate.py suite now has 18 gates.

Screenshots under screenshots/validation/W1.3 are original generator renders.
Capture bandit_camp() with Vox.save patched, then use render_structure(v,yaw=-0.72,
pitch=0.65) for the south view. For the diagnostic cutaway, copy the Vox, clear
x=10..22,y=3..12,z=4..11 and x=22..28,y=3..12,z=13..24, and render with pitch=0.8.
The actual asset retains those roofs. The full all-category pipeline runs in isolated
tmp/conformance/W1.3-full-screenshots; C2 separately tracks all 29 structure outputs.

[G] A search located a [Windows TLC Twinblade battle screenshot](https://www.mobygames.com/game/19218/fable-the-lost-chapters/screenshots/windows/127441/).
Opening its page returned HTTP 403, so no reference pixels were inspected or copied.
Original-TLC screenshot comparison and canon grading remain pending. The current
renders clearly show two gate lines, a distinct command canopy, three stall roofs,
a cobble-bordered fighting floor and fires outside it. Their cube approximation does
not prove Bedrock collision, cloth silhouettes, lantern suspension or flame animation.
No in-world or canon A pass is inferred from the automatic appearance grades.

## Manual checklist — all unrun

- [ ] Discover new camps on grass, dark and rock terrain (including slopes); check
      outer grading and the supported southern entrance, then walk both checkpoints.
- [ ] Walk every chest/counter route, open all four chests and inspect rolled loot;
      enter the two crew tents and command tent without breaking canvas or fixtures.
- [ ] Climb both ladders onto the watch decks and descend safely; inspect ladder
      facing, canvas collision, lighting and fence shapes in Bedrock.
- [ ] Confirm the four enemies spawn clear of geometry; fight Twinblade in the circle,
      checking hitboxes, AI navigation and the off-circle campfire hazards.
- [ ] With two players, reload/revisit and confirm saved regions prevent duplicate
      placement/population/loot; existing camps retain their original blocks.
- [ ] Compare gates, hide tents, stalls and the fighting ring with verified 2005 TLC
      imagery; track lakeside setting, checkpoint quests and staged duel as gaps.

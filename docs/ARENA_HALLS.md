# W1.4 Arena halls

Layout recorded before implementation. [B] Retain fc:arena_ring, width 27 and height
12; extend depth from 27 to 41 for southern halls. Runtime STRUCTS and C2 manifest
must change together. Weight 5, sand/rock/grass surfaces and dark theme stay unchanged.
Keep the three pit enemies, add one existing trader for the preparation shop and
supply all four with local spawn coordinates. No travel or generic Demon Door flag.

| Feature | Local coordinates |
| --- | --- |
| Original amphitheatre | x/z=0..26; pit center (13,13), floor y=0 |
| South entrance corridor | x=12..14,z=21..40,floor y=0 |
| Waiting room | x=3..11,z=28..38; east doorway x=11,z=32..34 |
| Practice dummies | (5,1..3,30), (5,1..3,35) |
| Shop counter / trader feet | x=8..9,y=1,z=36 / (9.5,1,34.5) |
| Hall of Heroes | x=15..25,z=28..38; west doorway x=15,z=32..34 |
| Hall statues | (18,1..4,30), (22,1..4,30), (18,1..4,36), (22,1..4,36) |
| Stand access | west aisle z=17..19, x=6..1, stair y=1..6 |
| Pit enemy feet | (10.5,1,12.5), (16.5,1,12.5), (13.5,1,16.5) |

[C] Sources: architecture.md, Arena paragraph; FullWorld §8; visual_reference.md,
Core Look. These describe tiered seating, inward statues, waiting dummies, a shop
and adjoining Hall of Heroes. [B] Dimensions/materials and southern annex layout
adapt these to procedural scatter. The pre-existing gate comment is reversed:
gdir==-1 is the south gate, but the code bars it. Correct the north/south condition.

## Routes and behavior

Enter from (13,1,40) along the three-wide corridor to the open south pit gate at
z=21..26. The north beast gate remains barred. Turn west at z=32..34 to the waiting
room and east to the Hall of Heroes. Stand at (7,1,30)/(7,1,35) beside practice props,
(9,1,34) near the trader/counter and (10,1,37) beside the barrel. Walk the hero hall's
central aisle through (20,1,29)..(20,1,37). All routes connect to the pit center.

From (7,1,18), climb west through x=6..1 at heights y=1..6. Step north from x=3
onto the lower seating tier at (3,5,16), or finish the ascent and step onto the upper
landing (1,7,16). The four original inward-facing rim statues and their sword arms
remain; four new hall figures line its aisle. No extracted sculptures are used.

The existing fc:trader interaction dispatches to shopMenu (main.js) with the standard
stock, reputation checks and transaction behavior. This addition instantiates that
existing NPC; no new shop inventory, prices or progression authority are introduced.
The two hay/pumpkin dummies are physical practice props: no new hit scoring or training
rewards are implemented. No staged arena rounds, spectators or boss encounter logic
is added. Enemy confinement and NPC survival/navigation need manual review.

The existing arena chest-loot table remains unchanged; this structure emits no chests
(as before), so it currently rolls no arena chest rewards. The shop and barrel are
separate from loot initialization. Raw `/structure load` places blocks only; use
fresh procedural scatter to observe the three pit enemies and preparation trader.
New placements use depth 41 and a matching settlement envelope. Existing saved arena
regions retain their old geometry and records; this is not a saved-world retrofit.

## Verification and evidence

Seven groups in scripts/tests/test_arena_halls.py check the coupled manifest/runtime
rectangle, all landmark routes, open south/barred north gates, practice/shop props,
retained inward statues plus hall figures, stair directions/landings, and actual
runtime population on sand/rock/grass using emitted voxel data. C2's actual-source
placement suite also includes the arena and verifies terrain/loot dimensions and
saved settlement envelope. Base validation now has 19 gates. The old owner fails
the new suite. All manual observations remain explicitly unrun.

The south render captures arena_ring() with Vox.save patched, then calls
render_structure(v,yaw=-0.72,pitch=0.75). The diagnostic cutaway copies that Vox,
clears x=3..25,y=5..11,z=28..38, and renders with pitch=0.85. Actual roofs remain.
All images are original generator renders in screenshots/validation/W1.4; the full
all-category pipeline runs in tmp/conformance/W1.4-full-screenshots, and C2 separately
renders all 29 structure assets. No offline image is a Bedrock playtest.

[G] The inspected south view shows the retained amphitheatre, distinct southern halls,
clear corridor and west stair aisle. The cutaway reveals practice props and hall
figures. These support layout review only; original-2005 TLC pixel comparison and
canon grading are pending. Cube approximations cannot prove stair collision, NPC
interaction, lighting or actual statue appearance.

## Manual checklist — all unrun

- [ ] Place fresh arenas through scatter on sand, rock and grass, including slopes;
      inspect the extended rectangular terrain grading and approach from the south.
- [ ] Walk the corridor, both halls and pit; climb/descend the west stairs to both
      seating tiers and inspect statue/railing clearance and the barred north gate.
- [ ] Interact with the trader: buy/cancel, insufficient funds, full inventory and
      reputation refusal; use the barrel and inspect dummy collisions and lighting.
- [ ] Verify three enemies spawn clear in the pit, the trader in the preparation room;
      test combat navigation, NPC survival and two-player crowding in doorways.
- [ ] Save/reload/revisit and check no duplicate placement/population/loot; old arena
      regions remain unchanged and new placements use the larger spacing envelope.
- [ ] Compare with verified original-2005 TLC screenshots before assigning a canon
      grade; keep staged rounds, spectators and scored training marked unimplemented.

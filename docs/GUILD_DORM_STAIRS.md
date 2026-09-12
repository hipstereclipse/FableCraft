# NE dormitory top stair — GP13

The NE dormitory's existing staircase now reaches its upper bedroom floor.
Only one block changes: the final west-facing oak stair at local `(86,5,11)` is
restored after the deck opening and rugs are finished. The earlier staircase,
its carriage and post, bunks, deck, roof and all campus anchors stay intact.

## Before proof and minimal repair

`spiral_stair` originally authors five outer courses, ending at `(86,5,11)`.
The later y5 stairwell opening clears that tread together with the deck. Its
solid stone carriage survives through y4, but the highest remaining oak tread
at `(87,4,11)` reaches feet y5; the adjoining bedroom deck reaches feet y6.
There is no intervening y5 stair/slab in the NE room. The older full-block-rise
probe could classify this as reachable because it allowed a one-block jump.

The revised source captures the existing helper's returned outer tread list and
calls `restore_guild_dorm_stair_top` after furnishing. That helper reinstates
only the final outer tread with its original west-facing state. It is placed
after the rug loop so the new stair acquires no floating carpet. The former
inner top cell remains open; this repair certifies one continuous route rather
than claiming a completely two-wide native spiral.

The restored stair supplies feet y5.5 on its eastern half and y6 on its western
half. It joins the unchanged upper deck at z12. Complete paired Guild builds
differ at exactly `(86,5,11)` and have identical final RNG states and normalized
block/state hashes everywhere else. No global spiral helper behavior changes.

This affects newly placed Guilds. There is no geometry replacement or migration
for occupied old Guilds, and no change to progress, NPC identity, doors or Maze's
fixed `(46,12,70)` study position.

## Reference and model boundaries

The inspected 2005 Prima guide, PDF pages 34–36 / printed pages 33–35, describes
upstairs barracks and books and shows an upper-room stair/window view near Maze.
It does not supply measured geometry for this generated NE staircase. This is
a proved access defect in the Minecraft building, not a reconstruction of a
specific TLC staircase. Room count, bed arrangement, native materials and
whole-facility fidelity remain separate review work.
[Original TLC guide PDF](https://www.ogxbox.co.uk/media/com_eshop/attachments/Fable_The_Lost_Chapters_Strategy_Guide_Book.pdf).
Edition provenance remains in [GUILD_CAVE_LIFECYCLE.md](GUILD_CAVE_LIFECYCLE.md);
external pixels remain ignored and their page-render hashes are in GP13 evidence.

The focused test extends GP2's full/slab occupied intervals, two-block standing
headroom and maximum half-block rise with half-cell horizontal samples. A
straight native oak stair is represented by its bottom slab and upper half-block.
The test checks that this flight contains no same-height perpendicular stair
neighbors that would require an inner/outer corner model. Vanilla oak stairs
use rotation and upside-down states; current native listings also expose corner
state, without requiring a pack/API change here.
[Microsoft vanilla block listing](https://learn.microsoft.com/en-us/minecraft/creator/reference/content/vanillalistingsreference/blocks?view=minecraft-bedrock-stable).

This certifies a supported centreline and standing-height columns. Entity width,
automatic steering, actual native collision execution and carpet thickness in
the walking graph remain outside the model. The focused renders show stairs as
two boxes, slabs at half height and carpets at 1/16 height, with other furniture
simplified and flat approximate colors. They do not simulate engine lighting.

## Verification and remaining acceptance

[GP13 evidence](../screenshots/validation/GP13/) includes before/after stair and
bedroom cutaways. `dorm-stair-render-scope.json` records the one changed cell,
matching outside hashes, failed baseline ascent, successful forward/reverse
routes and exact crop/removal limits.

Six focused groups pass: exact one-cell/RNG scope; straight stair shape/half
heights; complete ascent/descent; a composed gate-to-upper-bedroom return route;
unchanged furniture/roof/post/Maze protection; and independent deleted-tread,
blocked-headroom and wrong-facing failures. The existing six Guild circulation
groups and 22 resident lifecycle/birth groups also pass.

- [ ] Native ascent/descent with auto-jump disabled, including both final turns.
- [ ] Native NPC collision/pathfinding and another Hero passing at the landing.
- [ ] Check carpet contact, bedroom interactions and the return route to the gate.
- [ ] Confirm occupied old Guild geometry and saved construction remain unchanged.
- [ ] Obtain clearer original sleeping-room views before changing room count or massing.

# Guild Will-island practice — GP9

GP9 gives the existing Will apprentices their own harmless background drill on
the Guild island. One eligible Will apprentice acquires the worn mark south of
the west dummy, raises both hands and sends four short blue lightning pulses
toward its pumpkin head. Might apprentices alone fill the sparring pair. A missing
Might partner no longer turns a Will or spare Skill apprentice into a swordsman.

## Reference and adaptation boundary

The original Xbox *Fable: The Lost Chapters* manual, printed pp XIV–XV (PDF page 8),
explicitly places Will practice on the island between two bridges and describes
magic-response dummies for lightning practice. Printed pp XVI–XVII (PDF page 9)
identify ranged Lightning as the first Will lesson. This is direct primary
support for the location, discipline and dummy response. The map on printed
pp XII–XIII identifies a distinct Will training area.
[Original TLC manual](https://www.gamesdatabase.org/Media/SYSTEM/Microsoft_Xbox/Manual/formated/Fable-_The_Lost_Chapters_-_Microsoft_Game_Studios.pdf).

The two anonymous Will residents, one-at-a-time assignment, 60-second drill /
120-second rest timetable, exact hand motion, quiet spell sound and harmless
particle effect are Minecraft adaptations. This does not implement the Hero's
Lightning lesson, Guildmaster instruction, scoring, mana use or graduation.
The current two block dummies, their facing and the island/bridge proportions
still need visual comparison with original TLC gameplay. A static pumpkin hit
with spark feedback does not establish the original game's reactive animation.

## Reproduced defect and bounded owners

The [baseline probe](../screenshots/validation/GP9/will-baseline-probe.mjs) runs the
actual GP7 reviewed scheduler and session owner at mocked engine boundaries. A
full Might pair leaves both Will apprentices without activity. Removing one Might
apprentice causes a Will apprentice to acquire the sparring role. The result,
source hashes and limits are recorded in
[will-baseline.json](../screenshots/validation/GP9/will-baseline.json).

`main.js` owns the new selection, pose and pulse callbacks. `guild_training.js`
adds `fc_train_will` to the existing shared cleanup contract; no new background
controller or behavior component group is needed. Existing Follow, conversation,
marriage and defence exclusions apply to the Will role. Release restores roaming
at the current position; it does not return or rebuild the resident.

The new generated standing column is local `(60,1,88)`, centred by the runtime
at `(60.5,1,88.5)`. `GUILD_LAYOUT.will_training`, `GUILD.training.will` and the
structure contract remain coupled. The target is the existing west dummy at
`(60,3,85)`, aimed at `(60.5,3.75,85.5)`. Its high aim clears the existing south
arm at `(60,2,86)`. The short ray checks air up to the already-validated pumpkin;
its hay torso must also remain present. The full apprentice footprint must have
an authored dirt floor and two clear standing blocks before checked placement.

The geometry owner authors one coarse-dirt support cell and standing clearance
for new Guilds. The runtime never repaves this mark or restores a missing dummy.
Old Guilds whose mark remains grass, whose target changed, or whose lane is
blocked simply decline Will practice. No missing flag authorizes a saved-world
migration. Existing residents keep their original IDs, roster slots, spouse
ownership, names and social progress.

`gen_emotes.py` adds a finite `animation.npc.will_practice` clip on the existing
NPC rig. `gen_resources.py` exposes that alias only on the Will apprentice.
`fc_mobs.py` removes its training-stick attachment while keeping the Might stick
and Skill bow. The shared owner keeps normal and married model/texture builds
consistent. Generated appearance outputs must follow these owners; exact output
deltas belong to the milestone's regeneration evidence.

## Interruption and harmlessness

Station acquisition retains the GP3 limit of one collision-checked placement per
resident per session, with no unchecked fallback or repeated placement after
failure. Walking to and from the island remains unimplemented. The second Will
resident stays available for ordinary activity unless it later qualifies for the
single station.

Each delayed pulse rechecks the session token, resident eligibility, dimension,
station position and support, dummy and beam clearance. Conversation, social
Follow/Watch, aggression, defence, rest, night, invalid handles, displacement,
missing support and modified props cancel pending feedback. Failed cleanup
remains pending and retries through the existing lifecycle. A callback from an
old session cannot release or render feedback for a later assignment.

The drill uses existing `wd:lightning_arc` and `wd:lightning_spark` particle assets
with explicit visible color/size/intensity variables. It never invokes the player
spell registry, creates a native lightning bolt or projectile, damages an entity,
changes a block, awards XP or drops an item. The cast pose lasts 1.4 seconds and
returns to neutral; native animation blending still requires engine inspection.

## Verification and remaining acceptance

The production training suite now passes 25 groups, including seven new Will
groups. They cover discipline selection, repeated practice without repeated
placement, blocked/missing/replaced support and targets, failed engine placement,
conversation/social/defence interruption, cancellation between pulses, reload
cleanup and stale callbacks. The new three-group Python suite executes the
actual station and ray preflights against final generated Guild voxels at a
translated world origin, rejects six independent changed/unavailable cells,
rejects numeric runtime-anchor drift and inspects generated animation/rig owners.

Commands and passing logs:

- `node --experimental-vm-modules scripts/tests/guild_training.test.mjs` —
  [25 groups](../screenshots/validation/GP9/will-training-tests.log).
- `python scripts/tests/test_guild_will.py` —
  [3 groups](../screenshots/validation/GP9/will-geometry-tests.log).

All live Bedrock acceptance remains **unrun**: NPC facing, beam visibility and
volume, hand alignment, collision, component restoration, actual Follow/Watch
and defence precedence, save/reload, two-Hero interruption, dusk/rest transition
and final island route walking. Inspect those before claiming an in-engine
training routine or complete TLC facility fidelity. Player lessons, purposeful
Guildmaster/Maze schedules and canonical staffing remain separate work.

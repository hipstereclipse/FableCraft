# Guild defence and offender attribution

GP4 implementation, 2026-09-12. Guild defence now selects identified offenders
from current local warrants and short, attributed provocations. One player's
payment or expiry no longer calms defenders while another eligible offender
remains. This is a multiplayer correctness pass over the existing Minecraft
defence system, not a reconstruction of TLC's tutorial or story reactions.

## Eligibility and lifecycle

`guild_defence.js` owns temporary player tag `fc_guild_offender`, defender marker
`fc_guild_defending` and the short provocation map. Existing bounty records remain
with their established owner. A warrant contributes eligibility while its player
is on Guild grounds; leaving through the Demon Door removes that eligibility
until the player returns. An attributed provocation can activate its nearby
defender for at most 320 session ticks. These short provocations deliberately
clear on reload; durable warrants are reconciled again from saved records.

The controller scans the campus and loaded Guild defenders near players. It
handles Guildmaster, Maze, the three apprentice types and Bowerstone guards with
the existing Guild-guard tag. It never creates, teleports or deletes residents.
Departed loaded defenders release combat when it is no longer needed. Initial
observation cleans legacy unowned attack state, stale aggravation tags and
tick deadlines. Failed cleanup retries before reactivation; a player target-tag
write failure suppresses active/new Guild defence until tags synchronize.

Payment first removes the payer's record, then reconciles all players. The
periodic expiry pass likewise updates saved warrants before its aggregate
reconciliation. Town guard recruitment and calming skip tagged Guild guards.
The defender controller interrupts drills and excludes defenders from boasting.

Expression attacks, failed theft/lockpicking, direct assault and protector alerts
carry the initiating player into the same hook. The death callback uses the
actual damaging entity or projectile owner. When neither resolves to a player,
it makes no player crime/kill attribution; it no longer guesses the nearest Hero.
This attribution correction also applies to non-Guild deaths handled there.

## Generated combat and social behavior

`gen_behavior.py` emits a priority-zero combat group requiring an actual player
with the offender tag. Target descriptions are reevaluated so a cleared tag
ceases to qualify. Old/direct social attack groups use the same restriction for
Guild residents; an ordinary untagged Bowerstone guard retains its prior policy.
Six entities were regenerated: Guildmaster, Maze, Might/Skill/Will apprentices
and Bowerstone guard. Models, animations, health, equipment and relationships
remain unchanged.

Follow/Watch groups survive defence. Their events reapply the active combat
group when the marker is present, preventing a social event from accidentally
removing an overlapping target component. Stop explicitly restores the guard's
original nearest-target, melee and hurt-by-target components; Bedrock does not
restore overridden base components merely by removing a group.
[Component removal](https://learn.microsoft.com/en-us/minecraft/creator/documents/entitybehaviorintroduction?view=minecraft-bedrock-stable#removing-components),
[readding a component group](https://learn.microsoft.com/en-us/minecraft/creator/reference/content/entityreference/examples/eventactions/add_component_group?view=minecraft-bedrock-stable).

Spouse ownership and saved progress are not reset. The existing Follow goal's
choice of player is outside this pass; retaining its group does not prove an
owner-specific follow system. Other towns' generic social targeting also remains
an open issue. Guild roster repair still counts nearby types and can duplicate
departed residents; no automatic deletion of those residents is introduced.

## Verification and remaining work

Fourteen focused tests execute the production controller, main/emote callbacks
and emitted component transitions. They cover two offenders plus an innocent
visitor, payment and expiry ordering, portal departure/return, short provocations,
reload, failed tag/event operations, invalid/departed residents, Follow/Watch,
town/Guild guard separation and projectile ownership. Eight generator groups,
18 training groups and the existing runtime suite also pass. Evidence for the
complete milestone is under `screenshots/validation/GP4/`. All 35 base gates
and explicit lint/spells/syntax/Guild diagnostics pass in the reviewed snapshot.
The full screenshot pipeline completed; all six defender cards are identical
to the prior static visuals. Representative cards were inspected, without
claiming that images establish behavior.

The independent cave audit is [GUILD_CAVE_REVIEW.md](GUILD_CAVE_REVIEW.md).
It records premature completion, missing maintenance, the unsupported library
threshold, a Cullis height mismatch and full-block hill rises. Those are
reproduced defects, not fixes included in the defence implementation.

Live acceptance remains **unrun**: observe actual target selection/dropping with
two offenders and an innocent visitor; pay or expire one warrant; leave/return
through the Library portal; provoke during training or Follow; reload/unload;
verify that NPC movement and combat goals resume correctly and inspect the
content log. Offline component/event models do not establish engine AI timing.

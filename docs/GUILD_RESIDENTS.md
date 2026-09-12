# Guild resident identity — GP6

Implemented 2026-09-12 in response to N5/N7 from
[GUILD_NPC_AUDIT.md](GUILD_NPC_AUDIT.md). A resident following one Hero away from
the Guild is no longer replaced while another Hero stays behind. Residence now
belongs to a saved entity ID, independently of the current scan, dimension,
activity or relationship. Death records a tombstone; proximity repair no longer
resurrects residents. These are offline-tested control-flow changes. Engine
loading, collision, movement and crash persistence remain **unrun**.

`packs/Fablecraft_BP/scripts/guild_residents.js` owns the registry, adoption,
spawn reservation and placement preflight. The handwritten `main.js` defines
twelve named slots, supplies world/entity operations, and uses the same owner
for founding and periodic maintenance. The generator's existing persistence
components remain unchanged; this pass regenerates no behavior, model or
animation outputs.

## Roles and adaptation boundaries

Guildmaster instruction, Maze's quarters and the three disciplines retain the
reference-supported role context documented in the GP1 audit. The anonymous
resident slots, two gate guards, permanent living Theresa in the Library,
generic trader, social behavior and background timetable remain the existing
Minecraft adaptations. This identity pass does not establish their canonical
2005 TLC presence, dialogue or routines. Whisper/player lessons, Will-island
activity and reference-led staffing remain open.

Safe birth placement also remains an adaptation: an authored home identifies a
voxel column; a new resident may spawn at a clear column centre within two
horizontal blocks of that centre, at the same authored height. This is a native
birth, not a teleport or a demonstrated walking route. Existing residents never
move during registration, maintenance or conflict handling.

## Durable state and native birth ordering

The world string `fc_guild_residents_v1` records schema 1, the founding base,
`fresh`/`legacy` origin and exactly twelve unique slot records. A bound record
contains the original opaque `entityId` and its provenance. The entity string
`fc_guild_resident_slot` contains the base coordinates and slot name; it does not
encode or replace the entity ID. Malformed data, unsupported schemas, repeated
slots/IDs, impossible state fields and changed founding bases refuse work.
Read/save failures retain pending work without authorizing another birth.

| State | Meaning and allowed action |
| --- | --- |
| `never` | A fresh founding has not attempted this slot's native spawn. A blocked/unloaded preflight can retry. |
| `unknown` | Historical residence is unresolved. Suitable observed legacy candidates may be adopted; missing residents are never synthesized. |
| `spawning` | Spawn intent was saved before native spawn. A returned ID/marker may finish bookkeeping; persisted intent alone never permits another native attempt. |
| `conflict` | Competing, wrong-type or inconsistently assigned slot markers reserve the slot. No inference or birth resolves it; a later single consistent marker can bind an existing entity. |
| `bound` | An original entity ID owns the slot. Failed lookup, removal, unloading or departure never clears it. |
| `dead` | A confirmed death for the bound ID is saved as a tombstone. No automatic resurrection or replacement occurs. |

Fresh registry enrollment must save successfully before the Guild structure is
placed. After placement/base persistence, population runs before the broad
decoration block; an unrelated Cullis/loot/portal failure cannot skip enrollment.
Maintenance runs every 200 ticks. It reconciles identities without requiring a
nearby Hero, but only attempts remaining fresh births while a Hero attends the
Guild. The terrain/occupancy preflight runs before the native spawn reservation.

For each permitted birth, the controller saves `spawning` before calling
`spawnEntity`. It consumes its in-memory permission before that call, including
calls that throw or return no valid handle. A returned entity is marked and its
original ID is saved. Failed marker/tag/save operations retry bookkeeping on
that entity without creating another one. A marker permits recovery after an
interrupted world-registry write. When a restart leaves only an unmarked spawn
intent, the slot stays reserved indefinitely: a missing handle cannot establish
that native creation never happened.

There is no atomic transaction between entity creation and world-property
saving. Offline failure injection exercises observable ordering and refusal
paths; it cannot prove durable save ordering after power loss. A native spawn
exception can leave an empty reserved slot even when no entity was created.
This pass provides no administrative reset or automatic respawn policy.

Microsoft describes entity IDs as intended to persist across world loads and
instructs callers to treat them as opaque. `World.getEntity` may return no handle
or throw; its contract does not establish that lookup failure means death.
These APIs and load/remove events predate the pack's pinned `@minecraft/server`
2.1.0 dependency. [Entity.id](https://learn.microsoft.com/en-us/minecraft/creator/scriptapi/minecraft/server/entity?view=minecraft-bedrock-stable#id),
[World.getEntity](https://learn.microsoft.com/en-us/minecraft/creator/scriptapi/minecraft/server/world?view=minecraft-bedrock-stable#getentity),
[API changelog](https://learn.microsoft.com/en-us/minecraft/creator/scriptapi/minecraft/server/changelog?view=minecraft-bedrock-stable).

## Historical adoption and preserved fields

An existing Guild with no registry starts with twelve `unknown` slots. It does
not acquire fresh spawning permission. Observation combines the campus scan,
loaded friendly entities near online Heroes in their current dimensions, load
events and direct lookup of bound IDs. These observations never prove that an
unobserved entity is absent from saved world storage.

Existing bound IDs take precedence. A single matching slot marker may enroll
an unbound slot. Otherwise historical `fc_guild_npc` or `fc_guild_guard` tags
provide adoption provenance before type-based inference. An unmarked nearby
trader or ordinary Bowerstone guard cannot occupy a Guild slot. A unique loaded
campus Guildmaster, Maze, Theresa or apprentice cohort may be adopted with
`legacy-inferred` provenance. These types suggest origin but cannot distinguish
original residents from summoned entities or every older repair duplicate.

An excess historical cohort remains unresolved rather than selecting one for
deletion. Duplicate/inconsistent definitive markers durably reserve the affected
unbound slot, including a fresh slot that would otherwise permit a new birth.
Existing bound IDs are never reassigned when extra claimants appear. Later
single-marker observation can select that existing entity without proving that
every competing claimant has ceased to exist; all extras remain untouched.
Unknown missing residents, unidentified original traders and existing excess
residents are intentional migration limitations.

Adoption adds only Guild identity metadata/tags. It does not reset
`fc:married`, `fc_spouse_player`, the player's `fc_spouses` IDs, `nameTag`,
love/social properties, gift cooldown, Follow/Watch groups, training, defence,
quests, warrants or player reward guards such as `fc_maze_gift`. No entity is
removed, killed, neutralized, teleported home or rebuilt by this controller.
Trader and guards can also be spouses; their identity preservation follows the
same rule as apprentices.

The existing Follow goal still selects a player without proving spouse-owner
selection, and Wait still restores normal random strolling. Retaining those
groups does not repair these separate behavioral limitations. The existing
[training](GUILD_TRAINING.md) and [defence](GUILD_DEFENCE.md) owners continue to
manage their own temporary state.

## Birth clearance and measured locations

The preflight requires an authored support-block type, air across the full
conservative 0.8-block footprint and two blocks of height (2.1 for Maze), and no
entity returned by a two-block-radius query. Unknown floors, missing chunks,
headroom obstruction and failed block/entity queries refuse that candidate.
The occupancy radius intentionally reserves more space than the resident
collider and can delay births near players, items or other entities. No floor,
headroom or furniture is modified. Native collision and gravity behavior still
need engine verification, including the dirt-path surface height.

The regression executes the production preflight against the final generated
Guild voxels and checks that its dimensions enclose every emitted resident
collider. Coordinates below are local to `fc_guild_base`. The independent column
checks have no entities; the sequential check presents all preceding births to
the same occupancy query in actual roster order.

| Slot | Authored home column (x,y,z) | Independent clear centre | Sequential clear centre |
| --- | --- | --- | --- |
| Guildmaster | 23,1,42 | 22.5,1,41.5 | 22.5,1,41.5 |
| Maze | 46,12,70 | 46.5,12,70.5 | 46.5,12,70.5 |
| Theresa | 26,1,23 | 26.5,1,23.5 | 26.5,1,23.5 |
| Trader | 5,1,46 | 5.5,1,46.5 | 5.5,1,46.5 |
| North guard | 10,1,39 | 11.5,1,39.5 | 11.5,1,39.5 |
| South guard | 10,1,45 | 11.5,1,45.5 | 11.5,1,45.5 |
| Might hall | 12,1,42 | 12.5,1,42.5 | 12.5,1,42.5 |
| Might ring | 101,1,61 | 101.5,1,61.5 | 101.5,1,61.5 |
| Skill range | 86,1,39 | 86.5,1,39.5 | 86.5,1,39.5 |
| Skill hall | 42,1,40 | 41.5,1,40.5 | 41.5,1,40.5 |
| Will Library | 26,1,24 | 26.5,1,24.5 | 25.5,1,25.5 |
| Will hall | 16,1,35 | 16.5,1,35.5 | 16.5,1,35.5 |

The old integer-coordinate births straddled four columns. Centering resolves
Maze's footprint without changing the audited `(46,12,70)` home. Guildmaster's
old birth overlaps map furniture, the guard posts overlap gate masonry and the
Skill hall post overlaps stairs, so their new births use adjacent clear columns.
Sequential occupancy moves the Will Library birth around Theresa. All twelve
remain possible without touching geometry. Existing residents at obstructed
locations remain unchanged; this is not a saved-world movement migration or a
repair of the furniture/post layout itself.

## Events, evidence and remaining acceptance

The independent `entityDie` callback initializes the saved registry before
recording a known ID's death. It runs for environmental and nonplayer causes
without depending on crime/XP attribution. `entityLoad` only observes identities;
`entityRemove` only forgets an in-memory handle. Microsoft explicitly includes
unloading among removal events, so removal never changes a bound record to
dead or vacant. [Removal event](https://learn.microsoft.com/en-us/minecraft/creator/scriptapi/minecraft/server/entityremoveafterevent?view=minecraft-bedrock-stable).

[resident-audit.json](../screenshots/validation/GP6/resident-audit.json) records
the inspected source hashes, all 22 focused test names and both measured birth
sets. [resident-tests.log](../screenshots/validation/GP6/resident-tests.log)
contains the actual passing run. Tests exercise production controller code,
the real founding/maintenance/death/load/remove callbacks and generated voxels.
They cover concurrent Heroes, departure/dimension change, unload/return,
tombstones, historical ambiguity, generic foreign NPCs, duplicate marker claims,
spouse/Follow preservation, corrupt data and injected persistence/spawn failures.
The existing 18 training, 14 defence and 20 cave groups also passed after runtime
integration; lint reports no errors and retains existing main-script warnings.


GP6 passes all 39 base gates from `tmp/conformance/GP6-reviewed-snapshot`, including
22 resident, 18 training, 14 defence and 20 cave groups. Base validation includes
ESLint and the spell suite; all 62 BP JavaScript files also pass ESM syntax checks.
The static Guild diagnostics reuse GP5 results with byte-identical dependency
hashes recorded in additional-results.json. The full screenshot pipeline completed
51 mobs, 55 items, 130 recipes, 32 structures and 13 galleries. All six representative
NPC card hashes match GP4; Guildmaster, Maze and Will apprentice were inspected.
No generated appearance outputs changed and no engine acceptance is claimed.

Live acceptance remains **unrun**: two Heroes separating and returning with a
spouse; actual chunk unloading/reloading and restart persistence; native spawn
clearance around the map, gates, tower and Library; movement and Follow/Watch
after adoption; environmental death and deliberate removal; invalid/missing
entity handling; content-log inspection; and interrupted save/crash recovery.
Static geometry and mocked callbacks do not establish engine AI timing,
canonical character behavior or overall Guild fidelity.

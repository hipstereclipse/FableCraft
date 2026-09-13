# Demon Door audit and Guild pilot contract

GP1 design audit, 2026-09-12. **Implemented pilot:** see [LIBRARY_ARCANUM.md](LIBRARY_ARCANUM.md)
for current DP1 behavior, migration, evidence and remaining limitations. The ranked
defects below describe the audited pre-pilot baseline. This document records the contract;
it is not an engine pass or a claim that DP1/DP2 are complete. The active queue is
`GUILD_DEMON_PRIORITIES.md`. Original 2005 TLC is the reference target.

## Verified Guild identity

The Guild's door opens when the Hero lights the **Lamp** and leads to **The
Library Arcanum**. The Elixir of Life is in its chest; Making Friends is on a
table; Book of Spells and the Howl Tattoo are in bookshelves. The original TLC
area-item walkthrough identifies all four locations, independently corroborated
by the PC walkthrough's explicit enter/explore/return sequence. Neither source
describes an opening-time inventory or XP payout.
[TLC area-item FAQ](https://gamefaqs.gamespot.com/xbox/929075-fable-the-lost-chapters/faqs/39945),
[TLC PC walkthrough](https://www.gamerstemple.com/games7/000926/000926g209.asp).

The contemporary Prima TLC guide also identifies Lamp → Library Arcanum → Elixir
of Life. Its assertion about the elixir's precise health effect is not adopted
as a Minecraft balancing specification.
[Prima TLC guide](https://www.ogxbox.co.uk/media/com_eshop/attachments/Fable_The_Lost_Chapters_Strategy_Guide_Book.pdf).

The destination's library-in-a-grove, bookshelves, chairs, small pond and
butterflies are described by the local architecture reference and corroborated
by the location article. These support features and atmosphere, not exact room
dimensions or inferred camera geometry. The later [reference review](LIBRARY_ARCANUM_REFERENCE_REVIEW.md) inspects one
2005 guide gameplay image. A matching player-height view, complete room layout
and footage comparison remain required.
[Library Arcanum](https://fable.fandom.com/wiki/The_Library_Arcanum),
`docs/references/fable-tlc-expert/architecture.md`, Guild section.

Use stable archetype `guild_library_arcanum` and stable instance `guild`.
Light activation near the face is the challenge. A held vanilla lantern plus
an explicit use action may stand in for the Lamp in a bounded pilot; label that
as the Minecraft adaptation, do not imply mere ownership solves the original
challenge. No lantern is consumed. The existing `fc:elixir_of_life` can serve
the main reward. Named book/paper pickups may represent the three minor
collectibles until their original item systems exist; these are explicitly
representations, not reproduced book text or a working tattoo unlock.

## Ranked baseline defects and ownership

| Priority | Defect | Owner and consequence |
| --- | --- | --- |
| P0 | Guild door selects an invented challenge from coordinates | `main.js:doorPersona`; Guild currently has no stable canonical identity |
| P0 | Opening immediately gives items/XP; no destination/return | `openDemonDoor`; required exploration experience absent |
| P0 | Open state and persona are replaceable-face properties | `fc_door_open`, `fc_door_idx`; entity replacement loses payment/unlock history |
| P0 | Two outstanding forms can both consume and award | `demonDoorTalk`/`doorRiddle`; no state reread/transaction lock at acceptance |
| P0 | Guild mouth has solid crag directly behind it | `guild_hall`; mouth only clears z=96, side lamps occupy the opening |
| P1 | Face move is hardcoded +z, retains its collider | `animateDoorOpening`; no general approach normal or clear aperture contract |
| P1 | Scatter's initial face and saved anchor differ by half a block | initial `(cx+.5,z+5.5)` vs persisted `(cx,z+5)`; replacement can select a different persona |
| P1 | `fc_doors` truncates to latest 64 records | `recordDemonDoor`; old arch maintenance silently stops |
| P1 | No dimension in old registry | maintenance assumes supplied Overworld; future cross-dimension identity unsafe |
| P1 | Face remains pushable/leashable, ordinary physics, small generic collider | `gen_behavior.py` door branch, inherited components; slab is visually 2x3 blocks but collider .7x1.9 |
| P2 | Static story faces and scatter personas have unrelated challenge names/rewards | catalogue and landmark integrations require explicit mapping, never a fallback riddle |

Data owner is `scripts/fc_data.py:DEMON_DOORS`; exporter is
`scripts/gen_behavior.py:emit_script_data` (the function owning the `demonDoors`
entry), producing `packs/Fablecraft_BP/scripts/fc_gamedata.js`.
Entity owner is its `behavior == "door"` branch; face mesh is
`scripts/fc_mobs.py:plan_demon_door`; resource animation/controller generation is
`scripts/gen_resources.py`. Do not hand-edit generated outputs.

### Existing catalogue compatibility

Preserve the eight existing table entries and their order for saved
`fc_door_idx` values. Append separate explicit canonical definitions or export
a keyed canonical map. The coordinate formula is not a permanent identity.

| Existing ID | Current challenge/reward summary | Audit disposition |
| --- | --- | --- |
| gourmand | Five pies; Wellow's Pickhammer and coins | Invented; do not map to Guild or Arboretum |
| warrior | Multiplier 14; Harbinger | Resembles Greatwood Caves challenge but has wrong reward; preserve legacy contract |
| judge | Goodness 500; armour | Unverified adaptation |
| corrupted | Evil -500; armour | Unverified adaptation; not the canonical Arboretum reward |
| hoarder | Fifty coins; Orkon's Club and keys | Unverified adaptation; not the Necropolis key challenge |
| moonlit | Night multiplier 5; Avenger | Unverified adaptation |
| riddler | Clock multiple-choice riddle; keys/grimoire | Invented; never a story-route substitute |
| arboretum | Renown 1000; Solus and elixir | Incorrect canonical name/challenge/reward association |

The TLC area-item FAQ specifically places Wellow's Pickhammer behind Greatwood
Gorge's evil-act Arboretum, and Cutlass Bluetane behind the multiplier door in
Greatwood Caves. It also identifies Nostro's onward Graveyard Path as a story
passage. The Guild pilot does not relabel or silently change saved scatter
challenges. Lychfield's static face stays a story gap until Nostro's equipment
and route sequence exists. Greatwood Gorge's static face likewise awaits its
own verified integration.
[TLC area-item FAQ](https://gamefaqs.gamespot.com/xbox/929075-fable-the-lost-chapters/faqs/39945).

For new scatter integration, assign an immutable door-instance ID when the arch
is registered; save archetype, source dimension, precise anchor and orientation
there. Existing scatter migrates its observed `fc_door_idx` once. Do not recompute
from a moved entity, change modulus by appending a row, or deduplicate merely by
persona. Keep unrelated procedural generation intact.

## Pinned Bedrock API decision

The repository manifest declares `@minecraft/server` **2.1.0**, `server-ui` 2.0.0,
minimum engine 1.21.100. No local `node_modules/@minecraft/server` declarations
were installed at this audit. A manifest version is not evidence of a running
engine; no engine connection or live content-log verification occurred.

Current Learn pages describe APIs newer than that dependency. The official
changelog adds `DimensionRegistry` and startup `dimensionRegistry` in **2.8.0**,
`TickingAreaManager` in **2.6.0**, and `Dimension.isChunkLoaded` in **2.3.0**.
`getPackStructureIds` is also 2.8.0. Therefore the pilot must not call them under
2.1.0. Current custom-dimension documentation is not proof of older support.
[Microsoft server changelog](https://learn.microsoft.com/en-us/minecraft/creator/scriptapi/minecraft/server/changelog?view=minecraft-bedrock-experimental).

Use supported Overworld storage. `world.structureManager.place` accepts a pack
structure ID and queues placement in unloaded chunks; its return is **void**,
not a completion promise. `get` documents memory/world structures and should
not be used as the sole existence test for a pack structure.
[Microsoft StructureManager](https://learn.microsoft.com/en-us/minecraft/creator/scriptapi/minecraft/server/structuremanager?view=minecraft-bedrock-stable).

Use a named `/tickingarea add <from> <to> <name> true` lease, then poll actual
blocks through `Dimension.getBlock` with bounded retries. The command needs
cheats/game-director authority; report a failed load and leave the player at the
source when unavailable. Never remove unrelated ticking areas. The older
command supports preload; do not substitute the later manager API.
[Microsoft tickingarea command](https://learn.microsoft.com/de-de/minecraft/creator/commands/commands/tickingarea?view=minecraft-bedrock-stable).

`Entity.tryTeleport` has been stable since server 1.3.0 and returns a boolean.
Use `dimension`, `checkForBlocks: true`, safe facing and zero velocity; inspect
the boolean and resulting location. Floor and headroom checks remain our
responsibility. Preserve the return ticket until travel success is confirmed.
[Microsoft 1.20.10 update](https://learn.microsoft.com/en-us/minecraft/creator/documents/update1.20.10?view=minecraft-bedrock-stable),
[Entity](https://learn.microsoft.com/en-us/minecraft/creator/scriptapi/minecraft/server/entity?view=minecraft-bedrock-stable),
[TeleportOptions](https://learn.microsoft.com/en-us/minecraft/creator/scriptapi/minecraft/server/teleportoptions?view=minecraft-bedrock-stable).

World dynamic properties store state independently of faces; player properties
store durable return tickets. Validate parsed JSON/version/finite bounds before
use. Keep the behavior-pack header UUID unchanged so the existing progress
namespace remains associated with the same pack.
[Microsoft World](https://learn.microsoft.com/en-us/minecraft/creator/scriptapi/minecraft/server/world?view=minecraft-bedrock-stable).

## Isolated storage and structure contract

Pilot allocation: Overworld cells start at `(600000,272,600000)`, spaced 128
blocks, with 64 columns and a bounded maximum of 4096 allocated cells. Bounds
and coordinates are Minecraft design choices, not Fable measurements. Persist
the chosen cell before building; occupied candidates can be skipped without
changing a room that has been visited. Do not assume distance proves a space
is empty: load and scan **every** block in the 49x28x49 target volume for air
before first placement, time-sliced to avoid watchdog stalls. Reject occupied
volumes without clearing them. Check player/entity presence too. A stable cell
record reserves it against simultaneous requests.

Pilot is one canonical Guild room. Future doors receive separate instance cells
even when they share an archetype. No room is added to `STRUCTS`, ambient loot
or the Cullis network. Exclude allocated realm bounds (plus a margin) from
scatter and ordinary local encounter/training/quest progression. Realm state
and actual position both matter after death or external teleport.

| Contract field | Local coordinates / requirement |
| --- | --- |
| Structure | `fc:library_arcanum`, version 1, **49x28x49** |
| Floor | Contained base y0..1; walkable grass/paving y2; normal feet y3 |
| Arrival | `(24.5,3,7.5)`, facing `(24.5,4,18.5)` |
| Return opening | x23..25, y3..6, centre plane z3.5; throat z3..9 clear |
| Main reward | Empty generated chest block `(24,3,35)`; runtime seeds one elixir |
| Minor discovery sites | Empty containers `(16,3,28)`, `(32,3,28)`, `(16,3,34)` for table/book/book respectively |
| Atmosphere | Original library grove with bookshelf bays, chairs, desks, mature trees and enclosing rocks |
| Pond | Small contained basin around `(11,2,17)`; dry walking loop bypasses water |
| Exploration | Three-wide connected dry paths from arrival to reading bays, main chest and return |
| Isolation | Enclosed foundation/perimeter and concealed upper containment; no openings into surrounding terrain |

The physical walk/dwell portal must remain primary. Original particles/sounds
can signal the opening; use no extracted Fable assets. A return interaction may
be an emergency backup, visibly associated with the return arch.

Guild source keeps its saved `fc_guild_door` coordinate. The implemented generator
clears x65..67, y1..4, z96..104 and moves lamps outside the throat. The initial
z96..98 design sketch above the baseline was insufficient: later inspection found
the full nine-block crag depth. The bounded fingerprint migration and its
same-material detection limit are detailed in [LIBRARY_ARCANUM.md](LIBRARY_ARCANUM.md).
The campus and existing stair geometry are never reloaded by this pilot.

## Durable state and transitions

Keep the runtime in an owned module, e.g. `scripts/fc_demon_doors.js`, with an
explicit adapter from `main.js`. Separate deterministic mapping/geometry/state
helpers from Bedrock effects so failure paths can be tested independently.

World record per instance: `schema`, immutable `id`, `archetype`, precise
`source {dimension,x,y,z,normal}`, `unlocked`, `legacy {status,idx}`,
`room {cell,version,phase}`, and individual `rewards {seeded,claimed}`.
Use bounded records or one property per door; never silently truncate a
registry of still-existing doors. Cache is disposable; properties are authority.

Player return ticket: `schema`, `doorId`, `realmCell`, precise source dimension
and safe source position, facing, and `phase` (`entering`, `inside`, `returning`).
The ticket snapshots the actual source for this visit; a nearest-door search
and the last player's shared return anchor are both incorrect. Prevent nesting
while a ticket is active. Persist a new ticket before attempting entry.

Shared-world semantics: anyone may use an unlocked Guild door; each physical
reward is available **once per door instance for the world**. This retains the
baseline shared-door reward policy rather than introducing a per-player farm.

1. Re-read authoritative state when a pending answer/use resolves. If already
   unlocked, do not check/consume/reward again. Guild light use consumes nothing.
   Any later consumptive challenge needs a transaction journal and per-door
   synchronous lock, with inventory success checked before unlock commit.
2. Commit unlock independently of room generation. Play opening; move the
   face out of the whole aperture or remove it after the animation. Maintenance
   must represent unlocked state instead of respawning a closed obstruction.
3. Lease destination chunks, preflight unused volume, reserve cell and place
   structure. Verify expected sentinels, all route samples, every required
   container, arrival floor/headroom, and exit before setting room ready.
4. Seed reward containers while the room is inaccessible. Record seeded state
   before enabling entry. Containers start empty in the asset. Repeated visits
   never run seeding and never replace a ready room.
5. After dwell, verify destination again, save return ticket, then tryTeleport.
   False/throw leaves the player at source and clears only an uncompleted entry
   ticket after position reconciliation. Success sets ticket inside.
6. In the room, players take real container items. Native container transfer
   owns inventory movement; do not additionally give the same item in script.
   Observe depletion to update claim flags, but missing claim observations
   must never authorize replenishment. Empty/missing visited containers remain
   depleted and are reported for geometry repair.
7. Return loads/probes the saved source and uses a clear approach tile outside
   the portal, facing away. Clear ticket only after success. On obstruction,
   search a small bounded set of clear source-approach alternatives; do not
   carve terrain or silently send the player to a different door.

Persist seeding/build phases before any room becomes accessible. DP9 supersedes the original unvisited-only retry rule: unknown legacy placing
and interrupted placement/seed intents never authorize replay. Saved success
receipts permit only verification and the next unperformed phase. Do not reset
a visited room. See [the Library preparation contract](LIBRARY_ARCANUM_PREPARATION.md).
If a ready room is damaged/missing, permit recovery return and report the room
unavailable; reconstructing it requires a separate versioned repair that keeps
all seeded/claimed history. Separate property writes and container operations
are not an atomic database transaction: engine-crash durability must be tested,
and ambiguous interrupted reward states must fail closed to regranting.

## Migration, concurrency and recovery

Surviving legacy face with `fc_door_open=true`: copy unlock into the durable
Guild record, preserve its legacy index for audit, and suppress all new room
rewards because the old opener already received a payout. The room remains
explorable and reusable. Never charge that door again.

Surviving closed face: canonical Guild lamp mapping may replace the incorrect
challenge; there is no consumed partial-payment feature to migrate. Capture the
old index first. If a pre-upgrade face was destroyed and recreated, old world
data has no payment ledger: history is **unrecoverable**, not demonstrably
unclaimed. Record this limitation explicitly; do not infer payment from current
inventory, title or a coordinate. Do not claim universal legacy duplicate safety.

Serialize build requests per cell, with one bounded worker for the pilot.
Different players retain distinct tickets/cooldowns. Recheck current player
location, dimension, identity and door state after every delayed callback.
Leaving the source cancels pending entry; disconnect does not delete a committed
ticket. Release only the pilot's temporary ticking-area leases after work.

After spawn/reload, reconcile actual position with the ticket: inside the room
means retain/recover the return route; outside after death means clear active
travel charging and retain recovery information without forcing the player back
into the room. Never change the player's home/bed spawn for a reward excursion.
An orphan player inside the reserved room can derive the source from its durable
door-cell record. A corrupt/missing record needs a safe fallback exit and a
diagnostic, never an infinite retry loop or an unsafe teleport.

Require a short dwell (e.g. 20 ticks), cooldown (e.g. 60 ticks), and leave-volume
rearming after every successful transition. Dwell is keyed by player and portal,
resets when outside, and must be reconstructed safely after reload. Arrival is
several blocks beyond the return plane. Both sides of each aperture require
testing, including sneaking, running and two simultaneous players.

## Acceptance before declaring the pilot complete

Automated tests must cover incorrect/correct light use, reentrant answers,
no consumption, no opening payout, stable Guild vs scatter mapping, surviving
paid migration, missing-history labeling, face replacement, interrupted build,
unloaded blocks, missing pack structure, occupied allocation rejection, blocked
arrival/source, teleport false/throw, room reward depletion and no refill,
per-player exact-source returns, reload/death reconciliation, cooldown/leave
rearming, and simultaneous entry/claim/return. Fixture negatives must actually
break an invariant rather than merely assert the same constants as production.

Run owner regressions before regeneration; regenerate targeted data/entity/
structure outputs; run base/domain validation and visual route inspections.
Save actual commands/results and labeled render comparisons under the pass's
validation directory. No live Minecraft tests ran during this design audit.
Engine acceptance still requires walking the opening and realm, taking every
reward, returning, reloading, dying, multiplayer races, entity replacement,
unavailable loading authority, and inspecting the content log at the installed
version. Mock success does not complete DP1, DP2 or GP4.

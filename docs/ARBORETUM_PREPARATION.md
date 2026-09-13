# Arboretum preparation receipts — DP10

Arboretum first-build preparation now refuses changed history and reacquires the
live reward chest after saved-state writes. A durable success receipt follows
each completed placement and verified reward write. Saved ready/visited rooms,
shared collection and exact-source return tickets retain their existing behavior.
This is an offline correction; native acceptance remains unrun.

## Reproduced effects

Independent probes execute the actual GP22 controller and actual generated
Arboretum room. They reproduce these decisions under injected boundary changes:

- A diamond added to slot zero during the seed-intent write is overwritten.
- A late occupant does not stop the reward write.
- A replacement chest at seed intent remains empty while a discarded handle
  receives the Pickhammer and certifies ready.
- Replacing the chest after the item write can certify ready, then record a
  claim against the empty live chest.
- Correct type/count with an unexpected name or lore is accepted.
- A structure call that completes its effects then throws has no success
  receipt, but reload previously seeded and admitted the room.
- Replacing an active scan's history with a ready/visited/claimed record is
  adopted by that job, causing a destructive structure write and invalid record.
- Changed same-revision progress during empty-slot inspection is overwritten by
  the seed journal.

Normal preparation and depleted-room reload controls are retained. These are
injected native-effect boundaries, not observations of their frequency in Bedrock.
Original probes, source hashes and output remain in `screenshots/validation/DP10/`.

## Saved contract and effects

The existing per-instance schema, outer room phases, source identity, revision,
cell reservation and tickets stay unchanged. An optional `room.preparation`
schema 1 record contains one of `placing`, `placed`, `seeding`, or `seeded`.
Its phase must agree with the outer room phase. Old ready records need no new
field. Old unfinished placing/seeding records without success receipts remain
closed; geometry alone never supplies missing history.

The active job pins its complete initial record. Every slice rejects unavailable
or changed authority, including changes with the same revision. Preparation
writes compare the fresh complete record, use the existing revision increment,
read back the exact write and verify current authority before the next effect.
Candidate allocation remains monotonic; failures never recycle reservations.

Placement intent precedes a fresh complete-volume and occupant check. Only a
successful native placement followed by a saved `placed` receipt permits shell,
route and chest verification. A thrown call or unsaved receipt never authorizes
placement replay or reward writes, even when the room appears complete.

All 27 chest slots must be empty before seed intent. After that write, preparation
reacquires the live chest and checks the room, complete shell, occupancy, all
slots and fresh history before inserting one Pickhammer. It then reacquires the
live chest again and verifies exact item type, amount, empty name/lore and all
26 unused slots. A discarded container handle cannot certify the destination.

A saved `seeded` receipt permits only fresh read-only reward/geometry/occupancy
verification and a ready-state retry. An ambiguous seed intent never writes
another item. Ready/visited rooms continue to allow depletion without restocking;
the receipt is preparation history, not a promise to keep the chest full.

Only the handwritten Arboretum controller changes among pack inputs. Main
adapters, Library controller, both geometries, challenges, source enrollment,
five/forty-tick isolation, guards and return tickets retain their owners.

## API and validation limits

The retained `@minecraft/server` 2.1.0 declaration exposes `ItemStack.nameTag`
and `getLore(): string[]`, plus the container size/item operations used here.
The [official ItemStack reference](https://github.com/MicrosoftDocs/minecraft-creator/blob/main/creator/ScriptAPI/minecraft/server/ItemStack.md)
corroborates these operations. The runtime and actual-main test doubles now model
empty default lore. No new API version or custom engine capability is required.

All 55 base gates and 65 ESM checks pass in the isolated reviewed-index
snapshot. Runtime 35, actual main integration 20, independent review 22 and
six additional second-review probes pass. Fresh C2 and Guild diagnostics pass;
all 36 structure assets/C2 images and seven visual owners match GP22. Its 282
full PNGs and seven Guild documentation scenes are retained from unchanged
inputs, not rerun. Only the Arboretum controller differs among 1,662 snapshot
pack files. All nine protected unrelated files remain exact. No base gate failed.
A diagnostics helper launch used the wrong working directory; a second-review
fixture initially mistook a source point for a ticket. Both corrections and a
review-helper SHA-logging update are retained; no production fix was required.
No native server or world has run. Legacy C3 remains 45 leaves and 7 done.
Reviewed snapshot hashes are recorded beside the independent probes. Retained
renders from identical inputs do not constitute native visual acceptance.

Dynamic properties and native block/item effects are separate saves. This cannot
prove crash atomicity, prevent external history deletion/rollback or automatically
repair quarantined unfinished rooms. No manual reset/reseed command is supplied.
Native loading cost, watchdog behavior, collision, collection, multiplayer,
disconnect/reload and persistence tests remain unrun. The existing two portal
pilots and the facility remain in-progress; the legacy scoreboard stays 7/45.

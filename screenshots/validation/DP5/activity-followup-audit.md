# Next Guild activity owner: requester identity before native station arrival

Read-only follow-up during DP5, 2026-09-12. This is a proposed GP17 scope, not an
implemented milestone. Production owners and generated packs are unchanged by
this audit. All native Bedrock movement, two-Hero behavior and save/reload
acceptance remain **unrun**.

The next bounded implementation should first make Guild Follow/Wait and deferred
relationship actions obey the requesting Hero. Purposeful arrival follows that
ownership work: a walking goal must not compete with a different Hero's Follow,
Wait, conversation or Guild defence. The current one-placement training session
remains an acknowledged adaptation until its replacement is exercised.

## Reproduced source defects

Both audit commands exited 0; their assertions confirm existing defects rather
than passing repaired behavior. Scripts, result JSON, logs, generated fixture
and downloaded API material are retained under ignored
`tmp/conformance/gp17-activity-audit/`.

| Probe | Actual result | Consequence / owner |
| --- | --- | --- |
| `python tmp/conformance/gp17-activity-audit/owner_probe.py` | Production `gen_behavior.emit_entity` emits a Follow filter containing only the player family. No requester criterion exists. | Both Heroes qualify for the same native Follow goal. `gen_behavior.py` owns that generated group. This is filter evidence, not an observed native target choice. |
| Same owner probe | No dedicated Wait event exists. Neutral removes social groups while base movement stays `0.34` and random stroll stays enabled. | The promised stationary Wait behavior is absent from the owner definition. Actual native motion was not run. |
| `node --experimental-vm-modules tmp/conformance/gp17-activity-audit/callback_probe.mjs` | Hero A's actual functional Wait sends neutral to A's follower, B's spouse/follower and an unrelated active Skill trainee. Both Follow markers disappear and the trainee's actual controller cancels its session. | `fable_emotes.js` broadcasts Wait to every nearby social NPC without requester ownership. |
| Same callback probe | After spouse ownership changes from A to B, A's pending menu still executes love, Follow and Wait selections. | `spouseMenu` needs fresh authority checks inside its deferred callback. |
| Same callback probe | A pending divorce resolved after ownership changes clears the new owner's marriage and owner property. | `divorceConfirm` must revalidate independently, including when opened by another deferred form. |
| Same callback probe | Two pending proposals consume two rings, finish with B as owner and leave the same spouse ID in both Heroes' spouse lists. | `proposeMenu` and `marryNpc` need a final eligibility/ownership check immediately before the mutation sequence. |

The callback harness extracts and executes production functions, uses the actual
training module and mocks only engine objects/forms. Its result files retain
source SHA-256 values. These observations do not justify changing existing spouse
IDs, love values, names, resident slots or historical player lists automatically.

## Verified API boundary

The manifest pins `@minecraft/server` **2.1.0** and a minimum engine **1.21.100**.
The exact Microsoft-published [2.1.0 package metadata](https://registry.npmjs.org/@minecraft/server/2.1.0)
and type archive were inspected without installing dependencies. In those types,
`EntityNavigationComponent` has read-only navigation settings and no methods;
`Entity` has no target member, `setTarget`, `moveTo`, `navigateTo` or `setPath`.
`EntityTameableComponent` exposes `tame(player)` with no corresponding untame
method. Do not invent script path commands or convert residents into permanent
pets as an ownership shortcut. The current [Entity documentation](https://learn.microsoft.com/en-us/minecraft/creator/scriptapi/minecraft/server/entity?view=minecraft-bedrock-stable#target)
also labels its newer target property pre-release and read-only; it is not a
pinned 2.1 API.

Mojang's archived [1.21.100.6 entity documentation](https://github.com/Mojang/bedrock-samples/blob/c32ab2ac8ebdd8b418c03990b30597d6b56bc8c9/documentation/Entities.html)
confirms native Follow filters, the other-entity tag filter and a block-directed
movement goal with block selection, destination offset, arrival radius and an
arrival event. It also documents native owner-follow teleporting by default.
This supports a generated goal driven by durable activity state; it does not
prove navigation through our Guild. The newer `target_block_filters` option is
absent from this pinned release and must not be assumed available. See also the
current primary descriptions of [Follow filtering](https://learn.microsoft.com/en-us/minecraft/creator/reference/content/entityreference/examples/entitygoals/minecraftbehavior_follow_mob?view=minecraft-bedrock-stable)
and [block-directed movement](https://learn.microsoft.com/en-us/minecraft/creator/reference/content/entityreference/examples/entitygoals/minecraftbehavior_move_to_block?view=minecraft-bedrock-stable).

Downloaded archive SHA-256:
`300f5afed99ce589bf9e44c327bce394c22d7b812bbe5c83d686814428935f45`.
Exact type-file SHA-256:
`38e989f3f0371967c1df82a12d5f37a3832cbff3944e38be8bb51638ed0e771d`.
Mojang tag `v1.21.100.6` resolves to
`c32ab2ac8ebdd8b418c03990b30597d6b56bc8c9`; its entity HTML SHA-256 is
`228e476ec50c3a107c08cf84fdd8708fd60dd01b32d79f2daad48eceb9c790e9`.
All downloaded third-party content stays ignored, outside packs and evidence.

## Smallest implementation sequence

1. **Close deferred ownership races first.** Revalidate valid player/NPC handles,
   the current marriage owner, dimension and interaction distance inside spouse
   and divorce responses. Proposal acceptance must recheck unmarried eligibility,
   current opinion and the ring before consuming or updating ownership. Keep the
   final check and mutation sequence synchronous; the second proposal then
   refuses the now-married NPC. Test each nested callback and ownership change,
   not just menu-opening predicates. Preserve all existing relationship history.
2. **Give the two identified Skill residents one activity authority.** Start with
   verified `skill_range` and `skill_hall` roster IDs, never arbitrary nearby
   entities of the same type. Store a separate versioned activity record holding
   requester ID, mode and a generation token. A current requester may change or
   release their activity; another Hero cannot silently take it over. For married
   residents, the existing spouse property is an additional authorization check.
   Unknown legacy Follow ownership must release/defer and await a new request;
   do not guess a requester or rewrite identity history.
3. **Use fixed native Follow channels and an owned Wait transition.** Generate a
   separate Follow group per fixed resident slot; its filter requires that slot's
   requester tag on the other player. An individual Hero may carry several such
   tags. Clear stale tags from online players before enabling a channel; reject
   activation if cleanup/write validation fails. Persist pending previous tag
   holders: an offline previous requester cannot be assumed clean, so the same
   channel cannot be reassigned until its cleanup is verified. Missing holder
   history must defer instead of activating against unknown stale tags. This
   conservative restriction avoids a reconnect interval in which both Heroes
   qualify. Reconcile joining players and loaded residents before reacquisition,
   and never recycle a fixed slot onto an unrelated entity. Wait reserves the
   resident for that requester, interrupts
   training and restores movement only on release. A movement-zero Wait overlay
   is feasible, but every exit must explicitly restore the overwritten movement
   component, and defence must release Wait before engaging. Neutral/social
   reactions must not unconditionally erase someone else's owned activity.
4. **Make precedence and recovery explicit.** Defence preempts social activity;
   valid Follow/Wait/conversation excludes training. Route emote and spouse entry
   points through the same owner. Wait affects only the caller's eligible owned
   followers, preserving other Heroes and unrelated trainees. On disconnect,
   dimension change, invalid/unreadable handles or failed events, stop/defer with
   bounded retry state; never teleport, tame, respawn or erase saved identities.
   Treat player tags as a derived native filter, never the durable authority.
5. **Then prototype one native Skill arrival.** The actual final-voxel survey
   finds exactly one campus fletching table, at local `(91,1,40)`. It is a candidate
   for the nearby `skill_range` resident's native block-directed goal with an
   offset toward the existing `(83.5,1,39.5)` mark. Limit the first pilot to a
   surveyed nearby search volume and refuse missing/edited/duplicate landmarks;
   do not use the four ambiguous bullseyes or repave a saved mark. Verify native
   target-offset centering before fixing its numeric offset. Add an `approaching`
   phase with a finite deadline and measured progress; reserve the station but
   emit no drill until actual location, footprint support and Skill target/lane
   checks pass. Arrival must not call `tryTeleport` or use a correcting fallback.
   A wrong goal, timeout or interruption releases the goal and station in place.
   Do not claim hall-to-range or whole-campus navigation from this first pilot.

Required regressions cover two Heroes with independent residents, attempted
ownership theft, owner disconnect/rejoin and dimension changes, invalid/unloaded
handles, failed tag/event/property writes, stale callback generations, legacy
Follow reconciliation, spouse changes during forms, training/defence precedence,
Wait release restoring movement and preservation of every identity property.
Native-arrival tests must cover blocked support/headroom, edited or duplicated
landmarks, an unreachable destination, no progress, wrong-arrival events and
cancellation before/after arrival. Native pathfinding, target selection, movement
restoration, Follow stopping and two-Hero save/reload remain separate engine
acceptance gates even when those offline contracts pass.

Owner hashes at inspection (DP5 source may receive subsequent unrelated edits):

| Owner | SHA-256 |
| --- | --- |
| `main.js` | `ce3ab2e866663102ce86e1e0cfe18b836983b394313d4e91e372e5369ac261c2` |
| `fable_emotes.js` | `4fad3f0db107b8d050c5a5e8965dc66bcf0926192c0494c36fd55be96700e366` |
| `guild_training.js` | `baf0ff28090d771fb94b4884090e8cf45ba387aa9a6c3cbe7148082e9a70db41` |
| `gen_behavior.py` | `05c75e6c53b275a6eb82e424cecb9fefd8327aa184d1a6ae05f5091be945ba7f` |
| `gen_structures.py` | `e6362334bc8d97715ac92c379a4db718032fcdaaa5d64241acfcf810c4793ae6` |

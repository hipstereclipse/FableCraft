# GP17 independent root review

Status: the final runtime and 24-group suite resolve the review findings below.
No remaining source blocker found within this bounded scope; isolated validation
and the separate independent review are recorded alongside this note.

The review reads actual main.js callbacks, generated wedding_ring.json and the
Microsoft-published @minecraft/server 2.1.0 declarations retained under ignored
tmp/conformance/gp17-activity-audit/. Native Bedrock is unavailable and unrun.

Findings sent to the implementation owner:

- Native entity wrapper object identity is not the persistent entity ID contract.
  Form supersession and mutation invalidation must share authority across separate
  handles for the same player/NPC IDs; same-Hero divorce/remarry must not revive
  an old spouse menu. Track active requests with bounded cleanup.
- Entity properties apply next tick. Rollback must override attempted queued
  married/love writes, including setters that throw after queuing. A same-tick
  old value is insufficient evidence that a setter had no effect.
- The generated wedding ring has max_stack_size 1. ItemStack.isStackableWith
  always returns false for a non-stackable item, so it cannot be used as equality
  for this payment. Use actual one-ring inventory slots in regression fixtures.
- Player spouse-list JSON must be read strictly: unreadable, malformed and
  non-string-entry history must defer instead of silently becoming an empty list.
- A failed inventory write may have already consumed the item. Do not blindly
  give or drop a replacement; preserve ownership when payment readback is
  ambiguous. This bounded change does not promise atomic save/crash recovery.

Primary references: [Entity property timing and persistent IDs](https://learn.microsoft.com/en-us/minecraft/creator/scriptapi/minecraft/server/entity?view=minecraft-bedrock-stable),
[exact published 2.1.0 package](https://registry.npmjs.org/@minecraft/server/2.1.0).
The version-pinned declarations are the compatibility reference; current docs
are corroboration.

Final reviewed main.js SHA-256: `3de202b284cde2acb20f22361b007570fb8154368d6d03fc3c22ea80d01122f8`.
Final reviewed relationship suite SHA-256: `ef1bafd464b907e5a3b6be12cf60a161a92aad8571a33a8c181465e86b3d6d17`.

The form registry uses only primitive IDs/expiry data, settles exact tokens and
invalidates all active NPC forms before ownership mutations. It is capped at 128
requests with a 2,400-tick lifetime. Real rings occupy single-item slots. Tests
include queued property flushes, distinct wrappers, rejected/expired forms,
unknown inventory readback and actual training interruption. No generator or
activity-movement owner changes are included.

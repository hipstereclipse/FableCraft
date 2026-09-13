# GP20 follow-up: one native Skill arrival, still a proposal

Read-only audit during DP6, 2026-09-12. No production, generated pack, saved
identity, activity journal, station geometry or staging changes were made.
The concrete next scope is **only the established `skill_range` resident walking
from the small clear corridor east of its existing mark**. Native pathfinding,
offset centering and arrival events remain **unrun**; this report does not close
the one-placement adaptation or claim an implemented GP20.

## Evidence and the current defect

Reproduce from the repository root:

```sh
python screenshots/validation/DP6/station-arrival-followup.py
```

The [Python probe](station-arrival-followup.py) independently decodes the shipped
Guild structure using the retained GP18 NBT reader, compares all final cells with
`build_guild_hall()`, and feeds those cells to the [JavaScript prototype](station-arrival-followup.mjs).
The latter executes actual `guildStationClear`, `guildSkillLaneClear`, runtime
anchors and `createGuildTrainingController`; only its proposed arrival predicate
is new audit code. [Results and owner hashes](station-arrival-followup.json)
record:

- Exactly one fletching table in the full `122 × 30 × 108` shipped campus:
  local `(91,1,40)`, with coarse dirt at `(91,0,40)` and no authored block states.
  The existing range mark is `(83.5,1,39.5)`; the practice target is
  `(83.5,2.45,34.5)` on hay. No target, prop or mark needs relocation.
- All 13 quarter-block samples from `(86.5,1,39.5)` to the mark pass the actual
  full-footprint/headroom support check. This is a clear short corridor, not a
  native pathfinding result or a whole-campus route claim.
- Current actual `acquire()` performs one `tryTeleport`, including when the
  trainee starts at that corridor endpoint. This is the baseline to replace.
- The proposed arrival predicate accepts the verified mark and rejects 27 cases:
  missing/replaced table or support, a closer duplicate, unreadable scan cells,
  edited station/target/hay/ray, wrong ID/slot/session/token/activity revision,
  Follow/Wait/blocked activity, marriage/read failure, defence/aggravation,
  deadline expiry, missing post-reload approach and reaching the table itself.
  Refusals leave altered cells untouched. These are prototype predicate tests;
  no production lifecycle implementation is implied. The 624 search cells below
  the serialized structure are explicitly mocked as readable air only for the
  predicate tests. Their actual saved-world contents remain unknown; unreadable
  cells or an alternate table there also refuse arrival.

The Skill scheduler currently selects the nearest eligible entity of the Skill
type; it does not select the saved `skill_range` slot. The first implementation
must remove that substitution for this mark: resolve the exact roster-bound ID
freshly and refuse `skill_hall`, copied markers, unknown/dead/unavailable history
and replacements. The existing strict `guildResidents.binding` supplies this
check. Do not fall back to another Skill entity or to the old range teleport.

## Pinned API and the unresolved offset

The manifest still requires `@minecraft/server` **2.1.0** and engine **1.21.100**;
the Skill entity uses format **1.21.0**. The Microsoft-published
[2.1.0 types](https://registry.npmjs.org/@minecraft/server/2.1.0) and Mojang's
[archived 1.21.100.6 entity documentation](https://github.com/Mojang/bedrock-samples/blob/c32ab2ac8ebdd8b418c03990b30597d6b56bc8c9/documentation/Entities.html)
were reread from the exact ignored downloads identified in the
[DP5 audit](../DP5/activity-followup-audit.md). Their SHA-256 values still match
`38e989f3f0371967c1df82a12d5f37a3832cbff3944e38be8bb51638ed0e771d` (types) and
`228e476ec50c3a107c08cf84fdd8708fd60dd01b32d79f2daad48eceb9c790e9` (entity HTML).
The web tool could not refetch the pinned GitHub blob during this audit; it did
retrieve the [current primary goal reference](https://learn.microsoft.com/en-us/minecraft/creator/reference/content/entityreference/examples/entitygoals/minecraftbehavior_move_to_block?view=minecraft-bedrock-stable).

The pinned native goal supports `target_blocks`, `target_selection_method`,
`search_range`, `search_height`, `target_offset`, `goal_radius` and `on_reach`.
Its offset description specifies addition to the selected target position;
**it does not define that position's corner/center convention**. The current
primary page does not resolve it either. These candidate offsets produce the
existing mark only under their stated hypotheses:

| Hypothesized target anchor | Candidate `target_offset` |
| --- | --- |
| Integer block corner `(91,1,40)` | `[-7.5,0,-0.5]` |
| Horizontal center at block foot `(91.5,1,40.5)` | `[-8,0,-1]` |
| Full block center `(91.5,1.5,40.5)` | `[-8,-0.5,-1]` |

This table is arithmetic, not evidence selecting one convention. A different
native anchor remains possible. Do not ship an offset based on this table alone.
The newer `target_block_filters` field is absent from the pinned material and
cannot supply an exact-coordinate selector here.

Stable 2.1 exposes `world.afterEvents.dataDrivenEntityTrigger`, filtered by entity
and event types; its event provides the entity and event ID, **no selected block
coordinate or script session token**. Use it as a wake-up to inspect the live
approach record. It is not an arrival authority or proof of which table was
selected. Navigation settings remain read-only; no `Entity.moveTo`, `navigateTo`
or path setter is available. `Entity.setRotation` is present if one verified
facing adjustment is required after arrival; no position correction is needed.

## Smallest implementation contract

1. **Admit one local approach.** Require the exact live `skill_range` binding,
   clear GP19 idle status/revision, readable unmarried state with empty owner,
   current daytime training session, no defence/aggravation, and completed old
   training cleanup. Limit feet to local `x=83.5..86.5`, `z=39..40`,
   `y=0.9..1.1`; leave a resident outside this corridor doing its existing work.
   Reserve the range session and a new approach token without freezing or
   teleporting. Preserve GP19's journal, offline debts and requester authority.
2. **Use one native block goal after calibration.** Candidate settings are
   `target_blocks:["minecraft:fletching_table"]`, nearest selection,
   `search_range:10`, `search_height:1`, speed multiplier `1`, priority `3`,
   start chance `1`, tick interval `1`, goal radius `0.2`, and
   `on_reach:{event:"fc:guild_range_arrived",target:"self"}`. The numeric offset
   remains gated by native calibration. Restore ordinary movement before adding
   the approach group; remove conflicting legacy social goals. Do not tame,
   target arbitrary players, add a landmark or emit a shot during approach.
3. **Certify the entire possible landmark search envelope.** The prototype's
   conservative moving-volume union is local `x=72..97`, `y=-1..3`, `z=28..51`
   (3,120 cells), covering the admitted corridor plus the proposed search radius
   and a rounding margin. Require every cell readable, exactly the authored
   fletching table, its authored support, the existing station and clear target
   lane. Recheck on each 10-tick approach pass and immediately before completion;
   cancel if the actor exits its admitted corridor or any second table appears.
   This bound assumes the native search really respects those configured bounds;
   engine calibration must confirm that too. Never infer uniqueness from only
   the immutable generated asset in an edited saved world.
4. **Complete from verified live state.** Extend the training owner with an
   explicit `approaching` phase and a no-teleport completion path. On a native
   wake-up, capture the current token/revision; any deferred callback revalidates
   both, exact ID/slot/base/dimension, session, live GP19 idle authority, marriage,
   defence, deadline and all geometry. Require actual feet within `0.25` blocks
   of the mark, clear support/headroom at both the nominal mark and actual feet,
   and the actual Skill ray from both positions. Only then remove approach,
   freeze with the existing training group, add the range role and issue a new
   active drill token. An unsolicited/stale event cannot create an approach.
   Existing `showPracticeShot` preflight remains on every delayed pulse.
5. **Release in place.** Use one finite attempt per session, a proposed 200-tick
   deadline and cancel after 60 ticks without at least `0.1` block improvement
   toward the mark. Recheck freshness before each transition. Conversation,
   valid Follow/Wait, marriage, defence, unload, death, changed session, wrong
   station/event, edited geometry or failed native cleanup interrupts it.
   Training `reserved`, `retain`, `beginPass` and cleanup must account for
   `approaching`; otherwise the existing eligibility filter would drop its own
   attempted resident. GP19's `stopTraining` adapter must finish removing that
   group before Follow/Wait can activate. Native defence-start must independently
   remove approach and restore motion even if script cleanup fails. Reload
   discards approach permission and first-observation cleanup removes any saved
   goal; a surviving native event never resumes it. Failed cleanup remains
   pending. No timeout fallback, repeated teleport or automatic replacement.

The owners are `guild_training.js` (phase/token/session/cleanup), `main.js`
(exact-slot selection, geometry and arrival subscription), `gen_behavior.py`
(approach/add/remove event composition and defence restoration), plus actual
controller/callback/generated-event/final-voxel regression tests. GP19
`guild_activity.js` should not acquire a separate training mode or rewrite its
schema for this pilot; its idle revision and existing interruption adapter remain
the cross-owner guard. Existing Might/Will acquisition stays outside this scope.

## Remaining gates and next task

The next task is a **disposable native calibration fixture**, using the pinned
manifest floor and actual Skill collision/navigation groups, at two translated
origins. Record feet and selected event sequence for a lone table and each offset
hypothesis; then add a closer alternative, obstruction and an interrupt. Verify
arrival radius, native search bounds, removal of cached goals, and no target
reselection outside the certified volume. Once that passes, implement the small
approaching phase with actual source regressions, including interruption before
and after arrival and reload while moving. Timing and the 3,120-block survey cost
are unprofiled and need measurement; do not treat them as performance promises.

Polling can refuse every observed duplicate/replacement, but stable block reads
cannot prove that an identical table was not removed and replaced between reads,
or that a transient duplicate never existed between script passes. The native
arrival event exposes no selected block to close that historical gap. If “fail on
replaced table” requires detecting such indistinguishable history rather than
current wrong type/support/position, that requirement remains unsolved and blocks
this native-goal choice. Do not claim exact native target provenance from the
prototype's unique-current-landmark check. No production navigation change should
be called complete before the centering and native acceptance gates pass.

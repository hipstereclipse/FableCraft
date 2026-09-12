# Animation gate audit and Phase 0.3 correction

The stale plan's blanket claim that `variable.attack_time` is never driven is not
supported. Microsoft's [Molang swing-duration documentation](https://learn.microsoft.com/en-us/minecraft/creator/reference/content/molangreference/examples/molangconcepts/queryfunctions/query_modified_swing_duration?view=minecraft-bedrock-stable)
identifies `variable.attack_time` as attack/swing progress. Mojang's
[zombie client entity](https://github.com/Mojang/bedrock-samples/blob/main/resource_pack/entity/zombie.entity.json)
uses attack controllers without assigning that variable, alongside a
[melee-box behavior](https://github.com/Mojang/bedrock-samples/blob/main/behavior_pack/entities/zombie.json).
Sources checked 2026-09-12. These current samples are newer than the pack target;
no new query/component from them has been introduced into this pack.

The pack's melee goals supply the engine swing mechanism. Adding a local timer or
assigning zero to attack_time would override rather than repair that mechanism.
Do not use nonexistent `query.attack_time`. The documented newer
`query.modified_swing_duration` is also not needed and is above this pack's minimum.

The strengthened audit found a narrower, real wiring mismatch: bandit_archer,
hobbe_scout and summoner referenced the melee overlay while their BP ranged/caster
behaviors explicitly omit the melee goal. Their controller gate had no configured
melee swing source. gen_resources.py now omits only those inappropriate overlays.
Archer/scout bow controllers remain; summoner's signature cast animation remains
an explicit E3 task. Existing melee clip/gate expressions are unchanged.
This is a static inference from pack wiring, not an observed engine-animation fix.

## Contract

`python scripts/_audit_anims.py` loads all 54 client entities, RP clips/controllers,
geometries and matching BP behavior components/groups. It checks:

- Reachable short names/controllers/clips, conditional animation entries and cycles.
- All played bones against referenced geometry.
- Variables used by transition/conditional-animation gates, with assignments from
  the same entity's scripts and reachable controller states/clips. Variable aliases
  must resolve dependencies. Assignments from another entity or unreachable state
  cannot satisfy the check.
- Engine binding: only attack_time, only with a configured melee goal. A constant
  assignment overriding it is rejected. Script property setters are not Molang
  variable setters; arbitrary matching JS strings cannot satisfy the audit.
- Invalid query.attack_time in reachable expressions.
- Nonzero process status on failure (the old audit only printed problems).

Static analysis does not prove state transition timing, mutually exclusive paths,
component-group activation by gameplay, script-started clips, all possible Molang
syntax, or that a newer engine preserves these semantics. Adding a new engine
binding requires official evidence and a negative fixture, not a blanket exemption.
Dynamic entity properties accessed with query.property are engine queries, not
user-variable assignments. They need separate property contracts when introduced.

## Test-the-test evidence

Before modifying gen_resources, the new audit exits 1 with three undriven gates:
`screenshots/validation/0.3/before.log`. After generator-only regeneration it exits
0 for 54 client entities: `after.log`. Ten regression tests include missing-driver
failure followed by a real assignment pass, unrelated-entity and unreachable-state
false positives, engine override, alias dependencies, cycles, missing bones/clips/
controllers, invalid query and a broken isolated pack's CLI exit status.

Run `python scripts/tests/test_animation_audit.py` and the base validator suite.
Only three client-entity files changed substantively; no models, textures or clips
changed. Re-rendering a static pose would not establish the changed controller
behavior; manual evidence below remains necessary.

## Required manual checks — UNRUN

- [ ] On Bedrock 1.21.100+ confirm balverine/bandit/troll/guard/dragon remain idle
      when not attacking, visibly swing during actual melee and return to locomotion.
- [ ] Confirm an NPC switches from social idle to melee after react_attack and back.
- [ ] Archer/scout still aim/fire, summoner still fires; no frozen models or new errors.
- [ ] Capture Content Log and short videos/stills showing idle, strike and recovery;
      record engine version and save evidence under screenshots/validation/0.3/.

Phase 0.3 code and automated tests are delivered, but its checklist stays
in-progress until these in-world checks run. No claim that all melee animations
were previously broken, or that a new timer fixed them, is made.

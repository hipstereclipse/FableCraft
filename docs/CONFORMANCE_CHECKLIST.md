# TLC Conformance checklist

Updated 2026-09-12. Leaf rows are the units of execution. See the playbook for recipes,
acceptance and evidence policy. `SELF` resolves to the commit containing that row update;
replace with a real hash in the next milestone. A mock or render is never an in-game pass.

## Prerequisites and bootstrap

| Item | Status (todo/in-progress/done) | Evidence (commit + screenshot/validator path) | Grade | Date |
| --- | --- | --- | --- | --- |
| Spell completion (code + automated validation; manual follow-up separate) | done | ccafd4c; screenshots/validation/spells/; SPELL_COMPANIONS.md | PASS (17 mocks); manual pending | 2026-09-12 |
| Spell in-world checklist | todo | ccafd4c; SPELL_COMPANIONS.md | PENDING (manual) | 2026-09-12 |
| Bootstrap document set | done | d9d5f7c; docs/CONFORMANCE_PLAN.md; LEGAL.md; screenshots/validation/bootstrap/ | PASS (docs); gameplay unchanged | 2026-09-12 |

## 0 — Stabilization

| Item | Status (todo/in-progress/done) | Evidence (commit + screenshot/validator path) | Grade | Date |
| --- | --- | --- | --- | --- |
| 0.1 Repair behavior generator | done | 6835313; screenshots/validation/0.1/ | PASS (automated) | 2026-09-12 |
| 0.2 Adopt orphan tools and output policy | done | 6ca1e14; screenshots/validation/0.2/ | PASS (automated) | 2026-09-12 |
| 0.3 Drive melee strike gates and test the audit | in-progress | SELF: TLC Conformance — 0.3: audit attack sources and remove unsupported overlays; screenshots/validation/0.3/ | PASS (automated); PENDING (manual) | 2026-09-12 |
| 0.4 Synchronize gameplay documentation | todo | — | — | — |

## L — Naming and legal

| Item | Status (todo/in-progress/done) | Evidence (commit + screenshot/validator path) | Grade | Date |
| --- | --- | --- | --- | --- |
| L1 Verify fan-work notice and release posture | todo | — | — | — |
| L2 Generator string table and local/original mode | todo | — | — | — |
| L3.1 Runtime strings and menu hub | todo | — | — | — |
| L3.2 Runtime quests, towns, shops and crime | todo | — | — | — |
| L3.3 Will modules, logbook and generated HUD text | todo | — | — | — |
| L4 Enforce original-only release packaging | todo | — | — | — |

## W — World

| Item | Status (todo/in-progress/done) | Evidence (commit + screenshot/validator path) | Grade | Date |
| --- | --- | --- | --- | --- |
| W1.1 Cullis gate | todo | — | — | — |
| W1.2 Lychfield crypt | todo | — | — | — |
| W1.3 Twinblade tent rings | todo | — | — | — |
| W1.4 Arena halls | todo | — | — | — |
| W2.1 Bowerstone North and Manor | todo | — | — | — |
| W2.2 Hook Coast lighthouse and Abbey | todo | — | — | — |
| W2.3 Oakvale Memorial Garden | todo | — | — | — |
| W2.4 Grey House and cellar | todo | — | — | — |
| W3.1 Bargate Prison | todo | — | — | — |
| W3.2 Bronze Gate and Archon Shrine | todo | — | — | — |
| W3.3 Archon Folly | todo | — | — | — |
| W3.4 Greatwood Gorge toll bridge | todo | — | — | — |
| W3.5 Darkwood Bordello | todo | — | — | — |
| W4.1 Oakvale walkability | todo | — | — | — |
| W4.2 Bowerstone walkability | todo | — | — | — |
| W4.3 Knothole walkability | todo | — | — | — |
| W4.4 Hook Coast walkability | todo | — | — | — |
| W4.5 Snowspire walkability | todo | — | — | — |

## E — Entities and animation

| Item | Status (todo/in-progress/done) | Evidence (commit + screenshot/validator path) | Grade | Date |
| --- | --- | --- | --- | --- |
| E1 Fill character and ambient roster gaps | todo | — | — | — |
| E2 Flyer attacks, death and hurt clips | todo | — | — | — |
| E3 Creature signature specials | todo | — | — | — |
| E4 Expression hold meter and sweet spot | todo | — | — | — |

## V — Particles

| Item | Status (todo/in-progress/done) | Evidence (commit + screenshot/validator path) | Grade | Date |
| --- | --- | --- | --- | --- |
| V1 Will charge and Cullis swirl | todo | — | — | — |
| V2 XP streams and Demon Door speech | todo | — | — | — |
| V3 Boss telegraphs | todo | — | — | — |
| V4 Regional ambient effects | todo | — | — | — |

## M — Mechanics

| Item | Status (todo/in-progress/done) | Evidence (commit + screenshot/validator path) | Grade | Date |
| --- | --- | --- | --- | --- |
| M0 In-world subsystem smoke harness | todo | — | — | — |
| M1 Interactive good/evil altars | todo | — | — | — |
| M2 Property ownership and rent | todo | — | — | — |
| M3 Fishing and digging | todo | — | — | — |
| M4 Tavern games | todo | — | — | — |
| M5 Scars and aging | todo | — | — | — |

## C — CI and scoring

| Item | Status (todo/in-progress/done) | Evidence (commit + screenshot/validator path) | Grade | Date |
| --- | --- | --- | --- | --- |
| C1 Continuous validation | todo | — | — | — |
| C2 Structure-manifest contract | todo | — | — | — |
| C3 Reproducible conformance scoreboard | todo | — | — | — |

## Scope gaps and manual evidence

Kraken is a documented roster gap but not named in approved E1; retain it for a later
explicit milestone. Full-world canon completeness cannot be inferred from the leaf count.
All in-world checks start unrun; composite screenshots cannot close them.

## Scoreboard

C3 will generate per-domain completion percentages and separate manual/visual grades.
No conformance percentage is claimed during bootstrap.

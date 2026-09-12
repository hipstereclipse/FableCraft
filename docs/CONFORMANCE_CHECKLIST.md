# TLC Conformance checklist

Updated 2026-09-12. Leaf rows are the units of execution. See the playbook for recipes,
acceptance and evidence policy. `SELF` resolves to the commit containing that row update;
replace with a real hash in the next milestone. A mock or render is never an in-game pass.

## Prerequisites and bootstrap

| Item | Status (todo/in-progress/done) | Evidence (commit + screenshot/validator path) | Grade | Date |
| --- | --- | --- | --- | --- |
| Spell completion (code + automated validation; manual follow-up separate) | done | ccafd4c; screenshots/validation/spells/; SPELL_COMPANIONS.md | PASS (17 mocks); manual pending | 2026-09-12 |
| Entity-scan fallback correction | done | bc3e7bd; screenshots/validation/scan-fallback/ | PASS (3 error-path tests) | 2026-09-12 |
| Spell in-world checklist | todo | ccafd4c; SPELL_COMPANIONS.md | PENDING (manual) | 2026-09-12 |
| Bootstrap document set | done | d9d5f7c; docs/CONFORMANCE_PLAN.md; LEGAL.md; screenshots/validation/bootstrap/ | PASS (docs); gameplay unchanged | 2026-09-12 |

## 0 — Stabilization

| Item | Status (todo/in-progress/done) | Evidence (commit + screenshot/validator path) | Grade | Date |
| --- | --- | --- | --- | --- |
| 0.1 Repair behavior generator | done | 6835313; screenshots/validation/0.1/ | PASS (automated) | 2026-09-12 |
| 0.2 Adopt orphan tools and output policy | done | 6ca1e14; screenshots/validation/0.2/ | PASS (automated) | 2026-09-12 |
| 0.3 Drive melee strike gates and test the audit | in-progress | fe7fa33; screenshots/validation/0.3/ | PASS (automated); PENDING (manual) | 2026-09-12 |
| 0.4 Synchronize gameplay documentation | done | 88c3f37; screenshots/validation/0.4/ | PASS (automated) | 2026-09-12 |

## L — Naming and legal

| Item | Status (todo/in-progress/done) | Evidence (commit + screenshot/validator path) | Grade | Date |
| --- | --- | --- | --- | --- |
| L1 Verify fan-work notice and release posture | done | 727d945; screenshots/validation/L1/ | PASS (automated) | 2026-09-12 |
| L2 Generator string table and local/original mode | done | 3642d33; screenshots/validation/L2/ | PASS (automated) | 2026-09-12 |
| L3.1 Runtime strings and menu hub | in-progress | d8361d4; screenshots/validation/L3.1/ | PASS (automated); PENDING (manual) | 2026-09-12 |
| L3.2 Runtime quests, towns, shops and crime | in-progress | 833fbaf; screenshots/validation/L3.2/ | PASS (automated); PENDING (manual/catalog review) | 2026-09-12 |
| L3.3 Will modules, logbook and generated HUD text | in-progress | cb9e0db; screenshots/validation/L3.3/ | PASS (automated); PENDING (manual/catalog review) | 2026-09-12 |
| L4 Enforce original-only release packaging | in-progress | 11dd038; screenshots/validation/L4/ | PASS (automated); RELEASE BLOCKED | 2026-09-12 |

## W — World

| Item | Status (todo/in-progress/done) | Evidence (commit + screenshot/validator path) | Grade | Date |
| --- | --- | --- | --- | --- |
| W1.1 Cullis gate | in-progress | 2db414bbe53fea87f48fdf5c2cfd67da6eec4b0a; screenshots/validation/W1.1/ | PASS (automated); PENDING (manual/reference comparison) | 2026-09-12 |
| W1.2 Lychfield crypt | in-progress | 608edf164b31b48f53c9ed601cde1ef31f67a485; screenshots/validation/W1.2/; docs/LYCHFIELD_CRYPT.md | PASS (automated); PENDING (manual/reference comparison) | 2026-09-12 |
| W1.3 Twinblade tent rings | in-progress | add099a2a33765faf3aab9eda59df09427454856; screenshots/validation/W1.3/; docs/TWINBLADE_CAMP.md | PASS (automated); PENDING (manual/reference comparison) | 2026-09-12 |
| W1.4 Arena halls | in-progress | SELF: TLC Conformance — W1.4: connect arena preparation and hero halls; screenshots/validation/W1.4/; docs/ARENA_HALLS.md | PASS (automated); PENDING (manual/reference comparison) | 2026-09-12 |
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
| C1 Continuous validation | done | 086337c; screenshots/validation/C1/remote-run.json; screenshots/validation/C1/remote/ | PASS (local + clean snapshot + GitHub CI) | 2026-09-12 |
| C2 Structure-manifest contract | in-progress | b3a1a45; screenshots/validation/C2/ | PASS (automated); PENDING (manual) | 2026-09-12 |
| C3 Reproducible conformance scoreboard | done | 05707d4; screenshots/validation/C3/ | PASS (automated) | 2026-09-12 |

## Scope gaps and manual evidence

Kraken is a documented roster gap but not named in approved E1; retain it for a later
explicit milestone. Full-world canon completeness cannot be inferred from the leaf count.
All in-world checks start unrun; composite screenshots cannot close them.

## Scoreboard

<!-- conformance-score:start -->

Generated by `python scripts/conformance_score.py --write`; CI checks for stale output.

| Domain | Done / total | Completion | Automated PASS recorded | Manual pending recorded | In progress | Todo |
| --- | --- | --- | --- | --- | --- | --- |
| 0 | 3 / 4 | 75.0% | 4 | 1 | 1 | 0 |
| L | 2 / 6 | 33.3% | 6 | 3 | 4 | 0 |
| W | 0 / 18 | 0.0% | 4 | 4 | 4 | 14 |
| E | 0 / 4 | 0.0% | 0 | 0 | 0 | 4 |
| V | 0 / 4 | 0.0% | 0 | 0 | 0 | 4 |
| M | 0 / 6 | 0.0% | 0 | 0 | 0 | 6 |
| C | 2 / 3 | 66.7% | 3 | 1 | 1 | 0 |
| Total | 7 / 45 | 15.6% | 17 | 9 | 10 | 28 |

Pending manual plan checks: 0.3, L3.1, L3.2, L3.3, W1.1, W1.2, W1.3, W1.4, C2.

Counts cover the 45 approved plan leaves. Spell/bootstrap prerequisites are listed
separately above. Completion means a row is done; automated PASS can coexist with
pending manual work. Todo rows have unknown verification, not an inferred pass.
Manual counts reflect explicit grade cells; absence of a pending label is not proof
that a feature has been tested in-world. The spell in-world checklist also remains separate.

Current offline structure appearance grades from
[the C2 audit](../screenshots/structures/contract/AUDIT.md): S=28, A=1, B=0, C=0, D=0.
These are renderer metrics, not canon/playability grades. No letter-grade average
or overall canon-conformance score is inferred.

<!-- conformance-score:end -->

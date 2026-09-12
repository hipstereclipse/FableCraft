# FableCraft → TLC Conformance Master Plan (with IP hardening)

## Context

The user wants every aspect of FableCraft — structures, towns, mechanics, characters, encounters, particles, animations — driven to maximum Fable: The Lost Chapters fidelity through an iterative, test-gated process a less-capable AI could execute solo. Required process features: a living checklist doc updated every step, per-step validators/renders/comparisons, commits+pushes, smoke/regression tests, a user continue-check after each step, and a handoff prompt whenever a session ends.

Added constraint: the mod will be **publicly released for free**, so the plan must build in IP risk reduction. Decided posture (user-selected): **dual-mode name layer** — mechanics stay 1:1 faithful; all Fable proper nouns route through one strings module so distributed builds can flip to original ("legally distinct") names while local builds stay faithful. Parody is explicitly NOT the defense (a faithful recreation can't claim it); the defenses are: original assets (already true — everything is generated), non-commercial, disclaimers, takedown readiness, and the name layer. World architecture decision (user-selected): **keep the procedural scatter engine, deepen/add POIs** — no fixed Albion map.

### Verified current state (from exploration)
- **World**: Guild is a faithful fixed campus (`scripts/gen_structures.py` + `main.js` GUILD anchors, physics-verified caves). ~23 other POIs scatter per 160-block cell via `STRUCTS` table (`packs/Fablecraft_BP/scripts/main.js:5465-6039`). Missing: Bargate Prison, Archon's Folly, Bronze Gate, Bowerstone North/Manor, Hook Coast lighthouse/Abbey, Greatwood Gorge toll bridge, Twinblade tent rings, Lychfield crypt, Arena halls, Darkwood Bordello, Grey House; `focus_site` is a generic proxy for Cullis gates. Offline render verification exists (`scripts/gen_screenshots.py` → `screenshots/structures/` + AUDIT.md grades; `_grade.py`/`_target_map.py`/`_audit_match.py` overlay grading).
- **Entities**: 55 `fc:*` entities generated from `scripts/fc_mobs.py` via `gen_behavior.py`/`gen_resources.py`. Missing canon: Thunder, Whisper, Scythe, Nostro, Kraken, chickens/livestock, crowd variety. **Bug: `variable.attack_time` is never driven** — creature melee strike clips never fire (gate in `fc.animation_controllers.json`). Flyers have no attack clip; no death/hurt/special clips.
- **Particles**: 34 custom particles, all spell IDs resolve. Missing Fable signatures: Will-charge caster aura, Cullis teleport swirl, XP-orb stream, demon-door mouth FX, boss telegraphs, ambient region VFX.
- **Mechanics**: implemented — morality/appearance, renown, 3-discipline XP, 31 emotes, marriage, quests+boasting, 8 demon doors, Cullis travel, crime/wanted/jail, shops, titles, 18 Will powers (README drift says 17). Missing — property ownership, fishing/digging, tavern games, interactive Avo/Skorm altars, emote hold-meter, scars/aging.
- **Build/test**: `scripts/build_addon.py` (validate + package; `--full` runs 10 generators). **Hazard: working-tree `scripts/gen_behavior.py` is older/stripped vs HEAD — running it or `--full` regresses NPC react events + 194 item icons.** No JS tests, no CI. Manual checklists in BOUNTY_SYSTEM.md / WILL_AND_DESTINY_PHASE1.md. Branch `phase3-will-destiny` tracks origin (GitHub), uncommitted audit tooling + modified files present.
- **Generator-owned files must never be hand-edited**: `entities/`, RP `models|entity|animations|animation_controllers|render_controllers|attachables|particles`, `fable_emote_registry.js`, `fable_hud.js`, `fc_gamedata.js`, `texts/languages.json`.

## Deliverables of this implementation

1. **Repo document set** (new `docs/` folder):
   - `docs/CONFORMANCE_PLAN.md` — the verbose master playbook (every phase/milestone below expanded into explicit numbered instructions with exact commands, file paths, acceptance tests, and canon citations tagged [C]/[G]/[B] — written so a weaker agent can execute any milestone cold).
   - `docs/CONFORMANCE_CHECKLIST.md` — living checklist; one table per domain; columns: `Item | Status (todo/in-progress/done) | Evidence (commit + screenshot/validator path) | Grade | Date`. Updated as part of EVERY step (enforced by protocol, see below).
   - `docs/HANDOFF.md` — standing handoff doc, rewritten at every stop point from a fixed template: current milestone, last commit hash, green/red state of validators, next 3 actions, known landmines (gen_behavior hazard, anchor coupling, generator-owned files).
   - `LEGAL.md` + README notice section — unaffiliated fan work; non-commercial; all assets original/generated, nothing extracted from any Fable game; Fable/Albion trademarks belong to Microsoft; takedown-compliance statement. (General info, not legal advice — recommend attorney review before large-scale distribution.)
2. **Name-indirection (branding) layer**: `scripts/fc_strings.py` (single table of every Fable proper noun → {faithful, original} pair) consumed by all generators; generated `packs/Fablecraft_BP/scripts/fc_strings.js` for runtime scripts; `build_addon.py --branding=faithful|original` flag; **distributed `dist/` artifacts always built `original`**; new validator: when branding=original, grep-fail any Fable proper-noun literal in packaged output. Natural choke points: `texts/languages.json` (all entity/item display names, generated) and menu/HUD strings in `main.js` (long tail — migrate file-by-file, validator tracks per-file exemption list shrinking to zero).
3. **Test scaffolding**:
   - Extend `scripts/_audit_anims.py`: assert every animation-controller gate variable (esp. `variable.attack_time`) is driven somewhere (pre_animation/controller/script).
   - New `fc:smoke` scriptevent: in-game smoke suite exercising every subsystem (XP award, morality delta, emote, spell cast, shop tx, bounty accrue/clear, cullis register, marriage gift, quest grant) printing PASS/FAIL lines to chat — becomes the manual-test backbone.
   - Structure-manifest test in `build_addon.py validate()`: every `STRUCTS` id ↔ generator function ↔ `.mcstructure` ↔ screenshot ↔ AUDIT grade row.
   - GitHub Actions CI (`.github/workflows/validate.yml`): `python scripts/build_addon.py` (validate, no `--full`), `npx eslint`, `verify_emotes.py`, `_audit_anims.py` on every push.
4. **The phased roadmap itself** (below), executed milestone-by-milestone with the per-step protocol.

## Phase plan (each milestone independently shippable, ends green+committed)

**Phase 0 — Stabilize the ground (must be first)**
- 0.1 Repair `scripts/gen_behavior.py`: diff working tree vs HEAD; port anything genuinely new; otherwise `git checkout HEAD -- scripts/gen_behavior.py`. Verify by regenerating one entity and diffing (react events + icon formats intact). Until green, `--full` builds stay banned.
- 0.2 Commit the orphan tooling (`scripts/audit_hud.py`, `preview_hud_faithful.py`, `_audit_*.py`, `_target_map.py`, `wd/ghostblade.js`, modified wd files); gitignore `tmp/`; decide `patch_guild_tiling.py` fate; establish dist-rebuild-only-at-milestone policy.
- 0.3 Fix `variable.attack_time`: investigate drive mechanism (engine-set for melee mobs vs. controller ramp on `query.anim_time` vs. script-set); implement in `gen_resources.py`; verify in-game + via extended `_audit_anims.py`.
- 0.4 Doc drift: README 17→18 Will powers; sync BOUNTY_SYSTEM.md edits.

**Phase L — Legal/IP hardening** (deliverables #1-LEGAL and #2 above; do early since it touches naming everywhere). L1: LEGAL.md + README notice. L2: `fc_strings.py` + languages.json flip. L3: runtime `fc_strings.js` + main.js migration (multi-milestone). L4: branding validator + renamed public pack name (user picks final public name from proposals).

**Phase W — World deepening** (scatter kept). One milestone per structure, protocol per milestone: write/extend generator in `gen_structures.py` → `STRUCTS` entry (weight/surface/loot/mobs/door/cullis flags) → render via `gen_screenshots.py` → grade vs `visual_reference.md`/reference shots → anchor-coupling check if interactive. Order: W1 promote proxies (real Cullis gate structure replacing `focus_site`, Lychfield crypt into graveyard, Twinblade tent rings, Arena halls). W2 missing towns (Bowerstone North+Manor, Hook Coast lighthouse+Abbey, Oakvale Memorial Garden+Grey House). W3 missing landmarks (Bargate Prison, Bronze Gate+Archon's Shrine, Archon's Folly, Greatwood Gorge toll bridge, Darkwood Bordello). W4 town walkability pass (streets, doors, interiors, guards+crowd spawns in existing towns).

**Phase E — Entities & animations**. E1 canon roster gaps (Thunder, Whisper, Scythe, Nostro; chickens/livestock; crowd variants — all via `fc_mobs.py` + regen). E2 flyer attack clips + death/hurt clips. E3 signature specials (balverine leap, banshee shriek, dragon breath, summoner cast). E4 emote hold-meter/sweet-spot mechanic.

**Phase V — Particles & VFX**. V1 Will-charge aura + Cullis teleport swirl. V2 XP-orb stream + demon-door mouth FX. V3 boss telegraphs. V4 ambient region VFX (Darkwood wisps, Oakvale fireflies, Skorm embers, Snowspire snow). All via `gen_wd.py`/`gen_resources.py` emitters; verified by `gen_doc_screenshots.py` renders + in-game checklist.

**Phase M — Missing mechanics**. Each gets a BOUNTY_SYSTEM.md-style spec doc + manual checklist + `fc:smoke` coverage: M1 interactive Avo/Skorm altars (constants already exist in `wd/alignment.js`). M2 property ownership (buy houses/rent). M3 fishing & digging. M4 tavern games. M5 scars/aging (flip `agingEnabled` behind config).

**Phase C — CI & conformance scoring**. C1 GitHub Actions. C2 structure-manifest test. C3 conformance scoreboard section in CONFORMANCE_CHECKLIST.md (per-domain % + AUDIT grades) regenerated by a small script so "iteratively improving" is measurable.

## Per-step protocol (encoded verbatim in CONFORMANCE_PLAN.md)

1. Read `docs/CONFORMANCE_CHECKLIST.md`; pick the top `todo` item of the active phase; mark `in-progress`.
2. Read the milestone's instructions in `docs/CONFORMANCE_PLAN.md` + cited references (`C:\Users\Eclipse\.claude\skills\fable-tlc-expert\references\*`).
3. Implement (generators/scripts only — never hand-edit generator-owned output; never run `--full` until 0.1 is green).
4. Validate: `python scripts/build_addon.py` (+ targeted: `gen_screenshots.py`, `_audit_anims.py`, `verify_emotes.py`, `audit_hud.py --check`, `npx eslint packs/Fablecraft_BP/scripts`).
5. Compare/grade vs references; save evidence under `screenshots/`.
6. Update CHECKLIST row (status/evidence/grade/date) + any spec docs.
7. Rewrite `docs/HANDOFF.md` from its template so it always contains a fresh, self-contained continuation prompt for the next agent (current milestone, last commit, validator state, next 3 actions, landmines). This happens after EVERY step, not only at stops.
8. Commit `TLC Conformance — <Phase><n>: <description>` (code + checklist + HANDOFF.md in one commit) and **push to origin immediately** — the pushed repo is the shared source of truth; any agent on any machine resumes from `docs/HANDOFF.md` at origin/HEAD.
9. AskUserQuestion: continue / stop. On stop or context exhaustion: additionally print the HANDOFF.md continuation prompt verbatim in chat.

## Risk register (goes in CONFORMANCE_PLAN.md)
gen_behavior.py regression (0.1 gate); Guild anchor coupling (gen_structures ↔ main.js GUILD; use `fc:reanchor`); generator-owned file edits; dist/ dirtiness; oversized structures (tiling à la `patch_guild_tiling.py`); no automated in-game testing (mitigated by `fc:smoke` + manual checklists); IP exposure (mitigated by Phase L; monetization stays prohibited).

## Verification of this implementation
- `python scripts/build_addon.py` green after Phase 0; regenerated entity diff clean.
- `_audit_anims.py` extended check fails before 0.3 fix, passes after (test the test).
- `--branding=original` package contains zero Fable proper nouns (validator grep proves it).
- Docs exist, CHECKLIST rows carry commit-hash evidence, CI runs green on push.
- In-game: `/scriptevent fc:smoke` prints all-PASS.

## Execution scope after approval
Create the document set + LEGAL scaffolding, then execute Phase 0 (0.1–0.4) under the per-step protocol — committing, pushing, updating the checklist, and checking with the user after each step exactly as prescribed. Subsequent phases proceed the same way.

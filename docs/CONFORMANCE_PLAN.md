# TLC Conformance execution playbook

Updated 2026-09-12. This is the executable expansion of [the approved source plan](SOURCE_PLAN.md).
The latest user instruction authorizes finishing the spell WIP and continuing through as much
of the plan as practical without permission questions. It supersedes the old per-step pause,
but not separate commits, validation, pushing or honest handoffs.

## Start here on either machine

1. Read [HANDOFF.md](HANDOFF.md) and [CONFORMANCE_CHECKLIST.md](CONFORMANCE_CHECKLIST.md).
2. Repository Linux path: `/run/media/eclipse/8E025A94025A80DF/Users/Eclipse/Fablecraft`;
   Windows: `C:\Users\Eclipse\Fablecraft`. Branch `phase3-will-destiny`, remote
   `https://github.com/hipstereclipse/FableCraft.git`. Verify both before mutation.
3. Run `git pull --ff-only` without autostashing. If unrelated dirty files prevent a
   required fast-forward, preserve them and use an isolated checkout; never reset them.
   A no-op up-to-date pull is safe with this tree. No force push.
4. Read every diff with `--ignore-cr-at-eol`. About 699 tracked paths initially looked
   modified; only 11 had substantive differences. Do not use `git add -A`, `git commit -a`,
   renormalization or a new .gitattributes. Stage named paths only. For already tracked
   text, use a reviewed `git diff --ignore-cr-at-eol --binary HEAD -- <explicit paths>`
   patch and `git apply --cached --ignore-whitespace <patch>` to avoid staging baseline
   newline churn. Inspect the staged diff and numstat before commit.
5. Use Python 3 and npm dependencies (`npm ci`). Current baseline here: Python 3.14.7,
   Node 26.7.0, ESLint 10.5.0; Node >=22.13 is a candidate CI runtime, to verify in C1.
   Python render tools need Pillow and NumPy; inspect imports for other dependencies.

## Source and confidence rules

Portable snapshots of the user-supplied references are in `docs/references/fable-tlc-expert/`:

- [Index](references/fable-tlc-expert/fablecraft_index.md): file and data lookup; counts are stale.
- [Architecture](references/fable-tlc-expert/architecture.md): region landmarks and topology.
- [Expressions](references/fable-tlc-expert/emotes.md): 31 expressions, unlocks and opinion directions.
- [Visual reference](references/fable-tlc-expert/visual_reference.md): original 2005 TLC silhouettes.
- [UI guide](references/fable-tlc-expert/UIofFable.md): HUD, menus, travel and morality.
- [FullWorld](references/fable-tlc-expert/FableCraft_BuildSpec_FullWorld.md): numbered region build sections.

Below, a bare reference filename means that snapshot; FullWorld means the last link.
[C] = documented canon in these references; [G] = game-look inference requiring screenshot
comparison; [B] = implementation/design decision. These are source confidence labels, not
proof of historical accuracy. The snapshots contain acknowledged contradictions and later-game
corroboration; verify uncertain details before implementation. Do not add a Fable II/III
breadcrumb trail, vendor expression manuals, or invented numerical canon. Exact region sizes,
block palettes, timers, prices and damage are [B] unless separately supported. No assets may
be extracted from Fable. Reference material is developer documentation, never a pack asset.

Original machine sources are under `/run/media/eclipse/8E025A94025A80DF/Users/Eclipse/.claude/`:
`skills/fable-tlc-expert/` and `projects/c--Users-Eclipse-Fablecraft/memory/` (MEMORY.md index).
Read relevant memory files there when available, but current code/user directions supersede
stale claims. In particular memory calls fable_hud.js hand-authored; this task explicitly
protects it as generator-owned. Find or establish its generator before modifying it.

## Reverified starting facts

- Base at 6cfea15; spell completion and lint prerequisites separately pushed as ccafd4c.
- There are **51 MOBS definitions**, **194 data items**, **23 scatter entries** and **34 RP
  particles**. These are not the same counts as emitted files; player/overlay assets add files.
- The live build validates 685 JSON, 341 PNG, 535 WAV, 29 structures, 55 scripts after adding
  Ghost Sword. It passes 31-expression/21-social-NPC and 112/112 HUD checks.
- There is no automated in-world test loop. Spell mocks pass 17 cases; runtime checks pending.
- The older gen_behavior working copy is still unsafe until 0.1. No genuinely new content was
  found in its 254-line diff against base. Never run it or --full before that milestone is green.
- Gate variable attack_time has no explicit script assignment because it is engine-owned;
  0.3 corrects the stale premise and audits compatible melee sources (see ANIMATION_AUDIT.md).
- README count drift extends beyond Will powers. Existing binaries use faithful names and
  must stay local/legacy until L4. Bootstrap does not claim the naming layer exists.
- npm/ESLint files were ignored and config was obsolete. ccafd4c adopts them; lint now has
  zero errors and 19 warnings about existing unused code. Empty catches are intentionally
  allowed for invalidated Bedrock handles; other recommended error rules remain active.

## Locked decisions and hazards

Faithful names locally; original names in every distributed build. Free, never monetized.
Parody is not a defense. Keep the procedural scatter engine and deepen/add POIs, no fixed
Albion map, even where a source recommends fixed region topology.

Do not hand-edit generator-owned BP entities, RP models/entity/animations/controllers/
attachables/particles, fable_emote_registry.js, fable_hud.js, fc_gamedata.js or
texts/languages.json. Check ownership for other outputs before editing. Regenerate only
through scripts. `--full` is forbidden until 0.1 passes; afterward prefer targeted generators
and review drift (e.g. Will Focus charge components) rather than assuming full regeneration safe.

Guild local coordinates in gen_structures.py and main.js GUILD must remain in lockstep:
footprint, wake, map, quest, skill/Cullis, Maze study, training, door, cave/chamber and terrain
bounds. Recheck actual GUILD_LAYOUT before copying remembered coordinates. For an existing
world, `/scriptevent fc:reanchor` refreshes anchors; it does not prove geometry/placement.
The build's `all cross-references OK` is never anchor-coupling evidence. HUD text order,
blank glyph spacers and clip offsets are another coupled contract; use faithful preview.

Rebuild dist only during milestone validation, not every intermediate edit. Until L4, the
required build's output is local development evidence, must remain unstaged and unpublished.
Existing archive dirtiness and alignment PNG scratch outputs are pre-existing; preserve them.
Do not execute patch_guild_tiling.py: it targets an older layout and requires a separate audit.

## Mandatory milestone loop (current user override applied)

1. `git pull --ff-only`; read HANDOFF + CHECKLIST; choose the top todo leaf in the active
   phase and mark in-progress. Order: 0, L, W, E, V, M, C. M0 supplies the planned smoke harness.
2. Read the numbered instructions below, their references and relevant current source.
3. Implement only that milestone; do not combine unrelated milestones or touch generated
   outputs by hand. Keep the completed spell prerequisite separate from conformance commits.
4. Run the base validator recipe and every applicable domain/leaf test. Preserve actual
   outputs. On failure, fix/retest or record red and stop dependent work; never claim green.
5. Compare/grade against the cited references; save new render evidence under screenshots/.
   Generated composites are not in-game evidence. Give manual tests explicit unchecked boxes.
6. Update the checklist row: status, commit reference, evidence paths, grade, date; update specs.
   A single commit cannot embed its own hash. Use `SELF: <exact commit subject>` in new rows,
   resolved with `git log -1 --format=%H --grep='<subject>'`; at the next milestone replace
   the previous SELF with its actual hash. Never invent a hash or amend recursively.
7. Rewrite HANDOFF as a self-contained continuation prompt with previous resolved commit,
   current containing-commit resolver, validator green/red/unrun, next three actions and hazards.
8. ONE conformance commit: `TLC Conformance — <ID>: <description>`, explicit staging only;
   push origin immediately and verify response. If push is unavailable, record local-only,
   preserve commits and complete independent work; never assert origin matches without evidence.
9. The source plan requested continue/stop after each milestone. The user explicitly removed
   those pauses on 2026-09-12. Continue autonomously; at context limits print HANDOFF's
   continuation prompt verbatim. Never mark an unfinished objective complete to stop.

## Validator recipes

### Base recipe (every milestone, including documentation)

From repository root, at the milestone boundary:

```sh
python scripts/build_addon.py
python scripts/verify_emotes.py
python scripts/audit_hud.py --check
npx --no-install eslint packs/Fablecraft_BP/scripts
node --experimental-vm-modules scripts/tests/spells.test.mjs
```

Build already invokes emote/HUD validators, but explicit logs make results independently
reviewable. Save stdout/stderr and exit codes under `screenshots/validation/<ID>/`; use
shell redirection then capture `$?` immediately (do not hide failures behind `tee`). The
Node test is invoked directly because this machine's process-isolated `--test` runner
failed without surfacing worker output; direct node:test execution correctly reports failure.
Syntax-check new JS with node --check. Run animation audit for changed animation/entities
(and every milestone after 0.3), behavior regression after 0.1, and appropriate new tests.
No screenshot regeneration is needed for docs-only edits; mark render checks not applicable.
Do not run --full as a substitute for understanding the change.

### World recipe (each W leaf; mandatory in addition to its numbered instructions)

1. Read the exact generator function, its `Vox` dimensions and its `save()` ID. Compare
   STRUCTS footprint/surface/weight and spawn/loot/travel flags in runtime main.js.
2. Record local feature coordinates and an entrance-to-interaction walking route; add
   generator and runtime changes together, retaining scatter and stable saved IDs.
3. For isolated generation before a full screenshot pass, use this pattern with the actual
   function substituted for `focus_site` (these Python APIs exist):

```sh
PYTHONPATH=scripts python - <<'PYCODE'
import gen_structures as gs
from gen_screenshots import render_structure
captured = {}
original = gs.Vox.save
try:
    gs.Vox.save = lambda self, name: captured.__setitem__(name, self)
    gs.focus_site()
finally:
    gs.Vox.save = original
for name, vox in captured.items():
    render_structure(vox).save(f"screenshots/structures/{name}_conformance.png")
PYCODE
```

4. Generate the actual changed structure using its function (`PYTHONPATH=scripts python -c
   'import gen_structures as g; g.focus_site()'` with the actual function), then
   `python scripts/gen_screenshots.py` at the milestone boundary. It currently renders all
   categories and rewrites AUDIT.md; inspect changes and stage only relevant evidence.
5. Check non-magenta block palette, silhouette, gates/stairs/interiors and local interaction
   anchors. Record observed deficiencies and grades against original TLC references, not an
   automatic aesthetic score. Guild edits additionally run `_audit_match.py`, `_audit_roofs.py`
   and explicit GUILD_LAYOUT↔GUILD coordinate comparison; external map diagnostics are optional
   if the source reference image is missing, but that absence cannot imply visual conformance.
6. Run base + `_audit_anims.py`; C2 adds structure-manifest tests when implemented. In a new
   world place/explore the POI on every supported terrain class; check floor/door/chest/NPC/
   Cullis positions. In an existing world verify retained IDs and anchor refresh as relevant.

### Entity / VFX recipes

Entity changes: run `python scripts/gen_entity_textures.py`, `python scripts/gen_behavior.py`
(only after 0.1), `python scripts/gen_resources.py` and `python scripts/gen_emotes.py` as
applicable; compare every substantive generated diff. Run `_audit_anims.py`, behavior
regression and `verify_emotes.py`, then render `gen_screenshots.py` and inspect changed mobs.
Do not claim pose renders prove controller execution. Use the in-world state checklist.

VFX changes: read gen_wd.main before choosing its arguments; `python scripts/gen_wd.py`
is the current generator. Run gen_resources only if it owns a changed emitter/asset.
Extend and run `python scripts/gen_doc_screenshots.py`; inspect scenes and indexed paths.
Test trigger/cancel/expiry, multiple players, distance culling and particle budgets in-game.

### Evidence grades

Use `PASS (automated)` for nonvisual engineering gates, `PENDING (manual)` when world
verification is required, and A/B/C/D only with a written visual rubric and inspected
comparison. A = all required landmarks/behaviors and no observed defect; B = minor visual
mismatch; C = substantial missing fidelity; D = broken/missing. An inherited AUDIT grade
is historical evidence, not a new comparison. Row status can be done only when its stated
acceptance is fulfilled; code delivered with required manual verification outstanding stays
in-progress and is clearly distinguished from untouched todo work.

## Numbered milestone instructions

### 0.1 — Repair behavior generator

References: [B] code audit; [C] emotes.md: NPC opinion axes.

Files: `scripts/gen_behavior.py`, `scripts/tests/test_gen_behavior.py`.

1. Compare `git diff --ignore-cr-at-eol HEAD -- scripts/gen_behavior.py` and `git show 6cfea15:scripts/gen_behavior.py`. Back up the old working copy under ignored tmp/conformance. Current diff contains regressions only: object icons/damage, missing social/bounty/training/persistence/marriage/cosmetic code. Preserve anything genuinely new if this changes.
2. Restore the proven generator from 6cfea15 using `git show 6cfea15:scripts/gen_behavior.py > scripts/gen_behavior.py` (or checkout only this path). Do not regenerate the full pack yet.
3. Write a unittest that redirects gen_behavior.BP to TemporaryDirectory, emits Theresa plus every data item through its actual category emitter, and compares JSON to checked-in entity/item contracts. Assert react_flee/react_attack/react_neutral, social client-sync properties, persistent-without-despawn, scalar icon and damage formats. Check Will Focus charging components separately; exact outputs may include later intentional changes.
4. Run the new test against the backed-up stripped module to demonstrate failure, then against the repaired module. Emit Theresa in isolation and compare parsed JSON with the existing pack; no hand edits to entities/items.
5. Run the **base** recipe (base always applies), save evidence, update checklist and HANDOFF, commit this leaf and push.

Acceptance: Before-fix regression fails, repaired test passes; Theresa react events and all 194 data-item icon formats survive; build/emote/HUD/lint green. Only then lift the gen_behavior/--full hazard gate.

### 0.2 — Adopt orphan tools and output policy

References: [B] code audit; [G] visual_reference.md: Core Look.

Files: `scripts/audit_hud.py`, `scripts/preview_hud_faithful.py`, `scripts/_audit_anims.py`, `scripts/_audit_match.py`, `scripts/_audit_roofs.py`, `scripts/_target_map.py`, `.gitignore`, `patch_guild_tiling.py`.

1. Inventory `git ls-files --others --exclude-standard`. Read each candidate before adding it. Ghost Sword was already completed separately in ccafd4c; never duplicate it in this milestone.
2. Commit the six audit/preview Python files with their required inputs and existing screenshots/ui evidence. Identify hard-coded Windows paths or external map inputs; make root paths portable or report optional diagnostics unavailable. Compile the tools; do not run one-off patch scripts as validators.
3. Ignore tmp/ and redundant scratch alignment renders; preserve all existing files on disk. Keep named curated screenshots. Node tooling was adopted as a prerequisite in ccafd4c; stop ignoring its tracked package manifests/config.
4. Inspect patch_guild_tiling.py against current guild_hall/save and runtime placement. It is a one-off migration, not a build step. Archive with a warning if not needed; if needed, implement tiling as a separately audited coupled change, never run the patch blindly.
5. Record package policy: required build validates and packages locally at milestone boundaries; never stage development archives until L4 original branding passes. Commit dist only for validated milestone releases. Run animation audit but note that its pre-0.3 exit code may hide problems.
6. Run the **base** recipe (base always applies), save evidence, update checklist and HANDOFF, commit this leaf and push.

Acceptance: Tools reproducible or clearly marked optional with missing inputs; no untracked dependency in required build; tmp ignored; patch fate documented; no faithful distribution artifacts staged.

### 0.3 — Validate attack gates and remove unsupported melee overlays

References: [B] current Bedrock wiring and [official sources in ANIMATION_AUDIT.md](ANIMATION_AUDIT.md); [G] visual_reference.md: readable silhouettes.

Files: `scripts/gen_resources.py`, `scripts/_audit_anims.py`, `scripts/tests/test_animation_audit.py`, three generated RP client entities.

1. Reverified 2026-09-12: the engine supplies variable.attack_time. The original claim of a globally missing driver was stale; preserve engine progress and never substitute query.attack_time or a fabricated timer.
2. The new entity-local audit must reject gates without a compatible assignment/engine binding. Run `python scripts/tests/test_animation_audit.py` for negative and positive fixtures, including unrelated-entity assignments, dead states and CLI exit status.
3. Before changing the generator, `python scripts/_audit_anims.py` rejected bandit_archer, hobbe_scout and summoner: they had a melee overlay but only ranged/caster BP goals. Raw failure is saved in screenshots/validation/0.3/before.log.
4. gen_resources.py omits only those unsupported melee overlays. Regenerate with `python scripts/gen_resources.py`, review the three entity diffs and run `python scripts/_audit_anims.py`: 54 client entities should pass. Preserve bow controllers and defer summoner signature casting to E3.
5. Run base validators and behavior regression. Follow docs/ANIMATION_AUDIT.md's in-world idle/strike/recovery/NPC/ranged checklist and record engine-version evidence. Existing geometry/clip art did not change; static pose renders cannot prove event timing.
6. Keep row in-progress while required manual tests remain unrun. Code/automated work can be committed/pushed, and independent documentation work can continue without claiming runtime conformance.

Acceptance: honest source-corrected mechanism, actual before-fix audit failure and after-fix pass, ten negative/positive regression cases, base suite green, and observed in-world idle/strike behavior. The last requirement is pending.

### 0.4 — Synchronize gameplay documentation

References: [B] live code; [C] emotes.md: 31 expressions.

Files: `README.md`, `BOUNTY_SYSTEM.md`, `packs/Fablecraft_BP/scripts/wd/spells/registry.js`, `packs/Fablecraft_BP/scripts/main.js`.

1. Count the live registry, data items, recipes, mob definitions, emitted entities, structures and audio separately; do not repeat the stale reference index counts.
2. Replace all four README references to 17 Will powers/spells with 18. Explain live wd casting and the legacy progression funnel accurately. Correct the headline counts if verified; label definitions versus emitted entities.
3. Review the existing BOUNTY_SYSTEM.md diff against accrueCrime, guild jurisdiction, tick clock, wanted decay and fc:wanted/fc:clearwanted handlers. Preserve genuine edits and remove superseded Guild Heat claims. Keep manual checks unchecked unless performed.
4. Run base validators and `rg -n "17 Will|17 spells|Guild Heat" README.md BOUNTY_SYSTEM.md`; remaining matches must be explicit historical context.
5. Run the **base** recipe (base always applies), save evidence, update checklist and HANDOFF, commit this leaf and push.

Acceptance: README and bounty spec describe current code; registry has 18 live casts; no claimed in-game pass without evidence.

### L1 — Verify fan-work notice and release posture

References: [B] project policy; LEGAL.md.

Files: `LEGAL.md`, `README.md`.

1. Bootstrap already adds the notice. Verify unaffiliated, free/non-commercial, original/generated/no-extraction, Microsoft marks and takedown compliance language. Check donation solicitations and paid-release instructions are gone.
2. Review LICENSE compatibility and avoid implying this notice revokes an existing code license. Keep disclaimer distinct from actual clearance and name-layer completion. Use official sources when giving legal guidance.
3. Confirm all archived faithful packages are marked legacy/local-only. This milestone can be marked done with bootstrap evidence, then confirm it in its own checklist/handoff commit after Phase 0.
4. Run the **base** recipe (base always applies), save evidence, update checklist and HANDOFF, commit this leaf and push.

Acceptance: All required notice elements present, no monetization solicitations, no claim that naming or disclaimers establish legal permission.

### L2 — Generator string table and local/original mode

References: [B] original names; [C] fablecraft_index.md: data IDs.

Files: `scripts/fc_strings.py`, `scripts/fc_branding.py`, `scripts/gen_behavior.py`, `scripts/gen_resources.py`, `scripts/build_addon.py`, `scripts/tests/test_branding.py`. Canonical faithful catalogs fc_data/fc_mobs remain unchanged; their display output routes through emitters.

1. Inventory user-facing proper nouns across data, items, lore, languages, manifests, names and generated scripts using `rg -n "Fable|Albion|Guild|Bowerstone|Oakvale|Jack|Avo|Skorm" scripts packs`. Expand the inventory beyond this seed, record every pair in fc_strings.py, and keep generic words separate from distinctive names.
2. Implement faithful/original pairs with stable semantic keys and a strict accessor that errors on missing keys/modes. Add argparse --branding=faithful|original, explicit local-vs-release output policy, and pass mode to generators. Preserve saved-world IDs unless an explicit migration maps them.
3. Route the L2 generator-owned display text (item display_name/lore, generated fc_gamedata, actual .lang contents and manifests; emotes/HUD owners follow in L3.3) through the table. languages.json is only a language list; do not mistake changing it for translating the text. Generate only through owners.
4. Add tests for missing keys, both modes, interpolation and accented/color-coded strings. Build both modes into separate temporary staging trees so an original build cannot contaminate local faithful sources. Do not claim zero packaged literals until L3/L4 finishes.
5. Use `python scripts/build_addon.py --branding original --preview` for the isolated original tree, and `python scripts/tests/test_branding.py` for the generator/isolation and negative audit tests. Write a temporary tracked debt inventory of remaining runtime literals by file; no silent release bypass. Keep original-mode packaging blocked until complete.
6. Run the **base** recipe (base always applies), save evidence, update checklist and HANDOFF, commit this leaf and push.

Acceptance: Both naming modes produce consistent L2 generated text; saved IDs unchanged or migrated; tests verify routing and isolation; no false release-ready claim.

### L3.1 — Runtime strings and menu hub

References: [C] UIofFable.md: Menu System/Fast Travel; [B] string indirection.

Files: `scripts/fc_strings.py`, `packs/Fablecraft_BP/scripts/fc_strings.js (generated)`, `packs/Fablecraft_BP/scripts/main.js`, `packs/Fablecraft_BP/scripts/wd/herobook.js`, `packs/Fablecraft_BP/scripts/wd/menu_bridge.js`.

1. Generate fc_strings.js from the same Python table; never maintain a second translation table. Import the accessor in this milestone's handwritten runtime files; locate strings with rg and migrate whole messages including interpolation.
2. Keep internal IDs, property keys, script events, texture paths and menu_bridge contracts stable. Resolve pack-path leaks through a future packaging map rather than breaking world saves. Add explicit mode tests for every migrated menu/message family.
3. Shrink the tracked per-file literal debt list; exemptions can document unfinished migration but must never exempt a public release. Inspect menu labels, quest destinations, logbook text, HUD payload and errors in both modes.
4. Run base validators, string tests, and audit_hud --check plus preview_hud_faithful.py if HUD sources changed. Preserve HUD payload/clip arithmetic and generator ownership.
5. Run the **base** recipe (base always applies), save evidence, update checklist and HANDOFF, commit this leaf and push.

Acceptance: All strings in this file group are table-owned, interpolation correct, debt shrinks, menus remain connected; both-mode manual menu checks recorded.

### L3.2 — Runtime quests, towns, shops and crime

References: [C] UIofFable.md: Menu System/Fast Travel; [B] string indirection.

Files: `scripts/fc_strings.py`, `packs/Fablecraft_BP/scripts/fc_strings.js (generated)`, `packs/Fablecraft_BP/scripts/main.js`.

1. Generate fc_strings.js from the same Python table; never maintain a second translation table. Import the accessor in this milestone's handwritten runtime files; locate strings with rg and migrate whole messages including interpolation.
2. Keep internal IDs, property keys, script events, texture paths and menu_bridge contracts stable. Resolve pack-path leaks through a future packaging map rather than breaking world saves. Add explicit mode tests for every migrated menu/message family.
3. Shrink the tracked per-file literal debt list; exemptions can document unfinished migration but must never exempt a public release. Inspect menu labels, quest destinations, logbook text, HUD payload and errors in both modes.
4. Run base validators, string tests, and audit_hud --check plus preview_hud_faithful.py if HUD sources changed. Preserve HUD payload/clip arithmetic and generator ownership.
5. Run the **base** recipe (base always applies), save evidence, update checklist and HANDOFF, commit this leaf and push.

Acceptance: All strings in this file group are table-owned, interpolation correct, debt shrinks, menus remain connected; both-mode manual menu checks recorded.

### L3.3 — Will modules, logbook and generated HUD text

References: [C] UIofFable.md: Menu System/Fast Travel; [B] string indirection.

Files: `scripts/fc_strings.py`, `packs/Fablecraft_BP/scripts/fc_strings.js (generated)`, `packs/Fablecraft_BP/scripts/wd/`, `scripts/gen_hud_runtime.py`, `scripts/templates/hud_runtime.js`, `scripts/gen_emotes.py`. gen_ui/gen_hud_font own pixel assets, not runtime display prose.

1. Generate fc_strings.js from the same Python table; never maintain a second translation table. Import the accessor in this milestone's handwritten runtime files; locate strings with rg and migrate whole messages including interpolation.
2. Keep internal IDs, property keys, script events, texture paths and menu_bridge contracts stable. Resolve pack-path leaks through a future packaging map rather than breaking world saves. Add explicit mode tests for every migrated menu/message family.
3. Shrink the tracked per-file literal debt list; exemptions can document unfinished migration but must never exempt a public release. Inspect menu labels, quest destinations, logbook text, HUD payload and errors in both modes.
4. Run base validators, string tests, and audit_hud --check plus preview_hud_faithful.py if HUD sources changed. Preserve HUD payload/clip arithmetic and generator ownership.
5. Run the **base** recipe (base always applies), save evidence, update checklist and HANDOFF, commit this leaf and push.

Acceptance: All strings in this file group are table-owned, interpolation correct, debt shrinks, menus remain connected; both-mode manual menu checks recorded.

### L4 — Enforce original-only release packaging

References: [B] release policy; LEGAL.md.

Files: `scripts/build_addon.py`, `scripts/fc_strings.py`, `scripts/scan_branding.py`, `scripts/tests/test_branding.py`, `scripts/tests/test_branding_scan.py`, `pack manifests`.

1. Prepare original public-name proposals and record the final user-selected name when available. In an autonomous session, a provisional internal name may support tests but must not be represented as the user's final selection.
2. Implement a recursive scanner over archive filenames, nested archives and all textual payloads (JSON/JS/lang/metadata). Normalize case, escapes and separators; scan exact distinctive phrases/tokens with documented generic-word handling. Local faithful builds must never write release dist paths.
3. Remove every runtime exemption. Original releases must reject faithful literals even in comments, identifiers/paths and nested packs. If stable runtime IDs contain protected names, implement an isolated packaging remap covering every reference and document saved-world compatibility; do not use raw blind replacement.
4. Inject one forbidden name into each supported output type and nested pack to prove failure. Build `python scripts/build_addon.py --branding=original` only once the flag exists; inspect all three archives and manifests, then verify faithful sources remain unchanged.
5. Only after a zero-debt scan and final branding selection may reviewed original-only dist archives be staged at a milestone release. Free distribution only.
6. Run the **base** recipe (base always applies), save evidence, update checklist and HANDOFF, commit this leaf and push.

Acceptance: Zero forbidden packaged literals, no exemptions, negative tests fail, original public title selected, faithful local build isolated; existing saves handled explicitly.

2026-09-12 checkpoint: recursive scanning and 15 regression groups pass; actual original preview still has 2,512 findings. Packaging stays blocked even for a clean static fixture. See docs/RELEASE_SCANNING.md for supported formats, conservative generic-word policy, limitations and remaining remap/review work. L4 is in-progress.

### W1.1 — Cullis gate

References: [C] architecture.md: World Overview; UIofFable.md: Fast Travel; [G] visual_reference.md: Core Look; [B] scatter adaptation.

Files: `scripts/gen_structures.py`, `packs/Fablecraft_BP/scripts/main.js`, `scripts/gen_screenshots.py`, `screenshots/AUDIT.md`.

1. Inspect generator `focus_site` (strip " (new)" for the proposed new Python name), STRUCTS and all fc:place/travel/loot references. Write the footprint and feature-local coordinates before implementation. Required recognizable features: Round weathered stone disc and blue glow; replace generic proxy while preserving existing travel registration.
2. Use the World recipe below in full. For a new POI implement the named generator, call it from main(), register STRUCTS with actual width/depth/weight/surface/theme and explicit loot/mobs/door/cullis flags. Existing POIs retain save IDs where possible.
3. Read the cited region section and use its [C] landmarks; block palettes and dimensions are [B], with [G] appearance verified against actual original-TLC reference shots. Keep provenance and comparison notes with each image.
4. Render this structure alone first, check bounds and magenta unknown blocks, then run the full screenshot generator at the milestone boundary. Inspect entrances, floor heights, interiors, lighting and spawn/interaction coordinates; document a walk-through route and failures.
5. Run the **world** recipe (base always applies), save evidence, update checklist and HANDOFF, commit this leaf and push.

Acceptance: Cullis gate landmarks visible; emitted footprint matches runtime; no missing palette entries or broken interaction anchors; render and AUDIT row agree. In-world placement/walk-through pending until checked.

### W1.2 — Lychfield crypt

References: [C] architecture.md: Lychfield; FullWorld §9; [G] visual_reference.md: Core Look; [B] scatter adaptation.

Files: `scripts/gen_structures.py`, `packs/Fablecraft_BP/scripts/main.js`, `scripts/gen_screenshots.py`, `screenshots/AUDIT.md`.

1. Inspect generator `graveyard` (strip " (new)" for the proposed new Python name), STRUCTS and all fc:place/travel/loot references. Write the footprint and feature-local coordinates before implementation. Required recognizable features: Nostro crypt, sarcophagi, gravekeeper hut and gate-stair stone face; preserve graveyard spawns.
2. Use the World recipe below in full. For a new POI implement the named generator, call it from main(), register STRUCTS with actual width/depth/weight/surface/theme and explicit loot/mobs/door/cullis flags. Existing POIs retain save IDs where possible.
3. Read the cited region section and use its [C] landmarks; block palettes and dimensions are [B], with [G] appearance verified against actual original-TLC reference shots. Keep provenance and comparison notes with each image.
4. Render this structure alone first, check bounds and magenta unknown blocks, then run the full screenshot generator at the milestone boundary. Inspect entrances, floor heights, interiors, lighting and spawn/interaction coordinates; document a walk-through route and failures.
5. Run the **world** recipe (base always applies), save evidence, update checklist and HANDOFF, commit this leaf and push.

Acceptance: Lychfield crypt landmarks visible; emitted footprint matches runtime; no missing palette entries or broken interaction anchors; render and AUDIT row agree. In-world placement/walk-through pending until checked.

### W1.3 — Twinblade tent rings

References: [C] architecture.md: Twinblade; FullWorld §10; [G] visual_reference.md: Core Look; [B] scatter adaptation.

Files: `scripts/gen_structures.py`, `packs/Fablecraft_BP/scripts/main.js`, `scripts/gen_screenshots.py`, `screenshots/AUDIT.md`.

1. Inspect generator `bandit_camp` (strip " (new)" for the proposed new Python name), STRUCTS and all fc:place/travel/loot references. Write the footprint and feature-local coordinates before implementation. Required recognizable features: Palisades/checkpoints, command tent, fighting circle, stalls and campfires.
2. Use the World recipe below in full. For a new POI implement the named generator, call it from main(), register STRUCTS with actual width/depth/weight/surface/theme and explicit loot/mobs/door/cullis flags. Existing POIs retain save IDs where possible.
3. Read the cited region section and use its [C] landmarks; block palettes and dimensions are [B], with [G] appearance verified against actual original-TLC reference shots. Keep provenance and comparison notes with each image.
4. Render this structure alone first, check bounds and magenta unknown blocks, then run the full screenshot generator at the milestone boundary. Inspect entrances, floor heights, interiors, lighting and spawn/interaction coordinates; document a walk-through route and failures.
5. Run the **world** recipe (base always applies), save evidence, update checklist and HANDOFF, commit this leaf and push.

Acceptance: Twinblade tent rings landmarks visible; emitted footprint matches runtime; no missing palette entries or broken interaction anchors; render and AUDIT row agree. In-world placement/walk-through pending until checked.

### W1.4 — Arena halls

References: [C] architecture.md: Arena; FullWorld §8; [G] visual_reference.md: Core Look; [B] scatter adaptation.

Files: `scripts/gen_structures.py`, `packs/Fablecraft_BP/scripts/main.js`, `scripts/gen_screenshots.py`, `screenshots/AUDIT.md`.

1. Inspect generator `arena_ring` (strip " (new)" for the proposed new Python name), STRUCTS and all fc:place/travel/loot references. Write the footprint and feature-local coordinates before implementation. Required recognizable features: Tiered seating, inward statues, waiting room with dummies/shop, adjoining Hall of Heroes.
2. Use the World recipe below in full. For a new POI implement the named generator, call it from main(), register STRUCTS with actual width/depth/weight/surface/theme and explicit loot/mobs/door/cullis flags. Existing POIs retain save IDs where possible.
3. Read the cited region section and use its [C] landmarks; block palettes and dimensions are [B], with [G] appearance verified against actual original-TLC reference shots. Keep provenance and comparison notes with each image.
4. Render this structure alone first, check bounds and magenta unknown blocks, then run the full screenshot generator at the milestone boundary. Inspect entrances, floor heights, interiors, lighting and spawn/interaction coordinates; document a walk-through route and failures.
5. Run the **world** recipe (base always applies), save evidence, update checklist and HANDOFF, commit this leaf and push.

Acceptance: Arena halls landmarks visible; emitted footprint matches runtime; no missing palette entries or broken interaction anchors; render and AUDIT row agree. In-world placement/walk-through pending until checked.

### W2.1 — Bowerstone North and Manor

References: [C] architecture.md: Bowerstone; FullWorld §3; [G] visual_reference.md: Core Look; [B] scatter adaptation.

Files: `scripts/gen_structures.py`, `packs/Fablecraft_BP/scripts/main.js`, `scripts/gen_screenshots.py`, `screenshots/AUDIT.md`.

1. Inspect generator `bowerstone_market` (strip " (new)" for the proposed new Python name), STRUCTS and all fc:place/travel/loot references. Write the footprint and feature-local coordinates before implementation. Required recognizable features: Readable wealthy district, internal class gate, proper manor and connected streets; adapt scatter footprint, no fixed map.
2. Use the World recipe below in full. For a new POI implement the named generator, call it from main(), register STRUCTS with actual width/depth/weight/surface/theme and explicit loot/mobs/door/cullis flags. Existing POIs retain save IDs where possible.
3. Read the cited region section and use its [C] landmarks; block palettes and dimensions are [B], with [G] appearance verified against actual original-TLC reference shots. Keep provenance and comparison notes with each image.
4. Render this structure alone first, check bounds and magenta unknown blocks, then run the full screenshot generator at the milestone boundary. Inspect entrances, floor heights, interiors, lighting and spawn/interaction coordinates; document a walk-through route and failures.
5. Run the **world** recipe (base always applies), save evidence, update checklist and HANDOFF, commit this leaf and push.

Acceptance: Bowerstone North and Manor landmarks visible; emitted footprint matches runtime; no missing palette entries or broken interaction anchors; render and AUDIT row agree. In-world placement/walk-through pending until checked.

### W2.2 — Hook Coast lighthouse and Abbey

References: [C] architecture.md: Hook Coast; FullWorld §5; [G] visual_reference.md: Core Look; [B] scatter adaptation.

Files: `scripts/gen_structures.py`, `packs/Fablecraft_BP/scripts/main.js`, `scripts/gen_screenshots.py`, `screenshots/AUDIT.md`.

1. Inspect generator `hook_coast` (strip " (new)" for the proposed new Python name), STRUCTS and all fc:place/travel/loot references. Write the footprint and feature-local coordinates before implementation. Required recognizable features: Harbor lighthouse with climbable interior, ruined Abbey, graveyard/bell and stairs between tiers.
2. Use the World recipe below in full. For a new POI implement the named generator, call it from main(), register STRUCTS with actual width/depth/weight/surface/theme and explicit loot/mobs/door/cullis flags. Existing POIs retain save IDs where possible.
3. Read the cited region section and use its [C] landmarks; block palettes and dimensions are [B], with [G] appearance verified against actual original-TLC reference shots. Keep provenance and comparison notes with each image.
4. Render this structure alone first, check bounds and magenta unknown blocks, then run the full screenshot generator at the milestone boundary. Inspect entrances, floor heights, interiors, lighting and spawn/interaction coordinates; document a walk-through route and failures.
5. Run the **world** recipe (base always applies), save evidence, update checklist and HANDOFF, commit this leaf and push.

Acceptance: Hook Coast lighthouse and Abbey landmarks visible; emitted footprint matches runtime; no missing palette entries or broken interaction anchors; render and AUDIT row agree. In-world placement/walk-through pending until checked.

### W2.3 — Oakvale Memorial Garden

References: [C] architecture.md: Oakvale; FullWorld §2; [G] visual_reference.md: Core Look; [B] scatter adaptation.

Files: `scripts/gen_structures.py`, `packs/Fablecraft_BP/scripts/main.js`, `scripts/gen_screenshots.py`, `screenshots/AUDIT.md`.

1. Inspect generator `oakvale_village` (strip " (new)" for the proposed new Python name), STRUCTS and all fc:place/travel/loot references. Write the footprint and feature-local coordinates before implementation. Required recognizable features: Path to garden, axe-bearing hero statue, graves, coastal tree/well village preserved.
2. Use the World recipe below in full. For a new POI implement the named generator, call it from main(), register STRUCTS with actual width/depth/weight/surface/theme and explicit loot/mobs/door/cullis flags. Existing POIs retain save IDs where possible.
3. Read the cited region section and use its [C] landmarks; block palettes and dimensions are [B], with [G] appearance verified against actual original-TLC reference shots. Keep provenance and comparison notes with each image.
4. Render this structure alone first, check bounds and magenta unknown blocks, then run the full screenshot generator at the milestone boundary. Inspect entrances, floor heights, interiors, lighting and spawn/interaction coordinates; document a walk-through route and failures.
5. Run the **world** recipe (base always applies), save evidence, update checklist and HANDOFF, commit this leaf and push.

Acceptance: Oakvale Memorial Garden landmarks visible; emitted footprint matches runtime; no missing palette entries or broken interaction anchors; render and AUDIT row agree. In-world placement/walk-through pending until checked.

### W2.4 — Grey House and cellar

References: [C] architecture.md: Grey House; FullWorld §11; [G] visual_reference.md: Core Look; [B] scatter adaptation.

Files: `scripts/gen_structures.py`, `packs/Fablecraft_BP/scripts/main.js`, `scripts/gen_screenshots.py`, `screenshots/AUDIT.md`.

1. Inspect generator `grey_house (new)` (strip " (new)" for the proposed new Python name), STRUCTS and all fc:place/travel/loot references. Write the footprint and feature-local coordinates before implementation. Required recognizable features: Isolated manor-cottage, navigable cellar and undead encounter; add standalone scatter entry.
2. Use the World recipe below in full. For a new POI implement the named generator, call it from main(), register STRUCTS with actual width/depth/weight/surface/theme and explicit loot/mobs/door/cullis flags. Existing POIs retain save IDs where possible.
3. Read the cited region section and use its [C] landmarks; block palettes and dimensions are [B], with [G] appearance verified against actual original-TLC reference shots. Keep provenance and comparison notes with each image.
4. Render this structure alone first, check bounds and magenta unknown blocks, then run the full screenshot generator at the milestone boundary. Inspect entrances, floor heights, interiors, lighting and spawn/interaction coordinates; document a walk-through route and failures.
5. Run the **world** recipe (base always applies), save evidence, update checklist and HANDOFF, commit this leaf and push.

Acceptance: Grey House and cellar landmarks visible; emitted footprint matches runtime; no missing palette entries or broken interaction anchors; render and AUDIT row agree. In-world placement/walk-through pending until checked.

### W3.1 — Bargate Prison

References: [C] architecture.md: Bargate; FullWorld §9; [G] visual_reference.md: Core Look; [B] scatter adaptation.

Files: `scripts/gen_structures.py`, `packs/Fablecraft_BP/scripts/main.js`, `scripts/gen_screenshots.py`, `screenshots/AUDIT.md`.

1. Inspect generator `bargate_prison (new)` (strip " (new)" for the proposed new Python name), STRUCTS and all fc:place/travel/loot references. Write the footprint and feature-local coordinates before implementation. Required recognizable features: Fortress courtyard/ramparts, three cell-block silhouettes (two explorable), barracks, warden office and underground chamber; Kraken encounter is deferred, not silently claimed.
2. Use the World recipe below in full. For a new POI implement the named generator, call it from main(), register STRUCTS with actual width/depth/weight/surface/theme and explicit loot/mobs/door/cullis flags. Existing POIs retain save IDs where possible.
3. Read the cited region section and use its [C] landmarks; block palettes and dimensions are [B], with [G] appearance verified against actual original-TLC reference shots. Keep provenance and comparison notes with each image.
4. Render this structure alone first, check bounds and magenta unknown blocks, then run the full screenshot generator at the milestone boundary. Inspect entrances, floor heights, interiors, lighting and spawn/interaction coordinates; document a walk-through route and failures.
5. Run the **world** recipe (base always applies), save evidence, update checklist and HANDOFF, commit this leaf and push.

Acceptance: Bargate Prison landmarks visible; emitted footprint matches runtime; no missing palette entries or broken interaction anchors; render and AUDIT row agree. In-world placement/walk-through pending until checked.

### W3.2 — Bronze Gate and Archon Shrine

References: [C] architecture.md: Northern Wastes; FullWorld §12; [G] visual_reference.md: Core Look; [B] scatter adaptation.

Files: `scripts/gen_structures.py`, `packs/Fablecraft_BP/scripts/main.js`, `scripts/gen_screenshots.py`, `screenshots/AUDIT.md`.

1. Inspect generator `archon_shrine (new)` (strip " (new)" for the proposed new Python name), STRUCTS and all fc:place/travel/loot references. Write the footprint and feature-local coordinates before implementation. Required recognizable features: Domed shrine with three soul sockets, Cullis disc and adjacent monumental bronze gate.
2. Use the World recipe below in full. For a new POI implement the named generator, call it from main(), register STRUCTS with actual width/depth/weight/surface/theme and explicit loot/mobs/door/cullis flags. Existing POIs retain save IDs where possible.
3. Read the cited region section and use its [C] landmarks; block palettes and dimensions are [B], with [G] appearance verified against actual original-TLC reference shots. Keep provenance and comparison notes with each image.
4. Render this structure alone first, check bounds and magenta unknown blocks, then run the full screenshot generator at the milestone boundary. Inspect entrances, floor heights, interiors, lighting and spawn/interaction coordinates; document a walk-through route and failures.
5. Run the **world** recipe (base always applies), save evidence, update checklist and HANDOFF, commit this leaf and push.

Acceptance: Bronze Gate and Archon Shrine landmarks visible; emitted footprint matches runtime; no missing palette entries or broken interaction anchors; render and AUDIT row agree. In-world placement/walk-through pending until checked.

### W3.3 — Archon Folly

References: [C] architecture.md: Northern Wastes; FullWorld §12; [G] visual_reference.md: Core Look; [B] scatter adaptation.

Files: `scripts/gen_structures.py`, `packs/Fablecraft_BP/scripts/main.js`, `scripts/gen_screenshots.py`, `screenshots/AUDIT.md`.

1. Inspect generator `archon_folly (new)` (strip " (new)" for the proposed new Python name), STRUCTS and all fc:place/travel/loot references. Write the footprint and feature-local coordinates before implementation. Required recognizable features: Volcanic blackstone/basalt platform, lava perimeter, boss-safe landing and exit; use existing dragon until its own entity work.
2. Use the World recipe below in full. For a new POI implement the named generator, call it from main(), register STRUCTS with actual width/depth/weight/surface/theme and explicit loot/mobs/door/cullis flags. Existing POIs retain save IDs where possible.
3. Read the cited region section and use its [C] landmarks; block palettes and dimensions are [B], with [G] appearance verified against actual original-TLC reference shots. Keep provenance and comparison notes with each image.
4. Render this structure alone first, check bounds and magenta unknown blocks, then run the full screenshot generator at the milestone boundary. Inspect entrances, floor heights, interiors, lighting and spawn/interaction coordinates; document a walk-through route and failures.
5. Run the **world** recipe (base always applies), save evidence, update checklist and HANDOFF, commit this leaf and push.

Acceptance: Archon Folly landmarks visible; emitted footprint matches runtime; no missing palette entries or broken interaction anchors; render and AUDIT row agree. In-world placement/walk-through pending until checked.

### W3.4 — Greatwood Gorge toll bridge

References: [C] architecture.md: Greatwood; FullWorld §6; [G] visual_reference.md: Core Look; [B] scatter adaptation.

Files: `scripts/gen_structures.py`, `packs/Fablecraft_BP/scripts/main.js`, `scripts/gen_screenshots.py`, `screenshots/AUDIT.md`.

1. Inspect generator `greatwood_gorge (new)` (strip " (new)" for the proposed new Python name), STRUCTS and all fc:place/travel/loot references. Write the footprint and feature-local coordinates before implementation. Required recognizable features: Ravine-spanning bridge, bandit shack/checkpoint, stairs and stone-face landmark; no unavoidable lethal entry.
2. Use the World recipe below in full. For a new POI implement the named generator, call it from main(), register STRUCTS with actual width/depth/weight/surface/theme and explicit loot/mobs/door/cullis flags. Existing POIs retain save IDs where possible.
3. Read the cited region section and use its [C] landmarks; block palettes and dimensions are [B], with [G] appearance verified against actual original-TLC reference shots. Keep provenance and comparison notes with each image.
4. Render this structure alone first, check bounds and magenta unknown blocks, then run the full screenshot generator at the milestone boundary. Inspect entrances, floor heights, interiors, lighting and spawn/interaction coordinates; document a walk-through route and failures.
5. Run the **world** recipe (base always applies), save evidence, update checklist and HANDOFF, commit this leaf and push.

Acceptance: Greatwood Gorge toll bridge landmarks visible; emitted footprint matches runtime; no missing palette entries or broken interaction anchors; render and AUDIT row agree. In-world placement/walk-through pending until checked.

### W3.5 — Darkwood Bordello

References: [C] architecture.md: Darkwood; FullWorld §7; [G] visual_reference.md: Core Look; [B] scatter adaptation.

Files: `scripts/gen_structures.py`, `packs/Fablecraft_BP/scripts/main.js`, `scripts/gen_screenshots.py`, `screenshots/AUDIT.md`.

1. Inspect generator `darkwood_bordello (new)` (strip " (new)" for the proposed new Python name), STRUCTS and all fc:place/travel/loot references. Write the footprint and feature-local coordinates before implementation. Required recognizable features: Warm safe-haven two-storey building in marsh, carved stone face and readable public/refuge areas.
2. Use the World recipe below in full. For a new POI implement the named generator, call it from main(), register STRUCTS with actual width/depth/weight/surface/theme and explicit loot/mobs/door/cullis flags. Existing POIs retain save IDs where possible.
3. Read the cited region section and use its [C] landmarks; block palettes and dimensions are [B], with [G] appearance verified against actual original-TLC reference shots. Keep provenance and comparison notes with each image.
4. Render this structure alone first, check bounds and magenta unknown blocks, then run the full screenshot generator at the milestone boundary. Inspect entrances, floor heights, interiors, lighting and spawn/interaction coordinates; document a walk-through route and failures.
5. Run the **world** recipe (base always applies), save evidence, update checklist and HANDOFF, commit this leaf and push.

Acceptance: Darkwood Bordello landmarks visible; emitted footprint matches runtime; no missing palette entries or broken interaction anchors; render and AUDIT row agree. In-world placement/walk-through pending until checked.

### W4.1 — Oakvale walkability

References: [C] FullWorld §2; [G] visual_reference.md: Core Look; [B] scatter adaptation.

Files: `scripts/gen_structures.py`, `packs/Fablecraft_BP/scripts/main.js`, `scripts/gen_screenshots.py`, `screenshots/AUDIT.md`.

1. Inspect generator `oakvale_village` (strip " (new)" for the proposed new Python name), STRUCTS and all fc:place/travel/loot references. Write the footprint and feature-local coordinates before implementation. Required recognizable features: Connected gate/tree/shops/garden/quay paths, traversable doors/interiors and lawful spawn points.
2. Use the World recipe below in full. For a new POI implement the named generator, call it from main(), register STRUCTS with actual width/depth/weight/surface/theme and explicit loot/mobs/door/cullis flags. Existing POIs retain save IDs where possible.
3. Read the cited region section and use its [C] landmarks; block palettes and dimensions are [B], with [G] appearance verified against actual original-TLC reference shots. Keep provenance and comparison notes with each image.
4. Render this structure alone first, check bounds and magenta unknown blocks, then run the full screenshot generator at the milestone boundary. Inspect entrances, floor heights, interiors, lighting and spawn/interaction coordinates; document a walk-through route and failures.
5. Run the **world** recipe (base always applies), save evidence, update checklist and HANDOFF, commit this leaf and push.

Acceptance: Oakvale walkability landmarks visible; emitted footprint matches runtime; no missing palette entries or broken interaction anchors; render and AUDIT row agree. In-world placement/walk-through pending until checked.

### W4.2 — Bowerstone walkability

References: [C] FullWorld §3; [G] visual_reference.md: Core Look; [B] scatter adaptation.

Files: `scripts/gen_structures.py`, `packs/Fablecraft_BP/scripts/main.js`, `scripts/gen_screenshots.py`, `screenshots/AUDIT.md`.

1. Inspect generator `bowerstone_market` (strip " (new)" for the proposed new Python name), STRUCTS and all fc:place/travel/loot references. Write the footprint and feature-local coordinates before implementation. Required recognizable features: Street/bridge/class-gate/market/Manor continuity, guard and crowd positions clear of walls.
2. Use the World recipe below in full. For a new POI implement the named generator, call it from main(), register STRUCTS with actual width/depth/weight/surface/theme and explicit loot/mobs/door/cullis flags. Existing POIs retain save IDs where possible.
3. Read the cited region section and use its [C] landmarks; block palettes and dimensions are [B], with [G] appearance verified against actual original-TLC reference shots. Keep provenance and comparison notes with each image.
4. Render this structure alone first, check bounds and magenta unknown blocks, then run the full screenshot generator at the milestone boundary. Inspect entrances, floor heights, interiors, lighting and spawn/interaction coordinates; document a walk-through route and failures.
5. Run the **world** recipe (base always applies), save evidence, update checklist and HANDOFF, commit this leaf and push.

Acceptance: Bowerstone walkability landmarks visible; emitted footprint matches runtime; no missing palette entries or broken interaction anchors; render and AUDIT row agree. In-world placement/walk-through pending until checked.

### W4.3 — Knothole walkability

References: [C] FullWorld §4; [G] visual_reference.md: Core Look; [B] scatter adaptation.

Files: `scripts/gen_structures.py`, `packs/Fablecraft_BP/scripts/main.js`, `scripts/gen_screenshots.py`, `screenshots/AUDIT.md`.

1. Inspect generator `knothole_glade` (strip " (new)" for the proposed new Python name), STRUCTS and all fc:place/travel/loot references. Write the footprint and feature-local coordinates before implementation. Required recognizable features: Gate, statue, range, shops, homes and Demon Door joined without compulsory jumping.
2. Use the World recipe below in full. For a new POI implement the named generator, call it from main(), register STRUCTS with actual width/depth/weight/surface/theme and explicit loot/mobs/door/cullis flags. Existing POIs retain save IDs where possible.
3. Read the cited region section and use its [C] landmarks; block palettes and dimensions are [B], with [G] appearance verified against actual original-TLC reference shots. Keep provenance and comparison notes with each image.
4. Render this structure alone first, check bounds and magenta unknown blocks, then run the full screenshot generator at the milestone boundary. Inspect entrances, floor heights, interiors, lighting and spawn/interaction coordinates; document a walk-through route and failures.
5. Run the **world** recipe (base always applies), save evidence, update checklist and HANDOFF, commit this leaf and push.

Acceptance: Knothole walkability landmarks visible; emitted footprint matches runtime; no missing palette entries or broken interaction anchors; render and AUDIT row agree. In-world placement/walk-through pending until checked.

### W4.4 — Hook Coast walkability

References: [C] FullWorld §5; [G] visual_reference.md: Core Look; [B] scatter adaptation.

Files: `scripts/gen_structures.py`, `packs/Fablecraft_BP/scripts/main.js`, `scripts/gen_screenshots.py`, `screenshots/AUDIT.md`.

1. Inspect generator `hook_coast` (strip " (new)" for the proposed new Python name), STRUCTS and all fc:place/travel/loot references. Write the footprint and feature-local coordinates before implementation. Required recognizable features: Tier stairs, harbor, lighthouse and Abbey paths; no buried doors or roof spawns.
2. Use the World recipe below in full. For a new POI implement the named generator, call it from main(), register STRUCTS with actual width/depth/weight/surface/theme and explicit loot/mobs/door/cullis flags. Existing POIs retain save IDs where possible.
3. Read the cited region section and use its [C] landmarks; block palettes and dimensions are [B], with [G] appearance verified against actual original-TLC reference shots. Keep provenance and comparison notes with each image.
4. Render this structure alone first, check bounds and magenta unknown blocks, then run the full screenshot generator at the milestone boundary. Inspect entrances, floor heights, interiors, lighting and spawn/interaction coordinates; document a walk-through route and failures.
5. Run the **world** recipe (base always applies), save evidence, update checklist and HANDOFF, commit this leaf and push.

Acceptance: Hook Coast walkability landmarks visible; emitted footprint matches runtime; no missing palette entries or broken interaction anchors; render and AUDIT row agree. In-world placement/walk-through pending until checked.

### W4.5 — Snowspire walkability

References: [C] FullWorld §12; [G] visual_reference.md: Core Look; [B] scatter adaptation.

Files: `scripts/gen_structures.py`, `packs/Fablecraft_BP/scripts/main.js`, `scripts/gen_screenshots.py`, `screenshots/AUDIT.md`.

1. Inspect generator `power_snowspire_oracle` (strip " (new)" for the proposed new Python name), STRUCTS and all fc:place/travel/loot references. Write the footprint and feature-local coordinates before implementation. Required recognizable features: Village to Oracle route, snowy interiors, safe travel arrival and crowd points.
2. Use the World recipe below in full. For a new POI implement the named generator, call it from main(), register STRUCTS with actual width/depth/weight/surface/theme and explicit loot/mobs/door/cullis flags. Existing POIs retain save IDs where possible.
3. Read the cited region section and use its [C] landmarks; block palettes and dimensions are [B], with [G] appearance verified against actual original-TLC reference shots. Keep provenance and comparison notes with each image.
4. Render this structure alone first, check bounds and magenta unknown blocks, then run the full screenshot generator at the milestone boundary. Inspect entrances, floor heights, interiors, lighting and spawn/interaction coordinates; document a walk-through route and failures.
5. Run the **world** recipe (base always applies), save evidence, update checklist and HANDOFF, commit this leaf and push.

Acceptance: Snowspire walkability landmarks visible; emitted footprint matches runtime; no missing palette entries or broken interaction anchors; render and AUDIT row agree. In-world placement/walk-through pending until checked.

### E1 — Fill character and ambient roster gaps

References: [C] architecture.md: named residents; visual_reference.md: Map And Ambient Detail; [B] stats and roles.

Files: `scripts/fc_mobs.py`, `scripts/gen_behavior.py`, `scripts/gen_resources.py`, `scripts/gen_entity_textures.py`, `scripts/gen_emotes.py`.

1. Add Thunder, Whisper, Scythe and Nostro with documented silhouettes/roles; add chickens/livestock and crowd variants as explicit entries. Check whether a vanilla livestock entity is sufficient before creating a duplicate. Record Kraken separately as a known gap outside this E1 roster, not delivered by implication.
2. Choose families, health/damage, social/guard behavior and loot as [B]. Every social character must inherit reaction, persistence and romance eligibility deliberately. Integrate story/region spawn sites without duplicating NPCs on reload.
3. Run 0.1 regression before any behavior regeneration, then targeted texture/behavior/resource/emote generators in dependency order. Check all generated changes including existing entities/items, no hand fixes.
4. Run `_audit_anims.py`, `verify_emotes.py`, build and full `gen_screenshots.py`; visually review each new mob silhouette and texture, compare original TLC evidence, and check spawn/reload in-game.
5. Run the **entity** recipe (base always applies), save evidence, update checklist and HANDOFF, commit this leaf and push.

Acceptance: Roster gaps explicitly filled, textures/clips/bones resolve, social events survive, crowd diversity demonstrated; no invented canon stats.

### E2 — Flyer attacks, death and hurt clips

References: [G] visual_reference.md: Core Look; [B] Bedrock animation state design.

Files: `scripts/gen_resources.py`, `scripts/gen_behavior.py`, `scripts/_audit_anims.py`.

1. Enumerate missing clips per plan (flyer, ghost, dragon, bipeds). Define one-shot attack/hurt/death state transitions and the signals driving them, using the 0.3 audit contracts.
2. Author clips only on bones present in each model. Keep hurt/death overlays separate from locomotion, avoid looping death, and ensure state resets for reused/summoned entities.
3. Regenerate resources, save pose renders, run animation audit/negative fixtures and base suite. Observe each state in-game including interrupt, despawn and repeated damage.
4. Run the **entity** recipe (base always applies), save evidence, update checklist and HANDOFF, commit this leaf and push.

Acceptance: Every supported plan has reachable compatible clips; no undefined gates/bones, death once, hurt resets, flyers visibly strike.

### E3 — Creature signature specials

References: [G] visual_reference.md: silhouette guidance; [B] combat timings.

Files: `scripts/gen_resources.py`, `scripts/gen_behavior.py`, `scripts/fc_mobs.py`, `packs/Fablecraft_BP/scripts/main.js`.

1. Implement balverine leap, banshee shriek, dragon breath and summoner cast as distinct readable windup/action/recovery sequences. Source each visual claim before labeling it canon.
2. Tie action effects/damage to actual state, with target validation, cooldowns, interruption and cleanup. Do not substitute an always-running clip for a special.
3. Regenerate through owners, audit gates/bones, test cooldown/ally safety in mocks, render poses, and record in-world telegraph-to-hit verification.
4. Run the **entity** recipe (base always applies), save evidence, update checklist and HANDOFF, commit this leaf and push.

Acceptance: Four specials have readable telegraphs and bounded effects matching their driven states, with interruption and ally-safe checks.

### E4 — Expression hold meter and sweet spot

References: [C] emotes.md: Mechanics/Caveats; UIofFable.md: Expression use; [B] numeric thresholds.

Files: `packs/Fablecraft_BP/scripts/main.js`, `scripts/gen_emotes.py`, `scripts/gen_ui.py`, `scripts/gen_hud_font.py`.

1. Find existing expression dispatch and NPC opinion mutation. Model begin/hold/release/cancel once per player; resolve Bedrock input with existing item-use conventions.
2. Add visible meter and bounded green window; apply best/normal/failure results once on release. Exact timing and opinion deltas are [B]; retain the 31 expression unlocks and no sequel expression vendors.
3. Cancel on death, dimension change, menu switch and disconnect. Keep existing HUD payload lines/clip offsets coupled and edit their generators only; establish an owner first if a purported generator is absent.
4. Test early/sweet/late releases, spam, cancel and multiple players. Run verify_emotes, audit_hud, faithful HUD preview, base build and in-world controller/keyboard checks.
5. Run the **entity** recipe (base always applies), save evidence, update checklist and HANDOFF, commit this leaf and push.

Acceptance: Release result applied once, failure behavior distinct, unlocks preserved, meter visible without HUD bleed.

### V1 — Will charge and Cullis swirl

References: [C/G] UIofFable.md: Fast Travel; [B] emitter implementation.

Files: `scripts/gen_wd.py`, `scripts/gen_resources.py`, `scripts/gen_doc_screenshots.py`, `packs/Fablecraft_BP/scripts/wd/`, `packs/Fablecraft_BP/scripts/main.js`.

1. Implement caster aura tied to actual charging plus teleport departure/arrival swirl. Inventory existing particle IDs and texture/material owners; add semantic names to fc_strings only if a user-visible label is needed.
2. Author emitter JSON in gen_wd.py/gen_resources.py, never under RP/particles by hand. Add runtime triggers and cleanup tied to actual gameplay state, with multiplayer/range limits and bounded particle budgets.
3. Extend gen_doc_screenshots.py with a scene showing the new effect. Its composited renders are design evidence, not proof that Bedrock executes emitters.
4. Run targeted generators, base suite and `python scripts/gen_doc_screenshots.py`. Review emitted ID references and manually check start/stop, visibility, clipping, interrupted casts, crowded scenes and performance.
5. Run the **vfx** recipe (base always applies), save evidence, update checklist and HANDOFF, commit this leaf and push.

Acceptance: Effects match their gameplay events, no orphan emitters or stale loops, screenshots and particle-count/performance notes recorded.

### V2 — XP streams and Demon Door speech

References: [C/G] UIofFable.md: Status/experience orbs; visual_reference.md: Demon Doors; [B] emitter implementation.

Files: `scripts/gen_wd.py`, `scripts/gen_resources.py`, `scripts/gen_doc_screenshots.py`, `packs/Fablecraft_BP/scripts/wd/`, `packs/Fablecraft_BP/scripts/main.js`.

1. Implement colored XP streams tied to real awards/collection and mouth FX tied to door speech. Inventory existing particle IDs and texture/material owners; add semantic names to fc_strings only if a user-visible label is needed.
2. Author emitter JSON in gen_wd.py/gen_resources.py, never under RP/particles by hand. Add runtime triggers and cleanup tied to actual gameplay state, with multiplayer/range limits and bounded particle budgets.
3. Extend gen_doc_screenshots.py with a scene showing the new effect. Its composited renders are design evidence, not proof that Bedrock executes emitters.
4. Run targeted generators, base suite and `python scripts/gen_doc_screenshots.py`. Review emitted ID references and manually check start/stop, visibility, clipping, interrupted casts, crowded scenes and performance.
5. Run the **vfx** recipe (base always applies), save evidence, update checklist and HANDOFF, commit this leaf and push.

Acceptance: Effects match their gameplay events, no orphan emitters or stale loops, screenshots and particle-count/performance notes recorded.

### V3 — Boss telegraphs

References: [C/G] visual_reference.md: Core Look; [B] emitter implementation.

Files: `scripts/gen_wd.py`, `scripts/gen_resources.py`, `scripts/gen_doc_screenshots.py`, `packs/Fablecraft_BP/scripts/wd/`, `packs/Fablecraft_BP/scripts/main.js`.

1. Implement windup danger indications for boss attacks, canceled on interruption/death. Inventory existing particle IDs and texture/material owners; add semantic names to fc_strings only if a user-visible label is needed.
2. Author emitter JSON in gen_wd.py/gen_resources.py, never under RP/particles by hand. Add runtime triggers and cleanup tied to actual gameplay state, with multiplayer/range limits and bounded particle budgets.
3. Extend gen_doc_screenshots.py with a scene showing the new effect. Its composited renders are design evidence, not proof that Bedrock executes emitters.
4. Run targeted generators, base suite and `python scripts/gen_doc_screenshots.py`. Review emitted ID references and manually check start/stop, visibility, clipping, interrupted casts, crowded scenes and performance.
5. Run the **vfx** recipe (base always applies), save evidence, update checklist and HANDOFF, commit this leaf and push.

Acceptance: Effects match their gameplay events, no orphan emitters or stale loops, screenshots and particle-count/performance notes recorded.

### V4 — Regional ambient effects

References: [C/G] architecture.md: regional atmosphere; FullWorld §§2,7,12; [B] emitter implementation.

Files: `scripts/gen_wd.py`, `scripts/gen_resources.py`, `scripts/gen_doc_screenshots.py`, `packs/Fablecraft_BP/scripts/wd/`, `packs/Fablecraft_BP/scripts/main.js`.

1. Implement Darkwood wisps, Oakvale fireflies, Skorm embers, Snowspire snow with distance/budget limits. Inventory existing particle IDs and texture/material owners; add semantic names to fc_strings only if a user-visible label is needed.
2. Author emitter JSON in gen_wd.py/gen_resources.py, never under RP/particles by hand. Add runtime triggers and cleanup tied to actual gameplay state, with multiplayer/range limits and bounded particle budgets.
3. Extend gen_doc_screenshots.py with a scene showing the new effect. Its composited renders are design evidence, not proof that Bedrock executes emitters.
4. Run targeted generators, base suite and `python scripts/gen_doc_screenshots.py`. Review emitted ID references and manually check start/stop, visibility, clipping, interrupted casts, crowded scenes and performance.
5. Run the **vfx** recipe (base always applies), save evidence, update checklist and HANDOFF, commit this leaf and push.

Acceptance: Effects match their gameplay events, no orphan emitters or stale loops, screenshots and particle-count/performance notes recorded.

### M0 — In-world subsystem smoke harness

References: [B] test scaffolding; UIofFable.md: subsystem overview.

Files: `packs/Fablecraft_BP/scripts/smoke.js (new)`, `packs/Fablecraft_BP/scripts/main.js`, `docs/SMOKE_TESTS.md (new)`.

1. Implement /scriptevent fc:smoke using system.afterEvents.scriptEventReceive, scoped to an operator/test player in a disposable world. Use a test adapter to call actual exported subsystem operations; do not fake PASS based on file presence.
2. Exercise XP award, morality delta, expression, spell cast, shop transaction, bounty accrue/clear, Cullis register, marriage gift and quest grant. Snapshot player state/inventory and isolate spawned entities; restore in finally and log cleanup failures.
3. Print named PASS/FAIL to chat and a final count; unknown/unavailable prerequisites report SKIP, never PASS. Add mock tests for deliberate failures and restoration. Document required in-world setup and expected lines.
4. Run base suite and manually execute the command once the user can launch Bedrock. Until then state smoke runtime UNRUN, even if mocks pass.
5. Run the **base** recipe (base always applies), save evidence, update checklist and HANDOFF, commit this leaf and push.

Acceptance: Harness covers all ten subsystems with actual operations, failure injection and restoration tests; runtime all-PASS only after observed run.

### M1 — Interactive good/evil altars

References: [C] architecture.md: Temple/Chapel; emotes.md: Follow; [B] numeric balance and persistence.

Files: `packs/Fablecraft_BP/scripts/wd/altars.js (new)`, `packs/Fablecraft_BP/scripts/wd/state.js`, `packs/Fablecraft_BP/scripts/wd/config.js`, `scripts/gen_wd.py`, `docs/M1_SPEC.md (new)`.

1. Write docs/M1_SPEC.md before code: triggers, prerequisites, data schema/migration, transaction order, failure paths, configuration, canon-vs-build choices and a manual checklist. Implement Avo donations and Skorm sacrifices use existing alignment constants; validate funds/follower/region, consume once and award once.
2. Wire to the existing menu_bridge/runtime hub and wd progression authority. Names go through fc_strings; no extra authority for XP/alignment, no magic constants presented as canon.
3. Test insufficient funds/items, cancellation, death, disconnect, duplicate input, full inventory, save/reload and two players. Keep rewards idempotent and cleanup reliable.
4. Extend fc:smoke with real altars operations and explicit cleanup. For M5 enable agingEnabled only after tests and migration are complete. Run base suite, state tests, relevant renders and the spec manual checklist.
5. Run the **base** recipe (base always applies), save evidence, update checklist and HANDOFF, commit this leaf and push.

Acceptance: Spec and implementation agree, state migrations preserve saves, failure paths consume/reward correctly, smoke includes subsystem, manual checks honestly recorded.

### M2 — Property ownership and rent

References: [C] UIofFable.md: auto-map/owned houses; FullWorld §§3–4; [B] numeric balance and persistence.

Files: `packs/Fablecraft_BP/scripts/wd/property.js (new)`, `packs/Fablecraft_BP/scripts/wd/state.js`, `packs/Fablecraft_BP/scripts/wd/config.js`, `scripts/gen_wd.py`, `docs/M2_SPEC.md (new)`.

1. Write docs/M2_SPEC.md before code: triggers, prerequisites, data schema/migration, transaction order, failure paths, configuration, canon-vs-build choices and a manual checklist. Implement buy houses, persist ownership per stable property ID, rent and collect without duplicate payouts or negative balances.
2. Wire to the existing menu_bridge/runtime hub and wd progression authority. Names go through fc_strings; no extra authority for XP/alignment, no magic constants presented as canon.
3. Test insufficient funds/items, cancellation, death, disconnect, duplicate input, full inventory, save/reload and two players. Keep rewards idempotent and cleanup reliable.
4. Extend fc:smoke with real property operations and explicit cleanup. For M5 enable agingEnabled only after tests and migration are complete. Run base suite, state tests, relevant renders and the spec manual checklist.
5. Run the **base** recipe (base always applies), save evidence, update checklist and HANDOFF, commit this leaf and push.

Acceptance: Spec and implementation agree, state migrations preserve saves, failure paths consume/reward correctly, smoke includes subsystem, manual checks honestly recorded.

### M3 — Fishing and digging

References: [C] UIofFable.md: Context-sensitive icons; architecture.md: Fisher Creek/Necropolis; [B] numeric balance and persistence.

Files: `packs/Fablecraft_BP/scripts/wd/gathering.js (new)`, `packs/Fablecraft_BP/scripts/wd/state.js`, `packs/Fablecraft_BP/scripts/wd/config.js`, `scripts/gen_wd.py`, `docs/M3_SPEC.md (new)`.

1. Write docs/M3_SPEC.md before code: triggers, prerequisites, data schema/migration, transaction order, failure paths, configuration, canon-vs-build choices and a manual checklist. Implement contextual fishing/dig spots, timing/loot, inventory capacity, depleted-spot persistence and no repeated unique rewards.
2. Wire to the existing menu_bridge/runtime hub and wd progression authority. Names go through fc_strings; no extra authority for XP/alignment, no magic constants presented as canon.
3. Test insufficient funds/items, cancellation, death, disconnect, duplicate input, full inventory, save/reload and two players. Keep rewards idempotent and cleanup reliable.
4. Extend fc:smoke with real gathering operations and explicit cleanup. For M5 enable agingEnabled only after tests and migration are complete. Run base suite, state tests, relevant renders and the spec manual checklist.
5. Run the **base** recipe (base always applies), save evidence, update checklist and HANDOFF, commit this leaf and push.

Acceptance: Spec and implementation agree, state migrations preserve saves, failure paths consume/reward correctly, smoke includes subsystem, manual checks honestly recorded.

### M4 — Tavern games

References: [C] architecture.md: taverns; [B] select and source rules before coding; [B] numeric balance and persistence.

Files: `packs/Fablecraft_BP/scripts/wd/tavern_games.js (new)`, `packs/Fablecraft_BP/scripts/wd/state.js`, `packs/Fablecraft_BP/scripts/wd/config.js`, `scripts/gen_wd.py`, `docs/M4_SPEC.md (new)`.

1. Write docs/M4_SPEC.md before code: triggers, prerequisites, data schema/migration, transaction order, failure paths, configuration, canon-vs-build choices and a manual checklist. Implement document sourced TLC games, explicit gold stakes, deterministic rule evaluation and bounded RNG; no real-money monetization.
2. Wire to the existing menu_bridge/runtime hub and wd progression authority. Names go through fc_strings; no extra authority for XP/alignment, no magic constants presented as canon.
3. Test insufficient funds/items, cancellation, death, disconnect, duplicate input, full inventory, save/reload and two players. Keep rewards idempotent and cleanup reliable.
4. Extend fc:smoke with real tavern_games operations and explicit cleanup. For M5 enable agingEnabled only after tests and migration are complete. Run base suite, state tests, relevant renders and the spec manual checklist.
5. Run the **base** recipe (base always applies), save evidence, update checklist and HANDOFF, commit this leaf and push.

Acceptance: Spec and implementation agree, state migrations preserve saves, failure paths consume/reward correctly, smoke includes subsystem, manual checks honestly recorded.

### M5 — Scars and aging

References: [C] UIofFable.md: Morality/Character customization; [B] numeric balance and persistence.

Files: `packs/Fablecraft_BP/scripts/wd/aging.js (new)`, `packs/Fablecraft_BP/scripts/wd/state.js`, `packs/Fablecraft_BP/scripts/wd/config.js`, `scripts/gen_wd.py`, `docs/M5_SPEC.md (new)`.

1. Write docs/M5_SPEC.md before code: triggers, prerequisites, data schema/migration, transaction order, failure paths, configuration, canon-vs-build choices and a manual checklist. Implement persist scar/age progression, handle config toggles and old saves, drive appearance overlays through their generators.
2. Wire to the existing menu_bridge/runtime hub and wd progression authority. Names go through fc_strings; no extra authority for XP/alignment, no magic constants presented as canon.
3. Test insufficient funds/items, cancellation, death, disconnect, duplicate input, full inventory, save/reload and two players. Keep rewards idempotent and cleanup reliable.
4. Extend fc:smoke with real aging operations and explicit cleanup. For M5 enable agingEnabled only after tests and migration are complete. Run base suite, state tests, relevant renders and the spec manual checklist.
5. Run the **base** recipe (base always applies), save evidence, update checklist and HANDOFF, commit this leaf and push.

Acceptance: Spec and implementation agree, state migrations preserve saves, failure paths consume/reward correctly, smoke includes subsystem, manual checks honestly recorded.

### C1 — Continuous validation

References: [B] engineering.

Files: ` .github/workflows/validate.yml (new)`, `package.json`, `package-lock.json`, `Python dependency manifest`.

1. Pin compatible Python/Node and install declared dependencies in a clean Linux runner using npm ci and pip. Never rely on ignored local tooling, external NTFS paths or uncommitted files.
2. On push and pull_request run python scripts/build_addon.py (no --full), npm run lint, verify_emotes.py, _audit_anims.py, audit_hud.py --check and meaningful regression tests. Persist logs as workflow artifacts; do not publish faithful dist output.
3. Run identical commands locally from a clean checkout or isolated index snapshot. Push workflow and inspect the actual run status; local success is not CI success.
4. Run the **base** recipe (base always applies), save evidence, update checklist and HANDOFF, commit this leaf and push.

Acceptance: Workflow committed, remote run green with no undeclared dependencies; artifacts are validator logs, no accidental release.

### C2 — Structure-manifest contract

References: [B] engineering; [G] screenshot evidence.

Files: `scripts/build_addon.py`, `scripts/gen_structures.py`, `packs/Fablecraft_BP/scripts/main.js`, `screenshots/AUDIT.md`, `scripts/tests/test_structure_manifest.py (new)`.

1. Create a machine-readable manifest or parse explicit supported tables (not broad regex guesses) linking each STRUCTS ID to generator, emitted .mcstructure, actual dimensions, screenshot and audit row. Model Guild/fixed/legacy structures separately so non-scatter output is intentional.
2. Validate both directions with declared aliases/tiles and no orphan reference. Screenshots must correspond to current generator output and footprint. Add this contract to build_addon.validate().
3. Negative tests remove one generator/asset/image/grade and mismatch width/height; each must fail. Add a distinct interaction/Guild anchor comparison, since asset cross-reference validation alone never proves coupling.
4. Run the full build, screenshot manifest and regression suite; retain explicit in-world placement checks.
5. Run the **base** recipe (base always applies), save evidence, update checklist and HANDOFF, commit this leaf and push.

Acceptance: Each contract edge and reverse edge validated, negative tests fail independently, anchors separately audited.

2026-09-12: implemented in structure_contract.py, structure_tables.cjs, structure_manifest.json and render_structure_contract.py. All 29 assets/renders, 23 scatter/two fixed/four legacy roles are checked; 13 Python groups and four actual-source placement tests pass. Rectangular bounds, stale Guild output and blocked Maze spawn were corrected. See docs/STRUCTURE_CONTRACT.md; C2 remains in-progress for the explicit in-world checklist.

### C3 — Reproducible conformance scoreboard

References: [B] scoring policy; [G] visual_reference.md.

Files: `scripts/conformance_score.py (new)`, `docs/CONFORMANCE_CHECKLIST.md`.

1. Parse checklist leaf rows with stable IDs and status enum, rejecting duplicate IDs, invalid states and nonexistent evidence paths. Add --check to detect stale scoreboard output.
2. Compute done/total percentage per domain, plus separate automated/manual completeness and actual AUDIT grades. Never treat a pending visual check as grade A or average letters without an explicit scale.
3. Generate a deterministic scoreboard section, test missing evidence/duplicate row/stale score, and wire --check into CI. Preserve manually written findings outside the generated section.
4. Run the **base** recipe (base always applies), save evidence, update checklist and HANDOFF, commit this leaf and push.

Acceptance: Per-domain totals reproducible; completed rows have traceable evidence; manual pending clearly separated; CI detects stale scores.

2026-09-12: implemented in scripts/conformance_score.py with ten regression groups. The marked checklist section reports the 45 approved leaves, separate automated/manual counts and current C2 appearance-grade histogram. See docs/SCORING.md for evidence validation and shallow-checkout limits.

## Risk register and completion criteria

| Risk | Mitigation / evidence |
| --- | --- |
| Stripped behavior generator | 0.1 negative/positive isolated regeneration; prohibit --full until green |
| Newline mirage | Explicit path patches, ignore-cr-at-eol diffs; no .gitattributes or renormalization |
| Guild coordinate drift | Generator/runtime coordinate table plus render and in-world reanchor checks |
| HUD slice drift | Generator ownership + payload/spacer/offset audit and faithful preview |
| Oversized structure load | Check dimension limits and runtime tiling together; archive obsolete patch |
| Legacy progression double count | Preserve wd alignment authority and legacy XP spend funnel |
| Missing NPC events / item formats | Behavior regression, verify_emotes and structured JSON comparisons |
| Distribution/IP exposure | No monetization/extracted assets, original-only release with zero-debt scan |
| False visual/runtime confidence | Separate mocks/composites from manual world observations; no invented grades |
| Dirty binaries / scratch outputs | Preserve locally, never blanket stage; original release gate before dist commit |
| Offline or rejected push | Exact error in handoff, record local hash and remote state; no claim of sync |

Overall completion requires all leaf acceptances, original packages with zero forbidden
literals, source/evidence/checklist together in pushed commits, green CI, structure/anchor
contracts, measured domain scores, and observed all-PASS fc:smoke. Missing Kraken and any
unplanned canon gap remain explicit scope gaps rather than disappearing from the scoreboard.

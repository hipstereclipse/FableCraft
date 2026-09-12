# Continuation prompt

Continue the FableCraft → TLC Conformance plan on Linux.
Repository: /run/media/eclipse/8E025A94025A80DF/Users/Eclipse/Fablecraft
Branch: phase3-will-destiny
Remote: https://github.com/hipstereclipse/FableCraft.git

Read docs/CONFORMANCE_PLAN.md and docs/CONFORMANCE_CHECKLIST.md. Source plan and
six reference snapshots are in docs/. User override (2026-09-12): finish the spell
WIP and continue as far as practical without permission questions. Keep separate
milestone commits, validation, immediate pushes, evidence and fresh handoffs.

Current milestone: W3.1 — Bargate Prison; status in-progress.
Last resolved prior commit: 40a92e78c95f2ee281e40d754f6371f51e4e7fb1 (pushed).
Containing commit: TLC Conformance — W3.1: add Bargate Prison and underground chamber.
Resolve current hash: git log -1 --format=%H --grep='TLC Conformance — W3.1: add Bargate Prison and underground chamber'.
Replace previous SELF with the actual hash next step; never invent a self-hash.

W3.1 adds fc:bargate_prison, 41x20x49, weight 4, grass/rock, dark theme. Courtyard
and three cell-block silhouettes (two open), four connected ramparts, east barracks,
lower west torture room and upper warden office sit above a navigable basin chamber.
Three ordinary chests and three Bowerstone guards have clear tested anchors. The
first route test found rear entrances blocked by the third block; north entrances
fix that. Seven groups pass, including independent blocked-cell/chamber fixtures.
Route tests permit one-block height changes; the chamber stair top has a full-block
transition, so jump-free movement is unproven. No prison quest, confiscation/recovery,
rescue, cell locks or Kraken. TLC reference
images show a much larger round domed basin hall with waterfall; our small flat
rectangular room is a major visual gap. See docs/BARGATE_PRISON.md and W3.1 evidence.

W2.4 at 40a92e7 adds fc:grey_house, 31x20x35, weight 5, grass/rock, dark theme.
Raised manor, internal cellar stairs, two coffins/chests and three undead have
seven passing groups. Stable, lantern sequence, ghost and investigation are absent.
A TLC guide stable image supplies material context, not full exterior/cellar proof.
See docs/GREY_HOUSE.md. Both new POIs keep local y=0 as the scatter foundation plane;
no buried placement offset. Added weights change future unvisited-region rolls;
existing region flags/geometry remain untouched. No Cullis or Demon Door at either.

W2.3 at 0edad619 widened Oakvale to 53x14x35 with east Memorial Garden, six graves
and upright axe statue. Its swinging pose/hillside/entry remain visual gaps. Five
emitted chests remain; an inherited cottage/quay overlap destroys an attempted sixth,
reserved for W4.1. W2.2 at a0b59f2 connects Hook Coast lighthouse/Abbey/graves; major
quest and travel gaps remain. W2.1 at fae89fb adds Bowerstone North/Manor, W1.4 at
ed57d1e adds Arena halls, W1.3 at add099a adds Twinblade rings, W1.2 at 608edf1 adds
Lychfield landmarks. Their detailed docs and manual checklists remain authoritative.
Nostro's onward route is missing: never substitute an unrelated Demon Door riddle.
No fc:place handler exists. Raw /structure load places blocks only; scatter owns
population, loot and travel. Keep procedural scatter, no fixed map or old-region retrofit.

All 24 local scripts/validate.py gates pass, plus explicit spell and syntax checks.
C2 covers 31 assets/renders (25 scatter/two fixed/four legacy), 15 contract groups
and nine placement cases. Current asset/render hashes match. Full all-category
pipelines ran through W3.1 in tmp/conformance/<ID>-full-screenshots; W3.1 renders
28 structure cards. Logs, audits, primary views and explicitly labeled cutaways
are in screenshots/validation/<ID>. These are offline evidence, never engine passes.
C2 checks mobSpawns count/finite shape/feet/head bounds; cross-POI fixtures catch
Snowspire contamination. Geometry clearance stays in individual POI tests.

C3 requires python scripts/conformance_score.py --write after EVERY checklist change,
then --check. It tracks 45 leaves, automated/manual counts and appearance separately.
W2.4 remote CI passed at 40a92e7 (run 34707520542); metadata is in
screenshots/validation/W2.4/remote-run.json. Inspect newest workflow's actual head next.
All current world rows remain in-progress for manual/reference work, not done.

Next three actions:
1. git pull --ff-only; start top todo W3.2 Bronze Gate and Archon Shrine.
2. Execute its numbered playbook and base/world validators. Save actual outputs
   under screenshots/validation/<ID>; every unobserved engine check stays unrun.
3. Update checklist/handoff, explicitly stage one milestone commit, push origin
   immediately and continue automatically. At context limits print this prompt verbatim.

Landmines: hundreds of apparent edits are CRLF noise. Never git add -A, commit -a,
renormalize, create .gitattributes or discard unrelated work. Read diffs with
--ignore-cr-at-eol; stage named reviewed patches via git apply --cached --ignore-whitespace.
Behavior owner was restored from 6cfea15 in 0.1. Run python scripts/tests/test_gen_behavior.py
before regeneration; use targeted owners. Passing 0.1 does not prove unrestricted
--full output drift safe. Stripped owner remains in tmp/conformance/gen_behavior_stripped.py.

Never hand-edit generator-owned BP entities, RP models/animations/controllers/
attachables/particles, fable_emote_registry.js, fable_hud.js, fc_gamedata.js or
texts/languages.json. Find/establish ownership if memory disagrees. Keep GUILD anchors
coupled to gen_structures; reanchor refreshes but does not audit. Maze stays (46,12,70).
No Guild tiling applied; never run the old patch blindly. All-cross-references-OK
checks assets only. Keep HUD payload/spacers/clip offsets coupled. wd alignment is
authoritative; preserve the legacy XP-spending bridge. HUD's narrow green radar,
missing hunger frame and navigation bleed remain visible gaps.

Spells are separately complete in ccafd4c; never stash/revert/refold them into this
plan. SPELL_COMPANIONS.md engine checks, 0.3 and L3 remain pending. BOUNTY_SYSTEM.md
was reconciled in 0.4. L4 public releases remain blocked: known-name debt, unselected
public title (Wayfarer Tales provisional) and missing saved-world remap. No exemptions.
Preserve inherited dist archives, four scripts/_align/overlay_*.png and scratch files.
Build faithful archives only in ignored tmp/builds/faithful-<run>/dist; never stage or
publish them. Public builds need original branding and zero-debt L4 scan. Original/
generated assets only; external reference images stay ignored developer scratch.
No extracted Fable pack assets, free and never monetized.

Git writes/network require escalation here. Use the existing repository author from
git log via commit-scoped -c options, not global config. Origin is user-authorized
and verified; separate pushes succeeded. No force push. Preserve local commits and
report any push failure honestly; never claim remote sync without checking.

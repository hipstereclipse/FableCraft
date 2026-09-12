# Continuation prompt

Continue the FableCraft → TLC Conformance plan on Linux.
Repository: /run/media/eclipse/8E025A94025A80DF/Users/Eclipse/Fablecraft
Branch: phase3-will-destiny
Remote: https://github.com/hipstereclipse/FableCraft.git

Read docs/CONFORMANCE_PLAN.md and docs/CONFORMANCE_CHECKLIST.md. The source plan and
six reference snapshots are in docs/. User override (2026-09-12): finish the spell WIP
and continue as far as practical without permission questions. Retain separate
milestone commits, validation, immediate pushes, evidence and fresh handoffs.

Current milestone: W1.2 — Lychfield crypt landmarks and safe spawns; status in-progress.
Last resolved prior commit: 2db414bbe53fea87f48fdf5c2cfd67da6eec4b0a (pushed).
Containing commit: TLC Conformance — W1.2: add Lychfield crypt landmarks and safe spawns.
Resolve current hash: git log -1 --format=%H --grep='TLC Conformance — W1.2: add Lychfield crypt landmarks and safe spawns'.
Replace previous SELF evidence with the actual hash next step; never invent a self-hash.

W1.2 retains fc:graveyard and 25x13x25 scatter/loot/save contracts. Nostro's crypt has
three stone sarcophagi and open walking aisles; a keeper hut and climbable gate-stair
stone face were added. main.js mobSpawns translates three clear local lane positions;
other POIs keep their previous spawn policy. Seven geometry/runtime regression groups
pass, including actual maybePlace with voxel data, both terrain classes and saved-region
idempotence. The old owner fails four landmark/route contracts. A missing crafting-table
render palette entry was added. docs/LYCHFIELD_CRYPT.md records routes and scope gaps.
The sealed stone face has no Nostro command, speech/opening or onward path implemented.
Do not silently register the unrelated generic Demon Door riddle. No fc:place handler
exists: raw /structure load places blocks only; scatter handles loot/population.

All 17 local scripts/validate.py gates pass. C2 render/asset hashes are current. The
full all-category pass uses isolated tmp/conformance/W1.2-full-screenshots; its logs,
audit and graveyard card are retained under screenshots/validation/W1.2. South/cutaway
views reveal the face and interiors hidden by the default camera. Original-TLC pixel
comparison remains pending: the dated MobyGames candidate could not be fetched.
No canon-A or in-world pass is claimed; every manual check remains explicitly unrun.

C3's scoreboard requires --write after EVERY checklist change:
python scripts/conformance_score.py --write, then --check. It tracks 45 plan leaves,
explicit automated/manual counts and offline appearance grades separately.
W1.1 remote CI passed at 2db414b (run 34678706829); metadata is in
screenshots/validation/W1.1/remote-run.json. Inspect this milestone's newest pushed
run for its actual head before the next milestone. C2/C1/C3/L4 CI also passed at
recorded commits. C2's in-world checklist remains in docs/STRUCTURE_CONTRACT.md.
No Guild tiling was applied; Maze's corrected spawn remains (46,12,70).

L4 releases remain blocked: original preview2,512 known-name findings, unselected final
public title (Wayfarer Tales provisional), and missing saved-world remap. No exemptions.
0.3/L3 and spell in-world checks remain pending. HUD still has narrow green radar,
missing hunger frame and nav bleed. Keep these visible rather than scoring them passed.

Next three actions:
1. git pull --ff-only; read the top pending row and start W1.3 Twinblade tent rings.
2. Execute its numbered playbook steps and applicable base/domain validators; preserve
   real output under screenshots/validation/<ID>/, mark manual observations unrun.
3. Update checklist/handoff in one explicitly staged milestone commit, push to origin,
   and continue automatically. On context limits print this prompt verbatim.

Landmines: hundreds of apparent edits are CRLF noise. Never git add -A, commit -a,
renormalize, create .gitattributes or discard unrelated work. Read every diff with
--ignore-cr-at-eol; stage named paths with reviewed patches to avoid newline churn.
Behavior generator was restored from 6cfea15 in 0.1; isolated tests prove social/react,
persistence/marriage, cosmetic and 194-item icon/damage contracts. The old copy is
preserved locally at tmp/conformance/gen_behavior_stripped.py. Before regeneration run
python scripts/tests/test_gen_behavior.py. Prefer targeted generators; lifting the
0.1 gate does not prove an unrestricted --full run has no other output drift.

Never hand-edit generator-owned BP entities, RP models/animations/controllers/
attachables/particles, fable_emote_registry.js, fable_hud.js, fc_gamedata.js or
texts/languages.json. Find/establish an owner if memory disagrees. Keep GUILD anchors
coupled to gen_structures; /scriptevent fc:reanchor refreshes but does not audit them.
All-cross-references-OK validates assets only. Keep HUD payload/spacers/clip offsets
coupled. Keep procedural scatter, no fixed Albion map. Never run the one-off Guild
tiling patch blindly. wd alignment remains authoritative; legacy XP spending funnels
through wd, so do not delete the legacy progression bridge blindly.

Ghost Sword/Assassin Rush are completed separately in ccafd4c; never stash/revert/refold
them into conformance. SPELL_COMPANIONS.md has the still-pending in-world checklist.
BOUNTY_SYSTEM.md was reconciled in 0.4. Remaining inherited edits include local dist
archives and four scripts/_align/overlay_*.png renders. Preserve unreviewed scratch files. Required
builds now package under tmp/builds/faithful-<run>/dist at milestone boundaries only: do not stage/publish faithful
archives. All public builds need original branding and L4 zero-debt scanning first.
Original/generated assets only, no extracted Fable content, free and never monetized.

Git writes/network require escalation here. Git author identity was unset; use the
existing repository identity from git log through commit-scoped -c options. Do not
change global config. Separate pushes to the above verified/user-authorized origin
succeeded; an earlier chained commit/push was rejected before destination verification.
No force push. Record push failures honestly rather than claiming shared-state sync.

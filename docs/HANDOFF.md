# Continuation prompt

Continue the FableCraft → TLC Conformance plan on Linux.
Repository: /run/media/eclipse/8E025A94025A80DF/Users/Eclipse/Fablecraft
Branch: phase3-will-destiny
Remote: https://github.com/hipstereclipse/FableCraft.git

Read docs/CONFORMANCE_PLAN.md and docs/CONFORMANCE_CHECKLIST.md. The source plan and
six reference snapshots are in docs/. User override (2026-09-12): finish the spell WIP
and continue as far as practical without permission questions. Retain separate
milestone commits, validation, immediate pushes, evidence and fresh handoffs.

Current milestone: 0.2 — adopt audit tooling and output policy; status done.
Last resolved prior commit: 6835313 (pushed before this milestone).
Containing commit: TLC Conformance — 0.2: adopt audit tooling and output policy.
Resolve current hash: git log -1 --format=%H --grep='TLC Conformance — 0.2: adopt audit tooling and output policy'.
Replace previous SELF evidence with the actual hash next step; never invent a self-hash.

Validator state: build, expressions (31/21), HUD (112/112), lint (0 errors/19 warnings),
17 spell mocks and behavior regression GREEN. Six audit tools compile/run. Animation
clip/bone audit passes 51 mobs; live gate-variable check remains for 0.3.
Evidence: screenshots/validation/0.2/ and screenshots/ui/. See docs/AUDIT_TOOLING.md.
Guild diagnostics: 85.3% structural-cell agreement, 0 unsupported clusters, 385 eave
cells flagged for review (not proven defects). HUD preview has a narrow green radar
column, missing hunger frame and possible nav-line bleed; no visual/in-world pass.
Target overlay accepts --reference; no external reference image was needed or bundled.
One-off tiling patch archived verbatim as docs/archive/patch_guild_tiling.py.txt;
root copy and scratch renders preserved/ignored. Development dependencies pinned.
Research for 0.3: official Microsoft query_modified_swing_duration documentation
explicitly calls variable.attack_time the swing progress; old premise may be false.
Do not invent a replacement query or falsify a before-fix failure.

Next three actions:
1. git pull --ff-only; read the top pending row and start 0.3 attack-gate audit and engine binding verification.
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
Remaining inherited edits include BOUNTY_SYSTEM.md until 0.4, local dist archives and
four scripts/_align/overlay_*.png renders. Preserve unreviewed scratch files. Required
builds package locally at milestone boundaries only: do not stage/publish faithful
archives. All public builds need original branding and L4 zero-debt scanning first.
Original/generated assets only, no extracted Fable content, free and never monetized.

Git writes/network require escalation here. Git author identity was unset; use the
existing repository identity from git log through commit-scoped -c options. Do not
change global config. Separate pushes to the above verified/user-authorized origin
succeeded; an earlier chained commit/push was rejected before destination verification.
No force push. Record push failures honestly rather than claiming shared-state sync.

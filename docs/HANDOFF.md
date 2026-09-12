# Continuation prompt

Continue the FableCraft → TLC Conformance plan on Linux.
Repository: /run/media/eclipse/8E025A94025A80DF/Users/Eclipse/Fablecraft
Branch: phase3-will-destiny
Remote: https://github.com/hipstereclipse/FableCraft.git

Read docs/CONFORMANCE_PLAN.md and docs/CONFORMANCE_CHECKLIST.md. The source plan and
six reference snapshots are in docs/. User override (2026-09-12): finish the spell WIP
and continue as far as practical without permission questions. Retain separate
milestone commits, validation, immediate pushes, evidence and fresh handoffs.

Current milestone: W1.1 — replace the Cullis gate proxy with a stone disc; status in-progress.
Last resolved prior commit: 05707d4 (pushed before this milestone).
Containing commit: TLC Conformance — W1.1: replace the Cullis gate proxy with a stone disc.
Resolve current hash: git log -1 --format=%H --grep='TLC Conformance — W1.1: replace the Cullis gate proxy with a stone disc'.
Replace previous SELF evidence with the actual hash next step; never invent a self-hash.

W1.1 now generates a weathered circular stone disc with blue inlay, a flush sea-lantern
core and eight carved runestones. fc:focus_site, its13x10x13 footprint and travel
registration stay unchanged; arrival is local(6,1,6). Existing-world blocks are not
retrofit. Five geometry/detector regression groups pass, including the actual runtime
portal detector on emitted voxel data; the old owner fails the new geometry tests.
C2 render/source hashes and audit were regenerated. docs/CULLIS_GATE.md has feature
coordinates, routes, provenance and manual checks. W1.1 stays in-progress for in-world
placement/travel and verified original2005 screenshot comparison; no canon-A claim.

The full all-category screenshot pass runs in isolated tmp/conformance/W1.1-full-screenshots;
its log/audit and current card are retained in screenshots/validation/W1.1. Base validation
uses scripts/validate.py (now16 gates). C3's scoreboard requires --write after EVERY
checklist change: python scripts/conformance_score.py --write, then --check. It tracks
45 plan leaves, explicit automated/manual counts and offline appearance grades separately.

C3 remote CI passed at05707d4 (run34678394054); metadata is in screenshots/validation/C3/remote-run.json.
C2/C1/L4 CI also passed at their recorded commits. Inspect the newest pushed run for its
actual head before the next milestone. C2 fixes four rectangular POI bounds, the stale
27-block Guild asset and Maze's blocked tower spawn (now46,12,70). Its manual checklist
is still pending in docs/STRUCTURE_CONTRACT.md. No Guild tiling was applied.

L4 releases remain blocked: original preview2,512 known-name findings, unselected final
public title (Wayfarer Tales provisional), and missing saved-world remap. No exemptions.
0.3/L3 and spell in-world checks remain pending. HUD still has narrow green radar,
missing hunger frame and nav bleed. Keep these visible rather than scoring them passed.

Next three actions:
1. git pull --ff-only; read the top pending row and start W1.2 Lychfield crypt.
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

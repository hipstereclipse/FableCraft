# Continuation prompt

Continue the FableCraft → TLC Conformance plan on Linux.
Repository: /run/media/eclipse/8E025A94025A80DF/Users/Eclipse/Fablecraft
Branch: phase3-will-destiny
Remote: https://github.com/hipstereclipse/FableCraft.git

Read docs/CONFORMANCE_PLAN.md and docs/CONFORMANCE_CHECKLIST.md. The source plan and
six reference snapshots are in docs/. User override (2026-09-12): finish the spell WIP
and continue as far as practical without permission questions. Retain separate
milestone commits, validation, immediate pushes, evidence and fresh handoffs.

Current milestone: C3 — generate reproducible progress scores; status done.
Last resolved prior commit: b3a1a45 (pushed before this milestone).
Containing commit: TLC Conformance — C3: generate reproducible progress scores.
Resolve current hash: git log -1 --format=%H --grep='TLC Conformance — C3: generate reproducible progress scores'.
Replace previous SELF evidence with the actual hash next step; never invent a self-hash.

C3 implements the deterministic 45-leaf scoreboard in the marked checklist section.
Run python scripts/conformance_score.py --write after any row update, then --check.
CI now runs fifteen command gates, including ten scoreboard regression groups.
Missing/duplicate IDs, invalid statuses, missing evidence paths, stale generated text
and pending grades incorrectly marked done fail. Manual prose is preserved. Appearance
histograms use the current C2 audit and are not canon grades. docs/SCORING.md records
scope; screenshots/validation/C3/ records actual validation. C3 is done.

C2 remote CI passed at b3a1a45 (run34678157199); metadata is in validation/C2/remote-run.json.
C2 links29 assets/renders and runtime placement roles, fixes four rectangular placement
bounds and the stale27-block Guild asset, and moves Maze from the solid tower column
to clear study floor (46,12,70). Its manual placement/interaction checklist remains
pending in docs/STRUCTURE_CONTRACT.md. Inspect the latest pushed workflow for its
actual head before beginning the next milestone; previous success is not current proof.

C1/L4 remote CI also passed. L4 release remains blocked by2,512 original-preview naming
findings, unselected final public title (Wayfarer Tales provisional), and missing save
compatibility remap. Do not exempt identifiers/paths/comments/legacy lookup keys.
0.3/L3 and spell in-world checks remain pending; HUD defects are still narrow green
radar, missing hunger frame and nav bleed. W1.1 can proceed independently: the existing
focus_site remains a purple monolith/crystal proxy, and its target is a weathered round
stone disc with blue glow while retaining fc:focus_site and travel registration.

Next three actions:
1. git pull --ff-only; read the top pending row and start W1.1 Cullis gate.
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

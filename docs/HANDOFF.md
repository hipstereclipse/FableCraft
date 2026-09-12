# Continuation prompt

Continue the FableCraft → TLC Conformance plan on Linux.
Repository: /run/media/eclipse/8E025A94025A80DF/Users/Eclipse/Fablecraft
Branch: phase3-will-destiny
Remote: https://github.com/hipstereclipse/FableCraft.git

Read docs/CONFORMANCE_PLAN.md and docs/CONFORMANCE_CHECKLIST.md. The source plan and
six reference snapshots are in docs/. User override (2026-09-12): finish the spell WIP
and continue as far as practical without permission questions. Retain separate
milestone commits, validation, immediate pushes, evidence and fresh handoffs.

Current milestone: C1 — add pinned continuous validation and clean-checkout proof; status in-progress.
Last resolved prior commit: cb9e0db (pushed before this milestone).
Containing commit: TLC Conformance — C1: add pinned continuous validation and clean-checkout proof.
Resolve current hash: git log -1 --format=%H --grep='TLC Conformance — C1: add pinned continuous validation and clean-checkout proof'.
Replace previous SELF evidence with the actual hash next step; never invent a self-hash.

C1 workflow and scripts/validate.py are implemented and locally green. Workflow
runs push/pull_request with contents:read, pins official v7 action commit hashes and
Ubuntu24.04/Python3.14.7/Node26.7.0, installs locked dependencies, runs every base and
regression gate plus original preview, and uploads ONLY tmp/validation logs. It never
publishes packs or runs --full. scripts/validate.py is the durable shared CI/local
entry point; use --output to save milestone logs. No untracked tools are required.

A fresh tracked snapshot of cb9e0db plus the two CI files passed all ten gate commands
with a new venv and npm ci. Evidence: screenshots/validation/C1/ and C1/clean/. The
snapshot used 684JSON rather than local685 because the inherited untracked pack-level
package.json is absent; all assets/tests pass without it. Runtime tests total42
(spells17, scan3, naming22); Python behavior4groups, animation10, branding16; HUD112/112,
animations54, expression31/21, lint0errors/19warnings. Local proof is not remote proof.

C1 status stays in-progress until the newly pushed workflow's actual GitHub run is
green. Query gh run list/view for branch phase3-will-destiny and inspect logs on failure;
record URL/head SHA/result honestly. Actions is enabled and GitHub API access works.
No user permission is needed to finish authorized CI verification. Naming milestones
L3.1–L3.3 and0.3 still have manual checks; L3.2/L3.3 also need final vocabulary review.
Original releases remain blocked by L4 and final naming selection. Do not relax the
zero-debt release rule merely to make CI green.

Next three actions:
1. git pull --ff-only; read the top pending row and start C1 remote-run verification, then L4 scanner groundwork or C2 contracts.
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

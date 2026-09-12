# Continuation prompt

Continue the FableCraft → TLC Conformance plan on Linux.
Repository: /run/media/eclipse/8E025A94025A80DF/Users/Eclipse/Fablecraft
Branch: phase3-will-destiny
Remote: https://github.com/hipstereclipse/FableCraft.git

Read docs/CONFORMANCE_PLAN.md and docs/CONFORMANCE_CHECKLIST.md. The source plan and
six reference snapshots are in docs/. User override (2026-09-12): finish the spell WIP
and continue as far as practical without permission questions. Retain separate
milestone commits, validation, immediate pushes, evidence and fresh handoffs.

Current milestone: L2 — isolate naming modes and local build outputs; status done.
Last resolved prior commit: 727d945 (pushed before this milestone).
Containing commit: TLC Conformance — L2: isolate naming modes and local build outputs.
Resolve current hash: git log -1 --format=%H --grep='TLC Conformance — L2: isolate naming modes and local build outputs'.
Replace previous SELF evidence with the actual hash next step; never invent a self-hash.

L2 is complete for item/data/lang/manifest generation. The shared fc_strings table
has strict faithful/original access; original alternatives (Wayfarer Tales etc.) are
provisional proposals, not the final public name. fc_branding copies source packs to
fresh tmp/builds/<mode>-<run> trees and invokes the display owners there. Both child
auditors take --root and inspect those copies. Default faithful archives now live in
that run's dist directory; legacy repository dist is untouched. Original mode requires
--preview and cannot package while L3/L4 remains incomplete. Source IDs/stats/UUIDs are
unchanged. docs/BRANDING.md explains ownership and docs/BRANDING_DEBT.md lists ten files
with remaining known display spellings; this is not the required L4 release scanner.

All L2 validators are green: build, emotes, HUD112/112, animation audit54clients,
ESLint0errors/19warnings, spell17 + scan3 tests, behavior4 groups, animation10 tests,
branding14 tests. Tests prove faithful generated text matches current source, original
items retain stats/IDs, owner paths recover on failure, and staged audit defects fail.
Evidence: screenshots/validation/L2/. Phase0.3 and spell in-world checks remain manual
and unrun; no Minecraft runtime is available in this session. Independent work may
continue without claiming those tests pass.

Next three actions:
1. git pull --ff-only; read the top pending row and start L3.1 (runtime string module and menu hub).
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

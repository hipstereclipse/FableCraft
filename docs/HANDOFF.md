# Continuation prompt

Continue the FableCraft → TLC Conformance plan on Linux.
Repository: /run/media/eclipse/8E025A94025A80DF/Users/Eclipse/Fablecraft
Branch: phase3-will-destiny
Remote: https://github.com/hipstereclipse/FableCraft.git

Read docs/CONFORMANCE_PLAN.md and docs/CONFORMANCE_CHECKLIST.md. The source plan and
six reference snapshots are in docs/. User override (2026-09-12): finish the spell WIP
and continue as far as practical without permission questions. Retain separate
milestone commits, validation, immediate pushes, evidence and fresh handoffs.

Current milestone: L3.2 — migrate legacy messages without rewriting saved identities; status in-progress.
Last resolved prior commit: d8361d4 (pushed before this milestone).
Containing commit: TLC Conformance — L3.2: migrate legacy messages without rewriting saved identities.
Resolve current hash: git log -1 --format=%H --grep='TLC Conformance — L3.2: migrate legacy messages without rewriting saved identities'.
Replace previous SELF evidence with the actual hash next step; never invent a self-hash.

L3.2 migrated 95 whole main.js messages through fc_strings.py; faithful templates
match the original AST values exactly. Runtime import is aliased msg to avoid local
t variables in NPC dialogue/title callbacks. Explicit placeName/titleName helpers
translate recognized persisted labels only at display time, retaining canonical save
names, jurisdiction keys, coordinates, title ownership and active selection. Two shop
sliders now use the declared UI2.0 options shape. Eighteen both-mode runtime tests cover
menu routes, slots, appearance, NPCs, travel, bounties, titles and shop callbacks.

The row remains in-progress: in-world checks in docs/RUNTIME_NAMING.md are unrun and a
final vocabulary/case audit remains (e.g. Guild seals, inn names, Hollow Men). Existing
known runtime matches now mostly represent canonical storage labels/comments. Explicit
legacy lookup keys in generated fc_strings.js are still L4 release debt, not exemptions.
The display inventory correctly strips color codes now, so prior counts understated
names immediately following formatting codes. There are 11 files of known display debt.
L3.3 should also translate the HUD navigation feed's saved landmark names; keep its
payload/clip arithmetic unchanged. No original distribution is authorized by previews.

All gates green in screenshots/validation/L3.2/: build56JS, emotes31/21, HUD112/112,
animations54, ESLint0errors/19warnings, spells17, scan-fallback3, behavior4groups,
animation10, branding15, runtime-strings18. Faithful and original staging validate;
only faithful local archives are produced under tmp/builds/<run>/dist. Public original
packaging remains blocked until L4 scanning and final title selection. Wayfarer Tales
is provisional. Manual spell and Phase0.3 engine checks also remain unrun.

Next three actions:
1. git pull --ff-only; read the top pending row and start L3.3 (Will, logbook, emote and HUD display text).
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

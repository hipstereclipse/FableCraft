# Continuation prompt

Continue the FableCraft → TLC Conformance plan on Linux.
Repository: /run/media/eclipse/8E025A94025A80DF/Users/Eclipse/Fablecraft
Branch: phase3-will-destiny
Remote: https://github.com/hipstereclipse/FableCraft.git

Read docs/CONFORMANCE_PLAN.md and docs/CONFORMANCE_CHECKLIST.md. The source plan and
six reference snapshots are in docs/. User override (2026-09-12): finish the spell WIP
and continue as far as practical without permission questions. Retain separate
milestone commits, validation, immediate pushes, evidence and fresh handoffs.

Current milestone: L3.1 — generate runtime names and migrate the menu hub; status in-progress.
Last resolved prior commit: 3642d33 (pushed before this milestone).
Containing commit: TLC Conformance — L3.1: generate runtime names and migrate the menu hub.
Resolve current hash: git log -1 --format=%H --grep='TLC Conformance — L3.1: generate runtime names and migrate the menu hub'.
Replace previous SELF evidence with the actual hash next step; never invent a self-hash.

L3.1 code and automated validation are complete; row remains in-progress for its
explicit manual menu checklist in docs/RUNTIME_NAMING.md. fc_strings.py owns the new
fc_strings.js. It emits selected-mode semantic names, whole messages and canonical
item/entity display names. Hero Menu text and key main.js inventory/map/status labels
use it; bridge keys and save IDs are stable. Eight both-mode boundary tests cover menu
routes, quick-slot mutation, interpolation and Appearance. Fixed existing UI2.0 modal
argument incompatibility and aura zero persistence; before-failure evidence is saved.
Two legacy shop sliders still use obsolete positional options: fix those in L3.2.

All current gates green: build (56JS), emotes31/21, HUD112/112, animations54,
ESLint0errors/19warnings, spells17, entity-scan3, behavior4groups, animation10,
branding14 and runtime-strings8. Logs: screenshots/validation/L3.1/. Original preview
passes staged asset validation but retains ten files of known literal debt. The
inventory shrank within main.js and herobook.js, not to zero. Next: main.js runtime
quest/town/shop/crime messages and saved-site display migration without changing save
keys or coordinates. L3.3 owns logbook/emote/HUD text. L4 remains fully blocked on
release scanning and the final public name (Wayfarer Tales is provisional).

L2 staging policy remains: default faithful packages only under tmp/builds/<run>/dist;
--branding original requires --preview and produces no archives. Do not edit generated
fc_strings.js manually. Regenerate with python scripts/fc_strings.py. No Minecraft
in-world tests have been run; Phase0.3 and spell/manual rows remain pending.

Next three actions:
1. git pull --ff-only; read the top pending row and start L3.2 (quests, towns, shops and crime).
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

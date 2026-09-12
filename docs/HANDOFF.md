# Continuation prompt

Continue the FableCraft → TLC Conformance plan on Linux.
Repository: /run/media/eclipse/8E025A94025A80DF/Users/Eclipse/Fablecraft
Branch: phase3-will-destiny
Remote: https://github.com/hipstereclipse/FableCraft.git

Read docs/CONFORMANCE_PLAN.md and docs/CONFORMANCE_CHECKLIST.md. The source plan and
six reference snapshots are in docs/. User override (2026-09-12): finish the spell WIP
and continue as far as practical without permission questions. Retain separate
milestone commits, validation, immediate pushes, evidence and fresh handoffs.

Current milestone: L3.3 — route logbook expressions and HUD labels through generators; status in-progress.
Last resolved prior commit: 833fbaf (pushed before this milestone).
Containing commit: TLC Conformance — L3.3: route logbook expressions and HUD labels through generators.
Resolve current hash: git log -1 --format=%H --grep='TLC Conformance — L3.3: route logbook expressions and HUD labels through generators'.
Replace previous SELF evidence with the actual hash next step; never invent a self-hash.

L3.3 code and automated tests are delivered; manual/catalog review remains pending.
Logbook narration uses message templates; canonical mob names are displayed without
rewriting existing cleaned kill/discovery keys. Thirteen expression-system messages
and the four generated Oracle names now use the single naming owner. Emote IDs,
unlocks, animation bindings and rating axes remain unchanged. HUD runtime had no
actual generator despite the inherited ownership rule: scripts/gen_hud_runtime.py
now emits scripts/templates/hud_runtime.js into fable_hud.js. Edit the template and
regenerate. Both HUD feeds translate saved site names without touching payload shape.

All gates green in screenshots/validation/L3.3/: build56JS, emotes31/21, HUD112/112,
animations54, ESLint0errors/19warnings, spells17, scan3, behavior4groups, animation10,
branding16, runtime22 tests. HUD tests assert all23lines and spacer/radar boundaries.
Inspected faithful preview: unchanged radar-column, missing hunger-frame and nav-bleed
defects from0.2 remain. No visual A-grade or in-world pass. Preview/logs are committed.

Known original-preview display debt is now six files, mostly explicit legacy keys and
historical comments. This is NOT a complete release scan: lower-case IDs, filenames,
escapes, aliases/case variants, unknown deed labels and unlisted vocabulary remain L4
work. Original packaging stays blocked. Public title Wayfarer Tales is provisional;
final naming requires user selection at release, not an autonomous claim. Independent
C1 validation tooling can proceed without opening that release gate. Continue without
permission pauses under the user's existing authorization.

Next three actions:
1. git pull --ff-only; read the top pending row and start C1 (independent continuous-validation tooling; L4 release work stays blocked).
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

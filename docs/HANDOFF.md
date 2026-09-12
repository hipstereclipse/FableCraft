# Continuation prompt

Continue the FableCraft → TLC Conformance plan on Linux.
Repository: /run/media/eclipse/8E025A94025A80DF/Users/Eclipse/Fablecraft
Branch: phase3-will-destiny
Remote: https://github.com/hipstereclipse/FableCraft.git

Read docs/CONFORMANCE_PLAN.md and docs/CONFORMANCE_CHECKLIST.md first. The approved
source plan and all six reference snapshots are in docs/. Latest user instruction
(2026-09-12): finish Ghost Sword/Assassin Rush, then do as much of the plan as possible
without permission questions. Continue automatically between milestones; retain one
commit per milestone, targeted validation, immediate push and honest handoffs.

Current milestone: bootstrap complete; next active phase is 0, beginning 0.1.
Last resolved implementation commit: ccafd4c (spell completion), pushed to origin.
Containing document commit: TLC Conformance — bootstrap: document set.
Resolve its exact hash with git log -1 --format=%H --grep='TLC Conformance — bootstrap: document set'.
A document cannot contain its own commit hash; replace prior SELF references next step.

Validator state: build GREEN (685 JSON/341 PNG/535 WAV/29 structures/55 JS), expressions
GREEN (31, 21 social NPCs), HUD GREEN (112/112), lint GREEN with 19 existing unused-code
warnings, spell mocks GREEN (17). Evidence: screenshots/validation/bootstrap/ (latest), screenshots/validation/spells/. Animation
live-driver audit not implemented until 0.3. In-world spell checks UNRUN; see
SPELL_COMPANIONS.md. No in-game conformance pass or visual grade is claimed.

Next three actions:
1. git pull --ff-only; mark 0.1 in-progress. Back up and inspect the stripped
   scripts/gen_behavior.py diff against 6cfea15; restore/port only that generator.
2. Add isolated entity/item regression tests; prove failure before and success after
   repair, preserving NPC reactions, persistence, married properties and scalar icons.
3. Run the base validators, update checklist/handoff, commit 0.1 and push; then continue
   0.2 orphan tooling, 0.3 attack driver and 0.4 doc drift in separate milestones.

Landmines: roughly 699 apparent tracked edits are mostly CRLF noise. Never git add -A,
commit -a, renormalize or add .gitattributes. Read all diffs with --ignore-cr-at-eol;
stage explicit paths with reviewed patches so line-ending noise does not enter commits.
The stripped behavior generator is still unsafe: do not run it or build_addon --full
until 0.1 tests pass. Never hand-edit generator-owned entities, RP models/animations/
controllers/attachables/particles, fable_emote_registry.js, fable_hud.js, fc_gamedata.js,
or texts/languages.json. Keep GUILD anchors coupled with gen_structures; fc:reanchor is
not a substitute for checking coordinates, and all-cross-references-OK does not check them.
HUD payload order/spacers/clip offsets also move together. Keep the scatter engine.

Spell WIP is finished in its own commit; do not stash/revert/refold it into Phase 0.
Remaining substantive dirt includes old gen_behavior, BOUNTY_SYSTEM.md, three locally
rebuilt dist archives and four alignment PNGs, plus orphan tools/UI renders and tmp/.
Preserve unrelated work. Old patch_guild_tiling.py must not be run blindly. Dist rebuilds
are local milestone validation only until L4: faithful names are local-only, distributed
builds must use original branding; no monetization. Bootstrap removes donation links.

Git writes require sandbox escalation here. Git identity was unset; use the existing
repository author identity from git log for commit-scoped -c options, not global config.
The first chained commit/push was auto-review rejected as an unverified destination;
a separate push succeeded after proving origin matched the user's explicitly named
GitHub URL. Reuse that verified destination, no force pushes. npm installation succeeded
with network escalation. Record any new command failure honestly; never claim a push
or runtime test succeeded without output.

# Continuation prompt

Continue the FableCraft → TLC Conformance plan on Linux.
Repository: /run/media/eclipse/8E025A94025A80DF/Users/Eclipse/Fablecraft
Branch: phase3-will-destiny
Remote: https://github.com/hipstereclipse/FableCraft.git

Read docs/CONFORMANCE_PLAN.md and docs/CONFORMANCE_CHECKLIST.md. The source plan and
six reference snapshots are in docs/. User override (2026-09-12): finish the spell WIP
and continue as far as practical without permission questions. Retain separate
milestone commits, validation, immediate pushes, evidence and fresh handoffs.

Current milestone: W2.3 — Oakvale Memorial Garden; status in-progress.
Last resolved prior commit: a0b59f28821869c4dfb8324c7de874fd531e0991 (pushed).
Containing commit: TLC Conformance — W2.3: connect Oakvale Memorial Garden.
Resolve current hash: git log -1 --format=%H --grep='TLC Conformance — W2.3: connect Oakvale Memorial Garden'.
Replace previous SELF evidence with the actual hash next step; never invent a self-hash.

W2.3 retains fc:oakvale_village, widening 35x14x35 to 53x14x35 for an eastern
raised garden. Runtime and C2 manifest match. The original squeezed memorial is
replaced by a larger axe-bearing statue, six graves and a walled garden reached
by an east lane and two steps. Oak/well/field/coast and five emitted chest coordinates
remain. Three existing resident types have explicit clear spawns; new computed
Cullis arrival (26,1,17) is clear. Six regression groups pass; the old owner fails
five, while its population test still passes. See docs/OAKVALE_MEMORIAL.md.
The original cottage/quay overlap overwrites an attempted sixth chest; W4.1 still
owns that repair. No garden reward, digging mechanic or saved-world retrofit added.
Two developer-only candidate reference images were fetched to ignored tmp/conformance.
The source calls the game Fable without confirming original-2005 TLC provenance.
The candidate statue lunges with a diagonal axe; our upright figure/vertical axe,
simplified entrance and hillside remain visual gaps. No canon grade is claimed.

W2.2 at a0b59f2 retains fc:hook_coast at 37x20x37; lighthouse stairs reach its lamp
deck, the Abbey gains a raised terrace/stairs, six graves and a north bell connect
to streets, cottage doors have two-block headroom and quay steps remain connected.
Three original resident types use clear explicit anchors; the inherited Oracle is
not a canon claim. Six groups pass; old owner fails six. Fire Heart, rotating beam,
ship travel, Maze fight, Abbey barrier/dispelling and evacuation remain missing.
See docs/HOOK_COAST.md. C2 now checks optional mobSpawns count, numeric shape and
finite horizontal/feet/head bounds. Review removed an unintended copy of Hook Coast
anchors into Snowspire; negative fixtures now catch it. Snowspire remains unchanged.

W2.1 at fae89fb78cb8b10a27ef624281f748262a993539 extends fc:bowerstone_market to
37x21x59, shifts the old district +22z, and adds a furnished two-floor manor and
forecourt, class wall and bridge stairs. Five clear residents include existing
Lady Grey once per new town; all eight chests and Cullis arrival are route-tested.
Six groups pass; old owner fails six. Arena admission/resident exclusion, Solus shop,
jail, full Quay and multi-town Lady Grey behavior remain gaps. See BOWERSTONE_NORTH.md.

W1.4 at ed57d1e1cbc58eb8daad8686ec863f71bb6e070c expands fc:arena_ring to 27x12x41,
opens its south gate and adds preparation/hero halls and west seating stairs.
Three enemies plus a trader spawn clear. Seven groups pass. Staged rounds, spectators,
scored training and confinement remain gaps. See docs/ARENA_HALLS.md.
W1.3 at add099a2a33765faf3aab9eda59df09427454856 adds Twinblade camp rings/landmarks;
W1.2 at 608edf164b31b48f53c9ed601cde1ef31f67a485 adds Lychfield crypt landmarks.
Nostro's command/onward route is missing; never register an unrelated Demon Door riddle.
No fc:place handler exists: raw /structure load places blocks only; scatter initializes
population/loot/travel. Keep procedural scatter, no fixed map or old-region retrofit.

All 22 local scripts/validate.py gates pass. C2 asset/render hashes are current.
Full all-category pipelines ran in tmp/conformance/<ID>-full-screenshots for
W1.2/W1.3/W1.4/W2.1/W2.2/W2.3. Logs, audits and primary/detail views are in each
milestone's screenshots/validation/<ID> evidence. These are offline renders, not
engine or canon passes. C2's in-world checklist remains pending in STRUCTURE_CONTRACT.md.

C3 requires python scripts/conformance_score.py --write after EVERY checklist change,
then --check. It tracks 45 leaves, automated/manual counts and offline appearance
metrics separately. W2.2 remote CI passed at a0b59f2 (run 34701741654); metadata is
screenshots/validation/W2.2/remote-run.json. W2.1/W1.4 and earlier runs also passed
at their recorded commits. Inspect the newest pushed workflow's actual head next.

L4 releases remain blocked: last recorded original preview had 2,512 known-name
findings, final public title is unselected (Wayfarer Tales provisional), and saved-world
remap is missing. No exemptions. 0.3/L3/spell in-world checks remain pending. HUD still
has narrow green radar, missing hunger frame and nav bleed; keep them visible.

Next three actions:
1. git pull --ff-only; read the top pending row and start W2.4 Grey House and cellar.
2. Execute its numbered playbook and base/domain validators; retain actual output
   under screenshots/validation/<ID>/ and mark every manual observation unrun.
3. Update checklist/handoff in one explicitly staged milestone commit, push to origin,
   and continue automatically. On context limits print this prompt verbatim.

Landmines: hundreds of apparent edits are CRLF noise. Never git add -A, commit -a,
renormalize, create .gitattributes or discard unrelated work. Read every diff with
--ignore-cr-at-eol; use named reviewed patches for staging to avoid newline churn.
Behavior generator was restored from 6cfea15 in 0.1; isolated tests prove social/react,
persistence/marriage, cosmetic and 194-item icon/damage contracts. The stripped copy
is preserved at tmp/conformance/gen_behavior_stripped.py. Before regeneration run
python scripts/tests/test_gen_behavior.py. Prefer targeted generators; lifting the
0.1 gate did not prove unrestricted --full output drift is safe.

Never hand-edit generator-owned BP entities, RP models/animations/controllers/
attachables/particles, fable_emote_registry.js, fable_hud.js, fc_gamedata.js or
texts/languages.json. Find/establish an owner if memory disagrees. Keep GUILD anchors
coupled to gen_structures; /scriptevent fc:reanchor refreshes but does not audit them.
All-cross-references-OK validates assets only. Keep HUD payload/spacers/clip offsets
coupled. No Guild tiling was applied; never run its one-off patch blindly. Maze's
corrected spawn remains (46,12,70). wd alignment is authoritative; preserve the
legacy progression bridge that funnels old XP spending through wd.

Ghost Sword/Assassin Rush are completed separately in ccafd4c; never stash/revert/refold
them into conformance. SPELL_COMPANIONS.md retains pending engine checks.
BOUNTY_SYSTEM.md was reconciled in 0.4. Preserve inherited local dist archives, four
scripts/_align/overlay_*.png renders and unreviewed scratch files. Required milestone
builds package under tmp/builds/faithful-<run>/dist; never stage/publish faithful
archives. Public builds require original branding and a zero-debt L4 scan first.
Original/generated assets only; no extracted Fable content, free and never monetized.

Git writes/network require escalation here. Author identity is unset; use the existing
repository identity from git log through commit-scoped -c options, not global config.
Separate pushes to the verified/user-authorized origin succeeded; an earlier chained
commit/push was rejected before destination verification. No force push. Preserve
local commits and report push failure honestly if origin cannot be updated.

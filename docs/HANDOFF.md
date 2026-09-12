# Continuation prompt

Continue the FableCraft → TLC Conformance plan on Linux.
Repository: /run/media/eclipse/8E025A94025A80DF/Users/Eclipse/Fablecraft
Branch: phase3-will-destiny
Remote: https://github.com/hipstereclipse/FableCraft.git

Read docs/CONFORMANCE_PLAN.md and docs/CONFORMANCE_CHECKLIST.md. The source plan and
six reference snapshots are in docs/. User override (2026-09-12): finish the spell WIP
and continue as far as practical without permission questions. Retain separate
milestone commits, validation, immediate pushes, evidence and fresh handoffs.

Current milestone: W2.2 — Hook Coast lighthouse and Abbey; status in-progress.
Last resolved prior commit: fae89fb78cb8b10a27ef624281f748262a993539 (pushed).
Containing commit: TLC Conformance — W2.2: connect Hook Coast lighthouse and Abbey.
Resolve current hash: git log -1 --format=%H --grep='TLC Conformance — W2.2: connect Hook Coast lighthouse and Abbey'.
Replace previous SELF evidence with the actual hash next step; never invent a self-hash.

W2.2 retains fc:hook_coast at 37x20x37. Three internal lighthouse stair flights
reach a new lamp deck; the foundation fills water beneath the tower. The Abbey
sits on a two-block terrace with eastward stairs and a clear nave. Six keeper/monk
markers and a north bell connect to cleared streets, cottage doors have two-block
headroom, and quay steps reach the original five chests. The three existing resident
types have clear explicit anchors; Cullis remains at (18,1,18). Six regression
groups pass and the previous owner fails all six. See docs/HOOK_COAST.md for routes,
coordinates, render provenance and unchecked manual tests. The inherited Oracle
is not a claim of canon. Fire Heart, rotating beam, ship travel, Maze fight,
Abbey barrier/dispelling and evacuation remain unimplemented.

W2.2 also strengthens C2: optional mobSpawns must match the mob count, contain
finite numeric triples and fit horizontal/feet/head bounds. Review caught and
removed an unintended copy of Hook Coast anchors into Snowspire. A saved before
fixture exposes the old missed error; two new C2 regression groups reject this
and malformed/count/headroom cases. Snowspire's runtime entry remains unchanged.

W2.1 at fae89fb retains fc:bowerstone_market, extends 37x16x37 to 37x21x59 and shifts the
existing market/river/houses +22 along z. Runtime and C2 manifest match. A north
stone manor has two furnished floors, a clear two-wide staircase and a gated
forecourt. The internal class wall connects to the bridge arch; its passage stays
open because staged Arena completion/admission is not implemented. The clock tower
moves west to clear the street. Bridge approach stairs, all eight chests (seven
retained, one new manor chest), five resident spawn points and center Cullis arrival
are route-tested. The four original resident types remain; existing Lady Grey is
added once per newly scattered town. Six regression groups pass; the old owner
fails all six. See docs/BOWERSTONE_NORTH.md for coordinates/routes/manual checks.
Arena invitation, resident exclusion, Solus-specific shop, jail and full Quay remain
gaps. Multiple-town Lady Grey interactions and engine behavior need manual review.
Existing saved structures and regions are not retrofitted.

W1.4 at ed57d1e keeps fc:arena_ring, extends to 27x12x41, opens the south pit gate,
adds preparation/hero halls and a west stair aisle. Three enemies plus one trader
use clear spawn points. Seven tests pass; staged rounds, spectators, scored training,
enemy confinement and engine checks remain gaps. See docs/ARENA_HALLS.md.

W1.3 at add099a adds Twinblade's two camp rings, command tent, three stalls, fighting
circle, crew tents and accessible watchtowers, retaining fc:bandit_camp at 33x13x33,
four enemies and four chests. Six tests pass; original-2005/in-world checks remain.
W1.2 at 608edf1 adds Lychfield's keeper hut, three stone sarcophagi, gate-stair stone
face and clear undead spawns, retaining fc:graveyard at 25x13x25. Seven tests pass.
Nostro's command, speech/opening and onward path are missing; do not register an
unrelated generic Demon Door riddle. See docs/TWINBLADE_CAMP.md and
LYCHFIELD_CRYPT.md. No fc:place handler exists: raw /structure load places blocks
only; scatter initializes population and loot. Keep procedural scatter, no fixed map.

All 21 local scripts/validate.py gates pass. poi_population.cjs is the shared
actual-source spawn harness; W1.2's graveyard_placement.cjs remains a wrapper.
C2 asset/render hashes are current. Full all-category passes run under isolated
tmp/conformance/<ID>-full-screenshots for W1.2/W1.3/W1.4/W2.1/W2.2;
logs, audits, primary cards and south/cutaway views are in each milestone's evidence.
Original-TLC comparison remains pending; MobyGames candidates for Twinblade/graveyard
could not be fetched. No canon-A or in-world pass is claimed for these renders.

C3's scoreboard requires --write after EVERY checklist change:
python scripts/conformance_score.py --write, then --check. It tracks 45 plan leaves,
explicit automated/manual counts and offline appearance grades separately.
W2.1 remote CI passed at fae89fb (run 34701284378); metadata is in
screenshots/validation/W2.1/remote-run.json. W1.2/W1.1/C2/C1/C3/L4 also passed at
recorded commits. Inspect the newest pushed run for its actual head before the next
milestone. C2's in-world checklist stays pending in docs/STRUCTURE_CONTRACT.md.
No Guild tiling was applied; Maze's corrected spawn remains (46,12,70).

L4 releases remain blocked: last recorded original preview had 2,512 known-name findings, unselected final
public title (Wayfarer Tales provisional), and missing saved-world remap. No exemptions.
0.3/L3 and spell in-world checks remain pending. HUD still has narrow green radar,
missing hunger frame and nav bleed. Keep these visible rather than scoring them passed.

Next three actions:
1. git pull --ff-only; read the top pending row and start W2.3 Oakvale Memorial Garden.
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

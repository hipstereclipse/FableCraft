# Guild archery firing divider

GP21, 2026-09-13. A newly inspected original TLC archery screenshot clearly shows
a low timber divider between the firing platform and the scenic targets. The
current range had four isolated cornerposts but no transverse divider. New Guild
structures now add two connected rail sections toward the targets, with an open
firing bay. This is a bounded reference-led improvement, with native acceptance
and the larger range layout still open.

## Original features and block adaptation

[Steam view 141099874](https://steamcommunity.com/sharedfiles/filedetails/?id=141099874)
was posted April 24, 2013 on the original TLC app 204030. Full-resolution pixels
show upright capped posts, broad paired horizontal timbers, diagonal braces and
a curved timber lip around the dirt firing platform. The rail crosses the firing
foreground; its ends and openings are outside the image. The scenic panel has
separate mountain/castle cutouts at different depths in front of it.

The new source and the earlier GP16 view 689540321 support a firing divider.
Neither establishes a complete circular range, five perimeter dummies or exact
source proportions. Those inherited layout choices are now explicitly described
as adaptations in the generator. The original x80/x92 side-rail feasibility
survey is not evidence for original rail orientation, so that hypothetical
22-cell perimeter was not authored.

`build_guild_archery_firing_rails` emits ten spruce-fence cells: x80..81 and
x85..92, y1, z38. Stock fences approximate the paired horizontal timbers; they
omit the diagonal bracing, broad carved members and capped paired posts. Exact
extent, block material, asymmetry, axis alignment and the three-column opening
at x82..84 are Minecraft adaptations. Full original perimeter fidelity is open.

The firing opening is deliberate. The current Skill ray is about y2.35..2.45;
a fence placed at y1 has a conservative collision extent through y2.5. The
block-cell ray harness alone would accept air in y2 above that lower fence.
A separate expanded-shape sweep detects this overlap in a negative fixture.
The authored opening remains clear at all five tested actor displacements.
This is offline reasoning about collision bounds, not native collision proof.

## Coupled routes and scope

The final helper consumes no RNG. Independent serialized DP7/current comparison
finds exactly ten changed cells among 395,280; all other cells, palette, states,
metadata, layout, anchors and seeded random streams remain exact. Both bridges,
the scenic board, every target/dummy/hay support, all floors, the unique fletching
table, doors, roofs, Maze at (46,12,70) and 678 surveyed Maze reservations stay.
Existing occupied Guilds are never rebuilt; reanchor still refreshes coordinates.

Only the ten now-occupied rail cells leave the conservative walking graph
(13,822 to 13,812 nodes). Every other node and gate-reachable node stays. All
seven complete gate routes have identical coordinate sequences. Eight local
routes, all three firing-gap columns, the actual Skill shot checks and the
13-sample future arrival corridor remain clear. Six independent route failures
are detected; the additional lower-fence fixture exposes the block-ray limit.
The 27 arrival prototype refusals remain a proposal, not native navigation.

## Verification and next comparison

Behavior regression passed before targeted generation. Whole-pack hashing found
only the Guild structure changed among 1,663 files. All 55 base gates pass in the
isolated reviewed-index snapshot. The independent helper, exact hashes, raw logs
and six decoded before/after schematics are in `screenshots/validation/GP21/`.
All 65 ESM checks, fresh C2, all 282 full PNGs and Guild diagnostics pass.
Only Guild changes among 36 assets/C2 images; only its card and the places
gallery change among 282 full PNGs. Seven applicable documentation scenes were
regenerated; the two full-campus scenes and archery scene change. The full and
documentation renderers simplify fences as cubes; focused schematics draw thin
approximate posts/rails. GP21 becomes the next visual baseline.
Render grades do not measure original-game fidelity or playability.

One newly accepted TLC image brings the supplementary source corpus to 27. Six
additional classic exterior photos from a 2009 post remain uncounted corroboration
pending exact-edition confirmation. Only their URLs, hashes and observations are
committed; all external pixels remain ignored. The production divider relies on
the explicitly attributed TLC archery views. See GUILD_ONLINE_REFERENCES.md and
the GP21 reference record for exclusions and provenance.

Next compare the separate low scenic mountain/tower forms visible in 141099874,
the platform edging and the adjoining architecture while preserving targets and
the full active firing lane. Continue interior/bridge reference work; deck width,
original bracing and exact room dimensions remain unresolved. Native lighting,
collision, movement, two-Hero passing and saved-world acceptance remain unrun.
Purposeful Skill arrival still needs the existing native offset/search/event
calibration. No unchanged failed server-download retry was attempted.

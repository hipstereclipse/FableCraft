# GP21 reviewed checkpoint

Code baseline is DP8 2d56f97e325642c936b7ad4898efff09981bb926, whose exact-head
CI 34740141802 passed. Geometry/full-render comparison is DP7, since DP8 changed
no geometry. Root inspected original TLC view 141099874, reviewed the final
no-RNG helper and exact staged patch, and inspected all six decoded detail
schematics, the C2 Guild image, full Guild card, places gallery and three updated
documentation images. The independent geometry reviewer found no source blocker.

The source image shows a transverse firing divider with broad horizontal timbers
and diagonal braces. The new stock-fence sections approximate this motif, with
explicitly adapted dimensions, material and a three-column firing gap. There is
no claim of complete range/perimeter fidelity or restored original bracing.
The source's actual ends/openings are outside its crop.

Exactly ten former-air cells change. All other 395,270 campus cells, RNG, palette,
layout, targets, props, roofs and 678 Maze reservations stay exact. The independent
actual predecessor/current serialized comparison keeps seven complete gate paths
identical, eight local routes open, and all tested emitted Skill rays clear under
a conservative expanded-fence sweep. A fence added in the gap is caught by that
sweep even though the older block-cell harness accepts y2 air above it. This is
an explicit offline-check boundary, not native collision verification.

Behavior regression passed before targeted Guild generation; only Guild changed
among 1,663 whole-pack files. All 55 base gates and 65 ESM checks pass in the
isolated reviewed-index snapshot. Fresh C2, all 282 full PNGs and Guild diagnostics
pass. Only Guild changes among 36 assets/C2 images; only the Guild card and places
gallery change among 282 full PNGs. All 35 other assets/C2 images and 280 other
full PNGs remain byte-exact. Seven applicable documentation scenes were regenerated:
only 01_hero_guild_gate, 12_guild_wide_lake_view and 26_archery_backboard change.

Concurrent README/screenshot commit 2c34743f4cc8414f66fac7c9e27f62b5bdcfa623 and
its producer code are preserved (CI 34740012446 passed). The new README edits
update the checkpoint labels, link the divider and correct shared per-source
room/reward semantics. Its architecture/room additions remain intact. Documentation
images are offline composites; the shared renderer draws fences as full cubes,
while the six focused schematics draw thin approximate timber members.

Initial full/doc render launches failed before Python ran because the new
snapshot lacked tmp/. The shell messages are retained in render-launch-errors.log;
the ignored directory was created and both commands reran successfully. A later
evidence-copy helper used a dotted summary name instead of the actual hyphenated
name; its error is retained. Only that helper was corrected, without rerunning
successful rendering or changing production/tests. These were orchestration
errors, not failing gameplay gates. C2 finished and its generated record/image
were reviewed/staged before base validation, avoiding stale-source build evidence.

Final docs were refreshed after source validation; the legacy scoreboard was
regenerated and checked at 45 leaves/7 done. Named staging excludes inherited
newline noise, seven protected binaries, local configs and all external pixels.
Native lighting, collision, movement, two-Hero behavior and saved-world acceptance
remain unrun. New geometry is only for new placements; no occupied Guild rebuild.
GP21 becomes the visual baseline. Whole-facility and both portal pilots remain
in-progress; the next return/reward hardening must have its own reproduced scope.

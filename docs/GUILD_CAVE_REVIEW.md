# Guild cave and Chamber route review

GP4 audit, 2026-09-12. This historical pass changed documentation and offline evidence only.
GP5 implements new-world repairs in [GUILD_CAVE_LIFECYCLE.md](GUILD_CAVE_LIFECYCLE.md);
the frozen outcomes below describe GP4, not the current construction owner.
This audit leaves production implementation, assets and saved worlds unchanged.
The [reproducible probe](../screenshots/validation/GP4-cave-audit/run_probe.py)
executes frozen, hashed excerpts of the actual `placeGuildAnnexes`, `carveGuildCaves`,
`hollowChamber` and `isCullisConfigured` callbacks from the audited `main.js` against
captured Guild/Chamber generator voxels in a solid-stone fixture. The Guild base
is `(0,40,0)` and the Chamber structure origin is `(11,18,27)`.
`routes.py` checks the assembled blocks with cardinal movement, real full/slab
surfaces and two-block headroom. This is not live Bedrock physics execution.

## Ranked findings

1. **Incomplete caves become permanently complete.** `main.js:580` swallows each
   block access/write failure; `:681` writes `fc_guild_caves_done=true` when the
   generator is scheduled, before its first write. The flag then blocks retry
   at `:578`. The actual probe records done=true, writes=0, queued jobs=1 just
   after scheduling. Cancel after two generator yields/50 writes: retry queues
   zero jobs. With one unavailable bridge head cell `(26,20,16)`, that cell
   remains solid stone, yet done=true and a second invocation writes nothing.
   In addition, `placeGuildAnnexes` has only one caller (`main.js:521`), inside
   the initial Guild decoration try. Its placement guard cannot supply retries
   from the normal maintenance interval (`:1228` onward). A first placement
   exception, earlier decoration exception, or interrupted carve can strand the
   route for that saved world.

   **Focused fix/test:** extract a cave lifecycle owner with explicit running/
   verified completion phases and retries for failed initial generation; only
   commit completion after route cells were written and verified. Add production
   callback tests for job cancellation, unavailable getBlock, thrown setType,
   failed Chamber placement and retry after reload. Existing legacy `done`
   worlds need a separate conservative policy: do not automatically recarve
   their occupied shaft, Chamber or player changes just because a new version
   can generate a better route.

2. **The library threshold is missing its expected floor.** The shaft carve
   opens its entire south face for `y >= base.y` (`main.js:600–607`), deleting the
   entrance's floor at `(27,base.y,16)`. The actual path is feet heights
   `(27,base.y+1,17) → (27,base.y,16) → (27,base.y+.5,15)`. The one-block first
   descent needs a jump on return. A half-step graph cannot connect the library
   to the top slab; permitting one-block jumps produces the three-point path.
   The helix itself and the landing-to-arch causeway pass both directions with
   42 and 15 route points respectively.

   **Focused fix/test:** preserve a full entrance floor at base.y while opening
   only the standing/head volume above it. Test the actual assembled threshold,
   each half-step transition and both directions. The existing
   `scripts/_verify_caves.py:140` invents a supported entry at base.y+1 and
   never checks its support; its independent mirrored geometry reports PASS
   against this actual defect. Replace this mirror as the route authority.

3. **Chamber Cullis registration cannot detect the generated core.** Runtime
   registers local Chamber y7 (`main.js:550–551`), but the generator's RAISE=3
   puts the platform block at local y4 and feet at y5
   (`gen_structures.py:3764–3765`, `:3787`). `isCullisConfigured` probes only
   registered y−1/y/y+1 (`main.js:4194–4198`), so it misses the actual core three
   blocks below the registered point. Actual callback result: false at the
   registered `(26,25,42)`, true at corrected standing `(26,23,42)`.
   The standing/dwell portal branch at `main.js:4274` therefore does not activate;
   the separate sneaking fallback still falls within the four-block y range.

   **Focused fix/test:** use one generated Chamber interaction contract in the
   registration owner and assert `isCullisConfigured` on assembled voxels. A
   narrowly recognized old registry-height migration can update coordinates
   without replacing blocks or resetting progress.

4. **The Chamber hill adds three one-block rises.** The north approach from the
   arch to the Cullis has feet y20 through z35, y21 at z36–37, y22 at z38, and y23
   from z39. The generator explicitly constructs full-block terraces
   (`gen_structures.py:3768–3780`), despite calling them walkable. The route is
   available with jumps but has no half-step route either direction. A focused
   generated north stair/ramp could connect the existing floor and dais without
   moving either room or the Guild anchors. Saved-world geometry remains a
   separate migration decision.

## Reproduction and limitations

Run from the repository root:

```sh
python screenshots/validation/GP4-cave-audit/run_probe.py
```

Results and source excerpts are under
[screenshots/validation/GP4-cave-audit](../screenshots/validation/GP4-cave-audit/).
`source_manifest.json` hashes the audited files and exact callback excerpts;
`geometry_manifest.json` identifies the generated input geometry. The probe fixes
only random material selection for reproducible stone/moss comparisons. Input
structure grids and assembled cells are temporary and never replace assets.

The isolated model starts with solid stone beneath the Guild, places the actual
Guild and Chamber voxels, runs the production cave callback, then executes all
four scheduled Chamber hollowing callbacks. It proves the recorded outcomes for
that ordering. It does not establish every possible terrain-job interleaving,
chunk loading schedule, Bedrock collision shape or live player's movement.
Existing `_verify_caves.py` was evaluated only through its text report, without
writing its historical screenshots: it reports PASS for a mirrored route that
fails to check the missing actual entrance floor.

The highest next bounded pass should own the cave lifecycle and its production
callback tests. It must distinguish unfinished initial work from existing saved
geometry, preserve the Guild/Chamber anchors and inventory/progress, and avoid a
blanket recarve or Chamber replacement. The small threshold and registered-height
fixes can follow through the same geometry contract; the terraced hill needs its
own generated route pass. Live Bedrock acceptance remains unrun.

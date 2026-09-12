# Audit tooling and development outputs

Adopted in Phase 0.2, 2026-09-12. Install `requirements-dev.txt` and `npm ci`.
Run from repository root:

| Command | Purpose and limits |
| --- | --- |
| `python scripts/audit_hud.py --check` | Required 112 structural/font/payload checks; no image writes |
| `python scripts/audit_hud.py` | Writes synthetic preview + screenshots/ui/HUD_AUDIT.md |
| `python scripts/preview_hud_faithful.py` | Slices a representative payload through configured clips |
| `python scripts/_audit_anims.py` | Clip/controller/bone wiring; extended gate audit scheduled for 0.3 |
| `python scripts/_audit_match.py` | Guild target/generated/mismatch render; diagnostic percentages |
| `python scripts/_audit_roofs.py` | Guild support/eave heuristic; reports findings, not a conformance pass |
| `python scripts/_target_map.py` | Portable target-only render; no external image required |
| `python scripts/_target_map.py --reference /path/to/reference.png` | Optional reference overlay; missing image is an error |

The target map is a hand transcription of an owner-supplied Inkarnate map. Some
coordinates follow GUILD_LAYOUT, so it is not an independent canonical oracle.
Do not treat its percentage as TLC fidelity or substitute it for anchor coupling.
A standalone target render without --reference is explicitly not a comparison.

Observed baseline: animation clips/bones resolve for 51 mobs; Guild structural
cell agreement 85.3%, path recall 25.3%; support heuristic finds 0 disconnected
blocks and 385 eave cells in 52 clusters. Eaves may be intentional; this is a
review queue, not 385 established bugs. See screenshots/validation/0.2/.

The regenerated HUD preview was visually inspected: the sample radar appears as
a narrow green column, the hunger bar has no visible frame, and the navigation
strip shows adjacent-line text. These are unresolved preview/asset concerns;
112 passing checks do not prove in-game layout. Keep screenshots/ui/hud_faithful.png
as baseline evidence and compare against an actual Bedrock capture before changing
HUD generators. No A-grade visual conformance is assigned during tool adoption.

## One-off Guild tiling patch

The exact original is archived as [patch_guild_tiling.py.txt](archive/patch_guild_tiling.py.txt).
The untracked root copy is retained locally and ignored, not deleted or executed.
It is not a supported build step. Its prose still names a 112-wide fc:guild while
injected code uses 122-wide guild_hall; it hardcodes dimensions, assumes no rotation,
and catches tile-placement failures independently. Current generator/runtime use
one guild_hall with chunk-loading/retry logic. No observed current load failure
justifies applying an old migration automatically. Any future tiling work must
change generator/runtime/manifest/anchors together and test complete placement,
rotation, failure recovery and existing worlds.

## Files and packaging policy

- Version the six Python tools and curated screenshots/ui outputs. Preserve pre-existing
  tracked overlay_*.png changes for their original work; do not stage them here.
- Ignore tmp/, scripts/_align/_*.png and screenshots/structures/_chk_*.png scratch outputs.
  A selected diagnostic is copied into screenshots/validation/<milestone>/ for evidence.
- npm package manifests/flat lint config and requirements-dev.txt are development tooling,
  committed for reproducibility. .eslintrc.json is an obsolete local file, not used by ESLint 10.
- Run build_addon only at milestone validation boundaries; it rebuilds three local archives.
  Until L4, never stage or publish those faithful artifacts. After L4, release dist only at
  an accepted milestone, with original branding, zero forbidden literals and provenance.
- Required build dependencies must be tracked. Optional external reference images remain
  external; unavailable comparison inputs are reported, not treated as passing evidence.

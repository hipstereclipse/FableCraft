# Runtime naming progress

L3.1–L3.3 code is implemented; required in-world checks remain unrun.

`scripts/fc_strings.py` owns `packs/Fablecraft_BP/scripts/fc_strings.js`. Run the
Python file to regenerate faithful source output. Isolated builds invoke the same
emitter under the chosen branding context. The emitted module contains one selected
name/message variant, with strict semantic accessors and single-pass interpolation.
Unknown keys and missing substitutions throw; player-provided substitution text is
not reinterpreted as a template or translated as a proper name.

The Hero Menu, Magic, binding and Appearance page text now uses that module. Its
eleven-button order and bridge keys are unchanged. `main.js` uses canonical item and
entity display names instead of capitalizing internal IDs; this also corrects menu
spellings such as `Avos Tear`. Inventory counts, map heading/intro/recall and key
status labels now follow the mode. Unknown item IDs retain the previous fallback.
`menu_bridge.js` contains registration keys and comments only, so it needs no runtime
translation. Its historical comments remain visible to the debt inventory.

L3.2 migrated 95 whole legacy messages, including quest/boss notifications, dialogue,
NPC greetings and crime notices. Map/travel/bounty displays translate recognized saved
place labels, including coordinate and Outskirts suffixes. Earned consort titles also
translate at display time. Registration keys, stored names, title ownership, selection
and coordinates remain canonical; neither helper rewrites saved state. Generic prose,
unlisted vocabulary and case variants still require a final catalog review. L3.3 translates logbook narration and bestiary labels, thirteen expression-system
messages and the four generated Oracle expression names. `recordKill` continues to
store the existing cleaned creature keys; display labels use the mob catalog.
Unknown creature/deed keys remain readable fallbacks and need the final catalog audit.
Expression IDs, unlocks, animations, rating axes and native-persona bindings are stable.

The HUD runtime had no generator in the inherited repository. Its owner is now
`scripts/gen_hud_runtime.py`, with source in `scripts/templates/hud_runtime.js`.
Edit that template and regenerate; never hand-edit fable_hud.js. Both live and legacy
HUD navigation display recognized saved-site names through placeName. Font/UI pixel
generators contain no additional player-facing prose and need no naming edits.
These unfinished areas and comments remain in [BRANDING_DEBT.md](BRANDING_DEBT.md).
All original packaging remains blocked; previews are development trees only.

## Appearance API correction

The existing Appearance page used UI 1.x positional control arguments despite the
manifest declaring `@minecraft/server-ui` 2.0.0. The 2.0 API takes options objects for
dropdown, toggle and slider controls. The migrated page now uses those objects, and
setting aura density to zero remains zero after saving. L3.2 also corrected both legacy shop quantity sliders without changing purchase/sale
amounts or inventory IDs.

Sources checked 2026-09-12: [Microsoft UI 2.0 changelog](https://learn.microsoft.com/en-us/minecraft/creator/scriptapi/minecraft/server-ui/changelog?view=minecraft-bedrock-stable),
[dropdown options](https://learn.microsoft.com/en-us/minecraft/creator/scriptapi/minecraft/server-ui/modalformdatadropdownoptions?view=minecraft-bedrock-stable),
[slider options](https://learn.microsoft.com/en-us/minecraft/creator/scriptapi/minecraft/server-ui/modalformdataslideroptions?view=minecraft-bedrock-stable),
[toggle options](https://learn.microsoft.com/en-us/minecraft/creator/scriptapi/minecraft/server-ui/modalformdatatoggleoptions?view=minecraft-bedrock-stable).
The current class page's example still shows older argument forms; use the versioned
changelog and current signatures, not that stale example.

## Automated and manual evidence

Twenty-two actual-module boundary tests cover both modes, strict lookup/interpolation,
canonical names, all eight legacy routes, quick-slot mutation/back navigation,
Appearance state, travel/save identity, title ownership, bounty summaries, NPC dialogue
shop quantity callbacks, logbook counter compatibility and the complete 23-line HUD
payload arrangement. The 95 faithful message templates were compared to their
pre-migration AST values and match exactly. The UI mock rejects obsolete positional options. Before-fix failure
and after-fix results are under `screenshots/validation/L3.1/` alongside the full suite.
Mocks do not prove Bedrock rendering, layout or asynchronous engine behavior.

For each mode in a development installation, record Bedrock version, screenshots and
observations. Original mode must use the isolated preview pack directories, never a
public release archive.

- [ ] Open the Hero Menu with the Seal; verify flourish, readable text and eleven buttons.
- [ ] Check good/neutral/evil titles and displayed mana values.
- [ ] Visit every category and return to the same hub without duplicate flourishes.
- [ ] Bind, move and remove each quick slot; cast the resulting active power.
- [ ] Change Appearance detail, both toggles and aura values 0/1/2; reopen and verify.
- [ ] Check item/entity names, long labels and color codes in inventory and weapon menus.
- [ ] Check map heading/recall and status clock/marital labels in both modes.
- [ ] Check NPC dialogue, rumors, quest completion and boss-choice notifications in both modes.
- [ ] Buy/sell chosen quantities; verify default/max values, price and inventory changes.
- [ ] Exercise crime/payment/expiry in Guild and town jurisdictions; verify translated notices.
- [ ] Reopen existing travel sites and consort titles; retain saved identity and selected markers.
- [ ] Record unknown saved-site spellings, case variants and logbook labels as naming debt.
- [ ] Verify existing worlds retain inventory, ownership, slot state and discovered sites.

Additional L3.3 manual checks (all unrun):

- [ ] Existing kill counters/discovery entries survive; bestiary names follow the mode.
- [ ] All four Oracle gestures show matching registry/dialogue names and still unlock.
- [ ] Native expression bindings and command descriptions work in both modes.
- [ ] HUD navigation translates old site labels without shifting eye/clock/map/gold/wanted clips.
- [ ] Inspect long original names at supported UI scales; keep existing radar/hunger/nav layout defects separate.

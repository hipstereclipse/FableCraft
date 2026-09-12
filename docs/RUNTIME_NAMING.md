# Runtime naming progress

L3.1 code is implemented; required in-world checks remain unrun.

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

Quest/town/shop/crime prose, persisted travel-site labels and unrelated legacy menus
still require L3.2. Logbook content and other Will/emote/HUD prose require L3.3.
These unfinished areas and comments remain in [BRANDING_DEBT.md](BRANDING_DEBT.md).
All original packaging remains blocked; previews are development trees only.

## Appearance API correction

The existing Appearance page used UI 1.x positional control arguments despite the
manifest declaring `@minecraft/server-ui` 2.0.0. The 2.0 API takes options objects for
dropdown, toggle and slider controls. The migrated page now uses those objects, and
setting aura density to zero remains zero after saving. Two legacy shop sliders still
need the same API correction in L3.2.

Sources checked 2026-09-12: [Microsoft UI 2.0 changelog](https://learn.microsoft.com/en-us/minecraft/creator/scriptapi/minecraft/server-ui/changelog?view=minecraft-bedrock-stable),
[dropdown options](https://learn.microsoft.com/en-us/minecraft/creator/scriptapi/minecraft/server-ui/modalformdatadropdownoptions?view=minecraft-bedrock-stable),
[slider options](https://learn.microsoft.com/en-us/minecraft/creator/scriptapi/minecraft/server-ui/modalformdataslideroptions?view=minecraft-bedrock-stable),
[toggle options](https://learn.microsoft.com/en-us/minecraft/creator/scriptapi/minecraft/server-ui/modalformdatatoggleoptions?view=minecraft-bedrock-stable).
The current class page's example still shows older argument forms; use the versioned
changelog and current signatures, not that stale example.

## Automated and manual evidence

Eight actual-module boundary tests cover both modes, strict lookup/interpolation,
canonical names, all eight legacy routes, quick-slot mutation/back navigation and
Appearance state. The UI mock rejects obsolete positional options. Before-fix failure
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
- [ ] Record remaining saved-site, quest and logbook faithful labels as L3.2/L3.3 debt.
- [ ] Verify existing worlds retain inventory, ownership, slot state and discovered sites.

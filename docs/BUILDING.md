# Building from source

Nothing in the packs is authored by hand. Textures, models, structures, sounds,
behaviour files, UI, runtime strings and the HUD are all emitted by generators
in `scripts/`, and the packs under `packs/` are their **output**, checked in for
diffability.

If you edit a generated file directly, the next build overwrites it. Edit the
generator.

---

## Requirements

```
Python 3.14    Pillow 12.3.0, numpy 2.5.2   (requirements-dev.txt)
Node 26        eslint 10                     (package.json, dev only)
```

```bash
python -m pip install -r requirements-dev.txt
npm ci
```

Node is only needed for linting and for the JavaScript runtime tests. You can
build the add-on with Python alone.

---

## Building

```bash
python scripts/build_addon.py
```

This regenerates, validates and packages. It prints the output path, which
looks like `tmp/builds/faithful-<run>/dist/Fablecraft_Reforged.mcaddon`, with
`Fablecraft_BP.mcpack` and `Fablecraft_RP.mcpack` beside it.

| Flag | Effect |
|---|---|
| *(none)* | Stage, validate and package locally under `tmp/builds/` |
| `--full` | Regenerate the live faithful assets first |
| `--branding original --preview` | Isolated original-name text preview; writes no archives |

Builds land in `tmp/`, which is gitignored. The archives tracked in `dist/`
predate the current release policy — see [../LEGAL.md](../LEGAL.md) — and are
not approved releases.

---

## The generators

`build_addon.py` runs these in order. Each one owns its output; if you want to
change something, find the generator that owns it.

| Generator | Owns |
|---|---|
| `gen_item_textures.py` | Every item icon |
| `gen_ui.py` | The parchment UI skin, buttons, scrollbars, Will Focus icon |
| `gen_hud_font.py` | The private-use HUD glyph sheet (`font/glyph_E9.png`) |
| `gen_entity_textures.py` | Every creature and NPC texture |
| `gen_behavior.py` | Behaviour-pack entity, item and recipe JSON |
| `fc_strings.py` | The runtime string table, in both branding modes |
| `gen_hud_runtime.py` | `fable_hud.js`, from `templates/hud_runtime.js` |
| `gen_resources.py` | Resource-pack geometry, render controllers, animations |
| `gen_wd.py` | Will & Destiny modules and sigils |
| `gen_emotes.py` | The 31 expressions and their animation data |
| `gen_structures.py` | All 36 `.mcstructure` files |
| `gen_sounds.py` | 535 WAVs across 262 sound definitions, synthesized |

Supporting modules: `fc_data.py` (the item/weapon/armour tables), `fc_mobs.py`
(the creature roster and model builder), `fc_lib.py` (paths, NBT writing,
deterministic RNG), `door_realms.py` (the two Demon Door reward worlds).

Everything is seeded deterministically, so the same source produces the same
bytes on every machine. That is what makes the pack diffs meaningful.

---

## Validating

```bash
python scripts/validate.py
```

**56 gates**, and any failure fails the run. They cover the build itself,
eslint, the expression and animation audits, the HUD static audit, and
regression tests for every Guild room, both Demon Door realms, structure
placement, Cullis geometry and detectors, the alignment authority, the branding
scanner and the conformance scoreboard.

Output and exit status for every command are written to `tmp/validation/` (use
`--output <dir>` to change that). This is also the CI entry point, so what runs
locally is what runs on GitHub.

JavaScript runtime tests alone:

```bash
npm test          # spells, entity-scan fallbacks, runtime strings
npm run lint      # eslint over packs/Fablecraft_BP/scripts
```

More detail in [CI.md](CI.md) and [AUDIT_TOOLING.md](AUDIT_TOOLING.md).

---

## Regenerating the imagery

Three separate image sets, three separate generators. Read
[MEDIA.md](MEDIA.md) for what each set is for and how honest each one is about
being a render.

```bash
python scripts/gen_screenshots.py           # catalogue: mobs, items, structures, gallery sheets
python scripts/gen_doc_screenshots.py       # showcase plates for the docs
python scripts/gen_ingame_screenshots.py    # staged player's-eye captures
python scripts/preview_hud_faithful.py      # HUD slice preview through the live clip offsets
```

`gen_ingame_screenshots.py` takes shot ids, so you can re-render one frame
without redoing the set:

```bash
python scripts/gen_ingame_screenshots.py 03_map_room 19_hero_menu
```

---

## Branding modes

The project ships two text modes. **Faithful** mode uses the original Fable
names and is for local development only. **Original** mode is the one every
distributed build must use, and it has to pass the package scan in
`scripts/scan_branding.py`.

The naming layer is not finished, which is why distribution is blocked. See
[BRANDING.md](BRANDING.md) and [BRANDING_DEBT.md](BRANDING_DEBT.md).

---

## Repository layout

```
packs/Fablecraft_BP/     behaviour pack — generated output
packs/Fablecraft_RP/     resource pack — generated output
scripts/                 every generator, audit and test
scripts/tests/           Python and Node regression tests
scripts/templates/       source templates for generated runtime JS
docs/                    this documentation, plus the conformance ledger
screenshots/             the three image sets, plus validation evidence
tmp/                     build and validation output (gitignored)
dist/                    historical archives, not releases
```

---

## Contributing

1. Change the generator, never the generated file.
2. Run `python scripts/validate.py` and get all 56 gates green.
3. If you touched geometry, regenerate the affected screenshots so the docs
   match what the build produces.
4. Keep provenance clean: nothing extracted from any Fable game, and — for
   anything that gets committed — nothing extracted from Minecraft either. See
   [../LEGAL.md](../LEGAL.md).

The TLC conformance work has its own queue, evidence policy and checkpoint
discipline; start at [CONFORMANCE_CHECKLIST.md](CONFORMANCE_CHECKLIST.md) and
[GUILD_DEMON_PRIORITIES.md](GUILD_DEMON_PRIORITIES.md) before touching the
Guild or the Demon Doors.

# Naming migration debt (after L3.1 code migration)

Generated from the original-mode staging preview. Known case-sensitive display names
only; comments count. IDs, filenames, escaped literals, case variants, nested archives
and unlisted names still require L4 scanning. This inventory cannot authorize a release.

| File | Matching lines | Known faithful spellings |
| --- | ---: | --- |
| `packs/Fablecraft_BP/config/fable_emotes.json` | 4 | Avisto, Calran, Moryk, Yeron |
| `packs/Fablecraft_BP/scripts/fable_emote_registry.js` | 4 | Avisto, Calran, Moryk, Yeron |
| `packs/Fablecraft_BP/scripts/fable_emotes.js` | 10 | Avisto, Calran, Fable, FableCraft, Fablecraft, Moryk, Yeron |
| `packs/Fablecraft_BP/scripts/fable_hud.js` | 1 | Fable |
| `packs/Fablecraft_BP/scripts/main.js` | 135 | Albion, Avo, Avo's Tear, Balverine, Bowerstone, Briar Rose, Chamber of Fate, Cullis, Cullis Gate, Cullis Gates, Darkwood, Demon Door, Demon Doors, Dragon of Blades, Fable, Fable: The Lost Chapters, Fablecraft, Fablecraft: Reforged, Fisher Creek, Guild Seal, Guildmaster, Heroes' Guild, Hobbes, Hook Coast, Jack of Blades, Knothole Glade, Lady Grey, Lookout Point, Maze, Necropolis, Oakvale, Orchard Farm, Rose Cottage, Snowspire, Sword of Aeons, Theresa, Twinblade, Windmill Hill |
| `packs/Fablecraft_BP/scripts/wd/herobook.js` | 1 | Fable |
| `packs/Fablecraft_BP/scripts/wd/logbook.js` | 2 | Albion, Avo |
| `packs/Fablecraft_BP/scripts/wd/menu_bridge.js` | 1 | Albion, Cullis |
| `packs/Fablecraft_BP/scripts/wd/spells/berserk.js` | 1 | Skorm |
| `packs/Fablecraft_BP/scripts/wd/spells/registry.js` | 1 | Fable |

Reproduce: `python scripts/build_addon.py --branding original --preview`; inspect
`branding-debt.json` in the printed staging directory. L3.1 owns menus, L3.2 owns
quests/towns/shops/crime, and L3.3 owns remaining Will/emote/HUD display text.
The manifest `generated_with` key and other internal lowercase names intentionally
remain unchanged until the L4 compatibility/remapping design.

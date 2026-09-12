# Naming migration debt (after L3.3 code migration)

Generated from the original-mode staging preview. Known case-sensitive display names
only; comments count. IDs, filenames, escaped literals, case variants, nested archives
and unlisted names still require L4 scanning. This inventory cannot authorize a release.

| File | Matching lines | Known faithful spellings |
| --- | ---: | --- |
| `packs/Fablecraft_BP/scripts/fc_strings.js` | 19 | Bowerstone, Bowerstone Market, Chamber of Fate, Consort of Bowerstone, Darkwood Trading Camp, Fisher Creek, Heroes' Guild, Hook Coast, Knothole Glade, Lookout Point, Necropolis, Oakvale, Oakvale Quay, Orchard Farm, Rose Cottage, Snowspire, Snowspire Oracle, Twinblade's Bandits, Windmill Hill |
| `packs/Fablecraft_BP/scripts/main.js` | 73 | Albion, Bowerstone, Bowerstone Market, Briar Rose, Chamber of Fate, Consort of Bowerstone, Cullis, Cullis Gate, Darkwood Trading Camp, Demon Door, Demon Doors, Fable, Fable: The Lost Chapters, Fablecraft, Fablecraft: Reforged, Fisher Creek, Guild Seal, Guildmaster, Heroes' Guild, Hook Coast, Jack of Blades, Knothole Glade, Lookout Point, Maze, Necropolis, Oakvale, Oakvale Quay, Orchard Farm, Rose Cottage, Snowspire, Snowspire Oracle, Sword of Aeons, Theresa, Twinblade's Bandits, Windmill Hill |
| `packs/Fablecraft_BP/scripts/wd/herobook.js` | 1 | Fable |
| `packs/Fablecraft_BP/scripts/wd/menu_bridge.js` | 1 | Albion, Cullis |
| `packs/Fablecraft_BP/scripts/wd/spells/berserk.js` | 1 | Skorm |
| `packs/Fablecraft_BP/scripts/wd/spells/registry.js` | 1 | Fable |

Reproduce: `python scripts/build_addon.py --branding original --preview`; inspect
`branding-debt.json` in the printed staging directory. L3.1 owns menus, L3.2 owns
quests/towns/shops/crime, and L3.3 owns remaining Will/emote/HUD display text.
The manifest `generated_with` key and other internal lowercase names intentionally
remain unchanged until the L4 compatibility/remapping design.

L3.2 strips color codes before detecting display names, correcting earlier undercounts.
The generated runtime module now deliberately exposes legacy place/title lookup keys: these
are compatibility debt for L4, not exemptions. main.js retains canonical registration,
jurisdiction and title values so existing saved records remain stable. Its remaining
known matches include those values and historical comments. Unlisted vocabulary,
case variants (for example Guild seals), and unknown deed labels still need review. HUD saved-place names now pass through
the same display helper; its 23-line payload contract remains unchanged.

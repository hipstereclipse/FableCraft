# ⚔ Fablecraft: Reforged

**Transform Minecraft Bedrock into Albion.** A complete recreation of *Fable: The Lost Chapters* as a single `.mcaddon` — Hero XP paths with coloured experience orbs, a living morality system, faction reputation, Will powers, Cullis Gate fast travel, a full mining-and-smithing economy, Demon Doors that talk back, legendary weapons, armour sets, quest chains, expressive townsfolk who walk, emote and react to you, Twinblade's war-camps, and Jack of Blades waiting at the end of it all.

> Every texture, model, structure and sound in this repository is **procedurally generated from code** — Python paints the pixels, builds the geometry, synthesizes the audio and renders the 3D showcase scenes below. The captures tagged *in-game* are the real thing, running live in Minecraft Bedrock.

![Bestiary of Albion](screenshots/gallery/bestiary.png)

| | | | | | | | | | |
|---|---|---|---|---|---|---|---|---|---|
| **51** creatures & NPCs | **193** items | **130** recipes | **17** Will powers | **15** quests | **31** emotes | **8** Demon Doors | **9** structures | **5** factions | **262** sounds |

> **Current release: v2.4.0** — built for Minecraft Bedrock **1.21.100+**.

---

## ✨ What's New in 2.4.0

- **The Lost Chapters-style interface.** The Guild Seal now opens a nine-section storybook menu matching the original PC structure: **Items, Weapons, Magic, Clothing, Expressions, Quests, Stats, Logbook, and Map**. Dark leather panels, warm parchment controls, gilt trim, and a dedicated Will Focus icon carry the original game's illuminated-manuscript direction into Bedrock.
- **Every major system has a UI path.** Equip weapons and full clothing suits, use inventory provisions and experience orbs, perform all learned expressions, inspect active and completed quests, manage legacy Will tomes and the modular Will Focus, review factions and bounties, train, choose titles, and travel through the Cullis lattice without command-only gaps.
- **Expanded trading and crime feedback.** Shops now support buy-one, buy-maximum, sell-one, sell-maximum, and exact quantity selection. Active warrants display an on-screen crime meter with the settlement, fine, response tier, and expiry time.
- **Faithful TLC navigation.** The Map remains a Cullis destination list with Guild recall; it intentionally does not add Fable II's golden breadcrumb trail.
- **Living NPCs — full body animation.** Every villager, guard, Guild member and named character now walks with alternating limbs and a weight-shifted bob, breathes on idle, looks around, gestures while talking and follows through on attacks — no more sliding statues. Identical townsfolk are phase-offset so a crowd never moves in lockstep.
- **31 Fable expressions & emotes.** The full *Fable: The Lost Chapters* expression set — Flirt, Blood Lust Roar, Belch, Laugh, Clap, Apologise, Dance and more — drives both your hero and the NPCs around you. Trigger them with `/fable:emote <name>`, watch NPCs react to your antics, and bind your native Persona emotes to Fable expressions. See [FABLE_EMOTE_VALIDATION.md](FABLE_EMOTE_VALIDATION.md).
- **Settlement bounty & jail.** Crimes against townsfolk and guards now raise a per-settlement bounty that scales the guard response from a pair of standard watchmen up to four elite enforcers, with warrants, arrest choices (pay / jail / resist) and a jail that strips your gear. Full spec in [BOUNTY_SYSTEM.md](BOUNTY_SYSTEM.md).
- **Will & Destiny (Phase 1 preview).** A new modular Will engine — a rebuilt four-level Fireball with mana, an evil aura and per-player alignment tiers — ships alongside the existing systems as an opt-in preview. Notes, schema and test plan in [WILL_AND_DESTINY_PHASE1.md](WILL_AND_DESTINY_PHASE1.md).

![Fable Expressions](screenshots/gallery/expressions.png)

---

## 📥 Installing

1. Grab **`dist/Fablecraft_Reforged.mcaddon`**.
2. Double-click it (or open it with Minecraft). Both packs import automatically.
3. Create a new world → **Add** the Behavior Pack *Fablecraft: Reforged [Behavior]* (the Resource Pack joins automatically as a dependency).
4. Under world settings, ensure **Holiday Creator Features / Beta APIs** toggles required by your Minecraft version are enabled for scripting.
5. Spawn in. You wake **inside the Heroes' Guild** kitted out in a full apprentice outfit, a Stick, your Guild Seal, a Quest Card and an Apple Pie — the Guildmaster is expecting you.

> Prefer separate packs? `dist/Fablecraft_BP.mcpack` and `dist/Fablecraft_RP.mcpack` install individually.

**Requirements:** Minecraft Bedrock **1.21.100+** (Windows / mobile / console via realm host), with the Script API enabled (`@minecraft/server` 2.1.0, `@minecraft/server-ui` 2.0.0).

![Quick Start Loadout](screenshots/docs/20_starter_inventory.png)

---

## 🧙 Hero Systems

![Hero at Heroes' Guild](screenshots/docs/01_hero_guild_gate.png)

### Experience & Training

Kills grant **General XP** plus **Strength** (melee) or **Skill** (ranged) XP; casting grants **Will XP**. Your **Combat Multiplier** climbs with every unanswered hit and multiplies XP gains — take damage and it shatters, exactly as the Guild taught you. Slain foes also shed **experience orbs** in Fable's colours — green (General), red (Strength), yellow (Skill) and blue (Will) — crush them to absorb bonus experience. Bosses burst with them.

Training happens **at the Guild**: the **Training Grounds** fill the east yard (archery range, sparring ring, Will circle) and the Map Room holds the Guildmaster. Spend XP on **Physique, Health, Toughness, Speed, Guile, Accuracy** and **Magic Power**.

The **Hero Menu** (use your Guild Seal) is Albion's storybook interface. Its nine sections follow *The Lost Chapters*: **Items, Weapons, Magic, Clothing, Expressions, Quests, Stats, Logbook, and Map**. It provides an in-game route to every major scripted system, while the normal play view remains sparse and combat feedback stays in short action-bar notices.

- **Items** uses provisions and experience orbs, opens Quest Cards, and routes augmentation stones into the forge.
- **Weapons** inspects damage and augment slots, then equips any carried Fable weapon.
- **Magic** upgrades learned powers, manages the 7–9 quick-cast bar, and opens Will Focus attunement.
- **Clothing** equips individual pieces or complete four-piece suits.
- **Expressions** groups all 31 social actions by category and runs unlocked expressions directly.
- **Quests** separates the active Quest Card, available work, and completed history.
- **Stats / Logbook** hold alignment, personality, XP, training, titles, factions, bounties, and system help.
- **Map** lists discovered Cullis destinations and Guild recall. TLC has no golden breadcrumb trail.

![Hero Menu](screenshots/docs/15_hero_menu_xp_morality.png)

### Morality, Factions & Renown

Slay monsters, escort traders and spare the innocent to shine; murder villagers, drain life and eat **Crunchy Chicks** to rot. Morality runs **-1000 … +1000**, gates spells (Divine Fury vs. Infernal Wrath), changes NPC dialogue, alters Demon Door verdicts, and wreaths you in golden light or black smoke. At extreme alignment, evil Heroes turn red-eyed and horned while good Heroes gain a radiant halo. Titles run from **Avatar of Skorm** to **Paragon**.

| Fully good — the radiant halo | Fully evil — Avatar of Skorm |
|:---:|:---:|
| ![Good Hero with halo](screenshots/ingame/hero_good_paladin_halo.jpg) | ![Evil Hero in a pool of blood](screenshots/ingame/hero_evil_avatar_of_skorm.jpg) |

> **In-game:** the same Hero at the two ends of the morality scale. Push toward good and a divine halo settles over your head; sink into evil and your eyes burn red, your skin corrupts and blood pools at your feet — applied as live overlays without replacing your skin.

Five factions keep a ledger on you: **the Guild, Bowerstone, Oakvale, Snowspire** and **Twinblade's Bandits**. Clearing bandit camps raises your standing with the towns; cutting down guards or villagers wrecks it. Reputation bends shop prices by up to 20% either way — and a town that marks you **hostile** will have its guards attack on sight. Fame from Renown buys better quests and villager adoration… and night-time assassin ambushes. Nothing in Albion is free.

### Crime, Bounties & Jail

Spill blood in a settlement and the law remembers. Killing civilians or guards raises a **bounty tied to that exact town**, and the guard response scales with it — a couple of standard watchmen for a petty crime, a squad of tougher veterans as it climbs, up to **four elite enforcers** for a true rampage. Guards approach before they strike; close the distance and a **warrant** offers three choices: **pay the bounty, go to jail, or resist arrest**. Jail clears the warrant but strips your carried inventory and armour (your Guild Seal, Will Focus, spell tomes and progression are spared) and turns you loose outside the walls. Leave town and the heat cools on a wall-clock timer; return too soon and the guards are still hunting. Full mechanics in [BOUNTY_SYSTEM.md](BOUNTY_SYSTEM.md).

### The Cullis Gate

The west yard of the Guild holds a humming **Cullis Gate** — Fable's teleport network. Step onto the ring and **sneak** to open the travel menu. Every **Focus Site** you discover in the wild joins the lattice, letting you blink across Albion.

![Cullis Gate Fast Travel](screenshots/docs/16_cullis_gate_travel_ui.png)

### The Final Choice

Defeat Jack of Blades and his dragon form, and the **Sword of Aeons** is yours. Keep it and rule through fear — or cast it away and receive **Avo's Tear**. The classic ending, your call.

---

## ⛏ Forge & Progression

Everything you can wear or swing is **craftable**, with a smithing chain that makes Albion-sense:

| Material | How to get it |
|---|---|
| **Iron** | Vanilla iron — the apprentice's metal |
| **Steel Ingot** | Fold 2 iron ingots over coal at a crafting table |
| **Obsidian Ingot** | Smelt a block of obsidian in any furnace — volcanic glass drawn molten |
| **Will Shard** | Mine glowing **azurite ore**, seeded through the deep underground (y 4–54) |
| **Master Ingot** | Quench a steel ingot in two Will Shards — steel remembers the magic |

Weapons follow classic patterns (longswords, katanas, cleavers, axes, maces, pickhammers, greatweapons), bows are bound from planks, string and a tier ingot, and all 13 armour sets craft from themed materials — chainmail from chains, guard uniforms from steel and town-colour wool, the Archon's set from Master ingots and gold.

![Item Compendium](screenshots/docs/04_inventory_weapon_armor.png)

### Crafting in Action

130 recipes cover every outfit, weapon and tool — fold steel from iron and coal, smelt obsidian ingots from obsidian, quench Master ingots in Will Shards mined from azurite ore.

![Crafting Progression](screenshots/docs/06_master_katana_recipe.png)
![The Forge of Albion](screenshots/gallery/forge.png)
![Forge Core Smithing Chain](screenshots/gallery/forge_smithing_core.png)
![Forge Weapon Progression](screenshots/gallery/forge_weapon_progression.png)
![Forge Armour and Augments](screenshots/gallery/forge_armor_augments.png)
![Full Weapon Tier Progression](screenshots/gallery/progression_weapons.png)
![Full Armour Set Progression](screenshots/gallery/progression_armor.png)
![Forge Weapons Recipes](screenshots/gallery/forge_weapons.png)
![Forge Armour Recipes](screenshots/gallery/forge_armor.png)
![Forge Components and Augments Recipes](screenshots/gallery/forge_systems.png)

All 130 recipe diagrams live in [screenshots/recipes](screenshots/recipes).

### Legendary Arsenal & Augments

Sword of Aeons · Avo's Tear · The Harbinger · Solus Greatsword · The Bereaver · Avenger · Katana Hiryu · Orkon's Club · Dollmaster's Mace · Wellow's Pickhammer · Arken's Crossbow · Skorm's Bow · Scimitar · and the humble **Stick**.

Weapons carry **augment slots** (Steel 1 / Obsidian 2 / Master 3). Bind **Sharpening, Piercing, Health, Mana, Experience, Lightning, Flame** or **Silver** augmentations — forged by binding monster trophies to Will Shards: a Balverine fang and silver-bright iron make a Silver augmentation; a Troll heart makes Health; a Banshee's tear crackles into Lightning. Silver burns Balverines and the undead, exactly as the bestiaries warn.

Using an augmentation stone opens the **Augmentation Forge** — pick which weapon in your pack receives the power from a list of every eligible blade and its filled/empty slots. Binding (or stripping, via the Augment Remover) wreathes the weapon in a burst of totem light and power-coloured sparks with a ringing anvil strike, and augmented weapons carry a faint, drifting aura of their bound colours while held.

![Archon Endgame Kit](screenshots/docs/05_archon_with_aeons.png)
![Weapon Augmentation](screenshots/docs/18_anvil_augments.png)
![Reliquary](screenshots/gallery/reliquary.png)

### Armour Sets

From apprentice hood to Archon plate, the addon includes 13 armour sets across 58 pieces, all attached as you equip them.

![Armour Sets](screenshots/docs/17_armor_sets.png)
![Armoury](screenshots/gallery/armoury.png)

---

## 🚪 Demon Doors & Structures

Eight ancient doors are scattered across the world, each a living stone face carved into a **hillside crag** that rises out of the landscape — the placement engine even hunts for naturally sloping ground so every door looks like it has been there for a thousand years. Speak to them. Flatter them. Feed them. One wants five apple pies. One wants to see a Combat Multiplier of 14 mid-battle. One asks a riddle and laughs at you for a century if you miss it. Behind each: legendary weapons, silver keys, elixirs.

![Demon Door Encounter](screenshots/docs/11_demon_door_closeup.png)

Beyond the doors, **9 structures** dot Albion — the walled Heroes' Guild (Cullis Gate + training grounds), the Arena, Temple of Avo, Chapel of Skorm, Twinblade's palisaded war-camp, Lychfield graveyard, focus sites, silver-chest ruins and Demon Door crags — all stocked with **lootable chests** and blended into the terrain.

### The Heroes' Guild

The Guild is a single connected campus on a curved river. You wake in the domed **Map Room** — the Cullis Gate and Skill Shrine glow in its western nooks — and a single open-arched grand stair climbs to the upper gallery without blocking the four arched doorways that join the Library, Dining Hall and Store. The **Dining Hall** seats two long banquet tables down its length; a grand riverside **stone staircase** with railings and a landing descends from the upper terrace to a gravel **promenade that wraps the whole complex**, knitting every bridge and the **Four Graves** memorial garden (laid out as a `+` around an eternal flame). **Maze's Tower** is now three floors: a wall-hugging spiral past book-lined walls, candles, lecterns and framed art up to Maze's study, with suits of armour standing guard at its two entrances and a north archway opening onto monuments and flower beds. Across the river the **Archery Range** (targets now correctly outside the kitchen wall), **Dueling Ring** and a richly-stocked **Kitchen / Dormitory** sit beside the water. Outside the west gate a **Trader** works a covered cart (random wares *and* vanity titles), and a red carpet leads up the **Boasting Platform** — step onto the stage and, depending on your Renown, the Guild's folk gather to watch you declare your title (an unknown draws a handful; the truly renowned draw the whole campus, cheering). Far beneath, a fixed spiral stair winds down to the **Chamber of Fate** and its flat warded Cullis dais.

![Temple of Avo](screenshots/docs/13_temple_avo_donation.png)
![Places of Power](screenshots/gallery/places.png)

---

## 👹 Bestiary & Encounters

**A deep bestiary** of custom creatures: Balverines (standard/White/Frost), Trolls (Earth/Ice/Rock Giant), Hobbes, Bandits and **Twinblade the Bandit King**, Hollow Men in three states of decay (shambler, soldier, knight), Wasps & Wasp Queen, Wraiths, Banshees, Summoners, Minions, Arachanox, Assassins, Nymphs and summoned allies. The full custom roster — creatures, bosses, allies and talking NPCs — runs to **51 entities**, each with idle, walk and combat animation.

![Balverine Night Hunt](screenshots/docs/02_balverine_night_fight.png)
![Creature Roster](screenshots/docs/03_roster_group_shot.png)

### Will Powers in the Field

**17 Will powers** — Fireball, Enflame, Lightning, Slow Time, Assassin Rush, Summon, Berserk, Divine Fury, Infernal Wrath and more — each with 4 upgrade levels.

![Will Power - Fireball](screenshots/docs/07_fireball_vs_hobbes.png)
![Will Power - Slow Time](screenshots/docs/08_slow_time_bandit_camp.png)

> **Preview — Will & Destiny (Phase 1).** A from-scratch modular Will engine is shipping alongside the classic spell tomes as an opt-in preview. It rebuilds **Fireball** as a scripted projectile with four damage/mana/cooldown tiers, adds a regenerating **mana** pool, morality auras, and seven-step **alignment tiers** persisted per-player for multiplayer. Extreme evil grows visible horns; extreme good adds a divine glow and halo without replacing the player's skin or helmet. It's driven by a dedicated **Will Focus** item (use to cast, sneak-use to attune and upgrade) and mirrors your existing progression behind a bridge flag, so current worlds keep their stats. The remaining physique and spell morphs are Phase 2/3 work — full schema, controls and test plan in [WILL_AND_DESTINY_PHASE1.md](WILL_AND_DESTINY_PHASE1.md).

### Boss Encounters

Twinblade anchors the bandit-camp quest line as a dedicated boss encounter, backed by raiders, archers, camp loot and a palisaded arena built for the fight. Lychfield's undead appear as three readable variants — Hollow Men, Hollow Soldiers and Hollow Knights — so the threat level is clear before you get close.

![Twinblade Boss Fight](screenshots/docs/10_twinblade_boss_fight.png)
![Boss Encounters](screenshots/gallery/bosses.png)
![Bosses Panel](screenshots/gallery/rogues_bosses.png)
![Hostile Creature Roster](screenshots/gallery/mobs_hostile.png)
![Undead and Beasts Panel](screenshots/gallery/rogues_undead_beasts.png)
![Raiders and Casters Panel](screenshots/gallery/rogues_raiders_casters.png)

Full bestiary renders live in [screenshots/mobs](screenshots/mobs), with a measured appearance report in [screenshots/AUDIT.md](screenshots/AUDIT.md) — every asset is auto-graded on silhouette, palette richness, contrast and brightness.

---

## 👥 NPCs, Quests & Factions

Albion is populated with townsfolk, guild staff, guards, traders, quest-givers and summonable allies — distinct archetypes for guards, villagers, blacksmiths, barkeeps, traders, the Guildmaster, Maze, Theresa, Lady Grey, the Oracle and Briar Rose, each with dialogue and reactions tied to morality and faction reputation. Briar Rose lingers near the wilds with cryptic hints about the Demon Doors and the trials they demand.

![Heroes' Guild — Walled Grounds](screenshots/docs/12_guild_wide_lake_view.png)

### Living, Emoting Townsfolk

Albion's people **move**. Every NPC now walks with alternating arms and legs over a foot-planted body bob, breathes and shifts weight on idle, glances around, gestures while talking and follows through on attacks — and identical villagers carry a per-character phase offset so a crowd never marches in robotic lockstep. All of it is generated from shared per-archetype animation clips in [scripts/gen_resources.py](scripts/gen_resources.py), so one well-made clip lifts every entity on that body plan.

On top of that sits the **Fable expression system**: all **31 expressions from *The Lost Chapters*** — Flirt, Blood Lust Roar, Belch, Laugh, Clap, Apologise, the dances and the cruder ones — playable on your hero and the NPCs alike. Run `/fable:emote <name>` (or the `/scriptevent fable:emote <name>` form), make NPCs react with `/fable:npc_react`, and the first time you use one of your own Persona emotes it binds to the next unlocked Fable expression. Setup, command list and validation steps live in [FABLE_EMOTE_VALIDATION.md](FABLE_EMOTE_VALIDATION.md).

![Fable Expressions](screenshots/gallery/expressions.png)

**15 quests** make up the full main chain (Wasp Menace → Twinblade → Jack of Blades) plus side quests, bounty jobs and the Silver Key treasure hunt. A **Quest Table** stands at the heart of the Great Hall's nave — interact with its lectern to browse and accept contracts. A guard's greeting — or threat — depends entirely on where you stand with their faction, and townsfolk will comment on your growing Renown as your fame spreads.

![Quest Log](screenshots/docs/09_quest_log_ui.png)
![Faction Reputation](screenshots/docs/14_guard_low_rep_dialogue.png)
![NPCs and Features](screenshots/gallery/npcs_features.png)

The summoned-ally ecosystem (mercenary, summoned hobbe/wasp/balverine) integrates with Will powers, and Demon Door interactions tie directly into quest, loot, and travel systems.

---

## 🎮 How to Play

| Action | How |
|---|---|
| Open the Hero menu | Use the **Guild Seal** |
| Recall to the Guild | **Sneak + use** the Guild Seal |
| Browse the TLC menu sections | Guild Seal → **Items / Weapons / Magic / Clothing / Expressions / Quests / Stats / Logbook / Map** |
| Fast-travel | Stand on a **Cullis Gate** and sneak |
| Take a quest | Use a **Quest Card**, or interact with the **Quest Table** lectern in the Great Hall |
| Cast a Will power | Use its **spell tome** (Maze gifts you two to start) |
| Absorb experience orbs | **Use** a dropped orb — each colour feeds its own discipline |
| Augment a weapon | Use an **augmentation stone** and choose a weapon in the Augmentation Forge |
| Train stats | Hero menu → **Guild Training**, at the Guild's Training Grounds or Map Room |
| Check your standing | Hero menu → **Factions & Standing** |
| Mine Will Shards | Dig for glowing **azurite ore** below y 54 |
| Talk to anyone | Interact with villagers, guards, barkeeps — they remember your reputation |
| Pull a Fable expression | `/fable:emote <name>` (e.g. `flirt`, `laugh`, `blood_lust_roar`) — or use a Persona emote to bind one |
| Make an NPC react | Look at them and run `/fable:npc_react <name>` |
| Pay off a bounty | Let an enforcing guard reach you, then choose **Pay**, **Jail**, or **Resist** on the warrant |
| Court Lady Grey | Complete her invitation… and bring a ring |

---

## 🧭 Roadmap — What's Done & What's Next

Fablecraft is content-complete on its **core systems** and actively growing its **world**. Here's an honest map of where it stands.

**Shipped & playable**

✅ Morality with live visual states (halo / horns) · ✅ XP, training & the Combat Multiplier · ✅ 17 Will powers · ✅ 130-recipe forge & augment system · ✅ 13 armour sets · ✅ legendary arsenal · ✅ 5-faction reputation · ✅ settlement bounty & jail · ✅ Cullis Gate fast travel · ✅ 8 Demon Doors · ✅ 51 entities with full-body animation · ✅ 31 Fable expressions · ✅ romance & marriage · ✅ the two-phase Jack of Blades finale · ✅ 262 synthesized sounds.

**In progress**

- 🏗 **Finishing the locations.** The Heroes' Guild is a complete, hand-built campus; **Bowerstone, Oakvale and Snowspire** so far exist as factions, guards and dialogue rather than fully walkable towns. Next: build the three settlements out as explorable hubs, then flesh out the Arena, Lychfield graveyard, and the interiors of the Temple of Avo and Chapel of Skorm.
- 🧠 **Updating behaviours.** Deeper NPC daily routines (day/night schedules, shop hours, crowd gathering), smarter guard pathing and arrest logic, and continued multiplayer-sync hardening so every per-player system reads correctly in co-op.
- 🔮 **Will & Destiny Phases 2–3.** Migrate the remaining classic spells onto the new modular Will engine and add the outstanding physique/appearance morphs. Current state, schema and test plan: [WILL_AND_DESTINY_PHASE1.md](WILL_AND_DESTINY_PHASE1.md).

**Planned**

- 🎲 **Procedurally generated quests.** A template-driven quest generator (hunt / escort / bounty / fetch / clearance jobs) seeded from your faction standing, morality and Renown, to grow Albion's work beyond the 15 hand-authored main and side quests.
- 🗺 More Demon Doors and Focus Sites, additional boss encounters, and a wider legendary-loot table.
- 🪙 Economy balancing pass across shop prices, quest rewards and reputation gains.

> Want to influence what lands next? Open an issue, or back the project below — see something off in-game, file it with a screenshot.

---

## 🛠 Building From Source

Everything regenerates deterministically from the Python pipeline:

```powershell
python -m venv .venv
.venv/Scripts/pip install pillow
.venv/Scripts/python scripts/build_addon.py --full        # regen + validate + package
.venv/Scripts/python scripts/gen_screenshots.py           # re-render the gallery + audit
.venv/Scripts/python scripts/gen_doc_screenshots.py       # build documentation showcase screenshots
.venv/Scripts/python scripts/gen_expression_previews.py   # render the 31 Fable expression cards + sheet
```

| Script | Role |
|---|---|
| [scripts/fc_data.py](scripts/fc_data.py) | Single source of truth: items, spells, quests, doors |
| [scripts/fc_mobs.py](scripts/fc_mobs.py) | Mob roster, body-plan geometry, UV packing |
| [scripts/gen_item_textures.py](scripts/gen_item_textures.py) | Paints all 193 item icons + the azurite ore block |
| [scripts/gen_ui.py](scripts/gen_ui.py) | Paints the parchment/leather form skin and dedicated Will Focus icon |
| [scripts/gen_entity_textures.py](scripts/gen_entity_textures.py) | Paints entity skins + worn-armour layer textures |
| [scripts/gen_behavior.py](scripts/gen_behavior.py) | Emits BP items/entities/loot/spawn rules/**130 recipes**/ore features |
| [scripts/gen_resources.py](scripts/gen_resources.py) | Emits RP geometry, client entities, **NPC animation clips & controllers**, **armour attachables**, lang |
| [scripts/gen_emotes.py](scripts/gen_emotes.py) | Builds the 31-strong Fable expression registry + player/NPC emote animations |
| [scripts/gen_structures.py](scripts/gen_structures.py) | Builds `.mcstructure` NBT for every site |
| [scripts/gen_sounds.py](scripts/gen_sounds.py) | Synthesizes the soundscape from raw math |
| [scripts/gen_screenshots.py](scripts/gen_screenshots.py) | Offline 3D renderer + recipe cards + automated visual audit |
| [scripts/gen_doc_screenshots.py](scripts/gen_doc_screenshots.py) | Composites 3D documentation scenes for README/GitHub showcases |
| [scripts/gen_expression_previews.py](scripts/gen_expression_previews.py) | Renders the Fable expression cards + contact sheet |
| [scripts/verify_emotes.py](scripts/verify_emotes.py) | Static audit of the expression registry (run inside `build_addon.py`) |
| [scripts/build_addon.py](scripts/build_addon.py) | Validation + `.mcaddon` packaging |

Gameplay logic lives in [packs/Fablecraft_BP/scripts/main.js](packs/Fablecraft_BP/scripts/main.js) — XP, morality, multiplier, 17 spells, quests, Demon Door dialogue, faction reputation, the **settlement bounty/jail system**, **Fable expressions & NPC reactions**, Cullis Gate travel, structure loot chests, terrain blending, NPC conversations, shops, world decoration and the two-phase Jack of Blades fight. The opt-in **Will & Destiny** preview lives in its own [packs/Fablecraft_BP/scripts/wd/](packs/Fablecraft_BP/scripts/wd/) module tree.

The generated sound library spans **262 distinct sounds** (535 synthesized `.wav` files in all) — creature voices, NPC speech, item handling, ambience, combat cues and spell/UI sounds; audition the full procedural set in [sound_preview/index.html](sound_preview/index.html).

![Synthesized Sound Design](screenshots/docs/19_sound_files_overview.png)

### Status & Media

![Known Issues and Future Plans](screenshots/docs/21_roadmap_progress.png)
![Gallery and Media](screenshots/docs/22_media_collage.png)

Full generated documentation set and shot manifest: [screenshots/docs/INDEX.md](screenshots/docs/INDEX.md)

---

## ❤️ Support Development

If you are enjoying Fablecraft and want to help keep development moving, please consider supporting the project through Buy Me a Coffee:

[buymeacoffee.com/k8ffh48yvke](https://buymeacoffee.com/k8ffh48yvke)

---

## 📜 Credits & Legal

A fan tribute to *Fable: The Lost Chapters* (Lionhead Studios / Microsoft). All Fable lore, names and concepts belong to Microsoft. Inspired by the original [Fablecraft mod](https://www.planetminecraft.com/mod/fablecraft-mod-216181/) for Minecraft 1.1. Not affiliated with Mojang or Microsoft.

*"Your health is low. Do you have any potions? Or food?"* — you know who

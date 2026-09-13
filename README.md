# Fablecraft: Reforged

**A recreation of *Fable: The Lost Chapters* inside Minecraft Bedrock.**

Hero experience split four ways, a morality scale that changes your face,
five factions that keep score, per-settlement bounties with real arrests,
eighteen Will powers, a smithing chain that ends in Master steel, Demon Doors
that talk back, and Jack of Blades waiting at the end of it.

![The Guild courtyard](screenshots/staged/02_guild_courtyard.png)

| | | | | | | |
|---|---|---|---|---|---|---|
| **51** creatures & NPCs | **195** items | **131** recipes | **18** Will powers | **15** quests | **31** expressions | **8** Demon Doors |
| **36** structures | **13** armour sets | **58** weapons | **8** augmentations | **5** factions | **262** sounds | **56** validation gates |

**Version 2.4.0** · Minecraft Bedrock **1.21.100+** · `@minecraft/server` 2.1.0

> Every texture, model, structure and sound in this repository is generated
> from code. Python paints the pixels, builds the geometry, synthesizes the
> audio and renders the images below. **Those images are renders, not
> captures** — the two exceptions are labelled where they appear, and
> [docs/MEDIA.md](docs/MEDIA.md) explains exactly what is real in each.

---

## Installing

There is no public release yet. [LEGAL.md](LEGAL.md) blocks distribution until
the original-name branding mode and its package scan are finished, so installing
means building:

```bash
python -m pip install -r requirements-dev.txt
python scripts/build_addon.py
```

The build prints the path to `Fablecraft_Reforged.mcaddon`. Open it with
Minecraft, create a world, activate the behaviour pack (the resource pack
follows as a dependency), and enable whatever scripting toggle your version
asks for.

You wake inside the Heroes' Guild in a full apprentice outfit, holding a Stick,
a Guild Seal, a Quest Card and an Apple Pie. The Guildmaster is expecting you.

Full walkthrough: **[docs/GETTING_STARTED.md](docs/GETTING_STARTED.md)**

---

## What you actually do

### Earn four kinds of experience

![The Map Room](screenshots/staged/03_map_room.png)

Kills grant **General** XP plus **Strength** (melee) or **Skill** (ranged);
casting grants **Will**. Enemies shed experience orbs in those four colours.

Your **combat multiplier** climbs with every unanswered hit and multiplies
everything you earn — then shatters the instant you take damage. It is the
reason Fable combat rewards spacing over trading blows.

Spend it at the Guild on seven attributes. Physique visibly changes your
silhouette.

→ [docs/HERO.md](docs/HERO.md)

### Become someone

Morality runs **−1000 to +1000** across seven tiers each way. Donate at an
Altar of Light for +125. Murder a villager for −100. Eat a Crunchy Chick for
−25.

It gates spells, rewrites dialogue, changes how Demon Doors judge you, and at
the extremes it shows: a good Hero gains a radiant halo, an evil one turns
red-eyed and horned with blood pooling underfoot — as live overlays, without
replacing your skin.

| Fully good — the radiant halo | Fully evil — Avatar of Skorm |
|:---:|:---:|
| ![Good Hero with halo](screenshots/ingame/hero_good_paladin_halo.jpg) | ![Evil Hero in a pool of blood](screenshots/ingame/hero_evil_avatar_of_skorm.jpg) |

> **These two are genuine in-game captures.** Every other image in this README
> is a staged render.

### Have a reputation, and a criminal record

![Bowerstone market](screenshots/staged/09_bowerstone_market.png)

Five factions track you from −200 to +200: the Guild, Bowerstone, Oakvale,
Snowspire and Twinblade's Bandits. Revered gets you **20% off**; wary costs you
**15% more**; hostile means traders refuse you and guards attack on sight.

Kill someone in a town and *that town* opens a bounty on you. The response
scales from two watchmen to **four elite enforcers**. Guards approach before
they strike, and the warrant offers three ways out: **pay**, **jail** — which
strips your inventory but spares your Seal, Focus, tomes and progression — or
**resist**.

![A warrant in Bowerstone](screenshots/staged/21_arrest_warrant.png)

→ [docs/HERO.md](docs/HERO.md#crime-bounties-and-jail) · [BOUNTY_SYSTEM.md](BOUNTY_SYSTEM.md)

### Cast

![Fireball over a hobbe pack](screenshots/staged/16_fireball_hobbes.png)

Eighteen Will powers on a regenerating pool, a three-slot quick-cast bar and
hold-to-charge. Six are alignment-locked, three each way: **Heal Life**,
**Summon** and **Divine Fury** for the good; **Drain Life**, **Berserk** and
**Infernal Wrath** for the wicked.

Ghost Sword, Summon and Turncoat put allies on the field that keep fighting.

→ [docs/WILL.md](docs/WILL.md)

### Forge

Iron → **Steel** (2 iron + coal) → **Obsidian** (smelt an obsidian block) →
**Master** (steel + 2 Will Shards, mined as azurite ore between y 4 and 54).

Nine melee shapes across four tiers, bows in four woods, fourteen named
uniques, thirteen four-piece armour sets, and eight augmentation stones — a
Master weapon takes three.

→ [docs/FORGE.md](docs/FORGE.md)

### Explore

![The Temple of Avo](screenshots/staged/10_temple_of_avo.png)

Thirty-six structures. The overworld is diced into 160-block cells, and each
one deterministically rolls at most one landmark suited to its ground type and
grades it into the land. Same seed, same Albion.

Towns, temples, the Arena, Bargate Prison, Lychfield, bandit camps, hobbe
caves, the Archon's monuments.

→ [docs/ALBION.md](docs/ALBION.md)

### Travel

![A Focus Site at night](screenshots/staged/11_cullis_gate.png)

The Cullis lattice is something you assemble. The Guild's Map Room holds one
gate; every **Focus Site** you find in the wild is another. Stand on one and
sneak.

The Map page lists destinations and distances. It deliberately has no golden
breadcrumb trail — that is Fable II, and this is TLC.

![The Cullis travel list](screenshots/staged/20_cullis_travel.png)

---

## The Heroes' Guild

![The Guild grounds at last light](screenshots/staged/01_guild_grounds.png)

122 × 30 × 108 blocks, and the subject of an ongoing reconstruction against
original 2005 reference material.

| | |
|---|---|
| ![The Guild Library](screenshots/staged/04_guild_library.png) | ![The Chamber of Fate](screenshots/staged/05_chamber_of_fate.png) |
| **The Library** — continuous framed cases, a reading desk, supported lamps | **The Chamber of Fate** — pointed bays, inset panels, where Maze reads what is coming |
| ![Maze's study](screenshots/staged/07_maze_study.png) | ![The archery range](screenshots/staged/08_archery_range.png) |
| **Maze's study** — timber cases and the restored red rug at the tower top | **The archery range** — the scenic valley backboard behind the firing lanes |

→ [docs/ALBION.md](docs/ALBION.md#the-heroes-guild)

---

## Demon Doors

![A Demon Door](screenshots/staged/12_demon_door.png)

Eight living stone faces: the Gourmand, the Warrior, the Judge, the Corrupted,
the Hoarder, the Moonlit, the Riddler and the Arboretum Door. All eight talk,
judge you by your morality, gear and deeds, and refuse you in character.

**Two currently open into reward worlds you can walk through.** The rest are
conversation and judgement while the traversable-portal work continues.

| | |
|---|---|
| ![The Library Arcanum](screenshots/staged/13_library_arcanum.png) | ![The Arboretum](screenshots/staged/14_arboretum.png) |
| **The Library Arcanum** — an Elixir of Life and three books | **The Arboretum** — nine rooted trees and Wellow's Pickhammer |

---

## The interface

![The Hero's Tale](screenshots/staged/19_hero_menu.png)

The resource pack switches Minecraft's **hearts, hunger and armour bar off**
and replaces them: an ornate status frame with health, Will and stamina; your
combat multiplier; wanted stars; a detection eye and day dial; an 11 × 11
terrain radar oriented to your view; a navigation line; and a coin purse. The
vanilla hotbar and XP bar are all that survive.

The **Guild Seal** opens *The Hero's Tale* — eleven storybook pages covering
every scripted system: The Hero, Magic, Appearance, Weapons, Inventory,
Clothing, Expressions, Quests, Factions, Map of Albion and Logbook. Sneak-use
it to recall to the Guild.

→ [docs/INTERFACE.md](docs/INTERFACE.md)

---

## Quests and creatures

![Twinblade's camp](screenshots/staged/17_twinblade_camp.png)

Fifteen quests: a seven-step main chain from *Join the Heroes' Guild* to
*Battle Jack of Blades*, six side quests and two standing jobs. Renown gates
what you are offered, so the chain opens itself.

Fifty-one creatures and NPCs, and none of them slide — every one walks with
alternating limbs, breathes on idle, looks around, gestures while talking and
follows through on attacks, with identical townsfolk phase-offset so a crowd
never moves in lockstep.

![Balverines by moonlight](screenshots/staged/15_balverine_night.png)

→ [docs/QUESTS.md](docs/QUESTS.md) · [docs/BESTIARY.md](docs/BESTIARY.md)

---

## How to play

| Action | How |
|---|---|
| Open the Hero menu | Use the **Guild Seal** |
| Recall to the Guild | **Sneak + use** the Guild Seal |
| Fast-travel | Stand on a **Cullis Gate** and sneak |
| Take a quest | Use a **Quest Card**, or a **Guild lectern** in the great hall |
| Cast a Will power | Assign quick-cast slots on the **Magic** page; crouch-use cycles them |
| Absorb experience orbs | Walk over a dropped orb — each colour feeds its own pool |
| Augment a weapon | Route a stone through **Inventory** and pick a weapon at the forge |
| Train | **The Hero** page, at the Guild |
| Check your standing | **Factions** page |
| Mine Will Shards | Dig for glowing **azurite ore** between y 4 and y 54 |
| Perform an expression | **Expressions** page, or `/fable:emote <name>` |
| Pay off a bounty | Let an enforcing guard reach you, then **Pay**, **Jail** or **Resist** |

Debug commands: `/fable:npc_stats`, `/fable:npc_react`, `/fable:animate`,
`/fable:test`, `/scriptevent fc:wanted`, `/scriptevent fc:clearwanted`,
`/scriptevent fc:reanchor`.

---

## Where it stands

**Working and playable.** Morality with live visual states · four XP pools,
training and the combat multiplier · 18 Will powers on the modular engine ·
the 131-recipe forge and augment system · 13 armour sets and the named arsenal
· five-faction reputation · settlement bounties, warrants and jail · the Cullis
lattice · 8 Demon Doors, 2 of them traversable · 51 fully animated entities ·
31 expressions · romance and marriage · the two-phase Jack of Blades finale ·
262 synthesized sounds.

**In progress.**

- **TLC conformance.** A running series of reviewed passes rebuilding the Guild
  and the Demon Door reward worlds against original references, tracked in
  [the priority ledger](docs/GUILD_DEMON_PRIORITIES.md). Offline validation is
  in place; **in-engine acceptance for every pass is still outstanding** — a
  render is never an in-game pass.
- **More traversable doors.** Six of the eight still only talk.
- **Deeper NPC routines.** Day/night schedules, shop hours, crowd gathering,
  smarter guard pathing, and continued multiplayer-sync hardening.
- **Will & Destiny finishing work.** The remaining physique and appearance
  morphs. See [WILL_AND_DESTINY_PHASE1.md](WILL_AND_DESTINY_PHASE1.md) and
  [SPELL_COMPANIONS.md](SPELL_COMPANIONS.md) — in-world spell verification is
  still manual and still pending.
- **Branding.** The original-name mode and its release scanner are unfinished,
  which is what blocks distribution.

**Planned.** Procedurally generated quests seeded from your standing, morality
and renown · more Demon Doors and Focus Sites · a wider legendary loot table ·
an economy balancing pass.

---

## Building

Nothing in `packs/` is authored by hand — it is all generator output, checked
in for diffability. Edit the generator, not the file.

```bash
python scripts/build_addon.py       # regenerate, validate, package
python scripts/validate.py          # 56 gates; also the CI entry point
npm test && npm run lint            # JS runtime tests and eslint
```

Twelve generators produce every texture, model, structure, sound, behaviour
file and runtime string, all deterministically seeded, so the same source
yields the same bytes on every machine.

→ **[docs/BUILDING.md](docs/BUILDING.md)**

---

## Documentation

**[docs/README.md](docs/README.md)** indexes everything. The guides:

[Getting started](docs/GETTING_STARTED.md) ·
[The Hero](docs/HERO.md) ·
[Will](docs/WILL.md) ·
[The forge](docs/FORGE.md) ·
[Albion](docs/ALBION.md) ·
[Bestiary](docs/BESTIARY.md) ·
[Quests](docs/QUESTS.md) ·
[Interface](docs/INTERFACE.md) ·
[Building](docs/BUILDING.md) ·
[About the imagery](docs/MEDIA.md)

The `docs/` folder also holds the TLC conformance ledger — per-room reference
notes, geometry decisions and evidence trails. It is the engineering record,
and it is indexed separately.

---

## Credits and legal

A fan tribute to *Fable: The Lost Chapters* (Lionhead Studios / Microsoft). All
Fable lore, names and concepts belong to Microsoft. Inspired by the original
[Fablecraft mod](https://www.planetminecraft.com/mod/fablecraft-mod-216181/)
for Minecraft 1.1. Not affiliated with Mojang or Microsoft.

Fablecraft is a free, non-commercial, unaffiliated fan work built from original
and generated assets, with nothing extracted from any Fable game. Fable and
Albion trademarks belong to Microsoft; no endorsement by Microsoft, Lionhead or
Mojang is implied. We will comply with rights-holder takedown requests.

Faithful names are for local development only. Public builds must use original
names and pass the branding validator, which is not finished — so the archives
in `dist/` are legacy development builds, **not approved releases**.

See **[LEGAL.md](LEGAL.md)** for the full notice, provenance requirements and
distribution policy. General information, not legal advice.

*"Your health is low. Do you have any potions? Or food?"*

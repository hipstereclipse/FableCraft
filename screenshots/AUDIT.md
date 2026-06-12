# Fablecraft: Reforged — Visual Audit

Automated appearance audit of all generated renders. Metrics measured
directly from the rendered RGBA buffers:

- **coverage** — % of frame occupied by the subject (silhouette weight)
- **colors** — distinct quantized colours (palette richness)
- **contrast** — luminance spread 0..1 (shading depth)
- **brightness** — mean luminance 0..1

Grades: S (≥90) A (≥75) B (≥60) C (≥45) D (<45)

## Mobs & NPCs

| Asset | Grade | Score | Coverage % | Colours | Contrast | Brightness | Notes |
|---|---|---|---|---|---|---|---|
| White Balverine | **S** | 100 | 17.2 | 25 | 0.99 | 0.53 | — |
| Frost Balverine | **S** | 100 | 17.2 | 28 | 0.96 | 0.46 | — |
| Hobbe | **S** | 100 | 22.2 | 22 | 0.95 | 0.36 | — |
| Hobbe Scout | **S** | 100 | 22.2 | 20 | 0.95 | 0.33 | — |
| Bandit | **S** | 100 | 16.4 | 30 | 0.95 | 0.23 | — |
| Bandit Archer | **S** | 100 | 16.4 | 24 | 0.95 | 0.22 | — |
| Twinblade | **S** | 100 | 22.3 | 47 | 1.0 | 0.3 | — |
| Hollow Man | **S** | 100 | 16.5 | 17 | 0.99 | 0.58 | — |
| Hollow Soldier | **S** | 100 | 16.5 | 31 | 0.99 | 0.45 | — |
| Hollow Knight | **S** | 100 | 17.2 | 23 | 0.95 | 0.28 | — |
| Wasp | **S** | 100 | 19.5 | 24 | 0.99 | 0.46 | — |
| Wasp Queen | **S** | 100 | 19.5 | 32 | 0.99 | 0.45 | — |
| Stag Beetle | **S** | 100 | 30.4 | 14 | 0.95 | 0.33 | — |
| Earth Troll | **S** | 100 | 32.7 | 24 | 0.95 | 0.25 | — |
| Ice Troll | **S** | 100 | 32.7 | 25 | 0.96 | 0.43 | — |
| Rock Giant | **S** | 100 | 32.7 | 22 | 0.95 | 0.21 | — |
| Wraith | **S** | 100 | 16.8 | 31 | 0.98 | 0.52 | — |
| Banshee | **S** | 100 | 15.3 | 30 | 0.99 | 0.71 | — |
| Minion | **S** | 100 | 20.5 | 30 | 0.99 | 0.24 | — |
| Jack of Blades | **S** | 100 | 18.0 | 49 | 0.99 | 0.25 | — |
| Albion Villager | **S** | 100 | 16.7 | 29 | 0.95 | 0.28 | — |
| Albion Villager (Woman) | **S** | 100 | 17.0 | 36 | 0.95 | 0.27 | — |
| Albion Farmer | **S** | 100 | 16.7 | 39 | 0.96 | 0.35 | — |
| Bowerstone Tailor | **S** | 100 | 16.9 | 40 | 0.95 | 0.25 | — |
| Albion Blacksmith | **S** | 100 | 16.7 | 35 | 0.95 | 0.19 | — |
| Oakvale Fisher | **S** | 100 | 16.7 | 47 | 0.95 | 0.31 | — |
| Bowerstone Guard | **S** | 100 | 17.1 | 37 | 0.95 | 0.37 | — |
| Oakvale Guard | **S** | 100 | 17.1 | 36 | 0.95 | 0.38 | — |
| Snowspire Guard | **S** | 100 | 17.1 | 38 | 0.99 | 0.46 | — |
| Trader | **S** | 100 | 14.1 | 26 | 0.95 | 0.29 | — |
| Barkeep | **S** | 100 | 16.4 | 23 | 0.95 | 0.25 | — |
| Guildmaster | **S** | 100 | 16.8 | 41 | 0.96 | 0.34 | — |
| Guild Apprentice (Might) | **S** | 100 | 16.9 | 43 | 1.0 | 0.47 | — |
| Guild Apprentice (Skill) | **S** | 100 | 16.9 | 43 | 1.0 | 0.48 | — |
| Guild Apprentice (Will) | **S** | 100 | 16.9 | 43 | 1.0 | 0.48 | — |
| Maze | **S** | 100 | 16.3 | 35 | 0.99 | 0.35 | — |
| Lady Grey | **S** | 100 | 16.7 | 41 | 0.95 | 0.31 | — |
| The Oracle | **S** | 100 | 16.8 | 26 | 0.99 | 0.68 | — |
| Briar Rose | **S** | 100 | 16.5 | 35 | 0.95 | 0.19 | — |
| Mercenary | **S** | 100 | 17.2 | 31 | 0.95 | 0.27 | — |
| Summoned Hornet | **S** | 100 | 19.5 | 31 | 0.98 | 0.48 | — |
| Summoned Hobbe | **S** | 100 | 22.2 | 23 | 0.95 | 0.45 | — |
| Summoned Balverine | **S** | 100 | 17.2 | 26 | 0.95 | 0.3 | — |
| Demon Door | **S** | 100 | 30.6 | 22 | 0.95 | 0.29 | — |
| Balverine | **S** | 92 | 17.2 | 16 | 0.95 | 0.14 | — |
| Arachanox | **S** | 92 | 19.6 | 16 | 0.95 | 0.15 | — |
| Assassin | **S** | 92 | 16.5 | 14 | 0.95 | 0.11 | — |
| Dragon of Blades | **S** | 92 | 21.2 | 17 | 0.95 | 0.1 | — |
| Theresa | **S** | 92 | 16.9 | 36 | 0.96 | 0.16 | — |
| Summoner | **A** | 85 | 16.5 | 11 | 0.95 | 0.18 | — |
| Nymph | **A** | 77 | 25.8 | 12 | 0.99 | 0.85 | — |

**Category average: 98.5**

## Items

| Asset | Grade | Score | Coverage % | Colours | Contrast | Brightness | Notes |
|---|---|---|---|---|---|---|---|
| Iron Longsword | **S** | 100 | 28.1 | 12 | 0.88 | 0.34 | — |
| Iron Katana | **S** | 100 | 24.2 | 7 | 0.9 | 0.33 | — |
| Iron Cleaver | **S** | 100 | 28.9 | 6 | 0.83 | 0.35 | — |
| Iron Axe | **S** | 100 | 32.0 | 7 | 0.83 | 0.31 | — |
| Iron Mace | **S** | 100 | 36.3 | 7 | 0.87 | 0.29 | — |
| Iron Pickhammer | **S** | 100 | 42.6 | 8 | 0.83 | 0.36 | — |
| Iron Greataxe | **S** | 100 | 37.9 | 7 | 0.83 | 0.33 | — |
| Iron Greatsword | **S** | 100 | 25.0 | 8 | 0.87 | 0.33 | — |
| Iron Greathammer | **S** | 100 | 38.7 | 8 | 0.83 | 0.36 | — |
| Steel Longsword | **S** | 100 | 28.1 | 12 | 0.88 | 0.37 | — |
| Steel Katana | **S** | 100 | 24.2 | 7 | 0.92 | 0.35 | — |
| Steel Cleaver | **S** | 100 | 28.9 | 6 | 0.92 | 0.4 | — |
| Steel Axe | **S** | 100 | 32.0 | 7 | 0.92 | 0.35 | — |
| Steel Mace | **S** | 100 | 36.3 | 7 | 0.92 | 0.32 | — |
| Steel Pickhammer | **S** | 100 | 42.6 | 8 | 0.92 | 0.41 | — |
| Steel Greataxe | **S** | 100 | 37.9 | 7 | 0.92 | 0.37 | — |
| Steel Greatsword | **S** | 100 | 25.0 | 8 | 0.92 | 0.36 | — |
| Steel Greathammer | **S** | 100 | 38.7 | 8 | 0.92 | 0.4 | — |
| Obsidian Longsword | **S** | 100 | 28.1 | 12 | 0.88 | 0.25 | — |
| Obsidian Katana | **S** | 100 | 24.2 | 7 | 0.74 | 0.24 | — |
| Obsidian Mace | **S** | 100 | 36.3 | 6 | 0.74 | 0.19 | — |
| Obsidian Greatsword | **S** | 100 | 25.0 | 8 | 0.74 | 0.21 | — |
| Master Longsword | **S** | 100 | 28.1 | 12 | 0.88 | 0.38 | — |
| Master Katana | **S** | 100 | 24.2 | 7 | 0.92 | 0.36 | — |
| Master Cleaver | **S** | 100 | 28.9 | 6 | 0.91 | 0.41 | — |
| Master Axe | **S** | 100 | 32.0 | 7 | 0.91 | 0.35 | — |
| Master Mace | **S** | 100 | 36.3 | 7 | 0.92 | 0.33 | — |
| Master Pickhammer | **S** | 100 | 42.6 | 8 | 0.91 | 0.42 | — |
| Master Greataxe | **S** | 100 | 37.9 | 7 | 0.91 | 0.38 | — |
| Master Greatsword | **S** | 100 | 25.0 | 8 | 0.92 | 0.37 | — |
| Master Greathammer | **S** | 100 | 38.7 | 8 | 0.91 | 0.42 | — |
| Yew Longbow | **S** | 100 | 46.1 | 7 | 0.84 | 0.29 | — |
| Yew Crossbow | **S** | 100 | 42.2 | 9 | 0.86 | 0.26 | — |
| Oak Longbow | **S** | 100 | 46.1 | 8 | 0.84 | 0.27 | — |
| Oak Crossbow | **S** | 100 | 42.2 | 8 | 0.86 | 0.26 | — |
| Ebony Longbow | **S** | 100 | 46.1 | 8 | 0.84 | 0.25 | — |
| Ebony Crossbow | **S** | 100 | 42.2 | 9 | 0.86 | 0.25 | — |
| Master Longbow | **S** | 100 | 46.1 | 8 | 0.91 | 0.36 | — |
| Master Crossbow | **S** | 100 | 42.2 | 9 | 0.86 | 0.28 | — |
| Sword of Aeons | **S** | 100 | 31.3 | 15 | 0.92 | 0.44 | — |
| Avo's Tear | **S** | 100 | 31.0 | 13 | 0.82 | 0.79 | — |
| Solus Greatsword | **S** | 100 | 30.4 | 13 | 0.83 | 0.77 | — |
| The Bereaver | **S** | 100 | 25.4 | 11 | 0.83 | 0.65 | — |
| Skorm's Bow | **S** | 100 | 43.8 | 12 | 0.81 | 0.41 | — |
| Scimitar | **S** | 100 | 29.3 | 13 | 0.9 | 0.38 | — |
| Apprentice Helm | **S** | 100 | 60.2 | 7 | 0.92 | 0.53 | — |
| Apprentice Torso | **S** | 100 | 51.6 | 8 | 0.92 | 0.55 | — |
| Apprentice Legs | **S** | 100 | 48.4 | 6 | 0.92 | 0.53 | — |
| Apprentice Boots | **S** | 100 | 41.0 | 7 | 0.92 | 0.43 | — |
| Villager Helm | **S** | 100 | 49.2 | 6 | 0.5 | 0.27 | — |
| Villager Torso | **S** | 100 | 51.6 | 6 | 0.5 | 0.3 | — |
| Villager Legs | **S** | 100 | 48.4 | 6 | 0.5 | 0.28 | — |
| Villager Boots | **S** | 100 | 41.0 | 7 | 0.5 | 0.23 | — |
| Bright Leather Helm | **S** | 100 | 49.2 | 6 | 0.69 | 0.35 | — |
| Bright Leather Torso | **S** | 100 | 51.6 | 6 | 0.69 | 0.39 | — |
| Bright Leather Legs | **S** | 100 | 48.4 | 6 | 0.69 | 0.35 | — |
| Bright Leather Boots | **S** | 100 | 41.0 | 7 | 0.69 | 0.3 | — |
| Bright Chainmail Helm | **S** | 100 | 49.2 | 6 | 0.82 | 0.44 | — |
| Bright Chainmail Torso | **S** | 100 | 51.6 | 6 | 0.82 | 0.5 | — |
| Bright Chainmail Legs | **S** | 100 | 48.4 | 6 | 0.82 | 0.45 | — |
| Bright Chainmail Boots | **S** | 100 | 41.0 | 7 | 0.82 | 0.37 | — |
| Dark Chainmail Helm | **S** | 100 | 49.2 | 6 | 0.53 | 0.22 | — |
| Dark Chainmail Torso | **S** | 100 | 51.6 | 6 | 0.53 | 0.25 | — |
| Dark Chainmail Legs | **S** | 100 | 48.4 | 6 | 0.53 | 0.23 | — |
| Dark Chainmail Boots | **S** | 100 | 41.0 | 6 | 0.53 | 0.19 | — |
| Platemail Helm | **S** | 100 | 49.2 | 6 | 0.91 | 0.44 | — |
| Platemail Torso | **S** | 100 | 51.6 | 6 | 0.91 | 0.5 | — |
| Platemail Legs | **S** | 100 | 48.4 | 6 | 0.91 | 0.46 | — |
| Platemail Boots | **S** | 100 | 41.0 | 7 | 0.91 | 0.37 | — |
| Bowerstone Guard Helm | **S** | 100 | 49.2 | 6 | 0.62 | 0.23 | — |
| Bowerstone Guard Torso | **S** | 100 | 51.6 | 6 | 0.61 | 0.25 | — |
| Bowerstone Guard Legs | **S** | 100 | 48.4 | 6 | 0.61 | 0.22 | — |
| Bowerstone Guard Boots | **S** | 100 | 41.0 | 7 | 0.61 | 0.2 | — |
| Oakvale Guard Helm | **S** | 100 | 49.2 | 6 | 0.66 | 0.23 | — |
| Oakvale Guard Torso | **S** | 100 | 51.6 | 6 | 0.66 | 0.25 | — |
| Oakvale Guard Legs | **S** | 100 | 48.4 | 6 | 0.66 | 0.22 | — |
| Oakvale Guard Boots | **S** | 100 | 41.0 | 7 | 0.66 | 0.2 | — |
| Snowspire Guard Helm | **S** | 100 | 49.2 | 6 | 0.83 | 0.35 | — |
| Snowspire Guard Torso | **S** | 100 | 51.6 | 6 | 0.82 | 0.39 | — |
| Snowspire Guard Legs | **S** | 100 | 48.4 | 6 | 0.82 | 0.34 | — |
| Snowspire Guard Boots | **S** | 100 | 41.0 | 7 | 0.82 | 0.3 | — |
| Fire Assassin Boots | **S** | 100 | 41.0 | 6 | 0.5 | 0.15 | — |
| Archon's Battle Armour Helm | **S** | 100 | 49.2 | 6 | 0.92 | 0.52 | — |
| Archon's Battle Armour Torso | **S** | 100 | 51.6 | 6 | 0.92 | 0.59 | — |
| Archon's Battle Armour Legs | **S** | 100 | 48.4 | 6 | 0.92 | 0.54 | — |
| Archon's Battle Armour Boots | **S** | 100 | 41.0 | 7 | 0.92 | 0.45 | — |
| Holy Warrior Helm | **S** | 100 | 49.2 | 6 | 0.92 | 0.53 | — |
| Pimp Hat | **S** | 100 | 45.3 | 12 | 0.89 | 0.24 | — |
| Sharpening Augmentation | **S** | 100 | 75.0 | 10 | 0.53 | 0.34 | — |
| Piercing Augmentation | **S** | 100 | 75.0 | 11 | 0.61 | 0.74 | — |
| Health Augmentation | **S** | 100 | 75.0 | 11 | 0.53 | 0.25 | — |
| Mana Augmentation | **S** | 100 | 75.0 | 11 | 0.53 | 0.34 | — |
| Experience Augmentation | **S** | 100 | 75.0 | 11 | 0.52 | 0.61 | — |
| Lightning Augmentation | **S** | 100 | 75.0 | 12 | 0.58 | 0.62 | — |
| Flame Augmentation | **S** | 100 | 75.0 | 11 | 0.52 | 0.55 | — |
| Silver Augmentation | **S** | 100 | 75.0 | 8 | 0.53 | 0.87 | — |
| Health Potion | **S** | 100 | 37.1 | 6 | 0.92 | 0.36 | — |
| Great Health Potion | **S** | 100 | 49.6 | 6 | 0.92 | 0.39 | — |
| Will Potion | **S** | 100 | 37.1 | 6 | 0.92 | 0.39 | — |
| Great Will Potion | **S** | 100 | 49.6 | 6 | 0.92 | 0.4 | — |
| Resurrection Phial | **S** | 100 | 21.1 | 8 | 0.52 | 0.82 | — |
| Ages of Might Potion | **S** | 100 | 21.1 | 8 | 0.77 | 0.65 | — |
| Ages of Skill Potion | **S** | 100 | 21.1 | 8 | 0.56 | 0.79 | — |
| Ages of Will Potion | **S** | 100 | 21.1 | 8 | 0.74 | 0.67 | — |
| Elixir of Life | **S** | 100 | 21.1 | 8 | 0.53 | 0.81 | — |
| Red Meat | **S** | 100 | 41.0 | 6 | 0.82 | 0.35 | — |
| Apple Pie | **S** | 100 | 53.5 | 6 | 0.78 | 0.49 | — |
| Gold Coin | **S** | 100 | 47.3 | 6 | 0.87 | 0.6 | — |
| Septimal Key | **S** | 100 | 20.3 | 6 | 0.63 | 0.44 | — |
| Guild Seal | **S** | 100 | 44.9 | 6 | 0.66 | 0.65 | — |
| Quest Card | **S** | 100 | 85.9 | 7 | 0.76 | 0.51 | — |
| Balverine Fang | **S** | 100 | 18.4 | 6 | 0.92 | 0.37 | — |
| Frost Balverine Hide | **S** | 100 | 50.0 | 7 | 0.88 | 0.55 | — |
| Balverine Summoning Trophy | **S** | 100 | 48.0 | 6 | 0.7 | 0.39 | — |
| Wasp Wing | **S** | 100 | 32.4 | 7 | 0.92 | 0.49 | — |
| Beetle Chitin | **S** | 100 | 18.4 | 6 | 0.92 | 0.21 | — |
| Troll Heart | **S** | 100 | 39.1 | 7 | 0.92 | 0.25 | — |
| Ectoplasm | **S** | 100 | 36.7 | 6 | 0.52 | 0.8 | — |
| Banshee's Tear | **S** | 100 | 12.5 | 6 | 0.51 | 0.78 | — |
| Minion Flesh | **S** | 100 | 36.7 | 6 | 0.8 | 0.3 | — |
| Steel Ingot | **S** | 100 | 44.1 | 6 | 0.92 | 0.5 | — |
| Obsidian Ingot | **S** | 100 | 44.1 | 7 | 0.92 | 0.2 | — |
| Master Ingot | **S** | 100 | 44.1 | 6 | 0.92 | 0.58 | — |
| Will Shard | **S** | 100 | 55.9 | 7 | 0.65 | 0.61 | — |
| Leather Straps | **S** | 100 | 49.2 | 6 | 0.51 | 0.19 | — |
| Guild Cloth | **S** | 100 | 50.0 | 6 | 0.92 | 0.52 | — |
| Runed Hilt | **S** | 100 | 37.9 | 8 | 0.78 | 0.32 | — |
| Strength Orb | **S** | 100 | 74.6 | 6 | 0.76 | 0.39 | — |
| Will Orb | **S** | 100 | 74.6 | 6 | 0.72 | 0.48 | — |
| Obsidian Cleaver | **A** | 85 | 28.9 | 6 | 0.45 | 0.22 | — |
| Obsidian Axe | **A** | 85 | 32.0 | 6 | 0.45 | 0.19 | — |
| Obsidian Pickhammer | **A** | 85 | 42.6 | 7 | 0.45 | 0.22 | — |
| Obsidian Greataxe | **A** | 85 | 37.9 | 6 | 0.45 | 0.2 | — |
| Obsidian Greathammer | **A** | 85 | 38.7 | 7 | 0.45 | 0.22 | — |
| The Harbinger | **A** | 85 | 7.3 | 11 | 0.84 | 0.64 | sparse silhouette |
| Arken's Crossbow | **A** | 85 | 9.4 | 12 | 0.84 | 0.44 | sparse silhouette |
| Avenger | **A** | 85 | 5.9 | 6 | 0.88 | 0.67 | sparse silhouette |
| Orkon's Club | **A** | 85 | 4.2 | 12 | 0.81 | 0.48 | sparse silhouette |
| Dollmaster's Mace | **A** | 85 | 10.4 | 14 | 0.79 | 0.52 | sparse silhouette |
| Wellow's Pickhammer | **A** | 85 | 9.6 | 12 | 0.68 | 0.58 | sparse silhouette |
| Katana Hiryu | **A** | 85 | 5.9 | 7 | 0.77 | 0.65 | sparse silhouette |
| Stick | **A** | 85 | 16.0 | 7 | 0.41 | 0.19 | — |
| Assassin Boots | **A** | 85 | 41.0 | 6 | 0.44 | 0.12 | — |
| Fire Assassin Helm | **A** | 85 | 60.2 | 6 | 0.48 | 0.17 | — |
| Fire Assassin Torso | **A** | 85 | 51.6 | 6 | 0.48 | 0.17 | — |
| Fire Assassin Legs | **A** | 85 | 48.4 | 6 | 0.48 | 0.15 | — |
| Demon Helm | **A** | 85 | 53.9 | 6 | 0.41 | 0.14 | — |
| Cured Leather | **A** | 85 | 50.0 | 6 | 0.32 | 0.24 | — |
| Wizard Hat | **A** | 83 | 44.1 | 4 | 0.63 | 0.25 | — |
| Bright Wizard Hat | **A** | 83 | 44.1 | 4 | 0.9 | 0.55 | — |
| Crunchy Chick | **A** | 83 | 32.4 | 4 | 0.76 | 0.56 | — |
| Tofu | **A** | 83 | 32.8 | 5 | 0.91 | 0.56 | — |
| Hobbe Tooth Ale | **A** | 83 | 37.9 | 4 | 0.83 | 0.35 | — |
| Will: Enflame | **A** | 83 | 85.9 | 4 | 0.59 | 0.53 | — |
| Will: Fireball | **A** | 83 | 85.9 | 4 | 0.63 | 0.45 | — |
| Will: Lightning | **A** | 83 | 85.9 | 4 | 0.52 | 0.64 | — |
| Will: Force Push | **A** | 83 | 85.9 | 4 | 0.55 | 0.72 | — |
| Will: Drain Life | **A** | 83 | 85.9 | 4 | 0.76 | 0.26 | — |
| Will: Physical Shield | **A** | 83 | 85.9 | 4 | 0.56 | 0.58 | — |
| Will: Slow Time | **A** | 83 | 85.9 | 4 | 0.53 | 0.79 | — |
| Will: Assassin Rush | **A** | 83 | 85.9 | 4 | 0.61 | 0.49 | — |
| Will: Turncoat | **A** | 83 | 85.9 | 4 | 0.52 | 0.63 | — |
| Will: Multi Arrow | **A** | 83 | 85.9 | 4 | 0.51 | 0.79 | — |
| Will: Multi Strike | **A** | 83 | 85.9 | 4 | 0.52 | 0.74 | — |
| Will: Battle Charge | **A** | 83 | 85.9 | 4 | 0.51 | 0.66 | — |
| Will: Berserk | **A** | 83 | 85.9 | 4 | 0.68 | 0.38 | — |
| Will: Infernal Wrath | **A** | 83 | 85.9 | 4 | 0.72 | 0.32 | — |
| Silver Key | **A** | 83 | 30.9 | 4 | 0.92 | 0.46 | — |
| Wedding Ring | **A** | 83 | 35.2 | 5 | 0.92 | 0.49 | — |
| Queen's Stinger | **A** | 83 | 16.0 | 5 | 0.53 | 0.72 | — |
| Troll Bones | **A** | 83 | 31.6 | 4 | 0.91 | 0.52 | — |
| Arachanox Stinger | **A** | 83 | 16.0 | 5 | 0.74 | 0.42 | — |
| Giant's Core | **A** | 83 | 84.4 | 5 | 0.73 | 0.48 | — |
| Summoner's Grimoire | **A** | 83 | 85.9 | 4 | 0.77 | 0.23 | — |
| Mask of Jack of Blades | **A** | 83 | 37.1 | 5 | 0.83 | 0.28 | — |
| Chain Links | **A** | 83 | 38.3 | 4 | 0.8 | 0.37 | — |
| Tempered Plate | **A** | 83 | 40.6 | 4 | 0.85 | 0.42 | — |
| Waxed Bowstring | **A** | 83 | 35.9 | 5 | 0.86 | 0.33 | — |
| Experience Orb | **A** | 83 | 74.6 | 5 | 0.58 | 0.72 | — |
| Skill Orb | **A** | 83 | 74.6 | 5 | 0.55 | 0.76 | — |
| Dark Leather Helm | **B** | 68 | 49.2 | 5 | 0.46 | 0.16 | — |
| Dark Leather Torso | **B** | 68 | 51.6 | 5 | 0.46 | 0.17 | — |
| Dark Leather Legs | **B** | 68 | 48.4 | 5 | 0.46 | 0.17 | — |
| Dark Leather Boots | **B** | 68 | 41.0 | 5 | 0.46 | 0.14 | — |
| Assassin Helm | **B** | 68 | 60.2 | 5 | 0.42 | 0.14 | — |
| Assassin Torso | **B** | 68 | 51.6 | 5 | 0.41 | 0.14 | — |
| Assassin Legs | **B** | 68 | 48.4 | 5 | 0.41 | 0.13 | — |
| Dark Wizard Hat | **B** | 68 | 44.1 | 4 | 0.4 | 0.19 | — |
| Augment Remover | **B** | 68 | 22.3 | 5 | 0.47 | 0.23 | — |
| Will: Heal Life | **B** | 68 | 85.9 | 4 | 0.43 | 0.79 | — |
| Will: Summon | **B** | 68 | 85.9 | 4 | 0.48 | 0.74 | — |
| Will: Divine Fury | **B** | 68 | 85.9 | 4 | 0.47 | 0.85 | — |
| Seasoned Bow Stave | **B** | 68 | 23.0 | 5 | 0.39 | 0.18 | — |

**Category average: 93.5**

## Structures

| Asset | Grade | Score | Coverage % | Colours | Contrast | Brightness | Notes |
|---|---|---|---|---|---|---|---|
| Demon Door | **S** | 100 | 27.0 | 45 | 0.9 | 0.37 | — |
| Heroes' Guild | **S** | 100 | 14.7 | 48 | 0.94 | 0.35 | — |
| Chamber of Fate | **S** | 100 | 29.8 | 21 | 0.84 | 0.37 | — |
| Oakvale | **S** | 100 | 11.2 | 27 | 0.8 | 0.49 | — |
| Bowerstone Market | **S** | 100 | 12.7 | 26 | 0.89 | 0.32 | — |
| Knothole Glade | **S** | 100 | 12.8 | 32 | 0.84 | 0.33 | — |
| Hook Coast | **S** | 100 | 13.1 | 23 | 0.8 | 0.44 | — |
| Silver Key Ruin | **S** | 100 | 13.9 | 33 | 0.78 | 0.4 | — |
| Focus Site | **S** | 100 | 24.5 | 23 | 0.94 | 0.47 | — |
| Guild Courtyard | **S** | 100 | 12.2 | 42 | 0.94 | 0.48 | — |
| Oakvale Quay | **S** | 100 | 12.2 | 35 | 0.82 | 0.48 | — |
| Snowspire Oracle | **S** | 100 | 14.0 | 25 | 0.91 | 0.4 | — |
| Necropolis Ruin | **S** | 100 | 12.5 | 34 | 0.94 | 0.37 | — |
| Bandit Camp | **S** | 100 | 22.3 | 37 | 0.92 | 0.27 | — |
| Lychfield Graveyard | **S** | 100 | 13.7 | 35 | 0.89 | 0.36 | — |
| The Arena | **S** | 100 | 26.9 | 30 | 0.83 | 0.42 | — |
| Temple of Avo | **A** | 77 | 22.9 | 12 | 0.72 | 0.78 | — |
| Chapel of Skorm | **A** | 77 | 23.2 | 13 | 0.87 | 0.16 | — |

**Category average: 97.4**

## Verdict

All assets graded B or above. Ship it to Bowerstone.
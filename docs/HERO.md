# The Hero

Everything that makes your character *yours* — experience, training, alignment,
reputation and your criminal record — lives here. All of it is reachable from
the Guild Seal's storybook menu.

![The Map Room](../screenshots/staged/03_map_room.png)

---

## Experience

Four separate pools, exactly as *The Lost Chapters* has them:

| Pool | Earned by | Colour |
|---|---|---|
| **General** | any kill | green |
| **Strength** | melee kills | red |
| **Skill** | ranged kills | yellow |
| **Will** | casting | blue |

Slain creatures shed **experience orbs** in those four colours. Walk over them
to absorb the bonus. Bosses burst with them.

### The combat multiplier

Every hit you land without being hit raises your combat multiplier, and the
multiplier scales everything you earn. Take a single hit and it shatters back
to nothing. It is the whole reason Fable combat rewards aggression and spacing
rather than trading blows — and it is why Will powers that keep enemies off you
(Slow Time, Force Push, Physical Shield) are worth more than their raw damage
suggests.

The current multiplier shows under the status frame on the HUD.

### Training

Training happens at the Guild. The **Training Grounds** fill the east yard —
an archery range, a sparring ring and a Will circle — and the Guildmaster holds
court in the Map Room. Spend XP through the menu on seven attributes:

**Physique · Health · Toughness · Speed · Guile · Accuracy · Magic Power**

![The archery range](../screenshots/staged/08_archery_range.png)

---

## Morality

Morality runs from **−1000 to +1000** and it is not cosmetic.

| Deed | Change |
|---|---|
| Donating at an Altar of Light | **+125** |
| Eating pure food | +15 |
| Killing a boss | +20 |
| Killing a hostile creature | +3 |
| Eating vile food (Crunchy Chicks) | −25 |
| Killing a tamed pet | −60 |
| Killing an iron golem | −75 |
| Killing a villager | **−100** |
| Sacrificing at an Altar of Shadow | **−175** |

Alignment crosses tier boundaries at **150, 300, 500, 700, 850 and 950** in
either direction, giving seven steps each way. Those tiers gate spells (Divine
Fury needs light, Infernal Wrath needs dark), change what NPCs say to you,
change how Demon Doors judge you, and eventually change how you look.

At the extremes it becomes visible: a fully good Hero gains a radiant halo, and
a fully evil one turns red-eyed and horned with blood pooling underfoot. Both
are applied as live overlays — your skin is not replaced.

| Fully good — the radiant halo | Fully evil — Avatar of Skorm |
|:---:|:---:|
| ![Good Hero with halo](../screenshots/ingame/hero_good_paladin_halo.jpg) | ![Evil Hero in a pool of blood](../screenshots/ingame/hero_evil_avatar_of_skorm.jpg) |

> These two are genuine in-game captures. Every other image in this
> documentation is a staged render — see [MEDIA.md](MEDIA.md).

Titles run from **Avatar of Skorm** at the bottom to **Paragon** at the top,
with Avatar of Avo, Good, Neutral, Rogue and Villain between. You can also buy
a title from a trader and wear it.

---

## Factions and reputation

Five factions keep a separate ledger on you, each from **−200 to +200**:

- **The Heroes' Guild**
- **Bowerstone**
- **Oakvale**
- **Snowspire**
- **Twinblade's Bandits**

Reputation lands in one of five tiers:

| Tier | Range | What it means |
|---|---|---|
| **Hostile** | −200 … −100 | Guards attack on sight; traders refuse to serve you at all |
| **Wary** | −99 … −1 | Prices **up 15%** |
| **Neutral** | 0 … 49 | Standard prices |
| **Friendly** | 50 … 149 | **10% off** |
| **Revered** | 150 … 200 | **20% off** |

Shop prices use the *average* of your three town reputations, so being adored
in Oakvale does not offset being loathed in Bowerstone.

Clearing bandit camps raises your standing with the towns and lowers it with
Twinblade's people. Cutting down guards or villagers wrecks it. Renown is
separate and global: fame buys better quests and villager adoration, and buys
you night-time assassin ambushes.

![Bowerstone market](../screenshots/staged/09_bowerstone_market.png)

---

## Crime, bounties and jail

Spill blood inside a settlement and the law remembers — and it remembers
*per town*.

**The bounty.** Killing civilians or guards raises a bounty tied to that exact
settlement. The size of the bounty sets the response tier.

**The response.** A petty crime brings a pair of standard watchmen. As the
bounty climbs you get tougher veterans, and a true rampage brings **four elite
enforcers**.

**The warrant.** Guards approach before they strike. Close the distance and you
get a three-way choice:

- **Pay the bounty** — costs the gold, clears the warrant, nothing else happens.
- **Go to jail** — clears the warrant, but strips your carried inventory and
  armour and turns you loose outside the walls. Your Guild Seal, Will Focus,
  spell tomes and progression are spared.
- **Resist arrest** — the enforcers come for you.

**Cooling off.** Leave town and the heat decays on a wall-clock timer. Every
fresh crime buys the law more time to hunt you, up to a cap. Come back too
early and the guards are still looking.

Your wanted level shows as stars across the top of the HUD whenever a warrant
is live, wherever you are.

![A warrant in Bowerstone](../screenshots/staged/21_arrest_warrant.png)

The full mechanical spec, including the exact tier thresholds and timers, is in
[BOUNTY_SYSTEM.md](../BOUNTY_SYSTEM.md).

---

## Expressions

Thirty-one *Lost Chapters* expressions are implemented — the social system, not
just emotes. They run on your Hero and on the NPCs around you, and townsfolk
react to what you do.

Trigger them from the **Expressions** page of the storybook menu, or with
`/fable:emote <name>`. You can also bind your native Bedrock Persona emotes to
Fable expressions.

The set covers the full original range, from Laugh, Clap, Apologise and Thanks
through the dances (Cossack, Flamenco, Disco, Ballet, Tap, Air Guitar) to Blood
Lust Roar, Sneer, Insult and the ruder end of Albion's social vocabulary.
Validation notes are in
[FABLE_EMOTE_VALIDATION.md](../FABLE_EMOTE_VALIDATION.md).

---

## The final choice

Defeat Jack of Blades and his dragon form and the **Sword of Aeons** is yours.
Keep it and rule Albion through fear, or cast it away and receive **Avo's
Tear**. The classic ending, unchanged.

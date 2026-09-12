# FableCraft - Full World Build Spec

Companion to **HeroesGuild_BuildSpec_SAMPLE.md**. Same format: footprints, top-down sketches, room/area adjacency, concrete Minecraft block palettes, vertical profiles, and connection points - every line tagged by confidence.

**Confidence legend:**
- **[C]** documented / canon (from sources)
- **[G]** from the game's actual look - verify against screenshots
- **[B]** buildable interpretation - scale / blocks I'm *proposing*, **not** canon. Swap freely.

> **Honesty note on [G]:** My visual confidence is highest for the iconic hubs (Oakvale, Bowerstone, the Guild). For minor and TLC-only regions (Necropolis, Lost Bay, Archon's Folly, etc.) it's thinner, so those entries lean on **[C]** facts + tagged **[B]** interpretation and use **[G]** sparingly. Prioritize screenshot verification on anything marked [G] in the back half of this doc.

---

## 1. Topology quick-map (how it all connects)

Albion is a network of discrete loading-zones joined at fixed gates/paths, with **Cullis Gates** (round glowing stone platforms) for long-range teleport. Build each as its own zone, linked by a distinct gateway structure (stone arch, wooden gate, or Cullis Gate disc).

```
                    [NORTHERN WASTES - TLC only]
        Lost Bay -> Foothills -+-> Necropolis
                               +-> Archon's Shrine -> Bronze Gate -> Archon's Folly
                               +-> Snowspire Village (Oracle)
                                   ^
                                   | (Ship of the Drowned, from the lighthouse)
                                   |
   [HOOK COAST] (snowy island, via Cullis Gate) -- lighthouse + ruined Abbey
                                   |
   [LYCHFIELD / BARGATE] -- Graveyard -> Old Graveyard Path -> tunnels -> Bargate Prison (island)
                                   | (north of Bowerstone)
                                   |
   [BOWERSTONE] -- South (slums/market) --+-- North (wealthy, gated)
                                          +-- Quay (harbor)
                                   |
                                   | (bridge)
   [LOOKOUT POINT] (central safe hub) --+-- Heroes' Guild (west)
                                        +-- Picnic Area
                                        +-- Greatwood Entrance (south)
                                   |
   [GREATWOOD] -- Entrance -+-- Fisher Creek / Orchard Farm / Rose Cottage
                            +-- Greatwood Lake -> Gorge (toll bridge) -> Cullis Gate
                            +-- Greatwood Caves (-> Hobbe Cave) -> south to Darkwood
                                   |
   [DARKWOOD] -- Entrance -> Marshes / Lake / Weir / Camp / Bordello(TLC) / Chapel of Skorm
                            -> Ancient Cullis Gate -> south to Barrow Fields
                                   |
   [OAKVALE] (coastal) -- Barrow Fields / Memorial Garden / Grey House
                            +-- Clifftop Path -> Abandoned Road -> Twinblade's Camp -> Tent

   [WITCHWOOD] (misty island, via Cullis Gate) -- Stones -> Temple of Avo / Lake
                            +-- Knothole Glade (village)
                            +-- Arena Entrance -> Arena -> Hall of Heroes
```

---

## 2. MAJOR HUB: OAKVALE (coastal starting village)

**Lore flavor [C]:** The Hero's secluded southern seaside home - farming + fishing. Burned by bandits early, rebuilt later. Warm and idyllic; the tonal opposite of Darkwood next door.

### Footprint & organization
**[C/G]** A village on a **rise above a beach**, built **amongst coastal cliffs**, arranged around a **central area with a large tree** that the shops surround. A **guarded gate** controls entry (weapons confiscated). Steps down to a **pier/quay** on the sea.

**[B] Envelope:** ~**80 x 80**, village core on a low plateau (y=66) stepping down ~4 blocks to **beach + sea** on the south/east edge. Tilled field west of the gate; barns to the SE.

```
        cliffs / fence line
   +-----------------------------------+
   |  TILLED FIELD     [TAVERN]        |
   |  + scarecrow                      |
   |        GATE==      ( BIG TREE )   |
   |        (guard)    [SHOP] [WEAPONS]|
   |                    [TATTOO]       |
   |   WELL  o   houses ring the green |
   |                                   |   > path E to MEMORIAL GARDEN
   |   ~~~ steps down to BEACH ~~~     |   > path to BARROW FIELDS
   |        PIER====o (quay, guarded)  |   > CLIFFTOP PATH (to bandits)
   +------------ SEA ------------------+
```

### Building-by-building
- **[C] Tavern** - the social hub. **[B]** Two-storey, biggest civic building; warm-lit, dark-oak + plaster, hanging sign.
- **[C] General store, weapons shop, tattoo shop** - ring the central tree. **[B]** Single-storey cottages with shop counters/signs facing the green.
- **[C/G] Houses** - modest cottages (4 in childhood, 7+ rebuilt) ringing a **well**. **[B]** 1-1.5 storeys, ~6x6 footprints.
- **[C] Memorial Garden** (graveyard, up a path E) - contains **a statue of a hero swinging a giant axe** + many graves. **[B]** Walled plot, the axe-hero statue as centerpiece (stone + armor-stand or carved form).
- **[C] Oakvale Demon Door** (the "Serenity Farm" door - wants an act of pure love). **[B]** Carved-face stone door in a wall near the green.
- **[C] Three barns** for food storage (SE); **tilled field + scarecrow** (W of gate). **[B]** Spruce barns, farmland with wheat, a scarecrow (fence + pumpkin + hay).

### Materials & atmosphere [G]
- **Cottages:** light **plaster walls** (white terracotta / bone-block / smooth quartz infill) over **spruce/oak timber frames**; **thatch roofs** - build thatch as **stripped-birch stairs/slabs** or **hay-bale + spruce-trapdoor** overlay.
- **Ground:** grass green core, **sand + sandstone** beach, **dirt-path** lanes.
- **Sea:** water; ruined boats + a jetty on the western beach (**spruce + stripped-log wrecks**).
- **Palette:** sandy tan + warm wood brown + white plaster + sea blue + grass green; **bright daytime**.

### Connections [C]
Gate -> Barrow Fields; path E -> Memorial Garden; **Clifftop Path** -> Abandoned Road -> Twinblade's Camp. Darkwood lies to the north via the fields.

---

## 3. MAJOR HUB: BOWERSTONE (largest town)

**Lore flavor [C]:** Albion's economic center, just north of the Guild, ruled by Mayor Lady Elvira Grey. Walled, heavily guarded, weapons confiscated at entry. Sharply **class-divided** - and that divide should be visible in the architecture.

### Footprint & organization
**[C]** Three connected districts: **South** (slums/market), **North** (wealthy, gated off until after the Arena), **Quay** (harbor on the **River Bower**, crossed by a **bridge**). The whole town is ringed by a **large wall with guarded gates**.

**[B] Envelope:** ~**110 x 90** total. South and North separated by an internal **gated wall**; the river runs through with a **stone bridge** linking districts; the Quay sits on the water at one edge.

```
   ====== OUTER TOWN WALL (stone brick, crenellated, gatehouses) ======
   |  [BOWERSTONE NORTH - wealthy]        |
   |   [BOWERSTONE MANOR]  pub   shop     |
   |   clean Tudor townhouses             |
   |======= internal gate (class barrier) =======|
   |  [BOWERSTONE SOUTH - slums/market]   |
   |   tavern  general  armour  weapons   |
   |   barber  SCHOOL   crooked sheds     |
   |        town square / market          |
   |   ~~~~~~ RIVER BOWER + stone bridge ~~~~~~   |
   |   [BOWERSTONE QUAY] barns, huts, docks      |  > river out to Oakvale
   ===============================================
   (Bowerstone Jail cell sits OUTSIDE the north wall)
```

### Bowerstone South (slums / market) [C]
Tavern, general store, **clothing & armour shop**, weapons smith, **barber**, several houses, and **the only school in Albion**. Many residents poor, in **shed-like houses**. Chickens roam; town-square/market feel.
- **[G/B] Build:** denser and more urban than the villages - **2-3 storey timber-framed** buildings, **crooked/mixed** materials (mossy cobble, spruce, patched plaster), **cobblestone streets**. Lower and scruffier than the North. The **Tavern Cellar** sits beneath/behind the tavern.

### Bowerstone North (wealthy) [C]
Gated; entry only after the Arena. Finer, larger houses, a pub, **one shop (sells the Solus Greatsword)**, and **Bowerstone Manor** (Lady Grey's residence) - the grandest building.
- **[G/B] Build:** clean, tall **dark-oak-and-white Tudor** townhouses, ordered streets, **stone-brick Manor** with a gated forecourt. Visibly richer: straight lines, intact plaster, decorative timbering. The class barrier is an enforced internal gate.

### Bowerstone Quay (harbor) [C]
Bowerstone's only harbor, on the river; commerce with Oakvale (goods sail down the delta). Has **barns, a hut**, and (TLC) **a witch's potion hut**. The Fist Fighters gang meets here.
- **[B] Build:** wooden **docks/piers**, moored boats, **spruce barns + warehouses**, crates/barrels.

### Materials & atmosphere [G]
- **Classic Tudor:** **dark-oak / oak log frames + white plaster infill** (white terracotta/concrete), **tile roofs** (dark-oak or deepslate stairs).
- **Walls/streets:** stone-brick town wall + gatehouses; **cobblestone** streets.
- **Palette:** dark-brown timber + white plaster + grey cobble; busier and greyer than rural areas. **Class divide legible in material quality** - ramshackle South vs. clean North.

### Connections [C]
South <-> Lookout Point (bridge, S); South <-> North (internal gate); South <-> Quay; Quay <-> river to Oakvale. Lychfield lies to the **north**.

---

## 4. MAJOR HUB: KNOTHOLE GLADE (hidden forest village)

**Lore flavor [C]:** A village founded by old woodcutters on the misty **Witchwood island**, near the Arena and Temple of Avo. Birthplace of the heroine Scarlet Robe; famed for balverine hunters. Constantly threatened - the **only town where weapons may be openly carried**.

### Footprint & organization
**[C]** Tucked **among cliffs**, protected by a **large wooden gate, constantly guarded** (the secure entrance). A **statue of Scarlet Robe stands in the middle of town**. Backs onto cliffs with a hill at one end; includes a **shooting range** (a unique feature).

**[B] Envelope:** ~**70 x 70**, ringed by **stone cliffs** on most sides, one **timber gate** as the only ground entry; a hill rising at the back.

```
        ////// CLIFFS (stone, mossy) //////
   /  [CHIEF'S HUT]      ( SCARLET ROBE   \
   /                       STATUE )        \
   |  tavern  weapons   bard   general      |
   |  tattoo   wooden huts w/ totems        |
   |  SHOOTING RANGE ----->  [DEMON DOOR]   |  (opens when shot with a strong bow)
   |  marital homes at the back             |
   \   ===WOODEN GATE=== (guarded)         /
        \\\\ misty spruce forest //////
```

### Building-by-building [C]
Tavern, weapons shop, tattoo shop, general store, **Chief's hut**, a **bard**, several buyable houses (incl. **marital homes at the back**), and the **shooting range**. A **Demon Door** opens only when **shot with a strong bow**, leading to the Hidden Copse.

### Materials & atmosphere [G/B]
- **[C/G] Norse-Celtic, all-wood.** (The wiki notes Witchwood is modeled on Celtic-period Ireland; the art director wanted "Norse and Celtic" for the villagers.) Build huts from **spruce logs + planks**, **steep/conical roofs** (spruce stairs), **carved totem posts** (stripped logs with notches, mob-head or carved tops) around the village.
- **[B] Scarlet Robe statue:** stone or carved-wood centerpiece, a robed figure on a plinth.
- **Surroundings:** **stone cliffs** (andesite/stone, mossy), **misty spruce forest**, woodsmoke from huts.
- **Palette:** spruce brown + mossy green + grey cliff + smoke. Damp, sheltered, enclosed.

### Connections [C]
Wooden gate -> Witchwood Lake -> Temple of Avo / Arena Entrance; Witchwood reached from the mainland by **Cullis Gate**.

---

## 5. MAJOR HUB: HOOK COAST (northern port town)

**Lore flavor [C]:** A snowy fishing town on an isolated northern island - the only intact remnant of the **Old Kingdom**, long protected by a barrier the monks died casting. Reached only by **Cullis Gate**. Later evacuated when Screamers drive the villagers out.

### Footprint & organization
**[C]** The only **snow-covered** town in the base game. Rows of houses, a **tavern**, a **weapon shop**, **stairs connecting tiers**, a **graveyard** (lighthouse keepers + monks, with a **bell at the end of the northern row**), the **ruined Abbey** with a magical barrier at its entrance, and the dominant landmark - the **lighthouse**, in the **bottom-right by the harbor**.

**[B] Envelope:** ~**90 x 70**, tiered down toward a **harbor** on the SE; lighthouse on the harbor point; Abbey ruin set apart with its barrier.

```
        ~~~ cold grey sea ~~~
   +----------------------------------+
   |  [RUINED ABBEY]  (barrier glows  |
   |   at entrance)                   |
   |   northern house row --- (BELL)  |
   |   GRAVEYARD (monks/keepers)      |
   |   tavern   weapon shop           |
   |   --- stairs between tiers ---   |
   |                    HARBOR docks  |
   |                     [LIGHTHOUSE] o|  (Fire Heart placed at top)
   +----------- SE: Ship of the Drowned departs ->
```

### Key structures
- **[C] Lighthouse:** tall stone tower, **interior stair to the top**; the Fire Heart is placed at its summit to summon the Ship of the Drowned. **[B]** Round **stone/diorite tower ~7 dia, ~18-24 tall**, glass-and-lantern lamp room up top, optional rotating beam (sea lanterns).
- **[C] Ruined Abbey:** the monastery the monks built; **magical barrier** seals its entrance until dispelled. **[B]** Roofless **stone-brick ruin**, broken arches, a **barrier plane** (tinted glass / soul-fire wall) across the doorway.
- **[C] Graveyard + bell:** monk/keeper graves; **a bell at the end of the northern house row**. **[B]** Standing-stone markers + a bell block on a frame.

### Materials & atmosphere [G/B]
- **Old Kingdom stone** reads **older/paler** than mainland - favor **smooth stone / diorite / calcite** accents over standard brick; **weathered timber** (stripped spruce) for fishing structures.
- **Snow everywhere:** **snow layers** on every roof and surface, **packed-ice/blue-ice** at the waterline.
- **Palette:** snow white + slate-blue + grey stone + weathered wood. Cold, quiet, isolated; the rotating lighthouse beam is the one moving light.
- **Destroyed state [C]:** for "Return to Hook Coast," show it **abandoned** - no villagers, the Abbey barrier sealed.

### Connections [C]
Arrives by Cullis Gate; **Ship of the Drowned** departs the harbor to the **Northern Wastes (Lost Bay)**.

---

## 6. GREATWOOD CLUSTER (bright central forest)

**[G] Palette for the whole cluster:** bright, lush green - oak/birch forest, dappled light, lots of foliage, fern + tall grass. The cheerful counterpart to Darkwood.

- **[C] Lookout Point** - the central **safe hub** (no hostile spawns), first area after the Guild. Open grassy hilltop with a **pointing statue that rotates like a clock**, a **Boasting Platform**, a **title vendor**, and **two guards at the Bowerstone gate**. **[B]** Grassy knoll, a central plinth + rotating arrow (armor stand / banner), low fences, paths radiating to Guild / Bowerstone / Picnic Area / Greatwood. Plays the warm "Summer Fields" theme - keep it sunlit and pastoral.
- **[C] Greatwood Entrance** - open area with **fences and branching paths** to Fisher Creek / Orchard Farm / Greatwood Lake. **[B]** A forest crossroads clearing, signposts, split-rail fences.
- **[C] Greatwood Lake** - large lake; bandits + trolls. **[B]** Big water body ringed by forest, a few ruins/rocks for troll perches.
- **[C] Greatwood Gorge** - a **gorge with a bandit toll bridge** and stairs; Demon Door "Arboretum." **[B]** A ravine spanned by a **wooden toll bridge** with a bandit gate-shack; stone stairs cut into the gorge wall.
- **[C] Greatwood Cullis Gate** - teleporter clearing. **[B]** Standard Cullis Gate disc in a forest glade.
- **[C] Greatwood Caves** - rocky tunnels **separating Greatwood from Darkwood**; house the **Hobbe Caves** entrance and the "Butterfly House" Demon Door; a sign reads **"Abandon hope all ye who enter here."** **[B]** Stone tunnel network, the warning sign at the mouth, a fork to Hobbe Cave.
- **[C] Orchard Farm** - apple/cider farm with **barns**. **[B]** Orchard rows (flowering oak), a farmhouse + barns, cider barrels.
- **[C] Fisher Creek** - a **fisherman's hut** where the creek meets the sea. **[B]** A single stilted hut, jetty, nets, the creek mouth.
- **[C] Rose Cottage** - small house with a **Demon Door in its garden**. **[B]** A cozy cottage + walled garden with rose bushes (pink/red flowers) and the carved-face door.

**[C] Hobbe Cave** - a dungeon off Greatwood Caves: dark stone tunnels, the archetypal Fable dungeon, **Hobbe-infested**. **[B]** Cramped twisting **cobblestone/deepslate** tunnels, low ceilings, scattered loot, dim.

---

## 7. DARKWOOD CLUSTER (twisted marsh forest)

**[G] Palette for the whole cluster:** murky greys and browns, **dead/twisted trees**, **fog**, standing water. Oppressive and dangerous - the tonal low point of the journey.

- **[C] Darkwood Entrance** - first area from Greatwood Caves. **[B]** A gloomy threshold clearing where bright forest gives way to dead trees and mist.
- **[C] Darkwood Marshes** - boggy, foggy wetland. **[B]** Shallow **mud/water** flats, dead bushes, fog (use lots of low foliage removed + dark palette), patches of **podzol/mud**.
- **[C] Darkwood Lake** - dark water. **[B]** A black-looking lake (dark bed, low light), dead snags rising from it.
- **[C] Darkwood Camp** - a small **fenced merchant sanctuary** (one of only two safe spots). **[B]** A palisade ring with a campfire, a trader stall, a couple of tents - a warm pocket in the gloom.
- **[C] Darkwood Bordello (TLC only)** - a safe-haven building with a **Demon Door**; can be run for profit or converted to a women's refuge. **[B]** A lit two-storey timber building standing out against the marsh; carved-face door.
- **[C] Darkwood Weir** - a weir on the water. **[B]** A low dam/sluice of stone + timber across a channel.
- **[C] Ancient Cullis Gate** - teleporter. **[B]** An older, more overgrown Cullis Gate disc (mossy, cracked ring).
- **[C] Chapel of Skorm** - evil sacrificial altar. **[B]** A grim shrine: blackstone altar, dripping candles/soul-fire, bone detailing, a sacrificial brazier.

### Connections [C]
Darkwood Entrance <- Greatwood Caves; Ancient Cullis Gate / paths -> Barrow Fields -> Oakvale.

---

## 8. WITCHWOOD CLUSTER + THE ARENA (misty island)

**[G] Palette:** misty **evergreen** - spruce forest, fog, damp greens and greys, standing stones.

- **[C] Witchwood Cullis Gate** - arrival teleporter from the mainland.
- **[C] Witchwood Stones** - **Old Kingdom standing stones / "singing stones"** that spell a Demon Door's name ("HITS"); the **Witchwood Cavern** lies behind that Demon Door. **[B]** A ring/avenue of tall **stone monoliths** (chiseled stone-brick/andesite), a few inscribed; the carved-face door set into rock.
- **[C] Temple of Avo** - a small **good-aligned** temple with a **circular donation fountain** and **two black-robed acolytes**. **[B]** A clean light-stone shrine (smooth stone / quartz accents), a round fountain centerpiece, candles, a calm sacred feel.
- **[C] Witchwood Lake** - small shallow lake between Knothole Glade, the Arena Entrance, and the Temple. **[B]** A shallow clear pool, lily pads, connecting paths.

### The Arena (Witchwood Arena) [C]
A giant **Roman-style Colosseum** commissioned by Nostro - a large circular amphitheater with **tiered spectator seating** and **statues looking down into the arena floor**. The **Arena Entrance** is a path where crowds gather (with a title vendor); the **Waiting Area** has practice dummies + a supply shop; the **Hall of Heroes** adjoins it. Eight rounds of combat take place in the central ring.
- **[B] Build:** an **oval/round colosseum, ~40-50 across** at the floor, **tiered stone-brick seating** rising on all sides, **arched entries** around the perimeter, **hero statues on the upper rim** looking inward, a sand combat floor, gated combatant tunnels. This is a hero landmark - make it monumental.

### Connections [C]
Cullis Gate -> Stones -> Temple / Lake -> Knothole Glade and Arena Entrance -> Arena -> Hall of Heroes.

---

## 9. LYCHFIELD + BARGATE CLUSTER (graveyards + the prison)

**[G] Palette:** decayed grey-green - dead vegetation, fog, crumbling stone, standing water. Gothic and bleak; endless undead.

- **[C] Lychfield Graveyard** - north of Bowerstone: **crypts, sarcophagi, tombstones**, pools of water, a **Gravekeeper's hut**, and **Nostro's crypt**. A **Demon Door at the gate stairs** guards the only access onward and opens **only at Nostro's command**. **[B]** A sprawling necropolis of **mossy stone-brick crypts**, leaning tombstones, iron-bar gates, the gravekeeper's shack, the carved-face door on a stair.
- **[C] Old Graveyard Path** - dead vegetation, rotten air. **[B]** A fog-choked trail between graves, bare trees, broken walls.
- **[C] Circle of the Dead** - a **ritual circle** where undead spawn. **[B]** A stone ring inlaid in the ground, runes, a sacrificial/summoning feel.
- **[C] Underground Chamber / Tunnel / Passage** - lead toward Bargate. **[B]** Cramped **mossy stone** catacombs, coffin niches, dripping water.

### Bargate Prison [C]
On an **isolated northern island** - a stone fortress-prison: a **courtyard, ramparts, three cell blocks (two explorable), a barracks, a torture chamber, and the warden's office**, all bearing **Bowerstone crests**. An **Underground Chamber** beneath once held a Kraken.
- **[B] Build:** a grim square **stone-brick keep** with high crenellated walls, a central courtyard, barred cell rows (iron bars + stone cells), guard barracks, a torture room (cages, chains), the warden's office up top; Bowerstone banners/crests on the walls. Bleak grey, minimal light, water below.

### Other connective Bargate-region zones [C]
**Cliffside Path**, **Windmill Hill** (with a **windmill** - build a working-look mill: stone base, spruce cap, sail arms), **Headsman's Hill**, **Headsman's Cave**, **Gibbet Woods** (hang gibbet-cages from trees for flavor), **Prison Path**.

---

## 10. BANDIT / TWINBLADE CLUSTER

**[C]** Reached via Oakvale's **Clifftop Path** and the **Abandoned Road**. A sprawl of **bandit tents and palisades by a lake**, with **three stalls** and a small **makeshift tavern**, progressing inward through **gated checkpoints**: Twinblade's Camp -> **Twinblade's Elite Camp** -> **Twinblade's Tent** (the Bandit King's large tent, with a **fighting circle surrounded by bandits** and chests inside).
- **[B] Build:** rough **wooden-fence palisades** and **hide tents** (wool/leather-look canvas over frames), **campfires**, watch platforms, crude gates between rings. Twinblade's Tent = an oversized command tent with a central dirt **fighting circle**. Palette: brown hide + wood + firelight + lakeside mud.
- **[C] Abandoned Road** - the derelict approach. **[B]** A broken, overgrown road with wrecked carts and ambush cover.

---

## 11. CONNECTIVE / MISC

- **[C] Grey House (+ cellar)** - a house in the Oakvale area tied to Lady Grey's backstory; scene of undead in the Murder/Investigating-the-Mayor questline. **[B]** An isolated, slightly sinister manor-cottage with a **stone cellar** (coffins, undead), set apart from town.
- **[C] Picnic Area / Barrow Fields / Memorial Garden / Darkwood Weir interiors** - small connective sub-zones with minimal documented detail. **[B]** Treat as **small filler areas** (a meadow with benches; open fields; the walled graveyard already covered) that bridge the major zones - keep them short and atmospheric rather than landmark builds.

---

## 12. NORTHERN WASTES CLUSTER - TLC ONLY (frozen north)

**[G] Palette for the whole cluster:** snow-white + slate-blue + grey stone, **constant blizzard**, packed ice, desolation - except **Archon's Folly**, which flips to volcanic reds/blacks.

- **[C] Lost Bay** - the **arrival port** from the Ship of the Drowned: a long-disused **snow-covered harbor** with an **abandoned building**, **ruined docks**, a **30-key Silver Chest**, and a **statue commemorating Archon's ancient soldiers**. The "northernmost port of the Old Kingdom." **[B]** Frozen jetties (packed/blue ice at the waterline), a half-collapsed warehouse, the soldier statue on a plinth, the distinctive silver chest as a landmark.
- **[C] Northern Wastes Foothills** - hills under **constant blizzard** leading up from Lost Bay, **splitting toward the Necropolis and Snowspire**; balverine-infested. The **northernmost gate** leads to the Necropolis. **[B]** Snow-blasted slopes (snow blocks + layers), sparse dead trees, a branching mountain pass, low visibility.
- **[C] Necropolis** - a **haunted ruined ghost-city**: once a thriving Old Kingdom town, now **rubble** - crumbling buildings, graves, a **broken bridge over a river**, roaming **ghosts** (who murmur, unaware they're dead) and zombies, plus Frost Balverines, Wraiths, an ice troll. The four **Glyphs of Inquiry** are dug up here. **[B]** A frozen gothic ruin-city: roofless **stone-brick shells**, snow-buried streets, a **snapped bridge** over a frozen river, graves and crypts throughout. Desolate and cold. *(Lore note [C]: Snowspire and the Necropolis were originally meant to be separate islands - build them as distinctly separate zones.)*
- **[C] Archon's Shrine** - a region between the Foothills and Snowspire dominated by a **large domed shrine**; the Hero places **three Hero souls into stones** in its center to open the adjacent **Bronze Gate**. Contains a Cullis Gate and chests; a plaque ties it to the **Kingdom of Archon** and the mystic locking of the gate. **[B]** A big stepped **domed temple** (stone brick + smooth stone dome), three soul-stone sockets in the central floor, the Cullis Gate disc, ancient inscriptions.
- **[C] Bronze Gate** - a **huge ancient door**, the northernmost barrier; legend says opening it brings the end of the world. Requires three Hero souls. Entrance to the final boss area. **[B]** A monumental **bronze/copper double door** (weathered copper blocks, oxidized accents) set in a massive stone frame - the most imposing gateway in the build.
- **[C] Snowspire Village** - the only remaining settlement in the Wastes; **similar in feel to Hook Coast**. Reduced over centuries from a great city to a village. Weapons illegal (guarded town). Has a **Charity Shop**, a buyable house, villagers, and at the far side the **Oracle** - an **enormous ancient stone monument/face carved from a giant slab of rock** that answers the Hero's questions. **[B]** A small snowbound village (snow-roofed stone + weathered timber, like Hook Coast), tiered, with the **colossal carved-stone Oracle face** built into the cliff at the far end as the showpiece - make it genuinely huge (a multi-storey carved visage).
- **[C] Archon's Folly (Dragon Cliff)** - the **northernmost point of Albion**, behind the Bronze Gate: the **final-boss arena**. A **medium rock platform surrounded by lava** in an infernal volcanic setting; here the Hero fights Jack's dragon form and chooses whether to cast the mask into the lava. **[B]** A circular **blackstone/basalt platform ringed by a lava lake**, glowing fissures, ash, jagged volcanic spires - total tonal flip from the surrounding ice. Fiery reds, blacks, molten glow.

### Connections [C]
Lighthouse (Hook Coast) -> Ship of the Drowned -> **Lost Bay** -> Foothills -> {Necropolis / Archon's Shrine -> Bronze Gate -> Archon's Folly / Snowspire}.

---

## 13. Recommended build order & fidelity

1. **Guild first** (see the sample spec) - most documented, most recognizable, sets your Cullis Gate + grey-stone vocabulary.
2. **The four other hubs** to lock in distinct architectural languages: coastal-cottage (Oakvale), Tudor-urban (Bowerstone), Norse-Celtic wood (Knothole Glade), Old-Kingdom-snow (Hook Coast).
3. **One region per cluster** next, each in its signature palette, so the world reads as distinct zones: bright-green (Greatwood), murky-fog (Darkwood), misty-evergreen (Witchwood), decayed-grey (Lychfield), and snow-white (Northern Wastes), with the volcanic Archon's Folly as the finale.
4. **Keep the loading-zone structure**: distinct gateway structures (stone arch / wooden gate / Cullis Gate disc) at every transition preserve the original connectivity.
5. **Verify [G] lines against screenshots** before committing large builds - strongest need on the minor and TLC regions in the back half.

## Caveats
- Layout facts ([C]) are reliable; atmospheric flourishes from wiki prose are interpretive.
- Decorative heraldry (banners, stained glass) is **not** source-confirmed and is discretionary.
- Building counts/proportions differ between childhood vs. rebuilt Oakvale and between TLC (2005) and the Anniversary remaster (2014); this targets the **2005 TLC** state.
- All **[B]** dimensions and block choices are starting points, not canon - tune to taste and to your mod's scale.

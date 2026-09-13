# Documentation

Two kinds of document live here, and it helps to know which you are reading.

**Guides** describe what the add-on is and how it works. They are written for
players and for anyone new to the codebase, and they are kept accurate against
the packs.

**The engineering ledger** is the working record of the TLC conformance effort:
per-room reference notes, geometry decisions, evidence trails and checkpoints.
It is written for the people doing that work, it is dense, and it is the source
of truth for what has actually been verified.

---

## Guides

Start here.

| | |
|---|---|
| [GETTING_STARTED.md](GETTING_STARTED.md) | Requirements, building, installing, your first ten minutes |
| [HERO.md](HERO.md) | Experience, training, morality, factions, crime and jail, expressions |
| [WILL.md](WILL.md) | The eighteen Will powers, casting, companions, the Will Focus |
| [FORGE.md](FORGE.md) | Materials, 58 weapons, 13 armour sets, augmentations, consumables |
| [ALBION.md](ALBION.md) | The Guild, the towns, the Cullis lattice, the Demon Doors |
| [BESTIARY.md](BESTIARY.md) | 51 creatures and NPCs, what they are worth, what killing them costs |
| [QUESTS.md](QUESTS.md) | The seven-quest main chain, six side quests, two standing jobs |
| [INTERFACE.md](INTERFACE.md) | The HUD and the eleven-page storybook menu |
| [BUILDING.md](BUILDING.md) | Generators, the 56 validation gates, contributing |
| [MEDIA.md](MEDIA.md) | What each image set is, and which images are real |

Also at the repository root:

| | |
|---|---|
| [../README.md](../README.md) | The front door |
| [../LEGAL.md](../LEGAL.md) | Fan-work notice and distribution policy |
| [../BOUNTY_SYSTEM.md](../BOUNTY_SYSTEM.md) | Full mechanical spec for crime, warrants and jail |
| [../SPELL_COMPANIONS.md](../SPELL_COMPANIONS.md) | Manual verification notes for Ghost Sword, Summon and Turncoat |
| [../FABLE_EMOTE_VALIDATION.md](../FABLE_EMOTE_VALIDATION.md) | Expression validation notes |

---

## Engineering ledger

### Start here

| | |
|---|---|
| [HANDOFF.md](HANDOFF.md) | The current continuation prompt and checkpoint |
| [GUILD_DEMON_PRIORITIES.md](GUILD_DEMON_PRIORITIES.md) | The active GP/DP execution queue |
| [CONFORMANCE_CHECKLIST.md](CONFORMANCE_CHECKLIST.md) | Leaf rows, status, evidence, grades |
| [CONFORMANCE_PLAN.md](CONFORMANCE_PLAN.md) | The playbook: recipes, acceptance, evidence policy |
| [SCORING.md](SCORING.md) · [SOURCE_PLAN.md](SOURCE_PLAN.md) | How conformance is scored and sourced |

### Process and tooling

| | |
|---|---|
| [CI.md](CI.md) | The validation workflow and its pins |
| [AUDIT_TOOLING.md](AUDIT_TOOLING.md) | The audit scripts and what each one proves |
| [STRUCTURE_CONTRACT.md](STRUCTURE_CONTRACT.md) | The contract every generated structure must satisfy |
| [BRANDING.md](BRANDING.md) · [BRANDING_DEBT.md](BRANDING_DEBT.md) | Faithful and original naming modes |
| [RUNTIME_NAMING.md](RUNTIME_NAMING.md) · [RELEASE_SCANNING.md](RELEASE_SCANNING.md) | Runtime strings and the release scanner |
| [ANIMATION_AUDIT.md](ANIMATION_AUDIT.md) | Animation coverage across the roster |

### The Guild

| | |
|---|---|
| [GUILD_GEOMETRY_AUDIT.md](GUILD_GEOMETRY_AUDIT.md) · [GUILD_CIRCULATION.md](GUILD_CIRCULATION.md) · [GUILD_HALL_LINKS.md](GUILD_HALL_LINKS.md) | Whole-building geometry and routing |
| [GUILD_ONLINE_REFERENCES.md](GUILD_ONLINE_REFERENCES.md) | Original TLC reference material and its provenance |
| [GUILD_MAP_TABLE.md](GUILD_MAP_TABLE.md) · [GUILD_LIBRARY_INTERIOR.md](GUILD_LIBRARY_INTERIOR.md) · [GUILD_MAZE_STUDY.md](GUILD_MAZE_STUDY.md) | Map Room, Library, Maze's study |
| [GUILD_CHAMBER_INTERIOR.md](GUILD_CHAMBER_INTERIOR.md) · [GUILD_CHAMBER_NEUTRAL_DETAILS.md](GUILD_CHAMBER_NEUTRAL_DETAILS.md) | The Chamber of Fate |
| [GUILD_DORM_STAIRS.md](GUILD_DORM_STAIRS.md) · [GUILD_DORM_WALL_BAY.md](GUILD_DORM_WALL_BAY.md) · [GUILD_DINING_SEATS.md](GUILD_DINING_SEATS.md) | Dormitory and dining hall |
| [GUILD_ARCHERY_BACKBOARD.md](GUILD_ARCHERY_BACKBOARD.md) · [GUILD_ARCHERY_SCENERY.md](GUILD_ARCHERY_SCENERY.md) · [GUILD_ARCHERY_FIRING_DIVIDER.md](GUILD_ARCHERY_FIRING_DIVIDER.md) | The archery range |
| [GUILD_TRAINING.md](GUILD_TRAINING.md) · [GUILD_WILL_TRAINING.md](GUILD_WILL_TRAINING.md) · [GUILD_SKILL_PREFLIGHT.md](GUILD_SKILL_PREFLIGHT.md) | Training grounds and shrines |
| [GUILD_RESIDENTS.md](GUILD_RESIDENTS.md) · [GUILD_NPC_AUDIT.md](GUILD_NPC_AUDIT.md) · [GUILD_ACTIVITY_OWNERSHIP.md](GUILD_ACTIVITY_OWNERSHIP.md) · [GUILD_RELATIONSHIP_AUTHORITY.md](GUILD_RELATIONSHIP_AUTHORITY.md) | Who lives there and what they do |
| [GUILD_DEFENCE.md](GUILD_DEFENCE.md) · [GUILD_MAINTENANCE.md](GUILD_MAINTENANCE.md) · [GUILD_BRIDGE_LAMPS.md](GUILD_BRIDGE_LAMPS.md) | Defence, upkeep, lighting |
| [GUILD_CAVE_LIFECYCLE.md](GUILD_CAVE_LIFECYCLE.md) · [GUILD_CAVE_REVIEW.md](GUILD_CAVE_REVIEW.md) | The Guild caves |

### Demon Doors and reward worlds

| | |
|---|---|
| [DEMON_DOOR_DESIGN.md](DEMON_DOOR_DESIGN.md) · [DEMON_DOOR_TICK_ISOLATION.md](DEMON_DOOR_TICK_ISOLATION.md) | Portal design and runtime isolation |
| [LIBRARY_ARCANUM.md](LIBRARY_ARCANUM.md) and its preparation, protections, recovery, source-authority, reference-review and ticket-read notes | The Guild door's reward world |
| [ARBORETUM.md](ARBORETUM.md) · [ARBORETUM_PREPARATION.md](ARBORETUM_PREPARATION.md) | The Greatwood Gorge door's reward world |

### Places

| | |
|---|---|
| [CULLIS_GATE.md](CULLIS_GATE.md) | Focus Sites and the travel lattice |
| [BOWERSTONE_NORTH.md](BOWERSTONE_NORTH.md) · [OAKVALE_MEMORIAL.md](OAKVALE_MEMORIAL.md) · [HOOK_COAST.md](HOOK_COAST.md) · [GREY_HOUSE.md](GREY_HOUSE.md) | Towns and houses |
| [ARENA_HALLS.md](ARENA_HALLS.md) · [BARGATE_PRISON.md](BARGATE_PRISON.md) · [LYCHFIELD_CRYPT.md](LYCHFIELD_CRYPT.md) · [TWINBLADE_CAMP.md](TWINBLADE_CAMP.md) | Arena, prison, crypt, war-camp |
| [ARCHON_SHRINE.md](ARCHON_SHRINE.md) · [ARCHON_FOLLY.md](ARCHON_FOLLY.md) · [GREATWOOD_GORGE.md](GREATWOOD_GORGE.md) | The Archon's monuments and the gorge |

---

## Keeping this accurate

The guides make factual claims — counts, costs, thresholds, ranges — and those
came from the packs, not from memory. If you change the data, change the guide.
The numbers worth re-checking after a data change are in
`packs/Fablecraft_BP/scripts/fc_gamedata.js` (weapons, armour, spells, quests,
Demon Doors, augments, kill tables), `scripts/structure_manifest.json`
(structure count and sizes) and the two pack manifests (version and minimum
engine).

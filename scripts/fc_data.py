"""fc_data.py — master content definitions for Fablecraft: Reforged.

Single source of truth. Every generator (textures, behavior pack, resource
pack, scripts data, screenshots) reads from here.

Damage/armor numbers carry both the *Fable* stat (lore-accurate, shown in
names/log) and the scaled Minecraft stat actually applied in-game.
"""
from fc_lib import title_case

NS = "fc"

# ---------------------------------------------------------------------------
# WEAPONS
# ---------------------------------------------------------------------------

MATERIALS = {
    # base fable damage, augment slots, gold value mult, durability
    "iron":     {"base": 18, "slots": 0, "value": 150,   "dur": 251,  "tier": 1},
    "steel":    {"base": 34, "slots": 1, "value": 450,   "dur": 451,  "tier": 2},
    "obsidian": {"base": 60, "slots": 2, "value": 2500,  "dur": 801,  "tier": 3},
    "master":   {"base": 90, "slots": 3, "value": 20000, "dur": 1401, "tier": 4},
}

WEAPON_TYPES = {
    # factor = damage multiplier, speed = lore attack speed, kind for icon art
    "longsword":   {"factor": 1.50, "speed": "fast",      "kind": "sword"},
    "katana":      {"factor": 1.17, "speed": "very fast", "kind": "katana"},
    "cleaver":     {"factor": 1.40, "speed": "fast",      "kind": "cleaver"},
    "axe":         {"factor": 1.60, "speed": "medium",    "kind": "axe"},
    "mace":        {"factor": 1.55, "speed": "medium",    "kind": "mace"},
    "pickhammer":  {"factor": 1.65, "speed": "medium",    "kind": "pickhammer"},
    "greataxe":    {"factor": 2.00, "speed": "slow",      "kind": "greataxe"},
    "greatsword":  {"factor": 1.90, "speed": "slow",      "kind": "greatsword"},
    "greathammer": {"factor": 2.25, "speed": "very slow", "kind": "greathammer"},
}

RANGED_TYPES = {
    "longbow":  {"kind": "bow",      "speed": "medium"},
    "crossbow": {"kind": "crossbow", "speed": "slow"},
}
RANGED_MATERIALS = {
    "yew":   {"base": 22, "slots": 0, "value": 200,   "dur": 301,  "tier": 1},
    "oak":   {"base": 38, "slots": 1, "value": 700,   "dur": 501,  "tier": 2},
    "ebony": {"base": 65, "slots": 2, "value": 3200,  "dur": 901,  "tier": 3},
    "master": {"base": 95, "slots": 3, "value": 24000, "dur": 1501, "tier": 4},
}


def mc_damage(fable):
    return min(26, round(3 + fable / 10))


def build_weapons():
    out = []
    for mat, m in MATERIALS.items():
        for wtype, t in WEAPON_TYPES.items():
            fable = round(m["base"] * t["factor"])
            out.append({
                "id": f"{mat}_{wtype}",
                "name": f"{title_case(mat)} {title_case(wtype)}",
                "cat": "melee",
                "kind": t["kind"],
                "material": mat,
                "wtype": wtype,
                "fable_damage": fable,
                "damage": mc_damage(fable),
                "slots": m["slots"],
                "value": round(m["value"] * t["factor"]),
                "durability": m["dur"],
                "speed": t["speed"],
                "two_handed": wtype.startswith("great"),
            })
    for mat, m in RANGED_MATERIALS.items():
        for wtype, t in RANGED_TYPES.items():
            fable = round(m["base"] * (1.35 if wtype == "crossbow" else 1.0))
            out.append({
                "id": f"{mat}_{wtype}",
                "name": f"{title_case(mat)} {title_case(wtype)}",
                "cat": "ranged",
                "kind": t["kind"],
                "material": mat,
                "wtype": wtype,
                "fable_damage": fable,
                "damage": mc_damage(fable),
                "slots": m["slots"],
                "value": round(m["value"] * 1.1),
                "durability": m["dur"],
                "speed": t["speed"],
                "two_handed": True,
            })
    return out


LEGENDARIES = [
    # id, name, kind(for art), fable dmg, built-in augments, lore source
    {"id": "sword_of_aeons", "name": "Sword of Aeons", "kind": "aeons", "fable_damage": 230,
     "augments": ["health", "mana", "sharpening"], "ranged": False,
     "lore": "Forged in the void by Jack of Blades. It hungers."},
    {"id": "avos_tear", "name": "Avo's Tear", "kind": "avos_tear", "fable_damage": 230,
     "augments": ["health", "mana", "sharpening"], "ranged": False,
     "lore": "Born of light the instant the Sword of Aeons was destroyed."},
    {"id": "the_harbinger", "name": "The Harbinger", "kind": "greatsword_legend", "fable_damage": 180,
     "augments": ["silver", "health"], "ranged": False,
     "lore": "Drawn from the stone at the Temple of Avo by a true Hero."},
    {"id": "solus_greatsword", "name": "Solus Greatsword", "kind": "greatsword_legend", "fable_damage": 190,
     "augments": ["flame"], "ranged": False,
     "lore": "The brightest blade in Albion, heavy as a setting sun."},
    {"id": "arkens_crossbow", "name": "Arken's Crossbow", "kind": "crossbow_legend", "fable_damage": 220,
     "augments": ["piercing", "lightning"], "ranged": True,
     "lore": "The shipwright's pride, lost beneath Darkwood Lake."},
    {"id": "the_bereaver", "name": "The Bereaver", "kind": "greatsword_legend", "fable_damage": 190,
     "augments": ["sharpening", "experience"], "ranged": False,
     "lore": "Taken from the grasp of a hundred grieving ghosts."},
    {"id": "avenger", "name": "Avenger", "kind": "katana_legend", "fable_damage": 180,
     "augments": ["sharpening", "health"], "ranged": False,
     "lore": "A katana folded ten thousand times by the last smith of the North."},
    {"id": "orkons_club", "name": "Orkon's Club", "kind": "greathammer_legend", "fable_damage": 150,
     "augments": ["flame"], "ranged": False,
     "lore": "Orkon never needed a second swing."},
    {"id": "dollmasters_mace", "name": "Dollmaster's Mace", "kind": "mace_legend", "fable_damage": 160,
     "augments": ["mana", "lightning"], "ranged": False,
     "lore": "Its puppets dance even now, somewhere beneath the marsh."},
    {"id": "wellows_pickhammer", "name": "Wellow's Pickhammer", "kind": "pickhammer_legend", "fable_damage": 142,
     "augments": ["piercing", "experience"], "ranged": False,
     "lore": "Dug too deep, found too much. Reward of the Arboretum Door."},
    {"id": "katana_hiryu", "name": "Katana Hiryu", "kind": "katana_legend", "fable_damage": 155,
     "augments": ["health"], "ranged": False,
     "lore": "The Flying Dragon. Lady Grey keeps its scabbard under her bed."},
    {"id": "the_avenger_bow", "name": "Skorm's Bow", "kind": "bow_legend", "fable_damage": 185,
     "augments": ["silver", "experience"], "ranged": True,
     "lore": "A gift for the faithful of the Chapel of Skorm. It drinks light."},
    {"id": "scimitar", "name": "Scimitar", "kind": "scimitar", "fable_damage": 112,
     "augments": [], "ranged": False,
     "lore": "A fast curved blade favoured by Bowerstone duellists."},
    {"id": "stick", "name": "Stick", "kind": "stick", "fable_damage": 20,
     "augments": [], "ranged": False,
     "lore": "Every legend starts somewhere."},
]


def build_legendaries():
    out = []
    for l in LEGENDARIES:
        out.append({
            "id": l["id"], "name": l["name"], "cat": "ranged" if l["ranged"] else "melee",
            "kind": l["kind"], "material": "legendary", "wtype": "legendary",
            "fable_damage": l["fable_damage"], "damage": mc_damage(l["fable_damage"]),
            "slots": 0, "augments": l["augments"], "value": 45000,
            "durability": 2201 if l["fable_damage"] > 100 else 131,
            "speed": "varies", "two_handed": "great" in l["kind"], "lore": l["lore"],
        })
    return out


# ---------------------------------------------------------------------------
# AUGMENTS
# ---------------------------------------------------------------------------

AUGMENTS = [
    {"id": "sharpening_augment", "name": "Sharpening Augmentation", "color": (212, 60, 38),
     "desc": "+25% damage dealt by this weapon."},
    {"id": "piercing_augment", "name": "Piercing Augmentation", "color": (200, 200, 215),
     "desc": "Ignores a portion of enemy armour."},
    {"id": "health_augment", "name": "Health Augmentation", "color": (190, 30, 50),
     "desc": "Restores health with every blow."},
    {"id": "mana_augment", "name": "Mana Augmentation", "color": (40, 90, 220),
     "desc": "Restores Will energy with every blow."},
    {"id": "experience_augment", "name": "Experience Augmentation", "color": (70, 200, 90),
     "desc": "Earn bonus experience from each kill."},
    {"id": "lightning_augment", "name": "Lightning Augmentation", "color": (120, 170, 255),
     "desc": "Shocks struck enemies with chain lightning."},
    {"id": "flame_augment", "name": "Flame Augmentation", "color": (255, 130, 30),
     "desc": "Sets struck enemies ablaze."},
    {"id": "silver_augment", "name": "Silver Augmentation", "color": (235, 240, 250),
     "desc": "Bonus damage against Balverines, Undead and the supernatural."},
    {"id": "augment_remover", "name": "Augment Remover", "color": (140, 90, 200),
     "desc": "Strips all augmentations from a weapon. The augments are lost."},
]

# ---------------------------------------------------------------------------
# ARMOR
# ---------------------------------------------------------------------------

ARMOR_SLOTS = ["helm", "torso", "legs", "boots"]
SLOT_MC = {"helm": "slot.armor.head", "torso": "slot.armor.chest",
           "legs": "slot.armor.legs", "boots": "slot.armor.feet"}
SLOT_SHARE = {"helm": 0.20, "torso": 0.35, "legs": 0.30, "boots": 0.15}

ARMOR_SETS = [
    # palette: base cloth/metal colour, trim colour
    {"id": "apprentice", "name": "Apprentice", "fable_armor": 30, "align": 0,
     "attract": 0, "scary": 0, "value": 80,
     "palette": {"base": (226, 228, 234), "trim": (146, 156, 172),
                  "accent": (148, 190, 224), "metal": False, "hood": True}},
    {"id": "villager", "name": "Villager", "fable_armor": 20, "align": 0,
     "attract": 5, "scary": 0, "value": 60,
     "palette": {"base": (146, 110, 72), "trim": (94, 70, 46), "metal": False}},
    {"id": "leather_bright", "name": "Bright Leather", "fable_armor": 100, "align": 1,
     "attract": 15, "scary": 0, "value": 600,
     "palette": {"base": (172, 128, 70), "trim": (220, 196, 140), "metal": False}},
    {"id": "leather_dark", "name": "Dark Leather", "fable_armor": 100, "align": -1,
     "attract": 0, "scary": 15, "value": 600,
     "palette": {"base": (74, 58, 48), "trim": (30, 24, 22), "metal": False}},
    {"id": "chainmail_bright", "name": "Bright Chainmail", "fable_armor": 180, "align": 1,
     "attract": 10, "scary": 0, "value": 1800,
     "palette": {"base": (168, 178, 192), "trim": (230, 220, 170), "metal": True}},
    {"id": "chainmail_dark", "name": "Dark Chainmail", "fable_armor": 180, "align": -1,
     "attract": 0, "scary": 10, "value": 1800,
     "palette": {"base": (88, 92, 104), "trim": (40, 38, 44), "metal": True}},
    {"id": "platemail", "name": "Platemail", "fable_armor": 300, "align": 0,
     "attract": 5, "scary": 5, "value": 9000,
     "palette": {"base": (190, 198, 210), "trim": (120, 126, 140), "metal": True}},
    {"id": "guard_bowerstone", "name": "Bowerstone Guard", "fable_armor": 220, "align": 0,
     "attract": 5, "scary": 5, "value": 2400,
     "palette": {"base": (52, 70, 140), "trim": (200, 180, 90), "metal": True}},
    {"id": "guard_oakvale", "name": "Oakvale Guard", "fable_armor": 200, "align": 0,
     "attract": 5, "scary": 5, "value": 2200,
     "palette": {"base": (150, 44, 40), "trim": (210, 190, 120), "metal": True}},
    {"id": "guard_snowspire", "name": "Snowspire Guard", "fable_armor": 260, "align": 0,
     "attract": 5, "scary": 5, "value": 3200,
     "palette": {"base": (200, 110, 36), "trim": (240, 230, 220), "metal": True}},
    {"id": "assassin", "name": "Assassin", "fable_armor": 150, "align": -1,
     "attract": 0, "scary": 25, "value": 4200, "no_helm": False,
     "palette": {"base": (44, 40, 50), "trim": (110, 30, 36), "metal": False, "hood": True}},
    {"id": "fire_assassin", "name": "Fire Assassin", "fable_armor": 160, "align": -1,
     "attract": 0, "scary": 30, "value": 5200,
     "palette": {"base": (84, 26, 24), "trim": (250, 120, 40), "metal": False, "hood": True}},
    {"id": "archon", "name": "Archon's Battle Armour", "fable_armor": 350, "align": 1,
     "attract": 30, "scary": 0, "value": 38000,
     "palette": {"base": (224, 228, 240), "trim": (250, 210, 110), "metal": True}},
]

HATS = [
    {"id": "holy_warrior_helm", "name": "Holy Warrior Helm", "fable_armor": 70, "align": 1,
     "attract": 20, "scary": 0, "value": 6000,
     "palette": {"base": (235, 230, 215), "trim": (250, 210, 110), "metal": True}},
    {"id": "demon_helm", "name": "Demon Helm", "fable_armor": 70, "align": -1,
     "attract": 0, "scary": 35, "value": 6000, "horns": True,
     "palette": {"base": (60, 30, 34), "trim": (200, 60, 40), "metal": True}},
    {"id": "pimp_hat", "name": "Pimp Hat", "fable_armor": 5, "align": 0,
     "attract": 40, "scary": 0, "value": 1500, "brim": True,
     "palette": {"base": (110, 40, 130), "trim": (240, 220, 120), "metal": False}},
    {"id": "wizard_hat", "name": "Wizard Hat", "fable_armor": 10, "align": 0,
     "attract": 5, "scary": 5, "value": 900, "brim": True,
     "palette": {"base": (60, 70, 130), "trim": (180, 180, 220), "metal": False}},
    {"id": "bright_wizard_hat", "name": "Bright Wizard Hat", "fable_armor": 10, "align": 1,
     "attract": 15, "scary": 0, "value": 1200, "brim": True,
     "palette": {"base": (210, 200, 160), "trim": (250, 230, 140), "metal": False}},
    {"id": "dark_wizard_hat", "name": "Dark Wizard Hat", "fable_armor": 10, "align": -1,
     "attract": 0, "scary": 15, "value": 1200, "brim": True,
     "palette": {"base": (38, 32, 46), "trim": (120, 60, 160), "metal": False}},
]


def build_armor():
    out = []
    scale = 20 / 350  # Archon (350) maps to full 20 armour points
    for s in ARMOR_SETS:
        total = max(1, round(s["fable_armor"] * scale))
        for slot in ARMOR_SLOTS:
            prot = max(1, round(total * SLOT_SHARE[slot]))
            out.append({
                "id": f"{s['id']}_{slot}",
                "name": f"{s['name']} {title_case(slot)}",
                "cat": "armor", "set": s["id"], "slot": slot,
                "protection": prot, "align": s["align"],
                "attract": s["attract"], "scary": s["scary"],
                "value": round(s["value"] / 4),
                "palette": s["palette"],
                "durability": 200 + s["fable_armor"] * 2,
            })
    for h in HATS:
        out.append({
            "id": h["id"], "name": h["name"], "cat": "armor", "set": h["id"],
            "slot": "helm", "protection": max(1, round(h["fable_armor"] * scale)),
            "align": h["align"], "attract": h["attract"], "scary": h["scary"],
            "value": h["value"], "palette": h["palette"],
            "durability": 300, "hat": True,
            "brim": h.get("brim", False), "horns": h.get("horns", False),
        })
    return out


# ---------------------------------------------------------------------------
# CONSUMABLES & MISC
# ---------------------------------------------------------------------------

CONSUMABLES = [
    {"id": "health_potion", "name": "Health Potion", "kind": "flask",
     "color": (200, 40, 50), "heal": 8, "will": 0, "value": 100},
    {"id": "great_health_potion", "name": "Great Health Potion", "kind": "flask_large",
     "color": (230, 30, 60), "heal": 20, "will": 0, "value": 600},
    {"id": "will_potion", "name": "Will Potion", "kind": "flask",
     "color": (50, 90, 230), "heal": 0, "will": 40, "value": 120},
    {"id": "great_will_potion", "name": "Great Will Potion", "kind": "flask_large",
     "color": (80, 60, 240), "heal": 0, "will": 100, "value": 700},
    {"id": "resurrection_phial", "name": "Resurrection Phial", "kind": "phial",
     "color": (255, 215, 130), "heal": 40, "will": 100, "value": 6000,
     "desc": "Cheats death once. Consumed automatically at the brink."},
    {"id": "ages_of_might_potion", "name": "Ages of Might Potion", "kind": "phial",
     "color": (220, 60, 40), "xp": "strength", "xp_amount": 500, "value": 3000},
    {"id": "ages_of_skill_potion", "name": "Ages of Skill Potion", "kind": "phial",
     "color": (240, 200, 60), "xp": "skill", "xp_amount": 500, "value": 3000},
    {"id": "ages_of_will_potion", "name": "Ages of Will Potion", "kind": "phial",
     "color": (60, 110, 240), "xp": "will", "xp_amount": 500, "value": 3000},
    {"id": "elixir_of_life", "name": "Elixir of Life", "kind": "phial",
     "color": (130, 240, 160), "heal": 40, "max_hp": 2, "value": 12000,
     "desc": "Permanently increases maximum health."},
    {"id": "crunchy_chick", "name": "Crunchy Chick", "kind": "food",
     "color": (240, 220, 90), "food": 2, "morality": -15, "value": 30,
     "desc": "Still cheeping. You monster."},
    {"id": "tofu", "name": "Tofu", "kind": "food",
     "color": (240, 238, 220), "food": 3, "morality": 5, "value": 25},
    {"id": "red_meat", "name": "Red Meat", "kind": "food",
     "color": (190, 60, 50), "food": 8, "morality": 0, "value": 40},
    {"id": "apple_pie", "name": "Apple Pie", "kind": "pie",
     "color": (220, 170, 90), "food": 10, "morality": 0, "value": 60},
    {"id": "golden_carrot_brew", "name": "Hobbe Tooth Ale", "kind": "tankard",
     "color": (200, 150, 60), "food": 4, "morality": 0, "value": 35,
     "desc": "Brewed in Bowerstone. Do not ask what the bits are."},
]

MISC_ITEMS = [
    {"id": "gold_coin", "name": "Gold Coin", "kind": "coin", "stack": 64,
     "color": (250, 210, 90), "value": 1},
    {"id": "silver_key", "name": "Silver Key", "kind": "key", "stack": 64,
     "color": (220, 228, 240), "value": 500},
    {"id": "septimal_key", "name": "Septimal Key", "kind": "key_ornate", "stack": 1,
     "color": (160, 90, 220), "value": 10000,
     "desc": "Hums near Focus Sites. Required to awaken the Sword of Aeons."},
    {"id": "guild_seal", "name": "Guild Seal", "kind": "seal", "stack": 1,
     "color": (90, 140, 230), "value": 0,
     "desc": "Sneak-use: recall to the Heroes' Guild. Use: Hero menu."},
    {"id": "quest_card", "name": "Quest Card", "kind": "card", "stack": 16,
     "color": (208, 188, 150), "value": 0},
    {"id": "wedding_ring", "name": "Wedding Ring", "kind": "ring", "stack": 1,
     "color": (250, 220, 120), "value": 800},
    {"id": "balverine_fang", "name": "Balverine Fang", "kind": "fang", "stack": 64,
     "color": (228, 224, 210), "value": 45},
    {"id": "frost_balverine_hide", "name": "Frost Balverine Hide", "kind": "hide", "stack": 64,
     "color": (190, 220, 240), "value": 220},
    {"id": "balverine_trophy", "name": "Balverine Summoning Trophy", "kind": "trophy", "stack": 1,
     "color": (200, 200, 210), "value": 2500},
    {"id": "wasp_wing", "name": "Wasp Wing", "kind": "wing", "stack": 64,
     "color": (220, 230, 240), "value": 12},
    {"id": "queens_stinger", "name": "Queen's Stinger", "kind": "stinger", "stack": 1,
     "color": (240, 200, 70), "value": 900},
    {"id": "beetle_chitin", "name": "Beetle Chitin", "kind": "chitin", "stack": 64,
     "color": (90, 110, 70), "value": 8},
    {"id": "troll_heart", "name": "Troll Heart", "kind": "heart", "stack": 16,
     "color": (160, 70, 60), "value": 350},
    {"id": "troll_bones", "name": "Troll Bones", "kind": "bones", "stack": 64,
     "color": (225, 220, 200), "value": 60},
    {"id": "ectoplasm", "name": "Ectoplasm", "kind": "goo", "stack": 64,
     "color": (150, 240, 200), "value": 90},
    {"id": "banshees_tear", "name": "Banshee's Tear", "kind": "tear", "stack": 16,
     "color": (170, 210, 250), "value": 400},
    {"id": "scorpion_stinger", "name": "Arachanox Stinger", "kind": "stinger", "stack": 1,
     "color": (140, 90, 200), "value": 1800},
    {"id": "giants_core", "name": "Giant's Core", "kind": "core", "stack": 1,
     "color": (255, 140, 40), "value": 2200},
    {"id": "minion_flesh", "name": "Minion Flesh", "kind": "goo", "stack": 64,
     "color": (140, 60, 80), "value": 35},
    {"id": "summoners_grimoire", "name": "Summoner's Grimoire", "kind": "book", "stack": 1,
     "color": (80, 40, 120), "value": 1200},
    {"id": "jack_of_blades_mask", "name": "Mask of Jack of Blades", "kind": "mask", "stack": 1,
     "color": (190, 40, 40), "value": 66666,
     "desc": "It whispers. Do not listen."},
]

# ---------------------------------------------------------------------------
# SPELLS (Will powers)
# ---------------------------------------------------------------------------

SPELLS = [
    # will = cost at lvl1, cd = cooldown ticks, align: 1 good-only, -1 evil-only
    {"id": "enflame", "name": "Enflame", "will": 15, "cd": 50, "align": 0,
     "color": (255, 120, 30), "desc": "A ring of fire erupts around the Hero."},
    {"id": "fireball", "name": "Fireball", "will": 12, "cd": 30, "align": 0,
     "color": (255, 90, 20), "desc": "Hurl an explosive sphere of flame."},
    {"id": "lightning", "name": "Lightning", "will": 14, "cd": 35, "align": 0,
     "color": (120, 180, 255), "desc": "Arc lightning leaps between your foes."},
    {"id": "force_push", "name": "Force Push", "will": 10, "cd": 45, "align": 0,
     "color": (170, 200, 255), "desc": "A telekinetic blast hurls enemies away."},
    {"id": "drain_life", "name": "Drain Life", "will": 16, "cd": 60, "align": -1,
     "color": (180, 30, 60), "desc": "Steal the life of those around you. (-5 morality)"},
    {"id": "heal_life", "name": "Heal Life", "will": 18, "cd": 60, "align": 1,
     "color": (120, 255, 150), "desc": "Convert Will energy into vitality."},
    {"id": "physical_shield", "name": "Physical Shield", "will": 12, "cd": 100, "align": 0,
     "color": (110, 160, 255), "desc": "A shell of Will absorbs harm while your energy lasts."},
    {"id": "slow_time", "name": "Slow Time", "will": 20, "cd": 200, "align": 0,
     "color": (200, 220, 255), "desc": "The world crawls. You do not."},
    {"id": "assassin_rush", "name": "Assassin Rush", "will": 8, "cd": 40, "align": 0,
     "color": (140, 120, 200), "desc": "Blink behind your target in a streak of shadow."},
    {"id": "summon", "name": "Summon", "will": 25, "cd": 200, "align": 1,
     "color": (120, 230, 200), "desc": "Call a creature to fight at your side. (Good Heroes only)"},
    {"id": "turncoat", "name": "Turncoat", "will": 18, "cd": 160, "align": 0,
     "color": (220, 150, 240), "desc": "Bend an enemy's mind to fight for you."},
    {"id": "multi_arrow", "name": "Multi Arrow", "will": 10, "cd": 60, "align": 0,
     "color": (200, 230, 150), "desc": "Your next volley splits into a fan of arrows."},
    {"id": "multi_strike", "name": "Multi Strike", "will": 12, "cd": 120, "align": 0,
     "color": (255, 200, 90), "desc": "Briefly strike with impossible speed."},
    {"id": "battle_charge", "name": "Battle Charge", "will": 14, "cd": 80, "align": 0,
     "color": (255, 170, 60), "desc": "Charge forward, smashing all in your path."},
    {"id": "berserk", "name": "Berserk", "will": 20, "cd": 240, "align": -1,
     "color": (255, 60, 40), "desc": "Rage swells your body and dims your mind."},
    {"id": "divine_fury", "name": "Divine Fury", "will": 35, "cd": 300, "align": 1,
     "color": (255, 240, 150), "desc": "Holy radiance sears the wicked. (Good Heroes only)"},
    {"id": "infernal_wrath", "name": "Infernal Wrath", "will": 35, "cd": 300, "align": -1,
     "color": (180, 40, 200), "desc": "Darkness devours all around you. (Evil Heroes only)"},
]

# ---------------------------------------------------------------------------
# GUILD UPGRADES
# ---------------------------------------------------------------------------

UPGRADES = [
    {"id": "physique", "name": "Physique", "xp": "strength", "max": 5,
     "desc": "+melee damage, +size. Your shadow grows."},
    {"id": "health", "name": "Health", "xp": "strength", "max": 5,
     "desc": "+max health per level."},
    {"id": "toughness", "name": "Toughness", "xp": "strength", "max": 5,
     "desc": "+damage resistance."},
    {"id": "speed", "name": "Speed", "xp": "skill", "max": 5,
     "desc": "+movement and attack speed."},
    {"id": "guile", "name": "Guile", "xp": "skill", "max": 5,
     "desc": "+luck, +stealth, better trade prices."},
    {"id": "accuracy", "name": "Accuracy", "xp": "skill", "max": 5,
     "desc": "+ranged damage."},
    {"id": "magic_power", "name": "Magic Power", "xp": "will", "max": 5,
     "desc": "+max Will energy and Will regeneration."},
]


def upgrade_cost(level):
    """XP cost to buy a given level (1-based)."""
    return level * 120


# ---------------------------------------------------------------------------
# XP & MORALITY TABLES (per mob family)
# ---------------------------------------------------------------------------

KILL_XP = {
    "fc_wasp": 6, "fc_beetle": 4, "fc_hobbe": 12, "fc_bandit": 18,
    "fc_undead": 15, "fc_balverine": 35, "fc_frost_balverine": 80,
    "fc_troll": 120, "fc_wraith": 45, "fc_banshee": 60, "fc_minion": 30,
    "fc_summoner": 55, "fc_assassin": 50, "fc_boss": 400, "fc_guard": 10,
    "fc_villager": 2, "fc_nymph": 5,
}

KILL_MORALITY = {
    "fc_balverine": 8, "fc_frost_balverine": 12, "fc_undead": 6,
    "fc_wasp": 1, "fc_beetle": 0, "fc_hobbe": 3, "fc_bandit": 5,
    "fc_troll": 10, "fc_wraith": 6, "fc_banshee": 8, "fc_minion": 5,
    "fc_summoner": 6, "fc_assassin": 6, "fc_boss": 50,
    "fc_villager": -100, "fc_guard": -150, "fc_trader": -120, "fc_nymph": -20,
}

# ---------------------------------------------------------------------------
# QUESTS
# ---------------------------------------------------------------------------

QUESTS = [
    {"id": "wasp_menace", "name": "The Wasp Menace", "chain": "main", "order": 1,
     "giver": "Guildmaster", "renown": 100,
     "desc": "Wasps swarm the picnic grounds. Slay the Wasp Queen before lunch is ruined forever.",
     "objectives": [{"type": "kill", "family": "fc_wasp", "count": 8, "label": "Slay 8 Wasps"},
                    {"type": "kill", "family": "fc_wasp_queen", "count": 1, "label": "Destroy the Wasp Queen"}],
     "rewards": {"gold": 200, "xp": {"general": 200, "strength": 50}, "morality": 20,
                 "items": [{"id": "fc:health_potion", "count": 2}]},
     "next": "trader_escort"},
    {"id": "trader_escort", "name": "Trader Escort", "chain": "main", "order": 2,
     "giver": "Guildmaster", "renown": 150,
     "desc": "Traders vanish on the Darkwood road. Hunt the beasts that prey upon them.",
     "objectives": [{"type": "kill", "family": "fc_hobbe", "count": 10, "label": "Clear 10 Hobbes from the road"},
                    {"type": "kill", "family": "fc_balverine", "count": 3, "label": "Slay 3 Balverines"}],
     "rewards": {"gold": 400, "xp": {"general": 300, "strength": 80}, "morality": 100,
                 "items": [{"id": "fc:steel_longsword", "count": 1}]},
     "next": "bandit_seeress"},
    {"id": "bandit_seeress", "name": "Find the Bandit Seeress", "chain": "main", "order": 3,
     "giver": "Guildmaster", "renown": 300,
     "desc": "Twinblade's camp shelters a seeress who knows your sister's fate. Cut your way to the truth.",
     "objectives": [{"type": "kill", "family": "fc_bandit", "count": 15, "label": "Defeat 15 of Twinblade's bandits"},
                    {"type": "collect", "item": "fc:quest_card", "count": 1, "label": "Recover the camp orders"}],
     "rewards": {"gold": 800, "xp": {"general": 500, "skill": 150}, "morality": 0,
                 "items": [{"id": "fc:obsidian_longsword", "count": 1}]},
     "next": "arena_of_heroes"},
    {"id": "arena_of_heroes", "name": "The Arena", "chain": "main", "order": 4,
     "giver": "Nostro's Echo", "renown": 600,
     "desc": "Prove yourself in the Arena: waves of beasts, then the champion's purse.",
     "objectives": [{"type": "kill", "family": "fc_beetle", "count": 6, "label": "Round 1: 6 Beetles"},
                    {"type": "kill", "family": "fc_hobbe", "count": 6, "label": "Round 2: 6 Hobbes"},
                    {"type": "kill", "family": "fc_bandit", "count": 6, "label": "Round 3: 6 Bandits"},
                    {"type": "kill", "family": "fc_balverine", "count": 4, "label": "Round 4: 4 Balverines"},
                    {"type": "kill", "family": "fc_troll", "count": 1, "label": "Final Round: an Earth Troll"}],
     "rewards": {"gold": 5000, "xp": {"general": 1200, "strength": 200, "skill": 200}, "morality": 0,
                 "items": [{"id": "fc:platemail_torso", "count": 1}], "title": "Champion of the Arena"},
     "next": "find_the_oracle"},
    {"id": "find_the_oracle", "name": "Find the Oracle", "chain": "main", "order": 5,
     "giver": "Maze", "renown": 900,
     "desc": "The Oracle of Snowspire remembers all. The Northern Wastes will test you on the way.",
     "objectives": [{"type": "kill", "family": "fc_frost_balverine", "count": 3, "label": "Slay 3 Frost Balverines"},
                    {"type": "kill", "family": "fc_summoner", "count": 4, "label": "Banish 4 Summoners"},
                    {"type": "collect", "item": "fc:banshees_tear", "count": 1, "label": "Bottle a Banshee's Tear"}],
     "rewards": {"gold": 2000, "xp": {"general": 1500, "will": 400}, "morality": 0,
                 "items": [{"id": "fc:septimal_key", "count": 1}]},
     "next": "jack_of_blades"},
    {"id": "jack_of_blades", "name": "Battle Jack of Blades", "chain": "main", "order": 6,
     "giver": "Theresa", "renown": 2000,
     "desc": "He took your mother. He burned Oakvale. He waits in the Chamber of Fate, wearing his red smile.",
     "objectives": [{"type": "kill", "family": "fc_jack", "count": 1, "label": "Defeat Jack of Blades"},
                    {"type": "kill", "family": "fc_jack_dragon", "count": 1, "label": "Slay the Dragon of Blades"}],
     "rewards": {"gold": 10000, "xp": {"general": 5000, "strength": 500, "skill": 500, "will": 500},
                 "morality": 0, "items": [{"id": "fc:sword_of_aeons", "count": 1}],
                 "title": "Hero of Oakvale"},
     "next": None},
    # --- side quests ---
    {"id": "hobbe_cave", "name": "The Hobbe Caves", "chain": "side", "order": 1,
     "giver": "Knothole Glade Elder", "renown": 120,
     "desc": "A child is lost in the Hobbe caves. Hobbes do terrible things to lost children.",
     "objectives": [{"type": "kill", "family": "fc_hobbe", "count": 12, "label": "Cull 12 cave Hobbes"}],
     "rewards": {"gold": 350, "xp": {"general": 250}, "morality": 60,
                 "items": [{"id": "fc:silver_key", "count": 1}]}, "next": None},
    {"id": "graveyard_path", "name": "The Graveyard Path", "chain": "side", "order": 2,
     "giver": "Lychfield Gravekeeper", "renown": 150,
     "desc": "The dead of Lychfield refuse to stay buried. Put them down with respect — or without.",
     "objectives": [{"type": "kill", "family": "fc_undead", "count": 10, "label": "Lay 10 Hollow Men to rest"},
                    {"type": "kill", "family": "fc_banshee", "count": 1, "label": "Silence the Banshee"}],
     "rewards": {"gold": 500, "xp": {"general": 400, "will": 100}, "morality": 40,
                 "items": [{"id": "fc:ectoplasm", "count": 4}]}, "next": None},
    {"id": "white_balverine", "name": "The White Balverine", "chain": "side", "order": 3,
     "giver": "Knothole Glade Chief", "renown": 400,
     "desc": "A White Balverine stalks Knothole Glade. Ordinary steel will not bite — silver will.",
     "objectives": [{"type": "kill", "family": "fc_white_balverine", "count": 1, "label": "Slay the White Balverine"}],
     "rewards": {"gold": 1500, "xp": {"general": 800, "strength": 200}, "morality": 80,
                 "items": [{"id": "fc:silver_augment", "count": 1},
                           {"id": "fc:balverine_trophy", "count": 1}]}, "next": None},
    {"id": "lady_greys_invitation", "name": "Lady Grey's Invitation", "chain": "side", "order": 4,
     "giver": "Lady Grey", "renown": 250,
     "desc": "The Mayor of Bowerstone desires a gift: a black rose... or failing that, a great deal of gold.",
     "objectives": [{"type": "collect", "item": "fc:gold_coin", "count": 32, "label": "Gather a courting gift (32 gold coins)"},
                    {"type": "collect", "item": "fc:wedding_ring", "count": 1, "label": "Acquire a Wedding Ring"}],
     "rewards": {"gold": 0, "xp": {"general": 300}, "morality": 0,
                 "items": [{"id": "fc:katana_hiryu", "count": 1}],
                 "title": "Consort of Bowerstone"}, "next": None},
    {"id": "treasure_of_the_keys", "name": "Treasure of the Keys", "chain": "side", "order": 5,
     "giver": "Silver Chest", "renown": 200,
     "desc": "Fifteen silver keys lie hidden in ruins across Albion. The great chest in the Guild waits.",
     "objectives": [{"type": "collect", "item": "fc:silver_key", "count": 15, "label": "Collect 15 Silver Keys"}],
     "rewards": {"gold": 3000, "xp": {"general": 600}, "morality": 0,
                 "items": [{"id": "fc:arkens_crossbow", "count": 1}]}, "next": None},
    {"id": "bounty_bandit_king", "name": "Bounty: Bandit Lieutenants", "chain": "job", "order": 6,
     "giver": "Bowerstone Notice Board", "renown": 180,
     "desc": "Bowerstone pays good coin for bandit ears. Bring proof of your work.",
     "objectives": [{"type": "kill", "family": "fc_bandit", "count": 20, "label": "Collect the bounty: 20 bandits"}],
     "rewards": {"gold": 1200, "xp": {"general": 350, "skill": 100}, "morality": 30,
                 "items": []}, "next": None},
    {"id": "trophy_hunter", "name": "Trophy Hunter", "chain": "job", "order": 7,
     "giver": "Fresco Dove", "renown": 220,
     "desc": "A collector in Bowerstone pays for exotic remains. No questions either way.",
     "objectives": [{"type": "collect", "item": "fc:balverine_fang", "count": 8, "label": "8 Balverine Fangs"},
                    {"type": "collect", "item": "fc:troll_heart", "count": 1, "label": "1 Troll Heart"},
                    {"type": "collect", "item": "fc:wasp_wing", "count": 12, "label": "12 Wasp Wings"}],
     "rewards": {"gold": 2000, "xp": {"general": 400}, "morality": -20,
                 "items": [{"id": "fc:experience_augment", "count": 1}]}, "next": None},
    {"id": "the_septimal_seal", "name": "The Septimal Seal", "chain": "side", "order": 8,
     "giver": "The Oracle", "renown": 500,
     "desc": "Awaken the Focus Sites. Carry the Septimal Key to their stones and feed them ectoplasm.",
     "objectives": [{"type": "collect", "item": "fc:ectoplasm", "count": 10, "label": "Gather 10 Ectoplasm"},
                    {"type": "kill", "family": "fc_wraith", "count": 5, "label": "Banish 5 Wraiths"}],
     "rewards": {"gold": 1000, "xp": {"will": 600, "general": 500}, "morality": 0,
                 "items": [{"id": "fc:summoners_grimoire", "count": 1}]}, "next": None},
]

# ---------------------------------------------------------------------------
# DEMON DOORS
# ---------------------------------------------------------------------------

DEMON_DOORS = [
    {"id": "gourmand", "name": "The Gourmand Door",
     "greeting": "Mmmm... I smell crumbs on you, little thing. FEED ME and we shall talk.",
     "requirement": {"type": "items", "item": "fc:apple_pie", "count": 5,
                     "hint": "Bring me FIVE apple pies. Warm ones."},
     "success": "Ohhh, flaky! Buttery! WORTH ETERNITY. Enter, pastry-friend.",
     "fail": "That is NOT pie. Come back when you respect dessert.",
     "reward": {"items": [{"id": "fc:wellows_pickhammer", "count": 1},
                          {"id": "fc:gold_coin", "count": 20}], "xp": 250}},
    {"id": "warrior", "name": "The Warrior Door",
     "greeting": "I open for violence alone. Show me a Combat Multiplier worthy of the old days.",
     "requirement": {"type": "multiplier", "count": 14,
                     "hint": "Return mid-battle with a Combat Multiplier of 14 or more."},
     "success": "YES! That is how heroes bled in MY day! Pass, slaughter-child.",
     "fail": "Pitiful. My hinges have seen scarier brawls.",
     "reward": {"items": [{"id": "fc:the_harbinger", "count": 1}], "xp": 400}},
    {"id": "judge", "name": "The Judge Door",
     "greeting": "I weigh souls, Hero. Only the truly radiant may pass my arch.",
     "requirement": {"type": "morality_min", "count": 500,
                     "hint": "Return when your goodness shines (Morality 500+)."},
     "success": "You glow like dawn over Oakvale. Pass, blessed one.",
     "fail": "Your soul is... beige. Do better.",
     "reward": {"items": [{"id": "fc:archon_torso", "count": 1},
                          {"id": "fc:holy_warrior_helm", "count": 1}], "xp": 350}},
    {"id": "corrupted", "name": "The Corrupted Door",
     "greeting": "I smell mercy on you. Disgusting. Only the vile may enter my dark.",
     "requirement": {"type": "morality_max", "count": -500,
                     "hint": "Return drenched in wickedness (Morality -500 or worse)."},
     "success": "Ahhh, what beautiful rot in your heart. Welcome home.",
     "fail": "Too kind, too clean. Go drown a kitten and come back.",
     "reward": {"items": [{"id": "fc:demon_helm", "count": 1},
                          {"id": "fc:fire_assassin_torso", "count": 1}], "xp": 350}},
    {"id": "hoarder", "name": "The Hoarder Door",
     "greeting": "Gold. Gooooold. I am a door of simple tastes. PAY THE TOLL.",
     "requirement": {"type": "items", "item": "fc:gold_coin", "count": 50,
                     "hint": "Feed my slot FIFTY gold coins."},
     "success": "Cha-CHING! A pleasure doing business, moneybags.",
     "fail": "Your purse whimpers. Come back wealthy.",
     "reward": {"items": [{"id": "fc:orkons_club", "count": 1},
                          {"id": "fc:silver_key", "count": 2}], "xp": 300}},
    {"id": "moonlit", "name": "The Moonlit Door",
     "greeting": "I open only beneath the moon, for those the night has marked.",
     "requirement": {"type": "night_multiplier", "count": 5,
                     "hint": "Come at night, riding a Combat Multiplier of 5 or more."},
     "success": "The moon approves of your violence. Slip through, night-thing.",
     "fail": "The moon is bored of you. Return bloodier, and after dusk.",
     "reward": {"items": [{"id": "fc:avenger", "count": 1}], "xp": 300}},
    {"id": "riddler", "name": "The Riddler Door",
     "greeting": "A game! I ask, you answer. Fail and I shall laugh at you for a century.",
     "requirement": {"type": "riddle",
                     "riddle": "I have a face I cannot wash, a mouth that cannot eat, and I sing to no one before dawn. What am I?",
                     "answers": ["A rooster", "A Demon Door", "A clock", "A grave"],
                     "correct": 2,
                     "hint": "Answer my riddle correctly."},
     "success": "Tick-tock, clever clogs. The prize is yours.",
     "fail": "WRONG! Hahahaha. Think harder, fleshling.",
     "reward": {"items": [{"id": "fc:silver_key", "count": 5},
                          {"id": "fc:summoners_grimoire", "count": 1}], "xp": 300}},
    {"id": "arboretum", "name": "The Arboretum Door",
     "greeting": "I guard a garden older than your Guild. Only a seasoned soul may smell its roses.",
     "requirement": {"type": "renown", "count": 1000,
                     "hint": "Return when Albion sings of your deeds (Renown 1000+)."},
     "success": "Your legend precedes you like perfume. Enter the green.",
     "fail": "Never heard of you. Do something worth a song.",
     "reward": {"items": [{"id": "fc:solus_greatsword", "count": 1},
                          {"id": "fc:elixir_of_life", "count": 1}], "xp": 500}},
]

# ---------------------------------------------------------------------------
# Convenience aggregations
# ---------------------------------------------------------------------------


def all_items():
    """Every item record across categories (weapons, armor, spells, misc...)."""
    items = []
    items += build_weapons()
    items += build_legendaries()
    items += build_armor()
    for a in AUGMENTS:
        items.append({"id": a["id"], "name": a["name"], "cat": "augment",
                      "kind": "augment", "color": a["color"], "value": 1300,
                      "desc": a["desc"], "stack": 16})
    for c in CONSUMABLES:
        rec = dict(c)
        rec["cat"] = "consumable"
        rec.setdefault("stack", 16)
        items.append(rec)
    for s in SPELLS:
        items.append({"id": f"spell_{s['id']}", "name": f"Will: {s['name']}",
                      "cat": "spell", "kind": "tome", "color": s["color"],
                      "spell": s["id"], "value": 2000, "desc": s["desc"], "stack": 1})
    for m in MISC_ITEMS:
        rec = dict(m)
        rec["cat"] = "misc"
        rec.setdefault("stack", rec.get("stack", 64))
        items.append(rec)
    return items


if __name__ == "__main__":
    items = all_items()
    print(f"{len(items)} items defined")
    from collections import Counter
    print(Counter(i["cat"] for i in items))

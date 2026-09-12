"""Single source for faithful/original display names (L2 foundation).

Semantic keys and resource/save IDs are stable. Original alternatives are build
proposals, not trademark clearance or a user-selected public title. Runtime
migration and release scanning remain L3/L4. Do not distribute preview packages.
"""
from contextlib import contextmanager
from contextvars import ContextVar
import re

# key, faithful spelling, original display spelling. Longest phrases match first.
_ROWS = [
    ('project_title', 'Fablecraft: Reforged', 'Wayfarer Tales'),
    ('project_title_caps', 'FableCraft: Reforged', 'Wayfarer Tales'),
    ('project_name', 'Fablecraft', 'Wayfarer Tales'),
    ('project_name_caps', 'FableCraft', 'Wayfarer Tales'),
    ('game_title', 'Fable: The Lost Chapters', 'The Wayfarer Chronicles'),
    ('game_name', 'Fable', 'Wayfarer'),
    ('realm', 'Albion', 'Elderfen'),
    ('guild', "Heroes' Guild", 'Wayfarer Hall'),
    ('guild_alt', 'Guild of Heroes', 'Wayfarer Hall'),
    ('guildmaster', 'Guildmaster', 'Hall Warden'),
    ('guild_seal', 'Guild Seal', 'Wayfarer Sigil'),
    ('bowerstone', 'Bowerstone', 'Rivergate'),
    ('consort_title', 'Consort of Bowerstone', 'Consort of Rivergate'),
    ('river_bower', 'River Bower', 'River Lorn'),
    ('oakvale', 'Oakvale', 'Briarhaven'),
    ('snowspire', 'Snowspire', 'Frostwatch'),
    ('hook_coast', 'Hook Coast', 'Lantern Coast'),
    ('knothole', 'Knothole Glade', 'Cedar Hollow'),
    ('knothole_short', 'Knothole', 'Cedar Hollow'),
    ('bowerstone_market', 'Bowerstone Market', 'Rivergate Market'),
    ('darkwood_camp', 'Darkwood Trading Camp', 'Duskfen Trading Camp'),
    ('oakvale_quay', 'Oakvale Quay', 'Briarhaven Quay'),
    ('snowspire_oracle', 'Snowspire Oracle', 'Frostwatch Oracle'),
    ('greatwood', 'Greatwood', 'Sunleaf Wood'),
    ('darkwood', 'Darkwood', 'Duskfen'),
    ('witchwood', 'Witchwood', 'Mistpine'),
    ('lychfield', 'Lychfield', 'Mournfield'),
    ('bargate', 'Bargate', 'Ironreach'),
    ('lookout_point', 'Lookout Point', 'Wayfarer Rise'),
    ('barrow_fields', 'Barrow Fields', 'Amber Fields'),
    ('orchard_farm', 'Orchard Farm', 'Ciderstead'),
    ('fisher_creek', 'Fisher Creek', 'Reedwater Creek'),
    ('rose_cottage', 'Rose Cottage', 'Heather Cottage'),
    ('grey_house', 'Grey House', 'Ashen House'),
    ('windmill_hill', 'Windmill Hill', 'Millward Hill'),
    ('headsman_hill', "Headsman's Hill", 'Gallows Rise'),
    ('gibbet_woods', 'Gibbet Woods', 'Rookwood'),
    ('lost_bay', 'Lost Bay', 'Forsaken Harbor'),
    ('northern_wastes', 'Northern Wastes', 'Winter Marches'),
    ('necropolis', 'Necropolis', 'Silent City'),
    ('archon_folly', "Archon's Folly", 'Cinder Crown'),
    ('archon_shrine', "Archon's Shrine", 'First-King Shrine'),
    ('bronze_gate', 'Bronze Gate', 'Copperbound Gate'),
    ('chamber_fate', 'Chamber of Fate', 'Hall of Echoes'),
    ('cullis', 'Cullis Gate', 'Waystone Gate'),
    ('cullis_plural', 'Cullis Gates', 'Waystone Gates'),
    ('cullis_word', 'Cullis', 'Waystone'),
    ('jack', 'Jack of Blades', 'The Masked Sovereign'),
    ('jack_dragon', 'Dragon of Blades', 'Cinder Sovereign'),
    ('twinblade', 'Twinblade', 'Redhand'),
    ('bandit_faction', "Twinblade's Bandits", "Redhand's Bandits"),
    ('maze', 'Maze', 'Orren'),
    ('theresa', 'Theresa', 'Seren'),
    ('lady_grey', 'Lady Grey', 'Lady Ashmere'),
    ('elvira_grey', 'Elvira Grey', 'Elowen Ashmere'),
    ('briar_rose', 'Briar Rose', 'Rowan Vale'),
    ('scarlet_robe', 'Scarlet Robe', 'Crimson Mantle'),
    ('thunder', 'Thunder', 'Stormwarden'),
    ('whisper', 'Whisper', 'Softstep'),
    ('scythe', 'Scythe', 'The Last Reaper'),
    ('nostro', 'Nostro', 'Mordren'),
    ('avo', 'Avo', 'Dawnkeeper'),
    ('skorm', 'Skorm', 'Nightfather'),
    ('archon', 'Archon', 'First King'),
    ('old_kingdom', 'Old Kingdom', 'First Dominion'),
    ('balverine', 'Balverine', 'Moonfang'),
    ('balverines', 'Balverines', 'Moonfangs'),
    ('hobbe', 'Hobbe', 'Burrowling'),
    ('hobbes', 'Hobbes', 'Burrowlings'),
    ('arachanox', 'Arachanox', 'Dunestinger'),
    ('hollow_man', 'Hollow Man', 'Gravewalker'),
    ('hollow_soldier', 'Hollow Soldier', 'Grave Soldier'),
    ('hollow_knight', 'Hollow Knight', 'Grave Knight'),
    ('demon_door', 'Demon Door', 'Stone Sentinel'),
    ('demon_doors', 'Demon Doors', 'Stone Sentinels'),
    ('sword_aeons', 'Sword of Aeons', 'Eonshard'),
    ('avos_tear', "Avo's Tear", 'Dawnfall'),
    ('harbinger', 'The Harbinger', 'Stonewake'),
    ('solus', 'Solus Greatsword', 'Sunfall Greatsword'),
    ('arken_crossbow', "Arken's Crossbow", 'Shipwright Crossbow'),
    ('bereaver', 'The Bereaver', 'Griefwarden'),
    ('avenger_bow', 'The Avenger', 'Oathkeeper'),
    ('avenger', 'Avenger', 'Oathkeeper'),
    ('orkon_club', "Orkon's Club", 'Ironroot Club'),
    ('orkon', 'Orkon', 'Gorran'),
    ('dollmaster_mace', "Dollmaster's Mace", 'Puppetwright Mace'),
    ('wellow_pickhammer', "Wellow's Pickhammer", 'Deepdelver'),
    ('katana_hiryu', 'Katana Hiryu', 'Skycoil Katana'),
    ('skorm_bow', "Skorm's Bow", 'Nightdrinker'),
    ('murren', 'Murren', 'Stoneward'),
    ('wellows', 'Wellow', 'Deepdelver'),
    ('arken', 'Arken', 'Marrel'),
    ('fire_heart', 'Fire Heart', 'Emberheart'),
    ('ship_drowned', 'Ship of the Drowned', 'Pale Voyager'),
    ('oracle_yeron', 'Yeron', 'Aren'),
    ('oracle_moryk', 'Moryk', 'Oren'),
    ('oracle_calran', 'Calran', 'Iren'),
    ('oracle_avisto', 'Avisto', 'Uren'),
    ('library_arcanum', 'Library Arcanum', 'Hidden Athenaeum'),
    ('serenity_farm', 'Serenity Farm', 'Stillwater Farm'),
    ('hidden_copse', 'Hidden Copse', 'Veiled Grove'),
    ('butterfly_house', 'Butterfly House', 'Mothlight House'),
    ('arboretum_door', 'Arboretum Door', 'Garden Sentinel'),
    ('chicken_chaser', 'Chicken Chaser', 'Hen Herder'),
]
STRINGS = {key: {'faithful': faithful, 'original': original} for key, faithful, original in _ROWS}
if len(STRINGS) != len(_ROWS):
    raise ValueError('duplicate semantic name key')
_MODE = ContextVar('branding', default='faithful')
_BY_NAME = {faithful: original for _, faithful, original in _ROWS}
_PATTERN = re.compile(r'(?<![\w])(?:' + '|'.join(re.escape(name).replace("'", "['’]") for name in sorted(_BY_NAME, key=len, reverse=True)) + r')(?![\w])')


def mode():
    return _MODE.get()


@contextmanager
def branding(selected):
    if selected not in ('faithful', 'original'):
        raise ValueError(f'unknown branding mode: {selected}')
    token = _MODE.set(selected)
    try:
        yield
    finally:
        _MODE.reset(token)


def name(key, selected=None):
    selected = mode() if selected is None else selected
    if selected not in ('faithful', 'original'):
        raise ValueError(f'unknown branding mode: {selected}')
    return STRINGS[key][selected]  # Unknown semantic keys deliberately raise.


def text(value):
    """Translate display prose, preserving color codes and namespaced/save IDs.

    Deliberately case-sensitive: display spellings are inventoried, while lower-case
    internal identifiers are left stable for the separate L4 package migration.
    """
    if mode() == 'faithful':
        return value
    parts = re.split(r'(§.)', value)
    for i in range(0, len(parts), 2):
        # Apostrophe variants in display prose should follow the same table.
        parts[i] = _PATTERN.sub(lambda match: _BY_NAME[match.group().replace('’', "'")], parts[i])
    return ''.join(parts)


def localize(value):
    """Copy display data; dictionary keys and numeric/gameplay values never change."""
    if isinstance(value, str):
        return text(value)
    if isinstance(value, dict):
        return {key: localize(item) for key, item in value.items()}
    if isinstance(value, list):
        return [localize(item) for item in value]
    if isinstance(value, tuple):
        return tuple(localize(item) for item in value)
    return value


def faithful_matches(value):
    """Known display-name debt, not a complete release scanner (L4)."""
    return sorted(set(_PATTERN.findall(re.sub(r'§.', '', value).replace('’', "'"))))


# Whole message templates. {@key} resolves a semantic name at generation time;
# {key} is a runtime value, substituted once without reinterpreting its contents.
MESSAGES = {
    'alignment.avo': '§eAvatar of {@avo}',
    'alignment.paragon': '§eParagon',
    'alignment.good': '§aGood',
    'alignment.neutral': '§7Neutral',
    'alignment.rogue': '§cRogue',
    'alignment.villain': '§cVillain',
    'alignment.skorm': '§5Avatar of {@skorm}',
    'menu.hero_title': "§0✦ The Hero's Tale ✦",
    'menu.hero_body': '§8A chronicle bound in parchment and gold.\n\n{alignment} §8· §7morality §f{morality}\n§7Will §9{mana}§7/§9{maxMana}',
    'menu.hero': 'The Hero', 'menu.magic': 'Magic', 'menu.appearance': 'Appearance',
    'menu.weapons': 'Weapons', 'menu.inventory': 'Inventory', 'menu.clothing': 'Clothing',
    'menu.expressions': 'Expressions', 'menu.quests': 'Quests', 'menu.factions': 'Factions',
    'menu.map': 'Map of {@realm}', 'menu.logbook': 'Logbook',
    'menu.unbound': '§7That page of the ledger is not yet bound.',
    'menu.back': '§8❖ Back',
    'magic.title': '§0✦ Magic ✦',
    'magic.body': '§8Assign your three hot-swap powers. Crouch + use the Will Focus to cycle them.\n\n{slots}',
    'magic.none': '§8You have learned no Will powers yet. Find and use a spell tome to weave one into your soul.',
    'magic.empty': '§8(empty)',
    'magic.slot_summary': '{active}§7Slot {slot}: {name}',
    'magic.slot_marker': '§9[Slot {slot}] ',
    'magic.spell': '{marker}§f{name} §7Lv {level}\n§8{category} · {mana} Will',
    'magic.bind_title': '§0Bind {name}',
    'magic.bind_body': '§8Choose a quick-slot to hold this power. Binding here also makes it the active power.',
    'magic.slot': '§fSlot {slot} §8({name})',
    'magic.empty_slot': 'empty',
    'magic.remove': '§7Remove from quick-slots',
    'logbook.title': '§0✦ The Logbook ✦',
    'appearance.title': '§0Appearance',
    'appearance.detail': 'Current rig — align {alignment}, str {strength}, skl {skill}, will {will}\n\nDetail',
    'appearance.full': 'Full (shells + ornaments + morph)',
    'appearance.overlays': 'Overlays only (no morph)',
    'appearance.ornaments': 'Horns / Halo only',
    'appearance.show': 'Show appearance overlays',
    'appearance.charge': 'Hold-to-charge spells',
    'appearance.aura': 'Aura density',
    'inventory.count': '§8{count} {@project_name} stacks carried',
    'weapons.none': '§7No {@game_name} weapon drawn.',
    'map.undiscovered': '§7{@cullis_plural} scattered across {@realm} will join the lattice as you find them.',
    'map.lattice': '§7The {@cullis_word} lattice bends {@realm} to your Will.',
    'map.recall': '§9Recall to the {@guild}',
    'stats.married': 'Married to {@lady_grey}',
    'stats.clock': '§7 ◈ {@realm} time: §f{hour}:{minute}',
}


# L3.2 whole legacy messages. Keys stay stable independently of source line numbers.
MESSAGES.update({
    "legacy.init_hero_01": "§6{@project_name}",
    "legacy.init_hero_02": "§eReforged — Welcome to {@realm}",
    "legacy.init_hero_03": "§6═══ The {@guildmaster} ═══",
    "legacy.init_hero_04": "§f\"Ah, the new apprentice wakes. Your §e{@guild_seal}§f opens the Hero menu. Use a §eQuest Card§f to begin your training. {@realm} is watching, little sparrow.\"",
    "legacy.root_01": "§b◈ {@cullis_word} §7{v0},{v1},{v2} §8({v3} away)",
    "legacy.build_guild_when_ready_01": "§6⚔ You awaken in the {@guild}. The §b{@cullis}§6 glows in the Map Room's south-west nook; the §aSkill Shrine§6 waits to the north-west.",
    "legacy.root_02": "§6§l⚔ {@twinblade} has fallen. The camps whisper of a new power in {@realm}.",
    "legacy.root_03": "§4§l✦ {@jack} falls... but his mask drinks the darkness!",
    "legacy.root_04": "§6§l✦ The {@jack_dragon} is destroyed. {@realm} is free.",
    "legacy.offer_aeons_choice_01": "§4The {@sword_aeons}",
    "legacy.offer_aeons_choice_02": "The blade hums in your hands, heavy with your bloodline's power.\n\n§cKeep it§r — and rule {@realm} through fear.\n§eDestroy it§r — and {@avos_tear} shall answer your sacrifice.",
    "legacy.offer_aeons_choice_03": "§5The Sword feeds. {@realm} will learn to kneel.",
    "legacy.offer_aeons_choice_04": "§eThe Sword shatters into dawn — {@avos_tear} is yours.",
    "legacy.recall_to_guild_01": "§9✦ The {@guild_seal} carries you home.",
    "legacy.completed_quests_menu_01": "§7{@realm} remembers these deeds.",
    "legacy.logbook_menu_01": "§b{@cullis_plural}",
    "legacy.logbook_menu_02": "Use the {@guild_seal} to open this book.",
    "legacy.logbook_menu_03": "Sneak-use the Seal to recall to the {@guild}.",
    "legacy.logbook_menu_04": "{@cullis_plural}",
    "legacy.logbook_menu_05": "Discovered Focus Sites join the {@cullis_word} lattice.",
    "legacy.logbook_menu_06": "Stand on a gate and sneak, or choose Map from the {@guild_seal}.",
    "legacy.map_menu_01": "§b◈ {v0}\n§8{v1}m distant",
    "legacy.map_menu_02": "§f{v0}",
    "legacy.faction_menu_01": "§7{@realm} keeps score. Guards, traders and barkeeps",
    "legacy.titles_menu_01": "§6Choose the title you wear — {@realm} will address you by it:",
    "legacy.titles_menu_02": "§6✦ You will be known as §e{v0}§6 across {@realm}.",
    "legacy.quest_board_01": "§7No quest cards remain. {@realm} sleeps soundly... for now.",
    "legacy.root_05": "{@jack} steps from the shadows.",
    "legacy.open_demon_door_01": "§5{@demon_door} Opened",
    "legacy.spouse_menu_01": "Whatever {@realm} throws at you, throw me a wink first.",
    "legacy.npc_talk_01": "§6The {@guildmaster}",
    "legacy.npc_talk_02": "{@realm} sings of your kindness, {v0}.",
    "legacy.npc_talk_03": "§5{@maze}",
    "legacy.npc_talk_04": "§o\"The Will is a muscle, Hero. Spell tomes hide in ruins and {@demon_door} hoards — each one a power your enemies will learn to dread. Visit the Oracle in the far snows, when you are ready for truths.\"§r",
    "legacy.npc_talk_05": "§9✦ {@maze} presses two humming tomes into your hands.",
    "legacy.npc_talk_06": "§5{@maze}: \"I am a Hero, not a lending library.\"",
    "legacy.npc_talk_07": "§d{@theresa}",
    "legacy.npc_talk_08": "§5Ask about {@jack}",
    "legacy.npc_talk_09": "§d{@theresa}: §o\"{v0}\"",
    "legacy.npc_talk_10": "§d{@theresa}: §o\"He wears a mask of swords and calls it a face. When he comes, the {@sword_aeons} will sing. What you do with it after is yours to choose — {@realm} remembers either way.\"",
    "legacy.npc_talk_11": "§d{@lady_grey}: §o\"My consort. {@bowerstone} bores me — slay something interesting.\"",
    "legacy.npc_talk_12": "§d{@lady_grey}, Mayor of {@bowerstone}",
    "legacy.npc_talk_13": "§d{@lady_grey}: §o\"Manners! How refreshing.\"",
    "legacy.npc_talk_14": "§bThe Oracle of {@snowspire}",
    "legacy.npc_talk_15": "§c{@briar_rose}",
    "legacy.npc_talk_16": "§cAsk about {@demon_doors}",
    "legacy.npc_talk_17": "§c{@briar_rose}: §o\"{@demon_doors} respond to deeds, not poetry. Multiplier 14 opens the Warrior's arch — if you can keep your footing.\"",
    "legacy.npc_talk_18": "§c{@briar_rose}: §o\"Every thorn here grew from a broken promise. Mind you don't leave one of your own behind.\"",
    "legacy.npc_talk_19": "§6{@hobbe} Tooth Ale — 1 gold",
    "legacy.npc_talk_20": "They say a White {@balverine} prowls {@knothole_short} way. Silver, friend. Silver.",
    "legacy.npc_talk_21": "{@lady_grey} never did find her sister. Don't ask her about it.",
    "legacy.npc_talk_22": "§6Guard: \"§o{v0} sleeps easy with you about, Hero. An honour.§r§6\"",
    "legacy.npc_talk_23": "§9Guard: \"Good to see a friend of {v0}. Mind the {@hobbes} after dark.\"",
    "legacy.npc_talk_24": "§9Guard: \"All quiet, Hero. Mind the {@hobbes} after dark.\"",
    "legacy.npc_talk_25": "The {@guildmaster} says footwork wins duels. My bruises agree.",
    "legacy.npc_talk_26": "One day I'll take {@twinblade}'s measure myself.",
    "legacy.npc_talk_27": "{@maze} says patience is an arrow loosed before the bow is drawn.",
    "legacy.npc_talk_28": "The Will hums louder near the {@cullis}.",
    "legacy.npc_talk_29": "I saw blue fire in my sleep. {@theresa} said not to panic.",
    "legacy.npc_talk_30": "§f§o\"{v0}\"§r\n\n§8Standing with {v1}: {v2}",
    "legacy.npc_talk_31": "§fVillager: §o\"{@avo} bless you, kind one!\"",
    "legacy.npc_talk_32": "{@twinblade}'s lot camp behind a palisade of whole trees. Cowards.",
    "legacy.npc_talk_33": "The {@cullis_plural} hum when a storm is coming. Or a Hero.",
    "legacy.root_06": "§b◈ {@cullis} §7— step into the light to travel",
    "legacy.root_07": "§b◈ {@cullis} §7— sneak to focus your Will and travel",
    "legacy.boast_menu_01": "§6✦ You declare yourself §e{v0}§6 before {@realm}!",
    "legacy.root_08": "Finest wares in {@realm}, {you}!",
    "legacy.root_09": "{@demon_doors} love a riddle, {you}.",
    "legacy.root_10": "{@bowerstone} watches you closely, {you}.",
    "legacy.root_11": "Did you hear the news from {@bowerstone}?",
    "legacy.root_12": "{@hobbes} got into the turnips again.",
    "legacy.root_13": "Fine cloth from {@bowerstone}, just in.",
    "legacy.root_14": "{@guildmaster}",
    "legacy.root_15": "{@maze}",
    "legacy.root_16": "{@theresa}",
    "legacy.root_17": "{@briar_rose}",
    "legacy.root_18": "{@lady_grey}",
    "legacy.root_19": "{@bowerstone} Guard",
    "legacy.root_20": "{@oakvale} Guard",
    "legacy.root_21": "{@snowspire} Guard",
    "legacy.cullis_travel_01": "§b◈ {@cullis}",
    "legacy.cullis_travel_02": "{v0}\n§7The lattice of {@realm} bends to your Will.\n§7Standing at: §b{v1}\n{v2}",
    "legacy.cullis_travel_03": "§b{v0}\n§8{v1}m distant",
    "legacy.cullis_travel_04": "§f{v0}",
    "legacy.add_rep_01": "§7✦ {v0}: {v1}{v2} §7reputation ({v3})",
    "legacy.renown_line_01": "Your name is sung in every tavern from here to {@bowerstone}.",
    "legacy.bounty_summary_lines_01": " §c⚖ {v0}: §6{v1}g §7· §e{v2}§7 · {v3}{v4}",
    "legacy.accrue_crime_01": "§4⚖ MURDER WITNESSED — you are WANTED in {v0}.",
    "legacy.accrue_crime_02": "§4⚖ ASSAULT WITNESSED — you are WANTED in {v0}.",
    "legacy.accrue_crime_03": "§4⚖ Your wanted level in {v0} rises to §e{v1}§4.",
    "legacy.clear_settlement_bounty_01": "§a⚖ {v0} bounty cleared — {v1}.",
    "legacy.send_to_jail_01": "§7Released outside {v0}; possessions confiscated",
    "legacy.send_to_jail_02": "§7The guards release you beyond the town limits with only your {@guild_seal} and Will powers.",
    "legacy.demand_bounty_resolution_01": "§4Warrant — {v0}",
    "legacy.root_22": "§a⚖ Your wanted level in {v0} has faded."
})

def message_template(key):
    return re.sub(r'\{@([\w]+)\}', lambda match: name(match[1]), MESSAGES[key])


PLACE_KEYS = ('bandit_faction', 'guild', 'bowerstone', 'oakvale', 'snowspire', 'hook_coast', 'knothole', 'lookout_point', 'darkwood_camp', 'bowerstone_market', 'oakvale_quay', 'snowspire_oracle', 'necropolis', 'orchard_farm', 'fisher_creek', 'rose_cottage', 'windmill_hill', 'chamber_fate')


def emit_runtime(bp):
    """Own the generated runtime module; emit only the selected naming variant."""
    import json
    import fc_data
    from fc_lib import NAMESPACE, write_text
    from fc_mobs import MOBS

    display_names = {f"{NAMESPACE}:{item['id']}": text(item['name'])
                     for item in fc_data.all_items() + MOBS}
    display_names['wd:will_focus'] = 'Will Focus'
    source = '// AUTO-GENERATED by scripts/fc_strings.py — do not edit.\n'
    source += 'export const BRANDING_MODE = ' + json.dumps(mode()) + ';\n'
    for label, values in (
        ('NAMES', {key: name(key) for key in STRINGS}),
        ('MESSAGES', {key: message_template(key) for key in MESSAGES}),
        ('DISPLAY_NAMES', display_names),
        ('LEGACY_PLACES', {STRINGS[key]['faithful']: name(key) for key in PLACE_KEYS}),
        ('LEGACY_TITLES', {STRINGS['consort_title']['faithful']: name('consort_title')}),
    ):
        source += f'const {label} = Object.freeze(' + json.dumps(values, ensure_ascii=False, indent=2) + ');\n'
    source += '''
const has = (table, key) => Object.prototype.hasOwnProperty.call(table, key);
export function name(key) {
  if (!has(NAMES, key)) throw new Error(`Unknown name key: ${key}`);
  return NAMES[key];
}
export function template(key) {
  if (!has(MESSAGES, key)) throw new Error(`Unknown message key: ${key}`);
  return MESSAGES[key];
}
export function t(key, values = {}) {
  return template(key).replace(/\\{(\\w+)\\}/g, (_, field) => {
    if (!has(values, field)) throw new Error(`Missing ${field} for message ${key}`);
    return String(values[field]);
  });
}
// Translate only recognized saved place labels, retaining suffixes and source records.
// This explicit compatibility map is still L4 release debt, not a scanner exemption.
export function placeName(value) {
  if (typeof value !== "string") return String(value);
  if (BRANDING_MODE === "faithful") return value;
  const coordinate = value.match(/^(.*?)( \\(-?\\d+,-?\\d+\\))$/);
  let base = coordinate ? coordinate[1] : value;
  const suffix = coordinate ? coordinate[2] : "";
  const outskirts = base.endsWith(" Outskirts") ? " Outskirts" : "";
  if (outskirts) base = base.slice(0, -outskirts.length);
  const article = base.startsWith("The ") ? "The " : "";
  if (article) base = base.slice(article.length);
  base = base.replace(/’/g, "'");
  return has(LEGACY_PLACES, base) ? article + LEGACY_PLACES[base] + outskirts + suffix : value;
}
export function titleName(value) {
  return has(LEGACY_TITLES, value) ? LEGACY_TITLES[value] : value;
}
export function itemName(id) {
  if (has(DISPLAY_NAMES, id)) return DISPLAY_NAMES[id];
  return id.replace(/^(fc|wd):/, "").split("_")
    .map((word) => word ? word[0].toUpperCase() + word.slice(1) : "").join(" ");
}
'''
    write_text(bp / 'scripts/fc_strings.js', source)


if __name__ == '__main__':
    from fc_lib import BP
    emit_runtime(BP)

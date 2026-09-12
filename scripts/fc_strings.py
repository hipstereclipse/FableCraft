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
    ('river_bower', 'River Bower', 'River Lorn'),
    ('oakvale', 'Oakvale', 'Briarhaven'),
    ('snowspire', 'Snowspire', 'Frostwatch'),
    ('hook_coast', 'Hook Coast', 'Lantern Coast'),
    ('knothole', 'Knothole Glade', 'Cedar Hollow'),
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
    return sorted(set(_PATTERN.findall(value.replace('’', "'"))))


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


def message_template(key):
    return re.sub(r'\{@([\w]+)\}', lambda match: name(match[1]), MESSAGES[key])


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
    ):
        source += f'const {label} = Object.freeze(' + json.dumps(values, ensure_ascii=False, indent=2) + ');\n'
    source += '''
const has = (table, key) => Object.prototype.hasOwnProperty.call(table, key);
export function name(key) {
  if (!has(NAMES, key)) throw new Error(`Unknown name key: ${key}`);
  return NAMES[key];
}
export function t(key, values = {}) {
  if (!has(MESSAGES, key)) throw new Error(`Unknown message key: ${key}`);
  return MESSAGES[key].replace(/\\{(\\w+)\\}/g, (_, field) => {
    if (!has(values, field)) throw new Error(`Missing ${field} for message ${key}`);
    return String(values[field]);
  });
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

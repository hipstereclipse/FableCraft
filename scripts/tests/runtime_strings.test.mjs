// Actual generated module and Hero Menu, with the Bedrock UI boundary mocked.
// node --experimental-vm-modules scripts/tests/runtime_strings.test.mjs
import { test } from 'node:test';
import assert from 'node:assert/strict';
import vm from 'node:vm';
import { readFile, mkdtemp, rm } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { resolve, dirname, join } from 'node:path';
import { spawnSync } from 'node:child_process';
import { parse } from 'espree';

async function fixture(mode) {
  const temp = await mkdtemp(join(tmpdir(), 'runtime-names-'));
  let strings;
  try {
    const result = spawnSync(process.env.PYTHON || 'python', ['-c',
      'import sys; from pathlib import Path; from fc_strings import branding,emit_runtime; ' +
      'ctx=branding(sys.argv[1]); ctx.__enter__(); emit_runtime(Path(sys.argv[2]))', mode, temp],
    { env: { ...process.env, PYTHONPATH: resolve('scripts') }, encoding: 'utf8' });
    assert.equal(result.status, 0, result.stderr);
    strings = await readFile(join(temp, 'scripts/fc_strings.js'), 'utf8');
  } finally { await rm(temp, { recursive: true, force: true }); }
  const forms = [], opened = [], messages = [];
  class Form {
    constructor() { this.buttons = []; this.controls = []; }
    title(value) { this.heading = value; return this; }
    body(value) { this.content = value; return this; }
    button(label, icon) { this.buttons.push({ label, icon }); return this; }
    dropdown(...args) { assert.equal(typeof args[2], 'object', 'UI 2.0 dropdown options'); this.controls.push(['dropdown', ...args]); return this; }
    toggle(...args) { assert.equal(typeof args[1], 'object', 'UI 2.0 toggle options'); this.controls.push(['toggle', ...args]); return this; }
    submitButton(label) { this.submit = label; return this; }
    slider(...args) { assert.equal(typeof args[3], 'object', 'UI 2.0 slider options'); assert.equal(args.length, 4); this.controls.push(['slider', ...args]); return this; }
    show() { forms.push(this); return new Promise(resolve => { this.answer = resolve; }); }
  }
  const state = {
    alignment: 900, mana: { current: 43.6, max: 100 }, ui: {},
    spells: { owned: { fireball: 2 }, slots: ['fireball', null, null], active: 0 },
    appearance: { tiers: { alignment: 2, strength: 3, skill: 4, will: 5 } },
    options: { appearanceDetail: 'full', morphEnabled: true, chargeEnabled: true, auraDensity: 1 },
  };
  const bridge = Object.fromEntries(['stats', 'weapons', 'items', 'clothing', 'expressions', 'quests', 'factions', 'map']
    .map(page => [page, () => opened.push(page)]));
  const mocks = {
    '@minecraft/server-ui': { ActionFormData: Form, ModalFormData: Form },
    'config.js': { WD_CONFIG: { guildSealFlourish: false } },
    'state.js': { getState: () => state, mutateState: (_, edit) => edit(state) },
    'particles.js': { spawnParticle() {} },
    'registry.js': { getSpell: id => id === 'fireball' ? { name: 'Fireball', category: 'attack', baseMana: 15 } : undefined,
      SPELL_ORDER: ['fireball'], CATEGORY_LABEL: { attack: 'Attack' } },
    'menu_bridge.js': { LEGACY_MENU: bridge },
    'logbook.js': { chronicle: () => ({ lines: ['Chronicle delegated to L3.3'] }) },
  };
  const context = vm.createContext({ console });
  const cache = new Map();
  async function load(path) {
    if (cache.has(path)) return cache.get(path);
    const mock = mocks[path] || mocks[path.split('/').at(-1)];
    const mod = mock ? new vm.SyntheticModule(Object.keys(mock), function () {
      for (const [key, value] of Object.entries(mock)) this.setExport(key, value);
    }, { context, identifier: path }) : new vm.SourceTextModule(path.endsWith('/fc_strings.js') ? strings :
      await readFile(path, 'utf8'), { context, identifier: path });
    cache.set(path, mod);
    await mod.link((specifier, parent) => load(specifier.startsWith('.') ? resolve(dirname(parent.identifier), specifier) : specifier));
    return mod;
  }
  const menu = await load(resolve('packs/Fablecraft_BP/scripts/wd/herobook.js'));
  await menu.evaluate();
  const api = cache.get(resolve('packs/Fablecraft_BP/scripts/fc_strings.js')).namespace;
  const player = { sendMessage: message => messages.push(message) };
  const choose = async (form, response) => { form.answer(response); await new Promise(resolve => setImmediate(resolve)); };
  async function legacy(declarations, bindings = {}) {
    const source = await readFile('packs/Fablecraft_BP/scripts/main.js', 'utf8');
    const ast = parse(source, { ecmaVersion: 'latest', sourceType: 'module', range: true });
    const chunks = declarations.map(name => {
      const node = ast.body.find(node => node.type === 'FunctionDeclaration' && node.id.name === name ||
        node.type === 'VariableDeclaration' && node.declarations.some(d => d.id.name === name));
      assert.ok(node, `Missing actual declaration ${name}`);
      return source.slice(...node.range);
    });
    Object.assign(context, {
      msg: api.t, template: api.template, placeName: api.placeName, titleName: api.titleName,
      ActionFormData: Form, ModalFormData: Form, MessageFormData: Form,
      fableTitle: text => text, fableBody: lines => lines.join('\n'),
      displayName: api.itemName, FABLE_RULE: 'RULE', ...bindings,
    });
    vm.runInContext(chunks.join('\n'), context);
    return vm.runInContext('({' + declarations.join(',') + '})', context);
  }
  return { api, state, forms, opened, messages, bridge, choose, legacy, open: () => menu.namespace.openHeroMenu(player) };
}

for (const mode of ['faithful', 'original']) {
  test(`${mode}: strict names, single-pass interpolation, stable IDs`, async () => {
    const { api } = await fixture(mode);
    assert.equal(api.BRANDING_MODE, mode);
    assert.equal(api.name('realm'), mode === 'faithful' ? 'Albion' : 'Elderfen');
    assert.equal(api.itemName('fc:avos_tear'), mode === 'faithful' ? "Avo's Tear" : 'Dawnfall');
    assert.equal(api.itemName('fc:theresa'), mode === 'faithful' ? 'Theresa' : 'Seren');
    assert.equal(api.itemName('other:unchanged_key'), 'Other:unchanged Key');
    assert.throws(() => api.name('toString'), /Unknown name/);
    assert.throws(() => api.t('toString'), /Unknown message/);
    assert.throws(() => api.t('inventory.count'), /Missing count/);
    assert.equal(api.t('magic.bind_title', { name: 'Zoë {other} $&' }), '§0Bind Zoë {other} $&');
  });

  test(`${mode}: root labels, mana, alignment and every legacy route`, async () => {
    const f = await fixture(mode);
    const routes = { 0: 'stats', 3: 'weapons', 4: 'items', 5: 'clothing', 6: 'expressions', 7: 'quests', 8: 'factions', 9: 'map' };
    for (const [selection, page] of Object.entries(routes)) {
      f.open(); const form = f.forms.at(-1);
      assert.equal(form.buttons.length, 11);
      assert.equal(form.buttons[9].label, mode === 'faithful' ? 'Map of Albion' : 'Map of Elderfen');
      assert.ok(form.content.includes(mode === 'faithful' ? 'Avatar of Avo' : 'Avatar of Dawnkeeper'));
      assert.ok(form.content.includes('§944'));
      assert.equal(form.buttons[9].icon, 'textures/ui/wd/sigil_map');
      await f.choose(form, { selection: Number(selection), canceled: false });
      assert.equal(f.opened.at(-1), page);
    }
  });

  test(`${mode}: quick-slot mutation and return to the same hub`, async () => {
    const f = await fixture(mode); f.open();
    await f.choose(f.forms.at(-1), { selection: 1 });
    const magic = f.forms.at(-1);
    assert.equal(magic.heading, '§0✦ Magic ✦');
    assert.match(magic.content, /Slot 1: §fFireball/);
    await f.choose(magic, { selection: 0 });
    assert.equal(f.forms.at(-1).heading, '§0Bind Fireball');
    await f.choose(f.forms.at(-1), { selection: 2 });
    assert.deepEqual(f.state.spells.slots, [null, null, 'fireball']);
    assert.equal(f.state.spells.active, 2);
    await f.choose(f.forms.at(-1), { selection: 1 });
    assert.equal(f.forms.at(-1).buttons.length, 11);
  });

  test(`${mode}: appearance controls and missing bridge fallback`, async () => {
    const f = await fixture(mode); f.open();
    await f.choose(f.forms.at(-1), { selection: 2 });
    const appearance = f.forms.at(-1);
    assert.equal(appearance.heading, '§0Appearance');
    assert.match(appearance.controls[0][1], /align 2, str 3, skl 4, will 5/);
    await f.choose(appearance, { formValues: [1, false, false, 0] });
    assert.equal(f.state.options.appearanceDetail, 'overlays_only');
    assert.equal(f.state.options.morphEnabled, false);
    assert.equal(f.state.options.auraDensity, 0);
    f.bridge.map = undefined;
    await f.choose(f.forms.at(-1), { selection: 9 });
    assert.deepEqual(f.messages, ['§7That page of the ledger is not yet bound.']);
  });

  test(`${mode}: saved place display and travel preserve canonical names and coordinates`, async () => {
    const f = await fixture(mode);
    const expected = mode === 'faithful' ? 'Oakvale Quay (-12,34)' : 'Briarhaven Quay (-12,34)';
    assert.equal(f.api.placeName('Oakvale Quay (-12,34)'), expected);
    assert.equal(f.api.placeName('The Heroes’ Guild Outskirts'),
      mode === 'faithful' ? 'The Heroes’ Guild Outskirts' : 'The Wayfarer Hall Outskirts');
    assert.equal(f.api.placeName('A player named Maze built this'), 'A player named Maze built this');
    let saved = JSON.stringify([{ name: "Heroes' Guild", x: 1, y: 64, z: 2 },
      { name: 'Oakvale Quay (-12,34)', x: -12, y: 70, z: 34 }]);
    const teleports = [], notices = [];
    const api = await f.legacy(['registerCullis', 'cullisTravel'], {
      world: { getDynamicProperty: () => saved, setDynamicProperty: (key, value) => {
        assert.equal(key, 'fc_cullis'); saved = value;
      } },
      showHeroTitle: (_, title, options) => notices.push({ title, ...options }),
    });
    api.registerCullis("Heroes' Guild", { x: 3.9, y: 66.2, z: 5.1 });
    const sites = JSON.parse(saved);
    assert.equal(sites.length, 2);
    assert.deepEqual(sites[0], { name: "Heroes' Guild", x: 3, y: 66, z: 5 });
    const before = saved;
    const player = { location: { x: 3, y: 66, z: 5 }, dimension: { spawnParticle() {} },
      playSound() {}, teleport: loc => teleports.push(JSON.parse(JSON.stringify(loc))) };
    api.cullisTravel(player, sites, sites[0]);
    assert.ok(f.forms.at(-1).buttons[0].label.includes(expected));
    await f.choose(f.forms.at(-1), { selection: 0 });
    assert.deepEqual(teleports, [{ x: -11.5, y: 71, z: 34.5 }]);
    assert.equal(notices[0].subtitle, '§f' + expected);
    assert.equal(saved, before);
  });

  test(`${mode}: bounty display retains amounts, timers, jurisdiction and stored record`, async () => {
    const f = await fixture(mode);
    const record = { name: 'Bowerstone Market', town: 'bowerstone', amount: 75, expiresAtMs: 65000 };
    const before = JSON.stringify(record);
    const api = await f.legacy(['bountySummaryLines', 'bountyResponseTier', 'bountyHeatLevel', 'formatBountyTime'], {
      getBounties: () => ({ original_key: record }), nowMs: () => 5000, GUILD_TOWN_KEY: 'guild',
    });
    const lines = api.bountySummaryLines({});
    assert.ok(lines.at(-1).includes(mode === 'faithful' ? 'Bowerstone Market' : 'Rivergate Market'));
    assert.ok(lines.at(-1).includes('75g'));
    assert.ok(lines.at(-1).includes('3 veteran guards'));
    assert.ok(lines.at(-1).includes('1m 0s left'));
    assert.equal(JSON.stringify(record), before);
  });

  test(`${mode}: earned title labels change without rewriting ownership or selected title`, async () => {
    const f = await fixture(mode);
    const owned = ['Consort of Bowerstone'];
    let active = owned[0];
    const api = await f.legacy(['activeTitle', 'applyTitleTag', 'heroAddress', 'titlesMenu'], {
      ensureBaseTitles() {},
      P: { get: () => 100, getJ: (_, key) => key === 'fc_titles' ? owned : active,
        setJ: (_, key, value) => { assert.equal(key, 'fc_active_title'); active = value; } },
    });
    const player = { name: 'Zoë', sendMessage() {} };
    const displayed = mode === 'faithful' ? 'Consort of Bowerstone' : 'Consort of Rivergate';
    assert.equal(api.heroAddress(player), displayed);
    api.titlesMenu(player);
    assert.equal(f.forms.at(-1).buttons[1].label, '§a● ' + displayed);
    await f.choose(f.forms.at(-1), { selection: 1 });
    assert.equal(player.nameTag, '§e' + displayed + '\n§fZoë');
    assert.equal(active, 'Consort of Bowerstone');
    assert.deepEqual(owned, ['Consort of Bowerstone']);
  });

  test(`${mode}: NPC voice interpolation and local t bindings do not shadow message access`, async () => {
    const f = await fixture(mode);
    const api = await f.legacy(['NPC_VOICE', 'NPC_NAME', 'npcTalk'], {
      morality: () => 0, renownLine: () => '',
    });
    assert.equal(api.NPC_NAME['fc:theresa'], mode === 'faithful' ? 'Theresa' : 'Seren');
    assert.equal(api.NPC_VOICE['fc:trader'][0].replace('{you}', 'Zoë'),
      mode === 'faithful' ? 'Finest wares in Albion, Zoë!' : 'Finest wares in Elderfen, Zoë!');
    const spoken = [];
    api.npcTalk({ sendMessage: value => spoken.push(value) }, { typeId: 'fc:theresa' });
    assert.equal(f.forms.at(-1).heading, mode === 'faithful' ? '§dTheresa' : '§dSeren');
    await f.choose(f.forms.at(-1), { selection: 1 });
    assert.ok(spoken[0].includes(mode === 'faithful' ? 'Sword of Aeons' : 'Eonshard'));
  });

  test(`${mode}: buy and sell quantity modals use UI 2.0 options and preserve selected amounts`, async () => {
    const f = await fixture(mode), purchases = [], sales = [];
    const api = await f.legacy(['buyQuantityMenu', 'sellQuantityMenu'], {
      countItem: () => 10,
      completePurchase: (_, title, stock, amount) => purchases.push({ title, stock, amount }),
      completeSale: (_, title, tier, entry, amount) => sales.push({ title, tier, entry, amount }),
    });
    api.buyQuantityMenu({}, 'Store', { id: 'fc:health_potion', label: 'Potion', cost: 2 });
    await f.choose(f.forms.at(-1), { selection: 2 });
    assert.equal(f.forms.at(-1).controls[0][4].defaultValue, 5);
    await f.choose(f.forms.at(-1), { formValues: [3] });
    assert.equal(purchases[0].amount, 3);
    api.sellQuantityMenu({}, 'Store', 'neutral', { id: 'fc:balverine_fang', count: 4, price: 1 });
    await f.choose(f.forms.at(-1), { selection: 2 });
    assert.equal(f.forms.at(-1).controls[0][4].defaultValue, 4);
    await f.choose(f.forms.at(-1), { formValues: [2] });
    assert.equal(sales[0].amount, 2);
    assert.equal(sales[0].entry.id, 'fc:balverine_fang');
  });
}

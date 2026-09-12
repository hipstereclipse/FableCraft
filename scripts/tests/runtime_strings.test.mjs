// Actual generated module and Hero Menu, with the Bedrock UI boundary mocked.
// node --experimental-vm-modules scripts/tests/runtime_strings.test.mjs
import { test } from 'node:test';
import assert from 'node:assert/strict';
import vm from 'node:vm';
import { readFile, mkdtemp, rm } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { resolve, dirname, join } from 'node:path';
import { spawnSync } from 'node:child_process';

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
  return { api, state, forms, opened, messages, bridge, choose, open: () => menu.namespace.openHeroMenu(player) };
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
}

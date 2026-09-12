// Exercise the actual scatter function with rectangular generated footprints.
const fs = require('node:fs');
const vm = require('node:vm');
const assert = require('node:assert/strict');
const test = require('node:test');
const espree = require('espree');
const readTables = require('../structure_tables.cjs');
const sourcePath = process.env.FC_STRUCTURE_TEST_SOURCE || 'packs/Fablecraft_BP/scripts/main.js';
const source = fs.readFileSync(sourcePath, 'utf8');
const tree = espree.parse(source, { ecmaVersion: 'latest', sourceType: 'module', range: true });
const node = tree.body.find(n => n.type === 'FunctionDeclaration' && n.id.name === 'maybePlace');
const fn = source.slice(...node.range);
const tables = readTables(sourcePath);
for (const id of ['chapel_skorm', 'demon_door_arch', 'power_snowspire_oracle', 'temple_avo', 'arena_ring', 'bowerstone_market', 'oakvale_village', 'grey_house', 'bargate_prison']) {
  test(`${id}: actual placement uses generator dimensions and preserves save envelope`, () => {
    const pick = tables.STRUCTS.find(s => s.id === `fc:${id}`);
    const calls = {};
    const capture = key => (...args) => { calls[key] = args; };
    const math = Object.create(Math); math.random = () => 0.99;
    const dimension = {};
    const context = {
      REGION: 256, Math: math,
      guildDoorWorldExcluded: () => false, guildDoorPilot: { excludesWorldPosition: () => false },
      world: { getDynamicProperty: () => undefined, setDynamicProperty: capture('saveRegion'), structureManager: { place: capture('place') } },
      hash2: () => 0, pickStruct: () => pick,
      sampleGroundY: (...args) => { calls.sample = args; return 65; },
      surfMatch: () => true, surfaceCategory: () => 'grass', tooCloseToExisting: (...args) => { calls.crowd = args; return false; },
      recordPlace: capture('record'), blendTerrain: capture('blend'), skirtTerrain: capture('skirt'), fillLootChests: capture('loot'),
      trySpawn: capture('spawn'), ensureDemonDoor: capture('door'), recordDemonDoor: () => {}, registerCullis: capture('cullis'), cullisLabel: () => 'test',
    };
    vm.runInNewContext(fn + '\nthis.run = maybePlace;', context);
    context.run({ location: { x: -30, y: 65, z: 28 }, dimension }, 0, 0);
    assert.deepEqual(calls.sample.slice(3), [pick.w, pick.d]);
    assert.deepEqual(calls.blend.slice(4), [pick.w, pick.d]);
    assert.deepEqual(calls.skirt.slice(4, 6), [pick.w, pick.d]);
    assert.deepEqual(calls.loot.slice(4, 7), [pick.w, pick.h, pick.d]);
    assert.equal(calls.record[2], Math.max(pick.w, pick.d));
    assert.equal(calls.crowd[2], Math.max(pick.w, pick.d));
    assert.equal(calls.place[0], pick.id);
    if (calls.spawn) assert.ok(calls.spawn[2].z < 28 + pick.d - 4);
    if (calls.cullis) assert.equal(calls.cullis[1].z, 28 + (pick.d >> 1));
  });
}

// GP7 executes the actual ten-tick maintenance callback at mocked boundaries.
// Former repair declarations, when present, are evaluated, never stubbed out.
// node --experimental-vm-modules scripts/tests/guild_maintenance.test.mjs
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
import test from 'node:test';
import { parse } from 'espree';

const main = fs.readFileSync('packs/Fablecraft_BP/scripts/main.js', 'utf8');
const ast = parse(main, { ecmaVersion: 'latest', sourceType: 'module', range: true });
const module = new vm.SourceTextModule(fs.readFileSync('packs/Fablecraft_BP/scripts/guild_training.js', 'utf8'));
await module.link(() => { throw Error('Unexpected training import'); });
await module.evaluate();
const training = module.namespace;
const retiredKeys = ['fc_guild_ring_scarecrows_removed', 'fc_guild_demon_approach_v2'];
const declaration = name => ast.body.find(node => node.type === 'FunctionDeclaration' && node.id.name === name
  || node.type === 'VariableDeclaration' && node.declarations.some(d => d.id.name === name));
const interval = ast.body.find(node => node.type === 'ExpressionStatement'
  && main.slice(...node.range).startsWith('system.runInterval(')
  && main.slice(...node.range).includes('guildTraining.beginPass'));
assert.ok(interval, 'Actual Guild maintenance callback');
const key = p => `${p.x},${p.y},${p.z}`;

function fixture({ legacyFlags, failRead, failWrite = false, failFlag = false } = {}) {
  const props = new Map([['fc_guild_placed', true]]), blocks = new Map(), entities = [];
  if (legacyFlags !== undefined) for (const name of retiredKeys) props.set(name, legacyFlags);
  const writes = [], reads = [], propertyWrites = [], propertyReads = [], adjacent = [];
  let tick = 10, runtime;
  const dim = { id: 'minecraft:overworld', getBlock(point) {
    const at = key(point); reads.push(at);
    if (at === failRead) return undefined;
    if (failRead === 'throw') throw Error('Injected unavailable block');
    const block = blocks.get(at) ?? { typeId: point.y === 0 ? 'minecraft:coarse_dirt' : 'minecraft:air' };
    return { get typeId() { return block.typeId; }, get isAir() { return block.typeId === 'minecraft:air'; },
      setType(typeId) { writes.push({ at, typeId }); if (failWrite) throw Error('Injected failed write');
        block.typeId = typeId; blocks.set(at, block); } };
  } };
  function put(at, typeId) { blocks.set(at, { typeId }); }
  function entity(id) {
    const e = { id, typeId: 'fc:guild_apprentice_might', isValid: true, dimension: dim,
      location: { x:101,y:1,z:61 }, tags: new Set(), placements: [], events: [],
      getTags() { return [...this.tags]; }, hasTag(tag) { return this.tags.has(tag); },
      addTag(tag) { this.tags.add(tag); }, removeTag(tag) { this.tags.delete(tag); },
      triggerEvent(event) { this.events.push(event); }, playAnimation() {},
      tryTeleport(point) { this.placements.push({ ...point }); this.location = { ...point }; return true; } };
    entities.push(e); return e;
  }
  const world = { getDynamicProperty(name) { propertyReads.push(name);
    if (failFlag && retiredKeys.includes(name)) throw Error('Injected old-flag failure');
    return props.get(name); },
    setDynamicProperty(name, value) { propertyWrites.push({ name, value }); props.set(name, value); },
    getTimeOfDay: () => 1000 };
  function reload() {
    const context = vm.createContext({ ...Object.fromEntries(Object.keys(training).map(k => [k, training[k]])),
      world, OW: () => dim, guildBounds: () => ({ base: { x:0,y:0,z:0 } }), TICKS: () => tick,
      system: { runTimeout() {}, get currentTick() { return tick; } },
      isMarried: () => false, isInsideGuild: () => true, guildApprentices: () => entities,
      placeGuildAnnexes: () => adjacent.push('caves'), repairGuildTerrain: () => adjacent.push('terrain'),
      repairGuildSkirtVegetation: () => adjacent.push('skirt'),
    });
    const names = ['GUILD', 'nextSparTick', 'nextArcheryTick', 'sparTurn', 'guildTraining',
      'localGuildPoint', 'distanceXZ', 'playSparExchange', 'showPracticeShot',
      'clearGuildRingScarecrows', 'repairGuildDemonApproach'];
    vm.runInContext(names.map(declaration).filter(Boolean).map(node => main.slice(...node.range)).join('\n'), context);
    runtime = vm.runInContext(`(${main.slice(...interval.expression.arguments[0].range)})`, context);
  }
  reload();
  return { props, blocks, writes, reads, propertyWrites, propertyReads, adjacent, put, entity, reload,
    run() { runtime(); tick += 10; } };
}

function foreignConstruction(f) {
  f.put('66,0,90', 'minecraft:diamond_block'); f.put('66,1,90', 'minecraft:chest');
  f.put('99,1,59', 'minecraft:hay_block'); f.put('63,2,87', 'minecraft:hay_block');
}
function assertPreserved(f, saved) {
  assert.equal(f.writes.length, 0, 'Maintenance attempted to overwrite saved geometry');
  assert.deepEqual([...f.blocks], saved, 'Every observed player block survives');
  assert.equal(f.propertyWrites.length, 0, 'Missing flags do not enroll a geometry migration');
}

test('missing legacy flags preserve player floors, containers and both scarecrow sites', () => {
  const f = fixture(); foreignConstruction(f); const saved = structuredClone([...f.blocks]);
  f.run(); assertPreserved(f, saved);
  assert.deepEqual(f.adjacent, ['caves', 'terrain', 'skirt'], 'Adjacent owners still execute');
  for (const name of retiredKeys) assert.equal(f.props.has(name), false);
});

test('existing true, false and unknown legacy flag values are retained across reload', () => {
  for (const legacyFlags of [true, false, 'unrecognized']) {
    const f = fixture({ legacyFlags }); foreignConstruction(f); const saved = structuredClone([...f.blocks]);
    f.run(); f.reload(); f.run(); assertPreserved(f, saved);
    for (const name of retiredKeys) assert.equal(f.props.get(name), legacyFlags);
  }
});

test('unloaded former footprint cells cannot cause repeated clears of new player edits', () => {
  const f = fixture({ failRead: '65,0,84' }); foreignConstruction(f);
  f.run(); f.put('66,1,90', 'minecraft:barrel'); const saved = structuredClone([...f.blocks]);
  f.run(); f.reload(); f.run(); assertPreserved(f, saved);
});

test('unreadable cells and write failures never authorize a repair attempt', () => {
  for (const options of [{ failRead: 'throw' }, { failWrite: true }]) {
    const f = fixture(options); foreignConstruction(f); const saved = structuredClone([...f.blocks]);
    assert.doesNotThrow(() => f.run()); assertPreserved(f, saved);
  }
});

test('obsolete flag read failures do not interrupt cave, terrain or apprentice maintenance', () => {
  const f = fixture({ failFlag: true }); assert.doesNotThrow(() => f.run());
  assert.deepEqual(f.adjacent, ['caves', 'terrain', 'skirt']);
  assert.equal(f.propertyReads.some(name => retiredKeys.includes(name)), false);
});

test('unplaced Guilds do not enter maintenance or enroll old geometry', () => {
  const f = fixture(); f.props.set('fc_guild_placed', false); foreignConstruction(f);
  const saved = structuredClone([...f.blocks]); f.run(); assertPreserved(f, saved);
  assert.deepEqual(f.adjacent, []);
});

test('blocked legacy training station is preserved and refused by the actual session owner', () => {
  const f = fixture(); f.put('99,1,61', 'minecraft:chest');
  const a = f.entity('a'), b = f.entity('b'); const saved = structuredClone([...f.blocks]);
  f.run(); f.run(); f.reload(); f.run(); assertPreserved(f, saved);
  assert.equal(a.placements.length, 0); assert.equal(b.placements.length, 0);
  assert.equal(a.tags.size, 0); assert.equal(b.tags.size, 0);
});

test('clear training stations still acquire once through the actual maintenance callback', () => {
  const f = fixture(), a = f.entity('a'), b = f.entity('b'); f.run(); f.run();
  assert.equal(a.placements.length, 1); assert.equal(b.placements.length, 1);
  assert.equal(f.writes.length, 0); assert.equal(f.propertyWrites.length, 0);
  assert.ok(a.tags.has('fc_train_ring_a')); assert.ok(b.tags.has('fc_train_ring_b'));
});

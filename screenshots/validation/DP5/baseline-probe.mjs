// Actual main.js adapters/callbacks and owned pilot/aperture modules, evaluated
// at mocked Bedrock boundaries. Run with node --experimental-vm-modules.
import test from 'node:test';
import assert from 'node:assert/strict';
import vm from 'node:vm';
import { readFile } from 'node:fs/promises';
import { parse } from 'espree';
import { resolve } from 'node:path';

// Optional repository snapshot root and expectation mode ('before' or 'after').
const sourceRoot = resolve(process.argv[2] ?? '.');
const expectation = process.argv[3] ?? 'after';
assert.ok(['before', 'after'].includes(expectation));
const main = await readFile(resolve(sourceRoot, 'packs/Fablecraft_BP/scripts/main.js'), 'utf8');
const ast = parse(main, { ecmaVersion: 'latest', sourceType: 'module', range: true });
const sources = await Promise.all(['fc_demon_doors.js', 'guild_door_aperture.js', 'fc_gamedata.js']
  .map((name) => readFile(resolve(sourceRoot, `packs/Fablecraft_BP/scripts/${name}`), 'utf8')));
const text = (node) => main.slice(...node.range);
const plain = (value) => JSON.parse(JSON.stringify(value));
const add = (a, b) => ({ x: a.x + b.x, y: a.y + b.y, z: a.z + b.z });
const cell = (p) => `${Math.floor(p.x)},${Math.floor(p.y)},${Math.floor(p.z)}`;
const declarations = (names) => names.map((name) => {
  const node = ast.body.find((entry) => entry.type === 'FunctionDeclaration' && entry.id.name === name
    || entry.type === 'VariableDeclaration' && entry.declarations.some((d) => d.id.name === name));
  assert.ok(node, `Production declaration ${name} exists`);
  return text(node);
}).join('\n');

async function fixture() {
  const errors = [], operations = [], timers = [], entities = [], players = [], blocks = new Map(), properties = new Map();
  const forms = [], payouts = [], placements = [], callbacks = {};
  const source = { x: 100, y: 65, z: 200, dimension: 'minecraft:overworld' };
  properties.set('fc_guild_door', JSON.stringify(source));
  const context = vm.createContext({ console: { warn: (message) => errors.push(message), log() {} } });
  const modules = [];
  for (const contents of sources) {
    const loaded = new vm.SourceTextModule(contents, { context });
    await loaded.link(() => { throw new Error('Injected owned modules have no engine imports'); });
    await loaded.evaluate(); modules.push(loaded.namespace);
  }
  const [pilotApi, apertureApi, dataApi] = modules;
  const system = { currentTick: 0, run(fn) { timers.push(fn); }, runTimeout(fn) { timers.push(fn); } };
  function blockAt(p, type = Math.floor(p.y) === 64 ? 'minecraft:cobblestone' : 'minecraft:air') {
    const key = cell(p);
    if (!blocks.has(key)) blocks.set(key, { location: { x: Math.floor(p.x), y: Math.floor(p.y), z: Math.floor(p.z) },
      typeId: type, get isAir() { return this.typeId === 'minecraft:air'; },
      setType(id) { this.typeId = id; operations.push({ kind: 'block', key, id }); }, getComponent() { return undefined; } });
    return blocks.get(key);
  }
  const dimension = {
    id: 'minecraft:overworld', getBlock: blockAt,
    getEntities(query) {
      if (this.failScan) throw new Error('injected unloaded entity scan');
      return entities.filter((e) => !e.removed && e.dimension.id === this.id && (!query.type || query.type === e.typeId)
        && (!query.location || Math.hypot(e.location.x - query.location.x, e.location.y - query.location.y, e.location.z - query.location.z) <= query.maxDistance));
    },
    runCommand(command) { operations.push({ kind: 'command', command, dimension: this.id }); return { successCount: 1 }; },
    spawnParticle() {},
  };
  const nether = { ...dimension, id: 'minecraft:nether' };
  const world = {
    getDynamicProperty: (key) => properties.get(key),
    setDynamicProperty(key, value) { operations.push({ kind: 'property', key, value }); if (value === undefined) properties.delete(key); else properties.set(key, value); },
    getPlayers: () => players,
    getDimension: (id) => id === 'nether' || id === 'minecraft:nether' ? nether : dimension,
    structureManager: { place(id, dim, origin, options) { placements.push({ id, dim, origin, options }); } },
  };
  function face({ location = source, open = false, index = 4 } = {}) {
    const props = new Map([['fc_door_open', open], ['fc_door_idx', index]]);
    const e = { id: `door-${entities.length}`, typeId: 'fc:demon_door', location: { ...location }, dimension, props,
      getDynamicProperty: (key) => props.get(key), setDynamicProperty: (key, value) => props.set(key, value),
      triggerEvent() {}, teleport(at) { this.location = plain(at); },
      remove() { if (this.failRemove) throw new Error('injected remove race'); this.removed = true; operations.push({ kind: 'remove', id: this.id }); } };
    entities.push(e); return e;
  }
  function spawn(dim, type, at) {
    operations.push({ kind: 'spawn', type, at });
    const e = face({ location: at, index: undefined }); e.dimension = dim; return e;
  }
  function player() {
    const props = new Map(), messages = [], moves = [];
    const p = { id: `hero-${players.length}`, typeId: 'minecraft:player', dimension,
      location: { x: 100.5, y: 65, z: 196.5 }, currentHeld: { typeId: 'minecraft:lantern' }, isSneaking: false,
      getDynamicProperty: (key) => props.get(key), setDynamicProperty: (key, value) => value === undefined ? props.delete(key) : props.set(key, value),
      getComponent: (name) => name === 'minecraft:equippable' ? { getEquipment: () => p.currentHeld } : undefined,
      sendMessage: (message) => messages.push(message), playSound() {},
      tryTeleport(at, options) { moves.push({ at: plain(at), options }); this.location = plain(at); this.dimension = options.dimension; return true; },
      messages, moves, props };
    players.push(p); return p;
  }
  class MessageFormData {
    constructor() { forms.push(this); }
    title() { return this; } body() { return this; } button1() { return this; } button2() { return this; }
    show() { return { then: (fn) => { this.resolve = fn; } }; }
  }
  let configuration;
  Object.assign(context, {
    world, system, DATA: dataApi.DATA,
    createGuildDoorAperture: apertureApi.createGuildDoorAperture,
    createDemonDoorPilot: (options) => { configuration = options; return pilotApi.createDemonDoorPilot(options); },
    ItemStack: class {}, EquipmentSlot: { Mainhand: 'Mainhand' }, MessageFormData,
    TICKS: () => system.currentTick, OW: () => dimension, trySpawn: spawn,
    morality: () => 0, countItem: () => 100, removeItem: () => true, P: { get: () => 0 },
    openDemonDoor: (...args) => payouts.push(args), doorRiddle: (...args) => payouts.push(['riddle', ...args]),
    hash2: () => 0.75,
  });
  vm.runInContext(declarations(['guildDoorAperture', 'guildDoorPilot', 'isGuildDoorSource', 'ensureGuildDoorPilot',
    'guildDoorWorldExcluded', 'heldItem', 'doorPersona', 'demonDoorTalk', 'ensureDemonDoor', 'ensureAllDemonDoors', 'REGION', 'maybePlace']), context);
  const runtime = vm.runInContext('({guildDoorPilot,guildDoorAperture,ensureGuildDoorPilot,isGuildDoorSource,guildDoorWorldExcluded,demonDoorTalk,ensureDemonDoor,ensureAllDemonDoors,maybePlace,REGION})', context);
  function callback(prefix, contains = '', name = prefix) {
    const node = ast.body.find((entry) => entry.type === 'ExpressionStatement' && entry.expression.type === 'CallExpression'
      && text(entry).startsWith(prefix) && text(entry).includes(contains));
    assert.ok(node, `Actual main callback ${name}`);
    callbacks[name] = node;
    return vm.runInContext(`(${text(node.expression.arguments[0])})`, context);
  }
  const interact = callback('world.beforeEvents.playerInteractWithEntity.subscribe(');
  const portalTick = callback('system.runInterval(', 'guildDoorPilot.tick()', 'portal tick');
  const breakBlock = callback('world.beforeEvents.playerBreakBlock.subscribe(', 'guildDoorPilot');
  const useBlock = callback('world.beforeEvents.playerInteractWithBlock.subscribe(', 'guildDoorPilot');
  const itemUse = callback('world.beforeEvents.itemUse.subscribe(', 'guildDoorPilot');
  const explosion = callback('world.beforeEvents.explosion.subscribe(', 'guildDoorPilot');
  const scriptEvent = callback('system.afterEvents.scriptEventReceive.subscribe(', 'fc:door_return');
  const scatter = callback('system.runInterval(', 'maybePlace(p,', 'scatter');
  function readyRoom() {
    runtime.ensureGuildDoorPilot(dimension, source, true);
    const state = plain(runtime.guildDoorPilot.getState());
    state.unlocked = true; state.rewards.seeded = true;
    state.room = { cell: 0, origin: plain(pilotApi.realmOrigin(0)), version: 1, phase: 'ready', visited: true };
    properties.set(pilotApi.DOOR_STATE_KEY, JSON.stringify(state));
    return state.room.origin;
  }
  function flush() { while (timers.length) timers.shift()(); }
  return { runtime, context, world, dimension, nether, source, player, face, entities, players, blocks, blockAt,
    properties, operations, placements, forms, payouts, errors, configuration, callbacks, pilotApi, timers, system,
    readyRoom, flush, interact, portalTick, breakBlock, useBlock, itemUse, explosion, scriptEvent, scatter };
}


const { createHash } = await import('node:crypto');
const results = [];
for (const failure of ['intact', 'missing', 'corrupt', 'unreadable', 'recreated', 'replacement']) {
  const f = await fixture(), origin = f.readyRoom(), visitor = f.player();
  const source = { x: 100.5, y: 65, z: 196.5, dimension: f.dimension.id };
  visitor.location = add(origin, f.pilotApi.ARCANUM.arrival);
  visitor.props.set(f.pilotApi.DOOR_RETURN_KEY, JSON.stringify({ schema: 1, doorId: 'guild', cell: 0, source, phase: 'inside' }));
  if (['missing', 'recreated'].includes(failure)) f.properties.delete(f.pilotApi.DOOR_STATE_KEY);
  if (failure === 'corrupt') f.properties.set(f.pilotApi.DOOR_STATE_KEY, '{broken');
  if (failure === 'unreadable') {
    const native = f.world.getDynamicProperty;
    f.world.getDynamicProperty = key => { if (key === f.pilotApi.DOOR_STATE_KEY) throw new Error('injected world read failure'); return native(key); };
  }
  if (failure === 'recreated') { f.player(); f.system.currentTick = 40; f.portalTick(); assert.equal(f.runtime.guildDoorPilot.getState().room, null); }
  if (failure === 'replacement') {
    const replacement = plain(f.runtime.guildDoorPilot.getState());
    replacement.room = { ...replacement.room, cell: 8, origin: plain(f.pilotApi.realmOrigin(8)) };
    f.properties.set(f.pilotApi.DOOR_STATE_KEY, JSON.stringify(replacement));
  }
  const before = f.properties.get(f.pilotApi.DOOR_STATE_KEY);
  const block = { location: add(origin, { x: 24, y: 2, z: 10 }), typeId: 'minecraft:cobblestone' };
  const breaking = { dimension: f.dimension, player: visitor, block, cancel: false }; f.breakBlock(breaking);
  const placing = { player: visitor, block, cancel: false }; f.useBlock(placing);
  const pearl = { source: visitor, itemStack: { typeId: 'minecraft:ender_pearl' }, cancel: false }; f.itemUse(pearl);
  let impacted = null;
  f.explosion({ dimension: f.dimension, getImpactedBlocks: () => [block], setImpactedBlocks: value => impacted = value });
  const excluded = f.runtime.guildDoorWorldExcluded(visitor);
  const scatterCalls = []; f.context.maybePlace = (...args) => scatterCalls.push(args); f.scatter();
  // Exercise the actual boss interval and its real quest-data mapping. The
  // injected RNG selects its normal 25% branch; trySpawn records the request.
  const bossFamilies = ['fc_wasp_queen','fc_white_balverine','fc_jack','fc_jack_dragon','fc_troll','fc_banshee','fc_twinblade'];
  const quest = f.context.DATA.quests.find(q => q.objectives.some(o => o.type === 'kill' && bossFamilies.includes(o.family)));
  assert.ok(quest);
  f.context.activeQuest = p => p === visitor ? { id: quest.id, progress: quest.objectives.map(() => 0) } : null;
  f.context.Math = Object.assign(Object.create(Math), { random: () => 0 });
  const bossNode = ast.body.find(n => n.type === 'ExpressionStatement' && text(n).startsWith('system.runInterval(') && text(n).includes('Your quarry has found YOU.'));
  assert.ok(bossNode);
  const bossTick = vm.runInContext(`(${text(bossNode.expression.arguments[0])})`, f.context);
  const operations = f.operations.length; bossTick();
  const bossSpawnRequests = f.operations.slice(operations).filter(op => op.kind === 'spawn').map(op => op.type);
  const occupied = f.runtime.guildDoorPilot.occupiedRealm(visitor);
  const sourceReturnSucceeded = f.runtime.guildDoorPilot.requestReturn(visitor);
  assert.equal(sourceReturnSucceeded, true);
  assert.equal(f.properties.get(f.pilotApi.DOOR_STATE_KEY), before);
  assert.equal(f.placements.length, 0);
  const result = { failure, occupied, breakCancelled: breaking.cancel, placementInteractionCancelled: placing.cancel,
    pearlCancelled: pearl.cancel, explosionBlocksRetained: impacted.length, excluded,
    scatterCalls: scatterCalls.length, bossSpawnRequests, sourceReturnSucceeded };
  if (failure === 'intact' || expectation === 'after') {
    assert.equal(result.breakCancelled, true); assert.equal(result.placementInteractionCancelled, true);
    assert.equal(result.explosionBlocksRetained, 0); assert.equal(result.excluded, true);
    assert.equal(result.scatterCalls, failure === 'recreated' ? 9 : 0); assert.deepEqual(result.bossSpawnRequests, []);
  } else {
    assert.equal(result.breakCancelled, false); assert.equal(result.placementInteractionCancelled, false);
    assert.equal(result.explosionBlocksRetained, 1); assert.equal(result.excluded, false);
    assert.ok(result.scatterCalls >= 9); assert.equal(result.bossSpawnRequests.length, 1);
  }
  assert.equal(result.occupied, true); assert.equal(result.pearlCancelled, true);
  results.push(result);
}
const hash = value => createHash('sha256').update(value).digest('hex');
const scope = declarations(['guildDoorPilot','guildDoorWorldExcluded']) + ast.body.filter(n => n.type === 'ExpressionStatement' && (text(n).includes('guildDoorPilot.protectsBlock') || text(n).includes('guildDoorPilot.occupiedRealm') || text(n).includes('Your quarry has found YOU.'))).map(text).join('\n');
console.log(JSON.stringify({ sourceRoot, expectation, engine_acceptance: 'unrun', sources: { mainUtf8: hash(main), portalUtf8: hash(sources[0]), apertureUtf8: hash(sources[1]), gamedataUtf8: hash(sources[2]), relevantMainScopeUtf8: hash(scope) }, results }, null, 2));

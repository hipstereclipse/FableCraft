// Actual main.js adapters/callbacks and owned pilot/aperture modules, evaluated
// at mocked Bedrock boundaries. Run with node --experimental-vm-modules.
import test from 'node:test';
import assert from 'node:assert/strict';
import vm from 'node:vm';
import { readFile } from 'node:fs/promises';
import { parse } from 'espree';

const main = await readFile('packs/Fablecraft_BP/scripts/main.js', 'utf8');
const ast = parse(main, { ecmaVersion: 'latest', sourceType: 'module', range: true });
const sources = await Promise.all(['fc_demon_doors.js', 'guild_door_aperture.js', 'fc_gamedata.js']
  .map((name) => readFile(`packs/Fablecraft_BP/scripts/${name}`, 'utf8')));
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
  const boss = callback('system.runInterval(', 'Your quarry has found YOU.', 'quest boss');
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
    readyRoom, flush, interact, portalTick, breakBlock, useBlock, itemUse, explosion, scriptEvent, scatter, boss };
}


// Audit-only observation probe: no production writes outside these in-memory fixtures.
const { createHash } = await import('node:crypto');
const results = [];
for (const path of ['readable', 'readable_blocked_default', 'periodic_unreadable', 'periodic_unreadable_blocked_default', 'command_unreadable', 'arch_click_unreadable', 'missing_ticket', 'corrupt_ticket', 'both_unreadable']) {
  const f = await fixture(), origin = f.readyRoom(), visitor = f.player();
  visitor.location = add(origin, f.pilotApi.ARCANUM.arrival);
  const exact = { x: f.source.x + 2.1, y: f.source.y, z: f.source.z - 4.5, dimension: f.dimension.id };
  const fallback = { x: f.source.x + 0.5, y: f.source.y, z: f.source.z - 3.5, dimension: f.dimension.id };
  if (path.includes('blocked_default')) {
    for (let x = 97; x <= 104; x++) f.blockAt({ x, y: 65, z: 196 }, 'minecraft:stone');
  }
  const original = JSON.stringify({ schema: 1, doorId: 'guild', cell: 0, source: exact, phase: 'inside' });
  visitor.props.set(f.pilotApi.DOOR_RETURN_KEY, original);
  if (path === 'missing_ticket') visitor.props.delete(f.pilotApi.DOOR_RETURN_KEY);
  if (path === 'corrupt_ticket') visitor.props.set(f.pilotApi.DOOR_RETURN_KEY, '{broken');
  const before = visitor.props.get(f.pilotApi.DOOR_RETURN_KEY), worldBefore = f.properties.get(f.pilotApi.DOOR_STATE_KEY);
  const nativeRead = visitor.getDynamicProperty;
  let errors = 0;
  if (path.includes('unreadable')) visitor.getDynamicProperty = key => {
    if (key === f.pilotApi.DOOR_RETURN_KEY) { errors++; throw new Error('temporarily unavailable player ticket read'); }
    return nativeRead(key);
  };
  if (path === 'both_unreadable') {
    const read = f.world.getDynamicProperty;
    f.world.getDynamicProperty = key => { if (key === f.pilotApi.DOOR_STATE_KEY) throw new Error('temporarily unavailable primary read'); return read(key); };
  }
  let afterReconcile;
  if (path.startsWith('readable') || path.startsWith('periodic_unreadable') || path === 'both_unreadable') {
    f.system.currentTick = 45; f.portalTick(); afterReconcile = visitor.props.get(f.pilotApi.DOOR_RETURN_KEY);
    visitor.getDynamicProperty = nativeRead;
    if (path !== 'both_unreadable') f.scriptEvent({ id: 'fc:door_return', sourceEntity: visitor });
  } else if (path === 'arch_click_unreadable') {
    const use = { player: visitor, block: { location: add(origin, { x: 24, y: 2, z: 3 }), typeId: 'minecraft:stone' }, cancel: false };
    f.useBlock(use); assert.equal(use.cancel, true); assert.equal(f.timers.length, 1); f.flush();
  } else f.scriptEvent({ id: 'fc:door_return', sourceEntity: visitor });
  visitor.getDynamicProperty = nativeRead;
  const expected = path.startsWith('readable') ? exact : fallback;
  if (path === 'both_unreadable') {
    assert.equal(visitor.props.get(f.pilotApi.DOOR_RETURN_KEY), before); assert.equal(visitor.moves.length, 0);
  } else if (path === 'periodic_unreadable_blocked_default') {
    assert.equal(visitor.moves.length, 0);
    assert.deepEqual(JSON.parse(visitor.props.get(f.pilotApi.DOOR_RETURN_KEY)).source, fallback);
    f.scriptEvent({ id: 'fc:door_return', sourceEntity: visitor });
    assert.equal(visitor.moves.length, 0, 'restored readable history no longer contains the safe original approach');
  } else {
    assert.equal(visitor.moves.length, 1);
    assert.deepEqual(visitor.location, { x: expected.x, y: expected.y, z: expected.z });
    assert.equal(visitor.props.has(f.pilotApi.DOOR_RETURN_KEY), false);
  }
  if (path.startsWith('readable')) assert.equal(afterReconcile, original);
  if (path.startsWith('periodic_unreadable')) {
    assert.deepEqual(JSON.parse(afterReconcile).source, fallback);
    assert.notEqual(afterReconcile, original, 'read failure overwrites readable backing history with a guessed approach');
  }
  assert.equal(f.properties.get(f.pilotApi.DOOR_STATE_KEY), worldBefore);
  assert.equal(f.placements.length, 0);
  results.push({ path, ticket_read_errors: errors, original_source: exact,
    default_return_corridor_blocked: path.includes('blocked_default'),
    source_after_periodic_reconciliation: afterReconcile ? JSON.parse(afterReconcile).source : null,
    return_moves: visitor.moves.length, returned_to: visitor.moves.length ? visitor.location : null,
    ticket_backing_history_preserved: visitor.props.get(f.pilotApi.DOOR_RETURN_KEY) === before,
    default_approach_used: visitor.moves.length ? visitor.location.x === fallback.x && visitor.location.z === fallback.z : false,
    world_history_unchanged: true, structures_placed: 0 });
}
const hash = value => createHash('sha256').update(value).digest('hex');
console.log(JSON.stringify({ audited_head: 'c83246751b86aa489897efa3d0cadd49f303c588 plus GP19 working edits',
  source_sha256: { main: hash(main), portal: hash(sources[0]), aperture: hash(sources[1]), gamedata: hash(sources[2]) }, results }, null, 2));

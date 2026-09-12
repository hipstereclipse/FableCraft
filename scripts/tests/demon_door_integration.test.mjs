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

test('production singleton passes canonical data, aperture gate and literal destination placement', async () => {
  const f = await fixture();
  assert.equal(f.configuration.definition.id, 'guild_library_arcanum');
  assert.equal(f.configuration.definition.requirement.item, 'minecraft:lantern');
  f.configuration.placeRoom(f.dimension, { x: 600000, y: 272, z: 600000 });
  assert.equal(f.placements[0].id, 'fc:library_arcanum');
  assert.equal(f.placements[0].options.includeEntities, false);
  const obstacle = f.blockAt(add(f.source, { x: 0, y: 1, z: 2 })); obstacle.typeId = 'minecraft:diamond_block';
  assert.equal(f.configuration.sourceReady(f.source), false);
  assert.equal(obstacle.typeId, 'minecraft:diamond_block');
});

test('production maintenance preserves a paid survivor before removing duplicate mouth faces', async () => {
  const f = await fixture(), closed = f.face(), paid = f.face({ open: true, index: 7 });
  f.runtime.ensureGuildDoorPilot(f.dimension);
  assert.equal(f.runtime.guildDoorPilot.getState().legacy.status, 'surviving_open');
  assert.equal(f.runtime.guildDoorPilot.getState().legacy.idx, 7);
  assert.equal(f.runtime.guildDoorPilot.getState().rewards.suppressed, true);
  assert.equal(paid.location.y, f.source.y + 5);
  assert.ok(closed.removed || closed.location.y >= f.source.y + 5, 'no inherited closed mouth collider remains');
  assert.equal(f.operations.filter((entry) => entry.kind === 'spawn').length, 0);
  const save = f.operations.findIndex((entry) => entry.kind === 'property' && entry.key === f.pilotApi.DOOR_STATE_KEY);
  const removal = f.operations.findIndex((entry) => entry.kind === 'remove');
  assert.ok(removal < 0 || save < removal, 'payment is preserved before face cleanup');
  f.runtime.ensureGuildDoorPilot(f.dimension);
  assert.equal(f.entities.filter((e) => !e.removed).length, 1);
});

test('new-world registration precedes missing chunks; replacement cannot lose new/legacy status', async () => {
  const f = await fixture(); f.dimension.failScan = true;
  f.runtime.ensureGuildDoorPilot(f.dimension, f.source, true);
  assert.equal(f.runtime.guildDoorPilot.getState().legacy.status, 'new');
  assert.equal(f.entities.length, 0);
  f.dimension.failScan = false; f.runtime.ensureGuildDoorPilot(f.dimension);
  assert.equal(f.entities.length, 1); assert.equal(f.runtime.guildDoorPilot.getState().rewards.suppressed, false);
  const saves = f.operations.findIndex((entry) => entry.kind === 'property' && entry.key === f.pilotApi.DOOR_STATE_KEY);
  const spawn = f.operations.findIndex((entry) => entry.kind === 'spawn'); assert.ok(saves < spawn);
  const g = await fixture(); g.runtime.ensureGuildDoorPilot(g.dimension);
  assert.equal(g.runtime.guildDoorPilot.getState().legacy.status, 'history_unknown');
  assert.equal(g.runtime.guildDoorPilot.getState().rewards.suppressed, true);
});

test('a transient surviving-face history read defers registration without reauthorizing paid rewards', async () => {
  for (const failedKey of ['fc_door_open', 'fc_door_idx']) {
    const f = await fixture(), paid = f.face({ open: true, index: 7 });
    const original = paid.getDynamicProperty;
    let openReads = 0;
    paid.getDynamicProperty = (key) => {
      if (key === 'fc_door_open') openReads++;
      if (key === failedKey && (key !== 'fc_door_open' || openReads === 2)) throw new Error('injected legacy history read');
      return original(key);
    };
    f.runtime.ensureGuildDoorPilot(f.dimension);
    assert.equal(f.properties.has(f.pilotApi.DOOR_STATE_KEY), false, failedKey);
    assert.equal(paid.props.get('fc_door_open'), true);
    assert.equal(f.operations.filter((entry) => ['spawn', 'remove'].includes(entry.kind)).length, 0);
    paid.getDynamicProperty = original;
    f.runtime.ensureGuildDoorPilot(f.dimension);
    const state = f.runtime.guildDoorPilot.getState();
    assert.equal(state.unlocked, true);
    assert.equal(state.legacy.status, 'surviving_open');
    assert.equal(state.rewards.suppressed, true);
    assert.equal(state.room, null);
    assert.equal(f.placements.length, 0);
  }
});

test('periodic source re-registration cannot strand a committed visitor at the original return arch', async () => {
  const f = await fixture(), origin = f.readyRoom(), visitor = f.player();
  f.player(); // A second visitor at the Guild triggers the actual maintenance adapter.
  f.runtime.ensureGuildDoorPilot(f.dimension);
  const source = { x: 100.5, y: 65, z: 196.5, dimension: f.dimension.id };
  visitor.location = add(origin, f.pilotApi.ARCANUM.arrival);
  visitor.props.set(f.pilotApi.DOOR_RETURN_KEY, JSON.stringify({ schema: 1, doorId: 'guild', cell: 0, source, phase: 'inside' }));
  f.properties.delete(f.pilotApi.DOOR_STATE_KEY);
  f.system.currentTick = 40;
  f.portalTick(); // Recreates a valid ledger with room:null before return reconciliation.
  const recreated = f.properties.get(f.pilotApi.DOOR_STATE_KEY);
  assert.equal(f.runtime.guildDoorPilot.getState().room, null);
  assert.equal(f.runtime.guildDoorPilot.occupiedRealm(visitor), true);
  visitor.location = add(origin, f.pilotApi.ARCANUM.exit);
  for (let tick = 45; tick <= 75; tick += 5) { f.system.currentTick = tick; f.portalTick(); }
  assert.deepEqual(visitor.location, { x: source.x, y: source.y, z: source.z });
  assert.equal(visitor.props.has(f.pilotApi.DOOR_RETURN_KEY), false);
  assert.equal(f.properties.get(f.pilotApi.DOOR_STATE_KEY), recreated, 'Recovery never resets unlocks, claims or room state');
  assert.equal(f.placements.length, 0, 'Recovery never builds or reseeds a room');
});

test('a lone visitor can walk through the remembered exit while the primary ledger is missing, corrupt or unreadable', async () => {
  for (const failure of ['missing', 'corrupt', 'unreadable']) {
    const f = await fixture(), origin = f.readyRoom(), visitor = f.player();
    const source = { x: 100.5, y: 65, z: 196.5, dimension: f.dimension.id };
    visitor.location = add(origin, f.pilotApi.ARCANUM.arrival);
    visitor.props.set(f.pilotApi.DOOR_RETURN_KEY, JSON.stringify({ schema: 1, doorId: 'guild', cell: 0, source, phase: 'inside' }));
    if (failure === 'missing') f.properties.delete(f.pilotApi.DOOR_STATE_KEY);
    else if (failure === 'corrupt') f.properties.set(f.pilotApi.DOOR_STATE_KEY, '{broken');
    else {
      const native = f.world.getDynamicProperty;
      f.world.getDynamicProperty = key => { if (key === f.pilotApi.DOOR_STATE_KEY) throw new Error('injected world read failure'); return native(key); };
    }
    const original = f.properties.get(f.pilotApi.DOOR_STATE_KEY);
    f.system.currentTick = 40; f.portalTick(); // Nobody at the Guild can re-register this ledger.
    visitor.location = add(origin, f.pilotApi.ARCANUM.exit);
    for (let tick = 45; tick <= 75; tick += 5) { f.system.currentTick = tick; f.portalTick(); }
    assert.deepEqual(visitor.location, { x: source.x, y: source.y, z: source.z }, failure);
    assert.equal(visitor.props.has(f.pilotApi.DOOR_RETURN_KEY), false);
    assert.equal(f.properties.get(f.pilotApi.DOOR_STATE_KEY), original);
    assert.equal(f.placements.length, 0);
  }
});

test('unavailable-ledger periodic dwell cannot invent return authority for an unticketed or invalid-ticket occupant', async () => {
  for (const failure of ['missing', 'corrupt', 'unreadable']) for (const ticketMode of ['absent', 'invalid']) {
    const f = await fixture(), origin = f.readyRoom(), visitor = f.player();
    visitor.location = add(origin, f.pilotApi.ARCANUM.arrival);
    if (ticketMode === 'invalid') visitor.props.set(f.pilotApi.DOOR_RETURN_KEY, JSON.stringify({ schema: 1, doorId: 'guild',
      cell: 4096, source: { x: 100.5, y: 65, z: 196.5, dimension: f.dimension.id }, phase: 'inside' }));
    if (failure === 'missing') f.properties.delete(f.pilotApi.DOOR_STATE_KEY);
    else if (failure === 'corrupt') f.properties.set(f.pilotApi.DOOR_STATE_KEY, '{broken');
    else {
      const native = f.world.getDynamicProperty;
      f.world.getDynamicProperty = key => { if (key === f.pilotApi.DOOR_STATE_KEY) throw new Error('injected world read failure'); return native(key); };
    }
    const originalWorld = f.properties.get(f.pilotApi.DOOR_STATE_KEY);
    const originalTicket = visitor.props.get(f.pilotApi.DOOR_RETURN_KEY);
    f.system.currentTick = 40; f.portalTick();
    visitor.location = add(origin, f.pilotApi.ARCANUM.exit);
    for (let tick = 45; tick <= 100; tick += 5) { f.system.currentTick = tick; f.portalTick(); }
    assert.equal(visitor.moves.length, 0, `${failure}/${ticketMode}`);
    assert.equal(visitor.props.get(f.pilotApi.DOOR_RETURN_KEY), originalTicket);
    assert.equal(f.properties.get(f.pilotApi.DOOR_STATE_KEY), originalWorld);
    assert.equal(f.placements.length, 0);
  }
});

test('a ticket for an occupied old cell survives replacement-ledger return failures and uses its exact source', async () => {
  const f = await fixture(), origin = f.readyRoom(), visitor = f.player();
  const source = { x: 100.5, y: 65, z: 196.5, dimension: f.dimension.id };
  const ticket = { schema: 1, doorId: 'guild', cell: 0, source, phase: 'inside' };
  visitor.location = add(origin, f.pilotApi.ARCANUM.arrival);
  visitor.props.set(f.pilotApi.DOOR_RETURN_KEY, JSON.stringify(ticket));
  const replacement = plain(f.runtime.guildDoorPilot.getState());
  replacement.room = { ...replacement.room, cell: 1, origin: plain(f.pilotApi.realmOrigin(1)) };
  replacement.rewards.claimed = [true, false, true, false];
  f.properties.set(f.pilotApi.DOOR_STATE_KEY, JSON.stringify(replacement));
  const savedWorld = f.properties.get(f.pilotApi.DOOR_STATE_KEY);
  const teleport = visitor.tryTeleport;
  visitor.tryTeleport = () => false;
  f.scriptEvent({ id: 'fc:door_return', sourceEntity: visitor });
  assert.ok(visitor.props.has(f.pilotApi.DOOR_RETURN_KEY));
  assert.equal(f.runtime.guildDoorPilot.occupiedRealm(visitor), true);
  visitor.tryTeleport = () => { throw new Error('injected return failure'); };
  f.scriptEvent({ id: 'fc:door_return', sourceEntity: visitor });
  assert.deepEqual(JSON.parse(visitor.props.get(f.pilotApi.DOOR_RETURN_KEY)).source, source);
  visitor.tryTeleport = (at, options) => { teleport.call(visitor, at, options); throw new Error('injected after-move failure'); };
  f.scriptEvent({ id: 'fc:door_return', sourceEntity: visitor });
  assert.deepEqual(visitor.location, { x: source.x, y: source.y, z: source.z });
  assert.equal(visitor.props.has(f.pilotApi.DOOR_RETURN_KEY), false);
  assert.equal(f.properties.get(f.pilotApi.DOOR_STATE_KEY), savedWorld);
  assert.equal(f.placements.length, 0);
});

test('a lowered ceiling above a fractional source approach selects a clear same-door fallback', async () => {
  const f = await fixture(), origin = f.readyRoom(), visitor = f.player();
  visitor.location = add(origin, f.pilotApi.ARCANUM.arrival);
  const source = { x: 100.5, y: 65.75, z: 196.5, dimension: f.dimension.id };
  visitor.props.set(f.pilotApi.DOOR_RETURN_KEY, JSON.stringify({ schema: 1, doorId: 'guild', cell: 0, source, phase: 'inside' }));
  // The approach was captured during a jump. Another visitor lowers the ceiling
  // while this player explores the room. Integer feet y65 still fit beneath it.
  f.blockAt({ x: 100, y: 67, z: 196 }, 'minecraft:stone');
  const native = visitor.tryTeleport, attempts = [];
  visitor.tryTeleport = (at, options) => {
    attempts.push(plain(at));
    if (at.x === 100.5 && at.z === 196.5 && at.y + 1.8 > 67) return false;
    return native.call(visitor, at, options);
  };
  const savedWorld = f.properties.get(f.pilotApi.DOOR_STATE_KEY);
  f.scriptEvent({ id: 'fc:door_return', sourceEntity: visitor });
  assert.deepEqual(visitor.location, { x: 100.5, y: 65, z: 196.5 });
  assert.deepEqual(attempts, [{ x: 100.5, y: 65, z: 196.5 }]);
  assert.equal(visitor.props.has(f.pilotApi.DOOR_RETURN_KEY), false);
  assert.equal(f.properties.get(f.pilotApi.DOOR_STATE_KEY), savedWorld);
});

test('replacement-ledger recovery rejects invalid or misplaced tickets and never borrows its source', async () => {
  const f = await fixture(), origin = f.readyRoom(), visitor = f.player();
  const source = { x: 100.5, y: 65, z: 196.5, dimension: f.dimension.id };
  const ticket = { schema: 1, doorId: 'guild', cell: 0, source, phase: 'inside' };
  const replacement = plain(f.runtime.guildDoorPilot.getState());
  replacement.room = { ...replacement.room, cell: 1, origin: plain(f.pilotApi.realmOrigin(1)) };
  replacement.source.x += 100;
  replacement.rewards.claimed = [true, true, true, true];
  f.properties.set(f.pilotApi.DOOR_STATE_KEY, JSON.stringify(replacement));
  const savedWorld = f.properties.get(f.pilotApi.DOOR_STATE_KEY);
  for (const invalid of [{ ...ticket, cell: 1 }, { ...ticket, cell: 4096 }, { ...ticket, phase: 'invalid' },
    { ...ticket, source: { ...source, dimension: 'missing:dimension' } }]) {
    visitor.location = add(origin, f.pilotApi.ARCANUM.arrival);
    visitor.props.set(f.pilotApi.DOOR_RETURN_KEY, JSON.stringify(invalid));
    f.scriptEvent({ id: 'fc:door_return', sourceEntity: visitor });
    assert.equal(visitor.moves.length, 0);
  }
  visitor.props.set(f.pilotApi.DOOR_RETURN_KEY, JSON.stringify(ticket));
  visitor.location = { x: 150, y: 65, z: 210 }; // A valid old ticket away from its recorded cell is inert.
  f.scriptEvent({ id: 'fc:door_return', sourceEntity: visitor });
  assert.equal(visitor.moves.length, 0);
  visitor.location = add(origin, f.pilotApi.ARCANUM.arrival);
  visitor.dimension = f.nether;
  f.scriptEvent({ id: 'fc:door_return', sourceEntity: visitor });
  assert.equal(visitor.moves.length, 0);
  visitor.dimension = f.dimension;
  f.blockAt({ x: 100, y: 65, z: 196 }, 'minecraft:stone');
  f.scriptEvent({ id: 'fc:door_return', sourceEntity: visitor });
  assert.equal(visitor.moves.length, 0, 'A blocked old source cannot borrow the replacement ledger destination');
  assert.ok(visitor.props.has(f.pilotApi.DOOR_RETURN_KEY));
  assert.equal(f.properties.get(f.pilotApi.DOOR_STATE_KEY), savedWorld);
  assert.equal(f.placements.length, 0);
});

test('actual deferred face interaction captures light-use item before event expiry', async () => {
  const f = await fixture(), p = f.player(), door = f.face();
  f.runtime.ensureGuildDoorPilot(f.dimension, f.source, true);
  const ev = { player: p, target: door, itemStack: { typeId: 'minecraft:lantern' }, cancel: false };
  f.interact(ev); assert.equal(ev.cancel, true); assert.equal(f.runtime.guildDoorPilot.getState().unlocked, false);
  ev.itemStack = { typeId: 'minecraft:apple' }; p.currentHeld = ev.itemStack; f.flush();
  assert.equal(f.runtime.guildDoorPilot.getState().unlocked, true);
  assert.equal(f.forms.length, 0); assert.equal(f.payouts.length, 0); assert.equal(p.moves.length, 0);
  const g = await fixture(), q = g.player(), otherDoor = g.face(); g.runtime.ensureGuildDoorPilot(g.dimension, g.source, true);
  const wrong = { player: q, target: otherDoor, itemStack: { typeId: 'minecraft:apple' }, cancel: false };
  g.interact(wrong); wrong.itemStack.typeId = 'minecraft:lantern'; g.flush();
  assert.equal(g.runtime.guildDoorPilot.getState().unlocked, false);
});

test('corrupt Guild progress never falls through to invented legacy challenge/payout', async () => {
  const f = await fixture(), p = f.player(), door = f.face();
  f.properties.set(f.pilotApi.DOOR_STATE_KEY, '{corrupt');
  f.runtime.demonDoorTalk(p, door, 'minecraft:lantern');
  assert.equal(f.properties.get(f.pilotApi.DOOR_STATE_KEY), '{corrupt');
  assert.equal(f.forms.length, 0); assert.equal(f.payouts.length, 0); assert.equal(f.entities.length, 1);
  assert.ok(p.messages.some((message) => message.includes('preserved')));
  door.props.set('fc_door_identity', 'guild'); door.location.x += 100;
  f.runtime.demonDoorTalk(p, door, 'minecraft:lantern');
  assert.equal(f.forms.length, 0, 'known Guild identity cannot become a random persona after displacement');
});

test('ordinary scattered door retains the existing requirement and payout path', async () => {
  const f = await fixture(), p = f.player(), door = f.face({ location: { x: 400, y: 65, z: 200 }, index: 4 });
  f.runtime.demonDoorTalk(p, door, 'minecraft:lantern');
  assert.equal(f.forms.length, 1); assert.equal(f.runtime.guildDoorPilot.getState(), null);
  f.forms[0].resolve({ canceled: false, selection: 0 });
  assert.equal(f.payouts.length, 1); assert.equal(f.payouts[0][2].id, 'hoarder');
});

test('five-tick production schedule repairs after reload without duplicate spawns', async () => {
  const f = await fixture(); f.player(); f.face({ open: true });
  const interval = f.callbacks['portal tick'].expression.arguments[1]; assert.equal(interval.value, 5);
  f.system.currentTick = 40; f.portalTick();
  assert.equal(f.runtime.guildDoorPilot.getState().unlocked, true);
  f.entities[0].removed = true; f.system.currentTick = 80; f.portalTick();
  assert.equal(f.entities.filter((e) => !e.removed).length, 1);
  assert.equal(f.entities.at(-1).location.y, f.source.y + 5);
  f.system.currentTick = 120; f.portalTick();
  assert.equal(f.entities.filter((e) => !e.removed).length, 1);
});

test('conflicting persisted hints cannot spawn repeated unkeyed faces or reset durable progress', async () => {
  const f = await fixture(); f.readyRoom();
  const record = plain(f.runtime.guildDoorPilot.getState());
  record.rewards.claimed = [true, false, true, false];
  f.properties.set(f.pilotApi.DOOR_STATE_KEY, JSON.stringify(record));
  const saved = f.properties.get(f.pilotApi.DOOR_STATE_KEY);
  f.entities[0].removed = true;
  const stale = { ...f.source, x: f.source.x + 300 };
  f.properties.set('fc_guild_door', JSON.stringify(stale));
  const unrelated = f.face({ location: stale, index: 7 });
  for (let i = 0; i < 4; i++) f.runtime.ensureGuildDoorPilot(f.dimension, stale, true);
  const active = f.entities.filter(e => !e.removed && e !== unrelated);
  assert.equal(active.length, 1);
  assert.equal(active[0].props.get('fc_door_identity'), 'guild');
  assert.deepEqual(active[0].location, { x: f.source.x, y: f.source.y + 5, z: f.source.z });
  assert.equal(unrelated.removed, undefined, 'No proof authorizes deleting a face at the stale hint');
  assert.equal(f.properties.get(f.pilotApi.DOOR_STATE_KEY), saved);
  assert.equal(f.properties.get('fc_guild_door'), JSON.stringify(stale), 'The historical hint is preserved without reanchoring');
  assert.equal(f.placements.length, 0);
});

test('periodic maintenance uses the durable source when the old hint is absent, broken, throwing or distant', async () => {
  for (const hint of ['missing', 'broken', 'throwing', 'distant']) {
    const f = await fixture(); f.readyRoom(); f.player(); f.entities[0].removed = true;
    const saved = f.properties.get(f.pilotApi.DOOR_STATE_KEY);
    if (hint === 'missing') f.properties.delete('fc_guild_door');
    if (hint === 'broken') f.properties.set('fc_guild_door', '{broken');
    if (hint === 'distant') f.properties.set('fc_guild_door', JSON.stringify({ ...f.source, x: 1000 }));
    if (hint === 'throwing') {
      const native = f.world.getDynamicProperty;
      f.world.getDynamicProperty = key => { if (key === 'fc_guild_door') throw new Error('unreadable legacy hint'); return native(key); };
    }
    for (const tick of [40, 80, 120]) { f.system.currentTick = tick; f.portalTick(); }
    const active = f.entities.filter(e => !e.removed);
    assert.equal(active.length, 1, hint);
    assert.equal(active[0].props.get('fc_door_identity'), 'guild', hint);
    assert.equal(active[0].location.x, f.source.x, hint);
    assert.equal(f.properties.get(f.pilotApi.DOOR_STATE_KEY), saved);
  }
});

test('the all-door sweep cannot recreate a Guild hint as an ordinary door or copy it across dimensions', async () => {
  const f = await fixture(); f.readyRoom(); f.entities[0].removed = true;
  const stale = { ...f.source, x: 400 }, p = f.player();
  f.properties.set('fc_guild_door', JSON.stringify(stale));
  f.properties.set('fc_doors', JSON.stringify([{ ...stale, f: 186 }, { x: 700, y: 65, z: 200, f: 186 }]));
  p.location = { ...stale }; f.runtime.ensureAllDemonDoors(f.dimension);
  assert.equal(f.entities.filter(e => !e.removed && e.location.x === stale.x).length, 0);
  p.location = { ...f.source }; f.runtime.ensureAllDemonDoors(f.dimension);
  assert.equal(f.entities.filter(e => !e.removed && e.props.get('fc_door_identity') === 'guild').length, 1);
  p.dimension = f.nether; f.runtime.ensureAllDemonDoors(f.nether);
  assert.equal(f.entities.filter(e => !e.removed && e.dimension.id === f.nether.id).length, 0);
  p.dimension = f.dimension; p.location.x = 700; f.runtime.ensureAllDemonDoors(f.dimension);
  assert.equal(f.entities.filter(e => !e.removed && e.location.x === 700).length, 1, 'Unrelated scatter still repairs');
});

test('a stale Guild hint is quarantined from ordinary challenge and reward interactions', async () => {
  const f = await fixture(); f.readyRoom();
  const stale = { ...f.source, x: 400 }, p = f.player(), door = f.face({ location: stale, index: 4 });
  f.properties.set('fc_guild_door', JSON.stringify(stale)); p.location = { ...stale };
  const saved = f.properties.get(f.pilotApi.DOOR_STATE_KEY);
  f.runtime.demonDoorTalk(p, door, 'minecraft:lantern');
  assert.equal(f.forms.length, 0); assert.equal(f.payouts.length, 0);
  assert.ok(p.messages.some(message => message.includes('preserved')));
  assert.equal(door.removed, undefined); assert.equal(f.properties.get(f.pilotApi.DOOR_STATE_KEY), saved);
});

test('a durable source dimension overrides both a conflicting hint and a supplied founding anchor', async () => {
  const f = await fixture(), p = f.player(); f.readyRoom(); f.entities[0].removed = true;
  const record = plain(f.runtime.guildDoorPilot.getState());
  record.source.dimension = f.nether.id;
  f.properties.set(f.pilotApi.DOOR_STATE_KEY, JSON.stringify(record));
  const saved = f.properties.get(f.pilotApi.DOOR_STATE_KEY);
  f.runtime.ensureGuildDoorPilot(f.dimension, f.source, true);
  f.runtime.ensureAllDemonDoors(f.dimension);
  assert.equal(f.entities.filter(e => !e.removed).length, 0);
  p.dimension = f.nether;
  f.nether.failScan = true;
  f.system.currentTick = 40; f.portalTick();
  assert.equal(f.entities.filter(e => !e.removed).length, 0, 'Failed scan cannot fall back across dimensions');
  f.nether.failScan = false;
  for (const tick of [80, 120]) { f.system.currentTick = tick; f.portalTick(); }
  const active = f.entities.filter(e => !e.removed);
  assert.equal(active.length, 1); assert.equal(active[0].dimension.id, f.nether.id);
  assert.equal(active[0].props.get('fc_door_identity'), 'guild');
  assert.equal(f.properties.get(f.pilotApi.DOOR_STATE_KEY), saved);
});

test('invalid or unreadable primary progress permits no fallback registration, spawning or cleanup', async () => {
  for (const failure of ['corrupt', 'throwing', 'invalid-source']) {
    const f = await fixture(); f.readyRoom(); f.player();
    const stale = { ...f.source, x: 400 };
    f.properties.set('fc_guild_door', JSON.stringify(stale));
    if (failure === 'corrupt') f.properties.set(f.pilotApi.DOOR_STATE_KEY, '{broken');
    if (failure === 'invalid-source') {
      const r = plain(f.runtime.guildDoorPilot.getState()); r.source.x = '100';
      f.properties.set(f.pilotApi.DOOR_STATE_KEY, JSON.stringify(r));
    }
    if (failure === 'throwing') {
      const native = f.world.getDynamicProperty;
      f.world.getDynamicProperty = key => { if (key === f.pilotApi.DOOR_STATE_KEY) throw new Error('unreadable primary'); return native(key); };
    }
    const saved = f.properties.get(f.pilotApi.DOOR_STATE_KEY), before = f.operations.length;
    f.runtime.ensureGuildDoorPilot(f.dimension, stale, true);
    f.runtime.ensureAllDemonDoors(f.dimension);
    f.system.currentTick = 40; f.portalTick();
    assert.equal(f.operations.slice(before).filter(op => ['spawn', 'remove', 'property'].includes(op.kind)).length, 0, failure);
    assert.equal(f.properties.get(f.pilotApi.DOOR_STATE_KEY), saved);
  }
});

test('production block protection permits native non-sneaking containers and both return landmarks', async () => {
  const f = await fixture(), p = f.player(), o = f.readyRoom(); p.location = add(o, f.pilotApi.ARCANUM.arrival);
  const inside = { location: add(o, { x: 16, y: 3, z: 28 }), typeId: 'minecraft:barrel' };
  const breakEvent = { dimension: f.dimension, player: p, block: inside, cancel: false }; f.breakBlock(breakEvent); assert.equal(breakEvent.cancel, true);
  const outside = { dimension: f.dimension, player: p, block: { location: { x: 0, y: 64, z: 0 }, typeId: 'minecraft:stone' }, cancel: false };
  f.breakBlock(outside); assert.equal(outside.cancel, false);
  const use = { player: p, block: inside, cancel: false }; f.useBlock(use); assert.equal(use.cancel, false);
  p.isSneaking = true; f.useBlock(use); assert.equal(use.cancel, true); p.isSneaking = false;
  const wall = { player: p, block: { location: add(o, { x: 0, y: 5, z: 3 }), typeId: 'minecraft:barrier' }, cancel: false };
  f.useBlock(wall); assert.equal(wall.cancel, true);
  for (const y of [2, 7]) {
    p.location = add(o, f.pilotApi.ARCANUM.exit);
    const exit = { player: p, block: { location: add(o, { x: 24, y, z: 3 }), typeId: y === 2 ? 'minecraft:stone_bricks' : 'minecraft:sea_lantern' }, cancel: false };
    const before = p.moves.length; f.useBlock(exit); assert.equal(exit.cancel, true); assert.equal(p.moves.length, before);
    f.flush(); assert.equal(p.moves.length, before + 1); assert.equal(p.location.x, f.source.x + 0.5);
  }
});

test('production explosion and dangerous-item protection preserves unrelated world behavior', async () => {
  const f = await fixture(), p = f.player(), o = f.readyRoom(); p.location = add(o, f.pilotApi.ARCANUM.arrival);
  const protectedBlock = { location: add(o, { x: 1, y: 1, z: 1 }) }, outsideBlock = { location: { x: 0, y: 64, z: 0 } };
  let remaining;
  f.explosion({ dimension: f.dimension, getImpactedBlocks: () => [protectedBlock, outsideBlock], setImpactedBlocks: (value) => { remaining = value; } });
  assert.deepEqual(remaining, [outsideBlock]);
  for (const id of ['minecraft:ender_pearl', 'minecraft:chorus_fruit', 'minecraft:lava_bucket', 'minecraft:flint_and_steel', 'minecraft:zombie_spawn_egg']) {
    const ev = { source: p, itemStack: { typeId: id }, cancel: false }; f.itemUse(ev); assert.equal(ev.cancel, true, id);
  }
  const potion = { source: p, itemStack: { typeId: 'fc:health_potion' }, cancel: false }; f.itemUse(potion); assert.equal(potion.cancel, false);
  p.location = { ...f.source }; const ordinary = { source: p, itemStack: { typeId: 'minecraft:ender_pearl' }, cancel: false }; f.itemUse(ordinary); assert.equal(ordinary.cancel, false);
});

test('production scatter and region retirement exclude realm storage including ground below it', async () => {
  const f = await fixture(), p = f.player(), o = f.readyRoom();
  const productionMaybePlace = f.runtime.maybePlace;
  const region = f.runtime.REGION;
  p.location = { x: o.x + 20, y: 64, z: o.z + 20 };
  assert.equal(f.runtime.guildDoorWorldExcluded(p), true);
  productionMaybePlace(p, Math.floor(p.location.x / region), Math.floor(p.location.z / region));
  assert.equal([...f.properties.keys()].some((key) => key.startsWith('fc_rgn_')), false);
  const calls = []; f.context.maybePlace = (...args) => calls.push(args);
  f.scatter(); assert.equal(calls.length, 0);
  p.location = { x: 20, y: 64, z: 20 }; f.scatter(); assert.equal(calls.length, 9);
  p.dimension = f.nether; f.scatter(); assert.equal(calls.length, 9);
});

test('actual recovery command requires a player source and returns the active room visitor', async () => {
  const f = await fixture(), p = f.player(), o = f.readyRoom();
  f.scriptEvent({ id: 'fc:door_return', sourceEntity: undefined });
  f.scriptEvent({ id: 'fc:door_return', sourceEntity: f.face() }); assert.equal(p.moves.length, 0);
  p.location = add(o, f.pilotApi.ARCANUM.arrival); f.scriptEvent({ id: 'fc:door_return', sourceEntity: p });
  assert.equal(p.moves.length, 1); assert.equal(p.location.x, f.source.x + 0.5); assert.equal(p.location.z, f.source.z - 3.5);
  assert.equal(f.runtime.guildDoorPilot.getReturnTicket(p), null);
});

test('actual recovery command uses an existing ticket when the main room record is corrupt', async () => {
  const f = await fixture(), p = f.player(), o = f.readyRoom();
  p.location = add(o, f.pilotApi.ARCANUM.arrival);
  f.system.currentTick = 45; f.portalTick();
  assert.ok(p.props.get(f.pilotApi.DOOR_RETURN_KEY));
  f.properties.set(f.pilotApi.DOOR_STATE_KEY, '{corrupt');
  f.scriptEvent({ id: 'fc:door_return', sourceEntity: p });
  assert.equal(p.moves.length, 1); assert.equal(p.location.x, f.source.x + 0.5);
  assert.equal(f.properties.get(f.pilotApi.DOOR_STATE_KEY), '{corrupt');
  assert.equal(p.props.has(f.pilotApi.DOOR_RETURN_KEY), false);
});

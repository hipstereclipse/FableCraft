import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import vm from 'node:vm';

const code = await readFile(new URL('../../packs/Fablecraft_BP/scripts/fc_demon_doors.js', import.meta.url), 'utf8');
const module = new vm.SourceTextModule(code, { context: vm.createContext({}) });
await module.link(() => { throw new Error('The pilot should have injected dependencies.'); });
await module.evaluate();
const { createDemonDoorPilot, DOOR_STATE_KEY, DOOR_RETURN_KEY, ARCANUM, realmOrigin } = module.namespace;
const plain = (x) => JSON.parse(JSON.stringify(x));
const key = (p) => `${Math.floor(p.x)},${Math.floor(p.y)},${Math.floor(p.z)}`;
const add = (a, b) => ({ x: a.x + b.x, y: a.y + b.y, z: a.z + b.z });
// Exercise the actual owned room builder. CaptureVox disables artifact writes;
// this is a geometry fixture, not a second implementation of the reward room.
if (!process.argv[2]) throw new Error('Run through python scripts/tests/test_demon_doors.py to supply actual generated geometry.');
const geometry = JSON.parse(await readFile(process.argv[2], 'utf8'));
assert.deepEqual(geometry.size, [49, 28, 49]);

function fixture({ sourceDimension = 'minecraft:overworld', bulk = 'native' } = {}) {
  const properties = new Map(), blocks = new Map(), commands = [], commandDimensions = [], errors = [], places = [], players = [];
  const seeds = [], writes = [], probes = [], effects = [];
  const source = { x: 10, y: 1, z: 10, dimension: sourceDimension };
  const system = { currentTick: 0 };
  const flags = { loaded: true, lease: true, structure: true, entities: [], teleport: 'ok', seedFail: false, sourceReady: true, damage: null };
  class ItemStack {
    constructor(typeId, amount) { this.typeId = typeId; this.amount = amount; }
    setLore(lore) { this.lore = [...lore]; }
    getLore() { return [...(this.lore ?? [])]; }
  }
  const copyItem = (item) => {
    if (!item) return undefined;
    const copy = new ItemStack(item.typeId, item.amount);
    copy.nameTag = item.nameTag; copy.setLore(item.getLore?.() ?? item.lore ?? []);
    return copy;
  };
  function chest() {
    const slots = new Map();
    const c = { size: 27, slots, getItem: (slot) => copyItem(slots.get(slot)), setItem(slot, value) {
      const effect = { container: c, slot, value: copyItem(value) };
      seeds.push(effect); effects.push({ kind: 'seed', ...effect });
      const fault = flags.seedFault?.(effect, seeds.length);
      if (flags.seedFail) { flags.seedFail = false; throw new Error('injected inventory failure'); }
      if (fault === 'before') throw new Error('injected inventory failure before write');
      if (fault === 'drop') return;
      value = copyItem(value);
      if (fault === 'type') value.typeId = 'minecraft:diamond';
      if (fault === 'count') value.amount = 2;
      if (fault === 'name') value.nameTag = 'Substituted keepsake';
      if (fault === 'lore') value.setLore(['Substituted lore']);
      if (value) slots.set(slot, value); else slots.delete(slot);
      flags.afterSeed?.(effect, seeds.length);
      if (fault === 'after') throw new Error('injected inventory failure after write');
    } };
    return c;
  }
  function block(typeId = 'minecraft:air', inventory = null) {
    return { typeId, isAir: typeId === 'minecraft:air', getComponent: (name) => name === 'minecraft:inventory' && inventory ? { container: inventory } : undefined };
  }
  const dim = {
    id: 'minecraft:overworld',
    getBlock(p) {
      flags.beforeBlock?.(p);
      if (!flags.loaded && p.x >= 600000) return undefined;
      if (blocks.has(key(p))) return blocks.get(key(p));
      return block(Math.floor(p.y) === 0 ? 'minecraft:cobblestone' : 'minecraft:air');
    },
    getEntities() { return flags.entities; },
    runCommand(command) { commands.push(command); commandDimensions.push({ dimension: this.id, command }); if (!flags.lease && command.startsWith('tickingarea add')) throw new Error('no authority'); return { successCount: 1 }; },
    spawnParticle() {},
  };
  const dimensions = { 'minecraft:overworld': dim, 'minecraft:nether': { ...dim, id: 'minecraft:nether' }, 'minecraft:the_end': { ...dim, id: 'minecraft:the_end' } };
  function placeRoom(_dim, origin) {
    effects.push({ kind: 'place', origin: plain(origin) });
    if (!flags.structure) throw new Error('pack structure missing');
    places.push(plain(origin));
    for (let i = 0; i < geometry.grid.length; i++) {
      const position = { x: Math.floor(i / (28 * 49)), y: Math.floor(i / 49) % 28, z: i % 49 };
      const type = geometry.palette[geometry.grid[i]];
      blocks.set(key(add(origin, position)), block(type, ['minecraft:chest', 'minecraft:barrel'].includes(type) ? chest() : null));
    }
    if (flags.damage) blocks.set(key(add(origin, flags.damage.at)), block(flags.damage.type));
    flags.afterPlace?.(origin);
  }
  const world = {
    getDynamicProperty(name) {
      if (name === DOOR_STATE_KEY && flags.stateReadFail) throw new Error('injected unavailable world record');
      return properties.get(name);
    },
    setDynamicProperty(name, value) {
      const record = name === DOOR_STATE_KEY && value !== undefined ? JSON.parse(value) : null;
      writes.push({ name, value, record }); effects.push({ kind: 'property', name, record });
      const fault = flags.worldWrite?.(record, name);
      if (fault === 'before') throw new Error('injected world write failure before persistence');
      if (fault === 'drop') return;
      if (fault === 'substitute') value = JSON.stringify({ ...record, source: { ...record.source, x: record.source.x + 1 } });
      if (value === undefined) properties.delete(name); else properties.set(name, value);
      if (fault === 'after') throw new Error('injected world write failure after persistence');
    },
    getDimension(id) { const resolved = dimensions[id.includes(':') ? id : `minecraft:${id}`]; assert.ok(resolved, `unsupported dimension ${id}`); return resolved; },
    getPlayers: () => players,
    structureManager: { place(_id, dimension, at) { placeRoom(dimension, at); } },
  };
  function player(id = `p${players.length}`) {
    const props = new Map(), messages = [], moves = [];
    const p = {
      id, dimension: dimensions[sourceDimension], location: { x: 10.5, y: 1, z: 6.5 }, props, messages, moves,
      getDynamicProperty: (name) => props.get(name),
      setDynamicProperty: (name, value) => value === undefined ? props.delete(name) : props.set(name, value),
      sendMessage: (message) => messages.push(message), playSound() {},
      tryTeleport(position, options) {
        moves.push({ position: plain(position), options });
        if (flags.teleport === 'false') return false;
        if (flags.teleport === 'throw') throw new Error('injected teleport failure');
        p.location = plain(position); p.dimension = options.dimension;
        if (flags.teleport === 'throw_after') throw new Error('ambiguous engine failure after movement');
        return true;
      },
    };
    players.push(p);
    return p;
  }
  function face({ open = false, idx = 4 } = {}) {
    const props = new Map([['fc_door_idx', idx], ['fc_door_open', open]]);
    return { typeId: 'fc:demon_door', dimension: dimensions[sourceDimension], location: { ...source }, props,
      getDynamicProperty: (name) => props.get(name), setDynamicProperty: (name, value) => props.set(name, value),
      triggerEvent() {}, teleport(position) { this.location = plain(position); } };
  }
  let pilot;
  const volumeIsBlock = (dimension, origin, size, typeId) => {
    const probe = { dimension: dimension.id, origin: plain(origin), size: plain(size), typeId };
    probes.push(probe); flags.beforeProbe?.(probe);
    if (bulk === 'throw') throw new Error('injected unavailable native volume');
    if (bulk === 'truthy') return 1;
    for (let x = 0; x < size.x; x++) for (let y = 0; y < size.y; y++) for (let z = 0; z < size.z; z++) {
      if (dimension.getBlock(add(origin, { x, y, z }))?.typeId !== typeId) return false;
    }
    return true;
  };
  const reload = () => (pilot = createDemonDoorPilot({ world, system, ItemStack, placeRoom,
    ...(bulk === 'missing' ? {} : { volumeIsBlock, volumeIsEmpty: (d, o, s) => volumeIsBlock(d, o, s, 'minecraft:air') }),
    sourceReady: () => flags.sourceReady, report: (error) => errors.push(error) }));
  const step = (count = 1) => { for (let i = 0; i < count; i++) { system.currentTick += 5; pilot.tick(); } };
  const state = () => plain(pilot.getState());
  const rewardContainer = (index) => dim.getBlock(add(state().room.origin, ARCANUM.rewards[index].at)).getComponent('minecraft:inventory').container;
  const leave = (p) => { p.location = { x: 10.5, y: 1, z: 6.5 }; p.dimension = dimensions[sourceDimension]; step(13); };
  const enter = (p) => { p.location = { x: 10.5, y: 1, z: 10 }; step(32); };
  const build = (p, f, legacy = false) => {
    if (!pilot.getState()) pilot.registerGuild(source, f, { isNew: !legacy });
    pilot.interact(p, f, 'minecraft:lantern');
    step(1); enter(p);
    for (let i = 0; i < 500 && state()?.room?.phase !== 'ready'; i++) step();
    assert.equal(state().room?.phase, 'ready', errors.join('\n'));
    leave(p);
  };
  const start = (p, door) => {
    pilot.registerGuild(source, door, { isNew: true }); pilot.interact(p, door, 'minecraft:lantern');
  };
  const until = (predicate, limit = 500) => {
    for (let i = 0; i < limit && !predicate(); i++) step();
    assert.ok(predicate(), `Expected fixture checkpoint; ${errors.join('\n')}`);
  };
  reload();
  return { source, system, flags, block, blocks, properties, commands, commandDimensions, errors, places, players, dim, world,
    seeds, writes, probes, effects, chest, ItemStack, start, until,
    player, face, step, state, build, enter, leave, reload, rewardContainer, get pilot() { return pilot; } };
}

let count = 0;
async function group(name, fn) { await fn(); count++; console.log(`PASS ${name}`); }

await group('canonical light challenge, no consumption/opening payout, animation aperture', () => {
  const f = fixture(), p = f.player(), door = f.face();
  f.pilot.registerGuild(f.source, door, { isNew: true });
  assert.equal(f.pilot.interact(p, door, 'minecraft:apple'), true);
  assert.equal(f.state().unlocked, false);
  assert.equal(f.places.length, 0);
  const unrelated = f.face(); unrelated.location.x += 100;
  assert.equal(f.pilot.interact(p, unrelated, 'minecraft:lantern'), false);
  f.pilot.interact(p, door, 'minecraft:lantern');
  f.pilot.interact(p, door, 'minecraft:lantern');
  assert.equal(f.state().unlocked, true);
  assert.equal(f.places.length, 0, 'opening does not give room loot');
  assert.equal(p.moves.length, 0, 'opening does not teleport');
  f.step(9);
  assert.equal(door.location.y, f.source.y + 5);
  f.build(p, door);
  assert.equal(f.places.length, 1);
  ARCANUM.rewards.forEach((reward, i) => assert.equal(f.rewardContainer(i).getItem(0).typeId, reward.item));
  assert.equal(f.state().archetype, 'guild_library_arcanum');
});

await group('surviving paid door, missing history and durable face replacement', () => {
  const f = fixture(), p = f.player(), door = f.face({ open: true, idx: 7 });
  f.build(p, door, true);
  assert.equal(f.state().legacy.status, 'surviving_open');
  assert.equal(f.state().legacy.idx, 7);
  assert.equal(f.state().rewards.suppressed, true);
  ARCANUM.rewards.forEach((_, i) => assert.equal(f.rewardContainer(i).getItem(0), undefined));
  const before = f.state(); f.reload();
  const replacement = f.face({ open: false, idx: 1 });
  f.pilot.registerGuild({ ...f.source, x: 300 }, replacement);
  f.pilot.reconcileFace(replacement);
  assert.equal(replacement.props.get('fc_door_open'), true);
  assert.equal(replacement.location.y, f.source.y + 5);
  assert.deepEqual(f.state(), before, 'new coordinates/index cannot redefine the saved room');
  const missing = fixture(); missing.pilot.registerGuild(missing.source);
  assert.equal(missing.state().legacy.status, 'history_unknown');
  assert.equal(missing.state().rewards.suppressed, true);
  assert.match(missing.errors[0], /history is missing/);
  const corrupt = fixture(); corrupt.properties.set(DOOR_STATE_KEY, '{broken');
  assert.equal(corrupt.pilot.registerGuild(corrupt.source, corrupt.face()), null);
  assert.equal(corrupt.properties.get(DOOR_STATE_KEY), '{broken', 'corrupt progress is not overwritten');
});

await group('full-volume allocation preflight rejects occupied cell without clearing', () => {
  const f = fixture(), p = f.player(), door = f.face();
  const obstruction = add(realmOrigin(0), { x: 31, y: 22, z: 45 });
  f.blocks.set(key(obstruction), f.block('minecraft:diamond_block'));
  f.build(p, door);
  assert.equal(f.state().room.cell, 1);
  assert.deepEqual(f.state().room.origin, plain(realmOrigin(1)));
  assert.equal(f.dim.getBlock(obstruction).typeId, 'minecraft:diamond_block');
  assert.equal(f.places.length, 1);
  assert.equal(f.places[0].x, realmOrigin(1).x);
});

await group('loading authority, unloaded chunks and missing structure fail at source', () => {
  for (const failure of ['lease', 'loaded', 'structure']) {
    const f = fixture(), p = f.player(), door = f.face();
    f.flags[failure] = false;
    f.pilot.registerGuild(f.source, door, { isNew: true });
    f.pilot.interact(p, door, 'minecraft:lantern');
    f.step(260);
    assert.equal(f.state().unlocked, true, `${failure}: unlock survives preparation failure`);
    assert.notEqual(f.state().room?.phase, 'ready');
    assert.equal(p.moves.length, 0);
    assert.equal(f.places.length, 0);
    assert.equal(p.props.has(DOOR_RETURN_KEY), false);
    assert.ok(f.errors.length > 0, `${failure}: a useful diagnostic is retained`);
    assert.ok(f.commands.every((command) => !command.includes('remove_all')));
  }
});

await group('partial native seeding stays quarantined across reload without replay or replenishment', () => {
  for (const failure of ['before', 'after']) {
    const f = fixture(), p = f.player(), door = f.face();
    f.flags.seedFault = (_effect, count) => count === 2 ? failure : null;
    f.start(p, door); f.step(260);
    assert.equal(f.state().room.phase, 'placing');
    assert.equal(f.state().room.preparation.phase, 'seeding');
    assert.equal(f.state().rewards.seeded, false);
    assert.deepEqual(f.state().rewards.claimed, [false, false, false, false]);
    assert.equal(f.rewardContainer(0).getItem(0).typeId, 'fc:elixir_of_life');
    assert.equal(f.seeds.length, 2);
    const foreign = add(f.state().room.origin, { x: 11, y: 11, z: 11 });
    f.blocks.set(key(foreign), f.block('minecraft:diamond_block'));
    f.flags.seedFault = null; f.reload(); f.leave(p); f.enter(p); f.step(260);
    assert.equal(f.places.length, 1);
    assert.equal(f.seeds.length, 2);
    assert.equal(f.dim.getBlock(foreign).typeId, 'minecraft:diamond_block');
    assert.equal(p.moves.length, 0);
    assert.equal(p.props.has(DOOR_RETURN_KEY), false);
  }
});

await group('native chest discovery persists depletion across revisits and reload', () => {
  const f = fixture(), p = f.player(), door = f.face(); f.build(p, door); f.enter(p);
  assert.equal(f.pilot.occupiedRealm(p), true);
  const c = f.rewardContainer(0);
  const acquired = c.getItem(0); c.setItem(0, undefined); // Native chest transfer, not a script grant.
  assert.equal(acquired.typeId, 'fc:elixir_of_life');
  f.step(); assert.equal(f.state().rewards.claimed[0], true);
  assert.equal(f.pilot.requestReturn(p), true);
  f.reload(); f.leave(p); f.enter(p);
  assert.equal(f.pilot.occupiedRealm(p), true);
  assert.equal(f.rewardContainer(0).getItem(0), undefined);
  assert.equal(f.places.length, 1);
  assert.equal(f.rewardContainer(1).getItem(0).nameTag, 'Making Friends');
  // A destroyed visited room must not become a fresh loot allocation.
  f.pilot.requestReturn(p);
  f.blocks.set(key(add(f.state().room.origin, ARCANUM.arrival)), f.block('minecraft:stone'));
  f.leave(p); f.enter(p); f.step(2);
  assert.equal(f.pilot.occupiedRealm(p), false);
  assert.equal(f.places.length, 1);
  assert.match(f.errors.join('\n'), /refusing to rebuild/);
});

await group('concurrent visitors keep independent exact-source tickets and return safely', () => {
  const f = fixture(), a = f.player('a'), b = f.player('b'), door = f.face();
  f.build(a, door);
  a.location = { x: 10.4, y: 1, z: 6.2 }; b.location = { x: 9.7, y: 1, z: 7.1 }; f.step(14);
  const sourceA = { ...a.location }, sourceB = { ...b.location };
  a.location = { x: 10.4, y: 1, z: 10 }; b.location = { x: 9.7, y: 1, z: 10 }; f.step(6);
  assert.equal(f.pilot.occupiedRealm(a), true); assert.equal(f.pilot.occupiedRealm(b), true);
  assert.deepEqual(plain(f.pilot.getReturnTicket(a).source), { ...sourceA, dimension: f.dim.id });
  assert.deepEqual(plain(f.pilot.getReturnTicket(b).source), { ...sourceB, dimension: f.dim.id });
  assert.equal(f.places.length, 1);
  f.flags.teleport = 'false'; assert.equal(f.pilot.requestReturn(a), false);
  assert.equal(f.pilot.getReturnTicket(a).phase, 'inside');
  f.flags.teleport = 'throw'; assert.equal(f.pilot.requestReturn(a), false);
  assert.equal(f.pilot.occupiedRealm(a), true);
  f.flags.teleport = 'ok'; assert.equal(f.pilot.requestReturn(b), true); assert.deepEqual(b.location, sourceB);
  f.flags.teleport = 'throw_after'; assert.equal(f.pilot.requestReturn(a), true); assert.deepEqual(a.location, sourceA);
  assert.equal(f.pilot.getReturnTicket(a), null); assert.equal(f.pilot.getReturnTicket(b), null);
});

await group('failed entry, blocked source, reload/death recovery and no portal bounce', () => {
  const f = fixture(), p = f.player(), door = f.face(); f.build(p, door);
  f.flags.teleport = 'false'; f.enter(p);
  assert.equal(f.pilot.occupiedRealm(p), false); assert.equal(f.pilot.getReturnTicket(p), null);
  assert.equal(f.state().room.visited, true);
  f.flags.teleport = 'ok'; f.leave(p); f.enter(p);
  const ticket = plain(f.pilot.getReturnTicket(p));
  f.reload(); f.step();
  assert.deepEqual(plain(f.pilot.getReturnTicket(p)), ticket);
  for (let x = 7; x <= 14; x++) for (let z = 5; z <= 8; z++) f.blocks.set(`${x},1,${z}`, f.block('minecraft:stone'));
  assert.equal(f.pilot.requestReturn(p), false);
  assert.equal(f.pilot.occupiedRealm(p), true);
  assert.ok(f.pilot.getReturnTicket(p));
  for (let x = 7; x <= 14; x++) for (let z = 5; z <= 8; z++) f.blocks.delete(`${x},1,${z}`);
  assert.equal(f.pilot.requestReturn(p), true);
  const moves = p.moves.length;
  p.location = { x: 10.5, y: 1, z: 10 }; f.step(20);
  assert.equal(p.moves.length, moves, 'remaining in the doorway never rearms a bounce');
  f.leave(p); f.enter(p);
  assert.equal(f.pilot.occupiedRealm(p), true);
  p.location = { x: 90, y: 1, z: 90 }; f.step(); // A respawn/home or external teleport.
  assert.equal(f.pilot.getReturnTicket(p).phase, 'outside');
  assert.equal(p.location.x, 90, 'death does not force the player back into the reward room');
  p.location = add(f.state().room.origin, ARCANUM.arrival); p.props.delete(DOOR_RETURN_KEY); f.reload(); f.step();
  assert.equal(f.pilot.getReturnTicket(p).phase, 'inside', 'orphan position recovers a durable source');
  f.blocks.set(key(add(f.state().room.origin, ARCANUM.rewards[0].at)), f.block('minecraft:air'));
  assert.equal(f.pilot.requestReturn(p), true);
});

await group('realm protection and ordinary-world exclusions are dimension/location bounded', () => {
  const f = fixture(), p = f.player(), door = f.face(); f.build(p, door);
  const o = f.state().room.origin;
  assert.equal(f.pilot.protectsBlock(f.dim.id, add(o, { x: 20, y: 2, z: 20 })), true);
  assert.equal(f.pilot.protectsBlock('minecraft:nether', add(o, { x: 20, y: 2, z: 20 })), false);
  assert.equal(f.pilot.protectsBlock(f.dim.id, { x: 30, y: 1, z: 30 }), false);
  assert.equal(f.pilot.excludesWorldPosition(f.dim.id, add(o, { x: 60, y: 3, z: 60 })), true);
  assert.equal(f.pilot.excludesWorldPosition(f.dim.id, { x: o.x + 20, y: 64, z: o.z + 20 }), true, 'surface scatter beneath storage is excluded too');
  assert.equal(f.pilot.excludesWorldPosition(f.dim.id, { x: 30, y: 1, z: 30 }), false);
});

await group('source readiness gates unlock and entry; corrupt tickets recover from the room record', () => {
  const f = fixture(), p = f.player(), door = f.face();
  f.flags.sourceReady = false;
  f.pilot.registerGuild(f.source, door, { isNew: true });
  f.pilot.interact(p, door, 'minecraft:lantern');
  assert.equal(f.state().unlocked, false);
  assert.equal(f.state().room, null);
  f.flags.sourceReady = true; f.build(p, door);
  f.flags.sourceReady = false; f.enter(p);
  assert.equal(f.pilot.occupiedRealm(p), false);
  f.flags.sourceReady = true; f.leave(p); f.enter(p);
  assert.equal(f.pilot.occupiedRealm(p), true);
  const good = plain(f.pilot.getReturnTicket(p));
  for (const mutation of [
    { ...good, cell: -1 }, { ...good, cell: 4096 }, { ...good, phase: 'nonsense' },
    { ...good, source: { ...good.source, dimension: 'mod:missing_dimension' } },
    { ...good, source: { ...good.source, x: 99999999 } },
  ]) {
    p.props.set(DOOR_RETURN_KEY, JSON.stringify(mutation));
    assert.equal(f.pilot.getReturnTicket(p), null);
    f.step();
    assert.equal(f.pilot.getReturnTicket(p).phase, 'inside');
    assert.equal(f.pilot.getReturnTicket(p).source.dimension, f.source.dimension);
  }
  assert.equal(f.pilot.requestReturn(p), true);
});

await group('return loading leases are removed in the saved source dimension', () => {
  const f = fixture({ sourceDimension: 'minecraft:nether' }), p = f.player(), door = f.face();
  f.build(p, door); f.enter(p);
  assert.equal(f.pilot.occupiedRealm(p), true);
  assert.equal(f.pilot.getReturnTicket(p).source.dimension, 'minecraft:nether');
  for (let x = 7; x <= 14; x++) for (let z = 5; z <= 8; z++) f.blocks.set(`${x},1,${z}`, f.block('minecraft:stone'));
  assert.equal(f.pilot.requestReturn(p), false);
  const added = f.commandDimensions.find((entry) => entry.command.startsWith('tickingarea add') && entry.command.includes('fc_dp_guild_return'));
  assert.equal(added.dimension, 'minecraft:nether');
  for (let x = 7; x <= 14; x++) for (let z = 5; z <= 8; z++) f.blocks.delete(`${x},1,${z}`);
  assert.equal(f.pilot.requestReturn(p), true);
  assert.equal(p.dimension.id, 'minecraft:nether');
  const removed = f.commandDimensions.filter((entry) => entry.command === 'tickingarea remove fc_dp_guild_return').at(-1);
  assert.equal(removed.dimension, 'minecraft:nether');
});

await group('independent shell, minor lid, approach and branch defects prevent admission/seeding', () => {
  for (const damage of [
    { at: { x: 0, y: 9, z: 17 }, type: 'minecraft:air', diagnosis: /containment/ },
    { at: { x: 16, y: 4, z: 28 }, type: 'minecraft:stone', diagnosis: /timed out/ },
    { at: { x: 16, y: 3, z: 33 }, type: 'minecraft:stone', diagnosis: /timed out/ },
    { at: { x: 20, y: 3, z: 26 }, type: 'minecraft:stone', diagnosis: /timed out/ },
  ]) {
    const f = fixture(), p = f.player(), door = f.face();
    f.flags.damage = damage;
    f.pilot.registerGuild(f.source, door, { isNew: true });
    f.pilot.interact(p, door, 'minecraft:lantern');
    f.step(260);
    assert.equal(f.state().room.phase, 'placing');
    assert.equal(f.state().rewards.seeded, false);
    assert.equal(p.moves.length, 0);
    assert.match(f.errors.join('\n'), damage.diagnosis);
    ARCANUM.rewards.forEach((_, i) => assert.equal(f.rewardContainer(i).getItem(0), undefined));
  }
});

await group('committed return ticket survives missing/corrupt world state; invalid or misplaced tickets cannot travel', () => {
  for (const primary of ['{broken', undefined]) {
    const f = fixture(), p = f.player(), door = f.face(); f.build(p, door); f.enter(p);
    const savedTicket = JSON.parse(p.props.get(DOOR_RETURN_KEY));
    const expected = { x: savedTicket.source.x, y: savedTicket.source.y, z: savedTicket.source.z };
    if (primary === undefined) f.properties.delete(DOOR_STATE_KEY); else f.properties.set(DOOR_STATE_KEY, primary);
    const places = f.places.length;
    f.flags.teleport = 'false'; assert.equal(f.pilot.requestReturn(p), false);
    assert.ok(p.props.get(DOOR_RETURN_KEY), 'a failed emergency return keeps the ticket');
    f.flags.teleport = 'ok'; assert.equal(f.pilot.requestReturn(p), true);
    assert.deepEqual(p.location, expected);
    assert.equal(p.props.has(DOOR_RETURN_KEY), false);
    assert.equal(f.properties.get(DOOR_STATE_KEY), primary, 'emergency return never resets world progress');
    assert.equal(f.places.length, places);
  }
  const f = fixture(), p = f.player(), door = f.face(); f.build(p, door); f.enter(p);
  const original = JSON.parse(p.props.get(DOOR_RETURN_KEY));
  f.properties.set(DOOR_STATE_KEY, '{broken');
  for (const invalid of [
    { ...original, cell: -1 }, { ...original, cell: 4096 }, { ...original, cell: 1 },
    { ...original, phase: 'invalid' }, { ...original, source: { ...original.source, dimension: 'missing:dimension' } },
    { ...original, source: { ...original.source, x: 40000000 } },
  ]) {
    p.props.set(DOOR_RETURN_KEY, JSON.stringify(invalid));
    const moves = p.moves.length; assert.equal(f.pilot.requestReturn(p), false); assert.equal(p.moves.length, moves);
  }
  p.props.set(DOOR_RETURN_KEY, JSON.stringify(original));
  p.location = { x: 10.5, y: 1, z: 6.5 };
  assert.equal(f.pilot.requestReturn(p), false, 'valid ticket cannot teleport a player outside its exact cell');
});

await group('placement and every native seed follow exact persisted preparation receipts', () => {
  const f = fixture(), p = f.player(), door = f.face(); f.build(p, door);
  assert.equal(f.state().schema, 1);
  assert.deepEqual(f.state().room.preparation, { schema: 1, phase: 'seeded' });
  const phases = f.writes.map(w => w.record?.room?.preparation?.phase).filter(Boolean);
  assert.deepEqual([...new Set(phases)], ['placing', 'placed', 'seeding', 'seeded']);
  const placement = f.effects.findIndex(e => e.kind === 'place');
  assert.equal(f.effects[placement - 1].record.room.preparation.phase, 'placing');
  const firstSeed = f.effects.findIndex(e => e.kind === 'seed');
  assert.equal(f.effects[firstSeed - 1].record.room.preparation.phase, 'seeding');
  assert.equal(f.seeds.length, 4);
  ARCANUM.rewards.forEach((reward, i) => {
    const c = f.rewardContainer(i), item = c.getItem(0);
    assert.equal(item.typeId, reward.item); assert.equal(item.amount, 1);
    assert.equal(item.nameTag, reward.name);
    assert.deepEqual(item.getLore(), reward.name ? ['A keepsake from the Library Arcanum.'] : []);
    for (let slot = 1; slot < c.size; slot++) assert.equal(c.getItem(slot), undefined);
  });
});

await group('unavailable or nonboolean native bulk authority cannot place a room', () => {
  for (const bulk of ['missing', 'throw', 'truthy']) {
    const f = fixture({ bulk }), p = f.player(), door = f.face(); f.start(p, door); f.step(260);
    assert.equal(f.places.length, 0, bulk); assert.equal(f.seeds.length, 0, bulk);
    assert.equal(p.moves.length, 0, bulk); assert.notEqual(f.state().room?.phase, 'ready', bulk);
  }
});

await group('late changes behind the completed air scan survive the final native volume check', () => {
  const f = fixture(), p = f.player(), door = f.face(), target = add(realmOrigin(0), { x: 1, y: 1, z: 1 });
  f.start(p, door); f.step(10); // The first x/y slice has already been read.
  f.blocks.set(key(target), f.block('minecraft:diamond_block')); f.step(260);
  assert.equal(f.dim.getBlock(target).typeId, 'minecraft:diamond_block');
  assert.equal(f.places.length, 0); assert.equal(f.seeds.length, 0); assert.equal(p.moves.length, 0);
  assert.ok(f.probes.some(probe => probe.typeId === 'minecraft:air'));
});

await group('unknown legacy placing and intent-only placement history never authorize reconstruction', () => {
  for (const preparation of [undefined, { schema: 1, phase: 'placing' }, { schema: 1, phase: 'seeding' }]) {
    const f = fixture(), p = f.player(), door = f.face(); f.pilot.registerGuild(f.source, door, { isNew: true });
    const state = f.state(); state.unlocked = true;
    state.room = { cell: 0, origin: plain(realmOrigin(0)), version: 1, phase: 'placing', visited: false };
    if (preparation) state.room.preparation = preparation;
    const raw = JSON.stringify(state); f.properties.set(DOOR_STATE_KEY, raw);
    f.reload(); f.leave(p); f.enter(p); f.step(260);
    assert.equal(f.properties.get(DOOR_STATE_KEY), raw);
    assert.equal(f.places.length, 0); assert.equal(f.seeds.length, 0); assert.equal(p.moves.length, 0);
  }
});

await group('a placement call that throws after emitting blocks cannot replay across reload', () => {
  const f = fixture(), p = f.player(), door = f.face();
  f.flags.afterPlace = () => { throw new Error('injected placement failure after world mutation'); };
  f.start(p, door); f.step(260);
  assert.equal(f.state().room.preparation.phase, 'placing'); assert.equal(f.places.length, 1);
  const target = add(f.state().room.origin, { x: 11, y: 11, z: 11 });
  f.blocks.set(key(target), f.block('minecraft:diamond_block'));
  f.flags.afterPlace = null; f.reload(); f.leave(p); f.enter(p); f.step(260);
  assert.equal(f.places.length, 1); assert.equal(f.seeds.length, 0); assert.equal(p.moves.length, 0);
  assert.equal(f.dim.getBlock(target).typeId, 'minecraft:diamond_block');
});

await group('all reward slots must be empty before even the first native reward write', () => {
  for (const suppressed of [false, true]) {
    const f = fixture(), p = f.player(), door = f.face({ open: suppressed });
    f.flags.afterPlace = origin => {
      const c = f.dim.getBlock(add(origin, ARCANUM.rewards[3].at)).getComponent('minecraft:inventory').container;
      c.slots.set(26, new f.ItemStack('minecraft:diamond', 3));
    };
    f.pilot.registerGuild(f.source, door, { isNew: !suppressed });
    f.pilot.interact(p, door, 'minecraft:lantern'); f.leave(p); f.enter(p); f.step(260);
    assert.equal(f.places.length, 1); assert.equal(f.seeds.length, 0); assert.equal(p.moves.length, 0);
    assert.equal(f.rewardContainer(3).getItem(26).amount, 3);
    assert.notEqual(f.state().room.phase, 'ready');
  }
});

await group('silent item type, count, name, lore and write losses never become ready', () => {
  for (const failure of ['drop', 'type', 'count', 'name', 'lore']) {
    const f = fixture(), p = f.player(), door = f.face();
    f.flags.seedFault = (_effect, count) => count === 2 ? failure : null;
    f.start(p, door); f.step(260);
    assert.equal(f.state().room.preparation.phase, 'seeding', failure);
    assert.equal(f.state().rewards.seeded, false, failure);
    assert.deepEqual(f.state().rewards.claimed, [false, false, false, false], failure);
    const attempts = f.seeds.length;
    f.flags.seedFault = null; f.reload(); f.leave(p); f.enter(p); f.step(260);
    assert.equal(f.seeds.length, attempts, failure); assert.equal(f.places.length, 1, failure);
    assert.equal(p.moves.length, 0, failure);
  }
});

await group('fresh post-seed inventories reject extra slots and replaced native container handles', () => {
  for (const failure of ['extra', 'replaced', 'unavailable']) {
    const f = fixture(), p = f.player(), door = f.face();
    f.flags.afterSeed = (_effect, count) => {
      if (count !== 4) return;
      if (failure === 'extra') f.rewardContainer(0).slots.set(26, new f.ItemStack('minecraft:diamond', 1));
      else {
        const at = add(f.state().room.origin, ARCANUM.rewards[0].at);
        const replacement = failure === 'replaced' ? f.chest() : null;
        f.blocks.set(key(at), f.block('minecraft:chest', replacement));
      }
    };
    f.start(p, door); f.step(260);
    assert.equal(f.state().room.preparation.phase, 'seeding', failure);
    assert.equal(f.state().rewards.seeded, false, failure); assert.equal(p.moves.length, 0, failure);
    f.flags.afterSeed = null; f.reload(); f.leave(p); f.enter(p); f.step(260);
    assert.equal(f.seeds.length, 4, failure); assert.equal(f.places.length, 1, failure);
  }
});

await group('a native seed callback cannot replace authority or fill the next reward before another write', () => {
  for (const failure of ['history', 'inventory']) {
    const f = fixture(), p = f.player(), door = f.face(); let changed;
    f.flags.afterSeed = (_effect, count) => {
      if (count !== 1) return;
      if (failure === 'history') {
        const record = f.state(); record.room.phase = 'ready'; record.room.visited = true;
        record.room.preparation.phase = 'seeded'; record.rewards.seeded = true;
        record.rewards.claimed = [true, true, true, true];
        changed = JSON.stringify(record); f.properties.set(DOOR_STATE_KEY, changed);
      } else f.rewardContainer(1).slots.set(0, new f.ItemStack('minecraft:diamond', 64));
    };
    f.start(p, door); f.step(260);
    assert.equal(f.seeds.length, 1, failure); assert.equal(f.places.length, 1, failure);
    assert.equal(p.moves.length, 0, failure);
    if (failure === 'history') assert.equal(f.properties.get(DOOR_STATE_KEY), changed);
    else {
      assert.equal(f.rewardContainer(1).getItem(0).typeId, 'minecraft:diamond');
      assert.equal(f.rewardContainer(1).getItem(0).amount, 64);
      assert.equal(f.state().room.preparation.phase, 'seeding');
    }
  }
});

await group('lost, thrown or substituted preparation commits never permit the dependent effect', () => {
  for (const phase of ['placing', 'placed', 'seeding', 'seeded', 'ready']) {
    for (const fault of ['before', 'drop', 'substitute']) {
      const f = fixture(), p = f.player(), door = f.face();
      f.flags.worldWrite = record => (phase === 'ready' ? record?.room?.phase === phase
        : record?.room?.preparation?.phase === phase) ? fault : null;
      f.start(p, door); f.step(260);
      assert.equal(p.moves.length, 0, `${phase}/${fault}`);
      if (phase === 'ready' && fault === 'substitute') {
        assert.equal(f.state().source.x, f.source.x + 1, 'failed read-back leaves the actual substituted native value untouched');
        assert.ok(f.errors.length > 0);
      } else assert.notEqual(f.state()?.room?.phase, 'ready', `${phase}/${fault}`);
      assert.equal(f.places.length, phase === 'placing' ? 0 : 1, `${phase}/${fault}`);
      assert.equal(f.seeds.length, ['seeded', 'ready'].includes(phase) ? 4 : 0, `${phase}/${fault}`);
    }
  }
});

await group('placed receipt retries verification and initial seeding without replaying placement', () => {
  const f = fixture(), p = f.player(), door = f.face(); let original;
  f.flags.afterPlace = origin => {
    const at = add(origin, ARCANUM.arrival); original = f.dim.getBlock(at);
    f.blocks.set(key(at), f.block('minecraft:stone'));
  };
  f.start(p, door); f.step(260);
  assert.equal(f.state().room.preparation.phase, 'placed'); assert.equal(f.seeds.length, 0);
  f.blocks.set(key(add(f.state().room.origin, ARCANUM.arrival)), original);
  f.flags.afterPlace = null; f.reload(); f.build(p, door);
  assert.equal(f.places.length, 1); assert.equal(f.seeds.length, 4);
  assert.equal(f.state().room.phase, 'ready');
});

await group('seeded receipts retry only readiness after fresh inventory and room verification', () => {
  for (const damage of ['none', 'inventory', 'shell', 'route']) {
    const f = fixture(), p = f.player(), door = f.face();
    f.flags.worldWrite = record => record?.room?.phase === 'ready' ? 'drop' : null;
    f.start(p, door); f.step(260);
    assert.equal(f.state().room.preparation.phase, 'seeded');
    assert.equal(f.seeds.length, 4); assert.equal(p.moves.length, 0);
    if (damage === 'inventory') f.rewardContainer(0).slots.delete(0);
    if (damage === 'shell') f.blocks.set(key(add(f.state().room.origin, { x: 0, y: 4, z: 5 })), f.block('minecraft:air'));
    if (damage === 'route') f.blocks.set(key(add(f.state().room.origin, ARCANUM.arrival)), f.block('minecraft:stone'));
    f.flags.worldWrite = null; f.reload();
    if (damage === 'none') f.build(p, door);
    else { f.leave(p); f.enter(p); f.step(260); assert.notEqual(f.state().room.phase, 'ready', damage); }
    assert.equal(f.seeds.length, 4, damage); assert.equal(f.places.length, 1, damage);
  }
});

await group('write-after-commit exceptions preserve conservative intent and usable effect receipts', () => {
  for (const phase of ['placing', 'placed', 'seeding', 'seeded', 'ready']) {
    const f = fixture(), p = f.player(), door = f.face();
    f.flags.worldWrite = record => (phase === 'ready' ? record?.room?.phase === phase
      : record?.room?.preparation?.phase === phase) ? 'after' : null;
    f.start(p, door); f.step(260);
    const placements = f.places.length, seeds = f.seeds.length;
    f.flags.worldWrite = null; f.reload();
    if (['placed', 'seeded', 'ready'].includes(phase)) {
      f.build(p, door); assert.equal(f.state().room.phase, 'ready', phase);
      assert.equal(f.seeds.length, 4, phase);
    } else {
      f.leave(p); f.enter(p); f.step(260);
      assert.equal(p.moves.length, 0, phase); assert.equal(f.seeds.length, seeds, phase);
    }
    assert.equal(f.places.length, placements, phase);
  }
});

await group('late shell loss and occupants block reward writes after placement', () => {
  for (const failure of ['shell', 'player', 'entity', 'entity-unavailable']) {
    const f = fixture(), p = f.player(), door = f.face(); f.start(p, door);
    f.until(() => f.places.length === 1); f.step(4);
    if (failure === 'shell') f.blocks.set(key(add(f.state().room.origin, { x: 0, y: 4, z: 5 })), f.block('minecraft:air'));
    else if (failure === 'player') { const visitor = f.player('intruder'); visitor.location = add(f.state().room.origin, { x: 11, y: 3, z: 11 }); }
    else if (failure === 'entity') f.flags.entities = [{ id: 'intruder' }];
    else f.dim.getEntities = () => { throw new Error('injected unavailable entity occupancy'); };
    f.step(260);
    assert.equal(f.seeds.length, 0, failure); assert.equal(p.moves.length, 0, failure);
    assert.notEqual(f.state().room.phase, 'ready', failure); assert.equal(f.places.length, 1, failure);
  }
});

await group('an active preparation refuses missing, unreadable or changed primary authority', () => {
  for (const checkpoint of ['scan', 'placed']) for (const failure of ['missing', 'corrupt', 'unreadable', 'changed']) {
    const f = fixture(), p = f.player(), door = f.face(); f.start(p, door);
    if (checkpoint === 'scan') f.step(10); else f.until(() => f.places.length === 1);
    const before = f.properties.get(DOOR_STATE_KEY), original = JSON.parse(before);
    if (failure === 'missing') f.properties.delete(DOOR_STATE_KEY);
    if (failure === 'corrupt') f.properties.set(DOOR_STATE_KEY, '{broken');
    if (failure === 'unreadable') f.flags.stateReadFail = true;
    if (failure === 'changed') { original.rewards.suppressed = true; f.properties.set(DOOR_STATE_KEY, JSON.stringify(original)); }
    const backing = f.properties.get(DOOR_STATE_KEY), attempts = f.writes.length;
    f.step(260);
    assert.equal(f.properties.get(DOOR_STATE_KEY), backing, `${checkpoint}/${failure}`);
    assert.equal(f.writes.length, attempts, `${checkpoint}/${failure}`);
    assert.equal(f.places.length, checkpoint === 'placed' ? 1 : 0, `${checkpoint}/${failure}`);
    assert.equal(f.seeds.length, 0, `${checkpoint}/${failure}`); assert.equal(p.moves.length, 0, `${checkpoint}/${failure}`);
  }
});

await group('legacy ready and visited rooms preserve depleted shared rewards without preparation metadata', () => {
  for (const visited of [false, true]) {
    const f = fixture(), p = f.player(), door = f.face(); f.build(p, door);
    const record = f.state(); delete record.room.preparation; record.room.visited = visited;
    record.rewards.claimed[0] = true; f.properties.set(DOOR_STATE_KEY, JSON.stringify(record));
    f.rewardContainer(0).slots.delete(0); f.reload(); f.leave(p); f.enter(p);
    assert.equal(f.pilot.occupiedRealm(p), true); assert.equal(f.places.length, 1); assert.equal(f.seeds.length, 4);
    assert.equal(f.rewardContainer(0).getItem(0), undefined); assert.equal(f.state().room.preparation, undefined);
    assert.equal(f.pilot.requestReturn(p), true);
    f.leave(p); const moves = p.moves.length;
    f.blocks.set(key(add(f.state().room.origin, { x: 0, y: 4, z: 5 })), f.block('minecraft:air'));
    f.enter(p); f.step(260);
    assert.equal(p.moves.length, moves, 'cached readiness cannot bypass a new nonsentinel shell hole');
    assert.equal(f.places.length, 1); assert.equal(f.seeds.length, 4);
  }
});

console.log(`Demon Door pilot: ${count} groups passed; engine checks remain unrun.`);

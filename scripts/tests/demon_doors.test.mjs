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

function fixture({ sourceDimension = 'minecraft:overworld' } = {}) {
  const properties = new Map(), blocks = new Map(), commands = [], commandDimensions = [], errors = [], places = [], players = [];
  const source = { x: 10, y: 1, z: 10, dimension: sourceDimension };
  const system = { currentTick: 0 };
  const flags = { loaded: true, lease: true, structure: true, entities: [], teleport: 'ok', seedFail: false, sourceReady: true, damage: null };
  class ItemStack {
    constructor(typeId, amount) { this.typeId = typeId; this.amount = amount; }
    setLore(lore) { this.lore = lore; }
  }
  function chest() {
    const slots = new Map();
    return { size: 27, getItem: (slot) => slots.get(slot), setItem(slot, value) {
      if (flags.seedFail) { flags.seedFail = false; throw new Error('injected inventory failure'); }
      if (value) slots.set(slot, value); else slots.delete(slot);
    } };
  }
  function block(typeId = 'minecraft:air', inventory = null) {
    return { typeId, isAir: typeId === 'minecraft:air', getComponent: (name) => name === 'minecraft:inventory' && inventory ? { container: inventory } : undefined };
  }
  const dim = {
    id: 'minecraft:overworld',
    getBlock(p) {
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
    if (!flags.structure) throw new Error('pack structure missing');
    places.push(plain(origin));
    for (let i = 0; i < geometry.grid.length; i++) {
      const position = { x: Math.floor(i / (28 * 49)), y: Math.floor(i / 49) % 28, z: i % 49 };
      const type = geometry.palette[geometry.grid[i]];
      blocks.set(key(add(origin, position)), block(type, ['minecraft:chest', 'minecraft:barrel'].includes(type) ? chest() : null));
    }
    if (flags.damage) blocks.set(key(add(origin, flags.damage.at)), block(flags.damage.type));
  }
  const world = {
    getDynamicProperty: (name) => properties.get(name),
    setDynamicProperty: (name, value) => value === undefined ? properties.delete(name) : properties.set(name, value),
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
  const reload = () => (pilot = createDemonDoorPilot({ world, system, ItemStack, placeRoom, sourceReady: () => flags.sourceReady, report: (error) => errors.push(error) }));
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
  reload();
  return { source, system, flags, block, blocks, properties, commands, commandDimensions, errors, places, players, dim, world,
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

await group('interrupted private preparation resumes without duplicate room reward', () => {
  const f = fixture(), p = f.player(), door = f.face();
  f.flags.seedFail = true;
  f.pilot.registerGuild(f.source, door, { isNew: true });
  f.pilot.interact(p, door, 'minecraft:lantern');
  f.step(200);
  assert.equal(f.state().room.phase, 'placing');
  assert.equal(f.state().rewards.seeded, false);
  assert.equal(p.moves.length, 0);
  f.reload(); f.build(p, door);
  assert.equal(f.state().rewards.seeded, true);
  for (let i = 0; i < ARCANUM.rewards.length; i++) assert.equal(f.rewardContainer(i).getItem(0).amount, 1);
  const before = f.places.length;
  f.reload(); f.leave(p); f.enter(p);
  assert.equal(f.places.length, before, 'a ready room is never reconstructed');
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

console.log(`Demon Door pilot: ${count} groups passed; engine checks remain unrun.`);

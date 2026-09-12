// Execute the real lifecycle, generated manifests and main initialization /
// maintenance callbacks. No copied cave builder or synthetic route authority.
// node --experimental-vm-modules scripts/tests/guild_caves.test.mjs
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
import test from 'node:test';
import { parse } from 'espree';

async function load(path) {
  const mod = new vm.SourceTextModule(fs.readFileSync(path, 'utf8'));
  await mod.link(() => { throw Error('Unexpected module dependency'); });
  await mod.evaluate();
  return mod.namespace;
}
const api = await load('packs/Fablecraft_BP/scripts/guild_caves.js');
const { DATA } = await load('packs/Fablecraft_BP/scripts/fc_gamedata.js');
const main = fs.readFileSync('packs/Fablecraft_BP/scripts/main.js', 'utf8');
const ast = parse(main, { ecmaVersion: 'latest', sourceType: 'module', range: true });
const declaration = (name) => {
  const node = ast.body.find((n) => n.type === 'FunctionDeclaration' && n.id.name === name
    || n.type === 'VariableDeclaration' && n.declarations.some((d) => d.id.name === name));
  assert.ok(node, `Actual production declaration ${name}`);
  return main.slice(...node.range);
};
const KEY = 'fc_guild_caves_v1';
const coordinate = (p) => `${p.x},${p.y},${p.z}`;
function permutation(name, states = {}) {
  const actual = { ...(name.endsWith('_slab') ? { 'minecraft:vertical_half': 'bottom' } : {}),
    ...(name === 'minecraft:cobblestone_wall' ? { wall_connection_type_east: 'none', wall_connection_type_north: 'none',
      wall_connection_type_south: 'none', wall_connection_type_west: 'none', wall_post_bit: false } : {}),
    ...(name === 'minecraft:water' ? { liquid_depth: 0 } : {}), ...states };
  return { name, getAllStates: () => ({ ...actual }) };
}
function decode(manifest, base) {
  const result = [], [sx, sy, sz] = manifest.size, [ox, oy, oz] = manifest.origin;
  let i = 0;
  for (const [pid, count] of manifest.runs) for (let n = 0; n < count; n++, i++) {
    result.push({ x: base.x + ox + Math.floor(i / (sy * sz)), y: base.y + oy + Math.floor(i / sz) % sy,
      z: base.z + oz + i % sz, ...manifest.palette[pid] });
  }
  assert.equal(i, sx * sy * sz);
  return result;
}

export function fixture({ physics = false, chamber = DATA.guildChamber } = {}) {
  const base = { x: 0, y: 40, z: 0 }, props = new Map(), cells = new Map(), writes = [], jobs = new Map(), timeouts = [];
  let serial = 0, tick = 0, context, runtime, fault = null, propertyFault = null, loot = 0, art = 0, bulk = 0;
  const bulkOrigins = [];
  props.set('fc_guild_base', JSON.stringify(base));
  props.set('fc_guild_placed', true);
  props.set('fc_guild_terrain_v3', true);
  function put(at, name, states = {}) {
    const block = { typeId: name, permutation: permutation(name, states),
      getComponent(id) { return id === 'minecraft:inventory' && this.typeId.includes('chest') ? {} : undefined; },
      setPermutation(value) {
        const mode = fault?.op === 'write' && (!fault.key || fault.key === coordinate(at)) ? fault.mode : null;
        if (mode) fault = null;
        if (mode === 'throw') throw Error('injected setPermutation');
        if (mode === 'silent') return;
        if (physics && ['minecraft:lantern', 'minecraft:soul_lantern'].includes(value.name)) {
          const hanging = value.getAllStates().hanging;
          const support = cells.get(coordinate({ ...at, y: at.y + (hanging ? 1 : -1) }));
          assert.ok(support && support.typeId !== 'minecraft:air', `Lantern support before placement: ${coordinate(at)}`);
        }
        if (physics && value.name === 'minecraft:water') {
          assert.equal(cells.get(coordinate({ ...at, y: at.y - 1 }))?.typeId, 'minecraft:glass', 'Water support is already complete');
          for (const [dx, dz] of [[1, 0], [-1, 0], [0, 1], [0, -1]]) {
            const other = cells.get(coordinate({ ...at, x: at.x + dx, z: at.z + dz }));
            assert.ok(other && other.typeId !== 'minecraft:air', `Skylight containment before fluid source: ${coordinate(at)}`);
          }
        }
        this.typeId = value.name; this.permutation = value;
        if (physics && value.name === 'minecraft:cobblestone_wall') this.permutation = permutation(value.name,
          { ...value.getAllStates(), wall_connection_type_east: 'short', wall_post_bit: true });
        writes.push({ key: coordinate(at), name: value.name });
        if (mode === 'after') throw Error('injected after mutation');
      },
    };
    cells.set(coordinate(at), block);
    return block;
  }
  for (const cell of decode(DATA.guildChamber.entry, base)) put(cell, cell.name, cell.states);
  const dim = { id: 'minecraft:overworld', getBlock(at) {
    if (fault?.op === 'read' && (!fault.key || fault.key === coordinate(at))) {
      const mode = fault.mode; fault = null;
      if (mode === 'throw') throw Error('injected getBlock');
      return undefined;
    }
    return cells.get(coordinate(at)) ?? put(at, 'minecraft:stone');
  } };
  const world = { getDynamicProperty: (key) => props.get(key),
    setDynamicProperty(key, value) {
      if (propertyFault?.(key, value)) { propertyFault = null; throw Error('injected journal write'); }
      if (typeof value === 'string') assert.ok(Buffer.byteLength(value) <= 32767, `${key} property capacity`);
      props.set(key, value);
    },
    getDimension: () => dim, getTimeOfDay: () => 0,
    structureManager: { place(id, dimension, origin) {
      bulk++; bulkOrigins.push({ ...origin });
      if (fault?.op === 'structure') { fault = null; throw Error('injected surface placement'); }
    } },
  };
  const system = { get currentTick() { return tick; },
    runJob(generator) { jobs.set(++serial, generator); return serial; },
    clearJob(id) { jobs.delete(id); },
    runTimeout(fn, delay = 0) { timeouts.push(Object.assign(fn, { delay })); },
  };
  const noOp = () => {};
  function reload(nextChamber = chamber) {
    chamber = nextChamber;
    jobs.clear();
    context = vm.createContext({ createGuildCaveLifecycle: api.createGuildCaveLifecycle, DATA: { ...DATA, guildChamber: chamber }, world, system,
      BlockPermutation: { resolve: permutation }, OW: () => dim, guildTerrainRepairRunning: false,
      fillLootChests: () => { loot++; }, hangChamberArt: () => { art++; }, ensureGuildChamberCullis: noOp,
      guildBounds: () => ({ base }), clearGuildRingScarecrows: noOp, repairGuildDemonApproach: noOp,
      repairGuildTerrain: noOp, repairGuildSkirtVegetation: noOp, guildApprentices: () => [],
      guildTraining: { beginPass: noOp }, guildTrainingSession: () => null, TICKS: () => tick,
      guildResidents: { initialize: () => true, reconcile: noOp },
      forceLoadGuild: () => true, sampleGroundY: () => base.y + 1, OVERWORLD_SEA_LEVEL: 40,
      showHeroTitle: noOp, ensureGuildDoorPilot: noOp,
      registerCullis: () => { throw Error('injected earlier decoration failure'); },
    });
    vm.runInContext(['GUILD', 'guildCaves', 'placeGuildAnnexes', 'carveGuildCaves', 'buildGuildWhenReady', 'placeGuildNear'].map(declaration).join('\n'), context);
    const interval = ast.body.find((n) => n.type === 'ExpressionStatement'
      && main.slice(...n.range).startsWith('system.runInterval(')
      && main.slice(...n.range).includes('placeGuildAnnexes(dim)'));
    assert.ok(interval, 'Actual maintenance retries the annex');
    const maintenance = vm.runInContext(`(${main.slice(...interval.expression.arguments[0].range)})`, context);
    runtime = { ...vm.runInContext('({ enroll: guildCaves.enroll, annex: placeGuildAnnexes, build: buildGuildWhenReady, near: placeGuildNear })', context), maintenance };
    return runtime;
  }
  function step(n = 1) {
    for (let i = 0; i < n && jobs.size; i++) {
      tick++;
      for (const [id, job] of [...jobs]) if (job.next().done) jobs.delete(id);
    }
  }
  function drain() { let n = 0; while (jobs.size && n++ < 20000) step(); assert.equal(jobs.size, 0, 'bounded work'); }
  function until(predicate) { let n = 0; while (!predicate() && jobs.size && n++ < 20000) step(); assert.ok(predicate()); }
  function retry() { tick += 250; runtime.maintenance(); drain(); }
  reload();
  return { base, cells, props, writes, jobs, world, dim, put, reload, step, drain, until, retry,
    runtime: () => runtime, record: () => JSON.parse(props.get(KEY) ?? 'null'),
    fault: (value) => { fault = value; }, propertyFault: (fn) => { propertyFault = fn; },
    decorations: () => [loot, art], bulk: () => bulk, bulkOrigins,
    advance: (n) => { tick += n; },
    timeouts, context: () => context,
  };
}

function start(f) { assert.equal(f.runtime().enroll(f.base), true); f.runtime().annex(f.dim); }
function ready(f) {
  assert.equal(f.record().phase, 'ready');
  assert.equal(f.props.get('fc_guild_caves_done'), true);
  assert.equal(f.props.get('fc_guild_chamber_placed'), true);
}

test('actual annex records completion only after every assembled Chamber/cave cell is verified', (t) => {
  const f = fixture(); start(f);
  assert.equal(f.writes.length, 0); assert.equal(f.jobs.size, 1);
  assert.equal(f.props.get('fc_guild_caves_done'), undefined);
  f.until(() => f.writes.length > 0);
  assert.equal(f.props.get('fc_guild_caves_done'), undefined);
  f.drain(); ready(f);
  const expected = new Map(decode(DATA.guildChamber, f.base).map((c) => [coordinate(c), c]));
  for (const cell of api.guildCavePlan(f.base)) expected.set(coordinate(cell), cell);
  for (const [key, cell] of expected) {
    assert.equal(f.cells.get(key).typeId, cell.name, key);
    assert.deepEqual(f.cells.get(key).permutation.getAllStates(), permutation(cell.name, cell.states).getAllStates(), key);
  }
  assert.equal(f.bulk(), 0, 'Per-cell placement never replaces a whole occupied structure');
  assert.deepEqual(f.decorations(), [1, 0]);
  const pages = [...f.props].filter(([key]) => key.startsWith(`${KEY}_`)).map(([, value]) => Buffer.byteLength(value));
  t.diagnostic(`${f.record().count} final cells; ${pages.length} journal pages; largest page ${Math.max(...pages)} bytes; total ${pages.reduce((a, b) => a + b, 0)} bytes`);
});

test('startup enrolls before earlier decoration exception and actual maintenance still builds', () => {
  const f = fixture(); f.props.delete('fc_guild_placed');
  f.runtime().build({ dimension: f.dim }, f.dim, f.base, 0);
  f.timeouts.shift()();
  assert.equal(f.record().phase, 'snapshot');
  assert.equal(f.jobs.size, 0, 'Earlier decoration exception prevented direct annex callback');
  f.runtime().maintenance(); f.drain(); ready(f);
});

test('failed enrollment persistence prevents initial Guild placement and the actual build retry recovers', () => {
  const f = fixture(); f.props.delete('fc_guild_placed');
  f.propertyFault((key) => key === KEY);
  f.runtime().build({ dimension: f.dim }, f.dim, f.base, 0);
  f.timeouts.shift()();
  assert.equal(f.props.get('fc_guild_placed'), undefined);
  assert.equal(f.bulk(), 0); assert.equal(f.record(), null);
  f.timeouts.shift()(); // existing build retry schedules its placement callback
  f.timeouts.shift()();
  assert.equal(f.record().phase, 'snapshot'); assert.equal(f.bulk(), 1);
  f.runtime().maintenance(); f.drain(); ready(f);
});

test('failed surface placement resumes the original enrolled anchor after reload and player movement', () => {
  const f = fixture(); f.props.delete('fc_guild_placed');
  f.fault({ op: 'structure' }); f.runtime().build({ dimension: f.dim }, f.dim, f.base, 0);
  f.timeouts.shift()(); assert.equal(f.props.get('fc_guild_placed'), undefined);
  assert.deepEqual(JSON.parse(f.record().anchor), [0, 40, 0]);
  f.reload(); f.timeouts.length = 0; f.advance(250);
  f.props.set('fc_guild_build_tick', 5000000); // previous session had a much longer uptime
  f.runtime().near({ dimension: f.dim, location: { x: 400, y: 100, z: 300 } }); f.timeouts.shift()();
  assert.deepEqual(f.bulkOrigins, [{ x: 0, y: 40, z: 0 }, { x: 0, y: 40, z: 0 }]);
  f.runtime().maintenance(); f.drain(); ready(f);
});

test('overlapping saved build tick schedules founding retry at the original anchor without duplicate placement', () => {
  const f = fixture(); f.props.delete('fc_guild_placed');
  assert.equal(f.runtime().enroll(f.base), true);
  f.props.set('fc_guild_build_tick', 10); f.reload(); f.advance(20);
  const hero = { dimension: f.dim, location: { x: 400, y: 100, z: 300 } };
  f.runtime().near(hero);
  assert.equal(f.bulk(), 0); assert.equal(f.timeouts.length, 1);
  const guardedRetry = f.timeouts.shift();
  assert.equal(guardedRetry.delay, 190, 'Retry once the saved guard expires');
  f.advance(guardedRetry.delay); guardedRetry();
  assert.equal(f.bulk(), 0); assert.equal(f.timeouts.length, 1);
  f.runtime().near(hero); // another same-session trigger while placement is queued
  const placement = f.timeouts.shift(); f.advance(placement.delay); placement();
  assert.equal(f.props.get('fc_guild_placed'), true);
  assert.equal(f.bulk(), 1); assert.deepEqual(f.bulkOrigins, [{ x: 0, y: 40, z: 0 }]);
  while (f.timeouts.length) {
    const callback = f.timeouts.shift(); f.advance(callback.delay); callback();
  }
  assert.equal(f.bulk(), 1, 'Already placed founding refuses queued duplicate retries');
  f.runtime().maintenance(); f.drain(); ready(f);
});

test('fresh founding and delayed callbacks refuse other dimensions; later Overworld founding can recover', () => {
  const f = fixture(); f.props.delete('fc_guild_placed');
  const nether = { ...f.dim, id: 'minecraft:nether' };
  const hero = { dimension: nether, location: { x: -16, y: 40, z: -16 } };
  f.runtime().near(hero); f.runtime().build(hero, nether, f.base, 0);
  assert.equal(f.timeouts.length, 0); assert.equal(f.record(), null); assert.equal(f.bulk(), 0);
  hero.dimension = f.dim; f.runtime().near(hero); hero.dimension = nether; f.timeouts.shift()();
  assert.equal(f.record(), null); assert.equal(f.bulk(), 0);
  hero.dimension = f.dim; f.advance(250); f.runtime().near(hero); f.timeouts.shift()();
  assert.equal(f.bulk(), 1); assert.equal(f.record().phase, 'snapshot');
  f.runtime().annex(nether); assert.equal(f.jobs.size, 0);
  f.runtime().maintenance(); f.drain(); ready(f);
});

test('permutation resolution and scheduler failures after enrollment retry without losing original ownership', () => {
  for (const fail of ['resolve', 'schedule']) {
    const f = fixture(); assert.equal(f.runtime().enroll(f.base), true);
    if (fail === 'resolve') {
      const resolver = f.context().BlockPermutation.resolve;
      f.context().BlockPermutation.resolve = (...args) => { f.context().BlockPermutation.resolve = resolver; throw Error(`injected ${args[0]}`); };
    } else {
      const schedule = f.context().system.runJob;
      f.context().system.runJob = (...args) => { f.context().system.runJob = schedule; throw Error(`injected schedule ${args.length}`); };
    }
    f.runtime().annex(f.dim); assert.equal(f.jobs.size, 0); assert.equal(f.writes.length, 0);
    f.reload(); f.retry(); ready(f);
  }
});

test('terrain jobs must finish before any Chamber placement; manifest replaces delayed scrubbing', () => {
  const f = fixture(); f.props.delete('fc_guild_terrain_v3'); start(f);
  assert.equal(f.jobs.size, 0); assert.equal(f.writes.length, 0);
  f.props.set('fc_guild_terrain_v3', true); f.retry(); ready(f);
  assert.equal(main.includes('function hollowChamber('), false);
});

test('canceled jobs retry through production maintenance; stale generator cannot resume writing', () => {
  const f = fixture(); start(f); f.until(() => f.writes.length > 30);
  const old = [...f.jobs.values()][0]; f.jobs.clear();
  const before = f.writes.length; f.retry(); ready(f);
  assert.ok(f.writes.length > before);
  const finished = f.writes.length; old.next(); assert.equal(f.writes.length, finished);
});

test('snapshot, partially placed Chamber and verification reloads resume without reseeding', () => {
  for (const phase of ['snapshot', 'applying', 'verification']) {
    const f = fixture(); start(f);
    if (phase === 'snapshot') f.step(2);
    else if (phase === 'applying') f.until(() => f.writes.length > 30);
    else f.until(() => {
      const last = [...f.props.keys()].filter((k) => k.startsWith(`${KEY}_`)).at(-1);
      return last && /^1+$/.test(JSON.parse(f.props.get(last)).done);
    });
    f.reload(); f.runtime().maintenance(); f.drain(); ready(f);
    const before = f.writes.length; f.reload(); f.runtime().maintenance();
    assert.equal(f.writes.length, before); assert.deepEqual(f.decorations(), [1, 0]);
  }
});

test('an enrolled old Chamber plan finishes its exact original geometry across a visual revision', () => {
  const legacy = JSON.parse(fs.readFileSync('scripts/data/guild_chamber_gp5.json', 'utf8'));
  const revision = JSON.parse(JSON.stringify(legacy));
  // An independent valid material revision makes the lifecycle regression fail
  // before the compatibility selector, without relying on one decorative design.
  revision.palette = revision.palette.map(p => p.name === 'minecraft:quartz_pillar'
    ? { name: 'minecraft:polished_andesite', states: {} } : p);
  revision.compatibility = [legacy];
  assert.notDeepEqual(revision.palette, legacy.palette);
  for (const phase of ['snapshot', 'applying', 'verification']) {
    const f = fixture({ chamber: legacy }); start(f);
    if (phase === 'snapshot') f.step(2);
    else if (phase === 'applying') f.until(() => f.writes.length > 30);
    else f.until(() => {
      const last = [...f.props.keys()].filter(k => k.startsWith(`${KEY}_`)).at(-1);
      return last && /^1+$/.test(JSON.parse(f.props.get(last)).done);
    });
    const hash = f.record().hash;
    f.reload(revision); f.runtime().maintenance(); f.drain(); ready(f);
    assert.equal(f.record().hash, hash, phase);
    const expected = new Map([...decode(legacy, f.base), ...api.guildCavePlan(f.base)].map(c => [coordinate(c), c]));
    for (const [key, cell] of expected) assert.equal(f.cells.get(key)?.typeId, cell.name, `${phase}: ${key}`);
    const before = f.writes.length; f.reload(revision); f.runtime().maintenance();
    assert.equal(f.writes.length, before); assert.deepEqual(f.decorations(), [1, 0]);
  }
});

test('unknown plan hashes and damaged completed legacy cells never authorize a new revision', () => {
  const legacy = JSON.parse(fs.readFileSync('scripts/data/guild_chamber_gp5.json', 'utf8'));
  const revision = { ...DATA.guildChamber, compatibility: [legacy] };
  for (const mode of ['unknown-hash', 'changed-cell']) {
    const f = fixture({ chamber: legacy }); start(f); f.until(() => f.writes.length > 30);
    if (mode === 'unknown-hash') f.props.set(KEY, JSON.stringify({ ...f.record(), hash: 'unknown-plan' }));
    else {
      const [x, y, z] = f.writes[0].key.split(',').map(Number);
      f.put({ x, y, z }, 'minecraft:chest');
    }
    const before = f.writes.length, original = f.props.get(KEY);
    f.reload(revision); f.runtime().maintenance(); f.drain();
    assert.equal(f.writes.length, before, mode); assert.notEqual(f.record().phase, 'ready');
    if (mode === 'unknown-hash') assert.equal(f.props.get(KEY), original);
  }
});

test('the shipped Chamber revision resumes a GP5 build without substituting new wall cells', () => {
  const legacy = JSON.parse(fs.readFileSync('scripts/data/guild_chamber_gp5.json', 'utf8'));
  assert.notDeepEqual(DATA.guildChamber.runs, legacy.runs, 'The test must cross the actual shipped geometry revision');
  const f = fixture({ chamber: legacy }); start(f); f.until(() => f.writes.length > 30);
  const enrolled = f.record().hash;
  f.reload(DATA.guildChamber); f.runtime().maintenance(); f.drain(); ready(f);
  assert.equal(f.record().hash, enrolled);
  const expected = new Map([...decode(legacy, f.base), ...api.guildCavePlan(f.base)].map(c => [coordinate(c), c]));
  for (const [key, cell] of expected) assert.equal(f.cells.get(key)?.typeId, cell.name, key);
  assert.deepEqual(f.decorations(), [1, 0]);
});

test('unloaded and throwing getBlock during snapshot or Chamber placement are retryable', () => {
  for (const mode of ['missing', 'throw']) for (const phase of ['snapshot', 'applying']) {
    const f = fixture(); start(f);
    if (phase === 'applying') f.until(() => f.writes.length > 30);
    f.fault({ op: 'read', mode }); f.drain();
    assert.notEqual(f.record().phase, 'ready'); assert.equal(f.props.get('fc_guild_caves_done'), undefined);
    f.retry(); ready(f);
  }
});

test('the audited unavailable bridge head cell prevents completion and maintenance opens it on retry', () => {
  const f = fixture(); start(f); f.until(() => f.writes.length > 30);
  f.fault({ op: 'read', mode: 'missing', key: '26,20,16' }); f.drain();
  assert.notEqual(f.record().phase, 'ready'); assert.equal(f.props.get('fc_guild_caves_done'), undefined);
  assert.equal(f.cells.get('26,20,16').typeId, 'minecraft:stone');
  f.retry(); ready(f); assert.equal(f.cells.get('26,20,16').typeId, 'minecraft:air');
});

test('failed, silently dropped and throwing-after-mutation Chamber writes remain incomplete until retry', () => {
  for (const mode of ['throw', 'silent', 'after']) {
    const f = fixture(); f.fault({ op: 'write', mode }); start(f); f.drain();
    assert.equal(f.record().phase, 'applying'); assert.equal(f.props.get('fc_guild_chamber_placed'), undefined);
    f.retry(); ready(f);
    assert.equal(new Set(f.writes.map((w) => w.key)).size, f.writes.length, 'Successful writes are never repeated');
  }
});

test('journal failure after successful write recognizes the target without writing it twice', () => {
  const f = fixture(); f.propertyFault((key, value) => key.startsWith(`${KEY}_`) && JSON.parse(value).done.includes('1'));
  start(f); f.drain(); assert.equal(f.writes.length, 1); assert.notEqual(f.record().phase, 'ready');
  f.reload(); f.retry(); ready(f);
  assert.equal(f.writes.filter((w) => w.key === f.writes[0].key).length, 1);
});

test('foreign underground inventory or masonry refuses the entire snapshot without block writes', () => {
  for (const name of ['minecraft:chest', 'minecraft:stone_bricks', 'minecraft:diamond_block']) {
    const f = fixture(); f.put({ x: 20, y: 20, z: 35 }, name); start(f); f.drain();
    assert.equal(f.record().issue, 'foreign-original'); assert.equal(f.writes.length, 0);
    f.retry(); assert.equal(f.writes.length, 0); assert.equal(f.cells.get('20,20,35').typeId, name);
  }
});

test('player edits to recorded unfinished or completed cells are preserved after reload', () => {
  for (const completed of [false, true]) {
    const f = fixture(); start(f); f.until(() => f.writes.length > 30);
    const key = completed ? f.writes[0].key : '40,20,35';
    const [x, y, z] = key.split(',').map(Number);
    f.put({ x, y, z }, 'minecraft:chest'); f.reload(); f.retry();
    assert.equal(f.record().issue, 'changed-cell');
    assert.equal(f.cells.get(key).typeId, 'minecraft:chest'); assert.notEqual(f.record().phase, 'ready');
  }
});

test('same block type with changed permutation is preserved; ready rooms perform no repair', () => {
  const f = fixture(); start(f); f.until(() => f.writes.some((w) => w.name.endsWith('_slab')));
  const slab = f.writes.find((w) => w.name.endsWith('_slab'));
  const [x, y, z] = slab.key.split(',').map(Number);
  f.put({ x, y, z }, slab.name, { 'minecraft:vertical_half': 'top' }); f.reload(); f.retry();
  assert.equal(f.record().issue, 'changed-cell');
  assert.equal(f.cells.get(slab.key).permutation.getAllStates()['minecraft:vertical_half'], 'top');
  const fresh = fixture(); start(fresh); fresh.drain(); ready(fresh);
  fresh.put({ x: 26, y: 23, z: 42 }, 'minecraft:chest'); const count = fresh.writes.length;
  fresh.reload(); fresh.runtime().maintenance(); assert.equal(fresh.writes.length, count);
  assert.equal(fresh.cells.get('26,23,42').typeId, 'minecraft:chest');
});

test('derived wall connections are accepted; lantern supports and skylight containment precede placement', () => {
  const f = fixture({ physics: true }); start(f); f.drain(); ready(f);
  const walls = [...f.cells.values()].filter((b) => b.typeId === 'minecraft:cobblestone_wall');
  assert.ok(walls.length > 10);
  assert.ok(walls.every((b) => b.permutation.getAllStates().wall_connection_type_east === 'short'));
  const firstFluid = f.writes.findIndex((w) => w.name === 'minecraft:water');
  assert.ok(firstFluid > 0);
  assert.ok(f.writes.slice(firstFluid).every((w) => w.name === 'minecraft:water'));
  assert.equal(f.cells.get('26,23,29').permutation.getAllStates().hanging, true, 'Arch lantern hangs from the lintel');
});

test('legacy flags, unknown records and changed anchors never authorize occupied-world construction', () => {
  for (const flags of [{}, { fc_guild_caves_done: true }, { fc_guild_chamber_placed: true },
    { [KEY]: 'bad JSON' }, { [KEY]: JSON.stringify({ schema: 99 }) }]) {
    const f = fixture(); for (const [key, value] of Object.entries(flags)) f.props.set(key, value);
    f.runtime().maintenance(); f.drain(); assert.equal(f.writes.length, 0);
    assert.equal(f.bulk(), 0);
  }
  const f = fixture(); start(f); f.step(2); f.reload();
  f.props.set('fc_guild_base', JSON.stringify({ ...f.base, x: 1 })); f.runtime().annex(f.dim); f.drain();
  assert.equal(f.writes.length, 0);
});

test('missing or corrupt saved originals fail closed instead of resnapshotting occupied cells', () => {
  for (const damage of ['missing', 'corrupt']) {
    const f = fixture(); start(f); f.until(() => f.writes.length > 30); f.reload();
    if (damage === 'missing') f.props.delete(`${KEY}_0`);
    else f.props.set(`${KEY}_0`, '{}');
    const before = f.writes.length; f.retry(); assert.equal(f.writes.length, before);
    assert.notEqual(f.record().phase, 'ready');
  }
});

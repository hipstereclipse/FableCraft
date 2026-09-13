// Compare actual preceding/current door owners with the same production adapter fixture.
import assert from 'node:assert/strict';
import vm from 'node:vm';
import { readFile, writeFile } from 'node:fs/promises';
import { createHash } from 'node:crypto';
import { parse } from 'espree';

const adapterPath = 'scripts/tests/demon_door_integration.test.mjs';
const adapter = await readFile(adapterPath, 'utf8');
const ast = parse(adapter, { ecmaVersion: 'latest', sourceType: 'module', range: true });
const firstTest = ast.body.find(n => n.type === 'ExpressionStatement' && n.expression.callee?.name === 'test').range[0];
let prefix = adapter.slice(0, firstTest);
for (const node of ast.body.filter(n => n.type === 'ImportDeclaration').reverse()) {
  prefix = prefix.slice(0, node.range[0]) + prefix.slice(node.range[1]);
}
const AsyncFunction = Object.getPrototypeOf(async function () {}).constructor;
const loadFixture = new AsyncFunction('assert', 'vm', 'readFile', 'parse', prefix
  + '\nreturn { fixture, replaceDoor(value) { sources[0] = value; } };');
const current = await readFile('packs/Fablecraft_BP/scripts/fc_demon_doors.js', 'utf8');
const baseline = await readFile('screenshots/validation/DP6/baseline-controller.js.txt', 'utf8');
const observed = {};

for (const [label, doorSource] of [['before', baseline], ['after', current]]) {
  const runtime = await loadFixture(assert, vm, readFile, parse);
  runtime.replaceDoor(doorSource);
  observed[label] = [];
  for (const boundary of ['returning', 'clear']) for (const timing of ['before', 'after']) {
    const f = await runtime.fixture(), origin = f.readyRoom(), p = f.player();
    const source = { x: 102.1, y: 65, z: 195.5, dimension: f.dimension.id };
    p.location = { x: origin.x + 24.5, y: origin.y + 3, z: origin.z + 7.5 };
    p.props.set(f.pilotApi.DOOR_RETURN_KEY, JSON.stringify({ schema: 1, doorId: 'guild', cell: 0, source, phase: 'inside' }));
    for (let x = 97; x <= 104; x++) f.blockAt({ x, y: 65, z: 196 }, 'minecraft:stone');
    const primary = f.properties.get(f.pilotApi.DOOR_STATE_KEY), setter = p.setDynamicProperty;
    let throws = 0;
    p.setDynamicProperty = (key, value) => {
      const selected = key === f.pilotApi.DOOR_RETURN_KEY && (boundary === 'clear'
        ? value === undefined : value !== undefined && JSON.parse(value).phase === 'returning');
      if (selected && timing === 'before') { throws++; throw Error('Injected write failure'); }
      setter(key, value);
      if (selected && timing === 'after') { throws++; throw Error('Injected write failure after mutation'); }
    };
    assert.throws(() => f.runtime.guildDoorPilot.requestReturn(p), /Injected write failure/);
    assert.equal(throws, 1);
    const backing = p.props.get(f.pilotApi.DOOR_RETURN_KEY);
    if (backing !== undefined) assert.deepEqual(JSON.parse(backing).source, source);
    const firstMoves = p.moves.length;
    assert.equal(firstMoves, boundary === 'clear' ? 1 : 0);
    p.setDynamicProperty = setter;
    const retry = f.runtime.guildDoorPilot.requestReturn(p);
    assert.equal(retry, boundary === 'returning');
    assert.equal(p.moves.length, 1);
    assert.deepEqual(p.location, { x: source.x, y: source.y, z: source.z });
    assert.equal(f.properties.get(f.pilotApi.DOOR_STATE_KEY), primary);
    assert.equal(f.placements.length, 0);
    assert.equal(f.payouts.length, 0);
    observed[label].push({ boundary, timing, firstMoves, retry,
      backingAfterFault: backing === undefined ? null : JSON.parse(backing),
      backingAfterRetry: p.props.get(f.pilotApi.DOOR_RETURN_KEY) ?? null,
      moves: p.moves.length, sourceRetained: true, worldHistoryUnchanged: true, placements: 0, payouts: 0 });
  }
}
assert.deepEqual(observed.after, observed.before);
const digest = value => createHash('sha256').update(value).digest('hex');
const result = { command: 'node --experimental-vm-modules screenshots/validation/DP6/independent-write-fault-probe.mjs',
  hashes: { baseline: digest(baseline), current: digest(current), adapter: digest(adapter) },
  scenariosPerOwner: 4, actualOwnerRuns: 8, observationsIdentical: true, observed,
  limits: 'Injected write-before/write-after failures, not native transaction or persistence acceptance.' };
await writeFile('screenshots/validation/DP6/independent-write-fault-results.json', JSON.stringify(result, null, 2) + '\n');
console.log(JSON.stringify({ actualOwnerRuns: 8, observationsIdentical: true, hashes: result.hashes }));

// Independent persisted-state probes of the actual controller. No production writes.
import assert from 'node:assert/strict';
import { readFile, writeFile } from 'node:fs/promises';
import { createHash } from 'node:crypto';
import vm from 'node:vm';

const source = await readFile('packs/Fablecraft_BP/scripts/guild_activity.js', 'utf8');
const module = new vm.SourceTextModule(source, { context: vm.createContext({}) });
await module.link(() => { throw Error('Unexpected controller import'); });
await module.evaluate();
const { createGuildActivityController, GUILD_ACTIVITY_CHANNELS } = module.namespace;
const OWNED = 'fc_guild_activity_owned_v1', WAIT = 'fc_guild_activity_wait_v1';
const tag = GUILD_ACTIVITY_CHANNELS.skill_range.tag;
const rows = [];

function fixture() {
  let tick = 100, raw, witness, livePlayers, ctl;
  const base = { x: 0, y: 0, z: 0 }, events = [], writes = [], hooks = {};
  function actor(id, typeId = 'minecraft:player') {
    const tags = new Set();
    return { id, typeId, tags, isValid: true, location: { x: 5, y: 1, z: 5 }, dimension: { id: 'minecraft:overworld' },
      hasTag(t) { hooks.hasTag?.(this, t); return tags.has(t); },
      addTag(t) { hooks.beforeAdd?.(this, t); tags.add(t); hooks.afterAdd?.(this, t); },
      removeTag(t) { hooks.beforeRemove?.(this, t); tags.delete(t); hooks.afterRemove?.(this, t); },
      getProperty(key) { assert.equal(key, 'fc:married'); return 0; },
      getDynamicProperty(key) { assert.equal(key, 'fc_spouse_player'); return ''; },
      triggerEvent(e) { events.push([this.id, e, tick]); hooks.event?.(this, e); },
    };
  }
  const a = actor('a'), b = actor('b'), x = actor('x', 'fc:guild_apprentice_skill'), y = actor('y', 'fc:guild_apprentice_skill');
  livePlayers = [a, b];
  const entities = [x, y];
  const options = { now: () => tick, base: () => base,
    read() { hooks.read?.(); return raw; }, write(value) { hooks.beforeWrite?.(value); raw = value; writes.push(value); hooks.afterWrite?.(value); },
    readWitness() { hooks.readWitness?.(); return witness; }, writeWitness(value) { hooks.beforeWitness?.(); witness = value; hooks.afterWitness?.(); },
    resolve(entity) { const override = hooks.resolve?.(entity); if (override !== undefined) return override;
      const i = entities.findIndex(e => e.id === entity?.id);
      return i < 0 ? { kind: 'other' } : { kind: 'bound', slot: i ? 'skill_hall' : 'skill_range', entityId: entity.id, type: entity.typeId, base }; },
    lookup: id => entities.find(e => e.id === id && e.isValid), players: () => livePlayers,
    stopTraining: () => true, trainingReserved: () => false,
  };
  const f = { a, b, x, y, hooks, events, writes, actor, base, get ctl() { return ctl; },
    get raw() { return raw; }, set raw(v) { raw = v; }, get witness() { return witness; }, set witness(v) { witness = v; },
    setPlayers(value) { livePlayers = value; }, pass() { ctl.reconcile(entities.filter(e => e.isValid)); },
    advance() { tick++; }, restart() { ctl = createGuildActivityController(options); },
    state() { return JSON.parse(raw); }, save(state) { raw = JSON.stringify(state); },
    start() { const r = ctl.request(x, a, 'follow'); assert.equal(r.accepted, true, r.reason); tick++; this.pass();
      assert.equal(ctl.status(x).blocked, false); assert.equal(a.tags.has(tag), true); },
  };
  f.restart(); f.pass(); return f;
}

async function probe(name, fn) {
  try { await fn(); rows.push({ name, passed: true }); }
  catch (error) { rows.push({ name, passed: false, error: String(error) }); }
}

for (const mode of ['follow', 'wait']) await probe(`revision exhaustion still stops loaded persisted ${mode}`, () => {
  const f = fixture(), saved = f.state();
  saved.channels.skill_range = { entityId: 'x', revision: Number.MAX_SAFE_INTEGER, mode, ownerId: 'a',
    dimension: 'minecraft:overworld', pendingTagHolders: mode === 'follow' ? ['a'] : [] };
  f.save(saved); f.x.tags.add(OWNED);
  if (mode === 'wait') f.x.tags.add(WAIT); else f.a.tags.add(tag);
  f.restart(); f.events.length = 0; f.pass();
  assert.ok(f.events.some(e => e[0] === 'x' && e[1] === 'fc:guild_activity_stop'), 'No native stop at maximum persisted revision');
  assert.equal(f.x.tags.has(OWNED), false);
  assert.equal(f.ctl.valid(f.x, Number.MAX_SAFE_INTEGER), false, 'Exhausted generation remains unavailable to callbacks');
  assert.equal(f.ctl.request(f.x, f.b, 'follow').accepted, false, 'Exhausted revision cannot authorize fresh activity');
});

await probe('corrupt witness while active removes native activity without resetting history', () => {
  const f = fixture(); f.start(); const before = f.raw; f.witness = 'true'; f.events.length = 0; f.pass();
  assert.equal(f.raw, before); assert.equal(f.x.tags.has(OWNED), false);
  assert.ok(f.events.some(e => e[0] === 'x' && e[1] === 'fc:guild_activity_stop'));
  assert.equal(f.ctl.request(f.x, f.b, 'follow').accepted, false);
});

for (const phase of ['beforeWrite', 'afterWrite']) await probe(`holder write ${phase} failure grants no player tag`, () => {
  const f = fixture(); let injected = 0;
  // Owner debt is now written while queueing, before the native-stop barrier.
  f.hooks[phase] = value => { if (JSON.parse(value).channels.skill_range.pendingTagHolders.includes('a')) { injected++; throw Error('holder write failed'); } };
  f.ctl.request(f.x, f.a, 'follow');
  f.advance(); f.pass();
  assert.ok(injected > 0, 'The owner-debt write failure must actually execute');
  assert.equal(f.a.tags.has(tag), false); assert.equal(f.x.tags.has(OWNED), false);
  assert.equal(f.events.some(e => e[1] === 'fc:guild_activity_follow_range'), false);
});

await probe('tag grant mutates then throws and owner disconnects: debt survives reload', () => {
  const f = fixture(); assert.equal(f.ctl.request(f.x, f.a, 'follow').accepted, true);
  f.hooks.afterAdd = (who, t) => { if (who === f.a && t === tag) { f.setPlayers([f.b]); throw Error('disconnect after tag mutation'); } };
  f.advance(); f.pass();
  assert.equal(f.a.tags.has(tag), true); assert.deepEqual(f.state().channels.skill_range.pendingTagHolders, ['a']);
  assert.equal(f.x.tags.has(OWNED), false); assert.equal(f.ctl.request(f.x, f.b, 'follow').accepted, false);
  f.restart(); f.pass(); assert.equal(f.ctl.request(f.x, f.b, 'follow').accepted, false);
  delete f.hooks.afterAdd; f.setPlayers([f.a, f.b]); f.pass(); assert.equal(f.a.tags.has(tag), false);
});

await probe('tag removal mutates then throws: no optimistic authority release', () => {
  const f = fixture(); f.start();
  f.hooks.afterRemove = (who, t) => { if (who === f.a && t === tag) throw Error('uncertain tag cleanup'); };
  const r = f.ctl.request(f.x, f.a, 'idle'); assert.equal(r.accepted, false);
  assert.equal(f.a.tags.has(tag), false); assert.equal(f.ctl.reserved(f.x), true);
  assert.equal(f.ctl.request(f.x, f.b, 'follow').accepted, false);
  delete f.hooks.afterRemove; f.pass(); assert.equal(f.ctl.reserved(f.x), false);
});

await probe('failed idle preemption cannot revive the captured old revision after reconciliation', () => {
  const f = fixture(), revision = f.ctl.status(f.x).revision;
  assert.equal(f.ctl.valid(f.x, revision), true);
  f.hooks.beforeWrite = () => { throw Error('preempt revision write refused'); };
  f.ctl.preempt(f.x);
  assert.equal(f.ctl.valid(f.x, revision), false);
  delete f.hooks.beforeWrite; f.pass();
  assert.equal(f.ctl.valid(f.x, revision), false, 'Old callback authority became valid again after failed preempt write');
});

await probe('unreadable unexpected online tag holder cannot disappear from cleanup debt by disconnecting', () => {
  const f = fixture(); f.start(); f.b.tags.add(tag);
  f.hooks.hasTag = (who, t) => { if (who === f.b && t === tag) throw Error('Unknown holder tag is unreadable'); };
  f.pass();
  assert.ok(f.state().channels.skill_range.pendingTagHolders.includes('b'), 'Unreadable online holder was never journaled');
  delete f.hooks.hasTag; f.setPlayers([f.a]); f.pass();
  assert.equal(f.state().channels.skill_range.mode, 'stopping');
  assert.equal(f.ctl.request(f.x, f.a, 'follow').accepted, false);
  f.setPlayers([f.a, f.b]); f.pass(); assert.equal(f.b.tags.has(tag), false);
});

await probe('failed discovery-debt write remains blocked when the unexpected holder disconnects', () => {
  const f = fixture(); f.start(); f.b.tags.add(tag);
  f.hooks.beforeWrite = value => { if (JSON.parse(value).channels.skill_range.pendingTagHolders.includes('b')) throw Error('Unexpected-holder journal write refused'); };
  f.pass(); assert.equal(f.b.tags.has(tag), true);
  delete f.hooks.beforeWrite; f.setPlayers([f.a]); f.pass();
  assert.equal(f.state().channels.skill_range.mode, 'stopping', 'Failed discovery debt was forgotten when holder went offline');
  assert.equal(f.ctl.request(f.x, f.a, 'follow').accepted, false);
  f.setPlayers([f.a, f.b]); f.pass(); assert.equal(f.b.tags.has(tag), false);
});

await probe('a conflicting newly bound candidate cannot hide the still-loaded durable owner from cleanup', () => {
  const f = fixture(); f.start(); const z = f.actor('replacement', 'fc:guild_apprentice_skill');
  f.hooks.resolve = entity => entity?.id === 'x' ? { kind: 'blocked' }
    : entity?.id === z.id ? { kind: 'bound', slot: 'skill_range', entityId: z.id, type: z.typeId, base: f.base }
      : undefined;
  f.events.length = 0; f.ctl.reconcile([z, f.y]);
  assert.ok(f.events.some(e => e[0] === 'x' && e[1] === 'fc:guild_activity_stop'), 'Conflicting candidate hid durable old ID from cleanup');
  assert.equal(f.x.tags.has(OWNED), false);
  assert.equal(f.state().channels.skill_range.entityId, 'x');
  assert.equal(f.ctl.request(z, f.b, 'follow').accepted, false);
});

for (const marker of [OWNED, WAIT]) await probe(`active Follow detects corrupted NPC marker ${marker}`, () => {
  const f = fixture(); f.start();
  if (marker === OWNED) f.x.tags.delete(OWNED); else f.x.tags.add(WAIT);
  f.events.length = 0; f.pass();
  assert.ok(f.events.some(e => e[0] === 'x' && e[1] === 'fc:guild_activity_stop'), 'Active native marker drift not reconciled');
  assert.equal(f.a.tags.has(tag), false); assert.equal(f.x.tags.has(WAIT), false);
});

const result = { source_sha256: createHash('sha256').update(source).digest('hex'),
  command: 'node --experimental-vm-modules screenshots/validation/GP19/independent-controller-probe.mjs',
  native_acceptance: 'unrun; fixture records calls rather than executing Bedrock goals',
  passed: rows.filter(r => r.passed).length, failed: rows.filter(r => !r.passed).length, cases: rows };
await writeFile('screenshots/validation/GP19/independent-controller-results.json', JSON.stringify(result, null, 2) + '\n');
console.log(JSON.stringify(result, null, 2));
if (result.failed) process.exitCode = 1;

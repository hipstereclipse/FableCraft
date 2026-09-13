// GP19: actual activity/resident/training/defence owners, emote module, and main
// adapters at mocked Bedrock boundaries. Native movement/target choice is unrun.
import nodeTest from 'node:test';
import { dirname, join } from 'node:path';
import assert from 'node:assert/strict';
import vm from 'node:vm';
import { readFile } from 'node:fs/promises';
import { parse } from 'espree';

const root = 'packs/Fablecraft_BP/scripts/';
const baselineProbe = process.env.FC_ACTIVITY_BASELINE_PROBE === '1';
const test = baselineProbe ? () => {} : nodeTest;
const mainPath = process.env.FC_ACTIVITY_MAIN_SOURCE ?? `${root}main.js`;
const main = await readFile(mainPath, 'utf8');
const currentMain = await readFile(`${root}main.js`, 'utf8');
const ast = parse(main, { ecmaVersion: 'latest', sourceType: 'module', range: true });
const currentAst = parse(currentMain, { ecmaVersion: 'latest', sourceType: 'module', range: true });
const files = ['guild_training.js', 'guild_activity.js', 'guild_activity_hooks.js',
  'guild_residents.js', 'guild_defence.js', 'fable_emotes.js', 'fable_emote_registry.js'];
const sources = new Map(await Promise.all(files.map(async file => [file, await readFile(file === 'fable_emotes.js'
  ? (process.env.FC_ACTIVITY_EMOTE_SOURCE ?? join(dirname(mainPath), file)) : root + file, 'utf8')])));
const declarations = names => names.map(name => {
  const matches = n => n.type === 'FunctionDeclaration' && n.id.name === name
    || n.type === 'VariableDeclaration' && n.declarations.some(d => d.id.name === name);
  const node = ast.body.find(matches);
  // Baseline probe uses GP18 main/emote functions. Only newly introduced wiring
  // absent in GP18 comes from the current fixture, leaving old callbacks intact.
  const fallback = baselineProbe && !node ? currentAst.body.find(matches) : null;
  assert.ok(node || fallback, `Production declaration ${name}`);
  return (node ? main : currentMain).slice(...(node ?? fallback).range);
}).join('\n');
const plain = value => JSON.parse(JSON.stringify(value));

async function fixture() {
  const operations = [], timers = [], actors = [], forms = [], properties = new Map(), bindings = new Map();
  const system = { currentTick: 10, run(fn) { timers.push({ at: this.currentTick + 1, fn }); },
    runTimeout(fn, delay) { timers.push({ at: this.currentTick + delay, fn }); },
    beforeEvents: { startup: { subscribe() {} } }, afterEvents: { scriptEventReceive: { subscribe(fn) { bindings.set('script', fn); } } } };
  const dimension = { id: 'minecraft:overworld',
    getEntities(query = {}) { return actors.filter(e => e.online && e.isValid && e.typeId !== 'minecraft:player'
      && e.dimension.id === this.id && (!query.type || query.type === e.typeId)
      && (!query.location || Math.hypot(e.location.x - query.location.x, e.location.y - query.location.y,
        e.location.z - query.location.z) <= query.maxDistance)); },
    getBlock(p) { return { typeId: Math.floor(p.y) === 0 ? 'minecraft:coarse_dirt' : 'minecraft:air', isAir: p.y > 0 }; },
    spawnParticle(id, location) { operations.push(['particle', id, location]); },
    spawnEntity() { throw Error('Integration must never create a resident/projectile'); } };
  const world = { getPlayers: () => actors.filter(e => e.online && e.isValid && e.typeId === 'minecraft:player'),
    getEntity: id => actors.find(e => e.id === id && e.online && e.isValid),
    getDynamicProperty: key => properties.get(key), setDynamicProperty(key, value) { properties.set(key, value); },
    getTimeOfDay: () => 1000, getDimension: () => dimension,
    afterEvents: { playerEmote: { subscribe() {} }, playerSpawn: { subscribe() {} } } };
  const context = vm.createContext({ console: { warn() {} },
    Math: Object.assign(Object.create(Math), { random: () => 0.9 }) });
  const engineValues = { system, world, CommandPermissionLevel: {}, CustomCommandParamType: {}, CustomCommandStatus: {} };
  const engine = new vm.SyntheticModule(Object.keys(engineValues), function () {
    for (const [key, value] of Object.entries(engineValues)) this.setExport(key, value);
  }, { context });
  const strings = new vm.SyntheticModule(['t'], function () { this.setExport('t', key => key); }, { context });
  const modules = new Map();
  for (const [file, source] of sources) modules.set(file, new vm.SourceTextModule(source, { context, identifier: file }));
  async function load(file) {
    const module = modules.get(file);
    if (module.status === 'unlinked') await module.link(specifier => {
      if (specifier === '@minecraft/server') return engine;
      if (specifier === './fc_strings.js') return strings;
      const dependency = modules.get(specifier.replace('./', ''));
      assert.ok(dependency, `Owned dependency ${specifier}`); return dependency;
    });
    if (module.status !== 'evaluated') await module.evaluate();
    return module.namespace;
  }
  const training = await load('guild_training.js'), hooks = await load('guild_activity_hooks.js');
  const activityApi = await load('guild_activity.js'), residentsApi = await load('guild_residents.js');
  const defenceApi = await load('guild_defence.js'), emotes = await load('fable_emotes.js');
  function actor(type, id) {
    const e = { typeId: type, id, isValid: true, online: true, dimension,
      location: { x: 83.5, y: 1, z: 39.5 }, name: id, nameTag: id,
      props: new Map(), sync: new Map([['fc:married', 0], ['fc:love_hate', 0], ['fc:fear_funny', 0], ['fc:ugly_attractive', 0]]),
      tags: new Set(),
      getDynamicProperty(key) { return this.props.get(key); },
      setDynamicProperty(key, value) { if (value === undefined) this.props.delete(key); else this.props.set(key, value); },
      getProperty(key) { return this.sync.get(key); }, setProperty(key, value) { this.sync.set(key, value); },
      hasTag(tag) { return this.tags.has(tag); }, getTags() { return [...this.tags]; },
      addTag(tag) { this.tags.add(tag); }, removeTag(tag) { this.tags.delete(tag); },
      triggerEvent(event) { operations.push(['event', this.id, event]); },
      playAnimation(animation) { operations.push(['animation', this.id, animation]); },
      playSound(sound) { operations.push(['sound', this.id, sound]); }, sendMessage(message) { operations.push(['message', this.id, message]); },
      lookAt() {}, getHeadLocation() { return { ...this.location, y: this.location.y + 1.6 }; },
      getEntitiesFromViewDirection() { return []; }, runCommand(command) { operations.push(['command', this.id, command]); },
      tryTeleport(point) { this.location = { ...point }; operations.push(['placement', this.id]); return true; },
      teleport(point) { this.location = { ...point }; operations.push(['teleport', this.id]); },
      getComponent(name) { if (name === 'minecraft:inventory') return { container: { size: 0 } }; return undefined; } };
    actors.push(e); return e;
  }
  const a = actor('minecraft:player', 'hero-a'), b = actor('minecraft:player', 'hero-b');
  const range = actor('fc:guild_apprentice_skill', 'canonical-range');
  const hall = actor('fc:guild_apprentice_skill', 'canonical-hall');
  const might = actor('fc:guild_apprentice_might', 'unrelated-might');
  b.location.x += 1; hall.location.x += 2; might.location.x += 3;
  range.props.set('fc_guild_resident_slot', '0,0,0/skill_range');
  hall.props.set('fc_guild_resident_slot', '0,0,0/skill_hall');
  class Form {
    title() { return this; } body() { return this; } button() { return this; } button1() { return this; } button2() { return this; }
    show() { forms.push(this); return { then: fn => { this.resolve = (selection, canceled = false) => fn({ selection, canceled });
      return { catch: fn => { this.reject = fn; } }; } }; }
  }
  for (const api of [training, hooks, activityApi, residentsApi, defenceApi]) Object.assign(context, Object.fromEntries(Object.keys(api).map(k => [k, api[k]])));
  Object.assign(context, { world, system, TICKS: () => system.currentTick, OW: () => dimension,
    guildBounds: () => ({ base: { x: 0, y: 0, z: 0 }, minX: 0, maxX: 122, minZ: 0, maxZ: 108 }),
    isInsideGuild: (_, id) => id === dimension.id, ActionFormData: Form, MessageFormData: Form,
    msg: key => key, displayName: id => id, morality: () => 0,
    addMorality: (p, value) => operations.push(['morality', p.id, value]),
    npcTalk: (p, npc) => operations.push(['dialogue', p.id, npc.id]),
    getBounties: p => p.warrant ? { active: { town: 'guild', amount: 5 } } : {}, GUILD_TOWN_KEY: 'guild', nowMs: () => 0 });
  vm.runInContext(declarations(['GUILD', 'GUILD_RESIDENT_SLOTS', 'APPRENTICE_TYPES', 'P', 'inv', 'countItem', 'removeItem',
    'LOVE_HEART', 'PET_NAMES', 'HELD_GIFTS', 'GIFT_COOLDOWN_TICKS', 'RELATIONSHIP_DISTANCE', 'RELATIONSHIP_FORM_TICKS',
    'RELATIONSHIP_FORM_LIMIT', 'relationshipForms', 'readRelationship', 'relationshipResponse', 'invalidateRelationshipForms',
    'applyRelationshipWrites', 'relationshipRingMatches', 'findRelationshipRing', 'isRomanceable', 'npcLove', 'setNpcLove',
    'isMarried', 'isMySpouse', 'npcName', 'marryNpc', 'proposeMenu', 'offerGift', 'bestGiftInBag', 'divorceConfirm', 'spouseMenu',
    'guildTraining', 'interruptGuildTraining', 'guildResidentCandidates', 'guildResidents', 'guildActivity',
    'guildDefenders', 'hasGuildWarrant', 'guildDefence', 'boastGatherCrowd']), context);
  const runtime = vm.runInContext('({training:guildTraining,activity:guildActivity,residents:guildResidents,defence:guildDefence,slots:GUILD_RESIDENT_SLOTS,spouse:spouseMenu,boast:boastGatherCrowd})', context);
  training.bindGuildTrainingReactions(runtime.training); hooks.bindGuildActivity(runtime.activity, runtime.training); defenceApi.bindGuildDefence(runtime.defence);
  const roster = { schema: 1, origin: 'legacy', base: { x: 0, y: 0, z: 0 }, residents: runtime.slots.map(slot =>
    ['skill_range', 'skill_hall'].includes(slot.id) ? { slot: slot.id, type: slot.type, status: 'bound',
      entityId: slot.id === 'skill_range' ? range.id : hall.id, provenance: 'marker' } : { slot: slot.id, type: slot.type, status: 'unknown' }) };
  properties.set(residentsApi.GUILD_RESIDENTS_KEY, JSON.stringify(roster));
  runtime.activity.reconcile([range, hall]);
  const interactionNode = ast.body.find(n => n.type === 'ExpressionStatement' && n.expression.type === 'CallExpression'
    && main.slice(...n.range).startsWith('world.beforeEvents.playerInteractWithEntity.subscribe('));
  assert.ok(interactionNode);
  runtime.interact = vm.runInContext(`(${main.slice(...interactionNode.expression.arguments[0].range)})`, context);
  function advance(tick, reconcile = false) {
    system.currentTick = tick;
    if (reconcile) runtime.activity.reconcile([range, hall]);
    const due = timers.filter(timer => timer.at <= tick); due.forEach(timer => timers.splice(timers.indexOf(timer), 1)); due.forEach(timer => timer.fn());
  }
  function request(entity, player, mode = 'follow', options) {
    const accepted = hooks.requestNpcActivity(entity, player, mode, options); assert.equal(accepted.accepted, true, JSON.stringify(accepted));
    advance(system.currentTick + 1, true); assert.equal(runtime.activity.status(entity).mode, mode);
    assert.equal(runtime.activity.status(entity).blocked, false); return accepted;
  }
  function emote(player, id) { return emotes.performFableEmote(player, id, { bypassUnlock: true, success: true, camera: false }); }
  return { context, operations, timers, actors, forms, properties, system, world, dimension, runtime, hooks, training, defenceApi,
    activityApi, emotes, a, b, range, hall, might, advance, request, emote };
}
const events = (f, e) => f.operations.filter(op => op[0] === 'event' && op[1] === e.id).map(op => op[2]);
const animations = (f, e) => f.operations.filter(op => op[0] === 'animation' && op[1] === e.id).map(op => op[2]);

test('actual functional Wait changes only its requester-owned follower and preserves the other Hero and unrelated trainee', async () => {
  const f = await fixture(); f.request(f.range, f.a); f.request(f.hall, f.b);
  f.runtime.training.beginPass([f.might]); const token = f.runtime.training.acquire(f.might, 'fc_train_ring_a', f.might.location, f.range.location);
  assert.notEqual(token, null); const other = plain(f.runtime.activity.status(f.hall));
  f.operations.length = 0; f.emote(f.a, 'wait'); f.advance(f.system.currentTick + 1, true);
  assert.equal(f.runtime.activity.status(f.range).mode, 'wait');
  assert.deepEqual(plain(f.runtime.activity.status(f.hall)), other);
  assert.equal(f.runtime.training.isActive(f.might, token), true);
  assert.equal(events(f, f.hall).length, 0); assert.equal(events(f, f.might).length, 0);
  assert.ok(events(f, f.range).includes('fc:guild_activity_wait'));
  assert.ok(!events(f, f.range).includes('fc:react_follow'));
  assert.equal(f.b.hasTag('fc_skill_hall_requester_v1'), true);
  assert.equal(f.a.hasTag('fc_skill_range_requester_v1'), false);
});

test('actual high-love implicit Follow carries the acting Hero through hooks and refuses takeover', async () => {
  const f = await fixture(); f.hall.location.x += 100; f.might.location.x += 100;
  f.range.sync.set('fc:love_hate', 60); f.emote(f.a, 'flirt'); f.advance(f.system.currentTick + 1, true);
  assert.equal(f.runtime.activity.status(f.range).ownerId, f.a.id);
  assert.equal(f.a.hasTag('fc_skill_range_requester_v1'), true);
  assert.ok(events(f, f.range).includes('fc:guild_activity_follow_range'));
  assert.ok(!events(f, f.range).includes('fc:react_follow'));
  const prior = plain(f.runtime.activity.status(f.range)); f.emote(f.b, 'follow'); f.advance(f.system.currentTick + 1, true);
  assert.deepEqual(plain(f.runtime.activity.status(f.range)), prior); assert.equal(f.b.hasTag('fc_skill_range_requester_v1'), false);
});

test('functional Wait on idle admirers cannot manufacture Follow or interrupt unrelated training', async () => {
  const f = await fixture(); f.range.sync.set('fc:love_hate', 90); f.hall.sync.set('fc:love_hate', 90);
  f.runtime.training.beginPass([f.might]); const token = f.runtime.training.acquire(f.might, 'fc_train_ring_a', f.might.location, f.range.location);
  f.operations.length = 0; f.emote(f.a, 'wait');
  assert.equal(f.runtime.activity.status(f.range).mode, 'idle'); assert.equal(f.runtime.activity.status(f.hall).mode, 'idle');
  assert.equal(f.runtime.training.isActive(f.might, token), true);
  assert.equal(f.operations.filter(op => op[0] === 'event').length, 0);
});

test('delayed fear and idle reactions cannot replace newer Follow, Wait, training or defence', async () => {
  for (const next of ['follow', 'wait', 'training', 'defence']) {
    const f = await fixture(); f.hall.location.x += 100; f.might.location.x += 100;
    f.range.sync.set('fc:fear_funny', 60); f.emote(f.a, 'blood_lust_roar');
    assert.ok(animations(f, f.range).includes('animation.npc.cower'));
    if (next === 'follow' || next === 'wait') { f.request(f.range, f.a); if (next === 'wait') f.request(f.range, f.a, 'wait'); }
    if (next === 'training') {
      // The social reaction interrupted this cycle; a new real session supersedes its old callbacks.
      f.system.currentTick = 3600; f.runtime.training.beginPass([f.range]);
      assert.notEqual(f.runtime.training.acquire(f.range, 'fc_train_range', f.range.location, { x: 83.5, y: 2.45, z: 34.5 }), null);
    }
    if (next === 'defence') f.defenceApi.provokeGuildDefence(f.range, f.b);
    const beforeEvents = events(f, f.range).length, beforeAnimations = animations(f, f.range).length;
    f.advance(Math.max(f.system.currentTick + 60, 100));
    assert.equal(events(f, f.range).length, beforeEvents, next);
    assert.equal(animations(f, f.range).length, beforeAnimations, next);
    assert.ok(!events(f, f.range).includes('fc:react_flee'), next);
  }
});

test('same-generation fear callback still executes when no activity supersedes it', async () => {
  const f = await fixture(); f.hall.location.x += 100; f.might.location.x += 100;
  f.range.sync.set('fc:fear_funny', 60); f.emote(f.a, 'blood_lust_roar'); f.advance(35);
  assert.ok(events(f, f.range).includes('fc:react_flee'));
});

test('actual spouse menu rejects an old activity revision and accepts a fresh owner Wait', async () => {
  const f = await fixture(); f.range.sync.set('fc:married', 1); f.range.sync.set('fc:love_hate', 80);
  f.range.props.set('fc_spouse_player', f.a.id); f.a.props.set('fc_spouses', JSON.stringify([f.range.id]));
  f.runtime.spouse(f.a, f.range); assert.equal(f.forms.length, 1);
  f.request(f.range, f.a); const revision = f.runtime.activity.status(f.range).revision;
  f.forms[0].resolve(2); assert.equal(f.runtime.activity.status(f.range).revision, revision);
  assert.equal(f.runtime.activity.status(f.range).mode, 'follow');
  f.runtime.spouse(f.a, f.range); f.forms[1].resolve(2); f.advance(f.system.currentTick + 1, true);
  assert.equal(f.runtime.activity.status(f.range).mode, 'wait'); assert.equal(f.runtime.activity.status(f.range).ownerId, f.a.id);
  const forms = f.forms.length; f.runtime.spouse(f.b, f.range); assert.equal(f.forms.length, forms);
});

test('queued interactions reject departed or changed actors before touching training and preserve another Hero activity', async () => {
  for (const departed of ['distance', 'dimension', 'invalid', 'target_dimension']) {
    const f = await fixture(); f.system.currentTick = 3600; f.runtime.training.beginPass([f.range]);
    const token = f.runtime.training.acquire(f.range, 'fc_train_range', f.range.location, { x: 83.5, y: 2.45, z: 34.5 });
    assert.notEqual(token, null); f.runtime.interact({ player: f.a, target: f.range, cancel: false });
    if (departed === 'distance') f.a.location.x += 100;
    if (departed === 'dimension') f.a.dimension = { ...f.dimension, id: 'minecraft:nether' };
    if (departed === 'target_dimension') f.range.dimension = { ...f.dimension, id: 'minecraft:nether' };
    if (departed === 'invalid') f.a.isValid = false;
    f.operations.length = 0; f.advance(f.system.currentTick + 1);
    assert.equal(f.operations.filter(op => ['event', 'dialogue', 'animation'].includes(op[0])).length, 0, departed);
    if (departed !== 'target_dimension') assert.equal(f.runtime.training.isActive(f.range, token), true, departed);
  }
  const f = await fixture(); f.request(f.range, f.a); const prior = plain(f.runtime.activity.status(f.range));
  f.runtime.interact({ player: f.b, target: f.range, cancel: false }); f.advance(f.system.currentTick + 1);
  assert.deepEqual(plain(f.runtime.activity.status(f.range)), prior);
});

test('actual boasting excludes owned Wait and actual defence preempts it before combat without reviving Follow', async () => {
  const f = await fixture(); f.request(f.range, f.a); f.request(f.range, f.a, 'wait');
  f.a.props.set('fc_renown', 500); f.operations.length = 0; f.runtime.boast(f.a, { x: 0, y: 0, z: 0 });
  assert.equal(f.operations.filter(op => op[0] === 'teleport' && op[1] === f.range.id).length, 0);
  assert.equal(f.runtime.activity.status(f.range).mode, 'wait');
  f.operations.length = 0; f.defenceApi.provokeGuildDefence(f.range, f.b);
  const sequence = events(f, f.range), start = sequence.indexOf('fc:guild_defence_start');
  assert.ok(start >= 0); assert.ok(sequence.slice(0, start).includes('fc:guild_activity_stop'));
  assert.equal(f.range.hasTag('fc_guild_defending'), true);
  assert.equal(f.a.hasTag('fc_skill_range_requester_v1'), false);
  assert.equal(f.range.hasTag('fc_guild_activity_wait_v1'), false);
  f.advance(f.system.currentTick + 321); f.runtime.defence.reconcile(); f.runtime.activity.reconcile([f.range, f.hall]);
  assert.equal(f.runtime.activity.status(f.range).mode, 'idle');
  assert.equal(f.range.hasTag('fc_guild_following'), false);
});


test('spouse activity callbacks cannot mutate movement after departure, invalidation or changed ownership', async () => {
  for (const cause of ['distance', 'dimension', 'invalid', 'owner']) for (const choice of [1, 2]) {
    const f = await fixture(); f.range.sync.set('fc:married', 1); f.range.sync.set('fc:love_hate', 80);
    f.range.props.set('fc_spouse_player', f.a.id); f.a.props.set('fc_spouses', JSON.stringify([f.range.id]));
    f.runtime.spouse(f.a, f.range); const before = plain(f.runtime.activity.status(f.range));
    if (cause === 'distance') f.a.location.x += 100;
    if (cause === 'dimension') f.a.dimension = { ...f.dimension, id: 'minecraft:nether' };
    if (cause === 'invalid') f.a.isValid = false;
    if (cause === 'owner') f.range.props.set('fc_spouse_player', f.b.id);
    f.operations.length = 0; f.forms[0].resolve(choice);
    assert.deepEqual(plain(f.runtime.activity.status(f.range)), before, `${cause}/${choice}`);
    assert.equal(events(f, f.range).length, 0, `${cause}/${choice}`);
  }
});

if (baselineProbe) {
  nodeTest('GP18 actual Wait broadcasts neutral to two prior followers and an unrelated active trainee', async () => {
    const f = await fixture();
    f.hall.location.x += 100; f.might.location.x += 100;
    f.range.sync.set('fc:love_hate', 80); f.emote(f.a, 'follow');
    assert.ok(events(f, f.range).includes('fc:react_follow'));
    f.range.location.x += 100; f.hall.location.x -= 100;
    f.hall.sync.set('fc:love_hate', 80); f.emote(f.b, 'follow');
    assert.ok(events(f, f.hall).includes('fc:react_follow'));
    f.range.location.x -= 100; f.might.location.x -= 100;
    f.system.currentTick = 3600; f.runtime.training.beginPass([f.might]);
    const token = f.runtime.training.acquire(f.might, 'fc_train_ring_a', f.might.location, f.range.location);
    assert.notEqual(token, null); f.operations.length = 0; f.emote(f.a, 'wait');
    for (const npc of [f.range, f.hall, f.might]) assert.ok(events(f, npc).includes('fc:react_neutral'), npc.id);
    assert.equal(f.runtime.training.isActive(f.might, token), false);
    console.log(JSON.stringify({ baseline: 'GP18', observed_defect: 'Wait broadcast',
      neutral_targets: [f.range.id, f.hall.id, f.might.id], unrelated_training_interrupted: true }));
  });
  nodeTest('GP18 actual deferred fear overwrites a later Follow reaction', async () => {
    const f = await fixture(); f.hall.location.x += 100; f.might.location.x += 100;
    f.range.sync.set('fc:fear_funny', 60); f.emote(f.a, 'blood_lust_roar');
    f.range.sync.set('fc:fear_funny', 0); f.range.sync.set('fc:love_hate', 80); f.emote(f.a, 'follow');
    assert.ok(events(f, f.range).includes('fc:react_follow')); const before = events(f, f.range).length;
    f.advance(35); assert.ok(events(f, f.range).slice(before).includes('fc:react_flee'));
    console.log(JSON.stringify({ baseline: 'GP18', observed_defect: 'stale fear callback',
      newer_reaction: 'fc:react_follow', later_stale_event: 'fc:react_flee' }));
  });
}

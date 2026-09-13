import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import vm from 'node:vm';

const code = await readFile(process.argv[3], 'utf8');
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
const observations=[];
function observe(name,fn){const info=fn();observations.push({name,...info});console.log(JSON.stringify(observations.at(-1)));}
function open(f=fixture()){const p=f.player(),door=f.face();f.start(p,door);return{f,p,door};}
function resume(f,p){f.reload();f.leave(p);f.enter(p);f.step(250);}

for (const marker of ['allocated','placing','placed','seeding','seeded','ready']) for(const mode of ['before','after','drop','substitute']) observe(`journal_${marker}_${mode}`,()=>{
 const {f,p}=open();
 // Allocation happened in interact; reopen with fault before it for this case.
 if(marker==='allocated') {const old=f.state();old.room=null;f.properties.set(DOOR_STATE_KEY,JSON.stringify(old));f.reload();}
 let injected=false;
 f.flags.worldWrite=r=>{
  const stage=r?.room?.phase==='ready'?'ready':r?.room?.preparation?.phase??r?.room?.phase;
  if(stage===marker&&!injected){injected=true;return mode;}
 };
 if(marker==='allocated'){f.leave(p);f.enter(p);}
 f.step(180);
 assert.equal(injected,true,marker);
 const before={placements:f.places.length,seeds:f.seeds.length,phase:f.state()?.room?.phase,preparation:f.state()?.room?.preparation?.phase};
 resume(f,p);
 const after={placements:f.places.length,seeds:f.seeds.length,phase:f.state()?.room?.phase,preparation:f.state()?.room?.preparation?.phase};
 assert.ok(f.places.length<=1,'No duplicate placement');assert.ok(f.seeds.length<=4,'No duplicate seeds');
 return {before,after};
});

observe('history_replaced_during_first_seed_stops_later_effects',()=>{
 const {f}=open();let replacement;
 f.flags.afterSeed=(_effect,n)=>{
  if(n!==1)return;
  const r=f.state();r.room.visited=true;r.room.phase='ready';r.rewards.seeded=true;r.rewards.claimed=[true,true,true,true];
  replacement=JSON.stringify(r);f.properties.set(DOOR_STATE_KEY,replacement);
 };
 f.step(180);
 assert.equal(f.seeds.length,1,'New authority stops all remaining native item effects');
 assert.equal(f.properties.get(DOOR_STATE_KEY),replacement);
 return{seeds:f.seeds.length,historyPreserved:true,phase:f.state().room.phase,claimed:f.state().rewards.claimed};
});
observe('later_container_filled_during_first_seed_is_preserved',()=>{
 const {f}=open();
 f.flags.afterSeed=(_effect,n)=>{
  if(n!==1)return;
  f.rewardContainer(1).slots.set(0,new f.ItemStack('minecraft:diamond',64));
 };
 f.step(180);
 assert.equal(f.rewardContainer(1).getItem(0).typeId,'minecraft:diamond');
 assert.equal(f.rewardContainer(1).getItem(0).amount,64);
 assert.equal(f.state().room.phase,'placing');
 assert.equal(f.seeds.length,1);
 f.reload();f.step(100);assert.equal(f.seeds.length,1,'No replay after reload');
 return{phase:f.state().room.phase,seeds:f.seeds.length,preservedForeignStack:f.rewardContainer(1).getItem(0).typeId};
});
observe('late_survey_edit_preserved',()=>{
 const {f}=open();f.step();const at=add(realmOrigin(0),{x:10,y:1,z:0});
 f.blocks.set(key(at),f.block('minecraft:diamond_block'));f.step(180);
 assert.equal(f.places.length,0);assert.equal(f.dim.getBlock(at).typeId,'minecraft:diamond_block');
 return{placements:f.places.length,preservedType:f.dim.getBlock(at).typeId};
});
observe('late_scanned_shell_hole_refuses_seed_and_entry',()=>{
 const {f,p}=open();f.until(()=>f.places.length===1);f.step();
 const at=add(realmOrigin(0),{x:0,y:4,z:5});f.blocks.set(key(at),f.block('minecraft:air'));
 f.step(60);f.enter(p);assert.equal(f.seeds.length,0);assert.equal(p.moves.length,0);
 return{placements:f.places.length,seeds:f.seeds.length,moves:p.moves.length};
});
observe('cached_ready_shell_hole_refuses_entry_without_rebuild',()=>{
 const f=fixture(),p=f.player(),door=f.face();f.build(p,door);
 const moves=p.moves.length;f.blocks.set(key(add(realmOrigin(0),{x:0,y:4,z:5})),f.block('minecraft:air'));
 f.enter(p);assert.equal(f.pilot.occupiedRealm(p),false);assert.equal(p.moves.length,moves);assert.equal(f.places.length,1);
 return{placements:f.places.length,extraMoves:p.moves.length-moves};
});
observe('ambiguous_placement_after_effect_never_replays',()=>{
 const {f,p}=open();f.flags.afterPlace=()=>{throw Error('native ambiguous completed placement');};
 f.step(180);assert.equal(f.places.length,1);assert.equal(f.seeds.length,0);f.flags.afterPlace=null;
 resume(f,p);assert.equal(f.places.length,1);assert.equal(f.seeds.length,0);
 return{placements:f.places.length,seeds:f.seeds.length,preparation:f.state().room.preparation.phase};
});
observe('legacy_unmarked_placing_never_replays_or_seeds',()=>{
 const {f,p}=open();f.until(()=>f.places.length===1);const r=f.state();delete r.room.preparation;
 f.properties.set(DOOR_STATE_KEY,JSON.stringify(r));
 f.rewardContainer(0).slots.set(0,new f.ItemStack('minecraft:diamond',64));
 resume(f,p);assert.equal(f.places.length,1);assert.equal(f.seeds.length,0);assert.equal(f.rewardContainer(0).getItem(0).typeId,'minecraft:diamond');
 return{placements:f.places.length,seeds:f.seeds.length,preservedType:f.rewardContainer(0).getItem(0).typeId};
});
observe('partial_native_seed_after_effect_never_replays',()=>{
 const {f,p}=open();f.flags.seedFault=(_effect,n)=>n===2?'after':null;f.step(180);
 assert.equal(f.seeds.length,2);assert.equal(f.state().room.preparation.phase,'seeding');f.flags.seedFault=null;
 resume(f,p);assert.equal(f.seeds.length,2);assert.equal(f.places.length,1);assert.notEqual(f.state().room.phase,'ready');
 return{placements:f.places.length,seeds:f.seeds.length,phase:f.state().room.phase};
});
observe('unmarked_legacy_ready_depletion_and_paid_suppression_preserved',()=>{
 const f=fixture(),p=f.player(),door=f.face();f.build(p,door);f.enter(p);
 f.rewardContainer(0).slots.delete(0);f.step();f.pilot.requestReturn(p);
 const r=f.state();delete r.room.preparation;f.properties.set(DOOR_STATE_KEY,JSON.stringify(r));
 resume(f,p);assert.equal(f.places.length,1);assert.equal(f.rewardContainer(0).getItem(0),undefined);assert.equal(f.state().rewards.claimed[0],true);
 const g=fixture(),q=g.player(),paid=g.face({open:true,idx:7});g.build(q,paid,true);
 assert.equal(g.state().rewards.suppressed,true);assert.equal(g.seeds.length,0);
 return{placements:f.places.length,claimed:f.state().rewards.claimed,paidSuppressed:g.state().rewards.suppressed,paidSeeds:g.seeds.length};
});
observe('missing_native_bulk_authority_defers_without_effects',()=>{
 const {f}=open(fixture({bulk:'missing'}));f.step(200);assert.equal(f.places.length,0);assert.equal(f.seeds.length,0);
 return{placements:f.places.length,seeds:f.seeds.length};
});
console.log(`PASS ${observations.length} independent DP9 review observations`);

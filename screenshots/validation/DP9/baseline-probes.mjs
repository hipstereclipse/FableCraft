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
// These assert observed baseline defects, rather than the intended safe result.
// Only the actual owned production module runs; the fixture supplies native effects.
const findings = [];
function observe(name, fn) { const evidence = fn(); findings.push({name, ...evidence}); console.log(JSON.stringify(findings.at(-1))); }
function opened() {
  const f = fixture(), p = f.player(), door = f.face();
  f.pilot.registerGuild(f.source, door, {isNew:true});
  f.pilot.interact(p, door, 'minecraft:lantern');
  return {f,p,door};
}
function waitPlacement(f) { for(let i=0; i<160 && !f.places.length; i++) f.step(); assert.equal(f.places.length,1); }
function waitReady(f) { for(let i=0; i<60 && f.state().room.phase!=='ready'; i++) f.step(); assert.equal(f.state().room.phase,'ready',f.errors.join('\n')); }
function retry(f,p) { f.reload(); f.leave(p); f.enter(p); }

observe('late_preflight_foreign_block_is_overwritten', () => {
  const {f}=opened(); f.step(); // First 512 voxels were proven air.
  const at=add(realmOrigin(0),{x:10,y:1,z:0});
  f.blocks.set(key(at),f.block('minecraft:diamond_block'));
  waitPlacement(f); waitReady(f);
  assert.notEqual(f.dim.getBlock(at).typeId,'minecraft:diamond_block');
  return {phase:f.state().room.phase, cell:f.state().room.cell, placements:f.places.length, changedAt:at, resultingType:f.dim.getBlock(at).typeId};
});

observe('placing_retry_rebuilds_over_foreign_edit_after_partial_seed', () => {
  const {f,p}=opened(); waitPlacement(f);
  const c0=f.rewardContainer(0), c1=f.rewardContainer(1);
  c1.setItem=()=>{throw Error('native seed failure at second reward');};
  f.step(25);
  assert.equal(f.state().room.phase,'placing');
  assert.equal(c0.getItem(0).typeId,'fc:elixir_of_life');
  const at=add(realmOrigin(0),{x:10,y:20,z:10});
  f.blocks.set(key(at),f.block('minecraft:diamond_block'));
  retry(f,p); waitReady(f);
  assert.equal(f.places.length,2);
  assert.notEqual(f.dim.getBlock(at).typeId,'minecraft:diamond_block');
  return {phase:f.state().room.phase, placements:f.places.length, partialRewardBeforeReload:c0.getItem(0).typeId, resultingType:f.dim.getBlock(at).typeId};
});

observe('late_nonsentinel_shell_hole_admits', () => {
  const {f,p}=opened(); waitPlacement(f); f.step();
  const at=add(realmOrigin(0),{x:0,y:4,z:5});
  f.blocks.set(key(at),f.block('minecraft:air')); // Already read in first 512 shell points.
  waitReady(f); f.enter(p);
  assert.equal(f.pilot.occupiedRealm(p),true);
  return {phase:f.state().room.phase, shellType:f.dim.getBlock(at).typeId, entered:f.pilot.occupiedRealm(p), placements:f.places.length};
});

for(const mode of ['ignore','wrong_type','wrong_count','wrong_name','wrong_lore','extra_slot']) observe(`unchecked_seed_${mode}_commits_ready`, () => {
  const {f}=opened(); waitPlacement(f);
  for(let i=0;i<4;i++) {
    const c=f.rewardContainer(i), native=c.setItem.bind(c);
    c.setItem=(slot,item)=>{
      if(mode==='ignore') return;
      if(mode==='wrong_type') item={...item,typeId:'minecraft:diamond'};
      if(mode==='wrong_count') item={...item,amount:2};
      if(mode==='wrong_name' && i>0) item={...item,nameTag:'Wrong keepsake'};
      if(mode==='wrong_lore' && i>0) item={...item,lore:['Wrong provenance']};
      native(slot,item);
      if(mode==='extra_slot') native(8,{typeId:'minecraft:diamond',amount:64});
    };
  }
  waitReady(f);
  const state=f.state(); assert.equal(state.rewards.seeded,true);
  return {phase:state.room.phase, seeded:state.rewards.seeded, claimed:state.rewards.claimed,
    items:[0,1,2,3].map(i=>f.rewardContainer(i).getItem(0)??null),extraSlot:f.rewardContainer(0).getItem(8)??null};
});

observe('late_prefilled_container_contents_are_overwritten', () => {
  const {f}=opened(); waitPlacement(f);
  f.rewardContainer(0).setItem(0,{typeId:'minecraft:diamond',amount:64});
  f.rewardContainer(1).setItem(8,{typeId:'minecraft:emerald',amount:64});
  waitReady(f);
  assert.equal(f.rewardContainer(0).getItem(0).typeId,'fc:elixir_of_life');
  assert.equal(f.rewardContainer(1).getItem(8).typeId,'minecraft:emerald');
  return {phase:f.state().room.phase, overwrittenSlot:f.rewardContainer(0).getItem(0).typeId, unexpectedExtraSlot:f.rewardContainer(1).getItem(8).typeId};
});

observe('late_player_occupancy_does_not_block_seeding', () => {
  const {f,p}=opened(); waitPlacement(f);
  p.location=add(realmOrigin(0),ARCANUM.arrival);
  waitReady(f);
  assert.equal(f.rewardContainer(0).getItem(0).typeId,'fc:elixir_of_life');
  return {phase:f.state().room.phase, playerAlreadyInside:true, seeded:f.state().rewards.seeded};
});

observe('control_ready_depletion_and_paid_history_remain_preserved', () => {
  const f=fixture(),p=f.player(),door=f.face(); f.build(p,door); f.enter(p);
  f.rewardContainer(0).setItem(0,undefined); f.step(); f.pilot.requestReturn(p); retry(f,p);
  for(let i=0;i<40;i++) f.step();
  assert.equal(f.places.length,1); assert.equal(f.rewardContainer(0).getItem(0),undefined);
  assert.equal(f.state().rewards.claimed[0],true);
  const g=fixture(), q=g.player(), paid=g.face({open:true,idx:7});g.build(q,paid,true);
  assert.equal(g.state().rewards.suppressed,true);
  for(let i=0;i<4;i++) assert.equal(g.rewardContainer(i).getItem(0),undefined);
  return {depletedReadyPlacements:f.places.length, claimed:f.state().rewards.claimed, paidSuppressed:g.state().rewards.suppressed};
});
console.log(`Observed ${findings.length-1} baseline defect probes and 1 preserved-history control.`);

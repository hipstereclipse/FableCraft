// Production registry + actual population, maintenance and lifecycle callbacks.
// No Bedrock engine persistence, navigation or native collision claims.
// node --experimental-vm-modules scripts/tests/guild_residents.test.mjs
import { test } from 'node:test';
import assert from 'node:assert/strict';
import vm from 'node:vm';
import { readFile } from 'node:fs/promises';
import { execFile } from 'node:child_process';
import { promisify } from 'node:util';
import { parse } from 'espree';

const source = await readFile('packs/Fablecraft_BP/scripts/guild_residents.js', 'utf8');
const main = await readFile('packs/Fablecraft_BP/scripts/main.js', 'utf8');
const ast = parse(main, {ecmaVersion:'latest',sourceType:'module',range:true});
const declaration = name => {
  const n = ast.body.find(n => n.type === 'FunctionDeclaration' && n.id.name === name
    || n.type === 'VariableDeclaration' && n.declarations.some(d => d.id.name === name));
  assert.ok(n, `Production declaration ${name}`); return main.slice(...n.range);
};
const base = {x:0,y:0,z:0};
const constants = vm.createContext({});
vm.runInContext(declaration('GUILD') + '\n' + declaration('GUILD_RESIDENT_SLOTS'), constants);
const slots = JSON.parse(vm.runInContext('JSON.stringify(GUILD_RESIDENT_SLOTS)', constants));

async function fixture(saved) {
  const context = vm.createContext({});
  const mod = new vm.SourceTextModule(source, {context});
  await mod.link(() => { throw Error('Registry must not import Bedrock'); }); await mod.evaluate();
  const api = mod.namespace;
  let stored = saved, serial = 0, writes = 0;
  const entities = [], spawned = [], calls = [], errors = new Map();
  const fail = key => { const n = errors.get(key) || 0; if (n) {errors.set(key,n-1);throw Error(`Injected ${key}`);} };
  const dimension = {
    id:'minecraft:overworld',
    getEntities(q) {fail('scan'); return entities.filter(e => e.isValid && e.dimension === this
      && (!q.type || e.typeId === q.type) && (!q.tags || q.tags.every(t => e.hasTag(t)))
      && (!q.location || Math.hypot(e.location.x-q.location.x,e.location.y-q.location.y,e.location.z-q.location.z) <= q.maxDistance));},
    getBlock(p) {fail('block');return {typeId:p.y===0?'minecraft:red_wool':'minecraft:air',isAir:p.y!==0};},
  };
  function entity(type='fc:guild_apprentice_will', location={x:26.5,y:1,z:24.5}) {
    const e = {id:`resident-${++serial}`,typeId:type,isValid:true,dimension,location:{...location},tags:new Set(),props:new Map(),
      nameTag:'Original name',social:{love:52,married:1},groups:new Set(['fc:reaction_follow']),
      getDynamicProperty(k){fail(`entity-read:${this.id}`);return this.props.get(k);},
      setDynamicProperty(k,v){fail(`entity-write:${this.id}`);this.props.set(k,v);},
      hasTag(k){return this.tags.has(k);},addTag(k){fail(`tag:${this.id}`);this.tags.add(k);},
      triggerEvent(){throw Error('Identity must not alter behavior');},teleport(){throw Error('Identity must not teleport');},
      tryTeleport(){throw Error('Identity must not teleport');},remove(){throw Error('Identity must not delete');},
    };
    entities.push(e); return e;
  }
  const options = {
    slots,
    read:()=>{fail('read');return stored;},
    write:value=>{writes++;calls.push({kind:'write',state:JSON.parse(value)});fail(`write:${writes}`);fail('write');stored=value;},
    lookup:id=>{fail('lookup');return entities.find(e => e.id===id && e.isValid);},
    candidates:()=>{fail('scan');return entities.filter(e=>e.isValid);},
    spawnPoint:(s,b)=>{fail('point');return errors.has(`blocked:${s.id}`)?undefined:{x:b.x+s.home.x+.5,y:b.y+(s.home.y??1),z:b.z+s.home.z+.5};},
    spawn:(s,p)=>{spawned.push(s.id);calls.push({kind:'spawn',slot:s.id,state:JSON.parse(stored)});fail(`spawn:${s.id}`);return entity(s.type,p);},
    onCampus:e=>e.dimension.id==='minecraft:overworld' && e.location.x>=0 && e.location.x<=122 && e.location.z>=0 && e.location.z<=108,
  };
  const ctl = api.createGuildResidentsController(options);
  return {api,ctl,options,entity,entities,dimension,spawned,calls,errors,
    read:()=>stored,writes:()=>writes,state:()=>JSON.parse(stored),
    fresh:()=>ctl.initialize(base,true),pass:(spawn=true)=>ctl.reconcile(base,spawn),
    restart:()=>api.createGuildResidentsController(options),
  };
}

test('fresh 12-slot population persists intent before each single birth and survives reload',async()=>{
  const f=await fixture();assert.equal(slots.length,12);assert.equal(new Set(slots.map(s=>s.id)).size,12);
  assert.equal(f.fresh(),true);f.pass();assert.equal(f.spawned.length,12);
  for(const c of f.calls.filter(c=>c.kind==='spawn')) assert.equal(c.state.residents.find(r=>r.slot===c.slot).status,'spawning');
  assert.equal(new Set(f.state().residents.map(r=>r.entityId)).size,12);
  f.pass();f.pass();const again=f.restart();again.reconcile(base,true);assert.equal(f.spawned.length,12);
  assert.ok(f.entities.every(e=>e.hasTag('fc_guild_npc')));
  assert.equal(f.entities.filter(e=>e.hasTag('fc_guild_guard')).length,2);
});

test('two-player departure, dimension change, unavailable lookup and return retain exact resident IDs',async()=>{
  const f=await fixture();f.fresh();f.pass();const original=f.read(),e=f.entities.find(e=>e.typeId==='fc:guild_apprentice_will');
  e.location={x:400,y:70,z:400};e.dimension={id:'minecraft:nether'};f.pass();
  e.isValid=false;f.ctl.removed(e.id);f.errors.set('lookup',24);f.pass();f.pass();
  assert.equal(f.read(),original);assert.equal(f.spawned.length,12);
  e.isValid=true;e.dimension=f.dimension;e.location={x:26,y:1,z:24};f.ctl.observe(e);f.pass();
  assert.equal(f.read(),original);assert.equal(f.spawned.length,12);
});

test('loaded ID outside every candidate scan still restores only identity metadata',async()=>{
  const f=await fixture();f.fresh();f.pass();const e=f.entities[0];e.tags.clear();e.props.clear();
  const ctl=f.api.createGuildResidentsController({...f.options,candidates:()=>[]});
  ctl.reconcile(base,false);assert.equal(e.hasTag('fc_guild_npc'),true);assert.equal(f.spawned.length,12);
});

test('confirmed death leaves a durable tombstone, including failed save and a late removal',async()=>{
  const f=await fixture();f.fresh();f.pass();const e=f.entities[0];e.isValid=false;
  f.errors.set('write',1);assert.equal(f.ctl.recordDeath(e),true);f.ctl.removed(e.id);f.pass();
  assert.equal(f.state().residents[0].status,'dead');assert.equal(f.state().residents[0].entityId,e.id);
  f.restart().reconcile(base,true);assert.equal(f.spawned.length,12);
  assert.equal(f.ctl.recordDeath({id:'foreign'}),false);
});

test('legacy empty or partially observed worlds never synthesize missing historical residents',async()=>{
  const f=await fixture();f.pass();assert.ok(f.state().residents.every(r=>r.status==='unknown'));
  const one=f.entity();f.pass();assert.equal(f.state().residents.filter(r=>r.status==='bound').length,1);
  assert.equal(f.spawned.length,0);one.isValid=false;f.pass();assert.equal(f.spawned.length,0);
});

test('foreign generic trader and town guard cannot suppress or occupy a fresh or legacy slot',async()=>{
  for(const fresh of [true,false]) {
    const f=await fixture();const trader=f.entity('fc:trader'),guard=f.entity('fc:guard_bowerstone');
    if(fresh)f.fresh();f.pass();
    assert.equal(trader.props.size,0);assert.equal(guard.tags.size,0);
    assert.ok(f.state().residents.every(r=>![trader.id,guard.id].includes(r.entityId)));
    assert.equal(f.spawned.length,fresh?12:0);
  }
});

test('legacy Guild tags enroll departed generic spouses without touching relationship or Follow state',async()=>{
  const f=await fixture();const e=f.entity('fc:trader',{x:400,y:80,z:400});e.dimension={id:'minecraft:nether'};
  e.tags.add('fc_guild_npc');e.tags.add('fc_guild_following');e.props.set('fc_spouse_player','hero-a');e.props.set('fc_gift_cd',77);
  const before={name:e.nameTag,social:{...e.social},groups:[...e.groups],location:{...e.location}};
  f.pass();const r=f.state().residents.find(r=>r.type==='fc:trader');assert.equal(r.entityId,e.id);assert.equal(r.provenance,'legacy-tag');
  assert.deepEqual({name:e.nameTag,social:e.social,groups:[...e.groups],location:e.location},before);
  assert.equal(e.props.get('fc_spouse_player'),'hero-a');assert.equal(e.props.get('fc_gift_cd'),77);assert.equal(e.hasTag('fc_guild_following'),true);
  assert.equal(f.spawned.length,0);
});

test('unique unmarked named/apprentice campus candidates migrate; excess cohorts remain untouched',async()=>{
  const f=await fixture();const maze=f.entity('fc:maze'),a=f.entity(),b=f.entity(),c=f.entity();f.pass();
  assert.equal(f.state().residents.find(r=>r.type==='fc:maze').entityId,maze.id);
  assert.equal(f.state().residents.find(r=>r.type==='fc:maze').provenance,'legacy-inferred');
  assert.ok(f.state().residents.filter(r=>r.type===a.typeId).every(r=>r.status==='unknown'));
  assert.ok([a,b,c].every(e=>e.tags.size===0&&e.props.size===0));assert.equal(f.spawned.length,0);
});

test('definitive slot markers take precedence and duplicate claims never remove or reassign an entity',async()=>{
  const f=await fixture();f.ctl.initialize(base);const slot=slots.find(s=>s.type==='fc:maze'),e=f.entity(slot.type),extra=f.entity(slot.type);
  e.props.set(f.api.GUILD_RESIDENT_SLOT,`0,0,0/${slot.id}`);f.pass();
  assert.equal(f.state().residents.find(r=>r.slot===slot.id).entityId,e.id);assert.equal(extra.props.size,0);
  extra.props.set(f.api.GUILD_RESIDENT_SLOT,`0,0,0/${slot.id}`);f.pass();
  assert.equal(f.state().residents.find(r=>r.slot===slot.id).entityId,e.id);
  const g=await fixture();g.ctl.initialize(base);for(let i=0;i<2;i++)g.entity(slot.type).props.set(g.api.GUILD_RESIDENT_SLOT,`0,0,0/${slot.id}`);
  g.pass();assert.equal(g.state().residents.find(r=>r.slot===slot.id).status,'conflict');assert.equal(g.spawned.length,0);
});

test('fresh duplicate slot claims persist a conflict and never create a third resident after reload',async()=>{
  const f=await fixture();f.fresh();const slot=slots[0];
  const existing=[f.entity(slot.type),f.entity(slot.type)];
  for(const e of existing)e.props.set(f.api.GUILD_RESIDENT_SLOT,`0,0,0/${slot.id}`);
  f.pass();f.pass();assert.equal(f.state().residents[0].status,'conflict');
  for(const e of existing)e.isValid=false;
  f.restart().reconcile(base,true);assert.equal(f.spawned.filter(id=>id===slot.id).length,0);
  assert.equal(f.state().residents[0].status,'conflict');
  existing[0].isValid=true;f.restart().reconcile(base,true);
  assert.equal(f.state().residents[0].entityId,existing[0].id);assert.equal(f.spawned.filter(id=>id===slot.id).length,0);
});

test('one entity cannot use inconsistent metadata to occupy a second fresh slot',async()=>{
  const f=await fixture();f.fresh();f.errors.set(`blocked:${slots[1].id}`,1);f.pass();
  const e=f.entities[0];e.props.set(f.api.GUILD_RESIDENT_SLOT,`0,0,0/${slots[1].id}`);
  f.errors.delete(`blocked:${slots[1].id}`);f.pass();f.restart().reconcile(base,true);
  assert.equal(f.state().residents[0].entityId,e.id);assert.equal(f.state().residents[1].status,'conflict');
  assert.equal(f.spawned.filter(id=>id===slots[1].id).length,0);
});

test('initialization and pre-spawn persistence failures perform no native spawn until saved',async()=>{
  const f=await fixture();f.errors.set('write',1);assert.equal(f.fresh(),false);assert.equal(f.spawned.length,0);
  f.errors.set(`write:${f.writes()+2}`,1);f.pass();assert.equal(f.spawned.length,0);
  f.pass();assert.equal(f.spawned.length,12);assert.equal(new Set(f.spawned).size,12);
});

test('native spawn exception or missing return handle permanently reserves its intent',async()=>{
  for(const missing of [false,true]) {
    const f=await fixture();const first=slots[0].id;f.fresh();
    let ctl=f.ctl;if(missing)ctl=f.api.createGuildResidentsController({...f.options,spawn:(s,p)=>{if(s.id!==first)return f.options.spawn(s,p);f.spawned.push(s.id);return undefined;}});
    else f.errors.set(`spawn:${first}`,1);
    ctl.reconcile(base,true);ctl.reconcile(base,true);f.restart().reconcile(base,true);
    assert.equal(f.spawned.filter(id=>id===first).length,1);assert.equal(f.state().residents[0].status,'spawning');
  }
});

test('a write that persists intent then throws cannot authorize a birth after reload',async()=>{
  const f=await fixture();let failed=false;
  const ctl=f.api.createGuildResidentsController({...f.options,write:value=>{
    f.options.write(value);
    if(!failed&&JSON.parse(value).residents[0].status==='spawning'){failed=true;throw Error('after persisted write');}
  }});
  ctl.initialize(base,true);ctl.reconcile(base,true);assert.equal(f.spawned.length,0);
  assert.equal(f.state().residents[0].status,'spawning');
  f.restart().reconcile(base,true);assert.equal(f.spawned.filter(id=>id===slots[0].id).length,0);
});

test('post-spawn marker and registry failures retain the original ID without another birth',async()=>{
  const f=await fixture();f.fresh();f.errors.set('entity-write:resident-1',1);f.errors.set('write:3',1);f.pass();
  assert.equal(f.spawned.length,1);assert.equal(f.state().residents[0].status,'spawning');
  f.pass();assert.equal(f.spawned.length,12);assert.equal(f.state().residents[0].entityId,f.entities[0].id);
  assert.equal(f.entities[0].hasTag('fc_guild_npc'),true);
});

test('reload after native birth recovers its marker or keeps an unmarked intent reserved',async()=>{
  for(const marked of [true,false]) {
    const f=await fixture();f.fresh();if(!marked)f.errors.set('entity-write:resident-1',1);f.errors.set('write:3',1);f.pass();
    const ctl=f.restart();ctl.reconcile(base,true);ctl.reconcile(base,true);
    assert.equal(f.spawned.filter(id=>id===slots[0].id).length,1);
    assert.equal(f.state().residents[0].status,marked?'bound':'spawning');
  }
});

test('identity-tag failure retries bookkeeping and never emits activity events',async()=>{
  const f=await fixture();f.fresh();f.errors.set('tag:resident-1',1);f.pass();f.pass();
  assert.equal(f.spawned.length,12);assert.equal(f.entities[0].hasTag('fc_guild_npc'),true);
  assert.deepEqual([...f.entities[0].groups],['fc:reaction_follow']);
});

test('corrupt registries, duplicate IDs, unsupported schema and base mismatch fail closed',async()=>{
  const good=await fixture();good.fresh();good.pass();const original=good.state();
  const badId=structuredClone(original);badId.residents[1].entityId=badId.residents[0].entityId;
  const badState=structuredClone(original);badState.residents[0].status='never';
  for(const raw of ['{',false,'null',JSON.stringify({...original,schema:2}),JSON.stringify(badId),JSON.stringify(badState)]) {
    const f=await fixture(raw);f.fresh();f.pass();assert.equal(f.spawned.length,0);assert.equal(f.writes(),0);
    assert.equal(f.ctl.snapshot().blocked,'invalid-registry');
  }
  const f=await fixture(JSON.stringify(original));f.ctl.reconcile({x:200,y:0,z:0},true);assert.equal(f.spawned.length,0);assert.equal(f.writes(),0);
  assert.equal(f.ctl.snapshot().blocked,'base-mismatch');
  f.pass();assert.equal(f.ctl.snapshot().blocked,undefined);assert.equal(f.spawned.length,0);
});

test('unloaded/blocked spawn preflight remains retryable before native spawn only',async()=>{
  const f=await fixture();f.fresh();for(const s of slots)f.errors.set(`blocked:${s.id}`,1);f.pass();
  assert.equal(f.spawned.length,0);assert.ok(f.state().residents.every(r=>r.status==='never'));
  for(const s of slots)f.errors.delete(`blocked:${s.id}`);f.pass();assert.equal(f.spawned.length,12);
  for(const s of slots)f.errors.set(`blocked:${s.id}`,1);f.pass();assert.equal(f.spawned.length,12);
});

test('generated Guild gives all 12 homes bounded supported birth centres covering emitted colliders',async()=>{
  const f=await fixture();
  const generated=JSON.parse((await promisify(execFile)('python',['-c',`
import json,sys
sys.path.insert(0,'scripts')
import gen_structures as g
v=g.build_guild_hall();cells={};colliders={}
for s in json.loads(sys.argv[1]):
 h=s['home']; y=h.get('y',1)
 for x in range(h['x']-2,h['x']+3):
  for z in range(h['z']-2,h['z']+3):
   for yy in range(y-1,y+3):cells[f'{x},{yy},{z}']=v.palette[v.grid[v.idx(x,yy,z)]][0]
 name=s['type'][3:]
 with open('packs/Fablecraft_BP/entities/'+name+'.json') as out:colliders[s['type']]=json.load(out)['minecraft:entity']['components']['minecraft:collision_box']
print(json.dumps({'cells':cells,'colliders':colliders}))
`,JSON.stringify(slots)],{encoding:'utf8'})).stdout);
  const dim={getBlock:p=>{const typeId=generated.cells[`${p.x},${p.y},${p.z}`];return typeId?{typeId,isAir:typeId==='minecraft:air'}:undefined;},getEntities:()=>[]};
  const births={};
  for(const s of slots) {
    const home={...s.home,y:s.home.y??1},p=f.api.guildResidentSpawnPoint(dim,home,s);assert.ok(p,s.id);births[s.id]={...p};
    assert.ok(Math.hypot(p.x-home.x-.5,p.z-home.z-.5)<=2,s.id);assert.equal(p.y,home.y);
    const size=generated.colliders[s.type];assert.ok(size.width<=.8);assert.ok(size.height<=(s.type==='fc:maze'?2.1:2));
  }
  assert.deepEqual(births.maze,{x:46.5,y:12,z:70.5});assert.deepEqual(births.guildmaster,{x:22.5,y:1,z:41.5});
  assert.deepEqual(births.guard_north,{x:11.5,y:1,z:39.5});assert.deepEqual(births.guard_south,{x:11.5,y:1,z:45.5});
  assert.deepEqual(births.skill_hall,{x:41.5,y:1,z:40.5});
  console.log('Offline generated-voxel resident birth centres:',JSON.stringify(births));
  const sequential={};
  dim.getEntities=q=>Object.values(sequential).filter(p=>Math.hypot(p.x-q.location.x,p.y-q.location.y,p.z-q.location.z)<=q.maxDistance);
  for(const s of slots) {
    const p=f.api.guildResidentSpawnPoint(dim,{...s.home,y:s.home.y??1},s);
    assert.ok(p,`Prior births leave a safe candidate for ${s.id}`);sequential[s.id]={...p};
  }
  assert.equal(Object.keys(sequential).length,12);
  assert.deepEqual(sequential.will_library,{x:25.5,y:1,z:25.5});
  console.log('Offline sequential occupied-voxel resident birth centres:',JSON.stringify(sequential));
});

test('production preflight refuses missing floors, unknown blocks, headroom, entities and failed scans',async()=>{
  const f=await fixture();const s=slots[0],home={x:20,y:1,z:30};
  for(const defect of ['floor','unknown','head','entity','unloaded','scan']) {
    const dim={getBlock:p=>{
      if(defect==='unloaded')throw Error('unloaded');
      const typeId=p.y===0?(defect==='floor'?'minecraft:air':defect==='unknown'?'minecraft:oak_slab':'minecraft:red_wool')
        :defect==='head'?'minecraft:stone_bricks':'minecraft:air';return {typeId,isAir:typeId==='minecraft:air'};
    },getEntities:()=>{if(defect==='scan')throw Error('query failed');return defect==='entity'?[{}]:[];}};
    assert.equal(f.api.guildResidentSpawnPoint(dim,home,s),undefined,defect);
  }
});

test('actual population enrollment precedes decoration; maintenance and death/load/remove callbacks preserve identity',async()=>{
  const f=await fixture();const props=new Map([['fc_guild_placed',true],['fc_guild_base',JSON.stringify(base)]]),listeners={},timers=[],heroes=[];
  let decorated=false,placements=0;
  const context=vm.createContext({...Object.fromEntries(Object.keys(f.api).map(k=>[k,f.api[k]])),
    world:{getDynamicProperty:k=>k===f.api.GUILD_RESIDENTS_KEY?f.read():props.get(k),
      setDynamicProperty:(k,v)=>{if(k===f.api.GUILD_RESIDENTS_KEY)f.options.write(v);else props.set(k,v);},
      getEntity:f.options.lookup,getPlayers:()=>heroes,afterEvents:Object.fromEntries(['entityDie','entityLoad','entityRemove'].map(k=>[k,{subscribe:fn=>listeners[k]=fn}])),
      structureManager:{place:()=>{placements++;assert.equal(f.state().origin,'fresh');assert.ok(f.state().residents.every(r=>r.status==='never'));}},},
    system:{runInterval:fn=>timers.push(fn),runTimeout:fn=>fn(),currentTick:10},OW:()=>f.dimension,
    guildBounds:()=>props.get('fc_guild_base')?{base:JSON.parse(props.get('fc_guild_base'))}:null,
    isInsideGuild:(p,id)=>id==='minecraft:overworld'&&p.x>=0&&p.x<=122,
    forceLoadGuild:()=>true,sampleGroundY:()=>66,OVERWORLD_SEA_LEVEL:63,showHeroTitle:()=>{},
    guildCaves:{enroll:()=>true,pendingBase:()=>undefined},ensureGuildDoorPilot:()=>{},
    registerCullis:()=>{decorated=true;throw Error('decoration unavailable');},
  });
  f.dimension.spawnEntity=(type,p)=>f.entity(type,p);
  vm.runInContext(['GUILD','GUILD_RESIDENT_SLOTS','guildResidentCandidates','guildResidents','maintainGuildResidents'].map(declaration).join('\n'),context);
  for(const prefix of ['world.afterEvents.entityDie.subscribe(','world.afterEvents.entityLoad.subscribe(','world.afterEvents.entityRemove.subscribe(']) {
    const node=ast.body.find(n=>n.type==='ExpressionStatement'&&main.slice(...n.range).startsWith(prefix)&&main.slice(...n.range).includes('guildResidents'));
    assert.ok(node,prefix);vm.runInContext(main.slice(...node.range),context);
  }
  const interval=ast.body.find(n=>n.type==='ExpressionStatement'&&main.slice(...n.range).startsWith('system.runInterval(')&&main.slice(...n.range).includes('maintainGuildResidents'));
  assert.ok(interval);vm.runInContext(main.slice(...interval.range),context);
  // Execute the production founding callback while unrelated decoration fails.
  props.delete('fc_guild_placed');props.delete('fc_guild_base');
  vm.runInContext(declaration('buildGuildWhenReady'),context);
  // A new Guild uses sampleGroundY()-1. Flat fixture follows that chosen base.
  f.dimension.getBlock=p=>({typeId:p.y===65?'minecraft:red_wool':'minecraft:air',isAir:p.y!==65});
  context.player={sendMessage(){},dimension:f.dimension};
  f.errors.set('write',1);vm.runInContext('buildGuildWhenReady(player, OW(), {x:0,z:0}, 600)',context);
  assert.equal(placements,0);assert.equal(f.entities.length,0);assert.equal(props.has('fc_guild_placed'),false);
  vm.runInContext('buildGuildWhenReady(player, OW(), {x:0,z:0}, 0)',context);
  assert.equal(placements,1);
  assert.equal(decorated,true);assert.equal(f.state().origin,'fresh');assert.ok(f.entities.length>0);
  assert.ok(f.state().residents.some(r=>r.status==='bound'));
  const born=f.entities[0],identity=f.state().residents.find(r=>r.entityId===born.id);assert.ok(identity);
  const initiallyBorn=f.entities.length;
  // An unavailable new Maze floor can retry once a Hero attends; a resident
  // following another Hero away is never included in a type-count shortfall.
  assert.equal(f.state().residents.find(r=>r.slot==='maze').status,'never');
  f.dimension.getBlock=p=>({typeId:[65,76].includes(p.y)?'minecraft:red_wool':'minecraft:air',isAir:![65,76].includes(p.y)});
  timers.forEach(fn=>fn());assert.equal(f.entities.length,initiallyBorn);
  born.location={x:400,y:66,z:400};heroes.push({location:born.location,dimension:f.dimension},{location:{x:25,y:66,z:30},dimension:f.dimension});
  timers.forEach(fn=>fn());assert.equal(f.entities.length,12);assert.equal(f.state().residents.find(r=>r.slot===identity.slot).entityId,born.id);
  born.isValid=false;listeners.entityRemove({removedEntityId:born.id});timers.forEach(fn=>fn());assert.equal(f.entities.length,12);
  born.isValid=true;born.location={x:20,y:66,z:40};listeners.entityLoad({entity:born});timers.forEach(fn=>fn());assert.equal(f.entities.length,12);
  // A nonplayer/environmental death must reach independent bookkeeping.
  listeners.entityDie({deadEntity:born,damageSource:{cause:'fall'}});
  assert.equal(f.state().residents.find(r=>r.entityId===born.id).status,'dead');
  assert.ok(timers.length>0);
});

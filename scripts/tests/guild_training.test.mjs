// Production session module + actual main/emote callbacks at mocked Bedrock boundaries.
// node --experimental-vm-modules scripts/tests/guild_training.test.mjs
import { test } from 'node:test';
import assert from 'node:assert/strict';
import vm from 'node:vm';
import { readFile } from 'node:fs/promises';
import { parse } from 'espree';

const moduleSource = await readFile('packs/Fablecraft_BP/scripts/guild_training.js', 'utf8');
const mainSource = await readFile('packs/Fablecraft_BP/scripts/main.js', 'utf8');
const emoteSource = await readFile('packs/Fablecraft_BP/scripts/fable_emotes.js', 'utf8');
const ast = parse(mainSource, { ecmaVersion: 'latest', sourceType: 'module', range: true });
const pointA = {x:99.5,y:1,z:61.5}, pointB = {x:102.5,y:1,z:61.5};
let serial = 0;

async function fixture() {
  const context = vm.createContext({ console });
  const module = new vm.SourceTextModule(moduleSource, { context });
  await module.link(() => { throw new Error('Session module must stay independent of engine imports'); });
  await module.evaluate();
  const api = module.namespace;
  let tick = 10, time = 1000;
  const entities = [], timers = [], particles = [], sounds = [], spawned = [], blocks = new Map();
  const blockReads = [], mutations = [];
  // The authored Skill bullseye and hay support; other props are explicit per test.
  blocks.set('83,2,34',{typeId:'minecraft:target',isAir:false});
  blocks.set('83,1,34',{typeId:'minecraft:hay_block',isAir:false});
  const dimension = {
    id: 'minecraft:overworld',
    getBlock(p) { const key = `${p.x},${p.y},${p.z}`; blockReads.push(key);
      const block=blocks.has(key)?blocks.get(key):{typeId:p.y===0?'minecraft:coarse_dirt':'minecraft:air',isAir:p.y>0};
      return block && {...block,setType:type=>mutations.push(['setType',key,type]),
        setPermutation:value=>mutations.push(['setPermutation',key,value])}; },
    getEntities(query) { return entities.filter(e=>e.isValid && (!query.type || e.typeId===query.type)
      && (!query.tags || query.tags.every(t=>e.tags.has(t))))
      .filter(e=>!query.location || Math.hypot(e.location.x-query.location.x,e.location.y-query.location.y,e.location.z-query.location.z)<=query.maxDistance); },
    spawnParticle(id,p,variables) { particles.push({id,p,variables}); },
    playSound(id,p) { sounds.push({id,p}); },
    spawnEntity(id,p) { spawned.push({id,p}); throw new Error('Practice must never spawn a projectile'); },
    spawnItem(...args) { mutations.push(['spawnItem',...args]); },
    runCommand(command) { mutations.push(['runCommand',command]); },
    setBlockType(...args) { mutations.push(['setBlockType',...args]); },
    setBlockPermutation(...args) { mutations.push(['setBlockPermutation',...args]); },
  };
  function entity(type='fc:guild_apprentice_might') {
    const e = {
      id:`trainee-${++serial}`, typeId:type, isValid:true, dimension, location:{x:12,y:1,z:42},
      tags:new Set(), events:[], placements:[], teleports:[], frozen:false, animations:[], errors:new Map(),
      getTags() { return [...this.tags]; }, hasTag(t) { return this.tags.has(t); },
      addTag(t) { this.throwIf('addTag'); this.tags.add(t); },
      removeTag(t) { this.throwIf('removeTag'); this.tags.delete(t); },
      throwIf(key) { const count=this.errors.get(key)||0; if (count) {this.errors.set(key,count-1);throw new Error(`Injected ${key}`);} },
      triggerEvent(event) {
        this.events.push(event);
        this.throwIf(event);
        if (event==='fc:guild_training_start') this.frozen=true;
        if (event==='fc:guild_training_stop') this.frozen=false;
        if (event.startsWith('fc:react_')) this.reaction=event;
      },
      tryTeleport(p,options) { this.placements.push({p,options});this.throwIf('tryTeleport');if(this.blocked) return false;this.location={...p};return true; },
      teleport(p) { this.teleports.push(p);this.location={...p}; },
      playAnimation(name) { this.animations.push(name); },
      applyDamage(...args) { mutations.push(['applyDamage',...args]); },
      setDynamicProperty(...args) { mutations.push(['setDynamicProperty',...args]); },
      addExperience(...args) { mutations.push(['addExperience',...args]); },
    };
    entities.push(e);return e;
  }
  function controller() {
    return api.createGuildTrainingController({now:()=>tick,session:()=>api.guildTrainingSession(tick,time),
      canTrain:e=>!e.hasTag('fc_aggravated')&&!e.hasTag('fc_guild_following')&&!e.married});
  }
  const ctl=controller();api.bindGuildTrainingReactions(ctl);
  function advance(value,newTime=time) { tick=value;time=newTime;if(context.system)context.system.currentTick=tick; }
  function runDue() { const due=timers.filter(t=>t.at<=tick);due.forEach(t=>timers.splice(timers.indexOf(t),1));due.forEach(t=>t.fn()); }
  function acquire(e,role='fc_train_ring_a',p=pointA) { return ctl.acquire(e,role,p,pointB); }
  function pair(a,b) { return ctl.acquirePair({entity:a,role:'fc_train_ring_a',point:pointA,facing:pointB},
    {entity:b,role:'fc_train_ring_b',point:pointB,facing:pointA}); }
  async function runtime() {
    const bindingNames = ['APPRENTICE_TYPES','GUILD','nextSparTick','nextArcheryTick','nextWillTick','sparTurn','guildTraining',
      'interruptGuildTraining','guildApprentices','localGuildPoint','distanceXZ','playSparExchange','showPracticeShot',
      'guildSkillLaneClear','guildWillLaneClear','showPracticeWill','playWillPractice','boastGatherCrowd'];
    const declarations=bindingNames.map(name=> {
      const node=ast.body.find(n=>n.type==='FunctionDeclaration'&&n.id.name===name || n.type==='VariableDeclaration'&&n.declarations.some(d=>d.id.name===name));
      assert.ok(node,`Production declaration ${name}`);return mainSource.slice(...node.range);
    });
    const dialogues=[];
    Object.assign(context,{
      ...Object.fromEntries(Object.keys(api).map(k=>[k,api[k]])),
      TICKS:()=>tick,OW:()=>dimension, world:{getTimeOfDay:()=>time,getDynamicProperty:()=>true},
      system:{currentTick:tick,runTimeout:(fn,delay)=>timers.push({fn,at:tick+delay}),run:fn=>fn()},
      guildBounds:()=>({base:{x:0,y:0,z:0}}),isMarried:e=>!!e.married,
      isInsideGuild:(loc,id)=>id==='minecraft:overworld',
      guildActivityReserved:()=>false,routeGuildActivityReaction:()=>false, // Activity arbitration has its own actual-controller integration suite.
      clearGuildRingScarecrows(){},repairGuildDemonApproach(){},repairGuildTerrain(){},repairGuildSkirtVegetation(){},
      placeGuildAnnexes(){}, // GP5's adjacent owner has its own actual-callback suite.
      isRomanceable:()=>false,npcTalk:(p,e)=>dialogues.push(e.id),P:{get:()=>500},
      MolangVariableMap:class {
        values={}; setFloat(key,value){this.values[key]=value;} setColorRGBA(key,value){this.values[key]=value;}
      },
    });
    vm.runInContext(declarations.join('\n'),context);
    vm.runInContext('bindGuildTrainingReactions(guildTraining)',context);
    const trainingNode=ast.body.find(n=>n.type==='ExpressionStatement'&&n.expression.type==='CallExpression'
      &&mainSource.slice(...n.range).startsWith('system.runInterval(')&&mainSource.slice(...n.range).includes('guildTraining.beginPass'));
    assert.ok(trainingNode,'Actual training interval');
    const training=vm.runInContext(`(${mainSource.slice(...trainingNode.expression.arguments[0].range)})`,context);
    const interactionNode=ast.body.find(n=>n.type==='ExpressionStatement'&&n.expression.type==='CallExpression'
      &&mainSource.slice(...n.range).startsWith('world.beforeEvents.playerInteractWithEntity.subscribe('));
    const interact=vm.runInContext(`(${mainSource.slice(...interactionNode.expression.arguments[0].range)})`,context);
    const emoteAst=parse(emoteSource,{ecmaVersion:'latest',sourceType:'module',range:true});
    const emoteNode=emoteAst.body.find(n=>n.type==='FunctionDeclaration'&&n.id.name==='triggerNpcEvent');
    context.audit=()=>{};vm.runInContext(emoteSource.slice(...emoteNode.range),context);
    return {training,interact,dialogues,...vm.runInContext('({controller:guildTraining,emote:triggerNpcEvent,shot:showPracticeShot,boast:boastGatherCrowd,will:showPracticeWill,lane:guildWillLaneClear})',context)};
  }
  return {api,context,ctl,controller,entity,entities,dimension,blocks,blockReads,mutations,particles,sounds,spawned,timers,advance,runDue,acquire,pair,runtime};
}

test('one checked station placement per active session; release does not teleport home',async()=>{
  const f=await fixture(),e=f.entity();f.ctl.beginPass([e]);const token=f.acquire(e);
  for(let tick=20;tick<=100;tick+=10){f.advance(tick);f.ctl.beginPass([e]);assert.equal(f.acquire(e),token);}
  assert.equal(e.placements.length,1);assert.equal(e.placements[0].options.checkForBlocks,true);
  assert.equal(e.frozen,true);f.advance(1200);f.ctl.beginPass([e]);
  assert.equal(e.frozen,false);assert.equal(e.tags.size,0);assert.equal(e.teleports.length,0);assert.equal(e.placements.length,1);
  f.advance(3600);f.ctl.beginPass([e]);assert.notEqual(f.acquire(e),null);assert.equal(e.placements.length,2);
});

test('failed stop keeps state pending and retries; successful cleanup does not repeat',async()=>{
  const f=await fixture(),e=f.entity();f.ctl.beginPass([e]);const token=f.acquire(e);
  e.errors.set('fc:guild_training_stop',1);f.ctl.interrupt(e);
  assert.equal(e.frozen,true);assert.equal(e.hasTag('fc_train_ring_a'),true);assert.equal(f.ctl.eligible(e),false);
  assert.equal(f.ctl.isActive(e,token),false);f.ctl.beginPass([e]);
  assert.equal(e.frozen,false);assert.equal(e.tags.size,0);
  const calls=e.events.length;f.ctl.beginPass([e]);assert.equal(e.events.length,calls);
});

test('failed start and tag writes clean up and cannot re-place during the same session',async()=>{
  for(const failure of ['fc:guild_training_start','addTag']){
    const f=await fixture(),e=f.entity();f.ctl.beginPass([e]);e.errors.set(failure,1);
    assert.equal(f.acquire(e),null);assert.equal(e.frozen,false);assert.equal(e.tags.size,0);
    f.ctl.beginPass([e]);assert.equal(f.acquire(e),null);assert.equal(e.placements.length,1);
    f.advance(3600);f.ctl.beginPass([e]);assert.notEqual(f.acquire(e),null);
  }
  const f=await fixture(),e=f.entity();f.ctl.beginPass([e]);f.acquire(e);e.errors.set('removeTag',1);f.ctl.interrupt(e);
  assert.equal(f.ctl.eligible(e),false);f.ctl.beginPass([e]);assert.equal(e.tags.size,0);assert.equal(e.frozen,false);
});

test('reload reconciles both old role tags and tagless frozen components',async()=>{
  for(const tagged of [false,true]){
    const f=await fixture(),e=f.entity();e.frozen=true;if(tagged)e.addTag('fc_train_range');
    f.advance(1500);f.ctl.beginPass([e]);assert.equal(e.frozen,false);assert.equal(e.tags.size,0);
  }
});

test('failed legacy cleanup prevents acquisition until a later successful release',async()=>{
  const f=await fixture(),e=f.entity();e.frozen=true;e.errors.set('fc:guild_training_stop',1);
  f.ctl.beginPass([e]);assert.equal(f.acquire(e),null);assert.equal(e.placements.length,0);
  f.ctl.beginPass([e]);assert.equal(e.frozen,false);assert.notEqual(f.acquire(e),null);
});

test('inactive invalid handles are forgotten and a returned id reconciles again',async()=>{
  const f=await fixture(),old=f.entity();f.advance(1500);f.ctl.beginPass([old]);
  assert.equal(old.frozen,false);old.isValid=false;f.ctl.beginPass([]);
  const loaded=f.entity();loaded.id=old.id;loaded.frozen=true;loaded.addTag('fc_train_ring_a');
  f.ctl.beginPass([loaded]);
  assert.equal(loaded.frozen,false);assert.equal(loaded.tags.size,0);
  assert.equal(loaded.events.filter(event=>event==='fc:guild_training_stop').length,1);
});

test('blocked headroom, side footprint, unsupported or unloaded station never acquires',async()=>{
  for(const obstruction of ['head','side','floor','unloaded']){
    const f=await fixture(),e=f.entity(),p={x:99.9,y:1,z:61.5};
    if(obstruction==='head')f.blocks.set('99,2,61',{isSolid:true,isAir:false});
    if(obstruction==='side')f.blocks.set('100,1,61',{isSolid:true,isAir:false});
    if(obstruction==='floor')f.blocks.set('99,0,61',{isSolid:false,isAir:true});
    if(obstruction==='unloaded')f.blocks.set('99,1,61',undefined);
    f.ctl.beginPass([e]);assert.equal(f.acquire(e,'fc_train_ring_a',p),null,obstruction);
    assert.equal(e.placements.length,0);assert.equal(e.frozen,false);
  }
});

test('authored floors work with stable 2.1 Block fields and unknown replacements are refused',async()=>{
  for(const typeId of ['minecraft:coarse_dirt','minecraft:dirt_path','minecraft:oak_fence']){
    const f=await fixture(),e=f.entity();f.blocks.set('99,0,61',{typeId,isAir:false});
    assert.equal(f.api.guildStationClear(e,pointA),typeId!=='minecraft:oak_fence');
  }
});

test('engine placement false/throw is not retried or replaced by unchecked teleport',async()=>{
  for(const failure of ['false','throw']){
    const f=await fixture(),e=f.entity();f.ctl.beginPass([e]);
    if(failure==='false')e.blocked=true;else e.errors.set('tryTeleport',1);
    assert.equal(f.acquire(e),null);f.ctl.beginPass([e]);assert.equal(f.acquire(e),null);
    assert.equal(e.placements.length,1);assert.equal(e.teleports.length,0);assert.equal(e.frozen,false);
  }
});

test('pair acquisition is all-or-release; retained lone partner is released',async()=>{
  const f=await fixture(),a=f.entity(),b=f.entity();f.ctl.beginPass([a,b]);b.blocked=true;
  assert.equal(f.pair(a,b),null);assert.equal(a.frozen,false);assert.equal(b.frozen,false);
  const g=await fixture(),c=g.entity(),d=g.entity();g.ctl.beginPass([c,d]);const tokens=g.pair(c,d);
  assert.ok(tokens);d.isValid=false;g.ctl.beginPass([c]);g.ctl.retain(new Set());
  assert.equal(c.frozen,false);assert.equal(g.ctl.isActive(c,tokens[0]),false);
});

test('combat, Follow, married state, dimension change and displacement invalidate activity',async()=>{
  for(const cause of ['combat','follow','married','dimension','displaced']){
    const f=await fixture(),e=f.entity();f.ctl.beginPass([e]);const token=f.acquire(e);
    if(cause==='combat')e.addTag('fc_aggravated');
    if(cause==='follow')e.addTag('fc_guild_following');
    if(cause==='married')e.married=true;
    if(cause==='dimension')e.dimension={...f.dimension,id:'minecraft:nether'};
    if(cause==='displaced')e.location={x:150,y:1,z:61.5};
    assert.equal(f.ctl.isActive(e,token),false,cause);assert.equal(e.frozen,false,cause);assert.equal(e.placements.length,1);
  }
});

test('night, empty scan and invalid/unloaded entity cancel tokens; reloaded entity is reconciled',async()=>{
  for(const cause of ['night','empty','invalid']){
    const f=await fixture(),e=f.entity();f.ctl.beginPass([e]);const token=f.acquire(e);
    if(cause==='night')f.advance(20,13000);
    if(cause==='invalid')e.isValid=false;
    f.ctl.beginPass(cause==='night'?[e]:[]);assert.equal(f.ctl.isActive(e,token),false);
    e.isValid=true;f.advance(1500);f.ctl.beginPass([e]);assert.equal(e.frozen,false);assert.equal(e.tags.size,0);
  }
});

test('an old session token cannot interrupt a new assignment or neutralize defence',async()=>{
  const f=await fixture(),e=f.entity();f.ctl.beginPass([e]);const old=f.acquire(e);
  f.advance(1200);f.ctl.beginPass([e]);f.advance(3600);f.ctl.beginPass([e]);const current=f.acquire(e);
  assert.equal(f.ctl.isActive(e,old),false);assert.equal(f.ctl.isActive(e,current),true);
  e.triggerEvent('fc:react_attack');e.addTag('fc_aggravated');f.ctl.interrupt(e);
  assert.equal(e.reaction,'fc:react_attack');assert.equal(e.hasTag('fc_aggravated'),true);assert.equal(e.frozen,false);
});

test('production scheduler repeats harmless activity without repeated placement and releases on rest',async()=>{
  const f=await fixture(),a=f.entity(),b=f.entity(),archer=f.entity('fc:guild_apprentice_skill');const runtime=await f.runtime();
  for(let tick=10;tick<=100;tick+=10){f.advance(tick);runtime.training();f.runDue();}
  for(const e of [a,b,archer]){assert.equal(e.placements.length,1);assert.equal(e.frozen,true);}
  assert.ok(f.particles.length>0);assert.ok(f.sounds.some(s=>s.id==='random.bow'));assert.equal(f.spawned.length,0);
  f.advance(1200);runtime.training();for(const e of [a,b,archer]){assert.equal(e.frozen,false);assert.equal(e.teleports.length,0);}
});

test('production conversation interrupts immediately and prevents same-session resumption',async()=>{
  const f=await fixture(),a=f.entity(),b=f.entity(),archer=f.entity('fc:guild_apprentice_skill');const runtime=await f.runtime();
  runtime.training();const ev={target:archer,player:{id:'hero',isValid:true,dimension:archer.dimension,location:{...archer.location}},cancel:false};runtime.interact(ev);
  assert.equal(ev.cancel,true);assert.equal(runtime.dialogues.length,1);assert.equal(archer.frozen,false);
  f.advance(30);runtime.training();f.runDue();assert.equal(archer.placements.length,1);assert.equal(archer.frozen,false);
  assert.equal(f.sounds.some(s=>s.id==='random.bow'),false);assert.equal(f.spawned.length,0);
});

test('production scheduler releases a lone fighter when the partner disappears',async()=>{
  const f=await fixture(),a=f.entity(),b=f.entity();f.entity('fc:guild_apprentice_skill');const runtime=await f.runtime();
  runtime.training();assert.equal(a.frozen,true);b.isValid=false;f.advance(20);runtime.training();
  assert.equal(a.frozen,false);assert.equal(a.tags.size,0);assert.equal(a.placements.length,1);
  f.runDue();assert.equal(f.sounds.some(s=>s.id==='fc.sword_clash'),false);
});

test('production delayed archery cancels on aggression, rest, death and social Watch/Follow',async()=>{
  for(const cause of ['aggression','rest','death','watch','follow']){
    const f=await fixture();f.entity();f.entity();const archer=f.entity('fc:guild_apprentice_skill');const runtime=await f.runtime();
    runtime.training();
    if(cause==='aggression')archer.addTag('fc_aggravated');
    if(cause==='death')archer.isValid=false;
    if(cause==='watch'||cause==='follow')runtime.emote(archer,`fc:react_${cause}`);
    f.advance(cause==='rest'?1200:30);f.runDue();
    assert.equal(f.sounds.some(s=>s.id==='random.bow'),false,cause);assert.equal(f.spawned.length,0);
    if(cause==='follow'){
      assert.equal(archer.hasTag('fc_guild_following'),true);f.advance(3600);runtime.training();assert.equal(archer.placements.length,1);
      runtime.emote(archer,'fc:react_neutral');assert.equal(archer.hasTag('fc_guild_following'),false);
      f.advance(7200);runtime.training();assert.equal(archer.placements.length,2);
    }
  }
});

test('production boast excludes active trainees, aggravated defenders and followers',async()=>{
  const f=await fixture();const a=f.entity(),b=f.entity(),archer=f.entity('fc:guild_apprentice_skill');const runtime=await f.runtime();
  runtime.training();const guard=f.entity('fc:guard_bowerstone');guard.addTag('fc_aggravated');
  const follower=f.entity();follower.addTag('fc_guild_following');
  runtime.boast({setDynamicProperty(){},sendMessage(){}},{x:0,y:0,z:0});
  for(const e of [a,b,archer,guard,follower])assert.equal(e.teleports.length,0,e.typeId);
  assert.equal(a.frozen,true);assert.equal(b.frozen,true);assert.equal(archer.frozen,true);
});

function willDummy(f) {
  f.blocks.set('60,2,85',{typeId:'minecraft:hay_block',isAir:false});
  f.blocks.set('60,3,85',{typeId:'minecraft:carved_pumpkin',isAir:false});
  f.blocks.set('60,2,86',{typeId:'minecraft:oak_fence',isAir:false});
}

test('Will practice stays on the island and never substitutes for missing Might fighters',async()=>{
  const f=await fixture();willDummy(f);
  const might=f.entity(),skill=f.entity('fc:guild_apprentice_skill'),will=f.entity('fc:guild_apprentice_will');
  const otherWill=f.entity('fc:guild_apprentice_will');otherWill.location={x:20,y:1,z:40};
  const runtime=await f.runtime();
  for(let tick=10;tick<=240;tick+=10){f.advance(tick);runtime.training();f.runDue();}
  assert.equal(might.placements.length,0);assert.equal(might.frozen,false);
  assert.equal(skill.hasTag('fc_train_range'),true);
  const practising=[will,otherWill].find(e=>e.hasTag('fc_train_will'));
  assert.ok(practising);assert.equal(practising.placements.length,1);
  assert.deepEqual({...practising.location},{x:60.5,y:1,z:88.5});
  assert.deepEqual({...practising.placements[0].options.facingLocation},{x:60.5,y:3.75,z:85.5});
  assert.ok(practising.animations.filter(n=>n==='animation.npc.will_practice').length>=2);
  assert.equal([will,otherWill].flatMap(e=>e.animations).some(n=>n==='animation.npc.spar'),false);
  assert.equal(f.spawned.length,0);
  const arcs=f.particles.filter(p=>p.id==='wd:lightning_arc');assert.ok(arcs.length>=32);
  assert.equal(arcs[0].variables.values['variable.color'].blue,1);
  assert.ok(arcs[0].variables.values['variable.size']>0);
  assert.ok(f.sounds.some(s=>s.id==='fc.spell_cast'));
  assert.equal([will,otherWill].filter(e=>e.frozen).length,1);
  f.advance(1200);runtime.training();
  for(const e of [will,otherWill]){assert.equal(e.frozen,false);assert.equal(e.teleports.length,0);}
});

test('Will refuses blocked, replaced and unavailable island support, dummy or beam without writes',async()=>{
  for(const cause of ['head','floor','unloaded','missing_dummy','replaced_dummy','missing_hay','beam']){
    const f=await fixture();willDummy(f);const will=f.entity('fc:guild_apprentice_will');
    if(cause==='head')f.blocks.set('60,2,88',{typeId:'minecraft:chest',isAir:false});
    if(cause==='floor')f.blocks.set('60,0,88',{typeId:'minecraft:diamond_block',isAir:false});
    if(cause==='unloaded')f.blocks.set('60,2,87',undefined);
    if(cause==='missing_dummy')f.blocks.delete('60,3,85');
    if(cause==='replaced_dummy')f.blocks.set('60,3,85',{typeId:'minecraft:chest',isAir:false});
    if(cause==='missing_hay')f.blocks.delete('60,2,85');
    if(cause==='beam')f.blocks.set('60,2,87',{typeId:'minecraft:stone',isAir:false});
    const before=[...f.blocks];const runtime=await f.runtime();
    for(let tick=10;tick<=60;tick+=10){f.advance(tick);runtime.training();f.runDue();}
    assert.equal(will.placements.length,0,cause);assert.equal(will.frozen,false,cause);
    assert.equal(f.particles.length,0,cause);assert.deepEqual([...f.blocks],before,cause);
  }
});

test('Will delayed pulses cancel before first release on conversation, Follow, defence and load/session changes',async()=>{
  for(const cause of ['conversation','follow','watch','aggravation','defence','rest','night','invalid','dimension','displaced','dummy','lane']){
    const f=await fixture();willDummy(f);const will=f.entity('fc:guild_apprentice_will'),runtime=await f.runtime();
    runtime.training();assert.equal(will.frozen,true,cause);
    if(cause==='conversation')runtime.interact({target:will,player:{id:'hero',isValid:true,dimension:will.dimension,location:{...will.location}},cancel:false});
    if(cause==='follow'||cause==='watch')runtime.emote(will,`fc:react_${cause}`);
    if(cause==='aggravation')will.addTag('fc_aggravated');
    if(cause==='defence')will.addTag('fc_guild_defending');
    if(cause==='invalid')will.isValid=false;
    if(cause==='dimension')will.dimension={...f.dimension,id:'minecraft:nether'};
    if(cause==='displaced')will.location={x:65,y:1,z:88};
    if(cause==='dummy')f.blocks.delete('60,3,85');
    if(cause==='lane')f.blocks.set('60,2,87',{typeId:'minecraft:chest',isAir:false});
    f.advance(cause==='rest'?1200:30,cause==='night'?13000:1000);f.runDue();
    assert.equal(f.particles.length,0,cause);assert.equal(f.sounds.length,0,cause);assert.equal(f.spawned.length,0,cause);
    assert.equal(will.placements.length,1,cause);
  }
});

test('Will interruption between pulses cancels all remaining feedback and retains social and resident identity',async()=>{
  const f=await fixture();willDummy(f);const will=f.entity('fc:guild_apprentice_will'),runtime=await f.runtime();
  const properties={fc_guild_resident_slot:'saved-will-hall',fc_spouse_player:'hero-a',fc_love:90,fc_gift_tick:100};
  will.properties=properties;will.nameTag='Named resident';const id=will.id;
  runtime.training();f.advance(18);f.runDue();assert.equal(f.particles.length,10);
  runtime.emote(will,'fc:react_follow');f.advance(40);f.runDue();runtime.training();
  assert.equal(f.particles.length,10);assert.equal(will.frozen,false);assert.equal(will.hasTag('fc_guild_following'),true);
  assert.equal(will.reaction,'fc:react_follow');assert.equal(will.id,id);assert.equal(will.nameTag,'Named resident');
  assert.strictEqual(will.properties,properties);assert.equal(will.placements.length,1);
  f.advance(3600);runtime.training();assert.equal(will.placements.length,1);
});

test('Will cleanup retries failed events and reconciles old Will role tags after reload',async()=>{
  const f=await fixture();willDummy(f);const will=f.entity('fc:guild_apprentice_will'),runtime=await f.runtime();
  runtime.training();will.errors.set('fc:guild_training_stop',1);runtime.controller.interrupt(will);
  assert.equal(will.hasTag('fc_train_will'),true);assert.equal(will.frozen,true);
  f.advance(30);f.runDue();assert.equal(f.particles.length,0);runtime.training();
  assert.equal(will.hasTag('fc_train_will'),false);assert.equal(will.frozen,false);
  will.frozen=true;will.addTag('fc_train_will');f.advance(1500);
  const reloaded=f.controller();reloaded.beginPass([will]);
  assert.equal(will.hasTag('fc_train_will'),false);assert.equal(will.frozen,false);
});

test('Will engine placement failure never retries during the session or falls back to teleport',async()=>{
  for(const fail of ['false','throw']){
    const f=await fixture();willDummy(f);const will=f.entity('fc:guild_apprentice_will'),runtime=await f.runtime();
    if(fail==='false')will.blocked=true;else will.errors.set('tryTeleport',1);
    runtime.training();f.advance(20);runtime.training();f.advance(40);f.runDue();
    assert.equal(will.placements.length,1,fail);assert.equal(will.teleports.length,0);assert.equal(will.frozen,false);
    assert.equal(f.particles.length,0);assert.equal(f.spawned.length,0);
  }
});

test('old Will callbacks cannot release a newly acquired later session',async()=>{
  const f=await fixture();willDummy(f);const will=f.entity('fc:guild_apprentice_will'),runtime=await f.runtime();
  runtime.training();const oldTimers=f.timers.splice(0);
  f.advance(1200);runtime.training();f.advance(3600);runtime.training();
  assert.equal(will.placements.length,2);oldTimers.forEach(t=>t.fn());
  assert.equal(f.particles.length,0);assert.equal(will.frozen,true);assert.equal(will.hasTag('fc_train_will'),true);
  f.advance(3620);f.runDue();assert.equal(f.particles.length,40);
});


const skillEdits = [
  ['missing_target','83,2,34','minecraft:air'],
  ['replaced_target','83,2,34','minecraft:chest'],
  ['unavailable_target','83,2,34',undefined],
  ['missing_hay','83,1,34','minecraft:air'],
  ['replaced_hay','83,1,34','minecraft:stone'],
  ['unavailable_hay','83,1,34',undefined],
  ['near_target_lane','83,2,35','minecraft:chest'],
  ['middle_lane','83,2,37','minecraft:chest'],
  ['near_archer_lane','83,2,38','minecraft:chest'],
  ['unavailable_lane','83,2,37',undefined],
  ['missing_station_support','83,0,39','minecraft:air'],
  ['replaced_station_support','83,0,39','minecraft:diamond_block'],
  ['unavailable_station_support','83,0,39',undefined],
  ['blocked_station_head','83,2,39','minecraft:chest'],
];
function editSkillCell(f,key,typeId) {
  f.blocks.set(key,typeId===undefined?undefined:{typeId,isAir:typeId==='minecraft:air'});
}
function assertSkillHarmless(f,before,label) {
  assert.deepEqual([...f.blocks],before,label);
  assert.deepEqual(f.mutations,[],label);
  assert.equal(f.spawned.length,0,label);
}

test('Skill clear pulses retain their six-particle ray, checked placement and saved resident state',async()=>{
  const f=await fixture(),skill=f.entity('fc:guild_apprentice_skill'),runtime=await f.runtime();
  const properties={fc_guild_resident_slot:'skill_range',fc_love:72,fc_gift_tick:50};
  skill.properties=properties;skill.nameTag='Saved Skill resident';const id=skill.id,before=[...f.blocks];
  for(const tick of [10,26,70,86]){f.advance(tick);if(tick===10||tick===70)runtime.training();f.runDue();}
  assert.equal(f.particles.length,12);assert.equal(f.sounds.filter(s=>s.id==='random.bow').length,2);
  for(const batch of [0,6])for(let i=1;i<=6;i++){
    const particle=f.particles[batch+i-1];assert.equal(particle.id,'minecraft:critical_hit_emitter');
    assert.deepEqual({...particle.p},{x:83.5,y:2.35+(2.45-2.35)*i/6,z:39.5-5*i/6});
  }
  assert.equal(skill.placements.length,1);assert.equal(skill.placements[0].options.checkForBlocks,true);
  assert.equal(skill.teleports.length,0);assert.equal(skill.id,id);assert.equal(skill.nameTag,'Saved Skill resident');
  assert.strictEqual(skill.properties,properties);assert.deepEqual(skill.properties,{fc_guild_resident_slot:'skill_range',fc_love:72,fc_gift_tick:50});
  assertSkillHarmless(f,before);
});

test('Skill refuses edited or unavailable target, hay, lane and standing cells before acquisition',async()=>{
  for(const [cause,key,typeId] of skillEdits){
    const f=await fixture(),skill=f.entity('fc:guild_apprentice_skill'),runtime=await f.runtime();
    editSkillCell(f,key,typeId);const before=[...f.blocks];
    for(const tick of [10,20,40]){f.advance(tick);runtime.training();f.runDue();}
    assert.equal(skill.placements.length,0,cause);assert.equal(skill.frozen,false,cause);
    assert.equal(skill.animations.length,0,cause);assert.equal(f.particles.length,0,cause);assert.equal(f.sounds.length,0,cause);
    assertSkillHarmless(f,before,cause);
  }
});

test('Skill delayed pulse rechecks each edited or unavailable cell and cannot resume the interrupted session',async()=>{
  for(const [cause,key,typeId] of skillEdits){
    const f=await fixture(),skill=f.entity('fc:guild_apprentice_skill'),runtime=await f.runtime();
    runtime.training();assert.equal(skill.frozen,true,cause);const previous=f.blocks.get(key),present=f.blocks.has(key);
    editSkillCell(f,key,typeId);const before=[...f.blocks];f.advance(26);f.runDue();
    assert.equal(skill.frozen,false,cause);assert.equal(skill.hasTag('fc_train_range'),false,cause);
    assert.equal(f.particles.length,0,cause);assert.equal(f.sounds.length,0,cause);assertSkillHarmless(f,before,cause);
    if(present)f.blocks.set(key,previous);else f.blocks.delete(key);
    f.advance(300);runtime.training();assert.equal(skill.placements.length,1,cause);assert.equal(skill.frozen,false,cause);
    f.advance(3600);runtime.training();assert.equal(skill.placements.length,2,cause);assert.equal(skill.frozen,true,cause);
  }
});

test('Skill missing-chunk exceptions refuse acquisition and cancel a queued pulse with retriable cleanup',async()=>{
  for(const key of ['83,2,34','83,1,34','83,2,37','83,0,39'])for(const delayed of [false,true]){
    const f=await fixture(),skill=f.entity('fc:guild_apprentice_skill'),runtime=await f.runtime();
    if(delayed)runtime.training();const read=f.dimension.getBlock.bind(f.dimension);
    f.dimension.getBlock=p=>{if(`${p.x},${p.y},${p.z}`===key)throw Error('Injected unavailable chunk');return read(p);};
    if(delayed)skill.errors.set('fc:guild_training_stop',1);
    const before=[...f.blocks];f.advance(26);if(!delayed)runtime.training();f.runDue();
    assert.equal(f.particles.length,0,key);assert.equal(f.sounds.length,0,key);assertSkillHarmless(f,before,key);
    assert.equal(skill.placements.length,delayed?1:0,key);
    if(delayed){
      assert.equal(skill.frozen,true,key);assert.equal(runtime.controller.eligible(skill),false,key);
      runtime.training();assert.equal(skill.frozen,false,key);assert.equal(skill.hasTag('fc_train_range'),false,key);
    }
  }
});

test('Skill checks every later scheduled pulse after a previously successful shot',async()=>{
  const f=await fixture(),skill=f.entity('fc:guild_apprentice_skill'),runtime=await f.runtime();
  runtime.training();f.advance(26);f.runDue();assert.equal(f.particles.length,6);
  f.advance(70);runtime.training();editSkillCell(f,'83,2,37','minecraft:chest');const before=[...f.blocks];
  f.advance(86);f.runDue();assert.equal(f.particles.length,6);assert.equal(f.sounds.length,1);
  assert.equal(skill.frozen,false);assert.equal(skill.placements.length,1);assert.equal(skill.teleports.length,0);
  assertSkillHarmless(f,before);
});

test('Skill delayed pulse preserves conversation, Follow, Watch, spouse and defender precedence',async()=>{
  for(const cause of ['conversation','follow','watch','married','aggravation','defence','rest','night','invalid','dimension','displaced']){
    const f=await fixture(),skill=f.entity('fc:guild_apprentice_skill'),runtime=await f.runtime();
    runtime.training();const properties={fc_guild_resident_slot:'skill_range',fc_spouse_player:'hero-a',fc_love:90};
    skill.properties=properties;skill.nameTag='Saved resident';const id=skill.id,before=[...f.blocks];
    if(cause==='conversation')runtime.interact({target:skill,player:{id:'hero',isValid:true,dimension:skill.dimension,location:{...skill.location}},cancel:false});
    if(cause==='follow'||cause==='watch')runtime.emote(skill,`fc:react_${cause}`);
    if(cause==='married')skill.married=true;
    if(cause==='aggravation')skill.addTag('fc_aggravated');
    if(cause==='defence'){skill.addTag('fc_guild_defending');skill.reaction='fc:react_attack';}
    if(cause==='invalid')skill.isValid=false;
    if(cause==='dimension')skill.dimension={...f.dimension,id:'minecraft:nether'};
    if(cause==='displaced')skill.location={x:88,y:1,z:39};
    f.advance(cause==='rest'?1200:26,cause==='night'?13000:1000);f.runDue();
    assert.equal(f.particles.length,0,cause);assert.equal(f.sounds.length,0,cause);assertSkillHarmless(f,before,cause);
    assert.equal(skill.placements.length,1,cause);assert.equal(skill.teleports.length,0,cause);
    assert.equal(skill.id,id,cause);assert.equal(skill.nameTag,'Saved resident',cause);assert.strictEqual(skill.properties,properties,cause);
    if(cause==='follow'){assert.equal(skill.hasTag('fc_guild_following'),true);assert.equal(skill.reaction,'fc:react_follow');}
    if(cause==='watch')assert.equal(skill.reaction,'fc:react_watch');
    if(cause==='aggravation')assert.equal(skill.hasTag('fc_aggravated'),true);
    if(cause==='defence'){assert.equal(skill.hasTag('fc_guild_defending'),true);assert.equal(skill.reaction,'fc:react_attack');}
  }
});

test('old Skill callbacks cannot inspect an edited lane or release a later assignment',async()=>{
  const f=await fixture(),skill=f.entity('fc:guild_apprentice_skill'),runtime=await f.runtime();
  runtime.training();const oldTimers=f.timers.splice(0);
  f.advance(1200);runtime.training();f.advance(3600);runtime.training();assert.equal(skill.placements.length,2);
  editSkillCell(f,'83,2,37','minecraft:chest');f.blockReads.length=0;oldTimers.forEach(t=>t.fn());
  assert.deepEqual(f.blockReads,[]);assert.equal(f.particles.length,0);assert.equal(f.sounds.length,0);
  assert.equal(skill.frozen,true);assert.equal(skill.hasTag('fc_train_range'),true);
  f.blocks.delete('83,2,37');f.advance(3616);f.runDue();assert.equal(f.particles.length,6);assert.equal(f.sounds.length,1);
});

test('Skill engine placement failure keeps the existing one-attempt session limit',async()=>{
  for(const failure of ['false','throw']){
    const f=await fixture(),skill=f.entity('fc:guild_apprentice_skill'),runtime=await f.runtime();
    if(failure==='false')skill.blocked=true;else skill.errors.set('tryTeleport',1);
    const before=[...f.blocks];for(const tick of [10,20,40]){f.advance(tick);runtime.training();f.runDue();}
    assert.equal(skill.placements.length,1,failure);assert.equal(skill.teleports.length,0,failure);assert.equal(skill.frozen,false,failure);
    assert.equal(f.particles.length,0,failure);assert.equal(f.sounds.length,0,failure);assertSkillHarmless(f,before,failure);
  }
});

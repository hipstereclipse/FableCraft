// GP16 actual scheduler/callback probe. Supply a saved main.js with its sibling
// guild_training.js and fable_emotes.js to reproduce the pre-fix behavior.
// Baseline: git show 17d1191e73d830ad4c809d2f6af62b724465eede:packs/Fablecraft_BP/scripts/<file>
// With no argument, probes the current working source at the same mocked boundary.
// Production session module + actual main/emote callbacks at mocked Bedrock boundaries.
// node --experimental-vm-modules scripts/tests/guild_training.test.mjs
import assert from 'node:assert/strict';
import vm from 'node:vm';
import { readFile } from 'node:fs/promises';
import { parse } from 'espree';
import { dirname, join } from 'node:path';
import { createHash } from 'node:crypto';

const mainPath = process.argv[2] ?? 'packs/Fablecraft_BP/scripts/main.js';
const moduleSource = await readFile(join(dirname(mainPath), 'guild_training.js'), 'utf8');
const mainSource = await readFile(mainPath, 'utf8');
const emoteSource = await readFile(join(dirname(mainPath), 'fable_emotes.js'), 'utf8');
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
  const dimension = {
    id: 'minecraft:overworld',
    getBlock(p) { const key = `${p.x},${p.y},${p.z}`; return blocks.has(key) ? blocks.get(key) : {typeId:p.y===0?'minecraft:coarse_dirt':'minecraft:air',isAir:p.y>0}; },
    getEntities(query) { return entities.filter(e=>e.isValid && (!query.type || e.typeId===query.type)
      && (!query.tags || query.tags.every(t=>e.tags.has(t))))
      .filter(e=>!query.location || Math.hypot(e.location.x-query.location.x,e.location.y-query.location.y,e.location.z-query.location.z)<=query.maxDistance); },
    spawnParticle(id,p,variables) { particles.push({id,p,variables}); },
    playSound(id,p) { sounds.push({id,p}); },
    spawnEntity(id,p) { spawned.push({id,p}); throw new Error('Practice must never spawn a projectile'); },
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
      'guildWillLaneClear','showPracticeWill','playWillPractice','boastGatherCrowd'];
    if(ast.body.some(n=>n.type==='FunctionDeclaration'&&n.id.name==='guildSkillLaneClear'))bindingNames.push('guildSkillLaneClear');
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
  return {api,context,ctl,controller,entity,entities,dimension,blocks,particles,sounds,spawned,timers,advance,runDue,acquire,pair,runtime};
}


const results=[];
for(const cause of ['clear','lane_chest','missing_target','replaced_target','unavailable_target','missing_hay','replaced_hay','unavailable_lane','throw_lane','missing_station_support']){
  const f=await fixture(), archer=f.entity('fc:guild_apprentice_skill');
  f.blocks.set('83,2,34',{typeId:'minecraft:target',isAir:false});
  f.blocks.set('83,1,34',{typeId:'minecraft:hay_block',isAir:false});
  const runtime=await f.runtime();runtime.training();
  if(cause==='lane_chest')f.blocks.set('83,2,37',{typeId:'minecraft:chest',isAir:false});
  if(cause==='missing_target')f.blocks.delete('83,2,34');
  if(cause==='replaced_target')f.blocks.set('83,2,34',{typeId:'minecraft:chest',isAir:false});
  if(cause==='unavailable_target')f.blocks.set('83,2,34',undefined);
  if(cause==='missing_hay')f.blocks.delete('83,1,34');
  if(cause==='replaced_hay')f.blocks.set('83,1,34',{typeId:'minecraft:chest',isAir:false});
  if(cause==='unavailable_lane')f.blocks.set('83,2,37',undefined);
  if(cause==='missing_station_support')f.blocks.set('83,0,39',{typeId:'minecraft:air',isAir:true});
  const read=f.dimension.getBlock.bind(f.dimension),reads=[];
  f.dimension.getBlock=p=>{const k=`${p.x},${p.y},${p.z}`;reads.push(k);if(cause==='throw_lane'&&k==='83,2,37')throw Error('Unloaded chunk');return read(p);};
  const before=[...f.blocks];f.advance(26);f.runDue();
  assert.deepEqual([...f.blocks],before);
  results.push({case:cause,particles:f.particles.length,bow_sounds:f.sounds.filter(s=>s.id==='random.bow').length,
    spawned_entities:f.spawned.length,placements:archer.placements.length,training_active:archer.frozen,
    delayed_reads:[...new Set(reads)],saved_blocks_unchanged:true});
}
console.log(JSON.stringify({main_path:mainPath,source_sha256:Object.fromEntries(
  [['main.js',mainSource],['guild_training.js',moduleSource],['fable_emotes.js',emoteSource]]
    .map(([name,source])=>[name,createHash('sha256').update(source).digest('hex')])),kind:'actual production Skill scheduler and delayed callback at mocked Bedrock boundaries',engine_acceptance:'unrun',results},null,2));

// Executes the production controller, emitted events/filters and main callbacks.
// node --experimental-vm-modules scripts/tests/guild_defence.test.mjs
import { test } from 'node:test';
import assert from 'node:assert/strict';
import vm from 'node:vm';
import { readFile } from 'node:fs/promises';
import { parse } from 'espree';

const source = await readFile('packs/Fablecraft_BP/scripts/guild_defence.js', 'utf8');
const main = await readFile('packs/Fablecraft_BP/scripts/main.js', 'utf8');
const emotes = await readFile('packs/Fablecraft_BP/scripts/fable_emotes.js', 'utf8');
const ast = parse(main, {ecmaVersion:'latest',sourceType:'module',range:true});
const ids = ['guildmaster','maze','guild_apprentice_might','guild_apprentice_skill','guild_apprentice_will','guard_bowerstone','guard_oakvale','trader'];
const definitions = Object.fromEntries(await Promise.all(ids.map(async id => [id, JSON.parse(await readFile(`packs/Fablecraft_BP/entities/${id}.json`,'utf8'))['minecraft:entity']])));
const declaration = name => {
  const node=ast.body.find(n=>n.type==='FunctionDeclaration'&&n.id.name===name
    ||n.type==='VariableDeclaration'&&n.declarations.some(d=>d.id.name===name));
  assert.ok(node,`Production declaration ${name}`);return main.slice(...node.range);
};
function filter(f,self,other) {
  if(f.all_of)return f.all_of.every(x=>filter(x,self,other));
  if(f.any_of)return f.any_of.some(x=>filter(x,self,other));
  const subject=f.subject==='self'?self:other;
  const result=f.test==='has_tag'?subject.hasTag(f.value):f.test==='is_family'?subject.families.includes(f.value):false;
  return ['not','!='].includes(f.operator)?!result:result;
}

async function fixture() {
  const mod=new vm.SourceTextModule(source,{context:vm.createContext({})});
  await mod.link(()=>{throw Error('Defence controller must have no Bedrock import');});await mod.evaluate();
  const api=mod.namespace;
  let tick=100, serial=0;
  const heroes=[],npcs=[],interruptions=[];
  const dimensions=Object.fromEntries(['overworld','nether'].map(id=>[`minecraft:${id}`,{
    id:`minecraft:${id}`,
    getEntities(q){return npcs.filter(e=>e.isValid&&e.dimension.id===this.id&&(!q.type||e.typeId===q.type)
      &&(!q.tags||q.tags.every(t=>e.hasTag(t)))&&(!q.families||q.families.every(f=>e.families.includes(f)))
      &&(!q.location||Math.hypot(e.location.x-q.location.x,e.location.y-q.location.y,e.location.z-q.location.z)<=q.maxDistance));},
  }]));
  function entity(type,location={x:30,y:1,z:40}) {
    const e={id:`e-${++serial}`,typeId:type,isValid:true,location:{...location},dimension:dimensions['minecraft:overworld'],
      tags:new Set(),props:new Map(),events:[],errors:new Map(),families:['fc_friendly'],messages:[],
      hasTag(t){return this.tags.has(t);},getTags(){return [...this.tags];},
      fail(key){const n=this.errors.get(key)||0;if(n){this.errors.set(key,n-1);throw Error(`Injected ${key}`);}},
      addTag(t){this.fail(`add:${t}`);this.tags.add(t);},removeTag(t){this.fail(`remove:${t}`);this.tags.delete(t);},
      getDynamicProperty(k){return this.props.get(k);},setDynamicProperty(k,v){this.props.set(k,v);},
      getProperty(){return undefined;},sendMessage(m){this.messages.push(m);},playSound(){},
    };
    if(type==='minecraft:player'){e.families=['player'];heroes.push(e);return e;}
    const definition=definitions[type.slice(3)];assert.ok(definition,type);
    e.definition=definition;e.live={...definition.components};e.groups=new Set();
    if(type.includes('guard_'))e.families.push('fc_guard');
    if(type.includes('guild_apprentice'))e.families.push('fc_guild');
    e.triggerEvent=function(name){
      this.events.push(name);this.fail(name);
      const apply=action=>{
        if(!action)return;
        if(action.sequence){action.sequence.forEach(apply);return;}
        if(action.filters&&!filter(action.filters,this,this))return;
        for(const g of action.remove?.component_groups??[])if(this.groups.has(g)){
          Object.keys(definition.component_groups[g]).forEach(k=>delete this.live[k]);this.groups.delete(g);
        }
        for(const g of action.add?.component_groups??[]){this.groups.add(g);Object.assign(this.live,definition.component_groups[g]);}
      };
      apply(definition.events[name]);
    };
    npcs.push(e);return e;
  }
  const player=()=>entity('minecraft:player');
  const npc=(id='guild_apprentice_might')=>entity(`fc:${id}`);
  const warrant=(p,expires=tick*50+120000)=>p.setDynamicProperty('fc_bounties',JSON.stringify({guild_heroes:{
    key:'guild_heroes',town:'guild',name:'Heroes Guild',amount:20,expiresAtMs:expires,dimension:'minecraft:overworld',x:0,z:0,w:122,
  }}));
  function runtime() {
    const context=vm.createContext({
      ...Object.fromEntries(Object.keys(api).map(k=>[k,api[k]])),
      world:{getPlayers:()=>heroes.filter(p=>p.isValid)},OW:()=>dimensions['minecraft:overworld'],TICKS:()=>tick,
      guildBounds:()=>({base:{y:0},minX:0,maxX:122,minZ:0,maxZ:108,minY:0,maxY:70}),
      interruptGuildTraining:e=>interruptions.push(e.id),entityHasFamily:(e,f)=>e.families.includes(f),
      msg:k=>k,placeName:v=>v,refreshWantedHud(){},syncWantedTags(){},showHeroActionBar(){},
      removeBountyGuards(){throw Error('Guild must not remove town guards');},formatBountyTime:()=>'',
      bountyCrimeKind:e=>api.isGuildDefender(e)?'guard':e.families.includes('fc_friendly')?'civilian':null,
      settlementForCrime:(p,victim)=>victim.location.x<122?{key:'guild_heroes',town:'guild',name:'Heroes Guild',dimension:'minecraft:overworld',x:0,z:0,w:122}:null,
      familyOf:()=>null,nearestPlayer:()=>{throw Error('Never guess a projectile owner');},
      notifyGuildTrainingReaction(){},setNpcLove(){},npcLove:()=>0,audit(){},
    });
    const names=['P','BOUNTY_KEY','BOUNTY_AMOUNT','BOUNTY_TIME_MS','BOUNTY_TIMER_START_MS','BOUNTY_TIMER_MAX_MS',
      'GUILD_TOWN_KEY','GUILD_BOUNTY_KEY','BOUNTY_GUARD_TYPE','BOUNTY_GUARD_DETECTION_RADIUS','GUARD_TOWN','bountyDemand','assaultCd',
      'CIVILIAN_FLEE_TICKS','GUARD_AGGRO_TICKS','nowMs','getBounties','setBounties','dominantBounty','bountyHeatLevel',
      'isInsideGuild','locationInsideSettlement','guildDefenders','hasGuildWarrant','guildDefence','rallyGuildDefenders','calmGuildDefenders',
      'clearSettlementBounty','isAssaultableNpc','isGuildDefenderType','aggravate','calmNpc','alertProtectors',
      'activateEnforcers','accrueCrime','handlePlayerAssault'];
    vm.runInContext(names.map(declaration).join('\n')+'\nbindGuildDefence(guildDefence);',context);
    function callback(prefix,contains){
      const node=ast.body.find(n=>n.type==='ExpressionStatement'&&main.slice(...n.range).startsWith(prefix)
        &&main.slice(...n.range).includes(contains));
      assert.ok(node,contains);return vm.runInContext(`(${main.slice(...node.expression.arguments[0].range)})`,context);
    }
    const emoteAst=parse(emotes,{ecmaVersion:'latest',sourceType:'module',range:true});
    const emoteNode=emoteAst.body.find(n=>n.type==='FunctionDeclaration'&&n.id.name==='triggerNpcEvent');
    vm.runInContext(emotes.slice(...emoteNode.range),context);
    return {...vm.runInContext('({ctl:guildDefence,clear:clearSettlementBounty,emote:triggerNpcEvent})',context),
      bounty:callback('system.runInterval(','The countdown runs EVERYWHERE'),
      damage:callback('world.afterEvents.entityHurt.subscribe(','handlePlayerAssault'),
      death:callback('world.afterEvents.entityDie.subscribe(','accrueCrime'),
      townSweep:callback('system.runInterval(','const wantedByDimension = new Map()'),
      sweep:callback('system.runInterval(','() => guildDefence.reconcile()'),
    };
  }
  const eligible=(e,p)=>e.live['minecraft:behavior.nearest_attackable_target']?.entity_types.some(t=>filter(t.filters,e,p))??false;
  const active=e=>e.hasTag(api.GUILD_DEFENDING_TAG);
  return {api,player,npc,warrant,runtime,heroes,npcs,dimensions,eligible,active,interruptions,advance:t=>{tick=t;}};
}

test('two offenders are eligible; innocent visitor is excluded for all six defender types',async()=>{
  const f=await fixture(),a=f.player(),b=f.player(),innocent=f.player();f.warrant(a);f.warrant(b);
  const defenders=ids.slice(0,6).map(f.npc);defenders.at(-1).addTag('fc_guild_guard');
  const r=f.runtime();r.sweep();
  for(const e of defenders){assert.equal(f.active(e),true);assert.equal(f.eligible(e,a),true);assert.equal(f.eligible(e,b),true);assert.equal(f.eligible(e,innocent),false);}
  assert.equal(innocent.hasTag('fc_guild_offender'),false);
});

test('actual payment callback removes A first and cannot calm B defence',async()=>{
  const f=await fixture(),a=f.player(),b=f.player(),e=f.npc();f.warrant(a);f.warrant(b);const r=f.runtime();r.sweep();
  const starts=e.events.filter(x=>x==='fc:guild_defence_start').length;
  r.clear(a,'guild_heroes','fine paid');
  assert.equal(a.hasTag('fc_guild_offender'),false);assert.equal(f.eligible(e,a),false);assert.equal(f.active(e),true);
  assert.equal(e.events.filter(x=>x==='fc:guild_defence_start').length,starts);
  assert.ok(JSON.parse(b.getDynamicProperty('fc_bounties')).guild_heroes);
  r.clear(b,'guild_heroes');assert.equal(f.active(e),false);
});

test('actual expiry callback is independent of player iteration order and preserves live warrant',async()=>{
  for(const reverse of [false,true]){
    const f=await fixture(),a=f.player(),b=f.player(),e=f.npc();f.warrant(a,5001);f.warrant(b);const r=f.runtime();r.sweep();
    if(reverse)f.heroes.reverse();f.advance(120);r.bounty();
    assert.equal(JSON.parse(a.getDynamicProperty('fc_bounties')).guild_heroes,undefined);
    assert.equal(f.active(e),true);assert.equal(a.hasTag('fc_guild_offender'),false);assert.equal(f.eligible(e,b),true);
  }
});

test('portal departure clears eligibility and stops defence; return and reload derive unchanged warrant',async()=>{
  const f=await fixture(),p=f.player(),e=f.npc();f.warrant(p);let r=f.runtime();r.sweep();
  const progress=p.getDynamicProperty('fc_bounties');p.location={x:600024.5,y:275,z:600007.5};r.sweep();
  assert.equal(p.hasTag('fc_guild_offender'),false);assert.equal(f.active(e),false);
  r=f.runtime();r.sweep();assert.equal(f.active(e),false);
  p.location={x:30,y:1,z:40};r.sweep();assert.equal(f.active(e),true);assert.equal(f.eligible(e,p),true);
  assert.equal(p.getDynamicProperty('fc_bounties'),progress);
});

test('short provocation identifies only the attacker, expires, and is scoped to its loaded defender',async()=>{
  const f=await fixture(),p=f.player(),innocent=f.player(),e=f.npc(),other=f.npc('maze');const r=f.runtime();
  r.ctl.provoke(p,[e],320);assert.equal(f.active(e),true);assert.equal(f.active(other),false);assert.equal(f.eligible(e,innocent),false);
  f.advance(421);r.sweep();assert.equal(f.active(e),false);assert.equal(p.hasTag('fc_guild_offender'),false);
});

test('actual damage and projectile death callbacks use the responsible player; unknown owner is unattributed',async()=>{
  const f=await fixture(),owner=f.player(),innocent=f.player(),e=f.npc('maze');const r=f.runtime();
  r.damage({hurtEntity:e,damageSource:{damagingProjectile:{getComponent:()=>({owner})}}});
  assert.ok(owner.getDynamicProperty('fc_bounties'));assert.equal(innocent.getDynamicProperty('fc_bounties'),undefined);
  const before=owner.getDynamicProperty('fc_bounties');
  r.death({deadEntity:e,damageSource:{damagingProjectile:{getComponent:()=>({})}}});
  assert.equal(owner.getDynamicProperty('fc_bounties'),before);assert.equal(innocent.getDynamicProperty('fc_bounties'),undefined);
  r.death({deadEntity:e,damageSource:{damagingProjectile:{getComponent:()=>({owner})}}});
  assert.equal(JSON.parse(owner.getDynamicProperty('fc_bounties')).guild_heroes.guardKills,1);
});

test('expression attack hook identifies provoking player and leaves non-Guild attack behavior intact',async()=>{
  const f=await fixture(),p=f.player(),innocent=f.player(),guild=f.npc('guard_bowerstone'),town=f.npc('guard_oakvale');guild.addTag('fc_guild_guard');const r=f.runtime();
  r.emote(guild,'fc:react_attack',p);assert.equal(f.active(guild),true);assert.equal(f.eligible(guild,innocent),false);
  r.emote(town,'fc:react_attack',p);assert.equal(f.active(town),false);assert.ok(town.events.includes('fc:react_attack'));
});

test('Follow/Watch and spouse properties survive defence; social replacement cannot erase offender filter',async()=>{
  const f=await fixture(),p=f.player(),innocent=f.player(),e=f.npc();e.setDynamicProperty('fc_spouse_id','saved-spouse');e.addTag('fc_guild_following');
  e.triggerEvent('fc:react_follow');f.warrant(p);const r=f.runtime();r.sweep();
  assert.ok(e.groups.has('fc:reaction_follow'));e.triggerEvent('fc:react_watch');assert.equal(f.eligible(e,innocent),false);assert.equal(f.eligible(e,p),true);
  r.clear(p,'guild_heroes');assert.ok(e.groups.has('fc:reaction_watch'));assert.equal(e.getDynamicProperty('fc_spouse_id'),'saved-spouse');
  assert.equal(e.hasTag('fc_guild_following'),true);assert.equal(e.events.includes('fc:react_neutral'),false);
});

test('stop restores normal guard combat and removes legacy unowned attack without social-neutral',async()=>{
  const f=await fixture(),p=f.player(),e=f.npc('guard_bowerstone');e.addTag('fc_guild_guard');e.addTag('fc_aggravated');e.setDynamicProperty('fc_aggro_until',999999);
  e.triggerEvent('fc:react_attack');const r=f.runtime();r.sweep();
  for(const key of ['minecraft:behavior.nearest_attackable_target','minecraft:behavior.melee_box_attack','minecraft:behavior.hurt_by_target'])assert.deepEqual(e.live[key],e.definition.components[key]);
  assert.equal(e.hasTag('fc_aggravated'),false);assert.equal(e.getDynamicProperty('fc_aggro_until'),undefined);assert.equal(e.events.includes('fc:react_neutral'),false);
  assert.equal(p.hasTag('fc_guild_offender'),false);
});

test('failed stop retries cleanup before restart; failed start leaves no uncontrolled combat',async()=>{
  const f=await fixture(),p=f.player(),e=f.npc();f.warrant(p);const r=f.runtime();r.sweep();
  e.errors.set('fc:guild_defence_stop',1);r.clear(p,'guild_heroes');assert.equal(f.active(e),true);r.sweep();assert.equal(f.active(e),false);
  f.warrant(p);e.errors.set('fc:guild_defence_start',1);r.sweep();r.sweep();assert.equal(f.active(e),true);
});

test('target-tag write failure fails closed across remaining offenders and recovers',async()=>{
  const f=await fixture(),a=f.player(),b=f.player(),e=f.npc();f.warrant(a);f.warrant(b);const r=f.runtime();r.sweep();
  a.errors.set('remove:fc_guild_offender',1);r.clear(a,'guild_heroes');assert.equal(f.active(e),false);
  r.sweep();assert.equal(a.hasTag('fc_guild_offender'),false);assert.equal(f.active(e),true);assert.equal(f.eligible(e,a),false);
});

test('loaded departed defender releases; invalid handle and persisted tags reconcile on return',async()=>{
  const f=await fixture(),p=f.player(),e=f.npc();f.warrant(p);let r=f.runtime();r.sweep();
  e.location={x:500,y:1,z:500};r.sweep();assert.equal(f.active(e),false);
  e.location={x:30,y:1,z:40};r.sweep();assert.equal(f.active(e),true);e.isValid=false;r.sweep();
  p.location={x:600024,y:275,z:600007};e.isValid=true;r=f.runtime();r.sweep();assert.equal(f.active(e),false);assert.equal(p.hasTag('fc_guild_offender'),false);
});

test('town guard sweep does not clear Guild defence; ordinary Bowerstone social attack is unchanged',async()=>{
  const f=await fixture(),p=f.player(),innocent=f.player(),guild=f.npc('guard_bowerstone'),town=f.npc('guard_bowerstone');
  guild.addTag('fc_guild_guard');f.warrant(p);const r=f.runtime();r.sweep();r.townSweep();
  assert.equal(f.active(guild),true);assert.equal(guild.events.includes('fc:calm'),false);assert.ok(town.events.includes('fc:calm'));
  r.emote(town,'fc:react_attack',p);assert.equal(f.eligible(town,innocent),true,'Non-Guild social target policy is outside this pass');
  assert.equal(f.eligible(guild,innocent),false);
});

test('reload clears transient provocation and stale target markers without resetting relationships or warrants',async()=>{
  const f=await fixture(),p=f.player(),e=f.npc();e.triggerEvent('fc:react_follow');e.setDynamicProperty('fc_spouse_id','saved');
  let r=f.runtime();r.ctl.provoke(p,[e]);assert.equal(f.active(e),true);
  f.advance(0);r=f.runtime();r.sweep();assert.equal(f.active(e),false);assert.equal(p.hasTag('fc_guild_offender'),false);
  assert.ok(e.groups.has('fc:reaction_follow'));assert.equal(e.getDynamicProperty('fc_spouse_id'),'saved');
  assert.equal(p.getDynamicProperty('fc_bounties'),undefined);
});

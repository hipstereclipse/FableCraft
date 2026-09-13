// Production romance/form callbacks and inventory/training owners at mocked Bedrock boundaries.
import test from 'node:test';
import assert from 'node:assert/strict';
import vm from 'node:vm';
import {readFile} from 'node:fs/promises';
import {dirname,join} from 'node:path';
import {parse} from 'espree';
const sourcePath=process.env.FC_RELATIONSHIP_SOURCE??'packs/Fablecraft_BP/scripts/main.js';
const source=await readFile(sourcePath,'utf8');
const training=await readFile(join(dirname(sourcePath),'guild_training.js'),'utf8');
const ast=parse(source,{ecmaVersion:'latest',sourceType:'module',range:true});
const required=['P','inv','countItem','removeItem','LOVE_HEART','PET_NAMES','HELD_GIFTS','GIFT_COOLDOWN_TICKS',
  'isRomanceable','npcLove','setNpcLove','isMarried','isMySpouse','npcName','marryNpc','proposeMenu',
  'offerGift','bestGiftInBag','divorceConfirm','spouseMenu'];
const optional=['RELATIONSHIP_DISTANCE','RELATIONSHIP_FORM_TICKS','RELATIONSHIP_FORM_LIMIT','relationshipForms','readRelationship',
  'relationshipResponse','invalidateRelationshipForms','applyRelationshipWrites','relationshipRingMatches','findRelationshipRing'];
const declarations=[...required,...optional].map(name=>{
  const node=ast.body.find(n=>n.type==='FunctionDeclaration'&&n.id.name===name||n.type==='VariableDeclaration'&&n.declarations.some(d=>d.id.name===name));
  if(!node){assert.ok(optional.includes(name),`Production declaration ${name}`);return '';}
  return source.slice(...node.range);
}).join('\n');
let serial=0;
async function fixture({deferredProperties=false}={}){
  const context=vm.createContext({});const module=new vm.SourceTextModule(training,{context});
  await module.link(()=>{throw Error('Training owner must remain injected');});await module.evaluate();
  const api=module.namespace,forms=[],operations=[],caught=[],npcs=[],actors=[];
  const dim={id:'minecraft:overworld',spawnParticle(id){operations.push(['particle',id]);},
    getBlock:p=>({typeId:p.y===0?'minecraft:coarse_dirt':'minecraft:air',isAir:p.y>0})};
  const faults=new Map();
  function itemStack(value){return {...value,maxAmount:value.typeId==='fc:wedding_ring'?1:64,clone(){return itemStack(this);},isStackableWith(other){
    if(this.maxAmount===1)return false;
    const data=v=>{const parsed=JSON.parse(JSON.stringify(v));delete parsed.amount;return parsed;};
    return JSON.stringify(data(this))===JSON.stringify(data(other));}};}
  function fail(key,phase){const fault=faults.get(key);if(fault?.phase===phase&&fault.count-->0)throw Error(`Injected ${phase} ${key}`);}
  function actor(type,id){
    const props=new Map(),sync=new Map(),items=new Map(),pending=new Map();
    const e={id,typeId:type,isValid:true,dimension:dim,location:{x:83.5,y:1,z:39.5},nameTag:'Saved name',tags:new Set(),props,sync,items,pending,
      getDynamicProperty(k){fail(`${id}:getDynamicProperty:${k}`,'before');return props.get(k);},
      setDynamicProperty(k,v){fail(`${id}:setDynamicProperty:${k}`,'before');operations.push(['property',id,k,v]);if(v===undefined)props.delete(k);else props.set(k,v);fail(`${id}:setDynamicProperty:${k}`,'after');},
      getProperty(k){fail(`${id}:getProperty:${k}`,'before');return sync.get(k);},
      setProperty(k,v){fail(`${id}:setProperty:${k}`,'before');operations.push(['synced',id,k,v]);(deferredProperties?pending:sync).set(k,v);fail(`${id}:setProperty:${k}`,'after');},
      getTags(){return [...this.tags];},hasTag(t){return this.tags.has(t);},addTag(t){this.tags.add(t);},removeTag(t){this.tags.delete(t);},
      triggerEvent(event){fail(`${id}:event`,'before');operations.push(['event',id,event]);},
      playAnimation(name){fail(`${id}:animation`,'before');operations.push(['animation',id,name]);},
      playSound(name){fail(`${id}:sound`,'before');operations.push(['sound',id,name]);},
      sendMessage(text){operations.push(['message',id,text]);},lookAt(){},getHeadLocation(){return {...this.location,y:this.location.y+1.6};},
      tryTeleport(point){this.location={...point};operations.push(['placement',id]);return true;},
      getComponent(name){if(name!=='minecraft:inventory')return undefined;fail(`${id}:inventory`,'before');return {container:{size:4,
        getItem(slot){fail(`${id}:getItem`,'before');const item=items.get(slot);return item?itemStack(item):undefined;},
        setItem(slot,item){fail(`${id}:setItem`,'before');operations.push(['inventory',id,slot,item?{...item}:null]);if(item)items.set(slot,{...item});else items.delete(slot);fail(`${id}:setItem`,'after');}}};},
    };actors.push(e);return e;
  }
  function player(id=`hero-${++serial}`){const p=actor('minecraft:player',id);for(const slot of [0,2])p.items.set(slot,{typeId:'fc:wedding_ring',amount:1});return p;}
  function npc(owner='',id=`resident-${++serial}`){const e=actor('fc:guild_apprentice_skill',id);e.sync.set('fc:married',owner?1:0);e.sync.set('fc:love_hate',80);
    e.props.set('fc_spouse_player',owner);e.props.set('fc_guild_resident_slot','skill_range');e.props.set('fc_social_history','retained');npcs.push(e);return e;}
  class Form{
    title(value){this.titleText=value;return this;}body(){return this;}button(){return this;}button1(){return this;}button2(){return this;}
    show(player){this.player=player;forms.push(this);return {then:fn=>{this.resolve=(selection,canceled=false)=>{try{return fn({selection,canceled});}catch(e){caught.push(e.message);this.reject?.(e);}};return {catch:fn=>{this.reject=fn;}};},catch:fn=>{this.reject=fn;}};}
  }
  Object.assign(context,{...Object.fromEntries(Object.keys(api).map(k=>[k,api[k]])),
    ActionFormData:Form,MessageFormData:Form,displayName:id=>id,morality:()=>0,msg:id=>id,
    system:{currentTick:10},addMorality:(p,n)=>operations.push(['morality',p.id,n])});
  vm.runInContext(declarations,context);
  const runtime=vm.runInContext('({propose:proposeMenu,marry:marryNpc,spouse:spouseMenu,divorce:divorceConfirm,gift:offerGift})',context);
  const ctl=api.createGuildTrainingController({now:()=>10,session:()=>0,canTrain:()=>true});api.bindGuildTrainingReactions(ctl);
  return {context,api,ctl,forms,operations,caught,npcs,dim,faults,player,npc,runtime,
    inject(id,method,phase='before',count=1){faults.set(`${id}:${method}`,{phase,count});},
    flushProperties(){for(const e of actors){for(const [key,value] of e.pending)e.sync.set(key,value);e.pending.clear();}},
    trackedForms(){return vm.runInContext('typeof relationshipForms === "undefined" ? -1 : relationshipForms.size',context);},
    rings:p=>[...p.items.values()].filter(item=>item.typeId==='fc:wedding_ring').reduce((sum,item)=>sum+item.amount,0),
    snapshot(p,n){return JSON.stringify({player:[...p.props],npc:[...n.props],sync:[...n.sync],items:[...p.items],name:n.nameTag});}};
}
function noAction(f,before,p,n,label){assert.equal(f.snapshot(p,n),before,label);assert.deepEqual(f.operations,[],label);}
function setSpouses(p,ids){p.props.set('fc_spouses',JSON.stringify(ids));}
function weddingEvents(f){return f.operations.filter(op=>op[0]==='morality'&&op[2]===40);}

// Capture pre-fix observations before implementing the guards; fixtures above
// can be extracted by the portable milestone probe without copying callbacks.
test('normal proposal commits one ring and preserves unrelated spouse/resident history',async()=>{
  const f=await fixture(),p=f.player(),n=f.npc();setSpouses(p,['existing-spouse']);const resident=n.props.get('fc_guild_resident_slot');
  f.runtime.propose(p,n);assert.equal(f.forms.length,1);f.forms[0].resolve(0);
  assert.equal(f.rings(p),1);assert.equal(n.sync.get('fc:married'),1);assert.equal(n.props.get('fc_spouse_player'),p.id);
  assert.deepEqual(JSON.parse(p.props.get('fc_spouses')),['existing-spouse',n.id]);assert.equal(n.sync.get('fc:love_hate'),100);
  assert.equal(n.props.get('fc_guild_resident_slot'),resident);assert.equal(n.props.get('fc_social_history'),'retained');assert.equal(weddingEvents(f).length,1);
});

test('two Heroes resolving pending proposals cannot replace the first accepted spouse or pay twice',async()=>{
  for(const order of [[0,1],[1,0]]){
    const f=await fixture(),players=[f.player(),f.player()],n=f.npc();players.forEach(p=>f.runtime.propose(p,n));
    f.forms[order[0]].resolve(0);f.forms[order[1]].resolve(0);f.forms[order[0]].resolve(0);
    assert.equal(n.props.get('fc_spouse_player'),players[order[0]].id);assert.equal(f.rings(players[order[0]]),1);assert.equal(f.rings(players[order[1]]),2);
    assert.deepEqual(JSON.parse(players[order[0]].props.get('fc_spouses')),[n.id]);assert.equal(players[order[1]].props.has('fc_spouses'),false);
    assert.equal(weddingEvents(f).length,1);
  }
});

test('newer forms invalidate earlier requests and every response is consumed once',async()=>{
  const f=await fixture(),p=f.player(),n=f.npc(p.id);f.runtime.spouse(p,n);f.runtime.spouse(p,n);
  f.forms[1].resolve(2);const before=f.operations.length;f.forms[0].resolve(1);f.forms[1].resolve(2);assert.equal(f.operations.length,before);
  const g=await fixture(),hero=g.player(),target=g.npc();g.runtime.propose(hero,target);g.forms[0].resolve(0,true);g.forms[0].resolve(0);
  assert.equal(g.rings(hero),2);assert.equal(target.sync.get('fc:married'),0);assert.equal(weddingEvents(g).length,0);
});

const eligibilityChanges={
  owner:(f,p,n)=>n.props.set('fc_spouse_player','another-hero'),
  married:(f,p,n)=>{n.sync.set('fc:married',1);n.props.set('fc_spouse_player','another-hero');},
  love:(f,p,n)=>n.sync.set('fc:love_hate',59),
  ring:(f,p)=>{p.items.delete(0);p.items.delete(2);},
  player_invalid:(f,p)=>{p.isValid=false;},npc_invalid:(f,p,n)=>{n.isValid=false;},
  player_id:(f,p)=>{p.id+='-changed';},npc_id:(f,p,n)=>{n.id+='-changed';},
  player_dimension:(f,p)=>{p.dimension={...f.dim,id:'minecraft:nether'};},
  npc_dimension:(f,p,n)=>{n.dimension={...f.dim,id:'minecraft:nether'};},
  both_dimension:(f,p,n)=>{p.dimension=n.dimension={...f.dim,id:'minecraft:nether'};},
  distant:(f,p,n)=>{n.location={x:100,y:1,z:39};},nonfinite:(f,p,n)=>{n.location={x:NaN,y:1,z:39};},
  romanceability:(f,p,n)=>n.sync.delete('fc:married'),
  bad_married:(f,p,n)=>n.sync.set('fc:married','0'),bad_love:(f,p,n)=>n.sync.set('fc:love_hate',NaN),
  corrupt_list:(f,p)=>p.props.set('fc_spouses','{bad'),null_list:(f,p)=>p.props.set('fc_spouses','null'),
  mixed_list:(f,p)=>p.props.set('fc_spouses','["saved",7]'),
};
test('proposal callbacks revalidate handles, captured dimension, proximity, opinion, ring and readable history',async()=>{
  for(const [cause,change] of Object.entries(eligibilityChanges)){
    const f=await fixture(),p=f.player(),n=f.npc();f.runtime.propose(p,n);change(f,p,n);const before=f.snapshot(p,n);f.operations.length=0;
    f.forms[0].resolve(0);noAction(f,before,p,n,cause);
  }
});

test('unavailable relationship, spouse-list and inventory reads defer before proposal mutations',async()=>{
  for(const phase of ['open','accept','direct'])for(const field of ['married','owner','love','spouses','inventory','items']){
    const f=await fixture(),p=f.player(),n=f.npc();if(phase==='accept')f.runtime.propose(p,n);
    const [entity,method]=field==='married'?[n,'getProperty:fc:married']:field==='owner'?[n,'getDynamicProperty:fc_spouse_player']:
      field==='love'?[n,'getProperty:fc:love_hate']:field==='spouses'?[p,'getDynamicProperty:fc_spouses']:
      field==='inventory'?[p,'inventory']:[p,'getItem'];
    f.inject(entity.id,method,'before',100);const before=f.snapshot(p,n);f.operations.length=0;
    if(phase==='accept')f.forms[0].resolve(0);else if(phase==='direct')f.runtime.marry(p,n);else f.runtime.propose(p,n);
    noAction(f,before,p,n,`${phase}/${field}`);
  }
});

test('direct marriage calls cannot bypass current eligibility',async()=>{
  for(const cause of ['owner','married','love','ring','player_invalid','npc_invalid','distant','nonfinite','romanceability','bad_married','corrupt_list']){
    const f=await fixture(),p=f.player(),n=f.npc();eligibilityChanges[cause](f,p,n);const before=f.snapshot(p,n);f.runtime.marry(p,n);noAction(f,before,p,n,cause);
  }
});

test('stale spouse selections cannot affect a different owner or open nested divorce',async()=>{
  for(const change of ['different_owner','unmarried','unreadable'])for(let choice=0;choice<=4;choice++){
    const f=await fixture(),p=f.player(),n=f.npc(p.id);setSpouses(p,[n.id]);p.items.set(1,{typeId:'minecraft:poppy',amount:1});f.runtime.spouse(p,n);
    if(change==='different_owner')n.props.set('fc_spouse_player','new-owner');
    if(change==='unmarried'){n.sync.set('fc:married',0);n.props.set('fc_spouse_player','');}
    if(change==='unreadable')f.inject(n.id,'getDynamicProperty:fc_spouse_player','before',100);
    const before=f.snapshot(p,n);f.operations.length=0;f.forms[0].resolve(choice);
    noAction(f,before,p,n,`${change}/${choice}`);assert.equal(f.forms.length,1);
  }
});

test('spouse and nested divorce responses retain live identity, proximity and original dimension',async()=>{
  for(const cause of ['player_invalid','npc_invalid','player_id','npc_id','player_dimension','npc_dimension','both_dimension','distant','nonfinite'])for(const nested of [false,true]){
    const f=await fixture(),p=f.player(),n=f.npc(p.id);setSpouses(p,[n.id]);f.runtime.spouse(p,n);if(nested)f.forms[0].resolve(4);
    eligibilityChanges[cause](f,p,n);const before=f.snapshot(p,n);f.operations.length=0;
    f.forms[nested?1:0].resolve(nested?0:1);noAction(f,before,p,n,`${cause}/${nested}`);
  }
});

test('divorce confirms fresh ownership, preserves other spouses and cannot apply its penalty twice',async()=>{
  const f=await fixture(),p=f.player(),n=f.npc(p.id);setSpouses(p,['other-spouse',n.id]);f.runtime.spouse(p,n);f.forms[0].resolve(4);
  f.forms[1].resolve(0);f.forms[1].resolve(0);
  assert.equal(n.sync.get('fc:married'),0);assert.equal(n.props.get('fc_spouse_player'),'');assert.equal(n.sync.get('fc:love_hate'),20);
  assert.deepEqual(JSON.parse(p.props.get('fc_spouses')),['other-spouse']);assert.equal(n.props.get('fc_guild_resident_slot'),'skill_range');
  assert.equal(f.operations.filter(op=>op[0]==='morality'&&op[2]===-30).length,1);
  for(const wrong of ['different_owner','corrupt_list','unreadable_owner']){
    const g=await fixture(),hero=g.player(),spouse=g.npc(hero.id);g.runtime.divorce(hero,spouse);
    if(wrong==='different_owner')spouse.props.set('fc_spouse_player','new-owner');
    if(wrong==='corrupt_list')hero.props.set('fc_spouses','{bad');
    if(wrong==='unreadable_owner')g.inject(spouse.id,'getDynamicProperty:fc_spouse_player','before',100);
    const before=g.snapshot(hero,spouse);g.operations.length=0;g.forms[0].resolve(0);noAction(g,before,hero,spouse,wrong);
  }
});

test('an old menu stays invalid after divorce and remarriage to the same Hero',async()=>{
  const f=await fixture(),p=f.player(),n=f.npc(p.id);setSpouses(p,[n.id]);f.runtime.spouse(p,n);
  f.runtime.divorce(p,n);f.forms[1].resolve(0);n.sync.set('fc:love_hate',80);f.runtime.marry(p,n);
  const before=f.snapshot(p,n);f.operations.length=0;f.forms[0].resolve(1);noAction(f,before,p,n);
});

test('legitimate spouse Follow and Wait still invoke the actual training interruption hook',async()=>{
  for(const choice of [1,2]){
    const f=await fixture(),p=f.player(),n=f.npc(p.id);setSpouses(p,[n.id]);f.ctl.beginPass([n]);const token=f.ctl.acquire(n,'fc_train_range',n.location,{x:83.5,y:2.45,z:34.5});
    assert.notEqual(token,null);const before=f.snapshot(p,n);f.operations.length=0;f.runtime.spouse(p,n);f.forms[0].resolve(choice);
    assert.equal(f.ctl.isActive(n,token),false);assert.equal(n.hasTag('fc_guild_following'),choice===1);assert.equal(f.snapshot(p,n),before);
    assert.ok(f.operations.some(op=>op[0]==='event'&&op[2]===(choice===1?'fc:react_follow':'fc:react_neutral')));
  }
});

test('normal sweet words and gift still update only the authorized relationship',async()=>{
  const f=await fixture(),p=f.player(),n=f.npc(p.id);setSpouses(p,['other',n.id]);p.items.set(1,{typeId:'minecraft:poppy',amount:2});
  f.runtime.spouse(p,n);f.forms[0].resolve(0);assert.equal(n.sync.get('fc:love_hate'),81);
  f.runtime.spouse(p,n);f.forms[1].resolve(3);assert.equal(n.sync.get('fc:love_hate'),90);assert.equal(p.items.get(1).amount,1);
  assert.deepEqual(JSON.parse(p.props.get('fc_spouses')),['other',n.id]);assert.equal(n.props.get('fc_spouse_player'),p.id);
});

test('failed required marriage writes roll back before consuming a ring or presenting success',async()=>{
  for(const field of ['owner','married','list','love'])for(const phase of ['before','after']){
    const f=await fixture(),p=f.player(),n=f.npc();setSpouses(p,['existing']);f.runtime.propose(p,n);const before=f.snapshot(p,n);
    const [e,key]=field==='owner'?[n,'setDynamicProperty:fc_spouse_player']:field==='married'?[n,'setProperty:fc:married']:
      field==='list'?[p,'setDynamicProperty:fc_spouses']:[n,'setProperty:fc:love_hate'];f.inject(e.id,key,phase);
    f.operations.length=0;f.forms[0].resolve(0);assert.equal(f.snapshot(p,n),before,`${field}/${phase}`);assert.equal(f.rings(p),2);
    assert.equal(weddingEvents(f).length,0);assert.equal(f.operations.some(op=>['animation','particle','sound'].includes(op[0])),false);
  }
});

test('failed divorce writes restore authorized history and never apply a penalty or neutral reaction',async()=>{
  for(const field of ['owner','married','list','love'])for(const phase of ['before','after']){
    const f=await fixture(),p=f.player(),n=f.npc(p.id);setSpouses(p,['existing',n.id]);f.runtime.divorce(p,n);const before=f.snapshot(p,n);
    const [e,key]=field==='owner'?[n,'setDynamicProperty:fc_spouse_player']:field==='married'?[n,'setProperty:fc:married']:
      field==='list'?[p,'setDynamicProperty:fc_spouses']:[n,'setProperty:fc:love_hate'];f.inject(e.id,key,phase);
    f.operations.length=0;f.forms[0].resolve(0);assert.equal(f.snapshot(p,n),before,`${field}/${phase}`);
    assert.equal(f.operations.some(op=>op[0]==='morality'||op[0]==='event'),false);
  }
});

test('inventory failure before payment restores history; ambiguous consumed payment cannot permit a second marriage',async()=>{
  for(const phase of ['before','after']){
    const f=await fixture(),p=f.player(),n=f.npc();f.runtime.propose(p,n);const before=f.snapshot(p,n);f.inject(p.id,'setItem',phase);
    f.forms[0].resolve(0);assert.equal(weddingEvents(f).length,0);
    if(phase==='before')assert.equal(f.snapshot(p,n),before);
    else {assert.equal(f.rings(p),1);assert.equal(n.props.get('fc_spouse_player'),p.id);assert.equal(n.sync.get('fc:married'),1);
      f.runtime.marry(p,n);assert.equal(f.rings(p),1);assert.equal(weddingEvents(f).length,0);}
  }
});

test('optional presentation failures cannot reopen a successful marriage or consume another ring',async()=>{
  for(const failure of ['animation','sound','name']){
    const f=await fixture(),p=f.player(),n=f.npc();
    if(failure==='name')Object.defineProperty(n,'nameTag',{get:()=> 'Saved name',set(){throw Error('Injected cosmetic name failure');}});
    else f.inject(failure==='sound'?p.id:n.id,failure);
    f.runtime.marry(p,n);f.runtime.marry(p,n);
    assert.equal(f.rings(p),1,failure);assert.equal(n.props.get('fc_spouse_player'),p.id,failure);assert.equal(weddingEvents(f).length,1,failure);
  }
});

test('stable IDs reject older forms through distinct native wrappers and after divorce/remarriage',async()=>{
  const f=await fixture(),p=f.player(),n=f.npc(p.id),otherP={...p},otherN={...n};setSpouses(p,[n.id]);
  f.runtime.spouse(p,n);f.runtime.spouse(otherP,otherN);f.forms[0].resolve(1);
  assert.equal(f.operations.length,0);assert.equal(f.trackedForms(),1);
  f.forms[1].resolve(2);assert.ok(f.operations.some(op=>op[0]==='event'&&op[2]==='fc:react_neutral'));assert.equal(f.trackedForms(),0);
  f.runtime.spouse(p,n);f.runtime.divorce(otherP,otherN);f.forms[3].resolve(0);n.sync.set('fc:love_hate',80);f.runtime.marry(otherP,otherN);
  const before=f.snapshot(p,n);f.operations.length=0;f.forms[2].resolve(1);noAction(f,before,p,n);
  const g=await fixture(),hero=g.player(),resident=g.npc();g.runtime.propose(hero,resident);g.runtime.propose({...hero},{...resident});
  g.forms[0].resolve(0);assert.equal(g.rings(hero),2);g.forms[1].resolve(0);assert.equal(g.rings(hero),1);assert.equal(weddingEvents(g).length,1);
});

test('settled/rejected/cancelled forms clean only their own token; idle registry is bounded and expires',async()=>{
  const f=await fixture(),p=f.player(),n=f.npc(p.id);f.runtime.spouse(p,n);f.runtime.spouse({...p},{...n});
  f.forms[0].reject(Error('Older UI closed'));assert.equal(f.trackedForms(),1);f.forms[1].resolve(5);assert.equal(f.trackedForms(),0);
  for(const ending of ['cancel','reject','accept']){
    f.runtime.spouse(p,n);assert.equal(f.trackedForms(),1);const form=f.forms.at(-1);
    if(ending==='reject')form.reject(Error('UI unavailable'));else form.resolve(5,ending==='cancel');
    assert.equal(f.trackedForms(),0,ending);
  }
  f.runtime.spouse(p,n);f.context.system.currentTick+=2400;f.operations.length=0;f.forms.at(-1).resolve(1);
  assert.equal(f.trackedForms(),0);assert.equal(f.operations.length,0);
  for(let i=0;i<129;i++)f.runtime.spouse(f.player(`visitor-${i}`),f.npc(`visitor-${i}`,`resident-${i}`));
  assert.equal(f.trackedForms(),128);f.operations.length=0;f.forms.at(-129).resolve(1);assert.equal(f.operations.length,0);
  f.context.system.currentTick+=2400;f.runtime.spouse(p,n);assert.equal(f.trackedForms(),1);
});

test('real nonstackable rings debit one exact slot and legacy remainder clones retain metadata',async()=>{
  const asset=JSON.parse(await readFile('packs/Fablecraft_BP/items/wedding_ring.json','utf8'));
  assert.equal(asset['minecraft:item'].components['minecraft:max_stack_size'],1);
  const f=await fixture(),p=f.player(),n=f.npc();p.items.delete(2);p.items.get(0).nameTag='Heirloom';
  assert.equal(p.getComponent('minecraft:inventory').container.getItem(0).maxAmount,1);
  assert.equal(p.getComponent('minecraft:inventory').container.getItem(0).isStackableWith(p.getComponent('minecraft:inventory').container.getItem(0)),false);
  f.runtime.marry(p,n);assert.equal(p.items.has(0),false);assert.equal(weddingEvents(f).length,1);
  const g=await fixture(),hero=g.player(),resident=g.npc();hero.items.set(0,{typeId:'fc:wedding_ring',amount:2,nameTag:'Legacy',lore:['Saved'],dynamic:{history:'retained'}});
  hero.items.delete(2);g.runtime.marry(hero,resident);
  const remaining=hero.items.get(0);assert.equal(remaining.amount,1);assert.equal(remaining.nameTag,'Legacy');assert.deepEqual(remaining.lore,['Saved']);assert.deepEqual(remaining.dynamic,{history:'retained'});
});

test('next-tick synced properties cannot admit a second marriage or divorce before their writes apply',async()=>{
  const f=await fixture({deferredProperties:true}),a=f.player(),b=f.player(),n=f.npc();
  f.runtime.propose(a,n);f.runtime.propose(b,n);f.forms[0].resolve(0);assert.equal(n.sync.get('fc:married'),0);
  f.forms[1].resolve(0);f.runtime.marry(a,n);f.runtime.marry(b,n);assert.equal(weddingEvents(f).length,1);assert.equal(f.rings(a),1);assert.equal(f.rings(b),2);
  f.flushProperties();assert.equal(n.sync.get('fc:married'),1);assert.equal(n.sync.get('fc:love_hate'),100);
  f.runtime.divorce(a,n);f.forms[2].resolve(0);f.runtime.divorce(a,n);assert.equal(f.forms.length,3);assert.equal(n.sync.get('fc:married'),1);
  f.flushProperties();assert.equal(n.sync.get('fc:married'),0);assert.equal(n.props.get('fc_spouse_player'),'');
  assert.equal(f.operations.filter(op=>op[0]==='morality'&&op[2]===-30).length,1);
});

test('next-tick attempted synced writes are explicitly restored on required-write and unpaid-ring failures',async()=>{
  for(const action of ['marry','divorce'])for(const field of ['owner','married','list','love',...(action==='marry'?['ring']:[])])for(const phase of ['before','after']){
    if(field==='ring'&&phase==='after')continue;
    const f=await fixture({deferredProperties:true}),p=f.player(),n=f.npc(action==='divorce'?p.id:'');setSpouses(p,action==='divorce'?['existing',n.id]:['existing']);
    const before=f.snapshot(p,n);if(action==='divorce')f.runtime.divorce(p,n);
    const [e,key]=field==='owner'?[n,'setDynamicProperty:fc_spouse_player']:field==='married'?[n,'setProperty:fc:married']:
      field==='list'?[p,'setDynamicProperty:fc_spouses']:field==='love'?[n,'setProperty:fc:love_hate']:[p,'setItem'];f.inject(e.id,key,phase);
    if(action==='marry')f.runtime.marry(p,n);else f.forms[0].resolve(0);
    f.flushProperties();assert.equal(f.snapshot(p,n),before,`${action}/${field}/${phase}`);
    assert.equal(f.operations.some(op=>op[0]==='morality'||op[0]==='event'),false);
  }
});

test('unreadable rollback retains reserved ownership and cannot reopen marriage or erase unrelated history',async()=>{
  const f=await fixture({deferredProperties:true}),p=f.player(),other=f.player(),n=f.npc();setSpouses(p,['existing']);
  f.inject(p.id,'setDynamicProperty:fc_spouses','after');f.inject(p.id,'getDynamicProperty:fc_spouses','before',0);
  const original=p.setDynamicProperty;p.setDynamicProperty=(key,value)=>{try{return original(key,value);}catch(error){f.inject(p.id,'getDynamicProperty:fc_spouses','before',100);throw error;}};
  f.runtime.marry(p,n);f.flushProperties();assert.equal(n.props.get('fc_spouse_player'),p.id);assert.equal(f.rings(p),2);assert.equal(weddingEvents(f).length,0);
  assert.deepEqual(JSON.parse(p.props.get('fc_spouses')),['existing',n.id]);f.runtime.marry(other,n);assert.equal(n.props.get('fc_spouse_player'),p.id);assert.equal(f.rings(other),2);
});

test('changed payment slots and unconfirmed inventory writes suppress success with bounded authority restoration',async()=>{
  for(const outcome of ['changed_before','ignored','unreadable_before','unreadable_after']){
    const f=await fixture({deferredProperties:true}),p=f.player(),n=f.npc();setSpouses(p,['existing']);
    const getComponent=p.getComponent;let debit=false;
    p.getComponent=name=>{const result=getComponent(name);if(!result)return result;const original=result.container;
      return {container:{size:original.size,getItem(slot){if(debit&&outcome.startsWith('unreadable'))throw Error('Unavailable payment readback');return original.getItem(slot);},
        setItem(slot,item){debit=true;if(outcome==='ignored')return;if(outcome==='unreadable_before')throw Error('Unavailable payment');original.setItem(slot,item);}}};};
    if(outcome==='changed_before'){
      const set=n.setDynamicProperty;n.setDynamicProperty=(key,value)=>{set(key,value);if(key==='fc_spouse_player'&&value===p.id)p.items.delete(0);};
    }
    f.runtime.marry(p,n);f.flushProperties();assert.equal(weddingEvents(f).length,0,outcome);
    if(outcome==='changed_before'||outcome==='ignored'){
      assert.equal(n.sync.get('fc:married'),0,outcome);assert.equal(n.props.get('fc_spouse_player'),'',outcome);assert.deepEqual(JSON.parse(p.props.get('fc_spouses')),['existing']);
    }else{
      assert.equal(n.props.get('fc_spouse_player'),p.id,outcome);assert.equal(n.sync.get('fc:married'),1,outcome);
      const before=f.rings(p);f.runtime.marry(p,n);assert.equal(f.rings(p),before,outcome);
    }
  }
});

test('a successful proposal keeps the production training interruption owner and preserved resident identity',async()=>{
  const f=await fixture(),p=f.player(),n=f.npc();f.ctl.beginPass([n]);const token=f.ctl.acquire(n,'fc_train_range',n.location,{x:83.5,y:2.45,z:34.5});
  assert.notEqual(token,null);f.runtime.propose(p,n);f.forms[0].resolve(0);
  assert.equal(f.ctl.isActive(n,token),false);assert.equal(n.hasTag('fc_guild_following'),true);assert.equal(n.props.get('fc_guild_resident_slot'),'skill_range');
});

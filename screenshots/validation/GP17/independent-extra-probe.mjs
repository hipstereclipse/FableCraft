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

let checked=0;
for(const field of ['married','love','spouses'])for(let choice=0;choice<=4;choice++){
 const f=await fixture({deferredProperties:true}),p=f.player(),n=f.npc(p.id);setSpouses(p,[n.id]);p.items.set(1,{typeId:'minecraft:poppy',amount:1});f.runtime.spouse(p,n);
 const [e,key]=field==='spouses'?[p,'getDynamicProperty:fc_spouses']:[n,'getProperty:fc:'+ (field==='married'?'married':'love_hate')];
 f.inject(e.id,key,'before',100);const before=f.snapshot(p,n);f.operations.length=0;f.forms[0].resolve(choice);f.flushProperties();
 noAction(f,before,p,n,`${field}/${choice}`);assert.equal(f.forms.length,1);checked++;
}
{
 const f=await fixture({deferredProperties:true}),p=f.player(),n=f.npc();const original=p.getComponent;
 p.getComponent=name=>{const result=original(name);if(result?.container)result.container.setItem=()=>{};return result;};
 const before=f.snapshot(p,n);assert.equal(f.runtime.marry(p,n),false);f.flushProperties();assert.equal(f.snapshot(p,n),before);assert.equal(weddingEvents(f).length,0);checked++;
}
{
 const f=await fixture({deferredProperties:true}),p=f.player(),other=f.player(),n=f.npc();const original=p.getComponent;
 p.getComponent=name=>{const result=original(name);if(result?.container){const set=result.container.setItem;result.container.setItem=(slot,item)=>{set(slot,item);f.inject(p.id,'getItem','before',100);};}return result;};
 assert.equal(f.runtime.marry(p,n),false);f.flushProperties();assert.equal(f.rings(p),1);assert.equal(n.props.get('fc_spouse_player'),p.id);assert.equal(n.sync.get('fc:married'),1);assert.equal(weddingEvents(f).length,0);
 assert.equal(f.runtime.marry(other,n),false);assert.equal(f.rings(other),2);assert.equal(n.props.get('fc_spouse_player'),p.id);checked++;
}
console.log(JSON.stringify({independent_extra_cases:checked,unreadable_spouse_choice_cases:15,silent_inventory_refusal_rollback:'pass',unreadable_post_debit_confirmation_keeps_authority:'pass',native:'unrun'}));

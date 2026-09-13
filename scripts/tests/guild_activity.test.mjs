// Actual activity, residence and training owners; Bedrock persistence/events mocked.
import test from 'node:test';
import assert from 'node:assert/strict';
import vm from 'node:vm';
import {readFile} from 'node:fs/promises';
const sources=Object.fromEntries(await Promise.all(['guild_activity','guild_residents','guild_training'].map(async name=>[name,await readFile(`packs/Fablecraft_BP/scripts/${name}.js`,'utf8')])));
async function fixture(){
  const api={};const context=vm.createContext({});
  for(const [name,source] of Object.entries(sources)){const module=new vm.SourceTextModule(source,{context});await module.link(()=>{throw Error('Controller must remain injected');});await module.evaluate();api[name]=module.namespace;}
  let tick=10,journal,witness,registry,ctl;
  const events=[],writes=[],entities=[],heroes=[],faults=new Map();
  const base={x:10,y:20,z:30};
  const slots=[{id:'skill_range',type:'fc:guild_apprentice_skill'},{id:'skill_hall',type:'fc:guild_apprentice_skill'}];
  function fail(key,phase='before'){const f=faults.get(key);if(f?.phase===phase&&!(f.skip-->0)&&f.count-->0)throw Error(`${phase}:${key}`);}
  const dimension={id:'minecraft:overworld',getBlock:p=>({typeId:p.y===20?'minecraft:coarse_dirt':'minecraft:air',isAir:p.y!==20})};
  function actor(id,type='minecraft:player'){
    const tags=new Set(),props=new Map(),sync=new Map([['fc:married',0],['fc:love_hate',80]]);
    return {id,typeId:type,isValid:true,dimension,location:{x:83.5,y:21,z:39.5},tags,props,sync,nameTag:'Saved name',movement:.34,
      hasTag(tag){fail(`${id}:hasTag:${tag}`);return tags.has(tag);},getTags(){return [...tags];},
      addTag(tag){fail(`${id}:addTag:${tag}`);events.push(['tag+',id,tag]);tags.add(tag);fail(`${id}:addTag:${tag}`,'after');},
      removeTag(tag){fail(`${id}:removeTag:${tag}`);events.push(['tag-',id,tag]);tags.delete(tag);fail(`${id}:removeTag:${tag}`,'after');},
      getProperty(key){fail(`${id}:getProperty:${key}`);return sync.get(key);},getDynamicProperty(key){fail(`${id}:getDynamicProperty:${key}`);return props.get(key);},
      setDynamicProperty(){throw Error('Activity must not rewrite resident history');},
      triggerEvent(event){fail(`${id}:event:${event}`);events.push(['event',id,event,tick]);
        if(['fc:guild_activity_stop','fc:guild_training_stop'].includes(event))this.movement=.34;
        if(['fc:guild_activity_wait','fc:guild_training_start'].includes(event))this.movement=0;
        fail(`${id}:event:${event}`,'after');},
      tryTeleport(p){this.location={...p};events.push(['placement',id]);return true;},
    };
  }
  const npcs=slots.map((slot,i)=>{const n=actor(`npc-${i}`,slot.type);n.props.set('fc_guild_resident_slot',`10,20,30/${slot.id}`);n.props.set('fc_spouse_player','');n.props.set('fc_saved_history','retained');entities.push(n);return n;});
  registry=JSON.stringify({schema:1,origin:'fresh',base,residents:slots.map((slot,i)=>({slot:slot.id,type:slot.type,status:'bound',entityId:npcs[i].id,provenance:'spawn'}))});
  const residents=api.guild_residents.createGuildResidentsController({slots,read:()=>{fail('registry-read');return registry;},write(){throw Error('Read-only resolver wrote roster');},lookup(){},candidates:()=>[],spawnPoint(){},spawn(){throw Error('Activity spawned entity');},onCampus:()=>true});
  const training=api.guild_training.createGuildTrainingController({now:()=>tick,session:()=>Math.floor(tick/3600),canTrain:e=>!ctl?.reserved(e)});
  const options={now:()=>tick,base:()=>base,resolve:e=>residents.binding(e,base),
    read:()=>{fail('journal-read');return journal;},write:raw=>{fail('journal-write');writes.push(['journal',JSON.parse(raw)]);journal=raw;fail('journal-write','after');},
    readWitness:()=>{fail('witness-read');return witness;},writeWitness:value=>{fail('witness-write');writes.push(['witness',value]);witness=value;fail('witness-write','after');},
    lookup:id=>{fail('lookup');return entities.find(e=>e.id===id&&e.isValid);},players:()=>{fail('players');return heroes.filter(p=>p.isValid);},
    stopTraining:e=>{fail('stopTraining');training.interrupt(e);return !training.reserved(e);},trainingReserved:e=>training.reserved(e)};
  const create=()=>api.guild_activity.createGuildActivityController(options);ctl=create();
  function player(id=`hero-${heroes.length}`){const p=actor(id);heroes.push(p);return p;}
  return {api,ctl,options,residents,training,npcs,entities,heroes,events,writes,base,dimension,player,
    advance(n=1){tick+=n;},restart(){ctl=create();this.ctl=ctl;return ctl;},pass(){ctl.reconcile(npcs.filter(e=>e.isValid));},
    fault(key,phase='before',count=1,skip=0){faults.set(key,{phase,count,skip});},clearFaults(){faults.clear();},
    raw:()=>journal,witness:()=>witness,state:()=>JSON.parse(journal),setRaw:v=>{journal=v;},setWitness:v=>{witness=v;},
    registry:()=>registry,setRegistry:v=>{registry=v;},
    history:n=>JSON.stringify({props:[...n.props],sync:[...n.sync],name:n.nameTag}),
  };
}
function start(f,n,p,mode='follow',options={}){const result=f.ctl.request(n,p,mode,options);assert.equal(result.accepted,true,result.reason);assert.equal(result.pending,true);f.advance();f.pass();assert.equal(f.ctl.status(n).mode,mode);assert.equal(f.ctl.status(n).blocked,false);}

test('witness and exact roster bindings precede any native channel permission',async()=>{
  const f=await fixture();f.pass();assert.equal(f.writes[0][0],'witness');assert.equal(f.witness(),true);assert.equal(f.state().channels.skill_range.entityId,f.npcs[0].id);
  assert.equal(f.state().channels.skill_hall.entityId,f.npcs[1].id);assert.equal(f.ctl.status(f.npcs[0]).blocked,false);
  assert.equal(f.events.some(e=>e[0]==='tag+'),false);assert.equal(f.residents.snapshot().state,undefined,'Resolver did not initialize/mutate cached roster');
});

test('independent Heroes acquire only their canonical channel after a native-stop tick barrier',async()=>{
  const f=await fixture();f.pass();const a=f.player(),b=f.player(),[x,y]=f.npcs;const history=f.history(x);
  for(const [n,p] of [[x,a],[y,b]])assert.equal(f.ctl.request(n,p,'follow').accepted,true);
  f.pass();assert.equal(a.tags.size,0);assert.equal(b.tags.size,0);assert.equal(f.ctl.status(x).blocked,true);
  f.advance();f.pass();assert.equal(a.hasTag('fc_skill_range_requester_v1'),true);assert.equal(a.hasTag('fc_skill_hall_requester_v1'),false);
  assert.equal(b.hasTag('fc_skill_hall_requester_v1'),true);assert.equal(b.hasTag('fc_skill_range_requester_v1'),false);assert.equal(f.history(x),history);
  assert.equal(x.hasTag('fc_guild_following'),true);assert.equal(f.ctl.request(x,b,'follow').accepted,false);
  const grant=f.writes.findIndex(w=>w[0]==='journal'&&w[1].channels.skill_range.pendingTagHolders.includes(a.id));assert.ok(grant>=0);
  const firstNative=f.events.find(e=>e[0]==='event'&&e[2]==='fc:guild_activity_follow_range');assert.equal(firstNative[3],11);
});

test('owned Wait holds movement, blocks unrelated requesters, and release restores movement/history',async()=>{
  const f=await fixture();f.pass();const a=f.player(),b=f.player(),n=f.npcs[0],history=f.history(n);start(f,n,a);
  assert.equal(f.ctl.request(n,b,'wait').accepted,false);start(f,n,a,'wait');assert.equal(n.movement,0);assert.equal(n.hasTag('fc_guild_activity_wait_v1'),true);
  assert.equal(a.hasTag('fc_skill_range_requester_v1'),false);assert.equal(f.ctl.reserved(n),true);
  assert.equal(f.ctl.request(n,a,'idle').accepted,true);assert.equal(n.movement,.34);assert.equal(f.ctl.reserved(n),false);assert.equal(f.history(n),history);
  assert.equal(f.ctl.request(f.npcs[1],a,'wait').accepted,false);assert.equal(f.ctl.request(f.npcs[1],a,'wait',{acquireWait:true}).accepted,false);f.npcs[1].sync.set('fc:married',1);f.npcs[1].props.set('fc_spouse_player',a.id);start(f,f.npcs[1],a,'wait',{acquireWait:true});
});

test('idle reconciliation never repeatedly cancels training; activation waits for actual training cleanup',async()=>{
  const f=await fixture();f.pass();const n=f.npcs[0],a=f.player();f.advance(3600);f.training.beginPass(f.npcs);const token=f.training.acquire(n,'fc_train_range',n.location,{x:83.5,y:22,z:34.5});assert.notEqual(token,null);
  f.events.length=0;f.pass();assert.equal(f.training.isActive(n,token),true);assert.equal(n.movement,0);assert.equal(f.events.length,0);
  start(f,n,a,'follow');start(f,n,a,'wait');assert.equal(f.training.isActive(n,token),false);assert.equal(n.movement,0);
  f.training.beginPass(f.npcs);assert.equal(n.movement,0);assert.equal(f.training.eligible(n),false);
  const g=await fixture();g.pass();const p=g.player();g.fault('stopTraining');assert.equal(g.ctl.request(g.npcs[0],p,'follow').accepted,false);assert.equal(p.tags.size,0);assert.equal(g.ctl.reserved(g.npcs[0]),true);
});

test('disconnect keeps holder debt and forbids reassignment until reconnect cleanup is verified',async()=>{
  const f=await fixture();f.pass();const a=f.player(),b=f.player(),n=f.npcs[0];start(f,n,a);a.isValid=false;f.pass();
  assert.equal(f.state().channels.skill_range.mode,'stopping');assert.deepEqual(f.state().channels.skill_range.pendingTagHolders,[a.id]);assert.equal(n.movement,.34);
  assert.equal(f.ctl.request(n,b,'follow').accepted,false);f.restart();f.pass();assert.equal(f.ctl.request(n,b,'follow').accepted,false);
  a.isValid=true;f.pass();assert.equal(a.hasTag('fc_skill_range_requester_v1'),false);assert.equal(f.state().channels.skill_range.mode,'idle');start(f,n,b);
  assert.equal(a.hasTag('fc_skill_range_requester_v1'),false);assert.equal(b.hasTag('fc_skill_range_requester_v1'),true);
});

test('unload and reload reconcile saved Follow/Wait without resurrection or replacement residents',async()=>{
  for(const mode of ['follow','wait']){
    const f=await fixture();f.pass();const p=f.player(),n=f.npcs[0];if(mode==='wait'){n.sync.set('fc:married',1);n.props.set('fc_spouse_player',p.id);}start(f,n,p,mode,{acquireWait:true});const old=f.ctl.status(n).revision;
    n.isValid=false;f.pass();assert.equal(f.state().channels.skill_range.mode,'stopping');assert.equal(f.ctl.valid(n,old),false);
    f.restart();n.isValid=true;f.pass();assert.equal(f.state().channels.skill_range.mode,'idle');assert.equal(n.hasTag('fc_guild_activity_owned_v1'),false);
    f.events.length=0;f.advance();f.pass();assert.equal(f.events.some(e=>e[0]==='event'&&e[2].includes('follow')),false);assert.equal(f.entities.length,2);
  }
});

test('queued activation rechecks generation, wrapper IDs, marriage, dimension and defensive state',async()=>{
  for(const change of ['married','unreadable','dimension','invalid','defending','aggravated','distance','preempt']){
    const f=await fixture();f.pass();const p=f.player(),n=f.npcs[0];assert.equal(f.ctl.request(n,p,'follow').accepted,true);const old=f.ctl.status(n).revision;
    if(change==='married'){n.sync.set('fc:married',1);n.props.set('fc_spouse_player','other');}
    if(change==='unreadable')f.fault(`${n.id}:getProperty:fc:married`,'before',20);
    if(change==='dimension')p.dimension={id:'minecraft:nether'};
    if(change==='invalid')p.isValid=false;
    if(change==='defending')n.tags.add('fc_guild_defending');if(change==='aggravated')n.tags.add('fc_aggravated');
    if(change==='distance')p.location={x:1000,y:21,z:39};if(change==='preempt')f.ctl.preempt(n);
    f.advance();f.pass();assert.equal(p.hasTag('fc_skill_range_requester_v1'),false,change);assert.equal(n.hasTag('fc_guild_activity_owned_v1'),false,change);assert.equal(f.ctl.valid(n,old),false,change);
  }
  const f=await fixture();f.pass();const p=f.player(),n=f.npcs[0];start(f,n,p);const old=f.ctl.status(n).revision;
  assert.equal(f.ctl.request({...n},{...p},'wait',{expectedRevision:old}).accepted,true);assert.equal(f.ctl.request(n,p,'follow',{expectedRevision:old}).accepted,false);
});

test('defence preemption restores Wait despite tag errors and retains retry obligations',async()=>{
  const f=await fixture();f.pass();const p=f.player(),n=f.npcs[0];n.sync.set('fc:married',1);n.props.set('fc_spouse_player',p.id);start(f,n,p,'wait',{acquireWait:true});const old=f.ctl.status(n).revision;
  f.fault(`${n.id}:removeTag:fc_guild_activity_wait_v1`,'before',10);assert.equal(f.ctl.preempt(n),false);assert.equal(n.movement,.34);assert.equal(f.ctl.valid(n,old),false);assert.equal(f.ctl.reserved(n),true);
  f.clearFaults();f.pass();assert.equal(n.hasTag('fc_guild_activity_wait_v1'),false);assert.equal(f.ctl.reserved(n),false);
});

test('missing established journal, malformed history and witness/read failures never become empty authority',async()=>{
  for(const damage of ['missing','json','holders','witness','read']){
    const f=await fixture();f.pass();const p=f.player();
    if(damage==='missing')f.setRaw(undefined);if(damage==='json')f.setRaw('{broken');
    if(damage==='holders'){const saved=f.state();saved.channels.skill_range.pendingTagHolders=['lost'];f.setRaw(JSON.stringify(saved));}
    if(damage==='witness')f.setWitness('true');if(damage==='read')f.fault('journal-read','before',100);
    const before=f.raw();assert.equal(f.ctl.request(f.npcs[0],p,'follow').accepted,false);f.pass();assert.equal(f.raw(),before,damage);assert.equal(p.tags.size,0,damage);
  }
  for(const key of ['witness-write','journal-write']){
    const f=await fixture();const p=f.player();f.fault(key,'after');assert.equal(f.ctl.request(f.npcs[0],p,'follow').accepted,false);assert.equal(p.tags.size,0);
    if(key==='witness-write'){assert.equal(f.witness(),true);assert.equal(f.raw(),undefined);assert.equal(f.ctl.request(f.npcs[0],p,'follow').accepted,false);}
  }
});

test('strict fresh roster resolver rejects cached saves, copied markers and wrong identity without writes',async()=>{
  const f=await fixture();f.pass();const n=f.npcs[0],p=f.player(),registry=f.registry();const oldWrites=f.writes.length;
  const clone={...n,id:'copied'};assert.equal(f.ctl.status(clone).managed,true);assert.equal(f.ctl.status(clone).blocked,true);assert.equal(f.ctl.request(clone,p,'follow').accepted,false);
  for(const damage of ['malformed','dead','base','duplicate']){
    const saved=JSON.parse(registry);if(damage==='dead')saved.residents[0].status='dead';if(damage==='base')saved.base.x++;
    if(damage==='duplicate')saved.residents[1].entityId=saved.residents[0].entityId;
    f.setRegistry(damage==='malformed'?'{bad':JSON.stringify(saved));assert.equal(f.ctl.request(n,p,'follow').accepted,false,damage);
  }
  assert.equal(f.writes.length,oldWrites);f.setRegistry(registry);assert.equal(f.residents.binding(n,f.base).kind,'bound');
});

test('active duplicate/missing channel tags or NPC marker drift stop native Follow without resurrection',async()=>{
  for(const fault of ['duplicate','missing','owned','wait','unreadable']){
    const f=await fixture();f.pass();const a=f.player(),b=f.player(),n=f.npcs[0];start(f,n,a);
    if(fault==='duplicate')b.tags.add('fc_skill_range_requester_v1');if(fault==='missing')a.tags.delete('fc_skill_range_requester_v1');
    if(fault==='owned')n.tags.delete('fc_guild_activity_owned_v1');if(fault==='wait')n.tags.add('fc_guild_activity_wait_v1');
    if(fault==='unreadable')f.fault(`${b.id}:hasTag:fc_skill_range_requester_v1`,'before',20);
    assert.equal(f.ctl.status(n).blocked,true,fault);f.pass();assert.equal(n.hasTag('fc_guild_activity_owned_v1'),false,fault);
    f.clearFaults();f.advance();f.pass();assert.equal(n.hasTag('fc_guild_following'),false,fault);assert.equal(a.hasTag('fc_skill_range_requester_v1'),false,fault);
  }
});

test('unavailable or conflicting fresh identity still stops the loaded durable resident and never falls through',async()=>{
  for(const damage of ['registry','journal','marker','lost-binding','replacement']){
    const f=await fixture();f.pass();const p=f.player(),n=f.npcs[0];start(f,n,p);const saved=JSON.parse(f.registry());
    if(damage==='registry')f.setRegistry('{bad');if(damage==='journal')f.setRaw('{bad');if(damage==='marker')n.props.delete('fc_guild_resident_slot');
    if(damage==='lost-binding'){saved.residents[0]={slot:'skill_range',type:n.typeId,status:'unknown'};saved.origin='legacy';f.setRegistry(JSON.stringify(saved));n.props.delete('fc_guild_resident_slot');}
    if(damage==='replacement'){
      const replacement={...n,id:'replacement',tags:new Set()};saved.residents[0].entityId=replacement.id;f.setRegistry(JSON.stringify(saved));
      f.events.length=0;f.ctl.reconcile([replacement,f.npcs[1]]);assert.ok(f.events.some(e=>e[0]==='event'&&e[1]===n.id&&e[2]==='fc:guild_activity_stop'));continue;
    }
    assert.equal(f.ctl.status(n).managed,true,damage);assert.equal(f.ctl.request(n,p,'follow').handled,true,damage);f.pass();assert.equal(n.hasTag('fc_guild_activity_owned_v1'),false,damage);
  }
});

test('failed request/preempt revision persistence cannot revive captured idle callbacks on retry',async()=>{
  for(const action of ['request','preempt'])for(const phase of ['before','after']){
    const f=await fixture();f.pass();const p=f.player(),n=f.npcs[0],old=f.ctl.status(n).revision;f.fault('journal-write',phase);
    if(action==='request')assert.equal(f.ctl.request(n,p,'follow').accepted,false);else assert.equal(f.ctl.preempt(n),false);
    assert.equal(f.ctl.valid(n,old),false,`${action}/${phase}`);f.pass();assert.equal(f.ctl.valid(n,old),false,`${action}/${phase}`);
    assert.ok(f.ctl.status(n).revision>old);
  }
  const f=await fixture();f.pass();const n=f.npcs[0],old=f.ctl.status(n).revision;assert.equal(f.ctl.preempt(n),true);assert.ok(f.ctl.status(n).revision>old);
});

test('unreadable or unsaved discovered holder debt survives disconnect and cleans reachable holders fairly',async()=>{
  for(const fault of ['tag-read','holder-save','stop-save']){
    const f=await fixture();f.pass();const a=f.player(),b=f.player(),c=f.player(),n=f.npcs[0];start(f,n,a);b.tags.add('fc_skill_range_requester_v1');
    if(fault==='tag-read')f.fault(`${b.id}:hasTag:fc_skill_range_requester_v1`,'before',100);
    else f.fault('journal-write','before',1,fault==='holder-save'?1:0);
    f.pass();b.isValid=false;f.clearFaults();f.pass();assert.equal(f.state().channels.skill_range.mode,'stopping',fault);
    assert.ok(f.state().channels.skill_range.pendingTagHolders.includes(b.id),fault);assert.equal(f.ctl.request(n,c,'follow').accepted,false,fault);
    // A later live unexpected holder is cleaned even when offline B appears first.
    c.tags.add('fc_skill_range_requester_v1');f.pass();assert.equal(c.tags.has('fc_skill_range_requester_v1'),false,fault);
    b.isValid=true;f.pass();assert.equal(f.state().channels.skill_range.mode,'idle');start(f,n,c);
  }
});

test('exhausted persisted revisions stop native effects while keeping authority blocked',async()=>{
  for(const mode of ['follow','wait']){
    const f=await fixture();f.pass();const p=f.player(),n=f.npcs[0];if(mode==='wait'){n.sync.set('fc:married',1);n.props.set('fc_spouse_player',p.id);}start(f,n,p,mode,{acquireWait:true});
    const saved=f.state();saved.channels.skill_range.revision=Number.MAX_SAFE_INTEGER;f.setRaw(JSON.stringify(saved));f.restart();f.pass();
    assert.equal(n.hasTag('fc_guild_activity_owned_v1'),false,mode);assert.equal(n.movement,.34,mode);assert.equal(f.ctl.status(n).blocked,true,mode);
    assert.equal(f.ctl.valid(n,Number.MAX_SAFE_INTEGER),false,mode);assert.equal(f.ctl.request(n,p,'follow').accepted,false,mode);
  }
});

test('holder overflow remains quarantined across failed persistence, cleared tags and reload',async()=>{
  const f=await fixture();f.pass();const owner=f.player(),n=f.npcs[0];start(f,n,owner);
  const tag='fc_skill_range_requester_v1',old=f.ctl.status(n).revision;
  const extras=Array.from({length:80},()=>f.player());for(const p of extras)p.tags.add(tag);
  f.fault('journal-write','before',100);f.pass();assert.equal(n.hasTag('fc_guild_activity_owned_v1'),false);
  assert.equal(f.ctl.valid(n,old),false);assert.equal(f.ctl.request(n,owner,'follow').accepted,false);
  // Overflow obligations cannot vanish when those unverified Heroes leave.
  for(const p of extras)p.isValid=false;f.clearFaults();f.pass();
  assert.equal(f.state().channels.skill_range.holderOverflow,true);
  assert.ok(f.state().channels.skill_range.pendingTagHolders.length<=64);
  // Even externally clearing every tag is insufficient proof for automatic reuse.
  for(const p of [owner,...extras]){p.tags.delete(tag);p.isValid=true;}
  f.pass();f.restart();f.pass();
  assert.equal(f.state().channels.skill_range.holderOverflow,true);assert.equal(f.ctl.reserved(n),true);
  assert.equal(f.ctl.request(n,owner,'follow').accepted,false);assert.equal(n.movement,.34);
  assert.equal(f.ctl.status(f.npcs[1]).blocked,false,'Independent channel remains available');
});

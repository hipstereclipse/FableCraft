import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {execFileSync} from 'node:child_process';
import vm from 'node:vm';
const root=new URL('../../',import.meta.url);
const code=readFileSync(new URL('packs/Fablecraft_BP/scripts/arboretum_doors.js',root),'utf8');
const module=new vm.SourceTextModule(code,{context:vm.createContext({})});
await module.link(()=>{throw Error('The Arboretum must inject engine effects');});await module.evaluate();
const {createArboretumDoors,ARBORETUM,ARBORETUM_INDEX_KEY:INDEX,ARBORETUM_WITNESS_KEY:WITNESS,
  ARBORETUM_RETURN_KEY:TICKET,arboretumStateKey:stateKey,arboretumCellKey:cellKey,arboretumOrigin:origin,inArboretum}=module.namespace;
// Execute the actual current owned builder once. No fixture imitates its room.
const geometry=JSON.parse(execFileSync('python',['-c',
  "import sys,json;sys.path.insert(0,'scripts');from gen_structures import Vox;from door_realms import build_arboretum;Vox.save=lambda *args:None;v=build_arboretum(Vox);print(json.dumps({'size':[v.sx,v.sy,v.sz],'grid':v.grid,'palette':[p[0] for p in v.palette]}))"],{cwd:root,encoding:'utf8',stdio:['ignore','pipe','pipe'],maxBuffer:4*1024*1024}));
const plain=v=>JSON.parse(JSON.stringify(v)),key=p=>`${Math.floor(p.x)},${Math.floor(p.y)},${Math.floor(p.z)}`;
const add=(a,b)=>({x:a.x+b.x,y:a.y+b.y,z:a.z+b.z});
const offset=(p,x=0,y=0,z=0)=>({...p,x:p.x+x,y:p.y+y,z:p.z+z});
function fixture(){
 const props=new Map(),blocks=new Map(),players=[],commands=[],places=[],reports=[],writes=[],particles=[],seeds=[];
 const activeLeases=new Map(),system={currentTick:0};
 const flags={source:true,witness:true,entry:true,loaded:true,lease:true,teleport:'ok',place:'ok',seed:'ok',entities:[],reads:new Set(),worldWrite:null,damage:null,prefill:false};
 const block=(typeId='minecraft:air',container=null)=>({typeId,isAir:typeId==='minecraft:air',getComponent:id=>id==='minecraft:inventory'&&container?{container}:undefined});
 function container(){const slots=new Map();return {size:27,slots,getItem:i=>slots.get(i),setItem(i,v){if(flags.seed==='before')throw Error('seed before');seeds.push(v);if(flags.seed==='ignore')return;if(flags.seed==='wrong')v={typeId:'minecraft:diamond',amount:1};if(flags.seed==='count')v={...v,amount:2};v?slots.set(i,v):slots.delete(i);if(flags.seed==='after')throw Error('seed after');}};}
 const dims={};
 for(const id of ['minecraft:overworld','minecraft:nether','minecraft:the_end'])dims[id]={id,
  getBlock(p){if(p.x>=620000&&!flags.loaded)return undefined;return blocks.get(id+'/'+key(p))??block(p.x<620000&&Math.floor(p.y)===69?'minecraft:grass_block':'minecraft:air');},
  getEntities(){if(flags.entities==='throw')throw Error('unreadable entities');return flags.entities;},
  runCommand(command){commands.push({id,command});const name=command.split(' ').at(-2)==='true'?command.split(' ').at(-2):command.split(' ').at(-1);
   if(command.startsWith('tickingarea add')){if(!flags.lease)throw Error('no loading authority');activeLeases.set(command.split(' ').at(-2),id);}
   else activeLeases.delete(name);return {successCount:1};},
  spawnParticle(name,p){particles.push({id,name,p:plain(p)});}};
 const world={getPlayers:()=>players,getDimension:id=>{if(!dims[id])throw Error('bad dimension');return dims[id];},
  getDynamicPropertyIds:()=>[...props.keys()],
  getDynamicProperty(k){if(flags.reads.has(k))throw Error('world read');return props.get(k);},
  setDynamicProperty(k,v){const mode=flags.worldWrite?.(k,v);if(mode==='before')throw Error('world write before');writes.push({k,v});v===undefined?props.delete(k):props.set(k,v);if(mode==='after')throw Error('world write after');},
  structureManager:{place(id,d,o){assert.equal(id,ARBORETUM.id);placeRoom(d,o);}}};
 function placeRoom(d,o){if(flags.place==='before')throw Error('place before');places.push(plain(o));
  for(let i=0;i<geometry.grid.length;i++){const p=add(o,{x:Math.floor(i/(28*49)),y:Math.floor(i/49)%28,z:i%49}),type=geometry.palette[geometry.grid[i]];
   const c=type==='minecraft:chest'?container():null;if(c&&flags.prefill)c.slots.set(8,{typeId:'minecraft:diamond',amount:1});blocks.set(d.id+'/'+key(p),block(type,c));}
  if(flags.damage)blocks.set(d.id+'/'+key(add(o,flags.damage.at)),block(flags.damage.type));
  if(flags.place==='after')throw Error('place after');}
 class ItemStack{constructor(typeId,amount){this.typeId=typeId;this.amount=amount;}}
 function player(id=`hero${players.length}`,at={x:132.5,y:70,z:206.5},dimension='minecraft:overworld'){
  const properties=new Map(),moves=[],playerWrites=[];
  const p={id,typeId:'minecraft:player',isValid:true,dimension:dims[dimension],location:plain(at),alignment:null,properties,moves,playerWrites,unreadable:false,writeFault:null,
   getDynamicProperty(k){if(p.unreadable&&k===TICKET)throw Error('ticket unavailable');return properties.get(k);},
   setDynamicProperty(k,v){const mode=p.writeFault?.(k,v);if(mode==='before')throw Error('player write before');playerWrites.push({k,v});v===undefined?properties.delete(k):properties.set(k,v);if(mode==='after')throw Error('player write after');},
   sendMessage(){},playSound(){},tryTeleport(at,options){moves.push({at:plain(at),options});if(flags.teleport==='false')return false;if(flags.teleport==='before')throw Error('teleport before');p.location=plain(at);p.dimension=options.dimension;if(flags.teleport==='after')throw Error('teleport after');return true;}};
  players.push(p);return p;
 }
 function face(r){const properties=new Map(),events=[],moves=[];return {id:'face/'+r.id,typeId:'fc:demon_door',isValid:true,dimension:dims[r.source.dimension],location:plain(r.source),properties,events,moves,
  getDynamicProperty:k=>properties.get(k),setDynamicProperty:(k,v)=>properties.set(k,v),triggerEvent:id=>events.push(id),teleport(at){moves.push(plain(at));this.location=plain(at);}};}
 let ctl;
 const volumeIsBlock=(d,o,s,type)=>{for(let x=0;x<s.x;x++)for(let y=0;y<s.y;y++)for(let z=0;z<s.z;z++)if(d.getBlock(add(o,{x,y,z}))?.typeId!==type)return false;return true;};
 const reload=()=>ctl=createArboretumDoors({world,system,ItemStack,placeRoom,sourceReady:()=>flags.source,canEnter:()=>flags.entry,
  canWitnessUse:()=>flags.witness,readAlignment:p=>p.alignment,volumeIsBlock,volumeIsEmpty:(d,o,s)=>volumeIsBlock(d,o,s,'minecraft:air'),report:s=>reports.push(s)});
 const step=(n=1)=>{for(let i=0;i<n;i++){system.currentTick+=5;ctl.tick();}};
 const state=id=>plain(ctl.getState(id));
 function register(n=0,dimension='minecraft:overworld'){
  const id=ctl.beginPlacement({regionKey:`fc_rgn_${n}_0`,origin:{x:100+n*100,y:64,z:200,dimension}});assert.ok(id);
  assert.equal(ctl.confirmPlacement(id),false,'geometry cannot replace successful placement receipt');
  assert.equal(ctl.recordPlaced(id),true);assert.equal(ctl.confirmPlacement(id),true);return state(id);
 }
 function open(r,p=player(undefined,offset(r.source,0,0,-1),r.source.dimension)){
  const door=face(r);p.alignment=-1000;assert.equal(ctl.interact(p,door),true);assert.equal(state(r.id).unlocked,true);return {p,door};
 }
 function build(r,p){const result=open(r,p);for(let i=0;i<650&&state(r.id).room.phase!=='ready';i++)step();assert.equal(state(r.id).room.phase,'ready',reports.join('\n'));return result;}
 function enter(p,r){p.dimension=dims[r.source.dimension];p.location=offset(r.source,2.1,0,-4.5);step(14);p.location=plain(r.source);for(let i=0;i<250&&!ctl.occupiedRealm(p);i++)step();assert.equal(ctl.occupiedRealm(p),true,reports.join('\n'));}
 function chest(r){return dims['minecraft:overworld'].getBlock(add(state(r.id).room.origin,ARBORETUM.chest)).getComponent('minecraft:inventory').container;}
 function inside(p,r,phase='inside',source=offset(r.source,2.1,0,-4.5)){
  const room=state(r.id).room;p.dimension=dims['minecraft:overworld'];p.location=add(room.origin,ARBORETUM.arrival);
  p.properties.set(TICKET,JSON.stringify({schema:1,family:'arboretum',id:r.id,cell:room.cell,door:r.source,source,phase}));return plain(source);
 }
 const setBlock=(p,type,dimension='minecraft:overworld')=>blocks.set(dimension+'/'+key(p),block(type));
 reload();return {props,blocks,players,commands,places,reports,writes,particles,seeds,activeLeases,system,flags,world,dims,
  player,face,step,state,register,open,build,enter,chest,inside,setBlock,reload,get ctl(){return ctl;}};
}
let passed=0,failed=0;
async function group(name,fn){try{await fn();passed++;console.log(`PASS ${name}`);}catch(e){failed++;console.error(`FAIL ${name}\n${e.stack}`);}}

await group('pristine read-only scatter gate and append-only placement receipt preserve unknown history',()=>{
 const f=fixture();assert.equal(f.ctl.isRecordedRegion('fc_rgn_0_0'),false);assert.equal(f.props.size,0);
 const arg={regionKey:'fc_rgn_0_0',origin:{x:100,y:64,z:200,dimension:'minecraft:overworld'}};
 const id=f.ctl.beginPlacement(arg);assert.equal(id,'arboretum:0');assert.equal(f.ctl.isRecordedRegion(arg.regionKey),true);
 assert.equal(f.ctl.beginPlacement(arg),null);assert.equal(f.ctl.confirmPlacement(id),false);
 assert.equal(f.ctl.sourceAt('minecraft:overworld',f.state(id).source).placement,'pending');
 assert.equal(f.ctl.recordPlaced(id),true);f.flags.source=false;assert.equal(f.ctl.confirmPlacement(id),false);
 f.reload();f.flags.source=true;assert.equal(f.ctl.confirmPlacement(id),true);assert.equal(f.places.length,0);
 for(const k of [WITNESS,INDEX,stateKey(id)]){const prior=f.props.get(k);f.props.delete(k);assert.equal(f.ctl.isRecordedRegion(arg.regionKey),true);assert.equal(f.ctl.beginPlacement(arg),null);f.props.set(k,prior);}
});
await group('ambiguous initial record writes quarantine exact source and never repeat placement',()=>{
 for(const mode of ['before','after']){const f=fixture();f.flags.worldWrite=k=>k===stateKey('arboretum:0')?mode:null;
  const arg={regionKey:'r',origin:{x:100,y:64,z:200,dimension:'minecraft:overworld'}};
  assert.equal(f.ctl.beginPlacement(arg),null);f.flags.worldWrite=null;
  assert.equal(f.ctl.beginPlacement(arg),null);assert.ok(f.ctl.sourceAt('minecraft:overworld',{x:132.5,y:70,z:207.5}));
  assert.equal(f.ctl.confirmPlacement('arboretum:0'),false);assert.equal(f.places.length,0);
 }
});
await group('new 64-instance and 64-Hero limits never evict existing identity or partial progress',()=>{
 const f=fixture();for(let i=0;i<64;i++)f.register(i);const before=f.props.get(INDEX);
 assert.equal(f.ctl.beginPlacement({regionKey:'overflow',origin:{x:10000,y:64,z:200,dimension:'minecraft:overworld'}}),null);assert.equal(f.props.get(INDEX),before);
 const r=f.state('arboretum:0');for(let i=0;i<64;i++){const p=f.player(`p${i}`,offset(r.source,0,0,-1));assert.equal(f.ctl.completeUse(p,'fc:crunchy_chick'),true);}
 const saved=f.props.get(stateKey(r.id));assert.equal(f.ctl.completeUse(f.player('overflow',offset(r.source,0,0,-1)),'fc:crunchy_chick'),false);assert.equal(f.props.get(stateKey(r.id)),saved);
});
await group('legacy paid/persona faces cannot be adopted and moved/copy markers never authorize unlock',()=>{
 const f=fixture(),r=f.register(),legacy=f.face(r);legacy.properties.set('fc_door_idx',7);legacy.properties.set('fc_door_open',true);
 assert.equal(f.ctl.bindFace(legacy),null);const p=f.player();p.alignment=-1000;f.ctl.interact(p,legacy);assert.equal(f.state(r.id).unlocked,false);
 const copied=f.face(r);copied.properties.set('fc_door_identity',r.id);copied.location.x+=2;assert.equal(f.ctl.isCanonicalFace(copied),true);f.ctl.interact(p,copied);assert.equal(f.state(r.id).unlocked,false);
 const door=f.face(r);assert.equal(f.ctl.bindFace(door),r.id);f.ctl.interact(p,door);f.step(9);assert.equal(door.location.y,r.source.y+5);
 const replacement=f.face(r);assert.equal(f.ctl.reconcileFace(replacement),true);assert.equal(replacement.properties.get('fc_door_identity'),r.id);
});
await group('ten completed qualified chicks are per Hero and instance with bounded immediate replay refusal',()=>{
 const f=fixture(),r=f.register(),a=f.player('a'),b=f.player('b');f.flags.witness=false;assert.equal(f.ctl.completeUse(a,'fc:crunchy_chick'),false);f.flags.witness=true;
 assert.equal(f.ctl.completeUse(a,'fc:apple_pie'),false);for(let i=0;i<5;i++){f.step();assert.equal(f.ctl.completeUse(a,'fc:crunchy_chick'),true);assert.equal(f.ctl.completeUse(a,'fc:crunchy_chick'),false);assert.equal(f.ctl.completeUse(b,'fc:crunchy_chick'),true);}
 assert.equal(f.state(r.id).unlocked,false);for(let i=0;i<5;i++){f.step();assert.equal(f.ctl.completeUse(a,'fc:crunchy_chick'),true);}
 assert.equal(f.state(r.id).unlocked,true);assert.deepEqual(f.state(r.id).progress.map(h=>h.count),[10,5]);assert.equal(a.moves.length,0);assert.equal(f.seeds.length,0);
});
await group('ambiguous multiple witnesses and wrong side/dimension never receive food credit',()=>{
 const f=fixture(),r=f.register();const id=f.ctl.beginPlacement({regionKey:'nearby',origin:{x:103,y:64,z:200,dimension:'minecraft:overworld'}});f.ctl.recordPlaced(id);f.ctl.confirmPlacement(id);
 const p=f.player();assert.equal(f.ctl.completeUse(p,'fc:crunchy_chick'),false);p.location=offset(r.source,0,0,1);assert.equal(f.ctl.completeUse(p,'fc:crunchy_chick'),false);
 p.location=offset(r.source,0,0,-1);p.dimension=f.dims['minecraft:nether'];assert.equal(f.ctl.completeUse(p,'fc:crunchy_chick'),false);assert.equal(f.state(r.id).progress.length,0);
});
await group('full evil reads exact validated -1000; failed credit/unlock writes never grant or consume',()=>{
 for(const value of [null,-999,-1001,Infinity,'-1000']){const f=fixture(),r=f.register(),p=f.player();p.alignment=value;f.ctl.interact(p,f.face(r));assert.equal(f.state(r.id).unlocked,false);}
 for(const mode of ['before','after']){const f=fixture(),r=f.register(),p=f.player();p.alignment=-1000;f.flags.worldWrite=k=>k===stateKey(r.id)?mode:null;f.ctl.interact(p,f.face(r));assert.equal(p.moves.length,0);assert.equal(f.places.length,0);assert.equal(f.seeds.length,0);}
});
await group('two canonical instances build separate real rooms and physical once-only reward chests',()=>{
 const f=fixture(),a=f.register(),b=f.register(1);f.build(a);f.build(b);assert.equal(f.state(a.id).room.cell,0);assert.equal(f.state(b.id).room.cell,1);
 assert.equal(f.places.length,2);for(const r of [a,b]){assert.equal(f.chest(r).getItem(0).typeId,'fc:wellows_pickhammer');assert.equal(f.chest(r).getItem(0).amount,1);}
 const changed=f.state(b.id);changed.room=f.state(a.id).room;f.props.set(stateKey(b.id),JSON.stringify(changed));assert.equal(f.ctl.getState(b.id),null,'another instance cannot borrow this cell reservation');
 assert.equal(JSON.parse(f.props.get(cellKey(0))),a.id);
});
await group('full-volume scan skips occupied candidates without clearing and allocator never recycles reservations',()=>{
 const f=fixture(),r=f.register(),at=add(origin(0),{x:31,y:22,z:45});f.setBlock(at,'minecraft:diamond_block');f.build(r);
 assert.equal(f.state(r.id).room.cell,1);assert.equal(f.dims['minecraft:overworld'].getBlock(at).typeId,'minecraft:diamond_block');assert.equal(JSON.parse(f.props.get(INDEX)).nextCell,2);
 assert.equal(f.places.length,1);assert.equal(JSON.parse(f.props.get(cellKey(0))),r.id);
});
await group('late edits to previously scanned air are refused immediately before placement',()=>{
 const f=fixture(),r=f.register();f.open(r);f.step();const at=add(origin(0),{x:4,y:0,z:0});f.setBlock(at,'minecraft:gold_block');f.step(145);
 assert.equal(f.places.length,0);assert.equal(f.dims['minecraft:overworld'].getBlock(at).typeId,'minecraft:gold_block');assert.match(f.reports.join('\n'),/changed during its survey/);
});
await group('entities, unavailable blocks and missing loading authority leave the player at the source',()=>{
 for(const failure of ['loaded','lease','entities']){const f=fixture(),r=f.register();if(failure==='entities')f.flags.entities=[{location:add(origin(0),{x:10,y:3,z:10})}];else f.flags[failure]=false;
  const {p}=f.open(r);f.step(340);assert.equal(f.places.length,0);assert.equal(p.moves.length,0);assert.equal(f.state(r.id).unlocked,true);}
});
await group('ambiguous structure placement never replays; a fully placed receipt can finish verification after reload',()=>{
 for(const failure of ['before','after']){const f=fixture(),r=f.register();f.flags.place=failure;const {p}=f.open(r);f.step(150);assert.equal(f.state(r.id).room.phase,'placing');const n=f.places.length;
  f.reload();f.flags.place='ok';p.location=offset(r.source,0,0,-1);f.step(2);p.location=plain(r.source);f.step(220);
  assert.equal(f.places.length,n);if(failure==='after'){assert.equal(f.state(r.id).room.phase,'ready');assert.equal(f.seeds.length,1);}else assert.equal(f.seeds.length,0);
 }
});
await group('seed failure before or after item transfer never authorizes reseeding or admission',()=>{
 for(const failure of ['before','after']){const f=fixture(),r=f.register();f.flags.seed=failure;const {p}=f.open(r);f.step(180);assert.equal(f.state(r.id).room.phase,'seeding');const n=f.seeds.length;
  f.reload();f.flags.seed='ok';p.location=offset(r.source,0,0,-1);f.step(2);p.location=plain(r.source);f.step(250);assert.equal(f.seeds.length,n);assert.equal(p.moves.length,0);assert.equal(f.places.length,1);
 }
});
await group('full shell, target chest and native inventory preconditions refuse altered first-build geometry',()=>{
 for(const damage of [{at:{x:0,y:17,z:22},type:'minecraft:air'},{at:{x:13,y:4,z:25},type:'minecraft:stone'}]){
  const f=fixture(),r=f.register();f.flags.damage=damage;const {p}=f.open(r);f.step(340);assert.equal(f.seeds.length,0);assert.equal(p.moves.length,0);assert.equal(f.places.length,1);
 }
 const f=fixture(),r=f.register();f.flags.prefill=true;f.open(r);f.step(180);assert.equal(f.seeds.length,0);assert.equal(f.chest(r).getItem(8).typeId,'minecraft:diamond');
});
await group('shared entry gate blocks nesting and never obstructs an occupied exact-source return',()=>{
 const f=fixture(),r=f.register(),{p}=f.build(r);f.flags.entry=false;p.location=plain(r.source);f.step(20);assert.equal(p.moves.length,0);
 f.flags.entry=true;p.location=offset(r.source,0,0,-1);f.step(14);f.enter(p,r);assert.equal(f.ctl.allowsOtherEntry(p),false);
 const saved=JSON.parse(p.properties.get(TICKET)).source;f.flags.entry=false;assert.equal(f.ctl.requestReturn(p),true);assert.deepEqual(p.location,{x:saved.x,y:saved.y,z:saved.z});
 p.unreadable=true;assert.equal(f.ctl.allowsOtherEntry(p),false);p.unreadable=false;assert.equal(f.ctl.allowsOtherEntry(p),true);
});
await group('two Heroes retain distinct exact approaches and native chest depletion is never refilled',()=>{
 const f=fixture(),r=f.register(),{p:a}=f.build(r),b=f.player('second');f.enter(a,r);const exactA=JSON.parse(a.properties.get(TICKET)).source;
 b.location=offset(r.source,-2.1,0,-3);f.step(14);b.location=plain(r.source);f.step(15);const exactB=JSON.parse(b.properties.get(TICKET)).source;
 assert.notDeepEqual(exactA,exactB);f.chest(r).slots.delete(0);f.step();assert.equal(f.state(r.id).reward.claimed,true);
 assert.equal(f.ctl.requestReturn(a),true);assert.equal(f.ctl.requestReturn(b),true);assert.deepEqual(a.location,{x:exactA.x,y:exactA.y,z:exactA.z});assert.deepEqual(b.location,{x:exactB.x,y:exactB.y,z:exactB.z});
 f.reload();f.enter(a,r);assert.equal(f.seeds.length,1);assert.equal(f.chest(r).getItem(0),undefined);assert.equal(f.places.length,1);
});
await group('committed tickets return and guard exact old cells across lost, corrupt and replaced primary records',()=>{
 for(const failure of ['missing','corrupt','unreadable','replacement']){const f=fixture(),r=f.register(),{p}=f.build(r),exact=f.inside(p,r);
  if(failure==='missing')f.props.delete(stateKey(r.id));if(failure==='corrupt')f.props.set(INDEX,'{broken');if(failure==='unreadable')f.flags.reads.add(INDEX);
  if(failure==='replacement'){const next=f.register(1);const replacement=f.state(r.id);replacement.source=next.source;f.props.set(stateKey(r.id),JSON.stringify(replacement));}
  const backing=JSON.stringify([...f.props]);assert.equal(f.ctl.protectsBlock('minecraft:overworld',add(origin(0),{x:20,y:3,z:20})),true);
  assert.equal(f.ctl.requestReturn(p),true,failure);assert.deepEqual(p.location,{x:exact.x,y:exact.y,z:exact.z});assert.equal(JSON.stringify([...f.props]),backing);assert.equal(f.seeds.length,1);
 }
});
await group('unreadable ticket phases defer all own writes/travel while another healthy visitor still returns',()=>{
 const f=fixture(),r=f.register(),{p:a}=f.build(r),b=f.player('healthy');
 for(const phase of ['entering','inside','outside','returning']){const exact=f.inside(a,r,phase);f.inside(b,r);a.unreadable=true;const saved=a.properties.get(TICKET),n=a.playerWrites.length,m=a.moves.length;
  f.step(3);assert.equal(f.ctl.requestReturn(a),false);assert.equal(a.properties.get(TICKET),saved);assert.equal(a.playerWrites.length,n);assert.equal(a.moves.length,m);
  assert.equal(f.ctl.requestReturn(b),true);a.unreadable=false;assert.equal(f.ctl.requestReturn(a),true);assert.deepEqual(a.location,{x:exact.x,y:exact.y,z:exact.z});
 }
});
await group('only readable absent/corrupt tickets use current occupied room fallback; wrong dimension/outside cannot',()=>{
 const f=fixture(),r=f.register(),{p}=f.build(r);
 for(const raw of [undefined,'{bad',JSON.stringify({schema:1,family:'arboretum',id:r.id,cell:0.5})]){p.location=add(origin(0),ARBORETUM.arrival);p.dimension=f.dims['minecraft:overworld'];raw===undefined?p.properties.delete(TICKET):p.properties.set(TICKET,raw);
  assert.equal(f.ctl.requestReturn(p),true);assert.deepEqual(p.location,{x:r.source.x,y:r.source.y,z:r.source.z-1});}
 p.location=add(origin(0),ARBORETUM.arrival);p.dimension=f.dims['minecraft:nether'];const n=p.moves.length;assert.equal(f.ctl.requestReturn(p),false);assert.equal(p.moves.length,n);
});
await group('return click identity is exact-cell, guards update immediately, and unrelated cells are not reserved',()=>{
 const f=fixture(),r=f.register(),{p}=f.build(r);f.inside(p,r);const arch=add(origin(0),ARBORETUM.returnDetectorCells[0]);assert.equal(f.ctl.isReturnBlock(p,'minecraft:overworld',arch),true);
 f.props.delete(INDEX);p.location=add(origin(1),ARBORETUM.arrival);assert.equal(f.ctl.isReturnBlock(p,'minecraft:overworld',arch),false);assert.equal(f.ctl.protectsBlock('minecraft:overworld',arch),false);
 assert.equal(f.ctl.protectsBlock('minecraft:overworld',add(origin(200),ARBORETUM.arrival)),false);
 for(const cell of [-1,4096,.5,NaN])assert.equal(inArboretum(add(origin(0),ARBORETUM.arrival),cell),false);
});
await group('failed and ambiguous teleports preserve committed exact sources; failed clear cannot double-return',()=>{
 const f=fixture(),r=f.register(),{p}=f.build(r);
 for(const fault of ['false','before','after']){const exact=f.inside(p,r);f.flags.teleport=fault;const result=f.ctl.requestReturn(p);assert.equal(result,fault==='after');
  if(fault!=='after')assert.deepEqual(JSON.parse(p.properties.get(TICKET)).source,exact);}
 f.flags.teleport='ok';for(const mode of ['before','after']){f.inside(p,r);p.writeFault=(k,v)=>k===TICKET&&v===undefined?mode:null;const n=p.moves.length;assert.equal(f.ctl.requestReturn(p),true);assert.equal(f.ctl.requestReturn(p),false);assert.equal(p.moves.length,n+1);p.writeFault=null;f.step();}
});
await group('one fresh periodic ticket read is sufficient and no cached ticket authorizes later calls',()=>{
 const f=fixture(),r=f.register(),{p}=f.build(r);f.inside(p,r);const original=p.getDynamicProperty;let reads=0;
 p.getDynamicProperty=k=>{if(k===TICKET&&++reads>1)throw Error('inconsistent second read');return original(k);};
 f.step();assert.equal(reads,1);p.getDynamicProperty=original;p.unreadable=true;const n=p.moves.length;assert.equal(f.ctl.requestReturn(p),false);assert.equal(p.moves.length,n);
});
await group('bounded portal shimmer is limited to relevant loaded visitors and leases use only two own names',()=>{
 const f=fixture(),r=f.register(),{p}=f.build(r);f.step(4);assert.ok(f.particles.some(v=>v.name==='minecraft:soul_particle'&&v.p.x<620000));
 f.inside(p,r);f.step(4);assert.ok(f.particles.some(v=>v.p.x>=620000));assert.ok(f.activeLeases.size<=2);
 assert.ok(f.commands.every(v=>!v.command.includes('remove_all')));assert.ok(f.commands.filter(v=>v.command.startsWith('tickingarea add')).every(v=>/fc_dp_arbor_(load|return) true$/.test(v.command)));
});
await group('ignored, wrong-item and wrong-count seed writes never become a ready reward or claim',()=>{
 for(const failure of ['ignore','wrong','count']){const f=fixture(),r=f.register();f.flags.seed=failure;f.open(r);f.step(180);
  assert.equal(f.state(r.id).room.phase,'seeding');assert.equal(f.state(r.id).reward.seeded,false);assert.equal(f.state(r.id).reward.claimed,false);assert.equal(f.seeds.length,1);
  f.reload();f.step(50);assert.equal(f.seeds.length,1);
 }
});
await group('surviving cell ownership alone proves established history and blocks index reinitialization',()=>{
 const f=fixture();f.props.set(cellKey(0),JSON.stringify('arboretum:0'));const before=JSON.stringify([...f.props]);
 assert.equal(f.ctl.isRecordedRegion('new'),true);assert.equal(f.ctl.beginPlacement({regionKey:'new',origin:{x:100,y:64,z:200,dimension:'minecraft:overworld'}}),null);
 assert.equal(JSON.stringify([...f.props]),before);assert.equal(f.writes.length,0);
});
await group('late nonsentinel shell loss blocks both first ready commit and later cached-room admission',()=>{
 const f=fixture(),r=f.register();f.open(r);for(let i=0;i<180&&!f.places.length;i++)f.step();assert.equal(f.places.length,1);f.step();
 f.setBlock(add(origin(0),{x:0,y:4,z:5}),'minecraft:air');f.step(35);assert.equal(f.seeds.length,0);assert.notEqual(f.state(r.id).room.phase,'ready');
 const g=fixture(),s=g.register(),{p}=g.build(s);g.setBlock(add(origin(0),{x:0,y:4,z:5}),'minecraft:air');p.location=offset(s.source,0,0,-1);g.step(14);p.location=plain(s.source);g.step(120);
 assert.equal(p.moves.length,0);assert.equal(g.seeds.length,1);assert.equal(g.places.length,1);
});
await group('revision exhaustion remains readable and refuses mutations before any cell reservation',()=>{
 const f=fixture(),r=f.register(),p=f.player(),exhausted=f.state(r.id);exhausted.revision=Number.MAX_SAFE_INTEGER;
 f.props.set(stateKey(r.id),JSON.stringify(exhausted));const before=JSON.stringify([...f.props]);p.alignment=-1000;f.ctl.interact(p,f.face(r));f.ctl.completeUse(p,'fc:crunchy_chick');f.step();
 assert.equal(f.ctl.getState(r.id).revision,Number.MAX_SAFE_INTEGER);assert.equal(JSON.stringify([...f.props]),before);assert.equal(f.places.length,0);
 const g=fixture();assert.equal(g.ctl.beginPlacement({regionKey:'outside',origin:{x:29999990,y:64,z:200,dimension:'minecraft:overworld'}}),null);assert.equal(g.props.size,0);
});
console.log(`Arboretum runtime: ${passed} groups passed, ${failed} failed; actual generated room cells ${geometry.grid.length}; native acceptance unrun.`);
if(failed)process.exitCode=1;

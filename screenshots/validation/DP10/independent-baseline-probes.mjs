import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import vm from 'node:vm';
const root=new URL('../../../',import.meta.url);
if(!process.env.ARBORETUM_OWNER||!process.env.ARBORETUM_GEOMETRY)throw Error('Use independent-review.py, or provide ARBORETUM_OWNER and ARBORETUM_GEOMETRY paths.');
const code=readFileSync(process.env.ARBORETUM_OWNER,'utf8');
const module=new vm.SourceTextModule(code,{context:vm.createContext({})});
await module.link(()=>{throw Error('The Arboretum must inject engine effects');});await module.evaluate();
const {createArboretumDoors,ARBORETUM,ARBORETUM_INDEX_KEY:INDEX,ARBORETUM_WITNESS_KEY:WITNESS,
  ARBORETUM_RETURN_KEY:TICKET,arboretumStateKey:stateKey,arboretumCellKey:cellKey,arboretumOrigin:origin,inArboretum}=module.namespace;
// Execute the actual current owned builder once. No fixture imitates its room.
const geometry=JSON.parse(readFileSync(process.env.ARBORETUM_GEOMETRY,'utf8'));
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
const outcomes=[];
function run(name,fn){try{const result=fn();outcomes.push({name,reproduced:true,...result});console.log(`REPRODUCED ${name}: ${JSON.stringify(result)}`);}catch(error){outcomes.push({name,reproduced:false,error:String(error),stack:error.stack});console.error(`FAILED PROBE ${name}\n${error.stack}`);process.exitCode=1;}}
function waitForPlacement(f){for(let i=0;i<250&&!f.places.length;i++)f.step();assert.equal(f.places.length,1);}
function afterBuild(f,id){for(let i=0;i<200&&f.state(id).room.phase!=='ready';i++)f.step();return f.state(id);}
function seedIntent(f,id,hook){f.flags.worldWrite=(k,v)=>{if(k===stateKey(id)&&JSON.parse(v).room?.phase==='seeding'){f.flags.worldWrite=null;hook();}return null;};}
run('control: normal first build has one native placement and one physical reward',()=>{
 const f=fixture(),r=f.register();f.build(r);assert.equal(f.places.length,1);assert.equal(f.seeds.length,1);assert.equal(f.chest(r).getItem(0).typeId,ARBORETUM.item);
 return {phase:f.state(r.id).room.phase,placements:f.places.length,seeds:f.seeds.length};
});
run('seed intent late slot-zero contents are overwritten',()=>{
 const f=fixture(),r=f.register();f.open(r);waitForPlacement(f);
 seedIntent(f,r.id,()=>f.chest(r).slots.set(0,{typeId:'minecraft:diamond',amount:7}));
 const state=afterBuild(f,r.id);assert.equal(state.room.phase,'ready');assert.equal(f.chest(r).getItem(0).typeId,ARBORETUM.item);assert.equal(f.seeds.length,1);
 return {phase:state.room.phase,injected:{typeId:'minecraft:diamond',amount:7},actual:plain(f.chest(r).getItem(0)),seeds:f.seeds.length};
});
run('seed intent late occupant does not prevent native reward write',()=>{
 const f=fixture(),r=f.register();f.open(r);waitForPlacement(f);
 seedIntent(f,r.id,()=>f.player('late-visitor',add(origin(0),ARBORETUM.arrival)));
 const state=afterBuild(f,r.id);assert.equal(state.room.phase,'ready');assert.equal(f.seeds.length,1);
 return {phase:state.room.phase,seeds:f.seeds.length,occupants:f.players.filter(p=>inArboretum(p.location,0)).length};
});
run('seed intent replaced native chest is not reacquired',()=>{
 const f=fixture(),r=f.register();f.open(r);waitForPlacement(f);const before=f.chest(r);
 const slots=new Map([[0,{typeId:'minecraft:diamond',amount:7}]]),replacement={size:27,getItem:i=>slots.get(i),setItem(i,v){slots.set(i,v);}};
 seedIntent(f,r.id,()=>f.blocks.set('minecraft:overworld/'+key(add(origin(0),ARBORETUM.chest)),{typeId:'minecraft:chest',getComponent:id=>id==='minecraft:inventory'?{container:replacement}:undefined}));
 const state=afterBuild(f,r.id);assert.equal(state.room.phase,'ready');assert.equal(f.chest(r).getItem(0).typeId,'minecraft:diamond');assert.equal(before.getItem(0).typeId,ARBORETUM.item);
 return {phase:state.room.phase,live:plain(f.chest(r).getItem(0)),detached:plain(before.getItem(0)),seeds:f.seeds.length};
});
run('native reward write replaces chest and same stale handle readback accepts missing reward',()=>{
 const f=fixture(),r=f.register();f.open(r);waitForPlacement(f);const c=f.chest(r),nativeWrite=c.setItem.bind(c);
 const replacement={size:27,getItem:()=>undefined,setItem(){throw Error('unexpected replacement write');}};
 c.setItem=(i,v)=>{nativeWrite(i,v);f.blocks.set('minecraft:overworld/'+key(add(origin(0),ARBORETUM.chest)),{typeId:'minecraft:chest',getComponent:id=>id==='minecraft:inventory'?{container:replacement}:undefined});};
 const state=afterBuild(f,r.id);assert.equal(state.room.phase,'ready');assert.equal(f.chest(r).getItem(0),undefined);assert.equal(c.getItem(0).typeId,ARBORETUM.item);
 return {phase:state.room.phase,claimed:state.reward.claimed,liveReward:null,detached:plain(c.getItem(0)),seeds:f.seeds.length};
});
run('reward readback ignores changed custom name and lore',()=>{
 const f=fixture(),r=f.register();f.open(r);waitForPlacement(f);const c=f.chest(r),nativeWrite=c.setItem.bind(c);
 c.setItem=(i,v)=>{v.nameTag='Wrong reward name';v.getLore=()=>['Wrong reward lore'];nativeWrite(i,v);};
 const state=afterBuild(f,r.id);assert.equal(state.room.phase,'ready');assert.equal(f.chest(r).getItem(0).nameTag,'Wrong reward name');
 return {phase:state.room.phase,name:f.chest(r).getItem(0).nameTag,lore:f.chest(r).getItem(0).getLore()};
});
run('full native placement then throw admits after reload without saved successful receipt',()=>{
 const f=fixture(),r=f.register();f.flags.place='after';const {p}=f.open(r);waitForPlacement(f);assert.equal(f.state(r.id).room.phase,'placing');assert.equal(f.seeds.length,0);
 f.flags.place='ok';f.reload();p.location=offset(r.source,2.1,0,-4.5);f.step(14);p.location=plain(r.source);f.step(200);
 const state=f.state(r.id);assert.equal(state.room.phase,'ready');assert.equal(f.places.length,1);assert.equal(f.seeds.length,1);assert.equal(p.moves.length,1);
 return {phase:state.room.phase,placements:f.places.length,seeds:f.seeds.length,teleports:p.moves.length,receipt:null};
});
run('control: collected ready room is never reseeded after reload',()=>{
 const f=fixture(),r=f.register(),{p}=f.build(r);f.chest(r).slots.clear();f.step();assert.equal(f.state(r.id).reward.claimed,true);f.reload();f.enter(p,r);
 assert.equal(f.places.length,1);assert.equal(f.seeds.length,1);assert.equal(f.chest(r).getItem(0),undefined);
 return {phase:f.state(r.id).room.phase,claimed:f.state(r.id).reward.claimed,placements:f.places.length,seeds:f.seeds.length};
});
console.log(JSON.stringify({nativeAcceptance:'unrun',outcomes},null,2));

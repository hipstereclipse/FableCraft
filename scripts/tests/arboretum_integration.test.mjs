// Actual main adapters, both door owners, alignment and final geometry builders.
// Engine boundaries are injected; this does not execute native Bedrock.
import test from 'node:test';
import assert from 'node:assert/strict';
import vm from 'node:vm';
import {readFileSync} from 'node:fs';
import {spawnSync} from 'node:child_process';
import {parse} from 'espree';
const main=readFileSync('packs/Fablecraft_BP/scripts/main.js','utf8'),ast=parse(main,{ecmaVersion:'latest',sourceType:'module',range:true});
const text=n=>main.slice(...n.range),plain=v=>JSON.parse(JSON.stringify(v));
const add=(a,b)=>({x:a.x+b.x,y:a.y+b.y,z:a.z+b.z}),cell=p=>`${Math.floor(p.x)},${Math.floor(p.y)},${Math.floor(p.z)}`;
function declarations(names){return names.map(name=>{const node=ast.body.find(n=>n.type==='FunctionDeclaration'&&n.id.name===name||n.type==='VariableDeclaration'&&n.declarations.some(d=>d.id.name===name));assert.ok(node,name);return text(node);}).join('\n');}
const geometryRun=spawnSync('python',['-c',`import json,sys
from unittest.mock import patch
sys.path.insert(0,'scripts')
import gen_structures as g
out={}
def capture(v,name):out['fc:'+name]={'size':[v.sx,v.sy,v.sz],'palette':v.palette,'grid':v.grid}
with patch.object(g.Vox,'save',capture):
 g.greatwood_gorge()
 g.arboretum()
print(json.dumps(out))`],{encoding:'utf8',maxBuffer:8*1024*1024});
assert.equal(geometryRun.status,0,geometryRun.stderr);const geometry=JSON.parse(geometryRun.stdout);
const sourceNames=['fc_demon_doors.js','guild_door_aperture.js','arboretum_doors.js','fc_gamedata.js','wd/alignment.js','wd/state.js','wd/config.js'];
const source=Object.fromEntries(sourceNames.map(n=>[n,readFileSync('packs/Fablecraft_BP/scripts/'+n,'utf8')]));
async function fixture(){
 const events=[],props=new Map(),players=[],entities=[],volumes=[],blocks=new Map(),faults=new Map(),timers=[],payouts=[],configs={};
 const context=vm.createContext({console:{warn:message=>events.push(['warn',message]),log(){}}}),modules=new Map();
 async function load(name){if(modules.has(name))return modules.get(name);const m=new vm.SourceTextModule(source[name],{context,identifier:name});modules.set(name,m);await m.link(dep=>load(name.startsWith('wd/')?'wd/'+dep.slice(2):dep.slice(2)));return m;}
 const api={};for(const n of sourceNames){const m=await load(n);await m.evaluate();api[n]=m.namespace;}
 const system={currentTick:1,run:fn=>timers.push(fn),runTimeout:fn=>timers.push(fn)};
 function fail(key){const n=faults.get(key)??0;if(n>0){faults.set(key,n-1);throw Error(key);}}
 const world={getDynamicProperty(key){fail('read:'+key);return props.get(key);},setDynamicProperty(key,value){fail('write:'+key);world.beforeWrite?.(key,value);events.push(['world-write',key,value]);if(value===undefined)props.delete(key);else props.set(key,value);world.afterWrite?.(key,value);fail('after-write:'+key);},getPlayers:()=>players.filter(p=>p.isValid),getDimension:id=>dimensions[id==='overworld'?'minecraft:overworld':id]};
 function material(dim,p){for(const v of [...volumes].reverse()){const [sx,sy,sz]=v.data.size,x=Math.floor(p.x-v.origin.x),y=Math.floor(p.y-v.origin.y),z=Math.floor(p.z-v.origin.z);if(v.dim===dim.id&&x>=0&&x<sx&&y>=0&&y<sy&&z>=0&&z<sz)return v.data.palette[v.data.grid[x*sy*sz+y*sz+z]][0];}return Math.floor(p.y)===64?'minecraft:cobblestone':'minecraft:air';}
 function blockAt(dim,p){const key=dim.id+'/'+cell(p);fail('block:'+key);if(!blocks.has(key)){let changed;const inventory={size:27,items:new Map(),getItem(i){return this.items.get(i);},setItem(i,item){this.items.set(i,item);events.push(['inventory-write',key,i,item?.typeId]);}};blocks.set(key,{location:{x:Math.floor(p.x),y:Math.floor(p.y),z:Math.floor(p.z)},get typeId(){return changed??material(dim,p);},set typeId(v){changed=v;},get isAir(){return this.typeId==='minecraft:air';},setType(v){changed=v;events.push(['block-write',key,v]);},getComponent(id){return id==='minecraft:inventory'&&this.typeId==='minecraft:chest'?{container:inventory}:undefined;}});}return blocks.get(key);}
 const dimensions=Object.fromEntries(['minecraft:overworld','minecraft:nether','minecraft:the_end'].map(id=>[id,{id,getBlock(p){return blockAt(this,p);},containsBlock(volume,filter,allowUnloaded){events.push(['bulk',plain(volume),plain(filter)]);this.beforeBulk?.(volume,filter);fail('bulk');assert.equal(filter.excludeTypes.length,1);assert.equal(typeof filter.excludeTypes[0],'string');assert.equal(allowUnloaded,false);for(let x=volume.from.x;x<=volume.to.x;x++)for(let y=volume.from.y;y<=volume.to.y;y++)for(let z=volume.from.z;z<=volume.to.z;z++){const p={x,y,z};if(!filter.excludeTypes.includes(blocks.get(this.id+'/'+cell(p))?.typeId??material(this,p)))return true;}return false;},getEntities(query){fail('scan');return entities.filter(e=>e.isValid&&e.dimension===this&&(!query.type||query.type===e.typeId)&&(!query.location||Math.hypot(e.location.x-query.location.x,e.location.y-query.location.y,e.location.z-query.location.z)<=query.maxDistance));},runCommand(command){events.push(['command',id,command]);return {successCount:1};},spawnParticle(){}}]));
 const dim=dimensions['minecraft:overworld'];
 world.structureManager={place(id,d,origin,options){events.push(['structure',id,plain(origin),options]);fail('structure-before');if(geometry[id])volumes.push({dim:d.id,origin:plain(origin),data:geometry[id]});fail('structure-after');}};
 function actor(typeId,id,location){const saved=new Map(),a={id,typeId,isValid:true,dimension:dim,location:{...location},props:saved,
  getDynamicProperty(k){fail(id+':read:'+k);return saved.get(k);},setDynamicProperty(k,v){fail(id+':write:'+k);events.push(['actor-write',id,k,v]);if(v===undefined)saved.delete(k);else saved.set(k,v);},
  triggerEvent(e){events.push(['native',id,e]);},teleport(p){this.location={...p};},remove(){this.isValid=false;},playSound(){},sendMessage(m){events.push(['message',id,m]);},getTags:()=>[],
  getComponent(){return undefined;},getGameMode(){fail(id+':mode');return this.mode;},mode:'Survival',
  tryTeleport(p,options){events.push(['teleport',id,plain(p),options.dimension.id]);this.location={...p};this.dimension=options.dimension;return true;}};return a;}
 function player(location={x:0,y:65,z:0}){const p=actor('minecraft:player','hero-'+players.length,location);p.props.set('wd:state',JSON.stringify({schemaVersion:3,alignment:0}));p.props.set('fc_morality',0);players.push(p);return p;}
 function face(location,old={}){const e=actor('fc:demon_door','face-'+entities.length,location);for(const [k,v]of Object.entries(old))e.props.set(k,v);entities.push(e);return e;}
 const data=api['fc_gamedata.js'].DATA;
 Object.assign(context,{world,system,DATA:data,BlockVolume:class{constructor(from,to){this.from={...from};this.to={...to};}},ItemStack:class{constructor(typeId,amount){this.typeId=typeId;this.amount=amount;}},
  GameMode:{Survival:'Survival',Adventure:'Adventure',Creative:'Creative',Spectator:'Spectator'},readAlignmentAuthority:api['wd/alignment.js'].readAlignmentAuthority,
  createGuildDoorAperture:api['guild_door_aperture.js'].createGuildDoorAperture,
  createDemonDoorPilot:o=>{configs.guild=o;return api['fc_demon_doors.js'].createDemonDoorPilot(o);},
  createArboretumDoors:o=>{configs.arbor=o;return api['arboretum_doors.js'].createArboretumDoors(o);},
  TICKS:()=>system.currentTick,OW:()=>dim,trySpawn:(d,type,location)=>{const e=face(location);e.dimension=d;e.typeId=type;events.push(['spawn',type]);return e;},
  hash2:()=>.1,pickStruct:()=>vm.runInContext('STRUCTS.find(s=>s.id==="fc:greatwood_gorge")',context),sampleGroundY:()=>65,surfaceCategory:()=> 'grass',surfMatch:()=>true,tooCloseToExisting:()=>false,
  recordPlace:(...args)=>events.push(['record-place',...args]),blendTerrain(){},skirtTerrain(){},fillLootChests(){},
  openDemonDoor:(...args)=>payouts.push(args),doorRiddle:(...args)=>payouts.push(args),morality:()=>0,countItem:()=>100,removeItem:()=>{events.push(['remove-item']);return true;},
  P:{get:()=>0,set(){},add(){}},addMorality:(p,n)=>api['wd/alignment.js'].changeAlignment(p,n,false),healPlayer(){},giveXp(){},maxWill:()=>100,willEnergy:()=>0,
 });
 const names=['guildDoorAperture','guildDoorPilot','arboretumDoors','arboretumSourceReady','ensureArboretumFaces','doorProtectsBlock','doorWorldPositionExcluded','occupiedDoor','requestDoorReturn','isGuildDoorSource','ensureGuildDoorPilot','guildDoorWorldExcluded','doorPersona','demonDoorTalk','ensureDemonDoor','ensureAllDemonDoors','REGION','STRUCTS','maybePlace','witnessedFoodEvents'];
 vm.runInContext(declarations(names),context);const runtime=vm.runInContext('({'+names.filter(n=>!['REGION','STRUCTS','witnessedFoodEvents'].includes(n)).join(',')+'})',context);
 function callback(prefix,includes=''){const n=ast.body.find(n=>n.type==='ExpressionStatement'&&text(n).startsWith(prefix)&&text(n).includes(includes));assert.ok(n,prefix);return vm.runInContext('('+text(n.expression.arguments[0])+')',context);}
 const complete=callback('world.afterEvents.itemCompleteUse.subscribe('),breakBlock=callback('world.beforeEvents.playerBreakBlock.subscribe(','doorProtectsBlock'),useBlock=callback('world.beforeEvents.playerInteractWithBlock.subscribe(','doorProtectsBlock'),itemUse=callback('world.beforeEvents.itemUse.subscribe(','occupiedDoor');
 function placeDirect(origin={dimension:dim.id,x:300,y:64,z:400},region='direct'){const id=runtime.arboretumDoors.beginPlacement({regionKey:region,origin});assert.ok(id);world.structureManager.place('fc:greatwood_gorge',world.getDimension(origin.dimension),origin);assert.equal(runtime.arboretumDoors.recordPlaced(id),true);assert.equal(runtime.arboretumDoors.confirmPlacement(id),true);return runtime.arboretumDoors.getState(id);}
 function approach(p,r){p.dimension=world.getDimension(r.source.dimension);p.location={...add(r.source,{x:0,y:0,z:-1})};}
 function eat(p,ev={source:p,itemStack:{typeId:'fc:crunchy_chick',amount:16},useDuration:0}){complete(ev);system.currentTick+=24;return ev;}
 return {api,configs,runtime,world,dim,dimensions,player,face,props,events,faults,payouts,system,timers,complete,breakBlock,useBlock,itemUse,placeDirect,approach,eat,blockAt:p=>blockAt(dim,p),flush(){while(timers.length)timers.shift()();}};
}

test('actual scatter reserves new Gorge before placement, confirms after final geometry, then marks region',async()=>{
 const f=await fixture(),p=f.player();f.runtime.maybePlace(p,0,0);
 const r=f.runtime.arboretumDoors.getPlacement('fc_rgn_0_0');assert.ok(r,'Fresh world can reach beginPlacement');assert.equal(r.placement,'confirmed');assert.equal(f.props.get('fc_rgn_0_0'),1);
 const pending=f.events.findIndex(e=>e[0]==='world-write'&&e[1]===f.api['arboretum_doors.js'].arboretumStateKey(r.id)&&JSON.parse(e[2]).placement==='pending');
 const structure=f.events.findIndex(e=>e[0]==='structure'),confirmed=f.events.findIndex(e=>e[0]==='world-write'&&e[1]===f.api['arboretum_doors.js'].arboretumStateKey(r.id)&&JSON.parse(e[2]).placement==='confirmed'),marker=f.events.findIndex(e=>e[0]==='world-write'&&e[1]==='fc_rgn_0_0');
 const receipt=f.events.findIndex(e=>e[0]==='world-write'&&e[1]===f.api['arboretum_doors.js'].arboretumStateKey(r.id)&&JSON.parse(e[2]).placement==='placed');
 assert.ok(pending>=0&&pending<structure&&structure<receipt&&receipt<confirmed&&confirmed<marker);
 assert.equal(f.payouts.length,0);assert.equal(f.events.filter(e=>e[0]==='structure').length,1);
});

test('old region markers never enroll or replay saved Gorges; pending reservations survive marker loss and ambiguous placement',async()=>{
 const old=await fixture(),p=old.player();old.props.set('fc_rgn_0_0',1);old.runtime.maybePlace(p,0,0);assert.equal(old.events.filter(e=>e[0]==='structure').length,0);assert.equal(old.props.has(old.api['arboretum_doors.js'].ARBORETUM_INDEX_KEY),false);
 for(const phase of ['structure-before','structure-after']){const f=await fixture(),p=f.player();f.faults.set(phase,1);f.runtime.maybePlace(p,0,0);const r=f.runtime.arboretumDoors.getPlacement('fc_rgn_0_0');assert.ok(r,phase);assert.equal(r.placement,'pending');f.props.delete('fc_rgn_0_0');f.runtime.maybePlace(p,0,0);assert.equal(f.events.filter(e=>e[0]==='structure').length,1,phase);f.approach(p,r);f.runtime.ensureArboretumFaces(f.dim);assert.equal(f.runtime.arboretumDoors.getState(r.id).placement,'pending',phase+' cannot adopt even when actual mouth geometry is present');}
 const f=await fixture(),q=f.player();f.runtime.maybePlace(q,0,0);f.props.delete('fc_rgn_0_0');f.runtime.maybePlace(q,0,0);assert.equal(f.events.filter(e=>e[0]==='structure').length,1);
});

test('actual sourceReady accepts final Gorge floor/throat and refuses edited support/headroom without repair',async()=>{
 const f=await fixture(),r=f.placeDirect();assert.equal(f.runtime.arboretumSourceReady(r),true);
 for(const offset of [{x:31,y:5,z:6},{x:33,y:9,z:11}]){const b=f.blockAt(add(r.origin,offset)),old=b.typeId;b.typeId='minecraft:chest';assert.equal(f.runtime.arboretumSourceReady(r),false);assert.equal(b.typeId,'minecraft:chest');b.typeId=old;}
});

test('canonical face dispatch preserves instance ownership and cannot pay a legacy persona after marker loss or corrupt state',async()=>{
 const f=await fixture(),r=f.placeDirect(),p=f.player();f.approach(p,r);f.runtime.ensureArboretumFaces(f.dim);
 const face=f.dim.getEntities({type:'fc:demon_door'})[0];assert.ok(face);assert.equal(face.props.get('fc_door_identity'),r.id);assert.equal(face.props.has('fc_door_idx'),false);
 face.props.delete('fc_door_identity');f.runtime.demonDoorTalk(p,face,'fc:lantern');assert.equal(face.props.get('fc_door_identity'),r.id);assert.equal(f.payouts.length,0);
 f.props.set(f.api['arboretum_doors.js'].arboretumStateKey(r.id),'{broken');f.runtime.demonDoorTalk(p,face,'fc:lantern');assert.equal(f.payouts.length,0);assert.equal(face.props.has('fc_door_idx'),false);
 const paid=f.face(r.source,{'fc_door_idx':0,'fc_door_open':true});assert.equal(f.runtime.arboretumDoors.bindFace(paid),null);f.runtime.demonDoorTalk(p,paid,'fc:lantern');assert.equal(f.payouts.length,0);assert.equal(paid.props.get('fc_door_idx'),0);
});

test('actual completed-use counts one per event in one instance while preserving native consumption/morality ownership',async()=>{
 const f=await fixture(),r=f.placeDirect(),p=f.player();f.approach(p,r);
 for(let i=0;i<9;i++)f.eat(p);let current=f.runtime.arboretumDoors.getState(r.id);assert.equal(current.progress[0].count,9);assert.equal(current.unlocked,false);
 f.eat(p);current=f.runtime.arboretumDoors.getState(r.id);assert.equal(current.progress[0].count,10);assert.equal(current.unlocked,true);assert.equal(JSON.parse(p.props.get('wd:state')).alignment,-150);
 assert.equal(f.events.some(e=>e[0]==='remove-item'),false);assert.equal(f.payouts.length,0);
 const other=f.placeDirect({dimension:f.dim.id,x:900,y:64,z:900},'other');assert.equal(f.runtime.arboretumDoors.getState(other.id).progress.length,0);
});

test('completed food requires Survival/Adventure; unavailable alignment cannot shortcut pre-normalization full evil',async()=>{
 for(const mode of ['Creative','Spectator','unreadable-mode','unreadable-state','missing-state']){const f=await fixture(),r=f.placeDirect(),p=f.player();f.approach(p,r);
  if(mode==='missing-state'||mode==='unreadable-state')p.props.set('fc_morality',-1000);
  if(mode==='unreadable-mode')f.faults.set(p.id+':mode',1);else if(mode==='unreadable-state'){p.props.set('wd:state',JSON.stringify({schemaVersion:3,alignment:-1000}));f.faults.set(p.id+':read:wd:state',1);}else if(mode==='missing-state')p.props.delete('wd:state');else p.mode=mode;
  f.eat(p);const after=f.runtime.arboretumDoors.getState(r.id),unavailableAlignment=['missing-state','unreadable-state'].includes(mode);assert.equal(after.progress.length,unavailableAlignment?1:0,mode);assert.equal(after.unlocked,false,mode);if(unavailableAlignment)assert.equal(JSON.parse(p.props.get('wd:state')).alignment,-1000,'Existing normalization occurred only after the witness decision');
 }
 for(const mode of ['Survival','Adventure']){const f=await fixture(),r=f.placeDirect(),p=f.player();p.mode=mode;f.approach(p,r);f.eat(p);assert.equal(f.runtime.arboretumDoors.getState(r.id).progress[0].count,1,mode);}
});

test('same object/same tick replay and competing nearby instances never multiply one completed-use credit',async()=>{
 const f=await fixture(),r=f.placeDirect(),p=f.player();f.approach(p,r);const event={source:p,itemStack:{typeId:'fc:crunchy_chick',amount:16},useDuration:0};f.complete(event);f.complete(event);f.complete({...event});assert.equal(f.runtime.arboretumDoors.getState(r.id).progress[0].count,1);
 const next=f.placeDirect({...r.origin,x:r.origin.x+2},'nearby');f.system.currentTick+=24;f.complete({...event});assert.equal(f.runtime.arboretumDoors.getState(r.id).progress[0].count,1);assert.equal(f.runtime.arboretumDoors.getState(next.id).progress.length,0);
});

test('full-evil interaction uses actual raw alignment authority, not old -500 or tier -950 or legacy fallback',async()=>{
 for(const alignment of [-1000,-999,-950,-500,null]){const f=await fixture(),r=f.placeDirect(),p=f.player();f.approach(p,r);p.props.set('fc_morality',-1000);if(alignment===null)p.props.set('wd:state','{broken');else p.props.set('wd:state',JSON.stringify({schemaVersion:3,alignment}));const face=f.face(r.source);f.runtime.demonDoorTalk(p,face,'fc:lantern');assert.equal(f.runtime.arboretumDoors.getState(r.id).unlocked,alignment===-1000,String(alignment));assert.equal(f.payouts.length,0);}
});

test('shared block/item guards and queued return use the occupied ticket exact source across families',async()=>{
 const f=await fixture(),r=f.placeDirect(),p=f.player(),ar=f.api['arboretum_doors.js'],guild=f.api['fc_demon_doors.js'],origin=ar.arboretumOrigin(7);
 const source={...add(r.source,{x:0,y:0,z:-1}),dimension:f.dim.id};p.location=add(origin,ar.ARBORETUM.arrival);p.props.set(ar.ARBORETUM_RETURN_KEY,JSON.stringify({schema:1,family:'arboretum',id:r.id,cell:7,source,door:r.source,phase:'inside'}));
 assert.equal(f.configs.guild.canEnter(p),false);assert.equal(f.runtime.occupiedDoor(p),f.runtime.arboretumDoors);assert.equal(f.runtime.doorWorldPositionExcluded(f.dim.id,p.location),true);
 const b={dimension:f.dim,block:{location:add(origin,{x:0,y:0,z:0})},cancel:false};f.breakBlock(b);assert.equal(b.cancel,true);
 const use={source:p,itemStack:{typeId:'minecraft:ender_pearl'},cancel:false};f.itemUse(use);assert.equal(use.cancel,true);
 const click={player:p,block:{location:add(origin,ar.ARBORETUM.returnDetectorCells[0]),typeId:'minecraft:chiseled_stone_bricks'},cancel:false};f.useBlock(click);assert.equal(click.cancel,true);f.flush();assert.deepEqual(p.location,{x:source.x,y:source.y,z:source.z});assert.equal(p.props.has(ar.ARBORETUM_RETURN_KEY),false);
 p.location=add(guild.realmOrigin(3),guild.ARCANUM.arrival);p.props.set(guild.DOOR_RETURN_KEY,JSON.stringify({schema:1,doorId:'guild',cell:3,source:{x:20.5,y:65,z:20.5,dimension:f.dim.id},phase:'inside'}));assert.equal(f.configs.arbor.canEnter(p),false);assert.equal(f.runtime.occupiedDoor(p),f.runtime.guildDoorPilot);
});

test('deferred return cannot transfer an old clicked arch into another cell or missing ticket authority',async()=>{
 for(const change of ['move-cell','unreadable-ticket']){const f=await fixture(),r=f.placeDirect(),p=f.player(),ar=f.api['arboretum_doors.js'],origin=ar.arboretumOrigin(0),source={...add(r.source,{x:0,y:0,z:-1}),dimension:f.dim.id};p.location=add(origin,ar.ARBORETUM.arrival);p.props.set(ar.ARBORETUM_RETURN_KEY,JSON.stringify({schema:1,family:'arboretum',id:r.id,cell:0,source,door:r.source,phase:'inside'}));
  const click={player:p,block:{location:add(origin,ar.ARBORETUM.returnDetectorCells[0]),typeId:'minecraft:chiseled_stone_bricks'},cancel:false};f.useBlock(click);assert.equal(click.cancel,true);
  if(change==='move-cell')p.location=add(ar.arboretumOrigin(1),ar.ARBORETUM.arrival);else f.faults.set(p.id+':read:'+ar.ARBORETUM_RETURN_KEY,10);f.flush();assert.equal(f.events.filter(e=>e[0]==='teleport').length,0,change);
 }
});

test('successful-placement receipt permits deferred confirmation; absent/uncertain receipt never replays source',async()=>{
 for(const failure of ['receipt-before','receipt-after','confirm-before']){
  const f=await fixture(),p=f.player();let injected=false;
  const hook=(key,value)=>{if(injected||!key.startsWith('fc_dp_arbor_v1_'))return;const r=JSON.parse(value);if(r.placement===(failure==='confirm-before'?'confirmed':'placed')){injected=true;throw Error(failure);}};
  f.world[failure==='receipt-after'?'afterWrite':'beforeWrite']=hook;f.runtime.maybePlace(p,0,0);assert.equal(injected,true,failure);
  const r=f.runtime.arboretumDoors.getPlacement('fc_rgn_0_0');assert.equal(r.placement,failure==='receipt-before'?'pending':'placed',failure);
  f.props.delete('fc_rgn_0_0');f.runtime.maybePlace(p,0,0);f.system.currentTick+=5;f.approach(p,r);f.runtime.ensureArboretumFaces(f.dim);
  assert.equal(f.events.filter(e=>e[0]==='structure').length,1,failure);assert.equal(f.runtime.arboretumDoors.getState(r.id).placement,failure==='receipt-before'?'pending':'confirmed',failure);
 }
});

test('two Heroes retain separate food counters and another family read failure cannot take over entry authority',async()=>{
 const f=await fixture(),r=f.placeDirect(),a=f.player(),b=f.player();f.approach(a,r);f.approach(b,r);
 for(let i=0;i<5;i++){f.eat(a);f.eat(b);}let s=f.runtime.arboretumDoors.getState(r.id);assert.equal(s.unlocked,false);assert.deepEqual(plain(s.progress.map(h=>[h.heroId,h.count])),[[a.id,5],[b.id,5]]);
 for(let i=0;i<5;i++)f.eat(a);s=f.runtime.arboretumDoors.getState(r.id);assert.equal(s.unlocked,true);assert.equal(s.progress.find(h=>h.heroId===b.id).count,5);
 f.faults.set(a.id+':read:'+f.api['fc_demon_doors.js'].DOOR_RETURN_KEY,1);assert.equal(f.configs.arbor.canEnter(a),false);
 f.faults.set(a.id+':read:'+f.api['arboretum_doors.js'].ARBORETUM_RETURN_KEY,1);assert.equal(f.configs.guild.canEnter(a),false);
});

test('actual room adapter accepts final authored geometry and seeds one physical chest after fresh bulk validation',async()=>{
 const f=await fixture(),r=f.placeDirect(),p=f.player();f.approach(p,r);for(let i=0;i<10;i++)f.eat(p);
 for(let i=0;i<400&&f.runtime.arboretumDoors.getState(r.id).room?.phase!=='ready';i++){f.system.currentTick+=5;f.runtime.arboretumDoors.tick();}
 const ready=f.runtime.arboretumDoors.getState(r.id);assert.equal(ready.room.phase,'ready');assert.equal(ready.reward.seeded,true);
 const placed=f.events.filter(e=>e[0]==='structure'&&e[1]==='fc:arboretum');assert.equal(placed.length,1);assert.equal(placed[0][3].includeEntities,false);
 assert.equal(f.events.filter(e=>e[0]==='inventory-write'&&e[3]==='fc:wellows_pickhammer').length,1);assert.ok(f.events.some(e=>e[0]==='bulk'));
});

test('late edited block or unavailable final bulk query refuses room placement after sliced scan',async()=>{
 for(const failure of ['late-block','unloaded']){const f=await fixture(),r=f.placeDirect(),p=f.player();f.approach(p,r);for(let i=0;i<10;i++)f.eat(p);const origin=f.runtime.arboretumDoors.getState(r.id).room.origin;
  if(failure==='late-block')f.dim.beforeBulk=()=>{f.blockAt(origin).typeId='minecraft:diamond_block';};else f.faults.set('bulk',1);
  for(let i=0;i<400&&!f.events.some(e=>e[0]==='bulk');i++){f.system.currentTick+=5;f.runtime.arboretumDoors.tick();}
  assert.ok(f.events.some(e=>e[0]==='bulk'),failure);assert.equal(f.events.filter(e=>e[0]==='structure'&&e[1]==='fc:arboretum').length,0,failure);
  if(failure==='late-block')assert.equal(f.blockAt(origin).typeId,'minecraft:diamond_block');assert.equal(f.events.filter(e=>e[0]==='inventory-write').length,0);
 }
});

test('an unavailable other-family ticket blocks new entry without blocking a healthy own exact-source return',async()=>{
 for(const own of ['arboretum','guild']){const f=await fixture(),p=f.player(),ar=f.api['arboretum_doors.js'],guild=f.api['fc_demon_doors.js'];let source;
  if(own==='arboretum'){const r=f.placeDirect();source={...add(r.source,{x:0,y:0,z:-1}),dimension:f.dim.id};p.location=add(ar.arboretumOrigin(2),ar.ARBORETUM.arrival);p.props.set(ar.ARBORETUM_RETURN_KEY,JSON.stringify({schema:1,family:'arboretum',id:r.id,cell:2,source,door:r.source,phase:'inside'}));f.faults.set(p.id+':read:'+guild.DOOR_RETURN_KEY,100);assert.equal(f.configs.arbor.canEnter(p),false);}
  else{source={x:20.5,y:65,z:20.5,dimension:f.dim.id};p.location=add(guild.realmOrigin(2),guild.ARCANUM.arrival);p.props.set(guild.DOOR_RETURN_KEY,JSON.stringify({schema:1,doorId:'guild',cell:2,source,phase:'inside'}));f.faults.set(p.id+':read:'+ar.ARBORETUM_RETURN_KEY,100);assert.equal(f.configs.guild.canEnter(p),false);}
  assert.equal(f.runtime.requestDoorReturn(p),true,own);assert.deepEqual(p.location,{x:source.x,y:source.y,z:source.z});
 }
});

test('a shell hole edited after sliced verification refuses ready state and reward seeding',async()=>{
 const f=await fixture(),r=f.placeDirect(),p=f.player();f.approach(p,r);for(let i=0;i<10;i++)f.eat(p);const origin=f.runtime.arboretumDoors.getState(r.id).room.origin;let injected=false;
 f.dim.beforeBulk=(volume,filter)=>{if(filter.excludeTypes[0]==='minecraft:barrier'){injected=true;f.blockAt(origin).typeId='minecraft:air';}};
 for(let i=0;i<400&&!injected;i++){f.system.currentTick+=5;f.runtime.arboretumDoors.tick();}
 assert.equal(injected,true);const after=f.runtime.arboretumDoors.getState(r.id);assert.notEqual(after.room.phase,'ready');assert.equal(after.reward.seeded,false);assert.equal(f.events.filter(e=>e[0]==='inventory-write').length,0);assert.equal(f.blockAt(origin).typeId,'minecraft:air');
});

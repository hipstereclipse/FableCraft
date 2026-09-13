// Audit prototype only. Actual station/lane/session code is executed; the proposed
// arrival predicate below is not installed in the behavior pack or engine.
import assert from 'node:assert/strict';
import vm from 'node:vm';
import {readFileSync} from 'node:fs';
import {parse} from 'espree';
const input=JSON.parse(readFileSync(0,'utf8'));
const source=readFileSync('packs/Fablecraft_BP/scripts/main.js','utf8');
const ast=parse(source,{ecmaVersion:'latest',sourceType:'module',range:true});
const context=vm.createContext({});
const training=new vm.SourceTextModule(readFileSync('packs/Fablecraft_BP/scripts/guild_training.js','utf8'),{context});
await training.link(()=>{throw Error('Unexpected import');});await training.evaluate();
for(const name of ['GUILD','localGuildPoint','guildSkillLaneClear']){
  const node=ast.body.find(n=>n.type==='FunctionDeclaration'&&n.id.name===name||n.type==='VariableDeclaration'&&n.declarations.some(d=>d.id.name===name));
  assert.ok(node,name);vm.runInContext(source.slice(...node.range),context);
}
const {station,target,lane}=vm.runInContext('({station:localGuildPoint({x:0,y:0,z:0},GUILD.training.range),target:localGuildPoint({x:0,y:0,z:0},GUILD.training.target,2.45),lane:guildSkillLaneClear})',context);
assert.deepEqual({...station},{x:83.5,y:1,z:39.5});
const cells=new Map(Object.entries(input.cells)),key=p=>`${Math.floor(p.x)},${Math.floor(p.y)},${Math.floor(p.z)}`;
const dim={id:'minecraft:overworld',getBlock(p){const typeId=cells.get(key(p));return typeId===undefined?undefined:{typeId,isAir:typeId==='minecraft:air'};}};
let placements=0;const tags=new Set();
const npc={id:'saved-range',typeId:'fc:guild_apprentice_skill',isValid:true,dimension:dim,location:{x:86.5,y:1,z:39.5},
  getTags:()=>[...tags],addTag:t=>tags.add(t),removeTag:t=>tags.delete(t),triggerEvent(){},
  tryTeleport(p){placements++;this.location={...p};return true;}};
const ctl=training.namespace.createGuildTrainingController({now:()=>10,session:()=>0,canTrain:()=>true});
ctl.beginPass([npc]);assert.notEqual(ctl.acquire(npc,'fc_train_range',station,target),null);assert.equal(placements,1);
const currentBaseline={actual_acquire_teleports:placements,location_after:{...npc.location}};
const snapshot={entityId:npc.id,session:7,token:19,activityRevision:4,deadline:600};
const fresh=()=>({entityId:npc.id,session:7,token:19,activityRevision:4,now:100,boundSlot:'skill_range',activityBlocked:false,activityMode:'idle',married:0,spouseOwner:'',defending:false,aggravated:false});
function uniqueLandmark(){
  let count=0;
  for(const [where,type] of cells){if(type===undefined)return false;if(type==='minecraft:fletching_table'){if(where!=='91,1,40')return false;count++;}}
  return count===1&&cells.get('91,0,40')==='minecraft:coarse_dirt';
}
function candidateArrival(state){
  // Wake-up events carry no target block/token. All authority comes from the
  // current approach record and fresh world reads, including actual footprint.
  try{return npc.isValid===true&&npc.dimension.id==='minecraft:overworld'
    &&state.entityId===snapshot.entityId&&state.boundSlot==='skill_range'
    &&state.session===snapshot.session&&state.token===snapshot.token&&state.activityRevision===snapshot.activityRevision
    &&state.now<snapshot.deadline&&!state.activityBlocked&&state.activityMode==='idle'
    &&state.married===0&&(state.spouseOwner===''||state.spouseOwner===undefined)&&!state.defending&&!state.aggravated
    &&Math.hypot(npc.location.x-station.x,npc.location.y-station.y,npc.location.z-station.z)<=.25
    &&uniqueLandmark()&&training.namespace.guildStationClear(npc,station)
    &&training.namespace.guildStationClear(npc,npc.location)&&lane(npc,target,station)&&lane(npc,target);
  }catch{return false;}
}
assert.equal(candidateArrival(fresh()),true);
const negatives=[];
for(const [label,where,value] of [
  ['missing table','91,1,40','minecraft:air'],['replaced table','91,1,40','minecraft:chest'],
  ['replaced table support','91,0,40','minecraft:stone'],
  ['alternate closer table','84,1,40','minecraft:fletching_table'],['unavailable scan cell','72,0,28',undefined],
  ['alternate below-base table','84,-1,40','minecraft:fletching_table'],['unreadable below-base cell','72,-1,28',undefined],
  ['removed station support','83,0,39','minecraft:air'],['blocked station head','83,2,39','minecraft:chest'],
  ['replaced target','83,2,34','minecraft:chest'],['missing target support','83,1,34','minecraft:air'],
  ['blocked ray','83,2,37','minecraft:chest']]){
  const old=cells.get(where);cells.set(where,value);assert.equal(candidateArrival(fresh()),false,label);assert.equal(cells.get(where),value);cells.set(where,old);negatives.push(label);
}
for(const [label,change] of Object.entries({wrongIdentity:{entityId:'copied'},wrongSlot:{boundSlot:'skill_hall'},endedSession:{session:8},staleCallback:{token:18},reloadedWithoutApproach:{token:null},preemptedActivity:{activityRevision:5},follow:{activityMode:'follow'},wait:{activityMode:'wait'},unavailableActivity:{activityBlocked:true},married:{married:1,spouseOwner:'hero'},unreadableMarriage:{married:undefined},defence:{defending:true},aggravated:{aggravated:true},timeout:{now:600}})){
  assert.equal(candidateArrival({...fresh(),...change}),false,label);negatives.push(label);
}
const location={...npc.location};npc.location={x:91.5,y:1,z:40.5};assert.equal(candidateArrival(fresh()),false);negatives.push('table location is not the station');npc.location=location;
const corridor=[];for(let x=83.5;x<=86.5;x+=.25){const p={x,y:1,z:39.5};assert.equal(training.namespace.guildStationClear(npc,p),true);corridor.push(p);}
assert.equal(placements,1,'Prototype did not teleport');
const anchors={corner:[91,1,40],horizontalCenter:[91.5,1,40.5],volumeCenter:[91.5,1.5,40.5]};
const offsets=Object.fromEntries(Object.entries(anchors).map(([name,p])=>[name,[station.x-p[0],station.y-p[1],station.z-p[2]]]));
console.log(JSON.stringify({current_baseline:currentBaseline,station,target,proposed_landmark:{x:91,y:1,z:40},
  sampled_clear_corridor_points:corridor.length,prototype_accepts_verified_mark:true,prototype_negative_cases:negatives,
  candidate_offsets_requiring_engine_calibration:offsets,production_repair_implemented:false,
  engine_target_offset_semantics:'unresolved',engine_pathfinding:'unrun'}));

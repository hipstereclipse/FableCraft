// GP15/GP16: production Skill station, lane and shot on final Guild voxels.
// Actual session callbacks run at mocked engine boundaries; native acceptance
// remains unrun. Edited and unavailable geometry must refuse harmless effects.
import assert from 'node:assert/strict';
import vm from 'node:vm';
import {readFileSync} from 'node:fs';
import {parse} from 'espree';
const input=JSON.parse(readFileSync(0,'utf8'));
const source=readFileSync('packs/Fablecraft_BP/scripts/main.js','utf8');
const ast=parse(source,{ecmaVersion:'latest',sourceType:'module',range:true});
const context=vm.createContext({});
const module=new vm.SourceTextModule(readFileSync('packs/Fablecraft_BP/scripts/guild_training.js','utf8'),{context});
await module.link(()=>{throw new Error('Unexpected engine import');});await module.evaluate();
for(const name of ['GUILD','localGuildPoint','guildSkillLaneClear','showPracticeShot']){
  const node=ast.body.find(n=>n.type==='FunctionDeclaration'&&n.id.name===name||n.type==='VariableDeclaration'&&n.declarations.some(d=>d.id.name===name));
  assert.ok(node,`Production declaration ${name}`);
  vm.runInContext(source.slice(...node.range),context);
}
const base={x:100,y:64,z:-200};context.base=base;
const scheduler=ast.body.find(n=>n.type==='ExpressionStatement'&&n.expression.type==='CallExpression'
  &&source.slice(...n.range).startsWith('system.runInterval(')&&source.slice(...n.range).includes('guildTraining.beginPass'));
for(const name of ['range','target']){
  const node=scheduler.expression.arguments[0].body.body.find(n=>n.type==='VariableDeclaration'&&n.declarations.some(d=>d.id.name===name));
  vm.runInContext(source.slice(...node.range),context);
}
const {station,target,shot,lane}=vm.runInContext('({station:range,target,shot:showPracticeShot,lane:guildSkillLaneClear})',context);
assert.deepEqual({...station},{x:183.5,y:65,z:-160.5});
assert.deepEqual({...target},{x:183.5,y:66.45,z:-165.5});
const cells=new Map(Object.entries(input.cells)), particles=[],sounds=[];
const key=p=>`${Math.floor(p.x)-base.x},${Math.floor(p.y)-base.y},${Math.floor(p.z)-base.z}`;
const dim={id:'minecraft:overworld',getBlock(p){
  const value=cells.get(key(p));
  return value===undefined?undefined:{typeId:value,isAir:value==='minecraft:air'};
},spawnParticle(id,p){particles.push({id,p});},playSound(id){sounds.push(id);}};
const entity={id:'saved-skill',isValid:true,dimension:dim,location:station,tags:new Set(),
  getTags(){return [...this.tags];},removeTag(t){this.tags.delete(t);},addTag(t){this.tags.add(t);},
  triggerEvent(){},tryTeleport(p,options){assert.equal(options.checkForBlocks,true);this.location={...p};return true;}};
function acquire(){
  const ctl=module.namespace.createGuildTrainingController({now:()=>10,session:()=>0,canTrain:()=>true});
  context.guildTraining=ctl;ctl.beginPass([entity]);
  const token=ctl.acquire(entity,'fc_train_range',station,target);assert.notEqual(token,null);
  return {ctl,token};
}
assert.equal(module.namespace.guildStationClear(entity,station),true);
assert.equal(lane(entity,target,station),true);
const initial=acquire();shot(entity,target,initial.token);
assert.equal(particles.length,6);
assert.deepEqual({...particles[5].p},{...target});
assert.equal(cells.get(key(target)),'minecraft:target');
// Recover the actual callback's line origin from its equally spaced outputs.
const start={},first=particles[0].p,last=particles[5].p;
for(const axis of ['x','y','z'])start[axis]=last[axis]-(last[axis]-first[axis])*6/5;
function clearRay(){
  for(let i=0;i<100;i++){
    const p={};for(const axis of ['x','y','z'])p[axis]=start[axis]+(target[axis]-start[axis])*i/100;
    if(key(p)!==key(target)&&cells.get(key(p))!=='minecraft:air')return false;
  }
  return true;
}
assert.equal(clearRay(),true,'New board must stay behind the existing target');
const negatives=[
  ['83,0,39','minecraft:air','station'],
  ['83,2,39','minecraft:chest','station'],
  ['83,2,37','minecraft:chest','lane'],
  ['83,2,37',undefined,'lane'],
  ['83,2,34','minecraft:air','lane'],
  ['83,2,34','minecraft:chest','lane'],
  ['83,2,34',undefined,'lane'],
  ['83,1,34','minecraft:air','lane'],
  ['83,1,34','minecraft:oak_fence','lane'],
  ['83,1,34',undefined,'lane'],
];
for(const [where,value,kind] of negatives){
  const {ctl,token}=acquire(),old=cells.get(where);
  cells.set(where,value);particles.length=0;sounds.length=0;
  assert.equal(kind==='station'?module.namespace.guildStationClear(entity,station):lane(entity,target),false,where);
  shot(entity,target,token);
  assert.equal(particles.length,0,where);assert.equal(sounds.length,0,where);
  assert.equal(ctl.reserved(entity),false,where);
  assert.equal(cells.get(where),value,'Refusal must not repair saved geometry');
  cells.set(where,old);
}
// Survey all cells actually crossed by the callback's line independently of
// its preflight implementation, including actors displaced within tolerance.
let crossedCellNegatives=0;
for(const offset of [{x:0,y:0,z:0},{x:.7,y:0,z:.2},{x:-.7,y:0,z:-.2},
  {x:0,y:.7,z:.34},{x:0,y:.66,z:-.34}]){
  const {ctl,token}=acquire();entity.location={x:station.x+offset.x,y:station.y+offset.y,z:station.z+offset.z};
  assert.equal(ctl.isActive(entity,token),true);
  assert.equal(lane(entity,target),true);
  const origin={...entity.location,y:entity.location.y+1.35},crossed=new Set();
  for(let i=0;i<10000;i++){
    const p={};for(const axis of ['x','y','z'])p[axis]=origin[axis]+(target[axis]-origin[axis])*i/10000;
    if(key(p)!==key(target))crossed.add(key(p));
  }
  for(const where of crossed){
    const old=cells.get(where);cells.set(where,'minecraft:chest');
    assert.equal(lane(entity,target),false,`Crossed cell ${where}, offset ${JSON.stringify(offset)}`);
    cells.set(where,old);crossedCellNegatives++;
  }
}
console.log(JSON.stringify({station,target,actual_emitted_particles_on_clear_lane:6,
  final_generated_station_clear:true,offline_ray_clear:true,negative_cases:negatives.length,
  crossed_cell_negatives:crossedCellNegatives,runtime_skill_lane_preflight:true,engine_acceptance:'unrun'}));

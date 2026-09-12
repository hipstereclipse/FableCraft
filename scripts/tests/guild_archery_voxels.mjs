// GP15: actual production Skill station/shot evaluated on final Guild voxels.
// The Skill callback is cosmetic and has no runtime block-lane preflight. The
// ray survey below is an offline geometric check, not a new runtime guarantee.
import assert from 'node:assert/strict';
import vm from 'node:vm';
import {readFileSync} from 'node:fs';
import {parse} from 'espree';
const input=JSON.parse(readFileSync(0,'utf8'));
const source=readFileSync('packs/Fablecraft_BP/scripts/main.js','utf8');
const ast=parse(source,{ecmaVersion:'latest',sourceType:'module',range:true});
const context=vm.createContext({guildTraining:{isActive:()=>true}});
const module=new vm.SourceTextModule(readFileSync('packs/Fablecraft_BP/scripts/guild_training.js','utf8'),{context});
await module.link(()=>{throw new Error('Unexpected engine import');});await module.evaluate();
for(const name of ['GUILD','localGuildPoint','showPracticeShot']){
  const node=ast.body.find(n=>n.type==='FunctionDeclaration'&&n.id.name===name||n.type==='VariableDeclaration'&&n.declarations.some(d=>d.id.name===name));
  vm.runInContext(source.slice(...node.range),context);
}
const base={x:100,y:64,z:-200};context.base=base;
const scheduler=ast.body.find(n=>n.type==='ExpressionStatement'&&n.expression.type==='CallExpression'
  &&source.slice(...n.range).startsWith('system.runInterval(')&&source.slice(...n.range).includes('guildTraining.beginPass'));
for(const name of ['range','target']){
  const node=scheduler.expression.arguments[0].body.body.find(n=>n.type==='VariableDeclaration'&&n.declarations.some(d=>d.id.name===name));
  vm.runInContext(source.slice(...node.range),context);
}
const {station,target,shot}=vm.runInContext('({station:range,target,shot:showPracticeShot})',context);
assert.deepEqual({...station},{x:183.5,y:65,z:-160.5});
assert.deepEqual({...target},{x:183.5,y:66.45,z:-165.5});
const cells=new Map(Object.entries(input.cells)), particles=[];
const key=p=>`${Math.floor(p.x)-base.x},${Math.floor(p.y)-base.y},${Math.floor(p.z)-base.z}`;
const dim={id:'minecraft:overworld',getBlock(p){
  const value=cells.get(key(p));
  return value===undefined?undefined:{typeId:value,isAir:value==='minecraft:air'};
},spawnParticle(id,p){particles.push({id,p});},playSound(){}};
const entity={dimension:dim,location:station};
assert.equal(module.namespace.guildStationClear(entity,station),true);
shot(entity,target,1);
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
for(const [where,value,check] of [
  ['83,0,39','minecraft:air',()=>module.namespace.guildStationClear(entity,station)],
  ['83,2,39','minecraft:chest',()=>module.namespace.guildStationClear(entity,station)],
  ['83,2,37','minecraft:chest',clearRay],
]){
  const old=cells.get(where);cells.set(where,value);assert.equal(check(),false,where);cells.set(where,old);
}
console.log(JSON.stringify({station,target,actual_emitted_particles:particles.length,
  final_generated_station_clear:true,offline_ray_clear:true,negative_cases:3,
  runtime_skill_lane_preflight:'absent; this change preserves the geometric ray only',engine_acceptance:'unrun'}));

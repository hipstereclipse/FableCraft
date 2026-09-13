// Execute the actual Skill shot at each retained within-tolerance displacement.
// Output the emitted line's reconstructed origin for independent shape checking.
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
for(const name of ['GUILD','localGuildPoint','guildSkillLaneClear','showPracticeShot']){
  const node=ast.body.find(n=>n.type==='FunctionDeclaration'&&n.id.name===name||n.type==='VariableDeclaration'&&n.declarations.some(d=>d.id.name===name));
  assert.ok(node,name);vm.runInContext(source.slice(...node.range),context);
}
const {station,target,shot}=vm.runInContext('({station:localGuildPoint({x:0,y:0,z:0},GUILD.training.range),target:localGuildPoint({x:0,y:0,z:0},GUILD.training.target,2.45),shot:showPracticeShot})',context);
const cells=new Map(Object.entries(input.cells)),particles=[],key=p=>`${Math.floor(p.x)},${Math.floor(p.y)},${Math.floor(p.z)}`;
const dim={id:'minecraft:overworld',getBlock(p){const typeId=cells.get(key(p));return typeId===undefined?undefined:{typeId,isAir:typeId==='minecraft:air'};},spawnParticle(id,p){particles.push({...p});},playSound(){}};
const entity={id:'saved-skill',isValid:true,dimension:dim,location:{...station},tags:new Set(),
  getTags(){return [...this.tags];},removeTag(t){this.tags.delete(t);},addTag(t){this.tags.add(t);},triggerEvent(){},
  tryTeleport(p,options){assert.equal(options.checkForBlocks,true);this.location={...p};return true;}};
const rays=[];
for(const offset of [{x:0,y:0,z:0},{x:.7,y:0,z:.2},{x:-.7,y:0,z:-.2},{x:0,y:.7,z:.34},{x:0,y:.66,z:-.34}]){
  const ctl=training.namespace.createGuildTrainingController({now:()=>10,session:()=>0,canTrain:()=>true});
  context.guildTraining=ctl;ctl.beginPass([entity]);const token=ctl.acquire(entity,'fc_train_range',station,target);assert.notEqual(token,null);
  entity.location={x:station.x+offset.x,y:station.y+offset.y,z:station.z+offset.z};assert.equal(ctl.isActive(entity,token),true);
  particles.length=0;shot(entity,target,token);assert.equal(particles.length,6);
  const origin={};for(const axis of ['x','y','z'])origin[axis]=particles[5][axis]-(particles[5][axis]-particles[0][axis])*6/5;
  rays.push({offset,actual_feet:{...entity.location},origin,target:{...particles[5]},particles:[...particles]});
}
console.log(JSON.stringify({scope:'Actual callback lines at mocked engine boundary',station,target,rays,native_collision:'unrun'}));

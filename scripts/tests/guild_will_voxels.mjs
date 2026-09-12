// Production Will lane/station preflight against the final Guild generator voxels.
import assert from 'node:assert/strict';
import vm from 'node:vm';
import { readFileSync } from 'node:fs';
import { parse } from 'espree';
const input=JSON.parse(readFileSync(0,'utf8'));
const source=readFileSync('packs/Fablecraft_BP/scripts/main.js','utf8');
const ast=parse(source,{ecmaVersion:'latest',sourceType:'module',range:true});
const context=vm.createContext({});
const module=new vm.SourceTextModule(readFileSync('packs/Fablecraft_BP/scripts/guild_training.js','utf8'),{context});
await module.link(()=>{throw new Error('Unexpected engine import');});await module.evaluate();
for(const name of ['GUILD','localGuildPoint','guildWillLaneClear']){
  const node=ast.body.find(n=>n.type==='FunctionDeclaration'&&n.id.name===name||n.type==='VariableDeclaration'&&n.declarations.some(d=>d.id.name===name));
  vm.runInContext(source.slice(...node.range),context);
}
const base={x:100,y:64,z:-200};context.base=base;
const scheduler=ast.body.find(n=>n.type==='ExpressionStatement'&&n.expression.type==='CallExpression'
  &&source.slice(...n.range).startsWith('system.runInterval(')&&source.slice(...n.range).includes('guildTraining.beginPass'));
for(const name of ['willStation','willTarget']){
  const node=scheduler.expression.arguments[0].body.body.find(n=>n.type==='VariableDeclaration'&&n.declarations.some(d=>d.id.name===name));
  vm.runInContext(source.slice(...node.range),context);
}
const {station,target,lane}=vm.runInContext('({station:willStation,target:willTarget,lane:guildWillLaneClear})',context);
assert.deepEqual({...station},{x:base.x+input.station[0]+.5,y:base.y+1,z:base.z+input.station[1]+.5});
assert.deepEqual({...target},{x:base.x+60.5,y:base.y+3.75,z:base.z+85.5});
const cells=new Map(Object.entries(input.cells));
const dim={id:'minecraft:overworld',getBlock(p){
  const value=cells.get(`${p.x-base.x},${p.y-base.y},${p.z-base.z}`);
  return value===undefined?undefined:{typeId:value,isAir:value==='minecraft:air'};
}};
const entity={id:'saved-will',isValid:true,dimension:dim,location:station,tags:new Set(),
  getTags(){return [...this.tags];},removeTag(t){this.tags.delete(t);},addTag(t){this.tags.add(t);},
  triggerEvent(){},tryTeleport(p,options){assert.equal(options.checkForBlocks,true);this.location={...p};return true;}};
assert.equal(module.namespace.guildStationClear(entity,station),true);
assert.equal(lane(entity,target,station),true,'Final generated dummy arm must not block the actual ray');
const ctl=module.namespace.createGuildTrainingController({now:()=>10,session:()=>0,canTrain:()=>true});
ctl.beginPass([entity]);const token=ctl.acquire(entity,'fc_train_will',station,target);assert.notEqual(token,null);
for(const [key,value,check] of [
  ['60,0,88','minecraft:diamond_block',()=>module.namespace.guildStationClear(entity,station)],
  ['60,2,88','minecraft:chest',()=>module.namespace.guildStationClear(entity,station)],
  ['60,3,85','minecraft:air',()=>lane(entity,target,station)],
  ['60,2,85','minecraft:air',()=>lane(entity,target,station)],
  ['60,3,86','minecraft:chest',()=>lane(entity,target,station)],
  ['60,2,87',undefined,()=>lane(entity,target,station)],
]){
  const old=cells.get(key);cells.set(key,value);assert.equal(check(),false,key);cells.set(key,old);
}
console.log(JSON.stringify({station,target,final_generated_preflight:true,negative_cases:6,engine_acceptance:'unrun'}));

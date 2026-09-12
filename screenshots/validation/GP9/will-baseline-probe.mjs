// GP9 read-only execution of the pre-fix main scheduler at mocked engine boundaries.
// Pass the saved main.js path; the sibling guild_training.js is its lifecycle owner.
import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';
import crypto from 'node:crypto';
import { parse } from 'espree';
const filename=process.argv[2];if(!filename)throw new Error('Expected baseline main.js path');
const source=fs.readFileSync(filename,'utf8');
const training=fs.readFileSync(path.join(path.dirname(filename),'guild_training.js'),'utf8');
const ast=parse(source,{ecmaVersion:'latest',sourceType:'module',range:true});
async function probe(mightCount){
  const context=vm.createContext({});const module=new vm.SourceTextModule(training,{context});
  await module.link(()=>{});await module.evaluate();
  let tick=10;const entities=[];
  const dimension={id:'minecraft:overworld',getBlock:p=>({typeId:p.y===0?'minecraft:coarse_dirt':'minecraft:air',isAir:p.y>0}),
    getEntities:q=>entities.filter(e=>!q.type||q.type===e.typeId)};
  for(const type of [...Array(mightCount).fill('might'),'skill','will','will']){
    entities.push({id:`${type}-${entities.length}`,typeId:`fc:guild_apprentice_${type}`,dimension,
      location:{x:12,y:1,z:42},tags:new Set(),placements:[],isValid:true,
      hasTag(t){return this.tags.has(t);},getTags(){return [...this.tags];},removeTag(t){this.tags.delete(t);},addTag(t){this.tags.add(t);},
      triggerEvent(){},tryTeleport(p){this.placements.push(p);this.location={...p};return true;},playAnimation(){}});
  }
  Object.assign(context,{...Object.fromEntries(Object.keys(module.namespace).map(k=>[k,module.namespace[k]])),
    TICKS:()=>tick,OW:()=>dimension,world:{getDynamicProperty:()=>true,getTimeOfDay:()=>1000},
    system:{runTimeout(){}},guildBounds:()=>({base:{x:0,y:0,z:0}}),isInsideGuild:()=>true,isMarried:()=>false,
    placeGuildAnnexes(){},repairGuildTerrain(){},repairGuildSkirtVegetation(){}});
  for(const name of ['APPRENTICE_TYPES','GUILD','nextSparTick','nextArcheryTick','sparTurn','guildTraining',
    'guildApprentices','localGuildPoint','distanceXZ','playSparExchange','showPracticeShot']){
    const node=ast.body.find(n=>n.type==='FunctionDeclaration'&&n.id.name===name||n.type==='VariableDeclaration'&&n.declarations.some(d=>d.id.name===name));
    vm.runInContext(source.slice(...node.range),context);
  }
  const interval=ast.body.find(n=>n.type==='ExpressionStatement'&&n.expression.type==='CallExpression'
    &&source.slice(...n.range).startsWith('system.runInterval(')&&source.slice(...n.range).includes('guildTraining.beginPass'));
  const callback=vm.runInContext(`(${source.slice(...interval.expression.arguments[0].range)})`,context);
  for(tick=10;tick<=100;tick+=10)callback();
  return entities.map(e=>({id:e.id,type:e.typeId,roles:[...e.tags],placements:e.placements.length,location:e.location}));
}
console.log(JSON.stringify({source:filename,source_sha256:crypto.createHash('sha256').update(source).digest('hex'),
  lifecycle_sha256:crypto.createHash('sha256').update(training).digest('hex'),
  full_might_pair:await probe(2),missing_might_partner:await probe(1),
  limits:'Actual scheduler and lifecycle, mocked engine. No Bedrock navigation or animation acceptance.'},null,2));

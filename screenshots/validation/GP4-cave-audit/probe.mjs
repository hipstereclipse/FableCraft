import fs from 'node:fs';
import vm from 'node:vm';
const folder=process.argv[2];
if(!folder)throw new Error('Run through run_probe.py');
const source=fs.readFileSync('screenshots/validation/GP4-cave-audit/source_callbacks.js','utf8');
const structures=JSON.parse(fs.readFileSync(`${folder}/structures.json`,'utf8'));
const base={x:0,y:40,z:0}, key=({x,y,z})=>`${Math.floor(x)},${Math.floor(y)},${Math.floor(z)}`;
function fixture(missing=null){
 const blocks=new Map(),properties=new Map([['fc_guild_base',JSON.stringify(base)]]),jobs=[],timeouts=[],cullis=[];let writes=0;
 function place(name,at){const v=structures[name], [sx,sy,sz]=v.size;for(let x=0;x<sx;x++)for(let y=0;y<sy;y++)for(let z=0;z<sz;z++)blocks.set(key({x:x+at.x,y:y+at.y,z:z+at.z}),v.palette[v.grid[x*sy*sz+y*sz+z]]);}
 place('guild_hall',base);
 const dim={getBlock(at){if(key(at)===missing)return undefined;return {get typeId(){return (blocks.get(key(at))??[at.y<base.y?'minecraft:stone':'minecraft:air',{}])[0];},get isAir(){return this.typeId==='minecraft:air';},setType(type){blocks.set(key(at),[type,{}]);writes++;}};}};
 const world={getDynamicProperty:k=>properties.get(k),setDynamicProperty:(k,v)=>properties.set(k,v),structureManager:{place(id,_dim,at){place(id.replace('fc:',''),at);}}};
 const system={runJob:g=>jobs.push(g),runTimeout:(fn,delay)=>timeouts.push({fn,delay})};
 const deterministicMath=Object.create(Math);deterministicMath.random=()=>0.5;
 const context=vm.createContext({Math:deterministicMath,world,system,registerCullis:(name,at)=>cullis.push({name,at}),fillLootChests(){},hangChamberArt(){}});
 vm.runInContext(source+'\nglobalThis.carveGuildCaves=carveGuildCaves;globalThis.placeGuildAnnexes=placeGuildAnnexes;globalThis.isCullisConfigured=isCullisConfigured;',context);
 const finishJobs=()=>{while(jobs.length){const g=jobs.shift();while(!g.next().done){}}};
 return {blocks,properties,jobs,timeouts,cullis,context,dim,finishJobs,writes:()=>writes,
   at(x,y,z){return blocks.get(`${x},${y},${z}`)??[y<base.y?'minecraft:stone':'minecraft:air',{}];}};
}
const clean=fixture();clean.context.placeGuildAnnexes(clean.dim);
const scheduled={done:clean.properties.get('fc_guild_caves_done'),writes:clean.writes(),jobs:clean.jobs.length};
clean.finishJobs();for(const t of clean.timeouts.sort((a,b)=>a.delay-b.delay)){t.fn();clean.finishJobs();}
const probes={};for(const [name,p]of Object.entries({entryFloor:[27,40,16],entryBelow:[27,39,16],firstSlab:[27,40,15],causewayFloor:[26,19,16],causewayFeet:[26,20,16],cullisDeck:[26,22,42],cullisFeet:[26,23,42],registeredCullisFeet:[26,25,42]}))probes[name]={at:p,block:clean.at(...p)};
const interrupted=fixture();interrupted.context.placeGuildAnnexes(interrupted.dim);const g=interrupted.jobs.shift();g.next();g.next();const interruptedWrites=interrupted.writes();interrupted.jobs.length=0;interrupted.context.carveGuildCaves(interrupted.dim,base);
const unavailable=fixture('26,20,16');unavailable.context.placeGuildAnnexes(unavailable.dim);unavailable.finishJobs();const unavailableWrites=unavailable.writes();unavailable.context.carveGuildCaves(unavailable.dim,base);
const report={scope:'Actual extracted production callbacks over generated Guild/Chamber voxels in solid stone; no engine execution.',scheduled,probes,cullis:clean.cullis,interrupted:{done:interrupted.properties.get('fc_guild_caves_done'),writes:interruptedWrites,retryJobs:interrupted.jobs.length},unavailable:{done:unavailable.properties.get('fc_guild_caves_done'),unwrittenBlock:unavailable.at(26,20,16),retryJobs:unavailable.jobs.length,extraWrites:unavailable.writes()-unavailableWrites}};
report.cullisConfigured={registered:clean.context.isCullisConfigured(clean.dim,{x:26,y:25,z:42}),atActualDaisFeet:clean.context.isCullisConfigured(clean.dim,{x:26,y:23,z:42})};
fs.writeFileSync(`${folder}/runtime-report.json`,JSON.stringify(report,null,2)+'\n');
const cells=[];for(let x=10;x<=42;x++)for(let y=1;y<=48;y++)for(let z=10;z<=57;z++)cells.push([x,y,z,...clean.at(x,y,z)]);
fs.writeFileSync(`${folder}/assembled.json`,JSON.stringify(cells));
console.log(JSON.stringify(report,null,2));

import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import vm from 'node:vm';
const input=JSON.parse(readFileSync(0,'utf8'));
const root=new URL('../../../',import.meta.url);
const main=readFileSync(new URL('packs/Fablecraft_BP/scripts/main.js',root),'utf8');
function declaration(name,end){const start=main.indexOf('const '+name+' =');assert.ok(start>=0);const stop=main.indexOf(end,start)+end.length;return main.slice(start,stop);}
const context=vm.createContext({});
vm.runInContext(declaration('GUILD','\n});')+'\n'+declaration('GUILD_RESIDENT_SLOTS','\n];')+'\nglobalThis.slots=GUILD_RESIDENT_SLOTS;',context);
const module=new vm.SourceTextModule(readFileSync(new URL('packs/Fablecraft_BP/scripts/guild_residents.js',root),'utf8'),{context});
await module.link(()=>{throw Error('resident controller dependencies changed');});await module.evaluate();
const spawnPoint=module.namespace.guildResidentSpawnPoint;
function fixture(vox,allowed=null,mode='ok'){
 return {getBlock(p){if(mode==='blocks-unavailable')return undefined;const {x,y,z}=p;if(x<0||y<0||z<0||x>=vox.size[0]||y>=vox.size[1]||z>=vox.size[2])return undefined;const typeId=vox.palette[vox.grid[x*vox.size[1]*vox.size[2]+y*vox.size[2]+z]][0];return {typeId,isAir:typeId==='minecraft:air'};},
  getEntities({location}){if(mode==='entities-unavailable')throw Error('unavailable occupants');return allowed===null||`${location.x},${location.z}`===allowed?[]:[{id:'occupied-candidate'}];}};
}
const defaults={},slotHomes=[];
for(const label of ['before','after']){
 defaults[label]={};
 for(const slot of context.slots){const home={...slot.home,y:slot.home.y??1};if(label==='before')slotHomes.push({id:slot.id,type:slot.type,home});const point=spawnPoint(fixture(input[label]),home,slot);defaults[label][slot.id]=point??null;
  assert.equal(spawnPoint(fixture(input[label],null,'blocks-unavailable'),home,slot),undefined);
  assert.equal(spawnPoint(fixture(input[label],null,'entities-unavailable'),home,slot),undefined);
 }
}
for(const slot of context.slots){const prior=defaults.before[slot.id];if(prior){const current=spawnPoint(fixture(input.after,`${prior.x},${prior.z}`),{...slot.home,y:slot.home.y??1},slot);assert.deepEqual(JSON.parse(JSON.stringify(current)),JSON.parse(JSON.stringify(prior)));}}
const skill=context.slots.find(slot=>slot.id==='skill_hall'),home={...skill.home,y:1};
const candidates=[];
for(const [dx,dz] of [[0,0],[-1,0],[1,0],[0,-1],[0,1],[-1,-1],[1,-1],[-1,1],[1,1],[-2,0],[2,0],[0,-2],[0,2]]){
 const target=`${home.x+dx+.5},${home.z+dz+.5}`,before=spawnPoint(fixture(input.before,target),home,skill)??null,after=spawnPoint(fixture(input.after,target),home,skill)??null;
 if(before)assert.deepEqual(JSON.parse(JSON.stringify(after)),JSON.parse(JSON.stringify(before)));
 candidates.push({offset:[dx,dz],before,after});
}
const gained=candidates.filter(v=>!v.before&&v.after);
assert.deepEqual(gained.map(v=>v.offset),[[0,-1]]);
assert.equal(candidates.find(v=>v.offset[0]===0&&v.offset[1]===1).after,null,'new red carpet remains non-air for existing birth authority');
console.log(JSON.stringify({defaults,defaultSpawnPointsExact:JSON.stringify(defaults.before)===JSON.stringify(defaults.after),allPriorDefaultChoicesStillAllowed:true,slotHomes,skillHallCandidates:candidates,gainedFutureBirthCandidates:gained,unavailableRefusals:context.slots.length*2*2,scope:'Actual resident spawn helper with decoded blocks and controlled occupant-query results; no actual births, teleports or native actors.',nativeAcceptance:'unrun'}));

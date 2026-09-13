import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
import { createHash } from 'node:crypto';
const main=fs.readFileSync(process.env.FC_REVIEW_MAIN || 'packs/Fablecraft_BP/scripts/main.js','utf8');
assert.equal(createHash('sha256').update(main).digest('hex'),'c18b286d79bc16d6b3ea08985d5882f7a2411ae2aeb61de3bd83594d6ffb103e');
const pStart=main.indexOf('const P = {'),pEnd=main.indexOf('\n};',pStart)+3;
const oldThreshold=main.match(/case "multiplier": (ok = P\.get\(p, "fc_mult", 0\) >= req\.count;) break;/)[1];
const ctx=vm.createContext({});
vm.runInContext(main.slice(pStart,pEnd)+`\nglobalThis.legacy=p=>{const req={count:14};let ok=false;${oldThreshold}return ok;};`,ctx);
// Proposed strict READER only; does not establish original multiplier semantics.
const strict=p=>{try{const raw=p.getDynamicProperty('fc_mult');return Number.isSafeInteger(raw)&&raw>=0?raw:null;}catch{return null;}};
const cases=[];
for(const raw of [undefined,null,false,13,14,14.5,'14',NaN,Infinity,-1,Number.MAX_SAFE_INTEGER,Number.MAX_SAFE_INTEGER+1]){
 let writes=0;const p={getDynamicProperty:()=>raw,setDynamicProperty:()=>writes++};
 const value=strict(p);assert.equal(writes,0);cases.push({raw:String(raw),type:typeof raw,legacyAccepts:ctx.legacy(p),strictValue:value,strictAccepts:value!==null&&value>=14});
}
assert.equal(strict({getDynamicProperty(){throw Error('unreadable');}}),null);
// The retained decay expression uses persisted fc_lastHit against currentTick.
// This arithmetic is not proof of a fresh native combat sequence after reload.
const reloadExample={fc_mult:14,fc_lastHit:10000,currentTick:20};
assert.equal(reloadExample.currentTick-reloadExample.fc_lastHit>240,false);
assert.equal(strict({getDynamicProperty:()=>reloadExample.fc_mult}),14);
const range=(base,size=49,margin=160)=>({physical:[base,base+63*128+size],excluded:[base-margin,base+63*128+size+margin]});
const grids={guild:range(600000),arboretum:range(620000),proposed_butterfly:range(640000)};
assert.ok(grids.guild.excluded[1]<grids.arboretum.excluded[0]);assert.ok(grids.arboretum.excluded[1]<grids.proposed_butterfly.excluded[0]);
const result={status:'Scratch proposal only; no production reader/controller/keys added',strictReaderCases:cases,unreadableReturns:null,reloadExample:{...reloadExample,existingDecayPredicate:false,strictRawThresholdAccepts:true,meaning:'Numeric strictness alone cannot witness session freshness or original combat-event qualification.'},proposedGrid:{origin:[640000,272,600000],maxRooms:4096,maxSources:64,stride:128,maxProposedRoomSize:[49,28,49],xBounds:grids,minimumExcludedGap:grids.proposed_butterfly.excluded[0]-grids.arboretum.excluded[1]},native:'unrun'};
fs.writeFileSync(new URL('next-door-authority-and-grid-result.json',import.meta.url),JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify(result,null,2));

import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import vm from 'node:vm';
if(!process.env.MULTIPLIER_OWNER)throw Error('Use independent-review.py --mode multiplier, or provide MULTIPLIER_OWNER.');
const main=readFileSync(process.env.MULTIPLIER_OWNER,'utf8');
const pStart=main.indexOf('const P = {'),pEnd=main.indexOf('\n};',pStart)+3;
const hitStart=main.indexOf('world.afterEvents.entityHitEntity.subscribe((ev) => {',main.indexOf('// Combat multiplier + kill XP'));
const hitEnd=main.indexOf('\n});',hitStart)+4;
const requirement=main.match(/case "multiplier": (ok = P\.get\(p, "fc_mult", 0\) >= req\.count;) break;/)?.[1];
assert.ok(requirement&&hitStart>=0&&hitEnd>hitStart);
let hit;
const context=vm.createContext({world:{afterEvents:{entityHitEntity:{subscribe:fn=>{hit=fn;}}}},TICKS:()=>100,currentBounty:()=>true,heldItem:()=>null});
vm.runInContext(main.slice(pStart,pEnd)+'\n'+main.slice(hitStart,hitEnd)+`\nglobalThis.check=(p)=>{const req={count:14};let ok=false;${requirement}return ok;};`,context);
const player=value=>{const props=new Map([['fc_mult',value]]);return {typeId:'minecraft:player',props,getDynamicProperty:k=>props.get(k),setDynamicProperty:(k,v)=>props.set(k,v)};};
const cases=[];
for(const [raw,expected] of [[undefined,false],[13,false],[14,true],[14.5,true],['14',true],['not-a-number',false]]){
 const p=player(raw),accepted=context.check(p);assert.equal(accepted,expected);cases.push({raw:raw??null,type:typeof raw,legacyAccepted:accepted});
}
const corrupted=player('14');hit({damagingEntity:corrupted,hitEntity:{typeId:'minecraft:cow'}});assert.equal(corrupted.props.get('fc_mult'),'141');
const ordinary=player(13);hit({damagingEntity:ordinary,hitEntity:{typeId:'minecraft:cow'}});assert.equal(ordinary.props.get('fc_mult'),14);
const unavailable=player(14);unavailable.getDynamicProperty=()=>{throw Error('unavailable');};assert.throws(()=>context.check(unavailable));
console.log(JSON.stringify({scope:'Actual main P helper, hit callback and legacy requirement expression; no native events ran.',cases,hitOnNonhostile:{numeric:ordinary.props.get('fc_mult'),string:corrupted.props.get('fc_mult')},unavailable:'throws; no canonical strict reader exists',legacyContract:'preserved; proposed canonical family must use a separate strict raw reader'},null,2));

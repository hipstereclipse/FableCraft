// Reproduce the exact GP20 baseline against the actual DP7 read-only helper.
// Run from repository root; no native Bedrock, world writes, or source edits.
import assert from 'node:assert/strict';
import vm from 'node:vm';
import {readFileSync,writeFileSync} from 'node:fs';
import {spawnSync} from 'node:child_process';
import {createHash} from 'node:crypto';
import {parse} from 'espree';
const root='packs/Fablecraft_BP/scripts/',out='screenshots/validation/DP7/';
const baselineCommit='71d70ed9f8ab21f49221a2c040f283c398f3f0ec';
function baseline(name){const r=spawnSync('git',['show',baselineCommit+':'+root+name],{encoding:'utf8',maxBuffer:2*1024*1024});assert.equal(r.status,0,r.stderr);return r.stdout;}
const source=Object.fromEntries(['wd/config.js','wd/state.js','wd/alignment.js','main.js'].map(p=>[p,baseline(p)]));
const context=vm.createContext({}),modules=new Map();
async function module(name){if(modules.has(name))return modules.get(name);const m=new vm.SourceTextModule(source[name],{context,identifier:name});modules.set(name,m);await m.link(dep=>module('wd/'+dep.replace('./','')));return m;}
const alignment=await module('wd/alignment.js');await alignment.evaluate();
const ast=parse(source['main.js'],{ecmaVersion:'latest',sourceType:'module',range:true});
const sub=ast.body.find(n=>n.type==='ExpressionStatement'&&source['main.js'].slice(...n.range).startsWith('world.afterEvents.itemCompleteUse.subscribe('));assert.ok(sub);
const callbackSource=source['main.js'].slice(...sub.expression.arguments[0].range);
const currentSources=Object.fromEntries(['wd/config.js','wd/state.js','wd/alignment.js'].map(p=>[p,readFileSync(root+p,'utf8')]));
const currentContext=vm.createContext({}),currentModules=new Map();
async function currentModule(name){if(currentModules.has(name))return currentModules.get(name);const m=new vm.SourceTextModule(currentSources[name],{context:currentContext,identifier:name});currentModules.set(name,m);await m.link(dep=>currentModule('wd/'+dep.replace('./','')));return m;}
const currentAlignment=await currentModule('wd/alignment.js');await currentAlignment.evaluate();
function player(raw,legacy=-1000,throwRead=false){const props=new Map([['wd:state',raw],['fc_morality',legacy]]),writes=[];return {id:'hero',typeId:'minecraft:player',isValid:true,props,writes,
  getDynamicProperty(k){if(throwRead&&k==='wd:state')throw Error('unavailable');return props.get(k);},
  setDynamicProperty(k,v){writes.push({k,v});props.set(k,v);},onScreenDisplay:{setActionBar(){}}};}
const proposedFresh=p=>currentAlignment.namespace.readAlignmentAuthority(p);
const cases=[
 ['missing',undefined],['malformed','{broken'],['missing_alignment',JSON.stringify({schemaVersion:3})],
 ['string_alignment',JSON.stringify({schemaVersion:3,alignment:'-1000'})],
 ['fractional_alignment',JSON.stringify({schemaVersion:3,alignment:-999.5})],
 ['out_of_range',JSON.stringify({schemaVersion:3,alignment:-1001})],
 ['unsupported_schema',JSON.stringify({schemaVersion:99,alignment:-1000})],
 ['unreadable',JSON.stringify({schemaVersion:3,alignment:-999}),true],
 ['valid_full_evil',JSON.stringify({schemaVersion:3,alignment:-1000})],
 ['valid_not_full',JSON.stringify({schemaVersion:3,alignment:-999})],
];
const rows=[];for(const [name,raw,unreadable] of cases){const p=player(raw,-1000,unreadable);const fresh=proposedFresh(p);assert.equal(p.writes.length,0);const old=alignment.namespace.getAlignment(p);assert.equal(old,name==='valid_not_full'?-999:-1000);assert.equal(fresh,name==='valid_full_evil'?-1000:name==='valid_not_full'?-999:null);rows.push({name,baseline_getAlignment:old,actual_DP7_readAlignmentAuthority:fresh,baseline_writes:p.writes.length});}
context.DATA={consumables:{'fc:crunchy_chick':{morality:-15}}};context.addMorality=(p,d)=>alignment.namespace.changeAlignment(p,d,false);
// Harmless injected engine boundaries execute the unchanged baseline callback.
context.healPlayer=()=>{};
const baselineHasNewWitness=callbackSource.includes('recordConsumption')||callbackSource.includes('arboretum');
let callbackReplay;
if(!baselineHasNewWitness){const callback=vm.runInContext('('+callbackSource+')',context);const p=player(JSON.stringify({schemaVersion:3,alignment:0}),0),event={source:p,itemStack:{typeId:'fc:crunchy_chick',amount:16},useDuration:0};callback(event);const first=alignment.namespace.getAlignment(p);callback(event);const second=alignment.namespace.getAlignment(p);assert.equal(first,-15);assert.equal(second,-30);callbackReplay={injected_same_event_twice_alignment:[first,second],native_replay_observed:false,stack16_still_one_effect_per_callback:true};}
const result={baseline_commit:baselineCommit,baseline_source_sha256:Object.fromEntries(Object.entries(source).map(([p,s])=>[root+p,createHash('sha256').update(s).digest('hex')])),
  current_helper_source_sha256:Object.fromEntries(Object.entries(currentSources).map(([p,s])=>[root+p,createHash('sha256').update(s).digest('hex')])),
  alignment_cases:rows,baseline_callback_replay:callbackReplay,
  actual_source_with_injected_engine_boundaries:true,native_consumption_and_replay_acceptance:'unrun'};
writeFileSync(out+'authority-baseline-results.json',JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify(result,null,2));

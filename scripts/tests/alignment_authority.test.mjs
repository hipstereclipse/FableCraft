// Actual alignment/state/config owners; only Player persistence is mocked.
import test from 'node:test';
import assert from 'node:assert/strict';
import vm from 'node:vm';
import {readFile} from 'node:fs/promises';
const sources=Object.fromEntries(await Promise.all(['alignment','state','config'].map(async name=>[name,await readFile(`packs/Fablecraft_BP/scripts/wd/${name}.js`,'utf8')])));
async function fixture(raw,legacy=-1000){
  const context=vm.createContext({}),modules=new Map();
  async function load(name){if(modules.has(name))return modules.get(name);const m=new vm.SourceTextModule(sources[name],{context});modules.set(name,m);await m.link(path=>load(path.replace('./','').replace('.js','')));return m;}
  const module=await load('alignment');await module.evaluate();
  const props=new Map([['wd:state',raw],['fc_morality',legacy]]),reads=[],writes=[];
  const player={id:'saved-hero',typeId:'minecraft:player',isValid:true,
    getDynamicProperty(key){reads.push(key);return props.get(key);},
    setDynamicProperty(key,value){writes.push([key,value]);props.set(key,value);},
    onScreenDisplay:{setActionBar(){}}};
  return {api:module.namespace,player,props,reads,writes};
}
const document=alignment=>JSON.stringify({schemaVersion:3,alignment,logbook:{deeds:{kept:4}},unrelatedHistory:{ids:['saved-old-spouse'],name:'Retained'}});

test('reads exact current alignment without changing unrelated history or legacy mirrors',async()=>{
  for(const alignment of [-1000,-999,-950,0,1,999,1000]){
    const raw=document(alignment),f=await fixture(raw);
    assert.equal(f.api.readAlignmentAuthority(f.player),alignment);
    assert.equal(f.props.get('wd:state'),raw);assert.equal(f.props.get('fc_morality'),-1000);
    assert.deepEqual(f.reads,['wd:state']);assert.equal(f.writes.length,0);
  }
});

test('missing, malformed and unsupported history never initializes or migrates authority',async()=>{
  for(const raw of [undefined,null,false,12,'',' ','{broken','null','[]','-1000','"state"',
    JSON.stringify({alignment:-1000}),...['3',0,1,2,4,99].map(schemaVersion=>JSON.stringify({schemaVersion,alignment:-1000}))]){
    const f=await fixture(raw);assert.equal(f.api.readAlignmentAuthority(f.player),null,String(raw));
    assert.equal(f.props.get('wd:state'),raw);assert.deepEqual(f.reads,['wd:state']);assert.equal(f.writes.length,0);
  }
});

test('missing or invalid alignment is never clamped, rounded or inherited from full-evil legacy state',async()=>{
  const raws=[JSON.stringify({schemaVersion:3}),...['-1000',null,false,-1001,1001,-999.5,.5].map(alignment=>JSON.stringify({schemaVersion:3,alignment})),
    '{"schemaVersion":3,"alignment":1e309}','{"schemaVersion":3,"alignment":-1e309}'];
  for(const raw of raws){const f=await fixture(raw);assert.equal(f.api.readAlignmentAuthority(f.player),null,raw);assert.deepEqual(f.reads,['wd:state']);assert.equal(f.writes.length,0);}
});

test('invalid/nonplayer/missing handles refuse before reading saved history',async()=>{
  const f=await fixture(document(-1000));
  for(const player of [undefined,null,{},...[
    {isValid:false},{isValid:undefined},{typeId:'fc:guild_apprentice_skill'},{id:''},{id:42},
  ].map(change=>({...f.player,...change}))])assert.equal(f.api.readAlignmentAuthority(player),null);
  for(const key of ['isValid','id','typeId']){const p={...f.player};Object.defineProperty(p,key,{get(){throw Error('unavailable handle');}});assert.equal(f.api.readAlignmentAuthority(p),null,key);}
  assert.equal(f.reads.length,0);assert.equal(f.writes.length,0);
});

test('unreadable persistence defers and each subsequent call obtains fresh state',async()=>{
  const f=await fixture(document(-1000));const read=f.player.getDynamicProperty;
  f.player.getDynamicProperty=()=>{throw Error('unloaded');};assert.equal(f.api.readAlignmentAuthority(f.player),null);
  f.player.getDynamicProperty=read;assert.equal(f.api.readAlignmentAuthority(f.player),-1000);
  f.props.set('wd:state',document(-500));assert.equal(f.api.readAlignmentAuthority({...f.player}),-500);
  f.props.delete('wd:state');assert.equal(f.api.readAlignmentAuthority(f.player),null);
  f.props.set('wd:state',document(250));assert.equal(f.api.readAlignmentAuthority(f.player),250);
  assert.equal(f.writes.length,0);assert.deepEqual(f.reads,['wd:state','wd:state','wd:state','wd:state']);
});

test('existing normal alignment mutation and its legacy mirror retain their owner behavior',async()=>{
  const f=await fixture(document(0),0);
  assert.equal(f.api.changeAlignment(f.player,-15,false),-15);
  assert.equal(f.props.get('fc_morality'),-15);assert.equal(JSON.parse(f.props.get('wd:state')).alignment,-15);
  const writes=f.writes.length;assert.ok(writes>0);assert.equal(f.api.readAlignmentAuthority(f.player),-15);assert.equal(f.writes.length,writes);
});

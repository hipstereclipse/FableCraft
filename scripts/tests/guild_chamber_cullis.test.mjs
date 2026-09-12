// Actual production detector and narrowly recognized saved-registry migration.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import vm from 'node:vm';
import { readFile } from 'node:fs/promises';
import { parse } from 'espree';
const main = await readFile('packs/Fablecraft_BP/scripts/main.js', 'utf8');
const dataSource = await readFile('packs/Fablecraft_BP/scripts/fc_gamedata.js', 'utf8');
const DATA = JSON.parse(dataSource.slice(dataSource.indexOf('export const DATA = ') + 20).trim().replace(/;$/, ''));
const ast = parse(main, {ecmaVersion:'latest',sourceType:'module',range:true});
function declaration(name) {
  const n = ast.body.find(n => n.type === 'FunctionDeclaration' && n.id.name === name
    || n.type === 'VariableDeclaration' && n.declarations.some(d => d.id.name === name));
  assert.ok(n, `production declaration ${name}`); return main.slice(...n.range);
}
function fixture() {
  const base = {x:0,y:40,z:0}, c = DATA.guildChamber;
  const grid = c.runs.flatMap(([index,count])=>Array(count).fill(index));
  assert.equal(grid.length,c.size.reduce((a,b)=>a*b,1));
  const blocks = new Map();
  for(let x=0;x<c.size[0];x++)for(let y=0;y<c.size[1];y++)for(let z=0;z<c.size[2];z++){
    const p=c.palette[grid[x*c.size[1]*c.size[2]+y*c.size[2]+z]];
    blocks.set(`${x+c.origin[0]},${base.y+y+c.origin[1]},${z+c.origin[2]}`,p.name);
  }
  const props=new Map([['fc_guild_chamber_placed',true]]), writes=[];let failWrite=false;
  const dim={getBlock(p){const key=`${p.x},${p.y},${p.z}`;if(!blocks.has(key))return undefined;
    const typeId=blocks.get(key);return {typeId,isAir:typeId==='minecraft:air'};}};
  const context=vm.createContext({DATA,world:{getDynamicProperty:k=>props.get(k),setDynamicProperty(k,v){if(failWrite)throw Error('Injected persistence failure');writes.push([k,v]);props.set(k,v);}}});
  vm.runInContext(['CULLIS_CORE','CULLIS_RING','isCullisConfigured','ensureGuildChamberCullis'].map(declaration).join('\n'),context);
  const expected={x:26,y:23,z:42}, old={name:'Chamber of Fate',x:26,y:25,z:42,custom:'preserved'};
  return {base,blocks,props,writes,dim,expected,old,failWrites:value=>{failWrite=value;},
    ensure:()=>context.ensureGuildChamberCullis(dim,base), configured:s=>context.isCullisConfigured(dim,s),
    setSites:sites=>props.set('fc_cullis',JSON.stringify(sites)),sites:()=>JSON.parse(props.get('fc_cullis'))};
}
test('generated core is detected at exported feet; historical y+7 fails',()=>{
  const f=fixture();assert.equal(f.configured(f.old),false);assert.equal(f.configured(f.expected),true);
  assert.deepEqual(DATA.guildChamber.cullis,[15,5,15]);
});
test('known legacy coordinate changes only y and preserves every other field/site',()=>{
  const f=fixture(),other={name:'Heroes\' Guild',x:15,y:41,z:49,discovered:true};f.setSites([other,f.old]);
  const before=[...f.blocks];assert.equal(f.ensure(),true);assert.deepEqual(f.sites(),[other,{...f.old,y:23}]);
  assert.deepEqual([...f.blocks],before);assert.equal(f.writes.length,1);
  assert.equal(f.ensure(),true);assert.equal(f.writes.length,1);
});
test('verified placed Chamber can restore missing registration without replacing blocks',()=>{
  const f=fixture();assert.equal(f.ensure(),true);assert.deepEqual(f.sites(),[{name:'Chamber of Fate',...f.expected}]);
  f.props.set('fc_guild_chamber_placed',false);assert.equal(f.ensure(),false);
});
test('customized, ambiguous and malformed registries remain untouched',()=>{
  for(const sites of [[{name:'Chamber of Fate',x:27,y:25,z:42}],[{name:'Chamber of Fate',x:26,y:24,z:42}],
    [{name:'Chamber of Fate',x:26,y:25,z:42},{name:'Chamber of Fate',x:26,y:25,z:42}],{},[null]]){
    const f=fixture();f.setSites(sites);assert.equal(f.ensure(),false);assert.equal(f.writes.length,0);
  }
  const f=fixture();f.props.set('fc_cullis','{');assert.equal(f.ensure(),false);assert.equal(f.writes.length,0);
});
test('missing core, unloaded arrival and blocked headroom defer correction',()=>{
  for(const [key,id] of [['26,22,42','minecraft:stone'],['26,23,42',null],['26,24,42','minecraft:stone']]){
    const f=fixture();f.setSites([f.old]);if(id)f.blocks.set(key,id);else f.blocks.delete(key);
    assert.equal(f.ensure(),false);assert.equal(f.writes.length,0);
    assert.deepEqual(f.sites(),[f.old]);
  }
});

test('failed registry write retries without changing blocks or losing custom metadata',()=>{
  const f=fixture();f.setSites([f.old]);const before=[...f.blocks];f.failWrites(true);
  assert.equal(f.ensure(),false);assert.deepEqual(f.sites(),[f.old]);assert.deepEqual([...f.blocks],before);
  f.failWrites(false);assert.equal(f.ensure(),true);assert.deepEqual(f.sites(),[{...f.old,y:23}]);
});

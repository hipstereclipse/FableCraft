import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { createHash } from 'node:crypto';
import vm from 'node:vm';
import { parse } from 'espree';
const main = readFileSync('packs/Fablecraft_BP/scripts/main.js','utf8');
const ast = parse(main, {ecmaVersion:'latest',sourceType:'module',range:true});
const node = ast.body.find(n=>n.type==='FunctionDeclaration'&&n.id.name==='guildSkillLaneClear');
const context=vm.createContext({});
vm.runInContext(main.slice(...node.range),context);
const lane=vm.runInContext('guildSkillLaneClear',context);
const axes=['x','y','z'];
const key=p=>axes.map(a=>Math.floor(p[a])).join(',');
let cases=0,crossedCells=0,maxRead=0,maxCandidates=0;
function oracle(origin,target){
  const times=[0,1];
  for(const axis of axes){
    const delta=target[axis]-origin[axis];
    if(!delta)continue;
    for(let plane=Math.ceil(Math.min(origin[axis],target[axis]));plane<=Math.floor(Math.max(origin[axis],target[axis]));plane++){
      const t=(plane-origin[axis])/delta;
      if(t>0&&t<1)times.push(t);
    }
  }
  times.sort((a,b)=>a-b);
  const cells=new Set();
  for(let i=1;i<times.length;i++){
    if(times[i]-times[i-1]<1e-12)continue;
    const t=(times[i]+times[i-1])/2;
    const point=Object.fromEntries(axes.map(a=>[a,origin[a]+(target[a]-origin[a])*t]));
    cells.add(key(point));
  }
  cells.delete(key(target));
  return cells;
}
for(let ix=-8;ix<=8;ix++)for(let iy=-8;iy<=8;iy++)for(let iz=-8;iz<=8;iz++){
  if(ix*ix+iy*iy+iz*iz>64)continue;
  const location={x:183.5+ix/10,y:65+iy/10,z:-160.5+iz/10};
  const target={x:183.5,y:66.45,z:-165.5};
  const origin={...location,y:location.y+1.35};
  const reads=new Set();let obstruction=null;
  const support={...target,y:Math.floor(target.y)-1};
  const dim={getBlock(point){
    const k=key(point);reads.add(k);
    if(k===key(target))return {typeId:'minecraft:target',isAir:false};
    if(k===key(support))return {typeId:'minecraft:hay_block',isAir:false};
    return obstruction===k?{typeId:'minecraft:chest',isAir:false}:{typeId:'minecraft:air',isAir:true};
  }};
  const archer={location,dimension:dim};
  assert.equal(lane(archer,target),true);
  const expected=oracle(origin,target);
  for(const cell of expected){
    assert.ok(reads.has(cell),`Missed ${cell} at ${ix},${iy},${iz}`);
    obstruction=cell;assert.equal(lane(archer,target),false);crossedCells++;
  }
  maxRead=Math.max(maxRead,reads.size);
  maxCandidates=Math.max(maxCandidates,axes.reduce((n,a)=>n*(Math.floor(Math.max(origin[a],target[a]))-Math.ceil(Math.min(origin[a],target[a]))+2),1));
  cases++;
}
assert.equal(cases,2109);
assert.ok(maxCandidates<=28);
console.log(JSON.stringify({main_sha256:createHash('sha256').update(main).digest('hex'),cases,crossed_cell_obstructions:crossedCells,max_distinct_block_reads:maxRead,max_candidate_voxels:maxCandidates,oracle:'All positive-length intervals between exact integer-plane crossings; independent of AABB clipping.',result:'pass'},null,2));

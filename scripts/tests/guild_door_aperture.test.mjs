import assert from "node:assert/strict";
import fs from "node:fs";
import vm from "node:vm";
import test from "node:test";
const load = async (path) => { const m = new vm.SourceTextModule(fs.readFileSync(path,"utf8")); await m.link(()=>{});await m.evaluate();return m.namespace; };
const {createGuildDoorAperture} = await load("packs/Fablecraft_BP/scripts/guild_door_aperture.js");
const {DATA} = await load("packs/Fablecraft_BP/scripts/fc_gamedata.js");
const fingerprint=DATA.guildDoorAperture;
function fixture(mode="legacy") {
  const cells=new Map(),props=new Map(),messages=[];let writes=0,failAt=null;
  const source={x:100,y:65,z:200,dimension:"minecraft:overworld"};
  const key=(p)=>[p.x,p.y,p.z].join(",");
  const put=(p,id)=>cells.set(key(p),{typeId:id,setType(id){if(writes===failAt){failAt=null;throw Error("unloaded mid-clear");}this.typeId=id;writes++;}});
  let i=0;for(let x=-1;x<=1;x++)for(let y=0;y<4;y++)for(let z=0;z<9;z++)
    put({x:100+x,y:65+y,z:200+z},mode==="new"?"minecraft:air":fingerprint.palette[fingerprint.indices[i++]]);
  for(let x=-1;x<=1;x++)for(let z=0;z<9;z++)put({x:100+x,y:64,z:200+z},"minecraft:cobblestone");
  const dim={getBlock(p){return cells.get(key(p));}};
  const world={getDimension(){return dim;},getDynamicProperty(k){return props.get(k);},setDynamicProperty(k,v){props.set(k,v);}};
  const make=()=>createGuildDoorAperture({world,fingerprint,report:s=>messages.push(s)});
  return {cells,props,source,world,dim,make,put,writes:()=>writes,fail(n){failAt=n;},messages};
}
test("known old throat clears once without any surrounding writes; new throat needs none",()=>{
  const f=fixture(),a=f.make();assert.equal(a.ready(f.source),true);assert(f.writes()>40);let n=f.writes();
  assert.equal(a.ready(f.source,5),true);assert.equal(f.writes(),n);
  for(const [key,b]of f.cells)if(key.split(",")[1]==="64")assert.equal(b.typeId,"minecraft:cobblestone");
  const fresh=fixture("new");assert.equal(fresh.make().ready(fresh.source),true);assert.equal(fresh.writes(),0);
});
test("foreign block, missing chunk and absent floor prevent every mutation",()=>{
  for(const damage of [f=>f.put({x:100,y:66,z:202},"minecraft:diamond_block"),
    f=>f.cells.delete("100,66,202"),f=>f.put({x:100,y:64,z:202},"minecraft:water")]){
    const f=fixture();damage(f);assert.equal(f.make().ready(f.source),false);assert.equal(f.writes(),0);
  }
});
test("partially cleared approved migration resumes after failure; ready rooms preserve new blocks",()=>{
  const f=fixture();f.fail(10);assert.equal(f.make().ready(f.source),false);assert.equal(f.writes(),10);
  assert.equal(f.make().ready(f.source,20),true);
  f.put({x:100,y:66,z:202},"minecraft:stone_bricks");let n=f.writes();
  assert.equal(f.make().ready(f.source,40),false);assert.equal(f.writes(),n);
});
test("invalid record or changed anchor refuses to reset the migration",()=>{
  for(const record of ["not JSON",JSON.stringify({schema:3}),JSON.stringify({schema:1,source:"wrong",phase:"ready"})]){
    const f=fixture();f.props.set("fc_guild_door_aperture_v1",record);assert.equal(f.make().ready(f.source),false);assert.equal(f.writes(),0);
  }
});

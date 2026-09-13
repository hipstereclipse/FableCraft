// Bounded independent adverse probes against the actual injected controller and
// actual-owner geometry. Fixture setup is retained from the permanent suite;
// these independently selected failure scenarios are not copied from its tests.
import assert from 'node:assert/strict';
import {readFileSync,writeFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
import * as espree from 'espree';

const root=new URL('../../../',import.meta.url);
const out=new URL('./',import.meta.url);
const fixturePath=new URL('scripts/tests/arboretum_doors.test.mjs',root);
const controllerPath=process.argv[2]?new URL(process.argv[2],root):new URL('packs/Fablecraft_BP/scripts/arboretum_doors.js',root);
const controller=readFileSync(controllerPath,'utf8');
// Prepared from the actual owner in a separate Python command because this
// sandbox denied nested spawnSync from Node. This fixture never saves a pack.
const geometryPath=new URL('tmp/conformance/dp7/independent-runtime-geometry.json',root);
const geometry=readFileSync(geometryPath,'utf8');
const fixtureSource=readFileSync(fixturePath,'utf8');
let setup=fixtureSource.slice(0,fixtureSource.indexOf('\nlet passed='));
const ast=espree.parse(setup,{ecmaVersion:'latest',sourceType:'module',range:true});
const replacements=[];
for(const node of ast.body){
  if(node.type!=='VariableDeclaration')continue;
  for(const decl of node.declarations){
    if(decl.id.name==='root')replacements.push([decl.init.range,`new URL(${JSON.stringify(root.href)})`]);
    if(decl.id.name==='code')replacements.push([decl.init.range,JSON.stringify(controller)]);
    if(decl.id.name==='geometry')replacements.push([decl.init.range,geometry]);
  }
}
for(const [range,text] of replacements.sort((a,b)=>b[0][0]-a[0][0]))setup=setup.slice(0,range[0])+text+setup.slice(range[1]);
// The initial permanent fixture omitted this capture boundary. It is safe and
// intentional here even if a later fixture already disables generator saving.
setup=setup.replace('v=build_arboretum(Vox);print','Vox.save=lambda *args:None;v=build_arboretum(Vox);print');
setup+='\nexport {fixture,ARBORETUM,INDEX,WITNESS,stateKey,cellKey,origin,add};';
const {fixture,ARBORETUM,INDEX,WITNESS,stateKey,cellKey,origin,add}=await import('data:text/javascript;base64,'+Buffer.from(setup).toString('base64'));
const results=[];
const untilPlaced=f=>{for(let n=0;n<180&&!f.places.length;n++)f.step();assert.equal(f.places.length,1);};
for(const mode of ['ignored','wrong-item','wrong-count']){
  const f=fixture(),r=f.register();f.open(r);untilPlaced(f);
  const c=f.chest(r),original=c.setItem;
  c.setItem=(i,item)=>{
    if(mode==='ignored')return;
    original.call(c,i,{typeId:mode==='wrong-item'?'minecraft:stone':item.typeId,amount:mode==='wrong-count'?2:item.amount});
  };
  f.step(80);
  const state=f.state(r.id);
  results.push({case:`seed-${mode}`,pass:state.room.phase==='seeding'&&!state.reward.seeded&&!state.reward.claimed,
    observed:{phase:state.room.phase,reward:state.reward,slot:c.getItem(0)??null,placements:f.places.length}});
}
{
  const f=fixture();f.props.set(cellKey(0),JSON.stringify('arboretum:0'));
  const before=JSON.stringify([...f.props]);
  const recorded=f.ctl.isRecordedRegion('new-region');
  const id=f.ctl.beginPlacement({regionKey:'new-region',origin:{x:100,y:64,z:200,dimension:'minecraft:overworld'}});
  results.push({case:'surviving-cell-reservation-blocks-pristine-bootstrap',pass:recorded===true&&id===null&&JSON.stringify([...f.props])===before,
    observed:{recorded,id,witness:f.props.get(WITNESS)??null,index:f.props.get(INDEX)??null}});
}
{
  const f=fixture(),r=f.register();f.open(r);untilPlaced(f);f.step();
  const at=add(origin(0),{x:0,y:2,z:5});f.setBlock(at,'minecraft:air');f.step(80);
  const state=f.state(r.id);
  results.push({case:'previously-checked-nonsentinel-shell-hole-blocks-ready',pass:state.room.phase!=='ready'&&!state.reward.seeded&&f.seeds.length===0,
    observed:{at,phase:state.room.phase,reward:state.reward,seeds:f.seeds.length,reports:f.reports}});
}
{
  const f=fixture(),r=f.register(),p=f.player();
  const row=f.state(r.id);row.revision=Number.MAX_SAFE_INTEGER-1;
  f.props.set(stateKey(r.id),JSON.stringify(row));
  const before=JSON.stringify([...f.props]);
  const result=f.ctl.completeUse(p,'fc:crunchy_chick');
  const readable=f.ctl.getState(r.id);
  const firstSafe=!!readable&&(result===false&&JSON.stringify([...f.props])===before
    ||result===true&&readable.revision===Number.MAX_SAFE_INTEGER&&readable.progress[0]?.count===1);
  f.step();const terminalBefore=JSON.stringify([...f.props]);
  const secondResult=f.ctl.completeUse(p,'fc:crunchy_chick');
  const terminalReadable=f.ctl.getState(r.id);
  results.push({case:'exhausted-revision-preserves-readable-history',
    pass:firstSafe&&secondResult===false&&!!terminalReadable&&JSON.stringify([...f.props])===terminalBefore,
    observed:{result,readable:!!readable,committedRevision:JSON.parse(f.props.get(stateKey(r.id))).revision,
      secondResult,terminalReadable:!!terminalReadable}});
}
const result={controller_sha256:createHash('sha256').update(controller).digest('hex'),
  fixture_sha256:createHash('sha256').update(fixtureSource).digest('hex'),
  actual_geometry_sha256:createHash('sha256').update(geometry).digest('hex'),
  scope:'Six independently selected negative probes. Actual current owner geometry; fixture dependency setup from the permanent controller suite.',
  passed:results.filter(r=>r.pass).length,total:results.length,results,native_acceptance:'unrun'};
const name=process.argv[2]?'independent-runtime-initial-results.json':'independent-runtime-results.json';
writeFileSync(new URL(name,out),JSON.stringify(result,null,2)+'\n');
console.log(JSON.stringify(result,null,2));
if(result.passed!==result.total)process.exitCode=1;

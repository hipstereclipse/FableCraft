"""DP7 actual Arboretum woodland, dry circulation and containment regressions."""
from collections import Counter, deque
import ast
import copy
import math
import json
from pathlib import Path
import sys
import subprocess
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'scripts/tests')]
import gen_structures as GS
from door_realms import ARBORETUM, GORGE_ARBORETUM_SOURCE, build_arboretum, arboretum_path_columns
from test_guild_routes import cell
from gen_screenshots import BLOCK_COLORS
import fc_data
from fc_strings import localize
from structure_contract import runtime_tables, builders


class ArboretumGeometry(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.clipped=[]; original=GS.Vox.set
        def bounded(v,x,y,z,*args,**kwargs):
            if not (0<=x<v.sx and 0<=y<v.sy and 0<=z<v.sz):cls.clipped.append((x,y,z))
            return original(v,x,y,z,*args,**kwargs)
        with patch.object(GS.Vox,'save',lambda *_:None),patch.object(GS.Vox,'set',bounded):
            cls.vox=build_arboretum(GS.Vox)

    def block(self,x,y,z,vox=None):
        return cell(vox or self.vox,x,y,z)[0]

    def reached(self,start=(24,7),vox=None):
        v=vox or self.vox
        floors={'minecraft:grass_block','minecraft:podzol','minecraft:moss_block',
                'minecraft:coarse_dirt','minecraft:chiseled_stone_bricks'}
        walk={(x,z) for x in range(1,48) for z in range(1,48)
              if self.block(x,2,z,v) in floors and all(self.block(x,y,z,v)=='minecraft:air' for y in (3,4))}
        seen={start} if start in walk else set();q=deque(seen)
        while q:
            x,z=q.popleft()
            for p in ((x+1,z),(x-1,z),(x,z+1),(x,z-1)):
                if p in walk and p not in seen:seen.add(p);q.append(p)
        return seen

    def check_routes(self,v):
        reached=self.reached(vox=v)
        for x,z in arboretum_path_columns():
            self.assertIn((x,z),reached,f'Lost dry lane {(x,z)}')
            for y in range(3,7):self.assertEqual(self.block(x,y,z,v),'minecraft:air')
        self.assertIn((24,2),reached);self.assertIn((34,34),reached)
        self.assertIn((24,7),self.reached((34,34),v))
        # Independent dense centre/shoulder samples exercise continuous diagonal
        # segments with a player footprint, rather than only endpoint columns.
        segments=list(zip(ARBORETUM['routeWaypoints'],ARBORETUM['routeWaypoints'][1:]))
        segments.extend((ARBORETUM['spine'],ARBORETUM['chestPath']))
        for (x0,z0),(x1,z1) in segments:
            length=math.hypot(x1-x0,z1-z0); steps=math.ceil(length*4)
            for i in range(steps+1):
                x=x0+.5+(x1-x0)*i/steps;z=z0+.5+(z1-z0)*i/steps
                for dx,dz in ((-.3,-.3),(-.3,.3),(.3,-.3),(.3,.3)):
                    self.assertIn((math.floor(x+dx),math.floor(z+dz)),reached,'Blocked sampled footprint')

    def check_shell(self,v):
        for x in range(49):
            for z in range(49):
                for y in (0,27):self.assertEqual(self.block(x,y,z,v),'minecraft:barrier')
        for y in range(28):
            for k in range(49):
                for x,z in ((0,k),(48,k),(k,0),(k,48)):
                    self.assertEqual(self.block(x,y,z,v),'minecraft:barrier')
        for x in range(1,48):
            for z in range(1,48):self.assertEqual(self.block(x,1,z,v),'minecraft:stone')

    def check_chest(self,v):
        containers={(x,y,z) for x in range(49) for y in range(28) for z in range(49)
                    if self.block(x,y,z,v) in ('minecraft:chest','minecraft:barrel')}
        self.assertEqual(containers,{(34,3,35)})
        self.assertEqual(containers,set(ARBORETUM['containers']))
        self.assertEqual(cell(v,34,3,35),('minecraft:chest',{'minecraft:cardinal_direction':'north'}))
        self.assertEqual(self.block(34,2,35,v),'minecraft:podzol')
        for y in range(4,7):self.assertEqual(self.block(34,y,35,v),'minecraft:air')
        for x in range(33,36):self.assertIn((x,34),self.reached(vox=v))
        self.assertFalse(hasattr(v,'block_position_data'),'No pre-seeded reward inventory')

    def test_dimension_palette_containment_and_no_clipped_writes(self):
        self.assertEqual((self.vox.sx,self.vox.sy,self.vox.sz),ARBORETUM['size'])
        self.assertEqual(ARBORETUM['size'],(49,28,49));self.assertEqual(self.clipped,[])
        self.assertLessEqual({n for n,s in self.vox.palette}-{'minecraft:air','minecraft:barrier'},BLOCK_COLORS.keys())
        self.check_shell(self.vox)

    def test_complete_dry_loop_spine_and_reward_approach_both_directions(self):
        self.check_routes(self.vox)
        self.assertEqual(ARBORETUM['routeWaypoints'][0],ARBORETUM['routeWaypoints'][-1])
        self.assertEqual(ARBORETUM['arrival'],(24.5,3,7.5))
        self.assertEqual(ARBORETUM['return'],(24.5,3,3.5))

    def test_one_empty_reward_chest_with_clear_lid_and_three_wide_front(self):
        self.check_chest(self.vox)

    def test_return_detectors_and_both_sides_of_timber_throat(self):
        for p,name in zip(ARBORETUM['returnDetectorCells'],ARBORETUM['returnDetectorBlocks']):
            self.assertEqual(self.block(*p),name)
        for x in range(23,26):
            for z in range(2,10):
                for y in range(3,7):self.assertEqual(self.block(x,y,z),'minecraft:air')
        self.assertEqual(self.block(21,3,3),'minecraft:dark_oak_log')
        self.assertEqual(self.block(27,3,3),'minecraft:dark_oak_log')

    def test_substantial_rooted_canopy_and_no_library_furnishings_or_water(self):
        counts=Counter(self.vox.palette[i][0] for i in self.vox.grid)
        self.assertGreater(counts['minecraft:dark_oak_log'],1000)
        self.assertGreater(counts['minecraft:oak_leaves'],4000)
        self.assertTrue(all(not counts[n] for n in ('minecraft:bookshelf','minecraft:lectern',
            'minecraft:barrel','minecraft:water','minecraft:cartography_table','minecraft:enchanting_table')))
        for x,z in ((23,22),(28,27),(8,23),(41,26)):
            for y in range(3,13):self.assertEqual(self.block(x,y,z),'minecraft:dark_oak_log')
        # The central mass forces discovery around either arc instead of an
        # empty rectangular courtyard with decorative one-column saplings.
        self.assertNotIn((23,22),self.reached())

    def test_independent_obstruction_support_lid_and_shell_failures(self):
        for at,name,check in (((24,3,7),'minecraft:stone',self.check_routes),
                              ((13,2,25),'minecraft:air',self.check_routes),
                              ((34,4,35),'minecraft:stone',self.check_chest),
                              ((48,5,24),'minecraft:air',self.check_shell),
                              ((24,27,24),'minecraft:air',self.check_shell)):
            with self.subTest(at=at):
                broken=copy.deepcopy(self.vox);broken.set(*at,name)
                with self.assertRaises(AssertionError):check(broken)

    def test_owner_is_deterministic_and_does_not_consume_shared_generator_rng(self):
        with patch.object(GS.Vox,'save',lambda *_:None),patch.object(GS,'rng',side_effect=AssertionError('Shared RNG')):
            second=GS.arboretum()
        self.assertEqual(self.vox.grid,second.grid);self.assertEqual(self.vox.palette,second.palette)

    def test_actual_runtime_room_waypoints_markers_and_source_match_python_owner(self):
        script="""
const fs=require('fs'),espree=require('espree'),vm=require('vm');
const src=fs.readFileSync('packs/Fablecraft_BP/scripts/arboretum_doors.js','utf8');
const ast=espree.parse(src,{ecmaVersion:'latest',sourceType:'module',range:true});
const result={};
for(const node of ast.body){
  const statement=node.type==='ExportNamedDeclaration'?node.declaration:node;
  if(statement?.type!=='VariableDeclaration')continue;
  for(const decl of statement.declarations){
    if(['ARBORETUM','ARBORETUM_SOURCE'].includes(decl.id.name))
      result[decl.id.name]=vm.runInNewContext('('+src.slice(...decl.init.range)+')');
  }
}
process.stdout.write(JSON.stringify(result));
"""
        actual=json.loads(subprocess.check_output(['node','-e',script],cwd=ROOT,text=True))
        room=actual['ARBORETUM'];source=actual['ARBORETUM_SOURCE']
        point=lambda values:dict(zip(('x','y','z'),values))
        self.assertEqual(room['id'],'fc:arboretum')
        self.assertEqual(room['version'],ARBORETUM['version'])
        for key in ('routeWaypoints','returnDetectorBlocks'):
            self.assertEqual(room[key],json.loads(json.dumps(ARBORETUM[key])),key)
        for key in ('size','arrival'):self.assertEqual(room[key],point(ARBORETUM[key]))
        self.assertEqual(room['returnDetectorCells'],[point(p) for p in ARBORETUM['returnDetectorCells']])
        self.assertEqual(room['exit'],point(ARBORETUM['return']))
        self.assertEqual(room['chest'],point(ARBORETUM['containers'][0]))
        self.assertEqual(room['chestApproach'],json.loads(json.dumps(ARBORETUM['chestPath'])))
        self.assertEqual(source['offset'],point(GORGE_ARBORETUM_SOURCE['center']))
        self.assertEqual(source['normal'],point(GORGE_ARBORETUM_SOURCE['normal']))
        self.assertEqual(source['throat'],{'min':point(GORGE_ARBORETUM_SOURCE['throatMin']),
                                          'max':point(GORGE_ARBORETUM_SOURCE['throatMax'])})

    def test_canonical_data_fixed_registration_and_renderer_share_the_new_owner(self):
        script="""
const fs=require('fs'),espree=require('espree'),vm=require('vm');
const src=fs.readFileSync('packs/Fablecraft_BP/scripts/fc_gamedata.js','utf8');
const ast=espree.parse(src,{ecmaVersion:'latest',sourceType:'module',range:true});
const decl=ast.body.find(n=>n.type==='ExportNamedDeclaration').declaration.declarations.find(d=>d.id.name==='DATA');
const data=vm.runInNewContext('('+src.slice(...decl.init.range)+')');
process.stdout.write(JSON.stringify({realms:data.demonDoorRealms,legacy:data.demonDoors}));
"""
        data=json.loads(subprocess.check_output(['node','-e',script],cwd=ROOT,text=True))
        self.assertEqual(data['realms'],localize(fc_data.CANONICAL_DEMON_DOORS))
        self.assertEqual(data['legacy'],localize(fc_data.DEMON_DOORS))
        definition=data['realms']['greatwood_gorge_arboretum']
        self.assertEqual(definition['destination'],{'structure':'fc:arboretum','version':ARBORETUM['version']})
        self.assertEqual(definition['reward'],{'items':[{'id':'fc:wellows_pickhammer','count':1}],'xp':0})
        manifest=json.loads((ROOT/'scripts/structure_manifest.json').read_text())
        entry=next(e for e in manifest['structures'] if e['name']=='arboretum')
        self.assertEqual(entry['kind'],'fixed');self.assertEqual(entry['generator'],'arboretum')
        self.assertEqual(entry['size'],list(ARBORETUM['size']))
        self.assertIn('arboretum',builders())
        tables=runtime_tables(ROOT)
        self.assertIn('fc:arboretum',tables['fixed'])
        self.assertNotIn('fc:arboretum',{s['id'] for s in tables['STRUCTS']})
        tree=ast.parse((ROOT/'scripts/gen_screenshots.py').read_text())
        dictionaries={}
        for node in ast.walk(tree):
            if isinstance(node,ast.Assign) and isinstance(node.value,ast.Dict):
                for name in node.targets:
                    if isinstance(name,ast.Name) and name.id in ('builders','STRUCT_LABELS'):
                        dictionaries[name.id]={ast.literal_eval(k):v for k,v in zip(node.value.keys,node.value.values)}
        emitter=dictionaries['builders']['arboretum']
        self.assertIsInstance(emitter,ast.Attribute);self.assertEqual(emitter.attr,'arboretum')
        self.assertEqual(emitter.value.id,'GS')
        self.assertEqual(ast.literal_eval(dictionaries['STRUCT_LABELS']['arboretum'])[0],'The Arboretum')


if __name__=='__main__':unittest.main(verbosity=2)

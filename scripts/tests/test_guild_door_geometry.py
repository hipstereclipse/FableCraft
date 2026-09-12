"""DP1 source throat, rear approach, fixed realm and invisible containment render."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import gen_structures as GS
from gen_screenshots import render_structure
from structure_contract import ROOT, runtime_tables


class GuildDoorGeometry(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.captured={}
        with patch.object(GS.Vox,'save',lambda v,n:cls.captured.setdefault(n,v)):
            GS.guild_hall();GS.library_arcanum()
        cls.vox=cls.captured['guild_hall']

    def block(self,v,x,y,z):return v.palette[v.grid[v.idx(x,y,z)]][0]

    def throat(self,v):
        # Both directions use every cell through the rock, not just a front plane.
        for zs in (range(96,105),range(104,95,-1)):
            for z in zs:
                for x in (65,66,67):
                    self.assertEqual(self.block(v,x,0,z),'minecraft:cobblestone',f'No throat floor {(x,z)}')
                    for y in range(1,5):self.assertEqual(self.block(v,x,y,z),'minecraft:air',f'Blocked throat {(x,y,z)}')

    def test_three_wide_four_high_tunnel_floor_and_both_approaches(self):
        self.throat(self.vox)
        for z in (95,104):
            for x in (65,66,67):
                self.assertNotIn(self.block(self.vox,x,0,z),('minecraft:air','minecraft:water'))
                for y in (1,2):self.assertEqual(self.block(self.vox,x,y,z),'minecraft:air')
        # Rear approach turns sideways before the existing south boundary wall.
        for x in range(63,70):
            for y in (1,2):self.assertEqual(self.block(self.vox,x,y,104),'minecraft:air')
        for x in (63,69):
            self.assertEqual(self.block(self.vox,x,2,95),'minecraft:chiseled_stone_bricks')
            self.assertEqual(self.block(self.vox,x,3,95),'minecraft:soul_lantern')
        self.assertEqual(GS.GUILD_LAYOUT['demon_door'],(66,96))
        self.assertEqual(GS.GUILD_LAYOUT['size'],(122,30,108))

    def test_independent_late_obstruction_and_floor_hole_are_rejected(self):
        blocked=copy.deepcopy(self.vox);blocked.set(66,2,100,'minecraft:stone_bricks')
        with self.assertRaisesRegex(AssertionError,'Blocked throat'):self.throat(blocked)
        hole=copy.deepcopy(self.vox);hole.set(66,0,100,'minecraft:air')
        with self.assertRaisesRegex(AssertionError,'No throat floor'):self.throat(hole)

    def test_actual_runtime_migrates_frozen_gp1_throat_and_preserves_every_floor(self):
        # Independent frozen geometry, not a fixture synthesized from the runtime
        # fingerprint. Run the real migration so its offsets and material guard
        # must agree with the old generated asset and the new clear volume.
        fixture=json.loads((Path(__file__).parent/'fixtures/guild_door_gp1.json').read_text())
        probe=r'''
import fs from 'node:fs';
import vm from 'node:vm';
const load=async(path)=>{const m=new vm.SourceTextModule(fs.readFileSync(path,'utf8'));await m.link(()=>{});await m.evaluate();return m.namespace;};
const {createGuildDoorAperture}=await load('packs/Fablecraft_BP/scripts/guild_door_aperture.js');
const {DATA}=await load('packs/Fablecraft_BP/scripts/fc_gamedata.js');
const fixture=JSON.parse(fs.readFileSync(0,'utf8')), cells=new Map(), props=new Map(), writes=[];
for(const [x,y,z,id]of fixture.cells){const key=[x,y,z].join(',');cells.set(key,{typeId:id,setType(next){this.typeId=next;writes.push(key);}});}
const dimension={getBlock:({x,y,z})=>cells.get([x,y,z].join(','))};
const world={getDimension:()=>dimension,getDynamicProperty:k=>props.get(k),setDynamicProperty:(k,v)=>props.set(k,v)};
const [x,y,z]=fixture.source;
const ready=createGuildDoorAperture({world,fingerprint:DATA.guildDoorAperture}).ready({x,y,z});
console.log(JSON.stringify({ready,writes,cells:[...cells].map(([k,b])=>[...k.split(',').map(Number),b.typeId])}));
'''
        completed=subprocess.run(['node','--experimental-vm-modules','--input-type=module','-e',probe],
                                 input=json.dumps(fixture),text=True,capture_output=True,cwd=ROOT)
        self.assertEqual(completed.returncode,0,completed.stderr)
        result=json.loads(completed.stdout)
        self.assertTrue(result['ready'],'Frozen old source must pass the runtime fingerprint guard')
        expected_writes={f'{x},{y},{z}' for x,y,z,b in fixture['cells'] if y>0 and b!='minecraft:air'}
        self.assertEqual(set(result['writes']),expected_writes)
        before={(x,y,z):b for x,y,z,b in fixture['cells']}
        for x,y,z,b in result['cells']:
            if y==0:
                self.assertEqual(b,before[(x,y,z)],'Migration must preserve existing floor materials')
                self.assertEqual(self.block(self.vox,x,y,z),'minecraft:cobblestone')
            else:
                self.assertEqual(b,'minecraft:air')
                self.assertEqual(b,self.block(self.vox,x,y,z))

    def test_library_is_explicit_fixed_destination_without_scatter_or_ambient_loot(self):
        self.assertEqual(set(self.captured),{'guild_hall','library_arcanum'})
        v=self.captured['library_arcanum']
        self.assertEqual((v.sx,v.sy,v.sz),(49,28,49))
        tables=runtime_tables(ROOT)
        self.assertIn('fc:library_arcanum',tables['fixed'])
        self.assertFalse(any(e['id']=='fc:library_arcanum' for e in tables['STRUCTS']))
        self.assertNotIn('fc:library_arcanum',tables['CHEST_LOOT'])

    def test_barriers_remain_in_asset_but_neither_render_nor_occlude_visible_faces(self):
        v=GS.Vox(3,3,3);v.set(1,1,1,'minecraft:stone_bricks')
        baseline=render_structure(v,size=(120,120)).tobytes()
        for x,y,z in ((1,1,0),(1,1,2),(0,1,1),(2,1,1),(1,2,1),(1,0,1)):
            v.set(x,y,z,'minecraft:barrier')
        self.assertEqual(render_structure(v,size=(120,120)).tobytes(),baseline)
        self.assertEqual(self.block(v,1,2,1),'minecraft:barrier')


if __name__=='__main__':unittest.main(verbosity=2)

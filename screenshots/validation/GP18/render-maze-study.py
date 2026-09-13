"""GP18 final-voxel study fixtures; schematic materials, never native screenshots."""
from pathlib import Path
import hashlib,json,math,sys
from unittest.mock import patch
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'scripts/tests')]
import gen_structures as g
import gen_screenshots as render
from test_guild_maze_study import FIXTURE,SURVEY,UPPER_APPROACH,FRONTS,DESTINATIONS
from test_guild_map_table import voxel_changes
from test_guild_routes import cell,walking_graph,reachable
OUT=Path(__file__).resolve().parent
with patch.object(g,'build_guild_maze_study',lambda *_:None):before=g.build_guild_hall()
after=g.build_guild_hall()
font_path='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
font=ImageFont.truetype(font_path,24);small=ImageFont.truetype(font_path,15)
colors={**render.BLOCK_COLORS,'minecraft:blue_carpet':(46,69,135)}
views={
 'study-cutaway':{'bounds':[40,53,11,16,66,78],'yaw':math.pi+.35,'pitch':.57,'omit_north_wall':True,'description':'North wall and roof omitted; retained study floor, approach and fixtures'},
 'study-case':{'bounds':[42,46,11,15,73,76],'yaw':math.pi+.18,'pitch':.22,'omit_north_wall':False,'description':'Southwest case pocket; four bookshelf cells between timber base and cap','before_description':'Empty supported southwest pocket before furnishing'},
 'study-plan':{'bounds':[40,53,11,16,66,78],'yaw':0.,'pitch':math.pi/2-.001,'omit_north_wall':False,'description':'Upper deck from above; roof omitted; existing approach openings retained'},
}
def draw(vox,view,label):
 b=view['bounds'];quads=[]
 for x in range(b[0],b[1]+1):
  for y in range(b[2],b[3]+1):
   for z in range(b[4],b[5]+1):
    if view['omit_north_wall'] and z<70 and y>11:continue
    name,states=cell(vox,x,y,z)
    if name=='minecraft:air':continue
    tex=Image.new('RGBA',(2,2),colors.get(name,(200,120,200))+(255,))
    origin=(x,y,z);size=(1,1,1)
    if name.endswith('_carpet'):size=(1,1/16,1)
    elif name.endswith('_slab'):
     upper=states.get('minecraft:vertical_half')=='top' or states.get('top_slot_bit')
     origin=(x,y+(.5 if upper else 0),z);size=(1,.5,1)
    quads.extend(render.cube_quads(origin,size,(0,0),tex,glow=name in render.GLOW_BLOCKS))
 img=Image.new('RGB',(1280,940),(240,237,231))
 raw=render.render_quads(quads,size=(1280,820),yaw=view['yaw'],pitch=view['pitch'],shadow=False)
 img.paste(raw,(0,65),raw)
 d=ImageDraw.Draw(img);d.text((30,18),'Maze study | '+label,font=font,fill=(32,35,39))
 d.text((30,52),view.get('before_description',view['description']) if label=='before' else view['description'],font=small,fill=(67,68,71))
 d.text((30,899),'Offline schematic: approximate flat colors; no native lighting, textures or collision acceptance.',font=small,fill=(67,68,71))
 return img
for name,view in views.items():
 for label,vox in [('before',before),('after',after)]:draw(vox,view,label).save(OUT/f'{name}-{label}.png')
def outside_hash(vox):
 h=hashlib.sha256()
 for x in range(vox.sx):
  for y in range(vox.sy):
   for z in range(vox.sz):
    if (x,y,z) in FIXTURE:continue
    h.update(json.dumps([x,y,z,*cell(vox,x,y,z)],sort_keys=True,separators=(',',':')).encode()+b'\n')
 return h.hexdigest()
changes=voxel_changes(before,after);assert set(changes)==FIXTURE
protected=SURVEY['protected_cells'];assert all(cell(after,*e['at'])==(e['name'],e['states']) for e in protected)
walks={label:reachable(vox,walking_graph(vox),(46,12.,70)) for label,vox in [('before',before),('after',after)]}
assert walks['before']-walks['after']=={(43,12.,75),(44,12.,75)}
for found in walks.values():assert all(p in found for p in UPPER_APPROACH+FRONTS+DESTINATIONS)
summary={'baseline_scope':'Current complete builder with only build_guild_maze_study disabled; independent review compares actual prior committed owner.',
 'views':views,'changed_final_voxels':len(changes),'changed_coordinates':changes,'protected_cells_exact':len(protected),
 'outside_fixture_sha256_before':outside_hash(before),'outside_fixture_sha256_after':outside_hash(after),
 'normalization':'Local coordinate, block identifier and sorted state properties; palette indices ignored.',
 'only_removed_reachable_nodes':sorted(walks['before']-walks['after']),
 'routes':'Existing full tower route plus both bookcase fronts, gate, middle landing, Maze ground and all 28 upper-door approach points remain reachable in the offline model.',
 'render_limits':'Clipped geometry per view. North wall explicitly omitted only in study-cutaway. Flat approximate colors; bookshelf blocks are plain color proxies, not native book textures. Carpets are 1/16 high, slabs half-height; other furniture, panes, walls and lamps simplified to full cubes. Blue carpet uses a local approximate blue because the shared renderer lacks that entry. No source pixels, native lighting, physical collision or NPC navigation.',
 'reference_images':SURVEY['known_reference_images'],
 'source_hashes':{n:hashlib.sha256((ROOT/n).read_bytes()).hexdigest() for n in ['scripts/gen_structures.py','scripts/gen_screenshots.py','scripts/tests/test_guild_maze_study.py','packs/Fablecraft_BP/structures/fc/guild_hall.mcstructure']},
 'image_hashes':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(OUT.glob('study-*.png'))},
 'engine_acceptance':'unrun'}
assert summary['outside_fixture_sha256_before']==summary['outside_fixture_sha256_after']
(OUT/'maze-study-render-scope.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps({'changed_final_voxels':len(changes),'protected_cells_exact':len(protected),'outside_hash_match':True,'images':len(summary['image_hashes']),'engine_acceptance':'unrun'}))

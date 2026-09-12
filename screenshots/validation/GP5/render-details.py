from pathlib import Path
import sys,subprocess,types,json,hashlib
from unittest.mock import patch
from PIL import Image
sys.path.insert(0,str(Path('scripts').resolve()))
import gen_structures as g
import gen_screenshots as render
out=Path('screenshots/validation/GP5');out.mkdir(parents=True,exist_ok=True)
baseline=types.ModuleType('gp4_gen_structures');exec(subprocess.check_output(['git','show','cd6815f:scripts/gen_structures.py']).decode(),baseline.__dict__)
captured={}
with patch.object(baseline.Vox,'save',lambda v,n:captured.setdefault(n,v)):baseline.chamber_of_fate()
old=captured['chamber_of_fate'];new=g.build_chamber_of_fate()
def detail(vox,bounds,yaw=2.4,pitch=.48,altar_only=False):
 quads=[]
 for x in range(bounds[0],bounds[1]+1):
  for y in range(bounds[2],bounds[3]+1):
   for z in range(bounds[4],bounds[5]+1):
    if altar_only and (x-15)**2+(z-15)**2 > 8.6**2:continue
    name,states=vox.palette[vox.grid[vox.idx(x,y,z)]]
    if name=='minecraft:air':continue
    slab=name.endswith('_slab');height=.5 if slab else 1
    offset=.5 if slab and (states.get('minecraft:vertical_half')=='top' or states.get('top_slot_bit')) else 0
    tex=Image.new('RGBA',(2,2),render.BLOCK_COLORS.get(name,(200,120,200))+(255,))
    quads.extend(render.cube_quads((x,y+offset,z),(1,height,1),(0,0),tex,glow=name in render.GLOW_BLOCKS))
 return render.render_quads(quads,size=(1100,850),yaw=yaw,pitch=pitch,shadow=False)
for label,v in [('before',old),('after',new)]:
 detail(v,(6,24,1,4,6,24),pitch=.68,altar_only=True).save(out/f'chamber-altar-stairs-{label}.png')
 cut=g.Vox(v.sx,v.sy,v.sz);cut.palette=list(v.palette);cut.pal_idx=dict(v.pal_idx);cut.grid=list(v.grid)
 cut.fill(0,9,0,30,19,30,'minecraft:air')
 cut.fill(0,2,0,30,8,3,'minecraft:air')
 detail(cut,(0,30,0,8,0,30),yaw=.2,pitch=.8).save(out/f'chamber-open-cutaway-{label}.png')
render.render_structure(new).save(out/'chamber-exterior-after.png')
(out/'render-scope.json').write_text(json.dumps({'source_before':'cd6815facd1312f7659fd64296d0f5167ce9b018','scope':'Offline owner geometry. Altar details crop radius8.6/y1..4 and preserve half-slab heights; open cutaways also render half-height slabs. Open cutaways remove local y>=9 and north z<=3 above floor; standard structure renderer draws all blocks as cubes. Neither lighting nor engine views.','scope_changes':'Concentric altar treads and skylight water rim only; core/room anchors preserved'},indent=2)+'\n')

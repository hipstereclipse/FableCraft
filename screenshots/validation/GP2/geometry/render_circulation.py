"""GP2 generated comparison views. Architectural cutaways are labeled.
Run: PYTHONPATH=scripts python screenshots/validation/GP2/geometry/render_circulation.py
"""
import hashlib,json,math
from pathlib import Path
from unittest.mock import patch
from PIL import ImageDraw
import gen_structures as GS
import gen_screenshots as SS
OUT=Path(__file__).resolve().parent
cap={}
with patch.object(GS.Vox,'save',lambda v,n:cap.setdefault(n,v)):GS.guild_hall()
v=cap['guild_hall']
def crop(x0,x1,z0,z1,ymax):
 o=GS.Vox(x1-x0+1,ymax+1,z1-z0+1)
 for x in range(x0,x1+1):
  for y in range(ymax+1):
   for z in range(z0,z1+1):
    n,s=v.palette[v.grid[v.idx(x,y,z)]];o.set(x-x0,y,z-z0,n,s)
 return o

def stair_cutaway(names,x0,x1,z0,z1,ymax):
 # Keep only the floor, authored stair treads/carriages and final landings.
 # Removing the architectural shell makes the full route visible in one view.
 o=GS.Vox(x1-x0+1,ymax+1,z1-z0+1)
 keep={(x,0,z) for x in range(x0,x1+1) for z in range(z0,z1+1)}
 for name in names:
  for x,feet,z in GS.guild_circulation_routes()[name]:
   y=math.ceil(feet)-1
   keep.update((x,yy,z) for yy in (max(0,y-1),y))
 if names==['tower']:
  for x,y,z in ((44,6,73),(44,6,72),(48,11,71),(47,11,71),(46,11,71),(46,11,70)):
   keep.add((x,y,z))
 for x,y,z in keep:
  if x0<=x<=x1 and z0<=z<=z1 and y<=ymax:
   n,s=v.palette[v.grid[v.idx(x,y,z)]];o.set(x-x0,y,z-z0,n,s)
 return o
views=[('new_exterior',v,math.pi-.65,.55,'GP2 current generator / exterior / offline'),
('new_hall_cutaway',crop(11,50,16,60,10),math.pi-.65,.72,'GP2 CUTAWAY y<=10 / hall + stairs'),
('new_tower_cutaway',crop(38,54,64,80,13),math.pi-.65,.80,'GP2 CUTAWAY y<=13 / tower + study'),
('lobby_circulation_cutaway',stair_cutaway(['lobby_north','lobby_south','gallery_bridge'],18,40,33,51,13),math.pi-.65,.65,'GP2 CIRCULATION CUTAWAY / hall shell omitted'),
('tower_circulation_cutaway',stair_cutaway(['tower'],40,52,66,78,15),math.pi-.65,.62,'GP2 CIRCULATION CUTAWAY / tower shell + decor omitted')]
meta={'scope':'Offline generated visuals, never engine movement or TLC-fidelity proof. Circulation views hide architectural shells.', 'source_sha256':hashlib.sha256(Path('scripts/gen_structures.py').read_bytes()).hexdigest(),'images':{}}
for name,vox,yaw,pitch,label in views:
 im=SS.render_structure(vox,size=(1200,1000),yaw=yaw,pitch=pitch).convert('RGB');ImageDraw.Draw(im).text((20,20),label,fill='white');path=OUT/(name+'.png');im.save(path)
 meta['images'][name]=hashlib.sha256(path.read_bytes()).hexdigest();print('rendered',name,flush=True)
(OUT/'views.json').write_text(json.dumps(meta,indent=2)+'\n')

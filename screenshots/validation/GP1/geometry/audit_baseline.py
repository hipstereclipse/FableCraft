"""GP1 immutable baseline probe; offline approximate collision, never engine proof.
Run from repository root: PYTHONPATH=scripts python screenshots/validation/GP1/geometry/audit_baseline.py
"""
import json, math, hashlib
from pathlib import Path
from collections import deque
import gen_structures as GS
import gen_screenshots as SS
from PIL import ImageDraw
OUT=Path(__file__).resolve().parent
cap={}
orig=GS.Vox.save
try:
    GS.Vox.save=lambda self,name:cap.__setitem__(name,self)
    GS.guild_hall()
finally: GS.Vox.save=orig
v=cap['guild_hall']
def block(x,y,z):
    if not (0<=x<v.sx and 0<=y<v.sy and 0<=z<v.sz): return 'minecraft:air'
    return v.palette[v.grid[v.idx(x,y,z)]][0]
AIR={'minecraft:air','minecraft:red_carpet','minecraft:blue_carpet','minecraft:light_blue_carpet','minecraft:azure_bluet','minecraft:allium','minecraft:rose_bush','minecraft:peony','minecraft:lilac','minecraft:tallgrass','minecraft:fern'}
NONFLOOR=AIR|{'minecraft:water','minecraft:lantern','minecraft:soul_lantern','minecraft:torch','minecraft:campfire','minecraft:end_rod','minecraft:chain'}
def support(n): return n not in NONFLOOR and not any(s in n for s in ('fence','wall','candle','leaves'))
walk={(x,y,z) for x in range(v.sx) for y in range(1,18) for z in range(v.sz) if block(x,y,z) in AIR and block(x,y+1,z) in AIR and support(block(x,y-1,z))}
start=(20,1,42); reached={start}; q=deque([start]); parents={start:None}
while q:
    x,y,z=q.popleft()
    for xx,zz in ((x-1,z),(x+1,z),(x,z-1),(x,z+1)):
        for yy in (y-1,y,y+1):
            p=(xx,yy,zz)
            if p in walk and p not in reached:
                # Upward move needs clearance above the departure head too.
                if yy>y and block(x,y+2,z) not in AIR: continue
                reached.add(p);parents[p]=(x,y,z);q.append(p)
targets={'entrance':(10,1,42),'library':(27,1,24),'store':(27,1,55),'dining':(39,1,42),'skill_approach':(16,1,35),'cullis_approach':(16,1,49),'north_wing':(33,1,10),'north_bridge_west':(42,1,7),'north_bridge_east':(78,1,5),'NE_stores':(78,1,20),'NE_dorm_ground':(88,1,20),'NE_dorm_upper':(91,6,20),'dining_dorm_upper':(40,8,45),'rotunda_gallery':(31,10,42),'cloister_ground':(22,1,69),'cloister_upper':(22,6,69),'tower_ground':(46,1,70),'tower_middle':(46,7,70),'maze':(46,12,70),'river_bridge_north':(63,2,36),'river_bridge_south':(63,2,54),'archery':(86,1,39),'dueling':(101,1,61),'will_island':(62,1,86),'door_approach':(66,1,88),'woods_exit':(119,1,32),'cave_threshold':(27,1,16)}
rows={}
for name,p in targets.items():
    route=[]; cur=p
    if p in reached:
        while cur is not None:route.append(cur);cur=parents[cur]
        route.reverse()
    rows[name]={'point':p,'standable':p in walk,'reachable':p in reached,'floor':block(p[0],p[1]-1,p[2]),'feet':block(*p),'head':block(p[0],p[1]+1,p[2]),'route':route}
# Tower's intended outer and inner tread components: feet/head clearance at all treads.
treads=[]
for i in range(22):
    y=1+i//2;a=math.radians(25+i*22.5)
    for radius in (4,3):
        x,z=46+round(math.cos(a)*radius),72+round(math.sin(a)*radius)
        treads.append({'i':i,'support':[x,y,z],'block':block(x,y,z),'feet':block(x,y+1,z),'head':block(x,y+2,z),'reachable_above':(x,y+1,z) in reached})
report={'method':'Cardinal full-cell graph, two clear cells, max one-block rise/drop; slabs/stairs treated as full cubes and listed plants/carpets passable. Upward edge requires departure overhead. Cannot certify Bedrock collision, jump-free walking, diagonal movement or NPC AI. Negative results require source/voxel corroboration.', 'size':[v.sx,v.sy,v.sz],'source_sha256':hashlib.sha256(Path('scripts/gen_structures.py').read_bytes()).hexdigest(),'reachable_nodes':len(reached),'targets':rows,'tower_treads':treads}
report['gallery_bridge_samples']=[{'point':[x,y,42],'block':block(x,y,42)} for x in range(30,38) for y in range(7,13)]
report['tower_gap_samples']=[{'point':[x,y,z],'block':block(x,y,z)} for x,z in ((48,75),(48,76),(49,75),(47,75)) for y in range(1,6)]
(OUT/'route-probe.json').write_text(json.dumps(report,indent=2)+'\n')
for name,row in rows.items():print(name,row['point'],'REACHABLE' if row['reachable'] else 'UNREACHED','standable',row['standable'],row['floor'],row['feet'],row['head'],flush=True)
def crop(x0,x1,z0,z1,ymax):
    o=GS.Vox(x1-x0+1,ymax+1,z1-z0+1)
    for x in range(x0,x1+1):
        for y in range(ymax+1):
            for z in range(z0,z1+1):
                name,states=v.palette[v.grid[v.idx(x,y,z)]];o.set(x-x0,y,z-z0,name,states)
    return o
for name,vox,yaw,pitch,label in [
('baseline_exterior',v,math.pi-0.65,0.55,'GP1 current generator / exterior / offline'),
('baseline_ground_cutaway',crop(0,121,0,107,3),0,math.pi/2-.001,'GP1 CUTAWAY y<=3 / ground routes / north up'),
('baseline_hall_cutaway',crop(11,50,16,60,10),math.pi-0.65,.72,'GP1 CUTAWAY y<=10 / hall + stairs'),
('baseline_tower_cutaway',crop(38,54,64,80,13),math.pi-.65,.80,'GP1 CUTAWAY y<=13 / tower stairs + study')]:
    im=SS.render_structure(vox,size=(1200,1000),yaw=yaw,pitch=pitch).convert('RGB');ImageDraw.Draw(im).text((20,20),label,fill='white');im.save(OUT/(name+'.png'));print('rendered',name,flush=True)

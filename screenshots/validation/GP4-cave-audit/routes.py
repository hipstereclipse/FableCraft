import json,math
from collections import deque
from pathlib import Path
from sys import path,argv
path.insert(0,'scripts/tests')
from test_guild_routes import PASSABLE,interval
folder=Path(argv[1])
cells={(x,y,z):(name,states) for x,y,z,name,states in json.loads((folder/'assembled.json').read_text())}
def cell(x,y,z):return cells.get((x,y,z),('minecraft:stone',{}))
def clear(x,feet,z):
    for y in range(math.floor(feet)-1,math.ceil(feet+2)):
        name,states=cell(x,y,z);span=interval(name,states,y)
        if span and span[0]<feet+2-1e-6 and span[1]>feet+1e-6:return False
    return True
nodes=set()
for (x,y,z),(name,states) in cells.items():
    if name in PASSABLE or name.endswith(('_fence','_wall','_stairs')) or name in ('minecraft:lantern','minecraft:soul_lantern','minecraft:campfire','minecraft:chain','minecraft:water','minecraft:iron_bars'):continue
    surface=interval(name,states,y)
    if surface and clear(x,surface[1],z):nodes.add((x,surface[1],z))
def route(start,end,max_rise):
    seen={start:None} if start in nodes else {};q=deque(seen)
    while q:
        p=q.popleft();x,y,z=p
        if p==end:
            out=[]
            while p is not None:out.append(p);p=seen[p]
            return list(reversed(out))
        for dx,dz in ((1,0),(-1,0),(0,1),(0,-1)):
            for i in range(-int(max_rise*2),int(max_rise*2)+1):
                next=(x+dx,y+i*.5,z+dz)
                if next in nodes and next not in seen and clear(x,max(y,next[1]),z) and clear(next[0],max(y,next[1]),next[2]):seen[next]=p;q.append(next)
    return None
landmarks={'library':(27,41.,17),'threshold':(27,40.,16),'top_slab':(27,40.5,15),'landing':(26,20.,15),'arch':(26,20.,29),'hill_toe':(26,20.,34),'cullis':(26,23.,42)}
report={'scope':'Actual-callback final voxels; full/slab two-block headroom and cardinal centerline transitions; max-rise 1 permits jumps and is not a jump-free claim.','landmarks':{},'routes':{}}
for name,p in landmarks.items():report['landmarks'][name]={'feet':p,'standable':p in nodes}
for start,end in [('library','top_slab'),('top_slab','landing'),('landing','arch'),('arch','cullis'),('library','cullis')]:
    for rise in (.5,1):
        fwd=route(landmarks[start],landmarks[end],rise);rev=route(landmarks[end],landmarks[start],rise)
        report['routes'][f'{start}->{end} max_rise={rise}']={'forward':len(fwd) if fwd else None,'reverse':len(rev) if rev else None}
        if fwd and rise==1 and (start,end) in [('library','top_slab'),('arch','cullis')]:report['routes'][f'{start}->{end} max_rise={rise}']['path']=fwd
(folder/'route-report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))

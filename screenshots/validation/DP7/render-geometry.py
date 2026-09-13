"""DP7 original offline topology, eye-level ray views and actual source delta.

Reads owner output; writes evidence and ignored scratch only. No reference pixels.
"""
import contextlib, hashlib, io, json, math
from pathlib import Path
import subprocess, sys, types
from unittest.mock import patch
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).resolve().parent
sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'scripts/tests')]
import gen_structures as g
import gen_screenshots as renderer
from door_realms import ARBORETUM, GORGE_ARBORETUM_SOURCE, arboretum_path_columns
from test_guild_routes import cell
from test_guild_map_table import voxel_changes
BASE='71d70ed9f8ab21f49221a2c040f283c398f3f0ec'
font=ImageFont.truetype('DejaVuSans.ttf',24);small=ImageFont.truetype('DejaVuSans.ttf',15)
sha=lambda b:hashlib.sha256(b).hexdigest()

def capture(module,fn):
    result=[];streams=[];original=module.rng
    def observed(*keys):
        r=original(*keys);streams.append((keys,r));return r
    with patch.object(module.Vox,'save',lambda v,n:result.append((v,n))),patch.object(module,'rng',observed):getattr(module,fn)()
    assert len(result)==1
    return result[0][0],[(keys,r.getstate()) for keys,r in streams]

oldsrc=subprocess.check_output(['git','show',BASE+':scripts/gen_structures.py'],cwd=ROOT)
old=types.ModuleType('dp7_original_owner');old.__file__=str(ROOT/'scripts/gen_structures.py')
exec(compile(oldsrc,old.__file__,'exec'),old.__dict__)
before,before_rng=capture(old,'greatwood_gorge');after,after_rng=capture(g,'greatwood_gorge')
room,room_rng=capture(g,'arboretum')
assert before_rng==after_rng and room_rng==[]
expected={(x,y,z) for x in range(31,34) for y in range(6,10) for z in range(8,11)}
expected|={(x,y,7) for x in range(31,34) for y in (7,8)}|{(32,9,7)}
changes=voxel_changes(before,after);assert set(changes)==expected
for module,v,name in ((old,before,'source-before'),(g,after,'source-after'),(g,room,'room')):
    with patch.object(module,'BP',ROOT/'tmp/conformance/dp7/render-owner'/name),contextlib.redirect_stdout(io.StringIO()):v.save(name)
    data=(ROOT/'tmp/conformance/dp7/render-owner'/name/'structures/fc'/f'{name}.mcstructure').read_bytes()
    if name=='source-before':expected_data=subprocess.check_output(['git','show',BASE+':packs/Fablecraft_BP/structures/fc/greatwood_gorge.mcstructure'],cwd=ROOT)
    else:expected_data=(ROOT/'packs/Fablecraft_BP/structures/fc'/('arboretum.mcstructure' if name=='room' else 'greatwood_gorge.mcstructure')).read_bytes()
    assert data==expected_data

def card(raw,title,description,footer):
    img=Image.new('RGB',(1280,940),(235,232,223));img.paste(raw,(0,90))
    d=ImageDraw.Draw(img);d.text((28,18),title,font=font,fill=(28,36,29))
    d.text((28,54),description,font=small,fill=(60,66,58))
    d.text((28,897),footer,font=small,fill=(60,66,58))
    return img

def ray_view(v,eye,target):
    # Vectorized exact-grid DDA. Foliage/furniture are opaque full cubes. This
    # is an explicit eye-level geometric sightline, not native block rendering.
    width,height=960,600
    eye=np.array(eye,dtype=float);forward=np.array(target,dtype=float)-eye;forward/=np.linalg.norm(forward)
    right=np.cross(np.array([0.,1.,0.]),forward);right/=np.linalg.norm(right)
    up=np.cross(forward,right)
    xx,yy=np.meshgrid((np.arange(width)+.5)/width*2-1,1-(np.arange(height)+.5)/height*2)
    rays=forward+xx[...,None]*right*math.tan(math.radians(70)/2)+yy[...,None]*up*math.tan(math.radians(70)/2)*height/width
    rays=rays.reshape(-1,3);rays/=np.linalg.norm(rays,axis=1)[:,None]
    count=len(rays);pos=np.tile(np.floor(eye).astype(int),(count,1));step=np.where(rays>=0,1,-1)
    inv=1/np.where(np.abs(rays)<1e-12,1e-12,rays)
    tmax=(np.where(step>0,pos+1,pos)-eye)*inv;tdelta=np.abs(inv)
    active=np.ones(count,dtype=bool);travel=np.zeros(count);axis=np.full(count,1)
    colors=np.array([renderer.BLOCK_COLORS.get(n,(66,80,69)) for n,s in v.palette],dtype=float)
    grid=np.array(v.grid);sky=np.array((76,101,82),dtype=float)
    pixels=np.tile(sky,(count,1))
    ignored={i for i,(n,s) in enumerate(v.palette) if n in ('minecraft:air','minecraft:barrier')}
    for _ in range(180):
        ids=np.flatnonzero(active)
        if not len(ids):break
        valid=np.all((pos[ids]>=0)&(pos[ids]<np.array([v.sx,v.sy,v.sz])),axis=1)
        active[ids[~valid]]=False;ids=ids[valid]
        if not len(ids):continue
        x,y,z=pos[ids].T;pid=grid[x*v.sy*v.sz+y*v.sz+z]
        hit=~np.isin(pid,list(ignored));hitids=ids[hit]
        shade=np.array([.76,1.,.87])[axis[hitids]]
        depth=np.clip(travel[hitids]/65,0,.5)
        pixels[hitids]=colors[pid[hit]]*shade[:,None]*(1-depth[:,None])+sky*depth[:,None]
        active[hitids]=False;ids=ids[~hit]
        if not len(ids):continue
        a=np.argmin(tmax[ids],axis=1);axis[ids]=a;travel[ids]=tmax[ids,a]
        pos[ids,a]+=step[ids,a];tmax[ids,a]+=tdelta[ids,a]
    return Image.fromarray(np.clip(pixels.reshape(height,width,3),0,255).astype('uint8')).resize((1280,800))

# Topology reveals ground/root shapes with high crowns omitted. Dotted contract
# line is a review overlay, not a breadcrumb trail shipped in the game.
top=Image.new('RGB',(1280,800),(37,49,39));draw=ImageDraw.Draw(top);scale=15;ox,oz=270,30
for x in range(49):
    for z in range(49):
        names=[cell(room,x,y,z)[0] for y in range(2,8)]
        name=next((n for n in reversed(names) if n not in ('minecraft:air','minecraft:barrier')),names[0])
        color=renderer.BLOCK_COLORS.get(name,(33,40,35))
        draw.rectangle((ox+x*scale,oz+z*scale,ox+(x+1)*scale-1,oz+(z+1)*scale-1),fill=color)
path=[(ox+(x+.5)*scale,oz+(z+.5)*scale) for x,z in ARBORETUM['routeWaypoints']]
draw.line(path,fill=(168,210,175),width=2)
for x,z in path:draw.ellipse((x-3,z-3,x+3,z+3),fill=(207,232,210))
for label,(x,z),color in [('arrival',(24,7),(142,195,243)),('return',(24,3),(232,225,150)),('chest',(34,35),(247,194,79))]:
    px,pz=ox+(x+.5)*scale,oz+(z+.5)*scale
    draw.ellipse((px-5,pz-5,px+5,pz+5),fill=color);draw.text((18,40+['arrival','return','chest'].index(label)*26),label,fill=color,font=small)
card(top,'The Arboretum | topology','Actual final ground/root columns through y7; higher canopy omitted; route overlay for review only.',
     'Original block geometry; no source pixels. Flat schematic colors; native lighting, collision and traversal unrun.').save(OUT/'arboretum-topology.png')

views={
    'arboretum-entry':{'eye':(24.5,4.62,7.5),'target':(23.5,5.2,22.5),'description':'Eye 1.62 blocks above arrival; path divides around substantial trunks and root forms.'},
    'arboretum-chest':{'eye':(31.5,4.62,31.5),'target':(34.5,3.6,35.5),'description':'Eye 1.62 blocks above the branch; the one empty chest sits beyond its clear front apron.'},
    'arboretum-return':{'eye':(24.5,4.62,9.5),'target':(24.5,4.7,3.5),'description':'Return timber frame, overhead marker and clear supported throat seen from the arrival spine.'}}
for name,view in views.items():
    raw=ray_view(room,view['eye'],view['target'])
    card(raw,'The Arboretum | '+name.removeprefix('arboretum-'),view['description'],
         'Offline geometric ray view: opaque full-cube leaves/chest, approximate colors/shading; no native textures or lighting.').save(OUT/f'{name}.png')

for label,v in (('before',before),('after',after)):
    quads=[]
    for x in range(28,37):
        for y in range(5,15):
            for z in range(6,13):
                name,_=cell(v,x,y,z)
                if name=='minecraft:air':continue
                texture=Image.new('RGBA',(2,2),renderer.BLOCK_COLORS[name]+(255,))
                quads.extend(renderer.cube_quads((x,y,z),(1,1,1),(0,0),texture))
    raw=renderer.render_quads(quads,size=(1280,800),yaw=math.pi+.3,pitch=.35,shadow=False)
    background=Image.new('RGB',(1280,800),(235,232,223));background.paste(raw,(0,0),raw)
    card(background,'Greatwood Gorge source | '+label,'Actual '+('committed GP20' if label=='before' else 'current')+' owner; crop x28..36,y5..14,z6..12.',
         'Offline full-cube cutaway. Only the three-wide/four-high passage changes; source face animation is not simulated.').save(OUT/f'gorge-source-{label}.png')

result={'baseline_commit':BASE,'actual_predecessor_and_current_owners_match_assets':True,
        'source_changed_cells':changes,'source_changed_count':len(changes),'source_total_cells':len(before.grid),
        'gorge_rng_state_equal':before_rng==after_rng,'arboretum_shared_rng_instances':len(room_rng),
        'room_contract':ARBORETUM,'source_contract':GORGE_ARBORETUM_SOURCE,
        'route_columns':sorted(arboretum_path_columns()),'route_column_count':len(arboretum_path_columns()),
        'views':views,'source_view':{'bounds':[28,36,5,14,6,12],'yaw':math.pi+.3,'pitch':.35},
        'font':{'path':font.path,'sha256':sha(Path(font.path).read_bytes())},
        'source_sha256':{p:sha((ROOT/p).read_bytes()) for p in ('scripts/gen_structures.py','scripts/door_realms.py','scripts/gen_screenshots.py','packs/Fablecraft_BP/structures/fc/arboretum.mcstructure','packs/Fablecraft_BP/structures/fc/greatwood_gorge.mcstructure','packs/Fablecraft_BP/structures/fc/library_arcanum.mcstructure')},
        'images':{p.name:sha(p.read_bytes()) for p in sorted(OUT.glob('*.png')) if p.name.startswith(('arboretum-','gorge-source-'))},
        'limits':'Root/tree count, path dimensions and exact composition are original adaptations. Reference low curved objects remain unidentified. Topology omits canopy above y7. Ray views use exact block cells but opaque cubic foliage/furniture and simple directional shading/fog; no native textures, light simulation, collision or player movement. No external pixels.'}
(OUT/'geometry-render-scope.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'source_delta':len(changes),'route_columns':len(arboretum_path_columns()),'images':len(result['images']),'native_acceptance':'unrun'}))

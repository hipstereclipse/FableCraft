#!/usr/bin/env python3
"""Independent decoded DP7/current Guild owner review; pack assets are read only."""
import argparse
from collections import deque
import contextlib
import copy
import hashlib
import importlib.util
import io
import json
import math
from pathlib import Path
import subprocess
import sys
import types

ROOT = next(p for p in Path(__file__).resolve().parents if (p/'scripts/gen_structures.py').exists())
OUT = Path(__file__).resolve().parent
sys.path[:0] = [str(ROOT/'scripts'), str(ROOT/'scripts/tests')]
from PIL import Image, ImageDraw, ImageFont
import gen_screenshots as renderer
from test_guild_routes import cell, clear, supported, walking_graph, reachable, GuildRoutes, interval
spec = importlib.util.spec_from_file_location('retained_decoder', ROOT/'screenshots/validation/GP20/independent-review.py')
reader = importlib.util.module_from_spec(spec); spec.loader.exec_module(reader)
BASE = 'e13127194b8bd596bf9db9fee03633a413825f24'
ASSET = 'packs/Fablecraft_BP/structures/fc/guild_hall.mcstructure'
SOURCE = 'scripts/gen_structures.py'
sha = lambda data: hashlib.sha256(data).hexdigest()
BRIDGES = {str(z): [(x, 1.5 if x in (59,67) else 2. if 60<=x<=66 else 1., z) for x in range(57,70)] for z in (36,54)}
LOCAL = {**{'bridge_'+k:v for k,v in BRIDGES.items()},
    'board_approach': [(79,1.,30)]+[(x,1.,29) for x in range(79,90)]+[(89,1.,30),(89,1.,31)]+[(x,1.,31) for x in range(88,79,-1)],
    'west_bypass': [(79,1.,z) for z in range(32,47)],
    'east_bypass': [(93,1.,z) for z in range(32,47)],
    'future_arrival': [(x,1.,39) for x in range(83,87)],
    'firing_gap': [(83,1.,z) for z in range(35,41)],
    'range_rear': [(x,1.,44) for x in range(79,94)]}
DESTINATIONS = [(78,1.,28),(90,1.,28),(83,1.,39),(93,1.,37),(99,1.,61),(102,1.,61),(60,1.,88)]

def committed(path): return subprocess.check_output(['git','show',BASE+':'+path],cwd=ROOT)

def generate(source,label):
    module=types.ModuleType('gp21_'+label);module.__file__=str(ROOT/SOURCE)
    exec(compile(source,module.__file__,'exec'),module.__dict__)
    module.BP=ROOT/'tmp/conformance/gp21-geometry/owners'/label
    streams=[];original=module.rng
    def observed(*keys):
        stream=original(*keys);streams.append((keys,stream));return stream
    module.rng=observed
    with contextlib.redirect_stdout(io.StringIO()):module.guild_hall()
    raw=(module.BP/'structures/fc/guild_hall.mcstructure').read_bytes()
    return module,raw,reader.decode(raw),[(keys,repr(r.getstate())) for keys,r in streams]

def changed(before,after):
    result=[]
    for i,(a,b) in enumerate(zip(before.grid,after.grid)):
        if before.palette[a]==after.palette[b]:continue
        x,yz=divmod(i,after.sy*after.sz);y,z=divmod(yz,after.sz)
        result.append({'at':(x,y,z),'before':before.palette[a],'after':after.palette[b]})
    return result

def setcell(v,p,name):
    pair=(name,{})
    if pair not in v.palette:v.palette.append(pair)
    v.grid[v.idx(*p)]=v.palette.index(pair)

def trace(v,start,destinations):
    nodes=walking_graph(v);parents={start:None};q=deque([start]);remaining=set(destinations)
    while q and remaining:
        a=q.popleft();remaining.discard(a);x,y,z=a
        for xx,zz in ((x-1,z),(x+1,z),(x,z-1),(x,z+1)):
            for dy in (-.5,0,.5):
                b=(xx,y+dy,zz)
                if b in parents or b not in nodes:continue
                top=max(y,b[1])
                if clear(v,x,top,z) and clear(v,xx,top,zz):parents[b]=a;q.append(b)
    assert not remaining,remaining
    paths={};checker=GuildRoutes()
    for dst in destinations:
        path=[];p=dst
        while p is not None:path.append(p);p=parents[p]
        path.reverse();checker.check_run(path,v);paths[str(dst)]=path
    return nodes,reachable(v,nodes,start),paths

def harness(v,path,arrival=False):
    if arrival:
        cells={f'{x},{y},{z}':cell(v,x,y,z)[0] for x in range(72,98) for y in range(4) for z in range(28,52)}
        cells.update({f'{x},-1,{z}':'minecraft:air' for x in range(72,98) for z in range(28,52)})
    else:
        cells={f'{x},{y},{z}':cell(v,x,y,z)[0] for x in range(77,94) for y in range(7) for z in range(29,43)}
    run=subprocess.run(['node','--experimental-vm-modules',path],cwd=ROOT,input=json.dumps({'cells':cells}),text=True,capture_output=True)
    assert run.returncode==0,run.stderr
    return json.loads(run.stdout)

def ray_collisions(v, emitted):
    """Independent dense sweep extends fence/wall occupancy through y+1.5.

    Horizontal fence cells are conservatively treated as whole columns; this
    bounds native shapes but does not run projectile or Bedrock collision code.
    """
    hits={};samples=10001
    for ray in emitted['rays']:
        offset=ray['offset'];origin=tuple(ray['origin'][a] for a in ('x','y','z'))
        target=tuple(ray['target'][a] for a in ('x','y','z'));found=set()
        for i in range(samples):
            f=i/samples;p=tuple(a+(b-a)*f for a,b in zip(origin,target));x,y,z=p
            if (math.floor(x),math.floor(y),math.floor(z))==(83,2,34):continue
            for yy in (math.floor(y)-1,math.floor(y)):
                name,states=cell(v,math.floor(x),yy,math.floor(z));span=interval(name,states,yy)
                if span and span[0]<y<span[1]:found.add((math.floor(x),yy,math.floor(z),name))
        hits[str(offset)]=sorted(found)
    return hits

def render(v,label):
    views={'range-south':((77,94,0,7,29,46),.18,.52),
           'range-north':((77,94,0,7,29,46),math.pi+.18,.60),
           'range-plan':((77,94,0,7,29,46),0,math.pi/2)}
    font=ImageFont.truetype('DejaVuSans.ttf',20);small=ImageFont.truetype('DejaVuSans.ttf',14)
    for name,(bounds,yaw,pitch) in views.items():
        quads=[]
        for x in range(bounds[0],bounds[1]+1):
            for y in range(bounds[2],bounds[3]+1):
                for z in range(bounds[4],bounds[5]+1):
                    block,states=cell(v,x,y,z)
                    if block=='minecraft:air':continue
                    assert block in renderer.BLOCK_COLORS,block
                    tex=Image.new('RGBA',(2,2),renderer.BLOCK_COLORS[block]+(255,))
                    boxes=[((x,y,z),(1,1,1))]
                    if block.endswith('_slab'):
                        upper=states.get('minecraft:vertical_half')=='top' or states.get('top_slot_bit')
                        boxes=[((x,y+(.5 if upper else 0),z),(1,.5,1))]
                    elif block.endswith('_carpet'):boxes=[((x,y,z),(1,1/16,1))]
                    elif block.endswith('_fence'):
                        boxes=[((x+.375,y,z+.375),(.25,1,.25))]
                        for dx,dz in ((1,0),(-1,0),(0,1),(0,-1)):
                            if cell(v,x+dx,y,z+dz)[0].endswith('_fence'):
                                for yy in (.375,.75):
                                    boxes.append(((x+.5+(dx*.5 if dx<0 else 0),y+yy,z+.4375),(abs(dx)*.5 or .125,.125,.125)) if dx else
                                                 ((x+.4375,y+yy,z+.5+(dz*.5 if dz<0 else 0)),(.125,.125,.5)))
                    elif block=='minecraft:torch':boxes=[((x+.4375,y,z+.4375),(.125,.625,.125))]
                    for start,size in boxes:quads.extend(renderer.cube_quads(start,size,(0,0),tex))
        corners=[renderer.rot_x(renderer.rot_y(c,yaw),pitch) for q in quads for c in q[0]]
        sx=max(p[0] for p in corners)-min(p[0] for p in corners);sy=max(p[1] for p in corners)-min(p[1] for p in corners)
        zoom=min(1280*.88/sx,760*.86/sy)
        raw=renderer.render_quads(quads,size=(1280,760),zoom=zoom,yaw=yaw,pitch=pitch,shadow=False,rim=False)
        img=Image.new('RGB',(1280,860),(240,237,231));img.paste(raw,(0,65),raw);d=ImageDraw.Draw(img)
        d.text((24,15),f'Decoded Guild | {label} | {name}',font=font,fill=(30,34,38))
        d.text((24,42),'Approximate authored geometry; clipped surrounding architecture. No native lighting or collision evidence.',font=small,fill=(65,65,65))
        d.text((24,834),'Fence visual members approximate connections; collision review separately uses conservative 1.5-block occupied columns.',font=small,fill=(65,65,65))
        img.save(OUT/f'{name}-{label}.png')
    return views

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--render',action='store_true');args=p.parse_args()
    old_source,new_source=committed(SOURCE),(ROOT/SOURCE).read_bytes()
    old,old_raw,old_nbt,old_rng=generate(old_source,'before');new,new_raw,new_nbt,new_rng=generate(new_source,'after')
    assert old_raw==committed(ASSET);assert new_raw==(ROOT/ASSET).read_bytes()
    assert old.GUILD_LAYOUT==new.GUILD_LAYOUT;assert old_rng==new_rng
    before,current=reader.voxel(old_nbt),reader.voxel(new_nbt)
    for key in ('format_version','structure_world_origin','size'):assert old_nbt[key]==new_nbt[key]
    for key in ('entities','palette'):assert old_nbt['structure'][key]==new_nbt['structure'][key]
    assert old_nbt['structure']['block_indices'][1]==new_nbt['structure']['block_indices'][1]
    cells={(x,1,38) for x in [80,81,*range(85,93)]}
    actual_changes=changed(before,current)
    assert {tuple(c['at']) for c in actual_changes}==cells
    assert all(c['before']==('minecraft:air',{}) and c['after']==('minecraft:spruce_fence',{}) for c in actual_changes)
    candidate=current
    checker=GuildRoutes()
    for v in (before,candidate):
        for run in LOCAL.values():checker.check_run(run,v)
        for x in range(82,85):checker.check_run([(x,1.,z) for z in range(37,41)],v)
    bn,br,bpaths=trace(before,(10,1.,42),DESTINATIONS);cn,cr,cpaths=trace(candidate,(10,1.,42),DESTINATIONS)
    expected={(x,1.,z) for x,y,z in cells};assert bn-cn==expected;assert br-cr==expected;assert not(cn-bn);assert not(cr-br)
    assert bpaths==cpaths
    results={}
    for label,v in (('baseline',before),('candidate',candidate)):
        emitted=harness(v,str(OUT/'ray-collision-probe.mjs'))
        results[label]={'shot':harness(v,'scripts/tests/guild_archery_voxels.mjs'),
            'arrival':harness(v,'screenshots/validation/DP6/station-arrival-followup.mjs',True),
            'actual_emitted_rays':emitted,'expanded_fence_ray_collisions':ray_collisions(v,emitted)}
        assert not any(results[label]['expanded_fence_ray_collisions'].values())
    negatives=[]
    for label,at,block,route in [('missing_bridge_deck',(63,1,36),'minecraft:air','bridge_36'),
        ('missing_bridge_approach',(59,1,36),'minecraft:air','bridge_36'),('bridge_head',(63,3,36),'minecraft:stone','bridge_36'),
        ('blocked_arrival',(84,1,39),'minecraft:spruce_fence','future_arrival'),
        ('blocked_board_bypass',(85,1,29),'minecraft:chest','board_approach'),
        ('closed_firing_gap',(83,1,38),'minecraft:spruce_fence','firing_gap')]:
        broken=copy.deepcopy(candidate);setcell(broken,at,block)
        try:checker.check_run(LOCAL[route],broken)
        except AssertionError:negatives.append({'name':label,'at':at,'detected':True})
        else:raise AssertionError(label)
    fence=copy.deepcopy(candidate);setcell(fence,(83,1,38),'minecraft:spruce_fence')
    fence_hits=ray_collisions(fence,results['candidate']['actual_emitted_rays']);assert any(fence_hits.values())
    # This is a deliberate audit of the harness's block-cell boundary: the
    # y1 fence is below every y2 ray sample despite its y2.5 collision top.
    misleading=harness(fence,'scripts/tests/guild_archery_voxels.mjs')
    fixtures=[{'at':p,'before':cell(before,*p),'support':cell(before,p[0],0,p[2])} for p in sorted(cells)]
    tables=[(x,y,z) for x in range(current.sx) for y in range(current.sy) for z in range(current.sz) if cell(current,x,y,z)[0]=='minecraft:fletching_table']
    assert tables==[(91,1,40)]
    protected=json.loads((ROOT/'screenshots/validation/GP17/maze-study-final-voxel-survey.json').read_text())['protected_cells']
    assert len(protected)==678
    assert all(cell(current,*item['at'])==(item['name'],item['states']) for item in protected)
    out={'baseline_commit':BASE,'scope':'Actual final owner comparison',
        'source_sha256':{'before':sha(old_source),'after':sha(new_source)},'asset_sha256':{'before':sha(old_raw),'after':sha(new_raw)},
        'owners_match_shipped_assets':True,'compared_cells':len(before.grid),'actual_changes':actual_changes,'candidate_cells':fixtures,
        'shared_rng_and_layout_exact':True,'rng_instances':len(old_rng),'baseline_nodes':len(bn),'candidate_nodes':len(cn),
        'existing_palette_entities_secondary_layer_origin_and_size_exact':True,'protected_maze_cells':len(protected),'all_campus_fletching_tables':tables,
        'only_removed_nodes':sorted(bn-cn),'only_removed_gate_reachable_nodes':sorted(br-cr),'baseline_gate_paths':bpaths,'candidate_gate_paths':cpaths,
        'all_seven_complete_gate_paths_exact':True,
        'protected_local_routes':LOCAL,'harnesses':results,'independent_route_negatives':negatives,
        'cross_firing_fence_negative':{'at':[83,1,38],'expanded_collision_hits':fence_hits,'block_cell_harness_still_passes':misleading},
        'native_acceptance':'unrun','limits':'No engine execution. Cardinal model treats fences as full columns through y+1.5. Current generic block-cell ray harness misses the lower-fence overhang; independent sweep explicitly checks it. Arrival prototype has 624 below-base cells mocked readable air; saved-world search remains uncalibrated.'}
    if args.render:
        out['views']=render(before,'before');render(candidate,'after')
        out['image_sha256']={f'{name}-{label}.png':sha((OUT/f'{name}-{label}.png').read_bytes()) for name in out['views'] for label in ('before','after')}
    paths=[SOURCE,ASSET,'scripts/gen_screenshots.py','scripts/tests/test_guild_routes.py',
        'scripts/tests/guild_archery_voxels.mjs','screenshots/validation/DP6/station-arrival-followup.mjs',
        'screenshots/validation/GP20/independent-review.py','packs/Fablecraft_BP/scripts/main.js',
        'packs/Fablecraft_BP/scripts/guild_training.js',str(Path(__file__).relative_to(ROOT)),
        str((OUT/'ray-collision-probe.mjs').relative_to(ROOT))]
    out['reviewed_source_sha256']={path:sha((ROOT/path).read_bytes()) for path in paths}
    font=ImageFont.truetype('DejaVuSans.ttf',20)
    out['font']={'path':str(font.path),'sha256':sha(Path(font.path).read_bytes())}
    (OUT/'independent-review-results.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({'scope':out['scope'],'actual_changes':len(actual_changes),'candidate_cells':len(cells),'walking_nodes_removed':len(bn-cn),
        'local_routes':len(LOCAL),'gate_destinations':len(DESTINATIONS),'expanded_ray_offsets':len(fence_hits),'route_negatives':len(negatives),
        'cross_fence_overhang_detected':True,'both_harnesses_pass':True,'native':'unrun'}))

if __name__=='__main__':main()

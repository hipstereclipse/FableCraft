#!/usr/bin/env python3
"""Read-only final-voxel bridge/range survey. Hypothetical rails exist only in RAM."""
from collections import deque
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'scripts/tests')]
import gen_structures as GS
from test_guild_routes import cell,clear,supported,walking_graph,GuildRoutes
spec=importlib.util.spec_from_file_location('gp18_nbt',ROOT/'screenshots/validation/GP18/independent_review_probe.py')
reader=importlib.util.module_from_spec(spec);spec.loader.exec_module(reader)
asset=ROOT/'packs/Fablecraft_BP/structures/fc/guild_hall.mcstructure'
serialized=reader.voxel(reader.decode_nbt(asset.read_bytes()))
vox=GS.build_guild_hall()
assert len(vox.grid)==len(serialized.grid)
assert all(vox.palette[a]==serialized.palette[b] for a,b in zip(vox.grid,serialized.grid))
checker=GuildRoutes()
bridges={str(z):[(x,1.5 if x in (59,67) else 2. if 60<=x<=66 else 1.,z) for x in range(57,70)] for z in (36,54)}
for run in bridges.values():checker.check_run(run,vox)
bridge_negatives=[]
for name,where in [('missing_deck',(63,1,36)),('missing_approach',(59,1,36)),('blocked_head',(63,3,36))]:
    edited=copy.deepcopy(vox);edited.set(*where,'minecraft:stone' if name=='blocked_head' else 'minecraft:air')
    try:checker.check_run(bridges['36'],edited)
    except AssertionError:bridge_negatives.append(name)
    else:raise AssertionError('Expected exact crossing failure: '+name)

# Existing cornerposts at x80/x92,z33/z45 leave these link cells empty.
# This is a collider/route feasibility fixture, not a proposed authored visual.
rail_cells={(x,1,z) for x in (80,92) for z in range(34,45)}
for x,y,z in rail_cells:
    assert cell(vox,x,y,z)[0]=='minecraft:air'
    assert supported(vox,x,1.,z)
    assert clear(vox,x,1.,z)
fixture=copy.deepcopy(vox)
for p in rail_cells:fixture.set(*p,'minecraft:spruce_fence')
changed={(x,y,z) for x in range(vox.sx) for y in range(vox.sy) for z in range(vox.sz)
         if cell(vox,x,y,z)!=cell(fixture,x,y,z)}
assert changed==rail_cells

# Retain door/board bypasses, existing corridor and each bridge exactly.
board_path=([(79,1.,30)]+[(x,1.,29) for x in range(79,90)]+[(89,1.,30),(89,1.,31)]+[(x,1.,31) for x in range(88,79,-1)])
west_bypass=[(79,1.,z) for z in range(32,47)]
east_bypass=[(93,1.,z) for z in range(32,47)]
native_candidate=[(x,1.,39) for x in range(83,87)]
local_runs={**{'bridge_'+k:v for k,v in bridges.items()},'board_approach':board_path,
            'west_rail_bypass':west_bypass,'east_rail_bypass':east_bypass,'future_short_arrival':native_candidate}
for run in local_runs.values():checker.check_run(run,fixture)

def paths(v,start,destinations):
    nodes=walking_graph(v);parents={start:None};queue=deque([start]);remaining=set(destinations)
    while queue and remaining:
        a=queue.popleft();remaining.discard(a)
        x,y,z=a
        for xx,zz in ((x-1,z),(x+1,z),(x,z-1),(x,z+1)):
            for dy in (-.5,0,.5):
                b=(xx,y+dy,zz)
                if b in parents or b not in nodes:continue
                top=max(y,b[1])
                if clear(v,x,top,z) and clear(v,xx,top,zz):parents[b]=a;queue.append(b)
    assert not remaining,remaining
    found={}
    for dst in destinations:
        path=[];p=dst
        while p is not None:path.append(p);p=parents[p]
        path.reverse();checker.check_run(path,v);found[str(dst)]=path
    return found

destinations=[(78,1.,28),(90,1.,28),(83,1.,39),(93,1.,37),(99,1.,61),(102,1.,61),(60,1.,88)]
gate_paths=paths(vox,(10,1.,42),destinations)
fixture_paths=paths(fixture,(10,1.,42),destinations)
for run in bridges.values():
    assert run[0] in paths(fixture,run[-1],[run[0]])[str(run[0])]

def lane(v):
    cells={f'{x},{y},{z}':cell(v,x,y,z)[0] for x in range(77,94) for y in range(7) for z in range(29,43)}
    run=subprocess.run(['node','--experimental-vm-modules','scripts/tests/guild_archery_voxels.mjs'],cwd=ROOT,
                       input=json.dumps({'cells':cells}),text=True,capture_output=True,check=True)
    return json.loads(run.stdout)

out={'scope':'Read-only survey; 22 hypothetical fence cells applied in RAM only; no production change',
     'native_collision_and_navigation':'unrun','serialized_asset_matches_generator':True,
     'asset_sha256':hashlib.sha256(asset.read_bytes()).hexdigest(),
     'generator_sha256':hashlib.sha256((ROOT/'scripts/gen_structures.py').read_bytes()).hexdigest(),
     'no_existing_bridge_gap_reproduced':True,'bridge_routes':bridges,'bridge_failure_fixtures':bridge_negatives,
     'candidate_rail_cells':[{'at':p,'before':cell(vox,*p),'support':cell(vox,p[0],0,p[2])} for p in sorted(rail_cells)],
     'protected_local_routes':local_runs,'baseline_gate_paths':gate_paths,'hypothetical_rail_gate_paths':fixture_paths,
     'actual_skill_harness_baseline':lane(vox),'actual_skill_harness_hypothetical_rails':lane(fixture),
     'recommendation':'Keep bridge centerlines unchanged. Rail cells are feasible under this conservative model; require measured original-reference rationale before authoring.'}
Path(__file__).with_suffix('.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({'bridges_clear':len(bridges),'bridge_negatives':len(bridge_negatives),'candidate_rail_cells':len(rail_cells),
                  'retained_local_routes':len(local_runs),'gate_destinations_retained':len(destinations),
                  'actual_skill_harness':'baseline and hypothetical rails pass','native':'unrun'},indent=2))

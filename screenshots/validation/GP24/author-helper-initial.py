from pathlib import Path
from collections import Counter
from PIL import Image,ImageDraw,ImageFont
import copy,hashlib,importlib.util,json,math,sys,types
ROOT=Path.cwd();OUT=ROOT/'tmp/conformance/gp24-author'
sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'scripts/tests')]
spec=importlib.util.spec_from_file_location('gp24_retained_review',ROOT/'screenshots/validation/GP23/independent-review.py')
review=importlib.util.module_from_spec(spec);spec.loader.exec_module(review);gp=review.gp
sha=lambda data:hashlib.sha256(data).hexdigest()
before_raw=(OUT/'baseline-guild.mcstructure').read_bytes();asset=ROOT/'packs/Fablecraft_BP/structures/fc/guild_hall.mcstructure';after_raw=asset.read_bytes()
assert before_raw!=after_raw,'Root must complete behavior-first targeted regeneration before this helper.'
(OUT/'current-guild.mcstructure').write_bytes(after_raw)
before=gp.reader.voxel(gp.reader.decode(before_raw));after=gp.reader.voxel(gp.reader.decode(after_raw))
changes=gp.changed(before,after);allowed={(x,1,z) for x in (38,42) for z in (37,39,41,43,45,47)}
assert {tuple(c['at']) for c in changes}==allowed
for c in changes:
 x,y,z=c['at']; assert c['before'][0]=='minecraft:oak_stairs'
 assert c['after']==(('minecraft:red_carpet',{}) if z in (41,43) else ('minecraft:air',{}))
assert before.palette==after.palette
# Actual old/new owners are built in memory only; root owns serialized regeneration.
def build(path,label):
 module=types.ModuleType('gp24_author_'+label);module.__file__=str(ROOT/'scripts/gen_structures.py');exec(compile(path.read_text(),module.__file__,'exec'),module.__dict__)
 orig=module.rng;streams=[]
 def traced(*keys):
  r=orig(*keys);streams.append((keys,r));return r
 module.rng=traced;v=module.build_guild_hall()
 return module,v,[(keys,repr(r.getstate())) for keys,r in streams]
bmod,bgen,brng=build(OUT/'baseline-gen_structures.py','before');amod,agen,arng=build(ROOT/'scripts/gen_structures.py','after')
assert not gp.changed(before,bgen) and not gp.changed(after,agen)
assert brng==arng and bmod.GUILD_LAYOUT==amod.GUILD_LAYOUT
nodes,reached,paths=gp.trace(before,(10,1.,42),gp.DESTINATIONS);anodes,areached,apaths=gp.trace(after,(10,1.,42),gp.DESTINATIONS)
assert nodes<=anodes and reached<=areached
for path in paths.values():gp.GuildRoutes().check_run(path,after)
for path in gp.LOCAL.values():gp.GuildRoutes().check_run(path,after)
# New across-seat paths model the four carpet cells as 1/16-block high. At
# those gaps the whole segment is raised to the carpet surface; actual small
# step transitions remain native-unrun. Surrounding seats use full columns.
def span(name,states,y):
 if name=='minecraft:red_carpet':return y,y+.0625
 return gp.interval(name,states,y)
def crossing_hits(vox,x,z,feet):
 a=(x-.5,feet,z+.5);b=(x+1.5,feet,z+.5);hits=[]
 for xx in range(36,46):
  for yy in range(8):
   for zz in range(33,52):
    limits=span(*gp.cell(vox,xx,yy,zz),yy)
    if limits and review.prior.segment_box(a,b,(xx-.35,limits[0]-1.9,zz-.35),(xx+1+.35,limits[1],zz+1+.35)):
     hits.append((xx,yy,zz))
 return hits
crossings=[]
for x,y,z in sorted(allowed):
 feet=1.0625 if z in (41,43) else 1.;blocked=crossing_hits(before,x,z,feet);clear=crossing_hits(after,x,z,feet)
 assert blocked and not clear
 assert gp.cell(before,x,0,z)==gp.cell(after,x,0,z)
 ceiling=next(yy for yy in range(3,after.sy) if gp.cell(after,x,yy,z)[0]!='minecraft:air')
 assert ceiling in (6,7)
 crossings.append({'at':[x,y,z],'feet':feet,'old_hits':blocked,'new_hits':clear,'ceiling_underside':ceiling,'modeled_head_top':feet+1.9,'remaining_headroom':ceiling-feet-1.9})
# Negative fixtures: spacing no-op, extra unowned block edit and reblocked gap.
negative={}
try:assert not any(gp.cell(before,x,1,z)[0]=='minecraft:oak_stairs' and gp.cell(before,x,1,z+1)[0]=='minecraft:oak_stairs' for x in (38,42) for z in range(36,47))
except AssertionError:negative['continuous_seating_rejected']=True
fixture=copy.deepcopy(after);fixture.grid[fixture.idx(37,0,35)]=fixture.palette.index(('minecraft:air',{}));negative['nonseat_change_rejected']=any(tuple(c['at']) not in allowed for c in gp.changed(before,fixture))
fixture=copy.deepcopy(after);fixture.grid[fixture.idx(38,1,37)]=before.grid[before.idx(38,1,37)];negative['blocked_gap_rejected']=bool(crossing_hits(fixture,38,37,1.))
assert all(negative.values())
# Focused cutaways use actual serialized voxels. Furniture box x37..44,
# y0..3,z34..50; roof/walls omitted to expose spacing. Carpet is 1/16 high,
# stairs use a lower half plus an approximate outward upper half.
font=ImageFont.truetype('DejaVuSans.ttf',17);small=ImageFont.truetype('DejaVuSans.ttf',14)
def render(v,label,view):
 yaw,pitch={'side':(.10,.5),'approach':(.72,.64)}[view];quads=[]
 for x in range(37,45):
  for y in range(4):
   for z in range(34,51):
    name,st=gp.cell(v,x,y,z)
    if name=='minecraft:air':continue
    col=gp.renderer.BLOCK_COLORS.get(name,(160,145,125));tex=Image.new('RGBA',(2,2),col+(255,));boxes=[((x,y,z),(1,1,1))]
    if name=='minecraft:red_carpet':boxes=[((x,y,z),(1,.0625,1))]
    elif name.endswith('_stairs'):
     direction=st.get('weirdo_direction',0);boxes=[((x,y,z),(1,.5,1))]
     if direction in (0,1):boxes.append(((x+(.5 if direction==0 else 0),y+.5,z),(.5,.5,1)))
     else:boxes.append(((x,y+.5,z+(.5 if direction==2 else 0)),(1,.5,.5)))
    elif name.endswith('_fence'):boxes=[((x+.375,y,z+.375),(.25,1,.25))]
    elif name=='minecraft:lantern':boxes=[((x+.3,y,z+.3),(.4,.6,.4))]
    elif name=='minecraft:cake':boxes=[((x+.0625,y,z+.0625),(.875,.5,.875))]
    for loc,size in boxes:quads.extend(gp.renderer.cube_quads(loc,size,(0,0),tex))
 quads.extend(gp.renderer.cube_quads((37,0,34),(8,4,17),(0,0),Image.new('RGBA',(2,2))))
 raw=gp.renderer.render_quads(quads,size=(1150,680),zoom=38,yaw=yaw,pitch=pitch,shadow=False,rim=False)
 im=Image.new('RGB',(1150,805),(240,237,231));im.paste(raw,(0,45),raw);d=ImageDraw.Draw(im)
 d.text((20,12),'Guild dining | '+label+' | '+view,font=font,fill=(30,30,35))
 d.text((20,725),'Actual decoded voxels; fixed scale. Cutaway x37..44/y0..3/z34..50 omits walls and upper floor.',font=small,fill=(40,40,45))
 d.text((20,749),'Floor y1; overhead underside y6..7. Four new runner cells have a modeled 1/16-block rise.',font=small,fill=(40,40,45))
 d.text((20,773),'Approximate stair/fixture shapes and flat colors; native textures, lighting, collision and steps remain unrun.',font=small,fill=(40,40,45))
 path=OUT/f'dining-{view}-{label}.png';im.save(path);return path
images=[render(v,label,view) for view in ('side','approach') for label,v in [('GP23',before),('GP24',after)]]
# Source comparison remains ignored with all external pixels; never a pack asset.
sheet=Image.new('RGB',(1600,1270),(240,237,231));d=ImageDraw.Draw(sheet)
d.text((18,12),'Original TLC dining cues and bounded Minecraft seating-spacing change',font=font,fill=(30,30,35))
refs=[]
for i,sid in enumerate(('343658414','236178734')):
 path=ROOT/f'tmp/conformance/next-guild-reference/reference-{sid}.jpg';im=Image.open(path).convert('RGB');im.thumbnail((775,480));sheet.paste(im,(15+i*795,50));d.text((20+i*795,540),'Original TLC '+sid+' | distinct stools; exact count/layout unknown',font=small,fill=(40,40,45));refs.append({'id':sid,'path':str(path.relative_to(ROOT)),'sha256':sha(path.read_bytes())})
for i,label in enumerate(('GP23','GP24')):
 im=Image.open(OUT/f'dining-approach-{label}.png');im.thumbnail((785,555));sheet.paste(im,(10+i*795,585))
d.text((20,1170),'Supported cue: separated seats along a long table. Twelve stock stair chairs and one-block gaps are adaptations.',font=small,fill=(40,40,45))
d.text((20,1197),'Unresolved: round red stools, decorated tabletop/mugs, twin dining stairs, complete room dimensions and native lighting.',font=small,fill=(40,40,45))
d.text((20,1224),'External source pixels stay in ignored scratch. This sheet is a comparison aid, not a matched-camera or in-engine claim.',font=small,fill=(40,40,45))
sheet.save(OUT/'dining-reference-comparison.jpg',quality=94)
report={'purpose':'GP24 author verification of actual GP23/root-regenerated GP24 decoded voxels, in-memory owner RNG and bounded dining views.','baseline_commit':'4aed7cff4bdb6cecc706e2c4711067cab648d530','owner_sha256':sha((ROOT/'scripts/gen_structures.py').read_bytes()),'baseline_owner_sha256':sha((OUT/'baseline-gen_structures.py').read_bytes()),'baseline_asset_sha256':sha(before_raw),'current_asset_sha256':sha(after_raw),'changes':changes,'changed_cells':len(changes),'after_material_counts':dict(Counter(c['after'][0] for c in changes)),'all_nonseat_cells_exact':True,'unchanged_cells':len(before.grid)-len(changes),'palette_states_exact':before.palette==after.palette,'actual_baseline_owner_matches_serialized_asset':True,'actual_current_owner_matches_serialized_asset':True,'rng_stream_states_exact':brng==arng,'rng_stream_state_sha256':sha(json.dumps(brng).encode()),'layout_anchors_exact':bmod.GUILD_LAYOUT==amod.GUILD_LAYOUT,'walking':{'old_nodes':len(nodes),'new_nodes':len(anodes),'all_old_nodes_retained':nodes<=anodes,'old_reachable':len(reached),'new_reachable':len(areached),'all_old_reachable_retained':reached<=areached,'new_nodes':sorted(anodes-nodes),'seven_old_complete_paths_still_valid':True,'seven_bfs_paths_identical':paths==apaths,'eight_local_routes_pass':True,'new_gap_body_crossings':crossings,'negative_fixtures':negative},'carpet_height_limit':'Legacy walking graph treats carpet as passable at floor feet y1. Four new carpet gaps are rendered 1/16 high and conservatively swept at feet1.0625; continuous raised segments do not execute stepping transitions. Native Bedrock small-step/collider behavior remains unrun.','render_scope':'Actual serialized interior x37..44,y0..3,z34..50; walls and upper floor omitted. Fixed framing/scale. Stairs approximate two boxes, fences narrow posts, lanterns/cake simplified. Flat colors; no native textures or lighting.','source_refs':refs,'source_support':'Both full original343658414 and236178734 images reinspected. Separate low red-covered stools and long decorated tables are visible. Exact count/spacing, stock chair shape and positions remain adaptations.','twin_stairs':'Too broad for this bounded furniture pass: original two red-covered stair runs are visible, but cropped endpoints, upper connections and complete room dimensions are not. Current dining dormitory has a solid y7 floor, gallery bridge and external stair access. Adding twin internal stairs would require floor/stairwell/wall/bed/door circulation redesign, exceeding non-seat scope. Keep this as a next-layout audit, not a completed match.','next_scope':'Round red stool shape and decorated table runner/mugs need separately inspected prototypes; retain all table lighting until native light review. No full dining layout or Library lighting claim.','source_images_external':True,'initial_helper_correction':'Initial assumption of uniform y7 ceiling failed at two existing gallery supports x38,z41/43,y6. Original failure retained in author-initial.log; captions and ceiling assertion corrected to actual final cells, with no production change.','native_acceptance':'Unrun','authored_files':['scripts/gen_structures.py'],'staging':'None by author agent; root owns stage/commit and generation.'}
(OUT/'author-evidence.json').write_text(json.dumps(report,indent=2)+'\n')
(OUT/'README.md').write_text('''# GP24 dining seat authoring

Owner change: place opposing oak-stair seats on alternating rows within the existing x38/x42,y1,z36..47 allocation. Twelve remain at even z36..46. Later existing carpet placement naturally fills the four vacated cells at z41/43; eight other vacancies become air. Exactly12 former seat cells change, all non-seat geometry and RNG/layout anchors remain exact. No stool count, shape, material or one-block spacing is called canonical.

Both full original dining photos were reinspected. Separate low red stools support the spacing cue; round red seats, decorated tabletop/mugs and twin dining stairs remain incomplete. The current block chairs and rectangular geometry are Minecraft adaptations.

Actual baseline/current owner outputs match the respective decoded assets. All prior walking/reachable nodes survive, all seven old complete paths and eight local routes remain valid. Twelve gap-crossing sweeps clear at body radius0.35,height1.9; the four carpet segments use feet1.0625. Legacy graph passability still ignores carpet height, and these sweeps do not execute native step transitions. Overhead underside is y6 at the two x38,z41/43 gallery-support gaps and y7 at the other ten gaps. Three negative fixtures reject continuous seats, an unrelated floor edit and a reblocked gap.

Four focused decoded cutaways and the source-comparison sheet show the final result at fixed framing. They omit walls and upper floor, approximate stair/fixture shapes and use flat colors. External pixels and all files here remain ignored scratch. No native lighting, textures, NPC collider execution, walking or saved-world acceptance has run.

Twin dining stairs remain too broad: their full endpoints and upper connections are not shown, while the current upper floor is solid and served by gallery/external access. Authoring twin stairs would require a separately reviewed change to floors, walls, beds and routes. Root handles serialized regeneration, full validation, documentation and staging; this author changed only gen_structures.py.
''')
print(json.dumps({'changed':len(changes),'after_materials':report['after_material_counts'],'old_nodes':len(nodes),'new_nodes':len(anodes),'old_reachable':len(reached),'new_reachable':len(areached),'bfs_paths_identical':paths==apaths,'new_gap_sweeps':len(crossings),'negative_fixtures':negative,'source_sha256':report['owner_sha256'],'asset_sha256':report['current_asset_sha256'],'images':[str(p.relative_to(ROOT)) for p in images]},indent=2))

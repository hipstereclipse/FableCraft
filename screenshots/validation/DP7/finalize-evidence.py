from pathlib import Path
import hashlib,json,shutil,subprocess
root=Path.cwd();snap=root/'tmp/conformance/DP7-reviewed-snapshot';ev=root/'screenshots/validation/DP7';prior=root/'tmp/conformance/GP20-reviewed-snapshot'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for p in (snap/'screenshots/validation/DP7').iterdir():
 if p.is_file() and p.suffix in {'.log','.json','.md'}:shutil.copy2(p,ev/p.name)
results=json.loads((ev/'results.json').read_text())['checks'];assert len(results)==55 and all(v['exit_code']==0 for v in results.values())
syntax={}
for p in sorted((snap/'packs/Fablecraft_BP/scripts').rglob('*.js')):
 r=subprocess.run(['node','--input-type=module','--check'],input=p.read_bytes(),capture_output=True)
 assert r.returncode==0,(p,r.stderr)
 syntax[str(p.relative_to(snap))]={'sha256':sha(p),'exit_code':r.returncode}
assert len(syntax)==65
(ev/'additional-results.json').write_text(json.dumps({'syntax_checks':syntax,'fresh_C2':'contract-render.log','fresh_full_render':'full-render-summary.json','fresh_Guild_diagnostics':'diagnostics-results.json','engine_acceptance':'unrun'},indent=2)+'\n')
delta={}
for label,folder,suffix,allowed in [('structure_assets','packs/Fablecraft_BP/structures/fc','.mcstructure',['greatwood_gorge.mcstructure','arboretum.mcstructure']),('C2_images','screenshots/structures/contract','.png',['greatwood_gorge.png','arboretum.png'])]:
 rows={str(p.relative_to(snap)):{'before':sha(prior/p.relative_to(snap)) if (prior/p.relative_to(snap)).exists() else None,'after':sha(p)} for p in sorted((snap/folder).glob('*'+suffix))}
 assert len(rows)==36
 changes=[p for p,r in rows.items() if r['before']!=r['after']]
 assert set(changes)=={folder+'/'+n for n in allowed},changes
 delta[label]={'baseline':'GP20','compared_existing':35,'added':1,'changed':changes,'sha256':rows}
 if label=='C2_images':
  for p in changes:shutil.copy2(snap/p,root/p)
  for n in ['greatwood_gorge','arboretum']:shutil.copy2(snap/folder/(n+'.png'),ev/('contract-'+n+'.png'))
summary=json.loads((ev/'full-render-summary.json').read_text());assert sum(summary['png_counts'].values())==282,summary
current=snap/summary['output'];old=prior/'tmp/GP20-full-screenshots'
rows={str(p.relative_to(current)):{'before':sha(old/p.relative_to(current)) if (old/p.relative_to(current)).exists() else None,'after':sha(p)} for p in sorted(current.rglob('*.png'))};assert len(rows)==282
changed=[p for p,r in rows.items() if r['before']!=r['after']]
assert changed==['gallery/places.png','structures/arboretum.png','structures/greatwood_gorge.png'],changed
delta['full_render']={'baseline':'GP20 same Linux font and 33-file vanilla item cache','compared_existing':281,'added':1,'changed':changed,'sha256':rows}
(ev/'visual-delta.json').write_text(json.dumps(delta,indent=2)+'\n')
for name in ['arboretum','greatwood_gorge']:shutil.copy2(current/'structures'/(name+'.png'),ev/('full-'+name+'.png'))
shutil.copy2(current/'gallery/places.png',ev/'full-places-gallery.png')
print(json.dumps({'base':len(results),'syntax':len(syntax),'asset_changes':delta['structure_assets']['changed'],'C2_changes':delta['C2_images']['changed'],'full_png_changes':changed}))

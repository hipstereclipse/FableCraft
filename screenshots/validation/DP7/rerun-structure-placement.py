"""Re-run only the failed rectangular-placement fixture after dependency wiring."""
from pathlib import Path
import hashlib,json,subprocess,shutil
root=Path.cwd();out=root/'screenshots/validation/DP7';result_path=out/'results.json'
results=json.loads(result_path.read_text());key='structure-placement-tests'
assert results['checks'][key]['exit_code']!=0
shutil.copy2(result_path,out/'initial-results.json')
shutil.copy2(out/(key+'.log'),out/('initial-'+key+'.log'))
command=results['checks'][key]['command'];r=subprocess.run(command,cwd=root,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
(out/(key+'.log')).write_bytes(r.stdout)
assert r.returncode==0,r.stdout.decode()
results['checks'][key]['exit_code']=0;result_path.write_text(json.dumps(results,indent=2)+'\n')
files=['scripts/tests/structure_placement.test.cjs','packs/Fablecraft_BP/scripts/main.js']
(out/'placement-fixture-rerun.json').write_text(json.dumps({'command':command,'exit_code':0,'reason':'Only the older rectangular-placement fixture lacked the new external portal dependencies; production unchanged.','source':'reviewed Git index snapshot; only this fixture refreshed after the first full run','sha256':{p:hashlib.sha256((root/p).read_bytes()).hexdigest() for p in files}},indent=2)+'\n')
print('structure-placement-tests: PASS; initial failure retained')

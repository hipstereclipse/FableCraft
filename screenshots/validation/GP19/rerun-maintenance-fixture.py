"""Rerun the one failed GP19 gate after its test-boundary correction.

Run from the reviewed snapshot after refreshing only guild_maintenance.test.mjs
from the reviewed index. Retain the original failing output and result summary;
all other gate results stay untouched. This is not a second full validator run.
"""
from pathlib import Path
import hashlib,json,os,subprocess,sys
root=Path.cwd();out=root/'screenshots/validation/GP19'
results=json.loads((out/'results.json').read_text())
name='guild-maintenance-tests'
assert [n for n,v in results['checks'].items() if v['exit_code'] != 0]==[name]
(out/'initial-results.json').write_bytes((out/'results.json').read_bytes())
(out/'initial-guild-maintenance-tests.log').write_bytes((out/(name+'.log')).read_bytes())
command=results['checks'][name]['command']
r=subprocess.run(command,env=dict(os.environ,PYTHON=sys.executable),stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
(out/(name+'.log')).write_bytes(r.stdout)
results['checks'][name]['exit_code']=r.returncode
results['targeted_rerun']={'scope':'Only the failed maintenance gate rerun; production source unchanged',
 'reason':'Might-only actual-maintenance fixture was missing the new external activity-reservation dependency; explicitly supplies unmanaged=false',
 'test_sha256':hashlib.sha256((root/'scripts/tests/guild_maintenance.test.mjs').read_bytes()).hexdigest(),
 'original_results':'initial-results.json','original_log':'initial-guild-maintenance-tests.log','command':command,'exit_code':r.returncode}
(out/'results.json').write_text(json.dumps(results,indent=2)+'\n')
print(name,'PASS' if r.returncode==0 else 'FAIL')
raise SystemExit(r.returncode)

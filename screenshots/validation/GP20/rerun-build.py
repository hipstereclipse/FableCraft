"""Rerun only GP20's failed build after refreshing generated C2 source metadata.

Run from the reviewed snapshot after its fresh C2 renderer completes. Preserve
all original gate output; this is not a second complete validator run.
"""
from pathlib import Path
import hashlib,json,os,subprocess,sys
root=Path.cwd();out=root/'screenshots/validation/GP20'
results=json.loads((out/'results.json').read_text());name='build'
assert [n for n,v in results['checks'].items() if v['exit_code']!=0]==[name]
(out/'initial-results.json').write_bytes((out/'results.json').read_bytes())
(out/'initial-build.log').write_bytes((out/'build.log').read_bytes())
command=results['checks'][name]['command']
r=subprocess.run(command,env=dict(os.environ,PYTHON=sys.executable),stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
(out/'build.log').write_bytes(r.stdout);results['checks'][name]['exit_code']=r.returncode
paths=['scripts/gen_structures.py','scripts/gen_screenshots.py','packs/Fablecraft_BP/structures/fc/guild_hall.mcstructure','screenshots/structures/contract/evidence.json','screenshots/structures/contract/guild_hall.png']
results['targeted_rerun']={'scope':'Only the failed build gate rerun; no production-source or test change',
 'reason':'Initial build reached structure validation before fresh C2 generation replaced the old Guild asset/image hashes; C2 output is now included in the reviewed index',
 'validated_sha256':{p:hashlib.sha256((root/p).read_bytes()).hexdigest() for p in paths},
 'original_results':'initial-results.json','original_log':'initial-build.log','command':command,'exit_code':r.returncode}
(out/'results.json').write_text(json.dumps(results,indent=2)+'\n')
print('build','PASS' if r.returncode==0 else 'FAIL');raise SystemExit(r.returncode)

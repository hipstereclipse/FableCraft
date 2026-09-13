"""Run the final actual-adapter suite against DP7's main callback and current code.

Only main.js input changes; actual realm owners and generated room voxels remain
current. Expected red predecessor output is retained, never a green runtime claim.
"""
from pathlib import Path
import hashlib,json,subprocess,sys
ROOT=Path(__file__).resolve().parents[3]
OUT=Path(__file__).resolve().parent
BASE='e13127194b8bd596bf9db9fee03633a413825f24'
fixture=ROOT/'scripts/tests/arboretum_integration.test.mjs'
main_path='packs/Fablecraft_BP/scripts/main.js'
source=subprocess.check_output(['git','show',BASE+':'+main_path],cwd=ROOT).decode()
text=fixture.read_text()
needle="const main=readFileSync('packs/Fablecraft_BP/scripts/main.js','utf8')"
assert text.count(needle)==1
scratch=ROOT/'tmp/conformance/dp8';scratch.mkdir(parents=True,exist_ok=True)
probe=scratch/'predecessor-integration.mjs'
probe.write_text(text.replace(needle,'const main='+json.dumps(source),1))
command=['node','--experimental-vm-modules',str(probe.relative_to(ROOT))]
result=subprocess.run(command,cwd=ROOT,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
(OUT/'predecessor-integration.log').write_text(result.stdout)
assert result.returncode!=0 and 'tests 20' in result.stdout and 'fail 4' in result.stdout,result.stdout
hashes={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in [main_path,str(fixture.relative_to(ROOT)),'packs/Fablecraft_BP/scripts/fc_demon_doors.js','packs/Fablecraft_BP/scripts/arboretum_doors.js','scripts/door_realms.py']}
summary={'baseline':BASE,'baseline_main_sha256':hashlib.sha256(source.encode()).hexdigest(),'current_inputs_sha256':hashes,'command':command,'exit_code':result.returncode,'expected_predecessor_failures':4,'retained_predecessor_passes':16,'scope':'Final actual main-adapter tests; only main source replaced by actual DP7 commit. Current realm owners and actual generated voxels.','native_acceptance':'unrun'}
(OUT/'predecessor-comparison.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps(summary,indent=2))

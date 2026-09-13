"""DP7 named geometry owners only; capture exact whole-pack mutation scope."""
from pathlib import Path
import hashlib
import json
import sys
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[3]
OUT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'scripts'))
import gen_structures as g

def hashes():
    return {str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()
            for p in (ROOT/'packs').rglob('*') if p.is_file()}

behavior=(OUT/'geometry-pre-regeneration-behavior.log').read_text()
assert 'Ran 8 tests' in behavior and '\nOK\n' in behavior, 'Behavior regression must pass before regeneration'
before=hashes()
# Rebuild the unrelated library only in ignored scratch to prove its output
# remains byte-identical; never regenerate it in the pack for this pass.
temporary=ROOT/'tmp/conformance/dp7/library-no-drift'
with patch.object(g,'BP',temporary):g.library_arcanum()
library='packs/Fablecraft_BP/structures/fc/library_arcanum.mcstructure'
assert (temporary/'structures/fc/library_arcanum.mcstructure').read_bytes()==(ROOT/library).read_bytes()
g.greatwood_gorge()
g.arboretum()
after=hashes()
changes=[{'path':p,'before':before.get(p),'after':after.get(p)}
         for p in sorted(before.keys()|after.keys()) if before.get(p)!=after.get(p)]
expected=['packs/Fablecraft_BP/structures/fc/arboretum.mcstructure',
          'packs/Fablecraft_BP/structures/fc/greatwood_gorge.mcstructure']
result={'files_before':len(before),'files_after':len(after),'changes':changes,
        'library_arcanum_owner_equals_unchanged_shipped':True,'library_sha256':before[library],
        'behavior_before_generation':'geometry-pre-regeneration-behavior.log',
        'source_sha256':{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
                         for p in ('scripts/gen_structures.py','scripts/door_realms.py')}}
(OUT/'targeted-geometry-drift.json').write_text(json.dumps(result,indent=2)+'\n')
assert [p['path'] for p in changes]==expected, changes
print(json.dumps(result,indent=2))

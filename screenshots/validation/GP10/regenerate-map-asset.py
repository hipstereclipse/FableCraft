"""Targeted GP10 regeneration in an isolated reviewed snapshot."""
import hashlib,json
from pathlib import Path
import sys
sys.path.insert(0,str(Path.cwd()/'scripts'))
import gen_structures as gs
root=Path.cwd();out=root/'screenshots/validation/GP10'
def pack_hashes():
    return {str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest()
            for p in (root/'packs').rglob('*') if p.is_file()}
before=pack_hashes()
gs.guild_hall()
after=pack_hashes()
changed=[{'path':p,'before_sha256':before.get(p),'after_sha256':after.get(p)}
         for p in sorted(before.keys()|after.keys()) if before.get(p)!=after.get(p)]
assert len(changed)==1 and changed[0]['path']=='packs/Fablecraft_BP/structures/fc/guild_hall.mcstructure',changed
record={'command':'python screenshots/validation/GP10/regenerate-map-asset.py','scope':'Only gs.guild_hall() inside isolated staged GP10 snapshot; behavior test8 passed before regeneration','exit_code':0,'changed_count':len(changed),'changes':changed,'owner_sha256':{p:hashlib.sha256((root/p).read_bytes()).hexdigest() for p in ['scripts/gen_structures.py','scripts/fc_lib.py']}}
(out/'targeted-generated-drift.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps(record,indent=2))

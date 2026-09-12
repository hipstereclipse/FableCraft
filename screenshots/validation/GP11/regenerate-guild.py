from pathlib import Path
import sys, hashlib, json
sys.path.insert(0,str(Path.cwd()/'scripts'))
import gen_structures as gs
root=Path.cwd(); out=root/'screenshots/validation/GP11'
def hashes(): return {str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in (root/'packs').rglob('*') if p.is_file()}
before=hashes(); gs.guild_hall(); after=hashes()
changes=[{'path':n,'before_sha256':before.get(n),'after_sha256':after.get(n)} for n in sorted(before.keys()|after.keys()) if before.get(n)!=after.get(n)]
assert [c['path'] for c in changes]==['packs/Fablecraft_BP/structures/fc/guild_hall.mcstructure']
(out/'targeted-generated-drift.json').write_text(json.dumps({'command':'python screenshots/validation/GP11/regenerate-guild.py','changes':changes,'scope':'GP10 reviewed index plus separately reviewed GP11 patch; no GP12/13 source'},indent=2)+'\n')
print(json.dumps(changes,indent=2))

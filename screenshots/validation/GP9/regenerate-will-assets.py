"""Targeted GP9 generated owners; run from the isolated reviewed snapshot root."""
import hashlib,json
from pathlib import Path
import sys
sys.path.insert(0, str(Path.cwd()/'scripts'))
import fc_mobs
import gen_structures as gs
import gen_resources as gr
import gen_entity_textures as gt
import gen_emotes as ge
from fc_lib import RP, write_json
root=Path.cwd(); out=root/'screenshots/validation/GP9'
def files():
    return {str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest()
            for p in (root/'packs').rglob('*') if p.is_file()}
before=files()
will=next(m for m in fc_mobs.MOBS if m['id']=='guild_apprentice_will')
gs.guild_hall()
gr.emit_geometry(will)
gr.emit_client_entity(will)
gt.paint_mob(will)
gt.paint_mob_married(will)
write_json(RP/'animations/fable_npc.animation.json',ge.npc_animations())
after=files()
changed=[{'path':p,'before_sha256':before.get(p),'after_sha256':after.get(p)}
         for p in sorted(before.keys()|after.keys()) if before.get(p)!=after.get(p)]
record={'command':'python screenshots/validation/GP9/regenerate-will-assets.py','scope':'isolated staged GP9 snapshot only; no behavior regeneration','changed_count':len(changed),'changes':changed}
(out/'targeted-generated-drift.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps(record,indent=2))

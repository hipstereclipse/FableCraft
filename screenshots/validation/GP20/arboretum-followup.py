#!/usr/bin/env python3
"""Read-only owner/shipped-asset audit. Writes only local candidate evidence."""
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'scripts/tests')]
import fc_data as DATA
import gen_structures as GS
spec=importlib.util.spec_from_file_location('retained_nbt_reader',ROOT/'screenshots/validation/GP18/independent_review_probe.py')
reader=importlib.util.module_from_spec(spec);spec.loader.exec_module(reader)
captured=[]
with patch.object(GS.Vox,'save',lambda v,name:captured.append((name,v))):
    GS.greatwood_gorge()
assert len(captured)==1 and captured[0][0]=='greatwood_gorge'
authored=captured[0][1]
asset=ROOT/'packs/Fablecraft_BP/structures/fc/greatwood_gorge.mcstructure'
shipped=reader.voxel(reader.decode_nbt(asset.read_bytes()))
assert (shipped.sx,shipped.sy,shipped.sz)==(authored.sx,authored.sy,authored.sz)==(39,16,43)
assert len(shipped.grid)==len(authored.grid)
assert all(shipped.palette[a]==authored.palette[b] for a,b in zip(shipped.grid,authored.grid))
legacy=[{'index':i,'id':d['id'],'requirement':d['requirement'],'reward':d['reward']} for i,d in enumerate(DATA.DEMON_DOORS)]
assert [d['id'] for d in legacy]==['gourmand','warrior','judge','corrupted','hoarder','moonlit','riddler','arboretum']
assert list(DATA.CANONICAL_DEMON_DOORS)==['guild_library_arcanum']
item=next(i for i in DATA.CONSUMABLES if i['id']=='crunchy_chick')
adapter=subprocess.run(['node',str(Path(__file__).with_suffix('.mjs'))],cwd=ROOT,capture_output=True,text=True,check=True)
paths=['scripts/fc_data.py','scripts/gen_structures.py','scripts/door_realms.py',
       'packs/Fablecraft_BP/scripts/main.js','packs/Fablecraft_BP/scripts/fc_demon_doors.js',
       'packs/Fablecraft_BP/scripts/wd/alignment.js','packs/Fablecraft_BP/scripts/wd/state.js',
       'packs/Fablecraft_BP/structures/fc/greatwood_gorge.mcstructure',
       'tmp/conformance/reference-arcanum/prima-tlc-guide.pdf',
       'tmp/conformance/dp7-candidate/prima-p173-image-018.png',
       'tmp/conformance/dp7-candidate/prima-p46-image-017.png']
output={'scope':'DP7 candidate only; no production, saved-world or staging mutations',
        'head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        'existing_canonical_ids':list(DATA.CANONICAL_DEMON_DOORS),'legacy_catalogue':legacy,
        'actual_scatter':json.loads(adapter.stdout),'gorge_generated_matches_shipped':True,
        'compared_gorge_cells':len(shipped.grid),'existing_crunchy_chick_morality':item['morality'],
        'selected_candidate':'greatwood_gorge_arboretum',
        'reference_limits':{'source_image':[207,153],'interior_image':[116,180],
          'interior_label_visible':'The Arboretum','full_layout_or_native_acceptance':'unverified'},
        'source_sha256':{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in paths}}
Path(__file__).with_suffix('.json').write_text(json.dumps(output,indent=2)+'\n')
print(json.dumps(output,indent=2))

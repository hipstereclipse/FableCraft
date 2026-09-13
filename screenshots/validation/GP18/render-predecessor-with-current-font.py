"""Isolate GP18 geometry from the intervening committed Linux font improvement.

Run from the reviewed GP18 snapshot. The supplied baseline is the exact
f7e8755 gen_structures.py blob, loaded only in this temporary render process.
Current renderer/data/assets are retained; all output goes to ignored scratch.
"""
from pathlib import Path
import hashlib,json,sys,types
root=Path.cwd();sys.path.insert(0,str(root/"scripts"))
source=(root/"tmp/GP18-predecessor-gen_structures.py").read_bytes()
expected="e6362334bc8d97715ac92c379a4db718032fcdaaa5d64241acfcf810c4793ae6"
assert hashlib.sha256(source).hexdigest()==expected
baseline=types.ModuleType("gen_structures");baseline.__file__=str(root/"scripts/gen_structures.py")
sys.modules["gen_structures"]=baseline
exec(compile(source,baseline.__file__,"exec"),baseline.__dict__)
import gen_screenshots as render
render.SHOTS=root/"tmp/GP18-predecessor-font-full"
render.main()
new=root/"tmp/GP18-full-screenshots"
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rows={str(p.relative_to(new)):{"predecessor_with_current_font":sha(render.SHOTS/p.relative_to(new)),"GP18":sha(p)} for p in sorted(new.rglob("*.png"))}
assert len(rows)==281
changes=[n for n,r in rows.items() if r["predecessor_with_current_font"]!=r["GP18"]]
result={"baseline_commit":"f7e875564d7aa61885ba5324e0a2a743f6751363","baseline_owner_sha256":expected,"renderer_sha256":sha(root/"scripts/gen_screenshots.py"),"scope":"Actual preceding committed geometry rendered with the same current Linux font owner/cache as GP18; temporary module only, no production mutation","compared_pngs":len(rows),"changed":changes,"sha256":rows,"native_acceptance":"unrun"}
(root/"screenshots/validation/GP18/predecessor-font-comparison.json").write_text(json.dumps(result,indent=2)+"\n")
print("Predecessor with current font:",len(changes),"changed of",len(rows))

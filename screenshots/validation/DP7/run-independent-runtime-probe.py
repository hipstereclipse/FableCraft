"""Reproduce the independent controller probes without preexisting scratch."""
from pathlib import Path
import json
import subprocess
import sys
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'scripts'))
from gen_structures import Vox
from door_realms import build_arboretum

with patch.object(Vox,'save',lambda *_:None):
    vox=build_arboretum(Vox)
path=ROOT/'tmp/conformance/dp7/independent-runtime-geometry.json'
path.parent.mkdir(parents=True,exist_ok=True)
path.write_text(json.dumps({'size':[vox.sx,vox.sy,vox.sz],'grid':vox.grid,'palette':[p[0] for p in vox.palette]}))
command=['node','--experimental-vm-modules','screenshots/validation/DP7/independent-runtime-probe.mjs',*sys.argv[1:]]
raise SystemExit(subprocess.run(command,cwd=ROOT).returncode)

"""Reproduce DP9's observed predecessor defects using generated Library geometry."""
from pathlib import Path
import json, subprocess, sys, tempfile
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'scripts'))
from gen_structures import Vox
from door_realms import build_library_arcanum
class CaptureVox(Vox):
    def save(self, name): pass
room = build_library_arcanum(CaptureVox)
with tempfile.TemporaryDirectory(prefix='fc-dp9-baseline-') as temporary:
    owner = Path(temporary) / 'fc_demon_doors.js'
    owner.write_bytes(subprocess.check_output(['git', 'show', 'c001e51929401de8068b85aff42cb7d10fb4f3ec:packs/Fablecraft_BP/scripts/fc_demon_doors.js'], cwd=ROOT))
    fixture = Path(temporary) / 'room.json'
    fixture.write_text(json.dumps({'size': [room.sx, room.sy, room.sz], 'palette': [p[0] for p in room.palette], 'grid': room.grid}))
    raise SystemExit(subprocess.run(['node', '--experimental-vm-modules', str(Path(__file__).with_name('baseline-probes.mjs')), str(fixture), str(owner)], cwd=ROOT).returncode)

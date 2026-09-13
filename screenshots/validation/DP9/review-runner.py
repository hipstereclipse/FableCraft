"""Reproduce DP9's independent final review using generated Library geometry."""
from pathlib import Path
import json, subprocess, sys, tempfile
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'scripts'))
from gen_structures import Vox
from door_realms import build_library_arcanum
class CaptureVox(Vox):
    def save(self, name): pass
room = build_library_arcanum(CaptureVox)
with tempfile.TemporaryDirectory(prefix='fc-dp9-review-') as temporary:
    owner = Path(temporary) / 'fc_demon_doors.js'
    owner.write_bytes((ROOT / 'packs/Fablecraft_BP/scripts/fc_demon_doors.js').read_bytes())
    fixture = Path(temporary) / 'room.json'
    fixture.write_text(json.dumps({'size': [room.sx, room.sy, room.sz], 'palette': [p[0] for p in room.palette], 'grid': room.grid}))
    raise SystemExit(subprocess.run(['node', '--experimental-vm-modules', str(Path(__file__).with_name('review-probes.mjs')), str(fixture), str(owner)], cwd=ROOT).returncode)

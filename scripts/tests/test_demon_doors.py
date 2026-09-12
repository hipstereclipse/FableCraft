"""Run the owned portal module against the actual generated Library Arcanum."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
from gen_structures import Vox
from door_realms import build_library_arcanum


class CaptureVox(Vox):
    def save(self, name):
        """Tests capture geometry without regenerating repository artifacts."""


def main():
    room = build_library_arcanum(CaptureVox)
    with tempfile.TemporaryDirectory(prefix='fc-door-fixture-') as directory:
        fixture = Path(directory) / 'room.json'
        fixture.write_text(json.dumps({
            'size': [room.sx, room.sy, room.sz],
            'palette': [entry[0] for entry in room.palette], 'grid': room.grid,
        }), encoding='utf-8')
        return subprocess.run([
            'node', '--experimental-vm-modules',
            str(ROOT / 'scripts/tests/demon_doors.test.mjs'), str(fixture),
        ], cwd=ROOT).returncode


if __name__ == '__main__':
    raise SystemExit(main())

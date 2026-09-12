"""Reproduce the frozen production-callback cave audit without asset writes."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
from unittest.mock import patch

EVIDENCE = Path(__file__).resolve().parent
ROOT = EVIDENCE.parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
import gen_structures as GS

manifest = json.loads((EVIDENCE / 'source_manifest.json').read_text())
assert hashlib.sha256((EVIDENCE / 'source_callbacks.js').read_bytes()).hexdigest() == manifest['source_callbacks_sha256']
captured = {}
with patch.object(GS.Vox, 'save', lambda v, name: captured.setdefault(name, v)):
    GS.guild_hall()
    GS.chamber_of_fate()
geometry = {
    name: {'size': [v.sx, v.sy, v.sz], 'palette': v.palette, 'grid': v.grid}
    for name, v in captured.items()
}
(EVIDENCE / 'geometry_manifest.json').write_text(json.dumps({
    'generator_sha256': hashlib.sha256((ROOT / 'scripts/gen_structures.py').read_bytes()).hexdigest(),
    'geometry': {name: {'size': value['size'], 'sha256': hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()}
        for name, value in geometry.items()},
}, indent=2) + '\n')
with tempfile.TemporaryDirectory(prefix='fc-guild-cave-audit-') as directory:
    scratch = Path(directory)
    (scratch / 'structures.json').write_text(json.dumps(geometry))
    for command, log in ((['node', str(EVIDENCE / 'probe.mjs'), directory], 'runtime.log'),
                         ([sys.executable, str(EVIDENCE / 'routes.py'), directory], 'routes.log')):
        result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
        (EVIDENCE / log).write_text(result.stdout + result.stderr)
        if result.returncode:
            raise SystemExit(result.returncode)
    for name in ('runtime-report.json', 'route-report.json'):
        (EVIDENCE / name).write_bytes((scratch / name).read_bytes())
print('Actual callback and assembled-route evidence refreshed; no production/assets/world writes.')

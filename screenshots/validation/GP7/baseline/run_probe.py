"""Run frozen pre-GP7 helpers against foreign blocks and current generated voxels.

python screenshots/validation/GP7/baseline/run_probe.py
Outputs JSON only; no generated assets or live-world data are modified.
"""
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / 'scripts'))
import gen_structures as GS

vox = GS.build_guild_hall()
cells = [[x, y, z, vox.palette[vox.grid[vox.idx(x, y, z)]][0]]
         for x in range(59, 85) for y in range(4) for z in range(74, 97)]
result = subprocess.run(['node', str(Path(__file__).with_name('reproduce.mjs'))],
                        input=json.dumps(cells), text=True, capture_output=True, cwd=ROOT)
print(result.stdout, end='')
print(result.stderr, end='', file=sys.stderr)
raise SystemExit(result.returncode)

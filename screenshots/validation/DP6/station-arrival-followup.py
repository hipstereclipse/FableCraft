#!/usr/bin/env python3
"""Read-only GP20 geometry/prototype audit. Writes only its evidence JSON."""
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT / 'scripts'), str(ROOT / 'scripts/tests')]
import gen_structures as GS

spec = importlib.util.spec_from_file_location('gp18_decode', ROOT / 'screenshots/validation/GP18/independent_review_probe.py')
reader = importlib.util.module_from_spec(spec)
spec.loader.exec_module(reader)
asset = ROOT / 'packs/Fablecraft_BP/structures/fc/guild_hall.mcstructure'
vox = reader.voxel(reader.decode_nbt(asset.read_bytes()))
authored = GS.build_guild_hall()
assert (vox.sx, vox.sy, vox.sz) == (authored.sx, authored.sy, authored.sz)
assert all(vox.palette[a] == authored.palette[b] for a, b in zip(vox.grid, authored.grid))

def cell(x, y, z):
    return vox.palette[vox.grid[vox.idx(x, y, z)]][0]

tables = [[x, y, z] for x in range(vox.sx) for y in range(vox.sy) for z in range(vox.sz)
          if cell(x, y, z) == 'minecraft:fletching_table']
assert tables == [[91, 1, 40]]
# Conservative union of a search_range=10 candidate's moving search volume,
# while its feet stay inside x83.5..86.5, z39..40, y0.9..1.1. Add a horizontal
# rounding margin; y-1..3 covers both foot levels and search_height=1. These
# geometric bounds are a proposed script admission rule, not native semantics.
bounds = {'x': [72, 97], 'y': [-1, 3], 'z': [28, 51]}
cells = {f'{x},{y},{z}': cell(x, y, z) for x in range(72, 98)
         for y in range(4) for z in range(28, 52)}
# The structure contains no below-base layer. Supply an explicitly hypothetical
# readable empty layer for predicate tests; this is not generated-world evidence.
unserialized = [f'{x},-1,{z}' for x in range(72, 98) for z in range(28, 52)]
cells.update({where: 'minecraft:air' for where in unserialized})
result = subprocess.run(['node', '--experimental-vm-modules', str(Path(__file__).with_suffix('.mjs'))],
                        cwd=ROOT, input=json.dumps({'cells': cells, 'bounds': bounds}), text=True,
                        capture_output=True, check=True)
paths = ['packs/Fablecraft_BP/structures/fc/guild_hall.mcstructure',
         'packs/Fablecraft_BP/scripts/main.js', 'packs/Fablecraft_BP/scripts/guild_training.js',
         'packs/Fablecraft_BP/scripts/guild_activity.js', 'packs/Fablecraft_BP/scripts/guild_residents.js',
         'scripts/gen_behavior.py', 'scripts/gen_structures.py']
output = {'scope': 'Read-only proposed GP20; no native engine execution or production edits',
          'final_serialized_matches_current_generator': True,
          'campus_dimensions': [vox.sx, vox.sy, vox.sz], 'campus_fletching_tables': tables,
          'search_envelope': bounds, 'search_envelope_cell_count': len(cells),
          'below_base_cells_mocked_for_predicate_only': len(unserialized),
          'source_sha256': {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in paths},
          'prototype': json.loads(result.stdout)}
Path(__file__).with_suffix('.json').write_text(json.dumps(output, indent=2) + '\n')
print(json.dumps(output, indent=2))

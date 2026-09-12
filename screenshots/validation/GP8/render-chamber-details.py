"""Offline GP8 owner comparison; run from the repository root with Python/Pillow.

The frozen GP5 compatibility plan is the byte-equivalent GP7 Chamber baseline.
No native game/reference pixels are embedded. Slabs retain their native halves;
lanterns and all other blocks retain the diagnostic renderer's cube convention.
"""
from collections import Counter
import copy
import hashlib
import json
import math
from pathlib import Path
import sys

from PIL import Image

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT / 'scripts'), str(ROOT / 'scripts/tests')]
import gen_structures as g
import gen_screenshots as render
from test_chamber_routes import clear, reached

COLORS = dict(render.BLOCK_COLORS)
# Explicit approximate colors for old materials absent from the general preview
# palette; no missing block silently receives the renderer's magenta fallback.
COLORS.update({
    'minecraft:orange_glazed_terracotta': (170, 105, 40),
    'minecraft:red_glazed_terracotta': (148, 62, 47),
    'minecraft:light_blue_glazed_terracotta': (84, 145, 175),
    'minecraft:black_glazed_terracotta': (52, 47, 52),
    'minecraft:white_glazed_terracotta': (200, 194, 178),
    'minecraft:yellow_glazed_terracotta': (201, 160, 54),
    'minecraft:lime_glazed_terracotta': (111, 146, 67),
    'minecraft:green_glazed_terracotta': (79, 105, 57),
    'minecraft:chain': (65, 65, 68), 'minecraft:glass': (190, 220, 235),
})

out = Path(__file__).resolve().parent
baseline = ROOT / 'scripts/data/guild_chamber_gp5.json'
plan = json.loads(baseline.read_text())
old = g.Vox(*plan['size'])
old.palette = [(entry['name'], entry['states']) for entry in plan['palette']]
old.pal_idx = {(name, tuple(sorted(states.items()))): i
               for i, (name, states) in enumerate(old.palette)}
old.grid = [index for index, count in plan['runs'] for _ in range(count)]
new = g.build_chamber_of_fate()


def detail(vox, bounds, yaw, pitch, altar=False):
    quads = []
    for x in range(bounds[0], bounds[1] + 1):
        for y in range(bounds[2], bounds[3] + 1):
            for z in range(bounds[4], bounds[5] + 1):
                if altar and math.hypot(x - 15, z - 15) > 8.6:
                    continue
                name, states = vox.palette[vox.grid[vox.idx(x, y, z)]]
                if name == 'minecraft:air':
                    continue
                slab = name.endswith('_slab')
                height = .5 if slab else 1
                upper = states.get('minecraft:vertical_half') == 'top' or states.get('top_slot_bit')
                offset = .5 if slab and upper else 0
                tex = Image.new('RGBA', (2, 2), COLORS[name] + (255,))
                quads.extend(render.cube_quads((x, y + offset, z), (1, height, 1), (0, 0),
                                               tex, glow=name in render.GLOW_BLOCKS))
    return render.render_quads(quads, size=(1100, 850), yaw=yaw, pitch=pitch, shadow=False)


def cutaway(vox):
    cut = copy.deepcopy(vox)
    cut.fill(0, 12, 0, 30, 19, 30, 'minecraft:air')
    for x in range(31):
        for z in range(15):
            if math.hypot(x - 15, z - 15) > 10.5:
                cut.fill(x, 2, z, x, 11, z, 'minecraft:air')
    return cut


for label, vox in [('before', old), ('after', new)]:
    detail(cutaway(vox), (0, 30, 0, 11, 0, 30), math.pi + .2, .65).save(
        out / f'chamber-open-cutaway-{label}.png')
    detail(vox, (23, 29, 1, 11, 9, 21), math.pi / 2 + .12, .1).save(
        out / f'chamber-east-bay-{label}.png')
    detail(vox, (6, 24, 1, 4, 6, 24), 2.4, .68, altar=True).save(
        out / f'chamber-altar-{label}.png')

ring = {(x, z) for x in range(31) for z in range(31) if 8.6 < math.hypot(x - 15, z - 15) <= 10.5}
summary = {}
for label, vox in [('before', old), ('after', new)]:
    counts = Counter(vox.palette[index][0] for index in vox.grid)
    connected = reached(vox, (15, 2., 0))
    summary[label] = {
        'outer_walk_cells': len(ring),
        'outer_walk_blocked': [[x, z] for x, z in sorted(ring) if not clear(vox, x, 2., z)],
        'outer_walk_reachable_at_y2': sum((x, 2., z) in connected for x, z in ring),
        'material_counts': {name: counts[name] for name in (
            'minecraft:glowstone', 'minecraft:quartz_block', 'minecraft:quartz_pillar',
            'minecraft:gold_block', 'minecraft:campfire', 'minecraft:lantern',
            'minecraft:water', 'minecraft:glass')},
    }
summary['changed_cells'] = sum(old.palette[a] != new.palette[b] for a, b in zip(old.grid, new.grid))
(out / 'chamber-comparison.json').write_text(json.dumps(summary, indent=2) + '\n')
(out / 'chamber-render-scope.json').write_text(json.dumps({
    'baseline_owner': 'scripts/data/guild_chamber_gp5.json (unchanged GP5/GP7 Chamber geometry)',
    'baseline_sha256': hashlib.sha256(baseline.read_bytes()).hexdigest(),
    'source_after': 'scripts/gen_structures.py:build_chamber_of_fate',
    'scope': 'Offline flat-color voxel geometry, native half-slab heights; other blocks including lamps are cubes. No engine lighting or perspective.',
    'open_cutaway': 'Remove y>=12 and the north half of the outer wall at radius>10.5 above the floor. Camera looks south into the retained walls.',
    'east_bay': 'Isolate x23..29/y1..11/z9..21, face the east wall from inside at low pitch. Adjacent room is cropped.',
    'altar': 'Crop radius8.6/y1..4. Exact protected altar ends at radius8.4; two obsolete floor lanterns beyond it disappear.',
}, indent=2) + '\n')
print(json.dumps(summary, indent=2))

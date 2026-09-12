"""Offline GP12 Library before/after; native slab halves, approximate colors."""
from collections import Counter
import hashlib
import json
import math
from pathlib import Path
import sys
from unittest.mock import patch

from PIL import Image

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT / 'scripts'), str(ROOT / 'scripts/tests')]
import gen_structures as g
import gen_screenshots as render
from test_guild_library import permitted_change, previous_library_interior
from test_guild_routes import cell

OUT = Path(__file__).resolve().parent
with patch.object(g, 'build_guild_library_interior', previous_library_interior):
    before = g.build_guild_hall()
after = g.build_guild_hall()


def detail(vox, bounds, yaw, pitch, cut=False):
    quads = []
    for x in range(bounds[0], bounds[1] + 1):
        for y in range(bounds[2], bounds[3] + 1):
            for z in range(bounds[4], bounds[5] + 1):
                if cut and x <= 20 and y >= 1:
                    continue
                name, states = cell(vox, x, y, z)
                if name == 'minecraft:air':
                    continue
                slab = name.endswith('_slab')
                height = .5 if slab else 1
                upper = states.get('minecraft:vertical_half') == 'top' or states.get('top_slot_bit')
                offset = .5 if slab and upper else 0
                tex = Image.new('RGBA', (2, 2), render.BLOCK_COLORS[name] + (255,))
                quads.extend(render.cube_quads((x, y + offset, z), (1, height, 1), (0, 0), tex,
                                               glow=name in render.GLOW_BLOCKS))
    return render.render_quads(quads, size=(1100, 850), yaw=yaw, pitch=pitch, shadow=False)


for label, vox in [('before', before), ('after', after)]:
    detail(vox, (18, 36, 0, 8, 16, 30), 1.35, .65, cut=True).save(
        OUT / f'library-open-cutaway-{label}.png')
    detail(vox, (34, 36, 0, 8, 17, 29), math.pi / 2 + .12, .12).save(
        OUT / f'library-east-bookcases-{label}.png')
    detail(vox, (29, 33, 0, 3, 19, 27), 2.4, .55).save(
        OUT / f'library-reading-desk-{label}.png')

changes, outside = [], [hashlib.sha256(), hashlib.sha256()]
for x in range(after.sx):
    for y in range(after.sy):
        for z in range(after.sz):
            old, new = cell(before, x, y, z), cell(after, x, y, z)
            if old != new:
                assert permitted_change(x, y, z), (x, y, z)
                changes.append([x, y, z])
            if not permitted_change(x, y, z):
                for digest, block in zip(outside, (old, new)):
                    digest.update(json.dumps([x, y, z, *block], sort_keys=True,
                                             separators=(',', ':')).encode() + b'\n')
summary = {}
for label, vox in [('before', before), ('after', after)]:
    counts = Counter(cell(vox, x, y, z)[0] for x in range(19, 36)
                     for y in range(1, 9) for z in range(17, 30))
    summary[label] = {name: counts[name] for name in (
        'minecraft:bookshelf', 'minecraft:dark_oak_planks', 'minecraft:spruce_slab',
        'minecraft:lectern', 'minecraft:lantern')}
summary.update({
    'baseline': 'test_guild_library.previous_library_interior reconstructs the pre-GP12 furnishings within the same final Guild builder.',
    'scope': 'Offline flat colors, native half-slab heights; other blocks including lamps and lecterns are cubes. No native lighting or player camera.',
    'open_cutaway': 'Crop x18..36/y0..8/z16..30. Remove west x18..20 above floor, including its bookcases/attached lamps, and the complete roof; opposite bookcases and desk remain visible.',
    'bookcases': 'Crop x34..36/y0..8/z17..29, looking east from inside at low pitch.',
    'desk': 'Crop x29..33/y0..3/z19..27; only the new desk area and unchanged floor.',
    'changed_cells': len(changes), 'changed_coordinates': changes,
    'outside_furnishings_sha256_before': outside[0].hexdigest(),
    'outside_furnishings_sha256_after': outside[1].hexdigest(),
    'shared_rng_draws_added_or_removed': 0,
})
assert summary['outside_furnishings_sha256_before'] == summary['outside_furnishings_sha256_after']
(OUT / 'library-render-scope.json').write_text(json.dumps(summary, indent=2) + '\n')
print(json.dumps({key: summary[key] for key in ('before', 'after', 'changed_cells')}, indent=2))

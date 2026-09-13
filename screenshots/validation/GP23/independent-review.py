#!/usr/bin/env python3
"""Independently compare actual committed DP10 and final GP23 Guild outputs."""
import argparse
import contextlib
import copy
from datetime import datetime, timezone
import hashlib
import importlib.util
import io
import json
import math
from pathlib import Path
import subprocess
import sys
import types

ROOT = next(p for p in Path(__file__).resolve().parents if (p / 'scripts/gen_structures.py').exists())
OUT = Path(__file__).resolve().parent
TEMP = ROOT / 'tmp/conformance/gp23-independent/owners'
BASE = '5fcf08a23389760762438c86092a8d3450f96195'
SOURCE = 'scripts/gen_structures.py'
ASSET = 'packs/Fablecraft_BP/structures/fc/guild_hall.mcstructure'
RAY = 'screenshots/validation/GP21/ray-collision-probe.mjs'
ARRIVAL = 'screenshots/validation/DP6/station-arrival-followup.mjs'
SHOT = 'scripts/tests/guild_archery_voxels.mjs'
sys.path[:0] = [str(ROOT / 'scripts'), str(ROOT / 'scripts/tests')]
spec = importlib.util.spec_from_file_location('retained_gp22_geometry', ROOT / 'screenshots/validation/GP22/independent-review.py')
prior = importlib.util.module_from_spec(spec)
spec.loader.exec_module(prior)
gp = prior.gp
sha = lambda data: hashlib.sha256(data).hexdigest()

# Explicit independent expectation; no candidate helper is disabled or imitated.
POSTS = [(x, z) for x in (58, 68) for z in (35, 37, 53, 55)]
EDIT = {(x, y, z) for x, z in POSTS for y in (2, 3)}


def committed(path):
    return subprocess.check_output(['git', 'show', BASE + ':' + path], cwd=ROOT)


def generate(source, label):
    module = types.ModuleType('gp23_actual_' + label)
    module.__file__ = str(ROOT / SOURCE)
    exec(compile(source, module.__file__, 'exec'), module.__dict__)
    module.BP = TEMP / label
    original_rng, streams = module.rng, []

    def observed(*keys):
        stream = original_rng(*keys)
        streams.append((keys, stream))
        return stream

    module.rng = observed
    with contextlib.redirect_stdout(io.StringIO()):
        module.guild_hall()
    raw = (module.BP / 'structures/fc/guild_hall.mcstructure').read_bytes()
    return module, raw, gp.reader.decode(raw), [(keys, repr(stream.getstate())) for keys, stream in streams]


def body_hits(vox, cells, paths, radius=.35, height=1.9):
    """Exact segment/AABB sweep of conservative fence/full-column bounds."""
    hits = []
    for name, path in paths.items():
        for first, last in zip(path, path[1:]):
            a = first[0] + .5, first[1], first[2] + .5
            b = last[0] + .5, last[1], last[2] + .5
            for x, y, z in sorted(cells):
                span = gp.interval(*gp.cell(vox, x, y, z), y)
                if span and prior.segment_box(a, b, (x - radius, span[0] - height, z - radius),
                                             (x + 1 + radius, span[1], z + 1 + radius)):
                    hits.append({'path': name, 'segment': [first, last], 'cell': [x, y, z]})
    return hits


def bridge_render(vox, label, zc, view):
    yaw, pitch = {'side': (.08, .35), 'approach': (math.pi / 2 + .24, .42)}[view]
    quads = []
    for x in range(56, 71):
        for y in range(6):
            for z in range(zc - 3, zc + 4):
                name, states = gp.cell(vox, x, y, z)
                if name == 'minecraft:air':
                    continue
                assert name in gp.renderer.BLOCK_COLORS, name
                texture = gp.Image.new('RGBA', (2, 2), gp.renderer.BLOCK_COLORS[name] + (255,))
                boxes = [((x, y, z), (1, 1, 1))]
                if name.endswith('_slab'):
                    upper = states.get('minecraft:vertical_half') == 'top' or states.get('top_slot_bit')
                    boxes = [((x, y + (.5 if upper else 0), z), (1, .5, 1))]
                elif name.endswith('_fence'):
                    boxes = [((x + .375, y, z + .375), (.25, 1, .25))]
                    for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        if gp.cell(vox, x + dx, y, z + dz)[0].endswith('_fence'):
                            for yy in (.375, .75):
                                boxes.append(((x + (.5 if dx >= 0 else 0), y + yy, z + .4375), (.5, .125, .125)) if dx else
                                             ((x + .4375, y + yy, z + (.5 if dz >= 0 else 0)), (.125, .125, .5)))
                elif name == 'minecraft:lantern':
                    boxes = [((x + .3, y, z + .3), (.4, .6, .4))]
                for start, size in boxes:
                    quads.extend(gp.renderer.cube_quads(start, size, (0, 0), texture))
    # Invisible common bounds stabilize BOTH scale and image centering. Without
    # this, the higher lamp heads would shift the unchanged deck in the renderer.
    quads.extend(gp.renderer.cube_quads((56, 0, zc - 3), (15, 6, 7), (0, 0), gp.Image.new('RGBA', (2, 2))))
    raw = gp.renderer.render_quads(quads, size=(1100, 640), zoom=52, yaw=yaw, pitch=pitch, shadow=False, rim=False)
    image = gp.Image.new('RGB', (1100, 760), (240, 237, 231))
    image.paste(raw, (0, 55), raw)
    draw = gp.ImageDraw.Draw(image)
    draw.text((20, 12), f'Decoded Guild bridge z{zc} | {label} | {view}', font=gp.ImageFont.truetype('DejaVuSans.ttf', 20), fill=(30, 30, 35))
    draw.text((20, 708), 'Actual serialized old/new geometry; fixed scale and framing. Rails/posts/lamps are simplified.', font=gp.ImageFont.truetype('DejaVuSans.ttf', 14), fill=(45, 45, 50))
    draw.text((20, 733), 'No native lighting, movement or collision run. Original opaque parapets and capped ends remain unresolved.', font=gp.ImageFont.truetype('DejaVuSans.ttf', 14), fill=(45, 45, 50))
    filename = f'independent-bridge-{zc}-{view}-{label}.png'
    image.save(OUT / filename)
    return filename


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--render', action='store_true')
    args = parser.parse_args()
    inputs = [SOURCE, ASSET, 'scripts/fc_lib.py', 'scripts/gen_screenshots.py', 'scripts/tests/test_guild_routes.py',
              'screenshots/validation/GP20/independent-review.py', 'screenshots/validation/GP21/independent-review.py',
              'screenshots/validation/GP22/independent-review.py', RAY, ARRIVAL, SHOT,
              'packs/Fablecraft_BP/scripts/main.js', 'packs/Fablecraft_BP/scripts/guild_training.js',
              'packs/Fablecraft_BP/entities/guild_apprentice_skill.json',
              'screenshots/validation/GP17/maze-study-final-voxel-survey.json', str(Path(__file__).relative_to(ROOT))]
    reviewed = {p: sha((ROOT / p).read_bytes()) for p in inputs}
    # This checkout carries inherited CRLF noise. Verify semantic identity of
    # the serializer dependency without rewriting either side's line endings.
    prior_library = committed('scripts/fc_lib.py')
    current_library = (ROOT / 'scripts/fc_lib.py').read_bytes()
    assert prior_library.replace(b'\r\n', b'\n') == current_library.replace(b'\r\n', b'\n')
    old_source, new_source = committed(SOURCE), (ROOT / SOURCE).read_bytes()
    old, old_raw, old_nbt, old_rng = generate(old_source, 'before')
    new, new_raw, new_nbt, new_rng = generate(new_source, 'after')
    assert old_raw == committed(ASSET), 'Actual DP10 generator differs from committed DP10 asset'
    assert new_raw == (ROOT / ASSET).read_bytes(), 'Actual GP23 generator differs from final shipped asset'
    assert old.GUILD_LAYOUT == new.GUILD_LAYOUT and old_rng == new_rng
    assert old_nbt.keys() == new_nbt.keys()
    for key in old_nbt:
        if key != 'structure':
            assert old_nbt[key] == new_nbt[key], key
    assert old_nbt['structure'].keys() == new_nbt['structure'].keys()
    for key in old_nbt['structure']:
        if key != 'block_indices':
            assert old_nbt['structure'][key] == new_nbt['structure'][key], key
    assert old_nbt['structure']['block_indices'][1:] == new_nbt['structure']['block_indices'][1:]
    before, after = gp.reader.voxel(old_nbt), gp.reader.voxel(new_nbt)
    changes = gp.changed(before, after)
    assert len(before.grid) == len(after.grid) == 395280 and len(changes) == 16
    assert {tuple(change['at']) for change in changes} == EDIT
    for change in changes:
        expected = [('minecraft:lantern', {'hanging': 0}), ('minecraft:dark_oak_fence', {})] if change['at'][1] == 2 else [('minecraft:air', {}), ('minecraft:lantern', {'hanging': 0})]
        assert [change['before'], change['after']] == expected
    for x, z in POSTS:
        assert gp.cell(before, x, 1, z) == gp.cell(after, x, 1, z) == ('minecraft:dark_oak_fence', {})
    rails = [(x, 2, z) for x in range(60, 67) for z in (35, 37, 53, 55)]
    assert len(rails) == 28
    for point in rails:
        assert gp.cell(before, *point) == gp.cell(after, *point) == ('minecraft:spruce_fence', {})
    for x in range(after.sx):
        for z in range(after.sz):
            for y in (0, 1):
                assert gp.cell(before, x, y, z) == gp.cell(after, x, y, z)
    water_before = [i for i, index in enumerate(before.grid) if before.palette[index][0] == 'minecraft:water']
    water_after = [i for i, index in enumerate(after.grid) if after.palette[index][0] == 'minecraft:water']
    assert water_before == water_after
    protected = json.loads((ROOT / 'screenshots/validation/GP17/maze-study-final-voxel-survey.json').read_text())['protected_cells']
    assert len(protected) == 678
    for saved in protected:
        for vox in (before, after):
            assert gp.cell(vox, *saved['at']) == (saved['name'], saved['states'])
    assert new.GUILD_LAYOUT['maze_spawn'] == (46, 70) and new.GUILD_LAYOUT['maze_study_y'] == 12
    bn, br, bpaths = gp.trace(before, (10, 1., 42), gp.DESTINATIONS)
    an, ar, apaths = gp.trace(after, (10, 1., 42), gp.DESTINATIONS)
    assert bn == an and br == ar and bpaths == apaths
    checker = gp.GuildRoutes()
    for vox in (before, after):
        for path in gp.LOCAL.values():
            checker.check_run(path, vox)
        for x in range(82, 85):
            checker.check_run([(x, 1., z) for z in range(37, 41)], vox)
    body_paths = {**gp.LOCAL, **{'gate_' + name: path for name, path in bpaths.items()}}
    body_paths.update({'gap_' + str(x): [(x, 1., z) for z in range(37, 41)] for x in range(82, 85)})
    body_paths['future_arrival_quarters'] = [(83 + i * .25, 1., 39) for i in range(13)]
    assert len(body_paths) == 19
    lateral_paths = {f'bridge_{zc}_lateral_{offset}': [(x, y, z + offset) for x, y, z in gp.BRIDGES[str(zc)]]
                     for zc in (36, 54) for offset in (-.15, -.10, 0., .10, .15)}
    collision_results = {}
    for label, vox in (('before', before), ('after', after)):
        collision_results[label] = {'protected_paths': body_hits(vox, EDIT, body_paths), 'lateral_bridge_paths': body_hits(vox, EDIT, lateral_paths)}
        assert not any(collision_results[label].values())
    collider = json.loads((ROOT / 'packs/Fablecraft_BP/entities/guild_apprentice_skill.json').read_text())['minecraft:entity']['components']['minecraft:collision_box']
    assert collider['width'] / 2 <= .35 and collider['height'] <= 1.9
    harnesses = {}
    for label, vox in (('before', before), ('after', after)):
        rays = gp.harness(vox, RAY)
        ray_hits = gp.ray_collisions(vox, rays)
        assert len(rays['rays']) == 5 and not any(ray_hits.values())
        arrival = gp.harness(vox, ARRIVAL, True)
        assert arrival['sampled_clear_corridor_points'] == 13 and len(arrival['prototype_negative_cases']) == 27
        harnesses[label] = {'actual_emitted_rays': rays, 'expanded_fence_ray_hits': ray_hits,
                            'shot': gp.harness(vox, SHOT), 'arrival': arrival}
    assert harnesses['before'] == harnesses['after']
    negatives = []
    for zc in (36, 54):
        for name, point, block in [('missing_deck', (63, 1, zc), 'minecraft:air'), ('missing_slab_approach', (59, 1, zc), 'minecraft:air'),
                                   ('headroom_block', (63, 3, zc), 'minecraft:stone'), ('centerline_post', (63, 2, zc), 'minecraft:dark_oak_fence')]:
            broken = copy.deepcopy(after)
            gp.setcell(broken, point, block)
            try:
                checker.check_run(gp.LOCAL[f'bridge_{zc}'], broken)
            except AssertionError as error:
                negatives.append({'name': f'{zc}_{name}', 'at': point, 'detected': True, 'reason': str(error)})
            else:
                raise AssertionError(name + ' was not detected')
            if name == 'centerline_post':
                hits = body_hits(broken, [point], body_paths)
                assert hits
                negatives[-1]['expanded_body_hits'] = hits
    fence = copy.deepcopy(after)
    gp.setcell(fence, (83, 1, 38), 'minecraft:spruce_fence')
    fence_hits = gp.ray_collisions(fence, harnesses['after']['actual_emitted_rays'])
    assert any(fence_hits.values())
    negatives.append({'name': 'lower_firing_fence_ray_overhang', 'detected': True, 'hits': fence_hits, 'block_cell_harness_still_passes': gp.harness(fence, SHOT)})
    lateral_limit = {f'bridge_{zc}_beyond_bound_{offset}': [(x, y, z + offset) for x, y, z in gp.BRIDGES[str(zc)]]
                     for zc in (36, 54) for offset in (-.16, .16)}
    before_limit = body_hits(before, EDIT, lateral_limit)
    after_limit = body_hits(after, EDIT, lateral_limit)
    assert before_limit and after_limit
    assert {hit['path'] for hit in before_limit} == {hit['path'] for hit in after_limit} == set(lateral_limit)
    negatives.append({'name': 'preexisting_conservative_post_clearance_limit', 'detected': True,
                      'before_hits': before_limit, 'after_hits': after_limit,
                      'meaning': 'The full-column collision bound refuses ±0.16 lateral offset in both versions; native fence width is not measured.'})
    report = {'baseline_commit': BASE, 'completed_utc': datetime.now(timezone.utc).isoformat(),
              'scope': 'Actual committed DP10/current GP23 full Guild generators and final serialized assets',
              'source_sha256': {'before': sha(old_source), 'after': sha(new_source)},
              'asset_sha256': {'before': sha(old_raw), 'after': sha(new_raw)},
              'owners_match_corresponding_shipped_assets': True, 'serialized_cells_compared': 395280,
              'actual_changes': changes, 'all_other_cells_exact': 395264,
              'all_ground_deck_slab_bank_pier_water_rail_cells_exact': True, 'water_cells': len(water_before),
              'lower_posts_exact': POSTS, 'deck_rails_exact': rails,
              'palette_states_entities_metadata_secondary_layers_origin_size_exact': True,
              'rng_layout_and_anchors_exact': True, 'rng_instances': len(old_rng), 'rng_calls_and_final_state_sha256': sha(json.dumps(old_rng).encode()),
              'layout_and_anchors': new.GUILD_LAYOUT, 'protected_maze_cells': 678, 'maze_anchor': [46, 12, 70],
              'walking_nodes': len(an), 'gate_reachable_nodes': len(ar), 'walking_graph_exact': True,
              'reachable_nodes_exact': True, 'seven_complete_gate_paths_exact': True, 'baseline_gate_paths': bpaths, 'current_gate_paths': apaths,
              'eight_local_routes_pass_both_directions': True, 'protected_local_routes': gp.LOCAL, 'firing_gap_columns_clear': 3,
              'expanded_body_review': {'radius': .35, 'height': 1.9, 'actual_entity_collider': collider, 'protected_paths': body_paths,
                                       'lateral_bridge_paths': lateral_paths, 'hits': collision_results,
                                       'model': 'Each changed fence is its full horizontal column through y+1.5; lanterns are full cubes. Analytic segment/AABB Minkowski bounds.'},
              'harnesses': harnesses, 'negative_fixtures': negatives,
              'native_acceptance': 'unrun',
              'limits': 'No engine execution. Cardinal graph uses a curated floor set. Body sweeps check changed columns against 19 protected paths and 10 bridge lateral paths; ±0.15 clearance is a conservative post-column result, not native fence geometry. Existing body navigation outside changed columns uses retained route checks. Arrival prototype treats 624 below-base cells as readable air; native search, offsets, events and saved-world content are uncalibrated. Eight lamp positions, materials and one-block rise are explicit Minecraft adaptations.',
              'serializer_dependency': {'before_sha256': sha(prior_library), 'after_sha256': sha(current_library),
                                        'equal_ignoring_only_CRLF': True},
              'reviewed_source_sha256': reviewed}
    if args.render:
        filenames = [bridge_render(vox, label, zc, view) for zc in (36, 54) for view in ('side', 'approach') for label, vox in (('before', before), ('after', after))]
        report['focused_views'] = filenames
        report['image_sha256'] = {name: sha((OUT / name).read_bytes()) for name in filenames}
        font = gp.ImageFont.truetype('DejaVuSans.ttf', 20)
        report['font'] = {'path': str(font.path), 'sha256': sha(Path(font.path).read_bytes())}
    assert reviewed == {p: sha((ROOT / p).read_bytes()) for p in inputs}, 'Reviewed inputs changed during run'
    (OUT / 'independent-summary.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({'passed': True, 'baseline': BASE, 'actual_changes': 16, 'other_cells_exact': 395264,
                      'walking_nodes': len(an), 'reachable_nodes': len(ar), 'gate_paths_exact': 7, 'local_routes': 8,
                      'protected_body_paths': 19, 'lateral_bridge_paths': 10, 'actual_rays': 5,
                      'arrival_samples': 13, 'arrival_refusals': 27, 'maze_reservations': 678,
                      'negative_fixtures': len(negatives), 'native': 'unrun'}))


if __name__ == '__main__':
    main()

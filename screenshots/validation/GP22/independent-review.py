#!/usr/bin/env python3
"""Compare actual DP9/current Guild owners and final serialized cells, read only.

Both generators run unchanged into ignored scratch. This review never edits a
pack asset or creates a disabled-helper stand-in for the actual predecessor.
"""
import argparse
import contextlib
import copy
from datetime import datetime, timezone
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import sys
import types

ROOT = next(p for p in Path(__file__).resolve().parents if (p / 'scripts/gen_structures.py').exists())
OUT = Path(__file__).resolve().parent
TEMP = ROOT / 'tmp/conformance/gp22-geometry/owners'
BASE = 'af73bfb42c3f742454c7cf88c17ad052c3f0cf41'
SOURCE = 'scripts/gen_structures.py'
ASSET = 'packs/Fablecraft_BP/structures/fc/guild_hall.mcstructure'
RAY = 'screenshots/validation/GP21/ray-collision-probe.mjs'
ARRIVAL = 'screenshots/validation/DP6/station-arrival-followup.mjs'
SHOT = 'scripts/tests/guild_archery_voxels.mjs'
sys.path[:0] = [str(ROOT / 'scripts'), str(ROOT / 'scripts/tests')]
spec = importlib.util.spec_from_file_location('gp21_review', ROOT / 'screenshots/validation/GP21/independent-review.py')
gp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gp)
sha = lambda data: hashlib.sha256(data).hexdigest()

# Independent explicit expectation, not read from the new production helper.
EDIT = {
    (80, 1, 32): 'minecraft:purple_terracotta',
    (81, 1, 32): 'minecraft:purple_terracotta',
    (81, 2, 32): 'minecraft:white_terracotta',
    (82, 1, 32): 'minecraft:purple_terracotta',
    (87, 1, 33): 'minecraft:light_blue_terracotta',
    (87, 2, 33): 'minecraft:light_blue_terracotta',
    (87, 3, 33): 'minecraft:light_blue_terracotta',
    (88, 1, 33): 'minecraft:black_wool',
    (88, 2, 33): 'minecraft:light_blue_terracotta',
    (89, 1, 33): 'minecraft:light_blue_terracotta',
    (89, 2, 33): 'minecraft:light_blue_terracotta',
    (89, 3, 33): 'minecraft:light_blue_terracotta',
}


def committed(path):
    return subprocess.check_output(['git', 'show', BASE + ':' + path], cwd=ROOT)


def generate(source, label):
    module = types.ModuleType('gp22_' + label)
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


def segment_box(a, b, low, high):
    """Analytic strict overlap; boundary contact alone does not enter a box."""
    entry, leave = 0., 1.
    for axis in range(3):
        delta = b[axis] - a[axis]
        if abs(delta) < 1e-12:
            if a[axis] <= low[axis] or a[axis] >= high[axis]:
                return False
        else:
            first, last = (low[axis] - a[axis]) / delta, (high[axis] - a[axis]) / delta
            entry, leave = max(entry, min(first, last)), min(leave, max(first, last))
    return entry < leave and leave > 0 and entry < 1


def added_body_hits(cells, paths, radius=.35, height=1.9):
    """Sweep feet-centre paths against added full cubes expanded by the body."""
    hits = []
    for name, path in paths.items():
        for first, last in zip(path, path[1:]):
            a = first[0] + .5, first[1], first[2] + .5
            b = last[0] + .5, last[1], last[2] + .5
            for x, y, z in cells:
                if segment_box(a, b, (x - radius, y - height, z - radius),
                               (x + 1 + radius, y + 1, z + 1 + radius)):
                    hits.append({'path': name, 'segment': [first, last], 'cell': [x, y, z]})
    return hits


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--render', action='store_true')
    args = parser.parse_args()
    inputs = [SOURCE, ASSET, 'scripts/gen_screenshots.py', 'scripts/tests/test_guild_routes.py',
              'screenshots/validation/GP20/independent-review.py',
              'screenshots/validation/GP21/independent-review.py', RAY, ARRIVAL, SHOT,
              'packs/Fablecraft_BP/scripts/main.js', 'packs/Fablecraft_BP/scripts/guild_training.js',
              'packs/Fablecraft_BP/entities/guild_apprentice_skill.json',
              'screenshots/validation/GP17/maze-study-final-voxel-survey.json',
              str(Path(__file__).relative_to(ROOT))]
    reviewed_hashes = {p: sha((ROOT / p).read_bytes()) for p in inputs}
    old_source, new_source = committed(SOURCE), (ROOT / SOURCE).read_bytes()
    old, old_raw, old_nbt, old_rng = generate(old_source, 'before')
    new, new_raw, new_nbt, new_rng = generate(new_source, 'after')
    assert old_raw == committed(ASSET), 'Actual predecessor generator differs from predecessor asset'
    assert new_raw == (ROOT / ASSET).read_bytes(), 'Current generator differs from final shipped asset'
    assert old.GUILD_LAYOUT == new.GUILD_LAYOUT
    assert old_rng == new_rng
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
    assert len(before.grid) == len(after.grid) == 395280
    changes = gp.changed(before, after)
    assert len(changes) == 12
    assert {tuple(change['at']) for change in changes} == set(EDIT)
    for change in changes:
        assert change['before'] == ('minecraft:air', {})
        assert change['after'] == (EDIT[tuple(change['at'])], {})
    assert all(y > 0 for x, y, z in EDIT)
    protected = json.loads((ROOT / 'screenshots/validation/GP17/maze-study-final-voxel-survey.json').read_text())['protected_cells']
    assert len(protected) == 678
    for saved in protected:
        for vox in (before, after):
            assert gp.cell(vox, *saved['at']) == (saved['name'], saved['states'])
    assert new.GUILD_LAYOUT['maze_spawn'] == (46, 70)
    assert new.GUILD_LAYOUT['maze_study_y'] == 12
    bn, br, bpaths = gp.trace(before, (10, 1., 42), gp.DESTINATIONS)
    an, ar, apaths = gp.trace(after, (10, 1., 42), gp.DESTINATIONS)
    footprint = {(x, 1., z) for x, y, z in EDIT}
    assert len(footprint) == 6
    assert bn - an == br - ar == footprint
    assert not an - bn and not ar - br
    assert bpaths == apaths
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
    body_hits = added_body_hits(EDIT, body_paths)
    assert not body_hits
    entity = json.loads((ROOT / 'packs/Fablecraft_BP/entities/guild_apprentice_skill.json').read_text())
    collider = entity['minecraft:entity']['components']['minecraft:collision_box']
    assert collider['width'] / 2 <= .35 and collider['height'] <= 1.9
    harnesses = {}
    for label, vox in (('before', before), ('after', after)):
        rays = gp.harness(vox, RAY)
        shape_hits = gp.ray_collisions(vox, rays)
        assert len(rays['rays']) == 5 and not any(shape_hits.values())
        arrival = gp.harness(vox, ARRIVAL, True)
        assert arrival['sampled_clear_corridor_points'] == 13
        assert len(arrival['prototype_negative_cases']) == 27
        harnesses[label] = {'actual_emitted_rays': rays, 'expanded_fence_ray_hits': shape_hits,
                            'shot': gp.harness(vox, SHOT), 'arrival': arrival}
    assert harnesses['before'] == harnesses['after']
    assert max(z + 1 for x, y, z in EDIT) == 34
    assert min(ray['target']['z'] for ray in harnesses['after']['actual_emitted_rays']['rays']) == 34.5
    tables = [(x, y, z) for x in range(after.sx) for y in range(after.sy) for z in range(after.sz)
              if gp.cell(after, x, y, z)[0] == 'minecraft:fletching_table']
    assert tables == [(91, 1, 40)]
    negatives = []
    for name, point, block, route in [
        ('missing_bridge_deck', (63, 1, 36), 'minecraft:air', 'bridge_36'),
        ('missing_bridge_approach', (59, 1, 36), 'minecraft:air', 'bridge_36'),
        ('bridge_headroom', (63, 3, 36), 'minecraft:stone', 'bridge_36'),
        ('blocked_arrival', (84, 1, 39), 'minecraft:spruce_fence', 'future_arrival'),
        ('blocked_board_bypass', (81, 1, 31), 'minecraft:purple_terracotta', 'board_approach'),
        ('closed_firing_gap', (83, 1, 38), 'minecraft:spruce_fence', 'firing_gap')]:
        broken = copy.deepcopy(after)
        gp.setcell(broken, point, block)
        try:
            checker.check_run(gp.LOCAL[route], broken)
        except AssertionError as error:
            negatives.append({'name': name, 'at': point, 'detected': True, 'reason': str(error)})
        else:
            raise AssertionError(name + ' failed to fail')
    fence = copy.deepcopy(after)
    gp.setcell(fence, (83, 1, 38), 'minecraft:spruce_fence')
    fence_hits = gp.ray_collisions(fence, harnesses['after']['actual_emitted_rays'])
    assert any(fence_hits.values())
    negatives.append({'name': 'lower_fence_ray_overhang', 'at': [83, 1, 38], 'detected': True,
                      'expanded_collision_hits': fence_hits,
                      'block_cell_harness_still_passes': gp.harness(fence, SHOT)})
    bay_hits = added_body_hits({(83, 1, 38)}, body_paths)
    assert bay_hits
    negatives.append({'name': 'expanded_body_bay_block', 'detected': True, 'hits': bay_hits})
    forward = copy.deepcopy(after)
    forward_cells = {(x, y, 35) for x, height in zip(range(89, 92), (3, 2, 3)) for y in range(1, height + 1)}
    for point in forward_cells:
        gp.setcell(forward, point, 'minecraft:light_blue_terracotta')
    _, _, forward_paths = gp.trace(forward, (10, 1., 42), gp.DESTINATIONS)
    forward_hits = added_body_hits(forward_cells, body_paths)
    assert forward_paths != apaths and forward_hits
    negatives.append({'name': 'forward_tower_overlaps_east_door_route', 'detected': True,
                      'all_destinations_still_reachable': True, 'exact_sequences_changed': True,
                      'hits': forward_hits})
    reference = json.loads((ROOT / 'screenshots/validation/GP21/reference-followup.json').read_text())['references'][0]
    assert reference['id'] == '141099874'
    assert reference['sha256'] == '6661646bf5aff6570803136b666571fa2f5f98c638b17b65510b719c7862f392'
    reference_file = ROOT / reference['path']
    if reference_file.exists():
        assert sha(reference_file.read_bytes()) == reference['sha256']
    report = {
        'baseline_commit': BASE, 'completed_utc': datetime.now(timezone.utc).isoformat(),
        'scope': 'Actual committed/current generator serialization and independent final-voxel comparison',
        'source_sha256': {'before': sha(old_source), 'after': sha(new_source)},
        'asset_sha256': {'before': sha(old_raw), 'after': sha(new_raw)},
        'owners_match_corresponding_shipped_assets': True, 'serialized_cells_compared': 395280,
        'actual_changes': changes, 'all_other_cells_exact': 395268,
        'all_prior_occupied_cells_and_all_floors_exact': True,
        'palette_states_entities_metadata_secondary_layers_origin_size_exact': True,
        'shared_rng_layout_and_anchors_exact': True, 'rng_instances': len(old_rng),
        'rng_calls_and_final_state_sha256': sha(json.dumps(old_rng).encode()),
        'layout_and_anchors': new.GUILD_LAYOUT, 'protected_maze_cells': 678,
        'maze_anchor': [46, 12, 70], 'all_campus_fletching_tables': tables,
        'baseline_walking_nodes': len(bn), 'current_walking_nodes': len(an),
        'baseline_gate_reachable_nodes': len(br), 'current_gate_reachable_nodes': len(ar),
        'only_removed_nodes': sorted(bn - an), 'only_removed_gate_reachable_nodes': sorted(br - ar),
        'new_walking_nodes': sorted(an - bn), 'new_reachable_nodes': sorted(ar - br),
        'baseline_gate_paths': bpaths, 'current_gate_paths': apaths,
        'seven_complete_gate_paths_exact': True, 'eight_local_routes_pass_both_directions': True,
        'protected_local_routes': gp.LOCAL, 'three_firing_gap_columns_clear': True,
        'expanded_body_review': {'radius': .35, 'height': 1.9, 'actual_entity_collider': collider,
                                 'paths': body_paths, 'added_collider_hits': body_hits},
        'harnesses': harnesses, 'negative_fixtures': negatives,
        'target_separation': 'All cutout blocks end at z34 or earlier; retained rays stop at z34.5.',
        'original_reference': {'id': reference['id'], 'page_url': reference['page_url'],
                               'image_url': reference['url'], 'sha256': reference['sha256'],
                               'local_pixels_checked_when_available': reference_file.exists()},
        'adaptation_limits': 'Coordinates, width, heights, depth, steps, chosen materials and dark full-cube painted slit are Minecraft adaptations, not measured TLC geometry.',
        'native_acceptance': 'unrun',
        'limits': 'No engine execution. Cardinal graph has a curated floor set and does not certify walking on decorative terracotta/wool tops. Added-body sweep checks only new full cubes against protected routes; preexisting routes use the retained slab/fence model. Fence ray sweep overestimates horizontal occupancy and extends fences/walls to y+1.5. Arrival prototype mocks 624 below-base cells as readable air; native search, offsets, events and saved-world contents remain uncalibrated.',
        'reviewed_source_sha256': reviewed_hashes,
    }
    if args.render:
        gp.OUT = OUT
        views = gp.render(before, 'before')
        gp.render(after, 'after')
        report['focused_views'] = views
        report['image_sha256'] = {f'{name}-{label}.png': sha((OUT / f'{name}-{label}.png').read_bytes())
                                  for name in views for label in ('before', 'after')}
        font = gp.ImageFont.truetype('DejaVuSans.ttf', 20)
        report['font'] = {'path': str(font.path), 'sha256': sha(Path(font.path).read_bytes())}
    assert reviewed_hashes == {p: sha((ROOT / p).read_bytes()) for p in inputs}, 'Reviewed inputs changed during run'
    (OUT / 'independent-summary.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({'passed': True, 'baseline': BASE, 'actual_changes': len(changes),
                      'other_cells_exact': 395268, 'nodes_before': len(bn), 'nodes_after': len(an),
                      'gate_paths_exact': 7, 'local_routes': 8, 'swept_body_paths': len(body_paths),
                      'actual_ray_offsets': 5, 'arrival_samples': 13, 'arrival_refusals': 27,
                      'maze_cells': 678, 'negative_fixtures': len(negatives), 'native': 'unrun'}))


if __name__ == '__main__':
    main()

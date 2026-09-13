#!/usr/bin/env python3
"""Read-only actual GP23/current Guild dining and resident-adjacent review."""
import argparse
import copy
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import subprocess

ROOT = next(p for p in Path(__file__).resolve().parents if (p / 'scripts/gen_structures.py').exists())
HERE = Path(__file__).resolve().parent
OUT = HERE
BASE = '4aed7cff4bdb6cecc706e2c4711067cab648d530'
SOURCE = 'scripts/gen_structures.py'
ASSET = 'packs/Fablecraft_BP/structures/fc/guild_hall.mcstructure'
spec = importlib.util.spec_from_file_location('gp23_geometry', ROOT / 'screenshots/validation/GP23/independent-review.py')
prior = importlib.util.module_from_spec(spec)
spec.loader.exec_module(prior)
prior.TEMP = ROOT / 'tmp/conformance/gp24-independent/owners'
gp = prior.gp
sha = lambda v: hashlib.sha256(v).hexdigest()
SEATS = {(x, 1, z) for x in (38, 42) for z in range(36, 48)}
REMOVED = {(x, 1, z) for x in (38, 42) for z in (37, 39, 41, 43, 45, 47)}
CARPETS = {(x, 1, z) for x in (38, 42) for z in (41, 43)}


def committed(path):
    return subprocess.check_output(['git', 'show', BASE + ':' + path], cwd=ROOT)


def body_span(name, states, y):
    if name == 'minecraft:air':
        return None
    if name.endswith('_carpet'):
        return y, y + 1 / 16
    return gp.interval(name, states, y)


def feet_at(vox, x, z):
    assert gp.supported(vox, x, 1., z), f'missing base floor {(x, z)}'
    return 1. + (1 / 16 if gp.cell(vox, x, 1, z)[0].endswith('_carpet') else 0)


def path_body_hits(vox, path, radius=.4, height=2.1):
    """Conservative full dining blocks; raise/translate/lower at each step."""
    solids = []
    for x in range(36, 46):
        for y in range(9):
            for z in range(33, 52):
                span = body_span(*gp.cell(vox, x, y, z), y)
                if span:
                    solids.append(((x, y, z), (x - radius, span[0] - height, z - radius),
                                   (x + 1 + radius, span[1], z + 1 + radius)))
    hits = []
    for direction, points in [('forward', path), ('reverse', list(reversed(path)))]:
        for first, last in zip(points, points[1:]):
            a, b = (first[0] + .5, first[1], first[2] + .5), (last[0] + .5, last[1], last[2] + .5)
            top = max(a[1], b[1])
            raised, translated = (a[0], top, a[2]), (b[0], top, b[2])
            for phase, start, end in [('raise', a, raised), ('translate', raised, translated), ('lower', translated, b)]:
                for cell, low, high in solids:
                    if prior.prior.segment_box(start, end, low, high):
                        hits.append({'direction': direction, 'phase': phase, 'segment': [first, last], 'cell': cell})
    return hits


def support_survey(vox, path, radius=.4):
    """Exact constant-footprint intervals along each straight new seat gap.

    This surveys all floor columns touched by the body's square bound, including
    both columns while it spans a carpet edge; it does not execute native steps.
    """
    assert len({p[2] for p in path}) == 1
    start, end = sorted((path[0][0] + .5, path[-1][0] + .5))
    z = path[0][2] + .5
    edges = {start, end}
    for boundary in range(math.floor(start - radius), math.ceil(end + radius) + 1):
        for x in (boundary - radius, boundary + radius):
            if start < x < end:
                edges.add(x)
    edges = sorted(edges)
    intervals = []
    for lo, hi in zip(edges, edges[1:]):
        centre = (lo + hi) / 2
        floors = []
        for x in range(math.floor(centre - radius), math.floor(centre + radius) + 1):
            for zz in range(math.floor(z - radius), math.floor(z + radius) + 1):
                assert gp.supported(vox, x, 1., zz), ('unsupported body footprint', x, zz)
                block = gp.cell(vox, x, 1, zz)[0]
                assert block == 'minecraft:air' or block.endswith('_carpet'), ('obstructed footprint', x, zz, block)
                floors.append({'x': x, 'z': zz, 'surface': 1. + (1 / 16 if block.endswith('_carpet') else 0)})
        intervals.append({'centre_x_interval': [lo, hi], 'footprint_floors': floors,
                          'clear_feet_height': max(p['surface'] for p in floors)})
    rises = [abs(a['clear_feet_height'] - b['clear_feet_height']) for a, b in zip(intervals, intervals[1:])]
    assert max(rises, default=0) <= 1 / 16
    return {'intervals': intervals, 'maximum_surface_step': max(rises, default=0),
            'unsupported_intervals': 0, 'native_step_dynamics': 'unrun'}


def dining_plan(vox, label):
    image = gp.Image.new('RGB', (780, 1110), (242, 237, 225))
    draw = gp.ImageDraw.Draw(image)
    font = gp.ImageFont.truetype('DejaVuSans.ttf', 16)
    draw.text((24, 18), 'Actual decoded dining furniture | ' + label, font=font, fill=(28, 28, 33))
    draw.text((24, 44), 'Schematic plan; wall openings read at y1. Furniture shapes simplified.', font=font, fill=(45, 45, 50))
    colors = {'minecraft:oak_stairs': (163, 113, 64), 'minecraft:oak_planks': (128, 82, 43),
              'minecraft:oak_fence': (112, 76, 40), 'minecraft:cake': (231, 212, 196),
              'minecraft:lantern': (249, 190, 65), 'minecraft:furnace': (103, 106, 105),
              'minecraft:smoker': (98, 92, 83), 'minecraft:barrel': (128, 92, 50), 'minecraft:cauldron': (81, 83, 83)}
    for z in range(33, 52):
        for x in range(36, 46):
            x0, y0 = 88 + (x - 36) * 57, 101 + (z - 33) * 46
            ground = (202, 191, 167)
            if gp.cell(vox, x, 1, z)[0] == 'minecraft:red_carpet':
                ground = (166, 61, 53)
            elif (x in (36, 45) or z in (33, 51)) and gp.cell(vox, x, 1, z)[0] != 'minecraft:air':
                ground = (111, 111, 103)
            draw.rectangle((x0, y0, x0 + 55, y0 + 44), fill=ground, outline=(148, 141, 123))
            for y in (1, 2, 3):
                name, _ = gp.cell(vox, x, y, z)
                if name in colors:
                    draw.rectangle((x0 + 7, y0 + 7, x0 + 48, y0 + 38), fill=colors[name])
                    text = {'minecraft:oak_stairs': 'seat', 'minecraft:oak_planks': 'table', 'minecraft:oak_fence': 'leg', 'minecraft:lantern': 'lamp'}.get(name, name.split(':')[1][:5])
                    draw.text((x0 + 8, y0 + 14), text, fill=(20, 20, 23))
            if (x, 1, z) in REMOVED and label == 'after':
                draw.text((x0 + 10, y0 + 14), 'gap', fill=(255, 238, 210) if (x, 1, z) in CARPETS else (35, 60, 37))
    for z in range(33, 52):
        draw.text((48, 112 + (z - 33) * 46), str(z), font=font, fill=(35, 35, 40))
    for x in range(36, 46):
        draw.text((106 + (x - 36) * 57, 76), str(x), font=font, fill=(35, 35, 40))
    draw.text((24, 999), 'Four vacated cells receive the existing red carpet runner; eight are air.', font=font, fill=(40, 40, 43))
    draw.text((24, 1027), 'Original stools are low and red-covered; these surviving oak stairs are adaptations.', font=gp.ImageFont.truetype('DejaVuSans.ttf', 15), fill=(40, 40, 43))
    draw.text((24, 1055), 'No native movement, lighting, sitting behavior or collision was executed.', font=font, fill=(40, 40, 43))
    image.save(OUT / f'dining-plan-{label}.png')


def main():
    global OUT
    parser = argparse.ArgumentParser()
    parser.add_argument('--render', action='store_true')
    parser.add_argument('--output', type=Path, default=HERE,
                        help='Evidence output directory; use ignored scratch when repeating a curated review.')
    args = parser.parse_args()
    OUT = args.output.resolve()
    OUT.mkdir(parents=True, exist_ok=True)
    tracked = [SOURCE, ASSET, 'scripts/fc_lib.py', 'scripts/tests/test_guild_routes.py', 'scripts/gen_screenshots.py',
               'packs/Fablecraft_BP/scripts/main.js', 'packs/Fablecraft_BP/scripts/guild_residents.js',
               'packs/Fablecraft_BP/scripts/guild_training.js', 'screenshots/validation/GP23/independent-review.py',
               'screenshots/validation/GP22/independent-review.py', 'screenshots/validation/GP21/independent-review.py',
               'screenshots/validation/GP20/independent-review.py', prior.RAY, prior.ARRIVAL, prior.SHOT,
               str(Path(__file__).relative_to(ROOT)), str((HERE / 'resident-probe.mjs').relative_to(ROOT))]
    hashes = {p: sha((ROOT / p).read_bytes()) for p in tracked}
    for path in ['scripts/fc_lib.py', 'packs/Fablecraft_BP/scripts/main.js', 'packs/Fablecraft_BP/scripts/guild_residents.js']:
        assert committed(path).replace(b'\r\n', b'\n') == (ROOT / path).read_bytes().replace(b'\r\n', b'\n')
    old_source, new_source = committed(SOURCE), (ROOT / SOURCE).read_bytes()
    old, old_raw, old_nbt, old_rng = prior.generate(old_source, 'before')
    new, new_raw, new_nbt, new_rng = prior.generate(new_source, 'after')
    assert old_raw == committed(ASSET) and new_raw == (ROOT / ASSET).read_bytes()
    assert old.GUILD_LAYOUT == new.GUILD_LAYOUT and old_rng == new_rng
    for key in old_nbt:
        if key != 'structure':
            assert old_nbt[key] == new_nbt[key]
    for key in old_nbt['structure']:
        if key != 'block_indices':
            assert old_nbt['structure'][key] == new_nbt['structure'][key]
    assert old_nbt['structure']['block_indices'][1:] == new_nbt['structure']['block_indices'][1:]
    before, after = gp.reader.voxel(old_nbt), gp.reader.voxel(new_nbt)
    changes = gp.changed(before, after)
    assert len(before.grid) == len(after.grid) == 395280
    assert {tuple(c['at']) for c in changes} == REMOVED and len(changes) == 12
    for c in changes:
        assert c['before'] == ('minecraft:oak_stairs', {'weirdo_direction': 1 if c['at'][0] == 38 else 0, 'upside_down_bit': 0})
        assert c['after'] == ('minecraft:red_carpet' if tuple(c['at']) in CARPETS else 'minecraft:air', {})
    for p in SEATS - REMOVED:
        assert gp.cell(before, *p) == gp.cell(after, *p)
    protected = json.loads((ROOT / 'screenshots/validation/GP17/maze-study-final-voxel-survey.json').read_text())['protected_cells']
    for cell in protected:
        assert gp.cell(before, *cell['at']) == gp.cell(after, *cell['at']) == (cell['name'], cell['states'])
    assert len(protected) == 678
    bn, br, bpaths = gp.trace(before, (10, 1., 42), gp.DESTINATIONS)
    an, ar, apaths = gp.trace(after, (10, 1., 42), gp.DESTINATIONS)
    assert bn <= an and br <= ar
    assert an - bn == ar - br == {(x, float(y), z) for x, y, z in REMOVED}
    checker = gp.GuildRoutes()
    dining = {f'aisle_x{x}': [(x, 1., z) for z in range(35, 50)] for x in (37, 39, 41, 43)}
    dining.update({f'end_z{z}': [(x, 1., z) for x in range(37, 45)] for z in (35, 49)})
    for vox in (before, after):
        for path in list(gp.LOCAL.values()) + list(bpaths.values()) + list(dining.values()):
            checker.check_run(path, vox)
    dining_body = {}
    for label, vox in [('before', before), ('after', after)]:
        dining_body[label] = {}
        for name, path in dining.items():
            physical = [(x, feet_at(vox, x, z), z) for x, _, z in path]
            hits = path_body_hits(vox, physical)
            assert not hits, (label, name, hits[:3])
            dining_body[label][name] = physical
    gaps, baseline_gap_hits, support = {}, {}, {}
    for x, _, z in sorted(REMOVED):
        name = f'gap_{x}_{z}'
        path = [(xx, feet_at(after, xx, z), z) for xx in (x - 1, x, x + 1)]
        assert not path_body_hits(after, path), name
        baseline_gap_hits[name] = path_body_hits(before, path)
        assert baseline_gap_hits[name], name
        gaps[name] = path
        support[name] = support_survey(after, path)
    payload = {label: {'size': [vox.sx, vox.sy, vox.sz], 'palette': vox.palette, 'grid': vox.grid} for label, vox in [('before', before), ('after', after)]}
    run = subprocess.run(['node', '--experimental-vm-modules', str(HERE / 'resident-probe.mjs')], cwd=ROOT, input=json.dumps(payload), text=True, capture_output=True)
    (OUT / 'resident-probe.log').write_text(run.stdout + run.stderr)
    assert run.returncode == 0, run.stderr
    residents = json.loads(run.stdout)
    colliders = {}
    for slot in residents['slotHomes']:
        path = 'packs/Fablecraft_BP/entities/' + slot['type'].split(':')[1] + '.json'
        collider = json.loads((ROOT / path).read_text())['minecraft:entity']['components']['minecraft:collision_box']
        assert collider['width'] / 2 <= .4 and collider['height'] <= 2.1
        colliders[path] = {'sha256': sha((ROOT / path).read_bytes()), 'collision_box': collider}
    harnesses = {}
    for label, vox in [('before', before), ('after', after)]:
        rays = gp.harness(vox, prior.RAY)
        assert not any(gp.ray_collisions(vox, rays).values())
        harnesses[label] = {'rays': rays, 'shot': gp.harness(vox, prior.SHOT), 'arrival': gp.harness(vox, prior.ARRIVAL, True)}
    assert harnesses['before'] == harnesses['after']
    negatives = []
    for name, at, material in [('restored_seat_blocks_new_gap', (38, 1, 37), 'minecraft:oak_stairs'),
                               ('low_headroom_blocks_tall_resident', (38, 3, 37), 'minecraft:stone'),
                               ('continuous_row_blocks_carpet_gap', (42, 1, 41), 'minecraft:oak_stairs')]:
        broken = copy.deepcopy(after)
        gp.setcell(broken, at, material)
        path = gaps[f'gap_{at[0]}_{at[2]}']
        hits = path_body_hits(broken, path)
        assert hits
        negatives.append({'name': name, 'at': at, 'detected': True, 'body_hits': hits})
    broken = copy.deepcopy(after)
    gp.setcell(broken, (38, 0, 37), 'minecraft:air')
    try:
        feet_at(broken, 38, 37)
    except AssertionError as error:
        negatives.append({'name': 'missing_new_gap_floor', 'detected': True, 'reason': str(error)})
    else:
        raise AssertionError('missing floor not detected')
    refs = json.loads((HERE / 'reference-reinspection.json').read_text())
    reference_availability = {}
    for ref in refs['references']:
        path = ROOT / f"tmp/conformance/next-guild-reference/reference-{ref['id']}.jpg"
        present = path.exists()
        if present:
            assert sha(path.read_bytes()) == ref['sha256']
        reference_availability[ref['id']] = {'pixels_present': present, 'hash_checked_this_run': present,
                                             'visual_inspection_this_run': False,
                                             'meaning': 'Retained reference provenance and earlier visual observations remain; this script only verifies pixels when locally available.'}
    report = {'baseline_commit': BASE, 'source_sha256': {'before': sha(old_source), 'after': sha(new_source)},
              'asset_sha256': {'before': sha(old_raw), 'after': sha(new_raw)}, 'actual_generators_match_shipped_assets': True,
              'serialized_cells_compared': 395280, 'changes': changes, 'all_other_cells_exact': 395268,
              'retained_seats': sorted(SEATS - REMOVED), 'new_air_cells': sorted(REMOVED - CARPETS), 'new_carpet_cells': sorted(CARPETS),
              'all_nonseat_fixtures_palette_states_metadata_and_layers_exact': True, 'RNG_and_layout_exact': True,
              'rng_state_sha256': sha(json.dumps(old_rng).encode()), 'layout': new.GUILD_LAYOUT, 'maze_reservations': len(protected),
              'walking_nodes': {'before': len(bn), 'after': len(an)}, 'reachable_nodes': {'before': len(br), 'after': len(ar)},
              'all_prior_nodes_and_reached_nodes_preserved': True, 'new_nodes': sorted(an - bn), 'new_reachable_nodes': sorted(ar - br),
              'retained_seven_complete_paths_still_pass': True, 'new_selected_paths_equal_previous': bpaths == apaths,
              'before_gate_paths': bpaths, 'after_gate_paths': apaths, 'existing_local_routes_pass': 8, 'dining_routes_pass': dining,
              'body': {'radius': .4, 'height': 2.1, 'carpet_height': 1 / 16, 'transition_model': 'raise then translate then lower, both directions',
                       'dining_aisles': dining_body, 'new_gap_paths': gaps, 'new_gap_floor_support': support,
                       'all_after_body_hits_empty': True, 'baseline_gap_obstructions': baseline_gap_hits},
              'actual_resident_helper': residents, 'resident_colliders': colliders, 'retained_skill_harnesses': harnesses,
              'negatives': negatives, 'references': refs, 'reference_availability_this_run': reference_availability,
              'native_acceptance': 'unrun',
              'limits': 'Graph treats carpets as passable at floor y1; independent full-body gap/aisle sweeps instead use 1/16 carpet height. Stair seats are conservative full cubes. Model certifies only these paths and bounds, not native actor navigation, seating, lighting or carpet/stair dynamics. Separate stools are source-supported; count, spacing, oak-stair shape and exact geometry remain adaptations. Resident-query fixture is controlled and does not spawn or move actors.',
              'reviewed_inputs': hashes}
    if args.render:
        for label, vox in [('before', before), ('after', after)]:
            dining_plan(vox, label)
        report['image_sha256'] = {f'dining-plan-{label}.png': sha((OUT / f'dining-plan-{label}.png').read_bytes()) for label in ('before', 'after')}
    assert hashes == {p: sha((ROOT / p).read_bytes()) for p in tracked}, 'reviewed input changed during run'
    (OUT / 'review.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({'passed': True, 'changes': len(changes), 'new_air': 8, 'new_carpet': 4, 'other_cells_exact': 395268,
                      'walking': report['walking_nodes'], 'reachable': report['reachable_nodes'],
                      'old_gate_paths_preserved': True, 'selected_paths_exact': bpaths == apaths,
                      'existing_local_routes': 8, 'dining_aisles': 6, 'new_body_gap_paths': 12,
                      'resident_defaults_exact': residents['defaultSpawnPointsExact'], 'resident_future_choices_gained': len(residents['gainedFutureBirthCandidates']),
                      'negatives': len(negatives), 'native': 'unrun'}))


if __name__ == '__main__':
    main()

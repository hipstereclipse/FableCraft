#!/usr/bin/env python3
"""Independent GP18 comparison of decoded complete owner-generated structures.

Writes temporary serialized structures only under ignored tmp. Never edits packs.
The predecessor is actual committed generator source, not a disabled new helper.
"""
import argparse
import contextlib
import hashlib
import io
import json
from pathlib import Path
import struct
import subprocess
import sys
import types

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT / 'scripts'), str(ROOT / 'scripts/tests')]
from test_guild_routes import GuildRoutes, cell, clear, reachable, supported, walking_graph


def digest(data):
    return hashlib.sha256(data).hexdigest()


def decode_nbt(data):
    """Read emitted Bedrock little-endian NBT independently of the writer."""
    stream = io.BytesIO(data)

    def scalar(fmt):
        return struct.unpack('<' + fmt, stream.read(struct.calcsize('<' + fmt)))[0]

    def string():
        return stream.read(scalar('H')).decode('utf8')

    def value(tag):
        if tag in (1, 2, 3, 4, 5, 6):
            return scalar({1: 'b', 2: 'h', 3: 'i', 4: 'q', 5: 'f', 6: 'd'}[tag])
        if tag == 7:
            return list(stream.read(scalar('i')))
        if tag == 8:
            return string()
        if tag == 9:
            kind, count = scalar('B'), scalar('i')
            return [value(kind) for _ in range(count)]
        if tag == 10:
            result = {}
            while (kind := scalar('B')) != 0:
                name = string()
                result[name] = value(kind)
            return result
        if tag in (11, 12):
            return [scalar('i' if tag == 11 else 'q') for _ in range(scalar('i'))]
        raise AssertionError(f'Unexpected NBT tag {tag}')

    assert scalar('B') == 10
    string()
    result = value(10)
    assert stream.tell() == len(data), 'Trailing unparsed bytes'
    return result


def voxel(nbt):
    sx, sy, sz = nbt['size']
    palette = [(b['name'], b['states']) for b in nbt['structure']['palette']['default']['block_palette']]
    grid = nbt['structure']['block_indices'][0]
    assert len(grid) == sx * sy * sz
    return types.SimpleNamespace(sx=sx, sy=sy, sz=sz, palette=palette, grid=grid,
                                 idx=lambda x, y, z: x * sy * sz + y * sz + z)


def generate(source, label):
    module = types.ModuleType('review_' + label)
    module.__file__ = str(ROOT / 'scripts/gen_structures.py')
    exec(compile(source, module.__file__, 'exec'), module.__dict__)
    module.BP = ROOT / 'tmp/conformance/gp18/independent-review' / label
    observed = []
    original_rng = module.rng

    def observed_rng(*args):
        generator = original_rng(*args)
        observed.append((args, generator))
        return generator

    module.rng = observed_rng
    with contextlib.redirect_stdout(io.StringIO()):
        module.guild_hall()
    data = (module.BP / 'structures/fc/guild_hall.mcstructure').read_bytes()
    rng_states = [(args, repr(generator.getstate())) for args, generator in observed]
    return module, data, decode_nbt(data), rng_states


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--baseline', default='732670a83bcd7909858ca4480c31f5dc8aeeb8ad')
    parser.add_argument('--require-shipped-match', action='store_true')
    args = parser.parse_args()
    before_source = subprocess.check_output(['git', 'show', args.baseline + ':scripts/gen_structures.py'], cwd=ROOT)
    after_source = (ROOT / 'scripts/gen_structures.py').read_bytes()
    baseline, old_data, old_nbt, old_rng = generate(before_source, 'before')
    current, new_data, new_nbt, new_rng = generate(after_source, 'after')
    before, after = voxel(old_nbt), voxel(new_nbt)
    assert baseline.GUILD_LAYOUT == current.GUILD_LAYOUT, 'Changed layout/anchors'
    assert old_rng == new_rng, 'Changed seeded RNG calls or final state'
    assert old_nbt['size'] == new_nbt['size'] == [122, 30, 108]
    for key in ('format_version', 'structure_world_origin'):
        assert old_nbt[key] == new_nbt[key]
    for key in ('entities',):
        assert old_nbt['structure'][key] == new_nbt['structure'][key]
    assert old_nbt['structure']['block_indices'][1] == new_nbt['structure']['block_indices'][1]
    assert old_nbt['structure']['palette'] == new_nbt['structure']['palette'], 'Changed palette/state/version or block metadata'
    expected = {(45, 12, 71): 'minecraft:red_carpet', (45, 12, 73): 'minecraft:red_carpet', (47, 12, 73): 'minecraft:red_carpet'}
    expected.update({(x, y, 75): 'minecraft:dark_oak_planks' if y in (12, 15) else 'minecraft:bookshelf'
                     for x in (43, 44) for y in range(12, 16)})
    changes = []
    for index, (old, new) in enumerate(zip(before.grid, after.grid)):
        if before.palette[old] != after.palette[new]:
            x, yz = divmod(index, after.sy * after.sz)
            y, z = divmod(yz, after.sz)
            point = (x, y, z)
            assert point in expected, f'Unauthorized full-campus delta {point}'
            assert after.palette[new] == (expected[point], {})
            assert before.palette[old] == ('minecraft:blue_carpet' if y == 12 and z != 75 else 'minecraft:air', {})
            changes.append({'at': point, 'before': before.palette[old], 'after': after.palette[new]})
    assert {tuple(c['at']) for c in changes} == set(expected)
    survey = json.loads((ROOT / 'screenshots/validation/GP17/maze-study-final-voxel-survey.json').read_text())
    assert len(survey['protected_cells']) == 678
    for item in survey['protected_cells']:
        assert cell(before, *item['at']) == cell(after, *item['at']) == (item['name'], item['states']), item['at']
    windows = [(x, y, z) for x in range(39, 54) for y in range(11, 18) for z in range(65, 80)
               if cell(before, x, y, z)[0] == 'minecraft:glass_pane']
    assert len(windows) == 35
    assert all(cell(before, *p) == cell(after, *p) for p in windows)
    for x in (43, 44):
        assert cell(after, x, 11, 75) == ('minecraft:dark_oak_planks', {})
        assert clear(after, x, 12, 74) and supported(after, x, 12, 74), 'Blocked case front'
    tower = GuildRoutes()
    tower.check_run(tower.tower_run(), after)
    for route in survey['study_connector_routes'].values():
        tower.check_run(route, after)
    old_nodes, new_nodes = walking_graph(before), walking_graph(after)
    old_reach, new_reach = reachable(before, old_nodes, (46, 12., 70)), reachable(after, new_nodes, (46, 12., 70))
    assert old_reach - new_reach == {(43, 12., 75), (44, 12., 75)}
    assert not (new_reach - old_reach)
    for target in [(10, 1., 42), (46, 1., 70), (44, 7., 72)]:
        assert target in new_reach, target
        assert (46, 12., 70) in reachable(after, new_nodes, target), target
    shipped = (ROOT / 'packs/Fablecraft_BP/structures/fc/guild_hall.mcstructure').read_bytes()
    if args.require_shipped_match:
        assert shipped == new_data, 'Shipped generated structure differs from reviewed owner output'
    print(json.dumps({
        'baseline_commit': args.baseline,
        'source_sha256': {'before': digest(before_source), 'after': digest(after_source)},
        'serialized_sha256': {'before': digest(old_data), 'after': digest(new_data), 'shipped': digest(shipped)},
        'shipped_matches_current_owner': shipped == new_data,
        'decoded_compared_cells': len(before.grid), 'exact_changes': changes,
        'protected_exact_cells': len(survey['protected_cells']), 'unchanged_window_glass_cells': len(windows),
        'layout_and_all_anchors_unchanged': True, 'serialized_palette_secondary_layer_entities_origin_unchanged': True,
        'seeded_rng_calls_and_final_state_unchanged': True,
        'rng_instances_observed': len(old_rng), 'complete_tower_and_study_connector_routes_both_directions': 'pass',
        'only_removed_reachable_nodes': sorted(old_reach - new_reach),
        'reference_images': [{'path': item['local_path'], 'sha256': digest((ROOT / item['local_path']).read_bytes())} for item in survey['known_reference_images']],
        'native_acceptance': 'unrun',
    }, indent=2))


if __name__ == '__main__':
    main()

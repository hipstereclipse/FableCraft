"""Validate generated structures, explicit runtime tables and current render provenance."""
import argparse
import ast
import contextlib
import hashlib
import io
import json
from pathlib import Path
import subprocess
import tempfile
from unittest.mock import patch

from fc_lib import ROOT
import gen_structures as GS

MANIFEST = ROOT / 'scripts/structure_manifest.json'
EVIDENCE = Path('screenshots/structures/contract/evidence.json')


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def runtime_tables(root):
    result = subprocess.run(['node', str(ROOT / 'scripts/structure_tables.cjs'),
                             str(root / 'packs/Fablecraft_BP/scripts/main.js')],
                            text=True, capture_output=True, check=True)
    return json.loads(result.stdout)


def builders():
    # Only direct calls from generator main() are supported; additions cannot hide
    # behind regex matches in comments, dead code or helper function definitions.
    tree = ast.parse((ROOT / 'scripts/gen_structures.py').read_text())
    main = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'main')
    result = []
    for statement in main.body:
        if not isinstance(statement, ast.Expr) or not isinstance(statement.value, ast.Call):
            raise ValueError('Unsupported generator main statement')
        call = statement.value
        if not isinstance(call.func, ast.Name):
            raise ValueError('Unsupported generator call')
        if call.func.id == 'print':
            continue
        if call.args or call.keywords:
            raise ValueError('Generator must use explicit no-argument builders')
        result.append(call.func.id)
    if len(set(result)) != len(result):
        raise ValueError('Duplicate generator call')
    return result


def capture():
    """Run owners into a temporary tree; never mutate shipped packs."""
    records, voxels = {}, {}
    original = GS.Vox.save
    with tempfile.TemporaryDirectory() as directory:
        base = Path(directory)
        current = None
        def save(vox, name):
            if name in records:
                raise ValueError(f'Duplicate generated structure: {name}')
            original(vox, name)
            path = base / 'structures/fc' / (name + '.mcstructure')
            records[name] = {'generator': current, 'size': [vox.sx, vox.sy, vox.sz], 'sha256': digest(path)}
            voxels[name] = vox
        with patch.object(GS, 'BP', base), patch.object(GS.Vox, 'save', save), contextlib.redirect_stdout(io.StringIO()):
            for current in builders():
                getattr(GS, current)()
    return records, voxels


def anchor_errors(actual):
    layout = GS.GUILD_LAYOUT
    def xz(key):
        x, z = layout[key][:2]
        return {'x': x, 'z': z}
    expected = {
        'sx': layout['size'][0], 'sz': layout['size'][2],
        **{key: xz(key) for key in ('wake', 'skill', 'cullis', 'quest', 'archery', 'dueling')},
        'questTables': [{'x': x, 'z': z} for x, z in layout['quest_tables']],
        'maze': {**xz('maze_spawn'), 'studyY': layout['maze_study_y']},
        'demon': {**xz('demon_door'), 'approachZ': layout['demon_door'][1] - 8},
        'cave': dict(zip(('sx', 'sz', 'x0', 'x1', 'z0', 'z1'), (*layout['cave_shaft'], *layout['cave_exclusion']))),
        'exitC': {'z': layout['exit_c_z']},
        'training': {
            'ringA': {'x': layout['dueling'][0] - 1.5, 'z': layout['dueling'][1] + .5},
            'ringB': {'x': layout['dueling'][0] + 1.5, 'z': layout['dueling'][1] + .5},
            'range': {'x': layout['archery'][0] - 2.5, 'z': layout['archery'][1] + .5},
            'target': {'x': layout['archery'][0] - 2.5, 'z': layout['archery'][1] - 4.5},
        },
    }
    return [f'Guild anchor mismatch: {key}' for key in sorted(expected.keys() | actual.keys())
            if expected.get(key) != actual.get(key)]


def interaction_errors(vox, actual):
    """Check selected interaction blocks and NPC/player standing columns separately."""
    errors = []
    def block(x, y, z):
        if not (0 <= x < vox.sx and 0 <= y < vox.sy and 0 <= z < vox.sz): return None
        return vox.palette[vox.grid[vox.idx(x, y, z)]][0]
    for key in ('skill', 'cullis'):
        point = actual[key]
        if block(point['x'], 0, point['z']) != 'minecraft:sea_lantern':
            errors.append(f'Guild interaction block mismatch: {key}')
    for i, point in enumerate(actual['questTables']):
        if block(point['x'], 1, point['z']) != 'minecraft:lectern':
            errors.append(f'Guild interaction block mismatch: questTables[{i}]')
    for key in ('wake', 'skill', 'cullis', 'maze', 'demon', 'archery', 'dueling'):
        point = actual[key]; x, z, y = point['x'], point['z'], point.get('studyY', 1)
        if (block(x, y - 1, z) in (None, 'minecraft:air', 'minecraft:water', 'minecraft:lava')
                or any(block(x, yy, z) != 'minecraft:air' for yy in (y, y + 1))):
            errors.append(f'Guild standing clearance mismatch: {key}')
    return errors


def check(root=ROOT, evidence_root=ROOT, manifest=None, generated=None, tables=None, voxels=None):
    manifest = json.loads(MANIFEST.read_text()) if manifest is None else manifest
    if generated is None or voxels is None:
        fresh, voxels = capture()
        generated = fresh if generated is None else generated
    tables = runtime_tables(root) if tables is None else tables
    errors = []
    if manifest.get('version') != 1: errors.append('Unsupported structure manifest version')
    entries = manifest['structures']
    names = [entry['name'] for entry in entries]
    if len(names) != len(set(names)):
        errors.append('Duplicate manifest structure')
    expected = set(names)
    def edges(label, actual, wanted=expected):
        for name in sorted(set(actual) - wanted): errors.append(f'Orphan {label}: {name}')
        for name in sorted(wanted - set(actual)): errors.append(f'Missing {label}: {name}')
    edges('generator output', generated)
    assets = {p.stem: p for p in (root / 'packs/Fablecraft_BP/structures/fc').glob('*.mcstructure')}
    edges('structure asset', assets)
    scatter = {s['id'].removeprefix('fc:'): s for s in tables['STRUCTS']}
    if len(scatter) != len(tables['STRUCTS']): errors.append('Duplicate runtime scatter ID')
    edges('scatter registration', scatter, {e['name'] for e in entries if e['kind'] == 'scatter'})
    edges('fixed registration', {s.removeprefix('fc:') for s in tables['fixed']}, {e['name'] for e in entries if e['kind'] == 'fixed'})
    for name in tables['CHEST_LOOT']:
        if name.removeprefix('fc:') not in expected: errors.append(f'Orphan loot reference: {name}')
    proof_path = evidence_root / EVIDENCE
    proof = json.loads(proof_path.read_text()) if proof_path.exists() else {}
    images = proof.get('structures', {})
    edges('render evidence', images)
    image_dir = evidence_root / EVIDENCE.parent
    edges('render file', {p.stem for p in image_dir.glob('*.png')})
    audit_path = image_dir / 'AUDIT.md'
    audit = audit_path.read_text() if audit_path.exists() else ''
    audit_ids = [line.split('|')[1].strip() for line in audit.splitlines()
                 if line.startswith('| ') and not line.startswith(('| ID |', '| --- |'))]
    edges('audit row', audit_ids)
    if len(audit_ids) != len(set(audit_ids)): errors.append('Duplicate audit row')
    for entry in entries:
        name = entry['name']; gen = generated.get(name); asset = assets.get(name)
        if entry['kind'] not in ('scatter', 'fixed', 'legacy'): errors.append(f'Unknown placement kind: {name}')
        if entry['kind'] == 'legacy' and not entry.get('reason'): errors.append(f'Undocumented legacy output: {name}')
        if gen:
            if gen['generator'] != entry['generator']: errors.append(f'Generator owner mismatch: {name}')
            if gen['size'] != entry['size']: errors.append(f'Manifest size mismatch: {name}')
            if asset and digest(asset) != gen['sha256']: errors.append(f'Stale generated asset: {name}')
        if name in scatter:
            runtime_size = [scatter[name].get(key) for key in ('w', 'h', 'd')]
            if entry['size'] != runtime_size: errors.append(f'Runtime footprint mismatch: {name}')
        image = image_dir / (name + '.png'); record = images.get(name, {})
        if gen and (record.get('asset_sha256') != gen['sha256'] or record.get('size') != gen['size']):
            errors.append(f'Stale render source: {name}')
        if image.exists() and record.get('image_sha256') != digest(image): errors.append(f'Stale render image: {name}')
        if record.get('grade') not in ('S', 'A', 'B', 'C', 'D'): errors.append(f'Missing render grade: {name}')
        row = f"| {name} | {record.get('grade')} | {record.get('score')} |"
        if row not in audit: errors.append(f'Missing audit row: {name}')
    errors.extend(anchor_errors(tables['GUILD']))
    if 'guild_hall' in voxels:
        errors.extend(interaction_errors(voxels['guild_hall'], tables['GUILD']))
    else:
        errors.append('Missing Guild interaction voxel proof')
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    errors = check(args.root)
    report = {'passed': not errors, 'errors': errors, 'scope': 'Asset/runtime/render provenance and numeric anchor coupling; in-world checks remain manual.'}
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, indent=2) + '\n')
    print(f'Structure contract: {len(errors)} errors')
    for error in errors: print('  ' + error)
    return bool(errors)


if __name__ == '__main__':
    raise SystemExit(main())

"""L2 isolated display generation; release packaging remains blocked by L3/L4.

Original-mode previews deliberately retain save IDs and unported runtime text.
Only the named emitters own changes to generated data. Live source packs are read-only.
"""
import json
from pathlib import Path
import shutil
import tempfile
from unittest.mock import patch

import fc_data
from fc_lib import write_json
from fc_strings import branding, emit_runtime, faithful_matches, text
import gen_behavior
import gen_resources


def emit_display_files(root, selected):
    """Generate through the owners, restoring their target paths even on failure."""
    bp, rp = root / 'packs/Fablecraft_BP', root / 'packs/Fablecraft_RP'
    with branding(selected), patch.object(gen_behavior, 'BP', bp), patch.object(gen_resources, 'RP', rp):
        items = fc_data.all_items()
        for item in items:
            cat = item['cat']
            emitter = (gen_behavior.emit_weapon if cat in ('melee', 'ranged') else
                       gen_behavior.emit_armor if cat == 'armor' else
                       gen_behavior.emit_consumable if cat == 'consumable' else
                       gen_behavior.emit_simple)
            emitter(item)
        gen_behavior.emit_script_data()
        gen_resources.emit_lang(items)
        emit_runtime(bp)
        # These manifests are source templates. This helper owns staged display fields;
        # UUIDs, versions, dependency edges and script entry points remain unchanged.
        for pack in (bp, rp):
            path = pack / 'manifest.json'
            manifest = json.loads(path.read_text(encoding='utf-8'))
            for key in ('name', 'description'):
                manifest['header'][key] = text(manifest['header'][key])
            manifest['metadata']['authors'] = [text(author) for author in manifest['metadata']['authors']]
            # Legal attribution is not a display name. Never translate it into a false
            # assertion that the provisional original names belong to another company.
            if selected == 'original':
                manifest['metadata']['license'] = 'Apache-2.0; see LICENSE and LEGAL.md in the source repository.'
            write_json(path, manifest)


def stage_packs(source_root, selected, build_parent=None):
    """Copy both packs to a fresh local tree, then regenerate only display-bearing files."""
    # Validate before creating any files.
    with branding(selected):
        pass
    parent = Path(build_parent) if build_parent is not None else source_root / 'tmp/builds'
    parent.mkdir(parents=True, exist_ok=True)
    root = Path(tempfile.mkdtemp(prefix=f'{selected}-', dir=parent))
    for label in ('Fablecraft_BP', 'Fablecraft_RP'):
        shutil.copytree(source_root / 'packs' / label, root / 'packs' / label)
    emit_display_files(root, selected)
    write_json(root / 'build-info.json', {
        'branding': selected, 'distribution_ready': False,
        'original_title': 'provisional; no final public name selected',
        'policy': 'Local development only. L3 runtime migration and L4 release scan pending.',
    })
    return root


def write_debt_report(root):
    """Inventory known display spellings by file/line; NOT the L4 release scanner."""
    files = {}
    for path in sorted((root / 'packs').rglob('*')):
        if not path.is_file() or path.suffix not in ('.js', '.json', '.lang'):
            continue
        entries = []
        for number, line in enumerate(path.read_text(encoding='utf-8').splitlines(), 1):
            names = faithful_matches(line)
            if names:
                entries.append({'line': number, 'names': names})
        if entries:
            files[path.relative_to(root).as_posix()] = entries
    report = {
        'scope': 'Known case-sensitive display names in JS/JSON/lang; includes comments. Not a release scan.',
        'limitations': 'L4 must also inspect case, escapes, filenames, IDs, metadata, binary text and nested archives.',
        'file_count': len(files), 'files': files,
    }
    write_json(root / 'branding-debt.json', report)
    return report

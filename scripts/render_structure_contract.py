"""Regenerate only the 29 structure contract renders and their provenance/audit."""
import json
from pathlib import Path

from fc_lib import ROOT
import gen_screenshots as render
from structure_contract import capture, digest, MANIFEST, EVIDENCE


def main():
    entries = json.loads(MANIFEST.read_text())['structures']
    generated, voxels = capture()
    output = ROOT / EVIDENCE.parent
    output.mkdir(parents=True, exist_ok=True)
    evidence = {'scope': 'Offline generator renders; grades measure image appearance, not canon or playability.', 'structures': {}}
    rows = ['# Current structure render audit', '', evidence['scope'], '',
            '| ID | Grade | Score | Footprint (x/y/z) | Image |', '| --- | --- | --- | --- | --- |']
    for entry in entries:
        name = entry['name']; gen = generated[name]
        image = render.render_structure(voxels[name], size=(700, 560))
        path = output / (name + '.png')
        image.save(path)
        metrics = render.audit_image(image)
        grade, score, notes = render.grade(metrics, 'mob')
        evidence['structures'][name] = {'asset_sha256': gen['sha256'], 'size': gen['size'],
            'image_sha256': digest(path), 'grade': grade, 'score': score, 'metrics': metrics, 'notes': notes}
        rows.append(f'| {name} | {grade} | {score} | {"/".join(map(str, gen["size"]))} | [{entry["title"]}]({name}.png) |')
        print(name, gen['size'], grade, score, flush=True)
    (output / 'AUDIT.md').write_text('\n'.join(rows) + '\n')
    (ROOT / EVIDENCE).write_text(json.dumps(evidence, indent=2) + '\n')


if __name__ == '__main__':
    main()

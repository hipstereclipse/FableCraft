"""Compare actual baseline emission, run regressions, then emit only Skill JSON."""
from pathlib import Path
import hashlib
import importlib.util
import json
import subprocess
import sys
import tempfile
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "scripts"))
from fc_mobs import MOBS

BASE = "c83246751b86aa489897efa3d0cadd49f303c588"
SOURCE = "scripts/gen_behavior.py"
TARGET = "packs/Fablecraft_BP/entities/guild_apprentice_skill.json"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def pack_hashes():
    return {str(p.relative_to(ROOT)): digest(p) for p in (ROOT / "packs").rglob("*") if p.is_file()}


commands = []
for test, log in (("scripts/tests/test_gen_behavior.py", "pre-regeneration-behavior.log"),
                  ("scripts/tests/test_guild_activity_behavior.py", "native-activity-tests.log")):
    result = subprocess.run([sys.executable, test], cwd=ROOT, capture_output=True, text=True)
    (OUT / log).write_text(result.stdout + result.stderr)
    commands.append({"command": [sys.executable, test], "exit_code": result.returncode,
                     "log": log, "timing": "Before targeted Skill regeneration"})
    assert result.returncode == 0, log

with tempfile.TemporaryDirectory(prefix="gp19-behavior-compare-") as directory:
    scratch = Path(directory)
    baseline_source = scratch / "baseline.py"
    baseline_source.write_bytes(subprocess.check_output(["git", "show", f"{BASE}:{SOURCE}"], cwd=ROOT))
    old = load(baseline_source, "gp19_baseline_behavior")
    current = load(ROOT / SOURCE, "gp19_current_behavior")
    all_outputs = []
    for label, module in (("before", old), ("after", current)):
        dest = scratch / label
        with patch.object(module, "BP", dest):
            for mob in MOBS:
                module.emit_entity(mob)
        all_outputs.append({str(p.relative_to(dest)): json.loads(p.read_text()) for p in dest.rglob("*.json")})
    assert all_outputs[0].keys() == all_outputs[1].keys()
    changed = [name for name in all_outputs[0] if all_outputs[0][name] != all_outputs[1][name]]
    assert changed == ["entities/guild_apprentice_skill.json"], changed
    scope = {"baseline_commit": BASE, "baseline_source_sha256": digest(baseline_source),
             "current_source_sha256": digest(ROOT / SOURCE), "emitted_entity_count": len(all_outputs[0]),
             "semantically_changed_entities": changed}

    before = pack_hashes()
    current.emit_entity(next(mob for mob in MOBS if mob["id"] == "guild_apprentice_skill"))
    after = pack_hashes()
    changed_pack = [{"path": name, "before_sha256": before.get(name), "after_sha256": after.get(name)}
                    for name in sorted(before.keys() | after.keys()) if before.get(name) != after.get(name)]
    assert [entry["path"] for entry in changed_pack] == [TARGET], changed_pack
    assert json.loads((ROOT / TARGET).read_text()) == all_outputs[1]["entities/guild_apprentice_skill.json"]
    scope.update({"command": [sys.executable, str(Path(__file__).relative_to(ROOT))],
                  "pre_regeneration_commands": commands, "pack_files_before": len(before),
                  "pack_files_after": len(after), "changed_pack_files": changed_pack,
                  "current_isolated_output_matches_shipped": True,
                  "native_acceptance": "unrun"})
    (OUT / "targeted-behavior-drift.json").write_text(json.dumps(scope, indent=2) + "\n")
    print(json.dumps(scope, indent=2))

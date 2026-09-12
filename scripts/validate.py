"""Run the Linux conformance gates and retain every command's output/exit status.

This is also the CI entry point. It never publishes packs or runs --full.
"""
import argparse
import json
import os
from pathlib import Path
import platform
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT / 'tmp/validation')
    args = parser.parse_args()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    commands = {
        'build': [sys.executable, 'scripts/build_addon.py'],
        'lint': ['npm', 'run', 'lint'],
        'expressions': [sys.executable, 'scripts/verify_emotes.py'],
        'animations': [sys.executable, 'scripts/_audit_anims.py'],
        'hud': [sys.executable, 'scripts/audit_hud.py', '--check'],
        'behavior-tests': [sys.executable, 'scripts/tests/test_gen_behavior.py'],
        'animation-tests': [sys.executable, 'scripts/tests/test_animation_audit.py'],
        'branding-tests': [sys.executable, 'scripts/tests/test_branding.py'],
        'branding-scan-tests': [sys.executable, 'scripts/tests/test_branding_scan.py'],
        'structure-tests': [sys.executable, 'scripts/tests/test_structure_manifest.py'],
        'structure-placement-tests': ['node', 'scripts/tests/structure_placement.test.cjs'],
        'cullis-tests': [sys.executable, 'scripts/tests/test_cullis_gate.py'],
        'graveyard-tests': [sys.executable, 'scripts/tests/test_graveyard.py'],
        'bandit-camp-tests': [sys.executable, 'scripts/tests/test_bandit_camp.py'],
        'bowerstone-north-tests': [sys.executable, 'scripts/tests/test_bowerstone_north.py'],
        'arena-halls-tests': [sys.executable, 'scripts/tests/test_arena_halls.py'],
        'scoreboard-tests': [sys.executable, 'scripts/tests/test_conformance_score.py'],
        'scoreboard': [sys.executable, 'scripts/conformance_score.py', '--check'],
        'runtime-tests': ['npm', 'test'],
        'original-preview': [sys.executable, 'scripts/build_addon.py', '--branding', 'original', '--preview'],
    }
    env = dict(os.environ, PYTHON=sys.executable)
    results = {}
    for name, command in commands.items():
        print(f'Running {name}...', flush=True)
        try:
            result = subprocess.run(command, cwd=ROOT, env=env, text=True,
                                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=600)
            code, log = result.returncode, result.stdout
        except (OSError, subprocess.TimeoutExpired) as error:
            code, log = 1, str(error) + '\n'
        (output / f'{name}.log').write_text(log, encoding='utf-8')
        results[name] = {'command': command, 'exit_code': code}
        print(f'{name}: {"PASS" if code == 0 else "FAIL"}', flush=True)
        if code:
            print(log, flush=True)
    summary = {'python': platform.python_version(), 'platform': platform.platform(), 'checks': results}
    (output / 'results.json').write_text(json.dumps(summary, indent=2) + '\n', encoding='utf-8')
    print(f'Validation evidence: {output}', flush=True)
    return int(any(item['exit_code'] != 0 for item in results.values()))


if __name__ == '__main__':
    sys.exit(main())

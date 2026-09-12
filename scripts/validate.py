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
        'guild-training-tests': ['node', '--experimental-vm-modules', 'scripts/tests/guild_training.test.mjs'],
        'guild-will-tests': [sys.executable, 'scripts/tests/test_guild_will.py'],
        'guild-maintenance-tests': [sys.executable, 'scripts/tests/test_guild_maintenance.py'],
        'guild-defence-tests': ['node', '--experimental-vm-modules', 'scripts/tests/guild_defence.test.mjs'],
        'guild-resident-tests': ['node', '--experimental-vm-modules', 'scripts/tests/guild_residents.test.mjs'],
        'guild-route-tests': [sys.executable, 'scripts/tests/test_guild_routes.py'],
        'guild-cave-tests': ['node', '--experimental-vm-modules', 'scripts/tests/guild_caves.test.mjs'],
        'chamber-route-tests': [sys.executable, 'scripts/tests/test_chamber_routes.py'],
        'chamber-cullis-tests': ['node', 'scripts/tests/guild_chamber_cullis.test.mjs'],
        'guild-door-geometry-tests': [sys.executable, 'scripts/tests/test_guild_door_geometry.py'],
        'guild-door-aperture-tests': ['node', '--experimental-vm-modules', 'scripts/tests/guild_door_aperture.test.mjs'],
        'demon-door-tests': [sys.executable, 'scripts/tests/test_demon_doors.py'],
        'demon-door-integration-tests': ['node', '--experimental-vm-modules', 'scripts/tests/demon_door_integration.test.mjs'],
        'library-arcanum-tests': [sys.executable, 'scripts/tests/test_library_arcanum.py'],
        'structure-tests': [sys.executable, 'scripts/tests/test_structure_manifest.py'],
        'structure-placement-tests': ['node', 'scripts/tests/structure_placement.test.cjs'],
        'cullis-tests': [sys.executable, 'scripts/tests/test_cullis_gate.py'],
        'graveyard-tests': [sys.executable, 'scripts/tests/test_graveyard.py'],
        'grey-house-tests': [sys.executable, 'scripts/tests/test_grey_house.py'],
        'greatwood-gorge-tests': [sys.executable, 'scripts/tests/test_greatwood_gorge.py'],
        'archon-folly-tests': [sys.executable, 'scripts/tests/test_archon_folly.py'],
        'archon-shrine-tests': [sys.executable, 'scripts/tests/test_archon_shrine.py'],
        'bargate-prison-tests': [sys.executable, 'scripts/tests/test_bargate_prison.py'],
        'bandit-camp-tests': [sys.executable, 'scripts/tests/test_bandit_camp.py'],
        'oakvale-memorial-tests': [sys.executable, 'scripts/tests/test_oakvale_memorial.py'],
        'hook-coast-tests': [sys.executable, 'scripts/tests/test_hook_coast.py'],
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

"""Run production cave lifecycle and assembled-route checks; no mirrored carve.

GP4 proved the historical mirror passed despite a missing actual entry floor.
This command now delegates to the same production callback/voxel suites as CI.
Results are offline evidence, never proof of Bedrock collision or pathfinding.
Historical baseline evidence remains in screenshots/validation/GP4-cave-audit/.
"""
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def main():
    commands = (
        ['node', '--experimental-vm-modules', 'scripts/tests/guild_caves.test.mjs'],
        [sys.executable, 'scripts/tests/test_chamber_routes.py'],
        ['node', 'scripts/tests/guild_chamber_cullis.test.mjs'],
    )
    failed = False
    for command in commands:
        print('Running ' + ' '.join(command), flush=True)
        failed |= subprocess.run(command, cwd=ROOT).returncode != 0
    return int(failed)


if __name__ == '__main__':
    sys.exit(main())

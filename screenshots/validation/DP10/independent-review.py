#!/usr/bin/env python3
"""Run independent DP10 probes with explicit native fixture files; never run Git."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("review", "baseline-native", "baseline-authority", "multiplier"), default="review")
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[3])
    parser.add_argument("--owner", type=Path, help="Explicit Arboretum predecessor/current owner; required for baseline modes.")
    parser.add_argument("--main", type=Path, help="Explicit main.js for multiplier extraction; defaults to current owned main.js.")
    args = parser.parse_args()
    root = args.repo.resolve()
    here = Path(__file__).resolve().parent
    if args.mode.startswith("baseline") and args.owner is None:
        parser.error("Baseline probes require --owner pointing to the captured predecessor Arboretum owner.")
    env = os.environ.copy()
    if args.mode == "multiplier":
        owner = (args.main or root / "packs/Fablecraft_BP/scripts/main.js").resolve()
        env["MULTIPLIER_OWNER"] = str(owner)
        print(f"Multiplier owner SHA256 {hashlib.sha256(owner.read_bytes()).hexdigest()}", flush=True)
        return subprocess.run(["node", str(here / "multiplier-audit.mjs")], cwd=root, env=env).returncode

    owner = (args.owner or root / "packs/Fablecraft_BP/scripts/arboretum_doors.js").resolve()
    print(f"Arboretum owner SHA256 {hashlib.sha256(owner.read_bytes()).hexdigest()}", flush=True)
    # Execute the actual owned builder in a separate Python process. No generated
    # structure is changed, and no captured baseline owner is silently retrieved.
    generated = subprocess.run([
        sys.executable, "-c",
        "import sys,json;sys.path.insert(0,'scripts');"
        "from gen_structures import Vox;from door_realms import build_arboretum;"
        "Vox.save=lambda *args:None;v=build_arboretum(Vox);"
        "print(json.dumps({'size':[v.sx,v.sy,v.sz],'grid':v.grid,'palette':[p[0] for p in v.palette]}))",
    ], cwd=root, text=True, capture_output=True, check=True)
    geometry = json.dumps(json.loads(generated.stdout))
    print(f"Generated geometry SHA256 {hashlib.sha256(geometry.encode()).hexdigest()}", flush=True)
    helper = {"review": "independent-review.mjs", "baseline-native": "independent-baseline-probes.mjs",
              "baseline-authority": "independent-baseline-authority.mjs"}[args.mode]
    with tempfile.TemporaryDirectory(prefix="fc-dp10-independent-") as scratch:
        geometry_path = Path(scratch) / "arboretum-geometry.json"
        geometry_path.write_text(geometry)
        env["ARBORETUM_OWNER"] = str(owner)
        env["ARBORETUM_GEOMETRY"] = str(geometry_path)
        return subprocess.run(["node", "--experimental-vm-modules", str(here / helper)], cwd=root, env=env).returncode


if __name__ == "__main__":
    raise SystemExit(main())

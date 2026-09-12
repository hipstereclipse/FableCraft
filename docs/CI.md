# Continuous conformance validation

`.github/workflows/validate.yml` runs on pushes and pull requests with read-only
repository permissions. It pins Ubuntu 24.04, Python 3.14.7 and Node 26.7.0, installs
the declared Python dependencies and locked npm tooling, then runs:

```sh
python scripts/validate.py
```

The same entry point works locally. `--output <directory>` selects the evidence
directory; the default is `tmp/validation/`. Every command records its output and
exit status, and any failed gate makes the overall command fail. The runner invokes
the local faithful build, lint, expression/animation/HUD audits, behavior/animation/
branding/structure regressions, placement, Cullis geometry/detector and scoreboard checks, all runtime tests and the isolated original naming preview.

The workflow uploads only `tmp/validation/` logs, retained for 14 days. It does not
upload local development archives or preview pack trees. It does not regenerate all
assets, change repository state or publish a release. In-world checks remain manual.

Official action v7 tags were resolved to commit hashes on 2026-09-12, using the
[checkout](https://github.com/actions/checkout),
[setup-python](https://github.com/actions/setup-python),
[setup-node](https://github.com/actions/setup-node) and
[upload-artifact](https://github.com/actions/upload-artifact) repositories. Update pins
deliberately after reviewing upstream changes and rerunning the clean-checkout test.

## Verification record

Local working-tree checks passed, as did a fresh archive of tracked commit `cb9e0db`
plus the two new CI files. That snapshot installed dependencies into a new Python
virtual environment and a new node_modules directory; it used no untracked pack
package.json or existing workspace dependencies. Evidence is under
`screenshots/validation/C1/` and its `clean/` subdirectory.

GitHub Actions [run 34676941284](https://github.com/hipstereclipse/FableCraft/actions/runs/34676941284)
completed successfully for `086337c478d6dc8935077778a1d23966ef2aac4d`. The job result and
actual validator artifact are retained in `screenshots/validation/C1/remote-run.json`
and `C1/remote/`. C1 is complete; this evidence verifies CI, not in-world behavior.

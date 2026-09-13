# GP24 author evidence correction

The initial author report used the literal key `walking.new_nodes` twice. Python retained the later list and silently dropped the candidate-node count. The successful console log still recorded 13,818 nodes. The corrected report stores `candidate_nodes: 13818` and twelve `added_nodes` separately. A syntax-tree check found no duplicate literal string keys in the corrected helper.

The original report, helper and successful log are preserved as `author-report-initial.json`, `author-helper-initial.py` and `author-report-initial.log`. Their exact hashes are in `author-report-correction.json`, alongside the unchanged production owner/asset hashes and byte-identical four render hashes. The earlier uniform-ceiling assertion failure remains separately preserved in `author-initial.log`.

The helper now accepts `--output`, `--baseline-owner`, `--baseline-asset` and optional `--references`. External source comparison is generated only when requested and both ignored source images exist; missing source pixels cause a recorded skip. Historical accepted source URLs/hashes remain in every report through GP23/reference-index.json. Existing files are not deleted when an optional sheet is skipped.

The corrected helper passed with explicit baseline/output options and reference pixels. A separate run from `/tmp` to an external output directory passed without `--references`, retained the corrected counts and historical source hashes, skipped the source sheet, and reproduced the same four decoded PNGs. Only this evidence helper was rerun; no production source or asset changed.

A read-only missing-file fixture also exercised `--references` with both source images reported unavailable. It passed with a recorded skip and retained the exact historical source hashes. No source image was moved or removed.

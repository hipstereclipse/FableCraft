# GP23 helper corrections and output preservation

No base gate failed and no production source changed for these corrections.

The independent comparison initially rejected inherited fc_lib.py CRLF bytes before generation. Its corrected dependency-only comparison ignores CRLF without rewriting either file. Exact actual generator/serialized comparisons remain. A later focused render margin adjustment prevents caption overlap; original logs and earlier images remain. See independent-helper-corrections.md.

The first full-render summary assumed all282 outputs were Git-tracked; spell_ghost_sword.png is intentionally retained only in render scratch. visual-summary-initial.log preserves a repeat capture of the same failed helper. The corrected comparison checks each actual GP22 full-render output against its committed visual-delta after hash before comparing GP23. DP10 changed no render inputs. All document comparisons still use actual DP10 committed image blobs. No output was copied before that first summary failure.

The exact lint stdout, including its trailing empty line, is preserved in lint-raw-output.json with original/readable hashes. Only that extra blank line is removed from readable lint.log to satisfy the staged whitespace check. This formatting does not change the command, exit code or original output. The separate DP10 commit-sequence error and required fail-fast follow-up are documented in dp10-commit-check-correction.md.

The GP23 staging check correctly stopped before commit on the original unified-diff artifact's blank context line, which has the required patch-format leading space. staged-check-initial.json preserves the check output. The exact patch is now encoded in owner-semantic-patch.json with its SHA256; its original file remains in ignored scratch. No source change or functional retest was required. The final staged check passes.

The raw check output echoed that literal trailing space and was itself rejected by the next staged check. Its exact output is likewise retained as JSON data, with the original log in ignored scratch. Both staged failures stopped before any commit.

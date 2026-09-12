# Reproducible progress reporting

Run `python scripts/conformance_score.py --write` after changing a checklist row,
then `python scripts/conformance_score.py --check`. CI checks the generated section
and runs ten integrity regressions. Only the marked section is rewritten; surrounding
manual findings remain intact.

The script recognizes the 45 stable IDs of the approved plan. Missing/duplicate IDs,
unknown states, missing evidence paths, invalid commit-reference syntax and incomplete
grades marked done fail. It validates all supplied local evidence paths for started
rows. It accepts SELF references for the containing milestone commit; resolve those
in the next checkpoint. Historical commit syntax is checked, but the tool does not
claim a shallow CI checkout can verify every historical commit's contents.

Domain completion is done leaves divided by all leaves. Automated PASS and pending
manual observations are counted separately from explicit grade cells. Neither an
automated pass nor a high renderer score closes an in-world checklist. Todo rows have
unknown verification. The separate spell/bootstrap rows are outside the 45-plan-leaf
denominator; their manual work remains visible above the generated section.

The current C2 structure audit contributes a histogram of its actual S/A/B/C/D image
appearance grades. The scoreboard does not average letters, treat these metrics as
canon grades, or infer an overall full-world completeness percentage. Older broad
render grades are not silently substituted for the current source-linked audit.

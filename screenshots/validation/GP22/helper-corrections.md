# GP22 evidence helper corrections

The first C2-copy helper assumed the twelve-cell scenery would change the distant
Guild image. The fresh render instead matches all 36 previous PNGs exactly; only
the Guild asset hash in evidence.json changes. Its assertion rejected the output
after copying that JSON, before writing c2-paths.json. The following staging
helper therefore failed to read c2-paths.json. Both original tool outputs are
retained in helper-initial-output.json. No image was changed to satisfy the
incorrect helper assumption. The corrected helper checks the observed exact
image equality and stages only the new asset provenance.

The first diagnostics launch attempted to read a previous ignored helper using
a relative path from the isolated snapshot. That path does not exist there.
The root-owned helper was created using absolute repository paths and rerun in
the snapshot. No diagnostic or gameplay assertion was reached on that launch.

The base validator began with already-fresh C2 outputs while the staging-helper
correction was being completed; the exact fresh outputs were then staged and
synchronized without changing any validated runtime/generator source.

The final staging audit found a separate documentation baseline error. GP21's
reviewed snapshot retained DP8 images in screenshots/docs, while its fresh GP21
outputs were written to tmp/GP21-doc-screenshots and then committed. The first
GP22 summary compared the former and incorrectly called three documentation
views changed. Comparing all seven actual GP21 committed blobs with its recorded
custom output proves that only 26_archery_backboard changes in GP22; views01/12
and the other four remain exact. Initial summaries/root notes and the assertion
output are retained with initial- prefixes. The corrected summary uses actual
committed blobs. No render or production change was needed, and no base gate
failed. The two unchanged images were explicitly re-added, producing no diff.

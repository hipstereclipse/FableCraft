# DP7 final verification

All 55 base gates and 65 ESM syntax checks pass in the isolated reviewed-index
snapshot. Runtime 27, actual main integration 16, alignment 6, Arboretum geometry 9,
Gorge 9, Library 5 and retained Guild adapter 38 groups pass. Independent runtime
review passes six negative probes against the final owner; its retained initial
checkpoint reproduces the revision-exhaustion defect before the final guard.
The first full run passed 54/55: the older rectangular-placement fixture lacked
new external portal dependencies. Only that fixture changed and its nine groups
reran successfully; the original result/log is retained. The earlier population
fixture correction and development failures are also explicitly recorded.

Fresh 36-asset C2, all 282 full PNGs and Guild diagnostics pass. Compared with GP20,
only the Gorge asset/C2 image changes and the Arboretum is added; all 34 other
assets/C2 images remain exact. Only the Gorge card and containing places gallery
change among 281 existing full PNGs, with one Arboretum card added. Root inspected
both cards, the gallery and six focused geometry views. Native acceptance remains
unrun. DP7 is the next visual baseline; C3 retains 45 leaves and 7 done.

The final reviewed source/contract hashes are recorded in provenance.json.
The isolated snapshot refreshed only structure_placement.test.cjs after its
failed gate; later documentation finalization does not change executable inputs.
Builds remain under ignored snapshot tmp/builds; protected dist and overlay files
are preserved. No external reference pixels or untracked local configuration
files are part of this milestone.

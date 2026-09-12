# DP4 offline source-authority evidence

All 39 base gates pass in results.json from the isolated reviewed-index snapshot.
The final actual-adapter suite passes 25 groups. adapter-red.log reproduces four
DP3 failures (20 passing groups); adapter-final.log includes the repairs and an
additional dimension/unavailable-scan regression. The base adapter log is refreshed
with that final suite; the scoreboard is rechecked after the checklist update.

additional-results.json records 62 ESM syntax checks and byte-identical dependencies
for GP6 full renders and GP5 Guild diagnostics. No asset/render owner changed.
provenance.json links source and log hashes; snapshot-provenance.json identifies
the isolated source. baseline-remote-run.json verifies successful DP3 exact-head CI.
Independent review found no blocking defect. All native Bedrock acceptance remains
unrun; stale faces with uncertain ownership are retained. See the DP4 specification.

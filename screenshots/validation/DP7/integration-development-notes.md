# DP7 integration fixture development log provenance

These raw logs preserve intermediate test development. They are not final gates
or evidence of native failures. Only the current final suite and its source
manifest count toward the milestone.

| Run | Result meaning | Test revision provenance |
| --- | --- | --- |
| first | Direct-placement fixture omitted the new successful-placement receipt before confirming. This caused dependent fixture setup failures. | Exact test revision was not retained; unavailable. |
| second | Fixture incorrectly expected unavailable alignment to prevent independent food progress. Correct contract allows one food count but denies the alignment shortcut. | Exact test revision was not retained; unavailable. |
| third | Fixture expected -1000 after a one-shot failed state read although the readable backing state was alignment 0; the old morality owner correctly produced -15. Fixture now uses actual -1000 backing state or missing state with legacy -1000 to exercise normalization ordering. | Exact test revision was not retained; unavailable. |
| fourth | Deferred confirmation was incorrectly driven through controller `tick` rather than actual main `ensureArboretumFaces` near the source. Bulk fixture also accepted only air filters and rejected new barrier queries. | SHA-256 in `integration-development-fourth-test.sha256`, captured before the next edit. |
| fifth | Final room/reward succeeded, but the assertion used inventory log element 4; the fixture records item type at element 3. | SHA-256 in `integration-development-fifth-test.sha256`, captured before the next edit. |

The first three test sources cannot be reconstructed exactly from retained
artifacts; no source hash is invented for them. Their raw logs remain historical
context, not independently reproducible defect proofs. Fourth and fifth hashes
identify the then-current test text; production sources were changing in
parallel and their exact run snapshots were not captured. Final validation
records fresh source hashes and asserts that they stay fixed during execution.

The successful current suite additionally tests unknown pending placements with
matching final mouth geometry and a late shell edit before reward readiness.
These are actual-controller regressions with injected engine failures; native
acceptance remains unrun.

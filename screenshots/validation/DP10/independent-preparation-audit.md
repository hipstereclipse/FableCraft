# Independent Demon Door preparation and third-family integration audit

2026-09-13. Read-only production audit; probes execute captured actual controllers and actual generated Arboretum voxels. Native Bedrock acceptance is **unrun**. `independent-review-provenance.json` records the exact baseline and source hashes. The DP10 production correction is reviewed separately from these baseline reproductions.

## Highest-priority reproducible defect

The current Arboretum worker does not pin the whole record for its active preparation job. While its first air scan is active, a later **valid, higher-revision ready/visited/claimed record** can replace the original allocated history. The next slices adopt that record. At scan completion the worker writes `placing` while retaining `visited:true`, invokes the native structure placement, and leaves a record rejected by its own reader. A visited room's authoritative history therefore does not prevent a stale preparation job from placing again. This is a mocked authority transition, not an assertion that this transition or native fault occurred in an actual Bedrock world.

`independent-baseline-authority.mjs` and `independent-baseline-authority-original.log` retain the complete reproduction. A second authority probe replaces progress with different valid data at the same revision during empty-inventory readback; the seed save silently restores its stale empty progress. Revision equality alone is not whole-record equality.

`independent-baseline-probes.mjs` and `independent-baseline-probes-original.log` reproduce six additional preparation gaps:

1. A seven-diamond slot zero written at the saved seed-intent boundary is overwritten by the Pickhammer.
2. A Hero arriving at that boundary does not prevent the native reward write or ready commit.
3. Replacing the native chest at that boundary leaves its diamond contents in place, writes the Pickhammer into the detached old handle, and commits ready.
4. Replacing the chest with an empty chest during `setItem` lets stale handle readback commit ready; ordinary claim observation then records the missing reward as claimed.
5. Correct item/count with an incorrect custom name and lore passes exact-reward acceptance.
6. Complete native placement followed by a thrown call resumes through reload, seeds, and admits despite having no saved successful-placement receipt. The older DP7 test deliberately accepted this recovery; DP9's stricter receipt boundary requires an explicit compatibility change, not a claim that DP7 already promised it.

Normal first build and collected-ready reload controls retain exactly one placement and one seed. The two baseline logs exit successfully because the unsafe outcomes were reproduced, not because those outcomes are acceptable.

## Independent DP10 draft review

`independent-review.py` defaults to the current production owner and derives actual current Arboretum geometry through Python; its JavaScript helper receives explicit owner/geometry paths. Baseline modes require an explicitly supplied captured predecessor owner. The fixture models native `ItemStack.getLore()`; the original baseline fixture and captured owner remain unchanged. `independent-review-initial.log` passes 22 cases: all reproduced boundaries, separate name/lore refusals, both history changes, before/after failures for placed/seeded/ready persistence, five native seed failures, unmarked legacy placing refusal, normal generation, and depleted-ready reload.

The reviewed draft introduces optional room preparation receipts within the existing schema, whole-record job comparison, fresh post-intent inventory acquisition, exact native reward readback and read-only seeded recovery. Intent-only placing is deliberately closed. No blocker was found in this draft review. This result does not certify untested native save ordering or arbitrary changes between independent native reads.


## Portable reproduction

Run from the repository root:

```sh
python screenshots/validation/DP10/independent-review.py --mode review
python screenshots/validation/DP10/independent-review.py --mode baseline-native --owner /tmp/dp10-before.js
python screenshots/validation/DP10/independent-review.py --mode baseline-authority --owner /tmp/dp10-before.js
```

The baseline file must be the Arboretum owner identified by `independent-review-provenance.json`; extract that committed file with a separate read-only `git show` command if the ignored captured owner is unavailable. The Python driver never invokes Git. It derives current owned geometry once per run and passes a temporary JSON file to Node; all structure/geometry owners are unchanged by DP10. JavaScript helpers do not spawn child processes. Direct JavaScript use requires `ARBORETUM_OWNER` and `ARBORETUM_GEOMETRY`. The original logs are byte-for-byte retained; curated helpers change only path/loading portability.

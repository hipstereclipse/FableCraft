# GP24 evidence reproduction

The source snapshot came from the explicitly reviewed Git index. Production is
scripts/gen_structures.py and its generated Guild asset; no runtime change.
Base invocation was python scripts/validate.py --output <root>/screenshots/validation/GP24
from tmp/conformance/GP24-reviewed-snapshot. Fresh C2 preceded base validation.
See provenance.json, generation-provenance.json and actual command/result logs.

From this checkpoint's repository root, reproduce the independent review with:

```sh
python screenshots/validation/GP24/independent-review.py --render --output tmp/conformance/gp24-reproduction
```

Its resident-probe.mjs and reference-reinspection.json are sibling resources.
It reads the exact committed GP23 baseline with git show. Generated comparison
structures remain in ignored tmp. External reference pixels are optional; when
absent, the helper retains historical provenance without claiming reinspection.
The initial and support-pass review runs passed; retained logs and helper hashes
show the subsequent evidence additions. Final-files provenance records originals
under scratch names; curated byte copies use descriptive independent names.

For the author comparison helper, first export GP23's scripts/gen_structures.py
and packs/Fablecraft_BP/structures/fc/guild_hall.mcstructure with git show into
ignored scratch. Then pass those paths to author-check-and-render.py using
--baseline-owner and --baseline-asset, plus --output in ignored scratch.
--references is optional and only creates a comparison sheet if both ignored
source images are available. Never stage that external-pixel sheet or comparison
mcstructure files. Original helper/report errors remain with correction notes.

The next-door-authority-and-grid-probe.mjs uses current main only after checking
its exact reviewed SHA; FC_REVIEW_MAIN can provide the exported baseline file.
The reader/grid remain proposals, not a third implemented room or combat owner.

No native Bedrock world, movement, loading, collision or saved-world acceptance
was performed by any of these helpers.

# Independent helper corrections

The first helper execution stopped before generation because it compared raw
`scripts/fc_lib.py` bytes with committed DP10 bytes. The worktree copy contains
inherited CRLF line endings. `independent-review-initial.log` preserves that
failure. The initial helper SHA256 was
`62142c97a149de21fa4d12c9f71284c198fcd0b6e1707a635d77250e89c60461`;
its complete copy stays ignored at
`tmp/conformance/gp23-independent/independent-review-initial.py`.

The corrected read-only check compares this dependency after replacing CRLF
with LF on both sides and records both original raw hashes. It does not rewrite
either source or weaken any generated-asset comparison. The committed dependency
hash is `c53491f9d640c9e10cb5b3d8f65ea8c85b3f526af03f7631d5d447ab6fe70797`;
the worktree hash is
`59753116ed20321b443138b0f3ef872bcac5ded9273964ed607a5a2ea804dec0`.

The next execution passed every geometry/behavior comparison and produced the
first eight decoded images. Its output remains in `independent-review-pass1.log`;
those first images and summary remain ignored under
`tmp/conformance/gp23-independent/focused-pass1/`. Visual inspection found the
approach ground plate too close to its caption. The helper's render viewport
height changes from 560 to 640, canvas height from 660 to 760, and captions move
from y608/633 to y708/733. Camera angles, 52-pixel scale, common framing bounds,
geometry, assertions and production sources remain unchanged. Final output is
`independent-review.log` and `independent-summary.json`.

Neither correction changes production or represents a failed base-validation
gate. All native acceptance remains unrun.

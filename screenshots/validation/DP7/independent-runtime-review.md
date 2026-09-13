# DP7 independent controller review

No remaining blocker found in the reviewed controller scope. Final reviewed
`arboretum_doors.js` SHA256:
`d2ea54066b594d57a3b9432c2a3b11edc85b41d08f2305caf96122c7ce9e7557`.

Read the actual registration, witness/counter, room allocation/build, reward,
entry, return-ticket, protection and cleanup paths. Independently exercised six
selected negative cases using the actual controller and current owned Arboretum
voxels. All six pass against the final hash. This review does not independently
certify geometry authored by the same reviewer; root inspected its six views and
owns the complete isolated validation, while another agent owns actual main
integration coverage.

The initial read raised exact seed readback, surviving reservation/bootstrap and
late shell-verification gaps. The first retained executable checkpoint already
contained their repairs, so its results are **not** represented as pre-fix failure
evidence. That actual checkpoint, SHA256
`7079fd2504a825226dedb01d469b0ffef94e5ce2a926184fe09e42c55cb415a1`,
passes five cases and fails the independently reproduced revision-boundary case:
a successful completed-use write changed an accepted revision to a number the
reader rejected, making saved history unreadable.

Final probes establish:

- Ignored seed writes, wrong items and wrong counts remain in ambiguous
  `seeding`, with neither seeded nor claimed authority. No second placement or
  successful admission is inferred from the attempted native write.
- A surviving cell reservation prevents a namespace from being treated as
  pristine after index/witness/state loss. The registration attempt changes no
  backing properties.
- Removing a previously scanned, non-sentinel shell cell before readiness
  prevents seeding/admission. The final containment check sees the late hole.
- The final allowed revision remains readable; a further completed-use mutation
  at the terminal revision is refused without changing saved properties. The
  allocation path also checks the terminal revision before changing the index
  or reserving another cell.

Reproduce current results with
`python screenshots/validation/DP7/run-independent-runtime-probe.py`.
The runner captures actual owner voxels with `Vox.save` disabled into ignored
scratch, then runs `independent-runtime-probe.mjs`. No preexisting ignored JSON
or production regeneration is needed. The Node probe derives dependency setup
from the permanent controller fixture but defines these six scenarios itself.
Controller, fixture and geometry hashes are retained in
`independent-runtime-results.json`; raw output is `independent-runtime.log`.

To reproduce the first checkpoint's five-pass/one-fail result, pass
`screenshots/validation/DP7/independent-runtime-initial-controller.js.txt` to the
same runner. The corresponding `independent-runtime-initial-results.json` and
`.log` retain the observed failure. The initial filename means first independent
review checkpoint, not the original implementation draft.

Native structure placement, API cost, ticking-area loading, consumption plus
property-write atomicity, inventory transfer, player collision, exact-source
travel, reload/death and simultaneous Heroes remain unrun. The controller's
permanent suite and root's main integration tests supply broader automated
coverage; this bounded independent probe is not a substitute for them or native
acceptance. No production runtime code, tests or staging were modified by this
independent controller review.

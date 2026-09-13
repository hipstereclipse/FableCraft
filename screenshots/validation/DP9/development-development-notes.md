# DP9 regression development results

Only scripts/tests/demon_doors.test.mjs and scripts/tests/demon_door_integration.test.mjs were changed by this test task. All production changes belonged to the root agent.

- Runtime attempt 1 failed at the `ready/substitute` fixture expectation. The native fault deliberately persisted a different valid ready record; the controller rejected exact readback and did not overwrite that observed value. The test had incorrectly required that no ready raw value exist. Its corrected assertion preserves the substituted source value, diagnostic, no movement and exact bounded placement/seed counts. This first log combines the verbatim output retained in the initial exec and final poll tool results; that invocation was not redirected to disk.
- Runtime attempt 2 passed the native fault matrices and both new per-item authority/contents race probes, then failed the final legacy-ready test. That fixture entered on its first tick after reload, correctly triggering existing portal anti-bounce disarming. The test now performs the supported leave/rearm before entering. No production change was made for either harness correction.
- Runtime attempt 3 passed all 29 groups. Original 13 groups are retained, with the old automatic seed-retry-success contract replaced by conservative partial-seed quarantine. Sixteen additional groups cover the guarded preparation design.
- Adapter attempt 1 used `node --experimental-vm-modules --test ...` and reported one successful file-level test. The normal repository gate command was then used for attempt 2: `node --experimental-vm-modules scripts/tests/demon_door_integration.test.mjs`. It reported all 39 groups passing (38 retained plus the actual native bulk-adapter boundary case).

Runtime command for all three attempts: `python scripts/tests/test_demon_doors.py`, which calls the actual generated Library voxel builder without writing pack artifacts. No native Bedrock engine acceptance was run.

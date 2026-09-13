# Independent review of first DP9 production patch

Frozen owner: `fc_demon_doors.review1.js`; SHA-256 is in
`review1-sha256.txt`. Actual geometry and injected native-effects harness are
reused. No production edits were made by this reviewer.

Run:

```sh
node --experimental-vm-modules tmp/conformance/dp9-audit/review1-probes.mjs tmp/conformance/dp9-audit/room.json
```

`review1-probes.log` retains 26 observation cases. First 24 exercise before-write
throws, after-write throws, silently dropped writes and substituted valid source
writes at allocated/placing/placed/seeding/seeded/ready journal transitions.
Across retry/reload, every case retained at most one actual room placement and
four attempted native reward writes. Failed intents persisted before any effect
remain conservatively blocked. Verified placed and seeded receipts can progress
without repeating their corresponding effects. Dropped intent writes permit a
fresh attempt because the prior native effect never ran.

Two bounded initial-patch defects remain at the four separate native item
boundaries:

1. During the first native setItem effect, replace world history with an
   otherwise valid ready/visited record, all four claims true. The first patch
   still calls setItem for the three other targets before its seed-receipt save
   notices changed authority. The newer record remains preserved, but the three
   unauthorized effects have already happened.
2. During that first effect, put 64 diamonds into the second target's slot 0.
   The first patch overwrites them with Making Friends and commits ready. The
   earlier all-four empty survey no longer describes this target.

The recommendation is narrow: immediately before each of the four setItem
calls, reacquire the target, require every slot still empty, and reread the
exact pinned authority after obtaining the handle/constructing metadata. Stop
before further item effects when either condition changed. Keep the existing
fresh post-effect exact readback and final geometry/occupancy checks. This is
independent of the retained whole-job and pre-journal authority guards.

These are native-effect injection reproductions, not live engine interleaving
claims. Native persistence and synchronous-effect behavior remain unrun.

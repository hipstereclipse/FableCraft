# GP20 independent material-bay review

No blocker found in the bounded production change. Reviewed the actual generator
and renderer diff against DP6 `274da7f779aec56562341a7dc75de58a8907b81c`, independently
serialized both complete Guild owners, decoded their little-endian NBT, and
inspected all six final before/after cutaways. This reviewer proposed the earlier
read-only candidate; root authored the production helper and renderer change.

The current generator SHA256 is
`787e34d47d364485ed30f2a12f8a96fa761d54016038f9a4bbe24369e27955b8`.
The shipped Guild matches that owner byte for byte, SHA256
`b9330af161ecc3fed96ccca1db05b51c059eacbd65b3cfbe90facdbce11015a0`.
The actual predecessor owner likewise matches its committed asset,
`a92f2c2ac76f1923b87f8c673a586d6427bb9a32a01dc5c83b7ab9f2091180e8`.

[The reproduction script](independent-review.py),
[complete results](independent-review-results.json) and
[successful command log](independent-review.log) retain the evidence. Run
`python screenshots/validation/GP20/independent-review.py` from the repository
root. It reads the actual committed predecessor, writes temporary structures only
under ignored scratch, and never modifies a pack or production source.

The decoded comparison proves exactly ten changed cells out of 395,280:
`x84,y7..8,z17..21`. Every old cell was solid stone brick. Six cells at `z18..20`
become red terracotta; four cells at `z17/21` become dark oak planks. No outside
cell changes. Existing palette entries, block states/versions, secondary layer,
entity list, origin and block metadata remain exact; one red-terracotta palette
entry is appended. Seeded RNG call keys/final state and all layout anchors match.
Only Guild changes among all 35 tracked structure assets. The renderer palette
adds only `minecraft:red_terracotta: (143,61,47)`.

All 4,820 other cells in the surveyed NE room remain exact, including all 345 y5
deck cells, ten east-wall glass panes, the roof courses, furniture and stairs.
The frozen 678 Maze reservations also remain exact. The complete campus retains
the same 13,822 walking nodes, 10,613-node gate component and 238-node bedroom
component. The bounded dorm stair retains all 284 half-cell nodes and both
21-point ascent/descent paths. All five wall-front points at `x85,y6,z17..21`
remain supported, clear and reachable; the full tower route also passes.
Independent unexpected-cell, deleted-top-tread and blocked-headroom injections
are all detected. The NBT adapter converts the upside-down byte to a Python
boolean for the existing stair model's strict `is False` assertion; raw palette
NBT is compared separately.

The original-TLC dormitory image
[141296214](https://steamcommunity.com/sharedfiles/filedetails/?id=141296214),
actually re-inspected, clearly supports red plaster-like panels between heavy
timber uprights above a carved lower dado. Its ignored retained pixel hash is
`4ca01ba79c85df67c6c644cdb7133403e4f6e90270432abd56403166632127cb`;
GP16 provenance, exact image URL and version limitations are repeated in results.
The chosen ten-cell position, proportions, terracotta/plank mapping and RGB color
are adaptations. The source does not establish this generated two-floor plan,
complete room dimensions, carved trim geometry or a calibrated palette.

The [east before](dorm-east-interior-before.png) and
[east after](dorm-east-interior-after.png) show the finish change clearly behind
the unchanged bed. The low west pair retains the stores roof and consequently
hides the changed wall. The [high west before](dorm-west-roof-high-before.png) and
[high west after](dorm-west-roof-high-after.png) expose its reverse face in the
existing roof recess. This small exterior-facing color change is acknowledged;
it is not a proved original exterior detail. No roof volume was altered.

All six images use actual decoded owner output and declared crop bounds, with
approximate flat colors. Carpets are thin; beds and other occupied cells remain
simplified full cubes. The resolved local font path/hash is recorded. Native
textures, lighting, physical collision, NPC navigation and occupied-world
migration remain unrun. This review does not close whole-dormitory fidelity or
the separate Skill arrival-calibration work.

# W1.2 render review

Inspected the original generator renders graveyard-isolated.png, graveyard-south.png,
and both roof cutaways. The south view shows the bald stone face, dark eye/mouth
recesses, projecting nose and three steps. The default north view conceals that face.
The new timber hut, crypt roof and headstone rows have distinct silhouettes; cutaways
show the interior floor, workbench light, chest and aisles around stone sarcophagi.
No unknown magenta block colors remain (palette regression also checks this).

These are original offline voxel renders. Stair/slab/iron-bar/glass collision and
lighting are approximated as cubes. The prominent pre-existing crypt roof still
dominates the yard; in-engine scale and the face's simplified beard need review.
No canon letter grade is assigned without inspected original-TLC reference pixels.
The MobyGames candidate and failed fetch are recorded in docs/LYCHFIELD_CRYPT.md.

The old owner fails four of seven regression groups; the new owner passes all seven.
The actual runtime scatter runs on generated blocks on grass and dark terrain and
checks three clear spawn positions, preserved loot bounds and region idempotence.
Those mocks do not replace the unrun manual checklist or implement Nostro's quest.

Full all-category pass completed with exit 0: 51 mobs, 55 item cards, 26 structure
cards, 130 recipe cards and 13 galleries. Its audit is full-render-AUDIT.md; only the
graveyard card was copied to the primary screenshot location. C2 separately covers
all 29 structure assets. The finial was already within bounds in the old owner; an
initial inspection suspicion was disproved by the strict write-bounds test.

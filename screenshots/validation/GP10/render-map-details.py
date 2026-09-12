"""Offline GP10 map comparison: half-height slabs, flat material colors, no engine light."""
from pathlib import Path
import hashlib
import json
import sys
from unittest.mock import patch

from PIL import Image

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "scripts/tests"))
import gen_structures as g
import gen_screenshots as render
from test_guild_map_table import legacy_map_table, voxel_changes

OUT = Path(__file__).resolve().parent
before_source = "f12b608e84bd4774caf6a39f4b2ba708ef71821b"
with patch.object(g, "build_guild_map_table", legacy_map_table):
    before = g.build_guild_hall()
after = g.build_guild_hall()


def detail(vox, bounds, *, yaw, pitch, size=(1100, 850), cut=False):
    quads = []
    for x in range(bounds[0], bounds[1] + 1):
        for y in range(bounds[2], bounds[3] + 1):
            for z in range(bounds[4], bounds[5] + 1):
                # Remove the near western slice above the floor to expose both
                # stairs and map. This is a cutaway, never a player camera claim.
                if cut and x <= 20 and y >= 1:
                    continue
                name, states = vox.palette[vox.grid[vox.idx(x, y, z)]]
                if name == "minecraft:air":
                    continue
                slab = name.endswith("_slab")
                height = .5 if slab else 1
                upper = states.get("minecraft:vertical_half") == "top" or states.get("top_slot_bit")
                offset = .5 if slab and upper else 0
                tex = Image.new("RGBA", (2, 2), render.BLOCK_COLORS.get(name, (200, 120, 200)) + (255,))
                quads.extend(render.cube_quads((x, y + offset, z), (1, height, 1), (0, 0), tex,
                                               glow=name in render.GLOW_BLOCKS))
    return render.render_quads(quads, size=size, yaw=yaw, pitch=pitch, shadow=False)


for label, vox in (("before", before), ("after", after)):
    detail(vox, (21, 31, 0, 3, 37, 47), yaw=.75, pitch=.76).save(OUT / f"map-relief-{label}.png")
    detail(vox, (18, 36, 0, 10, 32, 52), yaw=1.57, pitch=.62, cut=True).save(OUT / f"map-hall-cutaway-{label}.png")

changes = voxel_changes(before, after)
cx, cz, _ = g.GUILD_LAYOUT["rotunda"]
outside = [(x, y, z) for x, y, z in changes
           if not (1 <= y <= 3 and (x-cx)**2 + (z-cz)**2 <= 3.4**2)]
assert not outside, outside


def outside_hash(vox):
    h = hashlib.sha256()
    for x in range(vox.sx):
        for y in range(vox.sy):
            for z in range(vox.sz):
                if 1 <= y <= 3 and (x-cx)**2 + (z-cz)**2 <= 3.4**2:
                    continue
                name, states = vox.palette[vox.grid[vox.idx(x, y, z)]]
                h.update(json.dumps([x, y, z, name, states], sort_keys=True,
                                    separators=(",", ":")).encode() + b"\n")
    return h.hexdigest()


metadata = {
    "baseline_map_source_commit": before_source,
    "baseline_scope": "Historical GP7 map fixture inserted into current Guild builder; all adjoining geometry identical in both renders.",
    "scope": "Offline owner geometry; slab half heights are respected. Flat color geometry, not game textures, dynamic lighting, NPCs or a native player camera.",
    "map_crop": {"x": [21, 31], "y": [0, 3], "z": [37, 47]},
    "hall_cutaway": {"x": [18, 36], "y": [0, 10], "z": [32, 52],
                     "removed": "Western x<=20 slice above floor; roof and all geometry outside crop omitted."},
    "shared_rng_draws_preserved": 37,
    "changed_final_voxels": len(changes),
    "changed_coordinates": changes,
    "non_map_changed_voxels": len(outside),
    "normalized_outside_map_sha256_before": outside_hash(before),
    "normalized_outside_map_sha256_after": outside_hash(after),
    "normalization": "Absolute local cell coordinate, block identifier and sorted state properties; palette indices are intentionally ignored.",
    "new_renderer_color": {"minecraft:dark_prismarine_slab": [51, 91, 78]},
    "reference_files": {},
}
for name in ("guild-table-review.jpg", "guild-table-moby.png", "guild-hall-uve.jpg"):
    reference = ROOT / "tmp/conformance/reference-guild" / name
    if reference.exists():
        metadata["reference_files"][name] = hashlib.sha256(reference.read_bytes()).hexdigest()
(OUT / "map-render-scope.json").write_text(json.dumps(metadata, indent=2) + "\n")
print(json.dumps({"changed_final_voxels": len(changes), "non_map_changed_voxels": len(outside),
                  "outside_hash_match": metadata["normalized_outside_map_sha256_before"] == metadata["normalized_outside_map_sha256_after"]}))

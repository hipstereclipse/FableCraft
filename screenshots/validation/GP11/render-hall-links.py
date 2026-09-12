"""GP11 before/after geometry: remove obsolete indoor tunnel shells only."""
from pathlib import Path
import hashlib
import json
import sys
from unittest.mock import patch

from PIL import Image

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT / "scripts"), str(ROOT / "scripts/tests")]
import gen_structures as g
import gen_screenshots as render
from test_guild_hall_links import legacy_link_corridor, in_link_scope
from test_guild_map_table import voxel_changes

OUT = Path(__file__).resolve().parent
with patch.object(g, "finish_guild_link_floor", legacy_link_corridor):
    before = g.build_guild_hall()
after = g.build_guild_hall()


def detail(vox, bounds, *, yaw, pitch, clip=None):
    quads = []
    for x in range(bounds[0], bounds[1] + 1):
        for y in range(bounds[2], bounds[3] + 1):
            for z in range(bounds[4], bounds[5] + 1):
                if clip and clip(x, y, z):
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
    return render.render_quads(quads, size=(1200, 950), yaw=yaw, pitch=pitch, shadow=False)


for label, vox in (("before", before), ("after", after)):
    detail(vox, (21, 32, 0, 6, 27, 35), yaw=.35, pitch=.72,
           clip=lambda x, y, z: z >= 34 and y >= 3).save(OUT / f"library-join-{label}.png")
    detail(vox, (23, 32, 0, 6, 49, 56), yaw=2.85, pitch=.72,
           clip=lambda x, y, z: z <= 50 and y >= 3).save(OUT / f"store-join-{label}.png")
    detail(vox, (18, 36, 0, 10, 17, 47), yaw=1.57, pitch=.8,
           clip=lambda x, y, z: (x <= 20 and y >= 1) or (z <= 33 and y >= 7)).save(
               OUT / f"hall-library-cutaway-{label}.png")


def outside_hash(vox):
    h = hashlib.sha256()
    for x in range(vox.sx):
        for y in range(vox.sy):
            for z in range(vox.sz):
                if in_link_scope(x, y, z):
                    continue
                name, states = vox.palette[vox.grid[vox.idx(x, y, z)]]
                h.update(json.dumps([x, y, z, name, states], sort_keys=True,
                                    separators=(",", ":")).encode() + b"\n")
    return h.hexdigest()


changes = voxel_changes(before, after)
outside = [p for p in changes if not in_link_scope(*p)]
assert not outside, outside
metadata = {
    "historical_connector_source_commit": "f12b608e84bd4774caf6a39f4b2ba708ef71821b",
    "baseline_scope": "Historical vertical link_corridor branch inserted into current Guild builder; every other owner is identical in both builds.",
    "scope": "Offline geometry, actual half-height slabs, approximate flat material colors. Not Bedrock textures, lighting, NPC movement or native cameras.",
    "library_detail": {"x": [21, 32], "y": [0, 6], "z": [27, 35],
                       "removed": "South z>=34 above y2 to see past the rotunda stair carriage; all geometry outside crop omitted."},
    "store_detail": {"x": [23, 32], "y": [0, 6], "z": [49, 56],
                     "removed": "North z<=50 above y2 to see past the rotunda stair carriage; all geometry outside crop omitted."},
    "hall_library_cutaway": {"x": [18, 36], "y": [0, 10], "z": [17, 47],
                             "removed": "Western x<=20 above floor and Library z<=33 above y6; all geometry outside crop omitted."},
    "shared_rng_draws_preserved": 48,
    "changed_final_voxels": len(changes),
    "changed_coordinates": changes,
    "non_link_changed_voxels": len(outside),
    "normalized_outside_link_sha256_before": outside_hash(before),
    "normalized_outside_link_sha256_after": outside_hash(after),
    "normalization": "Local cell coordinate, block identifier and sorted state properties; palette indices ignored.",
    "reference_files": {},
}
for name in ("guild-table-review.jpg", "guild-table-moby.png", "guild-hall-uve.jpg",
             "page-034.png", "page-035.png", "page-036.png"):
    source = ROOT / "tmp/conformance/reference-guild" / name
    if source.exists():
        metadata["reference_files"][name] = hashlib.sha256(source.read_bytes()).hexdigest()
(OUT / "hall-link-render-scope.json").write_text(json.dumps(metadata, indent=2) + "\n")
print(json.dumps({"changed_final_voxels": len(changes), "non_link_changed_voxels": len(outside),
                  "outside_hash_match": metadata["normalized_outside_link_sha256_before"] == metadata["normalized_outside_link_sha256_after"]}))

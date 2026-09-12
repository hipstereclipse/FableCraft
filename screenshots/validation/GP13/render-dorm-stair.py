"""GP13 native-stair/slab geometry review; no engine texture or light simulation."""
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
from test_guild_dorm_routes import DormStairSurvey, LOWER, UPPER
from test_guild_map_table import voxel_changes

OUT = Path(__file__).resolve().parent
with patch.object(g, "restore_guild_dorm_stair_top", lambda *args: None):
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
                tex = Image.new("RGBA", (2, 2), render.BLOCK_COLORS.get(name, (200, 120, 200)) + (255,))
                boxes = [((x, y, z), (1, 1, 1))]
                if name.endswith("_slab"):
                    upper = states.get("minecraft:vertical_half") == "top" or states.get("top_slot_bit")
                    boxes = [((x, y + (.5 if upper else 0), z), (1, .5, 1))]
                elif name.endswith("_carpet"):
                    boxes = [((x, y, z), (1, 1/16, 1))]
                elif name == "minecraft:oak_stairs":
                    assert states.get("upside_down_bit") is False
                    d = states["weirdo_direction"]
                    upper_start = (x + (.5 if d == 0 else 0), y + .5, z + (.5 if d == 2 else 0))
                    upper_size = (.5, .5, 1) if d in (0, 1) else (1, .5, .5)
                    boxes = [((x, y, z), (1, .5, 1)), (upper_start, upper_size)]
                for start, size in boxes:
                    quads.extend(render.cube_quads(start, size, (0, 0), tex,
                                                   glow=name in render.GLOW_BLOCKS))
    return render.render_quads(quads, size=(1200, 950), yaw=yaw, pitch=pitch, shadow=False)


for label, vox in (("before", before), ("after", after)):
    detail(vox, (85, 91, 0, 7, 7, 13), yaw=2.7, pitch=.68,
           clip=lambda x, y, z: z <= 8 and y >= 5).save(OUT / f"dorm-stair-{label}.png")
    detail(vox, (84, 98, 0, 8, 6, 27), yaw=2.45, pitch=.9,
           clip=lambda x, y, z: (x == 84 or z == 6) and y >= 1).save(
               OUT / f"dorm-room-cutaway-{label}.png")


def outside_hash(vox):
    h = hashlib.sha256()
    for x in range(vox.sx):
        for y in range(vox.sy):
            for z in range(vox.sz):
                if (x, y, z) == (86, 5, 11):
                    continue
                name, states = vox.palette[vox.grid[vox.idx(x, y, z)]]
                h.update(json.dumps([x, y, z, name, states], sort_keys=True,
                                    separators=(",", ":")).encode() + b"\n")
    return h.hexdigest()


changes = voxel_changes(before, after)
assert changes == [(86, 5, 11)], changes
old_survey, survey = DormStairSurvey(before), DormStairSurvey(after)
metadata = {
    "baseline_scope": "Current Guild builder with only final tread restoration disabled; reproduces the original deck-cut deletion and unchanged lower native stair.",
    "scope": "Offline straight native stair boxes, half slabs and 1/16-block carpets; remaining furniture simplified. Approximate material colors, no Bedrock light/pathfinding/corner execution.",
    "stair_detail": {"x": [85, 91], "y": [0, 7], "z": [7, 13],
                     "removed": "North z<=8 above y4; all geometry outside crop omitted."},
    "room_cutaway": {"x": [84, 98], "y": [0, 8], "z": [6, 27],
                     "removed": "West x84 and north z6 walls above floor; roof/geometry outside crop omitted."},
    "changed_final_voxels": len(changes),
    "changed_coordinates": changes,
    "before_top": before.palette[before.grid[before.idx(86, 5, 11)]],
    "after_top": after.palette[after.grid[after.idx(86, 5, 11)]],
    "baseline_ascent": old_survey.coordinates(old_survey.path(LOWER, UPPER)),
    "after_ascent": survey.coordinates(survey.path(LOWER, UPPER)),
    "after_descent": survey.coordinates(survey.path(UPPER, LOWER)),
    "route_model": "GP2 interval/headroom/half-step rules, with half-cell horizontal centers resolving each straight native stair's low/high half. Entity width, steering and carpet thickness are not simulated. Tests reject perpendicular same-height stair neighbors.",
    "normalized_outside_stair_sha256_before": outside_hash(before),
    "normalized_outside_stair_sha256_after": outside_hash(after),
    "normalization": "Local coordinate, block identifier and sorted state properties; palette indices ignored.",
    "reference_files": {},
}
for name in ("page-034.png", "page-035.png", "page-036.png"):
    source = ROOT / "tmp/conformance/reference-guild" / name
    if source.exists():
        metadata["reference_files"][name] = hashlib.sha256(source.read_bytes()).hexdigest()
(OUT / "dorm-stair-render-scope.json").write_text(json.dumps(metadata, indent=2) + "\n")
print(json.dumps({"changed_final_voxels": len(changes), "before_ascent": bool(metadata["baseline_ascent"]),
                  "after_ascent": bool(metadata["after_ascent"]), "after_descent": bool(metadata["after_descent"]),
                  "outside_hash_match": metadata["normalized_outside_stair_sha256_before"] == metadata["normalized_outside_stair_sha256_after"]}))

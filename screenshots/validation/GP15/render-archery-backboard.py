"""GP15 authored board/target context; approximate colors, no native lighting."""
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
from test_guild_archery_backboard import BOARD, APPROACH, DESTINATIONS
from test_guild_map_table import voxel_changes
from test_guild_routes import cell, walking_graph, reachable

OUT = Path(__file__).resolve().parent
with patch.object(g, "build_guild_archery_backboard", lambda *_: None):
    before = g.build_guild_hall()
after = g.build_guild_hall()


def detail(vox, bounds, *, yaw, pitch):
    quads = []
    for x in range(bounds[0], bounds[1] + 1):
        for y in range(bounds[2], bounds[3] + 1):
            for z in range(bounds[4], bounds[5] + 1):
                name, states = cell(vox, x, y, z)
                if name == "minecraft:air":
                    continue
                tex = Image.new("RGBA", (2, 2), render.BLOCK_COLORS.get(name, (200, 120, 200)) + (255,))
                boxes = [((x, y, z), (1, 1, 1))]
                if name.endswith("_slab"):
                    upper = states.get("minecraft:vertical_half") == "top" or states.get("top_slot_bit")
                    boxes = [((x, y + (.5 if upper else 0), z), (1, .5, 1))]
                elif name.endswith("_carpet"):
                    boxes = [((x, y, z), (1, 1/16, 1))]
                elif name.endswith("_fence"):
                    # This crop has isolated torch posts, not connected rails.
                    boxes = [((x + .375, y, z + .375), (.25, 1, .25))]
                elif name == "minecraft:torch":
                    boxes = [((x + .4375, y, z + .4375), (.125, .625, .125))]
                for start, size in boxes:
                    quads.extend(render.cube_quads(start, size, (0, 0), tex,
                                                   glow=name in render.GLOW_BLOCKS))
    return render.render_quads(quads, size=(1200, 850), yaw=yaw, pitch=pitch, shadow=False)


for label, vox in (("before", before), ("after", after)):
    detail(vox, (79, 89, 0, 7, 29, 31), yaw=.08, pitch=.12).save(OUT / f"archery-board-{label}.png")
    detail(vox, (75, 98, 0, 8, 27, 47), yaw=.18, pitch=.50).save(OUT / f"archery-range-{label}.png")


def outside_hash(vox):
    h = hashlib.sha256()
    for x in range(vox.sx):
        for y in range(vox.sy):
            for z in range(vox.sz):
                if (x, y, z) in BOARD:
                    continue
                h.update(json.dumps([x, y, z, *cell(vox, x, y, z)], sort_keys=True,
                                    separators=(",", ":")).encode() + b"\n")
    return h.hexdigest()


changes = voxel_changes(before, after)
assert set(changes) == BOARD
routes = {}
for label, vox in (("before", before), ("after", after)):
    nodes = walking_graph(vox)
    found = reachable(vox, nodes, (10, 1., 42))
    routes[label] = {str(point): point in found for point in DESTINATIONS + tuple(APPROACH)}
    assert all(routes[label].values())
refs = ROOT / "tmp/conformance/reference-guild-additional"
source_files = ["altered-archery.jpg", "gamepressure-will.jpg"]
summary = {
    "baseline_scope": "Current complete Guild builder with only final scenic-backboard helper disabled.",
    "board_detail": {"bounds": [79, 89, 0, 7, 29, 31], "yaw": .08, "pitch": .12},
    "range_context": {"bounds": [75, 98, 0, 8, 27, 47], "yaw": .18, "pitch": .50},
    "render_limits": "Geometry outside each crop omitted. Flat approximate colors, half-height slabs, thin carpets and isolated torch/fence posts. Other furniture simplified; no native target textures, lighting, physics, collision or pathfinding execution.",
    "changed_final_voxels": len(changes),
    "changed_coordinates": changes,
    "changed_before_materials": sorted({cell(before, *point)[0] for point in changes}),
    "normalized_outside_board_sha256_before": outside_hash(before),
    "normalized_outside_board_sha256_after": outside_hash(after),
    "normalization": "Local coordinate, block identifier and sorted state properties; palette indices ignored.",
    "gate_routes": routes,
    "reference_files": {name: hashlib.sha256((refs / name).read_bytes()).hexdigest() for name in source_files},
    "authorship": "Original coarse block mountain/valley mosaic; no original screenshot pixels or extracted game assets used as pack art.",
    "engine_acceptance": "unrun",
}
assert summary["normalized_outside_board_sha256_before"] == summary["normalized_outside_board_sha256_after"]
(OUT / "archery-backboard-render-scope.json").write_text(json.dumps(summary, indent=2) + "\n")
print(json.dumps({"changed_final_voxels": len(changes), "outside_hash_match": True,
                  "all_surveyed_gate_routes_before_after": True, "engine_acceptance": "unrun"}))

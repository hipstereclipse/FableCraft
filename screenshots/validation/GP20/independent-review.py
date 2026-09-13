#!/usr/bin/env python3
"""Compare actual DP6/current Guild owners, decode outputs, and render six views.

No disabled helper or mirrored prototype substitutes for the predecessor. Pack
files are read only. Temporary serialized outputs go under ignored scratch.
"""
import ast
import contextlib
import copy
import hashlib
import io
import json
import math
from pathlib import Path
import struct
import subprocess
import sys
import types
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
TEMP = ROOT / "tmp/conformance/gp20/independent-review"
BASE = "274da7f779aec56562341a7dc75de58a8907b81c"
sys.path[:0] = [str(ROOT / "scripts"), str(ROOT / "scripts/tests")]
import gen_screenshots as renderer
from test_guild_routes import cell, clear, supported, walking_graph, reachable, GuildRoutes
from test_guild_dorm_routes import DormStairSurvey, LOWER, UPPER

EDIT = {(84, y, z) for y in (7, 8) for z in range(17, 22)}
INFILL = {(84, y, z) for y in (7, 8) for z in range(18, 21)}
NE = {(x, y, z) for x in range(84, 99) for y in range(14) for z in range(6, 29)}
FRONTS = [(85, 6., z) for z in range(17, 22)]
sha = lambda data: hashlib.sha256(data).hexdigest()


def committed(path):
    return subprocess.check_output(["git", "show", BASE + ":" + path], cwd=ROOT)


def decode(data):
    """Independent little-endian NBT reader, separate from the owner writer."""
    stream = io.BytesIO(data)
    def scalar(fmt):
        return struct.unpack("<" + fmt, stream.read(struct.calcsize("<" + fmt)))[0]
    def string():
        return stream.read(scalar("H")).decode("utf8")
    def value(tag):
        if tag in (1, 2, 3, 4, 5, 6):
            return scalar({1: "b", 2: "h", 3: "i", 4: "q", 5: "f", 6: "d"}[tag])
        if tag == 7: return list(stream.read(scalar("i")))
        if tag == 8: return string()
        if tag == 9:
            kind, count = scalar("B"), scalar("i")
            return [value(kind) for _ in range(count)]
        if tag == 10:
            result = {}
            while (kind := scalar("B")) != 0:
                name = string()
                result[name] = value(kind)
            return result
        if tag in (11, 12):
            return [scalar("i" if tag == 11 else "q") for _ in range(scalar("i"))]
        raise AssertionError("Unexpected NBT tag " + str(tag))
    assert scalar("B") == 10
    string()
    result = value(10)
    assert stream.tell() == len(data)
    return result


def voxel(nbt):
    sx, sy, sz = nbt["size"]
    # NBT stores this boolean as a byte. The existing independent stair model
    # requires Python False by identity; normalize only its documented bit here.
    # Raw decoded NBT is still compared separately for palette/state/version drift.
    palette = [(b["name"], {k: bool(v) if k == "upside_down_bit" and v in (0, 1) else v
        for k, v in b["states"].items()}) for b in nbt["structure"]["palette"]["default"]["block_palette"]]
    grid = nbt["structure"]["block_indices"][0]
    assert len(grid) == sx * sy * sz
    return types.SimpleNamespace(sx=sx, sy=sy, sz=sz, palette=palette, grid=grid,
        idx=lambda x, y, z: x*sy*sz + y*sz + z)


def generate(source, label):
    module = types.ModuleType("review_" + label)
    module.__file__ = str(ROOT / "scripts/gen_structures.py")
    exec(compile(source, module.__file__, "exec"), module.__dict__)
    module.BP = TEMP / label
    streams = []
    rng = module.rng
    def observed_rng(*keys):
        stream = rng(*keys)
        streams.append((keys, stream))
        return stream
    module.rng = observed_rng
    with contextlib.redirect_stdout(io.StringIO()):
        module.guild_hall()
    data = (module.BP / "structures/fc/guild_hall.mcstructure").read_bytes()
    return module, data, decode(data), [(keys, repr(s.getstate())) for keys, s in streams]


def exact_scope(before, after):
    changed = []
    for i, (old, new) in enumerate(zip(before.grid, after.grid)):
        if before.palette[old] == after.palette[new]: continue
        x, rem = divmod(i, after.sy*after.sz)
        y, z = divmod(rem, after.sz)
        p = (x, y, z)
        assert p in EDIT, ("Unexpected changed cell", p)
        assert before.palette[old] == ("minecraft:stone_bricks", {})
        expected = "minecraft:red_terracotta" if p in INFILL else "minecraft:dark_oak_planks"
        assert after.palette[new] == (expected, {}), p
        changed.append({"at": p, "before": before.palette[old], "after": after.palette[new]})
    assert {tuple(c["at"]) for c in changed} == EDIT
    return changed


def route_summary(v):
    nodes = walking_graph(v)
    ground = reachable(v, nodes, (10, 1., 42))
    upper = reachable(v, nodes, (90, 6., 12))
    assert (90, 1., 9) in ground
    assert all(p in upper and supported(v, *p) and clear(v, *p) for p in FRONTS)
    assert all(p in upper for p in [(91, 6., 20), (94, 6., 9), (94, 6., 20)])
    stair = DormStairSurvey(v)
    up, down = stair.path(LOWER, UPPER), stair.path(UPPER, LOWER)
    assert up and down
    tower = GuildRoutes()
    tower.check_run(tower.tower_run(), v)
    return {"nodes": nodes, "ground": ground, "upper": upper, "stair_nodes": stair.nodes,
            "ascent": stair.coordinates(up), "descent": stair.coordinates(down)}


def colors(source):
    tree = ast.parse(source)
    node = next(n for n in tree.body if isinstance(n, ast.Assign) and
        any(isinstance(t, ast.Name) and t.id == "BLOCK_COLORS" for t in n.targets))
    return ast.literal_eval(node.value)


def render_views(before, after):
    views = {
        "dorm-east-interior": {"bounds": [84, 89, 5, 8, 16, 22], "yaw": -math.pi/2+.22, "pitch": .3,
            "description": "Dormitory east face; ceiling/roof y9+ omitted, existing bed and deck retained"},
        "dorm-west-roof": {"bounds": [80, 84, 5, 10, 16, 22], "yaw": math.pi/2+.22, "pitch": .3,
            "description": "Reverse west face at a low angle; retained stores roof occludes the changed wall"},
        "dorm-west-roof-high": {"bounds": [80, 84, 5, 10, 16, 22], "yaw": math.pi/2+.22, "pitch": 1.,
            "description": "Reverse west face from above; existing roof and narrow recess retained"}}
    fontpath = Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")
    font, small = ImageFont.truetype(str(fontpath), 24), ImageFont.truetype(str(fontpath), 15)
    for view_name, view in views.items():
        for label, v in (("before", before), ("after", after)):
            b = view["bounds"]
            quads = []
            for x in range(b[0], b[1]+1):
                for y in range(b[2], b[3]+1):
                    for z in range(b[4], b[5]+1):
                        name, _ = cell(v, x, y, z)
                        if name == "minecraft:air": continue
                        assert name in renderer.BLOCK_COLORS, ("Missing schematic material", name)
                        texture = Image.new("RGBA", (2, 2), renderer.BLOCK_COLORS[name] + (255,))
                        size = (1, 1/16, 1) if name.endswith("_carpet") else (1, 1, 1)
                        quads.extend(renderer.cube_quads((x, y, z), size, (0, 0), texture))
            raw = renderer.render_quads(quads, size=(1280, 760), yaw=view["yaw"], pitch=view["pitch"], shadow=False)
            img = Image.new("RGB", (1280, 880), (240, 237, 231))
            img.paste(raw, (0, 75), raw)
            d = ImageDraw.Draw(img)
            d.text((28, 18), "Dormitory wall | " + view_name + " | " + label, font=font, fill=(32, 35, 39))
            d.text((28, 52), view["description"], font=small, fill=(67, 68, 71))
            d.text((28, 845), "Decoded owner-output schematic; approximate colors/full cubes except carpet. Native appearance remains unrun.", font=small, fill=(67, 68, 71))
            img.save(OUT / f"{view_name}-{label}.png")
    # Pillow may resolve the requested basename through a platform font path.
    actual_fontpath = Path(font.path)
    return views, {"requested_path": str(fontpath), "actual_path": str(actual_fontpath), "sha256": sha(actual_fontpath.read_bytes())}


def main():
    source_path = "scripts/gen_structures.py"
    old_source, new_source = committed(source_path), (ROOT / source_path).read_bytes()
    baseline, old_data, old_nbt, old_rng = generate(old_source, "before")
    current, new_data, new_nbt, new_rng = generate(new_source, "after")
    asset_path = "packs/Fablecraft_BP/structures/fc/guild_hall.mcstructure"
    assert old_data == committed(asset_path), "Actual predecessor owner does not match committed asset"
    assert new_data == (ROOT / asset_path).read_bytes(), "Actual current owner does not match shipped asset"
    before, after = voxel(old_nbt), voxel(new_nbt)
    assert baseline.GUILD_LAYOUT == current.GUILD_LAYOUT
    assert old_rng == new_rng
    assert old_nbt["size"] == new_nbt["size"] == [122, 30, 108]
    for key in ("format_version", "structure_world_origin"):
        assert old_nbt[key] == new_nbt[key]
    assert old_nbt["structure"]["entities"] == new_nbt["structure"]["entities"]
    assert old_nbt["structure"]["block_indices"][1] == new_nbt["structure"]["block_indices"][1]
    old_pal, new_pal = (n["structure"]["palette"]["default"] for n in (old_nbt, new_nbt))
    assert old_pal["block_position_data"] == new_pal["block_position_data"]
    assert new_pal["block_palette"][:-1] == old_pal["block_palette"]
    assert new_pal["block_palette"][-1] == {"name": "minecraft:red_terracotta", "states": {}, "version": 18176512}
    changes = exact_scope(before, after)
    assert all(cell(before, *p) == cell(after, *p) for p in NE - EDIT)
    maze = json.loads((ROOT / "screenshots/validation/GP17/maze-study-final-voxel-survey.json").read_text())
    assert all(cell(after, *r["at"]) == (r["name"], r["states"]) for r in maze["protected_cells"])
    windows = [p for p in sorted(NE) if cell(before, *p)[0] == "minecraft:glass_pane"]
    assert len(windows) == 10
    old_routes, new_routes = route_summary(before), route_summary(after)
    assert old_routes == new_routes, "Changed walking nodes, reachability or complete stair path"
    negative_results = []
    for at, name, check in (
        ((85, 6, 20), "minecraft:stone_bricks", lambda v: exact_scope(before, v)),
        ((86, 5, 11), "minecraft:air", lambda v: route_summary(v)),
        ((86, 6, 11), "minecraft:stone_bricks", lambda v: route_summary(v))):
        broken = copy.deepcopy(after)
        broken.palette.append((name, {}))
        broken.grid[broken.idx(*at)] = len(broken.palette)-1
        try:
            check(broken)
        except AssertionError:
            negative_results.append({"at": at, "injected": name, "result": "detected"})
        else:
            raise AssertionError(("Missed independent failure", at))
    renderer_path = "scripts/gen_screenshots.py"
    old_renderer, new_renderer = committed(renderer_path), (ROOT / renderer_path).read_bytes()
    old_colors, new_colors = colors(old_renderer), colors(new_renderer)
    assert new_colors == {**old_colors, "minecraft:red_terracotta": (143, 61, 47)}
    views, font = render_views(before, after)
    structure_paths = subprocess.check_output(["git", "ls-tree", "-r", "--name-only", BASE, "packs/Fablecraft_BP/structures"], cwd=ROOT, text=True).splitlines()
    structure_paths = [p for p in structure_paths if p.endswith(".mcstructure")]
    current_paths = sorted(str(p.relative_to(ROOT)) for p in (ROOT / "packs/Fablecraft_BP/structures").rglob("*.mcstructure"))
    assert sorted(structure_paths) == current_paths
    structure_deltas = [p for p in structure_paths if committed(p) != (ROOT / p).read_bytes()]
    assert structure_deltas == [asset_path]
    ref = next(r for r in json.loads((ROOT / "screenshots/validation/GP16/additional-online-references.json").read_text())["references"] if r["screenshot_id"] == "141296214")
    result = {"baseline_commit": BASE, "source_sha256": {"before": sha(old_source), "after": sha(new_source)},
        "renderer_sha256": {"before": sha(old_renderer), "after": sha(new_renderer)},
        "serialized_sha256": {"before": sha(old_data), "after": sha(new_data)},
        "both_serialized_owners_match_their_assets": True, "decoded_compared_cells": len(before.grid), "exact_changes": changes,
        "protected_ne_room_cells": len(NE-EDIT), "protected_ne_windows": windows, "protected_ne_y5_deck_cells": 345,
        "protected_maze_cells": len(maze["protected_cells"]), "all_existing_palette_entries_unchanged": True,
        "added_palette": new_pal["block_palette"][-1], "secondary_layer_entities_origin_metadata_unchanged": True,
        "layout_and_all_anchors_unchanged": True, "rng_instances": len(old_rng), "rng_calls_and_final_states_unchanged": True,
        "full_campus_walking_nodes_identical": True, "full_campus_walking_nodes": len(old_routes["nodes"]),
        "gate_reachable_nodes": len(old_routes["ground"]), "bedroom_reachable_nodes": len(old_routes["upper"]),
        "dorm_half_cell_stair_nodes": len(old_routes["stair_nodes"]), "dorm_ascent": old_routes["ascent"], "dorm_descent": old_routes["descent"],
        "wall_front_points": FRONTS, "independent_negatives": negative_results,
        "structure_assets_compared": len(structure_paths), "structure_asset_deltas": structure_deltas,
        "renderer_color_delta_only": {"minecraft:red_terracotta": [143, 61, 47]},
        "reference": ref, "views": views, "font": font,
        "image_hashes": {p.name: sha(p.read_bytes()) for p in sorted(OUT.glob("dorm-*.png"))},
        "render_limits": "Actual decoded before/after owner output, clipped per view. Flat approximate colors; carpets thin, bed/furniture/roof cells otherwise full cubes. No native textures, lighting, width-aware collision or movement simulation. Low west view occludes changed wall behind unchanged stores roof; high west view reveals red reverse face in existing roof recess.",
        "native_acceptance": "unrun"}
    (OUT / "independent-review-results.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"compared_cells": len(before.grid), "changed_cells": len(changes), "protected_ne": len(NE-EDIT),
        "protected_maze": len(maze["protected_cells"]), "walking_nodes_unchanged": len(old_routes["nodes"]),
        "independent_negatives": len(negative_results), "structure_assets_compared": len(structure_paths), "images": len(result["image_hashes"]),
        "shipped_sha256": sha(new_data), "native_acceptance": "unrun"}))


if __name__ == "__main__":
    main()

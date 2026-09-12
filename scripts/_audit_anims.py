"""Animation wiring audit. For every mob:
  - resolve its clip set the way emit_client_entity does (incl. the social-NPC override);
  - confirm each referenced clip exists in the emitted animation JSONs;
  - confirm every bone the clip animates exists in that mob's geometry (catches the
    beetle-class bug: animating bones the model lacks = silent no-op);
  - confirm controllers only reference short-names present in the mob's anim_map.
Run from REPO ROOT:  python scripts/_audit_anims.py
"""
import json
from pathlib import Path
import gen_resources as GR
import fc_mobs

ROOT = Path(__file__).resolve().parent.parent
RP = ROOT / "packs" / "Fablecraft_RP"

# ---- load emitted clips (both animation systems) ----
clips = {}
for f in ("animations/fc_shared.animation.json", "animations/fable_npc.animation.json",
          "animations/fable_player_emotes.animation.json"):
    p = RP / f
    if p.exists():
        clips.update(json.loads(p.read_text(encoding="utf-8")).get("animations", {}))

# ---- load controllers: short-names each controller plays ----
ctrl_json = json.loads((RP / "animation_controllers" / "fc.animation_controllers.json").read_text(encoding="utf-8"))
ctrl_anims = {}
for cid, cdef in ctrl_json["animation_controllers"].items():
    used = set()
    for st in cdef.get("states", {}).values():
        used.update(st.get("animations", []))
    ctrl_anims[cid] = used


def geo_bones(eid):
    p = RP / "models" / "entity" / f"{eid}.geo.json"
    if not p.exists():
        return None
    data = json.loads(p.read_text(encoding="utf-8"))
    bones = set()
    for g in data.get("minecraft:geometry", []):
        for b in g.get("bones", []):
            bones.add(b["name"])
    return bones


def clip_bones(clip_id):
    return set(clips.get(clip_id, {}).get("bones", {}).keys())


problems = []
for mob in fc_mobs.MOBS:
    eid = mob["id"]
    ce_path = RP / "entity" / f"{eid}.entity.json"
    if not ce_path.exists():
        problems.append(f"{eid}: no client-entity file")
        continue
    desc = json.loads(ce_path.read_text(encoding="utf-8"))["minecraft:client_entity"]["description"]
    anim_map = desc["animations"]          # short-name -> clip id OR controller id
    animate = desc["scripts"]["animate"]   # entries actually played
    bones = geo_bones(eid)
    if bones is None:
        problems.append(f"{eid}: no geometry file")
        continue

    # resolve every animate entry to the concrete clips it ultimately plays
    def resolve_clips(short):
        ref = anim_map.get(short)
        if ref is None:
            problems.append(f"{eid}: animate '{short}' not in animations map")
            return []
        if ref.startswith("controller."):
            out = []
            for s in ctrl_anims.get(ref, ()):
                out += resolve_clips(s)        # controller short-names index anim_map too
            return out
        if ref not in clips:
            problems.append(f"{eid}: clip '{ref}' (via '{short}') missing from emitted JSON")
            return []
        return [ref]

    played = []
    for entry in animate:
        played += resolve_clips(entry)

    # bone check across every clip this mob actually plays
    for clip_id in set(played):
        missing = clip_bones(clip_id) - bones
        if missing:
            problems.append(f"{eid}: clip {clip_id} animates bones absent from geometry: {sorted(missing)}")

if problems:
    print(f"=== {len(problems)} ANIMATION PROBLEMS ===")
    for p in problems:
        print("  " + p)
else:
    print(f"OK — all {len(fc_mobs.MOBS)} mobs: every played clip exists and only animates bones the model has.")

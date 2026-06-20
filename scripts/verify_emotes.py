"""Static audit for the generated Fable expression and NPC animation system."""
import json
import sys
from pathlib import Path

from fc_emotes import EMOTES
from fc_lib import BP, RP, ROOT
from fc_mobs import MOBS


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def main():
    errors = []
    registry_path = BP / "config" / "fable_emotes.json"
    if not registry_path.exists():
        errors.append("missing BP/config/fable_emotes.json")
        registry = {"emotes": []}
    else:
        registry = load(registry_path)

    actual = registry.get("emotes", [])
    expected_ids = [entry["id"] for entry in EMOTES]
    actual_ids = [entry.get("id") for entry in actual]
    if len(actual) != 31:
        errors.append(f"registry contains {len(actual)} expressions, expected 31")
    if actual_ids != expected_ids:
        errors.append("generated expression IDs do not match scripts/fc_emotes.py")
    if len(set(actual_ids)) != len(actual_ids):
        errors.append("duplicate expression IDs")

    player_anim_path = RP / "animations" / "fable_player_emotes.animation.json"
    player_anims = load(player_anim_path).get("animations", {}) if player_anim_path.exists() else {}
    for entry in EMOTES:
        if entry["animation"] not in player_anims:
            errors.append(f"missing player animation {entry['animation']}")
            continue
        bones = player_anims[entry["animation"]].get("bones", {})
        required_player_bones = {"rightArm", "leftArm", "rightLeg", "leftLeg", "body", "head"}
        missing = required_player_bones - set(bones)
        if missing:
            errors.append(f"{entry['id']}: missing/case-invalid player bones {sorted(missing)}")
    if len(player_anims) != 31:
        errors.append(f"player animation file contains {len(player_anims)} clips, expected 31")

    npc_anim_path = RP / "animations" / "fable_npc.animation.json"
    npc_anims = load(npc_anim_path).get("animations", {}) if npc_anim_path.exists() else {}
    required_npc_anims = {
        "animation.npc.idle", "animation.npc.walk", "animation.npc.run",
        "animation.npc.cower", "animation.npc.laugh", "animation.npc.clap",
        "animation.npc.cheer", "animation.npc.angry", "animation.npc.spar",
        "animation.npc.block", "animation.npc.archery_shot",
    }
    for animation in sorted(required_npc_anims - set(npc_anims)):
        errors.append(f"missing NPC animation {animation}")

    controller_path = RP / "animation_controllers" / "fc.animation_controllers.json"
    controllers = load(controller_path).get("animation_controllers", {}) if controller_path.exists() else {}
    movement = controllers.get("controller.animation.npc.move", {})
    states = movement.get("states", {})
    if set(states) != {"idle", "walk", "run"}:
        errors.append("controller.animation.npc.move must contain idle, walk and run states")

    geometry_path = RP / "models" / "entity" / "fable_npc.geo.json"
    if geometry_path.exists():
        bones = {
            bone["name"]
            for bone in load(geometry_path)["minecraft:geometry"][0].get("bones", [])
        }
        required_bones = {"head", "body", "arm_r", "arm_l", "leg_r", "leg_l"}
        if not required_bones.issubset(bones):
            errors.append(f"reference NPC geometry missing bones: {required_bones - bones}")
    else:
        errors.append("missing models/entity/fable_npc.geo.json")

    social_mobs = [
        mob for mob in MOBS
        if mob.get("behavior") in ("npc", "guard") or mob["id"] == "mercenary"
    ]
    for mob in social_mobs:
        entity_path = BP / "entities" / f"{mob['id']}.json"
        client_path = RP / "entity" / f"{mob['id']}.entity.json"
        if not entity_path.exists() or not client_path.exists():
            errors.append(f"{mob['id']}: missing behavior or client entity")
            continue
        entity = load(entity_path)["minecraft:entity"]
        properties = entity["description"].get("properties", {})
        for prop in ("fc:love_hate", "fc:fear_funny", "fc:ugly_attractive"):
            if prop not in properties:
                errors.append(f"{mob['id']}: missing property {prop}")
        events = entity.get("events", {})
        for event in ("fc:react_flee", "fc:react_follow", "fc:react_watch",
                      "fc:react_attack", "fc:react_neutral"):
            if event not in events:
                errors.append(f"{mob['id']}: missing event {event}")
        if mob["plan"][0] == "humanoid":
            client = load(client_path)["minecraft:client_entity"]["description"]
            animations = client.get("animations", {})
            if animations.get("ctrl_move") != "controller.animation.npc.move":
                errors.append(f"{mob['id']}: not wired to controller.animation.npc.move")
            for key in ("idle", "walk", "run"):
                if key not in animations:
                    errors.append(f"{mob['id']}: missing client animation key {key}")

    runtime_path = BP / "scripts" / "fable_emotes.js"
    runtime = runtime_path.read_text(encoding="utf-8") if runtime_path.exists() else ""
    for marker in (
        "world.afterEvents.playerEmote.subscribe",
        'player.camera.setCamera("minecraft:third_person")',
        "player.camera.clear()",
        'name: "fable:emote"',
        'name: "fable:npc_stats"',
        'name: "fable:npc_react"',
        'name: "fable:animate"',
        "runFableEmoteTests",
        "runFableVisualDemo",
    ):
        if marker not in runtime:
            errors.append(f"runtime missing marker: {marker}")

    manifest = load(BP / "manifest.json")
    server_dep = next(
        (dep for dep in manifest.get("dependencies", [])
         if dep.get("module_name") == "@minecraft/server"),
        {},
    )
    server_version = str(server_dep.get("version", ""))
    if server_version not in {"2.1.0"}:
        errors.append("@minecraft/server 2.1.0 is required for custom commands")

    if errors:
        print("Fable expression audit FAILED")
        for error in errors:
            print(f"  ERROR {error}")
        return 1
    print(
        f"Fable expression audit passed: 31 expressions, {len(social_mobs)} social NPCs, "
        f"{len(required_npc_anims)} NPC clips"
    )
    print(f"registry: {registry_path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

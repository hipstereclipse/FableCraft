"""Audit entity-local animation clips, bones, controller gates and variable drivers.

Run from the repository root: python scripts/_audit_anims.py
No pack mutation. Nonzero exit on any problem. Engine attack_time is accepted only
for an entity with a melee goal, not for arbitrary similarly named variables.
See docs/ANIMATION_AUDIT.md for official sources and static-analysis limitations.
"""
import argparse
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
VAR = re.compile(r'\b(?:variable|v)\.([a-zA-Z_]\w*)')
ASSIGN = re.compile(r'\b(?:variable|v)\.([a-zA-Z_]\w*)\s*=(?!=)\s*([^;]+)')
MELEE_GOALS = {'minecraft:behavior.melee_attack', 'minecraft:behavior.melee_box_attack',
               'minecraft:behavior.delayed_attack'}


def strings(value):
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for v in value.values():
            yield from strings(v)
    elif isinstance(value, list):
        for v in value:
            yield from strings(v)


def entries(value):
    """Animation short-name entries can be bare or weighted/conditional objects."""
    for entry in value:
        if isinstance(entry, str):
            yield entry, None
        elif isinstance(entry, dict):
            yield from entry.items()


def expressions(value):
    # JSON keys are identifiers, not executable expressions. Strip Molang comments.
    return [re.sub(r'//[^\n]*', '', s) for s in strings(value)]


def engine_bindings(behavior):
    components = [behavior.get('components', {}), *behavior.get('component_groups', {}).values()]
    return {'attack_time'} if any(MELEE_GOALS.intersection(c) for c in components) else set()


def audit_entity(desc, behavior, controllers, clips, bones):
    problems = []
    label = desc['identifier']
    anim_map = desc.get('animations', {})
    assignments = {}
    gates = []
    visited = set()
    played = set()

    def collect_drivers(value):
        for expression in expressions(value):
            for name, rhs in ASSIGN.findall(expression):
                assignments.setdefault(name, []).append(rhs)

    def collect_gate(expression):
        if isinstance(expression, str):
            gates.append(expression)

    collect_drivers(desc.get('scripts', {}))

    def visit(short, stack=()):
        ref = anim_map.get(short)
        if ref is None:
            problems.append(f"{label}: animation short-name {short!r} missing")
            return
        if ref in stack:
            problems.append(f'{label}: controller cycle: {" -> ".join((*stack, ref))}')
            return
        if ref in visited:
            return
        visited.add(ref)
        if ref.startswith('controller.'):
            definition = controllers.get(ref)
            if definition is None:
                problems.append(f'{label}: missing controller {ref}')
                return
            states = definition.get('states', {})
            initial = definition.get('initial_state', 'default')
            if initial not in states:
                problems.append(f'{label}: {ref} missing initial state {initial}')
                return
            # Only reachable states can supply a driver. Dead-state assignments
            # must not make a gate from the initial state appear valid.
            pending = [initial]
            seen = set()
            while pending:
                state = pending.pop()
                if state in seen:
                    continue
                seen.add(state)
                body = states.get(state)
                if body is None:
                    problems.append(f'{label}: {ref} transition targets missing state {state}')
                    continue
                collect_drivers(body.get('on_entry', []))
                collect_drivers(body.get('on_exit', []))
                for child, condition in entries(body.get('animations', [])):
                    collect_gate(condition)
                    visit(child, (*stack, ref))
                for transition in body.get('transitions', []):
                    for destination, condition in transition.items():
                        collect_gate(condition)
                        pending.append(destination)
                # Controller variables are valid driver declarations with an
                # input expression and an optional remap_curve.
                for name, value in body.get('variables', {}).items():
                    name = name.removeprefix('variable.').removeprefix('v.')
                    rhs = value.get('input', '') if isinstance(value, dict) else value
                    if isinstance(rhs, str):
                        assignments.setdefault(name, []).append(rhs)
        else:
            clip = clips.get(ref)
            if clip is None:
                problems.append(f'{label}: missing clip {ref}')
                return
            played.add(ref)
            collect_drivers(clip)

    for short, condition in entries(desc.get('scripts', {}).get('animate', [])):
        collect_gate(condition)
        visit(short)
    # Older client-entity controller declarations can coexist with scripts.animate.
    for group in desc.get('animation_controllers', []):
        for short, ref in group.items():
            anim_map = {**anim_map, short: ref}
            visit(short)

    bindings = engine_bindings(behavior)

    def driven(name, stack=()):
        if name in stack:
            return False
        if name in bindings:
            # Shadowing attack_time with a constant would defeat engine swings.
            return name not in assignments
        for rhs in assignments.get(name, []):
            refs = set(VAR.findall(rhs))
            if all(driven(dep, (*stack, name)) for dep in refs):
                return True
        return False

    required = {name for gate in gates for name in VAR.findall(gate)}
    for name in sorted(required):
        if not driven(name):
            reason = 'no compatible melee goal supplies engine swing progress' if name == 'attack_time' else 'no entity-local assignment/dependency driver'
            problems.append(f'{label}: undriven gate variable.{name}: {reason}')
    for ref in sorted(played):
        missing = set(clips[ref].get('bones', {})) - bones
        if missing:
            problems.append(f'{label}: clip {ref} animates absent bones {sorted(missing)}')
    for expression in [*gates, *expressions({key: clips[key] for key in played}),
                       *expressions(desc.get('scripts', {}))]:
        if re.search(r'\b(?:query|q)\.attack_time\b', expression):
            problems.append(f'{label}: invalid query.attack_time; use the engine variable')
            break
    return problems


def audit(root=ROOT):
    rp = root / 'packs/Fablecraft_RP'
    bp = root / 'packs/Fablecraft_BP'
    controllers, clips, geometries, behaviors = {}, {}, {}, {}
    for path in (rp / 'animation_controllers').glob('*.json'):
        controllers.update(json.loads(path.read_text())['animation_controllers'])
    for path in (rp / 'animations').glob('*.json'):
        clips.update(json.loads(path.read_text()).get('animations', {}))
    for path in (rp / 'models/entity').glob('*.json'):
        for geo in json.loads(path.read_text()).get('minecraft:geometry', []):
            geometries[geo['description']['identifier']] = {bone['name'] for bone in geo['bones']}
    for path in (bp / 'entities').glob('*.json'):
        data = json.loads(path.read_text()).get('minecraft:entity', {})
        behaviors[data.get('description', {}).get('identifier')] = data
    problems, count = [], 0
    for path in sorted((rp / 'entity').glob('*.json')):
        count += 1
        desc = json.loads(path.read_text())['minecraft:client_entity']['description']
        bones = set()
        for ref in desc.get('geometry', {}).values():
            if ref not in geometries:
                problems.append(f'{desc["identifier"]}: missing geometry {ref}')
            bones |= geometries.get(ref, set())
        problems += audit_entity(desc, behaviors.get(desc['identifier'], {}), controllers, clips, bones)
    if count == 0:
        problems.append('no client entities found')
    return count, problems


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT, help='Isolated pack tree for negative tests')
    args = parser.parse_args()
    count, problems = audit(args.root)
    if problems:
        print(f'=== {len(problems)} ANIMATION PROBLEMS ===')
        for problem in problems:
            print('  ' + problem)
        return 1
    print(f'OK — {count} client entities: reachable clips/bones/controllers and entity-local gate drivers resolve.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

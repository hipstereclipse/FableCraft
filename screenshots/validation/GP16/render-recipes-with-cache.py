"""Rerender recipes/forge sheets using unchanged owner code and a retained cache.

Run from the reviewed snapshot after supplying the ignored vanilla cache recorded
in vanilla-cache-provenance.json. No external Fable pixels or pack writes occur.
"""
import ast
from pathlib import Path
import sys

sys.path.insert(0, str(Path.cwd() / "scripts"))
import gen_screenshots as owner

owner.SHOTS = Path("tmp/GP16-full-screenshots")
cards = owner.render_recipe_cards(owner.fc_data.all_items())
tree = ast.parse(Path("scripts/gen_screenshots.py").read_text())
main = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "main")
def assigns(node, name):
    return isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == name for t in node.targets)
start = next(i for i, n in enumerate(main.body) if assigns(n, "weapon_ids"))
end = next(i for i, n in enumerate(main.body) if assigns(n, "item_img"))
scope = dict(vars(owner), recipe_cards=cards)
exec(compile(ast.Module(body=main.body[start:end], type_ignores=[]), "<owned forge sheets>", "exec"), scope)
print(f"PASS: {len(cards)} recipe cards and four forge galleries rendered by unchanged owner code")

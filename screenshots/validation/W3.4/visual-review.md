# W3.4 visual review

Inspected actual-owner exterior, rear overview and shack cutaway: a timber bridge crosses the
dry ravine, rails protect the span, and the east-bank shack adjoins stairs to
the lower path. The front face has readable eyes/nose/mouth but is a simple
upright slab. Trees, sheer banks and shack are regular block silhouettes.
No magenta palette entries or clipped writes; route evidence is separate.

The small [TLC toll guide shot](https://www.gamepressure.com/fablethelostchapters/bandit-toll/zc39)
shows wooded approach, stonework and rough timber, with a payment prompt.
It does not show the bridge/ravine/face. This supplies material context only;
whole-POI canon grade and reference comparison remain pending. Sparse foliage,
uniform cliff walls and static slab face are visible gaps. The implementation
has no toll payment, surrender/fleeing, quest completion or Arboretum challenge.

Six regression groups pass, including actual grass/rock scatter and independent
broken-deck, blocked-shack and obstructed-stair fixtures. Floor/head clearance
and supported routes do not prove Bedrock stair/fence collisions. All engine
checks remain unrun. Full render outcome is in full-render-summary.json.

The shack cutaway removes only x26..36,z24..35,y>=9 for diagnosis. It shows
the single chest, clear interior and adjacent descending stair trench. It is
not emitted geometry. All 27 local gates and explicit spell/syntax checks pass.
A second diagnostic crops x26..36,z24..35,y5..8 into a temporary voxel view
so the chest/lantern and doorway can be inspected closely (gorge-shack-detail.png).

Full all-category pipeline exited 0: 51 mobs, 55 item cards, 31 structures,
130 recipes and 13 galleries. C2 separately covers all 34 structure assets.

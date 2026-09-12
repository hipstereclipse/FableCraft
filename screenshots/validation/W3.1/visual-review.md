# W3.1 visual review

Inspected actual-owner exterior, courtyard cutaway (y=5..8) and chamber cutaway
(x/z=16..32,y=0..4). Exterior has continuous ramparts, paired cell roofs and a
higher office tower. Cutaways show four cell interiors, clear central lanes,
barracks/torture room and an avoidable water basin. The repeated box forms and
plain masonry need refinement. Diagnostic crops are not emitted geometry.

Two TLC guide images were inspected in ignored developer storage. Office props
are denser in the reference; the reference chamber is vast, round and domed with
waterfall and Kraken. Our flat, small rectangular chamber remains a large visual
gap. Reference URLs/hashes and provenance limits are in reference-candidates.json.
No canon grade assigned; original exterior comparison and all engine checks pending.

Seven regression groups pass after moving two obstructed rear entrances to the
north cross-lane. The original red route output remains in first-bargate-tests.log.
Independent closed-cell and blocked-chamber fixtures now fail the real route
assertions. All guards/chests have clear tested anchors. No prison quest, equipment
transaction, rescue, unique reward, cell gate mechanic or Kraken was implemented.

All 24 local gates and explicit spell/syntax commands pass. Full all-category
rendering exited 0: 51 mobs, 55 item cards, 28 structures, 130 recipe cards and
13 galleries. Primary card and broad audit row come from that pass; C2 separately
covers all 31 assets. Full-cell route tests allow one-block height changes, so they
do not prove jump-free movement at the chamber stair's top landing. Engine stair
and partial-block collision checks remain explicitly unrun.

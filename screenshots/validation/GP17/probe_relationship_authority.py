#!/usr/bin/env python3
"""Run the committed actual-source relationship fixture against current or saved main.js."""
import argparse
import os
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[3]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--main', type=Path, default=ROOT / 'packs/Fablecraft_BP/scripts/main.js')
args = parser.parse_args()
fixture = (ROOT / 'scripts/tests/guild_relationships.test.mjs').read_text().split('// Capture pre-fix observations', 1)[0]
probe = r'''
const observations=[];
for(const deferredProperties of [false,true]){
  const f=await fixture({deferredProperties}),a=f.player('hero-a'),b=f.player('hero-b'),n=f.npc('', 'resident');
  f.runtime.propose(a,n);f.runtime.propose(b,n);f.forms[0].resolve(0);f.forms[1].resolve(0);f.flushProperties();
  observations.push({case:'two_pending_proposals',deferredProperties,owner:n.props.get('fc_spouse_player'),rings:[f.rings(a),f.rings(b)],
    spouses:[a.props.get('fc_spouses')??null,b.props.get('fc_spouses')??null],marriageRewards:weddingEvents(f).length});
}
{
  const f=await fixture(),p=f.player('hero-a'),n=f.npc(p.id,'resident');setSpouses(p,['saved-other',n.id]);
  f.runtime.spouse(p,n);f.forms[0].resolve(4);n.props.set('fc_spouse_player','hero-b');f.operations.length=0;f.forms[1].resolve(0);
  observations.push({case:'nested_divorce_owner_changed',owner:n.props.get('fc_spouse_player'),married:n.sync.get('fc:married'),spouses:p.props.get('fc_spouses'),mutations:f.operations});
}
{
  const f=await fixture(),p=f.player('hero-a'),n=f.npc(p.id,'resident');setSpouses(p,[n.id]);f.ctl.beginPass([n]);
  const token=f.ctl.acquire(n,'fc_train_range',n.location,{x:83.5,y:2.45,z:34.5});f.runtime.spouse(p,n);n.props.set('fc_spouse_player','hero-b');
  f.operations.length=0;f.forms[0].resolve(1);
  observations.push({case:'stale_spouse_follow',trainingStillActive:f.ctl.isActive(n,token),following:n.hasTag('fc_guild_following'),mutations:f.operations});
}
{
  const f=await fixture({deferredProperties:true}),p=f.player('hero-a'),n=f.npc('','resident');setSpouses(p,['saved-other']);
  f.inject(p.id,'setDynamicProperty:fc_spouses','after');let failure=null;try{f.runtime.marry(p,n);}catch(error){failure=error.message;}f.flushProperties();
  observations.push({case:'failed_list_write_after_mutation_next_tick',failure,owner:n.props.get('fc_spouse_player'),married:n.sync.get('fc:married'),love:n.sync.get('fc:love_hate'),
    spouses:p.props.get('fc_spouses'),rings:f.rings(p),marriageRewards:weddingEvents(f).length});
}
{
  const f=await fixture(),p=f.player('hero-a'),n=f.npc('','resident');p.items.delete(2);f.runtime.propose(p,n);f.forms[0].resolve(0);
  observations.push({case:'normal_single_nonstackable_ring',owner:n.props.get('fc_spouse_player'),rings:f.rings(p),marriageRewards:weddingEvents(f).length});
}
const {createHash}=await import('node:crypto');
const hash=s=>createHash('sha256').update(s).digest('hex');
console.log(JSON.stringify({mainSourceSha256:hash(source),trainingSourceSha256:hash(training),observations},null,2));
'''
runtime = ROOT / 'tmp/conformance/gp17/probe-runtime.mjs'
runtime.parent.mkdir(parents=True, exist_ok=True)
runtime.write_text(fixture + probe)
env = dict(os.environ, FC_RELATIONSHIP_SOURCE=str(args.main.resolve()))
result = subprocess.run(['node', '--experimental-vm-modules', str(runtime)], cwd=ROOT, env=env, text=True)
raise SystemExit(result.returncode)

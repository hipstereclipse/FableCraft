// GP1 read-only probe: execute the actual Guild scheduler/roster in a small VM.
// This records baseline control flow, not Bedrock movement or damage behavior.
// Run from repository root: node screenshots/validation/GP1/npc/baseline-probe.mjs
import fs from 'node:fs';
import vm from 'node:vm';
import crypto from 'node:crypto';

const source = fs.readFileSync('packs/Fablecraft_BP/scripts/main.js', 'utf8');
const start = source.indexOf('const APPRENTICE_TYPES =');
const end = source.indexOf('// Combat multiplier + kill XP', start);
const guildStart = source.indexOf('const GUILD = Object.freeze(');
const guildEnd = source.indexOf('\n});', guildStart) + 4;
const behavior = JSON.parse(fs.readFileSync('packs/Fablecraft_BP/entities/guild_apprentice_skill.json'))['minecraft:entity'];
let serial = 0;
function fixture() {
  const entities = [], intervals = [], timers = [], spawns = [];
  let time = 1000;
  const properties = new Map([['fc_guild_placed', true]]);
  const dimension = {
    getEntities(q) {
      return entities.filter(e => !e.removed && (!q.type || q.type === e.typeId)
        && (!q.tags || q.tags.every(t => e.tags.has(t)))
        && (!q.location || Math.hypot(e.location.x - q.location.x,
          e.location.y - q.location.y, e.location.z - q.location.z) <= q.maxDistance));
    },
    spawnEntity(type, loc) { const e = entity(type, loc); spawns.push(e); return e; },
    playSound() {}, spawnParticle() {},
  };
  function entity(type, location) {
    const e = {
      typeId: type, location: {...location}, id: `probe-${++serial}`, tags: new Set(),
      calls: [], teleports: 0, frozen: false, dimension,
      getTags() { return [...this.tags]; }, addTag(t) { this.tags.add(t); },
      removeTag(t) { this.tags.delete(t); }, hasTag(t) { return this.tags.has(t); },
      triggerEvent(event) {
        this.calls.push(event);
        if (event === this.failEvent) throw new Error('Injected component event failure');
        if (event === 'fc:guild_training_start') this.frozen = true;
        if (event === 'fc:guild_training_stop') this.frozen = false;
      },
      teleport(loc) { this.teleports++; this.location = {...loc}; },
      playAnimation() {}, remove() { this.removed = true; },
      getComponent() { return {shoot() {}}; },
    };
    entities.push(e); return e;
  }
  const context = vm.createContext({
    world: {getDynamicProperty: key => properties.get(key), setDynamicProperty: (key, val) => properties.set(key, val),
      getTimeOfDay: () => time, getPlayers: () => [{location: {x:20,y:1,z:42},dimension:{id:'minecraft:overworld'}}]},
    system: {currentTick: 10, runInterval: (fn, ticks) => intervals.push({fn,ticks}),
      runTimeout: (fn,ticks) => timers.push({fn,ticks})},
    OW: () => dimension, guildBounds: () => ({base:{x:0,y:0,z:0}}),
    isInsideGuild: () => true, trySpawn: (dim,type,loc) => dim.spawnEntity(type,loc),
  });
  vm.runInContext(`const TICKS = () => system.currentTick;\n${source.slice(guildStart,guildEnd)}\n${source.slice(start,end)}`,context);
  vm.runInContext('clearGuildRingScarecrows = repairGuildDemonApproach = repairGuildTerrain = repairGuildSkirtVegetation = () => {};',context);
  return {context, entity, entities, intervals, timers, spawns,
    train: () => intervals.find(x=>x.ticks === 10).fn(),
    roster: () => intervals.find(x=>x.ticks === 200).fn(),
    time: value => {time=value;},
    evaluate: code => vm.runInContext(code,context)};
}
function residents(f) {
  const roster = f.evaluate('GUILD_ROSTER.map(e => ({...e, homes: e.homes.map(h => ({...h}))}))');
  for (const entry of roster) for (const h of entry.homes) {
    const e=f.entity(entry.type,{x:h.x,y:h.y??1,z:h.z});
    if (entry.tag) e.addTag(entry.tag);
  }
}
const observations = {};
{
  const f=fixture(); residents(f);
  for(let tick=10;tick<=100;tick+=10) {f.context.system.currentTick=tick;f.train();}
  observations.station_teleports_over_100_ticks=f.entities.filter(e=>e.teleports).map(e=>({type:e.typeId,teleports:e.teleports}));
  f.context.system.currentTick=1200; f.train();
  observations.rest_transition=f.entities.filter(e=>e.teleports).map(e=>({type:e.typeId,total_teleports:e.teleports,frozen:e.frozen,location:e.location}));
}
{
  const f=fixture(); residents(f); f.train();
  const e=f.entities.find(e=>e.hasTag('fc_train_ring_a'));
  e.failEvent='fc:guild_training_stop';f.time(13000);f.train();f.train();
  observations.failed_stop={tags:e.getTags(),frozen_in_component_stub:e.frozen,stop_attempts:e.calls.filter(v=>v==='fc:guild_training_stop').length};
}
{
  const f=fixture(); residents(f);f.train();
  const a=f.entities.find(e=>e.hasTag('fc_train_ring_a'));
  f.entities.filter(e=>e.typeId.startsWith('fc:guild_apprentice') && e!==a && !e.hasTag('fc_train_range')).forEach(e=>e.removed=true);
  f.train();
  observations.missing_partner={tags:a.getTags(),frozen_in_component_stub:a.frozen};
}
{
  const f=fixture();residents(f);
  const absent=f.entities.find(e=>e.typeId==='fc:guild_apprentice_will');
  absent.location={x:400,y:1,z:400}; // A resident following one Hero; another Hero remains in Guild.
  f.roster();
  absent.location={x:26,y:1,z:24};f.roster();
  observations.resident_left_and_returned={spawned:f.spawns.map(e=>e.typeId),total_will_residents:f.entities.filter(e=>e.typeId==='fc:guild_apprentice_will').length};
}
{
  const f=fixture();residents(f);
  f.entities.find(e=>e.typeId==='fc:trader').removed=true;
  f.entity('fc:trader',{x:130,y:1,z:42});f.roster();
  observations.foreign_trader_suppresses_repair={spawned_traders:f.spawns.filter(e=>e.typeId==='fc:trader').length};
}
{
  const f=fixture();residents(f);f.train();
  const skill=f.entities.find(e=>e.hasTag('fc_train_range'));
  skill.addTag('fc_aggravated'); // Hit between station tick and delayed release.
  f.timers.find(t=>t.ticks===16).fn();
  observations.delayed_release_after_aggravation={training_arrows:f.spawns.filter(e=>e.typeId==='minecraft:arrow').length};
}
observations.reaction_target_filter=behavior.component_groups['fc:reaction_attack']['minecraft:behavior.nearest_attackable_target'].entity_types;
observations.training_arrow_tag_references=source.split('fc_training_arrow').length-1;
console.log(JSON.stringify({kind:'offline_baseline_control_flow_probe',main_js_sha256:crypto.createHash('sha256').update(source).digest('hex'),
  limitations:'Component success/failure is stubbed; no engine AI, collision, damage, navigation, or save-loading claims.',observations},null,2));

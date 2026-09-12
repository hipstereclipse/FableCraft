// Frozen pre-GP7 production helpers; no live world, assets or source are written.
// Input: current generator crop supplied by run_probe.py.
import fs from 'node:fs';
import vm from 'node:vm';
import { createHash } from 'node:crypto';

const folder = new URL('./', import.meta.url);
const source = fs.readFileSync(new URL('retired_helpers.js', folder), 'utf8');
const manifest = JSON.parse(fs.readFileSync(new URL('source-manifest.json', folder), 'utf8'));
if (createHash('sha256').update(source).digest('hex') !== manifest.excerpt_sha256) throw Error('Frozen helper hash changed');
const generated = JSON.parse(fs.readFileSync(0, 'utf8'));

function fixture(initial = []) {
  const props = new Map(), blocks = new Map(initial.map(([x,y,z,id]) => [`${x},${y},${z}`, id]));
  const writes = [], changes = [];
  let unavailable;
  const dimension = { getBlock(point) {
    const key = `${point.x},${point.y},${point.z}`;
    if (key === unavailable) return undefined;
    return { get typeId() { return blocks.get(key) ?? 'minecraft:air'; }, setType(value) {
      const before = blocks.get(key) ?? 'minecraft:air';
      writes.push(key);
      if (before !== value) changes.push({ position: key.split(',').map(Number), before, after: value });
      blocks.set(key, value);
    } };
  } };
  const context = vm.createContext({ GUILD: { demon: { x:66,z:96 }, dueling: { x:101,z:61 } },
    world: { getDynamicProperty: key => props.get(key), setDynamicProperty: (key,value) => props.set(key,value) } });
  vm.runInContext(source + '\nglobalThis.repair=repairGuildDemonApproach;', context);
  return { props, blocks, writes, changes, unavailable(key) { unavailable = key; },
    run() { context.repair(dimension, { x:0,y:0,z:0 }); } };
}

const foreign = [[66,0,90,'minecraft:diamond_block'], [66,1,90,'minecraft:chest']];
const simple = fixture(foreign); simple.run();
const retry = fixture(foreign); retry.unavailable('65,0,84'); retry.run();
const firstWrites = retry.writes.length;
retry.blocks.set('66,1,90', 'minecraft:barrel'); retry.run();
const current = fixture(generated); current.run();
console.log(JSON.stringify({
  scope: 'Frozen actual production helper in memory; not Bedrock execution.',
  missingLegacyFlag: { writes: simple.writes.length, floor: simple.blocks.get('66,0,90'),
    container: simple.blocks.get('66,1,90'), done: simple.props.get('fc_guild_demon_approach_v2') },
  unavailableOtherCell: { firstWrites, retryWrites: retry.writes.length - firstWrites,
    replacementContainer: retry.blocks.get('66,1,90'), done: retry.props.get('fc_guild_demon_approach_v2') ?? false },
  currentGenerator: { changes: current.changes,
    onlyCobblePaletteChanges: current.changes.every(row => [row.before,row.after].every(id =>
      ['minecraft:cobblestone','minecraft:mossy_cobblestone'].includes(id))) },
}, null, 2));

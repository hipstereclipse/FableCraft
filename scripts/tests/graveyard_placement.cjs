// Run the actual scatter function against the generated graveyard's voxel data.
const fs = require('node:fs');
const vm = require('node:vm');
const assert = require('node:assert/strict');
const espree = require('espree');
const readTables = require('../structure_tables.cjs');
const sourcePath = 'packs/Fablecraft_BP/scripts/main.js';
const source = fs.readFileSync(sourcePath, 'utf8');
const tree = espree.parse(source, { ecmaVersion: 'latest', sourceType: 'module', range: true });
const node = tree.body.find(n => n.type === 'FunctionDeclaration' && n.id.name === 'maybePlace');
const fn = source.slice(...node.range);
const pick = readTables(sourcePath).STRUCTS.find(s => s.id === 'fc:graveyard');
const voxels = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
for (const surface of ['grass', 'dark']) {
  let origin, saved = false, placements = 0, doors = 0, travel = 0;
  const spawns = [], loot = [];
  const dim = {};
  const context = {
    REGION: 160, Math,
    world: { getDynamicProperty: () => saved, setDynamicProperty: () => { saved = true; },
      structureManager: { place: (id, dimension, at) => { assert.equal(id, pick.id); assert.equal(dimension, dim); origin = at; placements++; } } },
    hash2: () => 0, pickStruct: () => pick, sampleGroundY: () => 65,
    surfMatch: (allowed, actual) => allowed.includes(actual), surfaceCategory: () => surface,
    tooCloseToExisting: () => false, recordPlace: () => {}, blendTerrain: () => {}, skirtTerrain: () => {},
    fillLootChests: (...args) => loot.push(args),
    trySpawn: (dimension, type, at) => { assert.equal(dimension, dim); spawns.push({ type, at }); },
    ensureDemonDoor: () => { doors++; }, recordDemonDoor: () => { doors++; },
    registerCullis: () => { travel++; }, cullisLabel: () => 'unexpected',
  };
  vm.runInNewContext(fn + '\nthis.run = maybePlace;', context);
  const player = { location: { x: -30, y: 65, z: 28 }, dimension: dim };
  context.run(player, 0, 0);
  assert.equal(placements, 1); assert.equal(spawns.length, 3); assert.equal(loot.length, 1);
  assert.equal(doors, 0); assert.equal(travel, 0);
  assert.deepEqual(loot[0].slice(4), [25, 13, 25, 'fc:graveyard']);
  assert.equal(pick.mobSpawns.length, pick.mobs.length);
  spawns.forEach(({ type, at }, i) => {
    assert.equal(type, pick.mobs[i]);
    const local = [at.x-origin.x, at.y-origin.y, at.z-origin.z];
    assert.deepEqual(local, pick.mobSpawns[i]);
    const [x,y,z] = local.map(Math.floor);
    assert.equal(voxels[`${x},${y},${z}`], 'minecraft:air');
    assert.equal(voxels[`${x},${y+1},${z}`], 'minecraft:air');
    assert.ok(voxels[`${x},${y-1},${z}`] && !['minecraft:air','minecraft:water'].includes(voxels[`${x},${y-1},${z}`]));
  });
  context.run(player, 0, 0);
  assert.equal(placements, 1); assert.equal(spawns.length, 3); assert.equal(loot.length, 1);
}
console.log('PASS: actual graveyard placement on grass/dark, clear translated spawns, loot bounds and saved-region idempotence');

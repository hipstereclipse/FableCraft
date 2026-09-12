// Run the existing portal detector against the actual newly generated voxel blocks.
const fs = require('node:fs');
const vm = require('node:vm');
const assert = require('node:assert/strict');
const espree = require('espree');
const source = fs.readFileSync('packs/Fablecraft_BP/scripts/main.js', 'utf8');
const tree = espree.parse(source, { ecmaVersion: 'latest', sourceType: 'module', range: true });
const nodes = tree.body.filter(n => n.type === 'FunctionDeclaration' && n.id.name === 'isCullisConfigured' ||
  n.type === 'VariableDeclaration' && n.declarations.some(d => ['CULLIS_CORE', 'CULLIS_RING'].includes(d.id.name)));
assert.equal(nodes.length, 3);
const context = {};
vm.runInNewContext(nodes.map(n => source.slice(...n.range)).join('\n') + '\nthis.detect = isCullisConfigured;', context);
const fixture = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
const site = { x: 6, y: 1, z: 6 };
const dimension = blocks => ({ getBlock: ({ x, y, z }) => ({ typeId: blocks[`${x},${y},${z}`] || 'minecraft:air' }) });
assert.equal(context.detect(dimension(fixture), site), true, 'generated disc must activate the existing portal detector');
const noCore = { ...fixture }; delete noCore['6,0,6'];
assert.equal(context.detect(dimension(noCore), site), false, 'missing core must not activate');
const noRing = Object.fromEntries(Object.entries(fixture).filter(([, type]) => type !== 'minecraft:chiseled_stone_bricks'));
assert.equal(context.detect(dimension(noRing), site), false, 'missing runestone ring must not activate');
assert.equal(context.detect({ getBlock: () => { throw Error('unloaded'); } }, site), false, 'unloaded terrain must not activate');
console.log('Cullis detector: actual generated fixture PASS; missing core/ring/unloaded negatives PASS');

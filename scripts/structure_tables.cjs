// Parse only the explicit runtime structure/anchor tables; never execute main.js.
const fs = require('node:fs');
const espree = require('espree');
function readTables(path) {
const tree = espree.parse(fs.readFileSync(path, 'utf8'), { ecmaVersion: 'latest', sourceType: 'module' });
function literal(node) {
  if (node.type === 'Literal') return node.value;
  if (node.type === 'ArrayExpression') return node.elements.map(literal);
  if (node.type === 'ObjectExpression') return Object.fromEntries(node.properties.map(p => {
    if (p.type !== 'Property' || p.computed || p.method || p.kind !== 'init') throw Error('Unsupported table property');
    return [p.key.name ?? p.key.value, literal(p.value)];
  }));
  if (node.type === 'CallExpression' && node.callee.object?.name === 'Object' && node.callee.property?.name === 'freeze' && node.arguments.length === 1) return literal(node.arguments[0]);
  throw Error(`Unsupported table expression: ${node.type}`);
}
const result = {};
// The Chamber now uses a resumable per-cell owner instead of structureManager.
// Recognize its actual top-level registration and generated manifest binding;
// a comment, loot label or unrelated/dead helper is not a placement edge.
const caveImport = tree.body.find(n => n.type === 'ImportDeclaration' && n.source.value === './guild_caves.js');
const caveFactory = caveImport?.specifiers.find(s => s.type === 'ImportSpecifier' && s.imported.name === 'createGuildCaveLifecycle')?.local.name;
const perCellFixed = [];
for (const node of tree.body) if (node.type === 'VariableDeclaration') for (const d of node.declarations) {
  if (['STRUCTS', 'GUILD', 'CHEST_LOOT'].includes(d.id.name)) {
    if (d.id.name in result) throw Error('Duplicate runtime table');
    result[d.id.name] = literal(d.init);
  }
  if (d.id.name === 'guildCaves' && caveFactory && d.init?.type === 'CallExpression' && d.init.callee.name === caveFactory) {
    const options = d.init.arguments[0];
    const chamber = options?.type === 'ObjectExpression' && options.properties.find(p => p.type === 'Property' && !p.computed && p.key.name === 'chamber')?.value;
    if (chamber?.type === 'MemberExpression' && !chamber.computed && chamber.object.name === 'DATA' && chamber.property.name === 'guildChamber') perCellFixed.push('fc:chamber_of_fate');
  }
}
for (const key of ['STRUCTS', 'GUILD', 'CHEST_LOOT']) if (!(key in result)) throw Error(`Missing table ${key}`);
result.fixed = perCellFixed;
function visit(node) {
  if (!node || typeof node !== 'object') return;
  if (node.type === 'CallExpression' && node.callee.type === 'MemberExpression' && node.callee.property.name === 'place' && node.callee.object.property?.name === 'structureManager') {
    const id = node.arguments[0];
    if (id.type === 'Literal') result.fixed.push(id.value);
    else if (!(id.type === 'MemberExpression' && id.object.name === 'pick' && id.property.name === 'id')) throw Error('Unmodeled dynamic structure placement');
  }
  for (const value of Object.values(node)) if (Array.isArray(value)) value.forEach(visit); else if (value && typeof value === 'object') visit(value);
}
visit(tree);
return result;
}
module.exports = readTables;
if (require.main === module) process.stdout.write(JSON.stringify(readTables(process.argv[2])));

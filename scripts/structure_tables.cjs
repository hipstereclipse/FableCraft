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
for (const node of tree.body) if (node.type === 'VariableDeclaration') for (const d of node.declarations) {
  if (['STRUCTS', 'GUILD', 'CHEST_LOOT'].includes(d.id.name)) {
    if (d.id.name in result) throw Error('Duplicate runtime table');
    result[d.id.name] = literal(d.init);
  }
}
for (const key of ['STRUCTS', 'GUILD', 'CHEST_LOOT']) if (!(key in result)) throw Error(`Missing table ${key}`);
result.fixed = [];
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

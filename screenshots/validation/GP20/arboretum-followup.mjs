// Read-only source catalogue adapter; no Bedrock callbacks or production edits.
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import vm from 'node:vm';
import {parse} from 'espree';
const source=readFileSync('packs/Fablecraft_BP/scripts/main.js','utf8');
const ast=parse(source,{ecmaVersion:'latest',sourceType:'module',range:true});
const declaration=ast.body.find(n=>n.type==='VariableDeclaration'&&n.declarations.some(d=>d.id.name==='STRUCTS'));
const init=declaration.declarations.find(d=>d.id.name==='STRUCTS').init;
const structures=vm.runInNewContext(source.slice(...init.range));
const gorge=structures.find(s=>s.id==='fc:greatwood_gorge');
assert.equal(gorge.door,false);assert.equal(gorge.cullis,false);
assert.equal(structures.find(s=>s.id==='fc:demon_door_arch').door,true);
console.log(JSON.stringify({gorge,legacyArch:structures.find(s=>s.id==='fc:demon_door_arch')}));

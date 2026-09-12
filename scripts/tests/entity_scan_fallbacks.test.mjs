// Exercise actual handwritten source slices without loading the world's main module.
import { readFileSync } from 'node:fs';
import vm from 'node:vm';
import { test } from 'node:test';
import assert from 'node:assert/strict';
const source = readFileSync('packs/Fablecraft_BP/scripts/main.js', 'utf8');
function section(start, end) {
  const a = source.indexOf(start), b = source.indexOf(end, a + start.length);
  assert.ok(a >= 0 && b > a, 'source boundary must resolve');
  return source.slice(a, b);
}
const dimension = { getEntities() { throw new Error('unloaded chunk'); } };
const player = { id: 'hero', location: { x: 0, y: 0, z: 0 }, dimension };
test('Guild defender lookup returns an empty list on an unreadable dimension', () => {
  const ctx = vm.createContext({ guildBounds: () => ({ minX: 0, maxX: 122, minZ: 0, maxZ: 108, base: { y: 64 } }),
    isGuildDefenderType: () => true, player });
  vm.runInContext(section('function guildDefendersNear(', 'function rallyGuildDefenders('), ctx);
  assert.equal(vm.runInContext('guildDefendersNear(player).length', ctx), 0);
});
test('Protector alert tolerates a failed entity scan', () => {
  const ctx = vm.createContext({ victim: player });
  vm.runInContext(section('function alertProtectors(', 'function isInsideGuild('), ctx);
  assert.doesNotThrow(() => vm.runInContext('alertProtectors(victim)', ctx));
});
test('Guard sweep tolerates failed scans and continues to later players', () => {
  let visited = false;
  const later = { ...player, id: 'later', dimension: { getEntities() { visited = true; return []; } } };
  const ctx = vm.createContext({ world: { getPlayers: () => [player, later] },
    getBounties: () => ({}), syncWantedTags() {}, BOUNTY_GUARD_DETECTION_RADIUS: 36,
    system: { runInterval(fn) { fn(); } } });
  assert.doesNotThrow(() => vm.runInContext(section('// Guards enforce active local warrants.', '// ---------------------------------------------------------------------------\n// ASSAULTING'), ctx));
  assert.equal(visited, true);
});

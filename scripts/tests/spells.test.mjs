// Run: node --experimental-vm-modules scripts/tests/spells.test.mjs
// Execute the actual spell modules with a small Bedrock boundary mock.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import vm from 'node:vm';
import { readFile } from 'node:fs/promises';
import { resolve, dirname } from 'node:path';

async function fixture() {
  const events = {}, effects = [], draws = [], hits = [];
  const system = { currentTick: 0, runInterval(fn) { this.tick = fn; } };
  const context = vm.createContext({ console });
  const world = { getPlayers: () => players, afterEvents: Object.fromEntries(
    ['playerLeave', 'entityDie', 'playerSpawn'].map(name => [name, { subscribe(fn) { events[name] = fn; } }])) };
  const air = { isAir: true, isLiquid: false }, stone = { isAir: false, isLiquid: false };
  const dim = { id: 'overworld', terrain: ({ y }) => y < 0 ? stone : air,
    getBlock(p) { return this.terrain(p); },
    getEntities({ location, maxDistance }) { return foes.filter(e => Math.hypot(e.location.x-location.x, e.location.y-location.y, e.location.z-location.z) <= maxDistance); } };
  const player = { id: 'hero', typeId: 'minecraft:player', isValid: true,
    location: { x: 0.5, y: 0, z: 0.5 }, dimension: dim,
    view: { x: 0, y: 0, z: 1 }, yaw: 0,
    getRotation() { return { x: 0, y: this.yaw }; }, getViewDirection() { return this.view; },
    getHeadLocation() { return { ...this.location, y: this.location.y + 1.6 }; },
    tryTeleport(p, opts) { this.teleportOptions = opts; if (this.rejectTeleport) return false; this.location = { ...p }; return true; } };
  const players = [player], foes = [];
  function foe(id, x, z, family = '') {
    const e = { id, isValid: true, typeId: 'fc:bandit', location: { x, y: 0, z },
      getComponent(name) { return name === 'minecraft:health' ? { currentValue: 20 } : { hasTypeFamily: f => f === family }; },
      applyDamage(amount, opts) { hits.push({ id, amount, opts, tick: system.currentTick }); } };
    foes.push(e); return e;
  }
  const mocks = {
    '@minecraft/server': { world, system, EntityDamageCause: { magic: 'magic' } },
    'stats.js': { markSpellDamage() {} },
    'vfx.js': { tint: (...args) => draws.push(args), burst() {}, dimensionSound() {} },
    'selfbuff.js': { applyEffect: (...args) => effects.push(args) },
  };
  const cache = new Map();
  async function load(path) {
    if (cache.has(path)) return cache.get(path);
    const mock = mocks[path] || mocks[path.split('/').at(-1)];
    const mod = mock ? new vm.SyntheticModule(Object.keys(mock), function () {
      for (const [key, value] of Object.entries(mock)) this.setExport(key, value);
    }, { context, identifier: path }) : new vm.SourceTextModule(await readFile(path, 'utf8'), { context, identifier: path });
    cache.set(path, mod);
    await mod.link((specifier, parent) => load(specifier.startsWith('.') ? resolve(dirname(parent.identifier), specifier) : specifier));
    return mod;
  }
  const root = resolve('packs/Fablecraft_BP/scripts/wd');
  const ghost = await load(resolve(root, 'ghostblade.js')); await ghost.evaluate();
  const rush = await load(resolve(root, 'spells/assassin_rush.js')); await rush.evaluate();
  const targeting = cache.get(resolve(root, 'spells/shared/targeting.js')).namespace;
  return { player, players, dim, air, stone, hits, draws, effects, events, foe, targeting,
    deploy: level => ghost.namespace.deployGhostSword(player, level, [1, 1, 1]),
    tick: t => { system.currentTick = t; system.tick(); },
    rush: () => rush.namespace.assassinRushCast({ player, level: 1, spell: { color: [1, 1, 1] } }) };
}

test('Rush follows horizontal yaw, preserves camera, and uses checked teleport', async () => {
  const f = await fixture(); f.player.view = { x: 0, y: 1, z: 0 }; f.player.yaw = -90;
  assert.equal(f.rush(), true); assert.equal(f.player.location.y, 0);
  assert.equal(f.player.location.x, 8.5);
  assert.equal(f.player.teleportOptions.checkForBlocks, true);
  assert.equal(f.player.teleportOptions.facingLocation, undefined);
  assert.equal(f.player.teleportOptions.keepVelocity, false);
});
for (const obstacle of ['wall', 'ledge', 'liquid', 'unloaded', 'throw', 'side-wall']) {
  test(`Rush stops before ${obstacle}`, async () => {
    const f = await fixture();
    if (obstacle === 'side-wall') f.player.location.x = 0.8;
    f.dim.terrain = ({ x, y, z }) => {
      if (z >= 3) {
        if (obstacle === 'unloaded') return undefined;
        if (obstacle === 'throw') throw Error('chunk unloaded');
        if (obstacle === 'ledge') return f.air;
        if (obstacle === 'liquid') return { isAir: false, isLiquid: true };
        if (obstacle === 'wall' || x >= 1) return f.stone;
      }
      return y < 0 ? f.stone : f.air;
    };
    assert.equal(f.rush(), true); assert.ok(f.player.location.z < 3);
  });
}
test('Rush handles a full-block step and refuses a low ceiling over it', async () => {
  const f = await fixture(); f.dim.terrain = ({ y, z }) => y < (z >= 3 ? 1 : 0) ? f.stone : f.air;
  assert.equal(f.rush(), true); assert.equal(f.player.location.y, 1);
  const g = await fixture(); g.dim.terrain = ({ y, z }) => y === 2 || y < (z >= 3 ? 1 : 0) ? g.stone : g.air;
  assert.equal(g.rush(), true); assert.ok(g.player.location.z < 3);
});
test('Rush failure produces no success buff when engine rejects destination', async () => {
  const f = await fixture(); f.player.rejectTeleport = true;
  assert.equal(f.rush(), false); assert.equal(f.effects.length, 0);
});
test('Ghost strikes immediately, obeys cooldown, and expires', async () => {
  const f = await fixture(); f.foe('enemy', 0.5, 2); f.deploy(1); f.tick(2);
  assert.equal(f.hits.length, 1); f.tick(4); assert.equal(f.hits.length, 1);
  f.tick(14); assert.equal(f.hits.length, 2); f.tick(200); f.tick(202);
  assert.equal(f.hits.length, 2); assert.equal(f.hits[0].opts.damagingEntity, f.player);
});
test('Ghost ignores allies, players and charmed enemies using real targeting module', async () => {
  const f = await fixture(); f.foe('ally', 0.5, 1, 'fc_ally');
  f.foe('visitor', 0.5, 1).typeId = 'minecraft:player';
  f.foe('charmed', 0.5, 1); f.targeting.setCharmed('charmed', true);
  f.deploy(1); f.tick(2); assert.equal(f.hits.length, 0);
});
test('Ghost recast replaces blade and renews lifetime', async () => {
  const f = await fixture(); f.foe('enemy', 0.5, 2); f.deploy(1); f.tick(190);
  f.deploy(4); f.tick(202); assert.equal(f.hits.length, 2); assert.equal(f.hits[1].amount, 7);
  f.tick(630); assert.equal(f.hits.length, 2);
});
for (const event of ['playerLeave', 'entityDie', 'playerSpawn']) {
  test(`Ghost clears on ${event}`, async () => {
    const f = await fixture(); f.foe('enemy', 0.5, 2); f.deploy(1);
    f.events[event]({ playerId: f.player.id, deadEntity: f.player, player: f.player });
    f.tick(2); assert.equal(f.hits.length, 0); assert.equal(f.draws.length, 0);
  });
}
test('Ghost reseats after teleport/dimension change and cannot hunt beyond owner radius', async () => {
  const f = await fixture(); f.deploy(1); f.player.location.x = 100; f.dim.id = 'nether'; f.tick(2);
  assert.ok(f.draws.every(args => args[2].x > 90));
  const g = await fixture(); g.foe('far', 0.5, 14); g.deploy(1);
  for (let t = 2; t < 100; t += 2) g.tick(t);
  assert.equal(g.hits.length, 0);
});
test('Ghost cannot travel or strike through a wall', async () => {
  const f = await fixture(); f.foe('enemy', 0.5, 3); f.deploy(1);
  f.dim.terrain = ({ y, z }) => y < 0 || z === 1 ? f.stone : f.air;
  for (let t = 2; t < 100; t += 2) f.tick(t);
  assert.equal(f.hits.length, 0);
});

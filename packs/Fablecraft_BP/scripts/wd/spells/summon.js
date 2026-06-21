// Summon — Surround (good). Wrenches a creature's soul to fight for the Hero;
// higher charge raises the summon tier. Good-only lock and mana/cooldown are
// enforced by the shared cast gate; this body just binds the ally through the
// summons framework, which caps the count and handles soul-replacement.
import { summonAlly } from "../summons.js";

export function summonCast(ctx) {
  const { player, level, spell } = ctx;
  // The sigil/soul VFX and the cap/ownership bookkeeping live in summons.js so
  // every summon (from any source) shares one ledger. Returning false on failure
  // lets the cast gate refund the Will.
  return summonAlly(player, level, spell.color) !== undefined;
}

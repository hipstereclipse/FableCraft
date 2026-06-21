// Will & Destiny menu bridge. A dependency-free hand-off so the storybook Hero
// Menu (herobook.js) can open the deep legacy ledgers defined in main.js (the
// 6k-line monolith) without a circular import. main.js registers its openers
// here after they are defined; herobook reads them at click time. Every opener
// is (player) => void and chains its own navigation back to the hub.
export const LEGACY_MENU = {
  hub: null,         // the storybook Hero Menu root — the single menu hub
  heroMenu: null,    // legacy root opener (kept as a fallback; now delegates to hub)
  recall: null,      // Guild recall

  // Deep ledger pages, each surfaced as its own storybook category button.
  stats: null,       // Hero Status (renown, alignment, XP, disciplines, training/titles)
  items: null,       // Inventory / provisions
  weapons: null,     // Weapon locker
  clothing: null,    // Clothing & armour
  expressions: null, // Expressions / emotes
  quests: null,      // Quest journal
  factions: null,    // Factions & bounties
  map: null,         // Map of Albion / Cullis travel
};

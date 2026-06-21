// Will & Destiny menu bridge. A dependency-free hand-off so the storybook Hero
// Menu (herobook.js) can open the deep legacy ledgers defined in main.js (the
// 6k-line monolith) without a circular import. main.js registers its openers
// here after they are defined; herobook reads them at click time.
export const LEGACY_MENU = {
  heroMenu: null,     // (player) => opens the legacy Hero Menu root
  recall: null,       // (player) => Guild recall
};

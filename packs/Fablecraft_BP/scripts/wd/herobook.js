// Will & Destiny storybook Hero Menu. A parchment-and-gold router rebuilt to
// read like the Fable: TLC in-game menu. Phase 2 ships: the Guild-Seal flourish,
// the page router, a fully working Magic / quick-slot page, a Hero (Stats)
// read-out, and an Appearance page that also drives the appearance/charge
// options. Deep legacy pages (Items, Weapons, Quests, Map, Factions) are reached
// through the legacy ledger via menu_bridge.js. The parchment theme itself is RP
// ui/ texture overrides emitted by the asset pipeline.
import { ActionFormData, ModalFormData } from "@minecraft/server-ui";
import { WD_CONFIG } from "./config.js";
import { getState, mutateState } from "./state.js";
import { spawnParticle } from "./particles.js";
import { getSpell, SPELL_ORDER, CATEGORY_LABEL } from "./spells/registry.js";
import { LEGACY_MENU } from "./menu_bridge.js";
import { chronicle } from "./logbook.js";
import { t } from "../fc_strings.js";

const SIGIL = "textures/ui/wd"; // generated storybook sigils (cosmetic if absent)

const ALIGN_TITLES = [
  { min: 850, title: t("alignment.avo") },
  { min: 500, title: t("alignment.paragon") },
  { min: 150, title: t("alignment.good") },
  { min: -149, title: t("alignment.neutral") },
  { min: -499, title: t("alignment.rogue") },
  { min: -849, title: t("alignment.villain") },
  { min: -1000, title: t("alignment.skorm") },
];

function alignmentTitle(value) {
  for (const tier of ALIGN_TITLES) {
    if (value >= tier.min) return tier.title;
  }
  return t("alignment.neutral");
}

function flourish(player) {
  if (!WD_CONFIG.guildSealFlourish) return;
  try {
    player.playSound("beacon.activate", { volume: 0.6, pitch: 1.5 });
    player.playSound("random.orb", { volume: 0.5, pitch: 1.2 });
  } catch {
    // Audio is additive.
  }
  const center = { x: player.location.x, y: player.location.y + 1.1, z: player.location.z };
  for (let i = 0; i < 12; i++) {
    const angle = (i / 12) * Math.PI * 2;
    spawnParticle(
      player.dimension,
      "wd:will_fizzle",
      { x: center.x + Math.cos(angle) * 0.9, y: center.y, z: center.z + Math.sin(angle) * 0.9 },
      { red: 0.2, green: 0.45, blue: 1.0, alpha: 0.8 },
      0.4,
      0.6,
    );
  }
}

function ownedSpells(state) {
  return SPELL_ORDER.filter((id) => (state.spells.owned[id] ?? 0) >= 1);
}

function slotSummary(state) {
  return state.spells.slots
    .map((id, i) => {
      const active = i === state.spells.active ? "§9▶ " : "§8  ";
      const name = id ? `§f${getSpell(id)?.name ?? id}` : t("magic.empty");
      return t("magic.slot_summary", { active, slot: i + 1, name });
    })
    .join("\n");
}

// ---------------------------------------------------------------------------
// Root
// ---------------------------------------------------------------------------
// The single Hero Menu hub. `silent` suppresses the Guild-Seal flourish so that
// returning here from a sub-page (legacy or storybook) doesn't re-chime.
export function openHeroMenu(player, silent = false) {
  if (!silent) flourish(player);
  const state = getState(player);
  mutateState(player, (d) => { d.ui.lastPage = "hero"; });

  const form = new ActionFormData()
    .title(t("menu.hero_title"))
    .body(
      t("menu.hero_body", {
        alignment: alignmentTitle(state.alignment), morality: state.alignment,
        mana: Math.round(state.mana.current), maxMana: state.mana.max,
      }),
    )
    // Buttons 1/2/10 use the storybook pages in this file; the rest open the deep
    // legacy ledgers through the menu bridge. The case map below MUST stay in
    // lockstep with this button order.
    .button(t("menu.hero"), `${SIGIL}/sigil_hero`)
    .button(t("menu.magic"), `${SIGIL}/sigil_magic`)
    .button(t("menu.appearance"), `${SIGIL}/sigil_appearance`)
    .button(t("menu.weapons"), `${SIGIL}/sigil_weapons`)
    .button(t("menu.inventory"), `${SIGIL}/sigil_inventory`)
    .button(t("menu.clothing"), `${SIGIL}/sigil_inventory`)
    .button(t("menu.expressions"), `${SIGIL}/sigil_factions`)
    .button(t("menu.quests"), `${SIGIL}/sigil_quests`)
    .button(t("menu.factions"), `${SIGIL}/sigil_factions`)
    .button(t("menu.map"), `${SIGIL}/sigil_map`)
    .button(t("menu.logbook"), `${SIGIL}/sigil_logbook`);

  form.show(player).then((res) => {
    if (res.canceled) return;
    switch (res.selection) {
      case 0: return openLegacy(player, "stats");      // Hero Status (renown, XP, training, titles)
      case 1: return magicPage(player);
      case 2: return appearancePage(player);
      case 3: return openLegacy(player, "weapons");
      case 4: return openLegacy(player, "items");
      case 5: return openLegacy(player, "clothing");
      case 6: return openLegacy(player, "expressions");
      case 7: return openLegacy(player, "quests");
      case 8: return openLegacy(player, "factions");
      case 9: return openLegacy(player, "map");
      case 10: return logbookPage(player);
      default: return undefined;
    }
  }).catch(() => {});
}

// Open a deep legacy ledger page by bridge key, falling back to the hub if main.js
// has not registered it yet (e.g. very early in load).
function openLegacy(player, page) {
  const opener = LEGACY_MENU[page];
  if (typeof opener === "function") return opener(player);
  if (typeof LEGACY_MENU.heroMenu === "function") return LEGACY_MENU.heroMenu(player);
  player.sendMessage(t("menu.unbound"));
}

// ---------------------------------------------------------------------------
// Magic — assign the three quick-slots
// ---------------------------------------------------------------------------
function magicPage(player) {
  const state = getState(player);
  const owned = ownedSpells(state);
  mutateState(player, (d) => { d.ui.lastPage = "magic"; });

  const form = new ActionFormData()
    .title(t("magic.title"))
    .body(
      t("magic.body", { slots: slotSummary(state) }),
    );

  if (owned.length === 0) {
    form.body(t("magic.none"));
  }
  for (const id of owned) {
    const spell = getSpell(id);
    const level = state.spells.owned[id];
    const slotIndex = state.spells.slots.indexOf(id);
    const marker = slotIndex >= 0 ? t("magic.slot_marker", { slot: slotIndex + 1 }) : "§8";
    const category = CATEGORY_LABEL[spell.category] ?? spell.category;
    form.button(t("magic.spell", { marker, name: spell.name, level, category, mana: spell.baseMana }));
  }
  form.button(t("menu.back"));

  form.show(player).then((res) => {
    if (res.canceled) return;
    if (res.selection === owned.length) return openHeroMenu(player, true);
    const id = owned[res.selection];
    if (id) return bindSlotPage(player, id);
  }).catch(() => {});
}

function bindSlotPage(player, id) {
  const spell = getSpell(id);
  const state = getState(player);
  const form = new ActionFormData()
    .title(t("magic.bind_title", { name: spell?.name ?? id }))
    .body(t("magic.bind_body"));
  for (let i = 0; i < state.spells.slots.length; i++) {
    const cur = state.spells.slots[i];
    const curName = cur ? getSpell(cur)?.name ?? cur : t("magic.empty_slot");
    form.button(t("magic.slot", { slot: i + 1, name: curName }));
  }
  form.button(t("magic.remove"));
  form.button(t("menu.back"));

  form.show(player).then((res) => {
    if (res.canceled) return magicPage(player);
    const slotCount = state.spells.slots.length;
    if (res.selection < slotCount) {
      const slot = res.selection;
      mutateState(player, (d) => {
        for (let k = 0; k < d.spells.slots.length; k++) if (d.spells.slots[k] === id) d.spells.slots[k] = null;
        d.spells.slots[slot] = id;
        d.spells.active = slot;
      });
    } else if (res.selection === slotCount) {
      mutateState(player, (d) => {
        for (let k = 0; k < d.spells.slots.length; k++) if (d.spells.slots[k] === id) d.spells.slots[k] = null;
      });
    } else {
      return magicPage(player);
    }
    magicPage(player);
  }).catch(() => {});
}

// ---------------------------------------------------------------------------
// Logbook — the narrated chronicle (kills, deeds, bestiary, "story so far")
// ---------------------------------------------------------------------------
function logbookPage(player) {
  mutateState(player, (d) => { d.ui.lastPage = "logbook"; });
  const { lines } = chronicle(player);
  new ActionFormData()
    .title(t("logbook.title"))
    .body(lines.join("\n"))
    .button(t("menu.back"))
    .show(player)
    .then((r) => { if (!r.canceled) openHeroMenu(player, true); })
    .catch(() => {});
}

// ---------------------------------------------------------------------------
// Appearance — read-out + options
// ---------------------------------------------------------------------------
function appearancePage(player) {
  const state = getState(player);
  const tiers = state.appearance.tiers;
  const detailOptions = ["full", "overlays_only", "horns_halo_only"];
  const currentDetail = Math.max(0, detailOptions.indexOf(state.options.appearanceDetail));

  new ModalFormData()
    .title(t("appearance.title"))
    .dropdown(
      t("appearance.detail", tiers),
      [t("appearance.full"), t("appearance.overlays"), t("appearance.ornaments")],
      { defaultValueIndex: currentDetail },
    )
    .toggle(t("appearance.show"), { defaultValue: state.options.morphEnabled !== false })
    .toggle(t("appearance.charge"), { defaultValue: state.options.chargeEnabled !== false })
    .slider(t("appearance.aura"), 0, 2, { valueStep: 1, defaultValue: Math.round(state.options.auraDensity ?? 1) })
    .show(player)
    .then((res) => {
      if (res.canceled) return openHeroMenu(player, true);
      const [detailIdx, morphEnabled, chargeEnabled, auraDensity] = res.formValues;
      mutateState(player, (d) => {
        d.options.appearanceDetail = detailOptions[detailIdx] ?? "full";
        d.options.morphEnabled = morphEnabled === true;
        d.options.chargeEnabled = chargeEnabled === true;
        const density = Number(auraDensity);
        d.options.auraDensity = Number.isFinite(density) ? Math.max(0, Math.min(2, density)) : 1;
      });
      openHeroMenu(player, true);
    })
    .catch(() => {});
}

# Wanted / Bounty System

Raising a hand against the innocent — or the law — makes you **Wanted**. Every
punch and every kill adds to a bounty tied to the jurisdiction responsible for it,
lights up wanted **stars**, and starts (or tops up) a live **countdown**. Behave
and the countdown runs out and the warrant fades; keep offending and it climbs.

The system covers two kinds of jurisdiction:

- **Generated settlements** (Bowerstone, Oakvale, Snowspire and their outlying
  villages/camps), enforced by that town's guard.
- **The Heroes' Guild**, its own jurisdiction, enforced by the Guild's standing
  defenders (the Guildmaster, Maze, the apprentices and the gate guards). There
  is no separate "Guild Heat" meter — the Guild uses the same wanted system.

A crime outside any recorded settlement falls back to a 64×64 jurisdiction cell
for the nearest relevant town.

## Bounty growth (per offence — Harsh / Fable-tough tuning)

| Crime | Townsfolk | Guard / Guild member |
|---|---:|---:|
| **Punch** (any blow) | +10 gold | +20 gold |
| **Kill** | +40 gold | +80 gold |

- Every distinct blow counts (rapid multi-hits on the *same* victim within a
  six-tick quiet interval coalesce; a fresh hit requires at least six ticks since
  the previous hit on that victim).
- Striking a guard or guild defender — or *any* kill — is an immediate lethal
  hunt. Merely cuffing a civilian only brings the watch over to demand a fine.
- Bounties are tracked independently per jurisdiction.

## The countdown

A new record starts with a **120-second base**, then adds the triggering crime's
time: the first punch produces **160 seconds**, the first kill **240 seconds**.
Further crimes add time on top of whatever is left:

| Crime | Time added |
|---|---:|
| Punch | +40 seconds |
| Kill | +120 seconds |

- The countdown is capped at **15 minutes**.
- It runs **everywhere while the game clock advances**, using `system.currentTick * 50`,
  not wall-clock time. Pausing the game pauses this clock; no exact offline/restart
  countdown guarantee is implemented. Missing or implausibly distant stored deadlines
  (including old epoch timestamps) reset to 120 seconds on the next player sweep.
- Stop committing crimes and it ticks down; reach zero and the warrant fades,
  the stars clear, and enforcers stand down. Warrants are processed for online players.
- Resisting arrest restarts the deadline at exactly 120 seconds; it does not extend
  an already longer timer. Death alone is not an implemented warrant-clear condition.

## Wanted heat (the stars)

The top-centre HUD shows one-to-five Fable wanted stars plus the live countdown
for your most serious active warrant, shown wherever you are while wanted:

| Bounty | Stars |
|---:|:---:|
| 1–19 gold | ★ |
| 20–59 gold | ★★ |
| 60–109 gold | ★★★ |
| 110–174 gold | ★★★★ |
| 175+ gold | ★★★★★ |

## Guard response scaling (settlements)

Existing nearby guards count toward the cap; only the missing responders spawn,
18–28 blocks away, preferably out of the player's immediate view.

| Local bounty | Maximum guards | Tier | Health | Damage | Speed | Knockback resist |
|---:|---:|---|---:|---:|---:|---:|
| 0–74 gold | 2 | Standard | Base | Base | Base | 0% |
| 75–199 gold | 3 | Veteran | 135% | 130% | 108% | 10% |
| 200+ gold | 4 | Elite | 165% | 160% | 118% | 22% |

Guards use town-specific wanted tags, so a wanted Hero never makes guards attack
innocent multiplayer participants. On Guild ground the Guild's own defenders rally
instead of spawning town watch.

## Confronting the watch (settlements)

When you have *only* assaulted civilians (an "approach" warrant), the watch comes
to confront you, and when a guard reaches you it offers a choice:

- **Pay the bounty** in full (instant clear).
- **Go to jail** — clears the bounty, confiscates carried inventory and worn
  armor (Guild Seal, Will Focus, spell items and the Summoner's Grimoire are
  preserved), and releases you just outside the town limits.
- **Resist arrest** (or cancel) — the guards turn hostile and the clock restarts.

A murder, or any violence against a guard or guild member, skips straight to a
hostile hunt — there is no fine to pay; evade until the countdown fades (death does not explicitly clear the warrant).

## Clearing a warrant

A warrant clears when:

- Its countdown reaches zero.
- You pay the fine in full (settlement assault warrants).
- You accept jail (settlements).

Reputation loss and morality changes are separate consequences and are not
restored when a warrant clears.

## Implementation scope and diagnostic commands

These values are current FableCraft tuning [B], not asserted exact TLC values.
Crime handlers classify the victim and jurisdiction; their "WITNESSED" message is
not proof of a separate witness line-of-sight simulation. Reputation and morality
have their own consequences. A fatal player blow may generate both an assault
and a kill event; do not assume its total is only the kill increment.

`/scriptevent fc:wanted` lists active warrants; `/scriptevent fc:clearwanted`
clears them for testing. `/scriptevent fc:reanchor` refreshes Guild anchors after
layout changes. These handlers are in main.js, not a wd/debug.js module.

## Manual test checklist — all UNRUN in this session

- [ ] Punch a Guild apprentice: verify a Guild warrant opens (+20g, ★★), the Guild's
   defenders turn on you, and a countdown appears top-centre.
- [ ] Keep punching different Guild members: verify the bounty climbs, the stars
   rise toward ★★★★★, and the countdown grows with each blow.
- [ ] Stop and wait: verify the countdown ticks down and the warrant fades at zero,
   the stars vanish, and the defenders calm.
- [ ] Punch a townsperson in a generated settlement: verify a +10g "approach"
   warrant and the watch coming to demand a fine.
- [ ] Kill a townsperson: verify it escalates to a hostile +40g hunt.
- [ ] Pay a settlement fine and verify the warrant and the response clear.
- [ ] Choose jail and verify only Guild/Will items remain and release occurs outside
   town.
- [ ] Create warrants in two settlements and verify they count down and resolve
   independently, with the HUD showing the most serious one.

- [ ] Verify a first punch starts near 160 seconds, an isolated kill near 240,
      and repeated offences cap at 900 seconds (allow for elapsed ticks).
- [ ] Compare 74/75/199/200-gold guard tiers; star thresholds remain 20/60/110/175.
- [ ] Test pause, disconnect/rejoin and server restart; record observed timer migration
      without asserting wall-clock persistence. Verify death does not silently clear it.
- [ ] Test multiple players, unloaded scan regions, and both diagnostic commands.

Reviewed against `accrueCrime`, `bountyResponseTier`, `nowMs`, `protectedFromJail`
and the 20-tick warrant sweep in `packs/Fablecraft_BP/scripts/main.js`, 2026-09-12.

# Settlement Bounty System

Killing civilians, villagers, traders, barkeeps, other friendly townsfolk, or guards creates a bounty tied to that exact generated settlement. A crime outside a recorded settlement uses a 64×64 jurisdiction cell for the nearest relevant town.

## Bounty growth

- Civilian murder: `20 + (15 × prior local kills)` gold.
- Guard murder: `35 + (15 × prior local kills)` gold.
- Bounties are independent per settlement.
- Bowerstone, Oakvale, and Snowspire use their own guard type and wanted-player tag.

## Guard response scaling

Existing nearby guards count toward the cap. Only the missing responders are spawned, 18–28 blocks away and preferably behind or near the edge of the player's view.

| Local bounty | Maximum guards | Tier | Health | Damage | Speed | Knockback resistance |
|---:|---:|---|---:|---:|---:|---:|
| 0–74 gold | 2 | Standard | Base | Base | Base | 0% |
| 75–199 gold | 3 | Veteran | 135% | 130% | 108% | 10% |
| 200+ gold | 4 | Elite | 165% | 160% | 118% | 22% |

The hard maximum is four active enforcing guards for one player's settlement bounty. Guards use town-specific wanted tags, so they do not target innocent multiplayer participants.

## Local wanted heat HUD

The top-center HUD shows one to five Fable-styled wanted stars for the active settlement bounty:

| Local bounty | Heat |
|---:|---:|
| 1–24 gold | 1 star |
| 25–74 gold | 2 stars |
| 75–124 gold | 3 stars |
| 125–199 gold | 4 stars |
| 200+ gold | 5 stars |

Heat is resolved from the exact settlement record the player is currently inside. The stars only appear while a matching town guard is within the 36-block enforcement radius. Leaving guard range, leaving that jurisdiction, clearing the bounty, or entering a different settlement hides or replaces the displayed heat without changing other settlements' bounty records.

## Leaving and returning

The expiry timer begins after the player leaves the settlement:

```text
90 seconds + 90 seconds per NPC/guard killed
```

The timer is capped at 15 minutes and uses wall-clock time, so it continues across server restarts.

Returning before expiry causes guards to approach rather than immediately attack. When a guard gets within nine blocks—or after six seconds if pathfinding is obstructed—the player receives three choices:

- Pay the bounty in full.
- Go to jail.
- Resist arrest.

Canceling the form counts as resisting arrest.

## Jail

Going to jail:

- Clears that settlement's bounty.
- Removes all carried inventory and equipped armor.
- Preserves Guild Seals, the Will Focus, spell items, the Summoner's Grimoire, and persistent Will/stat progression.
- Teleports the player fourteen blocks beyond the nearest settlement boundary.
- Releases the player without equipped clothing.

Confiscated items are permanently removed; there is no evidence-chest recovery system.

## Clearing a bounty

A settlement bounty clears when:

- Its away timer expires.
- The player pays the complete gold amount.
- The player accepts jail.

Reputation loss and morality changes remain separate consequences and are not restored when the bounty clears.

## Manual test checklist

1. Kill one civilian in a generated settlement: verify a 20-gold bounty and at most two standard guards.
2. Kill additional civilians until the bounty passes 75 gold: verify the cap becomes three and guards become veterans.
3. Raise the bounty above 200 gold: verify the cap becomes four and guards become elite.
4. Confirm guards spawn 18–28 blocks away rather than directly beside the player.
5. Test with another player nearby and verify guards target only the wanted player.
6. Leave the settlement and verify spawned responders are removed and the timer starts.
7. Return before expiry and verify guards approach before showing the warrant menu.
8. Pay with enough gold and verify the bounty and hostile response clear.
9. Attempt payment without enough gold and verify the guards attack.
10. Choose jail while wearing armor and carrying mixed items. Verify only Guild/Will items remain and release occurs outside town.
11. Stay away until the timer expires and verify the warrant clears.
12. Create bounties in two settlements and verify they expire and resolve independently.
13. Move beyond 36 blocks from every matching guard and verify the wanted stars hide without clearing the bounty.
14. Return to matching guard range and verify the stars restore at the heat level for that settlement.
15. Enter a second wanted settlement and verify its independent heat level replaces the first.

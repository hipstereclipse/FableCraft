# Fable expression validation

The behavior pack registers all 31 Fable TLC expressions and listens to
`world.afterEvents.playerEmote`. The first time a native Persona emote UUID is
seen, it is bound to the next unlocked Fable expression for that player. The
binding persists in `fc_native_emote_bindings`.

Minecraft requires custom commands to have a namespace, so the supported
spellings are:

- `/fable:emote <emote_name>`
- `/fable:npc_stats`
- `/fable:npc_react <emote_name>`
- `/fable:animate <walk|idle|run>`
- `/fable:test`
- `/fable:demo`

The same operations can be automated with `/scriptevent`, for example:

```text
/scriptevent fable:emote flirt
/scriptevent fable:npc_react blood_lust_roar
/scriptevent fable:animate run
```

## Static and runtime audits

From the repository root:

```powershell
python scripts/gen_emotes.py
python scripts/gen_expression_previews.py
python scripts/verify_emotes.py
python scripts/build_addon.py
```

The preview generator renders all expressions from the current animation JSON
using a rotating cast of villagers, guards, Guild characters and named NPCs.
Individual cards are written to `screenshots/expressions/`; the combined sheet
is written to `screenshots/gallery/expressions.png`. Use `--models` with a
comma-separated list of NPC IDs to override the cast.

In Minecraft, enable cheats and the Content Log, look toward an NPC, then run
`/fable:test`. It validates all 31 registry entries and their social-rating
deltas, toggles the camera, and writes timestamped pass/fail records with
`console.warn`.

## Capture sequence

1. Stand in a bright, open area with one Albion villager in view.
2. Start Xbox Game Bar (`Win+Alt+R`) or OBS.
3. Run `/fable:demo`.
4. Keep the player and NPC in frame for about 30 seconds.
5. Confirm the recording contains:
   - Flirt, Blood Lust Roar, Fart and Vulgar Thrust with third-person camera cuts.
   - An NPC walking a circle with alternating arms/legs and body bob.
   - The NPC cowering/running, followed by laughing or clapping.
6. For still validation, pause the recording or use `Win+Alt+PrtScn` during each
   sequence. Review the Minecraft Content Log for `EMOTE`, `CAMERA`,
   `REACTION`, `FINE`, and `TEST_PASS` entries.

The Camera API cannot query a player's current first/third-person preference.
The implementation therefore calls `camera.clear()` after 40 ticks, which
returns control to the player's own configured perspective.

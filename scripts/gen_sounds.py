"""gen_sounds.py — synthesizes the Fablecraft soundscape as OGG-free WAV/FSB
alternative: Bedrock accepts .ogg only; we synthesize 16-bit PCM WAVs then
convert minimal RIFF->OGG is non-trivial without deps, so instead we emit
.wav files which Bedrock plays via 'sound_definitions.json' (wav is supported
for sounds in RPs).

Sounds: demon door rumble/speak, banshee shriek, spell casts, level-up chime,
guild ambience pad.
"""
import math
import struct
import wave

from fc_lib import ROOT, RP, rng, write_json

OUT = RP / "sounds" / "fc"
SR = 22050


def write_wav(path, samples):
    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        frames = b"".join(struct.pack("<h", max(-32767, min(32767, int(s * 32767)))) for s in samples)
        w.writeframes(frames)


def env(t, dur, a=0.02, r=0.3):
    if t < a:
        return t / a
    if t > dur - r:
        return max(0.0, (dur - t) / r)
    return 1.0


def synth(dur, fn):
    n = int(SR * dur)
    return [fn(i / SR) * env(i / SR, dur) for i in range(n)]


def door_rumble():
    r = rng("snd", "door")
    def fn(t):
        base = math.sin(2 * math.pi * 38 * t + 3 * math.sin(2 * math.pi * 2.2 * t))
        sub = math.sin(2 * math.pi * 52 * t)
        grit = (r.random() * 2 - 1) * 0.25 * math.sin(2 * math.pi * 0.8 * t) ** 2
        return 0.5 * base + 0.25 * sub + grit
    return synth(2.2, fn)


def door_speak():
    r = rng("snd", "speak")
    def fn(t):
        f = 90 + 35 * math.sin(2 * math.pi * 1.7 * t) + 20 * math.sin(2 * math.pi * 4.3 * t)
        v = math.sin(2 * math.pi * f * t)
        v += 0.5 * math.sin(2 * math.pi * f * 0.5 * t)
        v += 0.2 * (r.random() * 2 - 1)
        gate = 0.55 + 0.45 * math.sin(2 * math.pi * 6.5 * t)
        return 0.55 * v * gate
    return synth(1.8, fn)


def banshee_shriek():
    def fn(t):
        f = 900 + 700 * math.sin(2 * math.pi * 1.1 * t) + 300 * math.sin(2 * math.pi * 7 * t)
        v = math.sin(2 * math.pi * f * t) + 0.5 * math.sin(2 * math.pi * f * 1.5 * t)
        return 0.4 * v
    return synth(1.6, fn)


def spell_cast():
    def fn(t):
        f = 300 + 900 * t
        shimmer = math.sin(2 * math.pi * f * t) + 0.6 * math.sin(2 * math.pi * f * 1.5 * t + 0.5)
        sparkle = 0.3 * math.sin(2 * math.pi * 2400 * t) * math.sin(2 * math.pi * 13 * t) ** 2
        return 0.45 * shimmer + sparkle
    return synth(0.9, fn)


def level_up():
    notes = [392, 523, 659, 784]  # G4 C5 E5 G5
    dur = 1.4
    def fn(t):
        idx = min(len(notes) - 1, int(t / 0.28))
        f = notes[idx]
        v = math.sin(2 * math.pi * f * t) + 0.4 * math.sin(2 * math.pi * f * 2 * t)
        bell = 0.3 * math.sin(2 * math.pi * f * 3 * t) * max(0, 1 - (t % 0.28) * 4)
        return 0.4 * v + bell
    return synth(dur, fn)


def guild_pad():
    chord = [130.8, 164.8, 196.0, 261.6]  # C3 E3 G3 C4
    def fn(t):
        v = sum(math.sin(2 * math.pi * f * t + i) for i, f in enumerate(chord)) / len(chord)
        slow = 0.7 + 0.3 * math.sin(2 * math.pi * 0.15 * t)
        return 0.35 * v * slow
    return synth(6.0, fn)


def sword_clash():
    r = rng("snd", "clash")
    def fn(t):
        ringf = 2300 * math.exp(-t * 6)
        ring = math.sin(2 * math.pi * (1200 + ringf) * t) * math.exp(-t * 7)
        noise = (r.random() * 2 - 1) * math.exp(-t * 30)
        return 0.5 * ring + 0.5 * noise
    return synth(0.7, fn)


SOUNDS = {
    "door_rumble": door_rumble,
    "door_speak": door_speak,
    "banshee_shriek": banshee_shriek,
    "spell_cast": spell_cast,
    "level_up": level_up,
    "guild_pad": guild_pad,
    "sword_clash": sword_clash,
}

SOUND_DESC = {
    "door_rumble": "Demon Door awakening — deep stone grinding with sub-bass wobble",
    "door_speak": "Demon Door voice — gravelly modulated speech-like drone",
    "banshee_shriek": "Banshee shriek — swooping dissonant wail",
    "spell_cast": "Will power cast — rising shimmer with sparkle overtones",
    "level_up": "Level-up chime — G-C-E-G bell arpeggio",
    "guild_pad": "Heroes' Guild ambience — slow C-major drone pad",
    "sword_clash": "Sword clash — metallic ring with impact noise",
}

PREVIEW = ROOT / "sound_preview"


def write_preview():
    """Copy WAVs into sound_preview/ with an HTML player for auditioning."""
    PREVIEW.mkdir(exist_ok=True)
    rows = []
    for name in SOUNDS:
        src = OUT / f"{name}.wav"
        dst = PREVIEW / f"{name}.wav"
        dst.write_bytes(src.read_bytes())
        rows.append(
            f'<tr><td class="n">{name}</td>'
            f'<td>{SOUND_DESC[name]}</td>'
            f'<td><audio controls preload="none" src="{name}.wav"></audio></td></tr>')
    html = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<title>Fablecraft: Reforged — Sound Test</title>
<style>
  body {{ background:#1d1610; color:#e6d8b8; font-family:Georgia,serif;
         max-width:860px; margin:2rem auto; padding:0 1rem; }}
  h1 {{ color:#f0c75e; border-bottom:2px solid #6b5530; padding-bottom:.4rem; }}
  table {{ width:100%; border-collapse:collapse; }}
  td {{ padding:.55rem .6rem; border-bottom:1px solid #3a2f1f; vertical-align:middle; }}
  td.n {{ color:#f0c75e; font-weight:bold; white-space:nowrap; }}
  audio {{ width:240px; }}
  p {{ color:#a89572; }}
</style></head><body>
<h1>⚔ Fablecraft: Reforged — Sound Test</h1>
<p>All {len(SOUNDS)} sounds are pure-math synthesis (no samples). The same WAVs ship
inside the resource pack under <code>sounds/fc/</code>. Open this file in any browser to audition.</p>
<table>{''.join(rows)}</table>
</body></html>
"""
    (PREVIEW / "index.html").write_text(html, encoding="utf-8")
    print(f"sound preview -> {PREVIEW} ({len(SOUNDS)} wavs + index.html)")


def main():
    for name, fn in SOUNDS.items():
        write_wav(OUT / f"{name}.wav", fn())
        print(f"  {name}.wav")
    defs = {
        "format_version": "1.14.0",
        "sound_definitions": {
            f"fc.{name}": {
                "category": "neutral",
                "sounds": [{"name": f"sounds/fc/{name}", "volume": 0.9}],
            } for name in SOUNDS
        },
    }
    write_json(RP / "sounds" / "sound_definitions.json", defs)
    print("sound_definitions.json written")
    write_preview()


if __name__ == "__main__":
    main()

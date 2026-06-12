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


# --- DSP helpers -----------------------------------------------------------

def zeros(dur):
    return [0.0] * int(SR * dur)


def add_partial(buf, freq, amp, t0=0.0, tau=0.5, vib_hz=0.0, vib_amt=0.0):
    """Additive sine partial with exponential decay (and optional vibrato)."""
    n0 = int(t0 * SR)
    phase = 0.0
    two_pi = 2 * math.pi
    for i in range(n0, len(buf)):
        t = (i - n0) / SR
        f = freq
        if vib_hz:
            f *= 1 + vib_amt * math.sin(two_pi * vib_hz * t)
        phase += two_pi * f / SR
        a = amp * math.exp(-t / tau)
        if a < 0.0005:
            break
        buf[i] += a * math.sin(phase)


def add_noise(buf, r, amp, t0, dur, tau, lp=0.3):
    """One-pole low-passed noise burst with exponential decay."""
    n0 = int(t0 * SR)
    n1 = min(len(buf), n0 + int(dur * SR))
    y = 0.0
    for i in range(n0, n1):
        t = (i - n0) / SR
        y = lp * y + (1 - lp) * (r.random() * 2 - 1)
        buf[i] += amp * math.exp(-t / tau) * y


def reverb(buf, mix=0.25, taps=((1123, .66), (1481, .61), (1873, .55))):
    """Parallel comb reverb, mixed under the dry signal."""
    n = len(buf)
    wet = [0.0] * n
    for d, g in taps:
        comb = [0.0] * n
        for i in range(n):
            comb[i] = buf[i] + (comb[i - d] * g if i >= d else 0.0)
        for i in range(n):
            wet[i] += (comb[i] - buf[i]) / len(taps)
    return [buf[i] + mix * wet[i] for i in range(n)]


def normalize(buf, peak=0.85):
    m = max(1e-6, max(abs(s) for s in buf))
    return [s * peak / m for s in buf]


# --- the sounds ------------------------------------------------------------

def door_rumble():
    """Stone door dragging open: juddering grind, resonant scrape harmonics,
    sub swell, and a heavy settling thud with dust at the end."""
    r = rng("snd", "door3")
    dur = 3.0
    buf = zeros(dur)
    two_pi = 2 * math.pi
    # judder gate: stone moves in jolts (~6.5 Hz, irregular)
    n = len(buf)
    gate = [0.0] * n
    for i in range(n):
        t = i / SR
        g = 0.5 + 0.5 * math.sin(two_pi * 6.5 * t + 1.7 * math.sin(two_pi * 0.9 * t))
        body = min(1.0, t / 0.35) * math.exp(-max(0.0, t - 2.0) / 0.25)
        gate[i] = (0.25 + 0.75 * g * g) * body
    # grind: brown noise through the gate
    y = 0.0
    for i in range(n):
        y = 0.982 * y + 0.018 * (r.random() * 2 - 1)
        buf[i] += 3.0 * gate[i] * y
    # resonant scrape partials, amplitude follows the same gate
    for f, a in ((84, .30), (123, .22), (167, .15), (236, .09)):
        phase = r.random() * two_pi
        for i in range(n):
            t = i / SR
            wob = 1 + 0.02 * math.sin(two_pi * 4.1 * t + phase)
            buf[i] += a * gate[i] * math.sin(two_pi * f * wob * t + phase)
    # sub swell
    for f, a in ((34, .45), (51, .25)):
        phase = r.random() * two_pi
        for i in range(n):
            t = i / SR
            body = min(1.0, t / 0.5) * math.exp(-max(0.0, t - 1.9) / 0.35)
            buf[i] += a * body * math.sin(two_pi * f * t + phase)
    # final settling THUD at 2.25s + dust trickle
    t0 = int(2.25 * SR)
    for i in range(t0, n):
        t = (i - t0) / SR
        buf[i] += 0.9 * math.exp(-t / 0.16) * math.sin(two_pi * 47 * t)
        buf[i] += 0.5 * math.exp(-t / 0.05) * math.sin(two_pi * 96 * t)
    add_noise(buf, r, amp=1.0, t0=2.25, dur=0.10, tau=0.03, lp=0.5)
    for _ in range(10):  # dust and pebbles after the thud
        add_noise(buf, r, amp=0.18 + r.random() * 0.2,
                  t0=2.35 + r.random() * 0.5, dur=0.03, tau=0.008, lp=0.3)
    return normalize(reverb(buf, 0.28))


def door_speak():
    """Formant-shaped gravel voice: four slow syllables, OH-AH-EH-UM."""
    r = rng("snd", "speak2")
    buf = zeros(2.3)
    two_pi = 2 * math.pi
    sylls = [(0.05, 0.42, 72, (520, 1050)), (0.55, 0.36, 64, (760, 1250)),
             (1.00, 0.50, 58, (640, 1700)), (1.62, 0.50, 50, (320, 700))]
    for (t0, dur, f0, (F1, F2)) in sylls:
        n0 = int(t0 * SR)
        n1 = min(len(buf), n0 + int(dur * SR))
        for h in range(1, 26):
            fh = f0 * h
            if fh > 3000:
                break
            w = (math.exp(-((fh - F1) / 220) ** 2)
                 + 0.7 * math.exp(-((fh - F2) / 320) ** 2)
                 + 0.06) / h ** 0.6
            if w < 0.01:
                continue
            phase = r.random() * two_pi
            for i in range(n0, n1):
                t = (i - n0) / SR
                a = math.sin(math.pi * min(1.0, t / dur)) ** 0.7
                jitter = 1 + 0.012 * math.sin(two_pi * 5.1 * t + h)
                buf[i] += 0.16 * w * a * math.sin(two_pi * fh * jitter * t + phase)
    # gravel bed under the voice
    y = 0.0
    for i in range(len(buf)):
        t = i / SR
        y = 0.988 * y + 0.012 * (r.random() * 2 - 1)
        a = min(1.0, t / 0.25) * math.exp(-max(0.0, t - 1.7) / 0.35)
        buf[i] += 1.1 * a * y
    return normalize(reverb(buf, 0.35))


def banshee_shriek():
    """Detuned scream choir: fast rise, vibrato hold, dying fall + breath."""
    r = rng("snd", "shriek2")
    buf = zeros(2.4)
    two_pi = 2 * math.pi

    def contour(t):
        if t < 0.3:
            return 700 + 1900 * (t / 0.3) ** 1.6
        if t < 1.3:
            return 2600
        return 2600 * math.exp(-(t - 1.3) * 1.1)

    for det, amp in ((1.0, .5), (1.011, .33), (0.987, .33), (0.5, .20), (2.003, .10)):
        phase = r.random() * two_pi
        ph = 0.0
        for i in range(len(buf)):
            t = i / SR
            vib = 1 + 0.045 * math.sin(two_pi * 6.3 * t) * min(1.0, t / 0.35)
            ph += two_pi * contour(t) * det * vib / SR
            a = min(1.0, t / 0.08) * math.exp(-max(0.0, t - 1.5) / 0.35)
            buf[i] += amp * a * math.sin(ph + phase)
    # breath/air layer
    y = 0.0
    for i in range(len(buf)):
        t = i / SR
        y = 0.55 * y + 0.45 * (r.random() * 2 - 1)
        a = min(1.0, t / 0.1) * math.exp(-max(0.0, t - 1.4) / 0.3)
        buf[i] += 0.15 * a * y
    return normalize(reverb(buf, 0.4, ((977, .7), (1361, .65), (1733, .6))))


def spell_cast():
    """Soft breath-whoosh into a warm harmonic bloom (G major add9),
    gentle shimmer, no laser sweep."""
    r = rng("snd", "spell3")
    dur = 1.25
    buf = zeros(dur)
    two_pi = 2 * math.pi
    n = len(buf)
    # whoosh: noise with opening then closing tone (lp coefficient ramps)
    y = 0.0
    for i in range(n):
        t = i / SR
        openness = math.sin(math.pi * min(1.0, t / 0.5)) if t < 0.5 else 0.0
        lp = 0.92 - 0.5 * openness
        y = lp * y + (1 - lp) * (r.random() * 2 - 1)
        buf[i] += 0.85 * openness * y
    # bloom chord: G3 B3 D4 A4 G5 with slow attack and chorused detune
    for f, a, t0 in ((196.0, .30, .12), (246.9, .24, .16), (293.7, .26, .20),
                     (440.0, .16, .26), (784.0, .10, .32)):
        for det in (1.0, 1.006, 0.994):
            phase = r.random() * two_pi
            n0 = int(t0 * SR)
            for i in range(n0, n):
                t = (i - n0) / SR
                a_env = min(1.0, t / 0.10) * math.exp(-t / 0.55)
                trem = 1 + 0.10 * math.sin(two_pi * 5.5 * t + phase)
                buf[i] += (a / 3) * a_env * trem * math.sin(two_pi * f * det * t + phase)
    # faint sparkle dust on the tail
    for _ in range(6):
        f = r.choice((1568, 1976, 2349))
        add_partial(buf, f, 0.05, t0=0.45 + r.random() * 0.45, tau=0.10)
    return normalize(reverb(buf, 0.30))


def level_up():
    """Warm rising fanfare: G–B–D–G chorused swell that lands on a full,
    sustained major chord with soft brass-like body. No plinks."""
    r = rng("snd", "lvl3")
    dur = 2.2
    buf = zeros(dur)
    two_pi = 2 * math.pi
    n = len(buf)
    notes = [(196.0, 0.00), (246.9, 0.16), (293.7, 0.32), (392.0, 0.48)]
    for f, t0 in notes:
        last = f == 392.0
        n0 = int(t0 * SR)
        for det in (1.0, 1.007, 0.993):
            phase = r.random() * two_pi
            for i in range(n0, n):
                t = (i - n0) / SR
                att = min(1.0, t / 0.07)
                rel = math.exp(-max(0.0, t - (1.2 if last else 0.6)) / 0.35)
                a = 0.16 * att * rel * (1.4 if last else 1.0)
                # soft saw-ish brass: first three harmonics
                s = (math.sin(two_pi * f * det * t + phase)
                     + 0.45 * math.sin(two_pi * f * det * 2 * t + phase)
                     + 0.20 * math.sin(two_pi * f * det * 3 * t + phase))
                buf[i] += a * s / 3
        # high octave halo on the landing note
        if last:
            add_partial(buf, 784.0, 0.10, t0=t0 + 0.05, tau=0.8)
            add_partial(buf, 1175.0, 0.05, t0=t0 + 0.1, tau=0.7)
    # soft golden shimmer across the tail
    for _ in range(5):
        add_partial(buf, r.choice((1568, 1976)), 0.04,
                    t0=0.7 + r.random() * 0.8, tau=0.18)
    return normalize(reverb(buf, 0.32))


def guild_pad():
    chord = [130.8, 164.8, 196.0, 261.6]  # C3 E3 G3 C4
    def fn(t):
        v = sum(math.sin(2 * math.pi * f * t + i) for i, f in enumerate(chord)) / len(chord)
        slow = 0.7 + 0.3 * math.sin(2 * math.pi * 0.15 * t)
        return 0.35 * v * slow
    return synth(6.0, fn)


def sword_clash():
    """Steel-on-steel: snap transient, bright clustered ring around 2–4 kHz
    with fast decay, and a low handle knock. Short and punchy."""
    r = rng("snd", "clash3")
    buf = zeros(0.75)
    # snap transient (almost unfiltered, very short)
    add_noise(buf, r, amp=2.2, t0=0.0, dur=0.012, tau=0.0035, lp=0.05)
    add_noise(buf, r, amp=0.9, t0=0.0, dur=0.045, tau=0.012, lp=0.35)
    # bright steel ring: tight inharmonic cluster, rapid decay
    base = 2150
    for mult, pa, tau in ((1.0, .42, .16), (1.17, .30, .13), (1.46, .22, .11),
                          (1.83, .15, .09), (2.52, .10, .07), (0.71, .18, .20)):
        f = base * mult * (1 + (r.random() - .5) * 0.008)
        add_partial(buf, f, pa, t0=0.001, tau=tau)
    # one singing partial carries a short tail
    add_partial(buf, 2870, 0.10, t0=0.004, tau=0.34)
    # low knock of the parry
    add_partial(buf, 168, 0.34, t0=0.0, tau=0.05)
    add_partial(buf, 96, 0.22, t0=0.0, tau=0.07)
    return normalize(reverb(buf, 0.16), peak=0.9)


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
    "door_rumble": "Demon Door opening — juddering stone grind, scrape resonance, settling thud",
    "door_speak": "Demon Door voice — formant-shaped gravel speech, four syllables",
    "banshee_shriek": "Banshee shriek — detuned scream choir with vibrato and dying fall",
    "spell_cast": "Will power cast — breath whoosh into a warm harmonic bloom",
    "level_up": "Level-up — rising chorused fanfare landing on a sustained major chord",
    "guild_pad": "Heroes' Guild ambience — slow C-major drone pad",
    "sword_clash": "Sword clash — snap transient with bright fast-decaying steel ring",
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

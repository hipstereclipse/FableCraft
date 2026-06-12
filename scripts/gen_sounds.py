"""gen_sounds.py - synthesizes a Fable-flavored sound library for the whole addon.

The generator derives cues from content data so every shipped entity and item has
its own sound definition. The output remains sample-free and deterministic.
"""
import html
import math
import shutil
import struct
import wave

from fc_data import all_items
from fc_lib import ROOT, RP, rng, write_json

OUT = RP / "sounds" / "fc"
PREVIEW = ROOT / "sound_preview"
SR = 22050
SPEECH_LEXICON = [
    ((1.00, 0, 1.00, 0.55), (0.92, 1, 0.82, 0.44), (1.08, 0, 0.90, 0.60), (0.98, 1, 0.72, 0.00)),
    ((1.05, 1, 0.92, 0.48), (0.95, 0, 0.78, 0.42), (1.12, 1, 1.00, 0.56), (0.88, 0, 0.70, 0.00)),
    ((0.90, 0, 0.86, 0.40), (1.02, 1, 0.76, 0.36), (1.15, 1, 1.08, 0.66), (0.96, 0, 0.82, 0.00)),
    ((1.08, 1, 1.00, 0.52), (0.94, 0, 0.74, 0.38), (0.98, 1, 0.82, 0.42), (1.16, 0, 0.92, 0.00)),
    ((0.98, 0, 0.88, 0.50), (1.10, 1, 0.98, 0.58), (0.92, 0, 0.76, 0.34), (1.04, 1, 0.84, 0.00)),
]


def write_wav(path, samples):
    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(SR)
        frames = b"".join(
            struct.pack("<h", max(-32767, min(32767, int(sample * 32767))))
            for sample in samples
        )
        wav_file.writeframes(frames)


def zeros(dur):
    return [0.0] * int(SR * dur)


def add_partial(buf, freq, amp, t0=0.0, tau=0.3, phase=0.0, vib_hz=0.0, vib_amt=0.0):
    n0 = int(t0 * SR)
    phi = phase
    two_pi = 2 * math.pi
    for idx in range(n0, len(buf)):
        t = (idx - n0) / SR
        cur_freq = freq
        if vib_hz:
            cur_freq *= 1 + vib_amt * math.sin(two_pi * vib_hz * t)
        phi += two_pi * cur_freq / SR
        amp_now = amp * math.exp(-t / max(tau, 1e-6))
        if amp_now < 0.0005:
            break
        buf[idx] += amp_now * math.sin(phi)


def add_noise(buf, r, amp, t0, dur, tau, lp=0.5):
    n0 = int(t0 * SR)
    n1 = min(len(buf), n0 + int(dur * SR))
    y = 0.0
    for idx in range(n0, n1):
        t = (idx - n0) / SR
        y = lp * y + (1 - lp) * (r.random() * 2 - 1)
        buf[idx] += amp * math.exp(-t / max(tau, 1e-6)) * y


def add_clicks(buf, r, count, amp, t0, spread, tau=0.01):
    for _ in range(count):
        add_noise(buf, r, amp * (0.7 + r.random() * 0.6), t0 + r.random() * spread, 0.02, tau, lp=0.15)


def add_gliss(buf, start_freq, end_freq, amp, t0, dur, phase=0.0):
    n0 = int(t0 * SR)
    n1 = min(len(buf), n0 + int(dur * SR))
    phi = phase
    two_pi = 2 * math.pi
    for idx in range(n0, n1):
        t = (idx - n0) / SR
        frac = t / max(dur, 1e-6)
        freq = start_freq + (end_freq - start_freq) * frac
        phi += two_pi * freq / SR
        buf[idx] += amp * math.sin(phi) * math.exp(-t / max(dur * 0.9, 1e-6))


def add_tremolo_partial(buf, freq, amp, t0, dur, trem_hz, trem_depth, phase=0.0,
                        vib_hz=0.0, vib_amt=0.0):
    n0 = int(t0 * SR)
    n1 = min(len(buf), n0 + int(dur * SR))
    phi = phase
    two_pi = 2 * math.pi
    for idx in range(n0, n1):
        t = (idx - n0) / SR
        env = math.sin(math.pi * min(1.0, t / max(dur, 1e-6))) ** 0.72
        trem = 1.0 - trem_depth * (0.5 + 0.5 * math.sin(two_pi * trem_hz * t))
        cur_freq = freq * (1 + vib_amt * math.sin(two_pi * vib_hz * t) if vib_hz else 1)
        phi += two_pi * cur_freq / SR
        buf[idx] += amp * env * trem * math.sin(phi)


def add_bark(buf, r, base, start, dur, force=1.0):
    add_noise(buf, r, amp=0.38 * force, t0=start, dur=dur * 0.36, tau=dur * 0.12, lp=0.34)
    add_gliss(buf, base * 1.9, base * 0.9, 0.16 * force, start, dur * 0.26,
              phase=r.random() * math.tau)
    add_partial(buf, base, 0.12 * force, t0=start + dur * 0.05, tau=dur * 0.42,
                phase=r.random() * math.tau, vib_hz=7.0, vib_amt=0.055)


def add_whisper_phrase(buf, r, start, syllables, base=118, breath=0.08, formant_shift=1.0):
    formants = [(460 * formant_shift, 980 * formant_shift), (620 * formant_shift, 1320 * formant_shift)]
    phrase = SPEECH_LEXICON[r.randrange(len(SPEECH_LEXICON))]
    add_phrase_from_lexicon(buf, r, base * r.uniform(0.92, 1.08), formants, phrase[:syllables], start,
                            0.16 + r.random() * 0.04, breath, roughness=0.06, stretch=1.18)


def reverb(buf, mix=0.22, taps=((911, 0.63), (1229, 0.57), (1699, 0.52))):
    wet = [0.0] * len(buf)
    for delay, gain in taps:
        comb = [0.0] * len(buf)
        for idx in range(len(buf)):
            comb[idx] = buf[idx] + (comb[idx - delay] * gain if idx >= delay else 0.0)
        for idx in range(len(buf)):
            wet[idx] += (comb[idx] - buf[idx]) / len(taps)
    return [buf[idx] + wet[idx] * mix for idx in range(len(buf))]


def normalize(buf, peak=0.88):
    mx = max(1e-6, max(abs(sample) for sample in buf))
    return [sample * peak / mx for sample in buf]


def harmonic_cluster(buf, freqs, amp, t0, tau, r, jitter=0.012):
    for freq in freqs:
        add_partial(
            buf,
            freq * (1 + (r.random() - 0.5) * jitter),
            amp * (0.8 + r.random() * 0.4),
            t0=t0 + r.random() * 0.02,
            tau=tau * (0.85 + r.random() * 0.35),
            phase=r.random() * math.tau,
            vib_hz=4.0 + r.random() * 2.5,
            vib_amt=jitter * 0.35,
        )


def note_freq(midi_note):
    return 440.0 * (2 ** ((midi_note - 69) / 12))


def motif(root_midi, offsets):
    return [note_freq(root_midi + off) for off in offsets]


def mix_buffers(*buffers):
    size = max(len(buf) for buf in buffers)
    out = [0.0] * size
    for buf in buffers:
        for idx, sample in enumerate(buf):
            out[idx] += sample
    return out


def add_formant_babble(buf, r, base, formants, starts, syllable_tau, breath_amp, roughness=0.0):
    for start in starts:
        syllable = base * r.uniform(0.9, 1.12)
        for harm in range(1, 7):
            amp = (0.10 / (harm ** 0.72)) * r.uniform(0.82, 1.18)
            add_partial(
                buf,
                syllable * harm,
                amp,
                t0=start,
                tau=syllable_tau * r.uniform(0.9, 1.2),
                phase=r.random() * math.tau,
                vib_hz=3.5 + r.random() * 1.8,
                vib_amt=0.008 + roughness * 0.02,
            )
        add_partial(buf, formants[0] * r.uniform(0.94, 1.06), 0.036, t0=start + 0.015,
                    tau=syllable_tau * 0.9, phase=r.random() * math.tau)
        add_partial(buf, formants[1] * r.uniform(0.94, 1.07), 0.022, t0=start + 0.022,
                    tau=syllable_tau * 0.75, phase=r.random() * math.tau)
        add_noise(buf, r, amp=breath_amp, t0=start, dur=syllable_tau * 0.45,
                  tau=syllable_tau * 0.28, lp=0.55 - roughness * 0.18)
        if roughness:
            add_noise(buf, r, amp=breath_amp * (0.6 + roughness), t0=start + 0.01,
                      dur=syllable_tau * 0.2, tau=syllable_tau * 0.1, lp=0.28)


def add_growl(buf, r, base, start, dur, noise_amp, pitch_lift=0.0):
    add_partial(buf, base, 0.18, t0=start, tau=dur * 0.75, phase=r.random() * math.tau,
                vib_hz=4.6, vib_amt=0.045)
    add_partial(buf, base * 1.52, 0.12, t0=start, tau=dur * 0.62, phase=r.random() * math.tau,
                vib_hz=5.1, vib_amt=0.03)
    add_partial(buf, base * 2.05, 0.07, t0=start + 0.01, tau=dur * 0.45,
                phase=r.random() * math.tau)
    add_noise(buf, r, amp=noise_amp, t0=start, dur=dur * 0.55, tau=dur * 0.24, lp=0.58)
    if pitch_lift:
        add_gliss(buf, base * 2.1, base * (2.6 + pitch_lift), 0.08, start + 0.04, dur * 0.3,
                  phase=r.random() * math.tau)


def add_grunt(buf, r, base, start, dur, click_count=0):
    harmonic_cluster(buf, [base, base * 1.48, base * 2.08], 0.12, start, dur * 0.45, r, jitter=0.012)
    add_noise(buf, r, amp=0.34, t0=start, dur=dur * 0.32, tau=dur * 0.14, lp=0.68)
    if click_count:
        add_clicks(buf, r, click_count, 0.08, start + 0.03, dur * 0.22, tau=0.012)


def add_distant_murmurs(buf, r, profile, variant_idx=0):
    profiles = {
        "guild": [(96, [(420, 920), (560, 1160)], 0.018, 0.12), (128, [(560, 1180), (700, 1420)], 0.012, 0.06)],
        "village": [(112, [(460, 1000), (620, 1280)], 0.016, 0.08), (142, [(640, 1300), (760, 1540)], 0.012, 0.05)],
        "bandit": [(82, [(380, 820), (480, 980)], 0.020, 0.18), (96, [(440, 900), (540, 1080)], 0.018, 0.22)],
        "graveyard": [(78, [(340, 720), (440, 900)], 0.014, 0.04), (122, [(520, 1120), (620, 1300)], 0.010, 0.03)],
    }
    phrase_count = 3 + variant_idx
    for idx in range(phrase_count):
        base, formants, breath, rough = profiles[profile][idx % len(profiles[profile])]
        start = 0.5 + idx * 0.82 + r.random() * 0.25
        phrase = SPEECH_LEXICON[(idx + variant_idx) % len(SPEECH_LEXICON)]
        add_phrase_from_lexicon(buf, r, base * r.uniform(0.92, 1.08), formants, phrase, start,
                                0.10 + r.random() * 0.035, breath, roughness=rough, stretch=1.0 + r.random() * 0.35)


def synth_ambient(spec, r, variant_idx=0):
    dur = 4.8 + 0.25 * variant_idx
    buf = zeros(dur)
    notes = motif(48 + variant_idx, [0, 4, 7, 12])
    for idx, freq in enumerate(notes):
        add_partial(buf, freq, 0.12 + idx * 0.02, tau=dur * 2.2, phase=idx,
                    vib_hz=0.12 + idx * 0.05 + variant_idx * 0.02, vib_amt=0.012)
    add_noise(buf, r, amp=0.05, t0=0.0, dur=dur, tau=dur * 1.3, lp=0.95)
    if "water" in spec["tags"]:
        add_clicks(buf, r, 5 + variant_idx, 0.06, 1.0, 2.6, tau=0.03)
    if "guild" in spec["tags"]:
        harmonic_cluster(buf, motif(55, [0, 4, 7]), 0.04, 0.35, 1.4, r, jitter=0.006)
    if "market" in spec["tags"]:
        add_clicks(buf, r, 8 + variant_idx, 0.035, 0.3, 3.4, tau=0.018)
        harmonic_cluster(buf, [220, 294, 392], 0.018, 0.7, 0.7, r, jitter=0.018)
    if "camp" in spec["tags"]:
        add_noise(buf, r, amp=0.08, t0=0.2, dur=1.4, tau=0.55, lp=0.72)
        add_clicks(buf, r, 6 + variant_idx, 0.055, 0.6, 2.6, tau=0.018)
    if "grave" in spec["tags"]:
        add_noise(buf, r, amp=0.10, t0=0.0, dur=dur, tau=dur * 0.95, lp=0.82)
        add_gliss(buf, 520 + 40 * variant_idx, 220, 0.035, 0.8, 1.3, phase=r.random() * math.tau)
    if "npc_murmur" in spec["tags"]:
        if "bandit" in spec["tags"]:
            add_distant_murmurs(buf, r, "bandit", variant_idx)
        elif "grave" in spec["tags"]:
            add_distant_murmurs(buf, r, "graveyard", variant_idx)
        elif "market" in spec["tags"]:
            add_distant_murmurs(buf, r, "village", variant_idx)
        else:
            add_distant_murmurs(buf, r, "guild", variant_idx)
    return normalize(reverb(buf, mix=0.34), peak=0.82)


def synth_demon_door(spec, r):
    voice = zeros(2.2)
    add_formant_babble(voice, r, 66, (540, 980), [0.06, 0.28, 0.52, 0.88, 1.22], 0.22, 0.045, roughness=0.18)
    for base in (58, 49):
        add_partial(voice, base, 0.12, t0=0.04, tau=0.7, phase=r.random() * math.tau,
                    vib_hz=1.6, vib_amt=0.018)
    stone = zeros(2.2)
    add_noise(stone, r, amp=0.55, t0=0.0, dur=1.2, tau=0.38, lp=0.86)
    harmonic_cluster(stone, [44, 63, 89, 126], 0.15, 0.02, 0.8, r, jitter=0.008)
    if "door" in spec["tags"]:
        add_partial(stone, 51, 0.36, t0=1.78, tau=0.18, phase=r.random() * math.tau)
    return normalize(reverb(mix_buffers(stone, voice), mix=0.3), peak=0.88)


def add_syllable_babble(buf, r, base_freq, syllables, formants, intensity=1.0, rasp=0.0, start=0.04):
    cursor = start
    for _ in range(syllables):
        dur = 0.09 + r.random() * 0.10
        gap = 0.025 + r.random() * 0.05
        if cursor + dur >= len(buf) / SR:
            break
        attack = 0.015 + r.random() * 0.015
        release = 0.03 + r.random() * 0.03
        local = zeros(dur)
        syll_f0 = base_freq * (0.92 + r.random() * 0.18)
        for harm in range(1, 7):
            weight = (0.11 * intensity) / (harm ** 0.68)
            add_partial(
                local,
                syll_f0 * harm,
                weight,
                t0=0.0,
                tau=max(0.04, dur * 0.7),
                phase=r.random() * math.tau,
                vib_hz=3.8 + r.random() * 2.1,
                vib_amt=0.008 + r.random() * 0.01,
            )
        f1, f2 = r.choice(formants)
        add_partial(local, f1 * (0.97 + r.random() * 0.06), 0.06 * intensity,
                    t0=0.01, tau=max(0.03, dur * 0.55), phase=r.random() * math.tau)
        add_partial(local, f2 * (0.97 + r.random() * 0.06), 0.035 * intensity,
                    t0=0.015, tau=max(0.03, dur * 0.5), phase=r.random() * math.tau)
        if rasp:
            add_noise(local, r, amp=0.09 * rasp, t0=0.0, dur=dur, tau=max(0.03, dur * 0.6), lp=0.58)
        for idx in range(len(local)):
            t = idx / SR
            local[idx] *= max(0.0, min(1.0, t / attack))
            tail = dur - t
            if tail < release:
                local[idx] *= max(0.0, tail / release)
        start_idx = int(cursor * SR)
        for idx, sample in enumerate(local):
            if start_idx + idx < len(buf):
                buf[start_idx + idx] += sample
        cursor += dur + gap


def add_phrase_from_lexicon(buf, r, base_freq, formants, phrase, start, syllable_tau,
                            breath_amp, roughness=0.0, stretch=1.0):
    cursor = start
    for pitch_mul, formant_idx, accent, gap_mul in phrase:
        dur = syllable_tau * stretch * (0.86 + accent * 0.34)
        syllable = base_freq * pitch_mul * r.uniform(0.985, 1.015)
        for harm in range(1, 7):
            amp = ((0.11 * accent) / (harm ** 0.72)) * r.uniform(0.94, 1.07)
            add_partial(
                buf,
                syllable * harm,
                amp,
                t0=cursor,
                tau=dur * r.uniform(0.88, 1.12),
                phase=r.random() * math.tau,
                vib_hz=3.2 + r.random() * 1.4,
                vib_amt=0.008 + roughness * 0.02,
            )
        f1, f2 = formants[min(formant_idx, len(formants) - 1)]
        add_partial(buf, f1 * r.uniform(0.98, 1.03), 0.034 * accent, t0=cursor + dur * 0.12,
                    tau=dur * 0.66, phase=r.random() * math.tau)
        add_partial(buf, f2 * r.uniform(0.98, 1.04), 0.020 * accent, t0=cursor + dur * 0.18,
                    tau=dur * 0.52, phase=r.random() * math.tau)
        add_noise(buf, r, amp=breath_amp * accent, t0=cursor, dur=dur * 0.44,
                  tau=dur * 0.24, lp=0.56 - roughness * 0.16)
        if roughness:
            add_noise(buf, r, amp=breath_amp * (0.45 + roughness) * accent, t0=cursor + dur * 0.05,
                      dur=dur * 0.2, tau=dur * 0.08, lp=0.26)
        cursor += dur + syllable_tau * stretch * gap_mul


def phrase_variants(spec, count=3):
    offset = rng("speech-lexicon", spec["key"]).randrange(len(SPEECH_LEXICON))
    return [SPEECH_LEXICON[(offset + idx) % len(SPEECH_LEXICON)] for idx in range(count)]


def variant_seed(spec, variant_idx):
    return rng("variant", spec["key"], str(variant_idx))


def synth_babbling_human(spec, r, variant_idx=0):
    dur = 1.18
    buf = zeros(dur)
    role = spec.get("role", "folk")
    roles = {
        "folk": {"base": 128, "formants": [(520, 1120), (640, 1320)], "breath": 0.07, "rasp": 0.10, "tau": 0.12, "stretch": 1.00},
        "guard": {"base": 104, "formants": [(430, 920), (520, 1180)], "breath": 0.05, "rasp": 0.16, "tau": 0.11, "stretch": 0.92},
        "hero": {"base": 118, "formants": [(500, 980), (620, 1260)], "breath": 0.05, "rasp": 0.08, "tau": 0.115, "stretch": 0.98},
        "seer": {"base": 92, "formants": [(360, 760), (470, 980)], "breath": 0.08, "rasp": 0.04, "tau": 0.14, "stretch": 1.12},
        "bandit": {"base": 98, "formants": [(460, 900), (560, 1080)], "breath": 0.09, "rasp": 0.22, "tau": 0.10, "stretch": 0.88},
        "noble": {"base": 142, "formants": [(620, 1280), (720, 1520)], "breath": 0.05, "rasp": 0.03, "tau": 0.11, "stretch": 1.04},
    }
    cfg = roles[role]
    phrase = phrase_variants(spec)[variant_idx % 3]
    pitch_profiles = {
        "low": (0.78, 0.92, 0.94),
        "midlow": (0.88, 0.96, 0.98),
        "neutral": (1.0, 1.0, 1.0),
        "high": (1.22, 1.08, 1.05),
    }
    pitch_mul, formant_mul, speed_mul = pitch_profiles.get(spec.get("pitch_profile", "neutral"), pitch_profiles["neutral"])
    npc_tone = rng("speech-voice", spec["key"]).uniform(0.94, 1.08) * pitch_mul
    npc_speed = rng("speech-rate", spec["key"]).uniform(0.92, 1.08) * speed_mul
    formants = [(f1 * formant_mul, f2 * formant_mul) for f1, f2 in cfg["formants"]]
    add_phrase_from_lexicon(
        buf,
        r,
        cfg["base"] * npc_tone,
        formants,
        phrase,
        0.05,
        cfg["tau"] / npc_speed,
        cfg["breath"],
        roughness=cfg["rasp"],
        stretch=cfg["stretch"] / npc_speed,
    )
    if role in {"guard", "bandit"}:
        add_noise(buf, r, amp=0.08 if role == "guard" else 0.12, t0=0.02, dur=0.07, tau=0.03, lp=0.40)
    if role == "seer":
        harmonic_cluster(buf, [392, 587, 784], 0.018, 0.24, 0.22, r, jitter=0.006)
    if role == "hero":
        harmonic_cluster(buf, motif(57, [0, 4, 7]), 0.015, 0.18, 0.20, r, jitter=0.005)
    return normalize(reverb(buf, mix=0.18), peak=0.8)


def synth_babbling_demon_door(spec, r, variant_idx=0):
    stone = synth_demon_door(spec, r)
    babble = zeros(2.2)
    formants = [(480, 900), (340, 640), (720, 1180)]
    phrase = phrase_variants(spec)[variant_idx % 3]
    npc_tone = rng("speech-voice", spec["key"]).uniform(0.88, 0.96)
    npc_speed = rng("speech-rate", spec["key"]).uniform(0.80, 0.92)
    add_phrase_from_lexicon(babble, r, 68 * npc_tone, formants, phrase, 0.08, 0.16 / npc_speed,
                            0.05, roughness=0.28, stretch=1.18 / npc_speed)
    add_partial(babble, 76, 0.08, t0=0.0, tau=1.1, phase=r.random() * math.tau, vib_hz=1.7, vib_amt=0.03)
    return normalize(reverb(mix_buffers(stone, babble), mix=0.24), peak=0.88)


def synth_balverine(spec, r, variant_idx=0):
    rv = variant_seed(spec, variant_idx)
    dur = (1.7 if "boss" in spec["tags"] else 1.32) + variant_idx * 0.08
    buf = zeros(dur)
    is_boss = "boss" in spec["tags"]
    is_frost = "frost" in spec["definition"]
    is_white = "white" in spec["definition"]
    low = (62 if is_boss else 78) * (0.96 + 0.025 * variant_idx)
    high = (88 if is_boss else 110) * (0.94 + 0.035 * variant_idx)
    add_growl(buf, r, low, 0.0, 0.50 + 0.05 * variant_idx, 0.30 + 0.03 * variant_idx, pitch_lift=0.18 + 0.08 * variant_idx)
    add_bark(buf, r, high * 1.15, 0.19 + 0.03 * variant_idx, 0.22 + 0.02 * variant_idx, force=1.08 if is_boss else 0.92)
    add_growl(buf, r, high, 0.38 + 0.05 * variant_idx, 0.32 + 0.04 * variant_idx, 0.17 + 0.02 * variant_idx, pitch_lift=0.52 + 0.10 * variant_idx)
    add_tremolo_partial(buf, low * 0.52, 0.10 if is_boss else 0.065, 0.02, dur * 0.72, 5.5 + variant_idx, 0.38,
                        phase=r.random() * math.tau, vib_hz=2.8, vib_amt=0.045)
    add_gliss(buf, 190 + 22 * variant_idx, (560 if is_boss else 440) + 35 * variant_idx, 0.20, 0.08, 0.34 + 0.03 * variant_idx,
              phase=r.random() * math.tau)
    add_gliss(buf, 720 + 50 * variant_idx, 260 + 14 * variant_idx, 0.08, 0.46, 0.42,
              phase=r.random() * math.tau)
    add_noise(buf, r, amp=0.28 + 0.03 * variant_idx, t0=0.0, dur=0.64 + 0.04 * variant_idx, tau=0.24, lp=0.50 + rv.random() * 0.04)
    add_clicks(buf, r, (9 if is_boss else 6) + variant_idx * 2, 0.095, 0.15 + 0.04 * variant_idx, 0.42 + 0.05 * variant_idx, tau=0.010)
    harmonic_cluster(buf, [312 + 16 * variant_idx, 468 + 20 * variant_idx, 702 + 26 * variant_idx], 0.035, 0.22, 0.38, r, jitter=0.026)
    if is_white:
        add_gliss(buf, 520 + 30 * variant_idx, 880 + 45 * variant_idx, 0.075, 0.72, 0.36,
                  phase=r.random() * math.tau)
    if is_frost:
        harmonic_cluster(buf, [980 + 45 * variant_idx, 1320 + 60 * variant_idx, 1760 + 70 * variant_idx], 0.035, 0.58, 0.24, r, jitter=0.008)
        add_noise(buf, r, amp=0.09, t0=0.64, dur=0.34, tau=0.18, lp=0.90)
    return normalize(reverb(buf, mix=0.24), peak=0.88)


def synth_hobbe(spec, r, variant_idx=0):
    dur = 0.9 + variant_idx * 0.08
    buf = zeros(dur)
    starts = [(0.03, [280, 340, 405]), (0.14, [300, 362, 430]), (0.28, [260, 322, 395]), (0.44, [286, 348, 418])]
    for start, freqs in starts[:3 + (1 if variant_idx > 0 else 0)]:
        shifted = [freq + variant_idx * 12 for freq in freqs]
        harmonic_cluster(buf, shifted, 0.055, start + 0.02 * variant_idx, 0.08 + variant_idx * 0.015, r, jitter=0.028)
        add_noise(buf, r, amp=0.11, t0=start, dur=0.05, tau=0.02, lp=0.22)
    add_clicks(buf, r, 9 + variant_idx * 2, 0.11, 0.02, 0.42 + variant_idx * 0.06, tau=0.012)
    if "scout" in spec["definition"]:
        add_noise(buf, r, amp=0.08, t0=0.48 + variant_idx * 0.06, dur=0.10, tau=0.04, lp=0.35)
    return normalize(reverb(buf, mix=0.14), peak=0.84)


def synth_ghost(spec, r, variant_idx=0):
    is_wraith = "wraith" in spec["definition"] or "cry" in spec["tags"]
    is_banshee = "banshee" in spec["definition"] or ("shriek" in spec["tags"] and not is_wraith)
    dur = (2.2 if is_wraith else (2.45 if is_banshee else 1.45)) + 0.08 * variant_idx
    buf = zeros(dur)
    add_noise(buf, r, amp=0.20 if not is_wraith else 0.24, t0=0.0, dur=dur, tau=dur * 0.9, lp=0.73)
    if is_wraith:
        add_gliss(buf, 620 + 70 * variant_idx, 2100 + 120 * variant_idx, 0.22, 0.05, 0.62 + 0.05 * variant_idx, phase=r.random() * math.tau)
        add_gliss(buf, 1320 + 60 * variant_idx, 760 - 40 * variant_idx, 0.12, 0.44, 0.70, phase=r.random() * math.tau)
        for start in (0.18, 0.64 + 0.04 * variant_idx, 1.14 + 0.05 * variant_idx):
            harmonic_cluster(buf, [248 + 14 * variant_idx, 320 + 18 * variant_idx, 408 + 20 * variant_idx], 0.05, start, 0.22, r, jitter=0.014)
            add_noise(buf, r, amp=0.08, t0=start, dur=0.16, tau=0.08, lp=0.42)
    elif is_banshee:
        add_whisper_phrase(buf, r, 0.05, 3, base=150 + 8 * variant_idx, breath=0.09, formant_shift=1.12)
        add_tremolo_partial(buf, 286 + 18 * variant_idx, 0.10, 0.02, 1.15, 8.0 + variant_idx, 0.62,
                            phase=r.random() * math.tau, vib_hz=5.4, vib_amt=0.05)
        add_tremolo_partial(buf, 432 + 25 * variant_idx, 0.065, 0.10, 0.95, 11.0 + variant_idx, 0.70,
                            phase=r.random() * math.tau, vib_hz=6.5, vib_amt=0.04)
        add_gliss(buf, 740 + 80 * variant_idx, 2840 + 170 * variant_idx, 0.23, 0.36, 0.58 + 0.03 * variant_idx, phase=r.random() * math.tau)
        add_gliss(buf, 1280 + 75 * variant_idx, 3180 - 130 * variant_idx, 0.18, 0.48, 0.72, phase=r.random() * math.tau)
        add_gliss(buf, 2350 + 80 * variant_idx, 820 - 50 * variant_idx, 0.10, 1.05, 0.86, phase=r.random() * math.tau)
        for start in (0.28, 0.78 + 0.04 * variant_idx, 1.45):
            harmonic_cluster(buf, [510 + 20 * variant_idx, 710 + 28 * variant_idx, 1040 + 42 * variant_idx], 0.034, start, 0.30, r, jitter=0.02)
            add_noise(buf, r, amp=0.075, t0=start, dur=0.18, tau=0.08, lp=0.34)
    else:
        for freq in (150, 232, 346, 518):
            add_partial(buf, freq + 18 * variant_idx, 0.09, t0=0.06, tau=0.7, phase=r.random() * math.tau,
                        vib_hz=4.0, vib_amt=0.012)
    if "void" in spec["tags"]:
        add_partial(buf, 74, 0.11, t0=0.02, tau=0.65, phase=r.random() * math.tau,
                    vib_hz=1.8, vib_amt=0.05)
    return normalize(reverb(buf, mix=0.38), peak=0.84)


def synth_undead(spec, r, variant_idx=0):
    dur = 0.95 + 0.08 * variant_idx
    buf = zeros(dur)
    add_clicks(buf, r, (12 if "knight" in spec["definition"] else 8) + variant_idx * 2, 0.14, 0.0, 0.42 + 0.06 * variant_idx, tau=0.015)
    add_noise(buf, r, amp=0.14, t0=0.02, dur=0.14 + 0.02 * variant_idx, tau=0.05, lp=0.48)
    harmonic_cluster(buf, [118 + 10 * variant_idx, 154 + 12 * variant_idx, 208 + 16 * variant_idx], 0.04, 0.04, 0.22, r, jitter=0.01)
    if "knight" in spec["definition"] or "soldier" in spec["definition"]:
        harmonic_cluster(buf, [920 + 60 * variant_idx, 1280 + 80 * variant_idx, 1700 + 120 * variant_idx], 0.03, 0.01, 0.12, r, jitter=0.016)
    return normalize(reverb(buf, mix=0.22), peak=0.83)


def synth_troll(spec, r, variant_idx=0):
    dur = 1.12 + 0.12 * variant_idx
    buf = zeros(dur)
    harmonic_cluster(buf, [46 + 2 * variant_idx, 69 + 4 * variant_idx, 91 + 5 * variant_idx, 128 + 6 * variant_idx], 0.18, 0.0, 0.48 + 0.04 * variant_idx, r, jitter=0.01)
    add_noise(buf, r, amp=0.56, t0=0.0, dur=0.22 + 0.02 * variant_idx, tau=0.10, lp=0.82)
    add_grunt(buf, r, 56 + 4 * variant_idx, 0.08, 0.26 + 0.04 * variant_idx, click_count=3 + variant_idx)
    add_clicks(buf, r, 8 + variant_idx, 0.09, 0.08, 0.28 + 0.04 * variant_idx, tau=0.012)
    if "ice_troll" in spec["definition"]:
        harmonic_cluster(buf, [980 + 40 * variant_idx, 1230 + 60 * variant_idx], 0.025, 0.24, 0.14, r, jitter=0.01)
    return normalize(reverb(buf, mix=0.18), peak=0.9)


def synth_insect(spec, r, variant_idx=0):
    dur = 0.8 + 0.07 * variant_idx
    buf = zeros(dur)
    definition = spec["definition"]
    if "wasp" in definition:
        for freq in (214 + 10 * variant_idx, 228 + 12 * variant_idx, 242 + 14 * variant_idx, 256 + 16 * variant_idx):
            add_partial(buf, freq, 0.09, t0=0.0, tau=dur * 0.9, phase=r.random() * math.tau,
                        vib_hz=31.0 + variant_idx * 2.5, vib_amt=0.13)
        add_gliss(buf, 1450 + 80 * variant_idx, 1950 + 110 * variant_idx, 0.05, 0.06, 0.18, phase=r.random() * math.tau)
        add_gliss(buf, 1880 + 60 * variant_idx, 1560 + 30 * variant_idx, 0.04, 0.28, 0.16, phase=r.random() * math.tau)
        add_noise(buf, r, amp=0.05, t0=0.0, dur=0.18, tau=0.06, lp=0.12)
    elif "beetle" in definition:
        for freq in (156 + 8 * variant_idx, 168 + 9 * variant_idx, 182 + 10 * variant_idx):
            add_partial(buf, freq, 0.11, t0=0.0, tau=dur * 0.82, phase=r.random() * math.tau,
                        vib_hz=18.0 + variant_idx * 1.8, vib_amt=0.10)
        add_clicks(buf, r, 5 + variant_idx, 0.07, 0.08, 0.34 + 0.05 * variant_idx, tau=0.012)
        add_noise(buf, r, amp=0.05, t0=0.04, dur=0.12, tau=0.05, lp=0.22)
    else:
        for freq in (188 + 10 * variant_idx, 206 + 12 * variant_idx, 224 + 14 * variant_idx):
            add_partial(buf, freq, 0.1, t0=0.0, tau=dur * 0.8, phase=r.random() * math.tau,
                        vib_hz=22.0 + variant_idx * 1.5, vib_amt=0.11)
        harmonic_cluster(buf, [1260 + 90 * variant_idx, 1480 + 100 * variant_idx, 1730 + 120 * variant_idx], 0.03, 0.03, 0.18, r, jitter=0.018)
    harmonic_cluster(buf, [1600, 1870, 2130], 0.032, 0.02, 0.16, r, jitter=0.02)
    if "queen" in definition or "arachanox" in definition:
        add_noise(buf, r, amp=0.08, t0=0.05, dur=0.16, tau=0.06, lp=0.28)
    return normalize(reverb(buf, mix=0.08), peak=0.8)


def synth_human(spec, r):
    dur = 1.02
    buf = zeros(dur)
    role = spec.get("role", "folk")
    roles = {
        "folk": (126, (540, 1100), 0.07, [0.04, 0.22, 0.44, 0.68], 0.13, 0.04),
        "guard": (100, (420, 900), 0.05, [0.03, 0.18, 0.38, 0.62], 0.15, 0.07),
        "hero": (116, (500, 980), 0.05, [0.05, 0.26, 0.49, 0.73], 0.15, 0.03),
        "seer": (90, (380, 760), 0.08, [0.06, 0.28, 0.56], 0.19, 0.02),
        "bandit": (98, (470, 940), 0.09, [0.02, 0.14, 0.31, 0.49, 0.68], 0.12, 0.12),
        "noble": (138, (620, 1260), 0.05, [0.06, 0.27, 0.51, 0.76], 0.12, 0.02),
    }
    base, formants, breath, starts, syllable_tau, roughness = roles[role]
    add_formant_babble(buf, r, base, formants, starts, syllable_tau, breath, roughness=roughness)
    if role in {"guard", "bandit"}:
        add_clicks(buf, r, 2 if role == "guard" else 3, 0.08, 0.08, 0.16, tau=0.014)
        add_noise(buf, r, amp=0.10 if role == "bandit" else 0.07, t0=0.02, dur=0.05, tau=0.03, lp=0.34)
    if role == "seer":
        harmonic_cluster(buf, [392, 587, 784], 0.02, 0.18, 0.24, r, jitter=0.008)
    if role == "hero":
        harmonic_cluster(buf, motif(57, [0, 4, 7]), 0.018, 0.16, 0.24, r, jitter=0.006)
    if role == "noble":
        harmonic_cluster(buf, [698, 1046], 0.015, 0.18, 0.12, r, jitter=0.006)
    return normalize(reverb(buf, mix=0.16), peak=0.8)


def synth_void_boss(spec, r, variant_idx=0):
    dur = 1.75 + 0.12 * variant_idx
    buf = zeros(dur)
    harmonic_cluster(buf, [41 + variant_idx, 82 + 2 * variant_idx, 155 + 4 * variant_idx, 233 + 5 * variant_idx], 0.12, 0.0, 0.8, r, jitter=0.008)
    add_noise(buf, r, amp=0.22, t0=0.04, dur=0.7 + 0.05 * variant_idx, tau=0.22, lp=0.74)
    add_grunt(buf, r, 58 + 3 * variant_idx, 0.06, 0.34, click_count=4 + variant_idx)
    add_grunt(buf, r, 52 + 4 * variant_idx, 0.28 + 0.03 * variant_idx, 0.28, click_count=3 + variant_idx)
    add_gliss(buf, 330 + 30 * variant_idx, 920 + 75 * variant_idx, 0.08, 0.10, 0.24, phase=r.random() * math.tau)
    if "dragon" in spec["definition"]:
        add_gliss(buf, 540 + 45 * variant_idx, 1200 + 80 * variant_idx, 0.1, 0.18, 0.26, phase=r.random() * math.tau)
        add_noise(buf, r, amp=0.12, t0=0.18, dur=0.28, tau=0.08, lp=0.28)
    return normalize(reverb(buf, mix=0.26), peak=0.88)


def synth_blade_item(spec, r, variant_idx=0):
    dur = 0.72 + 0.06 * variant_idx
    buf = zeros(dur)
    add_noise(buf, r, amp=1.0, t0=0.0, dur=0.028, tau=0.01, lp=0.12)
    harmonic_cluster(buf, [820 + 90 * variant_idx, 1260 + 110 * variant_idx, 1830 + 140 * variant_idx, 2580 + 160 * variant_idx], 0.11, 0.005, 0.15, r, jitter=0.02)
    add_gliss(buf, 2450 + 120 * variant_idx, 920 + 40 * variant_idx, 0.12, 0.01, 0.15 + 0.02 * variant_idx, phase=r.random() * math.tau)
    add_clicks(buf, r, 3 + variant_idx, 0.12, 0.04, 0.14 + 0.04 * variant_idx, tau=0.01)
    add_partial(buf, 196 + 18 * variant_idx, 0.09, t0=0.03, tau=0.18, phase=r.random() * math.tau)
    item_id = spec.get("source_id", "")
    if item_id in {"sword_of_aeons", "jack_of_blades_mask"}:
        add_partial(buf, 84, 0.11, t0=0.03, tau=0.28, phase=r.random() * math.tau,
                    vib_hz=2.0, vib_amt=0.04)
    if item_id == "avos_tear":
        harmonic_cluster(buf, [1046, 1396, 1760], 0.04, 0.06, 0.16, r, jitter=0.005)
    return normalize(reverb(buf, mix=0.18), peak=0.89)


def synth_bow_item(spec, r):
    dur = 0.58
    buf = zeros(dur)
    harmonic_cluster(buf, [196, 294, 440, 660], 0.09, 0.0, 0.16, r, jitter=0.01)
    add_noise(buf, r, amp=0.24, t0=0.0, dur=0.022, tau=0.008, lp=0.04)
    if "crossbow" in spec.get("source_kind", ""):
        add_clicks(buf, r, 3, 0.10, 0.02, 0.05, tau=0.012)
    return normalize(reverb(buf, mix=0.1), peak=0.86)


def synth_potion_item(spec, r, variant_idx=0):
    dur = 0.66 + 0.07 * variant_idx
    buf = zeros(dur)
    add_clicks(buf, r, 3 + variant_idx, 0.08, 0.0, 0.05 + 0.03 * variant_idx, tau=0.015)
    add_gliss(buf, 180 + 20 * variant_idx, 120 + 12 * variant_idx, 0.1, 0.04, 0.18 + 0.03 * variant_idx, phase=r.random() * math.tau)
    add_noise(buf, r, amp=0.10, t0=0.10, dur=0.08 + 0.02 * variant_idx, tau=0.04, lp=0.64)
    if "will" in spec.get("source_id", "") or "ages_" in spec.get("source_id", ""):
        harmonic_cluster(buf, [1175, 1568], 0.03, 0.22, 0.14, r, jitter=0.008)
    if "resurrection" in spec.get("source_id", ""):
        add_partial(buf, 92, 0.09, t0=0.12, tau=0.28, phase=r.random() * math.tau)
    return normalize(reverb(buf, mix=0.16), peak=0.84)


def synth_food_item(spec, r, variant_idx=0):
    dur = 0.46 + 0.06 * variant_idx
    buf = zeros(dur)
    add_noise(buf, r, amp=0.22 + 0.03 * variant_idx, t0=0.0, dur=0.06 + 0.02 * variant_idx, tau=0.025, lp=0.18)
    add_clicks(buf, r, 2 + variant_idx, 0.08, 0.04, 0.05 + 0.03 * variant_idx, tau=0.012)
    if spec.get("source_kind") == "pie":
        harmonic_cluster(buf, [262 + 20 * variant_idx, 392 + 30 * variant_idx, 523 + 35 * variant_idx], 0.03, 0.03, 0.10, r, jitter=0.012)
    return normalize(reverb(buf, mix=0.08), peak=0.82)


def synth_paper_item(spec, r, variant_idx=0):
    dur = 0.74 + 0.08 * variant_idx
    buf = zeros(dur)
    add_noise(buf, r, amp=0.22, t0=0.0, dur=0.08 + 0.02 * variant_idx, tau=0.04, lp=0.2)
    add_noise(buf, r, amp=0.11, t0=0.12 + 0.03 * variant_idx, dur=0.07, tau=0.04, lp=0.24)
    if "spell_" in spec.get("source_id", ""):
        harmonic_cluster(buf, motif(60 + variant_idx, [0, 4, 7, 11]), 0.025, 0.15, 0.26, r, jitter=0.007)
    if spec.get("source_id") == "jack_of_blades_mask":
        add_partial(buf, 128, 0.10, t0=0.08, tau=0.24, phase=r.random() * math.tau)
    return normalize(reverb(buf, mix=0.16), peak=0.8)


def synth_trinket_item(spec, r, variant_idx=0):
    dur = 0.48 + 0.06 * variant_idx
    buf = zeros(dur)
    harmonic_cluster(buf, [880 + 55 * variant_idx, 1175 + 70 * variant_idx, 1760 + 110 * variant_idx], 0.05, 0.0, 0.12, r, jitter=0.007)
    if "septimal_key" in spec.get("source_id", "") or "guild_seal" in spec.get("source_id", ""):
        harmonic_cluster(buf, [1046, 1396], 0.04, 0.08, 0.18, r, jitter=0.004)
    if "jack_of_blades_mask" in spec.get("source_id", ""):
        add_partial(buf, 98, 0.1, t0=0.02, tau=0.22, phase=r.random() * math.tau)
    return normalize(reverb(buf, mix=0.18), peak=0.86)


def synth_material_item(spec, r, variant_idx=0):
    dur = 0.5 + 0.06 * variant_idx
    buf = zeros(dur)
    source_kind = spec.get("source_kind", "")
    if source_kind == "ingot":
        harmonic_cluster(buf, [460 + 40 * variant_idx, 690 + 48 * variant_idx, 920 + 60 * variant_idx], 0.05, 0.0, 0.14, r, jitter=0.012)
        add_partial(buf, 122 + 8 * variant_idx, 0.08, t0=0.02, tau=0.18, phase=r.random() * math.tau)
    elif source_kind == "shard":
        harmonic_cluster(buf, [1046 + 70 * variant_idx, 1396 + 85 * variant_idx, 1760 + 100 * variant_idx], 0.05, 0.0, 0.16, r, jitter=0.006)
    else:
        add_noise(buf, r, amp=0.16, t0=0.0, dur=0.05 + 0.02 * variant_idx, tau=0.03, lp=0.38)
        add_clicks(buf, r, 3 + variant_idx, 0.07, 0.03, 0.08 + 0.03 * variant_idx, tau=0.01)
    return normalize(reverb(buf, mix=0.1), peak=0.8)


def classify_entity(entity_id):
    category = "hostile"
    desc = f"{entity_id.replace('_', ' ')} signature cue"
    tags = {"entity"}
    voice = "human"
    role = "folk"
    pitch_profile = "neutral"
    if any(term in entity_id for term in ("villager", "guild", "barkeep", "trader", "guard", "maze", "theresa", "oracle", "lady_grey", "briar_rose", "guildmaster", "mercenary")):
        category = "neutral"
        tags |= {"human", "folk"}
    if any(term in entity_id for term in ("balverine", "wasp", "beetle", "nymph", "arachanox")):
        tags |= {"beast"}
    if any(term in entity_id for term in ("wasp", "beetle", "arachanox")):
        tags |= {"insect"}
    if "balverine" in entity_id:
        tags |= {"howl", "claw", "feral"}
        desc = "Balverine throat-growl, bark, and pack-lunge warning"
        voice = "balverine"
    if "white_balverine" in entity_id or "frost_balverine" in entity_id:
        tags |= {"boss"}
    if "hobbe" in entity_id:
        tags |= {"goblin", "scrap"}
        desc = "Hobbe cackle and junk-weapon scamper"
        voice = "hobbe"
    if entity_id in {"banshee", "wraith"}:
        tags |= {"ghost", "shriek", "void"}
        desc = "Wailing spectral voice and grave shriek"
        voice = "ghost"
    if entity_id == "wraith":
        tags |= {"cry"}
        desc = "Wraith crying scream and sorrowful moan"
    if entity_id.startswith("undead"):
        tags |= {"undead", "rattle", "grave"}
        desc = "Undead bone-rattle and grave wind"
        voice = "undead"
    if any(term in entity_id for term in ("troll", "giant")):
        tags |= {"stone", "thud", "giant"}
        desc = "Heavy giant footfall and stone breath"
        voice = "troll"
    if entity_id in {"jack_of_blades", "jack_dragon"}:
        tags |= {"void", "boss", "fire", "mask"}
        desc = "Jack of Blades void resonance and fire omen"
        voice = "void_boss"
    if entity_id == "demon_door":
        tags |= {"stone", "voice", "door"}
        desc = "Demon Door bass resonance and ancient speech"
        voice = "demon_door"
    if entity_id == "twinblade":
        tags |= {"human", "boss", "metal", "bandit"}
        desc = "Twinblade duel cue with iron slam"
        voice = "human"
        role = "bandit"
        pitch_profile = "low"
    if any(term in entity_id for term in ("bandit", "assassin")):
        tags |= {"bandit", "leather", "blade"}
        role = "bandit"
        pitch_profile = "low"
    if any(term in entity_id for term in ("summoner", "summoned", "minion")):
        tags |= {"magic", "void"}
        if voice == "human":
            role = "seer"
    if any(term in entity_id for term in ("guild", "theresa", "maze", "oracle", "briar_rose")):
        tags |= {"magic", "heroic"}
        if entity_id == "theresa":
            role = "seer"
        elif entity_id in {"oracle", "briar_rose", "maze", "guildmaster", "guild_apprentice_might", "guild_apprentice_skill", "guild_apprentice_will"}:
            role = "hero"
    if any(term in entity_id for term in ("guard_",)):
        role = "guard"
        pitch_profile = "low"
    if entity_id == "lady_grey":
        role = "noble"
    if entity_id in {"guildmaster", "maze", "mercenary", "barkeep", "trader", "summoner"}:
        pitch_profile = "low"
    if entity_id in {"lady_grey", "briar_rose", "theresa", "villager_woman", "nymph"}:
        pitch_profile = "high"
    if any(term in entity_id for term in ("wasp", "beetle", "arachanox")):
        voice = "insect"
    variants = 1
    if voice in {"human", "demon_door"}:
        variants = 3
    elif voice in {"balverine", "hobbe", "ghost", "undead", "troll", "insect", "void_boss"}:
        variants = 3 if voice in {"ghost", "undead", "insect"} else 2
    return {
        "key": f"entity/{entity_id}",
        "definition": f"fc.entity.{entity_id}",
        "category": category,
        "desc": desc,
        "tags": tags,
        "group": "Entities",
        "voice": voice,
        "role": role,
        "pitch_profile": pitch_profile,
        "variants": variants,
    }


def classify_item(item):
    item_id = item["id"]
    desc = f"{item['name']} handling cue"
    tags = {"item"}
    kind = item.get("kind", "")
    voice = "material_item"
    if item["cat"] in {"melee", "ranged"}:
        tags |= {"metal", "weapon"}
    if item["cat"] == "spell":
        tags |= {"magic", "will", "paper"}
        desc = f"{item['name']} will-tome whisper"
        voice = "paper_item"
    if item["cat"] == "augment":
        tags |= {"magic", "gem", "chime"}
        desc = f"{item['name']} socketing chime"
        voice = "trinket_item"
    if item["cat"] == "consumable":
        tags |= {"drink" if "potion" in item_id or "phial" in kind else "food"}
    if item["cat"] == "armor":
        tags |= {"cloth"}
    if kind in {"sword", "katana", "cleaver", "axe", "mace", "pickhammer", "greataxe", "greatsword", "greathammer", "aeons", "avos_tear", "greatsword_legend", "katana_legend", "mace_legend", "pickhammer_legend", "scimitar"}:
        tags |= {"blade", "metal"}
        desc = f"{item['name']} steel flourish"
        voice = "blade_item"
    if kind in {"bow", "crossbow", "bow_legend", "crossbow_legend"}:
        tags |= {"bow", "wood", "string"}
        desc = f"{item['name']} uses vanilla bow shot"
        voice = "vanilla_bow"
    if kind in {"flask", "flask_large", "phial"}:
        tags |= {"glass", "drink", "magic"}
        desc = f"{item['name']} potion glug"
        voice = "potion_item"
    if kind in {"food", "pie"}:
        tags |= {"food", "warm"}
        desc = f"{item['name']} rustic meal cue"
        voice = "food_item"
    if kind == "tankard":
        tags |= {"drink", "wood"}
        desc = f"{item['name']} tavern swig"
        voice = "potion_item"
    if kind in {"coin", "key", "key_ornate", "ring", "seal", "card", "mask", "trophy", "book"}:
        tags |= {"trinket"}
    if kind in {"coin", "ring"}:
        tags |= {"jingle", "metal"}
    if kind in {"key", "key_ornate", "seal"}:
        tags |= {"key", "metal"}
    if kind in {"card", "book", "tome"}:
        tags |= {"paper"}
        voice = "paper_item"
    if kind in {"mask", "trophy"}:
        tags |= {"ritual"}
        voice = "trinket_item"
    if kind == "ingot":
        tags |= {"metal"}
    if kind == "shard":
        tags |= {"crystal", "magic"}
    if kind in {"hide", "straps", "fang", "wing", "stinger", "chitin", "heart", "bones", "goo", "tear", "core"}:
        tags |= {"monster"}
    if item_id in {"will_shard", "ages_of_might_potion", "ages_of_skill_potion", "ages_of_will_potion", "guild_seal", "jack_of_blades_mask", "septimal_key"}:
        tags |= {"magic"}
    if item_id == "jack_of_blades_mask":
        tags |= {"void", "mask"}
        desc = "Mask of Jack of Blades ominous hum"
    if item_id == "guild_seal":
        tags |= {"heroic", "guild"}
        desc = "Guild Seal arrival pulse"
    variants = 1
    if voice in {"blade_item", "potion_item", "food_item", "paper_item", "trinket_item", "material_item"}:
        variants = 2
    return {
        "key": f"item/{item_id}",
        "definition": f"fc.item.{item_id}",
        "category": "player",
        "desc": desc,
        "tags": tags,
        "group": "Items",
        "voice": voice,
        "source_id": item_id,
        "source_kind": kind,
        "sound_name": "random.bow" if voice == "vanilla_bow" else None,
        "variants": variants,
    }


def system_specs():
    return [
        {
            "key": "system/door_rumble",
            "definition": "fc.magic.demon_door_open",
            "category": "hostile",
            "desc": "Demon Door opening stone grind",
            "tags": {"stone", "door", "thud", "voice"},
            "group": "Systems",
        },
        {
            "key": "system/door_speak",
            "definition": "fc.magic.demon_door_voice",
            "category": "hostile",
            "desc": "Demon Door taunting bass speech",
            "tags": {"voice", "stone", "void"},
            "group": "Systems",
            "voice": "demon_door",
            "variants": 3,
        },
        {
            "key": "system/banshee_shriek",
            "definition": "fc.magic.banshee_shriek",
            "category": "hostile",
            "desc": "Banshee despair shriek",
            "tags": {"ghost", "shriek", "void"},
            "group": "Systems",
            "voice": "ghost",
            "variants": 3,
        },
        {
            "key": "system/spell_cast",
            "definition": "fc.magic.will_cast",
            "category": "player",
            "desc": "General Will cast bloom",
            "tags": {"magic", "will", "heroic"},
            "group": "Systems",
            "voice": "trinket_item",
            "variants": 2,
        },
        {
            "key": "system/level_up",
            "definition": "fc.ui.level_up",
            "category": "player",
            "desc": "Hero level-up fanfare",
            "tags": {"heroic", "guild", "chime"},
            "group": "Systems",
            "voice": "trinket_item",
            "variants": 2,
        },
        {
            "key": "system/guild_pad",
            "definition": "fc.ambience.heroes_guild",
            "category": "ambient",
            "desc": "Heroes' Guild orchard-and-stone ambience",
            "tags": {"guild", "heroic", "ambient", "water", "npc_murmur"},
            "group": "Systems",
            "variants": 3,
        },
        {
            "key": "system/bowerstone_market",
            "definition": "fc.ambience.bowerstone_market",
            "category": "ambient",
            "desc": "Bowerstone market chatter and foot traffic",
            "tags": {"ambient", "market", "npc_murmur"},
            "group": "Systems",
            "variants": 3,
        },
        {
            "key": "system/bandit_camp_murmur",
            "definition": "fc.ambience.bandit_camp_murmur",
            "category": "ambient",
            "desc": "Bandit camp low voices, leather, and firelight",
            "tags": {"ambient", "camp", "bandit", "npc_murmur"},
            "group": "Systems",
            "variants": 3,
        },
        {
            "key": "system/graveyard_whispers",
            "definition": "fc.ambience.graveyard_whispers",
            "category": "ambient",
            "desc": "Graveyard wind with distant mournful murmurs",
            "tags": {"ambient", "grave", "npc_murmur"},
            "group": "Systems",
            "variants": 3,
        },
        {
            "key": "system/sword_clash",
            "definition": "fc.combat.sword_clash",
            "category": "player",
            "desc": "Steel-on-steel clash",
            "tags": {"metal", "blade", "weapon"},
            "group": "Systems",
            "voice": "blade_item",
            "variants": 2,
        },
    ]


def render_sound(spec):
    return render_sound_variant(spec, 0)


def render_sound_variant(spec, variant_idx=0):
    r = rng("sound", spec["key"])
    voice = spec.get("voice", "material_item")
    if "ambient" in spec["tags"]:
        return synth_ambient(spec, r)
    if voice == "demon_door":
        return synth_babbling_demon_door(spec, r, variant_idx=variant_idx)
    if voice == "balverine":
        return synth_balverine(spec, r, variant_idx=variant_idx)
    if voice == "hobbe":
        return synth_hobbe(spec, r, variant_idx=variant_idx)
    if voice == "ghost":
        return synth_ghost(spec, r, variant_idx=variant_idx)
    if voice == "undead":
        return synth_undead(spec, r, variant_idx=variant_idx)
    if voice == "troll":
        return synth_troll(spec, r, variant_idx=variant_idx)
    if voice == "insect":
        return synth_insect(spec, r, variant_idx=variant_idx)
    if voice == "void_boss":
        return synth_void_boss(spec, r, variant_idx=variant_idx)
    if voice == "human":
        return synth_babbling_human(spec, r, variant_idx=variant_idx)
    if voice == "blade_item":
        return synth_blade_item(spec, r, variant_idx=variant_idx)
    if voice == "bow_item":
        return synth_bow_item(spec, r)
    if voice == "potion_item":
        return synth_potion_item(spec, r, variant_idx=variant_idx)
    if voice == "food_item":
        return synth_food_item(spec, r, variant_idx=variant_idx)
    if voice == "paper_item":
        return synth_paper_item(spec, r, variant_idx=variant_idx)
    if voice == "trinket_item":
        return synth_trinket_item(spec, r, variant_idx=variant_idx)
    return synth_material_item(spec, r, variant_idx=variant_idx)


def variant_records(spec):
    count = spec.get("variants", 1)
    records = []
    for idx in range(count):
        if count == 1:
            records.append({"key": spec["key"], "sound_name": spec.get("sound_name") or f"sounds/fc/{spec['key']}", "variant_idx": 0})
        else:
            key = f"{spec['key']}_{idx + 1}"
            records.append({"key": key, "sound_name": spec.get("sound_name") or f"sounds/fc/{key}", "variant_idx": idx})
    return records


def build_specs():
    specs = system_specs()
    entity_ids = sorted(path.stem for path in (ROOT / "packs" / "Fablecraft_BP" / "entities").glob("*.json"))
    specs.extend(classify_entity(entity_id) for entity_id in entity_ids)
    specs.extend(classify_item(item) for item in all_items())
    return specs


def legacy_aliases():
    return {
        "fc.door_rumble": ("system/door_rumble", "hostile"),
        "fc.door_speak": ("system/door_speak", "hostile"),
        "fc.banshee_shriek": ("system/banshee_shriek", "hostile"),
        "fc.spell_cast": ("system/spell_cast", "player"),
        "fc.level_up": ("system/level_up", "player"),
        "fc.guild_pad": ("system/guild_pad", "ambient"),
        "fc.sword_clash": ("system/sword_clash", "player"),
    }


def write_preview(specs):
    if PREVIEW.exists():
        for wav_path in PREVIEW.rglob("*.wav"):
            wav_path.unlink()
    else:
        PREVIEW.mkdir(parents=True, exist_ok=True)
    rows = []
    for spec in sorted(specs, key=lambda rec: (rec["group"], rec["definition"])):
        preview_parts = []
        for record in variant_records(spec):
            if not record["sound_name"].startswith("sounds/fc/"):
                preview_parts = [f"<span>{html.escape(record['sound_name'])}</span>"]
                break
            src = OUT / f"{record['key']}.wav"
            dst = PREVIEW / f"{record['key']}.wav"
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(src, dst)
            label = ""
            if spec.get("variants", 1) > 1:
                kind = "phrase" if spec.get("voice") in {"human", "demon_door"} else "variant"
                label = f"<span class=\"v\">{kind} {record['variant_idx'] + 1}</span>"
            preview_parts.append(f"<div class=\"pv\">{label}<audio controls preload=\"none\" src=\"{html.escape(record['key'])}.wav\"></audio></div>")
        preview_cell = "".join(preview_parts)
        rows.append(
            "<tr>"
            f"<td class=\"g\">{html.escape(spec['group'])}</td>"
            f"<td class=\"n\">{html.escape(spec['definition'])}</td>"
            f"<td>{html.escape(spec['desc'])}</td>"
            f"<td>{preview_cell}</td>"
            "</tr>"
        )
    html_text = f"""<!DOCTYPE html>
<html lang=\"en\"><head><meta charset=\"utf-8\">
<title>Fablecraft: Reforged - Sound Library</title>
<style>
  body {{ background:#1b140e; color:#e6d8b8; font-family:Georgia,serif; max-width:1200px; margin:2rem auto; padding:0 1rem; }}
  h1 {{ color:#f0c75e; border-bottom:2px solid #6b5530; padding-bottom:.4rem; }}
  p {{ color:#ad9b78; }}
  table {{ width:100%; border-collapse:collapse; font-size:14px; }}
  td {{ padding:.5rem .6rem; border-bottom:1px solid #3a2f1f; vertical-align:middle; }}
  td.g {{ color:#d3b26d; white-space:nowrap; }}
  td.n {{ color:#f0c75e; font-weight:bold; white-space:nowrap; }}
  audio {{ width:240px; }}
    .pv {{ display:flex; align-items:center; gap:.4rem; margin:.15rem 0; }}
    .v {{ color:#ad9b78; font-size:12px; min-width:3.8rem; }}
</style></head><body>
<h1>Fablecraft: Reforged - Sound Library</h1>
<p>Generated from addon data with deterministic synthesis. This preview mirrors the resource pack under <code>sounds/fc/</code>.</p>
<table>{''.join(rows)}</table>
</body></html>
"""
    (PREVIEW / "index.html").write_text(html_text, encoding="utf-8")
    print(f"sound preview -> {PREVIEW} ({len(specs)} wavs + index.html)")


def main():
    specs = build_specs()
    spec_by_key = {spec["key"]: spec for spec in specs}
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True, exist_ok=True)

    definitions = {}
    for spec in specs:
        sound_entries = []
        for record in variant_records(spec):
            sound_name = record["sound_name"]
            if sound_name.startswith("sounds/fc/"):
                wav_path = OUT / f"{record['key']}.wav"
                write_wav(wav_path, render_sound_variant(spec, record["variant_idx"]))
                print(f"  {record['key']}.wav")
            else:
                print(f"  {spec['key']} -> {sound_name}")
            sound_entries.append({"name": sound_name, "volume": 0.9})
        definitions[spec["definition"]] = {
            "category": spec["category"],
            "sounds": sound_entries,
        }

    for alias, (target, category) in legacy_aliases().items():
        target_spec = spec_by_key.get(target)
        alias_sounds = [{"name": f"sounds/fc/{target}", "volume": 0.9}]
        if target_spec is not None:
            alias_sounds = [
                {"name": record["sound_name"], "volume": 0.9}
                for record in variant_records(target_spec)
            ]
        definitions[alias] = {
            "category": category,
            "sounds": alias_sounds,
        }

    write_json(
        RP / "sounds" / "sound_definitions.json",
        {"format_version": "1.14.0", "sound_definitions": definitions},
    )
    print("sound_definitions.json written")
    write_preview(specs)


if __name__ == "__main__":
    main()

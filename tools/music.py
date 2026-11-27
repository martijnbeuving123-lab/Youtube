"""Make a low, sombre ambient music bed (no samples, no licence needed).

    python3 tools/music.py videos/<slug> --minutes 22 [--key D] [--seed 1]

Slow minor-chord pads with a soft drone and filtered noise, so it sits under narration.
Writes assets/audio/music.wav and sets "music" in audio.json. render.py sets the level
(edit.json "music_db", about -23).
"""
import argparse
import json
import os

import numpy as np
import soundfile as sf

SR = 44100
NOTES = {"C": 0, "C#": 1, "D": 2, "D#": 3, "E": 4, "F": 5, "F#": 6, "G": 7, "G#": 8, "A": 9, "A#": 10, "B": 11}
# i - VI - III - VII in a minor key, as semitone offsets from the tonic
PROG = [(0, 3, 7), (-4, 0, 3), (3, 7, 10), (-2, 2, 5)]


def hz(semi):  # semitones above A2 (110 Hz)
    return 110.0 * 2 ** (semi / 12)


def pad(freqs, n, rng):
    t = np.arange(n) / SR
    out = np.zeros(n)
    for f in freqs:
        for det in (-0.12, 0.0, 0.11):
            ph = rng.uniform(0, 2 * np.pi)
            lfo = 1 + 0.002 * np.sin(2 * np.pi * 0.07 * t + ph)
            out += np.sin(2 * np.pi * (f + det) * t * lfo + ph) * 0.6
            out += np.sin(2 * np.pi * 2 * (f + det) * t + ph) * 0.12
    env = np.minimum(1, np.minimum(t / 4.0, (t[-1] - t) / 4.0))  # 4 s fade in/out
    return out * env / (len(freqs) * 3)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("vdir")
    ap.add_argument("--minutes", type=float, default=22)
    ap.add_argument("--key", default="D")
    ap.add_argument("--seed", type=int, default=1)
    a = ap.parse_args()
    rng = np.random.default_rng(a.seed)
    tonic = NOTES[a.key] - 9  # relative to A

    chord_len = 16.0  # seconds per chord, chords overlap by 4 s
    total = int(a.minutes * 60 * SR)
    out = np.zeros(total + int(chord_len * SR))
    step, i, pos = int((chord_len - 4) * SR), 0, 0
    while pos < total:
        ch = PROG[i % len(PROG)]
        freqs = [hz(tonic + s) for s in ch] + [hz(tonic + ch[0] - 12)]
        seg = pad(freqs, int(chord_len * SR), rng)
        out[pos:pos + len(seg)] += seg
        pos += step
        i += 1
    out = out[:total]
    t = np.arange(total) / SR
    out += 0.25 * np.sin(2 * np.pi * hz(tonic - 24) * t)  # low drone
    noise = rng.standard_normal(total)
    k = int(SR * 0.004)
    noise = np.convolve(noise, np.ones(k) / k, mode="same") * 0.05  # soft dark noise
    out += noise
    fade = int(6 * SR)
    out[:fade] *= np.linspace(0, 1, fade)
    out[-fade:] *= np.linspace(1, 0, fade)
    out = out / np.max(np.abs(out)) * 0.7
    stereo = np.stack([out, np.roll(out, int(0.011 * SR))], axis=1)

    os.makedirs(f"{a.vdir}/assets/audio", exist_ok=True)
    sf.write(f"{a.vdir}/assets/audio/music.wav", stereo.astype(np.float32), SR)
    path = f"{a.vdir}/audio.json"
    meta = json.load(open(path)) if os.path.exists(path) else {}
    meta["music"] = {"file": "music.wav", "source": f"tools/music.py key {a.key} seed {a.seed} (generated)"}
    json.dump(meta, open(path, "w"), indent=1)
    print(f"music.wav: {a.minutes} min")


if __name__ == "__main__":
    main()

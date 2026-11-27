"""Generate the narration for a video with Kokoro (free, open-source TTS, runs locally).

    python3 tools/voiceover.py videos/<slug> [--voice bm_george] [--speed 0.95]

Reads beats.json ([{"id": "01", "text": "..."}]), speaks every beat, and writes
assets/audio/vo.wav plus audio.json in the format tools/render.py expects:
{"voice": ..., "parts": [{"file", "beats", "starts", "end"}], "music": {...}}.
An existing "music" entry in audio.json is kept.

Needs: pip install kokoro soundfile (in a venv) and espeak-ng. The model is downloaded from
huggingface.co on first use.
"""
import argparse
import json
import os
import sys

import numpy as np
import soundfile as sf

SR = 24000
GAP = 0.35  # seconds of silence after each beat


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("vdir")
    ap.add_argument("--voice", default="bm_george")
    ap.add_argument("--speed", type=float, default=0.95)
    ap.add_argument("--only", help="comma-separated beat ids (test run)")
    a = ap.parse_args()

    from kokoro import KPipeline

    lang = "b" if a.voice.startswith("b") else "a"  # b = British English, a = American
    pipe = KPipeline(lang_code=lang, repo_id="hexgrad/Kokoro-82M")

    beats = json.load(open(f"{a.vdir}/beats.json"))
    if a.only:
        keep = set(a.only.split(","))
        beats = [b for b in beats if b["id"] in keep]

    chunks, starts, t = [], [], 0.0
    for b in beats:
        text = b["text"].strip()
        pieces = [audio for _, _, audio in pipe(text, voice=a.voice, speed=a.speed, split_pattern=r"\n+")]
        if not pieces:
            sys.exit(f"beat {b['id']}: no audio produced")
        wav = np.concatenate([np.asarray(p, dtype=np.float32) for p in pieces])
        wav = np.concatenate([wav, np.zeros(int(GAP * SR), dtype=np.float32)])
        starts.append(round(t, 6))
        chunks.append(wav)
        t += len(wav) / SR
        print(f"beat {b['id']}: {len(wav) / SR:.1f}s", flush=True)

    os.makedirs(f"{a.vdir}/assets/audio", exist_ok=True)
    full = np.concatenate(chunks)
    full = full / max(1e-6, float(np.max(np.abs(full)))) * 0.89  # peak -1 dBFS
    sf.write(f"{a.vdir}/assets/audio/vo.wav", full, SR)

    path = f"{a.vdir}/audio.json"
    old = json.load(open(path)) if os.path.exists(path) else {}
    out = {
        "voice": f"Kokoro {a.voice} (speed {a.speed})",
        "parts": [{"file": "vo.wav", "beats": f"{beats[0]['id']}-{beats[-1]['id']}",
                   "starts": starts, "end": round(t, 6)}],
    }
    if "music" in old:
        out["music"] = old["music"]
    json.dump(out, open(path, "w"), indent=1)
    print(f"done: {t / 60:.1f} min, {len(beats)} beats -> assets/audio/vo.wav")


if __name__ == "__main__":
    main()

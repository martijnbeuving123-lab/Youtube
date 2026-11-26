#!/usr/bin/env python3
"""Render a Precinct Archive video from edit.json + audio.json.

    python3 tools/render.py videos/<slug> [--preview N]   # N = only first N beats

edit.json: {"beats": [{"id": "01", "visual": "assets/img/x.jpg" | "assets/cards/x.png",
             "motion": "in|out|left|right|still", "caption": "optional text",
             "pause_before": 1.8, "grade": true}], "music_db": -24}
audio.json: voiceover parts with per-line start times (from vidIQ), plus music.
Output: <video_dir>/out/<slug>.mp4, narration.wav, timeline.json, captions.srt
"""
import json, os, re, subprocess, sys
from concurrent.futures import ThreadPoolExecutor
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps

W, H, FPS = 1920, 1080, 25
X = 0.7          # cross-dissolve length
GAP = 0.45       # pause after every beat
LEAD = 1.0       # silence before the first word
TAIL = 4.0       # hold after the last word
SR = 48000
CAP_FONT = "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"


def sh(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:
        sys.exit(f"FAILED: {' '.join(cmd)}\n{r.stderr[-2000:]}")
    return r.stdout


def prep_image(src, dst, grade):
    """Fit any image onto a 1.25x canvas with a blurred fill, then grade it."""
    cw, ch = int(W * 1.25), int(H * 1.25)
    im = ImageOps.exif_transpose(Image.open(src)).convert("RGB")
    if grade:
        g = ImageOps.grayscale(im)
        g = ImageOps.autocontrast(g, cutoff=1)
        im = ImageOps.colorize(g, black=(18, 14, 10), white=(238, 226, 200), mid=(128, 112, 90))
    bg = im.resize((cw, ch)).filter(ImageFilter.GaussianBlur(40))
    bg = Image.blend(bg, Image.new("RGB", (cw, ch), (0, 0, 0)), 0.55)
    s = min(cw / im.width, ch / im.height)
    fg = im.resize((max(1, int(im.width * s)), max(1, int(im.height * s))), Image.LANCZOS)
    bg.paste(fg, ((cw - fg.width) // 2, (ch - fg.height) // 2))
    bg.save(dst, quality=95)


def caption_png(text, dst):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    f = ImageFont.truetype(CAP_FONT, 44)
    tw = d.textlength(text, font=f)
    x, y = 110, H - 170
    d.rectangle((x - 30, y - 22, x + tw + 30, y + 66), fill=(10, 9, 8, 185))
    d.line((x - 30, y - 22, x - 30, y + 66), fill=(176, 58, 46, 255), width=6)
    d.text((x, y), text, font=f, fill=(236, 228, 212, 255))
    img.save(dst)


def motion_filter(m, dur):
    """Smooth pan/zoom on the 1.25x canvas, output 1920x1080."""
    n = max(1, int(dur * FPS))
    p = f"(on/{n})"
    ease = f"(0.5-0.5*cos(PI*{p}))"
    if m == "in":
        z, x, y = f"1+0.12*{ease}", "iw/2-(iw/zoom/2)", "ih/2-(ih/zoom/2)"
    elif m == "out":
        z, x, y = f"1.12-0.12*{ease}", "iw/2-(iw/zoom/2)", "ih/2-(ih/zoom/2)"
    elif m == "left":
        z, x, y = "1.06", f"(iw-iw/zoom)*(1-{ease})", "ih/2-(ih/zoom/2)"
    elif m == "right":
        z, x, y = "1.06", f"(iw-iw/zoom)*{ease}", "ih/2-(ih/zoom/2)"
    else:
        z, x, y = "1.0", "iw/2-(iw/zoom/2)", "ih/2-(ih/zoom/2)"
    # upscale first so zoompan's integer crop steps are invisible
    return (f"scale={W*2}:{H*2}:flags=lanczos,"
            f"zoompan=z='{z}':x='{x}':y='{y}':d={n}:s={W}x{H}:fps={FPS},"
            f"noise=alls=6:allf=t,format=yuv420p")


def main():
    vdir = sys.argv[1].rstrip("/")
    slug = os.path.basename(vdir)
    preview = int(sys.argv[sys.argv.index("--preview") + 1]) if "--preview" in sys.argv else None
    edit = json.load(open(f"{vdir}/edit.json"))
    audio = json.load(open(f"{vdir}/audio.json"))
    beats_txt = {b["id"]: b["text"] for b in json.load(open(f"{vdir}/beats.json"))}
    work = f"{vdir}/assets/build"
    os.makedirs(work, exist_ok=True)
    os.makedirs(f"{vdir}/out", exist_ok=True)

    # 1. narration segments per beat, from the vidIQ line timings
    segs = []
    for part in audio["parts"]:
        st = part["starts"] + [part["end"]]
        for i in range(len(part["starts"])):
            segs.append((f"{vdir}/assets/audio/{part['file']}", st[i], st[i + 1]))
    beats = edit["beats"][:preview] if preview else edit["beats"]
    assert len(segs) >= len(beats), "more beats than voiceover lines"

    timeline, t = [], LEAD
    concat = [f"{work}/silence_lead.wav"]
    sh(["ffmpeg", "-y", "-f", "lavfi", "-i", f"anullsrc=r={SR}:cl=mono", "-t", str(LEAD), concat[0]])
    for i, b in enumerate(beats):
        src, a, z = segs[i]
        pre = float(b.get("pause_before", 0))
        if pre:
            p = f"{work}/pause_{b['id']}.wav"
            sh(["ffmpeg", "-y", "-f", "lavfi", "-i", f"anullsrc=r={SR}:cl=mono", "-t", str(pre), p])
            concat.append(p); t += pre
        seg = f"{work}/vo_{b['id']}.wav"
        gap = GAP if i < len(beats) - 1 else TAIL
        sh(["ffmpeg", "-y", "-ss", f"{a:.3f}", "-to", f"{z:.3f}", "-i", src, "-ac", "1", "-ar", str(SR),
            "-af", f"apad=pad_dur={gap}", seg])
        dur = float(sh(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", seg]))
        concat.append(seg)
        timeline.append({"id": b["id"], "start": round(t, 3), "speech": round(z - a, 3), "dur": round(dur, 3)})
        t += dur
    # pauses belong to the visual of the beat before them
    for i in range(len(timeline) - 1):
        timeline[i]["vis"] = timeline[i + 1]["start"] - timeline[i]["start"]
    timeline[-1]["vis"] = timeline[-1]["dur"]
    timeline[0]["vis"] += LEAD
    timeline[0]["vstart"] = 0.0
    with open(f"{work}/concat.txt", "w") as f:
        f.writelines(f"file '{os.path.abspath(p)}'\n" for p in concat)
    narration = f"{vdir}/out/narration.wav"
    sh(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", f"{work}/concat.txt", "-c", "pcm_s16le", narration])
    total = t
    json.dump(timeline, open(f"{vdir}/out/timeline.json", "w"), indent=1)

    # 2. one clip per beat
    def clip(i):
        b, tl = beats[i], timeline[i]
        dur = tl["vis"] + (X if i < len(beats) - 1 else 0)
        img = f"{work}/img_{b['id']}.jpg"
        prep_image(f"{vdir}/{b['visual']}", img, b.get("grade", not b["visual"].startswith("assets/cards")))
        out = f"{work}/clip_{b['id']}.mp4"
        vf = motion_filter(b.get("motion", "in"), dur)
        cmd = ["ffmpeg", "-y", "-loop", "1", "-framerate", str(FPS), "-t", f"{dur:.3f}", "-i", img]
        if b.get("caption"):
            cap = f"{work}/cap_{b['id']}.png"
            caption_png(b["caption"], cap)
            cmd += ["-loop", "1", "-framerate", str(FPS), "-t", f"{dur:.3f}", "-i", cap]
            fc = (f"[0:v]{vf}[bg];[1:v]format=rgba,fade=t=in:st=0.6:d=0.6:alpha=1,"
                  f"fade=t=out:st={max(1.5, min(6.0, dur - 1.0)):.2f}:d=0.8:alpha=1[c];"
                  f"[bg][c]overlay=0:0,format=yuv420p[v]")
            cmd += ["-filter_complex", fc, "-map", "[v]"]
        else:
            cmd += ["-vf", vf]
        cmd += ["-t", f"{dur:.3f}", "-r", str(FPS), "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", out]
        sh(cmd)
        return out

    with ThreadPoolExecutor(max_workers=2) as ex:
        clips = list(ex.map(clip, range(len(beats))))

    # 3. cross-dissolve chain
    inputs, fc, last, off = [], [], "0:v", 0.0
    for c in clips:
        inputs += ["-i", c]
    for i in range(1, len(clips)):
        off += timeline[i - 1]["vis"]
        fc.append(f"[{last}][{i}:v]xfade=transition=fade:duration={X}:offset={off:.3f}[x{i}]")
        last = f"x{i}"
    video = f"{work}/video.mp4"
    if fc:
        fc[-1] = fc[-1].rsplit("[", 1)[0] + "[vout]"
        sh(["ffmpeg", "-y", *inputs, "-filter_complex", ";".join(fc), "-map", "[vout]",
            "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p", video])
    else:
        os.replace(clips[0], video)

    # 4. mix narration + looped music bed, fade in/out, normalise for YouTube
    music = f"{vdir}/assets/audio/{audio['music']['file']}"
    mdb = edit.get("music_db", -24)
    out = f"{vdir}/out/{slug}.mp4"
    af = (f"[1:a]aloop=loop=-1:size=2e9,atrim=0:{total:.3f},volume={mdb}dB,"
          f"afade=t=in:d=3,afade=t=out:st={total-4:.3f}:d=4[m];"
          f"[2:a]aformat=channel_layouts=stereo[n];"
          f"[n][m]amix=inputs=2:duration=first:normalize=0,loudnorm=I=-14:TP=-1.5:LRA=11[a]")
    sh(["ffmpeg", "-y", "-i", video, "-i", music, "-i", narration, "-filter_complex", af,
        "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
        "-ar", str(SR), "-movflags", "+faststart", "-shortest", out])

    # 5. captions (sentence-level, timed by character share within each beat)
    def ts(s):
        h, m = divmod(int(s), 3600); m, sec = divmod(m, 60)
        return f"{h:02}:{m:02}:{sec:02},{int((s-int(s))*1000):03}"
    n, lines = 1, []
    for tl in timeline:
        sents = re.split(r"(?<=[.?!\"])\s+(?=[A-Z\"])", beats_txt[tl["id"]])
        total_c = sum(len(s) for s in sents)
        cur = tl["start"]
        for s in sents:
            d = tl["speech"] * len(s) / total_c
            lines.append(f"{n}\n{ts(cur)} --> {ts(cur + d)}\n{s}\n"); n += 1; cur += d
    open(f"{vdir}/out/captions.srt", "w").write("\n".join(lines))
    print(f"done: {out}  ({total/60:.1f} min)")


if __name__ == "__main__":
    main()

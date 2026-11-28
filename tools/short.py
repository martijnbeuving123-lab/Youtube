#!/usr/bin/env python3
"""Make a vertical YouTube Short (1080x1920) from a finished long video, in the house style.

    python3 tools/short.py spec.json out.mp4

spec.json (times in seconds of the LONG video; image paths relative to the repo or absolute):
{
  "video": "videos/<slug>/out/<slug>.mp4",       # the rendered long video (audio is cut from it)
  "captions": "deliveries/<slug>/captions.srt",   # its SRT, for the on-screen captions
  "start": 0.9, "end": 54.9,                      # 30-55 s that stand on their own
  "hook": ["HE DISGUISED HIS", "LOVER AS A BOY."],        # cream, on screen from 0 s
  "hook_red": ["A TELEGRAM", "STILL CAUGHT HIM."],        # red, from 1.2 s; hook gone at 3 s
  "end_card": ["UNDER THE", "CELLAR", "FLOOR..."],        # first line cream, rest red
  "end_label": "FULL CASE ON THE CHANNEL",
  "end_at": 47.7,                                  # Short time at which the end card starts
  "shots": [                                        # Short time; each fills the 9:16 frame
    {"t0": 0, "t1": 7.6, "src": "frame:2", "mode": "card", "box": [10, 14, 80, 72], "zoom": [1.0, 1.08]},
    {"t0": 14.6, "t1": 22.4, "src": "videos/<slug>/assets/img/x.jpg", "mode": "fill",
     "zoom": [1.0, 1.12], "center": [0.5, 0.35], "to": [0.5, 0.45], "sepia": true},
    {"t0": 40.8, "t1": 47.7, "src": "frame:25", "mode": "wide", "zoom": [1.35, 1.6], "pan": [0.85, 0.15]}
  ]
}
src: an archive image, or "frame:<seconds>" for a frame of the long video (maps, cards).
mode: "fill" (crop to 9:16, for portraits and photos), "card" (a document/card region `box`
in percent, shown large on a blurred backdrop), "wide" (a wide image such as a map, panned
across a blurred backdrop).

Rules (owner, 2026-11-27): the hook is the strongest line, in the first second, different words
from the narration; only real archive images (never an AI face); captions 2 words at a time; the
end card points to the full video. Check sampled frames before uploading.
"""
import json
import os
import re
import subprocess
import sys

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageOps

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W, H, FPS = 1080, 1920, 25
HEAD = os.path.join(REPO, "tools", "fonts", "PlayfairDisplay-Black.ttf")
MONO = "/usr/share/fonts/truetype/freefont/FreeMonoBold.ttf"
CREAM, RED, BG, PAPER, INK = (241, 232, 212), (200, 38, 28), (18, 16, 14), (232, 219, 186), (34, 29, 24)


def find_sans():
    for root, _, files in os.walk("/usr/share/fonts"):
        for f in files:
            if f.startswith("Inter") and "ExtraBold" in f and f.endswith((".ttf", ".otf")) and "Display" not in f:
                return os.path.join(root, f)
    return "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"


SANS = find_sans()


def path(p):
    return p if os.path.isabs(p) else os.path.join(REPO, p)


def sepia(im):
    g = ImageOps.autocontrast(ImageOps.grayscale(im), cutoff=1)
    return ImageOps.colorize(g, black=(12, 10, 8), white=(240, 228, 204), mid=(126, 108, 86))


def fill(im, zoom, cx=0.5, cy=0.5):
    iw, ih = im.size
    if iw / ih > W / H:
        ch = ih / zoom
        cw = ch * W / H
    else:
        cw = iw / zoom
        ch = cw * H / W
    x = min(max(cx * iw - cw / 2, 0), iw - cw)
    y = min(max(cy * ih - ch / 2, 0), ih - ch)
    return im.crop((int(x), int(y), int(x + cw), int(y + ch))).resize((W, H), Image.BILINEAR)


def backdrop(im):
    return ImageEnhance.Brightness(fill(im, 1.0).filter(ImageFilter.GaussianBlur(30))).enhance(0.35)


def load_src(src, video, start):
    if src.startswith("frame:"):
        t = float(src.split(":", 1)[1])
        out = "/tmp/_short_frame.png"
        subprocess.run(["ffmpeg", "-v", "error", "-ss", str(t), "-i", video, "-frames:v", "1", "-y", out], check=True)
        return Image.open(out).convert("RGB")
    return Image.open(path(src)).convert("RGB")


def lerp(a, b, p):
    return a + (b - a) * p


def make_shot(sh, video, start):
    im = load_src(sh["src"], video, start)
    if sh.get("sepia"):
        im = sepia(im)
    mode = sh.get("mode", "fill")
    z0, z1 = sh.get("zoom", [1.0, 1.08])
    if mode == "card":
        x, y, w, h = (v / 100 for v in sh.get("box", [0, 0, 100, 100]))
        card = im.crop((int(x * im.width), int(y * im.height), int((x + w) * im.width), int((y + h) * im.height)))
        bg = backdrop(card)
        fy = sh.get("focus_y", 0.5)

        def fn(p):
            img = bg.copy()
            cw = int(1000 * lerp(z0, z1, p))
            c = card.resize((cw, int(card.height * cw / card.width)), Image.BILINEAR)
            img.paste(c, ((W - cw) // 2, int(1000 - fy * c.height)))
            return img
        return fn
    if mode == "wide":
        bg = ImageEnhance.Brightness(fill(im, 1.0).filter(ImageFilter.GaussianBlur(25))).enhance(0.5)
        a, b = sh.get("pan", [0.85, 0.15])

        def fn(p):
            img = bg.copy()
            w = int(W * lerp(z0, z1, p))
            m = im.resize((w, int(im.height * w / im.width)), Image.BILINEAR)
            img.paste(m, (int((W - w) * lerp(a, b, p)), 960 - m.height // 2 - 120))
            return img
        return fn
    c0 = sh.get("center", [0.5, 0.4])
    c1 = sh.get("to", c0)
    return lambda p: fill(im, lerp(z0, z1, p), lerp(c0[0], c1[0], p), lerp(c0[1], c1[1], p))


def end_card(lines, label):
    def fn(p):
        img = Image.new("RGB", (W, H), BG)
        d = ImageDraw.Draw(img)
        f = ImageFont.truetype(HEAD, 118)
        y = 620
        for i, t in enumerate(lines):
            ff = f
            while d.textlength(t, font=ff) > W - 120:
                ff = ImageFont.truetype(HEAD, ff.size - 6)
            d.text(((W - d.textlength(t, font=ff)) / 2, y), t, font=ff, fill=CREAM if i == 0 else RED)
            y += 150
        d.rectangle((240, y + 30, 840, y + 40), fill=RED)
        if p > 0.45 and label:
            fl = ImageFont.truetype(MONO, 40)
            tw = d.textlength(label, font=fl)
            d.rectangle(((W - tw) / 2 - 24, y + 100, (W + tw) / 2 + 24, y + 170), fill=PAPER)
            d.text(((W - tw) / 2, y + 116), label, font=fl, fill=INK)
        return img
    return fn


def read_captions(srt_path, start, dur):
    caps = []
    for blk in open(path(srt_path)).read().strip().split("\n\n"):
        ls = blk.split("\n")
        if len(ls) < 3:
            continue
        m = re.match(r"(\d+):(\d+):(\d+)[,.](\d+) --> (\d+):(\d+):(\d+)[,.](\d+)", ls[1])
        if not m:
            continue
        t0 = int(m[1]) * 3600 + int(m[2]) * 60 + int(m[3]) + int(m[4]) / 1000 - start
        t1 = int(m[5]) * 3600 + int(m[6]) * 60 + int(m[7]) + int(m[8]) / 1000 - start
        if t1 < 0 or t0 > dur:
            continue
        words = " ".join(ls[2:]).split()
        chunks = [" ".join(words[i:i + 2]) for i in range(0, len(words), 2)]
        tot = sum(len(c) for c in chunks) or 1
        t = t0
        for c in chunks:
            dt = (t1 - t0) * len(c) / tot
            caps.append((t, t + dt, c.upper()))
            t += dt
    return caps


def main():
    spec = json.load(open(sys.argv[1]))
    out = sys.argv[2]
    video = path(spec["video"])
    start, end = float(spec["start"]), float(spec["end"])
    dur = end - start
    end_at = float(spec.get("end_at", dur - 6))
    shots = [(s["t0"], s["t1"], make_shot(s, video, start)) for s in spec["shots"]]
    shots.append((end_at, dur + 1, end_card(spec.get("end_card", []), spec.get("end_label", ""))))
    caps = read_captions(spec["captions"], start, dur)
    hook, hook_red = spec.get("hook", []), spec.get("hook_red", [])

    audio = "/tmp/_short_audio.wav"
    subprocess.run(["ffmpeg", "-v", "error", "-ss", str(start), "-t", str(dur), "-i", video, "-vn",
                    "-af", f"afade=t=in:d=0.3,afade=t=out:st={dur - 0.8}:d=0.8", "-ar", "48000", "-y", audio],
                   check=True)
    fcap = ImageFont.truetype(SANS, 84)
    fhook = ImageFont.truetype(HEAD, 88)
    ff = subprocess.Popen([
        "ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
        "-i", "-", "-i", audio, "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "160k", "-shortest", out], stdin=subprocess.PIPE)
    last = Image.new("RGB", (W, H), BG)
    for i in range(int(dur * FPS)):
        t = i / FPS
        img = None
        for a, b, fn in shots:
            if a <= t < b:
                img = fn((t - a) / max(b - a, 0.01))
                if t - a < 0.25:  # short punch-in on every cut
                    k = 1.04 - 0.16 * (t - a)
                    img = img.crop((int(W * (k - 1) / 2), int(H * (k - 1) / 2),
                                    int(W - W * (k - 1) / 2), int(H - H * (k - 1) / 2))).resize((W, H))
                break
        img = img or last.copy()
        last = img
        d = ImageDraw.Draw(img)
        if t < 3.0 and (hook or hook_red):
            lines = [(x, CREAM) for x in hook] + ([(x, RED) for x in hook_red] if t >= 1.2 else [])
            d.rectangle((0, 150, W, 200 + 112 * (len(hook) + len(hook_red))), fill=(10, 9, 8))
            for j, (txt, col) in enumerate(lines):
                fh = fhook
                while d.textlength(txt, font=fh) > W - 80:
                    fh = ImageFont.truetype(HEAD, fh.size - 4)
                d.text(((W - d.textlength(txt, font=fh)) / 2, 180 + j * 112), txt, font=fh, fill=col)
        if t < end_at:
            for a, b, c in caps:
                if a <= t < b:
                    f = fcap
                    while d.textlength(c, font=f) > W - 120 and f.size > 50:
                        f = ImageFont.truetype(SANS, f.size - 6)
                    d.text(((W - d.textlength(c, font=f)) / 2, 1440), c, font=f, fill=CREAM,
                           stroke_width=8, stroke_fill=(0, 0, 0))
                    break
        ff.stdin.write(img.tobytes())
    ff.stdin.close()
    ff.wait()
    sys.exit(ff.returncode)


if __name__ == "__main__":
    main()

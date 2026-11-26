#!/usr/bin/env python3
"""Generate 1920x1080 text cards for Precinct Archive videos.

    python3 tools/cards.py title  out.png "PRECINCT ARCHIVE" "Case file: Crippen, 1910"
    python3 tools/cards.py telegram out.png "message text" ["header line"]
    python3 tools/cards.py quote  out.png "quoted words" "attribution"
    python3 tools/cards.py text   out.png "big line" ["small line"]
"""
import random, sys, textwrap
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H = 1920, 1080
BG = (14, 13, 11)
INK = (232, 224, 208)
DIM = (150, 140, 122)
ACCENT = (176, 58, 46)
SERIF = "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"
SERIF_B = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"
SERIF_I = "/usr/share/fonts/truetype/freefont/FreeSerifItalic.ttf"
MONO = "/usr/share/fonts/truetype/freefont/FreeMono.ttf"
MONO_B = "/usr/share/fonts/truetype/freefont/FreeMonoBold.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def grain(img, amount=10, seed=7):
    rnd = random.Random(seed)
    noise = Image.effect_noise((W // 2, H // 2), 40).resize((W, H)).convert("L")
    noise = noise.point(lambda v: 128 + (v - 128) * amount // 40)
    out = Image.blend(img.convert("RGB"), Image.merge("RGB", (noise,) * 3), 0.06)
    return out


def vignette(img, strength=0.55):
    mask = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(mask)
    d.ellipse((-W * 0.25, -H * 0.35, W * 1.25, H * 1.35), fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(220))
    dark = Image.new("RGB", (W, H), (0, 0, 0))
    return Image.composite(img, Image.blend(img, dark, strength), mask)


def centered(d, y, text, f, fill):
    w = d.textlength(text, font=f)
    d.text(((W - w) / 2, y), text, font=f, fill=fill)


def title(out, big, small=""):
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    f1 = font(SERIF_B, 120)
    centered(d, 400, big, f1, INK)
    d.line((W / 2 - 260, 560, W / 2 + 260, 560), fill=ACCENT, width=3)
    if small:
        centered(d, 600, small, font(SERIF_I, 52), DIM)
    vignette(grain(img)).save(out)


def text(out, big, small=""):
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    lines = textwrap.wrap(big, 28)
    f1 = font(SERIF_B, 96)
    y = H / 2 - len(lines) * 60 - (40 if small else 0)
    for ln in lines:
        centered(d, y, ln, f1, INK); y += 120
    if small:
        centered(d, y + 30, small, font(SERIF_I, 50), DIM)
    vignette(grain(img)).save(out)


def quote(out, words, who=""):
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    f1 = font(SERIF_I, 74)
    lines = textwrap.wrap("“" + words + "”", 40)
    y = H / 2 - len(lines) * 50 - 40
    for ln in lines:
        centered(d, y, ln, f1, INK); y += 100
    if who:
        centered(d, y + 40, "— " + who, font(SERIF, 44), DIM)
    vignette(grain(img)).save(out)


def telegram(out, msg, header="WIRELESS MESSAGE"):
    img = Image.new("RGB", (W, H), BG)
    paper = Image.new("RGB", (1500, 720), (226, 214, 184))
    pd = ImageDraw.Draw(paper)
    for i in range(0, 720, 3):  # faint fibre lines
        c = 214 + (i * 37 % 11)
        pd.line((0, i, 1500, i), fill=(c, c - 12, c - 40))
    pd.rectangle((30, 30, 1470, 690), outline=(120, 90, 60), width=3)
    pd.text((70, 60), header, font=font(SERIF_B, 40), fill=(90, 50, 35))
    pd.text((70, 115), "S.S. MONTROSE  ·  JULY 1910", font=font(SERIF, 30), fill=(110, 80, 55))
    pd.line((70, 170, 1430, 170), fill=(120, 90, 60), width=2)
    y = 220
    for ln in textwrap.wrap(msg.upper(), 46):
        pd.text((80, y), ln, font=font(MONO_B, 46), fill=(40, 34, 30)); y += 70
    pd.text((70, 630), "Text as recorded  \u00b7  reconstruction", font=font(SERIF_I, 26), fill=(120, 95, 70))
    paper = paper.rotate(-1.2, resample=Image.BICUBIC, expand=True, fillcolor=BG)
    img.paste(paper, ((W - paper.width) // 2, (H - paper.height) // 2))
    vignette(grain(img), 0.45).save(out)


if __name__ == "__main__":
    kind, out, *args = sys.argv[1:]
    {"title": title, "text": text, "quote": quote, "telegram": telegram}[kind](out, *args)

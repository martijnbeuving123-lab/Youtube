#!/usr/bin/env python3
"""House-style thumbnail for both channels ("case file" style, owner's choice 2026-11-27).

    python3 tools/thumbnail.py out.jpg portrait.jpg "LINE ONE" "LINE TWO" \
        --label "CASE FILE · LONDON, 1910" [--crop x,y,w,h] \
        [--top scene.jpg] [--bottom object.jpg] [--top-crop x,y,w,h] [--bottom-crop x,y,w,h]

Layout (reference: The Defector Files, "8 Nazi Saboteurs Landed in America"):
- dark, grainy warm background with a vignette;
- a large black-and-white / sepia archive image on the right, its left edge fading out;
- headline on the left in two lines: line one cream, line two larger and red (Playfair Display
  Black), with a red rule under it;
- a cream "case file" label in typewriter capitals: what, where, when;
- optional faded archive scenes top-left (--top) and bottom-left (--bottom), e.g. a map, a
  street, a ship.

Rules: only real archive images (no AI images of real people); line one + line two together at
most about three words and they must not repeat the title. Crops are percentages of the source
image (x,y,w,h). Output 1280x720 JPEG, under 2 MB. The old style (--strip) is still accepted
and treated as --label.
"""
import os
import random
import sys

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageOps

W, H = 1280, 720
HERE = os.path.dirname(os.path.abspath(__file__))
HEAD = os.path.join(HERE, "fonts", "PlayfairDisplay-Black.ttf")
if not os.path.exists(HEAD):
    HEAD = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"
MONO = "/usr/share/fonts/truetype/freefont/FreeMonoBold.ttf"
CREAM = (241, 232, 212)
RED = (200, 38, 28)
PAPER = (232, 219, 186)
INK = (34, 29, 24)


def crop_pct(im, spec):
    if not spec:
        return im
    x, y, w, h = (float(v) / 100 for v in spec.split(","))
    return im.crop((int(x * im.width), int(y * im.height),
                    int((x + w) * im.width), int((y + h) * im.height)))


def sepia(im, contrast=1.3):
    g = ImageOps.autocontrast(ImageOps.grayscale(im), cutoff=1)
    g = ImageEnhance.Contrast(g).enhance(contrast)
    return ImageOps.colorize(g, black=(12, 10, 8), white=(240, 228, 204), mid=(126, 108, 86))


def fade_mask(size, left=0, right=0, top=0, bottom=0, strength=255):
    w, h = size
    m = Image.new("L", size, strength)
    px = m.load()
    for x in range(w):
        for y in range(h):
            a = 1.0
            if left and x < left:
                a *= (x / left) ** 1.8
            if right and x > w - right:
                a *= (w - x) / right
            if top and y < top:
                a *= y / top
            if bottom and y > h - bottom:
                a *= (h - y) / bottom
            px[x, y] = int(strength * a)
    return m


def ghost(img, path, box, spec, opacity):
    """Paste a faded archive scene into box=(x0, y0, x1, y1)."""
    x0, y0, x1, y1 = box
    s = sepia(crop_pct(Image.open(path), spec), 1.1)
    s = ImageOps.fit(s, (x1 - x0, y1 - y0), Image.LANCZOS)
    s = ImageEnhance.Brightness(s).enhance(0.85)
    m = fade_mask(s.size, right=int(s.width * 0.45), top=int(s.height * 0.25),
                  bottom=int(s.height * 0.35), strength=int(255 * opacity))
    img.paste(s, (x0, y0), m)


def fit_font(d, text, start, max_w):
    size = start
    f = ImageFont.truetype(HEAD, size)
    while d.textlength(text, font=f) > max_w and size > 40:
        size -= 4
        f = ImageFont.truetype(HEAD, size)
    return f, size


def main():
    args = sys.argv[1:]
    opts = {}
    for key in ("--label", "--strip", "--crop", "--top", "--bottom", "--top-crop", "--bottom-crop"):
        if key in args:
            i = args.index(key)
            opts[key] = args[i + 1]
            del args[i:i + 2]
    out, portrait, *lines = args
    lines = [ln.upper() for ln in lines][:2]
    label = opts.get("--label") or opts.get("--strip")

    # background: warm near-black with a soft light patch behind the headline
    img = Image.new("RGB", (W, H), (22, 19, 16))
    glow = Image.new("L", (W, H), 0)
    ImageDraw.Draw(glow).ellipse((-200, 60, 760, 680), fill=70)
    glow = glow.filter(ImageFilter.GaussianBlur(160))
    img = Image.composite(Image.new("RGB", (W, H), (70, 60, 48)), img, glow)

    if opts.get("--top"):
        ghost(img, opts["--top"], (0, 0, 760, 250), opts.get("--top-crop"), 0.45)
    if opts.get("--bottom"):
        ghost(img, opts["--bottom"], (0, 500, 700, 720), opts.get("--bottom-crop"), 0.7)

    # portrait right, fading into the background on its left
    p = sepia(crop_pct(Image.open(portrait), opts.get("--crop")))
    # fixed box on the right; the image fills it (cropped from the top, faces stay in view)
    pw = 700
    p = ImageOps.fit(p, (pw, H), Image.LANCZOS, centering=(0.5, 0.2))
    mask = fade_mask(p.size, left=int(pw * 0.5), bottom=int(H * 0.08))
    img.paste(p, (W - pw, 0), mask)

    d = ImageDraw.Draw(img)
    max_w = 700
    f1, s1 = fit_font(d, lines[0], 165, max_w) if lines else (None, 0)
    f2, s2 = fit_font(d, lines[1], 230, max_w) if len(lines) > 1 else (None, 0)
    block = s1 + (s2 + 6 if f2 else 0) + 40 + (70 if label else 0)
    y = max(70, (H - block) // 2 - 10)
    x = 64
    right_edge = x
    for f, text, colour in ((f1, lines[0] if lines else "", CREAM),
                            (f2, lines[1] if len(lines) > 1 else "", RED)):
        if not f:
            continue
        top = f.getbbox(text)[1]
        for dx, dy in ((5, 6), (3, 3)):
            d.text((x + dx, y - top + dy), text, font=f, fill=(0, 0, 0))
        d.text((x, y - top), text, font=f, fill=colour)
        bbox = f.getbbox(text)
        right_edge = max(right_edge, x + int(d.textlength(text, font=f)))
        y += bbox[3] - top + 14
    y += 10
    d.rectangle((x + 4, y, right_edge, y + 9), fill=RED)
    y += 30
    if label:
        fl = ImageFont.truetype(MONO, 36)
        tw = d.textlength(label, font=fl)
        while x + tw + 40 > 760 and fl.size > 22:
            fl = ImageFont.truetype(MONO, fl.size - 2)
            tw = d.textlength(label, font=fl)
        d.rectangle((x - 6, y, x + tw + 30, y + fl.size + 30), fill=PAPER)
        d.text((x + 12, y + 14), label, font=fl, fill=INK)

    # vignette and film grain
    vig = Image.new("L", (W, H), 0)
    ImageDraw.Draw(vig).rectangle((0, 0, W, H), outline=255, width=60)
    vig = vig.filter(ImageFilter.GaussianBlur(90))
    img = Image.composite(Image.new("RGB", (W, H), (0, 0, 0)), img, vig.point(lambda v: int(v * 0.8)))
    random.seed(7)
    noise = Image.effect_noise((W, H), 28).convert("RGB")
    img = Image.blend(img, ImageOps.autocontrast(noise), 0.06)
    img.save(out, quality=90)


if __name__ == "__main__":
    main()

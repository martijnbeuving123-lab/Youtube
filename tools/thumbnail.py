#!/usr/bin/env python3
"""Precinct Archive thumbnail: archive portrait right, short headline left, red rule.

    python3 tools/thumbnail.py out.jpg portrait.jpg "LINE ONE" "LINE TWO" [--strip "small text"]

1280x720, under 2 MB. Text is at most three words (feed-size rule).
"""
import sys
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageOps

W, H = 1280, 720
BOLD = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"
MONO = "/usr/share/fonts/truetype/freefont/FreeMonoBold.ttf"


def main():
    out, portrait, *lines = sys.argv[1:]
    strip = None
    if "--strip" in lines:
        i = lines.index("--strip"); strip = lines[i + 1]; lines = lines[:i]
    img = Image.new("RGB", (W, H), (14, 13, 11))
    p = ImageOps.grayscale(Image.open(portrait))
    p = ImageOps.autocontrast(p, cutoff=1)
    p = ImageEnhance.Contrast(p).enhance(1.25)
    p = ImageOps.colorize(p, black=(10, 8, 6), white=(245, 233, 208), mid=(130, 112, 88))
    s = H / p.height * 1.08
    p = p.resize((int(p.width * s), int(p.height * s)), Image.LANCZOS)
    x0 = W - p.width + int(p.width * 0.06)
    # soft left edge so the portrait melts into the dark panel
    mask = Image.new("L", p.size, 255)
    md = ImageDraw.Draw(mask)
    for i in range(260):
        md.line((i, 0, i, p.height), fill=int(255 * i / 260))
    img.paste(p, (x0, -int(p.height * 0.04)), mask)
    d = ImageDraw.Draw(img)
    y = 170
    for ln in lines:
        size = 118
        f = ImageFont.truetype(BOLD, size)
        while d.textlength(ln, font=f) > 640:
            size -= 4; f = ImageFont.truetype(BOLD, size)
        d.text((62, y + 4), ln, font=f, fill=(0, 0, 0))
        d.text((58, y), ln, font=f, fill=(242, 234, 218))
        y += size + 18
    d.rectangle((60, y + 10, 330, y + 22), fill=(192, 52, 40))
    if strip:
        f = ImageFont.truetype(MONO, 30)
        tw = d.textlength(strip, font=f)
        d.rectangle((52, y + 54, 76 + tw, y + 104), fill=(226, 214, 184))
        d.text((64, y + 62), strip, font=f, fill=(40, 34, 30))
    img.save(out, quality=92)


if __name__ == "__main__":
    main()

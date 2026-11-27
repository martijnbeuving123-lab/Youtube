#!/usr/bin/env python3
"""Schematic bath diagrams (labelled reconstruction). Proportions: 5 ft bath, 5 ft 7 in figure."""
import sys
from PIL import Image, ImageDraw, ImageFont
W, H = 1920, 1080
BG, INK, DIM, RED, WATER = (14, 13, 11), (232, 224, 208), (150, 140, 122), (176, 58, 46), (52, 70, 82)
SERIF = "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"
F = lambda s: ImageFont.truetype(SERIF, s)
d = sys.argv[1]
S = 220  # pixels per foot

def base(title, note):
    img = Image.new("RGB", (W, H), BG); g = ImageDraw.Draw(img)
    x0, x1, yb, yt = 400, 400 + 5 * S, 820, 520
    # bath: sloping head end on the left, upright foot end on the right
    tub = [(x0 - 160, yt), (x0, yb), (x1, yb), (x1 + 20, yt)]
    g.polygon([(x0 - 100, 600), (x0, yb), (x1, yb), (x1 + 15, 600)], fill=WATER)
    g.line(tub, fill=INK, width=6)
    g.line((x0, yb + 40, x1, yb + 40), fill=DIM, width=2)
    g.text(((x0 + x1) // 2 - 60, yb + 50), "about 5 ft", font=F(34), fill=DIM)
    g.text((80, 60), title, font=F(56), fill=INK)
    g.text((80, 140), note, font=F(32), fill=DIM)
    g.text((80, H - 80), "Schematic reconstruction, not to exact scale · not an archive image", font=F(26), fill=DIM)
    return img, g, x0, x1, yb

# 1: measurements
img, g, x0, x1, yb = base("Herne Bay: the bath and the woman", "Bessie Mundy, 5 ft 7 in  ·  bath about 5 ft long")
g.line((x0 - 150, 470, x0 - 150 + int(5.58 * S), 470), fill=RED, width=5)
g.text((x0 - 150, 410), "5 ft 7 in", font=F(40), fill=RED)
img.save(f"{d}/diag_measure.png")

# 2: rigid phase: body extends, head pushed up the slope, above water
img, g, x0, x1, yb = base("Spilsbury's reasoning: the first stage of a fit", "the body stiffens and stretches; in a short bath the head is pushed up the slope")
g.line((x0 - 120, 540, x1 - 20, 790), fill=INK, width=16)   # stylised body line
g.ellipse((x0 - 175, 490, x0 - 95, 570), outline=INK, width=8)  # head above water
g.text((x0 - 300, 420), "head above the water", font=F(34), fill=RED)
img.save(f"{d}/diag_rigid.png")

# 3: feet lifted, head slides under
img, g, x0, x1, yb = base("The position Dr French described", "head under the water, legs straight, feet raised at the narrow end")
g.line((x0 + 40, 790, x1 + 60, 470), fill=INK, width=16)
g.ellipse((x0 - 20, 750, x0 + 60, 830), outline=INK, width=8)
g.polygon([(x1 + 120, 430), (x1 + 80, 520), (x1 + 160, 520)], fill=RED)
g.text((x1 + 40, 360), "feet lifted", font=F(34), fill=RED)
g.text((x0 - 40, 850), "head slides under", font=F(34), fill=RED)
img.save(f"{d}/diag_lift.png")

# 4: empty bath in a room (opening)
img = Image.new("RGB", (W, H), BG); g = ImageDraw.Draw(img)
x0, x1, yb, yt = 500, 1400, 760, 520
g.polygon([(x0 - 80, 600), (x0, yb), (x1, yb), (x1 + 15, 600)], fill=WATER)
g.line([(x0 - 140, yt), (x0, yb), (x1, yb), (x1 + 20, yt)], fill=INK, width=6)
g.text((80, 60), "Kentish Town police station · 1915", font=F(56), fill=INK)
g.text((80, 140), "an ordinary household bath, filled with water", font=F(32), fill=DIM)
g.text((80, H - 80), "Illustration · not an archive image", font=F(26), fill=DIM)
img.save(f"{d}/diag_room.png")

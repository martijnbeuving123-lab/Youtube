#!/usr/bin/env python3
"""Cards, schematic map and labelled illustrations for the Deptford video.
    python3 videos/deptford/make_visuals.py videos/deptford
Everything here is a card, schematic or illustration (labelled); no archive images."""
import sys, subprocess, math
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
sys.path.insert(0, "tools")
import cards
W, H = 1920, 1080
BG, INK, DIM, RED = cards.BG, cards.INK, cards.DIM, cards.ACCENT
F = lambda s, p=cards.SERIF: ImageFont.truetype(p, s)
d = sys.argv[1] + "/assets/cards"

def T(name, big, small=""): cards.text(f"{d}/{name}.png", big, small)
def Q(name, words, who=""): cards.quote(f"{d}/{name}.png", words, who)

def finish(img, name, label=None):
    if label:
        g = ImageDraw.Draw(img); g.text((80, H - 80), label, font=F(26), fill=DIM)
    cards.vignette(cards.grain(img), 0.45).save(f"{d}/{name}.png")

def fingerprint(size=700, seed=1, loop=True):
    """Synthetic ridge pattern (illustration only, not anyone's real print)."""
    rng = np.random.default_rng(seed)
    y, x = np.mgrid[-1:1:size*1j, -1.2:1.2:size*1j]
    cx, cy = 0.05 * rng.standard_normal(), -0.1
    r = np.sqrt((x - cx) ** 2 + ((y - cy) * 1.25) ** 2)
    th = np.arctan2(y - cy, x - cx)
    f = r * 38 + (3.0 * np.sin(th) if loop else 0) + 1.2 * np.sin(3 * x + 2 * y + seed) + 0.6 * np.sin(7 * y)
    rid = (np.sin(f) > 0.15).astype(np.uint8) * 255
    mask = ((x / 0.95) ** 2 + ((y + 0.05) / 1.0) ** 2) < 1
    a = np.where(mask, rid, 0).astype(np.uint8)
    return Image.fromarray(a).filter(ImageFilter.GaussianBlur(1.2))

def print_panel(img, box, seed, color, smudge=False):
    fp = fingerprint(box[2] - box[0], seed).resize((box[2] - box[0], box[3] - box[1]))
    if smudge:
        fp = fp.filter(ImageFilter.GaussianBlur(2.5))
        arr = np.array(fp).astype(float); yy, xx = np.mgrid[0:arr.shape[0], 0:arr.shape[1]]
        arr *= np.clip(0.35 + 0.65 * np.sin(xx / 90.0 + 1) ** 2, 0, 1); fp = Image.fromarray(arr.astype(np.uint8))
    layer = Image.new("RGB", fp.size, color)
    img.paste(layer, box[:2], fp)

# --- text cards ---
T("c01", "Deptford High Street", "Monday 27 March 1905 · 8.30 am")
T("c02", "No. 34 — shuttered", "Chapman's Oil and Colour Shop")
Q("c04", "No British jury had ever convicted anyone of murder on the strength of a fingerprint.")
cards.title(f"{d}/title.png", "PRECINCT ARCHIVE", "Case file: The Deptford Murders, 1905")
T("c07", "Chapman's Oil and Colour Shop", "paint · oils · brushes · household goods")
T("c08", "Thomas Farrow, 71", "Ann Farrow, 65 · the flat above the shop")
T("c09", "Every Monday", "the owner collects the week's takings")
T("c10", "8.30 am", "the shutters are still up")
T("c11", "The parlour behind the shop", "")
T("c12", "Doctor and police sent for", "Ann Farrow taken to hospital")
T("c14", "Police reconstruction", "not a witness account")
T("c16", "The cash box — empty", "accounts put the takings at about £13")
T("c17", "Sergeant Albert Atkinson", "moves the cash box with his bare hands")
T("c18", "Melville Macnaghten", "Assistant Commissioner (Crime), Scotland Yard")
T("c19", "The Belper Committee, 1900", "recommends fingerprints for identifying criminals")
T("c23", "1 July 1901", "the Fingerprint Bureau opens at Scotland Yard")
T("c24", "Burglary, yes.", "Murder — never.")
T("c26", "Handkerchief · paper · Scotland Yard", "the cash box goes to the Fingerprint Bureau")
T("c27", "Det. Insp. Charles Stockley Collins", "head of the Fingerprint Bureau")
T("c28", "Ruled out", "Thomas Farrow · Ann Farrow · Sgt Atkinson")
T("c29", "80,000 – 90,000 sets on file", "no match")
T("c30", "31 March 1905", "Ann Farrow dies without regaining consciousness")
T("c32", "About 7.30 am", "two men seen leaving the shop")
T("c33", "Brown suit and cap · Blue serge suit and bowler", "as described by witnesses")
T("c34", "Henry Littlefield · Ellen Stanton", "name the man in the brown suit")
T("c35", "Alfred Stratton, born 1882", "Albert Stratton, born 1884")
T("c36", "Annie Cromarty", "the brown coat · the shoes · the old stockings")
T("c37", "Sunday 2 April 1905", "Alfred arrested at the King of Prussia")
T("c38", "About £4", "buried near a local waterworks")
T("c41", "The case would stand or fall", "on one thumbprint")
T("c42", "The Old Bailey · 5 May 1905", "before Mr Justice Channell")
T("c43", "Richard Muir", "prosecuting for the Crown · 'Muir's playing cards'")
T("c44", "Over 40 witnesses", "for the Crown")
T("c45", "For the defence", "Dr John Garson · Dr Henry Faulds")
T("c46", "Alfred Stratton gives evidence", "'about half past two in the morning…'")
Q("c47", "I reckon he will get strung up and I shall get about ten years… He has led me into this.", "Albert Stratton, as reported by prison officer William Gittings")
T("c48", "Detective Inspector Collins", "explains fingerprints to the jury")
T("c50", "Dr John Garson", "'not in agreement'")
Q("c52", "I am an independent witness.", "Dr John Garson, under cross-examination")
T("c53", "Dr Henry Faulds", "not called")
T("c54", "Guilty", "6 May 1905")
T("c55", "23 May 1905 · 9 am", "HM Prison Wandsworth")
T("c56", "Not on the print alone", "but the print placed him inside the house")
T("c58", "The Henry system", "with Azizul Haque and Hemchandra Bose · Bengal, 1897")
T("c59", "Macnaghten · Muir", "Dr Crippen, 1910 — another case file")
T("c60", "Henry Faulds, 1843 – 1930", "memorial in Beith, Ayrshire")
T("c61", "Remembered for one first", "Britain's first murder conviction built on a fingerprint")
T("c62", "Thomas Farrow · Ann Farrow", "Deptford, 1905 · remembered with respect")
cards.title(f"{d}/end.png", "PRECINCT ARCHIVE", "This case file is closed.")

# --- schematic map of London ---
img = Image.new("RGB", (W, H), BG); g = ImageDraw.Draw(img)
pts = [(80, 430), (330, 470), (520, 560), (700, 520), (860, 430), (1000, 470), (1080, 600), (1170, 650), (1300, 600), (1360, 470), (1480, 430), (1700, 470), (1860, 440)]
g.line(pts, fill=(52, 70, 82), width=46, joint="curve")
for name, (x, y), col in [("City of London", (870, 360), INK), ("Wandsworth", (330, 640), DIM), ("Deptford", (1190, 720), RED), ("Greenwich", (1420, 640), DIM), ("Old Bailey", (780, 300), DIM)]:
    g.ellipse((x - 12, y - 12, x + 12, y + 12), fill=col)
    g.text((x + 22, y - 26), name, font=F(44 if col == RED else 38), fill=col)
g.text((80, 60), "London, 1905", font=F(60), fill=INK)
g.text((80, 140), "Deptford: south bank of the Thames, downriver from the City", font=F(32), fill=DIM)
g.text((560, 520), "River Thames", font=F(30, cards.SERIF_I), fill=(120, 140, 150))
finish(img, "map", "Schematic map, positions approximate")

# --- Bertillon vs fingerprints ---
img = Image.new("RGB", (W, H), BG); g = ImageDraw.Draw(img)
g.text((160, 160), "Bertillonage", font=F(70, cards.SERIF_B), fill=INK)
for i, t in enumerate(["head length and breadth", "arm span", "finger and foot length", "measured with callipers", "slow · depends on the clerk"]):
    g.text((170, 300 + i * 70), "· " + t, font=F(40), fill=DIM)
g.line((W // 2, 160, W // 2, 900), fill=RED, width=3)
g.text((1060, 160), "Fingerprints", font=F(70, cards.SERIF_B), fill=INK)
print_panel(img, (1180, 300, 1560, 760), 3, (200, 190, 170))
finish(img, "bertillon", "Illustration: synthetic ridge pattern, not a real print")

# --- the cash box (illustration) ---
img = Image.new("RGB", (W, H), BG); g = ImageDraw.Draw(img)
g.polygon([(560, 520), (1360, 520), (1460, 440), (660, 440)], fill=(70, 66, 58), outline=INK)
g.rectangle((560, 520, 1360, 820), fill=(58, 54, 48), outline=INK, width=4)
g.polygon([(1360, 520), (1460, 440), (1460, 740), (1360, 820)], fill=(46, 43, 38), outline=INK)
g.rectangle((700, 240, 1300, 400), fill=(84, 79, 70), outline=INK, width=4)
g.text((700, 190), "the inner tray, lifted out (underside)", font=F(34), fill=DIM)
smear = Image.new("L", (130, 170), 0); ImageDraw.Draw(smear).ellipse((10, 10, 120, 160), fill=150)
smear = smear.filter(ImageFilter.GaussianBlur(14)); img.paste(Image.new("RGB", smear.size, (150, 140, 110)), (960, 235), smear)
g.text((1320, 300), "← the smudge", font=F(40), fill=RED)
g.text((80, 60), "The cash box", font=F(60), fill=INK)
finish(img, "cashbox", "Illustration, not the actual cash box")

# --- single print ---
img = Image.new("RGB", (W, H), BG); print_panel(img, (660, 140, 1260, 940), 7, (210, 200, 180), smudge=True)
finish(img, "print", "Illustration: synthetic ridge pattern, not the Deptford print")

# --- comparison ---
def compare(name, title, match=False, points=False):
    img = Image.new("RGB", (W, H), BG); g = ImageDraw.Draw(img)
    print_panel(img, (180, 200, 780, 900), 7, (210, 200, 180), smudge=True)
    print_panel(img, (1140, 200, 1740, 900), 7 if match else 11, (210, 200, 180))
    g.text((180, 140), "mark from the cash box", font=F(36), fill=DIM)
    g.text((1140, 140), "inked thumbprint", font=F(36), fill=DIM)
    g.text((80, 50), title, font=F(56), fill=RED if match else INK)
    if points:
        rng = np.random.default_rng(4)
        for i in range(12):
            px, py = int(rng.integers(120, 480)), int(rng.integers(120, 600))
            for ox in (180, 1140):
                g.ellipse((ox + px - 16, 200 + py - 16, ox + px + 16, 200 + py + 16), outline=RED, width=4)
            g.line((180 + px + 16, 200 + py, 1140 + px - 16, 200 + py), fill=(120, 50, 40), width=1)
    finish(img, name, "Illustration: synthetic ridge patterns, not the Deptford prints")
compare("compare", "Comparing the mark with each finger")
compare("match", "Right thumb, Alfred Stratton: match", match=True)
compare("points", "Up to twelve points of agreement", match=True, points=True)

# --- two letters ---
img = Image.new("RGB", (W, H), BG); g = ImageDraw.Draw(img)
for i, (x, to) in enumerate([(250, "To the Director of Public Prosecutions"), (1010, "To the solicitor for the defence")]):
    paper = Image.new("RGB", (660, 760), (226, 214, 184)); pd = ImageDraw.Draw(paper)
    pd.text((50, 50), "Same day, 1905", font=F(32, cards.SERIF_I), fill=(110, 80, 55))
    pd.text((50, 110), to, font=F(30, cards.SERIF_B), fill=(70, 45, 30))
    for k in range(9):
        pd.line((50, 220 + k * 50, 610 - (k % 3) * 60, 220 + k * 50), fill=(150, 130, 100), width=3)
    pd.text((50, 680), "— J. G. Garson", font=F(32, cards.SERIF_I), fill=(70, 45, 30))
    paper = paper.rotate((-2, 2)[i], resample=Image.BICUBIC, expand=True, fillcolor=BG)
    img.paste(paper, (x, 150))
finish(img, "letters", "Reconstruction: the letters' wording is not shown")

# --- night-clothes / reconstruction diagram ---
img = Image.new("RGB", (W, H), BG); g = ImageDraw.Draw(img)
g.rectangle((300, 560, 1000, 900), outline=INK, width=5); g.text((330, 580), "Shop and parlour", font=F(40), fill=INK)
g.rectangle((300, 200, 1000, 540), outline=INK, width=5); g.text((330, 220), "Flat: bedroom", font=F(40), fill=INK)
g.line((1000, 880, 1120, 880, 1120, 520, 1000, 520), fill=DIM, width=4); g.text((1140, 680), "stairs", font=F(34), fill=DIM)
g.line((150, 820, 300, 820), fill=RED, width=6); g.text((40, 700), "street door:\nno forced entry", font=F(32), fill=RED)
g.text((330, 380), "cash box found here, empty", font=F(34), fill=DIM)
g.text((80, 60), "34 Deptford High Street", font=F(60), fill=INK)
finish(img, "house", "Schematic reconstruction, not a plan of the building")

# --- masks ---
img = Image.new("RGB", (W, H), BG); g = ImageDraw.Draw(img)
for x in (560, 1060):
    g.rounded_rectangle((x, 380, x + 320, 600), radius=60, fill=(30, 28, 26), outline=DIM, width=3)
    g.ellipse((x + 60, 450, x + 130, 500), fill=BG); g.ellipse((x + 190, 450, x + 260, 500), fill=BG)
g.text((80, 60), "Two masks, made from black stocking tops", font=F(56), fill=INK)
finish(img, "masks", "Illustration, not the actual masks")
print("visuals done")

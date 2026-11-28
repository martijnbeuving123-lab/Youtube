#!/usr/bin/env python3
"""Count the real archive images a video has, before rendering.

    python3 tools/image_check.py <video_dir> [--min 12]

Counts images in <video_dir>/assets/img/ that have a credits.json entry (so they came from an
archive tool: Wellcome, LoC, Commons, ...), and how many of them edit.json actually uses.
Exits 1 when fewer than --min are used, so the run keeps searching instead of rendering
a video made only of cards and maps.
"""
import json, os, sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import credits as cr


def source(c):
    s = (c.get("credit", "") + " " + c.get("page", "")).lower()
    for key, name in (("wellcome", "Wellcome"), ("loc.gov", "Library of Congress"),
                      ("wikimedia", "Wikimedia Commons"), ("archive.org", "Internet Archive")):
        if key in s:
            return name
    return "other"


def main():
    a = sys.argv[1:]
    if not a:
        sys.exit(__doc__)
    vdir = a[0].rstrip("/")
    need = int(a[a.index("--min") + 1]) if "--min" in a else 12
    credits = cr.load(vdir)
    have = {k: c for k, c in credits.items() if os.path.exists(f"{vdir}/assets/img/{k}.jpg")}
    used = set()
    if os.path.exists(f"{vdir}/edit.json"):
        txt = open(f"{vdir}/edit.json").read()
        used = {k for k in have if f"{k}.jpg" in txt or f'"{k}"' in txt}
    pool = used if os.path.exists(f"{vdir}/edit.json") else set(have)
    print(f"real archive images: {len(have)} downloaded, {len(used)} used in edit.json (need {need})")
    for s, n in Counter(source(have[k]) for k in pool).most_common():
        print(f"  {s}: {n}")
    if len(pool) < need:
        print("NOT ENOUGH: search more (Wellcome --books / --search, LoC) before rendering.")
        sys.exit(1)
    print("OK")


if __name__ == "__main__":
    main()

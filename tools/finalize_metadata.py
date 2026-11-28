#!/usr/bin/env python3
"""Fill CHAPTERS and CREDITS in <video_dir>/metadata.md from the render's timeline.

    python3 tools/finalize_metadata.py videos/<slug>

Chapter starts come from `chapters` in edit.json: {"beat_id": "Chapter title", ...}.
"""
import json, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import credits as cr

vdir = sys.argv[1].rstrip("/")
edit = json.load(open(f"{vdir}/edit.json"))
tl = {b["id"]: b["start"] for b in json.load(open(f"{vdir}/out/timeline.json"))}
credits = cr.load(vdir)
used = {v.split("/")[-1].rsplit(".", 1)[0] for b in json.load(open(f"{vdir}/out/used_visuals.json"))
        for v in (b["visual"], b.get("visual2")) if v} \
    if __import__("os").path.exists(f"{vdir}/out/used_visuals.json") else set(credits)


def ts(s):
    s = int(s)
    return f"{s // 60}:{s % 60:02d}" if s < 3600 else f"{s // 3600}:{s % 3600 // 60:02d}:{s % 60:02d}"


chapters = []
for i, (bid, title) in enumerate(edit["chapters"].items()):
    start = 0 if i == 0 else tl[bid]
    chapters.append(f"{ts(start)} {title}")
lines = []
for k, c in sorted(credits.items()):
    if k not in used:
        continue
    who = f", {c['artist']}" if c.get("artist") and c.get("license") != "Public domain" else ""
    via = f", {c['credit']}" if c.get("credit", "").startswith(("Wellcome", "Library of Congress")) else ""
    lines.append(f"- {cr.label(c)}{who}{via} ({c.get('license', '?')}): {c.get('page', '')}")
md = open(f"{vdir}/metadata.md").read()
md = md.replace("CHAPTERS\n", "CHAPTERS\n" + "\n".join(chapters) + "\n", 1)
md = md.replace("CREDITS\n", "\n".join(lines) + "\n", 1)
open(f"{vdir}/metadata.md", "w").write(md)
print("\n".join(chapters))

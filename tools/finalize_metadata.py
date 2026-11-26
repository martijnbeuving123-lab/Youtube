#!/usr/bin/env python3
"""Fill CHAPTERS and CREDITS in <video_dir>/metadata.md from the render's timeline.

    python3 tools/finalize_metadata.py videos/<slug>

Chapter starts come from `chapters` in edit.json: {"beat_id": "Chapter title", ...}.
"""
import json, sys

vdir = sys.argv[1].rstrip("/")
edit = json.load(open(f"{vdir}/edit.json"))
tl = {b["id"]: b["start"] for b in json.load(open(f"{vdir}/out/timeline.json"))}
credits = json.load(open(f"{vdir}/credits.json"))
used = {b["visual"].split("/")[-1].rsplit(".", 1)[0] for b in json.load(open(f"{vdir}/out/used_visuals.json"))} \
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
    who = f", {c['artist']}" if c["artist"] and c["license"] != "Public domain" else ""
    lines.append(f"- {c['title'][5:].rsplit('.', 1)[0]}{who} ({c['license']}): {c['page']}")
md = open(f"{vdir}/metadata.md").read()
md = md.replace("CHAPTERS\n", "CHAPTERS\n" + "\n".join(chapters) + "\n", 1)
md = md.replace("CREDITS\n", "\n".join(lines) + "\n", 1)
open(f"{vdir}/metadata.md", "w").write(md)
print("\n".join(chapters))

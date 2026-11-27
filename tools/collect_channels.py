"""Collect the latest long videos of competitor channels for the yt-viral skill.

    ~/kvenv/bin/python tools/collect_channels.py channel/competitors.txt [--per 30] > collected.json
    python3 .claude/skills/yt-viral/swipe.py collected.json --min 2.0

competitors.txt: one channel URL or @handle per line; '#' starts a comment.
Reads public channel listings only (yt-dlp, no login). Shorts (< 3 min) are left out.
"""
import argparse
import json
import subprocess
import sys


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("listfile")
    ap.add_argument("--per", type=int, default=30, help="latest videos per channel")
    a = ap.parse_args()

    rows = []
    for line in open(a.listfile):
        ch = line.split("#", 1)[0].strip()
        if not ch:
            continue
        url = ch if ch.startswith("http") else f"https://www.youtube.com/{ch}"
        url = url.rstrip("/") + "/videos"
        r = subprocess.run([sys.executable, "-m", "yt_dlp", "--flat-playlist", "-J",
                            "--playlist-end", str(a.per), url], capture_output=True, text=True)
        if r.returncode != 0:
            print(f"skip {ch}: {r.stderr.strip().splitlines()[-1:]}", file=sys.stderr)
            continue
        d = json.loads(r.stdout)
        name = d.get("channel") or d.get("uploader") or ch
        n = 0
        for e in d.get("entries") or []:
            if not e.get("view_count") or (e.get("duration") or 0) < 180:
                continue
            rows.append({"channel": name, "title": e.get("title"), "views": e["view_count"],
                         "url": f"https://www.youtube.com/watch?v={e['id']}", "duration": e.get("duration")})
            n += 1
        print(f"{name}: {n} videos", file=sys.stderr)
    json.dump(rows, sys.stdout, indent=1)


if __name__ == "__main__":
    main()

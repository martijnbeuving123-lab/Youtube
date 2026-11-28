"""Shared image-credit store for all download tools.

credits.json is a dict {name: {"title", "page", "license", "artist", "credit"}}.
Older list-style files (from loc_get.py) are converted on load.
"""
import json, os


def label(c):
    """Human title: strips the 'File:' prefix and extension of Commons titles."""
    t = c.get("title", "")
    return t[5:].rsplit(".", 1)[0] if t.startswith("File:") else t


def load(vdir):
    path = f"{vdir}/credits.json"
    if not os.path.exists(path):
        return {}
    data = json.load(open(path))
    if isinstance(data, dict):
        return data
    out = {}
    for c in data:  # old loc_get list format
        out[c["name"]] = {"title": c.get("title", ""), "page": c.get("source", ""),
                          "license": c.get("rights", "") or c.get("license", ""),
                          "artist": c.get("artist", ""), "credit": c.get("credit", "")}
    return out


def save(vdir, credits):
    json.dump(credits, open(f"{vdir}/credits.json", "w"), indent=1)
    with open(f"{vdir}/credits.md", "w") as f:
        f.write("# Image credits\n\n")
        for k, c in sorted(credits.items()):
            who = f" — {c['artist']}" if c.get("artist") else ""
            src = f" {c['credit']}." if c.get("credit") else ""
            f.write(f"- **{k}**: {label(c)}{who}.{src} {c.get('license', '?')}. {c.get('page', '')}\n")

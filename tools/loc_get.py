#!/usr/bin/env python3
"""Download Library of Congress photos and record their credits.

    python3 tools/loc_get.py <video_dir> <name>=<loc item id or URL> [...]
    python3 tools/loc_get.py --search "rosenberg spy"      # list candidates with rights

Saves <video_dir>/assets/img/<name>.jpg (largest JPEG, max 2400px wide) and merges
source, title, date and rights statement into <video_dir>/credits.json and credits.md.
Use only items whose rights say "No known restrictions" / "No copyright restriction known"
or that are US government work; check the rights line before using an image.
"""
import io, json, os, re, sys, urllib.parse, urllib.request
from PIL import Image

UA = "Mozilla/5.0 (documentary research; contact via YouTube channel)"


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    return urllib.request.urlopen(req, timeout=90).read()


def rights(item):
    r = item.get("rights_advisory") or item.get("rights") or ""
    return (r[0] if isinstance(r, list) and r else r) or ""


def search(q):
    url = f"https://www.loc.gov/photos/?q={urllib.parse.quote(q)}&fo=json&c=25&fa=online-format:image"
    for r in json.loads(get(url))["results"]:
        iid = r.get("id", "").rstrip("/").split("/")[-1]
        w = max([int(m.group(1)) for u in r.get("image_url", []) for m in [re.search(r"w=(\d+)", u)] if m] or [0])
        if w < 600:
            continue  # thumbnail only: full size withheld, usually because of rights
        print(f"{iid:>12}  w={w:<5} {r.get('date', '')[:4]}  {r.get('title', '')[:85]}")
        print(f"{'':>14}rights: {rights(r)[:100]}")


def fetch(vdir, name, ref):
    iid = ref.rstrip("/").split("/")[-1]
    data = json.loads(get(f"https://www.loc.gov/item/{iid}/?fo=json"))
    item = data.get("item", {})
    urls = []
    for res in data.get("resources", []):
        for f in res.get("files", []):
            for v in f:
                if v.get("mimetype") == "image/jpeg" and v.get("url"):
                    urls.append((v.get("width") or 0, v["url"]))
    if not urls:
        raise RuntimeError("no full-size image online (usually rights-restricted); pick another")
    urls.sort()
    best = [u for w, u in urls if w <= 2400] or [urls[0][1]]
    im = Image.open(io.BytesIO(get(best[-1]))).convert("RGB")
    os.makedirs(f"{vdir}/assets/img", exist_ok=True)
    im.save(f"{vdir}/assets/img/{name}.jpg", quality=92)
    title = item.get("title") or data.get("title") or iid
    date = item.get("date") or ""
    rt = rights(item) or rights(data)
    print(f"{name}: {im.width}x{im.height}  {title[:70]}\n   rights: {rt[:120]}")
    return {"name": name, "source": f"https://www.loc.gov/item/{iid}/", "title": title,
            "date": date, "rights": rt, "credit": "Library of Congress, Prints & Photographs Division"}


def main():
    if sys.argv[1] == "--search":
        return search(" ".join(sys.argv[2:]))
    vdir = sys.argv[1].rstrip("/")
    path = f"{vdir}/credits.json"
    credits = {c["name"]: c for c in (json.load(open(path)) if os.path.exists(path) else [])}
    for arg in sys.argv[2:]:
        name, ref = arg.split("=", 1)
        try:
            credits[name] = fetch(vdir, name, ref)
        except Exception as e:
            print(f"{name}: FAILED {e}")
    json.dump(list(credits.values()), open(path, "w"), indent=1)
    with open(f"{vdir}/credits.md", "w") as f:
        f.write("# Image credits\n\n")
        for c in credits.values():
            f.write(f"- **{c['name']}**: {c['title']} ({c.get('date', '')}). {c.get('credit', '')}. "
                    f"{c['source']}. Rights: {c.get('rights', '')}\n")


if __name__ == "__main__":
    main()

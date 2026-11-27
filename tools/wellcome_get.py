#!/usr/bin/env python3
"""Search and download Wellcome Collection images, with credits.

    python3 tools/wellcome_get.py --search "fingerprints scotland yard"
    python3 tools/wellcome_get.py <video_dir> <name>=<image id> [...]

Only licences that allow use on a monetised channel are listed or downloaded:
public domain (pdm), CC0 and CC BY. CC BY-NC and other restricted images are skipped.
Saves <video_dir>/assets/img/<name>.jpg (up to 2000 px) and merges the source, title,
creator and licence into credits.json / credits.md (via tools/credits.py).
CC BY needs the credit in the description; finalize_metadata.py adds it from credits.json.
"""
import io, json, os, sys, urllib.parse, urllib.request
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import credits as cr

API = "https://api.wellcomecollection.org/catalogue/v2"
OK = {"pdm": "Public domain", "cc-0": "CC0", "cc-by": "CC BY 4.0"}
UA = "PrecinctArchive/1.0 (documentary research; https://www.youtube.com/@precinctarchive)"


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    return urllib.request.urlopen(req, timeout=90).read()


def lic(img):
    return (img.get("locations") or [{}])[0].get("license", {}).get("id", "")


def search(q, n=40):
    """Lists usable images; open the page URL in credits to check the picture before use."""
    qs = urllib.parse.urlencode({"query": q, "pageSize": n, "locations.license": ",".join(OK)})
    d = json.loads(get(f"{API}/images?{qs}"))
    print(f"{d.get('totalResults', 0)} usable results for {q!r}")
    for img in d.get("results", []):
        print(f"{img['id']:>10}  {OK.get(lic(img), lic(img)):<13} {img['source'].get('title', '')[:90]}")


def fetch(vdir, name, iid):
    img = json.loads(get(f"{API}/images/{iid}"))
    l = lic(img)
    if l not in OK:
        raise RuntimeError(f"licence {l!r} not usable on a monetised channel; pick another")
    src = img.get("source", {})
    base = img["locations"][0]["url"].rsplit("/info.json", 1)[0]
    im = Image.open(io.BytesIO(get(f"{base}/full/!2000,2000/0/default.jpg"))).convert("RGB")
    os.makedirs(f"{vdir}/assets/img", exist_ok=True)
    im.save(f"{vdir}/assets/img/{name}.jpg", quality=92)
    work = json.loads(get(f"{API}/works/{src.get('id')}?include=contributors,production"))
    who = ", ".join(c.get("agent", {}).get("label", "") for c in work.get("contributors", []))
    date = ", ".join(d.get("label", "") for p in work.get("production", []) for d in p.get("dates", []))
    title = src.get("title", iid) + (f" ({date})" if date else "")
    print(f"{name}: {im.width}x{im.height}  {OK[l]}  {title[:70]}")
    return {"title": title, "page": f"https://wellcomecollection.org/works/{src.get('id')}/images?id={iid}",
            "license": OK[l], "artist": who, "credit": "Wellcome Collection"}


def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    if sys.argv[1] == "--search":
        return search(" ".join(sys.argv[2:]))
    vdir = sys.argv[1].rstrip("/")
    credits = cr.load(vdir)
    for arg in sys.argv[2:]:
        name, iid = arg.split("=", 1)
        try:
            credits[name] = fetch(vdir, name, iid.strip())
        except Exception as e:
            print(f"{name}: FAILED {e}")
    cr.save(vdir, credits)


if __name__ == "__main__":
    main()

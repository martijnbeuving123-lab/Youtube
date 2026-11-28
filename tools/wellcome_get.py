#!/usr/bin/env python3
"""Search and download Wellcome Collection images, with credits.

    python3 tools/wellcome_get.py --search "fingerprints scotland yard"
    python3 tools/wellcome_get.py <video_dir> <name>=<image id> [...]
    python3 tools/wellcome_get.py --books "police photographs" [--before 1928]
    python3 tools/wellcome_get.py --pages <work id>          # list a book's pages
    python3 tools/wellcome_get.py --sheet <work id> <out.jpg> [first-last]   # contact sheet
    python3 tools/wellcome_get.py <video_dir> <name>=<work id>:<page>[:x,y,w,h] [...]

--books searches whole digitised books and pamphlets (only public domain / CC0 / CC BY) and
is the richest source: period police manuals, forensic textbooks, trial reports and
newspapers, with plates and photographs. --pages lists each page with its label so you can
pick the plates; then fetch "<work id>:<page number>" like an image id. Add ":x,y,w,h" (percent
of the page, e.g. ":10,15,80,50") to crop to the plate and leave the margins and caption out.

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


def iiif_licence(work):
    for it in work.get("items", []):
        for l in it.get("locations", []):
            if l.get("locationType", {}).get("id") == "iiif-presentation":
                return l.get("url"), l.get("license", {}).get("id", "")
    return None, ""


def books(q, before=None, n=30):
    """Digitised works with a usable licence; prints work id, licence, date and title."""
    p = {"query": q, "pageSize": 100, "items.locations.locationType": "iiif-presentation",
         "include": "items,production"}
    if before:
        p["production.dates.to"] = f"{before}-12-31"
    d = json.loads(get(f"{API}/works?{urllib.parse.urlencode(p)}"))
    rows = []
    for w in d.get("results", []):
        url, l = iiif_licence(w)
        if url and l in OK:
            date = ", ".join(x.get("label", "") for p in w.get("production", []) for x in p.get("dates", []))
            rows.append((w["id"], OK[l], date[:12], w["title"][:80]))
    print(f"{len(rows)} usable digitised works for {q!r} (of {d.get('totalResults', 0)})")
    for r in rows[:n]:
        print(f"{r[0]:>10}  {r[1]:<13} {r[2]:<12} {r[3]}")


def canvases(wid):
    work = json.loads(get(f"{API}/works/{wid}?include=items,contributors,production"))
    url, l = iiif_licence(work)
    if not url:
        raise RuntimeError(f"{wid} has no digitised copy")
    man = json.loads(get(url))
    cv = [c for s in man.get("sequences", []) for c in s.get("canvases", [])]
    return work, l, cv


def pages(wid):
    work, l, cv = canvases(wid)
    print(f"{work['title'][:90]}  [{OK.get(l, l + ' - NOT USABLE')}]  {len(cv)} pages")
    for i, c in enumerate(cv, 1):
        print(f"  {i:>4}  {c.get('label', '')}")


def sheet(wid, out, rng=None):
    """Numbered thumbnails of a book's pages, to spot the plates and photographs by eye."""
    from PIL import ImageDraw
    work, l, cv = canvases(wid)
    a, b = (int(x) for x in rng.split("-")) if rng else (1, min(len(cv), 120))
    idx = list(range(a, min(b, len(cv)) + 1))
    W, H, cols = 160, 230, 10
    rows = (len(idx) + cols - 1) // cols
    canvas = Image.new("RGB", (cols * W, rows * H), "white")
    d = ImageDraw.Draw(canvas)
    for k, i in enumerate(idx):
        svc = cv[i - 1]["images"][0]["resource"]["service"]["@id"]
        try:
            t = Image.open(io.BytesIO(get(f"{svc}/full/!150,200/0/default.jpg"))).convert("RGB")
            canvas.paste(t, ((k % cols) * W + 5, (k // cols) * H + 5))
        except Exception:
            pass
        d.text(((k % cols) * W + 5, (k // cols) * H + 208), str(i), fill="red")
    canvas.save(out, quality=80)
    print(f"{out}: pages {idx[0]}-{idx[-1]} of {len(cv)} [{OK.get(l, l + ' - NOT USABLE')}]")


def fetch_page(vdir, name, wid, page, region="full"):
    work, l, cv = canvases(wid)
    if l not in OK:
        raise RuntimeError(f"licence {l!r} not usable on a monetised channel; pick another")
    c = cv[int(page) - 1]
    svc = c["images"][0]["resource"]["service"]["@id"]
    reg = f"pct:{region}" if region != "full" else "full"
    im = Image.open(io.BytesIO(get(f"{svc}/{reg}/!2000,2000/0/default.jpg"))).convert("RGB")
    os.makedirs(f"{vdir}/assets/img", exist_ok=True)
    im.save(f"{vdir}/assets/img/{name}.jpg", quality=92)
    lab = c.get("label", "")
    lab = lab if lab and lab != "-" else f"image {page}"
    who = ", ".join(x.get("agent", {}).get("label", "") for x in work.get("contributors", []))
    date = ", ".join(d.get("label", "") for p in work.get("production", []) for d in p.get("dates", []))
    title = work["title"] + (f" ({date})" if date else "") + f", p. {lab}"
    print(f"{name}: {im.width}x{im.height}  {OK[l]}  {title[:70]}")
    return {"title": title, "page": f"https://wellcomecollection.org/works/{wid}/items?canvas={page}",
            "license": OK[l], "artist": who, "credit": "Wellcome Collection"}


def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    if sys.argv[1] == "--search":
        return search(" ".join(sys.argv[2:]))
    if sys.argv[1] == "--books":
        a = sys.argv[2:]
        before = a[a.index("--before") + 1] if "--before" in a else None
        q = [x for i, x in enumerate(a) if x != "--before" and (i == 0 or a[i - 1] != "--before")]
        return books(" ".join(q), before)
    if sys.argv[1] == "--sheet":
        return sheet(sys.argv[2], sys.argv[3], sys.argv[4] if len(sys.argv) > 4 else None)
    if sys.argv[1] == "--pages":
        return pages(sys.argv[2])
    vdir = sys.argv[1].rstrip("/")
    credits = cr.load(vdir)
    for arg in sys.argv[2:]:
        name, iid = arg.split("=", 1)
        try:
            iid = iid.strip()
            if ":" in iid:
                credits[name] = fetch_page(vdir, name, *iid.split(":", 2))
            else:
                credits[name] = fetch(vdir, name, iid)
        except Exception as e:
            print(f"{name}: FAILED {e}")
    cr.save(vdir, credits)


if __name__ == "__main__":
    main()

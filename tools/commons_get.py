#!/usr/bin/env python3
"""Download Wikimedia Commons files and record their credits.

    python3 tools/commons_get.py <video_dir> <name>="File:Title.jpg" [...]

Saves <video_dir>/assets/img/<name>.jpg (max 1920px wide) and rewrites
<video_dir>/credits.json and credits.md with source, author and licence.
"""
import json, os, re, sys, time, urllib.parse, urllib.request

UA = "PrecinctArchiveResearch/0.1 (small documentary research script)"


def get(url, tries=5):
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            return urllib.request.urlopen(req, timeout=60).read()
        except Exception as e:
            err = e
            time.sleep(10 * (i + 1))
    raise err


def strip(html):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", html or "")).strip()


def main():
    vdir, pairs = sys.argv[1], sys.argv[2:]
    os.makedirs(f"{vdir}/assets/img", exist_ok=True)
    cpath = f"{vdir}/credits.json"
    credits = json.load(open(cpath)) if os.path.exists(cpath) else {}
    for pair in pairs:
        name, title = pair.split("=", 1)
        if os.path.exists(f"{vdir}/assets/img/{name}.jpg") and name in credits:
            continue
        try:
            fetch(vdir, name, title, credits)
        except Exception as e:
            print(f"{name}: FAILED {e}")
        json.dump(credits, open(cpath, "w"), indent=1)
        time.sleep(3)
    write_md(vdir, credits)


def fetch(vdir, name, title, credits):
    if True:
        q = urllib.parse.urlencode({"action": "query", "format": "json", "titles": title,
                                    "prop": "imageinfo", "iiprop": "url|extmetadata",
                                    "iiurlwidth": 1920})  # a standard thumbnail size (w.wiki/GHai)
        meta = json.loads(get("https://commons.wikimedia.org/w/api.php?" + q))
        page = next(iter(meta["query"]["pages"].values()))
        ii = page["imageinfo"][0]
        m = ii.get("extmetadata", {})
        url = (ii.get("thumburl") or ii["url"]).replace("//thumb.wikimedia.org/", "//upload.wikimedia.org/")
        data = get(url)
        out = f"{vdir}/assets/img/{name}.jpg"
        open(out, "wb").write(data)
        credits[name] = {"title": title, "page": ii["descriptionurl"],
                         "license": m.get("LicenseShortName", {}).get("value", "?"),
                         "artist": strip(m.get("Artist", {}).get("value", "")),
                         "credit": strip(m.get("Credit", {}).get("value", ""))[:200]}
        print(f"{name}: {len(data)//1024} KB  {credits[name]['license']}")


def write_md(vdir, credits):
    with open(f"{vdir}/credits.md", "w") as f:
        f.write("# Image credits\n\nAll images via Wikimedia Commons.\n\n")
        for k, c in sorted(credits.items()):
            who = f" — {c['artist']}" if c["artist"] else ""
            f.write(f"- **{k}**: {c['title'][5:]}{who}. {c['license']}. {c['page']}\n")


if __name__ == "__main__":
    main()

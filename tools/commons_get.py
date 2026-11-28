#!/usr/bin/env python3
"""Download Wikimedia Commons files and record their credits.

    python3 tools/commons_get.py <video_dir> <name>="File:Title.jpg" [...]

Saves <video_dir>/assets/img/<name>.jpg (max 1280px wide) and rewrites
<video_dir>/credits.json and credits.md with source, author and licence.
"""
import json, os, re, sys, time, urllib.error, urllib.parse, urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import credits as cr

UA = "PrecinctArchiveBot/0.2 (https://www.youtube.com/@precinctarchive) python-urllib"


def get(url, tries=4):
    """Polite fetch: honour Retry-After on 429 instead of hammering."""
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            return urllib.request.urlopen(req, timeout=60).read()
        except urllib.error.HTTPError as e:
            err = e
            wait = int(e.headers.get("Retry-After", 30)) if e.code == 429 else 15
            print(f"  waiting {wait}s ({e.code})", flush=True)
            time.sleep(min(wait, 900) + 5)
        except Exception as e:
            err = e
            time.sleep(15)
    raise err


def strip(html):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", html or "")).strip()


def main():
    vdir, pairs = sys.argv[1], sys.argv[2:]
    os.makedirs(f"{vdir}/assets/img", exist_ok=True)
    credits = cr.load(vdir)
    for pair in pairs:
        name, title = pair.split("=", 1)
        if os.path.exists(f"{vdir}/assets/img/{name}.jpg") and name in credits:
            continue
        try:
            fetch(vdir, name, title, credits)
        except Exception as e:
            print(f"{name}: FAILED {e}", flush=True)
        cr.save(vdir, credits)
        time.sleep(60)
    cr.save(vdir, credits)


def fetch(vdir, name, title, credits):
    if True:
        q = urllib.parse.urlencode({"action": "query", "format": "json", "titles": title,
                                    "prop": "imageinfo", "iiprop": "url|extmetadata",
                                    "iiurlwidth": 1280})  # a standard thumbnail size (w.wiki/GHai)
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
        print(f"{name}: {len(data)//1024} KB  {credits[name]['license']}", flush=True)



if __name__ == "__main__":
    main()

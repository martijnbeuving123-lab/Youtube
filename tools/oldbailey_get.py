#!/usr/bin/env python3
"""Old Bailey Proceedings (1674-1913): search trials and save the full trial text.

    python3 tools/oldbailey_get.py --search "stratton fingerprint" [--year 1905]
    python3 tools/oldbailey_get.py <video_dir> <trial id, e.g. t19050502-404> [...]

Saves <video_dir>/sources/oldbailey-<id>.txt (the verbatim trial account plus its citation),
to quote and cite in research.md. Primary source for cases tried at the Old Bailey up to 1913.
The scans of the printed pages are licensed for non-commercial use only: do NOT put them
in a video. The text itself (the words spoken in court) is quoted with the citation.
The API refuses requests without a User-Agent; this one identifies the channel honestly.
"""
import html, json, os, re, sys, urllib.parse, urllib.request

API = "https://www.dhi.ac.uk/api/data"
UA = "PrecinctArchive/1.0 (documentary research; https://www.youtube.com/@precinctarchive)"


def get(path):
    req = urllib.request.Request(f"{API}/{path}", headers={"User-Agent": UA})
    return json.loads(urllib.request.urlopen(req, timeout=60).read())


def clean(s):
    return html.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", s or ""))).strip()


def search(words, year=None):
    q = {"text": words, "start": 0, "count": 30}
    if year:
        q.update(year_gte=year, year_lte=year)
    d = get("oldbailey_record?" + urllib.parse.urlencode(q))
    print(f"{d['hits']['total']} hits")
    for h in d["hits"]["hits"]:
        s = h["_source"]
        if s["idkey"].startswith("t"):
            print(f"{s['idkey']:>16}  {s.get('title', '')[:100]}")


def fetch(vdir, tid):
    s = get(f"oldbailey_record_single?idkey={tid}")["hits"]["hits"][0]["_source"]
    os.makedirs(f"{vdir}/sources", exist_ok=True)
    out = f"{vdir}/sources/oldbailey-{tid}.txt"
    with open(out, "w") as f:
        f.write(f"{s.get('title', tid)}\n")
        f.write(f"Source: {clean(s.get('citation'))}\nURL: https://www.oldbaileyonline.org/record/{tid}\n\n")
        f.write(clean(s.get("html") or s.get("text")) + "\n")
    print(f"{tid}: {os.path.getsize(out) // 1024} KB -> {out}  ({s.get('title', '')[:70]})")


def main():
    a = sys.argv[1:]
    if not a:
        sys.exit(__doc__)
    if a[0] == "--search":
        year = None
        if "--year" in a:
            i = a.index("--year")
            year, a = a[i + 1], a[:i] + a[i + 2:]
        return search(" ".join(a[1:]), year)
    for tid in a[1:]:
        try:
            fetch(a[0].rstrip("/"), tid)
        except Exception as e:
            print(f"{tid}: FAILED {e}")


if __name__ == "__main__":
    main()

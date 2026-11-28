#!/usr/bin/env python3
"""Our own YouTube uploader (YouTube Data API v3), used by .github/workflows/youtube.yml.

    python3 tools/youtube_api.py upload <meta.json> <video.mp4>   # prints RESULT {"videoId": ...}
    python3 tools/youtube_api.py schedule <videoId> <ISO time>    # private + publishAt
    python3 tools/youtube_api.py status <videoId>                  # privacy, publishAt, processing
    python3 tools/youtube_api.py whoami                            # which channel the token is for

Credentials come from the environment, never from files in the repo:
    YT_CLIENT_ID, YT_CLIENT_SECRET, YT_REFRESH_TOKEN
(set as GitHub Actions secrets; see channel/youtube-api-setup.md).

meta.json (paths relative to the repo root):
{
  "title": "...", "description": "...", "tags": ["..."], "categoryId": "27",
  "madeForKids": false, "syntheticMedia": true, "language": "en",
  "thumbnail": "defector-files/deliveries/<slug>/thumbnail.jpg",
  "captions": "defector-files/deliveries/<slug>/captions.srt",
  "publishAt": null          # optional ISO time; otherwise it stays private until scheduled
}
Videos are always uploaded PRIVATE. Only standard library; no extra packages.
"""
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
import uuid

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
API = "https://www.googleapis.com/youtube/v3"
UPLOAD = "https://www.googleapis.com/upload/youtube/v3"


def die(msg):
    print("ERROR " + msg, flush=True)
    sys.exit(1)


def http(method, url, body=None, headers=None, raw=False):
    req = urllib.request.Request(url, data=body, method=method, headers=headers or {})
    try:
        with urllib.request.urlopen(req, timeout=600) as r:
            data = r.read()
            return (r, data) if raw else (json.loads(data) if data else {})
    except urllib.error.HTTPError as e:
        die(f"{method} {url.split('?')[0]} -> {e.code}: {e.read().decode(errors='replace')[:800]}")


def token():
    for k in ("YT_CLIENT_ID", "YT_CLIENT_SECRET", "YT_REFRESH_TOKEN"):
        if not os.environ.get(k):
            die(f"{k} is not set (GitHub secret missing?)")
    body = urllib.parse.urlencode({
        "client_id": os.environ["YT_CLIENT_ID"], "client_secret": os.environ["YT_CLIENT_SECRET"],
        "refresh_token": os.environ["YT_REFRESH_TOKEN"], "grant_type": "refresh_token"}).encode()
    r = http("POST", "https://oauth2.googleapis.com/token", body,
             {"Content-Type": "application/x-www-form-urlencoded"})
    return r["access_token"]


def auth(tok, extra=None):
    h = {"Authorization": f"Bearer {tok}"}
    h.update(extra or {})
    return h


def path(p):
    return p if os.path.isabs(p) else os.path.join(ROOT, p)


def upload(meta_path, video):
    meta = json.load(open(path(meta_path)))
    tok = token()
    status = {"privacyStatus": "private", "selfDeclaredMadeForKids": bool(meta.get("madeForKids", False)),
              "containsSyntheticMedia": bool(meta.get("syntheticMedia", True)), "embeddable": True}
    if meta.get("publishAt"):
        status["publishAt"] = meta["publishAt"]
    body = {"snippet": {"title": meta["title"][:100], "description": meta.get("description", "")[:5000],
                        "tags": meta.get("tags", [])[:30], "categoryId": str(meta.get("categoryId", "27")),
                        "defaultLanguage": meta.get("language", "en"),
                        "defaultAudioLanguage": meta.get("language", "en")},
            "status": status}
    size = os.path.getsize(video)
    r, _ = http("POST", f"{UPLOAD}/videos?uploadType=resumable&part=snippet,status&notifySubscribers=false",
                json.dumps(body).encode(), auth(tok, {"Content-Type": "application/json; charset=UTF-8",
                                                      "X-Upload-Content-Length": str(size),
                                                      "X-Upload-Content-Type": "video/mp4"}), raw=True)
    loc = r.headers["Location"]
    with open(video, "rb") as f:
        res = http("PUT", loc, f.read(), auth(tok, {"Content-Type": "video/mp4", "Content-Length": str(size)}))
    vid = res["id"]
    print(f"uploaded {vid} (private)", flush=True)
    result = {"videoId": vid, "url": f"https://www.youtube.com/watch?v={vid}", "thumbnail": False, "captions": False}
    if meta.get("thumbnail") and os.path.exists(path(meta["thumbnail"])):
        img = open(path(meta["thumbnail"]), "rb").read()
        http("POST", f"{UPLOAD}/thumbnails/set?videoId={vid}&uploadType=media", img,
             auth(tok, {"Content-Type": "image/jpeg"}))
        result["thumbnail"] = True
    if meta.get("captions") and os.path.exists(path(meta["captions"])):
        b = uuid.uuid4().hex
        snippet = {"snippet": {"videoId": vid, "language": meta.get("language", "en"), "name": "English"}}
        srt = open(path(meta["captions"]), "rb").read()
        payload = (f"--{b}\r\nContent-Type: application/json; charset=UTF-8\r\n\r\n{json.dumps(snippet)}\r\n"
                   f"--{b}\r\nContent-Type: application/octet-stream\r\n\r\n").encode() + srt + f"\r\n--{b}--".encode()
        http("POST", f"{UPLOAD}/captions?uploadType=multipart&part=snippet", payload,
             auth(tok, {"Content-Type": f"multipart/related; boundary={b}"}))
        result["captions"] = True
    print("RESULT " + json.dumps(result), flush=True)


def get(tok, vid):
    r = http("GET", f"{API}/videos?part=status,snippet,contentDetails,processingDetails&id={vid}", None, auth(tok))
    if not r.get("items"):
        die(f"video {vid} not found for this channel")
    return r["items"][0]


def schedule(vid, when):
    tok = token()
    st = get(tok, vid)["status"]
    status = {"privacyStatus": "private", "publishAt": when,
              "selfDeclaredMadeForKids": st.get("selfDeclaredMadeForKids", False),
              "embeddable": st.get("embeddable", True)}
    if "containsSyntheticMedia" in st:
        status["containsSyntheticMedia"] = st["containsSyntheticMedia"]
    http("PUT", f"{API}/videos?part=status", json.dumps({"id": vid, "status": status}).encode(),
         auth(tok, {"Content-Type": "application/json"}))
    after = get(tok, vid)["status"]
    print("RESULT " + json.dumps({"videoId": vid, "privacyStatus": after.get("privacyStatus"),
                                  "publishAt": after.get("publishAt")}), flush=True)


def status(vid):
    it = get(token(), vid)
    print("RESULT " + json.dumps({"videoId": vid, "title": it["snippet"]["title"], "status": it["status"],
                                  "duration": it["contentDetails"].get("duration"),
                                  "processing": it.get("processingDetails", {}).get("processingStatus")}), flush=True)


def whoami():
    r = http("GET", f"{API}/channels?part=snippet&mine=true", None, auth(token()))
    print("RESULT " + json.dumps([{"id": c["id"], "title": c["snippet"]["title"]} for c in r.get("items", [])]))


if __name__ == "__main__":
    cmd, *args = sys.argv[1:] or ["help"]
    {"upload": upload, "schedule": schedule, "status": status, "whoami": whoami}.get(
        cmd, lambda *a: print(__doc__))(*args)

#!/usr/bin/env python3
"""Stage a finished video on GitHub so Hermoso can fetch it, then empty the stage again.

    python3 tools/hermoso_stage.py push <video.mp4>   # prints the public raw URL
    python3 tools/hermoso_stage.py clear              # empties the staging branch

Why: Hermoso refuses files over ~16 MB sent from this cloud session, and fetches any size
from a public URL. The repo is public, so a file on a branch has a raw.githubusercontent URL.
GitHub caps files at 100 MB, so `push` makes an upload copy of at most ~95 MB (two-pass
x264; 1080p when the bitrate allows, else 720p) and force-pushes it as the only file of an
orphan commit on branch `upload-staging`. After Hermoso has fetched it (upload_file url=...),
run `clear` AT ONCE: it force-pushes an empty commit, so the unpublished video stops being
reachable at that URL. Cloud sessions cannot delete branches, which is why the branch is reused.
"""
import json, os, subprocess, sys, tempfile

BRANCH = "upload-staging"
REPO = "martijnbeuving123-lab/Youtube"
MAX_MB = int(os.environ.get("STAGE_MAX_MB", 95))  # override only for tests
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def run(cmd, **kw):
    print("+", " ".join(cmd) if len(" ".join(cmd)) < 200 else cmd[0], flush=True)
    return subprocess.run(cmd, check=True, **kw)


def duration(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "json", path],
                         check=True, capture_output=True, text=True).stdout
    return float(json.loads(out)["format"]["duration"])


def make_upload_copy(src, dst):
    if os.path.getsize(src) <= MAX_MB * 1024 * 1024:
        run(["cp", src, dst])
        return
    dur = duration(src)
    audio_k = 128
    video_k = int(MAX_MB * 8 * 1024 * 0.97 / dur) - audio_k  # 3% container margin
    height = 1080 if video_k >= 1400 else 720
    print(f"upload copy: {dur / 60:.1f} min, video {video_k} kb/s at {height}p", flush=True)
    with tempfile.TemporaryDirectory() as td:
        common = ["-vf", f"scale=-2:{height}", "-c:v", "libx264", "-preset", "slow", "-b:v", f"{video_k}k",
                  "-pix_fmt", "yuv420p", "-passlogfile", f"{td}/pass"]
        run(["ffmpeg", "-loglevel", "error", "-y", "-i", src, *common, "-pass", "1", "-an", "-f", "mp4", os.devnull])
        run(["ffmpeg", "-loglevel", "error", "-y", "-i", src, *common, "-pass", "2",
             "-c:a", "aac", "-b:a", f"{audio_k}k", "-movflags", "+faststart", dst])
    mb = os.path.getsize(dst) / 1024 / 1024
    if mb > 99:
        sys.exit(f"upload copy is {mb:.0f} MB, over GitHub's 100 MB limit")
    print(f"upload copy: {mb:.0f} MB", flush=True)


def push_commit(files, message):
    """Force-push an orphan commit holding exactly `files` (name -> path) to BRANCH."""
    remote = subprocess.run(["git", "-C", ROOT, "remote", "get-url", "origin"],
                            check=True, capture_output=True, text=True).stdout.strip()
    with tempfile.TemporaryDirectory() as td:
        run(["git", "init", "-q", td])
        run(["git", "-C", td, "checkout", "-q", "--orphan", BRANCH])
        for name, path in files.items():
            run(["cp", path, f"{td}/{name}"])
        run(["git", "-C", td, "add", "-A"])
        run(["git", "-C", td, "-c", "user.name=Claude", "-c", "user.email=noreply@anthropic.com",
             "commit", "-qm", message])
        for i in range(4):
            r = subprocess.run(["git", "-C", td, "push", "-q", "-f", remote, f"{BRANCH}:refs/heads/{BRANCH}"])
            if r.returncode == 0:
                return
            print(f"push failed, retry {i + 1}", flush=True)
            subprocess.run(["sleep", str(5 * (i + 1))])
        sys.exit("push to upload-staging failed")


def main():
    if len(sys.argv) < 2 or sys.argv[1] not in ("push", "clear"):
        sys.exit(__doc__)
    if sys.argv[1] == "clear":
        with tempfile.TemporaryDirectory() as td:
            open(f"{td}/README.md", "w").write("Temporary upload staging for Hermoso; emptied after each upload.\n")
            push_commit({"README.md": f"{td}/README.md"}, "Empty upload staging")
        print("upload-staging emptied")
        return
    src = sys.argv[2]
    with tempfile.TemporaryDirectory() as td:
        copy = f"{td}/video.mp4"
        make_upload_copy(src, copy)
        push_commit({"video.mp4": copy}, "Temporary upload copy for Hermoso")
    print(f"https://raw.githubusercontent.com/{REPO}/{BRANCH}/video.mp4")


if __name__ == "__main__":
    main()

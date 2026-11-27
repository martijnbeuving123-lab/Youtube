"""
YouTube Automation Pipeline — Template
=======================================

A scheduled-upload pipeline for YouTube + optional TikTok/Instagram cross-post.
This is a TEMPLATE — replace all values in [BRACKETS] with your own.

Recommended setup flow: don't edit this file by hand. Tell Claude:
    "Read START_HERE.md and walk me through setting this up"
and Claude will fill in the placeholders for you, ask the right questions,
and produce a customized version named upload.py.

Architecture:
    spreadsheet (the brain) -> this script -> YouTube API
                                            -> Upload Post API -> TikTok + IG

Usage:
    python pipeline_template.py               # Upload 6 videos (default)
    python pipeline_template.py 10            # Upload 10 videos
    python pipeline_template.py --check       # Verify spreadsheet, no uploads

Author: CryptoClaud (https://www.youtube.com/@CryptoClaud)
License: MIT — see LICENSE file
"""

import os
import sys
import json
import shutil
import argparse
from datetime import datetime, timedelta
from pathlib import Path

# Third-party imports — install via: pip install google-api-python-client google-auth-oauthlib openpyxl requests
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError
from openpyxl import load_workbook
import requests

try:
    from zoneinfo import ZoneInfo  # Python 3.9+
except ImportError:
    from backports.zoneinfo import ZoneInfo  # pip install backports.zoneinfo


# ============================================================
# CONFIGURATION — replace [BRACKETED] values with your own
# ============================================================

# Your YouTube Channel ID (from YouTube Studio -> Settings -> Channel -> Advanced)
EXPECTED_CHANNEL_ID = "[CHANNEL_ID]"

# Path to your OAuth client_secret.json file (download from Google Cloud Console)
# CRITICAL: Keep this file OUTSIDE your project folder if the project is on GitHub
CLIENT_SECRET_PATH = "[CLIENT_SECRET_PATH]"

# Path where the OAuth token will be cached (created automatically on first run)
# Same recommendation: keep outside the project folder
TOKEN_FILE_PATH = "[TOKEN_FILE_PATH]"

# Path to the folder containing your video files
VIDEOS_FOLDER = "[VIDEOS_FOLDER]"

# Path to your upload master spreadsheet (the brain)
SPREADSHEET_PATH = "[SPREADSHEET_PATH]"

# YouTube category ID for your videos
# Common: 15=Pets & Animals, 22=People & Blogs, 24=Entertainment, 27=Education
CATEGORY_ID = "[CATEGORY_ID]"

# Hours to publish at (Pacific time by default)
# e.g. [10, 17] means 10:00 AM and 5:00 PM
PUBLISH_HOURS = [10, 17]

# Days of week to publish (0=Mon, 6=Sun)
PUBLISH_DAYS = [0, 1, 2, 3, 4, 5, 6]

# Timezone for scheduling (use IANA name)
TIMEZONE = "[TIMEZONE]"  # e.g. America/Los_Angeles

# Whether your content is "Made for Kids" (kids' content has different distribution)
MADE_FOR_KIDS = False

# YouTube OAuth scopes — these are the minimum required
SCOPES = ["https://www.googleapis.com/auth/youtube.upload",
          "https://www.googleapis.com/auth/youtube.readonly"]

# Cross-post configuration (set CROSSPOST_ENABLED = False to skip)
CROSSPOST_ENABLED = False
UPLOAD_POST_API_KEY = "[UPLOAD_POST_API_KEY]"
UPLOAD_POST_PROFILE = "[UPLOAD_POST_PROFILE]"
UPLOAD_POST_API_URL = "https://api.upload-post.com/api/upload"

# Where to log run state — created automatically
STATE_DIR = Path(__file__).parent / "state"
UPLOAD_LOG_PATH = STATE_DIR / "upload_log.json"
CROSSPOST_LOG_PATH = STATE_DIR / "uploadpost_log.json"


# ============================================================
# AUTHENTICATION
# ============================================================

def authenticate():
    """Load cached token or prompt for OAuth consent. Returns YouTube API client."""
    creds = None

    if os.path.exists(TOKEN_FILE_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE_PATH, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_PATH, SCOPES)
            creds = flow.run_local_server(port=0)

        # Save the token for next time
        os.makedirs(os.path.dirname(TOKEN_FILE_PATH), exist_ok=True)
        with open(TOKEN_FILE_PATH, "w") as token_file:
            token_file.write(creds.to_json())

    return build("youtube", "v3", credentials=creds)


def verify_channel(youtube):
    """Confirm the authenticated user owns the EXPECTED_CHANNEL_ID. Hard exit if not."""
    response = youtube.channels().list(part="snippet", mine=True).execute()
    if not response.get("items"):
        print("ERROR: No channels found for this account.")
        sys.exit(1)

    channel = response["items"][0]
    channel_id = channel["id"]
    channel_title = channel["snippet"]["title"]

    if channel_id != EXPECTED_CHANNEL_ID:
        print(f"ERROR: Wrong channel!")
        print(f"  Authenticated as: {channel_title} ({channel_id})")
        print(f"  Expected:         {EXPECTED_CHANNEL_ID}")
        print(f"  Fix: delete {TOKEN_FILE_PATH} and re-run, picking the correct brand account.")
        sys.exit(1)

    print(f"Authenticated as channel: {channel_title}")
    print(f"Channel verification: ✓ Match")
    return channel_id


# ============================================================
# SPREADSHEET HANDLING
# ============================================================

# Column indices (0-based)
COL_VIDEO_NUM = 0
COL_SOURCE_FILE = 1
COL_HOOK_TEXT = 2
COL_OUTPUT_FILE = 3
COL_TITLE = 4
COL_DESCRIPTION = 5
COL_TAGS = 6
COL_TIKTOK_CAPTION = 7
COL_IG_CAPTION = 8
COL_MADE_FOR_KIDS = 9
COL_STATUS = 10
COL_NOTES = 11
COL_SCHEDULE_DATE = 12

SHEET_NAME = "Ready to Upload"


def read_spreadsheet():
    """Load the spreadsheet, return (workbook, worksheet, pending_rows)."""
    wb = load_workbook(SPREADSHEET_PATH)

    if SHEET_NAME not in wb.sheetnames:
        print(f"ERROR: Sheet '{SHEET_NAME}' not found in {SPREADSHEET_PATH}")
        print(f"  Available sheets: {wb.sheetnames}")
        sys.exit(1)

    ws = wb[SHEET_NAME]
    pending = []

    for row_idx in range(2, ws.max_row + 1):  # skip header row
        row = [ws.cell(row=row_idx, column=c+1).value for c in range(13)]
        status = (row[COL_STATUS] or "").strip()
        if status.lower() == "pending":
            pending.append((row_idx, row))

    return wb, ws, pending


def validate_files(pending_rows):
    """Check that every pending row's Output File exists in VIDEOS_FOLDER."""
    available = set(os.listdir(VIDEOS_FOLDER))
    valid, missing = [], []

    for row_idx, row in pending_rows:
        filename = (row[COL_OUTPUT_FILE] or "").strip()
        if not filename:
            missing.append((row_idx, "(empty Output File)"))
        elif filename not in available:
            missing.append((row_idx, filename))
        else:
            valid.append((row_idx, row))

    if missing:
        print(f"\nWarning: {len(missing)} row(s) have missing files (will be skipped):")
        for row_idx, filename in missing:
            print(f"  Row {row_idx}: {filename}")

    return valid


# ============================================================
# SCHEDULING
# ============================================================

def find_last_scheduled_date(youtube):
    """Query YouTube directly for the latest scheduled upload's publishAt time."""
    try:
        # Get the channel's uploads playlist
        channels = youtube.channels().list(part="contentDetails", mine=True).execute()
        uploads_playlist = channels["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]

        # Get recent uploads (paginated)
        latest_publishat = None
        next_page = None
        scanned = 0

        while scanned < 200:  # cap at 200 most-recent
            playlist_response = youtube.playlistItems().list(
                part="contentDetails",
                playlistId=uploads_playlist,
                maxResults=50,
                pageToken=next_page
            ).execute()

            video_ids = [item["contentDetails"]["videoId"] for item in playlist_response.get("items", [])]
            scanned += len(video_ids)
            if not video_ids:
                break

            videos_response = youtube.videos().list(part="status", id=",".join(video_ids)).execute()
            for v in videos_response.get("items", []):
                status = v.get("status", {})
                publish_at = status.get("publishAt")
                if publish_at and status.get("privacyStatus") == "private":
                    dt = datetime.fromisoformat(publish_at.replace("Z", "+00:00"))
                    dt_pt = dt.astimezone(ZoneInfo(TIMEZONE))
                    if latest_publishat is None or dt_pt > latest_publishat:
                        latest_publishat = dt_pt

            next_page = playlist_response.get("nextPageToken")
            if not next_page:
                break

        return latest_publishat

    except HttpError as e:
        print(f"Warning: could not query YouTube for latest scheduled video ({e})")
        return None


def find_last_in_log():
    """Read the latest scheduled date from upload_log.json (fallback)."""
    if not UPLOAD_LOG_PATH.exists():
        return None
    try:
        with open(UPLOAD_LOG_PATH) as f:
            log = json.load(f)
        if not log:
            return None
        timestamps = [datetime.fromisoformat(e["scheduled"]) for e in log if "scheduled" in e]
        return max(timestamps) if timestamps else None
    except (json.JSONDecodeError, ValueError, KeyError):
        return None


def generate_publish_dates(count, youtube):
    """
    Generate `count` future publish slots, starting strictly after the latest
    already-scheduled video.

    Source of truth: max(YouTube reality, local log). YouTube wins ties.
    """
    yt_latest = find_last_scheduled_date(youtube)
    log_latest = find_last_in_log()
    if log_latest:
        log_latest = log_latest.replace(tzinfo=ZoneInfo(TIMEZONE)) if log_latest.tzinfo is None else log_latest

    candidates = [d for d in (yt_latest, log_latest) if d is not None]
    last_scheduled = max(candidates) if candidates else None

    now = datetime.now(ZoneInfo(TIMEZONE))
    cursor = max(last_scheduled, now) if last_scheduled else now

    # Generate slots strictly after `cursor`
    dates = []
    day = cursor.date()
    while len(dates) < count:
        for hour in PUBLISH_HOURS:
            slot = datetime.combine(day, datetime.min.time(), tzinfo=ZoneInfo(TIMEZONE)).replace(hour=hour)
            if day.weekday() in PUBLISH_DAYS and slot > cursor:
                dates.append(slot)
                if len(dates) == count:
                    break
        day += timedelta(days=1)

    return dates


# ============================================================
# UPLOAD
# ============================================================

def upload_video(youtube, file_path, title, description, tags, publish_at):
    """Upload a single video to YouTube with scheduled publish. Returns video_id."""
    body = {
        "snippet": {
            "title": title[:100],
            "description": description,
            "tags": tags,
            "categoryId": str(CATEGORY_ID),
            "defaultLanguage": "en",
        },
        "status": {
            "privacyStatus": "private",
            "publishAt": publish_at.astimezone(ZoneInfo("UTC")).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "selfDeclaredMadeForKids": MADE_FOR_KIDS,
        },
    }

    media = MediaFileUpload(file_path, chunksize=10 * 1024 * 1024, resumable=True)
    request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)

    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"    Upload progress: {int(status.progress() * 100)}%")

    return response["id"]


def crosspost(file_path, tiktok_caption, ig_caption, scheduled_for):
    """Cross-post the video to TikTok and Instagram via Upload Post API."""
    if not CROSSPOST_ENABLED:
        return

    payload = {
        "api_key": UPLOAD_POST_API_KEY,
        "profile": UPLOAD_POST_PROFILE,
        "platforms": ["tiktok", "instagram"],
        "caption_tiktok": tiktok_caption or "",
        "caption_instagram": ig_caption or "",
    }

    try:
        with open(file_path, "rb") as f:
            files = {"video": f}
            response = requests.post(UPLOAD_POST_API_URL, data=payload, files=files, timeout=120)

        log_entry = {
            "file": os.path.basename(file_path),
            "scheduled": scheduled_for.isoformat(),
            "status_code": response.status_code,
            "response": response.text[:500],
        }
    except Exception as e:
        log_entry = {
            "file": os.path.basename(file_path),
            "scheduled": scheduled_for.isoformat(),
            "error": str(e),
        }

    # Append to log
    STATE_DIR.mkdir(exist_ok=True)
    log = []
    if CROSSPOST_LOG_PATH.exists():
        try:
            log = json.loads(CROSSPOST_LOG_PATH.read_text())
        except json.JSONDecodeError:
            log = []
    log.append(log_entry)
    CROSSPOST_LOG_PATH.write_text(json.dumps(log, indent=2))


# ============================================================
# MAIN
# ============================================================

def main():
    parser = argparse.ArgumentParser(description="YouTube automation pipeline")
    parser.add_argument("count", nargs="?", default=6, type=int, help="Number of videos to upload (default: 6)")
    parser.add_argument("--check", action="store_true", help="Verify spreadsheet, don't upload")
    args = parser.parse_args()

    print("=" * 60)
    print("YouTube Automation Pipeline")
    print("=" * 60)

    # 1. Authenticate
    print("\n[1/5] Authenticating...")
    youtube = authenticate()
    verify_channel(youtube)

    # 2. Read spreadsheet
    print(f"\n[2/5] Reading {SPREADSHEET_PATH}...")
    wb, ws, pending = read_spreadsheet()
    print(f"      Found {len(pending)} pending row(s)")

    if not pending:
        print("Nothing to upload. Exiting.")
        return

    # 3. Validate files exist
    print(f"\n[3/5] Validating files in {VIDEOS_FOLDER}...")
    valid = validate_files(pending)
    to_upload = valid[:args.count]
    print(f"      Will upload: {len(to_upload)} video(s)")

    if args.check:
        print("\n--check mode: stopping before upload.")
        return

    if not to_upload:
        print("No valid pending uploads. Exiting.")
        return

    # 4. Compute schedule
    print("\n[4/5] Computing publish schedule...")
    publish_dates = generate_publish_dates(len(to_upload), youtube)
    for i, dt in enumerate(publish_dates):
        print(f"      Slot {i+1}: {dt.strftime('%Y-%m-%d %H:%M %Z')}")

    # 5. Upload each video
    print(f"\n[5/5] Uploading {len(to_upload)} videos...")
    STATE_DIR.mkdir(exist_ok=True)

    success_count = 0
    for i, ((row_idx, row), publish_dt) in enumerate(zip(to_upload, publish_dates)):
        filename = row[COL_OUTPUT_FILE].strip()
        title = row[COL_TITLE] or filename
        description = row[COL_DESCRIPTION] or ""
        tags = [t.strip() for t in (row[COL_TAGS] or "").split(",") if t.strip()]
        tiktok = row[COL_TIKTOK_CAPTION] or ""
        ig = row[COL_IG_CAPTION] or ""

        file_path = os.path.join(VIDEOS_FOLDER, filename)
        print(f"\n  [{i+1}/{len(to_upload)}] {filename}")
        print(f"        Title: {title[:60]}")
        print(f"        Scheduled: {publish_dt.strftime('%Y-%m-%d %H:%M %Z')}")

        try:
            video_id = upload_video(youtube, file_path, title, description, tags, publish_dt)
            video_url = f"https://youtu.be/{video_id}"
            print(f"        ✓ Uploaded: {video_url}")

            # Update spreadsheet
            ws.cell(row=row_idx, column=COL_STATUS+1, value="Uploaded")
            ws.cell(row=row_idx, column=COL_NOTES+1, value=video_url)
            ws.cell(row=row_idx, column=COL_SCHEDULE_DATE+1, value=publish_dt.strftime("%Y-%m-%d %H:%M:%S"))
            wb.save(SPREADSHEET_PATH)

            # Append to upload log
            log = []
            if UPLOAD_LOG_PATH.exists():
                try:
                    log = json.loads(UPLOAD_LOG_PATH.read_text())
                except json.JSONDecodeError:
                    log = []
            log.append({
                "num": row[COL_VIDEO_NUM],
                "file": filename,
                "video_id": video_id,
                "video_url": video_url,
                "scheduled": publish_dt.isoformat(),
                "uploaded_at": datetime.now(ZoneInfo(TIMEZONE)).isoformat(),
            })
            UPLOAD_LOG_PATH.write_text(json.dumps(log, indent=2))

            # Cross-post if enabled
            if CROSSPOST_ENABLED and (tiktok or ig):
                print(f"        Cross-posting to TikTok + Instagram...")
                crosspost(file_path, tiktok, ig, publish_dt)

            success_count += 1

        except HttpError as e:
            error_msg = str(e)
            if "quotaExceeded" in error_msg:
                print(f"        ✗ Quota exceeded. Stopping batch.")
                break
            else:
                print(f"        ✗ Upload failed: {error_msg[:200]}")
                ws.cell(row=row_idx, column=COL_STATUS+1, value="Failed")
                wb.save(SPREADSHEET_PATH)

    print("\n" + "=" * 60)
    print(f"UPLOAD COMPLETE: {success_count}/{len(to_upload)} succeeded")
    print("=" * 60)


if __name__ == "__main__":
    main()

# START HERE — Claude Code YouTube Automation Pipeline

> **For Claude (the assistant reading this file):** This is a step-by-step runbook for helping a user build their own automated YouTube upload pipeline. Follow it linearly. Always pause and ask the user to confirm before moving to the next section. Never run commands or generate code without explaining what they do first. The user may be technical or non-technical — adapt your tone.

> **For the user:** You don't need to read this file end-to-end. Just tell Claude:
> > *"Read START_HERE.md and walk me through setting this up step by step."*
>
> Claude will take it from there.

---

## Project Briefing

**The goal:** Build a Python pipeline that takes a folder of video files and a spreadsheet of metadata, uploads them to a YouTube channel on a schedule, and (optionally) cross-posts to TikTok and Instagram. Run it daily with one command. Scale to 50+ videos a day.

**The architecture:**

```
Video files → Spreadsheet (the brain) → Python script → YouTube API
                                                      → Upload Post API → TikTok + Instagram
```

The user already has the kit downloaded (you're reading it now). Your job is to walk them through:
1. Path selection (Cowork or Claude Code)
2. Prerequisites check
3. Google Cloud + OAuth setup
4. Code customization (filling placeholders in `pipeline_template.py`)
5. Spreadsheet setup
6. Test upload
7. First production batch
8. What's next

Each section ends with a checkpoint where you confirm with the user before continuing.

---

## Section 1 — Path Selection

Ask the user:

> *"Are you using Cowork (the desktop app) or Claude Code (the CLI tool)?"*

If they don't know what either is, explain:
- **Cowork** is Anthropic's desktop app — drop a folder in, chat with Claude. Familiar chat interface. Best for non-technical users.
- **Claude Code** is Anthropic's command-line tool. Install with `npm install -g @anthropic-ai/claude-code`. More technical, but works anywhere.

Both paths build the same pipeline. The end result is identical.

Store the answer as `[USER_PATH]`. All commands and instructions in this runbook will branch on this value.

If unsure, recommend **Cowork** for non-technical users and **Claude Code** for terminal-comfortable users.

**Checkpoint:** Confirm `[USER_PATH]` before moving to Section 2.

---

## Section 2 — Prerequisites Check

Ask the user about each of these one at a time. If anything is missing, pause and give clear instructions to acquire it BEFORE proceeding.

### Required for everyone:

1. **YouTube channel they own** with a Channel ID.
   How to find it: YouTube Studio → Settings → Channel → Advanced settings → Channel ID. It looks like `UCxxxxxxxxxxxxxxxxxxxxxx` (24 characters starting with UC).
   Store as `[CHANNEL_ID]`.

2. **Google account that owns the channel.**
   This is what you'll authorize for OAuth. Note: if the channel is a Brand Account, the Google login UI will ask which account to act as — they must pick the brand account, not the personal one.

3. **At least 5-10 video files ready to upload.**
   Sora outputs, AI clips, recorded shorts — anything in MP4. If they have zero videos, pause and tell them to come back when they have at least 5.

4. **Google Cloud account (free).**
   If missing: send them to [console.cloud.google.com](https://console.cloud.google.com) to sign up. New users get a free trial.

5. **Python 3.10 or newer.**
   On Windows: open PowerShell, run `python --version`.
   On macOS: open Terminal, run `python3 --version`.
   If missing: [python.org/downloads](https://www.python.org/downloads/).

### Required for cross-posting (optional):

6. **Upload Post account** at [upload-post.com](https://upload-post.com). Free tier works.
7. **TikTok account** (Creator account preferred — Personal works but limited).
8. **Instagram Business or Creator account** linked to a Facebook Page. Personal IG accounts cannot be cross-posted via API.

If skipping cross-posting, note `[CROSSPOST_ENABLED] = false` and tell the user the pipeline will only upload to YouTube. They can add cross-posting later.

### For Claude Code path only:

9. **Terminal application.** Default Terminal on Mac, PowerShell on Windows.
10. **Claude Code installed and authenticated.** Verify with `claude --version`.

### For Cowork path only:

11. **Cowork desktop app installed and signed in.**
12. **A Cowork project pointed at this kit folder** (the user has likely already done this if they're reading this runbook).

Store the answers:
- `[CHANNEL_ID]` = the user's YouTube Channel ID
- `[USER_PATH]` = "cowork" or "claude_code"
- `[CROSSPOST_ENABLED]` = true or false
- `[OS]` = "windows" or "macos" or "linux"
- `[PYTHON_CMD]` = "python" on Windows, "python3" on Mac/Linux

Once everything is verified, say:

> *"All prerequisites confirmed. Next, we'll set up Google Cloud and OAuth credentials. This is the gnarliest part of the whole build — about 15-20 minutes — but I'll walk you through every click. Ready to start?"*

**Checkpoint:** Wait for confirmation before proceeding to Section 3.

---

## Section 3 — Google Cloud + OAuth Setup

This is the hardest part. Be patient. Walk them through one click at a time. Use exact button names.

### 3.1 Create a Google Cloud project

Tell the user:

1. Open [console.cloud.google.com](https://console.cloud.google.com) in a browser.
2. At the top of the page, click the **project picker** (says "Select a project" or shows the current project name).
3. In the popup, click **"New Project"** in the top right.
4. Project name: any name they want, e.g. `youtube-uploader`. Leave the org/location at default.
5. Click **"Create"**.
6. Wait 10-30 seconds. Once created, click the **project picker** again and select the new project.

**Verify:** The project name should appear in the top bar of the Cloud Console.

### 3.2 Enable the YouTube Data API v3

1. In the search bar at the top, type **"YouTube Data API v3"** and select it from results.
2. Click **"Enable"**.
3. Wait for it to enable (~10 seconds).

If they're cross-posting, they don't need to enable any other APIs — Upload Post handles its own auth.

### 3.3 Configure OAuth consent screen

1. In the left sidebar, navigate to **APIs & Services → OAuth consent screen**.
2. Choose **"External"** (unless they have a Google Workspace organization). Click **Create**.
3. **App name:** anything they want (e.g. "My YouTube Uploader"). Doesn't appear publicly.
4. **User support email:** their own email.
5. **Developer contact email:** same.
6. Skip "App domain", "Authorized domains" — leave blank.
7. Click **"Save and Continue"** to advance through Scopes (skip — leave default), Test Users (skip — they'll add themselves later), and Summary.
8. Back at the OAuth consent screen page, click **"Publish App"** (button changes from "Testing" to "In Production"). Confirm if asked.

**Why publish:** keeps the OAuth token from expiring every 7 days.

### 3.4 Create OAuth Client credentials

1. Left sidebar → **APIs & Services → Credentials**.
2. Click **"+ Create Credentials"** at the top → **"OAuth client ID"**.
3. **Application type:** Desktop app.
4. **Name:** anything (e.g. "youtube-uploader-desktop").
5. Click **"Create"**.
6. A popup shows the client ID and client secret. Click **"Download JSON"** (top of popup, looks like a download icon).
7. Save the file somewhere safe — preferably **outside the project folder** (e.g. `~/Documents/secrets/` on Mac or `C:\Users\YourName\secrets\` on Windows). Rename it to something simple like `client_secret.json`.

**Critical:** This file is a secret. NEVER put it in the project folder if the project is on GitHub. NEVER commit it. NEVER share it.

Tell the user the path where they saved the file. Store as `[CLIENT_SECRET_PATH]`.

**Checkpoint:** Confirm they have the `client_secret.json` file saved and the path noted before moving to Section 4.

---

## Section 4 — Code Customization

Now we customize `pipeline_template.py` for their channel.

### 4.1 Open the template

Tell the user to open `pipeline_template.py` in their editor (or in Cowork if they're using that path). You'll be filling in the values they captured in Sections 2-3.

### 4.2 Replace the placeholders

The template has placeholders in `[BRACKETS]` format. Walk through each one with the user. The required edits are:

| Placeholder | Replace with | Source |
|---|---|---|
| `[CHANNEL_ID]` | Their actual Channel ID (from Section 2) | YouTube Studio |
| `[CLIENT_SECRET_PATH]` | Full path to their `client_secret.json` | Section 3.4 |
| `[TOKEN_FILE_PATH]` | Where to save the OAuth token (suggest same folder as client_secret) | They choose |
| `[VIDEOS_FOLDER]` | Path to the folder where they'll keep videos to upload | They choose |
| `[SPREADSHEET_PATH]` | Path to the upload master spreadsheet | They choose |
| `[CATEGORY_ID]` | YouTube category number (15 = Pets, 24 = Entertainment, 22 = People & Blogs, 27 = Education) | Their channel content |
| `[PUBLISH_HOURS]` | List of hours per day to publish (e.g. `[10, 17]` for 10 AM and 5 PM) | Their schedule preference |
| `[TIMEZONE]` | Their timezone (e.g. `America/Los_Angeles`) | Their location |
| `[MADE_FOR_KIDS]` | `True` or `False` | Their content audience |

If `[CROSSPOST_ENABLED] = true`, also fill in:

| Placeholder | Replace with |
|---|---|
| `[UPLOAD_POST_API_KEY]` | API key from upload-post.com dashboard |
| `[UPLOAD_POST_PROFILE]` | Profile name they configured at Upload Post |

For each placeholder, you can offer to make the edit yourself (since you have file write access). Show the user the change before saving so they can verify.

### 4.3 Save the customized script

Save the file as `upload.py` (or any name they prefer) in their project folder.

**Checkpoint:** Confirm all placeholders are filled in and the file is saved.

---

## Section 5 — Spreadsheet Setup

### 5.1 Open the template

Tell the user to open `upload_master_TEMPLATE.xlsx` in Excel (or Google Sheets, or LibreOffice).

### 5.2 The columns

Walk through the column structure:

| Column | What It's For |
|---|---|
| **A — Video #** | Sequential number (1, 2, 3...). Just for sorting. |
| **B — Source File** | Original filename (provenance only — script doesn't read this). |
| **C — Hook Text** | The on-screen text they'll burn into their edited video. |
| **D — Output File** | The exact filename of the edited `.mp4` in their videos folder. **This must match the file on disk.** |
| **E — Title** | YouTube title (≤100 chars). |
| **F — Description** | Full YouTube description. |
| **G — Tags** | Comma-separated keywords. |
| **H — TikTok Caption** | Short caption for TikTok cross-post. Skip if not cross-posting. |
| **I — IG Caption** | Caption for Instagram. Skip if not cross-posting. |
| **J — Made for Kids** | Should match `[MADE_FOR_KIDS]` from Section 4. |
| **K — Status** | Set to `Pending` for new rows. The script writes `Uploaded` after success. |
| **L — Notes** | Free-form. Use `REVIEW BEFORE UPLOAD` to flag rows that need attention. |
| **M — Schedule Date** | The script fills this in after upload. Leave blank for new rows. |

### 5.3 First test row

Have the user add ONE row for a test:
- Video #: 1
- Output File: the filename of one of their video files (case-sensitive)
- Title: anything (we'll just verify upload works — it'll be private)
- Description: anything
- Tags: any 2-3 words
- Status: `Pending`
- Made for Kids: matches their setting

Save the spreadsheet at the path they set as `[SPREADSHEET_PATH]` in Section 4.

**Checkpoint:** One test row added and saved.

---

## Section 6 — First Test Upload

### 6.1 Run the test

Tell the user to open their terminal/PowerShell and navigate to the project folder. Then run:

```
[PYTHON_CMD] upload.py 1
```

(Where `[PYTHON_CMD]` is `python` on Windows or `python3` on Mac.)

### 6.2 What to expect

**First run only:** A browser window will open for OAuth consent. The user must:
1. Choose the Google account that owns the YouTube channel
2. If the channel is a Brand Account, pick the brand identity (not personal)
3. Click "Allow"
4. Browser shows a success page

The token is then saved to `[TOKEN_FILE_PATH]` and won't need to be redone.

**Then in the terminal:** They should see:
- "Authenticated as channel: [their channel name]"
- "Channel verification: ✓ Match"
- "Reading spreadsheet..."
- "Found 1 pending row"
- "Uploading [filename]..."
- "Upload complete: [video URL]"

### 6.3 Verify

Have them open YouTube Studio and check the Content tab. The test video should appear with:
- Privacy: Private (or Scheduled if `publishAt` was set)
- Title: matches what they entered
- Status: scheduled to publish at the next slot in `[PUBLISH_HOURS]`

### 6.4 Common errors and fixes

If the test fails, here are the most likely causes:

| Error | Fix |
|---|---|
| `Wrong channel ID` | The OAuth flow authorized the wrong channel. Delete the token file, re-run, pick the brand account this time. |
| `File not found` | Column D in the spreadsheet doesn't match the actual filename. Check case sensitivity and spaces. |
| `Quota exceeded` | Their Google Cloud project hit its daily quota. Wait 24 hours OR check if they need to enable the YouTube Data API. |
| `Invalid client secret` | The path in `[CLIENT_SECRET_PATH]` is wrong. Verify the file exists at that path. |
| `Browser won't open` | Run with `--no-browser` flag and copy the URL manually. |

**Checkpoint:** Test upload succeeds and shows in YouTube Studio.

---

## Section 7 — First Production Batch

Once the test succeeds, the user is production-ready.

### 7.1 Add real rows to the spreadsheet

Have them fill out 5-10 more rows in the spreadsheet with their actual content.

### 7.2 Run the batch

```
[PYTHON_CMD] upload.py 6
```

(The number is how many videos to upload. Default 6 if omitted.)

The script will:
1. Authenticate (silent — uses cached token)
2. Verify channel
3. Read spreadsheet, find pending rows
4. Determine the next available scheduling slot
5. Upload each video, scheduling at 2x daily slots (or whatever they set in `[PUBLISH_HOURS]`)
6. Cross-post to TikTok + IG (if enabled)
7. Update the spreadsheet with status + scheduled date
8. Log everything to `state/upload_log.json`

### 7.3 Verify the schedule

In YouTube Studio → Content, they should see the new videos as Scheduled with publish times.

**Checkpoint:** First production batch lives in YouTube Studio with correct scheduled times.

---

## Section 8 — Daily Operating Rhythm

Tell the user the daily flow from this point on:

1. **Generate or record new content** when inspired (Sora, recordings, etc.)
2. **Drop the files** in their videos folder
3. **Add rows** to the spreadsheet (or have Claude help with metadata)
4. **Run the script** once a day:
   ```
   [PYTHON_CMD] upload.py 6
   ```
5. **YouTube auto-publishes** at the scheduled times. No further action needed.

Total time per day after setup: about 2 minutes.

---

## Section 9 — Common Issues After Going Live

If the user comes back later with problems, here's a quick reference.

### "Schedule has gaps / collisions / starts in the past"

Run the script with the `--start-date YYYY-MM-DD` flag to force a starting date. Or run a `verify_schedule.py` script (not included in v1.0 — Claude can write one if needed) to audit the current schedule.

### "OAuth keeps asking me to re-authorize"

Either the OAuth consent screen wasn't published (Section 3.3 step 8), or the token file got deleted. Re-run and verify the consent screen status in Cloud Console.

### "I want to add a third channel"

Two options:
1. Same Google Cloud project: just generate a new OAuth token for the new channel. They'll share the same daily API quota.
2. Separate Cloud project: create a new project, repeat Section 3, get a new client_secret.json. Better isolation.

### "Cross-posts aren't going through"

Check `state/uploadpost_log.json` for the response from Upload Post. Most common cause: the Upload Post profile got disconnected (TikTok or IG re-auth needed).

### "I want to clear the queue / reset the schedule"

Manually reschedule via YouTube Studio (drag videos to new times) OR have Claude write a `reschedule.py` helper that does it via API.

---

## Section 10 — What's Next

Once the user is live and running, point them to:

- **Part 2 of the CryptoClaud series** — adds Claude-powered metadata generation (auto-write titles, descriptions, tags from a Sora prompt)
- **Part 3** — OAuth deep-dive and Brand Account gotchas
- **Part 4** — Scaling to 50+ uploads/day
- **Part 5** — Cross-posting deep-dive (Upload Post API, TikTok auth)
- **Part 6** — VidIQ-driven metadata optimization

The full series is on [@CryptoClaud](https://www.youtube.com/@CryptoClaud) — subscribe to get notified when new parts drop.

Final message to the user:

> *"You're set. The pipeline is running. Daily uploads happen on autopilot. If you hit any issues, ask me to debug — I have the runbook context. Good luck building."*

---

## Notes for Claude (the assistant)

A few patterns that keep this experience smooth:

1. **One section at a time.** Never rush the user through multiple sections in one go. They'll lose context.

2. **Confirm before destructive actions.** Especially anything that writes files, edits the script, or touches their Google Cloud project.

3. **Show work before committing.** When filling placeholders, show the diff or the proposed edit before saving.

4. **If they get stuck, slow down.** Re-explain in different words. Show them screenshots-as-text descriptions of what they should see.

5. **Encourage testing.** Always recommend the test upload (1 video) before production batches.

6. **Acknowledge the milestones.** When the test upload succeeds, that's a real win for them. Acknowledge it.

7. **If they ask to modify the script beyond what this runbook covers** (e.g. adding a new feature, changing the publishing logic), help them — but warn them they're going off the runbook and the pipeline behavior may diverge from the documented version.

8. **End every section with a checkpoint.** "Confirm X before continuing to Y."

---

## Final Note for the User

This kit is v1.0 — built around what works for one creator's pipeline. As the channel evolves, expect updates: better metadata generation, more cross-post platforms, new cadence options.

Star the repo on GitHub if it helped you. Open an issue if something's broken.

Built with Claude. Documented for humans.

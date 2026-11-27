# Daily production run

A scheduled task starts a fresh session every morning (about 09:45 Amsterdam time). That session
follows this runbook. **Deadline: the video is uploaded to YouTube as private by 17:00 Amsterdam
time**, so the owner can review it and make it public at 19:00.

The owner decided on 2026-11-27:
- one new 20-minute video every day;
- no script approval in advance: the owner approves by watching the private upload in Studio;
- Claude uploads as private only. Never public, unlisted or scheduled.

Read `CLAUDE.md`, `.claude/youtube/ceo-brief.md` and `.claude/youtube/voice.md` first.
Work on branch `claude/inspiring-tesla-iif0hl`, and commit and push after every step so a crashed
session can resume.

## 0. Check (5 min)
- `TZ=Europe/Amsterdam date`. If the previous run left a half-finished video (see
  `channel/pipeline.md`), finish that one first instead of starting a new case.
- `vidiq_balance`. One video costs about 420 credits (voiceover ~390, music ~25).
  **If there are not enough credits, do NOT start the voiceover.** Do steps 1-3, plus image
  prefetch, then stop and report "credits op" with the balance and reset date. Never buy credits
  or use a paid service; that is the owner's call.

## 1. Pick the case (15 min)
- Take the top "Next up" case from `channel/pipeline.md`, otherwise the highest-priority case on the
  current shortlist (`channel/shortlist-*.md`) that is not yet produced.
- When fewer than 3 shortlisted cases remain, or on Mondays, write a new weekly shortlist
  (format: `channel/shortlist-2026-11.md`) and add the cases to the case log.

## 2. Research (60 min) → `videos/<slug>/research.md`
- Sources: Wikipedia via `https://en.wikipedia.org/w/index.php?title=<Title>&action=raw` (the API
  rate-limits), plus Old Bailey Proceedings, National Archives and other reliable sources
  reachable from here. Every fact sourced, contested points marked ⚠, as in `videos/crippen/research.md`.

## 3. Script (45 min) → `script.md` and `beats.json`
- About 3,000 words, 50-60 beats, each with `[ON SCREEN: ...]`. Structure and voice as in
  `voice.md`. Run the `yt-script` hook scorer on 5 hooks and keep the best.
- `beats.json`: `[{"id": "01", "screen": "...", "text": "narration"}]`, as in `videos/crippen/`.

## 4. Images (start early; runs in the background)
- Find public-domain or CC images on Wikimedia Commons. Download with `tools/commons_get.py`
  (it honours 429 Retry-After; Commons allows only about one file per 20 minutes from here).
  Start this the moment the case is chosen. Anything still missing at render time falls back to
  cards, maps and images that did arrive.
- **Prefetch:** at the end of the run, start downloads for tomorrow's case so they are there
  in the morning.
- Cards with `tools/cards.py` (title, text, quote, telegram); maps with `tools/maps.py`
  (needs `pip install basemap basemap-data-hires` in a venv).
- Never AI images of real victims or perpetrators. Check every image visually before using it.

## 5. Audio (20 min) → `audio.json`
- `vidiq_voiceover_generate`, voice Daniel `onwK4e9ZLuTAKqWW03F9`, using `scriptLines` (one line per
  beat) so the result has per-line start times. Split into two parts as for Crippen if needed.
- `vidiq_generate_music`: low, sombre instrumental bed. Poll with `vidiq_job_poll`.
- Download the files to `videos/<slug>/assets/audio/`.

## 6. Edit and render (40 min)
- `edit.json` (beats with visual, motion, caption, pause_before 1.4 at act changes, fallback;
  `music_db` -23; `chapters`), as in `videos/crippen/edit.json`.
- `python3 tools/render.py videos/<slug>`, then `python3 tools/finalize_metadata.py videos/<slug>`.
- QA: duration, 1080p, loudness about -14 LUFS, look at sampled frames.

## 7. Package → `metadata.md` and `out/thumbnail.jpg`
- 3 titles and 3 thumbnail concepts (scored with `yt-package`'s `title.py`), the winner used.
- Thumbnail with `tools/thumbnail.py` from an archive photo.
- Description, chapters, sources, image credits, tags, pinned comment.

## 8. Upload as private (by 17:00)
- `vidiq_video_upload` with `localFile` (run the command it returns), then the thumbnail via
  `vidiq_upload_image` (a public raw GitHub URL of the pushed thumbnail works; mcp.vidiq.com is
  blocked here), then `vidiq_social_post_draft_create` with `privacyStatus: "private"`,
  `categoryId: 27`, then `vidiq_social_post_publish`, then `vidiq_social_post_status` until it is
  completed.
- Push `out/captions.srt` and the thumbnail to `deliveries/<slug>/` so the owner can add the captions.

## 9. Report
Update `channel/pipeline.md` and end with a short report in Dutch:
- the YouTube link;
- the title and the case;
- the owner's tasks in Studio: AI disclosure **Yes**, not made for kids, upload the captions,
  make it public at 19:00;
- the credits left;
- anything that went wrong or is uncertain;
- tomorrow's case.

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
- **vidIQ is used for the upload only** (owner's decision, 2026-11-27). Topic research, script,
  packaging and SEO use the repo skills (`yt-viral`, `yt-script`, `yt-package`, `yt-seo`); voice
  and music are made locally for free. Do not call other vidIQ tools.
- Set up the tools: `bash tools/setup.sh` (venv at `~/kvenv` with Kokoro, yt-dlp, soundfile).
- `TZ=Europe/Amsterdam date`. If the previous run left a half-finished video (see
  `channel/pipeline.md`), finish that one first instead of starting a new case.
- Are the vidIQ tools (`mcp__vidIQ__*`) available (ToolSearch)? Only step 8 needs them. If they are
  missing, do everything up to the render, push, and report that the scheduled task needs the
  vidIQ connector added in claude.ai.

## 1. Pick the case with the most viral potential (30 min, no credits)
The owner wants every video to be the case with the **highest chance of going viral** that day.
Decide on data, not on a fixed order:

1. **Candidates (8-12).** Combine:
   - the unproduced cases in `channel/pipeline.md` and the latest shortlist;
   - **`yt-viral`**: `~/kvenv/bin/python tools/collect_channels.py channel/competitors.txt > /tmp/collected.json`,
     then `python3 .claude/skills/yt-viral/swipe.py /tmp/collected.json --min 2.0`. Which cases and
     angles beat their channel's own median? Name the formula, as the skill says;
   - WebSearch for anniversaries this week, new documentaries, series or news that put an
     old case back in the spotlight, and for search interest in the case name.
2. **Score** each candidate 1-10 on the ten criteria in `.claude/youtube/ceo-brief.md`, with the
   evidence next to each score (outlier multiples, news, competition seen in the swipe file).
   Weight demand, outlier evidence and topicality double. Write it to `channel/selection/<date>.md`.
3. **Pick the highest total** that also passes the hard limits: closed case, strong sources, no
   accusation of anyone not convicted, advertiser-safe enough to monetise, not already Produced.
   Fit with the channel (historical cases, any country) counts as a criterion, not a ban.
4. Add new candidates to the case log so they are not researched twice.

Packaging and scripts also use the repo skills: `/yt-script` (hookscore.py), `/yt-package`
(title.py), `/yt-seo`, `/yt-chapters`.

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
- Voice: `~/kvenv/bin/python tools/voiceover.py videos/<slug> --voice bm_george --speed 0.95`
  (Kokoro, free, runs here). It speaks every beat of `beats.json` and writes
  `assets/audio/vo.wav` and `audio.json` with per-beat start times.
- Music: `~/kvenv/bin/python tools/music.py videos/<slug> --minutes 22 --key D --seed <day>`
  (generated low, sombre pad; vary key and seed per video).
- Listen-check: spot-check a few beats for mispronounced names; fix with phonetic spelling in
  `beats.json` (never in `script.md`) and re-run with `--only <ids>` to test.

## 6. Edit and render (40 min)
- `edit.json` (beats with visual, motion, caption, pause_before 1.4 at act changes, fallback;
  `music_db` -23; `chapters`), as in `videos/crippen/edit.json`.
- `python3 tools/render.py videos/<slug>`, then `python3 tools/finalize_metadata.py videos/<slug>`.
- QA: duration, 1080p, loudness about -14 LUFS, look at sampled frames.

## 7. Package → `metadata.md` and `out/thumbnail.jpg`
- 3 titles and 3 thumbnail concepts (scored with `yt-package`'s `title.py`), the winner used.
- **Thumbnail: always the channel's house style**, the same as the Crippen video (owner's choice,
  reference `videos/crippen/out/thumbnail.jpg`). Make it with
  `python3 tools/thumbnail.py out/thumbnail.jpg <archive photo> "LINE1" "LINE2" --strip "QUOTE..."`:
  - near-black left half; on it two short lines in big cream serif capitals (2-4 words in total);
  - a red bar under the headline;
  - a typewriter-style cream strip with a short quote or fact from the case, ending in "...";
  - on the right, a real archive photo (sepia), fading into the black.
  Never an AI-generated face, painting or "likeness" of a real person, and no red AI-style lettering.
  The thumbnail words must not repeat the title.
- Description, chapters, sources, image credits, tags, pinned comment.

## 8. Upload as private (by 17:00)
- `vidiq_video_upload` with `localFile` (run the command it returns), then the thumbnail via
  `vidiq_upload_image` (a public raw GitHub URL of the pushed thumbnail works; mcp.vidiq.com is
  blocked here), then `vidiq_social_post_draft_create` with `privacyStatus: "private"`,
  `categoryId: 27`, then `vidiq_social_post_publish`, then `vidiq_social_post_status` until it is
  completed.
- Push `out/captions.srt` and the thumbnail to `deliveries/<slug>/` so the owner can add the captions.

## 9. Report
Update `channel/pipeline.md`: mark today's case **Produced** in the case log (with the YouTube
link), and set tomorrow's case as "Next up". Never produce a case that is already marked Produced.
Then end with a short report in Dutch:
- the YouTube link;
- the title and the case;
- the owner's tasks in Studio: AI disclosure **Yes**, not made for kids, upload the captions,
  make it public at 19:00;
- anything that went wrong or is uncertain;
- tomorrow's case.

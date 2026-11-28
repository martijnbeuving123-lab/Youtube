# Daily production run

A scheduled task starts a fresh session every morning (about 09:45 Amsterdam time). That session
follows this runbook. **Deadline: the video is uploaded to YouTube as private by 17:00 Amsterdam
time**. The daily check (`channel/daily-check.md`, ~17:40) then schedules it to go public at
19:00 if it is fully ready (owner's decision, 2026-11-27).

The owner decided on 2026-11-27:
- one new 20-minute video every day;
- no script approval in advance: the owner approves by watching the private upload in Studio;
- Claude uploads as private only. Never public, unlisted or scheduled.

Read `CLAUDE.md`, `.claude/youtube/ceo-brief.md` and `.claude/youtube/voice.md` first.
Work on branch `claude/pensive-cerf-dz4nqf` (the branch the scheduled task names), and commit and push after every step so a crashed
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
- **Primary source first.** For a trial at the Old Bailey up to 1913, fetch the verbatim
  trial account: `python3 tools/oldbailey_get.py --search "<surname> murder" --year <year>`, then
  `python3 tools/oldbailey_get.py videos/<slug> <trial id>` (saves `sources/oldbailey-<id>.txt`).
  Quote witnesses and the judge from it, with the citation. Never put the page scans in the video
  (non-commercial licence).
- Then Wikipedia via `https://en.wikipedia.org/w/index.php?title=<Title>&action=raw`, the
  National Archives catalogue (`https://discovery.nationalarchives.gov.uk/API/search/records?sps.searchQuery=<words>`,
  `Accept: application/json`) for file references, and archive.org search/metadata
  (`archive.org/advancedsearch.php`, `archive.org/metadata/<id>`) to cite books such as the
  *Notable British Trials* volumes. archive.org file downloads do NOT work from here (they
  redirect to storage servers outside the allowlist).
- Every fact sourced, contested points marked ⚠, as in `videos/crippen/research.md`. Say in the
  report which primary sources were used.

## 3. Script (45 min) → `script.md` and `beats.json`
- **Originality:** follow `channel/originality-rules.md` (own angle, analysis passages, an opening
  unlike the last 10 videos, no boilerplate). Owner's decision 2026-11-27.
- About 3,000 words, 50-60 beats, each with `[ON SCREEN: ...]`. Structure and voice as in
  `voice.md`. Run the `yt-script` hook scorer on 5 hooks and keep the best.
- `beats.json`: `[{"id": "01", "screen": "...", "text": "narration"}]`, as in `videos/crippen/`.

## 4. Images (start early, right after the case is chosen)
Wikimedia Commons rate-limits this cloud's shared IP (HTTP 429 on almost every request), so it
can no longer be the main source. Use the sources in this order, and aim for **at least 12 real
archive images** per video:
1. **Wellcome Collection, digitised books** (the richest source; whole public-domain books
   with plates and photographs: police and detective manuals, forensic and medico-legal
   textbooks, trial reports, prison and asylum records, period newspapers):
   - `python3 tools/wellcome_get.py --books "<words>" --before 1935` lists usable works
     (public domain, CC0, CC BY only). Search short terms: the forensic first ("finger prints",
     "Bertillon", "firearms", "poisons", "medical jurisprudence"), "police", "Scotland Yard",
     "criminal", the town, the prison, the newspaper.
   - `python3 tools/wellcome_get.py --sheet <work id> /tmp/sheet.jpg 1-120` makes a numbered
     contact sheet; **look at it** (Read the image) to spot the plates, photos and diagrams.
   - `python3 tools/wellcome_get.py videos/<slug> <name>=<work id>:<page>[:x,y,w,h]` downloads
     a page, cropped to the plate with the percent box (e.g. `:5,15,90,40`). Look at the result.
2. **Wellcome Collection, single images**: `python3 tools/wellcome_get.py --search "<words>"`,
   then `python3 tools/wellcome_get.py videos/<slug> <name>=<image id> ...`. Never CC BY-NC
   (the channel is monetised); the tool refuses it and writes the credit CC BY requires.
3. **Library of Congress** (`tools/loc_get.py --search` / fetch): good for US and some British
   press photos. It also rate-limits at times (429): try again later in the run.
4. **Wikimedia Commons** (`tools/commons_get.py`): blocked for this cloud almost all the time
   (HTTP 429 for every client, Hermoso included). Only a background job for one or two images
   found nowhere else, e.g. the defendant's police photo. Never wait on it.
- **Gate before rendering:** `python3 tools/image_check.py videos/<slug> --min 12`. If it fails,
  search more (other terms, other books) before rendering. Only if three more searches still
  give nothing, render anyway and put the shortfall at the top of the report.
- **When choosing the case (step 1):** do a quick `--books` and `--search` for each of the top
  three candidates. A case with fewer than about 8 findable real images loses points on
  visual potential.
- All tools write to the same `credits.json` / `credits.md`; `finalize_metadata.py` puts the
  used ones in the description.
- **Thumbnail:** the right-hand photo must be a real archive image (from any of these
  sources). Only if none arrived, use a period object or place, never an illustration of a person.
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
- **Originality gate first:** check `channel/originality-rules.md` rules 1–6 and record the result
  in `metadata.md`. Fix before rendering; never skip it for the deadline.
- `edit.json` (beats with visual, motion, caption, pause_before 1.4 at act changes, fallback;
  `music_db` -23; `chapters`), as in `videos/crippen/edit.json`.
- `python3 tools/render.py videos/<slug>`, then `python3 tools/finalize_metadata.py videos/<slug>`.
- QA: duration, 1080p, loudness about -14 LUFS, look at sampled frames.


## 6b. Short for tomorrow 12:00 (owner's decision 2026-11-27; 20 min, never at the cost of the deadline)
Every day one YouTube Short from today's long video, published the next day at **12:00
Amsterdam** (the daily check schedules it). Skip it if the long video is not uploaded yet with
less than 90 minutes to the deadline; the long video always comes first.
1. **Pick** 30-55 s that stand on their own (`/yt-shorts`): a complete opening thought, a turn,
   an ending line that sets up the full video (e.g. "Under the cellar floor...").
2. **Hook:** write 5 on-screen hooks (two lines cream + two lines red, different words from the
   narration), score them with `.claude/skills/yt-script/hookscore.py`, keep the best. If none is
   genuinely gripping in the first second, make no Short today (no Short beats a weak one).
3. **Build** with `python3 tools/short.py videos/<slug>/shorts/short1.json out/short1.mp4`
   (spec format in the tool; example `videos/crippen/shorts/short1.json`): real archive images
   only, full-frame shots that change every 5-10 s, the house fonts and colours.
4. **Check** 6 sampled frames (hook readable, captions inside the frame, no AI faces) and the
   length (under 60 s).
5. **Upload as private** without a publish time, with: title = the hook as a sentence +
   " #Shorts" (under 100 characters); description = one line of context, "Watch the full case:"
   + the long video's link, image credits, "Narration is AI-generated."; category Education;
   made for kids No; AI disclosure Yes where the tool allows it. Record the Short's video id in
   the pipeline as "Short (private, for tomorrow 12:00)".
   Upload route: Precinct Archive: `vidiq_video_upload` + `vidiq_social_post_draft_create` (YouTube, privacyStatus private, no publishAt) + `vidiq_social_post_publish`, as in step 8.

## 7. Package → `metadata.md` and `out/thumbnail.jpg`
- 3 titles and 3 thumbnail concepts (scored with `yt-package`'s `title.py`), the winner used.
- **Thumbnail: always the shared house style of both channels** ("case file" style, owner's
  choice 2026-11-27; reference `channel/style/thumbnail-reference.jpg`, examples in
  `deliveries/*/thumbnail.jpg`). Make it with
  `python3 tools/thumbnail.py <out.jpg> <archive photo> "LINE1" "LINE2" --label "CASE FILE · PLACE, YEAR" [--crop x,y,w,h] [--top <scene>] [--bottom <scene>]`:
  - dark, grainy background; on the left two lines in Playfair Display Black capitals, line one
    cream, line two larger and red (2-4 words in total), with a red rule under them;
  - a cream "case file" label in typewriter capitals: what, where, when;
  - on the right, a large real archive photo (black-and-white / sepia) fading into the dark;
  - optional faded archive scenes top-left / bottom-left (a document, telegram card, map, plate).
  Only real archive images: never an AI-generated face, painting or "likeness" of a real person,
  and no swastikas or other hate symbols large in the thumbnail (advertiser safety). Never change
  the layout, fonts or colours. The thumbnail words must not repeat the title.
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
- whether AI disclosure **Yes**, not made for kids and the captions were set at upload (write
  this in `channel/pipeline.md` too, so the daily check knows); the daily check schedules the
  video for 19:00;
- how many real archive images were used, and from which sources;
- anything that went wrong or is uncertain;
- tomorrow's case.

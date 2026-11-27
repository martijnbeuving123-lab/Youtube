# Daily production run — The Defector Files

A scheduled task starts a fresh session every morning. **Deadline: by 15:00 Amsterdam time the
video is on YouTube as PRIVATE**, uploaded by Claude via Hermoso. The daily check (`channel/daily-check.md`)
then schedules it to go public at 19:00 if it is fully ready (owner's decision, 2026-11-27).

Read `defector-files/README.md` and `defector-files/voice.md` first. Work on branch
`claude/pensive-cerf-dz4nqf`. Commit and push after every step (`git pull --rebase` before every
push: the Precinct Archive run pushes to the same branch, in other folders). Never touch files
outside `defector-files/` except shared tools when a tool bug blocks you.

**Upload via Hermoso only (step 8), always as private. Never vidIQ for this channel. Never make
a video public, unlisted or scheduled, and change nothing else on the live channel.**

## 0. Check (5 min)
- `bash tools/setup.sh` (Kokoro, yt-dlp, soundfile).
- `TZ=Europe/Amsterdam date`. If the previous run left a half-finished video (see
  `defector-files/pipeline.md`), finish that one first.
- Hermoso check (ToolSearch "Hermoso"): `list_connector_accounts` must show YouTube
  `@thedefectorfiles`, and `hermoso_credits` → `posting.left` must be at least 1. If the
  connector is missing, YouTube is not connected, or no posts are left, still make the video,
  deliver it as in the fallback in step 8, and say so at the top of the report.

## 1. Pick the case with the most viral potential (30 min)
1. Candidates (8–12), always including at least two **recent** cases (2015 onwards, see
   README.md; aim for about 1–2 recent videos a week, check the case log for this week's mix):
   unproduced cases in the case log, plus
   `~/kvenv/bin/python tools/collect_channels.py defector-files/competitors.txt > /tmp/collected.json`
   and `python3 .claude/skills/yt-viral/swipe.py /tmp/collected.json --min 2.0` (what beats its
   channel's median, and which formula), plus WebSearch for anniversaries, new books,
   documentaries, declassifications or news that put an old case in the spotlight.
2. **Check images before choosing:** `python3 tools/loc_get.py --search "<case terms>"`, and for
   older or European cases also `python3 tools/wellcome_get.py --books "<terms>"` and
   `--search "<terms>"`. A case needs at least 8 usable full-size images (people, places,
   documents) or it waits.
3. Score 1–10 on: interest, search demand, originality, source quality, story quality, visual
   potential, competition, topicality, advertiser suitability, distinctiveness. Demand, outlier
   evidence and topicality count double. Write `defector-files/selection/<date>.md`.
4. Pick the highest total that passes the hard limits in README.md and is not Produced.
   Add new candidates to the case log.

## 2. Research (60 min) → `defector-files/videos/<slug>/research.md`
- Wikipedia raw (`https://en.wikipedia.org/w/index.php?title=<Title>&action=raw`) as the map,
  then the primary and official sources it cites (FBI, CIA, NSA histories, court records,
  official inquiries). Every fact sourced; contested points marked ⚠.

## 3. Script (45 min) → `script.md` and `beats.json`
- **Originality:** follow `channel/originality-rules.md` (own angle, analysis passages, an opening
  unlike the last 10 videos, no boilerplate). Owner's decision 2026-11-27.
- ~3,000 words, 50–60 beats, each with `[ON SCREEN: ...]`, structure and voice per `voice.md`.
  Score 5 hooks with the `yt-script` scorer and keep the best.
- `beats.json`: `[{"id": "01", "screen": "...", "text": "narration"}]`. Write numbers and dates
  as words where Kokoro might misread them ("June nineteenth, 1953").

## 4. Images (start right after the pick)
- `python3 tools/loc_get.py defector-files/videos/<slug> name=<item id> ...` (writes credits).
- LoC sometimes answers 429: wait a few minutes and try again later in the run, do not give up.
- **Wellcome Collection** as the second source (public domain / CC0 / CC BY only, credits
  written): `python3 tools/wellcome_get.py --search "<words>"` for single images, and
  `--books "<words>" --before 1960` for digitised books and pamphlets (wartime propaganda,
  espionage and codes, police and forensic manuals). Make a contact sheet with
  `--sheet <work id> /tmp/sheet.jpg 1-120`, look at it, then fetch
  `defector-files/videos/<slug> <name>=<work id>:<page>[:x,y,w,h]` (percent crop to the plate).
- Commons via `tools/commons_get.py` only as a background job for one or two images found
  nowhere else; it is blocked (429) for this cloud nearly all the time. Never wait on it.
- **Gate before rendering:** `python3 tools/image_check.py defector-files/videos/<slug> --min 12`.
  If it fails, search more first. Only if three more searches give nothing, render anyway
  and put the shortfall at the top of the report.
- Cards with `tools/cards.py` (title, text, quote, telegram with your own sub line), maps with
  `tools/maps.py`. Look at every image before using it.

## 5. Audio (15 min)
- `~/kvenv/bin/python tools/voiceover.py defector-files/videos/<slug> --voice am_michael --speed 0.95`
- `~/kvenv/bin/python tools/music.py defector-files/videos/<slug> --minutes 22 --key <A-G> --seed <day>`

## 6. Edit and render (30 min)
- **Originality gate first:** check `channel/originality-rules.md` rules 1–6 and record the result
  in `metadata.md`. Fix before rendering; never skip it for the deadline.
- `edit.json` as in `videos/crippen/edit.json` (visual, motion, caption, pause_before, fallback,
  `music_db` -23, `chapters`).
- `python3 tools/render.py defector-files/videos/<slug>`, then
  `python3 tools/finalize_metadata.py defector-files/videos/<slug>` if it fits.
- QA: duration, 1080p, about -14 LUFS, sampled frames.

## 7. Package → `metadata.md` and thumbnail
- 3 titles and 3 thumbnail concepts (`yt-package` title.py), winner used. Thumbnail with
  `tools/thumbnail.py` in the house style; words must not repeat the title.
- `yt-seo`: description (with sources and image credits, and "Narration is AI-generated."),
  chapters, tags, pinned comment.

## 8. Upload as private via Hermoso (by 15:00)
Hermoso refuses files over ~16 MB sent from here, but fetches any size from a public URL. The
repo is public, so the video is staged for a few minutes on branch `upload-staging`:
1. Write `defector-files/deliveries/<slug>/upload.md` (title, description with chapters, tags,
   pinned comment, category Education, AI disclosure Yes, made for kids No, language English)
   and copy `thumbnail.jpg` and `captions.srt` there. Push (record and backup).
2. `python3 tools/hermoso_stage.py push defector-files/videos/<slug>/out/<slug>.mp4`
   (makes an upload copy of at most 95 MB, pushes it, prints the raw URL).
3. Hermoso `upload_file` with `url` = that raw URL → a Hermoso video URL.
4. **At once:** `python3 tools/hermoso_stage.py clear` (empties the branch, so the unpublished
   video is no longer public there). Do this even if step 3 failed.
5. Thumbnail: Hermoso `upload_file` with `getUploadUrl: true`, then
   `curl -T defector-files/deliveries/<slug>/thumbnail.jpg -H "Content-Type: image/jpeg" <uploadUrl>`
   → a Hermoso image URL.
6. `post_to_youtube` with: `videoUrl` (step 3), `title`, `description`, `tags`,
   **`privacy: "private"`**, `categoryId: "27"`, `madeForKids: false`, `aiGenerated: true`,
   `notifySubscribers: false`, `defaultLanguage: "en"`, `defaultAudioLanguage: "en"`,
   `thumbnailUrl` (step 5). Never pass `publishAt`. Note the video id it returns.
7. Captions: `manage_youtube_caption` `action: "upload"`, `videoId`, `language: "en"`,
   `name: "English"`, `text` = the contents of `captions.srt`.
8. Check: `list_youtube_videos` shows the video with privacy **private**. If it is not private,
   stop and put that at the top of the report.
9. Save the YouTube link in `upload.md` and push.

Fallback (Hermoso missing, no posts left, or an error you cannot fix): send the MP4 with
SendUserFile (status `proactive`, display `attach`) and say in the report that the owner must
upload it with `upload.md`.

## 9. Report (Dutch, short)
Update `defector-files/pipeline.md` (case → Produced, tomorrow's case → Next up). Then report:
the YouTube link (private), the title and case, that the daily check will schedule it for 19:00, Hermoso posts left (`hermoso_credits` → `posting.left`), how many real archive images were
used and from which sources (`tools/image_check.py`), anything uncertain,
tomorrow's case.

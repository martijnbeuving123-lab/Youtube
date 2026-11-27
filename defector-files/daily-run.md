# Daily production run — The Defector Files

A scheduled task starts a fresh session every morning. **Deadline: by 15:00 Amsterdam time
the owner has the MP4 and the upload pack.** The owner uploads it to YouTube themselves.

Read `defector-files/README.md` and `defector-files/voice.md` first. Work on branch
`claude/pensive-cerf-dz4nqf`. Commit and push after every step (`git pull --rebase` before every
push: the Precinct Archive run pushes to the same branch, in other folders). Never touch files
outside `defector-files/` except shared tools when a tool bug blocks you.

**Do not use vidIQ or any upload tool for this channel.**

## 0. Check (5 min)
- `bash tools/setup.sh` (Kokoro, yt-dlp, soundfile).
- `TZ=Europe/Amsterdam date`. If the previous run left a half-finished video (see
  `defector-files/pipeline.md`), finish that one first.

## 1. Pick the case with the most viral potential (30 min)
1. Candidates (8–12), always including at least two **recent** cases (2015 onwards, see
   README.md; aim for about 1–2 recent videos a week, check the case log for this week's mix):
   unproduced cases in the case log, plus
   `~/kvenv/bin/python tools/collect_channels.py defector-files/competitors.txt > /tmp/collected.json`
   and `python3 .claude/skills/yt-viral/swipe.py /tmp/collected.json --min 2.0` (what beats its
   channel's median, and which formula), plus WebSearch for anniversaries, new books,
   documentaries, declassifications or news that put an old case in the spotlight.
2. **Check images before choosing:** `python3 tools/loc_get.py --search "<case terms>"`. A case
   needs at least 8 usable full-size images (people, places, documents) or it waits.
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
- ~3,000 words, 50–60 beats, each with `[ON SCREEN: ...]`, structure and voice per `voice.md`.
  Score 5 hooks with the `yt-script` scorer and keep the best.
- `beats.json`: `[{"id": "01", "screen": "...", "text": "narration"}]`. Write numbers and dates
  as words where Kokoro might misread them ("June nineteenth, 1953").

## 4. Images (start right after the pick)
- `python3 tools/loc_get.py defector-files/videos/<slug> name=<item id> ...` (writes credits).
- Commons via `tools/commons_get.py` only if LoC lacks something; it may be rate-limited.
- Cards with `tools/cards.py` (title, text, quote, telegram with your own sub line), maps with
  `tools/maps.py`. Look at every image before using it.

## 5. Audio (15 min)
- `~/kvenv/bin/python tools/voiceover.py defector-files/videos/<slug> --voice am_michael --speed 0.95`
- `~/kvenv/bin/python tools/music.py defector-files/videos/<slug> --minutes 22 --key <A-G> --seed <day>`

## 6. Edit and render (30 min)
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

## 8. Deliver to the owner (by 15:00)
- Write `defector-files/deliveries/<slug>/upload.md` with, ready to paste: title, description
  (with chapters), tags, pinned comment, category Education, "Altered or synthetic content: Yes",
  "Made for kids: No", language English. Copy `thumbnail.jpg` and `captions.srt` there. Push.
- Send the MP4 with SendUserFile (status `proactive`, display `attach`), with a one-line caption.
  If the send fails or the file is refused, say so in the report and leave the MP4 in the session.

## 9. Report (Dutch, short)
Update `defector-files/pipeline.md` (case → Produced, tomorrow's case → Next up). Then report:
the title and case, where the upload pack is, the owner's steps (upload in Studio, paste
`upload.md`, thumbnail, captions, AI disclosure Yes, not for kids, publish), anything uncertain,
tomorrow's case.

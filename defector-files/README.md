# The Defector Files — channel brief

YouTube channel **The Defector Files** (@TheDefectorFiles, channel ID `UCgxd9z2Sxn6dPkxhZdQvpJg`).
Faceless, narrated documentaries of about 20 minutes: true spy stories from the declassified
record. Double agents, defectors, moles, codebreakers, wartime deceptions, and the
investigations that caught them. Closed cases only.

Sister channel of Precinct Archive; it shares the repo's `tools/` and the yt-* skills.
Talk to the owner in Dutch. Videos, scripts and metadata in English (**American spelling**,
American date order: "June 19, 1953").

## Standing decisions (owner, 2026-11-27)

- One case, one video, about 20 minutes (~3,000 words). Every day.
- **Claude uploads every video as PRIVATE via Hermoso** (owner's decision, 2026-11-27), by
  **15:00 Amsterdam time**, with title, description, tags, category Education, thumbnail,
  captions, "altered or synthetic content" Yes and "made for kids" No. The owner checks it in
  YouTube Studio and makes it public themselves. Never public, unlisted or scheduled, and no
  other changes on the live channel, except that the Sunday weekly review may repackage
  underperforming public videos (title, description, tags, thumbnail in the house style;
  `channel/weekly-review.md` step 3b). No vidIQ for this channel. Steps: `daily-run.md` step 8.
  The upload pack in `defector-files/deliveries/<slug>/` is still written, as a record and backup.
- Research, script, packaging and SEO with the repo skills (`yt-viral`, `yt-script`,
  `yt-package`, `yt-seo`). No paid services.
- Voice: Kokoro `am_michael`, speed 0.95 (`tools/voiceover.py`). Music: `tools/music.py`.
- Visuals: real public-domain archive material only. Main source: Library of Congress
  (`tools/loc_get.py`; only items with a full-size image and "no known restrictions" /
  government work). Wikimedia Commons (`tools/commons_get.py`) as a second source; it is often
  rate-limited from the cloud. Cards (`tools/cards.py`) and maps (`tools/maps.py`) fill gaps.
  Record every image in `credits.md`. **No AI imagery of real people.** Never present a
  generic photo as the specific person, place or document.
- **Recent cases are welcome** (owner, 2026-11-27): now and then, about 1–2 times a week, a case
  from roughly 2015 onwards (e.g. a 2020 arrest), when it beats the historical candidates on
  the scores. Extra rules for recent cases: the conviction or guilty plea is final (no trial or
  appeal still running) or the facts are officially confirmed; only what courts, prosecutors
  and official bodies established; living relatives and bystanders are not named; no claims
  about people who were never charged. Images: court sketches and documents released by the
  court or the US government, maps and cards; never press photos without a clear licence.
- Hard limits: closed case; strong sources; nobody called a spy unless convicted, officially
  confirmed (e.g. Venona, an official history) or self-confessed; contested points flagged;
  advertiser-safe; no glorifying of violence.

Voice profile: `defector-files/voice.md`. Daily runbook: `defector-files/daily-run.md`.
Production board and case log: `defector-files/pipeline.md`.

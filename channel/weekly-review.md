# Weekly review — both channels (Sunday 15:00 Amsterdam)

A scheduled task starts a fresh session every Sunday at about 15:00 Amsterdam time. That session
follows this runbook. Goal: measure the past week on **Precinct Archive** and **The Defector
Files**, give the owner extensive advice in Dutch, and **improve the daily runbooks itself** so
next week's videos are better.

Work on branch `claude/pensive-cerf-dz4nqf` (the branch both daily runs use). `git pull --rebase`
before every push. Read first: `CLAUDE.md`, `.claude/youtube/ceo-brief.md`,
`channel/daily-run.md`, `defector-files/README.md`, `defector-files/daily-run.md`, both
`pipeline.md` files, and the previous reports in `reports/weekly/` (especially the last one's
"experiments" section — this week's job is to judge them).

## Hard limits (never change these, not even via a runbook edit)
- On the live channels you may change **only the title, description, tags and thumbnail** of
  public videos, as step 3b describes (owner's decision, 2026-11-27). Never privacy, schedule,
  made-for-kids, AI disclosure, category, comments, playlists, posts, uploads or deletions.
- **Thumbnail house style is fixed.** A new thumbnail is made with `tools/thumbnail.py` in the
  channel's own house style; only the photo and the words change. Never a different layout, font,
  colour scheme or template, not even on one video.
- No spending: never buy credits, plans or paid services. vidIQ: at most **60 credits** per
  review (analytics 5 per call, each title/description/tags update 5, each thumbnail 5); check
  `vidiq_balance` first, and never let it drop below 550 (the daily Precinct video needs ~520).
  Hermoso analytics and updates are free.
- Do not touch the owner's standing decisions in `CLAUDE.md`, `defector-files/README.md` and the
  "Hard limits"/"Standing decisions" sections: private uploads only, daily cadence, voices, no AI
  images of real people, ethics and source rules, upload deadlines. If the data says one of those
  should change, put it in the report as a **proposal for the owner**, do not edit it.
- Never invent a number. If a metric is missing, say so. Zero rows means "no data", not zero views.
- Do not edit the scheduled tasks themselves.

## 1. Collect data (window: last 7 days, plus the 28 days before it for comparison)
Save raw numbers to `reports/weekly/data/<YYYY-MM-DD>.json` (small JSON, no media).

**Precinct Archive** (`UCdRfVXC9tY_Poq1cNZ-JXGA`, vidIQ connector):
- `vidiq_channel_analytics` with `report: "top_videos"` (metrics views, engagedViews,
  estimatedMinutesWatched, averageViewDuration, averageViewPercentage, subscribersGained),
  `report: "traffic_sources"`, and `dimensions: ["day"]` for the trend.
- `audience_retention` for the 1-2 most important videos of the week (best and worst).
- Use `engagedViews` for comparisons (YouTube changed view counting on 2026-08-27).

**The Defector Files** (`UCgxd9z2Sxn6dPkxhZdQvpJg`, Hermoso connector, 0 credits):
- `youtube_channel_report` reports `topVideos`, `trafficSource`, `day`, `subscribedStatus`,
  `trafficSourceDetail` with parent `YT_SEARCH` (the real search terms), and `audienceRetention`
  for the best and worst video of the week. `youtube_video_insights` / `list_youtube_video_stats`
  for per-video CTR and impressions when available.

**Both (public, free):** TubeAlfred `youtube_channel_videos` for the public list, titles and
views; `youtube_comments_list` on this week's videos (what viewers ask, praise, complain about).
If a connector is missing in the session, use the public data, and say in the report which
connector the scheduled task lacks.

**Monetisation (both channels):** public subscriber counts (TubeAlfred `youtube_channel_get`);
long-form watch minutes over the last 365 days and Shorts views over the last 90 days
(`report: "shorts_vs_longform_split"` / Hermoso `report: "contentType"`, one call per window).
Check the current Partner Program thresholds (WebSearch on YouTube's own help page; they are
reported to double for new applicants from 2027-02-01).

**Competitors (both niches):** for the channels in `channel/competitors.txt` and
`defector-files/competitors.txt` (add strong ones you find): subscribers, uploads in the last
7 days, and their best video of the week with its views (TubeAlfred `youtube_channel_get` /
`youtube_channel_videos`, or `tools/collect_channels.py`). Run `/yt-viral` (`swipe.py`) on it.

Join the numbers to the repo: for each video find `videos/<slug>/` or
`defector-files/videos/<slug>/` (title, hook, case, length, thumbnail text, selection scores in
`channel/selection/`). That turns "video X did well" into "hook type / case type / title formula
Y did well".

## 2. Analyse
Per channel, and then the two side by side:
- **Trend:** views/engaged views, watch time, subscribers, this week vs the previous 4 weeks.
- **Packaging:** CTR and impressions per video; which title formulas and thumbnail texts win.
  Run `python3 .claude/skills/yt-package/title.py` on the week's titles for a lint.
- **Retention:** where viewers leave (first 30 s, first minute, mid-video dips). Use the
  `yt-retention` method. Connect dips to beats in `beats.json` / `script.md`.
- **Topics:** which case types beat the channel median (use the selection scores: did high
  "demand"/"topicality" scores predict views? Recalibrate the weights if not).
- **Traffic:** search vs browse vs suggested; which search terms bring viewers (feed this into
  `yt-seo` guidance).
- **Production quality:** read the week's run reports and pipeline: missed deadlines, failed
  steps, image problems, render issues. Fixes go into the runbooks.
- **Last week's experiments:** worked / did not work / not enough data.

Be honest about small numbers: with a few hundred views, one video is noise. State confidence
(high/medium/low) for every conclusion and do not overfit a runbook to one data point.
**Minimum-data rule:** while a channel's videos get fewer than ~100 views each, change no content
rules (topics, hooks, length) on performance; only fix packaging (titles, thumbnails, search
names) and production problems.

**Hermoso data:** Hermoso relays YouTube API data under YouTube's developer policy: show those
numbers exactly as returned (tables are fine) and add no derived figures (percentages, ratios,
averages, rankings, growth) and no sentences that interpret them. For The Defector Files, base
advice on content (titles, scripts, comments, public counts) and on numbers as returned.

## 2b. Be the best in the niche
The owner's goal is for both channels to become the best in their niche. Keep a leaderboard per
niche in `channel/niche-leaderboard.md` and `defector-files/niche-leaderboard.md`: each
competitor's subscribers, weekly uploads and best video of the week, with our channel in the same
table, week by week. From it, name in the report:
- which cases, angles and title formulas broke out for competitors this week (outlier multiple
  from `swipe.py`), and which of them we should cover next (add them to the case log with the
  evidence, so the daily runs pick them up);
- what the top channels do that we do not (length, thumbnails, openings, series, Shorts,
  community posts), each as a concrete action or experiment;
- where we already beat them.
Never copy a competitor's script, title word for word or thumbnail; take the case and the
pattern, and make our own.

## 3. Improve the process yourself
Make concrete, small edits — at most about 5 per channel per week — where the evidence supports
them, in these files only:
- `channel/daily-run.md`, `defector-files/daily-run.md` (steps, checks, time budget)
- `.claude/youtube/voice.md`, `defector-files/voice.md` (hook and script guidance)
- `channel/competitors.txt`, `defector-files/competitors.txt` (add/remove channels to study)
- the selection weights/criteria in the daily runbooks
- `channel/playbook.md` and `defector-files/playbook.md` — the running list of **what works**
  (create them if missing): proven title formulas, hook types, case types, thumbnail rules,
  each with the evidence and date. Daily runs must read the playbook (add that line to step 1
  of each daily runbook if it is not there yet).

Each edit: one commit with a clear message (`Weekly review <date>: <change> (evidence)`).
Never delete a rule silently: move retired rules to a "Retired" section with the reason.
Also set **1-3 experiments for next week** per channel (e.g. "3 of 7 titles use a question
formula") and write them into the daily runbook so the daily runs actually do them; mark them
`EXPERIMENT <date>` so next Sunday can judge them.

## 3b. Fix the packaging of videos that did not work
The owner wants underperforming videos repackaged every week, not just advice.

**Which videos.** Public videos at least 7 days old, not repackaged in the last 14 days (see the
packaging log), that clearly lag the channel's own videos (views, impressions click-through,
views from search) or fail the `yt-package` / `yt-seo` checks (truncated or vague title, no
searchable case name, thin description, missing tags). At most **5 videos per channel per week**,
worst first. Never touch a video that is still private (the owner has not reviewed it yet).

**What to change.** Preferably one element per video, so next week shows what worked:
- **Title:** `/yt-package` (`title.py`); lead with the name people search for; under ~60
  characters visible; British spelling for Precinct Archive, American for The Defector Files;
  factual, no claim the video does not deliver, nobody called guilty who was not convicted.
- **Description and tags:** `/yt-seo`. Keep chapters, sources/credits lines and disclosures.
- **Thumbnail:** only `tools/thumbnail.py` in the house style (Precinct Archive: reference
  `videos/crippen/out/thumbnail.jpg`; The Defector Files: `defector-files/voice.md`). New archive
  photo and/or new words, same rules as the daily run (real archive image, no AI images of real
  people, words do not repeat the title). Look at the image before uploading.

**How.** Precinct Archive: `vidiq_update_video` (title/description/tags) and
`vidiq_update_video_thumbnail`, channel `UCdRfVXC9tY_Poq1cNZ-JXGA`. The Defector Files: Hermoso
`update_youtube_video` (only `title`, `description`, `tags`) and `set_youtube_thumbnail` (image via
`upload_file`). Read the result back; if YouTube asks for verification, stop and tell the owner.

**Log every change** in `channel/packaging-log.md` or `defector-files/packaging-log.md` (create
if missing): date, video id, element, old value → new value, reason with evidence. Also update the
video's `metadata.md` in the repo. Next Sunday, compare before/after; if a change did worse,
restore the old value and note it in the log. Winning patterns go into the playbook.

**If the house style itself seems to be the problem** (e.g. click-through stays low across many
videos while titles and topics vary): do NOT change the style. Put it in the report under
"Jouw akkoord nodig": the evidence, and 1-2 alternative styles as example images (made locally,
not uploaded). Only after the owner approves a new style in a conversation is it applied, and then
to **all** videos of that channel at once and in `tools/thumbnail.py` and the daily runbook, so
the channel keeps one style.

## 3c. Update the money plan
Check `channel/monetisation-plan.md` against this week's numbers and rules: update the "Waar staan
we" table, mark steps done, and add the most useful next step. Changes to the owner's decisions
(Shorts, accounts, spending) stay proposals.

## 3d. Challenge yourself
The owner wants Claude to keep raising the bar, not just tick boxes. Every week:
- **Self-critique:** name the weakest part of our own process this week (selection, research,
  script, visuals, packaging, the checks) and fix one thing in it, with evidence.
- **One bold idea:** propose or run (within the hard limits) one experiment bigger than a tweak:
  a new format, a new hook style, a new kind of case, a series of related cases, a collaboration
  idea. Say what success would look like and how we measure it next week.
- **Benchmark up:** compare our best video with the niche's best video of the week and name the
  gap honestly.

## 3e. Growth: when to propose a new channel
The owner wants to add a channel, run exactly like the other two, as soon as one is clearly going
the right way. Check every week whether **one** channel meets all of these:
- at least 4 weeks of daily uploads with no missed day and no failed 19:00 schedule;
- subscribers and long-form watch minutes up three weeks in a row;
- the production runs finish without manual fixes (images, render, upload).

When that is true, research a niche for channel 3 and put a recommendation in the report:
3 candidate niches, each with evidence: outlier videos and competitor channels (`/yt-viral`,
`swipe.py`), audience size and growth, likely ad value (RPM: history/education is mid to high),
free archive imagery available for it (Library of Congress, Wellcome, Commons, national
archives), whether our tools and rules fit (faceless, closed or historical subjects, no AI images
of real people, advertiser-safe), competition, and risk under YouTube's inauthentic-content
policy. Name your pick and why, plus a channel name, positioning line and the first 10 video
ideas. The owner decides and creates the YouTube channel; after that Claude sets it up like
`defector-files/` (README, voice, runbook, competitors, pipeline) and proposes the daily task.
Until then, keep a short list of niche candidates in `channel/next-channel.md` and update it
when the weekly research turns up evidence.

## 3f. Monetisation-review audit ("keuringscheck")
The owner does not want to work a year and then be rejected. Audit both channels every week as
a YouTube Partner Program reviewer would, against `channel/originality-rules.md` and YouTube's
current monetisation policies (inauthentic content, reused content, advertiser-friendly
guidelines; check the current wording with WebSearch on YouTube's help pages once a month).
- **Every week (light):** sample 3 videos per channel: this week's newest, the most viewed and the
  one with the most watch time (that is what reviewers look at). Score each rule pass/fail, look
  at the 10 newest titles and thumbnails side by side for sameness, and check the originality
  gate lines in `metadata.md`. Fix process problems in the runbooks (step 3); name videos that
  would hurt a review.
- **Full audit** once a channel is within about 20% of a threshold (subscribers or watch hours):
  every public video, the channel page and About text, and a clear verdict: **groen** (apply),
  **oranje** (fix these first) or **rood** (do not apply yet), with the list of fixes. Advise
  the owner to apply only on groen.
- Proposals that need the owner (human voice, making weak old videos private, slower cadence) go
  under "Jouw akkoord nodig".
In the report: a traffic light per channel (keuringsstatus) and the top 3 risks.

## 4. Report → `reports/weekly/<YYYY-MM-DD>.md` (Dutch)
Structure:
1. **Samenvatting** (5 regels): hoe ging de week, belangrijkste inzicht, belangrijkste actie.
2. **Cijfers** per kanaal: tabel met de video's van de week (titel, views/engaged views, CTR,
   gem. kijkduur, % bekeken, abonnees), plus week-op-week verandering.
3. **Wat werkte / wat niet** — met bewijs en zekerheid.
4. **Uitgebreid advies** per kanaal: titels, thumbnails, hooks, onderwerpen, lengte, SEO,
   Shorts, community, en strategie voor de komende 30 dagen.
5. **Wat ik zelf heb aangepast** — elke wijziging aan draaiboeken (bestand, waarom, commit) én
   elke aangepaste video: oude → nieuwe titel/beschrijving/tags/thumbnail, met reden; plus het
   oordeel over de aanpassingen van vorige week (beter/slechter/teruggedraaid).
6. **Experimenten volgende week**, inclusief het grote idee van de week (3d).
6a. **Keuringsstatus** per kanaal (groen/oranje/rood) met de top 3 risico's (3f).
6b. **Groei:** staat een kanaal klaar voor een nieuw zusterkanaal (3e)? Zo ja: nicheadvies.
7. **Voorstellen die jouw akkoord nodig hebben** (bijv. aanpassingen aan bestaande live-video's,
   andere uploadtijd, uitgaven, wijzigingen aan vaste besluiten) — als duidelijke vragen.
8. Kosten van deze review (vidIQ-credits gebruikt, saldo).

## 4b. Update the dashboard (https://claude.ai/artifact/JtDHcTqwXtZH9DyK1gbr1q)
The owner wants the weekly report, including the money progress, in this dashboard every Sunday.
It is an Artifact of the "Data" type: its numbers are CSV files, its text is `files/index.html`
in its store. Load the `Artifact` and `ArtifactData` tools (ToolSearch), then:
1. Read the store (`ArtifactData` list on collections `dash`, `datasets`, `files`) and note each
   document's `version`.
2. Write this week's CSVs with the same columns as the current files (`precinct_videos.csv`,
   `defector_videos.csv`, `defector_traffic.csv`, `channels.csv`, `ypp.csv`; read the current ones
   with `Artifact` read `path` if needed), upload each with `Artifact` publish `asset: true` to
   the dashboard url, and point each dataset at its new `/_blob/<id>` with an `update` (with
   `if_version`) that also sets `updated: {at, by: "Claude, weekreview"}`.
3. Replace the week-specific text in `files/index.html` (date line, takeaway, findings, advice,
   what was changed, experiments, approvals) with `str_replace` on its `text` field. Keep the
   layout, classes, `data-draw` drawings and marks. Never put a number in static text that a
   dataset holds; mark it instead.
4. Read `data/users/me/check` and `runs` afterwards; fix what fails. If the dashboard cannot be
   reached, say so in the report and carry on.
Hermoso numbers (The Defector Files) are shown as returned, with no derived figures.

Commit and push the report. The owner reads the result in the Claude app (push notification),
so end with a final message in Dutch that holds the advice in full: points 1, 3-7 of the report
(not only a summary), the money progress, plus the report's path and the dashboard link. Send the report file with `SendUserFile` (status
proactive). No email.

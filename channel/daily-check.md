# Daily check — both channels (every day ~17:40 Amsterdam)

A scheduled task starts a fresh session every day at about 17:40 Amsterdam time, after both
upload deadlines (The Defector Files 15:00, Precinct Archive 17:00) and before the owner makes the
videos public at 19:00. Two jobs: **(A) is today's video on each channel fully ready to go public
at 19:00**, and **(B) reply to viewers' comments**. Owner's decisions, 2026-11-27.

Work on branch `claude/pensive-cerf-dz4nqf`; `git pull --rebase` before every push. Read
`CLAUDE.md`, `defector-files/README.md`, `.claude/youtube/voice.md` and `defector-files/voice.md`
first. Talk to the owner in Dutch.

Connections: **Precinct Archive** (`UCdRfVXC9tY_Poq1cNZ-JXGA`) via vidIQ, or via Hermoso if that
channel is connected there (`list_connector_accounts`; Hermoso is free, prefer it).
**The Defector Files** (`UCgxd9z2Sxn6dPkxhZdQvpJg`) via Hermoso. Public reads via TubeAlfred.

## Hard limits
- Never change privacy, never make anything public or unlisted, never schedule (`publishAt`),
  never delete anything. The owner makes videos public at 19:00.
- vidIQ: at most 30 credits per day, and never below a balance of 550. Never buy anything.
- Only reply to comments; never delete, hide, hold, like-bomb or report them, never post to the
  community tab.

## A. Readiness check for today's private upload
For each channel, find today's upload (the newest private video; `channel/pipeline.md` /
`defector-files/pipeline.md` and `deliveries/<slug>/` / `defector-files/deliveries/<slug>/` say
which one and hold the prepared files). Check:

| Check | Pass |
|---|---|
| Video uploaded today | yes, and still **private** |
| Processing | finished, plays, no copyright/claim warning if the connector shows it |
| Length | about 15–25 minutes |
| Title | matches `metadata.md`, ≤100 characters, correct spelling (British / American) |
| Description | present, with chapters (first at 0:00) and the sources/credits line |
| Tags | present |
| Thumbnail | custom thumbnail set, in the house style |
| Captions | English captions uploaded |
| Audience | made for kids: **No** |
| AI disclosure | altered or synthetic content: **Yes** |
| Category | Education (27) |

**Fix what you can** with the prepared files from the repo, never anything else: title,
description and tags from `metadata.md`; the thumbnail from `deliveries/<slug>/`; captions from
`deliveries/<slug>/captions.srt` (Hermoso `manage_youtube_caption` for The Defector Files);
made-for-kids No and AI disclosure Yes (Hermoso `update_youtube_video` for The Defector Files).
For Precinct Archive, vidIQ can set title/description/tags and the thumbnail; what it cannot set
(captions, AI disclosure, made-for-kids) goes on the owner's to-do list unless Hermoso reaches
that channel. Read every change back.

**No video uploaded?** Say so plainly at the top of the report ("NIET KLAAR"), with what the
day's production run reported (its session / `pipeline.md`), and whether the finished MP4 exists
so the owner can upload it by hand.

## B. Comment replies (Claude posts them)
1. Read new comments on the channel's public videos from the last 60 days (Hermoso
   `list_youtube_comments`; vidIQ `vidiq_video_comments` for Precinct Archive). Skip comments
   already answered: check `channel/comments-log.md` / `defector-files/comments-log.md` (create if
   missing) and whether the channel already replied in the thread.
2. Reply to every genuine comment — questions, praise, corrections, case discussion, topic
   requests — up to **20 per channel per day** (Precinct Archive via vidIQ: at most 10, 1 credit
   each). Oldest unanswered first.
3. **Skip** spam, bots, self-promotion, links, abuse, trolling and political fights. Never argue.
4. How to reply: as the channel, in English (British spelling for Precinct Archive, American for
   The Defector Files), in the channel's voice (`voice.md`): 1–3 short sentences, warm, specific
   to what they said, factual. Answer questions only from the video's `research.md`; if unsure,
   say so. Never call anyone guilty who was not convicted, never add new allegations, never share
   personal data, no links except to the channel's own videos or playlists, no begging for
   subscriptions, at most one emoji. If asked whether AI is used, answer honestly that the
   channel uses AI tools (voice, production) and researches every case from archive sources.
5. **Flag, don't just answer:** a factual correction that looks right (log it in the pipeline as
   a possible correction for the owner), a commenter who says they are a relative of someone in
   the case (reply with care and respect only, and flag it), legal threats or copyright claims
   (do not reply; flag), topic requests (add to the case log as candidates).
6. Log each reply: date, video, comment id, short comment, reply text.
Never post the same reply twice; if a posting result is uncertain, check the thread before
retrying.

## Report (Dutch, short — the owner reads it as a notification)
Start with one line per channel: **✅ klaar voor 19:00** or **❌ niet klaar**. Then per channel:
what was wrong and what you fixed, what the owner must still do in YouTube Studio (if anything),
the number of comments answered and skipped, and anything flagged. Commit and push the logs.

# Claude Code YouTube Automation Pipeline

> Open-source starter kit for building an automated YouTube upload pipeline with Claude. Schedule and post 50+ videos a day to YouTube, TikTok, and Instagram. **No coding experience required** — Claude builds the pipeline with you, step by step.

🎥 **Video walkthrough:** [Coming soon — link will be added when video drops]
📺 **YouTube channel:** [@CryptoClaud](https://www.youtube.com/@CryptoClaud)

---

## What This Kit Does

This kit turns Claude into your engineering partner. By the end of setup, you'll have a Python pipeline that:

- Uploads videos to your YouTube channel on a schedule (2x/day, 6x/day, or whatever you choose)
- Reads from a simple spreadsheet you fill out in Excel
- Cross-posts the same video to TikTok and Instagram automatically (optional)
- Handles authentication, slot scheduling, and error recovery for you

The result: drop new videos in a folder, fill out a spreadsheet, run one command. Everything else happens on autopilot.

You don't need to know Python, OAuth, or the YouTube API. Claude reads the included runbook and walks you through every step.

---

## Quick Start

1. **Download this kit** — click the green **`Code`** button above → **`Download ZIP`**, then unzip it.
2. **Open the folder in Cowork** (the Claude desktop app) OR **navigate to it in Claude Code** (the CLI).
3. **Tell Claude this exact message:**
   > *"Read START_HERE.md and walk me through setting this up step by step."*
4. **Answer Claude's questions** as it walks you through Google Cloud setup, OAuth, the spreadsheet, and your first test upload.
5. **Run your first batch upload** when Claude says you're ready.

That's it. Claude does the heavy lifting.

**Estimated setup time:** 45-90 minutes the first time. After setup, daily runs take 60 seconds.

---

## What's in This Kit

| File | What It Is |
|---|---|
| **[START_HERE.md](START_HERE.md)** | The runbook Claude reads to walk you through setup |
| **[pipeline_template.py](pipeline_template.py)** | The Python upload script template — Claude will customize it for your channel |
| **[upload_master_TEMPLATE.xlsx](upload_master_TEMPLATE.xlsx)** | Spreadsheet template for managing your upload queue |
| **[sora_prompting_guide.md](sora_prompting_guide.md)** | How to write Sora prompts that produce consistent characters across videos |

---

## Tools You'll Need

These are the tools used in the kit. Some have referral or affiliate links — they don't cost you anything extra and they help support the channel.

- **[Claude](https://claude.ai)** — the AI doing the work. Pro plan ($20/mo) or Max plan ($100-200/mo) recommended for this kit. Use referral code in the description of the YouTube video for a discount.
- **[VidIQ](https://vidiq.com)** — keyword research and metadata optimization (used in Part 2 of the series)
- **[CapCut](https://www.capcut.com)** — video editing (free tier works fine)
- **[Sora 2 / ChatGPT Plus](https://openai.com/chatgpt)** — for AI video generation
- **[Upload Post](https://upload-post.com)** — for cross-posting to TikTok and Instagram (optional)

---

## Requirements

Before you start, you'll need:

- **Python 3.10 or newer** ([download here](https://www.python.org/downloads/))
- **A YouTube channel you own** (with the Channel ID handy)
- **A Google account** that owns the channel
- **A Google Cloud account** (free — [console.cloud.google.com](https://console.cloud.google.com))
- **At least 5-10 video files** ready to upload
- **Either Cowork or Claude Code** (any plan that includes Claude)

For optional cross-posting:
- An Upload Post account (free tier available)
- A TikTok account and an Instagram Business or Creator account

---

## How This Differs from Other Tutorials

Most YouTube automation tutorials give you code. This kit gives you a runbook that Claude reads — so even non-coders can build their own pipeline by answering questions, not by reading documentation.

The pipeline this kit builds is the same architecture used to run multiple production YouTube channels with hundreds of scheduled uploads.

---

## License

MIT — see [LICENSE](LICENSE). Free to use, modify, and redistribute. Attribution to CryptoClaud appreciated but not required.

---

## Support & Updates

- **Found a bug or have a suggestion?** Open an issue on this repo
- **Want walkthroughs of advanced features?** New videos in the series cover OAuth deep-dives, metadata generation, scaling to 100+ uploads/day, and more
- **Subscribe** to [@CryptoClaud](https://www.youtube.com/@CryptoClaud) for updates as the kit evolves

---

*Built with Claude. Documented for humans.*

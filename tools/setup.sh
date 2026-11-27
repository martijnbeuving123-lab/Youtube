#!/bin/bash
# One-time tool setup for a production session: Kokoro TTS, yt-dlp, espeak-ng.
set -e
command -v espeak-ng >/dev/null || apt-get install -y -q espeak-ng >/dev/null
[ -x "$HOME/kvenv/bin/python" ] || python3 -m venv "$HOME/kvenv"
"$HOME/kvenv/bin/pip" install -q --upgrade kokoro soundfile yt-dlp
echo "tools ready: $HOME/kvenv/bin/python"

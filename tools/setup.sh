#!/bin/bash
# One-time tool setup for a production session: Kokoro TTS (ONNX), soundfile, yt-dlp.
set -e
[ -x "$HOME/kvenv/bin/python" ] || python3 -m venv "$HOME/kvenv"
"$HOME/kvenv/bin/pip" install -q --upgrade kokoro-onnx soundfile yt-dlp
mkdir -p "$HOME/.cache/kokoro"
for f in kokoro-v1.0.onnx voices-v1.0.bin; do
  [ -s "$HOME/.cache/kokoro/$f" ] || curl -sSL -o "$HOME/.cache/kokoro/$f" \
    "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/$f"
done
echo "tools ready: $HOME/kvenv/bin/python"

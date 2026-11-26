#!/bin/bash
# Link the repo's voice profile to where the yt-* skills look for it.
mkdir -p "$HOME/.claude/youtube"
ln -sf "$CLAUDE_PROJECT_DIR/.claude/youtube/voice.md" "$HOME/.claude/youtube/voice.md"

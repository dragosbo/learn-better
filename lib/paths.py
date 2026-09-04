"""Shared output folder names, so all scripts agree on where things go.

All outputs live under a single `data/` root. Everything under `data/` is
git-ignored EXCEPT `data/summaries/`, which is kept tracked via a .gitignore
negation (authored content). Paths are relative to the repo root, which is where
the scripts/runners are run from.
"""

import os

DATA_DIR = "data"              # single root for all outputs (structured + generated)
AUDIO_DIR = os.path.join("data", "audio")            # downloaded audio (mp3/webm/m4a)
AUDIO_REENCODED_DIR = os.path.join("data", "audio_reencoded")  # re-encoded audio at a target bitrate
TRANSCRIPT_DIR = os.path.join("data", "transcripts")  # saved transcript .txt files (from YouTube captions)
GENERATED_TRANSCRIPT_DIR = os.path.join("data", "generated_transcripts")  # Whisper-generated transcripts
WORDCLOUD_DIR = os.path.join("data", "wordclouds")   # word_cloud.json outputs
TTS_OUTPUT_DIR = os.path.join("data", "tts_output")  # text-to-speech audio (wav/mp3) from text sources
SUMMARY_DIR = os.path.join("data", "summaries")      # AI-generated summaries (tracked via .gitignore negation)

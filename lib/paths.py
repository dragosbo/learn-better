"""Shared output folder names, so all scripts agree on where things go.

All three are git-ignored (see .gitignore). Paths are relative to the repo
root, which is where the scripts/batch files are run from.
"""

import os

AUDIO_DIR = "audio"            # downloaded audio (mp3/webm/m4a)
TRANSCRIPT_DIR = "transcripts"  # saved transcript .txt files (from YouTube captions)
GENERATED_TRANSCRIPT_DIR = "generated_transcripts"  # Whisper-generated transcripts
DATA_DIR = "data"              # structured data, e.g. data/playlists.json
WORDCLOUD_DIR = os.path.join("data", "wordclouds")  # word_cloud.json outputs

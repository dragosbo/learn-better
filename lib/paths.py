"""Shared output folder names, so all scripts agree on where things go.

All three are git-ignored (see .gitignore). Paths are relative to the repo
root, which is where the scripts/batch files are run from.
"""

AUDIO_DIR = "audio"            # downloaded audio (mp3/webm/m4a)
TRANSCRIPT_DIR = "transcripts"  # saved transcript .txt files
DATA_DIR = "data"              # structured data, e.g. data/playlists.json

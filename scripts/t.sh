#!/usr/bin/env bash
# Transcripts only, per language (Linux/macOS equivalent of t.bat).
#   ./t.sh
set -e
if command -v conda >/dev/null 2>&1; then
    source "$(conda info --base)/etc/profile.d/conda.sh"
    conda activate learn-better 2>/dev/null || true
fi
python code/read_transcript.py

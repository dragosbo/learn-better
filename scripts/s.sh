#!/usr/bin/env bash
# Prepare summaries: list transcripts needing one + print the AI instruction
# (Linux/macOS equivalent of s.bat).
#   ./s.sh
set -e
if command -v conda >/dev/null 2>&1; then
    source "$(conda info --base)/etc/profile.d/conda.sh"
    conda activate learn-better 2>/dev/null || true
fi
python code/make_summaries.py

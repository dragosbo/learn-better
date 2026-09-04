#!/usr/bin/env bash
# Audio + transcripts for a source (Linux/macOS equivalent of r.bat).
#   ./r.sh
set -e
if command -v conda >/dev/null 2>&1; then
    source "$(conda info --base)/etc/profile.d/conda.sh"
    conda activate learn-better 2>/dev/null || true
fi
python code/read_channel.py

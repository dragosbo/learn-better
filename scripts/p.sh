#!/usr/bin/env bash
# List a channel's public playlists -> data/playlists.json (equivalent of p.bat).
#   ./p.sh
set -e
if command -v conda >/dev/null 2>&1; then
    source "$(conda info --base)/etc/profile.d/conda.sh"
    conda activate learn-better 2>/dev/null || true
fi
python code/list_playlists.py

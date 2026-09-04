#!/usr/bin/env bash
# Audio re-encode / bitrate (todo1 item 4). Optional arg: a JSON config in config/.
#   ./a.sh                            -> config/config_reencode.json (or in-file defaults)
#   ./a.sh config/config_reencode.json -> explicit config
set -e
if command -v conda >/dev/null 2>&1; then
    source "$(conda info --base)/etc/profile.d/conda.sh"
    conda activate learn-better 2>/dev/null || true
fi
python code/reencode_audio.py "$@"

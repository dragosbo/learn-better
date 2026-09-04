#!/usr/bin/env bash
# Text to speech via Piper (todo2, Phase D). Optional arg: a JSON config in config/.
#   ./v.sh                        -> config/config_tts.json (or in-file defaults)
#   ./v.sh config/config_tts.json -> explicit config
set -e
if command -v conda >/dev/null 2>&1; then
    source "$(conda info --base)/etc/profile.d/conda.sh"
    conda activate learn-better 2>/dev/null || true
fi
python code/generate_speech.py "$@"

#!/usr/bin/env bash
# Whisper transcription (Phase C). Optional arg: a JSON config file in config/.
#   ./w.sh                                  -> config/config_transcribe.json (or in-file defaults)
#   ./w.sh config/config_transcribe.id.json -> transcribe by video id
set -e
if command -v conda >/dev/null 2>&1; then
    source "$(conda info --base)/etc/profile.d/conda.sh"
    conda activate learn-better 2>/dev/null || true
fi
python code/transcribe_audio.py "$@"

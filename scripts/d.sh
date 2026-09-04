#!/usr/bin/env bash
# Word cloud data for ONE transcript (the INPUT set atop make_wordcloud.py)
# (Linux/macOS equivalent of d.bat).
#   ./d.sh
set -e
if command -v conda >/dev/null 2>&1; then
    source "$(conda info --base)/etc/profile.d/conda.sh"
    conda activate learn-better 2>/dev/null || true
fi
python code/make_wordcloud.py

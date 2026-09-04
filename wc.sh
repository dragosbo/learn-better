#!/usr/bin/env bash
# Word cloud batch/merge (Phase W3). Optional arg: a JSON config file in config/.
#   ./wc.sh                               -> config/config_wordcloud.json (or in-file defaults)
#   ./wc.sh config/config_wordcloud.json  -> explicit config
set -e
if command -v conda >/dev/null 2>&1; then
    source "$(conda info --base)/etc/profile.d/conda.sh"
    conda activate learn-better 2>/dev/null || true
fi
python code/make_wordcloud.py "$@"

#!/usr/bin/env bash
# Activate the learn-better conda env (Linux/macOS equivalent of c.bat).
# Usage:  source c.sh   (must be sourced, not run, so the env stays active)
# In Docker/Codespaces without conda, deps are already on the base python — skip this.
if command -v conda >/dev/null 2>&1; then
    # shellcheck disable=SC1091
    source "$(conda info --base)/etc/profile.d/conda.sh"
    conda activate learn-better
else
    echo "conda not found — assuming the current python already has the deps"
fi

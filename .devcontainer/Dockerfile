# See here for image contents: https://github.com/microsoft/vscode-dev-containers/tree/v0.245.0/containers/python-3/.devcontainer/base.Dockerfile

# [Choice] Python version + OS. Current devcontainer images live under
# mcr.microsoft.com/devcontainers/python (the old vscode/devcontainers/... path
# and the 0- / -bullseye tags are retired and 404 on pull). Use bookworm/trixie.
ARG VARIANT="3.12-bookworm"
FROM mcr.microsoft.com/devcontainers/python:${VARIANT}

# Install ffmpeg: a SYSTEM dependency yt-dlp/faster-whisper need to convert/merge
# audio (e.g. to mp3). It is NOT pip-installable, so the base image lacks it and
# audio steps fail without this layer. (See how_to_deploy.md — the #1 setup gap.)
RUN apt-get update \
    && apt-get install -y --no-install-recommends ffmpeg \
    && rm -rf /var/lib/apt/lists/*

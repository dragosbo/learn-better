"""Download transcripts for the videos in a playlist / channel / search.

Thin entry script: the real logic lives in lib/ (see lib/youtube.py). This file
is just configuration + a main() that wires the lib functions together.

Method: yt-dlp downloads the subtitle track directly and handles
cookies/proxies/anti-bot, so it avoids the `ParseError: no element found`
(empty body) that youtube-transcript-api hits on corporate/proxied networks.

For each video it saves one cleaned, timestamped .txt per available language:
    data/transcripts/<title> [<id>].<lang>.txt
Files already present are skipped. Languages come from code/languages.json.

Usage (from the repo root, with the learn-better env active):
    python code/read_transcript.py
"""

import os
import sys

# Make the repo root importable so `from lib import ...` works when this script
# is run as `python code/read_transcript.py` (which puts code/ on the path,
# not the repo root).
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib import net, textutil, youtube  # noqa: E402
from lib.paths import TRANSCRIPT_DIR      # noqa: E402

# ---------------------------------------------------------------------------
# Source: fill in ONE (playlist, then channel, then search is used).
#   PLAYLIST_ID - part after "list=" in a playlist URL.
#   CHANNEL     - "@handle", a "UC..." id, or a full channel URL.
#   SEARCH      - text you'd type into YouTube search.
# ---------------------------------------------------------------------------
PLAYLIST_ID = "PLsWyhklHwjExuXrXjJktcdYkCFL0PNdW7"  # or None
CHANNEL = None
SEARCH = None
LIMIT = 5                      # max videos to process (never more than this)

# Cookies / proxy live in lib.net (COOKIES_FILE auto-detects code/cookies.txt,
# NO_PROXY=True by default). Override here if needed, e.g.:
#   net.COOKIES_FROM_BROWSER = ("chrome", None)


def main():
    net.apply_no_proxy_env()
    languages = textutil.load_languages()
    print(f"Languages (from languages.json): {languages}\n")

    label, url = youtube.build_url(playlist_id=PLAYLIST_ID, channel=CHANNEL,
                                   search=SEARCH, limit=LIMIT)
    if url is None:
        print("No source set. Fill in PLAYLIST_ID, CHANNEL, or SEARCH.")
        return

    print(f"Listing up to {LIMIT} video(s) from {label} ...")
    videos = youtube.list_videos(url, limit=LIMIT)
    if not videos:
        print("No videos returned. Is the playlist/channel PUBLIC and non-empty?")
        return

    print(f"\nProcessing {len(videos)} video(s) (max {LIMIT})...\n")
    no_transcript = []
    for i, (vid, title) in enumerate(videos, 1):
        print(f"--- [{i}/{len(videos)}] {title} ({vid}) ---")
        saved = youtube.download_transcript(vid, title, languages,
                                            output_dir=TRANSCRIPT_DIR)
        # Treat "already on disk" as success, not a missing transcript.
        base = textutil.safe_filename(f"{title} [{vid}]")
        on_disk = any(os.path.exists(os.path.join(TRANSCRIPT_DIR,
                      f"{base}.{lang}.txt")) for lang in languages)
        if not saved and not on_disk:
            no_transcript.append((vid, title))
        print()

    print("=" * 60)
    print(f"Done. Processed {len(videos)} video(s).")
    if no_transcript:
        print(f"{len(no_transcript)} had NO transcript in {languages}:")
        for vid, title in no_transcript:
            print(f"  - {title} ({vid})")
    else:
        print(f"All videos have at least one transcript in {languages}.")


if __name__ == "__main__":
    main()

"""Read a playlist / channel / search WITHOUT an API key: transcripts + audio.

Thin entry script: the real logic lives in lib/ (see lib/youtube.py). This file
is configuration + a main() that runs, for each video:
  - STEP 2: download transcripts (one cleaned, timestamped .txt per language)
  - STEP 3: download the audio (mp3)
(STEP 1 is listing the videos.)

Everything uses yt-dlp (no Google API key). Files already on disk are skipped,
so re-running only fetches what's missing.

Usage (from the repo root, with your env activated):
    python code/read_channel.py
"""

import os
import sys

# Make the repo root importable so `from lib import ...` works when run as
# `python code/read_channel.py`.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib import net, textutil, youtube  # noqa: E402
from lib.paths import AUDIO_DIR, TRANSCRIPT_DIR  # noqa: E402

# ---------------------------------------------------------------------------
# Config: fill in ONE source, keep LIMIT small while testing.
#   PLAYLIST_ID - part after "list=" in a playlist URL.
#   CHANNEL     - "@handle", a "UC..." id, or a full channel URL.
#   SEARCH      - any text you'd type into the YouTube search box.
# The FIRST source that is set wins (playlist, then channel, then search).
# ---------------------------------------------------------------------------
PLAYLIST_ID = "PLsWyhklHwjExuXrXjJktcdYkCFL0PNdW7"  # or None
CHANNEL = None               # e.g. "@dragosborosgpt" or "UCtXMX2QDtGA__BoLNIu4o5w"
SEARCH = None                # e.g. "Manolis Kellis Lex Fridman"
LIMIT = 5                    # max videos to process (never more than this)

# STEP 3 download settings
DOWNLOAD = True              # set False to skip the audio download step
AUDIO_FORMAT = "mp3"         # or None to keep native webm/m4a (no ffmpeg needed)
AUDIO_QUALITY = "192"        # mp3 bitrate in kbps (only used when AUDIO_FORMAT set)

# Cookies / proxy live in lib.net (COOKIES_FILE auto-detects code/cookies.txt,
# NO_PROXY=True). Override here if needed, e.g.:
#   net.COOKIES_FROM_BROWSER = ("chrome", None)


def main():
    net.apply_no_proxy_env()
    languages = textutil.load_languages()
    print(f"Languages (from languages.json): {languages}")

    label, url = youtube.build_url(playlist_id=PLAYLIST_ID, channel=CHANNEL,
                                   search=SEARCH, limit=LIMIT)
    if url is None:
        print("STEP 1: no source set. Fill in PLAYLIST_ID, CHANNEL, or SEARCH.")
        return

    print(f"STEP 1: listing up to {LIMIT} video(s) from {label} ...")
    videos = youtube.list_videos(url, limit=LIMIT)
    if not videos:
        print("STEP 1: no videos returned. Is the playlist/channel PUBLIC and "
              "non-empty?")
        return

    print(f"\nProcessing {len(videos)} clip(s) (max {LIMIT})...\n")
    missing_transcripts = []
    for i, (vid, title) in enumerate(videos, 1):
        print(f"--- [{i}/{len(videos)}] {title} ({vid}) ---")

        # STEP 2 - transcripts. Treat "already on disk" as success.
        saved = youtube.download_transcript(vid, title, languages,
                                            output_dir=TRANSCRIPT_DIR)
        base = textutil.safe_filename(f"{title} [{vid}]")
        on_disk = any(os.path.exists(os.path.join(TRANSCRIPT_DIR,
                      f"{base}.{lang}.txt")) for lang in languages)
        if not saved and not on_disk:
            missing_transcripts.append((vid, title))

        # STEP 3 - audio.
        if DOWNLOAD:
            youtube.download_audio(vid, output_dir=AUDIO_DIR,
                                   audio_format=AUDIO_FORMAT,
                                   audio_quality=AUDIO_QUALITY)
        print()

    print("=" * 60)
    print(f"Done. Processed {len(videos)} clip(s).")
    if missing_transcripts:
        print(f"{len(missing_transcripts)} clip(s) had NO transcript:")
        for vid, title in missing_transcripts:
            print(f"  - {title} ({vid})")
    else:
        print("All processed clips had a transcript.")


if __name__ == "__main__":
    main()

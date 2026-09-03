"""List all public playlists of a YouTube channel WITHOUT an API key.

Phase A of mini_todo.md. Thin entry script: the yt-dlp work lives in
lib/youtube.py; this file is config + presentation (table, progress, JSON).

For the configured CHANNEL it:
  - lists every public playlist (title, id, availability, video count),
  - optionally fetches each playlist's videos to get an accurate count + names,
  - saves everything to data/playlists.json,
  - optionally prints one playlist's videos (LIST_VIDEOS_FOR).

Only PUBLIC playlists are visible without authentication. See the README
("Making playlists visible to the tool") for how to make playlists public.

Usage (from the repo root, with the learn-better env active):
    python code/list_playlists.py
"""

import json
import os
import sys

# Make the repo root importable so `from lib import ...` works when run as
# `python code/list_playlists.py`.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib import net, youtube  # noqa: E402
from lib.paths import DATA_DIR  # noqa: E402

# ---------------------------------------------------------------------------
# Config
#   CHANNEL         - an "@handle", a "UC..." id, or a full channel URL.
#   LIST_VIDEOS_FOR - set to a "PL..." id to also print that playlist's videos.
#   COUNT_VIDEOS    - open each playlist to get an accurate count + video names
#                     (one request each; slower). False = fast, no exact counts.
# ---------------------------------------------------------------------------
CHANNEL = "@dragosborosgpt"         # or "UCtXMX2QDtGA__BoLNIu4o5w" or a full URL
LIST_VIDEOS_FOR = None              # e.g. "PLsWyhklHwjExuXrXjJktcdYkCFL0PNdW7"
VIDEO_LIMIT = 5                     # how many videos to show for LIST_VIDEOS_FOR
COUNT_VIDEOS = True

OUTPUT_JSON = os.path.join(DATA_DIR, "playlists.json")

# Cookies / proxy live in lib.net. Override here if needed, e.g.:
#   net.COOKIES_FROM_BROWSER = ("chrome", None)


def print_and_count(channel=CHANNEL):
    """List the channel's playlists, fill in accurate counts, print, return."""
    print(f"Listing playlists for {channel}\n"
          f"  via {youtube.playlists_url(channel)}\n")

    playlists, meta = youtube.list_playlists(channel)

    if meta.get("error") is not None:
        err = meta["error"]
        print(f"Failed to list playlists - {type(err).__name__}: {err}")
        msg = str(err).lower()
        if "404" in msg or "not found" in msg:
            print("\n  A 404 usually means the CHANNEL doesn't exist. Check the\n"
                  "  handle/id at the top of this script - open the channel in\n"
                  "  your browser and copy the exact '@handle' from the URL.")
        elif "cookie database" in msg or "could not copy" in msg:
            print("\n  Chrome locks its cookie database while running. Export a\n"
                  "  cookies.txt instead (see README) and save as code/cookies.txt.")
        return []

    if not playlists:
        print("No playlists returned. Is the channel correct and does it have "
              "PUBLIC playlists? (Private/unlisted playlists are not visible.)")
        return []

    if meta.get("incomplete"):
        print("  NOTE: yt-dlp had trouble reading the playlists page, so this\n"
              "  list may be INCOMPLETE (some playlists could be missing). Try\n"
              "  again; totals can differ between runs. Compare with\n"
              "  studio.youtube.com -> Content -> Playlists for the true total.\n")

    # Sort alphabetically by title (case-insensitive).
    playlists.sort(key=lambda p: (p["title"] or "").lower())

    # Accurate counts + video names (one request per playlist), with live
    # progress so it doesn't look frozen.
    if COUNT_VIDEOS:
        total = len(playlists)
        print(f"Counting videos in {total} playlist(s) "
              f"(one request each; set COUNT_VIDEOS=False to skip)...")
        for i, p in enumerate(playlists, 1):
            title = (p["title"] or "")[:40]
            print(f"  [{i:>3}/{total}] {title:<40}", end="\r", flush=True)
            videos = youtube.fetch_playlist_videos(p["id"])
            if videos is not None:
                p["count"] = len(videos)
                p["videos"] = videos
        print(" " * 60, end="\r")
        print(f"Counted {total} playlist(s).\n")

    print(f"Found {len(playlists)} playlist(s):\n")
    for p in playlists:
        count = p["count"] if p["count"] is not None else "?"
        avail = p["availability"] or "public?"
        print(f"  {str(count):>4} videos  [{avail:<8}]  "
              f"{p['id'] or '(no id)':<40}  {p['title']}")

    non_public = [p for p in playlists
                  if p["availability"] and p["availability"] != "public"]
    if non_public:
        print(f"\n  {len(non_public)} non-public playlist(s) visible "
              f"(thanks to cookies):")
        for p in non_public:
            print(f"    [{p['availability']}] {p['title']}")
    return playlists


def save_playlists(playlists, path=OUTPUT_JSON):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    payload = {"channel": CHANNEL, "count": len(playlists), "playlists": playlists}
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)
    print(f"\nSaved {len(playlists)} playlist(s) -> {path}")


def main():
    net.apply_no_proxy_env()
    playlists = print_and_count()
    if not playlists:
        return
    save_playlists(playlists)
    if LIST_VIDEOS_FOR:
        print(f"\nListing up to {VIDEO_LIMIT} video(s) from "
              f"playlist {LIST_VIDEOS_FOR} ...")
        url = f"https://www.youtube.com/playlist?list={LIST_VIDEOS_FOR}"
        youtube.list_videos(url, limit=VIDEO_LIMIT)


if __name__ == "__main__":
    main()

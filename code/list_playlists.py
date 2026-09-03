"""List all public playlists of a YouTube channel WITHOUT an API key.

Phase A of mini_todo.md. Uses only yt-dlp (extract_flat) to read a channel's
`/playlists` page, so there is no Google API key and no secrets.json involved.

For the configured CHANNEL it:
  - A1: prints every public playlist (title, id, video count),
  - A2: saves them to data/playlists.json,
  - A3: optionally lists the videos of one playlist (set LIST_VIDEOS_FOR).

The network helpers (proxy / cookies / browser impersonation) are copied from
test_read_channel.py so this script stands alone. Phase B will move them into a
shared lib/ module and de-duplicate.

Usage (from the repo root, with the learn-better env active):
    python code/list_playlists.py
"""

import json
import os

from yt_dlp import YoutubeDL

# ---------------------------------------------------------------------------
# Config
#
# CHANNEL: an "@handle" (e.g. "@dragosborosgpt"), a "UC..." channel id, or a
#          full channel URL. This is the channel whose playlists we list.
#          (Find your handle at youtube.com -> your avatar -> your channel.)
#
# LIST_VIDEOS_FOR: set to a playlist id (the "PL..." value) to also print that
#          playlist's first few videos (A3). Leave None to skip.
# ---------------------------------------------------------------------------
CHANNEL = "@dragosborosgpt"         # or "UCtXMX2QDtGA__BoLNIu4o5w" or a full URL
LIST_VIDEOS_FOR = None              # e.g. "PLsWyhklHwjExuXrXjJktcdYkCFL0PNdW7"
VIDEO_LIMIT = 5                     # how many videos to show for LIST_VIDEOS_FOR

# The channel /playlists page (extract_flat) often does NOT report a reliable
# video count. When COUNT_VIDEOS is True, we open each playlist to count its
# videos exactly (one extra lightweight request per playlist, so a bit slower).
# Set to False for a fast listing when you don't need accurate counts.
COUNT_VIDEOS = True

DATA_DIR = "data"                   # where playlists.json is written (git-ignored)
OUTPUT_JSON = os.path.join(DATA_DIR, "playlists.json")

# ---------------------------------------------------------------------------
# Cookies for yt-dlp (only needed if YouTube shows "Sign in to confirm you're
# not a bot", common on cloud IPs). Set ONE; leave the other None.
#   COOKIES_FILE         - path to a Netscape cookies.txt (e.g. "code/cookies.txt")
#   COOKIES_FROM_BROWSER - a tuple like ("chrome", None)
# ---------------------------------------------------------------------------
# Default: no cookies (works fine for PUBLIC playlists, which is the common
# case). Cookies are only needed to TRY to see private/unlisted playlists.
#   - To try that: export a code/cookies.txt (install "Get cookies.txt LOCALLY"
#     in Chrome, export youtube.com while logged in) - it's auto-detected below.
#   - Reading straight from Chrome via COOKIES_FROM_BROWSER = ("chrome", None)
#     works too, but Chrome LOCKS its cookie DB while running on Windows, so it
#     often fails with "Could not copy Chrome cookie database". The cookies.txt
#     route avoids that entirely, so it's preferred.
COOKIES_FROM_BROWSER = None
COOKIES_FILE = "code/cookies.txt" if os.path.exists("code/cookies.txt") else None

# Force a direct connection, ignoring any HTTP_PROXY/HTTPS_PROXY env vars.
NO_PROXY = True
PROXY_URL = None


# ---- network helpers (copied from test_read_channel.py; deduped in Phase B) --
def _cookie_opts():
    opts = {}
    if COOKIES_FILE:
        opts["cookiefile"] = COOKIES_FILE
    elif COOKIES_FROM_BROWSER:
        opts["cookiesfrombrowser"] = COOKIES_FROM_BROWSER
    return opts


def _proxy_opts():
    if NO_PROXY:
        return {"proxy": ""}
    if PROXY_URL:
        return {"proxy": PROXY_URL}
    return {}


def _apply_no_proxy_env():
    if not NO_PROXY:
        return
    for var in ("HTTP_PROXY", "HTTPS_PROXY", "http_proxy", "https_proxy",
                "ALL_PROXY", "all_proxy"):
        os.environ.pop(var, None)


def _impersonate_opts():
    """yt-dlp browser-impersonation opts (needs curl_cffi); empty if absent."""
    try:
        import curl_cffi  # noqa: F401
        from yt_dlp.networking.impersonate import ImpersonateTarget
        return {"impersonate": ImpersonateTarget()}
    except Exception:
        return {}


def _net_opts():
    """Merge the shared yt-dlp network options."""
    return {**_proxy_opts(), **_cookie_opts(), **_impersonate_opts()}


_apply_no_proxy_env()


# ---------------------------------------------------------------------------
# URL building
# ---------------------------------------------------------------------------
def _playlists_url(channel):
    """Return the channel's /playlists page URL for any accepted CHANNEL form."""
    if channel.startswith("http"):
        # Accept a full channel URL; ensure it points at the playlists tab.
        base = channel.rstrip("/")
        return base if base.endswith("/playlists") else f"{base}/playlists"
    if channel.startswith("@"):
        return f"https://www.youtube.com/{channel}/playlists"
    if channel.startswith("UC"):
        return f"https://www.youtube.com/channel/{channel}/playlists"
    # Bare name -> treat as a handle.
    return f"https://www.youtube.com/@{channel}/playlists"


def fetch_playlist_videos(playlist_id):
    """Return the playlist's videos as [{id, title}], or None on failure.

    Uses a lightweight extract_flat pass (lists entries without downloading),
    so it's one cheap request per playlist. The count is just len() of this,
    and the same call gives us the video titles for the JSON output.
    """
    if not playlist_id:
        return None
    url = f"https://www.youtube.com/playlist?list={playlist_id}"

    # Silence yt-dlp's own warnings here (e.g. "N unavailable videos are
    # hidden") - those are expected and just noise. A null logger swallows
    # them; we only care about the playable entries.
    class _NullLogger:
        def debug(self, m): pass
        def info(self, m): pass
        def warning(self, m): pass
        def error(self, m): pass

    opts = {
        "quiet": True,
        "extract_flat": True,
        "skip_download": True,
        "ignoreerrors": True,
        "logger": _NullLogger(),
        # Bound the time spent on any single playlist so one slow/hanging
        # request can't stall the whole run (this was making it "go forever").
        "socket_timeout": 20,     # per-connection timeout in seconds
        "retries": 2,             # limited network retries
        "extractor_retries": 1,   # don't retry the extractor many times
        **_net_opts(),
    }
    try:
        with YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=False)
    except Exception:
        return None
    if not info:
        return None
    videos = []
    for e in (info.get("entries") or []):
        if e and e.get("id"):
            videos.append({"id": e.get("id"),
                           "title": e.get("title", "(no title)")})
    return videos


# ---------------------------------------------------------------------------
# A1 - list the channel's playlists
# ---------------------------------------------------------------------------
def list_playlists(channel=CHANNEL):
    """Return [{title, id, url, count, availability, videos}] for the channel.

    `videos` is a list of {id, title} when COUNT_VIDEOS is on (populated by the
    per-playlist pass), otherwise None.
    """
    url = _playlists_url(channel)
    print(f"Listing playlists for {channel}\n  via {url}\n")

    # Track whether yt-dlp emitted any warnings while paging the playlists tab.
    # If it did, pagination may have stopped early and the list can be
    # INCOMPLETE (this is why the total sometimes varies between runs). We
    # capture warnings via a tiny logger and surface a clear note afterwards.
    warnings_seen = []

    class _WarnLogger:
        def debug(self, m): pass
        def info(self, m): pass
        def warning(self, m): warnings_seen.append(m)
        def error(self, m): warnings_seen.append(m)

    opts = {
        "quiet": True,
        "extract_flat": True,     # don't resolve each playlist, just list them
        "skip_download": True,
        # Robustness: page the playlists tab more persistently so we don't
        # silently drop playlists when a continuation request hiccups.
        "extractor_retries": 5,   # retry the extractor's own page fetches
        "retries": 5,             # retry network reads
        "socket_timeout": 30,
        "logger": _WarnLogger(),  # capture warnings instead of spamming stdout
        **_net_opts(),
    }
    try:
        with YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=False)
    except Exception as err:
        print(f"Failed to list playlists - {type(err).__name__}: {err}")
        msg = str(err).lower()
        if "404" in msg or "not found" in msg:
            print("\n  A 404 usually means the CHANNEL doesn't exist. Check the\n"
                  "  handle/id at the top of this script - open the channel in\n"
                  "  your browser and copy the exact '@handle' from the URL\n"
                  "  (e.g. youtube.com/@yourhandle), or use the 'UC...' id.")
        elif "cookie database" in msg or "could not copy" in msg:
            print("\n  Chrome locks its cookie database while running. Either:\n"
                  "   (a) fully close Chrome (incl. tray/background processes in\n"
                  "       Task Manager), then re-run; or\n"
                  "   (b) export a cookies.txt: install 'Get cookies.txt LOCALLY'\n"
                  "       in Chrome, export youtube.com while logged in, save as\n"
                  "       code/cookies.txt - this script auto-detects it and\n"
                  "       avoids the lock entirely.")
        return []

    playlists = []
    seen_ids = set()
    for entry in (info.get("entries") or []):
        if not entry:
            continue
        pid = entry.get("id")
        # Skip duplicates (pagination can return the same playlist twice).
        if pid and pid in seen_ids:
            continue
        if pid:
            seen_ids.add(pid)
        title = entry.get("title", "(untitled)")
        # yt-dlp exposes the count under different keys depending on version.
        count = (entry.get("playlist_count")
                 or entry.get("video_count")
                 or entry.get("n_entries"))
        # availability is "public" / "unlisted" / "private" when yt-dlp knows it
        # (often only when authenticated via cookies). None if unreported.
        availability = entry.get("availability")
        purl = entry.get("url") or (
            f"https://www.youtube.com/playlist?list={pid}" if pid else None)
        playlists.append({"title": title, "id": pid, "url": purl,
                          "count": count, "availability": availability,
                          "videos": None})

    if not playlists:
        print("No playlists returned. Is the channel correct and does it have "
              "PUBLIC playlists? (Private/unlisted playlists are not visible.)")
        return []

    # If yt-dlp warned while paging the tab, the list may be incomplete - which
    # is the usual reason the total varies between runs. Say so plainly.
    page_warnings = [w for w in warnings_seen
                     if "initial data" in w.lower()
                     or "retrying" in w.lower()
                     or "giving up" in w.lower()]
    if page_warnings:
        print("  NOTE: yt-dlp had trouble reading the playlists page, so this\n"
              "  list may be INCOMPLETE (some playlists could be missing). Try\n"
              "  running again; counts/totals can differ between runs when this\n"
              "  happens. Compare with studio.youtube.com -> Content -> Playlists\n"
              "  for the authoritative total.\n")

    # Sort alphabetically by title (case-insensitive) so the output is stable
    # and easy to scan; applies to both the console table and the saved JSON.
    playlists.sort(key=lambda p: (p["title"] or "").lower())

    # The flat listing's count is unreliable, so (when enabled) open each
    # playlist to get its exact video list. This is one extra request per
    # playlist - a bit slower, but we then have trustworthy counts AND each
    # video's id/title (saved to the JSON). Set COUNT_VIDEOS=False to skip.
    if COUNT_VIDEOS:
        total = len(playlists)
        print(f"Counting videos in {total} playlist(s) "
              f"(one request each; set COUNT_VIDEOS=False to skip)...")
        for i, p in enumerate(playlists, 1):
            # Live progress on ONE rewritten line so you can see it working and
            # estimate remaining time (each playlist is one network request).
            title = (p["title"] or "")[:40]
            print(f"  [{i:>3}/{total}] {title:<40}", end="\r", flush=True)
            videos = fetch_playlist_videos(p["id"])
            if videos is not None:
                p["count"] = len(videos)
                p["videos"] = videos      # [{id, title}, ...] -> saved to JSON
        print(" " * 60, end="\r")   # clear the progress line
        print(f"Counted {total} playlist(s).\n")

    # Print a simple aligned table, including availability so you can see
    # whether any unlisted/private playlists surfaced (they usually only do
    # when authenticated via cookies).
    print(f"Found {len(playlists)} playlist(s):\n")
    for p in playlists:
        count = p["count"] if p["count"] is not None else "?"
        avail = p["availability"] or "public?"
        print(f"  {str(count):>4} videos  [{avail:<8}]  "
              f"{p['id'] or '(no id)':<40}  {p['title']}")

    # Highlight any non-public playlists that cookies made visible.
    non_public = [p for p in playlists
                  if p["availability"] and p["availability"] != "public"]
    if non_public:
        print(f"\n  {len(non_public)} non-public playlist(s) visible "
              f"(thanks to cookies):")
        for p in non_public:
            print(f"    [{p['availability']}] {p['title']}")
    return playlists


# ---------------------------------------------------------------------------
# A2 - save to data/playlists.json
# ---------------------------------------------------------------------------
def save_playlists(playlists, path=OUTPUT_JSON):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    payload = {"channel": CHANNEL, "count": len(playlists), "playlists": playlists}
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)
    print(f"\nSaved {len(playlists)} playlist(s) -> {path}")


# ---------------------------------------------------------------------------
# A3 - list the videos of a single playlist (optional)
# ---------------------------------------------------------------------------
def list_playlist_videos(playlist_id, limit=VIDEO_LIMIT):
    """Return [(video_id, title)] for up to `limit` videos in a playlist."""
    url = f"https://www.youtube.com/playlist?list={playlist_id}"
    print(f"\nListing up to {limit} video(s) from playlist {playlist_id} ...")
    opts = {
        "quiet": True,
        "extract_flat": True,
        "skip_download": True,
        "playlistend": limit,
        **_net_opts(),
    }
    try:
        with YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=False)
    except Exception as err:
        print(f"Failed to list videos - {type(err).__name__}: {err}")
        return []

    out = []
    for entry in (info.get("entries") or [])[:limit]:
        if entry:
            out.append((entry.get("id"), entry.get("title", "(no title)")))
            print(f"   {out[-1][0]}  {out[-1][1]}")
    if not out:
        print("   No videos returned. Is the playlist PUBLIC and non-empty?")
    return out


def main():
    playlists = list_playlists()
    if not playlists:
        return
    save_playlists(playlists)
    if LIST_VIDEOS_FOR:
        list_playlist_videos(LIST_VIDEOS_FOR)


if __name__ == "__main__":
    main()

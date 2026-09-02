"""Download transcripts for the videos in a playlist / channel / search.

Method: yt-dlp. It downloads the subtitle track directly and handles
cookies/proxies/anti-bot the same way a video download does, so it avoids the
`ParseError: no element found` (empty body) that youtube-transcript-api hits on
corporate/proxied networks even when captions clearly exist.

For each video it saves one cleaned, timestamped .txt per available language:
    transcripts/<title> [<id>].<lang>.txt
Files already present are skipped (no re-download).

Languages come from code/languages.json (English, French, Romanian by default).

Usage (from the repo root, with the learn-better env active):
    python code/test_read_transcript.py
"""

import html
import json
import os
import re

from yt_dlp import YoutubeDL

# ---------------------------------------------------------------------------
# Source: fill in ONE (playlist, then channel, then search is used). Same
# shape as test_read_channel.py so both tools behave consistently.
#
#   PLAYLIST_ID - part after "list=" in a playlist URL.
#   CHANNEL     - "@handle", a "UC..." id, or a full channel URL.
#   SEARCH      - text you'd type into YouTube search.
# ---------------------------------------------------------------------------
PLAYLIST_ID = "PLsWyhklHwjExuXrXjJktcdYkCFL0PNdW7"  # or None
CHANNEL = None
SEARCH = None
LIMIT = 5                      # max videos to process (never more than this)

TRANSCRIPT_DIR = "transcripts"

# Subtitle languages are read from this JSON config (English, French, Romanian
# by default). Only languages that actually exist for a video are downloaded.
LANGUAGES_CONFIG = os.path.join(os.path.dirname(__file__), "languages.json")

# Cookies help when YouTube blocks anonymous requests. Set ONE (or leave both
# None to try without). COOKIES_FROM_BROWSER is a tuple like ("chrome", None);
# COOKIES_FILE is a path to a Netscape cookies.txt.
COOKIES_FROM_BROWSER = None       # e.g. ("chrome", None)
COOKIES_FILE = "code/cookies.txt" if os.path.exists("code/cookies.txt") else None

# Force a direct connection, ignoring any HTTP_PROXY/HTTPS_PROXY env vars.
NO_PROXY = True


def load_languages(path=LANGUAGES_CONFIG):
    """Read the preferred subtitle languages from languages.json."""
    try:
        with open(path, encoding="utf-8") as f:
            langs = json.load(f).get("languages")
        if isinstance(langs, list) and langs:
            return [str(x) for x in langs]
    except Exception as err:
        print(f"(could not read {path}: {err}; using defaults)")
    return ["en", "fr", "ro"]


def _apply_no_proxy_env():
    if not NO_PROXY:
        return
    for var in ("HTTP_PROXY", "HTTPS_PROXY", "http_proxy", "https_proxy",
                "ALL_PROXY", "all_proxy"):
        os.environ.pop(var, None)


def _safe_filename(name):
    """Strip characters that are illegal in Windows filenames."""
    return "".join(c for c in name if c not in '\\/:*?"<>|').strip()


def _net_opts():
    """Shared yt-dlp options: proxy bypass, cookies, browser impersonation."""
    opts = {}
    if NO_PROXY:
        opts["proxy"] = ""
    if COOKIES_FILE:
        opts["cookiefile"] = COOKIES_FILE
    elif COOKIES_FROM_BROWSER:
        opts["cookiesfrombrowser"] = COOKIES_FROM_BROWSER
    # yt-dlp needs to "impersonate" a real browser (TLS fingerprint) to fetch
    # subtitle data; otherwise the response is empty. Needs curl_cffi
    # (pip install "yt-dlp[default,curl-cffi]"). Pass an ImpersonateTarget()
    # instance (the string "chrome" raises a bare AssertionError; empty lets
    # yt-dlp auto-pick an available target).
    try:
        import curl_cffi  # noqa: F401
        from yt_dlp.networking.impersonate import ImpersonateTarget
        opts["impersonate"] = ImpersonateTarget()
    except Exception:
        pass
    return opts


# ---------------------------------------------------------------------------
# List videos from the configured source (same approach as test_read_channel).
# ---------------------------------------------------------------------------
def _build_url():
    if PLAYLIST_ID:
        return (f"playlist {PLAYLIST_ID}",
                f"https://www.youtube.com/playlist?list={PLAYLIST_ID}")
    if CHANNEL:
        if CHANNEL.startswith("http"):
            url = CHANNEL
        elif CHANNEL.startswith("@"):
            url = f"https://www.youtube.com/{CHANNEL}/videos"
        elif CHANNEL.startswith("UC"):
            url = f"https://www.youtube.com/channel/{CHANNEL}/videos"
        else:
            url = f"https://www.youtube.com/@{CHANNEL}/videos"
        return f"channel {CHANNEL}", url
    if SEARCH:
        return f"search {SEARCH!r}", f"ytsearch{LIMIT}:{SEARCH}"
    return None, None


def list_videos(limit=LIMIT):
    """Return [(video_id, title), ...] for up to `limit` videos."""
    label, url = _build_url()
    if url is None:
        print("No source set. Fill in PLAYLIST_ID, CHANNEL, or SEARCH.")
        return []

    print(f"Listing up to {limit} video(s) from {label} ...")
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
        print("No videos returned. Is the playlist/channel PUBLIC and non-empty?")
    return out


# ---------------------------------------------------------------------------
# VTT -> readable, timestamped text.
# ---------------------------------------------------------------------------
# Matches a VTT timing line, e.g. "00:00:04.799 --> 00:00:06.950 align:start ..."
# capturing the start time "HH:MM:SS" (or "MM:SS"), dropping milliseconds.
_TIMING_RE = re.compile(r"^\s*(\d{1,2}:\d{2}(?::\d{2})?)[.,]\d{3}\s*-->")


def _clean_text(raw):
    """Strip VTT/HTML tags, decode entities, normalize whitespace on one line."""
    text = re.sub(r"<[^>]+>", "", raw)          # drop <...> tags
    text = html.unescape(text)                  # &nbsp; &amp; &#39; -> chars
    text = text.replace("\u00a0", " ")          # nbsp -> normal space
    return re.sub(r"\s+", " ", text).strip()


def _vtt_to_text(vtt_path):
    """Convert a WebVTT subtitle file into readable, timestamped lines.

    One line per cue: "[HH:MM:SS] text", e.g.

        [00:00:04] Salut a tous, je m'appelle Moss
        [00:00:06] et bienvenue dans cette serie de tutoriels

    Same format for every language. Strips tags, decodes HTML entities,
    collapses whitespace, and drops consecutively repeated lines (common in
    auto-captions).
    """
    with open(vtt_path, encoding="utf-8") as f:
        lines = f.read().splitlines()

    out = []
    current_ts = None
    last_text = None
    for line in lines:
        stripped = line.strip()
        m = _TIMING_RE.match(line)
        if m:
            current_ts = m.group(1)
            continue
        if (not stripped
                or stripped.startswith("WEBVTT")
                or stripped.startswith(("Kind:", "Language:", "NOTE"))
                or stripped.isdigit()):
            continue
        text = _clean_text(line)
        if not text or text == last_text:
            continue
        out.append(f"[{current_ts or '00:00:00'}] {text}")
        last_text = text
    return "\n".join(out)


# ---------------------------------------------------------------------------
# Download transcript(s) for ONE video.
# ---------------------------------------------------------------------------
def download_transcript(video_id, title, languages, output_dir=TRANSCRIPT_DIR):
    os.makedirs(output_dir, exist_ok=True)
    base = _safe_filename(f"{title} [{video_id}]") if title else video_id

    # Skip only the languages already saved; still fetch any that are missing.
    missing = [lang for lang in languages
               if not os.path.exists(os.path.join(output_dir, f"{base}.{lang}.txt"))]
    if not missing:
        print(f"   all requested transcripts already exist (skip)")
        return []

    url = f"https://www.youtube.com/watch?v={video_id}"
    opts = {
        "quiet": True,
        "skip_download": True,
        "writesubtitles": True,
        "writeautomaticsub": True,
        "subtitleslangs": list(missing),
        "subtitlesformat": "vtt",
        "outtmpl": os.path.join(output_dir, f"{base}.%(ext)s"),
        **_net_opts(),
    }

    try:
        with YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=True)
    except Exception as err:
        print(f"   !! yt-dlp failed ({type(err).__name__}): {err}")
        return []

    # Collect each .vtt yt-dlp wrote (one per language actually available).
    vtt_by_lang = {}
    for lang, sub in (info.get("requested_subtitles") or {}).items():
        fp = sub.get("filepath")
        if fp and os.path.exists(fp):
            vtt_by_lang[lang] = fp
    if not vtt_by_lang:
        prefix = f"{base}."
        for name in os.listdir(output_dir):
            if name.startswith(prefix) and name.endswith(".vtt"):
                vtt_by_lang[name[len(prefix):-len(".vtt")]] = \
                    os.path.join(output_dir, name)

    if not vtt_by_lang:
        print(f"   !! no transcript found in {missing} for this video")
        return []

    saved = []
    for lang, vtt_path in sorted(vtt_by_lang.items()):
        text = _vtt_to_text(vtt_path)
        txt_path = os.path.join(output_dir, f"{base}.{lang}.txt")
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(text)
        os.remove(vtt_path)
        print(f"   saved [{lang}] {len(text)} chars -> {txt_path}")
        saved.append(txt_path)
    return saved


# ---------------------------------------------------------------------------
# Process every listed video (capped at LIMIT).
# ---------------------------------------------------------------------------
def main():
    _apply_no_proxy_env()
    languages = load_languages()
    print(f"Languages (from languages.json): {languages}\n")

    videos = list_videos()
    if not videos:
        return

    print(f"\nProcessing {len(videos)} video(s) (max {LIMIT})...\n")
    no_transcript = []
    for i, (vid, title) in enumerate(videos, 1):
        print(f"--- [{i}/{len(videos)}] {title} ({vid}) ---")
        saved = download_transcript(vid, title, languages)
        if not saved and not any(
            os.path.exists(os.path.join(TRANSCRIPT_DIR,
                           f"{_safe_filename(f'{title} [{vid}]')}.{lang}.txt"))
            for lang in languages
        ):
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

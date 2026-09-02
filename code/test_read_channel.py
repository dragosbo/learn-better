"""Quick, incremental sandbox for reading YouTube data WITHOUT an API key.

Uses only yt-dlp (no Google API key) to, for each video in a playlist /
channel / search:
  - STEP 2: download transcripts (one cleaned, timestamped .txt per language)
  - STEP 3: download the audio (mp3)

Why yt-dlp for transcripts too: youtube-transcript-api hits
`ParseError: no element found` (empty body) on corporate/proxied networks even
when captions exist. yt-dlp handles cookies/proxy/anti-bot the same way the
audio download does, so it is far more reliable.

Languages come from code/languages.json (shared with test_read_transcript.py).

Run the whole file, or copy blocks into a Jupyter cell, to test one step at a
time. Each step prints its result so you can see exactly where something breaks.

Usage (from the repo root, with your env activated):
    python code/test_read_channel.py
"""

import html
import json
import os
import re

from yt_dlp import YoutubeDL

# ---------------------------------------------------------------------------
# Config: fill in ONE source, keep LIMIT small while testing.
#
# HOW TO FIND THESE (all from youtube.com in your browser, no login/API needed):
#   PLAYLIST_ID - open a playlist, copy the part after "list=" in the URL:
#                 youtube.com/playlist?list=PLxxxxxxxx  ->  "PLxxxxxxxx"
#   CHANNEL     - the @handle (e.g. "@dragosboros_rapid") or the UC... id, or a
#                 full channel URL.
#   SEARCH      - any text you'd type into the YouTube search box.
#
# The script uses the FIRST source that is set (playlist, then channel, then
# search). Leave the others as None.
# ---------------------------------------------------------------------------
PLAYLIST_ID = "PLsWyhklHwjExuXrXjJktcdYkCFL0PNdW7"  # or None
CHANNEL = None               # e.g. "@dragosboros_rapid" or "UCtXMX2QDtGA__BoLNIu4o5w"
SEARCH = None                # e.g. "Manolis Kellis Lex Fridman"
LIMIT = 5                    # max videos to process (never more than this)

# STEP 3 download settings
DOWNLOAD = True              # set False to skip the download step
AUDIO_DIR = "audio"          # folder where audio files are saved (git-ignored)
TRANSCRIPT_DIR = "transcripts"  # folder where transcript .txt files are saved

# Subtitle languages are read from this shared JSON config (English, French,
# Romanian by default). Only languages that exist for a video are saved.
LANGUAGES_CONFIG = os.path.join(os.path.dirname(__file__), "languages.json")

# Audio format for STEP 3. YouTube's "bestaudio" stream is usually .webm
# (Opus) or .m4a (AAC) - neither is mp3. Setting AUDIO_FORMAT = "mp3" tells
# yt-dlp to run its FFmpegExtractAudio postprocessor after downloading, which
# transcodes the raw stream to mp3. This REQUIRES ffmpeg to be installed and
# on your PATH (https://ffmpeg.org/download.html - on Windows the easiest way
# is `winget install ffmpeg` or `choco install ffmpeg`, then restart your
# terminal). Set AUDIO_FORMAT = None to keep whatever format yt-dlp downloads
# natively (no ffmpeg needed, but you get webm/m4a instead of mp3).
AUDIO_FORMAT = "mp3"         # or None
AUDIO_QUALITY = "192"        # mp3 bitrate in kbps (only used when AUDIO_FORMAT is set)

# ---------------------------------------------------------------------------
# Cookies for yt-dlp (needed when YouTube shows "Sign in to confirm you're
# not a bot"). Set ONE of these; leave the other as None. Both are optional -
# if neither is set, yt-dlp runs anonymously and may hit the bot-check.
#
#   COOKIES_FROM_BROWSER - easiest option. A tuple: (browser, profile).
#       profile can be None to use the browser's default profile.
#       Examples:
#         ("chrome", None)        -> Chrome, default profile
#         ("edge", None)          -> Edge, default profile
#         ("firefox", "default")  -> Firefox, profile named "default"
#       You must be logged into YouTube in that browser. Close the browser
#       first on Windows if you get a "database is locked" error.
#
#   COOKIES_FILE - path to a cookies.txt exported in Netscape format (e.g.
#       via the "Get cookies.txt LOCALLY" browser extension while logged
#       into youtube.com). Use this if COOKIES_FROM_BROWSER doesn't work
#       (locked profile, remote/headless machine, etc.).
#       Example: "code/cookies.txt"
# ---------------------------------------------------------------------------
COOKIES_FROM_BROWSER = None              # or e.g. ("chrome", None)
COOKIES_FILE = "code/cookies.txt"        # or None

# NOTE: COOKIES_FROM_BROWSER makes yt-dlp open Chrome's live cookie database
# file directly. On Windows, Chrome locks that file while it's running, so
# yt-dlp fails with "Could not copy Chrome cookie database" unless Chrome is
# fully closed first (including background processes). COOKIES_FILE avoids
# that entirely: export once with a "Get cookies.txt LOCALLY" browser
# extension while logged into youtube.com, save as code/cookies.txt, and
# you're done - no need to close the browser on every run. It's also the
# only option youtube_transcript_api (STEP 2) can use, since that library
# has no "read from browser" support at all.

# ---------------------------------------------------------------------------
# Proxy handling. Some machines (often corporate laptops) have HTTP_PROXY /
# HTTPS_PROXY env vars set system-wide, and yt-dlp picks those up
# automatically. If that proxy needs auth you haven't configured (407 Proxy
# Authentication Required), the simplest fix is to tell yt-dlp to bypass any
# proxy entirely and connect directly. NO_PROXY = True does that.
#
# If you actually need to go through a proxy, set NO_PROXY = False and put
# the full proxy URL (with credentials if required) in PROXY_URL, e.g.
#   PROXY_URL = "http://user:pass@proxyhost:8080"
# ---------------------------------------------------------------------------
NO_PROXY = True        # force a direct connection, ignoring env var proxies
PROXY_URL = None        # only used when NO_PROXY is False


def _cookie_opts():
    """Return the yt-dlp option(s) needed to attach browser cookies, if any."""
    opts = {}
    if COOKIES_FILE:
        opts["cookiefile"] = COOKIES_FILE
    elif COOKIES_FROM_BROWSER:
        opts["cookiesfrombrowser"] = COOKIES_FROM_BROWSER
    return opts


def _proxy_opts():
    """Return the yt-dlp option(s) controlling proxy use.

    Passing "proxy": "" explicitly tells yt-dlp/urllib to use NO proxy,
    overriding any HTTP_PROXY/HTTPS_PROXY environment variables that would
    otherwise be picked up automatically.
    """
    if NO_PROXY:
        return {"proxy": ""}
    if PROXY_URL:
        return {"proxy": PROXY_URL}
    return {}


def _apply_no_proxy_env():
    """If NO_PROXY, strip proxy env vars for this process.

    yt-dlp's own "proxy": "" opt only affects yt-dlp's requests. STEP 2 uses
    youtube_transcript_api, which goes through `requests` and reads
    HTTP_PROXY/HTTPS_PROXY (and lowercase variants) from the environment
    directly. Clearing them here makes ALL steps bypass the proxy, not just
    the yt-dlp-based ones.
    """
    if not NO_PROXY:
        return
    for var in ("HTTP_PROXY", "HTTPS_PROXY", "http_proxy", "https_proxy",
                "ALL_PROXY", "all_proxy"):
        os.environ.pop(var, None)


_apply_no_proxy_env()


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


def _impersonate_opts():
    """yt-dlp browser-impersonation opts (needs curl_cffi); empty if absent.

    Required so YouTube returns subtitle data instead of an empty body. Pass an
    ImpersonateTarget() instance (the string "chrome" raises AssertionError;
    empty lets yt-dlp auto-pick an available target).
    """
    try:
        import curl_cffi  # noqa: F401
        from yt_dlp.networking.impersonate import ImpersonateTarget
        return {"impersonate": ImpersonateTarget()}
    except Exception:
        return {}


def _build_url():
    """Return (label, url) for the first configured source, or (None, None)."""
    if PLAYLIST_ID:
        url = f"https://www.youtube.com/playlist?list={PLAYLIST_ID}"
        return f"playlist {PLAYLIST_ID}", url
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
        # ytsearchN: is yt-dlp's built-in search; N caps the results.
        return f"search {SEARCH!r}", f"ytsearch{LIMIT}:{SEARCH}"
    return None, None


# ---------------------------------------------------------------------------
# STEP 1 - list a few videos from whichever source is set. No API key.
# extract_flat avoids downloading; it just reads the entry list quickly.
# ---------------------------------------------------------------------------
def step1_list_videos(limit=LIMIT):
    label, url = _build_url()
    if url is None:
        print("STEP 1: no source set. Fill in PLAYLIST_ID, CHANNEL, or SEARCH.")
        return []

    print(f"STEP 1: listing up to {limit} video(s) from {label} ...")
    opts = {
        "quiet": True,
        "extract_flat": True,      # don't resolve each video, just list them
        "skip_download": True,
        "playlistend": limit,      # only fetch the first `limit` entries
        **_proxy_opts(),
    }
    try:
        with YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=False)
    except Exception as err:
        print(f"STEP 1: failed to list - {type(err).__name__}: {err}")
        return []

    entries = info.get("entries") or []
    out = []
    for entry in entries[:limit]:
        if not entry:
            continue
        vid = entry.get("id")
        title = entry.get("title", "(title unavailable)")
        out.append((vid, title))
        print(f"        {vid}  {title}")

    if not out:
        print("STEP 1: no videos returned. Is the playlist/channel PUBLIC and "
              "non-empty?")
    return out


# ---------------------------------------------------------------------------
# STEP 2 - fetch transcript(s) for a single video id via yt-dlp. No API key.
#
# We use yt-dlp (NOT youtube-transcript-api) for the same reason STEP 1 and
# STEP 3 do: it reuses the same cookie / proxy / browser-impersonation options,
# so it avoids the empty-body `ParseError` youtube-transcript-api hits on
# corporate/proxied networks. This mirrors test_read_transcript.py, saving one
# cleaned, timestamped .txt per available language:
#     transcripts/<title> [<id>].<lang>.txt
# ---------------------------------------------------------------------------
def _safe_filename(name):
    """Strip characters that are illegal in Windows filenames."""
    return "".join(c for c in name if c not in '\\/:*?"<>|').strip()


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

    One line per cue: "[HH:MM:SS] text". Strips tags, decodes HTML entities,
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


def step2_transcript(video_id, title="", languages=("en", "fr", "ro"),
                     output_dir=TRANSCRIPT_DIR):
    os.makedirs(output_dir, exist_ok=True)
    base = _safe_filename(f"{title} [{video_id}]") if title else video_id

    # Skip only the languages already saved; still fetch any that are missing.
    missing = [lang for lang in languages
               if not os.path.exists(
                   os.path.join(output_dir, f"{base}.{lang}.txt"))]
    if not missing:
        print(f"STEP 2: {video_id} all requested transcripts already exist "
              f"(skip)")
        return [os.path.join(output_dir, f"{base}.{lang}.txt")
                for lang in languages]

    url = f"https://www.youtube.com/watch?v={video_id}"
    opts = {
        "quiet": True,
        "skip_download": True,
        "writesubtitles": True,
        "writeautomaticsub": True,
        "subtitleslangs": list(missing),
        "subtitlesformat": "vtt",
        "outtmpl": os.path.join(output_dir, f"{base}.%(ext)s"),
        **_cookie_opts(),
        **_proxy_opts(),
        **_impersonate_opts(),
    }
    try:
        with YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=True)
    except Exception as err:
        print(f"STEP 2: !! yt-dlp failed for {video_id} "
              f"({type(err).__name__}): {err}")
        return None

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
        print(f"STEP 2: !! NO TRANSCRIPT for {video_id} in {missing} "
              f"- subtitles likely disabled")
        return None

    saved = []
    for lang, vtt_path in sorted(vtt_by_lang.items()):
        text = _vtt_to_text(vtt_path)
        txt_path = os.path.join(output_dir, f"{base}.{lang}.txt")
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(text)
        os.remove(vtt_path)
        print(f"STEP 2: {video_id} saved [{lang}] {len(text)} chars "
              f"-> {txt_path}")
        saved.append(txt_path)
    return saved


# ---------------------------------------------------------------------------
# STEP 3 - actually DOWNLOAD the audio of one video to AUDIO_DIR. No API key.
# Extracts the best audio-only stream (usually .webm or .m4a) and saves it
# named after the video title. If AUDIO_FORMAT is set (e.g. "mp3"), yt-dlp
# transcodes it to that format via ffmpeg after downloading. Requires yt-dlp
# (already in requirements) and, when AUDIO_FORMAT is set, ffmpeg on PATH.
# ---------------------------------------------------------------------------
def step3_download_audio(video_id, output_dir=AUDIO_DIR):
    os.makedirs(output_dir, exist_ok=True)

    # Skip if we already have an audio file for this video id. The filename
    # embeds "[<video_id>]", so we match on that regardless of the title.
    # target_ext is the final extension we expect (mp3 when converting, else
    # any audio file for this id).
    target_ext = AUDIO_FORMAT if AUDIO_FORMAT else None
    for existing in os.listdir(output_dir):
        if f"[{video_id}]" in existing:
            if target_ext is None or existing.lower().endswith(f".{target_ext}"):
                print(f"STEP 3: {video_id} audio already exists -> "
                      f"{os.path.join(output_dir, existing)} (skip)")
                return os.path.join(output_dir, existing)

    url = f"https://www.youtube.com/watch?v={video_id}"
    opts = {
        "quiet": True,
        "format": "bestaudio/best",
        # Save as "<title> [<id>].<ext>" inside output_dir.
        "outtmpl": os.path.join(output_dir, "%(title)s [%(id)s].%(ext)s"),
        **_cookie_opts(),
        **_proxy_opts(),
    }
    if AUDIO_FORMAT:
        # Runs ffmpeg after the raw download to transcode to AUDIO_FORMAT
        # (e.g. mp3) and deletes the original webm/m4a, so you end up with
        # just the .mp3. Needs ffmpeg installed and on PATH - if it's
        # missing, yt-dlp will raise an error naming ffmpeg explicitly.
        opts["postprocessors"] = [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": AUDIO_FORMAT,
            "preferredquality": AUDIO_QUALITY,
        }]
    print(f"STEP 3: downloading audio for {video_id} into '{output_dir}/' ...")
    try:
        with YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=True)
            path = ydl.prepare_filename(info)
            if AUDIO_FORMAT:
                # prepare_filename() still reports the pre-conversion name/ext
                # (e.g. ".webm"); the postprocessor renames the file on disk
                # to AUDIO_FORMAT, so fix up the extension to match reality.
                path = os.path.splitext(path)[0] + f".{AUDIO_FORMAT}"
        print(f"STEP 3: saved -> {path}")
        return path
    except Exception as err:
        print(f"STEP 3: download failed - {type(err).__name__}: {err}")
        return None


# ---------------------------------------------------------------------------
# Run the steps for EVERY listed clip (capped at LIMIT, never more than that):
#   STEP 2 - save its transcript (or signal that none exists)
#   STEP 3 - download its audio (skipping any already downloaded)
# ---------------------------------------------------------------------------
def main():
    languages = load_languages()
    print(f"Languages (from languages.json): {languages}")

    videos = step1_list_videos()
    if not videos:
        return

    print(f"\nProcessing {len(videos)} clip(s) (max {LIMIT})...\n")
    missing_transcripts = []
    for i, (vid, title) in enumerate(videos, 1):
        print(f"--- [{i}/{len(videos)}] {title} ({vid}) ---")
        if step2_transcript(vid, title=title, languages=languages) is None:
            missing_transcripts.append((vid, title))
        if DOWNLOAD:
            step3_download_audio(vid)
        print()

    # Summary: make the "no transcript" clips easy to spot.
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

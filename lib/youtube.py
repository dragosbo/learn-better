"""Core YouTube operations via yt-dlp (no API key).

Behavior-preserving extraction of the proven logic from the entry scripts:
  build_url            - source (playlist/channel/search) -> (label, url)
  list_videos          - list up to `limit` videos from a source url
  list_playlists       - list a channel's public playlists (+ optional counts)
  fetch_playlist_videos- one playlist's videos as [{id, title}]
  download_transcript  - save one cleaned, timestamped .txt per language
  download_audio       - download bestaudio (optionally transcode to mp3)

All network options come from lib.net; text cleaning from lib.textutil; output
folders from lib.paths.
"""

import os

from yt_dlp import YoutubeDL

from . import net
from . import textutil
from . import paths


# ---------------------------------------------------------------------------
# URL building
# ---------------------------------------------------------------------------
def build_url(playlist_id=None, channel=None, search=None, limit=5):
    """Return (label, url) for the first configured source, or (None, None).

    Precedence matches the original scripts: playlist, then channel, then
    search. `limit` only affects the search form (ytsearchN).
    """
    if playlist_id:
        url = f"https://www.youtube.com/playlist?list={playlist_id}"
        return f"playlist {playlist_id}", url
    if channel:
        if channel.startswith("http"):
            url = channel
        elif channel.startswith("@"):
            url = f"https://www.youtube.com/{channel}/videos"
        elif channel.startswith("UC"):
            url = f"https://www.youtube.com/channel/{channel}/videos"
        else:
            url = f"https://www.youtube.com/@{channel}/videos"
        return f"channel {channel}", url
    if search:
        # ytsearchN: is yt-dlp's built-in search; N caps the results.
        return f"search {search!r}", f"ytsearch{limit}:{search}"
    return None, None


def playlists_url(channel):
    """Return the channel's /playlists page URL for any accepted CHANNEL form."""
    if channel.startswith("http"):
        base = channel.rstrip("/")
        return base if base.endswith("/playlists") else f"{base}/playlists"
    if channel.startswith("@"):
        return f"https://www.youtube.com/{channel}/playlists"
    if channel.startswith("UC"):
        return f"https://www.youtube.com/channel/{channel}/playlists"
    return f"https://www.youtube.com/@{channel}/playlists"


# ---------------------------------------------------------------------------
# Listing videos from a source (playlist / channel / search)
# ---------------------------------------------------------------------------
def list_videos(url, limit=5):
    """Return [(video_id, title)] for up to `limit` videos from `url`.

    Uses extract_flat (fast, no per-video resolution). Prints each as it goes,
    matching the original STEP 1 output.
    """
    opts = {
        "quiet": True,
        "extract_flat": True,
        "skip_download": True,
        "playlistend": limit,
        **net.proxy_opts(),
    }
    try:
        with YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=False)
    except Exception as err:
        print(f"        failed to list - {type(err).__name__}: {err}")
        return []

    out = []
    for entry in (info.get("entries") or [])[:limit]:
        if not entry:
            continue
        vid = entry.get("id")
        title = entry.get("title", "(title unavailable)")
        out.append((vid, title))
        print(f"        {vid}  {title}")
    return out


# ---------------------------------------------------------------------------
# Listing a channel's playlists (Phase A logic)
# ---------------------------------------------------------------------------
class _NullLogger:
    def debug(self, m): pass
    def info(self, m): pass
    def warning(self, m): pass
    def error(self, m): pass


def fetch_playlist_videos(playlist_id):
    """Return a playlist's videos as [{id, title}], or None on failure.

    Lightweight extract_flat pass (one request), with a per-request timeout and
    bounded retries so a single slow playlist can't hang a batch.
    """
    if not playlist_id:
        return None
    url = f"https://www.youtube.com/playlist?list={playlist_id}"
    opts = {
        "quiet": True,
        "extract_flat": True,
        "skip_download": True,
        "ignoreerrors": True,
        "logger": _NullLogger(),
        "socket_timeout": 20,
        "retries": 2,
        "extractor_retries": 1,
        **net.net_opts(),
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


def list_playlists(channel):
    """Return [{title, id, url, count, availability, videos}] for a channel.

    Only PUBLIC playlists are visible without authentication. `count` and
    `videos` are filled lazily by the caller (via fetch_playlist_videos) since
    the flat listing's count is unreliable. Returns the raw list plus a flag
    for whether the listing looked incomplete.
    """
    url = playlists_url(channel)

    warnings_seen = []

    class _WarnLogger:
        def debug(self, m): pass
        def info(self, m): pass
        def warning(self, m): warnings_seen.append(m)
        def error(self, m): warnings_seen.append(m)

    opts = {
        "quiet": True,
        "extract_flat": True,
        "skip_download": True,
        "extractor_retries": 5,
        "retries": 5,
        "socket_timeout": 30,
        "logger": _WarnLogger(),
        **net.net_opts(),
    }
    try:
        with YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=False)
    except Exception as err:
        return [], {"error": err, "warnings": warnings_seen}

    playlists = []
    seen_ids = set()
    for entry in (info.get("entries") or []):
        if not entry:
            continue
        pid = entry.get("id")
        if pid and pid in seen_ids:
            continue
        if pid:
            seen_ids.add(pid)
        count = (entry.get("playlist_count")
                 or entry.get("video_count")
                 or entry.get("n_entries"))
        purl = entry.get("url") or (
            f"https://www.youtube.com/playlist?list={pid}" if pid else None)
        playlists.append({"title": entry.get("title", "(untitled)"),
                          "id": pid, "url": purl, "count": count,
                          "availability": entry.get("availability"),
                          "videos": None})

    page_warnings = [w for w in warnings_seen
                     if "initial data" in w.lower()
                     or "retrying" in w.lower()
                     or "giving up" in w.lower()]
    return playlists, {"error": None, "warnings": warnings_seen,
                       "incomplete": bool(page_warnings)}


# ---------------------------------------------------------------------------
# Download a transcript (subtitles) for one video, one .txt per language
# ---------------------------------------------------------------------------
def download_transcript(video_id, title, languages, output_dir=None):
    """Save cleaned, timestamped transcripts for a video, one .txt per language.

    Returns a list of saved paths, [] if none/failed. Skips languages already
    on disk. Uses yt-dlp subtitles (reliable across proxied networks).
    """
    output_dir = output_dir or paths.TRANSCRIPT_DIR
    os.makedirs(output_dir, exist_ok=True)
    base = textutil.safe_filename(f"{title} [{video_id}]") if title else video_id

    missing = [lang for lang in languages
               if not os.path.exists(
                   os.path.join(output_dir, f"{base}.{lang}.txt"))]
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
        **net.net_opts(),
    }
    try:
        with YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=True)
    except Exception as err:
        print(f"   !! yt-dlp failed ({type(err).__name__}): {err}")
        return []

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
        text = textutil.vtt_to_text(vtt_path)
        txt_path = os.path.join(output_dir, f"{base}.{lang}.txt")
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(text)
        os.remove(vtt_path)
        print(f"   saved [{lang}] {len(text)} chars -> {txt_path}")
        saved.append(txt_path)
    return saved


# ---------------------------------------------------------------------------
# Download the audio of one video (optionally transcode to mp3)
# ---------------------------------------------------------------------------
def download_audio(video_id, output_dir=None, audio_format="mp3",
                   audio_quality="192"):
    """Download bestaudio for a video into output_dir, skip if already present.

    If audio_format is set (e.g. "mp3"), transcode via ffmpeg. Returns the saved
    path, or None on failure.
    """
    output_dir = output_dir or paths.AUDIO_DIR
    os.makedirs(output_dir, exist_ok=True)

    target_ext = audio_format if audio_format else None
    for existing in os.listdir(output_dir):
        if f"[{video_id}]" in existing:
            if target_ext is None or existing.lower().endswith(f".{target_ext}"):
                print(f"   audio already exists -> "
                      f"{os.path.join(output_dir, existing)} (skip)")
                return os.path.join(output_dir, existing)

    url = f"https://www.youtube.com/watch?v={video_id}"
    opts = {
        "quiet": True,
        "format": "bestaudio/best",
        "outtmpl": os.path.join(output_dir, "%(title)s [%(id)s].%(ext)s"),
        **net.cookie_opts(),
        **net.proxy_opts(),
    }
    if audio_format:
        opts["postprocessors"] = [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": audio_format,
            "preferredquality": audio_quality,
        }]
    print(f"   downloading audio for {video_id} into '{output_dir}/' ...")
    try:
        with YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=True)
            path = ydl.prepare_filename(info)
            if audio_format:
                path = os.path.splitext(path)[0] + f".{audio_format}"
        print(f"   saved -> {path}")
        return path
    except Exception as err:
        print(f"   download failed - {type(err).__name__}: {err}")
        return None

"""Phase C: transcribe selected audio files with Whisper, no API key.

Transcribes one or more audio files from `data/audio/` with faster-whisper and
saves each result to `data/generated_transcripts/` using a name derived from the
AUDIO FILE, not a generic hard-coded name. For:
    data/audio/Git and GitHub Tutorial for Beginners [tRZGeaHPoaw].mp3
it writes:
    data/generated_transcripts/Git and GitHub Tutorial for Beginners [tRZGeaHPoaw].whisper.en.txt

The `.whisper.<lang>.` marker keeps these Whisper transcripts distinct from the
YouTube-caption transcripts in `data/transcripts/`. Only one language per run in this
phase (the detected language, or LANGUAGE if you pin it).

TASK controls transcribe vs. translate:
  - TASK = "transcribe": text in the audio's ORIGINAL language (French audio ->
    French text). Output name uses the detected/pinned language.
  - TASK = "translate": Whisper translates to ENGLISH ONLY. This is a fixed model
    capability, it CANNOT target French/Romanian/etc. A French or Romanian clip
    therefore yields an English transcript, always named `.whisper.en.txt`.

Selecting which files to process (set SELECT_BY + SELECT below):
  - SELECT_BY = "name": SELECT is a list of case-insensitive substrings matched
    against the audio file NAME, e.g. ["Git and GitHub", "GitLab Pipeline"].
  - SELECT_BY = "id":   SELECT is a list of YouTube video ids matched against the
    `[<id>]` embedded in each audio file name, e.g. ["tRZGeaHPoaw"]. These ids
    are exactly the `id` values in data/playlists.json, so you can copy them
    straight from there.
  - SELECT_BY = "all":  transcribe every audio file (ignores SELECT). Slow; use
    only when you really want the whole data/audio/ folder.
  - SELECT_BY = "source": the C3 use case. Instead of local files, take a
    playlist/channel/search, and for each video first try the YouTube caption
    transcript; only clips with NO caption transcript get their audio downloaded
    (or reused from data/audio/) and Whisper-transcribed. Driven by the SOURCE_*
    config keys (playlist_id / channel / search / limit / languages), not SELECT.

Uses faster-whisper (CTranslate2 backend): faster and lighter than
openai-whisper, CPU-friendly, and can also translate (task="translate").
Needs the `faster-whisper` package and ffmpeg (already installed for the
downloaders). See install instructions in the chat / README.

Usage (from the repo root, with the learn-better env active):
    python code/transcribe_audio.py                              # in-file defaults below
    python code/transcribe_audio.py config/config_transcribe.json    # load a JSON config
    python code/transcribe_audio.py config/config_transcribe.id.json # by video id

A JSON config may set any of: select_by, select, model_size, device,
compute_type, task, language. Keys it omits keep the in-file defaults. If no
argument is given and config/config_transcribe.json exists, it is loaded
automatically; otherwise the in-file defaults are used.

First run downloads the model weights (a few hundred MB for "base"), so it may
take a minute before transcription starts. Transcription itself is CPU-bound.
Bump MODEL_SIZE to "small"/"medium" for better accuracy, slower.

Re-running skips any file that already has a matching transcript in
data/generated_transcripts/ (skip-if-exists), so it is cheap to run again.
"""

import json
import os
import re
import sys

# Make the repo root importable so `from lib import ...` works when this script
# is run as `python code/transcribe_audio.py`.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Strip corporate HTTP_PROXY/HTTPS_PROXY/NO_PROXY env vars BEFORE importing
# anything that makes network calls. faster-whisper downloads the model from
# Hugging Face via httpx, and a malformed proxy value in the environment (seen
# as `httpx.InvalidURL: Invalid port: '...;localhost'`) crashes that download.
# lib.net.apply_no_proxy_env() clears those vars for this process, the same fix
# the yt-dlp scripts already use.
from lib import net  # noqa: E402
from lib import paths  # noqa: E402
from lib import youtube  # noqa: E402
from lib.textutil import safe_filename  # noqa: E402

net.apply_no_proxy_env()

from faster_whisper import WhisperModel  # noqa: E402

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AUDIO_DIR = os.path.join(_REPO_ROOT, paths.AUDIO_DIR)
OUTPUT_DIR = os.path.join(_REPO_ROOT, paths.GENERATED_TRANSCRIPT_DIR)

# Which audio files to transcribe. See the module docstring for the modes.
SELECT_BY = "name"       # "name" | "id" | "all" | "source"
SELECT = [               # substrings (name) or video ids (id); ignored for "all"/"source"
    "Git and GitHub",
]

# For SELECT_BY = "source" (C3): pick ONE source, leave the others None.
SOURCE_PLAYLIST_ID = None    # a playlist id, e.g. "PLxxxx"
SOURCE_CHANNEL = None        # a channel: "@handle", "UC...", or full URL
SOURCE_SEARCH = None         # a search string
SOURCE_LIMIT = 5             # max videos to consider from the source
# Caption languages to try before falling back to Whisper. None = languages.json.
SOURCE_LANGUAGES = None

AUDIO_EXTS = (".mp3", ".m4a", ".webm", ".wav", ".opus")

# Whisper settings.
MODEL_SIZE = "base"      # tiny | base | small | medium | large-v3 (bigger = slower, better)
DEVICE = "cpu"           # "cuda" if you have a working GPU + CUDA
COMPUTE_TYPE = "int8"    # int8 is fast + low-memory on CPU
TASK = "transcribe"      # "translate" would produce English from any language
LANGUAGE = None          # None = auto-detect; or pin e.g. "en"

# The `[<id>]` YouTube ids embed in downloaded file names, e.g. "... [tRZGeaHPoaw].mp3".
_ID_IN_NAME_RE = re.compile(r"\[([A-Za-z0-9_-]{11})\]")

# Config keys allowed in a JSON config, mapped to the module globals they set.
_CONFIG_KEYS = {
    "select_by": "SELECT_BY",
    "select": "SELECT",
    "model_size": "MODEL_SIZE",
    "device": "DEVICE",
    "compute_type": "COMPUTE_TYPE",
    "task": "TASK",
    "language": "LANGUAGE",
    # SELECT_BY = "source" (C3) keys:
    "playlist_id": "SOURCE_PLAYLIST_ID",
    "channel": "SOURCE_CHANNEL",
    "search": "SOURCE_SEARCH",
    "limit": "SOURCE_LIMIT",
    "languages": "SOURCE_LANGUAGES",
}
_DEFAULT_CONFIG = os.path.join("config", "config_transcribe.json")


def load_config(path):
    """Override the module-level settings from a JSON config file.

    Only the keys present in the file are applied; anything omitted keeps its
    in-file default. Keys starting with `_` (e.g. `_comment`) are ignored.
    """
    with open(path, encoding="utf-8") as f:
        cfg = json.load(f)
    applied = {}
    for key, value in cfg.items():
        if key.startswith("_"):
            continue
        if key not in _CONFIG_KEYS:
            print(f"  (ignoring unknown config key: {key!r})")
            continue
        globals()[_CONFIG_KEYS[key]] = value
        applied[key] = value
    return applied


def resolve_config_path():
    """Return the config path to load, or None to use in-file defaults.

    A path given on the command line wins; otherwise fall back to
    config/config_transcribe.json if it exists.
    """
    if len(sys.argv) > 1:
        return sys.argv[1]
    default = os.path.join(_REPO_ROOT, _DEFAULT_CONFIG)
    return default if os.path.exists(default) else None


def output_path_for(audio_name, language):
    """Build data/generated_transcripts/<base>.whisper.<lang>.txt from an audio name.

    <base> is the audio file name without its extension, so the transcript name
    tracks the audio file rather than a generic hard-coded name.
    """
    base = safe_filename(os.path.splitext(audio_name)[0])
    return os.path.join(OUTPUT_DIR, f"{base}.whisper.{language}.txt")


def list_audio_files():
    """All audio file names (not paths) in AUDIO_DIR."""
    if not os.path.isdir(AUDIO_DIR):
        return []
    return [f for f in os.listdir(AUDIO_DIR)
            if f.lower().endswith(AUDIO_EXTS)]


def pick_audio_files(select_by, select):
    """Return the audio file names to process, per the selection mode.

    - "all":  every audio file.
    - "name": files whose name contains any SELECT substring (case-insensitive).
    - "id":   files whose embedded `[<id>]` matches any SELECT video id.
    """
    files = list_audio_files()
    if select_by == "all":
        return sorted(files)

    if select_by == "name":
        wanted = [s.lower() for s in select]
        return sorted(f for f in files
                      if any(w in f.lower() for w in wanted))

    if select_by == "id":
        wanted = set(select)
        chosen = []
        for f in files:
            m = _ID_IN_NAME_RE.search(f)
            if m and m.group(1) in wanted:
                chosen.append(f)
        return sorted(chosen)

    raise ValueError(f"Unknown SELECT_BY: {select_by!r} (use name|id|all)")


def known_output_language():
    """The output language label we can know BEFORE decoding, or None.

    - task="translate": Whisper always outputs English, so the label is "en"
      regardless of the source language.
    - task="transcribe" with LANGUAGE pinned: the output is that language.
    - task="transcribe" with auto-detect: unknown until after decoding -> None.
    """
    if TASK == "translate":
        return "en"
    if LANGUAGE:
        return LANGUAGE
    return None


def existing_transcripts_for_base(base):
    """Return any already-present Whisper transcripts for a transcript base name.

    If we can know the output language up front (translate, or a pinned
    LANGUAGE) we check that exact target; otherwise we look for any
    `<base>.whisper.*.txt`.
    """
    if not os.path.isdir(OUTPUT_DIR):
        return []
    out_lang = known_output_language()
    if out_lang:
        p = os.path.join(OUTPUT_DIR, f"{base}.whisper.{out_lang}.txt")
        return [p] if os.path.exists(p) else []
    return [
        os.path.join(OUTPUT_DIR, f)
        for f in os.listdir(OUTPUT_DIR)
        if f.startswith(f"{base}.whisper.") and f.endswith(".txt")
    ]


def existing_transcripts(audio_name):
    """Whisper transcripts already present for a local audio file name."""
    base = safe_filename(os.path.splitext(audio_name)[0])
    return existing_transcripts_for_base(base)


def _transcribe_path(audio_path, base, model):
    """Run Whisper on `audio_path` and write data/generated_transcripts/<base>.whisper.<lang>.txt.

    `base` is the (already safe) transcript base name. Returns the output path,
    or None if it was skipped (already exists) / failed. Shared by the local-file
    flow and the source (C3) flow.
    """
    if not os.path.exists(audio_path):
        print(f"  ! audio not found, skipping: {audio_path}")
        return None

    already = existing_transcripts_for_base(base)
    if already:
        print(f"  = transcript exists, skipping: {os.path.basename(already[0])}")
        return None

    action = "Translating to English" if TASK == "translate" else "Transcribing"
    print(f"\n{action}:\n  {audio_path}")
    segments, info = model.transcribe(audio_path, task=TASK, language=LANGUAGE)
    detected = info.language
    print(f"  detected source language: {detected} "
          f"(probability {info.language_probability:.2f})")

    # Output language label: English for translate, else the detected/pinned lang.
    out_lang = "en" if TASK == "translate" else detected

    parts = []
    for seg in segments:
        parts.append(seg.text)
        print(f"    [{seg.start:6.1f}s] {seg.text.strip()[:70]}")

    transcript = " ".join(p.strip() for p in parts).strip()

    output_file = os.path.join(OUTPUT_DIR, f"{base}.whisper.{out_lang}.txt")
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(transcript)
    print(f"  -> {len(transcript)} chars written to:\n     {output_file}")
    return output_file


def transcribe_one(audio_name, model):
    """Transcribe a single local audio file (from AUDIO_DIR). Returns the output
    path, or None if skipped / failed."""
    audio_path = os.path.join(AUDIO_DIR, audio_name)
    base = safe_filename(os.path.splitext(audio_name)[0])
    return _transcribe_path(audio_path, base, model)


def load_model():
    print(f"\nLoading Whisper model '{MODEL_SIZE}' ({DEVICE}/{COMPUTE_TYPE})...")
    print("(first run downloads the model weights - this can take a minute)")
    return WhisperModel(MODEL_SIZE, device=DEVICE, compute_type=COMPUTE_TYPE)


def run_local_flow():
    """Modes name/id/all: transcribe files already in data/audio/."""
    selected = pick_audio_files(SELECT_BY, SELECT)
    if not selected:
        print(f"No audio files matched SELECT_BY={SELECT_BY!r} SELECT={SELECT!r}")
        print(f"(looked in {AUDIO_DIR})")
        return

    print(f"Selected {len(selected)} file(s) via SELECT_BY={SELECT_BY!r}:")
    for f in selected:
        print(f"  - {f}")

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    model = load_model()

    written = 0
    for name in selected:
        if transcribe_one(name, model):
            written += 1

    print(f"\nDone. {written} new transcript(s) written, "
          f"{len(selected) - written} skipped, in:\n  {OUTPUT_DIR}")


def run_source_flow():
    """Mode source (C3): for each video in a playlist/channel/search, use the
    YouTube caption transcript if it exists; only Whisper-transcribe the clips
    that have NO caption transcript, reusing/downloading their audio."""
    languages = SOURCE_LANGUAGES
    if not languages:
        from lib.textutil import load_languages
        languages = load_languages()

    label, url = youtube.build_url(playlist_id=SOURCE_PLAYLIST_ID,
                                   channel=SOURCE_CHANNEL,
                                   search=SOURCE_SEARCH,
                                   limit=SOURCE_LIMIT)
    if not url:
        print("SELECT_BY='source' but no source set. Set one of "
              "playlist_id / channel / search in the config.")
        return

    print(f"Source: {label}")
    print(f"Listing up to {SOURCE_LIMIT} video(s)...")
    videos = youtube.list_videos(url, limit=SOURCE_LIMIT)
    if not videos:
        print("No videos found for this source.")
        return

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    model = None  # lazily loaded only if a clip actually needs Whisper

    have_caption = 0
    whispered = 0
    skipped = 0
    for vid, title in videos:
        print(f"\n=== {title} ({vid}) ===")
        # 1) Try the YouTube caption transcript first.
        saved = youtube.download_transcript(vid, title, languages)
        base = safe_filename(f"{title} [{vid}]") if title else vid
        caption_dir = os.path.join(_REPO_ROOT, paths.TRANSCRIPT_DIR)
        has_existing_caption = any(
            f.startswith(f"{base}.") and f.endswith(".txt")
            for f in (os.listdir(caption_dir) if os.path.isdir(caption_dir) else [])
        )
        if saved or has_existing_caption:
            print("   caption transcript available -> no Whisper needed")
            have_caption += 1
            continue

        # 2) No caption transcript: ensure audio exists, then Whisper it.
        print("   NO caption transcript -> falling back to Whisper")
        audio_path = youtube.download_audio(vid, output_dir=AUDIO_DIR)
        if not audio_path or not os.path.exists(audio_path):
            print("   ! could not obtain audio, skipping")
            skipped += 1
            continue

        audio_base = safe_filename(os.path.splitext(os.path.basename(audio_path))[0])
        if model is None:
            model = load_model()
        if _transcribe_path(audio_path, audio_base, model):
            whispered += 1
        else:
            skipped += 1

    print(f"\nDone (source flow). {len(videos)} video(s): "
          f"{have_caption} had captions, {whispered} Whisper-transcribed, "
          f"{skipped} skipped.\nWhisper output in:\n  {OUTPUT_DIR}")


def main():
    config_path = resolve_config_path()
    if config_path:
        if not os.path.exists(config_path):
            print(f"Config file not found: {config_path}")
            return
        applied = load_config(config_path)
        print(f"Loaded config from {config_path}: {applied}")
    else:
        print("No config file; using in-file defaults.")

    if SELECT_BY == "source":
        run_source_flow()
    else:
        run_local_flow()


if __name__ == "__main__":
    main()

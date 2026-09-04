"""Audio re-encode / bitrate helper (todo item 4 from plan.md).

Re-encode existing audio (data/audio/*.mp3, .m4a, .webm, ...) to a chosen BITRATE
and FORMAT using ffmpeg, writing the results to a SEPARATE folder so the originals
are never touched. Re-encoding to a lower bitrate is lossy and irreversible, so
we always write to data/audio_reencoded/ and treat data/audio/ as read-only.

Input audio lives in:
    data/audio/<title> [<id>].mp3            (also .m4a / .webm / .opus / .ogg / .wav)
Output:
    data/audio_reencoded/<title> [<id>].<bitrate>.<ext>   e.g. ....64kbps.mp3

Free tooling only: this shells out to the ffmpeg binary the project already
requires (yt-dlp uses it for mp3 conversion; see README "Install ffmpeg"). No
new pip dependency, no API, no paid service. Default codec libmp3lame ships with
ffmpeg and plays everywhere.

Selecting which audio files to process (set SELECT_BY + SELECT below):
  - SELECT_BY = "name": audio files whose NAME contains any SELECT substring
    (case-insensitive), e.g. ["Git and GitHub", "GitLab"].
  - SELECT_BY = "id":   audio files matched by YouTube video id (the `[<id>]`
    in the file name), e.g. ["tRZGeaHPoaw"].
  - SELECT_BY = "all":  every audio file in data/audio/ (slow).

Usage (from the repo root, with the learn-better env active):
    python code/reencode_audio.py                          # in-file defaults / auto-config
    python code/reencode_audio.py config/config_reencode.json  # load a JSON config

A JSON config may set any of: select_by, select, bitrate, format, codec,
sample_rate, channels. Keys it omits keep the in-file defaults. If no argument
is given and config/config_reencode.json exists, it is loaded automatically;
otherwise the in-file defaults are used.

No extra pip deps: pure stdlib (subprocess, shutil, re, json).
"""

import json
import os
import re
import shutil
import subprocess
import sys

# Force UTF-8 stdout so non-ASCII audio titles (fr/ro, emoji) never crash the
# Windows cp1252 console when we print them.
try:
    sys.stdout.reconfigure(encoding="utf-8")
except (AttributeError, ValueError):
    pass

# Make the repo root importable so `from lib import ...` works when run as
# `python code/reencode_audio.py`.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from lib import paths  # noqa: E402

# ---------------------------------------------------------------------------
# Config. For R1 the defaults re-encode ONE file (the Git & GitHub clip) at 64k.
# See the module docstring for the selection modes and JSON-config keys.
# ---------------------------------------------------------------------------
_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AUDIO_DIR = os.path.join(_REPO_ROOT, paths.AUDIO_DIR)
OUTPUT_DIR = os.path.join(_REPO_ROOT, paths.AUDIO_REENCODED_DIR)

# Selection: what to process. See the module docstring for the modes.
SELECT_BY = "name"       # "name" | "id" | "all"
SELECT = ["Git and GitHub"]  # substrings (name) or video ids (id); ignored for all

BITRATE = "64k"          # target audio bitrate (ffmpeg -b:a), e.g. 64k / 128k / 96k
FORMAT = "mp3"           # output container/extension: mp3 | m4a | ogg | opus | wav
CODEC = "libmp3lame"     # audio encoder; libmp3lame is the free, universal default
SAMPLE_RATE = None       # ffmpeg -ar (e.g. 44100); None = keep source
CHANNELS = None          # ffmpeg -ac (e.g. 1 = mono to shrink size); None = keep source

# JSON config keys -> the module globals they set.
_CONFIG_KEYS = {
    "select_by": "SELECT_BY",
    "select": "SELECT",
    "bitrate": "BITRATE",
    "format": "FORMAT",
    "codec": "CODEC",
    "sample_rate": "SAMPLE_RATE",
    "channels": "CHANNELS",
}
_DEFAULT_CONFIG = os.path.join("config", "config_reencode.json")


def human_size(num_bytes):
    """Bytes -> a short human string, e.g. 9.5 MB / 812 KB."""
    size = float(num_bytes)
    for unit in ("B", "KB", "MB", "GB"):
        if size < 1024 or unit == "GB":
            return f"{size:.0f} {unit}" if unit in ("B", "KB") else f"{size:.1f} {unit}"
        size /= 1024

# Audio extensions we accept as input.
_AUDIO_EXTS = (".mp3", ".m4a", ".webm", ".opus", ".ogg", ".wav")
# The `[<id>]` YouTube id embedded in audio file names.
_ID_IN_NAME_RE = re.compile(r"\[([A-Za-z0-9_-]{11})\]")


def find_ffmpeg():
    """Locate the ffmpeg binary (PATH or active conda env). Return the path, or
    None after printing a clear install hint."""
    exe = shutil.which("ffmpeg")
    if exe:
        return exe
    print("!! ffmpeg not found on PATH.")
    print("   This tool re-encodes audio with ffmpeg (free, already used by "
          "yt-dlp). Install it, then re-run:")
    print("     conda install -c conda-forge ffmpeg -y   :: into the active env "
          "(recommended)")
    print("     winget install ffmpeg                     :: Windows, system-wide")
    print("     brew install ffmpeg                       :: macOS")
    print("     sudo apt install ffmpeg                    :: Debian / Ubuntu")
    print("   Then open a NEW terminal and verify: ffmpeg -version")
    return None


def normalize_bitrate(value):
    """Normalize a bitrate spec to (ffmpeg_flag, name_tag).

    Accepts '64k', '64000', 64 -> ffmpeg_flag '64k', name_tag '64kbps'.
    Returns (None, None) on nonsense so the caller can abort with a message.
    """
    s = str(value).strip().lower()
    m = re.fullmatch(r"(\d+)\s*k(?:bps|bit)?", s)   # "64k", "64kbps", "64kbit"
    if m:
        kbps = int(m.group(1))
    else:
        m = re.fullmatch(r"(\d+)", s)               # plain integer
        if not m:
            return None, None
        n = int(m.group(1))
        # A bare number >= 1000 is treated as bits/sec (64000 -> 64k).
        kbps = n // 1000 if n >= 1000 else n
    if kbps <= 0:
        return None, None
    return f"{kbps}k", f"{kbps}kbps"


def _audio_files():
    """Yield (abspath, filename) for every audio file in data/audio/."""
    if not os.path.isdir(AUDIO_DIR):
        return
    for f in sorted(os.listdir(AUDIO_DIR)):
        if f.lower().endswith(_AUDIO_EXTS):
            yield os.path.join(AUDIO_DIR, f), f


def pick_audio(select_by, select):
    """Return [(abspath, filename)] to process, per the selection mode."""
    files = list(_audio_files())

    def matches(fname):
        if select_by == "all":
            return True
        if select_by == "name":
            low = fname.lower()
            return any(s.lower() in low for s in select)
        if select_by == "id":
            m = _ID_IN_NAME_RE.search(fname)
            return bool(m and m.group(1) in set(select))
        return False  # unknown mode; main() validates SELECT_BY up front

    return [(a, f) for a, f in files if matches(f)]


def reencode_one(ffmpeg, src_abs, filename, ffmpeg_bitrate, name_tag):
    """Re-encode one audio file. Returns "written" | "skipped" | "failed"."""
    base = os.path.splitext(filename)[0]
    out_name = f"{base}.{name_tag}.{FORMAT}"
    out_path = os.path.join(OUTPUT_DIR, out_name)

    if os.path.exists(out_path):
        print(f"  = exists, skipping: {out_name}")
        return "skipped"

    # List-form command (no shell=True) so titles with spaces/accents/emoji are
    # safe. -vn drops any cover-art video stream; -y overwrites a stale partial.
    cmd = [ffmpeg, "-hide_banner", "-loglevel", "error", "-y",
           "-i", src_abs, "-vn", "-c:a", CODEC, "-b:a", ffmpeg_bitrate]
    if SAMPLE_RATE:
        cmd += ["-ar", str(SAMPLE_RATE)]
    if CHANNELS:
        cmd += ["-ac", str(CHANNELS)]
    cmd.append(out_path)

    print(f"  -> {name_tag} {FORMAT}: {out_name}")
    result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8",
                            errors="replace")
    if result.returncode != 0:
        reason = (result.stderr or "").strip().splitlines()
        reason = reason[-1] if reason else f"ffmpeg exit code {result.returncode}"
        print(f"  ! failed: {reason}")
        # Don't leave a half-written / zero-byte output behind.
        if os.path.exists(out_path):
            try:
                os.remove(out_path)
            except OSError:
                pass
        return "failed"

    src_size = os.path.getsize(src_abs)
    out_size = os.path.getsize(out_path)
    saved = (1 - out_size / src_size) * 100 if src_size else 0
    print(f"     {human_size(src_size)} -> {human_size(out_size)} "
          f"(saved {saved:.0f}%)")
    return "written"


def load_config(path):
    """Override module-level settings from a JSON config file. Only present keys
    are applied; `_comment`/unknown keys are ignored."""
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
    """CLI-arg config path wins; else config/config_reencode.json if present."""
    if len(sys.argv) > 1:
        return sys.argv[1]
    default = os.path.join(_REPO_ROOT, _DEFAULT_CONFIG)
    return default if os.path.exists(default) else None


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

    ffmpeg = find_ffmpeg()
    if not ffmpeg:
        return

    ffmpeg_bitrate, name_tag = normalize_bitrate(BITRATE)
    if not ffmpeg_bitrate:
        print(f"!! Invalid bitrate {BITRATE!r}. Use e.g. '64k', '128k', or 64000.")
        return

    if SELECT_BY not in ("name", "id", "all"):
        print(f"!! Invalid select_by {SELECT_BY!r}. Use one of: name | id | all.")
        return
    if SELECT_BY in ("name", "id") and not SELECT:
        print(f"!! select_by={SELECT_BY!r} needs a non-empty 'select' list "
              f"({'name substrings' if SELECT_BY == 'name' else 'video ids'}).")
        return

    selected = pick_audio(SELECT_BY, SELECT)
    if not selected:
        print(f"No audio matched SELECT_BY={SELECT_BY!r} SELECT={SELECT!r}")
        print(f"(looked in {AUDIO_DIR}\\)")
        return

    print(f"Selected {len(selected)} audio file(s) via SELECT_BY={SELECT_BY!r}, "
          f"target {ffmpeg_bitrate} {FORMAT} ({CODEC}):")
    for _abs, f in selected:
        print(f"  - {f}")

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    written = skipped = failed = 0
    for abspath, filename in selected:
        print(f"\n{filename}")
        status = reencode_one(ffmpeg, abspath, filename, ffmpeg_bitrate, name_tag)
        written += status == "written"
        skipped += status == "skipped"
        failed += status == "failed"

    print(f"\nDone. {written} re-encoded, {skipped} skipped, {failed} failed, in:"
          f"\n  {OUTPUT_DIR}")


if __name__ == "__main__":
    main()

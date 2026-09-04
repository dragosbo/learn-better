"""Text-to-Speech baseline (todo2 items 3, 6 — baseline only).

Read a TEXT source (a transcript, a Whisper transcript, or a summary), synthesize
narration with the free, local, CPU-only **Piper** engine, and write the audio to
a separate `tts_output/` folder. This mirrors Phase C (speech-to-text via
faster-whisper) in the opposite direction: text -> audio.

Input text lives in:
    transcripts/<title> [<id>].<lang>.txt            (YouTube captions)
    generated_transcripts/<title> [<id>].whisper.<lang>.txt  (Whisper)
    summaries/<title> [<id>].summary.md              (AI summaries; Markdown)
Output:
    tts_output/<base>.<voice>.wav   (e.g. ... .en_US-lessac-medium.wav)

Free tooling only: Piper is MIT-licensed, CPU-only, no GPU, no API key, no paid
service (`pip install piper-tts`). The voice model (a small .onnx) downloads on
first use into tts_output/.voices/ (same "first-run download" idea faster-whisper
uses). Optional mp3 output reuses the ffmpeg binary the project already requires.

This script drives the Piper **CLI** via subprocess (its interface is stable
across versions), and uses `python -m piper.download_voices` to fetch a voice.

Selecting which text to voice (set SELECT_BY + SELECT below):
  - SELECT_BY = "name": text files whose NAME contains any SELECT substring
    (case-insensitive), e.g. ["Git and GitHub"].
  - SELECT_BY = "id":   text files matched by YouTube video id (the `[<id>]` in
    the name), e.g. ["tRZGeaHPoaw"].
  - SELECT_BY = "all":  every text file in the three folders (slow).

When several text sources exist for one video, ONE is voiced per video id,
preferring: summary > caption transcript > Whisper transcript.

D0 decisions (recorded here per the plan):
  - New dep: piper-tts (MIT, CPU-only). ffmpeg only for optional mp3.
  - Output folder tts_output/ (git-ignored); name <base>.<voice>.<ext> so
    multiple voices coexist and skip-if-exists works.
  - summaries/*.summary.md is stripped of Markdown before synthesis.

Usage (from the repo root, with the learn-better env active):
    python code/generate_speech.py                       # in-file defaults / auto-config
    python code/generate_speech.py config/config_tts.json  # load a JSON config

A JSON config may set any of: select_by, select, engine, voice, format,
max_chars. Omitted keys keep the in-file defaults.

No extra pip deps beyond piper-tts: pure stdlib (re, json, subprocess, shutil).
"""

import json
import os
import re
import shutil
import subprocess
import sys

# Force UTF-8 stdout so non-ASCII titles (fr/ro, emoji, fullwidth) never crash
# the Windows cp1252 console when we print them.
try:
    sys.stdout.reconfigure(encoding="utf-8")
except (AttributeError, ValueError):
    pass

# Make the repo root importable so `from lib import ...` works when run as
# `python code/generate_speech.py`.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from lib import paths  # noqa: E402
from lib import net  # noqa: E402

# ---------------------------------------------------------------------------
# Config. For D1 the defaults voice ONE file (the Git & GitHub caption transcript)
# with the en_US-lessac-medium voice. See the module docstring for the modes.
# ---------------------------------------------------------------------------
_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TRANSCRIPT_DIR = os.path.join(_REPO_ROOT, paths.TRANSCRIPT_DIR)
GENERATED_DIR = os.path.join(_REPO_ROOT, paths.GENERATED_TRANSCRIPT_DIR)
SUMMARY_DIR = os.path.join(_REPO_ROOT, "summaries")
OUTPUT_DIR = os.path.join(_REPO_ROOT, paths.TTS_OUTPUT_DIR)
VOICE_DIR = os.path.join(OUTPUT_DIR, ".voices")  # downloaded .onnx models cache

SELECT_BY = "name"       # "name" | "id" | "all"
SELECT = ["Git and GitHub"]  # substrings (name) or video ids (id); ignored for all

ENGINE = "piper"         # only "piper" in the baseline
VOICE = "en_US-lessac-medium"  # Piper voice id; model downloads on first use
FORMAT = "wav"           # "wav" (Piper native) or "mp3" (converted via ffmpeg)
LENGTH_SCALE = 1.0       # speaking speed (Piper --length-scale): >1 slower, <1 faster.
                         # Handy presets: 0.9 (faster), 1.0 (normal), 1.15 (slower/clearer).
MAX_CHARS = None         # optional cap on input length for a quick test; None = all

# JSON config keys -> the module globals they set.
_CONFIG_KEYS = {
    "select_by": "SELECT_BY",
    "select": "SELECT",
    "engine": "ENGINE",
    "voice": "VOICE",
    "format": "FORMAT",
    "length_scale": "LENGTH_SCALE",
    "max_chars": "MAX_CHARS",
}
_DEFAULT_CONFIG = os.path.join("config", "config_tts.json")

# Text folders, in dedupe preference order (summary > caption > whisper).
_TEXT_SOURCES = (
    (SUMMARY_DIR, "summaries"),
    (TRANSCRIPT_DIR, paths.TRANSCRIPT_DIR),
    (GENERATED_DIR, paths.GENERATED_TRANSCRIPT_DIR),
)
_TEXT_EXTS = (".txt", ".md")
# Strip the leading "[HH:MM:SS] " timestamp that vtt_to_text writes.
_TS_PREFIX_RE = re.compile(r"^\s*\[\d{1,2}:\d{2}(?::\d{2})?\]\s*")
# The `[<id>]` YouTube id embedded in file names.
_ID_IN_NAME_RE = re.compile(r"\[([A-Za-z0-9_-]{11})\]")


def find_piper():
    """Locate the piper CLI (PATH or active conda env). Return the path, or None
    after printing a clear install hint."""
    exe = shutil.which("piper")
    if exe:
        return exe
    print("!! piper not found on PATH.")
    print("   This tool synthesizes speech with Piper (free, MIT, CPU-only). "
          "Install it, then re-run:")
    print("     pip install piper-tts")
    print("   Verify: piper --help")
    return None


def parse_meta(filename):
    """Extract (base, video_id) from a text file name.

    base drops the language/summary suffix so the output name tracks the video:
      "<title> [<id>].en.txt"          -> base "<title> [<id>]"
      "<title> [<id>].whisper.fr.txt"  -> base "<title> [<id>]"
      "<title> [<id>].summary.md"      -> base "<title> [<id>]"
    """
    name = filename
    for ext in (".txt", ".md"):
        if name.endswith(ext):
            name = name[: -len(ext)]
            break
    # Drop a trailing .summary / .whisper.<lang> / .<lang> suffix chain.
    name = re.sub(r"\.summary$", "", name)
    name = re.sub(r"\.(?:whisper\.)?[A-Za-z]{2,3}$", "", name)
    base = name.strip()
    vid = None
    mid = _ID_IN_NAME_RE.search(base)
    if mid:
        vid = mid.group(1)
    return base, vid


def _all_text_files():
    """Yield (abspath, filename, source_label) for every text file, in
    preference order (summaries first, then captions, then whisper)."""
    for folder, label in _TEXT_SOURCES:
        if not os.path.isdir(folder):
            continue
        for f in sorted(os.listdir(folder)):
            if f.lower().endswith(_TEXT_EXTS):
                yield os.path.join(folder, f), f, label


def pick_text(select_by, select):
    """Return [(abspath, filename, source_label)] to voice, per the mode.

    Dedupes by video id, preferring summary > caption > whisper (the yield order),
    so we produce one narration per video."""
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

    chosen = {}
    for abspath, fname, label in _all_text_files():
        if not matches(fname):
            continue
        base, vid = parse_meta(fname)
        key = vid or base
        if key not in chosen:  # first (highest-preference) wins
            chosen[key] = (abspath, fname, label)
    return list(chosen.values())


def _strip_markdown(text):
    """Reduce Markdown to plain narratable prose (for summaries/*.md)."""
    out = []
    in_fence = False
    for line in text.splitlines():
        if line.strip().startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        s = line
        s = re.sub(r"^\s{0,3}#{1,6}\s*", "", s)          # headings
        s = re.sub(r"^\s*[-*+]\s+", "", s)               # bullet markers
        s = re.sub(r"^\s*\d+\.\s+", "", s)               # numbered markers
        s = re.sub(r"!?\[([^\]]*)\]\([^)]*\)", r"\1", s)  # links/images -> text
        s = re.sub(r"[*_`>#]", "", s)                    # stray emphasis/code marks
        out.append(s)
    return "\n".join(out)


def read_text(path, filename):
    """Read a text source into narratable plain text.

    Strips [HH:MM:SS] timestamps (transcripts) and Markdown (summaries), then
    applies MAX_CHARS if set."""
    with open(path, encoding="utf-8") as f:
        raw = f.read()
    if filename.lower().endswith(".md"):
        text = _strip_markdown(raw)
    else:
        text = "\n".join(_TS_PREFIX_RE.sub("", ln) for ln in raw.splitlines())
    text = re.sub(r"\n{2,}", "\n", text).strip()
    if MAX_CHARS:
        text = text[: int(MAX_CHARS)]
    return text


def ensure_voice(voice):
    """Ensure the Piper voice .onnx is present in VOICE_DIR; download if missing.

    Returns the .onnx path, or None on failure (after printing a hint)."""
    onnx = os.path.join(VOICE_DIR, f"{voice}.onnx")
    if os.path.exists(onnx):
        return onnx
    os.makedirs(VOICE_DIR, exist_ok=True)
    net.apply_no_proxy_env()  # same corporate-proxy bypass Phase C uses for HF
    print(f"  downloading voice {voice!r} -> {VOICE_DIR} (first use only)...")
    result = subprocess.run(
        [sys.executable, "-m", "piper.download_voices", voice,
         "--data-dir", VOICE_DIR],
        capture_output=True, text=True, encoding="utf-8", errors="replace")
    if result.returncode != 0 or not os.path.exists(onnx):
        reason = (result.stderr or result.stdout or "").strip().splitlines()
        reason = reason[-1] if reason else f"exit code {result.returncode}"
        print(f"  ! voice download failed: {reason}")
        print(f"    Try manually: python -m piper.download_voices {voice} "
              f"--data-dir \"{VOICE_DIR}\"")
        return None
    return onnx


def synthesize_one(piper, onnx, abspath, filename):
    """Voice one text file. Returns "written" | "skipped" | "empty" | "failed"."""
    base, _vid = parse_meta(filename)
    # Only tag the name with the speed when it's non-default, so normal-speed
    # (1.0) output names stay unchanged and different speeds coexist.
    speed_tag = "" if float(LENGTH_SCALE) == 1.0 else f".s{LENGTH_SCALE}"
    out_name = f"{base}.{VOICE}{speed_tag}.{FORMAT}"
    out_path = os.path.join(OUTPUT_DIR, out_name)
    if os.path.exists(out_path):
        print(f"  = exists, skipping: {out_name}")
        return "skipped"

    text = read_text(abspath, filename)
    if not text.strip():
        print("  ! empty after cleaning — nothing to synthesize")
        return "empty"

    # Piper writes wav; for mp3 we synth to a temp wav then convert with ffmpeg.
    wav_path = out_path if FORMAT == "wav" else out_path[:-4] + ".__tmp__.wav"
    cmd = [piper, "-m", onnx, "-f", wav_path]
    if float(LENGTH_SCALE) != 1.0:
        cmd += ["--length-scale", str(LENGTH_SCALE)]
    print(f"  -> {VOICE} {FORMAT} (speed {LENGTH_SCALE}): {out_name}")
    result = subprocess.run(cmd, input=text, capture_output=True, text=True,
                            encoding="utf-8", errors="replace")
    if result.returncode != 0 or not os.path.exists(wav_path):
        reason = (result.stderr or "").strip().splitlines()
        reason = reason[-1] if reason else f"piper exit code {result.returncode}"
        print(f"  ! failed: {reason}")
        if os.path.exists(wav_path):
            _safe_remove(wav_path)
        return "failed"

    if FORMAT == "mp3":
        if not _wav_to_mp3(wav_path, out_path):
            _safe_remove(wav_path)
            return "failed"
        _safe_remove(wav_path)

    size_kb = os.path.getsize(out_path) / 1024
    print(f"     wrote {out_path} ({size_kb:.0f} KB)")
    return "written"


def _wav_to_mp3(wav_path, mp3_path):
    """Convert wav -> mp3 via ffmpeg (reuses the already-required binary)."""
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        print("  ! ffmpeg not found (needed for mp3). Install it or use "
              "format=wav.")
        return False
    result = subprocess.run(
        [ffmpeg, "-hide_banner", "-loglevel", "error", "-y", "-i", wav_path,
         "-c:a", "libmp3lame", "-b:a", "96k", mp3_path],
        capture_output=True, text=True, encoding="utf-8", errors="replace")
    if result.returncode != 0:
        reason = (result.stderr or "").strip().splitlines()
        print(f"  ! mp3 conversion failed: {reason[-1] if reason else ''}")
        return False
    return True


def _safe_remove(path):
    try:
        os.remove(path)
    except OSError:
        pass


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
    """CLI-arg config path wins; else config/config_tts.json if present."""
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

    if ENGINE != "piper":
        print(f"!! Invalid engine {ENGINE!r}. The baseline supports only 'piper'.")
        return
    if FORMAT not in ("wav", "mp3"):
        print(f"!! Invalid format {FORMAT!r}. Use 'wav' or 'mp3'.")
        return
    try:
        if float(LENGTH_SCALE) <= 0:
            raise ValueError
    except (TypeError, ValueError):
        print(f"!! Invalid length_scale {LENGTH_SCALE!r}. Use a positive number "
              f"(e.g. 0.9 faster, 1.0 normal, 1.15 slower).")
        return
    if SELECT_BY not in ("name", "id", "all"):
        print(f"!! Invalid select_by {SELECT_BY!r}. Use one of: name | id | all.")
        return
    if SELECT_BY in ("name", "id") and not SELECT:
        print(f"!! select_by={SELECT_BY!r} needs a non-empty 'select' list.")
        return

    piper = find_piper()
    if not piper:
        return

    selected = pick_text(SELECT_BY, SELECT)
    if not selected:
        print(f"No text matched SELECT_BY={SELECT_BY!r} SELECT={SELECT!r}")
        print(f"(looked in summaries\\, {paths.TRANSCRIPT_DIR}\\, "
              f"{paths.GENERATED_TRANSCRIPT_DIR}\\)")
        return

    print(f"Selected {len(selected)} text file(s) via SELECT_BY={SELECT_BY!r}, "
          f"voice {VOICE!r} -> {FORMAT}:")
    for _abs, f, label in selected:
        print(f"  - [{label}] {f}")

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    onnx = ensure_voice(VOICE)
    if not onnx:
        return

    written = skipped = empty = failed = 0
    for abspath, filename, _label in selected:
        print(f"\n{filename}")
        status = synthesize_one(piper, onnx, abspath, filename)
        written += status == "written"
        skipped += status == "skipped"
        empty += status == "empty"
        failed += status == "failed"

    print(f"\nDone. {written} synthesized, {skipped} skipped, {empty} empty, "
          f"{failed} failed, in:\n  {OUTPUT_DIR}")


if __name__ == "__main__":
    main()

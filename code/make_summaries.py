"""Prepare transcript summaries by handing off to the AI (Kiro).

This is the "option 2" helper: a plain script CANNOT write the analytical
summaries (table of contents, strengths, weaknesses) - that requires an LLM
reading each transcript. So instead this script does the deterministic part:

  1. finds every English transcript, from BOTH sources:
       - data/transcripts/<base>.en.txt            (YouTube captions)
       - data/generated_transcripts/<base>.whisper.en.txt  (Whisper, Phase C)
  2. picks ONE per video (base): a caption transcript is preferred; a Whisper
     transcript is used only when that video has no caption transcript
     (captions-first, Whisper fills the gaps - mirrors the C3 source flow),
  3. works out its expected summary path in data/summaries/,
  4. reports which videos already have a summary and which don't (tagging the
     source, caption vs. whisper),
  5. prints a single ready-to-paste instruction you give to Kiro in chat,
     which applies skill_summary.md to the missing ones.

Nothing here calls a paid API or needs a key. Run it via s.bat (or
`python code/make_summaries.py`), then paste the printed instruction into Kiro.

Base name rule (must match skill_summary.md), for BOTH sources:
    data/transcripts/<title> [<id>].en.txt                  -> data/summaries/<title> [<id>].summary.md
    data/generated_transcripts/<title> [<id>].whisper.en.txt -> data/summaries/<title> [<id>].summary.md
Both map to the SAME summary file, so a video summarized from Whisper and later
gaining captions never produces a duplicate/orphan summary.
"""

import os
import re
import sys

# Transcript filenames can contain non-ASCII characters (e.g. accented or
# non-Latin video titles). On Windows the console defaults to cp1252, which
# raises UnicodeEncodeError when printing those. Force UTF-8 output so the
# report never crashes on an exotic filename.
try:
    sys.stdout.reconfigure(encoding="utf-8")
except (AttributeError, ValueError):
    pass

# Make the repo root importable so `from lib import paths` works when this
# script is run as `python code/make_summaries.py`.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from lib import paths  # noqa: E402

# Resolve folders relative to the repo root (this file lives in code/).
_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TRANSCRIPT_DIR = os.path.join(_REPO_ROOT, paths.TRANSCRIPT_DIR)
GENERATED_DIR = os.path.join(_REPO_ROOT, paths.GENERATED_TRANSCRIPT_DIR)
SUMMARY_DIR = os.path.join(_REPO_ROOT, paths.SUMMARY_DIR)
SKILL_FILE = "skill_summary.md"          # relative path, for the printed hint

# Forward-slash relative forms of the folders, for the messages/instruction we
# print (so the paste-ready Kiro instruction points at the real data/ dirs).
_TRANSCRIPT_REL = paths.TRANSCRIPT_DIR.replace("\\", "/")
_GENERATED_REL = paths.GENERATED_TRANSCRIPT_DIR.replace("\\", "/")
_SUMMARY_REL = paths.SUMMARY_DIR.replace("\\", "/")

CAPTION_SUFFIX = ".en.txt"               # <transcripts>/<base>.en.txt
WHISPER_SUFFIX = ".whisper.en.txt"       # <generated_transcripts>/<base>.whisper.en.txt

# The `[<id>]` YouTube id embedded in a transcript file name. This is the true
# per-video identity, and it survives filename sanitizing (the caption and
# Whisper names for the same video can differ elsewhere, e.g. stripped `?`/`|`,
# but the id in brackets is identical).
_ID_IN_NAME_RE = re.compile(r"\[([A-Za-z0-9_-]{11})\]")


def _video_key(base):
    """Return the video id for a base name if present, else the base itself.

    Keying on the id makes captions-first dedupe work even when the caption and
    Whisper file names for the same video are spelled differently.
    """
    m = _ID_IN_NAME_RE.search(base)
    return m.group(1) if m else base


def _summary_path_for(base):
    """'<base>' -> absolute 'data/summaries/<base>.summary.md'."""
    return os.path.join(SUMMARY_DIR, f"{base}.summary.md")


def find_candidates():
    """Return {video_key: (base, source, rel_path)} with captions preferred.

    Keyed on the video id (see _video_key) so the same video is never listed
    twice. source is "caption" or "whisper"; rel_path is repo-relative for the
    paste-ready instruction. A video present as a caption is never overridden by
    a Whisper transcript (captions-first); Whisper is added only for videos with
    no caption.
    """
    candidates = {}

    # 1) Captions first (win on conflict). Note: .whisper.en.txt also ends with
    #    .en.txt, so guard against it here even though it lives in another dir.
    if os.path.isdir(TRANSCRIPT_DIR):
        for name in sorted(os.listdir(TRANSCRIPT_DIR)):
            if name.endswith(WHISPER_SUFFIX):
                continue
            if name.endswith(CAPTION_SUFFIX):
                base = name[: -len(CAPTION_SUFFIX)]
                candidates[_video_key(base)] = ("caption", base,
                                                f"{_TRANSCRIPT_REL}/{name}")

    # 2) Whisper fills gaps: add only videos not already covered by a caption.
    if os.path.isdir(GENERATED_DIR):
        for name in sorted(os.listdir(GENERATED_DIR)):
            if name.endswith(WHISPER_SUFFIX):
                base = name[: -len(WHISPER_SUFFIX)]
                key = _video_key(base)
                if key not in candidates:
                    candidates[key] = ("whisper", base,
                                       f"{_GENERATED_REL}/{name}")

    return candidates


def main():
    os.makedirs(SUMMARY_DIR, exist_ok=True)

    candidates = find_candidates()
    if not candidates:
        print(f"No English transcripts found in {_TRANSCRIPT_REL}/ (*{CAPTION_SUFFIX}) "
              f"or {_GENERATED_REL}/ (*{WHISPER_SUFFIX}).")
        print("Run t (captions) or w (Whisper) first.")
        return

    done, missing = [], []
    for key in candidates:
        source, base, rel = candidates[key]
        entry = (base, source, rel)
        (done if os.path.exists(_summary_path_for(base)) else missing).append(entry)

    done.sort()
    missing.sort()

    print(f"Found {len(candidates)} video(s) with an English transcript "
          f"(captions preferred, Whisper fills gaps):")
    for base, source, _ in done:
        print(f"  [have summary]  ({source}) {base}")
    for base, source, _ in missing:
        print(f"  [NEEDS summary] ({source}) {base}")
    print()

    if not missing:
        print(f"All videos already have a summary in {_SUMMARY_REL}/.")
        print(f"To force-refresh one, delete its {_SUMMARY_REL}/*.summary.md and re-run.")
        return

    # Print a single copy-paste instruction for Kiro. The AI does the actual
    # reading + writing; this script just told you exactly what to ask for.
    print("=" * 70)
    print("NEXT STEP - paste this into Kiro (the AI writes the summaries):")
    print("=" * 70)
    print(f"Apply {SKILL_FILE} to these transcripts and save each to "
          f"{_SUMMARY_REL}/<base>.summary.md:")
    for base, source, rel in missing:
        print(f"  - {rel}")
    print()
    print("(Kiro reads each transcript and writes a summary following "
          f"{SKILL_FILE}. Whisper transcripts live in {_GENERATED_REL}/, "
          f"caption transcripts in {_TRANSCRIPT_REL}/; both map to the same "
          "summary base name.)")


if __name__ == "__main__":
    main()

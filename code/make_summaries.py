"""Prepare transcript summaries by handing off to the AI (Kiro).

This is the "option 2" helper: a plain script CANNOT write the analytical
summaries (table of contents, strengths, weaknesses) - that requires an LLM
reading each transcript. So instead this script does the deterministic part:

  1. finds every English transcript in transcripts/  (*.en.txt),
  2. works out its expected summary path in summaries/,
  3. reports which transcripts already have a summary and which don't,
  4. prints a single ready-to-paste instruction you give to Kiro in chat,
     which applies skill_summary.md to the missing ones.

Nothing here calls a paid API or needs a key. Run it via s.bat (or
`python code/make_summaries.py`), then paste the printed instruction into Kiro.

Base name rule (must match skill_summary.md):
    "<title> [<id>].en.txt"  ->  "summaries/<title> [<id>].summary.md"
"""

import os

# Resolve folders relative to the repo root (this file lives in code/).
_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TRANSCRIPT_DIR = os.path.join(_REPO_ROOT, "transcripts")
SUMMARY_DIR = os.path.join(_REPO_ROOT, "summaries")
SKILL_FILE = "skill_summary.md"          # relative path, for the printed hint
LANG_SUFFIX = ".en.txt"                  # only summarize English transcripts


def _summary_path_for(transcript_name):
    """'<base>.en.txt' -> absolute 'summaries/<base>.summary.md'."""
    base = transcript_name[: -len(LANG_SUFFIX)]   # strip ".en.txt"
    return os.path.join(SUMMARY_DIR, f"{base}.summary.md")


def find_transcripts():
    """Return sorted English transcript filenames (just the names)."""
    if not os.path.isdir(TRANSCRIPT_DIR):
        return []
    return sorted(
        name for name in os.listdir(TRANSCRIPT_DIR)
        if name.endswith(LANG_SUFFIX)
    )


def main():
    os.makedirs(SUMMARY_DIR, exist_ok=True)

    transcripts = find_transcripts()
    if not transcripts:
        print(f"No '*{LANG_SUFFIX}' transcripts found in {TRANSCRIPT_DIR}/.")
        print("Run t.bat first to download some transcripts.")
        return

    done, missing = [], []
    for name in transcripts:
        (done if os.path.exists(_summary_path_for(name)) else missing).append(name)

    print(f"Found {len(transcripts)} English transcript(s) in transcripts/:")
    for name in done:
        print(f"  [have summary] {name}")
    for name in missing:
        print(f"  [NEEDS summary] {name}")
    print()

    if not missing:
        print("All English transcripts already have a summary in summaries/.")
        print("To force-refresh one, delete its summaries/*.summary.md and re-run.")
        return

    # Print a single copy-paste instruction for Kiro. The AI does the actual
    # reading + writing; this script just told you exactly what to ask for.
    print("=" * 70)
    print("NEXT STEP - paste this into Kiro (the AI writes the summaries):")
    print("=" * 70)
    rel_paths = [f"transcripts/{name}" for name in missing]
    print(f"Apply {SKILL_FILE} to these transcripts and save each to "
          f"summaries/<base>.summary.md:")
    for rel in rel_paths:
        print(f"  - {rel}")
    print()
    print("(Kiro reads each transcript and writes a summary following "
          f"{SKILL_FILE}.)")


if __name__ == "__main__":
    main()

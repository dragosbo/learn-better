"""Compare the Whisper output (data/generated_transcripts/*.whisper.*.txt)
against the YouTube English transcript for the same video, ignoring timestamps,
casing, and punctuation. Prints similarity metrics and a rough quality percentage.

Usage:
    python code/compare_transcripts.py
"""

import os
import re
import sys
import difflib
from collections import Counter

# Make the repo root importable so `from lib import paths` works when this
# script is run as `python code/compare_transcripts.py`.
_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _REPO_ROOT)
from lib import paths  # noqa: E402

WHISPER_FILE = os.path.join(
    _REPO_ROOT, paths.GENERATED_TRANSCRIPT_DIR,
    "Git and GitHub Tutorial for Beginners [tRZGeaHPoaw].whisper.en.txt")
YT_FILE = os.path.join(
    _REPO_ROOT, paths.TRANSCRIPT_DIR,
    "Git and GitHub Tutorial for Beginners [tRZGeaHPoaw].en.txt")

TIMESTAMP_RE = re.compile(r"\[\d{2}:\d{2}:\d{2}\]")
WORD_RE = re.compile(r"[a-z0-9]+")


def read_text(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def normalize(text):
    """Strip timestamps, lowercase, collapse to a list of word tokens."""
    text = TIMESTAMP_RE.sub(" ", text)
    text = text.lower()
    # Treat github/git hub, dot/./ etc. loosely by just extracting word tokens.
    return WORD_RE.findall(text)


def main():
    whisper_raw = read_text(WHISPER_FILE)
    yt_raw = read_text(YT_FILE)

    w = normalize(whisper_raw)
    y = normalize(yt_raw)

    print("=== Raw sizes ===")
    print(f"Whisper: {len(whisper_raw):>7} chars, {len(w):>6} word tokens")
    print(f"YouTube: {len(yt_raw):>7} chars, {len(y):>6} word tokens")
    print()

    # 1) Sequence similarity on the token streams (order-sensitive).
    sm = difflib.SequenceMatcher(a=y, b=w, autojunk=False)
    ratio = sm.ratio()
    print("=== Sequence similarity (order-sensitive, YouTube as reference) ===")
    print(f"difflib ratio: {ratio*100:.1f}%")

    # Word-level "accuracy" analogous to (1 - WER) using difflib opcodes.
    matches = sum(blk.size for blk in sm.get_matching_blocks())
    subs = ins = dels = 0
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "replace":
            subs += max(i2 - i1, j2 - j1)
        elif tag == "delete":
            dels += i2 - i1
        elif tag == "insert":
            ins += j2 - j1
    ref_len = len(y)
    wer = (subs + ins + dels) / ref_len if ref_len else 0.0
    print(f"matching words: {matches}/{ref_len} of reference")
    print(f"approx WER: {wer*100:.1f}%  ->  word accuracy ~ {(1-wer)*100:.1f}%")
    print()

    # 2) Bag-of-words overlap (order-insensitive) via multiset intersection.
    cw, cy = Counter(w), Counter(y)
    inter = sum((cw & cy).values())
    jacc = inter / (len(w) + len(y) - inter) if (w or y) else 0.0
    cov_ref = inter / len(y) if y else 0.0
    print("=== Bag-of-words overlap (order-insensitive) ===")
    print(f"shared word instances: {inter}")
    print(f"Jaccard (multiset): {jacc*100:.1f}%")
    print(f"coverage of reference vocab instances: {cov_ref*100:.1f}%")
    print()

    # 3) Some concrete divergences: words the reference has that Whisper lacks
    #    (candidate errors), most common first.
    missing = (cy - cw)
    extra = (cw - cy)
    print("=== Top words in YouTube but under-represented in Whisper ===")
    for word, n in missing.most_common(15):
        print(f"  -{n:>3}  {word}")
    print()
    print("=== Top words Whisper has but YouTube doesn't (misrecognitions) ===")
    for word, n in extra.most_common(15):
        print(f"  +{n:>3}  {word}")


if __name__ == "__main__":
    main()

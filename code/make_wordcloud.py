"""Phase W (steps W0-W1): build word_cloud.json from ONE transcript.

Data-only: this script does NO plotting. It reads a transcript, counts word
frequencies (minus stopwords), and writes a renderer-agnostic JSON that a small
HTML page renders client-side with wordcloud.js (see wordcloud.html, Phase W2).

Input transcripts live in:
    transcripts/<title> [<id>].en.txt              (YouTube captions)
    generated_transcripts/<title> [<id>].whisper.<lang>.txt  (Whisper, Phase C)
Output:
    data/wordclouds/<title> [<id>].word_cloud.json

The JSON shape (words pre-sorted by descending weight):
    {
      "source": "transcripts/... .en.txt",
      "video_id": "...", "title": "...", "language": "en",
      "total_tokens": N, "unique_words": M,
      "generated_at": "<iso8601>",
      "params": { "min_length": 3, "max_words": 150, "lowercase": true },
      "words": [ {"text": "git", "weight": 128}, ... ]
    }

Selecting which transcripts to process (set SELECT_BY + SELECT below):
  - SELECT_BY = "input": just the single INPUT file/id (the W1 behavior).
  - SELECT_BY = "name":  transcripts whose file NAME contains any SELECT
    substring (case-insensitive), e.g. ["Git and GitHub", "GitLab"].
  - SELECT_BY = "id":    transcripts matched by YouTube video id (the `[<id>]`
    in the file name), e.g. ["tRZGeaHPoaw"].
  - SELECT_BY = "all":   every transcript in transcripts/ + generated_transcripts/.

When both a caption (transcripts/) and a Whisper (generated_transcripts/)
transcript exist for the same video, the CAPTION one is preferred (one word
cloud per video), matching make_summaries.py.

MERGE = True combines ALL selected transcripts into ONE word cloud (word counts
summed across files) and writes a single data/wordclouds/<OUTPUT_NAME>.word_cloud.json.
Use it to get a single cloud for, say, a whole series: pick the transcripts with
name/id/all, set merge=true and output_name="git-series". All merged transcripts
must be the same language (the language guard still applies).

Usage (from the repo root, with the learn-better env active):
    python code/make_wordcloud.py                          # in-file defaults / auto-config
    python code/make_wordcloud.py config/config_wordcloud.json  # load a JSON config

A JSON config may set any of: select_by, select, input, min_length, max_words,
lowercase, language, stopwords_extra. Keys it omits keep the in-file defaults.
If no argument is given and config/config_wordcloud.json exists, it is loaded
automatically; otherwise the in-file defaults are used.

No extra pip deps: pure stdlib (re, json, collections). The JS word-cloud
library is loaded from a CDN in the HTML, not here.
"""

import json
import os
import re
import sys
from collections import Counter
from datetime import datetime, timezone

# Force UTF-8 stdout so non-ASCII transcript titles (fr/ro, emoji) never crash
# the Windows cp1252 console when we print them.
try:
    sys.stdout.reconfigure(encoding="utf-8")
except (AttributeError, ValueError):
    pass

# Make the repo root importable so `from lib import ...` works when run as
# `python code/make_wordcloud.py`.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from lib import paths  # noqa: E402
from lib.textutil import safe_filename  # noqa: E402

# ---------------------------------------------------------------------------
# Config (W1 - single file). Point INPUT at a transcript file NAME (it is
# looked up in transcripts/ first, then generated_transcripts/) or a video id.
# ---------------------------------------------------------------------------
_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TRANSCRIPT_DIR = os.path.join(_REPO_ROOT, paths.TRANSCRIPT_DIR)
GENERATED_DIR = os.path.join(_REPO_ROOT, paths.GENERATED_TRANSCRIPT_DIR)
OUTPUT_DIR = os.path.join(_REPO_ROOT, paths.WORDCLOUD_DIR)

# Selection: what to process. See the module docstring for the modes.
SELECT_BY = "input"      # "input" | "name" | "id" | "all"
SELECT = []              # substrings (name) or video ids (id); ignored for input/all
INPUT = "Git and GitHub Tutorial for Beginners [tRZGeaHPoaw].en.txt"  # for SELECT_BY="input"

# Merge mode: combine ALL selected transcripts into ONE word cloud.
#   MERGE = False -> one word_cloud.json per video (default).
#   MERGE = True  -> sum word counts across every selected transcript and write a
#                    single data/wordclouds/<OUTPUT_NAME>.word_cloud.json.
MERGE = False
OUTPUT_NAME = "combined"  # base name of the merged file (MERGE=True only)

MIN_LENGTH = 3           # drop tokens shorter than this
MAX_WORDS = 150          # keep the top-N most frequent words
LOWERCASE = True         # fold case before counting
LANGUAGE = "en"          # picks the built-in stopword list: en | fr | ro
STOPWORDS_EXTRA = []     # extra words to always drop (project/domain noise)

# JSON config keys -> the module globals they set.
_CONFIG_KEYS = {
    "select_by": "SELECT_BY",
    "select": "SELECT",
    "input": "INPUT",
    "merge": "MERGE",
    "output_name": "OUTPUT_NAME",
    "min_length": "MIN_LENGTH",
    "max_words": "MAX_WORDS",
    "lowercase": "LOWERCASE",
    "language": "LANGUAGE",
    "stopwords_extra": "STOPWORDS_EXTRA",
}
_DEFAULT_CONFIG = os.path.join("config", "config_wordcloud.json")

# Strip the leading "[HH:MM:SS] " timestamp that vtt_to_text writes.
_TS_PREFIX_RE = re.compile(r"^\s*\[\d{1,2}:\d{2}(?::\d{2})?\]\s*")
# Unicode-aware word token: runs of letters (keeps accented fr/ro), no digits.
_WORD_RE = re.compile(r"[^\W\d_]+", re.UNICODE)
# The `[<id>]` YouTube id embedded in transcript file names.
_ID_IN_NAME_RE = re.compile(r"\[([A-Za-z0-9_-]{11})\]")

# Small, dependency-free stopword lists. Not exhaustive; extend as needed or via
# STOPWORDS_EXTRA. (A heavier NLP list, e.g. nltk, is a possible future upgrade.)
_STOPWORDS = {
    "en": {
        "the", "and", "a", "an", "to", "of", "in", "is", "it", "that", "this",
        "for", "on", "you", "i", "we", "he", "she", "they", "with", "as", "at",
        "be", "are", "was", "were", "so", "if", "or", "but", "not", "no", "yes",
        "have", "has", "had", "do", "does", "did", "can", "could", "will",
        "would", "should", "my", "your", "our", "their", "his", "her", "its",
        "me", "us", "them", "him", "what", "when", "where", "which", "who",
        "how", "why", "here", "there", "then", "than", "just", "like", "get",
        "got", "up", "out", "about", "into", "over", "all", "some", "any", "one",
        "now", "also", "from", "by", "let", "going", "want", "make", "see",
        "use", "using", "very", "really", "well", "okay", "ok", "yeah", "gonna",
        "im", "youre", "dont", "thats", "were", "its", "ive", "youll", "well",
        "s", "t", "re", "ll", "ve", "m", "d",
    },
    "fr": {
        "le", "la", "les", "un", "une", "des", "de", "du", "et", "ou", "que",
        "qui", "quoi", "dont", "pour", "par", "avec", "sans", "dans", "sur",
        "sous", "est", "sont", "ete", "etre", "avoir", "je", "tu", "il", "elle",
        "nous", "vous", "ils", "elles", "on", "ce", "cet", "cette", "ces", "mon",
        "ton", "son", "ma", "ta", "sa", "mes", "tes", "ses", "notre", "votre",
        "leur", "leurs", "ne", "pas", "plus", "moins", "tres", "bien", "aussi",
        "mais", "donc", "car", "si", "comme", "quand", "ou", "y", "en", "au",
        "aux", "se", "sa", "ses", "cela", "ca", "oui", "non", "fait", "faire",
        "a", "l", "d", "j", "c", "n", "s", "t", "m", "qu", "ll",
    },
    "ro": {
        "si", "sa", "sau", "de", "la", "in", "un", "o", "cu", "ca", "ce", "cel",
        "cea", "cei", "cele", "este", "sunt", "era", "fi", "am", "ai", "are",
        "avem", "aveti", "au", "eu", "tu", "el", "ea", "noi", "voi", "ei", "ele",
        "pe", "din", "prin", "pentru", "dar", "insa", "deci", "daca", "cand",
        "unde", "care", "cine", "cum", "mai", "foarte", "bine", "asa", "acest",
        "aceasta", "acesti", "aceste", "meu", "tau", "sau", "nostru", "vostru",
        "lor", "nu", "da", "se", "isi", "il", "ii", "le", "ne", "va", "te",
        "ma", "mi", "ti", "l", "s", "i",
    },
}


def resolve_input(name):
    """Find the transcript file for INPUT (a file name or a video id).

    Returns (abs_path, source_rel) or (None, None). Looks in transcripts/ first,
    then generated_transcripts/. If `name` is an 11-char id, match by `[<id>]`.
    """
    candidates = []
    for folder, rel_prefix in ((TRANSCRIPT_DIR, paths.TRANSCRIPT_DIR),
                               (GENERATED_DIR, paths.GENERATED_TRANSCRIPT_DIR)):
        if not os.path.isdir(folder):
            continue
        for f in sorted(os.listdir(folder)):
            if not f.endswith(".txt"):
                continue
            candidates.append((os.path.join(folder, f), f"{rel_prefix}/{f}", f))

    # Exact file-name match wins.
    for abspath, rel, fname in candidates:
        if fname == name:
            return abspath, rel
    # Otherwise treat `name` as a video id (or substring of the file name).
    is_id = bool(re.fullmatch(r"[A-Za-z0-9_-]{11}", name))
    for abspath, rel, fname in candidates:
        if is_id:
            m = _ID_IN_NAME_RE.search(fname)
            if m and m.group(1) == name:
                return abspath, rel
        elif name.lower() in fname.lower():
            return abspath, rel
    return None, None


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
    """CLI-arg config path wins; else config/config_wordcloud.json if present."""
    if len(sys.argv) > 1:
        return sys.argv[1]
    default = os.path.join(_REPO_ROOT, _DEFAULT_CONFIG)
    return default if os.path.exists(default) else None


def _all_transcripts():
    """Yield (abspath, source_rel, filename) for every .txt in both folders."""
    for folder, rel_prefix in ((TRANSCRIPT_DIR, paths.TRANSCRIPT_DIR),
                               (GENERATED_DIR, paths.GENERATED_TRANSCRIPT_DIR)):
        if not os.path.isdir(folder):
            continue
        for f in sorted(os.listdir(folder)):
            if f.endswith(".txt"):
                yield os.path.join(folder, f), f"{rel_prefix}/{f}", f


def pick_transcripts(select_by, select, input_name):
    """Return [(abspath, source_rel, filename)] to process, per the mode.

    Dedupes by video id, preferring the caption transcript (transcripts/) over
    the Whisper one (generated_transcripts/) when both exist for a video, so we
    produce one word cloud per video. `_all_transcripts` yields captions first.
    """
    if select_by == "input":
        abspath, rel = resolve_input(input_name)
        return [(abspath, rel, os.path.basename(abspath))] if abspath else []

    all_files = list(_all_transcripts())

    def matches(fname):
        if select_by == "all":
            return True
        if select_by == "name":
            low = fname.lower()
            return any(s.lower() in low for s in select)
        if select_by == "id":
            m = _ID_IN_NAME_RE.search(fname)
            return bool(m and m.group(1) in set(select))
        raise ValueError(f"Unknown SELECT_BY: {select_by!r} "
                         f"(use input|name|id|all)")

    chosen = {}
    for abspath, rel, fname in all_files:
        if not matches(fname):
            continue
        base, vid, _title, _lang = parse_meta(fname)
        key = vid or base          # dedupe key: video id, else base name
        if key not in chosen:      # captions come first -> win on conflict
            chosen[key] = (abspath, rel, fname)
    return list(chosen.values())


def parse_meta(filename):
    """Extract (base, video_id, language) from a transcript file name.

    base drops the language suffix so the JSON name tracks the video:
      "<title> [<id>].en.txt"          -> base "<title> [<id>]", lang "en"
      "<title> [<id>].whisper.fr.txt"  -> base "<title> [<id>]", lang "fr"
    """
    name = filename
    lang = None
    if name.endswith(".txt"):
        name = name[:-4]
    # .whisper.<lang> or .<lang>
    m = re.search(r"\.(?:whisper\.)?([A-Za-z]{2,3})$", name)
    if m:
        lang = m.group(1)
        name = name[: m.start()]
    base = safe_filename(name)
    vid = None
    mid = _ID_IN_NAME_RE.search(base)
    if mid:
        vid = mid.group(1)
    title = _ID_IN_NAME_RE.sub("", base).strip()
    return base, vid, title, lang


def read_transcript_text(path):
    """Read a transcript, stripping the leading [HH:MM:SS] timestamps."""
    lines = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            lines.append(_TS_PREFIX_RE.sub("", line))
    return " ".join(lines)


def count_transcript(text, language, min_length, lowercase, extra):
    """Tokenize + filter one transcript -> a Counter of kept words.

    Shared by the per-file and merge paths so combining is just Counter addition.
    """
    stop = set(_STOPWORDS.get(language, set())) | {w.lower() for w in extra}
    tokens = _WORD_RE.findall(text)
    if lowercase:
        tokens = [t.lower() for t in tokens]
    kept = [t for t in tokens if len(t) >= min_length and t not in stop]
    return Counter(kept)


def top_words(counts, max_words):
    """Counter -> (top_words list of {text, weight}, total_tokens, unique_words)."""
    top = counts.most_common(max_words)
    words = [{"text": w, "weight": n} for w, n in top]
    total = sum(counts.values())
    return words, total, len(counts)


def count_words(text, language, min_length, max_words, lowercase, extra):
    """Convenience: count one transcript and return its top-N (back-compat)."""
    counts = count_transcript(text, language, min_length, lowercase, extra)
    return top_words(counts, max_words)


def process_transcript(abspath, source_rel, filename):
    """Build one word_cloud.json for a transcript. Returns a status string:
    "written" | "skipped" | "empty"."""
    base, video_id, title, file_lang = parse_meta(filename)
    # LANGUAGE picks the stopword list; fall back to the file's language.
    language = LANGUAGE or file_lang or "en"

    out_path = os.path.join(OUTPUT_DIR, f"{base}.word_cloud.json")
    if os.path.exists(out_path):
        print(f"  = exists, skipping: {os.path.basename(out_path)}")
        return "skipped"

    print(f"  reading: {source_rel}")
    text = read_transcript_text(abspath)
    words, total, unique = count_words(
        text, language, MIN_LENGTH, MAX_WORDS, LOWERCASE, STOPWORDS_EXTRA)
    if not words:
        print("  ! no words left after filtering — check language / min_length")
        return "empty"

    payload = {
        "source": source_rel,
        "video_id": video_id,
        "title": title,
        "language": language,
        "total_tokens": total,
        "unique_words": unique,
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "params": {
            "min_length": MIN_LENGTH,
            "max_words": MAX_WORDS,
            "lowercase": LOWERCASE,
            "stopwords_language": language,
        },
        "words": words,
    }
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    top = ", ".join(f"{w['text']}({w['weight']})" for w in words[:8])
    print(f"  -> {language}: {total} tokens, {unique} unique, top {len(words)} "
          f"| {top}")
    print(f"     wrote {out_path}")
    return "written"


def check_language_consistency(selected):
    """Guard: all selected transcripts must be the SAME language as LANGUAGE.

    A word cloud uses one stopword list (LANGUAGE). Mixing languages in one batch
    would apply the wrong stopwords to the off-language files, producing garbage.
    We read each file's language from its name suffix (.en / .whisper.fr / ...).

    Returns True if consistent (all == LANGUAGE, or a file has no detectable
    suffix language, which we allow). On mismatch, prints the offenders and
    returns False so the caller can abort.
    """
    offenders = []
    for _abs, rel, filename in selected:
        _base, _vid, _title, file_lang = parse_meta(filename)
        # Allow files with no detectable language suffix (we can't judge them).
        if file_lang and file_lang != LANGUAGE:
            offenders.append((rel, file_lang))
    if offenders:
        print(f"\n!! LANGUAGE MISMATCH — refusing to run a mixed-language batch.")
        print(f"   Stopwords are set for LANGUAGE={LANGUAGE!r}, but these "
              f"selected transcripts are a different language:")
        for rel, lang in offenders:
            print(f"     [{lang}] {rel}")
        print(f"   A word cloud uses ONE stopword list, so mixing languages "
              f"gives poor results.")
        print(f"   Fix: narrow the selection to one language (by name/id), or "
              f"set LANGUAGE to {sorted({l for _, l in offenders})} and run those "
              f"separately.")
        return False
    return True


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

    selected = pick_transcripts(SELECT_BY, SELECT, INPUT)
    if not selected:
        print(f"No transcripts matched SELECT_BY={SELECT_BY!r} SELECT={SELECT!r}"
              f" INPUT={INPUT!r}")
        print(f"(looked in {TRANSCRIPT_DIR}\\ and {GENERATED_DIR}\\)")
        return

    print(f"Selected {len(selected)} transcript(s) via SELECT_BY={SELECT_BY!r}:")
    for _abs, rel, _f in selected:
        print(f"  - {rel}")

    # Guard: a batch must be single-language (all matching LANGUAGE), because one
    # word cloud uses one stopword list. Abort on a mixed-language selection.
    if not check_language_consistency(selected):
        return

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    if MERGE:
        run_merge(selected)
        return

    written = skipped = empty = 0
    for abspath, rel, filename in selected:
        print(f"\n{filename}")
        status = process_transcript(abspath, rel, filename)
        written += status == "written"
        skipped += status == "skipped"
        empty += status == "empty"

    print(f"\nDone. {written} written, {skipped} skipped, {empty} empty, in:"
          f"\n  {OUTPUT_DIR}")


def run_merge(selected):
    """Combine ALL selected transcripts into ONE word cloud (sum word counts),
    written to data/wordclouds/<OUTPUT_NAME>.word_cloud.json."""
    language = LANGUAGE or "en"
    out_name = safe_filename(OUTPUT_NAME) or "combined"
    out_path = os.path.join(OUTPUT_DIR, f"{out_name}.word_cloud.json")
    if os.path.exists(out_path):
        print(f"\n= merged file exists, skipping: {os.path.basename(out_path)}")
        print("  (delete it to regenerate, or change OUTPUT_NAME)")
        return

    print(f"\nMerging {len(selected)} transcript(s) -> one cloud "
          f"'{out_name}' (language {language})...")
    combined = Counter()
    sources = []
    for abspath, rel, filename in selected:
        text = read_transcript_text(abspath)
        combined += count_transcript(
            text, language, MIN_LENGTH, LOWERCASE, STOPWORDS_EXTRA)
        sources.append(rel)
        print(f"  + {rel}")

    words, total, unique = top_words(combined, MAX_WORDS)
    if not words:
        print("  ! no words left after filtering — check language / min_length")
        return

    payload = {
        "source": sources,                 # list of all merged transcripts
        "video_id": None,                  # not a single video
        "title": f"{OUTPUT_NAME} (merged from {len(sources)} transcripts)",
        "language": language,
        "total_tokens": total,
        "unique_words": unique,
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "params": {
            "min_length": MIN_LENGTH,
            "max_words": MAX_WORDS,
            "lowercase": LOWERCASE,
            "stopwords_language": language,
            "merged": True,
            "merged_count": len(sources),
        },
        "words": words,
    }
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    top = ", ".join(f"{w['text']}({w['weight']})" for w in words[:10])
    print(f"\n-> merged {language}: {total} tokens, {unique} unique, "
          f"top {len(words)} | {top}")
    print(f"Done. Wrote:\n  {out_path}")


if __name__ == "__main__":
    main()

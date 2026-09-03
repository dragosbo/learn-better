"""Filename sanitizing, subtitle (VTT) cleaning, and language config.

Moved verbatim (behavior-preserving) from the entry scripts so transcript
handling lives in one place.
"""

import html
import json
import os
import re

# languages.json lives next to the code/ scripts. lib/ is a sibling of code/,
# so resolve it relative to the repo root (parent of this file's parent).
_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LANGUAGES_CONFIG = os.path.join(_REPO_ROOT, "code", "languages.json")

# Matches a VTT timing line, e.g. "00:00:04.799 --> 00:00:06.950 align:start ..."
# capturing the start time "HH:MM:SS" (or "MM:SS"), dropping milliseconds.
TIMING_RE = re.compile(r"^\s*(\d{1,2}:\d{2}(?::\d{2})?)[.,]\d{3}\s*-->")


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


def safe_filename(name):
    """Strip characters that are illegal in Windows filenames."""
    return "".join(c for c in name if c not in '\\/:*?"<>|').strip()


def clean_text(raw):
    """Strip VTT/HTML tags, decode entities, normalize whitespace on one line."""
    text = re.sub(r"<[^>]+>", "", raw)          # drop <...> tags
    text = html.unescape(text)                  # &nbsp; &amp; &#39; -> chars
    text = text.replace("\u00a0", " ")          # nbsp -> normal space
    return re.sub(r"\s+", " ", text).strip()


def vtt_to_text(vtt_path):
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
        m = TIMING_RE.match(line)
        if m:
            current_ts = m.group(1)
            continue
        if (not stripped
                or stripped.startswith("WEBVTT")
                or stripped.startswith(("Kind:", "Language:", "NOTE"))
                or stripped.isdigit()):
            continue
        text = clean_text(line)
        if not text or text == last_text:
            continue
        out.append(f"[{current_ts or '00:00:00'}] {text}")
        last_text = text
    return "\n".join(out)

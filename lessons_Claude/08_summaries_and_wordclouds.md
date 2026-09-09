# Lesson 08 — Summaries and Word Clouds

**You'll build:** `code/make_summaries.py` (generates paste-ready AI instructions for summarising
transcripts), `code/make_wordcloud.py` (produces word-frequency JSON for the HTML viewer),
`lib/textutil.py` (the real text utilities — replacing the stub from Lesson 05), `skill_summary.md`
(the reusable summarisation instruction set), and `config/config_wordcloud.json`.
**Complexity:** ⭐⭐⭐⭐☆   **Est. time:** ~90–105 min
**AI tasks in this lesson:** instruction-set design, text-processing script generation, AI-as-author
concept, pure-stdlib script generation

---

## Prerequisites

- Lesson 07 completed: all runners and `init.bat` in place
- At least one transcript file in `data/transcripts/` or `data/generated_transcripts/`
- `lib/textutil.py` stub exists (from Lesson 05) — this lesson replaces it with the full version

---

## Re-orient the AI

> Paste this block at the start of a new session, or any time the assistant loses context:
>
> "I'm working on the **learn-better** repo — a Python tool that downloads YouTube audio and
> transcripts, transcribes locally with faster-whisper, and generates summaries and word clouds.
> We're on **Lesson 08 — Summaries and Word Clouds**. All download and transcription scripts are
> working. We have NOT yet written `make_summaries.py`, `make_wordcloud.py`, or `skill_summary.md`.
> `lib/textutil.py` currently has stubs — this lesson replaces them with real implementations.
> OS: Windows. Conda env: `learn-better`. Please continue from where I left off."

---

## Concepts

1. **`make_summaries.py` doesn't call any AI — it prepares instructions for you to paste.**
   The script finds transcripts that lack a matching summary, formats a paste-ready prompt
   (including the transcript text), and prints it. You copy that output into your AI assistant.
   This design means the summarisation step is transparent, auditable, and works with any assistant.

2. **A reusable instruction set lives in `skill_summary.md`.** The structure of a good summary
   (table of contents, key takeaways, strengths, weaknesses) is encoded in that file once and
   referenced by `make_summaries.py`. When you want to change the summary format, you edit one
   file, not every prompt.

3. **Pure stdlib is enough for word clouds.** Word frequency counting needs only `collections.Counter`
   and text normalisation — no third-party NLP library required. The output is a JSON file that a
   small HTML viewer (`wordcloud.html`) reads directly.

---

## Step-by-step

### 08.1 — Design `skill_summary.md`

**Prompt:**
```
I need a reusable instruction set for summarising YouTube video transcripts. This file will be
used as the template that make_summaries.py includes in every paste-ready prompt.

The summary should have these sections:
  1. Source video title and approximate length
  2. Topic and target audience (one sentence each)
  3. One-line takeaway
  4. Table of contents with timestamps (from the transcript)
  5. Section-by-section summaries (one paragraph each)
  6. Key takeaways as a numbered list
  7. Strengths of the video
  8. Weaknesses or gaps
  9. Who should watch (and who shouldn't)

Requirements:
  - Write in Markdown
  - Use placeholder tokens like {{TITLE}} and {{TRANSCRIPT}} that make_summaries.py will replace
  - Output filename format: data/summaries/<base name>.summary.md
  - Tone: clear and factual, no marketing language, no emojis

Write skill_summary.md. Output only the file content.
```

**Expected output:** A markdown file with clear section headers and `{{TITLE}}` / `{{TRANSCRIPT}}`
placeholders. The instruction for the AI assistant should be explicit: "Read the transcript below
and write a summary following the structure above."

**Verify:** Check that `{{TRANSCRIPT}}` appears somewhere near the bottom (the full transcript
goes there). Check that the output naming instruction is present (`data/summaries/<base>.summary.md`).

---

### 08.2 — Generate `code/make_summaries.py`

**Prompt:**
```
Write code/make_summaries.py with these exact requirements:

Purpose: finds transcripts that don't have a matching summary yet and generates a paste-ready
instruction for an AI assistant to write each summary. Does NOT call any AI itself.

Config block at the top:
  SKILL_FILE = "skill_summary.md"   # the instruction template
  MAX_TRANSCRIPTS = 5               # max number of unsummarised transcripts to process at once

Imports:
  import os
  from lib import textutil
  from lib.paths import TRANSCRIPT_DIR, GENERATED_TRANSCRIPT_DIR, SUMMARY_DIR

Base name rules (critical — must match exactly):
  - A YouTube caption transcript: data/transcripts/Title.en.txt
    Base name = "Title" (strip the .en.txt suffix)
  - A Whisper transcript: data/generated_transcripts/Title.whisper.en.txt
    Base name = "Title" (strip the .whisper.en.txt suffix)
  - Summary output: data/summaries/Title.summary.md

Logic:
  1. Collect all transcripts from both TRANSCRIPT_DIR and GENERATED_TRANSCRIPT_DIR
     Prefer YouTube captions over Whisper transcripts if both exist for the same base name
  2. For each base name, check if data/summaries/<base>.summary.md exists
  3. If it doesn't, that transcript needs a summary
  4. Load skill_summary.md, replace {{TITLE}} with the base name and {{TRANSCRIPT}} with the
     transcript text (pass through textutil.clean_text() first)
  5. Print the assembled prompt to stdout with a header:
     "=== Paste into your AI assistant for: <base name> ==="
  6. Stop after MAX_TRANSCRIPTS (so the output is manageable)
  7. At the end, print a summary: N transcripts need summaries, N shown

Output only the file content.
```

**Expected output:** A script that scans both transcript folders, computes the set difference
against existing summaries, and prints one assembled prompt per missing summary.

**Verify:** Run the script and confirm it prints assembled prompts (not empty output). Each printed
block should start with `=== Paste into your AI assistant for: ...` and end with the full
transcript text.

---

### 08.3 — Test the summary workflow

Run `make_summaries.py` and use its output.

```cmd
python code\make_summaries.py
```

Copy the first assembled prompt block from the terminal output and paste it into your AI
assistant. The assistant should return a formatted markdown summary following the structure in
`skill_summary.md`.

Once the assistant returns the summary:
1. Create `data/summaries/` if it doesn't exist yet: `mkdir data\summaries`
2. Save the returned text as `data/summaries/<base name>.summary.md`
3. Re-run `python code\make_summaries.py` — that base name should no longer appear in the output

**Verify:** Run `make_summaries.py` a second time and confirm the count decreases by one.

---

### 08.4 — Write the real `lib/textutil.py`

The stub from Lesson 05 has `NotImplementedError` on three functions. Replace it now.

**Prompt:**
```
Replace the stub in lib/textutil.py with full implementations. The module needs:

safe_filename(text: str) -> str
  Strips characters that are illegal in Windows filenames: \ / : * ? " < > |
  Returns the cleaned string. Do not shorten the name or replace characters — just remove them.

load_languages() -> list[str]
  Reads code/languages.json if it exists; falls back to ["en", "fr", "ro"] if the file
  is missing or malformed. The JSON should be a list of language codes.

clean_text(text: str) -> str
  Strips VTT/HTML timestamp tags (e.g. <00:00:05.000>, <c>, </c>),
  strips VTT cue timing lines (e.g. "00:00:01.000 --> 00:00:05.000"),
  strips HTML entities (decode &amp; &lt; &gt; &#39; &quot;),
  strips remaining HTML tags,
  collapses multiple spaces and blank lines to single whitespace.
  Returns clean plain text.

All functions must work with only the standard library (no third-party imports).
Add a module docstring.
Output only the file content.
```

**Expected output:** A complete `lib/textutil.py` with the three functions, using only `os`,
`json`, `re`, and `html` from the standard library.

**Verify:**
```cmd
python -c "
from lib.textutil import safe_filename, clean_text, load_languages
print(safe_filename('Hello: World?'))
print(load_languages())
print(clean_text('<00:00:05.000>Hello <c>world</c>'))
"
```
Expected: `Hello World` (colon and question mark removed), `['en', 'fr', 'ro']`, `Hello world`.

---

### 08.5 — Generate `code/make_wordcloud.py`

**Prompt:**
```
Write code/make_wordcloud.py with these exact requirements:

Purpose: reads transcript files and produces word-frequency JSON for the wordcloud.html viewer.

Config block at the top:
  SELECT_BY = "input"   # "input" | "name" | "id" | "all"
  SELECT = ""           # value for name/id modes
  MERGE = False         # if True, merge all selected transcripts into one combined cloud
  TOP_N = 200           # how many words to include in the output

JSON config file support (same pattern as transcribe_audio.py):
  DEFAULT_CONFIG = "config/config_wordcloud.json"
  If sys.argv[1] is provided, use that path instead.
  Keys: select_by, select, merge, top_n

Imports: only stdlib — os, json, sys, re, collections, glob
  from lib import textutil
  from lib.paths import TRANSCRIPT_DIR, GENERATED_TRANSCRIPT_DIR, WORDCLOUD_DIR

Selection logic:
  - "input": prompt the user for a transcript file path (input()) or read from stdin
  - "name": find transcripts in both folders whose filename contains SELECT
  - "id": same but match the YouTube video ID
  - "all": use all transcripts in both folders

Word counting:
  1. For each transcript: pass through textutil.clean_text(), then lowercase
  2. Remove stop words: a short hardcoded list of ~30 English function words
     (the, a, an, is, it, in, on, at, to, of, for, and, or, but, this, that, was, are, be,
      with, as, by, from, not, we, you, i, he, she, they, have, had, has, will, do, did, does)
  3. Tokenize to words (re.findall(r'\b[a-z]{3,}\b', text))
  4. Use collections.Counter; take the top TOP_N words
  5. Output: {"words": [{"text": "word", "count": N}, ...]} sorted descending
  6. Output file: WORDCLOUD_DIR/<base_name>.word_cloud.json (or "merged.word_cloud.json" for MERGE)

Viewer: the output is consumed by wordcloud.html at the repo root (exact filename).

Output only the file content.
```

**Expected output:** A pure-stdlib script with config loading, selection logic, word counting, and
JSON output. No imports of `wordcloud`, `nltk`, `spacy`, or any third-party NLP library.

**Verify:**
```cmd
python code\make_wordcloud.py
```
(If SELECT_BY = "input", it will prompt for a path — enter the path to a transcript file.)
Check that a `.word_cloud.json` file appears in `data/wordclouds/`.

---

### 08.6 — Generate config files

**Prompt:**
```
Write two config files:

1. config/config_wordcloud.json — default word cloud config:
   {"select_by": "input", "select": "", "merge": false, "top_n": 200}

2. config/config_wordcloud.merge.json — merge all transcripts:
   {"select_by": "all", "select": "", "merge": true, "top_n": 300}

Output each with its filename as a header.
```

**Verify:** Validate both JSON files:
```cmd
python -c "import json; [json.load(open(f)) for f in ['config/config_wordcloud.json','config/config_wordcloud.merge.json']]; print('both valid')"
```

---

### 08.7 — View a word cloud

Open `wordcloud.html` in your browser (it reads the JSON files from `data/wordclouds/` via
relative path). You should see the word cloud visualisation with the words you just generated.

If the HTML file shows nothing, check:
- The browser must open `wordcloud.html` from the filesystem (it reads local JSON files)
- The JSON file must be in `data/wordclouds/` with the `.word_cloud.json` suffix
- Some browsers block local file reads; if that's the case, ask the assistant: "How do I serve
  the wordcloud.html file locally so the browser can read data/ files?" (A simple
  `python -m http.server` in the repo root usually solves it.)

---

### 08.8 — Commit

**Prompt:**
```
Give me git commands to add and commit:
  skill_summary.md
  code/make_summaries.py
  code/make_wordcloud.py
  lib/textutil.py     (replaced stub with full implementation)
  config/config_wordcloud.json
  config/config_wordcloud.merge.json

Commit message: "add make_summaries, make_wordcloud, real textutil, skill_summary template"
OS: Windows, Command Prompt.
```

**Verify:** `git log --oneline` should show seven commits.

---

## When the AI misbehaves

**`make_summaries.py` strips only `.en.txt` but not `.whisper.en.txt`, leaving the wrong base name.**
The base name rules are strict: `.en.txt` → strip `.en.txt`; `.whisper.en.txt` → strip
`.whisper.en.txt`. A regex like `re.sub(r'\.(whisper\.)?en\.txt$', '', filename)` handles both.
Ask: "The base name still contains `.whisper` — can you fix the suffix stripping to handle both
`.en.txt` and `.whisper.en.txt` in one step?"

**The assistant imports `wordcloud` or `nltk` in `make_wordcloud.py`.**
Those are not in the project's requirements. Push back: "This script must use only the standard
library. Can you remove the `wordcloud` and `nltk` imports and implement word frequency counting
with `collections.Counter` and a simple regex tokenizer?"

**`clean_text()` leaves behind VTT timing lines like `WEBVTT` or `Kind: captions`.**
VTT files start with a `WEBVTT` header block. Add a strip step: remove any line that is
`WEBVTT`, `Kind: ...`, `Language: ...`, or a cue identifier (bare number on its own line).
Ask: "The cleaned text still has lines like 'WEBVTT', 'Kind: captions', and bare numbers.
Can you add stripping for the VTT header block and cue IDs?"

**`make_summaries.py` prints an empty block (no transcript text in the output).**
Usually means `clean_text()` over-aggressively stripped everything. Add a diagnostic: print
the first 200 characters of the transcript before and after `clean_text()` and confirm the
stripped version is not empty.

---

## What you have now

Files added this lesson:

```
learn-better/
    skill_summary.md            (new — reusable summarisation instruction set)
    code/
        make_summaries.py       (new)
        make_wordcloud.py       (new)
    lib/
        textutil.py             (replaced stub with full implementation)
    config/
        config_wordcloud.json        (new)
        config_wordcloud.merge.json  (new)
    data/
        summaries/              (git-tracked — authored content goes here)
        wordclouds/             (generated — git-ignored)
```

Repo state: summarisation and word-cloud pipeline complete. You can now go from transcript to
summary to word cloud without leaving the terminal. Seven commits on `main`.

---

## Next →

[Lesson 09 — TTS and the Full Pipeline](09_tts_and_full_pipeline.md)

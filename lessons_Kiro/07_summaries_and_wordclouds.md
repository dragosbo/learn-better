# Lesson 07 — Summaries + word clouds (AI as author, data/JS split)

**You'll build:** `code/make_summaries.py` + a reusable `skill_summary.md` (the AI
*authors* the summaries), and `code/make_wordcloud.py` + `wordcloud.html` (Python
produces data, the browser renders it). Runners `s`, `d`, `wc`.
**Complexity:** ⭐⭐⭐⭐   **Est. time:** ~60–90 min

> **Assistant-agnostic.** Any AI assistant works. This is the lesson where the
> assistant becomes an *author*, not just a coder.

---

## Prerequisites (from Lesson 06)

- Transcripts on disk (`data/transcripts/*.en.txt` and/or
  `data/generated_transcripts/*.whisper.en.txt`).
- `lib/` in place; runner + config patterns established.

---

## Re-orient the AI (paste after a crash/restart)

```
Context: Lesson 07 of building a YouTube→study-material toolkit with your help.
OS: <your OS>. Repo: learn-better/ with transcripts under data/transcripts/ and
data/generated_transcripts/, a reusable lib/, config-driven tools + runners.
Goal now: (1) make_summaries.py that finds transcripts needing a summary and prints
a paste-ready instruction; a reusable skill_summary.md defining the summary format;
the AI then authors summaries into data/summaries/. (2) make_wordcloud.py →
data/wordclouds/*.word_cloud.json rendered by wordcloud.html. Runners s / d / wc.
Last thing done: <e.g. "wrote skill_summary.md">. Please continue from there.
```

---

## Concepts (what this lesson teaches about working with AI)

1. **The script-vs-AI boundary.** Some work is deterministic (find files, dedupe,
   check what's done) → a script. Some is reasoning (write a good summary) → the AI.
   Name the boundary and split the work along it.
2. **A reusable skill file.** Put the *format/rules* in one committed file
   (`skill_summary.md`) so every summary is consistent and the "prompt" is just
   "apply the skill to these files."
3. **Data vs. presentation.** The Python side emits renderer-agnostic **data**
   (JSON); a static HTML page renders it client-side. No plotting dependency.

---

## Step-by-step

### 07.1 — Define the summary format once (`skill_summary.md`)

**Ask your assistant to** write a reusable spec for what a good summary looks like.

> **Prompt:**
> "Create `skill_summary.md`: a reusable instruction set for turning a video
> transcript into a concise, structured summary. Include: the naming rule
> (`<base>.summary.md` under `data/summaries/`), rules (be concise, ground
> everything in the transcript, neutral tone), and a fixed Markdown template
> (title/metadata, one-line takeaway, timestamped table of contents, per-section
> bullets, key takeaways, strengths, weaknesses, who-should-watch), plus a
> pre-save checklist. This is the single source of truth for summary format."

**Expected response:** a `skill_summary.md` with a clear template + checklist. The
value: future summaries are a one-liner ("apply `skill_summary.md` to X") instead of
re-describing the format each time.

**Verify:** the file has a concrete template you'd be happy to see filled in.

### 07.2 — Build the prep script (the deterministic half)

**Ask your assistant to** write a tool that finds transcripts lacking a summary and
prints a ready-to-paste instruction — explicitly *not* writing the prose itself.

> **Prompt:**
> "Create `code/make_summaries.py`. It should: find every English transcript from
> BOTH `data/transcripts/*.en.txt` and `data/generated_transcripts/*.whisper.en.txt`
> (paths from `lib/paths.py`); pick ONE per video (captions preferred; dedupe by the
> `[<id>]` in the filename); check which already have `data/summaries/<base>.summary.md`;
> print done vs. missing; and for the missing ones print a single paste-ready
> instruction telling an AI to apply `skill_summary.md` and save each to
> `data/summaries/<base>.summary.md`. It must NOT try to write the summaries itself —
> that's the AI's job. Explain in comments why the split exists."

**Expected response:** a script that lists and instructs, never authors. This honest
"a batch script can't reason, so it hands off" design is the heart of the lesson.

**Verify:** run it (via a new `s` runner — ask for `s.bat`/`s.sh`). It lists your
transcripts and prints an instruction naming the exact files + output paths.

### 07.3 — Have the AI author the summaries (the reasoning half)

**Ask your assistant to** do exactly what the printed instruction says.

> **Prompt (paste what `make_summaries.py` printed):**
> "Apply skill_summary.md to these transcripts and save each to
> data/summaries/<base>.summary.md:
> - data/transcripts/<Video A> [<id>].en.txt
> - data/generated_transcripts/<Video B> [<id>].whisper.en.txt"

**Expected response / aside:** the assistant reads each transcript and writes a
structured `.summary.md` per `skill_summary.md`. *(Kiro can create the files
directly; a chat assistant returns the Markdown to save.)* Existing summaries are
left alone, so re-running `s` only surfaces new ones.

**Verify:** `data/summaries/` gets one well-structured `.summary.md` per video, each
grounded in its transcript (no invented facts) and following the template.

> *Aside — `data/summaries/` is the one tracked output.* Unlike audio/transcripts
> (regenerated, git-ignored), summaries are *authored content*. Note that `data/` is
> ignored **except** `data/summaries/` — a `.gitignore` negation you'll wire up when
> you consolidate outputs (Lesson 08).

### 07.4 — Word cloud: data (Python) + rendering (JS)

**Ask your assistant to** build the data side, then a separate static renderer.

> **Prompt:**
> "Create `code/make_wordcloud.py`: read a transcript (from `data/transcripts/` or
> `data/generated_transcripts/`, paths from `lib/paths.py`), strip timestamps,
> tokenize (Unicode-aware, keep accented fr/ro letters), drop stopwords (built-in
> en/fr/ro lists) + very short words, count frequencies, and write
> `data/wordclouds/<base>.word_cloud.json`. Config-driven (`select_by` name/id/all,
> plus a merge mode to combine several transcripts into one cloud). Skip-if-exists.
> NO plotting library — just emit JSON. Then a separate static `wordcloud.html` that
> loads a chosen JSON and renders a cloud client-side with a CDN JS library
> (e.g. wordcloud2.js). Add runners `d` (one file) and `wc` (config batch/merge)."

**Expected response:** a Python script emitting renderer-agnostic JSON + a static
`wordcloud.html`, plus `d`/`wc` runners. The split means you could swap the JS
library later without touching the Python.

**Verify:** `d` (or `wc config/config_wordcloud.json`) writes a
`data/wordclouds/*.word_cloud.json`; opening `wordcloud.html` and loading that JSON
renders a word cloud. A single-language guard should refuse a mixed-language batch.

---

## When the AI misbehaves

- **It tries to make `make_summaries.py` write the summaries itself.** Push back:
  the script only *finds and instructs*; authoring is a separate AI step. That
  separation is the whole point.
- **A summary invents facts not in the transcript.** Reject it and cite the rule
  from `skill_summary.md` ("ground everything in the transcript"); ask it to redo
  grounded strictly in the source.
- **Summaries come out inconsistent.** The format lives in `skill_summary.md` — tell
  the assistant to follow it exactly, and tweak the *skill file* (one place) rather
  than re-describing format each time.
- **The word cloud script reaches for `matplotlib`/`wordcloud` (plotting).** No —
  Python emits JSON only; rendering is client-side JS. Ask it to remove any plotting
  dependency.
- **Mixed-language batch produces garbage.** A cloud uses one stopword list; the
  tool should refuse a mixed-language selection with a clear message — ask for that
  guard if missing.

---

## What you have now

```
learn-better/
├── skill_summary.md                     # reusable summary format (tracked)
├── code/make_summaries.py               # finds + instructs (script half)
├── code/make_wordcloud.py               # transcript → word_cloud.json (data)
├── wordcloud.html                       # renders a cloud client-side (JS)
├── s / d / wc  runners (.bat + .sh)
└── data/
    ├── summaries/        # <base>.summary.md  (AI-authored; will be TRACKED)
    └── wordclouds/       # <base>.word_cloud.json  (git-ignored)
```
The AI is now an author working to a spec, and you have a clean data/presentation
split for visualization.

---

## Next → Lesson 08 — TTS + tidy outputs + full pipeline

You'll add text-to-speech (Piper — free, local, CPU), an audio re-encoder, run the
whole pipeline end to end (download → transcribe → summarize → speak), and do a
cross-cutting refactor to consolidate every output under a single `data/` root
without ever destroying your inputs.

# Lesson 07 — Runners and Automation

**You'll build:** The complete `scripts/` runner set (all `.bat` / `.sh` pairs, including the
remaining ones for scripts from future lessons), `init.bat` (the session initialiser that adds
`scripts/` to PATH), and `code/compare_transcripts.py` (a quality-check tool that compares Whisper
output against YouTube captions).
**Complexity:** ⭐⭐⭐⭐☆   **Est. time:** ~60–75 min
**AI tasks in this lesson:** batch file generation, PATH reasoning, difflib usage, quality metric design

---

## Prerequisites

- Lesson 06 completed: `transcribe_audio.py` working, `w.bat` / `w.sh` exist
- Runners `p.*`, `r.*`, `t.*`, `w.*` already in `scripts/`
- At least one file in `data/transcripts/` (YouTube caption) and one matching file in
  `data/generated_transcripts/` (Whisper) for the comparison test

---

## Re-orient the AI

> Paste this block at the start of a new session, or any time the assistant loses context:
>
> "I'm working on the **learn-better** repo — a Python tool that downloads YouTube audio and
> transcripts, transcribes locally with faster-whisper, and generates summaries and word clouds.
> We're on **Lesson 07 — Runners and Automation**. Runners p, r, t, w already exist in scripts/.
> We have NOT yet written init.bat, the remaining runners (s, d, wc, v, a, c), or
> compare_transcripts.py. OS: Windows. Conda env: `learn-better`. Please continue from
> where I left off."

---

## Concepts

1. **`init.bat` uses `%~dp0`, not `%CD%`.** `%~dp0` expands to the directory where `init.bat`
   lives (the repo root), regardless of where you run it from. `%CD%` expands to the current
   working directory — if you're anywhere other than the repo root, the PATH addition points to
   the wrong folder. The difference matters the first time you run `init` from inside a subfolder.

2. **`init.bat` must be called, not double-clicked.** Running it in a child process (double-click,
   or running it as a subprocess) sets PATH for that child and then throws it away when the child
   exits. To keep the PATH change, run it in your current Command Prompt session: type `init` (not
   `init.bat`) at the prompt.

3. **Quality measurement makes the pipeline observable.** Once you can score Whisper output against
   a known-good caption transcript, you can choose model sizes and languages confidently.
   `compare_transcripts.py` is a debugging tool, not a production script — but it closes the loop
   on whether the transcription is working well.

---

## Step-by-step

### 07.1 — Create `init.bat`

**Prompt:**
```
Write scripts/init.bat — a Windows batch file that adds the scripts/ folder to the current
session's PATH so I can run shortcut commands (r, t, w, p, etc.) from any directory in the
project.

Requirements:
  - Must use %~dp0 (the directory where init.bat lives, i.e. the repo root), NOT %CD%
  - The PATH modification should affect only the current cmd session
  - Print a confirmation message after setting the PATH
  - File name when run: just type "init" at the prompt (not "init.bat")

Important: this file should NOT activate the conda environment — that is each runner's job.
Output only the file content.
```

**Expected output:**
```bat
@echo off
set "PATH=%~dp0scripts;%PATH%"
echo [init] scripts/ added to PATH. You can now type: r, t, w, p, s, d, wc, v, a
```

**Verify:** The file must have `%~dp0scripts` (not `%CD%\scripts`). Ask the assistant to explain
the difference if it uses `%CD%`. Then run:
```cmd
init
echo %PATH%
```
Confirm the path to your `scripts/` folder appears near the beginning of the output.

---

### 07.2 — Generate the remaining runners

Scripts `s`, `d`, `wc`, `v`, and `a` are for lessons 08 and 09. Create them now so `init` exposes
a complete set from the start.

**Prompt:**
```
Write the remaining runner shortcut files for my learn-better project. Each needs a .bat and .sh
pair. All follow the same pattern: activate conda env, run the python script.

Runners to create:
  s.bat / s.sh   → python code\make_summaries.py
  d.bat / d.sh   → python code\make_wordcloud.py (no config arg needed)
  wc.bat / wc.sh → python code\make_wordcloud.py %* (passes optional config arg)
  v.bat / v.sh   → python code\generate_speech.py %*
  a.bat / a.sh   → python code\reencode_audio.py %*

Pattern for .bat:
  @echo off
  call conda activate learn-better
  python code\<script>.py [%* if applicable]

Pattern for .sh:
  #!/usr/bin/env bash
  conda activate learn-better
  python code/<script>.py ["$@" if applicable]

Note: d.bat does NOT pass %* (no config arg). wc.bat, v.bat, a.bat DO pass %*.
Output each file with its filename as a header. Show all 10 files.
```

**Expected output:** Ten files. `d.bat` ends with just `python code\make_wordcloud.py` (no `%*`).
`wc.bat` ends with `python code\make_wordcloud.py %*`. Same distinction in their `.sh` pairs.

**Verify:** Open `d.bat` and `wc.bat` and confirm the difference — `d` runs without arguments,
`wc` passes arguments through.

---

### 07.3 — Generate `code/compare_transcripts.py`

**Prompt:**
```
Write code/compare_transcripts.py — a script that compares two transcripts for the same video:
  1. The YouTube caption transcript in data/transcripts/ (e.g. Title.en.txt — may have VTT timestamps)
  2. The Whisper-generated transcript in data/generated_transcripts/ (e.g. Title.whisper.en.txt)

The script should:
  - Accept the base name (without extension) as a command-line argument, or let the user
    configure it at the top as BASE_NAME = "..."
  - Find the matching files in both folders
  - Normalize both texts: strip VTT/HTML tags, strip timestamps, lowercase, tokenize to words
  - Use difflib.SequenceMatcher to compute a similarity ratio
  - Print: total words in each transcript, words in common, similarity percentage, and a
    short quality label ("excellent" > 90%, "good" 75-90%, "fair" 50-75%, "poor" < 50%)
  - Optionally print the first N differing segments side by side

Imports:
  import os, sys, difflib, re
  from lib import textutil
  from lib.paths import TRANSCRIPT_DIR, GENERATED_TRANSCRIPT_DIR

Output only the file content.
```

**Expected output:** A script that loads two files, normalizes them, computes similarity, and
prints a readable report. The normalization step is critical — raw VTT files have timestamps like
`00:01:23.456 --> 00:01:27.890` that must be stripped before comparison.

**Verify:** Save the file. Then run (substitute a real base name):
```cmd
python code\compare_transcripts.py "VideoTitle"
```
Expected output (example):
```
YouTube captions: 2,341 words
Whisper output:   2,298 words
Words in common:  2,104
Similarity:       89.7%
Quality:          good
```

---

### 07.4 — Test `init.bat` and run a full one-letter command

```cmd
init
r
```

`init` adds `scripts/` to PATH. `r` should then launch `read_channel.py` just as if you had typed
`python code\read_channel.py`.

**Verify:** After `init`, confirm you can run `r`, `t`, `w`, `p` without typing `python code\...`.
If any runner is "not recognized", check that the corresponding `.bat` file exists in `scripts/`
and that `init.bat` used `%~dp0scripts` (not `%CD%\scripts`).

---

### 07.5 — Commit

**Prompt:**
```
Give me git commands to add and commit these new files:
  scripts/init.bat
  scripts/s.bat  scripts/s.sh
  scripts/d.bat  scripts/d.sh
  scripts/wc.bat scripts/wc.sh
  scripts/v.bat  scripts/v.sh
  scripts/a.bat  scripts/a.sh
  code/compare_transcripts.py

Commit message: "add init.bat, remaining runners, compare_transcripts.py"
OS: Windows, Command Prompt.
```

**Verify:** `git log --oneline` should show six commits.

---

## When the AI misbehaves

**The assistant writes `init.bat` with `%CD%\scripts` instead of `%~dp0scripts`.**
Ask it to explain the difference: "What's the difference between `%CD%` and `%~dp0` in a Windows
batch file?" It should explain that `%~dp0` is the file's own directory, while `%CD%` is the
current directory when the script runs — which might be anywhere. For `init.bat`, only `%~dp0`
is correct.

**The assistant says `init.bat` should be run with `call init` or double-clicked.**
It should be run as `init` (plain, no call, in your current prompt). `call` is for calling one
`.bat` from another — it still works here but is unnecessary. Double-clicking opens a child cmd
window and then closes it; the PATH change is lost. Push back: "I need to run this by typing
`init` at the Command Prompt so the PATH change stays in my current session."

**`compare_transcripts.py` crashes because the VTT timestamp stripping is incomplete.**
YouTube VTT files have multi-line cue blocks with timestamps (`-->` notation) and sometimes HTML
tags (`<c>`, `<00:00:01.234>`). A regex like `r'\d{2}:\d{2}:\d{2}\.\d{3} --> .*'` only strips
some lines. Ask: "The comparison is giving near-zero similarity because the timestamp lines
aren't fully stripped. Can you improve the normalization to handle VTT cue blocks, including
lines with only timestamps, blank lines between cues, and inline timing tags like `<00:00:05>`?"

**A runner fails with `'conda' is not recognized`.**
The Anaconda Prompt shortcut sets up conda's PATH; a plain Command Prompt does not. Options:
1. Use the Anaconda Prompt shortcut
2. Run `init` first in a conda-aware prompt
3. Replace `call conda activate learn-better` with the full path to the activate script

Ask the assistant: "conda is not found in my plain Command Prompt. What's the minimal change
to the .bat file so it works without modifying the system PATH?"

---

## What you have now

Files added this lesson:

```
learn-better/
    scripts/
        init.bat         (new — session PATH initialiser)
        s.bat  / s.sh    (new)
        d.bat  / d.sh    (new)
        wc.bat / wc.sh   (new)
        v.bat  / v.sh    (new)
        a.bat  / a.sh    (new)
    code/
        compare_transcripts.py   (new)
```

Full runner set:

| Key | Script | Config arg |
|-----|--------|-----------|
| `c` | conda activate | — |
| `p` | list_playlists.py | — |
| `r` | read_channel.py | — |
| `t` | read_transcript.py | — |
| `w` | transcribe_audio.py | optional |
| `s` | make_summaries.py | — |
| `d` | make_wordcloud.py | — |
| `wc` | make_wordcloud.py | optional |
| `v` | generate_speech.py | optional |
| `a` | reencode_audio.py | optional |

Repo state: all runner shortcuts in place, `init.bat` wires them to a one-letter workflow.
Six commits on `main`.

---

## Next →

[Lesson 08 — Summaries and Word Clouds](08_summaries_and_wordclouds.md)

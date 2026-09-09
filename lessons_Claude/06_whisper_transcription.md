# Lesson 06 — Whisper Transcription

**You'll build:** `code/transcribe_audio.py` — a config-driven script that transcribes local audio
files using faster-whisper, writes results to `data/generated_transcripts/`, and reads its
parameters from `config/config_transcribe.json` (and named variants). Plus the runner
`scripts/w.bat` / `scripts/w.sh`.
**Complexity:** ⭐⭐⭐⭐☆   **Est. time:** ~75–90 min
**AI tasks in this lesson:** config-driven script design, JSON schema design, error-from-output
debugging

---

## Prerequisites

- Lesson 05 completed: `code/read_channel.py`, audio in `data/audio/`, config file skeleton in
  `config/`, stubs for `lib/textutil.py` and `lib/youtube.py`
- faster-whisper installed in the conda env
- At least one `.mp3` audio file in `data/audio/` to transcribe

---

## Re-orient the AI

> Paste this block at the start of a new session, or any time the assistant loses context:
>
> "I'm working on the **learn-better** repo — a Python tool that downloads YouTube audio and
> transcripts, transcribes locally with faster-whisper, and generates summaries and word clouds.
> We're on **Lesson 06 — Whisper Transcription**. Files so far include `code/read_channel.py`,
> `code/read_transcript.py`, `config/config_transcribe.json`, and all runners. We have NOT yet
> written `transcribe_audio.py`. OS: Windows. Conda env: `learn-better`. Please continue from
> where I left off."

---

## Concepts

1. **Config files let the same script behave differently without editing Python.** A single
   `transcribe_audio.py` can transcribe everything, transcribe one file by name, or transcribe by
   playlist, depending on which JSON config you pass. The script reads the config, merges it with
   its defaults, and runs. No copy-paste variants needed.

2. **SELECT_BY modes isolate the selection concern.** `select_by` controls *how* to find files
   (`"name"`, `"id"`, `"all"`, `"source"`); `select` carries the value for those modes. Adding a
   new selection mode is one small addition in the config handler, not a structural rewrite.

3. **Apply proxy bypass before importing faster-whisper.** `faster-whisper` uses CTranslate2, which
   can inherit the system's `HTTP_PROXY` setting and route all GPU/CPU calls through a proxy,
   causing slow or failed transcriptions in corporate environments. `net.apply_no_proxy_env()` must
   be called *before* `from faster_whisper import WhisperModel` — not just before the network
   calls.

---

## Step-by-step

### 06.1 — Design the config schema

**Prompt:**
```
I want to write a transcription script that reads parameters from a JSON config file.
The script will use faster-whisper to transcribe audio files from data/audio/.

The JSON config needs to support these use cases:
  1. Transcribe all files in data/audio/
  2. Transcribe files whose name matches a string (e.g. a video title fragment)
  3. Transcribe one file by its YouTube video ID
  4. Transcribe files that came from a specific playlist/channel/search (the "source" mode,
     which re-fetches the video list to find which audio files to process)

Before writing code: propose the JSON config schema for all four use cases. For each use case,
show me an example config JSON. Use short, clear key names. Think step by step.
```

**Expected output:** The assistant should propose a schema with at least:

```json
{
  "select_by": "all | name | id | source",
  "select": "value for name/id modes; ignored for all",
  "model_size": "tiny | base | small | medium | large-v2",
  "device": "cpu | cuda | auto",
  "compute_type": "int8 | float16 | float32",
  "task": "transcribe | translate",
  "language": "en | fr | null (auto-detect)",
  "playlist_id": "(for source mode only)",
  "channel": "(for source mode only)",
  "search": "(for source mode only)",
  "limit": 10
}
```

**Verify:** All four `select_by` modes should be present. If `"source"` mode is missing, push back
and explain that it means "re-use the same video list as read_channel.py to find matching audio
files."

---

### 06.2 — Generate `code/transcribe_audio.py`

**Prompt:**
```
Write code/transcribe_audio.py with these exact requirements:

Config block at the top (all-caps, clearly commented — these are the defaults):
  SELECT_BY = "all"   # "name" | "id" | "all" | "source"
  SELECT = ""         # value for name/id; ignored for all/source
  MODEL_SIZE = "small"
  DEVICE = "cpu"
  COMPUTE_TYPE = "int8"
  TASK = "transcribe"
  LANGUAGE = "en"

JSON config file support:
  DEFAULT_CONFIG = "config/config_transcribe.json"
  If sys.argv[1] is provided, use that path instead of DEFAULT_CONFIG.
  Load the JSON and override the defaults. Use .get() so missing keys fall back to defaults.
  JSON keys: select_by, select, model_size, device, compute_type, task, language,
             playlist_id, channel, search, limit, languages

CRITICAL import order:
  1. Standard library imports (os, json, sys, glob)
  2. from lib import net
  3. net.apply_no_proxy_env()   ← must happen BEFORE the faster_whisper import
  4. from faster_whisper import WhisperModel
  5. from lib import textutil, youtube
  6. from lib.paths import AUDIO_DIR, GENERATED_TRANSCRIPT_DIR

Selection logic:
  - "all": glob AUDIO_DIR for *.mp3 (and *.wav, *.m4a)
  - "name": glob AUDIO_DIR for files containing SELECT in their name
  - "id": find file in AUDIO_DIR whose name contains SELECT (the video id)
  - "source": use youtube.build_url + youtube.list_videos, then match audio files by video id

Transcription loop:
  - Load WhisperModel(MODEL_SIZE, device=DEVICE, compute_type=COMPUTE_TYPE) once before the loop
  - For each audio file: call model.transcribe(path, task=TASK, language=LANGUAGE or None)
  - Output file: GENERATED_TRANSCRIPT_DIR/<base>.whisper.en.txt (use textutil.safe_filename)
  - Write each segment's text, skip if output file already exists (do not re-transcribe)
  - Print progress: file name, number of segments written

Use GENERATED_TRANSCRIPT_DIR from lib.paths for the output folder.
Output only the file content.
```

**Expected output:** The script with the exact import order described, config loading via
`sys.argv`, and the transcription loop. The critical detail is that `net.apply_no_proxy_env()` is
called at module level, before `from faster_whisper import WhisperModel`.

**Verify:**
- Open the file and check the import section. `net.apply_no_proxy_env()` must appear *before*
  the `from faster_whisper import WhisperModel` line.
- Check that the output path uses `GENERATED_TRANSCRIPT_DIR`, not `TRANSCRIPT_DIR` — those are
  different folders (`data/generated_transcripts/` vs `data/transcripts/`).
- Check that `language=None` is passed to `model.transcribe()` when `LANGUAGE` is empty or None
  (this enables auto-detection).

---

### 06.3 — Generate the runner and config variants

**Prompt:**
```
Write these files:

1. scripts/w.bat — runner for transcribe_audio.py
   Pattern: call conda activate learn-better, then python code\transcribe_audio.py %*
   The %* passes any extra argument (the config path) through.

2. scripts/w.sh — same for Linux/macOS
   Pattern: conda activate learn-better, then python code/transcribe_audio.py "$@"

3. config/config_transcribe.all.json — transcribe all audio files, small model, CPU, int8

4. config/config_transcribe.id.json — transcribe by video ID, model small, CPU, int8
   Leave "select" as empty string (user fills in the ID at run time by editing the file)

5. config/config_transcribe.name.json — transcribe by title fragment

Output each file separately with its filename as a header.
```

**Expected output:** Five files. The `.bat` and `.sh` runners pass `%*` / `"$@"` so the user can
run `w config\config_transcribe.id.json` to override the default config. The JSON files should be
minimal — only the keys needed for that use case.

**Verify:** Check that `w.bat` ends with `python code\transcribe_audio.py %*` (not without the
`%*`). Without it, you can't pass a custom config path on the command line.

---

### 06.4 — First transcription run

```cmd
conda activate learn-better
python code\transcribe_audio.py
```

**Expected outcome:**

**A — Success:** You see segment counts and files appear in `data/generated_transcripts/` with
names like `VideoTitle.whisper.en.txt`. Open one and verify it contains readable text.

**B — `CUDA out of memory` or `CUDA not available`:** If you have a GPU and CUDA fails, set
`DEVICE = "cpu"` in the config or at the top of the script. CPU transcription is slower but
always works.

**C — Slow (several minutes for a short audio file):** Normal for CPU with a medium or large
model. For testing, set `MODEL_SIZE = "tiny"` — it is much faster and accurate enough to verify
the pipeline.

**D — Any error:** See the debugging cycle from Lesson 04 — paste the full traceback into the
assistant.

**Verify:**
```cmd
dir data\generated_transcripts
```
Files should end in `.whisper.en.txt`.

---

### 06.5 — Test a named config

Run with a config variant to verify the `%*` passthrough works:

```cmd
python code\transcribe_audio.py config\config_transcribe.all.json
```

**Verify:** Same result as the default (since `config_transcribe.all.json` also selects all). This
confirms the config override path works. If the script ignores the argument and behaves
differently from what the config specifies, check the `sys.argv` parsing logic.

---

### 06.6 — Commit

**Prompt:**
```
Give me git commands to add and commit:
  code/transcribe_audio.py
  scripts/w.bat  scripts/w.sh
  config/config_transcribe.all.json
  config/config_transcribe.id.json
  config/config_transcribe.name.json

Commit message: "add transcribe_audio.py with config variants and w.bat/w.sh runners"
OS: Windows, Command Prompt.
```

**Verify:** `git log --oneline` should show five commits.

---

## When the AI misbehaves

**The assistant places `net.apply_no_proxy_env()` after `from faster_whisper import WhisperModel`.**
This is the most important correctness check in this lesson. Push back explicitly: "The proxy
bypass must happen before faster-whisper is imported — CTranslate2 reads the proxy environment
variable at import time. Can you move `net.apply_no_proxy_env()` to before the faster_whisper
import?" Show the exact required order from step 06.2.

**The assistant uses `TRANSCRIPT_DIR` instead of `GENERATED_TRANSCRIPT_DIR` for output.**
`TRANSCRIPT_DIR` = `data/transcripts/` (YouTube captions, from Lesson 05).
`GENERATED_TRANSCRIPT_DIR` = `data/generated_transcripts/` (Whisper output, this lesson).
Push back: "The output folder for Whisper transcriptions should be `GENERATED_TRANSCRIPT_DIR`
(`data/generated_transcripts/`), not `TRANSCRIPT_DIR`. Can you fix that import and the path?"

**The assistant re-transcribes files that already have a `.whisper.en.txt` output.**
This wastes time. The skip check should be: if the output file already exists, print a skip
message and continue. Ask: "The script should skip files that have already been transcribed.
Can you add a check at the start of the loop: if the output `.whisper.en.txt` file already
exists, skip it?"

**`model.transcribe()` returns nothing or the text is empty.**
Usually means the audio file is corrupt or the wrong format. Verify the file plays correctly:
`ffplay data\audio\<file>.mp3`. Also check `LANGUAGE` — if set to the wrong language code,
Whisper may transcribe gibberish. Try `LANGUAGE = None` (auto-detect) as a diagnostic.

---

## What you have now

Files added this lesson:

```
learn-better/
    code/
        transcribe_audio.py     (new)
    scripts/
        w.bat / w.sh            (new)
    config/
        config_transcribe.json       (from Lesson 05)
        config_transcribe.all.json   (new)
        config_transcribe.id.json    (new)
        config_transcribe.name.json  (new)
    data/
        generated_transcripts/   (generated — git-ignored)
```

Repo state: full local transcription pipeline working. Audio → Whisper → generated transcript.
Five commits on `main`.

---

## Next →

[Lesson 07 — Runners and Automation](07_runners_and_automation.md)

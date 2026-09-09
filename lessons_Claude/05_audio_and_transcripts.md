# Lesson 05 — Audio and Transcripts

**You'll build:** `code/read_channel.py` (audio download) and `code/read_transcript.py` (caption
download), a first `config/config_transcribe.json`, and the runner shortcuts `scripts/r.bat` /
`scripts/r.sh` and `scripts/t.bat` / `scripts/t.sh`.
**Complexity:** ⭐⭐⭐☆☆   **Est. time:** ~75–90 min
**AI tasks in this lesson:** multi-file creation, config design, format options reasoning

---

## Prerequisites

- Lesson 04 completed: `code/list_playlists.py`, runner `scripts/p.bat`, `lib/net.py` stub, all committed
- `lib/paths.py` exists with `AUDIO_DIR`, `TRANSCRIPT_DIR`
- conda env `learn-better` active, yt-dlp installed

---

## Re-orient the AI

> Paste this block at the start of a new session, or any time the assistant loses context:
>
> "I'm working on the **learn-better** repo — a Python tool that downloads YouTube audio and
> transcripts, transcribes locally with faster-whisper, and generates summaries and word clouds.
> We're on **Lesson 05 — Audio and Transcripts**. Files so far: `lib/paths.py`, `lib/net.py` (stub),
> `code/list_playlists.py`, `scripts/p.bat`, `scripts/p.sh`. We have NOT yet written
> `read_channel.py`, `read_transcript.py`, or any config files. OS: Windows. Conda env:
> `learn-better`. Please continue from where I left off."

---

## Concepts

1. **Two download modes, two scripts.** Audio download (`read_channel.py`) and caption/transcript
   download (`read_transcript.py`) are deliberately separate scripts. Transcripts are free and
   fast; audio is large and slow. You often want one without the other.

2. **Selection by playlist, channel URL, or search.** Both scripts support three input modes —
   a playlist ID, a channel handle, or a search string. A single `PLAYLIST_ID` / `CHANNEL` /
   `SEARCH` / `LIMIT` config block handles all three. Only one needs to be non-empty.

3. **Config files extend the top-of-file defaults.** For scripts you run frequently with different
   parameters, a JSON config file in `config/` is cleaner than editing the Python file each time.
   The pattern: top-of-file variables are the defaults; if a config file is passed (or exists at a
   well-known path), it overrides those defaults.

---

## Step-by-step

### 05.1 — Discuss the two-script design

**Prompt:**
```
I want to write two scripts for my YouTube tool:
1. read_channel.py — downloads audio files from YouTube using yt-dlp
2. read_transcript.py — downloads auto-generated captions/transcripts using yt-dlp

Both scripts should support three ways to identify videos:
  - By playlist ID (e.g. PLxxxxx)
  - By channel handle (e.g. @SomeChannel)
  - By search query (e.g. "python tutorial")

For read_channel.py, the audio format should be configurable (mp3 default), as should quality.
For read_transcript.py, the language(s) to try should be configurable.

Both scripts need to call lib.net.apply_no_proxy_env() before any network calls, and import
output paths from lib.paths.

Before writing any code: list the config variables each script needs at the top, and explain
the selection priority (if PLAYLIST_ID is set, use it; else if CHANNEL is set, use that; etc.).
```

**Expected output:** The assistant should propose configs like:

For `read_channel.py`:
- `PLAYLIST_ID`, `CHANNEL`, `SEARCH`, `LIMIT` (selection — only one used)
- `DOWNLOAD` (whether to actually download or just list)
- `AUDIO_FORMAT` (e.g. `"mp3"`)
- `AUDIO_QUALITY` (e.g. `"192"`)

For `read_transcript.py`:
- `PLAYLIST_ID`, `CHANNEL`, `SEARCH`, `LIMIT` (same selection block)

And a priority rule: PLAYLIST_ID → CHANNEL → SEARCH, with an error if none are set.

**Verify:** Confirm both configs include all four selection variables (`PLAYLIST_ID`, `CHANNEL`,
`SEARCH`, `LIMIT`). If `LIMIT` is missing, push back — without it a channel query will try to
fetch every video, which can be thousands.

---

### 05.2 — Generate `code/read_channel.py`

**Prompt:**
```
Write code/read_channel.py with these exact requirements:

Config block at the top (all-caps, clearly commented):
  PLAYLIST_ID = ""      # playlist ID (e.g. PLxxxxx); takes priority over CHANNEL/SEARCH
  CHANNEL = "@handle"   # channel handle; used if PLAYLIST_ID is empty
  SEARCH = ""           # search query; used if PLAYLIST_ID and CHANNEL are both empty
  LIMIT = 10            # max number of videos to process
  DOWNLOAD = True       # if False, just list videos without downloading
  AUDIO_FORMAT = "mp3"  # output audio format
  AUDIO_QUALITY = "192" # audio quality in kbps (for mp3)

Imports:
  import os
  from lib import net, textutil, youtube
  from lib.paths import AUDIO_DIR

Logic:
  1. Call net.apply_no_proxy_env() at the very start
  2. Build the source URL using youtube.build_url(PLAYLIST_ID, CHANNEL, SEARCH, LIMIT)
     which returns (label, url)
  3. List videos with youtube.list_videos(url, LIMIT) → list of (vid_id, title) tuples
  4. For each video: print the title; if DOWNLOAD is True, call
     youtube.download_audio(vid_id, AUDIO_DIR, AUDIO_FORMAT, AUDIO_QUALITY)
  5. Print a summary: N videos found, N downloaded

Use AUDIO_DIR from lib.paths as the output folder (do not hardcode the path).
Output only the file content.
```

**Expected output:** A clean script matching that spec. The config block should be at the top,
clearly separated from imports. The call to `net.apply_no_proxy_env()` should be the first
executable line. Paths should use `AUDIO_DIR` throughout.

**Verify:** Check for `from lib.paths import AUDIO_DIR` (not `DATA_DIR`). Check that
`net.apply_no_proxy_env()` appears before any yt-dlp call. Check that `DOWNLOAD = True` controls
whether actual downloading happens — it's the dry-run flag.

---

### 05.3 — Generate `code/read_transcript.py`

**Prompt:**
```
Write code/read_transcript.py with these exact requirements:

Config block at the top:
  PLAYLIST_ID = ""     # playlist ID; takes priority over CHANNEL/SEARCH
  CHANNEL = "@handle"  # channel handle; used if PLAYLIST_ID is empty
  SEARCH = ""          # search query; used if PLAYLIST_ID and CHANNEL are both empty
  LIMIT = 10           # max number of videos

Imports:
  import os
  from lib import net, textutil, youtube
  from lib.paths import TRANSCRIPT_DIR

Logic:
  1. Call net.apply_no_proxy_env() at the very start
  2. Build URL: youtube.build_url(PLAYLIST_ID, CHANNEL, SEARCH, LIMIT) → (label, url)
  3. List videos: youtube.list_videos(url, LIMIT) → [(vid_id, title), ...]
  4. For each video: call youtube.download_transcript(vid_id, title, languages, TRANSCRIPT_DIR)
     where languages comes from textutil.load_languages() — do not hardcode ["en","fr","ro"]
  5. Print a summary: N videos processed

Use TRANSCRIPT_DIR from lib.paths as the output folder.
Output only the file content.
```

**Expected output:** Mirrors the structure of `read_channel.py` but uses `TRANSCRIPT_DIR` and calls
`download_transcript` instead of `download_audio`. Languages come from `textutil.load_languages()`
so the user can configure them in `code/languages.json` without touching Python.

**Verify:** Check for `from lib.paths import TRANSCRIPT_DIR`. Check that languages are loaded via
`textutil.load_languages()`, not hardcoded. Check that `net.apply_no_proxy_env()` is first.

---

### 05.4 — Generate runner pairs

**Prompt:**
```
Write the runner shortcut files for both scripts. Each script needs a .bat (Windows) and
a .sh (Linux/macOS/devcontainer):

  scripts/r.bat + scripts/r.sh  — for read_channel.py
  scripts/t.bat + scripts/t.sh  — for read_transcript.py

Pattern for .bat:
  call conda activate learn-better
  python code\<script>.py

Pattern for .sh:
  #!/usr/bin/env bash
  conda activate learn-better
  python code/<script>.py

Output each file separately with its filename as a header.
```

**Expected output:** Four files, two lines each (three for .sh with the shebang). The `.bat` files
use `call conda activate` (not just `conda activate`) — `call` is required in `.bat` files or the
script exits immediately after conda returns.

**Verify:** Open `scripts/r.bat` in a text editor and confirm it has `call conda activate` (not
just `conda activate`). The missing `call` is a common `.bat` mistake that causes the script to
silently not run.

---

### 05.5 — Create `config/config_transcribe.json`

This is the first config file. It mirrors the top-of-file config for `read_transcript.py` and is
used in Lesson 06 by `transcribe_audio.py`.

**Prompt:**
```
Create config/config_transcribe.json — a JSON config file for my transcript-related scripts.
It should have keys matching the config variables in read_transcript.py:

  playlist_id:  ""         (playlist ID or empty string)
  channel:      "@handle"  (channel handle)
  search:       ""         (search query)
  limit:        10         (max videos)

Add a comment block at the top explaining what each key does. But remember: JSON doesn't support
comments. Instead, add a README-style text at the bottom of this response (not inside the JSON)
explaining the key meanings. Output only valid JSON for the file itself.
```

**Expected output:** A valid JSON file with four keys. JSON doesn't allow comments, so the file
itself must be pure JSON. The assistant should include a brief note (outside the JSON) explaining
the keys.

**Verify:** Validate the JSON:
```cmd
python -c "import json; json.load(open('config/config_transcribe.json')); print('valid JSON')"
```

---

### 05.6 — First test run (transcript download)

Test `read_transcript.py` with a real channel.

1. Edit `code/read_transcript.py` — set `CHANNEL = "@SomeChannel"` and `LIMIT = 3`
2. Run:
```cmd
conda activate learn-better
python code\read_transcript.py
```

**Expected outcome:** One of three things:
- **Success:** Files appear in `data/transcripts/` as `<title>.<lang>.txt`
- **ImportError on lib.textutil or lib.youtube:** Those stubs don't exist yet — proceed to step
  05.7 to handle the missing stubs
- **Other error:** See "When the AI misbehaves" section

**Verify (if success):**
```cmd
dir data\transcripts
```
You should see `.en.txt` (or `.fr.txt` etc.) files, one per video processed.

---

### 05.7 — Extend the stubs if needed

If `lib/textutil.py` or `lib/youtube.py` don't exist yet (they are written fully in Lesson 09),
ask the assistant to create minimal stubs now.

**Prompt:**
```
My script imports from lib.textutil and lib.youtube, but those files don't exist yet.
I need minimal stubs so the script can run. The functions actually called are:

From lib.textutil:
  load_languages() — returns ["en", "fr", "ro"]
  safe_filename(text) — strips Windows-illegal characters from a string, returns cleaned string
  clean_text(text) — strips VTT/HTML tags and decodes HTML entities, returns plain text

From lib.youtube:
  build_url(playlist_id, channel, search, limit) — returns (label, url) tuple
  list_videos(url, limit) — returns list of (vid_id, title) tuples
  download_transcript(vid_id, title, languages, output_dir) — downloads transcript, returns path or None
  download_audio(vid_id, output_dir, audio_format, audio_quality) — downloads audio, returns path

Write stubs: each function should just raise NotImplementedError with a message saying
"stub — implement in Lesson 09". Except load_languages() — that one should actually
return ["en", "fr", "ro"] so the script can at least partially run.
Output lib/textutil.py and lib/youtube.py separately.
```

**Expected output:** Two stub files. Each real function raises `NotImplementedError` with a clear
message. `load_languages()` returns the three-language list. This is enough for the scripts to
import cleanly and for the parts that don't hit the not-implemented functions to run.

**Verify:**
```cmd
python -c "from lib import textutil, youtube; print('stubs OK')"
```

---

### 05.8 — Commit

**Prompt:**
```
Give me git commands to add and commit the following new files:
  code/read_channel.py
  code/read_transcript.py
  scripts/r.bat  scripts/r.sh
  scripts/t.bat  scripts/t.sh
  config/config_transcribe.json
  lib/textutil.py  (stub)
  lib/youtube.py   (stub)

Commit message: "add read_channel, read_transcript, runner scripts, config stub"
OS: Windows, Command Prompt.
```

**Verify:** `git log --oneline` should show four commits.

---

## When the AI misbehaves

**The assistant hardcodes `["en", "fr", "ro"]` directly in `read_transcript.py` instead of
calling `textutil.load_languages()`.**
Push back: "The language list should come from `textutil.load_languages()`, not be hardcoded.
Later the user will configure it in `code/languages.json`. Can you change the call?"

**The `.bat` file is missing `call` before `conda activate`.**
In `.bat` files, `conda activate` is itself a script. Without `call`, the parent script exits
after conda finishes, and `python code\read_channel.py` never runs. The fix is always
`call conda activate learn-better`. Ask: "The .bat file stops after conda activate and never
runs the python script. I think `call` is missing before `conda activate`. Can you check?"

**`download_transcript` silently writes nothing because the channel has no auto-generated captions.**
Not all channels have caption tracks. Ask: "The script runs but no transcript files appear.
What are the reasons a video might not have downloadable captions? What flag does yt-dlp use to
list available subtitle tracks for a video?" (Answer: `yt-dlp --list-subs <url>`.)

**The assistant writes `read_channel.py` to output to `data/audio` (hardcoded) instead of using
`AUDIO_DIR`.**
Same fix as in Lesson 04: "Please use `AUDIO_DIR` from `lib.paths` as the output path — don't
hardcode `data/audio`."

---

## What you have now

Files added this lesson:

```
learn-better/
    code/
        read_channel.py     (new)
        read_transcript.py  (new)
    scripts/
        r.bat / r.sh        (new)
        t.bat / t.sh        (new)
    config/
        config_transcribe.json   (new)
    lib/
        textutil.py   (stub — full version in Lesson 09)
        youtube.py    (stub — full version in Lesson 09)
    data/
        transcripts/  (generated — git-ignored)
```

Repo state: audio and caption download scripts exist and can run (with stubs), runners in place,
first config file created. Four commits on `main`.

---

## Next →

[Lesson 06 — Whisper Transcription](06_whisper_transcription.md)

# Lesson 04 — First Working Script

**You'll build:** `code/list_playlists.py` — a script that lists a channel's public playlists and
saves them to `data/playlists.json`, plus the runner pair `scripts/p.bat` / `scripts/p.sh` so you
can launch it with a single letter. You'll also run through the full "iterate and fix" debugging
cycle for the first time.
**Complexity:** ⭐⭐⭐☆☆   **Est. time:** ~60–90 min
**AI tasks in this lesson:** multi-file creation, config design, debugging from an error message

---

## Prerequisites

- Lesson 03 completed: conda env `learn-better` active with all packages, `lib/paths.py` and
  `requirements.txt` committed
- `lib/__init__.py` exists (created in Lesson 02)
- Internet access (the script queries YouTube)

---

## Re-orient the AI

> Paste this block at the start of a new session, or any time the assistant loses context:
>
> "I'm working on the **learn-better** repo — a Python tool that downloads YouTube audio and
> transcripts, transcribes locally with faster-whisper, and generates summaries and word clouds.
> We're on **Lesson 04 — First Working Script**. The environment is set up (`learn-better` conda
> env, Python 3.12, ffmpeg, all packages installed). The last files we created were
> `requirements.txt` and `lib/paths.py`. We have NOT yet written any scripts in `code/` or
> `scripts/`. OS: Windows. Conda env: `learn-better`. Please continue from where I left off."

---

## Concepts

1. **Config at the top of the file.** All tunable parameters (which channel, how many results,
   whether to count) live in a clearly-marked config block at the top of the script — not buried
   in function bodies. This makes it easy to scan and change without reading the implementation.

2. **Feed the actual error message back.** When a script fails, copy-paste the full traceback into
   the assistant's chat window. Never paraphrase. The exact error text (exception type, file name,
   line number) is what the assistant uses to diagnose the problem. A paraphrase removes that signal.

3. **Ask for diagnosis before asking for a patch.** After pasting an error, ask "what does this
   error mean?" before "how do I fix it?" You learn more, and you can catch cases where the
   assistant's proposed fix is addressing a symptom rather than the root cause.

---

## Step-by-step

### 04.1 — Ask the assistant to explain the script's purpose and design

Before writing any code, make sure the design is clear. This is the spec step.

**Prompt:**
```
I want to write a Python script called code/list_playlists.py. Its job:
- Accept a YouTube channel handle (like @handle) or channel URL as a config variable
- List all public playlists for that channel, using yt-dlp
- Optionally list the videos inside each playlist, up to a VIDEO_LIMIT per playlist
- Count the total number of videos in each playlist (optional, controlled by a flag)
- Save the result as JSON to data/playlists.json

The project already has:
- lib/paths.py with DATA_DIR = "data" (and other constants)
- lib/net.py with network helpers (proxy, cookies) — it's not written yet, we'll stub it for now
- lib/youtube.py with YouTube helpers — also not written yet, stub it

Tell me: what config variables will this script need at the top, and what should the JSON
output structure look like? Think step by step. Do not write code yet.
```

**Expected output:** The assistant should propose config variables along these lines:
- `CHANNEL` — channel handle or URL (string)
- `LIST_VIDEOS_FOR` — which playlists to expand (None = all, or a list of playlist IDs)
- `VIDEO_LIMIT` — max videos to list per playlist (integer)
- `COUNT_VIDEOS` — whether to include video counts (boolean)

And an output JSON structure something like:
```json
[
  {
    "id": "PLxxxxx",
    "title": "Playlist title",
    "url": "https://www.youtube.com/playlist?list=PLxxxxx",
    "video_count": 42,
    "videos": [{"id": "...", "title": "..."}, ...]
  }
]
```

**Verify:** Check that the proposed config block has at least `CHANNEL`, `VIDEO_LIMIT`, and
`COUNT_VIDEOS`. If `LIST_VIDEOS_FOR` is missing, ask the assistant to add it — it controls which
playlists get their video list expanded.

---

### 04.2 — Generate the script

Now ask for the full script. This is a multi-file creation step (the script + two runner files).

**Prompt:**
```
Now write code/list_playlists.py with these exact requirements:

Config block at the top (all-caps, clearly commented):
  CHANNEL = "@handle"          # channel handle or URL
  LIST_VIDEOS_FOR = None       # None = list videos for all playlists; or list of playlist IDs
  VIDEO_LIMIT = 5              # max videos to list per playlist
  COUNT_VIDEOS = True          # include video counts in output

Imports:
  import os, json
  from lib import net, youtube
  from lib.paths import DATA_DIR

Logic:
  1. Call net.apply_no_proxy_env() at the very start (corporate proxy fix)
  2. Build the output path: OUTPUT_JSON = os.path.join(DATA_DIR, "playlists.json")
  3. Fetch all playlists for CHANNEL using youtube.list_playlists(CHANNEL)
  4. For each playlist: if LIST_VIDEOS_FOR is None or playlist id is in LIST_VIDEOS_FOR,
     fetch videos up to VIDEO_LIMIT using youtube.fetch_playlist_videos(playlist_id)
  5. If COUNT_VIDEOS is True, include a video_count field
  6. Write the result to OUTPUT_JSON with json.dump, indented
  7. Print a summary line: how many playlists found, path written

Also write:
  scripts/p.bat — activates conda env and runs the script
  scripts/p.sh  — bash equivalent (for Linux/macOS/devcontainer)

Output each file separately with its filename as a header. Output only the file contents.
```

**Expected output:** Three files. `code/list_playlists.py` should have the config block at the
top, the imports exactly as specified, `net.apply_no_proxy_env()` called before any network work,
and a final `json.dump` write to `data/playlists.json`. `scripts/p.bat` should be two lines:
```bat
call conda activate learn-better
python code\list_playlists.py
```
`scripts/p.sh` should be:
```bash
#!/usr/bin/env bash
conda activate learn-better
python code/list_playlists.py
```

**Verify:** Check that `from lib import net, youtube` is present (not `import lib.net` separately).
Check that `net.apply_no_proxy_env()` appears before any yt-dlp or network call. Check that the
output path uses `os.path.join(DATA_DIR, "playlists.json")` rather than a hardcoded string.

---

### 04.3 — Save the files and do a first run

Save the three files into the repo, then run the script to see what happens.

**Steps:**
1. Save `code/list_playlists.py`, `scripts/p.bat`, `scripts/p.sh` to those paths
2. Edit the `CHANNEL` variable in `list_playlists.py` to a real YouTube channel handle you want
   to test with (e.g. `"@SomeChannel"`)
3. Open Command Prompt, activate the env, and run:

```cmd
conda activate learn-better
python code\list_playlists.py
```

**Expected outcome:** One of three things will happen:

**A — It works:** You see a summary line and `data/playlists.json` appears. Open it and confirm it
has the right structure. Proceed to step 04.5.

**B — ImportError on `lib.net` or `lib.youtube`:** The helper modules don't exist yet (they come
in Lesson 09). Proceed to step 04.4.

**C — Some other error:** See "When the AI misbehaves" at the bottom of this lesson, then proceed
to step 04.4.

---

### 04.4 — Iterate and fix: the debugging cycle

This is the core skill of the lesson. When the script fails, follow this three-part cycle:

**Step 1 — Copy the full traceback. Paste it without editing it.**

Open the assistant and paste:
```
I ran code/list_playlists.py and got this error:

[paste the full traceback here — every line, from "Traceback (most recent call last):" to the end]

What does this error mean? What is the most likely cause?
```

Do NOT paraphrase. "It says something about an import error" is less useful than the actual output.

**Expected output:** The assistant should identify the error type and explain it in plain terms.
For an `ImportError: cannot import name 'apply_no_proxy_env' from 'lib.net'`, it should explain
that the function is referenced before it is defined — `lib/net.py` either doesn't exist yet or
doesn't have that function.

**Step 2 — Confirm the diagnosis, then ask for the fix.**

After the assistant explains the error, reply:
```
That makes sense. How should I fix this?
```

**Expected output:** A concrete fix. For a missing `lib/net.py`, the assistant will likely offer
to stub it — a minimal version that has `apply_no_proxy_env()` as a no-op, so the script can run
without the full networking layer.

**Step 3 — Apply the fix and re-run. Repeat until the script runs.**

Apply the fix exactly as given, re-run `python code\list_playlists.py`, and copy-paste any new
error back into the assistant. Each iteration should clear at least one error. After 2–3 cycles,
the script should run.

**Verify:** The script exits cleanly and `data/playlists.json` exists with at least one playlist
entry in it.

---

### 04.5 — Read the output and confirm the structure

```cmd
type data\playlists.json
```

(Or open it in VS Code for a formatted view.)

**Expected structure:**
```json
[
  {
    "id": "PLxxxxx",
    "title": "Some Playlist Title",
    "video_count": 12,
    "videos": [
      {"id": "abc123", "title": "Video One"},
      ...
    ]
  },
  ...
]
```

**Verify:** Confirm the file is valid JSON (VS Code will highlight syntax errors). Confirm there is
at least one playlist. If `video_count` is missing, check that `COUNT_VIDEOS = True` is set in the
config. If `videos` is an empty list, check `VIDEO_LIMIT` — it may be 0.

---

### 04.6 — Commit the new files

**Prompt:**
```
Give me the git commands to add and commit code/list_playlists.py, scripts/p.bat,
scripts/p.sh, and any new lib/ stubs I created, with a clear commit message.
OS: Windows, Command Prompt.
```

**Expected output:**
```cmd
git add code\list_playlists.py scripts\p.bat scripts\p.sh lib\net.py
git commit -m "add list_playlists.py with p.bat/p.sh runners"
git push
```

**Verify:** `git log --oneline` should show three commits: initial scaffold, environment files,
and the new scripts commit.

---

## When the AI misbehaves

**The assistant hardcodes the output path as `"data/playlists.json"` instead of using `DATA_DIR`.**
Push back: "The project uses `lib/paths.py` as the single source of truth for output paths.
Can you change the output path to use `os.path.join(DATA_DIR, 'playlists.json')` and import
`DATA_DIR` from `lib.paths`?" This is a habit to enforce now — it pays off in Lesson 07.

**The script runs but `data/playlists.json` contains an empty list `[]`.**
Two common causes: (1) the channel handle is wrong — try opening `https://www.youtube.com/@handle`
in a browser to confirm it exists; (2) the channel has no public playlists (private playlists
aren't visible without authentication). Ask the assistant: "The channel exists but the output is
empty. What are the reasons `youtube.list_playlists()` might return nothing for a valid channel?"

**You get a `403` or `429` HTTP error.**
YouTube occasionally rate-limits unauthenticated requests. Ask the assistant: "I'm getting a 403
error when fetching playlists. What are my options for authenticating yt-dlp, and does this
project's lib/net.py handle cookies?" (It does — `lib/net.py` has a `COOKIES_FROM_BROWSER`
option. That module is written in Lesson 09; for now, wait a few minutes and try again.)

**The assistant produces `p.bat` that uses `python3` instead of `python`.**
On Windows with conda, the correct command is `python` (not `python3`). Push back: "On Windows
with conda, the command is `python`, not `python3`. Can you update the .bat file?"

**`p.bat` fails with `'conda' is not recognized as an internal or external command`.**
conda is not on PATH in a plain Command Prompt. Either run from the Anaconda Prompt shortcut, or
add conda to PATH during installation. Ask the assistant: "conda is not recognized in my Command
Prompt. What's the quickest fix on Windows without adding it to the system PATH?" The usual answer
is to use the Anaconda Prompt shortcut that ships with Miniconda.

---

## What you have now

Files added this lesson:

```
learn-better/
    code/
        list_playlists.py   (new)
    scripts/
        p.bat               (new)
        p.sh                (new)
    lib/
        net.py              (stub — full version in Lesson 09)
    data/
        playlists.json      (generated — git-ignored)
```

Repo state: first real script running, output to `data/`, two runner shortcuts in `scripts/`,
three commits on `main`.

---

## Next →

[Lesson 05 — Audio and Transcripts](05_audio_and_transcripts.md)

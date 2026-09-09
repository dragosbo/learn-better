# Lesson 02 — Your first working tool (early win)

**You'll build:** a small, no-API-key script that lists a YouTube source and
downloads a clip's **audio + transcript** to a `data/` folder — a real file you
can see on disk by the end. Plus the single most important AI-pairing skill:
**feeding an error back and iterating.**
**Complexity:** ⭐⭐   **Est. time:** ~45–75 min

> **Assistant-agnostic.** Any AI assistant works. From here on, an IDE-integrated
> assistant (one that can create files in your folder) is convenient — noted as an
> aside where it matters.

---

## Prerequisites (from Lesson 01)

- An empty `learn-better/` repo (`git init` done) with a minimal `.gitignore`.
- Python 3.12 and ffmpeg both verified on PATH (`python --version` → 3.12.x,
  `ffmpeg -version` → a banner).

---

## Re-orient the AI (paste after a crash/restart)

```
Context: Lesson 02 of building a YouTube→study-material toolkit with your help.
OS: <your OS>. Repo: learn-better/ (git initialized, minimal .gitignore).
Env: Python 3.12 + ffmpeg verified on PATH.
Goal now: one no-API-key script (code/read_channel.py) that lists a YouTube
source and downloads a clip's audio + transcript into data/, skipping files that
already exist. Uses yt-dlp. No API key.
Last thing done: <e.g. "installed yt-dlp", or "script written, hit an error">.
Please continue from there.
```

---

## Concepts (what this lesson teaches about working with AI)

1. **Get to a working result fast.** A tool that produces a real file early keeps
   the project concrete and motivating. Don't perfect the structure yet.
2. **Prompt discipline that prevents 80% of misfires:** always tell the assistant
   your **OS**, your **environment**, and the **exact file** to write; ask it to
   **list the files it will create before creating them**.
3. **Iterate and fix (the core skill).** Real tools fail on the first run. The
   difference between fast and slow progress is *how you feed the failure back* —
   the actual error text, and a request for a **diagnosis**, not just a patch.

---

## Step-by-step

### 02.1 — Install the one dependency you need now

**Ask your assistant** for the single package that downloads YouTube audio +
subtitles without an API key, and how to install it into your env.

> **Prompt:**
> "For `<your OS>`, what one pip package lets me download YouTube audio AND
> subtitles without any API key, and reliably gets past YouTube's bot check? Give
> me the exact `pip install` command. One line."

**Expected response:** `yt-dlp`, and — importantly — the **`curl_cffi`** extra for
bot-check bypass, i.e. something like:

```
pip install "yt-dlp[default,curl-cffi]"
```

**Verify:** `python -c "import yt_dlp; print(yt_dlp.version.__version__)"` prints a
version. If it errors, you're likely in the wrong environment (see *When the AI
misbehaves*).

> *Why `curl_cffi`?* Ask the assistant if you're curious — short version: it lets
> yt-dlp impersonate a real browser's TLS fingerprint, so YouTube returns real
> subtitle/format data instead of an empty "are you a bot?" response.

### 02.2 — Ask for the plan before the code

Good habit: make the assistant **enumerate the files and behavior first**, so you
can course-correct before anything is written.

> **Prompt:**
> "Before writing anything, list the file(s) you'll create and the behavior, as a
> short plan. I want ONE script `code/read_channel.py` that: (1) reads a YouTube
> source set at the top of the file — a playlist id, a channel handle, OR a search
> term (set one, leave the others empty) plus a `LIMIT`; (2) for each clip up to
> LIMIT, saves the transcript to `data/transcripts/` and downloads the audio (mp3
> via ffmpeg) to `data/audio/`; (3) SKIPS anything already on disk; (4) if a clip
> has no transcript, prints a loud line and keeps going. No API key. I'm on
> `<your OS>`, env has Python 3.12 + ffmpeg + yt-dlp. Confirm the plan; don't code yet."

**Expected response:** a short plan naming `code/read_channel.py`, the config
block at the top (`PLAYLIST_ID` / `CHANNEL` / `SEARCH` / `LIMIT`), the two output
folders, skip-if-exists, and the "no transcript" flag. If the plan misses one of
your four points, say so before it writes code.

**Verify:** the plan matches your four requirements. Only then say "looks good,
write it."

### 02.3 — Have it write the script

> **Prompt:**
> "Looks good. Create `code/read_channel.py` exactly as planned. Put the source
> config (`PLAYLIST_ID`, `CHANNEL`, `SEARCH`, `LIMIT`) at the very top with
> comments. Use yt-dlp for both subtitles and audio. Default `LIMIT = 1` so my
> first run is fast."

**Expected response / aside:** an IDE assistant creates the file directly; a chat
assistant returns the code to save as `code/read_channel.py`. Skim it — you should
see the config block at the top and calls into `yt-dlp`.

**Verify:** `python code/read_channel.py --help` or just opening the file confirms
it exists and the config block is at the top. Don't run the download yet.

### 02.4 — Point it at a video and run it

Set the source. A **search** is the easiest first test.

> **Prompt:**
> "Set `SEARCH` to `git tutorial for beginners`, leave `PLAYLIST_ID` and `CHANNEL`
> empty, and `LIMIT = 1`. Then give me the exact command to run it on `<your OS>`."

**Expected response:** edits the config and gives you `python code/read_channel.py`.

**Run it.** Expect it to: list 1 video, save a transcript to `data/transcripts/`,
and download audio to `data/audio/`. On a second run it should say the files
already exist and skip them.

**Verify:** you have a real file — e.g. `dir data\audio` (Windows) or
`ls -R data` (macOS/Linux) shows an `.mp3` and a `.txt`. **That's your early win.**

### 02.5 — When your first run doesn't work (the iterate-and-fix skill)

Your first run may **not** succeed — and that's the point of this section. The two
most common first-run failures on a fresh machine:

- **`Sign in to confirm you're not a bot`** — YouTube blocking an anonymous
  download from your IP.
- **Empty/short output, or a `curl_cffi`/import error** — a missing piece of the
  install, or the wrong environment.

Here's the skill. When something breaks:

1. **Feed back the *actual* error, not a paraphrase.** Copy the real terminal
   output. Assistants debug from exact text far better than from "it didn't work."
   > **Prompt:** "Running it gave this exact output: `<paste the full error>`.
   > What is the root cause, and what's the smallest change to fix it? Explain the
   > cause first, then the fix."
2. **Ask for a diagnosis before accepting a patch.** If the assistant jumps
   straight to "try this," ask *why* — a fix you understand won't silently break
   later.
3. **Know when to change approach, not re-patch.** If two attempts at the same
   approach both fail, say so:
   > **Prompt:** "That's the second fix on the same approach that didn't work.
   > Step back — what's the actual root cause, and is there a fundamentally
   > different approach?" (For the bot-check, the real fix is usually **cookies**:
   > export a `cookies.txt` from a logged-in browser and point the tool at it, or
   > update yt-dlp — ask the assistant to wire that in.)

**Verify:** after iterating, a re-run produces the files from 02.4. Note *which*
fix worked and *why* — you'll reuse this loop in every later lesson.

### 02.6 — Establish `data/` as the output home

**Ask your assistant to** confirm outputs live under a single `data/` folder and
that it's git-ignored (you added `data/` to `.gitignore` in Lesson 01).

> **Prompt:**
> "Confirm the script writes only under `data/` (e.g. `data/audio/`,
> `data/transcripts/`) and that `data/` is git-ignored so I never commit large
> media. If any output path is outside `data/`, fix it."

**Verify:** `git status` shows your **code** as new/changed but **not** the
downloaded media (it's under the ignored `data/`).

---

## When the AI misbehaves

- **`ModuleNotFoundError: yt_dlp` even though you installed it.** You're almost
  certainly in a different Python than the one you installed into. Check
  `python -c "import sys; print(sys.executable)"` and make sure it's your 3.12 env;
  activate the env, or paste the path back and ask the assistant to reconcile it.
  *(This exact "wrong interpreter" trap bites often — worth remembering.)*
- **Bot-check (`Sign in to confirm you're not a bot`).** Not a code bug — YouTube
  is throttling anonymous access. Iterate per 02.5: cookies file or a yt-dlp update.
- **It edits the wrong file or invents a path.** Re-state the exact target
  (`code/read_channel.py`) and the exact output folders; specificity fixes it.
- **Terminal output looks empty or garbled** (especially on Windows `cmd`). Don't
  trust the console alone — check whether the **file** actually appeared in
  `data/`. The artifact is the source of truth.
- **A long download stalls.** Give it time; if truly stuck, interrupt, re-run
  (skip-if-exists means you won't re-download what already landed), and if it
  recurs paste the output back for diagnosis.

---

## What you have now

```
learn-better/
├── .gitignore
├── code/
│   └── read_channel.py     # lists a source; saves audio + transcript
└── data/                   # git-ignored
    ├── audio/              # <clip>.mp3
    └── transcripts/        # <clip>.<lang>.txt
```
A working, no-API-key tool that put a real audio file and transcript on disk — and
the iterate-and-fix loop you'll lean on for the rest of the course.

---

## Next → Lesson 03 — Getting the environment right (properly)

You got here with a *lightweight* setup. Next you'll make it **reproducible**:
conda vs venv vs uv (and when each), why ffmpeg can't be pip-installed, a pinned
`requirements.txt`, and a `lib/paths.py` that becomes the single source of truth
for every output path — then repoint this tool through it.

# Lesson 03 — Getting the environment right (properly)

**You'll build:** a pinned `requirements.txt`, a `lib/paths.py` that becomes the
single source of truth for every output path, and a reproducible environment you
understand — then repoint Lesson 02's tool through it.
**Complexity:** ⭐⭐   **Est. time:** ~45–60 min

> **Assistant-agnostic.** Any AI assistant works.

---

## Prerequisites (from Lesson 02)

- `code/read_channel.py` runs and produced a real `.mp3` + transcript under `data/`.
- Python 3.12 + ffmpeg + yt-dlp installed (even if only "lightly" so far).

---

## Re-orient the AI (paste after a crash/restart)

```
Context: Lesson 03 of building a YouTube→study-material toolkit with your help.
OS: <your OS>. Repo: learn-better/ with a working code/read_channel.py that
downloads audio + transcript into data/.
Goal now: make the environment reproducible — pick conda/venv/uv deliberately,
pin a requirements.txt, explain why ffmpeg isn't pip-installable, and add
lib/paths.py as the single source of truth for output paths, then repoint the
existing tool through it.
Last thing done: <e.g. "wrote requirements.txt">. Please continue from there.
```

---

## Concepts (what this lesson teaches about working with AI)

1. **Ask for the trade-offs, then decide.** Don't let the assistant silently pick
   your tooling. Ask it to *compare* options with pros/cons, then you choose.
2. **A single source of truth beats scattered constants.** Centralizing paths in
   one module means later changes touch one file, not ten — and the assistant can
   "follow the constant" instead of guessing paths.
3. **Pin what you depend on.** Reproducibility is a prompt away — ask for pinned
   versions and a note on the *system* dependency that pip can't handle.

---

## Step-by-step

### 03.1 — Choose an environment strategy (deliberately)

**Ask your assistant to** compare the options for your OS and recommend one, with
reasons — so the choice is yours, not a default.

> **Prompt:**
> "Compare conda vs pip+venv vs uv for a Python 3.12 project that also needs the
> **ffmpeg** system binary, on `<your OS>`. Give a short pros/cons for each and a
> one-line recommendation for someone who wants the fewest surprises. Note
> explicitly which option can install ffmpeg for me and which can't."

**Expected response:** a compact comparison. Key point it must surface: **conda
can install ffmpeg into the env; pip and uv cannot** (ffmpeg is a system binary).
A common recommendation is conda for day-to-day (ffmpeg handled), uv for speed.

**Verify:** you can state which tool you're using and why, and whether you still
need a separate ffmpeg install.

### 03.2 — Create the environment and confirm the interpreter

**Ask your assistant** for the exact create/activate commands for your chosen tool,
plus the interpreter-check that prevents the #1 install failure.

> **Prompt:**
> "Give me the exact commands for `<your OS>` to create and activate a Python 3.12
> environment named `learn-better` using `<conda|venv|uv>`, then a command to
> confirm the active interpreter is really 3.12 before I install anything."

**Expected response:** create + activate commands, then a verify like
`python --version` (must print 3.12.x) and optionally
`python -c "import sys; print(sys.executable)"` to confirm *which* python.

**Verify:** `python --version` → 3.12.x **inside the activated env**. This check is
the fix for the "wrong interpreter" trap you may have hit in Lesson 02.

### 03.3 — Understand why ffmpeg is special

**Ask your assistant to** explain, briefly, why ffmpeg isn't in `requirements.txt`.

> **Prompt:**
> "In 3 sentences: why can't ffmpeg go in `requirements.txt`, and how should I
> install/verify it on `<your OS>`? I want to understand the 'system binary vs pip
> package' distinction."

**Expected response:** ffmpeg is a compiled system program, not a Python package,
so pip/uv can't install it; use the OS package manager (or conda), and verify with
`ffmpeg -version`. This is *the* #1 setup trap — worth internalizing.

**Verify:** `ffmpeg -version` prints a banner.

### 03.4 — Pin a `requirements.txt`

**Ask your assistant to** create a pinned `requirements.txt` for the active stack,
with ffmpeg documented as a system dependency in a comment (not a pip line).

> **Prompt:**
> "Create `requirements.txt` for this project: `yt-dlp[default,curl-cffi]`,
> `youtube-transcript-api`, `pandas`, and `ipykernel`. Pin each to a sensible
> range. Add a comment block at the top documenting that **ffmpeg is a required
> SYSTEM dependency** (not pip-installable) with the install command for `<your
> OS>`. Don't include anything we're not using yet."

**Expected response:** a short `requirements.txt` with pinned ranges and an ffmpeg
comment block. (Whisper/Piper come in later lessons — the plan adds new deps
*per phase*, only once a tool actually needs them, so don't front-load them.)

**Verify:** `pip install -r requirements.txt` succeeds, then the import smoke test:
`python -c "import yt_dlp, pandas; print('OK')"`.

### 03.5 — Create `lib/paths.py` as the single source of truth

**Ask your assistant to** create a small module that defines every output path
once, and to make it the place all tools import from.

> **Prompt:**
> "Create `lib/paths.py` defining the project's output folders as constants, all
> under a single `data/` root: `DATA_DIR`, `AUDIO_DIR` (`data/audio`),
> `TRANSCRIPT_DIR` (`data/transcripts`), and leave room to add more later
> (generated transcripts, summaries, tts_output, wordclouds, audio_reencoded).
> Also add an `__init__.py` so `from lib import paths` works. Keep it plain — just
> path constants, no logic."

**Expected response:** `lib/paths.py` with the constants + `lib/__init__.py`. The
key idea: *one file* owns the paths, so a future move (e.g. reorganizing `data/`)
is a one-line change here.

**Verify:** `python -c "from lib import paths; print(paths.AUDIO_DIR)"` prints
`data\audio` (or `data/audio`).

### 03.6 — Repoint Lesson 02's tool through `lib/paths.py`

**Ask your assistant to** update `read_channel.py` so its output paths come from
`paths.*` instead of hard-coded strings — and to change **nothing else**.

> **Prompt:**
> "Update `code/read_channel.py` to import `from lib import paths` and use
> `paths.AUDIO_DIR` / `paths.TRANSCRIPT_DIR` for its outputs, replacing any
> hard-coded `data/audio` / `data/transcripts` strings. Change ONLY the paths —
> keep all other behavior identical. Show me what changed."

**Expected response:** a small diff that swaps the path strings for the constants.
Insist on "change only the paths" — this is your first taste of a **behavior-
preserving refactor**, a skill Lesson 06 leans on hard ("verify sameness").

**Verify:** re-run `python code/read_channel.py`. It should behave exactly as in
Lesson 02 — same files, and **skip-if-exists** recognizes the ones already there.
If it re-downloads or writes to a new place, the repoint was wrong; feed the
behavior back and ask for a fix.

---

## When the AI misbehaves

- **It picks a tool without asking.** Make it compare and justify; the decision is
  yours. If it assumes conda but you want venv, say so.
- **`pip install` pulls broken/ancient versions.** Almost always the wrong Python
  (an old system 3.x). Confirm `python --version` is 3.12 *in the active env*
  first — re-check 03.2 before touching the pins.
- **It adds deps you don't need yet** (whisper, piper, …). Trim it: "only what the
  current tools import." New deps get added per lesson, when first used.
- **The repoint changes behavior** (re-downloads, new folders). That's a failed
  behavior-preserving edit — paste what happened and ask it to restore exact
  sameness, changing only the path source.
- **Wrong-interpreter imports.** `python -c "import sys; print(sys.executable)"`
  tells you which python is active; if it's not your env, activate it.

---

## What you have now

```
learn-better/
├── requirements.txt        # pinned; ffmpeg documented as a system dep
├── code/
│   └── read_channel.py     # now imports paths from lib/
├── lib/
│   ├── __init__.py
│   └── paths.py            # single source of truth for output paths
└── data/                   # git-ignored (audio/, transcripts/)
```
A reproducible environment you understand, and a paths module that every future
tool will import from.

---

## Next → Lesson 04 — Playlists + transcripts, config-driven

You'll add a playlist lister and a transcript-only tool, introduce the `config/`
folder + JSON configs (so runs are driven by data, not code edits), and add the
first one-letter runners.

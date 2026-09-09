# Lesson 03 — Environment Setup

**You'll build:** A working Python 3.12 conda environment with all project dependencies
installed, plus `lib/paths.py` — the file that tells every script where its outputs go.
**Complexity:** ⭐⭐☆☆☆   **Est. time:** ~45–60 min
**AI tasks in this lesson:** recommendation + reasoning, command generation, file creation

---

## Prerequisites

- Lesson 02 completed: repo exists with `.gitignore`, `README.md`, `plan.md`, on GitHub
- conda installed (Miniconda or Anaconda)
- Internet connection (for conda package downloads)

---

## Re-orient the AI

> Paste this block at the start of a new session, or any time the assistant loses context:
>
> "I'm working on the **learn-better** repo — a Python tool that downloads YouTube audio and
> transcripts, transcribes locally with faster-whisper, and generates summaries and word clouds.
> We're on **Lesson 03 — Environment Setup**. The repo already exists with `.gitignore`,
> `README.md`, and `plan.md`. We have NOT yet created the conda environment or any Python files.
> OS: Windows. Please continue from where I left off."

---

## Concepts

1. **ffmpeg is a system binary — not a Python package.** It must be installed at the OS level
   (conda-forge handles this cleanly). `pip install ffmpeg` installs a stub that does NOT include
   the binary itself — a very common trap that causes silent failures later in yt-dlp and Whisper.

2. **One constants file, one source of truth for paths.** `lib/paths.py` defines every output
   folder as a named constant. Every script imports from it. When you move the data folder or
   rename a subfolder, you change exactly one file and all scripts stay in sync.

3. **Commit configuration, not data.** `requirements.txt` and `lib/paths.py` are committed.
   The `data/` folder is git-ignored (with the one exception: `data/summaries/` where authored
   content lives). Never commit audio files, transcripts, or model weights.

---

## Step-by-step

### 03.1 — Ask the assistant to recommend an environment strategy

**Prompt:**
```
I'm setting up a Python project on Windows. The project uses yt-dlp, faster-whisper,
and Piper TTS. I need to decide between conda + pip, plain pip + venv, and uv.
What are the trade-offs for this specific toolset? Pay special attention to ffmpeg,
which some of these tools require as a system binary.
```

**Expected output:** The assistant should explain that conda is preferred here because it can
install ffmpeg as a real binary alongside the Python packages (no separate installer needed on
Windows). Plain pip/venv cannot install ffmpeg and requires a separate system install. uv is
very fast but also cannot install ffmpeg directly. For this project, `conda + pip` is the
cleanest path on Windows.

**Verify:** The answer should explicitly mention that `pip install ffmpeg` installs a Python
wrapper stub, NOT the real ffmpeg binary, and that this causes yt-dlp mp3 conversion to silently
fail.

---

### 03.2 — Create the conda environment

**Prompt:**
```
Give me the exact conda commands to:
1. Create a new environment named learn-better with Python 3.12
2. Activate it
3. Install ffmpeg from conda-forge (not pip)
4. Verify that ffmpeg is correctly installed after

OS: Windows, Command Prompt.
```

**Expected output:**
```cmd
conda create -n learn-better python=3.12 -y
conda activate learn-better
conda install -c conda-forge ffmpeg -y
ffmpeg -version
```

**Verify:** Run `ffmpeg -version`. You should see a version string like
`ffmpeg version 7.x.x built with gcc ...`. If the command is not found, ffmpeg was not
installed — check that you're in the `learn-better` env (`conda activate learn-better`).

---

### 03.3 — Ask the assistant to explain why ffmpeg cannot use pip

This is worth understanding deeply — it's the #1 environment trap in this project.

**Prompt:**
```
Why does `pip install ffmpeg` not work for a project that uses yt-dlp to download and
convert audio? What actually happens when you run that command, and what should you do
instead on Windows?
```

**Expected output:** The assistant should explain that `pip install ffmpeg` installs a Python
package named `ffmpeg` that contains only Python bindings or a stub — it does NOT install the
actual C binary that yt-dlp calls via subprocess. yt-dlp invokes `ffmpeg` as an external
command (`subprocess.run(["ffmpeg", ...])`); if the binary isn't on PATH, yt-dlp silently falls
back to a container format (webm/m4a) instead of converting to mp3, with no clear error message.
The fix: install via `conda install -c conda-forge ffmpeg` or from ffmpeg.org/download.

**Verify:** No command. The key test is later when `r.bat` downloads audio — if the output is
`.mp3` (not `.m4a` or `.webm`), ffmpeg is working.

---

### 03.4 — Create `requirements.txt`

**Prompt:**
```
Create a requirements.txt for a Python 3.12 project with these dependencies. Use
minimum-version pins (>=), not exact pins, so updates aren't blocked:

- youtube-transcript-api >= 0.6, < 1   (caption download fallback)
- yt-dlp[default,curl-cffi] >= 2024.4.9  (primary downloader; curl_cffi is REQUIRED for bot-detection bypass)
- curl_cffi >= 0.7                       (also listed explicitly, in case the extra name changes)
- pandas >= 2.0, < 3                     (metadata tables)
- ipykernel >= 6.29, < 7                 (for notebooks)
- faster-whisper >= 1.0                  (local speech-to-text, CTranslate2 backend)
- piper-tts >= 1.2                       (local TTS, CPU-only, MIT-licensed)

Add a comment at the top noting that ffmpeg is a SYSTEM DEPENDENCY that must be
installed separately (not via pip), and show the conda-forge, winget, and apt commands.
Do NOT include pytube or scrapetube — both are retired/broken.
Output only the file content.
```

**Expected output:** A commented `requirements.txt` with those 7 dependencies, and a prominent
comment block explaining the ffmpeg system dependency with three install options.

**Verify:** Save the output as `requirements.txt`. Then run:
```cmd
pip install -r requirements.txt
```
Watch for any error. Common issue: `faster-whisper` may download a few hundred MB of compiled
libraries on first install (CTranslate2) — this is expected. If piper-tts fails, try
`pip install piper-tts` separately and check the error message.

---

### 03.5 — Smoke-test the environment

**Prompt:**
```
Give me a short Python one-liner I can run from the command line to verify that
yt-dlp, faster-whisper, and curl_cffi all imported correctly in the learn-better
environment. OS: Windows.
```

**Expected output:** Something like:
```cmd
python -c "import yt_dlp, faster_whisper, curl_cffi; print('All imports OK')"
```

**Verify:** Run the command with the `learn-better` env active. You should see `All imports OK`.
If any import fails, install the missing package individually and check for errors.

---

### 03.6 — Create `lib/paths.py`

This is the single most important shared file in the project. Every script that writes an output
file imports its destination folder from here.

**Prompt:**
```
Create lib/paths.py for my Python project. It should define output folder constants for
all the data subfolders. Requirements:
- All outputs live under a single data/ root
- Subfolders needed: audio, audio_reencoded, transcripts, generated_transcripts,
  wordclouds, tts_output, summaries
- Use os.path.join() so the constants work on both Windows and Linux
- Add a module docstring explaining the purpose: one source of truth for output paths,
  all relative to the repo root (where scripts are run from)
- Add a comment explaining that data/summaries/ is the one exception that IS git-tracked
  (authored content)
- Name the constants: DATA_DIR, AUDIO_DIR, AUDIO_REENCODED_DIR, TRANSCRIPT_DIR,
  GENERATED_TRANSCRIPT_DIR, WORDCLOUD_DIR, TTS_OUTPUT_DIR, SUMMARY_DIR
Output only the Python file content.
```

**Expected output:** A clean `paths.py` with those 8 constants, a docstring, and the
git-tracking note. The pattern should be:
```python
DATA_DIR = "data"
AUDIO_DIR = os.path.join("data", "audio")
...
```

**Verify:** Save as `lib/paths.py`. Then:
```cmd
python -c "from lib.paths import AUDIO_DIR, SUMMARY_DIR; print(AUDIO_DIR, SUMMARY_DIR)"
```
Expected: `data\audio data\summaries`

---

### 03.7 — Commit the environment files

**Prompt:**
```
Give me the git commands to add and commit requirements.txt and lib/paths.py, with a
clear commit message. OS: Windows, Command Prompt.
```

**Expected output:**
```cmd
git add requirements.txt lib\paths.py
git commit -m "add requirements.txt and lib/paths.py"
git push
```

**Verify:** `git log --oneline` should show two commits: the initial scaffold from Lesson 02
and the new environment commit.

---

## When the AI misbehaves

**The assistant suggests `pip install ffmpeg` or `pip install ffmpeg-python`.**
Both install Python wrappers, not the real binary. Push back: "I understand these are Python
packages that wrap ffmpeg — they don't install the binary itself. yt-dlp calls `ffmpeg` as a
subprocess command and needs the real binary on PATH. Can you show me the conda-forge install
command instead?"

**pip install fails with a long error on `faster-whisper` or `CTranslate2`.**
CTranslate2 has pre-built wheels for Windows x86-64. If pip can't find a wheel, it may try to
compile from source and fail. Ask the assistant: "pip is failing to install faster-whisper. I'm
on Windows x86-64 with Python 3.12. Is there a pre-built wheel I should look for, or a different
install flag that helps?" Usually `pip install faster-whisper --prefer-binary` resolves it.

**The assistant pins versions with `==` instead of `>=`.**
Exact pins make sense for production deployments, not development projects. Ask: "Can you use
minimum-version pins (>=) instead of exact pins? This is a development project and I want to
keep it easy to update."

---

## What you have now

Files added this lesson:

```
learn-better/
    requirements.txt
    lib/
        __init__.py    (from Lesson 02)
        paths.py       (new)
```

Conda environment `learn-better` active with Python 3.12, ffmpeg, and all packages installed.

Repo state: environment files committed and pushed; no code scripts yet — those start in
Lesson 04.

---

## Next →

[Lesson 04 — First Working Script](04_first_script.md)

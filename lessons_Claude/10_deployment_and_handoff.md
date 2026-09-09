# Lesson 10 — Deployment and Handoff

**You'll build:** A `.devcontainer/` configuration for VS Code Remote Containers, a standalone
`Dockerfile.standalone`, a GitHub Actions CI workflow, the `notebooks/colab_setup.ipynb` Colab
notebook, final updates to `README.md` and `youtube.html`, and a consolidated troubleshooting
appendix. This lesson closes the project.
**Complexity:** ⭐⭐⭐⭐⭐   **Est. time:** ~90–120 min
**AI tasks in this lesson:** Dockerfile authoring, YAML generation, notebook generation, documentation
writing, deployment reasoning

---

## Prerequisites

- Lesson 09 completed: all scripts complete and tested, full pipeline runs end-to-end
- GitHub repo is up to date with all 9 previous lessons committed
- Docker Desktop installed (for devcontainer and standalone Docker test)
- VS Code with the Remote - Containers extension (optional — can verify devcontainer file without running it)

---

## Re-orient the AI

> Paste this block at the start of a new session, or any time the assistant loses context:
>
> "I'm working on the **learn-better** repo — a Python tool that downloads YouTube audio and
> transcripts, transcribes locally with faster-whisper, and generates summaries and word clouds.
> We're on **Lesson 10 — Deployment and Handoff**. All scripts are complete and working.
> This lesson adds the devcontainer, standalone Dockerfile, CI workflow, a Colab notebook, and
> final documentation. OS: Windows. Conda env: `learn-better`. Please continue from where I left off."

---

## Concepts

1. **The devcontainer is for development; the standalone Docker image is for portability.** The
   `.devcontainer/` configuration lets VS Code open the project in a container with the right
   Python version and system packages. `Dockerfile.standalone` is a self-contained image that can
   run on any host without VS Code or conda — useful for sharing the project with someone who
   doesn't want to set up the environment manually.

2. **ffmpeg in the devcontainer is an `apt` package, not conda.** The devcontainer base image is
   typically a Debian/Ubuntu image. Inside it, `conda` may not be available. Install ffmpeg via
   `apt-get install ffmpeg` in the devcontainer `Dockerfile`. This is the correct approach for
   Linux containers — not conda-forge (which is for the Windows development setup).

3. **Deploy guidance lives in README, not in a separate file.** Keeping deployment instructions
   in the README ensures they're the first thing a new user sees. A separate `how_to_deploy.md`
   is easy to overlook.

---

## Step-by-step

### 10.1 — Create `.devcontainer/devcontainer.json` and `Dockerfile`

**Prompt:**
```
Write the VS Code devcontainer configuration for my Python project. Requirements:

Files to create:
  .devcontainer/devcontainer.json
  .devcontainer/Dockerfile

Dockerfile requirements:
  - Base image: python:3.12-slim
  - Install system packages via apt-get: ffmpeg, git, curl
  - Install Python packages via pip from requirements.txt
  - Copy the project into /workspace
  - Set the working directory to /workspace

devcontainer.json requirements:
  - Name: "learn-better"
  - Build context: the .devcontainer/ folder
  - workspaceFolder: /workspace
  - Extensions to install: ms-python.python, ms-python.pylance
  - postCreateCommand: pip install -r requirements.txt
  - Set remoteUser to "root" (simplest setup for a dev container)

Note: ffmpeg must be installed via apt-get, NOT via pip (same reason as Lesson 03 — the pip
package is a stub, not the real binary).
Output each file with its filename as a header.
```

**Expected output:** Two files. The `Dockerfile` should have `RUN apt-get update && apt-get install -y ffmpeg git curl`. The `devcontainer.json` should be valid JSON with all four required fields.

**Verify:** Validate the JSON:
```cmd
python -c "import json; json.load(open('.devcontainer/devcontainer.json')); print('valid')"
```

---

### 10.2 — Create `Dockerfile.standalone`

**Prompt:**
```
Write Dockerfile.standalone — a self-contained Docker image for the learn-better project.
It should be runnable without VS Code and without conda.

Requirements:
  - Base image: python:3.12-slim
  - Install ffmpeg, git, curl via apt-get
  - Copy the full project into /app
  - Install Python dependencies: pip install -r requirements.txt
  - Set WORKDIR to /app
  - Default CMD: python code/read_channel.py (the most commonly run script)
  - Add a commented section showing alternative CMD options for each script
  - Include a LABEL with maintainer and description

Output only the Dockerfile content.
```

**Verify:** Build the image locally (optional but recommended):
```cmd
docker build -f Dockerfile.standalone -t learn-better:latest .
```
The build should complete without errors. It will take several minutes on first run (downloading
the base image and building CTranslate2/faster-whisper wheels).

---

### 10.3 — Create the GitHub Actions CI workflow

**Prompt:**
```
Write .github/workflows/ci.yml — a GitHub Actions workflow that runs basic import checks
on the project.

Requirements:
  - Trigger: push to main, pull_request to main
  - OS: ubuntu-latest
  - Python version: 3.12
  - Steps:
    1. Checkout the repo
    2. Set up Python 3.12
    3. Install system packages: sudo apt-get install -y ffmpeg
    4. Install Python dependencies: pip install -r requirements.txt
    5. Check that all scripts import cleanly:
       python -c "import code.list_playlists" etc. — but since these are scripts, not modules,
       the better test is: python -m py_compile code/list_playlists.py (repeat for all scripts)
    6. Run a quick smoke test: python -c "from lib import net, textutil, youtube; net.apply_no_proxy_env(); print('imports OK')"

Scripts to compile-check: list_playlists.py, read_channel.py, read_transcript.py,
transcribe_audio.py, make_summaries.py, make_wordcloud.py, generate_speech.py,
reencode_audio.py, compare_transcripts.py

Output only the YAML file content.
```

**Expected output:** A valid GitHub Actions YAML. The `py_compile` approach tests syntax without
executing the scripts (which would require real audio files).

**Verify:** Push to GitHub and confirm the Actions tab shows the workflow running. A green check
means the syntax and imports are clean.

---

### 10.4 — Create the Colab notebook

**Prompt:**
```
Write notebooks/colab_setup.ipynb — a Jupyter notebook for Google Colab that lets someone run
the learn-better pipeline without any local setup.

The notebook should have these cells (in order):

Cell 1 (markdown): Title and description — what the notebook does, what it requires
  (a Google account, and optionally a YouTube channel handle to test with)

Cell 2 (code): Install system dependencies in Colab:
  !apt-get install -y ffmpeg
  !pip install yt-dlp faster-whisper piper-tts youtube-transcript-api

Cell 3 (code): Clone or mount the repo:
  If running in Colab, either git clone or mount Google Drive.
  Show both options as alternatives (comment out whichever the user doesn't need).

Cell 4 (code): Configuration — channel handle, model size, limit
  CHANNEL = "@YourChannel"    # replace with a real channel
  MODEL_SIZE = "tiny"         # tiny is fastest for Colab testing
  LIMIT = 2

Cell 5 (code): Download audio for the configured channel
  (equivalent to running read_channel.py)

Cell 6 (code): Transcribe with Whisper
  (equivalent to running transcribe_audio.py)

Cell 7 (markdown): Manual step — generate summaries
  Explain that this step requires pasting into an AI assistant manually.
  Show where the paste-ready output appears (stdout of make_summaries.py).

Cell 8 (code): Run make_summaries.py and print the output

Output the notebook as a valid JSON object with the .ipynb format. Use nbformat 4.
```

**Expected output:** A valid `.ipynb` file. Each cell should have `"cell_type"`, `"source"`, and
(for code cells) `"outputs": []` and `"execution_count": null`.

**Verify:**
```cmd
python -c "import json; nb=json.load(open('notebooks/colab_setup.ipynb')); print(len(nb['cells']),'cells')"
```
You should see `8 cells` (or close to it).

---

### 10.5 — Update `README.md` with deployment guidance

**Prompt:**
```
Update README.md to add a Deployment section after the Quick Start section. The section should
cover three options:

Option A — Local (Windows, conda)
  The standard setup from Lessons 02–03. Point to the conda env setup commands.
  One-liner: conda create -n learn-better python=3.12 && conda install -c conda-forge ffmpeg

Option B — VS Code devcontainer
  Open the repo in VS Code, click "Reopen in Container". ffmpeg is installed automatically.
  When to use: Linux development, reproducible environment, or sharing with others.

Option C — Google Colab
  Open notebooks/colab_setup.ipynb in Colab. No local install required.
  When to use: one-off transcription without a local environment.

Also add a brief note at the end of the section explaining why Vercel/serverless deployment
is not appropriate: the project requires ffmpeg, faster-whisper, and Piper TTS — all of which
need system packages and several hundred MB of model files. These do not fit in a serverless
function's runtime or size limits.

Output only the new section text, not the full README (I'll add it manually).
```

**Expected output:** A clean `## Deployment` section with three options and the serverless caveat.
The ffmpeg note should repeat the core message: install at the OS level, not via pip.

**Verify:** Add the section to `README.md`. Then read the Prerequisites and Deployment sections
together to confirm they're consistent (both mention ffmpeg as a system binary, Python 3.12,
and conda).

---

### 10.6 — Write the troubleshooting appendix

**Prompt:**
```
Write docs/troubleshooting.md — a consolidated troubleshooting reference for the project.
Organised by symptom (not by lesson). Include these categories:

1. Environment and setup
   - ffmpeg not found (and why pip install ffmpeg doesn't help)
   - conda activate not recognized in Command Prompt
   - faster-whisper install fails

2. Audio download (read_channel.py)
   - yt-dlp 403 / 429 error
   - Output is .m4a or .webm instead of .mp3 (ffmpeg not on PATH)
   - cookies.txt not found

3. Transcription (transcribe_audio.py)
   - CUDA out of memory (fall back to CPU)
   - Empty output (wrong LANGUAGE setting)
   - Corporate proxy blocking CTranslate2 (apply_no_proxy_env not called first)

4. Transcript download (read_transcript.py)
   - TranscriptsDisabled: video has no captions
   - Empty transcripts/ folder after running

5. Word clouds and summaries
   - wordcloud.html shows nothing (browser blocking local file reads)
   - make_summaries.py prints 0 unsummarised transcripts (already summarised, or wrong base name)

6. TTS (generate_speech.py)
   - Voice model not found (first-run download)
   - piper binary not found

Keep each entry to 2–4 sentences: what the symptom is, what causes it, how to fix it.
Output only the file content.
```

**Verify:** Save as `docs/troubleshooting.md`. Skim each entry against what you actually
encountered in lessons 03–09.

---

### 10.7 — Final commit and tag

**Prompt:**
```
Give me git commands to:
1. Add and commit all files from this lesson:
   .devcontainer/devcontainer.json
   .devcontainer/Dockerfile
   Dockerfile.standalone
   .github/workflows/ci.yml
   notebooks/colab_setup.ipynb
   README.md  (updated)
   docs/troubleshooting.md

   Commit message: "lesson 10: devcontainer, CI, Colab notebook, deployment docs"

2. Create a git tag marking the completed curriculum:
   Tag name: v1.0-curriculum
   Message: "10-lesson curriculum complete"

3. Push everything including the tag.

OS: Windows, Command Prompt.
```

**Verify:**
```cmd
git log --oneline
git tag
```
You should see nine commits and the `v1.0-curriculum` tag.

---

## When the AI misbehaves

**The devcontainer `Dockerfile` installs ffmpeg via `pip install ffmpeg` instead of `apt-get`.**
Push back using the same argument as Lesson 03: "Inside the container we're on Linux. `pip install
ffmpeg` installs a Python stub, not the real binary. Can you change it to `apt-get install -y
ffmpeg` in the RUN layer?"

**The CI workflow tries to `conda activate` on ubuntu-latest.**
GitHub Actions' ubuntu runner doesn't have conda by default. The workflow should use `pip install`
directly (or use the `setup-miniconda` action if conda is genuinely needed). For this project,
`pip install -r requirements.txt` is enough in CI. Push back: "The CI runner doesn't have conda.
Can you change the Python package install step to use pip directly?"

**The `.ipynb` notebook is not valid JSON or uses the wrong nbformat.**
The correct nbformat is 4, not 3 or 5. Cell types must be `"markdown"` or `"code"` (lowercase).
Code cells must have `"outputs": []` and `"execution_count": null`. If the file fails to validate,
ask: "Can you output the notebook as a valid nbformat 4 JSON? Each code cell needs an 'outputs'
and 'execution_count' key."

**The README deployment section recommends `pip install faster-whisper` without mentioning the
CTranslate2 size.**
CTranslate2 is ~300 MB on first install. Users in bandwidth-constrained environments should know
this. Add a note: "The first `pip install` will download CTranslate2 (~300 MB compiled library).
This is expected."

---

## What you have now

Files added this lesson:

```
learn-better/
    .devcontainer/
        devcontainer.json   (new)
        Dockerfile          (new)
    .github/
        workflows/
            ci.yml          (new)
    Dockerfile.standalone   (new)
    notebooks/
        colab_setup.ipynb   (new)
    docs/
        troubleshooting.md  (new)
    README.md               (updated — Deployment section added)
```

Repo state: project complete. Full pipeline runs end-to-end on Windows (native), in a VS Code
devcontainer, or in Google Colab. CI checks syntax on every push. Nine commits, tagged `v1.0-curriculum`.

---

## Curriculum complete

You have built the complete **learn-better** project from an empty folder, working through:

- Lesson 01 — Understanding AI assistant capabilities and the re-orient pattern
- Lesson 02 — Project scaffold, git, GitHub
- Lesson 03 — conda environment, ffmpeg, `lib/paths.py`
- Lesson 04 — First script, debugging cycle
- Lesson 05 — Audio and caption download
- Lesson 06 — Local Whisper transcription
- Lesson 07 — Runner automation, `init.bat`
- Lesson 08 — Summaries, word clouds, real `lib/textutil.py`
- Lesson 09 — TTS, reencoding, real `lib/net.py` and `lib/youtube.py`, end-to-end pipeline
- Lesson 10 — Devcontainer, CI, Colab, deployment docs

The full pipeline: `r` → `w` → `s` (+ AI paste) → `v` — downloads audio, transcribes it locally,
generates a structured summary with AI assistance, and synthesises speech from that summary, all
without sending your audio to any cloud service.

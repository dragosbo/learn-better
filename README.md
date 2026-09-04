# learn-better
useful minimalist free learning solutions

Minimalist, free tools that turn YouTube content into study material: audio,
transcripts, and metadata that feed downstream steps like summarization,
mind-maps, and Obsidian-based knowledge consolidation. See `plan.md` for the
roadmap.

---

## Dependencies

### Python packages (installed via `requirements.txt`)

**Active packages** (the current workflow):

| Package | Purpose |
|---|---|
| `yt-dlp[default,curl-cffi]` | Core, actively-maintained downloader for audio, video listing, and subtitles. |
| `curl_cffi` | Powers yt-dlp's browser **impersonation** (TLS fingerprint). Required, without it YouTube blocks subtitle/format fetches (bot-check, empty subtitle responses). |
| `youtube-transcript-api` | Fetch video transcripts/subtitles. |
| `faster-whisper` | Local, no-API-key speech-to-text (and translate-to-English) for clips whose captions are disabled. CPU-friendly (`int8`); needs `ffmpeg`. Used by `transcribe_audio.py` (`w.bat`). |
| `piper-tts` | Local, no-API-key **text-to-speech** (MIT, CPU-only, no GPU). Turns a transcript/summary into narrated audio. Downloads a small per-voice `.onnx` model on first use. Used by `generate_speech.py` (`v.bat`). |
| `pandas` | Metadata tables/dataframes. |
| `ipykernel` | Lets the Jupyter notebooks run inside this environment. |

**Legacy packages** (kept only for older/archived scripts, not the active tools):
`pytube` is still imported by `code/youtube_download.py` (fragile; superseded by
yt-dlp), and `google-api-python-client` is only used by the retired
`ignore/get_my_playlists.py`. `scrapetube` was **dropped** (broken since 2025;
no active code uses it) — `yt-dlp` replaces it.

Install them all with (see step 3 for the full flow):

```cmd
pip install -r requirements.txt
```

### System dependency (NOT pip-installable): ffmpeg

`yt-dlp` needs the **ffmpeg** binary to convert or merge audio (e.g. to real
`.mp3`). It is a system tool, not a Python package, so it is **not** in
`requirements.txt` and must be installed separately. Pick the option matching
your setup:

```cmd
conda install -c conda-forge ffmpeg -y   :: installs into the active conda env (recommended)
winget install ffmpeg                     :: system-wide (Windows; may prompt for elevation)
choco install ffmpeg -y                   :: system-wide (Windows; run as Administrator)
```

```bash
brew install ffmpeg          # macOS
sudo apt install ffmpeg      # Debian / Ubuntu
```

Verify (open a new terminal first if you installed system-wide):

```cmd
ffmpeg -version
```

Once ffmpeg is on your PATH (or in your active conda env), yt-dlp finds it
automatically.

### Recommended: a JavaScript runtime (Deno)

Recent yt-dlp prints `No supported JavaScript runtime could be found` and warns
that "YouTube extraction without a JS runtime has been deprecated." The tools
still work without one (impersonation via `curl_cffi` covers subtitles and
audio), but YouTube increasingly relies on JS in its player, so installing a
runtime is **recommended**: it removes the warning and can restore some formats
yt-dlp would otherwise skip.

Install **Deno** once (it is the runtime yt-dlp enables by default):

```cmd
winget install DenoLand.Deno   :: Windows (open a NEW terminal afterwards)
```

```bash
brew install deno              # macOS
curl -fsSL https://deno.land/install.sh | sh   # Linux
```

Open a new terminal so `deno` is on your PATH, then verify:

```cmd
deno --version
```

yt-dlp finds it automatically on the next run; the JS-runtime warning is gone.
The code also passes `no_warnings` to yt-dlp on the transcript/audio paths, so
the message is suppressed even if a runtime is missing, but installing Deno is
still the proper fix.

---

## Environment setup

Follow these steps in order. Skipping the Python-version check is the most
common cause of a broken install.

### 0. Prerequisites

- **Python 3.12** (3.10+ works; 3.12 is recommended). Do **not** use Python 3.7,
  which ships as the base of some older Anaconda installs. The modern
  dependencies (`yt-dlp`, `pandas` 2.x) require
  Python ≥ 3.10. On an older interpreter, pip silently falls back to broken
  ancient versions or fails outright with `No matching distribution found`.
- One of: **conda**, or **Python 3.12 from [python.org](https://www.python.org/downloads/)**,
  or a **Dev Container / GitHub Codespaces** setup.
- `git` (to clone the repo).

Clone the repo and move into it:

```cmd
git clone https://github.com/dragosbo/learn-better.git
cd learn-better
```

### 1. Create an isolated Python 3.12 environment

Pick the option that matches your setup. An isolated environment keeps these
dependencies from colliding with your system Python.

#### Option A — conda (recommended if you already have Anaconda/Miniconda)

```cmd
conda create -n learn-better python=3.12 -y
conda activate learn-better
```

If your conda is old and does not offer Python 3.12, update it first, then retry
the create step:

```cmd
conda update -n base conda -y
```

#### Option B — venv (requires Python 3.12 installed from python.org)

Windows (cmd):

```cmd
py -3.12 -m venv .venv
.venv\Scripts\activate
```

macOS / Linux (bash/zsh):

```bash
python3.12 -m venv .venv
source .venv/bin/activate
```

#### Option C — Dev Container / GitHub Codespaces

Open the repo in a container ("Reopen in Container" in VS Code, or create a
Codespace). The `.devcontainer` builds on Python 3.12 and runs the install for
you automatically, you can skip straight to step 4 (verify).

### 2. Verify the interpreter BEFORE installing

This one check prevents the most common failure:

```cmd
python --version
```

It **must** print `Python 3.12.x`. If it prints `Python 3.7.x` (or anything
below 3.10), the environment is not active, re-run the activate command from
step 1. Do not continue until this shows 3.12.

### 3. Install dependencies

```cmd
python -m pip install --upgrade pip
pip install -r requirements.txt
```

This installs `yt-dlp`, `youtube-transcript-api`, `curl_cffi`, `pandas`, and
`ipykernel` (the active stack), plus the legacy `pytube` and
`google-api-python-client`. Pinned versions live in `requirements.txt`.

### 3b. Install ffmpeg (needed to download/convert audio)

ffmpeg is a system binary, not a pip package (see the Dependencies section
above). The simplest option inside a conda env:

```cmd
conda install -c conda-forge ffmpeg -y
```

Then confirm it is available:

```cmd
ffmpeg -version
```

Skip this only if you never download/convert audio with `yt-dlp`.

### 4. Verify the install works

Confirm every core package imports cleanly:

```cmd
python -c "import youtube_transcript_api, yt_dlp, pandas, curl_cffi, ipykernel; print('all imports OK')"
```

You should see `all imports OK`. If any import fails, re-check step 2 (you are
almost certainly on the wrong interpreter).

> **No API key needed.** The active tools (`read_channel.py`,
> `read_transcript.py`, the notebook) all use `yt-dlp` and work without a
> Google API key. The old API-key workflow (`get_my_playlists.py`) has been
> retired to the git-ignored `ignore/` folder.

---

## Deploying / running anywhere

You can run this project locally, in a container, or in the cloud. They all end
up at the same place: a **Python 3.12** environment with `requirements.txt`
installed and **ffmpeg** available. Pick whichever fits.

### ⚡ 1-click deploy (zero local setup)

Three targets get you a ready-to-run environment (ffmpeg + all dependencies +
the `data/` output layout) with a single click — no manual install steps:

| Target | How | What you get |
|---|---|---|
| **Google Colab** | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/dragosbo/learn-better/blob/main/notebooks/colab_setup.ipynb) → **Runtime → Run all** | Free T4 GPU (fast Whisper), notebook opens the repo and installs everything in the first cell. |
| **GitHub Codespaces** | [![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/dragosbo/learn-better) | Full VS Code in the browser; the `.devcontainer/` builds Python 3.12 + ffmpeg + deps automatically. Persists per codespace. |
| **VS Code / Kiro Dev Container** | Open the repo → **Reopen in Container** (or *Dev Containers: Reopen in Container*) | Same `.devcontainer/` locally on Docker; one build, then everything works. |

> **"1-click" = a ready-to-run env.** ffmpeg, the Python deps, and the `data/`
> layout are all set up for you; run any tool with `python code/<script>.py`.
> Typing the bare one-letter names (`r`, `w`, …) is a separate optional
> convenience — see **Running the tools** for the `scripts/` + PATH step.

### Platform overview

| Where | Best for | Setup effort |
|---|---|---|
| **Local — conda** | Everyday use; conda installs ffmpeg too. | One env create. |
| **Local — pip/venv or uv** | Minimal tooling or fast rebuilds. | Env + manual ffmpeg. |
| **Dev Container / Codespaces** | Reproducible env, zero manual steps. | 1-click (above). |
| **Docker / Podman** | CI, servers, scripted batch runs. | Build an image. |
| **Google Colab** | Free GPU for Whisper; quick experiments. | 1-click (above). |

### Local — conda (recommended)

Conda is the only method that installs **ffmpeg** into the same environment, and
it matches what the `scripts/` runners assume. Identical on Windows/Linux/macOS:

```bash
conda create -n learn-better python=3.12 -y
conda activate learn-better
conda install -c conda-forge ffmpeg -y
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Verify: `python --version` (3.12.x), `ffmpeg -version`, and
`python -c "import yt_dlp, faster_whisper, pandas; print('OK')"`.

### Local — pip/venv or uv

Standard `venv` (or [uv](https://docs.astral.sh/uv/) for faster installs +
lockfiles). ffmpeg is a **separate, manual** step here (see **Dependencies**):
`winget install ffmpeg` (Windows) · `sudo apt install ffmpeg` (Debian/Ubuntu) ·
`brew install ffmpeg` (macOS).

```bash
py -3.12 -m venv .venv            # Windows: .venv\Scripts\activate
python3.12 -m venv .venv          # Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt   # or:  uv pip install -r requirements.txt
```

### Dev Container (VS Code / Kiro + Docker)

The repo ships a `.devcontainer/` on **Python 3.12-bullseye** that **installs
ffmpeg** (via the Dockerfile) and `requirements.txt` (via `postCreateCommand`),
and preloads the Python + Jupyter extensions — nothing manual.

1. Install [Docker](https://www.docker.com/) and the **Dev Containers** extension.
2. Open the repo and choose **Reopen in Container**.
3. Wait for the build. ffmpeg and deps are already there — run a tool directly:

   ```bash
   python code/read_channel.py
   ```

Inside the container use `./scripts/*.sh` runners or `python code/<script>.py`
directly (the `.bat` files are Windows-only and won't run in the Linux container).

### GitHub Codespaces

Codespaces runs the same `.devcontainer/` in the cloud — 1-click, no local setup.

1. **Code → Codespaces → Create codespace on main** (or the badge above).
2. It builds automatically (ffmpeg + deps included).
3. Run in the terminal — no ffmpeg step needed:

   ```bash
   python code/read_channel.py
   ```

Configure the source at the top of the script as you would locally. Outputs land
under `data/` in the codespace; download via the file explorer or push tracked
outputs.

### Docker / Podman (self-hosted, CI)

A slim, IDE-free image (`Dockerfile.standalone`: Python 3.12-slim + ffmpeg,
non-root). Mount the single `data/` folder to persist all outputs:

```bash
docker build -f Dockerfile.standalone -t learn-better .
# Linux/macOS:
docker run -it --rm -v "$(pwd)/data:/app/data" learn-better
# Windows cmd:  docker run -it --rm -v "%CD%\data:/app/data" learn-better
# Windows PS:   docker run -it --rm -v "${PWD}\data:/app/data" learn-better
```

Run a tool non-interactively, e.g.:

```bash
docker run --rm -v "$(pwd)/data:/app/data" learn-better \
  python code/transcribe_audio.py config/config_transcribe.json
```

Podman uses the same syntax (`podman build/run`); on Windows it runs through
WSL2, so use Linux-style volume paths (`/mnt/c/...`).

### Google Colab

1-click via the badge above (opens `notebooks/colab_setup.ipynb`; **Run all**).
Or clone manually in a cell:

```python
!apt-get -qq install -y ffmpeg
!git clone https://github.com/dragosbo/learn-better.git
%cd learn-better
!pip install -q -r requirements.txt
!python code/transcribe_audio.py config/config_transcribe.json
```

Notes for Colab:
- Free **T4 GPU** makes Whisper 5–10× faster (`Runtime → Change runtime type → T4`).
  `faster-whisper` uses CUDA automatically when a GPU is present.
- The YouTube **bot-check** is more likely on cloud IPs. If you hit
  "Sign in to confirm you're not a bot", upload a `cookies.txt` (see the cookies
  note under *Running the tools*) and point `COOKIES_FILE` at it.
- Sessions are ephemeral: save anything in `data/` to Google Drive before the
  runtime disconnects (see the notebook's Drive cell).

### Known gotchas

| Symptom | Fix |
|---|---|
| `ffmpeg: command not found` | ffmpeg is a **system binary**, not pip-installable. Install it (conda / winget / apt / brew) — see **Dependencies**. Only conda bundles it in-env. |
| `No module named 'curl_cffi'` | `pip install "yt-dlp[default,curl-cffi]"` — required for the YouTube bot-check bypass. Already in `requirements.txt`. |
| Container builds but ffmpeg missing | Use the repo's `.devcontainer/Dockerfile` / `Dockerfile.standalone` (both install ffmpeg). Don't hand-roll a base image without the ffmpeg layer. |
| Docker volume path errors | Linux/macOS: `$(pwd)/data`; Windows cmd: `%CD%\data`; PowerShell: `${PWD}\data`; Podman on Windows (WSL2): `/mnt/c/...`. |
| GPU not used in a container | GPU passthrough works only on **Linux host + NVIDIA** (`--gpus all`); not on Windows/macOS Docker Desktop. CPU still works. |
| Colab lost work on disconnect | Write results to Google Drive as they complete; don't batch at the very end. |
| conda solve is very slow | `conda config --set solver libmamba`. |

---

## Running the tools

Activate your environment first (step 1), then run any of the scripts below.
The helper runners live in the **`scripts/`** folder (they still call
`code/<script>.py` with no `cd`, so run them from the repo root):

```cmd
scripts\r.bat
scripts\wc.bat config\config_wordcloud.json
```

**Keep the one-letter UX by adding `scripts/` to your PATH.** Then the bare
names (`r`, `w`, `v`, …) work from the repo root, exactly as before they moved.

Windows (`cmd`) — for the current session:

```cmd
set PATH=%CD%\scripts;%PATH%
r
wc config\config_wordcloud.json
```

To make it permanent on Windows, add the full `...\learn-better\scripts` path
via **System Properties → Environment Variables → Path** (the safest way — it
edits the stored PATH without expanding or truncating it). `setx` also works but
writes the *expanded* PATH and truncates at 1024 chars, so prefer the GUI.

Linux/macOS (bash/zsh) — for the current session:

```bash
export PATH="$PWD/scripts:$PATH"
r.sh
w.sh config/config_transcribe.id.json
```

To make it permanent, add that `export` line (with the absolute repo path) to
your `~/.bashrc` / `~/.zshrc`.

> **Windows vs. Linux/macOS.** The one-letter helpers come in two forms:
> `.bat` for Windows `cmd` (e.g. `r`) and matching `.sh` for Linux/macOS and the
> containers/cloud shells (e.g. `r.sh`, or `bash scripts/r.sh`). The `.sh` runners
> activate the `learn-better` conda env if `conda` is present, otherwise they use
> the current `python` (which is how the Docker/Codespaces images are set up).
> Both forms call the same `code/<script>.py`. Without `scripts/` on PATH, invoke
> them by their path: `scripts\r.bat` (Windows) or `scripts/r.sh` (Linux/macOS).

- `c.bat` — activates the `learn-better` conda env (`c` from the repo root).
- `r.bat` — activates the env and runs `code\read_channel.py` (`r`).
- `t.bat` — activates the env and runs `code\read_transcript.py` (`t`).
- `s.bat` — activates the env and runs `code\make_summaries.py` to prepare
  transcript summaries (`s`); see "Summarize transcripts" below.
- `p.bat` — activates the env and runs `code\list_playlists.py` (`p`); see
  "List your playlists" below.
- `w.bat` — activates the env and runs `code\transcribe_audio.py` for Whisper
  speech-to-text (`w`, or `w config\config_transcribe.<mode>.json`); see
  "Transcribe audio with Whisper" below.
- `d.bat` — activates the env and runs `code\make_wordcloud.py` for one
  transcript (`d`); see "Word cloud" below.
- `wc.bat` — activates the env and runs `code\make_wordcloud.py` with a config
  (`wc config\config_wordcloud.json`) for batch/merge word clouds.
- `a.bat` — activates the env and runs `code\reencode_audio.py` to re-encode
  audio at a different bitrate (`a`, or `a config\config_reencode.json`); see
  "Audio re-encode / bitrate" below.
- `v.bat` — activates the env and runs `code\generate_speech.py` to turn a
  transcript/summary into narrated audio (`v`, or `v config\config_tts.json`);
  see "Text to speech" below.

### List your playlists (no API key)

`code/list_playlists.py` lists a channel's **public** playlists (title, id, video
count) and saves them to `data/playlists.json`. Set `CHANNEL` at the top of the
script to your `@handle`, `UC...` id, or full channel URL, then:

```cmd
p
```

(or `python code\list_playlists.py`).

#### Making playlists visible to the tool

The tool sees only **public** playlists — private and unlisted ones don't appear
on a channel's public playlists page, so they can't be enumerated without
authentication (an API key can't read them either; only OAuth can, which is a
lot of setup). The simplest fix is to make the playlists you want to process
**public**.

There's no bulk "make everything public" button in YouTube — you set visibility
per playlist. But it's quick, via YouTube Studio:

1. Go to **studio.youtube.com** → left sidebar → **Content** → **Playlists** tab.
2. Each playlist's visibility is shown in the list. Click the playlist (or the
   pencil/edit icon).
3. Find the **Visibility** dropdown (Public / Unlisted / Private) → set to
   **Public** → **Save**.
4. Repeat for each one.

> Public means anyone can find and view the playlist and its list of videos, so
> leave anything personal private (it just won't be enumerable). Unlisted
> playlists are still readable **if you already know the exact `PL...` id**, but
> they won't show up when listing a channel's playlists.

### Read a channel/playlist: download audio + transcripts (no API key)

**Recommended starting point.** `code/read_channel.py` reads a playlist,
channel, or search using `yt-dlp` + `youtube-transcript-api`, no Google API key
needed. For each clip it saves the audio and the transcript, and clearly flags
clips that have no transcript.

What it does, per clip (up to `LIMIT`, default **5**, never more):

1. **Lists** the videos from your chosen source.
2. **Saves the transcript** to `data/transcripts/<title> [<id>].txt`. If a clip
   has no transcript (subtitles disabled), it prints a loud `!! NO TRANSCRIPT`
   line and lists that clip in the end-of-run summary.
3. **Downloads the audio** to `data/audio/<title> [<id>].mp3`. Both steps
   **skip** any file already present, so re-running only fetches what's missing.

Configure the source at the top of the file (set ONE, leave the others `None`):

```python
PLAYLIST_ID = "PLxxxxxxxx"          # a playlist
CHANNEL     = "@your_handle"        # or a whole channel (handle or UC... id)
SEARCH      = "some search terms"   # or a search
LIMIT       = 5                     # max clips to process
```

Run it:

```cmd
r
```

(or `python code\read_channel.py`). Output goes to `data/audio/` and
`data/transcripts/` (both git-ignored).

Notes:
- **mp3 conversion needs ffmpeg** (see Dependencies). Set `AUDIO_FORMAT = None`
  in the file to skip conversion and keep the native `.webm`/`.m4a` instead.
- **Bot-check / "Sign in to confirm you're not a bot":** YouTube may block
  anonymous downloads. Provide cookies, either set
  `COOKIES_FROM_BROWSER = ("chrome", None)` (must be logged into YouTube in
  that browser; close it first on Windows), or export a `cookies.txt` and set
  `COOKIES_FILE = "code/cookies.txt"`. The cookies.txt option is also the only
  one that helps the transcript step.

### Transcribe audio with Whisper (`w.bat`)

For clips whose YouTube captions are disabled (the ones the tools flag as
`NO TRANSCRIPT`), generate a transcript from the audio using
[`faster-whisper`](https://github.com/SYSTRAN/faster-whisper) — a fast,
CPU-friendly, no-API-key speech-to-text engine. `code/transcribe_audio.py` writes
to `data/generated_transcripts/<title> [<id>].whisper.<lang>.txt` (named from the
audio file), and **skips** any transcript already present.

It is driven by small JSON config files in the `config/` folder, passed to `w`:

```cmd
w                                   :: uses config\config_transcribe.json (or in-file defaults)
w config\config_transcribe.name.json  :: pick files by name substring
w config\config_transcribe.id.json    :: pick files by YouTube video id
w config\config_transcribe.source.json:: playlist/channel/search, captions-first
```

Each config sets `select_by` and the Whisper options:

- **`select_by = "name"`** — `select` is a list of case-insensitive substrings
  matched against audio file names.
- **`select_by = "id"`** — `select` is a list of YouTube video ids (the `[<id>]`
  in each audio file name; copy them from `data/playlists.json`).
- **`select_by = "all"`** — every audio file in `data/audio/` (slow).
- **`select_by = "source"`** — the real "fill the gaps" use case: give a
  `playlist_id` / `channel` / `search`, and for each video it uses the YouTube
  caption transcript if one exists, and **only** Whisper-transcribes the
  caption-less clips (reusing or downloading their audio; the model loads only if
  a clip actually needs it).

**Transcribe vs. translate** (the `task` key):

- `task = "transcribe"` — text in the audio's original language. Pin `language`
  (e.g. `"fr"`, `"ro"`) for a same-language transcript, or leave it `null` to
  auto-detect.
- `task = "translate"` — Whisper translates to **English only** (a fixed model
  capability; it cannot target French/Romanian). Output is always
  `.whisper.en.txt`.

Model/quality knobs (`model_size`, `device`, `compute_type`) default to
`base` / `cpu` / `int8`. Bump `model_size` to `"small"`/`"medium"` for better
accuracy (slower). On the sample clip, `base` scored ~95% word accuracy against
YouTube's captions (see "Whisper transcription quality" below).

```cmd
w config\config_transcribe.source.json
```

Output goes to `data/generated_transcripts/` (git-ignored). Re-running skips
clips that already have a transcript.

### Summarize transcripts (`s.bat`)

Turn the downloaded English transcripts into concise, structured summaries
(table of contents, sections, strengths, weaknesses). The format is defined
once in `skill_summary.md` and reused for every video.

**Important — how this works.** A batch script cannot *write* the summaries by
itself: analyzing a transcript and drafting prose is an AI task. So `s.bat`
does the deterministic half and hands the thinking to Kiro:

```cmd
s
```

`code/make_summaries.py` then:

1. finds every English transcript from **both** sources — YouTube captions
   (`data/transcripts/*.en.txt`) and Whisper output
   (`data/generated_transcripts/*.whisper.en.txt`),
2. picks **one per video** (captions preferred; a Whisper transcript is used only
   when that video has no caption), deduplicating by the `[<id>]` video id so the
   same clip is never listed twice,
3. checks which already have a matching `data/summaries/<base>.summary.md`,
4. prints which are done vs. missing (tagging each `(caption)` or `(whisper)`), and
5. for the missing ones, prints a single ready-to-paste instruction whose paths
   point at the correct folder.

You copy that printed instruction into the Kiro chat, e.g.:

> Apply skill_summary.md to these transcripts and save each to
> data/summaries/<base>.summary.md:
> - data/transcripts/Some Video [abc123].en.txt
> - data/generated_transcripts/Another Video [def456].whisper.en.txt

Kiro reads each transcript and writes the summary following `skill_summary.md`.
Existing summaries are left alone, so re-running only surfaces new transcripts.
To regenerate one, delete its `data/summaries/*.summary.md` and run `s` again.

Typical flow for a new video: `t` or `w` (get a transcript, caption or Whisper) →
`s` (list what needs summarizing) → paste the instruction into Kiro.

Note: only English transcripts are summarized, and both a caption and a Whisper
transcript for the same video map to the same `data/summaries/<base>.summary.md`.
Summaries are saved to `data/summaries/` (this folder **is** tracked by git,
unlike `data/audio/`, `data/transcripts/`, and `data/generated_transcripts/`,
since summaries are authored content rather than regenerated downloads).

### Word cloud (`d.bat` / `wc.bat`)

Turn a transcript into a **word cloud**. This is split in two, matching the rest
of the repo: a Python script produces **data** (a `word_cloud.json`), and a small
HTML page renders it **client-side** with a JavaScript library. No `matplotlib`,
no plotting deps.

**1. Generate the data.** `code/make_wordcloud.py` reads a transcript (from
`data/transcripts/` or `data/generated_transcripts/`), strips timestamps, tokenizes
(Unicode-aware, keeps accented fr/ro letters), drops stopwords + very short
words, counts frequencies, and writes
`data/wordclouds/<title> [<id>].word_cloud.json` (skip-if-exists).

One transcript (edit `INPUT` at the top of the script):

```cmd
d
```

Several at once, or a merged cloud, via a JSON config in `config/`:

```cmd
wc config\config_wordcloud.json          :: batch: one cloud per selected transcript
wc config\config_wordcloud.merge.json    :: merge: ONE cloud from many transcripts
```

Config keys (`config/config_wordcloud.json`):

- **`select_by`** — `input` (the single `input` file/id) | `name` (file-name
  substrings in `select`) | `id` (video ids in `select`) | `all` (every
  transcript). Selection dedupes by video id, preferring the caption transcript.
- **`merge`** + **`output_name`** — when `merge: true`, all selected transcripts
  are combined into ONE `data/wordclouds/<output_name>.word_cloud.json` (word
  counts summed). Great for a whole series (e.g. `output_name: "git-series"`).
- **`language`** — `en` | `fr` | `ro`, picks the built-in stopword list.
- **`min_length`**, **`max_words`**, **`lowercase`**, **`stopwords_extra`** — tune
  the tokenizer.

> **Same-language rule.** A word cloud uses one stopword list, so a batch/merge
> must be a single language. If the selected transcripts' language suffixes don't
> all match `language`, the run aborts with a message listing the offenders —
> narrow the selection (by name/id) or set `language` and run per language.

**2. Render it.** Open `wordcloud.html` in a browser, click **Load a JSON**, and
pick a file from `data/wordclouds/`. Word size scales with frequency. (Opening
from disk uses the file picker; to use the `?file=` URL param instead, serve the
folder with `python -m http.server` — see the on-page note.) The renderer uses
[wordcloud2.js](https://github.com/timdream/wordcloud2.js) from a CDN; the JSON is
renderer-agnostic, so a different library (d3-cloud, ECharts) could be swapped in
without touching the Python side.

Output goes to `data/wordclouds/` (git-ignored). Re-running skips files that
already exist; delete one (or change `output_name`) to regenerate.

### Audio re-encode / bitrate (`a.bat`)

Re-encode existing downloaded audio to a **different (usually lower) bitrate**,
handy for shrinking files or standardizing them for playback. `code/reencode_audio.py`
reads from `data/audio/`, re-encodes with **ffmpeg**, and writes to a separate
`data/audio_reencoded/` folder so the originals are never touched (re-encoding to
a lower bitrate is lossy and irreversible).

This uses **only free tooling**: ffmpeg is already required by the project
(yt-dlp uses it for mp3 conversion — see "Install ffmpeg" above). No new pip
package, no API, no paid service. The default codec `libmp3lame` ships with
ffmpeg and plays everywhere.

Run it with the default config (Git & GitHub clip at 96 kbps mp3):

```cmd
a
```

Or pass an explicit config:

```cmd
a config\config_reencode.json
```

Config keys (`config/config_reencode.json`):

- **`select_by`** — `name` (case-insensitive substrings of the audio file name,
  in `select`) | `id` (11-char YouTube ids, the `[<id>]` in the name, in
  `select`) | `all` (every audio file in `data/audio/`, slow).
- **`bitrate`** — the target audio bitrate: `"64k"`, `"96k"`, `"128k"` (or a
  plain number like `64000`). Lower = smaller file, lower quality. 96k is a good
  balance for speech.
- **`format`** / **`codec`** — output container/encoder. Defaults `mp3` /
  `libmp3lame` (free, universal). `m4a`/`aac`, `ogg`/`libvorbis`, `opus`/
  `libopus` also work.
- **`sample_rate`** (ffmpeg `-ar`) / **`channels`** (ffmpeg `-ac`, e.g. `1` =
  mono to shrink further) — optional; `null` keeps the source value.

Output files are named `data/audio_reencoded/<name>.<bitrate>.<ext>` (e.g.
`... .96kbps.mp3`), so different bitrates coexist. Re-running **skips** files
that already exist; delete one (or pick a new bitrate) to regenerate. The run
prints an `original -> new (saved %)` line per file. Output goes to
`data/audio_reencoded/` (git-ignored).

Verify a result played the way you expect, or check its bitrate with `ffprobe`
(ships with ffmpeg):

```cmd
ffprobe -v error -show_entries format=bit_rate -of default=noprint_wrappers=1 "data\audio_reencoded\<file>.96kbps.mp3"
```

### Text to speech (`v.bat`)

Turn study material back into audio: `code/generate_speech.py` reads a text
source (a `data/summaries/*.summary.md`, a `data/transcripts/` caption file, or a
`data/generated_transcripts/` Whisper file), synthesizes narration with the free,
local **Piper** engine, and writes a `.wav` to `data/tts_output/`. This is the
opposite direction of the Whisper step (text → audio).

Free tooling only: **Piper** is MIT-licensed, CPU-only, no GPU, no API key, no
paid service (`pip install piper-tts`). On first use it downloads a small
per-voice `.onnx` model into `data/tts_output/.voices/` (cached after). Optional
`mp3` output reuses the ffmpeg binary the project already requires.

Run it with the default config (Git & GitHub summary, `en_US-lessac-medium`
voice, wav):

```cmd
v
```

Or pass an explicit config:

```cmd
v config\config_tts.json
```

Config keys (`config/config_tts.json`):

- **`select_by`** — `name` (case-insensitive substrings of the file name, in
  `select`) | `id` (11-char YouTube ids, the `[<id>]` in the name, in `select`) |
  `all` (every text file, slow). When several sources exist for one video, ONE is
  voiced per id, preferring **summary > caption transcript > Whisper transcript**.
- **`voice`** — a Piper voice id (default `en_US-lessac-medium`). Many free voices
  exist, including `fr_FR-*` and `ro_RO-*`; changing this downloads that voice on
  first use.
- **`length_scale`** — speaking **speed**: it multiplies the audio *length*, so
  **below 1.0 = faster** (shorter audio), **above 1.0 = slower** (longer). Presets:
  `0.9` faster, `1.0` normal, `1.15` slower/clearer. A non-1.0 value adds a
  `.s<scale>` tag to the output name so speeds coexist. (See
  `config/config_tts.speed09.json` for a ready-made faster preset.)
- **`format`** — `wav` (Piper native) or `mp3` (converted via ffmpeg).
- **`max_chars`** — optional cap on input length for a quick test (`null` = whole
  file).

Output files are named `data/tts_output/<base>.<voice>[.s<scale>].<ext>` (e.g.
`... .en_US-lessac-medium.wav`, or `... .en_US-lessac-medium.s0.9.wav` at 0.9
speed). Re-running **skips** files that already exist. Output goes to
`data/tts_output/` (git-ignored). Open a result in any player, or check it with
`ffprobe`:

```cmd
ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1 "data\tts_output\<file>.wav"
```

### Download audio from YouTube (legacy)

`pytube`-based downloader for a search, a public playlist, or single videos.
Audio is saved to the `data/audio/` folder.

```cmd
python code\youtube_download.py
```

### Explore in Jupyter

The notebook has cleaner, reusable helpers (`vl`, `y2a`, `vm`) and builds a
metadata table with pandas.

`ipykernel` (installed via `requirements.txt`) lets this environment show up as
a notebook kernel. Then either open the notebook in VS Code and pick the
`learn-better` kernel, or run Jupyter directly:

```cmd
pip install jupyter
jupyter notebook notebooks\yt_download.ipynb
```

(The Dev Container already includes the Jupyter extension.)

---

## Whisper transcription quality (validation)

Before generalizing the speech-to-text step, we validated it on one clip.
`code/transcribe_audio.py` transcribes *Git and GitHub Tutorial for Beginners*
with `faster-whisper` (model `base`, CPU, `int8`) to
`data/generated_transcripts/...whisper.en.txt`. We then compared that output against
YouTube's own English captions for the same video.

### How the numbers were obtained

`code/compare_transcripts.py` reads both files, strips the `[HH:MM:SS]`
timestamps from the captions, lowercases everything, and reduces each text to a
stream of word tokens (punctuation removed). It then computes:

- **Sequence similarity** (`difflib`, order-sensitive) and an approximate
  **word error rate (WER)** from the insert/delete/replace opcodes, using the
  YouTube captions as the reference.
- **Bag-of-words overlap** (order-insensitive multiset intersection): Jaccard
  and reference-vocabulary coverage.
- The **top divergent words** in each direction, to see *what* actually differs.

Reproduce it with:

```cmd
python code\compare_transcripts.py
```

### Result: ~95% quality

| Metric | Result | Meaning |
|---|---|---|
| Sequence similarity (order-sensitive) | **96.4%** | Same words, same order |
| Word accuracy (1 − approx. WER) | **~95.4%** | ~4.6% raw word error rate |
| Bag-of-words coverage of reference | **97.6%** | Nearly all real words captured |
| Jaccard overlap (multiset) | 94.0% | Overall vocabulary agreement |

For the `base` model on CPU this is a solid, usable result. Crucially, almost
none of the divergences are genuine mis-hearings, they are formatting and
spelling conventions:

- **"git" heard as "get"** (the single biggest contributor to WER) — cosmetic.
- **"GitHub" split into "Git Hub"**, `fixtemp` vs. "fix temp", etc. — spacing.
- **Spoken symbols spelled out:** "dash" for `-`, "dot" for `.`, "e mail" for
  "email". Whisper transcribes speech; the captions render symbols.
- **Minor filler swaps** ("can" vs. "could"/"will") that don't change meaning.

So the *semantic* error rate is well below the raw 4.6%. For the summary
pipeline, which cares about meaning, the `base` output is already good enough.

### Key recommendations

1. **Bump the model** in `transcribe_audio.py`: `MODEL_SIZE = "small"` (or
   `"medium"`) drops the raw WER toward 2–3% and better handles "git"/"GitHub".
   Tradeoff: `small` is ~2–3x slower, `medium` much slower on CPU.
2. **Prime domain vocabulary** with `initial_prompt` on
   `model.transcribe(..., initial_prompt="Git, GitHub, git config, gitignore,
   git commit, repository, branch")` — the cheapest fix for the
   "get/git/GitHub" errors without a larger model.
3. **Pin the language** to `LANGUAGE = "en"` for known-English clips to avoid
   auto-detection slips and shave a little time.
4. **Optional post-processing** if you want output closer to the captions: map
   " dash " → " -", " dot " → ".", "git hub" → "GitHub". Not needed for
   summaries, where meaning is already intact.

---

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `No matching distribution found for yt-dlp>=...` | Installing on Python < 3.10 (often Anaconda base 3.7). | Create and activate a 3.12 env (step 1), verify with `python --version` (step 2). |
| pip installs very old versions with no error | Same, old interpreter, pip falling back to legacy releases. | Same as above. |
| `python --version` still shows 3.7 after activating | Environment not actually active in this shell. | Re-run the activate command; open a new terminal if needed. |
| `conda create` can't find `python=3.12` | Old conda. | `conda update -n base conda -y`, then retry. |
| `ModuleNotFoundError` when running a script | Wrong interpreter / deps not installed in this env. | Activate the env, re-run steps 3–4. |
| `pytube` errors / downloads failing | `pytube` breaks often against YouTube changes. | `yt-dlp` is installed as the robust alternative; prefer it (migration is on the roadmap in `plan.md`). |
| `ffmpeg not found` / yt-dlp can't convert to mp3 | ffmpeg not installed or not on PATH. | Install ffmpeg (step 3b / Dependencies section); open a new terminal; check `ffmpeg -version`. |
| yt-dlp: `Sign in to confirm you're not a bot` | YouTube is blocking anonymous downloads. | Pass browser cookies to yt-dlp (`cookiesfrombrowser`) or an exported `cookies.txt`; update yt-dlp with `pip install -U yt-dlp`. |
| yt-dlp: `No supported JavaScript runtime could be found` | No JS runtime installed. Harmless (subtitles/audio still work). | Install Deno (`winget install DenoLand.Deno`; see "Recommended: a JavaScript runtime"), open a new terminal. The code also sets `no_warnings`, so it stays quiet even without Deno. |
| VS Code asks to install `ipykernel` for the notebook | Kernel package missing in this env. | `pip install -r requirements.txt` (includes `ipykernel`), then pick the env as the notebook kernel. |

---

## Repository layout

```
learn-better/
├── code/                # scripts
│   ├── read_channel.py        # no-API-key: audio + transcripts (recommended)
│   ├── read_transcript.py     # no-API-key: transcripts only (per language)
│   ├── list_playlists.py      # no-API-key: list a channel's public playlists (p.bat)
│   ├── transcribe_audio.py    # Whisper speech-to-text + translate (w.bat)
│   ├── compare_transcripts.py # Whisper-vs-captions quality check
│   ├── make_summaries.py      # lists transcripts needing a summary (used by s.bat)
│   ├── make_wordcloud.py      # transcript -> word_cloud.json (d.bat / wc.bat)
│   ├── reencode_audio.py      # re-encode audio at a target bitrate (a.bat)
│   ├── generate_speech.py     # text -> speech via Piper (v.bat)
│   ├── youtube_download.py    # legacy pytube audio downloader
│   └── languages.json         # subtitle languages to fetch (en, fr, ro)
├── lib/                 # reusable helpers: net, textutil, paths, youtube
├── notebooks/           # yt_download.ipynb (reusable helpers + metadata)
├── .devcontainer/       # Codespaces / Dev Container (Python 3.12)
├── data/                # ALL generated outputs live here (git-ignored, except summaries/)
│   ├── audio/               # downloaded audio (git-ignored)
│   ├── audio_reencoded/     # re-encoded audio at a target bitrate (git-ignored)
│   ├── tts_output/          # text-to-speech audio + .voices/ cache (git-ignored)
│   ├── transcripts/         # saved caption transcripts (git-ignored)
│   ├── generated_transcripts/ # Whisper transcripts (git-ignored)
│   ├── summaries/           # AI-generated summaries (TRACKED by git via .gitignore negation)
│   ├── wordclouds/          # *.word_cloud.json (git-ignored)
│   └── playlists.json       # channel playlists (git-ignored)
├── config/              # run configs: config_transcribe*.json, config_wordcloud*.json, config_reencode.json, config_tts*.json
├── chats/               # AI chat logs: kiro_* and claude_* (prompts + conversation)
├── ignore/              # git-ignored: retired code + todo.md, mini_todo.md, notes
├── wordcloud.html       # renders a word_cloud.json (wordcloud2.js)
├── skill_summary.md     # reusable summary format/procedure
├── scripts/             # one-letter runners (add to PATH for c/r/t/s/p/w/d/wc/a/v)
│   ├── c.bat / c.sh     # activate the learn-better conda env
│   ├── r.bat / r.sh     # activate env + run read_channel.py
│   ├── t.bat / t.sh     # activate env + run read_transcript.py
│   ├── s.bat / s.sh     # activate env + run make_summaries.py (prep summaries)
│   ├── p.bat / p.sh     # activate env + run list_playlists.py
│   ├── w.bat / w.sh     # activate env + run transcribe_audio.py (Whisper)
│   ├── d.bat / d.sh     # activate env + run make_wordcloud.py (one transcript)
│   ├── wc.bat / wc.sh   # activate env + run make_wordcloud.py (config: batch/merge)
│   ├── a.bat / a.sh     # activate env + run reencode_audio.py (audio bitrate)
│   └── v.bat / v.sh     # activate env + run generate_speech.py (text to speech)
├── Dockerfile.standalone # slim Docker/Podman/CI image (ffmpeg, non-root); see how_to_deploy.md
├── .dockerignore        # keeps the Docker build context lean
├── how_to_deploy.md     # deployment guide: 12 platforms + image scripts
├── requirements.txt
├── plan.md              # roadmap and analysis
└── README.md
```

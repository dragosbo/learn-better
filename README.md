# learn-better
useful minimalist free learning solutions

Minimalist, free tools that turn YouTube content into study material: audio,
transcripts, and metadata that feed downstream steps like summarization,
mind-maps, and Obsidian-based knowledge consolidation. See `plan.md` for the
roadmap.

---

## Dependencies

### Python packages (installed via `requirements.txt`)

| Package | Purpose |
|---|---|
| `google-api-python-client` | YouTube Data API v3 client. Only used by the retired `ignore/get_my_playlists.py`; not needed by the active tools. |
| `scrapetube` | Older way to list playlist/channel videos. **Broken** (returns 0 videos); only referenced by the retired `ignore/get_my_playlists.py`. `yt-dlp` replaces it. |
| `youtube-transcript-api` | Fetch video transcripts/subtitles. |
| `yt-dlp[default,curl-cffi]` | Robust, actively-maintained downloader for audio/video, listing, and subtitles. |
| `curl_cffi` | Powers yt-dlp's browser **impersonation** (TLS fingerprint). Required, without it YouTube blocks subtitle/format fetches (bot-check, empty subtitle responses). |
| `pytube` | Older downloader (kept for the legacy scripts; breaks often). |
| `pandas` | Metadata tables/dataframes. |
| `ipykernel` | Lets the Jupyter notebooks run inside this environment. |

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

### Optional: a JavaScript runtime (silences a yt-dlp warning)

Recent yt-dlp prints `No supported JavaScript runtime could be found`. It still
works (impersonation via `curl_cffi` covers the important cases), but installing
a JS runtime removes the warning and can restore some formats. Optional:

```cmd
winget install DenoLand.Deno   :: Windows (open a new terminal afterwards)
```

```bash
brew install deno              # macOS
```

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

This installs the YouTube API client, transcript API, `scrapetube`, `yt-dlp`,
`pytube`, `pandas`, and `ipykernel`. Pinned versions live in `requirements.txt`.

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
python -c "import googleapiclient, scrapetube, youtube_transcript_api, yt_dlp, pytube, pandas, curl_cffi, ipykernel; print('all imports OK')"
```

You should see `all imports OK`. If any import fails, re-check step 2 (you are
almost certainly on the wrong interpreter).

> **No API key needed.** The active tools (`test_read_channel.py`,
> `test_read_transcript.py`, the notebook) all use `yt-dlp` and work without a
> Google API key. The old API-key workflow (`get_my_playlists.py`) has been
> retired to the git-ignored `ignore/` folder.

---

## Running the tools

Activate your environment first (step 1), then run any of the scripts below.
Two helper batch files are provided for convenience:

- `c.bat` — activates the `learn-better` conda env (`c` from the repo root).
- `r.bat` — activates the env and runs `code\test_read_channel.py` (`r`).
- `t.bat` — activates the env and runs `code\test_read_transcript.py` (`t`).
- `s.bat` — activates the env and runs `code\make_summaries.py` to prepare
  transcript summaries (`s`); see "Summarize transcripts" below.

### Read a channel/playlist: download audio + transcripts (no API key)

**Recommended starting point.** `code/test_read_channel.py` reads a playlist,
channel, or search using `yt-dlp` + `youtube-transcript-api`, no Google API key
needed. For each clip it saves the audio and the transcript, and clearly flags
clips that have no transcript.

What it does, per clip (up to `LIMIT`, default **5**, never more):

1. **Lists** the videos from your chosen source.
2. **Saves the transcript** to `transcripts/<title> [<id>].txt`. If a clip has
   no transcript (subtitles disabled), it prints a loud `!! NO TRANSCRIPT`
   line and lists that clip in the end-of-run summary.
3. **Downloads the audio** to `audio/<title> [<id>].mp3`. Both steps **skip**
   any file already present, so re-running only fetches what's missing.

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

(or `python code\test_read_channel.py`). Output goes to `audio/` and
`transcripts/` (both git-ignored).

Notes:
- **mp3 conversion needs ffmpeg** (see Dependencies). Set `AUDIO_FORMAT = None`
  in the file to skip conversion and keep the native `.webm`/`.m4a` instead.
- **Bot-check / "Sign in to confirm you're not a bot":** YouTube may block
  anonymous downloads. Provide cookies, either set
  `COOKIES_FROM_BROWSER = ("chrome", None)` (must be logged into YouTube in
  that browser; close it first on Windows), or export a `cookies.txt` and set
  `COOKIES_FILE = "code/cookies.txt"`. The cookies.txt option is also the only
  one that helps the transcript step.

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

1. finds every English transcript (`transcripts/*.en.txt`),
2. checks which already have a matching `summaries/<base>.summary.md`,
3. prints which are done vs. missing, and
4. for the missing ones, prints a single ready-to-paste instruction.

You copy that printed instruction into the Kiro chat, e.g.:

> Apply skill_summary.md to these transcripts and save each to
> summaries/<base>.summary.md:
> - transcripts/Some Video [abc123].en.txt

Kiro reads each transcript and writes the summary following `skill_summary.md`.
Existing summaries are left alone, so re-running only surfaces new transcripts.
To regenerate one, delete its `summaries/*.summary.md` and run `s` again.

Typical flow for a new video: `t` (download its transcript) → `s` (list what
needs summarizing) → paste the instruction into Kiro.

Note: only English (`.en.txt`) transcripts are summarized. Summaries are saved
to `summaries/` (this folder **is** tracked by git, unlike `audio/` and
`transcripts/`, since summaries are authored content rather than regenerated
downloads).

### Download audio from YouTube (legacy)

`pytube`-based downloader for a search, a public playlist, or single videos.
Audio is saved to an `audio/` folder.

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
| VS Code asks to install `ipykernel` for the notebook | Kernel package missing in this env. | `pip install -r requirements.txt` (includes `ipykernel`), then pick the env as the notebook kernel. |

---

## Repository layout

```
learn-better/
├── code/                # scripts
│   ├── test_read_channel.py   # no-API-key: audio + transcripts (recommended)
│   ├── test_read_transcript.py # no-API-key: transcripts only (per language)
│   ├── make_summaries.py      # lists transcripts needing a summary (used by s.bat)
│   ├── youtube_download.py    # legacy pytube audio downloader
│   └── languages.json         # subtitle languages to fetch (en, fr, ro)
├── notebooks/           # yt_download.ipynb (reusable helpers + metadata)
├── .devcontainer/       # Codespaces / Dev Container (Python 3.12)
├── audio/               # downloaded audio (git-ignored)
├── transcripts/         # saved transcripts (git-ignored)
├── summaries/           # AI-generated summaries (tracked by git)
├── ignore/              # retired/dead code (git-ignored): get_my_playlists.py, secrets.example.json
├── skill_summary.md     # reusable summary format/procedure
├── c.bat                # activate the learn-better conda env
├── r.bat                # activate env + run test_read_channel.py
├── t.bat                # activate env + run test_read_transcript.py
├── s.bat                # activate env + run make_summaries.py (prep summaries)
├── requirements.txt
├── plan.md              # roadmap and analysis
└── README.md
```

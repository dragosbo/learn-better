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

## How to run it (local or remote)

You can run this project four ways. They all end up at the same place: a Python
3.12 environment with `requirements.txt` installed. Pick whichever fits.

| Where | Best for | Setup effort |
|---|---|---|
| **Local** | Everyday use on your own machine. | Manual env (above). |
| **Dev Container** | Reproducible local env in VS Code + Docker. | One click. |
| **GitHub Codespaces** | Zero local install; runs in the cloud/browser. | One click. |
| **Google Colab** | Quick experiments, free GPU for later ASR work. | Paste a cell. |

### 1. Local

Follow **Environment setup** above (conda or venv), then run the tools with the
`c` / `r` / `t` / `s` batch files (Windows) or `python code/<script>.py`
(any OS). This is the default path and what the batch helpers assume.

### 2. Dev Container (VS Code + Docker)

The repo ships a `.devcontainer/` built on **Python 3.12-bullseye** that installs
`requirements.txt` automatically (via `postCreateCommand`) and preloads the
Python + Jupyter extensions.

1. Install [Docker](https://www.docker.com/) and the VS Code
   **Dev Containers** extension.
2. Open the repo in VS Code and choose **Reopen in Container**
   (or run *Dev Containers: Reopen in Container* from the command palette).
3. Wait for the build. Dependencies install themselves, so you can skip straight
   to running the tools:

   ```bash
   python code/read_channel.py
   ```

   (The `.bat` helpers assume a conda env named `learn-better`; inside the
   container just call `python` directly.)

You still need **ffmpeg** for mp3 conversion; add it in the container with
`sudo apt install ffmpeg` (or set `AUDIO_FORMAT = None` to skip conversion).

### 3. GitHub Codespaces (nothing to install)

Codespaces runs the same `.devcontainer/` in the cloud, so there is no local
setup at all.

1. On the GitHub repo page, click **Code &rarr; Codespaces &rarr; Create codespace on main**.
2. Wait for it to build (it reuses the Dev Container config, so deps install
   automatically).
3. In the Codespaces terminal:

   ```bash
   sudo apt install -y ffmpeg          # once, for mp3 conversion
   python code/read_channel.py
   ```

Edit the `PLAYLIST_ID` / `CHANNEL` / `SEARCH` config at the top of the script
just as you would locally. Downloaded files live in the Codespace; use the file
explorer to download them, or push non-ignored outputs to the repo.

### 4. Google Colab

Colab is handy for quick runs and for the future speech-to-text work (free GPU).
There is no repo checkout by default, so clone it inside a cell:

```python
# In a Colab cell:
!git clone https://github.com/dragosbo/learn-better.git
%cd learn-better
!pip install -r requirements.txt
!apt-get -qq install -y ffmpeg          # for mp3 conversion

# Edit the source in the file, or set it inline, then run:
!python code/read_transcript.py
```

Notes for Colab:
- The YouTube **bot-check** is more likely on cloud IPs. If you hit
  "Sign in to confirm you're not a bot", upload a `cookies.txt` (see the cookies
  note under *Running the tools*) and point `COOKIES_FILE` at it.
- Colab sessions are ephemeral: download anything in `audio/` / `transcripts/`
  before the runtime disconnects, or mount Google Drive to persist them.

---

## Running the tools

Activate your environment first (step 1), then run any of the scripts below.
Helper batch files are provided for convenience (run them from the repo root):

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

(or `python code\read_channel.py`). Output goes to `audio/` and
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

### Transcribe audio with Whisper (`w.bat`)

For clips whose YouTube captions are disabled (the ones the tools flag as
`NO TRANSCRIPT`), generate a transcript from the audio using
[`faster-whisper`](https://github.com/SYSTRAN/faster-whisper) — a fast,
CPU-friendly, no-API-key speech-to-text engine. `code/transcribe_audio.py` writes
to `generated_transcripts/<title> [<id>].whisper.<lang>.txt` (named from the audio
file), and **skips** any transcript already present.

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
- **`select_by = "all"`** — every audio file in `audio/` (slow).
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

Output goes to `generated_transcripts/` (git-ignored). Re-running skips clips that
already have a transcript.

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
   (`transcripts/*.en.txt`) and Whisper output
   (`generated_transcripts/*.whisper.en.txt`),
2. picks **one per video** (captions preferred; a Whisper transcript is used only
   when that video has no caption), deduplicating by the `[<id>]` video id so the
   same clip is never listed twice,
3. checks which already have a matching `summaries/<base>.summary.md`,
4. prints which are done vs. missing (tagging each `(caption)` or `(whisper)`), and
5. for the missing ones, prints a single ready-to-paste instruction whose paths
   point at the correct folder.

You copy that printed instruction into the Kiro chat, e.g.:

> Apply skill_summary.md to these transcripts and save each to
> summaries/<base>.summary.md:
> - transcripts/Some Video [abc123].en.txt
> - generated_transcripts/Another Video [def456].whisper.en.txt

Kiro reads each transcript and writes the summary following `skill_summary.md`.
Existing summaries are left alone, so re-running only surfaces new transcripts.
To regenerate one, delete its `summaries/*.summary.md` and run `s` again.

Typical flow for a new video: `t` or `w` (get a transcript, caption or Whisper) →
`s` (list what needs summarizing) → paste the instruction into Kiro.

Note: only English transcripts are summarized, and both a caption and a Whisper
transcript for the same video map to the same `summaries/<base>.summary.md`.
Summaries are saved to `summaries/` (this folder **is** tracked by git, unlike
`audio/`, `transcripts/`, and `generated_transcripts/`, since summaries are
authored content rather than regenerated downloads).

### Word cloud (`d.bat` / `wc.bat`)

Turn a transcript into a **word cloud**. This is split in two, matching the rest
of the repo: a Python script produces **data** (a `word_cloud.json`), and a small
HTML page renders it **client-side** with a JavaScript library. No `matplotlib`,
no plotting deps.

**1. Generate the data.** `code/make_wordcloud.py` reads a transcript (from
`transcripts/` or `generated_transcripts/`), strips timestamps, tokenizes
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
reads from `audio/`, re-encodes with **ffmpeg**, and writes to a separate
`audio_reencoded/` folder so the originals are never touched (re-encoding to a
lower bitrate is lossy and irreversible).

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
  `select`) | `all` (every audio file in `audio/`, slow).
- **`bitrate`** — the target audio bitrate: `"64k"`, `"96k"`, `"128k"` (or a
  plain number like `64000`). Lower = smaller file, lower quality. 96k is a good
  balance for speech.
- **`format`** / **`codec`** — output container/encoder. Defaults `mp3` /
  `libmp3lame` (free, universal). `m4a`/`aac`, `ogg`/`libvorbis`, `opus`/
  `libopus` also work.
- **`sample_rate`** (ffmpeg `-ar`) / **`channels`** (ffmpeg `-ac`, e.g. `1` =
  mono to shrink further) — optional; `null` keeps the source value.

Output files are named `audio_reencoded/<name>.<bitrate>.<ext>` (e.g.
`... .96kbps.mp3`), so different bitrates coexist. Re-running **skips** files
that already exist; delete one (or pick a new bitrate) to regenerate. The run
prints an `original -> new (saved %)` line per file. Output goes to
`audio_reencoded/` (git-ignored).

Verify a result played the way you expect, or check its bitrate with `ffprobe`
(ships with ffmpeg):

```cmd
ffprobe -v error -show_entries format=bit_rate -of default=noprint_wrappers=1 "audio_reencoded\<file>.96kbps.mp3"
```

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

## Whisper transcription quality (validation)

Before generalizing the speech-to-text step, we validated it on one clip.
`code/transcribe_audio.py` transcribes *Git and GitHub Tutorial for Beginners*
with `faster-whisper` (model `base`, CPU, `int8`) to
`generated_transcripts/...whisper.en.txt`. We then compared that output against
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
│   ├── youtube_download.py    # legacy pytube audio downloader
│   └── languages.json         # subtitle languages to fetch (en, fr, ro)
├── lib/                 # reusable helpers: net, textutil, paths, youtube
├── notebooks/           # yt_download.ipynb (reusable helpers + metadata)
├── .devcontainer/       # Codespaces / Dev Container (Python 3.12)
├── audio/               # downloaded audio (git-ignored)
├── audio_reencoded/     # re-encoded audio at a target bitrate (git-ignored)
├── transcripts/         # saved caption transcripts (git-ignored)
├── generated_transcripts/ # Whisper transcripts (git-ignored)
├── summaries/           # AI-generated summaries (tracked by git)
├── data/                # playlists.json + wordclouds/*.word_cloud.json (git-ignored)
├── config/              # run configs: config_transcribe*.json, config_wordcloud*.json, config_reencode.json
├── chats/               # AI chat logs: kiro_* and claude_* (prompts + conversation)
├── ignore/              # git-ignored: retired code + todo.md, mini_todo.md, notes
├── wordcloud.html       # renders a word_cloud.json (wordcloud2.js)
├── skill_summary.md     # reusable summary format/procedure
├── c.bat                # activate the learn-better conda env
├── r.bat                # activate env + run read_channel.py
├── t.bat                # activate env + run read_transcript.py
├── s.bat                # activate env + run make_summaries.py (prep summaries)
├── p.bat                # activate env + run list_playlists.py
├── w.bat                # activate env + run transcribe_audio.py (Whisper)
├── d.bat                # activate env + run make_wordcloud.py (one transcript)
├── wc.bat               # activate env + run make_wordcloud.py (config: batch/merge)
├── a.bat                # activate env + run reencode_audio.py (audio bitrate)
├── requirements.txt
├── plan.md              # roadmap and analysis
└── README.md
```

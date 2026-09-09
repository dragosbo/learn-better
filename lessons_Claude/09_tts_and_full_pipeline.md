# Lesson 09 — TTS and the Full Pipeline

**You'll build:** `code/generate_speech.py` (Piper TTS — converts text to speech), `code/reencode_audio.py`
(ffmpeg-based audio reencoding), `lib/net.py` (real network helpers replacing the stub), `lib/youtube.py`
(real YouTube helpers replacing the stub), and a `docs/how_to_test.md` covering the full end-to-end
run. You'll also do the first complete R→W→S→V pipeline run.
**Complexity:** ⭐⭐⭐⭐⭐   **Est. time:** ~120–150 min
**AI tasks in this lesson:** multi-module generation, subprocess integration, library documentation
reading, end-to-end debugging

---

## Prerequisites

- Lessons 05–08 completed: all scripts exist (some with stubs), runners all in place
- Piper TTS installed (`piper-tts>=1.2` from requirements.txt)
- ffmpeg installed in the conda env (from Lesson 03)
- At least one summary in `data/summaries/` (from Lesson 08) for the TTS test

---

## Re-orient the AI

> Paste this block at the start of a new session, or any time the assistant loses context:
>
> "I'm working on the **learn-better** repo — a Python tool that downloads YouTube audio and
> transcripts, transcribes locally with faster-whisper, and generates summaries and word clouds.
> We're on **Lesson 09 — TTS and the Full Pipeline**. All scripts exist; `lib/net.py` and
> `lib/youtube.py` currently have stubs with NotImplementedError. This lesson replaces those stubs
> with full implementations and adds `generate_speech.py` and `reencode_audio.py`.
> OS: Windows. Conda env: `learn-better`. Please continue from where I left off."

---

## Concepts

1. **Voice model files download on first use — not at install time.** Piper TTS downloads `.onnx`
   model files into `data/tts_output/.voices/` the first time you request a voice. This takes
   time and bandwidth. If you see a long pause or a download progress bar, that is expected.
   Subsequent runs use the cached files.

2. **Preference order for TTS source: summary > caption transcript > Whisper transcript.** The
   text-to-speech pipeline reads the best available text source for each video. A clean,
   AI-authored summary produces better TTS audio than a raw transcript that may have filler
   words, fragmented sentences, or timestamps.

3. **The full pipeline is: `r` → `w` → `s` (manual paste) → `v`.** Running these four steps end-to-end
   (download audio → transcribe → generate summary → synthesise speech) closes the loop on the
   entire project. End-to-end testing surfaces integration bugs that unit tests miss.

---

## Step-by-step

### 09.1 — Write the real `lib/net.py`

**Prompt:**
```
Replace the stub in lib/net.py with a full implementation. The module handles corporate network
configuration for the project.

Required contents:

COOKIES_FROM_BROWSER = None   # e.g. "chrome" or "firefox" — browser to extract cookies from
COOKIES_FILE = None           # auto-detect: if "code/cookies.txt" exists, use it

# Auto-detect cookies.txt
if os.path.isfile("code/cookies.txt"):
    COOKIES_FILE = "code/cookies.txt"

NO_PROXY = True    # strip HTTP_PROXY/HTTPS_PROXY env vars (corporate proxy workaround)
PROXY_URL = None   # set a specific proxy URL if needed

def apply_no_proxy_env():
    """
    Strips HTTP_PROXY, HTTPS_PROXY, http_proxy, https_proxy from os.environ.
    Must be called BEFORE importing faster_whisper or making any yt-dlp network calls.
    """
    for var in ["HTTP_PROXY", "HTTPS_PROXY", "http_proxy", "https_proxy"]:
        os.environ.pop(var, None)

The cookies detection should silently do nothing if the file is not found.
Add a module docstring explaining the purpose.
Output only the file content.
```

**Expected output:** A short, clean module with the two config blocks, auto-detection logic, and
`apply_no_proxy_env()`. Pure stdlib (only `os`).

**Verify:**
```cmd
python -c "from lib import net; net.apply_no_proxy_env(); print('net OK')"
```

---

### 09.2 — Write the real `lib/youtube.py`

This is the largest module in the project. Generate it in two sub-steps.

**Prompt (part 1 — read the design):**
```
I need to write lib/youtube.py — the YouTube helper module used by all the project's download
scripts. Before writing code, explain the design for each function I need:

build_url(playlist_id, channel, search, limit) -> (label, url)
  - If playlist_id is non-empty: return ("playlist:<id>", yt-dlp URL for that playlist)
  - If channel is non-empty: return ("channel:<handle>", yt-dlp URL for that channel)
  - If search is non-empty: return ("search:<query>", yt-dlp ytsearch URL)
  - Otherwise: raise ValueError

list_videos(url, limit) -> list[(vid_id, title)]
  - Use yt-dlp in flat-playlist mode (--flat-playlist) to list videos without downloading
  - Return up to `limit` entries as (video_id, title) tuples
  - Apply lib.textutil.safe_filename to each title

list_playlists(channel) -> list[dict]
  - Use yt-dlp to list all playlists for a channel
  - Return a list of {"id": ..., "title": ..., "url": ...} dicts

fetch_playlist_videos(playlist_id, limit) -> list[(vid_id, title)]
  - Same as list_videos but for a specific playlist ID

download_transcript(vid_id, title, languages, output_dir) -> str | None
  - Use youtube_transcript_api to download captions
  - Try each language in `languages` in order; use first that succeeds
  - Save to output_dir/<safe_title>.<lang>.txt
  - Strip VTT formatting via textutil.clean_text before saving
  - Return the output path, or None if no captions found

download_audio(vid_id, output_dir, audio_format, audio_quality) -> str | None
  - Use yt-dlp to download audio only, converting to audio_format at audio_quality kbps
  - Pass cookies from lib.net (COOKIES_FROM_BROWSER and/or COOKIES_FILE) if set
  - Output filename: output_dir/<safe_title>.<audio_format>
  - Return the output path, or None on failure

For each function: describe the yt-dlp or library call pattern, and what the return value
should look like. Do not write code yet.
```

**Expected output:** A clear design spec for all six functions. Confirm the design before proceeding.

---

**Prompt (part 2 — write the module):**
```
Now write lib/youtube.py based on the design above. Exact requirements:

Imports:
  import os, json
  from lib import net, textutil
  from lib.paths import DATA_DIR

For list_videos and list_playlists: use yt-dlp Python API (yt_dlp.YoutubeDL) with options:
  quiet=True, no_warnings=True, extract_flat=True (for listing), noplaylist=False

For download_transcript: use youtube_transcript_api.YouTubeTranscriptApi
  - fetch(vid_id, languages=languages)
  - Format: join all snippet["text"] values with a space, then textutil.clean_text()
  - File suffix: .<lang>.txt (e.g. .en.txt)

For download_audio: use yt-dlp Python API with:
  format="bestaudio/best"
  postprocessors=[{"key":"FFmpegExtractAudio","preferredcodec":audio_format,"preferredquality":audio_quality}]
  If net.COOKIES_FROM_BROWSER is set: add "cookiesfrombrowser": (net.COOKIES_FROM_BROWSER,)
  If net.COOKIES_FILE is set: add "cookiefile": net.COOKIES_FILE
  outtmpl: os.path.join(output_dir, "%(title)s.%(ext)s")

All file output names must pass through textutil.safe_filename().
Add a module docstring.
Output only the file content.
```

**Expected output:** The full `lib/youtube.py`. It should be the longest module in the project
(~80–120 lines). Check imports: `from lib import net, textutil` (not separate imports).

**Verify:**
```cmd
python -c "from lib import youtube; print('youtube OK')"
```

---

### 09.3 — Generate `code/reencode_audio.py`

**Prompt:**
```
Write code/reencode_audio.py with these exact requirements:

Purpose: re-encodes audio files using ffmpeg (via subprocess). Useful for reducing file size
or converting format before TTS or storage.

Config block at the top:
  SELECT_BY = "all"    # "name" | "id" | "all"
  SELECT = ""          # value for name/id modes
  BITRATE = "64k"
  FORMAT = "mp3"
  CODEC = "libmp3lame"
  SAMPLE_RATE = 22050
  CHANNELS = 1

JSON config file support (same pattern as transcribe_audio.py):
  DEFAULT_CONFIG = "config/config_reencode.json"
  If sys.argv[1] is provided, use that path instead.
  Keys: select_by, select, bitrate, format, codec, sample_rate, channels

Imports:
  import os, json, sys, subprocess, glob
  from lib.paths import AUDIO_DIR, AUDIO_REENCODED_DIR

Logic:
  1. Select source files from AUDIO_DIR based on SELECT_BY / SELECT
  2. For each file: build the output path in AUDIO_REENCODED_DIR as
     <base>.<bitrate>.<format>  (e.g. "Title.64k.mp3")
  3. Skip if output file already exists
  4. Call ffmpeg via subprocess.run with the appropriate flags:
     ffmpeg -i <input> -b:a <bitrate> -ar <sample_rate> -ac <channels>
            -acodec <codec> -y <output>
  5. Print each conversion: input → output
  6. Print a summary: N files reencoded

Output only the file content.
```

**Expected output:** A clean config-driven script using only stdlib + subprocess. No pydub, no
soundfile — just ffmpeg called via subprocess.

**Verify:**
```cmd
python code\reencode_audio.py
```
Check that a file appears in `data/audio_reencoded/` with the bitrate in its name.

---

### 09.4 — Generate `code/generate_speech.py`

**Prompt:**
```
Write code/generate_speech.py with these exact requirements:

Purpose: converts text sources (summaries, transcripts) to speech using Piper TTS.

Config block at the top:
  SELECT_BY = "all"     # "name" | "id" | "all"
  SELECT = ""           # value for name/id modes
  VOICE = "en_US-ryan-medium"   # Piper voice model name
  OUTPUT_FORMAT = "wav"  # "wav" or "mp3"

JSON config file support:
  DEFAULT_CONFIG = "config/config_tts.json"
  If sys.argv[1] is provided, use that path instead.
  Keys: select_by, select, voice, output_format

Imports:
  import os, json, sys, subprocess, glob
  from lib import textutil
  from lib.paths import SUMMARY_DIR, TRANSCRIPT_DIR, GENERATED_TRANSCRIPT_DIR, TTS_OUTPUT_DIR

Text source priority (for each base name):
  1. Check SUMMARY_DIR for <base>.summary.md — if exists, use it
  2. Else check TRANSCRIPT_DIR for <base>.en.txt — if exists, use it
  3. Else check GENERATED_TRANSCRIPT_DIR for <base>.whisper.en.txt — use it
  4. If none found: skip

Voice model directory: TTS_OUTPUT_DIR / ".voices"
  Piper downloads .onnx model files there on first use.

TTS call: use the piper Python API (piper.PiperVoice.load()) or subprocess call to piper binary.
  Output file: TTS_OUTPUT_DIR/<base>.<voice>.<output_format>
  Skip if output file already exists.

If OUTPUT_FORMAT is "mp3": convert with ffmpeg after generating the wav
  (piper always outputs wav; mp3 conversion is a post-processing step via subprocess)

Output only the file content.
```

**Expected output:** A script with text source priority logic, Piper API call, and optional ffmpeg
conversion for mp3.

**Verify:** Run with a summary file present:
```cmd
python code\generate_speech.py
```
A `.wav` (or `.mp3`) file should appear in `data/tts_output/`.

---

### 09.5 — Create TTS config files

**Prompt:**
```
Write two TTS config files:

1. config/config_tts.json — default:
   {"select_by": "all", "select": "", "voice": "en_US-ryan-medium", "output_format": "wav"}

2. config/config_tts.speed09.json — same but with output_format "mp3" and a note in the filename
   that this is the 0.9 speed variant (if piper supports speed via config, add "speed": 0.9;
   otherwise just change output_format to "mp3"):
   {"select_by": "all", "select": "", "voice": "en_US-ryan-medium", "output_format": "mp3"}

Output each with its filename as a header.
```

---

### 09.6 — Run the full pipeline end-to-end

This is the milestone step for the whole project. Run the complete pipeline on a fresh video.

```cmd
init
r            (download audio for a test video)
w            (transcribe with Whisper)
s            (make_summaries.py — prints paste-ready prompt)
```
Paste the output from `s` into your AI assistant and save the returned summary to
`data/summaries/<base>.summary.md`.

```cmd
v            (generate speech from the summary)
```

**Verify:**
- `data/audio/` has an `.mp3` file
- `data/generated_transcripts/` has a `.whisper.en.txt` file
- `data/summaries/` has a `.summary.md` file
- `data/tts_output/` has a `.wav` (or `.mp3`) file

If any step fails, use the debugging cycle from Lesson 04: copy the full traceback and paste it
into the assistant.

---

### 09.7 — Write `docs/how_to_test.md`

**Prompt:**
```
Write docs/how_to_test.md — a testing guide for the learn-better project. It should cover:

1. The full pipeline smoke test (end-to-end: r → w → s → v for one video)
2. How to verify each output type (audio, transcript, summary, TTS, word cloud)
3. How to use compare_transcripts.py to assess Whisper quality
4. Common failure modes and first diagnostic steps for each script
5. How to re-run a single step without re-running the full pipeline

Keep it concise and practical — this is a developer reference, not a tutorial.
Output only the file content.
```

**Verify:** Save as `docs/how_to_test.md`. Skim it for accuracy against what you built in lessons
04–09.

---

### 09.8 — Commit

**Prompt:**
```
Give me git commands to add and commit all new and modified files from this lesson:
  lib/net.py          (replaced stub)
  lib/youtube.py      (replaced stub)
  code/generate_speech.py
  code/reencode_audio.py
  config/config_tts.json
  config/config_tts.speed09.json
  config/config_reencode.json
  docs/how_to_test.md

Commit message: "add generate_speech, reencode_audio, real net/youtube libs, test guide"
OS: Windows, Command Prompt.
```

**Verify:** `git log --oneline` should show eight commits.

---

## When the AI misbehaves

**`lib/youtube.py` uses `subprocess` to call `yt-dlp` as a shell command instead of the Python API.**
Shell commands break on different OS configurations and don't respect the project's cookie/proxy
settings in `lib/net.py`. Push back: "Can you use the yt-dlp Python API (`yt_dlp.YoutubeDL`)
instead of `subprocess`? I need to pass options like `cookiefile` and `cookiesfrombrowser`."

**`generate_speech.py` crashes because piper can't find the voice model.**
On first run, Piper downloads the model. If the download fails (corporate proxy, slow connection),
the `.onnx` file won't be in `.voices/`. Ask: "Piper can't find the voice model. Where does it
look by default, and how can I pre-download the model file and point Piper to it?" You can
manually download from the Piper GitHub releases page.

**`reencode_audio.py` fails with `ffmpeg not found`.**
ffmpeg must be on PATH (installed via conda-forge in Lesson 03). If the conda env is not active,
ffmpeg won't be found. Check: `conda activate learn-better`, then `ffmpeg -version`. If still not
found, run `conda install -c conda-forge ffmpeg -y` again.

**`download_transcript` in `lib/youtube.py` raises `TranscriptsDisabled` or `NoTranscriptFound`.**
Not all videos have captions. This is expected — `download_transcript` should catch this exception
and return `None` gracefully, with a print message saying the transcript was not available.
Ask: "Can you wrap the `fetch()` call in a try/except that catches `TranscriptsDisabled` and
`NoTranscriptFound` from youtube_transcript_api and returns `None` instead of raising?"

---

## What you have now

Files added this lesson:

```
learn-better/
    code/
        generate_speech.py    (new)
        reencode_audio.py     (new)
    lib/
        net.py                (replaced stub with full implementation)
        youtube.py            (replaced stub with full implementation)
    config/
        config_tts.json       (new)
        config_tts.speed09.json  (new)
        config_reencode.json  (new)
    docs/
        how_to_test.md        (new)
    data/
        tts_output/           (generated — git-ignored)
        audio_reencoded/      (generated — git-ignored)
```

Repo state: all scripts complete with real implementations. The full R→W→S→V pipeline runs
end-to-end. Eight commits on `main`.

---

## Next →

[Lesson 10 — Deployment and Handoff](10_deployment_and_handoff.md)

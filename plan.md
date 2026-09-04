# learn-better — Plan

Minimalist, free learning tools that turn YouTube content into study material:
audio, transcripts, and metadata, feeding downstream steps like summarization
and mind-maps.

This document analyzes the original `todo.md` (now archived in `ignore/`), records
the fixes already applied, and proposes a concrete roadmap. plan.md is now the
single source of truth for what remains to be done.

---

## 1. Where the project stands today

| Area | State | Notes |
|------|-------|-------|
| `code/read_channel.py` | **working** | No-API-key workflow (`yt-dlp`): lists a playlist/channel/search, saves audio + transcripts, skips already-downloaded files, caps at `LIMIT`. Recommended entry point. (Logic now lives in `lib/`.) |
| `code/read_transcript.py` | **working** | No-API-key transcript-only tool, one file per language. Thin wrapper over `lib/`. |
| `code/list_playlists.py` | **working** | No-API-key: lists a channel's public playlists + each playlist's videos → `data/playlists.json` (`p.bat`). |
| `lib/` package | **working** | Reusable helpers: `net`, `textutil`, `paths`, `youtube`. All entry scripts are thin config + `main()` wrappers; no duplicated logic. |
| `code/transcribe_audio.py` | **working** | Whisper speech-to-text (`faster-whisper`): transcribe audio to `data/generated_transcripts/`, translate to English, select by name/id/all/source, JSON-config driven (`w`). |
| `code/make_summaries.py` | **working** | Prep step for summaries: scans caption + Whisper transcripts (captions preferred), one per video, prints a paste-ready Kiro instruction (`s.bat`). |
| `code/compare_transcripts.py` | **working** | Quality check: Whisper output vs. YouTube captions (~95% word accuracy on the sample). |
| `code/youtube_download.py` | working (fragile) | Simple `pytube` audio downloader (search / playlist / single video). |
| `get_my_playlists.py` | **retired** | Old YouTube Data API + `scrapetube` script. Depended on an API key and the broken `scrapetube`; superseded by the no-key `yt-dlp` tools. Moved to the git-ignored `ignore/` folder rather than deleted. |
| `notebooks/yt_download.ipynb` | working | Cleaner refactor with `vl` / `y2a` / `vm` helpers and metadata DataFrame. |
| `.devcontainer/` | fixed | Codespaces-ready; Python versions were mismatched (now aligned to 3.12). |
| `requirements.txt` | fixed | Typo fixed; pinned; added `yt-dlp`, `ipykernel`, `faster-whisper`; documented `ffmpeg` as a system dep. |
| `code/make_wordcloud.py` | **working** | Transcript → `data/wordclouds/*.word_cloud.json` (data only); batch + merge + single-language guard; JSON-config driven (`d.bat` / `wc.bat`). Rendered by `wordcloud.html` (wordcloud2.js). |
| `code/reencode_audio.py` | **working** | Re-encode `data/audio/` → `data/audio_reencoded/*.<bitrate>.<ext>` via ffmpeg (free; no new deps); name/id/all selection, skip-if-exists, failed-run handling; JSON-config driven (`a`). Item 4. |
| `code/generate_speech.py` | **working** | Text → speech via Piper (free, MIT, CPU-only): voice a summary/transcript to `data/tts_output/*.wav`; selectable voice + speed (`length_scale`), name/id/all selection, skip-if-exists; JSON-config driven (`v`). Item 3 (baseline). |
| Remaining (item 6 extras) | partial / optional | Baseline TTS done; higher-quality/cloning voices deferred. `data/` consolidation DONE (todo3); a self-contained summarization notebook still open. |

### Fixes already applied
- **`requirements.txt`**: corrected `youtoube-transcript-api` → `youtube-transcript-api`,
  pinned versions, added `yt-dlp` (robust alternative to the fragile `pytube`),
  added `ipykernel` (so the notebooks run in this env), and documented `ffmpeg`
  as a required **system** dependency (not pip-installable).
- **Devcontainer**: aligned `devcontainer.json` (`3.8-bullseye`) and `Dockerfile`
  (`3.10-bullseye`) to a single supported version (`3.12-bullseye`); replaced the
  removed `python.linting.*` / `python.formatting.*` settings with the current
  black-formatter setup; added the Jupyter extension; fixed `postCreateCommand`.
- **Bug fixes**: invalid short URLs (`https://youtu.be/v=<id>` → `https://youtu.be/<id>`)
  in the script and the notebook; auto-create the `timestamped/` output folder in
  `get_my_playlists.py`.
- Added `code/secrets.example.json` to document the required `YOUTUBE_API_KEY` shape.
- **New no-API-key tool** `code/read_channel.py`: reads a playlist/channel/search
  with `yt-dlp`, saves each clip's audio to `data/audio/` and transcript to
  `data/transcripts/`, skips files already present, signals clips with no transcript,
  and processes up to `LIMIT` (default 5) clips. Handles the YouTube bot-check via
  cookies and bypasses corporate proxies.
- Added `c.bat` (activate env) and `r.bat` (activate + run the tool) helpers.
- Minimalist `.gitignore`; `data/` (audio, transcripts, generated_transcripts, etc.)
  are git-ignored (except `data/summaries/`, tracked via a `.gitignore` negation).
- **Playlists tool** `code/list_playlists.py` (`p.bat`): lists a channel's public
  playlists and each playlist's videos to `data/playlists.json`, no API key.
- **Reusable `lib/` package**: extracted the proven download/transcript logic into
  `lib/net`, `lib/textutil`, `lib/paths`, `lib/youtube`; all entry scripts are now
  thin config + `main()` wrappers with no duplicated helpers (behavior preserved).
- **Whisper speech-to-text** `code/transcribe_audio.py` (`w.bat`), using
  `faster-whisper`:
  - Writes to `data/generated_transcripts/<title> [<id>].whisper.<lang>.txt` (named
    from the audio file), with skip-if-exists.
  - **File selection**: `SELECT_BY = name | id | all | source`. `source` takes a
    playlist/channel/search and transcribes only clips with no YouTube caption
    (captions-first, Whisper fills the gaps; audio reused/downloaded; lazy model).
  - **Translation**: `task="translate"` → English (Whisper's only target);
    `task="transcribe"` + pinned `language` → same-language transcript.
  - **JSON configs** in the `config/` folder (`config/config_transcribe*.json`) +
    optional CLI-arg config path.
  - Quality validated by `code/compare_transcripts.py`: ~95% word accuracy vs.
    YouTube captions on the sample (documented in README + youtube.html).
- **Summaries prep** `code/make_summaries.py` (`s.bat`) now feeds from BOTH
  caption transcripts and Whisper transcripts (captions preferred, one summary per
  video, deduped by video id, UTF-8-safe output).
- Added `t.bat`, `s.bat`, `p.bat`, `w.bat` helper runners.
- **yt-dlp warning cleanup**: `no_warnings` on the transcript/audio calls; README +
  youtube.html recommend installing Deno as the proper JS-runtime fix.

### Known issue
- **`scrapetube` listing is broken** (confirmed returning 0 videos; last release
  Sep 2025). `yt-dlp` is the working replacement and is used by all active tools.
  The only script that still depended on `scrapetube` (`get_my_playlists.py`) has
  been **retired to `ignore/`**, so this no longer affects the active workflow.

---

## 2. Analysis of the original `todo.md` (archived in `ignore/`)

The TODO mixes three kinds of work. Grouping them clarifies sequencing.

### A. New notebooks (the core ask)
1. speech to text
2. speech to translated text
3. text to speech
4. audio to audio at a different bit rate
5. text summarization
6. text to speech with special voices
7. create word cloud

These form a natural **audio → text → knowledge** pipeline. Several share the same
building blocks (an ASR model, an audio I/O layer), so they should not be built in
isolation.

### B. Content / documentation tasks
- Record a video: "from a video to a mindmap".
- Document the prompt-building logic.
- Learn/document GitHub Codespaces (the devcontainer is the practical start).

### C. Housekeeping notes
- Scattered local paths (`C:\...\youtube`, `streamlit`, `YouTubeChapterGenerator`)
  — these are pointers to other work, not tasks in this repo.

### Observations
- **The download + transcript foundation now exists.** `read_channel.py`
  already downloads audio and saves transcripts (with skip-if-exists and a clip
  cap) without an API key. This is the base the ASR/summarization work can build on.
- **Model choices unstated.** `openai-whisper` (or faster `faster-whisper`) covers
  transcription *and* translation, which collapses items 1 and 2 into one tool.
  (Note: YouTube already provides transcripts for many clips, so Whisper is mainly
  needed for clips whose subtitles are disabled or for translation.)
- **Output layout is consolidated under `data/`.** Audio → `data/audio/`, transcripts → `data/transcripts/`
  (both git-ignored). Summaries live under `data/summaries/` (tracked); all
  outputs now share the single `data/` root.
- **`scrapetube` is broken, `yt-dlp` is the default.** Confirmed via testing; all
  new listing/downloading should use `yt-dlp`.

---

## 3. Proposed roadmap

### Phase 0 — Foundation (enables everything else)
- [x] Working no-API-key downloader + transcript fetcher (`read_channel.py`),
      with skip-if-exists and a clip cap.
- [x] Output folders in use, now under `data/`: `data/audio/`, `data/transcripts/` (git-ignored).
- [x] Retired the API-key/`scrapetube` script (`get_my_playlists.py`) to
      `ignore/` instead of migrating it; the no-key `yt-dlp` tools supersede it.
- [x] Refactored the working logic from `read_channel.py` into a reusable `lib/`
      package (`lib/net`, `lib/textutil`, `lib/paths`, `lib/youtube`); the entry
      scripts are now thin config + `main()` wrappers. (Phase B of mini_todo.)
- [x] Playlists tool `list_playlists.py` → `data/playlists.json` (Phase A of
      mini_todo).
- [x] Decided models: `faster-whisper` for STT + translation (added to
      `requirements.txt`). `edge-tts` (free) still the plan for TTS.
- [x] New deps added lean, per phase: `faster-whisper` added when STT started.
- [x] Consolidate outputs under a single `data/` root (done in `todo3.md`)
      (`data/audio/`, `data/transcripts/`, `data/summaries/`).

### Phase 1 — Audio → Text (`todo` items 1, 2, 4)
> Delivered as **scripts** (not notebooks) in Phase C of mini_todo:
> `code/transcribe_audio.py` (`w.bat`) + `lib/`. Notebooks remain optional.
- [x] **Speech to text** — `transcribe_audio.py` runs `faster-whisper` over
      downloaded audio → `data/generated_transcripts/*.whisper.<lang>.txt`, with
      skip-if-exists and name/id/all/source selection. Quality ~95% vs. captions
      (`compare_transcripts.py`).
- [x] **Speech → translated text** (item 2) — `task="translate"` (English only,
      Whisper's fixed target); `task="transcribe"` + pinned `language` gives a
      same-language transcript.
- [x] **Captions-first source flow** — for a playlist/channel/search, use the
      YouTube caption when present and only Whisper the caption-less clips.
- [x] `audio_bitrate` — re-encode audio at a target bitrate via `ffmpeg`
      (item 4). `reencode_audio.py` (`a`) reads `data/audio/`, re-encodes with
      ffmpeg (free, already required — no new deps), and writes to a separate
      `data/audio_reencoded/*.<bitrate>.<ext>` (originals untouched). name/id/all
      selection, skip-if-exists, JSON-config (`config/config_reencode.json`).

### Phase 2 — Text → Knowledge (`todo` items 5, 7)
- [~] **Summarization** (item 5) — `make_summaries.py` (`s.bat`) does the
      deterministic prep: it finds caption + Whisper transcripts (captions
      preferred), reports which lack a summary, and prints a paste-ready
      instruction; Kiro then applies `skill_summary.md` and writes
      `data/summaries/*.summary.md`. A fully self-contained notebook (local HF model /
      API prompt) is still open.
- [x] **Word cloud** (item 7) — done as scripts + JS, NOT matplotlib.
      `make_wordcloud.py` (`d.bat` one file, `wc.bat` batch/merge via a
      `config/config_wordcloud*.json`) tokenizes a transcript, drops stopwords
      (built-in en/fr/ro), and writes `data/wordclouds/<base>.word_cloud.json`.
      `wordcloud.html` renders it client-side with wordcloud2.js. Extras: a
      single-language guard, and a merge mode (combine several transcripts into
      one cloud, e.g. `git-series`). The JSON is renderer-agnostic (d3-cloud /
      ECharts could be swapped in).

### Phase 3 — Text → Speech (`todo` items 3, 6)
> Delivered as a **script** (not a notebook), matching the rest of the repo:
> `code/generate_speech.py` (`v.bat`). Piper chosen over edge-tts as the baseline
> — fully local, MIT, CPU-only, no cloud/ToS caveats (see the archived `tts.md`
> research and `todo2.md` for the decision).
- [x] **Baseline TTS** (item 3) — `generate_speech.py` voices a summary /
      caption / Whisper transcript to `data/tts_output/<base>.<voice>[.s<scale>].wav`
      via Piper (free, CPU-only, no GPU/API). name/id/all selection (dedupe
      preferring summary > caption > whisper), skip-if-exists, JSON-config
      (`config/config_tts.json`). Voice model auto-downloads on first use.
- [~] **Special / custom voices** (item 6) — partial: the **voice** and speaking
      **speed** (`length_scale`: 0.9/1.0/1.15) are selectable now (any free Piper
      voice, incl. `fr_FR-*`/`ro_RO-*`). A higher-quality engine (Kokoro) and
      voice **cloning** (XTTS/Chatterbox) remain deferred (todo2 Phase D4).

### Phase 4 — Knowledge consolidation & docs (`todo` section B)
- [ ] "Video → mindmap" walkthrough (Markdown; link the recorded video when ready).
- [ ] Prompt-building doc capturing the author's logic, referenced from the
      summarization notebook.
- [x] Codespaces / remote-run doc: covered by the "How to run it" section in the
      README (local, Dev Container, GitHub Codespaces, Google Colab). The old
      `learning_codspaces.txt` notes are archived in `ignore/`.

### Phase 5 — Polish (optional)
- [x] Migrate downloads from `pytube`/`scrapetube` to `yt-dlp` for reliability.
      Done across the board: the active tools use yt-dlp; the `scrapetube`-based
      `get_my_playlists.py` was retired to `ignore/`; and `notebooks/yt_download.ipynb`
      is now rewritten on `lib/` + yt-dlp (`vl`/`y2a`/`vm` helpers, no `pytube`).
      The only remaining `pytube` user is the legacy `code/youtube_download.py`;
      `pytube` can be dropped from `requirements.txt` if/when that script is retired.
- [ ] Optional Streamlit front-end (the author already explores Streamlit elsewhere).
- [ ] Light CI: lint + "notebooks execute" smoke test.

### Phase 6 — Deployment & packaging (reproducible setup anywhere)
> Distinct from Phase 4's "how to run it" quick-start: this is a full,
> comparison-driven guide to reproducibly standing up the environment on any
> target (local, container, or cloud), plus the container/image scripts to do it.
> Detailed research + copy-paste scripts live in `how_to_deploy.md` (repo root).
- [x] **Deployment matrix documented** — `how_to_deploy.md` ranks 12 platforms by
      complexity vs. capabilities: local (conda / pip+venv / uv), containers
      (VS Code & Kiro dev containers, Docker, Podman), and cloud (Colab,
      Codespaces, Gitpod; Replit/Binder noted as not-recommended). Includes
      ready-to-use `Dockerfile.standalone`, a patched `.devcontainer/Dockerfile`,
      `colab_setup.py`, `setup_codespaces.sh`, and `podman_setup.sh`.
- [x] **Fix the devcontainer ffmpeg gap** — applied: `.devcontainer/Dockerfile`
      now installs `ffmpeg` via an `apt-get install --no-install-recommends
      ffmpeg` layer (was missing — the #1 setup-failure cause per
      `how_to_deploy.md`). Also done: removed the unused `azure-cli` feature from
      `devcontainer.json` and added a `~/.cache` model-cache volume (faster-whisper
      + Piper weights survive rebuilds).
- [x] **Add the standalone container assets to the repo** — added
      `Dockerfile.standalone` (slim Python base, ffmpeg, non-root user) and a
      `.dockerignore` (keeps the build context lean, mirrors the git-ignored
      outputs) so Docker/Podman/CI users get a lighter, IDE-free image.
- [x] **Link `how_to_deploy.md` from README / youtube.html** — linked from both,
      next to the "How to run it" quick-start, so the deployment guide is
      discoverable.
- [x] **`.bat` helpers vs. Linux** — added matching `.sh` runners for all ten
      helpers (`c/r/t/p/s/d/w/wc/a/v`) so the tools work inside the Linux
      containers/cloud shells. They activate conda if present, else use the
      current `python` (Docker/Codespaces style). `.gitattributes` forces `*.sh`
      to LF (a CRLF shebang breaks on Linux) and keeps `*.bat` CRLF. Documented
      in README + how_to_test.md.

---

## 4. Repository layout

Current layout (see README.md for the annotated version):

```
learn-better/
├── code/                # scripts (read_channel, read_transcript, list_playlists,
│                        #          transcribe_audio, compare_transcripts, make_summaries)
├── lib/                 # shared helpers: net, textutil, paths, youtube
├── config/              # Whisper run configs: config_transcribe*.json
├── notebooks/           # yt_download.ipynb (future: one per capability)
├── data/                # ALL generated outputs (git-ignored, except summaries/)
│   ├── audio/               # downloaded audio (git-ignored)
│   ├── audio_reencoded/     # re-encoded audio (git-ignored)
│   ├── transcripts/         # caption transcripts (git-ignored)
│   ├── generated_transcripts/ # Whisper transcripts (git-ignored)
│   ├── tts_output/          # Piper TTS audio + .voices/ (git-ignored)
│   ├── summaries/           # AI-generated summaries (TRACKED via .gitignore negation)
│   ├── wordclouds/          # *.word_cloud.json (git-ignored)
│   └── playlists.json       # channel playlists (git-ignored)
├── scripts/             # one-letter runners c/r/t/s/p/w/d/wc/a/v (.bat + .sh; add to PATH)
├── init.bat             # adds scripts/ to PATH for the current cmd session
├── requirements.txt
└── plan.md
```

Still open (roadmap): a `docs/` folder for mindmap / prompt-building notes. The
git-ignored outputs are now **consolidated under `data/`** (done in `todo3.md`),
and the one-letter runners live in `scripts/` (add to PATH via `init.bat`).

---

## 5. Recommended next step

Phases 0–1 and the summarization prep are now delivered (as scripts): playlists,
the reusable `lib/`, Whisper STT + translation with a captions-first source flow,
and a summaries hook that reads both caption and Whisper transcripts. (The
detailed, per-subtask build log for this work lived in `mini_todo.md`, now
archived in `ignore/`.)

The next high-value moves, in order:

1. **TTS voice extras** (`todo` item 6, optional) — a higher-quality engine
   (Kokoro) and/or voice cloning (XTTS/Chatterbox). The baseline (Piper, with
   selectable voice + speed) is done; these are deferred niceties (todo2 D4).
2. **Self-contained summarization notebook** (local HF model / API prompt) if you
   want summaries without the manual Kiro paste step. (Output consolidation under
   a single `data/` root is DONE — see `todo3.md`.)
3. **Docs / consolidation** — the "video → mindmap" walkthrough and the
   prompt-building doc (Phase 4).

(The **devcontainer ffmpeg gap** flagged in `how_to_deploy.md` is now fixed —
`.devcontainer/Dockerfile` installs `ffmpeg` — so Dev Containers / Codespaces
handle audio/mp3 out of the box.)

(**Word cloud** (item 7), the **audio-bitrate helper** (item 4), and the **TTS
baseline** (item 3) are now done. Word cloud: a data-only Python script writes
`word_cloud.json`, rendered by `wordcloud.html` (wordcloud2.js), no matplotlib.
Audio bitrate: `reencode_audio.py` (`a`) re-encodes with ffmpeg into
`data/audio_reencoded/`. TTS: `generate_speech.py` (`v`) voices text with Piper
into `data/tts_output/` — all free, no new heavy deps.)

(The old `scrapetube`/API-key script `get_my_playlists.py` has been retired to
`ignore/`, so no migration of it is needed; the no-key `yt-dlp` tools cover its
use case.)

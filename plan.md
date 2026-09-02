# learn-better — Plan

Minimalist, free learning tools that turn YouTube content into study material:
audio, transcripts, and metadata, feeding downstream steps like summarization,
mind-maps, and Obsidian-based knowledge consolidation.

This document analyzes the current `todo.md`, records the fixes already applied,
and proposes a concrete roadmap.

---

## 1. Where the project stands today

| Area | State | Notes |
|------|-------|-------|
| `code/test_read_channel.py` | **working** | No-API-key workflow (`yt-dlp` + `youtube-transcript-api`): lists a playlist/channel/search, saves audio + transcripts, skips already-downloaded files, caps at `LIMIT`. Recommended entry point. |
| `code/youtube_download.py` | working (fragile) | Simple `pytube` audio downloader (search / playlist / single video). |
| `get_my_playlists.py` | **retired** | Old YouTube Data API + `scrapetube` script. Depended on an API key and the broken `scrapetube`; superseded by the no-key `yt-dlp` tools. Moved to the git-ignored `ignore/` folder rather than deleted. |
| `notebooks/yt_download.ipynb` | working | Cleaner refactor with `vl` / `y2a` / `vm` helpers and metadata DataFrame. |
| `.devcontainer/` | fixed | Codespaces-ready; Python versions were mismatched (now aligned to 3.12). |
| `requirements.txt` | fixed | Typo fixed; pinned; added `yt-dlp`, `ipykernel`; documented `ffmpeg` as a system dep. |
| Downstream notebooks (STT, TTS, summarization, word cloud) | not started | The bulk of `todo.md`. |

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
- **New no-API-key tool** `code/test_read_channel.py`: reads a playlist/channel/search
  with `yt-dlp`, saves each clip's audio to `audio/` and transcript to
  `transcripts/`, skips files already present, signals clips with no transcript,
  and processes up to `LIMIT` (default 5) clips. Handles the YouTube bot-check via
  cookies and bypasses corporate proxies.
- Added `c.bat` (activate env) and `r.bat` (activate + run the tool) helpers.
- Minimalist `.gitignore`; `audio/` and `transcripts/` are git-ignored.

### Known issue
- **`scrapetube` listing is broken** (confirmed returning 0 videos; last release
  Sep 2025). `yt-dlp` is the working replacement and is used by all active tools.
  The only script that still depended on `scrapetube` (`get_my_playlists.py`) has
  been **retired to `ignore/`**, so this no longer affects the active workflow.

---

## 2. Analysis of `todo.md`

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
- Document using Obsidian with the mindmap to consolidate knowledge.
- Document the prompt-building logic.
- Learn/document GitHub Codespaces (the devcontainer is the practical start).

### C. Housekeeping notes
- Concern about notebook refactoring ergonomics (script vs. notebook).
- Scattered local paths (`C:\...\youtube`, `streamlit`, `YouTubeChapterGenerator`)
  — these are pointers to other work, not tasks in this repo.

### Observations
- **The download + transcript foundation now exists.** `test_read_channel.py`
  already downloads audio and saves transcripts (with skip-if-exists and a clip
  cap) without an API key. This is the base the ASR/summarization work can build on.
- **Model choices unstated.** `openai-whisper` (or faster `faster-whisper`) covers
  transcription *and* translation, which collapses items 1 and 2 into one tool.
  (Note: YouTube already provides transcripts for many clips, so Whisper is mainly
  needed for clips whose subtitles are disabled or for translation.)
- **Output layout is stabilizing.** Audio → `audio/`, transcripts → `transcripts/`
  (both git-ignored). Summaries still need a home; a single `data/` root would tidy this.
- **`scrapetube` is broken, `yt-dlp` is the default.** Confirmed via testing; all
  new listing/downloading should use `yt-dlp`.

---

## 3. Proposed roadmap

### Phase 0 — Foundation (enables everything else)
- [x] Working no-API-key downloader + transcript fetcher (`test_read_channel.py`),
      with skip-if-exists and a clip cap.
- [x] Output folders in use: `audio/`, `transcripts/` (git-ignored).
- [x] Retired the API-key/`scrapetube` script (`get_my_playlists.py`) to
      `ignore/` instead of migrating it; the no-key `yt-dlp` tools supersede it.
- [ ] Refactor the working logic from `test_read_channel.py` into a small reusable
      `lib/` module: `download_audio()`, `get_transcript()`, later `transcribe()`,
      `translate()`, `synthesize()` — so notebooks stay short.
- [ ] Optionally consolidate outputs under a single `data/` root
      (`data/audio/`, `data/transcripts/`, `data/summaries/`).
- [ ] Decide models: `faster-whisper` for STT+translation, `edge-tts` (free) for TTS.
- [ ] Add new deps to `requirements.txt` as each phase starts, to keep installs lean.

### Phase 1 — Audio → Text (`todo` items 1, 2, 4)
- [ ] `01_speech_to_text.ipynb` — Whisper transcription of downloaded audio.
- [ ] Extend it with `task="translate"` for **speech → translated text** (item 2).
- [ ] `audio_bitrate.ipynb` — re-encode audio at a target bitrate via `ffmpeg`
      (item 4). Small and independent; good warm-up task.

### Phase 2 — Text → Knowledge (`todo` items 5, 7)
- [ ] `02_summarization.ipynb` — summarize transcripts. Offer two modes: a local
      HF model and an API-based prompt (ties into the "prompt-building" doc).
- [ ] `03_word_cloud.ipynb` — word cloud from a transcript (`wordcloud` + `matplotlib`).

### Phase 3 — Text → Speech (`todo` items 3, 6)
- [ ] `04_text_to_speech.ipynb` — baseline TTS (`edge-tts`, free, many voices).
- [ ] Extend with **special / custom voices** (item 6) — voice selection, or a
      higher-quality engine (e.g. Coqui TTS) documented as an optional heavier dep.

### Phase 4 — Knowledge consolidation & docs (`todo` section B)
- [ ] "Video → mindmap" walkthrough (Markdown; link the recorded video when ready).
- [ ] Obsidian workflow doc: how transcript → summary → mindmap → notes fit together.
- [ ] Prompt-building doc capturing the author's logic, referenced from the
      summarization notebook.
- [ ] Codespaces doc: fold `learning_codspaces.txt` into a proper README section.

### Phase 5 — Polish (optional)
- [~] Migrate downloads from `pytube`/`scrapetube` to `yt-dlp` for reliability.
      Done in the active tools; the `scrapetube`-based `get_my_playlists.py` was
      retired to `ignore/` rather than migrated; the notebook is still pending.
- [ ] Optional Streamlit front-end (the author already explores Streamlit elsewhere).
- [ ] Light CI: lint + "notebooks execute" smoke test.

---

## 4. Suggested repository layout

```
learn-better/
├── code/                # existing scripts
├── lib/                 # NEW: shared helpers (download, transcribe, tts, summarize)
├── notebooks/           # one notebook per capability
├── data/                # git-ignored: audio/, transcripts/, summaries/
├── docs/                # mindmap / Obsidian / prompt-building / codespaces
├── requirements.txt
└── plan.md
```

---

## 5. Recommended next step

The download + transcript foundation is now working (`test_read_channel.py`), so
the next high-value move is **`01_speech_to_text.ipynb`**: run Whisper over the
audio in `audio/` to produce transcripts for the clips whose subtitles are
disabled (the ones the tool currently flags as `NO TRANSCRIPT`). That closes the
gap between "YouTube gave us a transcript" and "every clip has a transcript", and
unblocks summarization (item 5) and translation (item 2).

(The old `scrapetube`/API-key script `get_my_playlists.py` has been retired to
`ignore/`, so no migration of it is needed; the no-key `yt-dlp` tools cover its
use case.)

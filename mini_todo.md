# Mini TODO — next three build steps (scripts only, no notebooks)

A focused, gradual plan for three things, ordered by **increasing complexity** so
each step is small, runnable, and testable before moving on:

1. **List all my YouTube playlists** (no API key, using yt-dlp).
2. **Refactor the proven logic into a reusable `lib/` module** (Phase 0 of `plan.md`).
3. **Speech-to-text with Whisper** for clips whose subtitles are disabled
   (the recommended next step in `plan.md`).

Everything is a **plain `.py` script** — no Jupyter notebooks yet. Each phase ends
with a concrete "test it" you can run from the repo root (env active, e.g. `c.bat`).

Grounding: the working download/transcript logic already lives in
`code/test_read_channel.py` (functions `step1_list_videos`, `step2_transcript`,
`step3_download_audio`, plus helpers `_build_url`, `_cookie_opts`, `_proxy_opts`,
`_impersonate_opts`, `load_languages`, `_vtt_to_text`, `_safe_filename`). The old
API-key playlist enumeration lives in `ignore/get_my_playlists.py` (retired). We
reuse ideas from both, key-free.

---

## Phase A — List all my playlists (simplest; ~1 short script)

**Goal:** given a channel (`@handle` or `UC...` id), print every public playlist
with its title, id, and video count. No API key (yt-dlp `extract_flat`).

Why first: it is self-contained, read-only, fast to test, and reuses the network
options already written in `test_read_channel.py`.

### [x] A0. Confirm the approach (5 min, no code) — DONE
- yt-dlp can list a channel's playlists via the URL
  `https://www.youtube.com/@<handle>/playlists` (or `/channel/UC.../playlists`)
  with `extract_flat=True`. Each entry exposes `id`, `title`, and often
  `playlist_count`.
- **Test:** none yet; just note the URL shape.
- ✅ Confirmed working against `@dragosborosgpt`.

### [x] A1. New script `code/list_playlists.py` — resolve + list — DONE
- Config block at top (same style as the other scripts):
  `CHANNEL = "@your_handle"` (or a `UC...` id, or full URL).
- Build the playlists URL from `CHANNEL` (mirror `_build_url` logic).
- Copy the network helpers from `test_read_channel.py`:
  `_proxy_opts`, `_cookie_opts`, `_impersonate_opts`, and `_apply_no_proxy_env`
  (Phase B will de-duplicate these; for now copy so the script stands alone).
- Run yt-dlp with `{"quiet": True, "extract_flat": True, "skip_download": True}`
  on the playlists URL; iterate `info["entries"]`.
- Print, per playlist: `title`, `id`, and `playlist_count` (guard for missing keys).
- **Test:**
  ```cmd
  python code\list_playlists.py
  ```
  Expect a printed table of your public playlists. Try both an `@handle` and a
  `UC...` id.
- ✅ Built `code/list_playlists.py` + `p.bat`. Went beyond spec: accepts
  `@handle` / `UC...` / full URL, alphabetical sort, captures `availability`
  (public/unlisted/private), actionable 404 + Chrome-cookie-lock error hints,
  and robust pagination (retries, dedupe, "incomplete run" warning).

### [x] A2. Save the result to a file — DONE
- Write the playlists to `data/playlists.json` (create `data/` if missing):
  a list of `{ "title", "id", "url", "count" }`.
- Add `data/` to `.gitignore` if not already ignored.
- **Test:** re-run; confirm `data/playlists.json` exists and matches the console
  output. Delete it and re-run to confirm it regenerates.
- ✅ Saves to `data/playlists.json`; `data/` added to `.gitignore`. Richer schema
  than spec: each playlist has `title, id, url, count, availability, videos`.

### [x] A3. Per-playlist video listing — DONE (exceeded)
- Add a function `list_playlist_videos(playlist_id, limit=None)` that reuses the
  same yt-dlp `extract_flat` call on
  `https://www.youtube.com/playlist?list=<id>` and returns `[(video_id, title)]`
  (this is exactly what `step1_list_videos` already does for one playlist).
- **Test:** pass one id from A2 and print its first few videos.
- ✅ Two paths: `list_playlist_videos()` (via `LIST_VIDEOS_FOR`) prints a single
  playlist's videos, AND `fetch_playlist_videos()` now writes every playlist's
  video list (`[{id, title}]`) into `data/playlists.json` with accurate counts
  and a live progress indicator + per-request timeout.

**Phase A done when:** you can list all your playlists and their videos with no
API key, and the result is saved to `data/playlists.json`.

> **STATUS: Phase A = 100% complete** (A0, A1, A2, A3 all done; A1–A3 exceeded
> their original spec). Verified live against `@dragosborosgpt`. Next up: Phase B.

---

## Phase B — Refactor the proven logic into a reusable `lib/` (medium)

**Goal:** extract the working functions from `test_read_channel.py` (and the new
`list_playlists.py`) into a small, importable package so future scripts stay
short. This is Phase 0 of `plan.md` ("small reusable `lib/` module").

Why second: it touches multiple files and changes imports, so it is riskier than
Phase A — but doing it now keeps Phase C (Whisper) clean.

### B1. Create the package skeleton
- New folder `lib/` with `lib/__init__.py`.
- New module `lib/net.py` holding the shared network helpers, moved verbatim:
  `apply_no_proxy_env()`, `proxy_opts()`, `cookie_opts()`, `impersonate_opts()`
  (drop the leading underscores now that they are public API), plus the config
  constants they depend on (`NO_PROXY`, `PROXY_URL`, `COOKIES_FILE`,
  `COOKIES_FROM_BROWSER`).
- **Test:**
  ```cmd
  python -c "import sys; sys.path.insert(0,'.'); from lib import net; print(net.proxy_opts())"
  ```
  Expect a dict (e.g. `{'proxy': ''}`), no import error.

### B2. Move text/util helpers to `lib/textutil.py`
- Move `_safe_filename`, `_clean_text`, `_vtt_to_text`, `_TIMING_RE`, and
  `load_languages` (+ `LANGUAGES_CONFIG`) here as public functions.
- **Test:** a one-liner that feeds a tiny fake VTT string to `vtt_to_text` and
  prints the cleaned lines.

### B3. Create `lib/youtube.py` — the core operations
- Public functions, each a thin move of the existing logic:
  - `build_url(playlist_id=None, channel=None, search=None, limit=5)`
    (from `_build_url`).
  - `list_videos(url, limit=5)` (from `step1_list_videos`).
  - `list_playlists(channel)` (from Phase A).
  - `download_transcript(video_id, title, languages, out_dir)`
    (from `step2_transcript` / the `test_read_transcript.py` version).
  - `download_audio(video_id, out_dir, audio_format="mp3", quality="192")`
    (from `step3_download_audio`).
- These import from `lib.net` and `lib.textutil`. Keep behavior identical.
- **Test:**
  ```cmd
  python -c "import sys; sys.path.insert(0,'.'); from lib import youtube as y; print(y.list_videos(y.build_url(playlist_id='PLsWyhklHwjExuXrXjJktcdYkCFL0PNdW7', limit=3)))"
  ```
  Expect the same 3 videos the current tool prints.

### B4. Rewrite the entry scripts to use `lib/`
- Slim `code/test_read_channel.py`, `code/test_read_transcript.py`, and
  `code/list_playlists.py` down to: config block + `main()` that calls `lib`
  functions. Delete the now-duplicated helper bodies from them.
- Keep the `c/r/t/s` batch files working unchanged (they still call the same
  script paths).
- **Test (regression):** run `r` and `t`; confirm identical output to before the
  refactor (same videos listed, transcripts saved to `transcripts/`, existing
  files skipped). This is the key check — behavior must not change.

### B5. (Optional) tiny `lib/paths.py` for output layout
- Centralize `AUDIO_DIR`, `TRANSCRIPT_DIR`, and a new `DATA_DIR="data"` so all
  scripts agree on where things go (sets up the eventual `data/` consolidation).
- **Test:** import it and print the paths.

**Phase B done when:** all entry scripts import from `lib/`, no logic is
duplicated across scripts, and `r` / `t` produce byte-for-byte the same results
as before.

---

## Phase C — Speech-to-text with Whisper (most complex)

**Goal:** for clips whose subtitles are disabled (the ones the tools flag as
`NO TRANSCRIPT`), generate a transcript from the downloaded audio using Whisper.
This closes the gap between "YouTube gave us captions" and "every clip has a
transcript", and unblocks summarization/translation. Script only, no notebook.

Why last: it adds a heavy dependency (a Whisper model), needs ffmpeg, is slower,
and benefits from the `lib/` foundation from Phase B.

### C0. Pick the engine and add the dependency (decision + install)
- Use **`faster-whisper`** (CTranslate2 backend): lighter and faster than
  `openai-whisper`, CPU-friendly, and supports transcription **and** translation
  (covers `todo` items 1 and 2 in one tool).
- Add `faster-whisper` to `requirements.txt` **only when starting this phase**
  (keep installs lean). Note it needs `ffmpeg` (already documented).
- **Test:**
  ```cmd
  pip install faster-whisper
  python -c "from faster_whisper import WhisperModel; print('faster-whisper OK')"
  ```

### C1. New script `code/transcribe_audio.py` — transcribe ONE file
- Config: `MODEL_SIZE = "base"` (start small; `small`/`medium` later),
  `DEVICE = "cpu"`, `COMPUTE_TYPE = "int8"`, and `TASK = "transcribe"`.
- Function `transcribe_file(audio_path, model, language=None)`:
  load the model once, run `model.transcribe(audio_path, task=TASK)`, and join
  the segment texts. Return `(text, detected_language)`.
- Hard-code one existing file from `audio/` to prove it works end to end.
- **Test:**
  ```cmd
  python code\transcribe_audio.py
  ```
  Expect printed transcript text for that one audio file. Time it; note how long
  `base` takes on your machine.

### C2. Save Whisper transcripts next to the yt-dlp ones
- Write to `transcripts/<title> [<id>].whisper.<lang>.txt`, reusing
  `lib.textutil.safe_filename` (from Phase B). Use a distinct `.whisper.` marker
  so these never collide with subtitle-derived transcripts.
- Skip if the target file already exists (match the skip-if-exists pattern used
  everywhere else).
- **Test:** run twice; second run should skip and not re-transcribe.

### C3. Wire it to the "NO TRANSCRIPT" clips (the real use case)
- Add a function that, for a playlist/channel/search, does:
  list videos (`lib.youtube.list_videos`) → try
  `lib.youtube.download_transcript` → if none, `lib.youtube.download_audio` then
  `transcribe_file`.
- In practice: reuse the audio already in `audio/`; only transcribe clips missing
  a subtitle transcript.
- **Test:** point it at a source containing at least one captions-disabled clip
  (the tools already flag which ids). Confirm a `.whisper.` transcript appears
  only for those clips.

### C4. (Optional) translation mode
- Set `TASK = "translate"` to get English text from a non-English clip
  (`todo` item 2). Save as `<title> [<id>].whisper.en.txt`.
- **Test:** run on a known non-English clip; confirm English output.

### C5. (Optional) batch + summary hook
- Add a batch runner (e.g. `w.bat` → `python code/transcribe_audio.py`) and make
  the output discoverable by `make_summaries.py` (it currently looks for
  `*.en.txt`; decide whether `.whisper.en.txt` should also feed summaries).
- **Test:** run `w`, then `s`; confirm the newly transcribed clip shows up as
  needing a summary.

**Phase C done when:** any clip with disabled subtitles gets a Whisper transcript
saved alongside the others, with skip-if-exists, driven by a plain script.

---

## Suggested order of attack (smallest testable increments)

| # | Task | Complexity | Test |
|---|------|-----------|------|
| 1 | A1 list playlists to console | low | `python code\list_playlists.py` |
| 2 | A2 save `data/playlists.json` | low | file regenerates |
| 3 | A3 list videos of one playlist | low | prints video ids |
| 4 | B1–B2 `lib/net.py`, `lib/textutil.py` | medium | import + tiny unit checks |
| 5 | B3 `lib/youtube.py` | medium | `list_videos` matches current output |
| 6 | B4 slim entry scripts | medium | `r` / `t` regression identical |
| 7 | C0–C1 install + transcribe one file | high | printed transcript |
| 8 | C2 save `.whisper.` transcripts | high | skip-if-exists works |
| 9 | C3 transcribe only NO-TRANSCRIPT clips | high | file only for disabled-caption clips |
| 10 | C4/C5 translate + batch (optional) | high | English output; `s` sees it |

Build top-to-bottom. Each row should run green before starting the next.

---

## Notes / guardrails
- **No API key** anywhere — everything uses yt-dlp (Phase A/B) or local Whisper
  (Phase C).
- **Cloud IPs** (Codespaces/Colab) may hit the YouTube bot-check; pass a
  `cookies.txt` via `COOKIES_FILE` as documented in the README.
- **Keep installs lean:** add `faster-whisper` to `requirements.txt` only at
  Phase C, not before.
- **Behavior parity is the Phase B success metric** — the refactor must not
  change what the tools produce, only where the code lives.
- Outputs continue to land in git-ignored folders (`audio/`, `transcripts/`, and
  the new `data/`).

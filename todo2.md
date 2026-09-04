# TODO2 — Text-to-Speech baseline (`todo` items 3, 6 from plan.md)

Build the **text → speech** feature (Phase 3 in `plan.md`): a Python script reads
a text source (a `transcripts/`, `generated_transcripts/`, or `summaries/` file),
synthesizes narration with a **local, free** TTS engine, and writes the audio to a
new `tts_output/` folder. This mirrors Phase C (speech-to-text via
`faster-whisper`) but in the opposite direction.

Scope for THIS plan = the **baseline** only: one engine (**Piper**, CPU-only,
MIT), no voice cloning. Item 6 (special/custom voices, cloning) is deliberately
left as an optional later phase (D4) so the simple case stays simple. The full
landscape research lives in `tts.md` (kept for reference).

**All free, no extra cost.** Piper is `pip install piper-tts` — MIT-licensed,
CPU-only, no GPU, no API key, no paid service. It downloads a small per-voice
`.onnx` model on first use (same "first-run download" pattern `faster-whisper`
already uses). Audio is written as `.wav`; optional `.mp3` conversion reuses the
**ffmpeg** binary the project already requires. This is the ONE new pip dep, added
lean when this phase starts (per plan.md's "new deps per phase" rule).

> Why Piper as the baseline: it matches this repo's existing CPU-only, no-GPU
> assumption, is permissively licensed, and is the fastest to get running.
> Kokoro (higher quality, still Apache-2.0, CPU-capable) is the documented
> upgrade path (phase D3); edge-tts / XTTS / Chatterbox are noted alternatives.
> See `tts.md` §2 for the decision framework.

---

## Design direction (decided, matches the repo)

- **Reuse the existing conventions.** Same shape as `transcribe_audio.py` /
  `make_wordcloud.py`: a config block at the top of the script, an optional JSON
  config in `config/`, `SELECT_BY = name | id | all` selection over the text
  folders, skip-if-exists, and a written/skipped/failed tally. A one-letter batch
  runner.
- **Input is TEXT, not audio.** Select from `transcripts/`,
  `generated_transcripts/`, and `summaries/` (the study material we produce).
  Reuse the same `[<id>]` video-id key and base-name conventions as
  `make_summaries.py` / `make_wordcloud.py`. For a `summaries/*.summary.md`,
  strip Markdown to plain text before synthesis.
- **Piper is the engine (baseline).** Prefer the Python API (`piper-tts`); fall
  back to invoking the `piper` CLI via list-form `subprocess` if the API is
  awkward. Detect the engine/voice up front and fail with a clear message +
  install hint if missing (mirrors `find_ffmpeg` in `reencode_audio.py`).
- **Never touch inputs.** Read text read-only; write audio to a NEW git-ignored
  `tts_output/` folder. Encode the voice into the output name so different voices
  coexist, e.g. `<base>.<voice>.wav`. Add `TTS_OUTPUT_DIR` to `lib/paths.py` and
  `.gitignore`.
- **Data/artifact split stays intact.** Pure text→audio transform; no HTML, no
  rendering. Slots next to the other `code/*.py` tools.
- **Model download may need the proxy bypass.** If Piper fetches its voice model
  over the network, reuse `lib/net.apply_no_proxy_env()` (the same corporate-proxy
  fix Phase C needed for Hugging Face). Verify on the first local run — Piper's
  model host may differ from HF (open item, see §gaps).

---

## Where files live

| Thing | Path | Notes |
|---|---|---|
| Input text | `transcripts/…`, `generated_transcripts/…`, `summaries/*.summary.md` | Produced by existing tools. Git-ignored except `summaries/` (tracked). |
| Output audio | `tts_output/<base>.<voice>.wav` (opt. `.mp3`) | NEW folder, git-ignored. Add `TTS_OUTPUT_DIR` to `lib/paths.py`. |
| Script | `code/generate_speech.py` | Config block + `main()`, same style as `transcribe_audio.py`. |
| Config | `config/config_tts.json` | select_by/select + voice/format knobs. |
| Runner | `v.bat` | `v` (defaults) or `v config\config_tts.json`. (`t`/`s`/`a`/`w`/`d`/`wc` taken; `v` = voice.) |

> **Why a new folder + voice in the name?** Keeps generated audio separate from
> downloaded `audio/`, and lets the same transcript be voiced by multiple voices
> without collision (drives skip-if-exists).

---

## Config — proposed `config/config_tts.json`

```json
{
  "_comment": "Text-to-speech config (todo items 3, 6 — baseline). select_by is one of name|id|all over the text folders (transcripts/, generated_transcripts/, summaries/). For 'name', select is case-insensitive substrings of the file name; for 'id', select is 11-char YouTube ids (the [<id>] in the name); for 'all', every text file is voiced. engine is 'piper' (the free CPU-only baseline). voice is a Piper voice id (e.g. 'en_US-lessac-medium'); the model downloads on first use. format is 'wav' (Piper native) or 'mp3' (converted via ffmpeg). max_chars optionally caps very long inputs for a quick test. Outputs go to tts_output/<base>.<voice>.wav (skip-if-exists); text inputs are never modified.",
  "select_by": "name",
  "select": ["Git and GitHub"],
  "engine": "piper",
  "voice": "en_US-lessac-medium",
  "format": "wav",
  "max_chars": null
}
```

- `voice`: the Piper voice model id. `en_US-lessac-medium` is a common, clear
  English voice; the model file is a few–tens of MB, cached after first download.
- `format`: `wav` is Piper's native output; `mp3` converts via ffmpeg for
  consistency with `audio/` (reuse the `reencode_audio.py` subprocess pattern).
- `max_chars`: optional cap so a first smoke test on a long transcript is quick;
  `null` = whole file.
- `engine`: fixed to `piper` for the baseline; `kokoro` is a later phase (D3).

---

## Phase D0 — Scope + prerequisites (no code) — DONE

- [x] **D0.1** Confirm the ONE new dep: `piper-tts` (MIT, CPU-only, no GPU/API).
      ffmpeg (already required) is only needed for optional `mp3` output. Will
      NOT add to `requirements.txt` until D1 proves it installs/runs locally
      (PyPI may be blocked in some environments — same caveat Phase C hit).
      ✅ Decision recorded; no `requirements.txt` change yet (deferred to D5 after
      D1 confirms it locally).
- [x] **D0.2** Output folder `tts_output/`; add `TTS_OUTPUT_DIR = "tts_output"`
      to `lib/paths.py`; add `tts_output/` to `.gitignore`.
      ✅ Added `TTS_OUTPUT_DIR = "tts_output"` to `lib/paths.py` (also refreshed
      the module docstring). Added `tts_output/` to `.gitignore` next to
      `audio_reencoded/`. Verified: `from lib import paths` →
      `TTS_OUTPUT_DIR = tts_output`, and `git check-ignore tts_output/x.wav`
      confirms the folder is ignored.
- [x] **D0.3** Output name pattern `<base>.<voice>.<ext>` where `<base>` is the
      input file's base (minus language/extension, reuse `make_wordcloud.py`'s
      `parse_meta` idea), `<voice>` is the Piper voice id, `<ext>` from `format`.
      Different voices coexist; drives skip-if-exists.
      ✅ Decision recorded; implemented in D1.
- [x] **D0.4** Markdown-to-text rule for `summaries/*.summary.md` (strip `#`,
      list markers, links, code fences → plain sentences) so the narration
      doesn't read out syntax.
      ✅ Decision recorded; implemented in D1's `read_text`.

**Test:** none (decisions only) except the D0.2 groundwork, verified above.
D0.1/D0.3/D0.4 are decisions, written as config comments atop the script in D1.

---

## Phase D1 — Synthesize ONE file (proof of concept) — DONE, USER-VALIDATED

- [x] **D1.1** New script `code/generate_speech.py`. Config block at top (same
      style as `transcribe_audio.py`): `SELECT_BY`, `SELECT`, `ENGINE="piper"`,
      `VOICE="en_US-lessac-medium"`, `FORMAT`, `MAX_CHARS`. Repo-root import
      (`from lib import paths, net`); UTF-8 stdout guard.
- [x] **D1.2** `find_piper()` — verifies the `piper` CLI is on PATH (env-scoped);
      clear install hint + clean abort if missing (mirrors `find_ffmpeg`).
      `ensure_voice()` auto-downloads the voice via `python -m
      piper.download_voices <voice> --data-dir tts_output/.voices` on first use,
      with a manual-command hint on failure. (Drives the CLI via subprocess — its
      interface is stable across piper versions, unlike the Python API.)
- [x] **D1.3** `read_text()` — strips `[HH:MM:SS]` timestamps for transcripts and
      Markdown (`_strip_markdown`) for `.summary.md`; applies `MAX_CHARS` if set.
- [x] **D1.4** `synthesize_one()` — pipes text into the piper CLI
      (`piper -m <onnx> -f <out.wav>`, list-form, no `shell=True`) to write the
      wav. If `FORMAT="mp3"`, converts via ffmpeg (`_wav_to_mp3`, reusing the
      `reencode_audio.py` command shape). Returns written/skipped/empty/failed.
- [x] **D1.5** Output path `tts_output/<base>.<voice>.<ext>`; creates the folder;
      **skip-if-exists**. Calls `lib.net.apply_no_proxy_env()` before the model
      download.

✅ Also: dedupe by video id preferring **summary > caption > whisper**, up-front
validation of `engine`/`format`/`select_by`, and empty-text handling. The voice
model caches in `tts_output/.voices/` (git-ignored) so it downloads only once.

**Local prerequisite (user did this):** `pip install piper-tts`. Confirmed the
`piper` CLI installed at `...\envs\learn-better\Scripts\piper.exe` and the
package exposes `piper.download_voices` (the modern MIT `piper1-gpl` build).

**How D1 was tested (record for re-runs):**
```cmd
c
python code\generate_speech.py     :: defaults: name "Git and GitHub", en_US-lessac-medium, wav
```
1. **First run** downloaded the voice to `tts_output/.voices/en_US-lessac-medium.onnx`
   (+ `.onnx.json`) and synthesized to
   `tts_output/Git and GitHub Tutorial for Beginners [tRZGeaHPoaw].en_US-lessac-medium.wav`
   (~9.5 MB). Tally `1 synthesized, 0 skipped, 0 empty, 0 failed`.
2. **Source picked = the SUMMARY** (`.summary.md`), per the summary>caption>whisper
   preference — a concise ~3.7-min narration rather than a 36-min transcript read.
   Markdown was stripped (no `#`/`*`/backticks spoken).
3. **ffprobe check:** `codec_name=pcm_s16le`, `sample_rate=22050`, `channels=1`,
   `duration=220.1s` — a valid, playable wav.
4. **Skip-if-exists:** second run printed `= exists, skipping` →
   `0 synthesized, 1 skipped`; the voice model was NOT re-downloaded (cached).
5. **Listen:** open the `.wav` in VLC / Windows Media Player / a browser — clear
   English narration of the summary.

**What to look for:** wav created; plays and is intelligible; ffprobe duration
> 0; input text unchanged; second run skips; voice downloaded once then cached.

---

## Phase D2 — Batch + selection + config + runner — DONE, USER-VALIDATED

- [x] **D2.1** Selection `SELECT_BY = "name" | "id" | "all"` over `summaries/` +
      `transcripts/` + `generated_transcripts/`, deduped by video id preferring
      **summary > caption > whisper** (documented in the config `_comment`).
      Reuses the `[<id>]` regex + a yield-in-preference-order iterator
      (`_all_text_files` / `pick_text`). (Implemented in D1.)
- [x] **D2.2** Loops the D1 core over the selection with a
      written/skipped/empty/failed tally; prints each input (tagged with its
      source folder), the voice, and the output name.
- [x] **D2.3** JSON config `config/config_tts.json` (schema above), loaded via an
      optional `argv[1]` path or auto-loaded if present — same
      `load_config` / `resolve_config_path` pattern as `make_wordcloud.py`.
- [x] **D2.4** `v.bat` runner: `v` (default config / in-file defaults) or
      `v config\config_tts.json`. Mirrors `wc.bat`
      (`python code\generate_speech.py %1`).

✅ Default `config/config_tts.json` = name "Git and GitHub", en_US-lessac-medium,
wav. `v.bat` created.

**How D2 was tested (record for re-runs):**
```cmd
c
v config\config_tts.json                :: default: Git & GitHub summary -> wav
```
1. **Batch by id** — a config with `select_by:"id"`,
   `select:["F2DBSH2VoHQ","9llCMADxvzI"]` (a `max_chars:400` cap kept the test
   fast) → `Selected 2 text file(s) via SELECT_BY='id'`, both resolved to their
   **summaries** (preference working), including the Unicode/space-heavy GitLab
   title. Tally `2 synthesized, 0 skipped, 0 empty, 0 failed`.
2. **Skip-if-exists (re-run)** — same config again → both `= exists, skipping`,
   tally `0 synthesized, 2 skipped`.
3. Config auto-load + CLI-arg path both resolve (same pattern as the other tools).
4. Cleaned up the truncated 400-char demo wavs after (kept the full D1 wav).

**What to look for:** selection list matches (right count/files); tally like
`2 synthesized, 0 skipped, 0 failed`; a no-match selection prints a clear
message (not a crash); a summary reads as clean prose (no `#`/`*`/backticks);
changing `voice` writes a new `<base>.<other-voice>.wav` without collision.

---

## Phase D-speed — Speaking speed (`length_scale`) — DONE, VALIDATED

Follow-up to the minimal baseline (user request): pick the speaking speed. Piper
exposes this natively as `--length-scale` (>1 = slower, <1 = faster; scales
phoneme duration), so it's a synthesis parameter, not a re-encode.

- [x] **DS.1** Added `LENGTH_SCALE` to the config block + `_CONFIG_KEYS` (key
      `length_scale`). Default `1.0`. Presets: **0.9** faster, **1.0** normal,
      **1.15** slower/clearer.
- [x] **DS.2** Passed to the piper CLI as `--length-scale <value>` in
      `synthesize_one`, appended only when it differs from 1.0.
- [x] **DS.3** Validated up front in `main()`: must be a positive number; a bad
      value prints `!! Invalid length_scale ...` and exits (no traceback).
- [x] **DS.4** Speed baked into the output name as `.s<scale>` (only when != 1.0,
      so normal-speed names are unchanged): `<base>.<voice>[.s<scale>].<ext>`.
      Different speeds coexist and skip-if-exists stays correct.
- [x] **DS.5** Documented `length_scale` in `config/config_tts.json`'s `_comment`
      (and the key added with default 1.0), noting the 0.9 / 1.0 / 1.15 presets.

**How D-speed was tested (record for re-runs):** synthesized the same short
summary (`max_chars:300`, id `F2DBSH2VoHQ`) at three speeds via throwaway configs.
- Three distinct files coexisted: `...s0.9.wav`, `...wav` (1.0, no tag),
  `...s1.15.wav`.
- ffprobe durations were monotonic on the SAME text: **0.9 → 20.48 s**,
  **1.0 → 21.71 s**, **1.15 → 23.57 s** — faster is shorter, slower is longer.
- Cleaned up the throwaway configs and demo wavs after.

**What to look for:** the 0.9 / 1.15 files carry an `.s0.9` / `.s1.15` tag while
1.0 has none; the 0.9 clip is audibly faster/shorter and 1.15 slower/longer
(confirm with `ffprobe ... duration`); a bad `length_scale` prints a clear `!!`
and exits without a traceback.

---

## Phase D3 — Robustness + edge cases — DONE, VALIDATED

Most guards were built during D1/D-speed; D3 confirmed and filled the gaps.

- [x] **D3.1** Missing engine/voice → friendly message + hint, clean exit.
      `find_piper()` handles a missing CLI; `ensure_voice()` handles a voice that
      can't be downloaded, printing `! voice download failed: <reason>` + a
      manual-retry command. No traceback.
- [x] **D3.2** A failed synthesis → `synthesize_one` captures the reason, counts
      it `failed`, deletes any partial output, and the loop **continues**; empty
      text after cleaning → `"empty"` (not a crash).
- [x] **D3.3** Empty selection → `No text matched SELECT_BY=... (looked in ...)`,
      exit 0. Empty input text → `! empty after cleaning`, counted `empty`.
- [x] **D3.4** Up-front validation of `engine` (only `piper`), `format`
      (`wav`/`mp3`), `select_by` (name/id/all + non-empty select), and
      `length_scale` (positive number). Long inputs are handled by Piper's own
      sentence splitting; `max_chars` is available as a quick-test cap.

**How D3 was tested (record for re-runs):** throwaway configs in `config/`.
- `length_scale:"fast"` → `!! Invalid length_scale 'fast'. Use a positive number
  (e.g. 0.9 faster, 1.0 normal, 1.15 slower).` — clean exit, no traceback.
- `voice:"en_XX-nonexistent-voice"` → `! voice download failed: <reason>` with a
  manual-retry hint — clean exit, no traceback, no partial file. (The host
  returned HTTP 429 during the test, but the graceful-failure path is what
  matters.)
- (Earlier phases already showed `!! Invalid select_by`, `!! Invalid format`, and
  `No text matched ...`.)

**What to look for:** each bad-input case prints a clear `!!`/`!` message and
exits without a Python traceback; a bad voice leaves no partial output; the batch
still finishes with a tally on per-file failures.

---

## Phase D4 — (OPTIONAL) special / custom voices — DEFERRED

`todo` item 6. Out of scope for the baseline; captured here so it isn't lost.
Only start if the user asks.

- [ ] **D4.1** Add voice **selection** (multiple Piper voices; list installed /
      downloadable voices).
- [ ] **D4.2** Optional higher-quality engine `kokoro` behind
      `engine: "kokoro"` (Apache-2.0, CPU-capable; documented Colab path). Keep
      Piper the default so the simple case is unchanged.
- [ ] **D4.3** Optional **voice cloning** (XTTS v2 / Chatterbox) gated behind an
      explicit `voice_sample: path/to/reference.wav` flag, kept separate from the
      no-cloning default. Note license caveats (XTTS v2 non-commercial) and the
      likely GPU/Colab requirement. See `tts.md` §1.1/§2.

**Test:** compare voices on the same input; for cloning, verify a clean 10–30s
reference sample produces a recognizable voice.

---

## Phase D5 — Docs + wiring — DONE

- [x] **D5.1** `README.md`: added a "Text to speech (`v.bat`)" section (what it
      does, `tts_output/` output, config keys incl. `length_scale`, the
      Piper-is-free/CPU-only note, first-run model download, ffprobe check); added
      `v.bat` to the helper list and `generate_speech.py` / `v.bat` /
      `tts_output/` + `config_tts*.json` to the repo layout; added `piper-tts` to
      the dependency table AND `requirements.txt`.
- [x] **D5.2** `how_to_test.md`: added a "Phase D" block (D1 one file, D2 batch,
      Speed, D3 failures) with commands + the ffprobe/listen check and a `::`
      caution; added `v` to the quick examples, the "all runners" table, and a
      new "TTS config files" table.
- [x] **D5.3** `youtube.html`: added the `v` row to the tools table; marked
      `todo` item 3 **Done** and item 6 **partial** (voice+speed selectable,
      cloning deferred); helper row → `c/r/t/s/p/w/d/wc/a/v`; added a "Text to
      speech" Overview card; added `generate_speech.py`, `tts_output/`, `v.bat`,
      `config_tts*.json` to the layout; recolored Phase 3 (and P1 bitrate) in the
      roadmap.
- [x] **D5.4** `plan.md`: ticked Phase 3 baseline TTS (`[x]`) and set item 6 to
      partial (`[~]`); added a `code/generate_speech.py` row to the Section 1
      status table; rewrote the Section 5 next-step (baseline TTS done → optional
      voice extras / consolidation / docs next).

**Test:** open `youtube.html` and `README.md`, confirm the new tool is listed and
`todo` item 3 shows Done; run through the `how_to_test.md` Phase D block.

---

## Status: ALL BASELINE PHASES COMPLETE (D0-D5 + D-speed)

Baseline TTS is delivered, validated, and documented. Only **D4** (optional
voices/cloning) remains, intentionally deferred. `todo2.md` is ready to be
archived to `ignore/` once the docs are confirmed and the work is committed.

---

## Suggested order of attack

| # | Task | Complexity | Test |
|---|------|-----------|------|
| 1 | D1 synthesize one file via Piper | med | output plays, intelligible, ffprobe duration > 0 |
| 2 | D2 batch/selection + config + `v.bat` | med | one output per selected text, skip-if-exists |
| 3 | D3 robustness (missing voice, failures) | low-med | friendly errors, no partial files, batch continues |
| 4 | D5 docs + wiring | low | tool listed; item 3 marked Done |
| — | D4 voices/cloning | high | DEFERRED — only if the user asks |

Build top-to-bottom; each row should run green before the next. (D4 is skipped
unless requested.)

---

## Notes / guardrails

- **Free only.** Piper (MIT, CPU-only) + stdlib + the already-required ffmpeg for
  optional mp3. No API, no paid service, no GPU required for the baseline. One new
  pip dep (`piper-tts`), added when D1 proves it locally.
- **Never touch inputs.** Read text read-only; write audio to `tts_output/`
  (git-ignored). Voice is in the filename so multiple voices don't collide.
- **No `shell=True`.** Use the Piper Python API, or list-form
  `subprocess.run([...])`, so titles with spaces/accents/emoji are safe.
- **Skip-if-exists** like every other tool.
- **Proxy/model download.** Reuse `lib.net.apply_no_proxy_env()` before any
  first-run model fetch (same fix Phase C used for Hugging Face) — verify Piper's
  model host on first local run.
- **PyPI may be blocked in some sandboxes.** Install + real synthesis testing
  happens on the local machine (same as `faster-whisper`); don't mark D1 done
  until it runs there.
- Keep the script's config style consistent with `transcribe_audio.py` /
  `make_wordcloud.py` (top-of-file config + optional JSON config in `config/` +
  one-letter batch runner).

---

## Open items / research gaps (from `tts.md`, verify during D1)

1. Whether Piper's voice-model host needs the `apply_no_proxy_env()` treatment
   (not confirmed; check on first local install).
2. Long-input behavior (chunking vs. a `max_chars` cap) — confirm no silent
   truncation on a full-length transcript.
3. Kokoro (D3-optional) and edge-tts remain documented alternatives in `tts.md`;
   not part of this baseline.

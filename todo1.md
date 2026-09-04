# TODO1 — Audio re-encode / bitrate helper (`todo` item 4 from plan.md)

Build the **audio-to-audio at a different bit rate** feature: a Python script
re-encodes existing `audio/*.mp3` (or `.webm`/`.m4a`) to a chosen bitrate/format
using **ffmpeg**, writing the results to a separate output folder so originals
are never touched. This is `todo` item 4 and the smallest, most independent
Phase 1 leftover in `plan.md`.

**All free, no extra cost.** ffmpeg is already a project dependency (used by
`yt-dlp` for mp3 conversion; documented in README/Installation). No pip package,
no API, no cloud service. The script just shells out to the `ffmpeg` binary the
user already has on PATH (or in the conda env). No new entry in
`requirements.txt`.

---

## Design direction (decided, matches the repo)

- **Reuse the existing conventions.** Same shape as `transcribe_audio.py` /
  `make_wordcloud.py`: a config block at the top of the script, an optional JSON
  config in `config/`, `SELECT_BY = name | id | all` selection over `audio/`,
  skip-if-exists, and a written/skipped/failed tally. A one-letter batch runner.
- **ffmpeg is the engine.** Pure stdlib `subprocess` call to `ffmpeg`. No
  `pydub`/`ffmpeg-python` wrappers needed (avoid extra deps). Detect ffmpeg on
  PATH up front and fail with a clear message + install hint if it is missing.
- **Never overwrite originals.** Read from `audio/`, write to a NEW folder
  `audio_reencoded/` (git-ignored). Encode the target bitrate into the output
  file name so different runs don't collide, e.g.
  `<title> [<id>].64kbps.mp3`.
- **Data/artifact split stays intact.** This is a pure file→file transform; no
  HTML, no rendering. It slots next to the other `code/*.py` tools.

---

## Where files live

| Thing | Path | Notes |
|---|---|---|
| Input audio | `audio/<title> [<id>].mp3` (also `.webm`/`.m4a`) | Produced by `read_channel.py` / `transcribe_audio.py`. Git-ignored. |
| Output audio | `audio_reencoded/<title> [<id>].<bitrate>.<ext>` | NEW folder, git-ignored. Add `AUDIO_REENCODED_DIR` to `lib/paths.py`. |
| Script | `code/reencode_audio.py` | Config block + `main()`, same style as `transcribe_audio.py`. |
| Config | `config/config_reencode.json` | select_by/select + bitrate/format/codec knobs. |
| Runner | `a.bat` | `a` (defaults) or `a config\config_reencode.json`. |

> **Why a new folder, not in place?** Re-encoding to a lower bitrate is lossy
> and irreversible. Writing beside the originals (or overwriting) risks
> destroying the good copy. A separate `audio_reencoded/` keeps it safe and
> makes skip-if-exists trivial.

---

## Config — proposed `config/config_reencode.json`

```json
{
  "_comment": "Audio re-encode config (todo item 4). select_by is one of name|id|all over the audio/ folder. For 'name', select is case-insensitive substrings of the audio file name; for 'id', select is 11-char YouTube ids (the [<id>] in the name); for 'all', every audio file is re-encoded. bitrate is the target audio bitrate (e.g. '64k', '128k', '96k'). format/codec pick the container/encoder (mp3/libmp3lame is the safe free default). sample_rate and channels are optional (null = keep source). Outputs go to audio_reencoded/<name>.<bitrate>.<ext> (skip-if-exists).",
  "select_by": "name",
  "select": ["Git and GitHub"],
  "bitrate": "64k",
  "format": "mp3",
  "codec": "libmp3lame",
  "sample_rate": null,
  "channels": null
}
```

- `bitrate`: the whole point of the feature. Constant bitrate via ffmpeg `-b:a`.
- `format` / `codec`: default `mp3` / `libmp3lame` (ships with ffmpeg, free,
  universally playable). Allow `m4a`/`aac` and `ogg`/`libvorbis` / `opus`/
  `libopus` later; keep mp3 as the tested default.
- `sample_rate` (`-ar`) and `channels` (`-ac`, e.g. `1` = mono to shrink size)
  optional; `null` = keep the source value.

---

## Phase R0 — Scope + prerequisites (no code) — DONE

- [x] **R0.1** Confirm ffmpeg is the only dependency and it is already required
      (README "Install ffmpeg"). No new pip package, no `requirements.txt`
      change. Note the free codecs that ship with ffmpeg (libmp3lame, aac,
      libvorbis, libopus).
      ✅ Verified ffmpeg + ffprobe present in the `learn-better` conda env
      (`.../envs/learn-better/Library/bin/ffmpeg.exe`). No pip/requirements
      change made.
- [x] **R0.2** Decide output folder `audio_reencoded/` and add
      `AUDIO_REENCODED_DIR = "audio_reencoded"` to `lib/paths.py`. Add it to
      `.gitignore` (like `audio/`).
      ✅ Added `AUDIO_REENCODED_DIR = "audio_reencoded"` to `lib/paths.py`; added
      `audio_reencoded/` to `.gitignore`.
- [x] **R0.3** Decide the output name pattern: `<base>.<bitrate>.<ext>` where
      `<base>` is the input name minus its extension, `<bitrate>` is normalized
      (e.g. `64k` -> `64kbps`), `<ext>` from `format`. This makes different
      bitrates coexist and drives skip-if-exists.
      ✅ Implemented as `<base>.<Nkbps>.<ext>` (e.g. `... .64kbps.mp3`,
      `... .128kbps.mp3` coexist).

**Test:** none (decisions only). Written as config comments atop
`code/reencode_audio.py`.

---

## Phase R1 — Re-encode ONE file (proof of concept) — DONE, USER-VALIDATED

- [x] **R1.1** New script `code/reencode_audio.py`. Config block at top
      (same style as `transcribe_audio.py`): `SELECT_BY="name"`, `SELECT=[...]`,
      `BITRATE="64k"`, `FORMAT="mp3"`, `CODEC="libmp3lame"`, `SAMPLE_RATE=None`,
      `CHANNELS=None`. Make the repo root importable and `from lib import paths`.
- [x] **R1.2** `find_ffmpeg()` — locate the ffmpeg binary via `shutil.which`
      (respects PATH and the active conda env). If missing, print a clear error
      with the install hints from README (`conda install -c conda-forge ffmpeg`,
      `winget install ffmpeg`, `brew install ffmpeg`, `apt install ffmpeg`) and
      abort — do NOT crash with a raw traceback.
- [x] **R1.3** `reencode_one(...)` — builds the ffmpeg command and runs it with
      `subprocess.run([...])` (list form, no `shell=True`, so titles with
      spaces/accents/emoji are safe). Command shape:
      `ffmpeg -hide_banner -loglevel error -y -i "<src>" -vn -c:a <codec> -b:a
      <bitrate> [-ar <sr>] [-ac <ch>] "<out>"`. `-vn` drops any cover-art video
      stream. Returns "written"/"skipped"/"failed" on the exit code.
- [x] **R1.4** Output path via `paths.AUDIO_REENCODED_DIR` +
      `<base>.<bitrate>.<ext>`; creates the folder if missing; **skip-if-exists**
      (prints `= exists, skipping`), matching the other tools.
- [x] **R1.5** UTF-8 stdout guard (`sys.stdout.reconfigure`) like
      `make_wordcloud.py`, so non-ASCII titles never crash the Windows console.

✅ Also added `normalize_bitrate()` (accepts `64k` / `64000` / `64`), failed-run
handling (captures ffmpeg stderr, deletes any partial output, counts `failed`,
continues), and a per-file `human_size` line **`orig X MB -> new Y MB
(saved Z%)`** so the size drop is visible in the run output (no `dir` needed).

**Test (run):**
```cmd
c                              :: activate the learn-better env (ffmpeg lives here)
python code\reencode_audio.py  :: SELECT_BY="name", SELECT=["Git and GitHub"], BITRATE="64k"
```

**How this was actually tested (record for re-runs):**
1. **First run wrote the file.** Output:
   `audio_reencoded\Git and GitHub Tutorial for Beginners [tRZGeaHPoaw].64kbps.mp3`.
2. **Size check** — original vs. re-encoded (the script now prints this itself):
   - 64k run: ~63.6 MB original → **~9.96 MB** (first pass) — big drop.
   - 128k demo run: `orig 63.6 MB -> 128k 28.2 MB (saved 56%)`.
   (Exact MB varies with the source file; the point is the output is clearly
   smaller and scales with the chosen bitrate.)
3. **Actual bitrate check with ffprobe** (ships with ffmpeg, no extra install):
   ```cmd
   ffprobe -v error -show_entries format=bit_rate,duration -of default=noprint_wrappers=1 "audio_reencoded\Git and GitHub Tutorial for Beginners [tRZGeaHPoaw].64kbps.mp3"
   ```
   → reported `bit_rate=64000` and the duration matched the original (~2195s).
   The audio stream was `codec_name=mp3` with **no video stream** (cover art
   dropped by `-vn`).
4. **Originals untouched** — `audio\...mp3` kept its original size/mtime.
5. **Skip-if-exists** — a second `python code\reencode_audio.py` printed
   `= exists, skipping` and the tally `0 re-encoded, 1 skipped, 0 failed`.
6. **Different bitrate coexists** — running at `128k` wrote a separate
   `... .128kbps.mp3` next to the 64k one (proves the name pattern).
7. **Listen** — open the `.64kbps.mp3` in VLC / Windows Media Player / a browser;
   speech is clear. (Note: if a player has the file open, Windows locks it, so
   close the player before regenerating that exact file.)

**What to look for:** output plays; size dropped and scales with bitrate;
`ffprobe` bitrate ≈ target; no video stream; original unchanged; second run
skips.

---

## Phase R2 — Batch + selection + config (mirror transcribe_audio.py) — DONE, USER-VALIDATED

- [x] **R2.1** Selection like the Whisper tool: `SELECT_BY = "name" | "id" |
      "all"` over the `audio/` folder. `name` = case-insensitive substrings;
      `id` = 11-char `[<id>]` match; `all` = every audio file. Reuses the id
      regex from `make_wordcloud.py` (`\[([A-Za-z0-9_-]{11})\]`). Accepts the
      common audio extensions (`.mp3`, `.m4a`, `.webm`, `.opus`, `.ogg`, `.wav`).
      (Implemented in R1 already via `pick_audio` / `_audio_files`.)
- [x] **R2.2** Loops the R1 core over the selection with a written/skipped/failed
      tally (same reporting style as `process_transcript`). Prints each input,
      the target bitrate/format/codec, the output name, and the size-saved line.
- [x] **R2.3** JSON config `config/config_reencode.json` (schema above), loaded
      via an optional `argv[1]` path or auto-loaded if present — same
      `load_config` / `resolve_config_path` pattern as `make_wordcloud.py`
      (only present keys override; `_comment`/unknown keys ignored with a note).
- [x] **R2.4** `a.bat` runner: `a` (default config / in-file defaults) or
      `a config\config_reencode.json`. Mirrors `wc.bat`
      (`python code\reencode_audio.py %1`).

✅ Default `config/config_reencode.json` targets the Git clip at **96k mp3**
(96k chosen as a good speech default: clearly smaller than typical downloads,
better quality than 64k). `a.bat` created.

**How R2 was tested (record for re-runs):**
1. **Batch by id** — a config with `select_by:"id"`,
   `select:["F2DBSH2VoHQ","9llCMADxvzI"]`, `bitrate:"96k"`:
   ```cmd
   a config\config_reencode.json      :: (or an explicit id config)
   ```
   → `Selected 2 audio file(s) via SELECT_BY='id'`, both written to
   `audio_reencoded/*.96kbps.mp3`.
2. **ffprobe bitrate check** — both outputs reported `bit_rate=96003` (≈96k):
   - `How to use Git inside of VSCode - 2020 [F2DBSH2VoHQ].96kbps.mp3`
   - `What Is GitLab Pipeline？ ... [9llCMADxvzI].96kbps.mp3`
   The GitLab title contains fullwidth Unicode (`？`, `｜`); the script's UTF-8
   stdout guard handled it without error.
3. **Skip-if-exists (re-run)** — running the same config again printed
   `= exists, skipping` for both and the tally
   `0 re-encoded, 2 skipped, 0 failed`.
4. **Different bitrate coexists** — a 128k demo wrote `... .128kbps.mp3`
   alongside the 64k file (no collision), confirming the name pattern.

5. **`a` runner confirmed** — running plain `a` at the prompt uses
   `config\config_reencode.json` (Git clip @ 96k) and re-encodes as expected.

**What to look for:** the selection list matches (right count/files); tally line
like `2 re-encoded, 0 skipped, 0 failed`; a non-matching selection prints a
"nothing matched" message (not a crash); changing `bitrate` writes a new
`...<N>kbps.mp3` without clobbering earlier ones.

> **Gotcha (interactive prompt):** `::` is a `.bat` comment only at the START of
> a line. Do NOT type inline notes after the command, e.g. `a  :: uses config` —
> cmd passes `::` as `%1`, so the script reports `Config file not found: ::`.
> Just run `a` (or `a config\config_reencode.json`) with nothing after it.

---

## Phase R3 — Robustness + edge cases — DONE, VALIDATED

- [x] **R3.1** Missing ffmpeg → friendly message + install hints, exit cleanly
      (`find_ffmpeg` via `shutil.which`; `main` returns if None — no traceback).
      Verified by inspection (didn't tamper with PATH); the logic is a simple
      which-check + guarded return.
- [x] **R3.2** A failed ffmpeg run (bad codec/bitrate) → captures stderr, prints
      a one-line reason, counts it as `failed`, and **continues** the batch.
      Deletes any half-written output. ✅ Verified with `codec:"nonsuch_codec"`:
      `! failed: Unknown encoder 'nonsuch_codec'`, tally
      `0 re-encoded, 0 skipped, 1 failed`, and NO `77kbps.mp3` partial left in
      `audio_reencoded/`.
- [x] **R3.3** Empty `audio/` or no matches → clear message, exit 0. ✅ Verified
      with `select:["zzz_no_such_file_zzz"]`:
      `No audio matched SELECT_BY='name' SELECT=[...]  (looked in ...\audio\)`.
- [x] **R3.4** Validate `bitrate` (`normalize_bitrate` accepts `64k`/`64000`/`64`,
      rejects nonsense) AND `select_by` up front. ✅ Verified:
      `bitrate:"banana"` → `!! Invalid bitrate 'banana'. Use e.g. '64k', ...`;
      `select_by:"banana"` → `!! Invalid select_by 'banana'. Use one of: name |
      id | all.` Also guards an empty `select` list for name/id modes.

✅ Extra hardening added in R3: `main()` validates `SELECT_BY` (and non-empty
`SELECT` for name/id) before doing any work; `pick_audio`'s unknown-mode branch
now returns `False` instead of raising (no traceback).

**How R3 was tested (record for re-runs):** point `a` at a throwaway config in
`config/` for each case (delete it after):
```cmd
a config\<bad-bitrate>.json   :: bitrate "banana"   -> "!! Invalid bitrate ..."
a config\<bad-select>.json    :: select_by "banana" -> "!! Invalid select_by ..."
a config\<no-match>.json      :: select ["zzz..."]  -> "No audio matched ..."
a config\<bad-codec>.json     :: codec "nonsuch", a FRESH bitrate (e.g. 77k so it
                              ::   doesn't skip) -> "! failed: Unknown encoder ..."
                              ::   tally "... 1 failed", no partial file left
```
**What to look for:** each bad-input case prints a clear `!!` message and exits
without a Python traceback; the bad-codec run marks that file `failed` with
ffmpeg's reason, leaves no partial output, and still finishes with a tally.

---

## Phase R4 — Docs + wiring — DONE

- [x] **R4.1** `README.md`: added an "Audio re-encode / bitrate (`a.bat`)"
      section (what it does, `audio_reencoded/` output, the config keys, the
      ffmpeg-is-free-and-already-installed note, ffprobe check); added `a.bat` to
      the helper list and `reencode_audio.py` / `a.bat` / `audio_reencoded/` +
      `config_reencode.json` to the repo layout.
- [x] **R4.2** `how_to_test.md`: added a "Phase R" block (R1 one file, R2 batch,
      R3 failure cases) with commands + the ffprobe bitrate check and the `::`
      gotcha note; added `a` to the quick copy-paste examples, the "all runners"
      table, and a new "Audio re-encode config files" table.
- [x] **R4.3** `youtube.html`: added the `a` row to the "Running the tools"
      table; marked `todo` item 4 **Done** in "Implemented vs. remaining";
      updated the helper-batch-files row to `c/r/t/s/p/w/d/wc/a`; added
      `reencode_audio.py`, `audio_reencoded/`, `a.bat`, and `config_reencode.json`
      to the repo layout.
- [x] **R4.4** `plan.md`: ticked Phase 1's `audio_bitrate` box; added a
      `code/reencode_audio.py` row to the Section 1 status table; updated the
      "Remaining" row to (TTS) only; rewrote the Section 5 next-step (bitrate
      done → TTS is the clear next move).

**Test:** open `youtube.html` and `README.md`, confirm the new tool is listed and
`todo` item 4 shows Done; run through the `how_to_test.md` Phase R block.

---

## Suggested order of attack

| # | Task | Complexity | Test |
|---|------|-----------|------|
| 1 | R1 re-encode one file via ffmpeg | low | output plays, smaller, ffprobe ~target bitrate |
| 2 | R2 batch/selection + config + `a.bat` | med | one output per selected file, skip-if-exists |
| 3 | R3 robustness (missing ffmpeg, failures) | low-med | friendly errors, no partial files, batch continues |
| 4 | R4 docs + wiring | low | tool listed; item 4 marked Done |

Build top-to-bottom; each row should run green before the next.

---

## Notes / guardrails

- **Free only.** ffmpeg (already required) + stdlib `subprocess`/`shutil`. No new
  pip deps, no APIs, no paid services. Default codec `libmp3lame` is free and
  bundled with ffmpeg.
- **Never touch originals.** Always write to `audio_reencoded/`; treat `audio/`
  as read-only. Lower bitrate = lossy and irreversible.
- **No `shell=True`.** Use list-form `subprocess.run([...])` so titles with
  spaces, accents (fr/ro), and emoji don't break or invite injection.
- **Skip-if-exists** like every other tool; the bitrate is in the file name so
  re-runs at a new bitrate don't clobber previous ones.
- **Outputs are git-ignored** (`audio_reencoded/`), like `audio/` and the other
  regenerated artifacts.
- Keep the script's config style consistent with `transcribe_audio.py` /
  `make_wordcloud.py` (top-of-file config + optional JSON config in `config/` +
  one-letter batch runner).
```

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

## Phase R0 — Scope + prerequisites (no code) — TODO

- [ ] **R0.1** Confirm ffmpeg is the only dependency and it is already required
      (README "Install ffmpeg"). No new pip package, no `requirements.txt`
      change. Note the free codecs that ship with ffmpeg (libmp3lame, aac,
      libvorbis, libopus).
- [ ] **R0.2** Decide output folder `audio_reencoded/` and add
      `AUDIO_REENCODED_DIR = "audio_reencoded"` to `lib/paths.py`. Add it to
      `.gitignore` (like `audio/`).
- [ ] **R0.3** Decide the output name pattern: `<base>.<bitrate>.<ext>` where
      `<base>` is the input name minus its extension, `<bitrate>` is normalized
      (e.g. `64k` -> `64kbps`), `<ext>` from `format`. This makes different
      bitrates coexist and drives skip-if-exists.

**Test:** none (decisions only). Write them as config comments at the top of the
new script.

---

## Phase R1 — Re-encode ONE file (proof of concept) — TODO

- [ ] **R1.1** New script `code/reencode_audio.py`. Config block at top
      (same style as `transcribe_audio.py`): `SELECT_BY="name"`, `SELECT=[...]`,
      `BITRATE="64k"`, `FORMAT="mp3"`, `CODEC="libmp3lame"`, `SAMPLE_RATE=None`,
      `CHANNELS=None`. Make the repo root importable and `from lib import paths`.
- [ ] **R1.2** `find_ffmpeg()` — locate the ffmpeg binary via `shutil.which`
      (respects PATH and the active conda env). If missing, print a clear error
      with the install hints from README (`conda install -c conda-forge ffmpeg`,
      `winget install ffmpeg`, `brew install ffmpeg`, `apt install ffmpeg`) and
      abort — do NOT crash with a raw traceback.
- [ ] **R1.3** `reencode_one(src, bitrate, fmt, codec, ...)` — build the ffmpeg
      command and run it with `subprocess.run([...], check=False)` (list form, no
      `shell=True`, so titles with spaces/accents/emoji are safe). Command shape:
      `ffmpeg -hide_banner -loglevel error -y -i "<src>" -vn -c:a <codec> -b:a
      <bitrate> [-ar <sr>] [-ac <ch>] "<out>"`. `-vn` drops any cover-art video
      stream. Return True/False on the exit code.
- [ ] **R1.4** Output path via `paths.AUDIO_REENCODED_DIR` +
      `<base>.<bitrate>.<ext>`; create the folder if missing; **skip-if-exists**
      (print `= exists, skipping`), matching the other tools.
- [ ] **R1.5** UTF-8 stdout guard (`sys.stdout.reconfigure`) like
      `make_wordcloud.py`, so non-ASCII titles never crash the Windows console.

**Test:**
```cmd
python code\reencode_audio.py
```
With `SELECT_BY="name"`, `SELECT=["Git and GitHub"]`, `BITRATE="64k"`. Confirm
`audio_reencoded/Git and GitHub Tutorial for Beginners [tRZGeaHPoaw].64kbps.mp3`
exists and is **smaller** than the original. Run twice → second run skips.

**What to look for:**
- The output file plays in any player (VLC / browser / Windows Media Player).
- File size dropped roughly in proportion to the bitrate (a 64k mp3 is ~half a
  128k one for the same duration).
- Verify the actual bitrate: `ffprobe -v error -show_entries
  format=bit_rate -of default=noprint_wrappers=1 "audio_reencoded\...64kbps.mp3"`
  reports ~64000. (ffprobe ships with ffmpeg; no extra install.)
- No stray video stream in the output (cover art dropped by `-vn`).
- Original in `audio/` is untouched (same size/mtime).

---

## Phase R2 — Batch + selection + config (mirror transcribe_audio.py) — TODO

- [ ] **R2.1** Selection like the Whisper tool: `SELECT_BY = "name" | "id" |
      "all"` over the `audio/` folder. `name` = case-insensitive substrings;
      `id` = 11-char `[<id>]` match; `all` = every audio file. Reuse the id regex
      idea from `make_wordcloud.py` (`\[([A-Za-z0-9_-]{11})\]`). Accept the
      common audio extensions (`.mp3`, `.m4a`, `.webm`, `.opus`, `.ogg`, `.wav`).
- [ ] **R2.2** Loop the R1 core over the selection with a written/skipped/failed
      tally (same reporting style as `process_transcript`). Print each input,
      the target bitrate, and the output path.
- [ ] **R2.3** JSON config `config/config_reencode.json` (schema above), loaded
      via an optional `argv[1]` path or auto-loaded if present — same
      `load_config` / `resolve_config_path` pattern as `make_wordcloud.py`
      (only present keys override; `_comment`/unknown keys ignored with a note).
- [ ] **R2.4** `a.bat` runner: `a` (default config / in-file defaults) or
      `a config\config_reencode.json`. Mirror `wc.bat` (`python
      code\reencode_audio.py %1`).

**Test (batch by name):**
```cmd
a config\config_reencode.json
```
Confirm one re-encoded file per selected audio in `audio_reencoded/`, and that
re-running skips existing ones. Try `select_by:"id"` and `select_by:"all"`.

**What to look for:**
- The selection list printed matches what you expect (right count, right files).
- Tally line reads e.g. `2 re-encoded, 1 skipped, 0 failed`.
- A file with no matching selection prints a clear "nothing matched" message
  (not a crash), like the other tools.
- Changing `bitrate` to `128k` writes a NEW `...128kbps.mp3` alongside the 64k
  one (they don't collide), proving the name pattern works.

---

## Phase R3 — Robustness + edge cases — TODO

- [ ] **R3.1** Missing ffmpeg → friendly message + install hints, exit cleanly
      (covered in R1.2; verify by temporarily renaming ffmpeg or emptying PATH).
- [ ] **R3.2** A failed ffmpeg run (bad codec/bitrate) → capture stderr, print a
      one-line reason, count it as `failed`, and **continue** the batch instead
      of aborting. Do not leave a half-written output file (ffmpeg `-y` plus
      checking the exit code; delete a zero-byte/failed output if present).
- [ ] **R3.3** Empty `audio/` or no matches → clear message, exit 0.
- [ ] **R3.4** Validate `bitrate` looks like `\d+k` (or a plain integer);
      normalize `64k`/`64000`/`64` consistently for the file name and the
      `-b:a` flag. Reject nonsense with a readable error.

**Test:**
```cmd
:: 1) ffmpeg missing (simulate): rename it on PATH or run in a shell without it
a
:: 2) bad codec: set "codec":"nonsuch" in the config
a config\config_reencode.json
```
**What to look for:** case 1 prints the install hint and exits without a
traceback; case 2 marks that file `failed` with ffmpeg's reason, leaves no
partial output, and the run still finishes with a tally.

---

## Phase R4 — Docs + wiring — TODO

- [ ] **R4.1** `README.md`: add an "Audio re-encode / bitrate (`a.bat`)" section
      (what it does, `audio_reencoded/` output, the config keys, the ffmpeg note
      that it is free and already installed), add `a.bat` to the helper list and
      `reencode_audio.py` / `a.bat` / `audio_reencoded/` to the repo layout.
- [ ] **R4.2** `how_to_test.md`: add a "Phase R" block (R1 one file, R2 batch,
      R3 failure cases) with the exact commands and the ffprobe bitrate check;
      add `a` to the "all runners" table and a "Re-encode config files" table.
- [ ] **R4.3** `youtube.html`: add the tool to the "Running the tools" table
      (`a` row) and mark `todo` item 4 **Done** in the "Implemented vs.
      remaining" section (it is currently "To do"). Optional: a short
      "Audio re-encode" note/section.
- [ ] **R4.4** `plan.md`: tick Phase 1's `audio_bitrate` box (`[ ]` -> `[x]`),
      update the Section 1 status table (new `reencode_audio.py` row), and adjust
      the Section 5 "recommended next step" (item 2 done → TTS becomes the clear
      next move).

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

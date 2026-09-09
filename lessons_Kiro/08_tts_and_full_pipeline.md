# Lesson 08 — TTS + tidy outputs + full pipeline

**You'll build:** `code/generate_speech.py` (Piper — free, local, CPU
text-to-speech), `code/reencode_audio.py` (bitrate re-encode), the end-to-end
pipeline run, and a cross-cutting refactor that consolidates every output under a
single `data/` root — without ever destroying your inputs. Runners `v`, `a`.
**Complexity:** ⭐⭐⭐⭐⭐   **Est. time:** ~75–90 min

> **Assistant-agnostic.** Any AI assistant works.

---

## Prerequisites (from Lesson 07)

- Summaries in `data/summaries/`, transcripts on disk, audio in `data/audio/`.
- `lib/` + runners + config pattern established.

---

## Re-orient the AI (paste after a crash/restart)

```
Context: Lesson 08 of building a YouTube→study-material toolkit with your help.
OS: <your OS>. Repo: learn-better/ with the full tool set (download, transcribe,
summaries, wordcloud), lib/, runners, config pattern; outputs under data/.
Goal now: add generate_speech.py (Piper TTS → data/tts_output/) and
reencode_audio.py (→ data/audio_reencoded/); run the full pipeline; and do a
cross-cutting refactor so EVERY output lives under data/ (via lib/paths.py),
keeping data/summaries/ git-TRACKED. Never overwrite inputs.
Last thing done: <e.g. "wrote generate_speech.py">. Please continue from there.
```

---

## Concepts (what this lesson teaches about working with AI)

1. **Another free local engine, same pattern.** Piper mirrors the Whisper lesson:
   free, CPU-only, no API key, config-driven, skip-if-exists. Reusing the shape
   makes the assistant's job (and yours) predictable.
2. **Never destroy inputs.** Derived output goes to a *new* folder; source folders
   are read-only. Encode variant params (bitrate, voice) into output filenames so
   re-runs at different settings coexist.
3. **A cross-cutting refactor is about verified sameness.** Moving everything under
   `data/` touches many files — change the single source of truth (`lib/paths.py`)
   first, then verify each tool still reads/writes the right place.

---

## Step-by-step

### 08.1 — Text-to-speech with Piper

**Ask your assistant to** add a free, local TTS tool that voices a summary or
transcript.

> **Prompt:**
> "Create `code/generate_speech.py` using **Piper** (MIT, CPU-only, no API key,
> `pip install piper-tts`). Read a text source — a `data/summaries/*.summary.md`, a
> `data/transcripts/` caption file, or a `data/generated_transcripts/` Whisper file
> (paths from `lib/paths.py`) — strip Markdown, synthesize narration, and write a
> `.wav` to `data/tts_output/`. Config-driven (`select_by` name/id/all; `voice`;
> `length_scale` for speed; `format` wav/mp3). Encode voice + speed into the output
> filename so variants coexist. Skip-if-exists. First use downloads a small voice
> model into `data/tts_output/.voices/`. Add a `v` runner (`v.bat`+`v.sh`).
> Plan first, then code."

**Expected response:** a plan, then the tool + runner. Add `piper-tts` to
`requirements.txt` now (per-phase dep). Filenames should carry the voice/speed so
`... .en_US-lessac-medium.wav` and a `.s0.9.wav` variant don't collide.

**Verify:** `v` voices a summary; a `.wav` appears under `data/tts_output/`; a
second run skips it. Play it back or check duration with `ffprobe`.

### 08.2 — Audio re-encode (never touch the originals)

**Ask your assistant to** add a bitrate re-encoder that writes to a *separate*
folder.

> **Prompt:**
> "Create `code/reencode_audio.py`: re-encode files from `data/audio/` to a target
> bitrate via ffmpeg (free, already required — no new dep), writing to a SEPARATE
> `data/audio_reencoded/` so originals are never touched (re-encoding is lossy).
> Config-driven (`select_by` name/id/all; `bitrate`; `format`/`codec`). Name outputs
> `<name>.<bitrate>.<ext>` so bitrates coexist. Skip-if-exists; print an
> `original → new (saved %)` line and a written/skipped/failed tally; fail cleanly
> (capture ffmpeg stderr, delete partial output, continue). Add an `a` runner."

**Expected response:** the tool + `a` runner, writing only to
`data/audio_reencoded/`. Confirm it treats `data/audio/` as read-only.

**Verify:** `a config/config_reencode.json` produces a smaller file under
`data/audio_reencoded/`; the original in `data/audio/` is unchanged; a second run
skips.

### 08.3 — Run the whole pipeline end to end

**Ask your assistant to** give you the ordered sequence and a one-page cheat-sheet.

> **Prompt:**
> "Give me the end-to-end sequence to go from a YouTube source to narrated audio,
> using the runners: r (download) → w (transcribe if captions missing) → s (prep +
> I paste the instruction so you author summaries) → v (voice a summary). One line
> per step with what each produces under `data/`. Make it a cheat-sheet I can keep."

**Expected response:** a compact R→W→S→V cheat-sheet mapping each runner to its
`data/` output.

**Verify:** walk the sequence on one video; you end with a `.wav` narration of its
summary. That's the whole product working together.

### 08.4 — Consolidate every output under `data/` (cross-cutting refactor)

Outputs may have crept into a few root folders. Unify them under `data/` — a
refactor that touches many files, so do it *methodically*.

> **Prompt:**
> "Refactor so EVERY generated output lives under a single `data/` root:
> `data/audio/`, `data/audio_reencoded/`, `data/transcripts/`,
> `data/generated_transcripts/`, `data/tts_output/`, `data/wordclouds/`, and
> `data/summaries/`. Do it by (1) updating `lib/paths.py` (the single source of
> truth) FIRST so all tools follow; (2) grepping for any hard-coded output strings
> that don't go through `paths.*` and fixing those; (3) physically moving any
> existing outputs (move, never delete). Then verify each tool still reads/writes
> the right place and skip-if-exists still recognizes moved files. Change locations
> only — no behavior change."

**Expected response:** an updated `paths.py` + a short list of hard-coded strings it
fixed + a move plan. The method matters: **source of truth first, then verify
sameness** — the same discipline as Lesson 06, now for paths.

**Verify:** run each tool; outputs land under `data/…`, and skip-if-exists finds the
moved files (no re-downloading/re-transcribing). If anything regenerates, a path was
missed — feed it back.

### 08.5 — Keep `data/summaries/` tracked (the one subtlety)

**Ask your assistant to** set up the `.gitignore` so `data/` is ignored *except*
the authored summaries.

> **Prompt:**
> "In `.gitignore`, ignore the `data/` outputs but KEEP `data/summaries/` tracked
> (it's authored content, not regenerated). Use the contents-ignore + negation
> pattern (`data/*` + `!data/summaries/` + `!data/summaries/**`) — explain in one
> line why a blanket `data/` prune would block re-including a child. Verify with
> `git check-ignore`."

**Expected response:** the `data/*` + negation rules, with the explanation that a
wholesale `data/` ignore prevents re-including `data/summaries/`, so you ignore the
*contents* instead.

**Verify:** `git check-ignore data/audio/x.mp3` echoes it (ignored);
`git check-ignore data/summaries/foo.md` prints nothing (tracked). Add `piper-tts`
to `requirements.txt` if not already done.

---

## When the AI misbehaves

- **Piper API vs CLI drift.** `piper-tts` has shifted Python APIs across versions;
  its CLI is stabler. If imports fail, ask the assistant to confirm what's installed
  (`where piper`, list submodules) and prefer shelling out to the CLI over guessing
  the API.
- **The re-encoder writes over originals.** Unacceptable — insist outputs go only to
  `data/audio_reencoded/` and `data/audio/` is read-only.
- **The consolidation refactor regenerates files** (re-download/re-transcribe) or
  loses a tracked file. That's a behavior change — verify with `git status` (no
  tracked output vanished) and re-runs (skip-if-exists holds); feed back anything off.
- **Summaries get git-ignored by mistake.** The blanket-`data/` trap — switch to
  `data/*` + `!data/summaries/**` and re-check with `git check-ignore`.
- **A locked output file won't regenerate** (Windows). Close any media player
  holding the `.wav`/`.mp3` first.

---

## What you have now

```
learn-better/
├── code/  (+ generate_speech.py, reencode_audio.py)
├── v / a  runners (.bat + .sh)
├── requirements.txt  (+ piper-tts)
├── .gitignore  (data/* ignored EXCEPT data/summaries/)
└── data/
    ├── audio/ audio_reencoded/ transcripts/ generated_transcripts/
    ├── tts_output/  (+ .voices/)
    ├── wordclouds/
    └── summaries/    # TRACKED
```
The full pipeline runs end to end, every output lives under one `data/` root, and
your source files are never at risk.

---

## Next → Lesson 09 — Deploy, 1-click, CI + close the loop

The finale: make it reproducible everywhere (local / container / Colab /
Codespaces), add 1-click install badges and a Colab notebook, wire up light CI,
explain *why this isn't a web app*, and have the AI update the docs and link the
lessons — closing the loop.

# Lesson 05 — Whisper transcription (local speech-to-text)

**You'll build:** `code/transcribe_audio.py` using `faster-whisper` — free,
no-API-key, CPU-friendly speech-to-text for clips whose captions are disabled —
driven by the same config pattern, with a `w` runner.
**Complexity:** ⭐⭐⭐⭐   **Est. time:** ~60–90 min

> **Assistant-agnostic.** Any AI assistant works. This lesson adds a real ML
> dependency, so expect a first-run model download.

---

## Prerequisites (from Lesson 04)

- Working download tools + `lib/paths.py`; the `config/` + `select_by` pattern and
  one-letter runners in place.
- You have at least one audio file under `data/audio/` (from Lesson 02/04), ideally
  one whose YouTube captions are disabled.

---

## Re-orient the AI (paste after a crash/restart)

```
Context: Lesson 05 of building a YouTube→study-material toolkit with your help.
OS: <your OS>. Repo: learn-better/ with lib/paths.py, config-driven tools
(select_by/select), one-letter runners, and audio under data/audio/.
Goal now: add code/transcribe_audio.py using faster-whisper (local, no API key)
that transcribes selected audio → data/generated_transcripts/, config-driven,
skip-if-exists, with a w runner. Handle long runs and the first-run model download.
Last thing done: <e.g. "installed faster-whisper">. Please continue from there.
```

---

## Concepts (what this lesson teaches about working with AI)

1. **Add a dependency deliberately, per phase.** You add `faster-whisper` *now*,
   because this is the lesson that needs it — not speculatively earlier. Then it
   goes into `requirements.txt`.
2. **Validate a model's output, don't trust it.** ML output needs a quality check
   (you'll build a proper one in Lesson 06); for now, read a sample and sanity-check.
3. **Design for long, resumable runs.** Transcription is slow. Skip-if-exists turns
   a scary multi-minute job into something you can stop and resume safely.

---

## Step-by-step

### 05.1 — Add the dependency (and know why this one)

**Ask your assistant** which free, local, no-API-key engine fits, and how it
compares to alternatives, before installing.

> **Prompt:**
> "I need local, no-API-key speech-to-text for audio whose YouTube captions are
> disabled, running on CPU on `<your OS>`. Compare `faster-whisper` vs
> `openai-whisper` in 3–4 bullets (speed, CPU-friendliness, whether it can also
> translate). Recommend one and give the `pip install` line. Note it needs ffmpeg
> (already installed) and downloads model weights on first use."

**Expected response:** a recommendation of `faster-whisper` (CTranslate2 backend —
lighter/faster on CPU with `int8`, can also translate to English), plus
`pip install faster-whisper`. Then add it to `requirements.txt` (per-phase dep).

**Verify:** `python -c "import faster_whisper; print('OK')"` prints `OK`.

### 05.2 — Write the transcriber (config-driven, into `data/generated_transcripts/`)

**Ask your assistant to** write a tool that transcribes *selected* audio files and
names outputs after the audio file (not a generic name).

> **Prompt:**
> "Create `code/transcribe_audio.py` using faster-whisper. Read a config
> (`config/config_transcribe.json`, path optional as `sys.argv[1]`) with:
> `select_by` (`name` | `id` | `all`), `select` (list), `model_size` (default
> `base`), `device` (`cpu`), `compute_type` (`int8`), `task` (`transcribe` |
> `translate`), and `language` (or null to auto-detect). For each selected file in
> `data/audio/` (path from `lib/paths.py`), write
> `data/generated_transcripts/<audio base name>.whisper.<lang>.txt`. SKIP any that
> already exist. Load the model lazily (only if something actually needs it). Print
> a written/skipped tally. Plan first, then code."

**Expected response:** a plan, then the tool. Key details it should honor: output
name derived from the **audio file name** (not a hard-coded label), a
`data/generated_transcripts/` path via `paths.*`, and lazy model loading.

**Verify:** with a `select_by: "name"` config targeting one clip, run it; a
`.whisper.<lang>.txt` appears under `data/generated_transcripts/`. First run
downloads the model (can take a minute); subsequent runs are faster.

### 05.3 — Add config variants + the `w` runner

**Ask your assistant to** add a few ready-made configs and the runner pair.

> **Prompt:**
> "Add config variants in `config/`: one selecting by name substring, one by video
> id, one that sets `task=translate` (Whisper translates to English only), and one
> pinning `language` to `fr` (French → French). Then create the `w` runner pair
> (`w.bat` + `w.sh`) calling `transcribe_audio.py` and passing an optional config
> path through."

**Expected response:** `config/config_transcribe.name.json`,
`…id.json`, `…translate.json`, `…fr.json`, plus `w.bat`/`w.sh`. Note the honest
constraint: `task=translate` targets **English only** — it can't translate *into*
French/Romanian.

**Verify:** `w config/config_transcribe.id.json` transcribes the selected id;
`w config/config_transcribe.translate.json` produces a `.whisper.en.txt`.

### 05.4 — Long runs: stop, resume, and the GPU option

**Ask your assistant to** explain how to make a long batch safe to interrupt and
whether a GPU helps.

> **Prompt:**
> "Transcription on CPU is slow for big batches. Two questions: (1) how does
> skip-if-exists let me stop with Ctrl-C and resume without redoing finished
> files? (2) When would a GPU (e.g. a free Colab T4) help, and does faster-whisper
> use it automatically if present? Keep it short."

**Expected response:** skip-if-exists means a re-run only processes what's missing,
so interrupting is safe; a CUDA GPU speeds Whisper 5–10× and faster-whisper uses it
automatically when `device` allows and a GPU is present (you'll run this on Colab's
free T4 in Lesson 09).

**Verify:** start a batch, Ctrl-C partway, re-run — finished files are skipped, only
the rest run. That's your "long runs are safe" confidence.

### 05.5 — Sanity-check the output

**Ask your assistant to** help you eyeball quality now (a rigorous comparison comes
in Lesson 06).

> **Prompt:**
> "Open the generated `.whisper.en.txt` and the YouTube caption `.txt` for the same
> video and tell me, roughly, how close they are — ignoring timestamps and casing.
> Flag any obviously wrong words (domain terms like tool names often slip)."

**Expected response:** a rough read that they're close, with a note that cosmetic
slips (e.g. a product name split into two words) are normal at the `base` model size
and improve with a larger model or an `initial_prompt`.

**Verify:** the transcript is clearly the same content as the captions. Good enough
to proceed; Lesson 06 makes the comparison quantitative.

---

## When the AI misbehaves

- **`ModuleNotFoundError: faster_whisper` after installing.** Wrong interpreter
  again — `python -c "import sys; print(sys.executable)"` and confirm it's your env.
- **First run seems frozen.** It's downloading model weights (hundreds of MB). Wait;
  check the artifact folder for progress rather than trusting the console.
- **It hard-codes a generic output name** (e.g. `transcript.txt`). Insist the name
  derives from the *audio file name* so multiple clips don't overwrite each other.
- **It claims Whisper can translate into French/Romanian.** It can't — `translate`
  is English-only. Ask it to correct the config comments if it got this wrong.
- **A huge batch stalls or the machine gets hot.** Lower `model_size` to `base`,
  keep `compute_type=int8`, transcribe fewer files per run (skip-if-exists resumes),
  or move to a GPU in Lesson 09.

---

## What you have now

```
learn-better/
├── code/transcribe_audio.py          # faster-whisper, config-driven
├── config/config_transcribe*.json    # name / id / translate / fr variants
├── w.bat  w.sh                        # Whisper runner
└── data/generated_transcripts/        # <base>.whisper.<lang>.txt  (git-ignored)
```
Local speech-to-text that fills the gaps where YouTube captions are missing.

---

## Next → Lesson 06 — Runner system + PATH + reusable `lib/`

Two tools now share yt-dlp/cookie/path logic. Next you'll generate the *full*
runner set (all `.bat` + `.sh`) in one prompt, add `init.bat` + a PATH setup so the
one-letter names work from anywhere, extract shared logic into `lib/` **without
changing behavior**, and add a `compare_transcripts.py` quality check.

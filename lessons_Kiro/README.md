# Lessons — build this project with an AI assistant

A hands-on course that takes you from an **empty folder** to the full
`learn-better` repo — a set of free, no-API-key tools that turn YouTube content
into study material (audio, transcripts, summaries, word clouds, narrated audio).
You build it **by collaborating with an AI coding assistant** (Kiro, Claude, or
any other), learning *how to prompt, review, correct, and iterate* along the way.

> **Assistant-agnostic.** The lessons say "your AI assistant" and work with any
> harness. Each step gives a plain-language instruction *and* a ready-to-paste
> example prompt underneath. Tool-specific notes (Kiro, Claude, …) appear only as
> short optional asides.

## Who this is for

Someone comfortable with a terminal and basic Python, **new to building a real
project with an AI assistant.** No prior AI-pairing experience needed. This is not
an AI-internals course — the focus is the *workflow* of getting to working software.

## How to use it

- Work the lessons **in order** — each builds on the previous one's files.
- Every lesson is roughly **one focused session (~30–90 min)**.
- Every lesson has a **"Re-orient the AI"** block you can paste if your assistant
  loses context or you come back after a break, plus a **"When the AI misbehaves"**
  box for that lesson's likely snags.
- Prompts shown are the **optimized** versions (cleaner than a first attempt) — copy
  them, adapt the specifics, and check the **Verify** step before moving on.

> **Prefer a visual overview?** Open [`kiro_lessons.html`](kiro_lessons.html) — a
> single self-contained page with diagrams, per-lesson goal/prompt/check/output
> cards, and click-through navigation between all nine lessons.

## The lessons

| # | Lesson | You'll build | ⭐ | Time |
|---|--------|--------------|----|------|
| 01 | [First contact + a minimal setup](01_first_contact_and_setup.md) | An empty repo + a lightweight Python 3.12 + ffmpeg environment | ⭐ | ~30–45 min |
| 02 | [Your first working tool (early win)](02_first_working_tool.md) | A no-API-key script that downloads a YouTube clip's audio + transcript | ⭐⭐ | ~45–75 min |
| 03 | [Getting the environment right (properly)](03_environment_done_right.md) | `requirements.txt`, a solid `lib/paths.py`, a reproducible env | ⭐⭐ | ~45–60 min |
| 04 | [Playlists + transcripts, config-driven](04_playlists_and_transcripts.md) | `list_playlists.py`, `read_transcript.py`, `config/`, first runners | ⭐⭐⭐ | ~60–75 min |
| 05 | [Whisper transcription](05_whisper_transcription.md) | Local speech-to-text with `faster-whisper` | ⭐⭐⭐⭐ | ~60–90 min |
| 06 | [Runner system + PATH + reusable `lib/`](06_runners_and_lib.md) | The full runner set, `init.bat`, a shared `lib/`, a quality check | ⭐⭐⭐⭐ | ~60–90 min |
| 07 | [Summaries + word clouds (AI as author)](07_summaries_and_wordclouds.md) | `make_summaries.py` + `skill_summary.md`, `make_wordcloud.py` + `wordcloud.html` | ⭐⭐⭐⭐ | ~60–90 min |
| 08 | [TTS + tidy outputs + full pipeline](08_tts_and_full_pipeline.md) | Piper TTS, audio re-encode, the end-to-end pipeline under `data/` | ⭐⭐⭐⭐⭐ | ~75–90 min |
| 09 | [Deploy, 1-click, CI + close the loop](09_deploy_ci_handoff.md) | Dev Container, Colab notebook, CI, and linking it all together | ⭐⭐⭐⭐⭐ | ~75–90 min |

> A topic may split into an extra numbered lesson if it would otherwise cram too
> much into one sitting; the numbered sequence and even ramp are what matter.

## What each lesson teaches about *working with an AI* (not just the code)

The real subject is the collaboration workflow. Across the nine lessons you
practice, in rising difficulty:

- **01 — Framing & recovery:** frame a request (who/OS/goal/where), adopt the
  review mindset, and keep a paste-ready **Re-orient the AI** block for stalls.
- **02 — Iterate & fix:** get an early, concrete win, then the core skill —
  feed back the *exact* error, ask for a diagnosis before a patch, know when to
  change approach.
- **03 — Decide, don't default:** make the AI compare trade-offs; establish a
  single source of truth (`lib/paths.py`); pin dependencies.
- **04 — Config over code edits:** drive runs from JSON; reuse the source of
  truth; generate small runners.
- **05 — Add a dependency deliberately** (per phase) and **validate ML output**
  instead of trusting it; design for long, resumable runs.
- **06 — Behavior-preserving refactor** ("verify sameness"); generate repetitive
  files in one prompt; turn "seems fine" into a measured number.
- **07 — The script-vs-AI boundary:** deterministic work → a script, reasoning →
  the AI (authoring to a reusable skill file); data vs. presentation split.
- **08 — Never destroy inputs;** run the whole pipeline; do a cross-cutting
  refactor by changing the source of truth first, then verifying sameness.
- **09 — Reproducible-anywhere + CI as a safety net;** know when *not* to build
  something (why this isn't a web app); close the loop by keeping docs honest.

A consolidated **"Troubleshooting your AI"** recap of every failure mode (stalls,
interrupted writes, wrong interpreter, garbled terminal, bot-checks, over-
production, behavior-changing refactors, …) lives at the end of Lesson 09.

## A note on the two series

This is the **Kiro** lesson series (`lessons_Kiro/`). A parallel **Claude** series
may live alongside it (e.g. `lessons_claude/`). They teach the same journey from
their respective assistant's vantage point; either can be followed on its own.

## The end state

By the last lesson you'll have reproduced the real repo: `code/` tools, a reusable
`lib/`, config-driven runs, one-letter `scripts/` runners, outputs consolidated
under `data/`, deployment options (local / container / Colab / Codespaces), light
CI, and the docs that tie it together.

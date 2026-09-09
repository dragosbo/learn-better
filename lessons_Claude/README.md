# lessons_claude — Curriculum Index

A guided curriculum that walks a complete beginner — no AI-assistant experience, no existing
Python project — from an empty folder to the full working state of this repo.

Each lesson is one focused working session (~30–90 min). You use an AI coding assistant as your
primary tool throughout; the lessons are framed by *kind of AI task* (explanation, file creation,
debugging) and work with any assistant you have available.

---

## Lessons

| # | File | What you build |
|---|------|---------------|
| 01 | [01_first_contact.md](01_first_contact.md) | Orient yourself: what AI coding assistants do, how to give them good prompts, how to recover when they lose context |
| 02 | [02_project_scaffold.md](02_project_scaffold.md) | Project folder layout, `.gitignore`, first `README.md`, repo on GitHub |
| 03 | [03_environment_setup.md](03_environment_setup.md) | conda env, Python 3.12, ffmpeg, `requirements.txt`, `lib/paths.py` |
| 04 | [04_first_script.md](04_first_script.md) | `code/list_playlists.py` — first real script, first debugging rep ("iterate and fix") |
| 05 | [05_audio_and_transcripts.md](05_audio_and_transcripts.md) | `code/read_channel.py` + `code/read_transcript.py` — audio and caption download via yt-dlp |
| 06 | [06_whisper_transcription.md](06_whisper_transcription.md) | `code/transcribe_audio.py` — local speech-to-text with faster-whisper, config-driven modes |
| 07 | [07_runners_and_automation.md](07_runners_and_automation.md) | Full `scripts/` runner set, `init.bat`, `code/compare_transcripts.py` |
| 08 | [08_summaries_and_wordclouds.md](08_summaries_and_wordclouds.md) | `code/make_summaries.py`, `code/make_wordcloud.py`, `lib/textutil.py` — AI as author |
| 09 | [09_tts_and_full_pipeline.md](09_tts_and_full_pipeline.md) | `code/generate_speech.py`, `code/reencode_audio.py`, `lib/net.py`, `lib/youtube.py`, end-to-end run |
| 10 | [10_deployment_and_handoff.md](10_deployment_and_handoff.md) | devcontainer, Docker, CI, Colab notebook, deploy guidance in README, final handoff |

> **Note:** more than 10 lesson files is fine — if a lesson grows too complex it will be split
> (e.g. `10a_` + `10b_`). The table above will be updated accordingly.

---

## How to use these files

1. Read the lesson file from top to bottom before opening your AI assistant.
2. Use the **Re-orient the AI** block whenever you start a new session or the assistant loses context.
3. After each step, run the **Verify** command before moving on.
4. If something goes wrong, check the **When the AI misbehaves** section first.

---

## Lesson template

All lessons follow the structure in [`_template.md`](_template.md).

# Prompt-building — how summaries are produced

The summarization step (`s`) is the one place `learn-better` hands work to an AI.
This doc explains the logic behind it: how the prompt is built, why it's split
between a script and the AI, and how the output format is defined. If you want to
change *how* summaries read, this is the file to understand first.

---

## Why it's split (script + AI)

Analyzing a transcript and drafting clear prose is reasoning work a batch script
can't do well. But *deciding what needs summarizing* and *where the output goes*
is deterministic. So the step is split:

- **`code/make_summaries.py`** (deterministic) — finds transcripts, dedupes,
  checks what's already done, and **prints a ready-to-paste instruction**.
- **Kiro / any assistant** (reasoning) — reads each transcript and writes the
  summary, following a fixed skill file.

This keeps the AI's job small and repeatable: it's handed an exact instruction
and a format spec, not an open-ended "summarize this."

## The two-part prompt

What the assistant receives is effectively **instruction + format spec**:

1. **The generated instruction** (from `make_summaries.py`), e.g.:

   ```
   Apply skill_summary.md to these transcripts and save each to
   data/summaries/<base>.summary.md:
     - data/transcripts/Some Video [abc123].en.txt
     - data/generated_transcripts/Another Video [def456].whisper.en.txt
   ```

   This part is **data**: which files, where to write, and a pointer to the format.
   It's built from the real `data/` paths (via `lib/paths.py`), so the assistant
   always reads/writes the correct folders.

2. **`skill_summary.md`** (the format spec / reusable skill) — the *how*: the
   rules, tone, length target, and the exact Markdown template every summary must
   follow. This is the single source of truth for what a summary looks like.

Keeping the format in a committed file (not inline in the prompt) means every
summary comes out consistent, and changing the format is a one-file edit — no
need to re-word a prompt each time.

## What `skill_summary.md` encodes

The skill file (`skill_summary.md` at the repo root) defines:

- **Inputs** — a timestamped `.txt` transcript; timestamps anchor the table of
  contents but aren't copied line by line.
- **Output** — one Markdown file, `data/summaries/<base>.summary.md`, where
  `<base>` is the transcript name minus the `.<lang>.txt` suffix (so a caption and
  a Whisper transcript for the same video map to the **same** summary file — no
  duplicates).
- **Rules** — be concise; **ground everything in the transcript** (no invented
  facts, tools, or steps); neutral factual tone; keep commands in code formatting;
  target ~1 page (300–500 words) regardless of video length.
- **Template** — a fixed structure: title/metadata, one-line takeaway, a
  timestamped table of contents, per-section bullets, key takeaways, and
  **both** strengths and weaknesses (as a learning resource, not opinion about the
  presenter), plus "who should watch".
- **Checklist** — a pre-save check (right folder/name, real timestamps, sections
  map to real content, strengths + weaknesses both filled, ~1 page).

## Design principles behind the prompt

- **Deterministic where possible, AI only where needed.** The script decides the
  *what/where*; the AI does only the *writing*.
- **Format lives in a file, not the prompt.** One committed spec → consistent
  output and easy edits.
- **Grounding over generation.** The strongest rule is "don't invent" — summaries
  must trace back to the transcript, which keeps them trustworthy study material.
- **Idempotent.** Existing summaries are skipped; re-running only surfaces new
  transcripts. To regenerate one, delete its `data/summaries/*.summary.md`.
- **Structured for reuse.** The fixed template (ToC + sections + takeaways) is
  what makes a summary trivially convertible to a mindmap — see
  [`video_to_mindmap.md`](video_to_mindmap.md).

## Changing how summaries read

- **Tweak wording/tone/length or the template** → edit `skill_summary.md`. Every
  future summary follows the change; existing ones are untouched until regenerated.
- **Change which transcripts are picked or where output goes** → edit
  `code/make_summaries.py` (selection/dedupe) or the paths in `lib/paths.py`.
- **Remove the manual paste step** (optional, not built) → this would mean calling
  a local model or an API from a script instead of handing the instruction to
  Kiro. It's intentionally left manual for now (free, no API key, no heavy model);
  see `plan.md` Phase 2 for the open note.

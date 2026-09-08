# From a video to a mindmap — end-to-end walkthrough

This is the whole `learn-better` pipeline in one page: take a YouTube video (or a
playlist / channel / search) and end up with study material you can turn into a
mindmap or drop into Obsidian. Every step is free, local, and no-API-key.

> **Recorded video:** _(link to be added once recorded)_ — this doc is the
> written companion so you can follow along without it.

---

## The flow at a glance

```
YouTube ──▶ download ──▶ transcript ──▶ summary ──▶ mindmap / notes
            (r)          (t or w)       (s + Kiro)   (your tool)
```

| Step | Runner | Script | Output (under `data/`) |
|------|--------|--------|------------------------|
| 1. Download audio + captions | `r` | `read_channel.py` | `data/audio/`, `data/transcripts/` |
| 2. Transcript (captions or Whisper) | `t` / `w` | `read_transcript.py` / `transcribe_audio.py` | `data/transcripts/`, `data/generated_transcripts/` |
| 3. Prep + write summaries | `s` + Kiro | `make_summaries.py` | `data/summaries/*.summary.md` |
| 4. Mindmap / notes | — | your mindmap tool | your knowledge base |

> Runners live in `scripts/` — add it to PATH (or run `init.bat`) to type the
> one-letter names, or call `python code/<script>.py` directly. All outputs land
> under `data/` (see `lib/paths.py`).

---

## Step 1 — Download the source

Pick ONE source at the top of `code/read_channel.py` (`PLAYLIST_ID` / `CHANNEL` /
`SEARCH`, leave the others `None`) and set `LIMIT`. Then:

```cmd
r
```

This saves each clip's audio to `data/audio/` and its caption transcript to
`data/transcripts/`, skipping anything already present, and flags clips that have
no captions (`!! NO TRANSCRIPT`).

## Step 2 — Get a transcript for every clip

Most clips already have YouTube captions from step 1. For the caption-less ones
(the flagged clips), generate a transcript from the audio with local Whisper:

```cmd
w
```

`transcribe_audio.py` writes `data/generated_transcripts/<title> [<id>].whisper.<lang>.txt`.
Use `w config\config_transcribe.source.json` for the "captions-first, Whisper
fills the gaps" flow over a whole playlist/channel/search. (Whisper can also
translate to English or transcribe French/Romanian — see the
`config/config_transcribe.*.json` variants.)

## Step 3 — Summarize (the one AI-assisted step)

A batch script can't *write* a good summary — that's reasoning work — so this
step is split: `make_summaries.py` does the deterministic prep, and Kiro (the AI)
writes the prose following `skill_summary.md`.

```cmd
s
```

`make_summaries.py` finds every English transcript (captions preferred, Whisper
fills gaps, deduped by video id), checks which already have a
`data/summaries/<base>.summary.md`, and prints a **ready-to-paste instruction**
listing the ones that still need a summary, e.g.:

```
Apply skill_summary.md to these transcripts and save each to data/summaries/<base>.summary.md:
  - data/transcripts/Some Video [abc123].en.txt
  - data/generated_transcripts/Another Video [def456].whisper.en.txt
```

Paste that into Kiro. It reads each transcript and writes a structured summary
(table of contents, sections, key takeaways, strengths, weaknesses) per
`skill_summary.md`. Existing summaries are left alone, so re-running only surfaces
new transcripts. See [`prompt_building.md`](prompt_building.md) for how that
instruction and the summary format are constructed.

## Step 4 — Turn the summary into a mindmap

Each `data/summaries/*.summary.md` is already structured for this: its **table of
contents** becomes the top-level branches, and each **section's bullets** become
child nodes. A few free ways to render it:

- **Obsidian** — drop the summary into a vault; use the outline/graph view, or a
  mindmap plugin, to see the structure. Good for building a lasting knowledge base.
- **Markdown-to-mindmap tools** — e.g. [Markmap](https://markmap.js.org/) renders
  a Markdown outline as an interactive mindmap directly from the headings/bullets.
- **By hand** — the ToC + section bullets map 1:1 onto mindmap branches, so it's
  quick to sketch in any tool you like.

Because the summary is plain Markdown grounded in the transcript, it stays
renderer-agnostic — no lock-in to one mindmap app.

---

## Related material

- Word cloud of a transcript: `d` / `wc` → `data/wordclouds/*.word_cloud.json`,
  rendered by `wordcloud.html`. A quick visual companion to a summary.
- Narrate a summary back to audio: `v` → `data/tts_output/*.wav` (Piper TTS).
- Full tool reference + setup: the repo `README.md`.

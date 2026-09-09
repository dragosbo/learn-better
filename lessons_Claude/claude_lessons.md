# TODO6_v3 — Lessons Folder: Plan (round 3, feedback incorporated)

---

## Goal

Create a `lessons_claude/` folder at the repo root containing 10 or more lesson files that form a
guided curriculum: a complete beginner — no AI-assistant experience, no existing Python project —
is walked step by step from an empty folder to the full current state of this repo (working
scripts, config-driven pipeline, runner shortcuts, deployment options, documentation).

The lessons are written from the perspective of someone learning to use an AI coding assistant as
their primary tool — framed by *kind of task* (long-form explanation, multi-file creation/refactor,
debugging from an error message), not by any specific AI product. This is a *curated, optimized*
retelling of how this project was actually built — using insights already captured in `chats/`,
`skill_summary.md`, `skill_todo.md`, and the chat logs — not a verbatim transcript. Prompts shown
are the clean, improved versions; the artifacts they produce must match the real repo exactly (no
invented capabilities). Complexity and repo-coverage increase gradually and evenly across the
lessons.

**Note on lesson count:** 10 is the baseline. If a lesson would become too complex or dense, split
it — 11, 12, or more files is fine. The constraint is that each lesson represents roughly one
focused working session, not that the count stays at exactly 10.

**Are the lessons themselves planning documents?** Yes — each `lessons_claude/NN_*.md` file is the
equivalent of the `todo1`–`todo6` series: a detailed plan/spec for that lesson's content and
structure. They are the deliverable of this planning phase. Writing the actual learner-facing
lesson prose (the final published content) is a later step, and these plan files are what get
reviewed before that work begins.

**Free, no extra cost.** Pure Markdown authoring — no new dependency, no API key, no code changes
to the existing tools (one exception: a real `notebooks/colab_setup.ipynb` file, still just a
plain file, no paid service). The only other repo edits at the very end are doc links (README,
`youtube.html`) plus the `chats/` update.

---

## CLARIFICATION QUESTIONS

> **Status:** All questions below are answered. Q1–Q7 were resolved by the author in the round-3
> feedback pass. Q0 is a new question/suggestion added at the start of this revised plan for
> explicit confirmation before build begins.

**Q0 (new) — AI-task field in the lesson template: confirm the replacement label.**
The `**Which AI:**` field in the lesson template has been replaced with
`**AI tasks in this lesson:** <describe kind of work, not product name>` — e.g. "long-form
explanation", "multi-file creation", "debugging from an error message". This keeps the lessons
portable to any AI harness. *Please confirm this label wording before drafting begins, or suggest
an alternative.*

**Q1 — File naming: underscores or dashes?**
✅ **Answered: underscores.** Convention `01_first_contact.md`, matching `skill_summary.md` /
`skill_todo.md`.

**Q2 — Assistant framing.**
✅ **Answered: AI-agnostic / portable to any AI harness.** Lessons do not name or assume a
specific AI product. All assistant references describe the *kind of task* (long-form explanation,
multi-file creation/refactor, debugging from an error message), not the tool. Readers can use
whatever AI assistant they have available.

**Q3 — Lessons index page.**
✅ **Answered: yes.** Include `lessons_claude/README.md` as a self-contained index.

**Q4 — Historical fidelity vs. a clean arc.**
✅ **Answered: (a) smoothed, optimized path.** Present the clean arc to the same end state; do
not preserve real detours.

**Q5 — `how_to_deploy.md`: recreate it, or teach the current approach?**
✅ **Answered: (a) teach the current approach.** No separate `how_to_deploy.md` — deploy
guidance is folded into the README-update step in Lesson 10, matching the real repo (that file was
retired to `ignore/`).

**Q6 — Where does the `lib/` extraction happen?**
✅ **Answered: (b) spread across 07/08/09.** Each lib module is introduced next to the tool that
first needs it: `lib/textutil.py` in Lesson 08, `lib/net.py` + `lib/youtube.py` in Lesson 09.

**Q7 — Does Lesson 10 produce an actual Colab notebook file?**
✅ **Answered: yes.** `notebooks/colab_setup.ipynb` is a confirmed Lesson 10 deliverable.

> **Already settled by convergence (no question needed):** pacing — first working script lands in
> Lesson 04, with Lessons 01–03 as orientation/scaffold/environment (both drafts agree); "iterate
> and fix" is a named sub-section inside Lesson 04, not a standalone lesson; a consolidated
> troubleshooting recap appears in Lesson 10 in addition to per-lesson boxes; the Lesson 09/10
> boundary is TTS + full pipeline (09) then deploy + CI + handoff (10); archiving `todo5.md`,
> `todo6.md`, `todo5_v2.md`, `todo6_v2.md`, and this file to `ignore/` is deferred until the user
> confirms the finished series, per the `skill_todo.md` convention.

---

## Cross-cutting constraints

| Constraint | How it is handled |
|---|---|
| AI crashes / lost context | Each lesson opens with a "Re-orient the AI" prompt block the reader can paste after a restart to restore context cheaply. |
| Realistic failure modes, not just "crashes" | Assume the assistant doesn't regularly hard-crash, but cover the failure modes actually seen in this project's history: a response that stalls/goes silent (retry / "are you still working?"), an interrupted file write (verify the file wasn't corrupted before continuing), the assistant using the wrong Python interpreter/env (activate the env first; verify with `where python`), a tool run whose terminal output looks empty/garbled (check the produced artifact, not the console), and prompt/network hiccups (retry, re-state the goal). |
| Gradual complexity | Complexity and file count both increase monotonically; no lesson introduces more than 2–3 new concepts. |
| Even spread | Lessons are sized so each represents roughly one focused working session (30–90 min). |
| Optimised prompts | Prompts embed the lessons learned from `skill_summary.md` and the Kiro chat logs — e.g. always state the OS, always reference `lib/paths.py`, always ask for both `.bat` and `.sh` variants. |
| AI tool mix | Lessons are AI-agnostic. All assistant references describe the *kind of task* (long-form explanation, multi-file creation, debugging), not a specific product. Readers can use any AI assistant they have available. |
| Fidelity to the real project | Lessons land the reader on the real repo — real tools (`read_channel.py`, `transcribe_audio.py`, `make_wordcloud.py`, `generate_speech.py`, …), real runners, real `data/` layout, real docs. Never invent a capability the repo doesn't have. |
| File-length target | ~300–600 lines per lesson; if a lesson grows past that, split the content rather than expanding it. |
| Final handoff step | Lesson 10 ends with explicit AI tasks to update `chats/`, `README.md`, and `youtube.html` to link to the lessons. |

---

## Collaboration / build protocol

Don't batch all lessons in one shot. Once this plan is approved, work proceeds one phase at a
time:

1. **Implement only that phase.** Don't run ahead into later lessons.
2. **Draft, then hand back for review.** After writing a lesson (or the agreed small batch), stop.
3. **Give a clear review pointer every time** — which file to open, what it should teach, and how
   it connects to the previous/next lesson.
4. **Wait for feedback/go-ahead** before the next phase. If a lesson needs rework, fix it and
   re-issue the review before moving on.
5. **Only after confirmation**, mark that phase's checkbox done and proceed.

> **draft → point to what to review → wait → continue.**

---

## House style — the lesson template (merged)

Every lesson uses this structure — combining header fields (AI task kind, est. time, concepts)
with a consistent step format:

```
# Lesson NN — Title
**You'll build:** <one line: the concrete artifact/capability by the end>
**Complexity:** <⭐ to ⭐⭐⭐⭐⭐>   **Est. time:** <~30–90 min, one session>
**AI tasks in this lesson:** <describe kind of work, not product name — e.g. "long-form explanation", "multi-file creation", "debugging from an error message">

## Prerequisites (from previous lessons)
## Re-orient the AI (paste after a crash/restart)
   > 5–8 lines: repo name, current lesson, last file created, OS, env name,
   > "here's where we are, continue from X".
## Concepts (2–3 ideas this lesson teaches about working with AI)
## Step-by-step (numbered; each step ≈ one AI interaction)
   ### NN.x — <step title>
   **Prompt:** <exact, copy-pasteable text — the OPTIMIZED version>
   **Expected output:** <what a good AI answer/action looks like>
   **Verify:** <command or check that confirms success>
## When the AI misbehaves (2–3 failure modes specific to this lesson)
## What you have now (files added; repo state at end of lesson)
## Next → <link to the next lesson>
```

- **Length:** ~300–600 lines per lesson; split rather than expand if it grows past that.

---

## Folder & file naming

```
lessons_claude/
    01_first_contact.md
    02_project_scaffold.md
    03_environment_setup.md
    04_first_script.md
    05_audio_and_transcripts.md
    06_whisper_transcription.md
    07_runners_and_automation.md
    08_summaries_and_wordclouds.md
    09_tts_and_full_pipeline.md
    10_deployment_and_handoff.md
    README.md
```

*(Underscore naming convention confirmed by Q1. More than 10 lesson files is fine — add
`11_*.md`, `12_*.md`, etc. if a lesson needs splitting to keep complexity manageable.)*

---

## Lesson-by-lesson plan

### Lesson 01 — First Contact
**Theme:** What are AI coding assistants, and how do you use one to build a real project?

**Content:**
- Brief framing: what an AI coding assistant does — conversational explanation, file creation,
  multi-file refactoring, debugging from error output — and how to choose the right kind of
  request for each
- Setting up: get access to an AI assistant of your choice (browser-based or IDE-embedded);
  open an empty project folder
- First prompt exercise: ask the assistant to explain what `yt-dlp` does and why it is better
  than `pytube`
- First agentic exercise: ask the assistant to describe the empty folder and suggest a starting
  structure for the project
- Crash recovery: what to do when the assistant loses context mid-session (paste the re-orient
  block); what to do when a long agentic task stalls (use "continue" or re-state the goal); the
  fuller failure-mode list from the cross-cutting constraints table, applied for the first time here

**Files produced by learner:** none yet — orientation only

**Complexity:** ⭐☆☆☆☆

---

### Lesson 02 — Project Scaffold
**Theme:** Ask the AI to design and create the project structure.

**Content:**
- Prompt the assistant with the project vision ("I want to build a tool that downloads YouTube
  audio and transcripts, transcribes them locally with Whisper, and generates summaries — no API
  key required")
- Ask for a recommended folder layout, `.gitignore`, and a first `README.md`
- `git init` + first commit, pushed to GitHub (AI-guided)
- Introduce the concept of a living planning document (`plan.md`)
- Prompt pattern: "Think step by step. List the files you will create before creating them."

**Files produced:** `README.md`, `.gitignore`, `plan.md`, repo on GitHub

**Complexity:** ⭐⭐☆☆☆

---

### Lesson 03 — Environment Setup
**Theme:** Python, conda, ffmpeg — get the runtime right before writing any code.

**Content:**
- Ask the assistant to recommend an environment strategy (conda vs pip+venv vs uv) and why
- Guided conda setup: `conda create -n learn-better python=3.12`, install ffmpeg via conda-forge
- Why ffmpeg cannot be installed with pip (the #1 setup trap) — ask the assistant to explain it
- Create `requirements.txt` with assistant help; run `pip install -r requirements.txt`
- Verify checklist: `python --version`, `ffmpeg -version`, import smoke-test
- Introduce `lib/paths.py` as the canonical place for all output paths — ask the assistant to
  create it

**Files produced:** `requirements.txt`, `lib/paths.py`, conda env `learn-better`

**Complexity:** ⭐⭐☆☆☆

---

### Lesson 04 — First Working Script: Playlist Lister *(+ "iterate and fix")*
**Theme:** Write, run, and debug the first real script with AI.

**Content:**
- Ask the assistant (in the repo folder) to write `code/list_playlists.py` — list a channel's
  public playlists, save to `data/playlists.json`; reference `lib/paths.py` for the output path
- Prompt discipline: always tell the assistant the OS, the env name, and which file to write to
- Create the first runner pair: `scripts/p.bat` (Windows) and `scripts/p.sh` (Linux/macOS)
- **"When your first run doesn't work" (iterate and fix):** feed the actual error back to the
  assistant rather than describing it from memory; ask for a diagnosis before accepting a patch;
  recognize when the right move is "try a different approach" instead of another patch on the same
  approach. This is the reader's first real debugging-with-AI rep.
- Run it; read the output JSON; ask the assistant to explain any errors
- Introduce `data/` as the single output root; update `.gitignore` to ignore `data/*`

**Files produced:** `code/list_playlists.py`, `scripts/p.bat`, `scripts/p.sh`, `data/playlists.json`

**Complexity:** ⭐⭐⭐☆☆

---

### Lesson 05 — Audio Download & Transcript Fetching
**Theme:** yt-dlp in practice — audio files and caption transcripts.

**Content:**
- Ask the assistant to write `code/read_channel.py` (audio + transcripts for a channel) and
  `code/read_transcript.py` (transcripts only, per language) — both import from `lib/paths.py`
- Explain `yt-dlp[default,curl-cffi]` — why `curl_cffi` is required (bot-detection bypass);
  prompt the assistant to include this in a requirements note
- Config-driven design: introduce `config/` folder and a sample `config_transcribe.json`
- Output layout: `data/audio/`, `data/transcripts/`
- Common yt-dlp errors and how to ask the assistant to diagnose them (rate-limit, geo-block,
  empty subtitle response)
- Add runner pairs `r.bat`/`r.sh` and `t.bat`/`t.sh`

**Files produced:** `code/read_channel.py`, `code/read_transcript.py`,
`config/config_transcribe.json`, runners `r.*`, `t.*`

**Complexity:** ⭐⭐⭐☆☆

---

### Lesson 06 — Whisper Transcription
**Theme:** Local speech-to-text with faster-whisper; config-driven modes.

**Content:**
- Ask the assistant to write `code/transcribe_audio.py` using `faster-whisper`; accept a config
  JSON for model size, language, compute type
- Explain int8 CPU mode vs GPU (T4 in Colab); ask the assistant for a decision guide
- Config variants: `config_transcribe.id.json`, `config_transcribe.en.json`,
  `config_transcribe.en-translate.json`
- Output to `data/generated_transcripts/`
- Model cache location (`~/.cache/huggingface`) and how to override with `download_root`
- Crash recovery is especially important here: Whisper runs can be long; lesson shows how to
  resume from a partially transcribed batch
- Add runner `w.bat`/`w.sh`

**Files produced:** `code/transcribe_audio.py`, config variants, `scripts/w.*`

**Complexity:** ⭐⭐⭐⭐☆

---

### Lesson 07 — Automation: Full Runner System & PATH Setup
**Theme:** One-letter shortcuts; working from the repo root without typing full paths.

**Content:**
- Ask the assistant to generate the complete `scripts/` set: all runners × 2 formats
  (`.bat` + `.sh`) in a single prompt; show the prompt pattern that gets consistent output
- `init.bat`: ask the assistant to create a PATH-setup helper for Windows cmd; explain why it
  uses `%~dp0` not `%CD%`
- Linux/macOS equivalent: `export PATH="$PWD/scripts:$PATH"`; permanent via `.bashrc`/`.zshrc`
- Add `scripts/c.bat`/`c.sh` for conda env activation
- Prompt discipline: always ask for both platform variants in one prompt; always ask the assistant
  to verify the runner calls the correct script in `code/`
- Introduce `code/compare_transcripts.py` as a quality-check tool

**Files produced:** full `scripts/` set, `init.bat`, `code/compare_transcripts.py`

**Complexity:** ⭐⭐⭐⭐☆

---

### Lesson 08 — Summaries & Word Clouds
**Theme:** Text post-processing; AI-assisted batch tooling; the AI as author.

**Content:**
- Ask the assistant to write `code/make_summaries.py` — lists transcripts needing a summary,
  writes stubs to `data/summaries/` (the only git-tracked output)
- Name the script-vs-AI boundary explicitly here — the script finds *what* needs summarizing, the
  assistant *authors* the summary text itself, following a reusable skill file (`skill_summary.md`)
  with paste-ready instructions. This is the first lesson where the assistant is the author, not
  just the coder.
- Ask the assistant to write `code/make_wordcloud.py` — transcript → `data/wordclouds/` + a
  `wordcloud.html` viewer; config for batch/merge mode *(confirm the exact viewer filename against
  the repo at drafting time)*
- `lib/textutil.py`: ask the assistant to extract reusable text helpers (chunking, normalisation)
  into the lib here, next to the tool that needed them; prompt pattern: "Extract any logic used by
  more than one script into `lib/`. Show me the before and after."
- Add runners `s.*`, `d.*`, `wc.*`
- Introduce black + ruff for code quality; ask the assistant to set up a pre-commit style check

**Files produced:** `code/make_summaries.py`, `code/make_wordcloud.py`, `skill_summary.md`,
`lib/textutil.py`, `wordcloud.html`, runners `s.*`, `d.*`, `wc.*`

**Complexity:** ⭐⭐⭐⭐☆

---

### Lesson 09 — TTS & Full End-to-End Pipeline
**Theme:** Text-to-speech with Piper; audio re-encoding; running the complete pipeline.

**Content:**
- Ask the assistant to write `code/generate_speech.py` (Piper TTS — no API key, CPU-only);
  output to `data/tts_output/`
- Ask the assistant to write `code/reencode_audio.py`; config for bitrate; output to
  `data/audio_reencoded/`
- Add runners `v.*`, `a.*`
- Full pipeline exercise: R → W → S → V (download → transcribe → summarise → speak); ask the
  assistant to write a one-page cheat-sheet of the sequence
- Introduce `lib/net.py` and `lib/youtube.py` as the network/YouTube helpers here, next to the
  tools that need them; ask the assistant to document them
- `how_to_test.md`: ask the assistant to write a manual test playbook covering each runner

**Files produced:** `code/generate_speech.py`, `code/reencode_audio.py`, `lib/net.py`,
`lib/youtube.py`, `how_to_test.md`, runners `v.*`, `a.*`

**Complexity:** ⭐⭐⭐⭐⭐

---

### Lesson 10 — Deployment, CI & Final Handoff
**Theme:** Make it reproducible everywhere; document everything; close the loop.

**Content:**
1. **Devcontainer:** ask the assistant to write `.devcontainer/Dockerfile` and `devcontainer.json`;
   critical prompt: "ensure ffmpeg is installed as a system package — it cannot be installed with pip"
2. **Docker:** ask the assistant to write `Dockerfile.standalone` (non-root user,
   production-ready); explain the `-v $(pwd)/data:/app/data` mount pattern
3. **Deploy guidance:** fold all deployment guidance (Colab / Codespaces / local conda-pip-uv /
   Docker / Podman / devcontainer / Gitpod) into the README update in step 9 — no separate
   `how_to_deploy.md` is created, matching the real repo (that file was retired to `ignore/`).
4. **Colab notebook:** ask the assistant to produce an actual `notebooks/colab_setup.ipynb` the
   reader can open in one click, rather than only documenting the workflow in prose.
5. **CI:** ask the assistant to add a GitHub Actions workflow — lint (ruff + black) + network-free
   smoke test; explain why network-dependent tests are excluded
6. **Deno:** add the yt-dlp JS-runtime recommendation (`winget install DenoLand.Deno`)
7. **Why not a web host (Vercel):** a short, grounding explanation of why this project is a
   local/CLI tool pipeline with heavy local dependencies (ffmpeg, ML models) rather than a
   request/response web service — the reader should be able to repeat this reasoning.
8. **Consolidated troubleshooting recap:** a short "Troubleshooting your AI across all lessons"
   summary box before the final handoff tasks.
9. **Final AI tasks (end of lesson):**
   - Ask the assistant: "Update `chats/` with a summary of what was built in the lessons"
   - Ask the assistant: "Update `README.md` to include a 'Lessons' section with links and one-line
     descriptions for each lesson file; also fold in deployment guidance for Colab, Codespaces,
     local conda, Docker, and devcontainer"
   - Ask the assistant: "Update `youtube.html` to include a Lessons section with links to each
     `lessons_claude/*.md` file and a brief description of the curriculum"

**Files produced:** `.devcontainer/`, `Dockerfile.standalone`, `.github/workflows/ci.yml`,
`notebooks/colab_setup.ipynb`, README and `youtube.html` updated with lesson links

**Complexity:** ⭐⭐⭐⭐⭐

> **Ramp check:** 01–03 = orientation + scaffold + environment; 04 = first real script + first
> debugging rep; 05–06 = real download/transcription tooling + a real dependency (Whisper); 07 =
> automation/runners; 08 = AI-as-author + word clouds + `lib/textutil.py`; 09 = second engine
> (Piper) + full pipeline + `lib/net.py`/`lib/youtube.py`; 10 = deploy/CI + documentation/meta
> close-out. Complexity and repo-coverage rise evenly, with no single lesson dumping more than
> 2–3 new concepts.
>
> **Note on fidelity:** every tool/runner/path a lesson references must exist in the repo as it is
> today — no invented capabilities. Prompts are the clean/optimized versions; outcomes are real.

---

## Suggested order of attack

| # | Phase | Scope | Complexity | Review gate |
|---|-------|-------|-----------|-------------|
| 0 | Scaffold | Create `lessons_claude/` + shared template + `lessons_claude/README.md` | low | template + Q0 (AI-task field) confirmed |
| 1 | Lessons 01–02 | First Contact, Project Scaffold | low | beginner on-ramp reads well |
| 2 | Lesson 03 | Environment Setup | low | env/ffmpeg guidance accurate |
| 3 | Lesson 04 | First Script + iterate/fix sub-section | med | debugging rep lands well |
| 4 | Lessons 05–06 | Download/transcripts, Whisper STT | med | tool mechanics + dependency validation accurate |
| 5 | Lesson 07 | Runners & automation | med | runner generation prompt pattern works; `compare_transcripts.py` lands |
| 6 | Lesson 08 | Summaries & word clouds (AI-as-author) | med | script-vs-AI boundary + skill file land |
| 7 | Lesson 09 | TTS & full pipeline | high | second engine + end-to-end run accurate |
| 8 | Lesson 10 | Deployment, CI, handoff, troubleshooting recap | high | deploy/CI/Vercel-reasoning/Colab notebook all exact; deploy guidance folded into README |
| 9 | Consistency pass | Read all 10 end-to-end: ramp, template, cross-links, real paths/tools everywhere | med | series flows as one coherent course |
| 10 | Wire into docs | README "Lessons" section, `youtube.html` Lessons section/nav, `plan.md` note | low | links resolve, discoverable |
| 11 | Update `chats/` | Append new prompts + summarized exchanges | low | logs reflect the lessons work |
| 12 | Commit, push, archive | Commit to `main` only when asked; archive all planning docs to `ignore/` once confirmed | low | everything on `main`; planning docs retired |

Build top-to-bottom. The riskiest content is the middle (05–09), where the repo's real mechanics
must be described exactly — keep those closest to the source files while drafting.

---

## Implementation notes for the author

- **Prompt templates to embed in each lesson** should be drawn from the optimised patterns in
  `skill_summary.md` and the Kiro chat logs in `chats/`. Do not invent new patterns — distil what
  already worked.
- **Re-orient blocks** should be short (5–8 lines max) and include: repo name, current lesson
  number, last file created, OS being used, env name.
- **Crash/failure handling** is concentrated at the three highest-risk points: Lesson 01 (theory +
  first exposure), Lesson 06 (Whisper long-running jobs), and Lesson 10 (complex agentic,
  multi-file tasks) — plus the Lesson 04 debugging sub-section and the Lesson 10 consolidated
  recap.
- **AI-agnostic framing (per Q2/Q0):** describe all assistant work by *kind of task* — long-form
  explanation, multi-file creation, debugging from an error message — not by product name. The
  `**AI tasks in this lesson:**` header field captures this per-lesson. Never name a specific AI
  tool in lesson prose.
- **File length target:** each lesson 300–600 lines. If a lesson grows beyond that, split the
  content rather than expanding it.
- **Fidelity check before publishing each lesson:** cross-check every tool name, runner letter,
  and file path mentioned against the actual repo — no lesson should promise something the repo
  doesn't have. This applies in particular to the `wordcloud.html` filename (Lesson 08) — verify
  against the repo as it exists today before drafting.

---

## Guardrails / Notes

- **Plan only for now.** Do NOT begin writing lessons until this revised plan is approved.
- **Optimize the prompts, keep the outcomes real.** Prompts shown are the clean, improved
  versions; the artifacts they produce must match the repo as it exists today. Never invent
  capabilities.
- **Free + Markdown only**, except the one confirmed exception (a real Colab notebook file) — no
  other new deps, no API, no code changes to the existing tools. The only repo edits are the
  lessons themselves + doc links + the `chats/` update.
- **Even, gradual ramp.** Complexity and coverage rise smoothly lesson by lesson; no single lesson
  should dump half the project. More than 10 lessons is fine — split rather than expand.

- **"When the AI misbehaves" / "Troubleshooting" in every lesson**, plus the Lesson 10
  consolidated recap: short, realistic recovery guidance per the cross-cutting constraints table.
  Assume crashes are rare; teach graceful recovery anyway.
- **Commit to `main` only when the user asks** (this repo works straight on `main`, no branches);
  stage files by name.
- **Archive planning docs once the series is confirmed complete:** move `todo5.md`, `todo6.md`,
  `todo5_v2.md`, `todo6_v2.md`, and this file to `ignore/`, following the `skill_todo.md`
  convention — but only as a future step once the user gives the go-ahead; not part of the current
  task.

---

## Acceptance criteria

- [ ] This revised plan approved (Q0 confirmed)
- [ ] `lessons_claude/` folder exists at repo root with 10 or more files (underscore naming)
- [ ] `lessons_claude/README.md` index exists
- [ ] Each file follows the standard template (You'll build / Prerequisites / Re-orient /
      Concepts / Steps / When the AI misbehaves / What you have now / Next)
- [ ] Complexity increases monotonically from Lesson 01 (⭐) to the final lesson (⭐⭐⭐⭐⭐)
- [ ] Every lesson embeds at least one verbatim, copy-pasteable, **optimized** AI prompt
- [ ] Every lesson has a **Re-orient the AI** block plus a "When the AI misbehaves" box
- [ ] Every lesson describes its AI work by kind (per Q0/Q2), not by product name — using the
      `**AI tasks in this lesson:**` field
- [ ] Every referenced tool / path / runner actually exists in the repo (checked against real
      filenames, especially `wordcloud.html`)
- [ ] Lesson 04 includes the "iterate and fix" debugging sub-section
- [ ] Lesson 07 introduces `compare_transcripts.py`; `lib/textutil.py` lands in Lesson 08;
      `lib/net.py` / `lib/youtube.py` land in Lesson 09
- [ ] Lesson 08 explicitly names the script-vs-AI-author boundary and references `skill_summary.md`
- [ ] Lesson 10 includes the "why not Vercel" reasoning, the consolidated troubleshooting recap,
      the Colab notebook, and deploy guidance folded into the README update (no separate
      `how_to_deploy.md`)
- [ ] Lesson 10 ends with the three AI update tasks (chats, README, youtube.html)
- [ ] README and `youtube.html` both link to all lessons after Lesson 10 is complete
- [ ] Build proceeded phase-by-phase with a review gate at each step, per the collaboration
      protocol above — not written all at once
- [ ] Once confirmed complete, all planning docs (`todo5.md`, `todo6.md`, `todo5_v2.md`,
      `todo6_v2.md`, this file) archived to `ignore/`

---

*Round 3 revision of `todo6_v3.md` on 2026-09-09: incorporated author feedback — folder renamed
to `lessons_claude/`, assistant framing made AI-agnostic throughout, Q1–Q7 marked resolved, Q0
added, all conditional branches collapsed to the resolved paths (Q5=a, Q6=b, Q7=yes), lesson
count relaxed to 10 or more, preamble removed. Source files `todo5_v2.md`, `todo6_v2.md`,
`todo5.md`, `todo6.md` were not modified.*

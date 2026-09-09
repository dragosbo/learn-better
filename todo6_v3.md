# TODO6_v3 — Lessons Folder: Merged Plan (round 2)

> **Scope of this file:** This is the ONLY file touched while producing this merge. `todo5_v2.md`
> and `todo6_v2.md` were both read in full but left completely untouched, as were the original
> `todo5.md` / `todo6.md` beneath them. Everything below is a new, merged plan that reconciles the
> two second-round drafts — Kiro's `todo5_v2.md` and Claude's `todo6_v2.md` — into one.
>
> **Still plan only.** Do not start writing any `lessons/*.md` file until the open questions below
> are answered and the merged plan is approved.

---

## Goal

Create a `lessons/` folder at the repo root containing 10 lesson files that form a guided
curriculum: a complete beginner — no AI-assistant experience, no existing Python project — is
walked step by step from an empty folder to the full current state of this repo (working scripts,
config-driven pipeline, runner shortcuts, deployment options, documentation).

The lessons are written from the perspective of someone learning to use AI coding assistants
(Claude, Kiro) as their primary tool. This is a *curated, optimized* retelling of how this project
was actually built — using insights already captured in `chats/`, `skill_summary.md`,
`skill_todo.md`, and the Kiro chat logs — not a verbatim transcript. Prompts shown are the clean,
improved versions; the artifacts they produce must match the real repo exactly (no invented
capabilities). Complexity and repo-coverage increase gradually and evenly across the ten lessons.

**Free, no extra cost.** Pure Markdown authoring — no new dependency, no API key, no code changes
to the existing tools, with one possible exception pending Q7 below (a real Colab notebook file,
still just a plain file, no paid service). The only other repo edits at the very end are doc links
(README, `youtube.html`) plus the `chats/` update.

---

## CLARIFICATION QUESTIONS (please answer before build)

Both `todo5_v2.md` and `todo6_v2.md` had already independently converged on several of the round-1
open questions (see "Already settled by convergence" further below). What's left are the points
where the two second drafts still disagree, plus two new questions that only became visible once
`todo5_v2.md` existed. Please answer inline, or say "go with the recommendation" for any/all.

**Q1 — File naming: underscores or dashes?**
Both drafts recommend the underscore convention (`01_first_contact.md`), matching the existing
`skill_summary.md` / `skill_todo.md` naming already in the repo. Neither draft has actually locked
this — `todo5_v2.md` still lists it as "needs a decision." Given the independent convergence,
*recommendation: confirm underscore and close this out.*

**Q2 — Assistant framing: explicit split, and for one assistant or two?**
Both drafts now lean toward an explicit Kiro-vs-Claude division of labor (Claude for
research/explanation/long-form docs, Kiro for file creation/multi-file refactors) rather than
generic "your AI assistant" prose. `todo5_v2.md` raises a second, unresolved dimension: should the
lessons assume the reader has **both** Claude and Kiro available, or pick one **primary** assistant
and treat the other as optional? *No recommendation on the second part — please pick:*
- **(A)** Assume both are available; teach the division of labor as the default workflow
- **(B)** Pick one primary assistant (state which); mention the other only in asides

**Q3 — Lessons index page.**
Both drafts assume a `lessons/README.md` index (listing all 10 lessons with one-line purposes),
but neither has fully locked it. *Recommendation: yes — cheap to add, gives `lessons/` a
self-contained entry point mirroring how `chats/` and `config/` are self-describing.* Confirm or
override.

**Q4 — Historical fidelity vs. a clean arc.**
New in `todo5_v2.md`. The real project hit real detours (yt-dlp/scrapetube dead ends, refactors of
already-working scripts, etc.). Should the lessons (a) present the **smoothed, optimized path** to
the same end state — recommended, better teaching — or (b) preserve some of the real detours as
explicit teaching moments ("here's a wrong turn and how we noticed")? A light mix is possible.
*No recommendation on the exact balance — please confirm which way to lean.*

**Q5 — `how_to_deploy.md`: recreate it, or teach the current approach?**
This is a genuine conflict between the two drafts, not just an unlocked default. `todo6_v2.md`'s
Lesson 10 has the reader produce a full, deep-research `how_to_deploy.md` file. `todo5_v2.md`
flags that this file was **actually retired to `ignore/`** in the real repo (its content now lives
in `README.md`), and recommends the lessons teach the **current** state instead — no separate
deploy doc, deploy guidance folded into the README-update step. *Recommendation: follow
`todo5_v2.md` here for fidelity — (a) teach the current approach, not (b) recreate a file the real
repo no longer has.* Please confirm or override.

**Q6 — Where does the `lib/` extraction happen?**
New structural difference between the two drafts. `todo5_v2.md`'s Lesson 07 bundles *all* of the
`lib/` extraction (`net.py`, `textutil.py`, `youtube.py`) together with the runner system in one
lesson. `todo6_v2.md` spreads it out — `compare_transcripts.py` in Lesson 07, `lib/textutil.py` in
Lesson 08 (alongside summaries/word clouds), `lib/net.py` + `lib/youtube.py` in Lesson 09 (alongside
TTS/pipeline) — so each lib module is introduced next to the tool that first needed it. *No
recommendation — both are defensible. Please pick:*
- **(A)** Bundle all `lib/` extraction into Lesson 07, one focused "refactor to reusable core" lesson
- **(B)** Spread it across 07/08/09, introducing each module where it's first needed (current draft
  below uses this)

**Q7 — Does Lesson 10 produce an actual Colab notebook file?**
`todo5_v2.md` now explicitly lists `notebooks/colab_setup.ipynb` as a Lesson 10 deliverable, which
resolves the open question from `todo6_v2.md` in favor of "yes, produce it." *Recommendation:
confirm this and treat it as settled* — flagged here only because it's a small scope increase (a
new file type) worth an explicit nod before Lesson 10 is drafted.

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
| Realistic failure modes, not just "crashes" | Assume Kiro/Claude don't regularly hard-crash, but cover the failure modes actually seen in this project's history: a response that stalls/goes silent (retry / "are you still working?"), an interrupted file write (verify the file wasn't corrupted before continuing), the assistant using the wrong Python interpreter/env (activate the env first; verify with `where python`), a tool run whose terminal output looks empty/garbled (check the produced artifact, not the console), and prompt/network hiccups (retry, re-state the goal). |
| Gradual complexity | Complexity and file count both increase monotonically; no lesson introduces more than 2–3 new concepts. |
| Even spread | Lessons are sized so each represents roughly one focused working session (30–90 min). |
| Optimised prompts | Prompts embed the lessons learned from `skill_summary.md` and the Kiro chat logs — e.g. always state the OS, always reference `lib/paths.py`, always ask for both `.bat` and `.sh` variants. |
| AI tool mix | *(Depends on Q2.)* Drafted below assuming both assistants are available, with an explicit division of labor. |
| Fidelity to the real project | Lessons land the reader on the real repo — real tools (`read_channel.py`, `transcribe_audio.py`, `make_wordcloud.py`, `generate_speech.py`, …), real runners, real `data/` layout, real docs. Never invent a capability the repo doesn't have. |
| File-length target | ~300–600 lines per lesson; if a lesson grows past that, split the content rather than expanding it. |
| Final handoff step | Lesson 10 ends with explicit AI tasks to update `chats/`, `README.md`, and `youtube.html` to link to the lessons. |

---

## Collaboration / build protocol

Both drafts agree: don't batch all ten lessons in one shot. Once this plan is approved, work
proceeds one phase at a time:

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

Every lesson uses this structure — combining `todo5_v2`'s header fields (which AI, est. time,
concepts) with `todo6_v2`'s step format:

```
# Lesson NN — Title
**You'll build:** <one line: the concrete artifact/capability by the end>
**Complexity:** <⭐ to ⭐⭐⭐⭐⭐>   **Est. time:** <~30–90 min, one session>
**Which AI:** <Claude for X / Kiro for Y, per the division of labor — pending Q2>

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
lessons/
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
    README.md                      ← pending Q3 confirmation
```

*(Naming shown uses the Q1-recommended underscore convention; flips to dashes if you override.)*

---

## Lesson-by-lesson plan

### Lesson 01 — First Contact
**Theme:** What are AI coding assistants? How do Kiro and Claude differ? *(Framing per Q2.)*

**Content:**
- Brief positioning: Claude = conversational / browser / multi-turn; Kiro = IDE-embedded /
  agentic / file-aware
- Setting up: Claude.ai account (free tier sufficient); AWS Builder ID for Kiro; VS Code + Kiro
  extension
- First prompt exercise: ask Claude to explain what `yt-dlp` does and why it is better than
  `pytube`
- First Kiro exercise: open an empty folder in VS Code, ask Kiro to describe what it sees
- Crash recovery: what to do when Claude loses context mid-session (paste the re-orient block);
  what to do when Kiro's agent loop times out (use "continue" or re-state goal); the fuller
  failure-mode list from the cross-cutting constraints table, applied for the first time here

**Files produced by learner:** none yet — orientation only

**Complexity:** ⭐☆☆☆☆

---

### Lesson 02 — Project Scaffold
**Theme:** Ask the AI to design and create the project structure.

**Content:**
- Prompt Claude with the project vision ("I want to build a tool that downloads YouTube audio and
  transcripts, transcribes them locally with Whisper, and generates summaries — no API key
  required")
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
- Ask AI to recommend an environment strategy (conda vs pip+venv vs uv) and why
- Guided conda setup: `conda create -n learn-better python=3.12`, install ffmpeg via conda-forge
- Why ffmpeg cannot be installed with pip (the #1 setup trap) — ask the AI to explain it
- Create `requirements.txt` with AI help; run `pip install -r requirements.txt`
- Verify checklist: `python --version`, `ffmpeg -version`, import smoke-test
- Introduce `lib/paths.py` as the canonical place for all output paths — ask AI to create it

**Files produced:** `requirements.txt`, `lib/paths.py`, conda env `learn-better`

**Complexity:** ⭐⭐☆☆☆

---

### Lesson 04 — First Working Script: Playlist Lister *(+ "iterate and fix")*
**Theme:** Write, run, and debug the first real script with AI.

**Content:**
- Ask Kiro (in the repo folder) to write `code/list_playlists.py` — list a channel's public
  playlists, save to `data/playlists.json`; reference `lib/paths.py` for the output path
- Prompt discipline: always tell the AI the OS, the env name, and which file to write to
- Create the first runner pair: `scripts/p.bat` (Windows) and `scripts/p.sh` (Linux/macOS)
- **"When your first run doesn't work" (iterate and fix):** feed the actual error back to the AI
  rather than describing it from memory; ask for a diagnosis before accepting a patch; recognize
  when the right move is "try a different approach" instead of another patch on the same
  approach. This is the reader's first real debugging-with-AI rep.
- Run it; read the output JSON; ask the AI to explain any errors
- Introduce `data/` as the single output root; update `.gitignore` to ignore `data/*`

**Files produced:** `code/list_playlists.py`, `scripts/p.bat`, `scripts/p.sh`, `data/playlists.json`

**Complexity:** ⭐⭐⭐☆☆

---

### Lesson 05 — Audio Download & Transcript Fetching
**Theme:** yt-dlp in practice — audio files and caption transcripts.

**Content:**
- Ask AI to write `code/read_channel.py` (audio + transcripts for a channel) and
  `code/read_transcript.py` (transcripts only, per language) — both import from `lib/paths.py`
- Explain `yt-dlp[default,curl-cffi]` — why `curl_cffi` is required (bot-detection bypass);
  prompt the AI to include this in a requirements note
- Config-driven design: introduce `config/` folder and a sample `config_transcribe.json`
- Output layout: `data/audio/`, `data/transcripts/`
- Common yt-dlp errors and how to ask the AI to diagnose them (rate-limit, geo-block, empty
  subtitle response)
- Add runner pairs `r.bat`/`r.sh` and `t.bat`/`t.sh`

**Files produced:** `code/read_channel.py`, `code/read_transcript.py`,
`config/config_transcribe.json`, runners `r.*`, `t.*`

**Complexity:** ⭐⭐⭐☆☆

---

### Lesson 06 — Whisper Transcription
**Theme:** Local speech-to-text with faster-whisper; config-driven modes.

**Content:**
- Ask AI to write `code/transcribe_audio.py` using `faster-whisper`; accept a config JSON for
  model size, language, compute type
- Explain int8 CPU mode vs GPU (T4 in Colab); ask AI for a decision guide
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

### Lesson 07 — Automation: Full Runner System & PATH Setup *(lib/ scope pending Q6)*
**Theme:** One-letter shortcuts; working from the repo root without typing full paths.

**Content:**
- Ask AI (Kiro) to generate the complete `scripts/` set: all runners × 2 formats (`.bat` + `.sh`)
  in a single prompt; show the prompt pattern that gets consistent output
- `init.bat`: ask AI to create a PATH-setup helper for Windows cmd; explain why it uses `%~dp0`
  not `%CD%`
- Linux/macOS equivalent: `export PATH="$PWD/scripts:$PATH"`; permanent via `.bashrc`/`.zshrc`
- Add `scripts/c.bat`/`c.sh` for conda env activation
- Prompt discipline: always ask for both platform variants in one prompt; always ask AI to verify
  the runner calls the correct script in `code/`
- Introduce `code/compare_transcripts.py` as a quality-check tool
- *(If Q6 = A):* also extract `lib/net.py`, `lib/textutil.py`, and `lib/youtube.py` here as one
  combined "refactor to a reusable core" step — prompt pattern: "Extract any logic used by more
  than one script into `lib/`. Show me the before and after — verify the behavior is unchanged."
  *(If Q6 = B, the current default): only `compare_transcripts.py` lands here; `lib/textutil.py`
  moves to Lesson 08 and `lib/net.py` / `lib/youtube.py` move to Lesson 09, each next to the tool
  that first needs it.*

**Files produced:** full `scripts/` set, `init.bat`, `code/compare_transcripts.py`
*(+ all of `lib/` if Q6 = A)*

**Complexity:** ⭐⭐⭐⭐☆

---

### Lesson 08 — Summaries & Word Clouds
**Theme:** Text post-processing; AI-assisted batch tooling; the AI as author.

**Content:**
- Ask AI to write `code/make_summaries.py` — lists transcripts needing a summary, writes stubs to
  `data/summaries/` (the only git-tracked output)
- Name the script-vs-AI boundary explicitly here — the script finds *what* needs summarizing, the
  AI *authors* the summary text itself, following a reusable skill file (`skill_summary.md`) with
  paste-ready instructions. This is the first lesson where the AI is the author, not just the coder.
- Ask AI to write `code/make_wordcloud.py` — transcript → `data/wordclouds/` + a `wordcloud.html`
  viewer; config for batch/merge mode *(confirm the exact viewer filename against the repo at
  drafting time)*
- *(If Q6 = B, current default):* `lib/textutil.py`: ask AI to extract reusable text helpers
  (chunking, normalisation) into the lib here, next to the tool that needed them; prompt pattern:
  "Extract any logic used by more than one script into `lib/`. Show me the before and after."
- Add runners `s.*`, `d.*`, `wc.*`
- Introduce black + ruff for code quality; ask AI to set up a pre-commit style check

**Files produced:** `code/make_summaries.py`, `code/make_wordcloud.py`, `skill_summary.md`,
`wordcloud.html` *(+ `lib/textutil.py` if Q6 = B)*, runners `s.*`, `d.*`, `wc.*`

**Complexity:** ⭐⭐⭐⭐☆

---

### Lesson 09 — TTS & Full End-to-End Pipeline
**Theme:** Text-to-speech with Piper; audio re-encoding; running the complete pipeline.

**Content:**
- Ask AI to write `code/generate_speech.py` (Piper TTS — no API key, CPU-only); output to
  `data/tts_output/`
- Ask AI to write `code/reencode_audio.py`; config for bitrate; output to `data/audio_reencoded/`
- Add runners `v.*`, `a.*`
- Full pipeline exercise: R → W → S → V (download → transcribe → summarise → speak); ask AI to
  write a one-page cheat-sheet of the sequence
- *(If Q6 = B, current default):* introduce `lib/net.py` and `lib/youtube.py` as the network/
  YouTube helpers here; ask AI to document them
- `how_to_test.md`: ask AI to write a manual test playbook covering each runner

**Files produced:** `code/generate_speech.py`, `code/reencode_audio.py`
*(+ `lib/net.py`, `lib/youtube.py` if Q6 = B)*, `how_to_test.md`, runners `v.*`, `a.*`

**Complexity:** ⭐⭐⭐⭐⭐

---

### Lesson 10 — Deployment, CI & Final Handoff
**Theme:** Make it reproducible everywhere; document everything; close the loop.

**Content:**
1. **Devcontainer:** ask AI to write `.devcontainer/Dockerfile` and `devcontainer.json`; critical
   prompt: "ensure ffmpeg is installed as a system package — it cannot be installed with pip"
2. **Docker:** ask AI to write `Dockerfile.standalone` (non-root user, production-ready); explain
   the `-v $(pwd)/data:/app/data` mount pattern
3. **Deploy guidance** *(per Q5)*: if Q5 = "teach current approach" (recommended), fold deploy
   guidance for Colab / Codespaces / local conda-pip-uv / Docker / Podman / devcontainer / Gitpod
   into the README update in step 9 below — no separate `how_to_deploy.md` is created, matching
   the real repo (that file was retired to `ignore/`). If Q5 = "recreate `how_to_deploy.md`",
   instead ask AI for a deep-research deployment guide as its own file, with a complexity ranking
   table, OS badges, and image scripts.
4. **Colab notebook** *(per Q7 — now the default)*: ask AI to produce an actual
   `notebooks/colab_setup.ipynb` the reader can open in one click, rather than only documenting
   the workflow in prose.
5. **CI:** ask AI to add a GitHub Actions workflow — lint (ruff + black) + network-free smoke
   test; explain why network-dependent tests are excluded
6. **Deno:** add the yt-dlp JS-runtime recommendation (`winget install DenoLand.Deno`)
7. **Why not a web host (Vercel):** a short, grounding explanation of why this project is a
   local/CLI tool pipeline with heavy local dependencies (ffmpeg, ML models) rather than a
   request/response web service — the reader should be able to repeat this reasoning.
8. **Consolidated troubleshooting recap:** a short "Troubleshooting your AI across all 10 lessons"
   summary box before the final handoff tasks.
9. **Final AI tasks (end of lesson):**
   - Ask AI: "Update `chats/` with a summary of what was built in lessons 01–10"
   - Ask AI: "Update `README.md` to include a 'Lessons' section with links and one-line
     descriptions for each lesson file" *(and, if Q5 = current-approach, fold deploy guidance in
     here rather than a separate file)*
   - Ask AI: "Update `youtube.html` to include a Lessons section with links to each
     `lessons/*.md` file and a brief description of the curriculum"

**Files produced:** `.devcontainer/`, `Dockerfile.standalone`, `.github/workflows/ci.yml`,
`notebooks/colab_setup.ipynb`, *(`how_to_deploy.md` only if Q5 overrides the recommendation)*,
README and `youtube.html` updated with lesson links

**Complexity:** ⭐⭐⭐⭐⭐

> **Ramp check:** 01–03 = orientation + scaffold + environment; 04 = first real script + first
> debugging rep; 05–06 = real download/transcription tooling + a real dependency (Whisper); 07 =
> automation/runners (+ possibly the `lib/` refactor); 08 = AI-as-author + word clouds (+ possibly
> `lib/textutil.py`); 09 = second engine (Piper) + full pipeline (+ possibly `lib/net.py`/
> `lib/youtube.py`); 10 = deploy/CI + documentation/meta close-out. Complexity and repo-coverage
> rise evenly, with no single lesson dumping more than 2–3 new concepts.
>
> **Note on fidelity:** every tool/runner/path a lesson references must exist in the repo as it is
> today — no invented capabilities. Prompts are the clean/optimized versions; outcomes are real.

---

## Suggested order of attack

| # | Phase | Scope | Complexity | Review gate |
|---|-------|-------|-----------|-------------|
| 0 | Decide + scaffold | Lock Q1–Q7, create `lessons/` + shared template (+ `lessons/README.md` if Q3 = yes) | low | decisions + template confirmed |
| 1 | Lessons 01–02 | First Contact, Project Scaffold | low | beginner on-ramp reads well |
| 2 | Lesson 03 | Environment Setup | low | env/ffmpeg guidance accurate |
| 3 | Lesson 04 | First Script + iterate/fix sub-section | med | debugging rep lands well |
| 4 | Lessons 05–06 | Download/transcripts, Whisper STT | med | tool mechanics + dependency validation accurate |
| 5 | Lesson 07 | Runners & automation (+ `lib/` per Q6) | med | runner generation prompt pattern works; lib scope matches Q6 |
| 6 | Lesson 08 | Summaries & word clouds (AI-as-author) | med | script-vs-AI boundary + skill file land |
| 7 | Lesson 09 | TTS & full pipeline | high | second engine + end-to-end run accurate |
| 8 | Lesson 10 | Deployment, CI, handoff, troubleshooting recap | high | deploy/CI/Vercel-reasoning/Colab/how_to_deploy.md decision all exact |
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
- **Kiro vs Claude split** *(scope per Q2)*: use Claude for research/explanation prompts and
  long-form docs; use Kiro for file-creation and multi-file refactoring inside the IDE.
- **File length target:** each lesson 300–600 lines. If a lesson grows beyond that, split the
  content rather than expanding it.
- **Fidelity check before publishing each lesson:** cross-check every tool name, runner letter,
  and file path mentioned against the actual repo — no lesson should promise something the repo
  doesn't have. This applies in particular to the `wordcloud.html` filename (Lesson 08) and the
  final state of `how_to_deploy.md` (Lesson 10, per Q5) — verify both against the repo as it
  exists today before drafting.

---

## Guardrails / Notes

- **Plan only for now.** Do NOT begin writing lessons until Q1–Q7 are answered and the merged plan
  is approved.
- **Optimize the prompts, keep the outcomes real.** Prompts shown are the clean, improved
  versions; the artifacts they produce must match the repo as it exists today. Never invent
  capabilities.
- **Free + Markdown only**, except the one thing confirmed by Q7 (a real Colab notebook file) — no
  other new deps, no API, no code changes to the existing tools. The only repo edits are the
  lessons themselves + doc links + the `chats/` update.
- **Even, gradual ramp.** Complexity and coverage rise smoothly 01→10; no single lesson should
  dump half the project.
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

- [ ] Q1–Q7 above answered / confirmed
- [ ] `lessons/` folder exists at repo root with 10 files (naming per Q1)
- [ ] `lessons/README.md` index exists, if Q3 = yes
- [ ] Each file follows the standard template (You'll build / Prerequisites / Re-orient /
      Concepts / Steps / When the AI misbehaves / What you have now / Next)
- [ ] Complexity increases monotonically from Lesson 01 (⭐) to Lesson 10 (⭐⭐⭐⭐⭐)
- [ ] Every lesson embeds at least one verbatim, copy-pasteable, **optimized** AI prompt
- [ ] Every lesson has a **Re-orient the AI** block plus a "When the AI misbehaves" box
- [ ] Every lesson names **which AI** fits its steps (per Q2)
- [ ] Every referenced tool / path / runner actually exists in the repo (checked against real
      filenames, especially `wordcloud.html` and the Q5 outcome for `how_to_deploy.md`)
- [ ] Lesson 04 includes the "iterate and fix" debugging sub-section
- [ ] Lesson 07/08/09 place the `lib/` extraction consistently with the Q6 answer
- [ ] Lesson 08 explicitly names the script-vs-AI-author boundary and references `skill_summary.md`
- [ ] Lesson 10 includes the "why not Vercel" reasoning, the consolidated troubleshooting recap,
      the Colab notebook (Q7), and the correct treatment of deploy docs (Q5)
- [ ] Lesson 10 ends with the three AI update tasks (chats, README, youtube.html)
- [ ] README and `youtube.html` both link to all 10 lessons after Lesson 10 is complete
- [ ] Build proceeded phase-by-phase with a review gate at each step, per the collaboration
      protocol above — not written all at once
- [ ] Once confirmed complete, all planning docs (`todo5.md`, `todo6.md`, `todo5_v2.md`,
      `todo6_v2.md`, this file) archived to `ignore/`

---

*Prepared by comparing `todo5_v2.md` (Kiro's second-round plan) against `todo6_v2.md` (Claude's
second-round plan) on 2026-09-08. Neither source file, nor the original `todo5.md` / `todo6.md`
beneath them, was modified in producing this merge.*

# TODO5 v3 — A `lessons_kiro/` tutorial series (converged plan)

Build a **~10-lesson tutorial** (10 is the target; more allowed if a topic needs
splitting) in a `lessons_kiro/` folder at the repo root that teaches
a reader how to collaborate with AI coding assistants (Kiro, Claude, etc.) to go
**from an empty folder to the full `learn-better` repo** — its content, files,
capabilities, and docs. The lessons are a *curated, optimized* retelling of how
this project was actually built (drawing on the real `chats/` logs,
`skill_summary.md`, and `skill_todo.md`), not a verbatim transcript. Prompts shown
are the clean, improved versions; the artifacts they produce must match the real
repo exactly (no invented capabilities). Complexity and repo-coverage rise
gradually and evenly across the ten lessons. **Free, Markdown-only** — no new
dependency, no API, no code changes to the existing tools; the only repo edits at
the end are doc links (README, `youtube.html`, `plan.md`) + the `chats/` update.

> **Plan only.** Do NOT write any `lesson` file until this plan is approved. This
> is a converged plan merging `todo5_v2.md` (Kiro) and `todo6_v2.md` (Claude);
> `todo5_v3.md` is the only file created/modified for it.

---

## On "are the lessons themselves plans?" (user question — answered)

The lessons are **NOT** planning docs like `todo1`…`todo6`. Those `todoN.md` files
are *internal build plans* (phases, checkboxes, review gates) for the developer +
AI to execute. The **lessons are the finished teaching product**: reader-facing
tutorials that a newcomer follows to reproduce the repo. `todo5_v3.md` (this file)
is the *plan* for producing them; the `lessons_kiro/*.md` files are the *deliverable*.

If that distinction isn't what you intended — i.e. if you actually want each lesson
to itself be a mini-plan (todo-style, tasks/checkboxes rather than prose
tutorials) — say so and I'll reshape the template. The plan below assumes
**reader-facing tutorials**.

---

## Decisions (each question + the user's locked answer)

**Folder name.** *Question: what should the lesson folder be called?*
→ **`lessons_kiro/`** (not `lessons/`) — Kiro's lesson series. A parallel Claude
series may live in its own folder; this plan only builds `lessons_kiro/`.

**Q1 — File naming: underscores or dashes?** (`01_first_contact.md` vs
`01-getting-started.md`; both sort correctly.)
→ **Underscores** → `lessons_kiro/01_first_contact.md` … (matches the existing
`skill_summary.md` / `skill_todo.md` convention).

**Q2 — Add a `lessons_kiro/README.md` index page?** (An index listing all lessons
with one-line purposes, separate from the README / youtube.html sections.)
→ **Yes.**

**Q3 — Assistant framing: (A) assistant-agnostic prose with tool-specific asides,
or (B) explicit Kiro-vs-Claude framing with a taught division of labor?**
→ **(A) assistant-agnostic** — write "your AI assistant", **portable to any AI
harness**. Kiro/Claude specifics only as short optional asides, never load-bearing.

**Q4 — Pacing: (A) steady scaffold → environment → first script (first runnable
tool ~Lesson 04), or (B) early win (a working no-API-key tool by ~Lesson 02, env
folded in around it)?**
→ **(B) early win** — get a working tool running early so progress feels concrete
and stays un-abstract, rather than three setup lessons first.

**Q5 — Is "iterate and fix with the AI" its own lesson or a sub-section?** (Feeding
errors back, diagnosis vs. patches, knowing when to change approach.)
→ **Sub-section** (recommended) — a named sub-section of the first tool lesson, not
a separate lesson.

**Q6 — Troubleshooting: per-lesson only, or per-lesson + a consolidated recap?**
→ **Per-lesson boxes PLUS a consolidated "Troubleshooting your AI" recap** in the
final lesson (recommended).

**Q7 — Does the deploy lesson produce a real `notebooks/colab_setup.ipynb`, or only
document Colab in prose?**
→ **Yes, produce the real notebook file** (matches the repo, which already has it).

**Q8 — Fidelity: smoothed/optimized path, or preserve the real detours
(yt-dlp/scrapetube, the `lib/` refactor) as teaching moments?**
→ **Yes, smoothed** — present the optimized path to the same end state, with a
light touch of real detours as teaching moments where valuable (recommended).

**Q9 — `how_to_deploy.md`: teach the current README-based deploy approach, or have
the reader recreate the (now-retired) `how_to_deploy.md`?**
→ **Yes, current approach** — deploy guidance lives in README; do **not** recreate
the retired `how_to_deploy.md` (recommended).

**Q10 — Archive the planning docs to `ignore/` when the series is done?**
→ **Yes, deferred** — archive once the series is confirmed complete; a future step,
not part of building the lessons.

**Lesson count — is 10 a hard cap?**
→ **10 is the target, but MORE IS ALLOWED.** If a topic would make a single lesson
too complex, split it into additional numbered lessons (e.g. an extra lesson, or
`05a`/`05b`) to keep each focused (≤2–3 new concepts). The numbered sequence and
even ramp matter, not a hard cap of 10.

---

## Suggestions + last questions (each + the user's locked answer)

- **S1 (suggestion).** Because framing is assistant-agnostic (Q3-A) but the repo's
  real logs are Kiro's, show each lesson's example prompts as a generic instruction
  ("ask your assistant to …") with the *concrete optimized prompt text* underneath
  — portable, but still a ready-to-paste example.
  → **Yes, adopted.**

- **S2 (suggestion).** The early-win pacing (Q4-B) needs a *lightweight* env before
  Lesson 02 can run a tool (Python 3.12 + ffmpeg + `pip install`), with the
  *deeper* environment discussion (conda vs venv vs uv, ffmpeg-is-a-system-binary)
  as its own slightly-later lesson — so "environment" content is intentionally
  split, not duplicated.
  → **Yes, adopted** (lightweight env in Lesson 01, deep env in Lesson 03).

- **Q-A — Should `lessons_kiro/` be git-tracked** (authored content, like `docs/`
  and `summaries/`) **or git-ignored?**
  → **Git-tracked** — the lessons are a shareable deliverable, linked from README.

- **Q-B — Should the README/youtube "Lessons" section link only `lessons_kiro/`,
  or also accommodate a parallel Claude lesson folder?**
  → **Accommodate BOTH folders** — write the "Lessons" section to present two
  parallel series (e.g. `lessons_kiro/` and a Claude folder such as
  `lessons_claude/`), so either can be added/linked without reworking the section.
  This plan still only *builds* `lessons_kiro/`; it just doesn't hard-code a
  single-series layout.

> All decisions are now locked — nothing remains open. The plan below reflects them.

---

## Cross-cutting constraints

| Constraint | How it is handled |
|---|---|
| AI crashes / lost context | Each lesson opens with a **"Re-orient the AI"** block the reader can paste after a restart to cheaply restore context (repo name, current lesson, last file created, OS, env name, "continue from X"). |
| Realistic failure modes (not just hard crashes) | Assume Kiro/Claude rarely hard-crash, but cover the modes actually seen here: a response that stalls/goes silent (retry / "are you still working?"); an interrupted file write (verify the file wasn't corrupted before continuing); the assistant using the wrong Python interpreter/env (activate the env; verify with `where python`); a tool run whose terminal output looks empty/garbled (check the produced artifact, not the console); prompt/network hiccups (retry, re-state the goal). |
| Gradual complexity | Complexity and file count increase monotonically; no lesson introduces more than **2–3 new concepts**. |
| Even spread | Each lesson ≈ one focused working session (**30–90 min**). |
| Optimised prompts | Prompts embed patterns distilled from `skill_summary.md` and the `chats/` logs — always state the OS + env name + target file; "list the files you'll create before creating them"; always ask for **both** `.bat` and `.sh` runners in one prompt; always reference `lib/paths.py` for output paths. Don't invent patterns — distil what worked. |
| AI harness | **Assistant-agnostic (Q3-A):** written for "your AI assistant" and portable to any harness (Kiro, Claude, or other). Tool-specific notes only as short optional asides. |
| Fidelity to the real project | Lessons land on the real repo — real tools (`read_channel.py`, `transcribe_audio.py`, `make_wordcloud.py`, `generate_speech.py`, …), real runners (`scripts/`, `init.bat`), real `data/` layout, real docs. Never promise a capability the repo doesn't have. |
| File length | ~300–600 lines per lesson; if it grows past that, **split** into an extra numbered lesson rather than expand. |
| Final handoff | The final lesson ends with explicit AI tasks to update `chats/`, `README.md`, and `youtube.html` to link the lessons. |

---

## Collaboration / build protocol

Once this plan is approved, write the lessons in **reviewable phases, not all at
once**. For each phase:

1. **Implement only that phase.** Don't run ahead into later lessons.
2. **Draft, then hand back for review.** After a lesson (or the agreed batch), stop.
3. **Give a clear review pointer** — which file to open, what it teaches, how it
   links to the previous/next lesson.
4. **Wait for feedback/go-ahead** before the next phase; if a lesson needs rework,
   fix and re-issue the review first.
5. **Only after confirmation**, mark the phase done and continue.

In short: **draft → point to what to review → wait → continue.**

---

## Folder & file naming

```
lessons_kiro/                         (git-tracked — Q-A)
    README.md                         ← index page (Q2 = yes)
    01_first_contact_and_setup.md     first contact + lightweight env (S2)
    02_first_working_tool.md          early win: a real tool runs (Q4-B) + iterate-and-fix (Q5)
    03_environment_done_right.md      deep env: conda/venv/uv, ffmpeg, lib/paths (S2)
    04_playlists_and_transcripts.md   config-driven yt-dlp tools
    05_whisper_transcription.md       faster-whisper (may split 05a/05b)
    06_runners_and_lib.md             scripts/ + init.bat + reusable lib/
    07_summaries_and_wordclouds.md    AI-as-author + data/JS split
    08_tts_and_full_pipeline.md       Piper TTS + data/ tidy + full pipeline
    09_deploy_ci_handoff.md           deploy/1-click/CI + close the loop
```
*(Underscore naming per Q1. Filenames are indicative and follow the Q4-B "early
win" order; topics may split into extra numbered lessons if needed, so the final
series may exceed nine files. A parallel Claude series (e.g. `lessons_claude/`)
may sit alongside — Q-B; this plan only builds `lessons_kiro/`.)*

### Lesson template (every lesson uses this)
```
# Lesson NN — Title
**You'll build:** <one line: the artifact/capability by the end>
**Complexity:** <⭐…⭐⭐⭐⭐⭐>   **Est. time:** <~30–90 min>

## Prerequisites (from previous lessons)
## Re-orient the AI (paste after a crash/restart)   [5–8 lines]
## Concepts (2–3 ideas about working with AI)
## Step-by-step (numbered; each step ≈ one AI interaction)
   ### NN.x — <title>
   **Prompt:** <generic instruction ("ask your assistant to …") + the exact,
                copy-pasteable OPTIMIZED prompt text underneath (per S1)>
   **Expected response:** <what a good AI answer/action looks like>
   **Verify:** <command or check confirming success>
## When the AI misbehaves (2–3 failure modes specific to this lesson)
## What you have now (files added; repo state)
## Next → <link to next lesson>
```
*(Assistant-agnostic per Q3-A: no per-lesson "which AI" field; keep prose portable
to any AI harness, with tool-specific notes only as optional asides.)*

---

## The lessons (Q4-B "early win" pacing)

Target 10; split into more numbered lessons if a topic gets too dense (≤2–3 new
concepts each). The key Q4-B change vs a scaffold-first order: a **working
no-API-key tool runs by Lesson 02**, with only a *lightweight* env set up first;
the *deeper* environment discussion comes a bit later (per S2).

### Lesson 01 — First contact + a minimal setup — ⭐
**You'll build:** an empty repo, a *lightweight* Python 3.12 + ffmpeg env, a
`.gitignore` — just enough to run something next lesson.
- What an AI coding assistant is and how to frame a first request; the review
  mindset; the re-orient block + failure-mode list (first crash-recovery exposure).
- Minimal env only: Python 3.12, ffmpeg installed, an empty repo. (The *deeper*
  env discussion — conda vs venv vs uv, why ffmpeg isn't pip-installable — is
  deferred to Lesson 03, per S2, so nothing abstract blocks the early win.)
- Assistant-agnostic (Q3-A): "ask your assistant to …" with a concrete example
  prompt underneath.

### Lesson 02 — Your first working tool (early win) — ⭐⭐
**You'll build:** `code/read_channel.py` (or a first slice of it) + a runner, an
actual audio/transcript file under `data/`. **The reader downloads something real
by the end of this lesson.**
- Give the AI the vision (no-API-key YouTube → study material); ask for one small
  script that lists + downloads with `yt-dlp`; run it; see a file appear.
- Prompt discipline introduced here: state OS + env + target file; "list the files
  you'll create before creating them"; ask for both `.bat` and `.sh` runners.
- **Named sub-section "When your first run doesn't work" (Q5):** feed the actual
  error back (bot-check, empty results), ask for a diagnosis before a patch, and
  recognize when to change approach rather than re-patch. First debugging rep.
- Sets up `data/` as the single output root (`.gitignore` it) + `lib/paths.py`
  seed.

### Lesson 03 — Getting the environment right (properly) — ⭐⭐
**You'll build:** `requirements.txt`, a solid `lib/paths.py`, env `learn-better`.
- Now that something works, harden the setup: conda vs pip/venv vs uv (and why);
  **ffmpeg is a system binary — the #1 trap** (ask the AI to explain why pip can't
  install it); pin `requirements.txt`; verify checklist (`python --version`,
  `ffmpeg -version`, import smoke test); make `lib/paths.py` the single source of
  truth for output paths and repoint Lesson 02's tool through it.

### Lesson 04 — Playlists + transcripts, config-driven — ⭐⭐⭐
**You'll build:** `code/list_playlists.py`, `code/read_transcript.py`,
`config/config_transcribe.json`, runners `p.*`, `t.*`, `r.*`.
- List a channel's public playlists → `data/playlists.json`; transcripts per
  language → `data/transcripts/`; why `yt-dlp[default,curl-cffi]` (bot-check
  bypass); introduce config-driven design (`config/`); asking the AI to diagnose
  common yt-dlp errors (rate-limit, geo-block, empty subtitles).

### Lesson 05 — Whisper transcription — ⭐⭐⭐⭐
**You'll build:** `code/transcribe_audio.py`, config variants, `scripts/w.*`.
- faster-whisper with a config JSON (model size, language, compute type); int8 CPU
  vs T4 GPU decision guide; config variants (id / language / translate); output to
  `data/generated_transcripts/`; model cache (`~/.cache/huggingface`, `download_root`).
- **High-risk crash point:** Whisper runs are long — show how to resume a partial
  batch (skip-if-exists).
- *(Split candidate: if config modes + translate + the GPU/CPU discussion make
  this too dense, break into 05a "transcribe" and 05b "translate + config modes".)*

### Lesson 06 — Runner system + PATH + reusable `lib/` — ⭐⭐⭐⭐
**You'll build:** full `scripts/` set, `init.bat`, `lib/*` (net/textutil/youtube),
`code/compare_transcripts.py`.
- Generate all runners (×`.bat`/`.sh`) in one prompt (show the pattern that yields
  consistent output); `init.bat` (`%~dp0`, not `%CD%`) + PATH; Linux/macOS
  `export PATH`; the `::`-comment gotcha; extract shared logic into `lib/`
  ("show me before and after"; verify sameness); `compare_transcripts.py` quality check.

### Lesson 07 — Summaries + word clouds (AI as author + data/JS split) — ⭐⭐⭐⭐
**You'll build:** `code/make_summaries.py`, `code/make_wordcloud.py`,
`skill_summary.md`, `wordcloud.html`, runners `s.*`, `d.*`, `wc.*`.
- **Name the script-vs-AI boundary explicitly:** the script finds *what* needs
  summarizing; the AI *authors* the text following a reusable `skill_summary.md`
  with paste-ready instructions (first lesson where the AI is author, not just
  coder). `make_summaries.py` → `data/summaries/` (the only tracked output).
- `make_wordcloud.py` → `data/wordclouds/` + `wordcloud.html` (data/JS split;
  renderer-agnostic JSON); `lib/textutil.py` extraction; add black+ruff quality checks.

### Lesson 08 — TTS + tidy outputs + full pipeline — ⭐⭐⭐⭐⭐
**You'll build:** `code/generate_speech.py`, `code/reencode_audio.py`,
`how_to_test.md`, runners `v.*`, `a.*`.
- Piper TTS (free, CPU, no key) → `data/tts_output/`; `reencode_audio.py` (bitrate
  config) → `data/audio_reencoded/`; the R→W→S→V pipeline cheat-sheet; consolidating
  outputs under `data/` as a cross-cutting refactor that **never destroys inputs**;
  `how_to_test.md` manual playbook. (`lib/net.py`/`lib/youtube.py` were introduced
  in L04/L06; document them here.)

### Lesson 09 — Deploy, 1-click, CI + close the loop — ⭐⭐⭐⭐⭐
**You'll build:** `.devcontainer/*`, `Dockerfile.standalone`,
`.github/workflows/ci.yml`, *(Q7)* `notebooks/colab_setup.ipynb`; README +
youtube.html lesson links.
- Devcontainer (critical prompt: **ffmpeg must be a system package, not pip**) +
  `Dockerfile.standalone` (non-root; `-v $(pwd)/data:/app/data` mount); run-anywhere
  overview (local/container/Colab/Codespaces) — **deploy guidance lives in README,
  not a recreated `how_to_deploy.md` (Q9)**; 1-click badges + *(Q7)* the Colab
  notebook; light CI (ruff+black lint + network-free smoke; explain why
  network tests are excluded); Deno JS-runtime note.
- **Why NOT a web host (Vercel):** it's a local/CLI pipeline with heavy local deps
  (ffmpeg, ML models), not a request/response web service — a short reasoning the
  reader can repeat.
- **Consolidated "Troubleshooting your AI" recap (Q6).**
- **Final AI tasks:** "update `chats/` with a summary of the lessons"; "add a
  **Lessons** section (links + one-line descriptions) to `README.md`"; "add a
  matching **Lessons** section to `youtube.html`." Per Q-B, write both sections to
  **present parallel series** (link `lessons_kiro/` now; leave room for a Claude
  folder such as `lessons_claude/`), so a second series links in without rework.

> **Ramp check (Q4-B early-win order):** 01 first contact + minimal setup; 02 a
> working tool + first debugging rep (the early win); 03 proper environment; 04
> playlists/transcripts + config; 05 real dependency (Whisper); 06 runners/`lib/`;
> 07 AI-as-author + refactor; 08 second engine (Piper) + full pipeline + `data/`
> tidy; 09 deploy/CI + documentation close-out. Monotonic ⭐; ≤2–3 new concepts
> each. (This is 9 focused lessons; the 10th slot is reserved for the most likely
> split — e.g. Whisper 05a/05b, or splitting deploy from the docs/handoff — so the
> final series lands at ~10 without cramming.)

---

## Build phases (reviewable, one at a time)

| # | Phase | Scope | Complexity | Review gate |
|---|-------|-------|-----------|-------------|
| 0 | Scaffold | Create `lessons_kiro/` (git-tracked, Q-A) + the lesson template + `lessons_kiro/README.md` index; cross-check mapping vs real repo | low | template + mapping confirmed |
| 1 | Lessons 01–02 | First contact + minimal setup; **first working tool (early win)** + debugging sub-section | low-med | reader downloads something real by L02 |
| 2 | Lesson 03 | Proper environment (conda/venv/uv, ffmpeg, paths) | low | env/ffmpeg guidance accurate |
| 3 | Lesson 04 | Playlists/transcripts + config-driven | med | tool mechanics accurate |
| 4 | Lesson 05 | Whisper STT (+ possible 05a/05b split) | med | dependency validation accurate |
| 5 | Lesson 06 | Runners & `lib/` | med | runner-generation prompt pattern works |
| 6 | Lesson 07 | Summaries & word clouds (AI-as-author) | med | script-vs-AI boundary + skill file land |
| 7 | Lesson 08 | TTS + full pipeline + `data/` tidy | high | second engine + end-to-end run exact |
| 8 | Lesson 09 | Deploy/CI/handoff + Vercel reasoning + recap | high | all exact; Q7/Q9 honored |
| 9 | Consistency pass | Read all lessons: ramp, template, cross-links, real paths/tools everywhere | med | flows as one coherent course |
| 10 | Wire into docs | README "Lessons" section (both-series-ready, Q-B) + tree; youtube.html section + nav; plan.md note | low | links resolve, discoverable |
| 11 | Update `chats/` | Append prompts (verbatim) + summarized exchanges | low | logs reflect the work |
| 12 | Commit, push, archive | Commit to `main` when asked (stage by name); archive planning docs to `ignore/` per Q10 | low | on `main`; docs retired |

Build top-to-bottom. The riskiest content is the middle (04–07), where the repo's
real mechanics must be described exactly — keep those closest to the source files.

---

## Implementation notes for the author

- **Distil, don't invent** prompt patterns — pull from `skill_summary.md`,
  `skill_todo.md`, and the `chats/` logs.
- **Assistant-agnostic (Q3-A):** write "your AI assistant"; keep the lessons
  portable to any AI harness. Any Kiro/Claude specifics are short optional asides,
  never required to follow a step.
- **Re-orient blocks:** short (5–8 lines) — repo name, current lesson, last file
  created, OS, env name.
- **Crash/failure focus points:** Lesson 01 (first exposure), Lesson 05 (long
  Whisper jobs), Lesson 09 (complex agentic/multi-file), plus the Lesson 02
  debugging sub-section and the Lesson 09 consolidated recap.
- **Fidelity check before publishing each lesson:** cross-check every tool name,
  runner letter, and file path against the actual repo.

---

## Acceptance criteria
- [ ] `lessons_kiro/` exists at repo root, **git-tracked** (Q-A), with the lesson
      files (underscore naming, Q1) + a `lessons_kiro/README.md` index (Q2).
- [ ] Each file follows the standard template (You'll build / Prereqs / Re-orient /
      Concepts / Steps / When the AI misbehaves / What you have now / Next).
- [ ] Lessons are **assistant-agnostic** (Q3-A) and portable to any AI harness.
- [ ] Complexity increases monotonically from Lesson 01 (⭐) to the last (⭐⭐⭐⭐⭐).
- [ ] **Early win (Q4-B):** the reader runs a real no-API-key tool by Lesson 02.
- [ ] Every lesson embeds ≥1 verbatim, copy-pasteable, **optimized** prompt.
- [ ] Every lesson has a **Re-orient the AI** block + a per-lesson misbehavior box.
- [ ] Every referenced tool / path / runner actually exists in the repo.
- [ ] Lesson 02 includes the "iterate and fix" debugging sub-section (Q5).
- [ ] The summaries lesson names the script-vs-AI-author boundary and references
      `skill_summary.md`.
- [ ] The deploy lesson includes the "why not Vercel" reasoning + the consolidated
      troubleshooting recap (Q6), produces a real `notebooks/colab_setup.ipynb`
      (Q7), and teaches the current README-based deploy approach (Q9 — no recreated
      `how_to_deploy.md`).
- [ ] The final lesson ends with the three AI update tasks (chats, README, youtube.html).
- [ ] README and youtube.html link all lessons after the series is done, with the
      **Lessons section written to present parallel series** (Q-B — `lessons_kiro/`
      now, room for a Claude folder like `lessons_claude/`).
- [ ] Topics that got too dense were split into extra numbered lessons rather than
      overloading one (≤2–3 new concepts each).
- [ ] Built phase-by-phase with a review gate at each step (not all at once).
- [ ] Once confirmed, planning docs archived to `ignore/` (Q10).

---

## Guardrails
- **Plan only.** All decisions (folder, Q1–Q10, S1–S2, Q-A/Q-B) are locked; no
  lessons get written until the user gives the go-ahead to start building.
- **Optimize prompts, keep outcomes real.** Artifacts must match the repo today;
  never invent capabilities.
- **Free + Markdown only** (plus the Colab `.ipynb` produced in the deploy lesson,
  Q7=yes — still free/no-API). No other new deps/APIs/code changes; only the
  `lessons_kiro/` files + doc links + chats update.
- **Even, gradual ramp;** ≤2–3 new concepts per lesson; ~300–600 lines each, split
  rather than expand.
- **Commit to `main` only when asked** (straight to main, no branches; stage by name).
- **Archive planning docs only on the user's word** (Q10), following `skill_todo.md`.
- **`todo6.md` / `todo6_v2.md` are already merged here** and are not re-consulted as
  live inputs going forward.

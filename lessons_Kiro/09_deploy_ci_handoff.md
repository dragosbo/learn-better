# Lesson 09 — Deploy, 1-click, CI + close the loop

**You'll build:** a Dev Container, a standalone Docker image, 1-click install
badges (Colab / Codespaces / Dev Container) + a real Colab notebook, light CI (lint
+ network-free smoke), the reasoning for *why this isn't a web app* — and finally,
have the AI update the docs and link the lessons.
**Complexity:** ⭐⭐⭐⭐⭐   **Est. time:** ~75–90 min

> **Assistant-agnostic.** Any AI assistant works. This lesson also includes the
> consolidated troubleshooting recap for the whole course.

---

## Prerequisites (from Lesson 08)

- The full pipeline runs; all outputs under `data/`; `requirements.txt` current;
  `lib/`, runners, configs in place.

---

## Re-orient the AI (paste after a crash/restart)

```
Context: FINAL lesson (09) of building a YouTube→study-material toolkit with your
help. OS: <your OS>. Repo: learn-better/ — full pipeline works, outputs under data/,
requirements.txt current, lib/ + runners + configs done.
Goal now: make it reproducible everywhere (devcontainer, Dockerfile.standalone,
Colab notebook + badges, Codespaces), add light CI (ruff/black lint + network-free
smoke test), document why it's NOT a web app, then have you update chats/ + README +
youtube.html to link the lessons.
Last thing done: <e.g. "wrote .devcontainer/Dockerfile">. Please continue from there.
```

---

## Concepts (what this lesson teaches about working with AI)

1. **Reproducible-anywhere is a documentation + config task**, not more code. The
   assistant is great at generating Dockerfiles/CI YAML — you review for the
   real-world traps (ffmpeg, base-image drift).
2. **CI is a cheap safety net.** A lint + a network-free smoke test catches the
   exact regressions this kind of project hits (stale imports, broken paths, bad
   base images) — without running slow network tools.
3. **Closing the loop.** The last act is having the AI keep the docs honest: update
   the chat logs and link the lessons so the work is discoverable.

---

## Step-by-step

### 09.1 — Dev Container (and the ffmpeg + base-image traps)

**Ask your assistant to** create a `.devcontainer/` that installs ffmpeg and the
deps automatically — and flag the two real gotchas.

> **Prompt:**
> "Create `.devcontainer/Dockerfile` and `devcontainer.json` for this project.
> CRITICAL: ffmpeg must be installed as a **system package** in the Dockerfile
> (`apt-get install -y ffmpeg`) — it can't be pip-installed. Use a CURRENT
> devcontainer Python base image (the older `mcr.microsoft.com/vscode/devcontainers/...`
> path and some OS tags are retired and 404 on pull — use
> `mcr.microsoft.com/devcontainers/python:3.12-bookworm`). `postCreateCommand`
> should `pip install -r requirements.txt`. Add a model-cache volume so Whisper/
> Piper weights survive rebuilds."

**Expected response:** a Dockerfile with an ffmpeg layer + a valid current base
image, and a `devcontainer.json` running the pip install. These two traps —
**ffmpeg-not-in-image** and **a retired base image (404 → recovery mode)** — are the
top causes of a broken container; call them out explicitly.

**Verify:** "Reopen in Container" builds cleanly; inside, `ffmpeg -version` and
`python -c "import yt_dlp, faster_whisper, pandas; print('OK')"` both succeed.

### 09.2 — Standalone Docker image

**Ask your assistant to** create a slim, IDE-free image for CI/servers.

> **Prompt:**
> "Create `Dockerfile.standalone`: slim `python:3.12-slim` base, install ffmpeg,
> non-root user, `pip install -r requirements.txt`, copy the project. Add a
> `.dockerignore` that keeps the build context lean (mirrors the git-ignored
> outputs). In the header comment, show the run pattern mounting outputs:
> `-v $(pwd)/data:/app/data`."

**Expected response:** `Dockerfile.standalone` + `.dockerignore`, with a single
`data/` volume mount to persist all outputs.

**Verify:** `docker build -f Dockerfile.standalone -t learn-better .` succeeds; a
run with `-v .../data:/app/data` can execute `python code/read_channel.py`.

### 09.3 — 1-click install: Colab notebook + three badges

**Ask your assistant to** produce a real Colab setup notebook and the README badges.

> **Prompt:**
> "Create `notebooks/colab_setup.ipynb` (valid nbformat) with idempotent cells:
> (1) `apt-get install -y ffmpeg` + clone the repo + `cd`; (2)
> `pip install -r requirements.txt`; (3) optional Google Drive mount + make the
> `data/` subdirs; (4) verify (ffmpeg, imports, and an accelerator check that
> reports CPU/GPU/TPU); (5) an example run using the REAL script
> (`python code/transcribe_audio.py config/config_transcribe.json`). Then give me
> three README badges for **1-click** setup: Open-in-Colab (→ this notebook),
> Open-in-Codespaces (→ `codespaces.new/<owner>/<repo>`), and a Dev Container
> 'Reopen in Container' line. Make Drive-mount failures non-fatal (wrap in
> try/except) and skip `ipykernel` on Colab (Colab ships its own — avoids pip
> conflict warnings)."

**Expected response:** a valid `.ipynb` + a "⚡ 1-click deploy" block with the three
entry points. "1-click" = a *ready-to-run env* (ffmpeg + deps + `data/` layout);
typing the one-letter runners is a separate optional PATH step.

**Verify:** the notebook is valid (`python -c "import json; json.load(open('notebooks/colab_setup.ipynb'))"`);
the badges resolve **once pushed to the repo's default branch**.

### 09.4 — Light CI (lint + network-free smoke)

**Ask your assistant to** add a GitHub Actions workflow that catches regressions
without touching the network.

> **Prompt:**
> "Add `.github/workflows/ci.yml` (runs on push/PR to the default branch), two jobs:
> **lint** — `ruff check --select E9,F` (syntax + real errors) + `compileall`, with
> `black --check` advisory (non-blocking); **smoke** — install ffmpeg + requirements,
> verify imports + `lib.paths`, then run a standard-library-only tool
> (`make_summaries.py`) as a network-free 'does the repo run?' check. Do NOT run
> yt-dlp/Whisper/Piper (network + slow). Use current action versions
> (`actions/checkout@v5`, `actions/setup-python@v6`) to avoid Node-deprecation
> warnings. Explain why network tests are excluded."

**Expected response:** a two-job workflow. It deliberately avoids network tools —
the goal is catching stale-import / broken-path / bad-base-image regressions early,
fast. Note black is advisory so formatting drift reports without failing the build
(run `black code lib` once to make it green).

**Verify:** push and watch the Actions tab — lint + smoke go green in ~1–2 min. (If
lint flags something real, like an `F541` f-string-without-placeholders, fix it —
that's CI doing its job.)

### 09.5 — Why this is NOT a web app (a grounding you can repeat)

**Ask your assistant to** explain why a serverless web host doesn't fit.

> **Prompt:**
> "In a short paragraph: why is this project NOT a good fit for a serverless web
> host like Vercel/Netlify, and what would you use instead if you wanted an
> always-on hosted run?"

**Expected response:** it's a **batch CLI pipeline**, not a request/response web
service — serverless hosts can't install the **ffmpeg** system binary, cap function
runtime at seconds–minutes (real transcription runs far longer), and give no
persistent filesystem for `data/`. For always-on, use a small VM or a container from
`Dockerfile.standalone`, not a web host.

**Verify:** you can restate the reasoning in one sentence. (It's a great example of
the AI telling you *not* to do something rather than building the wrong thing.)

### 09.6 — Close the loop: update docs + link the lessons

**Ask your assistant to** keep the docs honest and make the course discoverable.

> **Prompt:**
> "Three doc tasks: (1) update the chat logs in `chats/` with a summary of what we
> built across these lessons; (2) add a **Lessons** section to `README.md` linking
> each lesson file with a one-line description; (3) add a matching **Lessons**
> section to `youtube.html`. Write both Lessons sections to present PARALLEL series
> — link this `lessons_Kiro/` series now, and leave room for a second series (e.g.
> `lessons_claude/`) to be added without reworking the section."

**Expected response:** updated `chats/` logs + a README Lessons section + a
youtube.html Lessons section, phrased for two parallel series (Q-B).

**Verify:** the README/youtube "Lessons" links resolve to the files in
`lessons_Kiro/`, and a second series could slot in beside them.

---

## Troubleshooting your AI — consolidated recap (all lessons)

The failure modes you met, and the move that fixes each. Assume your assistant
rarely *hard*-crashes; these are the everyday snags:

- **It stalls / goes silent.** Wait a beat, then a short "are you still there?
  please continue," or re-send. For a lost thread, paste the lesson's **Re-orient
  the AI** block. (First met in Lesson 01.)
- **A file write got interrupted.** Before continuing, verify the file isn't
  half-written/corrupted (open it or re-read); don't build on a truncated file.
- **Wrong Python interpreter/env.** The classic `ModuleNotFoundError` despite
  installing. `python -c "import sys; print(sys.executable)"` — if it's not your
  env, activate it. (Lessons 02, 03, 05.)
- **Terminal output looks empty/garbled** (esp. Windows `cmd`). Don't trust the
  console — check whether the **artifact** (a file under `data/`) actually appeared.
- **Bot-check / rate-limit (429) from YouTube.** Not a code bug — cloud/anonymous
  IPs get throttled. Cookies file, or wait and retry; fetch fewer languages. (Lessons
  02, 05, 09/Colab.)
- **It over-produces** (150-line `.gitignore`, unrequested deps, essays). Push back:
  "minimal," "only what's used." (Lesson 01, 03.)
- **A refactor changes behavior** (re-downloads, new folders, a lost tracked file).
  Require *verified sameness*: change the source of truth first, then re-run + `git
  status`. (Lessons 06, 08.)
- **`.sh` runners fail on Linux (`^M`).** CRLF line endings — fix via
  `.gitattributes` (`*.sh eol=lf`). (Lesson 06.)
- **Container won't build.** Usually ffmpeg missing from the image, or a retired
  base image (404). Check both first. (Lesson 09.)
- **When to change approach, not re-patch.** If two fixes on the same approach both
  fail, ask for the *root cause* and a *fundamentally different* approach. (Lesson
  02, reinforced throughout.)
- **Feed back exact errors.** Across every lesson: paste the real output, ask for a
  diagnosis before a patch. This one habit outperforms everything else.

---

## What you have now (the whole repo)

```
learn-better/
├── code/        # read_channel, read_transcript, list_playlists, transcribe_audio,
│                #   compare_transcripts, make_summaries, make_wordcloud,
│                #   generate_speech, reencode_audio
├── lib/         # paths, net, textutil, youtube
├── config/      # config_*.json (transcribe / wordcloud / reencode / tts)
├── scripts/ or root runners (.bat + .sh) + init.bat
├── notebooks/   # colab_setup.ipynb (+ any exploration notebook)
├── .devcontainer/  Dockerfile.standalone  .dockerignore
├── .github/workflows/ci.yml
├── skill_summary.md  wordcloud.html  how_to_test.md
├── README.md  youtube.html  plan.md   # with a Lessons section linking this series
├── chats/       # kiro/claude logs
├── lessons_Kiro/  # THIS course
└── data/        # all outputs (git-ignored except summaries/)
```

---

## You're done 🎉

You built the full `learn-better` toolkit from an empty folder — and, more
importantly, you practiced the workflow that got you there: framing requests,
splitting deterministic work from reasoning, iterating on real errors, refactoring
with verified sameness, and keeping the docs honest. Those habits transfer to any
project and any AI assistant.

**Where to go next:** pick a capability the repo *doesn't* have (a nicer TTS voice,
a web viewer for summaries, a scheduled run) and drive it end-to-end with your
assistant using the same loop — plan → build → verify → document.

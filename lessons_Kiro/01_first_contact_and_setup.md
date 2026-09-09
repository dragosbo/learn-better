# Lesson 01 — First contact + a minimal setup

**You'll build:** an empty project folder, a *lightweight* Python 3.12 + ffmpeg
environment, and a `.gitignore` — just enough to run something real next lesson.
**Complexity:** ⭐   **Est. time:** ~30–45 min

> **Assistant-agnostic.** Everything here works with any AI coding assistant
> (Kiro, Claude, or another). Where a step is easier in one tool, it's noted as a
> short *aside*, never as a requirement.

---

## Prerequisites

- A terminal you're comfortable opening (Windows `cmd`/PowerShell, macOS/Linux bash).
- `git` installed, and a GitHub (or similar) account if you want to push later.
- An AI assistant available in some form (a chat window is enough for this lesson;
  an IDE-integrated assistant helps from Lesson 02 on).
- **No Python knowledge beyond "I can run a command" is required yet.**

---

## Re-orient the AI (paste after a crash/restart)

If your assistant loses the thread — or you come back later — paste a short block
like this to cheaply restore context. Keep it to ~5–8 lines:

```
Context: I'm doing Lesson 01 of a course that builds a YouTube→study-material
toolkit with your help, from an empty folder.
OS: <your OS, e.g. Windows 11 / macOS / Ubuntu>.
Goal of this lesson: create an empty repo + a Python 3.12 env with ffmpeg, and a
.gitignore. Nothing built yet.
Last thing done: <e.g. "installed Python 3.12", or "nothing yet">.
Please continue from there; ask me for anything you need.
```

You'll write a lesson-specific version of this at the top of every lesson — it's
the single most useful habit for working with an assistant that can forget.

---

## Concepts (what this lesson teaches about working with AI)

1. **Frame the request, don't just ask.** Tell the assistant *who you are, what OS
   you're on, what you're trying to end up with, and what you've done so far.* A
   framed request gets a usable answer; a vague one gets a generic essay.
2. **The review mindset.** The assistant's output is a *draft to check*, not a
   verdict. Every step ends with a way to **verify** the result yourself.
3. **Cheap recovery beats long sessions.** Assistants can stall or lose context.
   A short re-orient block (above) restores it in seconds — far cheaper than
   re-explaining everything.

---

## Step-by-step

### 01.1 — Understand what you're about to build

**Ask your assistant to** explain the project at a high level and confirm the tools
it will need, so you start with a shared mental model.

> **Prompt (copy, adapt the OS):**
> "I want to build a small, free, no-API-key toolkit that downloads YouTube audio
> and transcripts, transcribes audio locally with Whisper, and generates
> summaries and word clouds — all runnable on my own machine (I'm on `<your OS>`).
> Before any code: in 5–8 bullets, what are the core building blocks and the one
> or two system tools I'll need installed? Keep it concrete."

**Expected response:** a short list naming things like `yt-dlp` (download +
subtitles), `faster-whisper` (local speech-to-text), a text-to-speech engine, and
crucially **ffmpeg** as a *system* tool (not a Python package). If it dumps a wall
of text, ask it to shorten to bullets.

**Verify:** you can restate, in one sentence, what the project does and that
**ffmpeg** is a system dependency. That's the whole check.

> *Aside (Kiro):* an IDE-integrated assistant can also open your (empty) folder and
> describe what it sees — a good way to confirm it's "looking at" the right place.

### 01.2 — Create the project folder and a git repo

**Ask your assistant to** give you the exact commands for your OS to make a new
folder and initialize git.

> **Prompt:**
> "Give me the exact terminal commands for `<your OS>` to: create a new folder
> called `learn-better`, move into it, and run `git init`. One command per line,
> no explanation."

**Expected response:** something equivalent to:

```
mkdir learn-better
cd learn-better
git init
```

**Verify:** run them, then `git status` — it should say you're on a branch with no
commits yet. If `git` isn't found, ask the assistant how to install it for your OS.

### 01.3 — Get a lightweight Python 3.12 + ffmpeg environment

This lesson keeps setup *minimal* — just enough to run a tool next lesson. The
deeper environment discussion (conda vs venv vs uv, why ffmpeg can't be pip-installed)
comes in **Lesson 03**; don't over-engineer it now.

**Ask your assistant to** give you the shortest path to Python 3.12 + ffmpeg on
your OS, and a one-liner to verify each.

> **Prompt:**
> "On `<your OS>`, give me the simplest way to get **Python 3.12** and **ffmpeg**
> installed and on my PATH. I don't want a deep environment lecture yet — just the
> install commands and a one-line verify command for each. If conda is the easiest
> single path that also handles ffmpeg, show that."

**Expected response:** install commands plus verifies. Typical shapes:

```
python --version        # must print Python 3.12.x
ffmpeg -version         # must print a version banner, NOT "command not found"
```

(On many setups the easiest single path is a conda env that installs both, e.g.
`conda create -n learn-better python=3.12 -y` then
`conda install -c conda-forge ffmpeg -y` — but any route that makes those two
verify commands succeed is fine for now.)

**Verify:** both commands above succeed. **This is the gate for the whole course** —
if `python --version` shows anything below 3.12 or `ffmpeg -version` says "not
found," fix it before moving on (ask the assistant, quoting the exact error).

### 01.4 — Add a starter `.gitignore`

**Ask your assistant to** create a minimal `.gitignore` suitable for a Python
project that will later produce downloaded media and generated files.

> **Prompt:**
> "Create a minimal `.gitignore` for a Python project on `<your OS>`. Ignore the
> usual Python artifacts (`__pycache__/`, `.venv/`, `*.pyc`), editor/OS cruft, and
> a top-level `data/` folder I'll use for generated output later. Keep it short —
> no giant framework boilerplate."

**Expected response:** a ~10–20 line `.gitignore`. If it's 150 lines of framework
templates, tell it "too big, make it minimalist" — a real interaction pattern
you'll reuse.

**Verify:** `.gitignore` exists and is short; `git status` shows it as the one new
file to track.

---

## When the AI misbehaves

- **It gives a 150-line generic `.gitignore` (or over-explains everything).** Push
  back plainly: *"too long — give me the minimal version."* Concise beats complete.
- **It assumes the wrong OS** (Linux commands on Windows, etc.). Re-state your OS
  in the prompt; that single detail fixes most command mismatches.
- **`python --version` shows the wrong version** (e.g. an old 3.7 from a system
  install). Don't fight it in code — you're in the wrong interpreter. Paste the
  exact output back and ask how to get a clean 3.12 for your OS. (Lesson 03 makes
  this bulletproof.)
- **The assistant stalls or goes silent.** Give it a moment; if nothing comes, a
  short "are you still there? please continue" or re-sending usually resumes it.
  For anything longer, paste the **Re-orient the AI** block above.

---

## What you have now

```
learn-better/
├── .git/          # initialized repo
└── .gitignore     # minimal
```
Plus, on your machine: Python 3.12 and ffmpeg, both verified on PATH. No project
code yet — that's next.

---

## Next → [Lesson 02 — Your first working tool (early win)](02_first_working_tool.md)

You'll get a real, no-API-key tool downloading a YouTube video's audio and
transcript — something concrete you can see on disk by the end — and learn the
single most important AI-pairing skill: **feeding an error back and iterating.**

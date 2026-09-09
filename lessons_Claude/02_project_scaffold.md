# Lesson 02 — Project Scaffold

**You'll build:** An empty repo with a sound folder layout, `.gitignore`, a first `README.md`,
a living `plan.md`, and the repo pushed to GitHub.
**Complexity:** ⭐⭐☆☆☆   **Est. time:** ~45–60 min
**AI tasks in this lesson:** project planning, multi-file creation, documentation generation

---

## Prerequisites

- Lesson 01 completed (you understand the re-orient pattern and what the project does)
- Git installed and configured with your name + email
- A GitHub account
- A terminal (Command Prompt, PowerShell, or bash — all work)

---

## Re-orient the AI

> Paste this block at the start of a new session, or any time the assistant loses context:
>
> "I'm working on the **learn-better** repo — a Python tool that downloads YouTube audio and
> transcripts, transcribes locally with faster-whisper, and generates summaries and word clouds.
> We're on **Lesson 02 — Project Scaffold**. No code files exist yet — we're creating the
> folder structure, `.gitignore`, `README.md`, and `plan.md`, then pushing to GitHub.
> OS: Windows. Please continue from [specific point]."

---

## Concepts

1. **Give the AI a project vision, not a task list.** When you describe the full shape of what
   you're building upfront, the assistant makes better structural decisions — folder names,
   separation of concerns, which things go where — than when you describe one file at a time.

2. **Think step by step.** Adding "think step by step. List the files you will create before
   creating them." to a multi-file prompt forces the assistant to plan before acting. This
   dramatically reduces half-finished sets of files.

3. **The planning document belongs in the repo.** A short `plan.md` that records what you decided
   and why is worth far more than notes in a chat session. The assistant loses context between
   sessions; a committed plan file doesn't.

---

## Step-by-step

### 02.1 — Ask the assistant to design the project structure

**Prompt:**
```
I'm starting a Python CLI project. Here is what it will do:

- Download YouTube audio files and auto-generated transcripts using yt-dlp
- Transcribe audio locally with faster-whisper (no API, no cloud)
- Generate text summaries of transcripts using an AI API
- Build word clouds from transcripts
- Convert summaries to speech with Piper TTS
- Reencode audio to target bitrate
- All outputs go to a local data/ folder that is git-ignored

The scripts will be CLI tools run from the terminal. There will be shared helper code
(path constants, network calls, text utilities). There will be runner shortcut scripts
in scripts/ for quick invocation on Windows (.bat) and Linux/macOS (.sh).

Think step by step. Before proposing a layout, list your assumptions. Then propose a
folder structure with one-line descriptions of each folder. Do not create any files yet.
```

**Expected output:** The assistant should propose a layout close to:
```
project-root/
    code/          — main Python scripts (one script per task)
    lib/           — reusable helpers (path constants, net, text utilities)
    scripts/       — one-letter runner shortcuts (.bat + .sh pairs)
    data/          — all output (audio, transcripts, summaries, word clouds) — git-ignored
    config/        — JSON config files for tunable parameters
    docs/          — supplementary documentation
    notebooks/     — optional Jupyter exploration
```

**Verify:** Read the layout aloud. Check that: `code/` and `lib/` are separate (scripts vs
helpers), `data/` exists as its own top-level folder, `scripts/` is for runner shortcuts. If the
assistant bundles scripts and helpers together, push back: "I'd like to keep reusable helper
code in lib/ so scripts can import from it cleanly."

---

### 02.2 — Create the folder structure

Now ask the assistant to emit the shell commands that create the actual folders.

**Prompt:**
```
Good. Now give me the exact shell commands to create this structure on Windows
(Command Prompt). Use mkdir. Create empty placeholder files where useful so git
tracks the folders. Show me one block of commands I can copy and paste.
```

**Expected output:** Something like:
```cmd
mkdir code lib scripts data config docs notebooks
type nul > lib\__init__.py
type nul > code\.gitkeep
type nul > data\.gitkeep
```

**Verify:** Run the commands. Then:
```cmd
dir /b
```
Check that `code`, `lib`, `scripts`, `data`, `config`, `docs`, `notebooks` all appear.

---

### 02.3 — Create the `.gitignore`

**Prompt:**
```
I'm working on Windows, but the project will also run on Linux inside a devcontainer.
Generate a .gitignore for a Python project with these specific requirements:
- Ignore the entire data/ folder EXCEPT data/summaries/ (those are kept)
- Ignore standard Python artifacts: __pycache__, .pyc, .egg-info, dist/, build/
- Ignore conda/venv environment folders
- Ignore editor files: .vscode/settings.json, .idea/
- Ignore OS files: Thumbs.db, .DS_Store
- Keep lib/__init__.py tracked even though lib/ is otherwise code (it should be tracked)
Output only the .gitignore content, no explanations.
```

**Expected output:** A `.gitignore` file with a `data/` ignore and a `!data/summaries/` exception.
The exception line is critical — without it `data/summaries/` gets ignored too.

**Verify:** Paste the output into a new file called `.gitignore` in your project root.
Then check the exception is present:
```cmd
findstr /i "summaries" .gitignore
```
You should see `!data/summaries/` (or similar). If it's missing, ask the assistant to add it.

---

### 02.4 — Create the first `README.md`

**Prompt:**
```
Write a README.md for this project. The project is called learn-better.
It should include:
1. A one-paragraph description: what it does, what it doesn't (no YouTube API needed,
   all transcription is local, no cloud processing).
2. A Prerequisites section: Python 3.12, conda, ffmpeg (system binary — not pip),
   yt-dlp[default,curl-cffi], faster-whisper, Piper TTS.
3. A Quick Start section with placeholder commands (we'll fill in the real ones in later lessons).
4. A folder layout section showing code/, lib/, scripts/, data/, config/.
5. No badges, no emojis, no marketing tone — clear and factual.
Output only the README.md content.
```

**Expected output:** A plain, readable README with the five sections above. The Prerequisites
section should explicitly call out that ffmpeg must be installed at the OS level (conda or system
package manager — NOT pip).

**Verify:** Read the Prerequisites section. Confirm it says:
- Python 3.12
- conda (or similar)
- ffmpeg as a system binary, not via pip
- yt-dlp[default,curl-cffi]

If the README suggests `pip install ffmpeg`, that is wrong — push back and ask for a correction.

---

### 02.5 — Create `plan.md`

`plan.md` is the project's living planning document. It records decisions and intentions that
are not visible in the code itself.

**Prompt:**
```
Create a plan.md for this project. It should serve as the living planning document — a place
to record what we've decided and why. Format it with these sections:

## Goal
One paragraph: what learn-better should do when complete.

## Stack
A table with columns: Component | Tool | Why chosen.
Rows: audio download, caption download, transcription, summarisation, TTS, audio reencoding,
word cloud. Leave "Why chosen" with a placeholder for now.

## Open questions
Three placeholder questions that a project like this typically needs to answer
(package versions, target audio format, model size vs speed tradeoff for whisper).

## Decisions log
Empty for now — one header row only.

Output only the plan.md content.
```

**Expected output:** A well-structured markdown file with those four sections. The Stack table
should have `yt-dlp` for audio/caption download, `faster-whisper` for transcription, `Piper`
for TTS.

**Verify:** Save the file as `plan.md`. Open it in a markdown preview and confirm the table
renders correctly (column separators aligned, no broken rows).

---

### 02.6 — Initialise git and push to GitHub

**Prompt:**
```
I need to initialise a git repo, make a first commit, and push to a new GitHub repo.
My GitHub username is [your-username]. I want the remote repo to be named learn-better
and be public. Give me the exact commands for Windows (Command Prompt).
Include: git init, setting the default branch to main, adding all files, first commit,
creating the GitHub repo with the GitHub CLI (gh), adding the remote, and pushing.
```

**Expected output:** A command sequence like:
```cmd
git init
git checkout -b main
git add .gitignore README.md plan.md lib\__init__.py
git commit -m "initial scaffold: folder layout, gitignore, README, plan"
gh repo create learn-better --public --source=. --remote=origin --push
```

**Verify:**
```cmd
git log --oneline
```
You should see one commit with your message. Then visit `https://github.com/[your-username]/learn-better`
and confirm the files are there.

---

### 02.7 — Ask the assistant how `plan.md` should grow

One last conceptual prompt — establishing the habit before you need it.

**Prompt:**
```
I've committed plan.md as a living planning document. How should I maintain it as the
project grows? Specifically: what should go in the Decisions log, when should I update
the Open questions section, and how often should I commit changes to it?
```

**Expected output:** The assistant should suggest updating the Decisions log whenever you make a
non-obvious choice (why a specific model size, why a specific audio format, why you chose one
library over another). Open questions should be resolved and moved to the Decisions log, not
deleted. Frequency: commit plan.md alongside any code commit that was motivated by a decision.

**Verify:** No command. Confirm you're comfortable with the maintenance habit described — you'll
use it in every lesson from here on.

---

## When the AI misbehaves

**The assistant creates a deeply nested folder structure with subfolders inside subfolders.**
Push back: "I'd like to keep this flat. One level of subdirectories under the project root.
Can you simplify?" A flat structure is easier to navigate and the project doesn't need nesting
at this stage.

**The `.gitignore` exception for `data/summaries/` is missing or the assistant uses the wrong
syntax.**
The correct pattern is:
```
data/
!data/summaries/
```
The `!` must come *after* the `data/` rule, not before. If the assistant reverses the order,
or uses `data/*` instead of `data/`, the exception won't work. Show it the two lines and ask
it to explain why order matters — this is a good learning moment.

**The README gets filled with emojis, badges (build passing, licence), or marketing language.**
Add to your prompt: "No badges, no emojis, no marketing tone. Plain GitHub markdown only."
If you get it after the fact, ask: "Rewrite in a plain, technical style. Remove all badges and
emojis."

**`gh repo create` is not available (GitHub CLI not installed).**
Ask the assistant for the alternative: "I don't have the GitHub CLI. How do I create the repo on
GitHub.com and add the remote manually?" The manual steps are: create repo on github.com, copy
the SSH/HTTPS remote URL, then `git remote add origin <url>` and `git push -u origin main`.

---

## What you have now

Files added this lesson:

```
learn-better/
    .gitignore
    README.md
    plan.md
    lib/
        __init__.py
    code/      (tracked via .gitkeep or placeholder)
    scripts/   (tracked via .gitkeep or placeholder)
    data/      (git-ignored except data/summaries/)
    config/
    docs/
    notebooks/
```

Repo state: empty but properly structured, `.gitignore` protecting `data/`, first commit on
`main`, pushed to GitHub.

---

## Next →

[Lesson 03 — Environment Setup](03_environment_setup.md)

# Lesson 06 — Runner system + PATH + reusable `lib/`

**You'll build:** the complete one-letter runner set (all `.bat` + `.sh`), an
`init.bat` + a PATH setup so the short names work from anywhere, a reusable `lib/`
extracted from the tools **without changing behavior**, and a
`compare_transcripts.py` quality check.
**Complexity:** ⭐⭐⭐⭐   **Est. time:** ~60–90 min

> **Assistant-agnostic.** Any AI assistant works. An IDE-integrated assistant
> shines here (multi-file refactor).

---

## Prerequisites (from Lesson 05)

- Several tools now exist (`read_channel`, `read_transcript`, `list_playlists`,
  `transcribe_audio`) with duplicated yt-dlp/cookie/text logic between them.
- `lib/paths.py` exists; a few runners (`p`, `t`, `r`, `w`) exist ad hoc.

---

## Re-orient the AI (paste after a crash/restart)

```
Context: Lesson 06 of building a YouTube→study-material toolkit with your help.
OS: <your OS>. Repo: learn-better/ with several code/*.py tools that duplicate
yt-dlp/cookie/text-cleaning logic, lib/paths.py, and some one-letter runners.
Goal now: generate the FULL runner set (.bat + .sh) in one go, add init.bat + a
PATH setup so short names work from anywhere, extract shared logic into lib/
(net/textutil/youtube) with IDENTICAL behavior, and add code/compare_transcripts.py.
Last thing done: <e.g. "extracted lib/net.py">. Please continue from there.
```

---

## Concepts (what this lesson teaches about working with AI)

1. **Behavior-preserving refactor ("verify sameness").** The win here is *no new
   behavior*. Ask for before/after, and re-run each tool to confirm identical
   results.
2. **Generate repetitive files in one prompt.** Ask for all runners × both
   platforms at once, with a stated pattern — far better than ten round-trips.
3. **A quality check makes ML trustworthy.** A tiny comparison script turns "seems
   fine" into a number you can cite.

---

## Step-by-step

### 06.1 — Generate the full runner set in one prompt

**Ask your assistant to** produce every runner, both platforms, consistently.

> **Prompt:**
> "Create the complete one-letter runner set as `<letter>.bat` (Windows) AND
> `<letter>.sh` (Linux/macOS) pairs, one prompt: c=activate env, r=read_channel,
> t=read_transcript, p=list_playlists, w=transcribe_audio. Each `.bat` activates
> the `learn-better` conda env then runs `python code/<script>.py %*`; each `.sh`
> activates conda if present (else uses current python) then `python code/<script>.py "$@"`.
> Pass through an optional config arg. Show them all; keep them tiny."

**Expected response:** all the pairs, uniform. Requesting "both platforms, one
prompt, stated pattern" is the discipline that yields consistent output.

**Verify:** each runner launches its tool and forwards a config arg (e.g.
`w config/config_transcribe.id.json`).

### 06.2 — Line endings for `.sh` (a real cross-platform trap)

**Ask your assistant to** ensure `.sh` files use LF, not CRLF.

> **Prompt:**
> "On Windows, git may give my `.sh` files CRLF line endings, which breaks them on
> Linux (`bad interpreter: ...^M`). Add a `.gitattributes` that forces `*.sh` to LF
> and keeps `*.bat` as CRLF, and tell me how to set the executable bit on the `.sh`
> files via git."

**Expected response:** a `.gitattributes` with `*.sh text eol=lf` / `*.bat text
eol=crlf`, plus `git update-index --chmod=+x <file>.sh`. A small thing that saves a
baffling Linux failure later.

**Verify:** `.gitattributes` exists; `.sh` files are LF.

### 06.3 — `init.bat` + PATH so short names work anywhere

**Ask your assistant to** create a session PATH helper and explain the `%~dp0`
detail.

> **Prompt:**
> "Create `init.bat` at the repo root that adds the folder containing the runners
> to PATH for the current cmd session, so I can type `c`, `r`, `w`… from the repo
> root. Use `%~dp0` (the .bat's own folder), NOT `%CD%` — explain why in one line.
> Also give the Linux/macOS equivalent (`export PATH="$PWD/<runners>:$PATH"`) and
> how to make each permanent."

**Expected response:** `init.bat` using `%~dp0` (resolves relative to the script, so
it works regardless of the current directory), plus the `export PATH` one-liner. If
the assistant suggests `setx` for permanence, note it truncates PATH at 1024 chars —
the GUI/Environment-Variables route is safer.

**Verify:** run `init`, then `where r` (Windows) resolves to a runner; the bare
name works from the repo root.

> *Aside — the `::` gotcha again.* At the `cmd` prompt, never append `:: note` after
> a command; cmd passes `::` as an argument.

### 06.4 — Extract shared logic into `lib/` (verify sameness)

Your tools duplicate yt-dlp setup, cookie/proxy handling, and text cleaning. Extract
it — **without changing behavior.**

> **Prompt:**
> "Extract logic used by more than one script into `lib/`: `lib/net.py` (proxy/
> cookie/impersonation helpers), `lib/textutil.py` (filename sanitizing, WebVTT→text
> cleaning), and `lib/youtube.py` (list/download/subtitle helpers over yt-dlp). Then
> rewrite the entry scripts as thin config + `main()` wrappers importing from `lib/`.
> Change ONLY structure — behavior must stay identical. Show me the before/after for
> one script."

**Expected response:** new `lib/` modules + slimmed entry scripts, plus a before/
after. Insist on "behavior identical" — this is the "verify sameness" skill from
Lesson 03, now at multi-file scale.

**Verify:** re-run `r`, `t`, `p`, `w`. Each must produce the *same* results as
before, and **skip-if-exists** must still recognize existing files. If any tool
re-downloads or writes somewhere new, the refactor changed behavior — feed that back
and ask for an exact restore.

### 06.5 — Add a quality-check tool

**Ask your assistant to** quantify Whisper accuracy vs. the YouTube captions.

> **Prompt:**
> "Create `code/compare_transcripts.py`: read a Whisper `.whisper.en.txt` and the
> YouTube caption `.txt` for the same video, strip timestamps, lowercase, tokenize,
> then report a rough word-accuracy % (difflib sequence similarity + a bag-of-words
> overlap) and the top divergent words. Get the file paths from `lib/paths.py`."

**Expected response:** a small script that prints a similarity %/WER and the biggest
word differences. On the sample content this tends to land around ~95% word accuracy
at `model_size=base` — cosmetic slips aside.

**Verify:** run it; you get a number and a short list of divergent words. Now "the
transcription is good" is a measured claim, not a vibe.

---

## When the AI misbehaves

- **The refactor changes behavior** (new folders, re-downloads, different output).
  That's the failure mode to catch: paste what differs and require exact sameness,
  structure-only.
- **`.sh` runners fail on Linux with `^M` / `bad interpreter`.** CRLF line endings —
  fix via `.gitattributes` (06.2) and re-checkout.
- **`init` doesn't make short names work.** Either it used `%CD%` (breaks when run
  from elsewhere) — switch to `%~dp0` — or PATH wasn't applied to the current
  session; re-run `init` in that same terminal.
- **A runner exists for only one OS.** Re-ask for the missing variant; always
  request both together.
- **Circular imports after extraction.** If `lib/youtube.py` imports a script that
  imports `lib/`, ask the assistant to keep `lib/` dependency-free of `code/`
  (helpers don't import entry scripts).

---

## What you have now

```
learn-better/
├── code/  (read_channel, read_transcript, list_playlists, transcribe_audio,
│           compare_transcripts)   # thin wrappers over lib/
├── lib/   (paths, net, textutil, youtube, __init__)
├── init.bat  + .gitattributes
├── c/r/t/p/w  runners (.bat + .sh)
└── data/  (git-ignored)
```
A clean, DRY codebase with a proper runner UX — and a measured quality number for
the Whisper step.

---

## Next → Lesson 07 — Summaries + word clouds (AI as author)

Next the AI stops being just your coder and becomes the *author*: it writes
structured summaries following a reusable skill file, while a script decides *what*
needs summarizing. Plus a word-cloud tool that splits data (Python) from rendering
(client-side JS).

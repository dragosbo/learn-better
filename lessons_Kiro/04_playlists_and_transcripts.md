# Lesson 04 — Playlists + transcripts, config-driven

**You'll build:** a playlist lister (`list_playlists.py`) and a transcript-only
tool (`read_transcript.py`), the `config/` folder with JSON configs so runs are
driven by data (not code edits), and your first one-letter runners.
**Complexity:** ⭐⭐⭐   **Est. time:** ~60–75 min

> **Assistant-agnostic.** Any AI assistant works.

---

## Prerequisites (from Lesson 03)

- A reproducible env (Python 3.12 + ffmpeg + `requirements.txt`).
- `lib/paths.py` as the single source of truth; `code/read_channel.py` repointed
  through it.

---

## Re-orient the AI (paste after a crash/restart)

```
Context: Lesson 04 of building a YouTube→study-material toolkit with your help.
OS: <your OS>. Repo: learn-better/ with lib/paths.py and a working
code/read_channel.py (audio + transcripts → data/, via yt-dlp, no API key).
Goal now: add code/list_playlists.py (list a channel's public playlists →
data/playlists.json) and code/read_transcript.py (transcripts only, per language);
introduce a config/ folder with JSON configs; add one-letter runners p / t / r.
Last thing done: <e.g. "wrote list_playlists.py">. Please continue from there.
```

---

## Concepts (what this lesson teaches about working with AI)

1. **Config over code edits.** Moving the "what to process" choices into JSON files
   means you (and the assistant) change *data*, not logic — safer and repeatable.
2. **Reuse the source of truth.** Every new tool imports paths from `lib/paths.py`,
   so the assistant never invents a new output location.
3. **Small runners, big convenience.** A one-line launcher per tool keeps commands
   short and consistent across the project.

---

## Step-by-step

### 04.1 — Add a playlist lister (no API key)

**Ask your assistant to** write a tool that lists a channel's public playlists to
`data/playlists.json`, using yt-dlp (no API key), reading paths from `lib/paths.py`.

> **Prompt:**
> "Create `code/list_playlists.py` (I'm on `<your OS>`, env has yt-dlp): given a
> `CHANNEL` set at the top (an `@handle`, a `UC…` id, or a full channel URL), list
> the channel's **public** playlists (title, id, video count) using yt-dlp with
> `extract_flat` — no API key. Save to `data/playlists.json` (get the path from
> `lib/paths.py`). Sort playlists alphabetically. Before coding, list the file and
> behavior; then write it."

**Expected response:** a plan, then `code/list_playlists.py` reading `CHANNEL` from
the top, writing `data/playlists.json` via `paths.DATA_DIR`. It should note that
**only public playlists are visible** without authentication.

**Verify:** set `CHANNEL` to a real handle, run it, and open `data/playlists.json`
— you should see a list of playlists with counts.

> *Aside — private playlists.* If you ask "why don't my private ones show up?",
> the honest answer is: they're not enumerable without authentication (an API key
> won't help — only OAuth would). Making them **public** in YouTube Studio is the
> simple fix. Good example of the assistant telling you a real limitation instead
> of inventing a workaround.

### 04.2 — Add a transcript-only tool

**Ask your assistant to** write `read_channel.py`'s lighter sibling: transcripts
only, one cleaned file per available language.

> **Prompt:**
> "Create `code/read_transcript.py`: for a source set at the top (playlist / channel
> / search + LIMIT), save ONE cleaned, timestamped `.txt` per available language to
> `data/transcripts/` (path from `lib/paths.py`), named `<title> [<id>].<lang>.txt`.
> Convert WebVTT to readable `[HH:MM:SS] text`, strip tags, skip languages already
> on disk. Reuse the yt-dlp + cookie/impersonation approach from read_channel.py.
> No audio download."

**Expected response:** `code/read_transcript.py` that writes per-language `.txt`
files and skips existing ones. It should share the same yt-dlp settings as
`read_channel.py` (a hint that shared logic is begging to be extracted — that's
Lesson 06).

**Verify:** run it on a captioned video; `data/transcripts/` gets one `.txt` per
language. A second run skips them.

### 04.3 — Introduce the `config/` folder + JSON configs

**Ask your assistant to** make a tool config-driven, so you pick *what to process*
in a JSON file instead of editing the script.

> **Prompt:**
> "Introduce a `config/` folder. Design a small JSON config (`config/config_transcribe.json`)
> with a `select_by` field (`name` | `id` | `all`) and a `select` list, so I can
> choose which items to process without editing code. Update one tool to accept an
> optional config path as its first CLI argument (`sys.argv[1]`), falling back to a
> sensible default when none is given. Show me the config and how the tool reads it."

**Expected response:** a `config/config_transcribe.json` and a tool that reads a
config path from `sys.argv[1]`. This "optional config-path arg + JSON `select_by`"
pattern recurs across the whole project — establish it cleanly here.

**Verify:** run the tool with and without a config path; both work, and the config
actually changes what's processed.

### 04.4 — Add one-letter runners (`p`, `t`, `r`)

**Ask your assistant to** create thin launcher scripts so you don't retype
`python code/…` — and to make **both** a Windows `.bat` and a Unix `.sh` in one go.

> **Prompt:**
> "Create tiny runner pairs so I can launch tools with one letter from the repo
> root: `p` → `list_playlists.py`, `t` → `read_transcript.py`, `r` →
> `read_channel.py`. Give me BOTH `<letter>.bat` (Windows) and `<letter>.sh`
> (Linux/macOS) for each. The `.sh` should activate a conda env if present, else
> use the current `python`. They should pass through an optional config argument."

**Expected response:** six tiny files (`p.bat`/`p.sh`, `t.bat`/`t.sh`,
`r.bat`/`r.sh`) that call `python code/<script>.py %*` / `"$@"`. **Always ask for
both platform variants in one prompt** — it's the prompt-discipline habit that
saves round-trips.

**Verify:** `p` (or `p.bat` / `./p.sh`) runs the lister; the config arg passes
through, e.g. `t config/config_transcribe.json`.

> *Aside — the `::` gotcha (Windows cmd).* Don't type inline `::` notes after a
> command at the prompt (`t  :: my note`) — cmd passes `::` as an argument. Run the
> command alone. (Lesson 06 revisits runners + PATH.)

---

## When the AI misbehaves

- **The lister returns fewer playlists than you expect, or warns "unable to extract
  yt initial data."** Usually yt-dlp pagination variance or an outdated yt-dlp, not
  lost data. Ask for retries + dedupe, and update yt-dlp; compare against YouTube
  Studio for the true total.
- **It hard-codes `data/...` paths again.** Point it back at `lib/paths.py` — every
  new tool imports paths, no exceptions.
- **The config schema drifts between tools.** Keep `select_by` / `select` consistent
  across configs; tell the assistant to mirror the shape it already used.
- **A runner only comes in one flavor.** Re-ask for the missing `.bat` or `.sh`;
  requesting both up front avoids this.
- **A run "hangs forever."** A single stuck network request can stall counting —
  ask for a socket timeout + a live progress line so it doesn't *look* frozen.

---

## What you have now

```
learn-better/
├── code/
│   ├── read_channel.py
│   ├── read_transcript.py      # transcripts only, per language
│   └── list_playlists.py       # channel → data/playlists.json
├── config/
│   └── config_transcribe.json  # select_by / select
├── lib/paths.py
├── p.bat p.sh  t.bat t.sh  r.bat r.sh   # one-letter runners
└── data/  (playlists.json, transcripts/, audio/)   # git-ignored
```
Config-driven runs and quick launchers — the shape every later tool follows.

---

## Next → Lesson 05 — Whisper transcription

Some clips have captions disabled. Next you'll add local speech-to-text with
`faster-whisper` (no API key, CPU-friendly), driven by the same config pattern —
and handle the reality that transcription runs can be *long*.

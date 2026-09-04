# How to test — learn-better

A chronological list of the manual tests we ran, each as a single `.bat`
command from the **repo root** with the `learn-better` env active. They are
ordered the way we built and validated them, so you can re-run the whole story
top to bottom.

> Run `c` first (or `c.bat`) to activate the conda env, unless a test line
> already includes activation. All Whisper config files now live in `config/`.
>
> Note on output: on Windows `cmd`, long transcription output can look noisy;
> that is normal. What matters is the final summary line each tool prints.

---

## Quick copy-paste examples

Run these from the repo root (`d:\work3\learn-better`) in a `cmd` terminal. A few
representative commands (see the full list further down):

```cmd
c                                          :: activate the env (once per terminal)

p                                          :: Phase A - list playlists -> data/playlists.json

t                                          :: Phase B - transcripts only -> transcripts/
r                                          :: Phase B - audio + transcripts for a source

w                                          :: C1 - Whisper the default clip
w config\config_transcribe.id.json         :: C2 - transcribe by video id
w config\config_transcribe.source.json     :: C3 - captions-first source flow
w config\config_transcribe.translate.json  :: C4 - French clip -> English
s                                          :: C5 - prepare summaries (both sources)

d                                          :: W1 - word cloud JSON for one transcript
wc config\config_wordcloud.json            :: W3 - batch: one cloud per transcript
wc config\config_wordcloud.merge.json      :: merge: many transcripts -> one cloud
```

If the `c` / `w` / `s` shortcuts are not on your PATH, use the `.bat` name or the
script directly, e.g.:

```cmd
w.bat config\config_transcribe.id.json
python code\transcribe_audio.py config\config_transcribe.id.json
```

---

## Prerequisites (one time)

```cmd
c                 :: activate the learn-better conda env (c.bat)
```

- Python 3.12 env with `pip install -r requirements.txt` done.
- `ffmpeg` on PATH (for mp3 conversion / Whisper audio).
- Deno installed (`winget install DenoLand.Deno`) to silence the yt-dlp
  "no JavaScript runtime" warning — optional, the tools work without it.

---

## Phase A — Playlists (no API key)

```cmd
p                 :: list a channel's public playlists + videos -> data/playlists.json
```
**Expect:** a printed list of playlists, then `data/playlists.json` written.
Delete the file and re-run to confirm it regenerates.
(Set `CHANNEL` at the top of `code/list_playlists.py` first.)

---

## Phase B — Download tools use the reusable lib/ (regression)

These prove the `lib/` refactor kept behavior identical.

```cmd
t                 :: transcripts only, one file per language -> transcripts/
r                 :: audio + transcripts for a playlist/channel/search
```
**Expect:** videos listed; transcripts saved to `transcripts/`; audio saved to
`audio/`; files already present are skipped. (Configure the source at the top of
`code/read_channel.py` / `code/read_transcript.py`.)

---

## Phase C — Whisper speech-to-text (`w` / transcribe_audio.py)

`w` takes an optional config file from `config/`. With no argument it uses
`config/config_transcribe.json`.

### C1 — transcribe one file (proof of concept)

```cmd
w                 :: uses config\config_transcribe.json (default: name "Git and GitHub")
```
**Expect:** the Git & GitHub clip transcribed to
`generated_transcripts/Git and GitHub Tutorial for Beginners [tRZGeaHPoaw].whisper.en.txt`,
ending with `-> N chars written to ...`. (First run downloads the Whisper model.)

We also validated quality with a helper (not a .bat):
```cmd
python code\compare_transcripts.py   :: ~95% word accuracy vs. YouTube captions
```

### C2 — select WHICH files, and skip-if-exists

Selection by **name substring**:
```cmd
w config\config_transcribe.name.json   :: names containing "VSCode" or "GitLab Pipeline"
```
**Expect:** `Selected 2 file(s)`, each transcribed to `generated_transcripts/`.

Selection by **video id** (ids are the `[<id>]` in the file name, same as
`data/playlists.json`):
```cmd
w config\config_transcribe.id.json     :: ids F2DBSH2VoHQ + 9llCMADxvzI
```
**Expect (second run):** both report `= exists, skipping`, ending
`0 new transcript(s) written, 2 skipped` — proves skip-if-exists.

Default again (Git clip, already done):
```cmd
w                                      :: caption/whisper already exists -> skipped
```

(There is also `config\config_transcribe.all.json` for every audio file — slow,
so we did not run it routinely.)

### C3 — source flow: captions first, Whisper fills the gaps

```cmd
w config\config_transcribe.source.json :: a playlist/channel/search
```
**Expect:** each video either `caption transcript available -> no Whisper needed`
or `NO caption transcript -> falling back to Whisper`. Ends with a tally like
`3 had captions, 0 Whisper-transcribed, 0 skipped`. If every clip has captions,
no model loads — that is the correct "only fill gaps" behavior.

> After this we added `no_warnings` to the yt-dlp calls (and recommend Deno), so
> re-running shows no "No supported JavaScript runtime" warning.

### C4 — translation + same-language transcripts (`task`)

Whisper's `translate` outputs **English only** (it cannot target fr/ro). These
four one-command configs cover the cases:

```cmd
w config\config_transcribe.translate.json     :: French audio  -> ENGLISH  (.whisper.en.txt)
w config\config_transcribe.translate.ro.json  :: Romanian audio-> ENGLISH  (.whisper.en.txt)
w config\config_transcribe.fr.json            :: French audio  -> FRENCH   (.whisper.fr.txt)
w config\config_transcribe.ro.json            :: Romanian audio-> ROMANIAN (.whisper.ro.txt)
```
**Expect:** `translate` runs print `Translating to English` and write
`.whisper.en.txt`; the `fr`/`ro` runs print `Transcribing`,
`detected source language: fr|ro`, and write `.whisper.<lang>.txt`.

> These use the source flow, so a clip that already has an English caption skips
> Whisper. To force the Whisper path, use clips without an English caption (raise
> `limit` or tweak the `search` in the config).

### C5 — summaries read BOTH caption and Whisper transcripts

```cmd
s                 :: prep summaries: scan transcripts/ + generated_transcripts/
```
**Expect:** one line per video, tagged `(caption)` or `(whisper)`, captions
preferred, deduped by video id (no clip listed twice). Then a paste-ready
instruction for Kiro whose paths point at the right folder
(`transcripts/...` vs `generated_transcripts/...`). Paste that into Kiro to write
`summaries/*.summary.md`.

**End-to-end:** `w config\config_transcribe.source.json` to Whisper a caption-less
clip, then `s` — that clip should now appear as `(whisper) [NEEDS summary]`.

---

## Phase W — Word cloud (`d` / `wc` + wordcloud.html)

Data-only Python + client-side JS renderer. No matplotlib. Output goes to
`data/wordclouds/*.word_cloud.json` (skip-if-exists).

### W1 — one transcript → JSON

```cmd
d                 :: build word_cloud.json for the INPUT set atop make_wordcloud.py
```
**Expect:** `data/wordclouds/<title> [<id>].word_cloud.json` with sensible top
words (e.g. Git clip: git/type/file/branch/commit), stopwords absent. Second run
prints `Already exists, skipping`.

### W3 — batch selection (config)

```cmd
wc config\config_wordcloud.json    :: default select_by="all" -> one cloud per video
```
**Expect:** a selection list, then per-file `-> en: N tokens ... | top words`,
ending `N written, M skipped`. Re-run → all skipped. Edit the config's
`select_by`/`select` for name/id subsets; `min_length`/`max_words`/`language`/
`stopwords_extra` tune the tokenizer.

### Merge — combine 2+ transcripts into ONE cloud

```cmd
wc config\config_wordcloud.merge.json   :: 3 git videos -> data/wordclouds/git-series.word_cloud.json
```
**Expect:** `Merging 3 transcript(s) -> one cloud 'git-series'`, combined top
words spanning all three (git/pipeline/job/commit), one file written.

### Language guard (should REJECT)

A word cloud uses one stopword list, so a batch must be single-language. To see
the guard fire, edit `config\config_wordcloud.json` → `"language": "fr"` (files
are `.en`), then:
```cmd
wc config\config_wordcloud.json
```
**Expect:** `!! LANGUAGE MISMATCH — refusing to run a mixed-language batch`,
listing the `[en]` files, nothing written. Reset to `"language": "en"` after.

### View any result

Open `wordcloud.html` → **Load a JSON** → pick a file from `data/wordclouds/`.
Word size scales with frequency. (Or serve the folder: `python -m http.server`
then `wordcloud.html?file=data/wordclouds/<base>.word_cloud.json`.)

---

## Quick reference — all runners

| Cmd | Script | Purpose |
|-----|--------|---------|
| `c` | (activate) | Activate the `learn-better` conda env |
| `p` | `list_playlists.py` | List a channel's public playlists -> `data/playlists.json` |
| `t` | `read_transcript.py` | Transcripts only, per language -> `transcripts/` |
| `r` | `read_channel.py` | Audio + transcripts for a source |
| `w` | `transcribe_audio.py` | Whisper STT / translate; `w config\config_transcribe.<mode>.json` |
| `s` | `make_summaries.py` | List transcripts needing a summary; print AI instruction |
| `d` | `make_wordcloud.py` | One transcript -> `word_cloud.json` (uses the script's `INPUT`) |
| `wc` | `make_wordcloud.py` | Batch/merge word clouds; `wc config\config_wordcloud.json` |

## Whisper config files (in `config/`)

| File | select_by / task | What it tests |
|------|------------------|---------------|
| `config_transcribe.json` | name / transcribe | Default (Git & GitHub clip) |
| `config_transcribe.name.json` | name / transcribe | Pick by name substring |
| `config_transcribe.id.json` | id / transcribe | Pick by video id + skip-if-exists |
| `config_transcribe.all.json` | all / transcribe | Every audio file (slow) |
| `config_transcribe.source.json` | source / transcribe | Captions-first, Whisper fills gaps |
| `config_transcribe.translate.json` | source / translate | French -> English |
| `config_transcribe.translate.ro.json` | source / translate | Romanian -> English |
| `config_transcribe.fr.json` | source / transcribe (fr) | French audio -> French text |
| `config_transcribe.ro.json` | source / transcribe (ro) | Romanian audio -> Romanian text |

## Word cloud config files (in `config/`)

| File | mode | What it tests |
|------|------|---------------|
| `config_wordcloud.json` | select_by=all | Batch: one cloud per video |
| `config_wordcloud.merge.json` | merge (id) | Combine the 3 git videos into `git-series` |

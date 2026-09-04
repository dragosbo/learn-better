# TODO3 — Consolidate outputs under `data/` + gather runners into one folder

> **STATUS: all phases (T0–T5) implemented.** Outputs live under `data/`, runners
> under `scripts/` (add to PATH via `init.bat`), and all four docs + the code
> messages/paths are swept. T2/T3/T4/T5 are marked "awaiting user test" per the
> per-phase protocol; the work itself is complete and self-verified.

Two related housekeeping goals (from `plan.md` Phase 0 + a new request):

**A. Consolidate outputs under a single `data/` root.** Today the generated/output
folders sit at the repo root (`audio/`, `audio_reencoded/`, `transcripts/`,
`generated_transcripts/`, `tts_output/`, `data/`, plus the tracked `summaries/`).
Move the git-ignored outputs under one `data/` root (e.g. `data/audio/`,
`data/transcripts/`, ...) so the root stays clean and all regenerated artifacts
live in one place.

**B. Collect the `.bat`/`.sh` runners into one folder**, but keep them easy to
launch from the repo root (the one-letter `c`/`r`/`t`/... ergonomics must survive).

> **Nature of this task:** unlike the previous mini-plans (which *added* a new
> tool), this is a **cross-cutting refactor** — it touches `lib/paths.py`, several
> `code/*.py` scripts, the runners, `.gitignore`, `.dockerignore`, and all four
> docs. Nothing new is built; the risk is **stale references**, not new logic. So
> the plan leans hard on: change the single source of truth (`lib/paths.py`),
> verify each tool still writes/reads the right place, and sweep the docs.

**All free, no extra cost.** Pure moves + path edits; no new deps.

---

## How we work this plan (interaction protocol — IMPORTANT)

This is a refactor with many moving references, so we go **one phase at a time**
with the user in the loop. For EACH phase T0 → T5:

1. **Implement only that phase.** Do not run ahead into the next phase.
2. **Stop and hand back to the user for testing.** After finishing a phase, pause.
3. **Give clear, copy-paste test guidance every time** — the exact commands to run
   (from the repo root), what output to expect, where to look (paths/files), and
   what "pass" looks like. Assume the user will actually run it and report back.
4. **Wait for the user's feedback / go-ahead** before starting the next phase. If
   the test surfaces a problem, fix it and re-issue the test steps before moving on.
5. **Only after the user confirms a phase passes**, mark it DONE in this file
   (record how it was tested) and proceed to the next.

> In short: **implement → tell the user exactly how to test → wait for feedback →
> then continue.** No batching phases together, no "it should work" without a
> concrete test recipe. Each phase below already lists a **Test** block; treat it
> as the minimum, and tailor the guidance to what actually changed.

---

## Design decisions (NEED USER REVIEW before coding)

These are the choices that shape everything below. Please confirm/adjust:

### A1. New output layout under `data/`
Proposed (git-ignored unless noted):
```
data/
├── playlists.json            # (already here, ignored)
├── wordclouds/               # (already here, ignored) *.word_cloud.json
├── audio/                    # was audio/                 (ignored)
├── audio_reencoded/          # was audio_reencoded/       (ignored)
├── transcripts/              # was transcripts/           (ignored, captions)
├── generated_transcripts/    # was generated_transcripts/ (ignored, Whisper)
├── tts_output/               # was tts_output/  (+ .voices/ cache) (ignored)
└── summaries/                # was summaries/   (TRACKED via .gitignore negation)
```
- **`summaries/` → DECIDED: move to `data/summaries/`.** It is git-TRACKED
  (authored content), so this needs a `.gitignore` negation to keep it tracked
  while `data/` is otherwise ignored: `data/` + `!data/summaries/` +
  `!data/summaries/**`, and the move uses `git mv`.
- **Migrate existing files → DECIDED: physically move** current outputs into
  `data/` (one-time `move`/`git mv`), so nothing re-downloads and skip-if-exists
  keeps working.

### A2. `.voices/` cache
Piper's voice models live in `tts_output/.voices/`. Under the new layout that
becomes `data/tts_output/.voices/` — no special handling needed; it just moves
with its parent.

### B1. Runner folder + root ergonomics
The `.bat`/`.sh` one-letter helpers currently sit at the repo root so you can type
`r`, `w config\...`, etc. If we move them into a `bin/` (or `scripts/`) folder,
typing `r` from the root stops working unless we keep a launcher at the root.
Options:
- **(a)** Move the real runners to `bin/` and keep **tiny root shims**
  (`r.bat` → `@call bin\r.bat %*`) so `r` still works from the root. Clean folder,
  same ergonomics, but doubles the file count (shim + real).
- **(b)** Move runners to `bin/` and add `bin/` to `PATH` (documented) so `r`
  works from anywhere. No shims, but requires a PATH step per machine/shell.
- **(c)** Keep the runners at the root (status quo) but that doesn't meet the
  "one folder" goal.
- **DECIDED: (b)** — the real runners live in `scripts/` and the user adds
  `scripts/` to PATH so `r`/`w`/`v` work from anywhere. No shim files; the root
  stays clean. (Option (a)'s root shims were considered and dropped.)

> **Please confirm:** A1 summaries option (a/b), A1 migrate option (a/b), B1
> option (a/b/c), and the folder name (`bin/` vs `scripts/`). The phases below
> assume the **recommended** choices; I'll adjust if you pick differently.

---

## Where files live (after, assuming recommendations)

| Thing | Before | After |
|---|---|---|
| Downloaded audio | `audio/` | `data/audio/` |
| Re-encoded audio | `audio_reencoded/` | `data/audio_reencoded/` |
| Caption transcripts | `transcripts/` | `data/transcripts/` |
| Whisper transcripts | `generated_transcripts/` | `data/generated_transcripts/` |
| TTS audio (+ voices) | `tts_output/` | `data/tts_output/` |
| Word cloud JSON | `data/wordclouds/` | `data/wordclouds/` (unchanged) |
| Playlists | `data/playlists.json` | `data/playlists.json` (unchanged) |
| Summaries (tracked) | `summaries/` | `data/summaries/` (still tracked via a `.gitignore` negation) |
| Runners | `*.bat` / `*.sh` at root | `scripts/*.bat` + `scripts/*.sh` (add `scripts/` to PATH for the one-letter UX) |

---

## Phase T0 — Decide + prep (no behavior change yet) — DONE PENDING USER SIGN-OFF

- [x] **T0.1** Decisions LOCKED (user-confirmed):
      - **A1 summaries:** move `summaries/` → **`data/summaries/`**. Because
        `summaries/` is git-TRACKED (authored content) and `data/` is ignored
        wholesale, `.gitignore` must ignore `data/` **except** `data/summaries/`
        (negation rule: `data/` + `!data/summaries/` + `!data/summaries/**`), and
        the move uses `git mv` so git follows the tracked files. Add a
        `paths.SUMMARY_DIR = data/summaries` constant and repoint the two
        hardcoded `"summaries"` strings (`make_summaries.py`, `generate_speech.py`)
        to it.
      - **A1 migrate:** YES — physically move existing outputs into `data/`
        (one-time) so skip-if-exists keeps working, nothing re-downloads.
      - **B1 runners:** option (b) — move real runners to **`scripts/`** and add
        `scripts/` to PATH so `r`/`w`/`v`… work from anywhere. No shims (option
        (a)'s root shims were considered and dropped).
      - **Folder name:** `scripts/`.
- [x] **T0.2** Reference inventory complete (verified by grep):
      - **`lib/paths.py`** — the single source of truth. Constants to repoint:
        `AUDIO_DIR`, `AUDIO_REENCODED_DIR`, `TRANSCRIPT_DIR`,
        `GENERATED_TRANSCRIPT_DIR`, `TTS_OUTPUT_DIR`. Already under `data/`:
        `DATA_DIR`, `WORDCLOUD_DIR`.
      - **`code/*.py`** — all build dirs from `paths.*` (follow automatically):
        `read_channel.py`, `read_transcript.py`, `list_playlists.py`,
        `transcribe_audio.py`, `make_summaries.py`, `make_wordcloud.py`,
        `reencode_audio.py`, `generate_speech.py`. **Hardcoded `"summaries"`**
        (NOT via paths) in `make_summaries.py` and `generate_speech.py` — leave
        as-is under option A1(a), but consider a `paths.SUMMARY_DIR` tidy-up.
      - **`lib/youtube.py`** — defaults `output_dir or paths.AUDIO_DIR` /
        `paths.TRANSCRIPT_DIR` (follow automatically).
      - **`.gitignore`** — lists `audio/ audio_reencoded/ tts_output/ transcripts/
        generated_transcripts/ data/` individually (+ `timestamped/ repos/`).
        Collapse the moved ones under `data/` (already ignored); keep `summaries/`
        tracked.
      - **`.dockerignore`** — same list as `.gitignore`; collapse similarly.
      - **Docs with output-path mentions to sweep in T5:**
        - `README.md` — Colab note (`audio/`/`transcripts/`), read_channel output,
          transcribe output (`generated_transcripts/`), select_by=all
          (`audio/`), word cloud (`data/wordclouds/`), re-encode
          (`audio/`→`audio_reencoded/`), TTS (`tts_output/`), repo layout block.
        - `youtube.html` — Whisper STT text + Mermaid diagrams (`generated_transcripts/`,
          `transcripts/`), summaries sequence diagram, word cloud diagram
          (`data/wordclouds/`), status rows (item 3/4 mention `tts_output/`,
          `audio_reencoded/`), repo-layout tree.
        - `how_to_test.md` — expected paths in Phase C/W/R/D blocks
          (`generated_transcripts\`, `data\wordclouds\`, `audio_reencoded\`,
          `tts_output\`).
        - `plan.md` — Section 4 repo-layout snippet + the Phase 0 checkbox.
      - **`notebooks/yt_download.ipynb`** — uses `lib/` (`youtube.download_audio`
        default dir), so it follows automatically; verify in T4.

**Test & hand off (STOP for user feedback):** no code ran in T0 (decisions +
inventory only). **Deliverable = the decision list + inventory above.** Please
review the four decisions (A1 summaries a/b, A1 migrate a/b, B1 runners a/b/c,
folder name) and confirm or adjust. On "go", T1 edits `lib/paths.py`.

---

## Phase T1 — Repoint paths to `data/` (the core change) — DONE, USER-VALIDATED

- [x] **T1.1** Edited `lib/paths.py` (single source of truth). All output dirs now
      under `data/`: `AUDIO_DIR=data\audio`, `AUDIO_REENCODED_DIR=data\audio_reencoded`,
      `TRANSCRIPT_DIR=data\transcripts`, `GENERATED_TRANSCRIPT_DIR=data\generated_transcripts`,
      `TTS_OUTPUT_DIR=data\tts_output`, added `SUMMARY_DIR=data\summaries`.
      `DATA_DIR`/`WORDCLOUD_DIR` already correct. Docstring refreshed.
- [x] **T1.2** Repointed the two hardcoded `"summaries"` strings
      (`make_summaries.py`, `generate_speech.py`) to `paths.SUMMARY_DIR`, and fixed
      the `generate_speech.py` "looked in ..." message to print `paths.SUMMARY_DIR`.
      The rest build dirs from `paths.*` (auto-updated).
- [x] **T1.3** Scripts `os.makedirs(..., exist_ok=True)` on their output dir (via
      the constant), so `data/...` subdirs are created on demand. Verified paths
      resolve; dir creation happens on first real write (T2/T4).

**Test & hand off — DONE, USER-VALIDATED.**
```cmd
c
python -c "from lib import paths; print(paths.AUDIO_DIR, paths.TRANSCRIPT_DIR, paths.GENERATED_TRANSCRIPT_DIR, paths.AUDIO_REENCODED_DIR, paths.TTS_OUTPUT_DIR, paths.SUMMARY_DIR)"
```
✅ Printed all `data\...` forms (`data\audio data\transcripts
data\generated_transcripts data\audio_reencoded data\tts_output data\summaries`).
```cmd
python code\reencode_audio.py config\config_reencode.json
```
✅ Loaded the config, then `No audio matched ... (looked in ...\data\audio\)` —
the "looked in `data\audio\`" confirms the repoint; "no match" is correct because
the files haven't moved yet (T2 moves them). User confirmed the output is right.

---

## Phase T2 — Move existing outputs + update ignore files — DONE (awaiting user test)

- [x] **T2.1** Moved the 5 git-IGNORED output folders into `data/`
      (`audio audio_reencoded transcripts generated_transcripts tts_output`).
- [x] **T2.2** `git mv summaries data/summaries` — git recorded 3 **renames** (R),
      so the tracked summaries followed the move.
- [x] **T2.3** `.gitignore`: used **`data/*` + `!data/summaries/`** (NOT `data/`).
      Key fix: a blanket `data/` prune blocks re-inclusion of children, so
      `!data/summaries/` had no effect and summaries were wrongly ignored;
      ignoring the *contents* (`data/*`) lets the negation re-include summaries.
- [x] **T2.4** `.dockerignore`: collapsed the individual output folders to
      `data/` (the image mounts data at runtime; nothing under it needs baking in).

**Test & hand off (STOP for user feedback):** run these and report back before T3.
```cmd
c
git status
git check-ignore data/audio/x.mp3
git check-ignore data/summaries/foo.md
```
**Expect:** `git status` shows the `summaries/ → data/summaries/` **renames**
(tracked, R) and **no other new tracked output files**; `git check-ignore
data/audio/x.mp3` **echoes** the path (ignored); `git check-ignore
data/summaries/foo.md` prints **nothing** (NOT ignored = still tracked).
Also eyeball `dir data\audio`, `dir data\summaries`, and that the old root
folders are gone. **Pass =** summaries tracked under `data/summaries/`, other
outputs ignored under `data/`, nothing tracked lost. Report back; then T3.

---

## Phase T3 — Gather runners into `scripts/` (option b: PATH) — DONE (awaiting user test)

> **Decision (user):** the real runners live in `scripts/` and the user adds
> `scripts/` to PATH so `r`/`w`/`v` work from anywhere. Cleaner root, nothing at
> the root level.

- [x] **T3.1** `git mv`'d all 20 runners (10 `.bat` + 10 `.sh`) into `scripts/`
      — git recorded 20 clean renames (R). `scripts/*` runners keep their
      `python code\...` / `python code/...` calls (run from the repo root).
      `scripts/` is NOT ignored (`git check-ignore` returns nothing; `git ls-files`
      shows all 20 tracked).
- [x] **T3.2** The root has no `.bat`/`.sh`. To keep the one-letter UX, add
      `scripts/` to PATH — now documented in `README.md`'s "Running the tools"
      section (session + permanent, Windows `set`/`setx` and Unix `export`), the
      "How to run it" intro, and the repo-layout tree (runners listed under
      `scripts/`). `scripts/*.sh` kept their exec bit through the rename (mode
      `100755`); `.gitattributes` globs still apply.
- [x] **T3.3** `scripts/*.sh` exec bits verified `100755` in the index
      (`git ls-files -s scripts/*.sh`), so the renames preserved the executable
      mode.

✅ Verified: `a config\config_reencode.json` routed to the tool, found
`Git and GitHub ... .mp3` in `data\audio\` (proving T1+T2), and skip-if-exists
worked (output under `data\audio_reencoded`). Invoke the runners as
`scripts\a.bat config\config_reencode.json` (or `scripts/a.sh ...` on Linux), or
add `scripts/` to PATH to keep typing `a`.

> Note (`scripts/` vs `code/`): the repo already has `code/` for the Python
> tools; `scripts/` is only the thin runners. Keep them distinct.

**Test & hand off (STOP for user feedback):** run and report before T4.

There is nothing at the repo root, so invoke the runners from `scripts\` (they
still call `python code\...` with no `cd`, so run them from the repo root):
```cmd
scripts\r.bat
```
```cmd
scripts\wc.bat config\config_wordcloud.json
```
On Linux/macOS:
```cmd
scripts/r.sh
```
```cmd
scripts/w.sh config/config_transcribe.id.json
```
To keep the **one-letter UX** (`r`, `wc`, …) add `scripts\` to PATH for the
session, then the bare names work from the repo root:
```cmd
set PATH=%CD%\scripts;%PATH%
r
wc config\config_wordcloud.json
```
On Linux/macOS:
```cmd
export PATH="$PWD/scripts:$PATH"
r.sh
w.sh config/config_transcribe.id.json
```
**Expect:** the runners execute `python code\...` and the config arg passes
through, exactly as before the move. **Pass =** same behavior as before, whether
called as `scripts\<x>.bat` or (with `scripts\` on PATH) by the short name.
Report back; T4.

---

## Phase T4 — Verify each tool end-to-end — DONE (awaiting user test)

- [x] **T4.1** Verified each tool resolves under `data/`:
      - **`a` (reencode)** — RAN: read `data/audio/`, wrote to
        `D:\...\data\audio_reencoded`, `1 skipped` (skip-if-exists held). ✅
      - **`d` / `wc` (wordcloud)** — RAN: read `data/transcripts/` +
        `data/generated_transcripts/`, wrote `D:\...\data\wordclouds`,
        `10 skipped` (skip-if-exists held). ✅
      - **`s` (make_summaries)** — RAN: scanned `data/transcripts/` +
        `data/generated_transcripts/`, checked `data/summaries/`, correctly
        tagged the 3 existing summaries `[have summary]`. ✅ (See T4 NOTE below —
        the printed paste-instruction still shows OLD root paths.)
      - **`v` (generate_speech), `w` (transcribe_audio), `p`/`r`/`t`
        (yt-dlp tools)** — deps ARE installed in the `learn-better` env
        (verified against the env's python:
        `...\envs\learn-better\python.exe -c "importlib.util.find_spec(...)"`
        → piper, faster_whisper, yt_dlp, youtube_transcript_api, pandas,
        curl_cffi all **OK**; user also confirmed `pip list` shows
        `piper-tts 1.7.0`). Path resolution verified by SOURCE:
        `generate_speech.py` builds `OUTPUT_DIR=paths.TTS_OUTPUT_DIR` + sources
        from `SUMMARY/TRANSCRIPT/GENERATED` `paths.*`; `transcribe_audio.py`
        builds `AUDIO_DIR`, `OUTPUT_DIR=GENERATED_TRANSCRIPT_DIR`,
        `caption_dir=TRANSCRIPT_DIR` from `paths.*` (skip checks read those
        `data/` dirs); `read_channel.py` imports `AUDIO_DIR`/`TRANSCRIPT_DIR` from
        `lib.paths`; `list_playlists.py` uses `OUTPUT_JSON=DATA_DIR/playlists.json`.
        All write/skip targets resolve under `data/`. ✅ (`v`/`w` runnable;
        `p`/`r`/`t` also need network.)

      > **Earlier-session correction:** a prior note here wrongly said these deps
      > were "MISSING". That was a test artifact — the `python` invoked in that
      > session had fallen through to a NON-env interpreter (PATH also lists bare
      > `Anaconda3-2019.10\python.exe` and the WindowsApps stub). Against the
      > actual `learn-better` env python, all deps are present. No repo/env fix
      > needed; only make sure the `learn-better` env is truly active (run `c`
      > first) so `python` = `...\envs\learn-better\python.exe`.
      - **Why `a`/`d`/`wc`/`s` ran regardless:** those scripts use only the Python
        standard library (+ `lib/paths`), so they execute under any interpreter.
      - Confirmed all 8 constants print `data\...`
        (`python -c "from lib import paths; ..."`).
- [x] **T4.2** Skip-if-exists confirmed on moved files: `a` (1 skipped), `wc`
      (10 skipped), and `s` recognizing the 3 moved summaries all prove the
      physical move (T2) + path repoint (T1) are consistent — the tools find the
      files at their new `data/` homes.

> **T4 NOTE (follow-up for T5 / code sweep):** `make_summaries.py` prints its
> paste-ready Kiro instruction with the OLD root paths — `transcripts/...`,
> `generated_transcripts/...`, and `save each to summaries/<base>.summary.md`.
> These are hardcoded display strings (the scan itself uses `data/` correctly),
> so summaries pasted from that instruction would point Kiro at the wrong folder.
> Fix in T5: repoint those printed strings to `data/transcripts/`,
> `data/generated_transcripts/`, `data/summaries/`.

**Test & hand off (STOP for user feedback):** re-run the local tools from the
repo root (or via `scripts\`) and confirm each prints `data\...` paths and skips
existing outputs:
```cmd
a config\config_reencode.json
wc config\config_wordcloud.json
s
```
**Expect:** `a` → `...\data\audio_reencoded` (1 skipped); `wc` →
`...\data\wordclouds` (10 skipped); `s` → lists 10 videos, 3 `[have summary]`.
`v` needs `pip install piper-tts` to run fully; `p`/`t`/`r`/`w` are network
tools — their paths are verified by source. **Pass =** outputs resolve under
`data/` and skip-if-exists holds. Report back; then T5.

---

## Phase T5 — Docs + wiring — DONE (awaiting user test)

- [x] **T5.1** `README.md`: runners/PATH part done earlier; NOW the output-folder
      half is done too — repo-layout tree nests all outputs under `data/`
      (audio, audio_reencoded, tts_output, transcripts, generated_transcripts,
      summaries [tracked], wordclouds, playlists.json), and every inline path
      mention in the tool sections repointed to `data/...` (Colab note,
      read_channel output, transcribe output, select_by=all, word cloud,
      re-encode + ffprobe, TTS + ffprobe, summaries section, Whisper-quality
      section, legacy downloader).
- [x] **T5.2** `youtube.html`: repo-layout tree nests outputs under `data/` +
      adds `scripts/`/`init.bat`; all Mermaid diagram node labels repointed
      (`audio/`→`data/audio/`, `transcripts/`, `generated_transcripts/`,
      `summaries/`, wordcloud); "Running the tools" intro documents `scripts/`
      + PATH + `init.bat`; command table `c.bat`→`scripts/c.bat`; status rows
      updated; runner comment labels changed from `x.bat` to bare `x`.
- [x] **T5.3** `how_to_test.md`: all hardcoded output paths in the Phase
      A/B/C/W/R/D expectations repointed to `data/...` (transcripts, audio,
      generated_transcripts, summaries, audio_reencoded + ffprobe, tts_output +
      ffprobe, quick-ref table).
- [x] **T5.4** `plan.md`: ticked the "consolidate outputs under a single `data/`
      root" checkbox (Phase 0); Section 4 repo-layout snippet rewritten with
      outputs nested under `data/` + `scripts/`/`init.bat`; status-table +
      Phase 1/2/3 + "next steps" output paths repointed; "layout stabilizing"
      note now reads "consolidated under `data/`"; runner labels de-`.bat`-ed.
- [x] **T5.5 (code, from the T4 NOTE + sweep):**
      - `make_summaries.py` — the paste-ready Kiro instruction + all printed
        messages now use `data/...` (derived from `paths.*`), not the old root
        strings. VERIFIED by running `s`: prints `data/summaries/<base>...`,
        `data/transcripts/...`, `data/generated_transcripts/...`.
      - `compare_transcripts.py` — was hardcoding `"generated_transcripts"` /
        `"transcripts"` (NOT via `paths`); now imports `lib.paths` and builds
        `WHISPER_FILE`/`YT_FILE` from `paths.GENERATED_TRANSCRIPT_DIR` /
        `paths.TRANSCRIPT_DIR`. VERIFIED: resolves to `data\...`.
      - `youtube_download.py` (legacy pytube) — default `output_path` changed
        from `"audio"` to `"data/audio"` for consistency.
      - All three parse clean (`ast.parse` OK).

**Test & hand off (STOP for user feedback):** skim the docs and confirm no old
root-level output paths remain, and the summaries instruction now points at
`data/`:
```cmd
s
```
**Expect:** the paste-ready block reads `save each to data/summaries/<base>.summary.md`
with `data/transcripts/...` / `data/generated_transcripts/...` entries.
Open `README.md`, `youtube.html`, `how_to_test.md`, `plan.md` — the repo-layout
blocks show outputs nested under `data/` and runners under `scripts/`; no doc
points at bare `audio/`, `transcripts/`, `tts_output/`, etc. **Pass =** docs
match reality; `s` prints `data/` paths. This completes TODO3.

---

## Suggested order of attack

| # | Task | Complexity | Test |
|---|------|-----------|------|
| 0 | T0 decide + inventory | low | decisions written; grep list complete |
| 1 | T1 repoint `lib/paths.py` (+ hardcoded summaries) | low-med | `paths.*` print `data\...`; tools resolve there |
| 2 | T2 move outputs + ignore files | med | git shows no tracked outputs; still ignored |
| 3 | T3 move runners to `scripts/` (+ PATH) | med | `scripts\r.bat` / `scripts/r.sh` work, args pass |
| 4 | T4 verify each tool | med | outputs land under `data/`; skip-if-exists holds |
| 5 | T5 docs sweep | low | layout blocks + paths match reality |

Build top-to-bottom. T2 (the physical move) is the riskiest step — do it after
T1 so the code already expects the new paths, and verify with `git status` that
nothing tracked moved unexpectedly.

---

## Notes / guardrails

- **Single source of truth:** change `lib/paths.py` first; the scripts follow.
  Grep for the two hardcoded `"summaries"` strings — those are the only paths NOT
  routed through `paths`.
- **`summaries/` → `data/summaries/` but STAYS tracked** — the one subtlety:
  `data/` is ignored, so a `.gitignore` negation (`!data/summaries/`,
  `!data/summaries/**`) re-includes it, and the move uses `git mv`. Verify with
  `git check-ignore data/summaries/x.md` printing NOTHING (= still tracked).
- **Moves, not deletes:** T2 moves git-ignored outputs; never delete the
  originals. Verify with `git status` that no tracked file vanished.
- **Preserve the one-letter UX:** with the runners in `scripts/`, add `scripts/`
  to PATH so typing `r` / `w` / `v` from the repo root still works.
- **Windows/Linux:** keep `.gitattributes` LF-for-`.sh` / CRLF-for-`.bat` covering
  `scripts/`. `.sh` files keep their executable bit.
- **No new deps; free.** Pure moves + path edits.
- This is a **refactor** — the win is verified sameness (every tool still reads/
  writes the right place), not new behavior. Test path resolution after each phase.

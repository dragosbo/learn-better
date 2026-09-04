# TODO3 — Consolidate outputs under `data/` + gather runners into one folder

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
├── playlists.json            # (already here)
├── wordclouds/               # (already here) *.word_cloud.json
├── audio/                    # was audio/
├── audio_reencoded/          # was audio_reencoded/
├── transcripts/              # was transcripts/   (YouTube captions)
├── generated_transcripts/    # was generated_transcripts/ (Whisper)
└── tts_output/               # was tts_output/  (+ .voices/ cache)
```
- **Open question — `summaries/`?** It is currently **tracked by git** (authored
  content, not regenerated). Options:
  - **(a) leave `summaries/` at the root** (keep it tracked, out of the ignored
    `data/`), OR
  - **(b) move to `data/summaries/`** and make `data/` ignore-everything-except
    `summaries/` (more complex `.gitignore`; mixes tracked + ignored under one
    root). **Recommendation: (a)** — simplest, keeps the tracked/ignored split
    clean. `data/` = regenerated/ignored; `summaries/` = tracked.
- **Open question — migrate existing files or start fresh?** The current output
  folders hold real files (audio, transcripts, the TTS wav, wordcloud JSONs).
  Options: **(a) leave old files where they are** (they're git-ignored; just point
  the code at the new dirs and re-generate as needed), or **(b) physically move**
  existing outputs into `data/`. **Recommendation: (b)** move them, so nothing has
  to be re-downloaded and skip-if-exists keeps working. (One-time `move`/`mv`.)

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
- **Recommendation: (a)** — a `bin/` folder holds the actual logic, and
  minimal root shims preserve the exact one-letter UX with no PATH setup. (The
  shims are one line each and rarely change.)

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
| Summaries (tracked) | `summaries/` | `summaries/` (unchanged — stays tracked) |
| Runners | `*.bat` / `*.sh` at root | `bin/*.bat` + `bin/*.sh`, with 1-line root shims |

---

## Phase T0 — Decide + prep (no behavior change yet) — TODO

- [ ] **T0.1** Lock the decisions above (A1 summaries, A1 migrate, B1 runner
      approach, folder name). Write them at the top of this file once confirmed.
- [ ] **T0.2** Inventory every reference to the output dirs and runners so nothing
      is missed. Known reference points (from a grep):
      - `lib/paths.py` — the 7 dir constants (single source of truth).
      - `code/*.py` — import the constants (`read_channel`, `read_transcript`,
        `list_playlists`, `transcribe_audio`, `make_summaries`, `make_wordcloud`,
        `reencode_audio`, `generate_speech`) + hardcoded `"summaries"` in
        `make_summaries.py` / `generate_speech.py`.
      - `lib/youtube.py` — defaults `output_dir or paths.AUDIO_DIR/TRANSCRIPT_DIR`.
      - `.gitignore`, `.dockerignore` — the ignored output folders.
      - Docs: `README.md`, `youtube.html`, `how_to_test.md`, `plan.md` (repo
        layout blocks + any `audio/`/`transcripts/` mentions).
      - The notebook `notebooks/yt_download.ipynb` (paths via `lib/`, so it
        follows automatically — verify).

**Test & hand off (STOP for user feedback):** no code runs in T0. The deliverable
is the locked decisions + the reference inventory. Hand the user the finalized
decision list and grep inventory to review; wait for "looks right / go" before T1.

---

## Phase T1 — Repoint paths to `data/` (the core change) — TODO

- [ ] **T1.1** Edit `lib/paths.py` — the single source of truth. Point the ignored
      output dirs under `data/`:
      `AUDIO_DIR = os.path.join("data","audio")`,
      `AUDIO_REENCODED_DIR = os.path.join("data","audio_reencoded")`,
      `TRANSCRIPT_DIR = os.path.join("data","transcripts")`,
      `GENERATED_TRANSCRIPT_DIR = os.path.join("data","generated_transcripts")`,
      `TTS_OUTPUT_DIR = os.path.join("data","tts_output")`.
      `DATA_DIR`/`WORDCLOUD_DIR` already correct. Keep `SUMMARY_DIR` at root
      (per recommendation) — consider adding a `SUMMARY_DIR = "summaries"` constant
      so the hardcoded `"summaries"` strings can reference `paths` too (tidy-up).
- [ ] **T1.2** Because scripts build their dirs from `paths.*`, most update
      automatically. Double-check the two hardcoded `"summaries"` spots
      (`make_summaries.py`, `generate_speech.py`) and any user-facing "looked in
      ..." messages that print folder names, so the messages match the new paths.
- [ ] **T1.3** Scripts `os.makedirs(..., exist_ok=True)` on their output dir, so
      `data/audio/` etc. are created on demand — confirm each tool still creates
      its dir (they use the constant, so yes; verify once).

**Test & hand off (STOP for user feedback):** I'll give you exact commands; run
them and report back before T2.
```cmd
c
python -c "from lib import paths; print(paths.AUDIO_DIR, paths.TRANSCRIPT_DIR, paths.GENERATED_TRANSCRIPT_DIR, paths.AUDIO_REENCODED_DIR, paths.TTS_OUTPUT_DIR)"
```
**Expect:** all print the `data\...` forms (e.g. `data\audio`, `data\transcripts`,
`data\tts_output`). Then, to confirm a tool resolves its dir under `data/`, run a
non-destructive lister, e.g.:
```cmd
python code\reencode_audio.py config\config_reencode.json
```
**Expect:** the "looked in ..." / selection line now points under `data\audio\`.
**Pass =** paths are all under `data\`. Report back; then we do T2.

---

## Phase T2 — Move existing outputs + update ignore files — TODO

- [ ] **T2.1** Physically move current outputs into `data/` (one-time), so
      skip-if-exists keeps working and nothing re-downloads:
      `audio/ audio_reencoded/ transcripts/ generated_transcripts/ tts_output/`
      → under `data/`. (These are git-ignored, so git sees no change.)
- [ ] **T2.2** Update `.gitignore`: replace the root entries with `data/` (which
      already ignores everything under it) — but keep `summaries/` tracked. Verify
      `data/` still ignores the moved folders and that `data/wordclouds` +
      `data/playlists.json` remain ignored as before.
- [ ] **T2.3** Update `.dockerignore` similarly (it currently lists `audio/`,
      `tts_output/`, etc. individually — collapse to `data/`).

**Test & hand off (STOP for user feedback):** run these and report back before T3.
```cmd
c
git status
git check-ignore data/audio/x.mp3
```
**Expect:** `git status` shows **no new tracked output files** (the moved audio/
transcripts/etc. stay ignored); `git check-ignore` **echoes** the path (= ignored).
Also eyeball that the old root folders are gone and the files now live under
`data\` (e.g. `dir data\audio`), and that `summaries\` is still at the root and
still tracked. **Pass =** nothing tracked moved, outputs ignored under `data/`,
`summaries/` untouched. Report back; then T3.

---

## Phase T3 — Gather runners into `bin/` with root shims — TODO

- [ ] **T3.1** Create `bin/` and move the real runners there: `bin/c.bat`,
      `bin/r.bat`, ... and `bin/c.sh`, `bin/r.sh`, ... (all 10 of each). Update
      each runner's internal path to the script if needed (they call
      `python code\...` / `python code/...` from the repo root — since the shims
      run them from root, the `code\...` paths still resolve; verify).
- [ ] **T3.2** Add tiny **root shims** so the one-letter UX is unchanged:
      - `r.bat` (root) → `@echo off` + `call "%~dp0bin\r.bat" %*`
      - `r.sh` (root) → `exec "$(dirname "$0")/bin/r.sh" "$@"`
      (one per runner). Keep `.gitattributes` LF/CRLF rules applying to `bin/*.sh`
      and the root `*.sh` shims.
- [ ] **T3.3** Keep executable bits on all `.sh` (real + shim) via
      `git update-index --chmod=+x`.

> Alternative if the user prefers **no shims** (B1 option b): move runners to
> `bin/`, skip the shims, and document adding `bin/` to PATH. Simpler tree, but
> `r` won't work from root until PATH is set.

**Test:**
```cmd
r                    :: root shim -> bin\r.bat -> python code\read_channel.py
wc config\config_wordcloud.json   :: shim forwards the arg
```
On Linux: `./r.sh`, `./w.sh config/config_transcribe.id.json`. Confirm the
one-letter commands still work from the repo root and args pass through.

---

## Phase T4 — Verify each tool end-to-end — TODO

- [ ] **T4.1** Re-run a light check of each tool so outputs land under `data/`:
      - `p` → `data/playlists.json` (unchanged path).
      - `d` / `wc` → `data/wordclouds/*.word_cloud.json` (unchanged path).
      - `a config\config_reencode.json` → `data/audio_reencoded/...` (reads
        `data/audio/`).
      - `v` → `data/tts_output/...` (reads `summaries/` + `data/transcripts/`).
      - `s` → lists from `data/transcripts/` + `data/generated_transcripts/`.
      - `t` / `r` / `w` → write under `data/` (network-dependent; skip-if-exists
        should recognize the moved files).
- [ ] **T4.2** Confirm skip-if-exists still triggers on the moved files (proves
      the move + repoint are consistent).

**Test:** run the above; each should print paths under `data/` and skip existing
outputs. (Network tools optional — the path resolution is the thing to confirm.)

---

## Phase T5 — Docs + wiring — TODO

- [ ] **T5.1** `README.md`: update the **repo layout** block (outputs now under
      `data/`; runners under `bin/` with root shims); update any inline
      `audio/`/`transcripts/`/`tts_output/` path mentions; note the `bin/` +
      shim arrangement in the "Running the tools" section.
- [ ] **T5.2** `youtube.html`: update the repo-layout tree and any path mentions
      (data pipeline diagram labels like `audio/` → `data/audio/`, etc.).
- [ ] **T5.3** `how_to_test.md`: update any hardcoded output paths in the test
      expectations (e.g. `audio_reencoded\...` → `data\audio_reencoded\...`,
      `tts_output\...` → `data\tts_output\...`).
- [ ] **T5.4** `plan.md`: tick Phase 0's "consolidate outputs under a single
      `data/` root" box; add a short note on the `bin/` runner reorg; update the
      Section 4 repo-layout snippet.

**Test:** open `README.md` / `youtube.html`, confirm the layout matches reality
and no doc still points at the old root-level output folders.

---

## Suggested order of attack

| # | Task | Complexity | Test |
|---|------|-----------|------|
| 0 | T0 decide + inventory | low | decisions written; grep list complete |
| 1 | T1 repoint `lib/paths.py` (+ hardcoded summaries) | low-med | `paths.*` print `data\...`; tools resolve there |
| 2 | T2 move outputs + ignore files | med | git shows no tracked outputs; still ignored |
| 3 | T3 `bin/` + root shims | med | `r` / `./r.sh` still work from root, args pass |
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
- **`summaries/` stays tracked** (recommended) — don't bury it under the ignored
  `data/` root, or git will stop tracking authored content.
- **Moves, not deletes:** T2 moves git-ignored outputs; never delete the
  originals. Verify with `git status` that no tracked file vanished.
- **Preserve the one-letter UX:** whatever the runner reorg, typing `r` / `w` /
  `v` from the repo root must still work (root shims, per recommendation).
- **Windows/Linux:** keep `.gitattributes` LF-for-`.sh` / CRLF-for-`.bat` covering
  both `bin/` and the root shims. `.sh` files keep their executable bit.
- **No new deps; free.** Pure moves + path edits.
- This is a **refactor** — the win is verified sameness (every tool still reads/
  writes the right place), not new behavior. Test path resolution after each phase.

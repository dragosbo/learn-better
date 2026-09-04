# Skill — writing mini-plan `todoN.md` files for further development

A reusable procedure for turning a roadmap item (from `plan.md`) into a small,
phased, testable **mini-plan** file that we build top-to-bottom. This is the
format we used for the word cloud (`todo.md`) and the audio-bitrate helper
(`todo1.md`); it worked well, so it is written down here to reuse.

Kiro: when the user asks to "plan" a feature, or to add a `todoN.md`, follow
this. Produce the plan file first, confirm the couple of decisions that need the
user, then implement phase by phase.

---

## When to use this

- The user picks a `plan.md` roadmap item (e.g. "let's do item 4") and asks for
  a plan, OR a task will take more than a couple of steps.
- Name the file `todoN.md` at the repo root (`todo.md`, `todo1.md`, `todo2.md`,
  …). One feature per file.
- After the feature is fully done and its docs are wired in, the old plan can be
  archived to `ignore/` (git-ignored) — but only when the user says so.

---

## Core principles (from how we work)

1. **Match the repo, don't invent.** Before planning, read 1–3 existing files
   that do something similar (e.g. `transcribe_audio.py`, `make_wordcloud.py`,
   `lib/paths.py`, an existing `*.bat`, a `config/config_*.json`). Mirror their
   conventions: top-of-file config block, optional JSON config in `config/`,
   `SELECT_BY = name|id|all` selection, skip-if-exists, UTF-8 stdout guard,
   repo-root import (`from lib import ...`), a one-letter `.bat` runner.
2. **Free tech only, no extra cost.** Prefer the Python stdlib and tools already
   required (ffmpeg is already a dep; JS libs load from a CDN). No new paid
   service, no API key. If a new pip dep is truly needed, call it out explicitly
   and add it lean, per phase — never speculatively.
3. **Data / artifact split.** Python produces data or files; rendering/plotting
   (if any) is client-side JS in a static `.html`. Keep outputs
   renderer-agnostic where it applies.
4. **Never destroy the user's inputs.** Write derived output to a NEW,
   git-ignored folder (e.g. `audio_reencoded/`, `data/wordclouds/`). Treat source
   folders as read-only. Encode variant params (bitrate, etc.) into the output
   filename so re-runs at different settings coexist. Add the new folder to
   `lib/paths.py` and `.gitignore`.
5. **Phases increase in complexity, each runnable and testable.** Start with a
   proof-of-concept on ONE item, then batch/selection + config + runner, then
   robustness, then docs. Each phase should run green before the next.
6. **Skip-if-exists + a written/skipped/failed tally** in every batch tool.
7. **Fail cleanly, never with a raw traceback.** Validate inputs up front
   (selection mode, numeric params) with clear `!! ...` messages; capture a
   subprocess's stderr, count it `failed`, delete any partial output, and
   continue the batch.
8. **Don't add tests/features the user didn't ask for.** Solve the item; keep it
   proportional.

---

## The `todoN.md` skeleton

Write the plan in this shape (adapt headings to the feature):

```
# TODOn — <Feature name> (`todo` item N from plan.md)

<2–4 sentence description: what it builds and the end result.>

**All free, no extra cost.** <name the only dependency and why it's already
present; state "no new pip dep / no API / no cloud".>

## Design direction (decided, matches the repo)
- <bullet the key decisions: reuse conventions, engine/lib choice, output
  folder, why not in-place, data/JS split.>

## Where files live
| Thing | Path | Notes |   <-- input, output, script, config, runner rows>

## Config — proposed `config/config_<feature>.json`
```json
{ "_comment": "<what each key does>", ... }
```
<explain the important keys, especially the one that IS the feature.>

## Phase X0 — Scope + prerequisites (no code) — TODO
- [ ] X0.1 confirm the dependency / no requirements change
- [ ] X0.2 output folder + `paths.<DIR>` + `.gitignore`
- [ ] X0.3 output name pattern (drives skip-if-exists)
**Test:** none (decisions only). Write them as config comments atop the script.

## Phase X1 — <do it for ONE item> — TODO
- [ ] X1.1 new `code/<feature>.py`, config block, repo-root import
- [ ] X1.2 locate/validate the engine (e.g. `find_ffmpeg` via shutil.which)
- [ ] X1.3 the core one-item function; safe subprocess (list form, no shell=True)
- [ ] X1.4 output path via `paths.<DIR>`; skip-if-exists
- [ ] X1.5 UTF-8 stdout guard
**Test:** <exact `python code/... .py` command>
**What to look for:** <concrete, checkable outcomes>

## Phase X2 — Batch + selection + config + runner — TODO
- [ ] X2.1 SELECT_BY = name|id|all over the input folder
- [ ] X2.2 loop the X1 core; written/skipped/failed tally
- [ ] X2.3 JSON config in config/ (load_config + resolve_config_path pattern)
- [ ] X2.4 `<letter>.bat` runner (mirror wc.bat: `python code/... %1`)
**Test / What to look for:** <commands + outcomes>

## Phase X3 — Robustness + edge cases — TODO
- [ ] X3.1 missing engine -> friendly hint, exit clean
- [ ] X3.2 failed run -> stderr reason, count failed, no partial, continue
- [ ] X3.3 empty input / no matches -> clear message
- [ ] X3.4 validate numeric/enum params up front
**Test / What to look for:** <bad-input commands + expected `!!` messages>

## Phase X4 — Docs + wiring — TODO
- [ ] X4.1 README.md: new section + runner in helper list + repo layout
- [ ] X4.2 how_to_test.md: a "Phase X" block + runner table + config table
- [ ] X4.3 youtube.html: tools-table row + mark the todo item Done + layout
- [ ] X4.4 plan.md: tick the checklist box + status-table row + next-step
**Test:** open youtube.html/README, confirm listed + item marked Done.

## Suggested order of attack
| # | Task | Complexity | Test |   <-- one row per phase, low->med>

## Notes / guardrails
- Free only; never touch originals; no shell=True; skip-if-exists; outputs
  git-ignored; config style consistent with the existing tools.
```

---

## The test-and-record discipline (important — the user asked for this)

Testing is not an afterthought; **record how each phase was tested inside the
`todoN.md`** so it can be re-run later. When a phase passes:

- Change its heading to `— DONE` (or `— DONE, USER-VALIDATED` once the user
  confirms), and flip its `- [ ]` boxes to `- [x]`.
- Under the phase, add a short **"How this was tested (record for re-runs)"**
  list: the exact commands and the concrete results (numbers, file names,
  tool output lines). Keep a **"What to look for"** line of checkable outcomes.
- Note any **extras** added beyond the original spec with a `✅` line.

Verify results, don't assume:
- A command exiting 0 is NOT proof of success. Check the real artifact: file
  exists, size/shape is right, and use the domain tool to confirm (e.g.
  `ffprobe` for bitrate, open the JSON, render the HTML).
- State what you verified vs. what you couldn't (e.g. "missing-engine path
  verified by inspection, not by tampering with PATH").
- Clean up temporary files created during testing (throwaway configs, captured
  output). Leave only intended artifacts.

---

## Environment gotchas learned here (Windows / cmd / conda)

- **Run inside the env.** ffmpeg/ffprobe and Python live in the `learn-better`
  conda env, not the base PATH. Prefix runs with `call conda activate
  learn-better && ...`, or use the `.bat` runners (which activate first).
- **`.bat` `::` comments are line-start only.** At the interactive prompt, do
  NOT type inline notes after a command (`a  :: note`) — cmd passes `::` as
  `%1`. Tell the user to run the command alone. When *showing* example commands
  with inline `::` annotations, warn that they're annotations, not to be typed.
- **Locked files.** If a media player has an output file open, Windows locks it,
  so regenerating/deleting that exact file fails — close the player first.
- **Long-running/interactive commands** (dev servers, watch mode) block; don't
  run them inline. Prefer single-run flags.
- **Non-ASCII titles** (fr/ro accents, emoji, fullwidth `？｜`) appear in file
  names — always `sys.stdout.reconfigure(encoding="utf-8")` in scripts and use
  list-form `subprocess.run([...])` (no `shell=True`).

---

## Interaction style (how to communicate around a mini-plan)

- **Plan first, then confirm the few real decisions, then build.** After writing
  `todoN.md`, surface the 1–2 choices that genuinely need the user (e.g. default
  bitrate, output folder, runner letter) and proceed once answered. Don't ask
  about things you can reasonably decide from repo conventions.
- **Do the work, don't just suggest it.** For a chosen item, implement and verify
  rather than describing what could be done.
- **One phase at a time; report and pause at sensible checkpoints.** After a
  phase: say what changed, how it was tested (the numbers), and give the user a
  copy-paste way to test it themselves. Then ask whether to continue.
- **Give the user a simple test recipe.** Exact `cmd` commands from the repo
  root, what to expect, and where the artifact is (path they can open/listen to).
- **Keep summaries tight and factual.** Show results (sizes, bitrates, tallies),
  not adjectives. Correct the user plainly when something's off (e.g. the `::`
  arg issue) instead of just agreeing.
- **Respect git safety.** Only commit/push when the user asks. This repo works
  **straight on `main`** (user preference) — no feature branches. Stage specific
  files by name (not `git add .`); leave unrelated untracked files (e.g. a
  stray notes file) out and mention them. Flag possible-secret files before
  committing. LF→CRLF warnings on Windows are harmless.

---

## Definition of done for a mini-plan

- All phases marked DONE with their `[x]` boxes and a testing record.
- The tool runs from a one-letter `.bat`, is config-driven, skips existing
  outputs, and fails cleanly on bad input.
- Docs wired in all four places: `README.md`, `how_to_test.md`, `youtube.html`,
  `plan.md` (checkbox + status row + next-step).
- Outputs are git-ignored; originals untouched; no new paid/heavy deps.
- Temp test files cleaned up.
- Committed to `main` only after the user confirms.
```

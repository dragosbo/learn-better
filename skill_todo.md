# Skill — writing mini-plan `todoN.md` files for further development

A reusable procedure for turning a roadmap item (from `plan.md`) into a small,
phased, testable **mini-plan** file that we build top-to-bottom. Proven on the
word cloud (`todo.md`), the audio-bitrate helper (`todo1.md`), the text-to-speech
baseline (`todo2.md`), and a consolidation refactor (`todo3.md`); written down
here to reuse.

Kiro: when the user asks to "plan" a feature/change, or to add a `todoN.md`,
follow this. Produce the plan file first, confirm the couple of decisions that
need the user, then implement phase by phase — stopping for the user to test
after each phase (see "Interaction protocol").

---

## When to use this

- The user picks a `plan.md` roadmap item (e.g. "let's do item 4") and asks for
  a plan, OR a task will take more than a couple of steps.
- Name the file `todoN.md` at the repo root (`todo.md`, `todo1.md`, `todo2.md`,
  …). One feature/change per file.
- Two shapes of task, plan them differently:
  - **New tool / feature** (word cloud, bitrate, TTS) — the phase skeleton below
    (proof-of-concept → batch → robustness → docs).
  - **Cross-cutting refactor** (consolidate outputs, move runners) — nothing new
    is built; the risk is **stale references**, not new logic. Lead with "change
    the single source of truth (`lib/paths.py`), then verify sameness"; inventory
    every reference up front; make the riskiest step (e.g. a physical file move)
    its own phase, after the code already expects the new state.
- After the plan is fully done and its docs are wired in, archive it to `ignore/`
  (git-ignored) — but only when the user says so. If the file was already
  committed, archive with `git rm --cached todoN.md` + `move`/`mv` into `ignore/`,
  then commit the removal (the copy in `ignore/` stays local and git-ignored).

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
9. **Ship a runner for every OS the repo targets.** This repo has both Windows
   `.bat` and Linux/macOS `.sh` one-letter helpers. A new tool needs BOTH (e.g.
   `v.bat` + `v.sh`). The `.sh` form should activate conda if present, else fall
   back to the current `python` (that's how the Docker/Codespaces images run).
   Keep `.gitattributes` forcing `*.sh` → LF (a CRLF shebang breaks on Linux with
   `bad interpreter: ...^M`) and `*.bat` → CRLF; set the `.sh` executable bit via
   `git update-index --chmod=+x`.
10. **Prefer a tool's stable CLI over its Python API when the API drifts.** Piper
    shifted APIs across `piper-tts`/`piper1-gpl`, but its CLI (`piper -m … -f …`,
    text on stdin) was stable — so the script shells out via list-form
    `subprocess`. Before wiring a new engine, confirm what's actually installed
    (`where <tool>`, `python -c "import x; print(x.__file__)"`, list its
    submodules) rather than guessing the interface.

---

## Interaction protocol — implement → test → wait → continue

This is how the user wants these plans run, and it works well: **one phase at a
time, with the user testing between phases.** For EACH phase:

1. **Implement only that phase.** Don't run ahead into the next one.
2. **Verify what you can yourself first** (syntax, path resolution, a real run
   with a domain check), then **hand off to the user for their own test.**
3. **Give clear, copy-paste test guidance every time** — exact commands from the
   repo root, what output to expect, where the artifact is (a path they can open/
   listen to), and what "pass" looks like. Put example commands on their **own
   clean line** with no inline `::`/`#` notes appended (the user will paste them
   verbatim; see the `::` gotcha).
4. **Pause and wait for the user's feedback/go-ahead** before the next phase. If
   a test fails, fix it and re-issue the test steps before moving on.
5. **Only after the user confirms**, mark the phase `— DONE, USER-VALIDATED` with
   its testing record, then continue.

State this protocol at the top of the `todoN.md` itself when the task is a
refactor or otherwise risky, so the plan file carries the contract. Don't batch
phases together, and don't declare success with "it should work" — always a
concrete recipe the user can run.

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
- [ ] X2.4 `<letter>.bat` AND `<letter>.sh` runners (mirror wc.bat/wc.sh:
      `python code/... %1` / `"$@"`); .gitattributes covers the new .sh
**Test / What to look for:** <commands + outcomes>

## Phase X3 — Robustness + edge cases — TODO
- [ ] X3.1 missing engine -> friendly hint, exit clean
- [ ] X3.2 failed run -> stderr reason, count failed, no partial, continue
- [ ] X3.3 empty input / no matches -> clear message
- [ ] X3.4 validate numeric/enum params up front
**Test / What to look for:** <bad-input commands + expected `!!` messages>

## Phase X4 — Docs + wiring — TODO
- [ ] X4.1 README.md: new section + BOTH runners in helper list + repo layout;
      add any new pip dep to the dependency table AND requirements.txt (only now,
      after X1 proved it installs locally)
- [ ] X4.2 how_to_test.md: a "Phase X" block + runner table + config table
- [ ] X4.3 youtube.html: tools-table row + mark the todo item Done + layout +
      roadmap recolor
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
- **Wrong interpreter for tools on PATH.** `jupyter`/`nbconvert` (and sometimes
  other tools) can resolve to the **base Anaconda 3.7** install, not the
  `learn-better` env — you'll see `ModuleNotFoundError: No module named 'pandas'`
  etc. Run through the env's python: `python -m jupyter nbconvert ...`. Even then,
  nbconvert executes with a registered **kernelspec** that may point at base; if
  so, validate notebook *logic* by importing its functions in a plain
  `python script.py` in the env instead of a full notebook execute.
- **Terminal stdout can be unreliable in this setup.** Live command output is
  sometimes swallowed/mangled. Redirect to a file and read it back
  (`... > _out.txt 2>&1` then read `_out.txt`); confirm long/slow runs by checking
  the produced artifact (a file appearing) rather than trusting console output.
  Clean up the `_out.txt` and any stray redirect-artifact files (e.g. a 0-byte
  `skips)`) afterward.
- **`.sh` on Windows checkout.** Author `.sh` with LF and enforce it via
  `.gitattributes` (`*.sh text eol=lf`); otherwise git's autocrlf gives them a
  CRLF shebang that fails on Linux. Set the exec bit through git
  (`git update-index --chmod=+x`) since Windows can't chmod.
- **New pip deps: defer to the docs phase.** Decide the dep in the scope phase but
  DON'T add it to `requirements.txt` until a real local run proves it installs and
  works (PyPI can be blocked in some sandboxes; installs happen on the user's
  machine, as with `faster-whisper`/`piper-tts`). Cache model downloads in a
  git-ignored folder (e.g. `tts_output/.voices/`, or a devcontainer `~/.cache`
  volume) so first-run downloads aren't repeated.

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

## Cross-cutting refactor playbook (when NOT building a new tool)

For tasks like "consolidate outputs under `data/`" or "move the runners into one
folder":
- **Change the single source of truth first.** Output paths funnel through
  `lib/paths.py`; most scripts follow automatically. Grep for the few hardcoded
  strings that DON'T (`"summaries"` was one) and fix those explicitly.
- **Inventory every reference up front** (grep for the constants, folder names,
  runner names) so nothing is missed: `code/*.py`, `lib/*.py`, `.gitignore`,
  `.dockerignore`, all four docs, the notebook.
- **Respect the tracked/ignored split.** `summaries/` is git-tracked (authored);
  the rest are git-ignored (regenerated). Don't bury tracked content under an
  ignored root, or git stops tracking it.
- **Physical moves are their own phase, done AFTER the code expects the new
  layout,** and verified with `git status` (no tracked file should vanish) +
  `git check-ignore`. Move, never delete.
- **Preserve UX.** If runners move to `bin/`, keep one-line root shims so `r`/`w`/
  `v` still work from the repo root (or document a PATH step) — confirm with the
  user which they prefer.
- The win is **verified sameness**, not new behavior: after each phase, test that
  every tool still reads/writes the right place.

---

## Definition of done for a mini-plan

- All phases marked DONE with their `[x]` boxes and a testing record; each phase
  was user-validated before the next began.
- The tool runs from a one-letter `.bat` **and** `.sh`, is config-driven, skips
  existing outputs, and fails cleanly on bad input (no raw tracebacks).
- Docs wired in all four places: `README.md`, `how_to_test.md`, `youtube.html`,
  `plan.md` (checkbox + status row + next-step). Any new dep is in the dependency
  table AND `requirements.txt`.
- `.gitattributes` covers new `.sh` (LF) and they carry the exec bit.
- Outputs are git-ignored; originals untouched; no new paid/heavy deps.
- Temp test files (captured output, throwaway configs, stray artifacts) cleaned up.
- Committed to `main` only after the user confirms (this repo works straight on
  `main`, no branches; stage files by name; leave unrelated untracked files out
  and mention them).
```

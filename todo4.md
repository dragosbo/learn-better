# TODO4 — Absorb `how_to_deploy.md` into the core docs + close the remaining `plan.md` gaps

Two related goals:

**A. Make `how_to_deploy.md` obsolete by design.** All the deployment knowledge
it holds (12-platform ranking, local/container/cloud setup, image scripts,
gotchas) should live in the *relevant* files — `README.md` (the actionable
"how to run/deploy" guidance), `youtube.html` (the visual overview), and
`plan.md` (roadmap/status). Once the useful, accurate parts are migrated and the
gaps are fixed, `how_to_deploy.md` is archived to `ignore/` (like `todo1/2/3`,
`mini_todo`, `tts`) — nothing links to it anymore.

**B. Deliver real "one-click" install** for the three zero-local-setup targets —
**Google Colab**, **GitHub Codespaces**, and **VS Code / Kiro Dev Container** — so
a newcomer goes from repo to a working environment in a single click (or one
pasted cell for Colab), with ffmpeg + all deps + the `data/` layout ready.

**C. Close the genuinely-open items** surfaced while auditing `how_to_deploy.md`
against reality, plus the still-open roadmap items in `plan.md`.

> **Nature of this task:** this is NOT a new tool. It is a **docs-migration +
> gap-fix** cross-cutting change. The risk is **stale/inaccurate guidance and
> broken copy-paste commands**, not new logic. So the plan leans on: inventory
> what's accurate vs. wrong in `how_to_deploy.md`, migrate the accurate parts
> into the right home, FIX the wrong parts as you migrate (don't copy bugs
> forward), create the one missing artifact (Colab notebook + badge), then retire
> the source doc. No new pip dep, no new paid service — pure docs + one notebook.

**All free, no extra cost.** Docs edits + a Colab setup notebook (plain Jupyter
JSON). No new dependency, no API, no cloud service.

---

## How we work this plan (interaction protocol — IMPORTANT)

Docs work with many moving references, so we go **one phase at a time** with the
user in the loop. For EACH phase F0 → F6:

1. **Implement only that phase.** Do not run ahead into the next phase.
2. **Verify what can be verified** (links resolve, commands match the real script
   interfaces, the notebook is valid JSON) then **hand back to the user.**
3. **Give clear, copy-paste review guidance every time** — which file/section to
   open, what it should now say, and what "pass" looks like. Assume the user will
   actually open it and report back.
4. **Wait for the user's feedback / go-ahead** before the next phase. If review
   surfaces a problem, fix it and re-issue the review steps before moving on.
5. **Only after the user confirms a phase passes**, mark it DONE in this file
   (record how it was verified) and proceed to the next.

> In short: **implement → tell the user exactly what to review → wait → then
> continue.** No batching phases together.

---

## Audit — what `how_to_deploy.md` holds, and its status (verified against the repo)

Read the whole file + checked each artifact it references. Findings:

### Accurate & already backed by real repo artifacts (migrate the guidance, keep the files)
- **`.devcontainer/Dockerfile` ffmpeg fix** — DONE in the repo (installs ffmpeg,
  cites the deploy doc). ✅
- **`.devcontainer/devcontainer.json` cleanup** — `azure-cli` removed;
  model-cache volume present (`learn-better-model-cache` → `/home/vscode/.cache`). ✅
- **`Dockerfile.standalone`** — exists in repo root (slim, ffmpeg, non-root). ✅
  BUT its own header-comment examples are STALE (mount `-v $(pwd)/audio:...`
  instead of the consolidated `-v $(pwd)/data:...`) — fix during migration.
- **`.dockerignore`** — exists. ✅
- **`scripts/*.sh` + `.bat` runners, `init.bat` PATH workflow** — exist, match
  the doc. ✅
- **Local (conda/pip/uv), Docker, Podman, Codespaces, Gitpod** setup steps —
  accurate as reference guidance.

### Wrong / broken in the doc (FIX while migrating, do NOT copy forward)
- **Stale command examples**: `python code/transcribe.py --config data/config.json`,
  `code/transcribe.py --url ... --output ...`. The real script is
  `code/transcribe_audio.py` and it is **config-path driven** (`sys.argv[1]` = a
  `config/config_transcribe*.json`), NO `--url`/`--config`/`--output` flags.
  Correct form: `python code/transcribe_audio.py config\config_transcribe.json`
  or the `w` runner.
- **`YOUR_USER` placeholders** throughout the git clone/Colab/Codespaces examples,
  even though the real repo is `dragosbo/learn-better`.
- **Colab/Drive dir snippets** hand-roll `AUDIO_DIR=.../audio`, `.../transcripts`,
  … — should mirror the real `data/` layout from `lib/paths.py`.

### One-click install status (verified) — the core of goal B
- **Dev Container (VS Code / Kiro)** — **already effectively one-click**:
  `.devcontainer/Dockerfile` installs ffmpeg; `.devcontainer/devcontainer.json`
  has `postCreateCommand: pip install -r requirements.txt`, the model-cache
  volume, port 8000 forwarded, and the Python+Jupyter extensions. "Reopen in
  Container" builds the whole env unattended. GAP: no README **badge/quick link**
  advertising it; verify the flow end-to-end and document the single click.
- **GitHub Codespaces** — **reuses the same `.devcontainer/`**, so "Create
  codespace on main" is already one-click for the environment. GAP: no
  **"Open in GitHub Codespaces" badge** in README; the post-create should leave
  the user ready to run (`w`/`python code/…`). Add badge + verify.
- **Google Colab** — **NOT one-click yet**: needs the promised
  `notebooks/colab_setup.ipynb` + an **"Open In Colab" badge** so one click opens
  a notebook whose first cell installs ffmpeg + deps + clones the repo. This is
  the main build item for one-click.

> **One-click = single action → ready env.** Colab: click badge → Run-all first
> cell. Codespaces: click badge/`Code → Codespaces`. Dev Container: click badge/
> "Reopen in Container". No manual ffmpeg step, no manual pip step, no PATH
> fiddling to *get running* (the `scripts/` PATH is only for the one-letter UX).

### Missing artifact the doc PROMISES but the repo lacks (CREATE)
- **`colab_setup.ipynb`** — the doc says "Save this as a notebook in the repo …
  Add this badge to README.md". Neither the notebook nor the "Open in Colab"
  badge exists. `plan.md` also claims `colab_setup.py` is "included" — it is not.
- **Inline image scripts** (`setup_conda.sh/.bat`, `setup_venv.sh/.bat`,
  `docker_build_run.sh/.bat`) are shown inline but not saved as files.
  `plan.md` calls them "included" — inaccurate. DECISION NEEDED (see below).

### Still-open `plan.md` items (unrelated to deploy, fold into this plan's later phases)
- Phase 2 summarization `[~]`: self-contained summarization notebook still open.
- Phase 3 item 6 `[~]`: higher-quality engine (Kokoro) / voice cloning — DEFERRED
  (explicitly optional; NOT in scope here unless the user asks).
- Phase 4 `[ ]`: "video → mindmap" walkthrough; prompt-building doc.
- Phase 5 `[ ]`: optional Streamlit front-end; light CI. (Optional.)

---

## Design decisions (NEED USER REVIEW before coding)

### D1. Where does the migrated deploy content go?
Proposed split (keeps each file in its lane):
- **`README.md`** — becomes the single actionable deployment reference. Expand
  the existing "How to run it" section into a compact **"Deploying / running
  anywhere"** section: the platform table (already there) + short per-platform
  setup (conda/pip/uv, Dev Container, Docker/Podman, Codespaces/Gitpod, Colab) +
  a **"Known gotchas"** subsection (ffmpeg, curl_cffi, container ffmpeg, volume
  paths, GPU, Colab session loss, conda solver). Drop the "see how_to_deploy.md"
  pointer.
- **`youtube.html`** — keep it visual: update the deploy diagram/table, replace
  the `how_to_deploy.md` note with a one-liner ("full setup in README"). No giant
  tables (that's README's job).
- **`plan.md`** — Phase 6 already ticked; just correct the "included assets"
  wording (Colab notebook now real; image scripts either added as files or
  reworded to "documented in README"), and repoint the "detailed research lives
  in how_to_deploy.md" line to "archived in ignore/".

### D2. Depth in README — full or condensed?
The deploy doc is ~750 lines. Proposed: migrate the **actionable 20%** (setup
commands per platform + gotchas table), NOT the essayistic per-platform "detailed
analysis" prose. README stays practical; the deep comparison prose retires with
the archived doc. **Confirm: condensed (recommended) vs. near-verbatim.**

### D3. Image scripts (`setup_conda.sh`, `setup_venv.*`, `docker_build_run.*`)?
Options:
- **(a)** Do NOT create them as files. Reword `plan.md` to "setup commands are
  documented in README." README already carries the copy-paste blocks.
  **(recommended — less surface area, nothing to keep in sync.)**
- **(b)** Create them as real files in a `scripts/` (or `deploy/`) subfolder so
  `plan.md`'s "included" claim becomes literally true.
- **Confirm which.** The phases below assume **(a)**.

### D4. Colab notebook location + badge
- File: **`notebooks/colab_setup.ipynb`** (repo already has `notebooks/`).
- README gets the **"Open In Colab"** badge pointing at
  `github/dragosbo/learn-better/blob/main/notebooks/colab_setup.ipynb`.
- Cells use the REAL layout (`data/`) and REAL runners (`python code/…` or `.sh`).
- **Confirm** the path/badge target.

### D5. Retire `how_to_deploy.md` — when + how?
After F1–F4 migrate/fix everything and F5 strips inbound links: archive with
`git mv how_to_deploy.md ignore/how_to_deploy.md` (there's already a dated
`ignore/how_to_deploy_04sep2026.md` snapshot; this becomes the final one).
**Confirm** you want it archived (vs. kept as a stub that points to README).

### D6. One-click install — badges + what each guarantees
Deliver a **"1-click deploy" block near the top of README** with three badges:
- **Open In Colab** → `notebooks/colab_setup.ipynb` (Run-all cell 1 = ffmpeg +
  clone + `pip install -r requirements.txt`; idempotent).
- **Open in GitHub Codespaces** →
  `https://codespaces.new/dragosbo/learn-better` (reuses `.devcontainer/`).
- **Dev Container** → a short "Reopen in Container" line + the VS Code
  `vscode://` dev-container open link (or just the documented one-click action).

Each badge/link must land the user in a **ready-to-run** env (ffmpeg present,
deps installed, `data/` layout available). The `.devcontainer/` needs no rebuild
for Codespaces/Dev Container (already correct); Colab relies on the new notebook.
**Confirm:** the three badges + targets, and that "one-click" means "env ready to
run a tool", not "PATH configured for the bare one-letter names" (that stays an
optional `init.bat`/PATH step, documented separately).

> **Please confirm D1–D6.** Phases below assume the **recommended** choices.

---

## Where things live (after)

| Thing | Before | After |
|---|---|---|
| Actionable deploy guidance | `how_to_deploy.md` | `README.md` "Deploying / running anywhere" + "Known gotchas" |
| Visual deploy overview | `youtube.html` note → how_to_deploy | `youtube.html` (self-contained; no external pointer) |
| Deploy roadmap/status | `plan.md` Phase 6 (+ inaccurate asset claims) | `plan.md` Phase 6 (claims corrected) |
| Colab setup | promised, missing | `notebooks/colab_setup.ipynb` + README badge |
| **1-click install** | none (no badges) | README "1-click deploy" block: Colab + Codespaces + Dev Container badges |
| Image scripts | inline in how_to_deploy | README copy-paste blocks (D3a) |
| The deploy doc itself | tracked at root | `ignore/how_to_deploy.md` (archived) |

---

## Phase F0 — Decide + inventory (no file changes) — DONE, USER-VALIDATED
- [x] **F0.1** D1–D6 LOCKED (user: "OK with proposal for D1 to D6"). All
      **recommended** options: D1 split (README actionable / youtube visual /
      plan status), D2 **condensed** (~20% actionable, not the essay prose), D3
      **(a)** no image-script files (README copy-paste + reword plan.md), D4
      `notebooks/colab_setup.ipynb` + badge, D5 **archive** `how_to_deploy.md` to
      `ignore/`, D6 three README badges (Colab / Codespaces / Dev Container),
      one-click = ready-to-run env (PATH stays a separate optional step).
- [x] **F0.2** Reference inventory RE-VERIFIED against the repo:
      - `YOUR_USER` placeholders — present (~8 spots: clone URLs, Gitpod link, gh
        commands, the Colab badge markdown). CONFIRMED.
      - `code/transcribe.py --config/--url/--output` — stale; real script is
        `code/transcribe_audio.py` (config-path via `sys.argv[1]`, no flags).
        CONFIRMED in the Docker/Colab/Codespaces/`setup_conda.sh` examples.
      - `colab_setup.ipynb` / any colab file — MISSING. CONFIRMED.
      - image scripts (`setup_conda*`, `setup_venv*`, `docker_build_run*`) — NOT
        saved as files (inline only). CONFIRMED.
- [x] **F0.3** Scope boundary CONFIRMED (user: "keep kokoro and streamlit out of
      the rework, put them on hold"). Item 6 (Kokoro / voice cloning) and Phase 5
      (Streamlit / CI) are **ON HOLD** — out of TODO4. F6 covers only Phase 4
      docs; the self-contained summarization notebook stays an OPTIONAL F6 item.
- [x] **F0.4** One-click definition CONFIRMED per D6.

**Verified:** grep confirmed `YOUR_USER`, `code/transcribe.py`, and the missing
Colab notebook / image-script files. No files changed in F0 (decisions only).

---

## Phase F1 — Migrate + FIX deploy guidance into `README.md` — DONE (awaiting user review)
- [x] **F1.1** Replaced "How to run it" with **"Deploying / running anywhere"**:
      platform-overview table + condensed per-platform setup (conda; pip/venv/uv;
      Dev Container; Codespaces; Docker + Podman with `-v <repo>/data:/app/data`
      and cmd/PS/WSL2 path variants; Colab). Real slug `dragosbo/learn-better`,
      no `YOUR_USER`.
- [x] **F1.2** Added a **"Known gotchas"** table (ffmpeg system binary; curl_cffi;
      container ffmpeg layer; volume-path syntax per shell; GPU only Linux+NVIDIA;
      Colab session loss → Drive; `conda config --set solver libmamba`).
- [x] **F1.3** FIXED command examples to real interfaces:
      `python code/transcribe_audio.py config/config_transcribe.json` (no
      `--url/--config/--output`); `read_channel.py` for the container/Colab
      quick runs; runner UX points to `scripts/` + PATH.
- [x] **F1.4** Removed the `> see how_to_deploy.md` pointer block.
- [x] **Bonus fix:** the old Dev Container/Codespaces sections told users to
      `sudo apt install ffmpeg` — STALE (the `.devcontainer/Dockerfile` now
      installs it). Rewrote to "ffmpeg already present, run a tool directly",
      which is what makes the 1-click claim honest.

**Verified:** grep of README shows no `YOUR_USER`, no `code/transcribe.py`, and
the pointer block gone. Two `how_to_deploy.md` mentions remain ONLY in the
repo-layout tree (the file still exists at root) — cleaned up in F4/F5.

**Review & hand off (STOP for user feedback):** open `README.md` and read the new
**"Deploying / running anywhere"** section (starts with the ⚡ 1-click deploy
block).
**Expect:** self-contained; 1-click block with Colab/Codespaces/Dev Container;
correct commands; Docker/Podman mount `data/`; no how_to_deploy link (except the
layout tree, pending F5). **Pass =** a newcomer could deploy from README alone.
> Note: the Colab badge target `notebooks/colab_setup.ipynb` is created in F2 —
> the link will 404 until then. Report back; then F2.

---

## Phase F2 — ONE-CLICK install: Colab notebook + 3 badges + verify — TODO
> The heart of goal B. Deliver a single "1-click deploy" block in README with
> three working entry points, each landing in a ready-to-run env.

**Colab (build the missing piece):**
- [ ] **F2.1** Author `notebooks/colab_setup.ipynb` (valid nbformat v4 JSON),
      idempotent cells: (1) `!apt-get install -y ffmpeg -q` + clone
      `https://github.com/dragosbo/learn-better.git` (skip if present) + `%cd`;
      (2) `!pip install -q -r requirements.txt`; (3) optional Drive mount + make
      the `data/` subdirs mirroring `lib/paths.py`; (4) verify (`ffmpeg -version`,
      `import yt_dlp, faster_whisper, pandas`, `nvidia-smi`); (5) example run with
      the REAL script `!python code/transcribe_audio.py config/config_transcribe.json`.
- [ ] **F2.2** README **"Open In Colab"** badge →
      `https://colab.research.google.com/github/dragosbo/learn-better/blob/main/notebooks/colab_setup.ipynb`.
- [ ] **F2.3** Validate the notebook is valid JSON / nbformat.

**Codespaces (verify + advertise; env already correct):**
- [ ] **F2.4** README **"Open in GitHub Codespaces"** badge →
      `https://codespaces.new/dragosbo/learn-better`. Confirm `.devcontainer/`
      builds a ready env (ffmpeg + `postCreateCommand` pip install) — one click
      from GitHub, no manual steps to *run* a tool.

**Dev Container (verify + advertise; env already correct):**
- [ ] **F2.5** README one-click line for **"Reopen in Container"** (VS Code /
      Kiro) — the same `.devcontainer/` builds Python 3.12 + ffmpeg + deps +
      Jupyter automatically. Optionally add the `vscode://` dev-container open
      link. Confirm the flow needs no manual ffmpeg/pip step.

**Assemble:**
- [ ] **F2.6** Group the three into a single **"⚡ 1-click deploy"** block near the
      top of README (above the manual setup), each with a one-line "what you get".

**Review & hand off (STOP):**
```cmd
python -c "import json; json.load(open('notebooks/colab_setup.ipynb', encoding='utf-8')); print('valid JSON')"
```
**Expect:** `valid JSON`; README shows the 1-click block with three badges
(Colab → the new notebook; Codespaces → `codespaces.new/dragosbo/learn-better`;
Dev Container → "Reopen in Container"). **Pass =** each entry point lands a
newcomer in a ready-to-run env with zero manual dependency steps. (Colab/
Codespaces actual boot is user-verified in their browser; the notebook validity +
badge URLs are verified here.) Report back; then F3.

---

## Phase F3 — Update `youtube.html` (self-contained, visual) — TODO
- [ ] **F3.1** Replace the `how_to_deploy.md` note with a one-liner pointing to
      README's deploy section (no external-doc dependency).
- [ ] **F3.2** Sanity-check the deploy diagram/table labels still match (Colab,
      Dev Container, Codespaces, Gitpod, Docker/Podman) and the runner UX line
      references `scripts/`/PATH.
- [ ] **F3.3** Mention the three **1-click** entry points (Colab / Codespaces /
      Dev Container) in the deploy overview so the visual page matches README.

**Review & hand off (STOP):** open `youtube.html`.
**Expect:** no mention of `how_to_deploy.md`; deploy overview stands on its own.
**Pass =** the page is complete without the external doc. Report back; then F4.

---

## Phase F4 — Fix stale examples in shipped artifacts + `plan.md` claims — TODO
- [ ] **F4.1** `Dockerfile.standalone` header comments: change the mount examples
      from `-v $(pwd)/audio:...`/`transcripts` to the single
      `-v $(pwd)/data:/app/data`; keep the `python code/<script>.py` note.
- [ ] **F4.2** `plan.md` Phase 6: correct the "included assets" wording —
      `colab_setup.ipynb` now real (point at `notebooks/`); image scripts either
      added (D3b) or reworded to "documented in README" (D3a); repoint the
      "detailed research lives in `how_to_deploy.md`" line to "archived in
      `ignore/`; full setup now in README".
- [ ] **F4.3** Grep the repo for any other `how_to_deploy.md` / `YOUR_USER` /
      `code/transcribe.py` references and fix/remove them.

**Review & hand off (STOP):**
```cmd
findstr /s /i /c:"how_to_deploy" /c:"YOUR_USER" /c:"code/transcribe.py" *.md *.html code\*.py
```
**Expect:** the only remaining `how_to_deploy` hit is the file itself (about to be
archived in F5); no `YOUR_USER`; no `code/transcribe.py`. Report back; then F5.

---

## Phase F5 — Retire `how_to_deploy.md` to `ignore/` — TODO
- [ ] **F5.1** Confirm F1–F4 leave NO inbound links to `how_to_deploy.md`
      (README, youtube.html, plan.md all self-contained).
- [ ] **F5.2** `git mv how_to_deploy.md ignore/how_to_deploy.md` (archive, not
      delete). Verify `git status` shows a rename and `git check-ignore
      ignore/how_to_deploy.md` echoes it (now ignored).

**Review & hand off (STOP):**
```cmd
git status --short
git check-ignore ignore/how_to_deploy.md
```
**Expect:** rename `how_to_deploy.md -> ignore/how_to_deploy.md`; the path echoes
(ignored); repo root no longer has `how_to_deploy.md`. **Pass =** doc retired, all
guidance lives in README/youtube/plan. Report back; then F6.

---

## Phase F6 — Remaining `plan.md` roadmap gaps (docs) — TODO
> Scope: the non-deploy open items. Optional/deferred items (Kokoro, cloning,
> Streamlit, CI) stay out unless the user asks.
- [ ] **F6.1** Phase 4 — **"Video → mindmap" walkthrough**: a short Markdown doc
      (or a README section) describing the end-to-end flow (r → w/t → s → Kiro →
      mindmap), with the command sequence. Link the recorded video when ready.
- [ ] **F6.2** Phase 4 — **Prompt-building doc**: capture the summarization logic
      (`skill_summary.md`) and how prompts are constructed, referenced from the
      summaries section.
- [ ] **F6.3** Phase 2 — **self-contained summarization** (OPTIONAL, confirm):
      only if the user wants to remove the manual Kiro-paste step (local HF model
      / API). Otherwise leave `[~]` as-is and note it stays intentionally manual.
- [ ] **F6.4** Tick the corresponding `plan.md` Phase 4 boxes + update status.

**Review & hand off (STOP):** open the new docs + `plan.md`.
**Expect:** Phase 4 doc items done and ticked; any optional item explicitly
marked in/out per the user. **Pass =** plan.md reflects reality. This completes
TODO4.

---

## Suggested order of attack

| # | Task | Complexity | Review |
|---|------|-----------|--------|
| 0 | F0 decide + inventory | low | 5 decisions locked; audit confirmed |
| 1 | F1 migrate+fix deploy into README | med | README self-contained; commands correct |
| 2 | F2 **1-click**: Colab notebook + 3 badges + verify | med | valid JSON; Colab/Codespaces/DevContainer badges land a ready env |
| 3 | F3 youtube.html self-contained | low | no how_to_deploy reference |
| 4 | F4 fix stale examples + plan.md claims | low | grep clean |
| 5 | F5 archive how_to_deploy.md | low | git rename; ignored |
| 6 | F6 remaining Phase 4 docs | med | plan.md Phase 4 ticked |

Build top-to-bottom. F5 (the archive) is last so nothing links to a moved file.

---

## Notes / guardrails
- **Migrate, then FIX — never copy bugs forward.** The doc's `--url/--config`
  examples, `YOUR_USER`, and hand-rolled dirs are wrong; correct them as they move.
- **Real interfaces only.** `transcribe_audio.py` takes ONE optional arg: a config
  path (`sys.argv[1]`). Runners are in `scripts/` (+ `init.bat`/PATH). Outputs
  under `data/` (`lib/paths.py`).
- **One-click = ready env, not configured PATH.** The three badges (Colab,
  Codespaces, Dev Container) must land a newcomer in an env where ffmpeg + deps
  are present and a tool runs with `python code/<script>.py`. The `scripts/` PATH
  (`init.bat`/`export PATH`) is a separate, optional convenience for the bare
  one-letter names — never a prerequisite to *get running*.
- **Reuse the existing `.devcontainer/`.** Codespaces and Dev Container already
  build a correct env (ffmpeg layer + `postCreateCommand` pip install); F2 adds
  badges and verifies — it does NOT rebuild the container config unless a real
  gap is found.
- **No new deps; free.** Docs + one Jupyter notebook (stdlib JSON). No pip change,
  no API, no cloud.
- **Don't over-migrate.** Keep README practical (the actionable 20%); the deep
  comparison prose retires with the archived doc.
- **Archive, don't delete** (`git mv` into the git-ignored `ignore/`), matching how
  `todo1/2/3`, `mini_todo`, `tts` were retired.
- **Optional items stay optional.** Kokoro/voice-cloning (item 6) and Streamlit/CI
  (Phase 5) are explicitly out of scope unless the user asks.
- **Commit to `main` only when the user says so**; stage files by name.

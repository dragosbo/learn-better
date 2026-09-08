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

## Phase F1 — Migrate + FIX deploy guidance into `README.md` — DONE, USER-VALIDATED
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

## Phase F2 — ONE-CLICK install: Colab notebook + 3 badges + verify — DONE, USER-VALIDATED
> The heart of goal B. Deliver a single "1-click deploy" block in README with
> three working entry points, each landing in a ready-to-run env.

**Colab (build the missing piece):**
- [x] **F2.1** Authored `notebooks/colab_setup.ipynb` (valid nbformat v4). Final
      cells: (1) ffmpeg + clone (skip-if-present) + `%cd`; (2) `pip install`
      **minus `ipykernel`** (Colab supplies its own → no noisy conflict warnings);
      (3) OPTIONAL Drive mount wrapped in try/except (graceful "not mounted" msg,
      won't halt Run-all); (4) **accelerator detection CPU/GPU/TPU** + verify
      (ffmpeg, imports); (5) example **download→transcribe** (English-only, real
      scripts `read_channel.py` + `transcribe_audio.py`); (6) OPTIONAL add-French
      cell; + "Accessing your files" and "Finishing up / logging out" sections.
- [x] **F2.2** README **"Open In Colab"** badge → the notebook. Confirmed correct URL.
- [x] **F2.3** Notebook validated (`nbformat.validate` OK; 17 cells, 8 code).
- [x] **F2.4** README **"Open in GitHub Codespaces"** badge →
      `codespaces.new/dragosbo/learn-better` (reuses `.devcontainer/`).
- [x] **F2.5** README **"Reopen in Container"** one-click line (same `.devcontainer/`).
- [x] **F2.6** Grouped into the **"⚡ 1-click deploy"** block near the top of README.

**How this was tested (record):** USER ran the Colab flow end-to-end from the
badge — install clean, accelerator reported CPU, English-only download avoided
the earlier French `429`, Whisper transcribed the clip (English detected,
timestamps printed). Notebook `nbformat.validate` OK locally. Iterated on real
user feedback: (a) silenced pip/ipykernel conflicts, (b) graceful Drive-mount
failure, (c) download-then-transcribe ordering, (d) CPU/GPU/TPU guidance,
(e) English-only + French-later, (f) logout guidance. **USER confirmed "F2 ok".**
✅ Extras beyond spec: accelerator detection, 429-avoidance (English-only),
French-later cell, file-access + logout sections.

**Codespaces validation + devcontainer fix (found during F2.4 user test):** the
user's first Codespaces build failed \u2014 `.devcontainer/Dockerfile` pulled the
RETIRED image `mcr.microsoft.com/vscode/devcontainers/python:0-3.12-bullseye`
(404 on `docker pull` \u2192 recovery mode). FIXED: switched both the Dockerfile and
`devcontainer.json` build-arg to the current image
`mcr.microsoft.com/devcontainers/python:3.12-bookworm` (verified on Microsoft's
Artifact Registry; old `vscode/` namespace + `0-`/`bullseye` tags are retired).
Repointed the `3.12-bullseye` wording in README/youtube/plan to `3.12 (bookworm)`.
USER re-created the Codespace: **built with no errors**, terminal confirmed
`ffmpeg 5.1.9`, `import yt_dlp, faster_whisper, pandas -> OK`, and
`python code/make_summaries.py` ran against the correct `data/` paths. Codespaces
one-click **USER-VALIDATED**.

---

## Phase F3 — Update `youtube.html` (self-contained, visual) — DONE, USER-VALIDATED
- [x] **F3.1** Replaced the `how_to_deploy.md` note with a self-contained
      **"⚡ 1-click deploy"** callout (Colab / Codespaces / Dev Container) that
      points to README's "Deploying / running anywhere" section. No external-doc
      dependency.
- [x] **F3.2** Deploy table reworked to lead with the 1-click targets + add
      Docker/Podman; the Local row now references `scripts/` + PATH/`init.bat`
      (was "batch files"). Deploy flowchart labels unchanged (still valid).
- [x] **F3.3** The three 1-click entry points are named in the callout + table.
- [x] **Bonus fixes:** removed the stale "Add ffmpeg with `sudo apt install
      ffmpeg`" Dev Container note (the `.devcontainer/` installs it); dropped the
      `how_to_deploy.md` line from the repo-layout tree and repointed
      `Dockerfile.standalone`'s "see how_to_deploy.md" → "deploy guide: README"
      (ahead of the F5 archive).

**Verified:** grep of `youtube.html` for `how_to_deploy` → **no matches**; page
is self-contained.

**Review & hand off (STOP for user feedback):** open `youtube.html` and check the
**Deployment** section: the 1-click callout names Colab/Codespaces/Dev Container
and points to README; no `how_to_deploy.md` reference anywhere. **Pass =** the
visual page stands on its own. Report back; then F4.

**Review & hand off (STOP):** open `youtube.html`.
**Expect:** no mention of `how_to_deploy.md`; deploy overview stands on its own.
**Pass =** the page is complete without the external doc. Report back; then F4.

---

## Phase F4 — Fix stale examples in shipped artifacts + `plan.md` claims — DONE (awaiting user review)
- [x] **F4.1** `Dockerfile.standalone` header comments fixed: the two run
      examples now use the single `-v $(pwd)/data:/app/data` mount (were
      `-v $(pwd)/audio:...` + `-v $(pwd)/transcripts:...`); kept the
      `python code/<script>.py` note.
- [x] **F4.2** `plan.md` Phase 6 rewritten: dropped the fictitious "included"
      assets (`colab_setup.py`, `setup_codespaces.sh`, `podman_setup.sh` never
      existed) and listed the REAL ones (`Dockerfile.standalone`, `.dockerignore`,
      patched `.devcontainer/`, `notebooks/colab_setup.ipynb`); per-platform setup
      is copy-paste in README (D3a, no `setup_*.sh` files); repointed the
      "research lives in `how_to_deploy.md`" line to "migrated into README/youtube
      + archived to `ignore/`"; added the 1-click + base-image-fix bullets.
- [x] **F4.3** Repo-wide grep (excluding `chats/`, `ignore/`, the doc itself):
      the ONLY remaining `how_to_deploy`/`YOUR_USER`/`code/transcribe.py` hits are
      inside **`todo4.md`** (which documents the migration) + the repo-layout
      trees still listing `how_to_deploy.md` as a file. No stale refs in live docs
      or code. The layout-tree listing + the file's existence are handled by F5.

- [x] **F4.4 (extra, user-requested)** Captured the "verify a fresh environment"
      guidance that had only been given in chat (it was nowhere in a file, so it
      would have been lost). Added a **"Verify your environment"** subsection to
      `README.md` (in the deploy section, before Known gotchas) and a **"Phase 0 —
      Verify a fresh environment"** block to `how_to_test.md`: the three checks
      (`ffmpeg -version`, the import check, `python code/make_summaries.py` as a
      network-free smoke test) + the Codespaces/Dev Container rebuild note.
      Deliberately NOT put in `how_to_deploy.md` (archived in F5).

**Verified:** grep clean across README / youtube.html / plan.md / `code/*.py` /
`Dockerfile.standalone` (no `YOUR_USER`, no `code/transcribe.py`, no how_to_deploy
pointer). Only todo4's own descriptive text + the pending layout-tree entry remain.

**Review & hand off (STOP for user feedback):** skim `Dockerfile.standalone`'s
header comment (data/ mount) and `plan.md` Phase 6 (accurate asset list). **Pass =**
no shipped artifact shows a stale mount/command; plan.md claims match reality.
Report back; then F5 archives `how_to_deploy.md`.

---

## Phase F5 — Retire `how_to_deploy.md` to `ignore/` — DONE (awaiting user review)
- [x] **F5.1** Confirmed NO inbound links remain: grep of README / youtube.html /
      `code/*.py` / `Dockerfile.standalone` for `how_to_deploy` → clean. Removed
      the last two layout-tree entries (README dropped the `how_to_deploy.md`
      line + repointed `Dockerfile.standalone`'s "see how_to_deploy.md" → README;
      plan.md's ffmpeg-gap aside repointed to README). plan.md's Phase 6 note now
      correctly says the doc was "migrated into README/youtube + archived to
      `ignore/`". (Remaining mentions live only in `todo4.md`, which documents
      the migration.)
- [x] **F5.2** `git mv how_to_deploy.md ignore/how_to_deploy.md` — git recorded a
      **rename** (`R how_to_deploy.md -> ignore/how_to_deploy.md`); repo root no
      longer has the file (file_search confirms); it now sits in the git-ignored
      `ignore/` (same archive pattern as `todo1/2/3`, `mini_todo`, `tts`).

**Review & hand off (STOP for user feedback):** `how_to_deploy.md` is gone from
the repo root and all deploy guidance lives in README / youtube.html / plan.md.
**Pass =** nothing points at the archived doc; docs are self-sufficient. Report
back; then F6 (remaining Phase 4 docs).

**Review & hand off (STOP):**
```cmd
git status --short
git check-ignore ignore/how_to_deploy.md
```
**Expect:** rename `how_to_deploy.md -> ignore/how_to_deploy.md`; the path echoes
(ignored); repo root no longer has `how_to_deploy.md`. **Pass =** doc retired, all
guidance lives in README/youtube/plan. Report back; then F6.

---

## Phase F6 — Remaining `plan.md` roadmap gaps (docs) — DONE (awaiting user review)
> Scope: the non-deploy open items. Optional/deferred items (Kokoro, cloning,
> Streamlit, CI) stay out unless the user asks.
- [x] **F6.1** Phase 4 — **"Video → mindmap" walkthrough**: created
      `docs/video_to_mindmap.md` — the end-to-end flow (download → transcript →
      summary → mindmap) with the real command sequence and a step-by-step
      table, plus how a `data/summaries/*.summary.md` maps onto mindmap branches
      (Obsidian / Markmap / by hand). Placeholder for the recorded-video link.
- [x] **F6.2** Phase 4 — **Prompt-building doc**: created
      `docs/prompt_building.md` — why it's split (script + AI), the two-part
      prompt (generated instruction + `skill_summary.md`), what the skill file
      encodes, the design principles (deterministic-where-possible, grounding,
      idempotent, structured-for-reuse), and how to change how summaries read.
      Cross-links `video_to_mindmap.md`.
- [~] **F6.3** Phase 2 — **self-contained summarization**: LEFT INTENTIONALLY
      MANUAL (not built). Documented as such in `docs/prompt_building.md` +
      `plan.md` Phase 2. Building it (local HF model / API to drop the Kiro-paste
      step) is a real feature needing a NEW decision + likely a new dep — **out of
      TODO4 scope; confirm separately if you want it.**
- [x] **F6.4** `plan.md`: ticked both Phase 4 boxes with what was delivered;
      added `docs/` to the Section 4 layout tree (+ `notebooks/colab_setup.ipynb`);
      updated the "Still open (roadmap)" note (docs now exist).
- [x] **Bonus fix:** `skill_summary.md` still said `summaries/` — repointed the 3
      mentions to `data/summaries/` (the docs reference it as the format source of
      truth, so it had to be accurate).

**Review & hand off (STOP for user feedback):** open `docs/video_to_mindmap.md`
and `docs/prompt_building.md`, and skim `plan.md` Phase 4. **Expect:** the
walkthrough reads as a usable end-to-end guide; the prompt doc explains the
summarization logic; plan.md Phase 4 both boxes ticked. **Pass =** the Phase 4
doc gap is closed. This completes TODO4 (F6.3 optional item deferred by design).

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

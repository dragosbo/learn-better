# How to deploy — learn-better

> **What "deploy" means here:** Reproducibly setting up the Python environment so `code/`, the `lib/` modules, and all helper scripts run correctly on a target machine. This project is not published as a PyPI package — there is no `pyproject.toml`/`setup.py` — so deployment means cloning the repo and wiring up the right Python + ffmpeg environment. The choice of *where* to run it (your laptop, a cloud VM, a container) is the main decision this document helps you make.

### OS legend used throughout this document

| Badge | Means |
|---|---|
| 🪟 | Windows (cmd / PowerShell) |
| 🐧 | Linux (Debian/Ubuntu/Fedora, any distro) |
| 🍎 | macOS |
| ☁️ | Cloud / browser-based (no local OS assumption) |

> **Runner scripts live in `scripts/`.**  Both platforms are covered: `scripts\a.bat` / `scripts\c.bat` / … (🪟 Windows, require conda `learn-better`) and `./scripts/a.sh` / `./scripts/c.sh` / … (🐧 🍎 Linux & macOS, auto-activate conda if present). Cloud platforms and containers run 🐧 Linux — use the `.sh` runners or call `python code/<script>.py` directly.

> **Output layout — all outputs live under `data/`** (defined in `lib/paths.py`):
> `data/audio/`, `data/audio_reencoded/`, `data/transcripts/`, `data/generated_transcripts/`,
> `data/summaries/` *(git-tracked)*, `data/tts_output/`, `data/wordclouds/`.
> Everything under `data/` is git-ignored except `data/summaries/`. Mount a single `-v $(pwd)/data:/app/data` volume when using Docker/Podman.

---

## Master ranking — complexity vs. capabilities

Lower complexity = faster to get running from zero. Capabilities = how much of the full feature set you get (ffmpeg, Whisper, yt-dlp, notebooks, scripts/ runners, persistent storage).

| # | Platform | OS | Complexity | Capabilities | GPU | Persistent | Cost | Best for |
|---|----------|-----|-----------|--------------|-----|------------|------|----------|
| 1 | **Google Colab** | ☁️ Linux | ⭐ | ★★★★☆ | ✅ T4 free | ❌ re-setup / Drive | Free | One-off GPU transcription |
| 2 | **GitHub Codespaces** | ☁️ Linux | ⭐⭐ | ★★★★★ | ❌ | ✅ per-codespace | 60 core-h/mo free | Remote VS Code, no local install |
| 3 | **Local — conda** | 🪟 🐧 🍎 | ⭐⭐ | ★★★★★ | ❌ CPU | ✅ | Free | Day-to-day; `scripts/` runners for 🪟🐧🍎 |
| 4 | **Local — pip + venv** | 🪟 🐧 🍎 | ⭐⭐ | ★★★★☆ | ❌ CPU | ✅ | Free | Minimal tooling, simple |
| 5 | **Local — uv** | 🪟 🐧 🍎 | ⭐⭐ | ★★★★☆ | ❌ CPU | ✅ | Free | Fast rebuilds, lockfile reproducibility |
| 6 | **VS Code Dev Container** | 🪟 🐧 🍎 → 🐧 inside | ⭐⭐⭐ | ★★★★★ | ❌ | ✅ | Free (Docker req.) | Consistent team env |
| 7 | **Kiro IDE Dev Container** | 🪟 🐧 🍎 → 🐧 inside | ⭐⭐⭐ | ★★★★★ | ❌ | ✅ | Free (Docker req.) | Same + Kiro AI features |
| 8 | **Gitpod** | ☁️ Linux | ⭐⭐⭐ | ★★★★☆ | ❌ | ✅ workspace | 50 h/mo free | Alternative to Codespaces |
| 9 | **Replit** | ☁️ Linux | ⭐⭐⭐ | ★★☆☆☆ | ❌ | ✅ | Free tier limited | ❌ Not recommended (network blocks yt-dlp) |
| 10 | **Docker** | 🪟 🐧 🍎 → 🐧 inside | ⭐⭐⭐⭐ | ★★★★★ | ❌ (🐧 GPU ok) | ✅ volume | Free (Docker req.) | CI, reproducible builds |
| 11 | **Podman** | 🐧 🍎 (🪟 via WSL2) | ⭐⭐⭐⭐ | ★★★★★ | ❌ (🐧 GPU ok) | ✅ volume | Free | Rootless/daemonless Docker alternative |
| 12 | **Binder** | ☁️ Linux | ⭐ | ★☆☆☆☆ | ❌ | ❌ | Free | ❌ Not recommended — 2 GB RAM, ephemeral |

> **Key constraint across all platforms:** `ffmpeg` is a system binary — `pip` and `uv` cannot install it. Every non-conda platform requires an explicit system-level ffmpeg install step. This is the #1 source of setup failures.

> **Container OS note:** Dev Containers, Docker, and Podman all run a **Linux** environment inside the container regardless of the host OS. This means `.bat` files on your Windows host cannot run inside the container — use the Python scripts directly or the `./scripts/*.sh` runners from inside the container.

---

## Part 1 — Local Installation

Three methods for running directly on your machine (🪟 🐧 🍎). All produce identical functionality; they differ in how much setup burden they put on you versus the tooling.

### Method 1 — conda (recommended)

Conda manages Python *and* system binaries inside the same environment. It is the **only** method that installs `ffmpeg` automatically, and it matches what the `scripts/*.bat` runners in the repo assume.

**Prerequisites:** [Miniconda](https://docs.conda.io/en/latest/miniconda.html) or Anaconda installed. The conda commands below are identical on all three OS — this is one of conda's main advantages.

```bash
# 🪟 🐧 🍎 — identical on all platforms
conda create -n learn-better python=3.12 -y
conda activate learn-better
conda install -c conda-forge ffmpeg -y
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Verify:

```bash
# 🪟 🐧 🍎
python --version        # Python 3.12.x
ffmpeg -version         # version banner, NOT "not found"
python -c "import yt_dlp, faster_whisper, pandas; print('OK')"
```

> **Running scripts — shortcuts via `init.bat` / PATH setup:**
>
> **🪟 Windows — option A (one-time PATH setup with `init.bat`):**
> Run `init` once from the repo root in `cmd` to add `scripts\` to PATH for the current session — then use bare one-letter names from anywhere in the repo:
> ```cmd
> init                    :: run once; adds scripts\ to PATH for this cmd session
> c                       :: activate conda env
> r                       :: download audio + transcripts
> t  w  s  p  wc  a  v   :: other runners
> ```
> For permanent PATH (survives new terminals): *System Properties → Environment Variables → Path* → add the full path to `…\learn-better\scripts`.
>
> **🪟 Windows — option B (no PATH change):** prefix with `scripts\` every time: `scripts\r.bat`, `scripts\t.bat`, `scripts\w.bat`, …
>
> **🐧 🍎 Linux/macOS — option A (session PATH setup):**
> ```bash
> # Run from the repo root — adds scripts/ to PATH for this shell session
> export PATH="$PWD/scripts:$PATH"
> r.sh   t.sh   w.sh   …   # bare names now work
> ```
> Permanent: add the line (with the absolute repo path) to `~/.bashrc` (🐧) or `~/.zshrc` (🍎).
>
> **🐧 🍎 Linux/macOS — option B (no PATH change):** `./scripts/r.sh`, `./scripts/t.sh`, …
>
> All `.sh` runners auto-activate the conda env if `conda` is present (via `conda.sh` sourcing); in Docker/Codespaces they use the current `python` directly.

**Pros:**
- ffmpeg installed inside the conda env — no separate manual step, no PATH confusion
- 🪟 Environment name `learn-better` matches all `scripts\*.bat` runners exactly; 🐧🍎 `scripts/*.sh` equivalents provided
- Reproducible across 🪟 🐧 🍎 without platform-specific branching

**Cons:**
- Conda's dependency solver is slow (3–10 min on first `create`)
- Requires Miniconda/Anaconda if not already present (150–500 MB installer)
- Mixing conda and pip within the same env is safe here but is a code smell some teams avoid

---

### Method 2 — pip + venv

The standard library approach. No extra tooling beyond Python 3.12.

**Prerequisites:**

- 🪟 Python 3.12 from [python.org](https://python.org) or `winget install Python.Python.3.12`
- 🐧 `sudo apt-get install python3.12 python3.12-venv` (Debian/Ubuntu) or `sudo dnf install python3.12` (Fedora)
- 🍎 `brew install python@3.12`

**Create and activate the environment:**

```cmd
:: 🪟 Windows (cmd)
py -3.12 -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

```bash
# 🐧 Linux / 🍎 macOS
python3.12 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

**Install ffmpeg separately:**

```cmd
:: 🪟 Windows — choose one:
winget install ffmpeg        # Windows 10/11 built-in package manager
choco install ffmpeg         # Chocolatey
```

```bash
# 🐧 Debian / Ubuntu
sudo apt-get update && sudo apt-get install -y ffmpeg

# 🐧 Fedora / RHEL
sudo dnf install ffmpeg

# 🍎 macOS
brew install ffmpeg
```

> 🪟 **Windows PATH caveat:** After `winget install ffmpeg`, open a **new** terminal window before running `ffmpeg -version`. The PATH update does not apply to already-open terminals. If it still fails, reboot once.

Verify: `python --version`, `ffmpeg -version`, and the import check from Method 1.

**Pros:**
- Zero extra tooling — `venv` ships with Python
- Fast pip solver compared to conda
- Universally understood by any Python developer

**Cons:**
- ffmpeg is a manual step — easy to forget; PATH changes need a fresh terminal (🪟) or reboot
- No lockfile by default — sub-dependency versions can drift over time
- 🪟 `scripts\*.bat` / 🐧🍎 `scripts/*.sh` runners assume conda `learn-better`; adapt them or call `python code/<script>.py` directly

---

### Method 3 — uv (fastest)

[uv](https://docs.astral.sh/uv/) is a Rust-based drop-in for pip + venv + pip-tools. Ideal for CI, Codespaces, or frequent rebuilds.

**Install uv once:**

```cmd
:: 🪟 Windows
winget install --id=astral-sh.uv -e
```

```bash
# 🐧 Linux / 🍎 macOS
curl -LsSf https://astral.sh/uv/install.sh | sh
# Then reload your shell: source ~/.bashrc  OR  source ~/.zshrc
```

**Set up the environment:**

```cmd
:: 🪟 Windows
uv venv --python 3.12
.venv\Scripts\activate
uv pip install -r requirements.txt
```

```bash
# 🐧 Linux / 🍎 macOS
uv venv --python 3.12
source .venv/bin/activate
uv pip install -r requirements.txt
```

**Optional fully-locked install (same on all OS):**

```bash
uv pip compile requirements.txt -o requirements.lock.txt
uv pip sync requirements.lock.txt
```

**Install ffmpeg:** same manual step as Method 2 above (🪟 winget/choco · 🐧 apt/dnf · 🍎 brew).

**Pros:**
- Noticeably faster than pip — parallel Rust resolver + global package cache
- `uv pip compile` + `uv pip sync` gives a full lockfile (exact sub-dependency versions)
- Drop-in replacement: all pip commands work with `uv pip` prefix

**Cons:**
- uv must be installed first (trivial, but one extra step vs pip which ships with Python)
- ffmpeg still a manual step — same PATH caveat on 🪟 as Method 2
- 🪟 `scripts/*.bat` runners still need adaptation (same conda env assumption as pip + venv)

---

### Local comparison table

| Criterion | pip + venv | conda | uv |
|---|---|---|---|
| Handles ffmpeg in-environment | ❌ manual | ✅ automatic | ❌ manual |
| Python dep reproducibility | Good (pinned ranges) | Good | **Best** (lockfile) |
| Setup speed | Medium | Slowest | **Fastest** |
| 🪟 Matches existing `scripts/*.bat` runners | ❌ adapt needed | ✅ Yes | ❌ adapt needed |
| Extra tooling to install | None | Miniconda | uv |
| "Works on my machine" risk | Medium (ffmpeg) | **Lowest** | Medium (ffmpeg) |
| Platform command differences | 🪟 vs 🐧🍎 activate differ | None — identical | 🪟 vs 🐧🍎 install differ |

**Recommendation:** Use **conda** for day-to-day local work (ffmpeg handled, 🪟 `scripts/*.bat` runners just work (and `scripts/*.sh` for 🐧🍎)). Use **uv** in CI or when rebuilding frequently. Use **pip + venv** only if you need zero extra tooling and are comfortable with the manual ffmpeg step.

---

### Recommended: Deno JS runtime (for yt-dlp)

Recent versions of yt-dlp print `No supported JavaScript runtime could be found` and warn that "YouTube extraction without a JS runtime has been deprecated." The tools still work without one — impersonation via `curl_cffi` covers subtitles and audio downloads — but YouTube increasingly embeds JS in its player, so installing a runtime is **recommended**. It removes the warning and can restore formats yt-dlp would otherwise skip.

Install **Deno** once (it is the runtime yt-dlp uses by default):

```cmd
:: 🪟 Windows
winget install DenoLand.Deno    :: then open a NEW terminal so deno is on PATH
```

```bash
# 🍎 macOS
brew install deno

# 🐧 Linux
curl -fsSL https://deno.land/install.sh | sh
# Reload your shell: source ~/.bashrc  OR  source ~/.zshrc
```

Verify: `deno --version`. yt-dlp finds it automatically on the next run; the JS-runtime warning disappears.

> The project code also passes `no_warnings` to yt-dlp, so the message is suppressed even if Deno is absent — but installing Deno is the proper long-term fix.

---

## Part 2 — Containerised (self-hosted)

These options run the project inside a **Linux container** on your machine, regardless of the host OS. Docker or Podman must be installed:

| Host OS | Free option | Commercial option |
|---|---|---|
| 🪟 Windows | [Rancher Desktop](https://rancherdesktop.io) (free) | Docker Desktop (free ≤ small business) |
| 🐧 Linux | Docker Engine (`apt install docker.io`) — always free | — |
| 🍎 macOS | Rancher Desktop or [OrbStack](https://orbstack.dev) (free for individuals) | Docker Desktop |

> **Inside the container:** the environment is always **🐧 Linux** (Debian Bookworm or Bullseye). `scripts/*.bat` runners from the 🪟 Windows host do **not** run inside the container. Use `./scripts/*.sh` runners or call Python scripts directly.

> **Important:** The existing `.devcontainer/Dockerfile` in this repo has a **confirmed gap** — it does not install `ffmpeg`. All container-based options below include the fix.

---

### VS Code Dev Container

The repo already ships a `.devcontainer/` configuration. With the ffmpeg gap fixed, this is the smoothest team-onboarding experience: clone the repo, open in VS Code, click "Reopen in Container", and the full environment builds automatically.

**Prerequisites:** Docker Desktop / Rancher Desktop / OrbStack (see table above), VS Code with the [Dev Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers).

**The fix — patch `.devcontainer/Dockerfile`:**

The current Dockerfile is only two lines:
```dockerfile
ARG VARIANT="3.12-bullseye"
FROM mcr.microsoft.com/vscode/devcontainers/python:0-${VARIANT}
```

Add an ffmpeg install layer:
```dockerfile
ARG VARIANT="3.12-bullseye"
FROM mcr.microsoft.com/vscode/devcontainers/python:0-${VARIANT}

# Fix: install ffmpeg (missing from original devcontainer)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*
```

Also remove the unnecessary `azure-cli` feature from `devcontainer.json` (saves ~200 MB and build time).

**Minimal working guidance:**

1. Open the cloned repo folder in VS Code
2. When prompted "Reopen in Container", click it (or Command Palette → "Dev Containers: Reopen in Container")
3. Wait for the container to build (2–5 min first time, cached on subsequent opens)
4. The terminal opens inside the 🐧 Linux container — `ffmpeg -version` and Python imports work immediately
5. Run scripts: `./scripts/r.sh` (or any other `scripts/*.sh` runner), or `python code/<script>.py` directly
6. Jupyter notebooks: use the Jupyter extension already installed in the devcontainer

**Pros:**
- One-click environment: Python 3.12, ffmpeg, all pip deps, VS Code extensions — all automatic
- Container is isolated — no polluting the host machine
- Works identically on 🪟 🐧 🍎 host machines
- Rebuild is trivial if the environment gets corrupted
- Port 8000 already forwarded in `devcontainer.json`

**Cons:**
- 🪟 Requires Rancher Desktop (free) or Docker Desktop (license check for commercial use)
- Cold start after a rebuild: 2–5 min
- 🐧 Inside the container — use `./scripts/*.sh` runners or Python scripts directly
- The existing Dockerfile uses Microsoft's devcontainer base image (300+ MB) — heavier than a minimal Python image
- GPU passthrough: 🐧 Linux host + NVIDIA Container Toolkit only; not available on 🪟 🍎

---

### Kiro IDE Dev Container

[Kiro](https://kiro.dev) is Amazon's IDE (released 2025), built on VS Code, with native AI agent features (Specs & Hooks). It reads the same `devcontainer.json` spec as VS Code — setup is identical.

**Prerequisites:** [Kiro IDE](https://kiro.dev/downloads/), Docker Desktop or Rancher Desktop.

**Minimal working guidance:** Apply the same Dockerfile ffmpeg fix → open repo in Kiro → Command Palette → "Dev Containers: Reopen in Container". Identical result to VS Code devcontainer.

**Pros:** Everything from VS Code Dev Container + Kiro AI Specs/Hooks for task automation.

**Cons:** Kiro is newer (less battle-tested). AWS credentials needed for full AI features. Same Docker + 🐧-inside-container caveat.

---

### Docker (standalone)

Run the project in a fully self-contained image. No IDE required. Useful for scripted batch processing, CI, or server deployment.

**Prerequisites:** Docker Engine (🐧) or Docker Desktop / Rancher Desktop (🪟 🍎).

**Build (identical on all host OS):**
```bash
docker build -f Dockerfile.standalone -t learn-better .
```

**Run interactively with volume mount for persistent output:**

> All outputs are consolidated under `data/` (see `lib/paths.py`). A single volume mount covers everything — audio, transcripts, summaries, TTS, word clouds.

```cmd
:: 🪟 Windows (cmd) — use %CD% for current directory
docker run -it --rm ^
  -v "%CD%\data:/app/data" ^
  learn-better
```

```bash
# 🐧 Linux / 🍎 macOS — use $(pwd)
docker run -it --rm \
  -v "$(pwd)/data:/app/data" \
  learn-better
```

> 🪟 **Windows PowerShell:** use `${PWD}` instead of `%CD%`:
> ```powershell
> docker run -it --rm -v "${PWD}\data:/app/data" learn-better
> ```

**Run a specific script non-interactively:**
```bash
# 🐧 🍎 (and 🪟 PowerShell with ${PWD})
docker run --rm \
  -v "$(pwd)/data:/app/data" \
  learn-better \
  python code/transcribe.py --config data/config.json
```

**🐧 GPU passthrough (Linux + NVIDIA only):**
```bash
docker run --gpus all -it --rm \
  -v "$(pwd)/data:/app/data" \
  learn-better \
  python code/transcribe.py
```

**Pros:**
- Maximum reproducibility — identical 🐧 Linux environment on any host
- No IDE required; CI-friendly (GitHub Actions, GitLab CI, Jenkins)
- `python:3.12-slim-bookworm` base is ~200 MB — lighter than the MS devcontainer base
- Can be pushed to a registry and pulled on any server

**Cons:**
- All I/O must go through volume mounts — outputs in the container are lost without `-v`
- No GUI / Jupyter by default (add `--port 8888` + `jupyter notebook --ip=0.0.0.0 --no-browser`)
- 🐧 Inside container — use `./scripts/*.sh` runners or Python scripts directly
- No GPU on 🪟 🍎 Docker Desktop
- Requires Docker knowledge for day-to-day use

---

### Podman

Podman is a daemonless, rootless container engine compatible with Docker syntax. Preferred in security-sensitive environments and 🐧 Linux servers.

**Prerequisites:**

```cmd
:: 🪟 Windows
winget install RedHat.Podman
:: Then use Podman Desktop (GUI) or WSL2 terminal for commands
```

```bash
# 🐧 Debian / Ubuntu
sudo apt-get install -y podman

# 🐧 Fedora / RHEL
sudo dnf install podman

# 🍎 macOS
brew install podman
```

> 🪟 **Windows note:** Podman on Windows runs through WSL2. Commands are run inside the WSL2 Linux shell, not cmd/PowerShell. Volume paths use Linux syntax: `-v /mnt/c/Users/you/project/data:/app/data`.

**Commands (same syntax as Docker, substitute `podman` for `docker`):**
```bash
podman build -f Dockerfile.standalone -t learn-better .

# 🐧 🍎 — note the :Z suffix on Fedora/RHEL for SELinux
podman run -it --rm \
  -v "$(pwd)/data:/app/data:Z" \
  learn-better
```

**Pros:**
- Rootless by default — no daemon running as root (better security posture than Docker)
- No Docker Desktop license concerns
- 🐧 Linux: available in standard distro repos, no extra install beyond `apt install podman`
- `podman compose` replaces `docker compose` for multi-container setups

**Cons:**
- 🪟 Windows: requires WSL2 — not as seamless as Docker Desktop; volume paths need Linux format
- Slightly less CI ecosystem support (some systems default to Docker)
- SELinux `:Z` volume label quirks on 🐧 RHEL/Fedora


---

## Part 3 — Cloud / Free Platforms

All cloud platforms run 🐧 **Linux**. Use `./scripts/*.sh` runners or call Python scripts directly. The ffmpeg install is always `apt-get install -y ffmpeg` (or `!apt-get` in Colab). No PATH gotchas — the shell is bash, and PATH changes apply immediately.

---

### Google Colab ☁️

Google Colab is a hosted Jupyter environment with free GPU access. It is the fastest path to running Whisper transcriptions with T4 GPU acceleration — 5–10× faster than CPU. Every session boots a fresh 🐧 Ubuntu VM; nothing persists between sessions unless you deliberately save it to Google Drive or another external store.

**Free tier:** ~12 h session (varies by load), T4 GPU, ~13 GB RAM, ~78 GB temp disk. Disconnects on inactivity or resource reclaim.

---

#### Setup cells (run once per session)

Paste these as separate notebook cells. They are idempotent — safe to re-run.

```python
# Cell 1 — System deps + repo clone
# (run this first, every session)
import os

!apt-get install -y ffmpeg -q

REPO = "https://github.com/YOUR_USER/learn-better.git"
if not os.path.exists("/content/learn-better"):
    !git clone {REPO} /content/learn-better

%cd /content/learn-better
```

```python
# Cell 2 — Python dependencies
!pip install -q -r requirements.txt
```

```python
# Cell 3 — Verify
!python --version
!ffmpeg -version | head -1
import yt_dlp, faster_whisper, pandas
print("✅ All imports OK")
```

> **GPU check:** `!nvidia-smi` — if it shows a T4, `faster-whisper` will use CUDA automatically (no code change needed). If it shows "no CUDA devices", go to Runtime → Change runtime type → T4 GPU and reconnect.

---

#### GitHub interaction from Colab

Colab runs a full 🐧 Linux shell, so `git` is available out of the box. The level of interaction depends on whether you need read-only access (public repos) or read-write (pushing changes).

**Clone (read-only, no authentication needed for public repos):**
```python
# Already in Cell 1 above — this is sufficient for most use cases
!git clone https://github.com/YOUR_USER/learn-better.git /content/learn-better
```

**Pull latest changes mid-session (if the repo was updated):**
```python
%cd /content/learn-better
!git pull origin main
```

**Push changes back to GitHub (requires a Personal Access Token):**

GitHub removed password auth in 2021 — use a PAT (Personal Access Token). Generate one at GitHub → Settings → Developer settings → Personal access tokens → Fine-grained tokens (scope: `Contents: Read and write` on your repo).

```python
# Option A — embed token in the remote URL (simplest, session-only)
import os
TOKEN = "ghp_YOUR_TOKEN_HERE"   # or use Colab Secrets (see below)
REPO  = "YOUR_USER/learn-better"

!git -C /content/learn-better config user.email "you@example.com"
!git -C /content/learn-better config user.name  "Your Name"
!git -C /content/learn-better remote set-url origin \
    https://{TOKEN}@github.com/{REPO}.git

# Then commit and push normally:
!git -C /content/learn-better add -A
!git -C /content/learn-better commit -m "Colab: add transcription results"
!git -C /content/learn-better push origin main
```

> **Security:** Never hardcode your token in a shared notebook. Use **Colab Secrets** instead (🔑 icon in the left sidebar → add `GITHUB_TOKEN`):
> ```python
> from google.colab import userdata
> TOKEN = userdata.get('GITHUB_TOKEN')
> ```

**Use the `gh` CLI (GitHub's official CLI — more ergonomic for PRs, issues, releases):**
```python
# Install gh CLI once per session
!curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg \
    | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg
!echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] \
    https://cli.github.com/packages stable main" \
    | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null
!sudo apt-get update -q && sudo apt-get install -y gh -q

# Authenticate using your token
from google.colab import userdata
import subprocess
TOKEN = userdata.get('GITHUB_TOKEN')
subprocess.run(["gh", "auth", "login", "--with-token"], input=TOKEN, text=True)

# Now use gh normally:
!gh repo view YOUR_USER/learn-better
!gh issue list
```

**Download a single file from a private repo (without cloning the whole repo):**
```python
from google.colab import userdata
import requests, os

TOKEN = userdata.get('GITHUB_TOKEN')
headers = {"Authorization": f"token {TOKEN}", "Accept": "application/vnd.github.v3.raw"}
url = "https://api.github.com/repos/YOUR_USER/learn-better/contents/requirements.txt"

resp = requests.get(url, headers=headers)
with open("/content/requirements.txt", "wb") as f:
    f.write(resp.content)
```

---

#### Google Drive integration — persist results across sessions

Because Colab sessions are ephemeral, saving outputs to Google Drive is the standard way to get durability without a paid subscription.

**Mount Drive:**
```python
from google.colab import drive
drive.mount('/content/drive')
# A browser popup asks for permission — grant it.
# After mounting, your Drive root is at /content/drive/MyDrive/
```

**Define your project output folder on Drive:**
```python
import os

DRIVE_PROJECT = "/content/drive/MyDrive/learn-better-output"
os.makedirs(DRIVE_PROJECT, exist_ok=True)

# Subdirectories mirror lib/paths.py layout under data/
AUDIO_DIR              = f"{DRIVE_PROJECT}/audio"
AUDIO_REENCODED_DIR    = f"{DRIVE_PROJECT}/audio_reencoded"
TRANSCRIPTS_DIR        = f"{DRIVE_PROJECT}/transcripts"
GEN_TRANSCRIPTS_DIR    = f"{DRIVE_PROJECT}/generated_transcripts"
SUMMARIES_DIR          = f"{DRIVE_PROJECT}/summaries"
TTS_OUTPUT_DIR         = f"{DRIVE_PROJECT}/tts_output"
WORDCLOUD_DIR          = f"{DRIVE_PROJECT}/wordclouds"
for d in [AUDIO_DIR, AUDIO_REENCODED_DIR, TRANSCRIPTS_DIR, GEN_TRANSCRIPTS_DIR,
          SUMMARIES_DIR, TTS_OUTPUT_DIR, WORDCLOUD_DIR]:
    os.makedirs(d, exist_ok=True)

print(f"Output root: {DRIVE_PROJECT}")
```

**Write outputs directly to Drive from scripts:**

If the scripts in `code/` accept an output path argument, pass the Drive path directly:
```python
!python code/transcribe.py \
    --url "https://www.youtube.com/watch?v=EXAMPLE" \
    --output {TRANSCRIPTS_DIR}
```

If a script writes to a local path, copy afterwards:
```python
import shutil, glob

# Copy outputs from all data/ subdirs to Drive
# data/ layout: audio/, transcripts/, generated_transcripts/, summaries/, tts_output/, wordclouds/
import pathlib
DATA = pathlib.Path("/content/learn-better/data")
for src in DATA.rglob("*"):
    if src.is_file():
        dest = pathlib.Path(DRIVE_PROJECT) / src.relative_to(DATA)
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(src, dest)
        print(f"Saved: {src.relative_to(DATA)}")
```

**Cache Whisper model weights on Drive** (avoids 1–3 GB re-download every session):
```python
import os
WHISPER_CACHE = f"{DRIVE_PROJECT}/whisper-model-cache"
os.makedirs(WHISPER_CACHE, exist_ok=True)

from faster_whisper import WhisperModel
# device="cuda" uses the T4 GPU; fall back to "cpu" if no GPU runtime
model = WhisperModel(
    "large-v2",
    device="cuda",
    compute_type="float16",   # float16 is optimal on T4 GPU
    download_root=WHISPER_CACHE
)
# First run: ~3 GB download to Drive. Subsequent sessions: loads from Drive in ~10 s.
```

---

#### Zip and download results

After a session produces outputs, you usually want to get them off Colab before the VM dies. Two strategies: save to Drive (above) or download directly to your browser.

**Create a dated zip of all outputs:**
```python
import zipfile, os, datetime

TIMESTAMP = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
ZIP_NAME  = f"learn-better-results-{TIMESTAMP}.zip"
ZIP_PATH  = f"/content/{ZIP_NAME}"

# What to include — mirrors the data/ layout in lib/paths.py
DATA_LOCAL = "/content/learn-better/data"
SOURCES = [
    (DATA_LOCAL,    "data"),          # all local outputs (audio, transcripts, generated_transcripts, …)
    (DRIVE_PROJECT, "drive-backup"),  # anything already synced to Drive
]

with zipfile.ZipFile(ZIP_PATH, "w", zipfile.ZIP_DEFLATED) as zf:
    for src_dir, arc_name in SOURCES:
        if not os.path.isdir(src_dir):
            continue
        for root, dirs, files in os.walk(src_dir):
            for fname in files:
                full = os.path.join(root, fname)
                # Archive path: arc_name/relative/path/to/file
                rel  = os.path.relpath(full, src_dir)
                zf.write(full, os.path.join(arc_name, rel))
                print(f"  + {arc_name}/{rel}")

print(f"\n✅ Zip created: {ZIP_PATH}  ({os.path.getsize(ZIP_PATH)/1024/1024:.1f} MB)")
```

**Option A — save zip to Google Drive:**
```python
import shutil
DRIVE_ZIP = f"{DRIVE_PROJECT}/{ZIP_NAME}"
shutil.copy(ZIP_PATH, DRIVE_ZIP)
print(f"Saved to Drive: {DRIVE_ZIP}")
```

**Option B — download zip directly to your browser:**
```python
from google.colab import files
files.download(ZIP_PATH)
# Browser will prompt you to save the file — works up to a few hundred MB.
# For larger files, use Drive (Option A) and download from drive.google.com.
```

**Option C — both (belt and suspenders):**
```python
# Save to Drive first (reliable), then also trigger browser download
shutil.copy(ZIP_PATH, DRIVE_ZIP)
files.download(ZIP_PATH)
```

---

#### Session management tips

- **Re-running after disconnect:** Re-run Cell 1 (clone check + ffmpeg) and Cell 2 (pip install). The Drive mount and Whisper cache cells also need re-running, but they complete in seconds thanks to caching.
- **Avoid accidental disconnects:** Colab disconnects tabs left idle for ~90 min. If running a long Whisper job, keep the tab visible or use Colab Pro's background execution.
- **Runtime type:** Go to Runtime → Change runtime type to switch between CPU and T4 GPU. Changing runtime type resets the VM — you lose all local files. Always push to Drive before switching.
- **Colab Pro / Pro+:** If you use this heavily, Colab Pro ($10/month) gives priority GPU access, longer sessions (24 h+), and background execution. Not necessary for occasional use.

**Pros (updated summary):**
- Free T4 GPU — `large-v2` Whisper runs in minutes
- No local setup
- ffmpeg one-liner cell
- Google Drive gives durable storage + zip workflow for archiving
- Full GitHub integration (clone, pull, push with PAT, `gh` CLI)
- Familiar Jupyter notebook interface

**Cons (updated summary):**
- Ephemeral VM — must re-run setup cells every session (~2–3 min)
- Random disconnects on free tier; no background execution
- 🐧 Linux only — `scripts/*.bat` runners don't work inside containers; use `./scripts/*.sh` or Python directly
- Large yt-dlp downloads may be throttled
- Google account required; Drive storage counts against your 15 GB free quota

---

### GitHub Codespaces ☁️

GitHub Codespaces gives you a full VS Code environment in the browser backed by a 🐧 Linux VM. The repo already has a `.devcontainer/` configuration, so setup is nearly one-click — once the ffmpeg gap is fixed.

**Free tier:** 60 core-hours/month (= 30 h on the free 2-core machine). 15 GB persistent storage. Codespaces pause after 30 min idle; deleted after 30 days of inactivity.

**Required fix before using (commit to repo):**

Add to `.devcontainer/Dockerfile`:
```dockerfile
RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg \
    && rm -rf /var/lib/apt/lists/*
```

Remove the unnecessary `azure-cli` feature from `devcontainer.json` (saves ~200 MB + build time).

**Minimal working guidance:**

1. Push the Dockerfile fix to the repo
2. On GitHub, click **Code → Codespaces → Create codespace on main**
3. Wait ~3 min for the container to build (first time; cached afterwards)
4. VS Code opens in browser with the full environment ready
5. Terminal: `ffmpeg -version`, `python -c "import yt_dlp, faster_whisper; print('OK')"`
6. Run scripts: `python code/transcribe.py --config data/config.json`
7. Jupyter: open any `.ipynb` or run `jupyter notebook --no-browser --port=8888` (auto-forwarded)

> 🐧 **Inside the container:** use `./scripts/*.sh` runners (e.g. `./scripts/r.sh`) or call `python code/SCRIPT.py` directly. The `scripts/*.bat` files won't run inside the Linux container.

**Saving Whisper model weights across rebuilds:**
```json
// Add to devcontainer.json:
"mounts": ["source=whisper-model-cache,target=/home/vscode/.cache/huggingface,type=volume"]
```
This attaches a persistent Docker volume to the HuggingFace cache — weights survive container rebuilds.

**Pros:**
- Full VS Code in browser — debugger, Jupyter, extensions, terminal
- Persistent storage per codespace — files survive between sessions (unlike Colab)
- Exactly the same devcontainer as local VS Code — zero divergence between team members
- Port 8000 forwarded; port 8888 easily added
- Native GitHub integration — git, PRs, Actions all native
- Scales to 4/8-core machines (paid)

**Cons:**
- 60 core-hours/month can run out quickly if used daily
- No GPU (CPU-only Whisper — small/medium models practical, large-v2 slow)
- 🐧 Linux inside — use `./scripts/*.sh` runners or Python directly
- Cold start after image rebuild: 3–5 min
- Codespace storage counts against GitHub account limits

---

### Gitpod ☁️

Gitpod is a GitHub Codespaces alternative with 50 h/month free. Also supports `devcontainer.json` (since 2023), so the same Dockerfile fix applies.

**Free tier:** 50 h/month. Workspaces auto-pause after 30 min; deleted after 14 days of inactivity.

**Option A — use existing devcontainer (simplest):** With the ffmpeg fix committed, open:
```
https://gitpod.io/#https://github.com/YOUR_USER/learn-better
```

**Option B — native `.gitpod.yml`:** See Image Scripts section below for the full files.

**Pros:** Similar to Codespaces. Works with GitHub, GitLab, and Bitbucket.
**Cons:** 50 h/mo, less GitHub ecosystem integration, separate account.

---

### Replit ☁️ — Not recommended

Replit's free-tier network restrictions throttle outbound HTTP connections in ways that break yt-dlp's YouTube download flow unpredictably. Free instances also cap RAM at 512 MB — far below the ~2 GB `faster-whisper` needs. Use Gitpod or Codespaces instead.

---

### Binder ☁️ — Not recommended

2 GB RAM cap, 6 h session maximum, 20 min build time, no GPU, no persistent storage. Technically possible for transcript-fetch-only demos (add `apt.txt` with `ffmpeg`), but not a viable deployment option for real use.


---

## Part 4 — Image Scripts

Image scripts are ready-to-paste files that do the full environment setup in one command. Copy, adjust the one or two variables at the top, and run.

---

### Conda environment script (🪟 🐧 🍎 — recommended)

`setup_conda.sh` / `setup_conda.bat` — works on all OS; `conda` handles ffmpeg automatically.

**🐧 Linux / 🍎 macOS — `setup_conda.sh`:**
```bash
#!/usr/bin/env bash
set -euo pipefail

ENV_NAME="learn-better"
PYTHON_VERSION="3.12"

echo "=== learn-better: conda setup ==="

# 1. Create env if it doesn't exist
if ! conda info --envs | grep -qw "$ENV_NAME"; then
    echo "Creating conda env '$ENV_NAME' (Python $PYTHON_VERSION)..."
    conda create -y -n "$ENV_NAME" python="$PYTHON_VERSION" ffmpeg
else
    echo "Env '$ENV_NAME' already exists — skipping create"
    conda install -y -n "$ENV_NAME" ffmpeg  # ensure ffmpeg is present
fi

# 2. Install pip deps
conda run -n "$ENV_NAME" pip install -r requirements.txt

echo ""
echo "✅ Done. Activate with:"
echo "   conda activate $ENV_NAME"
echo "   python code/transcribe.py --help"
```

**🪟 Windows — `setup_conda.bat`:**
```bat
@echo off
setlocal
set ENV_NAME=learn-better
set PYTHON_VERSION=3.12

echo === learn-better: conda setup ===

conda info --envs | findstr /C:"%ENV_NAME%" >nul 2>&1
if errorlevel 1 (
    echo Creating conda env '%ENV_NAME%' ...
    conda create -y -n %ENV_NAME% python=%PYTHON_VERSION% ffmpeg
) else (
    echo Env '%ENV_NAME%' already exists
    conda install -y -n %ENV_NAME% ffmpeg
)

conda run -n %ENV_NAME% pip install -r requirements.txt

echo.
echo Done. Activate with:
echo   conda activate %ENV_NAME%
endlocal
```

---

### pip + venv setup script

No conda required. You must install ffmpeg separately (conda is easier).

**🐧 Linux / 🍎 macOS — `setup_venv.sh`:**
```bash
#!/usr/bin/env bash
set -euo pipefail

PYTHON="${PYTHON:-python3.12}"  # override: PYTHON=python3.11 ./setup_venv.sh

# 1. Install ffmpeg (skip if already installed)
if ! command -v ffmpeg &>/dev/null; then
    echo "Installing ffmpeg..."
    if command -v apt-get &>/dev/null; then
        sudo apt-get update && sudo apt-get install -y ffmpeg
    elif command -v brew &>/dev/null; then
        brew install ffmpeg
    else
        echo "ERROR: cannot detect package manager. Install ffmpeg manually." && exit 1
    fi
fi

# 2. Create venv
if [ ! -d ".venv" ]; then
    "$PYTHON" -m venv .venv
fi
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "✅ Done. Activate with:"
echo "   source .venv/bin/activate"
```

**🪟 Windows — `setup_venv.bat`:**
```bat
@echo off
setlocal

rem Check ffmpeg
where ffmpeg >nul 2>&1
if errorlevel 1 (
    echo ffmpeg not found. Installing via winget...
    winget install Gyan.FFmpeg --silent
    if errorlevel 1 (
        echo winget failed. Try: choco install ffmpeg
        exit /b 1
    )
)

rem Create venv
if not exist ".venv" (
    py -3.12 -m venv .venv
)
call .venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt

echo.
echo Done. Activate with: .venv\Scripts\activate
endlocal
```

---

### Docker image script — `docker_build_run.sh` / `.bat`

Builds the container image and launches an interactive session with the data folder mounted.

Prerequisite: fix the Dockerfile gap first (see Part 2). The build will fail without ffmpeg.

**🐧 Linux / 🍎 macOS — `docker_build_run.sh`:**
```bash
#!/usr/bin/env bash
set -euo pipefail

IMAGE="learn-better"
DATA_DIR="${1:-$(pwd)/data}"   # pass custom data path as first arg

docker build -t "$IMAGE" .
docker run -it --rm \
    -v "$DATA_DIR:/app/data" \
    -v "whisper-model-cache:/root/.cache/huggingface" \
    "$IMAGE" bash
```

**🪟 Windows — `docker_build_run.bat`:**
```bat
@echo off
set IMAGE=learn-better
if "%~1"=="" (set DATA_DIR=%CD%\data) else (set DATA_DIR=%~1)

docker build -t %IMAGE% .
docker run -it --rm ^
    -v "%DATA_DIR%:/app/data" ^
    -v "whisper-model-cache:/root/.cache/huggingface" ^
    %IMAGE% bash
```

> **🪟 PowerShell alternative:**
> ```powershell
> $IMAGE = "learn-better"
> $DATA  = "$PWD\data"
> docker build -t $IMAGE .
> docker run -it --rm -v "${DATA}:/app/data" -v "whisper-model-cache:/root/.cache/huggingface" $IMAGE bash
> ```

---

### Dockerfile patch (add to `.devcontainer/Dockerfile`)

Current file is missing ffmpeg. Add these lines after the `FROM` line:

```dockerfile
ARG VARIANT="3.12-bullseye"
FROM mcr.microsoft.com/vscode/devcontainers/python:0-${VARIANT}

# ── System deps ──────────────────────────────────────────────────────────────
RUN apt-get update && apt-get install -y --no-install-recommends \
        ffmpeg \
        curl \
    && rm -rf /var/lib/apt/lists/*

# ── Python deps ──────────────────────────────────────────────────────────────
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt
```

---

### `devcontainer.json` — lean version

Remove the `azure-cli` feature (saves ~200 MB + build time). Add model-cache volume.

```json
{
    "name": "learn-better",
    "build": {
        "dockerfile": "Dockerfile",
        "args": { "VARIANT": "3.12-bullseye" }
    },
    "forwardPorts": [8000, 8888],
    "mounts": [
        "source=whisper-model-cache,target=/home/vscode/.cache/huggingface,type=volume"
    ],
    "customizations": {
        "vscode": {
            "extensions": [
                "ms-python.python",
                "ms-toolsai.jupyter"
            ]
        }
    },
    "remoteUser": "vscode"
}
```

---

### Google Colab setup notebook — `colab_setup.ipynb` skeleton

Save this as a notebook in the repo. Students can open it with "Open in Colab" badge.

```python
# Cell 1 — System + repo
import os
!apt-get install -y ffmpeg -q
REPO = "https://github.com/YOUR_USER/learn-better.git"
if not os.path.exists("/content/learn-better"):
    !git clone {REPO} /content/learn-better
%cd /content/learn-better

# Cell 2 — Python deps
!pip install -q -r requirements.txt

# Cell 3 — Mount Drive + set up output dirs
from google.colab import drive
drive.mount('/content/drive')
DRIVE_OUT = "/content/drive/MyDrive/learn-better-output"
# Subdirs mirror lib/paths.py: audio, transcripts, generated_transcripts, summaries, tts_output, wordclouds
for sub in ["audio", "audio_reencoded", "transcripts", "generated_transcripts", "summaries", "tts_output", "wordclouds", "whisper-model-cache"]:
    os.makedirs(f"{DRIVE_OUT}/{sub}", exist_ok=True)
print(f"Drive output: {DRIVE_OUT}")

# Cell 4 — Verify
!nvidia-smi | head -3  # check for GPU
!ffmpeg -version | head -1
import yt_dlp, faster_whisper, pandas
print("✅ All imports OK")
```

Add this badge to `README.md`:
```markdown
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/YOUR_USER/learn-better/blob/main/colab_setup.ipynb)
```


---

## Part 5 — Deep Analysis & Ranking

### Master comparison table

| # | Platform | OS runtime | Complexity (1=easy) | Free tier | GPU | Persistent storage | Time to first run | Best for |
|---|----------|-----------|---------------------|-----------|----|-------------------|------------------|----------|
| 1 | **Google Colab** ☁️ | 🐧 Linux | 1 | 12 h session, T4 GPU | ✅ T4 free | ❌ session-only (Drive saves outputs) | ~5 min | Fastest GPU Whisper, one-off transcription |
| 2 | **Conda local** 🪟🐧🍎 | Host OS | 2 | Unlimited | ✅ if CUDA GPU present | ✅ full | ~10 min first install | Daily use, all platforms |
| 3 | **GitHub Codespaces** ☁️ | 🐧 Linux | 2 | 60 core-h/mo | ❌ CPU only | ✅ 15 GB per codespace | ~3 min (cold) | Team/classroom, VS Code power users |
| 4 | **Gitpod** ☁️ | 🐧 Linux | 2 | 50 h/mo | ❌ CPU only | ✅ workspace storage | ~3 min (cold) | Codespaces alternative, multi-VCS |
| 5 | **Docker** 🪟🐧🍎 | 🐧 Linux (inside) | 3 | Unlimited | ✅ 🐧 Linux + NVIDIA only | ✅ via volume mounts | ~5 min build | Reproducible builds, CI, teams |
| 6 | **VS Code devcontainer** 🪟🐧🍎 | 🐧 Linux (inside) | 3 | Unlimited | ✅ 🐧 Linux + NVIDIA only | ✅ full | ~5 min build | IDE-integrated Docker, reproducibility |
| 7 | **Kiro IDE devcontainer** 🪟🐧🍎 | 🐧 Linux (inside) | 3 | Unlimited | ✅ 🐧 Linux + NVIDIA only | ✅ full | ~5 min build | AI-assisted workflows + reproducibility |
| 8 | **pip + venv local** 🪟🐧🍎 | Host OS | 3 | Unlimited | ✅ if CUDA GPU present | ✅ full | ~15 min (ffmpeg friction) | Clean environments without conda |
| 9 | **Podman** 🪟🐧🍎 | 🐧 Linux (inside) | 4 | Unlimited | ✅ 🐧 Linux + NVIDIA only | ✅ via volume mounts | ~5 min build | Rootless, enterprise/security constraints |
| 10 | **uv** 🪟🐧🍎 | Host OS | 3 | Unlimited | ✅ if CUDA GPU present | ✅ full | ~5 min | Speed-first teams, reproducible lockfiles |

---

### Detailed platform analysis

#### Google Colab ☁️

**Ideal scenario:** You need to run Whisper `large-v2` on a 2-hour video and you want results in 20 minutes, not 2 hours. Or you're teaching a class and everyone needs the same environment without any laptop setup.

**Complexity drivers:** Setup cells take 3–5 minutes per session. The `files.download()` / Drive workflow adds steps that don't exist locally. GitHub push requires a PAT — a friction point for beginners.

**Key risk — session loss:** Any code running when Colab disconnects is lost. For long Whisper jobs, write partial results to Drive as you go (per-video, not at the end).

**ffmpeg:** Always available via `!apt-get install -y ffmpeg` — no complications.

**yt-dlp:** Runs fine on Colab's IPs for most videos. Very popular channels may throttle. The `curl_cffi` extra (`yt-dlp[default,curl-cffi]`) helps with TLS fingerprinting — include it in `requirements.txt`.

**Model cache on Drive:** The first session takes 10–15 min to download `large-v2` (3 GB). With the Drive cache pattern, subsequent sessions load in ~30 seconds.

---

#### Conda local 🪟🐧🍎

**Ideal scenario:** You use this project daily and want the fastest iteration cycle. Conda is the cleanest path on Windows because it installs ffmpeg without any OS-level package manager.

**Complexity drivers:** Conda itself (~500 MB to install if not already present). Package solves can be slow; `mamba`/`libmamba` solver helps. The `conda run` pattern avoids activation issues in scripts.

**Key advantage:** Same `conda create` command on all three OS. No platform-specific ffmpeg steps.

**Key risk:** Conda env bloat. Over time, `conda install` can introduce dependency conflicts. Pin the env to `environment.yml` for reproducibility.

---

#### Docker / VS Code devcontainer / Kiro devcontainer 🪟🐧🍎

These three share the same underlying technology. The differences are:

- **Plain Docker:** CLI-only; you run `docker build` and `docker run` yourself. Most flexible. Full GPU support on 🐧 Linux + NVIDIA.
- **VS Code devcontainer:** Docker managed by VS Code. Adds IDE integration (debugger, Jupyter, extensions). Works on 🪟🐧🍎, but GPU passthrough only works on 🐧 Linux host.
- **Kiro devcontainer:** Same devcontainer spec, adds AI-assisted coding. Same OS/GPU constraints.

**Critical Dockerfile gap:** The current `.devcontainer/Dockerfile` has only 2 lines and does NOT install ffmpeg. You must patch it before any container-based workflow works (see Part 4). This is not obvious and is the #1 failure point for new users.

**Volume mounts — OS differences:**

| Host OS | Docker cmd syntax | PowerShell |
|---------|------------------|-----------|
| 🪟 Windows (cmd) | `-v "%CD%\data:/app/data"` | `-v "${PWD}\data:/app/data"` |
| 🐧 Linux / 🍎 macOS | `-v "$(pwd)/data:/app/data"` | — |

**GPU passthrough — only on 🐧 Linux:**
```bash
# 🐧 Linux only — requires NVIDIA Container Toolkit
docker run --gpus all learn-better
```
On 🪟 Windows and 🍎 macOS, GPU passthrough is not available (Docker runs inside a Linux VM, and the NVIDIA toolkit doesn't bridge through). CPU-only Whisper still works but is slow for large models.

---

#### Podman 🪟🐧🍎

Podman is Docker-compatible (same CLI syntax) but rootless — no daemon running as root. Required in some enterprise environments.

**🪟 Windows caveat:** Podman on Windows requires WSL2. Volume paths in `podman run -v` must use Linux format even from a Windows shell:
```cmd
podman run -it --rm -v /mnt/c/Users/YOU/data:/app/data learn-better bash
```
(not `C:\Users\...`). This confuses Windows users.

**Build compatibility:** `podman build` understands the same `Dockerfile` syntax as Docker. Same ffmpeg gap applies — patch it first.

---

#### pip + venv local 🪟🐧🍎

**Ideal scenario:** You explicitly don't want conda and are comfortable installing system packages manually.

**OS-specific ffmpeg steps** are the main complexity driver (see Part 1). Once ffmpeg is installed, `pip install -r requirements.txt` is identical on all platforms.

**Python version management:** On 🪟 Windows, the `py` launcher (`py -3.12 -m venv .venv`) is the most reliable way to select a specific Python version. On 🐧 Linux / 🍎 macOS, use `python3.12 -m venv .venv` — but you must first install Python 3.12 (`sudo apt install python3.12`, `brew install python@3.12`).

---

#### uv 🪟🐧🍎

`uv` is a modern package installer (written in Rust by Astral) that is 10–100× faster than pip for installs. It supports `pip`-compatible requirements files.

**Install:**
```cmd
:: 🪟 Windows (PowerShell or cmd with winget)
winget install astral-sh.uv
```
```bash
# 🐧 Linux / 🍎 macOS
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Use:**
```bash
uv venv .venv --python 3.12
source .venv/bin/activate    # 🐧🍎
# .venv\Scripts\activate     # 🪟 Windows

uv pip install -r requirements.txt  # ~5–10× faster than pip
```

**Lockfile workflow (reproducible across machines):**
```bash
# Generate a lockfile from requirements.txt
uv pip compile requirements.txt -o requirements.lock.txt
# Install exactly what's in the lockfile
uv pip sync requirements.lock.txt
```

**ffmpeg:** uv is a Python tool only — you still need to install ffmpeg via the OS package manager (see Part 1). uv doesn't solve the ffmpeg problem.

---

### Capability summary by use case

| Use case | Best option |
|----------|-------------|
| Fastest Whisper transcription (free) | Google Colab (T4 GPU) |
| Daily local use, all OS | Conda local |
| Classroom / zero-setup for students | Google Colab + Colab setup notebook |
| Team, consistent environment, VS Code | VS Code devcontainer (+ ffmpeg fix) |
| CI / automated pipelines | Docker |
| Enterprise / rootless requirement | Podman |
| Fastest pip install, lockfiles | uv |
| Browser-based VS Code, 60 h/mo free | GitHub Codespaces (+ ffmpeg fix) |

---

### Known gotchas and fixes

| Problem | OS | Fix |
|---------|----|-----|
| `ffmpeg: command not found` | All | Install ffmpeg via package manager (see Part 1) — it's a system binary, not pip-installable |
| `No module named 'curl_cffi'` | All | `pip install "yt-dlp[default,curl-cffi]"` — required for YouTube bot-detection bypass |
| Container starts but ffmpeg missing | 🪟🐧🍎 | Patch `.devcontainer/Dockerfile` — add `apt-get install -y ffmpeg` (see Part 4) |
| `%CD%` not working in Docker cmd | 🪟 | Use `%CD%` in cmd; `${PWD}` in PowerShell; `$(pwd)` in bash |
| Podman volume path error | 🪟 | Use Linux path format in WSL2: `/mnt/c/Users/...` not `C:\Users\...` |
| GPU not detected in container | 🪟🍎 | GPU passthrough not available on Windows/macOS Docker — 🐧 Linux only |
| Colab session lost mid-run | ☁️ | Write per-video results to Drive as they complete; don't batch at the end |
| Whisper re-downloads model every Colab session | ☁️ | Set `download_root` to a Drive path (see Part 3) |
| `devcontainer` build takes 5+ min | ☁️🪟🐧🍎 | Remove `azure-cli` feature from `devcontainer.json` — saves ~200 MB |
| conda solve is very slow | 🪟🐧🍎 | `conda config --set solver libmamba` — switch to the fast solver |


# How to deploy — learn-better

> **What "deploy" means here:** Reproducibly setting up the Python environment so `code/`, the `lib/` modules, and all helper scripts run correctly on a target machine. This project is not published as a PyPI package — there is no `pyproject.toml`/`setup.py` — so deployment means cloning the repo and wiring up the right Python + ffmpeg environment. The choice of *where* to run it (your laptop, a cloud VM, a container) is the main decision this document helps you make.

---

## Master ranking — complexity vs. capabilities

Lower complexity = faster to get running from zero. Capabilities = how much of the full feature set you get (ffmpeg, Whisper, yt-dlp, notebooks, .bat helpers, persistent storage).

| # | Platform | Complexity | Capabilities | GPU | Persistent | Cost | Best for |
|---|----------|-----------|--------------|-----|------------|------|----------|
| 1 | **Google Colab** | ⭐ | ★★★★☆ | ✅ T4 free | ❌ re-setup each session | Free | One-off Whisper transcription, GPU speed |
| 2 | **GitHub Codespaces** | ⭐⭐ | ★★★★★ | ❌ | ✅ per-codespace | 60 core-h/mo free | Remote VS Code, full Linux, no local install |
| 3 | **Local — conda** | ⭐⭐ | ★★★★★ | ❌ CPU | ✅ | Free | Day-to-day, matches .bat helpers |
| 4 | **Local — pip + venv** | ⭐⭐ | ★★★★☆ | ❌ CPU | ✅ | Free | Minimal tooling, simple |
| 5 | **Local — uv** | ⭐⭐ | ★★★★☆ | ❌ CPU | ✅ | Free | Fast rebuilds, lockfile reproducibility |
| 6 | **VS Code Dev Container** | ⭐⭐⭐ | ★★★★★ | ❌ | ✅ | Free (Docker req.) | Consistent team env, local Docker |
| 7 | **Kiro IDE Dev Container** | ⭐⭐⭐ | ★★★★★ | ❌ | ✅ | Free (Docker req.) | Same as VS Code + Kiro AI features |
| 8 | **Gitpod** | ⭐⭐⭐ | ★★★★☆ | ❌ | ✅ workspace | 50 h/mo free | Alternative to Codespaces |
| 9 | **Replit** | ⭐⭐⭐ | ★★☆☆☆ | ❌ | ✅ | Free tier limited | **Not recommended** — network blocks yt-dlp |
| 10 | **Docker** | ⭐⭐⭐⭐ | ★★★★★ | ❌ | ✅ volume | Free (Docker req.) | CI, reproducible builds, server deploy |
| 11 | **Podman** | ⭐⭐⭐⭐ | ★★★★★ | ❌ | ✅ volume | Free | Rootless/daemonless Docker alternative |
| 12 | **Binder** | ⭐ | ★☆☆☆☆ | ❌ | ❌ | Free | **Not recommended** — 2 GB RAM, ephemeral |

> **Key constraint across all platforms:** `ffmpeg` is a system binary — `pip` and `uv` cannot install it. Every non-conda platform requires an explicit system-level ffmpeg install step. This is the #1 source of setup failures.

---

## Part 1 — Local Installation

Three methods for running directly on your machine. All produce identical functionality; they differ in how much setup burden they put on you versus the tooling.

### Method 1 — conda (recommended)

Conda manages Python *and* system binaries inside the same environment. It is the **only** method that installs `ffmpeg` automatically, and it matches what all `.bat` helpers in the repo assume.

**Prerequisites:** [Miniconda](https://docs.conda.io/en/latest/miniconda.html) or Anaconda installed.

```cmd
conda create -n learn-better python=3.12 -y
conda activate learn-better
conda install -c conda-forge ffmpeg -y
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Verify:

```cmd
python --version
ffmpeg -version
python -c "import yt_dlp, faster_whisper, pandas; print('OK')"
```

**Pros:**
- ffmpeg installed inside the conda env — no separate manual step, no PATH confusion
- Environment name `learn-better` matches all `.bat` files exactly
- Reproducible across Windows / macOS / Linux without platform-specific branching

**Cons:**
- Conda's dependency solver is slow (3–10 min on first `create`)
- Requires Miniconda/Anaconda if not already present (150–500 MB installer)
- Mixing conda and pip within the same env is safe here but is a code smell some teams avoid

---

### Method 2 — pip + venv

The standard library approach. No extra tooling beyond Python 3.12.

**Prerequisites:** Python 3.12 from [python.org](https://python.org) or `winget install Python.Python.3.12`.

```cmd
py -3.12 -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Install ffmpeg separately:

```cmd
winget install ffmpeg          # Windows 10/11
choco install ffmpeg           # Chocolatey
brew install ffmpeg            # macOS
sudo apt-get install -y ffmpeg # Debian/Ubuntu
```

Verify: `python --version`, `ffmpeg -version`, import check above.

**Pros:**
- Zero extra tooling — `venv` ships with Python
- Fast pip solver compared to conda
- Universally understood by any Python developer

**Cons:**
- ffmpeg is a manual step — easy to forget, PATH changes need a fresh terminal/reboot
- No lockfile by default — sub-dependency versions can drift over time
- `.bat` helpers assume conda `learn-better` env; need adaptation

---

### Method 3 — uv (fastest)

[uv](https://docs.astral.sh/uv/) is a Rust-based drop-in for pip + venv + pip-tools. Ideal for CI, Codespaces, or frequent rebuilds.

Install uv once:

```cmd
winget install --id=astral-sh.uv -e         # Windows
curl -LsSf https://astral.sh/uv/install.sh | sh  # macOS/Linux
```

Set up the environment:

```cmd
uv venv --python 3.12
.venv\Scripts\activate          # Windows
source .venv/bin/activate        # macOS/Linux
uv pip install -r requirements.txt
```

Optional fully-locked install:

```cmd
uv pip compile requirements.txt -o requirements.lock.txt
uv pip sync requirements.lock.txt
```

ffmpeg: same manual step as pip + venv above.

**Pros:**
- Noticeably faster than pip — parallel Rust resolver + global package cache
- `uv pip compile` + `uv pip sync` gives a full lockfile (exact sub-dependency versions)
- Drop-in replacement: all pip commands work with `uv pip` prefix

**Cons:**
- uv must be installed first (trivial, but one extra step)
- ffmpeg still a manual step
- `.bat` helpers need same adaptation as pip + venv

---

### Local comparison table

| Criterion | pip + venv | conda | uv |
|---|---|---|---|
| Handles ffmpeg in-environment | ❌ manual | ✅ automatic | ❌ manual |
| Python dep reproducibility | Good (pinned ranges) | Good | **Best** (lockfile) |
| Setup speed | Medium | Slowest | **Fastest** |
| Matches existing `.bat` files | Partial | ✅ Yes | Partial |
| Extra tooling to install | None | Miniconda | uv |
| "Works on my machine" risk | Medium (ffmpeg) | **Lowest** | Medium (ffmpeg) |

**Recommendation:** Use **conda** for day-to-day local work (ffmpeg handled, `.bat` files just work). Use **uv** in CI or when rebuilding frequently. Use **pip + venv** only if you need zero extra tooling and are comfortable with the manual ffmpeg step.


---

## Part 2 — Containerised (self-hosted)

These options run the project inside a container on your local machine, combining reproducibility with full local performance. Docker must be installed (Docker Desktop on Windows/macOS; Docker Engine on Linux; or Rancher Desktop as a free alternative to Docker Desktop).

> **Important:** The existing `.devcontainer/Dockerfile` in this repo has a **confirmed gap** — it does not install `ffmpeg`. All container-based options below include the fix.

---

### VS Code Dev Container

The repo already ships a `.devcontainer/` configuration. With the ffmpeg gap fixed, this is the smoothest team-onboarding experience: clone the repo, open in VS Code, click "Reopen in Container", and the full environment builds automatically.

**Prerequisites:** [Docker Desktop](https://www.docker.com/products/docker-desktop/) (or Rancher Desktop), VS Code with the [Dev Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers).

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

# Install system dependencies missing from the base image
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*
```

Also consider removing the unnecessary `azure-cli` feature from `devcontainer.json`:
```json
// Remove or comment out:
// "features": { "azure-cli": "latest" }
```

**Minimal working guidance:**

1. Open the cloned repo folder in VS Code
2. When prompted "Reopen in Container", click it (or use Command Palette → "Dev Containers: Reopen in Container")
3. Wait for the container to build (2–5 min first time, cached on subsequent opens)
4. The terminal opens inside the container — `ffmpeg -version` and Python imports work immediately
5. Jupyter notebooks: use the Jupyter extension already installed in the devcontainer

**Pros:**
- One-click environment: everything (Python 3.12, ffmpeg, all pip deps, VS Code extensions) is installed automatically
- Container is isolated — no "polluting" the host machine
- Rebuild is trivial if the environment gets corrupted
- Port 8000 already forwarded in `devcontainer.json`
- Works on Windows, macOS, and Linux identically

**Cons:**
- Requires Docker Desktop (licensed for commercial use — free only for small businesses/students) or Rancher Desktop (always free)
- Cold start after a rebuild: 2–5 min
- `.bat` files won't work inside the Linux container — use equivalent bash commands or run them from the host
- The existing Dockerfile uses Microsoft's devcontainer base image (300+ MB) — heavier than a minimal Python image
- `azure-cli` feature in devcontainer.json is unnecessary bloat (~200 MB)

**Performance notes:** All compute runs on your local machine's CPU. Whisper (via `faster-whisper`) uses int8 quantisation and is CPU-friendly, but large models (medium/large-v2) will be slow without a GPU. For GPU passthrough, Docker GPU support requires NVIDIA Container Toolkit (Linux only, not available in Docker Desktop on Windows/macOS).

---

### Kiro IDE Dev Container

[Kiro](https://kiro.dev) is Amazon's IDE (released 2025), built on VS Code, with native AI agent features (Specs & Hooks). It reads the same `devcontainer.json` spec as VS Code, so the setup is identical.

**Prerequisites:** [Kiro IDE](https://kiro.dev/downloads/), Docker Desktop or Rancher Desktop.

**Minimal working guidance:**

1. Apply the same Dockerfile ffmpeg fix described above
2. Open the repo folder in Kiro
3. Use Command Palette → "Dev Containers: Reopen in Container" (same as VS Code)
4. Same result as VS Code devcontainer

**Pros:**
- Everything from VS Code Dev Container applies
- Additional Kiro "Specs" and "Hooks" can automate repetitive tasks in the project (e.g., auto-summarise new transcripts)
- Native integration with Amazon Q / Bedrock for AI assistance

**Cons:**
- Kiro is newer and less battle-tested than VS Code
- Amazon-specific AI features require AWS credentials for full use
- Same Docker dependency as VS Code devcontainer

---

### Docker (standalone)

Run the project in a fully self-contained Docker image with no dependency on VS Code or any IDE. Useful for scripted batch processing, CI pipelines, or server deployment.

**Prerequisites:** Docker Engine (Linux) or Docker Desktop (Windows/macOS).

**Standalone Dockerfile** (save as `Dockerfile.standalone` in the repo root — see also the Image Scripts section):

```dockerfile
FROM python:3.12-slim-bookworm

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create a non-root user
RUN useradd -m -u 1000 appuser
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Switch to non-root user
USER appuser

# Default: open a shell
CMD ["/bin/bash"]
```

**Build:**
```bash
docker build -f Dockerfile.standalone -t learn-better .
```

**Run interactively (with volume mount for persistent output):**
```bash
# Windows (cmd)
docker run -it --rm \
  -v "%CD%\data:/app/data" \
  -v "%CD%\output:/app/output" \
  learn-better

# macOS / Linux
docker run -it --rm \
  -v "$(pwd)/data:/app/data" \
  -v "$(pwd)/output:/app/output" \
  learn-better
```

**Run a specific script non-interactively:**
```bash
docker run --rm \
  -v "$(pwd)/data:/app/data" \
  learn-better \
  python code/transcribe.py --config data/config.json
```

**Pros:**
- Maximum reproducibility — identical environment on any machine with Docker
- No IDE required
- CI-friendly: works in GitHub Actions, GitLab CI, Jenkins, etc.
- Python image base (`python:3.12-slim-bookworm`) is ~200 MB — lighter than the MS devcontainer base
- Can be pushed to a registry and pulled anywhere

**Cons:**
- All I/O must go through volume mounts — outputs not in the container survive only if mounted
- No GUI / Jupyter by default (can be added with `jupyter notebook --ip=0.0.0.0 --no-browser` + port forward)
- `.bat` files don't work inside the container (Linux only)
- Slower Whisper than Colab (no GPU in standard Docker on Windows/macOS)
- Requires Docker knowledge for day-to-day use

---

### Podman

Podman is a daemonless, rootless container engine compatible with Docker syntax. It runs without a background daemon and without root privileges, making it preferred in security-sensitive environments and Linux servers.

**Prerequisites:** [Podman](https://podman.io/docs/installation) (available via `winget install RedHat.Podman` on Windows, `brew install podman` on macOS, `apt-get install podman` on Debian/Ubuntu).

**Key differences from Docker:**

The same `Dockerfile.standalone` works unchanged. All commands are identical with `podman` substituted for `docker`:

```bash
podman build -f Dockerfile.standalone -t learn-better .
podman run -it --rm \
  -v "$(pwd)/data:/app/data:Z" \
  learn-better
```

> Note: The `:Z` SELinux label suffix is needed on Fedora/RHEL for volume mounts. On other distros, omit it.

**Podman-specific bootstrapper** (`podman_setup.sh` — see Image Scripts section):
```bash
#!/usr/bin/env bash
set -euo pipefail
podman machine init --cpus 4 --memory 4096 --disk-size 40  # macOS/Windows only
podman machine start
podman build -f Dockerfile.standalone -t learn-better .
echo "Ready. Run: podman run -it --rm -v \$(pwd)/data:/app/data learn-better"
```

**Pros:**
- Rootless by default — no daemon running as root
- No Docker Desktop license concerns
- Better security posture for server/production use
- Podman Desktop (free) provides a GUI similar to Docker Desktop
- `podman compose` can replace `docker compose` for multi-container setups

**Cons:**
- Slightly less ecosystem support (some CI systems default to Docker)
- `podman machine` (Windows/macOS) is less mature than Docker Desktop
- Same I/O volume-mount requirement as Docker
- SELinux label quirks on RHEL/Fedora


---

## Part 3 — Cloud / Free Platforms

These platforms let you run the project with zero local setup. The trade-off is always some combination of: limited free hours, ephemeral storage, no `.bat` support (Linux shells only), and potential network restrictions that affect yt-dlp.

---

### Google Colab

Google Colab is a hosted Jupyter environment with free GPU access. It is the fastest path to running Whisper transcriptions with T4 GPU acceleration — which makes large-model transcription 5–10× faster than CPU.

**Free tier:** 12 h session (approximate, varies by load), T4 GPU, ~13 GB RAM, ~78 GB temp disk. No persistent storage unless you mount Google Drive. Sessions reset on disconnect.

**Minimal working guidance:**

Create a new notebook and run these cells in order:

```python
# Cell 1 — Clone repo and install system deps
!git clone https://github.com/YOUR_USER/learn-better.git
%cd learn-better
!apt-get install -y ffmpeg -q
```

```python
# Cell 2 — Install Python dependencies
!pip install -q -r requirements.txt
```

```python
# Cell 3 — (Optional) Mount Google Drive for persistent output
from google.colab import drive
drive.mount('/content/drive')
# Then write outputs to /content/drive/MyDrive/learn-better-output/
```

```python
# Cell 4 — Verify setup
!python --version
!ffmpeg -version
import yt_dlp, faster_whisper, pandas
print("All imports OK")
```

```python
# Cell 5 — Example: run a transcription script
!python code/transcribe.py --url "https://www.youtube.com/watch?v=EXAMPLE"
```

> **Tip for GPU use:** Check GPU is available with `!nvidia-smi`. Whisper's `faster-whisper` will automatically use the GPU when CUDA is detected — no code change needed.

**Pros:**
- Free T4 GPU: large-v2 Whisper model runs in minutes instead of hours
- No setup whatsoever — just open a notebook in any browser
- ffmpeg installed with a single `!apt-get` cell
- Familiar Jupyter interface
- Google Drive integration gives optional persistent storage

**Cons:**
- Sessions are ephemeral — all work (including downloaded model weights) is lost on disconnect
- Must re-run setup cells at the start of every session (~2–3 min per session)
- Random disconnections after ~12 h (free tier) or when Colab reclaims resources
- No `.bat` file support — use Python scripts directly or bash equivalents
- yt-dlp YouTube downloads work but very large downloads may be throttled or fail
- Whisper model weights (1–3 GB for large-v2) re-download every session unless saved to Drive
- Not suitable for long-running unattended pipelines (session will disconnect)

**Optimization:** Save Whisper model weights to Drive to avoid re-downloading each session:
```python
import os
model_cache = "/content/drive/MyDrive/whisper-models"
os.makedirs(model_cache, exist_ok=True)
# faster-whisper respects the cache_dir argument:
from faster_whisper import WhisperModel
model = WhisperModel("large-v2", device="cuda", cache_dir=model_cache)
```

---

### GitHub Codespaces

GitHub Codespaces gives you a full VS Code environment in the browser (or connected to your local VS Code), backed by a Linux VM. The repo already has a `.devcontainer/` configuration, so setup is nearly one-click — once the ffmpeg gap is fixed.

**Free tier:** 60 core-hours/month (= 30 hours on a 2-core machine, the free default). 15 GB persistent storage. Codespaces are paused after 30 min of inactivity and deleted after 30 days of inactivity.

**Required fix before using (commit to repo):**

Add to `.devcontainer/Dockerfile`:
```dockerfile
RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg \
    && rm -rf /var/lib/apt/lists/*
```

Remove unnecessary feature from `.devcontainer/devcontainer.json` (saves ~200 MB and build time):
```json
// Delete this block:
"features": { "azure-cli": "latest" }
```

**Minimal working guidance:**

1. Push the Dockerfile fix above to the repo
2. On GitHub, click **Code → Codespaces → Create codespace on main**
3. Wait ~3 min for the container to build (first time only; subsequent opens use a cached image)
4. VS Code opens in browser with the full environment ready
5. Open a terminal: `ffmpeg -version`, `python -c "import yt_dlp, faster_whisper; print('OK')"` — both work immediately
6. Run scripts: `python code/transcribe.py --config data/config.json`
7. Jupyter: click any `.ipynb` file or run `jupyter notebook --no-browser --port=8888` (port forwarded automatically)

**Pros:**
- Full VS Code in browser — syntax highlighting, Jupyter, debugger, all extensions
- Persistent storage per codespace — files survive between sessions
- Exactly the same devcontainer as local VS Code — zero config divergence between team members
- Port forwarding (port 8000 already configured): run a local web server and access it via browser
- GitHub integration: git operations, PRs, Actions all native
- Scales to 4-core / 8-core machines (paid tier) for heavier Whisper workloads

**Cons:**
- 60 core-hours/month is enough for ~30 h of actual work on 2-core; can run out mid-month if used heavily
- No GPU (CPU-only Whisper — small/medium models practical, large-v2 will be slow)
- `.bat` files don't run on Linux — use Python scripts or create bash equivalents
- Cold start after image rebuild: 3–5 min
- Codespace storage counts against GitHub account limits
- Whisper model weights download on first run (no local caching across codespace rebuilds)

**Saving model weights across rebuilds:** Add to `devcontainer.json`:
```json
"mounts": ["source=whisper-model-cache,target=/home/vscode/.cache/huggingface,type=volume"]
```
This attaches a Docker volume (persistent across rebuilds) to the HuggingFace cache directory.

---

### Gitpod

Gitpod is a GitHub Codespaces alternative. It also reads `devcontainer.json` natively (since Gitpod 2023), so the same Dockerfile fix applies. The main difference is the free tier and the additional `.gitpod.yml` configuration format.

**Free tier:** 50 hours/month (Organization plan), then pay-as-you-go. Workspaces auto-pause after 30 min; deleted after 14 days of inactivity.

**Option A — use existing devcontainer (simplest):**

With the ffmpeg Dockerfile fix committed, Gitpod will use `devcontainer.json` automatically. Just open:
```
https://gitpod.io/#https://github.com/YOUR_USER/learn-better
```

**Option B — native `.gitpod.yml` (more control):**

Create `.gitpod.yml` in the repo root:
```yaml
image:
  file: .gitpod.Dockerfile

tasks:
  - name: Setup
    init: |
      pip install --upgrade pip
      pip install -r requirements.txt
    command: echo "Environment ready"

ports:
  - port: 8888
    visibility: private
    description: Jupyter
```

Create `.gitpod.Dockerfile`:
```dockerfile
FROM gitpod/workspace-python-3.12

# Install system dependencies
RUN sudo apt-get update && sudo apt-get install -y ffmpeg && sudo rm -rf /var/lib/apt/lists/*
```

**Pros:**
- Similar capabilities to GitHub Codespaces
- VS Code in browser or local VS Code with Gitpod extension
- Slightly more flexible workspace configuration via `.gitpod.yml`
- Works with GitHub, GitLab, and Bitbucket repos (not limited to GitHub)

**Cons:**
- 50 h/month — slightly less than Codespaces 60 core-hours if using 2-core
- Less integrated with GitHub ecosystem
- Requires a Gitpod account separate from GitHub
- No GPU on free tier
- Same `.bat` incompatibility (Linux shell)

---

### Replit

Replit is a browser-based IDE with Nix package management. While it can technically run this project, it is **not recommended** as a primary platform due to significant limitations.

**Why Replit is problematic for this project:**

1. **Network restrictions on free tier:** yt-dlp requires network access to YouTube CDN to download audio. Replit's free-tier sandboxes throttle and restrict outbound HTTP connections in ways that break yt-dlp's download flow unpredictably.
2. **Nix environment is not intuitive:** The `replit.nix` format is different from everything else in this repo's ecosystem.
3. **Memory limits:** Free Replit instances have 512 MB RAM — far less than the ~2 GB that `faster-whisper` needs for even the small Whisper model.

**If you still want to try it (`replit.nix`):**

```nix
{ pkgs }: {
  deps = [
    pkgs.python312
    pkgs.ffmpeg
    pkgs.git
    pkgs.curl
  ];
  env = {
    PYTHON_LD_LIBRARY_PATH = pkgs.lib.makeLibraryPath [
      pkgs.stdenv.cc.cc.lib
    ];
  };
}
```

Then in the Replit shell:
```bash
pip install -r requirements.txt
```

**Verdict:** Use Gitpod or Codespaces instead. Replit's value proposition is interactive coding education, not running data-heavy CLI pipelines against external APIs.

---

### Binder (mybinder.org)

Binder builds a Docker image from your repo and serves a Jupyter environment. Zero login, just a URL with a badge.

**Why Binder is unsuitable for this project:**

1. **2 GB RAM cap** — `faster-whisper` with even the smallest model needs ~1 GB, and yt-dlp + pandas overhead will hit this ceiling
2. **No persistent storage** — sessions die after 10 min of inactivity; all output is lost
3. **20 min build time** (first visit) — impractical for a tool you want to iterate on
4. **No GPU** — Whisper runs on CPU only
5. **Session lifetime** — 6 h maximum even if active

**Technically possible setup** (for very light use — transcript fetching only, no Whisper):

Add `apt.txt` to repo root:
```
ffmpeg
```

Binder will install `ffmpeg` during the image build alongside the `requirements.txt` pip deps. The `apt.txt` mechanism is the only supported way to add system packages on Binder.

**Verdict:** Only viable for demonstrating the transcript-fetch functions (no Whisper) in a throwaway session. Not a deployment option for real use.


---

## Part 4 — Image Scripts

A consolidated collection of all scripts mentioned above, ready to copy into the repo.

---

### `Dockerfile.standalone` — self-contained image (Docker / Podman)

Save at repo root. Uses the official slim Python image instead of the Microsoft devcontainer base — lighter and no IDE tooling bloat.

```dockerfile
# Dockerfile.standalone
# Usage:
#   docker build -f Dockerfile.standalone -t learn-better .
#   docker run -it --rm -v "$(pwd)/data:/app/data" learn-better
FROM python:3.12-slim-bookworm

LABEL org.opencontainers.image.description="learn-better: YouTube-to-study-material pipeline"

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Non-root user for security
RUN useradd -m -u 1000 appuser

WORKDIR /app

# Install Python deps before copying full source (layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy project source
COPY . .
RUN chown -R appuser:appuser /app

USER appuser

# Expose a port if needed (e.g. for Jupyter)
EXPOSE 8888

# Default: interactive shell; override at runtime for scripts
CMD ["/bin/bash"]
```

---

### `.devcontainer/Dockerfile` — patched devcontainer image

This replaces the existing 2-line Dockerfile. Add this to the repo to fix the ffmpeg gap for both VS Code Dev Containers and Codespaces.

```dockerfile
# .devcontainer/Dockerfile
ARG VARIANT="3.12-bullseye"
FROM mcr.microsoft.com/vscode/devcontainers/python:0-${VARIANT}

# Fix: install ffmpeg (missing from original devcontainer)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Optional: install uv for fast dependency management in devcontainer
RUN pip install --no-cache-dir uv
```

And the matching `devcontainer.json` (cleaned up — azure-cli removed):

```json
{
  "name": "learn-better",
  "forwardPorts": [8000, 8888],
  "build": {
    "dockerfile": "Dockerfile",
    "context": "..",
    "args": {
      "VARIANT": "3.12-bullseye",
      "NODE_VERSION": "none"
    }
  },
  "customizations": {
    "vscode": {
      "settings": {
        "python.defaultInterpreterPath": "/usr/local/bin/python",
        "[python]": {
          "editor.defaultFormatter": "ms-python.black-formatter"
        }
      },
      "extensions": [
        "ms-python.python",
        "ms-python.vscode-pylance",
        "ms-python.black-formatter",
        "ms-toolsai.jupyter"
      ]
    }
  },
  "postCreateCommand": "pip3 install --upgrade pip && pip3 install -r requirements.txt",
  "remoteUser": "vscode",
  "mounts": [
    "source=whisper-model-cache,target=/home/vscode/.cache/huggingface,type=volume"
  ]
}
```

> The `mounts` entry adds a persistent Docker volume for Whisper model weights — they survive container rebuilds and don't need to be re-downloaded each time.

---

### `colab_setup.py` — Google Colab bootstrap cells

Save as `colab_setup.py` at repo root (or paste directly into Colab cells). This is the minimal Colab setup script.

```python
# colab_setup.py
# Paste these blocks as separate Colab cells, or run as a script.
# Designed to be idempotent — safe to re-run.

import subprocess, sys, os

def run(cmd):
    """Run a shell command, printing output live."""
    result = subprocess.run(cmd, shell=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"Command failed: {cmd}")

# 1. Install system deps
print("==> Installing ffmpeg...")
run("apt-get install -y ffmpeg -q")

# 2. Clone repo (if not already present)
if not os.path.exists("learn-better"):
    print("==> Cloning repo...")
    run("git clone https://github.com/YOUR_USER/learn-better.git")
os.chdir("learn-better")

# 3. Install Python deps
print("==> Installing Python dependencies...")
run(f"{sys.executable} -m pip install -q -r requirements.txt")

# 4. Optional: mount Google Drive for persistent storage
# from google.colab import drive
# drive.mount('/content/drive')

# 5. Verify
print("==> Verifying setup...")
run("ffmpeg -version")
run(f"{sys.executable} -c \"import yt_dlp, faster_whisper, pandas; print('All imports OK')\"")
print("\n✅ Colab setup complete. Run scripts with: python code/SCRIPT_NAME.py")
```

---

### `setup_codespaces.sh` — Codespaces post-create helper

An alternative to the inline `postCreateCommand` — useful if your post-create logic grows:

```bash
#!/usr/bin/env bash
# setup_codespaces.sh
# Called by devcontainer.json postCreateCommand if you change it to:
#   "postCreateCommand": "bash .devcontainer/setup_codespaces.sh"
set -euo pipefail

echo "==> Upgrading pip..."
pip3 install --upgrade pip

echo "==> Installing Python dependencies..."
pip3 install -r requirements.txt

echo "==> Verifying ffmpeg..."
ffmpeg -version || echo "WARNING: ffmpeg not found — check Dockerfile"

echo "==> Verifying Python imports..."
python3 -c "import yt_dlp, faster_whisper, pandas; print('All imports OK')"

echo "==> Setup complete."
```

---

### `podman_setup.sh` — Podman first-run bootstrapper (macOS/Windows)

```bash
#!/usr/bin/env bash
# podman_setup.sh — run once to initialize Podman machine and build the image
# macOS and Windows only (Linux Podman doesn't need a VM)
set -euo pipefail

if [[ "$(uname)" != "Linux" ]]; then
    echo "==> Initializing Podman machine..."
    podman machine init --cpus 4 --memory 4096 --disk-size 40 || true
    podman machine start || true
fi

echo "==> Building learn-better image..."
podman build -f Dockerfile.standalone -t learn-better .

echo ""
echo "==> Done. Run the container with:"
echo "    podman run -it --rm -v \$(pwd)/data:/app/data learn-better"
```

---

### `.gitpod.yml` and `.gitpod.Dockerfile` — Gitpod config

`.gitpod.yml`:
```yaml
# .gitpod.yml
image:
  file: .gitpod.Dockerfile

tasks:
  - name: Setup environment
    init: |
      pip install --upgrade pip
      pip install -r requirements.txt
      echo "Setup complete"
    command: |
      echo "Environment ready. Python: $(python --version), ffmpeg: $(ffmpeg -version | head -1)"

ports:
  - port: 8888
    visibility: private
    description: Jupyter Notebook
  - port: 8000
    visibility: private
    description: Dev server

vscode:
  extensions:
    - ms-python.python
    - ms-toolsai.jupyter
    - ms-python.black-formatter
```

`.gitpod.Dockerfile`:
```dockerfile
# .gitpod.Dockerfile
FROM gitpod/workspace-python-3.12

# Install system dependencies
RUN sudo apt-get update \
    && sudo apt-get install -y --no-install-recommends ffmpeg \
    && sudo rm -rf /var/lib/apt/lists/*
```

---

### `apt.txt` — Binder system package declaration

For Binder only (place at repo root alongside `requirements.txt`):
```
ffmpeg
```

Binder reads `apt.txt` during image build and installs each line as a Debian package. This is the only supported way to get system packages on Binder.

---

## Part 5 — Deep Analysis: pros, cons, and fit for this project

| Platform | Setup time (first) | Persistent? | GPU | ffmpeg | yt-dlp works? | Whisper speed | .bat support | Free limits | Recommended for |
|---|---|---|---|---|---|---|---|---|---|
| **Local conda** | 10–20 min | ✅ always | ❌ CPU | ✅ auto | ✅ | Medium (CPU int8) | ✅ Yes | None | Day-to-day, team standard |
| **Local pip/uv** | 5–10 min | ✅ always | ❌ CPU | ⚠️ manual | ✅ | Medium (CPU int8) | ⚠️ adapt | None | Individual devs who know Python tooling |
| **VS Code DevContainer** | 5–15 min | ✅ always | ❌ CPU* | ✅ fix Dockerfile | ✅ | Medium (CPU int8) | ❌ bash equiv | None (Docker) | Teams wanting identical environments |
| **Kiro DevContainer** | 5–15 min | ✅ always | ❌ CPU* | ✅ fix Dockerfile | ✅ | Medium (CPU int8) | ❌ bash equiv | None (Docker) | Teams using Kiro AI features |
| **Docker** | 5–10 min build | ✅ volume | ❌ CPU* | ✅ in image | ✅ | Medium (CPU int8) | ❌ bash equiv | None (Docker) | CI, reproducible batch jobs |
| **Podman** | 5–10 min build | ✅ volume | ❌ CPU* | ✅ in image | ✅ | Medium (CPU int8) | ❌ bash equiv | None | Security-conscious / rootless |
| **GitHub Codespaces** | 3–5 min build | ✅ per-codespace | ❌ CPU | ✅ fix Dockerfile | ✅ | Slow (2-core CPU) | ❌ bash equiv | 60 core-h/mo | Remote work, no local machine |
| **Gitpod** | 3–5 min build | ✅ workspace | ❌ CPU | ✅ gitpod.Dockerfile | ✅ | Slow (CPU) | ❌ bash equiv | 50 h/mo | Alternative to Codespaces |
| **Google Colab** | ~2 min (per session) | ❌ re-setup | ✅ T4 GPU | ✅ `!apt-get` cell | ✅ | **Fast (GPU)** | ❌ Python scripts | 12 h session | One-off GPU transcription |
| **Replit** | 5–10 min | ✅ limited | ❌ | ✅ nix | ⚠️ throttled | Very slow (512 MB) | ❌ | 512 MB RAM | **Not recommended** |
| **Binder** | 15–20 min build | ❌ ephemeral | ❌ | ✅ apt.txt | ⚠️ unreliable | **Too slow** (2 GB) | ❌ | 6 h session | **Not recommended** |

*GPU passthrough available on Linux with NVIDIA Container Toolkit, not on macOS/Windows Docker Desktop.

### Key decision criteria

**"I want it to just work with zero fuss"** → **Google Colab** (accept re-setup each session) or **GitHub Codespaces** (once devcontainer is fixed).

**"I'll use this every day on my own machine"** → **Local conda** (matches the .bat helpers, ffmpeg handled).

**"My whole team needs identical environments"** → **VS Code Dev Container** (everyone gets the same Dockerfile).

**"I need GPU for fast Whisper transcription"** → **Google Colab** (free T4) or local machine with GPU + conda.

**"I want to run this in CI / automate batch jobs"** → **Docker** or **Podman** (reproducible, scriptable, no GUI dependency).

**"I'm away from my machine and need a quick session"** → **GitHub Codespaces** (full VS Code, persistent files, 60 h/mo free).

**"I care about security / rootless"** → **Podman**.


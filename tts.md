# Text-to-Speech (TTS): Free / Self-Hosted Options — Analysis & Plan

Goal: turn generated study material (transcripts, summaries, mind-map notes) into audio, using
mechanisms that are **completely free**, ideally **self-hosted** (own machine) or runnable on
**Google Colab's free tier**. No paid APIs (ElevenLabs, OpenAI TTS, Azure/AWS paid tiers, etc.).

This mirrors Phase C (speech-to-text via `faster-whisper`) but in the opposite direction: text → audio.

---

## 1. Landscape overview

Three broad categories were researched:

1. **Python-based local/open-source model libraries** — run on your own CPU/GPU or free Colab GPU.
2. **"Voicebox"** — two unrelated things share this name; only one is usable.
3. **Gemini Studio / Gemini API** — Google's free tier, with caveats.
4. A bonus category found during research: **edge-tts** — a free cloud wrapper, not a local model,
   but notable enough to include.

### 1.1 Python-based local/open-source options

| Library | License | Cloning? | Approx. resources | Quality (MOS*) | Speed (RTF**) | Colab-friendly | Notes |
|---|---|---|---|---|---|---|---|
| **Piper** | MIT | No | CPU only, tiny | ~3.5 | ~0.008 (very fast) | Yes | `pip install piper-tts`. 30–50+ languages/voices. Actively maintained fork: `OHF-Voice/piper1-gpl`. Best pick if you just want fast, robotic-but-clear, zero-GPU narration. |
| **Kokoro-82M** | Apache-2.0 | No | <1GB VRAM, or CPU | ~4.2 | ~0.03 | Yes (documented Colab tutorial) | `pip install kokoro>=0.8`. 54 voices / 8 languages. Best quality-per-resource ratio of the no-cloning options. |
| **Coqui XTTS v2** (community fork) | CPML (non-commercial) | Yes (3–6s ref) | ~4GB VRAM | ~4.0 | moderate | Yes — public notebook exists (`kubinka0505/colab-notebooks`, `Coqui_XTTS.ipynb`) | `pip install coqui-tts`; needs `COQUI_TOS_AGREED=1` env var for non-interactive license acceptance. Best pick if you want to clone a specific narrator voice. Non-commercial license only — fine for personal study use. |
| **Bark (Suno)** | MIT | Limited | ~6GB VRAM | good but variable | ~0.85 (slow) | Yes | Can add non-speech sounds (laughs, pauses) but slow and less consistent for long-form narration. |
| **Fish Speech** | Apache-2.0 | Yes (10–30s ref) | ~4GB VRAM | ~4.1 | moderate | Yes | 8 languages. Good middle ground: cloning + permissive license. |
| **F5-TTS** | CC-BY-NC 4.0 (non-commercial) | Yes, strong | ~4GB VRAM | high | moderate | Yes | Non-commercial only, same restriction class as XTTS. |
| **Dia** (Nari Labs) | Apache-2.0 | Yes (audio prompt) | ~5GB VRAM | good | moderate | Yes | Newer, less battle-tested. |
| **Parler-TTS** (HF) | Apache-2.0 | No (text-described voice) | modest | good | fast | Yes | Voice described in words ("a calm female voice speaking slowly") instead of cloned. |
| **Chatterbox** (Resemble AI) | MIT | Yes, zero-shot | ~modest GPU | claimed to beat ElevenLabs in blind test | fast | Yes | 0.5B params; "Chatterbox Turbo" variant exists. Fully permissive license + cloning — arguably the single most attractive option if it lives up to the claim. |
| **GPT-SoVITS** | Open | Yes (from ~1 min audio) | GPU | good | moderate | Yes | Popular in cloning communities; more setup complexity. |

\* MOS = Mean Opinion Score (subjective quality, 1–5 scale), as reported by each project; not independently verified here.
\** RTF = Real-Time Factor (seconds of compute per second of audio); lower is faster.

**Licensing is the practical deciding factor**, not just voice quality:
- **Commercially safe** (Apache-2.0 / MIT): Kokoro, Fish Speech, Dia, Parler-TTS, Bark, Piper, Chatterbox.
- **Non-commercial only** (CPML / CC-BY-NC): Coqui XTTS v2, F5-TTS. Fine for personal study-material use, not for redistribution/monetization.

### 1.2 "Voicebox" — two different things

- **Meta's Voicebox** (research paper, 2023): Meta explicitly declined to release the model or
  code, citing misuse/safety concerns. **Not available, dead end.**
- **jamiepine/voicebox** (`voicebox.sh`, GitHub, open source): an actual desktop app for
  macOS/Windows/Linux — "the open-source AI voice studio." Local-first, does voice cloning from
  3+ seconds of audio, dictation, and bundles multiple engines under one UI: Qwen3-TTS, Qwen
  CustomVoice, LuxTTS, Chatterbox, Chatterbox Turbo, TADA, Kokoro — plus Whisper for STT. Stack:
  Tauri/Rust + React frontend, FastAPI (Python) backend. Runs GPU inference locally (Metal / CUDA /
  ROCm / Intel Arc / DirectML) or can connect to a remote machine. This is almost certainly what
  was meant by "voicebox" in the original request, and it's a legitimate, free, self-hosted option
  — effectively a friendly GUI wrapper over several of the libraries in §1.1 (notably Kokoro and
  Chatterbox, both already in the table above).

### 1.3 Gemini Studio / Gemini API

- Google AI Studio has a free tier (no credit card required), but as of 2026 it increasingly
  restricts the more capable "Pro" models. Flash / Flash-Lite remain free with daily/rate caps
  (e.g., Gemini 2.5 Flash: ~10 requests/min, 250–1500 requests/day; 2.5 Pro: ~5 RPM, 50–100 RPD).
- **Privacy caveat**: on the free tier, prompts and outputs may be used by Google to improve its
  products — worth knowing if any source material is sensitive.
- **Open research gap, unresolved**: I was not able to confirm the specifics of Gemini's native
  speech/audio-generation TTS capability (as distinct from plain text generation) — i.e., whether
  there is a dedicated, well-documented "generate spoken audio from this text" endpoint on the free
  tier, its voice options, and its actual rate/quota limits for audio specifically. **Action: verify
  directly against Google's current AI Studio / Gemini API docs before relying on this path.**
  Given the mature, well-documented, zero-cost alternatives in §1.1 and §1.4, Gemini TTS is treated
  here as a **secondary/optional** option pending that verification, not the primary plan.

### 1.4 edge-tts (bonus / notable "other AI" find)

- **edge-tts**: a Python package + CLI (`edge-tts`, `edge-playback`) that scripts Microsoft Edge's
  free online "Read Aloud" neural TTS cloud service — no Edge browser, no Windows, no API key
  required. Quality is genuinely good (real neural voices, e.g. `en-US-AvaNeural`,
  `ja-JP-KeitaNeural`), and it's very easy to use.
- **Legal/ToS status: gray area.** It's an unofficial, reverse-engineered use of a Microsoft cloud
  endpoint. A Microsoft Q&A response indicated personal use "should not pose legal risks" but this
  is not an official guarantee, and it's not a locally-run model — it depends on an external
  service that could change or be blocked at any time.
- Related project **openai-edge-tts** (`travisvn/openai-edge-tts`, GPL-3.0) wraps edge-tts to expose
  an OpenAI-TTS-API-compatible endpoint (`/v1/audio/speech`), useful for dropping into tools that
  expect OpenAI's paid TTS API (e.g. Open WebUI).
- **Verdict**: probably the best out-of-the-box quality/effort ratio of everything researched, but
  because it isn't a model you run yourself and carries ToS uncertainty, it's recommended as a
  **convenience fallback**, not the primary/only mechanism — pair it with a genuinely local option
  (Piper or Kokoro) so the workflow keeps working even if edge-tts ever stops being available.

### 1.5 Not yet directly verified (lower priority)

- **gTTS** — lightweight Python wrapper around Google Translate's TTS endpoint. Similar
  gray-area/cloud-dependency profile to edge-tts, generally lower voice quality. Likely superseded
  by edge-tts for this project's purposes; not separately recommended unless edge-tts becomes
  unavailable.
- **eSpeak-NG** — classic, extremely lightweight, robotic-sounding formant synthesizer. Useful only
  as a last-resort, zero-dependency fallback (e.g., no internet, no GPU, minimal disk space); Piper
  already covers this niche with much better quality at similarly low resource cost.

---

## 2. Recommendation / decision framework

Pick based on what you actually need:

- **Just want clear narration, minimal setup, CPU only, no cloning** → **Piper**. Fastest to get
  running, MIT-licensed, works everywhere including this project's existing environment.
- **Want noticeably better/more natural voice quality, still no cloning, CPU-or-small-GPU** →
  **Kokoro-82M**. Best quality-per-resource tradeoff among non-cloning options; documented Colab
  path if local GPU isn't available.
- **Want to clone a specific voice (e.g., narrate in a consistent "podcast host" voice)** →
  **Coqui XTTS v2** for personal/non-commercial use (best-documented Colab notebook of the cloning
  options), or **Chatterbox** if you want a fully permissive (MIT) license with zero-shot cloning
  and are willing to accept it's newer/less battle-tested.
- **Want a GUI instead of writing scripts, and/or want to try several engines interchangeably** →
  **jamiepine/voicebox** app (bundles Kokoro, Chatterbox, and others under one local-first UI).
- **Want the highest quality with least engineering effort, and are comfortable with an
  unofficial/cloud-dependent gray-area service as a fallback layer** → **edge-tts**, paired with
  Piper or Kokoro as the "real" self-hosted fallback.
- **Gemini path** → only after directly verifying current free-tier native audio-generation specifics
  in Google's docs; not recommended as the primary mechanism today given the unresolved research gap.

**Proposed default for this repo**: start with **Piper** (zero-friction, matches the existing
CPU-only, no-GPU-assumed setup of this project) as the baseline, and add **Kokoro** as a
higher-quality optional upgrade path once Piper is working end-to-end. Treat XTTS v2 / Chatterbox /
voicebox-app / edge-tts as documented alternatives to swap in later without changing the surrounding
pipeline.

---

## 3. Development plan

### 3.1 New folder convention (`lib/paths.py`)

Add a new output-folder constant, following the existing pattern (git-ignored, relative to repo root):

```python
# lib/paths.py  (proposed addition)
TTS_OUTPUT_DIR = "tts_output"   # generated speech audio (wav/mp3) from text/transcripts
```

### 3.2 New dependency (`requirements.txt`)

Proposed addition, mirroring the style/commenting of the existing Whisper entry:

```
# Text-to-speech (Phase D): generate spoken audio from transcripts/summaries.
# Piper (MIT) is CPU-only, very fast (RTF ~0.008), no GPU required — matches
# this project's existing CPU-only assumption. Downloads voice models on first
# use (small, per-voice .onnx files).
piper-tts>=1.2

# Optional higher-quality alternative (no voice cloning, still no GPU required
# for CPU inference, though a small GPU speeds it up). Apache-2.0 licensed.
# Uncomment to try instead of/alongside Piper:
# kokoro>=0.8
```

### 3.3 New script: `code/generate_speech.py`

Follow the same structure as `code/transcribe_audio.py` (Phase C precedent):

1. Accept an input text/transcript file path (e.g., a file from `transcripts/` or
   `generated_transcripts/`) and an output filename.
2. Load the Piper voice model (download on first run, cache locally — same "first-use download"
   pattern already used by `faster-whisper` via Hugging Face).
3. Reuse `lib/net.py`'s `apply_no_proxy_env()` if the chosen library also fetches models from
   Hugging Face (Kokoro does; Piper's own model host may differ — verify before relying on this).
4. Synthesize audio, write to `TTS_OUTPUT_DIR` as a `.wav` (Piper's native output) or convert to
   `.mp3` via the existing `ffmpeg` system dependency for consistency with `audio/`.
5. Keep the same "start with ONE file, generalize later" approach used for Phase C — pick a single
   short transcript first (e.g., a `summaries/*.summary.md` file) before building a batch/generic
   pipeline.

### 3.4 Phasing

- **Phase D0**: Install Piper locally (`pip install piper-tts`), verify `piper --version` works,
  download one small English voice, synthesize a short test string to `.wav`.
- **Phase D1**: Build `code/generate_speech.py` for a single fixed input file → single output file
  (mirrors Phase C1's approach for `transcribe_audio.py`).
- **Phase D2**: Generalize to accept any transcript/summary file as input, with the output filename
  and `TTS_OUTPUT_DIR` derived automatically.
- **Phase D3 (optional)**: Add Kokoro as a selectable alternative engine (`--engine piper|kokoro`
  flag) for quality comparison.
- **Phase D4 (optional)**: Add XTTS v2 or Chatterbox as a cloning-capable engine, gated behind an
  explicit `--voice-sample path/to/reference.wav` flag, kept separate from the default no-cloning
  path so the simple case stays simple.

---

## 4. Testing plan

Because this sandbox blocks outbound `pip install` from PyPI (`pypi.org` / `files.pythonhosted.org`
return 403 / `blocked-by-allowlist` — the same constraint hit during Phase C), **all package
installation and actual TTS testing must happen on your local machine**, not in this sandbox. This
matches how `faster-whisper` testing was handled.

Steps to run locally:

1. `pip install piper-tts` (add `--break-system-packages` only if your environment requires it,
   same as this sandbox's convention — not needed on a normal local install).
2. Download a voice model (Piper provides a model list; smaller models are a few MB to ~60MB).
3. Run a minimal smoke test:
   ```bash
   echo "This is a test of the text to speech pipeline." | piper --model <voice>.onnx --output_file test.wav
   ```
4. Confirm `test.wav` plays correctly and sounds intelligible.
5. Once `code/generate_speech.py` exists, run it against one real transcript/summary file from this
   repo (e.g., the Git/GitHub tutorial summary) and confirm output lands in `tts_output/`.
6. If trying Kokoro instead/also: `pip install kokoro>=0.8`, run its documented quick example
   (`KPipeline(lang_code="a")`), and compare output quality/speed against Piper on the same input
   text.
7. If trying Colab (for GPU-hungry options like XTTS v2 or Kokoro-with-GPU): use the referenced
   public notebooks (`kubinka0505/colab-notebooks` → `Coqui_XTTS.ipynb` for XTTS v2) rather than
   building one from scratch first; adapt only after confirming it runs.

---

## 5. Verification / checklist

- [ ] Confirm chosen library actually installs and runs on your local machine (sandbox cannot
      verify this — PyPI is blocked here).
- [ ] Confirm license fits intended use: Piper/Kokoro/Chatterbox/Fish Speech/Dia/Parler-TTS/Bark
      (MIT/Apache-2.0) are safe for any use including commercial; XTTS v2/F5-TTS (CPML/CC-BY-NC) are
      personal/non-commercial use only.
- [ ] If using edge-tts/openai-edge-tts: acknowledge the ToS gray-area (unofficial use of a
      Microsoft cloud service, not guaranteed to remain available) and keep a local fallback
      (Piper/Kokoro) so the pipeline doesn't hard-depend on it.
- [ ] If using Gemini: directly re-verify current free-tier native audio-generation specifics
      against Google's live docs (this was an unresolved research gap here, not confirmed) before
      depending on it.
- [ ] Verify first-run model download works from your network (corporate proxy interference is a
      known risk here — same class of issue `apply_no_proxy_env()` was built for in Phase C).
- [ ] Listen to generated audio for intelligibility, correct language/accent, and no truncation on
      longer inputs (some cloning models, e.g. XTTS v2 in Colab, have documented text-length limits).
  - [ ] Confirm output file lands in the new `tts_output/` folder (once `lib/paths.py` is updated)
      and is git-ignored consistently with `audio/`, `transcripts/`, etc.
  - [ ] If adding voice cloning later: confirm the reference audio sample is clean (little background
      noise, 3s+ minimum, ideally 10-30s) — quality of cloning is very sensitive to reference quality.
  - [ ] Update `requirements.txt` and `lib/paths.py` for real once a library is finalized (this
      document's §3.1/§3.2 are proposals, not yet applied to those files).

---

## 6. Open items / research gaps (explicitly flagged, not resolved here)

1. Gemini's native speech/audio-generation TTS capability specifics (voices, quotas, whether it
   exists as a distinct free-tier feature at all) — needs direct verification against current docs.
2. `gTTS` and `eSpeak-NG` were not directly hands-on tested here; included only as lower-priority
   baseline mentions since edge-tts and Piper already cover their respective niches (simple cloud
   wrapper, minimal-dependency fallback) at equal or better quality.
3. Whether Piper's model files are hosted somewhere requiring the same `apply_no_proxy_env()`
   treatment as Hugging Face — not yet confirmed; check on first local install attempt.

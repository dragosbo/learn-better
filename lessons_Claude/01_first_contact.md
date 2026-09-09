# Lesson 01 — First Contact

**You'll build:** Nothing tangible yet — by the end you know how to give an AI assistant useful
instructions, how to get a coherent explanation of an unfamiliar tool, and what to do when the
assistant loses its train of thought mid-session.
**Complexity:** ⭐☆☆☆☆   **Est. time:** ~30–45 min
**AI tasks in this lesson:** long-form explanation, Q&A, orientation

---

## Prerequisites

None. This is the first lesson.

You need:
- An AI assistant you can type to (browser-based or IDE-embedded — any will do)
- A text editor or IDE (VS Code recommended for later lessons)
- No code, no repo, no environment yet — those come in Lessons 02 and 03

---

## Re-orient the AI

> If you start a new session mid-lesson, paste this:
>
> "I'm working through a guided curriculum to build a YouTube transcription and summarisation tool
> in Python, using an AI assistant as my primary coding tool. I'm on **Lesson 01 — First Contact**.
> We haven't created any files yet — this lesson is orientation only. Please continue from where I
> left off."

---

## Concepts

1. **The assistant is a collaborator, not a search engine.** You get the best results by giving it
   context (what you're trying to build, what OS you're on, what already exists) rather than
   asking bare questions.

2. **Prompts are repeatable.** A well-structured prompt works consistently. This curriculum shows
   you the optimised versions — the prompts that worked after the project was actually built.

3. **Context is fragile; recovery is cheap.** Long AI sessions accumulate context. When the
   assistant goes off-track or forgets earlier steps, you don't start from scratch — you paste a
   short re-orient block and pick up where you left off.

---

## Step-by-step

### 01.1 — Ask the assistant to explain an unfamiliar tool

This is your first prompt exercise. The goal is to get a clear explanation of `yt-dlp` — the
core downloader this project uses — and why it replaced the older alternatives.

**Prompt:**
```
I'm planning to build a Python tool that downloads YouTube audio and transcripts for local
processing. I've heard of yt-dlp, pytube, and scrapetube. Can you explain what each one does,
why yt-dlp is now the preferred choice, and what its main advantages are over the others?
Please be concrete — mention specific things that broke or were retired.
```

**Expected output:** The assistant should explain that `pytube` is fragile (breaks frequently
when YouTube changes its API), `scrapetube` has been broken since ~2025, and `yt-dlp` is the
actively-maintained successor that handles audio, video, subtitles, format merging (via ffmpeg),
and YouTube's bot-detection countermeasures. It should mention `curl_cffi` as the plugin that
handles TLS fingerprinting.

**Verify:** No command — just check that the answer is specific and mentions at least: yt-dlp's
active maintenance, the pytube fragility issue, and why ffmpeg is needed alongside yt-dlp.

---

### 01.2 — Understand the kinds of tasks an AI assistant is good at

Before writing any code, it helps to know where the assistant excels and where it needs guidance.

**Prompt:**
```
I'm going to use you as my primary coding assistant to build a Python project from scratch.
What kinds of tasks should I give you directly (where you work well without much hand-holding),
and where should I be careful or verify your output? Give me practical examples for a
Python project that uses yt-dlp, faster-whisper, and Piper TTS.
```

**Expected output:** The assistant should distinguish between tasks it handles well (explaining
concepts, generating boilerplate, writing config-driven scripts, suggesting project structure,
writing documentation) and areas requiring more care (knowing which package versions are current,
awareness of OS-specific differences, very long agentic tasks where it may lose track of state).

**Verify:** The answer should mention something about verification (running the code, checking
output files, or confirming command behaviour) — not just trusting the generated output blindly.

---

### 01.3 — Learn the re-orient pattern

This is the most important skill in the curriculum. AI sessions have limited context — when you
start a new chat, or when a long session drifts, the assistant loses the picture of what you've
built. The fix is a short re-orient block you paste at the start of each session.

**Prompt:**
```
I want to learn how to write a good "re-orient" block — a short paragraph I can paste at the
start of a new chat session (or after a long break mid-session) to quickly restore your context
about an ongoing project. What should such a block contain? Give me a template I can fill in
for a Python CLI project.
```

**Expected output:** The assistant should suggest including: project name and purpose, current
working file or milestone, OS and environment name, and one sentence on where to continue.
Something like: "I'm working on [project name]. It is a Python tool that [purpose]. We are
currently on [step]. The last file we created was [file]. OS: [Windows/Linux/macOS]. Env:
[env name]. Please continue from [specific point]."

**Verify:** The template should cover: what the project does, what was just created, OS, env name,
and where to pick up. If any of those are missing, ask the assistant to add them.

---

### 01.4 — Practise crash recovery

Run a short simulation: paste the re-orient block from the top of this lesson into a new session
(or a fresh browser tab) and verify the assistant picks up correctly.

**Prompt:** *(paste the block from the top of this lesson verbatim)*
```
I'm working through a guided curriculum to build a YouTube transcription and summarisation tool
in Python, using an AI assistant as my primary coding tool. I'm on Lesson 01 — First Contact.
We haven't created any files yet — this lesson is orientation only. Please continue from where I
left off.
```

**Expected output:** The assistant acknowledges the context and asks what to do next (or suggests
starting Lesson 02). It should not ask you to repeat project details.

**Verify:** If the assistant responds as if it has context, the pattern works. If it asks
clarifying questions about the project, your re-orient block needs more detail — add the project
description from Step 01.1.

---

## When the AI misbehaves

**The assistant gives a very long answer when you asked for something brief.**
Add a length constraint at the end of your prompt: "Keep your answer to 3–5 bullet points" or
"Give me a one-paragraph summary first, then offer to go deeper." Assistants default to thorough;
you have to ask for concise.

**The assistant confidently states something wrong (e.g. that pytube is still maintained).**
Don't accept it silently. Ask: "Are you sure? My understanding is that pytube is fragile because
YouTube frequently changes its internal API. Can you confirm?" The assistant will usually
self-correct. For anything that affects your toolchain, verify with a quick web search.

**The assistant loses the thread mid-session and starts treating earlier context as if it never
happened.**
Paste the re-orient block from the top of this lesson. If that doesn't help, start a fresh
session with the same block. Sessions have a finite context window; once it fills, earlier
information silently drops out.

---

## What you have now

No files created. What you do have:

- A working mental model of what the assistant is good at and where to double-check it
- A re-orient block pattern you can adapt for every future lesson
- Familiarity with `yt-dlp` as the foundation of this project

Repo state: nothing yet — the repo doesn't exist until Lesson 02.

---

## Next →

[Lesson 02 — Project Scaffold](02_project_scaffold.md)
